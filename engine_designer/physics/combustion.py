"""
Literature-anchored (Tc, gamma, M) vs mixture-ratio lookup tables, one per
supported propellant pair. NOT a from-scratch chemical-equilibrium solve -
these are engineering-reference-grade CEA-class values, linearly
interpolated over mixture ratio, with Pc-dependence neglected (small over
the pressure ranges these engines run at). The practical accuracy guardrail
is the per-pair spot-check in validate.py, not this table's precision.

Propellant pairs: LOX/RP-1, LOX/LH2, N2O4/MMH (storable hypergolic, MON3
treated as chemically equivalent to pure N2O4), Aerozine-50/NTO (storable
hypergolic, MON1 treated the same way - shares N2O4/MMH's table, see below),
and Hydrazine (a MONOPROPELLANT - see the note on `_TABLES["Hydrazine"]` and
`MONOPROPELLANT_PAIRS` for how that's represented without a parallel code path).
"""
import numpy as np

_TABLES = {
    "LOX/RP-1": dict(
        mr=[2.0, 2.2, 2.4, 2.6, 2.8, 3.0],
        tc=[3480.0, 3560.0, 3625.0, 3670.0, 3700.0, 3715.0],
        gamma=[1.229, 1.223, 1.218, 1.213, 1.209, 1.206],
        m=[21.6, 22.1, 22.6, 23.1, 23.5, 23.9],
    ),
    "LOX/LH2": dict(
        mr=[3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0],
        tc=[2960.0, 3145.0, 3290.0, 3390.0, 3465.0, 3520.0, 3585.0],
        gamma=[1.140, 1.148, 1.155, 1.163, 1.171, 1.179, 1.196],
        m=[10.0, 10.8, 11.6, 12.4, 13.1, 13.8, 15.1],
    ),
    # LOX/CH4 (methalox). Stoichiometric MR is ~4.0; real engines run fuel-rich at
    # MR 3.4-3.6 (BE-4 3.6, Raptor 3.55, M10/RD-016x 3.4-3.5). Products carry more
    # H2O/H2/CO than kerolox soot, so lower molar mass and lower gamma than LOX/RP-1,
    # between LOX/RP-1 and LOX/LH2. Engineering-reference (CEA-class) values;
    # the accuracy guardrail is validate.py's Raptor-2 / BE-4 spot checks.
    "LOX/CH4": dict(
        mr=[2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0],
        tc=[3380.0, 3470.0, 3530.0, 3570.0, 3595.0, 3600.0, 3590.0],
        gamma=[1.170, 1.166, 1.162, 1.158, 1.152, 1.147, 1.142],
        m=[19.6, 20.2, 20.8, 21.4, 22.0, 22.5, 23.0],
    ),
    "N2O4/MMH": dict(
        mr=[1.6, 1.8, 2.0, 2.16, 2.4, 2.6],
        tc=[3060.0, 3160.0, 3230.0, 3270.0, 3305.0, 3320.0],
        gamma=[1.223, 1.218, 1.213, 1.210, 1.206, 1.204],
        m=[20.0, 20.6, 21.1, 21.5, 22.0, 22.3],
    ),
    # Aerozine-50 (50/50 UDMH/hydrazine) is chemically close enough to MMH (both
    # hydrazine-family fuels paired with an NTO-family oxidizer) that this reuses
    # N2O4/MMH's exact table rather than an independently-sourced one - defensible,
    # not independently verified (see PART G's open items in the plan history).
    "Aerozine-50/NTO": dict(
        mr=[1.6, 1.8, 2.0, 2.16, 2.4, 2.6],
        tc=[3060.0, 3160.0, 3230.0, 3270.0, 3305.0, 3320.0],
        gamma=[1.223, 1.218, 1.213, 1.210, 1.206, 1.204],
        m=[20.0, 20.6, 21.1, 21.5, 22.0, 22.3],
    ),
    # Hydrazine: a MONOPROPELLANT, not a fuel/oxidizer pair - catalytic decomposition
    # (partial NH3 dissociation into N2/H2), not combustion. Represented as a
    # single-point table on purpose: np.interp against a length-1 array returns that
    # one value for ANY query "mixture ratio", so combustion_state() needs zero
    # special-casing, and mr_bounds() naturally returns (1.0, 1.0) - a degenerate
    # signal the GUI uses to treat the mixture-ratio slider as not applicable.
    "Hydrazine": dict(
        mr=[1.0],
        tc=[1400.0],
        gamma=[1.30],
        m=[11.0],
    ),
    # H2O2 (high-test hydrogen peroxide): a MONOPROPELLANT decomposed over a
    # catalyst bed (2 H2O2 -> 2 H2O + O2, exothermic), not combustion. Same
    # single-point-table trick as Hydrazine. The (Tc, gamma, M) below are a chosen
    # representative ~80-85% HTP adiabatic catalytic-decomposition state (steam +
    # O2), NOT a CEA run - verified only via the final Isp match to the Sprite
    # (de Havilland Spectre/Sprite) HTP JATO engine in validate.py. 98% HTP would
    # run hotter (Isp ~155-165 s) and needs its own pair/2-point table - out of scope.
    "H2O2": dict(
        mr=[1.0],
        tc=[755.0],
        gamma=[1.27],
        m=[21.8],
    ),
}

MONOPROPELLANT_PAIRS = {"Hydrazine", "H2O2"}


def is_monopropellant(pair):
    return pair in MONOPROPELLANT_PAIRS


# (rho_fuel_kg_m3, rho_ox_kg_m3) - standard propellant densities at storage conditions.
# For Hydrazine (monopropellant) the "ox" slot is a harmless duplicate - it's never
# actually read for a pressure-fed monopropellant design (verified: rho_ox is only
# used inside design.py's turbopump-family cycle branches, none of which apply here).
PROPELLANT_DENSITIES = {
    "LOX/RP-1": (810.0, 1141.0),
    "LOX/LH2": (71.0, 1141.0),
    "LOX/CH4": (422.0, 1141.0),          # liquid methane at ~112 K
    "N2O4/MMH": (880.0, 1440.0),
    "Aerozine-50/NTO": (903.0, 1440.0),
    "Hydrazine": (1021.0, 1021.0),
    "H2O2": (1390.0, 1390.0),            # ~85% HTP; "ox" slot is the harmless monoprop duplicate
}

# Combustion (c*) efficiency applied to the ideal c*, per pair.
# 2026-09-25 (P1 performance re-anchor): for the five BIPROPELLANT pairs this is
# now a real COMBUSTION efficiency on the shifting-equilibrium c* of the baked
# Cantera tables - one cited value, [Huzel §4.2] ~0.975 for a good chamber +
# injector, inside [Sutton §5.5]'s 0.96-0.99 - and the NOZZLE loss (kinetics,
# boundary layer, anything unmodelled) is carried separately by ETA_CF below.
# Before this date each bipropellant value was one lumped Isp calibration on the
# old effective Tc/gamma/M table (RP-1 0.955, LH2 0.94, CH4 0.96, MMH 0.90,
# A-50 0.9435). The monopropellants still run on that legacy table and keep
# their lumped calibrations.
DEFAULT_ETA_CSTAR = {
    "LOX/RP-1": 0.975,
    "LOX/LH2": 0.975,
    "LOX/CH4": 0.975,
    "N2O4/MMH": 0.975,
    "Aerozine-50/NTO": 0.975,
    "Hydrazine": 0.80,          # catalytic decomposition, inherently less energetic than
                                # bipropellant combustion - lower than any bipropellant
                                # pair here, which is a correctness signal, not a fudge
                                # (MR-80B-calibrated)
    "H2O2": 0.95,               # catalytic decomposition efficiency (near 1.0 for a good bed);
                                # the low absolute Isp is carried by the low Tc in the table,
                                # same pattern as Hydrazine (Sprite-calibrated)
}

# Nozzle (thrust-coefficient) efficiency vs the IDEAL shifting-equilibrium CF
# of the baked tables, per bipropellant pair: everything between ideal
# shifting-equilibrium expansion and the real engine that is not combustion
# efficiency or divergence (kinetic/finite-rate recombination, boundary-layer
# drag/heat loss, residual non-uniformity). REVERSE-SOLVED (P1, 2026-09-25) so
# each pair's validate SPOT_CHECKS anchor hits its real vacuum Isp through the
# same path as the design (eta_c* 0.975, 80%-bell reference nozzle):
# RD-111 / RL10A-3-3 / Raptor-2 / Aestus / AJ10-137. One number per pair is the
# chosen loss model ("option A"): other engines of the same pair miss by the
# spread their real losses actually have - reported per engine by validate's
# performance-residual table, not tuned away. A kinetic/boundary-layer split
# (JANNAF ODK/TDK/BLM-style) would replace this; the tables already carry the
# frozen-expansion Isp bound it needs (thermo_tables.isp_vac_ideal_s(frozen=True)).
# The monopropellants have no equilibrium table: 1.0 (their legacy path's
# DEFAULT_ETA_CSTAR still carries the whole loss).
ETA_CF = {
    "LOX/RP-1": 0.9358,          # RD-111 309.5 s
    "LOX/LH2": 0.9826,           # RL10A-3-3 442.2 s
    "LOX/CH4": 0.9588,           # Raptor-2 347.0 s
    "N2O4/MMH": 0.9088,          # Aestus 306.0 s
    "Aerozine-50/NTO": 0.9518,   # AJ10-137 314.5 s
    "Hydrazine": 1.0,
    "H2O2": 1.0,
}

# --- combustion completeness vs. L* ---------------------------------------
# Real liquid propellant needs residence time (roughly L*/c*) to vaporize,
# mix, and react before it hits the throat - if the chamber is too short,
# combustion doesn't finish and effective c* efficiency drops. This is a
# chosen curve SHAPE (Hill/saturating function), not derived or independently
# calibrated - same tier as the expander cycle's heat-flux proxy (see
# ASSUMPTIONS.md). L_MID_BASE is a per-pair "characteristic chamber length"
# for combustion completion: kerolox needs the most (real liquid droplets
# need real vaporization time), hydrolox the least (H2 is injected
# essentially as a cold gas - fast diffusion/reaction), hypergolic storable
# in between (reacts on contact but still needs mixing time). Deliberately
# chosen so a large-engine-typical L* (~1.0 m) with the baseline (impinging)
# injector sits deep in the saturated region for all three pairs - the
# existing propellant-pair Isp calibration (validate.py) is built on designs
# in that regime and should barely move; see PART F's regression check.
L_MID_BASE = {
    "LOX/RP-1": 0.030,
    "LOX/LH2": 0.015,
    "LOX/CH4": 0.022,           # between kerolox and hydrolox - methane needs some
                                 # vaporization time but less than kerosene droplets
    "N2O4/MMH": 0.020,
    "Aerozine-50/NTO": 0.020,   # same family/regime as N2O4/MMH
    "Hydrazine": 0.010,          # catalyst beds are compact/fast - shortest of any pair,
                                 # matching how small/simple real monoprop thrusters are
    "H2O2": 0.010,              # catalytic decomposition bed - compact/fast, like Hydrazine
}
COMPLETENESS_EFF_MIN = 0.3   # floor - real combustion is never literally zero, but a
                              # drastically too-short chamber is genuinely bad
COMPLETENESS_EFF_MAX = 1.0   # ceiling - a long/typical L* leaves DEFAULT_ETA_CSTAR's
                              # existing calibration untouched (no regression there)
COMPLETENESS_N = 1.5         # curve steepness


def completeness_factor(lstar_m, pair, atomization_time_modifier=1.0):
    """
    Combustion completeness (0-1, applied as an extra multiplier on eta_cstar)
    from chamber L* - a Hill/saturating function of L* relative to a per-pair,
    per-injector characteristic length:
        L_mid = L_MID_BASE[pair] * atomization_time_modifier
        f(L*) = eff_min + (eff_max - eff_min) / (1 + (L_mid / L*)^n)
    A finer-atomization injector (atomization_time_modifier < 1) needs a
    SHORTER L* for the same completeness than a coarser one.
    """
    l_mid = L_MID_BASE[pair] * atomization_time_modifier
    ratio = (l_mid / lstar_m) ** COMPLETENESS_N
    return COMPLETENESS_EFF_MIN + (COMPLETENESS_EFF_MAX - COMPLETENESS_EFF_MIN) / (1.0 + ratio)


def available_pairs():
    return list(_TABLES.keys())


def propellant_densities(pair):
    return PROPELLANT_DENSITIES[pair]


def mr_bounds(pair):
    """MR range the performance data covers: the equilibrium table's grid for
    a bipropellant pair, the legacy table's for a monopropellant."""
    from . import thermo_tables
    if thermo_tables.has_gas_table(pair):
        s = thermo_tables.gas_state(pair, 0.0, 1e6)
        return s["mr_range"]
    t = _TABLES[pair]
    return min(t["mr"]), max(t["mr"])


def combustion_state(pair, mr):
    """Return (Tc [K], gamma, M [kg/kmol]) for the given propellant pair at mixture ratio `mr`."""
    if pair not in _TABLES:
        raise ValueError(f"unsupported propellant pair {pair!r}; choices: {available_pairs()}")
    t = _TABLES[pair]
    mr_arr = np.array(t["mr"])
    tc = float(np.interp(mr, mr_arr, t["tc"]))
    gamma = float(np.interp(mr, mr_arr, t["gamma"]))
    m_molar = float(np.interp(mr, mr_arr, t["m"]))
    return tc, gamma, m_molar


def performance_state(pair, mr, pc_pa):
    """Chamber state the PERFORMANCE path runs on (P1 re-anchor, 2026-09-25).

    A bipropellant pair reads the baked Cantera equilibrium tables at the actual
    (MR, Pc): tc_k, m_molar, gamma_chamber = the chamber gas's FROZEN gamma
    (chamber Mach, sound speed, a tap-off drive gas), gamma_s = its shifting
    isentropic exponent, cstar_ideal_ms = the shifting-equilibrium c*, and
    source "equilibrium". Pressure along the nozzle comes from
    exit_pressure_ratio() (the table's own expansion), and expansion_gamma()
    fits the one-gamma exponent the downstream area relations use. The ideal vacuum thrust
    coefficient comes from cf_vac_ideal() on the same table. A monopropellant
    (no table) falls back to the legacy _TABLES row (source "legacy",
    cstar_ideal from the frozen one-gamma formula).
    """
    from . import isentropic as iso, thermo_tables
    g = thermo_tables.gas_state(pair, mr, pc_pa)
    if g is not None:
        return dict(tc_k=g["tc_k"], m_molar=g["m_molar"], gamma_chamber=g["gamma_frozen"],
                    gamma_s=g["gamma_s"], cstar_ideal_ms=g["cstar_ms"], source="equilibrium",
                    mr_clamped=g["mr_clamped"], pc_clamped=g["pc_clamped"])
    tc, gamma, m = combustion_state(pair, mr)
    return dict(tc_k=tc, m_molar=m, gamma_chamber=gamma, gamma_s=gamma,
                cstar_ideal_ms=iso.c_star(tc, gamma, m, 1.0),
                source="legacy", mr_clamped=False, pc_clamped=False)


def exit_pressure_ratio(pair, mr, pc_pa, eps, state):
    """Exit static / chamber pressure at area ratio eps: the table's shifting-
    equilibrium expansion for an "equilibrium" state, the one-gamma relation
    for a legacy one."""
    from . import isentropic as iso, thermo_tables
    if state["source"] == "equilibrium":
        return thermo_tables.pe_over_pc_at_eps(pair, mr, pc_pa, eps)[0]
    return iso.pe_over_pc_from_eps(eps, state["gamma_chamber"])


def expansion_gamma(eps, pe_pc):
    """The single isentropic exponent whose one-gamma relation gives pe_pc at
    area ratio eps - an 'effective expansion gamma' for the downstream
    one-gamma area/pressure/temperature relations (local wall pressure, static
    temperature along the nozzle), fitted to the real exit state (bisection)."""
    from . import isentropic as iso
    lo, hi = 1.01, 1.67
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        # pe/pc at fixed eps rises as gamma falls
        if iso.pe_over_pc_from_eps(eps, mid) > pe_pc:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def cf_vac_ideal(pair, mr, pc_pa, eps, state):
    """(ideal vacuum CF, eps_clamped) at area ratio eps for a performance_state
    `state`: the table's shifting-equilibrium Isp x g0 / c* for a bipropellant,
    the one-gamma isentropic CF for a legacy (monopropellant) state."""
    from . import isentropic as iso, thermo_tables
    if state["source"] == "equilibrium":
        isp, clamped = thermo_tables.isp_vac_ideal_s(pair, mr, pc_pa, eps)
        return isp * iso.G0 / state["cstar_ideal_ms"], clamped
    g = state["gamma_chamber"]
    pe_pc = iso.pe_over_pc(iso.mach_from_area_ratio(eps, g), g)
    return iso.cf_vacuum(g, pe_pc, eps), False


_R_UNIVERSAL_J_KMOL_K = 8314.462


def mixture_cp_j_kgk(gamma, m_molar):
    """Specific heat at constant pressure [J/kg-K] of an ideal gas mixture from
    its ratio of specific heats and molar mass [kg/kmol]:
        cp = gamma/(gamma-1) * R_universal / M
    Exact for an ideal gas - lets the tap-off cycle use the real main-chamber
    combustion products as its turbine drive gas without a separate Cp table.
    Sanity: LOX/RP-1 chamber (gamma~1.22, M~22) -> ~2100, matching GG_GAS_PROPERTIES."""
    if m_molar <= 0 or gamma <= 1.0:
        return 0.0
    return (gamma / (gamma - 1.0)) * _R_UNIVERSAL_J_KMOL_K / m_molar


# --- combustion-gas transport properties (for the Bartz gas-side heat-transfer
# coefficient in physics/cooling.py) --------------------------------------------
# Neither is a fitted per-pair table: viscosity is the standard Bartz molar-
# mass/temperature estimate and Prandtl number is the Eucken relation, so both
# are DERIVED from the (Tc, gamma, M) tables already above rather than adding new
# magic numbers. A real CEA transport solve would do better; the practical
# guardrail is validate.py's run_cooling_heat_flux_check() (F-1 / SSME / RL10).

# mu [lb/in-sec] = 46.6e-10 * M^0.5 * T[R]^0.6  [Bartz, via Huzel eq. 4-14/4-16].
# Folded into SI (M in kg/kmol, T in K): the unit conversion 1 lb/(in.s) =
# 17.858 Pa.s and T[R] = 1.8 T[K] collapse the leading constant to ~1.184e-7.
BARTZ_VISCOSITY_COEFF_SI = 1.184e-7   # mu[Pa.s] = this * M^0.5 * T[K]^0.6


def gas_viscosity_pa_s(m_molar, t_k):
    """Dynamic viscosity [Pa.s] of the combustion-gas mixture, from the Bartz
    molar-mass/temperature estimate (see BARTZ_VISCOSITY_COEFF_SI). Sanity:
    LOX/RP-1 chamber (M~22, T~3600 K) -> ~7.6e-5 Pa.s, in the expected
    0.7-1.1e-4 band for hot bipropellant exhaust."""
    if m_molar <= 0 or t_k <= 0:
        return 0.0
    return BARTZ_VISCOSITY_COEFF_SI * m_molar ** 0.5 * t_k ** 0.6


def prandtl(gamma):
    """Prandtl number of the combustion gas from the Eucken relation
    Pr = 4*gamma / (9*gamma - 5) - exact for an ideal gas given gamma, so no
    separate table. gamma ~ 1.2 -> Pr ~ 0.77, the textbook value Bartz's
    correlation assumes."""
    if gamma <= 1.0:
        return 0.0
    return 4.0 * gamma / (9.0 * gamma - 5.0)


def heat_transfer_gas_properties(pair, mr, pc_pa):
    """Combustion-gas properties for the WALL HEAT TRANSFER side (Bartz h_g,
    recovery temperature) - 2026-09-23 cooling audit, G1/G2.

    Bipropellants read the generated chemical-equilibrium tables
    (physics/thermo_tables.py, from tools/property_tables/): chamber Tc,
    FROZEN cp / gamma, mixture-averaged viscosity and frozen Prandtl number at
    the actual (MR, Pc). The PERFORMANCE path (combustion_state, whose
    (Tc, gamma, M) set Isp via combustion.DEFAULT_ETA_CSTAR calibrated against
    real engines) is deliberately left alone: its LOX/LH2 gamma/M columns are
    effective performance values, not physical gas properties - which is
    exactly why feeding them into cp = g/(g-1) R/M, the Bartz viscosity fit and
    Eucken Pr made LOX/LH2 heat transfer wrong and swing ~1.7x across MR.
    Monopropellants (no table) keep the old derived values, flagged
    source="legacy". Returns dict(tc_k, gamma, cp_j_kgk, mu_pa_s, prandtl,
    source, mr_clamped)."""
    from . import thermo_tables
    st = thermo_tables.gas_state(pair, mr, pc_pa)
    if st is None:
        tc, g, m = combustion_state(pair, mr)
        return dict(tc_k=tc, gamma=g, cp_j_kgk=mixture_cp_j_kgk(g, m),
                    mu_pa_s=gas_viscosity_pa_s(m, tc), prandtl=prandtl(g),
                    source="legacy (no equilibrium table)", mr_clamped=False)
    return dict(tc_k=st["tc_k"], gamma=st["gamma_frozen"], cp_j_kgk=st["cp_frozen_j_kgk"],
                mu_pa_s=st["mu_pa_s"], prandtl=st["pr_frozen"],
                source="chemical-equilibrium table", mr_clamped=st["mr_clamped"])


# --- finite-contraction-ratio chamber flow (C1) ------------------------------
# The chamber is NOT a true stagnation reservoir: the gas has to accelerate from
# ~0 at the injector face to a finite Mach at the chamber end (nozzle entrance),
# and that acceleration drops the stagnation pressure. [Sutton 8.2]: "gas
# acceleration pressure loss becomes appreciable when the chamber area is less
# than three times the throat area" - i.e. contraction ratio < 3. The injector
# end therefore sits at a HIGHER pressure than the nozzle-stagnation Pc that
# sets thrust/Isp; the pump has to supply that higher pressure.


def _area_ratio_from_mach(mach, gamma):
    """A/A* for a Mach number (same relation as isentropic.area_ratio_from_mach;
    inlined to keep combustion.py import-free)."""
    return (1.0 / mach) * (
        (2.0 / (gamma + 1.0)) * (1.0 + (gamma - 1.0) / 2.0 * mach ** 2)
    ) ** ((gamma + 1.0) / (2.0 * (gamma - 1.0)))


def chamber_mach(contraction_ratio, gamma):
    """Subsonic Mach number at the chamber end for A_chamber / A_throat =
    contraction_ratio, by bisection on the area-Mach relation. ~0.4 at
    contraction ratio 1.6, -> 0 as the ratio grows."""
    if contraction_ratio <= 1.0:
        return 1.0
    lo, hi = 1e-4, 1.0 - 1e-6
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        # A/A* decreases as M rises toward 1 on the subsonic branch
        if _area_ratio_from_mach(mid, gamma) > contraction_ratio:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def chamber_flow(contraction_ratio, gamma):
    """Returns dict(mach, injector_end_pressure_ratio, pc_loss_fraction) for a
    chamber of the given contraction ratio. `injector_end_pressure_ratio` =
    p0_injector / p0_nozzle = (1 + gamma*Mc^2) / (1 + (gamma-1)/2*Mc^2)^(g/(g-1))
    (the Rayleigh stagnation-pressure ratio from M~0 to Mc); >= 1.0, ~1.08 at
    contraction ratio 1.6, ~1.16 at 1.15 (matching [Sutton Table 5-4]'s ~16%).
    Clamped to <= 1.25."""
    mc = chamber_mach(contraction_ratio, gamma)
    ratio = ((1.0 + gamma * mc ** 2)
             / (1.0 + (gamma - 1.0) / 2.0 * mc ** 2) ** (gamma / (gamma - 1.0)))
    ratio = max(1.0, min(1.25, ratio))
    return {"mach": mc,
            "injector_end_pressure_ratio": ratio,
            "pc_loss_fraction": 1.0 - 1.0 / ratio}


# --- per-pair L* defaults (C2) ----------------------------------------------
# [Huzel Table 4-1] recommended characteristic length by propellant combination.
# EngineDesign.lstar_m keeps its flat 1.0 m default (so no spot check moves);
# the GUI seeds the slider from this on pair-select, the way ignition.py seeds
# the igniter.
L_STAR_DEFAULT_M = {
    "LOX/RP-1": 1.10,          # [Huzel Table 4-1] 40-50 in
    "LOX/LH2": 0.75,           # 22-40 in (LH2 injection)
    "LOX/CH4": 1.05,           # ~40 in - between kerolox and hydrolox, closer to kerolox
    "N2O4/MMH": 0.85,          # N2O4 / hydrazine-base 30-35 in
    "Aerozine-50/NTO": 0.85,
    "Hydrazine": 1.00,         # monoprop catalyst bed - H2O2/RP-1 "incl. catalyst bed" is
                                # 60-70 in; a hydrazine bed is compact -> ~1 m
    "H2O2": 0.60,              # HTP catalyst bed - compact silver-screen/pellet bed
}


def l_star_default_for_pair(pair):
    return L_STAR_DEFAULT_M.get(pair, 1.0)


def residence_time_from_lstar_s(lstar_m, tc_k, cstar_ms, m_molar):
    """
    Combustion-gas residence (stay) time [s] implied by a characteristic length
    L*:  t = L* * M * c* / (R_u * Tc).

    Exact inverse of L* = Vc/At: with Vc = t * mdot / rho_c,
    rho_c = Pc*M/(R_u*Tc) and At = mdot*c*/Pc, the mdot and Pc cancel and
    Vc/At = t * R_u * Tc / (M * c*). So sizing a chamber to this stay time
    (geometry.chamber_geometry sizing_method="residence_time") reproduces the
    L* sizing exactly - it's the same knob in different units. Not an estimate;
    exact algebra given L*. Feeds the GUI's residence-time slider default and
    physics/validate.py's C4 equivalence check.
    """
    if tc_k <= 0.0 or m_molar <= 0.0 or cstar_ms <= 0.0:
        return 0.0
    return lstar_m * m_molar * cstar_ms / (_R_UNIVERSAL_J_KMOL_K * tc_k)


if __name__ == "__main__":
    # Self-checks for completeness_factor: monotonic increase with L*, approaches
    # eff_max as L*->inf, approaches eff_min as L*->0, and a finer-atomization
    # injector (smaller modifier) gives higher completeness at a fixed L*.
    for pair in available_pairs():
        vals = [completeness_factor(l, pair) for l in (0.001, 0.02, 0.15, 1.0, 100.0)]
        assert all(vals[i] < vals[i + 1] for i in range(len(vals) - 1)), (pair, vals)
        assert abs(vals[-1] - COMPLETENESS_EFF_MAX) < 1e-3, (pair, vals[-1])
        assert vals[0] < COMPLETENESS_EFF_MIN + 0.05, (pair, vals[0])

        fine = completeness_factor(0.1, pair, atomization_time_modifier=0.6)
        coarse = completeness_factor(0.1, pair, atomization_time_modifier=1.0)
        assert fine > coarse, (pair, fine, coarse)

    # Transport properties: viscosity in the right band and rising with T;
    # Prandtl number in the physical range for these gammas. Bands are the tool's
    # own sanity limits, not validated numbers: the low-mu floor is 2.5e-5 (H2O2's
    # cool ~755 K decomposition gas legitimately has lower viscosity than hot
    # bipropellant exhaust) and the Pr ceiling is 0.87 (LOX/CH4's product mix sits
    # at Pr~0.855 via the Eucken relation - real, not a bug).
    for pair in available_pairs():
        tc, gamma, m_molar = combustion_state(pair, sum(mr_bounds(pair)) / 2.0)
        mu = gas_viscosity_pa_s(m_molar, tc)
        assert 2.5e-5 < mu < 1.5e-4, (pair, mu)
        assert gas_viscosity_pa_s(m_molar, tc + 500) > mu, pair
        pr = prandtl(gamma)
        assert 0.6 < pr < 0.87, (pair, pr)

    # Finite-contraction-ratio chamber flow (C1).
    for pair in available_pairs():
        _, g, _ = combustion_state(pair, sum(mr_bounds(pair)) / 2.0)
        tight = chamber_flow(1.3, g)
        loose = chamber_flow(4.0, g)
        assert 0.3 < tight["mach"] < 0.7, (pair, tight)
        assert loose["mach"] < tight["mach"]
        assert 1.0 <= loose["injector_end_pressure_ratio"] < tight["injector_end_pressure_ratio"] <= 1.25
        assert loose["pc_loss_fraction"] < 0.03 < tight["pc_loss_fraction"] < 0.20
    mid = chamber_flow(1.6, 1.20)
    assert abs(mid["mach"] - 0.40) < 0.06, mid
    assert 0.05 < mid["pc_loss_fraction"] < 0.12, mid

    # Per-pair L* defaults (C2).
    assert l_star_default_for_pair("LOX/RP-1") == 1.10
    assert l_star_default_for_pair("LOX/LH2") == 0.75
    assert l_star_default_for_pair("something/else") == 1.0

    print("combustion.py self-checks: OK")
    print(f"chamber flow @CR1.6: Mc {mid['mach']:.2f}, injector-end Pc x"
          f"{mid['injector_end_pressure_ratio']:.3f} ({mid['pc_loss_fraction']*100:.0f}% loss)")
    print(f"{'pair':>10} {'L*=1.0':>8} {'L*=0.15':>9} {'L*=0.02':>9}")
    for pair in available_pairs():
        row = [completeness_factor(l, pair) for l in (1.0, 0.15, 0.02)]
        print(f"{pair:>10} {row[0]:8.4f} {row[1]:9.4f} {row[2]:9.4f}")
