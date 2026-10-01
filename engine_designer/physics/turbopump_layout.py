"""
True-scale turbopump CASING layout (turbopump roadmap E2a/E2b, 2026-09-27) - the ONE
source of casing geometry, mesh-free, so physics can place ports on it.

Each component (pump / turbine / motor) is a local SPEC with its shaft on the local x
axis: revolved wall polylines, spiral volute / collector / exhaust scrolls with their
tangential discharge cones, tori, straight cones and bolted flanges, plus its ports
(base/pos/dir/dia_m, `pos` = the flange face). `build_layout` strings the components along
their shaft(s) - bearing/seal housings between neighbours, dual-shaft units side by side in
z - and `place_layout` puts the whole thing beside the engine the way geometry3d places the
ghost envelope.

Consumers:
  - the Turbopump 3D tab (gui/turbopump_scene.py) - always, at the local origin;
  - EngineDesign.turbopump_geometry_model "casings" (design/turbomachinery_stage.py): the
    pump inlet/discharge and turbine exhaust ports come from `ports_from_layout` instead of
    geometry3d.turbopump_ports, so plumbing lands on the real flanges and pump-connected
    line losses / the exhaust duct follow them; the main 3D preview and Shape Lab draw it.
    The default "envelope" never calls this module (bit-identical).
Meshing lives in gui/preview3d_gl_core/turbopump_meshes.layout_pieces.

Sizes come from the Round 2 meanline (pump_meanline: D2, b2, meridional shroud, volute
spiral, axial tip/chord) and turbopump_sizing's turbine envelope factors (no turbine
meanline until Round 3). The proportions below are Tier-3 defaults (ASSUMPTIONS.md): they
shape the drawn casing and, in "casings" mode, where the ports sit - they carry no mass
(the turbopump mass is still the specific-power rollup; casing walls/mass are roadmap E3).
"""
import math

import numpy as np

from . import geometry3d, turbopump_sizing

# --- casing proportions (Tier 3: drawing + port placement only, no mass) ------------------
HOUSING_CLEARANCE_D2 = 0.03         # casing stand-off outside the impeller shroud, x D2
INLET_LEAD_D2 = 0.05                # inlet neck ahead of the inducer, x D2 (Detail tab)
INDUCER_LEN_TIP_MULT = 0.4          # inducer length / inducer tip dia (Detail tab)
STAGE_PITCH_EXTRA_D2 = 0.35         # stage pitch = impeller axial length + this x D2 (Detail tab)
CROSSOVER_RISE_D2 = 0.06            # crossover barrel above r2 + clearance, x D2 (Detail tab)
SHAFT_R_HUB_MULT = 0.35             # shaft radius = this x hub radius + 0.02 D2 (Detail tab)
BEARING_HOUSING_SHAFT_MULT = 2.0    # bearing/seal housing radius / shaft radius
BEARING_HOUSING_LEN_D2 = 0.25       # bearing/seal housing length behind the pump, x D2
FLANGE_LIP_BORE_MULT = 0.35         # bolted flange lip / bore radius
FLANGE_WIDTH_BORE_MULT = 0.25       # bolted flange thickness / bore radius
FLANGE_BOLTS = 8
AXIAL_GAP_CHORD = 0.15              # axial blade-row gap / chord (Detail tab)
AXIAL_IGV_CHORD = 0.7               # inlet guide row length / chord (Detail tab)
AXIAL_ROW_CHORD = 0.6               # rotor / stator row length / chord (Detail tab)
COLLECTOR_SECTION_TIP_MULT = 0.35   # axial-pump collector section radius / tip radius (Detail tab)
TURBINE_CLEARANCE_DISK = 0.03       # rotor housing stand-off outside the disk OD, x disk OD
TURBINE_R_LINK_DISK = 0.25          # turbine hub-housing radius (where a bearing housing meets it), x disk OD
INLET_TORUS_SPLIT = 0.25            # inlet torus section radius / (manifold OD - disk OD)
INLET_TORUS_MIN_DISK = 0.06         # ... floored at this x disk OD
GG_INLET_TUBE_MULT = 0.7            # GG/preburner inlet stub radius / inlet torus section radius
GG_INLET_LEN_TUBE_MULT = 1.5        # stub length beyond the torus / its section radius
EXHAUST_SCROLL_EXIT_FRAC = 0.85     # exhaust scroll end-section radius / exhaust bore radius
EXHAUST_CONE_MIN_LEN_DIA = 0.5      # exhaust outlet cone minimum length / exhaust bore
EXHAUST_SCROLL_FLOOR_FRAC = 0.3     # its start-section radius / its end-section radius
CLOSED_CYCLE_OUTLET_DISK_MULT = 0.45  # turbine outlet bore when no exhaust port (staged/
                                      # expander: gas goes on to the injector), x disk OD
ENVELOPE_R_LINK_OD = 0.2            # correlation-pump / motor cylinder: link radius, x its OD
# Tangential discharge diffuser cone after a scroll: conical-diffuser half-angle and a
# length window in exit diameters (not a hydraulic design) - the cap keeps a port bore far
# above the scroll's end section (the port is sized by the downstream ring, not the pump)
# from stretching the cone metres long.
DISCHARGE_DIFFUSER_HALF_ANGLE_DEG = 5.0
DISCHARGE_MIN_LEN_DIA_MULT = 1.0
DISCHARGE_MAX_LEN_DIA_MULT = 1.5
VOLUTE_STATIONS = 73                # scroll stations the 10-deg meanline spiral is resampled to
# Every scroll discharges at u = pi: the -y side, facing the engine axis (u = 0 is +y, the
# manifold-ring convention), its cone tangential in +-z - where the ghost envelope's
# discharge port sits too (geometry3d.turbopump_ports).
DISCHARGE_END_U_RAD = math.pi
# Spacing (Cory's "tighten + fill", 2026-09-27): the bearing/seal housing between two
# neighbours on a shaft is turbopump_sizing.SHAFT_SPAN_FACTOR x the SMALLER neighbour's OD
# (the ghost uses the largest body - the turbine's - which left ~0.7 m of bare shaft on the
# F-1), and dual-shaft units sit this x the largest OD apart, envelope to envelope.
UNIT_CLEARANCE_OD_MULT = 0.10

PUMP_KEYS = ("fuel_pump", "ox_pump")
TURBINE_KEYS = ("turbine", "ox_turbine")


def volute_sections(spiral, r_tongue_m, floor_r_m, n=VOLUTE_STATIONS):
    """
    Meanline volute spiral table [(theta_deg, r_outer_m), ...] (pump_meanline.
    _volute_geometry: constant-mean-velocity law, outer radius = r_tongue + 2 x section
    radius) -> per-station (wrap_rad, center_r_m, tube_r_m). The section radius is floored
    (the throat area is 0 at the tongue; the casing must still cover the impeller outlet)
    and kept non-decreasing; the inner edge stays on r_tongue.
    """
    th = np.array([p[0] for p in spiral], dtype=float)
    ro = np.array([p[1] for p in spiral], dtype=float)
    u = np.linspace(th[0], th[-1], n)
    rs = np.maximum(float(floor_r_m), 0.5 * (np.interp(u, th, ro) - float(r_tongue_m)))
    rs = np.maximum.accumulate(rs)
    return math.radians(th[-1] - th[0]), float(r_tongue_m) + rs, rs


def scroll_exit(x_m, center_r_end_m, tube_r_end_m, u_end_rad, handed, discharge_dia_m,
                half_angle_deg=DISCHARGE_DIFFUSER_HALF_ANGLE_DEG,
                min_len_dia_mult=DISCHARGE_MIN_LEN_DIA_MULT,
                max_len_dia_mult=DISCHARGE_MAX_LEN_DIA_MULT):
    """The tangential discharge cone leaving a scroll's end section (at angle u_end round
    the x axis, wrapped in the `handed` +1/-1 sense): {"start", "end", "r0", "r1", "dir"}.
    Length keeps the cone at half_angle_deg, clamped to [min, max] x the exit diameter;
    discharge_dia_m <= 0 keeps the end section's own bore."""
    handed = 1 if handed >= 0 else -1
    radial = np.array([0.0, math.cos(u_end_rad), math.sin(u_end_rad)])
    onward = handed * np.array([0.0, -math.sin(u_end_rad), math.cos(u_end_rad)])
    start = np.array([float(x_m), 0.0, 0.0]) + float(center_r_end_m) * radial
    r0 = float(tube_r_end_m)
    r1 = 0.5 * discharge_dia_m if discharge_dia_m > 0.0 else r0
    length = min(max(min_len_dia_mult * 2.0 * r1,
                     abs(r1 - r0) / math.tan(math.radians(half_angle_deg))),
                 max_len_dia_mult * 2.0 * r1)
    return {"start": start, "end": start + length * onward, "r0": r0, "r1": r1, "dir": onward}


def _scroll(x_m, ctr, tube, wrap_rad, handed, discharge_dia_m, **cone_kw):
    """A scroll spec ending at DISCHARGE_END_U_RAD, + its discharge cone."""
    handed = 1 if handed >= 0 else -1
    span = handed * float(wrap_rad)
    ctr = np.asarray(ctr, dtype=float)
    tube = np.asarray(tube, dtype=float)
    return {"x": float(x_m), "center_r": ctr, "tube_r": tube,
            "u_start": DISCHARGE_END_U_RAD - span, "span": span,
            "cone": scroll_exit(x_m, ctr[-1], tube[-1], DISCHARGE_END_U_RAD, handed,
                                discharge_dia_m, **cone_kw)}


def _flange(face, direction, bore_r):
    """A bolted flange whose OUTER face is `face` (the port / mating plane), `dir` pointing
    out of it; the flange body sits FLANGE_WIDTH_BORE_MULT x bore behind the face."""
    return {"face": np.asarray(face, dtype=float), "dir": np.asarray(direction, dtype=float),
            "bore_r": float(bore_r)}


def _port(base, pos, direction, dia_m):
    return {"base": np.asarray(base, dtype=float), "pos": np.asarray(pos, dtype=float),
            "dir": np.asarray(direction, dtype=float), "dia_m": float(dia_m)}


def _component(key, kind, length_m, r_link_m, od_m, summary, revolves=(), scrolls=(),
               tori=(), cones=(), flanges=(), ports=None):
    """`od_m` = the casing's own OD (volute / torus / barrel, NOT the discharge cones) -
    what the bearing spans and the dual-shaft unit gap are sized on."""
    return {"key": key, "kind": kind, "length_m": float(length_m), "r_link_m": float(r_link_m),
            "od_m": float(od_m), "summary": summary, "revolves": list(revolves),
            "scrolls": list(scrolls), "tori": list(tori), "cones": list(cones),
            "flanges": list(flanges), "ports": ports or {}}


def _eye_dia(pump):
    return float(pump.get("inlet_eye_dia_m", 0.0) or 0.0)


def centrifugal_pump(key, pump, discharge_dia_m, handed=1):
    """One centrifugal pump in its LOCAL frame: inlet flange face at x = 0 (flow enters
    along +x), casing walked inlet -> back so the housing's outside is the polyline's left.
    """
    ml = pump["meanline"]
    st, mer, vol = ml["stage"], ml["meridional"], ml["volute"]
    d2, b2, n = st["d2_m"], st["b2_m"], ml["n_stages"]
    r2 = 0.5 * d2
    c = HOUSING_CLEARANCE_D2 * d2
    dt = _eye_dia(pump) or st["d1_m"]
    r_in = max(0.5 * dt, 0.5 * st["d1_m"]) + c
    lead = INDUCER_LEN_TIP_MULT * dt + INLET_LEAD_D2 * d2
    lz = mer["axial_length_m"] - b2
    pitch = mer["axial_length_m"] + STAGE_PITCH_EXTRA_D2 * d2
    r_shaft = SHAFT_R_HUB_MULT * 0.5 * st["d_hub_m"] + 0.02 * d2
    r_bh = min(BEARING_HOUSING_SHAFT_MULT * r_shaft, 0.8 * r_in)

    xs, rs = [0.0, lead], [r_in, r_in]
    for z, r in mer["shroud"]:
        xs.append(lead + z)
        rs.append(max(r + c, r_in))
    x_tip = lead + lz + (n - 1) * pitch             # last stage's impeller tip plane
    if n > 1:                                         # stages 1..n-1: crossover barrel
        r_bar = r2 + c + CROSSOVER_RISE_D2 * d2
        xs += [xs[-1], x_tip]
        rs += [r_bar, r_bar]
    r_side = max(vol["r_tongue_m"], rs[-1])           # side wall up to the volute's inner edge
    x_back = x_tip + b2 + c
    x_end = x_back + BEARING_HOUSING_LEN_D2 * d2
    xs += [x_tip, x_back, x_back, x_end, x_end]
    rs += [r_side, r_side, r_bh, r_bh, 0.0]

    wrap, ctr, tube = volute_sections(vol["spiral"], vol["r_tongue_m"], 0.5 * b2 + c)
    scroll = _scroll(x_tip + 0.5 * b2, ctr, tube, wrap, handed, discharge_dia_m)
    cone = scroll["cone"]
    diff = vol.get("diffuser")
    summary = (f"centrifugal, {n} stage{'s' if n > 1 else ''}, D2 {d2 * 1e3:.0f} mm, "
               f"b2 {b2 * 1e3:.1f} mm, inlet {dt * 1e3:.0f} mm, volute OD "
               f"{vol['od_m'] * 1e3:.0f} mm ({'vaned diffuser, ' + str(diff['zd']) + ' vanes' if diff else 'vaneless'}), "
               f"discharge {2.0 * cone['r1'] * 1e3:.0f} mm")
    ports = {"inlet": _port((lead, 0.0, 0.0), (0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), _eye_dia(pump)),
             "discharge": _port(cone["start"], cone["end"], cone["dir"], discharge_dia_m)}
    return _component(key, "pump", x_end, r_bh, 2.0 * float(np.max(ctr + tube)), summary,
                      revolves=[(np.array(xs), np.array(rs))], scrolls=[scroll],
                      flanges=[_flange((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), r_in),
                               _flange(cone["end"], cone["dir"], cone["r1"])],
                      ports=ports)


def axial_pump(key, pump, discharge_dia_m, handed=1):
    """An axial pump (inducer + inlet guide row + n rotor/stator rows, the Detail tab's
    row lengths) in a barrel, discharging through a constant-section collector (the
    meanline designs no volute for an axial pump - the Detail tab's 0.35 x r_tip section)."""
    ml = pump["meanline"]
    dt, chord, n = ml["d_tip_m"], ml["chord_m"], ml["n_stages"]
    rt = 0.5 * dt
    c = HOUSING_CLEARANCE_D2 * dt
    gap = AXIAL_GAP_CHORD * chord
    eye = _eye_dia(pump) or dt
    r_b = max(rt, 0.5 * eye) + c
    rows = (INDUCER_LEN_TIP_MULT * dt + gap + AXIAL_IGV_CHORD * chord + gap
            + n * (2.0 * AXIAL_ROW_CHORD * chord + 2.0 * gap))
    r_sec = COLLECTOR_SECTION_TIP_MULT * rt
    x_c = INLET_LEAD_D2 * dt + rows + r_sec
    x_back = x_c + r_sec
    r_bh = min(BEARING_HOUSING_SHAFT_MULT * 0.6 * 0.5 * ml["d_hub_m"], 0.8 * r_b)
    x_end = x_back + BEARING_HOUSING_LEN_D2 * dt
    xs = np.array([0.0, x_back, x_back, x_end, x_end])
    rs = np.array([r_b, r_b, r_bh, r_bh, 0.0])
    ctr = np.full(VOLUTE_STATIONS, r_b + 0.2 * r_sec)
    tube = np.full(VOLUTE_STATIONS, r_sec)
    scroll = _scroll(x_c, ctr, tube, 2.0 * math.pi, handed, discharge_dia_m)
    cone = scroll["cone"]
    summary = (f"axial, inducer + {n} stages, tip {dt * 1e3:.0f} mm, hub/tip "
               f"{ml['hub_tip']:.2f}, discharge {2.0 * cone['r1'] * 1e3:.0f} mm")
    ports = {"inlet": _port((INLET_LEAD_D2 * dt, 0.0, 0.0), (0.0, 0.0, 0.0), (-1.0, 0.0, 0.0),
                            _eye_dia(pump)),
             "discharge": _port(cone["start"], cone["end"], cone["dir"], discharge_dia_m)}
    return _component(key, "pump", x_end, r_bh, 2.0 * (r_b + 1.2 * r_sec), summary,
                      revolves=[(xs, rs)], scrolls=[scroll],
                      flanges=[_flange((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), r_b),
                               _flange(cone["end"], cone["dir"], cone["r1"])],
                      ports=ports)


def _cylinder_polyline(od_m, length_m):
    r = 0.5 * od_m
    return np.array([0.0, 0.0, length_m, length_m]), np.array([0.0, r, r, 0.0])


def envelope_pump(key, pump, discharge_dia_m, handed=1):
    """Fallback for a pump with no meanline (pump_model "correlation"): its true-scale
    envelope cylinder (volute OD x body length, before the ghost's render_scale), with a
    straight discharge stub on the -y side like the ghost's."""
    od, length = pump["volute_od_m"], pump["body_length_m"]
    r = 0.5 * od
    direction = np.array([0.0, 0.0, -float(1 if handed >= 0 else -1)])
    base = np.array([0.5 * length, -r, 0.0])
    pos = base + geometry3d.PORT_STUB_DIA_MULT * discharge_dia_m * direction
    cones, flanges = [], [_flange((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), max(0.5 * _eye_dia(pump), 0.2 * r))]
    if discharge_dia_m > 0.0:
        cones.append((base, pos, 0.5 * discharge_dia_m, 0.5 * discharge_dia_m))
        flanges.append(_flange(pos, direction, 0.5 * discharge_dia_m))
    ports = {"inlet": _port((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), _eye_dia(pump)),
             "discharge": _port(base, pos, direction, discharge_dia_m)}
    return _component(key, "pump", length, ENVELOPE_R_LINK_OD * od, od,
                      f"envelope only (pump model 'correlation' - no meanline geometry), "
                      f"OD {od * 1e3:.0f} mm",
                      revolves=[_cylinder_polyline(od, length)], cones=cones, flanges=flanges,
                      ports=ports)


def turbine(key, tb, exhaust_dia_m, handed=1):
    """A turbine in its LOCAL frame, x = 0 on its pump side: rotor housing round the disk,
    an inlet manifold torus with a radial GG/preburner inlet stub (+y), and an exhaust
    scroll discharging tangentially to `exhaust_dia_m` (the turbine exhaust port's true
    bore, or a closed-cycle outlet default). Sizes are turbopump_sizing's envelope factors -
    no turbine meanline until Round 3."""
    dod = tb["disk_od_m"]
    r_h = 0.5 * dod + TURBINE_CLEARANCE_DISK * dod
    tube_in = max(INLET_TORUS_SPLIT * (tb["manifold_od_m"] - dod), INLET_TORUS_MIN_DISK * dod)
    ctr_in = max(0.5 * tb["manifold_od_m"] - tube_in, r_h)
    closed = exhaust_dia_m <= 0.0
    exh = CLOSED_CYCLE_OUTLET_DISK_MULT * dod if closed else exhaust_dia_m
    rs_end = EXHAUST_SCROLL_EXIT_FRAC * 0.5 * exh
    length = max(tb["disk_thickness_m"] + tb["manifold_length_m"],
                 2.0 * tube_in + 2.0 * rs_end + tb["disk_thickness_m"])
    x_in = tube_in
    stub_r = GG_INLET_TUBE_MULT * tube_in
    stub_end = np.array([x_in, ctr_in + tube_in + GG_INLET_LEN_TUBE_MULT * tube_in, 0.0])
    tube = np.linspace(EXHAUST_SCROLL_FLOOR_FRAC * rs_end, rs_end, VOLUTE_STATIONS)
    scroll = _scroll(length - rs_end, r_h + tube, tube, 2.0 * math.pi, handed, exh,
                     min_len_dia_mult=EXHAUST_CONE_MIN_LEN_DIA)
    cone = scroll["cone"]
    summary = (f"{tb['staging'].replace('_', ' ')}, pitchline {tb['d_mean_m'] * 1e3:.0f} mm, "
               f"disk OD {dod * 1e3:.0f} mm, inlet torus OD {2 * (ctr_in + tube_in) * 1e3:.0f} mm, "
               + (f"outlet {exh * 1e3:.0f} mm (closed cycle - default bore)" if closed
                  else f"exhaust {exh * 1e3:.0f} mm"))
    ports = {} if closed else {"exhaust": _port(cone["start"], cone["end"], cone["dir"], exh)}
    return _component(key, "turbine", length, TURBINE_R_LINK_DISK * dod,
                      2.0 * max(ctr_in + tube_in, r_h + 2.0 * rs_end), summary,
                      revolves=[_cylinder_polyline(2.0 * r_h, length)], scrolls=[scroll],
                      tori=[(x_in, ctr_in, tube_in)],
                      cones=[(np.array([x_in, ctr_in, 0.0]), stub_end, stub_r, stub_r)],
                      flanges=[_flange(stub_end, (0.0, 1.0, 0.0), stub_r),
                               _flange(cone["end"], cone["dir"], 0.5 * exh)],
                      ports=ports)


def motor(motor_body):
    od, length = motor_body["od_m"], motor_body["length_m"]
    return _component("motor", "motor", length, ENVELOPE_R_LINK_OD * od, od,
                      f"electric motor + controller (mass-sized cylinder), OD {od * 1e3:.0f} mm",
                      revolves=[_cylinder_polyline(od, length)])


def units_for(sizing):
    """[[component key, ...] per shaft unit], in drawing order along +x - the ghost's
    order (turbopump_sizing._assemble_bodies): single-shaft / geared fuel pump | turbine
    (or motor) | ox pump inline; dual-shaft [fuel pump, turbine] + [ox pump, ox turbine]."""
    if sizing.get("arrangement") == "dual_shaft" and sizing.get("ox_turbine"):
        return [[k for k in ("fuel_pump", "turbine") if sizing.get(k)],
                [k for k in ("ox_pump", "ox_turbine") if sizing.get(k)]]
    middle = []
    if sizing.get("turbine"):
        middle = ["turbine"]
    elif any(b["kind"] == "motor" for b in sizing.get("bodies", [])):
        middle = ["motor"]
    return [[k for k in ["fuel_pump"] + middle + ["ox_pump"]
             if k == "motor" or sizing.get(k)]]


def _discharge_sign(key, unit_index, dual):
    """+1/-1: the z direction a component's scroll discharges in - away from the assembly
    centre, the ghost's convention (geometry3d.turbopump_ports): single shaft fuel -z /
    ox +z (the turbine with the fuel side); dual shaft by unit (unit 0 sits at -z)."""
    if dual:
        return -1 if unit_index == 0 else 1
    return 1 if key == "ox_pump" else -1


def _neg_y_extent(comp):
    """How far a LOCAL component reaches toward -y (the engine side) - conservative."""
    lip = 1.0 + FLANGE_LIP_BORE_MULT
    ext = [float(np.max(rs)) for _, rs in comp["revolves"]]
    for s in comp["scrolls"]:
        ext.append(float(np.max(s["center_r"] + s["tube_r"])))
        cn = s["cone"]
        ext += [-cn["start"][1] + cn["r0"] * lip, -cn["end"][1] + cn["r1"] * lip]
    ext += [ctr + tube for _, ctr, tube in comp["tori"]]
    for a, b, ra, rb in comp["cones"]:
        ext += [-a[1] + ra * lip, -b[1] + rb * lip]
    ext += [-f["face"][1] + f["bore_r"] * lip for f in comp["flanges"]]
    return max(ext) if ext else 0.0


def _pos_y_extent(comp):
    """How far a LOCAL component reaches toward +y (outboard) - _neg_y_extent's mirror; a
    rolled / flipped placement can turn this side toward the engine."""
    lip = 1.0 + FLANGE_LIP_BORE_MULT
    ext = [float(np.max(rs)) for _, rs in comp["revolves"]]
    for s in comp["scrolls"]:
        ext.append(float(np.max(s["center_r"] + s["tube_r"])))
        cn = s["cone"]
        ext += [cn["start"][1] + cn["r0"] * lip, cn["end"][1] + cn["r1"] * lip]
    ext += [ctr + tube for _, ctr, tube in comp["tori"]]
    for a, b, ra, rb in comp["cones"]:
        ext += [a[1] + ra * lip, b[1] + rb * lip]
    ext += [f["face"][1] + f["bore_r"] * lip for f in comp["flanges"]]
    return max(ext) if ext else 0.0


def build_layout(sizing, discharge_dia_by_pump=None, turbine_exhaust_dia_m=0.0):
    """
    The whole assembly at true scale, at the LOCAL origin (place_layout moves it beside
    the engine): {"arrangement", "units", "components": {key: local spec}, "placements":
    {key: {x0, sx, dz, x_start, x_end}}, "links": [{x0, x1, r0, r1, dz}] (bearing/seal
    housings between neighbours), "unit_gap_m", "length_m", "neg_y_extent_m",
    "origin_xyz"}. None without a turbopump (pressure-fed / no sizing).
    `discharge_dia_by_pump` = each pump's discharge port bore (the downstream ring's feed
    bore, as geometry3d.turbopump_ports gets it); `turbine_exhaust_dia_m` > 0 = an open
    cycle's exhaust port bore (else a closed-cycle outlet is drawn and no port made).
    """
    if not sizing or not any(sizing.get(k) for k in PUMP_KEYS):
        return None
    dis = discharge_dia_by_pump or {}
    units = units_for(sizing)
    dual = len(units) > 1
    comps = {}
    for u_idx, unit in enumerate(units):
        for key in unit:
            handed = -_discharge_sign(key, u_idx, dual)     # scroll dir z = -handed at u = pi
            if key in PUMP_KEYS:
                pump = sizing[key]
                ml = pump.get("meanline")
                d = float(dis.get(key, 0.0) or 0.0)
                if ml is None:
                    comps[key] = envelope_pump(key, pump, d, handed)
                elif ml["type"] == "axial":
                    comps[key] = axial_pump(key, pump, d, handed)
                else:
                    comps[key] = centrifugal_pump(key, pump, d, handed)
            elif key in TURBINE_KEYS:
                comps[key] = turbine(key, sizing[key], float(turbine_exhaust_dia_m or 0.0), handed)
            else:
                comps[key] = motor(next(b for b in sizing["bodies"] if b["kind"] == "motor"))

    unit_ods = [max(comps[k]["od_m"] for k in unit) for unit in units]
    unit_gap = (0.5 * unit_ods[0] + 0.5 * unit_ods[1]
                + UNIT_CLEARANCE_OD_MULT * max(unit_ods)) if dual else 0.0
    placements, links, length = {}, [], 0.0
    for u_idx, unit in enumerate(units):
        dz = (u_idx - (len(units) - 1) / 2.0) * unit_gap
        x = 0.0
        for i, key in enumerate(unit):
            comp = comps[key]
            if i > 0:
                prev = comps[unit[i - 1]]
                span = turbopump_sizing.SHAFT_SPAN_FACTOR * min(prev["od_m"], comp["od_m"])
                links.append({"x0": x, "x1": x + span, "r0": prev["r_link_m"],
                              "r1": comp["r_link_m"], "dz": dz})
                x += span
            # a pump after the first component of its unit faces its inlet outboard (+x)
            sx = -1.0 if (key in PUMP_KEYS and i > 0) else 1.0
            placements[key] = {"x0": x + comp["length_m"] if sx < 0 else x, "sx": sx, "dz": dz,
                               "x_start": x, "x_end": x + comp["length_m"]}
            x += comp["length_m"]
        length = max(length, x)
    neg_y = max([_neg_y_extent(c) for c in comps.values()]
                + [max(k["r0"], k["r1"]) for k in links])
    return {"arrangement": sizing.get("arrangement", ""), "units": units, "components": comps,
            "placements": placements, "links": links, "unit_gap_m": unit_gap,
            "length_m": length, "neg_y_extent_m": neg_y, "origin_xyz": (0.0, 0.0, 0.0)}


def _z_extent(comp):
    """How far a LOCAL component reaches either way in z (the dual-unit / tangential
    direction) - conservative, like _neg_y_extent."""
    lip = 1.0 + FLANGE_LIP_BORE_MULT
    ext = [float(np.max(rs)) for _, rs in comp["revolves"]]
    for s in comp["scrolls"]:
        ext.append(float(np.max(s["center_r"] + s["tube_r"])))
        cn = s["cone"]
        ext += [abs(cn["start"][2]) + cn["r0"] * lip, abs(cn["end"][2]) + cn["r1"] * lip]
    ext += [ctr + tube for _, ctr, tube in comp["tori"]]
    for a, b, ra, rb in comp["cones"]:
        ext += [abs(a[2]) + ra * lip, abs(b[2]) + rb * lip]
    ext += [abs(f["face"][2]) + f["bore_r"] * lip for f in comp["flanges"]]
    return max(ext) if ext else 0.0


def _x_extent(comp):
    """(lo, hi) of a component along its OWN shaft x (before the layout's sx flip) over
    everything drawn - revolves, scrolls / tori (+- tube), discharge cones and flanges
    (+- the lip) - a flange or scroll can stand proud of the [0, length] span, which a
    head mount (clearing the injector along x) has to see."""
    lip = 1.0 + FLANGE_LIP_BORE_MULT
    lo, hi = [0.0], [float(comp["length_m"])]
    for xs, _ in comp["revolves"]:
        lo.append(float(np.min(xs)))
        hi.append(float(np.max(xs)))
    for s in comp["scrolls"]:
        t = float(np.max(s["tube_r"]))
        lo.append(s["x"] - t)
        hi.append(s["x"] + t)
        cn = s["cone"]
        for p, r in ((cn["start"], cn["r0"]), (cn["end"], cn["r1"])):
            lo.append(p[0] - r * lip)
            hi.append(p[0] + r * lip)
    for x, _ctr, tube in comp["tori"]:
        lo.append(x - tube)
        hi.append(x + tube)
    for a, b, ra, rb in comp["cones"]:
        lo += [a[0] - ra * lip, b[0] - rb * lip]
        hi += [a[0] + ra * lip, b[0] + rb * lip]
    for f in comp["flanges"]:
        lo.append(f["face"][0] - f["bore_r"] * lip)
        hi.append(f["face"][0] + f["bore_r"] * lip)
    return min(lo), max(hi)


def layout_boxes(layout):
    """The casing layout as LOCAL placement boxes (geometry3d.turbopump_placement): one per
    component (its drawn shaft-wise extent - _x_extent mapped through its x0 / sx - unit
    offset, z half-width and engine-side / outboard reach) and one per bearing/seal housing
    between neighbours."""
    boxes = []
    for key, comp in layout["components"].items():
        pl = layout["placements"][key]
        e_lo, e_hi = _x_extent(comp)
        ends = (pl["x0"] + pl["sx"] * e_lo, pl["x0"] + pl["sx"] * e_hi)
        boxes.append({"x0": min(pl["x_start"], *ends), "x1": max(pl["x_end"], *ends),
                      "dz": pl["dz"],
                      "half_z": _z_extent(comp), "reach": _neg_y_extent(comp),
                      "reach_out": _pos_y_extent(comp), "kind": key})
    for k in layout["links"]:
        r = max(k["r0"], k["r1"])
        boxes.append({"x0": k["x0"], "x1": k["x1"], "dz": k["dz"], "half_z": r, "reach": r,
                      "reach_out": r, "kind": "shaft"})
    return boxes


def place_layout(layout, profile_xs_m, profile_rs_m, **placement_kw):
    """`layout` moved beside the engine by the ONE placement rule the ghost uses
    (geometry3d.turbopump_placement - azimuth / axial station / standoff / shaft
    orientation in `placement_kw`, the obstacle `bands`): each casing box clears the local
    contour + rings over its own span. Adds "rotation" and "placement" (the solve's
    report) to the layout."""
    if layout is None:
        return None
    pl = geometry3d.turbopump_placement(layout_boxes(layout), profile_xs_m, profile_rs_m,
                                        **placement_kw)
    return dict(layout, origin_xyz=pl["origin_xyz"], rotation=pl["rotation"], placement=pl)


def _rotation(layout):
    """The placed layout's rotation (geometry3d.split_placement: None = legacy frame)."""
    return geometry3d.split_placement(layout)[1]


def to_world(layout, key, point):
    """A component-local point -> the layout's frame (engine coordinates once placed):
    strung along the shaft (x0 + sx x, dz), then the placement's rotation about the origin
    (geometry3d.turbopump_rotation; None / identity = the legacy translate-only frame)."""
    pl = layout["placements"][key]
    ox, oy, oz = layout["origin_xyz"]
    p = np.asarray(point, dtype=float)
    rot = _rotation(layout)
    if rot is None:
        return np.array([ox + pl["x0"] + pl["sx"] * p[0], oy + p[1], oz + pl["dz"] + p[2]])
    local = np.array([pl["x0"] + pl["sx"] * p[0], p[1], pl["dz"] + p[2]])
    return np.array([ox, oy, oz], dtype=float) + rot @ local


def dir_to_world(layout, key, direction):
    d = np.asarray(direction, dtype=float)
    out = np.array([layout["placements"][key]["sx"] * d[0], d[1], d[2]])
    return geometry3d.place_dir(_rotation(layout), out)


def _port_world(layout, key, port):
    return {"base": to_world(layout, key, port["base"]), "pos": to_world(layout, key, port["pos"]),
            "dir": dir_to_world(layout, key, port["dir"]), "dia_m": port["dia_m"],
            "frame": geometry3d.placement_frame_of(dict(layout.get("placement") or {},
                                                        origin_xyz=layout["origin_xyz"],
                                                        rotation=layout.get("rotation")))}


def ports_from_layout(layout):
    """The same dict geometry3d.turbopump_ports returns - {"fuel_pump"/"ox_pump":
    {"inlet", "discharge"}, "turbine": {"exhaust"} (open cycles only)}, each
    {base, pos, dir, dia_m} - but on the casing: `pos` = the flange face a pipe run lands
    on, `base` = where that neck / cone leaves the casing."""
    if layout is None:
        return None
    comps = layout["components"]
    out = {key: {name: _port_world(layout, key, p) for name, p in comps[key]["ports"].items()}
           for key in PUMP_KEYS if key in comps}
    if "turbine" in comps and "exhaust" in comps["turbine"]["ports"]:
        out["turbine"] = {"exhaust": _port_world(layout, "turbine",
                                                 comps["turbine"]["ports"]["exhaust"])}
    return out


def pump_points_from_layout(layout):
    """{"fuel_pump"/"ox_pump": xyz} - each pump casing's centre on its shaft (the Shape
    Lab's straight-ray target, geometry3d.turbopump_pump_points' casing twin)."""
    out = {}
    origin = layout["origin_xyz"]
    ox, oy, oz = origin
    rot = _rotation(layout)
    for key in PUMP_KEYS:
        pl = layout["placements"].get(key)
        if pl:
            out[key] = geometry3d.place_point(
                origin, rot, np.array([ox + 0.5 * (pl["x_start"] + pl["x_end"]), oy, oz + pl["dz"]]))
    return out


def self_test():
    import json
    import os
    from .design import EngineDesign

    # --- volute sections from a meanline-style spiral table ---
    r_tongue = 0.105
    spiral = [(10.0 * i, r_tongue + 2.0 * math.sqrt(0.002 * i / 36.0 / math.pi))
              for i in range(37)]
    wrap, ctr, tube = volute_sections(spiral, r_tongue, 0.004)
    assert abs(wrap - 2.0 * math.pi) < 1e-12
    assert tube[0] == 0.004 and np.all(np.diff(tube) >= 0.0)
    assert np.allclose(ctr - tube, r_tongue)                   # inner edge on the tongue circle
    assert abs(ctr[-1] + tube[-1] - spiral[-1][1]) < 1e-9       # outer edge on the table
    # scroll discharge: starts on the end section at u = pi (-y), tangential, z = -handed
    for handed in (1, -1):
        s = _scroll(0.2, ctr, tube, wrap, handed, 0.06)
        cn = s["cone"]
        assert np.allclose(cn["start"], [0.2, -ctr[-1], 0.0], atol=1e-12)
        assert np.allclose(cn["dir"], [0.0, 0.0, -handed], atol=1e-12)
        assert abs(s["u_start"] + s["span"] - math.pi) < 1e-12
        length = np.linalg.norm(cn["end"] - cn["start"])
        assert math.degrees(math.atan(abs(cn["r1"] - cn["r0"]) / length)) \
            <= DISCHARGE_DIFFUSER_HALF_ANGLE_DEG + 1e-9
        assert length <= DISCHARGE_MAX_LEN_DIA_MULT * 0.06 + 1e-12

    here = os.path.join(os.path.dirname(__file__), "..", "validation_engines", "engines")

    def corpus(name, **over):
        with open(os.path.join(here, f"{name}.json")) as f:
            d = json.load(f)["design"]
        d.update(over)
        return EngineDesign.from_dict({"schema_version": EngineDesign.SCHEMA_VERSION, "design": d})

    for name, over in [("F-1", {}), ("J-2", {}), ("RS-25", {}), ("RL10A-3-3", {}),
                       ("Rutherford", {}), ("Merlin-1D", {}), ("F-1", {"pump_model": "correlation"})]:
        r = corpus(name, **over).compute()
        sz = r["turbopump_sizing"]
        ports = r["turbopump_ports"]
        dis = {k: ports[k]["discharge"]["dia_m"] for k in PUMP_KEYS}
        exh = ports.get("turbine", {}).get("exhaust", {}).get("dia_m", 0.0)
        lay = place_layout(build_layout(sz, dis, exh), r["profile_xs_m"], r["profile_rs_m"])
        tag = f"{name}{over or ''}"
        dual = len(lay["units"]) > 1
        cp = ports_from_layout(lay)
        assert set(cp) == set(ports), (tag, set(cp), set(ports))   # same ports as the ghost
        oz = lay["origin_xyz"][2]
        for key, group in cp.items():
            for pname, p in group.items():
                for v in ("base", "pos", "dir"):
                    assert np.all(np.isfinite(p[v])), (tag, key, pname)
                assert abs(np.linalg.norm(p["dir"]) - 1.0) < 1e-12, (tag, key, pname)
                assert p["dia_m"] == ports[key][pname]["dia_m"], (tag, key, pname)
                # the port face is a flange face of its own component
                comp_key = key
                faces = [to_world(lay, comp_key, f["face"])
                         for f in lay["components"][comp_key]["flanges"]]
                if pname != "discharge" or p["dia_m"] > 0:
                    assert min(np.linalg.norm(f - p["pos"]) for f in faces) < 1e-12, (tag, key, pname)
                if pname in ("discharge", "exhaust") and "correlation" not in str(over):
                    # engine side (-y of the shaft), tangential, away from the assembly centre
                    shaft_y = lay["origin_xyz"][1]
                    assert p["pos"][1] < shaft_y, (tag, key)
                    unit = next(i for i, u in enumerate(lay["units"]) if key in u)
                    want = _discharge_sign(key, unit, dual)
                    assert abs(p["dir"][2] - want) < 1e-12, (tag, key, p["dir"])
                    if dual:
                        assert np.sign(p["pos"][2] - oz) == want, (tag, key)
                assert lay["origin_xyz"][1] - p["pos"][1] <= lay["neg_y_extent_m"] + 1e-9, (tag, key)
            if key in PUMP_KEYS:   # inlet faces away from the rest of its unit
                unit = next(u for u in lay["units"] if key in u)
                rest = [0.5 * (lay["placements"][k]["x_start"] + lay["placements"][k]["x_end"])
                        for k in unit if k != key]
                mid = 0.5 * (lay["placements"][key]["x_start"] + lay["placements"][key]["x_end"])
                if rest:
                    assert np.sign(group["inlet"]["dir"][0]) == np.sign(mid - np.mean(rest)), (tag, key)
        # the engine-side reach clears the chamber by the ghost's stand-off
        # every casing box clears the local contour over its own span by the standoff
        # (span-aware, E1) - and the assembly sits inboard of the old bell-exit rule
        for kind, clr in geometry3d.placement_clearances(layout_boxes(lay), lay["placement"],
                                                         r["profile_xs_m"], r["profile_rs_m"]):
            assert clr > 0.0, (tag, kind, clr)
        r_max = float(np.max(r["profile_rs_m"]))
        assert lay["origin_xyz"][1] - lay["neg_y_extent_m"] <= r_max * 1.04 + 1e-9, tag
        # tightened spans: each bearing housing is SHAFT_SPAN_FACTOR x the smaller neighbour
        for k in lay["links"]:
            assert k["x1"] > k["x0"] and k["r0"] > 0 and k["r1"] > 0, tag
        if dual:   # the two units' envelopes don't overlap
            ods = [max(lay["components"][k]["od_m"] for k in u) for u in lay["units"]]
            assert lay["unit_gap_m"] - 0.5 * sum(ods) > 0.0, tag
            ghost_gap = geometry3d.TURBOPUMP_UNIT_GAP_OD_MULT * max(ods)
            assert lay["unit_gap_m"] < ghost_gap, (tag, lay["unit_gap_m"], ghost_gap)
        if name == "F-1" and not over:
            f = lay["placements"]
            gap = f["turbine"]["x_start"] - f["fuel_pump"]["x_end"]
            assert gap < 0.69 * 0.7, gap                          # was 0.69 m of bare shaft
        pts = pump_points_from_layout(lay)
        assert set(pts) == set(PUMP_KEYS), tag
        # placement rotation (E1): the rotated layout is the legacy one pivoted rigidly
        # about its origin - ports still on their flange faces, bores unchanged
        o = np.asarray(lay["origin_xyz"])
        for az, orient in ((37.0, "axial"), (215.0, "tangential")):
            R = geometry3d.turbopump_rotation(az, orient)
            rl = dict(lay, rotation=R)
            rp = ports_from_layout(rl)
            for key, group in cp.items():
                faces = [to_world(rl, key, f["face"]) for f in lay["components"][key]["flanges"]]
                for pname, p in group.items():
                    q = rp[key][pname]
                    assert np.allclose(q["pos"], o + R @ (p["pos"] - o)), (tag, key, pname)
                    assert np.allclose(q["dir"], R @ p["dir"]) and q["dia_m"] == p["dia_m"]
                    if pname != "discharge" or p["dia_m"] > 0:
                        assert min(np.linalg.norm(f - q["pos"]) for f in faces) < 1e-9
            for key, pt in pump_points_from_layout(rl).items():
                assert np.allclose(pt, o + R @ (pts[key] - o)), (tag, key)
        # roll / flip / radial preset / head mount (2026-10-01): every casing box clears
        # (side: the local envelope; head: forward of the injector head), ports stay on
        # their flange faces with unit dirs, and carry the engine-aligned placement frame
        base = build_layout(sz, dis, exh)
        for orient, roll, flip, mount in (("axial", 30.0, False, "side"),
                                          ("radial", 0.0, True, "side"),
                                          ("tangential", 215.0, True, "side"),
                                          ("axial", 0.0, False, "head"),
                                          ("radial", 90.0, False, "head"),
                                          ("axial", 45.0, True, "head")):
            pl_kw = dict(azimuth_deg=120.0, shaft_orientation=orient, roll_deg=roll, flip=flip,
                         mount=mount, head_offset_m=0.1)
            ml = place_layout(base, r["profile_xs_m"], r["profile_rs_m"], **pl_kw)
            assert ml["placement"]["mount"] == mount
            for kind, clr in geometry3d.placement_clearances(
                    layout_boxes(ml), ml["placement"], r["profile_xs_m"], r["profile_rs_m"]):
                assert clr > 0.0, (tag, orient, roll, flip, mount, kind, clr)
            mp = ports_from_layout(ml)
            for key, group in mp.items():
                faces = [to_world(ml, key, f["face"]) for f in ml["components"][key]["flanges"]]
                for pname, q in group.items():
                    assert np.isclose(np.linalg.norm(q["dir"]), 1.0)
                    assert np.array_equal(q["frame"], geometry3d.placement_frame_rows(120.0))
                    if pname != "discharge" or q["dia_m"] > 0:
                        assert min(np.linalg.norm(f - q["pos"]) for f in faces) < 1e-9, \
                            (tag, orient, roll, mount, key, pname)
        assert ports_from_layout(dict(lay, rotation=np.eye(3)))["fuel_pump"]["inlet"]["pos"] \
            .tobytes() == cp["fuel_pump"]["inlet"]["pos"].tobytes()
    # casings mode end to end: design.py takes its ports from the placed layout and every
    # pump-connected run closes onto its casing flange
    import dataclasses
    from . import manifold, plumbing

    def hooks_of(res):
        return {"manifold_result": res["manifold_result"],
                "jacket_manifold_result": res["jacket_manifold_result"],
                "turbine_exhaust_hardware": res["turbine_exhaust_hardware"]}

    for name in ("F-1", "J-2"):
        d = corpus(name, turbopump_geometry_model="casings")
        r = d.compute()
        lay = r["turbopump_layout"]
        assert lay and lay["placement"]["axis_radius_m"] > float(np.max(r["profile_rs_m"][:5])), name
        assert r["turbopump_placement"]["origin_xyz"] == lay["origin_xyz"], name
        again = ports_from_layout(lay)
        for key, group in r["turbopump_ports"].items():
            for pname, p in group.items():
                assert np.allclose(p["pos"], again[key][pname]["pos"]), (name, key, pname)
        # "Route to pump" runs (the Shape Lab's seed) onto both pumps' casing discharges
        runs = []
        for host in ("jacket_inlet", "ox"):
            hk = plumbing.hook_for_host(hooks_of(r), host)
            port = plumbing.port_for_host(r["turbopump_ports"], host)
            runs.append(plumbing.run_to_dict(plumbing.seed_route_to_port(
                hk, port, hk["major_radius_m"], manifold.ring_outer_radius_at(hk, 0.0), host)))
        r = dataclasses.replace(d, plumbing_runs=runs).compute()
        for rd in runs:
            run = plumbing.run_from_dict(rd)
            hook = plumbing.hook_for_host(hooks_of(r), run.host)
            port = plumbing.port_for_host(r["turbopump_ports"], run.host)
            res = plumbing.resolve_run(run, hook, hook["major_radius_m"],
                                       manifold.ring_outer_radius_at(hook, run.attach_angle_deg),
                                       port=port)
            assert np.allclose(res["waypoints_xyz"][-1], port["pos"], atol=1e-9), (name, run.host)
        assert all(v is not None for v in r["line_loss_computed"].values()), (name, r["line_loss_computed"])
    assert build_layout(None) is None and place_layout(None, 1.0, 1.0) is None
    assert build_layout(EngineDesign(cycle="pressure_fed").compute().get("turbopump_sizing")) is None
    print("turbopump_layout self-test: OK (volute sections, scroll exits, 7 corpus layouts: "
          "ports on flange faces facing the engine, same port set/bores as the ghost, "
          "tightened spans, dual-shaft clearance; casings-mode F-1/J-2: design ports = layout "
          "ports, pump-connected runs land on the casing flanges; pressure-fed None)")


if __name__ == "__main__":
    self_test()
