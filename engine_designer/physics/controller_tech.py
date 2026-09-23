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

Purely an EXPORT-time catalog: none of these fields feed
EngineDesign.compute()'s physics, so choosing a tier never changes Isp/
thrust/warnings - only the exported .cfg's TESTFLIGHT block and 3 new
fields (throttleResponseRate, varyIsp/varyMixture, residualsThresholdBase).
Zero regression risk to physics/validate.py.

The four `*_reliability_*` values and `tested_to_rated_multiplier` are now the
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

tested_to_rated_multiplier: how many multiples of the computed rated burn
time a design's testedBurnTime gets (testedBurnTime = ratedBurnTime *
this), replacing what used to be a flat rated*20 constant in
export/cfg_writer.py regardless of anything. Grounded in 4 real,
well-documented engines researched this session: Saturn V F-1 ~13.6x
(2250s tested / 165s rated), RD-180 ~6.2x (1590s/255s), SpaceX Merlin 1D
~10.6x (1970s cumulative qual test time / 185s rated flight burn), Ariane 5
Vulcain 2 ~16.5x (10,000s qualification / 605s nominal flight). The real
data does NOT show a clean correlation between control-system era and this
ratio (RD-180 is 1990s staged-combustion tech at the LOW end; Vulcain 2's
16.5x is the high end) - it's driven more by each program's own test/QA
philosophy than by controller electronics sophistication. The 4 tiers below
are a reasoned progression SPANNING the real observed 6-17x range as a
design-choice spectrum, not a claim that any one tier literally reproduces
a specific historical engine's program. Ablative-cooled designs override
this entirely (tested = rated, matching the real "ablative, no extra time"
pattern - see physics/design.py) regardless of controller tier.
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
    tested_to_rated_multiplier: float
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
        tested_to_rated_multiplier=6.0,
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
        tested_to_rated_multiplier=10.0,
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
        tested_to_rated_multiplier=14.0,
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
        tested_to_rated_multiplier=17.0,
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
