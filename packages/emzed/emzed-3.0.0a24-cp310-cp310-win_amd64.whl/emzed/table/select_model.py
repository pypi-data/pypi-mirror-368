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


from ..utils.sqlite import create_uid
from .base_models import ViewModel


class SelectModel(ViewModel):
    def __init__(self, selection, parent_model):
        if isinstance(selection, slice):
            row_indices = parent_model.indices[selection]

            def fix_name(v):
                return str(v) if v is None or v >= 0 else f"minus_{abs(v)}"

            start = fix_name(selection.start)
            stop = fix_name(selection.stop)
            step = fix_name(selection.step)

            access_name = (
                f"{parent_model._access_name}_slice_view_{start}_{stop}_{step}"
            )

        else:
            row_indices = [parent_model.indices[s] for s in selection]
            access_name = f"{parent_model._access_name}_selection_view_{create_uid()}"

        super().__init__(parent_model, access_name)

        # this approach is faster than submitting a sql statement with a huge IN clause
        # and also more robust as we don't rely on internal limits about the maximal
        # size of a statement or IN clause: (tested with up to 1e7 rows)

        aux_table = f"indices_{self._access_name}"
        stmt = f"CREATE TABLE IF NOT EXISTS '{aux_table}'(__index INTEGER);"
        self._conn.execute(stmt)
        stmt = f"DELETE FROM '{aux_table}'"
        self._conn.execute(stmt)
        stmt = f"INSERT INTO '{aux_table}'(__index) VALUES(?);"
        self._conn.executemany(stmt, ((i,) for i in row_indices))

        columns = ", ".join(self.col_name_mapping.values())

        stmt = f"""CREATE VIEW IF NOT EXISTS '{self._access_name}'
                   AS  SELECT _index, {columns}
                       FROM '{parent_model._access_name}'
                       JOIN '{aux_table}'
                       WHERE _index = '{aux_table}'.__index
                       ORDER BY '{aux_table}'.ROWID;
                """

        self._drop_statements.append(f"DROP VIEW IF EXISTS '{self._access_name}'")
        self._drop_statements.append(f"DROP TABLE IF EXISTS '{aux_table}'")

        self._conn.execute(stmt)
        self._conn.commit()
