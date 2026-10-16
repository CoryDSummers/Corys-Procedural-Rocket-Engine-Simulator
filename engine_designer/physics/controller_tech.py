"""
Engine-controller/avionics sophistication catalog. No real RO config models
a distinct "controller" module or part (confirmed by exhaustive grep across
the 316-file Engine_Configs reference set - zero hits for any controller/
avionics/ModuleCommand field anywhere). Real precedent - including this
project's OWN H3-250K_Config.cfg (throttleResponseRate=0.6, "FADEC
closed-loop") and H4-250K_Config.cfg (varyIsp=0.004/varyMixture=0.001/
residualsThresholdBase=0.005, "dual-channel fail-operational digital
controller") - represents control sophistication purely by tuning these
existing RF/TestFlight scalar fields. This catalog is Tier 3
(reasonable-but-arbitrary, same status H3/H4's own numbers already carry),
except where a tier directly cites H3/H4's own values (flagged in that
tier's notes).

Almost purely an EXPORT-time catalog: choosing a tier never changes Isp/
thrust/mass - only the exported .cfg's TESTFLIGHT block and 3 fields
(throttleResponseRate, varyIsp/varyMixture, residualsThresholdBase). The one
exception (2026-10-16): `era_year` dates a design that has no RP-1 tech node,
and the default rated-burn duty (physics/burn_time.py, inside compute()) has an
era term - so with no tech node and no explicit duty target, the tier moves
rated_burn_time_s (and, for an ablative or electric-pump design, the liner /
battery sized to it).

The four `*_reliability_*` values and `era_year` are now the
ANCHOR / build-quality inputs to physics/reliability.py, which derives the
actually-exported TESTFLIGHT numbers from the design (cycle complexity,
chamber pressure, oxidiser-rich turbomachinery, throttle depth, restart count,
tip-speed / fatigue margin). The `throttleResponseRate` / `vary*` / `residuals`
fields still go straight to the .cfg unchanged.

The "baseline" tier's reliability values (0.970/0.995/0.970/0.995) are chosen
so that a LOW-COMPLEXITY design (pressure-fed or GG, moderate Pc) still exports
almost exactly those numbers - matching every .cfg exported before this catalog
existed - while a modern FFSC/ORSC design at the same tier exports meaningfully
lower reliability.

era_year: the year a tier stands for when the design has no RP-1 tech node -
physics/burn_time.design_year uses it for the era terms of the RO-corpus duty and
tested/rated fits (catalog/testflight_corpus.json). It replaces the old
`tested_to_rated_multiplier` (6/10/14/17 x rated), whose anchors were cumulative
QUALIFICATION time (Merlin 1D 1970 s, Vulcain 2 10,000 s) - but RO's TestFlight
reads testedBurnTime as the longest SINGLE burn, and the real RO corpus has
tested/rated median 3.0 (10-90 %: 1.5-9.6), rising with era, not 6-17x. The
tiers' reliability values were checked against the same corpus' per-decade
medians (pump-fed cycleReliabilityStart/End: 1950s 0.87/0.979, 1960s 0.96/0.994,
1970s+ 0.98/0.997): electromechanical ~ 1950s, baseline ~ 1960s, FADEC ~ 1970s+;
dual_redundant sits above the corpus median (its 0.999 end is inside the corpus
range, max 0.9997).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ControllerTech:
    key: str
    display_name: str
    throttle_response_rate: float
    vary_isp: float
    vary_mixture: float
    residuals_threshold_base: float
    ignition_reliability_start: float
    ignition_reliability_end: float
    cycle_reliability_start: float
    cycle_reliability_end: float
    era_year: int
    relative_cost_factor: float
    tech_era_hint: str
    notes: str


CONTROLLER_TECHS = {
    "electromechanical": ControllerTech(
        key="electromechanical",
        display_name="Early Electromechanical Control",
        throttle_response_rate=0.25,
        vary_isp=0.02, vary_mixture=0.01, residuals_threshold_base=0.02,
        ignition_reliability_start=0.900, ignition_reliability_end=0.970,
        cycle_reliability_start=0.900, cycle_reliability_end=0.970,
        era_year=1958,
        relative_cost_factor=0.6,
        tech_era_hint="Early (1950s-60s, relay/analog electromechanical sequencers)",
        notes="Slow throttle response and loose build tolerances relative to "
              "later digital control - representative of pre-digital engine "
              "control systems. Not independently sourced (Tier 3, same "
              "status as this project's own H3/H4 controller numbers).",
    ),
    "baseline": ControllerTech(
        key="baseline",
        display_name="Baseline Analog/Early Digital (previous default)",
        throttle_response_rate=0.4,
        vary_isp=0.01, vary_mixture=0.005, residuals_threshold_base=0.01,
        ignition_reliability_start=0.970, ignition_reliability_end=0.995,
        cycle_reliability_start=0.970, cycle_reliability_end=0.995,
        era_year=1966,
        relative_cost_factor=1.0,
        tech_era_hint="Mature (1960s-70s)",
        notes="Reproduces this tool's ORIGINAL hardcoded TESTFLIGHT numbers "
              "exactly (0.970/0.995/0.970/0.995) - kept as the default tier "
              "so every .cfg exported before this catalog existed is "
              "unaffected. throttleResponseRate/vary*/residuals are new "
              "fields this tool never exported before; these particular "
              "values are a reasonable default, not derived.",
    ),
    "digital_fadec": ControllerTech(
        key="digital_fadec",
        display_name="Digital FADEC",
        throttle_response_rate=0.6,
        vary_isp=0.008, vary_mixture=0.004, residuals_threshold_base=0.008,
        ignition_reliability_start=0.980, ignition_reliability_end=0.997,
        cycle_reliability_start=0.980, cycle_reliability_end=0.997,
        era_year=1980,
        relative_cost_factor=1.4,
        tech_era_hint="Modern (1970s+)",
        notes="throttle_response_rate=0.6 is cited directly from this "
              "project's own H3-250K_Config.cfg ('FADEC closed-loop: ~1.7s "
              "to slew the full 20% band').",
    ),
    "dual_redundant": ControllerTech(
        key="dual_redundant",
        display_name="Dual-Redundant Fail-Operational Digital",
        throttle_response_rate=0.75,
        vary_isp=0.004, vary_mixture=0.001, residuals_threshold_base=0.005,
        ignition_reliability_start=0.990, ignition_reliability_end=0.999,
        cycle_reliability_start=0.990, cycle_reliability_end=0.999,
        era_year=1990,
        relative_cost_factor=2.0,
        tech_era_hint="Modern (1980s+)",
        notes="vary_isp=0.004/vary_mixture=0.001/residuals_threshold_base="
              "0.005 are cited directly from this project's own "
              "H4-250K_Config.cfg ('Dual-channel fail-operational digital "
              "controller with condition monitoring').",
    ),
}


def available_controller_techs():
    return list(CONTROLLER_TECHS.keys())
