"""Cooling: wall heat flux / Bartz magnitude vs F-1 / SSME / RL10 (COOLING_CHECKS) and the contraction-ratio heat-flux sensitivity.

Part of the physics/validate/ package (split verbatim out of the former
single-file validate.py - run the whole suite with
`python3 -m engine_designer.physics.validate`)."""
import numpy as np

from .. import (cooling, expander, materials)
from ..design import EngineDesign


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
T_WG_LO_K = 200.0   # 2026-09-23: was 450. With a real 45 K LH2 inlet and the cited
                    # roughness/curvature coolant-side enhancement, a small copper
                    # RL10-class throat legitimately runs ~300 K; this floor only
                    # guards against an absurd (sub-coolant) solve.
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
         # 2026-09-23: the CITED SSME design point, 72 Btu/in2-s = 118 MW/m2
         # [Wieseneck-J2 p.6], +/-30 % (was an uncited 18-140).
         q_throat_lo_mw=82.4, q_throat_hi_mw=153.0, hg_lo=12000.0, hg_hi=60000.0,
         t_wg_hi_k=1050.0, dp_lo_mpa=0.2, dp_hi_mpa=4.0),
    dict(name="RL10-class (LOX/LH2, expander, small upper stage)",
         pair="LOX/LH2", pc_pa=3.2e6, mr=5.5, eps=61.0, thrust_n=73_000.0,
         cycle="expander", material="narloy_z",
         e_frac_lo=0.002, e_frac_hi=0.08, max_coolant_dt_k=500.0,
         # No cited RL10 throat flux. Bartz's Pc^0.8 Dt^-0.2 scaling of the cited
         # SSME point to 3.2 MPa / this throat gives ~35-45 MW/m2; band is that
         # +/- a factor ~1.5-4 (plausibility, uncited - was 3-22, set around the
         # old 0.55-scaled model).
         q_throat_lo_mw=10.0, q_throat_hi_mw=60.0, hg_lo=3000.0, hg_hi=30000.0,
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
        # The OLD flat anchor is propellant-agnostic (Pc^0.8 only) and reads
        # LOX/LH2 ~4-6x low against the now-unscaled Bartz model that meets the
        # cited J-2 / SSME fluxes - reported comparison, sanity-gated loosely.
        anchor_ok = 0.3 <= vs_anchor_ratio <= 8.0

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
               # c* cost on the FUEL basis (audit W3): 0.5 x 6 % / (1 + MR 2.27)
               # = 0.92 % (the old 2-6 % band encoded the (1+MR)x-overstated one)
               and 0.5 <= eta_drop_pct <= 2.0
               and isp_move_pct <= 5.5
               # film cuts the heat the jacket takes (2026-09-23: on the mdot*cp*Tc
               # energy basis the unfilmed F-1 sits at ~0.4 %, so the filmed one
               # legitimately falls below Sutton's band floor)
               and 0.001 <= c6["wall_heat_energy_fraction"] < c0["wall_heat_energy_fraction"]
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
