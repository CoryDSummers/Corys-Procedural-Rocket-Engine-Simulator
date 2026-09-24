"""
Bartz-lite engine wall heat transfer: a heat-flux DISTRIBUTION along the
chamber/nozzle contour, the integrated wall heat load, and the
regenerative-jacket coolant temperature rise it implies.

Scoped exactly like physics/expander.py's heat model and materials.py's
cooling_effectiveness proxy: this is NOT a full Bartz / boundary-layer / CFD
solve (that needs combustion-gas transport properties - viscosity, Prandtl
number - which this tool does not carry). It resolves the SHAPE of the flux
profile (peak at the throat, ~(At/A)^0.9, per claude_lit/topics/06) and
anchors its MAGNITUDE to the same representative regen-chamber duty point
physics/expander.py already uses (5 MW/m^2 area-average at Pc 4 MPa). Because
the magnitude is normalised to that anchor over the same actively-cooled
area, wall_heat_total_w() equals what expander.heat_pickup_w() computes for
the same surface - the two models can't contradict each other.

Real THROAT heat flux is several times the area-average this is anchored to
(claude_lit/topics/06: "< 0.5 .. > 160 MW/m^2, the high end at the throat of
large bipropellant chambers"); the profile's peak/mean ratio comes out of the
contour geometry, not a second constant.
"""

# Package layout (split 2026-09-23 from the former single-file cooling.py, code moved
# verbatim). Every public AND private name the old module exposed is re-exported here,
# so `from engine_designer.physics import cooling; cooling.X` is unchanged for callers.
# Submodules:
#   gas_side       Gas-side heat transfer: Bartz h_g, recovery temperature, the authoritative abs
#   profile        Contour geometry helpers + the legacy area-averaged flux anchor/shape and the 
#   coolant_props  Coolant (fuel) properties and capacity: cp, transport, density, dT limits, fla
#   methods        Cooling method as an explicit per-section design choice + the material x metho
#   dump           Dump cooling: coolant bled through the nozzle extension and ejected overboard.
#   radiation      Radiation-equilibrium wall temperature.
#   regen_credit   Regenerative-cooling Isp credit.
#   film           Fuel-film overlay: chamber curtain + nozzle-extension slot effectiveness, film
#   channels       Coolant-side channel/tube model: geometry, wall constructions, velocities, Dit
#   wall           Through-wall balance: gas film -> wall -> coolant (throat and full-length).
#   march          1-D coolant marches: single-pass counterflow and the J-2 two-pass layout.

from .profile import (  # noqa: F401
    HEAT_FLUX_REFERENCE_W_M2,
    PC_REFERENCE_PA,
    HEAT_FLUX_PC_EXPONENT,
    BARTZ_AREA_RATIO_EXPONENT,
    INJECTOR_FLUX_FRACTION,
    WALL_HEAT_ENERGY_FRACTION_TYPICAL,
    _frustum_area,
    _local_area_ratio,
    _bartz_shape,
    reference_area_avg_flux_w_m2,
    _shape_profile,
    heat_flux_profile,
    wall_heat_total_w,
    area_weighted_mean,
)
from .gas_side import (  # noqa: F401
    STEFAN_BOLTZMANN_W_M2K4,
    BARTZ_COEFF,
    BARTZ_SIGMA,
    BARTZ_RC_OVER_DT,
    RECOVERY_FACTOR,
    bartz_hg,
    recovery_temperature,
    wall_gas_temperature,
    WALL_TEMP_FRACTION_DEFAULT,
    BARTZ_ABS_FLUX_CALIBRATION,
    _BARTZ_ABS_FLUX_CALIBRATION_FALLBACK,
    absolute_heat_flux_profile,
    _injector_face_taper,
    bartz_hg_profile,
)
from .coolant_props import (  # noqa: F401
    MAX_COOLANT_DELTA_T_K,
    FUEL_CP_J_KGK,
    coolant_temp_rise_k,
    coolant_limit_k,
    regen_feasible,
    COOLANT_TRANSPORT,
    COOLANT_DENSITY_KG_M3,
    _COOLANT_TRANSPORT_FALLBACK,
    _COOLANT_DENSITY_FALLBACK,
)
from .methods import (  # noqa: F401
    COOLING_METHODS,
    resolve_cooling_method,
    resolve_cooling_method_checked,
)
from .dump import (  # noqa: F401
    DUMP_THRUST_RECOVERY_FRACTION,
    DUMP_COOLANT_FRACTION_MIN,
    DUMP_COOLANT_FRACTION_MAX,
    size_dump_coolant_fraction,
    dump_cooling_isp_penalty_fraction,
)
from .radiation import (  # noqa: F401
    radiative_wall_temperature,
)
from .regen_credit import (  # noqa: F401
    REGEN_ISP_BONUS_MAX,
    REGEN_ISP_ENERGY_TO_ISP,
    regen_isp_bonus_from_heat,
)
from .film import (  # noqa: F401
    FILM_ETA0_PER_FRACTION,
    FILM_ETA0_MAX,
    FILM_DECAY_THROAT_DIAMETERS,
    FILM_FLUX_FLOOR,
    FILM_MDOT_RATIO_REFERENCE,
    film_effectiveness_profile,
    nozzle_film_effectiveness_profile,
    combined_film_phi,
    film_adiabatic_wall_temp,
)
from .channels import (  # noqa: F401
    CHANNEL_PITCH_FRACTION,
    CHANNEL_PITCH_MIN_M,
    CHANNEL_PITCH_MAX_M,
    CHANNEL_LAND_FRACTION_DEFAULT,
    CHANNEL_ROUGHNESS_M,
    CHANNEL_MIN_COUNT,
    TARGET_COOLANT_VELOCITY_MS,
    _TARGET_COOLANT_VELOCITY_FALLBACK,
    CHANNEL_ASPECT_RATIO_MAX,
    SIEDER_TATE_C,
    SIEDER_TATE_RE_EXP,
    SIEDER_TATE_PR_EXP,
    SIEDER_TATE_VISC_EXP,
    LAMINAR_NU,
    RE_LAMINAR,
    CHANNEL_DP_CALIBRATION,
    WALL_CONSTRUCTIONS,
    H_C_CONSTRUCTION_FACTOR,
    DP_CONSTRUCTION_FACTOR,
    JACKET_MASS_CONSTRUCTION_FACTOR,
    channel_count,
    channel_target_height_m,
    channel_count_at_station,
    channel_hydraulic_geometry,
    passage_velocity_ms,
    channel_geometry_profile,
    coolant_side_htc,
    _darcy_friction,
)
from .wall import (  # noqa: F401
    coupled_wall_temps,
    GAS_SIDE_DEPOSIT_FACTOR,
    solve_wall_balance,
    solve_wall_balance_profile,
)
from .march import (  # noqa: F401
    _passage_v,
    _segments_to_stations,
    march_coolant,
    J2_DOWN_TO_UP_TUBE_RATIO,
    two_pass_tube_counts,
    down_pass_velocity_ms,
    march_coolant_two_pass,
)
# 2026-09-23 cooling audit: unified per-station thermal solve + its building blocks
from .gas_side import (  # noqa: F401
    BARTZ_OMEGA,
    adiabatic_wall_temperature_profile,
    bartz_hg_raw_profile,
    bartz_sigma,
    mach_profile,
    recovery_factor_from_prandtl,
)
from .channels import FIN_CONSTRUCTIONS, rib_fin_factor  # noqa: F401
from .coolant_state import CP_FALLBACK_J_KGK, CoolantModel  # noqa: F401
from .thermal_solve import (  # noqa: F401
    ABLATIVE,
    ACTIVE_METHODS,
    DUMP,
    RADIATIVE,
    REGEN,
    solve_thermal,
    station_treatments,
)
