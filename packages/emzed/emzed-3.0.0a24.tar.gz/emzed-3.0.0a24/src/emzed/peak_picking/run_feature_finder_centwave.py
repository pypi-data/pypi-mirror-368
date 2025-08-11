def _read_help():
    import pathlib

    here = pathlib.Path(__file__).absolute().parent
    return (here / "centwave.txt").read_text()


def run_feature_finder_centwave(
    peakmap,
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
):
    from emzed.r_connect import xcms_connector

    parameters = dict(
        ppm=ppm,
        peakwidth=peakwidth,
        prefilter=prefilter,
        snthresh=snthresh,
        integrate=integrate,
        mzdiff=mzdiff,
        noise=noise,
        mzCenterFun=mzCenterFun,
        fitgauss=fitgauss,
        msLevel=msLevel,
        verboseColumns=verboseColumns,
        roiList=roiList,
        firstBaselineCheck=firstBaselineCheck,
        roiScales=roiScales,
        extendLengthMSW=extendLengthMSW,
        verboseBetaColumns=verboseBetaColumns,
    )

    pp = xcms_connector.CentwaveFeatureDetector(**parameters)
    return pp.process(peakmap)


run_feature_finder_centwave.__doc__ = _read_help()


def install_xcms():
    from emzed.r_connect import xcms_connector

    xcms_connector.CentwaveFeatureDetector.install_xcms()
