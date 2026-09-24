"""Cooling: explicit per-section cooling methods (incl. dump) and the material x method hard-block compatibility.

Part of the physics/validate/ package (split verbatim out of the former
single-file validate.py - run the whole suite with
`python3 -m engine_designer.physics.validate`)."""

from .. import (cooling, materials)
from ..design import EngineDesign


def run_explicit_cooling_check():
    """
    The per-section cooling-method choice (physics/cooling.resolve_cooling_method,
    EngineDesign.chamber_cooling_method / nozzle_cooling_method).

    Two things to pin:
      1. AUTO-EQUIVALENCE - "auto" must be a pure alias for the material's own
         cooling_method, so `compute()` is field-identical to the pre-Phase-2
         behaviour for every (material x cycle). This is the "nothing moved" gate.
      2. OVERRIDE ROUTING - an explicit method must actually re-route the
         jacket-dP / rated-burn-time / regen-Isp-credit / fatigue logic,
         regardless of what the chosen material's own method is.
    """
    print()
    print("=" * 78)
    print("EXPLICIT COOLING-METHOD SPOT CHECK (auto-equivalence + override routing)")
    print("=" * 78)
    all_ok = True

    # 1. Auto-equivalence across every material x a few cycles.
    eq_fields = ("isp_vac_engine_s", "isp_sl_engine_s", "thrust_vac_n",
                 "computed_dry_mass_kg", "rated_burn_time_s")
    eq_cool = ("jacket_dp_pa", "t_wg_throat_k", "coolant_delta_t_k",
               "regen_isp_bonus_fraction", "wall_heat_total_w", "regen_cooled")
    eq_ok = True
    n_eq = 0
    for mk in materials.available_materials():
        for cyc in ("gas_generator", "pressure_fed", "expander"):
            kw = dict(cycle=cyc, material_key=mk, bell_material_key=mk)
            if cyc == "expander":
                kw.update(propellant_pair="LOX/LH2", mixture_ratio=5.5)
            base = EngineDesign(**kw).compute()
            auto = EngineDesign(chamber_cooling_method="auto",
                                 nozzle_cooling_method="auto", **kw).compute()
            n_eq += 1
            for f in eq_fields:
                if base[f] != auto[f]:
                    eq_ok = False
                    print(f"  DIFF {mk}/{cyc} {f}: {base[f]} vs {auto[f]}")
            for f in eq_cool:
                if base["cooling"][f] != auto["cooling"][f]:
                    eq_ok = False
                    print(f"  DIFF {mk}/{cyc} cooling.{f}: "
                          f"{base['cooling'][f]} vs {auto['cooling'][f]}")
            if auto["cooling"]["chamber_cooling_method"] != materials.MATERIALS[mk].cooling_method:
                eq_ok = False
                print(f"  RESOLVE {mk}: {auto['cooling']['chamber_cooling_method']}")
    all_ok &= eq_ok
    print(f"\nauto-equivalence over {n_eq} (material x cycle) cases  "
          f"[{'OK' if eq_ok else '*** FAIL ***'}]")

    # 2. Override routing - within each material's allowed_cooling_methods.
    #    Physically meaningless combos are HARD-BLOCKED (2026-09-23): an explicit
    #    ablative on a copper liner / regen on an ablative phenolic coerce back
    #    to the material's own method with a failing checklist row.
    cu = EngineDesign(cycle="gas_generator", material_key="narloy_z")           # regen copper
    cu_abl = EngineDesign(cycle="gas_generator", material_key="narloy_z",
                           chamber_cooling_method="ablative").compute()
    cu_base = cu.compute()
    _row_a = next(c for c in cu_abl["checklist"]
                  if c["name"] == "Chamber cooling method compatible with material")
    a_ok = (cu_abl["cooling"]["chamber_cooling_method"] == "regenerative"
            and cu_abl["cooling"]["chamber_cooling_rejected"] == "ablative"
            and not _row_a["passed"] and "BLOCKED" in _row_a["detail"]
            and cu_abl["cooling"]["jacket_dp_pa"] == cu_base["cooling"]["jacket_dp_pa"]
            and cu_abl["rated_burn_time_s"] == cu_base["rated_burn_time_s"])
    all_ok &= a_ok
    print(f"\n(a) explicit ablative on NARloy-Z -> BLOCKED, runs "
          f"{cu_abl['cooling']['chamber_cooling_method']} (jacket dP "
          f"{cu_abl['cooling']['jacket_dp_pa']/1e6:.2f} MPa, rated "
          f"{cu_abl['rated_burn_time_s']:.0f}s = auto)   [{'OK' if a_ok else 'FAIL'}]")

    ph_base = EngineDesign(cycle="gas_generator", material_key="ablative_phenolic").compute()
    ph_regen = EngineDesign(cycle="gas_generator", material_key="ablative_phenolic",
                             chamber_cooling_method="regenerative").compute()
    _row_b = next(c for c in ph_regen["checklist"]
                  if c["name"] == "Chamber cooling method compatible with material")
    b_ok = (ph_base["cooling"]["jacket_dp_pa"] == 0.0
            and ph_regen["cooling"]["jacket_dp_pa"] == 0.0
            and not ph_regen["cooling"]["regen_cooled"]
            and ph_regen["cooling"]["chamber_cooling_method"] == "ablative"
            and not _row_b["passed"]
            and ph_regen["rated_burn_time_s"] == ph_base["rated_burn_time_s"])
    all_ok &= b_ok
    print(f"(b) explicit regen on ablative phenolic -> BLOCKED, runs "
          f"{ph_regen['cooling']['chamber_cooling_method']} (jacket dP "
          f"{ph_regen['cooling']['jacket_dp_pa']/1e6:.2f} MPa)   [{'OK' if b_ok else 'FAIL'}]")

    un = EngineDesign(cycle="gas_generator", material_key="narloy_z",
                       chamber_cooling_method="uncooled").compute()
    fatigue_row = next(c for c in un["checklist"]
                       if c["name"] == "Throat thermal-fatigue cycle life")
    c_ok = (un["cooling"]["jacket_dp_pa"] == 0.0
            and un["cooling"]["regen_isp_bonus_fraction"] == 0.0
            and "n/a" in fatigue_row["detail"])
    all_ok &= c_ok
    print(f"(c) uncooled chamber: jacket dP {un['cooling']['jacket_dp_pa']/1e6:.2f} MPa, "
          f"regen Isp credit {un['cooling']['regen_isp_bonus_fraction']:.4f}, fatigue row n/a   "
          f"[{'OK' if c_ok else 'FAIL'}]")

    nz = EngineDesign(cycle="gas_generator", bell_material_key="inconel_718",
                       nozzle_cooling_method="radiative").compute()
    d_ok = (nz["cooling"]["bell_wall_temp_k"] is not None
            and nz["cooling"]["nozzle_cooling_source"] == "explicit"
            and nz["cooling"]["nozzle_cooling_method"] == "radiative")
    all_ok &= d_ok
    print(f"(d) explicit radiative nozzle on Inconel bell: radiative-eq wall temp "
          f"~{nz['cooling']['bell_wall_temp_k']:.0f} K   [{'OK' if d_ok else 'FAIL'}]")

    # (e) Wall construction (physics/cooling.WALL_CONSTRUCTIONS). F-1-class regen
    # design in channels mode: a brazed tube wall runs a hotter coolant-side
    # throat (lower h_c) and a higher jacket dP than milled channels, and carries
    # extra jacket structural mass; milled_channel is bit-identical to no field.
    wc_kw = dict(propellant_pair="LOX/RP-1", mixture_ratio=2.27, chamber_pressure_pa=7.0e6,
                  expansion_ratio=16.0, cycle="gas_generator", nozzle_type="bell",
                  bell_percent_length=80.0, injector_type="impinging", material_key="narloy_z",
                  target_vac_thrust_n=7_770_000.0, regen_channel_model="channels")
    wc_mil = EngineDesign(**wc_kw, wall_construction="milled_channel").compute()
    wc_base = EngineDesign(**wc_kw).compute()
    wc_tube = EngineDesign(**wc_kw, wall_construction="tube_wall").compute()
    wc_coax = EngineDesign(**wc_kw, wall_construction="coax_shell").compute()
    e_neutral = (wc_mil["cooling"]["jacket_dp_pa"] == wc_base["cooling"]["jacket_dp_pa"]
                 and wc_mil["computed_dry_mass_kg"] == wc_base["computed_dry_mass_kg"]
                 and wc_mil["jacket_structure_mass_kg"] == 0.0)
    e_dir = (wc_tube["cooling"]["coolant_side_wall_t_throat_k"]
             > wc_mil["cooling"]["coolant_side_wall_t_throat_k"]
             and wc_tube["cooling"]["jacket_dp_pa"] > wc_mil["cooling"]["jacket_dp_pa"]
             and wc_tube["jacket_structure_mass_kg"] > 0.0
             and wc_coax["jacket_structure_mass_kg"] > wc_tube["jacket_structure_mass_kg"])
    e_band = 0.3e6 <= wc_tube["cooling"]["jacket_dp_pa"] <= 4.0e6
    e_ok = e_neutral and e_dir and e_band
    all_ok &= e_ok
    print(f"\n(e) wall construction (F-1-class, channels): milled dP "
          f"{wc_mil['cooling']['jacket_dp_pa']/1e6:.2f} / T_wc {wc_mil['cooling']['coolant_side_wall_t_throat_k']:.0f}K "
          f"-> tube dP {wc_tube['cooling']['jacket_dp_pa']/1e6:.2f} / T_wc "
          f"{wc_tube['cooling']['coolant_side_wall_t_throat_k']:.0f}K / +{wc_tube['jacket_structure_mass_kg']:.0f}kg jacket   "
          f"[{'OK' if e_ok else 'FAIL'}]")

    # (f) Dump cooling (nozzle extension only): Vulcain-HM-60-class and J-2-class,
    # a full-length dump-cooled nozzle extension (regen_nozzle_end_eps ==
    # expansion_ratio) vs the same design radiatively cooled. Auto-sized dump
    # fraction must respect the LOX/LH2 coolant limit; the net Isp loss vs the
    # radiative baseline must be small; no section = "dump" must be a no-op.
    dump_ok = True
    dump_rows = []
    for name, pair, mr, pc, eps, thrust_n in [
            ("Vulcain-HM-60-class", "LOX/LH2", 5.5, 11.0e6, 45.0, 1_140_000.0),
            ("J-2-class", "LOX/LH2", 5.5, 5.4e6, 27.5, 1_033_000.0)]:
        dkw = dict(propellant_pair=pair, mixture_ratio=mr, chamber_pressure_pa=pc,
                    expansion_ratio=eps, cycle="gas_generator", nozzle_type="bell",
                    bell_percent_length=80.0, injector_type="impinging",
                    material_key="narloy_z", target_vac_thrust_n=thrust_n)
        d_rad = EngineDesign(**dkw, nozzle_cooling_method="radiative").compute()
        d_dump = EngineDesign(**dkw, nozzle_cooling_method="dump",
                               regen_nozzle_end_eps=eps).compute()
        cd = d_dump["cooling"]
        isp_loss_pct = 100.0 * (d_rad["isp_vac_engine_s"] - d_dump["isp_vac_engine_s"]) / d_rad["isp_vac_engine_s"]
        row_ok = (0.1 <= cd["dump_isp_penalty_fraction"] * 100.0 <= 1.6
                  and cd["dump_coolant_dt_k"] <= cooling.MAX_COOLANT_DELTA_T_K["LOX/LH2"] + 1.0
                  and 0.0 <= isp_loss_pct <= 2.0
                  and 0.02 <= cd["dump_coolant_fraction"] <= 0.25)
        dump_ok &= row_ok
        dump_rows.append((name, cd, isp_loss_pct, row_ok))
    # Neutral: no section resolved to "dump" (built-in materials never are) -> no-op.
    no_dump_a = EngineDesign(cycle="gas_generator").compute()
    no_dump_b = EngineDesign(cycle="gas_generator", dump_coolant_fraction=0.10).compute()
    dump_neutral_ok = (no_dump_a["isp_vac_engine_s"] == no_dump_b["isp_vac_engine_s"]
                       and no_dump_b["cooling"]["dump_isp_penalty_fraction"] == 0.0)
    dump_ok &= dump_neutral_ok
    all_ok &= dump_ok
    print(f"\n(f) dump cooling (nozzle extension)  [{'OK' if dump_ok else '*** FAIL ***'}]")
    for name, cd, isp_loss_pct, row_ok in dump_rows:
        print(f"  {name:20s} {cd['dump_coolant_fraction']*100:.1f}% of fuel, dT "
              f"{cd['dump_coolant_dt_k']:.0f} K, Isp penalty {cd['dump_isp_penalty_fraction']*100:.2f}% "
              f"(vs radiative: {isp_loss_pct:+.2f}%)   [{'OK' if row_ok else 'FAIL'}]")
    print(f"  no dump section -> no-op  [{'OK' if dump_neutral_ok else 'FAIL'}]")

    # Realism sanity (not gated): storable engines with ablative/radiative chambers.
    for name, pair, mr, pc, eps, mat_key, thrust_n, real_rated_s in [
            ("AJ10-137 (Apollo SPS, N2O4/A-50, ablative)",
             "Aerozine-50/NTO", 1.6, 0.7e6, 62.5, "ablative_phenolic", 45_000.0, None),
            ("Aestus (N2O4/MMH, ablative/radiative)",
             "N2O4/MMH", 1.9, 1.1e6, 84.0, "ablative_phenolic", 45_000.0, None),
            ("LMAE (Apollo LM ascent, MON1/A-50, Refrasil-phenolic ablative)",
             "Aerozine-50/NTO", 1.6, 0.83e6, 45.6, "refrasil_phenolic", 15_570.0, 560.0)]:
        r = EngineDesign(propellant_pair=pair, mixture_ratio=mr, chamber_pressure_pa=pc,
                          expansion_ratio=eps, cycle="pressure_fed",
                          nozzle_type="bell", bell_percent_length=80.0,
                          material_key=mat_key,
                          target_vac_thrust_n=thrust_n).compute()
        real_str = (f" (real ratedBurnTime {real_rated_s:.0f} s - this tool's hoop-stress-"
                    f"derived wall thickness at LMAE's low 120 psia Pc undershoots a real "
                    f"erosion-life-sized ablative liner, see materials.py's "
                    f"_REFRASIL_CONSUMPTION_RATE_M_S comment)" if real_rated_s else "")
        print(f"  {name}: resolved {r['cooling']['chamber_cooling_method']} cooling, "
              f"Isp {r['isp_vac_engine_s']:.0f} s, rated {r['rated_burn_time_s']:.0f} s "
              f"(informational){real_str}")

    print()
    print("ALL EXPLICIT-COOLING CHECKS OK" if all_ok else
          "*** EXPLICIT-COOLING CHECK FAILED - review physics/cooling.resolve_cooling_method "
          "/ design.py cooling routing ***")
    print("=" * 78)
    return all_ok


def run_cooling_compatibility_check():
    """
    Material/cooling-method HARD BLOCK (materials.Material.allowed_cooling_methods,
    cooling.resolve_cooling_method_checked, 2026-09-23) - a deliberate exception
    to the tool's "warn, don't block" rule for physically meaningless combos.

      1. Resolver sweep: every material x every method (+ the retired "film"):
         allowed -> honoured; disallowed -> the material's own method + the
         rejected name. Every material's own default is always allowed.
      2. compute() routing: one disallowed method per material (chamber) and a
         regen-on-niobium bell: runs the default method, a FAILING checklist row
         says BLOCKED, and the result is field-identical to "auto".
      3. Schema 7 -> 8 migration: a saved "film" section method becomes
         "uncooled" (or "auto" where uncooled isn't allowed) + the film overlay.
    """
    print()
    print("=" * 78)
    print("COOLING-COMPATIBILITY CHECK (material x cooling-method hard block)")
    print("=" * 78)
    all_ok = True
    n_allowed = n_blocked = 0
    for mk, mat in materials.MATERIALS.items():
        ok_default = mat.cooling_method in mat.allowed_cooling_methods
        all_ok &= ok_default
        for meth in cooling.COOLING_METHODS + ("film",):
            eff, rej = cooling.resolve_cooling_method_checked(meth, mat)
            if meth in mat.allowed_cooling_methods:
                row_ok = eff == meth and rej is None
                n_allowed += 1
            else:
                row_ok = eff == mat.cooling_method and rej == meth
                n_blocked += 1
            if not row_ok:
                print(f"  RESOLVE {mk}/{meth}: -> ({eff}, {rej})   [FAIL]")
            all_ok &= row_ok
        all_ok &= cooling.resolve_cooling_method_checked("auto", mat) == (mat.cooling_method, None)
    for mk in ("ablative_phenolic", "refrasil_phenolic"):
        all_ok &= materials.MATERIALS[mk].allowed_cooling_methods == ("ablative",)
    print(f"  resolver sweep: {n_allowed} allowed + {n_blocked} blocked combos "
          f"over {len(materials.MATERIALS)} materials   [{'OK' if all_ok else 'FAIL'}]")

    route_ok = True
    fields = ("isp_vac_engine_s", "thrust_vac_n", "computed_dry_mass_kg", "rated_burn_time_s")
    cfields = ("jacket_dp_pa", "t_wg_throat_k", "wall_heat_total_w", "regen_cooled")
    for mk, mat in materials.MATERIALS.items():
        bad = next(m for m in cooling.COOLING_METHODS if m not in mat.allowed_cooling_methods)
        auto = EngineDesign(cycle="gas_generator", material_key=mk).compute()
        blk = EngineDesign(cycle="gas_generator", material_key=mk,
                            chamber_cooling_method=bad).compute()
        row = next(c for c in blk["checklist"]
                   if c["name"] == "Chamber cooling method compatible with material")
        ok = (not row["passed"] and "BLOCKED" in row["detail"]
              and blk["cooling"]["chamber_cooling_rejected"] == bad
              and blk["cooling"]["chamber_cooling_method"] == mat.cooling_method
              and all(auto[f] == blk[f] for f in fields)
              and all(auto["cooling"][f] == blk["cooling"][f] for f in cfields))
        if not ok:
            print(f"  ROUTE {mk} + {bad}: [FAIL]")
        route_ok &= ok
    nb = EngineDesign(bell_material_key="niobium_c103",
                       nozzle_cooling_method="regenerative").compute()
    nb_row = next(c for c in nb["checklist"]
                  if c["name"] == "Nozzle/bell cooling method compatible with material")
    route_ok &= (nb["cooling"]["nozzle_cooling_method"] == "radiative"
                 and nb["cooling"]["nozzle_cooling_rejected"] == "regenerative"
                 and not nb_row["passed"])
    ok_row = next(c for c in EngineDesign().compute()["checklist"]
                  if c["name"] == "Chamber cooling method compatible with material")
    route_ok &= ok_row["passed"]
    all_ok &= route_ok
    print(f"  compute() routing: every material's blocked pick coerces to its default, "
          f"red row, field-identical to auto; regen niobium bell -> radiative   "
          f"[{'OK' if route_ok else 'FAIL'}]")

    mig = EngineDesign.from_dict({"schema_version": 7, "design": {
        "chamber_cooling_method": "film", "nozzle_cooling_method": "film",
        "material_key": "stainless_steel", "bell_material_key": "ablative_phenolic",
        "film_cooling_fraction": 0.0, "cooling_transition_eps": 8.0}})
    mig_ok = (mig.chamber_cooling_method == "uncooled"
              and mig.film_cooling_fraction == cooling.FILM_MDOT_RATIO_REFERENCE
              and mig.nozzle_cooling_method == "auto"          # ablative can't be uncooled
              and mig.nozzle_film_fraction == cooling.FILM_MDOT_RATIO_REFERENCE
              and mig.nozzle_film_inject_eps == 8.0)
    keep = EngineDesign.from_dict({"design": {"chamber_cooling_method": "film",
                                              "film_cooling_fraction": 0.08}})
    mig_ok &= keep.film_cooling_fraction == 0.08 and keep.chamber_cooling_method == "uncooled"
    all_ok &= mig_ok
    print(f"  schema 7->8 'film' migration -> uncooled/auto + film overlay   "
          f"[{'OK' if mig_ok else 'FAIL'}]")
    print()
    print("ALL COOLING-COMPATIBILITY CHECKS OK" if all_ok else
          "*** COOLING-COMPATIBILITY CHECK FAILED - review materials.allowed_cooling_methods "
          "/ cooling.resolve_cooling_method_checked ***")
    print("=" * 78)
    return all_ok


def run_cooling_robustness_sweep():
    """
    2026-09-23 cooling audit: every propellant pair x every chamber method x
    every nozzle method (material chosen to allow it), plus every wall
    construction x both channel models on a regen chamber, must compute with
    finite cooling numbers and a converged unified thermal solve. Catches the
    old silent-zero / TypeError / KeyError class (pairs with no coolant data:
    Aerozine-50, hydrazine, H2O2) and any non-converging treatment mix.
    """
    import itertools
    import math
    from .. import combustion
    print()
    print("=" * 78)
    print("COOLING ROBUSTNESS SWEEP (pair x method x construction, no crash / NaN)")
    print("=" * 78)
    mats = {"regenerative": "stainless_steel", "dump": "stainless_steel",
            "radiative": "niobium_c103", "uncooled": "inconel_718",
            "ablative": "ablative_phenolic"}
    combos = [(p, ch, nz, "milled_channel", "channels")
              for p, ch, nz in itertools.product(combustion.available_pairs(), mats, mats)]
    combos += [(p, "regenerative", "regenerative", wc, model)
               for p in ("LOX/RP-1", "LOX/LH2", "Aerozine-50/NTO")
               for wc, model in itertools.product(cooling.WALL_CONSTRUCTIONS, ("flat", "channels"))]
    bad = []
    for pair, ch, nz, wc, model in combos:
        lo, hi = combustion.mr_bounds(pair)
        mono = combustion.is_monopropellant(pair)
        d = EngineDesign(propellant_pair=pair, mixture_ratio=0.5 * (lo + hi),
                         chamber_cooling_method=ch, nozzle_cooling_method=nz,
                         material_key=mats[ch], bell_material_key=mats[nz],
                         wall_construction=wc, regen_channel_model=model,
                         regen_nozzle_end_eps=10.0, nozzle_type="bell",
                         cycle="pressure_fed" if mono else "gas_generator",
                         chamber_pressure_pa=3.0e6)
        try:
            r = d.compute()
            c = r["cooling"]
            vals = (c["q_throat_w_m2"], c["wall_heat_total_w"], r["isp_vac_engine_s"],
                    r["rated_burn_time_s"])
            if (not all(v is not None and math.isfinite(v) for v in vals)
                    or not c["thermal_solve_converged"]):
                bad.append(f"{pair} {ch}/{nz} {wc} {model}: nonfinite or not converged")
        except Exception as e:      # a crash is exactly what this sweep exists to catch
            bad.append(f"{pair} {ch}/{nz} {wc} {model}: {e!r}"[:160])
    for b in bad[:20]:
        print("  " + b)
    ok = not bad
    print(f"  {len(combos)} combinations, {len(bad)} bad   [{'OK' if ok else 'FAIL'}]")
    print()
    print("ALL COOLING ROBUSTNESS CHECKS OK" if ok else
          "*** COOLING ROBUSTNESS SWEEP FAILED - review cooling/thermal_solve.py ***")
    print("=" * 78)
    return ok
