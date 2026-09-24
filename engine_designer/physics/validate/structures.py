"""Mass-model sensitivity, jacket overpressure (plausibility + Huzel sample calc) and hatband plausibility.

Part of the physics/validate/ package (split verbatim out of the former
single-file validate.py - run the whole suite with
`python3 -m engine_designer.physics.validate`)."""
import math

import numpy as np

from .. import (cycles, geometry, mass_model, materials)
from ..design import EngineDesign


def run_mass_model_sensitivity_check():
    """
    New: chamber/nozzle wall mass now comes from a real thin-wall pressure-
    vessel hoop-stress formula (physics/mass_model.py) - a higher chamber
    pressure or a weaker (lower allowable_stress_pa) material should both
    give a thicker, heavier wall. Also checks the ablative rated-burn-time
    coupling (higher consumption rate -> shorter rated burn, since the same
    chamber wall thickness is consumed faster) and the non-ablative
    margin-driven rated-burn-time scaling (checked at its own reference
    point, materials.THIN_MARGIN_THRESHOLD, where the multiplier must be
    exactly 1.0 by construction).
    """
    print()
    print("=" * 78)
    print("MASS MODEL / RATED-BURN-TIME SENSITIVITY CHECK")
    print("=" * 78)
    base = dict(propellant_pair="LOX/RP-1", mixture_ratio=2.34, expansion_ratio=14.0,
                cycle="gas_generator", injector_type="impinging", target_vac_thrust_n=500_000.0)

    # Tested directly against mass_model.wall_thickness_m (holding radius fixed), NOT through
    # the full EngineDesign pipeline: at a FIXED target thrust, raising Pc also shrinks the
    # whole chamber (At = mdot*cstar/Pc, so radius falls as ~1/sqrt(Pc)) - a real, already-
    # existing effect of this tool's geometry sizing. That shrinkage can outweigh the thicker
    # wall higher Pc demands, so whole-engine wall mass vs. Pc at fixed thrust is NOT
    # guaranteed to be monotonic (confirmed empirically: it actually decreases here) - that's
    # a real emergent consequence of already-existing physics, not a bug in the new hoop-
    # stress formula. The formula itself, at a fixed radius, must still be monotonic in Pc.
    thicknesses = [mass_model.wall_thickness_m(pc, 0.3, 110e6) for pc in (4.0e6, 8.0e6, 16.0e6)]
    ok_mass_vs_pc = thicknesses[0] < thicknesses[1] < thicknesses[2]
    print(f"  wall_thickness_m strictly increases with Pc at fixed radius (4/8/16 MPa): "
          f"{thicknesses[0]*1000:.1f} -> {thicknesses[1]*1000:.1f} -> {thicknesses[2]*1000:.1f} mm  "
          f"[{'OK' if ok_mass_vs_pc else 'FAIL'}]")

    d_weak = EngineDesign(material_key="stainless_steel", **base)   # lower allowable_stress_pa
    d_strong = EngineDesign(material_key="niobium_c103", **base)    # higher allowable_stress_pa
    mass_weak = d_weak.compute()["chamber_wall_mass_kg"]
    mass_strong = d_strong.compute()["chamber_wall_mass_kg"]
    assert materials.MATERIALS["stainless_steel"].allowable_stress_pa < \
        materials.MATERIALS["niobium_c103"].allowable_stress_pa
    ok_mass_vs_stress = mass_weak > mass_strong
    print(f"  Weaker material (lower allowable_stress_pa) gives a heavier wall at the same Pc: "
          f"stainless {mass_weak:.1f} kg > niobium {mass_strong:.1f} kg  "
          f"[{'OK' if ok_mass_vs_stress else 'FAIL'}]")

    rates = []
    for rate in (1.0e-4, 2.0e-4, 4.0e-4):
        d = EngineDesign(material_key="ablative_phenolic", **base)
        wall_t = mass_model.wall_thickness_m(
            d.chamber_pressure_pa,
            geometry.chamber_geometry(1.0, 1500.0, d.chamber_pressure_pa, d.expansion_ratio,
                                       d.lstar_m, d.contraction_ratio)["chamber_dia_m"] / 2.0,
            materials.MATERIALS["ablative_phenolic"].allowable_stress_pa)
        rates.append(mass_model.ablative_rated_burn_time_s(wall_t, rate))
    ok_ablative_rate = rates[0] > rates[1] > rates[2]
    print(f"  Ablative rated burn time strictly decreases as consumption rate rises: "
          f"{rates[0]:.0f} -> {rates[1]:.0f} -> {rates[2]:.0f} s  [{'OK' if ok_ablative_rate else 'FAIL'}]")

    d_ref = EngineDesign(material_key="narloy_z", **base)
    r_ref = d_ref.compute()
    # 2026-09-23: burn time scales with the WORST of the throat and full-length
    # peak margins (the throat alone used to set it - cooling audit W7).
    _worst = min(r_ref["material_margin"]["margin_ratio"],
                 r_ref["cooling"]["peak_wall_margin_ratio"] or float("inf"))
    ref_mult = _worst / materials.THIN_MARGIN_THRESHOLD
    ref_mult_clamped = max(0.3, min(3.0, ref_mult))
    expected_rated = 200.0 * ref_mult_clamped
    ok_rated_matches = abs(r_ref["rated_burn_time_s"] - expected_rated) < 1e-6
    print(f"  Non-ablative rated burn time matches the margin-scaled formula exactly: "
          f"{r_ref['rated_burn_time_s']:.2f} == {expected_rated:.2f} s  "
          f"[{'OK' if ok_rated_matches else 'FAIL'}]")

    all_ok = ok_mass_vs_pc and ok_mass_vs_stress and ok_ablative_rate and ok_rated_matches
    print("ALL MASS MODEL SENSITIVITY CHECKS OK" if all_ok else
          "*** MASS MODEL SENSITIVITY CHECK FAILED ***")
    print("=" * 78)
    return all_ok


def run_jacket_overpressure_check():
    """
    PLAUSIBILITY check only for design.py's jacket/coolant-overpressure-vs-
    channel-wall structural-margin flag ("channels" regen mode only) - NOT a
    validated spot check against a real engine (no citable real-engine
    channel-wall reversed-pressure failure/success data exists in claude_lit
    to calibrate a pass/fail threshold against - see ASSUMPTIONS.md). This
    only asserts:
      (1) a near-throat-only cooled length (worst station close to the
          throat, where local gas pressure is still high) does NOT trip it,
      (2) pushing the cooled length + Pc up DOES trip it, and
      (3) the reported jacket-vs-local-gas differential is MONOTONIC as the
          cooled length is pushed further downstream - the physics should
          only get worse, never flip back non-monotonically.
    Trust the DIRECTION this pins, not the threshold.
    """
    print()
    print("=" * 78)
    print("JACKET/COOLANT OVERPRESSURE PLAUSIBILITY CHECK (design.py, \"channels\" "
          "regen mode - NOT a validated spot check, see docstring)")
    print("=" * 78)

    def _design(cooling_transition_eps, chamber_pressure_pa=8.0e6):
        d = EngineDesign(regen_channel_model="channels",
                          cooling_transition_eps=cooling_transition_eps,
                          chamber_pressure_pa=chamber_pressure_pa)
        return d.compute()

    modest = _design(cooling_transition_eps=1.5)
    modest_ok = modest["jacket_overpressure_ok"]
    print(f"\nNear-throat cutoff (eps~1.5): ok={modest_ok}   [{'OK' if modest_ok else 'FAIL'}]")

    extreme = _design(cooling_transition_eps=14.0, chamber_pressure_pa=3.0e7)
    extreme_ok = extreme["jacket_overpressure_ok"]
    print(f"Deep + high-Pc cutoff (eps~14, Pc 30 MPa): ok={extreme_ok}   "
          f"[{'OK' if not extreme_ok else 'FAIL'}]")

    sweep_eps = [1.5, 3.0, 6.0, 10.0, 14.0]
    prev_dp = None
    mono_ok = True
    for eps in sweep_eps:
        r = _design(cooling_transition_eps=eps, chamber_pressure_pa=2.0e7)
        net_dp = (r["jacket_pressure_at_worst_station_pa"]
                  - r["jacket_local_gas_pressure_at_worst_station_pa"])
        if prev_dp is not None and net_dp < prev_dp - 1.0:
            mono_ok = False
        print(f"  cooled to eps={eps:5.1f}: net differential {net_dp/1e6:6.2f} MPa   "
              f"[{'OK' if mono_ok else 'FAIL'}]")
        prev_dp = net_dp

    all_ok = modest_ok and (not extreme_ok) and mono_ok
    print()
    print("ALL JACKET-OVERPRESSURE PLAUSIBILITY CHECKS OK" if all_ok else
          "*** JACKET-OVERPRESSURE CHECK FAILED - review physics/design.py's jacket "
          "overpressure block ***")
    print("=" * 78)
    return all_ok


def run_jacket_overpressure_sample_calc_check():
    """
    REAL-ENGINE spot check for the tube_wall/coax_shell combined-stress
    formula (mass_model.hoop_stress_pa + mass_model.thermal_stress_pa, used
    by design.py's jacket-overpressure block for those two constructions) -
    unlike run_jacket_overpressure_check() above, this is NOT a plausibility-
    only check: it reproduces `[Huzel Sample Calculation 4-4]`'s real A-1
    (LOX/RP-1, Pc 1000 psia) and A-2 (LOX/LH2, Pc 800 psia) circular-tube
    numbers at the throat directly.

    PARTIAL/ADAPTED, not literal: this calls the two low-level mass_model
    functions directly with Huzel's own real d/t/N/Pco/Pg/material numbers
    (no EngineDesign/full-engine compute involved) and confirms the resulting
    combined (hoop + thermal-restraint) stress lands close to Huzel's own
    stated pre-M_A figures (~52,500 psi A-1, ~68,750 psi A-2). This ONLY
    confirms the FORMULA IMPLEMENTATION reproduces real published numbers -
    it does NOT confirm the tool's own auto-sized tube geometry would
    reproduce A-1/A-2 end-to-end (this tool never solves for d/t/N from a
    target velocity + structural constraint the way Huzel's worked example
    does - see design.py's own jacket-overpressure warning text, which
    flags wall thickness as still the tool's generic Pc-derived sizing, not
    a construction-specific one).

    All inputs kept in Huzel's own units (psi, in, Btu/in^2-sec, deg F) -
    hoop_stress_pa/thermal_stress_pa are pure algebraic ratios with no
    embedded unit constants, so any consistent unit system works and this
    avoids a US-to-SI conversion step that could itself introduce error.
    """
    print()
    print("=" * 78)
    print("JACKET-OVERPRESSURE REAL-ENGINE SPOT CHECK (Huzel Sample Calc 4-4, "
          "A-1/A-2 tube-wall numbers at the throat)")
    print("=" * 78)

    def _combined_psi(pco_psi, pg_psi, r_in, t_in, q_btu_in2_sec, e_psi, alpha_per_f,
                       k_btu_in2_sec_f_per_in, nu=0.35):
        hoop = mass_model.hoop_stress_pa(pco_psi - pg_psi, r_in, t_in)
        dt_f = q_btu_in2_sec * t_in / k_btu_in2_sec_f_per_in
        thermal = mass_model.thermal_stress_pa(dt_f, e_psi, alpha_per_f, nu=nu)
        return hoop, thermal, hoop + thermal

    tol_pct = 2.0
    # design.py's tube_wall sizing (mass_model.min_combined_stress_thickness_m,
    # 2026-09-23) - PLAUSIBILITY only: Huzel's real tube gauge must sit inside
    # the feasible window (both roots of K*t^2 - F_ty*t + dP*r = 0) and the
    # tool's sized t within SIZED_T_TOL_PCT of it. Does NOT show the tool's own
    # auto-sized d/N would reproduce A-1/A-2 end to end. A-2's sized t lands on
    # TUBE_WALL_MIN_THICKNESS_M, which was taken FROM A-2 - circular; A-1 is the
    # independent one (its t* is an unclamped optimum).
    sized_t_tol_pct = 30.0
    t_floor_in = mass_model.TUBE_WALL_MIN_THICKNESS_M / 0.0254
    all_ok = True
    for name, pco, pg, d_in, t_in, q, e, alpha, k, huzel_combined_psi, f_ty_psi in [
        ("A-1 (LOX/RP-1, Pc 1000 psia)", 1500.0, 562.0, 0.855, 0.020, 3.00,
         28.0e6, 8.0e-6, 3.19e-4, 52500.0, 82000.0),
        ("A-2 (LOX/LH2, Pc 800 psia)", 1200.0, 443.0, 0.185, 0.008, 19.10,
         24.0e6, 8.2e-6, 3.86e-4, 68750.0, 81000.0),
    ]:
        hoop, thermal, combined = _combined_psi(pco, pg, d_in / 2.0, t_in, q, e, alpha, k)
        err_pct = abs(combined - huzel_combined_psi) / huzel_combined_psi * 100.0
        ok = err_pct <= tol_pct
        print(f"\n{name}")
        print(f"  hoop {hoop:,.0f} + thermal {thermal:,.0f} = {combined:,.0f} psi   "
              f"(Huzel: {huzel_combined_psi:,.0f} psi, {err_pct:.2f}% error)   "
              f"[{'OK' if ok else 'FAIL'}]")

        k_per_in = thermal / t_in
        dp_r = (pco - pg) * d_in / 2.0
        disc = f_ty_psi ** 2 - 4.0 * k_per_in * dp_r
        t_lo = (f_ty_psi - math.sqrt(disc)) / (2.0 * k_per_in) if disc > 0 else float("nan")
        t_hi = (f_ty_psi + math.sqrt(disc)) / (2.0 * k_per_in) if disc > 0 else float("nan")
        window_ok = disc > 0 and t_lo <= t_in <= t_hi
        t_sized, _limit = mass_model.min_combined_stress_thickness_m(
            pco - pg, d_in / 2.0, k_per_in, t_floor_in, 1.0)
        sized_err_pct = abs(t_sized - t_in) / t_in * 100.0
        sized_ok = sized_err_pct <= sized_t_tol_pct
        print(f"  feasible t window [{t_lo:.4f}, {t_hi:.4f}] in contains Huzel's {t_in:.3f} in   "
              f"[{'OK' if window_ok else 'FAIL'}]")
        print(f"  tool-sized t {t_sized:.4f} in ({_limit}) vs Huzel {t_in:.3f} in, "
              f"{sized_err_pct:.0f}% (tol {sized_t_tol_pct:.0f}%)   [{'OK' if sized_ok else 'FAIL'}]")
        # What design.py's row now gates on (2026-09-24): PRIMARY hoop vs
        # allowable/SF; the thermal-restraint term is secondary (fatigue).
        # Huzel's real tube carries its hoop load with margin, and his own
        # elastic rule (combined <= F_ty, no SF) holds for his sample.
        primary_ok = hoop <= f_ty_psi / mass_model.SAFETY_FACTOR
        huzel_rule_ok = combined <= f_ty_psi
        print(f"  primary hoop {hoop:,.0f} psi <= F_ty/SF {f_ty_psi / mass_model.SAFETY_FACTOR:,.0f} psi   "
              f"[{'OK' if primary_ok else 'FAIL'}];  Huzel's elastic rule combined <= F_ty "
              f"{f_ty_psi:,.0f} psi   [{'OK' if huzel_rule_ok else 'FAIL'}]")
        all_ok = all_ok and ok and window_ok and sized_ok and primary_ok and huzel_rule_ok

    # Real tube-wall engines from the validation corpus must NOT trip the
    # structural row (convention #1: every one of them did while the row held
    # hoop + thermal-restraint to allowable/SF - F-1 423 vs 133 MPa, J-2 990 vs
    # 67, RL10 761 vs 67). A coax_shell J-2 (full-radius hoop lever) must still
    # trip it, so the row is not simply disabled.
    import os
    from ...gui.project_io import load_design
    eng_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), "validation_engines", "engines")
    print()
    for name in ("F-1", "J-2", "RL10A-3-3"):
        d = load_design(os.path.join(eng_dir, f"{name}.json"))
        r = d.compute()
        eng_ok = bool(r["jacket_overpressure_ok"]) and d.wall_construction == "tube_wall"
        print(f"  real {name} (tube_wall): structural row passes, governing station "
              f"{r['jacket_overpressure_worst_station']}: hoop "
              f"~{r['jacket_hoop_stress_pa']/1e6:.0f} MPa, thermal-restraint "
              f"~{r['jacket_thermal_stress_pa']/1e6:.0f} MPa (secondary)   "
              f"[{'OK' if eng_ok else 'FAIL'}]")
        all_ok = all_ok and eng_ok
    d = load_design(os.path.join(eng_dir, "J-2.json"))
    d.wall_construction = "coax_shell"
    r = d.compute()
    coax_trips = not bool(r["jacket_overpressure_ok"])
    print(f"  J-2 rebuilt as coax_shell: hoop ~{r['jacket_hoop_stress_pa']/1e6:.0f} MPa "
          f"trips the row   [{'OK' if coax_trips else 'FAIL'}]")
    all_ok = all_ok and coax_trips

    print()
    print("ALL JACKET-OVERPRESSURE SAMPLE-CALC SPOT CHECKS OK" if all_ok else
          "*** JACKET-OVERPRESSURE SAMPLE-CALC CHECK FAILED - review "
          "mass_model.hoop_stress_pa/thermal_stress_pa ***")
    print("=" * 78)
    return all_ok


def run_hatband_plausibility_check():
    """
    PLAUSIBILITY check (NOT a validated spot check - no dimensioned retaining-band
    data exists in the literature set; SP-8120 gives criteria, not sizes) for the
    structural hatbands (physics/hatbands.py) and the swaged-tube taper advisory
    (design.py, SP-8087 Sec.2.1.1.3). On an F-1-class LOX/RP-1 tube-wall design
    (7 MPa, eps 16, 6.77 MN, whole bell regen-cooled) it asserts the qualitative
    behaviour SP-8120 describes:
      (1) a continuous shell just aft of the throat, then >= 3 bands, all passing
          hoop (bands carry ALL hoop load) and ring buckling;
      (2) spacing widens downstream while the wall is above ambient pressure
          (tube span grows as wall pressure falls);
      (3) "auto" picks flat straps near the throat and a stiffer section at the
          overexpanded (sea-level) exit (SP-8120 Fig. 40 practice);
      (4) band mass is a small, non-zero fraction of dry mass;
      (5) a vacuum-only nozzle (separated at sea level) needs flat straps only;
      (6) an eps-40 fully-cooled single tube count trips the >6:1 taper warning
          and a tube bifurcation clears it;
      (7) bands off -> no band result, no band mass (default designs unchanged).
    """
    print()
    print("=" * 78)
    print("HATBAND / TUBE-TAPER PLAUSIBILITY CHECK (hatbands.py - NOT a validated "
          "spot check, see docstring)")
    print("=" * 78)

    def _run(**kw):
        base = dict(propellant_pair="LOX/RP-1", mixture_ratio=2.34, chamber_pressure_pa=7.0e6,
                    expansion_ratio=16, nozzle_type="bell", bell_percent_length=80.0,
                    cycle=cycles.GAS_GENERATOR, target_vac_thrust_n=6_770_000,
                    wall_construction="tube_wall", material_key="inconel_718",
                    bell_material_key="inconel_718", cooling_transition_eps=16.0,
                    tube_hatbands=True)
        base.update(kw)
        return EngineDesign(**base).compute()

    checks = []
    r = _run()
    hb = r["cooling"]["hatbands"]
    bands = hb["bands"]
    for b in bands:
        print(f"  eps {b['local_eps']:5.1f}  {b['shape']:7s} w {b['width_m'] * 1e3:5.0f} mm  "
              f"t {b['gauge_m'] * 1e3:5.1f} mm  p_wall {b['p_wall_pa'] / 1e3:6.0f} kPa  "
              f"hoop x{b['hoop_margin']:.2f}  buckle x{min(b['buckling_margin'], 99):.2f}  "
              f"{b['mass_kg']:6.1f} kg")
    checks.append(("continuous shell aft of throat, then >=3 passing bands",
                   hb["shell_end_x_m"] > hb["shell_start_x_m"] and len(bands) >= 3
                   and hb["all_ok"]))
    above = [b["x_m"] for b in bands if b["p_wall_pa"] > 101325.0]
    gaps = np.diff([hb["shell_end_x_m"]] + above)
    checks.append(("spacing widens downstream while p_wall > p_amb",
                   len(gaps) < 2 or bool(np.all(np.diff(gaps) > -1e-9))))
    checks.append(("auto: flat near throat, stiffer at overexpanded exit",
                   bands[0]["shape"] == "flat" and bands[-1]["shape"] != "flat"))
    frac = r["hatband_mass_kg"] / max(r["computed_dry_mass_kg"], 1e-9)
    checks.append((f"band mass a small fraction of dry ({100 * frac:.1f}%)", 0.0 < frac < 0.10))
    rv = _run(expansion_ratio=40, cooling_transition_eps=40.0)
    checks.append(("vacuum-only nozzle: flat straps only",
                   rv["cooling"]["hatbands"]["shapes_used"] == ["flat"]))
    taper_warn = any("taper" in w for w in rv["warnings"])
    rs = _run(expansion_ratio=40, cooling_transition_eps=40.0, tube_split_eps=8.0)
    split_clears = not any("taper" in w for w in rs["warnings"])
    checks.append((f"eps-40 taper {rv['cooling']['tube_taper_ratio']:.1f}:1 warns, "
                   f"split -> {rs['cooling']['tube_taper_ratio']:.1f}:1 clears",
                   taper_warn and split_clears))
    ro = _run(tube_hatbands=False)
    checks.append(("bands off -> no band result/mass",
                   ro["cooling"]["hatbands"] is None and ro["hatband_mass_kg"] == 0.0))

    all_ok = True
    for name, ok in checks:
        all_ok = all_ok and bool(ok)
        print(f"  {name:62s} [{'OK' if ok else 'FAIL'}]")
    print()
    print("ALL HATBAND PLAUSIBILITY CHECKS OK" if all_ok else
          "*** HATBAND PLAUSIBILITY CHECK FAILED - review physics/hatbands.py ***")
    print("=" * 78)
    return all_ok
