#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>

import os
import pickle

import pytest

import emzed
from emzed import mf
from emzed.chemistry import (
    compute_centroids,
    formula_table,
    mass,
    measured_centroids,
    plot_profile,
)
from emzed.chemistry.formula_parser import join_formula, parse_formula


def test_delayed_elements_table(regtest):
    from emzed.chemistry.elements import DelayedElementsTable

    for method, args in [
        ("__getattr__", ("symbol",)),
        ("__str__", ()),
        ("__repr__", ()),
        ("__dir__", ()),
        ("__len__", ()),
        ("__eq__", (0,)),
        ("__iter__", ()),
        ("__getitem__", (0,)),
    ]:
        t = DelayedElementsTable()
        getattr(t, method)(*args)
        assert isinstance(t, emzed.Table)
        assert not isinstance(t, DelayedElementsTable)

    t = DelayedElementsTable()
    with pytest.raises(NotImplementedError):
        pickle.dumps(t)


def test_elements(regtest):
    print(emzed.elements, file=regtest)


def test_mass():
    assert emzed.mass.C12 == 12.0
    assert emzed.mass.C[12] == 12.0
    assert sorted(emzed.mass.C.keys()) == [12, 13]

    assert emzed.mass.e > 0
    assert emzed.mass.p > 0
    assert emzed.mass.n > 0


def test_abundance():
    assert emzed.abundance.C12 + emzed.abundance.C13 == 1.0
    assert emzed.abundance.C[12] + emzed.abundance.C[13] == 1.0


def test_adducts(regtest):
    import emzed.chemistry.adducts as adducts

    print(adducts.all, file=regtest)


def test_adduct_formulas_valid(regtest):
    import emzed.chemistry.adducts as adducts

    adducts = adducts.all.copy()

    adducts.add_column(
        "mass_add", adducts.apply(mass.of, adducts.adduct_add), emzed.MzType
    )
    adducts.add_column(
        "mass_sub", adducts.apply(mass.of, adducts.adduct_sub), emzed.MzType
    )


def test_mf():
    mf = emzed.mf("[13]C7")
    assert mf.as_dict() == {("C", 13): 7}
    assert str(mf) == "[13]C7"
    assert mf.mass() == emzed.mass.C13 * 7

    assert (3 * mf).mass() == emzed.mass.of("[13]C21")

    with pytest.raises(ValueError):
        mass.of("X")


def test_parser():
    assert join_formula(parse_formula("CHNOPS")) == "CHNOPS"
    assert join_formula(parse_formula("COPSHN")) == "CHNOPS"
    assert join_formula(parse_formula("H2O")) == "H2O"
    assert join_formula(parse_formula("[13]CC")) == "C[13]C"
    assert join_formula(parse_formula("C(CH2)7")) == "C8H14"
    assert join_formula(parse_formula("H2 O")) == "H2O"
    assert join_formula(parse_formula("H2 O N ")) == "H2NO"


def test_molecular_formula_object():
    assert (mf("H2O") + mf("NaCl")) == mf("H2ONaCl")
    assert (mf("H2ONaCl") - mf("NaCl")) == mf("H2O")

    assert abs(mf("H2O").mass() - 18.010_565) <= 1e-5, mf("H2O").mass()
    assert abs(mf("[13]C").mass() - 13.003_355) <= 1e-6
    assert abs(mf("[12]C").mass() - 12.0) <= 1e-6

    assert mf("Xx").mass() is None


def test_formula_fit(regtest):
    t = formula_table(100, 100.013)
    print(t, file=regtest)

    t = formula_table(100, 100.013, apply_rules=False)
    print(t, file=regtest)

    t = formula_table(100, 100.013, c_range=(1, 7))
    print(t, file=regtest)

    t = formula_table(100, 100.013, h_range=(1, 7))
    print(t, file=regtest)

    t = formula_table(100, 100.013, n_range=(1, 7))
    print(t, file=regtest)

    t = formula_table(100, 100.013, o_range=(1, 7))  # noqa E741
    print(t, file=regtest)

    t = formula_table(100, 100.013, p_range=(1, 7))
    print(t, file=regtest)

    t = formula_table(100, 100.013, s_range=(1, 7))
    print(t, file=regtest)

    t = formula_table(100, 100.013, mass_c=mass.C13)
    print(t, file=regtest)

    t = formula_table(100, 100.013, c_range=7)
    print(t, file=regtest)

    t = formula_table(100, 100.013, h_range=1)
    print(t, file=regtest)

    t = formula_table(100, 100.013, n_range=1)
    print(t, file=regtest)

    t = formula_table(100, 100.013, o_range=1)  # noqa E741
    print(t, file=regtest)

    t = formula_table(100, 100.013, p_range=0)
    print(t, file=regtest)

    t = formula_table(100, 100.013, s_range=0)
    print(t, file=regtest)


def test_isotope_pattern_generator(regtest, tmpdir):
    for explained_p in (0.9, 0.99, 0.999, 0.9999):
        t = compute_centroids("C7[13]C2HO3", explained_p)
        sum_ = sum(t.abundance)
        assert sum_ >= explained_p

    print(t, file=regtest)
    print(compute_centroids("C12S7", 0.995), file=regtest)
    print(measured_centroids("C12S7", 250_000, 0.995), file=regtest)
    print(measured_centroids("C12S7", 100_000, 0.999), file=regtest)

    path = tmpdir.join("plot.png").strpath
    plot_profile("C12S7", 250_000, 0.995, path=path)
    assert os.path.exists(path)


def test_isotope_pattern_generator_fix_multiples(regtest):
    mf = "C20H25N3ONa2"
    print(measured_centroids(mf, 10000, 0.999), file=regtest)


def test_measured_centroids_different_abundance(regtest):
    print(
        measured_centroids(
            "C6H12O6",
            R=6e4,
            explained_abundance=0.999,
            abundances=dict(O={16: 0.01, 17: 0.01, 18: 0.98}),
        ),
        file=regtest,
    )


def test_adducts_are_unique():
    import emzed.chemistry.adducts as adducts

    assert len(list(adducts.all.adduct_name)) == len(set(adducts.all.adduct_name))


def test_issue_111():
    """some atom numbers where strings and not integers"""
    import emzed.chemistry.mass as mass

    assert all(isinstance(k, int) for k in mass.Nd.keys())
