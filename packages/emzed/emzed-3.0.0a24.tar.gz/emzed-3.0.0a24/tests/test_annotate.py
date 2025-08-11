#!/usr/bin/env python

import random

import pytest

import emzed


def test_annotate_adducts_simple(regtest):
    targets = emzed.Table.create_table(
        ["mf", "rt"], [str, emzed.RtType], rows=[["H2O", 10]]
    )
    targets.add_enumeration()
    adducts = emzed.Table.stack_tables(
        [
            emzed.adducts.M_plus_Br,
            emzed.adducts.Two_M_plus_H,
            emzed.adducts.M_plus_ACN_plus_H,
            emzed.adducts.M_minus_H,
        ]
    )
    adducts.drop_columns("id")
    adducts.add_enumeration()
    targets = emzed.targeted.solution_space(targets, adducts, 0.99)
    peaks = targets.extract_columns("target_id", "rt", "mz", "adduct_name")
    peaks.rename_columns(adduct_name="original_adduct_name")

    result = emzed.annotate.annotate_adducts(
        peaks, adducts, 2e-5, 5, explained_abundance=0.99
    ).sort_by("adduct_cluster_id")

    assert len(result) == len(targets) - 1
    assert set(result.adduct_cluster_id) == {0}

    assert len(result.filter(result.adduct_name == result.original_adduct_name)) == len(
        result
    )
    print(result)
    print(result, file=regtest)


def test_annotate_adducts_simple_with_noise(regtest):
    targets = emzed.Table.create_table(
        ["mf", "rt"], [str, emzed.RtType], rows=[["H2O", 10]]
    )
    targets.add_enumeration()
    adducts = emzed.Table.stack_tables(
        [
            emzed.adducts.M_plus_Br,
            emzed.adducts.Two_M_plus_H,
            emzed.adducts.M_plus_ACN_plus_H,
            emzed.adducts.M_minus_H,
        ]
    )
    adducts.drop_columns("id")
    adducts.add_enumeration()
    targets = emzed.targeted.solution_space(targets, adducts, 0.99)
    peaks = targets.extract_columns("id", "target_id", "rt", "mz", "adduct_name")
    peaks.rename_columns(adduct_name="original_adduct_name")

    random.seed(42)
    peaks.replace_column("mz", peaks.mz + 1e-5 * (peaks.apply(random.random) - 0.5))

    result = emzed.annotate.annotate_adducts(
        peaks, adducts, 2e-5, 5, explained_abundance=0.99
    ).sort_by("adduct_cluster_id")

    assert len(result) == len(targets) - 1
    assert set(result.adduct_cluster_id) == {0}

    assert len(result.filter(result.adduct_name == result.original_adduct_name)) == len(
        result
    )
    print(result.sort_by("id", "adduct_cluster_id"), file=regtest)


def test_annotate_adducts_simple_with_different_rt(regtest):
    targets = emzed.Table.create_table(
        ["mf", "rt"], [str, emzed.RtType], rows=[["H2O", 10], ["H2O", 20]]
    )
    targets.add_enumeration()
    adducts = emzed.Table.stack_tables(
        [
            emzed.adducts.M_plus_Br,
            emzed.adducts.Two_M_plus_H,
            emzed.adducts.M_plus_ACN_plus_H,
            emzed.adducts.M_minus_H,
            emzed.adducts.M_plus_H_plus_Na,
        ]
    )
    adducts.drop_columns("id")
    adducts.add_enumeration()
    targets = emzed.targeted.solution_space(targets, adducts, 0.99)
    peaks = targets.extract_columns("id", "target_id", "rt", "mz", "adduct_name")
    peaks.rename_columns(adduct_name="original_adduct_name")

    result = emzed.annotate.annotate_adducts(
        peaks, adducts, 1e-5, 9.99, explained_abundance=0.99
    ).sort_by("adduct_cluster_id")
    print(result.sort_by("id", "adduct_cluster_id"), file=regtest)

    assert len(result) == 16
    assert set(result.adduct_cluster_id) == {0, 1}

    for t in result.split_by_iter("rt"):
        assert len(set(t.adduct_cluster_id)) == 1

    assert len(result.filter(result.adduct_name == result.original_adduct_name)) == len(
        result
    )


def test_annotate_adducts_complex(regtest):
    # we expect that all matches original adduct_name == adduct_name
    # have the correct mass of H2O.
    targets = emzed.Table.create_table(
        ["mf", "rt"], [str, emzed.RtType], rows=[["H2O", 10]]
    )
    targets.add_enumeration()
    adducts = emzed.Table.stack_tables(
        [
            emzed.adducts.Two_M_plus_FA_minus_H,
            emzed.adducts.M_plus,
            emzed.adducts.M_plus_ACN_plus_H,
        ]
    )
    adducts = emzed.adducts.all
    targets = emzed.targeted.solution_space(targets, adducts, 0.99)
    peaks = targets.extract_columns("id", "target_id", "rt", "mz", "adduct_name")
    peaks.rename_columns(adduct_name="original_adduct_name")
    result = emzed.annotate.annotate_adducts(
        peaks, adducts, 1e-5, 5, explained_abundance=0.99
    ).sort_by("adduct_cluster_id")
    print(result.sort_by("id", "adduct_cluster_id"), file=regtest)

    # we expect matches for all adducts with exception of neutral M
    found = result.filter(result.adduct_name == result.original_adduct_name)
    found.add_column(
        "keep", found.adduct_m0.approx_equal(emzed.mass.of("H2O"), 1e-4, 0), bool
    )
    found = found.filter(found.keep)
    found.drop_columns("keep")
    assert set(peaks.original_adduct_name) - set(found.adduct_name) == set(["M"])


def test_annotate_adducts_more_realistic(data_path, regtest):
    targets = emzed.Table.create_table(
        ["mf", "rt"], [str, emzed.RtType], rows=[["H2O", 10], ["H2S", 20]]
    )
    targets.add_enumeration()

    adducts = emzed.adducts.all

    targets = emzed.targeted.solution_space(targets, adducts, 0.99)
    peaks = targets.extract_columns("id", "target_id", "rt", "mz", "adduct_name")
    peaks.rename_columns(adduct_name="original_adduct_name")

    # reduce matches by distorting peaks
    random.seed(42)
    peaks.replace_column("mz", peaks.mz + 3e-4 * (peaks.apply(random.random)))
    peaks.replace_column("rt", peaks.rt + 4 * (peaks.apply(random.random)))

    max_rt = peaks.rt.max().eval()

    peak_tables = []
    for i in range(2):
        peaks.replace_column("rt", peaks.rt + max_rt + 2)
        peak_tables.append(peaks.consolidate())

    peaks = emzed.Table.stack_tables(peak_tables)
    peaks.drop_columns("id")
    peaks.add_enumeration()

    adducts = emzed.adducts.positive

    with regtest:
        result = emzed.annotate.annotate_adducts(
            peaks, adducts, 1e-5, 2, explained_abundance=0.99
        ).sort_by("adduct_cluster_id")

    found = result.filter(result.adduct_cluster_id.is_not_none()).sort_by("adduct_m0")
    print(found, file=regtest)

    assert len(found) == 728


def test_annotate_corner_cases(regtest):
    t0 = emzed.to_table("mz", [338.802399, 339.132507], emzed.MzType)
    t0.add_column("rt", [10, 10], emzed.RtType)
    adducts = emzed.adducts.negative

    t1 = emzed.annotate.annotate_adducts(t0, adducts, 0.003, 2.0)
    print(t1, file=regtest)


def test_issue_139():
    t0 = emzed.to_table("mz", [338.802399, 339.132507], emzed.MzType)
    t0.add_column("rt", [10, 10], emzed.RtType)
    adducts = emzed.adducts.negative

    before = t0.col_names
    emzed.annotate.annotate_adducts(t0, adducts, 0.003, 2.0)
    assert t0.col_names == before


@pytest.fixture
def _t():
    adducts = emzed.Table.stack_tables(
        [emzed.adducts.M_minus_H, emzed.adducts.M_minus_3H]
    )
    mf = "C6H13O9P"
    t = emzed.to_table("mf", [mf], str)
    t.add_enumeration()
    t.add_column_with_constant_value("rt", 12.5 * 60, emzed.RtType)
    t = emzed.targeted.solution_space(t, adducts, 0.2, 6e4)
    colnames = ["z", "mz", "rt"]
    return t.extract_columns(*colnames)


def test_annotate_issue_162_0(_t):
    # annotate inverses targeted_solution_space
    m0 = emzed.mass.of("C6H13O9P")
    adducts = emzed.Table.stack_tables(
        [emzed.adducts.M_minus_H, emzed.adducts.M_minus_3H]
    )
    t_a = emzed.annotate.annotate_adducts(
        _t, adducts, 0.0001, 1.0, explained_abundance=0.3
    )
    assert all([abs(m0 - _m0) < 1e-5 for _m0 in t_a.adduct_m0])


def test_annotate_issue_162_1(_t):
    # solution includes 2M-H and 3M-H with higher mz tolerance
    adducts = emzed.adducts.negative
    t_a = emzed.annotate.annotate_adducts(
        _t, adducts, 0.001, 1.0, explained_abundance=0.3
    )
    expected = set(["M-H", "2M-H", "3M-H", "M-2H", "M-3H"])
    assert set(t_a.adduct_name) - (expected) == set([])
