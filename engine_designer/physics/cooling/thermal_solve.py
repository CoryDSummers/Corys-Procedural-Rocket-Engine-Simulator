"""Unified per-station thermal solve (2026-09-23 cooling audit).

ONE self-consistent answer for every station of the real contour, replacing
the old patchwork in which the flux profile assumed T_wg = 0.25*T_aw, the
"computed" throat wall temperature was that assumption inverted back out (the
circular W1 bug), film was applied twice (phi*q AND a lowered T_aw), the dump
slice's heat was charged to both the regen jacket and the dump bleed, and the
throat check, full-length check, fatigue and the GUI each read a different
flux / wall temperature.

Per station:
    h_g  = Bartz(station) * sigma(T_wg/T0, M) * calibration * deposit      [W/m2K]
    T_aw = T_s + r (T0 - T_s),  r = Pr^(1/3);  film lowers it:
           T_aw,f = T_aw - eta_f (T_aw - T_film),  eta_f = 1 - phi   (film enters ONLY here)
    q    = h_g (T_aw,f - T_wg)
and T_wg closes the balance according to the station's cooling:
    regen   : gas film -> wall (t/k) -> coolant film (h_c) -> bulk, on the
              enthalpy coolant march (real T-dependent properties) fed THIS q
    dump    : the same balance against a separate dump-coolant bleed that is
              auto-sized (or user-pinned) to hold its rise within the pair's limit
    radiative/uncooled : radiation equilibrium h_g (T_aw,f - T_wg) = e sigma T_wg^4
    ablative: surface held at the material's char/service temperature
Iterated (under-relaxed fixed point on T_wg; sigma, the march, the film
temperature and the dump flow all follow) to `tol_k`.
"""
from __future__ import annotations

import numpy as np

from .channels import FIN_CONSTRUCTIONS, rib_fin_factor
from .coolant_state import CoolantModel
from .dump import DUMP_COOLANT_FRACTION_MAX, DUMP_COOLANT_FRACTION_MIN
from .film import film_adiabatic_wall_temp
from .gas_side import (adiabatic_wall_temperature_profile, bartz_hg_raw_profile, bartz_sigma,
                       mach_profile, recovery_factor_from_prandtl)
from .march import march_coolant, march_coolant_two_pass
from .profile import _local_area_ratio, wall_heat_total_w
from .radiation import radiative_wall_temperature
from .wall import solve_wall_balance_profile

ACTIVE_METHODS = ("regenerative", "dump")
# per-station treatment labels
REGEN, DUMP, RADIATIVE, ABLATIVE = "regen", "dump", "radiative", "ablative"


def station_treatments(rs_m, throat_dia_m, chamber_method, nozzle_method,
                       eps_transition, cooled_length_eps):
    """(treatment per station, section per station, regen_cut_eps, notes).

    Chamber stations (subsonic + supersonic up to the material transition)
    follow the chamber method; nozzle stations follow the nozzle method, but an
    ACTIVE nozzle method only reaches `cooled_length_eps` (regen_nozzle_end_eps)
    - past it the bell has no coolant and is solved as uncooled (radiation
    equilibrium), with a note. A chamber 'dump' method is treated as a regen
    jacket (its coolant still flows through the chamber wall). A regen nozzle
    behind a non-jacketed chamber has no coolant source and runs uncooled."""
    rs = np.asarray(rs_m, dtype=float)
    rt = throat_dia_m / 2.0
    ti = int(np.argmin(rs))
    chamber_active = chamber_method in ACTIVE_METHODS
    treat, section, notes = [], [], []
    uncovered = False
    for i, r in enumerate(rs):
        eps = _local_area_ratio(r, rt)
        if i <= ti or eps <= eps_transition + 1e-9:
            section.append("chamber")
            treat.append(REGEN if chamber_active else
                         ABLATIVE if chamber_method == "ablative" else RADIATIVE)
            continue
        section.append("nozzle")
        if nozzle_method == "ablative":
            treat.append(ABLATIVE)
        elif nozzle_method in ACTIVE_METHODS and eps <= cooled_length_eps + 1e-9:
            if nozzle_method == "regenerative":
                treat.append(REGEN if chamber_active else RADIATIVE)
                if not chamber_active:
                    uncovered = True
            else:
                treat.append(DUMP)
        else:
            if nozzle_method in ACTIVE_METHODS:
                uncovered = True
            treat.append(RADIATIVE)
    if uncovered:
        notes.append("uncooled_active_nozzle")
    regen_cut = (cooled_length_eps if (chamber_active and nozzle_method == "regenerative")
                 else eps_transition)
    return np.array(treat), np.array(section), regen_cut, notes


def solve_thermal(*, xs_m, rs_m, throat_dia_m, pc_pa, cstar_ms, t0_k, gamma, cp_gas,
                  mu_gas, pr_gas, pair, treatment, k_wall, emissivity, t_wall_m, t_surface_k,
                  film_phi, film_post_jacket, coolant_inlet_k, coolant_p_pa,
                  regen_mdot_kgs=0.0, regen_cut_eps=None, two_pass=False, inlet_eps=None,
                  march_kw=None, dump_fraction_fixed=0.0, mdot_fuel_kgs=0.0,
                  coolant_limit_k=None, calibration=1.0, deposit_factor=1.0,
                  gas_film_phi=None, gas_film_t_k=None, liner_resistance_m2k_w=None,
                  max_iter=80, tol_k=0.5, relax=0.5):
    xs = np.asarray(xs_m, dtype=float)
    rs = np.asarray(rs_m, dtype=float)
    n = len(rs)
    treat = np.asarray(treatment)
    k_wall = np.asarray(k_wall, dtype=float)
    t_wall = np.asarray(t_wall_m, dtype=float)
    emis = np.asarray(emissivity, dtype=float)
    t_surf = np.asarray(t_surface_k, dtype=float)
    phi = np.asarray(film_phi, dtype=float)
    film_on = bool(np.any(phi < 1.0))
    # Optional THIRD film: a hot-GAS film at its own temperature (turbine
    # exhaust injected into the nozzle - physics/turbine_exhaust.py), applied
    # AFTER the liquid-fuel film(s): T_aw -> film(T_aw, phi_liq, T_fuel) ->
    # film(., phi_gas, T_gas). None/inactive -> the old path, bit-identical.
    gphi = None if gas_film_phi is None else np.asarray(gas_film_phi, dtype=float)
    gas_film_on = gphi is not None and gas_film_t_k is not None and bool(np.any(gphi < 1.0))
    liner_resist = (np.zeros(n) if liner_resistance_m2k_w is None
                    else np.asarray(liner_resistance_m2k_w, dtype=float))

    def _taw_film(t_film_liquid):
        base = film_adiabatic_wall_temp(t_aw, phi, t_film_liquid) if film_on else t_aw
        return film_adiabatic_wall_temp(base, gphi, float(gas_film_t_k)) if gas_film_on else base
    march_kw = dict(march_kw or {})
    construction = march_kw.get("construction", "milled_channel")

    mach = mach_profile(rs, throat_dia_m, gamma)
    r_rec = recovery_factor_from_prandtl(pr_gas)
    t_aw = adiabatic_wall_temperature_profile(t0_k, gamma, mach, r_rec)
    hg_raw = bartz_hg_raw_profile(xs, rs, throat_dia_m, pc_pa, cstar_ms, mu_gas, cp_gas, pr_gas)
    cal = calibration * deposit_factor
    coolant = CoolantModel(pair, coolant_p_pa)

    m_regen = treat == REGEN
    m_dump = treat == DUMP
    m_rad = treat == RADIATIVE
    m_abl = treat == ABLATIVE
    regen_on = bool(m_regen.any()) and regen_mdot_kgs > 0
    # dump slice = the contiguous DUMP stations plus the station just upstream
    dump_idx = np.flatnonzero(m_dump)
    dump_on = dump_idx.size > 0 and mdot_fuel_kgs > 0
    limit = coolant_limit_k if coolant_limit_k else 200.0

    twg = np.where(m_abl, t_surf, np.where(m_rad, 0.5 * t0_k, 0.3 * t0_k))
    twc = np.full(n, np.nan)
    t_film = float(coolant_inlet_k)
    march = None
    dump = dict(fraction=0.0, mdot_kgs=0.0, delta_t_k=0.0, heat_w=0.0, jacket_dp_pa=0.0,
                sized=False)
    converged = False
    it = 0
    for it in range(1, max_iter + 1):
        sigma = bartz_sigma(twg / t0_k, mach, gamma)
        hg = hg_raw * sigma * cal
        taw_f = _taw_film(t_film)
        q = np.maximum(hg * (taw_f - twg), 0.0)
        new = twg.copy()

        if regen_on:
            q_m = np.where(m_regen, q, 0.0)
            # Channels are sized at the coolant INLET density, i.e. the target
            # velocity fixes the jacket MASS FLUX (the constants were chosen
            # at liquid density: LH2 95 m/s x ~53-71 kg/m3 ~ 5000-6700
            # kg/m2s, the order of the SSME main chamber's real ~8700). The
            # local velocity then rises as the coolant heats (supercritical H2
            # expands ~10-20x) - real, and the reason H2 jackets run fast.
            kw = dict(march_kw, transition_area_ratio=regen_cut_eps, t_inlet_k=coolant_inlet_k,
                      coolant_model=coolant, t_wall_coolant_profile_k=twc)
            if two_pass:
                kw.pop("split_eps", None)
                march = march_coolant_two_pass(xs, rs, q_m, throat_dia_m, regen_mdot_kgs, pair,
                                               inlet_area_ratio=inlet_eps, **kw)
            else:
                march = march_coolant(xs, rs, q_m, throat_dia_m, regen_mdot_kgs, pair, **kw)
            _balance(new, twc, m_regen, hg, taw_f, _fin_hc(march, n, construction, k_wall),
                     march["t_bulk_profile_k"], t_wall, k_wall)
            if film_post_jacket:
                t_film = float(coolant_inlet_k + march["coolant_delta_t_k"])

        if dump_on:
            i0 = max(int(dump_idx[0]) - 1, 0)
            i1 = int(dump_idx[-1])
            sx, sr, sq = xs[i0:i1 + 1], rs[i0:i1 + 1], q[i0:i1 + 1]
            heat = wall_heat_total_w(sx, sr, sq)
            if dump_fraction_fixed > 0.0:
                frac = dump_fraction_fixed
            else:
                dh = coolant.heat_capacity_to(coolant_inlet_k, limit)
                need = heat / dh if dh > 0 else 0.0
                frac = min(max(need / mdot_fuel_kgs, DUMP_COOLANT_FRACTION_MIN),
                           DUMP_COOLANT_FRACTION_MAX)
            mdot_d = frac * mdot_fuel_kgs
            dkw = {k: v for k, v in march_kw.items() if k != "split_eps"}
            dmarch = march_coolant(sx, sr, sq, throat_dia_m, mdot_d, pair,
                                   t_inlet_k=coolant_inlet_k, coolant_model=coolant, **dkw)
            hc_full = _fin_hc(dmarch, n, construction, k_wall, i0=i0)
            tb_full = np.full(n, np.nan)
            tb_full[i0:i1 + 1] = dmarch["t_bulk_profile_k"]
            _balance(new, twc, m_dump, hg, taw_f, hc_full, tb_full, t_wall, k_wall)
            dump = dict(fraction=frac, mdot_kgs=mdot_d, delta_t_k=dmarch["coolant_delta_t_k"],
                        heat_w=heat, jacket_dp_pa=dmarch["jacket_dp_pa"],
                        sized=dump_fraction_fixed <= 0.0)

        for i in np.flatnonzero(m_rad):
            new[i] = radiative_wall_temperature(hg[i], taw_f[i], emis[i],
                                                liner_resistance_m2k_w=liner_resist[i])
        new[m_abl] = t_surf[m_abl]

        delta = float(np.nanmax(np.abs(new - twg))) if n else 0.0
        twg = twg + relax * (new - twg)
        if delta < tol_k:
            converged = True
            break

    # final consistent evaluation at the converged wall temperature
    sigma = bartz_sigma(twg / t0_k, mach, gamma)
    hg = hg_raw * sigma * cal
    taw_f = _taw_film(t_film)
    q = np.maximum(hg * (taw_f - twg), 0.0)
    heat_regen = (wall_heat_total_w(xs, rs, np.where(m_regen, q, 0.0), throat_dia_m=throat_dia_m,
                                    transition_area_ratio=regen_cut_eps) if regen_on else 0.0)
    # STRUCTURAL SHELL temperature behind a radiative liner (see radiation.
    # radiative_wall_temperature's docstring): t_wg_k above stays the true
    # gas/liner-facing temperature (bit-identical everywhere liner_resist==0,
    # in particular at every non-radiative station and every radiative one
    # with no liner active), while t_shell_k is what the bell MATERIAL
    # actually sees - exact algebra at the converged fixed point, no second
    # bisection.
    t_shell_k = twg - q * liner_resist
    return dict(mach=mach, recovery_factor=r_rec, t_aw_k=t_aw, t_aw_film_k=np.asarray(taw_f, float),
                sigma=sigma, h_g_w_m2k=hg, q_w_m2=q, t_wg_k=twg, t_wc_k=twc, t_shell_k=t_shell_k,
                treatment=treat, regen_mask=m_regen, dump_mask=m_dump, radiative_mask=m_rad,
                ablative_mask=m_abl, march=march, dump=dump, wall_heat_regen_w=heat_regen,
                t_film_k=t_film, iterations=it, converged=converged,
                coolant_source=coolant.source, coolant_has_data=coolant.has_data,
                coolant_model=coolant)


def _fin_hc(march, n, construction, k_wall, i0=0):
    """March h_c profile x the rib/fin factor (hot-wall-area basis), padded to n
    stations starting at station i0."""
    hc = np.full(n, np.nan)
    m = len(march["h_c_profile_w_m2k"])
    hc[i0:i0 + m] = march["h_c_profile_w_m2k"]
    if construction not in FIN_CONSTRUCTIONS:
        return hc
    w = np.full(n, np.nan)
    p = np.full(n, np.nan)
    w[i0:i0 + m] = march["channel_width_profile_m"]
    p[i0:i0 + m] = march["channel_pitch_profile_m"]
    return hc * rib_fin_factor(hc, w, p, march["channel_height_m"], k_wall)


def _balance(out_twg, out_twc, mask, hg, taw_f, hc, tb, t_wall, k_wall):
    """Coupled wall balance on the masked stations (grouped by wall thickness and
    conductivity, which solve_wall_balance_profile takes as scalars); stations
    with no coolant state keep their previous T_wg. `hc` is already on the
    hot-wall-area basis (fin-corrected)."""
    hc = np.asarray(hc, dtype=float)
    tb = np.asarray(tb, dtype=float)
    ok = mask & np.isfinite(hc) & np.isfinite(tb) & (hc > 0)
    if not ok.any():
        return
    for tw, kw in {(float(t_wall[i]), float(k_wall[i])) for i in np.flatnonzero(ok)}:
        sel = ok & (t_wall == tw) & (k_wall == kw)
        t_wg, t_wc, _ = solve_wall_balance_profile(hg[sel], np.asarray(taw_f)[sel], hc[sel],
                                                   tb[sel], tw, kw)
        out_twg[sel] = t_wg
        out_twc[sel] = t_wc
