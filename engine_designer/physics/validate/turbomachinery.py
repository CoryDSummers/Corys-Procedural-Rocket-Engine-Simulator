"""Turbopump efficiency / sizing / bearing DN, GG bleed, per-cycle models, feed-system plausibility and the pump pressure chain.

Part of the physics/validate/ package (split verbatim out of the former
single-file validate.py - run the whole suite with
`python3 -m engine_designer.physics.validate`)."""

from .. import (cooling, cycles, turbopump_sizing)
from ..design import EngineDesign


# Real engines for the DERIVED turbopump-efficiency model
# (physics/turbopump_efficiency.py). Pump eta from SP-8107 Table II, turbine eta
# from Table III. Bands are +-0.08 absolute (the curve shapes are calibrated
# choices, no published eta-vs-Ns / eta-vs-U-C0 curve exists). RL10's tiny 1962
# geared H2 pump (55%) is a documented low outlier - reported, gated at +-0.13.
TURBOPUMP_EFFICIENCY_CHECKS = [
    dict(name="F-1 (LOX/RP-1, GG, 2-row VC turbine)",
         kw=dict(propellant_pair="LOX/RP-1", mixture_ratio=2.27, chamber_pressure_pa=7.0e6,
                 expansion_ratio=16.0, cycle="gas_generator",
                 turbine_staging="velocity_compounded_2row", target_vac_thrust_n=7_770_000.0),
         eta_pf=0.726, eta_po=0.746, eta_turb=0.605),
    dict(name="J-2 (LOX/LH2, GG, 2-row VC turbine)",
         kw=dict(propellant_pair="LOX/LH2", mixture_ratio=5.5, chamber_pressure_pa=5.4e6,
                 expansion_ratio=27.5, cycle="gas_generator", target_vac_thrust_n=1_023_000.0),
         eta_pf=0.73, eta_po=0.80, eta_turb=0.601),
    dict(name="H-1 (LOX/RP-1, GG, 2-stage PC turbine)",
         kw=dict(propellant_pair="LOX/RP-1", mixture_ratio=2.23, chamber_pressure_pa=4.8e6,
                 expansion_ratio=8.0, cycle="gas_generator", target_vac_thrust_n=1_030_000.0),
         eta_pf=0.718, eta_po=0.778, eta_turb=0.702),
    dict(name="RL10 (LOX/LH2, expander, reaction turbine)",
         kw=dict(propellant_pair="LOX/LH2", mixture_ratio=5.5, chamber_pressure_pa=3.2e6,
                 expansion_ratio=61.0, cycle="expander", target_vac_thrust_n=73_000.0),
         eta_pf=0.55, eta_po=0.63, eta_turb=0.74, eta_pf_tol=0.13),
    dict(name="SSME-class (LOX/LH2, FRSC, reaction turbine)",
         kw=dict(propellant_pair="LOX/LH2", mixture_ratio=6.0, chamber_pressure_pa=20.0e6,
                 expansion_ratio=69.0, cycle="frsc", turbopump_material_key="powder_met_superalloy",
                 target_vac_thrust_n=2_200_000.0),
         eta_pf=0.741, eta_po=0.781, eta_turb=0.79),
]
ETA_TOLERANCE = 0.08


def run_turbopump_efficiency_check():
    """
    Turbopump pump & turbine efficiency is now DERIVED from the machinery design
    (physics/turbopump_efficiency.py: pump eta from whole-pump Ns / size; turbine
    eta from staging ceiling x pitchline x admission x PR), not picked from a
    tier constant. This spot check pins those curves to real SP-8107 Table II /
    III efficiencies through the full EngineDesign.compute() pipeline - the same
    role SPOT_CHECKS plays for DEFAULT_ETA_CSTAR.

    Also checks the build-quality tiers (early_simple / mature / advanced) move
    the derived efficiency monotonically without changing the model's shape.
    """
    print()
    print("=" * 78)
    print(f"DERIVED TURBOPUMP-EFFICIENCY SPOT CHECK (tolerance +-{ETA_TOLERANCE}, full pipeline)")
    print("=" * 78)
    all_ok = True
    for check in TURBOPUMP_EFFICIENCY_CHECKS:
        s = EngineDesign(nozzle_type="bell", bell_percent_length=80.0,
                          injector_type="impinging", **check["kw"]).compute()["turbopump_sizing"]
        rows = [
            ("eta_pump_fuel", s["eta_pump_fuel"], check["eta_pf"], check.get("eta_pf_tol", ETA_TOLERANCE)),
            ("eta_pump_ox", s["eta_pump_ox"], check["eta_po"], check.get("eta_po_tol", ETA_TOLERANCE)),
            ("eta_turbine", s["eta_turbine"], check["eta_turb"], check.get("eta_turb_tol", ETA_TOLERANCE)),
        ]
        ok = all(abs(got - want) <= tol for _, got, want, tol in rows)
        all_ok &= ok
        print(f"\n{check['name']}  [{'OK' if ok else '*** FAIL ***'}]  overall {s['eta_overall']:.3f}")
        for label, got, want, tol in rows:
            print(f"  {label:14} {got:.3f}  vs real {want:.3f}  (d {got-want:+.3f}, tol {tol:.2f})  "
                  f"[{'OK' if abs(got-want) <= tol else 'FAIL'}]")

    # Build-quality tiers: derived efficiency should rise early -> mature -> advanced.
    etas = []
    for key in ("early_simple", "mature", "advanced"):
        s = EngineDesign(propellant_pair="LOX/RP-1", mixture_ratio=2.34, chamber_pressure_pa=8.0e6,
                          expansion_ratio=14.0, cycle="gas_generator", injector_type="impinging",
                          turbopump_tech_key=key, target_vac_thrust_n=1_000_000.0).compute()["turbopump_sizing"]
        etas.append(s["eta_pump_fuel"])
    mono = etas[0] < etas[1] < etas[2]
    all_ok &= mono
    print(f"\nbuild-quality tiers move derived eta_pump_fuel monotonically "
          f"({etas[0]:.3f} < {etas[1]:.3f} < {etas[2]:.3f}): [{'OK' if mono else 'FAIL'}]")
    print()
    print("ALL TURBOPUMP-EFFICIENCY CHECKS OK" if all_ok else
          "*** TURBOPUMP-EFFICIENCY CHECK FAILED - review physics/turbopump_efficiency.py ***")
    print("=" * 78)
    return all_ok


# Real gas-generator-cycle engines and their published turbine-bleed flow
# fractions - the spot-check that calibrates design.py's GG_GAS_PROPERTIES the
# same way SPOT_CHECKS calibrates DEFAULT_ETA_CSTAR. Bands are deliberately wide:
# the single-stage turbine specific-work model and the fuel-rich-gas cp/gamma are
# coarser physics than the isentropic-nozzle path (5% tolerance), and the
# literature gives a RANGE (fleet turbine PR 15.7-29; GG Isp loss 1/3-1% at
# 1000 psia [SP-8107 Table VI]), not a point value. The tool uses one shared
# turbine PR (22), so it cannot track per-engine PR spread - e.g. RD-0110's real
# PR is ~13.8, so the tool reads a bit below its real 4.2% bleed. See
# claude_lit/topics/{08,09,10} and claude_lit/sources/kbkha-turbopumps-aiaa2005.md.
GG_BLEED_CHECKS = [
    dict(name="F-1 (LOX/RP-1, GG cycle, Saturn V F-1)",
         pair="LOX/RP-1", pc_pa=7.0e6, mr=2.27, eps=16.0, thrust_n=7_770_000.0,
         bleed_lo=0.022, bleed_hi=0.048, turbine_staging="velocity_compounded_2row",
         note="real GG bleed ~3.0% (~77 of ~2578 kg/s); F-1's real turbine is a 2-row "
              "velocity-compounded stage (SP-8107 Table III), an exception among kerolox "
              "GG engines - given explicitly here. Lower band widened to 2.2% now that "
              "pump/turbine efficiency is derived (was a flat 0.72/0.75/0.62)"),
    dict(name="RD-0110 (LOX/RP-1, GG cycle, [KBKhA Table 2])",
         pair="LOX/RP-1", pc_pa=6.8e6, mr=2.20, eps=82.0, thrust_n=298_000.0,
         bleed_lo=0.024, bleed_hi=0.050,
         note="real turbine flow 3.97 of 93.8 kg/s = 4.23%; tool's fixed PR 22 vs "
              "RD-0110's real ~13.8 -> tool reads a bit low, same order"),
    dict(name="J-2 (LOX/LH2, GG cycle, Saturn upper-stage J-2)",
         pair="LOX/LH2", pc_pa=5.4e6, mr=5.5, eps=27.5, thrust_n=1_023_000.0,
         bleed_lo=0.008, bleed_hi=0.022, gate_isp_loss=True,
         note="real GG bleed ~1.3%; also gated on the [SP-8107 Table VI] GG Isp-loss "
              "band (1/3-1% at 1000 psia Pc, proportional to Pc), widened x2"),
]


def run_gg_flow_fraction_check():
    """
    Reproduce real gas-generator-cycle engines through the FULL
    EngineDesign.compute() pipeline (Bell@80% / impinging, matching
    run_integration_checks) and check the turbine-bleed flow fraction against
    published values.

    This is the check that would have caught the "GG bleed fraction is 5x too
    high for LOX/LH2" bug: design.py's GG turbine drive-gas properties (cp, gamma,
    Tin) were one global set calibrated to fuel-rich LOX/RP-1 gas, applied to
    every propellant. LOX/LH2's fuel-rich GG gas is hydrogen-rich (~4x the cp),
    so a J-2 reproduction demanded ~7.6% bleed instead of the real ~1.3%.
    GG_GAS_PROPERTIES is now per-pair; this check pins it there.
    """
    print()
    print("=" * 78)
    print("GAS-GENERATOR TURBINE-BLEED SPOT CHECK (full pipeline, Bell@80%/impinging)")
    print("=" * 78)
    all_ok = True
    for check in GG_BLEED_CHECKS:
        d = EngineDesign(propellant_pair=check["pair"], mixture_ratio=check["mr"],
                          chamber_pressure_pa=check["pc_pa"], expansion_ratio=check["eps"],
                          nozzle_type="bell", bell_percent_length=80.0,
                          cycle="gas_generator", injector_type="impinging",
                          turbine_staging=check.get("turbine_staging", "auto"),
                          target_vac_thrust_n=check["thrust_n"])
        r = d.compute()
        x = r["cycle_result"]["gg_flow_fraction"]
        bleed_ok = check["bleed_lo"] <= x <= check["bleed_hi"]

        # [SP-8107]'s figure is the GG DUMP loss alone: back out the regen-cooling
        # Isp credit design.py adds to the chamber stream (2026-09-23: now sized by
        # the recovered heat, ~0.3-0.8 % on a regen LH2 engine - enough to mask
        # the dump loss in a plain chamber-minus-engine difference).
        _credit = (r["cooling"]["regen_isp_bonus_fraction"]
                   * (1.0 - r["cycle_result"]["gg_fraction_of_total"]) * r["isp_vac_chamber_s"])
        isp_loss = (r["isp_vac_chamber_s"] - (r["isp_vac_engine_s"] - _credit)) / r["isp_vac_chamber_s"]
        pc_psia = check["pc_pa"] / 6894.76
        # [SP-8107 Table VI]: GG engine Isp loss ~= 1/3 to 1% at 1000 psia Pc,
        # proportional to Pc. Widen x2 for the coarse turbine model.
        band_lo = (1.0 / 3.0) * (pc_psia / 1000.0) / 100.0 / 2.0
        band_hi = 1.0 * (pc_psia / 1000.0) / 100.0 * 2.0
        isp_ok = (not check.get("gate_isp_loss")) or (band_lo <= isp_loss <= band_hi)

        # Flow/thrust accounting (2026-09-24 fix): the GG draw is EXTRA flow on
        # top of the chamber's, reported in mdot_kgs, and thrust = total flow x
        # the total-flow-averaged engine Isp (it used to be chamber flow x a
        # Isp that treated the chamber-relative bleed as a share of the total).
        _g0 = 9.80665
        _mt = r["mdot_chamber_kgs"] + r["cycle_result"]["gg_mdot_kgs"]
        acct_ok = (abs(r["mdot_kgs"] - _mt) <= 1e-9 * _mt
                   and abs(r["thrust_vac_n"] - r["mdot_kgs"] * r["isp_vac_engine_s"] * _g0)
                   <= 1e-9 * r["thrust_vac_n"])

        ok = bleed_ok and isp_ok and acct_ok
        all_ok &= ok
        print(f"\n{check['name']}  [{'OK' if ok else '*** FAIL ***'}]")
        print(f"  flow accounting: mdot {r['mdot_kgs']:.2f} = chamber {r['mdot_chamber_kgs']:.2f} "
              f"+ GG {r['cycle_result']['gg_mdot_kgs']:.2f} kg/s, thrust = mdot x engine Isp   "
              f"[{'OK' if acct_ok else 'FAIL'}]")
        print(f"  {check['note']}")
        print(f"  bleed fraction: {x*100:5.2f}%   allowed band {check['bleed_lo']*100:.1f}-"
              f"{check['bleed_hi']*100:.1f}%   [{'OK' if bleed_ok else 'FAIL'}]")
        if check.get("gate_isp_loss"):
            print(f"  engine Isp loss vs chamber: {isp_loss*100:.2f}%   "
                  f"SP-8107 band (x2) {band_lo*100:.2f}-{band_hi*100:.2f}%   "
                  f"[{'OK' if isp_ok else 'FAIL'}]")
        else:
            print(f"  engine Isp loss vs chamber: {isp_loss*100:.2f}%   (informational, not gated)")
    print()
    print("ALL GG-BLEED CHECKS OK" if all_ok else
          "*** GG-BLEED CHECK FAILED - review design.py GG_GAS_PROPERTIES ***")
    print("=" * 78)
    return all_ok


# Real turbopumps for the 1-D preliminary sizing (physics/turbopump_sizing.py).
# What is gate-able: the ARCHITECTURE it derives (shafts / turbine count) and
# rotor / tip speeds to the right ORDER OF MAGNITUDE. Bands are wide (factor
# ~2-3) on purpose - Ns-based 1-D sizing with one assumed head coefficient and
# no NPSH model is a preliminary estimate, not a point predictor (it over-
# predicts rotor speed for extreme high-head pumps a real designer slows with
# extra axial stages for cavitation margin). `mass_modifier == 1.0` for the
# auto architecture is asserted exactly - that is the regression guard that
# keeps every existing compute() result bit-for-bit.
TURBOPUMP_SIZING_CHECKS = [
    dict(name="F-1 (LOX/RP-1, GG) - single shaft, both pumps, 1 turbine",
         pair="LOX/RP-1", pc_pa=7.0e6, mr=2.27, eps=16.0, thrust_n=7_770_000.0,
         cycle="gas_generator", arrangement="single_shaft", n_turbines=1,
         real_shaft_rpm=5488.0, shaft_rpm_factor=2.2,
         real_mass_kg=1429.0, mass_factor=2.0),   # [SP-8107 Table I] assembly mass
    dict(name="J-2 (LOX/LH2, GG) - dual shaft, multistage LH2 pump, 2 turbines",
         pair="LOX/LH2", pc_pa=5.4e6, mr=5.5, eps=27.5, thrust_n=1_023_000.0,
         cycle="gas_generator", arrangement="dual_shaft", n_turbines=2,
         min_fuel_pump_stages=4, real_fuel_tip_m_s=264.0, fuel_tip_factor=2.5,
         real_mass_kg=305.0, mass_factor=2.0),
    dict(name="RD-0110 (LOX/RP-1, GG) - single shaft, 1 turbine, small/fast",
         pair="LOX/RP-1", pc_pa=6.8e6, mr=2.20, eps=82.0, thrust_n=298_000.0,
         cycle="gas_generator", arrangement="single_shaft", n_turbines=1,
         real_shaft_rpm=18_400.0, shaft_rpm_factor=3.0,
         real_mass_kg=90.0, mass_factor=2.2),
]


def run_turbopump_sizing_check():
    """
    Full-pipeline turbopump preliminary sizing (physics/turbopump_sizing.py)
    against real engines. Pins the derived architecture and the neutral-default
    contract (auto architecture -> mass_modifier == 1.0), and sanity-bounds
    rotor / tip speeds. See TURBOPUMP_SIZING_CHECKS for the (wide) bands.
    """
    print()
    print("=" * 78)
    print("TURBOPUMP SIZING SPOT CHECK (full pipeline, Bell@80%/impinging)")
    print("=" * 78)
    all_ok = True
    for check in TURBOPUMP_SIZING_CHECKS:
        d = EngineDesign(propellant_pair=check["pair"], mixture_ratio=check["mr"],
                          chamber_pressure_pa=check["pc_pa"], expansion_ratio=check["eps"],
                          nozzle_type="bell", bell_percent_length=80.0,
                          cycle=check["cycle"], injector_type="impinging",
                          target_vac_thrust_n=check["thrust_n"])
        s = d.compute()["turbopump_sizing"]

        arr_ok = s["arrangement"] == check["arrangement"]
        nt_ok = s["n_turbines"] == check["n_turbines"]
        mod_ok = abs(s["mass_modifier"] - 1.0) < 1e-12

        checks_ok = [("arrangement", arr_ok, f"{s['arrangement']} (want {check['arrangement']})"),
                     ("turbine count", nt_ok, f"{s['n_turbines']} (want {check['n_turbines']})"),
                     ("mass_modifier == 1.0", mod_ok, f"{s['mass_modifier']:.6f}")]

        if "real_shaft_rpm" in check:
            f = check["shaft_rpm_factor"]
            got = s["fuel_shaft_rpm"]
            rpm_ok = check["real_shaft_rpm"] / f <= got <= check["real_shaft_rpm"] * f
            checks_ok.append(("shaft rpm", rpm_ok,
                              f"{got:.0f} vs real {check['real_shaft_rpm']:.0f} (x{f})"))
        if "min_fuel_pump_stages" in check:
            st = s["fuel_pump"]["n_stages"]
            checks_ok.append(("fuel pump stages", st >= check["min_fuel_pump_stages"],
                              f"{st} (want >= {check['min_fuel_pump_stages']})"))
        if "real_fuel_tip_m_s" in check:
            f = check["fuel_tip_factor"]
            got = s["fuel_pump"]["u_tip_m_s"]
            tip_ok = check["real_fuel_tip_m_s"] / f <= got <= check["real_fuel_tip_m_s"] * f
            checks_ok.append(("fuel pump tip speed", tip_ok,
                              f"{got:.0f} m/s vs real {check['real_fuel_tip_m_s']:.0f} (x{f})"))
        if "real_mass_kg" in check:
            f = check["mass_factor"]
            got = s["mass_kg"]
            m_ok = check["real_mass_kg"] / f <= got <= check["real_mass_kg"] * f
            checks_ok.append(("assembly mass", m_ok,
                              f"{got:.0f} kg vs real {check['real_mass_kg']:.0f} (x{f})"))

        ok = all(c[1] for c in checks_ok)
        all_ok &= ok
        print(f"\n{check['name']}  [{'OK' if ok else '*** FAIL ***'}]")
        for label, cok, detail in checks_ok:
            print(f"  {label:22} {detail:44} [{'OK' if cok else 'FAIL'}]")
    print()
    print("ALL TURBOPUMP-SIZING CHECKS OK" if all_ok else
          "*** TURBOPUMP-SIZING CHECK FAILED - review physics/turbopump_sizing.py ***")
    print("=" * 78)
    return all_ok


def run_bearing_dn_check():
    """
    PLAUSIBILITY check only for the turbopump bearing-material catalog
    (physics/turbopump_materials.py BEARING_MATERIALS) - NOT a validated spot
    check against a real engine. No RealismOverhaul config exposes bearing
    bore or DN, and no source in claude_lit gives real turbopump bearing DN
    figures, so there is nothing to reverse-solve against (unlike every other
    SPOT_CHECKS-style function in this file). This only asserts:
      (1) DN scales in the right qualitative DIRECTION - a real high-speed
          LH2-class shaft (J-2-like) implies much higher bearing DN than a
          real dense-propellant shaft (F-1-like) at a comparable design, and
      (2) the three bearing materials are never inconsistently ordered - a
          material with a HIGHER max_dn_mm_rpm must never warn where a lower-
          capability one at the identical design does not.
    The 1.2M / 1.5M / 2.4M mm*rpm thresholds themselves are general aerospace
    rolling-element-bearing figures, NOT sourced from claude_lit - see
    ASSUMPTIONS.md. Trust the ORDERING this check pins, not the magnitudes.
    """
    print()
    print("=" * 78)
    print("BEARING DN PLAUSIBILITY CHECK (turbopump_materials.BEARING_MATERIALS - "
          "NOT a validated spot check, see docstring)")
    print("=" * 78)

    def _dn(pair, mr, pc_pa, eps, cycle, thrust_n, mat_key, bearing_key):
        d = EngineDesign(propellant_pair=pair, mixture_ratio=mr, chamber_pressure_pa=pc_pa,
                          expansion_ratio=eps, nozzle_type="bell", bell_percent_length=80.0,
                          cycle=cycle, injector_type="impinging", target_vac_thrust_n=thrust_n,
                          turbopump_material_key=mat_key, bearing_material_key=bearing_key)
        s = d.compute()["turbopump_sizing"]
        return max(s["fuel_bearing_dn"], s["ox_bearing_dn"])

    f1_dn = _dn("LOX/RP-1", 2.27, 7.0e6, 14.0, "gas_generator", 7_770_000.0,
                "inconel_718", "cronidur_30")
    j2_dn = _dn("LOX/LH2", 5.5, 5.42e6, 27.5, "gas_generator", 1_023_000.0,
                "titanium_forged", "cronidur_30")
    direction_ok = j2_dn > f1_dn
    print(f"\nDirection: F-1-class dense-propellant DN {f1_dn:,.0f} vs J-2-class "
          f"high-speed-LH2 DN {j2_dn:,.0f}   [{'OK' if direction_ok else 'FAIL'}]")

    # Monotonic ordering: at an IDENTICAL (extreme, high-rpm) design, a higher-
    # capability bearing material must never carry MORE bearing-DN warnings
    # than a lower-capability one. Called directly against
    # turbopump_sizing.size_turbopump (bypassing EngineDesign, same pattern as
    # that module's own __main__ "extreme" case) with an artificially tiny
    # flow so the DN sweep actually crosses all three thresholds - realistic
    # EngineDesign parameters don't reach 440C's 1.2M limit at all, which
    # would make this sub-check trivially (and uninformatively) pass.
    def _n_bearing_warnings(bearing_key):
        # mdot, mr, pc, dp_fuel, dp_ox, rho_fuel, rho_ox, eta_f, eta_ox, specific_power,
        # gg_tin_k, gg_cp, gg_eta_turbine, gg_pressure_ratio, gg_gamma - matching
        # turbopump_sizing.py's own __main__ J-2-ish case, but with an artificially
        # extreme fuel-pump head (single forced stage) so the resulting bearing DN
        # (~2.1M mm*rpm) actually falls BETWEEN the three materials' real 1.2M/1.5M/
        # 2.4M thresholds and differentiates them - realistic engine parameters stay
        # well under even 440C's limit, which would make this sub-check trivially
        # (and uninformatively) pass at 0 warnings for every material.
        dp_fuel_extreme = 250e6
        cyc = cycles.gas_generator_result(
            50.0, 5.5, 7.0e6, dp_fuel_extreme, 6.5e6, 71.0, 1141.0, 0.72, 0.75, 36000.0,
            1050.0, 2100.0, 0.62, 22.0, 1.13)
        cyc["turbine_specific_work_j_kg"] = 2.5e6
        s = turbopump_sizing.size_turbopump(
            cyc, dp_fuel_extreme, 6.5e6, 71.0, 1141.0, "LOX/LH2", 50_000.0, "gas_generator",
            "single_shaft", "auto", "titanium_forged", turbine_inlet_k=922.0,
            pump_stages_fuel=1, bearing_material_key=bearing_key)
        return sum(1 for w in s["warnings"] if "bearing DN" in w), s

    order_ok = True
    prev_n = None
    for bearing_key in ("440c_steel", "cronidur_30", "si3n4_ceramic"):
        n_warn, s = _n_bearing_warnings(bearing_key)
        dn = max(s["fuel_bearing_dn"], s["ox_bearing_dn"])
        if prev_n is not None and n_warn > prev_n:
            order_ok = False   # a higher-capability material warned MORE than a lower one
        prev_n = n_warn
        print(f"  {bearing_key:14} DN {dn:,.0f}   {n_warn} bearing-DN warning(s)   "
              f"[{'OK' if order_ok else 'FAIL'}]")
    all_ok = direction_ok and order_ok

    print()
    print("ALL BEARING-DN PLAUSIBILITY CHECKS OK" if all_ok else
          "*** BEARING-DN CHECK FAILED - review physics/turbopump_materials.py ***")
    print("=" * 78)
    return all_ok


def run_cycle_model_check():
    """
    Full-pipeline per-cycle physics (physics/staged_combustion.py,
    physics/electric_pump.py, the tap-off gas model) against real engines, one
    per distinct cycle. Bands are deliberately WIDE and documented: the tool's
    rotor speeds have no NPSH model. The staged cycles' preburner temperatures
    are design INPUTS (pair defaults sourced where possible - SSME 1113 K
    [ch12-materials], ox-rich 628 K [NK-33-Mod]) and the turbine PR is SOLVED
    (staged_combustion.solve_staged_power_balance); the quantitative pressure-
    chain spot checks live in run_staged_power_balance_check(). What this pins
    is that each cycle has DISTINCT, physically-correct-in-direction behaviour:
      - closed cycles (FRSC/ORSC/FFSC/electric) lose no Isp to an overboard dump;
      - the staged power balance CLOSES for each real engine (RD-180 and
        Raptor-2 only with an explicit hotter ox-rich preburner - see below);
      - ORSC routes most of the flow through the preburner, FRSC a fraction;
      - FFSC runs two turbines and preburns ~all of both propellants;
      - tap-off taps cooled main-chamber gas (below Tc) and keeps a good dump Isp;
      - electric pump-fed has no turbine and carries battery+motor as dry mass.
    """
    print()
    print("=" * 78)
    print("PER-CYCLE MODEL SPOT CHECK (full pipeline, Bell@80%/impinging)")
    print("=" * 78)
    all_ok = True

    def _design(**kw):
        kw.setdefault("nozzle_type", "bell")
        kw.setdefault("bell_percent_length", 80.0)
        kw.setdefault("injector_type", "impinging")
        return EngineDesign(**kw).compute()

    def _report(name, checks):
        nonlocal all_ok
        ok = all(c[1] for c in checks)
        all_ok &= ok
        print(f"\n{name}  [{'OK' if ok else '*** FAIL ***'}]")
        for label, cok, detail in checks:
            print(f"  {label:26} {detail:42} [{'OK' if cok else 'FAIL'}]")

    def _closed_cycle_isp_ok(r):
        """A closed cycle takes no overboard dump loss, so engine Isp must not
        fall below chamber Isp - but a regen-cooled chamber legitimately gains a
        small Isp credit (cooling.regen_isp_bonus_fraction, [Sutton 8.2]), so
        engine Isp a little ABOVE chamber Isp is expected, not a regression."""
        lo = r["isp_vac_chamber_s"] - 1e-6
        hi = r["isp_vac_chamber_s"] * (1.0 + cooling.REGEN_ISP_BONUS_MAX + 1e-6)
        return lo <= r["isp_vac_engine_s"] <= hi

    # --- RD-180: oxidiser-rich staged combustion, LOX/RP-1 --------------------
    r = _design(propellant_pair="LOX/RP-1", mixture_ratio=2.72, chamber_pressure_pa=26.66e6,
                expansion_ratio=36.4, cycle="orsc", turbopump_material_key="monel_k500",
                target_vac_thrust_n=4_152_000.0,
                # UNSOURCED: RD-180 does not close at the NK-33-sourced 628 K default
                # (26.66 MPa needs a hotter ox-rich preburner, ~>730 K). 800 K is a
                # Tier-3 estimate - no RD-170/180 preburner temperature in claude_lit/.
                ox_preburner_tin_k=800.0)
    c, s = r["cycle_result"], r["turbopump_sizing"]
    pbf = c["preburner_flow_fraction"]
    _report("RD-180 (ORSC, LOX/RP-1, 26.66 MPa, MR 2.72, ox preburner 800 K est.)", [
        ("oxidizer_rich flag", c["oxidizer_rich"] is True, f"{c['oxidizer_rich']}"),
        ("preburner flow fraction", 0.55 <= pbf <= 0.90, f"{pbf:.3f} (want 0.55-0.90)"),
        ("power balance closes", c["feasible"], f"margin {c['power_margin']:.2f}"),
        ("solved turbine PR 1.3-2.2", 1.3 <= c["turbine_pressure_ratio"] <= 2.2,
         f"{c['turbine_pressure_ratio']:.2f}"),
        ("engine Isp >= chamber Isp (no dump loss; regen credit ok)",
         _closed_cycle_isp_ok(r),
         f"{r['isp_vac_engine_s']:.1f} vs {r['isp_vac_chamber_s']:.1f} s"),
    ])

    # --- SSME: fuel-rich staged combustion, LOX/LH2 --------------------------
    r = _design(propellant_pair="LOX/LH2", mixture_ratio=6.0, chamber_pressure_pa=20.6e6,
                expansion_ratio=69.0, cycle="frsc", turbopump_material_key="powder_met_superalloy",
                target_vac_thrust_n=2_279_000.0)
    c, s = r["cycle_result"], r["turbopump_sizing"]
    pbf = c["preburner_flow_fraction"]
    _report("SSME (FRSC, LOX/LH2, 20.6 MPa, MR 6.0)", [
        ("oxidizer_rich flag", c["oxidizer_rich"] is False, f"{c['oxidizer_rich']}"),
        ("preburner flow fraction", 0.10 <= pbf <= 0.35, f"{pbf:.3f} (want 0.10-0.35)"),
        ("turbine inlet K (sourced 1113 K default)", 1050.0 <= s["turbine_inlet_k"] <= 1200.0,
         f"{s['turbine_inlet_k']:.0f} K (want 1050-1200)"),
        ("power balance closes", c["feasible"], f"margin {c['power_margin']:.2f}"),
        ("engine Isp >= chamber Isp (no dump loss; regen credit ok)",
         _closed_cycle_isp_ok(r),
         f"{r['isp_vac_engine_s']:.1f} vs {r['isp_vac_chamber_s']:.1f} s"),
    ])

    # --- RD-0124: small ORSC, LOX/RP-1 -------------------------------------
    r = _design(propellant_pair="LOX/RP-1", mixture_ratio=2.6, chamber_pressure_pa=15.7e6,
                expansion_ratio=94.0, cycle="orsc", turbopump_material_key="monel_k500",
                target_vac_thrust_n=294_000.0)
    c, s = r["cycle_result"], r["turbopump_sizing"]
    rpm, real_rpm = s["fuel_shaft_rpm"], 39_000.0
    _report("RD-0124 (ORSC, LOX/RP-1, 15.7 MPa, MR 2.6)", [
        ("oxidizer_rich flag", c["oxidizer_rich"] is True, f"{c['oxidizer_rich']}"),
        ("shaft rpm within x3.5 of real", real_rpm / 3.5 <= rpm <= real_rpm * 3.5,
         f"{rpm:.0f} vs real {real_rpm:.0f} (x3.5, no NPSH model)"),
    ])

    # --- J-2X (J-2S data): tap-off, LOX/LH2 ------------------------------
    # The J-2X's turbine exhaust is injected supersonically into its nozzle
    # extension through a manifold [J2X-Overview leaf 10-11, 13] -> nozzle_injection
    # (at the J-2's cited 10.9 - the J-2X's own station isn't in the paper).
    r = _design(propellant_pair="LOX/LH2", mixture_ratio=5.5, chamber_pressure_pa=9.22e6,
                expansion_ratio=92.0, cycle="tap_off", target_vac_thrust_n=1_307_000.0,
                turbine_exhaust_mode="nozzle_injection", turbine_exhaust_inject_eps=10.9)
    c = r["cycle_result"]
    tin = c["drive_gas"]["tin_k"]
    isp_loss_pct = 100.0 * (1.0 - r["isp_vac_engine_s"] / r["isp_vac_chamber_s"])
    _report("J-2X (tap-off, LOX/LH2, 9.22 MPa, MR 5.5)", [
        ("tap gas below chamber Tc", tin < r["tc_k"], f"{tin:.0f} K vs Tc {r['tc_k']:.0f} K"),
        ("tap gas in 850-1200 K", 850.0 <= tin <= 1200.0, f"{tin:.0f} K"),
        # computed by physics/turbine_exhaust.py since 2026-09-24 (was a flat 0.80)
        ("dump Isp fraction computed, 0.3-0.9", 0.3 <= c["gg_dump_isp_fraction"] <= 0.9,
         f"{c['gg_dump_isp_fraction']:.2f}"),
        ("engine Isp loss 0.1-2.0 %", 0.1 <= isp_loss_pct <= 2.0, f"{isp_loss_pct:.3f} %"),
    ])

    # --- Rutherford: electric pump-fed, LOX/RP-1 -----------------------------
    r = _design(propellant_pair="LOX/RP-1", mixture_ratio=2.5, chamber_pressure_pa=12.0e6,
                expansion_ratio=10.0, cycle="electric_pump", material_key="inconel_718",
                target_vac_thrust_n=26_000.0)
    c, s = r["cycle_result"], r["turbopump_sizing"]
    elec_mass = c["battery_mass_kg"] + c["motor_mass_kg"]
    # Band is wide + high: the derived pump-efficiency model is pessimistic for a
    # pump this small (~0.58) and the tool models no separate low-speed boost
    # pump, so shaft power (hence battery+motor) runs ~2x a real Rutherford. The
    # direction is the point: electric hardware is a large mass fraction.
    _report("Rutherford (electric pump-fed, LOX/RP-1, 12 MPa, 26 kN)", [
        ("n_turbines == 0", s["n_turbines"] == 0, f"{s['n_turbines']}"),
        ("battery+motor 15-140 kg", 15.0 <= elec_mass <= 140.0, f"{elec_mass:.0f} kg (wide, runs high)"),
        ("engine Isp >= chamber Isp (no dump loss; regen credit ok)",
         _closed_cycle_isp_ok(r),
         f"{r['isp_vac_engine_s']:.1f} vs {r['isp_vac_chamber_s']:.1f} s"),
        ("a warning is present", len(r["warnings"]) >= 1, f"{len(r['warnings'])} warning(s)"),
    ])

    # --- Raptor-2: full-flow staged combustion, real LOX/CH4 methalox --------
    r = _design(propellant_pair="LOX/CH4", mixture_ratio=3.55, chamber_pressure_pa=30.0e6,
                expansion_ratio=40.0, cycle="ffsc", turbopump_material_key="powder_met_superalloy",
                target_vac_thrust_n=2_255_000.0,
                # UNSOURCED, same as RD-180 above: at 30 MPa the ox-rich side needs
                # a hotter preburner than the 628 K default. Tier-3 estimate.
                ox_preburner_tin_k=800.0)
    c, s = r["cycle_result"], r["turbopump_sizing"]
    _report("Raptor-2 (FFSC, LOX/CH4, 30 MPa, MR 3.55, ox preburner 800 K est.)", [
        ("power balance closes (both preburners)", c["feasible"], f"margin {c['power_margin']:.2f}"),
        ("n_turbines == 2", s["n_turbines"] == 2, f"{s['n_turbines']}"),
        ("preburner flow fraction > 0.9", c["preburner_flow_fraction"] > 0.9,
         f"{c['preburner_flow_fraction']:.3f}"),
        ("no overboard dump", abs(c["gg_dump_isp_fraction"] - 1.0) < 1e-9,
         f"{c['gg_dump_isp_fraction']:.2f}"),
        ("vac Isp in 340-360 s", 340.0 <= r["isp_vac_engine_s"] <= 360.0,
         f"{r['isp_vac_engine_s']:.1f} s (real ~347)"),
        ("engine Isp >= chamber Isp (no dump loss; regen credit ok)",
         _closed_cycle_isp_ok(r),
         f"{r['isp_vac_engine_s']:.1f} vs {r['isp_vac_chamber_s']:.1f} s"),
    ])

    # --- BE-4: oxidiser-rich staged combustion, real LOX/CH4 methalox -------
    r = _design(propellant_pair="LOX/CH4", mixture_ratio=3.6, chamber_pressure_pa=13.4e6,
                expansion_ratio=40.0, cycle="orsc", turbopump_material_key="monel_k500",
                target_vac_thrust_n=2_647_500.0)
    c, s = r["cycle_result"], r["turbopump_sizing"]
    pbf = c["preburner_flow_fraction"]
    _report("BE-4 (ORSC, LOX/CH4, 13.4 MPa, MR 3.6)", [
        ("oxidizer_rich flag", c["oxidizer_rich"] is True, f"{c['oxidizer_rich']}"),
        ("preburner flow fraction", 0.55 <= pbf <= 0.90, f"{pbf:.3f} (want 0.55-0.90)"),
        ("power balance closes at the 628 K default", c["feasible"],
         f"margin {c['power_margin']:.2f}, PR {c['turbine_pressure_ratio']:.2f}"),
        ("vac Isp in 335-350 s", 335.0 <= r["isp_vac_engine_s"] <= 350.0,
         f"{r['isp_vac_engine_s']:.1f} s (real ~341)"),
        ("engine Isp >= chamber Isp (no dump loss; regen credit ok)",
         _closed_cycle_isp_ok(r),
         f"{r['isp_vac_engine_s']:.1f} vs {r['isp_vac_chamber_s']:.1f} s"),
    ])

    # --- FRSC vs ORSC distinctness (identical base design) -----------------
    base = dict(propellant_pair="LOX/RP-1", mixture_ratio=2.72, chamber_pressure_pa=25.5e6,
                expansion_ratio=36.0, turbopump_material_key="monel_k500",
                target_vac_thrust_n=4_150_000.0)
    rf = _design(cycle="frsc", **base)
    ro = _design(cycle="orsc", **base)

    def _rel(a, b):
        return abs(a - b) / max(abs(a), abs(b), 1e-9)

    d_tin = _rel(rf["turbopump_sizing"]["turbine_inlet_k"], ro["turbopump_sizing"]["turbine_inlet_k"])
    d_pbf = _rel(rf["cycle_result"]["preburner_flow_fraction"],
                 ro["cycle_result"]["preburner_flow_fraction"])
    d_head = _rel(rf["turbopump_sizing"]["fuel_pump"]["head_m"],
                  ro["turbopump_sizing"]["fuel_pump"]["head_m"])
    _report("FRSC vs ORSC distinctness (same base design)", [
        ("turbine inlet K differs > 5%", d_tin > 0.05,
         f"{rf['turbopump_sizing']['turbine_inlet_k']:.0f} vs "
         f"{ro['turbopump_sizing']['turbine_inlet_k']:.0f} K ({d_tin*100:.0f}%)"),
        ("preburner flow frac differs > 5%", d_pbf > 0.05,
         f"{rf['cycle_result']['preburner_flow_fraction']:.3f} vs "
         f"{ro['cycle_result']['preburner_flow_fraction']:.3f} ({d_pbf*100:.0f}%)"),
        ("fuel-pump head differs > 5%", d_head > 0.05,
         f"{rf['turbopump_sizing']['fuel_pump']['head_m']:.0f} vs "
         f"{ro['turbopump_sizing']['fuel_pump']['head_m']:.0f} m ({d_head*100:.0f}%)"),
    ])

    print()
    print("ALL CYCLE-MODEL CHECKS OK" if all_ok else
          "*** CYCLE-MODEL CHECK FAILED - review physics/staged_combustion.py / "
          "electric_pump.py / design.py tap-off ***")
    print("=" * 78)
    return all_ok


def run_feed_system_plausibility_check():
    """
    PLAUSIBILITY check only for the two feed-system warnings added alongside
    the jacket-overpressure check above: turbopump_sizing.size_pump's "wanted
    more stages than the modeled ceiling" flag, and
    turbopump_sizing.feed_dp_plausibility_warning's FEED_DP_PLAUSIBLE_CEILING_PA
    (55.2 MPa, cited [SP-8107 Tables V-VI] - see ASSUMPTIONS.md). Both exist
    because this tool always SOLVES a pump for whatever dP design.py demands -
    there is no independent pump-performance ceiling, so no "not enough flow
    reaches the chamber" failure mode is possible by construction; these
    flags are the honest proxy instead. This only asserts:
      (1) the tool's own reference GG design trips neither warning,
      (2) an artificially extreme FFSC case trips at least one, and
      (3) sweeping chamber pressure up on that extreme case flips the feed-dP
          warning on monotonically (no flapping back off).
    """
    print()
    print("=" * 78)
    print("FEED-SYSTEM PUMP PLAUSIBILITY CHECK (turbopump_sizing.py - NOT a "
          "validated spot check, see docstring)")
    print("=" * 78)

    def _warnings(chamber_pressure_pa, thrust_n, cycle=cycles.GAS_GENERATOR):
        d = EngineDesign(chamber_pressure_pa=chamber_pressure_pa,
                          target_vac_thrust_n=thrust_n, cycle=cycle)
        r = d.compute()
        stage_warn = any("pump stages" in w for w in r["warnings"])
        dp_warn = any("pump discharge dP" in w for w in r["warnings"])
        return stage_warn, dp_warn

    ref_stage, ref_dp = _warnings(7.0e6, 800_000.0)
    ref_ok = not ref_stage and not ref_dp
    print(f"\nReference GG design (Pc 7 MPa, 800 kN): stage_warn={ref_stage} "
          f"dp_warn={ref_dp}   [{'OK' if ref_ok else 'FAIL'}]")

    ext_stage, ext_dp = _warnings(3.5e7, 8.0e6, cycle=cycles.FFSC)
    ext_ok = ext_stage or ext_dp
    print(f"Extreme FFSC design (Pc 35 MPa, 8 MN): stage_warn={ext_stage} "
          f"dp_warn={ext_dp}   [{'OK' if ext_ok else 'FAIL'}]")

    sweep_pc = [1.0e7, 2.0e7, 2.8e7, 3.5e7]
    prev_on = False
    mono_ok = True
    for pc in sweep_pc:
        _, dp_warn = _warnings(pc, 8.0e6, cycle=cycles.FFSC)
        if prev_on and not dp_warn:
            mono_ok = False
        print(f"  Pc={pc/1e6:5.1f} MPa: dp_warn={dp_warn}   [{'OK' if mono_ok else 'FAIL'}]")
        prev_on = dp_warn

    all_ok = ref_ok and ext_ok and mono_ok
    print()
    print("ALL FEED-SYSTEM PLAUSIBILITY CHECKS OK" if all_ok else
          "*** FEED-SYSTEM PLAUSIBILITY CHECK FAILED - review physics/turbopump_sizing.py ***")
    print("=" * 78)
    return all_ok


def run_pump_pressure_chain_check():
    """
    Pump pressure-chain / power-balance spot checks (2026-09-23 round): the
    staged-combustion discharge is now BUILT from the real chain (main injector
    -> turbine -> preburner injector -> jacket -> lines, [SP-8107 3.1.1.1]) with
    the turbine PR SOLVED from a preburner temperature input, not a fixed
    discharge/Pc multiplier (staged_combustion.solve_staged_power_balance).

    Real anchors (claude_lit): SSME HPFTP 70,000 hp / 6800 psi discharge
    [ch12-materials]; SSME preburner 5880 psia at Pc 3237 psia and turbine PR
    1.56-1.59 [SP-8107 Tables I/III]; RD-0124 turbine-inlet P / LOX & kerosene
    discharge / turbine flow [KBKhA Table 2]; NK-33 preburner 2.21 x Pc at a
    628 K turbine inlet [NK-33-Mod Table I]. Pc/MR/thrust from Engine_Configs/.

    Known shortfall, REPORTED not tuned: NK-33's solved preburner/Pc runs ~18 %
    low (band +-20 %). The SSME power row compares pump work PER KG of fuel,
    because this Bell@80%/impinging design runs ~8 % below SSME's real Isp and so
    pumps ~19 % more fuel than the real engine - the real per-kg figure uses
    the RO config's 100 % point (2090 kN / 455.2 s, MR 6 -> 66.9 kg/s fuel);
    the literature doesn't state the power level of the 70,000 hp figure, so
    the band is +-25 %.
    """
    print()
    print("=" * 78)
    print("PUMP PRESSURE-CHAIN / POWER-BALANCE SPOT CHECK (full pipeline, Bell@80%/impinging)")
    print("=" * 78)
    all_ok = True

    def _within(val, real, tol):
        return abs(val / real - 1.0) <= tol

    def _row(label, ok, detail):
        nonlocal all_ok
        all_ok &= bool(ok)
        print(f"  {label:44s} {detail:44s} [{'OK' if ok else 'FAIL'}]")

    def _d(**kw):
        kw.setdefault("nozzle_type", "bell")
        kw.setdefault("bell_percent_length", 80.0)
        kw.setdefault("injector_type", "impinging")
        return EngineDesign(**kw).compute()

    # --- SSME (FRSC, LOX/LH2) -------------------------------------------------
    r = _d(propellant_pair="LOX/LH2", mixture_ratio=6.0, chamber_pressure_pa=20.6e6,
           expansion_ratio=69.0, cycle="frsc", turbopump_material_key="powder_met_superalloy",
           target_vac_thrust_n=2_279_000.0)
    c, tpw = r["cycle_result"], r["cycle_result"]["turbopump"]
    print("\nSSME (FRSC, LOX/LH2, 20.6 MPa, MR 6.0, default 1113 K preburner)")
    _row("power balance closes", c["feasible"], f"margin {c['power_margin']:.2f}")
    dis = c["pump_discharge_fuel_pa"]
    _row("fuel-pump discharge vs 46.9 MPa (+-15%)", _within(dis, 46.9e6, 0.15),
         f"{dis/1e6:.1f} MPa ({(dis/46.9e6-1)*100:+.0f}%)")
    ppc = c["preburner_pressure_pa"] / 20.6e6
    _row("preburner P / Pc vs 5880/3237=1.82 (+-15%)", _within(ppc, 1.82, 0.15),
         f"{ppc:.2f} ({(ppc/1.82-1)*100:+.0f}%)")
    pr = c["turbine_pressure_ratio"]
    _row("solved turbine PR in 1.3-2.0 (real 1.56-1.59)", 1.3 <= pr <= 2.0, f"{pr:.2f}")
    w_kg = tpw["power_fuel_w"] / tpw["mdot_fuel_kgs"]
    w_real = 70_000 * 745.7 / 66.9
    _row("fuel-pump work per kg fuel (+-25%)", _within(w_kg, w_real, 0.25),
         f"{w_kg/1e6:.3f} vs {w_real/1e6:.3f} MJ/kg ({(w_kg/w_real-1)*100:+.0f}%)")

    # --- RD-0124 (ORSC, LOX/kerosene) -------------------------------------------
    r = _d(propellant_pair="LOX/RP-1", mixture_ratio=2.6, chamber_pressure_pa=15.7e6,
           expansion_ratio=94.0, cycle="orsc", turbopump_material_key="monel_k500",
           target_vac_thrust_n=294_000.0)
    c = r["cycle_result"]
    print("\nRD-0124 (ORSC, LOX/RP-1, 15.7 MPa, MR 2.6, default 628 K preburner)")
    _row("power balance closes", c["feasible"], f"margin {c['power_margin']:.2f}")
    for label, val, real in (
            ("turbine-inlet P vs 29.98 MPa (+-20%)", c["preburner_pressure_pa"], 29.98e6),
            ("LOX-pump discharge vs 33.28 MPa (+-20%)", c["pump_discharge_ox_pa"], 33.28e6),
            # the kerosene pump's preburner-feed (kick) stage - the leg that
            # must reach the ox-rich preburner's injector
            ("kerosene kick-stage disch. vs 36.56 MPa (+-20%)", c["boost_discharge_fuel_pa"], 36.56e6),
            ("turbine flow vs 59.85 kg/s (+-20%)", c["gg_mdot_kgs"], 59.85)):
        unit, scale = ("kg/s", 1.0) if "flow" in label else ("MPa", 1e6)
        _row(label, _within(val, real, 0.20),
             f"{val/scale:.2f} {unit} ({(val/real-1)*100:+.0f}%)")

    # --- NK-33 (ORSC, LOX/kerosene, 1960s turbomachinery) -----------------------
    r = _d(propellant_pair="LOX/RP-1", mixture_ratio=2.59, chamber_pressure_pa=14.54e6,
           expansion_ratio=27.7, cycle="orsc", turbopump_material_key="monel_k500",
           turbopump_tech_key="early_simple", target_vac_thrust_n=1_681_600.0)
    c = r["cycle_result"]
    print("\nNK-33 (ORSC, LOX/RP-1, 14.54 MPa, MR 2.59, early_simple tier, 628 K)")
    _row("power balance closes", c["feasible"], f"margin {c['power_margin']:.2f}")
    ppc = c["preburner_pressure_pa"] / 14.54e6
    _row("preburner P / Pc vs 2.21 (+-20%, known low)", _within(ppc, 2.21, 0.20),
         f"{ppc:.2f} ({(ppc/2.21-1)*100:+.0f}%)")

    # --- RL10A-3-3 (expander, LOX/LH2): series turbine dP on the fuel leg -------
    r = _d(propellant_pair="LOX/LH2", mixture_ratio=5.0, chamber_pressure_pa=2.72e6,
           expansion_ratio=61.0, cycle="expander", material_key="narloy_z",
           target_vac_thrust_n=70_050.0)
    c = r["cycle_result"]
    print("\nRL10A-3-3 (expander, LOX/LH2, 2.72 MPa, MR 5.0)")
    dpc = c["pump_discharge_fuel_pa"] / 2.72e6
    _row("fuel-pump discharge / Pc vs 2.5 (+-20%)", _within(dpc, 2.5, 0.20),
         f"{dpc:.2f} ({(dpc/2.5-1)*100:+.0f}%)  [SP-8107 p.25]")
    _row("expander still feasible", c["feasibility_margin"] >= 1.0,
         f"margin {c['feasibility_margin']:.2f}")

    # --- plausibility (not spot checks) ---------------------------------------
    print("\nPlausibility (direction, not magnitude):")
    # [Tripropellant-CR150444]: fuel-rich LOX/hydrocarbon preburners were
    # power-infeasible at ~4000 psia-class Pc (needed > 2200 R turbine inlet).
    r = _d(propellant_pair="LOX/RP-1", mixture_ratio=2.72, chamber_pressure_pa=27.6e6,
           expansion_ratio=36.0, cycle="frsc", turbopump_material_key="monel_k500",
           target_vac_thrust_n=4_150_000.0)
    c = r["cycle_result"]
    flagged = (not c["feasible"]) or c["turbine_pressure_ratio"] > 2.0
    _row("fuel-rich kerolox FRSC @ 27.6 MPa is flagged", flagged,
         f"feasible={c['feasible']} PR {c['turbine_pressure_ratio']:.2f}")
    # discharge/Pc rises with Pc (SP-8107 Table VI "nonlinear ... may exceed 2 x Pc")
    ratios = []
    for pc in (8e6, 11e6, 14.54e6, 18e6):
        rr = _d(propellant_pair="LOX/RP-1", mixture_ratio=2.59, chamber_pressure_pa=pc,
                expansion_ratio=27.7, cycle="orsc", turbopump_material_key="monel_k500",
                target_vac_thrust_n=1_681_600.0)["cycle_result"]
        ratios.append(rr["drive_discharge_over_pc"])
    mono = all(b > a for a, b in zip(ratios, ratios[1:]))
    _row("ORSC drive discharge/Pc rises with Pc", mono, " -> ".join(f"{x:.2f}" for x in ratios))
    # the RD-180 class does NOT close at the sourced 628 K default
    c = _d(propellant_pair="LOX/RP-1", mixture_ratio=2.72, chamber_pressure_pa=26.66e6,
           expansion_ratio=36.4, cycle="orsc", turbopump_material_key="monel_k500",
           target_vac_thrust_n=4_152_000.0)["cycle_result"]
    _row("RD-180 class @ 628 K default is infeasible", not c["feasible"],
         f"margin {c['power_margin']:.2f} (needs a hotter preburner)")

    print()
    print("ALL PUMP PRESSURE-CHAIN CHECKS OK" if all_ok else
          "*** PUMP PRESSURE-CHAIN CHECK FAILED - review physics/staged_combustion.py / "
          "design.py cycle branches ***")
    print("=" * 78)
    return all_ok
