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


import enum
import inspect
import os
import pathlib
import pickle
import sys
import warnings
from collections import defaultdict, namedtuple
from contextlib import contextmanager
from functools import wraps
from pickle import PicklingError

import numpy as np

from emzed.core import DbBackedDictionary, DbBackedModel, ImmutableDbBackedDictionary
from emzed.core.hashes import md5_hexdigest
from emzed.pyopenms import encode, pyopenms
from emzed.utils.sqlite import Connection, copy_table, list_tables, table_exists

from .peak_map_hasher import compute_peakmap_hash

try:
    profile
except NameError:

    def profile(fun):
        return fun


class Chromatogram(namedtuple("_Chromatogram", ["rts", "intensities"])):
    def __str__(self):
        rtmin, rtmax = min(self.rts), max(self.rts)
        rtmin, rtmax = round(rtmin, 1), round(rtmax, 1)
        return f"Chromatogram(rt_range={rtmin!s}..{rtmax!s})"

    def __repr__(self):
        return f"<Chromatogram length={len(self.rts)}>"


class ImmutablePeakMap(DbBackedModel):
    _access_name = None

    _cache = {}

    @classmethod
    def _load_from_unique_id(cls, conn, unique_id):
        if isinstance(unique_id, bytes):
            unique_id = str(unique_id, "ascii")
        key = (conn.uri, unique_id)
        if key in cls._cache:
            if cls._cache[key]._conn.is_closed():
                del cls._cache[key]
        if key not in cls._cache:
            access_name = f"peakmap_{unique_id}"
            cls._cache[key] = ImmutablePeakMap(conn, access_name)
            cls._cache[key]._unique_id = unique_id
        return cls._cache[key]

    def __init__(self, conn, access_name, meta_data=None, info=None):
        self._conn = conn
        self._access_name = access_name
        self._unique_id = None

        self._info = ImmutableDbBackedDictionary(conn, access_name, "info", info)
        self.meta_data = ImmutableDbBackedDictionary(
            conn, access_name, "meta", meta_data
        )
        self.spectra = ImmutableSpectra(self)
        self.ms_chromatograms = ImmutableMSChromatograms(self)

    def _make_mutable(self):
        return PeakMap(self._conn, self._access_name, self.meta_data, self._info)

    def ms_levels(self):
        return self._info.get("ms_levels")

    def get_dominating_peak_map(self):
        ms_level = min(self.ms_levels())
        pm = self.extract(mslevelmin=ms_level, mslevelmax=ms_level)
        for spectrum in pm.spectra:
            spectrum.ms_level = 1
        return pm

    @classmethod
    def open(cls, path):
        if not os.path.exists(path):
            raise IOError(f"file {path} does not exist")
        conn = Connection(path)
        access_name = "peakmap"
        return cls(conn, access_name, {}, {})

    def close(self):
        self._conn.close()

    def is_open(self):
        return self._conn.is_open()

    def is_in_memory(self):
        return self._conn.db_path is None

    @classmethod
    def load(cls, path, *, target_db_file=None, overwrite=False):
        # open-ms returns empty peakmap if file does not exists, so we check ourselves:

        assert isinstance(
            path, (str, pathlib.Path)
        ), "must be string or pathlib.Path object"

        path = os.path.abspath(path)
        if not os.path.exists(path):
            raise OSError(f"file {path} does not exist")
        if not os.path.isfile(path):
            raise OSError(f"{path} is not a file")

        if target_db_file == path:
            raise ValueError(
                "you must not use the same path for 'path' and 'target_db_file'"
            )

        if target_db_file is not None and os.path.exists(target_db_file):
            if overwrite:
                os.unlink(target_db_file)
            else:
                raise ValueError(f"{target_db_file} already exists")

        if sys.platform == "win32":
            path = path.replace("/", "\\")  # needed for network shares
        spectra, chromatograms, source = pyopenms.load_experiment(encode(path))

        return cls._from_iter(
            pickle.loads(spectra),
            pickle.loads(chromatograms),
            target_db_file,
            source,
        )

    def __len__(self):
        return len(self.spectra)

    def scan_counts(self):
        cursor = self._conn.execute(
            f"""
                SELECT ms_level, count(*) from {self._access_name}_spectra
                GROUP BY ms_level"""
        )
        return dict(cursor)

    def __eq__(self, other):
        if not isinstance(other, ImmutablePeakMap):
            return False

        return self is other or (
            len(self) == len(other)
            and self.rt_ranges() == other.rt_ranges()
            and self.mz_ranges() == other.mz_ranges()
            and self.ms_levels() == other.ms_levels()
            and self.unique_id == other.unique_id
        )

    def __hash__(self):
        return int(self.unique_id, 16)

    def filter(self, predicate, target_db_file=None):
        conn = Connection(target_db_file)
        conn, access_name = create_table(conn=conn)
        peakmap = PeakMap(conn, access_name, self.meta_data, self._info)
        with peakmap.spectra_for_modification() as spectra:
            for spectrum in self:
                if predicate(spectrum):
                    spectra.add_spectrum(spectrum)
        return peakmap

    def __getstate__(self):
        parent_module = inspect.currentframe().f_back.f_code.co_filename.replace(
            "\\", "/"
        )
        if not parent_module.endswith("/multiprocessing/reduction.py"):
            raise NotImplementedError("pickling not supported for PeakMaps")

        if self.is_in_memory():
            raise PicklingError("can not use multiprocessing for in-memory PeakMaps")

        return self.__dict__

    def __setstate__(self, data):
        self.__dict__.update(data)

    def extract_for_precursors(self, mzs, mz_tol, *, target_db_file=None):
        assert isinstance(mzs, (tuple, list)), "need tuple or list"
        assert all(isinstance(mz, (int, float)) for mz in mzs), "need real numbers"

        # we prefilter on db for multiplexed data but must later sort out
        # false positives
        n = len(mzs)
        low = sum(mzs) - n * mz_tol
        high = sum(mzs) + n * mz_tol

        mzs = np.array(sorted(mzs))

        stmt = f"""
            SELECT S.scan_number, S.polarity, S.ms_level, S.rt, S.mzs, S.intensities,
                   group_concat(P.mz), group_concat(p.intensity), group_concat(p.charge)
            FROM {self._access_name}_spectra as S
            JOIN {self._access_name}_precursors as P
            ON   S.scan_number = P.scan_number
            WHERE S.ms_level > 1
            GROUP BY P.scan_number
            HAVING SUM(P.mz) BETWEEN {low} AND {high}
        """

        def iter_samples():
            for (
                scan_number,
                polarity,
                ms_level,
                rt,
                mzs_blob,
                iis_blob,
                precursor_mzs,
                precursor_intensities,
                precursor_charges,
            ) in self._conn.execute(stmt):
                precursor_mzs = precursor_mzs.split(",")
                if len(precursor_mzs) != n:
                    continue

                precursor_mzs = sorted(map(float, precursor_mzs))
                precursor_mzs = np.array(precursor_mzs)
                if np.any(np.abs(mzs - precursor_mzs) > mz_tol):
                    continue

                precursor_intensities = list(
                    map(float, precursor_intensities.split(","))
                )
                precursor_charges = list(map(int, precursor_charges.split(",")))

                precursors = zip(
                    precursor_mzs, precursor_intensities, precursor_charges
                )

                peaks = np.hstack(
                    (
                        np.frombuffer(mzs_blob, dtype=np.float64)[:, None],
                        np.frombuffer(iis_blob, dtype=np.float32)[:, None],
                    )
                )
                yield peaks, rt, ms_level, polarity, precursors, scan_number

        meta_data = self.meta_data.as_dict()
        meta_data["split_by_precursor"] = mzs
        meta_data["split_by_precursor_mz_tol"] = mz_tol

        return self._from_iter(
            iter_samples(), None, target_db_file, meta_data=meta_data
        )

    def extract(
        self,
        mzmin=None,
        mzmax=None,
        rtmin=None,
        rtmax=None,
        imin=None,
        imax=None,
        mslevelmin=None,
        mslevelmax=None,
        precursormzmin=None,
        precursormzmax=None,
        polarity=None,
        *,
        target_db_file=None,
    ):
        conditions = []

        if rtmin is not None:
            conditions.append(f"S.rt >= {rtmin}")
        if rtmax is not None:
            conditions.append(f"S.rt <= {rtmax}")

        if polarity is not None:
            if polarity not in ["+", "-"]:
                raise ValueError("polarity must be either '+' or '-'")

            conditions.append(f"S.polarity = '{polarity}'")

        stmt = f"""SELECT S.scan_number, S.polarity, S.ms_level, S.rt, S.mzs,
                          S.intensities
                FROM {self._access_name}_spectra AS S
                """
        if precursormzmin is not None or precursormzmax is not None:
            if precursormzmin is None:
                precursormzmin = 0.0
            if precursormzmax is None:
                precursormzmax = 999_999
            conditions.append(
                f"""
                (S.scan_number IN (
                    SELECT scan_number
                    FROM {self._access_name}_precursors
                    WHERE mz BETWEEN {precursormzmin} AND {precursormzmax}
                    )
                )"""
            )

        if conditions:
            filter_stmt = " AND ".join(conditions)
            stmt += f"WHERE {filter_stmt}"

        cursor = self._conn.execute(stmt)

        scan_numbers_msn = set()

        # manage and avoid duplicates which might happen if multiple precursor mz values
        # match to precursormz{min,max} limits. the alternative solution to introduce
        # a DISTINCT in the previous SQL statement is to slow.
        seen_scan_numbers = set()

        def iter_samples():
            for (
                scan_number,
                polarity,
                ms_level,
                rt,
                mzs_bytes,
                intensities_bytes,
            ) in cursor:
                if scan_number in seen_scan_numbers:
                    continue

                seen_scan_numbers.add(scan_number)

                if mslevelmin is not None and ms_level < mslevelmin:
                    continue

                if mslevelmax is not None and ms_level > mslevelmax:
                    continue

                if ms_level > 1:
                    scan_numbers_msn.add(scan_number)

                mzs = np.frombuffer(mzs_bytes, dtype=np.float64)
                intensities = np.frombuffer(intensities_bytes, dtype=np.float32)

                if mzmin is not None:
                    mask = mzs >= mzmin
                    mzs = mzs[mask]
                    intensities = intensities[mask]

                if mzmax is not None:
                    mask = mzs <= mzmax
                    mzs = mzs[mask]
                    intensities = intensities[mask]

                if imin is not None:
                    mask = intensities >= imin
                    mzs = mzs[mask]
                    intensities = intensities[mask]

                if imax is not None:
                    mask = intensities <= imax
                    mzs = mzs[mask]
                    intensities = intensities[mask]

                peaks = np.hstack((mzs[:, None], intensities[:, None]))
                yield peaks, rt, ms_level, polarity, [], scan_number

        meta_data = self.meta_data.as_dict()
        meta_data["extraction window"] = dict(
            mzmin=mzmin,
            mzmax=mzmax,
            rtmin=rtmin,
            rtmax=rtmax,
            imin=imin,
            imax=imax,
            mslevelmin=mslevelmin,
            mslevelmax=mslevelmax,
            precursormzmin=precursormzmin,
            precursormzmax=precursormzmax,
            polarity=polarity,
        )

        result = self._from_iter(
            iter_samples(), None, target_db_file, meta_data=meta_data
        )

        if scan_numbers_msn:
            cursor = self._conn.execute(
                f"""SELECT scan_number, mz, intensity, charge, hash
                    FROM {self._access_name}_precursors
                    WHERE scan_number >= {min(scan_numbers_msn)}
                    AND   scan_number <= {max(scan_numbers_msn)}
                """
            )

            precursors = []
            for scan_number, mz, intensity, charge, hash in cursor:
                if scan_number not in scan_numbers_msn:
                    continue
                if precursormzmin is not None and mz < precursormzmin:
                    continue
                if precursormzmax is not None and mz > precursormzmax:
                    continue
                precursors.append((scan_number, mz, intensity, charge, hash))

            result._conn.executemany(
                f"""
                    INSERT INTO {result._access_name}_precursors VALUES (?, ?, ?, ?, ?)
                    """,
                precursors,
            )

        return result

    def rt_range(self, ms_level=None):
        return self._info.get("rt_ranges").get(ms_level, (None, None))

    def mz_range(self, ms_level=None):
        return self._info.get("mz_ranges").get(ms_level, (None, None))

    def rt_ranges(self, ms_level=None):
        return self._info.get("rt_ranges")

    def mz_ranges(self, ms_level=None):
        return self._info.get("mz_ranges")

    def polarities(self):
        return self._info.get("polarities")

    def chromatogram(
        self,
        mzmin=None,
        mzmax=None,
        rtmin=None,
        rtmax=None,
        ms_level=None,
        precursormzmin=None,
        precursormzmax=None,
        polarity=None,
    ):
        if not len(self):
            return Chromatogram([], [])

        if ms_level is None:
            ms_level = min(self.ms_levels())

        return chromatogram(
            self._conn,
            self._access_name,
            mzmin,
            mzmax,
            rtmin,
            rtmax,
            ms_level,
            precursormzmin,
            precursormzmax,
            polarity,
        )

    def __getattribute__(self, name):
        if name not in ("__str__", "__repr__", "_conn", "is_open"):
            dd = super().__getattribute__("__dict__")
            if "_conn" in dd:
                if not dd["_conn"].is_open():
                    raise ValueError("PeakMap is closed.")
        return super().__getattribute__(name)

    def representing_mz_peak(self, mzmin, mzmax, rtmin, rtmax, ms_level=1):
        return representing_mz_peak(
            self._conn, self._access_name, mzmin, mzmax, rtmin, rtmax, ms_level
        )

    def get_precursors_mzs(self):
        grouped_mz = defaultdict(list)
        for scan_number, mz in self._conn.execute(
            f"SELECT scan_number, mz FROM {self._access_name}_precursors"
        ):
            grouped_mz[scan_number].append(mz)
        return set(tuple(v) for v in grouped_mz.values())

    def split_by_precursors(self, mz_tol=0.0):
        peakmaps = {}
        for mzs in self.get_precursors_mzs():
            if mz_tol == 0.0:
                key = mzs
            else:
                key = tuple(sorted(round(mz_tol * int(mz / mz_tol), 6) for mz in mzs))
            peakmaps[key] = self.extract_for_precursors(mzs, mz_tol)
        return peakmaps

    def __str__(self):
        if not self.is_open():
            return "<PeakMap CLOSED>"
        if "id" in self.meta_data:
            return f"<PeakMap id={self.meta_data['id']}>"
        return f"<PeakMap {self.unique_id[:6]}...>"

    def __repr__(self):
        if not self.is_open():
            return "<PeakMap CLOSED>"
        if "id" in self.meta_data:
            return f"<PeakMap id={self.meta_data['id']}>"
        return f"<PeakMap {self.unique_id}>"

    def _to_openms_experiment(self):
        spectra = sorted(
            (
                s.rt,
                s.ms_level,
                s.polarity,
                s.precursors,
                s.mzs,
                s.intensities,
                s.scan_number,
            )
            for s in self.spectra
        )

        chromatograms = [
            (c._mz, c._precursor_mz, c._rts, c._intensities, c._type)
            for c in self.ms_chromatograms
        ]
        chromatograms.sort(key=lambda x: x[:2])

        return pyopenms.to_openms_experiment(
            pickle.dumps((spectra, chromatograms, self.meta_data.get("source") or ""))
        )

    def save(self, path, *, overwrite=False):
        if not overwrite and os.path.exists(path):
            raise OSError(
                f"file {path} exists, use overwrite=True in case you want to overwrite"
                " the file."
            )

        if sys.platform == "win32":
            path = path.replace(
                "/", "\\"
            )  # needed for network share handling in openms

        if path.upper().endswith(".MZXML") and len(self.ms_chromatograms):
            warnings.warn(
                "your peakmap contains ms chromatograms which will be lost"
                " in mzXML format. better use .mzML to save your data"
            )

        experiment = self._to_openms_experiment()
        fh = pyopenms.FileHandler()
        fh.storeExperiment(encode(path), experiment)

    @classmethod
    def _from_iter(
        cls,
        spec_iter,
        chromatogram_iter,
        target_db_file=None,
        source=None,
        meta_data=None,
    ):
        conn = Connection(target_db_file)

        conn, access_name = create_table(conn=conn)

        mzmins, mzmaxs, rts = defaultdict(list), defaultdict(list), defaultdict(list)

        polarities = set()

        for item in spec_iter:
            peaks, rt, ms_level, polarity, precursors, scan_number = item
            if not peaks.shape[0]:  # skip empty spectra
                continue

            insert_peaks(
                conn,
                access_name,
                peaks,
                rt,
                ms_level,
                polarity,
                precursors,
                scan_number,
            )
            mzmin = float(min(peaks[:, 0]))
            mzmax = float(max(peaks[:, 0]))
            mzmins[ms_level].append(mzmin)
            mzmaxs[ms_level].append(mzmax)
            mzmins[None].append(mzmin)
            mzmaxs[None].append(mzmax)
            rts[ms_level].append(rt)
            rts[None].append(rt)
            polarities.add(polarity)

        for mz, precursor_mz, peaks, type_ in chromatogram_iter or []:
            insert_chromatogram(conn, access_name, mz, precursor_mz, peaks, type_)

        conn.commit()
        create_indices(conn, access_name)
        conn.commit()

        mz_ranges = {}
        for ms_level in mzmins.keys():
            mz_ranges[ms_level] = (min(mzmins[ms_level]), max(mzmaxs[ms_level]))

        rt_ranges = {}
        for ms_level in rts.keys():
            rt_ranges[ms_level] = (min(rts[ms_level]), max(rts[ms_level]))

        ms_levels = set(mz_ranges.keys()) - {None}

        meta_dict = {}
        if meta_data is not None:
            meta_dict.update(meta_data)

        if "full_source" not in meta_dict or source is not None:
            meta_dict["full_source"] = source

        full_source = meta_dict.get("full_source")
        if isinstance(full_source, str):
            meta_dict["source"] = os.path.basename(full_source)
        else:
            meta_dict["source"] = None

        info = {
            "rt_ranges": rt_ranges,
            "mz_ranges": mz_ranges,
            "ms_levels": ms_levels,
            "polarities": polarities,
        }
        return cls(conn, access_name, meta_dict, info)

    def summary(self):
        from emzed import Table

        rows = []
        for ms_level, (rtmin, rtmax) in self.rt_ranges().items():
            if ms_level is None:
                continue
            rt_range = f"{rtmin / 60:.1f}m .. {rtmax / 60:.1f}m"
            rows.append(("rt range", str(ms_level), rt_range))

        for ms_level, (mzmin, mzmax) in self.mz_ranges().items():
            if ms_level is None:
                continue
            mz_range = f"{mzmin:.3f} .. {mzmax:.3f}"
            rows.append(("mz range", (ms_level), mz_range))

        for ms_level, scan_count in self.scan_counts().items():
            rows.append(("num_scans", str(ms_level), scan_count))

        rows.append(("polarities", "", str(self.polarities())))
        rows.append(("ms_chromatograms", "", len(self.ms_chromatograms)))

        return Table.create_table(
            ["info", "ms_level", "value"], [str, str, str], rows=rows
        )

    @property
    def unique_id(self):
        if self._unique_id is None:
            self._unique_id = md5_hexdigest(
                compute_peakmap_hash(self._conn, self._access_name),
                self.meta_data.unique_id,
            )

        return self._unique_id

    def _reset_unique_id(self):
        raise RuntimeError("must never happen")

    def _copy_into(self, conn):
        """copy all db tables into db conn"""

        access_name = f"peakmap_{self.unique_id}"
        if table_exists(conn, f"{access_name}_spectra"):
            return

        copy_table(
            self._conn, conn, f"{self._access_name}_spectra", f"{access_name}_spectra"
        )

        if table_exists(
            self._conn,
            f"{self._access_name}_chromatograms",
        ):
            copy_table(
                self._conn,
                conn,
                f"{self._access_name}_chromatograms",
                f"{access_name}_chromatograms",
            )
        else:
            _create_chromatograms_table(conn, access_name)

        target = f"{access_name}_info"
        source = f"{self._access_name}_info"
        copy_table(self._conn, conn, source, target)

        target = f"{access_name}_meta"
        source = f"{self._access_name}_meta"
        copy_table(self._conn, conn, source, target)

        target = f"{access_name}_precursors"
        source = f"{self._access_name}_precursors"
        copy_table(self._conn, conn, source, target)

        return access_name

    @classmethod
    def _remove_unused_references(clz, table_model, unique_ids_in_use):
        deleted = False
        for t in list_tables(table_model._conn):
            if t.startswith("peakmap_"):
                unique_id = t.removeprefix("peakmap_").split("_")[0]
                if unique_id not in unique_ids_in_use:
                    table_model._conn.execute(f"DROP TABLE {t};")
                    deleted = True
        if deleted:
            table_model._conn.commit()

    def __iter__(self):
        return iter(self.spectra)


class PeakMap(ImmutablePeakMap):
    def __init__(self, conn, access_name, meta_data, info):
        self._conn = conn
        self._access_name = access_name
        self._unique_id = None

        self._info = DbBackedDictionary(self, suffix="info")
        self.meta_data = DbBackedDictionary(self, suffix="meta")

        self.meta_data.update(meta_data)
        self._info.update(info)

        self.spectra = ImmutableSpectra(self)
        self.ms_chromatograms = ImmutableMSChromatograms(self)

    @classmethod
    def from_(clz, pm, *, target_db_file=None):
        pm_new = clz.__new__(clz)
        conn = Connection(target_db_file)
        pm._copy_into(conn)

        pm_new._conn = conn
        pm_new._access_name = pm._access_name
        pm_new._unique_id = None

        pm_new._info = DbBackedDictionary(pm_new, suffix="info")
        pm_new.meta_data = DbBackedDictionary(pm_new, suffix="meta")

        pm_new.spectra = ImmutableSpectra(pm_new)
        pm_new.ms_chromatograms = ImmutableMSChromatograms(pm_new)
        return pm_new

    def add_spectrum(self, spectrum):
        raise TypeError("please use Peakmap.spectra.add_spectrum method instead")

    def _reset_unique_id(self):
        self._unique_id = None

    def merge(self, other):
        assert isinstance(other, self.__class__)
        overlapping_scan_numbers = set(self.spectra._scan_numbers) & set(
            other.spectra._scan_numbers
        )
        if overlapping_scan_numbers:
            raise ValueError("can not merge peakmaps with overlapping scan numbers")

        merged_meta_data = {
            self.unique_id: self.meta_data,
            other.unique_id: other.meta_data,
        }

        self.meta_data.clear()
        self.meta_data["merged from"] = merged_meta_data

        with self.spectra_for_modification() as spectra:
            spectra._add_spectra(other.spectra)

    def _update_mz_ranges(self, mzmins, mzmaxs):
        for msl in mzmins.keys():
            mzmin, mzmax = self.mz_range(msl)

            if mzmin is None:
                mzmin = min(mzmins[msl])
            else:
                mzmin = min(min(mzmins[msl]), mzmin)
            if mzmax is None:
                mzmax = max(mzmaxs[msl])
            else:
                mzmax = max(max(mzmaxs[msl]), mzmax)

            self._info["mz_ranges"][msl] = (mzmin, mzmax)

        self._reset_unique_id()

    def _update_polarities(self, polarities):
        self._info["polarities"].update(polarities)
        self._reset_unique_id()

    def _update_rt_ranges(self, rts):
        for msl in rts.keys():
            rtmin, rtmax = self.rt_range(msl)

            if rtmin is None:  # either rtmin are both None, or both are not None
                rtmin = min(rts[msl])
                rtmax = max(rts[msl])
            else:
                rtmin = min(min(rts[msl]), rtmin)
                rtmax = max(max(rts[msl]), rtmax)

            self._info["rt_ranges"][msl] = (rtmin, rtmax)

        self._reset_unique_id()

    @contextmanager
    def spectra_for_modification(self):
        """contextmanager. in this context one can change spectra attributes like
        rt, ms_level, peaks or polarity"""

        spectra = MutableSpectra(self)
        yield spectra
        self.spectra._load_scan_numbers()

        mzmins, mzmaxs = defaultdict(list), defaultdict(list)
        rts = defaultdict(list)
        polarities = set()
        for spec in spectra:
            peaks = spec.peaks
            ms_level = spec.ms_level
            rt = spec.rt
            polarity = spec.polarity
            mzmin = peaks[:, 0].min()
            mzmax = peaks[:, 0].max()
            mzmins[ms_level].append(mzmin)
            mzmaxs[ms_level].append(mzmax)
            mzmins[None].append(mzmin)
            mzmaxs[None].append(mzmax)
            rts[ms_level].append(rt)
            rts[None].append(rt)
            polarities.add(polarity)
        mz_ranges = {}
        for ms_level in mzmins.keys():
            mz_ranges[ms_level] = (min(mzmins[ms_level]), max(mzmaxs[ms_level]))

        rt_ranges = {}
        for ms_level in rts.keys():
            rt_ranges[ms_level] = (min(rts[ms_level]), max(rts[ms_level]))

        ms_levels = set(mz_ranges.keys()) - {None}
        info = {
            "rt_ranges": rt_ranges,
            "mz_ranges": mz_ranges,
            "ms_levels": ms_levels,
            "polarities": polarities,
        }
        self._info.update(info)
        self._reset_unique_id()


class ImmutableMSChromatograms:
    def __init__(self, peakmap):
        self._parent = peakmap
        self._conn = peakmap._conn
        self._access_name = peakmap._access_name
        self._chromatograms = []
        self._load_chromatograms()

    def __len__(self):
        return len(self._chromatograms)

    def _load_chromatograms(self):
        if not table_exists(self._conn, f"{self._access_name}_chromatograms"):
            return
        self._chromatograms = [
            MSChromatogram(
                mz,
                precursor_mz,
                np.frombuffer(rts, dtype=np.float32),
                np.frombuffer(intensities, dtype=np.float32),
                type_,
            )
            for mz, precursor_mz, rts, intensities, type_ in self._conn.execute(
                "SELECT mz, precursor_mz, rts, intensities, type from"
                f" {self._access_name}_chromatograms ORDER BY mz, precursor_mz;"
            )
        ]

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return len(self) == len(other) and all(s0 == s1 for s0, s1 in zip(self, other))

    def __iter__(self):
        return iter(self._chromatograms)

    def __getitem__(self, index):
        return self._chromatograms.__getitem__(index)


class SpectraBase:
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return len(self) == len(other) and all(s0 == s1 for s0, s1 in zip(self, other))


class ImmutableSpectra(SpectraBase):
    def __init__(self, peakmap, is_mutable=False):
        self._parent = peakmap
        self._conn = peakmap._conn
        self._access_name = peakmap._access_name
        self._scan_numbers = []
        self._load_scan_numbers()
        self._is_mutable = is_mutable

    def __len__(self):
        return len(self._scan_numbers)

    def _load_scan_numbers(self):
        rows = self._scan_numbers = self._conn.execute(
            f"SELECT scan_number from {self._access_name}_spectra ORDER BY scan_number;"
        ).fetchall()
        self._scan_numbers = [row[0] for row in rows]

    def __iter__(self):
        return (self[i] for i in range(len(self)))

    def __getitem__(self, index):
        if isinstance(index, slice):
            start = 0 if index.start is None else index.start
            stop = self.size if index.stop is None else index.stop
            step = 1 if index.step is None else index.step
            return [
                BoundSpectrum(self, self._scan_numbers[i])
                for i in range(start, stop, step)
            ]
        assert isinstance(index, int)
        if index < 0:
            index += len(self)
        return BoundSpectrum(self, self._scan_numbers[index])

    def add_spectrum(self, spectrum):
        raise TypeError(
            "you must use the PeakMap.spectra_for_modification"
            " context manager in case you want to modify spectra"
        )


class MutableSpectra(ImmutableSpectra):
    def __init__(self, peakmap):
        super().__init__(peakmap, is_mutable=True)

    def _add_spectra(self, spectra):
        if not len(spectra):
            return

        rts = defaultdict(list)
        mzmins = defaultdict(list)
        mzmaxs = defaultdict(list)
        polarities = set()

        for spectrum in spectra:
            ms_level = spectrum.ms_level

            rt = spectrum.rt
            insert_peaks(
                self._conn,
                self._access_name,
                spectrum.peaks,
                rt,
                ms_level,
                spectrum.polarity,
                spectrum.precursors,
                spectrum.scan_number,
            )
            rts[ms_level].append(rt)
            rts[None].append(rt)
            polarities.add(spectrum.polarity)

            mzmins[spectrum.ms_level].append(min(spectrum.peaks[:, 0]))
            mzmins[None].append(min(spectrum.peaks[:, 0]))

            mzmaxs[spectrum.ms_level].append(max(spectrum.peaks[:, 0]))
            mzmaxs[None].append(max(spectrum.peaks[:, 0]))

        self._parent._update_rt_ranges(rts)
        self._parent._update_mz_ranges(mzmins, mzmaxs)
        self._parent._update_polarities(polarities)
        self._parent._reset_unique_id()
        self._conn.commit()
        self._load_scan_numbers()

    def add_spectrum(self, spectrum):
        self._add_spectra([spectrum])

    def _transform_rt(self, transform):
        old = self._conn.execute(
            f"""SELECT scan_number, rt FROM {self._access_name}_spectra"""
        )

        if not old:
            return

        sns, rts = zip(*old)
        rts_transformed = pyopenms.transform_rt_values(transform, rts)

        self._conn.executemany(
            f"UPDATE {self._access_name}_spectra SET rt = ? WHERE scan_number = ?;",
            zip(rts_transformed, sns),
        )
        self._conn.commit()
        return

    def _transform_mz(self, transform):
        cursor = self._conn.execute(
            f"""
            SELECT rt, mzs
            FROM   {self._access_name}_spectra
            WHERE  ms_level = 1
            """
        )

        updates = []

        for row in cursor:
            rt = row[0]
            mzs = np.frombuffer(row[1])
            mzs_transformed = transform(mzs).tobytes()
            updates.append((mzs_transformed, rt))

        cursor = self._conn.executemany(
            f"""
            UPDATE {self._access_name}_spectra
            SET mzs = ?
            WHERE rt = ?
            """,
            updates,
        )
        self._conn.commit()


class DbBackedProperty:
    """Property which fetches / updated value from/to db table on demand"""

    def __init__(self, get_function, set_function=None):
        self.get_function = get_function
        self.set_function = set_function

    def __get__(self, instance, owner):
        if instance is not None and not instance._loaded:
            instance._load()
        return self.get_function(instance)

    def __set__(self, instance, value):
        self.set_function(instance, value)
        instance._loaded = False


db_backed_property = DbBackedProperty


class ChromatogramType(enum.Enum):
    MASS_CHROMATOGRAM = 0
    TOTAL_ION_CURRENT_CHROMATOGRAM = 1
    SELECTED_ION_CURRENT_CHROMATOGRAM = 2
    BASEPEAK_CHROMATOGRAM = 3
    SELECTED_ION_MONITORING_CHROMATOGRAM = 4
    SELECTED_REACTION_MONITORING_CHROMATOGRAM = 5
    ELECTROMAGNETIC_RADIATION_CHROMATOGRAM = 6
    ABSORPTION_CHROMATOGRAM = 7
    EMISSION_CHROMATOGRAM = 8


class MSChromatogram:
    def __init__(self, mz, precursor_mz, rts, intensities, type_):
        self._mz = mz
        self._precursor_mz = precursor_mz
        self._rts = rts
        self._intensities = intensities
        if isinstance(type_, str):
            type_ = ChromatogramType[type_]
        self._type = type_

    def __str__(self):
        rtmin, rtmax = self.rt_range()
        rtmin, rtmax = round(rtmin, 1), round(rtmax, 1)
        return (
            f"MSChromatogram({self.type}, mz={self._mz},"
            f" precursor_mz={self._precursor_mz}, length={len(self)},"
            f" rt_range={rtmin!s}..{rtmax!s})"
        )

    def __repr__(self):
        return f"<MSChromatogram length={len(self)}>"

    @classmethod
    def _load_from_pickle(clz, bytes_):
        return pickle.loads(bytes_)

    def __len__(self):
        return len(self._rts)

    def rt_range(self):
        return min(self._rts), max(self._rts)

    @property
    def available_types(self):
        return [item.name for item in ChromatogramType]

    @property
    def type(self):
        return ChromatogramType(self._type).name

    @property
    def mz(self):
        return self._mz

    @property
    def precursor_mz(self):
        return self._precursor_mz

    @property
    def rts(self):
        return self._rts

    @property
    def intensities(self):
        return self._intensities

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return (
            self.mz == other.mz
            and self.precursor_mz == other.precursor_mz
            and np.all(self.rts == other.rts)
            and np.all(self.intensities == other.intensities)
        )


class BoundSpectrum:
    def __init__(self, parent, scan_number):
        self._conn = parent._conn
        self._access_name = parent._access_name
        self._scan_number = scan_number
        self._loaded = False
        self._is_mutable = parent._is_mutable
        self._precursors = None

    def __str__(self):
        npeaks = self.peaks.shape[0]
        return (
            f"Spectrum(scan_number={self.scan_number} rt={self.rt},"
            f" ms_level={self.ms_level}, polarity={self.polarity},"
            f" n_peaks={npeaks})"
        )

    def __repr__(self):
        npeaks = self.peaks.shape[0]
        return f"<BoundSpectrum n_peaks={npeaks}>"

    def __getstate__(self):
        raise PicklingError(
            "pickling a BoundSpectrum does not work, call .unbind() first"
        )

    def unbind(self):
        """dettaches spectrum from peakmap"""
        return Spectrum(
            self._scan_number,
            self.rt,
            self.ms_level,
            self.polarity,
            self.precursors,
            self.peaks,
        )

    def __eq__(self, other):
        if not isinstance(other, (BoundSpectrum, Spectrum)):
            return False

        return (
            self.rt == other.rt
            and self.ms_level == other.ms_level
            and self.polarity == other.polarity
            and self.scan_number == other.scan_number
            and self.peaks.shape == other.peaks.shape
            and np.all(self.mzs == other.mzs)
            and np.all(self.intensities == other.intensities)
        )

    def _get_peaks(self):
        return self._peaks

    def check(method):
        @wraps(method)
        def inner(self, *a, **kw):
            if not self._is_mutable:
                raise TypeError(
                    "spectrum must not be modified."
                    " use the PeakMap.spectra_for_modification context manager instead"
                )
            return method(self, *a, **kw)

        return inner

    @check
    def _set_peaks(self, peaks):
        assert isinstance(peaks, np.ndarray)
        assert peaks.dtype == np.float64
        assert peaks.shape[1] == 2, "need mz and intensity values as separate columns"
        mzs = peaks[:, 0]
        iis = peaks[:, 1].astype(np.float32)
        self._conn.execute(
            f"""
            UPDATE {self._access_name}_spectra
            SET mzs = ?, intensities = ?
            WHERE scan_number = ?
            """,
            (mzs.tobytes(), iis.tobytes(), self.scan_number),
        )
        self._conn.commit()

    peaks = db_backed_property(_get_peaks, _set_peaks)

    def _get_scan_number(self):
        return self._scan_number

    @property
    def scan_number(self):
        return self._scan_number

    def _get_polarity(self):
        return self._polarity

    @check
    def _set_polarity(self, p):
        assert isinstance(p, str) and p in "+-0"
        self._set("polarity", p)

    polarity = db_backed_property(_get_polarity, _set_polarity)

    def _get_ms_level(self):
        return self._ms_level

    @check
    def _set_ms_level(self, ms_level):
        assert isinstance(ms_level, int) and ms_level >= 1
        self._set("ms_level", ms_level)

    ms_level = db_backed_property(_get_ms_level, _set_ms_level)

    def _get_rt(self):
        return self._rt

    @check
    def _set_rt(self, rt):
        assert isinstance(rt, (int, float)) and rt >= 0
        self._set("rt", rt)

    rt = db_backed_property(_get_rt, _set_rt)

    def _get_mzs(self):
        return self._mzs

    def _set_mzs(self, values):
        raise TypeError("please set the peaks attribute and not the mzs")

    mzs = db_backed_property(_get_mzs, _set_mzs)

    def _get_intensities(self):
        return self._intensities

    def _set_intensities(self, values):
        raise TypeError("please set the peaks attribute and not the intensities")

    intensities = db_backed_property(_get_intensities, _set_intensities)

    def _set(self, col_name, value):
        self._conn.execute(
            f"UPDATE {self._access_name}_spectra SET {col_name}  = {value!r} "
            f"WHERE scan_number = {self.scan_number};"
        )
        self._conn.commit()

    @property
    def precursors(self):
        if self._precursors is None:
            self._load_precursors()
        return self._precursors

    def _load_precursors(self):
        self._precursors = self._conn.execute(
            f"SELECT mz, intensity, charge FROM {self._access_name}_precursors"
            f" WHERE scan_number = {self._scan_number};"
        ).fetchall()

    def _load(self):
        rows = self._conn.execute(
            f"SELECT * FROM {self._access_name}_spectra"
            f" WHERE scan_number={self._scan_number};"
        ).fetchall()
        if not rows:
            raise RuntimeError(
                f"empty result when loading spectrum {self._scan_number} "
                f"from {self._access_name}_spectra"
            )
        row = rows[0]
        self._scan_number = row[0]
        self._polarity = row[1]
        self._ms_level = row[2]
        self._rt = row[3]

        self._mzs = np.frombuffer(row[4], dtype=np.float64)
        self._intensities = np.frombuffer(row[5], dtype=np.float32)
        self._peaks = np.hstack((self._mzs[:, None], self._intensities[:, None]))


class Spectrum:
    def __init__(self, scan_number, rt, ms_level, polarity, precursors, peaks):
        self.scan_number = scan_number
        self.rt = rt
        self.ms_level = ms_level
        self.polarity = polarity
        self.precursors = precursors
        self.peaks = peaks
        self.mzs = peaks[:, 0]
        self.intensities = peaks[:, 1]

    def unbind(self):
        """dettaches spectrum from peakmap"""
        return self


def create_table(access_name="peakmap", conn=None):
    if conn is None:
        conn = Connection()
    _create_spectra_table(conn, access_name)
    _create_precursors_table(conn, access_name)
    _create_chromatograms_table(conn, access_name)
    conn.commit()
    return conn, access_name


def _create_spectra_table(conn, access_name):
    conn.execute(
        f"""CREATE TABLE {access_name}_spectra (
                        -- spectrum_index INTEGER UNIQUE
                        -- ,
                        scan_number  INTEGER UNIQUE
                        , polarity     TEXT
                        , ms_level     INTEGER
                        , rt           FLOAT
                        , mzs          BLOB
                        , intensities  BLOB
                        , hash         TEXT
                        --, mz         FLOAT
                        --, intensity  INTEGER
                        );"""
    )


def _create_precursors_table(conn, access_name):
    conn.execute(
        f"""CREATE TABLE {access_name}_precursors (
                        scan_number INTEGER
                        , mz          FLOAT
                        , intensity   FLOAT
                        , charge      INTEGER
                        , hash        TEXT
                        );"""
    )


def _create_chromatograms_table(conn, access_name):
    conn.execute(
        f"""CREATE TABLE IF NOT EXISTS {access_name}_chromatograms (
                        mz           FLOAT
                        , precursor_mz FLOAT
                        , rts          BLOB
                        , intensities  BLOB
                        , type         int
                        , hash         TEXT
                        );"""
    )


def create_indices(conn, access_name):
    conn.execute(f"CREATE INDEX {access_name}_i1 on {access_name}_spectra (ms_level);")
    conn.execute(
        f"CREATE INDEX {access_name}_i2 on {access_name}_spectra (ms_level, rt);"
    )
    conn.execute(
        f"CREATE INDEX  {access_name}_i3 on {access_name}_precursors (scan_number);"
    )
    conn.execute(
        f"CREATE INDEX  {access_name}_i4 on {access_name}_spectra (scan_number);"
    )
    conn.commit()


def insert_chromatogram(conn, access_name, mz, precursor_mz, peaks, type_):
    rts, iis = peaks
    assert isinstance(rts, np.ndarray)
    assert isinstance(iis, np.ndarray)

    rts = rts.astype(np.float32)
    iis = iis.astype(np.float32)

    values = [mz, precursor_mz, rts.tobytes(), iis.tobytes(), type_]
    hash_ = md5_hexdigest(*values)

    place_holders = ", ".join("?" * len(values))

    conn.execute(
        f"INSERT INTO {access_name}_chromatograms VALUES ({place_holders}, ?)",
        values + [hash_],
    )
    # no commit here, degrades performance!


def insert_peaks(
    conn, access_name, peaks, rt, ms_level, polarity, precursors, scan_number
):
    mzs = peaks[:, 0]
    iis = peaks[:, 1]
    assert isinstance(mzs, np.ndarray)
    assert isinstance(iis, np.ndarray)

    assert mzs.dtype == np.float64, "need full resolution"
    iis = iis.astype(np.float32)

    values = [scan_number, polarity, ms_level, rt, mzs.tobytes(), iis.tobytes()]
    hash_ = md5_hexdigest(*values)

    place_holders = ", ".join("?" * len(values))

    conn.execute(
        f"INSERT INTO {access_name}_spectra VALUES ({place_holders}, ?)",
        values + [hash_],
    )

    if precursors:
        insert_precursors(conn, access_name, scan_number, precursors)

    # no commit here, degrades performance!


def insert_precursors(conn, access_name, scan_number, precursors):
    values = (
        (scan_number, mz, ii, charge, md5_hexdigest(scan_number, mz, ii, charge))
        for (mz, ii, charge) in precursors
    )

    conn.executemany(
        f"""
            INSERT INTO {access_name}_precursors VALUES (?, ?, ?, ?, ?)
            """,
        values,
    )

    # no commit here, degrades performance!


def representing_mz_peak(conn, access_name, mzmin, mzmax, rtmin, rtmax, ms_level):
    rtmin = max(0, rtmin)
    rtmax = max(0, rtmax)
    mzmin = max(0, mzmin)
    mzmax = max(0, mzmax)

    cursor = conn.execute(
        f"""
        SELECT mzs, intensities
        FROM   {access_name}_spectra
        WHERE  ms_level = {ms_level}
        AND    rt >= {rtmin}
        AND    rt <= {rtmax}"""
    )

    all_mzs = []
    intensities = []

    for row in cursor:
        mzs = np.frombuffer(row[0])
        mask = (mzmin <= mzs) * (mzs <= mzmax)
        if not np.any(mask):
            continue
        all_mzs.extend(mzs[mask])
        iis = np.frombuffer(row[1], dtype=np.float32)
        intensities.extend(iis[mask])

    if not all_mzs:
        return None

    mzs = np.array(all_mzs, dtype=np.float64)
    weights = np.log(1 + np.array(intensities, dtype=np.float64))

    return mzs @ weights / np.sum(weights)


def chromatogram(
    conn,
    access_name,
    mzmin,
    mzmax,
    rtmin,
    rtmax,
    ms_level,
    precursormzmin,
    precursormzmax,
    polarity,
):
    stmt = f"SELECT S.rt, S.mzs, S.intensities FROM {access_name}_spectra as S"

    conditions = [f"S.ms_level = {ms_level}"]

    if precursormzmin is not None or precursormzmax is not None:
        if ms_level == 1:
            raise ValueError(
                "extracting chromatograms using precursor windows"
                " does not make sense on ms level 1"
            )

        stmt += f"""
        JOIN {access_name}_precursors as P
        ON   P.scan_number = S.scan_number
        """

        if precursormzmin is not None:
            conditions.append(f"P.mz >= {precursormzmin}")
        if precursormzmax is not None:
            conditions.append(f"P.mz <= {precursormzmax}")

    if rtmin is not None:
        conditions.append(f"S.rt >= {rtmin}")
    if rtmax is not None:
        conditions.append(f"S.rt <= {rtmax}")

    if polarity is not None:
        if polarity not in ["+", "-"]:
            raise ValueError("polarity must be either '+' or '-'")

        conditions.append(f"S.polarity = '{polarity}'")

    stmt += f" WHERE {' AND '.join(conditions)}"

    cursor = conn.execute(stmt)

    rts = []
    intensities = []

    # we might get duplicates because of precursor filtering of multiplexed data
    # so we track these:
    seen_rts = set()

    for row in cursor:
        rt = row[0]
        if rt in seen_rts:
            continue
        seen_rts.add(rt)
        rts.append(rt)
        mzs = np.frombuffer(row[1])
        mask = mzs >= 0
        if mzmin is not None:
            mask *= mzmin <= mzs
        if mzmax is not None:
            mask *= mzs <= mzmax
        if not np.any(mask):
            intensities.append(0)
            continue
        iis = np.frombuffer(row[2], dtype=np.float32)
        intensity = np.sum(iis[mask])
        intensities.append(intensity)

    return Chromatogram(
        np.array(rts, dtype=np.float64), np.array(intensities, dtype=np.float32)
    )


def extract_spectrum(mspec):
    return mspec.extract_spectrum()


def to_openms_spectrum(s):
    return pyopenms.to_openms_spectrum(
        s.rt, s.ms_level, s.polarity, s.precursors, s.mzs, s.intensities, s.scan_number
    )
