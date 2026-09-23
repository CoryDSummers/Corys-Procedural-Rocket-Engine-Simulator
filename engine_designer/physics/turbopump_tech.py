"""
Turbopump technology tier catalog. Same epistemic status as injectors.py's
per-type multipliers: real RO configs never expose distinct pump-efficiency
fields (confirmed by exhaustive grep of the 316-file Engine_Configs
reference set - turbopump performance is always implicit in the resulting
Isp/thrust numbers, never a separate RF field), so there's no clean
single-variable real analog to calibrate against the way propellant pairs
were. This is an engineering-judgment catalog - Tier 2, like injector-type
multipliers.

The "mature" tier's numbers (0.72/0.75) are the SAME flat values this tool
used before this catalog existed, kept as the default so
physics/validate.py's 5 real-engine spot checks (which construct
EngineDesign(...) without specifying a turbopump tier) are bit-for-bit
unaffected - same "neutral reference point" pattern already used for
contraction_ratio's default (1.6) and materials.CONTRACTION_RATIO_REFERENCE.

specific_power_w_kg (turbopump shaft power per kg of turbopump ASSEMBLY mass)
is used to turn the already-computed turbopump power into an actual mass
estimate (physics/turbopump.py::turbopump_power). Two of three tiers are
real, cited data points:
  - mature: Saturn V F-1 turbopump - 1,134 kg (2,500 lb) assembly mass,
    ~55,000 hp (~41 MW) shaft power => ~36,000 W/kg. High confidence
    (NASA NTRS 20140011656 "Waking a Giant"; Smithsonian NASM F-1 turbopump
    object records).
  - early_simple: V-2 (A-4) - 355.2 kg (783 lb) for the COMBINED turbopump +
    steam generator + frame assembly (Smithsonian NASM object record), at
    ~600 hp (~447 kW) per enginehistory.org's Rocket Propulsion Evolution
    monograph => ~1,300 W/kg. Medium confidence and an explicit UPPER BOUND
    on mass (the figure bundles non-pump hardware), so real bare-turbopump
    specific power was likely somewhat higher (mass somewhat lower) than
    this implies.
  - advanced: NOT independently sourced. No reliable primary-sourced modern
    turbopump mass could be found (RS-25 secondary sources disagree "100 hp/
    lb" vs "70 hp/lb" with no primary citation; a "68 kg" Merlin figure found
    online appears to belong to the older Merlin 1A, not 1D). Set as a
    flagged, round extrapolation (~2x the confirmed F-1 figure) reflecting
    known qualitative trends (higher shaft speeds, better materials) - Tier 3,
    treat with real skepticism, not the same confidence as the other two.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class TurbopumpTech:
    key: str
    display_name: str
    build_quality_factor: float  # multiplies the DERIVED pump & turbine efficiency
                                  # (physics/turbopump_efficiency.py). "mature" = 1.00,
                                  # so an F-1-class design recovers its real ~0.73 pump
                                  # efficiency from the derived model with no tier boost.
    eta_pump_fuel: float          # LEGACY / display + optional-manual-override hint only -
    eta_pump_ox: float            #   efficiency is derived now, not taken from these.
    specific_power_w_kg: float    # FALLBACK ONLY - turbopump mass is geometry-derived
                                   #   (physics/turbopump_sizing.py); this is used only
                                   #   when the geometry model is degenerate.
    relative_cost_factor: float
    tech_era_hint: str
    notes: str


TURBOPUMP_TECHS = {
    "early_simple": TurbopumpTech(
        key="early_simple",
        display_name="Early/Simple Centrifugal Pump",
        build_quality_factor=0.93,
        eta_pump_fuel=0.62,
        eta_pump_ox=0.65,
        specific_power_w_kg=1300.0,
        relative_cost_factor=0.7,
        tech_era_hint="Early (1940s-50s, V-2/early ICBM-class turbopumps)",
        notes="Single-stage centrifugal pumps with limited blade/impeller "
              "refinement - real early turbopumps ran meaningfully less "
              "efficiently than the mature designs that followed. Specific "
              "power (~1.3 kW/kg) is a V-2-derived upper bound - the source "
              "mass figure bundles the steam generator and frame with the "
              "turbopump itself, so the real bare-pump number was likely "
              "somewhat higher (lighter).",
    ),
    "mature": TurbopumpTech(
        key="mature",
        display_name="Mature Turbopump (baseline)",
        build_quality_factor=1.00,
        eta_pump_fuel=0.72,
        eta_pump_ox=0.75,
        specific_power_w_kg=36000.0,
        relative_cost_factor=1.0,
        tech_era_hint="Mature (1960s+, most flown liquid engines)",
        notes="This tool's original flat default, before this catalog "
              "existed - kept as the reference tier so physics/validate.py's "
              "5 real-engine spot checks (calibrated assuming these exact "
              "numbers) are bit-for-bit unaffected by this feature. Specific "
              "power (~36 kW/kg) is directly from the Saturn V F-1 turbopump "
              "(1,134 kg, ~41 MW) - the best-documented data point of the "
              "three tiers.",
    ),
    "advanced": TurbopumpTech(
        key="advanced",
        display_name="Advanced High-Efficiency Turbopump",
        build_quality_factor=1.04,
        eta_pump_fuel=0.80,
        eta_pump_ox=0.83,
        specific_power_w_kg=70000.0,
        relative_cost_factor=1.6,
        tech_era_hint="Modern (1990s+, refined multi-stage/boost-pump designs)",
        notes="Represents a more refined, higher-stage-count or "
              "boost-pump-assisted design (RS-68/RD-180-class refinement) - "
              "real efficiency gains here are incremental and hard-won, not "
              "free, hence the higher relative cost factor. Specific power "
              "(~70 kW/kg) is a ROUND EXTRAPOLATION, NOT independently "
              "sourced - no reliable primary-sourced modern turbopump mass "
              "figure could be found; treat this number with real "
              "skepticism (see module docstring).",
    ),
}


def available_turbopump_techs():
    return list(TURBOPUMP_TECHS.keys())
