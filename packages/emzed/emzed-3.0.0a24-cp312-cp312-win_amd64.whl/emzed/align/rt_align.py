#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>

import os.path

import matplotlib.pyplot as plt
import numpy as np
import pyopenms

from emzed.table.table import Table
from emzed.table.table_utils import RtType, to_openms_feature_map


def rt_align(
    tables,
    reference_table=None,
    destination=None,
    reset_integration=False,
    n_peaks=-1,
    max_rt_difference=100,
    max_mz_difference=0.3,
    max_mz_difference_pair_finder=0.5,
    model="b_spline",
    **model_parameters,
):
    """aligns feature tables in respect to retention times.
    the algorithm returns new tables with aligned data.

    :param reference_table: extra reference table, if *None* the table
                  with most features among *tables* is taken.

    :param destination: target folder for quality plots. If this value is `None`
             no plots will be created.

    :param reset_integration: sets integration related column names to `None` if
                  present. Else the alignment will fail for already integrated
                  tables.

    :param n_peaks: max number of peaks matched by superimposer, -1
                  means: all peaks, can be float between 0 and 1 to refer to
                  fraction of peaks in reference table.

    :param max_rt_difference: max allowed difference in rt values for
                  searching matching features.

    :param max_mz_difference: max allowed difference in mz values for
                  super imposer.

    :param max_mz_difference_pair_finder: max allowed difference in mz values
                  for pair finding.

    :param model: can be "b_spline" or "lowess"

    :param model_parameters: key word parameters depending on provided value for
                 'model'. For 'b_spline' the user can set

                  - num_nodes: number of break points of fitted spline.
                                   default:5, more points result in splines with higher
                                   variation.

                 For 'lowess' the parameters are:

                 - span: value between 0 and 1, larger values lead to more smoothing.
                    default is 2/3.
                 - interpolation_type: either "cspline" or "linear"

    :returns: aligned peak tables.
    """

    _check_args(reference_table, tables, reset_integration, model)
    model_parameters = _check_and_set_defaults(model, model_parameters)

    assert destination is None or isinstance(destination, str)
    if destination is not None:
        destination = os.path.abspath(destination)
        assert os.path.exists(destination) and os.path.isdir(
            destination
        ), f"folder {destination} does not exist"

    # convert to pyOpenMS types and find map with max num features which is taken as
    # refamp:
    feature_maps = [to_openms_feature_map(table) for table in tables]
    if reference_table is None:
        reference_map = max(feature_maps, key=lambda feature_map: feature_map.size())
        idx = feature_maps.index(reference_map)
        reference_table = tables[idx]
        print(
            "reference_map is",
            os.path.basename(reference_table.meta_data.get("source", "<noname>")),
        )
    else:
        if reference_table in tables:
            reference_map = feature_maps[tables.index(reference_table)]
        else:
            reference_map = to_openms_feature_map(reference_table)

    if isinstance(n_peaks, float):
        assert 0 < n_peaks <= 1.0, "need relative value if you use float for n_peaks"
        n_peaks = int(len(reference_table) * n_peaks)

    algorithm = _setup_algorithm(
        n_peaks, max_mz_difference_pair_finder, max_rt_difference, max_mz_difference
    )

    aligned_tables = []
    for feature_map, table in zip(feature_maps, tables):
        if feature_map is reference_map:
            aligned_tables.append(table)
            continue
        aligned_table = _align(
            table,
            feature_map,
            reference_map,
            model,
            model_parameters,
            destination,
            algorithm,
        )
        aligned_tables.append(aligned_table)

    for table in aligned_tables:
        table.meta_data["rt_aligned"] = True

    return aligned_tables


def _check_args(reference_table, tables, reset_integration, model):
    assert reference_table is None or isinstance(reference_table, Table)

    integration_columns = ("peak_shape_model", "area", "rmse", "valid_model")

    found_integrated = False
    for t in tables:
        if all(n in t.col_names for n in integration_columns):
            found_integrated = True
            break

    if found_integrated and not reset_integration:
        raise ValueError(
            "one ot the tables to align is integrated which will turn invalid "
            "after alignment. Either remove the integration columns, or set\n"
            "parameter reset_integration to True"
        )

    if found_integrated and reset_integration:
        for t in tables:
            if all(n in t.col_names for n in integration_columns):
                for n in integration_columns:
                    t.replace_column_with_constant_value(n, None)

    for table in tables:
        _check_table(table)

    if reference_table is not None:
        _check_table(reference_table)

    if model not in ("b_spline", "lowess"):
        raise ValueError("model must be either 'b_spline' or 'lowess'")


def _check_and_set_defaults(model, model_parameters):
    if model == "b_spline":
        return _check_and_set_default_bspline_model(model_parameters)
    else:
        return _check_and_set_default_lowess_model(model_parameters)


def _check_and_set_default_bspline_model(model_parameters):
    param = pyopenms.Param()

    # workaround bug in pyopenms >= 2.6, method getDefaultParameters is not static
    # anymore, so we need a "fake" instance of TransformationModelBSpline to retrieve
    # default settings
    points = [pyopenms.TM_DataPoint(i, i) for i in (1.0, 2.0, 3.0)]

    pyopenms.TransformationModelBSpline(points, param).getDefaultParameters(param)

    if not model_parameters:
        return param

    unknown = model_parameters.keys() - set(("num_nodes",))
    if unknown:
        unknown = ", ".join(sorted(unknown))
        raise ValueError(f"unknown parameter(s) {unknown} for for b_spline model.")

    num_nodes = model_parameters["num_nodes"]

    if not isinstance(num_nodes, int):
        raise ValueError("num_nodes must be an integer number")
    if num_nodes < 0:
        raise ValueError("negative value not allowed for num_nodes")

    param.setValue("num_nodes", num_nodes)
    return param


def _check_and_set_default_lowess_model(model_parameters):
    param = pyopenms.Param()

    # getDefaultParameters is not avail as static method of TransformationModelLowess
    param.setValue("span", 2.0 / 3)
    param.setValue("num_iterations", 3)
    param.setValue("delta", -1.0)
    param.setValue("interpolation_type", b"cspline")
    param.setValue("extrapolation_type", b"four-point-linear")

    unknown = model_parameters.keys() - set(("span", "interpolation_type"))
    if unknown:
        unknown = ", ".join(sorted(unknown))
        raise ValueError(f"unknown parameter(s) {unknown} for lowess  model.")

    span = model_parameters.get("span")
    if span is not None:
        if not isinstance(span, float):
            raise ValueError("span must be a float number")
        if not 0 < span <= 1.0:
            raise ValueError("span must be > 0 and <= 1.0")

        param.setValue("span", span)

    interpolation_type = model_parameters.get("interpolation_type")
    if interpolation_type is not None:
        if interpolation_type not in ("linear", "cspline"):
            raise ValueError("interpolation_type must be 'linear' or 'cspline'")

        param.setValue("interpolation_type", interpolation_type.encode("ascii"))

    return param


def _check_table(table):
    pm = table.peakmap.unique_value()
    if pm.meta_data.get("rt_aligned"):
        raise ValueError("there are already rt_aligned peakmaps in the table(s).")
    assert isinstance(table, Table), "non table object in tables"
    assert "mz" in table.col_names, "need mz column for alignment"
    assert "rt" in table.col_names, "need rt column for alignment"


def _setup_algorithm(
    n_peaks, max_mz_difference_pair_finder, max_rt_difference, max_mz_difference
):
    algorithm = pyopenms.MapAlignmentAlgorithmPoseClustering()
    algorithm.setLogType(pyopenms.LogType.CMD)

    parameters = algorithm.getDefaults()
    parameters[b"max_num_peaks_considered"] = n_peaks
    parameters[b"superimposer:num_used_points"] = n_peaks
    parameters[b"superimposer:mz_pair_max_distance"] = float(
        max_mz_difference_pair_finder
    )
    parameters[b"pairfinder:distance_RT:max_difference"] = float(max_rt_difference)
    parameters[b"pairfinder:distance_MZ:max_difference"] = float(max_mz_difference)
    parameters[b"pairfinder:distance_MZ:unit"] = b"Da"
    algorithm.setParameters(parameters)
    return algorithm


def _align(
    table, feature_map, reference_map, model, model_params, destination, algorithm
):
    table = table.consolidate()
    transformation = _compute_transformation(
        algorithm, reference_map, feature_map, model, model_params
    )

    if destination:
        _plot_and_save(transformation, table, destination)

    _transform_table(table, transformation)
    table.meta_data["rt_aligned"] = True
    return table


def _compute_transformation(algorithm, reference_map, feature_map, model, model_params):
    algorithm.setReference(reference_map)
    transformation = pyopenms.TransformationDescription()

    algorithm.align(feature_map, transformation)
    transformation.fitModel(model, model_params)
    return transformation


def _plot_and_save(transformation, table, destination):
    sources = set(table.source)
    assert len(sources) == 1, "multiple sources in table"

    source = sources.pop()
    filename = os.path.basename(source)

    data_points = transformation.getDataPoints()
    assert data_points, "no matching data points found"
    print(len(data_points), "matching data points")

    x = np.array([dp.first for dp in data_points])
    y = np.array([dp.second for dp in data_points])
    plt.plot(x, y - x, ".")

    x.sort()
    yn = [transformation.apply(xi) for xi in x]
    plt.plot(x, yn - x)

    filename = os.path.splitext(filename)[0] + "_aligned.png"
    target_path = os.path.join(destination, filename)
    print()
    print("SAVE", os.path.abspath(target_path))
    print()
    plt.savefig(target_path)
    plt.close()


def _transform_table(table, transformation):
    rt_new = pyopenms.transform_rt_values(
        transformation, [(float(rt)) for rt in table.rt]
    )
    rtmin_new = pyopenms.transform_rt_values(
        transformation, [(float(rt)) for rt in table.rtmin]
    )
    rtmax_new = pyopenms.transform_rt_values(
        transformation, [(float(rt)) for rt in table.rtmax]
    )

    table.replace_column("rt", rt_new, RtType)
    table.replace_column("rtmin", rtmin_new, RtType)
    table.replace_column("rtmax", rtmax_new, RtType)

    # we know that there is only one peakmap in the table
    peakmap = next(iter(table.peakmap))._make_mutable()
    peakmap.meta_data["rt_aligned"] = True
    with peakmap.spectra_for_modification() as spectra:
        spectra._transform_rt(transformation)
