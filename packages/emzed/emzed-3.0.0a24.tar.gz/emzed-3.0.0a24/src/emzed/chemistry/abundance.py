#!/usr/bin/env python

_loaded = {}


def __getattr__(name):
    # mimics lazy import
    if not _loaded:
        from .elements import load_elements

        _, _, abundance_dict, _ = load_elements()
        _loaded.update(abundance_dict)
    return _loaded[name]


def __dir__():
    """forward attributes for autocompletion"""
    return list(_loaded.keys())
