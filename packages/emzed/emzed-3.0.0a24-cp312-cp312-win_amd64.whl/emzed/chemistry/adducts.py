ACN = "C2H3N"
IsoProp = "C3H8O"
Methanol = "CH3OH"
DMSO = "C2H6OS"

Hac = "C2H4O2"
TFA = "CF3CO2H"
FA = "H2CO2"


_default_adducts = [
    ("M+", 1, "", "", 1),
    ("M+H", 1, "H", "", 1),
    ("M+NH4", 1, "NH4", "", 1),
    ("M+H+NH4", 1, "HNH4", "", 2),
    ("M+Na", 1, "Na", "", 1),
    ("M+H-2H2O", 1, "H", "(H2O)2", 1),
    ("M+H-H2O", 1, "H", "H2O", 1),
    ("M+K", 1, "K", "", 1),
    ("M+ACN+H", 1, "C2H3NH", "", 1),
    ("M+2ACN+H", 1, f"({ACN})2H", "", 1),
    ("M+2ACN+2H", 1, f"({ACN})2H2", "", 2),
    ("M+3ACN+2H", 1, f"({ACN})3H2", "", 2),
    ("M+ACN+2H", 1, f"({ACN})1H2", "", 2),
    ("M+ACN+Na", 1, f"({ACN})1Na", "", 1),
    ("M+2Na-H", 1, "Na2", "H", 1),
    ("M+Li", 1, "Li", "", 1),
    ("M+CH3OH+H", 1, f"{Methanol}H", "", 1),
    ("M+2H", 1, "H2", "", 2),
    ("M+H+Na", 1, "HNa", "", 2),
    ("M+H+K", 1, "HK", "", 2),
    ("M+3H", 1, "H3", "", 3),
    ("M+2H+Na", 1, "(H2)1Na", "", 3),
    ("M+2Na", 1, "Na2", "", 2),
    ("M+2K-H", 1, "K2", "H", 1),
    ("M+3Na", 1, "Na3", "", 3),
    ("M+2Na+H", 1, "(Na2)1H", "", 3),
    ("M+IsoProp+H", 1, f"({IsoProp})1H", "", 1),
    ("M+IsoProp+Na+H", 1, f"({IsoProp})1NaH", "", 1),
    ("M+DMSO+H", 1, f"({DMSO})1H", "", 1),
    ("M-", 1, "", "", -1),
    ("M-H", 1, "", "H", -1),
    ("M-2H", 1, "", "H2", -2),
    ("M-3H", 1, "", "H3", -3),
    ("M-H2O-H", 1, "", "H2OH", -1),
    ("M+Na-2H", 1, "Na", "H2", -1),
    ("M+Cl", 1, "Cl", "", -1),
    ("M+K-2H", 1, "K", "H2", -1),
    ("M+KCl-H", 1, "KCl", "H", -1),
    ("M+FA-H", 1, FA, "H", -1),
    ("M+F", 1, "F", "", -1),
    ("M+Hac-H", 1, Hac, "H", -1),
    ("M+Br", 1, "Br", "", -1),
    ("M+TFA-H", 1, TFA, "H", -1),
    ("2M+H", 2, "H", "", 1),
    ("2M+NH4", 2, "NH4", "", 1),
    ("2M+Na", 2, "Na", "", 1),
    ("2M+K", 2, "K", "", 1),
    ("2M+ACN+H", 2, f"({ACN})1H", "", 1),
    ("2M+ACN+Na", 2, f"({ACN})1Na", "", 1),
    ("2M-H", 2, "", "H", -1),
    ("2M+FA-H", 2, FA, "H", -1),
    ("2M+Hac-H", 2, Hac, "H", -1),
    ("3M-H", 3, "", "H", -1),
    ("M", 1, "", "", 0),
]

_default_adducts.sort(key=lambda row: row[-1])

_col_names = ["adduct_name", "m_multiplier", "adduct_add", "adduct_sub", "z"]


def _create_adducts_table(adducts):
    from emzed.table import Table

    t = Table.create_table(_col_names, [str, int, str, str, int], rows=adducts)
    t.set_title("adducts table")
    t.add_column("sign_z", (t.z > 0).then_else(1, -1), int)
    t.replace_column("z", t.apply(abs, t.z), int)
    t.add_enumeration()
    return t


def _check_adduct_table(t):
    required = set(["id", "sign_z"] + _col_names)
    if set(t.col_names) != required:
        raise ValueError(
            f"adducts table must have column names {', '.join(sorted(required))}"
        )


all = _create_adducts_table(_default_adducts)


def _adducts_for_z(*zs):
    return all.filter((all.z * all.sign_z).is_in(zs), keep_view=True)


positive = _adducts_for_z(+1, +2, +3, +4, +5)
negative = _adducts_for_z(-1, -2, -3, -4, -5)
neutral = _adducts_for_z(0)
single_charged = _adducts_for_z(+1, -1)
double_charged = _adducts_for_z(+2, -2)
triple_charged = _adducts_for_z(+3, -3)
positive_single_charged = _adducts_for_z(+1)
positive_double_charged = _adducts_for_z(+2)
positive_triple_charged = _adducts_for_z(+3)
negative_single_charged = _adducts_for_z(-1)
negative_double_charged = _adducts_for_z(-2)
negative_triple_charged = _adducts_for_z(-3)


def _valid_python_identifier(adduct_mf):
    name = adduct_mf.replace("+", "_plus_").replace("-", "_minus_").rstrip("_")
    if name.startswith("2"):
        return "Two_" + name[1:]
    if name.startswith("3"):
        return "Three_" + name[1:]
    return name


for _name, *a in _default_adducts:
    # _t = _create_adducts_table([(_name, *a)])
    _t = all.filter(all.adduct_name == _name, keep_view=True)
    locals()[_valid_python_identifier(_name)] = _t
