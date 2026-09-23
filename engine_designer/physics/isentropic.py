"""
Exact 1D isentropic nozzle-flow relations, generalized from
/home/cory/ksp_config/sim/isentropic.py (same math, unchanged). This module
only knows gas dynamics - no propellant- or engine-specific numbers live
here.

Adds one thing sim/isentropic.py didn't have: a real, geometry-driven
conical-nozzle divergence efficiency (lambda), so a user-adjustable nozzle
half-angle feeds directly into thrust coefficient instead of a flat
"eta_noz" guess.

Reference: Sutton & Biblarz, "Rocket Propulsion Elements" - the standard
area-Mach, thrust-coefficient, and conical-divergence-loss relations.
"""
import math
from scipy.optimize import brentq

R_UNIVERSAL = 8314.46  # J / (kmol . K)
G0 = 9.80665           # m / s^2


def vandenkerckhove(gamma):
    """Gamma function Γ(γ) = sqrt(γ) * (2/(γ+1))^((γ+1)/(2(γ-1)))."""
    return math.sqrt(gamma) * (2.0 / (gamma + 1.0)) ** ((gamma + 1.0) / (2.0 * (gamma - 1.0)))


def area_ratio_from_mach(mach, gamma):
    """A/A* for a given (supersonic or subsonic) Mach number."""
    return (1.0 / mach) * (
        (2.0 / (gamma + 1.0)) * (1.0 + (gamma - 1.0) / 2.0 * mach ** 2)
    ) ** ((gamma + 1.0) / (2.0 * (gamma - 1.0)))


def mach_from_area_ratio(eps, gamma, m_low=1.0 + 1e-6, m_high=50.0):
    """Solve the SUPERSONIC branch of A/A* = eps for Mach number via root-finding."""
    def f(m):
        return area_ratio_from_mach(m, gamma) - eps

    hi = m_high
    while f(hi) < 0:
        hi *= 1.5
        if hi > 1e5:
            raise RuntimeError(f"could not bracket a root for eps={eps}, gamma={gamma}")
    return brentq(f, m_low, hi)


def pe_over_pc(mach, gamma):
    """Static-to-chamber pressure ratio at a given Mach number (isentropic)."""
    return (1.0 + (gamma - 1.0) / 2.0 * mach ** 2) ** (-gamma / (gamma - 1.0))


def pe_over_pc_from_eps(eps, gamma):
    """Convenience: exit static pressure ratio directly from expansion ratio."""
    mach = mach_from_area_ratio(eps, gamma)
    return pe_over_pc(mach, gamma)


def cf_vacuum(gamma, pe_pc, eps):
    """Ideal vacuum thrust coefficient: momentum term + pressure term."""
    momentum_term_sq = (
        (2.0 * gamma ** 2 / (gamma - 1.0))
        * (2.0 / (gamma + 1.0)) ** ((gamma + 1.0) / (gamma - 1.0))
        * (1.0 - pe_pc ** ((gamma - 1.0) / gamma))
    )
    return math.sqrt(momentum_term_sq) + eps * pe_pc


def cf_at_ambient(gamma, pe_pc, eps, pa_pc):
    """Ideal thrust coefficient at a given ambient/chamber pressure ratio."""
    return cf_vacuum(gamma, pe_pc, eps) - eps * pa_pc


def nozzle_divergence_efficiency(half_angle_deg):
    """
    Conical-nozzle divergence-loss factor lambda = (1 + cos(alpha)) / 2.
    Accounts for exhaust velocity components not aligned with the thrust
    axis in a conical (not ideal bell) nozzle. A real, geometry-driven
    efficiency term, in place of a flat guessed "eta_noz".
    lambda(0 deg) = 1.0 (ideal, no divergence loss)
    lambda(15 deg) ~ 0.983    lambda(30 deg) ~ 0.933
    """
    alpha = math.radians(half_angle_deg)
    return (1.0 + math.cos(alpha)) / 2.0


def c_star(tc, gamma, m_molar, eta_cstar=1.0):
    """Characteristic velocity from chamber conditions, scaled by a combustion efficiency."""
    r_specific = R_UNIVERSAL / m_molar
    gamma_fn = vandenkerckhove(gamma)
    cstar_ideal = math.sqrt(r_specific * tc) / gamma_fn
    return cstar_ideal * eta_cstar


def isp_from_cf(cstar, cf, g0=G0):
    return cstar * cf / g0


def static_temperature_ratio(mach, gamma):
    """
    Exact isentropic static-to-stagnation temperature ratio: T/Tc = 1 / (1 +
    (gamma-1)/2 * M^2). Used to find the LOCAL gas temperature at some point
    downstream of the throat (e.g. where nozzle cooling changes from
    regenerative to radiative) - the gas has expanded and cooled a lot by
    then, so a wall-temperature check at Tc alone is far too pessimistic for
    a nozzle-extension material.
    """
    return 1.0 / (1.0 + (gamma - 1.0) / 2.0 * mach ** 2)


def is_separated(pe, pa, k=0.4):
    """Summerfield-style separation criterion: nozzle separates if Pe < k * Pa.
    k is typically cited in the 0.35-0.4 range for kerolox/hydrolox exhaust."""
    return pe < k * pa


# ---------------------------------------------------------------------------
# Self-checks. No pytest dependency - deterministic, catch the class of
# arithmetic/sign bugs hand-calculation is prone to.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    gamma = 1.22

    # 1) Round-trip: area_ratio(mach_from_area_ratio(eps)) should recover eps.
    for eps in (8, 12, 16, 18, 20, 25, 40, 61, 84):
        m = mach_from_area_ratio(eps, gamma)
        eps_back = area_ratio_from_mach(m, gamma)
        assert abs(eps_back - eps) / eps < 1e-6, f"round-trip failed at eps={eps}: {eps_back}"

    # 2) Pe/Pc must fall monotonically as area ratio grows.
    eps_list = [8, 12, 16, 20, 25, 40, 61, 84]
    pe_pc_list = [pe_over_pc_from_eps(e, gamma) for e in eps_list]
    assert all(pe_pc_list[i] > pe_pc_list[i + 1] for i in range(len(pe_pc_list) - 1)), \
        f"Pe/Pc not monotonically decreasing: {list(zip(eps_list, pe_pc_list))}"

    # 3) Cf_vacuum must rise monotonically with area ratio.
    cf_vac_list = [cf_vacuum(gamma, pe_pc, e) for e, pe_pc in zip(eps_list, pe_pc_list)]
    assert all(cf_vac_list[i] < cf_vac_list[i + 1] for i in range(len(cf_vac_list) - 1)), \
        f"Cf_vacuum not monotonically increasing: {list(zip(eps_list, cf_vac_list))}"

    # 4) Perfectly-expanded case (Pa == Pe): Cf_at_ambient == pure momentum term.
    for e, pe_pc in zip(eps_list, pe_pc_list):
        cf_perfectly_expanded = cf_at_ambient(gamma, pe_pc, e, pa_pc=pe_pc)
        momentum_only = cf_vacuum(gamma, pe_pc, e) - e * pe_pc
        assert abs(cf_perfectly_expanded - momentum_only) < 1e-12

    # 5) Divergence efficiency: 1.0 at 0 deg, monotonically decreasing, matches
    #    the textbook 15 deg ~ 0.983 figure within 0.001.
    assert abs(nozzle_divergence_efficiency(0.0) - 1.0) < 1e-12
    angles = [0, 5, 10, 15, 20, 30]
    lambdas = [nozzle_divergence_efficiency(a) for a in angles]
    assert all(lambdas[i] > lambdas[i + 1] for i in range(len(lambdas) - 1)), lambdas
    assert abs(nozzle_divergence_efficiency(15.0) - 0.983) < 0.001, nozzle_divergence_efficiency(15.0)

    # 6) Static temperature ratio: 1.0 at M=0, monotonically decreasing with Mach.
    assert abs(static_temperature_ratio(0.0, gamma) - 1.0) < 1e-12
    machs = [0.0, 0.5, 1.0, 2.0, 3.0, 5.0]
    ratios = [static_temperature_ratio(m, gamma) for m in machs]
    assert all(ratios[i] > ratios[i + 1] for i in range(len(ratios) - 1)), ratios

    print("isentropic.py self-checks: OK")
    print(f"{'eps':>5} {'Pe/Pc':>10} {'Cf_vac':>10}")
    for e, pe_pc, cf in zip(eps_list, pe_pc_list, cf_vac_list):
        print(f"{e:5.0f} {pe_pc:10.5f} {cf:10.4f}")
    print(f"\n{'half-angle deg':>15} {'lambda':>10}")
    for a, lam in zip(angles, lambdas):
        print(f"{a:15.0f} {lam:10.4f}")
