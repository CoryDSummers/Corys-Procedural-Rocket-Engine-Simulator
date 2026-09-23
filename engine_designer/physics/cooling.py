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
import math

import numpy as np

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

# --- magnitude anchor (shared with physics/expander.py, which imports these) ---
# Representative regen-chamber wall heat flux AREA-AVERAGED over the actively
# cooled surface (injector face -> throat -> cooling-transition area ratio), at
# a reference chamber pressure, scaled with a Bartz-like Pc^0.8 term. Point is
# RL10 / regen-cooled-chamber duty; deliberately conservative. Not derived.
HEAT_FLUX_REFERENCE_W_M2 = 5.0e6
PC_REFERENCE_PA = 4.0e6
HEAT_FLUX_PC_EXPONENT = 0.8

# --- flux-profile shape -------------------------------------------------------
BARTZ_AREA_RATIO_EXPONENT = 0.9   # gas-side h_g ~ (At/A)^0.9  [Huzel eq. 4-13; Sutton Fig 8-8]
INJECTOR_FLUX_FRACTION = 0.6      # finite combustion length: the chamber's first
                                  # stretch runs cooler than Bartz predicts
                                  # (claude_lit/topics/07 - "over-cooled zone,
                                  # first ~3 in from the injector"). Flux ramps
                                  # from this fraction of the local-Bartz value
                                  # at the injector face to 1.0 at the chamber
                                  # end. Reasoned, not independently sourced.
RECOVERY_FACTOR = 0.9            # turbulent recovery factor, T_aw = r * Tc
                                  # [Huzel 4.4: 0.90-0.98; TN-Dump App.B: 0.88].
                                  # Carried for annotation/context; the anchored
                                  # magnitude already bakes in a representative
                                  # (T_aw - T_wall).

# Fraction-of-jet-power reaching the walls, plausibility band only
# [Sutton 8.2: "0.5-5 % of the total energy generated reaches the walls"],
# widened for the coarseness of this model.
WALL_HEAT_ENERGY_FRACTION_TYPICAL = (0.003, 0.06)

# --- coolant side (owned here; physics/expander.py imports these) -------------
# Max practical coolant (fuel-side) temperature rise before the turbine / before
# the jacket outlet, per propellant pair. Hydrocarbons coke (crack into solid
# channel-fouling deposits) well below hydrogen's limits - this is why real
# expander-cycle engines are LH2-only and why a hydrocarbon regen jacket at high
# Pc runs out of margin.
MAX_COOLANT_DELTA_T_K = {
    "LOX/LH2": 500.0,
    "LOX/RP-1": 120.0,
    "LOX/CH4": 250.0,        # methane cokes far less than RP-1, well above LH2's limit
    "N2O4/MMH": 150.0,
}
FUEL_CP_J_KGK = {
    "LOX/LH2": 14300.0,
    "LOX/RP-1": 2100.0,
    "LOX/CH4": 3450.0,       # liquid/supercritical methane
    "N2O4/MMH": 2900.0,
}


def _frustum_area(x0, r0, x1, r1):
    """Lateral surface area of the frustum swept by revolving segment (x0,r0)-(x1,r1)."""
    return math.pi * (r0 + r1) * math.hypot(x1 - x0, r1 - r0)


def _local_area_ratio(r, r_throat):
    return (r / r_throat) ** 2 if r_throat > 0 else 1.0


def _bartz_shape(area_ratio):
    """Normalised gas-side heat-flux shape: 1.0 at the throat, ~(1/CR)^0.9 in
    the chamber, falling as (At/A)^0.9 down the nozzle."""
    return area_ratio ** (-BARTZ_AREA_RATIO_EXPONENT)


def reference_area_avg_flux_w_m2(pc_pa):
    """The Pc-scaled area-average anchor flux (shared with expander.heat_pickup_w)."""
    return HEAT_FLUX_REFERENCE_W_M2 * (pc_pa / PC_REFERENCE_PA) ** HEAT_FLUX_PC_EXPONENT


def _shape_profile(xs_m, rs_m, throat_dia_m):
    """Per-station relative flux shape, incl. the injector-side finite-combustion taper."""
    xs = np.asarray(xs_m, dtype=float)
    rs = np.asarray(rs_m, dtype=float)
    rt = throat_dia_m / 2.0
    throat_idx = int(np.argmin(rs))
    shape = np.array([_bartz_shape(_local_area_ratio(r, rt)) for r in rs])

    # Taper across the constant-radius cylindrical chamber (x=0 to the convergent
    # cone). rs[0] is the chamber radius; the cylindrical run is the leading
    # points that share it, up to the throat.
    cyl_mask = np.isclose(rs, rs[0], rtol=1e-6) & (np.arange(len(rs)) <= throat_idx)
    if cyl_mask.sum() > 1:
        cyl_x = xs[cyl_mask]
        span = cyl_x[-1] - cyl_x[0]
        if span > 0:
            frac = (cyl_x - cyl_x[0]) / span
            shape[cyl_mask] *= INJECTOR_FLUX_FRACTION + (1.0 - INJECTOR_FLUX_FRACTION) * frac
    return shape


def heat_flux_profile(xs_m, rs_m, throat_dia_m, pc_pa, transition_area_ratio=None):
    """
    Per-station wall heat flux [W/m^2] along the (xs_m, rs_m) contour.

    The magnitude is set so the AREA-WEIGHTED MEAN of the returned flux over the
    actively-cooled zone (injector face through the throat and out to
    `transition_area_ratio`; the whole contour if None) equals
    `reference_area_avg_flux_w_m2(pc_pa)` - i.e. exactly the flat flux
    expander.heat_pickup_w() applies over the same area. The per-station values
    just redistribute that total onto the real (At/A)^0.9 profile, so the throat
    peak comes out several times the mean.
    """
    xs = np.asarray(xs_m, dtype=float)
    rs = np.asarray(rs_m, dtype=float)
    rt = throat_dia_m / 2.0
    throat_idx = int(np.argmin(rs))
    shape = _shape_profile(xs, rs, throat_dia_m)

    total_area = 0.0
    weighted = 0.0
    for i in range(len(rs) - 1):
        if (transition_area_ratio is not None and i >= throat_idx
                and _local_area_ratio(max(rs[i], rs[i + 1]), rt) > transition_area_ratio):
            continue
        a = _frustum_area(xs[i], rs[i], xs[i + 1], rs[i + 1])
        total_area += a
        weighted += a * 0.5 * (shape[i] + shape[i + 1])
    mean_shape = weighted / total_area if total_area > 0 else 1.0

    k = reference_area_avg_flux_w_m2(pc_pa) / mean_shape if mean_shape > 0 else 0.0
    return shape * k


def wall_heat_total_w(xs_m, rs_m, q_profile_w_m2, throat_dia_m=None, transition_area_ratio=None):
    """
    Integrate the heat-flux profile over the revolved (frustum) wetted area.
    With `transition_area_ratio` (and `throat_dia_m`) given, only the actively
    cooled zone out to that local area ratio past the throat is counted -
    matching expander.cooled_surface_area's cutoff.
    """
    xs = np.asarray(xs_m, dtype=float)
    rs = np.asarray(rs_m, dtype=float)
    q = np.asarray(q_profile_w_m2, dtype=float)
    rt = (throat_dia_m / 2.0) if throat_dia_m else 0.0
    throat_idx = int(np.argmin(rs))
    total = 0.0
    for i in range(len(rs) - 1):
        if (transition_area_ratio is not None and rt > 0 and i >= throat_idx
                and _local_area_ratio(max(rs[i], rs[i + 1]), rt) > transition_area_ratio):
            continue
        a = _frustum_area(xs[i], rs[i], xs[i + 1], rs[i + 1])
        total += a * 0.5 * (q[i] + q[i + 1])
    return total


def area_weighted_mean(xs_m, rs_m, values, throat_dia_m=None, transition_area_ratio=None):
    """Frustum-wetted-area-weighted mean of per-station `values` over the cooled
    zone (same injector-face -> throat -> transition_area_ratio cutoff as
    heat_flux_profile / wall_heat_total_w). Returns 1.0 for a degenerate contour."""
    xs = np.asarray(xs_m, dtype=float)
    rs = np.asarray(rs_m, dtype=float)
    v = np.asarray(values, dtype=float)
    rt = (throat_dia_m / 2.0) if throat_dia_m else 0.0
    throat_idx = int(np.argmin(rs))
    tot_a = 0.0
    tot_va = 0.0
    for i in range(len(rs) - 1):
        if (transition_area_ratio is not None and rt > 0 and i >= throat_idx
                and _local_area_ratio(max(rs[i], rs[i + 1]), rt) > transition_area_ratio):
            continue
        a = _frustum_area(xs[i], rs[i], xs[i + 1], rs[i + 1])
        tot_a += a
        tot_va += a * 0.5 * (v[i] + v[i + 1])
    return tot_va / tot_a if tot_a > 0 else 1.0


def coolant_temp_rise_k(total_heat_w, mdot_coolant_kgs, cp_j_kgk):
    """Bulk coolant temperature rise if `total_heat_w` is dumped into a coolant
    stream of `mdot_coolant_kgs` at specific heat `cp_j_kgk`."""
    if not mdot_coolant_kgs or not cp_j_kgk or mdot_coolant_kgs <= 0 or cp_j_kgk <= 0:
        return 0.0
    return total_heat_w / (mdot_coolant_kgs * cp_j_kgk)


def coolant_limit_k(pair):
    """Coking/boiling coolant delta-T limit for `pair`, or None if not tabulated."""
    return MAX_COOLANT_DELTA_T_K.get(pair)


def regen_feasible(delta_t_k, pair):
    """True if a regen jacket carrying the fuel can absorb the wall heat within
    the coking/boiling limit. Unknown pair -> True (no basis to warn)."""
    limit = MAX_COOLANT_DELTA_T_K.get(pair)
    return limit is None or delta_t_k <= limit


# --- cooling method as an explicit per-section design choice -----------------
# The chamber and the nozzle/bell each get their own cooling method. Until now
# the method was inferred from the chosen material (materials.Material.
# cooling_method - one value per material); an EngineDesign field of "auto" keeps
# exactly that, an explicit value overrides it - but ONLY within the material's
# allowed_cooling_methods (resolve_cooling_method_checked below).
#
# "film" is NOT a section method (it was until 2026-09-23): fuel-film cooling is
# an OVERLAY on top of whichever method a section uses - the chamber curtain
# (EngineDesign.film_cooling_fraction, film_effectiveness_profile) and the
# nozzle-extension slot (EngineDesign.nozzle_film_fraction,
# nozzle_film_effectiveness_profile) - so regen + film, ablative + film,
# radiative extension + slot film all combine in the flux / T_aw math. A
# film-cooled-only wall is "uncooled" + the overlay.
COOLING_METHODS = ("regenerative", "dump", "radiative", "ablative", "uncooled")


def resolve_cooling_method(explicit, material_default):
    """The cooling method requested for a section: `material_default` (the
    material's own cooling_method) when `explicit` is "" / "auto" / None,
    otherwise `explicit`. No compatibility check - see
    resolve_cooling_method_checked, which design.py uses."""
    if not explicit or explicit == "auto":
        return material_default
    return explicit


def resolve_cooling_method_checked(explicit, material):
    """
    The cooling method actually in effect for a section built from `material`
    (a materials.Material), HARD-BLOCKING physically meaningless choices.

    Returns (method, rejected): `rejected` is None when the request was honoured
    ("auto", or an explicit method in material.allowed_cooling_methods), else
    the rejected explicit name - in which case `method` falls back to the
    material's own cooling_method. Unknown / retired names (e.g. the pre-overlay
    "film") are rejected the same way. The caller surfaces a rejection as a
    failing checklist row; old project files are never rewritten.
    """
    requested = resolve_cooling_method(explicit, material.cooling_method)
    allowed = material.allowed_cooling_methods or (material.cooling_method,)
    if requested in allowed and requested in COOLING_METHODS:
        return requested, None
    return material.cooling_method, requested


# --- dump cooling: coolant ejected overboard, not returned to the injector ---
# A small coolant bleed absorbs the wall heat exactly like a regen jacket, but is
# ejected overboard at the nozzle lip instead of returning to the main injector -
# Vulcain HM-60's dump-cooled nozzle extension (header Isp 431.5 s vac), J-2's
# turbine-exhaust-dump-cooled skirt. It still contributes SOME thrust (ejected
# near the nozzle lip, well below the core exhaust velocity), so the net Isp
# loss is only a fraction of what losing that propellant flow entirely would
# cost [Sutton 8.2's dump-cooling discussion]. design.py applies this to the
# NOZZLE-EXTENSION portion only (nozzle_cooling_method="dump") - real engines
# dump-cool skirts, not main chambers.
#
# Tier 3: DUMP_THRUST_RECOVERY_FRACTION is an engineering estimate (the dumped
# stream's effective specific impulse as a fraction of the core chamber's), not
# independently sourced; the auto-sizing floor/ceiling are sanity bounds on a
# bled coolant stream, not per-engine data.
DUMP_THRUST_RECOVERY_FRACTION = 0.40   # k_dump
DUMP_COOLANT_FRACTION_MIN = 0.02       # auto-size floor - not worth modelling below this
DUMP_COOLANT_FRACTION_MAX = 0.25       # auto-size ceiling - a sane bound on a bled stream


def size_dump_coolant_fraction(wall_heat_w, mdot_fuel_kgs, cp_j_kgk, dt_limit_k):
    """
    Fuel fraction (of mdot_fuel_kgs) a dump-cooled coolant stream needs to absorb
    `wall_heat_w` while staying within a coolant temperature rise of `dt_limit_k`
    (the pair's coking/boiling limit) - the auto-sizing counterpart to
    march_coolant's channel-count/height auto-sizing. Clamped to
    [DUMP_COOLANT_FRACTION_MIN, DUMP_COOLANT_FRACTION_MAX].
    """
    if mdot_fuel_kgs <= 0.0 or cp_j_kgk <= 0.0 or dt_limit_k <= 0.0:
        return DUMP_COOLANT_FRACTION_MIN
    needed_mdot = wall_heat_w / (cp_j_kgk * dt_limit_k)
    frac = needed_mdot / mdot_fuel_kgs
    return min(DUMP_COOLANT_FRACTION_MAX, max(DUMP_COOLANT_FRACTION_MIN, frac))


def dump_cooling_isp_penalty_fraction(dump_mdot_kgs, total_mdot_kgs):
    """
    Net fractional Isp loss from dumping `dump_mdot_kgs` of the total propellant
    flow `total_mdot_kgs` overboard at the nozzle lip instead of through the main
    injector:
        Isp_new / Isp_core = 1 - (1 - DUMP_THRUST_RECOVERY_FRACTION) * (dump/total)
    i.e. the dumped stream still contributes DUMP_THRUST_RECOVERY_FRACTION of the
    core Isp, not zero. Returns 0.0 for no dump flow / no total flow.
    """
    if total_mdot_kgs <= 0.0 or dump_mdot_kgs <= 0.0:
        return 0.0
    ratio = min(1.0, dump_mdot_kgs / total_mdot_kgs)
    return (1.0 - DUMP_THRUST_RECOVERY_FRACTION) * ratio


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


def radiative_wall_temperature(h_gc_w_m2k, t_aw_k, emissivity, tol=0.5, max_iter=60):
    """
    Equilibrium wall temperature of a RADIATION-cooled surface (no active
    coolant loop): the temperature that satisfies both the gas-side convective
    input and the re-radiated flux,
        h_gc * (T_aw - T_wg) = emissivity * sigma_SB * T_wg^4   [Huzel eq. 4-38].
    Solved by bisection on [0, T_aw]. This is the right check for whether a
    niobium / C-103 / rhenium nozzle extension actually survives where the
    cooling transition is placed - materials.py otherwise just compares the
    local GAS temperature to the material limit.
    """
    if h_gc_w_m2k <= 0 or emissivity <= 0:
        return t_aw_k
    lo, hi = 0.0, t_aw_k

    def imbalance(twg):
        return h_gc_w_m2k * (t_aw_k - twg) - emissivity * STEFAN_BOLTZMANN_W_M2K4 * twg ** 4

    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        f = imbalance(mid)
        if abs(f) < tol or (hi - lo) < tol:
            return mid
        # imbalance is monotonically decreasing in twg
        if f > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# --- regenerative-cooling Isp credit ------------------------------------------
# [Sutton 8.2]: the heat the coolant absorbs is not wasted - it augments the
# propellant's energy content before injection, raising exhaust velocity
# 0.1-1.5 %. Not modelled before this (the tool credited exactly zero).
REGEN_ISP_BONUS_MIN = 0.001
REGEN_ISP_BONUS_MAX = 0.015


def regen_isp_bonus_fraction(coolant_delta_t_k, pair):
    """Fractional exhaust-velocity (hence Isp) gain from regenerative heat
    recovery, scaled within [Sutton 8.2]'s 0.1-1.5 % band by how hard the
    coolant is working (its temperature rise vs the pair's practical limit).
    Returns 0.0 for a pair with no tabulated coolant limit."""
    limit = MAX_COOLANT_DELTA_T_K.get(pair)
    if not limit or coolant_delta_t_k <= 0:
        return 0.0
    frac = min(1.0, coolant_delta_t_k / limit)
    return REGEN_ISP_BONUS_MIN + (REGEN_ISP_BONUS_MAX - REGEN_ISP_BONUS_MIN) * frac


# --- fuel-film / curtain cooling as a length-decaying flux reduction --------
# A cool fuel curtain injected at (or downstream of) the injector face shields
# the wall; its effectiveness eta_f is highest at injection and decays as the hot
# core entrains it. The local gas-side flux is multiplied station-by-station by
# phi(x) = 1 - eta_f(x), with eta_f(x) = eta_f0 * exp(-(s - s_inject)/L_decay)
# for stations downstream of injection (phi = 1 upstream). This REPLACES the old
# flat `1 - FILM_COOLING_FLUX_REDUCTION*f` knock-down, which protected the whole
# chamber+throat equally and never recovered.
#
# Tier 3: the exp-decay SHAPE and the calibration are engineering estimates -
# tuned so ~10% film on an F-1-class chamber gives ~0.55x throat flux (throat
# wall back under the NARloy-Z limit) recovering toward ~1x down the nozzle, and
# ~2% film is a gentle ~0.9x area-average. Anchors: F-1 (~10-12% of fuel as a
# boundary curtain), RD-170 (film-cooled ORSC chamber).
FILM_ETA0_PER_FRACTION = 7.0        # eta_f0 = min(cap, this * film_mdot_ratio)
FILM_ETA0_MAX = 0.75               # a heavy curtain still can't perfectly shield the wall
FILM_DECAY_THROAT_DIAMETERS = 2.5   # curtain 1/e persistence length L_decay = this * Dt
FILM_FLUX_FLOOR = 0.35            # phi floor - the wall always sees some flux
FILM_MDOT_RATIO_REFERENCE = 0.03   # documented reference film fraction (informational)


def film_effectiveness_profile(xs_m, rs_m, throat_dia_m, film_mdot_ratio,
                                inject_area_ratio=None):
    """
    Per-station gas-side heat-flux multiplier phi in [FILM_FLUX_FLOOR, 1.0] from a
    fuel-film curtain of `film_mdot_ratio` (= film fuel / total fuel flow).
    Injected at the injector face, or - if `inject_area_ratio` (> 1) is given - at
    the first contour station whose local area ratio is at/below it (a downstream
    slot). All-ones for film_mdot_ratio <= 0.
    """
    xs = np.asarray(xs_m, dtype=float)
    rs = np.asarray(rs_m, dtype=float)
    n = len(xs)
    if film_mdot_ratio <= 0.0 or throat_dia_m <= 0.0 or n < 2:
        return np.ones(max(n, 1))
    seg = np.hypot(np.diff(xs), np.diff(rs))
    s = np.concatenate([[0.0], np.cumsum(seg)])            # arc length from injector face
    s_inject = 0.0
    if inject_area_ratio and inject_area_ratio > 1.0:
        rt = throat_dia_m / 2.0
        thr = int(np.argmin(rs))
        for i in range(n):
            if i <= thr and (rs[i] / rt) ** 2 <= inject_area_ratio:
                s_inject = s[i]
                break
    eta0 = min(FILM_ETA0_MAX, FILM_ETA0_PER_FRACTION * film_mdot_ratio)
    l_decay = FILM_DECAY_THROAT_DIAMETERS * throat_dia_m
    eta = np.where(s >= s_inject, eta0 * np.exp(-(s - s_inject) / l_decay), 0.0)
    return np.clip(1.0 - eta, FILM_FLUX_FLOOR, 1.0)


# --- nozzle-extension film slot (the second, independent film site) ---------
# A fuel film injected through a slot/manifold on the SUPERSONIC nozzle wall at
# area ratio `inject_eps` - the F-1's film-cooled extension (film from 10:1 to
# the 16:1 exit [SP-8120]; there turbine exhaust, here post-jacket fuel), J-2X
# and Vulcain practice. Same eta_f0 law as the chamber curtain, but the decay
# length scales with the LOCAL wall diameter at the slot (the film's
# persistence scales with the boundary-layer/stream size it sits in, not the
# throat's), so a slot at eps 10 persists ~sqrt(10)x longer than a face curtain.
#
# Tier 3: no film-effectiveness correlation in hand - NASA SP-8124 (the
# self-cooled-chamber / film-cooling monograph) is the missing source (see
# claude_lit/OPEN_QUESTIONS.md), and [SECA-HT] shows decay length is the hard
# part even for CFD. Trust the direction, not the magnitude.
def nozzle_film_effectiveness_profile(xs_m, rs_m, throat_dia_m, film_mdot_ratio,
                                      inject_eps):
    """
    Per-station flux multiplier phi in [FILM_FLUX_FLOOR, 1.0] from a nozzle-
    extension film slot carrying `film_mdot_ratio` (= slot film fuel / total fuel
    flow), injected at the first SUPERSONIC station whose local area ratio is
    >= `inject_eps`. phi = 1 upstream of the slot; all-ones when the fraction is
    <= 0, `inject_eps` <= 1, or the slot lies beyond the contour's exit.
    """
    xs = np.asarray(xs_m, dtype=float)
    rs = np.asarray(rs_m, dtype=float)
    n = len(xs)
    if (film_mdot_ratio <= 0.0 or throat_dia_m <= 0.0 or n < 2
            or not inject_eps or inject_eps <= 1.0):
        return np.ones(max(n, 1))
    rt = throat_dia_m / 2.0
    thr = int(np.argmin(rs))
    i_slot = next((i for i in range(thr + 1, n) if (rs[i] / rt) ** 2 >= inject_eps), None)
    if i_slot is None:
        return np.ones(n)
    seg = np.hypot(np.diff(xs), np.diff(rs))
    s = np.concatenate([[0.0], np.cumsum(seg)])
    eta0 = min(FILM_ETA0_MAX, FILM_ETA0_PER_FRACTION * film_mdot_ratio)
    l_decay = FILM_DECAY_THROAT_DIAMETERS * 2.0 * rs[i_slot]
    eta = np.where(np.arange(n) >= i_slot,
                   eta0 * np.exp(-(s - s[i_slot]) / l_decay), 0.0)
    return np.clip(1.0 - eta, FILM_FLUX_FLOOR, 1.0)


def combined_film_phi(phi_chamber, phi_nozzle):
    """Both film sites together: the product of the two multipliers (treated as
    independent films - Tier 3), clipped at FILM_FLUX_FLOOR. With no slot film
    (phi_nozzle all ones) this returns phi_chamber unchanged."""
    return np.clip(np.asarray(phi_chamber, dtype=float) * np.asarray(phi_nozzle, dtype=float),
                   FILM_FLUX_FLOOR, 1.0)


def film_adiabatic_wall_temp(t_aw_k, phi, t_film_k):
    """Effective adiabatic-wall (driving) temperature under a film:
    T_aw,film = T_aw - eta_f*(T_aw - T_film), eta_f = 1 - phi. Scalar or
    per-station array - the throat line in design.py is this at the throat."""
    eta_f = np.maximum(0.0, 1.0 - np.asarray(phi, dtype=float))
    out = t_aw_k - eta_f * (t_aw_k - t_film_k)
    return float(out) if np.ndim(out) == 0 else out


# --- coolant-side channel model (regenerative jackets only) ------------------
# A 1-D counterflow coolant march: the fuel enters the jacket at the nozzle
# cooling-transition point and flows UP toward the injector, picking up the
# gas-side heat flux station by station. It gives (1) a coolant-side wall
# temperature via a series-resistance solve against the already-computed
# gas-side flux, and (2) a real jacket pressure drop (Darcy-Weisbach) that
# REPLACES the flat design.JACKET_DP_PA constant.
#
# Same honesty tier as BARTZ_SIGMA / materials.cooling_effectiveness: the
# relations (Dittus-Boelter, Darcy-Weisbach via Haaland, series resistance) are
# textbook; the channel-geometry defaults and the single CHANNEL_DP_CALIBRATION
# scalar are calibrated so the reference regen design (EngineDesign(
# cycle="gas_generator") defaults - LOX/RP-1, Pc 8 MPa, CR 1.6, narloy_z, auto
# channels) reproduces ~1.6 MPa jacket dP, the tool's long-standing flat value.
# That is a neutral-default contract: nothing already validated moves unless the
# user changes channel geometry or selects regen_channel_model="channels".
# Channel COUNT scales with engine size, not a fixed pitch: real regen jackets
# hold the channel count roughly constant (~150-400 - F-1 ~178, SSME ~390, RL10
# ~180) and grow the channel cross-section with the engine, so the throat
# coolant velocity - and hence the jacket dP - stays roughly scale-invariant.
CHANNEL_PITCH_FRACTION = 0.014         # throat channel pitch as a fraction of throat dia
                                       # -> n_channels ~ pi/0.014 ~ 224, near-constant
CHANNEL_PITCH_MIN_M = 1.2e-3           # floor for a tiny throat
CHANNEL_PITCH_MAX_M = 9.0e-3           # ceiling for a very large throat
CHANNEL_LAND_FRACTION_DEFAULT = 0.35   # fraction of the pitch taken by the rib (land) between channels
CHANNEL_ROUGHNESS_M = 6.0e-6          # milled / EDM channel wall
CHANNEL_MIN_COUNT = 40
# Target THROAT coolant velocity, per pair - the channel height is sized to hit
# this (aspect ratio is then an output, unless the user overrides it). Real
# regen practice: kerosene ~30-45 m/s, LH2 much faster, methane in between.
TARGET_COOLANT_VELOCITY_MS = {
    "LOX/RP-1": 35.0,
    "LOX/LH2": 95.0,
    "LOX/CH4": 45.0,
    "N2O4/MMH": 28.0,
}
_TARGET_COOLANT_VELOCITY_FALLBACK = 35.0
CHANNEL_ASPECT_RATIO_MAX = 8.0         # cap on the derived height/width
DITTUS_BOELTER_C = 0.023
DITTUS_BOELTER_M = 0.8
DITTUS_BOELTER_N = 0.4                 # heating (coolant colder than wall)
CHANNEL_DP_CALIBRATION = 0.93          # single free multiplier on the summed straight-channel
                                       # Darcy dP - folds together the manifold entry/exit and
                                       # throat U-turn losses this 1-D single-pass march omits
                                       # AND the fact that a real jacket is not one perfectly
                                       # straight tube. Tuned so the reference regen design
                                       # (see module docstring) lands at ~1.6 MPa - the tool's
                                       # long-standing flat JACKET_DP_PA. Same trust tier as
                                       # BARTZ_SIGMA; pinned by validate.py's cooling check.

# --- jacket wall construction ------------------------------------------------
# The cooled wall can be built three ways, each with its own coolant-side heat
# transfer, jacket pressure drop and structural mass. "milled_channel" is the
# reference (the channel model above is calibrated to it: SSME MCC-class slotted
# liner). Multipliers are Tier 3 - the DIRECTION is solid (a brazed tube bundle
# runs a bit hotter and heavier than milled channels; a single coax annulus is
# gentler on dP but the worst heat-transfer and the heaviest structure), the
# magnitudes are engineering estimates.
#   milled_channel : SSME / RS-25 main chamber (reference, all factors 1.0)
#   tube_wall      : F-1, J-2, RL10 - brazed formed-tube bundle + outer jacket
#   coax_shell     : V-2, early Atlas - one annular gap between two shells
WALL_CONSTRUCTIONS = ("milled_channel", "tube_wall", "coax_shell")
H_C_CONSTRUCTION_FACTOR = {            # multiplies the Dittus-Boelter coolant-side h_c
    "milled_channel": 1.00,
    "tube_wall": 0.85,                 # round tubes: lower wetted-perimeter efficiency
    "coax_shell": 0.55,               # one low-velocity annular passage
}
DP_CONSTRUCTION_FACTOR = {            # multiplies the summed jacket Darcy dP
    "milled_channel": 1.00,
    "tube_wall": 1.15,               # extra tube bends / return manifold
    "coax_shell": 0.50,             # one big annulus, low velocity
}
JACKET_MASS_CONSTRUCTION_FACTOR = {   # extra structural mass vs the bare hoop-stress shell
    "milled_channel": 1.00,           # already what shell_mass_kg captures
    "tube_wall": 1.20,               # braze-filled tube bundle + structural jacket
    "coax_shell": 1.35,             # full structural outer shell
}

# Per-pair coolant (fuel) transport at jacket conditions: (conductivity W/m-K,
# dynamic viscosity Pa.s). Representative liquid / supercritical values; cp and
# density come from FUEL_CP_J_KGK / COOLANT_DENSITY_KG_M3 below.
COOLANT_TRANSPORT = {
    "LOX/RP-1": (0.13, 7.5e-4),
    "LOX/LH2":  (0.10, 1.3e-5),
    "LOX/CH4":  (0.19, 1.1e-4),
    "N2O4/MMH": (0.20, 5.8e-4),
}
COOLANT_DENSITY_KG_M3 = {              # fuel density in the jacket (kept local to avoid
    "LOX/RP-1": 810.0,                 # importing combustion.py from here)
    "LOX/LH2": 71.0,
    "LOX/CH4": 422.0,
    "N2O4/MMH": 880.0,
}
_COOLANT_TRANSPORT_FALLBACK = (0.15, 5.0e-4)
_COOLANT_DENSITY_FALLBACK = 800.0


def channel_count(throat_dia_m, override=0):
    """Number of coolant channels around the circumference. Auto: from a
    throat-diameter-scaled pitch, so the count comes out roughly constant
    (~200-250) across engine sizes, matching real practice."""
    if override and override > 0:
        return int(override)
    if throat_dia_m <= 0:
        return CHANNEL_MIN_COUNT
    pitch = min(CHANNEL_PITCH_MAX_M,
                max(CHANNEL_PITCH_MIN_M, CHANNEL_PITCH_FRACTION * throat_dia_m))
    return max(CHANNEL_MIN_COUNT, round(math.pi * throat_dia_m / pitch))


def channel_target_height_m(throat_dia_m, n_channels, mdot_coolant_kgs, pair,
                             land_fraction, aspect_ratio_override=0.0,
                             target_velocity_ms=0.0):
    """Channel height that makes the THROAT coolant velocity equal
    TARGET_COOLANT_VELOCITY_MS (so jacket dP is scale-invariant), unless the
    user pins an aspect ratio. `target_velocity_ms>0` replaces the per-pair
    target (EngineDesign.regen_coolant_velocity_ms). Returns (height_m,
    throat_width_m)."""
    pitch = math.pi * throat_dia_m / n_channels if n_channels > 0 else throat_dia_m
    width = max(1e-5, pitch * (1.0 - land_fraction))
    if aspect_ratio_override and aspect_ratio_override > 0:
        return width * aspect_ratio_override, width
    rho = COOLANT_DENSITY_KG_M3.get(pair, _COOLANT_DENSITY_FALLBACK)
    v_target = (target_velocity_ms if target_velocity_ms and target_velocity_ms > 0
                else TARGET_COOLANT_VELOCITY_MS.get(pair, _TARGET_COOLANT_VELOCITY_FALLBACK))
    total_area_needed = mdot_coolant_kgs / (rho * v_target) if rho > 0 and v_target > 0 else 0.0
    height = total_area_needed / (n_channels * width) if n_channels > 0 and width > 0 else width
    height = min(height, width * CHANNEL_ASPECT_RATIO_MAX)
    return max(height, width * 0.5), width


def channel_count_at_station(n_channels_base, local_eps, split_eps):
    """Real F-1-style channel-COUNT doubling (e.g. 178->356) once the contour
    reaches `split_eps` area ratio, keeping per-channel width from growing
    unbounded as circumference increases downstream of the split. Matches
    `EngineDesign.tube_split_eps` - previously a 3D-preview-only rendering
    field (gui/preview3d_gl.py/preview3d_gl_core.py), now also real physics
    via march_coolant()/channel_geometry_profile() below.
    `split_eps<=0` (the default) means no split - unchanged prior behavior,
    a single channel count for the whole march."""
    if split_eps and split_eps > 0 and local_eps >= split_eps:
        return 2 * n_channels_base
    return n_channels_base


def channel_hydraulic_geometry(local_dia_m, n_channels, channel_height_m, land_fraction):
    """Per-station channel width/height/flow-area/hydraulic-diameter for
    `n_channels` rectangular channels of fixed height `channel_height_m` wrapped
    around a wall of `local_dia_m` (channels widen as the circumference grows)."""
    if local_dia_m <= 0 or n_channels <= 0:
        return dict(width_m=0.0, height_m=0.0, area_m2=0.0, dh_m=0.0, total_area_m2=0.0)
    pitch = math.pi * local_dia_m / n_channels
    width = max(1e-5, pitch * (1.0 - land_fraction))
    height = max(1e-5, channel_height_m)
    area = width * height
    perim = 2.0 * (width + height)
    dh = 4.0 * area / perim if perim > 0 else 0.0
    return dict(width_m=width, height_m=height, area_m2=area, dh_m=dh,
                total_area_m2=area * n_channels)


def passage_velocity_ms(local_dia_m, throat_dia_m, mdot_coolant_kgs, pair, *,
                        n_channels=0, aspect_ratio=0.0, land_fraction=0.0, split_eps=0.0,
                        target_velocity_ms=0.0):
    """Bulk coolant velocity in the jacket passages at a station of wall
    diameter `local_dia_m`: V = mdot / (rho * total passage flow area) - the
    exact expression march_coolant() uses per segment, but as a pure function
    of the same channel-sizing relations (channel_count /
    channel_target_height_m / channel_count_at_station /
    channel_hydraulic_geometry), so it is available in BOTH regen channel
    models ("flat" never runs the march). Used to size the regen-jacket
    manifold rings off the passages they feed: SP-8087's constant-velocity
    torus theory gives every passage the same inlet velocity [SP-8087
    Sec.2.1.2.1 p.19-20], and Fagherazzi's supply-volute design explicitly
    avoids abrupt velocity changes between the volute and the channels
    [Fagherazzi, see claude_lit/sources/fagherazzi-regen-cooling-thesis.md]."""
    if local_dia_m <= 0 or throat_dia_m <= 0 or mdot_coolant_kgs <= 0:
        return 0.0
    n_ch = channel_count(throat_dia_m, n_channels)
    lf = land_fraction if land_fraction and land_fraction > 0 else CHANNEL_LAND_FRACTION_DEFAULT
    height, _ = channel_target_height_m(throat_dia_m, n_ch, mdot_coolant_kgs, pair, lf,
                                        aspect_ratio_override=aspect_ratio,
                                        target_velocity_ms=target_velocity_ms)
    n_station = (channel_count_at_station(n_ch, _local_area_ratio(local_dia_m / 2.0,
                                                                  throat_dia_m / 2.0), split_eps)
                 if split_eps and split_eps > 0 else n_ch)
    g = channel_hydraulic_geometry(local_dia_m, n_station, height, lf)
    rho = COOLANT_DENSITY_KG_M3.get(pair, _COOLANT_DENSITY_FALLBACK)
    if g["total_area_m2"] <= 0 or rho <= 0:
        return 0.0
    return mdot_coolant_kgs / (rho * g["total_area_m2"])


def channel_geometry_profile(xs_m, rs_m, n_channels, channel_height_m, land_fraction,
                              throat_dia_m=0.0, split_eps=0.0):
    """Per-station channel/tube width/height/hydraulic-diameter across the
    WHOLE contour, for the 3D preview's rib pattern only - a separate,
    additive wrapper around channel_hydraulic_geometry(). Unlike
    march_coolant() (which restricts itself to the actively-cooled segments,
    in coolant-flow order, and feeds jacket dP / coolant temperature rise),
    this covers every station in xs_m/rs_m and feeds no lumped physics
    number - march_coolant's own internal per-station calls and outputs are
    untouched by this function's existence.

    `throat_dia_m`/`split_eps`: when both given, channel COUNT doubles past
    `split_eps` area ratio (channel_count_at_station) - matches the real
    channel count march_coolant() now uses, so the rendered rib pattern and
    the actual flow physics agree. `throat_dia_m<=0` (the default) skips the
    area-ratio computation entirely and reproduces the prior no-split
    behavior exactly."""
    xs_m = np.asarray(xs_m, dtype=float)
    rs_m = np.asarray(rs_m, dtype=float)
    n = rs_m.size
    width_m = np.zeros(n)
    height_m = np.zeros(n)
    dh_m = np.zeros(n)
    area_m2 = np.zeros(n)
    n_station_arr = np.zeros(n, dtype=int)
    total_area_m2 = np.zeros(n)
    rt = throat_dia_m / 2.0 if throat_dia_m > 0 else 0.0
    for i, r in enumerate(rs_m):
        n_ch_station = n_channels
        if rt > 0 and split_eps and split_eps > 0:
            n_ch_station = channel_count_at_station(
                n_channels, _local_area_ratio(r, rt), split_eps)
        g = channel_hydraulic_geometry(2.0 * r, n_ch_station, channel_height_m, land_fraction)
        width_m[i] = g["width_m"]
        height_m[i] = g["height_m"]
        dh_m[i] = g["dh_m"]
        area_m2[i] = g["area_m2"]
        n_station_arr[i] = n_ch_station
        total_area_m2[i] = g["total_area_m2"]
    return dict(width_m=width_m, height_m=height_m, dh_m=dh_m, area_m2=area_m2,
                n_channels_station=n_station_arr, total_area_m2=total_area_m2)


def coolant_side_htc(mdot_coolant_kgs, total_area_m2, dh_m, pair,
                     construction="milled_channel"):
    """Coolant-side convective coefficient h_c [W/m^2/K] and channel Reynolds
    number from the Dittus-Boelter correlation Nu = 0.023 Re^0.8 Pr^0.4, scaled
    by the wall-construction factor (milled_channel = 1.0 reference)."""
    k, mu = COOLANT_TRANSPORT.get(pair, _COOLANT_TRANSPORT_FALLBACK)
    cp = FUEL_CP_J_KGK.get(pair, 2100.0)
    if total_area_m2 <= 0 or dh_m <= 0 or mu <= 0 or k <= 0:
        return 0.0, 0.0
    g_flux = mdot_coolant_kgs / total_area_m2          # coolant mass flux [kg/m^2/s]
    re = g_flux * dh_m / mu
    pr = mu * cp / k
    nu = DITTUS_BOELTER_C * re ** DITTUS_BOELTER_M * pr ** DITTUS_BOELTER_N
    h_c = nu * k / dh_m * H_C_CONSTRUCTION_FACTOR.get(construction, 1.0)
    return h_c, re


def _darcy_friction(re, dh_m, roughness_m=None):
    """Darcy friction factor: laminar 64/Re below Re 2300, else Haaland.
    `roughness_m` defaults to the milled-channel CHANNEL_ROUGHNESS_M
    (physics/plumbing.py passes its own drawn-tubing value)."""
    if re < 1.0:
        return 0.02
    if re < 2300.0:
        return 64.0 / re
    rough = CHANNEL_ROUGHNESS_M if roughness_m is None else roughness_m
    eps_rel = rough / dh_m if dh_m > 0 else 0.0
    inv_sqrt_f = -1.8 * math.log10((eps_rel / 3.7) ** 1.11 + 6.9 / re)
    return 1.0 / inv_sqrt_f ** 2 if inv_sqrt_f != 0 else 0.02


def coupled_wall_temps(q_w_m2, h_g_w_m2k, t_aw_k, h_c_w_m2k, t_coolant_k,
                       t_wall_m, k_wall_w_mk):
    """1-D series-resistance wall solve given the gas-side flux `q_w_m2`:
        T_wc = T_coolant + q / h_c            (coolant-side wall)
        T_wg = T_wc + q * t_wall / k_wall     (hot-gas-side wall)
    Returns (t_wg_k, t_wc_k). h_g / t_aw are accepted for callers that want the
    gas-side cross-check T_aw - q/h_g."""
    t_wc = t_coolant_k + (q_w_m2 / h_c_w_m2k if h_c_w_m2k > 0 else 0.0)
    cond = q_w_m2 * t_wall_m / k_wall_w_mk if k_wall_w_mk > 0 else 0.0
    return t_wc + cond, t_wc


# Gas-side carbon-deposit (soot) knockdown on the raw Bartz h_g, applied ONLY in
# the coupled wall balance below (solve_wall_balance), never to the flux
# profile. [TP2862-LOXRP1] measured LOX/RP-1 h_g ~40% (UMR injector, Pc 4.3 MPa)
# to ~60% (zoned injector, Pc 13.8 MPa) below the soot-free calculated value;
# 0.5 is the mid-band. Why only here: absolute_heat_flux_profile's per-class
# calibration was fitted to real engines' integrated wall heat (which already
# carried their deposits), while bartz_hg is the raw clean-wall correlation.
# Cross-check: without it a coupled solve melts the real F-1's Inconel tubes;
# with 0.4-0.6 it survives (validate.py run_coupled_wall_temperature_check).
# Tier 2 - cited range, midpoint chosen. Pairs not listed get 1.0 (no credit).
GAS_SIDE_DEPOSIT_FACTOR = {
    "LOX/RP-1": 0.5,
}


def solve_wall_balance(h_g_w_m2k, t_aw_k, h_c_w_m2k, t_bulk_k, t_wall_m, k_wall_w_mk):
    """
    Steady 1-D series-resistance balance through gas film, wall and coolant film
    [Huzel eq. 4-10; EUCASS-2023 Eq.1]:
        q = h_g (T_aw - T_wg) = (k/t)(T_wg - T_wc) = h_c (T_wc - T_bulk)
    solved in closed form with U = 1/(1/h_c + t/k):
        T_wg = (h_g T_aw + U T_bulk) / (h_g + U)
    Unlike coupled_wall_temps (which takes q as given), the flux here is an
    OUTPUT - the wall temperature responds to coolant h_c, wall thickness and
    conductivity. Returns (t_wg_k, t_wc_k, q_w_m2).
    """
    r_cool = 1.0 / h_c_w_m2k if h_c_w_m2k > 0 else float("inf")
    r_wall = t_wall_m / k_wall_w_mk if k_wall_w_mk > 0 else 0.0
    u = 1.0 / (r_cool + r_wall) if (r_cool + r_wall) > 0 else float("inf")
    if h_g_w_m2k <= 0:
        return t_bulk_k, t_bulk_k, 0.0
    if math.isinf(u):
        return t_bulk_k, t_bulk_k, h_g_w_m2k * (t_aw_k - t_bulk_k)
    t_wg = (h_g_w_m2k * t_aw_k + u * t_bulk_k) / (h_g_w_m2k + u)
    q = h_g_w_m2k * (t_aw_k - t_wg)
    t_wc = t_bulk_k + (q / h_c_w_m2k if h_c_w_m2k > 0 else 0.0)
    return t_wg, t_wc, q


def solve_wall_balance_profile(h_g_w_m2k, t_aw_k, h_c_w_m2k, t_bulk_k, t_wall_m,
                               k_wall_w_mk):
    """
    solve_wall_balance at every station at once (the full-length coupled wall
    balance). Array inputs broadcast; a station with a non-finite or <= 0 h_c or
    h_g (outside the cooled length) returns NaN. Same closed form, so the throat
    station reproduces solve_wall_balance. Returns (t_wg_k, t_wc_k, q_w_m2).
    """
    hg = np.asarray(h_g_w_m2k, dtype=float)
    taw = np.asarray(t_aw_k, dtype=float)
    hc = np.asarray(h_c_w_m2k, dtype=float)
    tb = np.asarray(t_bulk_k, dtype=float)
    hg, taw, hc, tb = np.broadcast_arrays(hg, taw, hc, tb)
    ok = np.isfinite(hg) & np.isfinite(hc) & np.isfinite(tb) & (hg > 0) & (hc > 0)
    r_wall = t_wall_m / k_wall_w_mk if k_wall_w_mk > 0 else 0.0
    with np.errstate(divide="ignore", invalid="ignore"):
        u = 1.0 / (1.0 / hc + r_wall)
        t_wg = (hg * taw + u * tb) / (hg + u)
        q = hg * (taw - t_wg)
        t_wc = tb + q / hc
    nan = np.full(hg.shape, np.nan)
    return (np.where(ok, t_wg, nan), np.where(ok, t_wc, nan), np.where(ok, q, nan))


def _passage_v(mdot_kgs, rho, total_area_m2):
    """Bulk passage velocity mdot/(rho*A), 0 for a degenerate passage."""
    return mdot_kgs / (rho * total_area_m2) if rho > 0 and total_area_m2 > 0 else 0.0


def _segments_to_stations(seg_vals, n):
    """Map per-segment march values (length n-1, NaN = segment not cooled) onto
    the n contour stations: each station takes the mean of its cooled adjacent
    segments (NaN where neither is cooled)."""
    seg_vals = np.asarray(seg_vals, dtype=float)
    left = np.concatenate([[np.nan], seg_vals])     # segment ending at station j
    right = np.concatenate([seg_vals, [np.nan]])    # segment starting at station j
    both = np.vstack([left, right])
    cnt = np.sum(np.isfinite(both), axis=0)
    tot = np.nansum(both, axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(cnt > 0, tot / np.maximum(cnt, 1), np.nan)


def march_coolant(xs_m, rs_m, q_profile_w_m2, throat_dia_m, mdot_coolant_kgs, pair,
                  *, n_channels=0, aspect_ratio=0.0, land_fraction=0.0,
                  transition_area_ratio=None, t_inlet_k=None,
                  construction="milled_channel", split_eps=0.0,
                  target_velocity_ms=0.0):
    """
    Counterflow 1-D coolant march over the actively-cooled contour (injector face
    through the throat and out to `transition_area_ratio`). The coolant enters at
    the nozzle (transition) end and flows toward the injector.

    Returns dict(coolant_exit_t_k, coolant_delta_t_k, jacket_dp_pa, n_channels,
    channel_dh_throat_m, t_wc_throat_k) - `t_wc_throat_k` is the coolant-side
    wall temperature at the throat (bulk coolant temp there + the convective film
    rise q/h_c), the number physics/design.py adds the through-wall gradient to.

    `split_eps>0`: channel COUNT doubles past that area ratio
    (channel_count_at_station - real F-1-style practice), changing per-segment
    flow area hence h_c/Re/dP downstream of the split station. `n_channels` in
    the returned dict stays the BASE (pre-split) count, unchanged in meaning.
    Default 0.0 reproduces the prior single-count-throughout behavior exactly.
    """
    xs = np.asarray(xs_m, dtype=float)
    rs = np.asarray(rs_m, dtype=float)
    q = np.asarray(q_profile_w_m2, dtype=float)
    rt = throat_dia_m / 2.0
    throat_idx = int(np.argmin(rs))
    n_ch = channel_count(throat_dia_m, n_channels)
    lf = land_fraction if land_fraction and land_fraction > 0 else CHANNEL_LAND_FRACTION_DEFAULT
    # Fixed channel height, sized at the throat to hit the target coolant
    # velocity (or the user's aspect-ratio override). Channels then widen away
    # from the throat as the circumference grows.
    ch_height_m, _ = channel_target_height_m(throat_dia_m, n_ch, mdot_coolant_kgs,
                                              pair, lf, aspect_ratio_override=aspect_ratio,
                                              target_velocity_ms=target_velocity_ms)
    cp = FUEL_CP_J_KGK.get(pair, 2100.0)
    rho = COOLANT_DENSITY_KG_M3.get(pair, _COOLANT_DENSITY_FALLBACK)
    t_bulk = t_inlet_k if t_inlet_k is not None else 290.0

    # Segment indices upstream of the transition area ratio, in COOLANT-flow
    # order (from the nozzle/transition end toward the injector).
    seg = []
    for i in range(len(rs) - 1):
        if (transition_area_ratio is not None and i >= throat_idx
                and _local_area_ratio(max(rs[i], rs[i + 1]), rt) > transition_area_ratio):
            continue
        seg.append(i)
    seg_flow = list(reversed(seg))

    delta_t = 0.0
    dp_total = 0.0
    t_wc_throat = None
    dh_throat = 0.0
    throat_state = (t_bulk, 0.0, 0.0)
    h_c_seg = np.full(max(len(rs) - 1, 0), np.nan)    # per-segment, for the
    t_bulk_seg = np.full(max(len(rs) - 1, 0), np.nan)  # full-length wall balance
    for i in seg_flow:
        local_dia = rs[i] + rs[i + 1]
        n_ch_station = (channel_count_at_station(n_ch, _local_area_ratio(local_dia / 2.0, rt), split_eps)
                        if split_eps and split_eps > 0 else n_ch)
        g = channel_hydraulic_geometry(local_dia, n_ch_station, ch_height_m, lf)
        a_seg = _frustum_area(xs[i], rs[i], xs[i + 1], rs[i + 1])
        q_seg = 0.5 * (q[i] + q[i + 1])
        h_c, re = coolant_side_htc(mdot_coolant_kgs, g["total_area_m2"], g["dh_m"], pair,
                                   construction=construction)

        d_t = (q_seg * a_seg / (mdot_coolant_kgs * cp)
               if mdot_coolant_kgs > 0 and cp > 0 else 0.0)
        t_bulk += d_t
        delta_t += d_t

        t_wc = t_bulk + (q_seg / h_c if h_c > 0 else 0.0)
        if abs(i - throat_idx) <= 1 and (t_wc_throat is None or t_wc > t_wc_throat):
            t_wc_throat = t_wc
            dh_throat = g["dh_m"]
            throat_state = (t_bulk, h_c, _passage_v(mdot_coolant_kgs, rho, g["total_area_m2"]))
        h_c_seg[i] = h_c
        t_bulk_seg[i] = t_bulk

        if g["total_area_m2"] > 0 and g["dh_m"] > 0 and rho > 0:
            v = mdot_coolant_kgs / (rho * g["total_area_m2"])
            length = math.hypot(xs[i + 1] - xs[i], rs[i + 1] - rs[i])
            f = _darcy_friction(re, g["dh_m"])
            dp_total += f * (length / g["dh_m"]) * 0.5 * rho * v * v

    dp_total *= CHANNEL_DP_CALIBRATION * DP_CONSTRUCTION_FACTOR.get(construction, 1.0)
    if t_wc_throat is None:
        t_wc_throat = t_bulk
    return dict(coolant_exit_t_k=t_bulk, coolant_delta_t_k=delta_t,
                jacket_dp_pa=dp_total, n_channels=n_ch,
                channel_dh_throat_m=dh_throat, t_wc_throat_k=t_wc_throat,
                t_bulk_throat_k=throat_state[0], h_c_throat_w_m2k=throat_state[1],
                v_throat_ms=throat_state[2],
                # per-STATION (NaN outside the cooled length) - additive, for
                # the full-length coupled wall balance
                h_c_profile_w_m2k=_segments_to_stations(h_c_seg, len(rs)),
                t_bulk_profile_k=_segments_to_stations(t_bulk_seg, len(rs)))


# Real J-2 regen circuit: "LH2 fuel from the fuel manifold circulated downward
# through 180 tubes, and back upward through 360 tubes to the thrust chamber
# injector" (literature/Rocket Propulsion Evolution_ 8.22 - J-2 Engine.html,
# thrust-chamber section; the cutaway there puts the fuel manifold partway down
# the nozzle). Tier 2 - one real engine's documented tube counts, informal
# (non-claude_lit) source. The F-1's 178 down / 356 return shares the same 1:2.
J2_DOWN_TO_UP_TUBE_RATIO = 0.5


def two_pass_tube_counts(throat_dia_m, n_channels=0):
    """(n_up, n_down) for the J-2-style two-pass circuit: the up (return)
    tubes run the full length and keep the single-pass channel_count - so the
    throat, which only up-tubes cross, is sized exactly as today - and the
    down tubes are J2_DOWN_TO_UP_TUBE_RATIO of them, sharing the circumference
    only downstream of the mid-nozzle inlet."""
    n_up = channel_count(throat_dia_m, n_channels)
    return n_up, max(1, round(n_up * J2_DOWN_TO_UP_TUBE_RATIO))


def down_pass_velocity_ms(local_dia_m, throat_dia_m, mdot_coolant_kgs, pair, *,
                          n_channels=0, aspect_ratio=0.0, land_fraction=0.0,
                          target_velocity_ms=0.0):
    """Bulk coolant velocity in the DOWN tubes of the two-pass circuit at a
    station of wall diameter `local_dia_m` in the shared (down+up) region -
    pure, like passage_velocity_ms, so the mid-nozzle jacket-inlet ring can be
    sized off it in either regen channel model. Down and up tubes share the
    circumference (width = pi*D/(n_up+n_down)), so the down pass runs
    (n_up+n_down)/n_down = 3x faster than a single-pass jacket at the same
    station would."""
    if local_dia_m <= 0 or throat_dia_m <= 0 or mdot_coolant_kgs <= 0:
        return 0.0
    n_up, n_down = two_pass_tube_counts(throat_dia_m, n_channels)
    lf = land_fraction if land_fraction and land_fraction > 0 else CHANNEL_LAND_FRACTION_DEFAULT
    height, _ = channel_target_height_m(throat_dia_m, n_up, mdot_coolant_kgs, pair, lf,
                                        aspect_ratio_override=aspect_ratio,
                                        target_velocity_ms=target_velocity_ms)
    g = channel_hydraulic_geometry(local_dia_m, n_up + n_down, height, lf)
    rho = COOLANT_DENSITY_KG_M3.get(pair, _COOLANT_DENSITY_FALLBACK)
    area_down = g["area_m2"] * n_down
    return mdot_coolant_kgs / (rho * area_down) if area_down > 0 and rho > 0 else 0.0


def march_coolant_two_pass(xs_m, rs_m, q_profile_w_m2, throat_dia_m, mdot_coolant_kgs, pair,
                           *, inlet_area_ratio, n_channels=0, aspect_ratio=0.0,
                           land_fraction=0.0, transition_area_ratio=None, t_inlet_k=None,
                           construction="milled_channel", target_velocity_ms=0.0):
    """
    J-2-style two-pass regen march (EngineDesign.cooling_flow_topology =
    "j2_mid_nozzle_inlet"): the coolant enters a manifold partway down the
    nozzle at `inlet_area_ratio`, flows DOWN n_down tubes to the cooled end
    (`transition_area_ratio`), turns around, and flows back UP n_up tubes over
    the whole cooled length to the injector (two_pass_tube_counts).

    Between the inlet and the cooled end both tube sets share the
    circumference (width = pi*D/(n_up+n_down), the same fixed height
    march_coolant uses) and split that segment's wall heat by circumference
    share; upstream of the inlet only the up tubes exist, exactly as in
    march_coolant. The down pass is marched first (from the inlet toward the
    exit), its outlet temperature carries through the turnaround into the up
    pass (exit -> injector). Per-pass Darcy dP uses the same Haaland friction
    and the same CHANNEL_DP_CALIBRATION x DP_CONSTRUCTION_FACTOR as
    march_coolant - no new calibration constant.

    Invariants (self-tested): an inlet at/after the cooled end (zero-length
    down pass) reproduces march_coolant (split_eps=0) exactly; the TOTAL
    coolant temperature rise equals march_coolant's for any inlet (same wall
    heat into the same mdot*cp); jacket dP grows with the down-pass length.

    Returns march_coolant's keys plus jacket_dp_down_pa, coolant_turnaround_t_k,
    down_pass_inlet_velocity_ms and n_channels_down.
    """
    xs = np.asarray(xs_m, dtype=float)
    rs = np.asarray(rs_m, dtype=float)
    q = np.asarray(q_profile_w_m2, dtype=float)
    rt = throat_dia_m / 2.0
    throat_idx = int(np.argmin(rs))
    n_up, n_down = two_pass_tube_counts(throat_dia_m, n_channels)
    n_tot = n_up + n_down
    lf = land_fraction if land_fraction and land_fraction > 0 else CHANNEL_LAND_FRACTION_DEFAULT
    ch_height_m, _ = channel_target_height_m(throat_dia_m, n_up, mdot_coolant_kgs,
                                              pair, lf, aspect_ratio_override=aspect_ratio,
                                              target_velocity_ms=target_velocity_ms)
    cp = FUEL_CP_J_KGK.get(pair, 2100.0)
    rho = COOLANT_DENSITY_KG_M3.get(pair, _COOLANT_DENSITY_FALLBACK)
    t0 = t_inlet_k if t_inlet_k is not None else 290.0

    seg = []
    for i in range(len(rs) - 1):
        if (transition_area_ratio is not None and i >= throat_idx
                and _local_area_ratio(max(rs[i], rs[i + 1]), rt) > transition_area_ratio):
            continue
        seg.append(i)

    # Per-segment split at the inlet station: the segment containing it is
    # divided into an up-only part (upstream) and a shared part (downstream),
    # by LENGTH for friction and by frustum AREA for heat, so the inlet is
    # resolved at any contour resolution (a conical contour's one throat->exit
    # segment included) and the total wall heat is exactly conserved.
    # (length_frac_shared, area_frac_shared, up-only mean dia, shared mean dia)
    r_inlet = rt * math.sqrt(max(inlet_area_ratio, 1.0))

    def _split(i):
        r0, r1 = rs[i], rs[i + 1]
        mean_dia = r0 + r1
        if i < throat_idx or max(r0, r1) <= r_inlet:
            return 0.0, 0.0, mean_dia, mean_dia
        if min(r0, r1) >= r_inlet or r1 <= r0:
            return 1.0, 1.0, mean_dia, mean_dia
        t = (r_inlet - r0) / (r1 - r0)            # r is linear along the segment
        return 1.0 - t, (r_inlet + r1) * (1.0 - t) / (r0 + r1), r0 + r_inlet, r_inlet + r1

    def _dp(mdot, area, dh, re, length):
        if area <= 0 or dh <= 0 or rho <= 0:
            return 0.0
        v = mdot / (rho * area)
        return _darcy_friction(re, dh) * (length / dh) * 0.5 * rho * v * v

    dp_scale = CHANNEL_DP_CALIBRATION * DP_CONSTRUCTION_FACTOR.get(construction, 1.0)
    heat_to = (1.0 / (mdot_coolant_kgs * cp)) if mdot_coolant_kgs > 0 and cp > 0 else 0.0

    # --- down pass: inlet -> cooled end (increasing x), shared parts only.
    t_bulk = t0
    dp_down = 0.0
    v_down_inlet = 0.0
    for i in seg:
        f_len, f_area, _, dia_sh = _split(i)
        if f_len <= 0.0:
            continue
        g = channel_hydraulic_geometry(dia_sh, n_tot, ch_height_m, lf)
        area = g["area_m2"] * n_down
        if v_down_inlet == 0.0 and area > 0 and rho > 0:
            v_down_inlet = mdot_coolant_kgs / (rho * area)
        a_seg = _frustum_area(xs[i], rs[i], xs[i + 1], rs[i + 1])
        q_seg = 0.5 * (q[i] + q[i + 1])
        _, re = coolant_side_htc(mdot_coolant_kgs, area, g["dh_m"], pair,
                                 construction=construction)
        t_bulk += q_seg * a_seg * f_area * (n_down / n_tot) * heat_to
        dp_down += _dp(mdot_coolant_kgs, area, g["dh_m"], re,
                       f_len * math.hypot(xs[i + 1] - xs[i], rs[i + 1] - rs[i]))
    t_turn = t_bulk

    # --- up pass: cooled end -> injector; within a split segment the coolant
    # meets the shared (downstream) part first, then the up-only part.
    dp_up = 0.0
    t_wc_throat = None
    dh_throat = 0.0
    throat_state = (t_bulk, 0.0, 0.0)
    # Per-segment UP-pass state (the tubes that cross the throat and carry the
    # warmer, returning coolant - the conservative wall in the shared region).
    h_c_seg = np.full(max(len(rs) - 1, 0), np.nan)
    t_bulk_seg = np.full(max(len(rs) - 1, 0), np.nan)
    for i in reversed(seg):
        f_len, f_area, dia_up, dia_sh = _split(i)
        a_seg = _frustum_area(xs[i], rs[i], xs[i + 1], rs[i + 1])
        q_seg = 0.5 * (q[i] + q[i + 1])
        seg_len = math.hypot(xs[i + 1] - xs[i], rs[i + 1] - rs[i])
        parts = []
        if f_len > 0.0:
            g = channel_hydraulic_geometry(dia_sh, n_tot, ch_height_m, lf)
            parts.append((g, g["area_m2"] * n_up, f_area * n_up / n_tot, f_len))
        if f_len < 1.0:
            g = channel_hydraulic_geometry(dia_up, n_up, ch_height_m, lf)
            parts.append((g, g["total_area_m2"], 1.0 - f_area, 1.0 - f_len))
        for g, area, heat_share, len_share in parts:
            h_c, re = coolant_side_htc(mdot_coolant_kgs, area, g["dh_m"], pair,
                                       construction=construction)
            t_bulk += q_seg * a_seg * heat_share * heat_to
            t_wc = t_bulk + (q_seg / h_c if h_c > 0 else 0.0)
            h_c_seg[i] = h_c
            t_bulk_seg[i] = t_bulk
            if abs(i - throat_idx) <= 1 and (t_wc_throat is None or t_wc > t_wc_throat):
                t_wc_throat = t_wc
                dh_throat = g["dh_m"]
                throat_state = (t_bulk, h_c, _passage_v(mdot_coolant_kgs, rho, area))
            dp_up += _dp(mdot_coolant_kgs, area, g["dh_m"], re, len_share * seg_len)

    if t_wc_throat is None:
        t_wc_throat = t_bulk
    return dict(coolant_exit_t_k=t_bulk, coolant_delta_t_k=t_bulk - t0,
                jacket_dp_pa=(dp_down + dp_up) * dp_scale, n_channels=n_up,
                channel_dh_throat_m=dh_throat, t_wc_throat_k=t_wc_throat,
                jacket_dp_down_pa=dp_down * dp_scale, coolant_turnaround_t_k=t_turn,
                down_pass_inlet_velocity_ms=v_down_inlet, n_channels_down=n_down,
                t_bulk_throat_k=throat_state[0], h_c_throat_w_m2k=throat_state[1],
                v_throat_ms=throat_state[2],
                h_c_profile_w_m2k=_segments_to_stations(h_c_seg, len(rs)),
                t_bulk_profile_k=_segments_to_stations(t_bulk_seg, len(rs)))


if __name__ == "__main__":
    # Headless unit smoke test - no matplotlib, no display.
    xs = np.array([0.0, 0.20, 0.32, 0.90])          # injector - chamber end - throat - exit
    rs = np.array([0.10, 0.10, 0.04, 0.15])
    dt_dia = 0.08

    q = heat_flux_profile(xs, rs, dt_dia, pc_pa=7.0e6)
    assert int(q.argmax()) == 2, f"peak flux should be at the throat, got index {q.argmax()}"
    assert q[0] < q[1], "injector-face taper should make x=0 the coolest chamber station"

    q_avg = reference_area_avg_flux_w_m2(7.0e6)
    total = wall_heat_total_w(xs, rs, q)
    assert total > 0.0
    dt = coolant_temp_rise_k(total, 20.0, FUEL_CP_J_KGK["LOX/RP-1"])
    assert dt > 0.0
    assert regen_feasible(50.0, "LOX/LH2") and not regen_feasible(600.0, "LOX/RP-1")

    # Anchor identity: mean flux over the cooled zone == the expander anchor.
    from_profile_mean = total / sum(
        _frustum_area(xs[i], rs[i], xs[i + 1], rs[i + 1]) for i in range(len(xs) - 1))
    assert abs(from_profile_mean - q_avg) / q_avg < 1e-6, (from_profile_mean, q_avg)

    # --- fuel-film curtain: length-decaying flux multiplier -------------------
    assert np.array_equal(film_effectiveness_profile(xs, rs, dt_dia, 0.0), np.ones(len(xs)))
    phi_lo = film_effectiveness_profile(xs, rs, dt_dia, 0.02)
    phi_hi = film_effectiveness_profile(xs, rs, dt_dia, 0.12)
    assert phi_hi[0] < phi_lo[0] < 1.0                    # more film -> more protection at the face
    assert (phi_hi[0] < phi_hi[-1] <= 1.0 + 1e-9)        # curtain decays downstream
    assert float(np.min(phi_hi)) >= FILM_FLUX_FLOOR - 1e-9
    m_lo = area_weighted_mean(xs, rs, phi_lo)
    m_hi = area_weighted_mean(xs, rs, phi_hi)
    assert 0.8 < m_lo < 1.0 and m_hi < m_lo               # 2% is gentle, 12% stronger
    # downstream-slot injection: no protection upstream of the slot
    phi_slot = film_effectiveness_profile(xs, rs, dt_dia, 0.10, inject_area_ratio=1.5)
    assert phi_slot[0] == 1.0 and float(np.min(phi_slot)) < 1.0

    # --- nozzle-extension film slot + combination + film T_aw ----------------
    # test contour: throat r 0.04 at index 2, exit r 0.15 (eps ~14) at index 3.
    assert np.array_equal(nozzle_film_effectiveness_profile(xs, rs, dt_dia, 0.0, 10.0),
                          np.ones(len(xs)))
    assert np.array_equal(nozzle_film_effectiveness_profile(xs, rs, dt_dia, 0.1, 50.0),
                          np.ones(len(xs)))                 # slot beyond the exit -> off
    phi_n = nozzle_film_effectiveness_profile(xs, rs, dt_dia, 0.10, 10.0)
    assert np.all(phi_n[:3] == 1.0) and phi_n[3] < 1.0     # only downstream of the slot
    _fx = np.linspace(0.0, 1.0, 60)                        # finer bell: phi recovers downstream
    _fr = np.where(_fx < 0.3, 0.10, np.where(_fx < 0.4, 0.10 - 0.6 * (_fx - 0.3),
                                              0.04 + 0.25 * (_fx - 0.4)))
    _pn = nozzle_film_effectiveness_profile(_fx, _fr, 0.08, 0.08, 8.0)
    _i0 = int(np.argmax(_pn < 1.0))
    assert _i0 > int(np.argmin(_fr)) and np.all(np.diff(_pn[_i0:]) >= -1e-12)
    _pc = film_effectiveness_profile(_fx, _fr, 0.08, 0.05)
    assert np.array_equal(combined_film_phi(_pc, np.ones_like(_pc)), _pc)
    assert np.all(combined_film_phi(_pc, _pn) <= _pc + 1e-12)
    assert float(np.min(combined_film_phi(_pc * 0 + 0.4, _pn * 0 + 0.4))) == FILM_FLUX_FLOOR
    assert film_adiabatic_wall_temp(3000.0, 1.0, 300.0) == 3000.0
    assert abs(film_adiabatic_wall_temp(3000.0, 0.6, 300.0) - (3000.0 - 0.4 * 2700.0)) < 1e-9

    # --- real Bartz h_g + computed wall temperature -------------------------
    # LOX/RP-1-class throat: Dt 0.9 m, Pc 7 MPa, c* 1720 m/s, mu 7.6e-5, cp 2100, Pr 0.77.
    hg_throat = bartz_hg(0.9, 7.0e6, 1720.0, 7.6e-5, 2100.0, 0.77, area_ratio=1.0)
    hg_up = bartz_hg(0.9, 7.0e6, 1720.0, 7.6e-5, 2100.0, 0.77, area_ratio=4.0)
    assert hg_throat > hg_up > 0.0, (hg_throat, hg_up)          # h_g peaks at the throat
    t_aw = recovery_temperature(3600.0)
    assert 3100.0 < t_aw < 3400.0, t_aw                         # r ~ 0.9
    q_throat_bartz = hg_throat * (t_aw - 800.0)                  # 800 K copper wall
    t_wg = wall_gas_temperature(q_throat_bartz, hg_throat, t_aw)
    assert abs(t_wg - 800.0) < 1.0, t_wg                        # inverts cleanly
    # Bartz throat flux and the conservative anchored profile peak agree to
    # within a small factor (the anchor is deliberately low; a real throat runs
    # several x its area-average).
    ratio = q_throat_bartz / q.max()
    assert 0.3 < ratio < 5.0, (q_throat_bartz / 1e6, q.max() / 1e6, ratio)

    # --- radiation-cooled nozzle-extension equilibrium ---------------------
    t_rad = radiative_wall_temperature(200.0, 2500.0, 0.85)
    assert 0.0 < t_rad < 2500.0
    convective = 200.0 * (2500.0 - t_rad)
    imbalance = convective - 0.85 * STEFAN_BOLTZMANN_W_M2K4 * t_rad ** 4
    assert abs(imbalance) / convective < 1e-3, (t_rad, imbalance, convective)  # balance solved

    # --- regen Isp credit -------------------------------------------------
    b_lo = regen_isp_bonus_fraction(5.0, "LOX/RP-1")
    b_hi = regen_isp_bonus_fraction(500.0, "LOX/RP-1")
    assert REGEN_ISP_BONUS_MIN <= b_lo < b_hi <= REGEN_ISP_BONUS_MAX
    assert regen_isp_bonus_fraction(100.0, "unknown/pair") == 0.0

    # --- coolant-side channel model -------------------------------------------
    # A representative regen contour: injector face -> chamber end -> throat -> exit.
    cx = np.array([0.0, 0.30, 0.45, 1.20])
    cr = np.array([0.14, 0.14, 0.055, 0.30])
    ct_dia = 0.11
    cq = heat_flux_profile(cx, cr, ct_dia, pc_pa=8.0e6, transition_area_ratio=6.0)

    n_lo = channel_count(ct_dia)
    n_hi = channel_count(0.9)                      # F-1-class throat
    assert n_lo >= CHANNEL_MIN_COUNT
    assert 100 <= n_lo <= 400 and 100 <= n_hi <= 500, (n_lo, n_hi)  # near-constant by design

    # channel_hydraulic_geometry: more channels at the same wall -> narrower
    # channels -> smaller Dh; coupled_wall_temps drops T_wg as h_c rises.
    g_few = channel_hydraulic_geometry(0.10, 60, 4.0e-3, 0.35)
    g_many = channel_hydraulic_geometry(0.10, 200, 4.0e-3, 0.35)
    assert 0.0 < g_many["dh_m"] < g_few["dh_m"]
    twg_lo_hc, twc_lo = coupled_wall_temps(20e6, 5e4, 3300.0, 3.0e4, 400.0, 1.5e-3, 325.0)
    twg_hi_hc, twc_hi = coupled_wall_temps(20e6, 5e4, 3300.0, 6.0e4, 400.0, 1.5e-3, 325.0)
    assert twg_hi_hc < twg_lo_hc and twc_hi < twc_lo   # higher h_c -> lower wall temps
    assert twg_lo_hc > twc_lo                          # hot face hotter than cold face

    # solve_wall_balance: the three fluxes agree, and the wall cools with higher
    # h_c, thinner wall, higher k, and lower h_g (deposit credit).
    twg, twc, qb = solve_wall_balance(7.0e3, 3100.0, 3.0e4, 350.0, 0.5e-3, 325.0)
    assert 350.0 < twc < twg < 3100.0
    assert abs(qb - 3.0e4 * (twc - 350.0)) / qb < 1e-9
    assert abs(qb - 325.0 / 0.5e-3 * (twg - twc)) / qb < 1e-9
    assert solve_wall_balance(7.0e3, 3100.0, 4.0e4, 350.0, 0.5e-3, 325.0)[0] < twg
    assert solve_wall_balance(7.0e3, 3100.0, 3.0e4, 350.0, 0.2e-3, 325.0)[0] < twg
    assert solve_wall_balance(7.0e3, 3100.0, 3.0e4, 350.0, 0.5e-3, 15.0)[0] > twg
    assert solve_wall_balance(3.5e3, 3100.0, 3.0e4, 350.0, 0.5e-3, 325.0)[0] < twg

    # march_coolant: sane outputs; the auto (velocity-targeted) geometry keeps
    # the coolant velocity - hence jacket dP - roughly scale-invariant, so a
    # bigger engine at the same duty comes out with a *similar* jacket dP, not a
    # runaway one.
    m1 = march_coolant(cx, cr, cq, ct_dia, 60.0, "LOX/RP-1", transition_area_ratio=6.0,
                       t_inlet_k=300.0)
    assert m1["coolant_exit_t_k"] > 300.0 and m1["coolant_delta_t_k"] > 0.0
    assert m1["t_wc_throat_k"] > m1["coolant_exit_t_k"] > 300.0
    assert 100 <= m1["n_channels"] <= 400
    # throat state: bulk temp between inlet and exit, and a user velocity override raises h_c (shallower channels).
    assert 300.0 < m1["t_bulk_throat_k"] < m1["coolant_exit_t_k"]
    assert m1["v_throat_ms"] > 0.0   # may undershoot the target when the height hits its AR floor
    m_fast = march_coolant(cx, cr, cq, ct_dia, 60.0, "LOX/RP-1", transition_area_ratio=6.0,
                           t_inlet_k=300.0, target_velocity_ms=55.0)
    assert m_fast["v_throat_ms"] > m1["v_throat_ms"]
    assert m_fast["h_c_throat_w_m2k"] > m1["h_c_throat_w_m2k"]
    assert m_fast["jacket_dp_pa"] > m1["jacket_dp_pa"]
    assert 0.5e-3 < m1["channel_dh_throat_m"] < 8e-3
    # coolant delta-T scales with total wall heat (double the flux -> ~double dT).
    cq2 = heat_flux_profile(cx, cr, ct_dia, pc_pa=8.0e6, transition_area_ratio=6.0) * 2.0
    m_hot = march_coolant(cx, cr, cq2, ct_dia, 60.0, "LOX/RP-1", transition_area_ratio=6.0,
                          t_inlet_k=300.0)
    assert 1.7 < m_hot["coolant_delta_t_k"] / m1["coolant_delta_t_k"] < 2.3
    # aspect-ratio override: wide shallow channels (low aspect) pack less flow
    # area -> higher coolant velocity -> higher jacket dP than deep narrow ones.
    m_shallow = march_coolant(cx, cr, cq, ct_dia, 60.0, "LOX/RP-1", aspect_ratio=2.0,
                              transition_area_ratio=6.0, t_inlet_k=300.0)
    m_deep = march_coolant(cx, cr, cq, ct_dia, 60.0, "LOX/RP-1", aspect_ratio=6.0,
                           transition_area_ratio=6.0, t_inlet_k=300.0)
    assert m_shallow["jacket_dp_pa"] > m_deep["jacket_dp_pa"] > 0.0

    # wall construction: milled_channel is the reference; a brazed tube wall runs
    # a hotter coolant-side throat (lower h_c) and a slightly higher jacket dP; a
    # coax shell is gentler on dP but hotter still.
    m_milled = march_coolant(cx, cr, cq, ct_dia, 60.0, "LOX/RP-1", transition_area_ratio=6.0,
                             t_inlet_k=300.0, construction="milled_channel")
    m_tube = march_coolant(cx, cr, cq, ct_dia, 60.0, "LOX/RP-1", transition_area_ratio=6.0,
                           t_inlet_k=300.0, construction="tube_wall")
    m_coax = march_coolant(cx, cr, cq, ct_dia, 60.0, "LOX/RP-1", transition_area_ratio=6.0,
                           t_inlet_k=300.0, construction="coax_shell")
    assert m_milled["jacket_dp_pa"] == m1["jacket_dp_pa"]          # default = milled, no change
    assert m_tube["t_wc_throat_k"] > m_milled["t_wc_throat_k"]
    assert m_coax["t_wc_throat_k"] > m_tube["t_wc_throat_k"]
    assert m_tube["jacket_dp_pa"] > m_milled["jacket_dp_pa"] > m_coax["jacket_dp_pa"] > 0.0

    # channel_geometry_profile: a separate, additive per-station wrapper for the
    # 3D preview - covers every station (not just the coolant-flow-restricted
    # segments march_coolant marches over) and touches none of march_coolant's
    # own internal per-station calls or lumped outputs.
    x_bell = np.linspace(0.0, 1.0, 8)
    r_bell = np.linspace(0.05, 0.30, 8)              # purely diverging (bell) contour
    prof = channel_geometry_profile(x_bell, r_bell, n_channels=120,
                                    channel_height_m=4.0e-3, land_fraction=0.35)
    assert prof["width_m"].shape == x_bell.shape
    assert np.all(prof["width_m"] > 0.0) and np.all(prof["dh_m"] > 0.0)
    assert np.all(np.diff(prof["width_m"]) > 0.0)      # wider radius -> wider channel
    assert np.allclose(prof["height_m"], 4.0e-3)       # fixed channel height, per design
    # unaffected: march_coolant's own numbers on the earlier chamber/throat/exit
    # contour are exactly as computed above, whether or not this function ran.
    m_recheck = march_coolant(cx, cr, cq, ct_dia, 60.0, "LOX/RP-1", transition_area_ratio=6.0,
                              t_inlet_k=300.0)
    assert {k: v for k, v in m_recheck.items() if not k.endswith("_profile_w_m2k")
            and not k.endswith("_profile_k")} == {
        k: v for k, v in m1.items() if not k.endswith("_profile_w_m2k")
        and not k.endswith("_profile_k")}
    assert np.array_equal(m_recheck["h_c_profile_w_m2k"], m1["h_c_profile_w_m2k"], equal_nan=True)
    # per-station march profiles: finite over the cooled length, NaN past the
    # transition; the vectorised wall balance reproduces the scalar one.
    _hp, _tp = m1["h_c_profile_w_m2k"], m1["t_bulk_profile_k"]
    assert _hp.shape == cx.shape and np.isfinite(_hp[0]) and np.isfinite(_tp[0])
    _tw, _tc, _qb = solve_wall_balance_profile(np.full(len(cx), 7.0e3), 3100.0, _hp, _tp,
                                               0.5e-3, 325.0)
    _ok = np.isfinite(_hp)
    assert np.array_equal(np.isfinite(_tw), _ok)
    _j = int(np.flatnonzero(_ok)[0])
    _ref = solve_wall_balance(7.0e3, 3100.0, float(_hp[_j]), float(_tp[_j]), 0.5e-3, 325.0)
    assert abs(_tw[_j] - _ref[0]) < 1e-9 and abs(_qb[_j] - _ref[2]) < 1e-6
    print("channel_geometry_profile self-check: OK")

    # --- dump cooling: auto-sizing and the Isp penalty ------------------------
    assert dump_cooling_isp_penalty_fraction(0.0, 100.0) == 0.0
    assert dump_cooling_isp_penalty_fraction(5.0, 0.0) == 0.0
    p_small = dump_cooling_isp_penalty_fraction(2.0, 100.0)
    p_big = dump_cooling_isp_penalty_fraction(10.0, 100.0)
    assert 0.0 < p_small < p_big < (1.0 - DUMP_THRUST_RECOVERY_FRACTION)  # bigger dump -> bigger loss
    assert abs(p_small - (1.0 - DUMP_THRUST_RECOVERY_FRACTION) * 0.02) < 1e-9  # exact formula

    frac_lo = size_dump_coolant_fraction(0.3e6, 20.0, 2100.0, 120.0)   # small heat load
    frac_hi = size_dump_coolant_fraction(0.9e6, 20.0, 2100.0, 120.0)   # 3x the heat load
    assert DUMP_COOLANT_FRACTION_MIN <= frac_lo < frac_hi <= DUMP_COOLANT_FRACTION_MAX
    assert size_dump_coolant_fraction(1.0, 20.0, 2100.0, 1e9) == DUMP_COOLANT_FRACTION_MIN  # floored
    assert size_dump_coolant_fraction(1e12, 20.0, 2100.0, 1.0) == DUMP_COOLANT_FRACTION_MAX  # ceiled

    # --- computed-absolute Bartz flux profile (reported diagnostic) -----------
    q_abs = absolute_heat_flux_profile(cx, cr, ct_dia, 8.0e6, 1720.0, 7.6e-5, 2100.0, 0.77,
                                       3240.0, transition_area_ratio=6.0)
    assert q_abs.size == cx.size and float(np.min(q_abs)) >= 0.0
    _hgp = bartz_hg_profile(cx, cr, ct_dia, 8.0e6, 1720.0, 7.6e-5, 2100.0, 0.77)
    assert np.allclose(_hgp * (3240.0 - WALL_TEMP_FRACTION_DEFAULT * 3240.0), q_abs, rtol=1e-12)
    thr_i = int(np.argmin(cr))
    assert int(np.argmax(q_abs)) == thr_i, "absolute profile should also peak at the throat"
    q_abs_hot = absolute_heat_flux_profile(cx, cr, ct_dia, 8.0e6, 1720.0, 7.6e-5, 2100.0, 0.77,
                                           3240.0, wall_temp_k=500.0, transition_area_ratio=6.0)
    assert float(q_abs_hot.max()) > float(q_abs.max()), "cooler wall -> higher flux (bigger T_aw-T_wg)"
    assert np.array_equal(absolute_heat_flux_profile(cx, cr, 0.0, 8.0e6, 1720.0, 7.6e-5, 2100.0,
                                                      0.77, 3240.0), np.zeros(cx.size))

    # --- J-2-style two-pass march (march_coolant_two_pass) -------------------
    _tx = np.linspace(0.0, 1.0, 241)
    _tr = np.interp(_tx, [0.0, 0.2, 0.3, 1.0], [0.10, 0.10, 0.04, 0.20])   # eps 25 exit
    _tdt = 0.08
    _tq = heat_flux_profile(_tx, _tr, _tdt, pc_pa=5.0e6, transition_area_ratio=25.0)
    _single = march_coolant(_tx, _tr, _tq, _tdt, 5.0, "LOX/LH2", transition_area_ratio=25.0,
                            t_inlet_k=40.0)
    # (i) zero-length down pass (inlet past the cooled end) == single pass.
    _z = march_coolant_two_pass(_tx, _tr, _tq, _tdt, 5.0, "LOX/LH2", inlet_area_ratio=30.0,
                                transition_area_ratio=25.0, t_inlet_k=40.0)
    for _key in ("coolant_exit_t_k", "coolant_delta_t_k", "jacket_dp_pa", "t_wc_throat_k",
                 "channel_dh_throat_m", "n_channels"):
        assert abs(_z[_key] - _single[_key]) <= 1e-9 * max(1.0, abs(_single[_key])), \
            (_key, _z[_key], _single[_key])
    assert _z["jacket_dp_down_pa"] == 0.0 and _z["coolant_turnaround_t_k"] == 40.0
    assert np.allclose(_z["h_c_profile_w_m2k"], _single["h_c_profile_w_m2k"], equal_nan=True)
    assert np.allclose(_z["t_bulk_profile_k"], _single["t_bulk_profile_k"], equal_nan=True)
    # (ii) total coolant temperature rise is inlet-independent (energy balance).
    _mid = march_coolant_two_pass(_tx, _tr, _tq, _tdt, 5.0, "LOX/LH2", inlet_area_ratio=8.0,
                                  transition_area_ratio=25.0, t_inlet_k=40.0)
    _deep = march_coolant_two_pass(_tx, _tr, _tq, _tdt, 5.0, "LOX/LH2", inlet_area_ratio=3.0,
                                   transition_area_ratio=25.0, t_inlet_k=40.0)
    for _m in (_mid, _deep):
        assert abs(_m["coolant_delta_t_k"] - _single["coolant_delta_t_k"]) < 1e-6 * _single["coolant_delta_t_k"]
        assert 40.0 < _m["coolant_turnaround_t_k"] < _m["coolant_exit_t_k"]
    # (iii) dP grows with the down-pass length; the down tubes run ~3x faster
    # than a single-pass jacket at the same station (shared circumference).
    assert _single["jacket_dp_pa"] < _mid["jacket_dp_pa"] < _deep["jacket_dp_pa"]
    assert 0.0 < _mid["jacket_dp_down_pa"] < _deep["jacket_dp_down_pa"]
    _d8 = 2.0 * 0.04 * math.sqrt(8.0)
    _v_dn = down_pass_velocity_ms(_d8, _tdt, 5.0, "LOX/LH2")
    _v_sp = passage_velocity_ms(_d8, _tdt, 5.0, "LOX/LH2")
    _nu, _nd = two_pass_tube_counts(_tdt)
    assert abs(_v_dn / _v_sp - (_nu + _nd) / _nd) < 1e-9
    assert _nd == round(_nu * J2_DOWN_TO_UP_TUBE_RATIO) and _mid["n_channels_down"] == _nd
    print(f"two-pass march: inlet eps 8 -> dT {_mid['coolant_delta_t_k']:.0f} K (= single-pass), "
          f"turnaround {_mid['coolant_turnaround_t_k']:.0f} K, dP {_single['jacket_dp_pa']/1e6:.2f} "
          f"-> {_mid['jacket_dp_pa']/1e6:.2f} MPa (down {_mid['jacket_dp_down_pa']/1e6:.2f}), "
          f"down-tube inlet {_mid['down_pass_inlet_velocity_ms']:.0f} m/s: OK")

    print(f"channel model: {m1['n_channels']} ch, Dh_throat {m1['channel_dh_throat_m']*1e3:.2f} mm, "
          f"coolant dT {m1['coolant_delta_t_k']:.0f} K, jacket dP {m1['jacket_dp_pa']/1e6:.2f} MPa "
          f"(x CHANNEL_DP_CALIBRATION={CHANNEL_DP_CALIBRATION})")

    print(f"cooling.py smoke test OK - throat {q.max()/1e6:.1f} MW/m^2, "
          f"area-avg anchor {q_avg/1e6:.1f} MW/m^2 (peak/mean {q.max()/from_profile_mean:.1f}x), "
          f"wall heat {total/1e6:.2f} MW, coolant dT {dt:.0f} K; "
          f"Bartz h_g throat {hg_throat:.0f} W/m^2/K -> q {q_throat_bartz/1e6:.1f} MW/m^2, "
          f"T_aw {t_aw:.0f} K; radiative T_wg {t_rad:.0f} K")
