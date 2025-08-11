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


class ExtractColumnsModel(ViewModel):
    def __init__(self, names, parent_model):
        uid_extract = create_uid()

        access_name = f"{parent_model._access_name}_extract_{uid_extract}"
        super().__init__(parent_model, access_name)

        ix_lookup = {n: i for (i, n) in enumerate(self.col_names)}

        self.col_names = list(names)

        self.col_types = [self.col_types[ix_lookup[name]] for name in names]
        self.col_formats = [self.col_formats[ix_lookup[name]] for name in names]

        self.col_name_mapping = {n: self.col_name_mapping[n] for n in names}

        self.update_col_formatters()

        columns = ", ".join(["_index"] + [self.col_name_mapping[n] for n in names])
        stmt = f"""CREATE VIEW IF NOT EXISTS '{self._access_name}' AS
                    SELECT {columns} FROM '{parent_model._access_name}';
                """
        self._drop_statements.append(f"DROP VIEW IF EXISTS '{self._access_name}'")
        self._conn.execute(stmt)
        self._conn.commit()
