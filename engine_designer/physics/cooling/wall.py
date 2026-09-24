"""Through-wall balance: gas film -> wall -> coolant (throat and full-length).

Part of the physics/cooling/ package (split verbatim out of the former
single-file cooling.py - see cooling/__init__.py for the package overview)."""
import math

import numpy as np

def coupled_wall_temps(q_w_m2, h_g_w_m2k, t_aw_k, h_c_w_m2k, t_coolant_k,
                       t_wall_m, k_wall_w_mk):
    """1-D series-resistance wall solve given the gas-side flux `q_w_m2`:
        T_wc = T_coolant + q / h_c            (coolant-side wall)
        T_wg = T_wc + q * t_wall / k_wall     (hot-gas-side wall)
    Returns (t_wg_k, t_wc_k). h_g / t_aw are accepted for callers that want the
    gas-side cross-check T_aw - q/h_g."""
    t_wc = t_coolant_k + (q_w_m2 / h_c_w_m2k if h_c_w_m2k > 0 else 0.0)
    cond = q_w_m2 * t_wall_m / k_wall_w_mk if k_wall_w_mk > 0 else 0.0
    return t_wc + cond, t_wc


# Gas-side carbon-deposit (soot) knockdown on the raw Bartz h_g, applied ONLY in
# the coupled wall balance below (solve_wall_balance), never to the flux
# profile. [TP2862-LOXRP1] measured LOX/RP-1 h_g ~40% (UMR injector, Pc 4.3 MPa)
# to ~60% (zoned injector, Pc 13.8 MPa) below the soot-free calculated value;
# 0.5 is the mid-band. Why only here: absolute_heat_flux_profile's per-class
# calibration was fitted to real engines' integrated wall heat (which already
# carried their deposits), while bartz_hg is the raw clean-wall correlation.
# Cross-check: without it a coupled solve melts the real F-1's Inconel tubes;
# with 0.4-0.6 it survives (validate.py run_coupled_wall_temperature_check).
# Tier 2 - cited range, midpoint chosen. Pairs not listed get 1.0 (no credit).
GAS_SIDE_DEPOSIT_FACTOR = {
    "LOX/RP-1": 0.5,
}


def solve_wall_balance(h_g_w_m2k, t_aw_k, h_c_w_m2k, t_bulk_k, t_wall_m, k_wall_w_mk):
    """
    Steady 1-D series-resistance balance through gas film, wall and coolant film
    [Huzel eq. 4-10; EUCASS-2023 Eq.1]:
        q = h_g (T_aw - T_wg) = (k/t)(T_wg - T_wc) = h_c (T_wc - T_bulk)
    solved in closed form with U = 1/(1/h_c + t/k):
        T_wg = (h_g T_aw + U T_bulk) / (h_g + U)
    Unlike coupled_wall_temps (which takes q as given), the flux here is an
    OUTPUT - the wall temperature responds to coolant h_c, wall thickness and
    conductivity. Returns (t_wg_k, t_wc_k, q_w_m2).
    """
    r_cool = 1.0 / h_c_w_m2k if h_c_w_m2k > 0 else float("inf")
    r_wall = t_wall_m / k_wall_w_mk if k_wall_w_mk > 0 else 0.0
    u = 1.0 / (r_cool + r_wall) if (r_cool + r_wall) > 0 else float("inf")
    if h_g_w_m2k <= 0:
        return t_bulk_k, t_bulk_k, 0.0
    if math.isinf(u):
        return t_bulk_k, t_bulk_k, h_g_w_m2k * (t_aw_k - t_bulk_k)
    t_wg = (h_g_w_m2k * t_aw_k + u * t_bulk_k) / (h_g_w_m2k + u)
    q = h_g_w_m2k * (t_aw_k - t_wg)
    t_wc = t_bulk_k + (q / h_c_w_m2k if h_c_w_m2k > 0 else 0.0)
    return t_wg, t_wc, q


def solve_wall_balance_profile(h_g_w_m2k, t_aw_k, h_c_w_m2k, t_bulk_k, t_wall_m,
                               k_wall_w_mk):
    """
    solve_wall_balance at every station at once (the full-length coupled wall
    balance). Array inputs broadcast; a station with a non-finite or <= 0 h_c or
    h_g (outside the cooled length) returns NaN. Same closed form, so the throat
    station reproduces solve_wall_balance. Returns (t_wg_k, t_wc_k, q_w_m2).
    """
    hg = np.asarray(h_g_w_m2k, dtype=float)
    taw = np.asarray(t_aw_k, dtype=float)
    hc = np.asarray(h_c_w_m2k, dtype=float)
    tb = np.asarray(t_bulk_k, dtype=float)
    hg, taw, hc, tb = np.broadcast_arrays(hg, taw, hc, tb)
    ok = np.isfinite(hg) & np.isfinite(hc) & np.isfinite(tb) & (hg > 0) & (hc > 0)
    r_wall = t_wall_m / k_wall_w_mk if k_wall_w_mk > 0 else 0.0
    with np.errstate(divide="ignore", invalid="ignore"):
        u = 1.0 / (1.0 / hc + r_wall)
        t_wg = (hg * taw + u * tb) / (hg + u)
        q = hg * (taw - t_wg)
        t_wc = tb + q / hc
    nan = np.full(hg.shape, np.nan)
    return (np.where(ok, t_wg, nan), np.where(ok, t_wc, nan), np.where(ok, q, nan))
