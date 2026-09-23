"""
Design-derived TestFlight reliability + tested/rated burn time.

EXPORT-TIME ONLY - nothing here is called from EngineDesign.compute(), so no
validate.py spot check moves. It replaces the four verbatim
`controller_tier.*_reliability_*` numbers that export/cfg_writer.py used to
write regardless of the design: a modern FFSC and a crude pressure-fed engine
should NOT get the same TESTFLIGHT curve.

Method: start from the chosen controller tier's four reliability values (they
stay the anchor / build-quality modifier), take the failure gap `1 - value`,
scale it by the cycle's inherent difficulty (BASE_BY_CYCLE), then inflate it
for the design's own risk drivers - high chamber pressure, oxidiser-rich
turbomachinery, deep throttling, many restarts, a tip-speed-marginal or
fatigue-marginal design, a multi-chamber layout. Clamp into a real band
(cycleReliabilityStart across ~300 RO configs runs 0.63 min / 0.97 median /
0.9997 max).

All coefficients are Tier 3 (reasonable-but-arbitrary), the same status the
controller-tier numbers themselves already carry. The point is the DIRECTION:
FFSC/ORSC < FRSC < GG < pressure-fed at a fixed tier; higher Pc lower; deep
throttle lower.
"""

# Cycle inherent difficulty: multiplies the (1 - reliability) failure gap.
# 1.0 = as reliable as the tier says; > 1 = harder to make reliable.
BASE_BY_CYCLE = {
    "pressure_fed": 0.85,
    "gas_generator": 1.00,
    "tap_off": 1.15,
    "expander": 0.95,
    "electric_pump": 1.05,
    "frsc": 1.6,
    "orsc": 2.2,
    "ffsc": 2.6,
}
_BASE_FALLBACK = 1.0

PC_REF_PA = 7.0e6
PC_GAP_PER_MPA = 0.030          # each MPa of Pc above the reference inflates the gap by this
OX_RICH_EXTRA = 0.35            # ORSC / FFSC: hot oxidiser-rich gas is corrosive/erosive
DEEP_THROTTLE_THRESHOLD = 0.5
DEEP_THROTTLE_EXTRA = 0.25      # throttling below 50 % of max
MANY_RESTART_THRESHOLD = 10
MANY_RESTART_EXTRA = 0.20
TIP_SPEED_MARGIN_WARN = 1.20    # pump tip-speed margin (limit / actual) below this
TIP_SPEED_EXTRA = 0.40
FATIGUE_MARGIN = 4.0            # throat fatigue cycles below ignitions * this
FATIGUE_EXTRA = 0.30
CHAMBER_COUNT_EXTRA = 0.15      # per extra chamber beyond the first

# Real-corpus clamp on the exported reliability values.
RELIABILITY_FLOOR = 0.55
RELIABILITY_CEILING = 0.99975

# tested / rated burn-time multiplier bounds.
TESTED_RATED_MIN = 3.0
TESTED_RATED_MAX = 30.0
TESTED_BURN_TIME_CAP_S = 180000.0


def _risk_multiplier(design, result):
    """(1 + sum of applicable risk inflators) on the cycle-scaled failure gap."""
    m = 1.0
    pc_mpa = design.chamber_pressure_pa / 1e6
    if pc_mpa > PC_REF_PA / 1e6:
        m += PC_GAP_PER_MPA * (pc_mpa - PC_REF_PA / 1e6)

    cyc = (result.get("cycle_result") or {})
    if cyc.get("oxidizer_rich") or design.cycle == "ffsc":
        m += OX_RICH_EXTRA

    if design.throttle_floor < DEEP_THROTTLE_THRESHOLD:
        m += DEEP_THROTTLE_EXTRA

    if getattr(design, "ignitions", 1) > MANY_RESTART_THRESHOLD:
        m += MANY_RESTART_EXTRA

    sizing = result.get("turbopump_sizing")
    if sizing:
        margins = [sizing["fuel_pump"]["tip_speed_margin"], sizing["ox_pump"]["tip_speed_margin"]]
        if min(margins) < TIP_SPEED_MARGIN_WARN:
            m += TIP_SPEED_EXTRA

    cool = result.get("cooling") or {}
    fat = cool.get("throat_fatigue_cycles")
    if fat is not None and fat < max(1, getattr(design, "ignitions", 1)) * FATIGUE_MARGIN:
        m += FATIGUE_EXTRA

    chambers = getattr(design, "chamber_count", 1)
    if chambers > 1:
        m += CHAMBER_COUNT_EXTRA * (chambers - 1)

    return m


def _derive_one(tier_value, base_by_cycle, risk_mult):
    gap = (1.0 - tier_value) * base_by_cycle * risk_mult
    return max(RELIABILITY_FLOOR, min(RELIABILITY_CEILING, 1.0 - gap))


def derived_reliability(design, result, controller_tier):
    """
    Return dict(ignition_reliability_start/end, cycle_reliability_start/end)
    derived from the design, with `controller_tier` as the anchor.
    """
    base = BASE_BY_CYCLE.get(design.cycle, _BASE_FALLBACK)
    risk = _risk_multiplier(design, result)
    return {
        "ignition_reliability_start": _derive_one(controller_tier.ignition_reliability_start, base, risk),
        "ignition_reliability_end": _derive_one(controller_tier.ignition_reliability_end, base, risk),
        "cycle_reliability_start": _derive_one(controller_tier.cycle_reliability_start, base, risk),
        "cycle_reliability_end": _derive_one(controller_tier.cycle_reliability_end, base, risk),
        "risk_multiplier": risk,
        "cycle_base": base,
    }


def derived_burn_times(design, result, controller_tier, rated_burn_time_s=None,
                       is_ablative=False):
    """
    Return (rated_burn_time_s, tested_burn_time_s). Rated is the
    chamber-material-driven value from compute() (passed in). Tested = rated x a
    multiplier that starts from the controller tier's tested_to_rated_multiplier
    and is nudged up for a reusable design signal (deep throttle range + many
    restarts) and down for a hard-to-reuse one; ablative chambers get
    tested == rated (matching real "ablative, no extra time" configs).
    """
    if rated_burn_time_s is None:
        rated_burn_time_s = result["rated_burn_time_s"]
    if is_ablative:
        return rated_burn_time_s, rated_burn_time_s

    mult = controller_tier.tested_to_rated_multiplier
    # Reusable-design signal: throttles deep AND restarts often -> more qual time.
    if (design.throttle_floor <= 0.6
            and getattr(design, "ignitions", 1) >= 5):
        mult *= 1.25
    if design.cycle in ("frsc", "orsc", "ffsc"):
        mult *= 1.10                                  # staged/FFSC engines are qual-heavy
    if getattr(design, "ignitions", 1) <= 1 and design.throttle_floor >= 0.95:
        mult *= 0.8                                   # expendable, fixed-thrust -> less qual

    mult = max(TESTED_RATED_MIN, min(TESTED_RATED_MAX, mult))
    tested = min(TESTED_BURN_TIME_CAP_S, rated_burn_time_s * mult)
    return rated_burn_time_s, tested


if __name__ == "__main__":
    from .controller_tech import CONTROLLER_TECHS
    from .design import EngineDesign

    tier = CONTROLLER_TECHS["baseline"]

    def rel(pair, cycle, **kw):
        d = EngineDesign(propellant_pair=pair, cycle=cycle, **kw)
        return derived_reliability(d, d.compute(), tier)

    # Cycle-complexity ordering at a fixed tier: pressure-fed > GG > FRSC > ORSC > FFSC.
    pf = rel("N2O4/MMH", "pressure_fed", chamber_pressure_pa=0.8e6, injector_type="impinging")
    gg = rel("LOX/RP-1", "gas_generator")
    fr = rel("LOX/LH2", "frsc", chamber_pressure_pa=20e6, mixture_ratio=6.0)
    orc = rel("LOX/RP-1", "orsc", chamber_pressure_pa=25e6, mixture_ratio=2.7)
    ff = rel("LOX/CH4", "ffsc", chamber_pressure_pa=30e6, mixture_ratio=3.55)
    order = [pf, gg, fr, orc, ff]
    starts = [x["cycle_reliability_start"] for x in order]
    assert all(starts[i] >= starts[i + 1] - 1e-9 for i in range(len(starts) - 1)), starts
    for name, x in zip(("pressure_fed", "gas_generator", "frsc", "orsc", "ffsc"), order):
        print(f"  {name:14} cycle_rel_start {x['cycle_reliability_start']:.4f}  "
              f"ign_start {x['ignition_reliability_start']:.4f}  (risk x{x['risk_multiplier']:.2f})")

    # Higher Pc -> lower reliability (same cycle).
    lo_pc = rel("LOX/RP-1", "gas_generator", chamber_pressure_pa=5e6)
    hi_pc = rel("LOX/RP-1", "gas_generator", chamber_pressure_pa=15e6)
    assert hi_pc["cycle_reliability_start"] < lo_pc["cycle_reliability_start"]

    # A low-complexity default design barely moves from the tier's own numbers.
    base_default = rel("LOX/RP-1", "gas_generator")
    assert abs(base_default["cycle_reliability_start"] - tier.cycle_reliability_start) < 0.02, \
        (base_default["cycle_reliability_start"], tier.cycle_reliability_start)

    # Burn times: ablative -> tested == rated; non-ablative -> in the 3-30x band.
    d = EngineDesign(cycle="gas_generator")
    r = d.compute()
    rated, tested = derived_burn_times(d, r, tier)
    assert 3.0 <= tested / rated <= 30.0, (rated, tested)
    rated_a, tested_a = derived_burn_times(d, r, tier, is_ablative=True)
    assert rated_a == tested_a
    print(f"  burn time: rated {rated:.0f} s -> tested {tested:.0f} s ({tested/rated:.1f}x); "
          f"ablative tested == rated")

    print("reliability.py self-checks: OK")
