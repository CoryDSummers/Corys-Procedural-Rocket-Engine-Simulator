"""
Procedural plumbing: a manifold ring (the ROOT) plus an ordered chain of
straight pipe segments joined by elbows, with optional flanges at any joint.
This is the "future plumbing/piping feature" physics/manifold.py's frozen
HOOK_POINT_FIELDS were reserved for - it consumes exactly those hook fields
(attach_axial_station_m / attach_angular_position_deg / inner_diameter_m,
plus wall_thickness_m for mass) and nothing else from the manifold result.

Every node says what it IS (`kind`: "manifold" | "pipe") and what it's FOR
(`role`: "fuel_feed", "coolant_supply", ...) so a future feature can walk
`design.plumbing_runs` and find, e.g., every pipe carrying fuel, without
inspecting geometry. The first concrete use is the regen-jacket coolant
inlet ring (`host="jacket_inlet"`), which used to carry a fixed auto-drawn
two-waypoint duct in gui/mesh_builder.py; any other ring (fuel/ox injector-
feed, jacket return, later a GG exhaust manifold) is the same code with a
different `host`.

Geometry conventions (engine axis = +x, pointing aft/downstream, same as
everything else in this tool):
- A run attaches to its host ring at `attach_angle_deg` around the engine
  axis (0 = +y, matching manifold.py's attach_angular_position_deg) and
  `attach_poloidal_deg` around the ring's own tube cross-section: 0 = the
  ring's outer equator (pipe leaves radially outward), +90 = the forward
  crown (pipe leaves along -x, toward the injector), 180 = inner equator
  (into the chamber - flagged by an advisory), 270 = aft crown (+x).
- Pipe 1 always leaves along the torus SURFACE NORMAL at that point; its
  polyline starts buried at the ring centreline so the swept tube emerges
  cleanly from the torus. Its `length_dia_mult` is measured from the torus
  surface, and its own yaw/pitch/bend_radius fields are ignored (there is
  no elbow at the root - the joint IS the torus).
- Each later pipe k turns relative to the previous pipe's local frame
  (tangent t, normal n, binormal b - right-handed, t x n = b): yaw rotates
  about n (positive = toward -b), then pitch rotates about the yawed b
  (positive = toward n). At the root, n is the poloidal tangent (at the
  outer equator that's -x, i.e. "toward the injector") and b runs around the
  ring. So on a radially-leaving pipe, +pitch bends the run forward along
  the engine and +/-yaw swings it around the engine's circumference.
- The elbow between pipe k-1 and pipe k has radius pipes[k].bend_radius_dia_
  mult x pipe diameter; it is trimmed back into both straight runs exactly
  as gui/preview3d_gl_core/profile_geometry.fillet_polyline does (same
  trim = R / tan(beta/2) and same 0.49-of-shorter-segment clamp - the
  formula is repeated here, not imported, because physics/ never imports
  from gui/).
- All lengths are stored as MULTIPLES OF PIPE DIAMETER so a run designed on
  one engine still reads correctly after the physics rescales the ring
  (pipe diameter = the host ring's flow diameter this round).

Mass (Tier-3 estimate, see ASSUMPTIONS.md): pipe wall thickness = the host
ring's own hoop-stress wall (`hook["wall_thickness_m"]`, already sized
against the real local feed pressure in manifold.py), density =
manifold.MANIFOLD_DENSITY_KG_M3, length = the untrimmed polyline length
(elbows shorten a run slightly; ignored, conservative). Flanges = a solid
annulus from the pipe OD out by the lip, `flange_width` thick, same density.
No real-engine feed-line mass figure exists in this project to spot-check
against (same caveat manifold.py already carries) - trust the direction,
not the magnitude.

Everything here is pure numpy/dataclasses - headlessly self-tested.
"""
from dataclasses import dataclass, field, asdict, fields as dc_fields
import math
import warnings

import numpy as np

from .cooling import COOLANT_TRANSPORT, _COOLANT_TRANSPORT_FALLBACK, _darcy_friction
from .manifold import (MANIFOLD_DENSITY_KG_M3, ring_flow_radius_at, velocity_cap_warning)

KINDS = ("manifold", "pipe")
ROLES = ("fuel_manifold", "ox_manifold", "coolant_supply_manifold", "coolant_return_manifold",
         "fuel_feed", "ox_feed", "coolant_supply", "coolant_return", "turbine_exhaust",
         "turbine_exhaust_manifold")
# host -> (compute()-result key, sub-key) for hook_for_host
HOSTS = {
    "jacket_inlet": ("jacket_manifold_result", "jacket_inlet"),
    "jacket_return": ("jacket_manifold_result", "jacket_return"),
    "fuel": ("manifold_result", "fuel"),
    "ox": ("manifold_result", "ox"),
    # open cycles: the turbine-exhaust duct's termination (physics/
    # turbine_exhaust.size_hardware - injection torus / aspirator inlet collar /
    # overboard exhaust-nozzle point hook)
    "turbine_exhaust": ("turbine_exhaust_hardware", "exhaust"),
}
# Per-host display/role data, keyed identically to HOSTS (self_test asserts
# the key sets match, so a future host - turbopump ports, a GG exhaust
# manifold - can't be added half-way). The GUI's Plumbing tab builds one row
# per host from these.
HOST_LABELS = {
    "jacket_inlet": "Jacket inlet ring (coolant supply)",
    "jacket_return": "Jacket return ring (coolant turnaround)",
    "fuel": "Fuel injector-feed ring",
    "ox": "Ox injector-feed ring",
    "turbine_exhaust": "Turbine exhaust duct (GG / tap-off)",
}
# Why hook_for_host can return None for that host, in user words.
HOST_MISSING_HINT = {
    "jacket_inlet": "needs a regeneratively cooled chamber",
    "jacket_return": "only exists under the F-1 split or J-2 mid-nozzle jacket topologies",
    "fuel": "always sized - if missing, the design failed to compute",
    "ox": "always sized - if missing, the design failed to compute",
    "turbine_exhaust": "only open cycles (gas generator / tap-off) dump turbine exhaust",
}
# kind/role tags a run rooted on each host gets by default (see ROLES).
HOST_RING_ROLE = {
    "jacket_inlet": "coolant_supply_manifold",
    "jacket_return": "coolant_return_manifold",
    "fuel": "fuel_manifold",
    "ox": "ox_manifold",
    "turbine_exhaust": "turbine_exhaust_manifold",
}
HOST_PIPE_ROLE = {
    "jacket_inlet": "coolant_supply",
    "jacket_return": "coolant_return",
    "fuel": "fuel_feed",
    "ox": "ox_feed",
    "turbine_exhaust": "turbine_exhaust",
}
# Which turbopump port each host's run is fed from (both jacket rings carry
# fuel as coolant). jacket_return is a turnaround - it never connects to a pump.
HOST_PUMP = {"jacket_inlet": "fuel_pump", "jacket_return": "fuel_pump",
             "fuel": "fuel_pump", "ox": "ox_pump", "turbine_exhaust": "turbine"}
# ...and which of that turbomachinery body's ports (geometry3d.turbopump_ports):
# pumps close onto their discharge, the exhaust duct onto the turbine exhaust.
HOST_PORT = {"jacket_inlet": "discharge", "jacket_return": "discharge",
             "fuel": "discharge", "ox": "discharge", "turbine_exhaust": "exhaust"}
CONNECTABLE_HOSTS = ("jacket_inlet", "fuel", "ox", "turbine_exhaust")
# Hot turbine-exhaust gas viscosity for the duct's friction loss (~800-900 K
# fuel-rich combustion gas). Tier 3 - textbook order of magnitude, not from a
# claude_lit source.
EXHAUST_GAS_VISCOSITY_PA_S = 3.0e-5


def port_for_host(ports, host):
    """The turbopump port dict (geometry3d.turbopump_ports) a connect_to_pump
    run on `host` closes onto, or None."""
    return ((ports or {}).get(HOST_PUMP.get(host, "fuel_pump")) or {}).get(
        HOST_PORT.get(host, "discharge"))
PORT_STANDOFF_DIA_MULT_MIN = 0.5
PORT_STANDOFF_DIA_MULT_MAX = 10.0
SEED_APPROACH_DIA_MULT = 3.0       # seed route: leg A length (the 90-deg approach to S)
AUTO_LEG_TURN_TOLERANCE_DEG = 10.0

# --- line pressure loss (run_pressure_loss_pa) - all Tier 3, textbook-typical
# values NOT found in claude_lit (ASSUMPTIONS.md) --------------------------
PIPE_ROUGHNESS_M = 1.5e-6          # drawn stainless tubing
# 90-deg bend loss coefficient vs bend radius / pipe dia (interpolated, flat
# beyond the ends); a bend of angle a uses K90 * a/90.
ELBOW_K90_BY_RD = ((0.5, 0.9), (1.0, 0.35), (1.5, 0.25), (2.0, 0.2), (5.0, 0.2))
# Conical reducer loss coefficient vs cone half-angle (deg), applied to the
# dynamic head at the SMALLER bore.
REDUCER_K_BY_HALF_ANGLE = ((0.0, 0.02), (10.0, 0.05), (15.0, 0.08), (30.0, 0.3),
                           (45.0, 0.5), (90.0, 1.0))
RING_ENTRY_K = 1.0                 # x the ring's design velocity head (Borda-Carnot split)
VALVE_AND_UNMODELED_K = 2.0        # main valve + undrawn fittings, x the dynamic head in the
                                   # run's largest-bore pipe (added in design.py per pump leg)
# Liquid oxidizer dynamic viscosity (Pa.s) at feed conditions; fuel viscosity
# comes from cooling.COOLANT_TRANSPORT. Textbook-typical, Tier 3.
OX_VISCOSITY_PA_S = {"LOX": 1.9e-4, "N2O4": 4.2e-4, "H2O2": 1.2e-3}
_OX_VISCOSITY_FALLBACK = 3.0e-4

# Slider/validation ranges (the Shape Lab clamps to these; from_dict clamps too
# so a hand-edited project file can't produce a hairpin or a zero-length pipe).
PIPE_LENGTH_DIA_MULT_MIN = 0.25
PIPE_LENGTH_DIA_MULT_MAX = 20.0
PIPE_TURN_DEG_MAX = 90.0
BEND_RADIUS_DIA_MULT_MIN = 0.5
BEND_RADIUS_DIA_MULT_MAX = 5.0
FLANGE_LIP_DIA_MULT_MAX = 0.6
FLANGE_WIDTH_DIA_MULT_MAX = 0.5
# Same 0.49-of-shorter-segment safety fraction as fillet_polyline.
FILLET_TRIM_MAX_SEGMENT_FRACTION = 0.49
# Auto bolt count for a pipe flange: target arc spacing between bolt centres,
# x pipe diameter, clamped [min, max] - cosmetic, the pipe-scale analogue of
# hardware_constants.BOLT_SPACING_THROAT_DIA_MULT / BOLT_MIN_COUNT / BOLT_MAX_COUNT.
FLANGE_BOLT_SPACING_DIA_MULT = 0.45
FLANGE_BOLT_MIN_COUNT = 4
FLANGE_BOLT_MAX_COUNT = 24
# Per-segment bore (PipeSegment.bore_scale = bore / the hook's full-flow feed
# bore; 1.0 = the pipe runs at the ring's own design velocity).
PIPE_BORE_SCALE_MIN = 0.4
PIPE_BORE_SCALE_MAX = 2.0
# Conical reducer wherever the bore changes - at the root (ring inlet bore ->
# pipe 1) and between segments (at the start of the downstream straight, after
# its elbow). Length = this x the LARGER diameter: a typical concentric
# butt-weld reducer is ~1-1.5 large-end OD long (Tier 3, ASSUMPTIONS.md).
# A reducer squeezed shorter than that by a short pipe is warned about when
# its cone half-angle exceeds REDUCER_MAX_HALF_ANGLE_DEG (Tier 3 - steeper
# cones start to separate the flow).
REDUCER_LENGTH_DIA_MULT = 1.5
REDUCER_MAX_HALF_ANGLE_DEG = 15.0
# Defaults that reproduce gui/mesh_builder.py's legacy auto-drawn jacket-inlet
# duct (see default_run_for_host): corner 2.5 bend radii out from the ring
# centreline, then a 2.1-bend-radius stub toward -x, bend radius 0.5 x dia.
_LEGACY_DUCT_BEND_RADIUS_DIA_MULT = 0.5
_LEGACY_DUCT_STANDOFF_BEND_RADIUS_MULT = 2.5
_LEGACY_DUCT_STUB_BEND_RADIUS_MULT = 2.1


@dataclass
class PipeSegment:
    kind: str = "pipe"
    role: str = "coolant_supply"
    length_dia_mult: float = 3.0        # straight length / pipe diameter (raw, pre-elbow-trim)
    yaw_deg: float = 0.0                # about previous normal, +/-PIPE_TURN_DEG_MAX
    pitch_deg: float = 0.0              # about the yawed binormal, +/-PIPE_TURN_DEG_MAX
    bend_radius_dia_mult: float = 0.5   # elbow at THIS segment's start (ignored on pipe 1)
    flange_at_end: bool = False         # flange at this segment's far end
    bore_scale: float = 1.0             # this pipe's bore / the hook's full-flow feed bore
                                        # (1.0 = ring design velocity; lengths/elbow radii
                                        # are multiples of THIS pipe's own diameter)


@dataclass
class PlumbingRun:
    kind: str = "manifold"
    role: str = "coolant_supply_manifold"
    host: str = "jacket_inlet"          # key of HOSTS: which ring the run is rooted on
    attach_angle_deg: float = 0.0       # around the engine axis (0 = +y)
    attach_poloidal_deg: float = 0.0    # around the ring tube (0 = outer equator, +90 = -x)
    flange_at_root: bool = False
    flange_lip_dia_mult: float = 0.25   # shared flange style, x pipe diameter
    flange_width_dia_mult: float = 0.15
    flange_bolt_count: int = 0          # 0 = auto (FLANGE_BOLT_SPACING_DIA_MULT rule)
    connect_to_pump: bool = False       # close the run onto HOST_PUMP[host]'s discharge port
                                        # (two AUTO legs appended by resolve_run)
    port_standoff_dia_mult: float = 2.5  # straight entry into the port, x port bore
    pipes: list = field(default_factory=list)   # list[PipeSegment]


def _clamp(v, lo, hi):
    return min(max(float(v), lo), hi)


def pipe_from_dict(d):
    """Tolerant PipeSegment rebuild: unknown keys dropped, missing take
    defaults, numeric fields clamped into their slider ranges."""
    known = {f.name for f in dc_fields(PipeSegment)}
    p = PipeSegment(**{k: v for k, v in (d or {}).items() if k in known})
    p.length_dia_mult = _clamp(p.length_dia_mult, PIPE_LENGTH_DIA_MULT_MIN, PIPE_LENGTH_DIA_MULT_MAX)
    p.yaw_deg = _clamp(p.yaw_deg, -PIPE_TURN_DEG_MAX, PIPE_TURN_DEG_MAX)
    p.pitch_deg = _clamp(p.pitch_deg, -PIPE_TURN_DEG_MAX, PIPE_TURN_DEG_MAX)
    p.bend_radius_dia_mult = _clamp(p.bend_radius_dia_mult, BEND_RADIUS_DIA_MULT_MIN,
                                    BEND_RADIUS_DIA_MULT_MAX)
    p.flange_at_end = bool(p.flange_at_end)
    p.bore_scale = _clamp(p.bore_scale, PIPE_BORE_SCALE_MIN, PIPE_BORE_SCALE_MAX)
    if p.kind not in KINDS or p.role not in ROLES:
        warnings.warn(f"plumbing: unknown pipe kind/role {p.kind!r}/{p.role!r} (kept as-is)")
    return p


def run_from_dict(d):
    """Tolerant PlumbingRun rebuild (same contract as EngineDesign.from_dict):
    accepts a dict whose `pipes` entries are dicts OR PipeSegments."""
    known = {f.name for f in dc_fields(PlumbingRun)}
    d = d or {}
    r = PlumbingRun(**{k: v for k, v in d.items() if k in known and k != "pipes"})
    r.pipes = [p if isinstance(p, PipeSegment) else pipe_from_dict(p)
               for p in (d.get("pipes") or [])]
    r.attach_angle_deg = float(r.attach_angle_deg) % 360.0
    r.attach_poloidal_deg = float(r.attach_poloidal_deg) % 360.0
    r.flange_at_root = bool(r.flange_at_root)
    r.flange_lip_dia_mult = _clamp(r.flange_lip_dia_mult, 0.0, FLANGE_LIP_DIA_MULT_MAX)
    r.flange_width_dia_mult = _clamp(r.flange_width_dia_mult, 0.0, FLANGE_WIDTH_DIA_MULT_MAX)
    r.flange_bolt_count = int(max(0, int(r.flange_bolt_count)))
    r.connect_to_pump = bool(r.connect_to_pump)
    r.port_standoff_dia_mult = _clamp(r.port_standoff_dia_mult, PORT_STANDOFF_DIA_MULT_MIN,
                                      PORT_STANDOFF_DIA_MULT_MAX)
    if r.connect_to_pump and r.host not in CONNECTABLE_HOSTS:
        warnings.warn(f"plumbing: a {r.host!r} run can't connect to a pump - flag cleared")
        r.connect_to_pump = False
    if r.kind not in KINDS or r.role not in ROLES:
        warnings.warn(f"plumbing: unknown run kind/role {r.kind!r}/{r.role!r} (kept as-is)")
    if r.host not in HOSTS:
        warnings.warn(f"plumbing: unknown host {r.host!r} - the run will not render")
    return r


def run_to_dict(run):
    """Plain JSON-able dict (what EngineDesign.plumbing_runs actually stores)."""
    return asdict(run)


def hook_for_host(result, host):
    """The manifold hook dict a run with this `host` roots on, from an
    EngineDesign.compute() result - or None if that ring doesn't exist for
    this design (e.g. jacket_return on a single-pass topology, or any
    jacket ring on a non-regen chamber)."""
    if host not in HOSTS:
        return None
    key, sub = HOSTS[host]
    group = result.get(key) if isinstance(result, dict) else None
    if not group:
        return None
    return group.get(sub) or None


def _rodrigues(v, axis, angle_rad):
    axis = axis / np.linalg.norm(axis)
    return (v * math.cos(angle_rad) + np.cross(axis, v) * math.sin(angle_rad)
            + axis * np.dot(axis, v) * (1.0 - math.cos(angle_rad)))


def root_frame(attach_angle_deg, attach_poloidal_deg):
    """(t, n, b) at the torus surface point: t = outward surface normal,
    n = poloidal tangent (direction of increasing poloidal angle), b = t x n."""
    th = math.radians(attach_angle_deg)
    ph = math.radians(attach_poloidal_deg)
    u_r = np.array([0.0, math.cos(th), math.sin(th)])
    e_x = np.array([1.0, 0.0, 0.0])
    t = math.cos(ph) * u_r - math.sin(ph) * e_x
    n = -math.sin(ph) * u_r - math.cos(ph) * e_x
    b = np.cross(t, n)
    return t, n, b


def _corner_trim(bend_radius_m, d_in, d_out, len_in, len_out):
    """fillet_polyline's trim-back distance for one corner, whether it had to
    be clamped (= the adjacent straight is too short for that elbow), and the
    EFFECTIVE elbow radius that trim corresponds to (= the request when not
    clamped). Renderers feed the effective radius to fillet_polyline so it
    never has to re-derive (and warn about) the same clamp on every redraw."""
    cos_beta = float(np.clip(-np.dot(d_in, d_out), -1.0, 1.0))
    beta = math.acos(cos_beta)
    if beta > math.pi - 1e-9:
        return 0.0, False, bend_radius_m
    half = beta / 2.0
    trim = bend_radius_m / math.tan(half) if half > 1e-9 else float("inf")
    max_allowed = FILLET_TRIM_MAX_SEGMENT_FRACTION * min(len_in, len_out)
    if trim > max_allowed:
        return max_allowed, True, max_allowed * math.tan(half)
    return trim, False, bend_radius_m


def _root_flow_radius_m(hook, attach_angle_deg):
    """The ring's local flow radius where a run leaves it (tapered header
    rings are fattest at their inlet) - what the root reducer starts from."""
    if "inlet_flow_radius_m" in hook:
        return float(ring_flow_radius_at(hook, attach_angle_deg))
    return float(hook.get("flow_radius_m", float(hook["inner_diameter_m"]) / 2.0))


def resolve_run(run, hook, ring_center_r_m, ring_tube_r_m, supercritical=False, port=None):
    """
    Turn a PlumbingRun (or its dict) rooted on `hook` (a manifold.py per-ring
    result dict) into concrete geometry. `ring_center_r_m` / `ring_tube_r_m`
    are the ring's RENDER centreline radius and tube radius - the caller
    passes whatever it draws the torus with (gui/mesh_builder.py's wall-
    snapped radius + outer_radius_m), so the pipe emerges from the drawn
    ring, not from the physics ring's nominal major radius.

    Each pipe has its own bore (PipeSegment.bore_scale x the hook's full-flow
    feed bore). Pipe 1 starts at the RING's local flow bore (flush with the
    drawn torus) and cones to its own bore over a reducer; any later bore
    change cones the same way at the start of the downstream straight.
    `supercritical` (LH2) skips the SP-8087 liquid-velocity advisory.

    `port` (a geometry3d.turbopump_ports discharge dict: pos/dir/dia_m): when
    the run has `connect_to_pump` set, two AUTO legs are appended after the
    user's pipes - leg A from the last pipe's end to a standoff point
    port.pos + port_standoff_dia_mult x bore x port.dir, then leg B straight
    into the port face (direction -port.dir) - both at the port's bore, so the
    run ends exactly on the port whatever ring radius the caller rooted it at.

    Returns a dict:
      waypoints_xyz      (n+1, 3): ring centreline point, then each pipe's end
      bend_radii_m       list, n-1: elbow radius at each interior corner (as asked)
      bend_radii_eff_m   list, n-1: the same after the short-straight clamp -
                         what actually gets rendered; pass THIS to fillet_polyline
      tube_radius_m      pipe 1's flow radius (back-compat scalar)
      pipe_dia_m         pipe 1's bore (back-compat scalar)
      pipe_radii_m       list, n: each pipe's own flow radius
      pipe_velocities_ms list, n: bulk velocity in each pipe (continuity)
      root_flow_radius_m the ring's local flow radius at the root
      reducers           list of {"pipe_index", "r_start_m", "r_end_m",
                         "start_offset_m", "length_m"} - start_offset is from
                         that pipe's waypoint start (the ring centre for pipe 1)
      segment_dirs       (n, 3) unit direction of each pipe
      joint_frames       list of {"name", "pipe_index", "pos", "t", "n", "b",
                          "flange": bool, "r_m", "flange_dims"} for the root
                          (surface point), each interior joint (at the end of
                          that pipe's straight run, before the elbow trim) and
                          the free end; flange_dims sized at the local bore
      flange             {"lip_m", "width_m", "bolt_count"} at pipe 1's bore
      total_length_m     untrimmed polyline length measured from the torus surface
      auto_leg_indices   list of pipe indices that are auto-close legs (empty
                         unless connected); closes_on_port bool
      pipe_kinds         list, n: "user" | "auto" per pipe
      advisories         list[str] (warn-don't-block)
    Empty run (no pipes) -> waypoints has 1 row, everything else empty.
    """
    if not isinstance(run, PlumbingRun):
        run = run_from_dict(run)
    feed_dia = float(hook["inner_diameter_m"])
    n_pipes = len(run.pipes)
    dias = [p.bore_scale * feed_dia for p in run.pipes]
    radii = [0.5 * d for d in dias]
    r_pipe = radii[0] if n_pipes else 0.5 * feed_dia
    dia = 2.0 * r_pipe
    r_root = _root_flow_radius_m(hook, run.attach_angle_deg)
    th = math.radians(run.attach_angle_deg)
    x0 = float(hook["attach_axial_station_m"])
    centre = np.array([x0, ring_center_r_m * math.cos(th), ring_center_r_m * math.sin(th)])
    t, n, b = root_frame(run.attach_angle_deg, run.attach_poloidal_deg)
    surface = centre + ring_tube_r_m * t

    advisories = []
    if 90.0 < run.attach_poloidal_deg < 270.0:
        advisories.append(f"Run on {run.host}: poloidal attach angle {run.attach_poloidal_deg:.0f} deg "
                          "points the pipe inward, toward the chamber wall.")

    waypoints = [centre]
    dirs = []
    frames = []
    for k, p in enumerate(run.pipes):
        if k > 0:
            t = _rodrigues(t, n, math.radians(p.yaw_deg))
            b = np.cross(t, n)
            t = _rodrigues(t, b, math.radians(p.pitch_deg))
            n = np.cross(b, t)
        # Renormalise to kill drift over long chains.
        t = t / np.linalg.norm(t); n = n / np.linalg.norm(n); b = np.cross(t, n)
        length = p.length_dia_mult * dias[k]
        start = surface if k == 0 else waypoints[-1]
        waypoints.append(start + length * t)
        dirs.append(t.copy())
        frames.append((t.copy(), n.copy(), b.copy()))
    # Auto-close onto a pump port (see docstring).
    pipes = list(run.pipes)
    auto_idx = []
    closes = False
    if run.connect_to_pump and port is not None:
        if not n_pipes:
            advisories.append(f"Run on {run.host}: connected to the pump but has no pipes - add "
                              "one (or use Route to pump) so the line can leave the ring.")
        else:
            d_port = float(port.get("dia_m") or 0.0) or dias[-1]
            p_dir = np.asarray(port["dir"], dtype=float)
            p_dir = p_dir / np.linalg.norm(p_dir)
            p_pos = np.asarray(port["pos"], dtype=float)
            standoff_pt = p_pos + run.port_standoff_dia_mult * d_port * p_dir
            for leg_end, last in ((standoff_pt, False), (p_pos, True)):
                leg = leg_end - waypoints[-1]
                length = float(np.linalg.norm(leg))
                if length < 1e-9:
                    continue
                tl = leg / length
                n_prev = frames[-1][1]
                nl = n_prev - np.dot(n_prev, tl) * tl
                if np.linalg.norm(nl) < 1e-6:
                    b_prev = frames[-1][2]
                    nl = b_prev - np.dot(b_prev, tl) * tl
                nl = nl / np.linalg.norm(nl)
                waypoints.append(leg_end.copy())
                dirs.append(tl)
                frames.append((tl, nl, np.cross(tl, nl)))
                pipes.append(PipeSegment(
                    role=run.pipes[-1].role, length_dia_mult=length / d_port,
                    bend_radius_dia_mult=run.pipes[-1].bend_radius_dia_mult,
                    flange_at_end=last, bore_scale=d_port / feed_dia if feed_dia > 0 else 1.0))
                dias.append(d_port)
                radii.append(0.5 * d_port)
                auto_idx.append(len(pipes) - 1)
            closes = bool(auto_idx)
    n_pipes = len(pipes)
    waypoints = np.array(waypoints, dtype=float)
    dirs = np.array(dirs, dtype=float) if dirs else np.zeros((0, 3))

    seg_lens = np.linalg.norm(np.diff(waypoints, axis=0), axis=1) if n_pipes else np.zeros(0)
    bend_radii = [pipes[k].bend_radius_dia_mult * dias[k] for k in range(1, n_pipes)]
    bend_radii_eff = list(bend_radii)
    trims = [0.0] * n_pipes  # trim at the END of pipe k (for the flange placement)
    for k in range(1, n_pipes):
        trim, clamped, r_eff = _corner_trim(bend_radii[k - 1], dirs[k - 1], dirs[k],
                                            seg_lens[k - 1], seg_lens[k])
        trims[k - 1] = trim
        bend_radii_eff[k - 1] = r_eff
        turn = math.degrees(math.acos(float(np.clip(np.dot(dirs[k - 1], dirs[k]), -1.0, 1.0))))
        if clamped:
            advisories.append(f"Pipe {k + 1}: its {bend_radii[k - 1] / dias[k]:.2f}-dia elbow needs "
                              f"more straight run than pipe {k} / pipe {k + 1} have - rendered "
                              f"at {r_eff / dias[k]:.2f} dia instead.")
        # auto-close legs get AUTO_LEG_TURN_TOLERANCE_DEG of slack: the render and
        # the physics root the same run on slightly different ring radii, which
        # skews a seeded 90-deg corner by a degree or two
        turn_cap = PIPE_TURN_DEG_MAX + (AUTO_LEG_TURN_TOLERANCE_DEG if k in auto_idx else 0.0)
        if turn > turn_cap + 1e-6:
            advisories.append(f"Pipe {k + 1}: combined yaw+pitch turn is {turn:.0f} deg (> "
                              f"{PIPE_TURN_DEG_MAX:.0f}) - a very tight elbow for a feed line.")
    for k in range(1, n_pipes + 1):
        radial = math.hypot(waypoints[k][1], waypoints[k][2])
        if radial < ring_center_r_m - ring_tube_r_m - 1e-9:
            advisories.append(f"Pipe {k}: its end lies inside the manifold ring's radius "
                              "(likely through the chamber/nozzle wall).")
            break

    # Reducers: wherever the bore changes (root: ring bore -> pipe 1).
    reducers = []
    for k in range(n_pipes):
        r_in = r_root if k == 0 else radii[k - 1]
        r_out = radii[k]
        if abs(r_out - r_in) <= 1e-6 * max(r_out, r_in, 1e-12):
            continue
        start_off = ring_tube_r_m if k == 0 else trims[k - 1]
        avail = max(seg_lens[k] - start_off - (trims[k] if k < n_pipes - 1 else 0.0), 0.0)
        want = REDUCER_LENGTH_DIA_MULT * 2.0 * max(r_in, r_out)
        length = min(want, avail)
        reducers.append({"pipe_index": k, "r_start_m": r_in, "r_end_m": r_out,
                         "start_offset_m": start_off, "length_m": length})
        half_angle = (90.0 if length <= 0 else
                      math.degrees(math.atan(abs(r_out - r_in) / length)))
        if half_angle > REDUCER_MAX_HALF_ANGLE_DEG:
            where = "the ring inlet" if k == 0 else f"pipe {k}"
            advisories.append(f"Pipe {k + 1}: its reducer from {where} ({2e3 * r_in:.0f} -> "
                              f"{2e3 * r_out:.0f} mm) has a {half_angle:.0f} deg half-angle (> "
                              f"{REDUCER_MAX_HALF_ANGLE_DEG:.0f}) - lengthen pipe {k + 1} for a "
                              "gentler cone.")

    # Bulk velocity per pipe (continuity from the hook's own design point:
    # the full-flow feed bore runs at design_feed_velocity_ms).
    v_feed = float(hook.get("design_feed_velocity_ms", 0.0) or 0.0)
    velocities = [v_feed / (p.bore_scale ** 2) for p in pipes]
    for k, v in enumerate(velocities):
        w = velocity_cap_warning(v, f"Run on {run.host}, pipe {k + 1}", supercritical=supercritical)
        if w:
            advisories.append(w.replace(" manifold bulk velocity", " bulk velocity"))

    wall_t_feed = float(hook.get("feed_wall_thickness_m", hook.get("wall_thickness_m", 0.0)))

    def _flange_dims(r_bore):
        d_local = 2.0 * r_bore
        lip = run.flange_lip_dia_mult * d_local
        width = run.flange_width_dia_mult * d_local
        if run.flange_bolt_count > 0:
            bolts = int(run.flange_bolt_count)
        else:
            wall_t = wall_t_feed * (r_bore / (0.5 * feed_dia)) if feed_dia > 0 else 0.0
            r_bolt_circle = r_bore + wall_t + 0.5 * lip
            bolts = (int(round(2.0 * math.pi * r_bolt_circle / (FLANGE_BOLT_SPACING_DIA_MULT * d_local)))
                     if d_local > 0 else FLANGE_BOLT_MIN_COUNT)
            bolts = min(max(bolts, FLANGE_BOLT_MIN_COUNT), FLANGE_BOLT_MAX_COUNT)
        return {"lip_m": lip, "width_m": width, "bolt_count": bolts}

    flange = _flange_dims(r_pipe)
    # The root flange sits at the torus surface - i.e. on the reducer's ring-
    # bore end when there is one.
    r_root_joint = r_root if (reducers and reducers[0]["pipe_index"] == 0) else r_pipe
    fl_root = _flange_dims(r_root_joint)
    joints = [{"name": "root", "pipe_index": -1,
               "pos": surface + 0.5 * fl_root["width_m"] * frames[0][0] if n_pipes else surface,
               "t": frames[0][0] if n_pipes else t, "n": frames[0][1] if n_pipes else n,
               "b": frames[0][2] if n_pipes else b, "flange": bool(run.flange_at_root),
               "r_m": r_root_joint, "flange_dims": fl_root}]
    for k in range(n_pipes):
        tk_, nk, bk = frames[k]
        fl_k = _flange_dims(radii[k])
        if k < n_pipes - 1:
            name = f"joint_{k + 1}"
            pos = waypoints[k + 1] - (trims[k] + 0.5 * fl_k["width_m"]) * tk_
        else:
            name = "port" if closes else "free_end"
            pos = waypoints[k + 1] - 0.5 * fl_k["width_m"] * tk_
        joints.append({"name": name, "pipe_index": k, "pos": pos, "t": tk_, "n": nk, "b": bk,
                       "flange": bool(pipes[k].flange_at_end), "r_m": radii[k],
                       "flange_dims": fl_k})

    total_length = float(seg_lens.sum() - ring_tube_r_m) if n_pipes else 0.0
    return {
        "waypoints_xyz": waypoints,
        "bend_radii_m": bend_radii,
        "bend_radii_eff_m": bend_radii_eff,
        "tube_radius_m": r_pipe,
        "pipe_dia_m": dia,
        "pipe_radii_m": radii,
        "pipe_velocities_ms": velocities,
        "root_flow_radius_m": r_root,
        "reducers": reducers,
        "segment_lengths_m": [float(v) for v in seg_lens],
        "ring_tube_r_m": float(ring_tube_r_m),
        "segment_dirs": dirs,
        "joint_frames": joints,
        "flange": flange,
        "total_length_m": max(total_length, 0.0),
        "auto_leg_indices": auto_idx,
        "closes_on_port": closes,
        "pipe_kinds": ["auto" if k in auto_idx else "user" for k in range(n_pipes)],
        "advisories": advisories,
    }


def nearest_segment(waypoints_xyz, points_xyz):
    """For each point, the index of the nearest straight pipe segment
    (waypoints k -> k+1) and the distance along it from waypoint k. Shared by
    the render's per-station radius and its selected-pipe tint."""
    wp = np.asarray(waypoints_xyz, dtype=float)
    pts = np.asarray(points_xyz, dtype=float)
    a = wp[:-1]
    d = wp[1:] - a
    d_len2 = np.maximum((d * d).sum(axis=1), 1e-18)
    rel = pts[:, None, :] - a[None, :, :]
    u = np.clip((rel * d[None, :, :]).sum(axis=2) / d_len2[None, :], 0.0, 1.0)
    dist2 = ((rel - u[:, :, None] * d[None, :, :]) ** 2).sum(axis=2)
    idx = dist2.argmin(axis=1)
    along = u[np.arange(len(pts)), idx] * np.sqrt(d_len2[idx])
    return idx, along


def centerline_radii(resolved, centerline_xyz):
    """Flow radius at each rendered centreline station: each pipe's own bore,
    coned through its reducer (linear in distance along the pipe). Elbow
    samples take the upstream pipe's bore (a reducer starts after its elbow);
    stations inside the torus take the ring's bore."""
    radii = resolved["pipe_radii_m"]
    if not radii:
        return np.zeros(len(centerline_xyz))
    idx, along = nearest_segment(resolved["waypoints_xyz"], centerline_xyz)
    red = {r["pipe_index"]: r for r in resolved["reducers"]}
    out = np.empty(len(idx))
    for i, (k, s_along) in enumerate(zip(idx, along)):
        rd = red.get(int(k))
        if rd is None:
            out[i] = radii[k]
            continue
        s_rel = s_along - rd["start_offset_m"]
        if s_rel <= 0.0:
            out[i] = rd["r_start_m"]
        elif rd["length_m"] <= 0.0 or s_rel >= rd["length_m"]:
            out[i] = rd["r_end_m"]
        else:
            f = s_rel / rd["length_m"]
            out[i] = rd["r_start_m"] + f * (rd["r_end_m"] - rd["r_start_m"])
    return out


def plumbing_mass_kg(hook, resolved, density_kg_m3=MANIFOLD_DENSITY_KG_M3):
    """Pipe + reducer + flange mass for one resolved run (see module
    docstring). Each pipe's wall is the feed bore's hoop-stress wall scaled
    to its own bore (constant t/r - the same hoop rule, same pressure);
    a reducer's length is costed at its mean radius."""
    r_feed = 0.5 * float(hook["inner_diameter_m"])
    t_feed = float(hook.get("feed_wall_thickness_m", hook.get("wall_thickness_m", 0.0)))
    k_wall = t_feed / r_feed if r_feed > 0 else 0.0

    def _shell(r, length):
        t = k_wall * r
        return math.pi * ((r + t) ** 2 - r ** 2) * max(length, 0.0) * density_kg_m3

    radii = resolved.get("pipe_radii_m") or []
    seg_lens = resolved.get("segment_lengths_m") or []
    red = {rd["pipe_index"]: rd for rd in resolved.get("reducers") or []}
    pipe_kg = 0.0
    for k, r in enumerate(radii):
        length = seg_lens[k] - (resolved.get("ring_tube_r_m", 0.0) if k == 0 else 0.0)
        rd = red.get(k)
        if rd is not None and rd["length_m"] > 0:
            pipe_kg += _shell(0.5 * (rd["r_start_m"] + rd["r_end_m"]), rd["length_m"])
            length -= rd["length_m"]
        pipe_kg += _shell(r, length)
    flange_kg = 0.0
    for j in resolved["joint_frames"]:
        if j["flange"]:
            r = j.get("r_m", resolved["tube_radius_m"])
            fd = j.get("flange_dims", resolved["flange"])
            t = k_wall * r
            flange_kg += (math.pi * ((r + t + fd["lip_m"]) ** 2 - (r + t) ** 2) * fd["width_m"]
                          * density_kg_m3)
    return pipe_kg + flange_kg, pipe_kg, flange_kg


def _interp_table(table, x):
    xs, ys = zip(*table)
    return float(np.interp(x, xs, ys))


def liquid_viscosity_pa_s(pair, host):
    """Dynamic viscosity of the liquid a `host`'s run carries: fuel from
    cooling.COOLANT_TRANSPORT, oxidizer from OX_VISCOSITY_PA_S (Tier 3)."""
    if host == "turbine_exhaust":
        return EXHAUST_GAS_VISCOSITY_PA_S
    if HOST_PUMP.get(host) == "ox_pump":
        return OX_VISCOSITY_PA_S.get(str(pair).split("/")[0], _OX_VISCOSITY_FALLBACK)
    return COOLANT_TRANSPORT.get(pair, _COOLANT_TRANSPORT_FALLBACK)[1]


def feed_density_kg_m3(hook):
    """rho from the hook's own design point: the full-flow feed bore carries
    mdot_kgs at design_feed_velocity_ms."""
    v = float(hook.get("design_feed_velocity_ms", 0.0) or 0.0)
    d = float(hook.get("inner_diameter_m", 0.0) or 0.0)
    mdot = float(hook.get("mdot_kgs", 0.0) or 0.0)
    if v <= 0 or d <= 0 or mdot <= 0:
        return 0.0
    return mdot / (v * math.pi * 0.25 * d * d)


def run_pressure_loss_pa(resolved, hook, viscosity_pa_s):
    """Static-pressure loss along one resolved run carrying the hook's full
    mdot (the line from the pump to the ring): Darcy friction on each straight
    (cooling._darcy_friction, PIPE_ROUGHNESS_M) + elbow K (ELBOW_K90_BY_RD x
    turn/90) + reducer K (REDUCER_K_BY_HALF_ANGLE, at the smaller bore) + the
    RING_ENTRY_K dump into the ring (Borda-Carnot: the full flow at 2V in the
    inlet bore splits into two branches at the ring's design velocity V, loss
    = rho(2V-V)^2/2 = one ring velocity head). Returns
    (total_pa, {"friction_pa", "elbows_pa", "reducers_pa", "entry_pa"})."""
    parts = {"friction_pa": 0.0, "elbows_pa": 0.0, "reducers_pa": 0.0, "entry_pa": 0.0}
    rho = feed_density_kg_m3(hook)
    mdot = float(hook.get("mdot_kgs", 0.0) or 0.0)
    radii = resolved.get("pipe_radii_m") or []
    if rho <= 0 or not radii:
        return 0.0, parts

    def _q(r):
        v = mdot / (rho * math.pi * r * r) if r > 0 else 0.0
        return 0.5 * rho * v * v, v

    seg_lens = resolved["segment_lengths_m"]
    for k, r in enumerate(radii):
        length = seg_lens[k] - (resolved.get("ring_tube_r_m", 0.0) if k == 0 else 0.0)
        q, v = _q(r)
        re = rho * v * 2.0 * r / viscosity_pa_s if viscosity_pa_s > 0 else 1e7
        f = _darcy_friction(re, 2.0 * r, PIPE_ROUGHNESS_M)
        parts["friction_pa"] += f * max(length, 0.0) / (2.0 * r) * q
    dirs = resolved["segment_dirs"]
    for k in range(1, len(radii)):
        turn = math.degrees(math.acos(float(np.clip(np.dot(dirs[k - 1], dirs[k]), -1.0, 1.0))))
        r_d = resolved["bend_radii_eff_m"][k - 1] / (2.0 * radii[k])
        parts["elbows_pa"] += _interp_table(ELBOW_K90_BY_RD, r_d) * turn / 90.0 * _q(radii[k])[0]
    for rd in resolved.get("reducers") or []:
        half = (90.0 if rd["length_m"] <= 0 else
                math.degrees(math.atan(abs(rd["r_end_m"] - rd["r_start_m"]) / rd["length_m"])))
        r_small = min(rd["r_start_m"], rd["r_end_m"])
        parts["reducers_pa"] += _interp_table(REDUCER_K_BY_HALF_ANGLE, half) * _q(r_small)[0]
    v_ring = float(hook.get("design_feed_velocity_ms", 0.0) or 0.0)
    parts["entry_pa"] = RING_ENTRY_K * 0.5 * rho * v_ring * v_ring
    return sum(parts.values()), parts


def seed_route_to_port(hook, port, ring_center_r_m, ring_tube_r_m, host="jacket_inlet",
                       bend_radius_dia_mult=1.0):
    """The Shape Lab's "Route to pump" seed: an editable, orthogonal run from
    the ring toward `port` (a turbopump_ports discharge dict), with
    connect_to_pump set so resolve_run's auto legs finish it.

    The standoff point S (port.pos + port_standoff x bore x port.dir) fixes the
    plane: the run attaches at S's angle around the engine, pipe 1 leaves
    radially to just inside S's radius (a 90-deg approach clearance below it),
    pipe 2 runs axially to S's station (split into <= PIPE_LENGTH_DIA_MULT_MAX
    chunks), and auto leg A then turns outward to S along a direction square
    to the port axis, leg B into the port - every corner ~90 deg. If S is too
    close to the ring's radius for an inward approach, pipe 1 overshoots it
    and leg A comes back in instead."""
    dia = float(hook["inner_diameter_m"])
    run = PlumbingRun(role=HOST_RING_ROLE.get(host, "coolant_supply_manifold"), host=host,
                      connect_to_pump=True)
    role_pipe = HOST_PIPE_ROLE.get(host, "coolant_supply")
    p_dir = np.asarray(port["dir"], dtype=float)
    p_dir = p_dir / np.linalg.norm(p_dir)
    d_port = float(port.get("dia_m") or 0.0) or dia
    s_pt = np.asarray(port["pos"], dtype=float) + run.port_standoff_dia_mult * d_port * p_dir
    # Approach S along u: S's radial direction with its port-axis component
    # removed, so leg A meets both the axial pipe 2 and leg B at ~90 deg.
    radial_s = np.array([0.0, s_pt[1], s_pt[2]])
    u = radial_s - np.dot(radial_s, p_dir) * p_dir
    u = u / np.linalg.norm(u) if np.linalg.norm(u) > 1e-12 else np.array([0.0, 1.0, 0.0])
    surface_r = ring_center_r_m + ring_tube_r_m
    clearance = SEED_APPROACH_DIA_MULT * d_port
    r_root_guess = _root_flow_radius_m(hook, float(hook.get("attach_angular_position_deg", 0.0)))
    l1_min = (REDUCER_LENGTH_DIA_MULT * max(2.0 * r_root_guess / dia, 1.0) + bend_radius_dia_mult
              + 0.1) * dia
    p_end = s_pt - clearance * u
    if math.hypot(p_end[1], p_end[2]) - surface_r < l1_min:
        p_end = s_pt + clearance * u        # too close to the ring: overshoot, come back in
    run.attach_angle_deg = math.degrees(math.atan2(p_end[2], p_end[1])) % 360.0
    l1 = max(math.hypot(p_end[1], p_end[2]) - surface_r, l1_min)
    pipes = [PipeSegment(role=role_pipe, length_dia_mult=_clamp(l1 / dia, PIPE_LENGTH_DIA_MULT_MIN,
                                                                PIPE_LENGTH_DIA_MULT_MAX),
                         bend_radius_dia_mult=bend_radius_dia_mult)]
    dx = float(s_pt[0] - hook["attach_axial_station_m"])
    if abs(dx) > 2.0 * dia:
        n_chunks = max(1, math.ceil(abs(dx) / dia / PIPE_LENGTH_DIA_MULT_MAX))
        for i in range(n_chunks):
            pipes.append(PipeSegment(
                role=role_pipe, length_dia_mult=abs(dx) / dia / n_chunks,
                pitch_deg=(90.0 if dx < 0 else -90.0) if i == 0 else 0.0,
                bend_radius_dia_mult=bend_radius_dia_mult))
    run.pipes = pipes
    return run


def default_run_for_host(hook, ring_tube_r_m, host="jacket_inlet", bend_radius_dia_mult=None):
    """A seed run reproducing gui/mesh_builder.py's legacy auto-drawn duct on
    that ring: radially out to the corner, then a stub toward -x. Pipe 1's
    length is from the torus SURFACE, hence the ring_tube_r_m correction.
    `bend_radius_dia_mult` overrides the elbow (the 3D preview's cosmetic
    duct-bend slider); the corner standoff and stub scale with it, as the
    legacy duct's did."""
    dia = float(hook["inner_diameter_m"])
    mult = (_LEGACY_DUCT_BEND_RADIUS_DIA_MULT if bend_radius_dia_mult is None
            else float(bend_radius_dia_mult))
    bend = mult * dia
    l1 = max((_LEGACY_DUCT_STANDOFF_BEND_RADIUS_MULT * bend - ring_tube_r_m) / dia,
             PIPE_LENGTH_DIA_MULT_MIN)
    l2 = _LEGACY_DUCT_STUB_BEND_RADIUS_MULT * bend / dia
    # A tapered header ring's inlet bore is smaller than the feed bore: leave
    # pipe 1 room for its full-length root reducer plus the elbow's trim.
    r_root = _root_flow_radius_m(hook, float(hook.get("attach_angular_position_deg", 0.0)))
    if abs(r_root - 0.5 * dia) > 1e-6 * dia:
        l1 = max(l1, REDUCER_LENGTH_DIA_MULT * max(2.0 * r_root / dia, 1.0) + mult + 0.1)
    role_pipe = HOST_PIPE_ROLE.get(host, "coolant_supply")
    role_ring = HOST_RING_ROLE.get(host, "coolant_supply_manifold")
    if host == "turbine_exhaust":
        # One short stub off the termination (forward, off an overboard
        # exhaust nozzle's inlet; radially out of a ring), then the auto legs
        # close it onto the turbine's exhaust port.
        point = bool(hook.get("point_hook"))
        return PlumbingRun(
            role=role_ring, host=host,
            attach_angle_deg=float(hook.get("attach_angular_position_deg", 0.0)),
            attach_poloidal_deg=90.0 if point else 0.0, connect_to_pump=True,
            pipes=[PipeSegment(role=role_pipe, length_dia_mult=max(l1, 2.0))])
    return PlumbingRun(
        role=role_ring, host=host,
        attach_angle_deg=float(hook.get("attach_angular_position_deg", 0.0)),
        attach_poloidal_deg=0.0,
        pipes=[PipeSegment(role=role_pipe, length_dia_mult=l1),
               PipeSegment(role=role_pipe, length_dia_mult=l2, pitch_deg=90.0,
                           bend_radius_dia_mult=mult)])


def runs_for_host(plumbing_runs, host):
    """The runs (dicts or PlumbingRuns) in an EngineDesign.plumbing_runs list
    rooted on `host`."""
    out = []
    for r in plumbing_runs or []:
        h = r.host if isinstance(r, PlumbingRun) else (r or {}).get("host")
        if h == host:
            out.append(r)
    return out


def self_test():
    hook = {"attach_axial_station_m": 1.2, "attach_radial_offset_m": 0.5,
            "attach_angular_position_deg": 0.0, "attach_direction_xyz": (0.0, 1.0, 0.0),
            "inner_diameter_m": 0.10, "mdot_kgs": 50.0, "design_feed_velocity_ms": 15.0,
            "wall_thickness_m": 0.003}
    ring_r, ring_tube = 0.5, 0.053

    # --- dict round trip + clamping ---
    run = default_run_for_host(hook, ring_tube)
    d = run_to_dict(run)
    assert isinstance(d["pipes"][0], dict)
    assert run_from_dict(d) == run
    bad = run_from_dict({"host": "jacket_inlet", "pipes": [{"yaw_deg": 400.0, "length_dia_mult": 0.0}]})
    assert bad.pipes[0].yaw_deg == PIPE_TURN_DEG_MAX
    assert bad.pipes[0].length_dia_mult == PIPE_LENGTH_DIA_MULT_MIN
    print("run_to_dict/run_from_dict round trip + clamp: OK")

    # --- legacy duct reproduction: [centre, corner, stub_end] equals the old
    # mesh_builder._fuel_inlet_duct_waypoints reversed ---
    res = resolve_run(run, hook, ring_r, ring_tube)
    wp = res["waypoints_xyz"]
    dia = hook["inner_diameter_m"]
    bend = 0.5 * dia
    attach = np.array([1.2, ring_r, 0.0])
    corner = attach + 2.5 * bend * np.array([0.0, 1.0, 0.0])
    stub_end = corner + 2.1 * bend * np.array([-1.0, 0.0, 0.0])
    assert np.allclose(wp, [attach, corner, stub_end], atol=1e-9), wp
    assert res["bend_radii_m"] == [bend]
    assert not res["advisories"], res["advisories"]
    assert np.isclose(res["total_length_m"], 2.5 * bend - ring_tube + 2.1 * bend)
    print("default_run_for_host reproduces the legacy auto duct: OK")

    # --- poloidal angle: 0 outer equator, +90 forward crown, 180 inner equator ---
    for pol, expect in ((0.0, [1.2, ring_r + ring_tube, 0.0]),
                        (90.0, [1.2 - ring_tube, ring_r, 0.0]),
                        (180.0, [1.2, ring_r - ring_tube, 0.0]),
                        (270.0, [1.2 + ring_tube, ring_r, 0.0])):
        r1 = PlumbingRun(attach_poloidal_deg=pol, pipes=[PipeSegment(length_dia_mult=1.0)])
        rr = resolve_run(r1, hook, ring_r, ring_tube)
        surf = rr["joint_frames"][0]["pos"] - 0.5 * rr["flange"]["width_m"] * rr["joint_frames"][0]["t"]
        assert np.allclose(surf, expect, atol=1e-9), (pol, surf)
    assert any("inward" in a for a in resolve_run(PlumbingRun(attach_poloidal_deg=180.0,
               pipes=[PipeSegment()]), hook, ring_r, ring_tube)["advisories"])
    # attach angle 90 -> ring point on +z
    rr = resolve_run(PlumbingRun(attach_angle_deg=90.0, pipes=[PipeSegment()]), hook, ring_r, ring_tube)
    assert np.allclose(rr["waypoints_xyz"][0], [1.2, 0.0, ring_r], atol=1e-9)
    print("attach angle / poloidal angle placement: OK")

    # --- yaw / pitch give orthogonal directions, frames stay orthonormal ---
    base = PipeSegment(length_dia_mult=3.0)
    for yaw, pitch in ((90.0, 0.0), (-90.0, 0.0), (0.0, 90.0), (0.0, -90.0)):
        r2 = PlumbingRun(pipes=[base, PipeSegment(length_dia_mult=3.0, yaw_deg=yaw, pitch_deg=pitch)])
        rr = resolve_run(r2, hook, ring_r, ring_tube)
        d0, d1 = rr["segment_dirs"]
        assert abs(np.dot(d0, d1)) < 1e-9, (yaw, pitch, d0, d1)
        for j in rr["joint_frames"]:
            m = np.stack([j["t"], j["n"], j["b"]])
            assert np.allclose(m @ m.T, np.eye(3), atol=1e-9)
            assert np.allclose(np.cross(j["t"], j["n"]), j["b"], atol=1e-9)
    # +pitch on a radial pipe at the outer equator bends toward -x (forward)
    rr = resolve_run(PlumbingRun(pipes=[base, PipeSegment(pitch_deg=90.0)]), hook, ring_r, ring_tube)
    assert np.allclose(rr["segment_dirs"][1], [-1.0, 0.0, 0.0], atol=1e-9)
    # +yaw swings around the circumference (toward -b = -z at angle 0)
    rr = resolve_run(PlumbingRun(pipes=[base, PipeSegment(yaw_deg=90.0)]), hook, ring_r, ring_tube)
    assert np.allclose(rr["segment_dirs"][1], [0.0, 0.0, -1.0], atol=1e-9)
    print("yaw/pitch turn conventions: OK")

    # --- n=5 chain: counts, monotone mass, flanges ---
    pipes = [PipeSegment(length_dia_mult=2.0 + k, yaw_deg=20.0 * k, pitch_deg=-15.0 * k,
                         bend_radius_dia_mult=1.0, flange_at_end=(k % 2 == 0)) for k in range(5)]
    r5 = PlumbingRun(pipes=pipes, flange_at_root=True)
    rr = resolve_run(r5, hook, ring_r, ring_tube)
    assert rr["waypoints_xyz"].shape == (6, 3)
    assert len(rr["bend_radii_m"]) == 4
    assert len(rr["joint_frames"]) == 6
    assert [j["name"] for j in rr["joint_frames"]] == ["root", "joint_1", "joint_2", "joint_3",
                                                        "joint_4", "free_end"]
    assert sum(j["flange"] for j in rr["joint_frames"]) == 1 + 3
    assert not np.any(np.isnan(rr["waypoints_xyz"]))
    # unclamped corners: effective == requested
    assert rr["bend_radii_eff_m"] == rr["bend_radii_m"]
    # a too-big elbow between two short straights: the resolver clamps the
    # EFFECTIVE radius (and says so) so that fillet_polyline, fed that
    # effective value, reproduces the identical trim without warning
    r_big = PlumbingRun(pipes=[PipeSegment(length_dia_mult=1.0),
                               PipeSegment(length_dia_mult=1.0, yaw_deg=90.0,
                                           bend_radius_dia_mult=4.0),
                               PipeSegment(length_dia_mult=1.0, yaw_deg=90.0,
                                           bend_radius_dia_mult=4.0)])
    rb = resolve_run(r_big, hook, ring_r, ring_tube)
    assert rb["bend_radii_eff_m"][1] < rb["bend_radii_m"][1]
    assert np.isclose(rb["bend_radii_eff_m"][1],
                      FILLET_TRIM_MAX_SEGMENT_FRACTION * 1.0 * rb["pipe_dia_m"])  # 90 deg: trim == R
    assert any("rendered at" in a for a in rb["advisories"])
    total, pipe_kg, flange_kg = plumbing_mass_kg(hook, rr)
    assert total > 0 and pipe_kg > 0 and flange_kg > 0 and np.isclose(total, pipe_kg + flange_kg)
    # mass linear in length: doubling every length doubles pipe mass (+ the same buried offset)
    pipes2 = [PipeSegment(length_dia_mult=2 * p.length_dia_mult, yaw_deg=p.yaw_deg,
                          pitch_deg=p.pitch_deg, bend_radius_dia_mult=1.0) for p in pipes]
    rr2 = resolve_run(PlumbingRun(pipes=pipes2), hook, ring_r, ring_tube)
    _, pipe_kg2, _ = plumbing_mass_kg(hook, rr2)
    expected = pipe_kg * (rr2["total_length_m"] / rr["total_length_m"])
    assert np.isclose(pipe_kg2, expected)
    assert FLANGE_BOLT_MIN_COUNT <= rr["flange"]["bolt_count"] <= FLANGE_BOLT_MAX_COUNT
    assert resolve_run(PlumbingRun(flange_bolt_count=7, pipes=[base]), hook, ring_r, ring_tube)["flange"]["bolt_count"] == 7
    print("5-pipe chain counts / mass / flange style: OK")

    # --- advisories: too-short segment for its elbow; >90 combined turn ---
    short = PlumbingRun(pipes=[base, PipeSegment(length_dia_mult=0.5, bend_radius_dia_mult=1.0, pitch_deg=90.0)])
    adv = resolve_run(short, hook, ring_r, ring_tube)["advisories"]
    assert any("elbow" in a for a in adv), adv
    # With yaw/pitch each clamped to +/-90 the composed turn can't exceed 90
    # (cos(turn) = cos(yaw)*cos(pitch) >= 0), so only an unclamped direct
    # construction (hand-edited file bypassing run_from_dict) can reach it.
    tight = PlumbingRun(pipes=[base, PipeSegment(length_dia_mult=6.0, yaw_deg=120.0)])
    adv = resolve_run(tight, hook, ring_r, ring_tube)["advisories"]
    assert any("combined" in a for a in adv), adv
    print("advisories (short segment, tight turn): OK")

    # --- empty run + host lookups ---
    rr0 = resolve_run(PlumbingRun(), hook, ring_r, ring_tube)
    assert rr0["waypoints_xyz"].shape == (1, 3) and rr0["total_length_m"] == 0.0
    assert plumbing_mass_kg(hook, rr0)[0] == 0.0
    result = {"jacket_manifold_result": {"jacket_inlet": hook, "jacket_return": None},
              "manifold_result": {"fuel": hook, "ox": hook}}
    assert hook_for_host(result, "jacket_inlet") is hook
    assert hook_for_host(result, "jacket_return") is None
    assert hook_for_host(result, "nope") is None
    assert hook_for_host({"jacket_manifold_result": None}, "jacket_inlet") is None
    assert len(runs_for_host([run_to_dict(run), {"host": "fuel"}], "jacket_inlet")) == 1
    print("empty run / hook_for_host / runs_for_host: OK")

    # Per-host display/role tables stay in lockstep with HOSTS.
    for _name, _tbl in (("HOST_LABELS", HOST_LABELS), ("HOST_MISSING_HINT", HOST_MISSING_HINT),
                        ("HOST_RING_ROLE", HOST_RING_ROLE), ("HOST_PIPE_ROLE", HOST_PIPE_ROLE)):
        assert set(_tbl) == set(HOSTS), f"{_name} keys != HOSTS keys"
    assert set(HOST_RING_ROLE.values()) <= set(ROLES) and set(HOST_PIPE_ROLE.values()) <= set(ROLES)
    for _h in HOSTS:
        _r = default_run_for_host(hook, ring_tube, _h)
        assert _r.host == _h and _r.role == HOST_RING_ROLE[_h]
        assert all(p.role == HOST_PIPE_ROLE[_h] for p in _r.pipes)
    print("per-host label/hint/role tables match HOSTS: OK")
    # --- per-segment bores + reducers ---
    # A tapered split ring (manifold._assemble fields): pipe 1 leaves at the
    # ring's local inlet bore and cones out to the full-flow feed bore.
    thook = dict(hook, inlet_flow_radius_m=0.05 / math.sqrt(2.0), min_flow_radius_m=0.02,
                 taper_blend=0.5, flow_radius_m=0.05 / math.sqrt(2.0),
                 feed_wall_thickness_m=0.003)
    trun = PlumbingRun(pipes=[PipeSegment(length_dia_mult=4.0),
                              PipeSegment(length_dia_mult=4.0, pitch_deg=60.0, bore_scale=0.7)])
    tres = resolve_run(trun, thook, ring_r, ring_tube)
    assert np.isclose(tres["root_flow_radius_m"], ring_flow_radius_at(thook, 0.0))
    assert [rd["pipe_index"] for rd in tres["reducers"]] == [0, 1]
    assert np.isclose(tres["reducers"][0]["r_start_m"], tres["root_flow_radius_m"])
    assert np.isclose(tres["pipe_radii_m"][1], 0.7 * 0.05)
    assert np.isclose(tres["pipe_velocities_ms"][1], 15.0 / 0.49)
    # the rendered radius: ring bore at the torus surface, pipe 1's bore past
    # its reducer, pipe 2's bore at the free end
    surf = np.array([1.2, ring_r + ring_tube, 0.0])
    t_dir = tres["segment_dirs"][0]
    probe = np.array([surf, surf + (tres["reducers"][0]["length_m"] + 0.01) * t_dir,
                      tres["waypoints_xyz"][-1]])
    rr = centerline_radii(tres, probe)
    assert np.allclose(rr, [tres["root_flow_radius_m"], 0.05, 0.035]), rr
    # bore_scale 1 everywhere + an untapered hook: identical waypoints, no reducer
    plain = resolve_run(PlumbingRun(pipes=[PipeSegment(length_dia_mult=4.0),
                                           PipeSegment(length_dia_mult=4.0, pitch_deg=60.0)]),
                        hook, ring_r, ring_tube)
    assert not plain["reducers"]
    assert np.allclose(plain["waypoints_xyz"][:2], tres["waypoints_xyz"][:2])
    # mass rises with bore; an old run dict with no bore_scale loads at 1.0
    m_small = plumbing_mass_kg(hook, resolve_run(PlumbingRun(pipes=[PipeSegment(bore_scale=0.8)]),
                                                 hook, ring_r, ring_tube))[0]
    m_big = plumbing_mass_kg(hook, resolve_run(PlumbingRun(pipes=[PipeSegment(bore_scale=1.3)]),
                                               hook, ring_r, ring_tube))[0]
    assert m_big > m_small > 0.0
    assert run_from_dict({"pipes": [{"length_dia_mult": 2.0}]}).pipes[0].bore_scale == 1.0
    assert run_from_dict({"pipes": [{"bore_scale": 9.0}]}).pipes[0].bore_scale == PIPE_BORE_SCALE_MAX
    # a fast pipe is warned (liquid), not for LH2
    fast = PlumbingRun(pipes=[PipeSegment(bore_scale=0.4)])   # 15 / 0.16 = 94 m/s
    assert any("61 m/s" in a for a in resolve_run(fast, hook, ring_r, ring_tube)["advisories"])
    assert not any("61 m/s" in a for a in resolve_run(fast, hook, ring_r, ring_tube,
                                                      supercritical=True)["advisories"])
    print("per-segment bores / reducers / velocity advisories: OK")

    # --- pump-port closure (connect_to_pump + auto legs) ---
    port = {"pos": np.array([0.1, 0.9, -0.25]), "dir": np.array([0.0, 0.0, -1.0]), "dia_m": 0.10}
    conn = PlumbingRun(connect_to_pump=True, pipes=[PipeSegment(length_dia_mult=3.0),
                                                    PipeSegment(length_dia_mult=5.0, pitch_deg=90.0,
                                                                bend_radius_dia_mult=1.0)])
    cres = resolve_run(conn, hook, ring_r, ring_tube, port=port)
    assert cres["closes_on_port"] and cres["auto_leg_indices"] == [2, 3]
    assert np.linalg.norm(cres["waypoints_xyz"][-1] - port["pos"]) < 1e-9
    assert np.allclose(cres["segment_dirs"][-1], -port["dir"])
    assert cres["joint_frames"][-1]["name"] == "port" and cres["joint_frames"][-1]["flange"]
    # a different ring radius (the render's) still lands on the port
    cres2 = resolve_run(conn, hook, ring_r * 1.05, ring_tube, port=port)
    assert np.linalg.norm(cres2["waypoints_xyz"][-1] - port["pos"]) < 1e-9
    # not connected / no port -> no auto legs; the flag never survives on jacket_return
    assert not resolve_run(conn, hook, ring_r, ring_tube)["auto_leg_indices"]
    assert not resolve_run(PlumbingRun(pipes=conn.pipes), hook, ring_r, ring_tube,
                           port=port)["auto_leg_indices"]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert not run_from_dict({"host": "jacket_return", "connect_to_pump": True}).connect_to_pump
    assert run_from_dict({"pipes": []}).connect_to_pump is False
    assert set(HOST_PUMP) == set(HOSTS) and set(CONNECTABLE_HOSTS) <= set(HOSTS)
    assert set(HOST_PORT) == set(HOSTS)
    assert port_for_host({"turbine": {"exhaust": {"pos": 1}}}, "turbine_exhaust") == {"pos": 1}
    assert port_for_host({"ox_pump": {"discharge": {"pos": 2}}}, "ox") == {"pos": 2}
    assert port_for_host({}, "fuel") is None
    # seed route: lands on the port, every corner <= 90 deg, no advisories
    seed = seed_route_to_port(hook, port, ring_r, ring_tube)
    sres = resolve_run(seed, hook, ring_r, ring_tube, port=port)
    assert np.linalg.norm(sres["waypoints_xyz"][-1] - port["pos"]) < 1e-9
    assert not sres["advisories"], sres["advisories"]
    print("pump-port closure + seed route: OK")

    # --- line pressure loss ---
    straight = resolve_run(PlumbingRun(pipes=[PipeSegment(length_dia_mult=10.0)]),
                           hook, ring_r, ring_tube)
    mu = 7.5e-4
    loss, parts = run_pressure_loss_pa(straight, hook, mu)
    rho = feed_density_kg_m3(hook)
    r0 = straight["pipe_radii_m"][0]
    v0 = hook["mdot_kgs"] / (rho * math.pi * r0 * r0)
    f0 = _darcy_friction(rho * v0 * 2 * r0 / mu, 2 * r0, PIPE_ROUGHNESS_M)
    assert not straight["reducers"]       # untapered hook: no root reducer
    l0 = straight["segment_lengths_m"][0] - ring_tube
    assert abs(parts["friction_pa"] - f0 * l0 / (2 * r0) * 0.5 * rho * v0 * v0) < 1e-9 * loss
    assert abs(parts["entry_pa"] - RING_ENTRY_K * 0.5 * rho * hook["design_feed_velocity_ms"] ** 2) < 1e-9
    assert parts["elbows_pa"] == 0.0 and loss > 0
    bent = resolve_run(PlumbingRun(pipes=[PipeSegment(length_dia_mult=4.0),
                                          PipeSegment(length_dia_mult=4.0, pitch_deg=90.0),
                                          PipeSegment(length_dia_mult=4.0, yaw_deg=90.0)]),
                       hook, ring_r, ring_tube)
    one_bend = resolve_run(PlumbingRun(pipes=[PipeSegment(length_dia_mult=4.0),
                                              PipeSegment(length_dia_mult=8.0, pitch_deg=90.0)]),
                           hook, ring_r, ring_tube)
    assert run_pressure_loss_pa(bent, hook, mu)[1]["elbows_pa"] > \
        run_pressure_loss_pa(one_bend, hook, mu)[1]["elbows_pa"] > 0
    fast_hook = dict(hook, mdot_kgs=2 * hook["mdot_kgs"], design_feed_velocity_ms=30.0)
    ratio = run_pressure_loss_pa(one_bend, fast_hook, mu)[1]["elbows_pa"] / \
        run_pressure_loss_pa(one_bend, hook, mu)[1]["elbows_pa"]
    assert abs(ratio - 4.0) < 1e-9, ratio      # K-losses scale with V^2
    assert liquid_viscosity_pa_s("LOX/RP-1", "ox") == OX_VISCOSITY_PA_S["LOX"]
    assert liquid_viscosity_pa_s("LOX/RP-1", "jacket_inlet") == COOLANT_TRANSPORT["LOX/RP-1"][1]
    print(f"line pressure loss: OK (10-dia straight {loss / 1e3:.1f} kPa, "
          f"connected seed {run_pressure_loss_pa(sres, hook, mu)[0] / 1e3:.1f} kPa)")

    print("ALL PLUMBING CHECKS OK")


if __name__ == "__main__":
    self_test()
