#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>
import importlib as _importlib
import os as _os
import sys as _sys

_PREFIX = "emzed_ext_"


def _find_extensions():
    import pkgutil

    extensions = [
        m for m in pkgutil.iter_modules() if m.ispkg and m.name.startswith(_PREFIX)
    ]

    ext_names = [e.name[len(_PREFIX) :] for e in extensions]
    return ext_names


_ext_names = _find_extensions()

__all__ = _ext_names


def __dir__():
    return _ext_names


# not setting it would trigger __getattr__
__path__ = [_os.path.dirname(__file__)]


class EmzedExtension:
    def __init__(self, name):
        self.__name = name
        self.__loaded = None

    def _load(self):
        self.__loaded = _sys.modules["emzed.ext." + self.__name] = (
            _importlib.import_module(_PREFIX + self.__name)
        )

    def __dir__(self):
        if self.__loaded is None:
            self._load()
        return dir(self.__loaded)

    def __getattr__(self, name):
        if self.__loaded is None:
            self._load()
        return getattr(self.__loaded, name)


_extensions = {}

for _ext_name in _ext_names:
    _extensions[_ext_name] = _sys.modules["emzed.ext." + _ext_name] = EmzedExtension(
        _ext_name
    )


def __getattr__(ext_name):
    if ext_name not in _ext_names:
        raise AttributeError(f"emzed.ext has no attribe {ext_name}")
    if "emzed.ext." + ext_name in _sys.modules:
        return _sys.modules["emzed.ext." + ext_name]
    return _extensions[ext_name]
