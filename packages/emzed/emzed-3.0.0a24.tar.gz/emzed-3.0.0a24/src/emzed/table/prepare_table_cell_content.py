#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>

import pickle
import sqlite3

import numpy as np

from ..ms_data import MSChromatogram, PeakMap
from .col_types import BASE_TYPES
from .full_table_model import FullTableModel
from .immutable_table_model import ImmutableTableModel
from .pickle import Pickle
from .table import Table


def prepare_table_cell_content(model, value, type_):
    if isinstance(value, np.number):
        value = value.item()

    if value is None or type_ in BASE_TYPES:
        return value

    if type_ is object or type_ is MSChromatogram:
        if isinstance(value, Pickle):
            return sqlite3.Binary(value.bytes)
        return sqlite3.Binary(pickle.dumps(value, protocol=4))

    if type_ is Table:
        if any(t is Table for t in value.col_types):
            raise ValueError("nesting tables in tables in tables not supported")

        # TO MAKE THIS WORK WE NEED TO RECURSE value._copy_into

        if not isinstance(value._model, (ImmutableTableModel, FullTableModel)):
            raise ValueError(
                "views in tables not supported, you have to consolidate"
                " the view you want to add first"
            )

    assert type_ in (Table, PeakMap), f"illegal type {type_}"

    value._copy_into(model._conn)
    return value.unique_id
