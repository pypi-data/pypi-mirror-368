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

from emzed.utils.sqlite import table_exists


def compute_peakmap_hash(conn, table_name):
    conn.commit()

    hash_spectra = (
        conn.execute(
            f"SELECT md5_hexdigest(hash) from {table_name}_spectra ORDER BY scan_number"
        ).fetchone()[0]
        or ""
    )
    hash_precursors = (
        conn.execute(
            f"SELECT md5_hexdigest(hash) from {table_name}_precursors"
            " ORDER by scan_number, mz"
        ).fetchone()[0]
        or ""
    )
    if not table_exists(conn, f"{table_name}_chromatograms"):
        # older versions of tables don't have chromatograms:
        hash_chromatograms = ""
    else:
        hash_chromatograms = (
            conn.execute(
                f"SELECT md5_hexdigest(hash) from {table_name}_chromatograms"
                " ORDER BY mz, precursor_mz"
            ).fetchone()[0]
            or ""
        )

    return hash_spectra + hash_precursors + hash_chromatograms
