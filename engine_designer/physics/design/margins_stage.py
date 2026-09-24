"""Thermal-margin stage of _compute_pass (throat + full-length wall).

2026-09-23 cooling audit: both rows read the SAME unified per-station thermal
solve (cooling_stage.thermal): the throat row is that solve at the throat
station, the peak row its hottest station relative to each section's material
limit - so they can no longer disagree about one station, and the throat row is
no longer the circular T_aw(1-0.75*cal) inversion (W1). Both rows use
materials.THIN_MARGIN_THRESHOLD. A value shared between stages lives on the
PassState `s` (see design/state.py)."""
import numpy as np

from .. import (cooling, geometry, manifold, materials)
from .constants import PEAK_WALL_THROAT_ZONE_EPS
from .checklist import _check


def thermal_margins(self, s):
    """Chamber material thermal margin (throat) + full-length peak wall."""
    th = s.thermal
    ti = s._throat_idx
    s.chamber_heat_flux_factor = materials.contraction_ratio_heat_flux_factor(self.contraction_ratio)
    treat_t = th["treatment"][ti]
    march = th["march"]
    s.h_g_throat_effective_w_m2k = float(th["h_g_w_m2k"][ti])
    s.q_throat_wall_balance_w_m2 = float(th["q_w_m2"][ti])     # == q_throat_w_m2 (one flux)
    _twc = th["t_wc_k"][ti]
    s.t_wc_throat_coupled_k = float(_twc) if np.isfinite(_twc) else None
    s.coolant_velocity_throat_ms = (march["v_throat_ms"]
                                    if (march is not None and treat_t == cooling.REGEN) else None)
    # ablative -> proxy path (erodes rather than melts); every other treatment
    # has a solved wall temperature.
    s.t_wg_throat_k = None if treat_t == cooling.ABLATIVE else float(th["t_wg_k"][ti])

    s.margin = materials.thermal_margin(self.material_key, s.tc,
                                      heat_flux_factor=s.chamber_heat_flux_factor,
                                      wall_temp_k=s.t_wg_throat_k)
    _deposit = cooling.GAS_SIDE_DEPOSIT_FACTOR.get(self.propellant_pair, 1.0)
    _deposit_txt = " incl. carbon-deposit credit" if _deposit < 1.0 else ""
    if treat_t == cooling.REGEN:
        _margin_basis = (
            f"coupled throat wall balance: gas h_g ~{s.h_g_throat_effective_w_m2k/1e3:.1f} "
            f"kW/m2K{_deposit_txt}, T_aw ~{s.t_aw_throat_k:.0f} K, coolant "
            f"~{(s.coolant_velocity_throat_ms or 0.0):.0f} m/s (coolant-side wall "
            f"~{s.t_wc_throat_coupled_k:.0f} K), {s.hot_wall_thickness_m*1e3:.2f} mm wall")
        _margin_fail = ((s.margin["warning"] or "") + f" Basis: {_margin_basis}. Levers "
                        f"that lower it: faster coolant (Coolant velocity; SP-8087 caps "
                        f"liquids at ~61 m/s, at a jacket-dP cost), a thinner wall, a "
                        f"liner rated hotter or more conductive (e.g. GRCop-84), or more "
                        f"film cooling.")
    elif treat_t == cooling.RADIATIVE:
        _margin_basis = (f"radiation-equilibrium throat wall ~{s.t_wg_throat_k:.0f} K "
                         f"(h_g ~{s.h_g_throat_effective_w_m2k/1e3:.1f} kW/m2K, T_aw "
                         f"~{s.t_aw_throat_k:.0f} K, no coolant)")
        _margin_fail = ((s.margin["warning"] or "") + f" Basis: {_margin_basis}. An uncooled/"
                        f"radiative throat needs a refractory liner, heavy film cooling or "
                        f"a regen jacket.")
    else:
        _margin_basis = f"proxy (ablative), CR heat-flux factor {s.chamber_heat_flux_factor:.2f}x"
        _margin_fail = s.margin["warning"] or ""
    if s.chamber_cooling != s.chamber_material.cooling_method:
        _margin_basis += (f"; explicit {s.chamber_cooling} cooling on a "
                          f"{s.chamber_material.cooling_method}-spec liner")
    _check(s.checklist, s.warnings, "materials", "Chamber material thermal margin",
           not s.margin["warning"], _margin_fail,
           f"OK - {s.margin['margin_ratio']:.2f}x margin ({_margin_basis})")

    # Full-length wall: the same solve at EVERY non-ablative station, ranked by
    # how close each runs to ITS section's material limit.
    nozzle = s.station_section == "nozzle"
    limit = np.where(nozzle, s.bell_material.max_service_temp_k,
                     s.chamber_material.max_service_temp_k)
    s.t_wg_profile_k = np.where(th["ablative_mask"], np.nan, th["t_wg_k"])
    s.peak_wall_temp_k = None
    s.peak_wall_temp_zone = None
    s.peak_wall_temp_eps = None
    s.peak_wall_margin_ratio = None
    if np.any(np.isfinite(s.t_wg_profile_k)):
        _ratio = np.where(np.isfinite(s.t_wg_profile_k), s.t_wg_profile_k / limit, -np.inf)
        _ip = int(np.argmax(_ratio))
        s.peak_wall_temp_k = float(s.t_wg_profile_k[_ip])
        s.peak_wall_temp_eps = float(s.eps_st[_ip])
        s.peak_wall_margin_ratio = float(limit[_ip]) / s.peak_wall_temp_k
        _rs_a = np.asarray(s.rs, dtype=float)
        _barrel_end = int(np.flatnonzero(
            np.isclose(_rs_a, _rs_a[0], rtol=1e-6) & (np.arange(len(s.rs)) <= ti)).max())
        if abs(_ip - ti) <= 1 or (_ip > ti and s.peak_wall_temp_eps <= PEAK_WALL_THROAT_ZONE_EPS):
            s.peak_wall_temp_zone = "throat"
        elif _ip <= _barrel_end:
            s.peak_wall_temp_zone = "chamber barrel"
        elif _ip < ti:
            s.peak_wall_temp_zone = "convergent section"
        else:
            s.peak_wall_temp_zone = "nozzle"
    _check(s.checklist, s.warnings, "cooling", "Peak wall temperature along the wall",
           s.peak_wall_margin_ratio is None or s.peak_wall_margin_ratio >= materials.THIN_MARGIN_THRESHOLD,
           (f"Hottest wall station is in the {s.peak_wall_temp_zone} (area ratio "
            f"~{s.peak_wall_temp_eps:.1f}, {th['treatment'][_ip]}): wall ~{s.peak_wall_temp_k:.0f} K, "
            f"{s.peak_wall_margin_ratio:.2f}x that section's material limit (warns below "
            f"{materials.THIN_MARGIN_THRESHOLD:.2f}x, like the throat row). Levers: more chamber "
            f"film (or a convergent film ring for the throat region), faster coolant, a thinner "
            f"or more conductive liner, or extend active cooling."
            if s.peak_wall_margin_ratio is not None else ""),
           (f"OK - hottest station ~{s.peak_wall_temp_k:.0f} K in the {s.peak_wall_temp_zone} "
            f"({s.peak_wall_margin_ratio:.2f}x margin)"
            if s.peak_wall_margin_ratio is not None
            else "n/a - fully ablative"))
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
    _jbody_xs, _jbody_rs, _, _, _ = geometry.split_profile_by_area_ratio(
        s.xs, s.rs, s.geo["throat_dia_m"], s.cooled_length_eps)
    s.x_jacket_end_m = float(_jbody_xs[-1])
    s.local_bore_dia_m = 2.0 * float(_jbody_rs[-1])
    s.x_jacket_inlet_forward_m = (s.manifold_result["ox"]["attach_axial_station_m"]
                                 + s.manifold_result["ox"]["outer_radius_m"]
                                 + manifold.MANIFOLD_AXIAL_RING_GAP_M)
