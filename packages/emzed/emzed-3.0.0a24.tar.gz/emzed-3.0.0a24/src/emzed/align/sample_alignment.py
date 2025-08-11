#!/usr/bin/env python

import warnings

from emzed import Table


def align_peaks(tables, mz_tol, rt_tol):
    """
    Assigns global peak ids over samples sucht that peaks which differ by
    given tolerances are are assigned to the sampe global peak id.

    Tables are modified in-place by adding a new columns ``global_peak_id``.

    :param tables: list or tuple of peak tables with columns "id", "mz" and "rt" at
                   least.
    :param mz_tol: mz tolerance in Da.
    :param rt_tol: rt tolerance in seconds.

    :returns: None
    """

    _check_tables(tables)

    feature_maps, count, max_id = _build_feature_maps(tables)
    print("number of total peaks     :", count)

    consensus_map = _compute_consensus_map(feature_maps, mz_tol, rt_tol)
    print("number of global peaks ids:", consensus_map.size())

    _assign_global_peak_ids(tables, consensus_map, max_id)


def _check_tables(tables):
    assert isinstance(tables, (list, tuple)), "tables parameter must be list or tuple"

    assert len(tables) > 0, "input tables list (resp. tuple) is empty"

    assert all(
        isinstance(t, Table) for t in tables
    ), "table parameter must contain tables only"

    for i, table in enumerate(tables):
        if "global_peak_id" in table.col_names:
            warnings.warn(
                f"table at position {i} of tables argument already has column"
                " global_peak_id"
            )

    for i, table in enumerate(tables):
        table._ensure_col_names("id", "mz", "rt")


def _build_feature_maps(tables):
    from pyopenms import Feature, FeatureMap

    feature_maps = []
    count = 0

    max_id = max(max(t.id) for t in tables)

    for i, table in enumerate(tables):
        fm = FeatureMap()
        for row in table:
            feature = Feature()
            feature.setMZ(float(row.mz))
            feature.setRT(float(row.rt))
            feature.setUniqueId(i * (max_id + 1) + row.id)
            fm.push_back(feature)
            count += 1
        fm.updateRanges()
        feature_maps.append(fm)
    return feature_maps, count, max_id


def _compute_consensus_map(feature_maps, mz_tol, rt_tol):
    from pyopenms import ConsensusMap, QTClusterFinder

    consensus_map = ConsensusMap()
    finder = QTClusterFinder()

    p = finder.getParameters()
    p.setValue("distance_RT:max_difference", float(rt_tol))
    p.setValue("distance_MZ:max_difference", float(mz_tol))
    p.setValue("distance_RT:exponent", 2.0)
    p.setValue("distance_MZ:exponent", 2.0)
    finder.setParameters(p)

    finder.run(feature_maps, consensus_map)
    return consensus_map


def _assign_global_peak_ids(tables, consensus_map, max_id):
    global_peak_ids = [dict() for _ in range(len(tables))]

    for global_peak_id, consensus_feature in enumerate(consensus_map):
        for feature in consensus_feature.getFeatureList():
            map_index = feature.getMapIndex()
            local_id = feature.getUniqueId() % (max_id + 1)
            global_peak_ids[map_index][local_id] = global_peak_id

    for i, table in enumerate(tables):
        if "global_peak_id" in table.col_names:
            table.replace_column(
                "global_peak_id",
                table.apply(global_peak_ids[i].get, table.id),
                int,
            )
        else:
            table.add_column(
                "global_peak_id",
                table.apply(global_peak_ids[i].get, table.id),
                int,
                insert_after="id",
            )
