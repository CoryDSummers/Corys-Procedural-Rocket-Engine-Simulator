"""Thermal-margin stage of _compute_pass (throat + full-length wall balance).

Split verbatim out of the former single-file design.py; a value shared
between stages lives on the PassState `s` (see design/state.py)."""
import numpy as np

from .. import (cooling, geometry, manifold, mass_model, materials)
from .constants import (
    PEAK_WALL_THROAT_ZONE_EPS,
    REGEN_HOT_WALL_THICKNESS_M,
)
from .checklist import _check


def thermal_margins(self, s):
    """Chamber material thermal margin (throat) + full-length coupled wall balance."""
    # --- Chamber material thermal margin (throat hot-gas wall) ---
    # Sits here, below the jacket pressures, so the coupled solve can size
    # the tube wall it conducts through the same way the jacket-overpressure
    # check does. What the check compares depends on the cooling method:
    #   radiative  -> the gas-side / radiation-equilibrium temperature.
    #   regen, "channels" model (a real coolant march ran) -> COUPLED series-
    #                 resistance balance (cooling.solve_wall_balance): gas film
    #                 -> wall -> coolant film -> bulk coolant, all at the throat.
    #                 The wall temperature responds to coolant velocity (h_c),
    #                 wall thickness and conductivity. Gas side = raw Bartz h_g
    #                 x the per-class flux calibration x the carbon-deposit
    #                 credit (cooling.GAS_SIDE_DEPOSIT_FACTOR, RP-1 only).
    #   regen "flat" / dump -> legacy: the coolant pins the wall no
    #                 hotter than the gas-side value, floored by the
    #                 cooling_effectiveness proxy (unchanged, so every flat-mode
    #                 spot check stays bit-identical).
    #   ablative   -> proxy (ablatives run hot by design and erode).
    # The integrated flux profile, coolant dT and fatigue dT are NOT re-derived
    # from the coupled flux (documented Tier-3 inconsistency, ASSUMPTIONS.md).
    s.chamber_heat_flux_factor = materials.contraction_ratio_heat_flux_factor(self.contraction_ratio)
    cool_method = s.chamber_cooling
    s.hot_wall_thickness_m = s.throat_wall_thickness_m
    s.h_g_throat_effective_w_m2k = None
    s.t_wc_throat_coupled_k = None
    s.q_throat_wall_balance_w_m2 = None
    s.coolant_velocity_throat_ms = None
    if cool_method in ("radiative", "uncooled"):
        # No active coolant loop - the wall runs at the gas-side-only temp.
        s.t_wg_throat_k = s.t_wg_gas_side_k
    elif cool_method in ("regenerative", "dump") and s.coolant_march is not None:
        deposit_factor = cooling.GAS_SIDE_DEPOSIT_FACTOR.get(self.propellant_pair, 1.0)
        s.h_g_throat_effective_w_m2k = (
            s.hg_throat_w_m2k
            * cooling.BARTZ_ABS_FLUX_CALIBRATION.get(self.propellant_pair, 1.0)
            * deposit_factor)
        if self.wall_construction == "tube_wall":
            # Same min-combined-stress tube wall the jacket-overpressure check
            # sizes at the throat (tube radius, net coolant-vs-Pc differential
            # at the topology's jacket pressure) - a thinner tube runs cooler.
            _jp_throat_pa = (s.jacket_return_pressure_pa
                             if self.cooling_flow_topology in ("f1_split_reverse_flow",
                                                               "j2_mid_nozzle_inlet")
                             else s.jacket_inlet_pressure_pa)
            _r_tube_throat_m = cooling.channel_hydraulic_geometry(
                s.geo["throat_dia_m"],
                cooling.channel_count_at_station(s._n_ch_visual, 1.0, s.split_eps_eff),
                s._channel_height_visual, s._land_fraction_visual)["dh_m"] / 2.0
            _k_per_m = (mass_model.thermal_stress_pa(
                s.q_throat_w_m2 / s.chamber_material.thermal_conductivity_w_mk,
                s.chamber_material.youngs_modulus_pa, s.chamber_material.cte_per_k,
                nu=mass_model.POISSON_RATIO)
                if s.chamber_material.thermal_conductivity_w_mk > 0 else 0.0)
            s.hot_wall_thickness_m, s._ = mass_model.min_combined_stress_thickness_m(
                _jp_throat_pa - self.chamber_pressure_pa, _r_tube_throat_m, _k_per_m,
                mass_model.TUBE_WALL_MIN_THICKNESS_M, REGEN_HOT_WALL_THICKNESS_M)
        s.t_wg_throat_k, s.t_wc_throat_coupled_k, s.q_throat_wall_balance_w_m2 = (
            cooling.solve_wall_balance(
                s.h_g_throat_effective_w_m2k, s.t_aw_throat_k,
                s.coolant_march["h_c_throat_w_m2k"], s.coolant_march["t_bulk_throat_k"],
                s.hot_wall_thickness_m, s.chamber_material.thermal_conductivity_w_mk))
        s.coolant_velocity_throat_ms = s.coolant_march["v_throat_ms"]
    elif cool_method in ("regenerative", "dump"):
        proxy_k = s.tc * s.chamber_material.cooling_effectiveness * s.chamber_heat_flux_factor
        coolant_side_k = s.coolant_inlet_k + s.coolant_delta_t_k + s.through_wall_delta_t_k
        s.t_wg_throat_k = min(s.t_wg_gas_side_k, max(proxy_k, coolant_side_k))
    else:  # ablative - proxy path (fallback), erodes rather than melts
        s.t_wg_throat_k = None

    s.margin = materials.thermal_margin(self.material_key, s.tc,
                                      heat_flux_factor=s.chamber_heat_flux_factor,
                                      wall_temp_k=s.t_wg_throat_k)
    if s.h_g_throat_effective_w_m2k is not None:
        _deposit_txt = (" incl. carbon-deposit credit"
                        if cooling.GAS_SIDE_DEPOSIT_FACTOR.get(self.propellant_pair, 1.0) < 1.0
                        else "")
        _margin_basis = (
            f"coupled throat wall balance: gas h_g ~{s.h_g_throat_effective_w_m2k/1e3:.1f} "
            f"kW/m2K{_deposit_txt}, coolant ~{s.coolant_velocity_throat_ms:.0f} m/s "
            f"(h_c ~{s.coolant_march['h_c_throat_w_m2k']/1e3:.1f} kW/m2K, coolant-side wall "
            f"~{s.t_wc_throat_coupled_k:.0f} K), {s.hot_wall_thickness_m*1e3:.2f} mm wall")
        _margin_fail = ((s.margin["warning"] or "") + f" Basis: {_margin_basis}. Levers "
                        f"that lower it: faster coolant (Coolant velocity; SP-8087 caps "
                        f"liquids at ~61 m/s, at a jacket-dP cost), a thinner wall, a "
                        f"liner rated hotter or more conductive (e.g. GRCop-84), or more "
                        f"film cooling.")
    else:
        _margin_basis = (f"computed wall temp ~{s.t_wg_throat_k:.0f} K vs T_aw {s.t_aw_chamber_k:.0f} K"
                         if s.t_wg_throat_k is not None
                         else f"proxy (ablative), CR heat-flux factor {s.chamber_heat_flux_factor:.2f}x")
        _margin_fail = s.margin["warning"] or ""
    if s.chamber_cooling != s.chamber_material.cooling_method:
        _margin_basis += (f"; explicit {s.chamber_cooling} cooling on a "
                          f"{s.chamber_material.cooling_method}-spec liner")
    _check(s.checklist, s.warnings, "materials", "Chamber material thermal margin",
           not s.margin["warning"], _margin_fail,
           f"OK - {s.margin['margin_ratio']:.2f}x margin ({_margin_basis})")

    # Full-length coupled wall balance ("channels" regen only): the throat
    # series-resistance balance above, repeated at EVERY cooled station with
    # that station's calibrated Bartz h_g (x the same carbon-deposit credit),
    # its film-lowered T_aw (both film sites), and the march's local coolant
    # h_c / bulk temperature. This is where the chamber curtain's barrel
    # protection - and a convergent film ring's shift of it - actually shows.
    # Warn-only NEW row: the throat margin row above, the rated burn time and
    # the fatigue check stay throat-based (so every spot check is unchanged).
    # Tier 3: one wall thickness (the throat's) and single-phase coolant
    # everywhere; the march's flux is not re-derived from the coupled one.
    s.t_wg_profile_k = None
    s.peak_wall_temp_k = None
    s.peak_wall_temp_zone = None
    s.peak_wall_temp_eps = None
    s.peak_wall_margin_ratio = None
    if s.h_g_throat_effective_w_m2k is not None and "h_c_profile_w_m2k" in s.coolant_march:
        _hg_prof = cooling.bartz_hg_profile(
            s.xs, s.rs, s.geo["throat_dia_m"], self.chamber_pressure_pa, s.cstar, s.mu_gas, s.cp_gas,
            s.pr_gas, pair=self.propellant_pair) * cooling.GAS_SIDE_DEPOSIT_FACTOR.get(
                self.propellant_pair, 1.0)
        _rs_a = np.asarray(s.rs, dtype=float)
        _eps_prof = (_rs_a / (s.geo["throat_dia_m"] / 2.0)) ** 2
        _supersonic = np.arange(len(s.rs)) > s._throat_idx
        _is_bell = _supersonic & (_eps_prof > s.eps_for_transition)
        _k_prof = np.where(_is_bell, s.bell_material.thermal_conductivity_w_mk,
                           s.chamber_material.thermal_conductivity_w_mk)
        _limit_prof = np.where(_is_bell, s.bell_material.max_service_temp_k,
                               s.chamber_material.max_service_temp_k)
        s.t_wg_profile_k = np.full(len(s.rs), np.nan)
        for _kk in np.unique(_k_prof):          # solve_wall_balance_profile takes one k
            _sel = _k_prof == _kk
            s.t_wg_profile_k[_sel] = cooling.solve_wall_balance_profile(
                _hg_prof[_sel], s.t_aw_film_profile_k[_sel],
                s.coolant_march["h_c_profile_w_m2k"][_sel],
                s.coolant_march["t_bulk_profile_k"][_sel],
                s.hot_wall_thickness_m, float(_kk))[0]
        if np.any(np.isfinite(s.t_wg_profile_k)):
            # rank stations by how close each runs to ITS material's limit
            _ratio = np.where(np.isfinite(s.t_wg_profile_k),
                              s.t_wg_profile_k / _limit_prof, -np.inf)
            _ip = int(np.argmax(_ratio))
            s.peak_wall_temp_k = float(s.t_wg_profile_k[_ip])
            s.peak_wall_temp_eps = float(_eps_prof[_ip])
            s.peak_wall_margin_ratio = float(_limit_prof[_ip]) / s.peak_wall_temp_k
            _barrel_end = int(np.flatnonzero(
                np.isclose(_rs_a, _rs_a[0], rtol=1e-6)
                & (np.arange(len(s.rs)) <= s._throat_idx)).max())
            if abs(_ip - s._throat_idx) <= 1 or s.peak_wall_temp_eps <= PEAK_WALL_THROAT_ZONE_EPS:
                s.peak_wall_temp_zone = "throat"
            elif _ip <= _barrel_end:
                s.peak_wall_temp_zone = "chamber barrel"
            elif _ip < s._throat_idx:
                s.peak_wall_temp_zone = "convergent section"
            else:
                s.peak_wall_temp_zone = "nozzle"
    _check(s.checklist, s.warnings, "cooling", "Peak wall temperature along cooled length",
           s.peak_wall_margin_ratio is None or s.peak_wall_margin_ratio >= 1.0,
           (f"Hottest cooled-wall station is in the {s.peak_wall_temp_zone} (area ratio "
            f"~{s.peak_wall_temp_eps:.1f}): coupled wall balance ~{s.peak_wall_temp_k:.0f} K, "
            f"over that section's material limit ({s.peak_wall_margin_ratio:.2f}x). Levers: "
            f"more chamber film (or a convergent film ring for the throat region), faster "
            f"coolant, a thinner or more conductive liner."
            if s.peak_wall_margin_ratio is not None else ""),
           (f"OK - hottest station ~{s.peak_wall_temp_k:.0f} K in the {s.peak_wall_temp_zone} "
            f"({s.peak_wall_margin_ratio:.2f}x margin)"
            if s.peak_wall_margin_ratio is not None
            else "n/a - needs the 'channels' regen model"))
    if s.coolant_velocity_throat_ms is not None:
        _v_warn = manifold.velocity_cap_warning(s.coolant_velocity_throat_ms, "Throat coolant",
                                                supercritical=s._fuel_lh2)
        _check(s.checklist, s.warnings, "cooling", "Throat coolant velocity vs. SP-8087 limit",
               _v_warn is None,
               (f"Throat coolant-passage velocity ~{s.coolant_velocity_throat_ms:.0f} m/s "
                f"exceeds SP-8087's {manifold.LIQUID_VELOCITY_MAX_MS:.0f} m/s liquid-coolant "
                f"limit [SP-8087 Sec.3.1.1.5.3] - expect erosion and a steep jacket-dP / "
                f"pump-power cost. Lower Coolant velocity or add film cooling instead."),
               (f"OK - {s.coolant_velocity_throat_ms:.0f} m/s" if not s._fuel_lh2
                else f"n/a - supercritical LH2 ({s.coolant_velocity_throat_ms:.0f} m/s)"))
    _jbody_xs, _jbody_rs, s._, s._, s._ = geometry.split_profile_by_area_ratio(
        s.xs, s.rs, s.geo["throat_dia_m"], s.cooled_length_eps)
    s.x_jacket_end_m = float(_jbody_xs[-1])
    s.local_bore_dia_m = 2.0 * float(_jbody_rs[-1])
    s.x_jacket_inlet_forward_m = (s.manifold_result["ox"]["attach_axial_station_m"]
                                 + s.manifold_result["ox"]["outer_radius_m"]
                                 + manifold.MANIFOLD_AXIAL_RING_GAP_M)
