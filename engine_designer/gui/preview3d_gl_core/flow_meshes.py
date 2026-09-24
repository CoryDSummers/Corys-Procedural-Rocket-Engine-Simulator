"""
Flow-visualization mesh primitives: temperature -> color on a selectable
FlowColorScale (the fixed log-T "absolute" scale, so a color means the same
temperature on every design, or a linear fit to this design's coolant /
stream range, so a jacket's small rise uses the whole colormap), thin tubes
swept along a stream centerline, a flow loop round a manifold ring, and the
revolved hot-gas core. Every piece carries per-vertex `scalar` (temperature,
K) and `flow_s` (arc length along its stream, m) on MeshBuffers for the
legend and the planned animated-flow shader. Pure numpy (+ matplotlib for
the colormap), no OpenGL/Tk - see this package's __init__.py.

Which temperature goes where is decided by physics/flow_network.py; mapping
its anchors onto rendered geometry is gui/mesh_builder.build_flow_pieces.
"""
from dataclasses import dataclass

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


@dataclass(frozen=True)
class FlowColorScale:
    """Which temperatures the flow colormap spans.
    mode "absolute": the fixed log scale FLOW_T_MIN_K..FLOW_T_MAX_K (colors mean
    the same temperature on every design); "coolant" / "streams": LINEAR over
    [lo_k, hi_k] - this design's regen-jacket range, or every drawn fuel/ox
    stream - so a jacket's tens-of-kelvin rise uses the whole colormap.
    Temperatures outside [lo_k, hi_k] clamp to the end colors."""
    mode: str = "absolute"
    lo_k: float = FLOW_T_MIN_K
    hi_k: float = FLOW_T_MAX_K

    @property
    def is_log(self):
        return self.mode == "absolute"


ABSOLUTE_SCALE = FlowColorScale()
#: UI order + labels of the scale modes (gui/app.py's dropdown).
FLOW_SCALE_MODES = (("coolant", "Coolant (fit)"), ("streams", "All streams (fit)"),
                    ("absolute", "Absolute (log 20-4000 K)"))
FLOW_MIN_FIT_SPAN_K = 1.0     # a fit range narrower than this is padded to it


def temperature_unit(t_k, scale=ABSOLUTE_SCALE):
    """0..1 position of `t_k` on `scale` (clipped)."""
    t = np.asarray(t_k, dtype=float)
    lo, hi = float(scale.lo_k), float(scale.hi_k)
    if scale.is_log:
        t = np.clip(t, lo, hi)
        return np.log(t / lo) / np.log(hi / lo)
    return np.clip((t - lo) / (hi - lo), 0.0, 1.0)


def temperature_colors(t_k, scale=ABSOLUTE_SCALE):
    """(N, 3) float32 RGB for temperatures `t_k` (K) on `scale`."""
    rgba = matplotlib.colormaps[FLOW_CMAP](temperature_unit(np.atleast_1d(t_k), scale))
    return np.asarray(rgba[..., :3], dtype=np.float32).reshape(-1, 3)


#: The streams the 3D Flow view draws (and the "streams" scale / legend fit):
#: the liquids plus an open cycle's turbine exhaust - never the hot core gas.
DRAWN_PROPELLANTS = ("fuel", "ox", "exhaust")


def scale_for_network(network, mode):
    """The FlowColorScale for `mode` on one physics/flow_network result:
    "coolant" = the regen jacket segments' range (falls back to "streams" when
    the design has no jacket), "streams" = every drawn (fuel/ox/exhaust) segment, anything else
    = ABSOLUTE_SCALE."""
    def _range(segs):
        vals = [np.atleast_1d(np.asarray(sg.t_k, dtype=float)) for sg in segs]
        vals = np.concatenate(vals) if vals else np.zeros(0)
        vals = vals[np.isfinite(vals)]
        return (float(vals.min()), float(vals.max())) if vals.size else None

    if mode not in ("coolant", "streams"):
        return ABSOLUTE_SCALE
    rng = None
    if mode == "coolant":
        rng = _range([sg for sg in network if sg.kind == "jacket_pass"])
        if rng is not None:
            mode_eff = "coolant"
    if rng is None:
        rng = _range([sg for sg in network if sg.propellant in DRAWN_PROPELLANTS])
        mode_eff = "streams"
    if rng is None:
        return ABSOLUTE_SCALE
    lo, hi = rng
    if hi - lo < FLOW_MIN_FIT_SPAN_K:
        mid = 0.5 * (lo + hi)
        lo, hi = mid - 0.5 * FLOW_MIN_FIT_SPAN_K, mid + 0.5 * FLOW_MIN_FIT_SPAN_K
    return FlowColorScale(mode_eff, lo, hi)


def scale_ticks(scale, n_target=5):
    """Legend tick temperatures (K) for `scale`: FLOW_LEGEND_TICKS_K on the
    absolute log scale, else round numbers (1/2/2.5/5 x 10^k steps) inside
    [lo_k, hi_k]."""
    if scale.is_log:
        return [float(t) for t in FLOW_LEGEND_TICKS_K]
    lo, hi = float(scale.lo_k), float(scale.hi_k)
    raw = (hi - lo) / max(n_target - 1, 1)
    mag = 10.0 ** np.floor(np.log10(raw))
    step = next(m * mag for m in (1.0, 2.0, 2.5, 5.0, 10.0) if m * mag >= raw)
    first = np.ceil(lo / step) * step
    return [float(t) for t in np.arange(first, hi + 1e-9 * step, step)]


def recolor(scalar, fallback_colors, scale):
    """Per-vertex colors from `scalar` (K) on `scale`; vertices whose scalar is
    NaN (e.g. tube length past the cooled end) keep `fallback_colors`."""
    out = np.array(fallback_colors, dtype=np.float32, copy=True)
    t = np.asarray(scalar, dtype=float)
    ok = np.isfinite(t)
    if np.any(ok):
        out[ok] = temperature_colors(t[ok], scale)
    return out


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
                   n_theta=FLOW_N_THETA, resample=True):
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
    if resample:
        spacing = spacing_m or max(4.0 * radius_m, 1e-4)
        pts, t, s = resample_polyline(pts, t_k, spacing)
    else:   # keep the given points (already dense enough) - cheaper for many streams
        t = np.broadcast_to(np.asarray(t_k, dtype=float), (pts.shape[0],)).copy()
        s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
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


def stream_inside_tube(tube, n_theta, t_of_x, shrink, reverse=False, s_offset_m=0.0):
    """
    The flow stream inside one drawn tube: the tube's own (n_theta,
    n_stations) grid shrunk by `shrink` toward its per-station centreline
    (the mean of each station's ring, seam duplicate excluded) - so it
    follows the tube exactly and always stays inside it, whatever its
    cross-section. `t_of_x` maps axial x -> temperature (K). flow_s counts
    along the centreline in flow direction: `reverse=True` when the stream runs
    toward station 0 (the tubes' stations are stored forward -> aft, so that's
    an up/forward-flowing tube).
    """
    V = np.asarray(tube.vertices, dtype=float)
    n_st = V.shape[0] // n_theta
    if n_st < 2 or n_st * n_theta != V.shape[0]:
        return None
    G = V.reshape(n_theta, n_st, 3)
    ring = G[:-1] if n_theta > 2 else G
    center = ring.mean(axis=0)                                  # (n_st, 3)
    Vs = center[None, :, :] + shrink * (G - center[None, :, :])
    seg = np.linalg.norm(np.diff(center, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    if reverse:
        s = s[-1] - s
    t = np.asarray(t_of_x(center[:, 0]), dtype=float)
    from .mesh_primitives import MeshBuffers
    buf = MeshBuffers(vertices=Vs.reshape(-1, 3).astype(np.float32),
                      normals=np.asarray(tube.normals, dtype=np.float32).copy(),
                      colors=np.zeros((V.shape[0], 3), dtype=np.float32),
                      indices=np.asarray(tube.indices, dtype=np.uint32).copy())
    return _attach_flow_attrs(buf, t, s + s_offset_m, n_theta)


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

    # color scales: absolute is today's log scale; fit modes are linear + clamped
    assert np.allclose(temperature_colors([90.0, 3500.0], ABSOLUTE_SCALE), c)
    fit = FlowColorScale("coolant", 300.0, 380.0)
    u = temperature_unit([250.0, 300.0, 340.0, 380.0, 500.0], fit)
    assert np.allclose(u, [0.0, 0.0, 0.5, 1.0, 1.0])
    # a 300->380 K jacket spans (nearly) the whole map on fit, a sliver on absolute
    span_fit = np.ptp(temperature_unit([300.0, 380.0], fit))
    span_abs = np.ptp(temperature_unit([300.0, 380.0]))
    assert span_fit == 1.0 and span_abs < 0.06, (span_fit, span_abs)
    rc = recolor([np.nan, 340.0], [[0.1, 0.2, 0.3], [0.0, 0.0, 0.0]], fit)
    assert np.allclose(rc[0], [0.1, 0.2, 0.3]) and np.allclose(rc[1], temperature_colors([340.0], fit)[0])

    class _Seg:
        def __init__(self, prop, kind, t):
            self.propellant, self.kind, self.t_k = prop, kind, np.asarray(t, dtype=float)
    net = [_Seg("fuel", "feed_line", [300.0]), _Seg("fuel", "jacket_pass", [300.0, 377.0]),
           _Seg("ox", "manifold_ring", [90.0]), _Seg("gas", "chamber_gas", [3500.0, 1500.0])]
    sc = scale_for_network(net, "coolant")
    assert (sc.mode, sc.lo_k, sc.hi_k) == ("coolant", 300.0, 377.0)
    ss = scale_for_network(net, "streams")
    assert (ss.mode, ss.lo_k, ss.hi_k) == ("streams", 90.0, 377.0)   # gas is not a drawn stream
    no_jacket = scale_for_network([sg for sg in net if sg.kind != "jacket_pass"], "coolant")
    assert no_jacket.mode == "streams" and (no_jacket.lo_k, no_jacket.hi_k) == (90.0, 300.0)
    flat = scale_for_network([_Seg("fuel", "jacket_pass", [100.0, 100.2])], "coolant")
    assert abs((flat.hi_k - flat.lo_k) - FLOW_MIN_FIT_SPAN_K) < 1e-9
    assert scale_for_network(net, "absolute") is ABSOLUTE_SCALE
    assert scale_ticks(ABSOLUTE_SCALE) == [float(t) for t in FLOW_LEGEND_TICKS_K]
    tk_ = scale_ticks(sc)                                   # 300..377 K
    assert tk_[0] >= 300.0 and tk_[-1] <= 377.0 and 3 <= len(tk_) <= 6, tk_
    assert np.allclose(np.diff(tk_), tk_[1] - tk_[0])

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

    # stream inside a tube: stays inside, same topology, flow_s follows direction
    from .tube_bundle import _single_tube_mesh
    xs = np.linspace(0.0, 1.0, 6)
    phi = np.linspace(0.0, 2.0 * np.pi, 12)
    tb = _single_tube_mesh(xs, phi, np.full(6, 0.5), 0.02, 0.3, (1, 1, 1), half_width_m=0.03)
    st = stream_inside_tube(tb, 12, lambda x: 100.0 + 100.0 * x, 0.45, reverse=True)
    assert st.vertices.shape == tb.vertices.shape and st.indices.shape == tb.indices.shape
    ctr = np.stack([xs, 0.5 * np.cos(0.3) * np.ones(6), 0.5 * np.sin(0.3) * np.ones(6)], axis=1)
    d_tube = np.linalg.norm(tb.vertices.reshape(12, 6, 3) - ctr, axis=2)
    d_st = np.linalg.norm(st.vertices.reshape(12, 6, 3) - ctr, axis=2)
    assert np.allclose(d_st, 0.45 * d_tube, atol=1e-6)
    fs = st.flow_s[:6]
    assert fs[0] > fs[-1] and abs(fs[-1]) < 1e-6          # reverse: flows toward station 0
    assert abs(st.scalar[:6][-1] - 200.0) < 1e-3

    # gas core
    core = gas_core_mesh([0, 0.5, 1.0], [0.2, 0.1, 0.3], [3500, 2400, 1500])
    assert core.scalar.shape == (core.vertices.shape[0],)
    print("flow_meshes self-test: OK")


if __name__ == "__main__":
    self_test()
