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


import hashlib
import re
import sqlite3
import sys
import traceback
import uuid
from functools import wraps
from multiprocessing.process import current_process


def create_uid():
    random_id = uuid.uuid4().hex[:12]
    blocks = [random_id[i : i + 4] for i in range(0, len(random_id), 4)]
    return "_".join(blocks)


def debug(function):
    @wraps(function)
    def wrapped(self, stmt, *a, **kw):
        if self._debug is not None:
            self._debug(stmt.strip())
            self._debug("\n")
            if a:
                self._debug(f"ARGS = {a}")
                self._debug("\n")
            self._debug("\n")
        try:
            return function(self, stmt, *a, **kw)
        except:  # noqa E722
            import traceback

            traceback.print_exc()
            print(stmt, a, kw)
            raise

    return wrapped


def reraise_exception_conn(function):
    @wraps(function)
    def wrapped(self, stmt, *a, **kw):
        try:
            result = function(self, stmt, *a, **kw)
        except sqlite3.OperationalError:
            if self._exception is None:
                self._exception = sys.exc_info()
        if self._exception is not None:
            et, ev, tb = self._exception
            traceback.print_exception(et, ev, tb)

            while tb.tb_next:
                tb = tb.tb_next

            print("Locals:", tb.tb_frame.f_locals)
            print()
            self._exception = None
            raise ev.with_traceback(tb)
        return result

    return wrapped


def proc_id():
    return current_process().ident


class Connection:
    _debug = None
    _open_connections = 0

    def __init__(self, db_path=None):
        if db_path is None:
            id_ = create_uid()
            db_name = "db_{}".format(id_)
            uri = f"file:{db_name}?mode=memory&cache=shared"
        else:
            uri = f"file:{db_path}"
        self.uri = uri
        self.db_path = db_path
        self._current_process_ident = proc_id()
        self._exception = None
        self._commit_pending = False
        self._functions = {}
        self._functions_cache = {}

        Connection._open_connections += 1

        self.reconnect()

    def close(self):
        if not self._is_open:
            return
        self.commit()
        self._connection.close()
        self._is_open = False
        Connection._open_connections -= 1

    def cursor(self):
        return Cursor(self)

    def set_exception(self, e_type, e_value, tb):
        self._exception = (e_type, e_value, tb)

    def commit(self):
        self._commit_pending = False
        self._connection.commit()

    def create_function(self, name, nargs, python_function):
        if name in self._functions:
            return
        self._functions[name] = (nargs, python_function)

        def wrapped(*a, **kw):
            try:
                return python_function(*a, **kw)
            except Exception:
                print(file=sys.stderr)
                print("FUNCITON STORED IN SQLITE RAISE ERRROR:", file=sys.stderr)
                print(python_function, a, kw, file=sys.stderr)
                print(file=sys.stderr)
                import traceback

                traceback.print_exc()
                raise

        self._connection.create_function(name, nargs, python_function)

    def transfer_functions(self, target_conn):
        for name, (nargs, python_function) in self._functions.items():
            target_conn.create_function(name, nargs, python_function)

    def __getattr__(self, name):
        #  forware methods to coonnection object
        if "_connection" not in self.__dict__:
            raise AttributeError(f"{name}")
        return getattr(self.__dict__["_connection"], name)

    def __getstate__(self):
        return {
            "uri": self.uri,
            "db_path": self.db_path,
            "_current_process_ident": self._current_process_ident,
            "_exception": self._exception,
            "_functions": self._functions,
        }

    def reconnect(self):
        self._connection = sqlite3.connect(self.uri, uri=True, check_same_thread=False)
        register_md5_hasher(self._connection)
        register_re_match_function(self)
        self.transfer_functions(self._connection)
        self._is_open = True

    def __setstate__(self, dd):
        self.__dict__.update(dd)
        self.reconnect()

    def is_closed(self):
        return not self._is_open

    def is_open(self):
        return self._is_open

    @debug
    @reraise_exception_conn
    def execute(self, stmt, *a, **kw):
        if proc_id() != self._current_process_ident:
            self._current_process_ident = proc_id()
            self._connection = sqlite3.connect(
                self.uri, uri=True, check_same_thread=False
            )
            register_md5_hasher(self._connection)
            register_re_match_function(self)
        self._commit_pending = True
        return self._connection.execute(stmt, *a, **kw)

    @debug
    @reraise_exception_conn
    def executemany(self, stmt, *a, **kw):
        if proc_id() != self._current_process_ident:
            self._current_process_ident = proc_id()
            self.reconnect()
        self._commit_pending = True
        return self._connection.executemany(stmt, *a, **kw)

    @property
    def schemata(self):
        rows = self._connection.execute("select * from sqlite_master").fetchall()
        from emzed import Table

        return Table.create_table(
            ["type", "name", "tbl_name", "rootpage", "sql"],
            [str, str, str, int, str],
            ["%s", "%s", "%s", "%d", "%r"],
            rows=rows,
        )

    def __enter__(self):
        return self

    def __exit__(self, type_, value, tb):
        self.close()


def reraise_exception_cursor(function):
    @wraps(function)
    def wrapped(self, stmt, *a, **kw):
        try:
            result = function(self, stmt, *a, **kw)
        except sqlite3.OperationalError:
            if self._conn._exception is None:
                self._conn._exception = sys.exc_info()
        if self._conn._exception is not None:
            et, ev, tb = self._conn._exception
            traceback.print_exception(et, ev, tb)

            while tb.tb_next:
                tb = tb.tb_next

            print("Locals:", tb.tb_frame.f_locals)
            print()
            self._conn._exception = None
            raise ev.with_traceback(tb)
        return result

    return wrapped


class Cursor:
    def __init__(self, conn):
        self._conn = conn
        self._cursor = conn._connection.cursor()
        self._exception = None

    @reraise_exception_cursor
    def execute(self, *a, **kw):
        return self._cursor.execute(*a, **kw)

    @reraise_exception_cursor
    def executemany(self, *a, **kw):
        return self._cursor.executemany(*a, **kw)

    def __getattr__(self, name):
        return getattr(self._cursor, name)

    def __getstate__(self):
        return self._conn

    def __setstate__(self, conn):
        self._conn = conn
        self._cursor = conn._connection.cursor()


def table_exists(conn, name):
    return (
        len(
            conn.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{name}';"
            ).fetchall()
        )
        != 0
    )


def list_tables(conn):
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [row[0] for row in cursor]


def list_views(conn):
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='view';")
    return [row[0] for row in cursor]


def copy_table(conn_from, conn_to, table_name_from, table_name_to):
    conn_to.execute(f"ATTACH DATABASE '{conn_from.uri}' AS DBFROM;")
    conn_from.transfer_functions(conn_to)
    conn_to.execute(
        f"CREATE TABLE {table_name_to} AS SELECT * FROM DBFROM.{table_name_from}"
    )
    conn_to.commit()
    conn_to.execute("DETACH DATABASE DBFROM;")
    conn_to.commit()


def copy_tables(conn_from, conn_to, table_names_from, table_names_to):
    conn_to.execute(f"ATTACH DATABASE '{conn_from.uri}' AS DBFROM;")

    conn_from.transfer_functions(conn_to)

    for table_name_to, table_name_from in zip(table_names_to, table_names_from):
        conn_to.execute(
            f"CREATE TABLE {table_name_to} AS SELECT * FROM DBFROM.{table_name_from}"
        )

    conn_to.commit()
    conn_to.execute("DETACH DATABASE DBFROM;")
    conn_to.commit()


class Md5HexDigestAggregate:
    def __init__(self):
        self._values = []

    def step(self, *args):
        self._values.append(args)

    def finalize(self):
        hasher = hashlib.md5()
        for args in sorted(self._values):
            for item in args:
                hasher.update(str(item).encode("utf-8"))
        return hasher.hexdigest()


def register_md5_hasher(sqlite3_connection):
    sqlite3_connection.create_aggregate("md5_hexdigest", -1, Md5HexDigestAggregate)


def register_re_match_function(conn):
    def re_match(regex, txt):
        if txt is None:
            return False
        try:
            return re.match(regex, txt) is not None
        except Exception:
            conn.set_exception(*sys.exc_info())
            raise

    conn._connection.create_function("re_match", 2, re_match)


def table_hash(conn, table_name):
    conn.commit()

    col_names = [row[1] for row in conn.execute(f"PRAGMA TABLE_INFO('{table_name}');")]

    col_names_spec = ", ".join(col_names)

    result = conn.execute(
        f"SELECT md5_hexdigest({col_names_spec}) FROM {table_name};"
    ).fetchone()
    return result[0] or ""  # avoids None
