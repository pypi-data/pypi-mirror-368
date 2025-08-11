#!/usr/bin/env python

import pickle

import pyopenms

from emzed.ms_data.peak_map import BoundSpectrum, ImmutableSpectra, PeakMap, Spectrum


def merge_spectra(spectra, mz_binning_width, is_ppm=False):
    """merges spectra.

    :param spectra: list of Spectrum objects or PeakMap or PeakMap.spectra attribute,
                    must be of same ms leve..
    :param mz_binning_width: tolerance parameter for matching m/z values
    :param is_ppm: indicates if mz_binning_width is in Da or ppm.

    :returns: merged spectrum, return None if spectra is empty.
    """

    if isinstance(spectra, (list, tuple)):
        assert all(
            isinstance(s, (BoundSpectrum, Spectrum)) for s in spectra
        ), "list/tuple must contain spectra only"
    else:
        assert isinstance(
            spectra, (PeakMap, ImmutableSpectra)
        ), "peakmap, peakmap.spectra or list/tuple of spectra required"

    assert isinstance(
        mz_binning_width, (int, float)
    ), "number required for mz_binning_width"
    assert is_ppm in (True, False), "need boolean value for is_ppm"

    if len(spectra) == 0:
        return None

    ms_levels = set(s.ms_level for s in spectra)
    if len(ms_levels) > 1:
        raise ValueError(
            "mixed ms levels {} in spectra".format(", ".join(sorted(ms_levels)))
        )
    ms_level = ms_levels.pop()

    spectra = [
        (
            s.rt,
            s.ms_level,
            s.polarity,
            s.precursors,
            s.mzs,
            s.intensities,
            s.scan_number,
        )
        for s in spectra
    ]

    scan_number, rt, ms_level, polarity, peaks = pyopenms.merge_spectra(
        pickle.dumps((spectra, [], "")),
        float(mz_binning_width),
        b"ppm" if is_ppm else b"Da",
        len(spectra) + 1,
        ms_level,
    )

    return Spectrum(scan_number, rt, ms_level, polarity, [], peaks)
