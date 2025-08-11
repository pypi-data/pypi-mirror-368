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


import multiprocessing
import os
import pickle
import sys

import numpy as np
import pytest

from emzed import PeakMap
from emzed.ms_data.peak_map import Spectrum


def test_basic(pm, pp):
    assert len(pm.spectra) == 928
    assert pm.meta_data is not None
    pp(sorted(pm.meta_data.keys()))
    pp(pm.mz_range())
    pp(pm.rt_range())

    assert pm == pm  # check __eq__


def test_mz_and_rt_range(pm, data_path, pp):
    pp(pm.ms_levels())
    pp()
    pp(pm.mz_range(None))
    pp(pm.mz_range(1))
    pp(pm.mz_range(2))
    pp()
    pp(pm.rt_range(None))
    pp(pm.rt_range(1))
    pp(pm.rt_range(2))
    pp()

    pm = PeakMap.load(data_path("ms1_and_ms2_mixed.mzML"))
    pp(pm.ms_levels())
    pp()
    pp(pm.mz_range(None))
    pp(pm.mz_range(1))
    pp(pm.mz_range(2))
    pp()
    pp(pm.rt_range(None))
    pp(pm.rt_range(1))
    pp(pm.rt_range(2))
    pp()


def test_spectrum_precursors(data_path, pp):
    pm = PeakMap.load(data_path("ms1_and_ms2_mixed.mzML"))
    lens = [len(s.precursors) for s in pm]
    assert sum(lens) == 1085


def test_unique_id_0(pm):
    rtmin, rtmax = pm.rt_range()
    mean_rt = (rtmin + rtmax) / 2.0
    pm1 = pm.extract(rtmax=mean_rt)
    pm2 = pm.extract(rtmin=mean_rt)

    pm1.merge(pm2)
    # merge does not update meta_data, thus:
    assert pm1.unique_id != pm.unique_id

    pm1.meta_data.clear()
    pm1.meta_data.update(pm.meta_data)
    assert pm1.unique_id == pm.unique_id


@pytest.mark.skipif(sys.platform != "darwin", reason="unique id is platform dependent")
def test_unique_id_1(pm, regtest):
    print(pm.unique_id, file=regtest)

    spectrum = Spectrum(9999, 2000, 1, "+", [], pm.spectra[-1].peaks.copy())
    with pm.spectra_for_modification() as spectra:
        spectra.add_spectrum(spectrum)

    print(pm.unique_id, file=regtest)


@pytest.mark.skipif(sys.platform == "win32", reason="output paths are different on win")
def test_pm_load_error_handling(pp, tmpdir):
    with pytest.raises(OSError) as e:
        PeakMap.load("/nonexisting" * 10)
    pp(e.value)

    os.chdir(tmpdir.strpath)
    with pytest.raises(OSError) as e:
        PeakMap.load(".")
    pp(e.value)


def test_pm_io(pm, tmpdir):
    path = tmpdir.join("peaks.mzML").strpath
    pm.save(path)
    pm_back = PeakMap.load(path)

    pm_back.meta_data.update(pm.meta_data)  # fix file path info in meta_data
    assert pm == pm_back

    path = tmpdir.join("test_smaller.mzXML").strpath
    pm.save(path)
    pm_back = PeakMap.load(path)

    pm_back.meta_data.update(pm.meta_data)  # fix file path info in meta_data
    assert pm == pm_back

    assert pm.polarities() == set("0")


def test_chromatogram(pm, pp):
    rts, intensities = pm.chromatogram(300, 301.0, 13, 14, 1)
    assert len(rts) == 66
    assert len(intensities) == len(rts)
    assert all(13 <= rt <= 14 for rt in rts)
    pp(rts)
    pp(rts.dtype)
    pp()
    pp(intensities)
    pp(intensities.dtype)


def test_total_tic(pm, pp):
    rts, intensities = pm.chromatogram(None, None, None, None)
    assert len(intensities) == len(rts)


def _test(pm):
    return pm.meta_data["source"]


def test_multiprocessing(pm_on_disk):
    with multiprocessing.Pool(2) as pool:
        result = pool.map(_test, [pm_on_disk, pm_on_disk])
    print(result)


def test_chromatogram_parallel(pm, tmpdir):
    path = tmpdir.join("data.mzXML").strpath
    pm.save(path)

    target_db_file = tmpdir.join("data.db").strpath
    pm = PeakMap.load(path, target_db_file=target_db_file)

    args = [(300 + i, 301 + 1, i / 2, i / 2 + 2) for i in range(10)]

    with multiprocessing.Pool(2) as p:
        chromatograms = p.starmap(pm.chromatogram, args)

    assert len(chromatograms) == len(args)


def test_chromatogram_no_rt_limits(pm, pp):
    rts, intensities = pm.chromatogram(300, 301.0)
    assert len(rts) == 928
    assert len(intensities) == len(rts)

    rts, intensities = pm.chromatogram(300, 301.0, 13)
    assert len(rts) == 131
    assert len(intensities) == len(rts)

    rts, intensities = pm.chromatogram(300, 301.0, None, 14)
    assert len(rts) == 863
    assert len(intensities) == len(rts)


def test_representing_mz_peak(pm, pp):
    mz = pm.representing_mz_peak(300, 301.0, 13, 14, 1)
    assert abs(mz - 300.36447912336706) < 1e-15

    mz = pm.representing_mz_peak(300, 300.0000001, 13, 14, 1)
    assert mz is None


def test_extract(pm):
    pm2 = pm.extract(0, 2000, 1, 25, imin=0, imax=1e38)
    assert len(pm2) == 874
    assert all(1 <= s.rt <= 25 for s in pm2.spectra)

    pm2 = pm.extract(100, 700, 1, 25, 5000, 10000, mslevelmin=1, mslevelmax=1)

    assert len(pm2) == 874
    assert all(1 <= s.rt <= 25 for s in pm2.spectra)

    assert all(np.all(s.mzs >= 100) for s in pm2.spectra)
    assert all(np.all(s.mzs <= 700) for s in pm2.spectra)
    assert all(np.all(s.intensities >= 5000) for s in pm2.spectra)
    assert all(np.all(s.intensities <= 10000) for s in pm2.spectra)


def test_extract_with_ms2(data_path):
    pm = PeakMap.load(data_path("peaks_for_ms2_extraction.mzXML"))
    pm2 = pm.extract(imin=0)
    assert (
        len([s.precursors for s in pm.spectra])
        == len([s.precursors for s in pm2.spectra])
        > 0
    )
    pm3 = pm2.extract(precursormzmin=330, precursormzmax=331)
    assert len(pm3) == 12
    assert all(330 <= s.precursors[0][0] <= 331 for s in pm3.spectra)

    pm4 = pm2.extract(mzmin=80, mzmax=500)
    assert [s.precursors for s in pm4.spectra] == [s.precursors for s in pm2.spectra]


def test_spectra_get_precursor_mzs(data_path):
    pm = PeakMap.load(data_path("peaks_for_ms2_extraction.mzXML"))
    precursors = pm.get_precursors_mzs()
    assert len(precursors) == 872
    assert all(isinstance(p, tuple) for p in precursors)
    assert all(len(p) == 1 for p in precursors)
    assert all(isinstance(p[0], float) for p in precursors)


def test_split_by_precursors(data_path):
    pm = PeakMap.load(data_path("peaks_for_ms2_extraction.mzXML"))
    # reduce for speeding up:
    pm = pm.extract(precursormzmin=700)
    pms = pm.split_by_precursors(mz_tol=1.0)
    assert len(pms) == 7
    assert sum(len(v) for v in pms.values()) == len(pm)


def test_extract_empty(pm):
    pm2 = pm.extract(mslevelmin=2, mslevelmax=3)
    assert len(pm2) == 0

    n = len(pm)

    pm.merge(pm2)

    assert len(pm) == n


def test_spectra(pm, pp):
    for spec in pm.spectra[:5]:
        pp(str(spec))

    pp()

    for _, spec in zip(range(5), pm.spectra):
        pp(str(spec))

    pp()
    pp(str(pm.spectra[-1]))

    pp()
    pp(len(pm.spectra[-1].mzs))
    pp(len(pm.spectra[-1].intensities))


def test_ms2_peakmap(data_path, pp):
    pm = PeakMap.load(data_path("peaks_for_ms2_extraction.mzXML"))
    pp(len(pm))
    for spec in pm.spectra[:5]:
        pp(str(spec))

    assert pm.mz_range(None) == pm.mz_range(2)


def test_pickle_peakmap(data_path):
    pm = PeakMap.load(data_path("peaks_for_ms2_extraction.mzXML"))
    with pytest.raises(NotImplementedError):
        pickle.dumps(pm)


def test_peakmap_add_spectrum(data_path):
    pm = PeakMap.load(data_path("peaks_for_ms2_extraction.mzXML"))

    spectrum = Spectrum(9999, 2000, 1, "+", [], pm.spectra[-1].peaks.copy())
    with pm.spectra_for_modification() as spectra:
        spectra.add_spectrum(spectrum)
    assert pm.spectra[-1] == spectrum


def test_spectrum_setters(data_path):
    pm = PeakMap.load(data_path("peaks_for_ms2_extraction.mzXML"))
    before = pm.spectra[0].peaks

    with pm.spectra_for_modification() as spectra:
        spectrum = spectra[0]
        spectrum.peaks = spectrum.peaks[1:, :]
        assert np.all(before[1:, :] == spectrum.peaks)

        spectrum.rt = 9999
        assert spectrum.rt == 9999

        spectrum.rt = 99999
        assert spectrum.rt == 99999

        with pytest.raises(AssertionError):
            spectrum.rt = -1

        with pytest.raises(AssertionError):
            spectrum.rt = "a"

        with pytest.raises(AttributeError):
            spectrum.scan_number = 99999

        spectrum.ms_level = 9
        assert spectrum.ms_level == 9

        spectrum.ms_level = 10
        assert spectrum.ms_level == 10

        with pytest.raises(AssertionError):
            spectrum.ms_level = "a"

        with pytest.raises(AssertionError):
            spectrum.ms_level = 0

        spectrum.polarity = "-"
        assert spectrum.polarity == "-"

        spectrum.polarity = "0"
        assert spectrum.polarity == "0"

        with pytest.raises(AssertionError):
            spectrum.polarity = 0

        with pytest.raises(AssertionError):
            spectrum.polarity = "NEUTRAL"

    spectrum = pm.spectra[0]
    assert np.all(before[1:, :] == spectrum.peaks)

    assert spectrum.rt == 99999
    assert spectrum.ms_level == 10
    assert spectrum.polarity == "0"


def test_filter_same(pm, data_path):
    same_pm = pm.filter(lambda spectrum: True)
    assert pm == same_pm


def test_filter_ms_level_1(data_path):
    pm = PeakMap.load(data_path("peaks_for_ms2_extraction.mzXML"))
    only_ms1 = pm.filter(lambda spectrum: spectrum.ms_level == 1)
    assert len(only_ms1) == 0

    only_ms2 = pm.filter(lambda spectrum: spectrum.ms_level == 2)
    assert len(only_ms2) == len(pm)


def test_mrm_data(data_path, regtest, tmpdir):
    pm = PeakMap.load(data_path("mrm_data.mzML"))
    assert len(pm.spectra) == 0
    assert len(pm.ms_chromatograms) == 8
    for c in pm.ms_chromatograms:
        print(c, file=regtest)

    path = tmpdir.join("test.mzML").strpath
    pm.save(path)
    pm2 = PeakMap.load(path)

    pm2.meta_data.clear()
    pm.meta_data.clear()

    assert pm == pm2


def test_chromatogram_multiplexed(data_path):
    pm = PeakMap.load(data_path("multiplexed_short.mzML"))
    rts, iis = pm.chromatogram(ms_level=2, precursormzmax=600)
    assert len(rts) == 16
    assert len(rts) == len(set(rts))
    assert list(rts) == sorted(rts)


def test_spectra_get_precursor_mzs_multiplexed(data_path):
    pm = PeakMap.load(data_path("multiplexed_short.mzML"))
    pms = pm.split_by_precursors(mz_tol=0.01)
    assert len(pms) == 3
    tobe = {
        (378.33, 473.17, 631.23, 947.1): 5,
        (429.95, 537.44, 717.26, 1076.14): 6,
        (481.57, 602.21, 803.29, 1205.18): 5,
    }
    for pc, pm in pms.items():
        assert tobe[pc] == len(pm)


def test_peakmap_open(data_path, tmpdir, regtest):
    target_db_file = tmpdir / "peaks.db"
    PeakMap.load(
        data_path("peaks_for_ms2_extraction.mzXML"), target_db_file=target_db_file
    )

    pm = PeakMap.open(target_db_file)
    assert not pm.is_in_memory()

    only_ms1 = pm.filter(lambda spectrum: spectrum.ms_level == 1)
    assert len(only_ms1) == 0

    only_ms2 = pm.filter(lambda spectrum: spectrum.ms_level == 2)
    assert len(only_ms2) == len(pm)

    assert pm.is_open()

    print(pm, file=regtest)
    pm.close()
    assert not pm.is_open()
    print(pm, file=regtest)

    with pytest.raises(ValueError) as e:
        len(pm)

    assert e.value.args[0] == "PeakMap is closed."


def test_set_of_pms(pm):
    pm1 = pm
    pm2 = pm.extract(rtmin=100)
    pm3 = pm

    assert len(set([pm1, pm2, pm3])) == 2


def test_multiple_polarities(data_path):
    pm = PeakMap.load(data_path("pos_neg_small.mzml"))

    assert pm.polarities() == {"+", "-"}

    # Test extraction
    pm_neg = pm.extract(polarity="-")
    assert pm_neg.polarities() == {"-"}
    assert len(pm_neg.spectra) == 416

    pm_pos = pm.extract(polarity="+")
    assert pm_pos.polarities() == {"+"}
    assert len(pm_pos.spectra) == 415

    # Test chromatograms
    rts, iis = pm.chromatogram(polarity="-", mzmin=600)
    assert len(rts) == 416
    assert len(iis) == len(rts)

    rts, iis = pm.chromatogram(polarity="+", mzmax=700)
    assert len(rts) == 415
    assert len(iis) == len(rts)
