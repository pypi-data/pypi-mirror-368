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


import numpy as np
import pytest

from emzed import to_table
from emzed.table.expressions import Value


@pytest.fixture
def t0():
    t = to_table("a", [1, 2, None, 3], int)
    t.add_column("b", t.a * 11.11, float)
    yield t


def test_comparison(regtest, t0):
    def check(expr):
        print(repr(expr), file=regtest)
        print(t0.filter(expr), file=regtest)
        print(file=regtest)

    check(t0.a < 1)
    check(t0.a < 3)
    check(t0.a <= 3)

    check(t0.a > 1)
    check(t0.a > 3)
    check(t0.a >= 3)


def test_value():
    for value in (None, 1, 1.0, False, "abc"):
        assert Value(value).value == value

    assert Value(np.float64(1.23)).value == 1.23
    assert Value(np.array([1.23])).value == 1.23
    assert Value(np.array([[1.23]])).value == 1.23

    for value in ((1, 2), {}, b"", bool, np.array([""])):
        with pytest.raises(TypeError):
            Value((1, 2))

    with pytest.raises(ValueError):
        Value(np.array([1, 2]))
