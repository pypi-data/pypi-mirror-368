#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>

import warnings
from collections import defaultdict
from math import log

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FormatStrFormatter
from scipy.signal import find_peaks

from emzed import MzType, Table

from .formula_parser import join_formula, parse_formula

with warnings.catch_warnings():
    warnings.filterwarnings("ignore")
    from IsoSpecPy import Iso, IsoDistribution, IsoTotalProb
    from scipy.optimize import minimize_scalar


def compute_centroids(mf, explained_abundance, *, abundances=None):
    """computes table with theoretial ms peaks of molecular formula.

    Usage examples:

    ```
    compute_centroids("C6S2", 0.995)
    compute_centroids("C6S2", 0.995, abundances=dict(C={12: 0.5, 13: 0.5}))
    ```

    :param mf: molecular sum formula.

    :param explained_abundance: stopping criterium, value is between 0 and 1.

    :param abundances:  override natural abundances.

    :returns: table with columns `id`, `mf`, `m0`, `abundance`.
    """

    rows = _compute_centroids(mf, explained_abundance, abundances)

    table = Table.create_table(
        ["mf", "m0", "abundance"], [str, MzType, float], rows=rows
    )
    table.set_col_format("abundance", "%5.3f")
    table = table.sort_by("abundance", ascending=False).consolidate()
    table.add_enumeration()
    return table


def _compute_centroids(mf, explained_abundance, user_defined_abundances):
    from .elements import abundance_dict, mass_dict

    if explained_abundance > 1.0:
        raise ValueError("value for explained_abundance must be <= 1.0")

    decomposed = parse_formula(mf)

    if user_defined_abundances is None:
        user_defined_abundances = {}

    atom_counts = []
    all_masses = []
    all_abundances = []
    decomposition_in_order = []

    for (element, isotope), count in decomposed.items():
        atom_counts.append(count)
        if isotope is None:
            if element in user_defined_abundances:
                abundance = user_defined_abundances[element]
            else:
                abundance = abundance_dict[element]
            abundances = []
            masses = []
            decomposition = []
            for key in abundance:
                if abundance[key] == 0:
                    continue
                abundances.append(abundance[key])
                masses.append(mass_dict[element][key])
                decomposition.append((element, key))
            all_abundances.append(abundances)
            all_masses.append(masses)
            decomposition_in_order.extend(decomposition)

        else:
            all_abundances.append([1.0])
            all_masses.append([mass_dict[element + str(isotope)]])
            decomposition_in_order.append((element, isotope))

    # isospecpy has issus with its __del__ implemenation which hangs randomly.
    # we just remove this. it might lead to resource leaks if you call this
    # **very often**, but forking and fixing IsoTotalProb would be too much work
    # right now:
    IsoTotalProb.__del__ = lambda self: None

    iso = Iso("", True, atom_counts, all_masses, all_abundances)
    t = iso.ffi.setupTotalProbFixedEnvelope(iso.iso, explained_abundance, False, True)
    generator = IsoDistribution(cobject=t, get_confs=True, iso=iso)
    iso.ffi.deleteFixedEnvelope(t, False)

    result = []
    for mass, prob, pattern in generator:
        pattern_flat = [pi for pii in pattern for pi in pii]
        c = defaultdict(int)
        for i, pi in enumerate(pattern_flat):
            key = decomposition_in_order[i]
            c[key] += pi
        result.append((join_formula(c, " "), mass, prob))
    return result


def measured_centroids(mf, R, explained_abundance, *, abundances=None):
    """computes table with theoretial measured ms peaks of molecular formula.

    Usage examples:

    ```
    measured_centroids("C6S2", 200_000, 0.995)
    measured_centroids("C6S2", 200_000, 0.995, abundances=dict(C={12: 0.5, 13: 0.5}))
    ```

    :param mf: molecular sum formula.

    :param R: resolution defined as as zz / FWHM

    :param explained_abundance: stopping criterium, value is between 0 and 1.

    :param abundances:  override natural abundances.

    :returns: table with columns `id`, `R`, `mf`, `m0`, `abundance`.
    """

    rows = _measured_centroids(mf, R, explained_abundance, abundances)

    table = Table.create_table(["m0", "abundance"], [MzType, float], rows=rows)
    table.set_col_format("abundance", "%5.3f")
    table.add_column_with_constant_value("R", R, float, insert_before="m0")
    table.add_enumeration()
    return table


def _measured_centroids(mf, R, explained_abundance, abundances):
    centroids = _compute_centroids(mf, explained_abundance, abundances)
    if not centroids:
        return []

    # sort by mass:
    centroids.sort(key=lambda e: e[1])
    # unpack tuples:
    mfs, masses, abundances = zip(*centroids)

    """
    basic idea:

    find peaks of

        f(m) = sum_i a_i * exp(-(m - mi) ** 2 / si ** 2)

        # R = M / delta_M
        R = M / FWHM

        delta_m = FWHM / 2 = M / (2 * R)

        exp(-delta_m ** 2 / si ** 2) = 0.5
        delta_m ** 2 = log(2) * si ** 2

        si ** 2 = (M / 2R) ** 2 / log(2)

    search width d around mi: decay to 50% = FWHM = M / R
    """

    # compute clusters by gap of .5 Da to reduce memory foot print.
    # we will compute profiles per cluster:
    groups = [0]
    group_id = 0
    last_m = masses[0]

    for m in masses[1:]:
        if m - last_m > 0.5:
            group_id += 1
        groups.append(group_id)
        last_m = m

    mass_groups = defaultdict(list)
    abundance_groups = defaultdict(list)

    for gi, mi, ai in zip(groups, masses, abundances):
        mass_groups[gi].append(mi)
        abundance_groups[gi].append(ai)

    centroids = {}

    for gi, masses in mass_groups.items():
        masses = np.array(masses)
        abundances = np.array(abundance_groups[gi])

        if len(masses) == 1:
            centroids[masses[0]] = abundances[0]
            continue

        min_m = min(masses)
        max_m = max(masses)

        si_2_vec = (masses / 2 / R) ** 2 / np.log(2)

        dm = max_m / R
        mvec = np.arange(min_m - dm, max_m + dm, dm / 10000)
        profile = np.sum(
            abundances * np.exp(-((masses - mvec[:, None]) ** 2) / si_2_vec), axis=1
        )

        max_indices, _ = find_peaks(profile)

        # refine exact positions of peaks to 8 digits after decimal point:
        for i in max_indices:
            mvec_fine = np.arange(mvec[i] - 0.001, mvec[i] + 0.001, 1e-8)
            profile = np.sum(
                abundances * np.exp(-((masses - mvec_fine[:, None]) ** 2) / si_2_vec),
                axis=1,
            )
            fine_indices, _ = find_peaks(profile)
            centroids.update(dict([(mvec_fine[i], profile[i]) for i in fine_indices]))

    total_intensity = sum(centroids.values())
    for m0, intensity in centroids.items():
        centroids[m0] /= total_intensity

    return sorted(centroids.items())


def plot_profile(mf, R, explained_abundance, *, path=None, abundances=None):
    """plots theoretial ms peaks of molecular formula.

    Usage examples:

    ```
    plot_profile("C6S2", 200_000, 0.995)
    plot_profile("C6S2", 200_000, 0.995, path="profile.png")
    plot_profile("C6S2", 200_000, 0.995, abundances=dict(C={12: 0.5, 13: 0.5}))
    ```

    :param mf: molecular sum formula.

    :param R: resolution defined as as zz / FWHM

    :param explained_abundance: stopping criterium, value is between 0 and 1.

    :param path: path to save plot to. If not provided a plot window will pop up.

    :param abundances:  override natural abundances.
    """
    centroids = _compute_centroids(mf, explained_abundance, abundances)

    plt.figure()
    plt.xlabel("m/z")
    plt.ylabel("abundance")
    plt.gca().xaxis.set_major_formatter(FormatStrFormatter("%.1f"))

    if centroids:
        # sort by mass:
        centroids.sort(key=lambda e: e[1])
        # unpack tuples:
        mfs, masses, abundances = zip(*centroids)

        mi_vec = np.array(masses)
        ai_vec = np.array(abundances)
        si_2_vec = (mi_vec / 2 / R) ** 2 / log(2)

        di_vec = mi_vec / R

        def f(m):
            # to compute maxima we must flip the sign:
            return -np.sum(ai_vec * np.exp(-((m - mi_vec) ** 2) / si_2_vec))

        peaks = {}

        # merge peaks
        digits = 9
        for di, mi, si_2 in zip(di_vec, mi_vec, si_2_vec):
            rtol = 10**-digits / mi / 10
            result = minimize_scalar(f, (mi - di, mi + di), tol=rtol)
            m0 = result.x
            bin_ = round(m0, digits)
            peaks[bin_] = -f(m0)

            xdata = np.linspace(mi - 7 * si_2**0.5, mi + 7 * si_2**0.5, 1000)
            ydata = np.array([-f(x) for x in xdata])
            plt.plot(xdata, ydata, "k")
            plt.plot([m0, m0], [0, -f(m0)], "r:")

        total_intensity = sum(peaks.values())
        for m0, intensity in peaks.items():
            peaks[m0] /= total_intensity

        ymin, ymax = plt.ylim()
        plt.ylim(ymin, ymax * 1.1)

    plt.title(f"{mf} / R = {R}")
    if path is None:
        plt.show()
    else:
        plt.savefig(path)
