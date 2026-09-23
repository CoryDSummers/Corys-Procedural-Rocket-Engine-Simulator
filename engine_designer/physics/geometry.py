"""
Chamber/throat/exit sizing (generalized copy of the validated math in
/home/cory/ksp_config/sim/engine_physics.py) plus a simple conical-nozzle
2D profile generator for the GUI schematic. This is a schematic outline,
not a manufacturing drawing - straight conical convergent/divergent
sections, not a true bell (parabolic) contour.
"""
import math

import numpy as np

# Universal gas constant [J/kmol-K] - matches physics/combustion._R_UNIVERSAL_J_KMOL_K
# (kept local to avoid a geometry -> combustion import). Used only by the
# residence-time chamber-sizing method below.
_R_UNIVERSAL_J_KMOL_K = 8314.462

THROAT_FILLET_R_OVER_RT = 1.5   # convergent-side throat-radius arc, R ~ 1.5*Rt
                                # ([Huzel Sample 4-2]; the sharp corner the tool
                                # drew before is not physical). Clamped so it
                                # never eats more than a fraction of the cone.
_FILLET_POINTS = 7
_WALL_FILLET_POINTS = 9         # points on the cylinder->convergent-cone blend arc


def _revolved_volume(xs, rs):
    """Volume of the solid of revolution of the (xs, rs) polyline about the axis,
    summed as conical frustums. |.| so segment order doesn't matter."""
    xs = np.asarray(xs, dtype=float)
    rs = np.asarray(rs, dtype=float)
    v = 0.0
    for i in range(len(xs) - 1):
        dx = xs[i + 1] - xs[i]
        v += math.pi * dx / 3.0 * (rs[i] ** 2 + rs[i] * rs[i + 1] + rs[i + 1] ** 2)
    return abs(v)


def _wall_fillet_arc(rc, rt, conv_len, convergent_half_angle_deg, fillet_r):
    """
    Circular arc blending the cylindrical chamber wall (r = rc) into the straight
    convergent cone, tangent to both. Returns (rel_x, r) arrays with rel_x
    measured from the nominal cylinder/cone junction (so the arc runs from
    rel_x = -R*tan(theta/2) on the cylinder to rel_x > 0 on the cone). Empty
    arrays when the fillet is degenerate or disabled.

    Radius is capped to 0.4*conv_len and 0.6*(rc - rt) so an aggressive request
    can't swallow the whole cone or the whole radius drop.
    """
    theta = math.radians(convergent_half_angle_deg)
    if fillet_r <= 0.0 or conv_len <= 0.0 or rc <= rt:
        return np.array([]), np.array([])
    r = min(fillet_r, 0.4 * conv_len, 0.6 * (rc - rt))
    d = r * math.tan(theta / 2.0)                  # cylinder tangent point at rel_x = -d
    cx, cr = -d, rc - r                            # arc centre
    phis = np.linspace(math.pi / 2.0, math.pi / 2.0 - theta, _WALL_FILLET_POINTS)
    return cx + r * np.cos(phis), cr + r * np.sin(phis)


def _wall_fillet_volume_removed(rc, rt, conv_len, convergent_half_angle_deg, fillet_r):
    """Gas volume the cylinder->cone blend arc removes versus the sharp-cornered
    profile (revolved), over the arc's own x-span. >= 0. Zero when the fillet is
    disabled - so the L* <-> chamber-length bookkeeping in chamber_geometry stays
    exact for whatever convergent_profile actually draws."""
    ax, ar = _wall_fillet_arc(rc, rt, conv_len, convergent_half_angle_deg, fillet_r)
    if ax.size == 0:
        return 0.0
    theta = math.radians(convergent_half_angle_deg)
    sharp_r = np.where(ax <= 0.0, rc, rc - math.tan(theta) * ax)   # cylinder then cone
    return _revolved_volume(ax, sharp_r) - _revolved_volume(ax, ar)


def chamber_geometry(mdot, cstar, pc, eps, lstar=1.0, contraction_ratio=1.6,
                      convergent_half_angle_deg=30.0, chamber_wall_fillet_r_over_rt=0.0,
                      sizing_method="lstar", residence_time_s=0.0, tc_k=0.0, m_molar=0.0):
    """
    Throat/exit/chamber sizing from mass flow, c*, chamber pressure and area
    ratio. Two ways to set the injector-face-to-throat volume Vc_total, both
    reduced to a cylindrical-section length the same way (subtract the
    convergent cone's own frustum volume, divide by the chamber area):

      sizing_method="lstar" (default): Vc_total = L* * At, the standard (Sutton)
        characteristic-length definition (Vc INCLUDING the convergent cone).

      sizing_method="residence_time": Vc_total = t_stay * mdot / rho_c, where
        rho_c = Pc*M/(R_u*Tc) is the chamber gas density. `implied_lstar_m` in
        the result is Vc_total/At. Sizing to the stay time
        combustion.residence_time_from_lstar_s(L*_default, ...) implies exactly
        L*_default (see physics/validate.py C4) - the two methods are the same
        knob in different units.

    Bug the L* path replaces: the previous version used chamber_length =
    (L*At)/Ac, which silently cancels At out of the result entirely (a 62.5cm
    chamber whether the engine was 100N or 1.45MN). Subtracting the
    convergent-cone volume is the textbook-correct fix; see physics/design.py's
    LSTAR_TYPICAL_M comment for why small engines ALSO need a genuinely smaller
    L*, not just this formula fix, to look right.

    chamber_wall_fillet_r_over_rt > 0 rounds the sharp cylinder/convergent-cone
    corner with a tangent arc of radius (this * Rt); its removed gas volume is
    subtracted from the convergent volume so Vc_total is still exact for the
    contour convergent_profile() draws. 0.0 = the historical sharp corner,
    bit-identical.
    """
    at = mdot * cstar / pc
    rt = math.sqrt(at / math.pi)
    dt = 2.0 * rt
    ae = eps * at
    de = math.sqrt(4.0 * ae / math.pi)
    ac = contraction_ratio * at
    rc = math.sqrt(ac / math.pi)
    dc = 2.0 * rc

    conv_len = (rc - rt) / math.tan(math.radians(convergent_half_angle_deg))
    v_conv = (math.pi * conv_len / 3.0) * (rc ** 2 + rc * rt + rt ** 2)  # frustum volume
    if chamber_wall_fillet_r_over_rt > 0.0:
        v_conv -= _wall_fillet_volume_removed(
            rc, rt, conv_len, convergent_half_angle_deg,
            chamber_wall_fillet_r_over_rt * rt)

    if sizing_method == "residence_time" and residence_time_s > 0.0 and tc_k > 0.0 and m_molar > 0.0:
        rho_c = pc * m_molar / (_R_UNIVERSAL_J_KMOL_K * tc_k)
        vc_total = residence_time_s * mdot / rho_c
    else:
        vc_total = lstar * at
    implied_lstar_m = vc_total / at if at > 0 else 0.0

    v_cyl = vc_total - v_conv
    cylindrical_volume_clamped = v_cyl <= 0.0
    lc = 0.0 if cylindrical_volume_clamped else v_cyl / ac

    return {
        "throat_area_m2": at, "throat_dia_m": dt,
        "exit_area_m2": ae, "exit_dia_m": de,
        "chamber_area_m2": ac, "chamber_dia_m": dc,
        "chamber_volume_m3": vc_total, "chamber_length_m": lc,
        "cylindrical_volume_clamped": cylindrical_volume_clamped,
        "sizing_method": sizing_method, "implied_lstar_m": implied_lstar_m,
    }


def convergent_profile(chamber_dia_m, throat_dia_m, chamber_length_m,
                        convergent_half_angle_deg=30.0, chamber_wall_fillet_r_over_rt=0.0):
    """
    Upstream-of-throat points (x, r): cylindrical chamber, an optional circular
    arc rounding the cylinder/cone corner (chamber_wall_fillet_r_over_rt > 0), a
    straight convergent cone, and a short circular fillet arc blending the cone
    into the throat (radius ~ 1.5*Rt). The final point is exactly (x_throat, rt)
    so the divergent section (cone or bell) appends seamlessly. Shared by both
    nozzle types - see physics/design.py.
    """
    rc = chamber_dia_m / 2.0
    rt = throat_dia_m / 2.0
    theta = math.radians(convergent_half_angle_deg)
    conv_len = (rc - rt) / math.tan(theta)
    x_chamber_end = chamber_length_m
    x_throat = x_chamber_end + conv_len

    r_fillet = min(THROAT_FILLET_R_OVER_RT * rt, 0.35 * conv_len)
    # Arc centred at (x_throat, rt + r_fillet): phi=0 is the throat (horizontal
    # tangent), phi=theta is the cone-tangent point.
    phis = np.linspace(theta, 0.0, _FILLET_POINTS)
    arc_x = x_throat - r_fillet * np.sin(phis)
    arc_r = rt + r_fillet * (1.0 - np.cos(phis))

    wx, wr = _wall_fillet_arc(rc, rt, conv_len, convergent_half_angle_deg,
                              chamber_wall_fillet_r_over_rt * rt)
    if wx.size and x_chamber_end + wx[0] > 0.0:
        # cylinder -> wall-fillet arc -> (implicit straight cone) -> throat fillet
        xs = np.concatenate([[0.0], x_chamber_end + wx, arc_x])
        rs = np.concatenate([[rc], wr, arc_r])
    else:
        xs = np.concatenate([[0.0, x_chamber_end], arc_x])
        rs = np.concatenate([[rc, rc], arc_r])
    return xs, rs, x_throat, conv_len


def nozzle_profile(chamber_dia_m, throat_dia_m, exit_dia_m, chamber_length_m,
                    convergent_half_angle_deg=30.0, divergent_half_angle_deg=15.0,
                    chamber_wall_fillet_r_over_rt=0.0):
    """
    Axisymmetric upper-contour points (x, r) in meters, from the injector
    face (x=0) through the cylindrical chamber, a straight convergent cone,
    the throat, and a straight divergent CONE to the exit plane (conical
    nozzle type only - see nozzle_shapes.py for the bell alternative).
    """
    xs_conv, rs_conv, x_throat, conv_len = convergent_profile(
        chamber_dia_m, throat_dia_m, chamber_length_m, convergent_half_angle_deg,
        chamber_wall_fillet_r_over_rt)
    rt = throat_dia_m / 2.0
    re = exit_dia_m / 2.0
    theta_div = math.radians(divergent_half_angle_deg)
    div_len = (re - rt) / math.tan(theta_div)
    x_exit = x_throat + div_len

    # Short downstream throat fillet (R ~ 0.382*Rt, the Rao value), then the
    # straight divergent cone out to the exit.
    r_down = min(0.382 * rt, 0.35 * div_len)
    phis = np.linspace(0.0, theta_div, _FILLET_POINTS)
    arc_x = x_throat + r_down * np.sin(phis)
    arc_r = rt + r_down * (1.0 - np.cos(phis))

    xs = np.concatenate([xs_conv[:-1], arc_x, [x_exit]])
    rs = np.concatenate([rs_conv[:-1], arc_r, [re]])
    return xs, rs, {
        "convergent_length_m": conv_len,
        "divergent_length_m": div_len,
        "total_length_m": x_exit,
    }


def split_profile_by_area_ratio(xs_m, rs_m, throat_dia_m, eps_for_transition):
    """
    Split an axisymmetric (xs_m, rs_m) profile into a "chamber/nozzle" part
    and a "nozzle extension" part at the point where local area ratio
    (r/rt)^2 reaches eps_for_transition (design.py's cooling-transition
    point, i.e. min(cooling_transition_eps, expansion_ratio)) - for
    RENDERING (gui/schematic.py, gui/preview3d.py) only, not new physics.

    A conical nozzle's profile has only 2 points past the throat (throat,
    exit) - snapping to the nearest EXISTING sample would always land on the
    exit itself (the only samples at/above most cutoffs), silently hiding the
    extension for every conical design. Instead this interpolates a synthetic
    boundary point between the two profile samples that straddle the target
    radius (exact for a straight conical section; a reasonable secant
    approximation for the discretized bell curve).

    Returns (body_xs, body_rs, ext_xs, ext_rs, has_extension). When the
    transition is at or beyond the nozzle exit (no real extension to draw),
    has_extension is False and body_xs/body_rs are the full profile unchanged.
    """
    xs_m = np.asarray(xs_m)
    rs_m = np.asarray(rs_m)
    rt = throat_dia_m / 2.0
    throat_idx = int(np.argmin(rs_m))
    target_r = rt * math.sqrt(eps_for_transition)

    # target_r reaching (or passing) the exit radius means the transition
    # point IS the nozzle exit - there's no real second piece to draw.
    # Without this guard, the search loop below still matches at the very
    # last segment (target_r == r1 == rs_m[-1] satisfies r0 <= target_r <=
    # r1), producing a degenerate zero-length "extension" (two coincident
    # points at the exit) while still reporting has_extension=True - which
    # lets a flange/bolt joint render right at the exit tip even though
    # there's no real two-piece assembly there. Relative tolerance (not
    # exact equality) absorbs float roundoff between how target_r and
    # rs_m[-1] were each independently computed (same style as
    # gui/preview3d_gl_core.py's _dedupe_monotonic).
    exit_tol = max(abs(rs_m[-1]), 1.0) * 1e-9
    if target_r >= rs_m[-1] - exit_tol:
        return xs_m, rs_m, xs_m[-1:], rs_m[-1:], False

    for i in range(throat_idx, len(rs_m) - 1):
        r0, r1 = rs_m[i], rs_m[i + 1]
        if r0 <= target_r <= r1:
            frac = 0.0 if r1 == r0 else (target_r - r0) / (r1 - r0)
            x_split = xs_m[i] + frac * (xs_m[i + 1] - xs_m[i])
            body_xs = np.concatenate([xs_m[:i + 1], [x_split]])
            body_rs = np.concatenate([rs_m[:i + 1], [target_r]])
            ext_xs = np.concatenate([[x_split], xs_m[i + 1:]])
            ext_rs = np.concatenate([[target_r], rs_m[i + 1:]])
            return body_xs, body_rs, ext_xs, ext_rs, True

    return xs_m, rs_m, xs_m[-1:], rs_m[-1:], False


if __name__ == "__main__":
    # --- split_profile_by_area_ratio: boundary behavior ---
    # A simple diverging profile: throat at x=1 (r=0.1), exit at x=5 (r=0.3),
    # so eps at the exit = (0.3/0.1)^2 = 9.0.
    xs_split = np.array([0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0])
    rs_split = np.array([0.2, 0.12, 0.1, 0.15, 0.2, 0.25, 0.3])
    throat_dia = 0.2  # rt = 0.1

    # Normal mid-profile split: transition well before the exit.
    bxs, brs, exs, ers, has_ext = split_profile_by_area_ratio(xs_split, rs_split, throat_dia, 4.0)
    assert has_ext
    assert bxs[-1] < xs_split[-1] and exs[0] == bxs[-1]
    assert np.isclose(brs[-1], 0.1 * math.sqrt(4.0))

    # eps_for_transition == expansion_ratio exactly at the exit: no real
    # extension - the bug this guard fixes (previously returned
    # has_extension=True with a zero-length/coincident ext piece).
    bxs_e, brs_e, exs_e, ers_e, has_ext_e = split_profile_by_area_ratio(
        xs_split, rs_split, throat_dia, 9.0)
    assert not has_ext_e
    assert np.array_equal(bxs_e, xs_split) and np.array_equal(brs_e, rs_split)
    assert exs_e[0] == xs_split[-1] and ers_e[0] == rs_split[-1]

    # Beyond the exit (eps_for_transition > exit eps): already-documented
    # "no extension" fallback, unaffected by the new guard.
    bxs_b, brs_b, exs_b, ers_b, has_ext_b = split_profile_by_area_ratio(
        xs_split, rs_split, throat_dia, 20.0)
    assert not has_ext_b
    assert np.array_equal(bxs_b, xs_split) and np.array_equal(brs_b, rs_split)

    # Conical case (only 2 points past the throat, per this function's own
    # docstring) - a mid-profile split must still interpolate a synthetic
    # boundary point, not silently collapse to "no extension".
    xs_cone = np.array([0.0, 1.0, 5.0])
    rs_cone = np.array([0.2, 0.1, 0.3])
    bxs_c, brs_c, exs_c, ers_c, has_ext_c = split_profile_by_area_ratio(
        xs_cone, rs_cone, throat_dia, 4.0)
    assert has_ext_c
    assert 1.0 < bxs_c[-1] < 5.0
    assert np.isclose(brs_c[-1], 0.1 * math.sqrt(4.0))

    print("split_profile_by_area_ratio self-check: OK")
