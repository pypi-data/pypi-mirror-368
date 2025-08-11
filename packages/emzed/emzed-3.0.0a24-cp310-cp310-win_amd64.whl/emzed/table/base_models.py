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


import csv
import os
from contextlib import wraps
from functools import partial

import dill

from ..core import DbBackedDictionary, DbBackedModel
from ..core.hashes import md5_hexdigest
from ..utils.sqlite import Connection, copy_table, create_uid, table_exists, table_hash
from .col_types import DEFAULT_DB_TYPES, DEFAULT_FORMATS, can_convert
from .expressions import column_accessor
from .row_class import create_row_class
from .table_migrations import migrate
from .table_utils import (
    copy_all_refered_tables,
    list_peakmap_tables,
    setup_col_formatters,
)

TABLE_VERSION = (0, 0, 42)


def check_if_model_is_valid(method):
    @wraps(method)
    def wrapped(self, *a, **kw):
        if not self._is_valid:
            raise ValueError("this view / model is not valid any more")
        return method(self, *a, **kw)

    return wrapped


class BaseModel(DbBackedModel):
    _access_name = None

    def __init__(
        self,
        parent_model,
        conn,
        access_name,
        col_names,
        col_types,
        col_formats,
        title,
        col_name_mapping,
        version=None,
    ):
        self.parent_model = parent_model
        self._conn = conn
        self._access_name = access_name

        if version is None:
            version = TABLE_VERSION

        if version < TABLE_VERSION:
            version = migrate(self, version, TABLE_VERSION)
            if version is None:
                raise ValueError("table version is outdated.")

        self.col_names = list(col_names)
        self.col_types = list(col_types)
        self.col_formats = list(col_formats)
        self.col_name_mapping = col_name_mapping
        self.title = title
        self.version = version

        self.update_col_formatters()

        self._count = None

        # we have a _index column in our tables and views, as views do not support
        # sqlite3 rowid.
        # self._indices maps absolute row index to _index column values and id lazily
        # loaded:
        self._indices = None
        self._max_index = None
        self._drop_statements = []
        self._is_valid = True
        self._unique_id = None

        self._info = None

    def close(self):
        self._conn.close()

    @property
    def info(self):
        if self._info is not None:
            return self._info

        self._setup_impl_specific_details()
        return self._info

    def _setup_impl_specific_details(self):
        """setup which might change in subclasses, e.g. ImmutableTableModel"""
        self._info = DbBackedDictionary(self, suffix="info")
        self.save_info()
        self._reset_unique_id()

    @property
    @check_if_model_is_valid
    def unique_id(self):
        if self._unique_id is None:
            hash_data = table_hash(self._conn, self._access_name).encode("ascii")
            hash_info = self.info.unique_id
            self._unique_id = md5_hexdigest(hash_data, hash_info)
        return self._unique_id

    def _reset_unique_id(self):
        self._unique_id = None

    @staticmethod
    def read_info(conn, access_name, key):
        results = conn.execute(
            f"SELECT value FROM {access_name}_info WHERE key = (?)", (key,)
        ).fetchall()
        if not results:
            return None
        return dill.loads(results[0][0])

    def save_info(self):
        self.info.update(
            {
                "col_names": self.col_names,
                "col_types": self.col_types,
                "col_formats": self.col_formats,
                "col_name_mapping": self.col_name_mapping,
                "title": self.title,
                "__version__": self.version,
            }
        )

    def set_title(self, title):
        self.title = title
        self.save_info()

    def update_col_formatters(self):
        self._col_formatters = setup_col_formatters(
            self.col_names, self.col_types, self.col_formats
        )

    def add_row(self, row):
        raise TypeError("you try to add a row to a view. you must consolidate first.")

    def delete_rows(self, rows):
        raise TypeError(
            "you try to remove rows from a view. you must consolidate first."
        )

    def add_column(self, name, what, type_, format_, insert_after, insert_before):
        raise TypeError(
            "you try to add a column to a view. you must consolidate first."
        )

    def replace_column(self, name, what, type_, format_):
        raise TypeError(
            "you try to replace a column of a view. you must consolidate first."
        )

    def drop_columns(self, col_names):
        raise TypeError(
            "you try to replace a column of a view. you must consolidate first."
        )

    def add_column_with_constant_value(
        self, name, value, type_, format_, insert_after, insert_before
    ):
        raise TypeError(
            "you try to add a column to a view. you must consolidate first."
        )

    def replace_column_with_constant_value(
        self, name, value, type_, format_, insert_after, insert_before
    ):
        raise TypeError(
            "you try to replace a column of a view. you must consolidate first."
        )

    def append(self, rows):
        raise TypeError("you try to add rows to a view. you must consolidate first.")

    def load_from(self, rows):
        raise TypeError("you try to add rows to a view. you must consolidate first.")

    def set_values(self, row_indices, col_index, values):
        raise TypeError("you try to modify a view. you must consolidate first.")

    def create_index(self, name):
        raise TypeError("you try to modify a view. you must consolidate first.")

    def drop_index(self, name):
        raise TypeError("you try to modify a view. you must consolidate first.")

    @check_if_model_is_valid
    def sorting_permutation(self, col_names_and_orders):
        db_col_names_and_orders = [
            (self.col_name_mapping[col_name], order)
            for col_name, order in col_names_and_orders
        ]
        orders = [
            f"{field} IS NULL ASC, {field} ASC"
            if order
            else f"{field} IS NULL ASC, {field} DESC"
            for field, order in db_col_names_and_orders
        ]

        order_expr = ", ".join(orders)

        stmt = f"SELECT _index FROM {self._access_name} ORDER BY {order_expr}"
        # translate form _index to table index we use e.g. with []:
        return [self.inv_indices[row[0]] for row in self._conn.execute(stmt).fetchall()]

    @check_if_model_is_valid
    def indices_for_rows_matching(self, expression):
        stmt = f"SELECT _index FROM {self._access_name} WHERE {expression}"
        # translate form _index to table index we use e.g. with []:
        return set(
            self.inv_indices[row[0]] for row in self._conn.execute(stmt).fetchall()
        )

    @check_if_model_is_valid
    def find_matching_rows(self, col_name, value):
        if not isinstance(value, (int, float, bool, str)):
            return []
        db_col_name = self.col_name_mapping[col_name]
        stmt = f"SELECT _index FROM {self._access_name} WHERE {db_col_name} = ?"
        # translate form _index to table index we use e.g. with []:
        return [
            self.inv_indices[row[0]]
            for row in self._conn.execute(stmt, (value,)).fetchall()
        ]

    @check_if_model_is_valid
    def consolidate(self, path, overwrite):
        """we pass meta_data from the Table class, model implementations do not manage
        meta data"""

        if path is not None:
            if os.path.exists(path):
                if overwrite:
                    os.remove(path)
                else:
                    raise OSError(f"database {path} already exists")

        target_conn = Connection(path)

        db_col_names = []
        db_col_types = []

        for col_name, db_col_name in self.col_name_mapping.items():
            db_col_names.append(db_col_name)
            col_type = self.col_types[self.col_names.index(col_name)]
            db_col_types.append(DEFAULT_DB_TYPES.get(col_type, "BLOB"))

        decls = ["_index INTEGER PRIMARY KEY AUTOINCREMENT"]
        decls.extend(
            "{} {}".format(name, type_)
            for (name, type_) in zip(db_col_names, db_col_types)
        )

        decl = ", ".join(decls)
        target_conn.execute(f"CREATE TABLE data ({decl});")
        target_conn.commit()

        uri = self._conn.uri
        target_conn.execute(f"ATTACH DATABASE '{uri}' AS SOURCE")
        self._conn.execute(f"ATTACH DATABASE '{target_conn.uri}' as TARGET")

        columns = ", ".join(db_col_names)

        # we must execute the following copy from the existing db to have access
        # to registered functions which might come into play when the current
        # model is a view involving custom functions.
        # see https://sissource.ethz.ch/sispub/emzed/emzed/-/issues/30
        self._conn.transfer_functions(target_conn)
        target_conn.execute(
            f"INSERT INTO data ({columns})"
            f" SELECT {columns} FROM SOURCE.'{self._access_name}'"
        )

        self._conn.commit()

        target_conn.commit()
        target_conn.execute("DETACH DATABASE SOURCE")
        target_conn.commit()

        self._conn.execute("DETACH DATABASE TARGET")
        self._conn.commit()

        # local import to avoid circular import:
        from .full_table_model import FullTableModel

        model = FullTableModel(
            target_conn,
            "data",
            self.col_names[:],
            self.col_types[:],
            self.col_formats[:],
            self.title,
            self.col_name_mapping.copy(),
            self.version,
        )
        model.save_info()

        copy_all_refered_tables(self, model._conn)
        return model

    def _split_by(self, col_names):
        db_col_names = [self.col_name_mapping[col_name] for col_name in col_names]
        cursor = self._conn.execute(
            f"SELECT DISTINCT {','.join(db_col_names)} FROM '{self._access_name}'"
        )

        def sql_repr(value):
            if isinstance(value, bytes):
                return repr(value.hex()).upper()
            return repr(value)

        def sql_func(value):
            if isinstance(value, bytes):
                return "hex"
            return ""

        all_values = list(cursor)
        for values in all_values:
            view_name = "_split_view_" + create_uid()
            where = " AND ".join(
                f"{sql_func(value)}({db_col_name}) = {sql_repr(value)}"
                if value is not None
                else f"{db_col_name} IS NULL"
                for (db_col_name, value) in zip(db_col_names, values)
            )
            self._conn.execute(
                f"CREATE VIEW {view_name} AS SELECT * FROM '{self._access_name}' "
                f"WHERE {where}"
            )
            yield ViewModel(self, view_name), view_name

    @check_if_model_is_valid
    def split_by(self, col_names):
        for model, view_name in self._split_by(col_names):
            yield model
            self._drop_statements.append(f"DROP VIEW {view_name};")

    @check_if_model_is_valid
    def split_by_iter(self, col_names):
        for model, view_name in self._split_by(col_names):
            yield model
            self._conn.execute(f"DROP VIEW {view_name};")

    @check_if_model_is_valid
    def count(self):
        if self._count is None:
            cursor = self._conn.execute(f"SELECT COUNT(*) FROM '{self._access_name}';")
            rows = cursor.fetchall()
            if not rows:
                self._count = 0
            else:
                self._count = int(rows[0][0])
        return self._count

    def __len__(self):
        return self.count()

    @check_if_model_is_valid
    def count_distinct(self, col_name):
        db_col_name = self.col_name_mapping[col_name]
        cursor = self._conn.execute(
            f"SELECT COUNT(DISTINCT {db_col_name}) FROM '{self._access_name}'"
        )
        return cursor.fetchone()[0]

    @property
    def indices(self):
        if self._indices is None:
            self._load_indices()
        return self._indices

    @property
    def inv_indices(self):
        if self._indices is None:
            self._load_indices()
        return self._inv_indices

    @property
    def max_index(self):
        if self._max_index is None:
            self._max_index = max(self.indices)
        return self._max_index

    @check_if_model_is_valid
    def get_row(self, index):
        if index < 0:
            index = self.count() + index

        if index >= len(self.indices):
            raise IndexError(f"index {index} out of range")

        columns = ", ".join(self.col_name_mapping[n] for n in self.col_names)
        row_id = self.indices[index]
        cursor = self._conn.execute(
            f"SELECT _index, {columns} FROM '{self._access_name}'"
            f"WHERE _index={row_id!r}"
        )
        rows = cursor.fetchall()
        if rows:
            names = ["_index"] + self.col_names
            Row = create_row_class(tuple(names))
            row = Row(tuple(self._load_rows(rows))[0])
            return row
        raise IndexError()

    @check_if_model_is_valid
    def _load_indices(self):
        cursor = self._conn.execute(f"SELECT _index FROM '{self._access_name}';")
        self._indices = [row[0] for row in cursor.fetchall()]
        self._inv_indices = {ix: i for i, ix in enumerate(self._indices)}

    @check_if_model_is_valid
    def get_iter(self):
        names = ["_index"] + self.col_names
        Row = create_row_class(tuple(names))
        for row in self.get_iter_raw():
            yield Row(row)

    @check_if_model_is_valid
    def get_iter_raw(self, col_names=None):
        if col_names is None:
            col_names = self.col_names
        columns = ", ".join(self.col_name_mapping[n] for n in col_names)
        cursor = self._conn.execute(
            f"SELECT _index, {columns} FROM '{self._access_name}'"
        )
        yield from self._load_rows(cursor, col_names)

    def _load_rows(self, row_iter, col_names=None):
        loaders = [int] + [
            self._get_loader(t)
            for (t, n) in zip(self.col_types, self.col_names)
            if col_names is None or n in col_names
        ]
        for row in row_iter:
            yield tuple(
                None if v is None else loader(v) for (loader, v) in zip(loaders, row)
            )

    @check_if_model_is_valid
    def column_accessor(self, col_name):
        if col_name != "_index":
            if col_name not in self.col_names:
                raise ValueError(f"invalid column name {col_name}")
        index = self.col_names.index(col_name)
        col_type = self.col_types[index]
        db_col_name = self.col_name_mapping[col_name]
        return column_accessor(self, col_name, col_type, db_col_name, self._access_name)

    @check_if_model_is_valid
    def set_col_format(self, col_name, format_):
        col_names = self.col_names
        if col_name not in col_names:
            raise ValueError(f"column '{col_name}' not known")
        ix = col_names.index(col_name)
        self.col_formats[ix] = format_
        self.update_col_formatters()
        self.save_info()
        self._reset_unique_id()

    @check_if_model_is_valid
    def set_col_type(self, col_name, type_, *, keep_format=False):
        col_names = self.col_names
        if col_name not in col_names:
            raise ValueError(f"column '{col_name}' not known")
        ix = col_names.index(col_name)
        type_now = self.col_types[ix]
        if not can_convert(type_now, type_):
            raise ValueError(f"can not convert type {type_now} to {type_}")
        self.col_types[ix] = type_
        if not keep_format:
            new_format = DEFAULT_FORMATS.get(type_)
            if new_format is not None:
                self.col_formats[ix] = new_format
                self.update_col_formatters()
        self.save_info()
        self._reset_unique_id()

    @check_if_model_is_valid
    def rename_columns(self, from_to):
        unknown = [name for name in from_to.keys() if name not in self.col_names]
        if unknown:
            unknown = ", ".join(unknown)
            raise ValueError(f"column(s) {unknown} not known")

        conflicting = [
            (col_name, new_name)
            for col_name, new_name in from_to.items()
            if new_name in self.col_names
        ]
        if conflicting:
            msg = ", ".join(
                f"{col_name} -> {new_name}" for col_name, new_name in conflicting
            )
            raise ValueError(f"renaming(s) {msg} conflict with existing columns")
        invalid = sorted(n for n in from_to.values() if n.startswith("_"))
        if invalid:
            raise ValueError(f"column names {', '.join(invalid)} are not valid.")
        mapping = self.col_name_mapping.copy()
        for from_, to in from_to.items():
            mapping[to] = mapping[from_]
            del mapping[from_]
        self.col_name_mapping = mapping

        self.col_names = [from_to.get(name, name) for name in self.col_names]
        self.update_col_formatters()
        self.save_info()
        self._reset_unique_id()

    @check_if_model_is_valid
    def extract_columns(self, names):
        """
        TODO: we might review the creation of views for joins and also
        for extracting columns etc.
        """
        unknown = [name for name in names if name not in self.col_names]
        if unknown:
            unknown = ", ".join(unknown)
            raise ValueError(f"column(s) {unknown} not known")

        # local import to avoid circular import:
        from .extract_columns_model import ExtractColumnsModel

        return ExtractColumnsModel(names, self)

    @check_if_model_is_valid
    def _copy_into(self, conn, unique_id_table):
        access_name = f"data_{unique_id_table}"
        if table_exists(conn, access_name):
            return

        copy_table(self._conn, conn, self._access_name, access_name)

        source = f"{self._access_name}_info"
        target = f"{access_name}_info"

        if not table_exists(conn, target):
            copy_table(self._conn, conn, source, target)

        target = f"{access_name}_meta"
        source = f"{self._access_name}_meta"
        if not table_exists(conn, target):
            copy_table(self._conn, conn, source, target)

        for table_name, _ in list_peakmap_tables(self._conn):
            if not table_exists(conn, table_name):
                copy_table(self._conn, conn, table_name, table_name)

        return access_name

    def _get_loader(self, t):
        if t is object:
            return lambda v: dill.loads(v)
        if hasattr(t, "_load_from_pickle"):
            return t._load_from_pickle
        if not hasattr(t, "_load_from_unique_id"):
            return t

        return partial(t._load_from_unique_id, self._conn)

    def register_view(self, view):
        raise RuntimeError("must never happend")

    def save_csv(self, path, as_printed, delimiter, dash_is_none):
        # https://docs.python.org/3.5/library/csv.html#id3
        with open(path, "w", newline="") as fh:
            writer = csv.writer(fh, delimiter=delimiter)
            if as_printed:
                col_names = [
                    name
                    for (name, format_, type_) in zip(
                        self.col_names, self.col_formats, self.col_types
                    )
                    if format_ is not None
                ]
                formatters = [self._col_formatters[n] for n in col_names]
            else:
                col_names = self.col_names
                noop = lambda x: "-" if x is None and dash_is_none else str(x)
                formatters = [noop for n in col_names]
            writer.writerow(col_names)
            for row in self.get_iter_raw(col_names):
                data = [f(value) for value, f in zip(row[1:], formatters)]
                writer.writerow(data)


class ViewModel(BaseModel):
    def __init__(self, parent_model, access_name):
        super().__init__(
            parent_model,
            parent_model._conn,
            access_name,
            parent_model.col_names,
            parent_model.col_types,
            parent_model.col_formats,
            parent_model.title,
            parent_model.col_name_mapping,
        )
        while parent_model.parent_model is not None:
            parent_model = parent_model.parent_model
        self.root_model = parent_model
        self.root_model.register_view(self)

    def invalidate(self):
        self._conn.execute(f"DROP VIEW IF EXISTS {self._access_name}")
        self._conn.commit()
        self._is_valid = False
