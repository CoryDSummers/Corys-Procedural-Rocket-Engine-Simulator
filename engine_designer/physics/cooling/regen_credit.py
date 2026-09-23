"""Regenerative-cooling Isp credit.

Part of the physics/cooling/ package (split verbatim out of the former
single-file cooling.py - see cooling/__init__.py for the package overview)."""

from .coolant_props import MAX_COOLANT_DELTA_T_K

# --- regenerative-cooling Isp credit ------------------------------------------
# [Sutton 8.2]: the heat the coolant absorbs is not wasted - it augments the
# propellant's energy content before injection, raising exhaust velocity
# 0.1-1.5 %. Not modelled before this (the tool credited exactly zero).
REGEN_ISP_BONUS_MIN = 0.001
REGEN_ISP_BONUS_MAX = 0.015


def regen_isp_bonus_fraction(coolant_delta_t_k, pair):
    """Fractional exhaust-velocity (hence Isp) gain from regenerative heat
    recovery, scaled within [Sutton 8.2]'s 0.1-1.5 % band by how hard the
    coolant is working (its temperature rise vs the pair's practical limit).
    Returns 0.0 for a pair with no tabulated coolant limit."""
    limit = MAX_COOLANT_DELTA_T_K.get(pair)
    if not limit or coolant_delta_t_k <= 0:
        return 0.0
    frac = min(1.0, coolant_delta_t_k / limit)
    return REGEN_ISP_BONUS_MIN + (REGEN_ISP_BONUS_MAX - REGEN_ISP_BONUS_MIN) * frac
