"""
Mixture-ratio sweep: hand the user the Isp-vs-MR curve and the peak-Isp MR so
"pick a mixture ratio" has feedback instead of being a blind slider.

Pure composition over EngineDesign.compute() - this is NOT called from inside
compute() and adds no physics constant, so it moves no validate.py spot check
(every propellant-pair spot check runs at its engine's real MR, which is
generally NOT the Isp-peak MR - see ASSUMPTIONS.md's note on why there is no
off-peak c* debit). A monopropellant has no mixture ratio, so the curve
degenerates to a single point.
"""
import dataclasses

from . import combustion
from .design import EngineDesign


def isp_vs_mr_curve(design, n=25):
    """
    Sweep mixture ratio across the propellant pair's literature-anchored table
    range (combustion.mr_bounds) holding every other design input fixed, and
    report engine vacuum Isp / chamber vacuum Isp / vacuum thrust at each point
    plus the MR that maximises engine Isp.

    Returns dict(mr, isp_vac_engine_s, isp_vac_chamber_s, thrust_vac_n, peak_mr,
    peak_isp_s, is_monopropellant). All lists are len n (len 1 for a
    monopropellant).
    """
    pair = design.propellant_pair
    mono = combustion.is_monopropellant(pair)
    lo, hi = combustion.mr_bounds(pair)

    if mono or hi - lo < 1e-9:
        r = design.compute()
        return {
            "mr": [design.mixture_ratio],
            "isp_vac_engine_s": [r["isp_vac_engine_s"]],
            "isp_vac_chamber_s": [r["isp_vac_chamber_s"]],
            "thrust_vac_n": [r["thrust_vac_n"]],
            "peak_mr": design.mixture_ratio,
            "peak_isp_s": r["isp_vac_engine_s"],
            "is_monopropellant": mono,
        }

    mrs, isp_eng, isp_ch, thr = [], [], [], []
    for i in range(n):
        mr = lo + (hi - lo) * i / (n - 1)
        r = dataclasses.replace(design, mixture_ratio=mr).compute()
        mrs.append(mr)
        isp_eng.append(r["isp_vac_engine_s"])
        isp_ch.append(r["isp_vac_chamber_s"])
        thr.append(r["thrust_vac_n"])

    peak_i = max(range(n), key=lambda i: isp_eng[i])
    return {
        "mr": mrs,
        "isp_vac_engine_s": isp_eng,
        "isp_vac_chamber_s": isp_ch,
        "thrust_vac_n": thr,
        "peak_mr": mrs[peak_i],
        "peak_isp_s": isp_eng[peak_i],
        "is_monopropellant": False,
    }


if __name__ == "__main__":
    # Every bipropellant sweep is well-formed and peak_mr genuinely maximises Isp.
    for pair in ("LOX/RP-1", "LOX/LH2", "LOX/CH4", "N2O4/MMH"):
        c = isp_vs_mr_curve(EngineDesign(propellant_pair=pair, cycle="pressure_fed"), n=21)
        lo, hi = c["mr"][0], c["mr"][-1]
        assert len(c["mr"]) == 21 and lo <= c["peak_mr"] <= hi
        assert c["peak_isp_s"] == max(c["isp_vac_engine_s"])
        edge = "endpoint" if c["peak_mr"] in (lo, hi) else "interior"
        print(f"{pair:>10}  peak Isp {c['peak_isp_s']:6.1f} s at MR {c['peak_mr']:.2f} ({edge})  "
              f"(range {lo:.2f}-{hi:.2f})")

    # LOX/RP-1 vacuum Isp genuinely peaks INSIDE its table range (kerolox has an
    # interior vac-Isp optimum; hydrolox's falls monotonically toward low MR, so
    # its "best" MR is the low endpoint - correct, not a bug).
    c = isp_vs_mr_curve(EngineDesign(propellant_pair="LOX/RP-1", cycle="pressure_fed"), n=21)
    assert c["mr"][0] < c["peak_mr"] < c["mr"][-1], c["peak_mr"]

    # A monopropellant degenerates to a single point.
    for pair in ("Hydrazine", "H2O2"):
        c = isp_vs_mr_curve(EngineDesign(propellant_pair=pair, cycle="pressure_fed",
                                          injector_type="catalyst_bed"))
        assert len(c["mr"]) == 1 and c["is_monopropellant"]
        assert c["peak_mr"] == c["mr"][0]
        print(f"{pair:>10}  single point: Isp {c['peak_isp_s']:6.1f} s (monopropellant)")

    print("mixture_ratio.py self-checks: OK")
