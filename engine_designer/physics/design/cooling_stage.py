"""Cooling stages of _compute_pass: jacket pre-march, gas-side heat flux + coolant march, nozzle-extension thermal, coolant capacity / regen credit / dump / film.

Split verbatim out of the former single-file design.py; a value shared
between stages lives on the PassState `s` (see design/state.py)."""
import numpy as np

from .. import (cooling, geometry, mass_model, materials, isentropic as iso)
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


def jacket_premarch(self, s):
    """Regen-jacket pressure drop for the pump chain (flat constant or a pre-march)."""
    # Regen-jacket pressure drop. "flat" (default) uses the legacy constant so
    # nothing already validated moves. "channels" runs the coolant-channel
    # march here (on a cheap conical-profile approximation of the contour -
    # the divergent section past the throat contributes almost nothing to
    # jacket dP, and only eps <= cooling_transition_eps of it is cooled at
    # all) so the pump-feed chain below sees the real jacket dP. The
    # authoritative coolant-side wall temperature / coolant dT are re-marched
    # further down on the real (bell) contour with the film-cooling factor.
    s.coolant_march_pre = None
    if (self.regen_channel_model == "channels"
            and s.chamber_cooling == "regenerative"):
        _geo_pre = geometry.chamber_geometry(
            s.mdot, s.cstar, self.chamber_pressure_pa, self.expansion_ratio,
            self.lstar_m, self.contraction_ratio, self.convergent_half_angle_deg,
            self.chamber_wall_fillet_r_over_rt, self.chamber_sizing_method,
            s.chamber_sizing_rt_s, s.tc, s.m_molar)
        _xs_pre, _rs_pre, s._ = geometry.nozzle_profile(
            _geo_pre["chamber_dia_m"], _geo_pre["throat_dia_m"], _geo_pre["exit_dia_m"],
            _geo_pre["chamber_length_m"], self.convergent_half_angle_deg,
            self.nozzle_half_angle_deg, self.chamber_wall_fillet_r_over_rt)
        _film_phi_pre = self._film_phi(_xs_pre, _rs_pre, _geo_pre["throat_dia_m"])[0]
        _q_pre = cooling.absolute_heat_flux_profile(
            _xs_pre, _rs_pre, _geo_pre["throat_dia_m"], self.chamber_pressure_pa, s.cstar,
            s.mu_gas, s.cp_gas, s.pr_gas, s.t_aw_chamber_k, pair=self.propellant_pair,
            transition_area_ratio=s.cooled_length_eps) * _film_phi_pre
        # Bypass-aware down-leg flow, mirroring mdot_coolant_jacket_kgs
        # below (not yet defined at this point in compute() - mdot_fuel_kgs
        # itself doesn't exist yet either, hence the local recomputation).
        _mdot_fuel_pre = s.mdot / (1.0 + self.mixture_ratio)
        _mdot_coolant_pre = (_mdot_fuel_pre * (1.0 - self.manifold_bypass_fraction)
                              if self.cooling_flow_topology == "f1_split_reverse_flow"
                              else _mdot_fuel_pre)
        _pre_kw = dict(n_channels=self.regen_channel_count,
                       aspect_ratio=self.regen_channel_aspect_ratio,
                       target_velocity_ms=self.regen_coolant_velocity_ms,
                       land_fraction=self.regen_channel_land_fraction,
                       transition_area_ratio=s.cooled_length_eps,
                       t_inlet_k=COOLANT_INLET_TEMP_K.get(self.propellant_pair, 290.0),
                       construction=self.wall_construction)
        s.coolant_march_pre = cooling.march_coolant(
            _xs_pre, _rs_pre, _q_pre, _geo_pre["throat_dia_m"],
            _mdot_coolant_pre, self.propellant_pair, split_eps=s.split_eps_eff,
            **_pre_kw)
        if s.two_pass:
            # This cheap conical contour has ONE throat->exit segment, so
            # it resolves no mid-nozzle down pass at all. Keep its single-
            # pass dP as the baseline (what every validated pump-feed
            # number is pinned to) and ADD the two-pass increment, measured
            # on a finely resampled copy of the same cone - zero down-pass
            # length still reproduces the single-pass value exactly.
            _xs_f = np.linspace(float(_xs_pre[0]), float(_xs_pre[-1]), 241)
            _rs_f = np.interp(_xs_f, _xs_pre, _rs_pre)
            _q_f = cooling.absolute_heat_flux_profile(
                _xs_f, _rs_f, _geo_pre["throat_dia_m"], self.chamber_pressure_pa, s.cstar,
                s.mu_gas, s.cp_gas, s.pr_gas, s.t_aw_chamber_k, pair=self.propellant_pair,
                transition_area_ratio=s.cooled_length_eps) * self._film_phi(
                _xs_f, _rs_f, _geo_pre["throat_dia_m"])[0]
            _tp_f = cooling.march_coolant_two_pass(
                _xs_f, _rs_f, _q_f, _geo_pre["throat_dia_m"], _mdot_coolant_pre,
                self.propellant_pair, inlet_area_ratio=s.jacket_inlet_eps_eff, **_pre_kw)
            _sp_f = cooling.march_coolant(
                _xs_f, _rs_f, _q_f, _geo_pre["throat_dia_m"], _mdot_coolant_pre,
                self.propellant_pair, **_pre_kw)
            _base_dp = s.coolant_march_pre["jacket_dp_pa"]
            s.coolant_march_pre = dict(_tp_f)
            s.coolant_march_pre["jacket_dp_pa"] = (
                _base_dp + max(0.0, _tp_f["jacket_dp_pa"] - _sp_f["jacket_dp_pa"]))
        jacket_dp_base_pa = s.coolant_march_pre["jacket_dp_pa"]
    else:
        jacket_dp_base_pa = JACKET_DP_PA
    s.jacket_dp_pa = jacket_dp_base_pa * JACKET_DP_FRACTION_BY_COOLING_METHOD.get(
        s.chamber_cooling, 1.0)


def heat_flux_and_march(self, s):
    """Gas-side heat transfer (Bartz h_g, flux profile, film), coolant march on the real contour, through-wall conduction."""
    # --- gas-side heat transfer: real Bartz h_g -> computed wall temperature ---
    # A real Bartz gas-side coefficient (physics/cooling.py, fed by the
    # combustion-gas transport properties physics/combustion.py now derives)
    # gives the throat heat flux and a gas-side-only hot-wall temperature
    # from q = h_g*(T_aw - T_wg) [Huzel eq. 4-10/4-13]. How that becomes the
    # number the material thermal-margin check sees depends on the cooling
    # method:
    #   radiative  -> the wall really does run at the gas-side / radiation-
    #                 equilibrium temperature (no coolant loop).
    #   regen/dump -> the coolant PINS the wall down; it can't be hotter than
    #                 the gas-side-only value, and normally sits near the
    #                 max(cooling_effectiveness proxy, coolant-inlet + coolant
    #                 rise + through-wall conduction rise). This keeps the
    #                 proxy as a floor (no regression) while letting a genuinely
    #                 cool big/low-Pc wall earn margin and a low-conductivity
    #                 liner at high Pc lose it.
    #   ablative   -> keep the proxy (ablatives run hot by design and erode).
    s.eps_for_transition = min(self.cooling_transition_eps, self.expansion_ratio)
    s.mdot_fuel_kgs = s.mdot / (1.0 + self.mixture_ratio)
    s.mdot_ox_kgs = s.mdot - s.mdot_fuel_kgs
    # Flow actually passing through the regen jacket - under
    # f1_split_reverse_flow, manifold_bypass_fraction of the fuel goes
    # straight to the injector (never enters the jacket at all), matching
    # manifold.size_jacket_manifolds's own internal mdot_down formula
    # (duplicated here rather than imported, to avoid coupling into that
    # module's own concurrent development - see ASSUMPTIONS.md). All
    # OTHER mdot_fuel_kgs uses (injector geometry, manifold ring sizing,
    # dump cooling) correctly keep the FULL flow - all fuel reaches the
    # injector regardless of which path it took.
    s.mdot_coolant_jacket_kgs = (s.mdot_fuel_kgs * (1.0 - self.manifold_bypass_fraction)
                                if self.cooling_flow_topology == "f1_split_reverse_flow"
                                else s.mdot_fuel_kgs)

    # Computed-absolute Bartz flux profile (Phase 7) - AUTHORITATIVE. Real
    # per-station Bartz h_g (fed real combustion-gas transport properties),
    # calibrated per propellant class against real engines
    # (cooling.BARTZ_ABS_FLUX_CALIBRATION) rather than shape-normalised to
    # the old flat, propellant-agnostic area-average anchor - see that
    # constant's module comment for the LOX/RP-1-vs-LOX/LH2 finding that
    # drove the per-class (not flat) calibration.
    s.q_profile_w_m2 = cooling.absolute_heat_flux_profile(
        s.xs, s.rs, s.geo["throat_dia_m"], self.chamber_pressure_pa, s.cstar,
        s.mu_gas, s.cp_gas, s.pr_gas, s.t_aw_chamber_k, pair=self.propellant_pair,
        transition_area_ratio=s.cooled_length_eps)
    # Fuel-film cooling: a length-decaying curtain multiplier on the gas-side
    # flux (physics/cooling.film_effectiveness_profile) - strongest near the
    # injector face, recovering toward 1.0 down the nozzle - times the
    # optional nozzle-extension slot film (nozzle_film_effectiveness_profile).
    # An OVERLAY on every section method: the SAME film-reduced q profile feeds
    # the regen march, the dump sizing and the wall checks, so regen + film
    # genuinely interact. film_flux_factor is its cooled-zone area-average,
    # kept for the schematic / readout.
    s.film_phi, s.chamber_film_phi, s.nozzle_film_phi = self._film_phi(s.xs, s.rs, s.geo["throat_dia_m"])
    s.nozzle_film_active = bool(np.any(s.nozzle_film_phi < 1.0))
    s.q_profile_w_m2 = s.q_profile_w_m2 * s.film_phi
    s.film_flux_factor = cooling.area_weighted_mean(
        s.xs, s.rs, s.film_phi, throat_dia_m=s.geo["throat_dia_m"],
        transition_area_ratio=s.cooled_length_eps)
    s.q_throat_w_m2 = float(np.max(s.q_profile_w_m2))
    s.q_chamber_avg_w_m2 = cooling.area_weighted_mean(
        s.xs, s.rs, s.q_profile_w_m2, throat_dia_m=s.geo["throat_dia_m"],
        transition_area_ratio=s.cooled_length_eps)

    # Reported comparison ONLY: the pre-Phase-7 flat, propellant-agnostic
    # area-average anchor. Nothing downstream uses this any more.
    s.q_chamber_avg_anchor_w_m2 = (
        cooling.reference_area_avg_flux_w_m2(self.chamber_pressure_pa) * s.film_flux_factor)
    s.q_throat_abs_w_m2 = s.q_throat_w_m2                    # kept as an alias - same value now
    s.q_chamber_avg_abs_w_m2 = s.q_chamber_avg_w_m2          # kept as an alias - same value now

    s.hg_throat_w_m2k = cooling.bartz_hg(
        s.geo["throat_dia_m"], self.chamber_pressure_pa, s.cstar,
        s.mu_gas, s.cp_gas, s.pr_gas, area_ratio=1.0)
    # A film curtain lowers the EFFECTIVE adiabatic-wall (driving) temperature
    # the throat sees, not just the flux: T_aw,film = T_aw - eta_f*(T_aw - T_film),
    # with eta_f = 1 - film_phi at the throat and the film fuel entering near
    # its jacket-inlet temperature. Without this the mechanical q = h_g*(T_aw -
    # T_wg) inversion would read a HOTTER wall from a lower film-reduced flux.
    s._throat_idx = int(np.argmin(s.rs))

    s.wall_heat_w = cooling.wall_heat_total_w(
        s.xs, s.rs, s.q_profile_w_m2, throat_dia_m=s.geo["throat_dia_m"],
        transition_area_ratio=s.cooled_length_eps)
    s.cp_fuel = cooling.FUEL_CP_J_KGK.get(self.propellant_pair)
    s.coolant_delta_t_k = cooling.coolant_temp_rise_k(s.wall_heat_w, s.mdot_coolant_jacket_kgs, s.cp_fuel)
    s.coolant_limit_k = cooling.coolant_limit_k(self.propellant_pair)
    s.coolant_inlet_k = COOLANT_INLET_TEMP_K.get(self.propellant_pair, 290.0)

    # Film fuel is tapped POST-JACKET (the F-1 curtain): with an active jacket
    # (regenerative / dump chamber) it enters at the jacket EXIT temperature -
    # the flat energy-balance estimate, since the flux profile (and so this
    # rise) doesn't depend on T_film; with no jacket it comes straight off the
    # fuel manifold at the inlet temperature. Per-station film T_aw feeds the
    # full-length wall balance; its throat value is the historical throat line.
    s._t_film_k = s.coolant_inlet_k + (
        s.coolant_delta_t_k if s.chamber_cooling in ("regenerative", "dump") else 0.0)
    s.t_aw_film_profile_k = (cooling.film_adiabatic_wall_temp(s.t_aw_chamber_k, s.film_phi, s._t_film_k)
                           if np.any(s.film_phi < 1.0)
                           else np.full(len(s.xs), float(s.t_aw_chamber_k)))
    s.t_aw_throat_k = float(s.t_aw_film_profile_k[s._throat_idx])
    s.t_wg_gas_side_k = cooling.wall_gas_temperature(s.q_throat_w_m2, s.hg_throat_w_m2k, s.t_aw_throat_k)

    # Coolant-channel march on the REAL contour + film factor (authoritative
    # for the coolant-side wall temp and coolant dT; the pump-feed chain
    # above already used the cheap early estimate). Regenerative "channels"
    # mode only - otherwise coolant_march stays None and the legacy proxy runs.
    s.coolant_march = None
    s.channel_geometry = None
    if (self.regen_channel_model == "channels"
            and s.chamber_cooling == "regenerative"):
        if s.two_pass:
            s.coolant_march = cooling.march_coolant_two_pass(
                s.xs, s.rs, s.q_profile_w_m2, s.geo["throat_dia_m"], s.mdot_coolant_jacket_kgs,
                self.propellant_pair, inlet_area_ratio=s.jacket_inlet_eps_eff,
                n_channels=self.regen_channel_count,
                aspect_ratio=self.regen_channel_aspect_ratio,
                target_velocity_ms=self.regen_coolant_velocity_ms,
                land_fraction=self.regen_channel_land_fraction,
                transition_area_ratio=s.cooled_length_eps, t_inlet_k=s.coolant_inlet_k,
                construction=self.wall_construction)
        else:
            s.coolant_march = cooling.march_coolant(
                s.xs, s.rs, s.q_profile_w_m2, s.geo["throat_dia_m"], s.mdot_coolant_jacket_kgs,
                self.propellant_pair, n_channels=self.regen_channel_count,
                aspect_ratio=self.regen_channel_aspect_ratio,
                target_velocity_ms=self.regen_coolant_velocity_ms,
                land_fraction=self.regen_channel_land_fraction,
                transition_area_ratio=s.cooled_length_eps, t_inlet_k=s.coolant_inlet_k,
                construction=self.wall_construction, split_eps=s.split_eps_eff)
        s.coolant_delta_t_k = s.coolant_march["coolant_delta_t_k"]
        # Per-station channel geometry across the WHOLE contour, for the 3D
        # preview's rib pattern only - re-derives n_channels/channel_height
        # the identical way march_coolant did internally (channel_count/
        # channel_target_height_m), then a separate additive function
        # (channel_geometry_profile) fans that out per station. Doesn't
        # feed any lumped number above; coolant_march's own outputs are
        # already final by this point.
        s._n_ch_visual = cooling.channel_count(s.geo["throat_dia_m"], self.regen_channel_count)
        s._land_fraction_visual = (self.regen_channel_land_fraction
                                 if self.regen_channel_land_fraction > 0
                                 else cooling.CHANNEL_LAND_FRACTION_DEFAULT)
        s._channel_height_visual, s._ = cooling.channel_target_height_m(
            s.geo["throat_dia_m"], s._n_ch_visual, s.mdot_coolant_jacket_kgs, self.propellant_pair,
            s._land_fraction_visual, aspect_ratio_override=self.regen_channel_aspect_ratio,
            target_velocity_ms=self.regen_coolant_velocity_ms)
        s.channel_geometry = cooling.channel_geometry_profile(
            s.xs, s.rs, s._n_ch_visual, s._channel_height_visual, s._land_fraction_visual,
            throat_dia_m=s.geo["throat_dia_m"], split_eps=s.split_eps_eff)

    # NOTE (2026-09-17): f1_split_reverse_flow's bypassed flow used to be
    # handled by a post-hoc rescale here (coolant_delta_t_k divided by
    # (1-bypass_fraction) after the fact). That's gone - mdot_coolant_jacket_kgs
    # (defined above, near mdot_fuel_kgs) now feeds the REAL reduced down-
    # leg flow directly into both the flat-mode proxy and the authoritative
    # march_coolant() call, so coolant_delta_t_k (and, new this round,
    # t_wc_throat_k/jacket_dp_pa/n_channels/channel_dh_throat_m - previously
    # untouched by the old rescale) all now correctly reflect the real
    # reduced flow from the source, not an approximation applied afterward.
    # Still a simplification, unchanged from before: this models the down-
    # leg and return-leg as one combined thermal unit sharing the same wall
    # heat-flux profile/channel geometry (one march_coolant() call, one
    # direction), not two independently-modeled interleaved streams - see
    # ASSUMPTIONS.md and regen_circuit_style's own TODO for that larger gap.

    # Through-wall conduction rise across a representative hot-wall land
    # (physics/materials.through_wall_delta_t_k - the first real use of a
    # material's thermal conductivity). Also feeds the fatigue check below.
    throat_hoop_thickness_m = mass_model.wall_thickness_m(
        self.chamber_pressure_pa, s.geo["throat_dia_m"] / 2.0,
        s.chamber_material.allowable_stress_pa)
    s.throat_wall_thickness_m = min(throat_hoop_thickness_m, REGEN_HOT_WALL_THICKNESS_M)
    s.through_wall_delta_t_k = materials.through_wall_delta_t_k(
        s.q_throat_w_m2, s.throat_wall_thickness_m, s.chamber_material.thermal_conductivity_w_mk)


def nozzle_extension_thermal(self, s):
    """Nozzle-extension material temperature at the cooling transition (radiative / film)."""
    # Nozzle-extension material at cooling_transition_eps. For a RADIATIVELY
    # cooled extension (no coolant loop) the real check is the radiation-
    # equilibrium wall temperature - h_gc*(T_aw - T_wg) balanced against
    # emissivity*sigma*T_wg^4 [Huzel eq. 4-38] - not just the local gas
    # temperature. An actively-cooled extension keeps the local-gas-static
    # basis (much cooler than Tc this far down the nozzle).
    mach_transition = iso.mach_from_area_ratio(s.eps_for_transition, s.gamma)
    s.t_local = s.tc * iso.static_temperature_ratio(mach_transition, s.gamma)
    s.bell_wall_temp_k = None
    s.bell_wall_temp_eps = None
    if s.nozzle_cooling in ("radiative", "uncooled"):
        t_aw_local_k = s.t_local + cooling.RECOVERY_FACTOR * (s.tc - s.t_local)
        hg_local_w_m2k = cooling.bartz_hg(
            s.geo["throat_dia_m"], self.chamber_pressure_pa, s.cstar,
            s.mu_gas, s.cp_gas, s.pr_gas, area_ratio=max(s.eps_for_transition, 1.0))
        s.bell_wall_temp_k = cooling.radiative_wall_temperature(
            hg_local_w_m2k, t_aw_local_k, s.bell_material.emissivity)
        s.bell_wall_temp_eps = s.eps_for_transition
        # Film overlay on a passive extension (the F-1 architecture): the film
        # lowers the local driving temperature, T_aw,film = T_aw - eta_f*(T_aw -
        # T_film) - the same T_aw-only convention as the coupled wall balance -
        # and it DECAYS downstream, so the hottest point can move off the
        # transition station. Evaluate every extension station and keep the
        # worst. No film anywhere on the extension -> the single-point check
        # above, unchanged.
        _rt_b = s.geo["throat_dia_m"] / 2.0
        _thr_b = int(np.argmin(s.rs))
        _eps_st = (np.asarray(s.rs) / _rt_b) ** 2
        _ext = [i for i in range(_thr_b + 1, len(s.rs)) if _eps_st[i] >= s.eps_for_transition]
        _ext_eps = np.concatenate([[s.eps_for_transition], _eps_st[_ext]])
        # each point takes its own station's film value; the transition point
        # takes the first extension station's (a slot AT the transition covers
        # it, one further downstream doesn't) - no interpolation across the slot
        _fp = np.asarray(s.film_phi)
        _ext_phi = (np.concatenate([[_fp[_ext[0]]], _fp[_ext]]) if _ext
                    else np.ones(1))
        if np.any(_ext_phi < 1.0):
            s.bell_wall_temp_k = None
            for _e, _ph in zip(_ext_eps, _ext_phi):
                _m = iso.mach_from_area_ratio(max(float(_e), 1.0 + 1e-9), s.gamma)
                _tl = s.tc * iso.static_temperature_ratio(_m, s.gamma)
                _taw = cooling.film_adiabatic_wall_temp(
                    _tl + cooling.RECOVERY_FACTOR * (s.tc - _tl), float(_ph), s._t_film_k)
                _hg = cooling.bartz_hg(s.geo["throat_dia_m"], self.chamber_pressure_pa, s.cstar,
                                       s.mu_gas, s.cp_gas, s.pr_gas, area_ratio=max(float(_e), 1.0))
                _tw = cooling.radiative_wall_temperature(_hg, _taw, s.bell_material.emissivity)
                if s.bell_wall_temp_k is None or _tw > s.bell_wall_temp_k:
                    s.bell_wall_temp_k, s.bell_wall_temp_eps = _tw, float(_e)
    s.bell_material_margin = materials.thermal_margin(
        self.bell_material_key, s.t_local, wall_temp_k=s.bell_wall_temp_k)
    _bell_basis = ((f"radiative equilibrium ~{s.bell_wall_temp_k:.0f} K"
                    + (f" (hottest extension station, eps {s.bell_wall_temp_eps:.1f}, "
                       f"with film)" if s.bell_wall_temp_eps != s.eps_for_transition else ""))
                   if s.bell_wall_temp_k is not None else f"local gas T {s.t_local:.0f} K")
    _check(s.checklist, s.warnings, "materials", "Nozzle-extension material thermal margin",
           not s.bell_material_margin["warning"],
           f"[nozzle extension] {s.bell_material_margin['warning']}",
           f"OK - {s.bell_material_margin['margin_ratio']:.2f}x margin ({_bell_basis})")


def coolant_capacity_and_isp(self, s):
    """Coolant capacity, throat fatigue, regen Isp credit, dump cooling, nozzle-slot film."""
    # --- coolant-side capacity, regen Isp credit, throat fatigue life ---
    # (wall_heat_w / coolant_delta_t_k / through_wall_delta_t_k were computed
    # above for the material thermal-margin check.)
    jet_power_w = 0.5 * s.mdot * s.cstar ** 2
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

    # Throat low-cycle thermal fatigue: the hot face runs hotter than the
    # coolant side by through_wall_delta_t_k (across a ~1 mm channel-wall
    # land, not the full hoop thickness); that gradient yields the wall every
    # firing and cracks it over enough start/stop cycles - the SSME throat
    # story. Only meaningful for an ACTIVELY cooled metal wall (a big
    # through-wall gradient held cycle after cycle); ablative liners char/
    # erode and radiative walls run near-isothermal, so the check is skipped
    # for those (the numbers are still reported). Warn-not-block.
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

    # Regenerative Isp credit [Sutton 8.2]: only for a PUMP-FED regen chamber
    # (a pressure-fed engine has no head budget for a full-flow jacket, and
    # the propellant-pair Isp spot checks all run pressure-fed - so those
    # stay bit-for-bit unchanged). Applied to the engine Isp after the cycle
    # branch, so mdot (from isp_vac_chamber) is untouched; thrust is bumped.
    s.regen_isp_bonus = (
        cooling.regen_isp_bonus_fraction(s.coolant_delta_t_k, self.propellant_pair)
        if s.regen_cooled and s.cyc["has_turbopump"] else 0.0)
    if s.regen_isp_bonus > 0.0:
        s.isp_vac_eng *= (1.0 + s.regen_isp_bonus)
        s.isp_sl_eng *= (1.0 + s.regen_isp_bonus)
        s.thrust_vac = s.mdot * s.isp_vac_eng * G0
        s.thrust_sl = s.mdot * s.isp_sl_eng * G0
        s.thrust_vac_floor = s.thrust_vac * self.throttle_floor

    # Dump cooling (nozzle extension only - real engines dump-cool skirts, not
    # main chambers): a small coolant bleed absorbs the nozzle-extension's
    # wall heat and is ejected overboard at the lip instead of returning to
    # the injector - Vulcain HM-60 / J-2 style. Sized (or user-pinned via
    # dump_coolant_fraction) to hold that slice's coolant dT within the pair's
    # coking/boiling limit, with a net Isp penalty for ejecting it at a lower
    # effective specific impulse than the core exhaust. No penalty (and no
    # cooled slice) unless regen_nozzle_end_eps has actually extended cooling
    # past the material transition - see that field's comment.
    s.dump_coolant_fraction_eff = 0.0
    s.dump_mdot_kgs = 0.0
    s.dump_coolant_dt_k = 0.0
    s.dump_isp_penalty_fraction = 0.0
    if s.nozzle_cooling == "dump" and s.cooled_length_eps > s.eps_for_transition:
        wall_heat_ext_w = max(0.0, s.wall_heat_w - cooling.wall_heat_total_w(
            s.xs, s.rs, s.q_profile_w_m2, throat_dia_m=s.geo["throat_dia_m"],
            transition_area_ratio=s.eps_for_transition))
        dump_limit_k = cooling.coolant_limit_k(self.propellant_pair) or 200.0
        s.dump_coolant_fraction_eff = (
            self.dump_coolant_fraction if self.dump_coolant_fraction > 0.0
            else cooling.size_dump_coolant_fraction(
                wall_heat_ext_w, s.mdot_fuel_kgs, s.cp_fuel, dump_limit_k))
        s.dump_mdot_kgs = s.dump_coolant_fraction_eff * s.mdot_fuel_kgs
        s.dump_coolant_dt_k = cooling.coolant_temp_rise_k(wall_heat_ext_w, s.dump_mdot_kgs, s.cp_fuel)
        s.dump_isp_penalty_fraction = cooling.dump_cooling_isp_penalty_fraction(s.dump_mdot_kgs, s.mdot)
    if s.dump_isp_penalty_fraction > 0.0:
        s.isp_vac_eng *= (1.0 - s.dump_isp_penalty_fraction)
        s.isp_sl_eng *= (1.0 - s.dump_isp_penalty_fraction)
        s.thrust_vac = s.mdot * s.isp_vac_eng * G0
        s.thrust_sl = s.mdot * s.isp_sl_eng * G0
        s.thrust_vac_floor = s.thrust_vac * self.throttle_floor
    dump_ok = (s.dump_coolant_dt_k <= 0.0
              or s.dump_coolant_dt_k <= (cooling.coolant_limit_k(self.propellant_pair) or 1e9))
    _check(s.checklist, s.warnings, "cooling", "Dump-cooled nozzle coolant capacity",
           dump_ok,
           f"Dump-cooled nozzle coolant temperature rise (~{s.dump_coolant_dt_k:.0f} K) exceeds "
           f"the coking/boiling limit for {self.propellant_pair}: raise dump_coolant_fraction "
           f"or shorten the dump-cooled slice (lower regen_nozzle_end_eps).",
           (f"OK - ~{s.dump_coolant_dt_k:.0f} K coolant rise, {s.dump_coolant_fraction_eff*100:.1f}% "
            f"of fuel, Isp penalty {s.dump_isp_penalty_fraction*100:.2f}%"
            if s.nozzle_cooling == "dump" and s.cooled_length_eps > s.eps_for_transition
            else "n/a - no dump-cooled nozzle slice"))

    # Nozzle-extension slot film: post-jacket fuel injected on the supersonic
    # wall never burns in the chamber, so - like dump flow - it is costed as a
    # low-velocity stream that recovers only DUMP_THRUST_RECOVERY_FRACTION of
    # the core Isp (the same physics as the F-1's turbine-exhaust film), not
    # as a c* loss. The chamber curtain keeps its c* penalty (it does burn,
    # off-mixture-ratio, inside the chamber - see eta_cstar above).
    s.nozzle_film_isp_penalty_fraction = 0.0
    if s.nozzle_film_active:
        s.nozzle_film_isp_penalty_fraction = cooling.dump_cooling_isp_penalty_fraction(
            self.nozzle_film_fraction * s.mdot_fuel_kgs, s.mdot)
        s.isp_vac_eng *= (1.0 - s.nozzle_film_isp_penalty_fraction)
        s.isp_sl_eng *= (1.0 - s.nozzle_film_isp_penalty_fraction)
        s.thrust_vac = s.mdot * s.isp_vac_eng * G0
        s.thrust_sl = s.mdot * s.isp_sl_eng * G0
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
