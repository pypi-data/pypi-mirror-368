#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>


from ..utils.sqlite import Connection, create_uid
from .full_table_model import FullTableModel
from .table_utils import create_db_table


def collapse(model, group_col_names, new_col_name, path):
    from .table import Table

    group_col_types, group_col_formats = unzip(
        [
            (col_type, col_format)
            for (col_name, col_type, col_format) in zip(
                model.col_names, model.col_types, model.col_formats
            )
            if col_name in group_col_names
        ]
    )

    remaining_col_names, remaining_col_types, remaining_col_formats = unzip(
        [
            (col_name, col_type, col_format)
            for (col_name, col_type, col_format) in zip(
                model.col_names, model.col_types, model.col_formats
            )
            if col_name not in group_col_names
        ]
    )

    result_col_names = group_col_names + (new_col_name,)
    result_col_types = group_col_types + (Table,)
    result_col_formats = group_col_formats + ("%r",)

    new_conn = Connection(path)
    new_table_col_name_mapping = create_db_table(
        new_conn, "data", result_col_names, result_col_types
    )
    result_model = FullTableModel(
        new_conn,
        "data",
        result_col_names,
        result_col_types,
        result_col_formats,
        "",
        new_table_col_name_mapping,
    )

    db_col_names = [
        model.col_name_mapping[col_name]
        for col_name in group_col_names + remaining_col_names
    ]

    n = len(group_col_names)
    cols = ", ".join(db_col_names[:n])
    sub_cols = ", ".join(db_col_names[n:])

    access_name = model._access_name
    for group_values in model._conn.execute(
        f"SELECT DISTINCT {cols} from {access_name}"
    ):
        sub_access_name = model._access_name + "_collapse_" + create_uid()
        col_name_mapping = create_db_table(
            model._conn, sub_access_name, remaining_col_names, remaining_col_types
        )

        new_cols = ", ".join(col_name_mapping[name] for name in remaining_col_names)

        expression = " AND ".join(
            f"{db_col} = {v}" for (db_col, v) in zip(db_col_names[:n], group_values)
        )

        model._conn.execute(
            f"INSERT INTO {sub_access_name} ({new_cols}) SELECT {sub_cols}"
            f" FROM {access_name} WHERE {expression}"
        )
        model._conn.commit()

        sub_table_model = FullTableModel(
            model._conn,
            sub_access_name,
            remaining_col_names,
            remaining_col_types,
            remaining_col_formats,
            "",
            col_name_mapping,
        )
        result_model.add_row(group_values + (Table(sub_table_model),))

    return Table(result_model)


def unzip(list_of_tuples):
    if not list_of_tuples:
        return []
    return zip(*list_of_tuples)
