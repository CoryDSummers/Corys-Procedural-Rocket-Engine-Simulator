"""Contour geometry helpers + the legacy area-averaged flux anchor/shape and the cooled-length integrals (wall heat, area-weighted mean).

Part of the physics/cooling/ package (split verbatim out of the former
single-file cooling.py - see cooling/__init__.py for the package overview)."""
import math

import numpy as np

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
# Fraction-of-jet-power reaching the walls, plausibility band only
# [Sutton 8.2: "0.5-5 % of the total energy generated reaches the walls"],
# widened for the coarseness of this model.
WALL_HEAT_ENERGY_FRACTION_TYPICAL = (0.003, 0.06)


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
