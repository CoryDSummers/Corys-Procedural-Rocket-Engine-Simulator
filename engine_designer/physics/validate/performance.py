"""Propellant-pair Isp spot checks, full-pipeline integration checks and chamber-detail (contraction ratio / residence time / fillets / bell table).

Part of the physics/validate/ package (split verbatim out of the former
single-file validate.py - run the whole suite with
`python3 -m engine_designer.physics.validate`)."""
import numpy as np

from .. import (combustion, expander, geometry, nozzle_shapes, isentropic as iso)
from ..design import EngineDesign
from ._common import INTEGRATION_TOLERANCE_PCT, PA_SEA_LEVEL, TOLERANCE_PCT


SPOT_CHECKS = [
    dict(name="RD-111 (LOX/RP-1, real RO engine)", pair="LOX/RP-1",
         pc_pa=7.85e6, eps=18.0, mr=2.39,
         actual_vac_isp=309.5, actual_sl_isp=268.0, sl_meaningful=True),
    dict(name="RL10A-3-3 (LOX/LH2, real RO engine)", pair="LOX/LH2",
         pc_pa=2.72e6, eps=61.0, mr=5.0,
         actual_vac_isp=442.2, actual_sl_isp=186.0, sl_meaningful=False),
    dict(name="Aestus (N2O4/MMH via MON3, real RO engine)", pair="N2O4/MMH",
         pc_pa=1.1e6, eps=84.0, mr=1.9,
         actual_vac_isp=306.0, actual_sl_isp=113.0, sl_meaningful=False),
    dict(name="AJ10-137 (Aerozine-50/NTO via MON1, real RO engine, Apollo SPS)",
         pair="Aerozine-50/NTO", pc_pa=0.68e6, eps=62.5, mr=1.6,
         actual_vac_isp=314.5, actual_sl_isp=None, sl_meaningful=False),
    dict(name="MR-80B (Hydrazine monopropellant, real RO engine, Mars Landing Engine)",
         pair="Hydrazine", pc_pa=2.4e6, eps=27.2, mr=1.0,
         actual_vac_isp=223.0, actual_sl_isp=79.0, sl_meaningful=False),
    dict(name="Raptor-2 (LOX/CH4, real RO engine, SpaceX FFSC)", pair="LOX/CH4",
         pc_pa=30.0e6, eps=40.0, mr=3.55,
         actual_vac_isp=347.0, actual_sl_isp=326.4, sl_meaningful=False),
    dict(name="Sprite DSpr (H2O2 monopropellant, real RO engine, de Havilland HTP JATO)",
         pair="H2O2", pc_pa=1.0e6, eps=3.0, mr=1.0,
         actual_vac_isp=121.0, actual_sl_isp=95.6, sl_meaningful=False, tol_pct=8.0),
]


def _predict(pair, pc_pa, eps, mr):
    """The design's own performance path at its neutral baseline (80%-bell
    reference nozzle, lambda_relative = 1, no injector multiplier / completeness):
    combustion.performance_state (equilibrium tables at the actual MR and Pc for
    a bipropellant, the legacy table for a monopropellant) x DEFAULT_ETA_CSTAR
    on c*, x ETA_CF on the ideal CF (P1 re-anchor, 2026-09-25)."""
    st = combustion.performance_state(pair, mr, pc_pa)
    tc, gamma = st["tc_k"], st["gamma_chamber"]
    eta_cstar = combustion.DEFAULT_ETA_CSTAR[pair]
    pe_pa = combustion.exit_pressure_ratio(pair, mr, pc_pa, eps, st) * pc_pa
    cstar = st["cstar_ideal_ms"] * eta_cstar
    cf_vac = combustion.cf_vac_ideal(pair, mr, pc_pa, eps, st)[0] * combustion.ETA_CF[pair]
    cf_sl = cf_vac - eps * (PA_SEA_LEVEL / pc_pa)
    isp_vac = iso.isp_from_cf(cstar, cf_vac)
    isp_sl = iso.isp_from_cf(cstar, cf_sl)
    separated = iso.is_separated(pe_pa, PA_SEA_LEVEL)
    return tc, gamma, eta_cstar, isp_vac, isp_sl, separated


def solve_eta_cf(check):
    """ETA_CF that makes `check`'s _predict hit its real vacuum Isp (Isp is
    linear in ETA_CF on this path) - how combustion.ETA_CF is reverse-solved."""
    saved = combustion.ETA_CF[check["pair"]]
    try:
        combustion.ETA_CF[check["pair"]] = 1.0
        isp1 = _predict(check["pair"], check["pc_pa"], check["eps"], check["mr"])[3]
    finally:
        combustion.ETA_CF[check["pair"]] = saved
    return check["actual_vac_isp"] / isp1


def run():
    print("=" * 78)
    print(f"PROPELLANT-PAIR SPOT CHECKS (tolerance {TOLERANCE_PCT}%, vac Isp gates pass/fail;")
    print("sl Isp is gated only when the nozzle is actually attached at sea level)")
    print("=" * 78)
    all_ok = True
    for check in SPOT_CHECKS:
        tol = check.get("tol_pct", TOLERANCE_PCT)   # per-row loosening (Sprite: Pc is a guess in the source)
        tc, gamma, eta_cstar, isp_vac, isp_sl, separated = _predict(
            check["pair"], check["pc_pa"], check["eps"], check["mr"])
        err_vac = (isp_vac - check["actual_vac_isp"]) / check["actual_vac_isp"] * 100
        vac_ok = abs(err_vac) <= tol
        ok = vac_ok
        if check["sl_meaningful"]:
            err_sl = (isp_sl - check["actual_sl_isp"]) / check["actual_sl_isp"] * 100
            ok = ok and abs(err_sl) <= tol
        all_ok &= ok
        status = "OK" if ok else "*** OUT OF TOLERANCE ***"
        print(f"\n{check['name']}  [{status}]")
        print(f"  Pc={check['pc_pa']/1e6:.2f} MPa  eps={check['eps']}  MR={check['mr']}  "
              f"eta_cstar={eta_cstar}  eta_CF={combustion.ETA_CF[check['pair']]:.4f}  "
              f"-> Tc={tc:.0f} K, gamma={gamma:.4f}")
        print(f"  vac Isp: predicted {isp_vac:6.1f} s  actual {check['actual_vac_isp']:6.1f} s  "
              f"err {err_vac:+.2f}%  [{'OK' if vac_ok else 'FAIL'}]")
        if check["sl_meaningful"]:
            err_sl = (isp_sl - check["actual_sl_isp"]) / check["actual_sl_isp"] * 100
            print(f"  sl  Isp: predicted {isp_sl:6.1f} s  actual {check['actual_sl_isp']:6.1f} s  "
                  f"err {err_sl:+.2f}%  [gated]")
        else:
            sl_display = f"{isp_sl:.1f} s" if isp_sl > 0 else "unphysical (deeply separated)"
            actual_sl = check["actual_sl_isp"]
            actual_sl_display = f"{actual_sl:.0f} s" if actual_sl is not None else "not quoted for this engine"
            print(f"  sl  Isp: model gives {sl_display} (informational only, NOT gated - this "
                  f"nozzle is separated at sea level per Pe/Pa criterion; real engine's "
                  f"{actual_sl_display} is itself an RPA-nominal, not-achieved figure)")
    print()
    print("=" * 78)
    print("ALL GATED SPOT CHECKS WITHIN TOLERANCE" if all_ok else
          "*** ONE OR MORE GATED SPOT CHECKS OUT OF TOLERANCE - review DEFAULT_ETA_CSTAR / ETA_CF / tables ***")
    print("=" * 78)
    return all_ok


def run_integration_checks():
    """
    Reproduce the same three real engines through the FULL EngineDesign.compute()
    pipeline (Bell @ 80% length - the reference nozzle - and the impinging
    injector, both defined as neutral baselines matching what _predict() above
    implicitly assumes) instead of the isolated formula _predict() uses.

    This is the check that would have caught the nozzle-divergence-efficiency
    double-counting bug (found via a user comparing a real LMDE reproduction):
    before the fix, this came out ~1.6% low for every design, not just LMDE's
    (which showed a larger ~7% gap because the same effect stacked with an
    injector multiplier). Pressure-fed is used here specifically to isolate
    the nozzle/combustion path from cycle-specific turbopump math.
    """
    print()
    print("=" * 78)
    print(f"INTEGRATION-LEVEL CHECK (tolerance {INTEGRATION_TOLERANCE_PCT}%): same three engines, "
          "through the FULL EngineDesign.compute() pipeline, Bell@80%/impinging")
    print("=" * 78)
    all_ok = True
    for check in SPOT_CHECKS:
        d = EngineDesign(propellant_pair=check["pair"], mixture_ratio=check["mr"],
                          chamber_pressure_pa=check["pc_pa"], expansion_ratio=check["eps"],
                          nozzle_type="bell", bell_percent_length=80.0,
                          cycle="pressure_fed", injector_type="impinging",
                          target_vac_thrust_n=100_000.0)
        r = d.compute()
        err = (r["isp_vac_engine_s"] - check["actual_vac_isp"]) / check["actual_vac_isp"] * 100
        tol = check.get("tol_pct", INTEGRATION_TOLERANCE_PCT)
        ok = abs(err) <= tol
        all_ok &= ok
        print(f"  {check['name']:<45} predicted {r['isp_vac_engine_s']:6.1f} s  "
              f"actual {check['actual_vac_isp']:6.1f} s  err {err:+.2f}%  "
              f"[{'OK' if ok else 'FAIL'}]")
    print()
    print("ALL INTEGRATION CHECKS WITHIN TOLERANCE" if all_ok else
          "*** ONE OR MORE INTEGRATION CHECKS OUT OF TOLERANCE - the nozzle-efficiency-vs-"
          "reference wiring in design.py may be broken again ***")
    print("=" * 78)
    return all_ok


def run_chamber_detail_check():
    """
    C1/C2/C3 - finite-contraction-ratio chamber flow, per-pair L* defaults +
    stay-time / L-over-D checks, and the throat fillet's effect on the contour.
    C4/C5/C6 - the residence-time chamber sizing method, the cylinder->cone wall
    fillet, and the Rao bell-angle table vs real engine bells.
    All are warn-not-block in design.py; this pins the numbers against
    [Sutton Table 5-4] / [Huzel Table 4-1] / [Sutton Fig 3-14].
    """
    print()
    print("=" * 78)
    print("CHAMBER-DETAIL SPOT CHECK (C1 Pc loss / C2 L* / C3 throat fillet / "
          "C4 residence time / C5 wall fillet / C6 bell table)")
    print("=" * 78)
    all_ok = True

    # C1: tight vs loose contraction ratio.
    tight = combustion.chamber_flow(1.6, 1.20)
    loose = combustion.chamber_flow(4.0, 1.20)
    c1_ok = (0.34 < tight["mach"] < 0.46
             and 0.05 < tight["pc_loss_fraction"] < 0.12
             and loose["pc_loss_fraction"] < 0.02)
    # feeding it in raises pump discharge but not the NOZZLE's Isp (the chamber
    # Isp - the engine Isp legitimately moves with the extra GG dump flow)
    base = EngineDesign(cycle="gas_generator", contraction_ratio=1.5).compute()
    lossy = EngineDesign(cycle="gas_generator", contraction_ratio=1.5,
                          apply_chamber_pressure_loss=True).compute()
    c1_feed_ok = (lossy["cycle_result"]["turbopump"]["power_total_w"]
                  > base["cycle_result"]["turbopump"]["power_total_w"]
                  and abs(lossy["isp_vac_chamber_s"] - base["isp_vac_chamber_s"]) < 0.5)
    all_ok &= c1_ok and c1_feed_ok
    print(f"\nC1 injector-end Pc loss  [{'OK' if c1_ok and c1_feed_ok else '*** FAIL ***'}]")
    print(f"  CR 1.6: Mc {tight['mach']:.2f}, {tight['pc_loss_fraction']*100:.0f}% loss; "
          f"CR 4.0: {loose['pc_loss_fraction']*100:.1f}%   [{'OK' if c1_ok else 'FAIL'}]")
    print(f"  apply_chamber_pressure_loss raises pump power, leaves Isp   "
          f"[{'OK' if c1_feed_ok else 'FAIL'}]")

    # C2: L* defaults + stay time + L/D.
    c2_ok = (combustion.l_star_default_for_pair("LOX/RP-1") == 1.10
             and combustion.l_star_default_for_pair("LOX/LH2") == 0.75)
    r = EngineDesign(cycle="gas_generator").compute()
    st_ok = 0.0005 <= r["stay_time_s"] <= 0.060
    long_narrow = EngineDesign(cycle="gas_generator", lstar_m=3.0, contraction_ratio=1.3).compute()
    ld_row = next(c for c in long_narrow["checklist"]
                  if c["name"] == "Chamber cylindrical L/D reasonable")
    all_ok &= c2_ok and st_ok
    print(f"\nC2 L* defaults + stay time + L/D  [{'OK' if c2_ok and st_ok else '*** FAIL ***'}]")
    print(f"  l_star_default_for_pair LOX/RP-1 1.10 / LOX/LH2 0.75   [{'OK' if c2_ok else 'FAIL'}]")
    print(f"  default design stay time {r['stay_time_s']*1e3:.1f} ms   [{'OK' if st_ok else 'FAIL'}]")
    print(f"  long/narrow chamber L/D {long_narrow['chamber_l_over_d']:.2f} -> "
          f"check {'WARNS' if not ld_row['passed'] else 'passes'}")

    # C3: throat fillet + convergent-angle slider.
    xs20, rs20, _, _ = geometry.convergent_profile(0.4, 0.2, 0.3, 20.0)
    xs40, rs40, _, _ = geometry.convergent_profile(0.4, 0.2, 0.3, 40.0)
    c3_ok = (len(xs20) >= 8 and abs(rs20[-1] - 0.1) < 1e-9      # fillet points, ends at rt
             and (xs20[-1] - xs20[1]) > (xs40[-1] - xs40[1]))   # 20 deg -> longer cone
    all_ok &= c3_ok
    print(f"\nC3 throat fillet + convergent angle  [{'OK' if c3_ok else '*** FAIL ***'}]")
    print(f"  convergent_profile has {len(xs20)} pts, ends exactly at the throat; "
          f"20 deg cone is longer than 40 deg   [{'OK' if c3_ok else 'FAIL'}]")

    # C4: the residence-time sizing method reproduces the L* method when fed the
    # stay time implied by the pair's L* default (they're the same knob).
    c4_ok = True
    c4_rows = []
    for pair in ("LOX/RP-1", "LOX/LH2", "LOX/CH4", "N2O4/MMH"):
        ls = combustion.l_star_default_for_pair(pair)
        a = EngineDesign(cycle="gas_generator", propellant_pair=pair, lstar_m=ls).compute()["geometry"]
        b = EngineDesign(cycle="gas_generator", propellant_pair=pair,
                          chamber_sizing_method="residence_time").compute()["geometry"]
        ratio = b["chamber_volume_m3"] / a["chamber_volume_m3"] if a["chamber_volume_m3"] else 0.0
        row_ok = 0.90 <= ratio <= 1.10 and abs(b["implied_lstar_m"] - ls) < 0.02
        c4_ok &= row_ok
        c4_rows.append((pair, ratio, b["implied_lstar_m"], ls, row_ok))
    all_ok &= c4_ok
    print(f"\nC4 residence-time sizing method  [{'OK' if c4_ok else '*** FAIL ***'}]")
    for pair, ratio, impl, ls, row_ok in c4_rows:
        print(f"  {pair:10s} RT-Vc / L*-Vc = {ratio:.4f}  implied L* {impl:.3f} (default {ls})  "
              f"[{'OK' if row_ok else 'FAIL'}]")

    # C5: the cylinder->convergent wall fillet takes gas volume out of the cone,
    # so at fixed Vc the cylindrical section lengthens; wetted (cooled) area
    # barely moves and the cooling model stays green.
    nf = EngineDesign(cycle="gas_generator", nozzle_type="bell").compute()
    wf = EngineDesign(cycle="gas_generator", nozzle_type="bell",
                       chamber_wall_fillet_r_over_rt=1.5).compute()
    area_nf = expander.cooled_surface_area(nf["profile_xs_m"], nf["profile_rs_m"],
                                            nf["geometry"]["throat_dia_m"], cutoff_area_ratio=6.0)
    area_wf = expander.cooled_surface_area(wf["profile_xs_m"], wf["profile_rs_m"],
                                            wf["geometry"]["throat_dia_m"], cutoff_area_ratio=6.0)
    area_move = abs(area_wf - area_nf) / area_nf if area_nf else 1.0
    id0 = EngineDesign(cycle="gas_generator").compute()
    id1 = EngineDesign(cycle="gas_generator", chamber_wall_fillet_r_over_rt=1.5).compute()
    c5_identical_at_zero = (np.array_equal(id0["profile_xs_m"],
                                           EngineDesign(cycle="gas_generator",
                                                        chamber_wall_fillet_r_over_rt=0.0).compute()["profile_xs_m"]))
    c5_ok = (wf["geometry"]["chamber_length_m"] > nf["geometry"]["chamber_length_m"]
             and area_move < 0.05
             and id1["cooling"]["q_throat_w_m2"] > 0
             and c5_identical_at_zero)
    all_ok &= c5_ok
    print(f"\nC5 cylinder->cone wall fillet  [{'OK' if c5_ok else '*** FAIL ***'}]")
    print(f"  chamber length {nf['geometry']['chamber_length_m']*1e3:.2f} -> "
          f"{wf['geometry']['chamber_length_m']*1e3:.2f} mm (longer),  cooled area moves "
          f"{area_move*100:.2f}% (<5%),  fillet=0 profile bit-identical: {c5_identical_at_zero}   "
          f"[{'OK' if c5_ok else 'FAIL'}]")

    # C6: the Rao bell-angle table (Sutton Fig 3-14) read against real ~80%
    # engine bells, +/-3 deg; the assembled bell contour carries the throat
    # fillet and starts exactly at the throat.
    c6_ok = True
    c6_rows = []
    for name, eps, tn_ref, te_ref in [("F-1", 16.0, 33.0, 11.0),
                                       ("J-2", 27.5, 35.5, 9.5),
                                       ("RS-25", 69.0, 37.5, 7.0)]:
        tn_i, te_i = nozzle_shapes.bell_angles(eps, 80.0)
        row_ok = abs(tn_i - tn_ref) <= 3.0 and abs(te_i - te_ref) <= 3.0
        c6_ok &= row_ok
        c6_rows.append((name, eps, tn_i, tn_ref, te_i, te_ref, row_ok))
    bell = EngineDesign(cycle="gas_generator", nozzle_type="bell", bell_percent_length=80.0,
                         expansion_ratio=25.0).compute()
    bxs, brs = bell["profile_xs_m"], bell["profile_rs_m"]
    thr_i = int(np.argmin(brs))
    dt = bell["geometry"]["throat_dia_m"]
    n_skirt = sum(1 for i in range(thr_i, len(brs))
                  if (brs[i] / (dt / 2.0)) ** 2 <= 1.0 + (0.1 * bell["profile_meta"]["divergent_length_m"] / dt))
    c6_contour_ok = abs(brs[thr_i] - dt / 2.0) < 1e-9 and n_skirt >= 5
    c6_ok &= c6_contour_ok
    all_ok &= c6_ok
    print(f"\nC6 Rao bell table + skirt fillet  [{'OK' if c6_ok else '*** FAIL ***'}]")
    for name, eps, tn_i, tn_ref, te_i, te_ref, row_ok in c6_rows:
        print(f"  {name:6s} eps {eps:4.1f}: theta_n {tn_i:.1f} (~{tn_ref}) / theta_e {te_i:.1f} "
              f"(~{te_ref})   [{'OK' if row_ok else 'FAIL'}]")
    print(f"  assembled bell: {n_skirt} pts in the throat-fillet region, throat radius exact   "
          f"[{'OK' if c6_contour_ok else 'FAIL'}]")

    print()
    print("ALL CHAMBER-DETAIL CHECKS OK" if all_ok else
          "*** CHAMBER-DETAIL CHECK FAILED - review combustion.py / geometry.py / design.py ***")
    print("=" * 78)
    return all_ok
