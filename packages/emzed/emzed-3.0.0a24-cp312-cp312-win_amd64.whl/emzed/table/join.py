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

from contextlib import nullcontext

from emzed.utils import temp_file_path

from ..utils.sqlite import Connection
from .table_utils import is_int


def join(left_model, right_model, expression, path, ignore_left=()):
    return _join(left_model, right_model, expression, "JOIN", path, ignore_left)


def left_join(left_model, right_model, expression, path, ignore_left=()):
    return _join(left_model, right_model, expression, "LEFT JOIN", path, ignore_left)


def _join(left_model, right_model, expression, join_kind, path, ignore_left):
    if expression is not None:
        models_involved = expression._models_involved
        expressions_only_use_left_and_right_models = models_involved <= set(
            (left_model, right_model)
        )
        if not expressions_only_use_left_and_right_models:
            raise ValueError(
                "your expression contains terms which refer to columns from other"
                " tables"
            )

    conn = Connection(path)

    left_col_names = [name for name in left_model.col_names if name not in ignore_left]
    left_col_types = [
        type_
        for type_, name in zip(left_model.col_types, left_model.col_names)
        if name not in ignore_left
    ]
    left_col_formats = [
        format_
        for format_, name in zip(left_model.col_formats, left_model.col_names)
        if name not in ignore_left
    ]

    right_col_names = right_model.col_names
    right_col_types = right_model.col_types
    right_col_formats = right_model.col_formats

    fixed_names_right_model = fix_names_right(left_col_names, right_col_names)

    col_names = list(left_col_names) + list(fixed_names_right_model)

    col_types = left_col_types + right_col_types
    col_formats = left_col_formats + right_col_formats

    i = -1

    def count():
        nonlocal i
        i += 1
        return i

    conn.create_function("_count", 0, count)

    n = len(left_col_names)

    # we reindex the table col names to become continous in all situations:
    col_name_mapping = {name: f"col_{i}" for (i, name) in enumerate(left_col_names)}

    col_name_mapping.update(
        {name: f"col_{i + n}" for (i, name) in enumerate(fixed_names_right_model)}
    )

    fields_left = [
        f"LD.{left_model.col_name_mapping[name]} as col_{i}"
        for i, name in enumerate(left_col_names)
    ]

    fields_right = [
        f"RD.{right_model.col_name_mapping[name]} as col_{i + n}"
        for i, name in enumerate(right_col_names)
        if name not in ignore_left
    ]

    fields = ", ".join(fields_left + fields_right)

    same_db = right_model._conn.uri == left_model._conn.uri

    stmt = f"ATTACH DATABASE '{left_model._conn.uri}' AS L;"
    conn.execute(stmt)

    left_model._conn.transfer_functions(conn)
    right_model._conn.transfer_functions(conn)

    if same_db:
        R = "L"
    else:
        stmt = f"ATTACH DATABASE '{right_model._conn.uri}' AS R;"
        conn.execute(stmt)
        R = "R"

    if expression is None:
        sql_expression = "1 = 1"
    else:
        sql_expression = expression._to_sql_expression(
            {left_model: "LD", right_model: "RD"}
        )

    stmt = f"""
    CREATE TABLE data
    AS SELECT _count() as _index, {fields}
    FROM L.'{left_model._access_name}' as LD
    {join_kind} {R}.'{right_model._access_name}' as RD
    ON {sql_expression}
    ORDER by LD._index, RD._index;
    """
    conn.execute(stmt)
    conn.commit()

    stmt = "DETACH DATABASE L;"
    conn.execute(stmt)

    if not same_db:
        stmt = "DETACH DATABASE R;"
        conn.execute(stmt)

    conn.commit()

    if left_model.title is None and right_model.title is None:
        merged_title = None
    else:
        merged_title = (left_model.title or "") + "_" + (right_model.title or "")

    return (conn, col_names, col_types, col_formats, merged_title, col_name_mapping)


def fix_names_right(left_model_names, right_model_names):
    """
    join column renaming scheme

    examples:

    col left          cols right       result columns
    a                 b                a          b__0
    a                 a a__0        -> a          a__0  a__1
    a__0              a a__0        -> a__0       a__1  a__2
    a__0 a__1         a a__0        -> a__0 a__1  a__2  a__3


    ix(a) = -1
    ix(a__0) = 0
    ...

    increment right = max(ix(left)) + 2
    """

    def postfix(name):
        if "__" in name:
            field = name.split("__")[1]
            if not is_int(field):
                raise ValueError(f"column name {name} is invalid")
            return int(field)
        return -1

    postfixes_left = [postfix(c) for c in left_model_names]

    increment = max(postfixes_left) + 2

    def increment_postfix(name, increment):
        pf = postfix(name)
        if "__" in name:
            name = name.split("__")[0]
        return name + "__" + str(pf + increment)

    fixed_names_right_model = [
        increment_postfix(col_name, increment) for col_name in right_model_names
    ]

    return fixed_names_right_model


def fast_join(left, right, col_name, col_name_other, atol, rtol, path, extra_condition):
    """runs optimized join for numerical comparisons."""
    return _fast_join(
        left, right, col_name, col_name_other, atol, rtol, join, path, extra_condition
    )


def fast_left_join(
    left, right, col_name, col_name_other, atol, rtol, path, extra_condition
):
    """runs optimized left join for numerical comparisons."""
    return _fast_join(
        left,
        right,
        col_name,
        col_name_other,
        atol,
        rtol,
        left_join,
        path,
        extra_condition,
    )


def _fast_join(
    left,
    right,
    col_name,
    col_name_other,
    atol,
    rtol,
    join_method,
    path,
    extra_condition,
):
    """runs optimized join for numerical comparisons.

    idea: reduce number of potential candidates using binning. the subset might contain
    false positives. thus wev have to  determine matches on the candidate set.

    using bins for matching we also have to consider neighbouring bins due to boundary
    effects. some experiments with sqlite3 gave best performance using three different
    columns and indices.

    the alternative approach to use one column and use +/1 in the joing did not work.
    it appears that sqlite does not use indcies any more when we use computations
    or the same indexed column in "or" comparisons.

    using binning columns and indices on left and right tables did not work and resulted
    in decreased performance.
    """

    if rtol:
        bin_width = atol + rtol * left.get_column(col_name).max().eval()
    else:
        bin_width = atol

    if bin_width == 0:
        with left._create_temp_indices(col_name):
            return join_method(
                left._model,
                right._model,
                left.get_column(col_name) == right.get_column(col_name_other),
                path=path,
            )

    if extra_condition is None:
        extra_condition = True

    if path is not None:
        path_contexts = [temp_file_path(), temp_file_path()]
    else:
        path_contexts = [nullcontext(None), nullcontext(None)]

    with path_contexts[0] as path_left, path_contexts[1] as path_intermediate:
        left_temp = left.consolidate(path=path_left, overwrite=True)

        left_temp.add_column(
            "_bins_0", (left.get_column(col_name) / bin_width).floor(), int
        )
        left_temp.add_column("_bins_1", left_temp._bins_0 + 1, int)
        left_temp.add_column("_bins_2", left_temp._bins_0 - 1, int)

        with left_temp._create_temp_indices("_bins_0", "_bins_1", "_bins_2"):
            result = join_method(
                left_temp._model,
                right._model,
                (
                    (
                        left_temp._bins_0
                        == (right.get_column(col_name_other) / bin_width).floor()
                    )
                    | (
                        left_temp._bins_1
                        == (right.get_column(col_name_other) / bin_width).floor()
                    )
                    | (
                        left_temp._bins_2
                        == (right.get_column(col_name_other) / bin_width).floor()
                    )
                )
                & left_temp.get_column(col_name).approx_equal(
                    right.get_column(col_name_other), atol, rtol
                )
                & extra_condition,
                path=path_intermediate,
                ignore_left=("_bins_0", "_bins_1", "_bins_2"),
            )
            return result
