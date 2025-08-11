#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>

import math

from . import mass

try:
    from emzed.optimized.formula_fit import formula_table as _formula_table
except ImportError:

    def _formula_table(*a, **kw):
        raise NotImplementedError("could not load optimized code")


def formula_table(
    min_mass,
    max_mass,
    *,
    mass_c=None,  # mass.C12,
    mass_h=None,  # mass.H1,
    mass_n=None,  # mass.N14,
    mass_o=None,  # mass.O16,
    mass_p=None,  # mass.P31,
    mass_s=None,  # mass.S32,
    c_range=None,
    h_range=None,
    n_range=None,
    o_range=None,
    p_range=None,
    s_range=None,
    apply_rules=True,
    apply_rule_1=True,
    apply_rule_2=True,
    apply_rule_4=True,
    apply_rule_5=True,
    apply_rule_6=True,
    rule_45_range="extended",
):
    """
    This is a Python version of HR2 formula generator for CHNOPS,
    see https://fiehnlab.ucdavis.edu/projects/seven-golden-rules

    This function generates a table containing molecular formulas consisting of elements
    C, H, N, O, P and S having a mass in range [**min_mass**, **max_mass**].  For each
    element one can provide an given count or an inclusive range of atom counts
    considered in this process.

    Putting some restrictions on atomcounts, eg **C=(0, 100)**, can speed up the process
    tremendously.
    """
    if mass_c is None:
        mass_c = mass.C12
    if mass_h is None:
        mass_h = mass.H1
    if mass_n is None:
        mass_n = mass.N14
    if mass_o is None:
        mass_o = mass.O16
    if mass_p is None:
        mass_p = mass.P31
    if mass_s is None:
        mass_s = mass.S32

    NMAX = 999_999

    def _check_range(name, value):
        if value is None:
            return 0, None
        if isinstance(value, int):
            return value, value
        assert isinstance(value, (list, tuple)), f"{name} must be list or tuple"
        assert len(value) == 2, f"{name} must have length 2"
        assert isinstance(value[0], (int, float)), f"entries of {name} must be numbers"
        assert isinstance(value[1], (int, float)), f"entries of {name} must be numbers"
        assert value[0] <= value[1], f"first value of {name} is larger than second"
        return value

    c_low, c_high = _check_range("c_range", c_range)
    h_low, h_high = _check_range("h_range", h_range)
    n_low, n_high = _check_range("n_range", n_range)
    o_low, o_high = _check_range("o_range", o_range)
    p_low, p_high = _check_range("p_range", p_range)
    s_low, s_high = _check_range("s_range", s_range)

    c_high = int(math.ceil(max_mass / mass_c) if c_high is None else c_high)
    h_high = int(math.ceil(max_mass / mass_h) if h_high is None else h_high)
    n_high = int(math.ceil(max_mass / mass_n) if n_high is None else n_high)
    o_high = int(math.ceil(max_mass / mass_o) if o_high is None else o_high)
    p_high = int(math.ceil(max_mass / mass_p) if p_high is None else p_high)
    s_high = int(math.ceil(max_mass / mass_s) if s_high is None else s_high)

    apply_rule_1 = apply_rules and apply_rule_1
    apply_rule_2 = apply_rules and apply_rule_2
    apply_rule_4 = apply_rules and apply_rule_4
    apply_rule_5 = apply_rules and apply_rule_5
    apply_rule_6 = apply_rules and apply_rule_6

    if apply_rule_1:
        c_max, h_max, n_max, o_max, p_max, s_max = _rule_1_limits(max_mass)
        c_high = min(c_high if c_high is not None else 999_000, c_max)
        h_high = min(h_high if h_high is not None else 999_000, h_max)
        n_high = min(n_high if n_high is not None else 999_000, n_max)
        o_high = min(o_high if o_high is not None else 999_000, o_max)
        p_high = min(p_high if p_high is not None else 999_000, p_max)
        s_high = min(s_high if s_high is not None else 999_000, s_max)

    h_to_c_max = n_to_c_max = o_to_c_max = p_to_c_max = s_to_c_max = NMAX
    h_to_c_min = n_to_c_min = o_to_c_min = p_to_c_min = s_to_c_min = 0

    if apply_rule_4 or apply_rule_5:
        ratio_limits = _ratio_limits.get(rule_45_range)
        if ratio_limits is None:
            raise ValueError(
                "rule_45_range must be in {}".format(sorted(_ratio_limits.keys()))
            )
        if apply_rule_4:
            h_to_c_min, h_to_c_max = ratio_limits[:2]
        if apply_rule_5:
            (
                _,
                _,
                n_to_c_min,
                n_to_c_max,
                o_to_c_min,
                o_to_c_max,
                p_to_c_min,
                p_to_c_max,
                s_to_c_min,
                s_to_c_max,
            ) = ratio_limits

    t = _formula_table(
        min_mass,
        max_mass,
        c_low,
        c_high,
        h_low,
        h_high,
        n_low,
        n_high,
        o_low,
        o_high,
        p_low,
        p_high,
        s_low,
        s_high,
        h_to_c_min,
        h_to_c_max,
        n_to_c_min,
        n_to_c_max,
        o_to_c_min,
        o_to_c_max,
        p_to_c_min,
        p_to_c_max,
        s_to_c_min,
        s_to_c_max,
        mass_c,
        mass_h,
        mass_n,
        mass_o,
        mass_p,
        mass_s,
        apply_rule_2,
        apply_rule_6,
    )
    return t


_ratio_limits = dict(
    common=(0.2, 3.1, 0.0, 1.3, 0.0, 1.2, 0.0, 0.3, 0.0, 0.8),
    extended=(0.1, 6.0, 0.0, 4.0, 0.0, 4.0, 0.0, 2.0, 0.0, 3.0),
)


def _rule_1_limits(mz_max):
    bin_ = min(int(mz_max / 500), 4)
    c_max = [39, 78, 156, 162][bin_]
    h_max = [72, 127, 236, 208][bin_]
    n_max = [20, 25, 20, 48][bin_]
    o_max = [20, 27, 63, 78][bin_]
    p_max = [9, 9, 9, 6][bin_]
    s_max = [10, 14, 14, 9][bin_]
    return c_max, h_max, n_max, o_max, p_max, s_max
