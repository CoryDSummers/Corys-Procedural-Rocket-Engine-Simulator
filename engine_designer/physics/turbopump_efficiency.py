"""
DERIVED pump and turbine efficiency for the turbopump - computed from the
machinery design (specific speed, stage count, size, turbine staging /
pitchline / pressure ratio / admission), NOT picked from a tier constant.

Same epistemic status as physics/GG_GAS_PROPERTIES: the SP-8107 monographs give
real per-engine efficiencies (Table II pumps, Table III turbines) and the rules
that drive them ("centrifugal-pump efficiency peaks over stage Ns 1300-2500",
"turbine efficiency ~ f(pitchline velocity) for given inlet T and PR", "small
low-hp turbines use partial admission"), but NO published eta-vs-Ns or
eta-vs-U/C0 curve. So the curve SHAPES here are calibrated engineering choices
fitted to the real anchors below and pinned by
validate.py::run_turbopump_efficiency_check(). Run `python3 -m
engine_designer.physics.turbopump_efficiency` to see the fit.

The `build_quality` multiplier (from physics/turbopump_tech.py's era tiers -
0.93 / 1.00 / 1.04) is the ONLY thing the old tier catalog now contributes;
`mature` = 1.00 so an F-1-class design recovers its real ~0.73 pump efficiency
from the derived model alone.
"""
import math

# --- pump ------------------------------------------------------------------
ETA_PUMP_PEAK = 0.78            # a well-designed mid/large centrifugal rocket pump at
                                # its best Ns - middle of the real [SP-8107 Table II]
                                # "good pump" spread (RP-1 ~0.72, LOX ~0.75-0.80)
NS_PEAK_US = 2200.0            # whole-pump specific speed (rpm*gpm^0.5/ft^0.75) of
                                # peak efficiency - middle of the [SP-8107 2.1.1.6]
                                # 1300-2500 band
NS_BELL_WIDTH = 5.05           # log-width of the efficiency bell in Ns (fitted so a
                                # J-2-class 7-stage LH2 pump at whole-pump Ns ~500
                                # retains ~92% of peak, matching its real 73%)
NS_BELL_FLOOR = 0.55           # the bell never drops below this
Q_FULL_M3S = 0.35             # volumetric flow at/above which there is no size penalty
Q_TINY_M3S = 0.010           # flow at/below which the size penalty is at its worst
SIZE_PENALTY_MIN = 0.75       # worst-case small-pump efficiency retention
                                # (Reynolds / relative tip-clearance; RL10 H2 pump anchor)

# --- turbine -------------------------------------------------------------
ETA_TURBINE_CEILING = {         # peak efficiency achievable per staging type
    "single_impulse": 0.62,             # [SP-8107 Table III] fleet maxima per type
    "velocity_compounded_2row": 0.63,   # F-1 60.5%, J-2 fuel 60.1%
    "pressure_compounded_2stage": 0.76, # H-1 70.2%, LR87 63.6% (big vs mid)
    "reaction": 0.80,                    # SSME 73-79%
}
U_PITCH_REF_M_S = 180.0        # pitchline velocity at/above which pitchline_factor = 1.0
U_PITCH_EXPONENT = 0.5         # how hard a genuinely slow wheel hurts (A-7 at ~126 m/s)
U_PITCH_FLOOR = 0.55
# Low-power turbines lose efficiency (windage/leakage a bigger fraction, partial
# admission for the tiny impulse ones). Per-staging floor at/below POWER_MIN_W;
# ramps to 1.0 at/above POWER_FULL_W. Full-admission reaction turbines (RL10) are
# barely affected; a tiny partial-admission impulse turbine (Agena) is hit hard.
ADMISSION_FLOOR = {
    "reaction": 0.92,
    "pressure_compounded_2stage": 0.80,
    "velocity_compounded_2row": 0.72,
    "single_impulse": 0.65,
}
POWER_MIN_W = 3.0e5
POWER_FULL_W = 5.0e6
PR_LOW = 2.0                   # below this PR: a small efficiency bonus for a non-reaction
PR_LOW_BONUS = 1.06           #   turbine (clean low-PR 2-stage - RL10-adjacent)
PR_HIGH = 25.0                # above this PR: leaving-velocity loss penalty
PR_HIGH_PENALTY = 0.85        #   (YLR81 at PR 38)

OVERALL_EFF_TYPICAL = (0.35, 0.60)   # [SP-8107 2.1.1.6] GG-era 35-48%, SSME ~60%


def _ns_bell(ns_us):
    if ns_us <= 0:
        return NS_BELL_FLOOR
    z = math.log(ns_us / NS_PEAK_US) / NS_BELL_WIDTH
    return max(NS_BELL_FLOOR, math.exp(-(z * z)))


def _size_penalty(q_m3s):
    if q_m3s >= Q_FULL_M3S:
        return 1.0
    if q_m3s <= Q_TINY_M3S:
        return SIZE_PENALTY_MIN
    frac = (math.log(q_m3s) - math.log(Q_TINY_M3S)) / (math.log(Q_FULL_M3S) - math.log(Q_TINY_M3S))
    return SIZE_PENALTY_MIN + (1.0 - SIZE_PENALTY_MIN) * frac


def pump_efficiency(ns_pump_us, q_m3s, build_quality=1.0):
    """
    Derived hydraulic efficiency of one propellant pump.

    `ns_pump_us` is the WHOLE-pump US specific speed (N * Q^0.5 / H_total^0.75);
    for the tool's multistage pumps this is `NS_TARGET_US / n_stages**0.75`,
    which is why a 7-stage LH2 pump lands well below the efficiency peak. Clamped
    to a sane [0.35, 0.88] band.
    """
    eta = ETA_PUMP_PEAK * _ns_bell(ns_pump_us) * _size_penalty(q_m3s) * build_quality
    return max(0.35, min(0.88, eta))


def _pitchline_factor(u_pitchline_m_s):
    if u_pitchline_m_s >= U_PITCH_REF_M_S:
        return 1.0
    return max(U_PITCH_FLOOR, (u_pitchline_m_s / U_PITCH_REF_M_S) ** U_PITCH_EXPONENT)


def _admission_factor(staging, shaft_power_w):
    floor = ADMISSION_FLOOR.get(staging, ADMISSION_FLOOR["velocity_compounded_2row"])
    if shaft_power_w >= POWER_FULL_W:
        return 1.0
    if shaft_power_w <= POWER_MIN_W:
        return floor
    frac = ((math.log(shaft_power_w) - math.log(POWER_MIN_W))
            / (math.log(POWER_FULL_W) - math.log(POWER_MIN_W)))
    return floor + (1.0 - floor) * frac


def _pr_factor(staging, pressure_ratio):
    # A reaction turbine's low-PR advantage is already baked into its ceiling,
    # so don't double-count it there.
    if staging == "reaction" or pressure_ratio <= 0:
        return 1.0
    if pressure_ratio < PR_LOW:
        return PR_LOW_BONUS
    if pressure_ratio > PR_HIGH:
        return PR_HIGH_PENALTY
    return 1.0


def turbine_efficiency(staging, u_pitchline_m_s, shaft_power_w, pressure_ratio,
                       build_quality=1.0):
    """Derived total-to-static efficiency of the turbine, from its staging type
    (efficiency ceiling), pitchline speed, whether it runs partial admission,
    and pressure ratio. Clamped to [0.30, 0.85]."""
    ceiling = ETA_TURBINE_CEILING.get(staging, ETA_TURBINE_CEILING["velocity_compounded_2row"])
    eta = (ceiling * _pitchline_factor(u_pitchline_m_s)
           * _admission_factor(staging, shaft_power_w) * _pr_factor(staging, pressure_ratio)
           * build_quality)
    return max(0.30, min(0.85, eta))


def overall_efficiency(eta_pump, eta_turbine):
    return eta_pump * eta_turbine


# Real anchors for the __main__ fit report and validate.py's spot check.
# (name, kind, staging, ns_pump_us, q_m3s, u_pitch_m_s, power_w, PR, real_eta)
_PUMP_ANCHORS = [
    # name,            ns_pump_us, q_m3s, real_eta   [SP-8107 Table II]
    ("F-1 RP-1 pump",      2200.0,  0.96, 0.726),
    ("F-1 LOX pump",       2200.0,  1.57, 0.746),
    ("J-2 LOX pump",       2200.0,  0.18, 0.800),
    ("J-2 LH2 pump (7st)",  511.0,  0.54, 0.730),
    ("H-1 RP-1 pump",      2200.0,  0.55, 0.718),
    ("H-1 LOX pump",       2200.0,  0.90, 0.778),
    ("RL10 H2 pump (2st)", 1309.0,  0.05, 0.550),
    ("SSME LOX pump",      2200.0,  0.45, 0.781),
    ("SSME H2 pump (3st)",  965.0,  0.60, 0.741),
]
_TURBINE_ANCHORS = [
    # name,        staging,                       u_pitch, power_w,  PR,   real_eta  [SP-8107 Table III]
    ("F-1 turbine",  "velocity_compounded_2row",   256.0,  3.9e7, 16.4, 0.605),
    ("J-2 fuel trb", "velocity_compounded_2row",   451.0,  6.0e6,  7.3, 0.601),
    ("J-2 ox trb",   "velocity_compounded_2row",   180.0,  2.0e6,  2.5, 0.484),
    ("H-1 turbine",  "pressure_compounded_2stage", 393.0,  1.5e7, 17.7, 0.702),
    ("RL10 turbine", "pressure_compounded_2stage", 238.0,  5.0e5,  1.4, 0.740),
    ("SSME fuel trb", "reaction",                  506.0,  4.0e7,  1.6, 0.790),
    ("A-7 turbine",  "velocity_compounded_2row",   126.0,  3.0e5, 21.2, 0.372),
    ("YLR81 turbine", "single_impulse",            261.0,  2.8e5, 37.7, 0.410),
]

PUMP_TOLERANCE = 0.08
TURBINE_TOLERANCE = 0.08
# Genuine outliers - reported, not gated. RL10's 1962 tiny geared H2 pump (55%)
# is the lowest pump anywhere; J-2's ox turbine (48%) is a tiny downstream series
# stage on already-expanded gas, not a design the tool ever produces (the tool's
# ox turbine takes a DERIVED power-proportional share of the series gas's specific
# work - turbopump_sizing.split_turbine_work - but its efficiency still comes from
# the same single-turbine correlation, which doesn't capture a downstream stage's
# leaving-loss/partial-admission penalty). The AUTHORITATIVE check
# is validate.py::run_turbopump_efficiency_check() through the full pipeline.
PUMP_OUTLIERS = {"RL10 H2 pump (2st)"}
TURBINE_OUTLIERS = {"J-2 ox trb"}


if __name__ == "__main__":
    ok = True
    print(f"{'PUMP anchor':<22} {'Ns':>7} {'Q m3/s':>7} {'pred':>6} {'real':>6} {'d':>6}")
    for name, ns, q, real in _PUMP_ANCHORS:
        pred = pump_efficiency(ns, q)
        d = pred - real
        if name in PUMP_OUTLIERS:
            print(f"{name:<22} {ns:>7.0f} {q:>7.3f} {pred:>6.3f} {real:>6.3f} {d:>+6.3f} "
                  f"(outlier, not gated)")
            continue
        good = abs(d) <= PUMP_TOLERANCE
        ok &= good
        print(f"{name:<22} {ns:>7.0f} {q:>7.3f} {pred:>6.3f} {real:>6.3f} {d:>+6.3f} "
              f"{'ok' if good else 'FAIL'}")
    print()
    print(f"{'TURBINE anchor':<22} {'Upit':>6} {'PR':>6} {'pred':>6} {'real':>6} {'d':>6}")
    for name, staging, u, p, pr, real in _TURBINE_ANCHORS:
        pred = turbine_efficiency(staging, u, p, pr)
        d = pred - real
        if name in TURBINE_OUTLIERS:
            print(f"{name:<22} {u:>6.0f} {pr:>6.1f} {pred:>6.3f} {real:>6.3f} {d:>+6.3f} "
                  f"(outlier, not gated)")
            continue
        good = abs(d) <= TURBINE_TOLERANCE
        ok &= good
        print(f"{name:<22} {u:>6.0f} {pr:>6.1f} {pred:>6.3f} {real:>6.3f} {d:>+6.3f} "
              f"{'ok' if good else 'FAIL'}")
    print()
    print("turbopump_efficiency.py fit OK" if ok else "*** turbopump_efficiency.py FIT OUT OF TOLERANCE ***")
    raise SystemExit(0 if ok else 1)
