"""Cooling: jacket flow layouts - F-1 manifold bypass and the J-2 two-pass circuit.

Part of the physics/validate/ package (split verbatim out of the former
single-file validate.py - run the whole suite with
`python3 -m engine_designer.physics.validate`)."""
import math

from .. import (cooling, cycles)
from ..design import EngineDesign


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
