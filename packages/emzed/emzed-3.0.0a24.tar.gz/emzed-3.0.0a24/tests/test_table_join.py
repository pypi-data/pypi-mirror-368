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


from emzed.table.join import fix_names_right


def test_fix_names_right(regtest):
    for left in [
        ["a", "b", "c"],
        ["a__0", "b", "c"],
        ["a__0", "b__0", "c"],
        ["a__0", "b__0", "c__0"],
        ["a__1", "b__0", "c__0"],
        ["a__1", "b__2", "c__0"],
        ["a__1", "b__2", "c__3"],
    ]:
        for right in [
            ["d", "e", "f"],
            ["a", "e", "f"],
            ["a", "b", "f"],
            ["a", "b", "c"],
            ["a__0", "b", "c"],
            ["a__0", "b__1", "c"],
            ["a__0", "b__1", "c__2"],
        ]:
            print(left, right, "->", fix_names_right(left, right), file=regtest)

        print(file=regtest)


def test_fast_join(regtest, t0):
    print(t0, file=regtest)
    t1 = t0.copy()

    t2 = t0.fast_join(t1, "a", atol=1.0, rtol=0)
    print(t2, file=regtest)

    t2 = t0.fast_join(t1, "a", atol=0, rtol=1.5)
    print(t2, file=regtest)


def test_fast_left_join(regtest, t0):
    print(t0, file=regtest)
    t1 = t0.copy()

    t2 = t0.fast_left_join(t1, "a", atol=1.0, rtol=0)
    print(t2, file=regtest)

    t2 = t0.fast_left_join(t1, "a", atol=0, rtol=1.5)
    print(t2, file=regtest)


def test_left_join(regtest, t0):
    t1 = t0.copy()
    t2 = t0.join(t1, t0.a == t1.a)
    print(t2, file=regtest)

    t2 = t0.left_join(t1, t0.a == t1.a)
    print(t2, file=regtest)


def test_fast_join_atol_zero(regtest, t0):
    t1 = t0.copy()

    t2 = t0.fast_left_join(t1, "a", atol=0.0, rtol=0.0)
    print(t2, file=regtest)
