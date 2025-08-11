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


import abc
import os
import sys


class _FolderLocationBase:
    def get_emzed_folder(self):
        folder = os.path.join(self.get_app_data_folder(), "emzed3")
        if not os.path.exists(folder):
            os.makedirs(folder)
        return folder

    @abc.abstractmethod
    def get_document_folder(self): ...

    @abc.abstractmethod
    def get_app_data_folder(self): ...

    @abc.abstractmethod
    def get_local_appdata_folder(self): ...


class _FolderLocationsLinux(_FolderLocationBase):
    def __init__(self):
        self._home = os.environ.get("HOME")
        if self._home is None:
            raise RuntimeError("$HOME not set")

    def get_document_folder(self):
        return self._home

    get_app_data_folder = get_local_appdata_folder = get_document_folder

    def get_emzed_folder(self):
        folder = os.path.join(self._home, ".emzed3")
        if not os.path.exists(folder):
            os.makedirs(folder)
        return folder


_FolderLocationsMacOs = _FolderLocationsLinux


class _FolderLocationsWindows(_FolderLocationBase):
    def __init__(self):
        import winreg

        self._winreg = winreg

        self.key = self._winreg.OpenKey(
            self._winreg.HKEY_CURRENT_USER,
            "Software\\Microsoft\\Windows\\CurrentVersion"
            "\\Explorer\\User Shell Folders",
        )

    def _query(self, sub_key):
        val, _ = self._winreg.QueryValueEx(self.key, sub_key)
        return self._winreg.ExpandEnvironmentStrings(val)

    def get_document_folder(self):
        return self._query("Personal")

    def get_app_data_folder(self):
        return self._query("AppData")

    def get_local_appdata_folder(self):
        return self._query("Local AppData")


if sys.platform == "win32":
    folders = _FolderLocationsWindows()
elif sys.platform == "darwin":
    folders = _FolderLocationsMacOs()
else:
    folders = _FolderLocationsLinux()
