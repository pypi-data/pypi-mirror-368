#!/usr/bin/env python

import emzed
from emzed.table.table_utils import MzType, RtType


def extract_ms_chromatograms(peakmap, path=None):
    columns = [
        "id",
        "peakmap",
        "rtmin_chromatogram",
        "rtmax_chromatogram",
        "precursor_mz_chromatogram",
        "mz_chromatogram",
        "type",
        "chromatogram",
    ]
    types = [
        int,
        emzed.PeakMap,
        RtType,
        RtType,
        MzType,
        MzType,
        str,
        emzed.MSChromatogram,
    ]
    rows = []

    id_ = 1
    for chromatogram in peakmap.ms_chromatograms:
        rts = chromatogram.rts
        rtmin = min(rts)
        rtmax = max(rts)
        precursor_mz = chromatogram.precursor_mz
        mz = chromatogram.mz
        type_ = chromatogram.type

        rows.append(
            [
                id_,
                peakmap,
                rtmin,
                rtmax,
                precursor_mz,
                mz,
                type_,
                chromatogram,
            ]
        )
        id_ += 1

    return emzed.Table.create_table(columns, types, rows=rows, path=path)
