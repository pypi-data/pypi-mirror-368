import os
import sys
import tempfile
from functools import cache

from emzed import PeakMap, Table

from ..table.col_types import MzType, RtType
from .r_executor import RInterpreter


@cache
def get_r_version(rip):
    version = rip.version
    return "%s.%s" % (version["major"], version["minor"])


def setup_r_libs_variable(rip):
    import emzed.config

    subfolder = "r_libs_%s" % get_r_version(rip)
    r_libs_folder = os.path.join(emzed.config.folders.get_emzed_folder(), subfolder)
    r_libs = [path for path in os.environ.get("R_LIBS", "").split(os.pathsep) if path]
    if r_libs_folder not in r_libs:
        if not os.path.exists(r_libs_folder):
            os.makedirs(r_libs_folder)
        r_libs.insert(0, r_libs_folder)
        r_libs_str = os.pathsep.join(r_libs)
        os.environ["R_LIBS"] = r_libs_str
        rip.execute(f'.libPaths(c("{r_libs_str}", .libPaths()))')


def _extract_single_level_peakmap(ms_level, peak_map):
    if ms_level is None:
        ms_levels = peak_map.ms_levels()
        if len(ms_levels) > 1:
            raise Exception(
                "multiple msLevels in peakmap " "please specify ms_level in config"
            )
        ms_level = ms_levels.pop()

    temp_peakmap = peak_map.extract(mslevelmin=ms_level, mslevelmax=ms_level)
    return temp_peakmap


class CentwaveFeatureDetector:
    standard_config = dict(
        ppm=25,
        peakwidth=(20, 50),
        prefilter=(3, 100),
        snthresh=10,
        integrate=1,
        mzdiff=-0.001,
        noise=0,
        mzCenterFun="wMean",
        fitgauss=False,
        msLevel=None,
        verboseColumns=False,
        roiList=[],
        firstBaselineCheck=False,
        roiScales=[],
        extendLengthMSW=False,
        verboseBetaColumns=False,
    )

    def __init__(self, **kw):
        self.config = self.standard_config.copy()
        self.config.update(kw)
        self.r = RInterpreter(do_log=True)
        setup_r_libs_variable(self.r)
        if not self.is_xcms_installed():
            raise Exception(
                "XCMS 4 not installed yet. Please import and call"
                " emzed.peak_picking.install_xcms()"
            )

    def is_xcms_installed(self):
        self.r.execute("library(xcms)")
        response = self.r.execute("status <- require(xcms)")
        print(response.status)
        response = self.r.execute(
            "status <- 0; "
            "status <- require(xcms) "
            '   && startsWith(paste(packageVersion("xcms")), "4.")'
        )
        return getattr(response, "status", False)

    @staticmethod
    def install_xcms():
        r = RInterpreter(do_log=True)
        setup_r_libs_variable(r)
        r.execute(
            """
            if (!require("BiocManager", quietly = TRUE))
                install.packages("BiocManager", repos="http://cran.us.r-project.org")
            BiocManager::install("xcms")
        """
        )

    def process(self, peak_map):
        assert isinstance(peak_map, PeakMap)
        if len(peak_map) == 0:
            raise ValueError("empty peakmap")

        with tempfile.TemporaryDirectory() as td:
            temp_input = os.path.join(td, "input.mzML")

            peak_map.save(temp_input)

            if sys.platform == "win32":
                temp_input = temp_input.replace("\\", "\\\\")

            dd = self.config.copy()

            for k, v in dd.items():
                setattr(self.r, k, v)

            script = f"""
                    options(conflicts.policy = list(warn = FALSE))
                    library(xcms)
                    library(MsExperiment)
                    param <- CentWaveParam(
                        ppm = ppm,
                        peakwidth = peakwidth,
                        snthresh = snthresh,
                        prefilter = prefilter,
                        mzCenterFun = mzCenterFun,
                        integrate = integrate,
                        mzdiff = mzdiff,
                        fitgauss = fitgauss,
                        noise = noise,
                        verboseColumns = FALSE,
                        roiList = roiList,
                        firstBaselineCheck = firstBaselineCheck,
                        roiScales = as.vector(roiScales, mode="numeric"),
                        extendLengthMSW = extendLengthMSW
                        )
                    e <- readMsExperiment(c("{temp_input}"))
                    ok = TRUE;
                    """
            self.r.execute(script)
            print(self.r.ok, file=sys.stderr)

            script = """
                    res <- findChromPeaks(e, param);
                    ok2 = TRUE;
                    peaks <- data.frame(chromPeaks(res));
                    write(paste(peaks), stderr());
                    ok3 = TRUE;
                    """

            self.r.execute(script)
            print(self.r.ok2, file=sys.stderr)
            print(self.r.ok3, file=sys.stderr)

            script = """
                    # pyper returns one row data frame with NAN in case the
                    # original data.frame is empty, so we also compute the
                    # actual number of rows here:
                    npeaks <- nrow(peaks);
                    """

            print(script)

            self.r.execute(script)

        if self.r.npeaks is not None and self.r.npeaks > 0:
            peaks = self.r.peaks
            for col in ("mz", "mzmin", "mzmax"):
                peaks.set_col_type(col, MzType)
            for col in ("rt", "rtmin", "rtmax"):
                peaks.set_col_type(col, RtType)
        else:
            peaks = Table.create_table(
                "mz mzmin mzmax rt rtmin rtmax into intb maxo sn sample".split(),
                [MzType] * 3 + [RtType] * 3 + [float] * 4 + [int],
            )

        for col in ("into", "intb", "maxo", "sn"):
            peaks.set_col_format(col, "%.2e")
        peaks.drop_columns("sample")

        peaks.add_column_with_constant_value("centwave_config", dd, object, None)
        peaks.add_column_with_constant_value("peakmap", peak_map, PeakMap, None)

        src = peak_map.meta_data.get("source", "")
        peaks.add_column_with_constant_value("source", src, str, None)

        peaks.add_enumeration()
        peaks.meta_data["generator"] = "xcms.centwave"
        peaks.set_title(os.path.basename(src))
        return peaks
