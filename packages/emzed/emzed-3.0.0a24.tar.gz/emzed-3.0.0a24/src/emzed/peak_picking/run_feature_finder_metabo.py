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


import locale
import os
import pickle
import time
import warnings

from emzed.ms_data import PeakMap
from emzed.pyopenms import decode, encode, pyopenms
from emzed.table import Table
from emzed.table.table_utils import MzType, RtType

std_config = {
    "epdet_width_filtering": "auto",
    "epdet_min_fwhm": 3.0,
    "common_chrom_fwhm": 25.0,
    "mtd_min_trace_length": 3.0,
    "ffm_local_mz_range": 15.0,
    "ffm_isotope_filtering_model": "none",
}


class RunFeatureFinderMetabo:
    _doc = None

    def __call__(
        self,
        peak_map,
        ms_level=None,
        verbose=True,
        run_feature_grouper=True,
        split_by_precursors_mz_tol=0.0,
        **parameters,
    ):
        """
        runs openms feature finder on peakmap.

        :param peak_map: emzed PeakMap object
        :param ms_level: ms level to pick peaks from, default picks from MS1
        :param verbose:  set to False to supress output
        :param run_feature_grouper:  also run feature grouper from openms.
        :param split_by_precursors_mz_tol: ms2 peakmaps are split by precusor first. this
                                          is the tolearance used for
                                          PeakMap.split_by_precursors. Set to  `None` to
                                          disable this!.
        """
        assert isinstance(peak_map, PeakMap)

        if not run_feature_grouper and any(
            k.startswith("ffm_") for k in parameters.keys()
        ):
            warnings.warn(
                "feature grouper related parameters are ignored as you set"
                " run_feature_grouper to False"
            )

        if split_by_precursors_mz_tol is None or ms_level in (1, None):
            tab = _run_feature_finder_metabo(
                peak_map,
                ms_level,
                verbose,
                run_feature_grouper,
                **parameters,
            )
            tab = _fix_ordering_and_enumerate(tab)
            return tab

        peak_tables = []
        num_warnings = 0
        MAX_WARNINGS = 5
        MIN_SPECTRA_NEEDED_BY_OPENMS = 3

        offset_feature_id = 0
        for precursors, sub_peak_map in sorted(
            peak_map.split_by_precursors(split_by_precursors_mz_tol).items()
        ):
            if len(sub_peak_map) < MIN_SPECTRA_NEEDED_BY_OPENMS:
                if num_warnings < MAX_WARNINGS:
                    warnings.warn(
                        f"not enough spectra for precusors {precursors}. you might consider"
                        " to increase split_by_precursors_mz_tol to fix this."
                    )
                elif num_warnings == MAX_WARNINGS:
                    warnings.warn("... skip further warnings")
                num_warnings += 1
                continue
            peaks = _run_feature_finder_metabo(
                sub_peak_map,
                ms_level,
                verbose,
                run_feature_grouper,
                **parameters,
            )
            peaks.add_column_with_constant_value("precursors", precursors, object)
            if run_feature_grouper:
                peaks.replace_column(
                    "feature_id", peaks.feature_id + offset_feature_id, int
                )
                if len(peaks):
                    offset_feature_id = peaks.feature_id.max().eval() + 1
            peak_tables.append(peaks)

        if not peak_tables:
            tab = _setup_final_table([], peak_map, run_feature_grouper)
        else:
            tab = Table.stack_tables(peak_tables)

        tab = _fix_ordering_and_enumerate(tab)
        return tab

    @property
    def __doc__(self):
        if self._doc is None:
            self._doc = _setup_doc_string()
        return self._doc


run_feature_finder_metabo = RunFeatureFinderMetabo()


def _run_feature_finder_metabo(
    peak_map,
    ms_level,
    verbose,
    run_feature_grouper,
    **parameters,
):
    config_params = std_config.copy()
    config_params.update(parameters)

    config_params = {encode(k): v for (k, v) in config_params.items()}

    if not verbose:

        def info(*a, **kw):
            return

    else:
        info = print

    info("RUN FEATURE FINDER METABO")

    start_at = time.time()

    (mtd_params, epdet_params, ffm_params, all_params) = _setup_mff_params(
        config_params
    )

    def dump_param(prefix, all_params=all_params):
        sub_params = all_params.copy(prefix)
        for k, v in sorted(sub_params.items()):
            k = decode(k)
            v = decode(v)
            info(("%s " % (k,)).ljust(35, "."), v)

    info("COMMON PARAMETERS")
    info()
    dump_param("common_")
    info()
    info("PARAMS MASS TRACE DETECTION:")
    info()
    dump_param("mtd_")
    info()
    info("PARAMS ELUTION PEAK DETECTION:")
    info()
    dump_param("epdet_")
    info()
    if run_feature_grouper:
        info("PARAMS FEATURE FINDER METABO:")
        info()
        dump_param("ffm_")
        info()

    # wrong locale can cause problems with the Metabo feature finder from OpenMS, which
    # fails to read some config files containing numercial values with a "." decimal
    # point, which is not the decimal point e.g. for german numbers. so we set:
    locale.setlocale(locale.LC_NUMERIC, "C")

    # extract peakmap and reset ms level to 1 to make openms peak picker work
    if ms_level is not None:
        peak_map = peak_map.extract(mslevelmin=ms_level, mslevelmax=ms_level)
        with peak_map.spectra_for_modification() as spectra:
            for spec in spectra:
                spec.ms_level = 1

    info()
    info("%d specs in peak map" % (len(peak_map),))

    mse = peak_map._to_openms_experiment()
    rows = pickle.loads(
        pyopenms.feature_finder(
            verbose, mse, mtd_params, epdet_params, run_feature_grouper, ffm_params
        )
    )

    # fix ms level again:
    if ms_level is not None:
        with peak_map.spectra_for_modification() as spectra:
            for spec in spectra:
                spec.ms_level = ms_level

    table = _setup_final_table(rows, peak_map, run_feature_grouper)

    needed = time.time() - start_at

    minutes = int(needed / 60)
    seconds = round(needed - 60 * minutes)

    info("found %d peaks" % len(table))
    info()
    info("needed %d minutes and %d seconds" % (minutes, seconds))
    info()

    return table


def _setup_doc_string():
    def _setup_doc_string():
        params = _build_params()

        yield "calls pyopenms MassTraceDetection + FeatureFindingMetabo"
        yield ""
        yield ":param peak_map: ``emzed.PeakMap``"
        yield ":param ms_level: optional specification of ms_level"
        yield ":param verbose: set to ``False`` to suppress output"
        yield (
            ":param run_feature_finder_metabo: set to ``False`` to suppress"
            " grouping of peaks to features"
        )

        def add_section(prefix, params=params):
            sub_params = params.copy(prefix)
            for k in sub_params.keys():
                e = params.getEntry(k)
                v = e.value
                if isinstance(v, (str, bytes)):
                    allowed = ", ".join("``%r``" % decode(vs) for vs in e.valid_strings)
                else:
                    allowed = None
                d = decode(e.description)
                v = decode(v)
                k = decode(k)
                yield ":param %s: %s" % (k, d)
                yield ""
                if allowed is None:
                    yield "    Default value: ``%r``." % (v,)
                else:
                    yield "    Default value: ``%r``, allowed values: %s." % (
                        v,
                        allowed,
                    )
                yield ""

        yield ""
        for heading, prefix in [
            ("Common Parameters", "common_"),
            ("Parameters Mass Trace Detector", "mtd_"),
            ("Elution Peak Detection", "epdet_"),
            ("Parameters Feature Finding Metabo", "ffm_"),
        ]:
            yield heading + ":"
            yield ""
            yield from add_section(prefix=prefix)

        yield ""
        yield (
            ":returns: `emzed.Table` with columns feature_id, mz, mzmin, mzmax,"
            " rt, rtmin, rtmax, intensity, quality, fwhm, and z."
        )

    return "\n".join(_setup_doc_string())


def _build_params():
    # pyopenms 2.4.0 defaults:
    mtd_defaults = {
        b"mass_error_ppm": 20.0,
        b"max_trace_length": -1.0,
        b"min_sample_rate": 0.5,
        b"min_trace_length": 5.0,
        b"noise_threshold_int": 10.0,
        b"quant_method": b"area",
        b"reestimate_mt_sd": b"true",
        b"trace_termination_criterion": b"outlier",
        b"trace_termination_outliers": 5,
    }
    epdet_defaults = {
        b"masstrace_snr_filtering": b"false",
        b"max_fwhm": 60.0,
        b"min_fwhm": 3.0,
        b"width_filtering": b"fixed",
    }

    ffm_defaults = {
        b"charge_lower_bound": 1,
        b"charge_upper_bound": 3,
        b"enable_RT_filtering": b"true",
        b"isotope_filtering_model": b"metabolites (5% RMS)",
        b"local_mz_range": 6.5,
        b"local_rt_range": 10.0,
        b"mz_scoring_13C": b"false",
        b"remove_single_traces": b"false",
        b"report_chromatograms": b"false",
        b"report_convex_hulls": b"true",
        b"report_summed_ints": b"false",
        b"use_smoothed_intensities": b"true",
    }

    mtd_params = pyopenms.MassTraceDetection().getDefaults()
    mtd_params.remove("chrom_peak_snr")
    for key, value in mtd_defaults.items():
        mtd_params.setValue(key, value)

    epdet_params = pyopenms.ElutionPeakDetection().getDefaults()
    epdet_params.remove("chrom_peak_snr")
    epdet_params.remove("chrom_fwhm")
    for key, value in epdet_defaults.items():
        epdet_params.setValue(key, value)

    ffm_params = pyopenms.FeatureFindingMetabo().getDefaults()
    ffm_params.remove("chrom_fwhm")

    for key, value in ffm_defaults.items():
        ffm_params.setValue(key, value)

    ffm_params.setValue("report_convex_hulls", b"true")

    common_params = pyopenms.Param()
    common_params.setValue("chrom_peak_snr", 3.0)
    common_params.setValue("chrom_fwhm", 5.0)

    combined_params = pyopenms.Param()
    combined_params.insert("common_", common_params)
    combined_params.insert("mtd_", mtd_params)
    combined_params.insert("epdet_", epdet_params)
    combined_params.insert("ffm_", ffm_params)

    return combined_params


def _setup_mff_params(dd):
    assert isinstance(dd, dict)

    params = _build_params()

    for k, v in dd.items():
        default_value = params.get(k)
        if default_value is not None:
            type_ = type(default_value)
            dd[k] = type_(v)

    params.update(dd)

    mtd_params = params.copy("mtd_", True)
    epdet_params = params.copy("epdet_", True)
    common_params = params.copy("common_", True)

    mtd_params.insert("", common_params)
    mtd_params.remove("chrom_fwhm")

    epdet_params.insert("", common_params)

    ffm_params = params.copy("ffm_", True)
    ffm_params.insert("", common_params)
    ffm_params.remove("noise_threshold_int")
    ffm_params.remove("chrom_peak_snr")

    return mtd_params, epdet_params, ffm_params, params


def _fix_ordering_and_enumerate(tab):
    """peaks are reported in different order by pyopenms on linux vs mac.
    this function fixex this."""
    tab = tab.sort_by("quality", "rt", "mz", ascending=(False, True, True))
    tab.add_enumeration()
    new_feature_ids = {}
    new_feature_id = 0
    for id_, feature_id in zip(tab.id, tab.feature_id):
        if feature_id is None:
            continue
        if feature_id in new_feature_ids:
            continue
        new_feature_ids[feature_id] = new_feature_id
        new_feature_id += 1
    tab.replace_column(
        "feature_id", tab.apply(new_feature_ids.get, tab.feature_id), int
    )
    return tab


def _setup_final_table(rows, peak_map, run_feature_grouper):
    column_names = [
        "feature_id",
        "mz",
        "mzmin",
        "mzmax",
        "rt",
        "rtmin",
        "rtmax",
        "intensity",
        "quality",
        "fwhm",
        "z",
    ]

    column_types = [
        int,
        MzType,
        MzType,
        MzType,
        RtType,
        RtType,
        RtType,
        float,
        float,
        RtType,
        int,
    ]

    tab = Table.create_table(column_names, column_types, rows=rows)
    tab.set_col_format("intensity", "%.2e")
    tab.set_col_format("quality", "%.2e")

    tab.add_column_with_constant_value("peakmap", peak_map, PeakMap)
    if run_feature_grouper:
        tab.add_column(
            "feature_size",
            tab.group_by(tab.feature_id).aggregate(len, tab.feature_id),
            int,
            insert_after="feature_id",
        )
    else:
        tab.add_column_with_constant_value(
            "feature_size", None, int, insert_after="feature_id"
        )

    src = peak_map.meta_data.get("source", "")
    tab.add_column_with_constant_value("source", src, str)
    if src:
        tab.title = "metabo features from %s" % os.path.basename(src)
    else:
        tab.title = "metabo features"

    return tab
