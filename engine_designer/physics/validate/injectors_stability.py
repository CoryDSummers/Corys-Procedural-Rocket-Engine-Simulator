"""Injector element geometry (incl. gas-centered swirl) and combustion acoustic stability.

Part of the physics/validate/ package (split verbatim out of the former
single-file validate.py - run the whole suite with
`python3 -m engine_designer.physics.validate`)."""

from .. import (combustion_stability)
from ..design import EngineDesign


# Real injector element counts (type-level spot check for physics/injectors.py's
# element_geometry). Orifice diameter is illustrative, so only the ORDER of the
# count and the injection-velocity / momentum-ratio ranges are gated.
INJECTOR_GEOMETRY_CHECKS = [
    dict(name="F-1 (LOX/RP-1, flat-plate impinging, ~6000 orifices)",
         pair="LOX/RP-1", pc_pa=7.0e6, mr=2.27, eps=16.0, thrust_n=7_770_000.0,
         injector="impinging", n_lo=1500, n_hi=25000),
    dict(name="RS-25/SSME-class (LOX/LH2, ~600 coax posts)",
         pair="LOX/LH2", pc_pa=20.6e6, mr=6.0, eps=69.0, thrust_n=2_200_000.0,
         injector="coaxial_swirl", n_lo=150, n_hi=6000),
    dict(name="LMDE-class (N2O4/MMH, single pintle)",
         pair="N2O4/MMH", pc_pa=0.7e6, mr=1.6, eps=47.0, thrust_n=45_000.0,
         injector="pintle", n_lo=1, n_hi=4000),
]


def run_injector_geometry_check():
    """
    Type-level spot check for physics/injectors.py's element_geometry(): does a
    real engine's per-stream orifice count come out the right ORDER, and do the
    injection velocities / momentum ratio land in textbook ranges
    ([Huzel 4.5 / Sutton 8.1])?
    """
    print()
    print("=" * 78)
    print("INJECTOR-GEOMETRY SPOT CHECK (full pipeline, Bell@80%)")
    print("=" * 78)
    all_ok = True
    for check in INJECTOR_GEOMETRY_CHECKS:
        d = EngineDesign(propellant_pair=check["pair"], mixture_ratio=check["mr"],
                          chamber_pressure_pa=check["pc_pa"], expansion_ratio=check["eps"],
                          nozzle_type="bell", bell_percent_length=80.0, cycle="gas_generator",
                          injector_type=check["injector"], target_vac_thrust_n=check["thrust_n"])
        g = d.compute()["injector_geometry"]
        n_ok = check["n_lo"] <= g["n_elements"] <= check["n_hi"]
        # A shear-coax H2 post legitimately injects at ~250-350 m/s (SSME) - far
        # faster than an impinging-liquid element - so the fuel-side band is wide.
        v_ok = 5.0 <= g["v_fuel_ms"] <= 400.0 and 5.0 <= g["v_ox_ms"] <= 150.0
        rm_ok = 0.2 <= g["momentum_ratio"] <= 6.0
        ok = n_ok and v_ok and rm_ok
        all_ok &= ok
        print(f"\n{check['name']}  [{'OK' if ok else '*** FAIL ***'}]")
        print(f"  element count: {g['n_elements']}   band {check['n_lo']}-{check['n_hi']}   "
              f"[{'OK' if n_ok else 'FAIL'}]")
        print(f"  injection velocity: fuel {g['v_fuel_ms']:.0f} / ox {g['v_ox_ms']:.0f} m/s   "
              f"allowed fuel 5-400 / ox 5-150   [{'OK' if v_ok else 'FAIL'}]")
        print(f"  injection momentum ratio Rm: {g['momentum_ratio']:.2f}   allowed 0.2-6.0   "
              f"[{'OK' if rm_ok else 'FAIL'}]")
        print(f"  ({g['note']})")

    # --- I1/I2/I3 detail (dP split, Cd, beta angle, injector-plate mass) ---
    imp = EngineDesign(propellant_pair="LOX/RP-1", mixture_ratio=2.34, chamber_pressure_pa=7e6,
                        expansion_ratio=14, nozzle_type="bell", bell_percent_length=80.0,
                        cycle="gas_generator", injector_type="impinging",
                        target_vac_thrust_n=7.77e6).compute()
    coax = EngineDesign(propellant_pair="LOX/LH2", mixture_ratio=6.0, chamber_pressure_pa=20e6,
                         expansion_ratio=69, nozzle_type="bell", bell_percent_length=80.0,
                         cycle="frsc", injector_type="coax_post", target_vac_thrust_n=2.2e6).compute()
    rounded = EngineDesign(propellant_pair="LOX/RP-1", mixture_ratio=2.34, chamber_pressure_pa=2e6,
                            expansion_ratio=14, nozzle_type="bell", bell_percent_length=80.0,
                            cycle="pressure_fed", injector_type="impinging",
                            orifice_type="short_tube_rounded", target_vac_thrust_n=1e5).compute()
    sharp = EngineDesign(propellant_pair="LOX/RP-1", mixture_ratio=2.34, chamber_pressure_pa=2e6,
                          expansion_ratio=14, nozzle_type="bell", bell_percent_length=80.0,
                          cycle="pressure_fed", injector_type="impinging",
                          target_vac_thrust_n=1e5).compute()
    tri = EngineDesign(propellant_pair="LOX/RP-1", mixture_ratio=2.34, chamber_pressure_pa=7e6,
                        expansion_ratio=14, nozzle_type="bell", bell_percent_length=80.0,
                        cycle="gas_generator", injector_type="unlike_triplet",
                        target_vac_thrust_n=7.77e6).compute()

    split_ok = (abs(imp["injector_dp_fuel_pa"] - imp["injector_dp_ox_pa"]) < 1.0
                and coax["injector_dp_ox_pa"] > coax["injector_dp_fuel_pa"] * 1.5)
    cd_ok = (rounded["orifice_cd"] == 0.88 and sharp["orifice_cd"] == 0.65
             and rounded["injector_dp_derived_pa"] < sharp["injector_dp_derived_pa"])
    beta_ok = (abs(tri["injector_geometry"]["beta_deg"]) < 1e-9
               and imp["injector_geometry"]["beta_deg"] > 0.0)
    plate_ok = (150.0 <= imp["injector_plate_mass_kg"] <= 1000.0
                and coax["injector_plate_mass_kg"] < imp["injector_plate_mass_kg"])
    all_ok &= split_ok and cd_ok and beta_ok and plate_ok
    print(f"\ninjector detail (dP split / Cd / beta / plate mass)  "
          f"[{'OK' if split_ok and cd_ok and beta_ok and plate_ok else '*** FAIL ***'}]")
    print(f"  impinging dP fuel==ox, coax_post ox>fuel   [{'OK' if split_ok else 'FAIL'}] "
          f"(coax {coax['injector_dp_fuel_pa']/1e6:.2f}/{coax['injector_dp_ox_pa']/1e6:.2f} MPa)")
    print(f"  rounded orifice Cd 0.88 needs less dP than sharp 0.65   [{'OK' if cd_ok else 'FAIL'}]")
    print(f"  symmetric triplet beta ~0, unlike doublet beta {imp['injector_geometry']['beta_deg']:+.1f} "
          f"deg   [{'OK' if beta_ok else 'FAIL'}]")
    print(f"  F-1-class injector plate {imp['injector_plate_mass_kg']:.0f} kg (150-900)   "
          f"[{'OK' if plate_ok else 'FAIL'}]")

    print()
    print("ALL INJECTOR-GEOMETRY CHECKS OK" if all_ok else
          "*** INJECTOR-GEOMETRY CHECK FAILED - review physics/injectors.py ***")
    print("=" * 78)
    return all_ok


def run_gas_centered_swirl_injector_check():
    """
    Injector-element-layer spot check for the "gas_centered_swirl" catalog entry
    (physics/injectors.py) - the RD-120/170/180/191-family ORSC element
    [Bazarov]. Distinct from run_cycle_model_check()'s RD-180 ORSC CYCLE-level
    row, which stays on the "impinging" default injector - this check exercises
    the new injector type explicitly.

    Does NOT assert an absolute match to RD-180's real 338.4 s vacuum Isp.
    Investigation while calibrating eta_cstar_multiplier found that this design's
    Isp is capped well below 338.4 s by design.py's ETA_CSTAR_CEILING (0.99)
    regardless of how high the injector multiplier is pushed - i.e. the shortfall
    is a pre-existing ORSC-cycle/nozzle-model limitation for this specific very-
    high-performance real engine, not something an injector-element multiplier
    can or should paper over (BE-4, a lower-performance real ORSC engine, matches
    the tool's model within ~1% with the SAME cycle machinery - see ASSUMPTIONS.md
    for the full comparison). Forcing the multiplier past the literature-motivated
    ~1.02 (the top of the existing injector-type spread) to chase 338.4 would
    misattribute a cycle-level gap to the injector and isn't done here.

    What this DOES assert: the new element type is genuinely better than the
    generic "impinging" baseline on an identical RD-180-parameter design (the
    real, literature-backed direction), and the derived injector dP/Pc lands
    near Bazarov's real ~10.5% figure.
    """
    print()
    print("=" * 78)
    print("GAS-CENTERED-SWIRL (ORSC) INJECTOR SPOT CHECK [Bazarov]")
    print("=" * 78)

    def _rd180(injector_type):
        return EngineDesign(propellant_pair="LOX/RP-1", mixture_ratio=2.72,
                             chamber_pressure_pa=26.66e6, expansion_ratio=36.87,
                             cycle="orsc", injector_type=injector_type,
                             turbopump_material_key="monel_k500",
                             target_vac_thrust_n=4_152_000.0).compute()

    baseline = _rd180("impinging")
    swirl = _rd180("gas_centered_swirl")
    isp_better_ok = swirl["isp_vac_engine_s"] > baseline["isp_vac_engine_s"]
    dp_ratio = swirl["injector_dp_fuel_pa"] / 26.66e6
    dp_ok = 0.08 <= dp_ratio <= 0.13   # Bazarov's real ~10.5%, wide band
    all_ok = isp_better_ok and dp_ok

    print(f"\nRD-180 params, impinging vs gas_centered_swirl  "
          f"[{'OK' if all_ok else '*** FAIL ***'}]")
    print(f"  Isp: impinging {baseline['isp_vac_engine_s']:.1f} s -> "
          f"gas_centered_swirl {swirl['isp_vac_engine_s']:.1f} s (real 338.4 s, "
          f"NOT asserted here - see docstring)   [{'OK' if isp_better_ok else 'FAIL'}]")
    print(f"  injector dP/Pc: {dp_ratio:.3f}   allowed 0.08-0.13 "
          f"([Bazarov Table 3] ~0.105)   [{'OK' if dp_ok else 'FAIL'}]")

    print()
    print("ALL GAS-CENTERED-SWIRL INJECTOR CHECKS OK" if all_ok else
          "*** GAS-CENTERED-SWIRL INJECTOR CHECK FAILED - review physics/injectors.py ***")
    print("=" * 78)
    return all_ok


def run_combustion_stability_check():
    """
    Chamber acoustic-mode frequencies (physics/combustion_stability.py) against a
    published real engine: Vulcain HM-60 first tangential mode T1 = 2424 Hz
    ([Sutton Table 9-3]). Also checks mode ordering (1R > 1T) and that a small
    chamber lands at higher frequency than a large one.
    """
    print()
    print("=" * 78)
    print("COMBUSTION-STABILITY SPOT CHECK (acoustic modes)")
    print("=" * 78)
    all_ok = True

    # Vulcain HM-60: LOX/LH2, Pc 10 MPa, MR 5.6, ~1 MN vac, eps ~45.
    d = EngineDesign(propellant_pair="LOX/LH2", mixture_ratio=5.6, chamber_pressure_pa=10.0e6,
                      expansion_ratio=45.0, nozzle_type="bell", bell_percent_length=80.0,
                      cycle="gas_generator", injector_type="coaxial_swirl",
                      target_vac_thrust_n=1_000_000.0)
    a = d.compute()["chamber_acoustics"]
    f1t, real_1t = a["tang_1t_hz"], 2424.0
    err = abs(f1t - real_1t) / real_1t * 100.0
    # Wide band: the tool's chamber length/diameter come from L* + contraction
    # ratio, not Vulcain's exact geometry.
    f1t_ok = err <= 30.0
    order_ok = a["rad_1r_hz"] > a["tang_1t_hz"] > 0.0 and a["long_1l_hz"] > 0.0
    all_ok &= f1t_ok and order_ok
    print(f"\nVulcain HM-60 (LOX/LH2, 10 MPa, MR 5.6)  "
          f"[{'OK' if f1t_ok and order_ok else '*** FAIL ***'}]")
    print(f"  a_e {a['sound_speed_ms']:.0f} m/s   1L {a['long_1l_hz']:.0f} Hz   "
          f"1T {f1t:.0f} Hz (real 2424, err {err:+.0f}%)   1R {a['rad_1r_hz']:.0f} Hz")
    print(f"  1T within 30% of published   [{'OK' if f1t_ok else 'FAIL'}]")
    print(f"  mode ordering 1R > 1T > 0, 1L > 0   [{'OK' if order_ok else 'FAIL'}]")

    # --- stability aids: a design that trips the acoustic advisory, then each
    # of the three cures clearing it (physics/combustion_stability.py aids). ---
    def _row(r, name):
        return next(c for c in r["checklist"] if c["name"] == name)

    trip_kw = dict(propellant_pair="LOX/RP-1", mixture_ratio=2.34, chamber_pressure_pa=5.0e6,
                    expansion_ratio=14.0, nozzle_type="bell", bell_percent_length=80.0,
                    cycle="gas_generator", injector_type="impinging", contraction_ratio=2.6,
                    lstar_m=1.3, target_vac_thrust_n=1.2e5)
    base = EngineDesign(**trip_kw).compute()
    trip_row = _row(base, "Combustion acoustic-mode margin")
    trip_1t = base["chamber_acoustics"]["tang_1t_hz"]
    trips = (not trip_row["passed"]) and trip_1t < combustion_stability.DAMAGING_MODE_CEILING_HZ

    baf = EngineDesign(**trip_kw, injector_baffles=True).compute()
    baf_row = _row(baf, "Combustion acoustic-mode margin")
    baf_ok = baf_row["passed"] and "baffle" in baf_row["detail"].lower()
    baf_mass_ok = baf["computed_dry_mass_kg"] > base["computed_dry_mass_kg"]

    cav = EngineDesign(**trip_kw, acoustic_cavities=True, acoustic_cavity_count=12).compute()
    cav_ok = _row(cav, "Combustion acoustic-mode margin")["passed"]

    stiff = EngineDesign(**trip_kw, injector_stiffness="very_stiff").compute()
    stiff_ok = (_row(stiff, "Combustion acoustic-mode margin")["passed"]
                and stiff["injector_dp_pa"] > base["injector_dp_pa"])

    even = EngineDesign(**trip_kw, injector_baffles=True, baffle_compartments=4).compute()
    even_ok = not _row(even, "Baffle compartment count")["passed"]

    aids_ok = trips and baf_ok and baf_mass_ok and cav_ok and stiff_ok and even_ok
    all_ok &= aids_ok
    print(f"\nStability aids (LOX/RP-1 impinging, 1T ~{trip_1t:.0f} Hz)  "
          f"[{'OK' if aids_ok else '*** FAIL ***'}]")
    print(f"  base design trips the acoustic advisory   [{'OK' if trips else 'FAIL'}]")
    print(f"  + injector-face baffle clears it (+{baf['computed_dry_mass_kg']-base['computed_dry_mass_kg']:.1f} kg)"
          f"   [{'OK' if baf_ok and baf_mass_ok else 'FAIL'}]")
    print(f"  + Helmholtz cavities clear it   [{'OK' if cav_ok else 'FAIL'}]")
    print(f"  + very-stiff injector clears it (dP {base['injector_dp_pa']/1e6:.2f} -> "
          f"{stiff['injector_dp_pa']/1e6:.2f} MPa)   [{'OK' if stiff_ok else 'FAIL'}]")
    print(f"  even (4) baffle compartment count warns   [{'OK' if even_ok else 'FAIL'}]")

    print()
    print("ALL COMBUSTION-STABILITY CHECKS OK" if all_ok else
          "*** COMBUSTION-STABILITY CHECK FAILED - review physics/combustion_stability.py ***")
    print("=" * 78)
    return all_ok
