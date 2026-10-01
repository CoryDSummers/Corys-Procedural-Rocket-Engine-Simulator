"""
Surface-of-revolution mesh generation for the 3D preview. The 2D schematic
profile (physics/geometry.py, physics/nozzle_shapes.py) already IS an
axisymmetric (axial position, radius) description of the engine - a 3D
"basic engine cone and chamber shape" is just that profile swept through
360 degrees. No new geometry to derive, only a different rendering of the
same data gui/schematic.py already draws in 2D.
"""
import numpy as np


def revolve_profile(xs_m, rs_m, n_theta=32):
    """
    Sweep an axisymmetric (x, r) profile around the x-axis.
    Returns (X, Y, Z) meshgrid-shaped arrays suitable for
    mpl_toolkits.mplot3d.Axes3D.plot_surface(X, Y, Z).
    """
    xs_m = np.asarray(xs_m)
    rs_m = np.asarray(rs_m)
    theta = np.linspace(0.0, 2.0 * np.pi, n_theta)
    X, Theta = np.meshgrid(xs_m, theta)
    R, _ = np.meshgrid(rs_m, theta)
    Y = R * np.cos(Theta)
    Z = R * np.sin(Theta)
    return X, Y, Z


def turbopump_block_mesh(chamber_dia_m, chamber_length_m, n_theta=16):
    """
    A simple symbolic cylinder representing "a turbopump is mounted here" -
    NOT a real turbomachinery model and NOT a physically-derived size (this
    tool doesn't compute turbopump physical dimensions anywhere). Sized as a
    fixed fraction of chamber diameter, mounted alongside the chamber
    (offset laterally in +Y so it doesn't visually intersect the chamber)
    near the injector-face end, where real turbopumps physically mount.
    Only meant to be drawn when the engine actually has a turbopump
    (result["cycle_result"]["has_turbopump"] is True).
    """
    block_dia = 0.35 * chamber_dia_m
    block_len = 0.6 * chamber_dia_m
    block_r = block_dia / 2.0
    y_offset = chamber_dia_m / 2.0 + block_r + 0.05 * chamber_dia_m
    x0 = 0.15 * min(chamber_length_m, block_len)

    theta = np.linspace(0.0, 2.0 * np.pi, n_theta)
    x = np.linspace(x0, x0 + block_len, 2)
    X, Theta = np.meshgrid(x, theta)
    Y = block_r * np.cos(Theta) + y_offset
    Z = block_r * np.sin(Theta)
    return X, Y, Z


def capped_cylinder(x0_m, length_m, radius_m, center_yz=(0.0, 0.0), n_theta=20):
    """A closed cylinder (lateral surface + both end caps) as ONE (X, Y, Z)
    plot_surface mesh: end cap at x0, lateral wall, end cap at x0+length. Axis
    parallel to +X, translated to `center_yz` in the Y-Z plane."""
    cy, cz = center_yz
    theta = np.linspace(0.0, 2.0 * np.pi, n_theta)
    # radial fraction 0->1 (cap), 1 (wall start), 1 (wall end), 1->0 (cap)
    x = np.array([x0_m, x0_m, x0_m + length_m, x0_m + length_m])
    rad = np.array([0.0, radius_m, radius_m, 0.0])
    X, Theta = np.meshgrid(x, theta)
    R, _ = np.meshgrid(rad, theta)
    Y = R * np.cos(Theta) + cy
    Z = R * np.sin(Theta) + cz
    return X, Y, Z


def disk(x_m, thickness_m, radius_m, center_yz=(0.0, 0.0), n_theta=24):
    """A short solid disk (a wide, thin capped_cylinder) - the turbine wheel."""
    return capped_cylinder(x_m, thickness_m, radius_m, center_yz, n_theta)


# Turbopump placement in engine coordinates (engine axis = +x, injector end
# at x=0): the assembly is mounted just past the injector end, its shaft
# parallel to the engine axis, offset outboard in +Y clear of the widest
# chamber/bell radius. Cosmetic-only (ASSUMPTIONS.md Tier 3); shared by the
# OpenGL preview (gui/mesh_builder), the matplotlib fallback (gui/preview3d)
# and the Shape Lab's ghost turbopump so all three agree on WHERE it is.
TURBOPUMP_ORIGIN_X_LENGTH_FRACTION = 0.03   # x = this * profile length
TURBOPUMP_STANDOFF_R_FRACTION = 0.04         # radial gap = this * max profile radius
TURBOPUMP_UNIT_GAP_OD_MULT = 1.15            # dual-shaft unit spacing along Z


# Placement = origin + rotation (turbopump roadmap E1, 2026-09-30). Every turbopump
# helper below is written in the assembly's LOCAL frame - shaft on x, engine side on -y,
# dual-shaft units spread along z - translated to the origin; a placement dict
# {"origin_xyz", "rotation"} then pivots that about the origin: world = O + R (p - O).
# rotation None / identity = the legacy frame, byte-for-byte. R's columns are the local
# x / y / z axes in engine coordinates (turbopump_rotation).
SHAFT_ORIENTATIONS = ("axial", "tangential")


def turbopump_rotation(azimuth_deg=0.0, shaft_orientation="axial"):
    """3x3 rotation, columns = the assembly's local x (shaft) / y (outboard radial) / z
    axes in engine coordinates, for an assembly clocked `azimuth_deg` round the engine
    axis (0 = +Y, increasing toward +Z - the manifold attach_angle convention):
      "axial":      shaft parallel to the engine axis       [e_x | e_r | e_theta]
      "tangential": shaft along the local circumference     [e_theta | e_r | -e_x]
    (both det +1, so mesh winding survives). Azimuth 0 + "axial" is exactly I."""
    phi = np.radians(float(azimuth_deg))
    c, s_ = (1.0, 0.0) if float(azimuth_deg) == 0.0 else (float(np.cos(phi)), float(np.sin(phi)))
    e_x = np.array([1.0, 0.0, 0.0])
    e_r = np.array([0.0, c, s_])
    e_t = np.array([0.0, -s_, c])
    if shaft_orientation == "tangential":
        return np.column_stack([e_t, e_r, -e_x])
    return np.column_stack([e_x, e_r, e_t])


def split_placement(placement):
    """(origin tuple, R or None) from a placement dict {"origin_xyz", "rotation"} or a
    bare legacy origin tuple. An identity rotation comes back None (the legacy path)."""
    if isinstance(placement, dict):
        rot = placement.get("rotation")
        origin = tuple(float(v) for v in placement["origin_xyz"])
        if rot is None:
            return origin, None
        rot = np.asarray(rot, dtype=float)
        return origin, (None if np.array_equal(rot, np.eye(3)) else rot)
    return tuple(placement), None


def place_point(origin, rot, p):
    """A point built in the legacy (unrotated) frame about `origin` -> engine coordinates."""
    if rot is None:
        return p
    o = np.asarray(origin, dtype=float)
    return o + rot @ (np.asarray(p, dtype=float) - o)


def place_dir(rot, d):
    return d if rot is None else rot @ np.asarray(d, dtype=float)


def port_frame_rows(rot):
    """A port's routing frame (plumbing.port_frame): rows = the assembly's local x / y / z
    axes in engine coordinates (R^T) - for either shaft orientation the same three axes:
    the engine axis, the pump's outboard radial (always row 1) and its tangent. The pipe
    runs closing onto the port are squared to these."""
    return np.eye(3) if rot is None else np.asarray(rot, dtype=float).T.copy()


def turbopump_origin_xyz(profile_x_max_m, profile_r_max_m, assembly_od_m):
    """The (x, y, z) the assembly's `x0_m = 0` bodies start from."""
    y_offset = (profile_r_max_m + 0.5 * assembly_od_m
                + TURBOPUMP_STANDOFF_R_FRACTION * profile_r_max_m)
    return (TURBOPUMP_ORIGIN_X_LENGTH_FRACTION * float(profile_x_max_m), float(y_offset), 0.0)


def obstacle_bands(hooks=(), te_hardware=None):
    """Axisymmetric (x_lo, x_hi, r) bands the turbopump must clear besides the wall
    contour: every manifold ring (fuel / ox / jacket inlet / return, the exhaust scroll /
    aspirator collar - its tube +- round the station, out to major + tube radius) and the
    turbine-exhaust termination (overboard nozzle, aspirator shroud, injection neck /
    flame shield). Conservative: a ring's band is the full circle."""
    bands = []
    for hk in hooks:
        if not hk or hk.get("point_hook"):
            continue
        x = float(hk["attach_axial_station_m"])
        t = float(hk.get("outer_radius_m", 0.0) or 0.0)
        bands.append((x - t, x + t, float(hk["major_radius_m"]) + t))
    te = te_hardware or {}
    out = te.get("outlet")
    if out:
        pos = np.asarray(out["pos"], dtype=float)
        half = 0.5 * max(float(out.get("inlet_dia_m", 0.0)), float(out.get("exit_dia_m", 0.0)))
        bands.append((pos[0] - half, pos[0] + float(out.get("length_m", 0.0)) + half,
                      float(np.hypot(pos[1], pos[2])) + half))
    for key, xs_key, rs_key in (("aspirator", "xs", "r_outer"), ("neck", "section_xs", "section_rs"),
                                ("neck", "shield_xs", "shield_rs")):
        part = te.get(key) or {}
        xs, rs = part.get(xs_key), part.get(rs_key)
        if xs is not None and rs is not None and len(xs) > 1:
            for k in range(len(xs) - 1):
                bands.append((min(xs[k], xs[k + 1]), max(xs[k], xs[k + 1]), max(rs[k], rs[k + 1])))
    return bands


def envelope_r_max(profile_xs_m, profile_rs_m, x_lo, x_hi, bands=()):
    """The largest radius anything axisymmetric reaches over [x_lo, x_hi]: the wall
    contour (interpolated at the ends, held at its end values beyond them) and every
    obstacle band overlapping the span."""
    xs = np.asarray(profile_xs_m, dtype=float)
    rs = np.asarray(profile_rs_m, dtype=float)
    r = max(float(np.interp(x_lo, xs, rs)), float(np.interp(x_hi, xs, rs)))
    inside = (xs >= x_lo) & (xs <= x_hi)
    if np.any(inside):
        r = max(r, float(rs[inside].max()))
    for lo, hi, rb in bands:
        if lo <= x_hi and hi >= x_lo:
            r = max(r, float(rb))
    return r


def boxes_from_bodies(bodies):
    """The ghost envelope's bodies as LOCAL placement boxes (turbopump_placement): shaft
    span [x0, x1], unit offset dz, half-width in z and the engine-side (-y) reach."""
    return [{"x0": float(b["x0_m"]), "x1": float(b["x0_m"] + b["length_m"]), "dz": float(dz),
             "half_z": 0.5 * float(b["od_m"]), "reach": 0.5 * float(b["od_m"]), "kind": b["kind"]}
            for b, dz in zip(bodies, turbopump_unit_dz(bodies))]


def turbopump_placement(boxes, profile_xs_m, profile_rs_m, azimuth_deg=0.0,
                        axial_station_frac=0.0, standoff_m=0.0, shaft_orientation="axial",
                        bands=()):
    """
    Where the turbopump goes (roadmap E1): the assembly - LOCAL boxes (boxes_from_bodies
    / turbopump_layout.layout_boxes; shaft on local x from 0, engine side -y) - clocked
    to `azimuth_deg`, shaft per `shaft_orientation` (turbopump_rotation), its MIDPOINT at
    axial_station_frac x engine length (0 = auto: forward end at
    TURBOPUMP_ORIGIN_X_LENGTH_FRACTION x length, the legacy station), and pushed out
    radially until EVERY box clears the envelope over its OWN axial span (envelope_r_max:
    contour + rings + exhaust hardware) by `standoff_m` (0 = auto,
    TURBOPUMP_STANDOFF_R_FRACTION x that local envelope radius). Span-aware: a pump beside
    a narrow chamber sits beside the chamber, not beyond the bell exit.
    Conservative: a box's tangential offset only ever adds clearance.
    Returns {"origin_xyz", "rotation", "azimuth_deg", "shaft_orientation",
    "axis_radius_m", "station_x_m", "x_span_m", "standoff_m", "envelope_r_m",
    "governing_kind"} (the last three for the governing box).
    With a constant contour, no bands, azimuth 0 and an axial shaft this is exactly the
    legacy turbopump_origin_xyz.
    """
    orient = shaft_orientation if shaft_orientation in SHAFT_ORIENTATIONS else "axial"
    rot = turbopump_rotation(azimuth_deg, orient)
    xs = np.asarray(profile_xs_m, dtype=float)
    x_max = float(np.max(xs))
    x_lo_l = min(b["x0"] for b in boxes)
    c_l = np.array([0.5 * (x_lo_l + max(b["x1"] for b in boxes)), 0.0, 0.0])
    # world-x offsets of each box from the assembly centre (local y never moves world x)
    offs = []
    for b in boxes:
        dx = [rot[0, 0] * (x - c_l[0]) + rot[0, 2] * z
              for x in (b["x0"], b["x1"]) for z in (b["dz"] - b["half_z"], b["dz"] + b["half_z"])]
        offs.append((min(dx), max(dx)))
    if axial_station_frac and axial_station_frac > 0.0:
        c_x = float(axial_station_frac) * x_max
    else:
        c_x = TURBOPUMP_ORIGIN_X_LENGTH_FRACTION * x_max - min(o[0] for o in offs)
    rho, gov = -np.inf, None
    for b, (lo, hi) in zip(boxes, offs):
        r_env = envelope_r_max(xs, profile_rs_m, c_x + lo, c_x + hi, bands)
        gap = float(standoff_m) if standoff_m and standoff_m > 0.0 \
            else TURBOPUMP_STANDOFF_R_FRACTION * r_env
        need = b["reach"] + r_env + gap
        if need > rho:
            rho, gov = need, (b, r_env, gap)
    e_r = rot[:, 1]
    centre = np.array([c_x, 0.0, 0.0]) + rho * e_r
    origin = centre - rot @ c_l
    return {"origin_xyz": tuple(float(v) for v in origin), "rotation": rot,
            "azimuth_deg": float(azimuth_deg), "shaft_orientation": orient,
            "axis_radius_m": float(rho), "station_x_m": float(c_x),
            "x_span_m": (float(c_x + min(o[0] for o in offs)), float(c_x + max(o[1] for o in offs))),
            "standoff_m": float(gov[2]), "envelope_r_m": float(gov[1]),
            "governing_kind": gov[0].get("kind", "")}


def placement_clearances(boxes, placement, profile_xs_m, profile_rs_m, bands=()):
    """[(kind, clearance_m)] per box of a placed assembly: how far its engine-side reach
    sits outside the envelope (envelope_r_max) over its OWN world-x span, measured along
    the pump's outboard radial. >= the resolved standoff for a turbopump_placement solve;
    negative = it hits the engine. The check every consumer/test shares."""
    rot = np.asarray(placement["rotation"], dtype=float)
    o = np.asarray(placement["origin_xyz"], dtype=float)
    out = []
    for b in boxes:
        xw = [o[0] + rot[0] @ np.array([x, 0.0, z])
              for x in (b["x0"], b["x1"]) for z in (b["dz"] - b["half_z"], b["dz"] + b["half_z"])]
        r_env = envelope_r_max(profile_xs_m, profile_rs_m, min(xw), max(xw), bands)
        ctr = o + rot @ np.array([0.5 * (b["x0"] + b["x1"]), 0.0, b["dz"]])
        out.append((b.get("kind", ""), float(np.dot(ctr, rot[:, 1])) - b["reach"] - r_env))
    return out


def turbopump_unit_dz(bodies):
    """Per-body Z offset (list, `bodies` order): 0 for a single unit; for a
    dual-shaft turbopump the units (`center` 0 / 1) are spread symmetrically
    about the origin by TURBOPUMP_UNIT_GAP_OD_MULT x the largest body OD."""
    unit_ids = sorted({b.get("center", 0) for b in bodies})
    unit_gap = 0.0
    if len(unit_ids) > 1:
        unit_gap = TURBOPUMP_UNIT_GAP_OD_MULT * max(b["od_m"] for b in bodies)
    return [(unit_ids.index(b.get("center", 0)) - (len(unit_ids) - 1) / 2.0) * unit_gap
            for b in bodies]


def turbopump_body_centers(bodies, origin_xyz):
    """Each body's mid-length point ON its shaft axis, in engine coordinates
    (list of {kind, center, pos (3,), radius_m, length_m} in `bodies` order) -
    the same placement turbopump_assembly_meshes(axis="x") draws, as data.
    `origin_xyz` = a legacy origin tuple or a placement dict (split_placement)."""
    (ox_, oy_, oz_), rot = split_placement(origin_xyz)
    out = []
    for b, dz in zip(bodies, turbopump_unit_dz(bodies)):
        pos = np.array([ox_ + b["x0_m"] + 0.5 * b["length_m"], oy_, oz_ + dz])
        out.append({"kind": b["kind"], "center": b.get("center", 0),
                    "pos": place_point((ox_, oy_, oz_), rot, pos),
                    "radius_m": 0.5 * b["od_m"], "length_m": float(b["length_m"])})
    return out


def turbopump_pump_points(bodies, origin_xyz):
    """{"fuel_pump": xyz, "ox_pump": xyz} - the pump bodies' centre points, the
    placeholder attach targets for plumbing until the turbopump grows real
    inlet/discharge hook points. turbopump_sizing._assemble_bodies always
    appends the fuel pump before the ox pump (in every arrangement), so the
    1st/2nd `kind == "pump"` body is fuel/ox; a monopropellant (one pump)
    just has no "ox_pump" key."""
    pumps = [c["pos"] for c in turbopump_body_centers(bodies, origin_xyz) if c["kind"] == "pump"]
    return {name: pos for name, pos in zip(("fuel_pump", "ox_pump"), pumps)}


def turbopump_origin_for_result(result):
    """turbopump_origin_xyz from an EngineDesign.compute() result (or any dict
    with profile_xs_m / profile_rs_m / turbopump_sizing) - the ONE placement
    every consumer (both previews, the Shape Lab, design.py's pump-port runs)
    uses. None when there is no turbopump. With turbopump_geometry_model "casings" it is
    the true-scale casing layout's own origin (physics/turbopump_layout.place_layout)."""
    sizing = result.get("turbopump_sizing") if isinstance(result, dict) else None
    if not sizing or not sizing.get("bodies"):
        return None
    if result.get("turbopump_layout"):
        return tuple(result["turbopump_layout"]["origin_xyz"])
    placed = result.get("turbopump_placement")
    if placed:
        return tuple(placed["origin_xyz"])
    return turbopump_origin_xyz(float(np.max(result["profile_xs_m"])),
                                float(np.max(result["profile_rs_m"])),
                                sizing["assembly_od_m"])


def turbopump_placement_for_result(result):
    """{"origin_xyz", "rotation"} for an EngineDesign.compute() result - what every
    consumer hands the turbopump helpers (turbopump_assembly_meshes / _pump_points /
    _body_centers accept it in place of a bare origin). None when there is no turbopump.
    rotation None = the legacy +Y, shaft-parallel frame."""
    origin = turbopump_origin_for_result(result)
    if origin is None:
        return None
    src = result.get("turbopump_layout") or result.get("turbopump_placement") or {}
    rot = src.get("rotation")
    return {"origin_xyz": origin, "rotation": None if rot is None else np.asarray(rot, dtype=float)}


PUMP_NAMES = ("fuel_pump", "ox_pump")
# A short straight nozzle stub between the body surface and the port face,
# x the port bore (Tier 3 cosmetic): runs land on the stub's free end.
PORT_STUB_DIA_MULT = 0.75


def turbopump_ports(bodies, origin_xyz, sizing=None, discharge_dia_by_pump=None,
                    turbine_exhaust_dia_m=0.0):
    """
    Per-pump inlet / discharge hook points, in engine coordinates:
      {"fuel_pump": {"inlet": {"pos", "dir", "dia_m"},
                     "discharge": {"pos", "dir", "dia_m"}}, "ox_pump": {...}}
    - inlet: centre of the pump body's end face AWAY from the rest of its unit
      (turbine/motor/other pump), `dir` pointing axially out along the shaft;
      bore = the pump's sized inlet eye (sizing["fuel_pump"/"ox_pump"]
      ["inlet_eye_dia_m"], 0 if not given).
    - discharge: on the volute rim on the side facing the engine axis (-y from
      the body centre), `dir` tangential (+/-z, away from the assembly's own
      centre - Tier 3 cosmetic); bore = discharge_dia_by_pump[name] (the
      downstream ring's full-flow feed bore, from design.py), 0 if not given.
    `dir` is always the direction flow LEAVES the port (out of the pump at the
    discharge, into the suction line at the inlet - i.e. outward normal).
    turbine_exhaust_dia_m > 0 (open cycles - physics/turbine_exhaust.py) adds
      {"turbine": {"exhaust": {"base", "pos", "dir", "dia_m"}}}: on the (first)
      turbine body's rim facing the engine, `dir` tangential (the fuel side's +-z,
      like the casings' exhaust scroll) - where the exhaust duct leaves the turbine.
    Every port also carries `frame` (port_frame_rows: the axes its pipe runs are
    squared to).
    Each port also carries `base` (the point on the body surface); `pos` sits
    PORT_STUB_DIA_MULT x bore further out along `dir` - the nozzle stub's face,
    where a pipe run lands.
    """
    origin_xyz, rot = split_placement(origin_xyz)
    if rot is not None:   # built in the legacy frame, then pivoted about the origin
        ports = turbopump_ports(bodies, origin_xyz, sizing, discharge_dia_by_pump,
                                turbine_exhaust_dia_m)
        return {key: {name: dict(p, base=place_point(origin_xyz, rot, p["base"]),
                                 pos=place_point(origin_xyz, rot, p["pos"]),
                                 dir=place_dir(rot, p["dir"]), frame=port_frame_rows(rot))
                      for name, p in group.items()}
                for key, group in ports.items()}
    discharge_dia_by_pump = discharge_dia_by_pump or {}
    centers = turbopump_body_centers(bodies, origin_xyz)
    pumps = [c for c in centers if c["kind"] == "pump"]
    oz_ = float(origin_xyz[2])
    out = {}
    for i, (name, c) in enumerate(zip(PUMP_NAMES, pumps)):
        others = [o for o in centers if o is not c and o["center"] == c["center"]]
        if others:
            ref_x = float(np.mean([o["pos"][0] for o in others]))
            sx = 1.0 if c["pos"][0] > ref_x else -1.0
        else:
            sx = -1.0
        inlet_dir = np.array([sx, 0.0, 0.0])
        inlet_pos = c["pos"] + 0.5 * c["length_m"] * inlet_dir
        dz = c["pos"][2] - oz_
        sz = (1.0 if dz > 0 else -1.0) if abs(dz) > 1e-12 else (-1.0 if i == 0 else 1.0)
        dis_pos = c["pos"] + np.array([0.0, -c["radius_m"], 0.0])
        dis_dir = np.array([0.0, 0.0, sz])
        eye = float(((sizing or {}).get(name) or {}).get("inlet_eye_dia_m", 0.0) or 0.0)
        dis_dia = float(discharge_dia_by_pump.get(name, 0.0) or 0.0)
        out[name] = {"inlet": {"base": inlet_pos, "dir": inlet_dir, "dia_m": eye,
                               "pos": inlet_pos + PORT_STUB_DIA_MULT * eye * inlet_dir,
                               "frame": port_frame_rows(None)},
                     "discharge": {"base": dis_pos, "dir": dis_dir, "dia_m": dis_dia,
                                   "pos": dis_pos + PORT_STUB_DIA_MULT * dis_dia * dis_dir,
                                   "frame": port_frame_rows(None)}}
    turbines = [c for c in centers if c["kind"] == "turbine"]
    if turbine_exhaust_dia_m > 0 and turbines:
        # on the rim facing the engine (-y), tangential +-z - where the casings' exhaust
        # scroll discharges (turbopump_layout), the fuel side's sign: deterministic,
        # whatever the pumps' relative lengths (E1; it used to be an axial end face
        # whose sign flipped with them)
        c = turbines[0]
        dz = c["pos"][2] - oz_
        ex_dir = np.array([0.0, 0.0, (1.0 if dz > 0 else -1.0) if abs(dz) > 1e-12 else -1.0])
        ex_base = c["pos"] + np.array([0.0, -c["radius_m"], 0.0])
        d = float(turbine_exhaust_dia_m)
        out["turbine"] = {"exhaust": {"base": ex_base, "dir": ex_dir, "dia_m": d,
                                      "pos": ex_base + PORT_STUB_DIA_MULT * d * ex_dir,
                                      "frame": port_frame_rows(None)}}
    return out


def turbopump_assembly_meshes(bodies, origin_xyz, axis="x", n_theta=20):
    """
    Build one (X, Y, Z) mesh per turbopump body from a `turbopump_sizing`
    `bodies` list (each {kind, od_m, length_m, x0_m, center}). The bodies of a
    unit are strung along `axis` starting at `origin_xyz`; for a dual-shaft
    turbopump the two units (center 0 / 1) are offset from each other along Z
    (turbopump_unit_dz).

    `origin_xyz` = a legacy origin tuple or a placement dict (split_placement): a
    rotation pivots every mesh about the origin.

    Returns list of (kind, (X, Y, Z)). Rendering only - no physics.
    """
    (ox_, oy_, oz_), rot = split_placement(origin_xyz)
    out = []
    for b, dz in zip(bodies, turbopump_unit_dz(bodies)):
        r = 0.5 * b["od_m"]
        if axis == "x":
            mesh = capped_cylinder(ox_ + b["x0_m"], b["length_m"], r,
                                    center_yz=(oy_, oz_ + dz), n_theta=n_theta)
        else:  # "y" - assembly runs parallel to the engine radius
            X, Y, Z = capped_cylinder(0.0, b["length_m"], r, center_yz=(0.0, 0.0),
                                       n_theta=n_theta)
            mesh = (Z + ox_, X + oy_ + b["x0_m"], Y + oz_ + dz)
        if rot is not None:
            pts = np.stack([np.asarray(mesh[0], dtype=float) - ox_,
                            np.asarray(mesh[1], dtype=float) - oy_,
                            np.asarray(mesh[2], dtype=float) - oz_], axis=-1) @ rot.T
            mesh = (pts[..., 0] + ox_, pts[..., 1] + oy_, pts[..., 2] + oz_)
        out.append((b["kind"], mesh))
    return out


def axial_bump_delta_r(xs_m, center_x_m, half_width_m, height_m, shape="smooth"):
    """
    A localized, AXIAL-ONLY (theta-invariant) radius bump delta_r(x), zero
    outside [center_x_m - half_width_m, center_x_m + half_width_m] - the
    shared building block for structural preview detail (flanges, nozzle
    stiffening rings, the exit lip): all three are just this bump added to
    the outer-wall profile before it's revolved, at different placements/
    sizes/shapes (see gui/preview3d_gl_core.py::build_shell_mesh).

    shape="smooth": a raised-cosine (Hann) bump, 0 at the edges rising
    smoothly to `height_m` at the center - for stiffening rings and the exit
    lip, where a soft profile blend looks right.
    shape="flat": the same envelope with its middle third held flat at
    `height_m` (cosine shoulders only near the edges) - a visible flat
    collar, for flanges.
    shape="rect": a true hard-edged step - exactly `height_m` everywhere
    inside the window, no shoulder taper at all - for a bolted-flange-style
    rectangular collar (sharp vertical edges, flat top), as opposed to
    "flat"'s still-tapered shoulders.

    Symmetric about center_x_m by construction (cos is even, "rect" trivially so).
    """
    xs_m = np.asarray(xs_m, dtype=float)
    delta = np.zeros_like(xs_m)
    if half_width_m <= 0 or height_m == 0:
        return delta
    d = np.abs(xs_m - center_x_m)
    inside = d <= half_width_m
    if not np.any(inside):
        return delta
    if shape == "rect":
        delta[inside] = height_m
    elif shape == "flat":
        shoulder_w = half_width_m / 3.0
        d_in = d[inside]
        shoulder = np.clip((d_in - (half_width_m - shoulder_w)) / shoulder_w, 0.0, 1.0)
        delta[inside] = height_m * (0.5 * (1.0 + np.cos(np.pi * shoulder)))
    else:  # "smooth"
        delta[inside] = height_m * 0.5 * (1.0 + np.cos(np.pi * d[inside] / half_width_m))
    return delta


if __name__ == "__main__":
    # Self-check: every revolved point must be exactly `r` from the x-axis,
    # and the x-coordinate must be unchanged by the revolution (a sweep
    # shouldn't move points along the axis it's sweeping around).
    xs = np.array([0.0, 1.0, 2.0, 3.0])
    rs = np.array([0.5, 0.3, 0.3, 0.8])
    X, Y, Z = revolve_profile(xs, rs, n_theta=16)
    radii = np.sqrt(Y ** 2 + Z ** 2)
    for j, r in enumerate(rs):
        assert np.allclose(radii[:, j], r, atol=1e-12), (j, r, radii[:, j])
        assert np.allclose(X[:, j], xs[j], atol=1e-12)
    print("geometry3d.py self-checks: OK")
    print(f"mesh shape: X{X.shape} Y{Y.shape} Z{Z.shape}")

    # Turbopump block sanity check: every point's distance from the OFFSET
    # axis (x-axis, translated to y_offset) must be exactly block_r, and the
    # block must not overlap a chamber of radius chamber_dia_m/2 (its nearest
    # point stays outside the chamber wall).
    chamber_dia, chamber_len = 0.5, 1.0
    Xtp, Ytp, Ztp = turbopump_block_mesh(chamber_dia, chamber_len, n_theta=16)
    y_offset_check = chamber_dia / 2.0 + 0.35 * chamber_dia / 2.0 + 0.05 * chamber_dia
    radii_tp = np.sqrt((Ytp - y_offset_check) ** 2 + Ztp ** 2)
    assert np.allclose(radii_tp, 0.35 * chamber_dia / 2.0, atol=1e-12)
    assert y_offset_check - 0.35 * chamber_dia / 2.0 >= chamber_dia / 2.0 - 1e-12, \
        "turbopump block clips into the chamber radius"
    print("turbopump_block_mesh self-check: OK")

    # capped_cylinder / disk: the lateral wall points sit at exactly `radius`
    # from the offset axis; the assembly helper strings bodies along the axis.
    Xc, Yc, Zc = capped_cylinder(0.5, 0.4, 0.1, center_yz=(2.0, -1.0), n_theta=12)
    rc = np.sqrt((Yc[:, 1:3] - 2.0) ** 2 + (Zc[:, 1:3] + 1.0) ** 2)
    assert np.allclose(rc, 0.1, atol=1e-12), rc
    bodies = [dict(kind="pump", od_m=0.3, length_m=0.2, x0_m=0.0, center=0),
              dict(kind="turbine", od_m=0.5, length_m=0.1, x0_m=0.25, center=0),
              dict(kind="pump", od_m=0.3, length_m=0.2, x0_m=0.0, center=1)]
    meshes = turbopump_assembly_meshes(bodies, (0.1, 0.6, 0.0))
    assert len(meshes) == 3 and all(len(m) == 2 for m in meshes)
    assert {k for k, _ in meshes} == {"pump", "turbine"}
    print("turbopump_assembly_meshes self-check: OK")

    # Placement-as-data helpers agree with the meshes: every body centre lies
    # on its own drawn cylinder's axis (mid-length, radius from the wall),
    # the dual-shaft fuel/ox pumps sit on different Z, an inline layout on the
    # same Z, and the origin formula is the one the previews always used.
    origin = (0.1, 0.6, 0.0)
    centers = turbopump_body_centers(bodies, origin)
    assert len(centers) == 3
    for c, (kind, (Xm, Ym, Zm)) in zip(centers, meshes):
        assert c["kind"] == kind
        assert np.isclose(c["pos"][0], 0.5 * (Xm.min() + Xm.max()))
        wall_r = np.sqrt((Ym[:, 1:3] - c["pos"][1]) ** 2 + (Zm[:, 1:3] - c["pos"][2]) ** 2)
        assert np.allclose(wall_r, c["radius_m"], atol=1e-12)
    pumps = turbopump_pump_points(bodies, origin)
    assert set(pumps) == {"fuel_pump", "ox_pump"}
    assert not np.isclose(pumps["fuel_pump"][2], pumps["ox_pump"][2])   # dual shaft: split in Z
    assert np.isclose(pumps["fuel_pump"][2] + pumps["ox_pump"][2], 0.0)  # ...symmetrically
    inline = [dict(b, center=0) for b in bodies]
    pumps_inline = turbopump_pump_points(inline, origin)
    assert np.isclose(pumps_inline["fuel_pump"][2], 0.0) and np.isclose(pumps_inline["ox_pump"][2], 0.0)
    assert all(dz == 0.0 for dz in turbopump_unit_dz(inline))
    assert "ox_pump" not in turbopump_pump_points(bodies[:2], origin)
    ox_o, oy_o, oz_o = turbopump_origin_xyz(2.0, 0.5, 0.3)
    assert np.isclose(ox_o, 0.06) and np.isclose(oy_o, 0.5 + 0.15 + 0.02) and oz_o == 0.0
    ports = turbopump_ports(bodies, origin, {"fuel_pump": {"inlet_eye_dia_m": 0.1}},
                            {"fuel_pump": 0.08, "ox_pump": 0.09})
    for nm, pp in ports.items():
        c = [cc for cc in centers if cc["kind"] == "pump"][PUMP_NAMES.index(nm)]
        dis = pp["discharge"]
        # discharge on the volute rim, tangential (perpendicular to the radius vector)
        assert np.isclose(np.linalg.norm((dis["base"] - c["pos"])[1:]), c["radius_m"])
        assert np.isclose(np.dot(dis["dir"], dis["base"] - c["pos"]), 0.0)
        assert np.allclose(dis["pos"], dis["base"] + PORT_STUB_DIA_MULT * dis["dia_m"] * dis["dir"])
        # inlet on the axial end face
        assert np.isclose(abs(pp["inlet"]["base"][0] - c["pos"][0]), 0.5 * c["length_m"])
    # dual shaft: ports mirror-symmetric in z
    assert np.isclose(ports["fuel_pump"]["discharge"]["base"][2],
                      -ports["ox_pump"]["discharge"]["base"][2])
    assert np.allclose(ports["fuel_pump"]["discharge"]["dir"], -ports["ox_pump"]["discharge"]["dir"])
    assert ports["fuel_pump"]["inlet"]["dia_m"] == 0.1 and ports["ox_pump"]["discharge"]["dia_m"] == 0.09
    assert "turbine" not in ports                     # closed cycle / no exhaust bore
    ports_te = turbopump_ports(bodies, origin, None, None, turbine_exhaust_dia_m=0.2)
    ex = ports_te["turbine"]["exhaust"]
    tc = [cc for cc in centers if cc["kind"] == "turbine"][0]
    # on the engine-side rim, tangential, the fuel side's sign (dual shaft: unit 0 = -z)
    assert np.isclose(ex["base"][0], tc["pos"][0]) and np.isclose(ex["base"][1],
                                                                  tc["pos"][1] - tc["radius_m"])
    assert np.isclose(np.dot(ex["dir"], ex["base"] - tc["pos"]), 0.0) and ex["dir"][2] == -1.0
    assert np.allclose(ex["pos"], ex["base"] + PORT_STUB_DIA_MULT * 0.2 * ex["dir"])
    assert turbopump_ports(inline, origin, turbine_exhaust_dia_m=0.2)["turbine"]["exhaust"][
        "dir"][2] == -1.0                             # single shaft: with the fuel pump
    print("turbopump placement helpers self-check: OK")

    # Placement rotation (E1): azimuth 0 + axial = identity (the legacy frame,
    # bit-for-bit); every rotation is proper; a rotated placement is the legacy one
    # pivoted rigidly about the origin - ports, body centres and meshes alike - and
    # the ports' bores / stub geometry survive it.
    assert np.array_equal(turbopump_rotation(0.0, "axial"), np.eye(3))
    for az in (0.0, 37.0, 90.0, 215.0):
        for orient in SHAFT_ORIENTATIONS:
            R = turbopump_rotation(az, orient)
            assert np.allclose(R.T @ R, np.eye(3)) and np.isclose(np.linalg.det(R), 1.0)
            # local y (outboard) is the engine radial at the azimuth, both orientations
            phi = np.radians(az)
            assert np.allclose(R[:, 1], [0.0, np.cos(phi), np.sin(phi)])
            assert np.isclose(abs(R[0, 0]), 1.0 if orient == "axial" else 0.0)
            pl = {"origin_xyz": origin, "rotation": R}
            o = np.asarray(origin)
            ports_r = turbopump_ports(bodies, pl, None, {"fuel_pump": 0.08, "ox_pump": 0.09},
                                      turbine_exhaust_dia_m=0.2)
            for key, group in turbopump_ports(bodies, origin, None,
                                              {"fuel_pump": 0.08, "ox_pump": 0.09},
                                              turbine_exhaust_dia_m=0.2).items():
                for nm, p in group.items():
                    q = ports_r[key][nm]
                    assert np.allclose(q["pos"], o + R @ (p["pos"] - o))
                    assert np.allclose(q["dir"], R @ p["dir"]) and q["dia_m"] == p["dia_m"]
                    assert np.allclose(q["pos"], q["base"] + PORT_STUB_DIA_MULT * q["dia_m"] * q["dir"])
            for c0, c1 in zip(turbopump_body_centers(bodies, origin),
                              turbopump_body_centers(bodies, pl)):
                assert np.allclose(c1["pos"], o + R @ (c0["pos"] - o))
            for (_, m0), (_, m1) in zip(turbopump_assembly_meshes(bodies, origin),
                                        turbopump_assembly_meshes(bodies, pl)):
                p0 = np.stack([np.asarray(a) for a in m0], axis=-1) - o
                p1 = np.stack([np.asarray(a) for a in m1], axis=-1) - o
                assert np.allclose(p1, p0 @ R.T)
    # identity placement dict == bare tuple, byte for byte
    pl_id = {"origin_xyz": origin, "rotation": np.eye(3)}
    for a, b in zip(turbopump_body_centers(bodies, origin), turbopump_body_centers(bodies, pl_id)):
        assert np.array_equal(a["pos"], b["pos"])
    print("turbopump placement rotation self-check: OK")

    # turbopump_placement (E1): the legacy rule exactly with a constant contour; span-
    # aware on a real-looking one (beside the chamber, not beyond the bell exit); every
    # box clears its local envelope by the standoff for any clocking / shaft orientation.
    boxes = boxes_from_bodies(bodies)
    od_max = max(b["od_m"] for b in bodies)
    xs_flat, rs_flat = np.array([0.0, 2.0]), np.array([0.5, 0.5])
    pl0 = turbopump_placement(boxes, xs_flat, rs_flat)
    assert np.allclose(pl0["origin_xyz"], turbopump_origin_xyz(2.0, 0.5, od_max), atol=1e-12)
    assert np.array_equal(pl0["rotation"], np.eye(3))
    xs_e = np.array([0.0, 0.6, 0.9, 1.2, 3.0])           # chamber 0.3, throat 0.15, bell 1.0
    rs_e = np.array([0.3, 0.3, 0.15, 0.3, 1.0])
    legacy = turbopump_origin_xyz(3.0, 1.0, od_max)
    for az in (0.0, 90.0, 215.0):
        for orient in SHAFT_ORIENTATIONS:
            for stand in (0.0, 0.05):
                pl = turbopump_placement(boxes, xs_e, rs_e, azimuth_deg=az,
                                         shaft_orientation=orient, standoff_m=stand,
                                         bands=[(0.05, 0.15, 0.42)])
                R = pl["rotation"]
                o = np.asarray(pl["origin_xyz"])
                assert pl["axis_radius_m"] < legacy[1] - 0.3, (az, orient, pl["axis_radius_m"])
                for b in boxes:   # each box's engine-side reach clears its own span's envelope
                    xw = [o[0] + R[0] @ np.array([x, 0.0, z])
                          for x in (b["x0"], b["x1"]) for z in (b["dz"] - b["half_z"],
                                                                 b["dz"] + b["half_z"])]
                    r_env = envelope_r_max(xs_e, rs_e, min(xw), max(xw), [(0.05, 0.15, 0.42)])
                    ctr = o + R @ np.array([0.5 * (b["x0"] + b["x1"]), 0.0, b["dz"]])
                    radial = float(np.dot(ctr, R[:, 1]))   # along the pump's outboard radial
                    gap = stand or TURBOPUMP_STANDOFF_R_FRACTION * r_env
                    assert radial - b["reach"] >= r_env + gap - 1e-9, (az, orient, b["kind"])
                # azimuth: the assembly centre sits on the clocked radial, axis_radius out
                c_l = 0.5 * (min(b["x0"] for b in boxes) + max(b["x1"] for b in boxes))
                ctr = o + R @ np.array([c_l, 0.0, 0.0])
                assert np.isclose(np.degrees(np.arctan2(ctr[2], ctr[1])) % 360.0, az % 360.0)
                assert np.isclose(np.hypot(ctr[1], ctr[2]), pl["axis_radius_m"])
    # an explicit axial station centres the assembly there; the ring band pushes it out
    pl_st = turbopump_placement(boxes, xs_e, rs_e, axial_station_frac=0.25)
    assert np.isclose(np.mean(pl_st["x_span_m"]), 0.75)
    pl_b = turbopump_placement(boxes, xs_e, rs_e, bands=[(0.0, 3.0, 0.9)])
    assert pl_b["envelope_r_m"] == 0.9 and pl_b["axis_radius_m"] > pl_st["axis_radius_m"]
    assert np.isclose(envelope_r_max(xs_e, rs_e, 0.85, 0.95), 0.175)  # throat region (interp. ends)
    assert np.isclose(envelope_r_max(xs_e, rs_e, -1.0, -0.5), 0.3)    # held at the end value
    print("turbopump_placement self-check: OK (legacy identity, span-aware clearance x "
          "azimuth x shaft orientation x standoff, station, bands)")

    # axial_bump_delta_r: peaks exactly at height_m at the center, is exactly
    # zero outside the half-width window, and is symmetric about the center
    # for the "smooth" (ring/lip), "flat" (old flange), and "rect" (bolted-
    # flange collar) shapes.
    xs_bump = np.linspace(-2.0, 2.0, 401)
    for shape in ("smooth", "flat", "rect"):
        d = axial_bump_delta_r(xs_bump, center_x_m=0.3, half_width_m=0.5,
                                height_m=0.02, shape=shape)
        center_idx = int(np.argmin(np.abs(xs_bump - 0.3)))
        assert abs(d[center_idx] - 0.02) < 1e-4, (shape, d[center_idx])
        assert np.all(d[xs_bump < 0.3 - 0.5 - 1e-9] == 0.0)
        assert np.all(d[xs_bump > 0.3 + 0.5 + 1e-9] == 0.0)
        left = axial_bump_delta_r(np.array([0.3 - 0.2]), 0.3, 0.5, 0.02, shape)
        right = axial_bump_delta_r(np.array([0.3 + 0.2]), 0.3, 0.5, 0.02, shape)
        assert abs(left[0] - right[0]) < 1e-12, (shape, left, right)
    # "rect" is a true hard step: exactly height_m everywhere inside the
    # window (no shoulder taper), unlike "flat" which still tapers near the
    # edges via cosine shoulders.
    d_rect = axial_bump_delta_r(xs_bump, 0.3, 0.5, 0.02, "rect")
    inside = np.abs(xs_bump - 0.3) <= 0.5
    assert np.allclose(d_rect[inside], 0.02)
    d_flat = axial_bump_delta_r(xs_bump, 0.3, 0.5, 0.02, "flat")
    assert not np.allclose(d_flat[inside], 0.02)  # flat has tapered shoulders, rect doesn't
    # a zero-height or zero-half-width bump is a no-op
    assert np.all(axial_bump_delta_r(xs_bump, 0.0, 0.5, 0.0) == 0.0)
    assert np.all(axial_bump_delta_r(xs_bump, 0.0, 0.0, 0.02) == 0.0)
    print("axial_bump_delta_r self-check: OK")
