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


import functools


class Row:
    pass


@functools.lru_cache()
def create_row_class(col_names):
    visible_names = [name for name in col_names if not name.startswith("_")]

    class _Row(Row):
        __slots__ = ["_fields"]

        def __init__(self, values):
            self._fields = dict(zip(col_names, values))

        def __getattr__(self, col_name):
            if col_name in self._fields:
                return self._fields[col_name]
            raise IndexError()

        def __iter__(self):
            return (self._fields[name] for name in visible_names)

        def __dir__(self):
            return visible_names

        def __contains__(self, name):
            return name in col_names

        def __getitem__(self, index):
            if not isinstance(index, (slice, int, str)):
                raise IndexError(f"invalid index {index!r}")
            if isinstance(index, int):
                if index < 0:
                    index += len(col_names)
                if index < 0 or index >= len(col_names):
                    raise IndexError(f"index {index} is out of range")
            elif isinstance(index, str):
                if index not in col_names:
                    raise IndexError(f"{index!r} is not a valid column name")
                return self._fields[index]
            return list(self._fields.values())[index]

        def get(self, col_name, default=None):
            return self._fields.get(col_name, default)

        def __eq__(self, other):
            if not isinstance(other, Row):
                return False
            return self._fields == other._fields

        def __repr__(self):
            values = ", ".join(
                "{}={}".format(key, value) for (key, value) in self._fields.items()
            )
            return f"Row({values})"

        def __str__(self):
            values = ", ".join(
                "{}={}".format(key, value) for (key, value) in self._fields.items()
            )
            return f"({values})"

        def __len__(self):
            return len(visible_names)

    return _Row
