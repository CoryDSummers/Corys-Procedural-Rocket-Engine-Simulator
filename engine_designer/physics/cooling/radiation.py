"""Radiation-equilibrium wall temperature.

Part of the physics/cooling/ package (split verbatim out of the former
single-file cooling.py - see cooling/__init__.py for the package overview)."""

from .gas_side import STEFAN_BOLTZMANN_W_M2K4

def radiative_wall_temperature(h_gc_w_m2k, t_aw_k, emissivity, tol=0.5, max_iter=60):
    """
    Equilibrium wall temperature of a RADIATION-cooled surface (no active
    coolant loop): the temperature that satisfies both the gas-side convective
    input and the re-radiated flux,
        h_gc * (T_aw - T_wg) = emissivity * sigma_SB * T_wg^4   [Huzel eq. 4-38].
    Solved by bisection on [0, T_aw]. This is the right check for whether a
    niobium / C-103 / rhenium nozzle extension actually survives where the
    cooling transition is placed - materials.py otherwise just compares the
    local GAS temperature to the material limit.
    """
    if h_gc_w_m2k <= 0 or emissivity <= 0:
        return t_aw_k
    lo, hi = 0.0, t_aw_k

    def imbalance(twg):
        return h_gc_w_m2k * (t_aw_k - twg) - emissivity * STEFAN_BOLTZMANN_W_M2K4 * twg ** 4

    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        f = imbalance(mid)
        if abs(f) < tol or (hi - lo) < tol:
            return mid
        # imbalance is monotonically decreasing in twg
        if f > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
