"""
The "Turbopump 3D" tab's scene (turbopump roadmap E2a/E2b, 2026-09-27): the whole
turbopump assembly's CASINGS drawn at TRUE meanline scale from what the physics designed -
each pump's inlet neck + flange, impeller shroud housing (the meanline's meridional
shroud), multistage crossover barrel, and spiral volute (the meanline's constant-mean-
velocity spiral from the tongue) with a tangential discharge diffuser; an axial pump's
barrel + collector; each turbine's rotor housing, inlet manifold torus with a GG/preburner
inlet stub, and exhaust scroll; an electric pump-fed engine's motor; and the bearing/seal
housings between them.

The geometry is physics/turbopump_layout.py's (the ONE source - with EngineDesign.
turbopump_geometry_model "casings" the main 3D preview draws the same layout and the
ports/plumbing sit on it); this module only meshes it (preview3d_gl_core.layout_pieces),
tags each piece with its component and frames the camera on the isolate choice. The tab
shows the casings whatever that setting is, at the layout's local origin.

Internals (bladed impellers, inducer helix, turbine blades) are a later round; the turbine
has no meanline yet (Round 3), so its housing comes from turbopump_sizing's envelope
factors.

Pure numpy - no Tk/OpenGL import - self-tested by `python3 -m engine_designer.gui.turbopump_scene`.
"""
import numpy as np

from ..physics import turbopump_layout, turbopump_materials
from . import mesh_builder
from .preview3d_gl_core.turbopump_meshes import layout_pieces

SCENE_PADDING_FRACTION = 0.08
FLANGE_RGB = mesh_builder.PLUMBING_FLANGE_RGB
ISOLATE_LABELS = {"assembly": "Assembly", "fuel_pump": "Fuel pump", "ox_pump": "Ox pump",
                  "turbine": "Turbine", "ox_turbine": "Ox turbine", "motor": "Motor"}


def _port_dia(ports, *path):
    node = ports or {}
    for key in path:
        node = node.get(key) if isinstance(node, dict) else None
        if node is None:
            return 0.0
    return float(node)


def layout_for_result(result):
    """The result's turbopump layout at the LOCAL origin: the one design.py placed
    (turbopump_geometry_model "casings"), else built here from the sizing and the same
    port bores - identical geometry either way. None without a turbopump."""
    placed = result.get("turbopump_layout")
    if placed:
        return dict(placed, origin_xyz=(0.0, 0.0, 0.0))
    ports = result.get("turbopump_ports")
    return turbopump_layout.build_layout(
        result.get("turbopump_sizing"),
        {k: _port_dia(ports, k, "discharge", "dia_m") for k in turbopump_layout.PUMP_KEYS},
        _port_dia(ports, "turbine", "exhaust", "dia_m"))


def main_view_uses_casings(result):
    return bool(result.get("turbopump_layout"))


def build_turbopump_scene(result, isolate="assembly"):
    """
    {"pieces", "center", "half", "components": [(key, label), ...], "summary": [str]}
    for the Turbopump 3D tab. `isolate` = "assembly" or a component key from
    "components"; the camera framing (center/half) follows what is kept.
    """
    layout = layout_for_result(result)
    if layout is None:
        return {"pieces": [], "center": (0.0, 0.0, 0.0), "half": 0.5,
                "components": [("assembly", ISOLATE_LABELS["assembly"])],
                "summary": ["No turbopump on this design (pressure-fed or no sizing)."]}
    tp_mat = turbopump_materials.MATERIALS[result["inputs"]["turbopump_material_key"]]
    pump_rgb = mesh_builder._hex_to_rgb01(tp_mat.color_hex)
    turb_rgb = mesh_builder._darken_rgb01(pump_rgb)
    dual = len(layout["units"]) > 1

    def label(key):
        return "Fuel turbine" if key == "turbine" and dual else ISOLATE_LABELS[key]

    pieces = []
    for key, pcs in layout_pieces(layout, pump_rgb, turb_rgb, FLANGE_RGB):
        pieces += _tag(pcs, key, tp_mat)
    order = [k for unit in layout["units"] for k in unit]
    summary = [f"{label(k)}: {layout['components'][k]['summary']}" for k in order]
    if layout["arrangement"] == "geared":
        summary.append("Geared: drawn inline on one shaft - the gearbox and the ox pump's "
                       "parallel shaft aren't modelled yet.")
    if main_view_uses_casings(result):
        summary.append("True meanline scale - the main 3D Preview draws these casings too, and "
                       "the pump/turbine ports and plumbing sit on their flanges "
                       "(Turbopump 3D geometry = casings).")
    else:
        summary.append("True meanline scale. The main 3D Preview draws the ghost envelope "
                       "(sized to the specific-power mass) - set Turbopump 3D geometry to "
                       "'casings' to use these there (moves the ports and plumbing).")

    components = [("assembly", ISOLATE_LABELS["assembly"])] + [(k, label(k)) for k in order]
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
                             else ml["d_tip_m"] * (1.0 + 2.4 * turbopump_layout.COLLECTOR_SECTION_TIP_MULT))
                pcs = [p for p in iso["pieces"] if p.meta["tp_component"] == key]
                dz = float(np.mean(np.concatenate([p.vertices[:, 2] for p in pcs])))
                rad = max(float(np.max(np.hypot(p.vertices[:, 1], p.vertices[:, 2] - dz)))
                          for p in pcs)
                assert 0.8 * ref <= rad, (tag, key, rad, ref)
        # every gap along a shaft is filled by a bearing/seal housing (no bare shaft)
        lay = layout_for_result(r)
        for unit in lay["units"]:
            spans = sorted((lay["placements"][k]["x_start"], lay["placements"][k]["x_end"])
                           for k in unit)
            for (_, a_end), (b_start, _) in zip(spans, spans[1:]):
                assert any(abs(k["x0"] - a_end) < 1e-12 and abs(k["x1"] - b_start) < 1e-12
                           for k in lay["links"]), (tag, a_end, b_start)
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
        assert "ghost envelope" in sc["summary"][-1], tag      # default: envelope main view

    # discharge cone exit bore == the pump's true discharge port bore (F-1 fuel pump)
    r = corpus("F-1").compute()
    dis = r["turbopump_ports"]["fuel_pump"]["discharge"]["dia_m"]
    assert "discharge %.0f mm" % (dis * 1e3) in build_turbopump_scene(r)["summary"][0]

    # pressure-fed: an empty scene with a message, no crash
    empty = build_turbopump_scene(EngineDesign(cycle="pressure_fed").compute())
    assert not empty["pieces"] and "No turbopump" in empty["summary"][0]
    print("turbopump_scene self-test: OK (9 corpus cases, isolate framing, true scale, "
          "every shaft gap housed, dual-shaft split, electric motor, correlation fallback, "
          "main preview untouched)")


if __name__ == "__main__":
    self_test()
