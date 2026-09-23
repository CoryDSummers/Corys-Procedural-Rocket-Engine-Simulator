"""
Throttle sweep: sea-level flow separation onset + injector-stiffness check
across a throttle range. Generalized copy of the validated math in
/home/cory/ksp_config/sim/engine_physics.py.
"""
from . import isentropic as iso


def throttle_sweep(pc_100, pe_pc, pa_sea_level, dp_inj_nominal, throttle_grid, separation_k=0.4):
    """
    Sweep throttle setting (fraction of max, fixed-throat engine) and report,
    at each point:
      - Pc(throttle)          assumed proportional to throttle (fixed throat, mdot ~ throttle)
      - Pe(throttle)          = Pc(throttle) * Pe/Pc  (Pe/Pc is throttle-independent for a
                                fixed-geometry nozzle - only the level of Pc moves)
      - separated_sl          Summerfield check against sea-level ambient pressure
      - dp_inj(throttle)      assumed ~ throttle^2 (orifice flow scaling)
      - dp_inj_over_pc        injector stiffness ratio - watch it stay above ~0.10
    """
    rows = []
    for t in throttle_grid:
        pc_t = pc_100 * t
        pe_t = pc_t * pe_pc
        separated = iso.is_separated(pe_t, pa_sea_level, k=separation_k)
        dp_inj_t = dp_inj_nominal * t ** 2
        rows.append({
            "throttle": t,
            "pc_pa": pc_t,
            "pe_pa": pe_t,
            "pe_over_pa": pe_t / pa_sea_level,
            "separated_sl": separated,
            "dp_inj_pa": dp_inj_t,
            "dp_inj_over_pc": dp_inj_t / pc_t,
        })
    return rows


def separation_onset_throttle(rows):
    """From a throttle_sweep table (ascending throttle), return the lowest throttle
    at which the nozzle is NOT separated at sea level (None if never attached)."""
    attached = [r["throttle"] for r in rows if not r["separated_sl"]]
    return min(attached) if attached else None


def injector_stiffness_ok(rows, throttle_floor, min_ratio=0.10):
    """True if dp_inj_over_pc stays above min_ratio at the throttle floor."""
    matches = [r for r in rows if abs(r["throttle"] - throttle_floor) < 1e-9]
    if not matches:
        return None
    return matches[0]["dp_inj_over_pc"] >= min_ratio
