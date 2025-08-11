# This file is part of emzed (https://emzed.ethz.ch), a software toolbox for analysing
# LCMS data with Python.
#
# Copyright (C) 2020 ETH Zurich, SIS ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.


import sys
from collections import Counter, defaultdict

import numpy as np

from emzed.ms_data import Spectrum
from emzed.utils import compute_spectra_alignments

from .merge_spectra import merge_spectra


def attach_ms2_spectra(
    peak_table, mode="union", mz_tolerance=1.3e-3, print_final_report=True
):
    """takes *peak_table* with columns "rtmin", "rtmax", "mzmin", "mzmax" and "peakmap"
    and extracts the ms2 spectra for these peaks.

    the *peak_table* is modified in place, an extra column "ms2_spectra" is added.
    the content of such a cell in the table is always a list of spectra. for modes
    "union" and "intersection" this list contains one single spectrum.

    modes:
        - "all": extracts a list of ms2 spectra per peak
        - "max_range": extracts spec with widest m/z range
        - "max_signal": extrats spec with maximal energy
        - "union": merges all ms2 spectra from one peak to one spectrum containing all
          peaks
        - "intersection": merges all ms2 spectra from one peak to one spectrum
          containing peaks which appear in all ms2 spectra.

    *mz_tolerance*: only needed for modes "union" and "intersection".

    *print_final_report*: prints some final report with diagnosis messages for testing
                          if mz_tolerance parameter fits, you shoud set this parameter
                          to True if you are not sure if mz_tolerance fits to your
                          machines resolution.
    """

    assert mode in ("all", "max_range", "max_signal", "union", "intersection")

    if not set(("rtmin", "rtmax", "mzmin", "mzmax", "peakmap")) <= set(
        peak_table.col_names
    ):
        raise ValueError(
            "need columns rtmin, rtmax, mzmin, mzmax and peakmap in peak table"
        )

    for name in ("spectra_ms2", "num_spectra_ms2", "ms2_extraction_info"):
        assert (
            name not in peak_table.col_names
        ), f"can not accept peak table with existing column '{name}'"

    rtmin = peak_table.rtmin.min().eval() - 5
    rtmax = peak_table.rtmax.max().eval() + 5
    mzmin = peak_table.mzmin.min().eval() - 1
    mzmax = peak_table.mzmax.max().eval() + 1

    lookup = {
        pm.unique_id: LookupMS2(
            # reduce size:
            pm.extract(
                mslevelmin=2,
                rtmin=rtmin,
                rtmax=rtmax,
                precursormzmin=mzmin,
                precursormzmax=mzmax,
            )
        )
        for pm in peak_table.peakmap.unique_values()
    }

    all_spectra = []
    last_n = -1
    num_spectra = []
    infos = []

    print("PROCESS PEAK TABLE: ", end="")

    for i, row in enumerate(peak_table):
        n = int(10.0 * i / len(peak_table))
        if n != last_n:
            print(n, end="")
            sys.stdout.flush()
            last_n = n
        ms2_spectra, charges = lookup[row.peakmap.unique_id].find_spectra(
            row.mzmin, row.mzmax, row.rtmin, row.rtmax
        )
        num_spectra.append(len(ms2_spectra))
        merged_spectra = _merge_spectra(ms2_spectra, mode, mz_tolerance)

        empty_result = merged_spectra is None or not any(
            len(s.peaks) for s in merged_spectra
        )
        if ms2_spectra and empty_result:
            infos.append("%s(empty)" % mode)
        else:
            infos.append(mode)

        if merged_spectra is None:
            all_spectra.append(None)
        else:
            merged_spectra = [s.unbind() for s in merged_spectra]
            charges = set(charges)
            charges.discard(0)
            if charges:
                charges = Counter(charges)
                (charge, _), *_ = charges.most_common(1)
            else:
                charge = 0
            for s in merged_spectra:
                s.precursors = [(0.5 * (row.mzmin + row.mzmax), 0, charge)]

            all_spectra.append(merged_spectra)

    # start new line
    print()

    peak_table.add_column("spectra_ms2", all_spectra, object)
    peak_table.add_column("num_spectra_ms2", num_spectra, int)
    peak_table.add_column("ms2_extraction_info", infos, str)
    if print_final_report:
        print_report(peak_table)


def print_report(peak_table):
    num_ms2_added = peak_table.spectra_ms2.count_not_none()
    print()
    print(
        "FINAL REPORT ==============================================================="
    )
    print()
    print(
        "1. added ms2 spectra to %d peaks out of %d" % (num_ms2_added, len(peak_table))
    )
    print()
    print(
        "============================================================================"
    )
    print()


class LookupMS2(object):
    """fast lookup of spectra for given peak limits. uses binning + dictionary
    for fast lookup.
    """

    def __init__(self, spectra, dmz=0.01, drt=10):
        self.bins = defaultdict(list)
        self.dmz = dmz
        self.drt = drt
        self._build_lookup_table(spectra)

    def _build_lookup_table(self, spectra):
        number = 0
        last_n = -1
        print("BUILD LOOKUP TABLE: ", end="")
        for i, spec in enumerate(spectra):
            n = int(10.0 * i / len(spectra))
            if n != last_n:
                print(n, end="")
                sys.stdout.flush()
                last_n = n
            if not spec.precursors:
                continue
            rt = spec.rt
            mz, _, charge = spec.precursors[0]
            i0 = int(mz / self.dmz)
            j0 = int(rt / self.drt)
            self.bins[i0, j0].append((number, mz, rt, spec, charge))
            number += 1
        print()

    def find_spectra(self, mzmin, mzmax, rtmin, rtmax):
        i0min = int(mzmin / self.dmz)
        i0max = int(mzmax / self.dmz)
        j0min = int(rtmin / self.drt)
        j0max = int(rtmax / self.drt)
        found = []
        charges = []
        seen = set()
        for i0 in range(i0min - 1, i0max + 2):
            for j0 in range(j0min - 1, j0max + 2):
                for number, mz, rt, spec, charge in self.bins[i0, j0]:
                    if number in seen:
                        continue
                    if mzmin <= mz <= mzmax and rtmin <= rt <= rtmax:
                        seen.add(number)
                        found.append(spec)
                        charges.append(charge)
        return found, charges


def _common_alignment(alignments):
    # find common peaks from bottom to up
    # the indices in the result list relate to the last spectrum
    if not alignments:
        return []
    common = [j for (i, j) in alignments[0]]
    for alignment in alignments[1:]:
        common = [j for (i, j) in alignment if i in common]
    return common


def _final_spectrum(peak_list, spectra):
    assert len(spectra) > 0
    rt = np.mean([s.rt for s in spectra])
    msLevel = 2
    polarity = spectra[0].polarity

    precursors = [p for spec in spectra for p in spec.precursors]
    return Spectrum(None, rt, msLevel, polarity, precursors, peak_list)


def _merge_spectra(spectra, mode, mz_tolerance):
    """merge a list of spectra. allowed modes are 'max_range', 'max_signal', 'union',
    'intersection' and 'all'
    """
    if not spectra:
        return None
    if mode == "all":
        return spectra

    if mode == "max_range":
        spectrum = max(spectra, key=lambda s: (max(s.peaks[:, 0]) - min(s.peaks[:, 0])))
    elif mode == "max_signal":
        spectrum = max(spectra, key=lambda s: sum(s.peaks[:, 1] ** 2))
    elif mode == "union":
        spectrum = merge_spectra(spectra, mz_tolerance)
    elif mode == "intersection":
        spectrum = _merge(spectra, mz_tolerance=mz_tolerance)
    else:
        raise ValueError("mode is not allowed")
    if spectrum is None:
        return None
    return [spectrum]


def _merge(spectra, mz_tolerance=1.3e-3):
    """merges a list of spectra to one spectrum.

    *mz_tolerance*        : binning size for grouping peaks.

    *merge_only_common_peaks*: if this value is True the resulting spectrum
                         only consists of dominating peaks which are present
                         in every input spectrum
    """

    if not spectra:
        return None, 0

    if len(spectra) == 1:
        return spectra[0], 0

    alignments = compute_spectra_alignments(spectra, mz_tolerance)
    common = _common_alignment(alignments)

    mz_vecs = [s.peaks[:, 0] for s in spectra]
    intensity_vecs = [s.peaks[:, 1] for s in spectra]

    mz_last = mz_vecs[-1]
    ii_last = intensity_vecs[-1]
    peaks = [(mz_last[i], ii_last[i]) for i in common]
    if peaks:
        peak_list = np.vstack(peaks)
    else:
        peak_list = np.zeros((0, 2))
    return _final_spectrum(peak_list, spectra)
