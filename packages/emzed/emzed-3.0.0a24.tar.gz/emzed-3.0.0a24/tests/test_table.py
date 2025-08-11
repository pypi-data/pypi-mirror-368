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
import pickle
import sys
from concurrent.futures import ProcessPoolExecutor
from functools import partial

import numpy as np
import pandas as pd
import pytest

from emzed import MzType, PeakMap, RtType, Table, to_table
from emzed.table.table_utils import get_references

from .conftest import with_disk_only, with_mem_and_disk

IS_WIN = sys.platform == "win32"


@with_mem_and_disk
def test_table_formats(regtest, create_table):
    t = create_table(
        ["a", "b", "c", "mz", "rt"],
        [int, float, str, MzType, RtType],
        rows=[[1, 1.0, "1", 1000.00001, 60.0], [2, 2.0, "2", 600.1, 90.0]],
    )
    print(t, file=regtest)
    assert t.unique_id is not None


@with_mem_and_disk
def test_table_hidden_column(regtest, create_table):
    t = create_table(
        ["a", "b", "c", "hidden"],
        [int, float, str, int],
        ["%d", "%f", "%s", None],
        rows=[[1, 1.0, "1", 1], [2, 2.0, "2", 2]],
    )
    t.print_(stream=regtest)


def test_table_invalid_args_col_name_missing(regtest, create_table):
    with pytest.raises(AssertionError) as e:
        create_table(
            ["a", "b", "c", "mz"],
            [int, float, str, MzType, RtType],
            rows=[[1, 1.0, "1", 1000.00001, 60.0], [2, 2.0, "2", 600.1, 90.0]],
        )

    print(e.value, file=regtest)


def test_table_invalid_args_row_0_value_missing(regtest, create_table):
    with pytest.raises(AssertionError) as e:
        create_table(
            ["a", "b", "c", "mz"],
            [int, float, str, MzType],
            rows=[[1, 1.0, "1", 1000.00001], [2, 2.0, "2", 600.1, 90.0]],
        )
    print(e.value, file=regtest)


def test_table_invalid_args_row_1_value_missing(regtest, create_table):
    with pytest.raises(AssertionError) as e:
        create_table(
            ["a", "b", "c", "mz"],
            [int, float, str, MzType, RtType],
            rows=[[1, 1.0, "1", 1000.00001, 60.0], [2, 2.0, "2", 600.1]],
        )
    print(e.value, file=regtest)


def test_table_invalid_args_col_format_missing(regtest, create_table):
    with pytest.raises(AssertionError) as e:
        create_table(
            ["a", "b", "c", "hidden"],
            [int, float, str, int],
            ["%d", "%f", "%s"],
            rows=[[1, 1.0, "1", 1], [2, 2.0, "2", 2]],
        )
    print(e.value, file=regtest)


def test_table_duplicate_col_name(regtest, create_table):
    with pytest.raises(AssertionError) as e:
        create_table(["a", "b", "a"], [int, float, int], ["%d", "%f", "%s"])
    print(e.value, file=regtest)


def test_table_multiple_duplicate_col_names(regtest, create_table):
    with pytest.raises(AssertionError) as e:
        create_table(
            ["a", "b", "a", "b"], [int, float, int, int], ["%d", "%f", "%s", "%s"]
        )
    print(e.value, file=regtest)


def test_table_io(dummy_table, tmpdir, regtest):
    path = tmpdir.join("table.table").strpath

    dummy_table.save(path)
    table_back = Table.open(path)

    table_back.print_(stream=regtest)

    assert dummy_table.meta_data == table_back.meta_data

    print(str(dummy_table.meta_data), file=regtest)

    assert dummy_table.unique_id == table_back.unique_id


def test_table_column_access(dummy_table, regtest, pm):
    with pytest.raises(AttributeError) as e:
        dummy_table.unknown_column_name

    print(e.value, file=regtest)

    a_col = dummy_table["a"]
    assert a_col.to_list() == [1, 2]

    dummy_table.add_column("d", [1.0, None], float)
    assert dummy_table.d.to_list() == [1.0, None]

    dummy_table.add_column("pm", [pm, pm], PeakMap)
    assert dummy_table.pm.to_list() == [pm, pm]

    dummy_table.add_column("pm2", [pm, None], PeakMap)
    assert dummy_table.pm2.to_list() == [pm, None]


@with_disk_only
def test_table_join(regtest, create_table):
    print_ = partial(print, file=regtest)

    t1 = create_table(
        ["a", "b", "c", "mz", "rt"],
        [int, int, str, MzType, RtType],
        rows=[[1, 1, "1", 1000.00001, 60.0], [2, 2, "2", 600.1, 90.0]],
    )
    t1.print_(stream=regtest)
    print_()

    t2 = create_table(
        ["a", "b", "c", "mz", "rt"],
        [int, int, str, MzType, RtType],
        rows=[[1, 2, "1", 1000.00001, 60.0], [2, 1, "2", 600.1, 90.0]],
    )
    print_()

    print_("join t1.a == t2.b")

    t = t1.join(t2, t1.a == t2.b)

    t.print_(stream=regtest)
    print_()

    print_("join t1.a == t2.b")
    t = t1.join(t2, t1.a == t2.b)
    t.print_(stream=regtest)
    print_()

    print_("join full t1.join(t2)")
    t = t1.join(t2)
    t.print_(stream=regtest)

    print_("join full t1.join(t2).join(t1)")
    t = t1.join(t2).join(t1)
    t.print_(stream=regtest)

    print_("join full t1.join(t2.join(t1))")
    t = t1.join(t2.join(t1))
    t.print_(stream=regtest)

    print_("join t1.a == t2.mz")
    t = t1.join(t2, t1.a == t2.mz)
    assert len(t) == 0
    t.print_(stream=regtest)
    print_()

    t1 = t1.filter(t1.a == t1.a)
    t2 = t2.filter(t2.a == t2.a)
    t = t1.join(t2, t1.a == t2.a)
    assert len(t) == 2
    print(t, file=regtest)
    print_()

    with pytest.raises(ValueError):
        t = t1.join(t2, t1[:1].a == t2.b)
    with pytest.raises(ValueError):
        t = t1.join(t2, t1[:1].a == t2[1:].b)

    with pytest.raises(ValueError):
        t = t1.filter(t1.b == 2).join(t2, t1.a == t2.a)

    with pytest.raises(ValueError):
        t = t1.filter(t1.b == 2).join(t2, t1.filter(t1.a == t1.a).a == t2.a)

    t2 = t1[0:2]
    print(t2, file=regtest)

    t2 = t2.consolidate()
    print(t2, file=regtest)

    t2 = t2.filter(t2.a == 1).consolidate()
    print(t2, file=regtest)


def test_read_csv(regtest, data_path, tmpdir):
    t = Table.load_csv(data_path("minimal.csv"))
    t.print_(stream=regtest)

    print(file=regtest)
    t = Table.load_csv(data_path("minimal.csv"), dash_is_none=False)
    t.print_(stream=regtest)

    with pytest.raises(OSError) as e:
        Table.load_csv(tmpdir.join("not-exist.csv").strpath)

    message = e.value.args[0]
    assert message.startswith("csv file")
    assert message.endswith("does not exist")

    with pytest.raises(ValueError) as e:
        t = Table.load_csv(data_path("minimal.csv"), col_names=["a", "b"])

    print(file=regtest)
    print(e.value, file=regtest)

    with pytest.raises(ValueError) as e:
        t = Table.load_csv(data_path("minimal.csv"), col_types=["a", "b"])

    print(file=regtest)
    print(e.value, file=regtest)

    with pytest.raises(ValueError) as e:
        t = Table.load_csv(data_path("minimal.csv"), col_formats=["a", "b"])

    print(file=regtest)
    print(e.value, file=regtest)


def test_set_col_type(t0, regtest):
    t0.print_(stream=regtest)
    print(file=regtest)

    t0.set_col_type("a", float)

    for row in t0:
        if row.a is not None:
            assert isinstance(row.a, float)

    t0.print_(stream=regtest)
    print(file=regtest)

    t0.set_col_type("a", MzType)
    for row in t0:
        if row.a is not None:
            assert isinstance(row.a, float)

    t0.print_(stream=regtest)
    print(file=regtest)

    # Mz to Rt does not work, so we first convert back to float:
    t0.set_col_type("a", float)
    for row in t0:
        if row.a is not None:
            assert isinstance(row.a, float)

    t0.print_(stream=regtest)
    print(file=regtest)

    t0.set_col_type("a", RtType)

    for row in t0:
        if row.a is not None:
            assert isinstance(row.a, float)


def test_set_col_format(t0, regtest):
    for fmt in ("%03d", None, "%f", "%s", "%r", lambda x: "*" if x is None else ":"):
        t0.set_col_format("a", fmt)
        print("set format of a to", repr(fmt), file=regtest)
        t0.print_(stream=regtest)
        print(file=regtest)

    for fmt in (None, "%s", "%r", lambda x: "*" if x is None else ":"):
        t0.set_col_format("b", fmt)
        print("set format of b to", repr(fmt), file=regtest)
        t0.print_(stream=regtest)
        print(file=regtest)


def test_add_column(t0, regtest):
    with pytest.raises(ValueError) as e:
        t0.add_column("c", [1.0, 2.0], float)

    print(e.value, file=regtest)
    print(file=regtest)

    t0.add_column("c", [1.0, 2.0, 3, None], float, "%.1f")

    t0.print_(stream=regtest)
    print(file=regtest)

    t0.add_column("d", t0.c, int)
    t0.print_(stream=regtest)

    t0.add_column("e", t0.c + 1, int)
    t0.print_(stream=regtest)

    t0.add_column("f", [None, None, None, None], int)
    t0.print_(stream=regtest)

    t0.add_column("g", [1, 2, 3, 4], int, insert_before="a")
    t0.add_column("h", [2, 3, 4, 5], int, insert_before="a")
    t0.add_column("i", [3, 4, 5, 6], int, insert_before="a")
    t0.print_(stream=regtest)

    t0.add_column("j", [1, 2, 3, 4], int, insert_after="g")
    t0.add_column("k", [2, 3, 4, 5], int, insert_after="f")
    t0.add_column("l", [3, 4, 5, 6], int, insert_after="k")
    t0.print_(stream=regtest)


def test_add_column_with_apply(t0, regtest):
    dd = {1: 11, 3: 15, 5: 7, None: 111}

    def m(a, b):
        return max(a, b)

    with pytest.raises(TypeError) as e:
        t0.add_column("lookup", t0.apply(m, t0.a, t0.b), int)

    print(e.value, file=regtest)
    print(file=regtest)

    t0.add_column("lookup", t0.apply(dd.get, t0.a, ignore_nones=False), int)

    t0.print_(stream=regtest)


def test_apply(t0, regtest):
    dd = {1: 11, 3: 15, 5: None, None: 111}

    def lookup(x, dd, key, z):
        return dd.get(key)

    t0.add_column(
        "lookup", t0.apply(lookup, 0, dd, t0.a, t0.b, ignore_nones=False), int
    )
    print(t0, file=regtest)


def test_apply_other_types(t0, pm, regtest):
    print(t0, file=regtest)

    dd = {1: 11, 3: 15, 5: 7, None: 111}

    def lookup(x, dd, key, z):
        if key == 5:
            return None
        return [x, dd, dd.get(key)]

    expr = t0.apply(lookup, 0, dd, t0.a, t0.b, ignore_nones=False)
    t0.add_column("lookup", expr, object)
    print(t0, file=regtest)

    with pytest.raises(TypeError):
        t0.add_column("lookup2", t0.apply(lambda: t0), Table)
        print(t0, file=regtest)

    with pytest.raises(TypeError):
        t0.add_column("lookup2", t0.apply(lambda: pm), PeakMap)
        print(t0, file=regtest)


def test_apply_numpy_types(t0, regtest):
    t0.add_column("i", np.arange(len(t0)), int)

    def lookup(arr, i):
        return arr[i]

    t0.add_column("j", t0.apply(lookup, np.arange(len(t0)), t0.i), int)
    print(t0, file=regtest)

    def update(d, key):
        return d[key]

    t = to_table("a", np.arange(1, 4), int)
    a2b = dict(zip(t.a, np.arange(2, 5)))
    t.add_column("b", t.apply(update, a2b, t.a), int)
    print(t, file=regtest)


def test_issue_30(t0, regtest):
    # https://sissource.ethz.ch/sispub/emzed/emzed/-/issues/30

    def one():
        return 1

    t0.filter(t0.apply(one) == 2).consolidate()


def test_add_constant_column(t0, regtest):
    t0.add_column_with_constant_value("c", 1.0, float, "%.1f")

    t0.print_(stream=regtest)
    print(file=regtest)

    t0.add_column_with_constant_value("d", None, int)
    t0.print_(stream=regtest)

    t0.add_column_with_constant_value("g", 1111, int, insert_before="a")
    t0.add_column_with_constant_value("h", "h", str, insert_before="a")
    t0.add_column_with_constant_value("i", "i", str, insert_before="a")
    t0.print_(stream=regtest)

    t0.add_column_with_constant_value("j", "j", str, insert_after="g")
    t0.add_column_with_constant_value("k", "k", str, insert_after="a")
    t0.add_column_with_constant_value("l", None, str, insert_after="d")
    t0.print_(stream=regtest)


def test_table_meta(t0, regtest):
    print(t0.meta_data, file=regtest)

    t0.meta_data["extra"] = dict(a=3, b=[1, 2, 3])
    t0.meta_data["extra_2"] = ("hi ho", True)

    print("lookup extra", t0.meta_data["extra"], file=regtest)
    print("lookup extra_2", t0.meta_data["extra_2"], file=regtest)
    print("keys", t0.meta_data.keys(), file=regtest)
    print("values", t0.meta_data.values(), file=regtest)
    print("items", t0.meta_data.items(), file=regtest)
    print("as string", t0.meta_data, file=regtest)
    print("as repr", repr(t0.meta_data), file=regtest)

    with pytest.raises(KeyError):
        t0.meta_data["abc"]

    print("use get", t0.meta_data.get("abc"), file=regtest)
    print("use get", t0.meta_data.get("abc", "DEFAULT"), file=regtest)

    assert t0.meta_data is not None
    assert t0.meta_data == t0.meta_data


def test_create_table_from_numpy(regtest):
    rows = np.array([[1, 0], [2.5, 3.0]])
    t = Table.create_table(["a", "b"], [int, float], rows=rows)

    t.print_(stream=regtest)


def test_create_table_from_pandas(regtest):
    rows = np.array([[1, 0], [2.5, 3.0]])
    df = pd.DataFrame(rows)
    t = Table.create_table(["a", "b"], [int, float], rows=df)

    t.print_(stream=regtest)


def test_to_table(regtest):
    t = to_table("abc", [1, 2, None], int)

    print(t, file=regtest)
    print(file=regtest)

    t = to_table("abc", [1, 2, None], int, "%02d")

    print(t, file=regtest)
    print(file=regtest)

    t = to_table("abc", [1, 2, None], int, meta_data=dict(hi="uwe"))
    assert t.meta_data.as_dict() == {"hi": "uwe"}

    print(t, file=regtest)
    print(file=regtest)


def test_rename_columns(regtest):
    t = to_table("a", [1, 2, None], int)
    t.add_column_with_constant_value("b", 1, int)
    t.add_column("c", t.a - t.b, int)

    t.rename_columns(b="B", c="cc")
    assert t.col_names == ("a", "B", "cc")
    print(t, file=regtest)

    t2 = t.filter(t.a < 3)
    t2.rename_columns(B="b", cc="c")
    assert t2.col_names == ("a", "b", "c")
    print(t2, file=regtest)

    assert t.col_names == ("a", "B", "cc")

    with pytest.raises(ValueError) as e:
        t.rename_columns(a="B", B="cc")

    print(e.value, file=regtest)


def test_group_by(regtest):
    t = Table.create_table(
        ["a", "b", "c"],
        [int, int, int],
        rows=[
            [1, 2, 3],
            [1, 3, 4],
            [None, 2, 2],
            [2, None, 3],
            [None, None, 4],
            [None, None, None],
        ],
    )

    print(t, file=regtest)

    t.add_column(
        "c_sum_by_a", t.group_by(t.a, group_nones=True).aggregate(sum, t.c), int
    )

    t.add_column(
        "c_sum_by_a_b",
        t.group_by(t.a, t.b, group_nones=True).aggregate(sum, t.c + 1),
        int,
    )

    def count_nones(values):
        return sum(1 for v in values if v is None)

    t.add_column(
        "nones",
        t.group_by(t.b, group_nones=True).aggregate(
            count_nones, t.b, ignore_nones=False
        ),
        int,
    )

    print(t, file=regtest)

    with pytest.raises(TypeError) as e:
        print(t._model)
        t.add_column(
            "c_sum_by_a_b_2",
            t.group_by(t.a, t.b).aggregate(sum, t.c + 1, ignore_nones=False),
            int,
        )

    print(e.value, file=regtest)


def test_group_by_predef_aggregates(regtest):
    t = Table.create_table(
        ["a", "b", "c"],
        [int, int, int],
        rows=[
            [1, 2, 3],
            [1, 3, 4],
            [None, 2, 2],
            [2, None, 3],
            [None, None, 4],
            [None, None, None],
        ],
    )
    t.add_column("sum_b_plus_c_by_a", t.group_by(t.a).sum(t.b + t.c), int)
    t.add_column("max_b_plus_c_by_a", t.group_by(t.a).max(t.b + t.c), int)
    t.add_column("min_b_plus_c_by_a", t.group_by(t.a).min(t.b + t.c), int)
    t.add_column("mean_b_plus_c_by_a", t.group_by(t.a).mean(t.b + t.c), int)
    t.add_column("count_b_plus_c_by_a", t.group_by(t.a).count(), int)
    print(t, file=regtest)


def test_group_by_multiple_args(regtest):
    t = Table.create_table(
        ["a", "b", "c"],
        [int, int, int],
        rows=[
            [8, 2, 3],
            [1, 11, 4],
            [1, None, 4],
            [None, 2, 2],
            [1, 2, 2],
            [2, 7, 3],
            [9, 3, 4],
            [None, None, None],
        ],
    )

    def agg(a_values, b_values):
        return max(a_values) + max(b_values)

    t.add_column("agg", t.group_by(t.c).aggregate(agg, t.a, t.b), int)
    print(t.sort_by("c"), file=regtest)


def test_group_by_statistical_aggregates(regtest):
    t = Table.create_table(
        ["a", "b", "c"],
        [int, int, int],
        rows=[
            [1, 2, 3],
            [1, 3, 4],
            [None, 2, 2],
            [2, None, 3],
            [None, None, 4],
            [None, None, None],
        ],
    )
    t.add_column("std_b_plus_c_by_a", t.group_by(t.a).std(t.b + t.c), float)
    t.add_column("median_b_plus_c_by_a", t.group_by(t.a).median(t.b + t.c), int)
    print(t, file=regtest)


def test_group_by_create_group_ids(regtest):
    t = Table.create_table(
        ["a", "b", "c"],
        [int, int, int],
        rows=[
            [1, 2, 3],
            [1, 3, 4],
            [None, 2, 2],
            [2, None, 3],
            [None, None, 4],
            [None, None, None],
        ],
    )

    t.add_column("id_by_a", t.group_by(t.a).id(), int)
    t.add_column("id_by_a_2", t.group_by(t.a, group_nones=True).id(), int)
    print(t, file=regtest)


@pytest.fixture
def t():
    t = Table.create_table(
        ["a", "b"],
        [int, bool],
        rows=[
            [1, True],
            [1, True],
            [None, False],
            [2, False],
            [None, None],
            [3, None],
            [3, False],
            [4, None],
            [4, True],
            [5, None],
            [5, None],
        ],
    )
    yield t


def test_group_by_all_false(t, regtest):
    t.add_column("b_all_false_by_a", t.group_by(t.a).all_false(t.b), bool)
    t.add_column(
        "b_all_false_by_a_2", t.group_by(t.a, group_nones=True).all_false(t.b), bool
    )
    t.add_column(
        "b_all_false_by_a_3",
        t.group_by(t.a, group_nones=True).all_false(t.b, ignore_nones=True),
        bool,
    )
    print(t, file=regtest)


def test_group_by_any_false(t, regtest):
    t.add_column("b_any_false_by_a", t.group_by(t.a).any_false(t.b), bool)
    t.add_column(
        "b_any_false_by_a_2", t.group_by(t.a, group_nones=True).any_false(t.b), bool
    )
    t.add_column(
        "b_any_false_by_a_3",
        t.group_by(t.a, group_nones=True).any_false(t.b, ignore_nones=True),
        bool,
    )
    print(t, file=regtest)


def test_group_by_all_true(t, regtest):
    t.add_column("b_all_true_by_a", t.group_by(t.a).all_true(t.b), bool)
    t.add_column(
        "b_all_true_by_a_2", t.group_by(t.a, group_nones=True).all_true(t.b), bool
    )
    t.add_column(
        "b_all_true_by_a_3",
        t.group_by(t.a, group_nones=True).all_true(t.b, ignore_nones=True),
        bool,
    )
    print(t, file=regtest)


def test_group_by_any_true(t, regtest):
    t.add_column("b_any_true_by_a", t.group_by(t.a).any_true(t.b), bool)
    t.add_column(
        "b_any_true_by_a_2", t.group_by(t.a, group_nones=True).any_true(t.b), bool
    )
    t.add_column(
        "b_any_true_by_a_3",
        t.group_by(t.a, group_nones=True).any_true(t.b, ignore_nones=True),
        bool,
    )
    print(t, file=regtest)


def test_group_by_all_none(t, regtest):
    t.add_column("b_all_none_by_a", t.group_by(t.a).all_none(t.b), bool)
    t.add_column(
        "b_all_none_by_a_2", t.group_by(t.a, group_nones=True).all_none(t.b), bool
    )
    print(t, file=regtest)


def test_group_by_any_none(t, regtest):
    t.add_column("b_any_none_by_a", t.group_by(t.a).any_none(t.b), bool)
    t.add_column(
        "b_any_none_by_a_2", t.group_by(t.a, group_nones=True).any_none(t.b), bool
    )

    print(t, file=regtest)


def test_replace_column(regtest):
    t = Table.create_table(
        ["a", "b", "c"],
        [int, int, int],
        rows=[
            [1, 2, 3],
            [1, 3, 4],
            [None, 2, 2],
            [2, None, 3],
            [None, None, 4],
            [None, None, None],
        ],
    )

    print(t, file=regtest)

    t.replace_column("a", [1, 2, 1, 2, 1, 2], int)
    print(t, file=regtest)

    t.replace_column("a", t.a + 2, int)
    print(t, file=regtest)

    t.replace_column("a", t.group_by(t.a).aggregate(sum, t.c), int)
    print(t, file=regtest)

    schemata = t._model._conn.schemata
    data_schema = schemata.filter(schemata.name == "data")[0].sql
    print(data_schema, file=regtest)

    t.replace_column_with_constant_value("a", "4711", str)
    t.replace_column_with_constant_value("b", None, bool)

    print(t, file=regtest)

    schemata = t._model._conn.schemata
    data_schema = schemata.filter(schemata.name == "data")[0].sql
    print(data_schema, file=regtest)


def test_peakmap_column(regtest, data_path):
    pm = PeakMap.load(data_path("ms1_and_ms2_mixed.mzML"))
    pm.meta_data["id"] = "pm"

    t = to_table("pm", [pm, pm, None], PeakMap)

    pm_back = t.pm.unique_values()[0]

    assert set(s.ms_level for s in pm_back) == {1, 2}

    t.set_col_format("pm", "%r")
    print(t, file=regtest)

    t.set_col_format("pm", "%s")
    print(t, file=regtest)

    tpm = t.pm
    t.add_column("pm2", tpm, PeakMap, format_="%s")
    print(t, file=regtest)

    t.add_column_with_constant_value("pm3", pm, PeakMap, format_="%s")
    print(t, file=regtest)

    t.add_column("pm4", [None, pm, None], PeakMap, format_="%s")
    print(t, file=regtest)

    assert t[0].pm == pm
    assert t[0].pm is t[1].pm

    t = t[:2].consolidate()
    assert t[0].pm == pm
    assert t[0].pm is t[1].pm

    assert t.unique_id is not None

    t.replace_column_with_constant_value("pm", pm, PeakMap, "%s")
    print(t, file=regtest)
    t.replace_column("pm2", [None, pm], PeakMap, "%s")
    print(t, file=regtest)

    t2 = t.extract_columns("pm4", "pm3", "pm2", "pm")
    print(t2, file=regtest)

    t3 = t.extract_columns("pm?")
    print(t3, file=regtest)

    t4 = t.extract_columns("pm*")
    print(t4, file=regtest)


def test_drop_columns(t0, regtest, tmpdir):
    path = tmpdir.join("table.table").strpath

    t0 = t0.consolidate(path=path)
    t0.add_column("aa", t0.a, int)
    print(t0, file=regtest)
    t0.drop_columns("a*")
    print(t0, file=regtest)

    # we also check that table stays on disk:
    assert t0._model._conn.uri.partition(":")[2] == path
    assert t0._model._conn.uri.partition(":")[2] == t0.path
    assert t0.is_open()
    assert not t0.is_in_memory()


def test_extract_column():
    t = Table.create_table(["a", "b", "c"], [int, float, str], rows=[[1, 1.0, "111"]])

    ta = t.extract_columns("a")
    assert ta.col_names == (t.col_names[0],)
    assert ta.col_types == (t.col_types[0],)
    assert ta.col_formats == (t.col_formats[0],)
    assert list(ta.a) == [1]

    tb = t.extract_columns("b")
    assert tb.col_names == (t.col_names[1],)
    assert tb.col_types == (t.col_types[1],)
    assert tb.col_formats == (t.col_formats[1],)
    assert list(tb.b) == [1.0]

    tc = t.extract_columns("c")
    assert tc.col_names == (t.col_names[2],)
    assert tc.col_types == (t.col_types[2],)
    assert tc.col_formats == (t.col_formats[2],)
    assert list(tc.c) == ["111"]

    trev = t.extract_columns("c", "b", "a")
    assert trev.col_names == t.col_names[::-1]
    assert trev.col_types == t.col_types[::-1]
    assert trev.col_formats == t.col_formats[::-1]
    assert list(trev.rows[0]) == ["111", 1.0, 1]


def test_peakmap_column_accessor(regtest, pm):
    t = to_table("pm", [pm, pm, None], PeakMap)  # noqa F841

    for expression in (
        "t.pm + 1",
        "t.pm - 1",
        "t.pm / 1",
        "t.pm * 1",
        "t.pm & 1",
        "t.pm | 1",
        "1 + t.pm",
        "1 - t.pm",
        "1 * t.pm",
        "1 / t.pm",
        "1 & t.pm",
        "1 | t.pm",
        "t.pm > 1",
        "t.pm >= 1",
        "t.pm < 1",
        "t.pm <= 1",
        "t.pm == 1",
        "t.pm != 1",
        "1 > t.pm",
        "1 >= t.pm",
        "1 <  t.pm",
        "1 <= t.pm",
        "1 == t.pm",
        "1 != t.pm",
    ):
        with pytest.raises(TypeError) as e:
            eval(expression)
        print(f"{expression:10s}", e.value.args[0], file=regtest)


def test_table_in_table(regtest):
    t0 = to_table("a", [1, 2, None], int, meta_data=dict(id="t0"))
    t1 = to_table("b", [t0, None], Table)

    print(t1, file=regtest)
    print(t1[0].b, file=regtest)

    assert t1[0].b.unique_id == t0.unique_id

    tsub = t1[0].b
    tsubc = t1[0].b.consolidate()

    with pytest.raises(TypeError):
        tsub.add_column_with_constant_value("c", None, int)

    tsubc.add_column_with_constant_value("c", None, int)

    with pytest.raises(TypeError):
        tsub.add_column("c", t0.a, int)

    tsubc.add_column("d", t0.a, int)

    with pytest.raises(ValueError):
        tsub.replace_column_with_constant_value("c", None, int)

    tsubc.replace_column_with_constant_value("c", None, int)

    with pytest.raises(ValueError):
        tsub.replace_column("e", t0.a, int)

    tsubc.replace_column("c", t0.a, int)

    with pytest.raises(ValueError):
        tsub.add_row([3, 4, 5])

    tsubc.add_row([3, 4, 5])
    print(tsubc, file=regtest)


def test_add_row(t0, regtest):
    t0.add_row([3, "3"])
    t0.add_row([None, None])
    print(t0, file=regtest)
    t0.add_row(t0[0])
    print(t0, file=regtest)

    t0.add_row({"a": 3})
    t0.add_row({"b": 4})
    t0.add_row({"a": 5, "b": 7})
    t0.add_row({})
    print(t0, file=regtest)


def test_table_in_table_in_table_not_allowed(regtest):
    t0 = to_table("a", [1, 2, None], int, meta_data=dict(id="t0"))
    t1 = to_table("b", [t0, None], Table)

    with pytest.raises(ValueError):
        to_table("c", [t1], Table)


def test_view_int_table_not_allowed(regtest):
    t0 = to_table("a", [1, 2, None], int, meta_data=dict(id="t0"))

    with pytest.raises(ValueError):
        to_table("b", [t0[:2], None], Table)

    t_cons = t0[:2].consolidate()
    print(t_cons.meta_data.as_dict(), file=regtest)
    t1 = to_table("b", [t_cons, None], Table)
    print(t1, file=regtest)

    with pytest.raises(ValueError):
        view = t0.filter(t0.a <= 2, keep_view=True)
        t1 = to_table("b", [view, None], Table)

    t_cons = t0.filter(t0.a <= 2).consolidate()
    print(t_cons.meta_data.as_dict(), file=regtest)
    t1 = to_table("b", [t_cons, None], Table)
    print(t1, file=regtest)


def test_slicing(t0, regtest):
    t0.extend(t0.copy())
    t0.add_enumeration()

    print(t0, file=regtest)
    print(file=regtest)

    t1 = t0[:-1]
    print(t1, file=regtest)
    print(file=regtest)

    t2 = t1[1:-1]
    print(t2, file=regtest)
    print(file=regtest)

    t3 = t2[::2]
    print(t3, file=regtest)

    print(t3.join(t3), file=regtest)


def test_peakmap_in_table_in_table(regtest, pm):
    t0 = to_table("pm", [pm, pm, None], PeakMap, format_="%s")
    t0.meta_data["id"] = "t0"

    t1 = to_table("b", [t0, None], Table)
    t1.meta_data["id"] = "t1"

    ref0 = get_references(t0._model)
    assert len(ref0) == 1

    ref1 = get_references(t1._model)
    assert len(ref1) == 2

    print(t0, file=regtest)
    print(t1, file=regtest)
    print(t1[0].b[0].pm, file=regtest)


def test_join_with_table_with_peakmap(pm, regtest):
    t0 = to_table("idx", [1, 2, 3], int)
    t0.add_column("pm", [None, pm, pm], PeakMap, format_="%s")

    t1 = to_table("idx", [1, 2, 3], int)
    t1.add_column("pm", [None, pm, pm], PeakMap, format_="%s")

    tn = t0.join(t1, t0.idx == t1.idx)
    print(tn, file=regtest)

    assert len(tn[1].pm) == 928
    assert len(tn[1].pm__0) == 928

    assert tn[1].pm.unique_id == tn[1].pm__0.unique_id
    assert tn[1].pm.unique_id == pm.unique_id


def test_join_with_table_with_table_with_peakmap(pm, regtest):
    t0 = to_table("idx", [1, 2, 3], int)
    t0.add_column("pm", [None, pm, pm], PeakMap, format_="%s")
    t0.meta_data["id"] = "t0"

    t2 = to_table("pm", [None, pm, None], PeakMap, format_="%s")
    t2.meta_data["id"] = "t2"

    t1 = to_table("idx", [1, 2, 3], int)
    t1.meta_data["id"] = "t1"
    t1.add_column("t", [t2, t2, None], Table)

    tn = t0.join(t1, t0.idx == t1.idx)
    print(tn, file=regtest)

    assert len(tn[1].pm) == 928
    assert len(tn[1].t__0[1].pm) == 928

    assert tn[1].pm.unique_id == tn[1].t__0[1].pm.unique_id
    assert tn[1].pm.unique_id == pm.unique_id


def test_add_enumeration(regtest):
    t = to_table("a", ["1", "2", "3"], str)
    t.add_enumeration()
    t.add_enumeration("idx_plus_10", insert_before="a", start_with=10)
    print(t, file=regtest)


def no_op(t):
    return t


def test_pickling(regtest, t0, pm, tmpdir):
    t0.add_column("pm", [None, pm, pm, None], PeakMap, format_="%s")

    t2 = to_table("pm", [None, pm, None], PeakMap, format_="%s")
    t2.meta_data["id"] = "t2"

    t0.add_column_with_constant_value("tsub", t2, Table)
    t0 = t0.consolidate(path=tmpdir.join("test.table").strpath)

    # direct pickling disabled, as dangerous / error prone, tables can be saved
    # instead:
    with pytest.raises(NotImplementedError):
        pickle.dumps(t0)

    with ProcessPoolExecutor(2) as p:
        print(t0._model._conn)
        [t_back] = p.map(no_op, [t0])

    assert t_back == t0


def get_access_name(t):
    print(t)
    return t._model._access_name


def test_pickling_view(t0, pm, regtest, tmpdir):
    t0.add_column("pm", [None, pm, pm, None], PeakMap, format_="%s")

    # we must keep connection alive for persisiting!
    tsub = t0[::2]

    tsub = tsub.consolidate(path=tmpdir.join("test.table").strpath)
    with ProcessPoolExecutor(2) as p:
        result = next(p.map(get_access_name, [tsub]))

    assert result == "data"


def test_sorting_permutation():
    t0 = to_table("a", [1, 2, 2, 3, 3], int)
    t0.add_column("b", ["5", "2", "3", "1", "4"], str)
    assert t0._sorting_permutation([("a", False), ("b", True)]) == [3, 4, 1, 2, 0]

    del t0[1]
    assert t0._sorting_permutation([("a", False), ("b", True)]) == [2, 3, 1, 0]


def test_sorting_permutation_with_nones(regtest):
    t0 = to_table("a", [None, 2, 2, 3, None], int)
    t0.add_column("b", [None, None, "1", "4", None], str)
    print(t0, file=regtest)
    perm = t0._sorting_permutation([("a", False), ("b", True)])
    print(t0[perm], file=regtest)
    print(t0[perm].consolidate(), file=regtest)


def test_set_value(regtest):
    t0 = to_table("a", [1, 2, 2, 3, 3], int)
    t0.add_column("b", ["5", "2", "3", "1", "4"], str)
    print(t0, file=regtest)

    t0._set_values([0, 1], 1, [666, 777])
    t0._set_value([2], "a", None)
    print(t0, file=regtest)


def test_set_value_with_object(regtest):
    t0 = to_table("a", [1, 2, 2, 3, 3], object)
    print(t0, file=regtest)

    t0._set_value([2], "a", {1: 2})
    print(t0, file=regtest)


def test_delete_row(t0, regtest):
    print(t0, file=regtest)
    print(file=regtest)

    del t0[0]
    print(t0, file=regtest)
    print(file=regtest)

    del t0[-1]
    print(t0, file=regtest)
    print(file=regtest)

    t = t0.join(t0)
    print(t, file=regtest)
    print(file=regtest)

    del t0[1]
    print(t0, file=regtest)
    print(file=regtest)


def test_save_csv(t0, regtest, tmpdir, pm):
    path = tmpdir.join("out.csv").strpath
    t0.add_column("c", [None, None, 1, ","], str)
    t0.add_column("pm", [pm, pm, None, None], PeakMap)
    t0.add_column("objects", [[], (), {}, None], object)
    t0.add_column("rt", [None, 120, 180, 210], RtType)

    t0.save_csv(path, delimiter=",", as_printed=True)
    regtest.write(open(path).read())
    print(file=regtest)

    with pytest.raises(OSError):
        # write again
        t0.save_csv(path, delimiter=",", as_printed=True)

    t0.save_csv(path, delimiter=",", as_printed=False, overwrite=True)
    regtest.write(open(path).read())

    print(file=regtest)
    t1 = Table.load_csv(path, delimiter=",")
    print(t1, file=regtest)


def test_to_pandas(t0, regtest):
    print(t0, file=regtest)
    print(t0.to_pandas(), file=regtest)


def test_pandas_roundtrip(t0, regtest):
    t1 = Table.from_pandas(t0.to_pandas())
    assert t1.unique_id == t0.unique_id


def test_pandas_with_object_columns(t0, regtest):
    t0.add_column_with_constant_value("pm", None, type_=PeakMap)
    t0.add_column_with_constant_value("tt", None, type_=Table)
    t0.add_column_with_constant_value("oo", None, type_=object)
    print(t0, file=regtest)
    print(file=regtest)

    df = t0.to_pandas()
    print(df.dtypes, file=regtest)
    print(file=regtest)
    print(df, file=regtest)
    print(file=regtest)

    t1 = Table.from_pandas(df)
    print(t1, file=regtest)


def test_table_load_excel(data_path, regtest):
    t1 = Table.load_excel(
        data_path("table.xlsx"), col_names=("a", "b"), col_types=(int, str)
    )

    print(t1, file=regtest)


def test_save_excel(t0, regtest, tmpdir):
    path = tmpdir.join("out.xlsx").strpath
    t0.save_excel(path)

    assert os.stat(path).st_size > 0

    with pytest.raises(OSError):
        t0.save_excel(path)

    t0.save_excel(path, overwrite=True)


def test_indices_for_rows_matching(t0, regtest):
    print(t0, file=regtest)

    ix = sorted(t0._indices_for_rows_matching("col_0 > 1"))
    print(t0[ix], file=regtest)

    t0 = t0[ix].consolidate()

    del t0[0]
    ix = sorted(t0._indices_for_rows_matching("col_0 > 1"))
    print(t0[ix], file=regtest)


def test_find_matching_rows(t0, regtest):
    print(t0, file=regtest)

    ix = t0._find_matching_rows("a", 3)
    print(t0[ix], file=regtest)

    del t0[0]
    ix = t0._find_matching_rows("a", 3)
    print(t0[ix], file=regtest)


def test_find_matching_rows_complext_data_types(t0, pm, regtest):
    t0.add_column_with_constant_value("pm", pm, PeakMap)
    assert t0._find_matching_rows("pm", pm) == [0, 1, 2, 3]
    assert t0._find_matching_rows("a", pm) == []


def test_object_columns(t0, regtest):
    t0.add_column("objects", [None, [1, 2], (1, 2), {1: 2}], object)
    for row in t0:
        print(row)
    print(t0)


def test_invalid_column_type(t0):
    with pytest.raises(TypeError):
        t0.add_column_with_constant_value("xxx", None, list)


def count_db_tables(t):
    schema = t._model._conn.schemata
    tables = schema.filter(schema.type == "table")
    return len(tables)


def test_extend(regtest, t0, pm):
    t0.meta_data["id"] = "t0"

    t1 = to_table("pm", [pm, None, None], PeakMap, format_="%s")
    t1.add_column("i", [1, 2, 3], int)
    t1.add_column("t", [None, t0, t0], Table)

    print(t1, file=regtest)
    assert count_db_tables(t1) == 12

    t2 = t1.copy()

    t2.extend(t1)
    print(t1, file=regtest)
    assert count_db_tables(t2) == 12

    t2.extend(t1)
    print(t2, file=regtest)
    assert count_db_tables(t2) == 12

    tback = t2.t.unique_values()[0]
    assert tback == t0

    pmback = t2.pm.unique_value()
    assert pmback == pm


def test_supported_postfixes():
    t1 = to_table("a", [], int)

    assert t1.supported_postfixes(["a"]) == [""]
    assert t1.supported_postfixes(["a", "b"]) == []

    t1.add_column("b", [], int)
    assert t1.supported_postfixes(["a", "b"]) == [""]

    t1.add_column("a__0", [], int)
    t1.add_column("b__0", [], int)
    assert t1.supported_postfixes(["a"]) == ["", "__0"]
    assert t1.supported_postfixes(["a", "b"]) == ["", "__0"]


def test_group_by_with_pickling(regtest):
    t1 = to_table("a", [1, 1, 1, 2, 2, 3], int)
    t1.add_column("b", [1, 2, 3, 4, 5, 6], int)

    def r(x):
        return x

    t1.add_column("c", t1.group_by(t1.a).aggregate(r, t1.b), object)
    print(t1, file=regtest)
