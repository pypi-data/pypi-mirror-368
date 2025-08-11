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


if True:  # avoids resorting by Isort, if we change order we run into circulare imports:
    import sys as _sys

    if _sys.platform == "linux":
        # importing matplotlib crashes on linux, this hack avoids this:
        import ctypes

        try:
            _dll = ctypes.CDLL("libgcc_s.so.1")
        except OSError:
            pass
    elif _sys.platform == "win32":
        # guess suitable matplotlib backend
        try:
            import tkinter as _tk  # noqa: F401

            del _tk  # keep namespace tidy
            # tikinter is default backend for matplotlib, so
            # we don't set anything here.
        except ImportError:
            # tkinter is missing on some windows Python distributions
            try:
                # reasonable alternative backend
                import matplotlib
                import PyQt5  # noqa: F401

                matplotlib.use("qt5agg")
            except ImportError:
                # let user decide later what to use
                pass


from importlib.metadata import version as _version

# disable isort, import order matters to avoid cirular imports below
# isort: off

# next module has top level code which imports pyopenms including some fixes /
# preparations because of linkage issues:
from .pyopenms import pyopenms  # noqa: F401
from . import ms_data as _msdata  # noqa: F401
from . import quantification  # noqa F401
from . import peak_picking  # noqa F401
from .peak_picking import extract_chromatograms  # noqa: F401
from .peak_picking import extract_ms_chromatograms  # noqa: F401
from .peak_picking import run_feature_finder_metabo  # noqa: F401
from .peak_picking import run_feature_finder_metabo_on_folder  # noqa: F401
from .table import Table, to_table  # noqa F401
from .table.table_utils import MzType, RtType  # noqa F401

PeakMap = _msdata.PeakMap
Spectrum = _msdata.Spectrum
MSChromatogram = _msdata.MSChromatogram

from . import align  # noqa: F401,E402
from . import io  # noqa: F401,E402
from .chemistry import abundance, adducts, elements, mass  # noqa: F401,E402
from .chemistry import MolecularFormula as mf  # noqa: F401,E402
from . import chemistry  # noqa: F401,E402
from . import db  # noqa: F401,E402
from . import ext  # noqa: F401,E402
from . import targeted  # noqa: F401,E402
from . import ms2  # noqa: F401,E402
from . import annotate  # noqa: F401,E402

# isort: on


def __dir__():
    return [
        "MzType",
        "PeakMap",
        "RtType",
        "Spectrum",
        "Table",
        "abundance",
        "adducts",
        "align",
        "annotate",
        "chemistry",
        "db",
        "elements",
        "ext",
        "gui",
        "io",
        "mass",
        "mf",
        "ms2",
        "peak_picking",
        "quantification",
        "run_feature_finder_metabo",
        "run_feature_finder_metabo_on_folder",
        "targeted",
        "to_table",
    ]


try:
    profile
except NameError:
    __builtins__["profile"] = lambda x: x


if _sys.platform == "win32":
    from .check_pyopenms import check_pyopenms_win32 as _check

    _check
    del check_pyopenms  # noqa: F821


elif _sys.platform == "linux":
    from .check_pyopenms import check_pyopenms_linux as _check

    _check
    del check_pyopenms  # noqa: F821


__version__ = _version(__package__)

__all__ = __dir__()


def __getattr__(name):
    if name == "gui":
        import emzed.gui

        return emzed.gui
    raise AttributeError(f"module {name} does not exist.")
