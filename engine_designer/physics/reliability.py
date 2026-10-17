"""
Design-derived TestFlight reliability + tested/rated burn time.

EXPORT-TIME ONLY - nothing here is called from EngineDesign.compute(), so no
validate.py spot check moves. (The RATED burn time itself is a compute()
output since 2026-10-16 - physics/burn_time.py.)

Reliability: start from the chosen controller tier's four reliability values
(the build-quality anchor), take the failure gap `1 - value`, scale it by the
cycle family (BASE_BY_CYCLE), then inflate it for the design's own risk
drivers - high chamber pressure, deep throttling, many restarts, a
tip-speed-marginal or fatigue-marginal design, a multi-chamber layout. Clamp
into the real RO band (cycleReliabilityStart over ~600 RO configs: 0.63 min /
0.97 median / 0.9997 max).

BASE_BY_CYCLE is FITTED where RealismOverhaul has the data (2026-10-16,
catalog/testflight_corpus.json, refit_cycle_gaps()): each family's failure gap
over the same-decade median of the other pump-fed (mostly gas-generator)
configs, geometric mean over the four reliability values -
  pressure-fed 0.66, expander 0.70 (RL10 / LE-5B / RD-0146 / Vinci),
  staged (ORSC and FRSC alike) 1.43 - which is the Pc term below at the staged
  fleet's median ~16 MPa (x1.27) times 1.13.
So RO does NOT rate ox-rich staged combustion worse than fuel-rich (the old
OX_RICH_EXTRA 0.35 and the 1.6 / 2.2 / 2.6 staged multipliers double-counted
the chamber-pressure term and are retired). FFSC (no RO data) takes the staged
value; tap-off and electric pump stay Tier 3 guesses.
The risk inflators are Tier 3 (reasonable-but-arbitrary): trust the direction.
"""

# Cycle family: multiplies the (1 - reliability) failure gap. 1.0 = the
# gas-generator / other-pump-fed reference group.
BASE_BY_CYCLE = {
    "pressure_fed": 0.66,       # fitted, 61 RO rows
    "gas_generator": 1.00,      # reference
    "tap_off": 1.15,            # Tier 3 - no RO tap-off rows (J-2S only flew on a stand)
    "expander": 0.70,           # fitted, 27 RO rows
    "electric_pump": 1.05,      # Tier 3 - Rutherford rows only, too few to fit
    "frsc": 1.13,               # fitted staged family / Pc term (see docstring)
    "orsc": 1.13,
    "ffsc": 1.13,               # no RO data - the staged value
}
_BASE_FALLBACK = 1.0
# Real chamber pressures of the RO staged-combustion configs the staged factor
# was fitted on (their Engine_Configs header comments, MPa); the median sets the
# Pc term BASE_BY_CYCLE["orsc"/"frsc"] is divided by.
STAGED_FAMILY_PC_MPA = {"RD180": 26.66, "RD170": 24.52, "RD191": 25.83, "RD120": 16.28,
                        "RD253": 14.7, "NK33": 14.5, "RD8": 0.7, "RD58": 5.30,
                        "RD0124": 15.69, "SSME": 20.48, "RD0120": 21.87, "LE7": 12.7}

PC_REF_PA = 7.0e6
PC_GAP_PER_MPA = 0.030          # each MPa of Pc above the reference inflates the gap by this
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

def _risk_multiplier(design, result):
    """(1 + sum of applicable risk inflators) on the cycle-scaled failure gap."""
    m = 1.0
    pc_mpa = design.chamber_pressure_pa / 1e6
    if pc_mpa > PC_REF_PA / 1e6:
        m += PC_GAP_PER_MPA * (pc_mpa - PC_REF_PA / 1e6)

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


def derived_burn_times(design, result, controller_tier=None, rated_burn_time_s=None,
                       is_ablative=False):
    """
    (rated_burn_time_s, tested_burn_time_s). Rated is compute()'s duty-capped
    value (physics/burn_time.py) unless overridden. Tested = rated x the
    RO-corpus tested/rated ratio for this era / pressure-fed / restartable /
    upper-stage engine (burn_time.tested_ratio), never past the hardware's
    life limit (result["burn_life_s"]) and never below rated; ablative =
    rated (the real "ablative, no extra time" pattern). controller_tier is
    accepted for call compatibility - the era comes from burn_time.design_year.
    """
    from . import burn_time
    if rated_burn_time_s is None:
        rated_burn_time_s = result["rated_burn_time_s"]
    year = result.get("design_year") or burn_time.design_year(design)[0]
    role = result.get("engine_role") or burn_time.engine_role(
        result.get("isp_vac_engine_s"), result.get("isp_sl_engine_s"),
        design.cycle == "pressure_fed")
    ratio = burn_time.tested_ratio(year, role == "pressure_fed",
                                   burn_time.is_restartable(getattr(design, "ignitions", 1)),
                                   role != "booster")
    tested = burn_time.tested_burn_time_s(rated_burn_time_s, result.get("burn_life_s"), ratio,
                                          ablative=is_ablative)
    return rated_burn_time_s, tested


def refit_cycle_gaps(rows=None):
    """{family: gap ratio} - each RO cycle family's failure gap over the same-
    decade median of the other pump-fed configs, geometric mean over the four
    reliability values. Families: catalog/build_testflight_corpus.FAMILY_FILES +
    "pf"."""
    import math
    import statistics
    if rows is None:
        from ..catalog import build_testflight_corpus
        rows = build_testflight_corpus.load_rows()
    keys = ("cyc_start", "cyc_end", "ign_start", "ign_end")
    rows = [r for r in rows if r["biprop"] and r["year"] and all(r[k] for k in keys)]
    dec = lambda y: min(y // 10 * 10, 2000)
    ref = {}
    for r in rows:
        if r["family"] == "pump":
            ref.setdefault(dec(r["year"]), []).append(r)
    out = {}
    for fam in sorted({r["family"] for r in rows} - {"pump"}):
        logs = []
        for k in keys:
            med = {d: 1.0 - statistics.median(x[k] for x in v) for d, v in ref.items()}
            ratios = [(1.0 - r[k]) / med[dec(r["year"])] for r in rows
                      if r["family"] == fam and med.get(dec(r["year"]), 0) > 0]
            logs.append(statistics.median(math.log(max(x, 1e-4)) for x in ratios))
        out[fam] = math.exp(sum(logs) / len(logs))
    return out


if __name__ == "__main__":
    from .controller_tech import CONTROLLER_TECHS
    from .design import EngineDesign

    tier = CONTROLLER_TECHS["baseline"]

    def rel(pair, cycle, **kw):
        d = EngineDesign(propellant_pair=pair, cycle=cycle, **kw)
        return derived_reliability(d, d.compute(), tier)

    # The cycle factors reproduce the RO corpus fit.
    import statistics
    gaps = refit_cycle_gaps()
    print("  RO failure-gap ratio vs same-era pump-fed: "
          + ", ".join(f"{k} {v:.2f}" for k, v in gaps.items()))
    assert abs(gaps["pf"] - BASE_BY_CYCLE["pressure_fed"]) < 0.05, gaps
    assert abs(gaps["expander"] - BASE_BY_CYCLE["expander"]) < 0.05, gaps
    pc_term = 1.0 + PC_GAP_PER_MPA * (statistics.median(STAGED_FAMILY_PC_MPA.values())
                                     - PC_REF_PA / 1e6)
    for fam in ("orsc", "frsc"):
        assert abs(BASE_BY_CYCLE[fam] * pc_term / gaps[fam] - 1.0) < 0.15, (fam, gaps[fam], pc_term)

    # Ordering at a fixed tier and each cycle's typical Pc: pressure-fed > GG >
    # FRSC > ORSC > FFSC - now carried by the Pc term, not a per-cycle penalty.
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

    # Burn times: inside the RO corpus band, never past the life, ablative tested == rated.
    d = EngineDesign(cycle="gas_generator")
    r = d.compute()
    rated, tested = derived_burn_times(d, r, tier)
    assert 1.0 <= tested / rated <= 10.0 and tested <= max(rated, r["burn_life_s"]) + 1e-9, \
        (rated, tested, r["burn_life_s"])
    rated_a, tested_a = derived_burn_times(d, r, tier, is_ablative=True)
    assert rated_a == tested_a
    print(f"  burn time: rated {rated:.0f} s -> tested {tested:.0f} s ({tested/rated:.1f}x, "
          f"life {r['burn_life_s']:.0f} s); ablative tested == rated")

    print("reliability.py self-checks: OK")
