"""Structural stages of _compute_pass: wall shells, overpressure, buckling, tubes, hatbands.

Split verbatim out of the former single-file design.py; a value shared
between stages lives on the PassState `s` (see design/state.py)."""
import math

import numpy as np

from .. import (cooling, geometry, hatbands, mass_model, materials, turbopump_sizing,
                isentropic as iso)
from .constants import (
    PA_SEA_LEVEL,
    REGEN_HOT_WALL_THICKNESS_M,
)
from .checklist import _check


def wall_structure(self, s):
    """Wall-shell mass/thickness profiles, jacket overpressure, thermal buckling."""
    # Dry-mass estimate: chamber/nozzle wall mass from a real thin-wall pressure-vessel
    # hoop-stress formula (physics/mass_model.py), split by material at the same
    # eps_for_transition point already used above and for rendering
    # (geometry.split_profile_by_area_ratio), plus turbopump mass (already computed
    # for pump-fed cycles). A LOWER BOUND on real dry mass - no injector/valves/
    # actuators/mounting structure. See physics/mass_model.py's module docstring.
    # (bell_material was looked up above for the nozzle-extension thermal check.)
    s.body_xs, s.body_rs, s.ext_xs, s.ext_rs, s.has_extension = geometry.split_profile_by_area_ratio(
        s.xs, s.rs, s.geo["throat_dia_m"], s.eps_for_transition)
    ext_rs = s.ext_rs   # local alias, unchanged below; also read by rollup_stage
                        # for the zirconia-liner mass (s.ext_xs/s.ext_rs)
    # For chamber_cooling == "ablative", this hoop-stress shell is the STRUCTURAL
    # OVERWRAP behind the sacrificial char liner, not the liner itself - rollup_stage.
    # burn_time_and_mass adds the liner's own mass (mass_model.ablative_liner_thickness_m/
    # constant_thickness_shell_mass_kg) into s.chamber_wall_mass_kg afterward. See
    # ASSUMPTIONS.md for the fix this reframing is part of.
    s.chamber_wall_mass_kg = mass_model.shell_mass_kg(
        s.body_xs, s.body_rs, self.chamber_pressure_pa,
        s.chamber_material.allowable_stress_pa, s.chamber_material.density_kg_m3)
    s.bell_wall_mass_kg = 0.0
    if s.has_extension:
        s.bell_wall_mass_kg = mass_model.shell_mass_kg(
            s.ext_xs, ext_rs, self.chamber_pressure_pa,
            s.bell_material.allowable_stress_pa, s.bell_material.density_kg_m3)
        # Orthogrid nozzle-extension stiffening (2026-09-25): a machined-waffle
        # shell pockets out material vs. a plain hoop-stress-thickness shell -
        # see mass_model.ORTHOGRID_MASS_FRACTION's own uncited-estimate flag.
        if (self.nozzle_extension_stiffening_style == "orthogrid"
                and s.nozzle_cooling in ("radiative", "uncooled")):
            s.bell_wall_mass_kg *= mass_model.ORTHOGRID_MASS_FRACTION
    # Per-station wall thickness (pointwise, not the segment-average
    # shell_mass_kg integrates for mass) - for the 3D preview's solid-shell
    # offset. Purely additive: doesn't feed any mass/thermal number above
    # (shell_mass_kg, just above, keeps its own flat-Pc approximation for
    # BOTH pieces unchanged - this pointwise profile is a rendering-only
    # refinement on top of it).
    #
    # The chamber/convergent/throat stations run near chamber pressure
    # throughout - real static pressure stays close to Pc until the
    # throat, so flat Pc is a fine approximation there. Past the throat,
    # BOTH the body piece's own diverging-bell portion (up to
    # eps_for_transition) and the separate EXTENSION piece instead use
    # the LOCAL isentropic static pressure at each station's own area
    # ratio (iso.pe_over_pc_from_eps) - thickness is proportional to
    # pressure x radius, and flat chamber pressure applied all the way to
    # a large-eps station (where the real static pressure has dropped to
    # a small fraction of Pc) made the RENDERED wall balloon into an
    # increasingly absurd flare as area ratio grew, despite real nozzle
    # walls being thin precisely because they run at low local pressure,
    # not from a material difference. Applying flat Pc to only the body
    # piece's OWN diverging stations (while the extension already used
    # local pressure) produced a large spurious thickness step right at
    # the body/extension joint - large enough to render as a visible
    # kink/bump in the 3D preview even with the bridging frustum that
    # smooths the two pieces' outer walls together.
    s.throat_r_m = s.geo["throat_dia_m"] / 2.0
    if s.throat_r_m > 0 and len(s.body_rs) > 1:
        body_throat_idx = int(np.argmin(s.body_rs))
        body_local_eps = np.clip((s.body_rs / s.throat_r_m) ** 2, 1.0 + 1e-6, None)
        body_pressure_pa = np.array([
            self.chamber_pressure_pa * iso.pe_over_pc_from_eps(float(e), s.gamma)
            for e in body_local_eps])
        body_pressure_pa[:body_throat_idx] = self.chamber_pressure_pa
    else:
        body_pressure_pa = self.chamber_pressure_pa
    s.body_wall_thickness_m = mass_model.wall_thickness_profile_m(
        s.body_rs, body_pressure_pa, s.chamber_material.allowable_stress_pa)
    if s.has_extension:
        ext_local_eps = (np.clip((ext_rs / s.throat_r_m) ** 2, 1.0 + 1e-6, None)
                         if s.throat_r_m > 0 else np.full_like(ext_rs, 1.0 + 1e-6))
        ext_pressure_pa = np.array([
            self.chamber_pressure_pa * iso.pe_over_pc_from_eps(float(e), s.gamma)
            for e in ext_local_eps])
        s.ext_wall_thickness_m = mass_model.wall_thickness_profile_m(
            ext_rs, ext_pressure_pa, s.bell_material.allowable_stress_pa)
    else:
        s.ext_wall_thickness_m = np.zeros(0)
    # --- jacket/coolant overpressure vs. wall structural margin
    # (structural PLAUSIBILITY flag, NOT a buckling analysis - see
    # ASSUMPTIONS.md). The coolant jacket runs at roughly the pump-discharge
    # pressure, nearly flat along its length in this model (no axial jacket-
    # pressure-drop profile exists - only one lumped jacket_dp_pa), while
    # local gas static pressure keeps falling past the throat
    # (iso.pe_over_pc_from_eps). The net differential between them can load
    # the wall inward rather than the outward/tension direction its
    # thickness was sized for - the real "liner buckling near the nozzle
    # exit" consideration.
    #
    # Per wall_construction (cooling.WALL_CONSTRUCTIONS), the physically
    # correct FORMULA differs - `[Huzel "Tubular Wall Thrust Chamber
    # Design" p.107-109]` (see claude_lit/topics/06-cooling-and-heat-
    # transfer.md):
    #   - tube_wall: eq 4-27/4-28, a circular tube's combined hoop (net
    #     Pco-Pg x the TUBE's own local radius / thickness) + longitudinal
    #     thermal-restraint stress. Sign-agnostic - no "reversal" framing
    #     needed. Huzel's own A-1 sample calc shows Pco=1500psia >
    #     Pg=562psia AT THE THROAT too, so net-inward loading is normal
    #     near-everywhere past the injector for a real tube/coax design,
    #     not just a downstream edge case - evaluated at both the throat
    #     (where heat flux, hence the thermal term, peaks) and the worst-
    #     reversal station (end of active cooling), taking the max.
    #   - coax_shell: eq 4-31, the SAME two terms but with the full local
    #     shell radius (a continuous shell, not discrete tubes) - this is
    #     the one case where the tool's original, since-corrected full-
    #     radius hoop-stress attempt was actually the right formula.
    #   - milled_channel: kept as the clamped rectangular-plate-strip
    #     approximation from the prior round (span = channel width,
    #     reversal-gated only) - no citation covers a thermal term
    #     combined with plate-bending for milled channels yet
    #     (`[Sutton Sec 8.3]`, still unread).
    # In all three cases, wall THICKNESS is still the tool's generic
    # Pc-derived shell thickness (mass_model.wall_thickness_m using the
    # FULL local radius) - a pre-existing gap this round does not fix; see
    # ASSUMPTIONS.md.
    jacket_overpressure_active = (s.chamber_cooling == "regenerative"
                                   and self.regen_channel_model == "channels"
                                   and s.channel_geometry is not None
                                   and s.jacket_dp_pa > 0.0 and s.throat_r_m > 0)
    s.jacket_overpressure_ok = True
    jacket_overpressure_detail = ""
    jacket_overpressure_ok_detail = "OK - stress stays within margin at the evaluated stations"
    s.jacket_worst_station_eps = None
    s.jacket_pressure_at_worst_station_pa = None
    s.jacket_local_gas_pressure_at_worst_station_pa = None
    s.jacket_overpressure_worst_station = None
    s.jacket_combined_stress_pa = None
    s.jacket_hoop_stress_pa = None
    s.jacket_thermal_stress_pa = None
    # --- longitudinal thermal inelastic buckling (Huzel eq 4-29) - a
    # DIFFERENT failure mode from the pressure/hoop check above: thermal-
    # restraint-driven buckling of the tube's hot-gas-side "zone I"
    # against its cooler, much more massive backside "zone II" - not a
    # coolant-vs-gas pressure differential. tube_wall only (the extracted
    # Huzel text gives no coax-shell buckling analogue). Real, citable
    # formula (mass_model.longitudinal_buckling_stress_pa), but E_c
    # (compression tangent modulus) has NO data for any material in this
    # codebase today - reports "n/a" per material rather than estimating
    # a cross-material ratio with no real grounding. See ASSUMPTIONS.md.
    buckling_active = False
    buckling_ok = True
    buckling_detail = ""
    buckling_material_name = None
    if jacket_overpressure_active:
        worst_eps = max(s.cooled_length_eps, 1.0 + 1e-6)
        worst_r_m = s.throat_r_m * math.sqrt(worst_eps)
        p_local_gas_worst_pa = self.chamber_pressure_pa * iso.pe_over_pc_from_eps(worst_eps, s.gamma)
        # Reuses the already-computed, topology-aware manifold pressure
        # variables (design.py:1290-1292) instead of recomputing the same
        # formula independently - single_pass_countercurrent (default)
        # uses jacket_inlet_pressure_pa (algebraically identical to the
        # old recomputation, zero behavior change); f1_split_reverse_flow
        # uses jacket_return_pressure_pa (lower, by the down-leg's own
        # share of jacket_dp_pa) instead of always assuming full inlet
        # pressure at the worst/aft station - resolves the "somewhat
        # conservative under f1_split_reverse_flow" gap noted in
        # ASSUMPTIONS.md's coolant_delta_t_k rescale entry.
        # j2_mid_nozzle_inlet: the aft (worst) station is at the
        # turnaround too - same return-pressure reasoning.
        jacket_pressure_pa = (s.jacket_return_pressure_pa
                               if self.cooling_flow_topology in ("f1_split_reverse_flow",
                                                                 "j2_mid_nozzle_inlet")
                               else s.jacket_inlet_pressure_pa)
        worst_material = s.chamber_material if worst_eps <= s.eps_for_transition else s.bell_material
        t_worst_m = max(
            mass_model.wall_thickness_m(p_local_gas_worst_pa, worst_r_m, worst_material.allowable_stress_pa),
            mass_model.MIN_WALL_THICKNESS_M)
        t_throat_m = max(
            mass_model.wall_thickness_m(self.chamber_pressure_pa, s.throat_r_m,
                                         s.chamber_material.allowable_stress_pa),
            mass_model.MIN_WALL_THICKNESS_M)
        s.jacket_worst_station_eps = worst_eps
        s.jacket_pressure_at_worst_station_pa = jacket_pressure_pa
        s.jacket_local_gas_pressure_at_worst_station_pa = p_local_gas_worst_pa

        if self.wall_construction in ("tube_wall", "coax_shell"):
            # q at the worst-reversal station, interpolated from the
            # already-computed absolute heat-flux profile (diverging side
            # only - eps isn't monotonic across the throat). q AT the
            # throat is exactly q_throat_w_m2 by definition (its max).
            throat_idx_full = int(np.argmin(s.rs))
            full_local_eps = (np.clip((s.rs / s.throat_r_m) ** 2, 1.0 + 1e-6, None)
                               if s.throat_r_m > 0 else np.full_like(s.rs, 1.0 + 1e-6))
            div_eps = full_local_eps[throat_idx_full:]
            div_q = s.q_profile_w_m2[throat_idx_full:]
            q_worst_w_m2 = (float(np.interp(worst_eps, div_eps, div_q))
                             if len(div_eps) > 1 else s.q_throat_w_m2)

            def _combined_stress(radius_m, t_m, p_local_gas_pa, q_w_m2, material):
                net_dp = jacket_pressure_pa - p_local_gas_pa
                s_hoop = mass_model.hoop_stress_pa(net_dp, radius_m, t_m)
                dt_thru_k = (q_w_m2 * t_m / material.thermal_conductivity_w_mk
                             if material.thermal_conductivity_w_mk > 0 else 0.0)
                s_thermal = mass_model.thermal_stress_pa(
                    dt_thru_k, material.youngs_modulus_pa, material.cte_per_k,
                    nu=mass_model.POISSON_RATIO)
                return net_dp, s_hoop, s_thermal, s_hoop + s_thermal

            if self.wall_construction == "tube_wall":
                n_ch_worst = cooling.channel_count_at_station(
                    s._n_ch_visual, worst_eps, s.split_eps_eff)
                n_ch_throat = cooling.channel_count_at_station(
                    s._n_ch_visual, 1.0, s.split_eps_eff)
                radius_worst_m = cooling.channel_hydraulic_geometry(
                    2.0 * worst_r_m, n_ch_worst, s._channel_height_visual,
                    s._land_fraction_visual)["dh_m"] / 2.0
                radius_throat_m = cooling.channel_hydraulic_geometry(
                    2.0 * s.throat_r_m, n_ch_throat, s._channel_height_visual,
                    s._land_fraction_visual)["dh_m"] / 2.0
                formula_name = "Huzel eq 4-27/4-28, tube_wall"
            else:  # coax_shell
                radius_worst_m = worst_r_m
                radius_throat_m = s.throat_r_m
                formula_name = "Huzel eq 4-31, coax_shell"

            # Wall thickness: the one minimising the SAME combined stress
            # (Huzel eq 4-27+4-28: |Pco-Pg|*r/t + K*t -> t* = sqrt(|dP|*r/K),
            # mass_model.min_combined_stress_thickness_m), sized against the
            # local tube/shell radius and the NET coolant-vs-gas differential
            # the wall really carries. Replaces (2026-09-23) sizing against
            # local GAS pressure alone, which left a nozzle-exit tube at the
            # gauge floor while holding ~Pc-class coolant pressure - a
            # "thicker wall" warning nothing could act on. Floor: tube_wall
            # uses the cited real tube gauge (TUBE_WALL_MIN_THICKNESS_M,
            # Huzel A-2); coax_shell keeps the generic MIN_WALL_THICKNESS_M.
            # Cap: the existing REGEN_HOT_WALL_THICKNESS_M precedent (a
            # coax_shell liner is backed by an outer jacket not modeled here,
            # never a lone ~15mm pressure vessel).
            t_floor_m = (mass_model.TUBE_WALL_MIN_THICKNESS_M
                         if self.wall_construction == "tube_wall"
                         else mass_model.MIN_WALL_THICKNESS_M)

            def _sized_thickness(radius_m, p_local_gas_pa, q_w_m2, material):
                k_per_m = (mass_model.thermal_stress_pa(
                    q_w_m2 / material.thermal_conductivity_w_mk, material.youngs_modulus_pa,
                    material.cte_per_k, nu=mass_model.POISSON_RATIO)
                    if material.thermal_conductivity_w_mk > 0 else 0.0)
                return mass_model.regen_hot_wall_thickness_m(
                    jacket_pressure_pa - p_local_gas_pa, radius_m, k_per_m,
                    material.allowable_stress_pa, t_floor_m, REGEN_HOT_WALL_THICKNESS_M)

            t_construction_worst_m, t_limit_worst = _sized_thickness(
                radius_worst_m, p_local_gas_worst_pa, q_worst_w_m2, worst_material)
            t_construction_throat_m, t_limit_throat = _sized_thickness(
                radius_throat_m, self.chamber_pressure_pa, s.q_throat_w_m2, s.chamber_material)

            net_worst, hoop_worst, thermal_worst, combined_worst = _combined_stress(
                radius_worst_m, t_construction_worst_m, p_local_gas_worst_pa,
                q_worst_w_m2, worst_material)
            net_throat, hoop_throat, thermal_throat, combined_throat = _combined_stress(
                radius_throat_m, t_construction_throat_m, self.chamber_pressure_pa,
                s.q_throat_w_m2, s.chamber_material)

            if self.wall_construction == "tube_wall":
                buckling_active = True
                # Evaluate at whichever station has the bigger THERMAL
                # term specifically (not necessarily the same station the
                # combined-stress check above picks - buckling is driven
                # purely by the thermal-restraint term, which typically
                # peaks at the throat where heat flux is highest).
                if thermal_throat >= thermal_worst:
                    buckling_material = s.chamber_material
                    buckling_thermal_pa = thermal_throat
                    buckling_t_m, buckling_r_m = t_construction_throat_m, radius_throat_m
                else:
                    buckling_material = worst_material
                    buckling_thermal_pa = thermal_worst
                    buckling_t_m, buckling_r_m = t_construction_worst_m, radius_worst_m
                buckling_material_name = buckling_material.display_name
                if buckling_material.e_c_pa is not None:
                    s_c_pa = mass_model.longitudinal_buckling_stress_pa(
                        buckling_material.youngs_modulus_pa, buckling_material.e_c_pa,
                        buckling_t_m, buckling_r_m, nu=mass_model.POISSON_RATIO)
                    buckling_limit_pa = 0.9 * s_c_pa
                    buckling_ok = buckling_thermal_pa <= buckling_limit_pa
                    if not buckling_ok:
                        buckling_detail = (
                            f"Longitudinal thermal-restraint stress (~{buckling_thermal_pa/1e6:.0f} MPa) "
                            f"exceeds 0.9x the critical inelastic-buckling stress "
                            f"(~{buckling_limit_pa/1e6:.0f} MPa of {s_c_pa/1e6:.0f} MPa, Huzel eq 4-29) "
                            f"for {buckling_material_name}'s hot-gas-side tube wall. Consider a lower "
                            f"heat flux there (film cooling, larger throat), a thicker wall, or a "
                            f"material with a higher compression tangent modulus.")
                else:
                    buckling_detail = (f"n/a - no compression tangent-modulus (E_c) data for "
                                        f"{buckling_material_name}; see ASSUMPTIONS.md")

            # Pass/fail on the PRIMARY (load-controlled) hoop stress only
            # (2026-09-24). The thermal-restraint term (Huzel eq 4-28) is a
            # SECONDARY stress: it comes from an imposed through-wall strain,
            # so once the hot face yields it stops growing and becomes cyclic
            # plastic strain - a low-cycle-fatigue question, answered by the
            # "Throat thermal-fatigue cycle life" row, not a burst/collapse
            # one (standard primary/secondary classification, e.g. ASME BPVC
            # Sec. III: P_m <= S_m, secondary stresses limited by shakedown/
            # fatigue). Holding hoop + thermal to allowable/SF failed EVERY
            # real tube-wall engine in the corpus (F-1 423 vs 133 MPa, J-2
            # 990 vs 67, RL10 761 vs 67) and Huzel's own Sample Calc 4-4.
            # Combined stress is still reported. See ASSUMPTIONS.md.
            # Governing station = the one furthest over ITS OWN allowable
            # (the two stations can be different materials), not the one
            # with the bigger raw stress - that hid e.g. a copper throat
            # over its lower allowable behind a larger exit stress.
            util_throat = hoop_throat / (s.chamber_material.allowable_stress_pa
                                         / mass_model.SAFETY_FACTOR)
            util_worst = hoop_worst / (worst_material.allowable_stress_pa
                                       / mass_model.SAFETY_FACTOR)
            if util_throat >= util_worst:
                station_name = "throat"
                station_eps = 1.0
                net_dp_pa, hoop_pa, thermal_pa, combined_pa = (
                    net_throat, hoop_throat, thermal_throat, combined_throat)
                station_material, station_t_m = s.chamber_material, t_construction_throat_m
                station_t_limit = t_limit_throat
            else:
                station_name = "cooled_length_end"
                station_eps = worst_eps
                net_dp_pa, hoop_pa, thermal_pa, combined_pa = (
                    net_worst, hoop_worst, thermal_worst, combined_worst)
                station_material, station_t_m = worst_material, t_construction_worst_m
                station_t_limit = t_limit_worst

            allowable_pa = station_material.allowable_stress_pa / mass_model.SAFETY_FACTOR
            # (1e-9 slack: a hoop-sized wall lands exactly on the allowable)
            s.jacket_overpressure_ok = hoop_pa <= allowable_pa * (1.0 + 1e-9)
            s.jacket_overpressure_worst_station = station_name
            s.jacket_combined_stress_pa = combined_pa
            s.jacket_hoop_stress_pa = hoop_pa
            s.jacket_thermal_stress_pa = thermal_pa
            station_desc = ("the throat" if station_name == "throat"
                             else f"the end of active cooling (area ratio ~{station_eps:.1f})")
            # Secondary-stress note, shown on pass or fail. Throat thermal
            # stress is the one the fatigue row evaluates (it peaks there).
            yield_pa = s.chamber_material.allowable_stress_pa
            thermal_note = (
                f"The thermal-restraint stress (~{thermal_throat/1e6:.0f} MPa at the throat, "
                f"dT = q*t/k across the wall) is a self-limiting secondary stress, not a "
                f"burst load")
            if hoop_throat + thermal_throat > yield_pa:
                thermal_note += (
                    f": with the hoop load it exceeds {s.chamber_material.display_name}'s "
                    f"~{yield_pa/1e6:.0f} MPa hot yield, so the hot face yields a little each "
                    f"firing - expected for a regen tube wall (the real F-1/J-2/RL10 do the same "
                    f"in this model). Its life limit is the 'Throat thermal-fatigue cycle "
                    f"life' row")
            thermal_note += "."
            jacket_overpressure_ok_detail = (
                f"OK - primary hoop stress ~{hoop_pa/1e6:.0f} MPa (~{net_dp_pa/1e6:.1f} MPa net "
                f"jacket-vs-gas differential, {formula_name}) vs a ~{allowable_pa/1e6:.0f} MPa "
                f"allowable at {station_desc} ({station_material.display_name}, SF "
                f"{mass_model.SAFETY_FACTOR:.1f}, wall ~{station_t_m*1e3:.2f} mm). {thermal_note}")
            if not s.jacket_overpressure_ok:
                if self.wall_construction == "coax_shell":
                    # Large-radius thin liner: r/t is inherently large (a
                    # continuous shell at full chamber radius, sized thin
                    # for heat transfer per Huzel's own description of the
                    # inner shell as structurally separate from the outer
                    # jacket) - almost ANY meaningful net pressure
                    # differential produces high stress here, at nearly
                    # any cooling extent, not just extreme designs. This
                    # matches real history: coax-shell construction was
                    # only ever used on small/early engines (V-2, early
                    # Atlas - see cooling.WALL_CONSTRUCTIONS's own
                    # comment), never scaled up. Expected/near-universal
                    # for this construction, not a marginal edge case.
                    mitigation = ("this construction only models the inner liner, not a "
                                   "supporting outer structural jacket that would share the "
                                   "load in a real design - consider tube_wall or "
                                   "milled_channel construction instead for a chamber this size")
                    framing = ("a large-radius thin shell inherently has a high stress-per-"
                                "unit-pressure ratio - this is expected/near-universal for "
                                "coax_shell at this scale, matching why real coax-shell "
                                "designs stayed small (V-2/early-Atlas class), not a marginal "
                                "or unusual result")
                else:
                    # Only reachable at the cap: below it the wall is
                    # thickened until hoop passes (regen_hot_wall_thickness_m).
                    mitigation = ("the wall is already at its "
                                   f"~{REGEN_HOT_WALL_THICKNESS_M*1e3:.1f} mm regen hot-wall "
                                   "maximum - consider more/narrower tubes there (tube count, "
                                   "tube split), lower jacket pressure (shorter cooled length, "
                                   "less jacket dP) or a stronger alloy")
                    framing = "the tube cannot hold its coolant pressure as drawn"
                jacket_overpressure_detail = (
                    f"At {station_desc}, the primary hoop stress ({formula_name}) is "
                    f"~{hoop_pa/1e6:.0f} MPa from a ~{net_dp_pa/1e6:.1f} MPa net jacket-vs-gas "
                    f"differential, against a ~{allowable_pa/1e6:.0f} MPa allowable "
                    f"({station_material.display_name}, SF {mass_model.SAFETY_FACTOR:.1f}) with "
                    f"the wall at ~{station_t_m*1e3:.2f} mm ({station_t_limit}-limited) - "
                    f"{framing}. {mitigation[:1].upper() + mitigation[1:]}. {thermal_note}")
        else:
            # milled_channel: unchanged clamped-plate-strip proxy.
            n_ch_worst = cooling.channel_count_at_station(
                s._n_ch_visual, worst_eps, s.split_eps_eff)
            channel_width_worst_m = cooling.channel_hydraulic_geometry(
                2.0 * worst_r_m, n_ch_worst, s._channel_height_visual,
                s._land_fraction_visual)["width_m"]
            net_dp_pa = jacket_pressure_pa - p_local_gas_worst_pa
            # Long clamped rectangular-plate-strip approximation (span =
            # channel width b, aspect ratio >> 1 since channels run the
            # wall's full length): peak bending stress at the clamped rib
            # edge, sigma_max = q * b^2 / (2 * t^2), the standard clamped-
            # clamped beam-strip result (M_support = q*b^2/12 per unit
            # width, section modulus t^2/6). Tier 3: the formula SHAPE is a
            # standard plate/beam-strip result, not invented, but has no
            # real-engine spot check in this codebase (see ASSUMPTIONS.md).
            equivalent_bending_stress_pa = (
                net_dp_pa * channel_width_worst_m ** 2 / (2.0 * t_worst_m ** 2)
                if channel_width_worst_m > 0 else 0.0)
            allowable_pa = worst_material.allowable_stress_pa / mass_model.SAFETY_FACTOR
            s.jacket_overpressure_ok = not (net_dp_pa > 0.0 and equivalent_bending_stress_pa > allowable_pa)
            s.jacket_overpressure_worst_station = "cooled_length_end"
            s.jacket_combined_stress_pa = equivalent_bending_stress_pa
            if not s.jacket_overpressure_ok:
                jacket_overpressure_detail = (
                    f"Near the end of active cooling (area ratio ~{worst_eps:.1f}), estimated "
                    f"jacket/coolant pressure (~{jacket_pressure_pa/1e6:.1f} MPa) exceeds local "
                    f"hot-gas static pressure (~{p_local_gas_worst_pa/1e6:.1f} MPa) - the net load on "
                    f"the channel-land wall there REVERSES direction. Modeled as a clamped-strip "
                    f"bending stress across the ~{channel_width_worst_m*1000:.1f} mm channel width, "
                    f"this reversed ~{net_dp_pa/1e6:.1f} MPa differential is "
                    f"~{equivalent_bending_stress_pa/1e6:.0f} MPa against a "
                    f"~{allowable_pa/1e6:.0f} MPa allowable ({worst_material.display_name}, SF "
                    f"{mass_model.SAFETY_FACTOR:.1f}) - but this is a coarse clamped-plate-strip "
                    f"proxy, NOT a real buckling/FEA analysis, and this codebase has no real-engine "
                    f"spot check for it yet. Treat this as 'worth a closer structural look', not a "
                    f"validated failure prediction. Consider more/narrower channels (smaller span), "
                    f"tapering the actively-cooled length, or a thicker wall there.")
    _check(s.checklist, s.warnings, "cooling", "Jacket overpressure vs. channel-wall structural margin",
           s.jacket_overpressure_ok, jacket_overpressure_detail,
           "n/a - only evaluated in \"channels\" regen mode with an active jacket"
           if not jacket_overpressure_active
           else jacket_overpressure_ok_detail)
    _check(s.checklist, s.warnings, "cooling", "Tube-wall longitudinal thermal buckling margin",
           buckling_ok, buckling_detail,
           "n/a - only evaluated for tube_wall construction with an active jacket"
           if not buckling_active
           else (buckling_detail if buckling_detail else "OK - thermal-restraint stress stays "
                 "under 0.9x the critical buckling stress"))


def tubes_and_hatbands(self, s):
    """Tube taper + structural hatbands, jacket structure mass, feed-system plausibility."""
    # --- tube_wall: swaged-tube taper limit + structural hatbands -------
    # A brazed tube bundle is contiguous: each tube is swaged/expanded to a
    # taper and "spanked" to fill the local pitch [Huzel p.113-114; SP-8087
    # Sec.2.1.1.3 p.12-13, Fig. 1]. Its width therefore tracks the local
    # circumference / tube count, and one tube's max/min width ratio over its
    # run is limited: 3.5:1 by pure reduction, 6:1 with a 2:1 expansion; past
    # that a bifurcation (tube_split_eps) is needed.
    tube_taper_ratio = 0.0
    hatband_result = None
    s.hatband_mass_kg = 0.0
    hatband_banded_fraction = 0.0
    is_tube_wall = (self.wall_construction == "tube_wall"
                    and s.chamber_cooling in ("regenerative", "dump"))
    if is_tube_wall and s.throat_r_m > 0:
        _n_tube_base = cooling.channel_count(s.geo["throat_dia_m"], self.regen_channel_count)

        def _n_tubes_at(r_m):
            return cooling.channel_count_at_station(
                _n_tube_base, max((r_m / s.throat_r_m) ** 2, 1.0), s.split_eps_eff)

        _i_throat = int(np.argmin(s.rs))
        _eps_all = np.maximum((s.rs / s.throat_r_m) ** 2, 1.0)
        _cooled = np.ones(s.rs.size, dtype=bool)
        _cooled[_i_throat:] = _eps_all[_i_throat:] <= s.cooled_length_eps * (1 + 1e-9)
        if self.chamber_tube_jacket:
            _cooled[:_i_throat] = False      # chamber is a continuous jacket, not tubes
        _n_st = np.array([_n_tubes_at(r) for r in s.rs])
        for _n in np.unique(_n_st[_cooled]):
            _w = s.rs[_cooled & (_n_st == _n)] / _n
            if _w.size >= 2 and _w.min() > 0:
                tube_taper_ratio = max(tube_taper_ratio, float(_w.max() / _w.min()))
        _check(s.checklist, s.warnings, "cooling", "Tube taper within swage/expand limit (SP-8087)",
               tube_taper_ratio <= 6.0,
               f"A single cooling tube must taper {tube_taper_ratio:.1f}:1 along its run - past "
               f"SP-8087's 6:1 limit for a swaged (3:1) + expanded (2:1) tube. Add a tube "
               f"bifurcation (Tube split area ratio) so the tube count doubles downstream.",
               f"OK - max tube taper {tube_taper_ratio:.1f}:1"
               + (" (beyond 3.5:1 pure reduction - needs an expansion step, SP-8087)"
                  if tube_taper_ratio > 3.5 else ""))

        if self.tube_hatbands:
            _band_mat = materials.MATERIALS.get(self.tube_hatband_material,
                                                 materials.MATERIALS["inconel_718"])
            _tube_h_m, s._ = cooling.channel_target_height_m(
                s.geo["throat_dia_m"], _n_tube_base, s.mdot_coolant_jacket_kgs,
                self.propellant_pair,
                (self.regen_channel_land_fraction if self.regen_channel_land_fraction > 0
                 else cooling.CHANNEL_LAND_FRACTION_DEFAULT),
                aspect_ratio_override=self.regen_channel_aspect_ratio,
                target_velocity_ms=self.regen_coolant_velocity_ms)
            # Bands run aft of the THROAT over the body's tube wall (plus the
            # extension if toggled): SP-8120 Sec.2.2.1 - a continuous structural
            # shell is normal practice over the chamber/throat, bands take over
            # downstream where wall pressure falls. The chamber (upstream of the
            # throat) keeps the tube_wall continuous-jacket mass below.
            _x0 = float(s.xs[_i_throat])
            _x1 = (float(s.ext_xs[-1]) if (self.tube_hatbands_on_extension and s.has_extension
                                          and len(s.ext_xs)) else float(s.body_xs[-1]))
            hatband_result = hatbands.size_bands(
                s.xs, s.rs, _x0, _x1, self.chamber_pressure_pa, s.gamma, _band_mat,
                s.chamber_material, _n_tubes_at, _tube_h_m,
                shape=(self.tube_hatband_shape
                       if self.tube_hatband_shape in hatbands.BAND_SHAPE_CHOICES else "auto"),
                count_override=self.tube_hatband_count,
                width_override_m=self.tube_hatband_width_m,
                p_amb_pa=0.0 if s.separated_100pct else PA_SEA_LEVEL,
                tube_crest_offset_m=_tube_h_m + 2.0 * hatbands.TUBE_WALL_T_REF_M)
            s.hatband_mass_kg = hatbands.hatband_mass_kg(hatband_result["bands"])
            # SP-8120: bands REPLACE the continuous structural shell where they
            # run, so the tube_wall "structural jacket" mass extra is dropped over
            # the banded fraction of the body's wall area.
            _bx, _br = np.asarray(s.body_xs, float), np.asarray(s.body_rs, float)
            if _bx.size >= 2 and hatband_result["n_bands"] > 0:
                _ds = np.hypot(np.diff(_bx), np.diff(_br))
                _da = 2.0 * np.pi * 0.5 * (_br[1:] + _br[:-1]) * _ds
                _xm = 0.5 * (_bx[1:] + _bx[:-1])
                _in = (_xm >= (hatband_result["shell_end_x_m"] or _x0)) & (_xm <= _x1)
                hatband_banded_fraction = (float(_da[_in].sum() / _da.sum())
                                           if _da.sum() > 0 else 0.0)
            _check(s.checklist, s.warnings, "cooling", "Hatband structural adequacy (SP-8120)",
                   hatband_result["all_ok"],
                   "Hatbands: " + " ".join(hatband_result["advisories"]),
                   f"OK - {hatband_result['n_bands']} bands "
                   f"({'/'.join(hatband_result['shapes_used']) or 'none'}), "
                   f"{s.hatband_mass_kg:.1f} kg, carry all hoop load"
                   + (f"; worst ring-buckling margin "
                      f"{hatband_result['worst_buckling_margin']:.2f}"
                      if np.isfinite(hatband_result['worst_buckling_margin']) else ""))
    s.cooling_result["tube_taper_ratio"] = tube_taper_ratio
    s.cooling_result["hatbands"] = hatband_result
    s.cooling_result["hatband_mass_kg"] = s.hatband_mass_kg

    # Extra jacket structure for a non-milled wall construction (tube bundle
    # + jacket / coax outer shell), on top of the bare hoop-stress shell.
    # Only where there's an active coolant loop; milled_channel factor 1.0 -> 0.
    # Structural hatbands replace that shell over the banded fraction (above).
    s.jacket_structure_mass_kg = 0.0
    if s.chamber_cooling in ("regenerative", "dump"):
        s.jacket_structure_mass_kg = mass_model.jacket_structure_mass_kg(
            s.chamber_wall_mass_kg,
            cooling.JACKET_MASS_CONSTRUCTION_FACTOR.get(self.wall_construction, 1.0)
        ) * (1.0 - hatband_banded_fraction)
    s.turbopump_mass_kg = s.cyc["turbopump"]["turbopump_mass_kg"] if s.cyc["has_turbopump"] else 0.0

    # --- feed-system pump plausibility (structural PLAUSIBILITY flag - see
    # ASSUMPTIONS.md / turbopump_sizing.FEED_DP_PLAUSIBLE_CEILING_PA). The
    # pump is always SOLVED to deliver whatever dp_fuel/dp_ox was just
    # computed above (no starvation failure mode exists by construction -
    # see turbopump_sizing.py's module docstring); this instead flags when
    # the DEMAND itself falls outside real flight-turbopump historical
    # practice [SP-8107 Tables V-VI], the honest proxy for "real hardware
    # may not deliver this flow." Only meaningful where a pump exists
    # (pressure-fed has none - that's a tank-pressure question instead).
    feed_plausibility_detail = ""
    if s.cyc["has_turbopump"]:
        feed_plausibility_detail = turbopump_sizing.feed_dp_plausibility_warning(s.dp_fuel, s.dp_ox) or ""
    _check(s.checklist, s.warnings, "turbopump", "Feed-system pump plausibility",
           not feed_plausibility_detail, feed_plausibility_detail,
           "n/a - no turbopump (pressure-fed)" if not s.cyc["has_turbopump"]
           else f"OK - required dP within {turbopump_sizing.FEED_DP_PLAUSIBLE_CEILING_PA/1e6:.0f} MPa "
                "of real flight-turbopump practice")
