#!/usr/bin/env python

from emzed import MzType, Table, mass
from emzed import mf as molecular_formula
from emzed.chemistry import compute_centroids, measured_centroids
from emzed.chemistry.adducts import _check_adduct_table


def solution_space(targets, adducts, explained_abundance=0.999, resolution=None):
    targets._ensure_col_names("id", "mf")
    _check_adduct_table(adducts)

    result_col_names = [
        "target_id",
        "adduct_id",
        "m_multiplier",
        "adduct_add",
        "adduct_sub",
        "z",
        "full_mf",
        "isotope_id",
        "isotope_decomposition",
        "m0",
        "abundance",
        "mz",
    ]

    if len(adducts) == 0 or len(targets) == 0:
        return Table.create_table(
            result_col_names,
            [int, int, int, str, str, int, str, int, str, MzType, float, MzType],
            rows=[],
        )

    if targets.supported_postfixes("") != [""]:
        raise ValueError("can not process targets table with postfixes in column names")

    conflicting_col_names = set(result_col_names) & set(targets.col_names)
    if conflicting_col_names:
        conflicting = ", ".join(sorted(conflicting_col_names))
        raise ValueError(f"column names {conflicting} not allowed in targets table")

    t = targets.join(adducts)
    t.rename_columns(id__0="adduct_id", id="target_id")
    t.rename_postfixes(__0="")
    t.add_enumeration()

    def add_formulas(mf, m_multiplier, adduct_add, adduct_sub):
        return (
            m_multiplier * molecular_formula(mf)
            + molecular_formula(adduct_add)
            - molecular_formula(adduct_sub)
        ).as_string()

    t.add_column(
        "full_mf",
        t.apply(add_formulas, t.mf, t.m_multiplier, t.adduct_add, t.adduct_sub),
        str,
    )

    # invalid formulas can arise when we subtract e.g. H2O which is not present
    # in t.mf:
    t = t.filter(t.full_mf.is_not_none(), keep_view=True)

    # corner case: for target == aduct we might anihilate both which results in an
    # empty full_mf
    t = t.filter(t.full_mf != "", keep_view=True)

    isotopes = Table.stack_tables(
        [
            _isotope_table(row.id, row.full_mf, resolution, explained_abundance)
            for row in t
        ]
    )
    t = t.join(isotopes, t.id == isotopes.id)
    t.drop_columns("id__0", "id")

    t.rename_postfixes(__0="")
    t.add_column("mz", (t.m0 - mass.e * t.sign_z) / t.z, MzType)

    t = t.sort_by("target_id", "adduct_id", "isotope_id")
    t.add_enumeration()
    return t


def _isotope_table(id_, mf, resolution, explained_abundance):
    if resolution is None:
        t = compute_centroids(mf, explained_abundance)
        t.rename_columns(id="isotope_id", mf="isotope_decomposition")
    else:
        t = measured_centroids(mf, resolution, explained_abundance)
        t.rename_columns(id="isotope_id", R="isotope_decomposition")
        t.replace_column_with_constant_value("isotope_decomposition", None, str)
    t.add_column_with_constant_value("id", id_, int, insert_before=0)
    return t
