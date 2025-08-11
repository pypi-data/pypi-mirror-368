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

import pickle

import numpy as np
import pytest

from emzed.quantification.peak_shape_models import (
    AsymmetricGaussModel,
    LinearInterpolationModel,
    SavGolModel,
    SimplifiedEmgModel,
)


def test_api(pm, regtest):
    model = LinearInterpolationModel.fit(pm, 0, 15, 300, 400, 1)
    print(round(model.area, 2), file=regtest)


@pytest.fixture
def chromatogram():
    rts = np.linspace(0, 10, 21)
    iis = 1e5 * np.exp(-((rts - 6) ** 2) / 5)
    yield (rts, iis)


@pytest.fixture
def linear_interpolation_model(chromatogram):
    yield LinearInterpolationModel._fit(*chromatogram, {})


@pytest.fixture
def asymmetric_gauss_model(chromatogram):
    yield AsymmetricGaussModel._fit(*chromatogram, {})


@pytest.fixture
def sav_gol_model(chromatogram):
    yield SavGolModel._fit(*chromatogram, {})


@pytest.fixture
def simplified_emg_model(chromatogram):
    yield SimplifiedEmgModel._fit(*chromatogram, {})


@pytest.fixture
def chromatogram_simplified_emg(simplified_emg_model, chromatogram):
    rts, iis = chromatogram
    yield (rts, simplified_emg_model.apply(rts))


def test_linear_interpolation_model_area(linear_interpolation_model):
    area_tobe = 393903.195615724
    assert abs(linear_interpolation_model.area - area_tobe) < 1e-8 * area_tobe


def test_linear_interpolation_model_rmse(linear_interpolation_model):
    assert linear_interpolation_model.rmse == 0.0


def test_linear_interpolation_model_graph(linear_interpolation_model, chromatogram):
    assert linear_interpolation_model.graph() == chromatogram


def test_asymmetric_gauss_model_area(asymmetric_gauss_model):
    area_tobe = 396332.7296
    assert abs(asymmetric_gauss_model.area - area_tobe) < 1e-8 * area_tobe


def test_asymmetric_gauss_model_rmse(asymmetric_gauss_model):
    assert asymmetric_gauss_model.rmse < 1e-10


def test_asymmetric_gauss_model_graph(asymmetric_gauss_model):
    rts, iis = asymmetric_gauss_model.graph()
    assert abs(np.mean(rts) - 6) < 1e-6 and abs(np.sum(iis) - 2615791.721974904) < 1e-6


def test_sav_gol_model_area(sav_gol_model):
    area_tobe = 395043.15092
    assert abs(sav_gol_model.area - area_tobe) < 1e-8 * area_tobe


def test_sav_gol_model_rmse(sav_gol_model):
    assert abs(sav_gol_model.rmse - 2543.6476265413994) < 1e-6


def test_sav_gol_model_graph(sav_gol_model):
    rts, iis = sav_gol_model.graph()
    assert abs(np.mean(rts) - 5) < 1e-6 and abs(np.sum(iis) - 791803.5488) < 1e-4


def test_simplified_emg_model_area(simplified_emg_model, chromatogram):
    area_tobe = 417575.015
    assert abs(simplified_emg_model.area - area_tobe) < 1e-8 * area_tobe


def test_simplified_emg_model_rmse(chromatogram_simplified_emg):
    model = SimplifiedEmgModel._fit(*chromatogram_simplified_emg, {})
    assert model.rmse < 1e-10


def test_simplified_emg_model_graph(simplified_emg_model, chromatogram):
    rts, iis = simplified_emg_model.graph()
    assert abs(np.mean(rts) - 6.547) < 1e-3 and abs(np.sum(iis) - 8324269) < 10


@pytest.mark.parametrize(
    "model_class",
    [AsymmetricGaussModel, LinearInterpolationModel, SavGolModel, SimplifiedEmgModel],
)
def test_pickling(model_class, chromatogram):
    model = model_class._fit(*chromatogram, {})
    assert pickle.loads(pickle.dumps(model)) == model
