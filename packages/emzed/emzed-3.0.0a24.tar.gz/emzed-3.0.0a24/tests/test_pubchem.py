#!/usr/bin/env python

import os

import pytest

from emzed.config import folders


@pytest.fixture
def patch_emzed_folder(monkeypatch, tmpdir):
    folder = tmpdir.join("emzed3").strpath
    os.makedirs(folder)
    monkeypatch.setattr(folders, "get_emzed_folder", lambda: folder)


def test_pubchem(patch_emzed_folder, regtest):
    import emzed.db

    with pytest.raises(OSError) as e:
        emzed.db.pubchem
    assert e.value.args[0] == "please run emzed.db.update_pubchem() first"

    if os.environ.get("CI") is not None:
        emzed.db.update_pubchem()
        assert len(emzed.db.pubchem) > 0
        assert emzed.db.pubchem.col_names == (
            "cid",
            "mw",
            "m0",
            "mf",
            "iupac",
            "synonyms",
            "inchi",
            "inchikey",
            "smiles",
            "is_in_kegg",
            "is_in_hmdb",
            "is_in_biocyc",
            "url",
        )
