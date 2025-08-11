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

from emzed import PeakMap, Spectrum
from emzed.ms2 import attach_ms2_spectra, export_sirius_files, merge_spectra
from emzed.peak_picking import run_feature_finder_metabo


@pytest.mark.parametrize("mode", ["union", "all", "max_signal", "max_range"])
def test_attach_ms2_spectra(data_path, regtest, mode):
    pm = PeakMap.load(data_path("ms1_and_ms2_mixed_2.mzXML"))
    peaks = run_feature_finder_metabo(
        pm, mtd_noise_threshold_int=10000, common_chrom_peak_snr=2000
    )
    peaks.print_(max_rows=None, stream=regtest)

    assert set(s.ms_level for s in pm) == {1, 2}
    assert set(s.ms_level for s in peaks.peakmap.unique_values()[0]) == {1, 2}
    attach_ms2_spectra(peaks, mode=mode)
    assert "spectra_ms2" in peaks.col_names
    assert peaks.spectra_ms2.count_not_none() == 4
    for spectra in peaks.spectra_ms2.unique_values():
        for s in spectra:
            assert isinstance(s, Spectrum)

    def format(spectra):
        return str(spectra)[:15] + "..."

    peaks = peaks.filter(peaks.num_spectra_ms2 > 0)
    peaks.drop_columns("source")
    peaks.set_col_format("spectra_ms2", format)
    peaks.add_column(
        "num_spectra_ms2_attached", peaks.apply(len, peaks.spectra_ms2), int
    )
    peaks.print_(max_rows=None, stream=regtest)


def test_merge_spectra(data_path, regtest):
    pm = PeakMap.load(data_path("ms1_and_ms2_mixed.mzML"))
    # reduce size
    pm = pm.extract(mslevelmin=2.0, precursormzmin=810, precursormzmax=811)
    for pk, pmi in sorted(pm.split_by_precursors(0.1).items()):
        spec = merge_spectra(pmi, 0.1)
        print(pk, round(spec.rt, 1), spec.peaks.shape, file=regtest)

    # int type should work too:
    for pk, pmi in sorted(pm.split_by_precursors(0.1).items()):
        spec = merge_spectra(pmi, 1)
        print(pk, round(spec.rt, 1), spec.peaks.shape, file=regtest)


def test_sirius_export(data_path, regtest, tmpdir):
    pm = PeakMap.load(data_path("ms1_and_ms2_mixed.mzML"))
    peaks = run_feature_finder_metabo(
        pm, mtd_noise_threshold_int=10000, common_chrom_peak_snr=2000
    )

    assert set(s.ms_level for s in pm) == {1, 2}
    assert set(s.ms_level for s in peaks.peakmap.unique_values()[0]) == {1, 2}
    attach_ms2_spectra(peaks, mode="union")

    folder = tmpdir.strpath
    export_sirius_files(peaks, folder, abs_min_intensity=10, rel_min_intensity=0.1)

    for p in sorted(os.listdir(folder)):
        print(p, file=regtest)
        lines = open(os.path.join(folder, p)).readlines()
        for line in lines[:10]:
            print(line.rstrip(), file=regtest)
        print("...", file=regtest)
        print(file=regtest)

    with pytest.raises(ValueError):
        export_sirius_files(peaks, folder, abs_min_intensity=10, rel_min_intensity=0.1)

    export_sirius_files(
        peaks, folder, abs_min_intensity=10, rel_min_intensity=0.1, overwrite=True
    )
