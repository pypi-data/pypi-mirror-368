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


def load_into_from(target, source):
    columns = ", ".join(target.col_name_mapping[n] for n in target.col_names)
    source_columns = ", ".join(source.col_name_mapping[n] for n in source.col_names)

    conn = target._conn

    conn.execute(f"ATTACH DATABASE '{source._conn.uri}' AS S;")
    conn.execute(
        f"INSERT INTO {target._access_name} ({columns})"
        f" SELECT {source_columns} FROM S.{source._access_name};"
    )
    conn.commit()
    conn.execute("DETACH DATABASE S;")

    conn.commit()
