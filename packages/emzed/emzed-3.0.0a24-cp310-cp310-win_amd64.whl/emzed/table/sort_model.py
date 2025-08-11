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


class SortModel(ViewModel):
    def __init__(self, col_names, ascending, parent_model):
        uid_expression = create_uid()
        access_name = f"{parent_model._access_name}_sorted_{uid_expression}"
        super().__init__(parent_model, access_name)

        sort_columns = [self.col_name_mapping[col_name] for col_name in col_names]

        sort_expression = ", ".join(
            "{col_name} {order}".format(
                col_name=col_name, order="ASC" if ascending else "DESC"
            )
            for (col_name, ascending) in zip(sort_columns, ascending)
        )

        columns = ", ".join(self.col_name_mapping.values())
        stmt = f"""CREATE VIEW IF NOT EXISTS '{self._access_name}' AS
                       SELECT _index, {columns} FROM '{parent_model._access_name}' as T
                       ORDER BY {sort_expression};
                """
        self._drop_statements.append(f"DROP VIEW IF EXISTS '{self._access_name}'")
        self._conn.execute(stmt)
        self._conn.commit()
