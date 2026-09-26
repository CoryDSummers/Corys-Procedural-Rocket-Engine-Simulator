"""Injector-geometry / manifold / jacket-ring / stability stages of _compute_pass.

Split verbatim out of the former single-file design.py; a value shared
between stages lives on the PassState `s` (see design/state.py)."""
import numpy as np

from .. import (combustion_stability, cooling, geometry, injectors, manifold, plumbing)
from .constants import (
    REGEN_CIRCUIT_STYLE_BY_TOPOLOGY,
)
from .checklist import _check


def injector_and_manifolds(self, s):
    """Injector element geometry, propellant manifolds, jacket inlet/return pressures."""
    # Injector element geometry (physics/injectors.py) + chamber acoustic
    # modes (physics/combustion_stability.py) - detail for the Injectors tab.
    s.injector_geometry = injectors.element_geometry(
        s.mdot_fuel_kgs, s.mdot_ox_kgs, s.rho_fuel, s.rho_ox, s.dp_injector, self.injector_type,
        cd=s.orifice_cd, dp_fuel_pa=s.dp_injector_fuel, dp_ox_pa=s.dp_injector_ox,
        included_angle_deg=self.impingement_angle_deg)

    # Propellant intake manifold sizing (physics/manifold.py) - real
    # cross-section from mdot/density/target feed velocity, mass from
    # hoop stress against the actual local feed pressure (pc_feed + this
    # leg's injector dP - NOT pump discharge pressure, which is
    # upstream of the manifold and undefined on the pressure-fed branch).
    # Each ring's velocity puts its dynamic head at the user's fraction
    # of that leg's own injector dP (manifold.velocity_from_head_fraction).
    fuel_feed_velocity_ms = manifold.velocity_from_head_fraction(
        self.fuel_manifold_head_fraction, s.dp_injector_fuel, s.rho_fuel)
    ox_feed_velocity_ms = manifold.velocity_from_head_fraction(
        self.ox_manifold_head_fraction, s.dp_injector_ox, s.rho_ox)
    # Each header ring's taper INLET follows the user's pipe: the first
    # plumbing run rooted on that host sets its inlet angle (else the
    # defaults - fuel 0, ox 180, jacket 0).
    s._inlet_angles = {}
    for _rd in (self.plumbing_runs or []):
        _r0 = plumbing.run_from_dict(_rd)
        if _r0.pipes and _r0.host not in s._inlet_angles:
            s._inlet_angles[_r0.host] = float(_r0.attach_angle_deg)
    s.manifold_result = manifold.size_manifolds(
        s.mdot_fuel_kgs, s.mdot_ox_kgs, s.rho_fuel, s.rho_ox, s.pc_feed,
        s.dp_injector_fuel, s.dp_injector_ox, s.geo["chamber_dia_m"],
        feed_velocity_target_ms={"fuel": fuel_feed_velocity_ms,
                                  "ox": ox_feed_velocity_ms},
        taper_blend={"fuel": self.fuel_manifold_taper_blend,
                     "ox": self.ox_manifold_taper_blend},
        inlet_angles_deg={k: v for k, v in s._inlet_angles.items() if k in ("fuel", "ox")})
    s.manifold_mass_kg = s.manifold_result["total_mass_kg"]
    _fuel_thin_warn = manifold.thin_wall_warning(
        s.manifold_result["fuel"]["thin_wall_ratio"], "Fuel")
    _check(s.checklist, s.warnings, "manifold", "Fuel manifold thin-wall approximation validity",
           not _fuel_thin_warn, _fuel_thin_warn or "",
           f"OK - t/r {s.manifold_result['fuel']['thin_wall_ratio']:.2f}")
    _ox_thin_warn = manifold.thin_wall_warning(
        s.manifold_result["ox"]["thin_wall_ratio"], "Ox")
    _check(s.checklist, s.warnings, "manifold", "Ox manifold thin-wall approximation validity",
           not _ox_thin_warn, _ox_thin_warn or "",
           f"OK - t/r {s.manifold_result['ox']['thin_wall_ratio']:.2f}")
    _fuel_bore_warn = manifold.bore_vs_chamber_warning(
        s.manifold_result["fuel"]["inner_diameter_m"], s.geo["chamber_dia_m"], "Fuel")
    _check(s.checklist, s.warnings, "manifold", "Fuel manifold bore vs. chamber packaging",
           not _fuel_bore_warn, _fuel_bore_warn or "", "OK")
    _ox_bore_warn = manifold.bore_vs_chamber_warning(
        s.manifold_result["ox"]["inner_diameter_m"], s.geo["chamber_dia_m"], "Ox")
    _check(s.checklist, s.warnings, "manifold", "Ox manifold bore vs. chamber packaging",
           not _ox_bore_warn, _ox_bore_warn or "", "OK")
    s._fuel_lh2 = self.propellant_pair == "LOX/LH2"
    _fuel_vel_warn = manifold.velocity_cap_warning(fuel_feed_velocity_ms, "Fuel",
                                                    supercritical=s._fuel_lh2)
    _check(s.checklist, s.warnings, "manifold", "Fuel manifold feed velocity vs. SP-8087 limit",
           not _fuel_vel_warn, _fuel_vel_warn or "",
           f"OK - {fuel_feed_velocity_ms:.1f} m/s"
           + (" (LH2: SP-8087 liquid limit n/a, gas Mach criterion not modelled)"
              if s._fuel_lh2 else ""))
    _ox_vel_warn = manifold.velocity_cap_warning(ox_feed_velocity_ms, "Ox")
    _check(s.checklist, s.warnings, "manifold", "Ox manifold feed velocity vs. SP-8087 limit",
           not _ox_vel_warn, _ox_vel_warn or "",
           f"OK - {ox_feed_velocity_ms:.1f} m/s")

    # Regen-cooling JACKET's own coolant-supply ring(s) (physics/manifold.
    # size_jacket_manifolds) - distinct from the injector-feed rings just
    # above. jacket_inlet_pressure_pa reuses the same formula already used
    # by the jacket-overpressure check further down (pc_feed + injector dP
    # + jacket_dp_pa - "the JACKET-INLET pressure...matching real counter-
    # flow regen routing"), computed here unconditionally rather than only
    # inside that check's own gated block. jacket_return_pressure_pa is
    # lower by the down-leg's own (Tier-3, arbitrary-symmetric-split) share
    # of the jacket's total pressure drop - only meaningful/used under
    # f1_split_reverse_flow. cooled_length_eps (not eps_for_transition -
    # see that field's own comment for why they can differ) is split out
    # separately here rather than reusing the mass-rollup section's own
    # split (further down, split at a DIFFERENT eps) - see ASSUMPTIONS.md.
    s.jacket_inlet_pressure_pa = s.pc_feed + s.dp_injector_fuel + s.jacket_dp_pa
    # Share of the jacket dP spent before the return/turnaround ring: the
    # two-pass march's REAL down-pass share when it ran; the Tier-3
    # symmetric split otherwise (f1_split_reverse_flow, or flat mode).
    _march_for_split = s.thermal["march"]    # the one real-contour march
    if (s.two_pass and _march_for_split and _march_for_split.get("jacket_dp_pa", 0) > 0
            and "jacket_dp_down_pa" in _march_for_split):
        s.jacket_return_split_fraction = (_march_for_split["jacket_dp_down_pa"]
                                        / _march_for_split["jacket_dp_pa"])
    else:
        s.jacket_return_split_fraction = manifold.JACKET_RETURN_SPLIT_FRACTION
    s.jacket_return_pressure_pa = (s.jacket_inlet_pressure_pa
                                  - s.jacket_dp_pa * s.jacket_return_split_fraction)


def jacket_manifolds_and_stability(self, s):
    """Jacket coolant-supply rings, J-2 rows, injector beta angle, acoustic stability, the cooling result dict."""
    # Local coolant-passage height at the jacket end sizes the split
    # topology's small turnaround collar (manifold.TURNAROUND_BORE_*);
    # None (no "channels" geometry) -> manifold's throat-dia fallback.
    turnaround_passage_height_m = (
        float(np.interp(s.x_jacket_end_m, s.xs, s.channel_geometry["height_m"]))
        if s.channel_geometry is not None else None)
    # Jacket-inlet ring velocity = the coolant-PASSAGE velocity at the
    # ring's own station (cooling.passage_velocity_ms - pure, so it works
    # in both regen channel models): SP-8087's constant-velocity torus
    # [SP-8087 Sec.2.1.2.1 p.19-20] / Fagherazzi's "no abrupt velocity
    # change between the supply volute and the channels". Station: the
    # bell end for single-pass, the forward (chamber) station for the
    # F-1 split topology.
    # J-2 layout: the mid-nozzle inlet station, and the DOWN-tube velocity
    # there (down + up tubes share the circumference -> ~3x faster).
    x_jacket_mid_inlet_m, jacket_mid_inlet_dia_m = None, None
    # Passages are sized at the REAL coolant inlet density (the thermal solve's
    # march), so the rings see the same passage velocities the march does.
    _m = s.thermal["march"]
    _rho_in = (_m["rho_inlet_kg_m3"] if (_m is not None and s.thermal["coolant_model"].table)
               else None)
    if s.two_pass:
        _jin_xs, _jin_rs, s._, s._, s._ = geometry.split_profile_by_area_ratio(
            s.xs, s.rs, s.geo["throat_dia_m"], s.jacket_inlet_eps_eff)
        x_jacket_mid_inlet_m = float(_jin_xs[-1])
        jacket_mid_inlet_dia_m = 2.0 * float(_jin_rs[-1])
        jacket_inlet_velocity_ms = cooling.down_pass_velocity_ms(
            jacket_mid_inlet_dia_m, s.geo["throat_dia_m"], s.mdot_coolant_jacket_kgs,
            self.propellant_pair, n_channels=self.regen_channel_count,
            aspect_ratio=self.regen_channel_aspect_ratio,
            target_velocity_ms=self.regen_coolant_velocity_ms,
            land_fraction=self.regen_channel_land_fraction, rho_kg_m3=_rho_in)
    else:
        _jin_station_dia_m = (s.geo["chamber_dia_m"]
                              if self.cooling_flow_topology == "f1_split_reverse_flow"
                              else s.local_bore_dia_m)
        jacket_inlet_velocity_ms = cooling.passage_velocity_ms(
            _jin_station_dia_m, s.geo["throat_dia_m"], s.mdot_coolant_jacket_kgs,
            self.propellant_pair, n_channels=self.regen_channel_count,
            aspect_ratio=self.regen_channel_aspect_ratio,
            target_velocity_ms=self.regen_coolant_velocity_ms,
            land_fraction=self.regen_channel_land_fraction, split_eps=s.split_eps_eff,
            rho_kg_m3=_rho_in)
    # User trim on the matched velocity (1.0 = Fagherazzi's match).
    _jin_vmult = min(max(self.jacket_inlet_velocity_mult, 0.5), 2.0)
    jacket_inlet_velocity_ms *= _jin_vmult
    s.jacket_manifold_result = manifold.size_jacket_manifolds(
        s.mdot_fuel_kgs, s.rho_fuel, self.cooling_flow_topology, self.manifold_bypass_fraction,
        s.jacket_inlet_pressure_pa, s.jacket_return_pressure_pa, s.geo["chamber_dia_m"],
        s.local_bore_dia_m, s.x_jacket_inlet_forward_m, s.x_jacket_end_m,
        feed_velocity_target_ms=jacket_inlet_velocity_ms,
        turnaround_passage_height_m=turnaround_passage_height_m,
        throat_dia_m=s.geo["throat_dia_m"], taper_blend=self.jacket_inlet_taper_blend,
        inlet_angle_deg=s._inlet_angles.get("jacket_inlet", 0.0),
        mid_inlet_x_m=x_jacket_mid_inlet_m, mid_inlet_dia_m=jacket_mid_inlet_dia_m,
        turnaround_velocity_ms=cooling.passage_velocity_ms(
            s.local_bore_dia_m, s.geo["throat_dia_m"], s.mdot_coolant_jacket_kgs,
            self.propellant_pair, n_channels=self.regen_channel_count,
            aspect_ratio=self.regen_channel_aspect_ratio,
            target_velocity_ms=self.regen_coolant_velocity_ms,
            land_fraction=self.regen_channel_land_fraction,
            split_eps=s.split_eps_eff, rho_kg_m3=_rho_in))
    s.jacket_manifold_mass_kg = s.jacket_manifold_result["total_mass_kg"]

    _jin_thin_warn = manifold.thin_wall_warning(
        s.jacket_manifold_result["jacket_inlet"]["thin_wall_ratio"], "Jacket inlet")
    _check(s.checklist, s.warnings, "manifold", "Jacket inlet manifold thin-wall approximation validity",
           not _jin_thin_warn, _jin_thin_warn or "",
           f"OK - t/r {s.jacket_manifold_result['jacket_inlet']['thin_wall_ratio']:.2f}")
    if s.two_pass:
        _clamped = abs(s.jacket_inlet_eps_eff - self.jacket_inlet_eps) > 1e-9
        _check(s.checklist, s.warnings, "cooling", "J-2 mid-nozzle inlet station",
               not _clamped,
               f"Jacket inlet area ratio {self.jacket_inlet_eps:.1f} lies outside the cooled "
               f"nozzle (throat .. eps {s.cooled_length_eps:.1f}) - clamped to "
               f"{s.jacket_inlet_eps_eff:.1f}"
               + (" (a zero-length down pass: this is single-pass cooling with a turnaround "
                  "collar)." if s.jacket_inlet_eps_eff >= s.cooled_length_eps else "."),
               f"OK - inlet at eps {s.jacket_inlet_eps_eff:.1f}, down tubes to eps "
               f"{s.cooled_length_eps:.1f}")
        _check(s.checklist, s.warnings, "cooling", "J-2 layout tube split",
               not (self.tube_split_eps and self.tube_split_eps > 0),
               "tube_split_eps is ignored under the J-2 mid-nozzle inlet layout - the two-"
               "pass circuit sets its own tube counts (1 down : 2 up, the real J-2's 180/360).",
               "OK")
        _check(s.checklist, s.warnings, "cooling", "J-2 layout two-pass march",
               self.regen_channel_model == "channels" or s.chamber_cooling != "regenerative",
               "The J-2 two-pass coolant march (cooling.march_coolant_two_pass) only runs in "
               "the \"channels\" regen model - the \"flat\" model keeps its lumped jacket dP "
               "and coolant dT, so only the manifold geometry reflects this layout.",
               "OK")
    _jin_vel_warn = manifold.velocity_cap_warning(
        jacket_inlet_velocity_ms, "Jacket inlet", supercritical=s._fuel_lh2)
    _check(s.checklist, s.warnings, "manifold", "Jacket inlet manifold velocity vs. SP-8087 limit",
           not _jin_vel_warn, _jin_vel_warn or "",
           f"OK - {jacket_inlet_velocity_ms:.1f} m/s (= {_jin_vmult:.2f} x local "
           "coolant-passage velocity)"
           + (" (LH2: SP-8087 liquid limit n/a, gas Mach criterion not modelled)"
              if s._fuel_lh2 else ""))
    _jin_bore_warn = manifold.bore_vs_chamber_warning(
        s.jacket_manifold_result["jacket_inlet"]["inner_diameter_m"], s.geo["chamber_dia_m"],
        "Jacket inlet")
    _check(s.checklist, s.warnings, "manifold", "Jacket inlet manifold bore vs. chamber packaging",
           not _jin_bore_warn, _jin_bore_warn or "", "OK")
    if s.jacket_manifold_result.get("jacket_return"):
        _jret_thin_warn = manifold.thin_wall_warning(
            s.jacket_manifold_result["jacket_return"]["thin_wall_ratio"], "Jacket return")
        _check(s.checklist, s.warnings, "manifold",
               "Jacket return manifold thin-wall approximation validity",
               not _jret_thin_warn, _jret_thin_warn or "",
               f"OK - t/r {s.jacket_manifold_result['jacket_return']['thin_wall_ratio']:.2f}")
        _jret_bore_warn = manifold.bore_vs_chamber_warning(
            s.jacket_manifold_result["jacket_return"]["inner_diameter_m"], s.local_bore_dia_m,
            "Jacket return")
        _check(s.checklist, s.warnings, "manifold",
               "Jacket return manifold bore vs. local nozzle packaging",
               not _jret_bore_warn, _jret_bore_warn or "", "OK")

    _beta_warn = injectors.beta_warning(s.injector_geometry["beta_deg"], self.propellant_pair)
    _check(s.checklist, s.warnings, "injector", "Injector resultant beta angle",
           not _beta_warn, _beta_warn or "",
           f"OK - beta {s.injector_geometry['beta_deg']:+.1f} deg"
           + ("" if 20.0 <= self.impingement_angle_deg <= 45.0
              else f" (impingement angle {self.impingement_angle_deg:.0f} deg outside 20-45)"))
    _check(s.checklist, s.warnings, "injector", "Impingement angle within 20-45 deg",
           20.0 <= self.impingement_angle_deg <= 45.0,
           f"Impingement included angle {self.impingement_angle_deg:.0f} deg is outside the "
           f"satisfactory 20-45 deg range [Huzel 4.5] - too shallow mixes poorly, too steep "
           f"risks splash-back onto the injector face.")
    a_e_ms = combustion_stability.speed_of_sound(s.gamma_chamber, s.m_molar, s.tc)
    s.chamber_acoustics = combustion_stability.acoustic_modes(
        a_e_ms, s.geo["chamber_length_m"], s.geo["chamber_dia_m"])
    # Raw advisory uses the EFFECTIVE dP/Pc (a stiff injector build clears it
    # here, exactly as raising injector dP does in real practice). If it
    # still fires, injector-face baffles and/or corner Helmholtz cavities
    # can resolve it (aids_resolution). Warn-not-block either way.
    stability_advisory = combustion_stability.instability_prone(
        s.chamber_acoustics, s.effective_dp_over_pc, self.target_vac_thrust_n)
    stability_resolution = None
    if stability_advisory:
        stability_resolution = combustion_stability.aids_resolution(
            s.chamber_acoustics, baffles=self.injector_baffles,
            baffle_compartments=self.baffle_compartments,
            cavities=self.acoustic_cavities, cavity_count=self.acoustic_cavity_count)
    stability_ok = (not stability_advisory) or (stability_resolution is not None)
    _stability_pass_detail = (
        f"OK - resolved: {stability_resolution}" if stability_resolution
        else f"OK - 1T ~{s.chamber_acoustics['tang_1t_hz']:.0f} Hz, 1L "
             f"~{s.chamber_acoustics['long_1l_hz']:.0f} Hz"
             + ("" if self.injector_stiffness == "nominal"
                else f" (stiff injector dP/Pc {s.effective_dp_over_pc:.2f})"))
    _check(s.checklist, s.warnings, "stability", "Combustion acoustic-mode margin",
           stability_ok, stability_advisory or "", _stability_pass_detail)
    _check(s.checklist, s.warnings, "stability", "Baffle compartment count",
           (not self.injector_baffles)
           or combustion_stability.baffle_compartments_ok(self.baffle_compartments),
           f"Injector-face baffle has {self.baffle_compartments} compartments - use an ODD "
           f"count >= 3 (SSME used 5). An even number sits on the tangential-mode nodal "
           f"lines and ENHANCES the standing mode.",
           f"OK - {self.baffle_compartments}-compartment baffle" if self.injector_baffles
           else "n/a - no baffle")

    s.stability_aid_mass_kg = combustion_stability.aid_mass_kg(
        s.geo["chamber_dia_m"], baffles=self.injector_baffles,
        baffle_compartments=self.baffle_compartments,
        cavities=self.acoustic_cavities, cavity_count=self.acoustic_cavity_count)
    s.stability_result = {
        "modes": s.chamber_acoustics,
        "advisory": stability_advisory,
        "resolution": stability_resolution,
        "resolved": stability_ok,
        "effective_dp_over_pc": s.effective_dp_over_pc,
        "injector_stiffness": self.injector_stiffness,
        "baffles": self.injector_baffles,
        "baffle_compartments": self.baffle_compartments,
        "cavities": self.acoustic_cavities,
        "cavity_count": self.acoustic_cavity_count,
        "aid_mass_kg": s.stability_aid_mass_kg,
    }

    s.cooling_result = {
        "chamber_cooling_method": s.chamber_cooling,
        "nozzle_cooling_method": s.nozzle_cooling,
        # Really a mass/mesh concept, not a cooling one - placed here anyway,
        # a pragmatic reuse of the one existing physics-result -> mesh-builder
        # gating path gui/mesh_builder.py already reads nozzle_cooling_method
        # from (see build_chamber_and_bell_shell_pieces's stiffening-ring/
        # orthogrid branch).
        "nozzle_extension_stiffening_style": self.nozzle_extension_stiffening_style,
        # the explicit method that was HARD-BLOCKED for that section's
        # material (None = honoured) - cooling.resolve_cooling_method_checked
        "chamber_cooling_rejected": s.chamber_cooling_rejected,
        "nozzle_cooling_rejected": s.nozzle_cooling_rejected,
        "wall_construction": self.wall_construction,
        "chamber_tube_jacket": self.chamber_tube_jacket,
        "tube_split_eps": s.split_eps_eff,
        "tube_hatbands": self.tube_hatbands,
        "tube_hatbands_on_extension": self.tube_hatbands_on_extension,
        "tube_hatband_count": self.tube_hatband_count,
        "tube_hatband_width_m": self.tube_hatband_width_m,
        "flange_thickness_m": self.flange_thickness_m,
        "flange_width_m": self.flange_width_m,
        "flange_bolt_count": self.flange_bolt_count,
        "regen_circuit_style": REGEN_CIRCUIT_STYLE_BY_TOPOLOGY.get(
            self.cooling_flow_topology, "single_pass_upflow"),
        "cooled_length_eps": s.cooled_length_eps,
        "regen_nozzle_end_eps": self.regen_nozzle_end_eps,
        "dump_coolant_fraction": s.dump_coolant_fraction_eff,
        "dump_mdot_kgs": s.dump_mdot_kgs,
        "dump_coolant_dt_k": s.dump_coolant_dt_k,
        "dump_isp_penalty_fraction": s.dump_isp_penalty_fraction,
        "chamber_cooling_source": (
            f"material-default - explicit {s.chamber_cooling_rejected} BLOCKED"
            if s.chamber_cooling_rejected else
            "explicit" if self.chamber_cooling_method not in ("", "auto")
            else "material-default"),
        "nozzle_cooling_source": (
            f"material-default - explicit {s.nozzle_cooling_rejected} BLOCKED"
            if s.nozzle_cooling_rejected else
            "explicit" if self.nozzle_cooling_method not in ("", "auto")
            else "material-default"),
        "q_profile_w_m2": s.q_profile_w_m2,
        "q_throat_w_m2": s.q_throat_w_m2,
        "q_chamber_avg_w_m2": s.q_chamber_avg_w_m2,
        "q_chamber_avg_anchor_w_m2": s.q_chamber_avg_anchor_w_m2,   # pre-Phase-7 anchor, reported only
        "q_profile_abs_w_m2": s.q_profile_w_m2,      # alias - q_profile_w_m2 IS the absolute profile now
        "q_throat_abs_w_m2": s.q_throat_abs_w_m2,
        "q_chamber_avg_abs_w_m2": s.q_chamber_avg_abs_w_m2,
        "wall_heat_total_w": s.wall_heat_w,
        "wall_heat_energy_fraction": s.wall_heat_energy_fraction,
        "coolant_delta_t_k": s.coolant_delta_t_k,
        "coolant_limit_k": s.coolant_limit_k,
        "regen_cooled": s.regen_cooled,
        "regen_ok": s.regen_ok,
        "hg_throat_w_m2k": s.hg_throat_w_m2k,
        "t_aw_chamber_k": s.t_aw_chamber_k,
        "t_wg_throat_k": s.t_wg_throat_k,
        # Coupled throat wall balance ("channels" + regen only; None otherwise):
        "t_wc_throat_k": s.t_wc_throat_coupled_k,
        "q_throat_wall_balance_w_m2": s.q_throat_wall_balance_w_m2,
        "h_g_throat_effective_w_m2k": s.h_g_throat_effective_w_m2k,
        "coolant_velocity_throat_ms": s.coolant_velocity_throat_ms,
        "hot_wall_thickness_m": s.hot_wall_thickness_m,
        "bell_wall_temp_k": s.bell_wall_temp_k,
        "film_cooling_fraction": s.film_fraction,
        "film_flux_factor": s.film_flux_factor,                 # cooled-zone area-average
        "film_flux_factor_effective": s.film_flux_factor,       # explicit alias
        "film_effectiveness_profile": s.film_phi,               # COMBINED (both sites)
        "chamber_film_profile": s.chamber_film_phi,
        "nozzle_film_profile": s.nozzle_film_phi,
        "gas_film_profile": s.gas_film_phi,                     # turbine-exhaust gas film
        "gas_film_temperature_k": s.gas_film_t_k,                # (nozzle_injection) or None
        "chamber_film_inject_area_ratio": self.chamber_film_inject_area_ratio,
        "nozzle_film_fraction": (self.nozzle_film_fraction if s.nozzle_film_active else 0.0),
        "nozzle_film_inject_eps": self.nozzle_film_inject_eps,
        "nozzle_film_isp_penalty_fraction": s.nozzle_film_isp_penalty_fraction,
        "film_temperature_k": s._t_film_k,                       # post-jacket film fuel temp
        "t_aw_film_profile_k": s.t_aw_film_profile_k,
        "film_cooled_length_eps": s.cooled_length_eps,
        # unified per-station thermal solve (cooling/thermal_solve.py)
        "wall_heat_regen_w": s.thermal["wall_heat_regen_w"],
        "wall_heat_dump_w": s.thermal["dump"]["heat_w"],
        "dump_jacket_dp_pa": s.thermal["dump"]["jacket_dp_pa"],
        "t_aw_profile_k": s.thermal["t_aw_k"],
        "bartz_sigma_profile": s.thermal["sigma"],
        "h_g_profile_w_m2k": s.thermal["h_g_w_m2k"],
        "t_wc_profile_k": s.thermal["t_wc_k"],
        "station_treatment": s.thermal["treatment"],
        "recovery_factor": s.thermal["recovery_factor"],
        "thermal_solve_iterations": s.thermal["iterations"],
        "thermal_solve_converged": s.thermal["converged"],
        "coolant_property_source": s.thermal["coolant_source"],
        "gas_property_source": s.ht_gas["source"],
        "gas_cp_frozen_j_kgk": s.cp_gas,
        "gas_viscosity_pa_s": s.mu_gas,
        "gas_prandtl": s.pr_gas,
        "coolant_inlet_t_k": s.coolant_inlet_k,
        "coolant_pressure_pa": s.coolant_p_pa,
        "mdot_coolant_jacket_kgs": s.mdot_coolant_jacket_kgs,
        # full-length coupled wall balance ("channels" regen only, else None)
        "t_wg_profile_k": s.t_wg_profile_k,
        "peak_wall_temp_k": s.peak_wall_temp_k,
        "peak_wall_temp_zone": s.peak_wall_temp_zone,
        "peak_wall_temp_eps": s.peak_wall_temp_eps,
        "peak_wall_margin_ratio": s.peak_wall_margin_ratio,
        "bell_wall_temp_eps": s.bell_wall_temp_eps,
        "regen_isp_bonus_fraction": s.regen_isp_bonus,
        "through_wall_delta_t_k": s.through_wall_delta_t_k,
        "throat_thermal_stress_pa": s.throat_thermal_stress_pa,
        "throat_fatigue_cycles": s.throat_fatigue_cycles,
        "regen_channel_model": self.regen_channel_model,
        "jacket_dp_pa": s.jacket_dp_pa,
        "coolant_channels": (s.coolant_march["n_channels"] if s.coolant_march else None),
        "coolant_channel_dh_throat_m": (s.coolant_march["channel_dh_throat_m"] if s.coolant_march else None),
        "coolant_exit_t_k": (s.coolant_march["coolant_exit_t_k"] if s.coolant_march else None),
        # the SOLVED coolant-side throat wall (fin-corrected, the one the margin
        # uses) - was the march's own uncoupled t_bulk + q/h_c (audit W6)
        "coolant_side_wall_t_throat_k": (s.t_wc_throat_coupled_k if s.coolant_march else None),
        "channel_land_fraction": (s._land_fraction_visual if s.channel_geometry else None),
        "channel_width_profile_m": (s.channel_geometry["width_m"] if s.channel_geometry else None),
        "channel_height_profile_m": (s.channel_geometry["height_m"] if s.channel_geometry else None),
        "channel_dh_profile_m": (s.channel_geometry["dh_m"] if s.channel_geometry else None),
        # Per-station bulk coolant velocity straight from the march (local
        # REAL density - supercritical H2 speeds up as it heats).
        "coolant_velocity_profile_ms": (s.coolant_march.get("velocity_profile_ms")
                                        if s.coolant_march else None),
        "jacket_inlet_velocity_ms": jacket_inlet_velocity_ms,
        "jacket_dp_down_pa": (s.coolant_march.get("jacket_dp_down_pa") if s.coolant_march else None),
        "coolant_turnaround_t_k": (s.coolant_march.get("coolant_turnaround_t_k")
                                   if s.coolant_march else None),
        "coolant_channels_down": (s.coolant_march.get("n_channels_down") if s.coolant_march else None),
        # Per-station bulk coolant temperature from the march (NaN outside the
        # cooled length; two-pass = the UP pass) - exported for
        # physics/flow_network.py, None outside "channels" mode.
        "coolant_t_bulk_profile_k": (s.coolant_march["t_bulk_profile_k"] if s.coolant_march else None),
    }
