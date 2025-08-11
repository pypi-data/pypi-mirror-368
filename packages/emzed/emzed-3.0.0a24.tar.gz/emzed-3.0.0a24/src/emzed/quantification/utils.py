#!/usr/bin/env python

import os
import tempfile

from emzed.core.multiprocessing import multiprocessing


def call_integrator(
    n_cores,
    integrate_function,
    table,
    post_fixes,
    peak_shape_model,
    ms_level,
    show_progress,
    model_extra_args,
):
    indices = list(range(len(table)))

    if n_cores == 1:
        result = integrate_function(
            (
                table,
                indices,
                post_fixes,
                peak_shape_model,
                ms_level,
                show_progress,
                model_extra_args,
                False,
                len(table),
                1,
            )
        )
        return result

    temp_folder = tempfile.mkdtemp()
    args = []
    for i in range(n_cores):
        sub_table = table[i::n_cores]
        sub_indices = indices[i::n_cores]
        _path = os.path.join(temp_folder, f"part_{i:03d}.table")
        sub_table = sub_table.consolidate(path=_path)
        show_progress = i == 0  # only first process prints progress status
        args.append(
            (
                sub_table,
                sub_indices,
                post_fixes,
                peak_shape_model,
                ms_level,
                show_progress,
                model_extra_args,
                True,
                len(table),
                n_cores,
            )
        )

    try:
        with multiprocessing.Pool(n_cores) as pool:
            results = pool.map(integrate_function, args)
            if results:
                result = next(results)
                for r in results:
                    result.update(r)
            else:
                result = {}

    finally:
        for p in os.listdir(temp_folder):
            try:
                os.unlink(os.path.join(temp_folder, p))
            except IOError:
                pass

    return result


def check_columns(table, needed, post_fixes):
    missing = []

    if post_fixes is None:
        post_fixes = table.supported_postfixes(needed)
        if not post_fixes:
            for name in needed:
                if name not in table.col_names:
                    missing.append(name)
        return missing, post_fixes

    for post_fix in post_fixes:
        for name in needed:
            if name + post_fix not in table.col_names:
                missing.append(name + post_fix)
    return missing, post_fixes


def check_num_cores(n_cores, table_size, min_table_size, max_cores, in_place):
    messages = []
    if multiprocessing.current_process().daemon and n_cores != 1:
        messages.append(
            "WARNING: you choose n_cores = %d but integrate already runs inside a "
            "daemon process which is not allowed. therefore set n_cores = 1" % n_cores
        )
        n_cores = 1

    if n_cores <= 0:
        messages.append(
            "WARNING: you requested to use %d cores, "
            "we use single core instead !" % n_cores
        )
        n_cores = 1

    n_cores = min(n_cores, max_cores)

    if n_cores > 1 and in_place:
        messages.append(
            "WARNING: you requested to use %d cores but you set in_place = True, "
            " which is not allowed and we set n_cores = 1" % n_cores
        )
        n_cores = 1

    if n_cores > 1 and table_size < min_table_size:
        messages.append(
            "INFO: as the table has les thann %d rows, we switch to one cpu mode"
            % min_table_size
        )
        n_cores = 1

    elif n_cores > multiprocessing.cpu_count():
        messages.append(
            "WARNING: more processes demanded than available cpu cores, this might be "
            "inefficient"
        )

    return messages, n_cores
