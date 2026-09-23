"""Fuel-film overlay: chamber curtain + nozzle-extension slot effectiveness, film-lowered adiabatic wall temperature.

Part of the physics/cooling/ package (split verbatim out of the former
single-file cooling.py - see cooling/__init__.py for the package overview)."""
import numpy as np

# --- fuel-film / curtain cooling as a length-decaying flux reduction --------
# A cool fuel curtain injected at (or downstream of) the injector face shields
# the wall; its effectiveness eta_f is highest at injection and decays as the hot
# core entrains it. The local gas-side flux is multiplied station-by-station by
# phi(x) = 1 - eta_f(x), with eta_f(x) = eta_f0 * exp(-(s - s_inject)/L_decay)
# for stations downstream of injection (phi = 1 upstream). This REPLACES the old
# flat `1 - FILM_COOLING_FLUX_REDUCTION*f` knock-down, which protected the whole
# chamber+throat equally and never recovered.
#
# Tier 3: the exp-decay SHAPE and the calibration are engineering estimates -
# tuned so ~10% film on an F-1-class chamber gives ~0.55x throat flux (throat
# wall back under the NARloy-Z limit) recovering toward ~1x down the nozzle, and
# ~2% film is a gentle ~0.9x area-average. Anchors: F-1 (~10-12% of fuel as a
# boundary curtain), RD-170 (film-cooled ORSC chamber).
FILM_ETA0_PER_FRACTION = 7.0        # eta_f0 = min(cap, this * film_mdot_ratio)
FILM_ETA0_MAX = 0.75               # a heavy curtain still can't perfectly shield the wall
FILM_DECAY_THROAT_DIAMETERS = 2.5   # curtain 1/e persistence length L_decay = this * Dt
FILM_FLUX_FLOOR = 0.35            # phi floor - the wall always sees some flux
FILM_MDOT_RATIO_REFERENCE = 0.03   # documented reference film fraction (informational)


def film_effectiveness_profile(xs_m, rs_m, throat_dia_m, film_mdot_ratio,
                                inject_area_ratio=None):
    """
    Per-station gas-side heat-flux multiplier phi in [FILM_FLUX_FLOOR, 1.0] from a
    fuel-film curtain of `film_mdot_ratio` (= film fuel / total fuel flow).
    Injected at the injector face, or - if `inject_area_ratio` (> 1) is given - at
    the first contour station whose local area ratio is at/below it (a downstream
    slot). All-ones for film_mdot_ratio <= 0.
    """
    xs = np.asarray(xs_m, dtype=float)
    rs = np.asarray(rs_m, dtype=float)
    n = len(xs)
    if film_mdot_ratio <= 0.0 or throat_dia_m <= 0.0 or n < 2:
        return np.ones(max(n, 1))
    seg = np.hypot(np.diff(xs), np.diff(rs))
    s = np.concatenate([[0.0], np.cumsum(seg)])            # arc length from injector face
    s_inject = 0.0
    if inject_area_ratio and inject_area_ratio > 1.0:
        rt = throat_dia_m / 2.0
        thr = int(np.argmin(rs))
        for i in range(n):
            if i <= thr and (rs[i] / rt) ** 2 <= inject_area_ratio:
                s_inject = s[i]
                break
    eta0 = min(FILM_ETA0_MAX, FILM_ETA0_PER_FRACTION * film_mdot_ratio)
    l_decay = FILM_DECAY_THROAT_DIAMETERS * throat_dia_m
    eta = np.where(s >= s_inject, eta0 * np.exp(-(s - s_inject) / l_decay), 0.0)
    return np.clip(1.0 - eta, FILM_FLUX_FLOOR, 1.0)


# --- nozzle-extension film slot (the second, independent film site) ---------
# A fuel film injected through a slot/manifold on the SUPERSONIC nozzle wall at
# area ratio `inject_eps` - the F-1's film-cooled extension (film from 10:1 to
# the 16:1 exit [SP-8120]; there turbine exhaust, here post-jacket fuel), J-2X
# and Vulcain practice. Same eta_f0 law as the chamber curtain, but the decay
# length scales with the LOCAL wall diameter at the slot (the film's
# persistence scales with the boundary-layer/stream size it sits in, not the
# throat's), so a slot at eps 10 persists ~sqrt(10)x longer than a face curtain.
#
# Tier 3: no film-effectiveness correlation in hand - NASA SP-8124 (the
# self-cooled-chamber / film-cooling monograph) is the missing source (see
# claude_lit/OPEN_QUESTIONS.md), and [SECA-HT] shows decay length is the hard
# part even for CFD. Trust the direction, not the magnitude.
def nozzle_film_effectiveness_profile(xs_m, rs_m, throat_dia_m, film_mdot_ratio,
                                      inject_eps):
    """
    Per-station flux multiplier phi in [FILM_FLUX_FLOOR, 1.0] from a nozzle-
    extension film slot carrying `film_mdot_ratio` (= slot film fuel / total fuel
    flow), injected at the first SUPERSONIC station whose local area ratio is
    >= `inject_eps`. phi = 1 upstream of the slot; all-ones when the fraction is
    <= 0, `inject_eps` <= 1, or the slot lies beyond the contour's exit.
    """
    xs = np.asarray(xs_m, dtype=float)
    rs = np.asarray(rs_m, dtype=float)
    n = len(xs)
    if (film_mdot_ratio <= 0.0 or throat_dia_m <= 0.0 or n < 2
            or not inject_eps or inject_eps <= 1.0):
        return np.ones(max(n, 1))
    rt = throat_dia_m / 2.0
    thr = int(np.argmin(rs))
    i_slot = next((i for i in range(thr + 1, n) if (rs[i] / rt) ** 2 >= inject_eps), None)
    if i_slot is None:
        return np.ones(n)
    seg = np.hypot(np.diff(xs), np.diff(rs))
    s = np.concatenate([[0.0], np.cumsum(seg)])
    eta0 = min(FILM_ETA0_MAX, FILM_ETA0_PER_FRACTION * film_mdot_ratio)
    l_decay = FILM_DECAY_THROAT_DIAMETERS * 2.0 * rs[i_slot]
    eta = np.where(np.arange(n) >= i_slot,
                   eta0 * np.exp(-(s - s[i_slot]) / l_decay), 0.0)
    return np.clip(1.0 - eta, FILM_FLUX_FLOOR, 1.0)


def combined_film_phi(phi_chamber, phi_nozzle):
    """Both film sites together: the product of the two multipliers (treated as
    independent films - Tier 3), clipped at FILM_FLUX_FLOOR. With no slot film
    (phi_nozzle all ones) this returns phi_chamber unchanged."""
    return np.clip(np.asarray(phi_chamber, dtype=float) * np.asarray(phi_nozzle, dtype=float),
                   FILM_FLUX_FLOOR, 1.0)


def film_adiabatic_wall_temp(t_aw_k, phi, t_film_k):
    """Effective adiabatic-wall (driving) temperature under a film:
    T_aw,film = T_aw - eta_f*(T_aw - T_film), eta_f = 1 - phi. Scalar or
    per-station array - the throat line in design.py is this at the throat."""
    eta_f = np.maximum(0.0, 1.0 - np.asarray(phi, dtype=float))
    out = t_aw_k - eta_f * (t_aw_k - t_film_k)
    return float(out) if np.ndim(out) == 0 else out
