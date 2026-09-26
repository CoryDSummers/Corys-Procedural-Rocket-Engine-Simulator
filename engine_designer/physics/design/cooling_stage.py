"""Cooling stages of _compute_pass.

2026-09-23 cooling audit: every cooling number now comes from ONE unified
per-station thermal solve (physics/cooling/thermal_solve.py), run on the REAL
contour BEFORE the pump chain (`thermal`), so the jacket dP the pumps are sized
for, the coolant rise, the wall temperatures the margins / fatigue / GUI read,
the expander's turbine heat and the regen Isp credit are all the same numbers.
The later stages only report from it. A value shared between stages lives on the
PassState `s` (see design/state.py)."""
import numpy as np

from .. import cooling, manifold, mass_model, materials, isentropic as iso
from ..cooling.coolant_state import CP_FALLBACK_J_KGK
from .constants import (
    G0,
    JACKET_DP_PA,
    JACKET_DP_FRACTION_BY_COOLING_METHOD,
    FILM_TOTAL_FRACTION_WARN,
    COOLANT_INLET_TEMP_K,
    REGEN_HOT_WALL_THICKNESS_M,
    FATIGUE_CYCLE_MARGIN,
    FATIGUE_CYCLE_FLOOR,
)
from .checklist import _check

# Outer passes of the thermal stage when the tube-wall thickness (sized off the
# jacket pressure + throat flux) or the dump bleed (subtracted from the jacket
# flow) feed back into the solve. Two corrections converge these to well under
# a kelvin; the inner solve itself iterates to cooling.thermal_solve tol_k.
THERMAL_OUTER_PASSES = 3
# Manufacturable floor for a milled-channel / coax hot-gas liner: [Fagherazzi-2019]
# fixes the liner at a practical 0.5 mm (process capability; the structurally
# required 0.05-0.6 mm is thinner). Tube walls keep their own cited 0.20 mm gauge
# (mass_model.TUBE_WALL_MIN_THICKNESS_M, Huzel's A-2 tube).
MILLED_CHANNEL_MIN_HOT_WALL_M = 0.5e-3


def _eps_stations(s):
    return (np.asarray(s.rs, dtype=float) / (s.geo["throat_dia_m"] / 2.0)) ** 2


def _turbine_exhaust_gas_film(self, s, carry):
    """nozzle_injection's gas film (physics/turbine_exhaust.
    gas_film_effectiveness_profile, [TN-D3836]) from the previous pass's
    carry: h_g on the thermal solve's own basis (calibrated Bartz x the
    deposit factor, no sigma), the main-gas velocity at the slot station
    (isentropic, supersonic branch), the slot's gas state. Returns (phi, info)
    or (None, None) when the slot lies past the contour."""
    from .. import turbine_exhaust, plumbing
    if not carry.get("slot_area_m2"):
        return None, None
    hg = cooling.bartz_hg_profile(
        s.xs, s.rs, s.geo["throat_dia_m"], self.chamber_pressure_pa, s.cstar, s.mu_gas,
        s.cp_gas, s.pr_gas, pair=self.propellant_pair) \
        * cooling.GAS_SIDE_DEPOSIT_FACTOR.get(self.propellant_pair, 1.0)
    g = s.gamma_ht
    mach = iso.mach_from_area_ratio(float(carry["inject_eps"]), g)
    t_static = s.tc_ht * iso.static_temperature_ratio(mach, g)
    v_gas = mach * np.sqrt(g * s.cp_gas * (g - 1.0) / g * t_static)
    rho_c = float(carry["slot_density_kg_m3"])
    alpha_c = plumbing.EXHAUST_GAS_VISCOSITY_PA_S / (rho_c * turbine_exhaust.EXHAUST_GAS_PRANDTL)
    prof = turbine_exhaust.gas_film_effectiveness_profile(
        s.xs, s.rs, s.geo["throat_dia_m"], float(carry["inject_eps"]), hg,
        float(carry["mdot_kgs"]), float(carry["cp"]), float(carry["slot_area_m2"]), v_gas, alpha_c)
    if prof is None:
        return None, None
    info = dict(slot_h_m=prof["slot_h_m"], slot_area_m2=float(carry["slot_area_m2"]),
                v_gas_ms=float(v_gas), v_coolant_ms=float(carry["slot_velocity_ms"]),
                velocity_ratio_c_over_g=float(carry["slot_velocity_ms"]) / float(v_gas),
                eta_exit=float(prof["eta"][-1]), x_over_s_exit=float(prof["x_over_s"][-1]),
                i_slot=prof["i_slot"], i_valid_end=prof["i_valid_end"])
    return prof["phi"], info


def thermal(self, s):
    """Unified per-station thermal solve on the real contour (before the pump
    chain): wall temperatures, heat flux, coolant march, dump bleed, jacket dP."""
    s.eps_for_transition = min(self.cooling_transition_eps, self.expansion_ratio)
    s.mdot_fuel_kgs = s.mdot / (1.0 + self.mixture_ratio)
    s.mdot_ox_kgs = s.mdot - s.mdot_fuel_kgs
    s._throat_idx = int(np.argmin(s.rs))
    s.eps_st = _eps_stations(s)
    # Fuel under f1_split_reverse_flow's bypass never enters the jacket.
    _jacket_fuel = (s.mdot_fuel_kgs * (1.0 - self.manifold_bypass_fraction)
                    if self.cooling_flow_topology == "f1_split_reverse_flow"
                    else s.mdot_fuel_kgs)

    # Film overlay profiles (both sites); film enters the solve ONLY through
    # the lowered adiabatic-wall temperature.
    s.film_phi, s.chamber_film_phi, s.nozzle_film_phi = self._film_phi(s.xs, s.rs, s.geo["throat_dia_m"])
    s.nozzle_film_active = bool(np.any(s.nozzle_film_phi < 1.0))
    # Turbine-exhaust gas film (nozzle_injection mode): the GG/tap-off flow and
    # exhaust temperature only exist after the pump stage, so it arrives as the
    # previous pass's carry (EngineDesign.compute's second pass). None = off.
    s.gas_film_phi = s.gas_film_t_k = s.gas_film_info = None
    _carry = getattr(s, "te_film_carry", None)
    if _carry:
        s.gas_film_phi, s.gas_film_info = _turbine_exhaust_gas_film(self, s, _carry)
        s.gas_film_t_k = float(_carry["t_k"]) if s.gas_film_phi is not None else None

    treat, section, regen_cut, notes = cooling.station_treatments(
        s.rs, s.geo["throat_dia_m"], s.chamber_cooling, s.nozzle_cooling,
        s.eps_for_transition, s.cooled_length_eps)
    s.station_section = section
    s.regen_cut_eps = regen_cut
    nozzle = section == "nozzle"
    k_wall = np.where(nozzle, s.bell_material.thermal_conductivity_w_mk,
                      s.chamber_material.thermal_conductivity_w_mk)
    emis = np.where(nozzle, s.bell_material.emissivity, s.chamber_material.emissivity)
    t_surf = np.where(nozzle, s.bell_material.max_service_temp_k,
                      s.chamber_material.max_service_temp_k)

    # Zirconia-class radiative-nozzle-extension liner (real physics, 2026-09-25):
    # a conduction resistance between the hot gas and the bell MATERIAL, lowering
    # the temperature the structural shell actually sees (cooling/radiation.py's
    # liner_resistance_m2k_w) - see cooling.solve_thermal's t_shell_k output,
    # read by nozzle_extension_thermal()/margins_stage.py instead of the raw
    # gas-facing t_wg_k wherever a liner is active. "" / 0.0 thickness = no
    # liner, bit-identical (zero resistance everywhere).
    s.liner = (materials.LINER_MATERIALS.get(self.nozzle_liner_material_key)
              if self.nozzle_liner_material_key and self.nozzle_liner_thickness_m > 0.0
              else None)
    liner_active = s.liner is not None
    s.nozzle_liner_thickness_m_eff = self.nozzle_liner_thickness_m if liner_active else 0.0
    liner_resistance = (np.where(nozzle & (treat == cooling.RADIATIVE),
                                 s.nozzle_liner_thickness_m_eff / s.liner.thermal_conductivity_w_mk, 0.0)
                        if liner_active else np.zeros(len(s.rs)))
    s.coolant_inlet_k = COOLANT_INLET_TEMP_K.get(self.propellant_pair, 290.0)
    s.coolant_limit_k = cooling.coolant_limit_k(self.propellant_pair)
    regen_chamber = s.chamber_cooling in ("regenerative", "dump")

    # Representative hot-wall land: hoop-limited, capped at 1.5 mm (unchanged).
    throat_hoop_thickness_m = mass_model.wall_thickness_m(
        self.chamber_pressure_pa, s.geo["throat_dia_m"] / 2.0,
        s.chamber_material.allowable_stress_pa)
    s.throat_wall_thickness_m = min(throat_hoop_thickness_m, REGEN_HOT_WALL_THICKNESS_M)
    s.hot_wall_thickness_m = s.throat_wall_thickness_m
    s.hot_wall_sizing_limit = "hoop/cap"

    march_kw = dict(n_channels=self.regen_channel_count, aspect_ratio=self.regen_channel_aspect_ratio,
                    target_velocity_ms=self.regen_coolant_velocity_ms,
                    land_fraction=self.regen_channel_land_fraction,
                    construction=self.wall_construction, split_eps=s.split_eps_eff)
    sized = regen_chamber    # hot wall structurally sized for every regen construction
    jdp = JACKET_DP_PA
    dump_mdot = 0.0
    passes = THERMAL_OUTER_PASSES if (sized or s.nozzle_cooling == "dump") else 1
    for _ in range(passes):
        s.mdot_coolant_jacket_kgs = max(_jacket_fuel - dump_mdot, 0.0)
        # coolant properties at the mean jacket pressure (injector feed + half the jacket)
        p_cool = s.pc_feed + s.dp_injector_fuel + 0.5 * jdp
        s.coolant_p_pa = p_cool
        s.thermal = cooling.solve_thermal(
            xs_m=s.xs, rs_m=s.rs, throat_dia_m=s.geo["throat_dia_m"],
            pc_pa=self.chamber_pressure_pa, cstar_ms=s.cstar, t0_k=s.tc_ht, gamma=s.gamma_ht,
            cp_gas=s.cp_gas, mu_gas=s.mu_gas, pr_gas=s.pr_gas, pair=self.propellant_pair,
            treatment=treat, k_wall=k_wall, emissivity=emis,
            t_wall_m=np.full(len(s.rs), s.hot_wall_thickness_m), t_surface_k=t_surf,
            film_phi=s.film_phi, film_post_jacket=regen_chamber,
            gas_film_phi=s.gas_film_phi, gas_film_t_k=s.gas_film_t_k,
            coolant_inlet_k=s.coolant_inlet_k, coolant_p_pa=p_cool,
            regen_mdot_kgs=s.mdot_coolant_jacket_kgs if regen_chamber else 0.0,
            regen_cut_eps=regen_cut, two_pass=s.two_pass, inlet_eps=s.jacket_inlet_eps_eff,
            march_kw=march_kw, dump_fraction_fixed=self.dump_coolant_fraction,
            mdot_fuel_kgs=s.mdot_fuel_kgs, coolant_limit_k=s.coolant_limit_k,
            calibration=cooling.BARTZ_ABS_FLUX_CALIBRATION.get(self.propellant_pair, 1.0),
            deposit_factor=cooling.GAS_SIDE_DEPOSIT_FACTOR.get(self.propellant_pair, 1.0),
            liner_resistance_m2k_w=liner_resistance)
        march = s.thermal["march"]
        jdp = (march["jacket_dp_pa"] if (march is not None and self.regen_channel_model == "channels")
               else JACKET_DP_PA)
        dump_mdot = s.thermal["dump"]["mdot_kgs"]
        if sized and march is not None:
            # Hot-gas wall sized by the min-combined-stress criterion [Huzel eq
            # 4-27/4-28] at the throat (net coolant-vs-Pc differential at the
            # topology's throat jacket pressure, this solve's throat flux for
            # the thermal term) for EVERY construction - previously only tube
            # walls were sized and milled channels got a flat 1.5 mm, a real
            # inconsistency that put ~1800 K across an Inconel channel wall
            # (2026-09-23 audit). Span radius per construction:
            #   tube_wall      : tube radius              floor 0.20 mm [Huzel A-2 tube]
            #   milled_channel : half the channel width   floor 0.5 mm  [Fagherazzi-2019]
            #   coax_shell     : the full shell radius    floor 0.5 mm  [Huzel eq 4-31]
            _j_in = s.pc_feed + s.dp_injector_fuel + jdp
            _split = ((march.get("jacket_dp_down_pa") or 0.0) / jdp
                      if s.two_pass and jdp > 0 else
                      (manifold.JACKET_RETURN_SPLIT_FRACTION
                       if self.cooling_flow_topology == "f1_split_reverse_flow" else 0.0))
            _jp_throat = _j_in - jdp * _split
            _n_throat = cooling.channel_count_at_station(march["n_channels"], 1.0, s.split_eps_eff)
            _g_t = cooling.channel_hydraulic_geometry(
                s.geo["throat_dia_m"], _n_throat, march["channel_height_m"],
                (self.regen_channel_land_fraction if self.regen_channel_land_fraction > 0
                 else cooling.CHANNEL_LAND_FRACTION_DEFAULT))
            if self.wall_construction == "tube_wall":
                _r_span, _t_floor = _g_t["dh_m"] / 2.0, mass_model.TUBE_WALL_MIN_THICKNESS_M
            elif self.wall_construction == "coax_shell":
                _r_span, _t_floor = s.geo["throat_dia_m"] / 2.0, MILLED_CHANNEL_MIN_HOT_WALL_M
            else:
                _r_span, _t_floor = _g_t["width_m"] / 2.0, MILLED_CHANNEL_MIN_HOT_WALL_M
            _q_t = float(s.thermal["q_w_m2"][s._throat_idx])
            _k_mat = s.chamber_material.thermal_conductivity_w_mk
            _k_per_m = (mass_model.thermal_stress_pa(_q_t / _k_mat, s.chamber_material.youngs_modulus_pa,
                                                     s.chamber_material.cte_per_k,
                                                     nu=mass_model.POISSON_RATIO)
                        if _k_mat > 0 else 0.0)
            s.hot_wall_thickness_m, s.hot_wall_sizing_limit = mass_model.regen_hot_wall_thickness_m(
                _jp_throat - self.chamber_pressure_pa, _r_span, _k_per_m,
                s.chamber_material.allowable_stress_pa, _t_floor, REGEN_HOT_WALL_THICKNESS_M)

    # Jacket dP the pump chain sees: the real-contour march ("channels") or the
    # legacy flat constant ("flat" now only means a flat DP - the thermal side
    # is always solved), scaled by the chamber method (dump chamber 0.2x;
    # ablative / radiative / uncooled 0). A nozzle dump bleed is a PARALLEL
    # branch off the pump discharge exhausting to the nozzle - its own dP
    # (reported) never governs the pump over the injector path.
    s.jacket_dp_pa = (jdp * JACKET_DP_FRACTION_BY_COOLING_METHOD.get(s.chamber_cooling, 1.0)
                      if regen_chamber else 0.0)

    _check(s.checklist, s.warnings, "cooling", "Coolant property data for the jacket",
           (not regen_chamber) or s.thermal["coolant_has_data"],
           f"No coolant property data for {self.propellant_pair}'s fuel - the regen jacket "
           f"is solved with generic kerosene-like fallback properties "
           f"(cp {CP_FALLBACK_J_KGK:.0f} J/kg-K); treat its coolant rise, wall temperatures and jacket dP as rough.",
           (f"OK - {s.thermal['coolant_source']}" if regen_chamber else "n/a - no regen jacket"))
    _check(s.checklist, s.warnings, "cooling", "Actively-cooled nozzle has a coolant path",
           "uncooled_active_nozzle" not in notes,
           f"The nozzle is set to '{s.nozzle_cooling}' but part of it has no coolant: "
           f"active cooling past the material transition (eps {s.eps_for_transition:.1f}) only "
           f"reaches regen_nozzle_end_eps ({self.regen_nozzle_end_eps:.1f}), and a regen "
           f"nozzle also needs a regen/dump chamber jacket to feed it. Those stations are "
           f"solved as UNCOOLED (radiation equilibrium) - set regen_nozzle_end_eps to the "
           f"exit for a full-length jacket.",
           "OK")
    _check(s.checklist, s.warnings, "cooling", "Thermal solve converged",
           s.thermal["converged"],
           f"The per-station wall-temperature solve did not converge in "
           f"{s.thermal['iterations']} iterations - cooling numbers are approximate.",
           f"OK - {s.thermal['iterations']} iterations")


def thermal_reporting(self, s):
    """Derive the reported / downstream cooling quantities from the thermal solve."""
    th = s.thermal
    ti = s._throat_idx
    s.q_profile_w_m2 = th["q_w_m2"]
    s.film_flux_factor = cooling.area_weighted_mean(
        s.xs, s.rs, s.film_phi, throat_dia_m=s.geo["throat_dia_m"],
        transition_area_ratio=s.cooled_length_eps)
    s.q_throat_w_m2 = float(s.q_profile_w_m2[ti])          # AT the throat station
    s.q_chamber_avg_w_m2 = cooling.area_weighted_mean(
        s.xs, s.rs, s.q_profile_w_m2, throat_dia_m=s.geo["throat_dia_m"],
        transition_area_ratio=s.cooled_length_eps)
    # Reported comparison ONLY: the pre-Phase-7 flat, propellant-agnostic anchor.
    s.q_chamber_avg_anchor_w_m2 = (
        cooling.reference_area_avg_flux_w_m2(self.chamber_pressure_pa) * s.film_flux_factor)
    s.q_throat_abs_w_m2 = s.q_throat_w_m2
    s.q_chamber_avg_abs_w_m2 = s.q_chamber_avg_w_m2
    s.hg_throat_w_m2k = float(th["h_g_w_m2k"][ti])
    s.wall_heat_w = th["wall_heat_regen_w"] + th["dump"]["heat_w"]
    march = th["march"]
    s.coolant_delta_t_k = march["coolant_delta_t_k"] if march is not None else 0.0
    s._t_film_k = th["t_film_k"]
    s.t_aw_film_profile_k = th["t_aw_film_k"]
    s.t_aw_throat_k = float(s.t_aw_film_profile_k[ti])
    s.t_wg_gas_side_k = float(th["t_wg_k"][ti])            # legacy name: the solved throat T_wg

    # Coolant-channel march is exposed for reporting / 3D ribs in "channels"
    # mode only (the "flat" model keeps its legacy flat jacket dP and no
    # channel readout, but its wall temperatures come from the same solve).
    s.coolant_march = march if self.regen_channel_model == "channels" else None
    s.channel_geometry = None
    if s.coolant_march is not None:
        s._n_ch_visual = s.coolant_march["n_channels"]
        s._land_fraction_visual = (self.regen_channel_land_fraction
                                   if self.regen_channel_land_fraction > 0
                                   else cooling.CHANNEL_LAND_FRACTION_DEFAULT)
        s._channel_height_visual = s.coolant_march["channel_height_m"]
        s.channel_geometry = cooling.channel_geometry_profile(
            s.xs, s.rs, s._n_ch_visual, s._channel_height_visual, s._land_fraction_visual,
            throat_dia_m=s.geo["throat_dia_m"], split_eps=s.split_eps_eff)

    # Through-wall conduction across the hot-wall land at the throat: exactly
    # T_wg - T_wc of the solve where a coolant exists, else q t / k.
    _twc = th["t_wc_k"][ti]
    s.through_wall_delta_t_k = (float(th["t_wg_k"][ti] - _twc) if np.isfinite(_twc)
                                else materials.through_wall_delta_t_k(
                                    s.q_throat_w_m2, s.hot_wall_thickness_m,
                                    s.chamber_material.thermal_conductivity_w_mk))


def nozzle_extension_thermal(self, s):
    """Nozzle-extension material margin from the solved extension stations."""
    mach_transition = iso.mach_from_area_ratio(s.eps_for_transition, s.gamma)
    s.t_local = s.tc * iso.static_temperature_ratio(mach_transition, s.gamma)
    th = s.thermal
    ext = np.flatnonzero((s.station_section == "nozzle") & ~th["ablative_mask"])
    s.bell_wall_temp_k = None
    s.bell_wall_temp_eps = None
    s.nozzle_liner_gas_face_temp_k = None
    if ext.size:
        # Ranked by t_shell_k - the STRUCTURAL shell's own temperature, what the
        # bell material's margin check actually needs (bit-identical to t_wg_k
        # wherever no liner is active, since t_shell_k == t_wg_k there).
        worst = int(ext[np.argmax(th["t_shell_k"][ext])])
        s.bell_wall_temp_k = float(th["t_shell_k"][worst])
        s.bell_wall_temp_eps = float(s.eps_st[worst])
        if s.liner is not None and th["treatment"][worst] == cooling.RADIATIVE:
            s.nozzle_liner_gas_face_temp_k = float(th["t_wg_k"][worst])
    s.bell_material_margin = materials.thermal_margin(
        self.bell_material_key, s.t_local, wall_temp_k=s.bell_wall_temp_k)
    if s.bell_wall_temp_k is not None:
        _kind = {cooling.REGEN: "regen-cooled", cooling.DUMP: "dump-cooled",
                 cooling.RADIATIVE: "radiation equilibrium"}.get(
            th["treatment"][worst], th["treatment"][worst])
        _liner_note = (f", {s.liner.display_name} liner (gas face "
                       f"~{s.nozzle_liner_gas_face_temp_k:.0f} K)"
                       if s.nozzle_liner_gas_face_temp_k is not None else "")
        _bell_basis = (f"hottest extension station eps {s.bell_wall_temp_eps:.1f}, {_kind} "
                       f"~{s.bell_wall_temp_k:.0f} K{_liner_note}")
    else:
        _bell_basis = f"ablative, local gas T {s.t_local:.0f} K"
    _check(s.checklist, s.warnings, "materials", "Nozzle-extension material thermal margin",
           not s.bell_material_margin["warning"],
           f"[nozzle extension] {s.bell_material_margin['warning']} ({_bell_basis})",
           f"OK - {s.bell_material_margin['margin_ratio']:.2f}x margin ({_bell_basis})")

    # Liner's OWN survival (warn-only, separate from the shell's margin check
    # above): the gas/liner-facing face runs HOTTER than the protected shell.
    if s.nozzle_liner_gas_face_temp_k is not None:
        _liner_ok = s.nozzle_liner_gas_face_temp_k <= s.liner.max_service_temp_k
        _check(s.checklist, s.warnings, "materials", "Nozzle-extension liner thermal margin",
               _liner_ok,
               f"[nozzle liner] {s.liner.display_name}: gas-facing temperature "
               f"{s.nozzle_liner_gas_face_temp_k:.0f} K EXCEEDS its "
               f"{s.liner.max_service_temp_k:.0f} K max service temp.",
               f"OK - {s.nozzle_liner_gas_face_temp_k:.0f} K vs "
               f"{s.liner.max_service_temp_k:.0f} K max")


def coolant_capacity_and_isp(self, s):
    """Coolant capacity, throat fatigue, regen Isp credit, dump cooling, nozzle-slot film."""
    th = s.thermal
    # Energy basis (2026-09-23 audit): [Sutton 8.2]'s "0.5-5 % of the total
    # energy generated reaches the walls" is measured against the chamber's
    # stagnation-enthalpy flow ~ mdot * cp * Tc (the energy an ideal infinite
    # expansion would turn into jet KE), not the old 0.5*mdot*c*^2 proxy - that
    # is ~5x smaller for LOX/LH2 (c*^2/2 ~ 2.6 vs cp Tc ~ 13.6 MJ/kg) and made
    # every hydrogen engine read 7-25 % and over-credited its regen Isp.
    jet_power_w = s.mdot * s.cp_gas * s.tc_ht
    s.wall_heat_energy_fraction = s.wall_heat_w / jet_power_w if jet_power_w > 0 else 0.0
    s.regen_cooled = s.chamber_cooling == "regenerative"
    s.regen_ok = (not s.regen_cooled) or cooling.regen_feasible(s.coolant_delta_t_k, self.propellant_pair)
    limit_txt = (f"~{s.coolant_limit_k:.0f} K" if s.coolant_limit_k is not None
                 else "the coking/boiling")
    regen_pass_detail = (f"OK - ~{s.coolant_delta_t_k:.0f} K coolant rise" if s.regen_cooled
                         else f"n/a - {s.chamber_cooling} cooling")
    _check(s.checklist, s.warnings, "cooling", "Regen jacket coolant capacity",
           s.regen_ok,
           f"Regen-jacket coolant temperature rise (~{s.coolant_delta_t_k:.0f} K) exceeds "
           f"{limit_txt} limit for {self.propellant_pair}: this chamber pressure/size drives "
           f"more heat into the wall than the fuel flow can carry away. Add film-cooling "
           f"assist, lower Pc, or move the cooling transition earlier.",
           regen_pass_detail)

    # Throat low-cycle thermal fatigue from the SOLVED throat through-wall
    # gradient (actively cooled metal walls only; warn-not-block).
    s.throat_thermal_stress_pa = mass_model.thermal_stress_pa(
        s.through_wall_delta_t_k, s.chamber_material.youngs_modulus_pa, s.chamber_material.cte_per_k)
    s.throat_fatigue_cycles = mass_model.low_cycle_fatigue_cycles(
        s.throat_thermal_stress_pa, s.chamber_material.youngs_modulus_pa)
    fatigue_threshold = max(self.ignitions * FATIGUE_CYCLE_MARGIN, FATIGUE_CYCLE_FLOOR)
    fatigue_relevant = s.chamber_cooling in ("regenerative", "dump")
    _check(s.checklist, s.warnings, "cooling", "Throat thermal-fatigue cycle life",
           (not fatigue_relevant) or s.throat_fatigue_cycles >= fatigue_threshold,
           f"Estimated throat low-cycle thermal-fatigue life ~{s.throat_fatigue_cycles:,.0f} "
           f"cycles (through-wall dT ~{s.through_wall_delta_t_k:.0f} K -> thermal stress "
           f"~{s.throat_thermal_stress_pa/1e6:.0f} MPa) is thin next to {self.ignitions} "
           f"planned ignition(s). A high-Pc regen throat is life-limited by cracking - "
           f"lower Pc, add film cooling, or a more fatigue-resistant liner.",
           (f"OK - ~{s.throat_fatigue_cycles:,.0f} thermal cycles" if fatigue_relevant
            else f"n/a - {s.chamber_cooling} cooling"))

    # Regenerative Isp credit [Sutton 8.2]: the jacket returns the wall heat to
    # the injector, so the CHAMBER stream keeps that energy. Isp ~ sqrt(energy)
    # -> credit ~ 0.5 x (regen heat / jet power), capped at REGEN_ISP_BONUS_MAX,
    # PUMP-FED regen chambers only (unchanged scope), and applied to the chamber
    # stream's share of the engine Isp only (a GG's dumped exhaust never saw it).
    s.regen_isp_bonus = (
        cooling.regen_isp_bonus_from_heat(th["wall_heat_regen_w"], jet_power_w)
        if s.regen_cooled and s.cyc["has_turbopump"] else 0.0)
    if s.regen_isp_bonus > 0.0:
        _chamber_share = s.mdot / s.mdot_total     # chamber stream's share of TOTAL flow
        s.isp_vac_eng += s.regen_isp_bonus * _chamber_share * s.isp_vac_chamber
        s.isp_sl_eng += s.regen_isp_bonus * _chamber_share * s.isp_sl_chamber
        s.thrust_vac = s.mdot_total * s.isp_vac_eng * G0
        s.thrust_sl = s.mdot_total * s.isp_sl_eng * G0
        s.thrust_vac_floor = s.thrust_vac * self.throttle_floor

    # Dump cooling (nozzle extension only): the bleed was sized INSIDE the
    # thermal solve against its own slice's heat (no longer double-charged to
    # the regen jacket, and subtracted from the jacket flow), ejected overboard
    # at a net Isp penalty.
    _d = th["dump"]
    s.dump_coolant_fraction_eff = _d["fraction"]
    s.dump_mdot_kgs = _d["mdot_kgs"]
    s.dump_coolant_dt_k = _d["delta_t_k"]
    s.dump_isp_penalty_fraction = (cooling.dump_cooling_isp_penalty_fraction(s.dump_mdot_kgs, s.mdot_total)
                                   if s.dump_mdot_kgs > 0 else 0.0)
    if s.dump_isp_penalty_fraction > 0.0:
        s.isp_vac_eng *= (1.0 - s.dump_isp_penalty_fraction)
        s.isp_sl_eng *= (1.0 - s.dump_isp_penalty_fraction)
        s.thrust_vac = s.mdot_total * s.isp_vac_eng * G0
        s.thrust_sl = s.mdot_total * s.isp_sl_eng * G0
        s.thrust_vac_floor = s.thrust_vac * self.throttle_floor
    _dump_limit = s.coolant_limit_k if s.coolant_limit_k else 200.0
    dump_ok = s.dump_coolant_dt_k <= _dump_limit + 1e-6
    _check(s.checklist, s.warnings, "cooling", "Dump-cooled nozzle coolant capacity",
           dump_ok,
           f"Dump-cooled nozzle coolant temperature rise (~{s.dump_coolant_dt_k:.0f} K) exceeds "
           f"the ~{_dump_limit:.0f} K coking/boiling limit for {self.propellant_pair}: raise "
           f"dump_coolant_fraction or shorten the dump-cooled slice (lower regen_nozzle_end_eps).",
           (f"OK - ~{s.dump_coolant_dt_k:.0f} K coolant rise, {s.dump_coolant_fraction_eff*100:.1f}% "
            f"of fuel, Isp penalty {s.dump_isp_penalty_fraction*100:.2f}%"
            if s.dump_mdot_kgs > 0 else "n/a - no dump-cooled nozzle slice"))

    # Nozzle-extension slot film: post-jacket fuel injected on the supersonic
    # wall never burns in the chamber, so - like dump flow - it is costed as a
    # low-velocity stream (DUMP_THRUST_RECOVERY_FRACTION of the core Isp), not
    # as a c* loss. The chamber curtain keeps its c* penalty (combustion stage).
    s.nozzle_film_isp_penalty_fraction = 0.0
    if s.nozzle_film_active:
        s.nozzle_film_isp_penalty_fraction = cooling.dump_cooling_isp_penalty_fraction(
            self.nozzle_film_fraction * s.mdot_fuel_kgs, s.mdot_total)
        s.isp_vac_eng *= (1.0 - s.nozzle_film_isp_penalty_fraction)
        s.isp_sl_eng *= (1.0 - s.nozzle_film_isp_penalty_fraction)
        s.thrust_vac = s.mdot_total * s.isp_vac_eng * G0
        s.thrust_sl = s.mdot_total * s.isp_sl_eng * G0
        s.thrust_vac_floor = s.thrust_vac * self.throttle_floor
    _slot_eps = self.nozzle_film_inject_eps
    _slot_ok = (self.nozzle_film_fraction <= 0.0 or s.nozzle_film_active)
    _check(s.checklist, s.warnings, "cooling", "Nozzle film slot on the nozzle wall",
           _slot_ok,
           f"Nozzle film slot at eps {_slot_eps:.1f} is not on the supersonic nozzle "
           f"(needs 1 < eps < {self.expansion_ratio:.1f}) - the "
           f"{self.nozzle_film_fraction*100:.1f}% slot film is ignored.",
           (f"OK - {self.nozzle_film_fraction*100:.1f}% of fuel as a slot film at eps "
            f"{_slot_eps:.1f}, Isp cost {s.nozzle_film_isp_penalty_fraction*100:.2f}%"
            if s.nozzle_film_active else "n/a - no nozzle slot film"))
    _film_total = max(0.0, self.film_cooling_fraction) + (
        max(0.0, self.nozzle_film_fraction) if s.nozzle_film_active else 0.0)
    _check(s.checklist, s.warnings, "cooling", "Total film-coolant fraction plausible",
           _film_total <= FILM_TOTAL_FRACTION_WARN,
           f"Total film coolant is {_film_total*100:.1f}% of the fuel flow (chamber curtain "
           f"+ nozzle slot) - above ~{FILM_TOTAL_FRACTION_WARN*100:.0f}% the c*/Isp cost "
           f"usually outweighs the cooling; real engines run ~2-12% (F-1 ~10-12%).",
           f"OK - {_film_total*100:.1f}% of fuel as film" if _film_total > 0.0
           else "n/a - no film cooling")
