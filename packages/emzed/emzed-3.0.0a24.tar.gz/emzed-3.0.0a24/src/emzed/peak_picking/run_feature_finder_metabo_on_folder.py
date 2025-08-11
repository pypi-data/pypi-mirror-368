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


import glob
import os
import warnings

from emzed.core.multiprocessing import multiprocessing
from emzed.ms_data import PeakMap

from .run_feature_finder_metabo import run_feature_finder_metabo


def run_feature_finder_metabo_on_folder(
    in_folder,
    file_patterns=None,
    out_folder=None,
    ms_level=None,
    n_cores=1,
    verbose=False,
    run_feature_grouper=True,
    split_by_precursor_mz_tol=0.0,
    overwrite=False,
    **parameters,
):
    assert os.path.exists(in_folder), f"folder {in_folder} does not exist"
    assert os.path.isdir(in_folder), f"path {in_folder} is not a folder"

    if out_folder is None:
        out_folder = in_folder

    if os.path.exists(out_folder):
        assert os.path.isdir(in_folder), f"path {out_folder} is not a folder"
    else:
        os.makedirs(out_folder)

    if file_patterns is None:
        file_patterns = ["*.mzML", "*.mzXML"]

    assert isinstance(file_patterns, (list, tuple))

    assert isinstance(n_cores, int)
    assert n_cores >= 1

    max_n_cores = multiprocessing.cpu_count()
    if n_cores > max_n_cores:
        warnings.warn(
            f"you specified {n_cores} cores which is more than the number"
            f" {max_n_cores} of available cores."
        )

    in_paths = [
        p
        for file_pattern in file_patterns
        for p in glob.glob(os.path.join(in_folder, file_pattern))
    ]

    if not in_paths:
        warnings.warn(f"did not find files matching {file_patterns} in {in_folder}")
        return

    out_paths = [
        os.path.join(
            out_folder, os.path.splitext(os.path.basename(p))[0] + "_peaks.table"
        )
        for p in in_paths
    ]
    existing_out_paths = [p for p in out_paths if os.path.exists(p)]

    if not overwrite and existing_out_paths:
        if len(existing_out_paths) <= 3:
            files = ", ".join(out_paths)
        else:
            files = ", ".join(out_paths[:3]) + ", ..."
        raise IOError(
            f"files {files} already exist. use overwrite=True to overwrite them"
        )

    if n_cores == 1:
        for path in in_paths:
            e = _run_on_file(
                path,
                ms_level,
                parameters,
                out_folder,
                verbose,
                run_feature_grouper,
                split_by_precursor_mz_tol,
            )
            if e is not None:
                return

    else:
        args = [
            (
                path,
                ms_level,
                parameters,
                out_folder,
                verbose,
                run_feature_grouper,
                split_by_precursor_mz_tol,
            )
            for path in in_paths
        ]

        with multiprocessing.Pool(n_cores) as pool:
            pool.starmap(_run_on_file, args)


def _run_on_file(
    path,
    ms_level,
    parameters,
    out_folder,
    verbose,
    run_feature_grouper,
    split_by_precursor_mz_tol,
):
    try:
        print("run run_feature_finder_metabo on", path)
        peaks = run_feature_finder_metabo(
            PeakMap.load(path),
            ms_level,
            verbose,
            run_feature_grouper,
            split_by_precursor_mz_tol,
            **parameters,
        )
        output_path = os.path.join(
            out_folder, os.path.splitext(os.path.basename(path))[0] + "_peaks.table"
        )
        peaks.save(output_path, overwrite=True)
    except Exception as e:
        return e


run_feature_finder_metabo_on_folder.__doc__ = (
    """runs feature_finder_metabo on all files in given folder matching provided"""
    """file_extension and saves the resulting table in out_folder.

:param in_folder: input folder, must exist.

:param file_patterns: list of file patterns. if not specified use ["*.mzML", "*.mzXML"].

:param out_folder: output folder, not required to exist, will be created on demand.
                   Default: out_folder = in_folder.

:param ms_level: optional ms level to be used for peak picking.

:param n_cores: run feature finding on n_cores in parallel.

:param verbose: set to ``True`` for verbose output.

:param parameters: check ``help(run_feature_finder_metabo)`` for details.

:returns: `None`."""
)
