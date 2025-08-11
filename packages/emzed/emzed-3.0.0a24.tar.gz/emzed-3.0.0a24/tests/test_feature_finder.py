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


import os

import pytest

from emzed import PeakMap, Table
from emzed.peak_picking import (
    run_feature_finder_centwave,
    run_feature_finder_metabo,
    run_feature_finder_metabo_on_folder,
)


@pytest.fixture
def peak_maps_folder(pm, tmpdir):
    pm.save(tmpdir.join("1.mzML").strpath)
    pm.save(tmpdir.join("2.mzXML").strpath)
    yield tmpdir.strpath


def test_feature_finder_metabo_help(regtest):
    print(run_feature_finder_metabo.__doc__, file=regtest)


def test_feature_finder_metabo(regtest, data_path):
    pm = PeakMap.load(data_path("test.mzXML"))
    pm = pm.extract(mzmin=255, mzmax=262)
    peaks = run_feature_finder_metabo(pm, mtd_noise_threshold_int=10000)

    peaks.print_(max_rows=None, stream=regtest)
    print(peaks.filter(peaks.feature_size == 5), file=regtest)


def test_feature_finder_centwave(regtest, data_path):
    pm = PeakMap.load(data_path("new.mzXML"))
    pm = pm.extract(mslevelmax=1, mzmin=1700)
    peaks = run_feature_finder_centwave(pm, peakwidth=(15, 30))

    peaks.print_(max_rows=None, stream=regtest)


def test_feature_finder_centwave_empty(regtest, data_path):
    pm = PeakMap.load(data_path("test.mzXML"))
    # creates an empty result:
    peaks = run_feature_finder_centwave(pm, peakwidth=(15, 30))
    peaks.print_(max_rows=None, stream=regtest)


def test_feature_finder_metabo_ms2(regtest, data_path):
    pm = PeakMap.load(data_path("peaks_for_ms2_extraction.mzXML"))
    peaks = run_feature_finder_metabo(pm, ms_level=2, verbose=False)
    peaks = peaks.sort_by("precursors")
    for t in peaks.split_by_iter("precursors"):
        print(
            "precursors=", t.precursors.unique_value(), "#peaks=", len(t), file=regtest
        )

    peaks = run_feature_finder_metabo(
        pm, ms_level=2, verbose=False, run_feature_grouper=False
    )
    print(peaks, file=regtest)


def test_feature_finder_metabo_no_grouping(regtest, pm):
    peaks = run_feature_finder_metabo(
        pm,
        run_feature_grouper=False,
        mtd_noise_threshold_int=2000,
        common_chrom_peak_snr=2000.0,
        mtd_reestimate_mt_sd="true",
        ffm_charge_upper_bound=2,
    )
    print(peaks, file=regtest)


def test_feature_finder_metabo_on_folder(peak_maps_folder, tmpdir, regtest):
    out_folder = tmpdir.join("peaks").strpath

    run_feature_finder_metabo_on_folder(
        peak_maps_folder,
        out_folder=out_folder,
        n_cores=1,
        mtd_noise_threshold_int=2000.0,
        common_chrom_peak_snr=2000.0,
        run_feature_grouper=False,
        mtd_reestimate_mt_sd="true",
        ffm_charge_upper_bound=2,
    )
    assert sorted(os.listdir(out_folder)) == ["1_peaks.table", "2_peaks.table"]
    assert len(Table.open(tmpdir.join("peaks").join("1_peaks.table").strpath)) == 3
    assert len(Table.open(tmpdir.join("peaks").join("2_peaks.table").strpath)) == 3
