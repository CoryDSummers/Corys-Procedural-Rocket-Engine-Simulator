"""
Profile-curve geometry helpers for the OpenGL 3D preview: offsetting a 2D
axisymmetric (x, r) profile along its local meridian normal, sampling exact
sub-segments of a profile polyline, rounding a 3D waypoint polyline into a
true circular-arc fillet, and parallel-transporting a frame along an
arbitrary 3D centerline. Split out of the former single-file
gui/preview3d_gl_core.py by geometry-operation kind - see this package's
__init__.py for the overview. No OpenGL/Tk import, pure numpy.
"""
import warnings

import numpy as np

from .hardware_constants import CHANNEL_OUTER_JACKET_M

def effective_offset_thickness_m(structural_thickness_m, channel_height_m):
    """
    The rendered wall-offset distance: at least the bare structural (hoop-
    stress) thickness, or (channel height + a thin outer jacket) when real
    channel data exists, whichever is larger - a ribbed wall's true outer
    surface sits outside the channel/tube layer, not at the bare structural
    shell thickness that's only correct for an unribbed wall. Without this,
    channel_modulated_grid's amplitude clamp (0.6x this same thickness) chokes
    real multi-mm channel height down to a fraction of the bare structural
    number, which can be far thinner (e.g. a nozzle-extension skirt sized off
    local static pressure, ~0.5mm) - rendering invisible ribs.

    Applied unconditionally, not just for tube_wall/milled_channel: a
    coax_shell's smooth double-wall annulus should also reflect the real
    coolant gap rather than collapsing to the bare structural thickness.
    """
    if channel_height_m is None:
        return structural_thickness_m
    return np.maximum(structural_thickness_m, channel_height_m + CHANNEL_OUTER_JACKET_M)

def sample_profile_segment(xs_m, rs_m, x_lo_m, x_hi_m):
    """
    The exact piecewise-linear polyline of (xs_m, rs_m) (sorted by x)
    restricted to [x_lo_m, x_hi_m]: interpolated endpoints at exactly
    x_lo_m/x_hi_m, plus any native stations strictly inside the range.

    Used to snap a flange's base edge onto the REAL rendered bell surface -
    this reuses np.interp on the SAME points the real shell mesh revolves,
    so a curve built from this output touches the real surface exactly
    (identical linear segments, not an approximation), regardless of local
    curvature or how coarse/fine the native station spacing happens to be.
    Requires x_lo_m <= x_hi_m and at least 2 points in xs_m/rs_m.
    """
    xs_m = np.asarray(xs_m, dtype=float)
    rs_m = np.asarray(rs_m, dtype=float)
    r_lo = float(np.interp(x_lo_m, xs_m, rs_m))
    r_hi = float(np.interp(x_hi_m, xs_m, rs_m))
    mask = (xs_m > x_lo_m) & (xs_m < x_hi_m)
    xs_out = np.concatenate([[x_lo_m], xs_m[mask], [x_hi_m]])
    rs_out = np.concatenate([[r_lo], rs_m[mask], [r_hi]])
    return xs_out, rs_out

def manifold_clear_of_flange_x(x_manifold, x_split, flange_half_width_m, manifold_tube_r_m):
    """
    Shift a far-end manifold/turnaround ring's axial position so it doesn't overlap a
    real bolted-flange joint at x_split: if x_manifold already sits at least
    flange_half_width_m + manifold_tube_r_m away, it's returned unchanged; otherwise
    it's moved to the CHAMBER side of the flange (x_split - clearance) - shifted
    upstream, away from the nozzle exit, per the chosen fix direction (grow clearance
    by moving the ring, not by growing its radius), so both pieces of hardware stay
    visible without overlapping.
    """
    clearance = flange_half_width_m + manifold_tube_r_m
    if abs(x_manifold - x_split) >= clearance:
        return x_manifold
    return x_split - clearance

def meridian_normals(xs_m, rs_m):
    """
    Analytic smooth-shading normal for a surface of revolution, in the
    meridian (x, r) plane: (-dr/dx, 1) normalized. For a cylinder (dr/dx=0)
    this is purely radial (0, 1); for a cone of half-angle a (dr/dx=tan a)
    this is (-sin a, cos a) - the standard "outward and leaning back against
    the direction of expansion" lampshade normal. Returns (n_x, n_r), each
    shape (len(xs_m),).
    """
    xs_m = np.asarray(xs_m, dtype=float)
    rs_m = np.asarray(rs_m, dtype=float)
    if xs_m.size < 2:
        return np.zeros_like(xs_m), np.ones_like(xs_m)
    xs_m = _dedupe_monotonic(xs_m)
    drdx = np.gradient(rs_m, xs_m)
    denom = np.sqrt(1.0 + drdx ** 2)
    n_x = -drdx / denom
    n_r = 1.0 / denom
    return n_x, n_r

def _dedupe_monotonic(xs_m):
    """
    Real contours legitimately produce an exact (or near-exact) duplicate
    adjacent x-value at a segment join - a fillet/arc endpoint, or a
    chamber/nozzle-extension split landing exactly on an existing sample
    (physics/geometry.split_profile_by_area_ratio). np.gradient's non-
    uniform-spacing formula divides by the adjacent spacing, so a zero (or
    effectively-zero) spacing NaNs that station's slope - previously only a
    cosmetic shading glitch at one vertex ring, but now that offset_profile
    uses this same normal to actually MOVE geometry (not just shade it), a
    single NaN there corrupts real mesh positions, not just lighting.

    Nudges any near-zero adjacent spacing up to a tiny (1e-9 x the profile's
    own span) minimum, preserving monotonic order - physically equivalent to
    treating a truly-vertical wall segment as very slightly sloped, well
    below anything visible.
    """
    span = float(xs_m.max() - xs_m.min()) if xs_m.size else 0.0
    eps = max(span, 1.0) * 1e-9
    xs_safe = xs_m.astype(float).copy()
    for i in range(1, xs_safe.size):
        if xs_safe[i] - xs_safe[i - 1] < eps:
            xs_safe[i] = xs_safe[i - 1] + eps
    return xs_safe

def offset_profile(xs_m, rs_m, thickness_m):
    """
    Push a 2D axisymmetric (x, r) profile outward by `thickness_m` along its
    LOCAL MERIDIAN NORMAL (reusing meridian_normals' (n_x, n_r)) rather than
    a flat radial offset - so a sloped section (convergent/divergent cone,
    bell) offsets correctly in both x and r, not just r. `thickness_m` may be
    a scalar or a per-station array (len(xs_m),).

    This is the solid-shell wall: the ORIGINAL profile is the inner (gas-
    side) wall, this function's output is the outer wall. Clamped so the
    outer radius never crosses the axis.
    """
    xs_m = np.asarray(xs_m, dtype=float)
    rs_m = np.asarray(rs_m, dtype=float)
    thickness_m = np.broadcast_to(np.asarray(thickness_m, dtype=float), rs_m.shape)
    thickness_m = np.minimum(thickness_m, 0.9 * rs_m)
    n_x, n_r = meridian_normals(xs_m, rs_m)
    outer_xs = xs_m + thickness_m * n_x
    outer_rs = rs_m + thickness_m * n_r
    return outer_xs, outer_rs

def fillet_polyline(waypoints_xyz, bend_radius_m, n_bend_samples=12):
    """
    Turn an ordered list of 3D waypoints (straight segments between them)
    into a smooth centerline with each interior corner rounded into a true
    circular arc of radius bend_radius_m - the standard pipe-elbow trim-back
    construction (trim distance along each incident segment =
    bend_radius_m / tan(beta/2), beta = the corner's own interior angle,
    i.e. the angle between the REVERSED incoming direction and the outgoing
    direction: beta=pi means the two segments are colinear (no bend needed,
    trim -> 0), beta->0 means a near hairpin (trim -> infinity, guarded
    below). This is real pipe-elbow geometry, not an approximation - every
    arc sample is at exactly bend_radius_m (or a clamped effective radius,
    see below) from its own arc's analytic center.

    If bend_radius_m would require a trim longer than (a safety fraction of)
    either segment adjacent to a corner, that corner's OWN effective radius
    is silently clamped down (via warnings.warn, not a raised exception) so
    the fillet still fits within its two segments without overlapping a
    neighboring corner's own fillet - this only guards against a single
    corner's own two adjacent segments; it does not resolve two back-to-back
    tight corners fighting over the same short middle segment (out of scope
    for the current "1-2 bends" use case).

    bend_radius_m may be a single scalar (every corner gets the same elbow)
    OR a sequence of n-2 per-corner radii (one per interior waypoint, in
    order) - physics/plumbing.py's per-joint bend radii use the latter;
    every pre-existing caller passes a scalar and is unaffected.

    Returns (centerline_xyz, tangents_xyz), both (K, 3) float64 arrays - the
    tangents are the arc's own analytic d/dtheta (never finite-differenced),
    so they can't be zero/NaN at a straight-to-arc transition.
    """
    waypoints_xyz = np.asarray(waypoints_xyz, dtype=float)
    n = waypoints_xyz.shape[0]
    if n < 2:
        raise ValueError("fillet_polyline needs at least 2 waypoints")
    radii = np.asarray(bend_radius_m, dtype=float)
    if radii.ndim == 0:
        radii = np.full(max(n - 2, 0), float(radii))
    elif radii.shape != (max(n - 2, 0),):
        raise ValueError(f"fillet_polyline: expected {n - 2} per-corner bend radii, got shape {radii.shape}")

    seg_vecs = np.diff(waypoints_xyz, axis=0)
    seg_lens = np.linalg.norm(seg_vecs, axis=1)
    if np.any(seg_lens < 1e-12):
        raise ValueError("fillet_polyline: zero-length segment in waypoints_xyz")
    seg_dirs = seg_vecs / seg_lens[:, None]

    if n == 2:
        return waypoints_xyz.copy(), np.stack([seg_dirs[0], seg_dirs[0]], axis=0)

    pts = [waypoints_xyz[0]]
    tans = [seg_dirs[0]]
    for c in range(n - 2):
        i = c + 1  # waypoint index of this interior corner
        d_in, d_out = seg_dirs[i - 1], seg_dirs[i]
        cos_beta = np.clip(-np.dot(d_in, d_out), -1.0, 1.0)
        beta = np.arccos(cos_beta)

        if beta > np.pi - 1e-9:
            # segments effectively colinear - no bend, pass straight through
            pts.append(waypoints_xyz[i])
            tans.append(d_out)
            continue

        half_beta = beta / 2.0
        r_corner = radii[c]
        trim = r_corner / np.tan(half_beta) if half_beta > 1e-9 else np.inf
        max_allowed = 0.49 * min(seg_lens[i - 1], seg_lens[i])
        # 1e-9 relative slack: a caller that pre-clamps its own radius to
        # exactly this limit (physics/plumbing.resolve_run) must not re-warn
        # over a last-ULP round-trip through tan()
        if trim > max_allowed * (1.0 + 1e-9):
            warnings.warn(
                f"fillet_polyline: bend_radius_m={r_corner:g} would trim "
                f"{trim:g} m at corner {i}, longer than a safe fraction of its "
                f"adjacent segment(s) - clamping to an effective trim of "
                f"{max_allowed:g} m there.")
        trim = min(trim, max_allowed)

        P = waypoints_xyz[i]
        trimmed_in = P - trim * d_in
        trimmed_out = P + trim * d_out
        r_eff = trim * np.tan(half_beta)

        bisector = -d_in + d_out
        bisector = bisector / np.linalg.norm(bisector)
        center = P + (r_eff / np.sin(half_beta)) * bisector

        e1 = (trimmed_in - center) / r_eff
        e2 = (trimmed_out - center) / r_eff
        axis = np.cross(e1, e2)
        axis = axis / np.linalg.norm(axis)
        alpha = np.arccos(np.clip(np.dot(e1, e2), -1.0, 1.0))

        pts.append(trimmed_in)
        tans.append(d_in)
        for s in np.linspace(0.0, alpha, n_bend_samples)[1:-1]:
            rotated = e1 * np.cos(s) + np.cross(axis, e1) * np.sin(s)
            pts.append(center + r_eff * rotated)
            tans.append(np.cross(axis, rotated))
        pts.append(trimmed_out)
        tans.append(d_out)

    pts.append(waypoints_xyz[-1])
    tans.append(seg_dirs[-1])

    tans = np.array(tans, dtype=float)
    tans = tans / np.linalg.norm(tans, axis=1, keepdims=True)
    return np.array(pts, dtype=float), tans

def rotation_minimizing_frames(centerline_xyz, tangents_xyz):
    """
    Parallel-transport (rotation-minimizing frame, "double reflection"
    method - Wang et al. 2008) an arbitrary initial normal along a 3D
    centerline, sample by sample. A naive Frenet frame is unusable for a
    fillet_polyline-style centerline: straight sections have zero curvature
    (an undefined normal), and successive arcs can bend in different planes,
    so a per-sample analytic normal isn't continuous end-to-end - RMF instead
    rotates the previous sample's normal by the MINIMUM twist needed to stay
    perpendicular to the new tangent, which is exactly zero extra twist on
    any straight run (each reflection below is a no-op when consecutive
    points/tangents are colinear).

    Returns (normals_xyz, binormals_xyz), each (K, 3) - an orthonormal frame
    (tangent, normal, binormal) at every centerline sample.
    """
    centerline_xyz = np.asarray(centerline_xyz, dtype=float)
    tangents_xyz = np.asarray(tangents_xyz, dtype=float)
    tangents_xyz = tangents_xyz / np.linalg.norm(tangents_xyz, axis=1, keepdims=True)
    k = centerline_xyz.shape[0]

    normals = np.zeros((k, 3))
    t0 = tangents_xyz[0]
    seed = np.array([1.0, 0.0, 0.0]) if abs(t0[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    n0 = seed - np.dot(seed, t0) * t0
    normals[0] = n0 / np.linalg.norm(n0)

    for i in range(k - 1):
        p_i, p_ip1 = centerline_xyz[i], centerline_xyz[i + 1]
        t_i, t_ip1 = tangents_xyz[i], tangents_xyz[i + 1]
        n_i = normals[i]

        v1 = p_ip1 - p_i
        c1 = np.dot(v1, v1)
        if c1 < 1e-24:
            normals[i + 1] = n_i
            continue
        r_l = n_i - (2.0 / c1) * np.dot(v1, n_i) * v1
        t_l = t_i - (2.0 / c1) * np.dot(v1, t_i) * v1

        v2 = t_ip1 - t_l
        c2 = np.dot(v2, v2)
        n_ip1 = r_l if c2 < 1e-24 else r_l - (2.0 / c2) * np.dot(v2, r_l) * v2
        normals[i + 1] = n_ip1 / np.linalg.norm(n_ip1)

    binormals = np.cross(tangents_xyz, normals)
    binormals = binormals / np.linalg.norm(binormals, axis=1, keepdims=True)
    # Re-orthogonalize against tiny accumulated numerical drift.
    normals = np.cross(binormals, tangents_xyz)
    normals = normals / np.linalg.norm(normals, axis=1, keepdims=True)
    return normals, binormals


def self_test():
    xs_cyl = np.linspace(0.0, 1.0, 5)
    rs_cyl = np.full_like(xs_cyl, 0.5)

    # --- meridian_normals: cylinder is purely radial; a cone matches the
    # analytic lampshade normal (-sin a, cos a) ---
    n_x, n_r = meridian_normals(xs_cyl, rs_cyl)
    assert np.allclose(n_x, 0.0, atol=1e-9)
    assert np.allclose(n_r, 1.0, atol=1e-9)

    half_angle = np.radians(15.0)
    xs_cone = np.linspace(0.0, 2.0, 20)
    rs_cone = 0.1 + xs_cone * np.tan(half_angle)
    n_x2, n_r2 = meridian_normals(xs_cone, rs_cone)
    assert np.allclose(n_x2[2:-2] ** 2 + n_r2[2:-2] ** 2, 1.0, atol=1e-9)
    assert np.allclose(n_x2[2:-2], -np.sin(half_angle), atol=1e-3)
    assert np.allclose(n_r2[2:-2], np.cos(half_angle), atol=1e-3)

    # --- meridian_normals with a REAL DUPLICATE adjacent x (a genuine
    # occurrence at contour segment joins, e.g. physics/geometry's fillet/arc
    # endpoints or a chamber/extension split landing exactly on an existing
    # sample) - must not divide-by-zero/NaN, and every other station's normal
    # stays exactly as if the duplicate weren't perturbed at all ---
    with warnings.catch_warnings():
        warnings.simplefilter("error", category=RuntimeWarning)
        xs_dup = np.array([0.0, 0.5, 0.5, 1.0, 1.5])   # exact duplicate at index 1/2
        rs_dup = np.array([0.2, 0.3, 0.3, 0.35, 0.5])
        n_x3, n_r3 = meridian_normals(xs_dup, rs_dup)
    assert not np.any(np.isnan(n_x3)) and not np.any(np.isnan(n_r3))
    assert np.allclose(n_x3 ** 2 + n_r3 ** 2, 1.0, atol=1e-6)
    xs_clean = np.array([0.0, 0.5, 1.0, 1.5])           # same profile, no duplicate
    rs_clean = np.array([0.2, 0.3, 0.35, 0.5])
    n_x_clean, n_r_clean = meridian_normals(xs_clean, rs_clean)
    assert abs(n_x3[0] - n_x_clean[0]) < 1e-6           # station 0 untouched by the fix
    assert abs(n_x3[-1] - n_x_clean[-1]) < 1e-6          # station -1 untouched by the fix
    print("meridian_normals duplicate-x self-check: OK")
    print("meridian_normals self-check: OK")

    # --- offset_profile: outer radius strictly > inner radius everywhere, no
    # NaNs, for a representative chamber/throat/bell profile; a scalar
    # thickness broadcasts the same as a matching per-station array ---
    xs_shell = np.array([0.0, 0.3, 0.5, 0.7, 1.5])
    rs_shell = np.array([0.20, 0.20, 0.06, 0.06, 0.35])
    t_scalar = 0.004
    t_array = np.full_like(rs_shell, t_scalar)
    oxs_a, ors_a = offset_profile(xs_shell, rs_shell, t_array)
    oxs_s, ors_s = offset_profile(xs_shell, rs_shell, t_scalar)
    assert np.allclose(oxs_a, oxs_s) and np.allclose(ors_a, ors_s)
    assert np.all(ors_a > rs_shell) and not np.any(np.isnan(oxs_a)) and not np.any(np.isnan(ors_a))
    # an oversized thickness is clamped short of crossing the axis
    oxs_big, ors_big = offset_profile(xs_shell, rs_shell, 10.0)
    assert np.all(ors_big > 0.0)
    print("offset_profile self-check: OK")

    # --- effective_offset_thickness_m: floors bare structural thickness up to
    # (channel height + outer jacket) so channel_modulated_grid's own 60%-of-
    # thickness amplitude clamp doesn't erase real channel geometry ---
    t_struct = np.array([0.5e-3, 2.0e-3, 5.0e-3])
    ch_test = np.array([4.0e-3, 1.0e-3, 0.0])
    eff = effective_offset_thickness_m(t_struct, ch_test)
    assert np.allclose(eff, [4.0e-3 + CHANNEL_OUTER_JACKET_M, 2.0e-3, 5.0e-3])
    assert np.array_equal(effective_offset_thickness_m(t_struct, None), t_struct)
    print("effective_offset_thickness_m self-check: OK")

    # --- sample_profile_segment: the exact piecewise-linear polyline of a
    # profile restricted to [x_lo, x_hi] - interpolated endpoints plus any
    # native stations strictly inside the range, used to snap a flange's
    # base onto the REAL rendered wall instead of an idealized chord ---
    xs_prof = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    rs_prof = np.array([1.0, 1.2, 1.5, 1.5, 2.0])  # a kink at x=2 (slope change)
    # a segment spanning the kink at x=2 must include it exactly
    xs_seg, rs_seg = sample_profile_segment(xs_prof, rs_prof, 1.5, 2.5)
    assert np.allclose(xs_seg, [1.5, 2.0, 2.5])
    assert np.allclose(rs_seg, [1.35, 1.5, 1.5])  # interp(1.5)=1.35, native@2=1.5, interp(2.5)=1.5
    # a segment entirely within one leg (no kink) returns just 2 interpolated endpoints
    xs_leg, rs_leg = sample_profile_segment(xs_prof, rs_prof, 0.25, 0.75)
    assert np.allclose(xs_leg, [0.25, 0.75])
    assert np.allclose(rs_leg, [1.05, 1.15])
    print("sample_profile_segment self-check: OK")

    # --- manifold_clear_of_flange_x: shifts a colliding manifold/turnaround
    # ring onto the chamber side of a real flange joint; leaves an already-
    # clear position untouched ---
    assert manifold_clear_of_flange_x(5.0, 5.0, 0.02, 0.03) == 5.0 - 0.05
    assert manifold_clear_of_flange_x(4.98, 5.0, 0.02, 0.03) == 5.0 - 0.05  # inside clearance -> shifted
    assert manifold_clear_of_flange_x(4.0, 5.0, 0.02, 0.03) == 4.0          # already clear -> untouched
    print("manifold_clear_of_flange_x self-check: OK")

    # --- fillet_polyline: an L-shaped 90-degree corner's arc samples all sit
    # at EXACTLY bend_radius_m from the arc's own known analytic center, the
    # straight segments before/after stay colinear with the original
    # waypoints, and the untrimmed path endpoints are preserved exactly ---
    wp_l = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]])
    r_l = 0.3
    c_l, t_l = fillet_polyline(wp_l, r_l, n_bend_samples=20)
    assert np.allclose(c_l[0], wp_l[0]) and np.allclose(c_l[-1], wp_l[-1])
    on_seg1 = np.isclose(c_l[:, 1], 0.0) & (c_l[:, 0] <= 1.0 + 1e-9)
    on_seg2 = np.isclose(c_l[:, 0], 1.0) & (c_l[:, 1] >= 0.0 - 1e-9)
    arc_mask = ~(on_seg1 | on_seg2)
    assert arc_mask.sum() >= 10  # got real arc resolution, not degenerate
    analytic_center = np.array([1.0 - r_l, r_l, 0.0])
    dists = np.linalg.norm(c_l[arc_mask] - analytic_center, axis=1)
    assert np.allclose(dists, r_l, atol=1e-9)
    assert np.all(np.isclose(t_l[on_seg1], [1.0, 0.0, 0.0]))
    assert np.all(np.isclose(t_l[on_seg2], [0.0, 1.0, 0.0]))
    print("fillet_polyline circular-arc self-check: OK")

    # --- fillet_polyline corner-angle edge cases: a near-straight corner
    # (179 degrees) produces a near-zero-deviation fillet with no NaN as
    # beta -> pi; a corner too sharp for the requested bend radius to fit its
    # own adjacent segments clamps (via warnings.warn) rather than producing
    # an overlapping/self-intersecting arc ---
    eps = np.radians(1.0)
    wp_near_straight = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0],
                                  [2.0, np.tan(eps), 0.0]])
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        c_ns, t_ns = fillet_polyline(wp_near_straight, 0.3, n_bend_samples=8)
    assert not np.any(np.isnan(c_ns)) and not np.any(np.isnan(t_ns))
    assert np.allclose(c_ns[0], wp_near_straight[0])
    assert np.allclose(c_ns[-1], wp_near_straight[-1])

    wp_sharp = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.1, 0.1, 0.0]])
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        c_sharp, t_sharp = fillet_polyline(wp_sharp, 5.0, n_bend_samples=8)
    assert any("clamping" in str(w.message) for w in caught)
    assert not np.any(np.isnan(c_sharp))
    print("fillet_polyline corner-angle edge-case self-check: OK")

    # --- rotation_minimizing_frames: orthonormality everywhere, bounded
    # per-step angular change across straight/arc transitions on a synthetic
    # NON-PLANAR path (two bends in different planes), and an explicit
    # contrast against a naive world-up-projected normal to prove this
    # synthetic case really exercises the flip failure mode RMF fixes (a
    # naive normal must flip close to 180 degrees somewhere; RMF must not) ---
    wp_s = np.array([
        [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0],
        [1.0, 1.0, 1.0], [2.0, 1.0, 1.0],
    ])
    c_s, t_s = fillet_polyline(wp_s, 0.2, n_bend_samples=10)
    n_s, b_s = rotation_minimizing_frames(c_s, t_s)
    assert np.allclose(np.linalg.norm(n_s, axis=1), 1.0, atol=1e-9)
    assert np.allclose(np.linalg.norm(b_s, axis=1), 1.0, atol=1e-9)
    assert np.allclose(np.sum(n_s * t_s, axis=1), 0.0, atol=1e-9)
    assert np.allclose(np.sum(b_s * t_s, axis=1), 0.0, atol=1e-9)
    cos_step = np.clip(np.sum(n_s[:-1] * n_s[1:], axis=1), -1.0, 1.0)
    step_angles_deg = np.degrees(np.arccos(cos_step))
    assert step_angles_deg.max() < 15.0, step_angles_deg.max()  # no flip anywhere

    def _naive_projected_normal(tangents):
        up = np.array([0.0, 0.0, 1.0])
        out = []
        for tt in tangents:
            proj = up - np.dot(up, tt) * tt
            pn = np.linalg.norm(proj)
            if pn < 1e-6:
                fallback = np.array([1.0, 0.0, 0.0])
                proj = fallback - np.dot(fallback, tt) * tt
                pn = np.linalg.norm(proj)
            out.append(proj / pn)
        return np.array(out)

    naive_n = _naive_projected_normal(t_s)
    cos_step_naive = np.clip(np.sum(naive_n[:-1] * naive_n[1:], axis=1), -1.0, 1.0)
    step_angles_naive_deg = np.degrees(np.arccos(cos_step_naive))
    assert step_angles_naive_deg.max() > 90.0, step_angles_naive_deg.max()
    print("rotation_minimizing_frames continuity/no-flip self-check: OK")
    print("ALL PROFILE_GEOMETRY CHECKS OK")


if __name__ == "__main__":
    self_test()
