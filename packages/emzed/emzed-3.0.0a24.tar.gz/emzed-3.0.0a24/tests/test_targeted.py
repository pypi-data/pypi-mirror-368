#!/usr/bin/env python

import pytest

import emzed


@pytest.mark.parametrize("z", [1, -1, 2])
def test_solution_space(z, regtest):
    all_adducts = emzed.adducts.all
    adducts = all_adducts.filter(all_adducts.sign_z == z)
    print(adducts, file=regtest)

    targets = emzed.Table.create_table(
        ["mf", "rtmin", "rtmax"],
        [str, emzed.RtType, emzed.RtType],
        rows=[["C21H30O2", 10, 60], ["C20H25N3O", None, None]],
    )
    targets.add_enumeration()
    print(targets, file=regtest)

    t = emzed.targeted.solution_space(targets, adducts, 0.99)
    print(t, file=regtest)

    t = emzed.targeted.solution_space(targets, adducts, 0.99, 10_000)
    print(t, file=regtest)


def test_solution_space_2m(regtest):
    all_adducts = emzed.adducts.all
    expr = all_adducts.adduct_name.startswith("2")
    adducts = all_adducts.filter(expr)
    print(adducts, file=regtest)

    targets = emzed.Table.create_table(
        ["mf", "rtmin", "rtmax"],
        [str, emzed.RtType, emzed.RtType],
        rows=[["C21H30O2", 10, 60], ["C20H25N3O", None, None]],
    )
    targets.add_enumeration()
    print(targets, file=regtest)

    t = emzed.targeted.solution_space(targets, adducts, 0.99)
    print(t, file=regtest)

    t = emzed.targeted.solution_space(targets, adducts, 0.99, 10_000)
    print(t, file=regtest)


def test_solution_space_3m(regtest):
    all_adducts = emzed.adducts.all
    expr = all_adducts.adduct_name.startswith("3")
    adducts = all_adducts.filter(expr)
    print(adducts, file=regtest)

    targets = emzed.Table.create_table(
        ["mf", "rtmin", "rtmax"],
        [str, emzed.RtType, emzed.RtType],
        rows=[["C21H30O2", 10, 60], ["C20H25N3O", None, None]],
    )
    targets.add_enumeration()
    print(targets, file=regtest)

    t = emzed.targeted.solution_space(targets, adducts, 0.99)
    print(t, file=regtest)

    t = emzed.targeted.solution_space(targets, adducts, 0.99, 10_000)
    print(t, file=regtest)


def test_h_error():
    targets = emzed.to_table("mf", ["H"], str)
    targets.add_enumeration()
    emzed.targeted.solution_space(targets, emzed.adducts.single_charged)
