# This file is part of emzed (https://emzed.ethz.ch), a software toolbox for analysing
# LCMS data with Python.
#
# Copyright (C) 2020 ETH Zurich, SIS ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.


import time

import tqdm

from .peak_shape_models import available_peak_shape_models
from .utils import call_integrator, check_columns, check_num_cores

MIN_SIZE_DEFAULT = 100


def integrate_chromatograms(
    chromatogram_table,
    peak_shape_model,
    ms_level=None,
    show_progress=True,
    n_cores=1,
    min_size_for_parallel_execution=MIN_SIZE_DEFAULT,
    post_fixes=None,
    max_cores=8,
    in_place=False,
    path=None,
    overwrite=False,
    **model_extra_args,
):
    """integrates peaks of chromatogram_table.

    :param chromatogram_table: :py:class:`emzed.Table` with required columns
                        ``id, mzmin, mzmax, rtmin, rtmax, peakmap``.
    :param peak_shape_model: String of model name applied to determine peak area.
                             Available models are: ``asym_gauss``, ``linear``,
                             ``no_integration``, ``sgolay``, ``emg``.
    :param ms_level: MS level of peak integration. Must only be specified if peakmap
                     has more than one MS levels. ``Default = None``.
    :param show_progress: Boolean value to activate progress bar. ``Default = True``.

    :param n_cores: Defines the number of cores used for multicore processing.
                    If ``n_cores`` exceeds the number of available cores  a
                    warning is displayed and.
                    ``Default = 1``.
    :param min_size_for_parallel_execution: Defines the number of table rows required
                    to execute multicore processing. ``Default = 100``.
    :param post_fixes: Defines a subset of peaks via postfixes i. e. ['__0', '__1'].
                        By default, all peak_tables of a table get integrated.
                        ``Default = None``.
    :param max_cores: The maximal number of cores used for multicore processing.
                      If ``max_cores`` exceeds the number of available cores
                      a warning is displayed and the ``n_cores`` is set to
                      ``max_cores``. Default is ``8``.
    :param in_place:  Allows operation in place if True.
                      Note: if ``in_place`` is ``True`` multicore processing
                      is not possible and n_cores is set to 1.
                      Default = ``False``.
                      Using in-place integration has performance benefits.
    :param path: If specified the result will be a Table with a db file backend,
             else the result will be managed in memory.
    :param overwrite: Indicate if an already existing database file should be
                  overwritten.
    :returns: :py:class:`emzed.Table` by default. Returns None if ``in_place`` is
              ``True``

    """  # noqa: E501

    if peak_shape_model not in available_peak_shape_models:
        names = ", ".join(available_peak_shape_models)
        raise ValueError(f"given integrator {peak_shape_model} must be one of {names}")

    needed_columns_chromatograms = [
        "rtmin_chromatogram",
        "rtmax_chromatogram",
        "chromatogram",
    ]

    missing, post_fixes = check_columns(
        chromatogram_table, needed_columns_chromatograms, post_fixes
    )
    if missing:
        raise ValueError("given table is not a valid chromatogram table")

    messages, n_cores = check_num_cores(
        n_cores,
        len(chromatogram_table),
        min_size_for_parallel_execution,
        max_cores,
        in_place,
    )
    for message in messages:
        print(message)

    started = time.time()

    result = call_integrator(
        n_cores,
        _integrate,
        chromatogram_table,
        post_fixes,
        peak_shape_model,
        None,
        show_progress,
        model_extra_args,
    )

    result_table = create_result_table(
        chromatogram_table,
        peak_shape_model,
        post_fixes,
        result,
        path,
        overwrite,
        in_place,
    )

    if show_progress:
        needed = time.time() - started
        minutes, seconds = divmod(needed, 60)
        if minutes:
            print("needed %d minutes and %.1f seconds" % (minutes, seconds))
        else:
            print("needed %.1f seconds" % seconds)

    return result_table


def _integrate(args):
    (
        chromatogram_table,
        indices,
        post_fixes,
        peak_shape_model,
        ms_level,
        show_progress,
        model_extra_args,
        is_parallel,
        peaks_total,
        n_cores,
    ) = args

    if is_parallel:
        chromatogram_table = chromatogram_table.consolidate()

    result = {}

    with tqdm.tqdm(
        total=len(post_fixes) * peaks_total, disable=not show_progress
    ) as bar:
        for postfix in post_fixes:
            for index, row in zip(indices, chromatogram_table):
                rtmin = row.get("rtmin_chromatogram" + postfix)
                rtmax = row.get("rtmax_chromatogram" + postfix)
                chromatogram = row.get("chromatogram" + postfix)
                if rtmin is None or rtmax is None or chromatogram is None:
                    current_peak_shape_model = available_peak_shape_models[
                        "no_integration"
                    ]
                else:
                    current_peak_shape_model = available_peak_shape_models[
                        peak_shape_model
                    ]

                model = current_peak_shape_model.fit_chromatogram(
                    rtmin, rtmax, chromatogram, **model_extra_args
                )
                result[index, postfix] = model
                bar.update(n_cores)
        bar.update(len(post_fixes) * peaks_total - bar.n)

    return result


def create_result_table(
    chromatogram_table,
    peak_shape_model,
    post_fixes,
    result,
    path,
    overwrite,
    in_place,
):
    result_table = (
        chromatogram_table
        if in_place
        else chromatogram_table.copy(path=path, overwrite=overwrite)
    )

    for post_fix in post_fixes:
        peak_shape_models = []
        areas = []
        rmses = []
        models = []
        is_valid = []

        for index, row in enumerate(chromatogram_table):
            model = result.get((index, post_fix))
            areas.append(model.area)
            rmses.append(model.rmse)
            models.append(model)
            is_valid.append(model.is_valid)
            peak_shape_models.append(model.model_name)

        result_table.add_or_replace_column(
            "peak_shape_model_chromatogram" + post_fix, peak_shape_models, str
        )
        result_table.add_or_replace_column(
            "area_chromatogram" + post_fix, areas, float, format_="%.2e"
        )
        result_table.add_or_replace_column(
            "rmse_chromatogram" + post_fix, rmses, float, format_="%.2e"
        )
        result_table.add_or_replace_column(
            "model_chromatogram" + post_fix, models, object, format_=None
        )
        result_table.add_or_replace_column(
            "valid_model_chromatogram" + post_fix, is_valid, bool
        )

    return None if in_place else result_table
