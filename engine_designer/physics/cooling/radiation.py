"""Radiation-equilibrium wall temperature.

Part of the physics/cooling/ package (split verbatim out of the former
single-file cooling.py - see cooling/__init__.py for the package overview)."""

from .gas_side import STEFAN_BOLTZMANN_W_M2K4

def radiative_wall_temperature(h_gc_w_m2k, t_aw_k, emissivity, liner_resistance_m2k_w=0.0,
                               tol=0.5, max_iter=60):
    """
    Equilibrium wall temperature of a RADIATION-cooled surface (no active
    coolant loop): the temperature that satisfies both the gas-side convective
    input and the re-radiated flux,
        h_gc * (T_aw - T_wg) = emissivity * sigma_SB * T_wg^4   [Huzel eq. 4-38].
    Solved by bisection on [0, T_aw]. This is the right check for whether a
    niobium / C-103 / rhenium nozzle extension actually survives where the
    cooling transition is placed - materials.py otherwise just compares the
    local GAS temperature to the material limit.

    liner_resistance_m2k_w (0.0 = today's bare-material behavior, bit-
    identical): a series conduction resistance (thickness / conductivity)
    between the actual gas/liner-facing surface and the STRUCTURAL SHELL that
    re-radiates. With a liner present, the equilibrium is solved on the
    SHELL's own temperature T_shell (h_gc*(T_aw - T_liner_face) = emissivity*
    sigma_SB*T_shell^4, where T_liner_face = T_shell + q*liner_resistance_m2k_w
    is hotter than the shell by the conduction drop across the liner), but
    this function still RETURNS T_liner_face - the gas-facing temperature -
    to preserve its existing contract for every caller that uses it to
    compute heat flux (q = h_gc*(T_aw - T_wg) stays correct at every station,
    lined or not). A caller that needs the STRUCTURAL shell's own temperature
    (the bell material's thermal-margin check) derives it separately as
    T_shell = T_liner_face - q*liner_resistance_m2k_w, exact at the converged
    fixed point (see cooling/thermal_solve.py's t_shell_k output) - no second
    bisection needed.
    """
    if h_gc_w_m2k <= 0 or emissivity <= 0:
        return t_aw_k
    lo, hi = 0.0, t_aw_k

    def imbalance(t_shell):
        q = emissivity * STEFAN_BOLTZMANN_W_M2K4 * t_shell ** 4
        t_liner_face = t_shell + q * liner_resistance_m2k_w
        return h_gc_w_m2k * (t_aw_k - t_liner_face) - q

    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        f = imbalance(mid)
        if abs(f) < tol or (hi - lo) < tol:
            t_shell = mid
            break
        # imbalance is monotonically decreasing in t_shell
        if f > 0:
            lo = mid
        else:
            hi = mid
    else:
        t_shell = 0.5 * (lo + hi)
    q = emissivity * STEFAN_BOLTZMANN_W_M2K4 * t_shell ** 4
    return t_shell + q * liner_resistance_m2k_w


def required_liner_resistance_m2k_w(h_gc_w_m2k, t_aw_k, emissivity, t_shell_target_k):
    """
    Liner conduction resistance (thickness / conductivity) that holds a
    radiation-cooled STRUCTURAL shell at exactly t_shell_target_k - the closed-
    form inverse of radiative_wall_temperature's liner equilibrium. With the
    shell at T*, it re-radiates q* = emissivity*sigma*T*^4; flux continuity
    through the gas film fixes the liner face at T_face = T_aw - q*/h_gc; the
    liner must drop T_face - T* at that flux, so R = (T_face - T*)/q*.
    0.0 when the bare shell already runs at or below the target. Exact for a
    fixed h_gc - Bartz's wall-temperature correction makes h_gc drift as the
    liner face heats, which callers absorb by re-solving and re-sizing.
    """
    if h_gc_w_m2k <= 0 or emissivity <= 0 or t_shell_target_k <= 0:
        return 0.0
    q_star = emissivity * STEFAN_BOLTZMANN_W_M2K4 * t_shell_target_k ** 4
    t_face = t_aw_k - q_star / h_gc_w_m2k
    return max(0.0, (t_face - t_shell_target_k) / q_star)
