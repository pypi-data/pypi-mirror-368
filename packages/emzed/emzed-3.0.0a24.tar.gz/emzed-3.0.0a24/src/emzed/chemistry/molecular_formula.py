#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>
from collections.abc import Mapping

from . import elements
from .formula_parser import join_formula, parse_formula


class MolecularFormula:
    def __init__(self, form):
        if isinstance(form, str):
            self._string_form = form
            self._dict_form = parse_formula(form)
        elif isinstance(form, Mapping):
            if any(count < 0 for count in form.values()):
                self._string_form = None
            else:
                self._string_form = join_formula(form)
            # cleanup zero counts:
            self._dict_form = dict((e, c) for (e, c) in form.items() if c)
        else:
            raise Exception("can not handle argument %s" % form)

    def as_dict(self):
        # make sure that we return a dict and not another kind of mapping:
        return dict(self._dict_form)

    def __str__(self):
        return self._string_form or "<invalid>"

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self}'>"

    def __eq__(self, other):
        return self.as_dict() == other.as_dict()

    def as_string(self):
        return self._string_form

    def __add__(self, mf):
        assert isinstance(mf, MolecularFormula)
        dd = self.as_dict().copy()
        for elem, count in mf.as_dict().items():
            dd[elem] = dd.get(elem, 0) + count
        return MolecularFormula(dd)

    def __sub__(self, mf):
        assert isinstance(mf, MolecularFormula)
        dd = self.as_dict().copy()
        for elem, count in mf.as_dict().items():
            dd[elem] = dd.get(elem, 0) - count
        return MolecularFormula(dd)

    def __mul__(self, factor):
        assert isinstance(factor, int)
        dd = self.as_dict().copy()
        for elem, count in dd.items():
            dd[elem] = dd[elem] * factor
        return MolecularFormula(dd)

    __rmul__ = __mul__

    def mass(self, **specialisations):
        """
        specialisations maps symbol to a dictionary d providing a mass
        by d["mass"], eg:

            specialisations = { 'C' : 12.0 }
            inst.mass(C=12.0)

        or if you use the mass module:

            inst.mass(C=mass.C12)

        or you use mass in connection with the elements module:

            inst.mass(C=elements.C12)
        """

        items = self._dict_form.items()

        def get_mass(sym, massnum):
            # if mass num is None, and there is a specialisation provided, we take this
            # specialisation.  else we consider monoisotopic mass
            if massnum is None:
                specialisation = specialisations.get(sym)
                if specialisation is not None:
                    # if isinstance(specialisation, Mapping):
                    # return specialisation["mass"]
                    try:
                        return float(specialisation)
                    except ValueError:
                        raise Exception(
                            "specialisation %r for %s invalid" % (specialisation, sym)
                        )

            return elements.masses.get((sym, massnum))

        single_masses = list(get_mass(sym, massnum) for (sym, massnum), _ in items)
        if None in single_masses:
            return None
        return sum(m * c for m, (_, c) in zip(single_masses, items))
