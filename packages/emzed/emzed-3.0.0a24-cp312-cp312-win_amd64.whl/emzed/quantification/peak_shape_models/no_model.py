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


from .base import PeakShapeModelBase


class NoModel(PeakShapeModelBase):
    __slots__ = []

    model_name = "no_integration"

    # singleton pattern
    _instance = None

    def __init__(self):
        pass

    def _getstate(self):
        return None

    def _setstate(self, data):
        pass

    @property
    def is_valid(self):
        return None

    @classmethod
    def fit(clz, *args, **kwargs):
        return clz._fit(None, None, None)

    @classmethod
    def fit_chromatogram(clz, *args, **kwargs):
        return clz._fit(None, None, None)

    @classmethod
    def _fit(clz, rts, intensities, extra_args):
        if clz._instance is None:
            clz._instance = clz()
        return clz._instance

    def graph(self):
        return [], []

    def apply(self, rts):
        return None

    @property
    def area(self):
        return None

    @property
    def rmse(self):
        return None
