import json
import re
import sys
from collections import defaultdict

import pyopenms

from emzed.table import Table

_loaded = {}


if sys.version_info < (3, 9):
    # importlib.resources either doesn't exist or lacks the files()
    # function, so use the PyPI version:
    import importlib_resources
else:
    # importlib.resources has files(), so use that:
    import importlib.resources as importlib_resources


class DelayedElementsTable:
    def __getattr__(self, name):
        self._load()
        return getattr(elements, name)

    def __str__(self):
        self._load()
        return str(self)

    def __repr__(self):
        self._load()
        return repr(self)

    def __dir__(self):
        self._load()
        return dir(self)

    def __len__(self):
        self._load()
        return len(self)

    def __eq__(self, other):
        self._load()
        return self.__eq__(other)

    def __iter__(self):
        self._load()
        return self.__iter__()

    def __getitem__(self, ix):
        self._load()
        return self.__getitem__(ix)

    def __getstate__(self):
        self._load()
        return self.__getstate__()

    def __setstate__(self, data):
        self._load()
        return self.__setstate__(data)

    def _load(self):
        from emzed.chemistry.elements import _elements as elements

        self.__class__ = elements.__class__
        self.__dict__ = elements.__dict__


elements = DelayedElementsTable()


def __getattr__(name):
    # mimics lazy import

    if name not in ("_elements", "mass_dict", "abundance_dict", "masses"):
        raise AttributeError(f"module {__name__} has no attribute {name}")
    if not _loaded:
        elements, mass_dict, abundance_dict, masses = load_elements()
        _loaded["_elements"] = _loaded["elements"] = elements
        _loaded["mass_dict"] = mass_dict
        _loaded["abundance_dict"] = abundance_dict
        _loaded["masses"] = masses
    return _loaded[name]


def load_elements():
    pkg = importlib_resources.files("emzed")
    path = str(pkg / "chemistry" / "Elements.xml")
    param = pyopenms.Param()
    ph = pyopenms.ParamXMLFile()
    ph.load(path, param)

    # pubchem is more complete, but for backwards compatibility
    # we take the openms data per default and extend by the pubchem
    # data:
    symbols, atomic_numbers, atomic_masses, abundances = load_elements_pubchem()

    symbols.update(_extract_symbols(param))
    atomic_numbers.update(_extract_atomic_numbers(param))
    abundances.update(_extract_isotope_abundances(param))
    atomic_masses.update(_extract_isotope_atomic_masses(param))

    average_masses = {}
    for name in symbols.keys():
        mass_sum = 0.0
        abundance_sum = 0.0
        for mass_number, abundance_in_percent in abundances[name].items():
            mass = atomic_masses[name][mass_number]
            mass_sum += mass * abundance_in_percent
            abundance_sum += abundance_in_percent
        average_masses[name] = mass_sum / abundance_sum

    table = create_elements_table(
        symbols, atomic_numbers, abundances, atomic_masses, average_masses
    )

    mass_dict = create_mass_dict(symbols, atomic_masses, average_masses)
    abundance_dict = create_abundance_dict(symbols, abundances)

    masses = {}
    for row in table:
        masses[row.symbol, row.mass_number] = row.mass

    for name, symbol in symbols.items():
        minmass = min(mass for (s, mass) in masses if s == symbol)
        masses[symbol, None] = masses[symbol, minmass]

    return table, mass_dict, abundance_dict, masses


def parse_float(txt):
    """txt from pubchem can be sth like "1.23 45 (23)" or '[1.2211, 1.2212]'"""
    txt = txt.replace(" ", "")
    txt, _, _ = txt.partition("(")
    if "," in txt:
        lower, _, upper = txt.strip("[]").partition(",")
        return 0.5 * float(lower) + 0.5 * float(upper)
    return float(txt)


def load_elements_pubchem():
    pkg = importlib_resources.files("emzed")
    path = pkg / "chemistry" / "elements_pubchem.json"
    with path.open() as fh:
        data = json.load(fh)

    masses = {}
    abundances = {}
    atomic_numbers = {}
    symbols = {}

    for num, name, isotopes, masses_, abundances_ in data:
        if isotopes is None or masses is None or abundances is None:
            # happens if there are no stable isotopes
            continue

        name, isotopes, masses_, abundances__ = fix_pubchem_entries(
            name, isotopes, masses_, abundances_
        )

        atomic_numbers[name] = num

        for isotope, mass, abundance in zip(isotopes, masses_, abundances_):
            number, symbol = re.match(r"(\d+)([A-Z][a-z]?)", isotope).groups()
            number = int(number)
            symbols[name] = symbol
            if name not in masses:
                masses[name] = {}
            masses[name][number] = parse_float(mass)
            if name not in abundances:
                abundances[name] = {}
            abundances[name][number] = 100 * parse_float(abundance)

    return symbols, atomic_numbers, masses, abundances


def fix_pubchem_entries(name, isotopes, masses, abundances):
    if name == "Strontium":
        abundances[0] = masses[0]
        iso0 = isotopes[0]
        masses[0] = iso0.split(" ", 1)[1]
        isotopes[0] = iso0.split(" ", 1)[0]
    if name == "Scandium":
        isotopes = ["45Sc"]
        masses = ["44.955907503"]
        abundances = ["1.0"]

    name = {
        "Boron": "Bor",
        "Aluminum": "Aluminium",
        "Iron": "Ferrum",
        "Cesium": "Caesium",
    }.get(name, name)

    return name, isotopes, masses, abundances


def create_mass_dict(symbols, atomic_masses, average_masses):
    result = {}

    for name, symbol in symbols.items():
        result[symbol] = average_masses[name]
        data = atomic_masses[name]
        for mass_number, mass in data.items():
            result[f"{symbol}{mass_number}"] = mass
        result[symbol] = data

    return result


def create_abundance_dict(symbols, abundances):
    result = {}

    for name, symbol in symbols.items():
        data = abundances[name].items()
        for mass_number, abundance_in_percent in data:
            result[f"{symbol}{mass_number}"] = abundance_in_percent / 100.0
        result[symbol] = {_symbol: value / 100 for _symbol, value in data}

    return result


def create_elements_table(
    symbols, atomic_numbers, abundances, atomic_masses, average_masses
):
    rows = []

    for name, symbol in symbols.items():
        atomic_number = atomic_numbers[name]
        average_mass = average_masses[name]
        for mass_number, abundance_in_percent in abundances[name].items():
            mass = atomic_masses[name][mass_number]
            rows.append(
                [
                    atomic_number,
                    symbol,
                    name,
                    average_mass,
                    mass_number,
                    mass,
                    abundance_in_percent / 100.0,
                ]
            )

    rows.sort()

    return Table.create_table(
        [
            "atomic_number",
            "symbol",
            "name",
            "average_mass",
            "mass_number",
            "mass",
            "abundance",
        ],
        [int, str, str, float, int, float, float],
        ["%d", "%s", "%s", "%.10f", "%d", "%.10f", "%.3f"],
        rows=rows,
    )


def _extract_symbols(param):
    return _filter_on_field_2(param, "Symbol")


def _extract_atomic_numbers(param):
    return _filter_on_field_2(param, "AtomicNumber")


def _extract_isotope_abundances(param):
    return _filter_on_field_4(param, "RelativeAbundance")


def _extract_isotope_atomic_masses(param):
    return _filter_on_field_4(param, "AtomicMass")


def _filter_on_field_2(param, what):
    result = {}
    for full_name, fields, value in _iter_items(param):
        if fields[2] == what:
            result[full_name] = value
    return result


def _filter_on_field_4(param, what):
    result = defaultdict(dict)
    for full_name, fields, value in _iter_items(param):
        if fields[2] == "Isotopes" and fields[4] == what:
            mass_number = int(fields[3])
            result[full_name][mass_number] = value
    return result


def _iter_items(param):
    for key, value in param.asDict().items():
        key = str(key, "ascii")
        if isinstance(value, bytes):
            value = str(value, "ascii")

        fields = key.split(":")
        full_name = fields[1]
        yield full_name, fields, value
