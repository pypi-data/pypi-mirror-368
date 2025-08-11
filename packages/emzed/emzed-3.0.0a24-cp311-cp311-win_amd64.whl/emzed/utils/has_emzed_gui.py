#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>


import sys
from contextlib import contextmanager


def has_emzed_gui():
    try:
        import emzed_gui  # noqa: F401

        return True
    except ModuleNotFoundError:
        return False


@contextmanager
def mock_emzed_gui():
    assert "emzed_gui" not in sys.modules, "emzed_gui is already installed"

    class emzed_gui:
        pass

    sys.modules["emzed_gui"] = emzed_gui

    try:
        yield emzed_gui
    finally:
        del sys.modules["emzed_gui"]
