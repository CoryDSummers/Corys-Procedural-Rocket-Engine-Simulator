"""
Pure-numpy scene assembly for the Shape Lab (gui/shape_lab.py). No Tk/OpenGL/
matplotlib import, so this is headlessly testable here (see CLAUDE.md
convention #4 - the same split gui/preview3d_gl_core/ and gui/mesh_builder.py
already use for exactly this reason).

Two scenes:

- build_plumbing_scene(): the REAL thing since the procedural-plumbing round -
  the loaded design's actual host manifold ring (jacket_inlet by default) at
  real scale, the run being edited (physics/plumbing.py PlumbingRun) drawn
  by the very same gui/mesh_builder.build_plumbing_pieces the main 3D
  preview uses for a baked run (so what you see IS what bakes), the selected
  pipe tinted, and optional pale "ghosts" of the chamber/nozzle wall and of
  the turbopump assembly for context (a flat pale tint, NOT transparency -
  the GL shader has no alpha path), plus a thin straight "ray" from the run's
  free end to the pump it will feed (HOST_PUMP) - a placeholder for the real
  connecting pipes of a future round. Bounds come from the ring + run +
  ghost turbopump + ray (not the ghost wall) so a long run still fits.

- build_manifold_test_pieces(): the original fixed-scale synthetic ring +
  legacy 3-waypoint duct, kept as the FALLBACK scene when the design has no
  host ring to root a run on (a non-regen chamber has no jacket_inlet ring),
  and as an isolated visual check of the three legacy duct parameters
  (intake angle / bend-radius ratio / rotation). These three no longer bake
  onto EngineDesign (the dead-stored fields were removed in schema 4); the
  Lab's plumbing panel is the real editor now.
"""
import numpy as np

from .preview3d_gl_core import (
    DUCT_APPROACH_STANDOFF_BEND_RADIUS_MULT,
    DUCT_STUB_LENGTH_BEND_RADIUS_MULT,
    HARDWARE_SHININESS,
    HARDWARE_SPECULAR_STRENGTH,
    RAY_N_THETA,
    RAY_RADIUS_TUBE_R_MULT,
    bent_tube_duct_mesh,
    manifold_ring_mesh,
    mesh_from_grid,
    ray_mesh,
    revolve_to_buffers,
)
from . import mesh_builder
from ..physics import geometry3d, plumbing

# Plumbing scene look: same ring/pipe tints per host as mesh_builder's main
# preview (jacket rings olive, fuel/ox grey-blue/tan), pale ghost wall.
PLUMBING_HOST_RGB = {"jacket_inlet": (0.56, 0.56, 0.20), "jacket_return": (0.56, 0.56, 0.20),
                     "fuel": (0.55, 0.62, 0.75), "ox": (0.70, 0.60, 0.55)}
GHOST_WALL_RGB = (0.80, 0.83, 0.86)
GHOST_WALL_N_THETA = 32
GHOST_TURBOPUMP_RGB = (0.72, 0.76, 0.82)   # a shade darker/bluer than the wall so the two read apart
RAY_RGB = (0.95, 0.35, 0.20)               # warm, unlike any pipe/selection tint
SCENE_PADDING_FRACTION = 0.15
# Which pump each host's run is heading for - the ray target. Every fuel-side
# ring (both jacket rings are coolant = fuel) feeds from the fuel pump.
HOST_PUMP = plumbing.HOST_PUMP   # moved to physics/plumbing.py (pump-port runs)

# Fixed-scale synthetic scene - independent of any real design's units, sized
# purely so the ring + duct read clearly at a consistent zoom level.
SYNTHETIC_RING_X0_M = 0.0
SYNTHETIC_RING_MAJOR_R_M = 0.4
SYNTHETIC_RING_TUBE_R_M = 0.05
# Real fuel-inlet ducts run almost as thick as the manifold ring's own tube
# cross-section (physics/manifold.py::_assemble - duct radius = r_flow, ring
# tube radius = r_flow + wall_t, a thin hoop-stress correction - verified
# ~0.98:1 across engine scales). Match that ratio here instead of an
# arbitrary one, so the synthetic scene reads proportionally like a real design.
SYNTHETIC_DUCT_TO_RING_TUBE_RADIUS_RATIO = 0.98
SYNTHETIC_TUBE_INNER_DIA_M = 2.0 * SYNTHETIC_RING_TUBE_R_M * SYNTHETIC_DUCT_TO_RING_TUBE_RADIUS_RATIO
SYNTHETIC_N_THETA_MAIN = 24
SYNTHETIC_N_THETA_TUBE = 12
SYNTHETIC_RING_COLOR = (0.55, 0.62, 0.75)
SYNTHETIC_DUCT_COLOR = (0.70, 0.60, 0.55)


def _synthetic_hook(intake_angle_deg, rotation_deg):
    """
    Build a HOOK_POINT_FIELDS-shaped dict (physics/manifold.py) for the fixed
    synthetic ring, at angular position `rotation_deg` around the main axis,
    with its approach direction tilted `intake_angle_deg` away from pure
    radial (0 deg) toward upstream-axial (-x) - i.e. the angle between the
    intake duct's final approach segment and the manifold ring's own radial
    normal.
    """
    rotation_rad = np.radians(rotation_deg)
    radial_unit = np.array([0.0, np.cos(rotation_rad), np.sin(rotation_rad)])
    intake_rad = np.radians(intake_angle_deg)
    direction = np.cos(intake_rad) * radial_unit - np.sin(intake_rad) * np.array([1.0, 0.0, 0.0])
    direction = direction / np.linalg.norm(direction)
    return {
        "attach_axial_station_m": SYNTHETIC_RING_X0_M,
        "attach_angular_position_deg": rotation_deg,
        "attach_direction_xyz": direction,
        "inner_diameter_m": SYNTHETIC_TUBE_INNER_DIA_M,
    }


def _duct_waypoints(hook, attach_radial_offset_m, bend_radius_tube_dia_mult):
    """
    Same 3-waypoint ([stub_end, corner, attach]) construction as
    gui/mesh_builder.py's _fuel_inlet_duct_waypoints, standalone here since
    that function takes a real manifold_result hook rather than this
    module's synthetic one. See that function's docstring for the reasoning
    behind each waypoint/standoff/stub length.
    """
    angle = np.radians(hook["attach_angular_position_deg"])
    x_attach = hook["attach_axial_station_m"]
    attach = np.array([x_attach, attach_radial_offset_m * np.cos(angle),
                        attach_radial_offset_m * np.sin(angle)])

    outward = np.asarray(hook["attach_direction_xyz"], dtype=float)
    tube_radius_m = hook["inner_diameter_m"] / 2.0
    bend_radius_m = bend_radius_tube_dia_mult * (2.0 * tube_radius_m)
    standoff = DUCT_APPROACH_STANDOFF_BEND_RADIUS_MULT * bend_radius_m
    corner = attach + standoff * outward

    stub_length = DUCT_STUB_LENGTH_BEND_RADIUS_MULT * bend_radius_m
    stub_end = corner + stub_length * np.array([-1.0, 0.0, 0.0])

    return np.array([stub_end, corner, attach]), bend_radius_m, tube_radius_m


def build_manifold_test_pieces(intake_angle_deg, bend_radius_tube_dia_mult, rotation_deg):
    """
    Build the Shape Lab's manifold-test scene for the current slider values.
    Returns {"ring": MeshBuffers, "duct": [MeshBuffers, ...]} (duct is a list
    per bent_tube_duct_mesh's own "body + end caps" convention).
    """
    ring = manifold_ring_mesh(SYNTHETIC_RING_X0_M, SYNTHETIC_RING_MAJOR_R_M,
                               SYNTHETIC_RING_TUBE_R_M, SYNTHETIC_N_THETA_MAIN,
                               SYNTHETIC_N_THETA_TUBE, base_color_rgb=SYNTHETIC_RING_COLOR)

    hook = _synthetic_hook(intake_angle_deg, rotation_deg)
    waypoints, bend_radius_m, tube_radius_m = _duct_waypoints(
        hook, SYNTHETIC_RING_MAJOR_R_M, bend_radius_tube_dia_mult)
    duct = bent_tube_duct_mesh(waypoints, bend_radius_m, tube_radius_m,
                                n_theta=SYNTHETIC_N_THETA_TUBE, base_color_rgb=SYNTHETIC_DUCT_COLOR)
    return {"ring": ring, "duct": duct}


def host_ring_from_result(result, host):
    """The (hook, render_center_r_m, tube_r_m) triple for rooting a Shape Lab
    run on `host` in this compute() result - the ring's INLET section (a
    split/tapered ring shrinks away from it; build_plumbing_scene draws the
    taper and roots the run locally) - render radius wall-snapped
    exactly as gui/mesh_builder.build_injector_head_pieces does, so the Lab
    ring sits where the main preview draws it. None if the ring doesn't
    exist for this design."""
    hook = plumbing.hook_for_host(result, host)
    if hook is None:
        return None
    return hook, mesh_builder.ring_render_center_r(result, hook), hook["outer_radius_m"]


def ghost_turbopump_from_result(result):
    """(pieces, pump_points) for the Shape Lab's ghost turbopump: the design's
    turbopump assembly (result["turbopump_sizing"]["bodies"]) placed exactly
    where the main preview draws it (geometry3d.turbopump_origin_xyz), in the
    flat GHOST_TURBOPUMP_RGB tint, plus geometry3d.turbopump_pump_points'
    {"fuel_pump"/"ox_pump": xyz} ray targets. None when the design has no
    turbopump (pressure-fed)."""
    sizing = result.get("turbopump_sizing")
    if not sizing or not sizing.get("bodies"):
        return None
    origin = geometry3d.turbopump_origin_for_result(result)
    pieces = [mesh_from_grid(Xt, Yt, Zt, GHOST_TURBOPUMP_RGB)
              for _kind, (Xt, Yt, Zt) in geometry3d.turbopump_assembly_meshes(sizing["bodies"], origin)]
    pieces.extend(mesh_builder.turbopump_port_stub_pieces(result, GHOST_TURBOPUMP_RGB))
    return pieces, geometry3d.turbopump_pump_points(sizing["bodies"], origin)


def build_plumbing_scene(run, hook, ring_center_r_m, ring_tube_r_m, host="jacket_inlet",
                         selected_index=None, wall_profile=None, show_ghost_wall=True,
                         ghost_turbopump=None, show_ghost_turbopump=True, supercritical=False,
                         port=None):
    """
    Build the Shape Lab's plumbing scene. `wall_profile` = (xs_m, rs_m) of the
    chamber/nozzle contour (result["profile_xs_m"/"profile_rs_m"]) for the
    ghost wall; None or show_ghost_wall=False omits it. `ghost_turbopump` =
    ghost_turbopump_from_result(result) (pieces, pump_points); when given and
    shown, the turbopump is drawn and a RAY_RGB ray_mesh runs from the last
    pipe's true end to HOST_PUMP[host]'s point. Returns
    {"pieces": [MeshBuffers...], "center": (x, y, z), "half": float,
     "resolved": plumbing.resolve_run dict, "ray_target": pump name or None,
     "ray_length_m": float or None} - the same dict shape ShapeLabPanel's
    build_pieces_fn contract expects, plus `resolved` so the panel can show
    advisories/length without a second solve.
    `port` (mesh_builder.run_port_for_result) closes a connect_to_pump run
    onto its pump's discharge port; a closed run draws no ray.
    """
    rgb = PLUMBING_HOST_RGB.get(host, (0.56, 0.56, 0.20))
    x0 = float(hook["attach_axial_station_m"])
    ring_ctr, ring_tube = ring_center_r_m, ring_tube_r_m
    run_ctr, run_tube = ring_center_r_m, ring_tube_r_m
    if "inlet_flow_radius_m" in hook:
        # A real physics/manifold.py ring is a split/tapered header: the
        # passed (centre, tube) are its INLET values (host_ring_from_result);
        # the inner edge stays flush, so draw the per-u taper and root the run
        # on the ring's local section at the run's own angle - the same as
        # gui/mesh_builder.build_injector_head_pieces.
        edge = ring_center_r_m - ring_tube_r_m
        ring_ctr, ring_tube = mesh_builder.ring_render_arrays(hook, edge, 24)
        _r = run if isinstance(run, plumbing.PlumbingRun) else plumbing.run_from_dict(run)
        run_ctr, run_tube = mesh_builder.ring_local_render(hook, edge, _r.attach_angle_deg)
    pieces = [manifold_ring_mesh(x0, ring_ctr, ring_tube, 24, 12, rgb,
                                 specular_strength=HARDWARE_SPECULAR_STRENGTH,
                                 shininess=HARDWARE_SHININESS)]
    run_pieces, resolved = mesh_builder.build_plumbing_pieces(
        run, hook, run_ctr, run_tube, rgb, selected_index=selected_index,
        supercritical=supercritical, port=port)
    pieces.extend(run_pieces)
    framed = [pieces[0]] + run_pieces   # what the camera fits to
    ray_target, ray_length = None, None
    if show_ghost_turbopump and ghost_turbopump is not None:
        tp_pieces, pump_points = ghost_turbopump
        pieces.extend(tp_pieces)
        framed.extend(tp_pieces)
        target = pump_points.get(HOST_PUMP.get(host, "fuel_pump"))
        if target is not None and run.pipes and not resolved["closes_on_port"]:
            end = resolved["waypoints_xyz"][-1]   # the true pipe end, not the flange-shifted joint
            ray = ray_mesh(end, target, RAY_RADIUS_TUBE_R_MULT * resolved["pipe_radii_m"][-1],
                           RAY_N_THETA, RAY_RGB)
            if ray:
                pieces.extend(ray)
                framed.extend(ray)
                ray_target = HOST_PUMP.get(host, "fuel_pump")
                ray_length = float(np.linalg.norm(np.asarray(target) - end))
    if show_ghost_wall and wall_profile is not None:
        xs, rs = (np.asarray(a, dtype=float) for a in wall_profile)
        if xs.size >= 2:
            pieces.append(revolve_to_buffers(xs, rs, GHOST_WALL_N_THETA, GHOST_WALL_RGB))
    # Bounds from the ring + run + ghost turbopump + ray - not the ghost wall,
    # which would zoom the camera out to the whole engine and shrink the
    # pipes to nothing.
    verts = np.concatenate([p.vertices for p in framed])
    lo, hi = verts.min(axis=0), verts.max(axis=0)
    center = (lo + hi) / 2.0
    half = float(np.max(hi - lo) / 2.0) * (1.0 + SCENE_PADDING_FRACTION)
    return {"pieces": pieces, "center": tuple(float(c) for c in center), "half": max(half, 1e-3),
            "resolved": resolved, "ray_target": ray_target, "ray_length_m": ray_length}


def self_test():
    # --- plumbing scene against a real design's jacket_inlet ring ---
    from ..physics.design import EngineDesign
    result = EngineDesign().compute()
    ring = host_ring_from_result(result, "jacket_inlet")
    assert ring is not None
    hook, ring_r, tube_r = ring
    assert ring_r > hook["major_radius_m"] * 0.5
    run = plumbing.default_run_for_host(hook, tube_r)
    run.pipes.append(plumbing.PipeSegment(length_dia_mult=5.0, yaw_deg=30.0, flange_at_end=True))
    wall = (result["profile_xs_m"], result["profile_rs_m"])
    scene = build_plumbing_scene(run, hook, ring_r, tube_r, selected_index=1, wall_profile=wall)
    n_with_ghost = len(scene["pieces"])
    scene_no_ghost = build_plumbing_scene(run, hook, ring_r, tube_r, wall_profile=wall,
                                          show_ghost_wall=False)
    assert n_with_ghost == len(scene_no_ghost["pieces"]) + 1
    for piece in scene["pieces"]:
        assert not np.any(np.isnan(piece.vertices)) and not np.any(np.isnan(piece.normals))
    assert scene["half"] > 0 and len(scene["center"]) == 3
    assert scene["resolved"]["total_length_m"] > 0
    # bounds ignore the ghost wall: identical with/without it
    assert np.allclose(scene["center"], scene_no_ghost["center"]) and np.isclose(scene["half"], scene_no_ghost["half"])
    # the run's end sits inside the scene box
    end = scene["resolved"]["waypoints_xyz"][-1]
    assert np.all(np.abs(end - np.array(scene["center"])) <= scene["half"] + 1e-9)
    # an empty run still gives a ring-only scene; a missing host returns None
    empty = build_plumbing_scene(plumbing.PlumbingRun(), hook, ring_r, tube_r)
    assert len(empty["pieces"]) == 1 and empty["ray_target"] is None
    assert host_ring_from_result(result, "jacket_return") is None
    assert scene["ray_target"] is None and scene["ray_length_m"] is None
    print("build_plumbing_scene self-check (real jacket_inlet ring, ghost wall, bounds): OK")

    # --- ghost turbopump + free-end -> pump ray ---
    ghost_tp = ghost_turbopump_from_result(result)   # default design is gas-generator: has one
    assert ghost_tp is not None
    tp_pieces, pump_points = ghost_tp
    # bodies + a 3-piece nozzle stub per pump port (inlet + discharge)
    assert len(tp_pieces) == (len(result["turbopump_sizing"]["bodies"])
                              + 3 * 2 * len(result["turbopump_ports"]))
    assert "fuel_pump" in pump_points and "ox_pump" in pump_points
    with_tp = build_plumbing_scene(run, hook, ring_r, tube_r, wall_profile=wall,
                                   ghost_turbopump=ghost_tp)
    # + turbopump bodies + 3 ray pieces (cylinder + 2 end disks)
    assert len(with_tp["pieces"]) == n_with_ghost + len(tp_pieces) + 3
    assert with_tp["ray_target"] == "fuel_pump"
    end = with_tp["resolved"]["waypoints_xyz"][-1]
    assert np.isclose(with_tp["ray_length_m"], np.linalg.norm(pump_points["fuel_pump"] - end))
    assert with_tp["ray_length_m"] > 0
    # the camera now frames the turbopump and the ray (ghost wall still excluded)
    assert with_tp["half"] > scene["half"]
    for pt in (end, pump_points["fuel_pump"]):
        assert np.all(np.abs(pt - np.array(with_tp["center"])) <= with_tp["half"] + 1e-6)
    for piece in with_tp["pieces"]:
        assert not np.any(np.isnan(piece.vertices)) and not np.any(np.isnan(piece.normals))
    # toggled off: identical to the plain scene; hidden turbopump hides the ray too
    off = build_plumbing_scene(run, hook, ring_r, tube_r, wall_profile=wall,
                               ghost_turbopump=ghost_tp, show_ghost_turbopump=False)
    assert len(off["pieces"]) == n_with_ghost and off["ray_target"] is None
    assert np.allclose(off["center"], scene["center"]) and np.isclose(off["half"], scene["half"])
    # an empty run with the turbopump shown: bodies but no ray
    empty_tp = build_plumbing_scene(plumbing.PlumbingRun(), hook, ring_r, tube_r,
                                    ghost_turbopump=ghost_tp)
    assert len(empty_tp["pieces"]) == 1 + len(tp_pieces) and empty_tp["ray_target"] is None
    # connected to the pump: the run closes on the discharge port, no ray
    port = result["turbopump_ports"]["fuel_pump"]["discharge"]
    seeded = plumbing.seed_route_to_port(hook, port, ring_r, tube_r, "jacket_inlet")
    conn = build_plumbing_scene(seeded, hook, ring_r, tube_r, ghost_turbopump=ghost_tp, port=port)
    assert conn["ray_target"] is None and conn["resolved"]["closes_on_port"]
    assert np.linalg.norm(conn["resolved"]["waypoints_xyz"][-1] - port["pos"]) < 1e-9
    # a pressure-fed design has no turbopump -> no ghost, scene unchanged
    from ..physics import cycles
    pf = EngineDesign(cycle=cycles.PRESSURE_FED, chamber_pressure_pa=2.0e6).compute()
    assert ghost_turbopump_from_result(pf) is None
    pf_ring = host_ring_from_result(pf, "jacket_inlet")
    if pf_ring is not None:
        pf_scene = build_plumbing_scene(plumbing.default_run_for_host(pf_ring[0], pf_ring[2]),
                                        *pf_ring, ghost_turbopump=None)
        assert pf_scene["ray_target"] is None
    print("build_plumbing_scene ghost turbopump + ray self-check: OK")

    for intake_angle_deg in (0.0, 45.0, 89.0):
        for bend_radius_tube_dia_mult in (0.5, 2.0, 5.0):
            for rotation_deg in (0.0, 90.0, 270.0):
                pieces = build_manifold_test_pieces(intake_angle_deg, bend_radius_tube_dia_mult,
                                                      rotation_deg)
                ring = pieces["ring"]
                assert not np.any(np.isnan(ring.vertices))
                assert not np.any(np.isnan(ring.normals))
                for duct_piece in pieces["duct"]:
                    assert not np.any(np.isnan(duct_piece.vertices))
                    assert not np.any(np.isnan(duct_piece.normals))
    print("build_manifold_test_pieces self-check (no NaN across slider ranges): OK")

    # rotation_deg=90 must place the attach point's Y near 0, Z near
    # +SYNTHETIC_RING_MAJOR_R_M (rotation is purely around the main X axis).
    hook_0 = _synthetic_hook(intake_angle_deg=0.0, rotation_deg=0.0)
    hook_90 = _synthetic_hook(intake_angle_deg=0.0, rotation_deg=90.0)
    wp_0, _, _ = _duct_waypoints(hook_0, SYNTHETIC_RING_MAJOR_R_M, 0.5)
    wp_90, _, _ = _duct_waypoints(hook_90, SYNTHETIC_RING_MAJOR_R_M, 0.5)
    attach_0, attach_90 = wp_0[-1], wp_90[-1]
    assert np.isclose(attach_0[2], 0.0, atol=1e-9)
    assert np.isclose(attach_90[1], 0.0, atol=1e-9)
    assert np.isclose(attach_90[2], SYNTHETIC_RING_MAJOR_R_M, atol=1e-9)
    print("rotation_deg self-check (attach point orbits the main axis): OK")

    # intake_angle_deg=0 -> pure-radial approach direction (no axial
    # component); intake_angle_deg=90 -> pure-axial (-x) approach direction.
    hook_radial = _synthetic_hook(intake_angle_deg=0.0, rotation_deg=0.0)
    hook_axial = _synthetic_hook(intake_angle_deg=90.0, rotation_deg=0.0)
    assert np.isclose(hook_radial["attach_direction_xyz"][0], 0.0, atol=1e-9)
    assert np.allclose(hook_axial["attach_direction_xyz"], [-1.0, 0.0, 0.0], atol=1e-9)
    print("intake_angle_deg self-check (radial -> axial approach direction): OK")

    # larger bend_radius_tube_dia_mult -> larger bend radius -> the stub end
    # sits further from the attach point (standoff + stub length both scale
    # with bend_radius_m).
    hook = _synthetic_hook(intake_angle_deg=45.0, rotation_deg=0.0)
    wp_small, br_small, _ = _duct_waypoints(hook, SYNTHETIC_RING_MAJOR_R_M, 0.5)
    wp_large, br_large, _ = _duct_waypoints(hook, SYNTHETIC_RING_MAJOR_R_M, 5.0)
    assert br_large > br_small
    dist_small = np.linalg.norm(wp_small[0] - wp_small[-1])
    dist_large = np.linalg.norm(wp_large[0] - wp_large[-1])
    assert dist_large > dist_small
    print("bend_radius_tube_dia_mult self-check (larger mult -> longer duct run): OK")

    print("ALL SHAPE_LAB_GEOMETRY CHECKS OK")


if __name__ == "__main__":
    self_test()
