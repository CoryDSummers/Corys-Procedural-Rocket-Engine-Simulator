"""
Exact 1D isentropic nozzle-flow relations. No engine-specific numbers live here -
this module only knows gas dynamics (gamma, area ratio, pressure ratio) and takes
Tc / gamma / M / efficiencies as inputs from the caller.

Reference: Sutton & Biblarz, "Rocket Propulsion Elements", the standard
area-Mach and thrust-coefficient relations for a converging-diverging nozzle.
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
    """Vacuum thrust coefficient: momentum term + pressure term."""
    momentum_term_sq = (
        (2.0 * gamma ** 2 / (gamma - 1.0))
        * (2.0 / (gamma + 1.0)) ** ((gamma + 1.0) / (gamma - 1.0))
        * (1.0 - pe_pc ** ((gamma - 1.0) / gamma))
    )
    return math.sqrt(momentum_term_sq) + eps * pe_pc


def cf_at_ambient(gamma, pe_pc, eps, pa_pc):
    """Thrust coefficient at a given ambient/chamber pressure ratio."""
    return cf_vacuum(gamma, pe_pc, eps) - eps * pa_pc


def c_star(tc, gamma, m_molar, eta_cstar=1.0):
    """Characteristic velocity from chamber conditions, scaled by an efficiency."""
    r_specific = R_UNIVERSAL / m_molar
    gamma_fn = vandenkerckhove(gamma)
    cstar_ideal = math.sqrt(r_specific * tc) / gamma_fn
    return cstar_ideal * eta_cstar


def isp_from_cf(cstar, cf, g0=G0):
    return cstar * cf / g0


def is_separated(pe, pa, k=0.4):
    """Summerfield-style separation criterion: nozzle separates if Pe < k * Pa.
    k is typically cited in the 0.35-0.4 range for kerolox/hydrolox exhaust."""
    return pe < k * pa


# ---------------------------------------------------------------------------
# Self-checks. No pytest dependency - these are cheap, deterministic, and
# catch the class of arithmetic/sign bugs that hand-calculation is prone to.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    gamma = 1.22

    # 1) Round-trip: area_ratio(mach_from_area_ratio(eps)) should recover eps.
    for eps in (8, 12, 16, 18, 20, 25, 40):
        m = mach_from_area_ratio(eps, gamma)
        eps_back = area_ratio_from_mach(m, gamma)
        assert abs(eps_back - eps) / eps < 1e-6, f"round-trip failed at eps={eps}: {eps_back}"

    # 2) Pe/Pc must fall monotonically as area ratio grows (bigger bell -> lower exit pressure).
    eps_list = [8, 12, 16, 20, 25, 40]
    pe_pc_list = [pe_over_pc_from_eps(e, gamma) for e in eps_list]
    assert all(pe_pc_list[i] > pe_pc_list[i + 1] for i in range(len(pe_pc_list) - 1)), \
        f"Pe/Pc not monotonically decreasing: {list(zip(eps_list, pe_pc_list))}"

    # 3) Cf_vacuum must rise monotonically with area ratio (more expansion -> more vacuum thrust).
    cf_vac_list = [cf_vacuum(gamma, pe_pc, e) for e, pe_pc in zip(eps_list, pe_pc_list)]
    assert all(cf_vac_list[i] < cf_vac_list[i + 1] for i in range(len(cf_vac_list) - 1)), \
        f"Cf_vacuum not monotonically increasing: {list(zip(eps_list, cf_vac_list))}"

    # 4) Perfectly-expanded case (Pa == Pe): Cf_at_ambient must equal the pure momentum
    #    term (no over/under-expansion pressure contribution) — a wiring/sign smoke test.
    for e, pe_pc in zip(eps_list, pe_pc_list):
        cf_perfectly_expanded = cf_at_ambient(gamma, pe_pc, e, pa_pc=pe_pc)
        momentum_only = cf_vacuum(gamma, pe_pc, e) - e * pe_pc
        assert abs(cf_perfectly_expanded - momentum_only) < 1e-12

    print("isentropic.py self-checks: OK")
    print(f"{'eps':>5} {'Pe/Pc':>10} {'Cf_vac':>10}")
    for e, pe_pc, cf in zip(eps_list, pe_pc_list, cf_vac_list):
        print(f"{e:5.0f} {pe_pc:10.5f} {cf:10.4f}")
