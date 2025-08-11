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
import inspect
import io
import os
import sys
import warnings
from collections import Counter
from collections.abc import Collection, Mapping, Sequence
from contextlib import contextmanager
from fnmatch import fnmatch
from pickle import PicklingError
from types import FunctionType

import dill
import numpy as np

from emzed.core import DbBackedDictionary
from emzed.core.hashes import md5_hexdigest
from emzed.utils.functools import extend_function
from emzed.utils.sqlite import Connection, copy_table, list_tables

from .base_models import ViewModel
from .col_types import (
    DEFAULT_FORMATS,
    NUMERICAL_TYPES,
    MzType,
    RtType,
    check_col_type,
    to_pandas_type,
)
from .collapse import collapse
from .expressions import Apply, Expression
from .filter_model import FilterModel
from .full_table_model import FullTableModel
from .group_by import GroupBy
from .immutable_table_model import ImmutableTableModel
from .join import fast_join, fast_left_join, join, left_join
from .select_model import SelectModel
from .sort_model import SortModel
from .table_utils import (
    best_convert,
    create_db_table,
    get_references,
    guess_col_format,
    guess_col_formats,
    guess_common_type,
    list_data_tables,
    list_peakmap_tables,
    print_table,
    table_to_html,
)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    # can trigger warning due to non matching numpy
    import pandas as pd


class not_specified:
    def __str__(self):
        return "<not specified>"


def consolidate_per_default(method):
    extra_kw_args = dict(keep_view=False, path=None, overwrite=False)

    def wrapped(self, *args, **kwargs):
        keep_view = kwargs.pop("keep_view")
        path = kwargs.pop("path")
        overwrite = kwargs.pop("overwrite")
        if keep_view and path is not None:
            raise ValueError(
                "you must not specify path argument if you want to keep"
                " the result as a view"
            )

        result = method(self, *args, **kwargs)
        assert isinstance(result, Table) and isinstance(result._model, ViewModel)
        if keep_view:
            return result
        return result.consolidate(path=path, overwrite=overwrite)

    extra_kw_args_doc = [
        ":param keep_view: keep view or consolidate result (default: True)",
        (
            ":param path: path in case view is consolidated, 'None' keeps result"
            "in memory"
        ),
        (
            ":param overwite: if path is not None, this flag specifies if an existing"
            " file should be overwritten"
        ),
    ]

    return extend_function(method, wrapped, extra_kw_args, extra_kw_args_doc)


def _check(col_names, col_types, col_formats, rows, meta_data, path):
    if meta_data is None:
        meta_data = {}

    _check_types(col_names, col_types, col_formats, meta_data, path)
    _check_col_names(col_names)
    _check_col_types(col_names, col_types)
    _check_col_formats(col_names, col_formats)
    rows_as_list = _check_rows(col_names, rows)

    return meta_data, rows_as_list


def _check_types(col_names, col_types, col_formats, meta_data, path):
    assert isinstance(col_names, (list, tuple)), "col_names must be list or tuple"
    assert isinstance(col_types, (list, tuple)), "col_types must be list or tuple"

    if col_formats is not None:
        assert isinstance(
            col_formats, (list, tuple)
        ), "col_formats must be list or tuple or None"

    assert isinstance(meta_data, dict), "meta_data must be a dictionary or None"

    assert path is None or isinstance(path, str), "path must be None or a string"


def _check_col_names(col_names):
    if any(not isinstance(col_name, str) for col_name in col_names):
        raise ValueError("column names must be strings")

    if any(col_name == "" for col_name in col_names):
        raise ValueError("on of the given column names is an empty string")

    c = Counter(col_names)
    duplicates = [name for (name, count) in c.items() if count > 1]

    if len(duplicates) == 1:
        raise AssertionError("column name {} is a duplicate".format(duplicates[0]))
    elif len(duplicates) > 1:
        raise AssertionError(
            "column names {} are duplicates".format(", ".join(duplicates))
        )

    assert not any(
        col_name.startswith("_") for col_name in col_names
    ), "don't use col names starting with '_'"


def _check_col_types(col_names, col_types):
    assert len(col_types) == len(
        col_names
    ), "len of col_types and col_names does not match"


def _check_col_formats(col_names, col_formats):
    if col_formats is not None:
        assert len(col_formats) == len(
            col_names
        ), "len of col_formats and col_names does not match"


def _check_rows(col_names, rows):
    if rows is None:
        rows = []

    assert isinstance(rows, (list, tuple, np.ndarray, pd.DataFrame))
    if isinstance(rows, pd.DataFrame):
        rows = rows.to_numpy()

    rows_as_list = []
    for i, row in enumerate(rows):
        try:
            row_as_list = list(row)
        except ValueError:
            raise ValueError(f"can not convert row {i} to list")
        rows_as_list.append(row_as_list)

    if rows_as_list:
        n0 = len(rows_as_list[0])
        assert (
            len(col_names) == n0
        ), "length of first row does not match number of col_names"

        assert all(
            len(row) == n0 for row in rows_as_list
        ), "inconsistent row lengths in given rows"

    return rows_as_list


def create_table(
    col_names,
    col_types,
    col_formats=None,
    rows=None,
    title=None,
    meta_data=None,
    path=None,
):
    if col_formats is None:
        col_formats = guess_col_formats(col_names, col_types)

    col_names = check_and_fix(col_names, "col_names")
    col_types = check_and_fix(col_types, "col_types")
    col_formats = check_and_fix(col_formats, "col_formats")

    meta_data, rows = _check(col_names, col_types, col_formats, rows, meta_data, path)

    if path is not None:
        assert not os.path.exists(path)
    conn = Connection(path)

    col_name_mapping = create_db_table(conn, "data", col_names, col_types)

    model = FullTableModel(
        conn, "data", col_names, col_types, col_formats, title, col_name_mapping
    )

    model.append(rows)

    return Table(model, meta_data)


def check_and_fix(t, what):
    try:
        return list(t)
    except ValueError:
        type_ = type(t)
        raise ValueError(f"can not convert {what} to list, current type is {type_}")


class Table:
    _cache = {}

    @classmethod
    def _load_from_unique_id(cls, conn, unique_id):
        key = (conn.uri, unique_id)
        if key not in cls._cache:
            access_name = f"data_{unique_id}"
            cls._cache[key] = ImmutableTableModel.from_db_tables(conn, access_name)
        model = cls._cache[key]
        return Table(model, _freeze_unique_id=unique_id)

    def __init__(self, model, meta_data=None, *, _freeze_unique_id=None):
        self._model = model
        self._meta_data = DbBackedDictionary(model)
        if meta_data is not None:
            self._meta_data.update(meta_data)

        if _freeze_unique_id is not None:
            assert meta_data is None and isinstance(
                model, ImmutableTableModel
            ), "internal error"

        self._freeze_unique_id = _freeze_unique_id

    def __getstate__(self):
        parent_module = inspect.currentframe().f_back.f_code.co_filename.replace(
            "\\", "/"
        )
        if not parent_module.endswith("/multiprocessing/reduction.py"):
            raise NotImplementedError("pickling not supported for tables")

        if self.is_in_memory():
            raise PicklingError("can not use multiprocessing for in-memory tables.")

        return dill.dumps(
            (self._model, self._freeze_unique_id, self._meta_data), protocol=4
        )

    def __setstate__(self, data):
        self._model, self._freeze_unique_id, self._meta_data = dill.loads(data)

    @property
    def meta_data(self):
        return self._meta_data

    def get_title(self):
        return self._model.title

    def set_title(self, title):
        self._model.set_title(title)

    title = property(get_title, set_title)

    @property
    def col_names(self):
        """Column names.

        :returns: tuple of strings.
        """
        return tuple(self._model.col_names)

    @property
    def col_types(self):
        """Column types.

        :returns: tuple of types.
        """
        return tuple(self._model.col_types)

    @property
    def col_formats(self):
        """Column formats.

        :returns: tuple of format specifiers.
        """
        return tuple(self._model.col_formats)

    def __dir__(self):
        return list(self.__dict__) + list(self.col_names)

    def __eq__(self, other):
        return (
            isinstance(other, Table)
            and self.col_names == other.col_names
            and self.col_types == other.col_types
            and self.col_formats == other.col_formats
            and self.meta_data == other.meta_data
            and self.unique_id == other.unique_id
        )

    @staticmethod
    def create_table(
        col_names,
        col_types,
        col_formats=None,
        rows=None,
        title=None,
        meta_data=None,
        path=None,
    ):
        """creates a table.

        :param col_names: list or tuple of strings.
        :param col_types: list of types.
        :param col_formats: list of formats using format specifiers like "%.2f"  If not
                            specified emzed tries to guess appropriate formats based
                            on column type and column name.
        :param rows: list of lists.
        :param title: table title as string.
        :param meta_data: dictionary to manage user defined meta data.
        :param path: path for the db backend, default is ``None`` to use the  the
                     in-memory db backend.

        :returns: :py:class:`emzed.Table`.
        """
        return create_table(
            col_names, col_types, col_formats, rows, title, meta_data, path
        )

    @classmethod
    def open(cls, path):
        """opens table on disk without loading data into memory.

        :param path: path to file.

        :returns: :py:class:`emzed.Table`.
        """
        if not os.path.exists(path):
            raise IOError(f"file {path} does not exist.")
        conn = Connection(path)
        return Table(FullTableModel.from_db_tables(conn, "data"))

    def close(self):
        self._model.close()

    def is_open(self):
        return self._model._conn.is_open()

    def is_in_memory(self):
        return self.path is None

    @property
    def path(self):
        return self._model._conn.db_path

    @classmethod
    def load(cls, path):
        """loads table from disk into memory.

        :param path: path to file.

        :returns: :py:class:`emzed.Table`.
        """
        if not os.path.exists(path):
            raise IOError(f"file {path} does not exist")
        with Connection(path) as conn:
            return Table(ImmutableTableModel.from_db_tables(conn, "data")).consolidate()

    @property
    def unique_id(self):
        """computes unique identifier based on table content and meta data.

        :returns: unique identifier as string.
        """
        if self._freeze_unique_id is not None:
            return self._freeze_unique_id
        return md5_hexdigest(self._model.unique_id, self.meta_data.unique_id)

    @staticmethod
    def load_excel(path, col_names=None, col_types=None, col_formats=None):
        """loads excel file.

        :param path: path to file.
        :param col_names: list of column names, if not provided first line of .xlsx
                          or .xls file is used instead.
        :param col_types: list of colum types, if not provided emzed determines
                          types from column contents and names.
        :param col_formats: list of colum formats, if not provided emzed determines
                            formats from column contents and names.

        :returns: :py:class:`emzed.Table`.
        """
        if not os.path.exists(path):
            raise OSError(f"file {path} does not exist")

        with warnings.catch_warnings():
            # warning from xlrd library
            warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
            df = pd.read_excel(path, engine="openpyxl")

        return Table.from_pandas(df, col_names, col_types, col_formats)

    @staticmethod
    def from_pandas(df, col_names=None, col_types=None, col_formats=None):
        """converts pandas data frame into emzed Table.

        :param df: pandas data frame.
        :param col_names: list of colum names, can be used to override data frame
                          colum names.
        :param col_types: list of colum types, if not provided emzed determines
                          types from column contents and names.
        :param col_formats: list of colum formats, if not provided emzed determines
                            formats from column contents and names.

        :returns: :py:class:`emzed.Table`.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("need pandas DataFrame")

        if col_names is None:
            col_names = df.columns

        if col_types is None:
            # replace nan's with None first and convert values of df to list
            rows = df.astype(object).where(df.notna(), None).values.tolist()

            col_types = [
                guess_common_type(col_name, [row[i] for row in rows])
                for i, col_name in enumerate(col_names)
            ]
        else:
            if len(col_types) != len(col_names):
                raise ValueError("col_types and col_names do not match")

            def convert_na(v, t):
                if pd.isna(v):
                    return None
                return t(v)

            rows = [
                [convert_na(v, t) for v, t in zip(row, col_types)]
                for index, row in df.iterrows()
            ]

        if len(col_names) != len(df.columns):
            raise ValueError("rows in data frame do not match number of col_names.")

        if col_formats is None:
            col_formats = [
                guess_col_format(col_name, col_type)
                for col_name, col_type in zip(col_names, col_types)
            ]

        if len(col_formats) != len(col_names):
            raise ValueError("col_formats and col_names do not match")

        meta_data = {}
        return create_table(
            col_names, col_types, col_formats, rows, meta_data=meta_data
        )

    @staticmethod
    def load_csv(
        path,
        col_names=None,
        col_types=None,
        col_formats=None,
        *,
        delimiter=";",
        dash_is_none=True,
    ):
        """loads csv file.

        :param path: path to csv file.
        :param col_names: list of colum names, if not provided first line of csv file
                          is used instead.
        :param col_types: list of colum types, if not provided emzed determines
                          types from column contents and names.
        :param col_formats: list of colum formats, if not provided emzed determines
                            formats from column contents and names.
        :param delimiter:  csv delimiter character.
        :param dash_is_none: cells with '-' are interpreted as None (missing value).
                            types. In case `-` should be handled as a string with
                            the single character `"-"` one must set this argument
                            to ``False``.

        :returns: :py:class:`emzed.Table`.
        """
        if not os.path.exists(path):
            raise OSError(f"csv file {path} does not exist")

        with open(path, "r", encoding="utf-8") as fh:
            reader = csv.reader(fh, delimiter=delimiter)
            rows = list(reader)

        if any(len(rows[0]) != len(row) for row in rows):
            raise ValueError(f"rows in {path} do not all have same length.")

        if col_names is None:
            col_names = rows[0]
            rows = rows[1:]
        else:
            if any(len(col_names) != len(row) for row in rows):
                raise ValueError(f"rows in {path} do not match length of col_names.")

        rows = [
            [best_convert(cell.strip(), dash_is_none) for cell in row] for row in rows
        ]

        if col_types is None:
            col_types = [
                guess_common_type(col_name, [row[i] for row in rows])
                for i, col_name in enumerate(col_names)
            ]

        if len(col_types) != len(col_names):
            raise ValueError("col_types and col_names do not match")

        if col_formats is None:
            col_formats = [
                guess_col_format(col_name, col_type)
                for col_name, col_type in zip(col_names, col_types)
            ]

        if len(col_formats) != len(col_names):
            raise ValueError("col_formats and col_names do not match")

        meta_data = {"path": os.path.abspath(path)}
        # TODO: write tests
        return create_table(
            col_names, col_types, col_formats, rows, meta_data=meta_data
        )

    def __len__(self):
        return self._model.count()

    def __getitem__(self, index):
        assert isinstance(index, (int, str, slice, Sequence))
        if isinstance(index, int):
            if index < 0:
                index = self._model.count() + index
            return self._model.get_row(index)
        elif isinstance(index, str):
            return self._model.column_accessor(index)

        else:
            model = SelectModel(index, self._model)
            meta_data = self.meta_data.as_dict()
            meta_data["created_from"] = (self.unique_id, index)
            if "id" in meta_data:
                if isinstance(index, slice):
                    meta_data["id"] += "_sliced"
                else:
                    meta_data["id"] += "_selected"
            return Table(model, meta_data)

    def __delitem__(self, indices):
        if isinstance(indices, int):
            indices = [indices]

        assert isinstance(
            indices, Sequence
        ), "only integers, lists and tuples are supported"

        n = len(self)
        indices = [i + n if i < 0 else i for i in indices]

        if any(i < 0 or i >= n for i in indices):
            if n == 1:
                raise IndexError("index is out of range")
            raise IndexError("(some) indices are out of range")

        self._model.delete_rows(indices)

    def __getattr__(self, name):
        if name in self.col_names or name == "_index":
            return self._model.column_accessor(name)
        # following fall back needed to make properties work, see also
        # https://stackoverflow.com/questions/25115366/
        try:
            return self.__getattribute__(name)
        except AttributeError:
            raise AttributeError(f"method or column named '{name}' does not exist")

    def __getattribute__(self, name):
        if name not in ("__str__", "__repr__", "_model", "is_open", "__class__"):
            dd = super().__getattribute__("__dict__")
            if "_model" in dd and not dd["_model"]._conn.is_open():
                raise ValueError("Table is closed.")
        return super().__getattribute__(name)

    def __iter__(self):
        return self._model.get_iter()

    def __str__(self):
        if not self.is_open():
            return "<closed Table>"
        stream = io.StringIO()
        self.print_(stream=stream)
        return stream.getvalue()

    def _repr_html_(self):
        if not self.is_open():
            return "&lt;closed Table&gt;"
        return table_to_html(self)

    @property
    def rows(self):
        """
        :returns: All rows as list of tuples.
        """
        return list(self)

    def add_enumeration(
        self, col_name="id", insert_before=None, insert_after=None, start_with=0
    ):
        """adds enumerated column as first column to table *in place*.

        :param col_name: name of added column. Default name is ``id``.

        :param insert_before: to add column ``col_name`` at a defined position, one can
                              specify its position via the name of an existing column,
                              or an integer index (negative values allowed).
                              setting ``insert_before`` and the ``insert_after`` at
                              the same time is not allowed.
        :param insert_after: to add column ``col_name`` at a defined position, one can
                              specify its position via the name of an existing column,
                              or an integer index (negative values allowed).
                              setting ``insert_before`` and the ``insert_after`` at
                              the same time is not allowed.

        :param start_with: start value for creating the ids. default value is 0.
        """
        if insert_before is None and insert_after is None:
            insert_before = 0

        self.add_column(
            col_name,
            list(range(start_with, start_with + len(self))),
            int,
            insert_before=insert_before,
            insert_after=insert_after,
        )

    @consolidate_per_default
    def filter(self, condition):
        """creates a new table by filtering rows fulfiling the given condition.
        similar use as pandas ``query``.

        :param condition: expression like ``t.a < 0`` or ``t.a <= t.b``.
        :returns: :py:class:`emzed.Table` with filtered rows.
        """

        model = FilterModel(condition, self._model)

        meta_data = self.meta_data.as_dict()
        meta_data["created_from"] = (self.unique_id, str(condition))
        if "id" in meta_data:
            meta_data["id"] += "_filtered"
        return Table(model, meta_data)

    def save(self, path, *, overwrite=False):
        """save table to a file.

        :param path: path describing target location.
        :param overwrite: If set to ``True`` an existing file will be overwritten,
                          else an exception will be thrown.
        """
        if os.path.splitext(path)[1] != ".table":
            warnings.warn(
                "better use .table as file name extension when you save tables"
            )
        model = self._model.consolidate(path, overwrite)
        meta = DbBackedDictionary(model)
        meta.update(self.meta_data)
        model._conn.close()

    def get_column(self, name):
        """returns column expression object for column ``name``.

        You can use ``t[name]`` instead.
        """
        if name != "_index":
            self._ensure_col_names(name)
        return self._model.column_accessor(name)

    def fast_join(
        self,
        other,
        col_name,
        col_name_other=None,
        atol=0.0,
        rtol=0.0,
        extra_condition=None,
        *,
        path=None,
        overwrite=False,
    ):
        """joins (combines) two tables based on comparing approximate equality of two
        numerical columns.

        :param other: second table for join.
        :param col_name: column name to consider.
        :param col_name_other: column name of other to consider in case it is different
                               to `col_name`.
        :param atol: absolute tolerance for approximate equlity check.
        :param rtol: relative tolerance for approximate equlity check.

        :returns: :py:class:`emzed.Table`.

        Performance: In case `other` is significantly larger than `self`, it is
        recommended to swap the tables.

        The apprimate equality check for two numbers a and b is:

             abs(a - b) <= atol + rtol * abs(a)

        So if you only need comparison based absolute tolerance  you can set rtol to
        0.0, and if you only need relative tolerance check you can set atol to 0.0.
        """
        return self._fast_join(
            other,
            col_name,
            col_name_other,
            atol,
            rtol,
            fast_join,
            path,
            overwrite,
            extra_condition,
        )

    def fast_left_join(
        self,
        other,
        col_name,
        col_name_other=None,
        atol=0.0,
        rtol=0.0,
        extra_condition=None,
        *,
        path=None,
        overwrite=False,
    ):
        """joins (combines) two tables based on comparing approximate equality of two
        numerical columns.

        In contrast to :py:meth:`~fast_join` this method will include also non-matching
        rows from ``self``.

        :param other: second table for join.
        :param col_name: column name to consider.
        :param col_name_other: column name of other to consider in case it is different
                               to `col_name`.
        :param atol: absolute tolerance for approximate equlity check.
        :param rtol: relative tolerance for approximate equlity check.

        :returns: :py:class:`emzed.Table`.

        Performance: In case `other` is significantly larger than `self`, it is
        recommended to swap the tables.

        The apprimate equality check for two numbers a and b is:

             abs(a - b) <= atol + rtol * abs(a)

        So if you only need comparison based absolute tolerance  you can set rtol to
        0.0, and if you only need relative tolerance check you can set atol to 0.0.
        """
        return self._fast_join(
            other,
            col_name,
            col_name_other,
            atol,
            rtol,
            fast_left_join,
            path,
            overwrite,
            extra_condition,
        )

    def _fast_join(
        self,
        other,
        col_name,
        col_name_other,
        atol,
        rtol,
        join_method,
        path,
        overwrite,
        extra_condition,
    ):
        if path is not None and os.path.exists(path):
            if overwrite:
                os.unlink(path)
            else:
                raise ValueError(f"file {path} already exists")

        if col_name_other is None:
            col_name_other = col_name
        assert isinstance(
            other, Table
        ), f"other argument must be a Table, is {type(other)}"

        self._ensure_col_names(col_name)
        other._ensure_col_names(col_name_other)

        assert (
            self.col_types[self.col_names.index(col_name)] in NUMERICAL_TYPES
        ), f"column {col_name} is not a numerical column of {self}"
        assert (
            other.col_types[other.col_names.index(col_name_other)] in NUMERICAL_TYPES
        ), f"column {col_name} is not a numerical column of {self}"

        assert (
            atol >= 0.0 and rtol >= 0.0
        ), "invalid negative value for atol and/or rtol"

        assert not isinstance(
            self._model, ViewModel
        ), "you must consolidate the left table first"

        return self._assemble_join_result(
            other,
            join_method(
                self, other, col_name, col_name_other, atol, rtol, path, extra_condition
            ),
        )

    def _assemble_join_result(self, other, join_result):
        (conn, col_names, col_types, col_formats, title, col_name_mapping) = join_result

        model = FullTableModel(
            conn, "data", col_names, col_types, col_formats, title, col_name_mapping
        )

        references_self = get_references(self._model)
        references_other = get_references(other._model)

        data_tables = set(
            table_name for (table_name, _) in list_data_tables(self._model._conn)
        )
        data_tables |= set(
            table_name for (table_name, _) in list_data_tables(other._model._conn)
        )
        data_tables |= set(
            table_name for (table_name, _) in list_peakmap_tables(self._model._conn)
        )
        data_tables |= set(
            table_name for (table_name, _) in list_peakmap_tables(other._model._conn)
        )

        for table_name in data_tables:
            reference = table_name.split("_")[1]

            if reference in references_self:
                copy_table(self._model._conn, model._conn, table_name, table_name)
            elif reference in references_other:
                copy_table(other._model._conn, model._conn, table_name, table_name)

        return Table(model)

    @contextmanager
    def _create_temp_indices(self, *names):
        index_names = [self._model.create_index(name) for name in names]
        try:
            yield
        finally:
            for index_name in index_names:
                self._model.drop_index(index_name)

    def drop_columns(self, *col_names):
        """removes columns *in place*.

        :param col_names: column names. either exact names or names containg wild cards
                          like ``?`` and ``*``.

        Example: Table ``t`` with colnames ``id, mz, mzmin, mzmax, sample_1k1,
        sample_1m1, sample_1k2``

        ``t.drop_columns('mz*', 'sample_1?1')``

        results ``t`` with columns ``id, sample_1k2``
        """
        col_names = self._glob_col_names(col_names)
        self._ensure_col_names(*col_names)
        self._model.drop_columns(col_names)

    def join(self, other, expression=None, *, path=None, overwrite=False):
        """joins (combines) two tables.

        :param other: second table for join.

        :param expression: If ``None`` this method returns a table with the row wise
                           cross product of both tables. else this expression is used
                           to filter rows from this cross product.

        :returns: :py:class:`emzed.Table`.

        Example:

        if you have two table ``t1`` and ``t2`` as

        .. parsed-literal::

            id   mz
            int  float
            ---  -----
              0  100.0
              1  200.0
              2  300.0

        and

        .. parsed-literal::

            id   mz     rt
            int  float  float
            ---  -----  -----
              0  100.0   10.0
              1  110.0   20.0
              2  200.0   30.0

        Then the result of ``t1.join(t2, t1.mz.in_range(t2.mz - 20.0, t2.mz + 20.0))``
        is

        .. parsed-literal::

            id   mz     id__0  mz__0  rt__0
            int  float  int    float  float
            ---  -----  -----  -----  -----
              0  100.0      0  100.0   10.0
              0  100.0      1  110.0   20.0
              1  200.0      2  200.0   30.0

        If you do not provide an expression, this method returns the full
        cross product.
        """
        return self._join(other, expression, join, path, overwrite)

    def left_join(self, other, expression=None, *, path=None, overwrite=False):
        """Combines two tables (also known as *outer join*).

        :param other: Second table for join.

        :param expression: If ``None`` this method returns a table with the row wise
                           cross product of both tables. Else this expression is used
                           to filter rows from this cross product, whereby all rows of
                           the left table are kept.

        :returns: :py:class:`emzed.Table`.

        If we take the example from :py:meth:`~.join`

        Then ``t1.left_join(t2, t1.mz.in_range(t2.mz - 20.0, t2.mz + 20.0))`` results:

        .. parsed-literal::

            id   mz     id__0  mz__0  rt__0
            int  float  int    float  float
            ---  -----  -----  -----  -----
              0  100.0      0  100.0   10.0
              0  100.0      1  110.0   20.0
              1  200.0      2  200.0   30.0
              3  300.0      -      -      -

        """
        return self._join(other, expression, left_join, path, overwrite)

    def _join(self, other, expression, join_function, path, overwrite):
        if path is not None and os.path.exists(path):
            if overwrite:
                os.unlink(path)
            else:
                raise ValueError(f"file {path} already exists")
        return self._assemble_join_result(
            other, join_function(self._model, other._model, expression, path)
        )

    def print_(self, max_rows=30, max_col_width=None, stream=None):
        """print table.

        :param max_rows: Maximum number of rows to display. If the table is longer
                         only head and tail of the table are shown. The missing
                         part is denoted with "...".

        :param max_col_width: If specified the width of columns can be restricted.

        :param stream: file object to redirect printing, e.g. to a file.
        """

        print_table(self, max_rows, max_col_width, stream)

    def add_row(self, row):
        """adds row.

        :param row: list or tuple of values. Length must match.
        """
        if isinstance(row, Mapping):
            row = [row.get(col_name) for col_name in self.col_names]

        n = len(self.col_names)
        if len(row) != n:
            raise ValueError(f"row does not fit to number columns {n}")
        self._model.add_row(row)

    def extend(self, other, path=None, overwrite=False):
        assert self.col_names == other.col_names
        assert self.col_types == other.col_types

        if not other._model._is_valid:
            raise ValueError("the table you try to merge is not valid anymore")

        self._model.load_from(other._model)

        data_tables_self = set(
            table_name for (table_name, _) in list_data_tables(self._model._conn)
        )
        data_tables_self |= set(
            table_name for (table_name, _) in list_peakmap_tables(self._model._conn)
        )

        data_tables_other = set(
            table_name for (table_name, _) in list_data_tables(other._model._conn)
        )
        data_tables_other |= set(
            table_name for (table_name, _) in list_peakmap_tables(other._model._conn)
        )

        for table_name in data_tables_other - data_tables_self:
            copy_table(other._model._conn, self._model._conn, table_name, table_name)

    @staticmethod
    def stack_tables(tables, path=None, overwrite=False):
        """builds a single Table from list or tuple of Tables.

        :param tables: list or tuple of Tables. All tables must have
                       the same colum names with same types and formats.
        :param path: If specified the result will be a Table with a db file backend,
                     else the result will be managed in memory.
        :param overwrite: Indicate if an already existing database file should be
                          overwritten.

        :returns: :py:class:`emzed.Table`.
        """
        if not isinstance(tables, (list, tuple)):
            raise ValueError("need list or tuple of tables")
        if len(tables) == 0:
            raise ValueError("need more than 0 tables")
        table, *other_tables = tables
        table = table.consolidate(path, overwrite=overwrite)
        for other_table in other_tables:
            table.extend(other_table)
        return table

    def consolidate(self, path=None, *, overwrite=False):
        """consolidates if underlying database table is a view.

        :param path: If specified the result will be a Table with a db file backend,
                     else the result will be managed in memory.

        :param overwrite: Indicate if an already existing database file should be
                          overwritten.

        :returns: :py:class:`emzed.Table`.
        """
        try:
            model = self._model.consolidate(path, overwrite)
        except PermissionError:
            raise PermissionError(
                f"{path} is not writable. reasons might be missing access rights"
                " or another emzed Table is operating on the same file"
            )
        return Table(model, self.meta_data)

    # emzed 2 compliance:
    copy = consolidate

    def _check_and_process(self, insert_before, insert_after):
        if insert_after is not None and insert_before is not None:
            raise ValueError(
                "you must not specify insert_after and insert_before at the same time"
            )

        def check(value, name):
            if value is not None:
                if isinstance(value, int):
                    if value < 0:
                        # support negative indexing:
                        value += len(self.col_names)
                    if value < 0 or value >= len(self.col_names):
                        raise ValueError(
                            f"the argument {value} for {name} is out of bounds."
                        )
                    return self.col_names[value]
                elif isinstance(value, str):
                    if value not in self.col_names:
                        raise ValueError(
                            f"the provided value {value} for the argument"
                            f" {name} is not valid column name."
                        )
                    return value
                else:
                    type_ = type(value)
                    raise ValueError(f"invalid type {type_} for argument {name}.")

        insert_before = check(insert_before, "insert_before")
        insert_after = check(insert_after, "insert_after")
        return insert_before, insert_after

    def add_column(
        self,
        name,
        what,
        type_,
        format_=not_specified,
        insert_before=None,
        insert_after=None,
    ):
        r"""adds a new column with ``name`` *in place*.

        :param name: the name of the new column.

        :param what: either a ``list`` with the same length as table or an
                     ``expression``.

        :param type\_: supported colum types are
                       *int, float, bool, MzType, RtType, str, PeakMap, Table, object*.
                       In case you want to use Python objects like lists or dicts, use
                       column type 'object' instead.  :param format\_: is a format
                       string as "%d" or or an executable  string with python code. To
                       suppress visibility set format\_ = ``None``.
                       By default (``not_specified``) the method tries to determine a
                       default format for the type.
        :param insert_before: to add column ``name`` at a defined position, one can
                       specify its position left-wise to column ``insert_before`` via
                       the name of an existing column, or an integer index (negative
                       values allowed !).
        :param insert_after: to add column ``name`` at a defined position, one can
                             specify its position right-wise to column ``insert_after``.

        """
        self._ensure_col_names_dont_exist(name)
        check_col_type(type_)
        insert_before, insert_after = self._check_and_process(
            insert_before, insert_after
        )

        if format_ is not_specified:
            format_ = DEFAULT_FORMATS.get(type_, "%r")
        self._model.add_column(name, what, type_, format_, insert_after, insert_before)

    def replace_column(self, name, what, type_=None, format_=not_specified):
        r"""replaces content of existing column ``name`` *in place*.

        :param name: the name of the exisiting column.

        :param what: you can use a ``list`` with the same length as table or an
                    ``expression``.

        :param type\_:  supported colum types are
                       *int, float, bool, MzType, RtType, str, PeakMap, Table, object*.
                       In case you want to use Python objects like lists or dicts, use
                       column type 'object' instead.
        :param format\_: is a format string as "%d" or or an executable  string with
                         python code. To suppress visibility set format\_ = ``None``.
                         By default (``not_specified``) the method tries to determine a
                         default format for the type.
        :param insert_before: to add column ``name`` at a defined position, one can
                        specify its position left-wise to  column ``insert_before`` via
                        the name of an existing column, or an integer index (negative
                        values allowed !).
        :param insert_after: to add column ``name`` at a defined position, one can
                            specify its position right-wise to  column ``insert_after``.
        """
        self._ensure_col_names(name)

        if type_ is None:
            type_ = self.col_types[self.col_names.index(name)]
        check_col_type(type_)

        if format_ is not_specified:
            format_ = DEFAULT_FORMATS.get(type_, "%r")
        self._model.replace_column(name, what, type_, format_)

    def add_or_replace_column(
        self,
        name,
        what,
        type_=None,
        format_=not_specified,
        insert_before=None,
        insert_after=None,
    ):
        """replaces the content of column ``name`` if  it exists, else ``name`` is added
        (*in place*).

        For parameters see :py:meth:`~.replace_column`.
        """
        if name in self.col_names:
            self.replace_column(name, what, type_, format_)
        else:
            self.add_column(name, what, type_, format_, insert_before, insert_after)

    def add_or_replace_column_with_constant_value(
        self,
        name,
        what,
        type_=None,
        format_=not_specified,
        insert_before=None,
        insert_after=None,
    ):
        """replaces the content of column ``name`` with unique value if  ``name``
        exists, else ``name`` is added (*in place*).

        For parameters see :py:meth:`~.replace_column_with_constant_value`.
        """
        if name in self.col_names:
            self.replace_column_with_constant_value(name, what, type_, format_)
        else:
            self.add_column_with_constant_value(
                name, what, type_, format_, insert_before, insert_after
            )

    def replace_column_with_constant_value(
        self, name, what, type_=None, format_=not_specified
    ):
        """replaces the content of column ``name`` with unique value ``what``.

        For method parameters see :py:meth:`~.replace_column` with exception of

        :param what: any of accepted types *int, float, bool, MzType, RtType, str,
                     PeakMap, Table*.
        """
        self._ensure_col_names(name)

        if type_ is None:
            type_ = self.col_types[self.col_names.index(name)]
        check_col_type(type_)

        if format_ is not_specified:
            format_ = DEFAULT_FORMATS.get(type_, "%r")
        self._model.replace_column_with_constant_value(name, what, type_, format_)

    def add_column_with_constant_value(
        self,
        name,
        value,
        type_,
        format_=not_specified,
        insert_before=None,
        insert_after=None,
    ):
        """add column ``name`` with unique value ``value``.

        For method parameters see :py:meth:`~.add_column` with exception of

        :param what: any of accepted types *int, float, bool, MzType, RtType, str,
                     PeakMap, Table*.
        """
        self._ensure_col_names_dont_exist(name)
        check_col_type(type_)

        if isinstance(value, Expression):
            raise ValueError(
                "please use add_column if you want to add a "
                "new column by using an expression"
            )

        insert_before, insert_after = self._check_and_process(
            insert_before, insert_after
        )

        if format_ is not_specified:
            format_ = DEFAULT_FORMATS.get(type_, "%r")

        self._model.add_column_with_constant_value(
            name, value, type_, format_, insert_after, insert_before
        )

    def set_col_format(self, col_name, format_):
        r"""sets format of column ``col_name`` to format ``format_``.

        :param col_name: column name.

        :param format\_: accepted column format (see :py:meth:`~.add_column`).

        :returns: ``None``.
        """
        self._model.set_col_format(col_name, format_)

    def set_col_type(self, col_name, type_):
        r"""sets type of column ``col_name`` to type ``type_``.

        :param col_name: column name.

        :param type\_: accepted column type (see :py:meth:`~.add_column`).

        :returns: ``None``.
        """
        self._model.set_col_type(col_name, type_)

    def apply(self, function, *args, ignore_nones=True, result_type=None):
        """allows computing columns using a function with multiple arguments.

        :param function: any function accepting arguments ``*args``. The return
                         value can be used to compute another column.
        :param args: function arguments. arguments can be column expressions like
                      t['col_name'], or local or global variables accepted by
                      the function.
        :param ignore_nones: since ``None`` represents a missing value, apply
                      will not call ``function`` in case one of the arguments
                      is ``None`` and will instead consider ``None`` as result.
                      in case the function is able to consider such missing values,
                      one must set ``ignore_nones`` to ``False``.

        Example: the following code

        .. code-block:: python

            def convert(v):
                return str(v) + "s"

            t = emzed.to_table("a", [1, None, 5], int)
            t.add_column("b", t.apply(replace_none, t.a), int)
            t.add_column("c", t.apply(replace_none, t.a, ignore_nones=False), int)
            print(t)

        prints

        .. parsed-literal::

            a    b    c
            int  int  int
            ---  ---  ---
            1    1    1
            -    -   -1
            5    5    5
        """
        return Apply(self._model, function, args, ignore_nones)

    def rename_columns(self, **from_to):
        """changes column names from *current* to *new* name using key word arguments.

           :param from_to: key word arguments like ``a="b"``, see example below.

        Example: ``t.rename_columns(a="b")`` renames column ``"a"`` to ``"b"``
        """
        self._model.rename_columns(from_to)

    def rename_postfixes(self, **from_to):
        """changes column names from *current* to *new* name using key word arguments.

        Example:

           .. code-block:: python

            t = emzed.Table.create_table(
                   ["a", "a__0", "a__1", "b__0", "b__1"],
                   [int, int, int, int, int],
                   rows=[[1, 2, 3, 4, 5]]
            )
            print(t)

            t.rename_postfixes(__0="_zero")
            print(t)

        prints

           .. parsed-literal::

               a   a__0  a__1  b__0  b__1
               int  int   int   int   int
               ---  ----  ----  ----  ----
                 1     2     3     4     5

               a    a_zero  a__1  b_zero  b__1
               int  int     int   int     int
               ---  ------  ----  ------  ----
                 1       2     3       4     5

        """
        mapping = {}
        for postfix, new_postfix in from_to.items():
            if not isinstance(postfix, str):
                raise ValueError(f"the provided postfix {postfix!r} is not a string")
            if not isinstance(new_postfix, str):
                raise ValueError(
                    f"the provided postfix {new_postfix!r} is not a string"
                )
            for col_name in self.col_names:
                if not postfix:
                    mapping[col_name] = col_name + new_postfix
                elif col_name.endswith(postfix):
                    mapping[col_name] = col_name[: -len(postfix)] + new_postfix
        self._model.rename_columns(mapping)

    @consolidate_per_default
    def extract_columns(self, *col_names):
        """returns new Table with selected columns ``col_names``.

        :param col_names: list or tuple with selected, existing column names.
        """
        col_names = self._glob_col_names(col_names)
        self._ensure_col_names(*col_names)
        return Table(self._model.extract_columns(col_names))

    @consolidate_per_default
    def sort_by(self, *col_names, ascending=True):
        """sort table by given column names in given order.

        :param col_names: one or more column names as separate arguments.
        :param ascending: either bool or list/tuple of bools of same number as
                          specified column names.

        :returns: :py:class:`emzed.Table`.
        """
        if ascending not in (True, False):
            if not isinstance(ascending, (tuple, list)):
                raise ValueError("ascending must be a bool or list/tuple of bools")
            if len(ascending) != len(col_names):
                raise ValueError(
                    "length of ascending must be the same as the number of"
                    " provided column names"
                )
            if not all(a in (True, False) for a in ascending):
                raise ValueError("entries of ascending must be True or False")
        else:
            ascending = [ascending] * len(col_names)

        if not all(isinstance(col_name, str) for col_name in col_names):
            raise ValueError(
                "not all column names are strings, maybe you did not"
                " specify ascending as 'ascending=...'"
            )

        model = SortModel(col_names, ascending, self._model)
        return Table(model, self.meta_data)

    def _glob_col_names(self, col_names):
        result = []
        for col_name in col_names:
            if "?" not in col_name and "*" not in col_name:
                result.append(col_name)
                continue
            result.extend([name for name in self.col_names if fnmatch(name, col_name)])
        return result

    def group_by(self, *colums, group_nones=False):
        """return Table group_by object where rows got grouped by columns.

           :param columns: table columns i.e ``t.a``, or ``t['b']``.

           :param group_nones: ignores rows where group columns are None.

           :returns: ``GroupBy`` object

        Examples: For given Table t

        .. parsed-literal::

          a    b    c
          int  int  int
          ---  ---  ---
            0    1    2
            1    -    1
            2    -    0
            2    2    3

        >>> t.add_Column('ga', t.group_by(t.a).min(t.c), int)
        >>> t.add_Column('gb1', t.group_by(t.b).min(t.c), int)
        >>> t.add_Column('gb2', t.group_by(t.c).min(t.c), int)

        >>> print(t)

        .. parsed-literal::

          a    b    c    ga   gb1  gb2
          int  int  int  int  int  int
          ---  ---  ---  ---  ---  ---
            0    1    2    2    2    2
            1    -    1    1    -    0
            2    -    0    0    -    0
            2    2    3    0    3    3

        """
        col_names = [column.col_name for column in colums]
        return GroupBy(self._model, col_names, group_nones)

    def _sorting_permutation(self, col_names_and_orders):
        assert isinstance(col_names_and_orders, Collection)
        assert all(isinstance(fo, Collection) for fo in col_names_and_orders)
        assert all(len(fo) == 2 for fo in col_names_and_orders)
        assert all(col_name in self.col_names for col_name, _ in col_names_and_orders)
        assert all(ascending in (True, False) for _, ascending in col_names_and_orders)
        return self._model.sorting_permutation(col_names_and_orders)

    def _indices_for_rows_matching(self, filter_expression):
        return self._model.indices_for_rows_matching(filter_expression)

    def _find_matching_rows(self, col_name, value):
        assert col_name in self.col_names
        from .prepare_table_cell_content import prepare_table_cell_content

        col_type = self.col_types[self.col_names.index(col_name)]
        value = prepare_table_cell_content(self._model, value, col_type)
        return self._model.find_matching_rows(col_name, value)

    def _copy_into(self, conn):
        return self._model._copy_into(conn, self.unique_id)

    def __repr__(self):
        if not self.is_open():
            return "<closed Table>"
        is_ipython = (
            hasattr(sys.stdout, "__module__")
            and sys.stdout.__module__ == "ipykernel.iostream"
        )
        if is_ipython:
            return str(self)
        if "id" in self.meta_data:
            return f"<Table id={self.meta_data['id']}>"
        return f"<Table {self.unique_id[:6]}...>"

    def is_mutable(self):
        """returns boolean value to show whether the content of a Table is mutable."""
        return isinstance(self._model, FullTableModel)

    def _set_value(self, row_indices, column, value):
        """replaces one value of ``column`` in row ``row_index`` with ``value``.

        :param row_indices: row indices to change

        :param column: argument can be a column name or an integer index of selected
                       value.

        :param value: new value

        Example: ``t._set_value([0], 'mz', 252.83332)``
        """
        if not isinstance(row_indices, Sequence):
            raise ValueError("row_indices must be a sequncee like list or tuple")

        if isinstance(column, str):
            if column not in self.col_names:
                raise ValueError(f"invalid value {column} for column")
            else:
                column = self.col_names.index(column)
        if not all(0 <= row_index < len(self) for row_index in row_indices):
            raise ValueError("invalid value in row_indices")
        if not 0 <= column < len(self.col_names):
            raise ValueError(f"invalid value {column} for column")
        self._model.set_value(row_indices, column, value)

    def _set_values(self, row_indices, column, values):
        if not isinstance(row_indices, Sequence):
            raise ValueError("row_indices must be a sequncee like list or tuple")

        if not isinstance(values, Sequence):
            raise ValueError("values must be a sequncee like list or tuple")

        if len(row_indices) != len(values):
            raise ValueError("values and row_indices must have same length")

        if isinstance(column, str):
            if column not in self.col_names:
                raise ValueError(f"invalid value {column} for column")
            else:
                column = self.col_names.index(column)
        if not all(0 <= row_index < len(self) for row_index in row_indices):
            raise ValueError("invalid value in row_indices")
        if not 0 <= column < len(self.col_names):
            raise ValueError(f"invalid value {column} for column")

        self._model.set_values(row_indices, column, values)

    def save_csv(
        self,
        path,
        delimiter=";",
        as_printed=False,
        dash_is_none=True,
        *,
        overwrite=False,
    ):
        """saves Table as csv in ``path``.

        :param path: specifies path of the file. The path must end with ``.csv``.

        :param delimiter: Alias for sep. Default value is set to Excel dialect ';'.

        :param as_printed: If ``True``, formatted values will be stored. Note,
                           format settings can lead to information loss, i.e. if column
                           format value is set to *.2f%* only the first 2 decimal places
                           will be saved.
        :param overwrite: If set to ``True`` an existing file will be overwritten,
                          else an exception will be thrown.
        """
        if not overwrite and os.path.exists(path):
            raise OSError(
                f"file {path} exists, use overwrite=True in case you want to overwrite"
                " the file."
            )

        if not path.lower().endswith(".csv"):
            raise ValueError(f"given path {path} does not end with .csv")

        self._model.save_csv(path, as_printed, delimiter, dash_is_none)

    def to_pandas(self):
        """converts table to pandas DataFrame object"""
        data = {}
        from emzed import PeakMap

        if len(self.col_names):
            # unzip trick, will fail for empty lists:
            names, types = zip(
                *[
                    (name, type_)
                    for (name, type_, format_) in zip(
                        self.col_names, self.col_types, self.col_formats
                    )
                    if format_ is not None and type_ not in (Table, PeakMap)
                ]
            )
        else:
            names, types = [], []

        for name in names:
            data[name] = list(getattr(self, name))

        df = pd.DataFrame(data, columns=names)

        type_mapping = {name: to_pandas_type(t) for (name, t) in zip(names, types)}

        return df.astype(type_mapping)

    def save_excel(self, path, *, overwrite=False):
        """saves Table as xls or xlsx in ``path``.

        :param path: specifies path of the file. The path must end with ``.xls`` or
                     ``.xlsx``.
        """
        if not overwrite and os.path.exists(path):
            raise OSError(
                f"file {path} exists, use overwrite=True in case you want to overwrite"
                " the file."
            )

        ext = os.path.splitext(path)[1].lower()
        if ext not in (".xls", ".xlsx"):
            raise ValueError(f"given path {path} does not end with .xls or xlsx")
        self.to_pandas().to_excel(path, index=False, engine="openpyxl")

    def supported_postfixes(self, col_names):
        """returns common postfixes (endings) of column ``col_names``.

        :param col_names: list or tuple of column names.

        :returns:
            list of common postfixes.

        Examples: Assuming a Table with columns
                  ``['rt', 'rtmin', 'rtmax', 'rt1', 'rtmin1']``.

        >>> t.supported_postfixes(['rt'])

        returns ``['', 'min', 'max', '1', 'min1']``

        >>> t.supported_postfixes(['rt', 'rtmin'])

        returns ``['', '1']``

        >>> t.supported_postfixes(['rt', 'rtmax'])

        returns ``['']``
        """

        def _check(postfix):
            return all(name + postfix in self.col_names for name in col_names)

        postfixes = []
        if _check(""):
            postfixes.append("")
        for name in self.col_names:
            if "__" in name:
                postfix = "__" + name.split("__", 1)[-1]
                if postfix not in postfixes and _check(postfix):
                    postfixes.append(postfix)
        return postfixes

    def _ensure_col_names(self, *names):
        missing = ", ".join(name for name in names if name not in self.col_names)
        if not missing:
            return
        raise ValueError(f"column(s) with name(s) {missing} required")

    def _ensure_col_names_dont_exist(self, *names):
        existing = ", ".join(name for name in names if name in self.col_names)
        if not existing:
            return
        raise ValueError(f"column(s) with name(s) {existing} already exist")

    def split_by(self, *col_names, keep_view=False):
        """generates a list of subtables, whereby split columns ``col_names`` contain
        unique values.

        :param col_names: column names with values defining split groups.

        :returns: a list of sub_tables

        Example: If we have a table ``t`` as

        .. parsed-literal::

            a   b   c
            int int int
            --- --- ---
              1   1   1
              1   1   2
              2   1   3
              2   2   4

        ``sub_tables = t.splitBy("a")`` results 3 subtables

        sub_tables[0]

        .. parsed-literal::

            a   b   c
            int int int
            --- --- ---
              1   1   1
              1   1   2

        sub_tables[1]

        .. parsed-literal::

            a   b   c
            int int int
            --- --- ---
              2   1   3

        and subtables[2]

        .. parsed-literal::

            a   b   c
            int int int
            --- --- ---
              2   2   4

        """
        self._ensure_col_names(*col_names)
        tables = [
            Table(model, self.meta_data) for model in self._model.split_by(col_names)
        ]
        if keep_view:
            return tables

        return [t.consolidate() for t in tables]

    def split_by_iter(self, *col_names, keep_view=False):
        """builds a generator yielding subtables, whereby subtable split columns
        ``col_names`` contain unique values.

        :param col_names: column names with values defining split groups.

        :returns: a generator object of subtables

        refering to example table :py:meth:`~.split_by`:

        >>> sub_tables=t.split_by_iter("a")

        >>> print(next(sub_tables))

        results

        .. parsed-literal::

            a   b   c
            int int int
            --- --- ---
              1   1   1
              1   1   2

        hence the first sub_table of t, corresponding to sub_tables[0] in
        :py:meth:`~.split_by` example. :py:meth:`~.split_by_iter` can be more memory
        efficient than :py:meth:`~split_by`.
        """
        self._ensure_col_names(*col_names)
        for model in self._model.split_by_iter(col_names):
            if keep_view:
                yield Table(model, self.meta_data)
            else:
                yield Table(model, self.meta_data).consolidate()

    def collapse(self, *col_names, new_col_name="collapsed", path=None):
        """colapses a table by grouping according to columns ``col_names``.

        :param col_names: column names with values defining colapsing groups.

        :param new_col_names: column name of new column resulting from colapsing
                              process.

        :param path: If specified the result will be a Table with a db file backend,
                     else the result will be managed in memory.
        :returns: ``emzed.Table``

        Example:

        .. parsed-literal::

            a   b   c
            int int int
            --- --- ---
              1   1   1
              1   1   2
              2   1   3
              2   2   4

        >>> print(t.collapse('a'))

        results

        .. parsed-literal::

            a   collapsed
            int emzed.Table
            --- ---------------
            1   <Table af3 ...>
            2   <Table e9f ...>

        """
        self._ensure_col_names(*col_names)
        return collapse(self._model, col_names, new_col_name, path)

    @classmethod
    def _remove_unused_references(clz, table_model, unique_ids_in_use):
        deleted = False
        for t in list_tables(table_model._conn):
            if t.startswith("data_"):
                unique_id = t.removeprefix("data_").split("_")[0]
                # don't delete base tables:
                if unique_id in ("info", "meta", ""):
                    continue
                if unique_id not in unique_ids_in_use:
                    table_model._conn.execute(f"DROP TABLE IF EXISTS {t};")
                    deleted = True
        if deleted:
            table_model._conn.commit()

    def summary(self):
        rows = []
        n = len(self)
        for name, type_, format in zip(
            self.col_names, self.col_types, self.col_formats
        ):
            min_, max_ = None, None
            if type_ in (int, float, MzType, RtType):
                min_ = min((v for v in self[name] if v is not None), default=None)
                max_ = max((v for v in self[name] if v is not None), default=None)
            distinct_values = self._model.count_distinct(name)
            nones = sum(1 for v in self[name] if v is None)
            if isinstance(format, FunctionType):
                format = format.__name__
            rows.append(
                (
                    name,
                    type_.__name__,
                    str(format),
                    nones,
                    n,
                    min_,
                    max_,
                    distinct_values,
                )
            )
        info_table = Table.create_table(
            ["name", "type", "format", "nones", "len", "min", "max", "distinct values"],
            [str, str, str, int, int, float, float, int],
            rows=rows,
        )
        info_table.add_enumeration()
        return info_table


def to_table(name, values, type_, format_=None, title=None, meta_data=None, path=None):
    r"""generates a one-column Table from an iterable, e.g. from a list.

    :param name: name of the column.

    :param values: iterable with column values.

    :param type\_:  supported colum types are
                   *int, float, bool, MzType, RtType, str, PeakMap, Table, object*.
                   In case you want to use Python objects like lists or dicts, use
                   column type 'object' instead.
    :param format\_: is a format string as "%d". To suppress visibility set
                     format\_ = ``None``.  By default (``not_specified``) the method
                     tries to determine a default format for the type.
    :param title: Table title as string.

    :param meta_data: Python dictionary to assign meta data to the table.

    :param path: Path for the db backend, use ``None`` for an in memory db backend.

    :returns: ``emzed.Table``
    """
    if format_ is not None:
        format_ = [format_]
    rows = [[value] for value in values]
    return Table.create_table([name], [type_], format_, rows, title, meta_data, path)
