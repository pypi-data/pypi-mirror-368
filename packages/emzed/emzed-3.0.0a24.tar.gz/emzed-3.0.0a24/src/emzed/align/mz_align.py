#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>

import os
import warnings

from emzed import MzType
from emzed.utils import has_emzed_gui

from .mz_align_routines import (
    _apply_transform,
    _find_mz_matches,
    _find_parameters,
    _plot_and_save_match,
)


def mz_align(
    table,
    reference_table,
    tol=15e-3,
    destination=None,
    min_r2=0.95,
    max_tol=1e-3,
    min_points=5,
    interactive=False,
):
    """
    performs affine linear mz-correction for a feature table.

    and retention times of  known metabolites. This table needs columns ``mz_calc`` for
    the mz value calculated from the mass of the isotope, ``rtmin``, ``rtmax`` for the
    retention time window where the peak is expected to elute from the column in order
    to restrict the match of the table against the  ``reference_table``.

    ``destination`` is a directory which will be used for storing the result and
    intermediate data.  If you do not specify this value, a dialog for choosing the
    destination directory will be opened.

    The input table **is not modified** in place, the function returns the aligned
    table.

    the parameter *tol* is related to find matching peaks, *max_tol* and *min_r2*
    determine stop criterion when removing outlier points in non interactive mode.
    """

    if not table.meta_data.get("rt_aligned", False):
        warnings.warn("you might get better results if you rt align your data first")

    assert min_r2 <= 1.0
    assert min_points > 1

    assert (
        not interactive or has_emzed_gui()
    ), "need emzed_gui package installed for interactive mode"

    source = table.source.unique_value()
    peakmaps = table.peakmap.unique_values()
    polarities = set.union(*[peakmap.polarities() for peakmap in peakmaps])
    polarities.discard(None)
    if len(polarities) < 1:
        raise ValueError("could not get polarites from peakmaps")
    if len(polarities) > 1:
        raise ValueError("table contains peakmap(s) with multiple polarities")

    polarity = polarities.pop()

    reference_table._ensure_col_names("mz", "rtmin", "rtmax", "name", "polarity")

    reference_table = reference_table.filter(reference_table.polarity == polarity)

    if len(reference_table) == 0:
        polarity_reference = set(reference_table.polarity)
        raise ValueError(
            "polarities in reference table %s "
            " do not correspond to polarity of sample tables %s"
            % (polarity_reference, polarity)
        )

    if destination is not None:
        basename = os.path.basename(source)
        fname, _ = os.path.splitext(basename)
        reference_table.save(
            os.path.join(destination, fname + "_reference.table"), overwrite=True
        )

    real, tobe, matches = _find_mz_matches(reference_table, table, tol)
    if len(real) <= 1:
        print("not enough matches for alignment")
        return

    if interactive:
        from .. import gui

        gui.inspect(matches, offerAbortOption=True)

    elif len(tobe) < min_points:
        raise Exception("could only match %d peaks" % len(tobe))

    if not interactive:
        result = _find_parameters(tobe.copy(), real.copy(), min_r2, max_tol, min_points)
        if result is None:
            print("could not match peaks")
            return None
        transform, used = result
    else:
        raise NotImplementedError("not implemented yet")

    if destination is not None:
        matches = matches.consolidate()
        matches.add_column("mz_aligned", transform(real), MzType, insert_after="mz")
        matches.add_column("error", transform(real) - tobe, float, "%.3e")
        matches.save(
            os.path.join(destination, fname + "_matches.table"), overwrite=True
        )
        matches.save_csv(
            os.path.join(destination, fname + "_matches.csv"), overwrite=True
        )

        path = os.path.join(destination, fname + "_mzalign.png")
        _plot_and_save_match(tobe, real, used, transform, path)

    transformed_table = _apply_transform(table, transform)
    return transformed_table
