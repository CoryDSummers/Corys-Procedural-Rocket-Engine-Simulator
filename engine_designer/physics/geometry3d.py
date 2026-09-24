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


def turbopump_origin_xyz(profile_x_max_m, profile_r_max_m, assembly_od_m):
    """The (x, y, z) the assembly's `x0_m = 0` bodies start from."""
    y_offset = (profile_r_max_m + 0.5 * assembly_od_m
                + TURBOPUMP_STANDOFF_R_FRACTION * profile_r_max_m)
    return (TURBOPUMP_ORIGIN_X_LENGTH_FRACTION * float(profile_x_max_m), float(y_offset), 0.0)


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
    the same placement turbopump_assembly_meshes(axis="x") draws, as data."""
    ox_, oy_, oz_ = origin_xyz
    out = []
    for b, dz in zip(bodies, turbopump_unit_dz(bodies)):
        out.append({"kind": b["kind"], "center": b.get("center", 0),
                    "pos": np.array([ox_ + b["x0_m"] + 0.5 * b["length_m"], oy_, oz_ + dz]),
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
    uses. None when there is no turbopump."""
    sizing = result.get("turbopump_sizing") if isinstance(result, dict) else None
    if not sizing or not sizing.get("bodies"):
        return None
    return turbopump_origin_xyz(float(np.max(result["profile_xs_m"])),
                                float(np.max(result["profile_rs_m"])),
                                sizing["assembly_od_m"])


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
      {"turbine": {"exhaust": {"base", "pos", "dir", "dia_m"}}}: the centre of
      the (first) turbine body's end face AWAY from the rest of its unit, `dir`
      axially out along the shaft - where the exhaust duct leaves the turbine.
    Each port also carries `base` (the point on the body surface); `pos` sits
    PORT_STUB_DIA_MULT x bore further out along `dir` - the nozzle stub's face,
    where a pipe run lands.
    """
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
                               "pos": inlet_pos + PORT_STUB_DIA_MULT * eye * inlet_dir},
                     "discharge": {"base": dis_pos, "dir": dis_dir, "dia_m": dis_dia,
                                   "pos": dis_pos + PORT_STUB_DIA_MULT * dis_dia * dis_dir}}
    turbines = [c for c in centers if c["kind"] == "turbine"]
    if turbine_exhaust_dia_m > 0 and turbines:
        c = turbines[0]
        others = [o for o in centers if o is not c and o["center"] == c["center"]]
        ref_x = float(np.mean([o["pos"][0] for o in others])) if others else c["pos"][0] - 1.0
        sx = 1.0 if c["pos"][0] > ref_x else -1.0
        ex_dir = np.array([sx, 0.0, 0.0])
        ex_base = c["pos"] + 0.5 * c["length_m"] * ex_dir
        d = float(turbine_exhaust_dia_m)
        out["turbine"] = {"exhaust": {"base": ex_base, "dir": ex_dir, "dia_m": d,
                                      "pos": ex_base + PORT_STUB_DIA_MULT * d * ex_dir}}
    return out


def turbopump_assembly_meshes(bodies, origin_xyz, axis="x", n_theta=20):
    """
    Build one (X, Y, Z) mesh per turbopump body from a `turbopump_sizing`
    `bodies` list (each {kind, od_m, length_m, x0_m, center}). The bodies of a
    unit are strung along `axis` starting at `origin_xyz`; for a dual-shaft
    turbopump the two units (center 0 / 1) are offset from each other along Z
    (turbopump_unit_dz).

    Returns list of (kind, (X, Y, Z)). Rendering only - no physics.
    """
    ox_, oy_, oz_ = origin_xyz
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
    assert np.isclose(abs(ex["base"][0] - tc["pos"][0]), 0.5 * tc["length_m"])   # axial end face
    assert np.allclose(ex["pos"], ex["base"] + PORT_STUB_DIA_MULT * 0.2 * ex["dir"])
    print("turbopump placement helpers self-check: OK")

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
