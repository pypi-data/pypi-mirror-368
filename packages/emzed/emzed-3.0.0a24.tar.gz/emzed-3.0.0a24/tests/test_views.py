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


import itertools
import sys
from functools import partial

import pytest

from emzed import MzType, PeakMap, RtType, Table, to_table
from emzed.table.table_utils import get_references

from .conftest import with_mem_and_disk

IS_WIN = sys.platform == "win32"
IS_LINUX = sys.platform.startswith("linux")


def test_table_access(dummy_table, regtest):
    assert len(dummy_table) == 2

    print(dummy_table.rows, file=regtest)

    assert dummy_table[0] == dummy_table.rows[0]
    assert dummy_table[1] == dummy_table.rows[1]

    assert dummy_table[-1] == dummy_table[len(dummy_table) - 1]

    with pytest.raises(IndexError):
        print(dummy_table.rows[2], file=regtest)

    with pytest.raises(IndexError):
        print(dummy_table[2], file=regtest)


@with_mem_and_disk
def test_filter(dummy_table, create_table, regtest):
    t = create_table(
        ["a", "b", "c", "mz", "rt"],
        [int, float, str, MzType, RtType],
        rows=[[1, 1.0, "1", 1000.00001, 60.0], [2, 2.0, "2", 600.1, 90.0]],
    )
    t.print_(stream=regtest)
    print(file=regtest)

    new_table = dummy_table.filter(t.a == 1, keep_view=True)
    new_table.print_(stream=regtest)

    assert new_table.unique_id is not None


def test_table_consolidate(create_table, regtest):
    t1 = create_table(
        ["a", "b", "c", "mz", "rt"],
        [int, int, str, MzType, RtType],
        rows=[[1, 1, "1", 1000.00001, 60.0], [2, 2, "2", 600.1, 90.0]],
    )

    t2 = t1[0:2]
    print(t2, file=regtest)

    t2 = t2.consolidate()
    print(t2, file=regtest)

    t2 = t2.filter(t2.a == 1)
    print(t2, file=regtest)


def test_extract_columns(regtest, pm):
    t = to_table("a", [1, 2, None], int)
    t.add_column_with_constant_value("b", 1, int)
    t.add_column("c", t.a - t.b, int)

    t2 = t.extract_columns("c", "b", keep_view=True)
    assert t2.col_names == ("c", "b")
    print(t2, file=regtest)

    t3 = t2.filter(t2.c == 1, keep_view=True)
    print(t3, file=regtest)

    with pytest.raises(ValueError):
        t2 = t.extract_columns("f", "g")

    t.add_column("pm", [pm, None, pm], PeakMap, format_="%s")
    print(t, file=regtest)

    # t3 is a view on t which we changed meanwhile:
    with pytest.raises(ValueError):
        print(t3)

    t2 = t.extract_columns("a", "c").consolidate()
    print(t2, file=regtest)

    assert len(get_references(t._model)) == 1
    assert len(get_references(t2._model)) == 0


def test_extract_and_join(regtest):
    t = to_table("a", [1, 2, None], int)
    t.add_column_with_constant_value("b", 1, int)
    t.add_column("c", t.a - t.b, int)

    t2 = t.extract_columns("c", "b")

    print(t.join(t2), file=regtest)

    t3 = t.join(t2, t.a == t2.b)
    print(t3, file=regtest)

    t4 = t2.join(t, t.a == t2.b)
    print(t4, file=regtest)


parent_modifications = [
    lambda t: partial(t.add_column, "c", t.a, int),
    lambda t: partial(t.replace_column, "b", t.a, int),
    lambda t: partial(t.add_row, [1, 2]),
]

parent_modification_ids = ["add_column", "replace_column", "add_row"]

views = [
    lambda t: t[::2],
    lambda t: t.filter(t.a < 2, keep_view=True),
    lambda t: t.extract_columns("a", keep_view=True),
]

view_ids = ["slice", "filter", "extract_columns"]

view_checks = [
    lambda t: t.consolidate(),
    lambda t: t.a,
    lambda t: t.extract_columns("a"),
    lambda t: to_table("a", [t], Table),
    lambda t: t.rename_columns(a="aa"),
    lambda t: t[0],
    lambda t: list(t),
]

view_check_ids = [
    "consolidate",
    "column_accces",
    "extract_columns",
    "table_in_table",
    "rename_columns",
    "access_row",
    "iter",
]
ids = [
    " + ".join(t)
    for t in itertools.product(parent_modification_ids, view_ids, view_check_ids)
]


@pytest.mark.parametrize(
    "parent_modification, view, view_check",
    itertools.product(parent_modifications, views, view_checks),
    ids=ids,
)
def test_view_invalidation(t0, regtest, parent_modification, view, view_check):
    tview = view(t0)
    assert tview._model._is_valid
    parent_modification(t0)()
    assert not tview._model._is_valid
    with pytest.raises(ValueError):
        view_check(tview)
