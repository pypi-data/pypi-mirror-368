#!/usr/bin/env python

import numpy as np

import emzed


def test_extract_chromatograms(data_path, regtest):
    peaks = emzed.io.load_table(data_path("peaks.table"))
    t = emzed.extract_chromatograms(peaks)
    print(t, file=regtest)

    assert "chromatogram" in t.col_names

    assert len(t[0].chromatogram) == 2
    rts, iis = t[0].chromatogram
    assert len(iis) == len(rts)

    assert len(iis) == 602


def test_extract_ms_chromatograms(data_path, regtest):
    pm = emzed.io.load_peak_map(data_path("210205_A8.mzML"))
    t = emzed.extract_ms_chromatograms(pm)
    print(t, file=regtest)


def test_issue_194(data_path, regtest):
    """to_pandas failed for MSChromatogram column type"""

    pm = emzed.io.load_peak_map(data_path("210205_A8.mzML"))
    t = emzed.extract_ms_chromatograms(pm)
    print(t[:10], file=regtest)
    print(t.to_pandas().head(10), file=regtest)


def test_ms_chromatogram_rt_range(data_path, regtest):
    pm = emzed.io.load_peak_map(data_path("210205_A8.mzML"))
    t = emzed.extract_ms_chromatograms(pm)
    rtmin, rtmax = t[0].chromatogram.rt_range()
    assert np.allclose((rtmin, rtmax), (70.092, 383.179))
