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
import warnings
import weakref
from collections import defaultdict

import numpy as np

from emzed.core import ImmutableDbBackedDictionary
from emzed.utils.sqlite import create_uid

from .add_column import (
    add_column_from_expression,
    add_column_with_constant_value,
    add_column_with_values,
)
from .base_models import BaseModel
from .delete_rows import delete_rows
from .expressions import Expression
from .load_into_from import load_into_from
from .replace_column import (
    replace_column_from_expression,
    replace_column_with_constant_value,
    replace_column_with_values,
)
from .table_utils import cleanup_references

_ref_counts = defaultdict(int)


def _finalize(conn, drop_statements):
    if conn.is_closed():
        return
    _ref_counts[conn.uri] -= 1
    if _ref_counts[conn.uri] > 0:
        return
    try:
        conn.commit()
        for stmt in drop_statements:
            conn.execute(stmt)
        conn.close()
    except sqlite3.OperationalError as e:
        warnings.warn(str(e))
    except sqlite3.DatabaseError as e:
        if "Cannot operate on a closed database." not in str(e):
            raise


class FullTableModel(BaseModel):
    def __init__(
        self,
        conn,
        access_name,
        col_names,
        col_types,
        col_formats,
        title,
        col_name_mapping,
        version=None,
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

        # sometimes models share connections, so:
        _ref_counts[conn.uri] += 1

        self._max_index = None
        self._count = None
        self._views = []
        # better than using __del__:
        weakref.finalize(self, _finalize, self._conn, self._drop_statements)

    def invalidate_views(self):
        for view in self._views:
            view.invalidate()
        self._views = []

    def register_view(self, view):
        self._views.append(view)

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

        return FullTableModel(
            conn,
            access_name,
            col_names,
            col_types,
            col_formats,
            title,
            col_name_mapping,
            version,
        )

    def _next_db_col_name(self):
        max_id = max(int(name.split("_")[1]) for name in self.col_name_mapping.values())
        return f"col_{max_id + 1}"

    def _add_column_with_checks_and_updates(
        self, name, what, type_, format_, insert_after, insert_before, action
    ):
        def check():
            assert isinstance(name, str)
            assert (
                name not in self.col_names
            ), "column with name {!r} already exists".format(name)

        def updates():
            if insert_after is not None and insert_after != self.col_names[-1]:
                index = self.col_names.index(insert_after)
                self.col_names.insert(index + 1, name)
                self.col_types.insert(index + 1, type_)
                self.col_formats.insert(index + 1, format_)
            elif insert_before is not None:
                index = self.col_names.index(insert_before)
                self.col_names.insert(index, name)
                self.col_types.insert(index, type_)
                self.col_formats.insert(index, format_)
            else:
                self.col_names.append(name)
                self.col_types.append(type_)
                self.col_formats.append(format_)

            self.col_name_mapping[name] = next_col_name
            self.update_col_formatters()
            self.save_info()
            self.content_changed()

        check()
        next_col_name = self._next_db_col_name()
        self.invalidate_views()
        action(next_col_name)
        updates()

    def drop_columns(self, col_names):
        col_names_to_drop = set(col_names)

        db_col_names_to_keep = ", ".join(
            self.col_name_mapping[name]
            for name in self.col_names
            if name not in col_names_to_drop
        )

        self.invalidate_views()
        _access_name = self._access_name
        try:
            self._conn.execute(
                f"""
                CREATE TABLE _temp AS SELECT _index, {db_col_names_to_keep}
                                    FROM {_access_name};
                """
            )
            self._conn.execute(f"DROP TABLE {_access_name};")
            self._conn.execute(f"ALTER TABLE _temp RENAME TO {_access_name};")
            self._conn.commit()
        finally:
            self._conn.execute("DROP TABLE IF EXISTS _temp;")
            self._conn.commit()

        remaining_col_names = []
        remaining_col_types = []
        remaining_col_formats = []

        for col_name, col_type, col_format in zip(
            self.col_names, self.col_types, self.col_formats
        ):
            if col_name in col_names_to_drop:
                del self.col_name_mapping[col_name]
                continue
            remaining_col_names.append(col_name)
            remaining_col_types.append(col_type)
            remaining_col_formats.append(col_format)

        self.col_names = remaining_col_names
        self.col_types = remaining_col_types
        self.col_formats = remaining_col_formats

        self._run_garbage_collector()
        self.update_col_formatters()
        self.save_info()
        self.content_changed()

    def add_column(self, name, what, type_, format_, insert_after, insert_before):
        def action(next_col_name):
            if isinstance(what, Expression):
                add_column_from_expression(self, next_col_name, what, type_, format_)

            else:
                values = to_list(what)
                if values is None:
                    raise ValueError(f"can not convert type {type(what)} to list")
                if len(values) != len(self):
                    raise ValueError(
                        "length {} of column does not match length of"
                        " table ({})".format(len(values), len(self))
                    )
                # local import to avoid circular import
                from .prepare_table_cell_content import prepare_table_cell_content

                values = [prepare_table_cell_content(self, v, type_) for v in values]
                add_column_with_values(self, next_col_name, values, type_, format_)

        self._add_column_with_checks_and_updates(
            name, what, type_, format_, insert_after, insert_before, action
        )

    def add_column_with_constant_value(
        self, name, value, type_, format_, insert_after, insert_before
    ):
        # local import to avoid circular import
        from .prepare_table_cell_content import prepare_table_cell_content

        value = prepare_table_cell_content(self, value, type_)

        def action(next_col_name):
            add_column_with_constant_value(self, next_col_name, value, type_, format_)

        self._add_column_with_checks_and_updates(
            name, value, type_, format_, insert_after, insert_before, action
        )

    def replace_column_with_constant_value(self, name, value, type_, format_):
        type_changed = self.col_types[self.col_names.index(name)] != type_
        # local import to avoid circular import
        from .prepare_table_cell_content import prepare_table_cell_content

        value = prepare_table_cell_content(self, value, type_)

        self.invalidate_views()
        replace_column_with_constant_value(
            self, name, value, type_, format_, type_changed
        )

        index = self.col_names.index(name)
        self.col_types[index] = type_
        self.col_formats[index] = format_

        cleanup_references(self, self.col_name_mapping[name], type_)

        self.update_col_formatters()
        self.save_info()
        self.content_changed()

    def replace_column(self, name, what, type_, format_):
        type_changed = self.col_types[self.col_names.index(name)] != type_

        self.invalidate_views()
        if isinstance(what, Expression):
            replace_column_from_expression(
                self, name, what, type_, format_, type_changed
            )

        else:
            # local import to avoid circular import
            from .prepare_table_cell_content import prepare_table_cell_content

            values = to_list(what)
            if values is None:
                raise ValueError(f"can not convert type {type(what)} to list")
            if len(values) != len(self):
                raise ValueError(
                    "length {} of column does not match length of" " table ({})".format(
                        len(values), len(self)
                    )
                )
            values = [prepare_table_cell_content(self, v, type_) for v in values]
            replace_column_with_values(self, name, values, type_, format_, type_changed)

        index = self.col_names.index(name)
        self.col_types[index] = type_
        self.col_formats[index] = format_
        cleanup_references(self, self.col_name_mapping[name], type_)
        self.update_col_formatters()
        self.save_info()
        self.content_changed()

    def add_row(self, row):
        self.append([row])
        self.size_changed()

    def delete_rows(self, row_indices):
        indices = [self.indices[row_index] for row_index in row_indices]
        delete_rows(self, indices)
        self._run_garbage_collector()
        self.size_changed()

    def _run_garbage_collector(self):
        from emzed import PeakMap, Table

        unique_ids_in_use = set()
        for name, type_ in zip(self.col_names, self.col_types):
            if type_ not in (PeakMap, Table):
                continue
            col_name = self.col_name_mapping[name]
            unique_ids_in_use.update(
                (
                    t[0]
                    for t in self._conn.execute(
                        f"""SELECT {col_name} FROM {self._access_name}"""
                    ).fetchall()
                )
            )

        PeakMap._remove_unused_references(self, unique_ids_in_use)
        Table._remove_unused_references(self, unique_ids_in_use)

    def append(self, rows):
        if not rows:
            return
        n_col = len(self.col_names)

        # local import to avoid circular import
        from .prepare_table_cell_content import prepare_table_cell_content

        rows = [
            [
                prepare_table_cell_content(self, cell, t)
                for cell, t in zip(row, self.col_types)
            ]
            for row in rows
        ]

        quotation_marks = ", ".join("?" * n_col)
        columns = ", ".join(self.col_name_mapping[n] for n in self.col_names)
        if self.count() == 0:
            # enforce to start with _index 1:
            stmt = (
                f"INSERT INTO {self._access_name} (_index, {columns}) "
                f"VALUES (1, {quotation_marks})"
            )
            self._conn.execute(stmt, rows[0])
            self._count = 1
            rows = rows[1:]
            if not rows:
                self._conn.commit()
                return
        stmt = f"INSERT INTO {self._access_name} ({columns}) VALUES ({quotation_marks})"
        self._conn.executemany(stmt, rows)
        self._conn.commit()
        self._count += len(rows)
        self.content_changed()

    def load_from(self, other):
        load_into_from(self, other)
        self.size_changed()

    def size_changed(self):
        self._indices = None
        self._count = None
        self.content_changed()

    def set_values(self, row_indices, col_index, values):
        from .prepare_table_cell_content import prepare_table_cell_content

        col_type = self.col_types[col_index]
        col_name = self.col_name_mapping[self.col_names[col_index]]

        self._conn.execute("BEGIN TRANSACTION")
        for row_index, value in zip(row_indices, values):
            value = prepare_table_cell_content(self, value, col_type)
            self._conn.execute(
                f"UPDATE {self._access_name} SET {col_name} = ? WHERE _index = ?",
                (value, self.indices[row_index]),
            )

        self._conn.execute("END TRANSACTION")
        self._conn.commit()
        self._run_garbage_collector()
        self.content_changed()
        return value

    def set_value(self, row_indices, col_index, value):
        from .prepare_table_cell_content import prepare_table_cell_content

        col_type = self.col_types[col_index]
        col_name = self.col_name_mapping[self.col_names[col_index]]
        value = prepare_table_cell_content(self, value, col_type)

        N = 1000

        self._conn.execute("BEGIN TRANSACTION")
        for i in range(0, len(row_indices), N):
            chunk = [self.indices[ri] for ri in row_indices[i : i + N]]
            placeholders = ", ".join("?" * len(chunk))
            stmt = (
                f"UPDATE {self._access_name} SET {col_name} = ? "
                "WHERE _index IN (%s)" % placeholders
            )
            self._conn.execute(stmt, (value, *chunk))
        self._conn.execute("END TRANSACTION")

        self._conn.commit()
        self._run_garbage_collector()
        self.content_changed()
        return value

    def content_changed(self):
        self._unique_id = None
        self.invalidate_views()

    def create_index(self, *col_names):
        columns = [self.col_name_mapping[name] for name in col_names]
        name = "_".join(columns)
        index_name = f"_index_{name}_{create_uid()}"

        cols = ", ".join(columns)
        self._conn.execute(f"CREATE INDEX {index_name} ON {self._access_name} ({cols})")
        return index_name

    def drop_index(self, index_name):
        self._conn.execute(f"DROP INDEX {index_name}")


def to_list(values):
    if not isinstance(values, (list, tuple, np.ndarray)):
        return None
    if isinstance(values, np.ndarray):
        assert values.ndim == 1
        return values.tolist()
    return list(values)
