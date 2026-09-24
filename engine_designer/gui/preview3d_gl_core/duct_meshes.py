"""
Bent-tube/duct mesh builders for the OpenGL 3D preview: sweeping a circular
cross-section along an arbitrary 3D centerline (rotation-minimizing frames,
via profile_geometry) and the convenience wrapper tying
fillet_polyline + swept_tube_mesh + end caps together for a real bent duct.
Split out of the former single-file gui/preview3d_gl_core.py by geometry-
operation kind - see this package's __init__.py for the overview. No
OpenGL/Tk import, pure numpy.
"""
import numpy as np

from .mesh_primitives import mesh_from_grid, _tube_end_disk
from .profile_geometry import fillet_polyline, rotation_minimizing_frames

def _swept_tube_mesh_from_frames(centerline_xyz, tangents_xyz, normals_f, binormals_f,
                                  tube_radius_m, n_theta, base_color_rgb,
                                  specular_strength=0.0, shininess=32.0):
    """Shared body of swept_tube_mesh/bent_tube_duct_mesh, taking already-computed
    RMF frames so bent_tube_duct_mesh's caps don't force a second RMF pass.
    `tube_radius_m` is a scalar or a per-station array (a reducer/cone along
    the path - physics/plumbing.py's per-segment bores); a varying radius
    tilts each normal back along the tangent by the local dr/ds slope."""
    phi = np.linspace(0.0, 2.0 * np.pi, n_theta)
    cos_phi = np.cos(phi)[:, None]
    sin_phi = np.sin(phi)[:, None]
    dirs = (cos_phi[:, :, None] * normals_f[None, :, :]
            + sin_phi[:, :, None] * binormals_f[None, :, :])
    r = np.asarray(tube_radius_m, dtype=float)
    if r.ndim == 0:
        pts = centerline_xyz[None, :, :] + float(r) * dirs
        nrm = dirs
    else:
        pts = centerline_xyz[None, :, :] + r[None, :, None] * dirs
        s_arc = np.concatenate(([0.0], np.cumsum(np.linalg.norm(
            np.diff(centerline_xyz, axis=0), axis=1))))
        drds = (np.gradient(r, s_arc, edge_order=1) if s_arc[-1] > 0 and np.all(np.diff(s_arc) > 0)
                else np.zeros_like(r))
        nrm = dirs - drds[None, :, None] * np.asarray(tangents_xyz, dtype=float)[None, :, :]
        nrm = nrm / np.linalg.norm(nrm, axis=2, keepdims=True)
    X, Y, Z = pts[..., 0], pts[..., 1], pts[..., 2]
    normals_flat = nrm.reshape(-1, 3).astype(np.float32)
    return mesh_from_grid(X, Y, Z, base_color_rgb, normals=normals_flat,
                           specular_strength=specular_strength, shininess=shininess)

def swept_tube_mesh(centerline_xyz, tangents_xyz, tube_radius_m, n_theta, base_color_rgb,
                     specular_strength=0.0, shininess=32.0):
    """
    Sweep a circular cross-section of radius tube_radius_m along an arbitrary
    3D centerline (centerline_xyz, tangents_xyz - typically fillet_polyline's
    output), using rotation_minimizing_frames to keep the cross-section from
    twisting/flipping at bends or across straight runs. Same (n_theta,
    n_stations) grid convention as every other swept mesh in this file
    (manifold_ring_mesh, _single_tube_mesh) - just with a per-station RMF
    frame instead of a fixed axis or planar circle. Returns the OPEN tube
    BODY only (no end caps) - see bent_tube_duct_mesh for the capped
    convenience wrapper most callers should actually use.

    tube_radius_m may be a scalar or a per-station array (along-path taper,
    e.g. a pipe reducer), analogous to revolve_to_buffers' rs_m.
    """
    centerline_xyz = np.asarray(centerline_xyz, dtype=float)
    tangents_xyz = np.asarray(tangents_xyz, dtype=float)
    normals_f, binormals_f = rotation_minimizing_frames(centerline_xyz, tangents_xyz)
    return _swept_tube_mesh_from_frames(centerline_xyz, tangents_xyz, normals_f, binormals_f,
                                         tube_radius_m, n_theta, base_color_rgb,
                                         specular_strength=specular_strength, shininess=shininess)

def bent_tube_duct_mesh(waypoints_xyz, bend_radius_m, tube_radius_m, n_theta, base_color_rgb,
                         n_bend_samples=12, cap_ends=True, specular_strength=0.0, shininess=32.0):
    """
    Convenience wrapper tying fillet_polyline + swept_tube_mesh (+ end caps)
    together - the one function most callers should reach for to render a
    real bent duct/pipe (e.g. gui/preview3d_gl.py's fuel main-inlet duct).
    Mirrors manifold_ring_mesh's role as the "do-everything" entry point
    relative to its own lower-level pieces.

    Returns a LIST of MeshBuffers (the tube body, plus one flat end-cap disk
    per open end if cap_ends=True) rather than a single merged buffer -
    matching build_shell_mesh/ShellMesh's own "list of separately-drawn
    pieces" convention instead of introducing a new merged-buffer path.
    """
    centerline_xyz, tangents_xyz = fillet_polyline(waypoints_xyz, bend_radius_m, n_bend_samples)
    normals_f, binormals_f = rotation_minimizing_frames(centerline_xyz, tangents_xyz)
    pieces = [_swept_tube_mesh_from_frames(centerline_xyz, tangents_xyz, normals_f, binormals_f,
                                            tube_radius_m, n_theta, base_color_rgb,
                                            specular_strength=specular_strength, shininess=shininess)]
    if cap_ends:
        pieces.append(_tube_end_disk(centerline_xyz[0], normals_f[0], binormals_f[0],
                                      tangents_xyz[0], tube_radius_m, n_theta, base_color_rgb,
                                      facing_sign=-1.0, specular_strength=specular_strength,
                                      shininess=shininess))
        pieces.append(_tube_end_disk(centerline_xyz[-1], normals_f[-1], binormals_f[-1],
                                      tangents_xyz[-1], tube_radius_m, n_theta, base_color_rgb,
                                      facing_sign=1.0, specular_strength=specular_strength,
                                      shininess=shininess))
    return pieces


def _frame_cylinder_mesh(start_xyz, tangent_xyz, normal_xyz, binormal_xyz, length_m, radius_m,
                         n_theta, base_color_rgb, specular_strength=0.0, shininess=32.0):
    """A straight open cylinder of `length_m` along `tangent_xyz` from
    `start_xyz`, in the given local frame - the 2-station degenerate case of
    _swept_tube_mesh_from_frames (no RMF pass needed: the frame is constant)."""
    start = np.asarray(start_xyz, dtype=float)
    t = np.asarray(tangent_xyz, dtype=float)
    centerline = np.stack([start, start + length_m * t])
    tangents = np.stack([t, t])
    normals_f = np.stack([normal_xyz, normal_xyz]).astype(float)
    binormals_f = np.stack([binormal_xyz, binormal_xyz]).astype(float)
    return _swept_tube_mesh_from_frames(centerline, tangents, normals_f, binormals_f, radius_m,
                                        n_theta, base_color_rgb,
                                        specular_strength=specular_strength, shininess=shininess)


# Pipe-flange bolt cosmetics, x the flange's own lip height / width (the
# pipe-scale analogue of hardware_constants' BOLT_HEAD_*_THROAT_DIA_MULT,
# which are engine-throat-scaled and would be absurd on a 5 cm pipe).
PIPE_FLANGE_BOLT_RADIUS_LIP_MULT = 0.22
PIPE_FLANGE_BOLT_LENGTH_WIDTH_MULT = 0.6
PIPE_FLANGE_BOLT_N_THETA = 8


def pipe_flange_pieces(center_xyz, tangent_xyz, normal_xyz, binormal_xyz, bore_radius_m,
                       lip_height_m, width_m, n_bolts, n_theta, base_color_rgb,
                       specular_strength=0.0, shininess=32.0, bolt_color_rgb=None):
    """
    A flange collar around a PIPE at an arbitrary joint: an annular ring of
    inner radius bore_radius_m (the drawn pipe's own radius), outer radius
    bore_radius_m + lip_height_m, `width_m` thick along tangent_xyz and
    centred on center_xyz, plus n_bolts small bolt heads on its +tangent
    face. The first FRAME-LOCAL hardware primitive in this package: the
    existing tilted_flange_mesh/bolt_ring_pieces are surfaces of revolution
    about the ENGINE x-axis and can't sit on a pipe pointing anywhere else,
    so this one is built from the same (tangent, normal, binormal) frame
    machinery the swept tubes use. Used by gui/mesh_builder.build_plumbing_
    pieces for physics/plumbing.py's per-joint flanges.

    Returns a list of MeshBuffers (collar side + two annular faces + one
    body and one cap per bolt), same "list of separately-drawn pieces"
    convention as bent_tube_duct_mesh. Degenerate inputs (lip or width <= 0)
    return [].
    """
    if lip_height_m <= 0.0 or width_m <= 0.0 or bore_radius_m <= 0.0:
        return []
    c = np.asarray(center_xyz, dtype=float)
    t = np.asarray(tangent_xyz, dtype=float)
    n_ = np.asarray(normal_xyz, dtype=float)
    b = np.asarray(binormal_xyz, dtype=float)
    r_out = bore_radius_m + lip_height_m
    back = c - 0.5 * width_m * t
    front = c + 0.5 * width_m * t
    kw = dict(specular_strength=specular_strength, shininess=shininess)
    pieces = [_frame_cylinder_mesh(back, t, n_, b, width_m, r_out, n_theta, base_color_rgb, **kw),
              _tube_end_disk(back, n_, b, t, r_out, n_theta, base_color_rgb, facing_sign=-1.0,
                             inner_radius_m=bore_radius_m, **kw),
              _tube_end_disk(front, n_, b, t, r_out, n_theta, base_color_rgb, facing_sign=1.0,
                             inner_radius_m=bore_radius_m, **kw)]
    if n_bolts > 0:
        bolt_r = PIPE_FLANGE_BOLT_RADIUS_LIP_MULT * lip_height_m
        bolt_len = PIPE_FLANGE_BOLT_LENGTH_WIDTH_MULT * width_m
        circle_r = bore_radius_m + 0.5 * lip_height_m
        bolt_rgb = bolt_color_rgb if bolt_color_rgb is not None else base_color_rgb
        for i in range(int(n_bolts)):
            ang = 2.0 * np.pi * i / n_bolts
            base = front + circle_r * (np.cos(ang) * n_ + np.sin(ang) * b)
            pieces.append(_frame_cylinder_mesh(base, t, n_, b, bolt_len, bolt_r,
                                               PIPE_FLANGE_BOLT_N_THETA, bolt_rgb, **kw))
            pieces.append(_tube_end_disk(base + bolt_len * t, n_, b, t, bolt_r,
                                         PIPE_FLANGE_BOLT_N_THETA, bolt_rgb, facing_sign=1.0, **kw))
    return pieces


# Straight "ray" placeholders (Shape Lab: pipe free end -> the pump it will
# feed, until real connecting pipes exist). Cosmetic-only, ASSUMPTIONS.md Tier 3.
RAY_RADIUS_TUBE_R_MULT = 0.15   # ray radius as a fraction of the pipe's tube radius
RAY_N_THETA = 8


def ray_mesh(start_xyz, end_xyz, radius_m, n_theta, base_color_rgb,
             specular_strength=0.0, shininess=32.0):
    """A thin closed cylinder from `start_xyz` to `end_xyz` (a visible
    straight line in a triangles-only renderer). Its local frame is built from
    the ray direction alone (any perpendicular serves as the normal), so it
    needs no caller-supplied frame. Returns a list of MeshBuffers (body + two
    end disks), or [] when the two points coincide or the radius is zero."""
    start = np.asarray(start_xyz, dtype=float)
    end = np.asarray(end_xyz, dtype=float)
    d = end - start
    length = float(np.linalg.norm(d))
    if length < 1e-9 or radius_m <= 0.0:
        return []
    t = d / length
    helper = np.array([0.0, 0.0, 1.0]) if abs(t[2]) < 0.9 else np.array([0.0, 1.0, 0.0])
    n = np.cross(helper, t)
    n /= np.linalg.norm(n)
    b = np.cross(t, n)
    kw = dict(specular_strength=specular_strength, shininess=shininess)
    return [_frame_cylinder_mesh(start, t, n, b, length, radius_m, n_theta, base_color_rgb, **kw),
            _tube_end_disk(start, n, b, t, radius_m, n_theta, base_color_rgb, facing_sign=-1.0, **kw),
            _tube_end_disk(end, n, b, t, radius_m, n_theta, base_color_rgb, facing_sign=1.0, **kw)]


def exhaust_nozzle_mesh(inlet_xyz, pos_xyz, dir_xyz, r_inlet_m, r_throat_m, r_exit_m,
                        converge_length_m, length_m, n_theta, base_color_rgb,
                        n_samples=16, specular_strength=0.0, shininess=32.0):
    """A small off-axis exhaust nozzle (physics/turbine_exhaust.size_hardware's
    overboard outlet) as ONE swept body: a straight inlet collar at the duct
    bore from `inlet_xyz` to `pos_xyz`, then along `dir_xyz` (possibly canted
    off the collar axis) a converging cone to the throat over
    `converge_length_m` and a diverging cone to the exit at `length_m`. Open at
    the exit (the exhaust leaves there); an end disk closes the inlet side.
    Returns [body, inlet_disk] or [] for a degenerate input."""
    a = np.asarray(inlet_xyz, dtype=float)
    p = np.asarray(pos_xyz, dtype=float)
    d = np.asarray(dir_xyz, dtype=float)
    if np.linalg.norm(d) < 1e-12 or r_inlet_m <= 0 or length_m <= 0:
        return []
    d = d / np.linalg.norm(d)
    conv = min(max(converge_length_m, 0.0), length_m)
    collar = [a + (p - a) * f for f in np.linspace(0.0, 1.0, 4)]
    s = np.linspace(0.0, length_m, n_samples + 1)[1:]
    pts = np.array(collar + [p + si * d for si in s])
    radii = [r_inlet_m] * 4
    for si in s:
        if si <= conv and conv > 0:
            radii.append(r_inlet_m + (r_throat_m - r_inlet_m) * si / conv)
        else:
            f = (si - conv) / max(length_m - conv, 1e-12)
            radii.append(r_throat_m + (r_exit_m - r_throat_m) * f)
    radii = np.asarray(radii, dtype=float)
    # drop coincident centreline points (a zero-length collar)
    keep = np.concatenate(([True], np.linalg.norm(np.diff(pts, axis=0), axis=1) > 1e-9))
    pts, radii = pts[keep], radii[keep]
    if pts.shape[0] < 2:
        return []
    tang = np.gradient(pts, axis=0)
    tang = tang / np.linalg.norm(tang, axis=1, keepdims=True)
    normals_f, binormals_f = rotation_minimizing_frames(pts, tang)
    body = _swept_tube_mesh_from_frames(pts, tang, normals_f, binormals_f, radii, n_theta,
                                        base_color_rgb, specular_strength=specular_strength,
                                        shininess=shininess)
    cap = _tube_end_disk(pts[0], normals_f[0], binormals_f[0], tang[0], float(radii[0]),
                         n_theta, base_color_rgb, facing_sign=-1.0,
                         specular_strength=specular_strength, shininess=shininess)
    return [body, cap]


def self_test():
    wp_l = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]])
    r_l = 0.3
    c_l, t_l = fillet_polyline(wp_l, r_l, n_bend_samples=20)

    # --- swept_tube_mesh / bent_tube_duct_mesh mesh invariants: vertex count,
    # constant cross-section radius at both a straight-section sample and the
    # tightest-curvature bend sample, no degenerate/zero-area triangles even
    # at a tight bend radius relative to tube radius, and correctly placed/
    # oriented end caps ---
    n_theta_tube_test = 16
    tube_r_test = 0.05
    body_mesh = swept_tube_mesh(c_l, t_l, tube_r_test, n_theta_tube_test, (0.5, 0.5, 0.5))
    n_stations_l = c_l.shape[0]
    assert body_mesh.vertices.shape == (n_theta_tube_test * n_stations_l, 3)
    verts_grid = body_mesh.vertices.reshape(n_theta_tube_test, n_stations_l, 3)
    for station_idx in (0, n_stations_l // 2, n_stations_l - 1):
        radii = np.linalg.norm(verts_grid[:, station_idx, :] - c_l[station_idx], axis=1)
        assert np.allclose(radii, tube_r_test, atol=1e-9)

    # tight bend (radius comparable to tube radius) - check for degenerate
    # (near-zero-area) triangles, which would indicate pinching/self-
    # intersection at the tightest curvature
    c_tight, t_tight = fillet_polyline(wp_l, 3.0 * tube_r_test, n_bend_samples=20)
    tight_mesh = swept_tube_mesh(c_tight, t_tight, tube_r_test, n_theta_tube_test, (0.5, 0.5, 0.5))
    tv = tight_mesh.vertices
    for a, b, cc in tight_mesh.indices:
        area2 = np.linalg.norm(np.cross(tv[b] - tv[a], tv[cc] - tv[a]))
        assert area2 > 1e-9, (a, b, cc, area2)
    print("swept_tube_mesh mesh-invariant self-check: OK")

    # per-station radius (a reducer cone): each station sits at ITS radius,
    # and on a straight cone the normals tilt back against the radius growth
    # (n . t = -dr/ds / sqrt(1 + (dr/ds)^2)).
    c_cone = np.stack([np.linspace(0.0, 1.0, 11), np.zeros(11), np.zeros(11)], axis=1)
    t_cone = np.tile([1.0, 0.0, 0.0], (11, 1))
    r_cone = np.linspace(0.10, 0.05, 11)             # dr/ds = -0.05
    cone = swept_tube_mesh(c_cone, t_cone, r_cone, n_theta_tube_test, (0.5, 0.5, 0.5))
    cv = cone.vertices.reshape(n_theta_tube_test, 11, 3)
    cn = cone.normals.reshape(n_theta_tube_test, 11, 3)
    for j in (0, 5, 10):
        assert np.allclose(np.linalg.norm(cv[:, j, 1:], axis=1), r_cone[j], atol=1e-6)
    assert np.allclose(cn[..., 0], 0.05 / np.sqrt(1.0 + 0.05 ** 2), atol=1e-5)
    print("swept_tube_mesh per-station radius (reducer) self-check: OK")

    c_duct, t_duct = fillet_polyline(wp_l, r_l)  # bent_tube_duct_mesh's own default n_bend_samples
    duct_pieces = bent_tube_duct_mesh(wp_l, r_l, tube_r_test, n_theta_tube_test, (0.5, 0.5, 0.5))
    assert len(duct_pieces) == 3  # body + 2 end caps
    body, cap0, cap1 = duct_pieces
    assert body.vertices.shape[0] == n_theta_tube_test * c_duct.shape[0]
    # each cap's own vertices sit within tube_r_test of its centerline endpoint
    for cap, end_pt, tangent_end, sign in ((cap0, c_duct[0], t_duct[0], -1.0), (cap1, c_duct[-1], t_duct[-1], 1.0)):
        cap_dists = np.linalg.norm(cap.vertices - end_pt, axis=1)
        assert np.all(cap_dists <= tube_r_test + 1e-6)  # float32 buffer round-trip tolerance
        assert np.allclose(cap.normals, sign * tangent_end, atol=1e-6)
    no_cap_pieces = bent_tube_duct_mesh(wp_l, r_l, tube_r_test, n_theta_tube_test,
                                         (0.5, 0.5, 0.5), cap_ends=False)
    assert len(no_cap_pieces) == 1
    print("bent_tube_duct_mesh end-cap self-check: OK")

    # --- per-corner bend radii (physics/plumbing.py's per-joint elbows): a
    # 3-corner path with three different radii - each arc's samples sit at
    # ITS OWN radius from its own centre, and a scalar radius still equals the
    # broadcast list ---
    wp_3 = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0],
                     [2.0, 1.0, 0.0], [2.0, 2.0, 0.0]])
    radii = [0.1, 0.25, 0.4]
    c_mix, t_mix = fillet_polyline(wp_3, radii, n_bend_samples=10)
    c_scalar, _ = fillet_polyline(wp_3, 0.25, n_bend_samples=10)
    c_bcast, _ = fillet_polyline(wp_3, [0.25, 0.25, 0.25], n_bend_samples=10)
    assert np.allclose(c_scalar, c_bcast)
    assert not np.allclose(c_mix.shape, c_scalar.shape) or not np.allclose(c_mix, c_scalar)
    # every centreline sample lies within its stated radius of one of the
    # three analytic elbow centres, or on a straight segment (colinear check)
    centres = [np.array([1.0 - r, r, 0.0]) if i == 0 else
               np.array([1.0 + r, 1.0 - r, 0.0]) if i == 1 else
               np.array([2.0 - r, 1.0 + r, 0.0]) for i, r in enumerate(radii)]
    for pt in c_mix:
        on_arc = any(np.isclose(np.linalg.norm(pt - cc), r, atol=1e-9)
                     for cc, r in zip(centres, radii))
        on_straight = (np.isclose(pt[1], 0.0) or np.isclose(pt[0], 1.0) or
                       np.isclose(pt[1], 1.0) or np.isclose(pt[0], 2.0))
        assert on_arc or on_straight, pt
    try:
        fillet_polyline(wp_3, [0.1, 0.2])
        raise AssertionError("expected a length mismatch ValueError")
    except ValueError:
        pass
    print("fillet_polyline per-corner radii self-check: OK")

    # --- pipe_flange_pieces: collar + 2 annular faces + bolts, all vertices
    # within bore+lip (collar) / bore+lip+bolt reach (bolts) of the joint
    # centre's axis, face normals = +/-tangent, works on an off-axis frame ---
    t_f = np.array([0.0, 0.6, 0.8])
    n_f = np.array([1.0, 0.0, 0.0])
    b_f = np.cross(t_f, n_f)
    centre = np.array([0.3, -0.2, 0.5])
    bore, lip, width = 0.05, 0.015, 0.008
    fl = pipe_flange_pieces(centre, t_f, n_f, b_f, bore, lip, width, 6, 24, (0.5, 0.5, 0.52))
    assert len(fl) == 3 + 2 * 6
    for piece in fl:
        assert not np.any(np.isnan(piece.vertices)) and not np.any(np.isnan(piece.normals))
    collar, face_back, face_front = fl[:3]
    rel = collar.vertices - centre
    radial = np.linalg.norm(rel - np.outer(rel @ t_f, t_f), axis=1)
    assert np.allclose(radial, bore + lip, atol=1e-6)
    axial = rel @ t_f
    assert np.allclose(np.abs(axial), 0.5 * width, atol=1e-6)
    assert np.allclose(face_back.normals, -t_f, atol=1e-6)
    assert np.allclose(face_front.normals, t_f, atol=1e-6)
    rf = np.linalg.norm((face_front.vertices - centre)
                        - np.outer((face_front.vertices - centre) @ t_f, t_f), axis=1)
    assert np.isclose(rf.min(), bore, atol=1e-6) and np.isclose(rf.max(), bore + lip, atol=1e-6)
    for bolt_piece in fl[3:]:
        ax = (bolt_piece.vertices - centre) @ t_f
        assert np.all(ax >= 0.5 * width - 1e-6)
    assert pipe_flange_pieces(centre, t_f, n_f, b_f, bore, 0.0, width, 6, 24, (0.5, 0.5, 0.5)) == []
    assert len(pipe_flange_pieces(centre, t_f, n_f, b_f, bore, lip, width, 0, 24, (0.5, 0.5, 0.5))) == 3
    print("pipe_flange_pieces self-check: OK")

    # ray_mesh: body spans exactly start->end, every wall vertex is `radius`
    # off the ray line, end disks sit at the endpoints, any direction works
    # (incl. the z-parallel case that swaps the helper axis); degenerate -> []
    p0, p1 = np.array([0.1, -0.2, 0.3]), np.array([0.7, 0.4, -0.1])
    for a, c in ((p0, p1), (p0, p0 + np.array([0.0, 0.0, 0.5]))):
        ray = ray_mesh(a, c, 0.01, 8, (0.9, 0.3, 0.2))
        assert len(ray) == 3
        d = (c - a) / np.linalg.norm(c - a)
        ax = (ray[0].vertices - a) @ d
        tol = 1e-6  # MeshBuffers stores float32
        assert np.isclose(ax.min(), 0.0, atol=tol) and np.isclose(ax.max(), np.linalg.norm(c - a), atol=tol)
        off = (ray[0].vertices - a) - np.outer(ax, d)
        assert np.allclose(np.linalg.norm(off, axis=1), 0.01, atol=tol)
        assert np.allclose(ray[1].vertices @ d, a @ d, atol=tol)
        assert np.allclose(ray[2].vertices @ d, c @ d, atol=tol)
        for piece in ray:
            assert not np.any(np.isnan(piece.normals))
    assert ray_mesh(p0, p0, 0.01, 8, (0.9, 0.3, 0.2)) == []
    assert ray_mesh(p0, p1, 0.0, 8, (0.9, 0.3, 0.2)) == []
    print("ray_mesh self-check: OK")

    # exhaust_nozzle_mesh: collar at the inlet bore, throat, then the exit
    # radius at `length` along a canted axis; open exit, one inlet disk
    a0, p0_ = np.array([0.9, 0.5, 0.0]), np.array([1.0, 0.5, 0.0])
    dcant = np.array([np.cos(0.2), np.sin(0.2), 0.0])
    en = exhaust_nozzle_mesh(a0, p0_, dcant, 0.05, 0.03, 0.06, 0.02, 0.2, 16, (0.5, 0.4, 0.4))
    assert len(en) == 2
    v = en[0].vertices.reshape(16, -1, 3)
    far = v[:, -1, :]                                  # exit ring
    assert np.allclose(np.linalg.norm(far - (p0_ + 0.2 * dcant), axis=1), 0.06, atol=1e-5)
    near = v[:, 0, :]                                  # collar start
    assert np.allclose(np.linalg.norm(near - a0, axis=1), 0.05, atol=1e-5)
    assert not np.any(np.isnan(en[0].normals))
    assert exhaust_nozzle_mesh(a0, p0_, np.zeros(3), 0.05, 0.03, 0.06, 0.02, 0.2, 16,
                               (0.5, 0.4, 0.4)) == []
    print("exhaust_nozzle_mesh self-check: OK")
    print("ALL DUCT_MESHES CHECKS OK")


if __name__ == "__main__":
    self_test()
