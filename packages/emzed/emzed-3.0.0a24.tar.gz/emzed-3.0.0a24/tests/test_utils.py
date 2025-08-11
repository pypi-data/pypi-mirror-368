#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>


from emzed.utils import has_emzed_gui, mock_emzed_gui


def test_emzed_gui_mock():
    assert not has_emzed_gui()

    with mock_emzed_gui() as emzed_gui:
        assert has_emzed_gui()
        emzed_gui.ask_for_single_file = lambda *a: "hi there"

        from emzed_gui import ask_for_single_file

        assert ask_for_single_file() == "hi there"

    assert not has_emzed_gui()
