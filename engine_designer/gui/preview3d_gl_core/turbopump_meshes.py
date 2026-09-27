"""
Turbopump casing mesh primitives for the "Turbopump 3D" tab (gui/turbopump_scene.py):
the revolved casing walls, the spiral volute / collector scroll with its tangential
discharge diffuser cone, and the mirror/translate placement of a component built in its
own local frame. Every component is built with its SHAFT ON THE LOCAL x AXIS (the same
axis every revolved-engine primitive in this package uses); turbopump_scene lays the
components out along the assembly shaft with `place_pieces`.

Render-only geometry - no physics reads anything here. Pure numpy, no OpenGL/Tk import,
self-tested by `python3 -m engine_designer.gui.preview3d_gl_core`.
"""
import dataclasses
import math

import numpy as np

from .mesh_primitives import MeshBuffers, mesh_from_grid, scroll_manifold_mesh
from .duct_meshes import frustum_mesh, pipe_flange_pieces

# A casing profile is split into separately-shaded strips wherever it turns by more than
# this, so a radial side wall meets the shroud with a crisp edge instead of one smeared
# normal (render-only).
CASING_CORNER_DEG = 35.0
# Tangential discharge diffuser cone after the volute: conical-diffuser half-angle and a
# minimum length in exit diameters (render-only defaults, not a hydraulic design).
DISCHARGE_DIFFUSER_HALF_ANGLE_DEG = 5.0
DISCHARGE_MIN_LEN_DIA_MULT = 1.0
# Volute stations the 10-deg meanline spiral table is resampled to (smooth sweep).
VOLUTE_STATIONS = 73


def _orient_to_normals(mesh):
    """Flip the winding if it disagrees with the vertex normals. Tested on the
    largest-area triangle so a strip touching the axis (degenerate r=0 triangles)
    still gets a meaningful answer."""
    if mesh.indices.shape[0] == 0:
        return mesh
    tri = mesh.vertices[mesh.indices].astype(float)
    face = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    k = int(np.argmax(np.linalg.norm(face, axis=1)))
    vn = mesh.normals[mesh.indices[k]].astype(float).sum(axis=0)
    if float(np.dot(face[k], vn)) < 0.0:
        mesh.indices = mesh.indices[:, [0, 2, 1]]
    return mesh


def _split_at_corners(xs, rs, corner_deg):
    """Consecutive-duplicate-free polyline -> list of index runs, split (sharing the
    corner vertex) wherever the direction turns by more than corner_deg."""
    keep = [0]
    for i in range(1, len(xs)):
        if math.hypot(xs[i] - xs[keep[-1]], rs[i] - rs[keep[-1]]) > 1e-12:
            keep.append(i)
    xs, rs = xs[keep], rs[keep]
    if len(xs) < 2:
        return xs, rs, []
    d = np.column_stack([np.diff(xs), np.diff(rs)])
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    cos_lim = math.cos(math.radians(corner_deg))
    runs, start = [], 0
    for i in range(1, len(d)):
        if float(np.dot(d[i - 1], d[i])) < cos_lim:
            runs.append((start, i))
            start = i
    runs.append((start, len(xs) - 1))
    return xs, rs, runs


def revolve_polyline_pieces(xs_m, rs_m, n_theta, base_color_rgb, corner_deg=CASING_CORNER_DEG,
                            specular_strength=0.0, shininess=32.0):
    """
    Revolve an OPEN meridian polyline (x, r) about the x axis - a casing wall that may
    step radially (vertical segments) or even run backwards in x, which revolve_to_buffers
    can't do (its normals assume r = f(x)). Normals come from the polyline's own arc-length
    tangent, rotated to (-dr, dx): the outward side is on the LEFT walking the polyline,
    i.e. walk it inlet -> back with the solid below. Sharp turns (> corner_deg) start a new,
    separately-shaded strip. Returns list[MeshBuffers], one per strip.
    """
    xs, rs, runs = _split_at_corners(np.asarray(xs_m, dtype=float),
                                     np.asarray(rs_m, dtype=float), corner_deg)
    theta = np.linspace(0.0, 2.0 * np.pi, n_theta)
    pieces = []
    for a, b in runs:
        px, pr = xs[a:b + 1], rs[a:b + 1]
        t = np.column_stack([np.gradient(px), np.gradient(pr)]) if len(px) > 2 else \
            np.tile([px[-1] - px[0], pr[-1] - pr[0]], (len(px), 1))
        t /= np.maximum(np.linalg.norm(t, axis=1, keepdims=True), 1e-15)
        n_x, n_r = -t[:, 1], t[:, 0]
        X, Th = np.meshgrid(px, theta)
        R, _ = np.meshgrid(pr, theta)
        Nx, _ = np.meshgrid(n_x, theta)
        Nr, _ = np.meshgrid(n_r, theta)
        normals = np.stack([Nx.ravel(), (Nr * np.cos(Th)).ravel(), (Nr * np.sin(Th)).ravel()],
                           axis=1).astype(np.float32)
        mesh = mesh_from_grid(X, R * np.cos(Th), R * np.sin(Th), base_color_rgb,
                              normals=normals, specular_strength=specular_strength,
                              shininess=shininess)
        pieces.append(_orient_to_normals(mesh))
    return pieces


def volute_sections(spiral, r_tongue_m, floor_r_m, n=VOLUTE_STATIONS):
    """
    Meanline volute spiral table [(theta_deg, r_outer_m), ...] (pump_meanline.
    _volute_geometry: constant-mean-velocity law, outer radius = r_tongue + 2 x section
    radius) -> per-station (wrap_rad, center_r_m, tube_r_m) for scroll_manifold_mesh. The
    section radius is floored (the throat area is 0 at the tongue; the casing must still
    cover the impeller outlet) and kept non-decreasing; the inner edge stays on r_tongue.
    """
    th = np.array([p[0] for p in spiral], dtype=float)
    ro = np.array([p[1] for p in spiral], dtype=float)
    u = np.linspace(th[0], th[-1], n)
    rs = np.maximum(float(floor_r_m), 0.5 * (np.interp(u, th, ro) - float(r_tongue_m)))
    rs = np.maximum.accumulate(rs)
    return math.radians(th[-1] - th[0]), float(r_tongue_m) + rs, rs


def volute_scroll_pieces(x_m, center_r_m, tube_r_m, wrap_rad, discharge_dia_m, n_tube,
                         base_color_rgb, *, u_start_rad=0.0, handed=1,
                         half_angle_deg=DISCHARGE_DIFFUSER_HALF_ANGLE_DEG,
                         min_len_dia_mult=DISCHARGE_MIN_LEN_DIA_MULT,
                         flange_lip_m=0.0, flange_width_m=0.0, n_bolts=0,
                         specular_strength=0.0, shininess=32.0):
    """
    A spiral volute (or constant-section collector) wrapped `wrap_rad` round the x axis in
    the plane x = x_m, from u_start_rad (u = 0 is +y) in the `handed` (+1/-1) sense, then a
    TANGENTIAL conical discharge diffuser from the scroll's end section to the discharge
    bore (length = the larger of min_len_dia_mult exit diameters and the length that keeps
    the cone at half_angle_deg), with an optional bolted flange at its exit.
    Returns (pieces, exit) - exit = {"pos", "dir", "dia_m"} of the discharge face.
    """
    ctr = np.asarray(center_r_m, dtype=float)
    tube = np.asarray(tube_r_m, dtype=float)
    handed = 1 if handed >= 0 else -1
    span = handed * float(wrap_rad)
    kw = dict(specular_strength=specular_strength, shininess=shininess)
    pieces = list(scroll_manifold_mesh(x_m, ctr, tube, u_start_rad, span, n_tube,
                                       base_color_rgb, cap_tail=False, **kw))
    ue = u_start_rad + span
    radial = np.array([0.0, math.cos(ue), math.sin(ue)])
    onward = handed * np.array([0.0, -math.sin(ue), math.cos(ue)])
    start = np.array([x_m, 0.0, 0.0]) + ctr[-1] * radial
    r0 = float(tube[-1])
    r1 = 0.5 * discharge_dia_m if discharge_dia_m > 0.0 else r0
    length = max(min_len_dia_mult * 2.0 * r1,
                 abs(r1 - r0) / math.tan(math.radians(half_angle_deg)))
    end = start + length * onward
    pieces += frustum_mesh(start, end, r0, r1, n_tube, base_color_rgb, **kw)
    if flange_lip_m > 0.0 and flange_width_m > 0.0:
        nrm = np.array([1.0, 0.0, 0.0])
        pieces += pipe_flange_pieces(end - 0.5 * flange_width_m * onward, onward, nrm,
                                     np.cross(onward, nrm), r1, flange_lip_m, flange_width_m,
                                     n_bolts, n_tube, base_color_rgb, **kw)
    return pieces, {"pos": end, "dir": onward, "dia_m": 2.0 * r1}


def place_pieces(pieces, x0_m=0.0, sx=1.0, dy_m=0.0, dz_m=0.0):
    """Copies of `pieces` mirrored along x (sx = -1) and translated: x' = x0 + sx x,
    y' = y + dy, z' = z + dz. A mirror flips the winding, so the indices are reversed
    with it (normals keep facing out)."""
    out = []
    for p in pieces:
        v = p.vertices.astype(float).copy()
        n = p.normals.copy()
        v[:, 0] = x0_m + sx * v[:, 0]
        v[:, 1] += dy_m
        v[:, 2] += dz_m
        idx = p.indices
        if sx < 0.0:
            n[:, 0] = -n[:, 0]
            idx = idx[:, [0, 2, 1]]
        out.append(dataclasses.replace(p, vertices=v.astype(np.float32), normals=n,
                                       indices=np.ascontiguousarray(idx)))
    return out


def self_test():
    rgb = (0.6, 0.6, 0.65)

    # --- polyline revolve: a step-up casing (neck -> radial wall -> barrel) ---
    xs = [0.0, 0.1, 0.1, 0.3, 0.3]
    rs = [0.05, 0.05, 0.12, 0.12, 0.02]
    pcs = revolve_polyline_pieces(xs, rs, 24, rgb)
    assert len(pcs) == 4, len(pcs)                      # 4 straight runs, 3 sharp corners
    for p in pcs:
        assert np.all(np.isfinite(p.vertices)) and np.all(np.isfinite(p.normals))
        assert np.allclose(np.linalg.norm(p.normals, axis=1), 1.0, atol=1e-5)
    # radial wall stepping UP while walking +x faces -x; the back wall stepping DOWN faces +x
    assert np.all(pcs[1].normals[:, 0] < -0.99) and np.all(pcs[3].normals[:, 0] > 0.99)
    # barrel normals point radially out
    v, nm = pcs[2].vertices, pcs[2].normals
    assert np.all(v[:, 1] * nm[:, 1] + v[:, 2] * nm[:, 2] > 0.0)
    # winding agrees with the normals on every non-degenerate triangle
    for p in pcs:
        tri = p.vertices[p.indices].astype(float)
        face = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        big = np.linalg.norm(face, axis=1) > 1e-12
        vn = p.normals[p.indices].astype(float).sum(axis=1)
        assert np.all(np.sum(face[big] * vn[big], axis=1) > 0.0)
    # a smooth curve (quarter ellipse) stays ONE strip
    t = np.linspace(0.0, 0.5 * np.pi, 17)
    assert len(revolve_polyline_pieces(0.1 * np.sin(t), 0.2 - 0.1 * np.cos(t), 16, rgb)) == 1

    # --- volute sections from a meanline-style spiral table ---
    r_tongue = 0.105
    spiral = [(10.0 * i, r_tongue + 2.0 * math.sqrt(0.002 * i / 36.0 / math.pi))
              for i in range(37)]
    wrap, ctr, tube = volute_sections(spiral, r_tongue, 0.004)
    assert abs(wrap - 2.0 * math.pi) < 1e-12
    assert tube[0] == 0.004 and np.all(np.diff(tube) >= 0.0)
    assert np.allclose(ctr - tube, r_tongue)             # inner edge on the tongue circle
    assert abs(ctr[-1] + tube[-1] - spiral[-1][1]) < 1e-9    # outer edge on the table

    # --- volute scroll + tangential discharge cone + flange ---
    for handed in (1, -1):
        pcs, ex = volute_scroll_pieces(0.2, ctr, tube, wrap, 0.06, 16, rgb, handed=handed,
                                       flange_lip_m=0.02, flange_width_m=0.01, n_bolts=6)
        assert all(np.all(np.isfinite(p.vertices)) for p in pcs)
        # cone starts centred on the scroll's end section, tangent to the wrap
        start = np.array([0.2, 0.0, 0.0]) + ctr[-1] * np.array([0.0, 1.0, 0.0])
        d = ex["pos"] - start
        assert abs(np.linalg.norm(np.cross(d, ex["dir"]))) < 1e-9 and np.dot(d, ex["dir"]) > 0
        assert abs(ex["dir"][2] - handed) < 1e-12 and abs(ex["dia_m"] - 0.06) < 1e-12
        half = math.degrees(math.atan(abs(0.03 - tube[-1]) / np.linalg.norm(d)))
        assert half <= DISCHARGE_DIFFUSER_HALF_ANGLE_DEG + 1e-9
        assert len(pcs) >= 1 + 3 + 3 + 12                # scroll + cone(3) + flange(3 + 2 x 6)

    # --- placement: mirror + translate keeps normals outward and winding consistent ---
    base = revolve_polyline_pieces([0.0, 0.2], [0.1, 0.1], 16, rgb)
    m = place_pieces(base, x0_m=1.0, sx=-1.0, dz_m=0.5)[0]
    assert np.allclose(sorted(set(np.round(m.vertices[:, 0], 9))), [0.8, 1.0])
    assert np.allclose(m.vertices[:, 2].mean(), 0.5, atol=1e-6)
    tri = m.vertices[m.indices].astype(float)
    face = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    vn = m.normals[m.indices].astype(float).sum(axis=1)
    big = np.linalg.norm(face, axis=1) > 1e-12
    assert np.all(np.sum(face[big] * vn[big], axis=1) > 0.0)
    assert base[0].vertices[0, 0] == 0.0                 # original untouched
    print("turbopump_meshes self-test: OK (polyline revolve, volute sections/scroll, placement)")


if __name__ == "__main__":
    self_test()
