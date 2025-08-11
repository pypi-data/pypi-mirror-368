#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>

import ctypes
import glob
import os.path

import pyopenms

# use win32api module to extract version info from windows dll, see
# https://www.blog.pythonlibrary.org/2014/10/23/


def get_version_number(filename):
    from win32api import HIWORD, LOWORD, GetFileVersionInfo

    info = GetFileVersionInfo(filename, "\\")
    ms = info["FileVersionMS"]
    ls = info["FileVersionLS"]
    return HIWORD(ms), LOWORD(ms), HIWORD(ls), LOWORD(ls)


# we must make sure that the Qt5 dlls shipped with pyopenms have same versions as the
# dlls shipped with PyQ5.

# we install PyQt 5.9.2 in windows, which is surprisingly linked against Qt 5.9.3:
EXPECTED_VERSION_WIN = (5, 9, 3, 0)

EXPECTED_VERSION_LINUX = (5, 9, 4, 0)


def check_pyopenms_win32():
    folder = os.path.dirname(pyopenms.__file__)
    for p in glob.glob(os.path.join(folder, "Qt5*.dll")):
        version = get_version_number(p)
        if version != EXPECTED_VERSION_WIN:
            raise RuntimeError(
                "installation issue: pyopenms shipped with emzed should"
                " have version {}.{}.{} but has {}.{}.{}".format(
                    *EXPECTED_VERSION_WIN[:3], *version[:3]
                )
            )


def check_pyopenms_linux():
    folder = os.path.join(os.path.abspath(os.path.dirname(pyopenms.__file__)), ".libs")
    for p in glob.glob(os.path.join(folder, "libQt5Core*.so*")):  # noqa: B007
        break
    else:
        raise RuntimeError("do not find libQt5Core* within pyopenms")

    lib = ctypes.CDLL(p)
    lib.qVersion.restype = ctypes.c_char_p

    v_str = str(lib.qVersion(), "ascii")

    version = tuple(map(int, v_str.split(".")))
    if version != EXPECTED_VERSION_LINUX[:3]:
        raise RuntimeError(
            "installation issue: libQt5 shipped with pyopenms should"
            " have version {}.{}.{} but has {}.{}.{}".format(
                *EXPECTED_VERSION_LINUX[:3], *version
            )
        )
