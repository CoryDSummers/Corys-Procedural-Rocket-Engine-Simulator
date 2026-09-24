"""Headless self-test for the cooling package: python3 -m engine_designer.physics.cooling"""
import math  # noqa: F401

import numpy as np

from engine_designer.physics.cooling import (  # noqa: F401
    CHANNEL_DP_CALIBRATION,
    CHANNEL_MIN_COUNT,
    DUMP_COOLANT_FRACTION_MAX,
    DUMP_COOLANT_FRACTION_MIN,
    DUMP_THRUST_RECOVERY_FRACTION,
    FILM_FLUX_FLOOR,
    FUEL_CP_J_KGK,
    J2_DOWN_TO_UP_TUBE_RATIO,
    REGEN_ISP_BONUS_MAX,
    REGEN_ISP_ENERGY_TO_ISP,
    CoolantModel,
    bartz_sigma,
    mach_profile,
    rib_fin_factor,
    solve_thermal,
    station_treatments,
    STEFAN_BOLTZMANN_W_M2K4,
    WALL_TEMP_FRACTION_DEFAULT,
    _frustum_area,
    absolute_heat_flux_profile,
    area_weighted_mean,
    bartz_hg,
    bartz_hg_profile,
    channel_count,
    channel_geometry_profile,
    channel_hydraulic_geometry,
    combined_film_phi,
    coolant_temp_rise_k,
    coupled_wall_temps,
    down_pass_velocity_ms,
    dump_cooling_isp_penalty_fraction,
    film_adiabatic_wall_temp,
    film_effectiveness_profile,
    heat_flux_profile,
    march_coolant,
    march_coolant_two_pass,
    nozzle_film_effectiveness_profile,
    passage_velocity_ms,
    radiative_wall_temperature,
    recovery_temperature,
    reference_area_avg_flux_w_m2,
    regen_feasible,
    regen_isp_bonus_from_heat,
    size_dump_coolant_fraction,
    solve_wall_balance,
    solve_wall_balance_profile,
    two_pass_tube_counts,
    wall_gas_temperature,
    wall_heat_total_w,
)

if __name__ == "__main__":
    # Headless unit smoke test - no matplotlib, no display.
    xs = np.array([0.0, 0.20, 0.32, 0.90])          # injector - chamber end - throat - exit
    rs = np.array([0.10, 0.10, 0.04, 0.15])
    dt_dia = 0.08

    q = heat_flux_profile(xs, rs, dt_dia, pc_pa=7.0e6)
    assert int(q.argmax()) == 2, f"peak flux should be at the throat, got index {q.argmax()}"
    assert q[0] < q[1], "injector-face taper should make x=0 the coolest chamber station"

    q_avg = reference_area_avg_flux_w_m2(7.0e6)
    total = wall_heat_total_w(xs, rs, q)
    assert total > 0.0
    dt = coolant_temp_rise_k(total, 20.0, FUEL_CP_J_KGK["LOX/RP-1"])
    assert dt > 0.0
    assert regen_feasible(50.0, "LOX/LH2") and not regen_feasible(600.0, "LOX/RP-1")

    # Anchor identity: mean flux over the cooled zone == the expander anchor.
    from_profile_mean = total / sum(
        _frustum_area(xs[i], rs[i], xs[i + 1], rs[i + 1]) for i in range(len(xs) - 1))
    assert abs(from_profile_mean - q_avg) / q_avg < 1e-6, (from_profile_mean, q_avg)

    # --- fuel-film curtain: length-decaying flux multiplier -------------------
    assert np.array_equal(film_effectiveness_profile(xs, rs, dt_dia, 0.0), np.ones(len(xs)))
    phi_lo = film_effectiveness_profile(xs, rs, dt_dia, 0.02)
    phi_hi = film_effectiveness_profile(xs, rs, dt_dia, 0.12)
    assert phi_hi[0] < phi_lo[0] < 1.0                    # more film -> more protection at the face
    assert (phi_hi[0] < phi_hi[-1] <= 1.0 + 1e-9)        # curtain decays downstream
    assert float(np.min(phi_hi)) >= FILM_FLUX_FLOOR - 1e-9
    m_lo = area_weighted_mean(xs, rs, phi_lo)
    m_hi = area_weighted_mean(xs, rs, phi_hi)
    assert 0.8 < m_lo < 1.0 and m_hi < m_lo               # 2% is gentle, 12% stronger
    # downstream-slot injection: no protection upstream of the slot
    phi_slot = film_effectiveness_profile(xs, rs, dt_dia, 0.10, inject_area_ratio=1.5)
    assert phi_slot[0] == 1.0 and float(np.min(phi_slot)) < 1.0

    # --- nozzle-extension film slot + combination + film T_aw ----------------
    # test contour: throat r 0.04 at index 2, exit r 0.15 (eps ~14) at index 3.
    assert np.array_equal(nozzle_film_effectiveness_profile(xs, rs, dt_dia, 0.0, 10.0),
                          np.ones(len(xs)))
    assert np.array_equal(nozzle_film_effectiveness_profile(xs, rs, dt_dia, 0.1, 50.0),
                          np.ones(len(xs)))                 # slot beyond the exit -> off
    phi_n = nozzle_film_effectiveness_profile(xs, rs, dt_dia, 0.10, 10.0)
    assert np.all(phi_n[:3] == 1.0) and phi_n[3] < 1.0     # only downstream of the slot
    _fx = np.linspace(0.0, 1.0, 60)                        # finer bell: phi recovers downstream
    _fr = np.where(_fx < 0.3, 0.10, np.where(_fx < 0.4, 0.10 - 0.6 * (_fx - 0.3),
                                              0.04 + 0.25 * (_fx - 0.4)))
    _pn = nozzle_film_effectiveness_profile(_fx, _fr, 0.08, 0.08, 8.0)
    _i0 = int(np.argmax(_pn < 1.0))
    assert _i0 > int(np.argmin(_fr)) and np.all(np.diff(_pn[_i0:]) >= -1e-12)
    _pc = film_effectiveness_profile(_fx, _fr, 0.08, 0.05)
    assert np.array_equal(combined_film_phi(_pc, np.ones_like(_pc)), _pc)
    assert np.all(combined_film_phi(_pc, _pn) <= _pc + 1e-12)
    assert float(np.min(combined_film_phi(_pc * 0 + 0.4, _pn * 0 + 0.4))) == FILM_FLUX_FLOOR
    assert film_adiabatic_wall_temp(3000.0, 1.0, 300.0) == 3000.0
    assert abs(film_adiabatic_wall_temp(3000.0, 0.6, 300.0) - (3000.0 - 0.4 * 2700.0)) < 1e-9

    # --- real Bartz h_g + computed wall temperature -------------------------
    # LOX/RP-1-class throat: Dt 0.9 m, Pc 7 MPa, c* 1720 m/s, mu 7.6e-5, cp 2100, Pr 0.77.
    hg_throat = bartz_hg(0.9, 7.0e6, 1720.0, 7.6e-5, 2100.0, 0.77, area_ratio=1.0)
    hg_up = bartz_hg(0.9, 7.0e6, 1720.0, 7.6e-5, 2100.0, 0.77, area_ratio=4.0)
    assert hg_throat > hg_up > 0.0, (hg_throat, hg_up)          # h_g peaks at the throat
    # recovery acts on the DYNAMIC part only: T0 in the chamber, ~0.99 T0 at the throat
    assert recovery_temperature(3600.0) == 3600.0
    t_aw = recovery_temperature(3600.0, r=0.9, mach=1.0, gamma=1.2)
    assert 3550.0 < t_aw < 3600.0, t_aw
    q_throat_bartz = hg_throat * (t_aw - 800.0)                  # 800 K copper wall
    t_wg = wall_gas_temperature(q_throat_bartz, hg_throat, t_aw)
    assert abs(t_wg - 800.0) < 1.0, t_wg                        # inverts cleanly
    # Bartz throat flux and the conservative anchored profile peak agree to
    # within a small factor (the anchor is deliberately low; a real throat runs
    # several x its area-average).
    ratio = q_throat_bartz / q.max()
    assert 0.3 < ratio < 5.0, (q_throat_bartz / 1e6, q.max() / 1e6, ratio)

    # --- radiation-cooled nozzle-extension equilibrium ---------------------
    t_rad = radiative_wall_temperature(200.0, 2500.0, 0.85)
    assert 0.0 < t_rad < 2500.0
    convective = 200.0 * (2500.0 - t_rad)
    imbalance = convective - 0.85 * STEFAN_BOLTZMANN_W_M2K4 * t_rad ** 4
    assert abs(imbalance) / convective < 1e-3, (t_rad, imbalance, convective)  # balance solved

    # --- regen Isp credit -------------------------------------------------
    # credit ~ 0.5 x recovered heat / chamber enthalpy flow, capped
    assert regen_isp_bonus_from_heat(0.0, 1e9) == 0.0
    assert abs(regen_isp_bonus_from_heat(1e7, 1e9) - REGEN_ISP_ENERGY_TO_ISP * 0.01) < 1e-15
    assert regen_isp_bonus_from_heat(1e9, 1e9) == REGEN_ISP_BONUS_MAX

    # --- coolant-side channel model -------------------------------------------
    # A representative regen contour: injector face -> chamber end -> throat -> exit.
    cx = np.array([0.0, 0.30, 0.45, 1.20])
    cr = np.array([0.14, 0.14, 0.055, 0.30])
    ct_dia = 0.11
    cq = heat_flux_profile(cx, cr, ct_dia, pc_pa=8.0e6, transition_area_ratio=6.0)

    n_lo = channel_count(ct_dia)
    n_hi = channel_count(0.9)                      # F-1-class throat
    assert n_lo >= CHANNEL_MIN_COUNT
    assert 100 <= n_lo <= 400 and 100 <= n_hi <= 500, (n_lo, n_hi)  # near-constant by design

    # channel_hydraulic_geometry: more channels at the same wall -> narrower
    # channels -> smaller Dh; coupled_wall_temps drops T_wg as h_c rises.
    g_few = channel_hydraulic_geometry(0.10, 60, 4.0e-3, 0.35)
    g_many = channel_hydraulic_geometry(0.10, 200, 4.0e-3, 0.35)
    assert 0.0 < g_many["dh_m"] < g_few["dh_m"]
    twg_lo_hc, twc_lo = coupled_wall_temps(20e6, 5e4, 3300.0, 3.0e4, 400.0, 1.5e-3, 325.0)
    twg_hi_hc, twc_hi = coupled_wall_temps(20e6, 5e4, 3300.0, 6.0e4, 400.0, 1.5e-3, 325.0)
    assert twg_hi_hc < twg_lo_hc and twc_hi < twc_lo   # higher h_c -> lower wall temps
    assert twg_lo_hc > twc_lo                          # hot face hotter than cold face

    # solve_wall_balance: the three fluxes agree, and the wall cools with higher
    # h_c, thinner wall, higher k, and lower h_g (deposit credit).
    twg, twc, qb = solve_wall_balance(7.0e3, 3100.0, 3.0e4, 350.0, 0.5e-3, 325.0)
    assert 350.0 < twc < twg < 3100.0
    assert abs(qb - 3.0e4 * (twc - 350.0)) / qb < 1e-9
    assert abs(qb - 325.0 / 0.5e-3 * (twg - twc)) / qb < 1e-9
    assert solve_wall_balance(7.0e3, 3100.0, 4.0e4, 350.0, 0.5e-3, 325.0)[0] < twg
    assert solve_wall_balance(7.0e3, 3100.0, 3.0e4, 350.0, 0.2e-3, 325.0)[0] < twg
    assert solve_wall_balance(7.0e3, 3100.0, 3.0e4, 350.0, 0.5e-3, 15.0)[0] > twg
    assert solve_wall_balance(3.5e3, 3100.0, 3.0e4, 350.0, 0.5e-3, 325.0)[0] < twg

    # march_coolant: sane outputs; the auto (velocity-targeted) geometry keeps
    # the coolant velocity - hence jacket dP - roughly scale-invariant, so a
    # bigger engine at the same duty comes out with a *similar* jacket dP, not a
    # runaway one.
    m1 = march_coolant(cx, cr, cq, ct_dia, 60.0, "LOX/RP-1", transition_area_ratio=6.0,
                       t_inlet_k=300.0)
    assert m1["coolant_exit_t_k"] > 300.0 and m1["coolant_delta_t_k"] > 0.0
    assert m1["t_wc_throat_k"] > m1["coolant_exit_t_k"] > 300.0
    assert 100 <= m1["n_channels"] <= 400
    # throat state: bulk temp between inlet and exit, and a user velocity override raises h_c (shallower channels).
    assert 300.0 < m1["t_bulk_throat_k"] < m1["coolant_exit_t_k"]
    assert m1["v_throat_ms"] > 0.0   # may undershoot the target when the height hits its AR floor
    m_fast = march_coolant(cx, cr, cq, ct_dia, 60.0, "LOX/RP-1", transition_area_ratio=6.0,
                           t_inlet_k=300.0, target_velocity_ms=55.0)
    assert m_fast["v_throat_ms"] > m1["v_throat_ms"]
    assert m_fast["h_c_throat_w_m2k"] > m1["h_c_throat_w_m2k"]
    assert m_fast["jacket_dp_pa"] > m1["jacket_dp_pa"]
    assert 0.5e-3 < m1["channel_dh_throat_m"] < 8e-3
    # coolant delta-T scales with total wall heat (double the flux -> ~double dT).
    cq2 = heat_flux_profile(cx, cr, ct_dia, pc_pa=8.0e6, transition_area_ratio=6.0) * 2.0
    m_hot = march_coolant(cx, cr, cq2, ct_dia, 60.0, "LOX/RP-1", transition_area_ratio=6.0,
                          t_inlet_k=300.0)
    assert 1.7 < m_hot["coolant_delta_t_k"] / m1["coolant_delta_t_k"] < 2.3
    # aspect-ratio override: wide shallow channels (low aspect) pack less flow
    # area -> higher coolant velocity -> higher jacket dP than deep narrow ones.
    m_shallow = march_coolant(cx, cr, cq, ct_dia, 60.0, "LOX/RP-1", aspect_ratio=2.0,
                              transition_area_ratio=6.0, t_inlet_k=300.0)
    m_deep = march_coolant(cx, cr, cq, ct_dia, 60.0, "LOX/RP-1", aspect_ratio=6.0,
                           transition_area_ratio=6.0, t_inlet_k=300.0)
    assert m_shallow["jacket_dp_pa"] > m_deep["jacket_dp_pa"] > 0.0

    # wall construction: milled_channel is the reference; a brazed tube wall runs
    # a hotter coolant-side throat (lower h_c) and a slightly higher jacket dP; a
    # coax shell is gentler on dP but hotter still.
    m_milled = march_coolant(cx, cr, cq, ct_dia, 60.0, "LOX/RP-1", transition_area_ratio=6.0,
                             t_inlet_k=300.0, construction="milled_channel")
    m_tube = march_coolant(cx, cr, cq, ct_dia, 60.0, "LOX/RP-1", transition_area_ratio=6.0,
                           t_inlet_k=300.0, construction="tube_wall")
    m_coax = march_coolant(cx, cr, cq, ct_dia, 60.0, "LOX/RP-1", transition_area_ratio=6.0,
                           t_inlet_k=300.0, construction="coax_shell")
    assert m_milled["jacket_dp_pa"] == m1["jacket_dp_pa"]          # default = milled, no change
    assert m_tube["t_wc_throat_k"] > m_milled["t_wc_throat_k"]
    assert m_coax["t_wc_throat_k"] > m_tube["t_wc_throat_k"]
    assert m_tube["jacket_dp_pa"] > m_milled["jacket_dp_pa"] > m_coax["jacket_dp_pa"] > 0.0

    # channel_geometry_profile: a separate, additive per-station wrapper for the
    # 3D preview - covers every station (not just the coolant-flow-restricted
    # segments march_coolant marches over) and touches none of march_coolant's
    # own internal per-station calls or lumped outputs.
    x_bell = np.linspace(0.0, 1.0, 8)
    r_bell = np.linspace(0.05, 0.30, 8)              # purely diverging (bell) contour
    prof = channel_geometry_profile(x_bell, r_bell, n_channels=120,
                                    channel_height_m=4.0e-3, land_fraction=0.35)
    assert prof["width_m"].shape == x_bell.shape
    assert np.all(prof["width_m"] > 0.0) and np.all(prof["dh_m"] > 0.0)
    assert np.all(np.diff(prof["width_m"]) > 0.0)      # wider radius -> wider channel
    assert np.allclose(prof["height_m"], 4.0e-3)       # fixed channel height, per design
    # unaffected: march_coolant's own numbers on the earlier chamber/throat/exit
    # contour are exactly as computed above, whether or not this function ran.
    m_recheck = march_coolant(cx, cr, cq, ct_dia, 60.0, "LOX/RP-1", transition_area_ratio=6.0,
                              t_inlet_k=300.0)
    assert {k: v for k, v in m_recheck.items() if not isinstance(v, np.ndarray)} == {
        k: v for k, v in m1.items() if not isinstance(v, np.ndarray)}
    assert np.array_equal(m_recheck["h_c_profile_w_m2k"], m1["h_c_profile_w_m2k"], equal_nan=True)
    # per-station march profiles: finite over the cooled length, NaN past the
    # transition; the vectorised wall balance reproduces the scalar one.
    _hp, _tp = m1["h_c_profile_w_m2k"], m1["t_bulk_profile_k"]
    assert _hp.shape == cx.shape and np.isfinite(_hp[0]) and np.isfinite(_tp[0])
    _tw, _tc, _qb = solve_wall_balance_profile(np.full(len(cx), 7.0e3), 3100.0, _hp, _tp,
                                               0.5e-3, 325.0)
    _ok = np.isfinite(_hp)
    assert np.array_equal(np.isfinite(_tw), _ok)
    _j = int(np.flatnonzero(_ok)[0])
    _ref = solve_wall_balance(7.0e3, 3100.0, float(_hp[_j]), float(_tp[_j]), 0.5e-3, 325.0)
    assert abs(_tw[_j] - _ref[0]) < 1e-9 and abs(_qb[_j] - _ref[2]) < 1e-6
    print("channel_geometry_profile self-check: OK")

    # --- dump cooling: auto-sizing and the Isp penalty ------------------------
    assert dump_cooling_isp_penalty_fraction(0.0, 100.0) == 0.0
    assert dump_cooling_isp_penalty_fraction(5.0, 0.0) == 0.0
    p_small = dump_cooling_isp_penalty_fraction(2.0, 100.0)
    p_big = dump_cooling_isp_penalty_fraction(10.0, 100.0)
    assert 0.0 < p_small < p_big < (1.0 - DUMP_THRUST_RECOVERY_FRACTION)  # bigger dump -> bigger loss
    assert abs(p_small - (1.0 - DUMP_THRUST_RECOVERY_FRACTION) * 0.02) < 1e-9  # exact formula

    frac_lo = size_dump_coolant_fraction(0.3e6, 20.0, 2100.0, 120.0)   # small heat load
    frac_hi = size_dump_coolant_fraction(0.9e6, 20.0, 2100.0, 120.0)   # 3x the heat load
    assert DUMP_COOLANT_FRACTION_MIN <= frac_lo < frac_hi <= DUMP_COOLANT_FRACTION_MAX
    assert size_dump_coolant_fraction(1.0, 20.0, 2100.0, 1e9) == DUMP_COOLANT_FRACTION_MIN  # floored
    assert size_dump_coolant_fraction(1e12, 20.0, 2100.0, 1.0) == DUMP_COOLANT_FRACTION_MAX  # ceiled

    # --- computed-absolute Bartz flux profile (reported diagnostic) -----------
    q_abs = absolute_heat_flux_profile(cx, cr, ct_dia, 8.0e6, 1720.0, 7.6e-5, 2100.0, 0.77,
                                       3240.0, transition_area_ratio=6.0)
    assert q_abs.size == cx.size and float(np.min(q_abs)) >= 0.0
    _hgp = bartz_hg_profile(cx, cr, ct_dia, 8.0e6, 1720.0, 7.6e-5, 2100.0, 0.77)
    assert np.allclose(_hgp * (3240.0 - WALL_TEMP_FRACTION_DEFAULT * 3240.0), q_abs, rtol=1e-12)
    thr_i = int(np.argmin(cr))
    assert int(np.argmax(q_abs)) == thr_i, "absolute profile should also peak at the throat"
    q_abs_hot = absolute_heat_flux_profile(cx, cr, ct_dia, 8.0e6, 1720.0, 7.6e-5, 2100.0, 0.77,
                                           3240.0, wall_temp_k=500.0, transition_area_ratio=6.0)
    assert float(q_abs_hot.max()) > float(q_abs.max()), "cooler wall -> higher flux (bigger T_aw-T_wg)"
    assert np.array_equal(absolute_heat_flux_profile(cx, cr, 0.0, 8.0e6, 1720.0, 7.6e-5, 2100.0,
                                                      0.77, 3240.0), np.zeros(cx.size))

    # --- J-2-style two-pass march (march_coolant_two_pass) -------------------
    _tx = np.linspace(0.0, 1.0, 241)
    _tr = np.interp(_tx, [0.0, 0.2, 0.3, 1.0], [0.10, 0.10, 0.04, 0.20])   # eps 25 exit
    _tdt = 0.08
    _tq = heat_flux_profile(_tx, _tr, _tdt, pc_pa=5.0e6, transition_area_ratio=25.0)
    _single = march_coolant(_tx, _tr, _tq, _tdt, 5.0, "LOX/LH2", transition_area_ratio=25.0,
                            t_inlet_k=40.0)
    # (i) zero-length down pass (inlet past the cooled end) == single pass.
    _z = march_coolant_two_pass(_tx, _tr, _tq, _tdt, 5.0, "LOX/LH2", inlet_area_ratio=30.0,
                                transition_area_ratio=25.0, t_inlet_k=40.0)
    for _key in ("coolant_exit_t_k", "coolant_delta_t_k", "jacket_dp_pa", "t_wc_throat_k",
                 "channel_dh_throat_m", "n_channels"):
        assert abs(_z[_key] - _single[_key]) <= 1e-9 * max(1.0, abs(_single[_key])), \
            (_key, _z[_key], _single[_key])
    assert _z["jacket_dp_down_pa"] == 0.0 and _z["coolant_turnaround_t_k"] == 40.0
    assert np.allclose(_z["h_c_profile_w_m2k"], _single["h_c_profile_w_m2k"], equal_nan=True)
    assert np.allclose(_z["t_bulk_profile_k"], _single["t_bulk_profile_k"], equal_nan=True)
    # (ii) total coolant temperature rise is inlet-independent (energy balance).
    _mid = march_coolant_two_pass(_tx, _tr, _tq, _tdt, 5.0, "LOX/LH2", inlet_area_ratio=8.0,
                                  transition_area_ratio=25.0, t_inlet_k=40.0)
    _deep = march_coolant_two_pass(_tx, _tr, _tq, _tdt, 5.0, "LOX/LH2", inlet_area_ratio=3.0,
                                   transition_area_ratio=25.0, t_inlet_k=40.0)
    for _m in (_mid, _deep):
        assert abs(_m["coolant_delta_t_k"] - _single["coolant_delta_t_k"]) < 1e-6 * _single["coolant_delta_t_k"]
        assert 40.0 < _m["coolant_turnaround_t_k"] < _m["coolant_exit_t_k"]
    # (iii) dP grows with the down-pass length; the down tubes run ~3x faster
    # than a single-pass jacket at the same station (shared circumference).
    assert _single["jacket_dp_pa"] < _mid["jacket_dp_pa"] < _deep["jacket_dp_pa"]
    assert 0.0 < _mid["jacket_dp_down_pa"] < _deep["jacket_dp_down_pa"]
    _d8 = 2.0 * 0.04 * math.sqrt(8.0)
    _v_dn = down_pass_velocity_ms(_d8, _tdt, 5.0, "LOX/LH2")
    _v_sp = passage_velocity_ms(_d8, _tdt, 5.0, "LOX/LH2")
    _nu, _nd = two_pass_tube_counts(_tdt)
    assert abs(_v_dn / _v_sp - (_nu + _nd) / _nd) < 1e-9
    assert _nd == round(_nu * J2_DOWN_TO_UP_TUBE_RATIO) and _mid["n_channels_down"] == _nd
    print(f"two-pass march: inlet eps 8 -> dT {_mid['coolant_delta_t_k']:.0f} K (= single-pass), "
          f"turnaround {_mid['coolant_turnaround_t_k']:.0f} K, dP {_single['jacket_dp_pa']/1e6:.2f} "
          f"-> {_mid['jacket_dp_pa']/1e6:.2f} MPa (down {_mid['jacket_dp_down_pa']/1e6:.2f}), "
          f"down-tube inlet {_mid['down_pass_inlet_velocity_ms']:.0f} m/s: OK")

    print(f"channel model: {m1['n_channels']} ch, Dh_throat {m1['channel_dh_throat_m']*1e3:.2f} mm, "
          f"coolant dT {m1['coolant_delta_t_k']:.0f} K, jacket dP {m1['jacket_dp_pa']/1e6:.2f} MPa "
          f"(x CHANNEL_DP_CALIBRATION={CHANNEL_DP_CALIBRATION})")

    print(f"cooling.py smoke test OK - throat {q.max()/1e6:.1f} MW/m^2, "
          f"area-avg anchor {q_avg/1e6:.1f} MW/m^2 (peak/mean {q.max()/from_profile_mean:.1f}x), "
          f"wall heat {total/1e6:.2f} MW, coolant dT {dt:.0f} K; "
          f"Bartz h_g throat {hg_throat:.0f} W/m^2/K -> q {q_throat_bartz/1e6:.1f} MW/m^2, "
          f"T_aw {t_aw:.0f} K; radiative T_wg {t_rad:.0f} K")

    # --- 2026-09-23 cooling audit: unified thermal solve + its building blocks ---
    # station Mach: subsonic upstream of the throat, 1 at it, supersonic after
    _m = mach_profile(cr, ct_dia, 1.2)
    _ti = int(np.argmin(cr))
    assert np.all(_m[:_ti] < 1.0) and _m[_ti] == 1.0 and np.all(_m[_ti + 1:] > 1.0), _m
    # Bartz sigma: < 1 for a hot wall, rises as the wall cools, ~1.2-1.4 for a cold throat
    _s_cold, _s_hot = bartz_sigma(0.2, 1.0, 1.2), bartz_sigma(0.8, 1.0, 1.2)
    assert 1.1 < _s_cold < 1.5 and _s_hot < _s_cold, (_s_cold, _s_hot)
    # rib/fin factor [EUCASS-2023 Eq.24-25]: tall conductive lands help, degenerate -> 1
    _f_cu = float(rib_fin_factor(1e5, 1e-3, 2e-3, 4e-3, 325.0))
    _f_ss = float(rib_fin_factor(1e5, 1e-3, 2e-3, 4e-3, 16.0))
    # copper lands are good fins (>1); a stainless land (k 16) is a poor one and its
    # unwetted land area can even pull the hot-wall-referred factor below 1
    assert _f_cu > 1.0 > _f_ss > 0.0 and float(rib_fin_factor(1e5, 1e-3, 1e-3, 4e-3, 325.0)) == 1.0
    # coolant model: enthalpy round-trip; LH2 table sensible at a 45 K inlet
    _cm = CoolantModel("LOX/LH2", 10e6)
    assert _cm.table and abs(_cm.t_from_h(_cm.h(150.0)) - 150.0) < 0.5
    assert 40.0 < _cm.props(45.0)[0] < 80.0 and _cm.props(300.0)[0] < 15.0
    _cf = CoolantModel("Hydrazine", 5e6)
    assert not _cf.has_data and _cf.source == "generic fallback"
    # full solve on the demo contour: regen chamber + radiative extension
    _tr, _sec, _cut, _notes = station_treatments(cr, ct_dia, "regenerative", "radiative", 6.0, 6.0)
    _n = len(cr)
    _sol = solve_thermal(
        xs_m=cx, rs_m=cr, throat_dia_m=ct_dia, pc_pa=8e6, cstar_ms=1720.0, t0_k=3600.0,
        gamma=1.2, cp_gas=2100.0, mu_gas=1e-4, pr_gas=0.6, pair="LOX/RP-1", treatment=_tr,
        k_wall=np.full(_n, 325.0), emissivity=np.full(_n, 0.8), t_wall_m=np.full(_n, 0.8e-3),
        t_surface_k=np.full(_n, 1500.0), film_phi=np.ones(_n), film_post_jacket=True,
        coolant_inlet_k=300.0, coolant_p_pa=10e6, regen_mdot_kgs=60.0, regen_cut_eps=_cut,
        march_kw=dict(construction="milled_channel"), mdot_fuel_kgs=60.0, coolant_limit_k=120.0,
        deposit_factor=0.5)
    assert _sol["converged"], _sol["iterations"]
    # closure: q = h_g (T_aw,f - T_wg) at EVERY station (one flux, no circular inversion)
    assert np.allclose(_sol["q_w_m2"], _sol["h_g_w_m2k"] * (_sol["t_aw_film_k"] - _sol["t_wg_k"]),
                       rtol=1e-9)
    # jacket energy balance: regen heat == mdot * (h_out - h_in) of the march
    _mr = _sol["march"]
    _cm2 = _sol["coolant_model"]
    _dh = _cm2.h(300.0 + _mr["coolant_delta_t_k"]) - _cm2.h(300.0)
    assert abs(_sol["wall_heat_regen_w"] - 60.0 * _dh) < 0.03 * _sol["wall_heat_regen_w"]
    # radiative stations satisfy h_g (T_aw - T_wg) = e sigma T_wg^4
    _rad = _sol["radiative_mask"]
    if _rad.any():
        _bal = _sol["q_w_m2"][_rad] - 0.8 * STEFAN_BOLTZMANN_W_M2K4 * _sol["t_wg_k"][_rad] ** 4
        assert np.all(np.abs(_bal) < 2e-3 * _sol["q_w_m2"][_rad] + 50.0), _bal
    # dump slice: its own bleed, rise held to the limit, heat not double-counted in the jacket
    _tr2, _, _cut2, _ = station_treatments(cr, ct_dia, "regenerative", "dump", 2.0, 6.0)
    _sol2 = solve_thermal(
        xs_m=cx, rs_m=cr, throat_dia_m=ct_dia, pc_pa=8e6, cstar_ms=1720.0, t0_k=3600.0,
        gamma=1.2, cp_gas=2100.0, mu_gas=1e-4, pr_gas=0.6, pair="LOX/RP-1", treatment=_tr2,
        k_wall=np.full(_n, 325.0), emissivity=np.full(_n, 0.8), t_wall_m=np.full(_n, 0.8e-3),
        t_surface_k=np.full(_n, 1500.0), film_phi=np.ones(_n), film_post_jacket=True,
        coolant_inlet_k=300.0, coolant_p_pa=10e6, regen_mdot_kgs=60.0, regen_cut_eps=_cut2,
        march_kw=dict(construction="milled_channel"), mdot_fuel_kgs=60.0, coolant_limit_k=120.0)
    if _sol2["dump_mask"].any():
        assert _sol2["dump"]["mdot_kgs"] > 0 and _sol2["dump"]["delta_t_k"] <= 120.0 + 1.0
        assert _cut2 == 2.0      # regen jacket stops at the transition; the slice is the dump's
    print(f"unified thermal solve: {_sol['iterations']} it, throat q "
          f"{_sol['q_w_m2'][_ti]/1e6:.1f} MW/m^2, T_wg {_sol['t_wg_k'][_ti]:.0f} K, sigma "
          f"{_sol['sigma'][_ti]:.2f}, r {_sol['recovery_factor']:.3f}, fin x{_f_cu:.2f}: OK")
