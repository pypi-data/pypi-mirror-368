#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>

import os
from contextlib import contextmanager

import pytest

import emzed
from emzed import PeakMap, Table
from emzed.config import folders
from emzed.utils import mock_emzed_gui

from .helpers import is_ci


@pytest.fixture
def patch_emzed_folder(monkeypatch, tmpdir):
    folder = tmpdir.join("emzed3").strpath
    os.makedirs(folder)
    monkeypatch.setattr(folders, "get_emzed_folder", lambda: folder)


@pytest.fixture
def patch_ask_for_single_file(data_path):
    @contextmanager
    def patch(file_name):
        with mock_emzed_gui() as emzed_gui:
            emzed_gui.ask_for_single_file = lambda *a, **kw: data_path(file_name)
            yield file_name

    yield patch


@pytest.fixture
def patch_ask_for_multiple_files(data_path):
    @contextmanager
    def patch(file_name):
        with mock_emzed_gui() as emzed_gui:
            emzed_gui.ask_for_multiple_files = lambda *a, **kw: [data_path(file_name)]
            yield file_name

    yield patch


@pytest.fixture
def patch_ask_for_multiple_files_cancel():
    with mock_emzed_gui() as emzed_gui:
        emzed_gui.ask_for_multiple_files = lambda *a, **kw: None
        yield


@pytest.fixture
def patch_ask_for_save(data_path, tmpdir):
    @contextmanager
    def patch(file_name):
        with mock_emzed_gui() as emzed_gui:
            path = tmpdir.join(file_name).strpath
            emzed_gui.ask_for_save = lambda *a, **kw: path
            yield path

    yield patch


@pytest.fixture
def patch_ask_for_single_file_cancel():
    with mock_emzed_gui() as emzed_gui:
        emzed_gui.ask_for_single_file = lambda *a, **kw: None
        yield


@pytest.fixture
def locations(patch_emzed_folder):
    emzed.io.locations = emzed.io.LocationManager()
    yield emzed.io.locations


def test_locations_manager_invalid_json(patch_emzed_folder):
    from emzed.config import folders

    emzed_folder = folders.get_emzed_folder()

    locations_file = os.path.join(emzed_folder, "last_locations.json")
    with open(locations_file, "w") as fh:
        print("invalid json", file=fh)

    locations = emzed.io.LocationManager()

    assert not os.path.exists(locations_file)
    assert len(locations) == 0


@pytest.mark.skipif(
    is_ci(),
    reason="linux ci will fail because tests run as root and on windows os.chmod does"
    " not work as expected, see https://stackoverflow.com/questions/27500067",
)
def test_locations_manager_io_error(patch_emzed_folder):
    locations = emzed.io.LocationManager()
    # enforce file creation:
    locations.update("x", "y")

    os.chmod(locations.path, 0)
    with pytest.warns(UserWarning) as record:
        emzed.io.LocationManager()
    os.chmod(locations.path, 0o644)

    assert record.list[0].message.args[0].startswith("can not open")


def test_load_peak_map(data_path, locations):
    assert len(locations) == 0
    pm = emzed.io.load_peak_map(data_path("test_smaller.mzXML"))
    assert len(pm) > 0
    assert len(locations) == 0


def test_load_peak_map_gui(data_path, locations, patch_ask_for_single_file):
    assert len(locations) == 0

    with patch_ask_for_single_file("test.mzXML"):
        pm = emzed.io.load_peak_map()
    assert len(pm) > 0
    assert len(locations) == 1

    # calling the method again triggers lookup of last location:
    # we do this to improve test coverage
    with patch_ask_for_single_file("test.mzXML"):
        pm = emzed.io.load_peak_map()
    assert len(pm) > 0
    assert len(locations) == 1


def test_load_peak_map_gui_cancel(
    data_path, locations, patch_ask_for_single_file_cancel
):
    assert len(locations) == 0
    pm = emzed.io.load_peak_map()
    assert pm is None
    assert len(locations) == 0


def test_load_csv_gui(data_path, locations, patch_ask_for_single_file, regtest):
    assert len(locations) == 0
    with patch_ask_for_single_file("minimal.csv"):
        t = emzed.io.load_csv(delimiter=";")
    assert len(t) > 0
    assert len(locations) == 1
    print(t, file=regtest)

    # calling the method again triggers lookup of last location:
    # we do this to improve test coverage
    with patch_ask_for_single_file("minimal.csv"):
        t = emzed.io.load_csv()
    assert len(t) > 0
    assert len(locations) == 1


def test_load_excel_gui(data_path, locations, patch_ask_for_single_file, regtest):
    assert len(locations) == 0

    with patch_ask_for_single_file("table.xlsx"):
        t = emzed.io.load_excel()

    assert len(t) > 0
    assert len(locations) == 1
    print(t, file=regtest)

    # calling the method again triggers lookup of last location:
    # we do this to improve test coverage
    with patch_ask_for_single_file("table.xlsx"):
        t = emzed.io.load_excel()
    assert len(t) > 0
    assert len(locations) == 1


def test_load_table_gui(data_path, locations, patch_ask_for_single_file, regtest):
    assert len(locations) == 0

    with patch_ask_for_single_file("peaks.table"):
        t = emzed.io.load_table()
    assert len(t) > 0
    assert len(locations) == 1
    print(t, file=regtest)

    # calling the method again triggers lookup of last location:
    # we do this to improve test coverage
    with patch_ask_for_single_file("peaks.table"):
        t = emzed.io.load_table()
    assert len(t) > 0
    assert len(locations) == 1


def test_save_peak_map_gui(data_path, locations, patch_ask_for_save):
    assert len(locations) == 0
    pm = PeakMap.load(data_path("test_smaller.mzXML"))
    with patch_ask_for_save("test.mzXML") as target_file:
        emzed.io.save_peak_map(pm)

    pm_back = PeakMap.load(target_file)
    assert len(pm) == len(pm_back)
    assert len(locations) == 1

    # calling the method again triggers lookup of last location:
    # we do this to improve test coverage
    with patch_ask_for_save("test.mzXML") as target_file:
        emzed.io.save_peak_map(pm)
    assert len(locations) == 1


def test_save_table_gui(data_path, locations, patch_ask_for_save):
    assert len(locations) == 0
    t = Table.load(data_path("peaks.table"))
    with patch_ask_for_save("test.table") as target_file:
        emzed.io.save_table(t)

    t_back = Table.load(target_file)
    assert len(t) == len(t_back)
    assert len(locations) == 1

    # calling the method again triggers lookup of last location:
    # we do this to improve test coverage
    with patch_ask_for_save("test.table") as target_file:
        emzed.io.save_table(t)
    assert len(locations) == 1


def test_save_csv_gui(data_path, locations, patch_ask_for_save, regtest):
    assert len(locations) == 0
    t = Table.load(data_path("peaks.table"))
    with patch_ask_for_save("test.csv") as target_file:
        emzed.io.save_csv(t, delimiter=",")

    t_back = Table.load_csv(target_file, delimiter=",")
    print(t_back, file=regtest)
    assert len(locations) == 1

    # calling the method again triggers lookup of last location:
    # we do this to improve test coverage
    with patch_ask_for_save("test.csv") as target_file:
        emzed.io.save_csv(t)
    assert len(locations) == 1


def test_save_excel_gui(data_path, locations, patch_ask_for_save, regtest):
    assert len(locations) == 0
    t = Table.load(data_path("peaks.table"))
    with patch_ask_for_save("test.xlsx") as target_file:
        emzed.io.save_excel(t)

    t_back = Table.load_excel(target_file)
    print(t_back, file=regtest)
    assert len(locations) == 1

    # calling the method again triggers lookup of last location:
    # we do this to improve test coverage
    with patch_ask_for_save("test.xlsx") as target_file:
        emzed.io.save_excel(t)
    assert len(locations) == 1


def test_load_tables(data_path):
    tables = emzed.io.load_tables(data_path("peaks.tabl?"))
    assert len(tables) == 1


def test_load_csvs(data_path):
    tables = emzed.io.load_csvs(data_path("minimal.cs?"))
    assert len(tables) == 1


def test_load_excels_with_wildcards(data_path):
    tables = emzed.io.load_excels(data_path("table.xls?"))
    assert len(tables) == 1


def test_load_peak_maps(data_path):
    pm = emzed.io.load_peak_maps(data_path("test_smalle?.mzXML"))
    assert len(pm) == 1


def test_load_peak_maps_gui(data_path, locations, patch_ask_for_multiple_files):
    assert len(locations) == 0

    with patch_ask_for_multiple_files("test.mzXML"):
        pms = emzed.io.load_peak_maps()
    assert len(pms) == 1
    assert len(locations) == 1

    # calling the method again triggers lookup of last location:
    # we do this to improve test coverage
    with patch_ask_for_multiple_files("test.mzXML"):
        pms = emzed.io.load_peak_maps()
    assert len(pms) == 1
    assert len(locations) == 1


def test_load_peak_maps_gui_cancel(locations, patch_ask_for_multiple_files_cancel):
    assert len(locations) == 0
    pms = emzed.io.load_peak_maps()
    assert pms is None
    assert len(locations) == 0
