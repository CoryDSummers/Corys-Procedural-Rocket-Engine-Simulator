"""(Re)build the real-engine validation corpus: ``validation_engines/engines/*.json``.

Each file is an ordinary engine_designer project (open it in the GUI) plus a
top-level ``"reference"`` block (ignored by ``EngineDesign.from_dict``) that
``run_corpus.py --report`` compares the model against.

Sourcing rules (CLAUDE.md "never invent a number, and say which"):
  * Pc / MR / eps / vac thrust / Isp come from the named ``Engine_Configs/*_Config.cfg``
    header block (RealismOverhaul's own numbers), cited as ``[RO <file> "<variant>"]``.
  * Cooling reference numbers come ONLY from claude_lit with their ``[Tag]`` cites.
    No cited number -> no metric; the gap is listed in the engine's ``gaps``.
  * Architecture choices (wall construction, topology, which section is regen /
    dump / ablative / radiative) are well-documented public facts of each engine,
    or an explicit stand-in - each carries a ``note`` saying which.
  * "validated" metrics gate ``--report``'s exit status; "plausibility" ones only flag.

Edit the ENGINES table below and re-run::

    python3 -m engine_designer.validation_engines.build_corpus
"""
from __future__ import annotations

import json
import os

from engine_designer.physics.design import EngineDesign

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "engines")

BTU_IN2_S_TO_MW_M2 = 1.634246   # 1 Btu/in^2-s = 1.634 MW/m^2
ISP_TOL_PCT = 5.0               # == validate.TOLERANCE_PCT


def _isp(v, cite):
    return {"value": v, "lo": round(v * (1 - ISP_TOL_PCT / 100), 2),
            "hi": round(v * (1 + ISP_TOL_PCT / 100), 2), "unit": "s",
            "kind": "validated", "cite": cite}


def _thrust_kn(v_n, cite):
    kn = v_n / 1e3
    return {"value": kn, "lo": round(kn * 0.99, 3), "hi": round(kn * 1.01, 3), "unit": "kN",
            "kind": "validated", "cite": cite}


# J-2-class hydrogen-engine throat flux band and the SSME design point [Wieseneck-J2 p.6, 12]
_J2_CLASS_Q = {"value": None, "lo": round(17 * BTU_IN2_S_TO_MW_M2, 1),
               "hi": round(35 * BTU_IN2_S_TO_MW_M2, 1), "unit": "MW/m2", "kind": "plausibility",
               "cite": "[Wieseneck-J2 p.6, 12] J-2/J-2S/M-1 17-35 Btu/in2-s"}
_SSME_Q = {"value": round(72 * BTU_IN2_S_TO_MW_M2, 1),
           "lo": round(72 * BTU_IN2_S_TO_MW_M2 * 0.7, 1), "hi": round(72 * BTU_IN2_S_TO_MW_M2 * 1.3, 1),
           "unit": "MW/m2", "kind": "plausibility",
           "cite": "[Wieseneck-J2 p.6] SSME design point 72 Btu/in2-s @3000 psia (band +/-30%)"}

_BELL = dict(nozzle_type="bell", bell_percent_length=80.0)

ENGINES = {
    "F-1": dict(
        design=dict(propellant_pair="LOX/RP-1", mixture_ratio=2.27, chamber_pressure_pa=6.77e6,
                    expansion_ratio=16.0, target_vac_thrust_n=7_775_490.0, cycle="gas_generator",
                    material_key="inconel_718", bell_material_key="inconel_718",
                    chamber_cooling_method="regenerative", nozzle_cooling_method="uncooled",
                    cooling_transition_eps=10.0, regen_channel_model="channels",
                    wall_construction="tube_wall", cooling_flow_topology="f1_split_reverse_flow",
                    turbine_exhaust_mode="nozzle_injection", turbine_exhaust_inject_eps=10.0,
                    injector_type="impinging", config_name="F-1", **_BELL),
        notes=["Inconel-X-750 tube wall in reality; inconel_718 is the closest catalog alloy.",
               "Regen tube bundle to eps 10, then a turbine-exhaust-film-cooled extension to eps 16 "
               "[SP-8120 s2.2.2]: modelled as an uncooled Inconel extension + the turbine exhaust "
               "injected at eps 10 (turbine_exhaust_mode nozzle_injection), whose gas film cools it. "
               "(Until 2026-09-24 an 8%-of-fuel liquid slot film stood in for the exhaust film.)",
               "The F-1's heat exchanger (LOX->GOX) in the exhaust duct is not modelled: no GOX "
               "flow in hand."],
        cite='[RO F1_Config.cfg "SA-501..503"]',
        isp=(301.0, 262.1), gaps=["throat heat flux", "coolant dT", "jacket dP", "wall temps"]),
    "J-2": dict(
        design=dict(propellant_pair="LOX/LH2", mixture_ratio=5.5, chamber_pressure_pa=5.26e6,
                    expansion_ratio=27.5, target_vac_thrust_n=1_023_090.6, cycle="gas_generator",
                    material_key="stainless_steel", bell_material_key="stainless_steel",
                    chamber_cooling_method="regenerative", nozzle_cooling_method="regenerative",
                    regen_nozzle_end_eps=27.5, regen_channel_model="channels",
                    wall_construction="tube_wall", cooling_flow_topology="j2_mid_nozzle_inlet",
                    jacket_inlet_eps=8.0, injector_type="coax_post", config_name="J-2",
                    regen_channel_count=360, turbine_exhaust_mode="nozzle_injection",
                    turbine_exhaust_inject_eps=10.9, **_BELL),
        notes=["347-stainless tube wall, full-length regen, two-pass with a mid-nozzle inlet "
               "(validate.run_two_pass_cooling_check's J-2 layout).",
               "Tubes: 180 down then 360 up [AEDC-J2S s2.1.1 p.1-2] (J-2S; same circuit as the "
               "J-2's 1-1/2-pass layout [SP-8087 Table I p.5]) -> regen_channel_count=360 (the "
               "up count; the down count follows as 180). jacket_inlet_eps 8 is NOT cited.",
               "Turbine exhaust enters the nozzle through eyelets ('cat-eyes') between the tubes, "
               "115 in2 total at eps 10.45-11.40 [J-2 history, literature/; SP-8120] -> "
               "nozzle_injection at eps 10.9 (the band's middle)."],
        cite='[RO J2_Config.cfg "J-2 230K (1968)"]', isp=(425.0, 304.0),
        extra={"q_throat_mw_m2": _J2_CLASS_Q},
        gaps=["coolant dT", "jacket dP", "wall temps"]),
    "RS-25": dict(
        design=dict(propellant_pair="LOX/LH2", mixture_ratio=6.0, chamber_pressure_pa=20.48e6,
                    expansion_ratio=77.5, target_vac_thrust_n=2_090_000.0, cycle="frsc",
                    material_key="narloy_z", bell_material_key="stainless_steel",
                    chamber_cooling_method="regenerative", nozzle_cooling_method="regenerative",
                    cooling_transition_eps=5.0, regen_nozzle_end_eps=77.5,
                    regen_channel_model="channels", wall_construction="milled_channel",
                    injector_type="coax_post", config_name="RS-25", **_BELL),
        notes=["NARloy-Z milled-channel main combustion chamber; regen stainless tube-wall nozzle "
               "to the exit (bell_material stainless_steel, transition eps 5 is a stand-in for "
               "the MCC/nozzle joint)."],
        cite='[RO SSME_Config.cfg first block]', isp=(455.2, 363.2),
        extra={"q_throat_mw_m2": _SSME_Q,
               "t_wg_throat_k": {"value": None, "lo": 0.0, "hi": 811.0, "unit": "K",
                                 "kind": "plausibility",
                                 "cite": "[Wieseneck-J2] 1000 F copper gas-side max"}},
        gaps=["coolant dT", "jacket dP"]),
    "RL10A-3-3": dict(
        design=dict(propellant_pair="LOX/LH2", mixture_ratio=5.0, chamber_pressure_pa=2.72e6,
                    expansion_ratio=61.0, target_vac_thrust_n=70_050.0, cycle="expander",
                    material_key="stainless_steel", bell_material_key="stainless_steel",
                    chamber_cooling_method="regenerative", nozzle_cooling_method="regenerative",
                    regen_nozzle_end_eps=61.0, regen_channel_model="channels",
                    wall_construction="tube_wall", injector_type="coax_post",
                    config_name="RL10A-3-3", **_BELL),
        notes=["Stainless tube-wall chamber+nozzle, fully regen (the heat IS the expander's "
               "turbine drive); real RL10 is ~1.5-pass, modelled single-pass counterflow."],
        cite='[RO RL10_Config.cfg "RL10A-3-3"]', isp=(442.2, 186.0),
        gaps=["throat heat flux", "coolant dT", "jacket dP", "wall temps"]),
    "Vulcain": dict(
        design=dict(propellant_pair="LOX/LH2", mixture_ratio=5.25, chamber_pressure_pa=11.0e6,
                    expansion_ratio=45.0, target_vac_thrust_n=1_145_000.0, cycle="gas_generator",
                    material_key="narloy_z", bell_material_key="inconel_718",
                    chamber_cooling_method="regenerative", nozzle_cooling_method="dump",
                    cooling_transition_eps=6.0, regen_nozzle_end_eps=45.0,
                    regen_channel_model="channels", wall_construction="milled_channel",
                    injector_type="coax_post", config_name="Vulcain", **_BELL),
        notes=["Copper-alloy milled-channel chamber; hydrogen-dump-cooled nozzle extension "
               "(validate.run_explicit_cooling_check (f) Vulcain-HM-60-class). narloy_z/inconel_718 "
               "are catalog stand-ins; transition eps 6 = the tool default."],
        cite='[RO Vulcain_Config.cfg first block]', isp=(431.5, 315.0),
        gaps=["throat heat flux", "coolant dT", "jacket dP", "dump fraction"]),
    "Raptor-2": dict(
        design=dict(propellant_pair="LOX/CH4", mixture_ratio=3.55, chamber_pressure_pa=30.0e6,
                    expansion_ratio=40.0, target_vac_thrust_n=2_255_530.0, cycle="ffsc",
                    material_key="grcop_84", bell_material_key="inconel_718",
                    chamber_cooling_method="regenerative", nozzle_cooling_method="regenerative",
                    regen_nozzle_end_eps=40.0, regen_channel_model="channels",
                    wall_construction="milled_channel", injector_type="coaxial_swirl",
                    config_name="Raptor-2", **_BELL),
        notes=["Chamber alloy/construction not public; grcop_84 milled-channel full-length regen "
               "is a representative stand-in, NOT a sourced fact."],
        cite='[RO Raptor_Config.cfg "Raptor-2"]', isp=(347.0, 326.357),
        gaps=["everything cooling-related (proprietary)"]),
    "RD-180": dict(
        design=dict(propellant_pair="LOX/RP-1", mixture_ratio=2.72, chamber_pressure_pa=26.66e6,
                    expansion_ratio=36.87, target_vac_thrust_n=4_152_000.0, cycle="orsc",
                    material_key="narloy_z", bell_material_key="inconel_718",
                    chamber_cooling_method="regenerative", nozzle_cooling_method="regenerative",
                    regen_nozzle_end_eps=36.87, regen_channel_model="channels",
                    wall_construction="milled_channel", turbopump_material_key="monel_k500",
                    injector_type="coaxial_swirl", config_name="RD-180", **_BELL),
        notes=["Copper-alloy liner brazed to a steel shell (Russian milled-channel practice) "
               "- narloy_z stand-in. Real engine also uses internal fuel film belts; not modelled "
               "(fraction not cited)."],
        cite='[RO RD180_Config.cfg first block]', isp=(338.4, 311.9),
        gaps=["film-belt fraction", "throat heat flux", "coolant dT", "jacket dP"]),
    "Merlin-1D": dict(
        design=dict(propellant_pair="LOX/RP-1", mixture_ratio=2.34, chamber_pressure_pa=9.72e6,
                    expansion_ratio=21.4, target_vac_thrust_n=742_400.0, cycle="gas_generator",
                    material_key="narloy_z", bell_material_key="inconel_718",
                    chamber_cooling_method="regenerative", nozzle_cooling_method="regenerative",
                    regen_nozzle_end_eps=21.4, regen_channel_model="channels",
                    wall_construction="milled_channel", injector_type="pintle",
                    config_name="Merlin-1D", **_BELL),
        notes=["Pintle injector and regen chamber/nozzle are public; alloy and channel details are "
               "stand-ins."],
        cite='[RO Merlin1_Config.cfg "Merlin 1D"]', isp=(311.0, 282.0),
        gaps=["everything cooling-related (proprietary)"]),
    "Rutherford": dict(
        design=dict(propellant_pair="LOX/RP-1", mixture_ratio=2.5, chamber_pressure_pa=12.0e6,
                    expansion_ratio=10.5, target_vac_thrust_n=26_190.0, cycle="electric_pump",
                    material_key="inconel_718", bell_material_key="inconel_718",
                    chamber_cooling_method="regenerative", nozzle_cooling_method="regenerative",
                    regen_nozzle_end_eps=10.5, regen_channel_model="channels",
                    wall_construction="milled_channel", injector_type="impinging",
                    config_name="Rutherford", **_BELL),
        notes=["3D-printed Inconel regen chamber (public). RO's own header flags Pc and eps with "
               "'?' - treat this engine's gas-side numbers as low-confidence."],
        cite='[RO Rutherford_Config.cfg first block (Pc "12?", eps "10.5?")]', isp=(317.0, 311.0),
        gaps=["everything cooling-related"]),
    "AJ10-137": dict(
        design=dict(propellant_pair="Aerozine-50/NTO", mixture_ratio=1.6, chamber_pressure_pa=0.68e6,
                    expansion_ratio=62.5, target_vac_thrust_n=97_416.0, cycle="pressure_fed",
                    material_key="ablative_phenolic", bell_material_key="niobium_c103",
                    chamber_cooling_method="ablative", nozzle_cooling_method="radiative",
                    cooling_transition_eps=6.0, injector_type="impinging",
                    config_name="AJ10-137", **_BELL),
        notes=["Apollo SPS: ablative chamber + throat to eps 6, radiation-cooled columbium (and "
               "titanium aft) extension - modelled as C-103 from eps 6 to the exit."],
        cite='[RO AJ10_137_Config.cfg first block]', isp=(314.5, None),
        gaps=["wall temps", "ablation rate"]),
    "Aestus": dict(
        design=dict(propellant_pair="N2O4/MMH", mixture_ratio=1.9, chamber_pressure_pa=1.1e6,
                    expansion_ratio=84.0, target_vac_thrust_n=27_800.0, cycle="pressure_fed",
                    material_key="stainless_steel", bell_material_key="niobium_c103",
                    chamber_cooling_method="regenerative", nozzle_cooling_method="radiative",
                    cooling_transition_eps=6.0, regen_channel_model="channels",
                    wall_construction="milled_channel", injector_type="coaxial_swirl",
                    config_name="Aestus", **_BELL),
        notes=["MMH-regen-cooled chamber + radiation-cooled extension (public architecture); alloys "
               "and the eps-6 transition are stand-ins."],
        cite='[RO Aestus_Config.cfg first block]', isp=(306.0, 113.0),
        gaps=["everything cooling-related"]),
    "LMAE": dict(
        design=dict(propellant_pair="Aerozine-50/NTO", mixture_ratio=1.6, chamber_pressure_pa=0.83e6,
                    expansion_ratio=45.6, target_vac_thrust_n=15_570.0, cycle="pressure_fed",
                    material_key="refrasil_phenolic", bell_material_key="refrasil_phenolic",
                    chamber_cooling_method="ablative", nozzle_cooling_method="ablative",
                    injector_type="impinging", config_name="LMAE", **_BELL),
        notes=["Bell Aerosystems LM ascent engine: fully ablative Refrasil-phenolic chamber+nozzle."],
        cite='[RO LMAE_Config.cfg first block]', isp=(311.0, None),
        gaps=["char depth / ablation rate"]),
}


def build():
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, e in ENGINES.items():
        d = EngineDesign(**e["design"])
        cite = e["cite"]
        metrics = {"isp_vac_s": _isp(e["isp"][0], cite),
                   "thrust_vac_kn": _thrust_kn(e["design"]["target_vac_thrust_n"], cite)}
        if e["isp"][1] is not None:
            m = _isp(e["isp"][1], cite)
            m["kind"] = "plausibility"   # tool's SL Isp is a separation-naive estimate
            metrics["isp_sl_s"] = m
        metrics.update(e.get("extra", {}))
        doc = d.to_dict()
        doc["reference"] = {"source": cite, "notes": e["notes"], "gaps": e.get("gaps", []),
                            "metrics": metrics}
        path = os.path.join(OUT_DIR, f"{name}.json")
        with open(path, "w") as f:
            json.dump(doc, f, indent=2)
        print(f"wrote {os.path.relpath(path)}")


if __name__ == "__main__":
    build()
