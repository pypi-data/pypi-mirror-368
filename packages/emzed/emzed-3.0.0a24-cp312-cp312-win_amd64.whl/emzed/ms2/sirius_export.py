#!/usr/bin/env python

import contextlib
import pathlib


def export_sirius_files(
    peak_table,
    output_folder,
    abs_min_intensity=0.0,
    rel_min_intensity=0.0,
    *,
    overwrite=False,
):
    """exports peaks with attached ms2 spectra as sirius .ms files to the
    specified folder.

    :param peak_table: peak table with column ``spectra_ms2``. Columns ``rt`` and
                       ``id`` can be helpful to identify results in sirius, but are
                       optional.

    :param output_folder: folder to write sirius files to.

    :param abs_min_intensity: filter ms2 spectra by absolute minimal intensity.
                              if rel_min_intensity is also specified peaks compliant
                              to both criteria are exported.

    :param rel_min_intensity: filter ms2 spectra by relatie minimal intensity compared
                              to highest ms2 peak.
                              if abs_min_intensity is also specified peaks compliant
                              to both criteria are exported.

    :param overwrite: set to ``True`` when the output folder already contains .ms files
                      and you take the risk to potentially overwrite existing files.
    """
    peak_table._ensure_col_names("spectra_ms2")

    if not isinstance(abs_min_intensity, (int, float)) or abs_min_intensity < 0:
        raise ValueError("please specify number >=0 for abs_min_intensity")

    if (
        not isinstance(rel_min_intensity, (int, float))
        or not 0 <= rel_min_intensity <= 1
    ):
        raise ValueError("please specify number in range 0..1 for rel_min_intensity")

    output_folder = pathlib.Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    for p in output_folder.glob("*.ms"):
        if overwrite:
            p.unlink()
        else:
            raise ValueError(
                f"folder {output_folder} already contains .ms file {p},"
                " use overwrite=True in case you want to overwrite existing files"
            )

    has_id = "id" in peak_table.col_names
    has_rt = "rt" in peak_table.col_names

    i = 0
    for row in peak_table:
        if row.spectra_ms2 is None:
            continue
        for j, msms in enumerate(row.spectra_ms2):
            pre_mz, _, charge = msms.precursors[0]
            peaks = msms.peaks
            peak_id = row.id if has_id else i
            path = output_folder / f"peak_{peak_id:06d}_spec_{j}.ms"
            rt = row.rt if has_rt else None
            _write_ms_file(
                path,
                pre_mz,
                charge,
                peaks,
                peak_id,
                rt,
                abs_min_intensity,
                rel_min_intensity,
            )
            i += 1


def _write_ms_file(
    path, pre_mz, charge, peaks, peak_id, rt, abs_min_intensity, rel_min_intensity
):
    with path.open("w") as fh:
        with contextlib.redirect_stdout(fh):
            print(f">compound {peak_id}")
            if charge in (-1, 1):
                print(f">charge {charge}")
            if rt is not None:
                print(f">rt {rt}")
            print(f">parentmass {pre_mz}")
            print(">ms2")

            if not peaks.shape[0]:
                return

            max_ii = max(peaks[:, 1])

            for mz, ii in peaks:
                if ii >= abs_min_intensity and ii >= rel_min_intensity * max_ii:
                    print(mz, ii)
