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

import dill
import numpy as np


def md5_hexdigest(*args):
    hasher = hashlib.md5()
    for arg in args:
        if isinstance(arg, (int, bool, float, str)):
            arg = str(arg).encode("utf-8")
        elif isinstance(arg, np.ndarray):
            arg = bytes(arg.data)
        else:
            arg = dill.dumps(arg, protocol=4)
        hasher.update(arg)
    return hasher.hexdigest()
