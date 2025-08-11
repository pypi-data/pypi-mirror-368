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


from emzed import PeakMap, to_table
from emzed.ms_data import ImmutablePeakMap


def test_extract_immutable_peakmap(pm):
    t = to_table("pm", [pm], PeakMap)

    pmi = t[0].pm
    assert isinstance(pmi, ImmutablePeakMap)
    assert not isinstance(pmi, PeakMap)

    rtmin, rtmax = pmi.rt_range()
    assert rtmin >= pm.rt_range()[0]
    assert rtmax <= pm.rt_range()[1]

    pm_e = pmi.extract(rtmin=0, rtmax=10, mslevelmin=2)
    assert len(pm_e) == 0

    pm_e = pmi.extract(rtmin=0, rtmax=10, mslevelmax=1)
    assert len(pm_e) == 599

    rtmin, rtmax = pm_e.rt_range()
    assert rtmin >= 0
    assert rtmax <= 10
