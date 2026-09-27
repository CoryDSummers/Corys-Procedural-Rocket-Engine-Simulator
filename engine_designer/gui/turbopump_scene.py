"""
The "Turbopump 3D" tab's scene (turbopump roadmap E2a, 2026-09-27): the whole turbopump
assembly's CASINGS drawn at TRUE meanline scale from what the physics designed - each
pump's inlet neck + flange, impeller shroud housing (the meanline's meridional shroud),
multistage crossover barrel, and spiral volute (the meanline's constant-mean-velocity
spiral from the tongue) with a tangential discharge diffuser; an axial pump's barrel +
collector; each turbine's rotor housing, inlet manifold torus with a GG/preburner inlet
stub, and exhaust scroll; an electric pump-fed engine's motor.

A SEPARATE view on purpose (Cory's call): the main 3D preview still draws the ghost
envelope (turbopump_sizing._assemble_bodies x render_scale) and its ports, which feed
physics (pump-connected plumbing line loss, turbine-exhaust duct). Nothing here is read
back by physics, so this module can't move a result.

Internals (bladed impellers, inducer helix, turbine blades) are a later round; the turbine
has no meanline yet (Round 3), so its housing comes from turbopump_sizing's envelope
factors. Every sizing constant below is RENDER-ONLY (ASSUMPTIONS.md, arbitrary tier).

Pure numpy - no Tk/OpenGL import - self-tested by `python3 -m engine_designer.gui.turbopump_scene`.
"""
import math

import numpy as np

from ..physics import geometry3d, turbopump_materials, turbopump_sizing
from . import mesh_builder
from .preview3d_gl_core.duct_meshes import frustum_mesh, pipe_flange_pieces
from .preview3d_gl_core.mesh_primitives import manifold_ring_mesh
from .preview3d_gl_core.turbopump_meshes import (VOLUTE_STATIONS, place_pieces,
                                                 revolve_polyline_pieces, volute_scroll_pieces,
                                                 volute_sections)

# --- render-only casing proportions (no physics meaning) ----------------------------------
N_THETA = 48                        # revolve resolution
N_TUBE = 24                         # scroll / torus cross-section resolution
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
INLET_TORUS_SPLIT = 0.25            # inlet torus section radius / (manifold OD - disk OD)
INLET_TORUS_MIN_DISK = 0.06         # ... floored at this x disk OD
GG_INLET_TUBE_MULT = 0.7            # GG/preburner inlet stub radius / inlet torus section radius
GG_INLET_LEN_TUBE_MULT = 1.5        # stub length beyond the torus / its section radius
EXHAUST_SCROLL_EXIT_FRAC = 0.85     # exhaust scroll end-section radius / exhaust bore radius
EXHAUST_CONE_MIN_LEN_DIA = 0.5      # exhaust outlet cone minimum length / exhaust bore
EXHAUST_SCROLL_FLOOR_FRAC = 0.3     # its start-section radius / its end-section radius
CLOSED_CYCLE_OUTLET_DISK_MULT = 0.45  # turbine outlet bore when no exhaust port (staged/
                                      # expander: gas goes on to the injector), x disk OD
SCENE_PADDING_FRACTION = 0.08

FLANGE_RGB = mesh_builder.PLUMBING_FLANGE_RGB
ISOLATE_LABELS = {"assembly": "Assembly", "fuel_pump": "Fuel pump", "ox_pump": "Ox pump",
                  "turbine": "Turbine", "ox_turbine": "Ox turbine", "motor": "Motor"}


def _flange(center, tangent, bore_r, rgb):
    t = np.asarray(tangent, dtype=float)
    n = np.array([0.0, 1.0, 0.0]) if abs(t[1]) < 0.9 else np.array([1.0, 0.0, 0.0])
    n = n - np.dot(n, t) * t
    n /= np.linalg.norm(n)
    return pipe_flange_pieces(center, t, n, np.cross(t, n), bore_r, FLANGE_LIP_BORE_MULT * bore_r,
                              FLANGE_WIDTH_BORE_MULT * bore_r, FLANGE_BOLTS, N_TUBE, rgb)


def _component(pieces, length_m, r_link_m, od_m, summary):
    """`od_m` = the casing's own OD (volute / torus / barrel, NOT the discharge cones) -
    what the shaft spans and the dual-shaft unit gap are sized on."""
    return {"pieces": pieces, "length_m": float(length_m), "r_link_m": float(r_link_m),
            "od_m": float(od_m), "summary": summary}


def centrifugal_pump_casing(pump, discharge_dia_m, rgb, handed=1):
    """One centrifugal pump in its LOCAL frame: inlet flange face at x = 0 (flow enters
    along +x), casing walked inlet -> back so the housing's outside is the polyline's left.
    """
    ml = pump["meanline"]
    st, mer, vol = ml["stage"], ml["meridional"], ml["volute"]
    d2, b2, n = st["d2_m"], st["b2_m"], ml["n_stages"]
    r2 = 0.5 * d2
    c = HOUSING_CLEARANCE_D2 * d2
    dt = pump.get("inlet_eye_dia_m") or st["d1_m"]
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
    pieces = revolve_polyline_pieces(xs, rs, N_THETA, rgb)
    pieces += _flange(np.array([0.5 * FLANGE_WIDTH_BORE_MULT * r_in, 0.0, 0.0]),
                      (-1.0, 0.0, 0.0), r_in, FLANGE_RGB)

    wrap, ctr, tube = volute_sections(vol["spiral"], vol["r_tongue_m"], 0.5 * b2 + c)
    scroll, exit_ = volute_scroll_pieces(x_tip + 0.5 * b2, ctr, tube, wrap, discharge_dia_m,
                                         N_TUBE, rgb, handed=handed)
    pieces += scroll
    pieces += _flange(exit_["pos"] - 0.5 * FLANGE_WIDTH_BORE_MULT * 0.5 * exit_["dia_m"]
                      * exit_["dir"], exit_["dir"], 0.5 * exit_["dia_m"], FLANGE_RGB)
    diff = vol.get("diffuser")
    summary = (f"centrifugal, {n} stage{'s' if n > 1 else ''}, D2 {d2 * 1e3:.0f} mm, "
               f"b2 {b2 * 1e3:.1f} mm, inlet {dt * 1e3:.0f} mm, volute OD "
               f"{vol['od_m'] * 1e3:.0f} mm ({'vaned diffuser, ' + str(diff['zd']) + ' vanes' if diff else 'vaneless'}), "
               f"discharge {exit_['dia_m'] * 1e3:.0f} mm")
    return _component(pieces, x_end, r_bh, 2.0 * float(np.max(ctr + tube)), summary)


def axial_pump_casing(pump, discharge_dia_m, rgb, handed=1):
    """An axial pump (inducer + inlet guide row + n rotor/stator rows, the Detail tab's
    row lengths) in a barrel, discharging through a constant-section collector (the
    meanline designs no volute for an axial pump - the Detail tab's 0.35 x r_tip section)."""
    ml = pump["meanline"]
    dt, chord, n = ml["d_tip_m"], ml["chord_m"], ml["n_stages"]
    rt = 0.5 * dt
    c = HOUSING_CLEARANCE_D2 * dt
    gap = AXIAL_GAP_CHORD * chord
    eye = pump.get("inlet_eye_dia_m") or dt
    r_b = max(rt, 0.5 * eye) + c
    rows = (INDUCER_LEN_TIP_MULT * dt + gap + AXIAL_IGV_CHORD * chord + gap
            + n * (2.0 * AXIAL_ROW_CHORD * chord + 2.0 * gap))
    r_sec = COLLECTOR_SECTION_TIP_MULT * rt
    x_c = INLET_LEAD_D2 * dt + rows + r_sec
    x_back = x_c + r_sec
    r_bh = min(BEARING_HOUSING_SHAFT_MULT * 0.6 * 0.5 * ml["d_hub_m"], 0.8 * r_b)
    x_end = x_back + BEARING_HOUSING_LEN_D2 * dt
    xs = [0.0, x_back, x_back, x_end, x_end]
    rs = [r_b, r_b, r_bh, r_bh, 0.0]
    pieces = revolve_polyline_pieces(xs, rs, N_THETA, rgb)
    pieces += _flange(np.array([0.5 * FLANGE_WIDTH_BORE_MULT * r_b, 0.0, 0.0]),
                      (-1.0, 0.0, 0.0), r_b, FLANGE_RGB)
    ctr = np.full(VOLUTE_STATIONS, r_b + 0.2 * r_sec)
    tube = np.full(VOLUTE_STATIONS, r_sec)
    scroll, exit_ = volute_scroll_pieces(x_c, ctr, tube, 2.0 * math.pi, discharge_dia_m,
                                         N_TUBE, rgb, handed=handed)
    pieces += scroll
    pieces += _flange(exit_["pos"] - 0.5 * FLANGE_WIDTH_BORE_MULT * 0.5 * exit_["dia_m"]
                      * exit_["dir"], exit_["dir"], 0.5 * exit_["dia_m"], FLANGE_RGB)
    summary = (f"axial, inducer + {n} stages, tip {dt * 1e3:.0f} mm, hub/tip "
               f"{ml['hub_tip']:.2f}, discharge {exit_['dia_m'] * 1e3:.0f} mm")
    return _component(pieces, x_end, r_bh, 2.0 * (r_b + 1.2 * r_sec), summary)


def _cylinder(od_m, length_m, rgb):
    r = 0.5 * od_m
    return revolve_polyline_pieces([0.0, 0.0, length_m, length_m], [0.0, r, r, 0.0],
                                   N_THETA, rgb)


def envelope_pump_casing(pump, rgb):
    """Fallback for a pump with no meanline (pump_model "correlation"): its true-scale
    envelope cylinder (volute OD x body length), before the ghost's render_scale."""
    return _component(_cylinder(pump["volute_od_m"], pump["body_length_m"], rgb),
                      pump["body_length_m"], 0.2 * pump["volute_od_m"], pump["volute_od_m"],
                      f"envelope only (pump model 'correlation' - no meanline geometry), "
                      f"OD {pump['volute_od_m'] * 1e3:.0f} mm")


def turbine_casing(tb, exhaust_dia_m, rgb, handed=1):
    """A turbine in its LOCAL frame, x = 0 on its pump side: rotor housing round the disk,
    an inlet manifold torus with a radial GG/preburner inlet stub, and an exhaust scroll
    discharging tangentially to `exhaust_dia_m` (the turbine exhaust port's true bore, or a
    closed-cycle outlet default). Sizes are turbopump_sizing's envelope factors - no
    turbine meanline until Round 3."""
    dod = tb["disk_od_m"]
    r_h = 0.5 * dod + TURBINE_CLEARANCE_DISK * dod
    tube_in = max(INLET_TORUS_SPLIT * (tb["manifold_od_m"] - dod), INLET_TORUS_MIN_DISK * dod)
    ctr_in = max(0.5 * tb["manifold_od_m"] - tube_in, r_h)
    closed = exhaust_dia_m <= 0.0
    exh = CLOSED_CYCLE_OUTLET_DISK_MULT * dod if closed else exhaust_dia_m
    rs_end = EXHAUST_SCROLL_EXIT_FRAC * 0.5 * exh
    length = max(tb["disk_thickness_m"] + tb["manifold_length_m"],
                 2.0 * tube_in + 2.0 * rs_end + tb["disk_thickness_m"])
    pieces = _cylinder(2.0 * r_h, length, rgb)
    x_in = tube_in
    pieces.append(manifold_ring_mesh(x_in, ctr_in, tube_in, N_THETA, N_TUBE, rgb))
    stub_r = GG_INLET_TUBE_MULT * tube_in
    stub_end = np.array([x_in, ctr_in + tube_in + GG_INLET_LEN_TUBE_MULT * tube_in, 0.0])
    pieces += frustum_mesh(np.array([x_in, ctr_in, 0.0]), stub_end, stub_r, stub_r, N_TUBE, rgb)
    pieces += _flange(stub_end - np.array([0.0, 0.5 * FLANGE_WIDTH_BORE_MULT * stub_r, 0.0]),
                      (0.0, 1.0, 0.0), stub_r, FLANGE_RGB)
    tube = np.linspace(EXHAUST_SCROLL_FLOOR_FRAC * rs_end, rs_end, VOLUTE_STATIONS)
    scroll, exit_ = volute_scroll_pieces(length - rs_end, r_h + tube, tube, 2.0 * math.pi, exh,
                                         N_TUBE, rgb, u_start_rad=math.pi, handed=handed,
                                         min_len_dia_mult=EXHAUST_CONE_MIN_LEN_DIA)
    pieces += scroll
    pieces += _flange(exit_["pos"] - 0.5 * FLANGE_WIDTH_BORE_MULT * 0.5 * exh * exit_["dir"],
                      exit_["dir"], 0.5 * exh, FLANGE_RGB)
    summary = (f"{tb['staging'].replace('_', ' ')}, pitchline {tb['d_mean_m'] * 1e3:.0f} mm, "
               f"disk OD {dod * 1e3:.0f} mm, inlet torus OD {2 * (ctr_in + tube_in) * 1e3:.0f} mm, "
               + (f"outlet {exh * 1e3:.0f} mm (closed cycle - default bore)" if closed
                  else f"exhaust {exh * 1e3:.0f} mm"))
    return _component(pieces, length, 0.25 * dod,
                      2.0 * max(ctr_in + tube_in, r_h + 2.0 * rs_end), summary)


def _units(sizing):
    """[[component key, ...] per shaft unit], in drawing order along +x."""
    if sizing.get("arrangement") == "dual_shaft" and sizing.get("ox_turbine"):
        return [["fuel_pump", "turbine"], ["ox_pump", "ox_turbine"]]
    middle = []
    if sizing.get("turbine"):
        middle = ["turbine"]
    elif any(b["kind"] == "motor" for b in sizing.get("bodies", [])):
        middle = ["motor"]
    return [["fuel_pump"] + middle + ["ox_pump"]]


def _port_dia(ports, *path):
    node = ports or {}
    for key in path:
        node = node.get(key) if isinstance(node, dict) else None
        if node is None:
            return 0.0
    return float(node)


def build_turbopump_scene(result, isolate="assembly"):
    """
    {"pieces", "center", "half", "components": [(key, label), ...], "summary": [str]}
    for the Turbopump 3D tab. `isolate` = "assembly" or a component key from
    "components"; the camera framing (center/half) follows what is kept.
    """
    sizing = result.get("turbopump_sizing")
    if not sizing:
        return {"pieces": [], "center": (0.0, 0.0, 0.0), "half": 0.5,
                "components": [("assembly", ISOLATE_LABELS["assembly"])],
                "summary": ["No turbopump on this design (pressure-fed or no sizing)."]}
    tp_mat = turbopump_materials.MATERIALS[result["inputs"]["turbopump_material_key"]]
    pump_rgb = mesh_builder._hex_to_rgb01(tp_mat.color_hex)
    turb_rgb = mesh_builder._darken_rgb01(pump_rgb)
    ports = result.get("turbopump_ports")
    exhaust_dia = _port_dia(ports, "turbine", "exhaust", "dia_m")
    units = _units(sizing)
    dual = len(units) > 1

    built, summary = {}, []
    for u_idx, unit in enumerate(units):
        handed = (-1 if u_idx == 0 else 1) if dual else 1
        for key in unit:
            if key in ("fuel_pump", "ox_pump"):
                pump = sizing[key]
                ml = pump.get("meanline")
                dis = _port_dia(ports, key, "discharge", "dia_m")
                h = handed if dual else (1 if key == "fuel_pump" else -1)
                if ml is None:
                    comp = envelope_pump_casing(pump, pump_rgb)
                elif ml["type"] == "axial":
                    comp = axial_pump_casing(pump, dis, pump_rgb, handed=h)
                else:
                    comp = centrifugal_pump_casing(pump, dis, pump_rgb, handed=h)
            elif key in ("turbine", "ox_turbine"):
                comp = turbine_casing(sizing[key], exhaust_dia, turb_rgb, handed=handed)
            else:
                motor = next(b for b in sizing["bodies"] if b["kind"] == "motor")
                comp = _component(_cylinder(motor["od_m"], motor["length_m"], turb_rgb),
                                  motor["length_m"], 0.2 * motor["od_m"], motor["od_m"],
                                  f"electric motor + controller (mass-sized cylinder), OD "
                                  f"{motor['od_m'] * 1e3:.0f} mm")
            built[key] = comp
            label = ISOLATE_LABELS[key]
            if key == "turbine" and dual:
                label = "Fuel turbine"
            summary.append(f"{label}: {comp['summary']}")

    unit_gap = (geometry3d.TURBOPUMP_UNIT_GAP_OD_MULT
                * max(c["od_m"] for c in built.values())) if dual else 0.0
    pieces = []
    for u_idx, unit in enumerate(units):
        dz = (u_idx - (len(units) - 1) / 2.0) * unit_gap
        span = turbopump_sizing.SHAFT_SPAN_FACTOR * max(built[k]["od_m"] for k in unit)
        x = 0.0
        for i, key in enumerate(unit):
            comp = built[key]
            if i > 0:
                r_link = min(comp["r_link_m"], built[unit[i - 1]]["r_link_m"])
                link = revolve_polyline_pieces([x, x + span], [r_link, r_link], N_THETA, pump_rgb)
                pieces += _tag(place_pieces(link, dz_m=dz), "shaft", tp_mat)
                x += span
            # a pump after the first component of its unit faces its inlet outboard (+x)
            sx = -1.0 if (key.endswith("_pump") and i > 0) else 1.0
            x0 = x + comp["length_m"] if sx < 0 else x
            pieces += _tag(place_pieces(comp["pieces"], x0_m=x0, sx=sx, dz_m=dz), key, tp_mat)
            x += comp["length_m"]

    arr = sizing.get("arrangement", "")
    if arr == "geared":
        summary.append("Geared: drawn inline on one shaft - the gearbox and the ox pump's "
                       "parallel shaft aren't modelled yet.")
    summary.append("True meanline scale. The main 3D Preview still draws the ghost envelope "
                   "(sized to the specific-power mass) - this view isn't applied there yet.")

    components = [("assembly", ISOLATE_LABELS["assembly"])]
    for unit in units:
        for key in unit:
            components.append((key, "Fuel turbine" if key == "turbine" and dual
                               else ISOLATE_LABELS[key]))
    keep = pieces if isolate == "assembly" else [
        p for p in pieces if p.meta.get("tp_component") == isolate]
    if not keep:
        keep = pieces
    center, half = _bounds(keep)
    return {"pieces": keep, "center": center, "half": half, "components": components,
            "summary": summary}


def _tag(pieces, component, mat):
    pieces = mesh_builder._stamp_material(pieces, mat)
    for p in pieces:
        p.role = "turbopump"
        p.meta = {**(p.meta or {}), "tp_component": component}
    return pieces


def _bounds(pieces):
    if not pieces:
        return (0.0, 0.0, 0.0), 0.5
    v = np.concatenate([p.vertices for p in pieces]).astype(float)
    lo, hi = v.min(axis=0), v.max(axis=0)
    center = 0.5 * (lo + hi)
    half = float(np.max(hi - lo) / 2.0) * (1.0 + SCENE_PADDING_FRACTION)
    return tuple(float(c) for c in center), max(half, 1e-3)


def self_test():
    import copy
    import json
    import os
    from ..physics.design import EngineDesign

    here = os.path.join(os.path.dirname(__file__), "..", "validation_engines", "engines")

    def corpus(name, **over):
        with open(os.path.join(here, f"{name}.json")) as f:
            d = json.load(f)["design"]
        d.update(over)
        return EngineDesign.from_dict({"schema_version": EngineDesign.SCHEMA_VERSION, "design": d})

    def mesh_digest(result):
        pcs = mesh_builder.build_mesh_data(result, False)
        return [(p.role, p.vertices.shape, float(np.sum(p.vertices))) for p in pcs]

    cases = [("F-1", {}), ("J-2", {}), ("RS-25", {}), ("RL10A-3-3", {}), ("Rutherford", {}),
             ("RD-180", {}), ("Merlin-1D", {}), ("Raptor-2", {}),
             ("F-1", {"pump_model": "correlation"})]
    for name, over in cases:
        r = corpus(name, **over).compute()
        sizing_before = copy.deepcopy(r["turbopump_sizing"]["bodies"])
        digest_before = mesh_digest(r) if name == "F-1" and not over else None
        sc = build_turbopump_scene(r)
        tag = f"{name}{' ' + str(over) if over else ''}"
        assert sc["pieces"], tag
        for p in sc["pieces"]:
            assert np.all(np.isfinite(p.vertices)) and np.all(np.isfinite(p.normals)), tag
            assert p.role == "turbopump" and p.meta["tp_component"], tag
        keys = [k for k, _ in sc["components"]]
        assert keys[0] == "assembly" and "fuel_pump" in keys and "ox_pump" in keys, (tag, keys)
        for key in keys[1:]:
            iso = build_turbopump_scene(r, isolate=key)
            assert iso["pieces"] and all(p.meta["tp_component"] == key for p in iso["pieces"])
            v = np.concatenate([p.vertices for p in iso["pieces"]])
            assert np.all(np.abs(v - np.array(iso["center"])) <= iso["half"] + 1e-6), (tag, key)
            assert iso["half"] <= sc["half"] + 1e-9
            if key.endswith("_pump") and not over:
                ml = r["turbopump_sizing"][key]["meanline"]
                # true scale: the casing's radial extent tracks the meanline's own size
                ref = 0.5 * (ml["volute"]["od_m"] if ml["type"] == "centrifugal"
                             else ml["d_tip_m"] * (1.0 + 2.4 * COLLECTOR_SECTION_TIP_MULT))
                pcs = [p for p in iso["pieces"] if p.meta["tp_component"] == key]
                dz = float(np.mean(np.concatenate([p.vertices[:, 2] for p in pcs])))
                rad = max(float(np.max(np.hypot(p.vertices[:, 1], p.vertices[:, 2] - dz)))
                          for p in pcs)
                assert 0.8 * ref <= rad, (tag, key, rad, ref)
        # the scene never mutates the result the main preview draws from
        assert r["turbopump_sizing"]["bodies"] == sizing_before, tag
        if digest_before is not None:
            assert mesh_digest(r) == digest_before, "main 3D preview output changed"
        if name == "J-2":
            assert "ox_turbine" in keys
            fz = np.mean(np.concatenate([p.vertices[:, 2] for p in sc["pieces"]
                                         if p.meta["tp_component"] == "fuel_pump"]))
            oz = np.mean(np.concatenate([p.vertices[:, 2] for p in sc["pieces"]
                                         if p.meta["tp_component"] == "ox_pump"]))
            assert oz - fz > 0.3, (fz, oz)      # two separated shaft units
            assert "axial" in sc["summary"][0]
        if name == "Rutherford":
            assert "motor" in keys and "turbine" not in keys
        if over:
            assert "envelope only" in " ".join(sc["summary"])

    # discharge cone exit bore == the pump's true discharge port bore (F-1 fuel pump)
    r = corpus("F-1").compute()
    pump = r["turbopump_sizing"]["fuel_pump"]
    dis = r["turbopump_ports"]["fuel_pump"]["discharge"]["dia_m"]
    comp = centrifugal_pump_casing(pump, dis, (0.6, 0.6, 0.6))
    assert "discharge %.0f mm" % (dis * 1e3) in comp["summary"]

    # pressure-fed: an empty scene with a message, no crash
    empty = build_turbopump_scene(EngineDesign(cycle="pressure_fed").compute())
    assert not empty["pieces"] and "No turbopump" in empty["summary"][0]
    print("turbopump_scene self-test: OK (9 corpus cases, isolate framing, true scale, "
          "dual-shaft split, electric motor, correlation fallback, main preview untouched)")


if __name__ == "__main__":
    self_test()
