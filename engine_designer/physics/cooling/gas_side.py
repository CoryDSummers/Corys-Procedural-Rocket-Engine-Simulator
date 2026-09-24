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

RECOVERY_FACTOR = 0.9            # turbulent recovery factor fallback [Huzel 4.4:
                                  # 0.90-0.98; TN-Dump App.B: 0.88]. The unified
                                  # thermal solve uses r = Pr^(1/3) from the real
                                  # frozen Prandtl number instead; this is only the
                                  # default of recovery_temperature().

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


def recovery_temperature(tc_k, r=RECOVERY_FACTOR, mach=0.0, gamma=1.2):
    """Adiabatic (recovery) wall temperature at local Mach `mach`:
    T_aw = T_s + r (T0 - T_s), T_s = T0 / (1 + (g-1)/2 M^2) [Huzel 4.4].
    2026-09-23: this used to return r * Tc - the recovery factor applied to the
    whole stagnation temperature (~350 K low at the throat). At M = 0 (the
    chamber) it is T0; at the throat (M = 1, g ~1.2) ~0.99 T0."""
    t_s = tc_k / (1.0 + 0.5 * (gamma - 1.0) * mach * mach)
    return t_s + r * (tc_k - t_s)


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
# 2026-09-23 cooling audit: ALL 1.0 - raw Bartz. The old LOX/LH2 0.55 / LOX/CH4
# 0.75 were compensating for bugs, not physics: LOX/LH2 cp/mu/Pr came from the
# performance table's effective gamma/M (cp too high, mu ~half, Eucken Pr 0.84
# vs the real frozen ~0.62), T_aw was 0.9*Tc instead of the recovery form, and
# sigma was fixed at 1. With chemical-equilibrium transport properties
# (physics/thermo_tables.py), the recovery T_aw and the real sigma, the UNSCALED
# unified thermal solve reproduces both cited LOX/LH2 anchors:
#   J-2   throat ~38 MW/m2 vs 17-35 Btu/in2-s = 28-57 MW/m2 [Wieseneck-J2 p.6,12]
#   SSME  throat ~140 MW/m2 vs design point 72 Btu/in2-s = 118 MW/m2 [Wieseneck-J2 p.6]
#   (validation_engines/ corpus, run_corpus --report). LOX/RP-1's real
# carbon-deposit reduction is carried by GAS_SIDE_DEPOSIT_FACTOR ([TP2862],
# 40-60 % below clean Bartz), now applied to the one h_g everywhere. Kept as a
# per-pair dict so a future CITED calibration can land here.
BARTZ_ABS_FLUX_CALIBRATION = {
    "LOX/RP-1": 1.00,
    "LOX/LH2": 1.00,
    "LOX/CH4": 1.00,
    "N2O4/MMH": 1.00,
    "Aerozine-50/NTO": 1.00,
    "Hydrazine": 1.00,
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


# --- station Mach, recovery temperature and Bartz sigma (2026-09-23 audit) -----
# The recovery temperature used to be T_aw = 0.9 * Tc everywhere - the recovery
# factor applied to the WHOLE stagnation temperature. Correct boundary-layer
# recovery only acts on the dynamic part: T_aw = T_s + r*(T0 - T_s), which is
# ~T0 in the chamber and ~0.99*T0 at the throat, not 0.9*T0 [Huzel 4.4; the
# nozzle-extension check already used this form]. r = Pr^(1/3), the turbulent
# flat-plate value, with Pr the FROZEN combustion-gas Prandtl number from the
# equilibrium tables (physics/thermo_tables.py).
# BARTZ sigma is the real property-variation correction [Huzel eq. 4-14, Bartz
# 1957; omega = 0.6 viscosity-temperature exponent]:
#   sigma = 1 / { [0.5*(Twg/T0)*(1 + (g-1)/2 M^2) + 0.5]^(0.8 - w/5)
#                 * [1 + (g-1)/2 M^2]^(w/5) }
# evaluated per station against the SOLVED wall temperature
# (cooling/thermal_solve.py iterates it) instead of the old constant 1.0.
BARTZ_OMEGA = 0.6


def recovery_factor_from_prandtl(prandtl):
    """Turbulent boundary-layer recovery factor r = Pr^(1/3)."""
    return max(prandtl, 1e-6) ** (1.0 / 3.0)


def _mach_subsonic(eps, gamma):
    from ..isentropic import area_ratio_from_mach
    from scipy.optimize import brentq
    if eps <= 1.0 + 1e-9:
        return 1.0
    return brentq(lambda m: area_ratio_from_mach(m, gamma) - eps, 1e-7, 1.0 - 1e-12)


def mach_profile(rs_m, throat_dia_m, gamma):
    """Isentropic Mach number at each contour station: the SUBSONIC root of
    A/A* upstream of the throat (chamber + convergent), the supersonic root
    downstream, exactly 1 at the throat station."""
    from ..isentropic import mach_from_area_ratio
    rs = np.asarray(rs_m, dtype=float)
    rt = throat_dia_m / 2.0
    ti = int(np.argmin(rs))
    out = np.empty(len(rs))
    for i, r in enumerate(rs):
        eps = max(_local_area_ratio(r, rt), 1.0)
        if i == ti or eps <= 1.0 + 1e-9:
            out[i] = 1.0
        elif i < ti:
            out[i] = _mach_subsonic(eps, gamma)
        else:
            out[i] = mach_from_area_ratio(eps, gamma)
    return out


def adiabatic_wall_temperature_profile(t0_k, gamma, mach, recovery_factor):
    """T_aw = T_s + r (T0 - T_s), T_s = T0 / (1 + (g-1)/2 M^2), per station."""
    m = np.asarray(mach, dtype=float)
    t_s = t0_k / (1.0 + 0.5 * (gamma - 1.0) * m * m)
    return t_s + recovery_factor * (t0_k - t_s)


def bartz_sigma(t_wg_over_t0, mach, gamma, omega=BARTZ_OMEGA):
    """Bartz boundary-layer property-variation correction (array-friendly)."""
    tw = np.asarray(t_wg_over_t0, dtype=float)
    m = np.asarray(mach, dtype=float)
    stag = 1.0 + 0.5 * (gamma - 1.0) * m * m
    return 1.0 / ((0.5 * tw * stag + 0.5) ** (0.8 - omega / 5.0) * stag ** (omega / 5.0))


def bartz_hg_raw_profile(xs_m, rs_m, throat_dia_m, pc_pa, cstar_ms, mu_pa_s, cp_j_kgk,
                         prandtl, sigma=None):
    """Per-station Bartz h_g [W/m^2K] x the injector-face taper x `sigma` (array or
    scalar; None = 1.0) - WITHOUT the per-class calibration or the carbon-deposit
    factor (the unified thermal solve applies each exactly once)."""
    xs = np.asarray(xs_m, dtype=float)
    rs = np.asarray(rs_m, dtype=float)
    n = len(xs)
    if throat_dia_m <= 0 or n < 2:
        return np.zeros(max(n, 1))
    rt = throat_dia_m / 2.0
    hg = np.array([bartz_hg(throat_dia_m, pc_pa, cstar_ms, mu_pa_s, cp_j_kgk, prandtl,
                            area_ratio=_local_area_ratio(r, rt), sigma=1.0) for r in rs])
    taper = _injector_face_taper(xs, rs, int(np.argmin(rs)))
    if taper is not None:
        hg[taper[0]] *= taper[1]
    return hg * (1.0 if sigma is None else np.asarray(sigma, dtype=float))


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
