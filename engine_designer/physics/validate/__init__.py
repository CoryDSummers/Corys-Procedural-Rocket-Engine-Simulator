"""
Reusable physics self-checks + one real-engine spot-check per propellant
pair. Run via:  python3 -m engine_designer.physics.validate
(from /home/cory/ksp_config)

This plays the same role sim/h4_report.py's RD-111 spot-check played for
the H-4 one-off: don't trust the physics for a new design until it can
reproduce a known real engine's Isp within a few percent.

Real engines use contoured bell nozzles, not the simple cones this tool's
schematic draws, so the spot-check uses nozzle_divergence_efficiency's
lambda = 1.0 (no divergence loss) - the remaining efficiency gap
(combustion + real-nozzle + engine-size/maturity effects) is absorbed by
combustion.DEFAULT_ETA_CSTAR, which is WHY these spot checks exist: they are
what sets those three constants, not just what verifies them.

Sea-level Isp is only a meaningful, gated comparison for a nozzle that's
actually attached at sea level (RD-111, eps 18 at Pc 7.85 MPa). RL10A-3-3
(eps 61) and Aestus (eps 84) are vacuum/upper-stage nozzles that never fire
at sea level - RO's own file comments flag their "SL Isp" as an RPA-nominal
figure, and the ideal fully-expanded formula used here goes unphysical
(even negative) that deep into over-expansion. Those two are reported as
informational only, not gated on tolerance.
"""

# Package layout (split 2026-09-23 from the former single-file validate.py, check code
# moved verbatim). Every name the old module defined is re-exported here.
# Submodules:
#   _common              shared tolerances
#   performance          Propellant-pair Isp spot checks, full-pipeline integration checks and 
#   cooling_flux         Cooling: wall heat flux / Bartz magnitude vs F-1 / SSME / RL10 (COOLIN
#   cooling_methods      Cooling: explicit per-section cooling methods (incl. dump) and the mat
#   cooling_layouts      Cooling: jacket flow layouts - F-1 manifold bypass and the J-2 two-pas
#   cooling_wall_film    Cooling: coupled throat wall temperature and the two-site film overlay
#   turbomachinery       Turbopump efficiency / sizing / bearing DN, GG bleed, per-cycle models
#   injectors_stability  Injector element geometry (incl. gas-centered swirl) and combustion ac
#   structures           Mass-model sensitivity, jacket overpressure (plausibility + Huzel samp

from ._common import (  # noqa: F401
    TOLERANCE_PCT,
    INTEGRATION_TOLERANCE_PCT,
    PA_SEA_LEVEL,
)
from .performance import (  # noqa: F401
    SPOT_CHECKS,
    _predict,
    run,
    run_integration_checks,
    run_chamber_detail_check,
)
from .injectors_stability import (  # noqa: F401
    INJECTOR_GEOMETRY_CHECKS,
    run_injector_geometry_check,
    run_gas_centered_swirl_injector_check,
    run_combustion_stability_check,
)
from .structures import (  # noqa: F401
    run_mass_model_sensitivity_check,
    run_jacket_overpressure_check,
    run_jacket_overpressure_sample_calc_check,
    run_hatband_plausibility_check,
)
from .turbomachinery import (  # noqa: F401
    TURBOPUMP_EFFICIENCY_CHECKS,
    ETA_TOLERANCE,
    run_turbopump_efficiency_check,
    GG_BLEED_CHECKS,
    run_gg_flow_fraction_check,
    TURBOPUMP_SIZING_CHECKS,
    run_turbopump_sizing_check,
    run_bearing_dn_check,
    run_cycle_model_check,
    run_feed_system_plausibility_check,
    run_pump_pressure_chain_check,
)
from .cooling_flux import (  # noqa: F401
    run_contraction_ratio_sensitivity_check,
    T_WG_LO_K,
    COOLING_CHECKS,
    CHANNELS_REF_DP_TARGET_PA,
    CHANNELS_REF_DP_TOL,
    run_cooling_heat_flux_check,
)
from .cooling_methods import (  # noqa: F401
    run_explicit_cooling_check,
    run_cooling_compatibility_check,
    run_cooling_robustness_sweep,
)
from .cooling_layouts import (  # noqa: F401
    run_manifold_bypass_check,
    run_two_pass_cooling_check,
)
from .cooling_wall_film import (  # noqa: F401
    FLAT_JACKET_DP_PA,
    WIESENECK_SSME_T_WC_K,
    WIESENECK_COPPER_T_WG_MAX_K,
    run_coupled_wall_temperature_check,
    run_film_overlay_check,
)

# Every check, in the order `python3 -m engine_designer.physics.validate` runs them.
ALL_CHECKS = (
    run,
    run_integration_checks,
    run_contraction_ratio_sensitivity_check,
    run_turbopump_efficiency_check,
    run_gg_flow_fraction_check,
    run_cooling_heat_flux_check,
    run_injector_geometry_check,
    run_gas_centered_swirl_injector_check,
    run_combustion_stability_check,
    run_chamber_detail_check,
    run_turbopump_sizing_check,
    run_bearing_dn_check,
    run_mass_model_sensitivity_check,
    run_cycle_model_check,
    run_explicit_cooling_check,
    run_jacket_overpressure_check,
    run_jacket_overpressure_sample_calc_check,
    run_manifold_bypass_check,
    run_two_pass_cooling_check,
    run_feed_system_plausibility_check,
    run_hatband_plausibility_check,
    run_coupled_wall_temperature_check,
    run_cooling_compatibility_check,
    run_cooling_robustness_sweep,
    run_film_overlay_check,
    run_pump_pressure_chain_check,
)
