#!/usr/bin/env python

from .molecular_formula import MolecularFormula

e = 5.4857990946e-4
p = 1.007276466812
n = 1.00866491600


def of(mf, **specialisation):
    value = MolecularFormula(mf).mass(**specialisation)
    if value is None:
        raise ValueError(f"formula '{mf}' is not valid")
    return value


_loaded = {}


def __getattr__(name):
    # mimics lazy import
    if not _loaded:
        from .elements import load_elements

        _, mass_dict, _, _ = load_elements()
        _loaded.update(mass_dict)
    return _loaded[name]


def __dir__():
    """forward attributes for autocompletion"""
    return list(_loaded.keys())
