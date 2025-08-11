#!/usr/bin/env python

from collections import defaultdict

import numpy as np

from emzed import MzType, Table, mass, to_table
from emzed.chemistry import compute_centroids
from emzed.utils import NeighbourSearch, temp_file_path


def annotate_adducts(peaks, adducts, mz_tol, rt_tol, explained_abundance=0.20):
    """
    attempts to group peaks as adducts.

    required column names are `mz` and `rt` only. all other columns will be ignored.
    """

    _check_col_names(peaks)
    peaks.add_enumeration("_id")

    invalid = peaks.filter(peaks.mz.is_none() | peaks.rt.is_none())
    valid = peaks.filter(peaks.mz.is_not_none() & peaks.rt.is_not_none())

    adducts_isotopes = _build_adducts_isotopes(adducts, explained_abundance)

    rt_windows = _find_rt_windows(valid, rt_tol)

    print(f"found {len(rt_windows) - 1} gaps > rt_tol in rt values")
    print()

    adduct_cluster_id_offset = 0
    partial_results = []

    for i, (rtmin, rtmax) in enumerate(rt_windows):
        print(f"process {i + 1} out of {len(rt_windows)}")
        partial_result, adduct_cluster_id_offset = _process(
            valid,
            rtmin,
            rtmax,
            adduct_cluster_id_offset,
            adducts_isotopes,
            mz_tol,
            rt_tol,
        )
        partial_results.append(partial_result)
        print()

    invalid.add_column_with_constant_value("adduct_name", None, str)
    invalid.add_column_with_constant_value("adduct_isotopes", None, str)
    invalid.add_column_with_constant_value("adduct_isotopes_abundance", None, float)
    invalid.add_column_with_constant_value("adduct_m0", None, MzType)
    invalid.add_column_with_constant_value("adduct_cluster_id", None, int)
    result = Table.stack_tables([invalid] + partial_results).sort_by("_id")
    result.drop_columns("_id")
    peaks.drop_columns("_id")
    return result


def _check_col_names(peaks):
    forbidden_col_names = [
        "adduct_name",
        "adduct_cluster_id",
        "adduct_isotopes",
        "adduct_isotopes_abundance",
        "adduct_m0",
    ]

    overlapping = set(forbidden_col_names) & set(peaks.col_names)
    if overlapping:
        raise ValueError(
            "columns names {} not allowed".format(", ".join(sorted(overlapping)))
        )

    peaks._ensure_col_names("rt", "mz")


def _find_rt_windows(peaks, rt_tol):
    rts = np.array(sorted(peaks.rt))
    gaps = rts[1:] - rts[:-1]
    gap_positions = np.where(gaps > rt_tol)[0]
    rtmin = rtmax = 0
    windows = []
    for position in gap_positions:
        rtmax = rts[position]
        windows.append((rtmin, rtmax))
        rtmin = rtmax + rt_tol
    windows.append((rtmin, max(rts) + 1))
    return windows


def _process(
    peaks, rtmin, rtmax, adduct_cluster_id_offset, adducts_isotopes, mz_tol, rt_tol
):
    p = peaks.filter((peaks.rt >= rtmin) & (peaks.rt <= rtmax))
    print(f"    process {len(p)} peaks in rt range {rtmin:.1f}..{rtmax:.1f}")
    partial_result = _annotate(p, adducts_isotopes, mz_tol, rt_tol)

    if len(partial_result):
        max_adduct_id = partial_result.adduct_cluster_id.max().eval()

        partial_result.replace_column(
            "adduct_cluster_id",
            partial_result.adduct_cluster_id + adduct_cluster_id_offset,
        )

        at_least_one_cluster_found = max_adduct_id is not None
        if at_least_one_cluster_found:
            adduct_cluster_id_offset += max_adduct_id + 1

    return partial_result, adduct_cluster_id_offset


def _annotate(peaks, adducts_isotopes, mz_tol, rt_tol):
    peaks.add_enumeration("_peak_id")
    peaks_sub = peaks.extract_columns("_peak_id", "mz", "rt", keep_view=True)

    with temp_file_path() as path:
        psa = peaks_sub.join(adducts_isotopes, path=path)
        psa.add_enumeration("_id")

        psa.rename_postfixes(__0="")

        psa.add_column(
            "m0",
            (psa.mz * psa.adduct_z + psa.adduct_sign_z * mass.e - psa.adducts_mass_diff)
            / psa.adduct_m_multiplier,
            MzType,
        )

        ids, connections = _find_matches(psa, mz_tol, rt_tol)
        psa_filtered = psa.filter(psa._id.is_in(ids))
        annotations = _build_annotations_table(ids, psa_filtered)

    id_to_cluster_id = _find_clusters(connections)
    annotations.add_column(
        "adduct_cluster_id",
        annotations.apply(id_to_cluster_id.get, annotations.id),
        int,
    )

    annotations.drop_columns("id")

    result = peaks.left_join(annotations, peaks._peak_id == annotations.peak_id)
    result = result.sort_by("_peak_id", "adduct_cluster_id__0")

    # remove clusters which contain only the same peak multiple times:
    result.add_column(
        "_peak_id_std",
        result.group_by(result.adduct_cluster_id__0).std(result._peak_id),
        float,
    )
    result = result.filter(result._peak_id_std > 0)
    result.drop_columns("_peak_id", "peak_id__0", "_peak_id_std")
    result.rename_postfixes(__0="")
    return result


def _build_adducts_isotopes(adducts, explained_abundance):
    t_empty = Table.create_table(
        ["m0", "mf", "abundance"], [MzType, str, float], rows=[[0.0, "", 1.0]]
    )

    rows = []

    for adduct in adducts:
        isotope_id = 0
        if adduct.adduct_add != "":
            t_add = compute_centroids(adduct.adduct_add, explained_abundance)
        else:
            t_add = t_empty
        if adduct.adduct_sub != "":
            t_sub = compute_centroids(adduct.adduct_sub, explained_abundance)
        else:
            t_sub = t_empty

        for ti_add in t_add:
            for ti_sub in t_sub:
                if ti_add.mf:
                    isotope_description = f"+{ti_add.mf} -{ti_sub.mf}".rstrip("- ")
                else:
                    isotope_description = f"-{ti_sub.mf}".rstrip("- ")
                row = [
                    adduct.id,
                    adduct.adduct_name,
                    adduct.z,
                    adduct.sign_z,
                    adduct.m_multiplier,
                    isotope_id,
                    isotope_description,
                    ti_add.abundance * ti_sub.abundance,
                    ti_add.m0 - ti_sub.m0,
                ]
                rows.append(row)
                isotope_id += 1

    adducts_isotopes = Table.create_table(
        [
            "adduct_id",
            "adduct_name",
            "adduct_z",
            "adduct_sign_z",
            "adduct_m_multiplier",
            "adduct_isotopes_id",
            "adduct_isotopes",
            "adduct_isotopes_abundance",
            "adducts_mass_diff",
        ],
        [int, str, int, int, int, int, str, float, MzType],
        rows=rows,
    )
    adducts_isotopes.set_col_format("adduct_isotopes_abundance", "%.3f")
    return adducts_isotopes


def _find_matches(psa, mz_tol, rt_tol):
    for_match = psa.extract_columns("_id", "rt", "m0")
    df = for_match.to_pandas()
    data = df.iloc[:, 1:].values
    print("    build up lookup table")
    lookup = NeighbourSearch(data, np.array([rt_tol, mz_tol]))

    connections = []
    print("    look for matches")

    for id_, row in enumerate(data):
        for match_id in lookup.find_matches(id_, row):
            connections.append((id_, match_id))

    print("    found matches")

    ids = set(i0 for (i0, i1) in connections)
    ids |= set(i1 for (i0, i1) in connections)
    return ids, connections


def _build_annotations_table(ids, psa_filtered):
    annotations = to_table("id", ids, int)

    annotations.add_column(
        "peak_id", annotations.id.lookup(psa_filtered._id, psa_filtered._peak_id), int
    )

    annotations.add_column(
        "adduct_name",
        annotations.id.lookup(psa_filtered._id, psa_filtered.adduct_name),
        str,
    )

    annotations.add_column(
        "adduct_isotopes",
        annotations.id.lookup(psa_filtered._id, psa_filtered.adduct_isotopes),
        str,
    )
    annotations.add_column(
        "adduct_isotopes_abundance",
        annotations.id.lookup(psa_filtered._id, psa_filtered.adduct_isotopes_abundance),
        float,
        "%3.f",
    )

    annotations.add_column(
        "adduct_m0", annotations.id.lookup(psa_filtered._id, psa_filtered.m0), MzType
    )
    return annotations


def _find_clusters(connections):
    graph = _build_undirected_graph(connections)
    components = _find_components(graph)
    return _build_id_to_cluster_id(components)


def _build_undirected_graph(connections):
    graph = defaultdict(list)

    for node_0, node_1 in connections:
        graph[node_0].append(node_1)
        graph[node_1].append(node_0)
    return graph


def _find_components(graph):
    components = []
    seen = set()
    for start_node in graph:
        if start_node in seen:
            continue
        component = set()
        _depth_first_search(graph, start_node, component)
        seen.update(component)
        components.append(component)

    return components


def _depth_first_search(graph, node, visited_nodes):
    if node in visited_nodes:
        return
    visited_nodes.add(node)
    for next_node in graph[node]:
        _depth_first_search(graph, next_node, visited_nodes)


def _build_id_to_cluster_id(components):
    id_to_cluster_id = dict()
    cluster_id = 0
    for component in components:
        for id_ in component:
            id_to_cluster_id[id_] = cluster_id
        cluster_id += 1
    return id_to_cluster_id
