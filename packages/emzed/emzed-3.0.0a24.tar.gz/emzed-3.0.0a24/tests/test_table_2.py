#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>

import re

import pytest

import emzed
from emzed.utils.sqlite import list_tables


def test_apply_bug(t0):
    def add(a, b):
        return a + b

    t0.add_column("a_plus_2", t0.apply(add, t0.a, 2), int)
    assert list(t0.a_plus_2) == [3, 5, 7, None]


def test_split_by_iter():
    N = 5
    data = list(range(300)) * N

    t = emzed.to_table("a", data, int)
    t.add_column("b", t.apply(str, t.a), str)

    for ti in t.split_by_iter("a", keep_view=True):
        assert len(ti) == N

    for ti in t.split_by_iter("b", keep_view=True):
        assert len(ti) == N

    for ti in t.split_by_iter("a", "b", keep_view=True):
        assert len(ti) == N

    for ti in t.split_by_iter("a", keep_view=False):
        assert len(ti) == N

    for ti in t.split_by_iter("b", keep_view=False):
        assert len(ti) == N

    for ti in t.split_by_iter("a", "b", keep_view=False):
        assert len(ti) == N


def test_split_by(regtest):
    N = 5
    data = list(range(3)) * N

    t = emzed.to_table("a", data, int)
    t.add_column("b", t.apply(str, 3 * t.a + 1), str)

    for ti in t.split_by("a", "b"):
        print(ti, file=regtest)
        ti.add_column("c", t.b, str)

    for ti in t.split_by("a", "b", keep_view=True):
        print(ti, file=regtest)
        with pytest.raises(TypeError):
            ti.add_column("c", t.b, str)


def test_split_by_object_col(regtest):
    data = list(range(10, 15)) * 3

    t = emzed.to_table("a", data, str)
    t.add_column("b", t.apply(tuple, t.a), object)

    for ti in t.split_by("b"):
        print(ti, file=regtest)


def test_split_by_with_none(regtest):
    # see https://sissource.ethz.ch/sispub/emzed/emzed/-/issues/41

    t = emzed.to_table("a", [None, None, 1, 1], int)
    t.add_column("b", t.a * 1000, int)
    t0, t1 = t.split_by("a")
    print(t0, file=regtest)
    print(t1, file=regtest)


def test_col_order_after_io(regtest, tmpdir):
    t = emzed.Table.create_table(
        ["a", "b", "c"], [int, float, str], rows=[[1, 1.1, "11"], [2, 2.2, "22"]]
    )
    print(t, file=regtest)

    t2 = t.extract_columns("c", "b", "a")

    print(t2, file=regtest)
    print(t2.consolidate(), file=regtest)

    path = tmpdir.join("test.table").strpath
    emzed.io.save_table(t2, path)
    t3 = emzed.io.load_table(path)
    print(t3, file=regtest)


def test_collapse_simple(regtest):
    t = emzed.Table.create_table(
        ["a", "b", "c"], [int, float, str], rows=2 * [[1, 1.1, "11"], [2, 2.2, "22"]]
    )
    print(t, file=regtest)

    tn = t.collapse("a")
    print(tn, file=regtest)

    print(tn[0].collapsed, file=regtest)
    print(tn[1].collapsed, file=regtest)


def test_collapse_with_peakmap(regtest, pm):
    t = emzed.Table.create_table(
        ["a", "b", "c", "pm"],
        [int, float, str, emzed.PeakMap],
        rows=2 * [[1, 1.1, "11", pm], [2, 2.2, "22", None]],
    )
    t.set_col_format("pm", "%r")

    print(t, file=regtest)

    tn = t.collapse("a", "b")
    print(tn, file=regtest)

    print(tn[0].collapsed, file=regtest)
    print(tn[1].collapsed, file=regtest)

    assert len(tn[0].collapsed[0].pm) == 928


def test_rename_postfixes(regtest, t0):
    t = t0.join(t0).join(t0)
    print(t, file=regtest)
    t.rename_postfixes(__0="_first", __1="_second")
    print(t, file=regtest)

    t = emzed.Table.create_table(["a", "a__0"], [int, int], rows=[])

    with pytest.raises(ValueError) as e:
        t.rename_postfixes(__0="")
    print(e.value, file=regtest)


def test_stack_tables(regtest, t0, tmpdir):
    with pytest.raises(ValueError):
        emzed.Table.stack_tables(None)

    with pytest.raises(ValueError):
        emzed.Table.stack_tables([])

    t3 = emzed.Table.stack_tables([t0, t0, t0], path=tmpdir.join("t3.table").strpath)
    print(t3, file=regtest)

    t4 = emzed.Table.stack_tables(
        [t0.copy(), t0.copy(), t0.copy()],
        path=tmpdir.join("t4.table").strpath,
        overwrite=True,
    )
    print(t4, file=regtest)


def test_conditional_expressions(regtest, t0):
    t0.add_column("c", t0.a.if_not_none_else(777), int)
    t0.add_column("d", (t0.a > 2).then_else(777, 888), int)
    t0.add_column("e", t0.a > 2, bool)
    t0.add_column("f", (t0.a > 2).then_else(t0.b, None), int)
    print(t0, file=regtest)


def test_is_none(regtest, t0):
    print(t0.filter(t0.a.is_none()), file=regtest)
    print(t0.filter(t0.a.is_none() | t0.b.is_none()), file=regtest)


def test_is_not_none(regtest, t0):
    print(t0.filter(t0.a.is_not_none()), file=regtest)
    print(t0.filter(t0.a.is_not_none() & t0.b.is_not_none()), file=regtest)


def test_lookup_from_other_table(regtest):
    lookup = emzed.to_table("key", [None, 1, 2, 3, 4], int)
    lookup.add_column("value", lookup.key + 1, int)
    print(lookup, file=regtest)

    data = emzed.to_table("key", [None, 1, 2, 3, 5], int)
    data.add_column(
        "value", data.key.lookup(lookup.key, lookup.value * lookup.value), int
    )
    print(data, file=regtest)


def test_lookup_from_view(regtest):
    lookup = emzed.to_table("key", [None, 1, 2, 3, 4], int)
    lookup.add_column("value", lookup.key + 1, int)

    lookup = lookup.filter(lookup.key.is_not_none())
    print(lookup, file=regtest)

    data = emzed.to_table("key", [None, 1, 2, 3, 5], int)
    data.add_column(
        "value", data.key.lookup(lookup.key, lookup.value * lookup.value), int
    )
    print(data, file=regtest)


def test_lookup_duplicate_keys(regtest):
    lookup = emzed.to_table("key", [None, 1, 2, 3, 1], int)
    lookup.add_column("value", lookup.key + 1, int)
    print(lookup, file=regtest)

    data = emzed.to_table("key", [None, 1, 2, 3, 5], int)
    with pytest.raises(LookupError):
        data.add_column(
            "value", data.key.lookup(lookup.key, lookup.value * lookup.value), int
        )


def test_lookup_from_same_table(regtest):
    t = emzed.to_table("key", [None, 1, 2, 3, 4], int)
    t.add_column("value", t.key + 1, int)
    t.add_column("value_2", t.key.lookup(t.key, t.value + 1000), int)
    print(t, file=regtest)


def test_lookup_object(regtest):
    t1 = emzed.to_table("a", [(1,), (2,)], object)
    t1.add_enumeration()
    t2 = emzed.to_table("id", [0, 1], int)
    t2.add_column("a", t2.id.lookup(t1.id, t1.a), object)
    print(t2, file=regtest)


def test_apply_issue_39(regtest):
    # fix https://sissource.ethz.ch/sispub/emzed/emzed/-/issues/39
    t = emzed.to_table("a", [[1.0, -1.0], [3.0, -5.0]], object)
    t.add_column("max_a", t.apply(max, t.a), int)
    print(t, file=regtest)


def test_apply_on_peakmap_column(regtest, pm):
    t = emzed.to_table("pm", [None, pm], type_=emzed.PeakMap)
    t.add_column("min_rt", t.apply(lambda pm: pm.rt_range()[1], t.pm), emzed.RtType)
    print(t, file=regtest)


def test_apply_on_table_column(regtest, t0):
    t = emzed.to_table("t0", [None, t0], type_=emzed.Table)
    t.add_column("len_t0", t.apply(len, t.t0), int)
    print(t, file=regtest)


def test_summary(regtest, t0, data_path):
    peaks = emzed.io.load_table(data_path("peaks.table"))
    peaks.add_column_with_constant_value("lists", [1, 2, 3], object)
    peaks.add_column_with_constant_value("t0", t0, emzed.Table)
    peaks.add_column_with_constant_value("bool", True, bool)
    print(peaks.summary(), file=regtest)


def test_sort_by(regtest, t0):
    print(t0.sort_by("a", ascending=False), file=regtest)
    print(t0.sort_by("a", ascending=True), file=regtest)


def test_string_like_expressions(regtest):
    t = emzed.to_table("a", [121, 1221, 211], int)
    t.add_column("b", t.apply(str, t.a), str)
    print(t, file=regtest)

    print(t.filter(t.b.startswith("1")), file=regtest)
    print(t.filter(t.b.endswith("1")), file=regtest)
    print(t.filter(t.b.contains("22")), file=regtest)

    print(t.filter(t.a.contains("")), file=regtest)


def test_max_expression(regtest):
    t = emzed.to_table("a", [121, 1221, 211], int)
    t.add_column("b", t.a.max(), int)
    print(t, file=regtest)


def test_is_in(regtest, pm):
    t = emzed.to_table("a", [121, 1221, 211, None], int)
    t.add_column("b", t.apply(str, t.a), str)
    t.add_column("c", [pm, None, None, None], emzed.PeakMap)
    t.set_col_format("c", "%r")

    t0 = emzed.to_table("x", [1, 2], int)
    t.add_column("d", [t0, t0, None, None], emzed.Table)

    t.add_column("e", [[1, 2], 3, (1, 2, 3), None], object)

    print(t.filter(t.a.is_in([121, 211])), file=regtest)
    print(t.filter(t.b.is_in(["121", "211", None])), file=regtest)
    print(t.filter(t.e.is_in([3])), file=regtest)
    print(t.filter(t.e.is_in([(1, 2, 3), 3, [1, 2]])), file=regtest)


def test_add_or_replace(t0, regtest):
    print(t0, file=regtest)
    t0.add_or_replace_column("c", t0.a, int, insert_before="b")
    print(t0, file=regtest)
    t0.add_or_replace_column("c", t0.a + 1)
    print(t0, file=regtest)


def test_mrm_peakmap_in_table(t0, regtest, data_path):
    pm = emzed.io.load_peak_map(data_path("mrm_data.mzML"))
    assert len(pm.spectra) == 0
    assert len(pm.ms_chromatograms) == 8
    t0.add_column("pm", [pm] * len(t0), emzed.PeakMap)
    assert t0[0].pm == pm


def test_to_html(t0, regtest):
    html = t0._repr_html_()
    html = re.sub(' id="T_[^"]*"', "", html)
    html = re.sub("T(_[0-9a-f]+)+_?", "T_xxxx", html)
    print(html, file=regtest)


def test_postfix_issue(regtest):
    t = emzed.to_table("a", [1, 2], int)
    t.rename_postfixes(**{"": "_1"})
    print(t, file=regtest)


def test_drop_columns_meta_data_issue(t0):
    t0.drop_columns("a")
    assert t0._model._conn is t0._meta_data.conn


def test_close_open_bug(data_path, regtest):
    t = emzed.Table.open(data_path("peaks.table"))
    print(t[0].peakmap)
    t.close()
    t = emzed.Table.open(data_path("peaks.table"))
    print(t[0].peakmap)
    print(t, file=regtest)
    t.close()
    print(t, file=regtest)
    with pytest.raises(ValueError):
        t.add_column("b", t.mz, float)


def test_issue_140(regtest):
    t = emzed.to_table("a", [None, None], int)
    print(t.summary(), file=regtest)


def test_issue_161(regtest):
    t = emzed.to_table("a", [1], int)
    t.add_column("div", 1.5 / t.a, float)
    t.add_column("minus", 1.5 - t.a, float)
    t.add_column("mult", 1.5 * t.a, float)
    t.add_column("add", 1.5 + t.a, float)
    print(t, file=regtest)


def test_issue_175():
    t = emzed.to_table("a", [1, 2, 3], int)
    t.add_column("b", t.apply(lambda v: str(v), t.a), str)
    t.add_column_with_constant_value("group", 0, int)

    def fun_with_error(a_s, b_s):
        return sum([a * b for a, b in zip(a_s, b_s)])

    with pytest.raises(TypeError) as e:
        t.add_column("c", t.group_by(t.group).aggregate(fun_with_error, t.a, t.b), int)

    assert "unsupported operand type(s) for +: 'int' and 'str'" in str(e.value)

    def fun_wo_error(a_s, b_s):
        return sum([a * int(b) for a, b in zip(a_s, b_s)])

    t.add_column("c", t.group_by(t.group).aggregate(fun_wo_error, t.a, t.b), int)


def test_issue_178_table_closed_problem(data_path):
    path = data_path("peaks.table")
    t = emzed.Table.open(path)
    t.close()
    assert t.__class__ is not None
    t = emzed.Table.open(path)


def test_table_cleanup(data_path, regtest):
    path = data_path("peaks.table")
    t = emzed.Table.load(path)

    def dump(title):
        print(title, file=regtest)
        for table_name in sorted(list_tables(t._model._conn)):
            print("", table_name, file=regtest)
        print(file=regtest)

    dump("table with first peakmap")

    pm = t.peakmap.unique_value()
    pm2 = emzed.PeakMap.from_(pm)
    t.add_column_with_constant_value("peakmap_2", pm2, emzed.PeakMap)
    dump("table with second peakmap")

    t.drop_columns("peakmap")
    dump("table with first peakmap dropped")

    t.drop_columns("peakmap_2")
    dump("table with second peakmap dropped")

    t0 = emzed.to_table("a", [1, 2, 3], int)
    t.add_column_with_constant_value("table", t0, emzed.Table)
    dump("table with new table in table column")

    t.replace_column_with_constant_value("table", None, emzed.Table)
    dump("table with table in table column replaced")


if __name__ == "__main__":
    pytest.main([__file__])
