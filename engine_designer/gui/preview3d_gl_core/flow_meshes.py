"""
Flow-visualization mesh primitives: temperature -> color on a FIXED log-T
scale (so a color means the same temperature on every design), thin tubes
swept along a stream centerline, a flow loop round a manifold ring, and the
revolved hot-gas core. Every piece carries per-vertex `scalar` (temperature,
K) and `flow_s` (arc length along its stream, m) on MeshBuffers for the
legend and the planned animated-flow shader. Pure numpy (+ matplotlib for
the colormap), no OpenGL/Tk - see this package's __init__.py.

Which temperature goes where is decided by physics/flow_network.py; mapping
its anchors onto rendered geometry is gui/mesh_builder.build_flow_pieces.
"""
import matplotlib
import numpy as np

from .duct_meshes import _swept_tube_mesh_from_frames
from .mesh_primitives import revolve_to_buffers
from .profile_geometry import rotation_minimizing_frames

#: Fixed log-temperature color scale (K): LH2 (~20 K) to above any Tc. Cosmetic.
FLOW_T_MIN_K = 20.0
FLOW_T_MAX_K = 4000.0
FLOW_CMAP = "turbo"
#: Legend tick temperatures (K) on that scale.
FLOW_LEGEND_TICKS_K = (20, 50, 100, 300, 1000, 3000)
FLOW_N_THETA = 8          # cross-section facets of a flow tube - they're thin


def temperature_unit(t_k):
    """0..1 position of `t_k` on the fixed log-T scale (clipped)."""
    t = np.clip(np.asarray(t_k, dtype=float), FLOW_T_MIN_K, FLOW_T_MAX_K)
    return np.log(t / FLOW_T_MIN_K) / np.log(FLOW_T_MAX_K / FLOW_T_MIN_K)


def temperature_colors(t_k):
    """(N, 3) float32 RGB for temperatures `t_k` (K)."""
    rgba = matplotlib.colormaps[FLOW_CMAP](temperature_unit(np.atleast_1d(t_k)))
    return np.asarray(rgba[..., :3], dtype=np.float32).reshape(-1, 3)


def resample_polyline(points_xyz, values, spacing_m):
    """Densify a polyline to ~`spacing_m` samples, interpolating a per-point
    value along arc length. Returns (points, values, arc_length)."""
    p = np.asarray(points_xyz, dtype=float)
    v = np.broadcast_to(np.asarray(values, dtype=float), (p.shape[0],))
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
    keep = np.concatenate([[True], np.diff(s) > 1e-12])
    p, v, s = p[keep], v[keep], s[keep]
    n = max(int(np.ceil(s[-1] / max(spacing_m, 1e-9))) + 1, 2)
    s_new = np.linspace(0.0, s[-1], n)
    p_new = np.stack([np.interp(s_new, s, p[:, k]) for k in range(3)], axis=1)
    return p_new, np.interp(s_new, s, v), s_new


def _attach_flow_attrs(buf, station_t_k, station_s, n_theta):
    """Per-station temperature/arc length tiled over the (n_theta, n_stations)
    grid layout mesh_from_grid flattens row-major."""
    buf.colors = np.tile(temperature_colors(station_t_k), (n_theta, 1))
    buf.scalar = np.tile(np.asarray(station_t_k, dtype=np.float32), n_theta)
    buf.flow_s = np.tile(np.asarray(station_s, dtype=np.float32), n_theta)
    return buf


def flow_tube_mesh(centerline_xyz, t_k, radius_m, s_offset_m=0.0, spacing_m=None,
                   n_theta=FLOW_N_THETA):
    """
    A thin tube swept along `centerline_xyz` (in flow direction) with a
    per-point temperature `t_k` (scalar or per point), colored on the fixed
    log-T scale. `s_offset_m` = arc length already travelled upstream, so
    flow_s keeps counting across a stream's consecutive segments. None for a
    degenerate (<2 distinct point) centerline.
    """
    pts = np.asarray(centerline_xyz, dtype=float)
    if pts.shape[0] < 2:
        return None
    spacing = spacing_m or max(4.0 * radius_m, 1e-4)
    pts, t, s = resample_polyline(pts, t_k, spacing)
    if s[-1] <= 0:
        return None
    tangents = np.gradient(pts, axis=0)
    tangents /= np.maximum(np.linalg.norm(tangents, axis=1, keepdims=True), 1e-15)
    nrm, bnm = rotation_minimizing_frames(pts, tangents)
    buf = _swept_tube_mesh_from_frames(pts, tangents, nrm, bnm, float(radius_m), n_theta,
                                       (1.0, 1.0, 1.0))
    return _attach_flow_attrs(buf, t, s + s_offset_m, n_theta)


def ring_loop_points(x_m, center_r_m, start_angle_deg, n=96):
    """A closed loop round the engine axis at axial station x_m, starting at
    `start_angle_deg` (0 = +y, the manifold attach-angle convention; y = r cos u,
    z = r sin u like manifold_ring_mesh)."""
    u = np.radians(start_angle_deg) + np.linspace(0.0, 2.0 * np.pi, n)
    r = np.broadcast_to(np.asarray(center_r_m, dtype=float), u.shape)
    return np.stack([np.full_like(u, x_m), r * np.cos(u), r * np.sin(u)], axis=1)


def gas_core_mesh(xs_m, rs_core_m, t_k, n_theta=48):
    """The hot-gas core: a surface of revolution inside the wall, colored by
    the local static gas temperature per station."""
    xs = np.asarray(xs_m, dtype=float)
    buf = revolve_to_buffers(xs, rs_core_m, n_theta, (1.0, 1.0, 1.0),
                             colors_per_station=temperature_colors(t_k))
    s = np.concatenate([[0.0], np.cumsum(np.abs(np.diff(xs)))])
    return _attach_flow_attrs(buf, t_k, s, n_theta)


def self_test():
    # scale endpoints + monotone "warmth" (turbo runs blue -> red)
    assert abs(temperature_unit(FLOW_T_MIN_K)) < 1e-12 and abs(temperature_unit(FLOW_T_MAX_K) - 1) < 1e-12
    assert temperature_unit(1.0) == 0.0 and temperature_unit(1e6) == 1.0
    u = temperature_unit(np.array(FLOW_LEGEND_TICKS_K))
    assert np.all(np.diff(u) > 0)
    c = temperature_colors([90.0, 3500.0])
    assert c.shape == (2, 3) and c[0, 2] > c[0, 0] and c[1, 0] > c[1, 2]  # cold blue, hot red

    # resample: endpoints kept, values interpolated along arc length
    p, v, s = resample_polyline([[0, 0, 0], [1, 0, 0], [1, 1, 0]], [0.0, 10.0, 20.0], 0.1)
    assert np.allclose(p[0], 0) and np.allclose(p[-1], [1, 1, 0]) and abs(s[-1] - 2.0) < 1e-12
    assert abs(np.interp(1.0, s, v) - 10.0) < 1e-9

    # tube: per-vertex attrs sized to the grid, flow_s monotone along the stream
    line = np.stack([np.linspace(0, 1, 5), np.zeros(5), np.zeros(5)], axis=1)
    tube = flow_tube_mesh(line, np.linspace(100, 400, 5), 0.01, s_offset_m=2.0)
    n = tube.vertices.shape[0]
    assert tube.scalar.shape == (n,) and tube.flow_s.shape == (n,) and tube.colors.shape == (n, 3)
    n_st = n // FLOW_N_THETA
    fs = tube.flow_s[:n_st]
    assert np.all(np.diff(fs) > 0) and abs(fs[0] - 2.0) < 1e-6 and abs(fs[-1] - 3.0) < 1e-5
    assert abs(tube.scalar.min() - 100) < 1e-3 and abs(tube.scalar.max() - 400) < 1e-3
    r = np.hypot(tube.vertices[:, 1], tube.vertices[:, 2])
    assert np.allclose(r, 0.01, atol=1e-6)
    assert flow_tube_mesh(np.zeros((1, 3)), 300.0, 0.01) is None

    # ring loop closes on itself at the attach angle
    loop = ring_loop_points(0.5, 0.3, 90.0)
    assert np.allclose(loop[0], loop[-1]) and np.allclose(loop[0], [0.5, 0.0, 0.3], atol=1e-12)

    # gas core
    core = gas_core_mesh([0, 0.5, 1.0], [0.2, 0.1, 0.3], [3500, 2400, 1500])
    assert core.scalar.shape == (core.vertices.shape[0],)
    print("flow_meshes self-test: OK")


if __name__ == "__main__":
    self_test()
