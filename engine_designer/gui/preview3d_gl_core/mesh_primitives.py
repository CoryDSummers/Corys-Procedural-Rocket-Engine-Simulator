"""
Generic mesh-buffer primitives for the OpenGL 3D preview: the flattened
GL-ready MeshBuffers dataclass, the (n_theta, n_stations) grid triangulation/
buffer-building helpers, and the small decorative hardware mesh builders
(end caps, flanges, manifold rings, bolt rings) built on top of them. Split
out of the former single-file gui/preview3d_gl_core.py by geometry-operation
kind - see this package's __init__.py for the overview. No OpenGL/Tk import,
pure numpy.
"""
from dataclasses import dataclass

import numpy as np

from ...physics import geometry3d
from .profile_geometry import meridian_normals

@dataclass
class MeshBuffers:
    """Flattened GL-ready buffers for one revolved mesh piece."""
    vertices: np.ndarray  # (N, 3) float32
    normals: np.ndarray   # (N, 3) float32, unit length
    colors: np.ndarray    # (N, 3) float32, 0..1
    indices: np.ndarray   # (M, 3) uint32
    specular_strength: float = 0.0  # Blinn-Phong highlight strength (0..1), one value
                                     # for the whole piece (like base_color_rgb) - cosmetic/
                                     # rendering only, no physics meaning. 0.0 default keeps
                                     # today's pure-Lambertian look for any caller that
                                     # doesn't pass a material-derived value explicitly.
    shininess: float = 32.0         # Blinn-Phong exponent - cosmetic/rendering only
    role: str = ""                  # which engine part this piece is ("wall", "turbopump",
                                     # ...), stamped by mesh_builder.build_mesh_data; "" =
                                     # untagged. Picks the render layer (render_layers.py).

def triangulate_grid(n_theta, n_stations):
    """
    Index buffer for the structured (n_theta, n_stations) grid revolve_profile/
    turbopump_assembly_meshes return, flattened row-major as idx(i,j) =
    i*n_stations + j. theta = linspace(0, 2pi, n_theta) is endpoint=True, so
    row 0 and row n_theta-1 are already spatially coincident (the seam is a
    duplicate vertex row) - a plain open-grid triangulation covers the closed
    surface exactly once, no wraparound/modulo indexing needed.
    """
    if n_theta < 2 or n_stations < 2:
        return np.zeros((0, 3), dtype=np.uint32)
    i, j = np.meshgrid(np.arange(n_theta - 1), np.arange(n_stations - 1), indexing="ij")
    i = i.ravel()
    j = j.ravel()

    def idx(ii, jj):
        return (ii * n_stations + jj).astype(np.uint32)

    v00 = idx(i, j)
    v10 = idx(i + 1, j)
    v01 = idx(i, j + 1)
    v11 = idx(i + 1, j + 1)
    tri_a = np.stack([v00, v10, v11], axis=1)
    tri_b = np.stack([v00, v11, v01], axis=1)
    return np.concatenate([tri_a, tri_b], axis=0).astype(np.uint32)

def mesh_from_grid(X, Y, Z, base_color_rgb, colors_per_station=None, normals=None,
                    specular_strength=0.0, shininess=32.0):
    """
    Generic (n_theta, n_stations)-meshgrid-to-MeshBuffers builder, shared by
    revolve_to_buffers (analytic meridian normals) and decorative hardware
    meshes built from geometry3d.capped_cylinder/turbopump_assembly_meshes,
    which reuse the exact same meshgrid shape convention (built the same way,
    via meshgrid(x_stations, theta)) but aren't a full profile revolution.
    When `normals` isn't supplied, falls back to a radial-normal
    approximation (0, y, z)/|.| - correct for cylindrical side walls, only
    approximate at flat end caps, acceptable for small decorative hardware
    pieces that never carry the heat-flux overlay (that path always goes
    through revolve_to_buffers's analytic normals instead).
    """
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    Z = np.asarray(Z, dtype=float)
    n_theta, n_stations = X.shape
    vertices = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1).astype(np.float32)

    if normals is None:
        r = np.sqrt(Y ** 2 + Z ** 2)
        r_safe = np.where(r > 1e-12, r, 1.0)
        normals = np.stack([np.zeros_like(X).ravel(), (Y / r_safe).ravel(),
                             (Z / r_safe).ravel()], axis=1).astype(np.float32)
    else:
        normals = np.asarray(normals, dtype=np.float32)

    if colors_per_station is not None:
        colors_per_station = np.asarray(colors_per_station, dtype=np.float32)
        colors = np.broadcast_to(colors_per_station, (n_theta, n_stations, 3)).reshape(-1, 3)
        colors = np.ascontiguousarray(colors, dtype=np.float32)
    else:
        base = np.asarray(base_color_rgb, dtype=np.float32)
        colors = np.tile(base, (n_theta * n_stations, 1)).astype(np.float32)

    indices = triangulate_grid(n_theta, n_stations)
    return MeshBuffers(vertices=vertices, normals=normals, colors=colors, indices=indices,
                        specular_strength=specular_strength, shininess=shininess)

def revolve_to_buffers(xs_m, rs_m, n_theta, base_color_rgb, colors_per_station=None,
                        flip_orientation=False, specular_strength=0.0, shininess=32.0):
    """
    Wrap geometry3d.revolve_profile + meridian_normals into one flattened
    MeshBuffers ready for glDrawElements. colors_per_station, if given, is
    shape (len(xs_m), 3) and is broadcast across all n_theta rings (heat-flux
    overlay mode); otherwise every vertex gets base_color_rgb (flat material
    color, today's default look).

    flip_orientation=False (default) preserves every prior call's behavior
    bit-for-bit: normals point radially outward, winding matches
    triangulate_grid's own outward-normal convention. flip_orientation=True
    negates the normals and reverses each triangle's winding - for the INNER
    (gas-side) surface of a solid shell (build_shell_mesh below), which
    should face into the bore rather than out of it.
    """
    xs_m = np.asarray(xs_m, dtype=float)
    rs_m = np.asarray(rs_m, dtype=float)
    X, Y, Z = geometry3d.revolve_profile(xs_m, rs_m, n_theta)

    n_x, n_r = meridian_normals(xs_m, rs_m)
    theta = np.linspace(0.0, 2.0 * np.pi, n_theta)
    Nx, Theta = np.meshgrid(n_x, theta)
    Nr, _ = np.meshgrid(n_r, theta)
    Ny = Nr * np.cos(Theta)
    Nz = Nr * np.sin(Theta)
    normals = np.stack([Nx.ravel(), Ny.ravel(), Nz.ravel()], axis=1).astype(np.float32)

    mesh = mesh_from_grid(X, Y, Z, base_color_rgb, colors_per_station, normals=normals,
                           specular_strength=specular_strength, shininess=shininess)
    if flip_orientation:
        mesh.normals = -mesh.normals
        mesh.indices = mesh.indices[:, [0, 2, 1]]
    return mesh

def end_cap_ring(x_m, r_inner_m, r_outer_m, n_theta, base_color_rgb, facing_sign=1.0,
                  specular_strength=0.0, shininess=32.0):
    """
    A flat annulus at fixed x, bridging r_inner_m (inner/gas-side wall) to
    r_outer_m (outer wall) - the piece neither revolve_profile (r depends on
    x only) nor triangulate_grid's caller-agnostic index buffer can build on
    their own, since here r varies at ONE fixed x. Used to close a solid
    shell's open ends (build_shell_mesh's cap_start/cap_end).

    facing_sign=+1 orients the front face toward +x, -1 toward -x - whichever
    way the cap's visible side should point. Determined empirically (via the
    first triangle's actual cross-product face normal) rather than assumed
    from triangulate_grid's convention, so it's correct regardless of that
    convention's details.
    """
    theta = np.linspace(0.0, 2.0 * np.pi, n_theta)
    rad = np.array([r_inner_m, r_outer_m])
    X, Theta = np.meshgrid(np.full(2, float(x_m)), theta)
    R, _ = np.meshgrid(rad, theta)
    Y = R * np.cos(Theta)
    Z = R * np.sin(Theta)
    normal = np.array([facing_sign, 0.0, 0.0], dtype=np.float32)
    normals = np.tile(normal, (n_theta * 2, 1))
    mesh = mesh_from_grid(X, Y, Z, base_color_rgb, normals=normals,
                           specular_strength=specular_strength, shininess=shininess)

    if mesh.indices.shape[0] > 0:
        p0, p1, p2 = mesh.vertices[mesh.indices[0]]
        face_normal = np.cross(p1 - p0, p2 - p0)
        if np.dot(face_normal, normal) < 0.0:
            mesh.indices = mesh.indices[:, [0, 2, 1]]
    return mesh

def _tube_end_disk(center_xyz, normal_xyz, binormal_xyz, tangent_xyz, radius_m, n_theta,
                    base_color_rgb, facing_sign=1.0, specular_strength=0.0, shininess=32.0,
                    inner_radius_m=0.0):
    """
    A flat filled disk closing one end of a bent_tube_duct_mesh tube -
    generalizes tube_end_cap_disk's "2-column grid, r=0 degenerates to a fan"
    construction (same degenerate-grid triangulation trick, no new
    triangulation code) from that function's fixed world-x-axis frame to an
    arbitrary local (tangent, normal, binormal) frame, since a swept-tube
    end's outward direction is the path's own local tangent, not necessarily
    the world x-axis. inner_radius_m > 0 makes it an annulus instead (the
    faces of duct_meshes.pipe_flange_pieces' collar) - same 2-column grid,
    just no longer degenerate at the inner column.
    """
    phi = np.linspace(0.0, 2.0 * np.pi, n_theta)
    rad = np.array([inner_radius_m, radius_m])
    Rad, Phi = np.meshgrid(rad, phi)  # shape (n_theta, 2)
    offset = (Rad * np.cos(Phi))[..., None] * normal_xyz + (Rad * np.sin(Phi))[..., None] * binormal_xyz
    pts = np.asarray(center_xyz, dtype=float) + offset
    X, Y, Z = pts[..., 0], pts[..., 1], pts[..., 2]
    normal_dir = (facing_sign * np.asarray(tangent_xyz, dtype=float)).astype(np.float32)
    normals = np.tile(normal_dir, (n_theta * 2, 1))
    mesh = mesh_from_grid(X, Y, Z, base_color_rgb, normals=normals,
                           specular_strength=specular_strength, shininess=shininess)

    if mesh.indices.shape[0] > 0:
        p0, p1, p2 = mesh.vertices[mesh.indices[0]]
        face_normal = np.cross(p1 - p0, p2 - p0)
        if np.dot(face_normal, normal_dir) < 0.0:
            mesh.indices = mesh.indices[:, [0, 2, 1]]
    return mesh

def manifold_ring_mesh(x0_m, center_r_m, tube_r_m, n_theta_main, n_theta_tube, base_color_rgb,
                        specular_strength=0.0, shininess=32.0):
    """
    A torus (donut) - the coolant-manifold ring hardware where the tube
    bundle's inlet/outlet collects. A small circular cross-section (radius
    tube_r_m) is swept in a full circle of radius center_r_m around the
    MAIN engine axis at fixed x0_m.

    `tube_r_m` / `center_r_m` may each be a scalar (a constant-section torus,
    the original case) or an array of length n_theta_main giving the value at
    each u = linspace(0, 2pi, n_theta_main) station - a TAPERED ring
    (physics/manifold.py's split/tapered header: biggest at its inlet,
    shrinking round each branch), with the centreline free to follow the
    taper so the ring's inner edge stays flush on the wall. Normals then come
    from the exact surface tangents dP/du x dP/dv (slope-corrected for
    r'(u)/c'(u)), oriented to agree with the constant-section outward normal.

    Both sweep axes (u: around the main engine axis, v: the manifold's own
    tube cross-section) are built as linspace(0, 2pi, n, endpoint=True), so
    triangulate_grid's existing duplicate-seam-vertex convention (already
    relied on for the theta axis everywhere else in this file) closes BOTH
    axes with no wraparound code needed - triangulate_grid's index logic
    (idx(ii,jj) = ii*n_stations+jj) is fully symmetric in its two axes and
    never treats either specially; see this file's __main__ self-check for
    the position-deduped edge-sharing proof that the result is watertight.
    Array inputs must repeat their first value at the last station (the
    duplicate seam) for that closure to hold - a caller sampling a periodic
    function of u gets this for free.
    """
    u = np.linspace(0.0, 2.0 * np.pi, n_theta_main)   # around the MAIN engine axis
    v = np.linspace(0.0, 2.0 * np.pi, n_theta_tube)   # the manifold's own cross-section
    U, V = np.meshgrid(u, v, indexing="ij")           # both shape (n_theta_main, n_theta_tube)

    tube_arr = np.broadcast_to(np.asarray(tube_r_m, dtype=float), (n_theta_main,))
    ctr_arr = np.broadcast_to(np.asarray(center_r_m, dtype=float), (n_theta_main,))
    Rt = tube_arr[:, None]
    Rc = ctr_arr[:, None]

    R = Rc + Rt * np.cos(V)
    X = x0_m + Rt * np.sin(V)
    Y = R * np.cos(U)
    Z = R * np.sin(U)

    Nx = np.sin(V)
    Ny = np.cos(V) * np.cos(U)
    Nz = np.cos(V) * np.sin(U)
    if np.ndim(tube_r_m) or np.ndim(center_r_m):
        # Periodic central differences (row n-1 duplicates row 0).
        m = max(n_theta_main - 1, 1)
        idx = np.arange(n_theta_main)
        du = 2.0 * (2.0 * np.pi / m)
        d_rt = ((tube_arr[(idx + 1) % m] - tube_arr[(idx - 1) % m]) / du)[:, None]
        d_rc = ((ctr_arr[(idx + 1) % m] - ctr_arr[(idx - 1) % m]) / du)[:, None]
        dR_du = d_rc + d_rt * np.cos(V)
        Pu = np.stack([d_rt * np.sin(V),
                       dR_du * np.cos(U) - R * np.sin(U),
                       dR_du * np.sin(U) + R * np.cos(U)], axis=-1)
        Pv = np.stack([Rt * np.cos(V),
                       -Rt * np.sin(V) * np.cos(U),
                       -Rt * np.sin(V) * np.sin(U)], axis=-1)
        n = np.cross(Pu, Pv)
        n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-15)
        n0 = np.stack([Nx, Ny, Nz], axis=-1)
        n = np.where(np.sum(n * n0, axis=-1, keepdims=True) < 0.0, -n, n)
        Nx, Ny, Nz = n[..., 0], n[..., 1], n[..., 2]
    normals_flat = np.stack([Nx.ravel(), Ny.ravel(), Nz.ravel()], axis=1).astype(np.float32)
    return mesh_from_grid(X, Y, Z, base_color_rgb, normals=normals_flat,
                           specular_strength=specular_strength, shininess=shininess)

def tilted_flange_mesh(base_xs_m, base_rs_m, normal, height_m,
                        n_theta, base_color_rgb, specular_strength=0.0, shininess=32.0):
    """
    A small flange/washer plate, TILTED to sit perpendicular to the local
    bell surface (`normal`) rather than perpendicular to the engine's
    centerline - unlike a structural_bumps bump (physics/geometry3d.
    axial_bump_delta_r), which can only add pure RADIUS at each x-station,
    correct for a cylindrical section but wrong for a diverging bell whose
    local surface is tilted at the cone/bell half-angle.

    `base_xs_m`/`base_rs_m` (>=2 points, ordered from one edge of the
    flange's span to the other) is the flange's BASE edge - normally built
    by the caller via sample_profile_segment against the real rendered
    body/extension outer profile, so it sits EXACTLY on the real (possibly
    curved, possibly kinked at the body/extension joint) wall, not an
    idealized straight chord between the two endpoints. That distinction
    matters: a straight chord between two points on a curved wall generally
    does NOT touch the wall in between, leaving a gap that reads as "part
    of the flange floating" - snapping the base to the real piecewise-
    linear data (the same segments the wall mesh itself draws) eliminates
    that gap by construction, for any number of intermediate stations.

    `tangent = (normal[1], -normal[0])` is derived from `normal` and used
    only for the two small end-cap faces at the flange's edges - fine as a
    single shared direction since those are thin end-caps, not the load-
    bearing surface-matching fix (that's the base/underside, see below).

    Raised OD edge: `od_pts = base_pts + height_m * normal` (all M base
    points offset by the SAME shared tilt normal - a straight parallel
    offset, so the OD rim's outward face is exactly `normal` for every
    segment, no per-segment variation needed).

    OPEN strip (M-1 segments on the OD rim, plus 2 end caps), walking:
    base[0] -> od[0] (leading cap, normal -tangent) -> od[0..M-1] (OD rim,
    normal +normal per segment) -> base[M-1] (trailing cap, normal
    +tangent). Deliberately NO underside face closing back from base[M-1]
    to base[0]: since `base_xs_m`/`base_rs_m` now sit EXACTLY on the real
    rendered wall (see above), a closed underside there would be coincident,
    redundant geometry - the shell mesh already draws that exact surface -
    which is the textbook setup for Z-fighting (the depth buffer can't
    consistently pick a winner between two triangulated surfaces occupying
    the identical position, so the render flickers/patches at the seam,
    worsened by the shading mismatch between this mesh's FLAT per-face
    normals and the shell's SMOOTH per-station ones). Leaving the strip open
    shows the real, already-drawn wall through where the underside would
    have been - visually identical, since it's the same surface either way -
    without the duplicate geometry. This is safe specifically because the
    base is now exact: an earlier round DID need a closed underside, back
    when the base was an idealized straight chord that didn't actually touch
    the real (curved/kinked) wall in between, so an open strip exposed a
    genuinely different surface underneath - that's no longer the case.

    Every corner is FLAT-shaded (each face gets its own constant normal via
    duplicated vertices, no blending across corners) - a real machined
    flange has sharp edges, and smooth-blended normals across a sharp corner
    render as a rounded/circular highlight even though the underlying
    geometry is a crisp rectangle. For M=2 (no native stations fall inside
    the span - the common case when the flange's own width is narrower than
    native station spacing) this is a 6-station open strip.

    Returns a single MeshBuffers, or None if height_m <= 0 or fewer than 2
    base points are given.
    """
    base_xs_m = np.asarray(base_xs_m, dtype=float)
    base_rs_m = np.asarray(base_rs_m, dtype=float)
    if height_m <= 0 or base_xs_m.size < 2:
        return None
    n_x, n_r = normal
    t_x, t_r = (normal[1], -normal[0])
    base_pts = np.stack([base_xs_m, base_rs_m], axis=1)  # (M, 2)
    od_pts = base_pts + height_m * np.array([n_x, n_r])
    m = base_pts.shape[0]

    stations = [base_pts[0], od_pts[0]]
    station_normals = [(-t_x, -t_r), (-t_x, -t_r)]
    for i in range(m - 1):
        stations += [od_pts[i], od_pts[i + 1]]
        station_normals += [(n_x, n_r), (n_x, n_r)]
    stations += [od_pts[-1], base_pts[-1]]
    station_normals += [(t_x, t_r), (t_x, t_r)]

    stations = np.stack(stations, axis=0)
    station_normals = np.array(station_normals)
    xs = stations[:, 0]
    rs = stations[:, 1]

    theta = np.linspace(0.0, 2.0 * np.pi, n_theta)
    X, Theta = np.meshgrid(xs, theta)
    R, _ = np.meshgrid(rs, theta)
    Y = R * np.cos(Theta)
    Z = R * np.sin(Theta)
    Nx_m, ThetaN = np.meshgrid(station_normals[:, 0], theta)
    Nr_m, _ = np.meshgrid(station_normals[:, 1], theta)
    Ny = Nr_m * np.cos(ThetaN)
    Nz = Nr_m * np.sin(ThetaN)
    normals = np.stack([Nx_m.ravel(), Ny.ravel(), Nz.ravel()], axis=1).astype(np.float32)

    return mesh_from_grid(X, Y, Z, base_color_rgb, normals=normals,
                           specular_strength=specular_strength, shininess=shininess)

def bolt_ring_pieces(x_center_m, base_r_m, n_bolts, bolt_radius_m, bolt_length_m,
                      n_theta_cyl, base_color_rgb, specular_strength=0.0, shininess=32.0,
                      tangent=(1.0, 0.0), normal=(0.0, 1.0)):
    """
    N discrete short cylindrical "bolt head" solids evenly spaced around theta
    at fixed x_center_m, each protruding along `normal` (default: purely
    radially outward) from base_r_m to base_r_m + bolt_length_m - the
    bolted-flange-joint detail (many small fasteners studding a flange
    collar, per a real chamber/nozzle-extension joint reference photo).
    Follows the same "separate discrete mesh, not baked into the offset
    envelope" pattern already used for the tube hatbands: a theta-dependent
    detail can't be represented by axial_bump_delta_r's theta-invariant bump.

    `tangent`/`normal` are perpendicular unit vectors in the (x, r) meridian
    plane (the SAME pair tilted_flange_mesh takes) - passing the flange's
    own tangent/normal here makes the bolts protrude from the flange's own
    tilted face ("on top of" it) instead of pure radius. The defaults
    `tangent=(1,0), normal=(0,1)` reproduce the original pure-radial-
    protrusion behavior exactly (this module's own hardcoded case before
    this generalization).

    Each bolt is a short capped cylinder built directly in this function
    (not via geometry3d.capped_cylinder - see below) with its length axis
    n_hat = (normal[0], normal[1]*cos theta_i, normal[1]*sin theta_i) - the
    SAME rotated-normal direction used for `tilted_flange_mesh`'s own tilt,
    evaluated at this bolt's own theta_i, so each bolt's protrusion is
    perpendicular to the flange's local face at its own azimuthal position
    (the physically-correct behavior for a bolt ring on a surface of
    revolution - confirmed against a real-photo reference and by explicit
    user sign-off after an earlier round wrongly reverted this to pure
    radial). Its round cross-section spans t_hat (rotated `tangent`) and
    c_hat = (0, -sin theta_i, cos theta_i) (pure circumferential); all three
    stay mutually orthonormal for any theta_i by the same proof as
    tilted_flange_mesh's tangent/normal rotation.

    Built as 6 stations, not capped_cylinder's 4: the rim (radius=
    bolt_radius_m) is DUPLICATED at each end so the flat base/tip cap fans
    and the round wall strip each get their own constant-vs-lateral shading
    normal, instead of sharing one vertex (and one compromise normal)
    between faces that should be shaded differently. Without this, the cap
    faces - especially the tip, the one part of the bolt that should
    visibly read as "pointing straight out along the flange's normal" - get
    shaded with the wall's lateral/radial normal instead, so the whole bolt
    visually reads as wrapped around the ring rather than clearly
    protruding (the bug an earlier round's user report - bolts "extending
    circularly along the x,y axis" - was actually describing: the geometry/
    positions were already correct, only the cap shading was wrong). Same
    "duplicate vertices at a hard edge for flat shading" technique as
    tilted_flange_mesh's corners.

    Returns a list of MeshBuffers, one per bolt (mirrors tube_bundle_pieces's
    "list of discrete pieces" convention).
    """
    if n_bolts <= 0 or bolt_radius_m <= 0 or bolt_length_m <= 0:
        return []
    n_x, n_r = normal
    t_x, t_r = tangent
    phi = np.linspace(0.0, 2.0 * np.pi, n_theta_cyl)
    cos_phi = np.cos(phi)
    sin_phi = np.sin(phi)
    # 6 stations (not capped_cylinder's 4): the rim (radius=bolt_radius_m) is
    # DUPLICATED at each end so the flat cap fan and the round wall strip each
    # get their own constant-vs-lateral normal, instead of sharing one vertex
    # (and one compromise normal) between two faces that should be shaded
    # differently - same "duplicate at the hard edge" technique as
    # tilted_flange_mesh's corners. Without this, the cap faces - especially
    # the tip, the one part of the bolt that should visibly read as "pointing
    # straight out along the flange's normal" - get shaded with the wall's
    # lateral/radial normal instead, so the whole bolt reads as wrapped
    # around the ring (dominated by the tangent/circumferential directions)
    # rather than clearly protruding.
    s_vals = np.array([0.0, 0.0, 0.0, bolt_length_m, bolt_length_m, bolt_length_m])
    rad_vals = np.array([0.0, bolt_radius_m, bolt_radius_m, bolt_radius_m, bolt_radius_m, 0.0])

    pieces = []
    for i in range(n_bolts):
        theta_i = 2.0 * np.pi * i / n_bolts
        cos_i, sin_i = np.cos(theta_i), np.sin(theta_i)

        n_hat = np.array([n_x, n_r * cos_i, n_r * sin_i])
        t_hat = np.array([t_x, t_r * cos_i, t_r * sin_i])
        c_hat = np.array([0.0, -sin_i, cos_i])
        base_center = np.array([x_center_m, base_r_m * cos_i, base_r_m * sin_i])

        u = np.outer(cos_phi, t_hat) + np.outer(sin_phi, c_hat)  # (n_theta_cyl, 3)

        pos = (base_center[None, None, :]
               + s_vals[None, :, None] * n_hat[None, None, :]
               + rad_vals[None, :, None] * u[:, None, :])  # (n_theta_cyl, 6, 3)

        norm = np.empty_like(pos)
        norm[:, 0, :] = -n_hat
        norm[:, 1, :] = -n_hat
        norm[:, 2, :] = u
        norm[:, 3, :] = u
        norm[:, 4, :] = n_hat
        norm[:, 5, :] = n_hat

        Xg = pos[:, :, 0]
        Yg = pos[:, :, 1]
        Zg = pos[:, :, 2]
        normals = norm.reshape(-1, 3).astype(np.float32)

        pieces.append(mesh_from_grid(Xg, Yg, Zg, base_color_rgb, normals=normals,
                                      specular_strength=specular_strength, shininess=shininess))
    return pieces

def revolve_closed_section(section_xs_m, section_rs_m, n_theta, base_color_rgb,
                           specular_strength=0.0, shininess=32.0):
    """
    Revolve a CLOSED meridian-plane polygon (x, r) about the engine axis - a solid
    ring of arbitrary cross-section (a hat/tee/channel/box retaining band, a
    shell sleeve). revolve_to_buffers can't do this: its analytic normals assume
    r is a function of x. Here each polygon edge becomes its own revolved
    2-station strip with a FLAT per-edge normal (the outward edge normal in the
    meridian plane, from the polygon's own orientation), so section corners stay
    crisp; all strips are concatenated into one MeshBuffers. Zero-length edges
    (e.g. a keyhole slit's shared vertex) are skipped; the slit itself becomes
    two coincident, opposite-facing strips inside the section, which never show.
    """
    px = np.asarray(section_xs_m, dtype=float)
    pr = np.asarray(section_rs_m, dtype=float)
    n = px.size
    area2 = float(np.sum(px * np.roll(pr, -1) - np.roll(px, -1) * pr))
    orient = 1.0 if area2 >= 0 else -1.0       # +1: counter-clockwise in (x, r)
    theta = np.linspace(0.0, 2.0 * np.pi, n_theta)
    verts, norms, idxs = [], [], []
    base = 0
    tri = triangulate_grid(n_theta, 2)
    for k in range(n):
        x0, r0, x1, r1 = px[k], pr[k], px[(k + 1) % n], pr[(k + 1) % n]
        dx, dr = x1 - x0, r1 - r0
        length = np.hypot(dx, dr)
        if length < 1e-12:
            continue
        # outward normal of a CCW polygon edge is (dr, -dx)/L in (x, r)
        nx, nr = orient * dr / length, -orient * dx / length
        Xs = np.array([x0, x1])
        Rs = np.array([r0, r1])
        X, Th = np.meshgrid(Xs, theta)
        R, _ = np.meshgrid(Rs, theta)
        Y, Z = R * np.cos(Th), R * np.sin(Th)
        N = np.stack([np.full(X.size, nx), (nr * np.cos(Th)).ravel(), (nr * np.sin(Th)).ravel()],
                     axis=1)
        V = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
        t = tri.copy()
        # fix winding so the face normal agrees with the edge normal
        a, b, c = V[t[0, 0]], V[t[0, 1]], V[t[0, 2]]
        fn = np.cross(b - a, c - a)
        if np.linalg.norm(fn) < 1e-18 and t.shape[0] > 1:
            a, b, c = V[t[1, 0]], V[t[1, 1]], V[t[1, 2]]
            fn = np.cross(b - a, c - a)
        mid = (a + b + c) / 3.0
        rr = np.hypot(mid[1], mid[2])
        n_mid = np.array([nx, nr * mid[1] / max(rr, 1e-12), nr * mid[2] / max(rr, 1e-12)])
        if np.dot(fn, n_mid) < 0.0:
            t = t[:, [0, 2, 1]]
        verts.append(V)
        norms.append(N)
        idxs.append(t + base)
        base += V.shape[0]
    if not verts:
        empty = np.zeros((0, 3), dtype=np.float32)
        return MeshBuffers(empty, empty, empty, np.zeros((0, 3), dtype=np.uint32),
                           specular_strength=specular_strength, shininess=shininess)
    V = np.concatenate(verts).astype(np.float32)
    N = np.concatenate(norms).astype(np.float32)
    colors = np.tile(np.asarray(base_color_rgb, dtype=np.float32), (V.shape[0], 1))
    return MeshBuffers(V, N, colors, np.concatenate(idxs).astype(np.uint32),
                       specular_strength=specular_strength, shininess=shininess)

def grid_vertex_normals(X, Y, Z):
    """
    Per-vertex smooth-shading normal for a structured (n_theta, n_stations)
    grid whose radius can vary with BOTH indices (unlike meridian_normals,
    which only handles the r(x)-only surface-of-revolution case): central-
    difference tangents along both grid axes, cross-producted, then oriented
    outward.

    The station axis (j) is OPEN (one-sided differences at the two ends).
    The theta axis (i) is PERIODIC, with row 0 and row n_theta-1 as literal
    duplicate points (triangulate_grid's own convention, from
    theta = linspace(0, 2pi, n_theta, endpoint=True)) - so neighbors there are
    taken mod (n_theta - 1), not a naive np.roll across all n_theta rows,
    which would difference against the coincident duplicate point itself and
    collapse the tangent (and the shading) right at the seam.
    """
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    Z = np.asarray(Z, dtype=float)
    n_theta, n_stations = X.shape
    P = np.stack([X, Y, Z], axis=-1)  # (n_theta, n_stations, 3)

    m = max(n_theta - 1, 1)  # periodic period; row m == row 0 by construction
    idx = np.arange(n_theta)
    ip1 = (idx + 1) % m
    im1 = (idx - 1) % m
    t_theta = P[ip1, :, :] - P[im1, :, :]

    t_station = np.zeros_like(P)
    if n_stations >= 2:
        t_station[:, 1:-1, :] = P[:, 2:, :] - P[:, :-2, :]
        t_station[:, 0, :] = P[:, 1, :] - P[:, 0, :]
        t_station[:, -1, :] = P[:, -1, :] - P[:, -2, :]

    normals = np.cross(t_station, t_theta)
    norm = np.linalg.norm(normals, axis=-1, keepdims=True)
    norm_safe = np.where(norm > 1e-15, norm, 1.0)
    normals = normals / norm_safe

    r = np.sqrt(Y ** 2 + Z ** 2)
    r_safe = np.where(r > 1e-12, r, 1.0)
    radial = np.stack([np.zeros_like(Y), Y / r_safe, Z / r_safe], axis=-1)
    flip = np.sum(normals * radial, axis=-1, keepdims=True) < 0.0
    normals = np.where(flip, -normals, normals)
    return normals.astype(np.float32)


def self_test():
    # --- triangulate_grid: index count + EMPIRICAL winding check (a synthetic
    # cylinder's every triangle's face normal, via cross(p1-p0, p2-p0), must
    # dot positive with the radial-outward direction at its centroid) ---
    xs_cyl = np.linspace(0.0, 1.0, 5)
    rs_cyl = np.full_like(xs_cyl, 0.5)
    n_theta = 8
    X, Y, Z = geometry3d.revolve_profile(xs_cyl, rs_cyl, n_theta)
    verts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
    tris = triangulate_grid(n_theta, xs_cyl.size)
    assert tris.shape == (2 * (n_theta - 1) * (xs_cyl.size - 1), 3)
    assert tris.max() < verts.shape[0]
    for a, b, c in tris:
        pa, pb, pc = verts[a], verts[b], verts[c]
        normal = np.cross(pb - pa, pc - pa)
        centroid = (pa + pb + pc) / 3.0
        outward = np.array([0.0, centroid[1], centroid[2]])
        outward = outward / (np.linalg.norm(outward) + 1e-12)
        assert np.dot(normal, outward) > 0, (a, b, c, normal, outward)
    print("triangulate_grid self-check (index count + winding): OK")

    # --- revolve_to_buffers: vertex count + colors_per_station broadcasts
    # identically across every theta ring for a given station ---
    n_stations = xs_cyl.size
    colors_per_station = np.linspace([1, 0, 0], [0, 0, 1], n_stations)
    mesh = revolve_to_buffers(xs_cyl, rs_cyl, n_theta, base_color_rgb=(0.5, 0.5, 0.5),
                               colors_per_station=colors_per_station)
    assert mesh.vertices.shape == (n_theta * n_stations, 3)
    assert mesh.normals.shape == (n_theta * n_stations, 3)
    assert mesh.colors.shape == (n_theta * n_stations, 3)
    colors_grid = mesh.colors.reshape(n_theta, n_stations, 3)
    for j in range(n_stations):
        assert np.allclose(colors_grid[:, j, :], colors_per_station[j])
    print("revolve_to_buffers self-check: OK")

    # --- mesh_from_grid's radial-normal fallback (used for decorative
    # hardware built from geometry3d.capped_cylinder/turbopump_assembly_meshes):
    # on the cylindrical wall stations, normals must be unit-length and
    # exactly radial (zero axial component) ---
    Xcap, Ycap, Zcap = geometry3d.capped_cylinder(0.0, 0.4, 0.2, n_theta=n_theta)
    hw_mesh = mesh_from_grid(Xcap, Ycap, Zcap, base_color_rgb=(0.5, 0.5, 0.5))
    wall_normals = hw_mesh.normals.reshape(n_theta, 4, 3)[:, 1:3, :]
    assert np.allclose(np.linalg.norm(wall_normals, axis=-1), 1.0, atol=1e-6)
    assert np.allclose(wall_normals[..., 0], 0.0, atol=1e-6)
    print("mesh_from_grid radial-normal fallback self-check: OK")

    xs_shell = np.array([0.0, 0.3, 0.5, 0.7, 1.5])
    rs_shell = np.array([0.20, 0.20, 0.06, 0.06, 0.35])

    # --- revolve_to_buffers flip_orientation: exact normal negation and
    # winding reversal vs. the default orientation ---
    mesh_out = revolve_to_buffers(xs_shell, rs_shell, n_theta, base_color_rgb=(0.5, 0.5, 0.5))
    mesh_in = revolve_to_buffers(xs_shell, rs_shell, n_theta, base_color_rgb=(0.5, 0.5, 0.5),
                                  flip_orientation=True)
    assert np.allclose(mesh_in.normals, -mesh_out.normals)
    assert np.array_equal(mesh_in.indices, mesh_out.indices[:, [0, 2, 1]])
    print("revolve_to_buffers flip_orientation self-check: OK")

    # --- end_cap_ring: bridges inner to outer radius at a fixed x; the
    # winding is chosen (empirically, via the actual face normal) so the
    # requested facing_sign is honored regardless of triangulate_grid's
    # default convention for a flat (x-constant) grid ---
    cap_pos = end_cap_ring(0.0, 0.1, 0.15, n_theta, (0.4, 0.4, 0.4), facing_sign=1.0)
    cap_neg = end_cap_ring(0.0, 0.1, 0.15, n_theta, (0.4, 0.4, 0.4), facing_sign=-1.0)
    for cap, sign in ((cap_pos, 1.0), (cap_neg, -1.0)):
        p0, p1, p2 = cap.vertices[cap.indices[0]]
        face_n = np.cross(p1 - p0, p2 - p0)
        assert np.dot(face_n, np.array([sign, 0.0, 0.0])) > 0.0
    assert np.allclose(np.sqrt(cap_pos.vertices[:, 1] ** 2 + cap_pos.vertices[:, 2] ** 2),
                        np.tile([0.1, 0.15], n_theta))
    print("end_cap_ring self-check: OK")

    # --- grid_vertex_normals: unit length everywhere; degenerates to the
    # analytic meridian normal on an UNMODULATED grid (r depends on x only);
    # the theta seam (row 0 / row n_theta-1) is a literal duplicate point, so
    # its normals must match exactly, not just approximately ---
    Xu, Yu, Zu = geometry3d.revolve_profile(xs_shell, rs_shell, n_theta)
    n_grid = grid_vertex_normals(Xu, Yu, Zu)
    lengths = np.linalg.norm(n_grid, axis=-1)
    assert np.allclose(lengths, 1.0, atol=1e-6)
    assert np.allclose(n_grid[0], n_grid[-1], atol=1e-9)          # seam continuity
    analytic = revolve_to_buffers(xs_shell, rs_shell, n_theta, (0, 0, 0)).normals.reshape(
        n_theta, xs_shell.size, 3)
    # interior stations only - grid_vertex_normals' one-sided station-axis
    # differencing is less accurate right at the two open ends
    cos_sim = np.sum(n_grid[:, 1:-1, :] * analytic[:, 1:-1, :], axis=-1)
    assert np.all(cos_sim > 0.97), cos_sim.min()
    print("grid_vertex_normals self-check: OK")

    # --- tilted_flange_mesh: a flange plate tilted to sit perpendicular to
    # the local bell surface (`normal`), not the engine centerline, with its
    # base edge snapped onto a REAL (possibly kinked) wall profile via
    # sample_profile_segment rather than an idealized straight chord. OPEN
    # strip (no underside face - see the function's own docstring for why:
    # since the base is exact, a closed underside would be redundant,
    # coincident geometry with the shell mesh, causing Z-fighting). The M=2
    # case (no native stations inside the span) is a 6-station strip; an
    # M=4 case (one native station inside the span, off the straight b1-b2
    # chord) checks the OD rim touches that real data point exactly, plus
    # flat (non-blended) per-face normals throughout ---
    a = np.radians(30.0)  # a 30-degree local cone half-angle
    normal_t = (-np.sin(a), np.cos(a))
    tangent_t = (np.cos(a), np.sin(a))
    assert np.isclose(normal_t[0] * tangent_t[0] + normal_t[1] * tangent_t[1], 0.0)  # perpendicular
    xc, rc, hw, ht = 2.0, 1.0, 0.1, 0.05
    b1 = np.array([xc - hw * tangent_t[0], rc - hw * tangent_t[1]])
    b2 = np.array([xc + hw * tangent_t[0], rc + hw * tangent_t[1]])
    r1 = b1 + ht * np.array(normal_t)
    r2 = b2 + ht * np.array(normal_t)
    assert r1[0] < b1[0]   # the non-monotonic-x property this feature exists for
    assert r2[0] < b2[0]

    n_theta_test = 9
    flange_mesh = tilted_flange_mesh(np.array([b1[0], b2[0]]), np.array([b1[1], b2[1]]),
                                      normal_t, ht, n_theta=n_theta_test,
                                      base_color_rgb=(0.5, 0.5, 0.5))
    assert not np.any(np.isnan(flange_mesh.vertices)) and not np.any(np.isnan(flange_mesh.normals))
    assert np.allclose(np.linalg.norm(flange_mesh.normals, axis=1), 1.0, atol=1e-6)
    # theta=0 row (first 6 vertices, since mesh_from_grid ravels (n_theta,
    # n_stations) row-major) sits at Y=R, Z=0 - directly exposing (x, r)
    v_theta0 = flange_mesh.vertices[:6]
    expected_stations = [b1, r1, r1, r2, r2, b2]
    assert np.allclose(v_theta0, [[s[0], s[1], 0.0] for s in expected_stations], atol=1e-6)
    n_theta0 = flange_mesh.normals[:6]
    expected_face_normals = [(-tangent_t[0], -tangent_t[1]), normal_t, tangent_t]
    for k, fn in enumerate(expected_face_normals):
        # each face's PAIR of stations both carry that face's exact constant
        # normal - no blending with the adjacent face at the shared corner
        assert np.allclose(n_theta0[2 * k], [fn[0], fn[1], 0.0], atol=1e-6)
        assert np.allclose(n_theta0[2 * k + 1], [fn[0], fn[1], 0.0], atol=1e-6)
    assert np.isclose(np.linalg.norm(b1 - [xc, rc]), hw)
    assert np.isclose(np.linalg.norm(r1 - b1), ht)

    # M=4 base (an extra real station strictly inside the span, off the
    # straight b1->b2 chord) - the OD rim must pass through it exactly, and
    # stay flat-shaded, still with no underside.
    bmid1 = b1 + 0.3 * (b2 - b1) + np.array([0.0, 0.01])   # off-chord bump
    bmid2 = b1 + 0.7 * (b2 - b1) - np.array([0.0, 0.005])  # off-chord dip
    base_xs4 = np.array([b1[0], bmid1[0], bmid2[0], b2[0]])
    base_rs4 = np.array([b1[1], bmid1[1], bmid2[1], b2[1]])
    flange4 = tilted_flange_mesh(base_xs4, base_rs4, normal_t, ht,
                                  n_theta=n_theta_test, base_color_rgb=(0.5, 0.5, 0.5))
    n_stations4 = 4 + 2 * (4 - 1)  # 10
    assert flange4.vertices.reshape(n_theta_test, n_stations4, 3).shape[1] == n_stations4
    v4_theta0 = flange4.vertices[:n_stations4]
    assert np.allclose(v4_theta0[0], [b1[0], b1[1], 0.0], atol=1e-9)     # leading cap base
    assert np.allclose(v4_theta0[-1], [b2[0], b2[1], 0.0], atol=1e-9)    # trailing cap base
    # OD rim walks od[0]->od[1]->od[2]->od[3]: stations 2..7 (2 leading-cap,
    # then 3 segments * 2 stations each)
    od4_xs = base_xs4 + ht * normal_t[0]
    od4_rs = base_rs4 + ht * normal_t[1]
    od_rim4 = v4_theta0[2:8, :2]
    expected_od_rim_xs_rs = [od4_xs[0], od4_rs[0], od4_xs[1], od4_rs[1],
                              od4_xs[1], od4_rs[1], od4_xs[2], od4_rs[2],
                              od4_xs[2], od4_rs[2], od4_xs[3], od4_rs[3]]
    assert np.allclose(od_rim4.ravel(), expected_od_rim_xs_rs, atol=1e-9)
    assert np.allclose(np.linalg.norm(flange4.normals, axis=1), 1.0, atol=1e-6)
    n4_theta0 = flange4.normals[:n_stations4]
    assert np.allclose(n4_theta0[2:8], [[normal_t[0], normal_t[1], 0.0]] * 6, atol=1e-6)

    # degenerate inputs are a no-op, matching bolt_ring_pieces' n_bolts<=0 convention
    assert tilted_flange_mesh(np.array([b1[0], b2[0]]), np.array([b1[1], b2[1]]),
                               normal_t, 0.0, 9, (0.5, 0.5, 0.5)) is None
    assert tilted_flange_mesh(np.array([b1[0]]), np.array([b1[1]]),
                               normal_t, ht, 9, (0.5, 0.5, 0.5)) is None
    print("tilted_flange_mesh self-check: OK")

    # --- manifold_ring_mesh: a torus - the coolant-manifold ring hardware.
    # Both sweep axes are built via linspace(0, 2pi, n, endpoint=True), so
    # triangulate_grid's existing duplicate-seam-vertex convention (already
    # relied on for the theta axis everywhere else in this file) closes BOTH
    # axes with no new wraparound code - verified below by DEDUPING vertices
    # by position first (the seam rows/columns are coincident in space but
    # are different vertex indices, so a naive index-based edge check would
    # incorrectly flag every periodic seam as "open" - true of every existing
    # revolve mesh in this file, not something new to the torus) and then
    # confirming every edge of the deduped triangulation is shared by
    # EXACTLY 2 triangles - the real definition of a watertight mesh.
    x0_ring, center_r_ring, tube_r_ring = 0.3, 1.0, 0.12
    n_main, n_tube = 20, 10
    ring_mesh = manifold_ring_mesh(x0_ring, center_r_ring, tube_r_ring,
                                    n_main, n_tube, base_color_rgb=(0.55, 0.55, 0.55))
    assert ring_mesh.vertices.shape == (n_main * n_tube, 3)
    assert ring_mesh.indices.shape == (2 * (n_main - 1) * (n_tube - 1), 3)

    # (a) every vertex is exactly tube_r_ring from ITS OWN local ring-center point
    u_row = np.repeat(np.linspace(0.0, 2 * np.pi, n_main), n_tube)
    centers = np.stack([np.full(n_main * n_tube, x0_ring),
                         center_r_ring * np.cos(u_row),
                         center_r_ring * np.sin(u_row)], axis=1)
    dist = np.linalg.norm(ring_mesh.vertices - centers, axis=1)
    assert np.allclose(dist, tube_r_ring, atol=1e-6)

    # (b) normals: unit length, pointing away from that same local center
    assert np.allclose(np.linalg.norm(ring_mesh.normals, axis=1), 1.0, atol=1e-6)
    outward = (ring_mesh.vertices - centers) / tube_r_ring
    assert np.allclose(np.sum(outward * ring_mesh.normals, axis=1), 1.0, atol=1e-6)

    # (c) winding (mirrors triangulate_grid's own empirical winding self-check
    # style): every triangle's face normal points away from ITS local center
    tris = ring_mesh.indices
    p0, p1, p2 = (ring_mesh.vertices[tris[:, 0]], ring_mesh.vertices[tris[:, 1]],
                  ring_mesh.vertices[tris[:, 2]])
    centroids = (p0 + p1 + p2) / 3.0
    face_normals = np.cross(p1 - p0, p2 - p0)
    u_c = np.linspace(0.0, 2 * np.pi, n_main)[tris[:, 0] // n_tube]
    tri_centers = np.stack([np.full(len(tris), x0_ring),
                             center_r_ring * np.cos(u_c), center_r_ring * np.sin(u_c)], axis=1)
    assert np.all(np.sum(face_normals * (centroids - tri_centers), axis=1) > 0.0)

    # (d) true topological closure - position-deduped edge-sharing check
    verts_rounded = np.round(ring_mesh.vertices.astype(np.float64), 9)
    _, inverse = np.unique(verts_rounded, axis=0, return_inverse=True)
    deduped_tris = inverse.ravel()[tris]
    edge_counts = {}
    for a, b, c in deduped_tris:
        for e in ((a, b), (b, c), (c, a)):
            key = (min(e), max(e))
            edge_counts[key] = edge_counts.get(key, 0) + 1
    assert edge_counts and all(v == 2 for v in edge_counts.values())
    print("manifold_ring_mesh self-check: OK")

    # --- manifold_ring_mesh, TAPERED (per-u tube + centre radius arrays, the
    # physics/manifold.py split/tapered header): every vertex sits exactly its
    # own station's tube radius from its own station's centre, the inner edge
    # stays at a constant radius (centre - tube = const, the wall-flush
    # placement), normals are unit and outward (positive against the local
    # centre->vertex direction), winding stays outward and the mesh is still
    # watertight.
    u_t = np.linspace(0.0, 2 * np.pi, n_main)
    tube_t = 0.12 * np.sqrt(np.maximum(1.0 - 0.5 * np.abs(((u_t + np.pi) % (2 * np.pi)) - np.pi)
                                       / np.pi, 0.15))
    ctr_t = 1.0 + tube_t
    tmesh = manifold_ring_mesh(x0_ring, ctr_t, tube_t, n_main, n_tube, (0.55, 0.55, 0.55))
    u_row_t = np.repeat(u_t, n_tube)
    tube_row = np.repeat(tube_t, n_tube)
    ctr_row = np.repeat(ctr_t, n_tube)
    centers_t = np.stack([np.full(n_main * n_tube, x0_ring), ctr_row * np.cos(u_row_t),
                          ctr_row * np.sin(u_row_t)], axis=1)
    assert np.allclose(np.linalg.norm(tmesh.vertices - centers_t, axis=1), tube_row, atol=1e-6)
    r_axis = np.hypot(tmesh.vertices[:, 1], tmesh.vertices[:, 2])
    assert r_axis.min() >= 1.0 - 1e-9              # inner edge never inside the wall radius
    assert np.allclose(np.linalg.norm(tmesh.normals, axis=1), 1.0, atol=1e-6)
    out_t = (tmesh.vertices - centers_t) / tube_row[:, None]
    assert np.all(np.sum(out_t * tmesh.normals, axis=1) > 0.9)
    tris_t = tmesh.indices
    q0, q1, q2 = (tmesh.vertices[tris_t[:, 0]], tmesh.vertices[tris_t[:, 1]],
                  tmesh.vertices[tris_t[:, 2]])
    uc_t = u_t[tris_t[:, 0] // n_tube]
    cc_t = ctr_t[tris_t[:, 0] // n_tube]
    tri_c_t = np.stack([np.full(len(tris_t), x0_ring), cc_t * np.cos(uc_t), cc_t * np.sin(uc_t)],
                       axis=1)
    assert np.all(np.sum(np.cross(q1 - q0, q2 - q0) * ((q0 + q1 + q2) / 3.0 - tri_c_t), axis=1) > 0.0)
    _, inv_t = np.unique(np.round(tmesh.vertices.astype(np.float64), 9), axis=0,
                         return_inverse=True)
    ec_t = {}
    for a, b, c in inv_t.ravel()[tris_t]:
        for e in ((a, b), (b, c), (c, a)):
            ec_t[(min(e), max(e))] = ec_t.get((min(e), max(e)), 0) + 1
    assert ec_t and all(v == 2 for v in ec_t.values())
    print("manifold_ring_mesh tapered self-check: OK")

    # --- manifold_ring_mesh, called twice at the two AXIAL stations and
    # independent radii physics/manifold.py's placement formula produces
    # (the propellant-intake-manifold feature's call pattern in
    # gui/preview3d_gl.py) - regression guard that the two rings never
    # overlap along the engine axis (X), checked the same watertight-mesh
    # way as (d) above: no vertex of one ring's X-extent overlaps the
    # other's. (Ring RADII are independent of each other by construction -
    # a radial-overlap check would be meaningless here, unlike an earlier
    # design that stacked the rings radially instead.) ---
    from ...physics import manifold as _manifold_physics
    _mr = _manifold_physics.size_manifolds(
        mdot_fuel_kgs=200.0, mdot_ox_kgs=450.0, rho_fuel=810.0, rho_ox=1141.0,
        pc_feed_pa=6.0e6, dp_injector_fuel_pa=1.0e6, dp_injector_ox_pa=1.0e6,
        chamber_dia_m=0.4)
    _fuel_mesh = manifold_ring_mesh(
        _mr["fuel"]["attach_axial_station_m"], _mr["fuel"]["major_radius_m"],
        _mr["fuel"]["outer_radius_m"], n_main, n_tube, base_color_rgb=(0.55, 0.62, 0.75))
    _ox_mesh = manifold_ring_mesh(
        _mr["ox"]["attach_axial_station_m"], _mr["ox"]["major_radius_m"],
        _mr["ox"]["outer_radius_m"], n_main, n_tube, base_color_rgb=(0.70, 0.60, 0.55))
    _fuel_x_max = _fuel_mesh.vertices[:, 0].max()
    _ox_x_min = _ox_mesh.vertices[:, 0].min()
    assert _fuel_x_max <= _ox_x_min + 1e-9, (_fuel_x_max, _ox_x_min)
    print("manifold_ring_mesh non-overlap (propellant intake rings) self-check: OK")

    # --- bolt_ring_pieces: N discrete bolt-head cylinders, each rigidly
    # rotated so its own long axis (n_hat) points radially outward at its
    # own theta_i (rather than along the engine's x-axis). 6-station layout
    # (not capped_cylinder's 4): [base-cap-center, base-cap-rim, wall-start,
    # wall-end, tip-cap-rim, tip-cap-center] - the rim is duplicated at each
    # end so the flat cap faces (0,1 and 4,5) get a constant normal along
    # +/-n_hat while the wall (2,3) keeps a smoothly-varying lateral normal ---
    x_center_bolt, base_r_bolt = 0.4, 0.5
    n_bolts_test, bolt_r_test, bolt_len_test, n_theta_cyl_test = 24, 0.01, 0.02, 8
    n_stations_bolt = 6
    bolt_pieces = bolt_ring_pieces(x_center_bolt, base_r_bolt, n_bolts_test,
                                    bolt_r_test, bolt_len_test, n_theta_cyl_test,
                                    base_color_rgb=(0.45, 0.45, 0.48))
    assert len(bolt_pieces) == n_bolts_test
    for i, piece in enumerate(bolt_pieces):
        assert not np.any(np.isnan(piece.vertices))
        assert not np.any(np.isnan(piece.normals))
        theta_i = 2.0 * np.pi * i / n_bolts_test
        cos_i, sin_i = np.cos(theta_i), np.sin(theta_i)
        n_hat = np.array([0.0, cos_i, sin_i])  # pure-radial default normal=(0,1)
        verts_grid = piece.vertices.reshape(n_theta_cyl_test, n_stations_bolt, 3)
        base_pt, tip_pt = verts_grid[0, 0], verts_grid[0, 5]
        assert np.allclose(base_pt, [x_center_bolt, base_r_bolt * cos_i,
                                      base_r_bolt * sin_i], atol=1e-9)
        assert np.allclose(tip_pt, [x_center_bolt, (base_r_bolt + bolt_len_test) * cos_i,
                                     (base_r_bolt + bolt_len_test) * sin_i], atol=1e-9)
        direction = (tip_pt - base_pt) / bolt_len_test
        assert np.allclose(direction, n_hat, atol=1e-9)

        norm_grid = piece.normals.reshape(n_theta_cyl_test, n_stations_bolt, 3)
        assert np.allclose(np.linalg.norm(norm_grid, axis=-1), 1.0, atol=1e-6)
        # cap faces: constant +/-n_hat, same at every phi row
        assert np.allclose(norm_grid[:, 0, :], -n_hat, atol=1e-6)
        assert np.allclose(norm_grid[:, 1, :], -n_hat, atol=1e-6)
        assert np.allclose(norm_grid[:, 4, :], n_hat, atol=1e-6)
        assert np.allclose(norm_grid[:, 5, :], n_hat, atol=1e-6)
        # wall: lateral, perpendicular to n_hat (varies with phi, not checked exactly here)
        assert np.allclose(np.sum(norm_grid[:, 2, :] * n_hat, axis=-1), 0.0, atol=1e-6)
        assert np.allclose(np.sum(norm_grid[:, 3, :] * n_hat, axis=-1), 0.0, atol=1e-6)
    assert bolt_ring_pieces(0.0, 1.0, 0, 0.01, 0.02, 8, (0.5, 0.5, 0.5)) == []

    # tilted case: bolts protruding along the flange's own tangent/normal
    # (reusing tangent_t/normal_t from the tilted_flange_mesh self-check
    # above) instead of pure radius - each bolt still perpendicular to its
    # own local position around the ring (confirmed correct design - an
    # earlier round's bug was in cap shading, not this position math).
    n_bolts_tilt = 12
    tilt_pieces = bolt_ring_pieces(x_center_bolt, base_r_bolt, n_bolts_tilt,
                                    bolt_r_test, bolt_len_test, n_theta_cyl_test,
                                    base_color_rgb=(0.45, 0.45, 0.48),
                                    tangent=tangent_t, normal=normal_t)
    assert len(tilt_pieces) == n_bolts_tilt
    for i, piece in enumerate(tilt_pieces):
        theta_i = 2.0 * np.pi * i / n_bolts_tilt
        cos_i, sin_i = np.cos(theta_i), np.sin(theta_i)
        n_hat_tilt = np.array([normal_t[0], normal_t[1] * cos_i, normal_t[1] * sin_i])
        verts_grid = piece.vertices.reshape(n_theta_cyl_test, n_stations_bolt, 3)
        base_pt, tip_pt = verts_grid[0, 0], verts_grid[0, 5]
        # the base pole is unaffected by tilt (s=0, rad=0 regardless of
        # tangent/normal) - still the plain radial-ring point
        assert np.allclose(base_pt, [x_center_bolt, base_r_bolt * cos_i,
                                      base_r_bolt * sin_i], atol=1e-9)
        direction = (tip_pt - base_pt) / bolt_len_test
        assert np.allclose(direction, n_hat_tilt, atol=1e-9)
        norm_grid = piece.normals.reshape(n_theta_cyl_test, n_stations_bolt, 3)
        assert np.allclose(norm_grid[:, 0, :], -n_hat_tilt, atol=1e-6)
        assert np.allclose(norm_grid[:, 5, :], n_hat_tilt, atol=1e-6)
    print("bolt_ring_pieces self-check: OK")
    # --- revolve_closed_section: a closed rectangle section revolves to a
    # solid ring; every triangle faces away from the section's own centroid ---
    sec_x = np.array([0.0, 0.1, 0.1, 0.0])
    sec_r = np.array([1.0, 1.0, 1.05, 1.05])
    for order in (slice(None), slice(None, None, -1)):   # CCW and CW input
        ring = revolve_closed_section(sec_x[order], sec_r[order], 24, (0.5, 0.5, 0.5))
        assert ring.indices.shape[0] == 4 * 2 * 23
        assert np.allclose(np.linalg.norm(ring.normals, axis=1), 1.0, atol=1e-6)
        for a, b, c in ring.indices:
            pa, pb, pc = ring.vertices[a], ring.vertices[b], ring.vertices[c]
            fn = np.cross(pb - pa, pc - pa)
            if np.linalg.norm(fn) < 1e-12:
                continue
            m = (pa + pb + pc) / 3.0
            rm = np.hypot(m[1], m[2])
            cen = np.array([0.05, 1.025 * m[1] / rm, 1.025 * m[2] / rm])
            assert np.dot(fn, m - cen) > 0.0
    print("revolve_closed_section self-check: OK")
    print("ALL MESH_PRIMITIVES CHECKS OK")


if __name__ == "__main__":
    self_test()
