"""Gas-side heat transfer: Bartz h_g, recovery temperature, the authoritative absolute wall-heat-flux profile and its per-propellant-class calibration.

Part of the physics/cooling/ package (split verbatim out of the former
single-file cooling.py - see cooling/__init__.py for the package overview)."""
import numpy as np

from .profile import BARTZ_AREA_RATIO_EXPONENT, INJECTOR_FLUX_FRACTION, _local_area_ratio

# Stefan-Boltzmann constant [W/m^2/K^4], for the radiation-cooled
# nozzle-extension equilibrium (Huzel eq. 4-38).
STEFAN_BOLTZMANN_W_M2K4 = 5.670374419e-8

# --- gas-side Bartz coefficient --------------------------------------------------
# Huzel eq. 4-13 (SI form, the English-units gravitational term folded away):
#   h_g = (0.026 / Dt^0.2) * (mu^0.2 * cp / Pr^0.6) * (Pc / c*)^0.8
#         * (Dt / r_curv)^0.1 * sigma * (At / A)^0.9
# This is the REAL gas-side coefficient the area-averaged anchor below only
# approximates. It needs combustion-gas transport properties (mu, Pr) which
# physics/combustion.py now derives (gas_viscosity_pa_s / prandtl). sigma is
# the boundary-layer property-variation correction [Huzel Fig 4-24], a weak
# function of Twg/Tc, gamma and local Mach; held at a single calibrated
# constant here (same honesty tier as combustion.DEFAULT_ETA_CSTAR) and pinned
# by validate.py's run_cooling_heat_flux_check() against F-1 / SSME / RL10.
BARTZ_COEFF = 0.026
BARTZ_SIGMA = 1.0            # [Huzel Fig 4-24] property-variation correction, calibrated
BARTZ_RC_OVER_DT = 1.0       # throat curvature radius / throat dia; a real throat runs
                             # ~0.5-1.5, and (Dt/rc)^0.1 stays within ~3% of 1 across that

RECOVERY_FACTOR = 0.9            # turbulent recovery factor, T_aw = r * Tc
                                  # [Huzel 4.4: 0.90-0.98; TN-Dump App.B: 0.88].
                                  # Carried for annotation/context; the anchored
                                  # magnitude already bakes in a representative
                                  # (T_aw - T_wall).

# --- real gas-side Bartz coefficient + computed wall temperature ---------------

def bartz_hg(throat_dia_m, pc_pa, cstar_ms, mu_pa_s, cp_j_kgk, prandtl,
             area_ratio=1.0, rc_over_dt=BARTZ_RC_OVER_DT, sigma=BARTZ_SIGMA):
    """
    Gas-side heat-transfer coefficient h_g [W/m^2/K] from the Bartz correlation
    (Huzel eq. 4-13, SI form). `area_ratio` = (A_local / At), so the default 1.0
    gives the throat value; pass the local contour ratio to get h_g up the
    chamber / down the nozzle (falls as (At/A)^0.9).
    """
    if throat_dia_m <= 0 or cstar_ms <= 0 or prandtl <= 0:
        return 0.0
    core = (BARTZ_COEFF / throat_dia_m ** 0.2
            * (mu_pa_s ** 0.2 * cp_j_kgk / prandtl ** 0.6)
            * (pc_pa / cstar_ms) ** 0.8
            * (1.0 / rc_over_dt) ** 0.1
            * sigma)
    return core * area_ratio ** (-BARTZ_AREA_RATIO_EXPONENT)


def recovery_temperature(tc_k, r=RECOVERY_FACTOR):
    """Adiabatic (recovery) wall temperature T_aw = r * Tc, r ~ 0.90 for a
    turbulent boundary layer [Huzel 4.4]. Replaces the implicit T_aw = Tc
    (recovery factor 1.0) that materials.py's proxy assumes."""
    return r * tc_k


def wall_gas_temperature(q_w_m2, h_g_w_m2k, t_aw_k):
    """Hot-gas-side wall temperature from q = h_g * (T_aw - T_wg)  [Huzel eq.
    4-10], inverted for T_wg. This is the number materials.thermal_margin()
    should compare to a material's max service temperature - a real computed
    wall temperature instead of the flat Tc * cooling_effectiveness proxy."""
    if h_g_w_m2k <= 0:
        return t_aw_k
    return t_aw_k - q_w_m2 / h_g_w_m2k



# --- computed-absolute Bartz flux profile (Phase 7 - now AUTHORITATIVE) ------
# design.py's gas-side flux was, until Phase 7, anchored to a conservative,
# propellant-agnostic area-average (reference_area_avg_flux_w_m2, Pc^0.8 only,
# kept below as a REPORTED comparison). This function instead computes
# q(x) = h_g(x)*(T_aw - T_wg) STATION BY STATION from the real Bartz h_g
# (bartz_hg, fed real combustion-gas transport properties) - the throat peak is
# a genuine Bartz value, not shape-normalised to an anchor. T_wg is held at a
# single representative fraction of T_aw (no per-station wall-temperature
# solve - that would need per-station coolant/material data this function
# doesn't have); the SPATIAL variation comes entirely from h_g's own
# (At/A)^0.9 falloff, the textbook Bartz behaviour, not a second assumed shape
# (avoiding the double-counting bug CLAUDE.md warns about). The same finite-
# combustion-length injector-face taper heat_flux_profile() uses is applied
# here too (a real effect, independent of h_g/T_wg).
#
# WALL_TEMP_FRACTION_DEFAULT (0.25) matches materials.py's cooling_effectiveness
# low end (a well-cooled copper liner).
#
# BARTZ_ABS_FLUX_CALIBRATION is PER-PROPELLANT-CLASS, not one flat constant -
# **a real finding from validating this**: the real Bartz h_g depends on Pc/c*
# (not Pc alone, unlike the old flat anchor) plus a mu^0.2*cp/Pr^0.6 gas-
# property term. Hydrogen's very low molar mass drives a much higher gas cp,
# so LOX/LH2 designs come out ~2-2.7x a LOX/RP-1-class design's ratio to the
# old anchor at otherwise-comparable conditions - a real, well-known effect
# (why LH2 stages have historically had the harder wall-cooling problem for a
# given Pc), not a bug. A single flat constant cannot bring both propellant
# classes within the tool's own existing per-engine jet-power-fraction-to-walls
# bands (WALL_HEAT_ENERGY_FRACTION_TYPICAL / validate.py's COOLING_CHECKS
# e_frac_lo/hi, themselves [Sutton 8.2]-anchored) at the same time as leaving
# real per-pair differentiation intact - so LOX/RP-1 keeps ~today's magnitude
# (1.00, it was already close) while LOX/LH2 is scaled down (0.55) enough that
# both SSME- and RL10-class references land back inside their existing
# (already RL10-widened) e_frac bands. Only these two classes are anchored
# against real engines; the rest interpolate/default (Tier 3) - see
# ASSUMPTIONS.md.
WALL_TEMP_FRACTION_DEFAULT = 0.25
BARTZ_ABS_FLUX_CALIBRATION = {
    "LOX/RP-1": 1.00,        # F-1-anchored
    "LOX/LH2": 0.55,         # SSME- and RL10-class-anchored
    "LOX/CH4": 0.75,         # interpolated (molar mass between RP-1 and LH2) - not independently anchored
    "N2O4/MMH": 1.00,        # storable, combustion-product molar mass close to RP-1's
    "Aerozine-50/NTO": 1.00,
    "Hydrazine": 1.00,       # monopropellant decomposition products, RP-1-like molar mass order
    "H2O2": 1.00,
}
_BARTZ_ABS_FLUX_CALIBRATION_FALLBACK = 1.00


def absolute_heat_flux_profile(xs_m, rs_m, throat_dia_m, pc_pa, cstar_ms, mu_pa_s,
                                cp_j_kgk, prandtl, t_aw_k, *, wall_temp_k=None,
                                pair=None, transition_area_ratio=None):
    """
    Per-station wall heat flux [W/m^2] computed directly from the real Bartz h_g
    at each station's local area ratio, q(x) = h_g(x) * (T_aw - T_wg). Unlike
    heat_flux_profile(), the magnitude is NOT normalised to a flat area-average
    anchor - it is the genuine Bartz value x BARTZ_ABS_FLUX_CALIBRATION[pair]
    (falls back to 1.0 for an unrecognised/omitted pair). `wall_temp_k`
    overrides the WALL_TEMP_FRACTION_DEFAULT*T_aw fallback (a single
    representative value, not station-varying). `transition_area_ratio` only
    affects the injector-face taper's cylindrical-run detection, matching
    heat_flux_profile()'s contour handling.
    """
    xs = np.asarray(xs_m, dtype=float)
    rs = np.asarray(rs_m, dtype=float)
    n = len(xs)
    if throat_dia_m <= 0 or n < 2:
        return np.zeros(max(n, 1))
    rt = throat_dia_m / 2.0
    throat_idx = int(np.argmin(rs))
    twg = wall_temp_k if wall_temp_k is not None else WALL_TEMP_FRACTION_DEFAULT * t_aw_k
    calibration = BARTZ_ABS_FLUX_CALIBRATION.get(pair, _BARTZ_ABS_FLUX_CALIBRATION_FALLBACK)
    q = np.array([
        max(0.0, bartz_hg(throat_dia_m, pc_pa, cstar_ms, mu_pa_s, cp_j_kgk, prandtl,
                          area_ratio=_local_area_ratio(r, rt)) * (t_aw_k - twg))
        for r in rs
    ])
    # Same finite-combustion-length injector-face taper as heat_flux_profile().
    taper = _injector_face_taper(xs, rs, throat_idx)
    if taper is not None:
        q[taper[0]] *= taper[1]
    return q * calibration


def _injector_face_taper(xs, rs, throat_idx):
    """(mask, multiplier) of the finite-combustion-length injector-face taper on
    the cylindrical chamber run - INJECTOR_FLUX_FRACTION at the face rising
    linearly to 1.0 at the end of the barrel - or None when the contour has no
    cylindrical run. Shared by absolute_heat_flux_profile and bartz_hg_profile."""
    n = len(xs)
    cyl_mask = np.isclose(rs, rs[0], rtol=1e-6) & (np.arange(n) <= throat_idx)
    if cyl_mask.sum() > 1:
        cyl_x = xs[cyl_mask]
        span = cyl_x[-1] - cyl_x[0]
        if span > 0:
            frac = (cyl_x - cyl_x[0]) / span
            return cyl_mask, INJECTOR_FLUX_FRACTION + (1.0 - INJECTOR_FLUX_FRACTION) * frac
    return None


def bartz_hg_profile(xs_m, rs_m, throat_dia_m, pc_pa, cstar_ms, mu_pa_s, cp_j_kgk,
                     prandtl, *, pair=None):
    """
    Per-station gas-side h_g [W/m^2K] on the SAME basis as
    absolute_heat_flux_profile's flux: raw Bartz h_g at each station's local
    area ratio x the injector-face taper x BARTZ_ABS_FLUX_CALIBRATION[pair] - so
    h_g(x) * (T_aw - T_wg) reproduces that profile for a uniform T_wg. The input
    to the full-length coupled wall balance (solve_wall_balance_profile);
    GAS_SIDE_DEPOSIT_FACTOR is applied by the caller, exactly as at the throat.
    """
    xs = np.asarray(xs_m, dtype=float)
    rs = np.asarray(rs_m, dtype=float)
    n = len(xs)
    if throat_dia_m <= 0 or n < 2:
        return np.zeros(max(n, 1))
    rt = throat_dia_m / 2.0
    throat_idx = int(np.argmin(rs))
    hg = np.array([bartz_hg(throat_dia_m, pc_pa, cstar_ms, mu_pa_s, cp_j_kgk, prandtl,
                            area_ratio=_local_area_ratio(r, rt)) for r in rs])
    taper = _injector_face_taper(xs, rs, throat_idx)
    if taper is not None:
        hg[taper[0]] *= taper[1]
    return hg * BARTZ_ABS_FLUX_CALIBRATION.get(pair, _BARTZ_ABS_FLUX_CALIBRATION_FALLBACK)
