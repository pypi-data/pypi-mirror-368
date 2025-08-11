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

from .col_types import DEFAULT_DB_TYPES


def replace_column_with_values(model, name, values, type_, format_, type_changed):
    db_type = DEFAULT_DB_TYPES[type_]
    conn = model._conn
    _access_name = model._access_name

    indices = conn.execute(f"SELECT _index FROM {_access_name}").fetchall()

    # setup table _temp with one column holding values
    try:
        conn.execute("BEGIN TRANSACTION")
        conn.execute(
            f"CREATE TABLE _temp (_index INTEGER PRIMARY KEY, {name} {db_type});"
        )
        conn.executemany(
            "INSERT INTO _temp VALUES (?, ?);",
            ((i[0], v) for i, v in zip(indices, values)),
        )

        # create new table _temp2
        columns = [model.col_name_mapping[n] for n in model.col_names]
        col_names = ", ".join(columns)

        index = model.col_names.index(name)
        col_types = model.col_types[:]
        col_types[index] = type_

        decls = ["_index INTEGER PRIMARY KEY AUTOINCREMENT"]
        decls.extend(
            "{} {}".format(name, DEFAULT_DB_TYPES[type_])
            for (name, type_) in zip(columns, col_types)
        )

        decl = ", ".join(decls)
        conn.execute(f"CREATE TABLE _temp2 ({decl});")

        # copy modified data into _temp2
        columns[index] = f"_temp.{name} AS {columns[index]}"
        columns.insert(0, f"{_access_name}._index")

        col_names = ", ".join(columns)

        conn.execute(
            f"""
            INSERT INTO _temp2
            SELECT {col_names} FROM {_access_name}
                            JOIN _temp ON {_access_name}._index = _temp._index;
            """
        )
        conn.execute("END TRANSACTION;")
        conn.execute("BEGIN TRANSACTION;")
        conn.execute(f"DROP TABLE {_access_name};")
        conn.execute(f"ALTER TABLE _temp2 RENAME TO {_access_name};")
        conn.execute("DROP TABLE _temp;")
        conn.commit()
    finally:
        # cleanup in case of failure
        conn.execute("DROP TABLE IF EXISTS _temp;")
        conn.execute("DROP TABLE IF EXISTS _temp2;")
        conn.commit()


def replace_column_with_constant_value(
    model, name, value, type_, format_, type_changed
):
    if isinstance(value, bytes):
        value = sqlite3.Binary(value)

    return _replace_column_using_single_value_update(
        model, name, value, type_, format_, type_changed
    )


def replace_column_from_expression(
    model, name, expression, type_, format_, type_changed
):
    conn = model._conn
    _access_name = model._access_name

    db_col_name = model.col_name_mapping[name]
    value = expression._to_sql_expression()
    db_type = DEFAULT_DB_TYPES[type_]

    if not type_changed:
        conn.execute(
            f"UPDATE {_access_name} SET {db_col_name} = CAST(({value}) AS {db_type});"
        )
        conn.commit()
        return

    # create new table _temp2
    columns = list(model.col_name_mapping.values())
    col_names = ", ".join(columns)

    index = model.col_names.index(name)
    col_types = model.col_types[:]
    col_types[index] = type_

    decls = ["_index INTEGER PRIMARY KEY AUTOINCREMENT"]
    decls.extend(
        "{} {}".format(name, DEFAULT_DB_TYPES[type_])
        for (name, type_) in zip(columns, col_types)
    )

    decl = ", ".join(decls)
    conn.execute(f"CREATE TABLE _temp2 ({decl});")

    # copy modified data into _temp2
    columns = list(model.col_name_mapping.values())
    columns.insert(0, "_index")

    col_names = ", ".join(columns)

    conn.execute(
        f"""
        INSERT INTO _temp2
        SELECT {col_names} FROM {_access_name}
        """
    )

    # remname _temp2 -> _access_name
    conn.execute(f"DROP TABLE {_access_name};")
    conn.execute(f"ALTER TABLE _temp2 RENAME TO {_access_name};")
    conn.execute(
        f"UPDATE {_access_name} SET {db_col_name} = CAST(({value}) AS {db_type});"
    )
    conn.commit()


def _replace_column_using_single_value_update(
    model, name, value, type_, format_, type_changed
):
    conn = model._conn
    _access_name = model._access_name
    db_col_name = model.col_name_mapping[name]

    if not type_changed:
        conn.execute(f"UPDATE {_access_name} SET {db_col_name} = (?);", (value,))
        conn.commit()
        return

    # create new table _temp2
    columns = list(model.col_name_mapping.values())
    col_names = ", ".join(columns)

    index = model.col_names.index(name)
    col_types = model.col_types[:]
    col_types[index] = type_

    decls = ["_index INTEGER PRIMARY KEY AUTOINCREMENT"]
    decls.extend(
        "{} {}".format(name, DEFAULT_DB_TYPES[type_])
        for (name, type_) in zip(columns, col_types)
    )

    decl = ", ".join(decls)
    conn.execute(f"CREATE TABLE _temp2 ({decl});")

    # copy modified data into _temp2
    columns = list(model.col_name_mapping.values())
    columns.insert(0, "_index")

    col_names = ", ".join(columns)

    conn.execute(
        f"""
        INSERT INTO _temp2
        SELECT {col_names} FROM {_access_name}
        """
    )

    # remname _temp2 -> _access_name
    conn.execute(f"DROP TABLE {_access_name};")
    conn.execute(f"ALTER TABLE _temp2 RENAME TO {_access_name};")
    conn.execute(f"UPDATE {_access_name} SET {db_col_name} = (?);", (value,))
    conn.commit()
