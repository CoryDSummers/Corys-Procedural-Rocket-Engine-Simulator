"""
Nozzle contour generation for both supported nozzle types:
  - conical: a straight cone from throat to exit at a user-set half-angle
    (unchanged from v1 - see geometry.nozzle_profile / isentropic.
    nozzle_divergence_efficiency).
  - bell: a Rao-style parabolic-approximation contour, shorter than an
    equivalent-performance cone for a given expansion ratio - the actual
    engineering reason bell nozzles exist, not just a different picture.

Bell (theta_n, theta_e) table: digitized from the Rao thrust-optimized-
parabola optimum-contour chart as reproduced in Sutton & Biblarz, *Rocket
Propulsion Elements* Fig. 3-14 (initial parabola angle theta_n and exit
angle theta_e vs area ratio, for 60 / 80 / 100 % bell length). Both angles
are largest for the shortest (60%) bell and fall as the bell lengthens.
Cross-checked against real engine bells (F-1 eps~16, J-2 eps~27.5, RS-25
eps~69, all ~80% length) in physics/validate.py's run_chamber_detail_check
C6. Still an engineering approximation - a chart read by eye, not RPA/MOC
output - but no longer an un-anchored guess.

The contour includes the small throat-radius fillet the full Rao method
uses (a circular arc of ~0.382*Rt just downstream of the throat, blending
the horizontal throat tangent up to theta_n before the parabola starts);
pass throat_fillet=False to bell_profile_points to get the bare parabola.
"""
import math

import numpy as np
from scipy.interpolate import RegularGridInterpolator

from . import isentropic as iso

_PERCENT_GRID = np.array([60.0, 80.0, 100.0])
_EPS_GRID = np.array([5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0])

# degrees; rows = percent length (60/80/100), cols = expansion ratio (_EPS_GRID).
# Sutton & Biblarz Fig. 3-14 (Rao TOP optimum-contour chart). theta_n and theta_e
# BOTH decrease as the bell lengthens 60 -> 80 -> 100 %.
_THETA_N = np.array([
    [32.0, 36.0, 38.0, 39.0, 40.0, 40.5, 41.5, 42.0],   # 60% bell
    [30.0, 33.0, 34.5, 35.5, 36.5, 37.0, 38.0, 38.5],   # 80% bell
    [26.0, 30.0, 31.5, 32.5, 33.0, 33.5, 34.5, 35.0],   # 100% bell
])
_THETA_E = np.array([
    [26.0, 22.0, 19.5, 18.0, 17.0, 16.0, 14.5, 13.5],   # 60% bell
    [18.0, 14.0, 12.0, 11.0, 10.0, 9.5, 8.5, 8.0],      # 80% bell
    [10.0, 7.5, 6.5, 6.0, 5.5, 5.0, 4.5, 4.0],          # 100% bell
])

_theta_n_interp = RegularGridInterpolator((_PERCENT_GRID, _EPS_GRID), _THETA_N)
_theta_e_interp = RegularGridInterpolator((_PERCENT_GRID, _EPS_GRID), _THETA_E)


def bell_angles(eps, percent_length):
    """(theta_n, theta_e) in degrees for the given expansion ratio and %-length.
    Clamped to the table's range rather than extrapolated."""
    eps_c = float(np.clip(eps, _EPS_GRID.min(), _EPS_GRID.max()))
    pl_c = float(np.clip(percent_length, _PERCENT_GRID.min(), _PERCENT_GRID.max()))
    theta_n = float(_theta_n_interp([[pl_c, eps_c]])[0])
    theta_e = float(_theta_e_interp([[pl_c, eps_c]])[0])
    return theta_n, theta_e


def cone_reference_length(rt, re, half_angle_deg=15.0):
    """Length of the equivalent 15-deg-half-angle conical nozzle - the
    reference "100% length" a bell is measured against."""
    return (re - rt) / math.tan(math.radians(half_angle_deg))


def bell_length(rt, re, percent_length, half_angle_deg=15.0):
    return (percent_length / 100.0) * cone_reference_length(rt, re, half_angle_deg)


_THROAT_FILLET_R_OVER_RT = 0.382   # downstream throat-arc radius, R ~ 0.382*Rt
                                   # (the Rao value; matches geometry.nozzle_profile's
                                   # conical-path downstream fillet)
_THROAT_FILLET_POINTS = 7


def bell_profile_points(rt, re, x_throat, theta_n_deg, theta_e_deg, length, n=30,
                         throat_fillet=True):
    """
    Divergent bell contour from the throat (x_throat, rt) to the exit
    (x_throat+length, re).

    With throat_fillet=True (default): a short circular arc of radius ~0.382*Rt
    just downstream of the throat blends the horizontal throat tangent up to
    theta_n, then a quadratic-Bezier parabola runs from the arc's end (at tangent
    angle theta_n) to the exit (at tangent angle theta_e). With throat_fillet=
    False: the bare parabola straight from (x_throat, rt) at theta_n.

    The contour still starts exactly at (x_throat, rt) and ends exactly at
    (x_throat+length, re) either way. Returns (xs, ys, (x1, y1)) where (x1, y1)
    is the Bezier control point.
    """
    tn = math.tan(math.radians(theta_n_deg))
    te = math.tan(math.radians(theta_e_deg))
    if abs(tn - te) < 1e-9:
        raise ValueError("theta_n and theta_e too close to define a parabola")
    x2, y2 = x_throat + length, re

    fx = fr = None
    if throat_fillet:
        r_arc = min(_THROAT_FILLET_R_OVER_RT * rt, 0.35 * length)
        phis = np.linspace(0.0, math.radians(theta_n_deg), _THROAT_FILLET_POINTS)
        fx = x_throat + r_arc * np.sin(phis)
        fr = rt + r_arc * (1.0 - np.cos(phis))
        x0, y0 = float(fx[-1]), float(fr[-1])
    else:
        x0, y0 = x_throat, rt

    x1 = (y2 - y0 + tn * x0 - te * x2) / (tn - te)
    y1 = y0 + tn * (x1 - x0)

    t = np.linspace(0.0, 1.0, n)
    bx = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * x1 + t ** 2 * x2
    by = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * y1 + t ** 2 * y2

    if throat_fillet:
        xs = np.concatenate([fx[:-1], bx])
        ys = np.concatenate([fr[:-1], by])
    else:
        xs, ys = bx, by
    return xs, ys, (x1, y1)


def bell_divergence_efficiency(theta_e_deg):
    """Reuses isentropic.nozzle_divergence_efficiency on the bell's EXIT
    angle - at this level of fidelity the exit flow-angle distribution
    (set by theta_e) is what dominates the divergence loss; theta_n mainly
    shapes the contour/length rather than the loss."""
    return iso.nozzle_divergence_efficiency(theta_e_deg)


def reference_lambda(eps, percent_length=80.0):
    """
    Divergence efficiency of the REFERENCE nozzle (an 80%-length Rao bell at
    this expansion ratio) - the nozzle quality physics/combustion.py's
    DEFAULT_ETA_CSTAR calibration implicitly assumes (see physics/validate.py,
    which checks Isp with no divergence-efficiency term at all - i.e. assumes
    whatever nozzle the real engine used performs AS WELL AS this reference).

    design.py scores every ACTUAL nozzle choice relative to this (lam_actual /
    reference_lambda(eps)), so picking the reference nozzle itself reproduces
    the calibration exactly, and any other choice shows an honest efficiency
    delta instead of double-counting a loss the calibration already absorbed.
    """
    _, theta_e = bell_angles(eps, percent_length)
    return bell_divergence_efficiency(theta_e)


if __name__ == "__main__":
    # 1) bell_length at 100% must exactly equal the reference conical length.
    rt, re = 0.18, 0.7
    lc = cone_reference_length(rt, re)
    assert abs(bell_length(rt, re, 100.0) - lc) < 1e-9

    # 2) theta_e must fall monotonically as percent_length rises 60->80->100,
    #    for every eps in the table - the actual point of a bell (longer bell,
    #    lower divergence loss). This exercises the digitized table itself,
    #    not just the interpolation machinery.
    for eps in _EPS_GRID:
        te60 = bell_angles(eps, 60.0)[1]
        te80 = bell_angles(eps, 80.0)[1]
        te100 = bell_angles(eps, 100.0)[1]
        assert te60 > te80 > te100, (eps, te60, te80, te100)

    # 2b) theta_n likewise falls monotonically with %length (Sutton Fig 3-14 -
    #     the shortest bell needs the largest initial turn).
    for eps in _EPS_GRID:
        tn60 = bell_angles(eps, 60.0)[0]
        tn80 = bell_angles(eps, 80.0)[0]
        tn100 = bell_angles(eps, 100.0)[0]
        assert tn60 > tn80 > tn100, (eps, tn60, tn80, tn100)

    # 3) Divergence efficiency must therefore rise monotonically with %length.
    for eps in (10.0, 20.0, 40.0):
        effs = [bell_divergence_efficiency(bell_angles(eps, pl)[1]) for pl in (60.0, 80.0, 100.0)]
        assert effs[0] < effs[1] < effs[2], (eps, effs)

    # 4) Bare-parabola (throat_fillet=False) endpoints must land exactly on the
    #    throat and exit points.
    theta_n, theta_e = bell_angles(20.0, 80.0)
    length = bell_length(rt, re, 80.0)
    xs, ys, (x1, y1) = bell_profile_points(rt, re, x_throat=1.0, theta_n_deg=theta_n,
                                            theta_e_deg=theta_e, length=length,
                                            throat_fillet=False)
    assert abs(xs[0] - 1.0) < 1e-9 and abs(ys[0] - rt) < 1e-9
    assert abs(xs[-1] - (1.0 + length)) < 1e-9 and abs(ys[-1] - re) < 1e-9

    # 5) The control point must actually lie on both tangent lines (validates
    #    the line-intersection algebra, not just the Bezier evaluation).
    tn, te = math.tan(math.radians(theta_n)), math.tan(math.radians(theta_e))
    y1_from_start_line = rt + tn * (x1 - 1.0)
    y1_from_end_line = re + te * (x1 - (1.0 + length))
    assert abs(y1 - y1_from_start_line) < 1e-9
    assert abs(y1 - y1_from_end_line) < 1e-9

    # 6) The filleted contour (default) still starts exactly at the throat and
    #    ends exactly at the exit, is longer near the throat than the bare
    #    parabola for the same length (the arc adds points), and the arc's last
    #    segment leaves at ~theta_n.
    fxs, fys, _ = bell_profile_points(rt, re, x_throat=1.0, theta_n_deg=theta_n,
                                       theta_e_deg=theta_e, length=length)
    assert abs(fxs[0] - 1.0) < 1e-9 and abs(fys[0] - rt) < 1e-9
    assert abs(fxs[-1] - (1.0 + length)) < 1e-9 and abs(fys[-1] - re) < 1e-9
    assert len(fxs) > len(xs)                       # arc points prepended
    arc_seg_ang = math.degrees(math.atan2(fys[_THROAT_FILLET_POINTS - 1] - fys[_THROAT_FILLET_POINTS - 2],
                                          fxs[_THROAT_FILLET_POINTS - 1] - fxs[_THROAT_FILLET_POINTS - 2]))
    assert abs(arc_seg_ang - theta_n) < 3.0, (arc_seg_ang, theta_n)

    # 7) Table anchored to real ~80%-length engine bells (Sutton Fig 3-14 read
    #    against F-1 / J-2 / RS-25), tolerance +/-3 deg.
    for name, eps, tn_ref, te_ref in [("F-1", 16.0, 33.0, 11.0),
                                       ("J-2", 27.5, 35.5, 9.5),
                                       ("RS-25", 69.0, 37.5, 7.0)]:
        tn_i, te_i = bell_angles(eps, 80.0)
        assert abs(tn_i - tn_ref) <= 3.0, (name, "theta_n", tn_i, tn_ref)
        assert abs(te_i - te_ref) <= 3.0, (name, "theta_e", te_i, te_ref)

    print("nozzle_shapes.py self-checks: OK")
    print(f"{'pl%':>5} {'eps':>5} {'theta_n':>8} {'theta_e':>8} {'lambda':>8}")
    for pl in (60.0, 80.0, 100.0):
        for eps in (10.0, 20.0, 40.0):
            tn_, te_ = bell_angles(eps, pl)
            lam = bell_divergence_efficiency(te_)
            print(f"{pl:5.0f} {eps:5.0f} {tn_:8.2f} {te_:8.2f} {lam:8.4f}")
