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


class FilterModel(ViewModel):
    def __init__(self, expression, parent_model):
        self.expression = expression
        uid_expression = create_uid()

        sql_filter = expression._to_sql_expression()

        tables = expression._accessors_involved()
        assert len(tables) < 2, "invalid filter expression with multiple tables"

        parent_accessors = set()

        # TODO: easier way to achieve this ?
        model = parent_model  # we need parent_model later
        while model is not None:
            parent_accessors.add(model._access_name)
            model = model.parent_model

        if tables:
            assert parent_accessors.intersection(
                tables
            ), "invalid filter expression with foreign table involved"

            # tables has one element only
            table = tables.pop()
            sql_filter = sql_filter.replace(table + ".", "T.")

        access_name = f"{parent_model._access_name}_filter_{uid_expression}"
        super().__init__(parent_model, access_name)

        columns = ", ".join(self.col_name_mapping.values())
        stmt = f"""CREATE VIEW IF NOT EXISTS '{self._access_name}' AS
                       SELECT _index, {columns} FROM '{parent_model._access_name}' as T
                       WHERE {sql_filter};
                """
        self._drop_statements.append(f"DROP VIEW IF EXISTS '{self._access_name}'")
        self._conn.execute(stmt)
        self._conn.commit()
