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
from collections import UserDict
from collections.abc import Mapping

import dill

from .db_backed_model import DbBackedModel
from .hashes import md5_hexdigest


class ImmutableDbBackedDictionary(UserDict, DbBackedModel):
    _access_name = None

    def __init__(self, conn, access_name, suffix, init_dict=None):
        self._access_name = f"{access_name}_{suffix}"
        self.conn = conn
        self._unique_id = None
        self._setup_table()
        if init_dict is not None:
            self._update(init_dict)

    def _setup_table(self):
        self.conn.execute(
            f"""CREATE TABLE IF NOT EXISTS '{self._access_name}' (
                      key TEXT PRIMARY KEY,
                      value BLOB
                )"""
        )

    def _update(self, dd):
        assert isinstance(dd, Mapping)
        stmt = f"INSERT OR REPLACE INTO {self._access_name} (key, value) VALUES (?, ?)"

        dd = resolve_db_backed_dicts(dd)

        self.conn.executemany(
            stmt,
            [
                (key, sqlite3.Binary(dill.dumps(value, protocol=4)))
                for key, value in dd.items()
            ],
        )
        self.conn.commit()

    def _reset_unique_id(self):
        raise RuntimeError("must not happen")

    @property
    def unique_id(self):
        if self._unique_id is None:
            self._unique_id = md5_hexdigest(dill.dumps(self.items(), protocol=4))
        return self._unique_id

    def copy(self, conn, target, source):
        conn.execute(
            f"""CREATE TABLE IF NOT EXISTS '{target}' (
                    key TEXT PRIMARY KEY,
                    value BLOB
            )"""
        )
        conn.execute(f"INSERT INTO {target} SELECT * FROM {source}")
        conn.commit()

    def __getitem__(self, key):
        results = self.conn.execute(
            f"SELECT value FROM {self._access_name} WHERE key = ?", (key,)
        ).fetchall()
        if not results:
            raise KeyError(f"no value for key {key!r}")
        assert len(results) == 1, "internal error"
        return dill.loads(results[0][0])

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        return key in self.keys()

    def __setitem__(self, key, value):
        raise NotImplementedError("this dictionary is immutable.")

    def __delitem__(self, key):
        raise NotImplementedError("this dictionary is immutable.")

    def update(self, dd):
        raise NotImplementedError("this dictionary is immutable.")

    def clear(self):
        raise NotImplementedError("this dictionary is immutable.")

    def keys(self):
        rows = self.conn.execute(f"SELECT key from {self._access_name}").fetchall()
        return [row[0] for row in rows]

    def values(self):
        rows = self.conn.execute(f"SELECT value from {self._access_name}").fetchall()
        return [dill.loads(row[0]) for row in rows]

    def items(self):
        rows = self.conn.execute(
            f"SELECT key, value from {self._access_name}"
        ).fetchall()
        return [(row[0], dill.loads(row[1])) for row in rows]

    def as_dict(self):
        return dict(self.items())

    def __str__(self):
        return str(self.as_dict())

    def __repr__(self):
        return repr(self.as_dict())


class DbBackedDictionary(ImmutableDbBackedDictionary):
    def __init__(self, parent_model, suffix="meta"):
        assert isinstance(parent_model, DbBackedModel)

        self.parent_model = parent_model
        self._access_name = f"{parent_model._access_name}_{suffix}"
        self.conn = parent_model._conn
        self._unique_id = None
        self._setup_table()

    def _reset_unique_id(self):
        self._unique_id = None

    def __setitem__(self, key, value):
        self.update({key: value})

    def update(self, dd):
        self._update(dd)
        self.parent_model._reset_unique_id()
        self._reset_unique_id()

    def __delitem__(self, key):
        if key not in self.keys():
            raise KeyError(f"unknown key {key!r}")

        self.conn.execute(f"DELETE FROM {self._access_name} WHERE key = ?", (key,))
        self.conn.commit()
        self.parent_model._reset_unique_id()
        self._reset_unique_id()

    def clear(self):
        self.conn.execute(f"DELETE FROM {self._access_name}")
        self.conn.commit()
        self.parent_model._reset_unique_id()
        self._reset_unique_id()


def resolve_db_backed_dicts(value):
    if isinstance(value, ImmutableDbBackedDictionary):
        return value.as_dict()
    elif isinstance(value, Mapping):
        return {k: resolve_db_backed_dicts(v) for (k, v) in value.items()}
    elif isinstance(value, list):
        return [resolve_db_backed_dicts(v) for v in value]
    elif isinstance(value, tuple):
        return tuple([resolve_db_backed_dicts(v) for v in value])
    elif isinstance(value, set):
        return set([resolve_db_backed_dicts(v) for v in value])
    return value
