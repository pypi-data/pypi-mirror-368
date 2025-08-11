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


import itertools
import re
import shutil
import string
import warnings

import pyopenms

from emzed.core import ImmutableDbBackedDictionary
from emzed.ms_data import PeakMap
from emzed.utils.sqlite import copy_tables

from .col_types import (
    DEFAULT_DB_TYPES,
    DEFAULT_FORMATS,
    TEST_VALUES,
    MzType,
    RtType,
    formatter_from_format_str,
)

with warnings.catch_warnings():
    warnings.filterwarnings("ignore")
    import pandas as pd


def table_to_html(t):
    col_formats = t._model.col_formats
    col_types = t._model.col_types
    col_names = t._model.col_names

    if len(t) > 60:
        rows = list(t[:30]) + list(t[30:])
    else:
        rows = list(t)

    visible = set(
        i for i, col_format in enumerate(col_formats) if col_format is not None
    )

    def filter_(values):
        return [v for i, v in enumerate(values) if i in visible]

    names = filter_(col_names)

    no_visible_columns = len(names) == 0

    if no_visible_columns:
        return ""

    types = [type_to_str(tt) for tt in filter_(col_types)]

    columns = pd.MultiIndex.from_tuples(zip(names, types))

    formatters = [t._model._col_formatters[name] for name in names]

    def format_row(row):
        row = filter_(row[1:])
        return [f(c).replace(" ", "&nbsp;") for f, c in zip(formatters, row)]

    df = pd.DataFrame(columns=columns)
    for i, row in enumerate(rows):
        df.loc[i] = format_row(row)

    return (
        df.style.set_table_styles(
            [
                {
                    "selector": "td",
                    "props": [
                        ("white-space", "pre"),
                        ("font-family", "monospace"),
                    ],
                },
                {
                    "selector": "th",
                    "props": [
                        ("white-space", "pre"),
                        ("font-family", "monospace"),
                    ],
                },
            ]
        )
        .hide()  # hides index
        ._repr_html_()
    )


def print_table(t, max_rows, max_col_width, stream):
    col_formats = t._model.col_formats
    col_types = t._model.col_types
    col_names = t._model.col_names

    visible = set(
        i for i, col_format in enumerate(col_formats) if col_format is not None
    )

    def filter_(values):
        return [v for i, v in enumerate(values) if i in visible]

    names = filter_(col_names)

    no_visible_columns = len(names) == 0

    if no_visible_columns:
        return

    types = [type_to_str(tt) for tt in filter_(col_types)]

    formatters = [t._model._col_formatters[name] for name in names]

    rows = [names, types]
    num_header_lines = len(rows)

    def format_row(row):
        assert not isinstance(row, (list, tuple))  # must be Row
        row = filter_(row[1:])  # skip _index
        return [f(c) for f, c in zip(formatters, row)]

    # build content
    n = t._model.count()
    if max_rows is None or n < max_rows:
        for row in t:
            rows.append(format_row(row))
    else:
        # invariant: head + 1 + tail == max_rows
        head = (max_rows - 1) // 2
        tail = max_rows - 1 - head

        for i in range(head):
            row = t._model.get_row(i)
            rows.append(format_row(row))

        rows.append(["..."] * len(t._model.col_names))

        for i in range(tail, 0, -1):
            row = t._model.get_row(-i)
            rows.append(format_row(row))

    n = len(names)

    # determine column widths
    col_widths = []
    for col_index in range(n):
        col_width = max(len(row[col_index]) for row in rows)
        if max_col_width is not None:
            col_width = min(max_col_width, col_width)
        col_widths.append(col_width)

    if max_col_width is None and len(t) > 0:
        minw = [max(len(row[i]) for row in rows[:num_header_lines]) for i in range(n)]
        for i, f in enumerate(formatters):
            width = 0
            try:
                width = len(f(0))
            except ValueError:
                try:
                    width = len(f(""))
                except ValueError:
                    pass
            minw[i] = max(minw[i], width)
        col_widths = _layout(minw, col_widths, col_types)

    # now we can compute separator line:
    rows.insert(num_header_lines, ["-" * col_width for col_width in col_widths])
    data_rows_start_at = num_header_lines + 1

    for row_index, row in enumerate(rows):
        for i, cell, width, type_ in zip(itertools.count(), row, col_widths, col_types):
            if len(cell) > width:
                cell = cell[: width - 3] + "..."
            elif row_index >= data_rows_start_at and type_ in (
                int,
                float,
                RtType,
                MzType,
            ):
                cell = " " * (width - len(cell)) + cell
            else:
                cell = cell + " " * (width - len(cell))
            print(cell, end="", file=stream)
            if i < n - 1:
                # intermediate space
                print("  ", end="", file=stream)
        print(file=stream)


def is_int(text):
    return all(c in string.digits for c in text)


def type_to_str(t):
    match = re.match("<class '(.*)'>", str(t))
    if match is not None:
        return match.groups()[0].rsplit(".", 1)[-1]
    return str(t)


def guess_col_format(col_name, col_type):
    if col_type is float:
        if col_name.startswith("mz"):
            return DEFAULT_FORMATS[MzType]
        if col_name.startswith("rt"):
            return DEFAULT_FORMATS[RtType]
    return DEFAULT_FORMATS.get(col_type, "%r")


def guess_col_formats(col_names, col_types):
    return [guess_col_format(n, t) for (n, t) in zip(col_names, col_types)]


def best_convert(value, dash_is_none):
    if dash_is_none and isinstance(value, str) and value.strip() == "-":
        return None

    if value == "True":
        return True

    if value == "False":
        return False

    for type_ in (int, float):
        try:
            return type_(value)
        except ValueError:
            continue
    return value


def guess_common_type(col_name, values):
    types = set(type(v) for v in values if v is not None)
    if object in types:
        return object
    if str in types:
        return str
    if float in types:
        if col_name.startswith("mz"):
            return MzType
        if col_name.startswith("rt"):
            return RtType
        return float
    if int in types:
        if col_name.startswith("mz"):
            return MzType
        if col_name.startswith("rt"):
            return RtType
        return int

    if bool in types:
        return bool

    return object


def setup_col_formatters(col_names, col_types, col_formats):
    formatters = {}
    for col_name, col_type, col_format in zip(col_names, col_types, col_formats):
        if col_format is None:
            formatters[col_name] = None
            continue

        elif isinstance(col_format, str):
            formatter = formatter_from_format_str(col_format)
        else:
            formatter = col_format

        test_value = TEST_VALUES.get(col_type, None)
        try:
            formatted = formatter(test_value)
        except:  # noqa: E722
            raise ValueError(
                "column format '{}' for column '{}' is not suitable "
                "for datatype {!r}".format(col_format, col_name, col_type)
            )

        if not isinstance(formatted, str) and formatted is not None:
            raise ValueError(
                "column format '{}' for column '{}' does not return a string or "
                "None for datatype {!r}".format(col_format, col_name, col_type)
            )

        try:
            formatter(None)
        except TypeError:
            raise ValueError(
                "column format '{}' for column '{}' can not handle None values".format(
                    col_format, col_name
                )
            )
        formatters[col_name] = formatter
    return formatters


def list_peakmap_tables(conn):
    rows = conn.execute(
        "SELECT name, sql FROM sqlite_master WHERE"
        " type='table' AND name LIKE 'peakmap_%';"
    )
    return [row[:2] for row in rows]


def list_data_tables(conn):
    rows = conn.execute(
        "SELECT name, sql FROM sqlite_master WHERE"
        " type='table' AND name LIKE 'data_%';"
    )
    return [row[:2] for row in rows]


def _get_references(model, db_col_name, col_type):
    rows = model._conn.execute(
        f"SELECT DISTINCT {db_col_name} FROM {model._access_name}"
    )
    references = set(row[0] for row in rows if row[0] is not None)

    if col_type is PeakMap:
        return references

    for reference in references.copy():
        info = ImmutableDbBackedDictionary(model._conn, f"data_{reference}", "info")
        for i, type_ in enumerate(info["col_types"]):
            if type_ is PeakMap:
                db_col_name = info["col_name_mapping"][info["col_names"][i]]
                rows = model._conn.execute(
                    f"SELECT DISTINCT {db_col_name} FROM data_{reference}"
                )
                references.update(row[0] for row in rows if row[0] is not None)

    return references


def get_references(model):
    from .table import Table

    references = set()
    for col_name, col_type in zip(model.col_names, model.col_types):
        db_col_name = model.col_name_mapping[col_name]
        if col_type in (PeakMap, Table):
            references.update(_get_references(model, db_col_name, col_type))
    return references


def copy_all_refered_tables(source_model, target_conn):
    references = get_references(source_model)

    table_names = [
        t
        for (t, s) in list_data_tables(source_model._conn)
        + list_peakmap_tables(source_model._conn)
        if t.split("_")[1] in references
    ]

    copy_tables(source_model._conn, target_conn, table_names, table_names)


def _layout(minw, col_widths, col_types):
    nc = len(minw)

    tw, _ = shutil.get_terminal_size(fallback=(None, None))
    if tw is None:
        # can not retieve terminal size, e.g. when used in pipe or with redirection
        return col_widths

    # we print 2 spaces between each column and a "\n" at the end:
    tw -= 2 * (nc - 1) + 1

    if sum(col_widths) < tw:
        # fits on sreen anyway
        return col_widths

    # i0: indices of colums we don't want to shrink: either we would loose information
    # for numbers of the colum width is alrady <= 10
    i0 = set(
        i
        for i, cw in enumerate(col_widths)
        if cw <= minw[i] or col_types[i] in (int, float) or cw <= 10
    )

    # these are the columns we want to shrink
    i1 = set(i for i in range(nc) if i not in i0)
    if not i1:
        return col_widths

    # we cut colwidths to reduce influence outlier on final layout:
    col_widths = [min(cw, 50) for cw in col_widths]

    # compute shrink factors delta[i] for column widths cw[i] so that:
    #
    #     sum_i0 cw[i] + sum_i1 (cw[i] * delta[i]) == tw
    #
    # shrinfactors should affect broader columns more than the narrower columns.
    #
    # one might think first about the following ansatz
    #
    #     delta_i = delta_0 / cw[i]
    #
    # which, after doing the math, results in setting all columns in i1 to a constant
    # length which shortens very broad columns too much.
    #
    # the following ansatz:
    #
    #     delta_i = delta_0 / sqrt(cw[i])
    #
    # leads to good looking results based on some experiments.
    #
    # solving the equations leads to the following formula:

    delta_0 = (tw - sum(col_widths[i] for i in i0)) / sum(
        (1 + col_widths[i]) ** 0.5 for i in i1
    )

    # we fix now the column widths but consider the lower bunds vorm minw[i] to ensure
    # that the header lines are printed without truncation.  this might result in output
    # extending the available space:
    col_widths = col_widths[:]
    for i in i1:
        delta_i = col_widths[i] ** -0.5 * delta_0
        newlen = int(col_widths[i] * delta_i)
        newlen = max(newlen, minw[i])
        col_widths[i] = newlen

    # because of rounding down when computing newlen we might have shortened columns too
    # much, thus we increase widths from the right:
    for k in range(nc - 1, -1, -1):
        if sum(col_widths) == tw:
            break
        col_widths[k] += 1
    return col_widths


def to_openms_feature_map(table):
    """
    converts table to pyopenms FeatureMap type.
    """

    data_columns = ("feature_id", "rt", "mz", "intensity")
    table._ensure_col_names(*data_columns)

    fm = pyopenms.FeatureMap()

    seen_feature_ids = set()

    cols = ", ".join(table._model.col_name_mapping[n] for n in data_columns)
    access_name = table._model._access_name

    f = pyopenms.Feature()
    for row in table._model._conn.execute(f"SELECT {cols} FROM {access_name}"):
        feature_id, rt, mz, intensity = row

        if rt is None or mz is None:
            continue

        if feature_id in seen_feature_ids:
            continue
        seen_feature_ids.add(feature_id)

        f.setMZ(mz)
        f.setRT(rt)
        f.setIntensity(intensity if intensity is not None else 1000.0)
        fm.push_back(f)

    return fm


def create_db_table(conn, access_name, col_names, col_types):
    db_col_names = ["col_%d" % i for i in range(len(col_names))]

    col_name_mapping = {
        col_name: db_col_name
        for (col_name, db_col_name) in zip(col_names, db_col_names)
    }

    decls = ["_index INTEGER PRIMARY KEY AUTOINCREMENT"]
    decls.extend(
        "{} {}".format(name, DEFAULT_DB_TYPES[type_])
        for (name, type_) in zip(db_col_names, col_types)
    )

    decl = ", ".join(decls)
    conn.execute(f"CREATE TABLE {access_name} ({decl});")
    conn.commit()

    return col_name_mapping


def cleanup_references(model, col_name, type_):
    from emzed import PeakMap, Table

    if type_ not in (Table, PeakMap):
        return

    unique_ids_in_use = set(
        (
            t[0]
            for t in model._conn.execute(
                f"""SELECT {col_name} FROM {model._access_name}"""
            ).fetchall()
        )
    )

    type_._remove_unused_references(model, unique_ids_in_use)
