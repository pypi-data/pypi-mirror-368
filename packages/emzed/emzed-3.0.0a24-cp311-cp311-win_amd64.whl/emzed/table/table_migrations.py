#!/usr/bin/env python

from emzed.core import DbBackedDictionary


def migrate(model, from_version, to_version):
    if to_version == (0, 0, 42):
        return migrate_to_0_0_42(model)
    return None


def migrate_to_0_0_42(model):
    print("migrate table to version 0.0.42")

    conn = model._conn
    schemata = conn.schemata
    for row in schemata.filter(schemata.type == "table"):
        table_name = row.name
        if table_name.startswith("spectra_"):
            ending = table_name.rsplit("_", 1)[-1]
            new_name = "peakmap_" + table_name.split("_", 1)[1]
            if ending not in ("meta", "info", "precursors"):
                new_name += "_spectra"
            rename_table(conn, table_name, new_name)
    info = DbBackedDictionary(model, "info")

    # circumvents issues with ImmutableTableModel:
    info._update(dict(__version__=(0, 0, 42)))
    model._unique_id = None
    return (0, 0, 42)


def rename_table(conn, from_name, to_name):
    print("rename", from_name, to_name)
    conn.execute(f"ALTER TABLE {from_name} RENAME TO {to_name}")
    conn.commit()
