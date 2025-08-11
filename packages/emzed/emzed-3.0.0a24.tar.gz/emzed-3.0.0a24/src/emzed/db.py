#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>

import os
import re
import tempfile

import requests

from emzed.config import folders
from emzed.utils import busy_indicator

URL = "https://emzed.ethz.ch/downloads/"


def pubchem_table_path():
    return os.path.join(folders.get_emzed_folder(), "pubchem.table")


def __dir__():
    return ["pubchem", "update_pubchem", "check_update"]


def _get_pubchem_file_name():
    r = requests.get(URL)
    try:
        r.raise_for_status()
    except Exception as e:
        raise IOError(f"could not connect to emzed server: {e}")
    matches = re.findall(r'href="(pubchem_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}\.gz)"', r.text)
    if not matches:
        raise FileNotFoundError("no pubchem archive found on emzed server.")
    latest = max(matches)
    return latest


def update_pubchem():
    """downloads latest version of remote pubchem table.

    the remote table is usually updated once per week.
    """

    with busy_indicator("update pubchem"):
        from emzed.chemistry.pubchem import assemble_table

        file_name = _get_pubchem_file_name()

        r = requests.get(URL + file_name)
        r.raise_for_status()

        target_folder = tempfile.mkdtemp()
        target_file = os.path.join(target_folder, file_name)

        with open(target_file, "wb") as fh:
            fh.write(r.content)

        if os.path.exists(pubchem_table_path()):
            os.remove(pubchem_table_path())
        table = assemble_table(target_file, pubchem_table_path())

    table.meta_data["created_from"] = os.path.basename(target_file)
    print("got", len(table), "entries from", os.path.basename(target_file))

    print("you can access emzed.db.pubchem now")


def check_update():
    """compares version of local pubchem and remote pubchem table.

    the remote table is usually updated once per week.
    """
    file_name = _get_pubchem_file_name()
    if not os.path.exists(pubchem_table_path()):
        print("local : no pubchem download yet")
        print("remote:", file_name)
        return
    import emzed

    t = emzed.Table.open(pubchem_table_path())
    created_from = t.meta_data["created_from"]

    print("local :", created_from)
    print("remote:", file_name)


# somehow __name__ lookup fails within __getattr__ below, this is a workaround:
_name = __name__

# kind of singleton:
_pubchem = None


def __getattr__(name):
    if name != "pubchem":
        raise AttributeError(f"module {_name} has not attribute {name}")

    global _pubchem
    if _pubchem is not None:
        return _pubchem

    import os

    if os.path.exists(pubchem_table_path()):
        import emzed

        _pubchem = emzed.Table.load(pubchem_table_path())
        return _pubchem

    raise IOError("please run emzed.db.update_pubchem() first")
