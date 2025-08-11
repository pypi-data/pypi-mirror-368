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


def delete_rows(model, indices):
    access_name = model._access_name
    conn = model._conn

    # single deletes don't perform better even if len(indices) < 100

    aux_table = f"indices_{access_name}"
    stmt = f"CREATE TABLE IF NOT EXISTS '{aux_table}'(__index INTEGER);"
    conn.execute(stmt)
    stmt = f"DELETE FROM '{aux_table}'"
    conn.execute(stmt)
    stmt = f"INSERT INTO '{aux_table}'(__index) VALUES(?);"
    conn.executemany(stmt, ((i,) for i in indices))

    conn.execute(
        f"DELETE FROM {access_name} WHERE _index IN (SELECT __index FROM {aux_table})"
    )
    conn.commit()

    model._drop_statements.append(f"DROP TABLE IF EXISTS '{aux_table}'")
