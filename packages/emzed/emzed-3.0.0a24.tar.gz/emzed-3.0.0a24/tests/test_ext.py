#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>


def test_empty_all():
    # as extension testing is done within extensions there should not be an extension
    # installed here

    import emzed.ext

    assert emzed.ext.__all__ == []


def test_empty_dir():
    # as extension testing is done within extensions there should not be an extension
    # installed here

    import emzed.ext

    assert dir(emzed.ext) == []
