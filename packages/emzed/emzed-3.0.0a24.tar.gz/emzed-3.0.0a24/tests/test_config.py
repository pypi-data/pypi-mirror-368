#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>


def test_folders():
    from emzed.config import folders

    print(folders.get_document_folder())
    print(folders.get_app_data_folder())
    print(folders.get_local_appdata_folder())
