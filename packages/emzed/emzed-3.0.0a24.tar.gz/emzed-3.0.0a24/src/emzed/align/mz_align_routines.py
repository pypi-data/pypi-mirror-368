# encoding: utf-8

import numpy as np


def _find_mz_matches(reference_table, table, atol):
    matched = table.fast_join(reference_table, "mz", atol=atol, rtol=0)
    matched = matched.filter(matched.rt.in_range(matched.rtmin__0, matched.rtmax__0))
    print(len(matched), "MATCHES FROM REFERENCE")

    matched = matched.extract_columns(
        "id",
        "mz",
        "mz__0",
        "rt",
        "rtmin__0",
        "rtmax__0",
        "name__0",
        "polarity__0",
        keep_view=True,
    )
    matched.rename_columns(
        mz__0="mz_reference",
        rtmin__0="rtmin",
        rtmax__0="rtmax",
        name__0="name",
        polarity__0="polarity",
    )
    real = np.array(list(matched.mz))
    tobe = np.array(list(matched.mz_reference))
    return real, tobe, matched


def _remove_value(vec, idx):
    return np.hstack((vec[:idx], vec[idx + 1 :]))


def _find_parameters(tobe, real, minR2, maxTol, minPoints):
    while len(real) >= minPoints:
        fit_result = _fit_parameters(real, tobe)
        if fit_result is None:
            return None

        transform, r2, imax, _, resid = fit_result

        print("NUMPOINTS=%3d  goodness=%.3f" % (len(real), r2))
        if r2 >= minR2 or max(resid) <= maxTol:
            break
        # remove match which fits worst:
        real = _remove_value(real, imax)
        tobe = _remove_value(tobe, imax)
    else:
        return None

    return transform, (real, tobe)


def irls_fit(A, b, p, N=10):
    """IRLS iterations for minimizing ||Ax-b||_p

    iterative weighting maxtrix is

                w_ii = (eps + resid_i)^[(p-2)/2]

    see also https://en.wikipedia.org/wiki/Iteratively_reweighted_least_squares
    """
    # we do not need to store full diagonal matrix, just its entries:
    W = np.ones(len(b))
    last_param = None

    for i in range(N):  # 2 iterations seem to be enough
        WA = (A.T * W).T  # calculates np.dot(np.diag(W), A)
        Wb = W * b  # calculates np.dot(np.diag(W), b).flatten()
        param = np.linalg.lstsq(WA, Wb, rcond=None)[0]

        resid = np.abs(np.dot(A, param) - b)
        W = (1e-8 + resid) ** (p - 2.0) / 2.0

        if last_param is None:
            last_param = param
        else:
            delta = np.linalg.norm(param - last_param) / np.linalg.norm(last_param)
            last_param = param
            if delta < 1e-3:
                break
    else:
        return None

    return param


def _fit_parameters(real_mz, tobe_mz):
    A = np.ones((len(real_mz), 2))
    A[:, 0] = real_mz
    shifts = tobe_mz - real_mz

    # p close to 1 is more outlier resistant than p = 2.
    # but p = 1.0 is a singularity, thus:
    param = irls_fit(A, shifts, p=1.01)
    if param is None:
        return None

    a, b = map(float, param)

    fitted_shift = a * real_mz + b
    resid = np.abs(fitted_shift - shifts.flatten())

    # robust replacement for pearson r:
    nom = np.linalg.norm(fitted_shift - shifts, ord=1.0)
    denom = np.linalg.norm(shifts - np.median(shifts), ord=1.0)
    r = 1.0 - nom / denom

    imax = np.argmax(resid)
    fitted = fitted_shift + real_mz

    def transform(x, a=a, b=b):
        return a * x + b + x

    return transform, r, imax, fitted, resid


def _plot_and_save_match(tobe, real, used, transform, path):
    import matplotlib

    matplotlib.use("Agg")

    import pylab

    fitted = transform(real)
    pylab.subplot(2, 1, 1)
    pylab.title(r"$mz$ vs $\Delta mz$")
    pylab.plot(real, tobe - real, "ro")
    pylab.plot(real, fitted - real)

    real_used, tobe_used = used
    fitted_used = transform(real_used)
    pylab.plot(real_used, tobe_used - real_used, "go")
    pylab.gca().set_xlabel(r"$mz$")
    pylab.gca().set_ylabel(r"$\Delta mz$")

    pylab.subplot(2, 1, 2)
    pylab.plot([np.min(real), np.max(real)], [0, 0])
    pylab.title(r"$residuals$")

    for rr, rs in zip(real, tobe - fitted):
        pylab.plot([rr, rr], [0, rs], "b")

    pylab.plot(real, tobe - fitted, "ro")

    pylab.plot(real_used, tobe_used - fitted_used, "go")
    pylab.gca().set_xlabel(r"$mz$")
    pylab.gca().set_ylabel(r"$\Delta mz$")

    pylab.tight_layout()
    pylab.savefig(path)
    pylab.close()


def _apply_transform(table, transform):
    from emzed import PeakMap

    # extract peakmap first:
    # if we do this after consolidate we get issues with database connections
    # and attached dbs in the same table db.
    immutable_peakmap = table.peakmap.unique_value()
    peakmap = PeakMap.from_(immutable_peakmap)

    # as we modify peakmaps below we need a real deepcopy here:
    table = table.consolidate()
    table.replace_column("mz", table.apply(transform, table.mz))
    table.replace_column("mzmin", table.apply(transform, table.mzmin))
    table.replace_column("mzmax", table.apply(transform, table.mzmax))

    with peakmap.spectra_for_modification() as spectra:
        spectra._transform_mz(transform)

    table.replace_column_with_constant_value("peakmap", peakmap)
    table.meta_data["mz_aligned"] = True
    return table
