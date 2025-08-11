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


import pyopenms


def compute_spectra_alignments(spectra, mz_tolerance):
    """takes a list of spectra and groups peaks given mz_tolerance.
    it returns a list of lists. every inner list specifies the alignment of one input
    spectrum to its follower in the list.
    One assignment is a list of tuples, where the first entry is a peak index from the
    first list, the second entry is the index of a peak from the second spectrum.

    For example:

        if you run this method with a list or tuple of three spectra (s0, s1, s2) the
        return values will be [align_0_to_1, align_1_to_2]

        an alignment is a list [(i0, j0), (i1, j1),  ...]

        so that s0.peaks[i0, :] is assigned to s1.peaks[j0, :] and so on.
    """
    aligner = pyopenms.SpectrumAlignment()
    alignment = []
    conf = aligner.getDefaults()
    conf_d = conf.asDict()
    conf_d[b"is_relative_tolerance"] = b"false"  # b"true" not implemented yet!
    conf_d[b"tolerance"] = mz_tolerance
    conf.update(conf_d)
    aligner.setParameters(conf)

    openms_spectra = [pyopenms.to_openms_spectrum(s) for s in spectra]

    # create pairwise alignments
    alignments = []
    for s0, s1 in zip(openms_spectra, openms_spectra[1:]):
        alignment = []
        aligner.getSpectrumAlignment(alignment, s0, s1)
        alignments.append(alignment)

    return alignments
