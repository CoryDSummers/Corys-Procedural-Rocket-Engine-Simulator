"""
H-4-relevant engine-subsystem math: combustion state, chamber geometry,
turbopump power balance, gas-generator flow fraction, and a throttle sweep
that locates the sea-level flow-separation onset and checks injector
stiffness at reduced flow.

Every function takes its inputs explicitly - no hidden module-level
constants baked into the physics. `h4_report.py` supplies the H-4 design
point; this module is just the math.
"""
import numpy as np

import isentropic as iso


# ---------------------------------------------------------------------------
# Combustion state - LITERATURE-ANCHORED LOOKUP, NOT A FROM-SCRATCH
# CHEMICAL-EQUILIBRIUM SOLVE. Anchor points are engineering-reference-grade
# LOX/RP-1 CEA-class values at ~6.9 MPa (1000 psia), interpolated linearly
# over mixture ratio. Pc-dependence of Tc/gamma/M is neglected (real
# variation over 6-10 MPa is small, well under 1% for this MR range) -
# that's the approximation the RD-111 spot check in h4_report.py is meant
# to catch if it matters.
# ---------------------------------------------------------------------------
_MR_ANCHOR = np.array([2.0, 2.2, 2.4, 2.6, 2.8, 3.0])
_TC_ANCHOR = np.array([3480.0, 3560.0, 3625.0, 3670.0, 3700.0, 3715.0])   # K
_GAMMA_ANCHOR = np.array([1.229, 1.223, 1.218, 1.213, 1.209, 1.206])
_M_ANCHOR = np.array([21.6, 22.1, 22.6, 23.1, 23.5, 23.9])                # kg/kmol


def combustion_state(mr):
    """Return (Tc [K], gamma, M [kg/kmol]) for LOX/RP-1 at the given mixture ratio."""
    tc = float(np.interp(mr, _MR_ANCHOR, _TC_ANCHOR))
    gamma = float(np.interp(mr, _MR_ANCHOR, _GAMMA_ANCHOR))
    m_molar = float(np.interp(mr, _MR_ANCHOR, _M_ANCHOR))
    return tc, gamma, m_molar


def chamber_geometry(mdot, cstar, pc, eps, lstar=1.0, contraction_ratio=1.6):
    """Throat/exit/chamber sizing from mass flow, c*, chamber pressure and area ratio."""
    at = mdot * cstar / pc
    dt = np.sqrt(4.0 * at / np.pi)
    ae = eps * at
    de = np.sqrt(4.0 * ae / np.pi)
    ac = contraction_ratio * at
    dc = np.sqrt(4.0 * ac / np.pi)
    vc = lstar * at
    lc = vc / ac  # cylindrical-equivalent chamber length to the throat
    return {
        "throat_area_m2": at, "throat_dia_m": dt,
        "exit_area_m2": ae, "exit_dia_m": de,
        "chamber_area_m2": ac, "chamber_dia_m": dc,
        "chamber_volume_m3": vc, "chamber_length_m": lc,
    }


def pump_power(mdot, dp, rho, eta):
    """Shaft power [W] to raise `mdot` [kg/s] through `dp` [Pa] at density `rho`, efficiency `eta`."""
    return mdot * dp / (rho * eta)


def turbopump_power(mdot_total, mr, dp_fuel, dp_ox, rho_fuel, rho_ox, eta_fuel, eta_ox):
    """Split total flow by mixture ratio and sum fuel + ox pump shaft power."""
    mdot_fuel = mdot_total / (1.0 + mr)
    mdot_ox = mdot_total - mdot_fuel
    p_fuel = pump_power(mdot_fuel, dp_fuel, rho_fuel, eta_fuel)
    p_ox = pump_power(mdot_ox, dp_ox, rho_ox, eta_ox)
    return {
        "mdot_fuel_kgs": mdot_fuel, "mdot_ox_kgs": mdot_ox,
        "power_fuel_w": p_fuel, "power_ox_w": p_ox,
        "power_total_w": p_fuel + p_ox,
    }


def gg_flow_fraction(pump_power_total_w, tin_k, cp, eta_turbine, pressure_ratio, gamma_gg):
    """Solve for the gas-generator mass flow (as a fraction of a reference total flow)
    needed to drive the turbopump, from a simple turbine specific-work model:

        dh = cp * Tin * eta_turbine * (1 - PR^(-(gamma-1)/gamma))
        mdot_gg = pump_power_total / dh
    """
    exponent = (gamma_gg - 1.0) / gamma_gg
    dh = cp * tin_k * eta_turbine * (1.0 - pressure_ratio ** (-exponent))
    mdot_gg = pump_power_total_w / dh
    return mdot_gg, dh


def throttle_sweep(pc_100, eps, gamma, pe_pc, pa_sea_level, dp_inj_nominal,
                    throttle_grid, separation_k=0.4):
    """
    Sweep throttle setting (fraction of max, fixed-throat engine) and report,
    at each point:
      - Pc(throttle)          assumed proportional to throttle (fixed throat, mdot ~ throttle)
      - Pe(throttle)          = Pc(throttle) * Pe/Pc  (Pe/Pc itself is throttle-independent
                                for a fixed-geometry nozzle - only the level of Pc moves)
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
