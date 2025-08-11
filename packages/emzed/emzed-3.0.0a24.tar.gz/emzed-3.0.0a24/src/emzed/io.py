#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>

"""
This module contains multple functions for readin and writing tables and peakmaps
in different formats.

If emzed-gui is installed all functions will open file dialogs as fall-back when the
caller does not specify file paths.
"""

import glob
import json
import os
import warnings
from functools import partial

import tqdm

from emzed.config import folders
from emzed.ms_data import PeakMap
from emzed.table import Table
from emzed.utils import download, has_emzed_gui


def __dir__():
    return [
        "load_table",
        "load_csv",
        "load_excel",
        "load_peak_map",
        "load_tables",
        "load_csvs",
        "load_excels",
        "load_peak_maps",
        "save_table",
        "save_csv",
        "save_excel",
        "save_peak_map",
    ]


PEAKMAP_FILE_EXTENSIONS = ["mzml", "mzxml"]
TABLE_FILE_EXTENSIONS = ["table"]
EXCEL_FILE_EXTENSIONS = ["xlsx"]
CSV_FILE_EXTENSIONS = ["csv", "tsv"]


class LocationManager:
    def __init__(self):
        self.path = os.path.join(folders.get_emzed_folder(), "last_locations.json")
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as fh:
                    self.locations = json.load(fh)
            except OSError:
                warnings.warn(f"can not open {self.path} for reading")
            except json.JSONDecodeError:
                self.locations = {}
                try:
                    os.remove(self.path)
                except OSError:
                    pass
        else:
            self.locations = {}

    def get(self, key):
        return self.locations.get(key)

    def update(self, key, location):
        self.locations[key] = location
        with open(self.path, "w") as fh:
            json.dump(self.locations, fh)

    def __len__(self):
        return len(self.locations)


locations = LocationManager()


def load_peak_map(path=None):
    """Load peak-map.

    :param path: Path to the file to load. if not specified and if emzed-gui is
                 installed a user dialog will pop up and ask for the file.

    :returns: :py:class:`emzed.PeakMap`
    """
    return _load(path, "load_peak_map", PEAKMAP_FILE_EXTENSIONS, PeakMap.load)


def load_table(path=None):
    """Load table in ``emzed`` format.

    :param path: Path to the file to load. if not specified and if emzed-gui is
                 installed a user dialog will pop up and ask for the file.
    :returns: :py:class:`emzed.Table`
    """
    return _load(path, "load_table", TABLE_FILE_EXTENSIONS, Table.load)


def load_csv(path=None, *, delimiter=";", dash_is_none=True):
    """Load CSV file.

    :param path: Path to the file to load. If not specified and if emzed-gui is
                 installed a user dialog will pop up and ask for the file.
    :param delimiter: CSV field delimiter
    :param dash_is_none: If set to ``True`` the value ``-`` will be interpreted
                         as ``None`` (missing value).
    :returns: :py:class:`emzed.Table`
    """

    return _load(
        path,
        "load_csv",
        CSV_FILE_EXTENSIONS,
        partial(Table.load_csv, delimiter=delimiter, dash_is_none=dash_is_none),
    )


def load_excel(path=None):
    """Load Excel file.

    :param path: Path to the file to load. If not specified and if emzed-gui is
                 installed a user dialog will pop up and ask for the file.
    :returns: :py:class:`emzed.Table`
    """

    return _load(path, "load_excel", EXCEL_FILE_EXTENSIONS, Table.load_excel)


def _load(path, key, extensions, load_function):
    if path is None:
        if not has_emzed_gui():
            raise ValueError("you must specify a path or install emzed_gui")
        last_file = locations.get(key)
        if last_file is not None:
            start_at = os.path.dirname(last_file)
        else:
            start_at = None
        import emzed_gui

        path = emzed_gui.ask_for_single_file(start_at, extensions=extensions)
        if path is None:
            return
        locations.update(key, path)

    if not any(path.lower().endswith("." + ext) for ext in extensions):
        ext = ", ".join(extensions)
        warnings.warn(f"you should use one of the supported extensions {ext}")

    if path.startswith("http://") or path.startswith("https://"):
        try:
            path_local = download(path)
            return load_function(path_local)
        except OSError as e:
            raise OSError(f"download from {path} faile: {e}") from None
        except Exception as e:
            raise ValueError(
                f"download from {path} worked, but result is invalid: {e}"
            ) from None

    return load_function(path)


def load_peak_maps(pattern=None):
    """Load multiple peak maps.

    :param pattern: Globbing pattern (same as used for :py:func:`glob.glob`). If not
                    specified and if emzed-gui is installed a user dialog will pop up
                    and ask for the files.
                    Can also be a folder in case emzed-gui is installed.
    :returns: ``list`` of :py:class:`emzed.PeakMap` instances
    """
    return _load_multiple(
        pattern, "load_peak_maps", PEAKMAP_FILE_EXTENSIONS, PeakMap.load
    )


def load_tables(pattern=None):
    """Load multiple tables in ``emzed`` format.

    :param pattern: Globbing pattern (same format as used by :py:func:`glob.glob`). If
                    not specified and if emzed-gui is installed a user dialog will pop
                    up and ask for the files.
                    Can also be a folder in case emzed-gui is installed.
    :returns: ``list`` of :py:class:`emzed.Table` instances
    """
    return _load_multiple(pattern, "load_tables", TABLE_FILE_EXTENSIONS, Table.load)


def load_csvs(pattern=None, *, delimiter=";", dash_is_none=True):
    """Load multiple CSV files.

    :param pattern: Globbing pattern (same format as used by :py:func:`glob.glob`). If
                    not specified and if emzed-gui is installed a user dialog will pop
                    up and ask for the files.
                    Can also be a folder in case emzed-gui is installed.
    :param delimiter: CSV field seperator.
    :param dash_is_none: If set to ``True`` the value ``-`` will be interpreted
                         as ``None`` (missing value).
    :returns: ``list`` of :py:class:`emzed.Table` instances
    """

    return _load_multiple(
        pattern,
        "load_csvs",
        CSV_FILE_EXTENSIONS,
        partial(Table.load_csv, delimiter=delimiter, dash_is_none=dash_is_none),
    )


def load_excels(pattern=None):
    """Load multiple excel files.

    :param pattern: Globbing pattern (same format as used by :py:func:`glob.glob`). If
                    not specified and if emzed-gui is installed a user dialog will pop
                    up and ask for the files.
                    Can also be a folder in case emzed-gui is installed.
    :returns: ``list`` of :py:class:`emzed.Table` instances
    """
    return _load_multiple(
        pattern, "load_excels", EXCEL_FILE_EXTENSIONS, Table.load_excel
    )


def _load_multiple(pattern, key, extensions, load_function):
    paths = glob.glob(pattern) if pattern is not None else []
    if not paths:
        if not has_emzed_gui():
            raise ValueError("you must specify a file pattern or install emzed_gui")
        if not pattern:
            last_folder = locations.get(key)
        else:
            last_folder = pattern
        if last_folder is not None:
            start_at = os.path.dirname(last_folder)
        else:
            start_at = None
        import emzed_gui

        paths = emzed_gui.ask_for_multiple_files(start_at, extensions=extensions)

        if not paths:
            return

        folder = os.path.dirname(paths[0])
        locations.update(key, folder)
    else:
        paths = glob.glob(pattern)

    if not all(
        any(path.lower().endswith("." + ext) for ext in extensions) for path in paths
    ):
        ext = ", ".join(extensions)
        warnings.warn(f"you should use one of the supported extensions {ext}")

    result = []
    for path in tqdm.tqdm(paths, total=len(paths)):
        result.append(load_function(path))
    return result


def _save(path, key, extensions, save_function, overwrite):
    overwrite = path is None or overwrite
    if path is None and has_emzed_gui:
        last_file = locations.get(key)
        if last_file is not None:
            start_at = os.path.dirname(last_file)
        else:
            start_at = None
        import emzed_gui

        path = emzed_gui.ask_for_save(start_at, extensions=extensions)
        if path is None:
            return
        locations.update(key, path)
    if not any(path.lower().endswith("." + ext) for ext in extensions):
        ext = ", ".join(extensions)
        warnings.warn(f"you should use one of the supported extensions {ext}")
    save_function(path, overwrite=overwrite)


def save_peak_map(peakmap, path=None, *, overwrite=False):
    """Save peak map.

    :param peakmap: Instance of :py:class:`emzed.PeakMap`.
    :param path: Target file location. If not specified and if emzed-gui is installed
                 a user dialog will pop up asking for the destination.
    :param overwrite: Enforce overwriting if file already exists.
    """

    _save(path, "save_peak_map", PEAKMAP_FILE_EXTENSIONS, peakmap.save, overwrite)


def save_table(table, path=None, *, overwrite=False):
    """Save table in ``emzed`` format.

    :param table: Instance of :py:class:`emzed.Table`.
    :param path: Target file location. If not specified and if emzed-gui is installed
                 a user dialog will pop up asking for the destination.
    :param overwrite: Enforce overwriting if file already exists.
    """
    _save(path, "save_table", TABLE_FILE_EXTENSIONS, table.save, overwrite)


def save_csv(table, path=None, *, delimiter=";", as_printed=True, overwrite=False):
    """Save table in ``csv`` format.

    :param table: Instance of :py:class:`emzed.Table`.
    :param path: Target file location. If not specified and if emzed-gui is installed
                 a user dialog will pop up asking for the destination.
    :param delimiter: CSV format field separator.
    :param as_printed: Uses specified table formats if set to ``True`` else all cells
                       (also the invisible cells with format set to ``None``) will be
                       saved in standard string representation.
    :param overwrite: Enforce overwriting if file already exists.
    """
    _save(
        path,
        "save_csv",
        CSV_FILE_EXTENSIONS,
        partial(table.save_csv, delimiter=delimiter, as_printed=as_printed),
        overwrite,
    )


def save_excel(table, path=None, *, overwrite=False):
    """Save table in excel format.

    :param table: Instance of :py:class:`emzed.Table`.
    :param path: Target file location. If not specified and if emzed-gui is installed
                 a user dialog will pop up asking for the destination.

    :param overwrite: Enforce overwriting if file already exists.
    """
    _save(path, "save_excel", EXCEL_FILE_EXTENSIONS, table.save_excel, overwrite)
