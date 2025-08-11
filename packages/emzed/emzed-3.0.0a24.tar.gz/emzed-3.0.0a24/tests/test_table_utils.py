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


from emzed import MzType, RtType, Table
from emzed.table.table_utils import guess_col_format


def test_print_table(regtest):
    t = Table.create_table(
        ["string", "float", "integer", "boolean", "mz", "rt"],
        [str, float, int, bool, MzType, RtType],
    )

    for i in range(12):
        t.add_row((i * str(i), i + 1.23, i + 123, i % 2 == 0, i + 123.1234, i + 66))

    t.print_(max_rows=8, stream=regtest)
    print(file=regtest)
    t.print_(max_rows=9, stream=regtest)
    print(file=regtest)
    t.print_(max_rows=10, stream=regtest)
    print(file=regtest)
    t.print_(max_rows=10, max_col_width=12, stream=regtest)


def test_guess_col_format():
    assert guess_col_format("abc", float) == "%f"
    assert guess_col_format("abc", int) == "%d"
    assert guess_col_format("abc", bool)(1) == "True"
    assert guess_col_format("abc", bool)(0) == "False"
    assert guess_col_format("abc", bool)(None) == "-"
    assert guess_col_format("abc", str) == "%s"

    assert guess_col_format("mz", float) == "%11.6f"
    assert guess_col_format("rt", float)(None) == "-"
    assert guess_col_format("rt", float)(120) == "  2.00 m"

    assert guess_col_format("abc", RtType)(None) == "-"
    assert guess_col_format("abc", RtType)(120) == "  2.00 m"

    assert guess_col_format("mz", float) == "%11.6f"
