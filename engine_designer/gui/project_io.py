"""
Save / load an EngineDesign as a JSON project file. Pure - no Tkinter - so it
has a headless self-check. The GUI (gui/app.py) wraps these with file dialogs
and the widget refresh.

Format: `{"schema_version": N, "design": {<every EngineDesign field>}}` (see
EngineDesign.to_dict / from_dict). Unknown keys are dropped and missing keys
take their default, so a file from an older or newer tool version still loads.
"""
import json
from pathlib import Path

from ..physics import plumbing
from ..physics.design import EngineDesign

FILE_SUFFIX = ".json"


def save_design(path, design):
    """Write `design` to `path` as a project JSON file."""
    Path(path).write_text(json.dumps(design.to_dict(), indent=2))


def load_design(path):
    """Read a project JSON file and return an EngineDesign."""
    return EngineDesign.from_dict(json.loads(Path(path).read_text()))


def file_schema_version(path):
    """Schema version stamped in a project file (1 if absent / unreadable)."""
    try:
        return int(json.loads(Path(path).read_text()).get("schema_version", 1))
    except Exception:
        return 1


if __name__ == "__main__":
    import tempfile

    # Round-trip: a default design and a heavily-customised one both come back
    # bit-for-bit equal.
    for d in (EngineDesign(),
              EngineDesign(propellant_pair="LOX/CH4", cycle="ffsc",
                           chamber_pressure_pa=30e6, mixture_ratio=3.55,
                           regen_channel_model="channels", regen_channel_count=180,
                           chamber_sizing_method="residence_time",
                           chamber_residence_time_ms=1.6,
                           chamber_wall_fillet_r_over_rt=1.2,
                           chamber_cooling_method="uncooled", nozzle_cooling_method="radiative",
                           film_cooling_fraction=0.06, chamber_film_inject_area_ratio=1.8,
                           nozzle_film_fraction=0.03, nozzle_film_inject_eps=12.0,
                           turbine_exhaust_mode="aspirator", turbine_exhaust_nozzle_eps=3.0,
                           turbine_exhaust_cant_deg=12.0, turbine_exhaust_inject_eps=9.0,
                           aspirator_fwd_length_frac=0.4, aspirator_overhang_frac=0.08,
                           turbine_exhaust_hx_gox_kgs=0.4,
                           wall_construction="tube_wall", regen_nozzle_end_eps=25.0,
                           regen_circuit_style="f1_double_pass",
                           dump_coolant_fraction=0.08,
                           injector_type="coax_post", material_key="grcop_84",
                           gimbal_mode="custom", gimbal_range_deg=8.0,
                           tech_node="FRSC1976", cost=140.0, entry_cost=90000.0,
                           ignitions=50,
                           output_mode="new_part_standalone",
                           config_name="Methalox-2M", host_model_reference_height_m=3.4,
                           new_part_name="Methalox-2M", new_part_title="Methalox 2M",
                           new_part_manufacturer="ACME", new_part_description="test",
                           plumbing_runs=[plumbing.run_to_dict(plumbing.PlumbingRun(
                               attach_angle_deg=30.0, flange_at_root=True,
                               pipes=[plumbing.PipeSegment(length_dia_mult=2.0),
                                      plumbing.PipeSegment(pitch_deg=60.0, flange_at_end=True),
                                      plumbing.PipeSegment(yaw_deg=-45.0, bend_radius_dia_mult=2.0)]))])):
        with tempfile.NamedTemporaryFile(suffix=FILE_SUFFIX, delete=False, mode="w") as fh:
            p = fh.name
        save_design(p, d)
        assert load_design(p) == d, d
        Path(p).unlink()

    # from_dict tolerance: newer schema + unknown field, and a bare field dict.
    assert EngineDesign.from_dict(
        {"schema_version": 99, "design": {"cycle": "orsc", "not_a_real_field": 7}}
    ).cycle == "orsc"
    assert EngineDesign.from_dict({"propellant_pair": "LOX/LH2"}).propellant_pair == "LOX/LH2"
    # A schema-3 file carrying the removed Shape Lab dummy fields still loads
    # (they're dropped), and a nested plumbing run survives the JSON round trip
    # as plain dicts that plumbing.run_from_dict rebuilds.
    old_v3 = EngineDesign.from_dict({"schema_version": 3, "design": {
        "manifold_intake_angle_deg": 45.0, "manifold_rotation_deg": 10.0, "cycle": "orsc"}})
    assert old_v3.cycle == "orsc" and old_v3.plumbing_runs == []
    # A schema-4 file's removed manifold_feed_velocity_ms baseline is dropped;
    # the velocity-head fraction takes its default.
    old_v4 = EngineDesign.from_dict({"schema_version": 4, "design": {
        "manifold_feed_velocity_ms": 40.0, "cycle": "orsc"}})
    assert old_v4.cycle == "orsc"
    assert old_v4.fuel_manifold_head_fraction == EngineDesign().fuel_manifold_head_fraction
    # A schema-5 file's global head fraction / taper seed every ring (schema 6).
    old_v5 = EngineDesign.from_dict({"schema_version": 5, "design": {
        "manifold_velocity_head_fraction": 0.07, "manifold_taper_blend": 0.2}})
    assert old_v5.fuel_manifold_head_fraction == old_v5.ox_manifold_head_fraction == 0.07
    assert (old_v5.fuel_manifold_taper_blend == old_v5.ox_manifold_taper_blend
            == old_v5.jacket_inlet_taper_blend == 0.2)
    assert old_v5.jacket_inlet_velocity_mult == 1.0
    # A schema-6 file (pre structural hatbands) loads with the new band fields at
    # their defaults and keeps its count/width overrides (schema 7).
    old_v6 = EngineDesign.from_dict({"schema_version": 6, "design": {
        "tube_hatbands": True, "tube_hatband_count": 5, "tube_hatband_width_m": 0.04}})
    assert old_v6.tube_hatband_shape == "auto" and old_v6.tube_hatband_material == "inconel_718"
    assert old_v6.tube_hatband_count == 5 and old_v6.tube_hatband_width_m == 0.04
    v7 = EngineDesign(tube_hatbands=True, tube_hatband_shape="hat",
                      tube_hatband_material="haynes_230")
    assert EngineDesign.from_dict(json.loads(json.dumps(v7.to_dict()))) == v7
    assert v7.to_dict()["schema_version"] >= 7
    # A schema-7 file's "film" section method (retired - film is now an overlay)
    # becomes an uncooled wall + the film fields (schema 8); an ablative section
    # that can't be "uncooled" falls back to "auto".
    old_v7 = EngineDesign.from_dict({"schema_version": 7, "design": {
        "chamber_cooling_method": "film", "film_cooling_fraction": 0.05,
        "nozzle_cooling_method": "film", "bell_material_key": "ablative_phenolic"}})
    assert old_v7.chamber_cooling_method == "uncooled" and old_v7.film_cooling_fraction == 0.05
    assert old_v7.nozzle_cooling_method == "auto" and old_v7.nozzle_film_fraction > 0.0
    assert EngineDesign().to_dict()["schema_version"] >= 8
    # A schema-8 file (pre turbine-exhaust handling) takes the new fields' defaults:
    # overboard duct, plain sonic exit, no heat exchanger (schema 9).
    old_v8 = EngineDesign.from_dict({"schema_version": 8, "design": {"cycle": "gas_generator"}})
    assert (old_v8.turbine_exhaust_mode == "overboard_duct"
            and old_v8.turbine_exhaust_nozzle_eps == 1.0
            and old_v8.turbine_exhaust_hx_gox_kgs == 0.0)
    assert EngineDesign().to_dict()["schema_version"] >= 9
    loaded = json.loads(json.dumps(d.to_dict()))
    rebuilt = EngineDesign.from_dict(loaded)
    assert rebuilt.plumbing_runs == d.plumbing_runs
    assert plumbing.run_from_dict(rebuilt.plumbing_runs[0]).pipes[1].pitch_deg == 60.0

    print("project_io.py self-checks: OK")
