"""
Chamber/nozzle wall mass estimate, from a real thin-wall pressure-vessel
hoop-stress formula: t = SAFETY_FACTOR * Pc * r / allowable_stress. This is
the same "derive a real physical consequence from chamber pressure" pattern
already used for turbopump mass (physics/turbopump_tech.py's
specific_power_w_kg) - a higher-pressure/wider chamber now genuinely needs a
thicker, heavier wall, not just a hotter one (that's materials.py's CR
heat-flux factor's job).

Thickness varies LOCALLY along the profile (t(x) = SF * Pc * r(x) /
allowable_stress) - a wide chamber section genuinely needs a thicker wall
than the narrow throat at the same internal pressure, for the same reason a
wide low-pressure pipe and a narrow high-pressure pipe need different wall
thicknesses. Chamber pressure is used uniformly along the whole profile
(not the locally-lower nozzle static pressure) - real nozzles taper wall
thickness further downstream as local pressure drops, which this tool does
NOT model, on top of the safety-factor/no-manufacturing-margin
simplifications below.

Explicitly a LOWER BOUND on real engine dry mass, not a complete model:
missing injector, valves, actuators, mounting structure/flanges, and any
manufacturing margin beyond the single safety factor below. Combined with
physics/turbopump_tech.py's turbopump_mass_kg (the other computed mass
contribution) in physics/design.py.
"""
import math

import numpy as np

SAFETY_FACTOR = 1.5  # typical aerospace pressure-vessel margin on allowable
                      # stress - real practice varies ~1.25-4x by program/
                      # human-rating; a reasonable single choice, not derived
                      # (Tier 3 - see ASSUMPTIONS.md)

ORTHOGRID_MASS_FRACTION = 0.6  # applied to a radiative nozzle extension's shell mass
                      # only when EngineDesign.nozzle_extension_stiffening_style ==
                      # "orthogrid": a machined-waffle shell pockets out material
                      # between ribs vs. a plain hoop-stress-thickness shell.
                      # ARBITRARY-BUT-REASONABLE, UNCITED (same tier as
                      # JACKET_DP_FRACTION_BY_COOLING_METHOD's "dump" value) - a
                      # plausible, real-direction-correct mass fraction, not derived
                      # or measured off any specific real orthogrid design. See
                      # ASSUMPTIONS.md.

MIN_WALL_THICKNESS_M = 0.5e-3  # a practical minimum-gauge/buckling floor for
                      # wall_thickness_profile_m's RENDERED thickness (only -
                      # never fed into shell_mass_kg or any other physics
                      # number). At a large nozzle-extension area ratio, local
                      # static pressure falls to a small fraction of Pc, and
                      # pure hoop stress alone would call for a vanishingly
                      # thin skin; real skirts don't actually get that thin -
                      # they're floored by handling rigidity, external-
                      # pressure buckling resistance at altitude, and minimum
                      # manufacturable sheet gauge, none of which this tool
                      # models. Not derived - an engineering-judgment floor
                      # (Tier 3), representative of real thin-sheet nozzle
                      # extensions (~0.3-1 mm class: RL10 niobium, etc).

TUBE_WALL_MIN_THICKNESS_M = 0.2e-3  # minimum regen-TUBE wall for design.py's
                      # tube_wall combined-stress sizing (min_combined_stress_
                      # thickness_m) - Huzel Sample Calc 4-4's real A-2 (LOX/LH2)
                      # Inconel X throat tube is 0.008 in = 0.20 mm [Huzel p.110-
                      # 113]; A-1 (LOX/RP-1) is 0.020 in. A cited real tube gauge,
                      # not a generic sheet floor - MIN_WALL_THICKNESS_M above is
                      # unchanged for everything else.


def wall_thickness_m(chamber_pressure_pa, radius_m, allowable_stress_pa):
    """Thin-wall pressure-vessel hoop stress: t = SF * P * r / sigma_allow."""
    return SAFETY_FACTOR * chamber_pressure_pa * radius_m / allowable_stress_pa


def wall_thickness_profile_m(rs_m, pressure_pa, allowable_stress_pa):
    """Pointwise per-STATION wall thickness t(x) = wall_thickness_m(P, r(x),
    sigma_allow), one value per station in rs_m - for the 3D preview's solid-
    shell offset (gui/preview3d_gl_core.py::offset_profile), which needs a
    thickness at every profile vertex, not the per-SEGMENT average radius
    shell_mass_kg integrates over for mass. Purely additive: does not touch
    shell_mass_kg or its mass integration.

    `pressure_pa` may be a scalar (flat chamber pressure, appropriate for the
    chamber/throat section) or a per-station array (the caller's own choice
    of local pressure - physics/design.py uses the local isentropic static
    pressure for the nozzle EXTENSION, since flat chamber pressure applied
    all the way to a large-area-ratio exit would render an increasingly
    absurd wall thickness there as expansion ratio grows)."""
    rs_m = np.asarray(rs_m, dtype=float)
    pressure_pa = np.broadcast_to(np.asarray(pressure_pa, dtype=float), rs_m.shape)
    t = SAFETY_FACTOR * pressure_pa * rs_m / allowable_stress_pa
    return np.maximum(t, MIN_WALL_THICKNESS_M)


def shell_mass_kg(xs_m, rs_m, chamber_pressure_pa, allowable_stress_pa, density_kg_m3):
    """
    Mass of a thin shell revolved from the (xs_m, rs_m) axisymmetric profile,
    with locally-varying wall thickness (see module docstring) at each
    segment's local average radius. Same frustum-lateral-surface-area
    pattern already used by physics/expander.py::cooled_surface_area.
    """
    mass = 0.0
    for i in range(len(xs_m) - 1):
        r1, r2 = rs_m[i], rs_m[i + 1]
        x1, x2 = xs_m[i], xs_m[i + 1]
        r_avg = (r1 + r2) / 2.0
        thickness = wall_thickness_m(chamber_pressure_pa, r_avg, allowable_stress_pa)
        slant = math.hypot(x2 - x1, r2 - r1)
        area = math.pi * (r1 + r2) * slant  # frustum lateral surface area
        mass += area * thickness * density_kg_m3
    return mass


def hoop_stress_pa(net_dp_pa, radius_m, thickness_m):
    """Thin-wall hoop stress magnitude for an arbitrary (possibly reversed-
    sign) net pressure differential across an ALREADY-SIZED wall - the
    inverse of wall_thickness_m's t = SF*P*r/sigma relation, used to
    evaluate a wall against a pressure differential it wasn't originally
    sized for (e.g. a regen jacket's coolant pressure exceeding local
    hot-gas static pressure near the nozzle exit - see design.py's jacket
    overpressure check). Deliberately NOT a buckling calculation: real thin
    shells fail by elastic buckling at pressures well below what this
    tension-stress formula implies once the net load reverses to
    net-inward, and real jackets resist that via channel/rib stiffening
    this tool does not model - the caller must frame this as a plausibility
    flag, not a validated structural verdict.

    Also used (2026-09-17) as the hoop term of Huzel eq 4-27 (tube_wall) /
    eq 4-31 (coax_shell) combined-stress checks in design.py's per-
    wall_construction jacket-overpressure block - see
    claude_lit/topics/06-cooling-and-heat-transfer.md."""
    if thickness_m <= 0:
        return float("inf")
    return abs(net_dp_pa) * radius_m / thickness_m


def jacket_structure_mass_kg(cooled_shell_mass_kg, mass_factor):
    """
    Extra structural mass a regen jacket adds ON TOP of the bare hoop-stress
    shell (shell_mass_kg above) for a non-milled wall construction: a braze-
    filled formed-tube bundle plus its outer jacket for a tube wall, a full
    structural outer shell for a coaxial design. `mass_factor` is
    cooling.JACKET_MASS_CONSTRUCTION_FACTOR for the chosen construction
    (milled_channel = 1.0 reference -> 0 extra). Tier 3: the direction (tube /
    coax walls are heavier than milled channels) is solid, the magnitude is an
    estimate. Kept a separate line item so shell_mass_kg stays a clean lower
    bound.
    """
    return max(0.0, mass_factor - 1.0) * max(0.0, cooled_shell_mass_kg)


# --- throat low-cycle thermal fatigue ---------------------------------------
# A high-Pc regen throat runs its hot face far hotter than its coolant-side
# face; that through-wall gradient makes the hot face want to expand against a
# cooler, stiffer backing, so it yields in compression every firing and in
# tension on shutdown. Enough start/stop cycles and it cracks - the classic
# SSME main-chamber throat "dog-house" bulging/cracking that caps reusable-
# engine life. This is a coarse strain-life estimate, NOT a thermostructural
# FEA: Tier 3, generic ductile-metal coefficients (Manson universal-slopes
# class), pinned only in ORDER OF MAGNITUDE by validate.py against SSME.
POISSON_RATIO = 0.3
FATIGUE_STRENGTH_COEFF_OVER_E = 6.0e-3   # sigma'_f / E  (~1.5*sigma_u / E)
FATIGUE_STRENGTH_EXPONENT = -0.09        # b, Basquin
FATIGUE_DUCTILITY_COEFF = 0.30           # epsilon'_f (~ true fracture ductility)
FATIGUE_DUCTILITY_EXPONENT = -0.6        # c, Coffin-Manson


def thermal_stress_pa(delta_t_k, youngs_modulus_pa, cte_per_k, nu=POISSON_RATIO):
    """Peak elastic thermal stress in a fully constrained wall with a
    through-thickness temperature difference delta_t_k:
        sigma_th = E * alpha * dT / (2 * (1 - nu)).
    The 1/(2(1-nu)) form is the standard flat-plate through-wall-gradient
    result (Sutton & Biblarz 8.3 / Timoshenko).

    Also used (2026-09-17) for the longitudinal thermal-restraint term of
    Huzel eq 4-28 (tube_wall) / eq 4-31 (coax_shell) in design.py's per-
    wall_construction jacket-overpressure block, via delta_t_k = q*t/k
    (steady 1-D Fourier conduction) - see
    claude_lit/topics/06-cooling-and-heat-transfer.md."""
    if youngs_modulus_pa <= 0 or cte_per_k <= 0 or delta_t_k <= 0:
        return 0.0
    return youngs_modulus_pa * cte_per_k * delta_t_k / (2.0 * (1.0 - nu))


def min_combined_stress_thickness_m(net_dp_pa, radius_m, thermal_per_m_pa, t_min_m, t_max_m):
    """Wall thickness minimising Huzel eq 4-27 + 4-28's combined stress
        S(t) = |dP|*r/t + K*t,   K = E*a*q / (2*(1-nu)*k)  (thermal term per metre of t)
    -> t* = sqrt(|dP|*r/K), clamped to [t_min_m, t_max_m]. Hoop falls and the
    thermal-restraint term grows with t, so t* is the best any single wall can do
    [Huzel eq 4-27/4-28 p.107-108]. Returns (t_m, limit) where limit is "floor"
    (thermal-limited - wants thinner than t_min), "cap" (pressure-limited - wants
    thicker than t_max) or "optimum"."""
    dp_r = abs(net_dp_pa) * radius_m
    if thermal_per_m_pa <= 0:
        t_star = t_max_m if dp_r > 0 else t_min_m
    else:
        t_star = math.sqrt(dp_r / thermal_per_m_pa)
    if t_star <= t_min_m:
        return t_min_m, "floor"
    if t_star >= t_max_m:
        return t_max_m, "cap"
    return t_star, "optimum"


def regen_hot_wall_thickness_m(net_dp_pa, radius_m, thermal_per_m_pa, allowable_stress_pa,
                               t_min_m, t_max_m):
    """Regen hot-gas wall thickness: the min-combined-stress gauge t*
    (min_combined_stress_thickness_m - reproduces Huzel A-1's real tube gauge,
    see validate.py), but never thinner than the gauge that carries the
    PRIMARY hoop load, t_hoop = SAFETY_FACTOR*|dP|*r/allowable. The thermal-
    restraint term is a secondary (self-limiting, strain-driven) stress whose
    consequence is low-cycle fatigue, not burst, so a hoop-limited wall is
    thickened even though that raises the thermal term (2026-09-24).
    Returns (t_m, limit): the min_combined_stress_thickness_m tags, or "hoop"
    when t_hoop governs."""
    t_m, limit = min_combined_stress_thickness_m(
        net_dp_pa, radius_m, thermal_per_m_pa, t_min_m, t_max_m)
    if allowable_stress_pa > 0 and limit != "cap":
        t_hoop = SAFETY_FACTOR * abs(net_dp_pa) * radius_m / allowable_stress_pa
        if t_hoop > t_m:
            return (t_max_m, "cap") if t_hoop >= t_max_m else (t_hoop, "hoop")
    return t_m, limit


def longitudinal_buckling_stress_pa(e_t_pa, e_c_pa, thickness_m, radius_m, nu=POISSON_RATIO):
    """Critical stress for longitudinal thermal INELASTIC BUCKLING of a
    regen tube's hot-gas-side "zone I" (restrained by the cooler, much more
    massive backside "zone II") - [Huzel eq 4-29]:
        S_c = 4*E_t*E_c*t / [(sqrt(E_t)+sqrt(E_c))^2 * sqrt(3*(1-nu^2)) * r]
    Design rule (Huzel): the longitudinal thermal stress (thermal_stress_pa
    above) should stay below 0.9*S_c.

    e_t_pa = tangential modulus, elastic (materials.Material.youngs_modulus_pa).
    e_c_pa = tangential modulus from the COMPRESSION stress-strain curve at
    wall temperature (materials.Material.e_c_pa) - a distinct, generally
    lower, nonlinear-regime quantity with NO real per-material data in this
    codebase today (every material's e_c_pa is None) - callers must check
    for that before calling this function; it is not handled here. See
    ASSUMPTIONS.md and claude_lit/topics/06-cooling-and-heat-transfer.md."""
    if e_t_pa <= 0 or e_c_pa <= 0 or thickness_m <= 0 or radius_m <= 0:
        return 0.0
    return (4.0 * e_t_pa * e_c_pa * thickness_m
            / ((math.sqrt(e_t_pa) + math.sqrt(e_c_pa)) ** 2
               * math.sqrt(3.0 * (1.0 - nu ** 2)) * radius_m))


def low_cycle_fatigue_cycles(stress_range_pa, youngs_modulus_pa):
    """
    Order-of-magnitude thermal-cycle life from the strain-life (Coffin-Manson +
    Basquin) equation, using the imposed elastic strain amplitude
    eps_a = stress_range / E and solving
        eps_a = (sigma'_f/E)*(2N)^b + eps'_f*(2N)^c
    for N by bisection. Returns +inf below the endurance-ish floor. Generic
    coefficients (module constants) - trust the exponent (how fast life falls
    as the gradient grows), not the absolute count.
    """
    if youngs_modulus_pa <= 0 or stress_range_pa <= 0:
        return float("inf")
    eps_a = stress_range_pa / youngs_modulus_pa

    def strain_at(n):
        two_n = 2.0 * n
        return (FATIGUE_STRENGTH_COEFF_OVER_E * two_n ** FATIGUE_STRENGTH_EXPONENT
                + FATIGUE_DUCTILITY_COEFF * two_n ** FATIGUE_DUCTILITY_EXPONENT)

    lo, hi = 1.0, 1.0e9
    if strain_at(hi) >= eps_a:
        return float("inf")          # essentially infinite life at this gradient
    if strain_at(lo) <= eps_a:
        return 1.0                    # fails on the first cycle
    for _ in range(200):
        mid = math.sqrt(lo * hi)     # bisection in log space
        if strain_at(mid) > eps_a:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo * hi)


# --- injector-plate mass (I3) ----------------------------------------------
# The injector body is a thick drilled plate/forging that has to carry the full
# chamber pressure across the bore - historically one of the heavier single
# chamber components, and until now the tool counted it as ZERO ("dry mass is a
# LOWER BOUND - no injector", see the module docstring). Modelled as a clamped
# circular plate: t ~ C_PLATE * dc * sqrt(SF*Pc / sigma_allow), mass = face
# area * t * density. Tier 3 - the direction (bigger bore / higher Pc = a much
# heavier plate) is right; the coefficient is an estimate. Sanity: F-1-class
# (dc ~1 m, Pc 7 MPa) -> a few hundred kg; a small chamber -> ~10 kg.
INJECTOR_PLATE_C = 0.38
INJECTOR_PLATE_SIGMA_ALLOW_PA = 2.0e8     # steel/Inconel plate, not the copper liner
INJECTOR_PLATE_DENSITY_KG_M3 = 8000.0
MAX_ELEMENT_DENSITY_PER_M2 = 40000.0      # buildable orifice crowding ceiling
                                          # (F-1 ~8000/m^2, SSME ~4000/m^2)


def injector_plate_mass_kg(chamber_dia_m, chamber_pressure_pa):
    """Mass of the injector plate (clamped-circular-plate proxy, see above)."""
    if chamber_dia_m <= 0 or chamber_pressure_pa <= 0:
        return 0.0
    t = (INJECTOR_PLATE_C * chamber_dia_m
         * math.sqrt(SAFETY_FACTOR * chamber_pressure_pa / INJECTOR_PLATE_SIGMA_ALLOW_PA))
    face_area = math.pi * (chamber_dia_m / 2.0) ** 2
    return face_area * t * INJECTOR_PLATE_DENSITY_KG_M3


def ablative_rated_burn_time_s(chamber_wall_thickness_m, consumption_rate_m_s):
    """
    LEGACY (no longer called from the main design path - see
    ablative_liner_thickness_m below, added 2026-09-25). Originally: for
    ablative-cooled chambers, the SAME hoop-stress-derived wall thickness
    used for every other material's mass calc ALSO capped how long the
    chamber could fire before the char layer was consumed through. That
    conflated the sacrificial liner with the pressure-bearing structural
    wall - real ablative liners are sized independently, for char-depth
    life, not hoop stress (see ASSUMPTIONS.md). Kept as a documented
    utility / its own self-test only.
    """
    return chamber_wall_thickness_m / consumption_rate_m_s


def ablative_liner_thickness_m(consumption_rate_m_s, target_burn_time_s, char_depth_safety_factor):
    """
    Erosion-life liner thickness: predicted char depth over the design's
    TARGET rated burn time, times a real char-depth safety factor
    [SP-8124 Sec.2.1/3.1] - independent of hoop stress. The existing
    hoop-stress wall_thickness_m now sizes the STRUCTURAL OVERWRAP behind
    this sacrificial liner (matching refrasil_phenolic's already-documented
    real 3-layer liner+insulation+overwrap construction), not the liner
    itself. See constant_thickness_shell_mass_kg for the liner's mass and
    ASSUMPTIONS.md for the fix this replaces.
    """
    return consumption_rate_m_s * target_burn_time_s * char_depth_safety_factor


def constant_thickness_shell_mass_kg(xs_m, rs_m, thickness_m, density_kg_m3):
    """
    Mass of a revolved shell at a FIXED (caller-supplied, not hoop-stress-
    derived) thickness - same frustum-lateral-surface-area integration as
    shell_mass_kg above, generalized for a caller that sizes its own
    thickness independently (an ablative char-depth liner here; a zirconia
    thermal-barrier liner elsewhere). `thickness_m` may be a scalar or a
    per-station array (a tapered liner - each segment uses its end mean).
    """
    per_station = np.ndim(thickness_m) > 0
    mass = 0.0
    for i in range(len(xs_m) - 1):
        r1, r2 = rs_m[i], rs_m[i + 1]
        x1, x2 = xs_m[i], xs_m[i + 1]
        slant = math.hypot(x2 - x1, r2 - r1)
        area = math.pi * (r1 + r2) * slant
        t = 0.5 * (thickness_m[i] + thickness_m[i + 1]) if per_station else thickness_m
        mass += area * t * density_kg_m3
    return mass


if __name__ == "__main__":
    # --- wall_thickness_profile_m: exact pointwise match to wall_thickness_m,
    # one call per station (the 3D preview's solid-shell offset needs a
    # thickness AT every profile vertex, unlike shell_mass_kg's per-segment
    # average-radius integration for mass) ---
    xs = np.array([0.0, 0.2, 0.4, 0.6, 1.0])
    rs = np.array([0.15, 0.15, 0.06, 0.06, 0.25])
    pc_pa = 6.0e6
    sigma_allow_pa = 1.5e8
    density_kg_m3 = 8900.0

    t_profile = wall_thickness_profile_m(rs, pc_pa, sigma_allow_pa)
    assert t_profile.shape == rs.shape
    for i, r in enumerate(rs):
        assert abs(t_profile[i] - wall_thickness_m(pc_pa, r, sigma_allow_pa)) < 1e-15
    # thicker where the radius is bigger, at the same pressure (real hoop-stress behavior)
    assert t_profile[0] > t_profile[2] and t_profile[-1] > t_profile[2]

    # a per-station pressure ARRAY (physics/design.py's local-isentropic-
    # pressure use for the nozzle extension) is honored pointwise, not
    # silently broadcast wrong
    pressure_profile = np.array([6.0e6, 6.0e6, 1.0e4, 1.0e4, 1.0e2])  # sharp falloff, like a real nozzle exit
    t_local = wall_thickness_profile_m(rs, pressure_profile, sigma_allow_pa)
    assert abs(t_local[0] - wall_thickness_m(6.0e6, rs[0], sigma_allow_pa)) < 1e-15
    # at near-zero local pressure, raw hoop stress would call for a
    # vanishingly thin wall - MIN_WALL_THICKNESS_M floors it at a real
    # minimum-gauge/buckling value instead of rendering nothing
    raw_at_tiny_p = SAFETY_FACTOR * 1.0e2 * rs[-1] / sigma_allow_pa
    assert raw_at_tiny_p < MIN_WALL_THICKNESS_M          # confirms the floor is actually being exercised
    assert abs(t_local[-1] - MIN_WALL_THICKNESS_M) < 1e-12
    print("wall_thickness_profile_m self-check: OK")

    # --- shell_mass_kg: pin a reference value on a fixed profile as a
    # regression anchor (no assertion existed for this function before) ---
    mass = shell_mass_kg(xs, rs, pc_pa, sigma_allow_pa, density_kg_m3)
    assert abs(mass - 61.32339076073339) / 61.32339076073339 < 1e-9, mass
    print(f"shell_mass_kg self-check: OK ({mass:.3f} kg reference)")

    # --- jacket_structure_mass_kg: milled_channel reference adds nothing;
    # a heavier construction factor adds a positive fraction of the bare shell ---
    assert jacket_structure_mass_kg(mass, mass_factor=1.0) == 0.0
    extra_tube = jacket_structure_mass_kg(mass, mass_factor=1.20)
    assert abs(extra_tube - 0.20 * mass) < 1e-9

    # --- hoop_stress_pa: inverse of wall_thickness_m - a wall exactly sized
    # for a given pressure sits right at the allowable/SF stress under that
    # SAME pressure; a bigger net differential on the same wall reads a
    # proportionally bigger stress ---
    r_ref, sigma_allow, p_ref = 0.2, 1.5e8, 6.0e6
    t_ref = wall_thickness_m(p_ref, r_ref, sigma_allow)
    stress_at_design_p = hoop_stress_pa(p_ref, r_ref, t_ref)
    assert abs(stress_at_design_p - sigma_allow / SAFETY_FACTOR) / (sigma_allow / SAFETY_FACTOR) < 1e-9
    stress_at_2x_p = hoop_stress_pa(2.0 * p_ref, r_ref, t_ref)
    assert abs(stress_at_2x_p - 2.0 * stress_at_design_p) < 1e-6
    assert hoop_stress_pa(-p_ref, r_ref, t_ref) == stress_at_design_p  # sign-agnostic magnitude
    assert hoop_stress_pa(p_ref, r_ref, 0.0) == float("inf")
    print("hoop_stress_pa self-check: OK")

    # --- ablative_liner_thickness_m: monotonic in rate and target burn time,
    # and (unlike the legacy ablative_rated_burn_time_s) independent of any
    # hoop-stress wall thickness ---
    rate_a, rate_b = 1.5e-4, 2.7e-5  # generic vs. refrasil-class rate
    t_target_a, t_target_b = 200.0, 400.0
    safety = 1.25
    liner_lo = ablative_liner_thickness_m(rate_b, t_target_a, safety)
    liner_hi_rate = ablative_liner_thickness_m(rate_a, t_target_a, safety)
    liner_hi_time = ablative_liner_thickness_m(rate_b, t_target_b, safety)
    assert liner_hi_rate > liner_lo   # higher consumption rate -> thicker liner at fixed target time
    assert liner_hi_time > liner_lo   # longer target burn time -> thicker liner at fixed rate
    assert abs(liner_lo - rate_b * t_target_a * safety) < 1e-15
    print("ablative_liner_thickness_m self-check: OK")

    # --- constant_thickness_shell_mass_kg: at a FLAT thickness equal to
    # shell_mass_kg's own local hoop-stress thickness on a cylindrical
    # (constant-radius) segment, the two must agree exactly - both are the
    # same frustum-lateral-area integration, just with a different thickness
    # source ---
    xs_cyl = np.array([0.0, 1.0])
    rs_cyl = np.array([0.1, 0.1])
    flat_t = wall_thickness_m(pc_pa, rs_cyl[0], sigma_allow_pa)
    m_flat = constant_thickness_shell_mass_kg(xs_cyl, rs_cyl, flat_t, density_kg_m3)
    m_hoop = shell_mass_kg(xs_cyl, rs_cyl, pc_pa, sigma_allow_pa, density_kg_m3)
    assert abs(m_flat - m_hoop) / m_hoop < 1e-9
    # doubling thickness doubles mass (linear in thickness)
    assert abs(constant_thickness_shell_mass_kg(xs_cyl, rs_cyl, 2.0 * flat_t, density_kg_m3)
               - 2.0 * m_flat) < 1e-9
    # per-station array: a uniform array matches the scalar exactly; a taper
    # lands strictly between its end thicknesses' flat masses
    _n = len(xs_cyl)
    assert abs(constant_thickness_shell_mass_kg(xs_cyl, rs_cyl, np.full(_n, flat_t), density_kg_m3)
               - m_flat) < 1e-9 * m_flat
    _m_taper = constant_thickness_shell_mass_kg(xs_cyl, rs_cyl, np.linspace(2 * flat_t, flat_t, _n),
                                                density_kg_m3)
    assert m_flat < _m_taper < 2.0 * m_flat
    print("constant_thickness_shell_mass_kg self-check: OK")

    # --- longitudinal_buckling_stress_pa: degenerate E_t==E_c collapses
    # (sqrt(E_t)+sqrt(E_c))^2 to 4*E, giving the simpler closed form
    # S_c = E*t / (sqrt(3*(1-nu^2)) * r) - a round-trip sanity check even
    # with synthetic numbers (no real E_c data exists yet - see
    # ASSUMPTIONS.md) ---
    e_test, t_test, r_test = 2.0e11, 0.001, 0.05
    s_c = longitudinal_buckling_stress_pa(e_test, e_test, t_test, r_test)
    s_c_closed_form = e_test * t_test / (math.sqrt(3.0 * (1.0 - POISSON_RATIO ** 2)) * r_test)
    assert abs(s_c - s_c_closed_form) / s_c_closed_form < 1e-9
    # thicker wall -> higher critical buckling stress (more resistant); bigger
    # radius -> lower (less resistant) - both monotonic
    assert longitudinal_buckling_stress_pa(e_test, e_test, 2.0 * t_test, r_test) > s_c
    assert longitudinal_buckling_stress_pa(e_test, e_test, t_test, 2.0 * r_test) < s_c
    assert longitudinal_buckling_stress_pa(e_test, 0.0, t_test, r_test) == 0.0  # no E_c data -> 0
    print("longitudinal_buckling_stress_pa self-check: OK")

    # --- thermal fatigue: a bigger through-wall gradient shortens life ---
    stress_lo = thermal_stress_pa(200.0, youngs_modulus_pa=1.2e11, cte_per_k=1.7e-5)
    stress_hi = thermal_stress_pa(600.0, youngs_modulus_pa=1.2e11, cte_per_k=1.7e-5)
    assert 0.0 < stress_lo < stress_hi
    cycles_lo = low_cycle_fatigue_cycles(stress_lo, youngs_modulus_pa=1.2e11)
    cycles_hi = low_cycle_fatigue_cycles(stress_hi, youngs_modulus_pa=1.2e11)
    assert cycles_hi < cycles_lo

    # --- injector plate mass: bigger bore / higher Pc -> heavier plate ---
    plate_small = injector_plate_mass_kg(0.3, pc_pa)
    plate_big = injector_plate_mass_kg(1.0, pc_pa)
    plate_hipc = injector_plate_mass_kg(0.3, pc_pa * 2.0)
    assert 0.0 < plate_small < plate_big
    assert plate_hipc > plate_small

    # --- min-combined-stress tube wall: t* = sqrt(dP*r/K), clamped ---
    dp_t, r_t, k_t = 14.4e6, 5.0e-3, 12.0e9
    t_opt, lim = min_combined_stress_thickness_m(dp_t, r_t, k_t, 0.2e-3, 5.0e-3)
    assert lim == "optimum" and abs(t_opt - math.sqrt(dp_t * r_t / k_t)) < 1e-12
    s_opt = hoop_stress_pa(dp_t, r_t, t_opt) + k_t * t_opt
    for t_other in (0.8 * t_opt, 1.25 * t_opt):
        assert hoop_stress_pa(dp_t, r_t, t_other) + k_t * t_other > s_opt
    assert min_combined_stress_thickness_m(dp_t, r_t, k_t, 0.2e-3, 1.5e-3) == (1.5e-3, "cap")
    assert min_combined_stress_thickness_m(2.5e6, 2e-3, 4e12, 0.2e-3, 1.5e-3) == (0.2e-3, "floor")
    print("mass_model.py: ALL SELF-CHECKS OK")
