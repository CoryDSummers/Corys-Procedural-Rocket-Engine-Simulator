"""
Expander cycle: no combustion drives the turbine at all. The regenerative-
cooling coolant (fuel) picks up heat from the chamber/nozzle wall, and only
THAT heat is available to drive the turbopump - a hard physical ceiling,
not a slider. This is the one new cycle that needed genuinely new physics
(see physics/cycles.py's docstring for why tap-off/FRSC/ORSC didn't).

Heat pickup now integrates the SAME computed-absolute Bartz flux profile
physics/cooling.py's cooling model uses (physics/cooling.
absolute_heat_flux_profile), over the same contour and cutoff design.py's
cooling_result reports - the two can't contradict each other (design.py's
wall_heat_total_w() and this module's heat_pickup_w() integrate the identical
profile). Before Phase 7 this used a flat, propellant-agnostic area-average
anchor; see physics/cooling.py's BARTZ_ABS_FLUX_CALIBRATION for the per-
propellant-class calibration this needed (LOX/LH2 designs run genuinely
hotter walls at a given Pc than LOX/RP-1, driven by hydrogen's much higher
gas cp - not modelled by a flat anchor).
"""
import math

import numpy as np

from . import turbopump as tp
from . import cooling
# The per-pair coolant limits live in physics/cooling.py (single source - the
# profile-resolved cooling model and this feasibility proxy must agree on
# them). Re-exported here so existing `expander.MAX_COOLANT_DELTA_T_K`
# callers keep working unchanged.
from .cooling import FUEL_CP_J_KGK, MAX_COOLANT_DELTA_T_K  # noqa: F401

ETA_EXPANDER_TURBINE = 0.55
COOLED_AREA_CUTOFF_EPS = 6.0  # DEFAULT ONLY - local area ratio beyond which real engines
                              # typically stop active cooling. design.py always passes its
                              # own design-driven cutoff (EngineDesign.cooled_length_eps,
                              # which cooling_transition_eps and, for a full-length regen
                              # nozzle, regen_nozzle_end_eps feed into) explicitly; this
                              # constant only matters to a caller that doesn't.


def cooled_surface_area(profile_xs_m, profile_rs_m, throat_dia_m, cutoff_area_ratio=COOLED_AREA_CUTOFF_EPS):
    """
    Approximate regeneratively-cooled wetted area: the full upstream section
    (injector face through the throat) plus the divergent nozzle up to
    `cutoff_area_ratio` (local area ratio relative to the throat) - design.py's
    cooled_length_eps, which can extend past the bell-material transition point
    for a full-length regen nozzle (regen_nozzle_end_eps).
    """
    rt = throat_dia_m / 2.0
    throat_idx = int(np.argmin(profile_rs_m))
    area = 0.0
    for i in range(len(profile_xs_m) - 1):
        r1, r2 = profile_rs_m[i], profile_rs_m[i + 1]
        x1, x2 = profile_xs_m[i], profile_xs_m[i + 1]
        if i >= throat_idx:
            local_eps = (max(r1, r2) / rt) ** 2
            if local_eps > cutoff_area_ratio:
                continue
        slant = math.hypot(x2 - x1, r2 - r1)
        area += math.pi * (r1 + r2) * slant  # frustum lateral surface area
    return area


def heat_pickup_w(xs_m, rs_m, throat_dia_m, pc_pa, cstar_ms, mu_pa_s, cp_j_kgk, prandtl,
                   t_aw_k, pair, cutoff_area_ratio=COOLED_AREA_CUTOFF_EPS):
    """
    Total heat [W] the coolant picks up over the cooled surface, integrated
    from cooling.absolute_heat_flux_profile (real per-station Bartz h_g, not a
    flat area-average anchor) - the same profile physics/design.py's
    wall_heat_total_w() integrates for the SAME contour/cutoff, so the two
    can't disagree. Returns (heat_w, mean_flux_w_m2).
    """
    q_profile = cooling.absolute_heat_flux_profile(
        xs_m, rs_m, throat_dia_m, pc_pa, cstar_ms, mu_pa_s, cp_j_kgk, prandtl, t_aw_k,
        pair=pair, transition_area_ratio=cutoff_area_ratio)
    total_w = cooling.wall_heat_total_w(xs_m, rs_m, q_profile, throat_dia_m=throat_dia_m,
                                        transition_area_ratio=cutoff_area_ratio)
    area = cooled_surface_area(xs_m, rs_m, throat_dia_m, cutoff_area_ratio)
    mean_flux = total_w / area if area > 0 else 0.0
    return total_w, mean_flux


def available_turbine_power_w(pair, mdot_fuel_kgs, heat_available_w, eta_turbine=None):
    """Available shaft power is capped by BOTH how much heat the wall gives
    up (heat_available_w) AND how much the coolant flow can absorb before
    its coking/thermal-stability limit. `eta_turbine` is the DERIVED reaction-
    turbine efficiency (physics/turbopump_efficiency.py); falls back to the flat
    ETA_EXPANDER_TURBINE when not supplied."""
    cp = FUEL_CP_J_KGK[pair]
    delta_t_max = MAX_COOLANT_DELTA_T_K[pair]
    max_absorbable_w = mdot_fuel_kgs * cp * delta_t_max
    heat_to_turbine = min(heat_available_w, max_absorbable_w)
    eta = eta_turbine if (eta_turbine or 0.0) > 0.0 else ETA_EXPANDER_TURBINE
    return heat_to_turbine * eta, max_absorbable_w


def expander_result(pair, mdot, mr, pc, dp_fuel, dp_ox, rho_fuel, rho_ox,
                     eta_fuel, eta_ox, specific_power_w_kg,
                     xs_m, rs_m, throat_dia_m, cstar_ms, mu_pa_s, cp_j_kgk, prandtl, t_aw_k,
                     cutoff_area_ratio=COOLED_AREA_CUTOFF_EPS, eta_turbine=None):
    tpump = tp.turbopump_power(mdot, mr, dp_fuel, dp_ox, rho_fuel, rho_ox, eta_fuel, eta_ox,
                                specific_power_w_kg)
    heat_w, flux = heat_pickup_w(xs_m, rs_m, throat_dia_m, pc, cstar_ms, mu_pa_s, cp_j_kgk,
                                 prandtl, t_aw_k, pair, cutoff_area_ratio)
    cooled_area_m2 = cooled_surface_area(xs_m, rs_m, throat_dia_m, cutoff_area_ratio)
    avail_w, max_absorbable_w = available_turbine_power_w(
        pair, tpump["mdot_fuel_kgs"], heat_w, eta_turbine)
    required_w = tpump["power_total_w"]
    margin = avail_w / required_w if required_w > 0 else float("inf")
    # Specific work per kg of turbine (fuel) flow, for physics/turbopump_sizing.py.
    mdot_fuel = tpump["mdot_fuel_kgs"]
    turbine_specific_work = avail_w / mdot_fuel if mdot_fuel > 0 else 0.0
    return {
        "cycle": "expander",
        "has_turbopump": True,
        "turbopump": tpump,
        "gg_mdot_kgs": 0.0,           # closed cycle - all coolant flow reaches the main chamber
        "gg_flow_fraction": 0.0,
        "gg_dump_isp_fraction": 1.0,  # no dump loss (see cycles.py docstring)
        "turbine_specific_work_j_kg": turbine_specific_work,
        "required_tank_pressure_pa": None,
        "heat_pickup_w": heat_w,
        "heat_flux_w_m2": flux,
        "cooled_area_m2": cooled_area_m2,
        "max_absorbable_heat_w": max_absorbable_w,
        "available_turbine_power_w": avail_w,
        "required_turbine_power_w": required_w,
        "feasibility_margin": margin,
    }
