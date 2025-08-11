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

import pytest

from emzed.table.expressions import Value


@pytest.fixture(scope="module")
def eval_():
    conn = sqlite3.connect(":memory:")

    def _eval(expression, conn=conn):
        return conn.execute(f"SELECT {expression};").fetchall()[0][0]

    yield _eval
    conn.close()


v1 = Value(1.0)
v2 = Value(2.0)
T = Value(True)
F = Value(False)


def test_str_conversion(regtest):
    for v in (v1, v1 + v2):
        print(v, file=regtest)


def test_repr_conversion(regtest):
    for v in (v1, v1 + v2):
        print(repr(v), file=regtest)


cases = [
    (v1 + v2, 3),
    (1 + v1, 2),
    (v1 + 1, 2),
    #
    (v1 * v2, 2),
    (3 * v1, 3),
    (v1 * 3, 3),
    #
    (v1 / v2, 0.5),
    (v2 / 2, 1),
    (2 / v2, 1),
    #
    (v1 - v2, -1),
    (1 - v1, 0),
    (v1 - 1, 0),
    #
    (v1 > 2, False),
    (2 > v1, True),
    (v1 > v2, False),
    (v1 > v1, False),
    #
    (v1 >= 2, False),
    (2 >= v1, True),
    (v1 >= v2, False),
    (v1 >= v1, True),
    #
    (v1 < 2, True),
    (2 < v1, False),
    (v1 < v2, True),
    (v1 < v1, False),
    #
    (v1 <= 2, True),
    (2 <= v1, False),
    (v1 <= v2, True),
    (v1 <= v1, True),
    #
    ((v1 == 1) & (v2 == 2), True),
    ((v1 == 2) & (v2 == 2), False),
    ((v1 == 1) | (v2 == 2), True),
    ((v1 == 2) | (v2 == 2), True),
    ((v1 == 2) | (v2 == 1), False),
    #
    (T & T, True),
    (T & F, False),
    (F & T, False),
    (F & F, False),
    (False & F, False),
    #
    (T | T, True),
    (T | F, True),
    (F | T, True),
    (F | F, False),
    (False | F, False),
]


@pytest.mark.parametrize("expression, expected", cases)
def test_binary_expressions(eval_, expression, expected):
    assert eval_(expression._to_sql_expression()) == expected


def test_eval_exceptions(regtest):
    # correct would be (3 > v1) | (v1 > 3):
    with pytest.raises(ValueError) as e:
        e = 3 > v1 | v1 > 3
    print(e.value, file=regtest)


def test_in_range(regtest, t0):
    print(t0, file=regtest)
    print(t0.filter(t0.a.in_range(3, 5)), file=regtest)


def test_approx_equal(regtest, t0):
    print(t0, file=regtest)
    t0.add_column("bf", t0.apply(float, t0.b), float)
    print(t0.filter(t0.a.approx_equal(t0.bf, rtol=0, atol=1)), file=regtest)
    expr = t0.a.approx_equal(t0.bf, rtol=0.5, atol=0)
    print(t0.filter(expr), file=regtest)
