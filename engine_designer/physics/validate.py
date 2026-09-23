"""
Reusable physics self-checks + one real-engine spot-check per propellant
pair. Run via:  python3 -m engine_designer.physics.validate
(from /home/cory/ksp_config)

This plays the same role sim/h4_report.py's RD-111 spot-check played for
the H-4 one-off: don't trust the physics for a new design until it can
reproduce a known real engine's Isp within a few percent.

Real engines use contoured bell nozzles, not the simple cones this tool's
schematic draws, so the spot-check uses nozzle_divergence_efficiency's
lambda = 1.0 (no divergence loss) - the remaining efficiency gap
(combustion + real-nozzle + engine-size/maturity effects) is absorbed by
combustion.DEFAULT_ETA_CSTAR, which is WHY these spot checks exist: they are
what sets those three constants, not just what verifies them.

Sea-level Isp is only a meaningful, gated comparison for a nozzle that's
actually attached at sea level (RD-111, eps 18 at Pc 7.85 MPa). RL10A-3-3
(eps 61) and Aestus (eps 84) are vacuum/upper-stage nozzles that never fire
at sea level - RO's own file comments flag their "SL Isp" as an RPA-nominal
figure, and the ideal fully-expanded formula used here goes unphysical
(even negative) that deep into over-expansion. Those two are reported as
informational only, not gated on tolerance.
"""
import math

import numpy as np

from . import (combustion, combustion_stability, cooling, cycles, expander, geometry,
               isentropic as iso, mass_model, materials, nozzle_shapes, turbopump_sizing,
               turbopump_tech)
from .design import EngineDesign

TOLERANCE_PCT = 5.0
INTEGRATION_TOLERANCE_PCT = 2.0
PA_SEA_LEVEL = 101_325.0

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
    tc, gamma, m_molar = combustion.combustion_state(pair, mr)
    eta_cstar = combustion.DEFAULT_ETA_CSTAR[pair]
    mach = iso.mach_from_area_ratio(eps, gamma)
    pe_pc = iso.pe_over_pc(mach, gamma)
    pe_pa = pe_pc * pc_pa
    cstar = iso.c_star(tc, gamma, m_molar, eta_cstar)
    cf_vac = iso.cf_vacuum(gamma, pe_pc, eps)  # lambda = 1.0, see module docstring
    cf_sl = cf_vac - eps * (PA_SEA_LEVEL / pc_pa)
    isp_vac = iso.isp_from_cf(cstar, cf_vac)
    isp_sl = iso.isp_from_cf(cstar, cf_sl)
    separated = iso.is_separated(pe_pa, PA_SEA_LEVEL)
    return tc, gamma, eta_cstar, isp_vac, isp_sl, separated


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
              f"eta_cstar={eta_cstar}  -> Tc={tc:.0f} K, gamma={gamma:.4f}")
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
          "*** ONE OR MORE GATED SPOT CHECKS OUT OF TOLERANCE - review DEFAULT_ETA_CSTAR / tables ***")
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


def run_contraction_ratio_sensitivity_check():
    """
    New (item 1): contraction ratio now drives chamber-wall heat flux via a
    damped Bartz area-ratio term (materials.contraction_ratio_heat_flux_factor)
    feeding materials.thermal_margin(). This should move margin_ratio
    monotonically across the full CR slider range, stay within the module's
    defensive clamp, and be EXACTLY neutral (factor == 1.0) at the CR=1.6
    default that validate.py's other checks above implicitly use - so this
    change can't have altered any of the results already gated above.
    """
    print()
    print("=" * 78)
    print("CONTRACTION-RATIO THERMAL-MARGIN SENSITIVITY CHECK")
    print("=" * 78)
    tc_k = 3700.0          # representative LOX/RP-1-class chamber temperature
    material_key = "narloy_z"
    crs = np.linspace(1.3, 6.0, 20)
    factors = [materials.contraction_ratio_heat_flux_factor(cr) for cr in crs]
    margins = [materials.thermal_margin(material_key, tc_k, hf)["margin_ratio"] for hf in factors]

    ref_factor = materials.contraction_ratio_heat_flux_factor(1.6)
    ok_reference = abs(ref_factor - 1.0) < 1e-9
    ok_monotonic = all(a > b for a, b in zip(factors, factors[1:]))   # strictly decreasing in CR
    lo, hi = materials.HEAT_FLUX_FACTOR_CLAMP
    ok_bounds = all(lo <= f <= hi for f in factors)

    print(f"  factor(CR=1.6) == 1.0 exactly: {ref_factor:.6f}  [{'OK' if ok_reference else 'FAIL'}]")
    print(f"  factor(CR) strictly decreasing over [1.3, 6.0]: [{'OK' if ok_monotonic else 'FAIL'}]")
    print(f"  factor(CR) within [{lo}, {hi}] over the whole range: "
          f"[{'OK' if ok_bounds else 'FAIL'}] (min {min(factors):.3f}, max {max(factors):.3f})")
    print(f"  margin_ratio(CR=1.3)={margins[0]:.3f}  margin_ratio(CR=6.0)={margins[-1]:.3f}")
    all_ok = ok_reference and ok_monotonic and ok_bounds
    print("ALL CR-SENSITIVITY CHECKS OK" if all_ok else "*** CR-SENSITIVITY CHECK FAILED ***")
    print("=" * 78)
    return all_ok


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

        isp_loss = (r["isp_vac_chamber_s"] - r["isp_vac_engine_s"]) / r["isp_vac_chamber_s"]
        pc_psia = check["pc_pa"] / 6894.76
        # [SP-8107 Table VI]: GG engine Isp loss ~= 1/3 to 1% at 1000 psia Pc,
        # proportional to Pc. Widen x2 for the coarse turbine model.
        band_lo = (1.0 / 3.0) * (pc_psia / 1000.0) / 100.0 / 2.0
        band_hi = 1.0 * (pc_psia / 1000.0) / 100.0 * 2.0
        isp_ok = (not check.get("gate_isp_loss")) or (band_lo <= isp_loss <= band_hi)

        ok = bleed_ok and isp_ok
        all_ok &= ok
        print(f"\n{check['name']}  [{'OK' if ok else '*** FAIL ***'}]")
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


# Real regen-cooled engines for the wall-heat-flux model (physics/cooling.py).
# Phase 7: the flux MAGNITUDE is now the computed-absolute Bartz value
# (physics/cooling.absolute_heat_flux_profile), calibrated PER PROPELLANT CLASS
# against these same real engines (physics/cooling.BARTZ_ABS_FLUX_CALIBRATION),
# not shape-normalised to a flat propellant-agnostic anchor - so absolute
# throat MW/m2 is now a genuinely gated quantity, not just reported. What's
# gated: (1) jet-power-to-walls fraction in the literature band [Sutton 8.2:
# 0.5-5%, widened per-engine for a small/low-Pc surface-to-volume effect and
# the coarse model]; (2) the profile peaks at the throat and isn't absurdly
# spiky; (3) the chamber-average flux is within a wide sanity band of the OLD
# flat anchor (reported, not tight - the whole point of the per-class
# calibration is that LOX/LH2 and LOX/RP-1 designs now genuinely differ, see
# cooling.BARTZ_ABS_FLUX_CALIBRATION's module comment); (4) real Bartz h_g and
# computed hot-gas-wall temperature.
# T_wg against the liner limit is allowed to run right up to / just past it for
# the two engines whose real throats did (SSME cracked; the F-1 copper wall sat
# near its limit).
T_WG_LO_K = 450.0
# jacket_dp bands (regen_channel_model="channels") are deliberately wide / order-
# of-magnitude, like the flux-magnitude bands above: the 1-D single-pass march is
# calibrated to ONE reference design (see cooling.CHANNEL_DP_CALIBRATION and
# CHANNELS_REF_DP_* below); away from it, "trust the direction" (a small-throat
# low-Pc engine like RL10 genuinely runs a tighter jacket -> higher dP).
COOLING_CHECKS = [
    dict(name="F-1 (LOX/RP-1, GG, Saturn V, regen NARloy-Z-class)",
         pair="LOX/RP-1", pc_pa=7.0e6, mr=2.27, eps=16.0, thrust_n=7_770_000.0,
         cycle="gas_generator", material="narloy_z",
         e_frac_lo=0.004, e_frac_hi=0.05, min_coolant_dt_k=20.0,
         q_throat_lo_mw=8.0, q_throat_hi_mw=45.0, hg_lo=2500.0, hg_hi=20000.0,
         t_wg_hi_k=1000.0, dp_lo_mpa=0.25, dp_hi_mpa=2.5),
    dict(name="SSME-class (LOX/LH2, FRSC, high-Pc regen)",
         pair="LOX/LH2", pc_pa=20.6e6, mr=6.0, eps=69.0, thrust_n=2_200_000.0,
         cycle="frsc", material="narloy_z",
         e_frac_lo=0.004, e_frac_hi=0.05, max_coolant_dt_k=500.0,
         q_throat_lo_mw=18.0, q_throat_hi_mw=140.0, hg_lo=12000.0, hg_hi=60000.0,
         t_wg_hi_k=1050.0, dp_lo_mpa=0.2, dp_hi_mpa=4.0),
    dict(name="RL10-class (LOX/LH2, expander, small upper stage)",
         pair="LOX/LH2", pc_pa=3.2e6, mr=5.5, eps=61.0, thrust_n=73_000.0,
         cycle="expander", material="narloy_z",
         e_frac_lo=0.002, e_frac_hi=0.08, max_coolant_dt_k=500.0,
         q_throat_lo_mw=3.0, q_throat_hi_mw=22.0, hg_lo=3000.0, hg_hi=30000.0,
         t_wg_hi_k=1000.0, dp_lo_mpa=0.5, dp_hi_mpa=5.0),
]
# Neutral-default regression: the reference regen design in "channels" mode must
# reproduce the tool's long-standing flat JACKET_DP_PA (1.6 MPa) to within a few
# percent, so flipping regen_channel_model does not move the GG-bleed / cycle /
# turbopump spot checks.
CHANNELS_REF_DP_TARGET_PA = 1.6e6
CHANNELS_REF_DP_TOL = 0.08


def run_cooling_heat_flux_check():
    """
    Full-pipeline wall-heat-flux model (physics/cooling.py) against real
    regen-cooled engines. This is the spot check that pins the cooling model
    the way SPOT_CHECKS pins DEFAULT_ETA_CSTAR and GG_BLEED_CHECKS pins
    GG_GAS_PROPERTIES. See COOLING_CHECKS for what is / isn't gated and why.
    """
    print()
    print("=" * 78)
    print("WALL HEAT-FLUX SPOT CHECK (full pipeline, Bell@80%/impinging)")
    print("=" * 78)
    all_ok = True
    for check in COOLING_CHECKS:
        d = EngineDesign(propellant_pair=check["pair"], mixture_ratio=check["mr"],
                          chamber_pressure_pa=check["pc_pa"], expansion_ratio=check["eps"],
                          nozzle_type="bell", bell_percent_length=80.0,
                          cycle=check["cycle"], injector_type="impinging",
                          material_key=check["material"], target_vac_thrust_n=check["thrust_n"])
        c = d.compute()["cooling"]

        e_frac = c["wall_heat_energy_fraction"]
        e_ok = check["e_frac_lo"] <= e_frac <= check["e_frac_hi"]

        peak_over_avg = c["q_throat_w_m2"] / c["q_chamber_avg_w_m2"]
        shape_ok = 1.5 <= peak_over_avg <= 12.0

        # Reported comparison vs the pre-Phase-7 flat anchor - wide sanity band
        # only (0.3-3x): the per-propellant-class calibration DELIBERATELY lets
        # LOX/LH2 and LOX/RP-1 designs land at different ratios to it now.
        anchor = c["q_chamber_avg_anchor_w_m2"]
        vs_anchor_ratio = c["q_chamber_avg_w_m2"] / anchor if anchor else 0.0
        anchor_ok = 0.3 <= vs_anchor_ratio <= 3.0

        dt = c["coolant_delta_t_k"]
        dt_ok = True
        if "min_coolant_dt_k" in check:
            dt_ok = dt_ok and dt >= check["min_coolant_dt_k"]
        if "max_coolant_dt_k" in check:
            dt_ok = dt_ok and dt <= check["max_coolant_dt_k"]

        # NEW: real Bartz h_g, throat flux magnitude and computed wall temperature.
        q_throat_mw = c["q_throat_w_m2"] / 1e6
        q_throat_ok = check["q_throat_lo_mw"] <= q_throat_mw <= check["q_throat_hi_mw"]
        hg = c["hg_throat_w_m2k"]
        hg_ok = check["hg_lo"] <= hg <= check["hg_hi"]
        t_wg = c["t_wg_throat_k"]
        t_wg_ok = T_WG_LO_K <= t_wg <= check["t_wg_hi_k"]

        # Coolant-channel model (regen_channel_model="channels"): a real
        # Darcy-Weisbach jacket dP in place of the flat constant. Wide band.
        d_ch = EngineDesign(
            propellant_pair=check["pair"], mixture_ratio=check["mr"],
            chamber_pressure_pa=check["pc_pa"], expansion_ratio=check["eps"],
            nozzle_type="bell", bell_percent_length=80.0, cycle=check["cycle"],
            injector_type="impinging", material_key=check["material"],
            target_vac_thrust_n=check["thrust_n"], regen_channel_model="channels")
        c_ch = d_ch.compute()["cooling"]
        dp_mpa = c_ch["jacket_dp_pa"] / 1e6
        dp_ok = check["dp_lo_mpa"] <= dp_mpa <= check["dp_hi_mpa"]

        ok = (e_ok and shape_ok and anchor_ok and dt_ok and q_throat_ok and hg_ok
              and t_wg_ok and dp_ok)
        all_ok &= ok
        print(f"\n{check['name']}  [{'OK' if ok else '*** FAIL ***'}]")
        print(f"  jet-power fraction to walls: {e_frac*100:.2f}%   band "
              f"{check['e_frac_lo']*100:.1f}-{check['e_frac_hi']*100:.1f}%   [{'OK' if e_ok else 'FAIL'}]")
        print(f"  throat peak / chamber-avg flux: {peak_over_avg:.2f}x   allowed 1.5-12x   "
              f"[{'OK' if shape_ok else 'FAIL'}]")
        print(f"  chamber-avg flux (computed-absolute, per-class calibrated): "
              f"{c['q_chamber_avg_w_m2']/1e6:.2f} MW/m2 vs pre-Phase-7 anchor {anchor/1e6:.2f} "
              f"MW/m2 ({vs_anchor_ratio:.2f}x)   [{'OK' if anchor_ok else 'FAIL'}]")
        print(f"  regen coolant dT: {dt:.0f} K (limit {c['coolant_limit_k']})   [{'OK' if dt_ok else 'FAIL'}]")
        print(f"  Bartz h_g throat: {hg:.0f} W/m2/K   band {check['hg_lo']:.0f}-{check['hg_hi']:.0f}   "
              f"[{'OK' if hg_ok else 'FAIL'}]")
        print(f"  throat flux: {q_throat_mw:.1f} MW/m2   band {check['q_throat_lo_mw']:.0f}-"
              f"{check['q_throat_hi_mw']:.0f}   [{'OK' if q_throat_ok else 'FAIL'}]")
        print(f"  computed wall temp T_wg: {t_wg:.0f} K   band {T_WG_LO_K:.0f}-{check['t_wg_hi_k']:.0f} "
              f"(T_aw {c['t_aw_chamber_k']:.0f} K)   [{'OK' if t_wg_ok else 'FAIL'}]")
        print(f"  wall heat {c['wall_heat_total_w']/1e6:.1f} MW, through-wall dT "
              f"{c['through_wall_delta_t_k']:.0f} K, throat fatigue ~{c['throat_fatigue_cycles']:,.0f} "
              f"cycles  (informational)")
        print(f"  channels-mode jacket dP: {dp_mpa:.2f} MPa ({c_ch['coolant_channels']} ch, "
              f"Dh_throat {c_ch['coolant_channel_dh_throat_m']*1e3:.2f} mm)   band "
              f"{check['dp_lo_mpa']:.1f}-{check['dp_hi_mpa']:.1f}   [{'OK' if dp_ok else 'FAIL'}]")

    # Fuel-film cooling as a length-decaying curtain (physics/cooling.
    # film_effectiveness_profile), against the F-1 (~10% of fuel ran as a
    # boundary curtain). Diffed against the no-film F-1 design above.
    f1 = next(c for c in COOLING_CHECKS if c["name"].startswith("F-1"))
    film_kw = dict(propellant_pair=f1["pair"], mixture_ratio=f1["mr"],
                    chamber_pressure_pa=f1["pc_pa"], expansion_ratio=f1["eps"],
                    nozzle_type="bell", bell_percent_length=80.0, cycle=f1["cycle"],
                    injector_type="impinging", material_key=f1["material"],
                    target_vac_thrust_n=f1["thrust_n"])
    fc0 = EngineDesign(**film_kw).compute()
    fc6 = EngineDesign(**film_kw, film_cooling_fraction=0.06).compute()
    fc2 = EngineDesign(**film_kw, film_cooling_fraction=0.02).compute()
    c0, c6, c2 = fc0["cooling"], fc6["cooling"], fc2["cooling"]
    eff6 = c6["film_flux_factor_effective"]
    twg_drop = c0["t_wg_throat_k"] - c6["t_wg_throat_k"]
    eta_drop_pct = 100.0 * (fc0["eta_cstar"] - fc6["eta_cstar"]) / fc0["eta_cstar"]
    isp_move_pct = 100.0 * abs(fc6["isp_vac_engine_s"] - fc0["isp_vac_engine_s"]) / fc0["isp_vac_engine_s"]
    film_ok = (0.55 <= eff6 <= 0.85
               and 80.0 <= twg_drop <= 400.0 and c6["t_wg_throat_k"] <= 800.0
               and 2.0 <= eta_drop_pct <= 6.0
               and isp_move_pct <= 5.5
               and f1["e_frac_lo"] <= c6["wall_heat_energy_fraction"] <= f1["e_frac_hi"]
               and 0.85 <= c2["film_flux_factor_effective"] <= 0.97
               and float(np.min(c6["film_effectiveness_profile"][-3:])) >= 0.8)  # recovers by the nozzle
    all_ok &= film_ok
    print(f"\nFUEL-FILM CURTAIN (F-1, 6% film vs none)  [{'OK' if film_ok else '*** FAIL ***'}]")
    print(f"  area-avg flux factor {eff6:.2f} (2% -> {c2['film_flux_factor_effective']:.2f}),  "
          f"throat T_wg {c0['t_wg_throat_k']:.0f} -> {c6['t_wg_throat_k']:.0f} K ({twg_drop:+.0f}),  "
          f"eta_c -{eta_drop_pct:.1f}%,  Isp {isp_move_pct:.1f}%,  "
          f"nozzle phi recovers to {float(np.min(c6['film_effectiveness_profile'][-3:])):.2f}   "
          f"[{'OK' if film_ok else 'FAIL'}]")

    # Regenerative nozzle continuation (EngineDesign.regen_nozzle_end_eps): the
    # ONE cooled-length number (cooling.cooled_length_eps) pushed past the
    # bell-material transition for a full-length regen nozzle (SSME/RL10-style).
    # jacket_dp_pa (pump-feed side) comes from a cheap early conical-contour
    # estimate that's coarse in the divergent section by design ("contributes
    # almost nothing to jacket dP" - see design.py) so it is NOT gated here;
    # what IS gated is what the authoritative march (on the real bell contour)
    # actually resolves: cooled area, coolant dT, and (for expander) the heat
    # pickup driving the turbine.
    ssme = next(c for c in COOLING_CHECKS if c["name"].startswith("SSME"))
    ssme_kw = dict(propellant_pair=ssme["pair"], mixture_ratio=ssme["mr"],
                    chamber_pressure_pa=ssme["pc_pa"], expansion_ratio=ssme["eps"],
                    nozzle_type="bell", bell_percent_length=80.0, cycle=ssme["cycle"],
                    injector_type="impinging", material_key=ssme["material"],
                    target_vac_thrust_n=ssme["thrust_n"])
    s6 = EngineDesign(**ssme_kw).compute()
    s20 = EngineDesign(**ssme_kw, regen_nozzle_end_eps=20.0).compute()
    s45 = EngineDesign(**ssme_kw, regen_nozzle_end_eps=45.0).compute()
    areas = [expander.cooled_surface_area(r["profile_xs_m"], r["profile_rs_m"],
                                          r["geometry"]["throat_dia_m"],
                                          cutoff_area_ratio=r["cooling"]["cooled_length_eps"])
             for r in (s6, s20, s45)]
    dts = [r["cooling"]["coolant_delta_t_k"] for r in (s6, s20, s45)]
    ssme_ok = (areas[0] < areas[1] < areas[2]
               and dts[0] < dts[1] < dts[2] <= cooling.MAX_COOLANT_DELTA_T_K["LOX/LH2"]
               and all(r["cooling"]["regen_isp_bonus_fraction"] <= cooling.REGEN_ISP_BONUS_MAX
                       for r in (s6, s20, s45))
               and s45["cooling"]["cooled_length_eps"] == 45.0)
    all_ok &= ssme_ok
    print(f"\nREGEN NOZZLE CONTINUATION (SSME-class, eps 6/20/45)  [{'OK' if ssme_ok else '*** FAIL ***'}]")
    print(f"  cooled area {areas[0]:.3f} -> {areas[1]:.3f} -> {areas[2]:.3f} m2,  "
          f"coolant dT {dts[0]:.0f} -> {dts[1]:.0f} -> {dts[2]:.0f} K (limit "
          f"{cooling.MAX_COOLANT_DELTA_T_K['LOX/LH2']:.0f})   [{'OK' if ssme_ok else 'FAIL'}]")

    # RL10-class (expander): heat pickup driving the turbine grows with the
    # cooled nozzle length, so feasibility margin should IMPROVE, not just hold.
    rl10 = next(c for c in COOLING_CHECKS if c["name"].startswith("RL10"))
    rl10_kw = dict(propellant_pair=rl10["pair"], mixture_ratio=rl10["mr"],
                    chamber_pressure_pa=rl10["pc_pa"], expansion_ratio=rl10["eps"],
                    nozzle_type="bell", bell_percent_length=80.0, cycle=rl10["cycle"],
                    injector_type="impinging", material_key=rl10["material"],
                    target_vac_thrust_n=rl10["thrust_n"])
    e6 = EngineDesign(**rl10_kw).compute()
    e61 = EngineDesign(**rl10_kw, regen_nozzle_end_eps=61.0).compute()
    m6 = e6["cycle_result"]["feasibility_margin"]
    m61 = e61["cycle_result"]["feasibility_margin"]
    dt6 = e6["cooling"]["coolant_delta_t_k"]
    dt61 = e61["cooling"]["coolant_delta_t_k"]
    rl10_ok = (m61 > m6 > 0.0 and dt61 > dt6
               and dt61 <= cooling.MAX_COOLANT_DELTA_T_K["LOX/LH2"]
               and e61["cooling"]["cooled_length_eps"] == 61.0)
    all_ok &= rl10_ok
    print(f"RL10-CLASS full-length regen (expander)  [{'OK' if rl10_ok else '*** FAIL ***'}]")
    print(f"  feasibility margin {m6:.2f}x -> {m61:.2f}x,  coolant dT {dt6:.0f} -> {dt61:.0f} K   "
          f"[{'OK' if rl10_ok else 'FAIL'}]")

    # Phase 7 docstring guarantee: physics/design.py's wall_heat_total_w() and
    # physics/expander.py's heat_pickup_w() must integrate the IDENTICAL
    # computed-absolute Bartz profile over the same contour/cutoff, so the
    # cooling-model's reported wall heat and the expander cycle's heat budget
    # can't silently disagree.
    e6_heat_from_cooling = e6["cooling"]["wall_heat_total_w"]
    e6_heat_from_expander = e6["cycle_result"]["heat_pickup_w"]
    heat_match_ok = abs(e6_heat_from_cooling - e6_heat_from_expander) < 1.0
    all_ok &= heat_match_ok
    print(f"  wall_heat_total_w == expander heat_pickup_w: {e6_heat_from_cooling/1e3:.2f} kW "
          f"vs {e6_heat_from_expander/1e3:.2f} kW   [{'OK' if heat_match_ok else 'FAIL'}]")
    # Pre-Phase-7 snapshot (flat anchor, eps 6 default): feasibility_margin was
    # 2.786. The per-class-calibrated computed-absolute flux moves this
    # substantially (the flat anchor had NO engine-throat-size dependence at
    # all; Bartz h_g's real Dt^-0.2 term means a small low-Pc expander chamber
    # like RL10 picks up genuinely more heat per unit Pc than the old anchor
    # assumed - not a regression, the tool now shows expander cycles as more
    # feasible for small/low-Pc LH2 designs than before). Reported, not gated
    # to the original +/-20% guess - that target didn't survive contact with
    # the real physics; see the Phase 7 checkpoint for the full explanation.
    pre_phase7_margin = 2.786
    margin_move_pct = 100.0 * (m6 - pre_phase7_margin) / pre_phase7_margin
    print(f"  feasibility margin vs pre-Phase-7 snapshot: {m6:.3f}x vs {pre_phase7_margin:.3f}x "
          f"({margin_move_pct:+.0f}%)   (informational)")

    # Neutral-default: regen_nozzle_end_eps=0.0 leaves cooled_length_eps (and so
    # everything downstream) untouched.
    neutral_a = EngineDesign(cycle="gas_generator").compute()
    neutral_b = EngineDesign(cycle="gas_generator", regen_nozzle_end_eps=0.0).compute()
    neutral_ok = (neutral_a["isp_vac_engine_s"] == neutral_b["isp_vac_engine_s"]
                  and neutral_a["cooling"]["cooled_length_eps"] == neutral_b["cooling"]["cooled_length_eps"]
                  and neutral_a["cooling"]["jacket_dp_pa"] == neutral_b["cooling"]["jacket_dp_pa"])
    all_ok &= neutral_ok
    print(f"neutral-default (regen_nozzle_end_eps=0.0 unchanged)  [{'OK' if neutral_ok else 'FAIL'}]")

    # Neutral-default regression: reference regen design, channels vs flat.
    ref_flat = EngineDesign(cycle="gas_generator").compute()
    ref_ch = EngineDesign(cycle="gas_generator", regen_channel_model="channels").compute()
    ref_dp = ref_ch["cooling"]["jacket_dp_pa"]
    ref_dp_ok = abs(ref_dp - CHANNELS_REF_DP_TARGET_PA) / CHANNELS_REF_DP_TARGET_PA <= CHANNELS_REF_DP_TOL
    isp_move = abs(ref_ch["isp_vac_engine_s"] - ref_flat["isp_vac_engine_s"])
    bleed_move = abs(ref_ch["cycle_result"]["gg_flow_fraction"]
                     - ref_flat["cycle_result"]["gg_flow_fraction"])
    ref_stable = isp_move < 0.5 and bleed_move < 0.002
    all_ok &= ref_dp_ok and ref_stable
    print(f"\nNEUTRAL-DEFAULT (reference regen design, channels vs flat)  "
          f"[{'OK' if ref_dp_ok and ref_stable else '*** FAIL ***'}]")
    print(f"  channels jacket dP {ref_dp/1e6:.3f} MPa vs flat 1.600 (tol {CHANNELS_REF_DP_TOL*100:.0f}%)  "
          f"[{'OK' if ref_dp_ok else 'FAIL'}]")
    print(f"  engine Isp moves {isp_move:.2f} s, GG bleed moves {bleed_move*100:.3f} pt  "
          f"[{'OK' if ref_stable else 'FAIL'}]")
    print()
    print("ALL COOLING CHECKS OK" if all_ok else
          "*** COOLING CHECK FAILED - review physics/cooling.py ***")
    print("=" * 78)
    return all_ok


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
    # feeding it in raises pump discharge but not Isp
    base = EngineDesign(cycle="gas_generator", contraction_ratio=1.5).compute()
    lossy = EngineDesign(cycle="gas_generator", contraction_ratio=1.5,
                          apply_chamber_pressure_loss=True).compute()
    c1_feed_ok = (lossy["cycle_result"]["turbopump"]["power_total_w"]
                  > base["cycle_result"]["turbopump"]["power_total_w"]
                  and abs(lossy["isp_vac_engine_s"] - base["isp_vac_engine_s"]) < 0.5)
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
    ref_mult = r_ref["material_margin"]["margin_ratio"] / materials.THIN_MARGIN_THRESHOLD
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
    r = _design(propellant_pair="LOX/LH2", mixture_ratio=5.5, chamber_pressure_pa=9.22e6,
                expansion_ratio=92.0, cycle="tap_off", target_vac_thrust_n=1_307_000.0)
    c = r["cycle_result"]
    tin = c["drive_gas"]["tin_k"]
    isp_loss_pct = 100.0 * (1.0 - r["isp_vac_engine_s"] / r["isp_vac_chamber_s"])
    _report("J-2X (tap-off, LOX/LH2, 9.22 MPa, MR 5.5)", [
        ("tap gas below chamber Tc", tin < r["tc_k"], f"{tin:.0f} K vs Tc {r['tc_k']:.0f} K"),
        ("tap gas in 850-1200 K", 850.0 <= tin <= 1200.0, f"{tin:.0f} K"),
        ("dump Isp fraction == 0.80", abs(c["gg_dump_isp_fraction"] - 0.80) < 1e-9,
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
        all_ok = all_ok and ok and window_ok and sized_ok

    print()
    print("ALL JACKET-OVERPRESSURE SAMPLE-CALC SPOT CHECKS OK" if all_ok else
          "*** JACKET-OVERPRESSURE SAMPLE-CALC CHECK FAILED - review "
          "mass_model.hoop_stress_pa/thermal_stress_pa ***")
    print("=" * 78)
    return all_ok


def run_manifold_bypass_check():
    """
    Real-physics check for `EngineDesign.manifold_bypass_fraction` under
    `cooling_flow_topology="f1_split_reverse_flow"` (2026-09-17: replaced a
    post-hoc coolant_delta_t_k rescale with feeding the real bypass-reduced
    down-leg flow directly into march_coolant() - see ASSUMPTIONS.md). Not a
    plausibility-only check - these are exact, verified directions:
      (1) bypass_fraction=0 reproduces single_pass_countercurrent's
          jacket_dp_pa EXACTLY (bit-identical) - the degenerate case.
      (2) jacket_dp_pa INCREASES monotonically with bypass_fraction - NOT the
          naively-expected decrease. channel_target_height_m sizes channels to
          a fixed target velocity regardless of total flow, so less down-leg
          flow means smaller channels (not lower velocity), and smaller
          channels mean more friction loss per unit length.
      (3) The jacket-overpressure check's combined stress DECREASES
          monotonically with bypass_fraction despite (2) - smaller channels
          also mean a smaller derived tube radius (Round 1's tube-radius-sized
          wall thickness), so the dominant thermal-restraint term shrinks
          faster than the hoop term grows.
      (4) The real F-1 anchor (bypass_fraction=0.30) produces finite, positive
          numbers throughout (not nan/negative) at every station.
    """
    print()
    print("=" * 78)
    print("MANIFOLD BYPASS-FRACTION REAL-PHYSICS CHECK (design.py "
          "f1_split_reverse_flow / mdot_coolant_jacket_kgs)")
    print("=" * 78)

    def _design(topology, bypass):
        d = EngineDesign(regen_channel_model="channels", wall_construction="tube_wall",
                          cooling_flow_topology=topology, manifold_bypass_fraction=bypass)
        return d.compute()

    r_single = _design("single_pass_countercurrent", 0.0)
    r_split0 = _design("f1_split_reverse_flow", 0.0)
    degenerate_ok = (r_single["cooling"]["jacket_dp_pa"] == r_split0["cooling"]["jacket_dp_pa"])
    print(f"\nDegenerate case: bypass=0 split-flow jacket_dp_pa == "
          f"single_pass_countercurrent's   [{'OK' if degenerate_ok else 'FAIL'}]")

    sweep = [0.0, 0.15, 0.30, 0.45, 0.60]
    prev_dp, prev_stress = None, None
    dp_mono_ok, stress_mono_ok, finite_ok = True, True, True
    for bypass in sweep:
        r = _design("f1_split_reverse_flow", bypass)
        dp = r["cooling"]["jacket_dp_pa"]
        stress = r["jacket_combined_stress_pa"]
        if not (math.isfinite(dp) and dp > 0 and stress is not None
                and math.isfinite(stress) and stress > 0):
            finite_ok = False
        if prev_dp is not None and dp < prev_dp - 1.0:
            dp_mono_ok = False
        if prev_stress is not None and stress > prev_stress + 1.0:
            stress_mono_ok = False
        print(f"  bypass={bypass:.2f}: jacket_dp_pa={dp/1e6:6.2f} MPa (increasing)   "
              f"combined_stress={stress/1e6:6.1f} MPa (decreasing)   "
              f"[{'OK' if (dp_mono_ok and stress_mono_ok and finite_ok) else 'FAIL'}]")
        prev_dp, prev_stress = dp, stress

    all_ok = degenerate_ok and dp_mono_ok and stress_mono_ok and finite_ok
    print()
    print("ALL MANIFOLD BYPASS-FRACTION CHECKS OK" if all_ok else
          "*** MANIFOLD BYPASS-FRACTION CHECK FAILED - review design.py's "
          "mdot_coolant_jacket_kgs wiring ***")
    print("=" * 78)
    return all_ok


def run_two_pass_cooling_check():
    """
    Real-engine check for cooling_flow_topology="j2_mid_nozzle_inlet" (the
    J-2's own regen circuit: fuel manifold partway down the nozzle, down 180
    tubes to the exit, back up 360 tubes to the injector - cooling.
    march_coolant_two_pass). Anchored on the real J-2 230K
    (Engine_Configs/J2_Config.cfg header: LOX/LH2, Pc 5.26 MPa, O/F 5.5,
    eps 27.5, 1023 kN vac; 347-stainless tube wall regen-cooled full length).
    Exact invariants plus one deliberately WIDE band, the same order-of-
    magnitude spirit as COOLING_CHECKS' jacket_dp bands (the J-2's real
    jacket dP is not in this repo, and neither is its inlet area ratio -
    jacket_inlet_eps stays the Tier-3 default here):
      (1) an inlet at the cooled end (zero-length down pass) reproduces the
          single-pass jacket dP / coolant dT / throat coolant-side wall temp
          EXACTLY - the degenerate case;
      (2) the total coolant dT does not depend on the inlet station (same wall
          heat into the same flow - energy balance);
      (3) jacket dP rises monotonically as the inlet moves upstream (a longer
          down pass through the 1/3-circumference down tubes);
      (4) at the default inlet the J-2 lands in a plausible jacket dP band
          [0.2, 5.0] MPa with LH2 dT under cooling.MAX_COOLANT_DELTA_T_K, and
          the mid-nozzle inlet ring runs at the down-tube velocity (~3x the
          single-pass passage velocity at that station).
    """
    print()
    print("=" * 78)
    print("J-2 TWO-PASS COOLING CHECK (cooling.march_coolant_two_pass, "
          "j2_mid_nozzle_inlet)")
    print("=" * 78)

    def _j2(topology, inlet_eps=8.0):
        return EngineDesign(
            propellant_pair="LOX/LH2", chamber_pressure_pa=5.26e6, mixture_ratio=5.5,
            expansion_ratio=27.5, target_vac_thrust_n=1_023_090.6, cycle=cycles.GAS_GENERATOR,
            material_key="stainless_steel", bell_material_key="stainless_steel",
            chamber_cooling_method="regenerative", nozzle_cooling_method="regenerative",
            regen_nozzle_end_eps=27.5, regen_channel_model="channels",
            wall_construction="tube_wall", cooling_flow_topology=topology,
            jacket_inlet_eps=inlet_eps).compute()

    single = _j2("single_pass_countercurrent")
    zero = _j2("j2_mid_nozzle_inlet", inlet_eps=27.5)
    keys = ("jacket_dp_pa", "coolant_delta_t_k", "coolant_side_wall_t_throat_k")
    degenerate_ok = all(abs(zero["cooling"][k] - single["cooling"][k])
                        <= 1e-9 * max(1.0, abs(single["cooling"][k])) for k in keys)
    print(f"\n(1) zero-length down pass == single pass (dP "
          f"{single['cooling']['jacket_dp_pa']/1e6:.3f} MPa, dT "
          f"{single['cooling']['coolant_delta_t_k']:.1f} K)   "
          f"[{'OK' if degenerate_ok else 'FAIL'}]")

    sweep = [27.5, 16.0, 8.0, 4.0]
    prev_dp, mono_ok, energy_ok = None, True, True
    results = {}
    for e in sweep:
        r = _j2("j2_mid_nozzle_inlet", inlet_eps=e)
        results[e] = r
        c = r["cooling"]
        if abs(c["coolant_delta_t_k"] - single["cooling"]["coolant_delta_t_k"]) > \
                1e-6 * single["cooling"]["coolant_delta_t_k"]:
            energy_ok = False
        if prev_dp is not None and c["jacket_dp_pa"] < prev_dp - 1.0:
            mono_ok = False
        prev_dp = c["jacket_dp_pa"]
        print(f"  inlet eps {e:5.1f}: jacket dP {c['jacket_dp_pa']/1e6:5.2f} MPa (down "
              f"{(c['jacket_dp_down_pa'] or 0)/1e6:4.2f}), dT {c['coolant_delta_t_k']:6.1f} K, "
              f"turnaround {c['coolant_turnaround_t_k']:6.1f} K")
    print(f"(2) coolant dT independent of the inlet station   [{'OK' if energy_ok else 'FAIL'}]")
    print(f"(3) jacket dP rises as the inlet moves upstream   [{'OK' if mono_ok else 'FAIL'}]")

    ref = results[8.0]
    c = ref["cooling"]
    dp_band_ok = 0.2e6 <= c["jacket_dp_pa"] <= 5.0e6
    dt_ok = 0.0 < c["coolant_delta_t_k"] <= cooling.MAX_COOLANT_DELTA_T_K.get("LOX/LH2", 500.0)
    ji = ref["jacket_manifold_result"]["jacket_inlet"]
    single_v = cooling.passage_velocity_ms(
        2.0 * math.sqrt(8.0) * ref["geometry"]["throat_dia_m"] / 2.0,
        ref["geometry"]["throat_dia_m"], ji["mdot_kgs"], "LOX/LH2")
    n_up, n_down = cooling.two_pass_tube_counts(ref["geometry"]["throat_dia_m"])
    v_ok = abs(ji["design_feed_velocity_ms"] / single_v - (n_up + n_down) / n_down) < 0.05
    print(f"(4) J-2 @ inlet eps 8: jacket dP {c['jacket_dp_pa']/1e6:.2f} MPa in [0.2, 5.0], "
          f"dT {c['coolant_delta_t_k']:.0f} K; inlet ring {ji['design_feed_velocity_ms']:.0f} m/s "
          f"= {ji['design_feed_velocity_ms']/single_v:.2f}x single-pass, ring ID "
          f"{ji['ring_inlet_inner_diameter_m']*1000:.0f} mm   "
          f"[{'OK' if (dp_band_ok and dt_ok and v_ok) else 'FAIL'}]")

    all_ok = degenerate_ok and energy_ok and mono_ok and dp_band_ok and dt_ok and v_ok
    print()
    print("ALL TWO-PASS COOLING CHECKS OK" if all_ok else
          "*** TWO-PASS COOLING CHECK FAILED - review cooling.march_coolant_two_pass / "
          "design.py's j2_mid_nozzle_inlet wiring ***")
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


# Pre-coupled-solve flat-mode throat T_wg for COOLING_CHECKS (2026-09-23): the
# coupled balance is scoped to regen_channel_model="channels", so the default
# flat path must reproduce these to the tenth of a kelvin.
FLAT_MODE_TWG_PINNED_K = {"F-1": 806.1, "SSME-class": 880.0, "RL10-class": 866.2}
WIESENECK_SSME_T_WC_K = 478.0          # 400 F coolant-side wall assumed at the SSME throat [Wieseneck-J2]
WIESENECK_COPPER_T_WG_MAX_K = 811.0    # 1000 F gas-side max for a copper chamber [Wieseneck-J2]


def run_coupled_wall_temperature_check():
    """
    Coupled throat wall balance (cooling.solve_wall_balance, "channels" regen
    only) - plausibility against real hardware, not a tight spot check:
      1. F-1 as built (Inconel-class brazed tubes, LOX/RP-1, Pc 7 MPa) must
         SURVIVE with an OK margin - the real engine flew. The same design
         WITHOUT the RP-1 carbon-deposit credit (cooling.GAS_SIDE_DEPOSIT_FACTOR,
         [TP2862-LOXRP1]) falls under the thin-margin threshold - at the
         auto-sized 0.2 mm tube wall it only just survives (~1.0x), so the
         credit is what moves a flown engine from "warn" to "OK".
      2. SSME-class milled NARloy-Z: coolant-side wall within 150 K of
         [Wieseneck-J2]'s assumed 400 F, gas side under its 1000 F copper max.
      3. Levers move the wall the right way: faster coolant cools it (and the
         velocity override is honoured), a low-k liner heats it, a smaller
         deposit credit heats it.
      4. Flat-mode neutrality: COOLING_CHECKS' T_wg unchanged, coupled keys None.
    """
    print()
    print("=" * 78)
    print("COUPLED WALL-TEMPERATURE CHECK (channels-mode throat balance)")
    print("=" * 78)
    checks = []

    f1 = next(c for c in COOLING_CHECKS if c["name"].startswith("F-1"))
    f1_kw = dict(propellant_pair=f1["pair"], mixture_ratio=f1["mr"],
                 chamber_pressure_pa=f1["pc_pa"], expansion_ratio=f1["eps"],
                 nozzle_type="bell", bell_percent_length=80.0, cycle=f1["cycle"],
                 injector_type="impinging", target_vac_thrust_n=f1["thrust_n"],
                 regen_channel_model="channels")

    def _run(**kw):
        return EngineDesign(**{**f1_kw, **kw}).compute()

    r_f1 = _run(material_key="inconel_718", wall_construction="tube_wall")
    m_f1 = r_f1["material_margin"]["margin_ratio"]
    saved = dict(cooling.GAS_SIDE_DEPOSIT_FACTOR)
    try:
        cooling.GAS_SIDE_DEPOSIT_FACTOR["LOX/RP-1"] = 1.0
        m_clean = _run(material_key="inconel_718", wall_construction="tube_wall")[
            "material_margin"]["margin_ratio"]
        cooling.GAS_SIDE_DEPOSIT_FACTOR["LOX/RP-1"] = 0.6
        twg_06 = _run(material_key="narloy_z")["cooling"]["t_wg_throat_k"]
    finally:
        cooling.GAS_SIDE_DEPOSIT_FACTOR.clear()
        cooling.GAS_SIDE_DEPOSIT_FACTOR.update(saved)
    c_f1 = r_f1["cooling"]
    checks.append((f"F-1 Inconel tubes survive: T_wg {c_f1['t_wg_throat_k']:.0f} K, "
                   f"margin {m_f1:.2f} (wall {c_f1['hot_wall_thickness_m']*1e3:.2f} mm)",
                   m_f1 >= 1.0))
    checks.append((f"  ...and is flagged thin without the deposit credit (margin {m_clean:.2f})",
                   m_clean < materials.THIN_MARGIN_THRESHOLD <= m_f1))

    ss = next(c for c in COOLING_CHECKS if c["name"].startswith("SSME"))
    c_ss = EngineDesign(propellant_pair=ss["pair"], mixture_ratio=ss["mr"],
                        chamber_pressure_pa=ss["pc_pa"], expansion_ratio=ss["eps"],
                        nozzle_type="bell", bell_percent_length=80.0, cycle=ss["cycle"],
                        injector_type="impinging", material_key="narloy_z",
                        target_vac_thrust_n=ss["thrust_n"],
                        regen_channel_model="channels").compute()["cooling"]
    checks.append((f"SSME T_wc {c_ss['t_wc_throat_k']:.0f} K vs Wieseneck "
                   f"{WIESENECK_SSME_T_WC_K:.0f} K (+/-150)",
                   abs(c_ss["t_wc_throat_k"] - WIESENECK_SSME_T_WC_K) <= 150.0))
    checks.append((f"SSME T_wg {c_ss['t_wg_throat_k']:.0f} K < copper max "
                   f"{WIESENECK_COPPER_T_WG_MAX_K:.0f} K",
                   c_ss["t_wg_throat_k"] < WIESENECK_COPPER_T_WG_MAX_K))

    c_base = _run(material_key="narloy_z")["cooling"]
    c_fast = _run(material_key="narloy_z", regen_coolant_velocity_ms=50.0)["cooling"]
    c_ni = _run(material_key="inconel_718")["cooling"]
    checks.append((f"faster coolant cools: {c_base['coolant_velocity_throat_ms']:.0f} -> "
                   f"{c_fast['coolant_velocity_throat_ms']:.0f} m/s, T_wg "
                   f"{c_base['t_wg_throat_k']:.0f} -> {c_fast['t_wg_throat_k']:.0f} K",
                   c_fast["t_wg_throat_k"] < c_base["t_wg_throat_k"]
                   and abs(c_fast["coolant_velocity_throat_ms"] - 50.0) < 5.0))
    checks.append((f"low-k liner runs hotter: NARloy {c_base['t_wg_throat_k']:.0f} K < "
                   f"Inconel {c_ni['t_wg_throat_k']:.0f} K",
                   c_ni["t_wg_throat_k"] > c_base["t_wg_throat_k"]))
    checks.append((f"smaller deposit credit runs hotter: 0.5 {c_base['t_wg_throat_k']:.0f} K "
                   f"< 0.6 {twg_06:.0f} K", twg_06 > c_base["t_wg_throat_k"]))

    flat_ok = True
    for ck in COOLING_CHECKS:
        c = EngineDesign(propellant_pair=ck["pair"], mixture_ratio=ck["mr"],
                         chamber_pressure_pa=ck["pc_pa"], expansion_ratio=ck["eps"],
                         nozzle_type="bell", bell_percent_length=80.0, cycle=ck["cycle"],
                         injector_type="impinging", material_key=ck["material"],
                         target_vac_thrust_n=ck["thrust_n"]).compute()["cooling"]
        pinned = next(v for k, v in FLAT_MODE_TWG_PINNED_K.items() if ck["name"].startswith(k))
        flat_ok = (flat_ok and abs(c["t_wg_throat_k"] - pinned) < 0.1
                   and c["t_wc_throat_k"] is None and c["h_g_throat_effective_w_m2k"] is None)
    checks.append(("flat mode unchanged (COOLING_CHECKS T_wg pinned, no coupled keys)", flat_ok))

    all_ok = True
    for name, ok in checks:
        all_ok = all_ok and bool(ok)
        print(f"  {name:66s} [{'OK' if ok else 'FAIL'}]")
    print()
    print("ALL COUPLED WALL-TEMPERATURE CHECKS OK" if all_ok else
          "*** COUPLED WALL-TEMPERATURE CHECK FAILED - review cooling.solve_wall_balance ***")
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


def run_film_overlay_check():
    """
    Film cooling as an OVERLAY on every section method, at two independent
    sites (2026-09-23): the chamber curtain (film_cooling_fraction, face or a
    convergent ring) and the nozzle-extension slot (nozzle_film_fraction at
    nozzle_film_inject_eps), both post-jacket. PLAUSIBILITY + neutrality, not a
    real-engine spot check - there is no film-effectiveness correlation in hand
    (NASA SP-8124 missing, claude_lit/OPEN_QUESTIONS.md); the constants are
    Tier 3 and only their DIRECTION is being pinned.

      (a) neutrality: a slot beyond the exit, or 0 % film, changes no number.
      (b) regen + chamber film: throat AND full-length peak wall temperature fall
          monotonically with film fraction (F-1-class, channels model).
      (c) [EUCASS-2023] plausibility: its 4 kN / 20 bar regen engine dropped peak
          wall temp 1124 -> 948 K (-176 K) when 7 % film was added. A LOX/RP-1
          analog (ethanol isn't a pair here) at the same scale must drop by the
          same ORDER (40-450 K).
      (d) F-1-class slot film (eps 10, the real F-1 film start [SP-8120]) on an
          uncooled Inconel extension: lowers the extension's radiative-equilibrium
          wall temperature, phi recovers downstream of the slot, and the Isp cost
          equals the dump-flow formula exactly (it never burns in the chamber).
      (e) convergent film ring: moves protection off the barrel onto the throat.
      (f) ablative + film: rated burn time rises (char-rate credit).
    """
    print()
    print("=" * 78)
    print("FILM-OVERLAY CHECK (two film sites, post-jacket, combined with base methods)")
    print("=" * 78)
    all_ok = True
    rows = []

    base = EngineDesign().compute()
    off = EngineDesign(nozzle_film_fraction=0.05, nozzle_film_inject_eps=500.0).compute()
    a_ok = (base["isp_vac_engine_s"] == off["isp_vac_engine_s"]
            and base["cooling"]["t_wg_throat_k"] == off["cooling"]["t_wg_throat_k"]
            and base["computed_dry_mass_kg"] == off["computed_dry_mass_kg"]
            and off["cooling"]["nozzle_film_isp_penalty_fraction"] == 0.0)
    rows.append(("(a) slot beyond exit / 0% film -> no-op", a_ok))

    f1 = dict(propellant_pair="LOX/RP-1", mixture_ratio=2.27, chamber_pressure_pa=7.0e6,
              expansion_ratio=16.0, cycle="gas_generator", nozzle_type="bell",
              bell_percent_length=80.0, injector_type="impinging", material_key="narloy_z",
              target_vac_thrust_n=7_770_000.0, regen_channel_model="channels")
    tw, pk = [], []
    for f in (0.0, 0.03, 0.06, 0.10):
        c = EngineDesign(**f1, film_cooling_fraction=f).compute()["cooling"]
        tw.append(c["t_wg_throat_k"])
        pk.append(c["peak_wall_temp_k"])
    b_ok = (all(np.diff(tw) < 0) and all(v is not None for v in pk) and all(np.diff(pk) < 0))
    rows.append((f"(b) F-1-class regen + 0/3/6/10% film: throat T_wg "
                 f"{'/'.join(f'{t:.0f}' for t in tw)} K, peak "
                 f"{'/'.join(f'{t:.0f}' for t in pk)} K (monotonic)", b_ok))

    small = dict(propellant_pair="LOX/RP-1", mixture_ratio=2.3, chamber_pressure_pa=2.0e6,
                 expansion_ratio=4.5, cycle="pressure_fed", nozzle_type="conical",
                 material_key="narloy_z", target_vac_thrust_n=4_000.0,
                 regen_channel_model="channels")
    s0 = EngineDesign(**small).compute()["cooling"]["peak_wall_temp_k"]
    s7 = EngineDesign(**small, film_cooling_fraction=0.07).compute()["cooling"]["peak_wall_temp_k"]
    c_ok = s0 is not None and s7 is not None and 40.0 <= s0 - s7 <= 450.0
    rows.append((f"(c) 4 kN/20 bar regen + 7% film: peak {s0:.0f} -> {s7:.0f} K "
                 f"(-{s0 - s7:.0f} K; EUCASS-2023 real: -176 K)", c_ok))

    ext = dict(f1, bell_material_key="inconel_718", nozzle_cooling_method="uncooled",
               cooling_transition_eps=10.0)
    e0 = EngineDesign(**ext).compute()
    e1 = EngineDesign(**ext, nozzle_film_fraction=0.05, nozzle_film_inject_eps=10.0).compute()
    t0 = e0["bell_material_margin"]["assumed_wall_temp_k"]
    t1 = e1["bell_material_margin"]["assumed_wall_temp_k"]
    phn = np.asarray(e1["cooling"]["nozzle_film_profile"])
    i0 = int(np.argmax(phn < 1.0))
    mdot_fuel = e1["mdot_kgs"] / (1.0 + f1["mixture_ratio"])
    want = cooling.dump_cooling_isp_penalty_fraction(0.05 * mdot_fuel, e1["mdot_kgs"])
    d_ok = (t1 < t0 and i0 > 0 and np.all(phn[:i0] == 1.0)
            and np.all(np.diff(phn[i0:]) >= -1e-12)
            and abs(e1["cooling"]["nozzle_film_isp_penalty_fraction"] - want) < 1e-12
            and e1["isp_vac_engine_s"] < e0["isp_vac_engine_s"])
    rows.append((f"(d) F-1-class eps-10 slot film 5%, uncooled Inconel extension: wall "
                 f"{t0:.0f} -> {t1:.0f} K, Isp cost "
                 f"{e1['cooling']['nozzle_film_isp_penalty_fraction']*100:.2f}% (= dump formula)",
                 d_ok))

    face = EngineDesign(**f1, film_cooling_fraction=0.05).compute()["cooling"]
    ring = EngineDesign(**f1, film_cooling_fraction=0.05,
                        chamber_film_inject_area_ratio=1.5).compute()["cooling"]
    pf, pr = np.asarray(face["chamber_film_profile"]), np.asarray(ring["chamber_film_profile"])
    e_ok = (pr[0] == 1.0 and pf[0] < 1.0
            and ring["t_wg_throat_k"] < face["t_wg_throat_k"])
    rows.append((f"(e) convergent film ring (eps 1.5) vs face: barrel unfilmed, throat "
                 f"{face['t_wg_throat_k']:.0f} -> {ring['t_wg_throat_k']:.0f} K", e_ok))

    ab0 = EngineDesign(material_key="ablative_phenolic").compute()["rated_burn_time_s"]
    ab1 = EngineDesign(material_key="ablative_phenolic",
                       film_cooling_fraction=0.06).compute()["rated_burn_time_s"]
    f_ok = ab1 > ab0
    rows.append((f"(f) ablative + 6% film: rated burn {ab0:.0f} -> {ab1:.0f} s", f_ok))

    for name, ok in rows:
        all_ok &= bool(ok)
        print(f"  {name}   [{'OK' if ok else 'FAIL'}]")
    print()
    print("ALL FILM-OVERLAY CHECKS OK" if all_ok else
          "*** FILM-OVERLAY CHECK FAILED - review cooling.film_effectiveness_profile / "
          "nozzle_film_effectiveness_profile / design.EngineDesign._film_phi ***")
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


if __name__ == "__main__":
    ok = (run() and run_integration_checks() and run_contraction_ratio_sensitivity_check()
          and run_turbopump_efficiency_check() and run_gg_flow_fraction_check()
          and run_cooling_heat_flux_check() and run_injector_geometry_check()
          and run_gas_centered_swirl_injector_check()
          and run_combustion_stability_check() and run_chamber_detail_check()
          and run_turbopump_sizing_check() and run_bearing_dn_check()
          and run_mass_model_sensitivity_check() and run_cycle_model_check()
          and run_explicit_cooling_check() and run_jacket_overpressure_check()
          and run_jacket_overpressure_sample_calc_check()
          and run_manifold_bypass_check()
          and run_two_pass_cooling_check()
          and run_feed_system_plausibility_check()
          and run_hatband_plausibility_check()
          and run_coupled_wall_temperature_check()
          and run_cooling_compatibility_check()
          and run_film_overlay_check()
          and run_pump_pressure_chain_check())
    raise SystemExit(0 if ok else 1)
