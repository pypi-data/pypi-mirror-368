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

import numpy as np
import pytest

import emzed
from emzed import Table, to_table
from emzed.ms_data.peak_map import Chromatogram
from emzed.quantification import (
    available_peak_shape_models,
    integrate,
    integrate_chromatograms,
)


@pytest.fixture(scope="module")
def peak_table(data_path):
    rv = Table.load(data_path("peaks.table"))
    rv._set_value([0], "rtmin", rv[0].rtmax + 1.0)  #  enforce empty EIC
    return rv


@pytest.fixture(scope="module")
def peak_table_1(data_path):
    return Table.load(data_path("peaks1.table"))


def test_model_names():
    assert sorted(available_peak_shape_models) == [
        "asym_gauss",
        "emg",
        "linear",
        "no_integration",
        "sgolay",
    ]


def test_invalid_integrator_name(peak_table, regtest):
    with pytest.raises(ValueError) as e:
        integrate(peak_table, "unknown")

    print(e.value, file=regtest)


@pytest.mark.parametrize(
    "method", ["no_integration", "emg", "asym_gauss", "linear", "sgolay"]
)
def test_integrator(peak_table, regtest, method):
    table = integrate(peak_table, method)
    assert table != peak_table

    print(table, file=regtest)


@pytest.mark.parametrize(
    "method", ["no_integration", "emg", "asym_gauss", "linear", "sgolay"]
)
def test_integrator_with_path(peak_table, tmp_path, regtest, method):
    path = tmp_path / "integrated.table"
    table = integrate(peak_table, method, path=path)
    assert table != peak_table
    table = Table.open(path)
    print(table, file=regtest)


def test_integrate_twice(peak_table):
    peak_table = integrate(peak_table, "linear")
    integrate(peak_table, "no_integration")


def test_integrator_parallel(peak_table):
    table_parallel = integrate(
        peak_table, "emg", n_cores=3, min_size_for_parallel_execution=0
    )
    table_serial = integrate(peak_table, "emg", n_cores=1)

    assert table_serial == table_parallel


def test_integrator_parallel_with_path(peak_table, tmp_path):
    path0 = tmp_path / "integrated0.table"
    table_parallel = integrate(
        peak_table, "emg", n_cores=3, min_size_for_parallel_execution=0, path=path0
    )
    path1 = tmp_path / "integrated1.table"
    table_serial = integrate(peak_table, "emg", n_cores=1, path=path1)

    assert table_serial == table_parallel


@pytest.mark.parametrize(
    "method", ["no_integration", "emg", "asym_gauss", "linear", "sgolay"]
)
def test_integrator_in_place(peak_table, method):
    table = integrate(peak_table, method)
    assert integrate(peak_table, method, in_place=True) is None
    assert table == peak_table


def test_integrator_in_place_twice_error(peak_table):
    fake = to_table("a", [1], int)
    integrate(peak_table, "no_integration", in_place=True)
    pm = peak_table.join(fake)
    integrate(pm, "emg", in_place=True)
    # crashed before:
    integrate(pm, "emg", in_place=True)


def test_integrator_in_place_parallel(peak_table):
    table = integrate(peak_table, "emg", n_cores=3, min_size_for_parallel_execution=0)
    assert integrate(peak_table, "emg", n_cores=3, in_place=True) is None
    assert table == peak_table


def test_integrator_with_missing_window_values(peak_table_1, regtest):
    table = integrate(peak_table_1, "emg")
    t = table.sort_by("id")
    print(t, file=regtest)


def test_ms_chromatogram_integration(data_path, regtest):
    pm = emzed.io.load_peak_map(data_path("210205_A8.mzML"))
    t = emzed.extract_ms_chromatograms(pm)

    integrated_peaks = integrate_chromatograms(t[10:20], "emg", n_cores=3)

    # mitigate numerical differences on different ci servers:
    integrated_peaks.set_col_format("area_chromatogram", "%.0e")
    integrated_peaks.set_col_format("rmse_chromatogram", "%.0e")
    print(integrated_peaks, file=regtest)


def test_chromatogram_integration(data_path, regtest):
    peaks = emzed.io.load_table(data_path("peaks.table"))
    t = emzed.extract_chromatograms(peaks)
    integrated_peaks = integrate_chromatograms(t, "emg", n_cores=3)

    print(integrated_peaks, file=regtest)


def test_chromatogram_integration_with_postfix(data_path):
    peaks = emzed.io.load_table(data_path("peaks.table"))
    t = emzed.extract_chromatograms(peaks)
    t1 = t.copy()
    t = t.join(t1, t.id == t1.id)
    integrated_peaks = integrate_chromatograms(t, "linear")
    assert "peak_shape_model_chromatogram__0" in integrated_peaks.col_names


def test_issue_205_integration_chromatogram_different_dtype(data_path, snapshot):
    peaks = emzed.io.load_table(data_path("peaks.table"))
    t = emzed.extract_chromatograms(peaks)

    def break_dtype(c):
        return Chromatogram(
            c.rts.astype(np.float64),
            c.intensities.astype(np.float32),
        )

    t.replace_column("chromatogram", t.apply(break_dtype, t.chromatogram))
    t2 = integrate_chromatograms(t, "emg")
    snapshot.check(np.array(t2[0].model_chromatogram._getstate()), atol=0, rtol=1e-6)


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
