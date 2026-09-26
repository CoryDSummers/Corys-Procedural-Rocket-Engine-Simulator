"""Pump meanline hydraulics + directional design intent (turbopump Round 2,
2026-09-26) - physics/pump_meanline.py, physics/turbopump_intent.py.

(a) Real pumps: the meanline efficiency of every CENTRIFUGAL_ANCHORS / AXIAL_ANCHORS
    pump (F-1, J-2, H-1, SSME HPOTP/HPFTP centrifugal; J-2 Mark 15-F and M-1 axial)
    within ±0.08 of its real efficiency [SP-8107 Table II; SSME-Orientation;
    SP-8125 Fig. 1] - the same tolerance as the Ns-bell correlation's check.
(b) SP-8109's own slip correlation (eq. 17) reproduces its Fig. 16 blade carpet
    within 0.03 in psi, and Huzel's worked A-1 LOX impeller (psi 0.46, beta2 24,
    8 blades) comes out at phi2 0.09-0.14 (book 0.116).
(c) PREDICTION, not fitted: the outlet width b2/D2 of four real impellers within
    15 % of SP-8109 Table I.
(d) Size effect: meanline vs SP-8109 Fig. 6 (stage eta vs Ns for 1-10 in
    impellers) within ±0.10 on the whole grid - a TREND check (Fig. 6 is read ±1 pt
    and mixes literature curves with test points; the seal-clearance floor is fitted to it).
(e) Neutral intent = Round 1 geometry: size_pump with a neutral HydraulicsSpec gives
    the identical rpm / impeller diameter / stages / tip speed as without one
    (plain, suction-capped and shaft-capped).
(f) Directions (full pipeline): Compact raises the pump's speed, shrinks its impeller
    and lowers the turbopump geometry mass ratio; Efficient does the reverse.
    Stable -> lower beta2 and a steeper (higher) shutoff head.
(g) Aggressive suction lets a suction-limited pump (corpus Vulcain LOX) run faster.
(h) pump_model "correlation" carries no meanline (the Round 1 path).
(i) Corpus J-2 fuel pump, axial (Mark 15-F): eta within 0.08 of 0.73, rpm within
    20 % of 28,266, design diffusion factor <= 0.60 [SP-8125 Table I/II].
(j) Pump heating (suction_stage.pump_heating) vs the SSME Block IIA station
    temperatures [SSME-Orientation p.19]: HPFTP LH2 23.7 -> 51.5 K within 3 K, LPFTP
    20.4 -> 23.7 K within 2 K, HPOTP main LOX +10.6 K within 2 K.
(k) Full pipeline: corpus RS-25 jacket inlet (tank 20.3 K + boost + HPFTP) within 3 K
    of the real MCC coolant inlet 52.0 K [SSME-Orientation p.45]; corpus J-2 inside the
    [TN-Dump] measured 32-47 K LH2 jacket-inlet band (1 K slack).
(l) coolant_inlet_model "table" and pump_model "correlation" keep the Round 1 table value.

Part of the physics/validate/ package - run the whole suite with
`python3 -m engine_designer.physics.validate`."""
import json
import math
import os

from .. import inducer, pump_meanline as pm, turbopump_materials, turbopump_sizing
from ..design import EngineDesign

_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "validation_engines", "engines")
_IN = 0.0254
G = 9.80665
FIG6 = {10: (68, 73.5, 77, 80, 81.5), 8: (67, 73, 75, 78.5, 79.5), 6: (62.5, 68.5, 71, 74.5, 76),
        4: (57.5, 63, 66.5, 69, 69.5), 2: (53, 58.5, 61.5, 64, 64), 1: (50, 55.5, 57.5, 60.5, 60.5)}
FIG6_NS = (800, 1000, 1200, 1600, 2000)
FIG16_NODES = ((6, 25.0, 0.101, 0.477), (8, 20.0, 0.062, 0.567), (12, 30.0, 0.089, 0.605),
               (20, 35.0, 0.080, 0.673), (4, 30.0, 0.155, 0.371))
J2_FUEL_RPM = 28_266.0     # [SP-8125 Table I] Mark 15-F


def _corpus(name, **over):
    with open(os.path.join(_DIR, f"{name}.json")) as f:
        d = json.load(f)["design"]
    d.update(over)
    return EngineDesign.from_dict({"schema_version": EngineDesign.SCHEMA_VERSION, "design": d})


def _neutral_spec(pump_type="centrifugal"):
    return pm.HydraulicsSpec(ns_target_us=turbopump_sizing.NS_TARGET_US,
                             psi=turbopump_sizing.HEAD_COEFFICIENT_PSI, beta2_deg=25.0,
                             tip_speed_fraction=turbopump_sizing.TIP_SPEED_DESIGN_FRACTION,
                             pump_type=pump_type)


def run_pump_meanline_check():
    print("=" * 78)
    print("PUMP MEANLINE + DESIGN INTENT (turbopump Round 2)")
    print("=" * 78)
    rows = []

    # (a) real pumps
    fit, _ = pm.fit_report()
    for name, eta, real, d, good in fit:
        rows.append((f"(a) {name:<20} meanline eta {eta:.3f} vs real {real:.3f} ({d:+.3f})", good, True))

    # (b) eq. 17 vs Fig. 16; Huzel A-1
    for z, b2, phi, psi_real in FIG16_NODES:
        psi = 0.82 * pm.psi_theoretical(phi, b2, z)
        rows.append((f"(b) Fig. 16 Z{z} beta2 {b2:.0f}: eq. 17 psi {psi:.3f} vs {psi_real:.3f}",
                     abs(psi - psi_real) < 0.03, True))
    phi_a1 = pm.solve_phi2(0.46 / 0.82, 24.0, 8, delta=0.75)
    rows.append((f"(b) Huzel SC 6-7 A-1 LOX impeller: phi2 {phi_a1:.3f} (book 0.116)",
                 0.09 < phi_a1 < 0.14, True))

    # (c) b2/D2 prediction
    for name, real in pm.TABLE_I_B2_OVER_D2.items():
        row = next(r for r in pm.CENTRIFUGAL_ANCHORS if r[0] == name)
        st = pm.centrifugal_anchor_eta(row)[1]["stage"]
        ratio = st["b2_m"] / st["d2_m"]
        rows.append((f"(c) {name:<9} b2/D2 {ratio:.3f} vs SP-8109 Table I {real:.3f} "
                     f"({st['z']} blades, phi2 {st['phi2']:.3f})",
                     abs(ratio / real - 1.0) < 0.15, True))

    # (d) Fig. 6 size effect
    worst = 0.0
    for d_in, reals in FIG6.items():
        for ns, real in zip(FIG6_NS, reals):
            u2 = 100.0
            h = 0.5 * u2 * u2 / G
            n = 60.0 * u2 / (math.pi * d_in * _IN)
            q = (ns * (h / 0.3048) ** 0.75 / n) ** 2 * 6.30902e-5
            e = pm.design_centrifugal(q, h, n, u2, 1, 1000.0, 1.0e-6, ss_design=10_000.0)["eta"]
            worst = max(worst, abs(e * 100.0 - real))
    rows.append((f"(d) SP-8109 Fig. 6 size effect (1-10 in, Ns 800-2000): worst |d| {worst:.1f} pts",
                 worst <= 10.0, True))

    # (e) neutral intent = Round 1 geometry
    mat = turbopump_materials.MATERIALS["inconel_718"]
    spec = inducer.make_spec("LOX", "ox", 90.2, 60.0)
    cases = (dict(), dict(suction=spec), dict(shaft_rpm_cap=5000.0))
    same = True
    for kw in cases:
        a = turbopump_sizing.size_pump(1800.0, 11e6, 1141.0, mat, **kw)
        b = turbopump_sizing.size_pump(1800.0, 11e6, 1141.0, mat, hydraulics=_neutral_spec(), **kw)
        for k in ("n_rpm", "d_impeller_m", "n_stages", "u_tip_m_s", "volute_od_m", "body_length_m"):
            same &= a[k] == b[k]
    rows.append(("(e) neutral intent: rpm / D2 / stages / tip speed / envelope identical to Round 1 "
                 "(plain, suction-capped, shaft-capped)", same, True))

    # (f) directions through the pipeline (J-2: dual shaft, ox pump centrifugal)
    base = _corpus("J-2").compute()["turbopump_sizing"]
    comp = _corpus("J-2", pump_priority=1.0).compute()["turbopump_sizing"]
    effi = _corpus("J-2", pump_priority=-1.0).compute()["turbopump_sizing"]
    ob, oc, oe = base["ox_pump"], comp["ox_pump"], effi["ox_pump"]
    ok_f = (oc["rpm_ns_optimum"] > ob["rpm_ns_optimum"] > oe["rpm_ns_optimum"]
            and oc["d_impeller_m"] < ob["d_impeller_m"] < oe["d_impeller_m"]
            and comp["intent_mass_ratio"] < 1.0 < effi["intent_mass_ratio"])
    rows.append((f"(f) J-2 ox pump Efficient/neutral/Compact: Ns-optimum rpm {oe['rpm_ns_optimum']:,.0f} / "
                 f"{ob['rpm_ns_optimum']:,.0f} / {oc['rpm_ns_optimum']:,.0f}, D2 "
                 f"{oe['d_impeller_m'] * 1000:.0f} / {ob['d_impeller_m'] * 1000:.0f} / "
                 f"{oc['d_impeller_m'] * 1000:.0f} mm, eta {oe['eta']:.3f} / {ob['eta']:.3f} / "
                 f"{oc['eta']:.3f}, geometry mass x{effi['intent_mass_ratio']:.2f} / 1 / "
                 f"x{comp['intent_mass_ratio']:.2f}", ok_f, True))
    stab = _corpus("J-2", pump_head_curve=-1.0).compute()["turbopump_sizing"]["ox_pump"]["meanline"]
    head = _corpus("J-2", pump_head_curve=1.0).compute()["turbopump_sizing"]["ox_pump"]["meanline"]
    ok_h = (stab["stage"]["beta2_deg"] < head["stage"]["beta2_deg"]
            and stab["hq"]["shutoff_ratio"] > head["hq"]["shutoff_ratio"])
    rows.append((f"(f) J-2 ox pump Stable/Max head: beta2 {stab['stage']['beta2_deg']:.0f} / "
                 f"{head['stage']['beta2_deg']:.0f} deg, shutoff head {stab['hq']['shutoff_ratio']:.2f} / "
                 f"{head['hq']['shutoff_ratio']:.2f} x design", ok_h, True))

    # (g) aggressive suction frees a suction-limited pump
    vb = _corpus("Vulcain").compute()["turbopump_sizing"]["ox_pump"]
    va = _corpus("Vulcain", suction_aggressiveness=1.0).compute()["turbopump_sizing"]["ox_pump"]
    rows.append((f"(g) Vulcain LOX pump (suction-limited {vb['suction_limited']}): {vb['n_rpm']:,.0f} rpm "
                 f"-> {va['n_rpm']:,.0f} rpm with aggressive suction (real ~13,600)",
                 vb["suction_limited"] and va["n_rpm"] > vb["n_rpm"], True))

    # (h) correlation switch
    cr = _corpus("F-1", pump_model="correlation").compute()["turbopump_sizing"]["ox_pump"]
    rows.append(("(h) pump_model 'correlation': no meanline, Ns-bell efficiency (Round 1 path)",
                 "meanline" not in cr and "eta_correlation" not in cr, True))

    # (i) corpus J-2 axial fuel pump
    fp = _corpus("J-2").compute()["turbopump_sizing"]["fuel_pump"]
    ml = fp.get("meanline") or {}
    ok_i = (fp.get("pump_type") == "axial" and abs(fp["eta"] - 0.73) <= 0.08
            and abs(fp["n_rpm"] / J2_FUEL_RPM - 1.0) <= 0.20
            and max(ml.get("df_rotor", 9), ml.get("df_stator", 9)) <= 0.60)
    rows.append((f"(i) corpus J-2 fuel pump axial: {fp['n_stages']} stages, {fp['n_rpm']:,.0f} rpm "
                 f"(real 28,266), eta {fp['eta']:.3f} (real 0.73), DF "
                 f"{max(ml.get('df_rotor', 0), ml.get('df_stator', 0)):.2f}, tip "
                 f"{ml.get('d_tip_m', 0) / _IN:.2f} in (real 7.22)", ok_i, True))

    # (j) pump heating vs the SSME Block IIA flow schematic [SSME-Orientation p.19]
    from ..design import suction_stage as ss
    psi = 6894.757
    t_hp = ss.fuel_pump_outlet_k("LOX/LH2", 23.7, 298 * psi, 5956 * psi, 0.750)
    t_lp = ss.fuel_pump_outlet_k("LOX/LH2", 20.4, 30 * psi, 298 * psi, 0.713)
    d_ox = ss.lox_pump_rise_k((4025 - 421) * psi, 1142.0, 0.718, 93.7)
    rows.append((f"(j) SSME pump heating: HPFTP LH2 23.7 -> {t_hp:.1f} K (real 51.5), LPFTP "
                 f"20.4 -> {t_lp:.1f} K (real 23.7), HPOTP main LOX +{d_ox:.1f} K (real +10.6)",
                 abs(t_hp - 51.5) <= 3.0 and abs(t_lp - 23.7) <= 2.0 and abs(d_ox - 10.6) <= 2.0,
                 True))
    # (k) full pipeline: corpus RS-25 jacket inlet = HPFTP discharge (real MCC coolant inlet)
    rs = _corpus("RS-25").compute()
    rows.append((f"(k) corpus RS-25 regen jacket inlet {rs['coolant_inlet_t_k']:.1f} K (tank 20.3 K + "
                 f"LPFTP + HPFTP heating) vs real MCC coolant inlet 52.0 K [SSME-Orientation p.45]",
                 abs(rs["coolant_inlet_t_k"] - 52.0) <= 3.0, True))
    j2 = _corpus("J-2").compute()
    rows.append((f"(k) corpus J-2 regen jacket inlet {j2['coolant_inlet_t_k']:.1f} K vs [TN-Dump] "
                 f"measured LH2 jacket inlets 32-47 K (1 K slack)",
                 31.0 <= j2["coolant_inlet_t_k"] <= 48.0, True))
    # (l) the table fallbacks are the Round 1 constant
    tb = _corpus("RS-25", coolant_inlet_model="table").compute()
    cr2 = _corpus("RS-25", pump_model="correlation").compute()
    rows.append((f"(l) coolant_inlet_model 'table' / pump_model 'correlation': jacket inlet "
                 f"{tb['coolant_inlet_t_k']:.0f} / {cr2['coolant_inlet_t_k']:.0f} K (the Round 1 table)",
                 tb["coolant_inlet_t_k"] == 45.0 and cr2["coolant_inlet_t_k"] == 45.0, True))

    all_ok = True
    for text, ok, gated in rows:
        tag = ("[OK]" if ok else "[*** FAIL ***]") if gated else ""
        print(f"  {text}  {tag}")
        all_ok &= ok
    print()
    print("ALL PUMP MEANLINE CHECKS OK" if all_ok else
          "*** PUMP MEANLINE CHECK FAILED - review physics/pump_meanline.py, turbopump_intent.py ***")
    print("=" * 78)
    return all_ok


if __name__ == "__main__":
    raise SystemExit(0 if run_pump_meanline_check() else 1)
