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


import sqlite3

from emzed.utils.sqlite import create_uid

from .col_types import DEFAULT_DB_TYPES


def add_column_with_values(model, name, values, type_, format_):
    db_type = DEFAULT_DB_TYPES[type_]
    conn = model._conn
    _access_name = model._access_name

    indices = conn.execute(f"SELECT _index FROM {_access_name}").fetchall()
    try:
        conn.execute("BEGIN TRANSACTION;")
        conn.execute(
            f"CREATE TABLE _temp (_index INTEGER PRIMARY KEY, {name} {db_type});"
        )
        conn.executemany(
            "INSERT INTO _temp VALUES (?, ?);",
            ((i[0], v) for i, v in zip(indices, values)),
        )

        columns = [f"{_access_name}._index"]
        columns += [
            f"{_access_name}.{model.col_name_mapping[n]}" for n in model.col_names
        ]
        columns.append(f"_temp.{name}")
        col_names = ", ".join(columns)

        conn.execute(
            f"""
            CREATE TABLE _temp2 AS
                SELECT {col_names}
                FROM {_access_name}
                JOIN _temp ON {_access_name}._index = _temp._index;
            """
        )
        conn.execute("END TRANSACTION;")
        conn.execute("BEGIN TRANSACTION;")
        conn.execute("DROP TABLE _temp;")
        model.invalidate_views()
        conn.execute(f"DROP TABLE {_access_name};")
        conn.execute(f"ALTER TABLE _temp2 RENAME TO {_access_name};")
        conn.commit()
    finally:
        conn.execute("DROP TABLE IF EXISTS _temp;")
        conn.execute("DROP TABLE IF EXISTS _temp2;")
        conn.commit()


def add_column_with_constant_value(model, name, value, type_, format_):
    if isinstance(value, bytes):
        value = sqlite3.Binary(value)

    return _add_column_using_single_value_update(model, name, value, type_, format_)


def add_column_from_expression(model, name, expression, type_, format_):
    db_type, tmp_col = _prepare_update(model, name, type_)
    value = expression._to_sql_expression()
    model._conn.execute(
        f"UPDATE {model._access_name} SET {tmp_col} = CAST(({value}) as {db_type});"
    )
    _finish_update(model, name, db_type, tmp_col)


def _add_column_using_single_value_update(model, name, value, type_, format_):
    db_type, tmp_col = _prepare_update(model, name, type_)
    model._conn.execute(f"UPDATE {model._access_name} SET {tmp_col} = (?)", (value,))
    _finish_update(model, name, db_type, tmp_col)


def _prepare_update(model, name, type_):
    db_type = DEFAULT_DB_TYPES[type_]
    conn = model._conn
    _access_name = model._access_name

    # using a temp colum is a workaround as sqlite3 of Python 3.7 does not wrap latest
    # sqlite3 and thus ALTER TABLE ... RENAME COLUMN ... is not supported regrettably
    # sqlite3 has no proper transcations support which would allow us to roll back in
    # case of exceptions when the expression is evaluted:

    tmp_col = f"_tmp_{create_uid()}"

    try:
        conn.execute(f"ALTER TABLE {_access_name} ADD COLUMN {tmp_col} {db_type};")
    except sqlite3.OperationalError as e:
        if "duplicate column" not in str(e):
            raise

    return db_type, tmp_col


def _finish_update(model, name, db_type, tmp_col):
    conn = model._conn
    conn.commit()
    conn.execute(f"ALTER TABLE {model._access_name} ADD COLUMN {name} {db_type};")
    conn.execute(f"UPDATE {model._access_name} SET {name} = {tmp_col};")
    # we can not delete _tmp_{name} and have to keep it until we consolidate the
    # table!
    conn.commit()
    model.invalidate_views()
