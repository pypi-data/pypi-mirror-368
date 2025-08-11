#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>

import os

import numpy as np
import pytest

from emzed import RtType, Table
from emzed.align import align_peaks, mz_align, rt_align
from emzed.io import load_table


@pytest.mark.parametrize("model", ["lowess", "b_spline"])
def test_rt_align(data_path, tmpdir, model):
    t1 = load_table(data_path("peaks.table"))

    # t2 = t1.filter(t1.feature_id < 10).consolidate()
    t2 = Table.stack_tables(100 * [t1])

    t2.replace_column("rt", t2.rt * 1.1, float)
    t2.replace_column("rtmin", t2.rtmin * 1.1, float)
    t2.replace_column("rtmax", t2.rtmax * 1.1, float)

    t1_aligned, t2_aligned = rt_align([t1, t2], destination=tmpdir.strpath, model=model)

    assert tmpdir.join("test_smaller_aligned.png").exists()

    del t1_aligned.meta_data["rt_aligned"]  # needed for equality check in next line

    return

    # peaks in t1 were not changed:
    assert t1 == t1_aligned

    t1_rt = np.array(list(t1.rt))
    t2_aligned_rt = np.array(list(t2_aligned.rt))

    # now t2_altigned rt values should be close to them from the ref table:
    assert np.allclose(t1_rt[:-1], t2_aligned_rt, atol=0, rtol=0.0001)

    pm1_rts = np.array([s.rt for s in t1.peakmap.unique_value().spectra])
    pm2_rts = np.array([s.rt for s in t2_aligned.peakmap.unique_value().spectra])

    # the first two spectra are not very well aligned, this is a known border effect:
    assert np.allclose(pm1_rts[3:] / pm2_rts[3:], 1.1, atol=0, rtol=8e-4)


@pytest.mark.parametrize(
    "model, model_parameters",
    [("lowess", dict(span=0.666)), ("b_spline", dict(num_nodes=5))],
)
def test_rt_align_with_reference_table(data_path, tmpdir, model, model_parameters):
    t1 = load_table(data_path("peaks.table"))

    t2 = t1.filter(t1.feature_id < 10).consolidate()
    t2.replace_column("rt", t2.rt * 1.1, float)
    t2.replace_column("rtmin", t2.rtmin * 1.1, float)
    t2.replace_column("rtmax", t2.rtmax * 1.1, float)

    (t2_aligned,) = rt_align(
        [t2], reference_table=t1, destination=None, model=model, **model_parameters
    )

    assert tmpdir.listdir() == []

    t1_rt = np.array(list(t1.rt))
    t2_aligned_rt = np.array(list(t2_aligned.rt))

    # now t2_altigned rt values should be close to them from the ref table:
    assert np.allclose(t1_rt[:-1], t2_aligned_rt, atol=0, rtol=0.0001)

    pm1_rts = np.array([s.rt for s in t1.peakmap.unique_value().spectra])
    pm2_rts = np.array([s.rt for s in t2_aligned.peakmap.unique_value().spectra])

    # the first two spectra are not very well aligned, this is a known border effect:
    assert np.allclose(pm1_rts[3:] / pm2_rts[3:], 1.1, atol=0, rtol=8e-4)


def test_rt_align_with_integrated_table(data_path, tmpdir):
    t1 = load_table(data_path("peaks.table"))

    t1.add_column_with_constant_value("peak_shape_model", None, object)
    t1.add_column_with_constant_value("area", None, float)
    t1.add_column_with_constant_value("rmse", None, float)
    t1.add_column_with_constant_value("valid_model", None, bool)

    t2 = t1.consolidate()

    with pytest.raises(ValueError):
        rt_align([t1, t2], reference_table=t1, destination=tmpdir.strpath, n_peaks=0.8)

    t1a, t2a = rt_align(
        [t1, t2],
        reference_table=t1,
        destination=tmpdir.strpath,
        reset_integration=True,
        n_peaks=0.8,
    )

    # can not align already aligned tables
    with pytest.raises(ValueError):
        rt_align([t1a, t2a], destination=tmpdir.strpath, reset_integration=True)


def test_rt_align_invalid_settings(data_path, regtest):
    t1 = load_table(data_path("peaks.table"))

    # invalid model
    with pytest.raises(ValueError) as e:
        rt_align([t1], model="xxxx")
    print(e.value, file=regtest)

    # misspelled n_points:
    with pytest.raises(ValueError) as e:
        rt_align([t1], npoints=3)
    print(e.value, file=regtest)

    with pytest.raises(ValueError) as e:
        rt_align([t1], npoints=3, model="lowess")
    print(e.value, file=regtest)

    # negative value
    with pytest.raises(ValueError) as e:
        rt_align([t1], num_nodes=-3)
    print(e.value, file=regtest)

    # span out of range 0 .. 1
    with pytest.raises(ValueError) as e:
        rt_align([t1], span=3.0, model="lowess")
    print(e.value, file=regtest)

    # invalid setting
    with pytest.raises(ValueError) as e:
        rt_align([t1], interpolation_type="xxx", model="lowess")
    print(e.value, file=regtest)


def test_mz_align(data_path, regtest, tmpdir):
    t1 = load_table(data_path("peaks.table"))

    ref_table = t1.filter((t1.mz >= 260) & (t1.mz <= 550)).consolidate()
    ref_table.replace_column("mz", ref_table.mz * 1.000001, float)
    ref_table.replace_column("rtmin", ref_table.rtmin * 0.8, RtType)
    ref_table.replace_column("rtmax", ref_table.rtmax * 1.2, RtType)
    ref_table.add_column(
        "name", ref_table.apply(lambda id: f"compound_{id}", ref_table.id), str
    )
    ref_table.add_column_with_constant_value("polarity", "0", str)
    ref_table = ref_table.extract_columns(
        "id", "mz", "rtmin", "rtmax", "polarity", "name"
    )

    aligned = mz_align(t1, ref_table, destination=tmpdir.strpath, tol=1e-2)
    print(aligned, file=regtest)

    before_mzs = [s.mzs for s in t1.peakmap.unique_value().spectra]
    after_mzs = [s.mzs for s in aligned.peakmap.unique_value().spectra]

    for mzs_b, mzs_a in zip(before_mzs, after_mzs):
        assert (np.linalg.norm(mzs_b - mzs_a)) > 0.0

    assert set(os.listdir(tmpdir.strpath)) == set(
        [
            "test_smaller_mzalign.png",
            "test_smaller_matches.table",
            "test_smaller_matches.csv",
            "test_smaller_reference.table",
        ]
    )

    loaded = load_table(tmpdir.join("test_smaller_matches.table").strpath)
    print(loaded, file=regtest)

    loaded_ref_table = load_table(tmpdir.join("test_smaller_reference.table").strpath)
    loaded_ref_table.meta_data.clear()

    assert ref_table == loaded_ref_table


def test_align_peaks(data_path, regtest):
    peaks_0 = load_table(data_path("peaks.table"))

    assert len(peaks_0) == 11

    peaks_1 = peaks_0[:8].consolidate()
    peaks_2 = peaks_0[3:].consolidate()

    peaks_1.replace_column("rt", peaks_1.rt + 1)
    peaks_2.replace_column("rt", peaks_2.rt + 2)

    peaks_1.replace_column("mz", peaks_1.mz + 1e-7)
    peaks_2.replace_column("mz", peaks_2.mz + 2e-7)

    align_peaks([peaks_0, peaks_1, peaks_2], 3e-7, 3)

    assert (
        set(peaks_0.global_peak_id),
        set(peaks_1.global_peak_id),
        set(peaks_2.global_peak_id),
    ) == (
        {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10},
        {0, 1, 2, 3, 4, 5, 6, 7},
        {3, 4, 5, 6, 7, 8, 9, 10},
    )


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "--pdb"])
