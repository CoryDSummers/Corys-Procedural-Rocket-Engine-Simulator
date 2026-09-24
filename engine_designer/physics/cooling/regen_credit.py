"""Regenerative-cooling Isp credit.

Part of the physics/cooling/ package (split out of the former single-file
cooling.py - see cooling/__init__.py for the package overview)."""

# --- regenerative-cooling Isp credit ------------------------------------------
# [Sutton 8.2]: the heat the coolant absorbs is not wasted - it augments the
# propellant's energy content before injection, raising exhaust velocity
# 0.1-1.5 %.
# 2026-09-23 audit (W8): the credit used to be interpolated in that band by
# coolant dT / the pair's dT limit - so anything that raised dT WITHOUT
# recovering more heat (e.g. the F-1 bypass cutting jacket flow) raised it too.
# It is now the recovered energy itself: Isp ~ sqrt(energy), so returning a
# fraction f = Q_regen / E_chamber of the chamber's stagnation-enthalpy flow
# (mdot cp Tc - design's energy basis) gains ~f/2, capped at [Sutton]'s 1.5 %
# ceiling (0.5-5 % of the energy reaches the walls [Sutton 8.2] -> 0.25-2.5 %,
# i.e. the band's own order).
REGEN_ISP_BONUS_MAX = 0.015
REGEN_ISP_ENERGY_TO_ISP = 0.5          # d(Isp)/Isp = 0.5 d(E)/E


def regen_isp_bonus_from_heat(heat_regen_w, jet_power_w):
    """Fractional chamber-stream Isp gain from the heat the regen jacket
    returns to the injector."""
    if heat_regen_w <= 0 or jet_power_w <= 0:
        return 0.0
    return min(REGEN_ISP_BONUS_MAX, REGEN_ISP_ENERGY_TO_ISP * heat_regen_w / jet_power_w)
