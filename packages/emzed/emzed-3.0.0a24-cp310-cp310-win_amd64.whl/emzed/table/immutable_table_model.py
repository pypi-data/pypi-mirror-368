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


from ..core import ImmutableDbBackedDictionary
from .base_models import BaseModel


class ImmutableTableModel(BaseModel):
    def __init__(
        self,
        conn,
        access_name,
        col_names,
        col_types,
        col_formats,
        title,
        col_name_mapping,
        version,
    ):
        super().__init__(
            None,
            conn,
            access_name,
            col_names,
            col_types,
            col_formats,
            title,
            col_name_mapping,
            version,
        )
        self._views = []

    def _setup_impl_specific_details(self):
        self._info = ImmutableDbBackedDictionary(
            self._conn, self._access_name, suffix="info"
        )

    @staticmethod
    def from_db_tables(conn, access_name):
        dd = ImmutableDbBackedDictionary(conn, access_name, "info")
        (col_names, col_types, col_formats, col_name_mapping, title, version) = (
            dd.get(k)
            for k in [
                "col_names",
                "col_types",
                "col_formats",
                "col_name_mapping",
                "title",
                "__version__",
            ]
        )

        if version is None:
            version = (0, 0, 41)

        return ImmutableTableModel(
            conn,
            access_name,
            col_names,
            col_types,
            col_formats,
            title,
            col_name_mapping,
            version,
        )

    def set_col_format(self, col_name, format_):
        raise TypeError(
            "you try to change a column format on a view. you must consolidate first."
        )

    def set_col_type(self, col_name, type_, *, keep_format=False):
        raise TypeError(
            "you try to change a column type on a view. you must consolidate first."
        )

    def rename_columns(self, from_to):
        raise TypeError(
            "you try to rename column names of a view. you must consolidate first."
        )

    def _reset_unique_id(self):
        raise RuntimeError("should never happen on an immutable table model")

    def register_view(self, view):
        self._views.append(view)
