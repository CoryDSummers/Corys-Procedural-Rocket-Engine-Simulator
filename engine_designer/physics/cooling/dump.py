"""Dump cooling: coolant bled through the nozzle extension and ejected overboard.

Part of the physics/cooling/ package (split verbatim out of the former
single-file cooling.py - see cooling/__init__.py for the package overview)."""

# --- dump cooling: coolant ejected overboard, not returned to the injector ---
# A small coolant bleed absorbs the wall heat exactly like a regen jacket, but is
# ejected overboard at the nozzle lip instead of returning to the main injector -
# Vulcain HM-60's dump-cooled nozzle extension (header Isp 431.5 s vac), J-2's
# turbine-exhaust-dump-cooled skirt. It still contributes SOME thrust (ejected
# near the nozzle lip, well below the core exhaust velocity), so the net Isp
# loss is only a fraction of what losing that propellant flow entirely would
# cost [Sutton 8.2's dump-cooling discussion]. design.py applies this to the
# NOZZLE-EXTENSION portion only (nozzle_cooling_method="dump") - real engines
# dump-cool skirts, not main chambers.
#
# Tier 3: DUMP_THRUST_RECOVERY_FRACTION is an engineering estimate (the dumped
# stream's effective specific impulse as a fraction of the core chamber's), not
# independently sourced; the auto-sizing floor/ceiling are sanity bounds on a
# bled coolant stream, not per-engine data.
DUMP_THRUST_RECOVERY_FRACTION = 0.40   # k_dump
DUMP_COOLANT_FRACTION_MIN = 0.02       # auto-size floor - not worth modelling below this
DUMP_COOLANT_FRACTION_MAX = 0.25       # auto-size ceiling - a sane bound on a bled stream


def size_dump_coolant_fraction(wall_heat_w, mdot_fuel_kgs, cp_j_kgk, dt_limit_k):
    """
    Fuel fraction (of mdot_fuel_kgs) a dump-cooled coolant stream needs to absorb
    `wall_heat_w` while staying within a coolant temperature rise of `dt_limit_k`
    (the pair's coking/boiling limit) - the auto-sizing counterpart to
    march_coolant's channel-count/height auto-sizing. Clamped to
    [DUMP_COOLANT_FRACTION_MIN, DUMP_COOLANT_FRACTION_MAX].
    """
    if mdot_fuel_kgs <= 0.0 or cp_j_kgk <= 0.0 or dt_limit_k <= 0.0:
        return DUMP_COOLANT_FRACTION_MIN
    needed_mdot = wall_heat_w / (cp_j_kgk * dt_limit_k)
    frac = needed_mdot / mdot_fuel_kgs
    return min(DUMP_COOLANT_FRACTION_MAX, max(DUMP_COOLANT_FRACTION_MIN, frac))


def dump_cooling_isp_penalty_fraction(dump_mdot_kgs, total_mdot_kgs):
    """
    Net fractional Isp loss from dumping `dump_mdot_kgs` of the total propellant
    flow `total_mdot_kgs` overboard at the nozzle lip instead of through the main
    injector:
        Isp_new / Isp_core = 1 - (1 - DUMP_THRUST_RECOVERY_FRACTION) * (dump/total)
    i.e. the dumped stream still contributes DUMP_THRUST_RECOVERY_FRACTION of the
    core Isp, not zero. Returns 0.0 for no dump flow / no total flow.
    """
    if total_mdot_kgs <= 0.0 or dump_mdot_kgs <= 0.0:
        return 0.0
    ratio = min(1.0, dump_mdot_kgs / total_mdot_kgs)
    return (1.0 - DUMP_THRUST_RECOVERY_FRACTION) * ratio
