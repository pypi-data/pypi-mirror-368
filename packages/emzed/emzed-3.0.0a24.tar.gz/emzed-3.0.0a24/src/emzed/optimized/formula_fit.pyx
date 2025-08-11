from emzed import MzType, Table

cimport cython


@cython.cdivision(True)
def formula_table(
    double min_mass,
    double max_mass,
    int c_low,
    int c_high,
    int h_low,
    int h_high,
    int n_low,
    int n_high,
    int o_low,
    int o_high,
    int p_low,
    int p_high,
    int s_low,
    int s_high,
    double h_to_c_min,
    double h_to_c_max,
    double n_to_c_min,
    double n_to_c_max,
    double o_to_c_min,
    double o_to_c_max,
    double p_to_c_min,
    double p_to_c_max,
    double s_to_c_min,
    double s_to_c_max,
    double mass_C,
    double mass_H,
    double mass_N,
    double mass_O,
    double mass_P,
    double mass_S,
    int apply_rule_2,
    int apply_rule_6,
):

    """
    This is a reduced Python version of HR2 formula generator,
    see http://fiehnlab.ucdavis.edu/projects/Seven_Golden_Rules/Software/

    This function generates a table containing molecular formulas consisting of elements
    C, H, N, O, P and S having a mass in range [**min_mass**, **max_mass**].
    For each element one can provide an given count or an inclusive range of atom counts
    considered in this process.

    If **apply_rule_2** is *True*, mass ratio rules (from "seven golden rules") and valence
    bond checks are used to avoid unrealistic compounds in the table, else all formulas
    explaining the given mass range are generated.

    Putting some restrictions on atomcounts, eg **C=(0, 100)**, can speed up the process
    tremendously.
    """

    # valence values for bound checks:
    cdef int valh = -1
    cdef int valc = +2
    cdef int valn = 1
    cdef int valo = 0
    cdef int valp = 3
    cdef int vals = 4

    cdef int c, h, n, o, p, s
    cdef int c_min, h_min, n_min, o_min, p_min, s_min
    cdef int c_max, h_max, n_max, o_max, p_max, s_max
    cdef double bond

    cdef double resmc_max, resms_max, resmp_max, resmo_max, resmn_max, resmh_max

    rows = []

    for c in range(c_low, c_high + 1):

        resmc_max = max_mass - c * mass_C
        s_max = min(s_high, <int>(resmc_max / mass_S))
        if c > 0:
            s_max = min(s_max, <int>(s_to_c_max * c))
        s_min = max(s_low, <int>(s_to_c_min * c))

        for s in range(s_min, s_max + 1):
            resms_max = resmc_max - s * mass_S
            p_max = min(p_high, <int>(resms_max / mass_P))
            if c > 0:
                p_max = min(p_max, <int>(p_to_c_max * c))
            p_min = max(p_low, <int>(p_to_c_min * c))

            for p in range(p_min, p_max + 1):
                resmp_max = resms_max - p * mass_P
                o_max = min(o_high, <int>(resmp_max / mass_O))
                if c > 0:
                    o_max = min(o_max, <int>(o_to_c_max * c))
                o_min = max(o_low, <int>(o_to_c_min * c))

                for o in range(o_min, o_max + 1):
                    resmo_max = resmp_max - o * mass_O
                    n_max = min(n_high, <int>(resmo_max / mass_N))
                    if c > 0:
                        n_max = min(n_max, <int>(n_to_c_max * c))
                    n_min = max(n_low, <int>(n_to_c_min * c))

                    if apply_rule_6 and o > 1 and p > 1 and s > 1:
                        if o >= 14 or p >= 3 or s >= 3:
                            break

                    for n in range(n_min, n_max + 1):
                        resmn_max = resmo_max - n * mass_N
                        h_max = min(h_high, <int>(resmn_max / mass_H))
                        if c > 0:
                            h_max = min(h_max, <int>(n_to_c_max * c))

                        h_min = max(h_low, <int>(h_to_c_min * c))

                        if apply_rule_6 and n > 3 and o > 3 and p > 3:
                            if n >= 11 or o >= 11 or p >=6:
                                break

                        if apply_rule_6 and p > 1 and s > 1 and n > 1:
                            if p >= 3 or s >= 3 or s >= 4:
                                break

                        if apply_rule_6 and n > 6 and o > 6 and s > 6:
                            if n >= 19 or o >= 14 or s >= 8:
                                break

                        for h in range(h_min, h_max + 1):
                            resmh_max = resmn_max - h * mass_H
                            if 0 <= resmh_max <= max_mass - min_mass:
                                bond = (
                                    2.0
                                    + c * valc
                                    + n * valn
                                    + o * valo
                                    + p * valp
                                    + s * vals
                                    + h * valh
                                ) / 2.0
                                if not apply_rule_2 or (bond >= 0 and bond % 1 != 0.5):
                                    mf = "C%d.H%d.N%d.O%d.P%d.S%d." % (c, h, n, o, p, s)
                                    mf = mf.replace("C0.", ".")
                                    mf = mf.replace("H0.", ".")
                                    mf = mf.replace("N0.", ".")
                                    mf = mf.replace("O0.", ".")
                                    mf = mf.replace("P0.", ".")
                                    mf = mf.replace("S0.", ".")
                                    mf = mf.replace("C1.", "C.")
                                    mf = mf.replace("H1.", "H.")
                                    mf = mf.replace("N1.", "N.")
                                    mf = mf.replace("O1.", "O.")
                                    mf = mf.replace("P1.", "P.")
                                    mf = mf.replace("S1.", "S.")
                                    mf = mf.replace(".", "")

                                    rows.append([mf, max_mass - resmh_max])

    rows = sorted(rows, key=lambda row: row[1])
    return Table.create_table(["mf", "m0"], [str, MzType], rows=rows)
