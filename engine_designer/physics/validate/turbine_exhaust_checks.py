"""Turbine-exhaust handling (physics/turbine_exhaust.py) through the full
EngineDesign.compute() pipeline: back pressure, exhaust thrust, the aspirator
slot, the injection-mode gas film, and the closed-cycle guard.

Part of the physics/validate/ package - run the whole suite with
`python3 -m engine_designer.physics.validate`."""
import json
import os

from .. import turbine_exhaust as te
from ..design import EngineDesign

PSI = 6894.757
LBF = 4.44822
G0 = 9.80665
_CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "validation_engines", "engines")
_CORPUS_F1 = os.path.join(_CORPUS_DIR, "F-1.json")


def _h1_design(mode="aspirator", **kw):
    """H-1 (200K rating) [H1-Man Fig 1-17/1-18]: LOX/RP-1, injector-end Pc
    689.3 psia, O/F 2.338, eps 8, 199,300 lbf SL at 267.9 s -> ~976 kN vac at
    RO's 295 s vac Isp [RO H1 header]."""
    return EngineDesign(propellant_pair="LOX/RP-1", mixture_ratio=2.338,
                        chamber_pressure_pa=689.3 * PSI, expansion_ratio=8.0,
                        nozzle_type="bell", bell_percent_length=80.0,
                        cycle="gas_generator", injector_type="impinging",
                        target_vac_thrust_n=199_300.0 * LBF * 295.0 / 267.9,
                        turbine_exhaust_mode=mode, **kw)


def _f1_corpus(**over):
    with open(_CORPUS_F1) as f:
        d = json.load(f)["design"]
    d.update(over)
    return EngineDesign.from_dict({"schema_version": EngineDesign.SCHEMA_VERSION, "design": d})


def run_turbine_exhaust_check():
    """
    (a) H-1 back pressure, full pipeline [H1-Man]: a sea-level booster
        (attached at SL) whose aspirator must leave sonic to sea level ->
        turbine exit ~33.8 psia, PR ~17.7 (EXHAUST_DUCT_PRESSURE_RATIO is
        reverse-solved on exactly this, so this pins the wiring); GG share of
        total flow vs the real 2.26 % and the aspirator slot vs the real
        0.440 in are PLAUSIBILITY bands (x0.5-2 / x0.6-1.5).
    (b) F-1 exhaust Isp calibration pin: the corpus F-1 in nozzle_injection at
        eps 10 must give 16,000 lbf / ~77 kg/s = 94.3 s +-5 % [SP-8120;
        topic 10] (EXHAUST_THRUST_EFFICIENCY is reverse-solved on this), and
        its gas film must cool the uncooled extension vs overboard disposal.
        (Engine Isp injection vs overboard is REPORTED, not ordered: with the
        F-1 back pressure the injection turbine runs a lower PR, so it can cost
        a few tenths of a second - the F-1 injects to cool its extension.)
    (c) LR-91 plausibility [RO LR91 header]: NTO/A-50 overboard exhaust
        nozzle's thrust within x0.5-2 of the real 865 lbf (storable GG flow
        is itself an unchecked estimate - see ASSUMPTIONS).
    (d) Theoretical fuel-rich GG exhaust dumped into a main nozzle
        [Tripropellant-CR150444 Table 2]: 141.6 s O2/CH4, 282.7 s O2/H2 vac -
        the IDEAL injection-mode Isp (efficiency divided back out) within
        +-20 %.
    (e) Closed cycle ignores the mode with a warning, results unchanged.
    (f) Engine-Isp consistency: cycle_result gg_dump_isp_fraction is the
        exhaust stream's vac Isp / chamber vac Isp (no flat 0.55 left).
    (g) Hardware: aspirator / manifold / outlet sized per mode, the default
        exhaust duct closes onto the turbine exhaust port.
    (h) F-1 back pressure, full pipeline [F1-Man Fig 1-16/3-14]: the corpus
        F-1 in injection mode gives turbine PR ~16.3 (945 / 58 psia) +-10 %
        and a turbine exit within +-15 % of 58 psia scaled by corpus Pc / the
        real 1,125 psia (EXHAUST_INJECTION_PRESSURE_RATIO is reverse-solved on
        this - an interim lumped value, see its comment).
    (i) F-1 plausibility [F1-Man]: GG share of total flow within x0.5-2 of
        2.91 % (167 / 5,737 lb/s - the model runs low because its pump power
        is low: turbine specific work matches the real ~508 kJ/kg, see
        OPEN_QUESTIONS), exhaust temperature +-15 % of the 1,138 F (888 K)
        extension coolant, duct bore x0.7-1.4 of the ~24 in heat-exchanger
        outlet end (the first check on TURBINE_EXHAUST_DUCT_MACH).
    (j) Gas film [TN-D3836] (turbine_exhaust.gas_film_effectiveness_profile):
        the corpus J-2's modelled injection slot area (the sonic slot) within
        x0.5-2 of its real 115 in^2 of eyelets [RPE-J2Blog], and the F-1 film
        is laid (the profile's monotone decay / flow dependence is in the
        module self-test).
    (k) Scroll manifold [F1-Man §1-18/§1-72; F-1 photo]: the corpus F-1's
        injection manifold is a tangentially-fed one-way scroll whose inlet
        bore (sized on the FULL exhaust flow) is within +-15 % of the real
        24 in heat-exchanger manifold end, tapering toward its tail, and the
        default duct enters it tangentially (no radial T, no root reducer);
        its omega expansion-joint count is the F-1's real 15 (the spacing is
        reverse-solved on it - a pin, not a prediction).
    """
    print()
    print("=" * 78)
    print("TURBINE-EXHAUST CHECK (overboard / aspirator / nozzle injection)")
    print("=" * 78)
    rows = []

    # (a) H-1
    r = _h1_design().compute()
    e = r["turbine_exhaust"]
    pout_psia = e["p_turbine_out_pa"] / PSI
    share = r["cycle_result"]["gg_fraction_of_total"]
    gap_in = e["aspirator_gap_m"] / 0.0254
    a_ok = (not r["separated_at_100pct_sl"] and e["back_pressure_limited"]
            and abs(pout_psia - 33.8) / 33.8 < 0.05
            and abs(e["turbine_pressure_ratio"] - 17.7) / 17.7 < 0.05
            and 0.5 * 0.0226 <= share <= 2.0 * 0.0226
            and 0.6 * 0.440 <= gap_in <= 1.5 * 0.440)
    rows.append((f"(a) H-1 aspirator: turbine exit {pout_psia:.1f} psia (real 33.8), PR "
                 f"{e['turbine_pressure_ratio']:.1f} (real ~17.7), GG {share*100:.2f}% of flow "
                 f"(real 2.26%), slot gap {gap_in:.3f} in (real 0.440)", a_ok))

    # (b) F-1 injection
    f_inj = _f1_corpus(turbine_exhaust_mode="nozzle_injection", turbine_exhaust_inject_eps=10.0,
                       nozzle_film_fraction=0.0).compute()
    f_ob = _f1_corpus(turbine_exhaust_mode="overboard_duct", nozzle_film_fraction=0.0).compute()
    ei = f_inj["turbine_exhaust"]
    tw_i = f_inj["bell_material_margin"]["assumed_wall_temp_k"]
    tw_o = f_ob["bell_material_margin"]["assumed_wall_temp_k"]
    want = 16_000.0 * LBF / (77.0 * G0)
    b_ok = (abs(ei["isp_vac_s"] - want) / want < 0.05 and ei.get("gas_film_applied")
            and tw_i < tw_o and (ei.get("film_residual_kgs") or 0.0) < 1e-6 * ei["mdot_kgs"] + 1e-9)
    rows.append((f"(b) F-1 injection at eps 10: exhaust Isp {ei['isp_vac_s']:.1f} s (16,000 lbf / "
                 f"77 kg/s = {want:.1f} s), extension wall {tw_i:.0f} K with the gas film vs "
                 f"{tw_o:.0f} K overboard, engine Isp {f_inj['isp_vac_engine_s']:.2f} vs "
                 f"{f_ob['isp_vac_engine_s']:.2f} s", b_ok))

    # (c) LR-91
    r91 = EngineDesign(propellant_pair="Aerozine-50/NTO", mixture_ratio=1.88,
                       chamber_pressure_pa=5.7e6, expansion_ratio=49.2, cycle="gas_generator",
                       target_vac_thrust_n=100_865.0 * LBF, turbine_exhaust_mode="overboard_duct",
                       turbine_exhaust_nozzle_eps=4.0).compute()
    f91 = r91["turbine_exhaust"]["thrust_vac_n"] / LBF
    c_ok = 0.5 * 865.0 <= f91 <= 2.0 * 865.0
    rows.append((f"(c) LR-91 overboard exhaust nozzle (eps 4): {f91:.0f} lbf vs real 865 "
                 f"(x0.5-2 plausibility; model GG {r91['turbine_exhaust']['mdot_kgs']:.2f} kg/s)",
                 c_ok))

    # (d) theoretical dump Isp, ideal (efficiency divided back out)
    d_rows = []
    for pair, mr, real in (("LOX/CH4", 3.4, 141.6), ("LOX/LH2", 5.5, 282.7)):
        rr = EngineDesign(propellant_pair=pair, mixture_ratio=mr, chamber_pressure_pa=10e6,
                          expansion_ratio=40.0, cycle="gas_generator", target_vac_thrust_n=1.0e6,
                          turbine_exhaust_mode="nozzle_injection",
                          turbine_exhaust_inject_eps=10.0).compute()
        ideal = rr["turbine_exhaust"]["isp_vac_s"] / te.EXHAUST_THRUST_EFFICIENCY
        d_rows.append((pair, ideal, real, abs(ideal - real) / real < 0.20))
    d_ok = all(x[3] for x in d_rows)
    rows.append(("(d) ideal injected-exhaust Isp: " + ", ".join(
        f"{p} {i:.0f} s (theory {rl})" for p, i, rl, _ in d_rows) + " (+-20%)", d_ok))

    # (e) closed cycle guard
    base = dict(propellant_pair="LOX/CH4", mixture_ratio=3.6, chamber_pressure_pa=25e6,
                expansion_ratio=35.0, cycle="ffsc", target_vac_thrust_n=2.0e6)
    c0 = EngineDesign(**base).compute()
    c1 = EngineDesign(**base, turbine_exhaust_mode="aspirator").compute()
    e_ok = (c1["isp_vac_engine_s"] == c0["isp_vac_engine_s"] and c1["turbine_exhaust"] is None
            and any("Turbine exhaust handling" in row.get("name", "") and not row.get("passed")
                    for row in c1["checklist"]))
    rows.append(("(e) FFSC with aspirator mode: ignored with a warning, Isp unchanged", e_ok))

    # (f) no flat fraction left
    f_ok = all(abs(x["cycle_result"]["gg_dump_isp_fraction"]
                   - x["turbine_exhaust"]["isp_vac_s"] / x["isp_vac_chamber_s"]) < 1e-12
               for x in (r, f_inj, r91))
    rows.append(("(f) gg_dump_isp_fraction == exhaust vac Isp / chamber vac Isp", f_ok))

    # (g) hardware: each mode sizes its termination, the default exhaust duct
    # closes onto the turbine's exhaust port, and it all lands in the dry mass
    g_parts = []
    for res in (r, f_inj, f_ob):
        hw = res["turbine_exhaust_hardware"]
        te_runs = [x for x in res["plumbing_results"] if x["host"] == "turbine_exhaust"]
        g_parts.append(hw is not None and hw["mass_kg"] > 0
                       and res["turbopump_ports"].get("turbine", {}).get("exhaust") is not None
                       and len(te_runs) == 1 and te_runs[0]["connected_pump"] == "turbine"
                       and te_runs[0]["implicit"])
    g_ok = (all(g_parts) and r["turbine_exhaust_hardware"]["aspirator"] is not None
            and f_inj["turbine_exhaust_hardware"]["manifold"] is not None
            and f_ob["turbine_exhaust_hardware"]["outlet"] is not None)
    rows.append((f"(g) hardware: H-1 aspirator shroud {r['turbine_exhaust_hardware']['mass_kg']:.0f} kg, "
                 f"F-1 injection manifold {f_inj['turbine_exhaust_hardware']['mass_kg']:.0f} kg / "
                 f"overboard outlet {f_ob['turbine_exhaust_hardware']['mass_kg']:.0f} kg; default duct "
                 f"closes on the turbine exhaust port", g_ok))

    # (h) F-1 back pressure
    pc_scale = f_inj["inputs"]["chamber_pressure_pa"] / (1125.0 * PSI)
    pout_f1 = ei["p_turbine_out_pa"] / PSI
    want_pout = 58.0 * pc_scale
    h_ok = (abs(ei["turbine_pressure_ratio"] - 16.3) / 16.3 < 0.10
            and abs(pout_f1 - want_pout) / want_pout < 0.15 and ei["back_pressure_limited"])
    rows.append((f"(h) F-1 injection back pressure: PR {ei['turbine_pressure_ratio']:.1f} (real 945/58 "
                 f"= 16.3), turbine exit {pout_f1:.1f} psia (real 58 x corpus/real Pc = "
                 f"{want_pout:.1f})", h_ok))

    # (i) F-1 plausibility
    share_f1 = f_inj["cycle_result"]["gg_fraction_of_total"]
    duct_in = f_inj["turbine_exhaust_hardware"]["duct"]["dia_m"] / 0.0254
    t_want = (1138.0 - 32.0) / 1.8 + 273.15
    i_ok = (0.5 * 0.0291 <= share_f1 <= 2.0 * 0.0291
            and abs(ei["t_exhaust_k"] - t_want) / t_want < 0.15
            and 0.7 * 24.0 <= duct_in <= 1.4 * 24.0)
    rows.append((f"(i) F-1 plausibility: GG {share_f1*100:.2f}% of flow (real 2.91%), exhaust "
                 f"{ei['t_exhaust_k']:.0f} K (real {t_want:.0f} K), duct {duct_in:.1f} in (real ~24)",
                 i_ok))

    # (j) gas film
    with open(os.path.join(_CORPUS_DIR, "J-2.json")) as f:
        dj = json.load(f)["design"]
    rj = EngineDesign.from_dict({"schema_version": EngineDesign.SCHEMA_VERSION, "design": dj}).compute()
    gj = rj["turbine_exhaust"]["gas_film"]
    slot_in2 = gj["slot_area_m2"] / 0.0254 ** 2
    gf = ei["gas_film"]
    j_ok = (0.5 * 115.0 <= slot_in2 <= 2.0 * 115.0 and gf is not None and gj is not None
            and 0.0 < gf["eta_exit"] <= te.GAS_FILM_ETA_MAX)
    rows.append((f"(j) gas film: J-2 slot {slot_in2:.0f} in^2 (real eyelets 115), F-1 film "
                 f"{gf['slot_h_m']*1e3:.0f} mm slot, eta at exit {gf['eta_exit']:.2f} "
                 f"(x/S {gf['x_over_s_exit']:.0f}, valid to ~100), Vc/Vg "
                 f"{gf['velocity_ratio_c_over_g']:.2f}", j_ok))

    # (k) scroll manifold
    from .. import manifold as _mf
    mk = f_inj["turbine_exhaust_hardware"]["manifold"]
    inlet_in = 2.0 * mk["inlet_flow_radius_m"] / 0.0254
    te_run = [x for x in f_inj["plumbing_results"] if x["host"] == "turbine_exhaust"][0]
    k_ok = (_mf.ring_is_scroll(mk) and abs(inlet_in - 24.0) / 24.0 < 0.15
            and mk["min_flow_radius_m"] < mk["inlet_flow_radius_m"]
            and te_run["root_tangential"] and not te_run["root_reducer"]
            and f_inj["turbine_exhaust_hardware"]["omega_joint_count"] == 15)
    rows.append((f"(k) scroll manifold: F-1 inlet bore {inlet_in:.1f} in (real 24), tail "
                 f"{2.0 * mk['min_flow_radius_m'] / 0.0254:.1f} in, tangential duct entry, "
                 f"{f_inj['turbine_exhaust_hardware']['omega_joint_count']} omega joints "
                 f"(real 15)", k_ok))

    all_ok = True
    for label, ok in rows:
        all_ok &= bool(ok)
        print(f"  {label}  [{'OK' if ok else '*** FAIL ***'}]")
    print()
    print("ALL TURBINE-EXHAUST CHECKS OK" if all_ok else
          "*** TURBINE-EXHAUST CHECK FAILED - review physics/turbine_exhaust.py ***")
    print("=" * 78)
    return all_ok
