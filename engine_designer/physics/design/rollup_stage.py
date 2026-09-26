"""Burn time, mass rollup, final checklist rows and the result dict.

Split verbatim out of the former single-file design.py; a value shared
between stages lives on the PassState `s` (see design/state.py)."""
import numpy as np

from .. import (combustion, cycles, electric_pump, gimbal, ignition, injectors,
                manifold, mass_model, materials)
from .constants import (
    PA_SEA_LEVEL,
    COOLANT_INLET_TEMP_K,
    OXIDIZER_INLET_TEMP_K,
    CONTRACTION_RATIO_TYPICAL,
    LSTAR_TYPICAL_M,
    BASE_RATED_BURN_TIME_S,
    RATED_TIME_MARGIN_MULT_MIN,
    RATED_TIME_MARGIN_MULT_MAX,
)
from .checklist import _check


def burn_time_and_mass(self, s):
    """Rated burn time, electric-pump battery/motor, injector plate, dry-mass rollup."""
    # Rated burn time: ablative chambers TARGET a burn time (ablative_target_burn_time_s,
    # a design input) rather than deriving one. That target sizes a real, independent
    # char-depth liner thickness (mass_model.ablative_liner_thickness_m, SP-8124's 1.25
    # char-depth safety factor) - the sacrificial material genuinely consumed over the
    # burn - separate from the hoop-stress wall thickness, which now correctly sizes the
    # STRUCTURAL OVERWRAP behind that liner (matching refrasil_phenolic's real documented
    # 3-layer liner+insulation+overwrap construction) rather than standing in for the
    # liner itself, as it used to (see ASSUMPTIONS.md for the gap this replaces). Every
    # other material scales a flat baseline by chamber thermal margin instead (see
    # BASE_RATED_BURN_TIME_S's comment above). Computed before the dry-mass sum because
    # the electric pump-fed cycle's battery mass scales with it.
    s.ablative_liner_thickness_m = 0.0
    s.ablative_liner_mass_kg = 0.0
    if s.chamber_cooling == "ablative":
        consumption_rate_m_s = (s.chamber_material.ablative_consumption_rate_m_s
                                 or materials.ABLATIVE_CONSUMPTION_RATE_M_S)
        # Film overlay on an ablative (LMDE/AJ10-style injector film): char
        # recession taken as ~proportional to the local wall heat flux, so the
        # film's throat flux multiplier scales the rate (Tier 3 - direction
        # sound, magnitude unanchored). No chamber film -> x1.0, unchanged.
        consumption_rate_m_s *= float(s.film_phi[s._throat_idx])
        s.rated_burn_time_s = self.ablative_target_burn_time_s
        s.ablative_liner_thickness_m = mass_model.ablative_liner_thickness_m(
            consumption_rate_m_s, self.ablative_target_burn_time_s, materials.CHAR_DEPTH_SAFETY_FACTOR)
        s.ablative_liner_mass_kg = mass_model.constant_thickness_shell_mass_kg(
            s.body_xs, s.body_rs, s.ablative_liner_thickness_m, s.chamber_material.density_kg_m3)
        s.chamber_wall_mass_kg += s.ablative_liner_mass_kg  # existing hoop-stress mass
                                                             # (structure_stage.wall_structure)
                                                             # is now the OVERWRAP, not the liner
    else:
        # the WORST of the throat row and the full-length peak row (the throat
        # alone used to set it even when another station ran hotter - audit W7)
        _margin = min(s.margin["margin_ratio"], s.peak_wall_margin_ratio or float("inf"))
        margin_mult = _margin / materials.THIN_MARGIN_THRESHOLD
        margin_mult = max(RATED_TIME_MARGIN_MULT_MIN, min(RATED_TIME_MARGIN_MULT_MAX, margin_mult))
        s.rated_burn_time_s = BASE_RATED_BURN_TIME_S * margin_mult

    # Electric pump-fed: size the battery + motor for the whole burn and add
    # their mass. (cyc was built provisionally in the cycle branch; rebuild it
    # now with the real burn time.)
    battery_motor_mass_kg = 0.0
    if self.cycle == cycles.ELECTRIC_PUMP:
        s.cyc = electric_pump.electric_pump_result(
            s.mdot, self.mixture_ratio, self.chamber_pressure_pa, s.dp_fuel, s.dp_ox,
            s.rho_fuel, s.rho_ox, s.eta_pf, s.eta_po, self.pump_specific_power_w_kg, s.rated_burn_time_s)
        battery_motor_mass_kg = s.cyc["battery_mass_kg"] + s.cyc["motor_mass_kg"]
        _check(s.checklist, s.warnings, "turbopump", "Electric pump-fed hardware mass",
               battery_motor_mass_kg <= 0.6 * (s.chamber_wall_mass_kg + s.bell_wall_mass_kg
                                               + s.turbopump_mass_kg + 1e-6),
               f"Battery + motor ({battery_motor_mass_kg:.0f} kg) is a large fraction of the "
               f"engine dry mass - electric pump-fed only pays off at small scale / short "
               f"burn (battery mass scales with burn time). Real electric pump-fed engines "
               f"(Rutherford) are small and stage their batteries.",
               f"OK - battery {s.cyc['battery_mass_kg']:.0f} kg + motor {s.cyc['motor_mass_kg']:.0f} kg")
        if self.propellant_pair == "LOX/LH2":
            _check(s.checklist, s.warnings, "propellant/cycle", "Electric pump-fed with LH2",
                   False,
                   "LH2's very high pump head makes electric pump-fed impractical - the "
                   "real electric pump-fed engine (Rutherford) is kerolox. Treat this "
                   "combination as unflown.")

    # I3 - injector-plate mass (a real, previously-uncounted term - see
    # mass_model.injector_plate_mass_kg). Always on.
    s.injector_plate_mass_kg = mass_model.injector_plate_mass_kg(
        s.geo["chamber_dia_m"], self.chamber_pressure_pa)
    _face_area_m2 = np.pi * (s.geo["chamber_dia_m"] / 2.0) ** 2
    _elem_density = (s.injector_geometry["n_elements"] / _face_area_m2
                     if _face_area_m2 > 0 else 0.0)
    _check(s.checklist, s.warnings, "injector", "Injector element crowding",
           _elem_density <= mass_model.MAX_ELEMENT_DENSITY_PER_M2,
           f"~{_elem_density:,.0f} elements/m^2 on the injector face exceeds a buildable "
           f"~{mass_model.MAX_ELEMENT_DENSITY_PER_M2:,.0f}/m^2 (F-1 ~8000, SSME ~4000) - "
           f"the pattern is over-crowded; use larger orifices or a wider chamber.",
           f"OK - ~{_elem_density:,.0f} elements/m^2")

    # Zirconia-class radiative-nozzle-extension liner mass (0.0 when inactive -
    # see cooling_stage.thermal's s.liner/s.nozzle_liner_thickness_m_eff).
    s.nozzle_liner_mass_kg = (
        mass_model.constant_thickness_shell_mass_kg(
            s.ext_xs, s.ext_rs, s.nozzle_liner_thickness_m_eff, s.liner.density_kg_m3)
        if s.liner is not None and s.has_extension else 0.0)

    s.computed_dry_mass_kg = (s.chamber_wall_mass_kg + s.bell_wall_mass_kg + s.turbopump_mass_kg
                            + battery_motor_mass_kg + s.stability_aid_mass_kg
                            + s.injector_plate_mass_kg + s.jacket_structure_mass_kg
                            + s.manifold_mass_kg + s.jacket_manifold_mass_kg + s.plumbing_mass_kg
                            + s.hatband_mass_kg + s.te_hardware_mass_kg + s.nozzle_liner_mass_kg)

    _check(s.checklist, s.warnings, "manifold", "Manifold structural mass fraction",
           s.manifold_mass_kg <= manifold.MANIFOLD_MASS_DRY_FRACTION_WARN
                                * max(s.computed_dry_mass_kg, 1e-6),
           f"Manifold mass ({s.manifold_mass_kg:.0f} kg) is a large fraction of dry mass - "
           f"raise the feed-velocity target or lower chamber pressure to lighten it.",
           f"OK - {s.manifold_mass_kg:.0f} kg")

    _check(s.checklist, s.warnings, "manifold", "Jacket manifold structural mass fraction",
           s.jacket_manifold_mass_kg <= manifold.MANIFOLD_MASS_DRY_FRACTION_WARN
                                       * max(s.computed_dry_mass_kg, 1e-6),
           f"Jacket manifold mass ({s.jacket_manifold_mass_kg:.0f} kg) is a large fraction "
           f"of dry mass - raise the feed-velocity target or lower chamber pressure to "
           f"lighten it.",
           f"OK - {s.jacket_manifold_mass_kg:.0f} kg")

    if s.plumbing_results:
        _check(s.checklist, s.warnings, "plumbing", "Plumbing structural mass fraction",
               bool(s.plumbing_mass_kg <= manifold.MANIFOLD_MASS_DRY_FRACTION_WARN
                    * max(s.computed_dry_mass_kg, 1e-6)),
               f"Plumbing (feed pipes + flanges) mass ({s.plumbing_mass_kg:.0f} kg) is a large "
               f"fraction of dry mass - shorten the runs or drop flanges.",
               f"OK - {s.plumbing_mass_kg:.1f} kg over {s.plumbing_total_length_m:.2f} m")

    _check(s.checklist, s.warnings, "chamber geometry",
           "Combustion completeness vs. L*/atomization", s.completeness >= 0.95,
           f"Chamber residence time ({s.residence_time_s*1000:.2f} ms) is short relative to "
           f"what {self.propellant_pair} with {s.injector.display_name} typically needs "
           f"(~{s.required_time_s*1000:.2f} ms) - combustion doesn't fully complete before "
           f"the throat, derating c* efficiency by a factor of {s.completeness:.2f}. "
           f"Increase L* or use a finer-atomization injector (pintle/platelet).",
           f"OK - {s.completeness:.2f}x completeness")
    _check(s.checklist, s.warnings, "injector", "Injector stiffness at throttle floor",
           s.inj_ok is not False,
           f"Injector stiffness at the {self.throttle_floor*100:.0f}% throttle floor "
           f"is below {s.injector.display_name}'s ~{s.injector.min_stable_dp_ratio:.2f} "
           f"dP/Pc chug threshold - this design is not stable that deep.",
           "OK - stable at floor throttle" if s.inj_ok else
           "Not evaluated (no exact match in the throttle sweep grid)")
    _check(s.checklist, s.warnings, "injector", "Injector practical minimum throttle",
           self.throttle_floor >= s.injector.practical_min_throttle,
           f"{s.injector.display_name} doesn't typically demonstrate throttling down to "
           f"{self.throttle_floor*100:.0f}% in real engines (representative practical "
           f"minimum ~{s.injector.practical_min_throttle*100:.0f}%) - this is separate from "
           f"the dP/Pc stiffness check above: an injector can be hydraulically stable at a "
           f"flow it was never actually engineered to reach.")
    inj_suit_warning = injectors.suitability_warning(self.injector_type, self.propellant_pair)
    _check(s.checklist, s.warnings, "injector", "Injector type suitability for propellant pair",
           not inj_suit_warning, inj_suit_warning or "")
    ign_warning = ignition.plausibility_warning(self.ignition_system, self.propellant_pair)
    _check(s.checklist, s.warnings, "ignition", "Ignition system plausibility",
           not ign_warning, ign_warning or "")


def checks_and_result(self, s):
    """Remaining checklist rows and the result dict."""
    # Monopropellant/bipropellant cross-checks. A "catalyst bed" only makes sense for a
    # monopropellant (it's a decomposition element, not a two-stream injector) and vice
    # versa; a monopropellant thruster is pressure-fed in every real design (no real
    # engine pumps a single decomposing propellant through a gas-generator/staged/
    # expander turbopump cycle).
    is_mono = combustion.is_monopropellant(self.propellant_pair)
    if is_mono and self.injector_type != "catalyst_bed":
        mono_injector_mismatch_detail = (
            f"{s.injector.display_name} is a bipropellant injector type; "
            f"{self.propellant_pair} is a monopropellant - a catalyst bed is "
            f"the real analog.")
    elif not is_mono and self.injector_type == "catalyst_bed":
        mono_injector_mismatch_detail = (
            f"Catalyst-bed decomposition doesn't apply to a bipropellant "
            f"combustion chamber ({self.propellant_pair}).")
    else:
        mono_injector_mismatch_detail = ""
    # if/elif above are mutually exclusive by construction (at most one can ever
    # fire) - merged into one checklist entry rather than two so the checklist
    # doesn't show a row that's trivially "passed" for whichever branch didn't apply.
    _check(s.checklist, s.warnings, "injector", "Injector type matches mono/bipropellant class",
           not mono_injector_mismatch_detail, mono_injector_mismatch_detail)
    _check(s.checklist, s.warnings, "propellant/cycle", "Monopropellant requires pressure-fed cycle",
           not (is_mono and self.cycle != cycles.PRESSURE_FED),
           f"Monopropellant thrusters are pressure-fed in every real design - "
           f"{cycles.CYCLE_DISPLAY[self.cycle]} has no real analog here.")
    _check(s.checklist, s.warnings, "chamber geometry", "Contraction ratio within typical range",
           CONTRACTION_RATIO_TYPICAL[0] <= self.contraction_ratio <= CONTRACTION_RATIO_TYPICAL[1],
           f"Contraction ratio {self.contraction_ratio:.2f} is outside the typical "
           f"{CONTRACTION_RATIO_TYPICAL[0]}-{CONTRACTION_RATIO_TYPICAL[1]} range.")
    _check(s.checklist, s.warnings, "chamber geometry", "L* within typical range",
           LSTAR_TYPICAL_M[0] <= self.lstar_m <= LSTAR_TYPICAL_M[1],
           f"L* {self.lstar_m:.2f} m is outside the typical "
           f"{LSTAR_TYPICAL_M[0]}-{LSTAR_TYPICAL_M[1]} m range.")
    sl_separation_note = " sl Isp/thrust are nominal placeholders, not physical." if s.sl_isp_unphysical else ""
    _check(s.checklist, s.warnings, "nozzle/aero", "Sea-level nozzle flow attachment",
           not s.separated_100pct,
           f"Nozzle is separated at sea level even at 100% throttle "
           f"(Pe/Pa={s.pe_pa/PA_SEA_LEVEL:.3f}) - this is a vacuum/high-altitude "
           f"nozzle, not suited to a sea-level-igniting stage.{sl_separation_note}")
    _check(s.checklist, s.warnings, "nozzle/aero", "Expansion ratio validity",
           self.expansion_ratio > 1.0, "Expansion ratio must be > 1.")

    gimbal_warning = gimbal.plausibility_warning(self.gimbal_mode, self.gimbal_range_deg)
    gimbal_pass_detail = ("OK - inherits host part's gimbal" if self.gimbal_mode == "inherit" else
                           "OK - explicitly ungimballed" if self.gimbal_mode == "ungimballed" else
                           f"OK - {self.gimbal_range_deg:.1f} deg within typical band")
    _check(s.checklist, s.warnings, "gimbal", "Gimbal range plausibility",
           not gimbal_warning, gimbal_warning or "", gimbal_pass_detail)

    return {
        "inputs": dict(self.__dict__),
        "tc_k": s.tc, "gamma": s.gamma, "m_molar": s.m_molar, "eta_cstar": s.eta_cstar,
        "completeness_factor": s.completeness,
        "residence_time_s": s.residence_time_s, "required_time_s": s.required_time_s,
        "cstar_ms": s.cstar, "pe_pc": s.pe_pc, "pe_pa": s.pe_pa,
        # P1 re-anchor (2026-09-25): where the chamber state came from, the
        # ideal (shifting-equilibrium) c* / vacuum CF and the fitted nozzle
        # efficiency applied on top of the divergence score
        "performance_source": s.perf["source"], "gamma_chamber": s.gamma_chamber, "cstar_ideal_ms": s.perf["cstar_ideal_ms"],
        "cf_vac_ideal": s.cf_vac_ideal, "eta_cf": s.eta_cf,
        "nozzle_divergence_efficiency": s.lam,
        "nozzle_efficiency_vs_reference": s.lam_relative,
        "theta_n_deg": s.theta_n_deg, "theta_e_deg": s.theta_e_deg,
        "mdot_kgs": s.mdot_total,          # TOTAL engine flow (chamber + any GG/tap-off draw)
        "mdot_chamber_kgs": s.mdot,        # through the main-chamber throat
        "isp_vac_chamber_s": s.isp_vac_chamber, "isp_sl_chamber_s": s.isp_sl_chamber,
        "isp_vac_engine_s": s.isp_vac_eng, "isp_sl_engine_s": s.isp_sl_eng,
        "thrust_vac_n": s.thrust_vac, "thrust_sl_n": s.thrust_sl,
        "thrust_vac_floor_n": s.thrust_vac_floor,
        "separated_at_100pct_sl": s.separated_100pct,
        "cycle_result": s.cyc,
        "turbine_exhaust": getattr(s, "turbine_exhaust", None),   # open cycles only
        "geometry": s.geo,
        "profile_xs_m": s.xs, "profile_rs_m": s.rs, "profile_meta": s.profile_meta,
        "throttle_sweep": s.rows,
        "separation_onset_throttle": s.onset,
        "injector_stiffness_ok_at_floor": s.inj_ok,
        "material_margin": s.margin,
        "bell_material_margin": s.bell_material_margin,
        "nozzle_liner_gas_face_temp_k": s.nozzle_liner_gas_face_temp_k,
        "chamber_heat_flux_factor": s.chamber_heat_flux_factor,
        "t_local_at_transition_k": s.t_local,
        "eps_for_transition": s.eps_for_transition,
        "cooling": s.cooling_result,
        "injector_geometry": s.injector_geometry,
        "chamber_acoustics": s.chamber_acoustics,
        "stability": s.stability_result,
        "stability_aid_mass_kg": s.stability_aid_mass_kg,
        "injector_dp_pa": s.dp_injector,
        "injector_dp_nominal_pa": s.dp_injector_nominal,
        "injector_dp_derived_pa": s.dp_injector_derived,
        "injector_dp_fuel_pa": s.dp_injector_fuel,
        "injector_dp_ox_pa": s.dp_injector_ox,
        "orifice_cd": s.orifice_cd,
        "chamber_flow": s.chamber_flow,
        "pc_feed_pa": s.pc_feed,
        "stay_time_s": s.stay_time_s,
        "chamber_l_over_d": s.chamber_l_over_d,
        "convergent_half_angle_deg": s.conv_half_angle,
        "injector_plate_mass_kg": s.injector_plate_mass_kg,
        "manifold_result": s.manifold_result,
        "manifold_mass_kg": s.manifold_mass_kg,
        "jacket_manifold_result": s.jacket_manifold_result,
        "jacket_manifold_mass_kg": s.jacket_manifold_mass_kg,
        "plumbing_results": s.plumbing_results,
        "turbopump_ports": s.turbopump_ports,
        "turbine_exhaust_hardware": s.te_hardware,
        "turbine_exhaust_hardware_mass_kg": s.te_hardware_mass_kg,
        "line_loss_fuel_pa": s.line_loss_fuel_pa,
        "line_loss_ox_pa": s.line_loss_ox_pa,
        "line_loss_source": {"fuel": "computed" if s._llo.get("fuel") is not None else "flat",
                             "ox": "computed" if s._llo.get("ox") is not None else "flat"},
        "line_loss_computed": s.line_loss_computed,
        "line_loss_residual_pa": 0.0,
        "plumbing_mass_kg": s.plumbing_mass_kg,
        "plumbing_total_length_m": s.plumbing_total_length_m,
        "cooling_flow_topology": self.cooling_flow_topology,
        # Stream inlet temperatures (flow visualization only - see the tables).
        "coolant_inlet_t_k": COOLANT_INLET_TEMP_K.get(self.propellant_pair, 290.0),
        "oxidizer_inlet_t_k": OXIDIZER_INLET_TEMP_K.get(self.propellant_pair),
        "jacket_inlet_eps_effective": s.jacket_inlet_eps_eff,
        "jacket_return_split_fraction": s.jacket_return_split_fraction,
        "manifold_bypass_fraction": self.manifold_bypass_fraction,
        "turbopump_sizing": s.tp_sizing,
        "chamber_wall_mass_kg": s.chamber_wall_mass_kg,
        "bell_wall_mass_kg": s.bell_wall_mass_kg,
        "body_wall_thickness_m": s.body_wall_thickness_m,
        "ext_wall_thickness_m": s.ext_wall_thickness_m,
        "jacket_structure_mass_kg": s.jacket_structure_mass_kg,
        "hatband_mass_kg": s.hatband_mass_kg,
        "jacket_overpressure_ok": s.jacket_overpressure_ok,
        "jacket_worst_station_eps": s.jacket_worst_station_eps,
        "jacket_pressure_at_worst_station_pa": s.jacket_pressure_at_worst_station_pa,
        "jacket_local_gas_pressure_at_worst_station_pa": s.jacket_local_gas_pressure_at_worst_station_pa,
        "jacket_overpressure_worst_station": s.jacket_overpressure_worst_station,
        "jacket_combined_stress_pa": s.jacket_combined_stress_pa,
        "jacket_hoop_stress_pa": s.jacket_hoop_stress_pa,
        "jacket_thermal_stress_pa": s.jacket_thermal_stress_pa,
        "computed_dry_mass_kg": s.computed_dry_mass_kg,
        "rated_burn_time_s": s.rated_burn_time_s,
        "ablative_liner_thickness_m": s.ablative_liner_thickness_m,
        "ablative_liner_mass_kg": s.ablative_liner_mass_kg,
        "nozzle_liner_mass_kg": s.nozzle_liner_mass_kg,
        "warnings": s.warnings,
        "checklist": s.checklist,
    }
