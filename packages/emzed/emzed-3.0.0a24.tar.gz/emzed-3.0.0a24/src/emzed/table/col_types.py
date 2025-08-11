# This file is part of emzed (https://emzed.ethz.ch), a software toolbox for analysing
# LCMS data with Python.
#
# Copyright (C) 2020 ETH Zurich, SIS ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.

from collections import defaultdict
from functools import partial

from emzed.ms_data import MSChromatogram, PeakMap


class RtType(float):
    pass


class MzType(float):
    pass


NUMERICAL_TYPES = (int, float, bool, MzType, RtType)
BASE_TYPES = NUMERICAL_TYPES + (str,)


def check_col_type(type_):
    # avoid circular import:
    from emzed import Table

    if type_ not in BASE_TYPES + (PeakMap, Table, MSChromatogram, object):
        types_txt = ", ".join(
            t.__qualname__
            for t in BASE_TYPES + (PeakMap, Table, MSChromatogram, object)
        )
        message = (
            f"type {type_} is not supported. supported colum types are {types_txt}. In"
            " case you want to use Python objects like lists or dicts, use column type"
            " 'object' instead."
        )
        raise TypeError(message)


def rt_formatter(v):
    if v is None:
        return "-"
    return "{:6.2f} m".format(v / 60)


def bool_formatter(v):
    if v is None:
        return "-"
    return str(bool(v))


def _format(what, fmt_str):
    if what is None:
        return "-"
    return fmt_str % (what,)


def formatter_from_format_str(fmt_str):
    return partial(_format, fmt_str=fmt_str)


DEFAULT_FORMATS = {
    int: "%d",
    float: "%f",
    bool: bool_formatter,
    str: "%s",
    RtType: rt_formatter,
    MzType: "%11.6f",
    PeakMap: None,  # invisible
}


DEFAULT_DB_TYPES = defaultdict(lambda: "BLOB")
DEFAULT_DB_TYPES.update(
    {
        int: "INTEGER",
        float: "REAL",
        bool: "BOOLEAN",
        str: "TEXT",
        MzType: "REAL",
        RtType: "REAL",
    }
)


TEST_VALUES = {
    int: 123,
    float: 123.456,
    bool: True,
    str: "Text",
    MzType: 801.123_456,
    RtType: 23.45,
}


def can_convert(from_, to):
    ok = set(
        [
            (int, float),
            (int, str),
            (float, str),
            (bool, int),
            (bool, float),
            (bool, str),
            (RtType, float),
            (float, RtType),
            (MzType, float),
            (float, MzType),
        ]
    )
    return (from_, to) in ok


def to_pandas_type(t):
    from emzed import Table

    return {
        int: "Int64",  # supports NAN
        str: "string",
        bool: "bool",
        float: float,
        RtType: float,
        MzType: float,
        PeakMap: object,
        MSChromatogram: object,
        Table: object,
    }.get(t, object)
