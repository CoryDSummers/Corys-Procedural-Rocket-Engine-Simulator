"""
Chamber acoustic-mode frequencies and a warn-not-block combustion-instability
regime flag.

The tool's existing stability model is the hydraulic-chug proxy only
(`injectors.min_stable_dp_ratio`, `throttle.py`). This module adds the acoustic
side: the first longitudinal / tangential / radial mode frequencies from chamber
geometry and the chamber-gas sound speed (Huzel Fig 4-59), and a flag for the
regime that historically needed baffles or acoustic cavities. It is advisory -
acoustic combustion stability is fundamentally empirical (new injectors must
reuse proven geometry and be hot-fire tested), so this WARNS, it never blocks
(CLAUDE.md convention #2).

Key relations [claude_lit/topics/14-combustion-stability.md]:
  a_e  = sqrt(gamma * R_universal * Tc / M)         chamber-gas sound speed
  1L   = a_e / (2 * Lc)                             first longitudinal  [Huzel Fig 4-59]
  1T   = 0.59 * a_e / dc                            first tangential
  1R   = 1.22 * a_e / dc                            first radial
Lc = chamber length (injector face to throat), dc = chamber diameter.
"""
import math

_R_UNIVERSAL_J_KMOL_K = 8314.462

# 1T mode multiplier and 1R mode multiplier on (a_e / dc)  [Huzel Fig 4-59].
TANGENTIAL_1T_COEFF = 0.59
RADIAL_1R_COEFF = 1.22

# "Damaging instability is rare above ~4000 Hz" and baffles are designed to
# suppress modes below it [Sutton 9.3]. A first tangential mode below this,
# combined with a soft (low dp/Pc) injector, is the regime that historically
# needed baffles / Helmholtz cavities.
DAMAGING_MODE_CEILING_HZ = 4000.0
SOFT_INJECTOR_DP_OVER_PC = 0.18
# Buzzing is most prevalent in medium engines [Sutton 9.3, Table 9-2].
MEDIUM_ENGINE_THRUST_N = (2.0e3, 2.5e5)


def speed_of_sound(gamma, m_molar, tc_k):
    """Chamber-gas acoustic velocity a_e = sqrt(gamma * R' * Tc / M) [m/s]."""
    if gamma <= 0 or m_molar <= 0 or tc_k <= 0:
        return 0.0
    return math.sqrt(gamma * _R_UNIVERSAL_J_KMOL_K * tc_k / m_molar)


def acoustic_modes(a_e_ms, lc_m, dc_m):
    """First longitudinal / tangential / radial mode frequencies [Hz]."""
    return {
        "sound_speed_ms": a_e_ms,
        "long_1l_hz": a_e_ms / (2.0 * lc_m) if lc_m > 0 else 0.0,
        "tang_1t_hz": TANGENTIAL_1T_COEFF * a_e_ms / dc_m if dc_m > 0 else 0.0,
        "rad_1r_hz": RADIAL_1R_COEFF * a_e_ms / dc_m if dc_m > 0 else 0.0,
    }


def instability_prone(modes, dp_over_pc, thrust_n):
    """
    Advisory string (or None) for a design whose first tangential mode sits in
    the historically troublesome band AND whose injector is on the soft side -
    the combination that drove baffle / acoustic-cavity development. Warn only.
    """
    f_1t = modes.get("tang_1t_hz", 0.0)
    if f_1t <= 0 or f_1t >= DAMAGING_MODE_CEILING_HZ:
        return None
    if dp_over_pc >= SOFT_INJECTOR_DP_OVER_PC:
        return None
    medium = MEDIUM_ENGINE_THRUST_N[0] <= thrust_n <= MEDIUM_ENGINE_THRUST_N[1]
    return (
        f"First tangential mode ~{f_1t:.0f} Hz is in the band damaging instability "
        f"lives in (<{DAMAGING_MODE_CEILING_HZ:.0f} Hz) and the injector is soft "
        f"(dP/Pc {dp_over_pc:.2f} < {SOFT_INJECTOR_DP_OVER_PC:.2f}). Historically this "
        f"regime needed an odd-compartment injector-face baffle or corner-mounted "
        f"Helmholtz cavities"
        + (" (buzzing is most prevalent at this thrust class)" if medium else "")
        + ". Stiffen the injector, or plan on damping devices."
    )


# --- stability aids: baffles, Helmholtz cavities, a stiffer injector ---------
# instability_prone()'s advisory names the historical cures; these model them as
# design CHOICES that resolve the advisory and carry a consequence
# [Sutton 9.3, claude_lit/topics/14]. There is no literature number for the mass
# or Isp cost of a baffle / cavity set - those coefficients are engineering
# estimates (Tier 3). What's solid is the direction: baffles add cooled hardware
# spanning the injector face; a stiffer injector trades feed-system weight /
# pump power for stability margin (dP/Pc pushed up from the ~0.15-0.25 nominal
# band toward ~0.35 large / ~0.5 small - claude_lit/topics/05).
AID_DAMPING_CEILING_HZ = 4000.0          # baffles/cavities damp modes below this
                                         # [Sutton 9.3] - the same ceiling
                                         # instability_prone() flags against
BAFFLE_MASS_PER_FACE_AREA_KG_M2 = 35.0   # cooled baffle blades spanning the face (Tier 3;
                                         # ~3 kg on a small chamber, ~30 kg on an F-1-class face)
CAVITY_MASS_EACH_KG_AT_REF_DC = 0.4      # one corner Helmholtz cavity ...
CAVITY_REF_DC_M = 0.3                    # ... at this reference bore; scales ~dc^2 (Tier 3)
BAFFLE_CSTAR_PENALTY = 0.008             # blades occupy face area + burn film coolant (Tier 3)
STIFF_INJECTOR_DP_OVER_PC = {            # effective dP/Pc floor for the stiffer builds
    "nominal": 0.0,
    "stiff": 0.30,
    "very_stiff": 0.42,
}


def baffle_compartments_ok(n):
    """An injector-face baffle's compartment count must be ODD and >= 3 - an
    even number sits on the tangential-mode nodal lines and ENHANCES the
    standing mode [Sutton 9.3]. SSME's main injector used 5."""
    return isinstance(n, int) and n >= 3 and n % 2 == 1


def stiff_injector_dp_over_pc(level, nominal_dp_over_pc):
    """Effective injector dP/Pc for a 'stiff' / 'very_stiff' build: the larger
    of the catalog nominal and the level's target floor. 'nominal' -> unchanged."""
    return max(nominal_dp_over_pc, STIFF_INJECTOR_DP_OVER_PC.get(level, 0.0))


def aid_mass_kg(chamber_dia_m, *, baffles=False, baffle_compartments=5,
                cavities=False, cavity_count=0):
    """Added dry mass [kg] of the selected stability aids. Baffle mass scales
    with the injector-face area it spans (and mildly with compartment count);
    cavity mass scales with chamber bore squared (cavity volume ~ dc^2)."""
    if chamber_dia_m <= 0:
        return 0.0
    m = 0.0
    face_area = math.pi * (chamber_dia_m / 2.0) ** 2
    if baffles:
        comp_factor = 1.0 + 0.05 * max(0, baffle_compartments - 3)
        m += BAFFLE_MASS_PER_FACE_AREA_KG_M2 * face_area * comp_factor
    if cavities and cavity_count > 0:
        m += (CAVITY_MASS_EACH_KG_AT_REF_DC * cavity_count
              * (chamber_dia_m / CAVITY_REF_DC_M) ** 2)
    return m


def aids_resolution(modes, *, baffles=False, baffle_compartments=5,
                    cavities=False, cavity_count=0):
    """
    If baffles and/or corner Helmholtz cavities are fitted and cover the modes
    an advisory flags (everything below AID_DAMPING_CEILING_HZ), return a human
    note describing the fix; otherwise None. An even / too-low baffle
    compartment count still counts as an attempt, but the note flags it as
    marginal (and design.py raises a separate warn-not-block check).
    """
    if not baffles and not (cavities and cavity_count > 0):
        return None
    f_1l = modes.get("long_1l_hz", 0.0)
    worst = max(modes.get("tang_1t_hz", 0.0),
                f_1l if f_1l < AID_DAMPING_CEILING_HZ else 0.0)
    if worst >= AID_DAMPING_CEILING_HZ:
        return None   # the flagged mode is above what a baffle / cavity set damps
    parts = []
    if baffles:
        tag = ("" if baffle_compartments_ok(baffle_compartments)
               else " (EVEN/low count - marginal; an odd >=3 count is the rule)")
        parts.append(f"{baffle_compartments}-compartment injector-face baffle{tag}")
    if cavities and cavity_count > 0:
        parts.append(f"{cavity_count} corner Helmholtz cavities")
    return " + ".join(parts) + f" damp the resonant modes below {AID_DAMPING_CEILING_HZ:.0f} Hz"


if __name__ == "__main__":
    # Vulcain HM-60 (LOX/LH2, Pc 10 MPa, MR 5.6): published first tangential
    # mode T1 = 2424 Hz [Sutton Table 9-3]. Reproduce it from geometry.
    # LOX/LH2 chamber at MR ~5.6: Tc ~3470 K, gamma ~1.17, M ~13.1.
    a_e = speed_of_sound(1.17, 13.1, 3470.0)
    assert 1400.0 < a_e < 1800.0, a_e
    modes = acoustic_modes(a_e, lc_m=0.45, dc_m=0.41)   # Vulcain chamber ~0.41 m bore
    assert abs(modes["tang_1t_hz"] - 2424.0) / 2424.0 < 0.10, modes["tang_1t_hz"]
    assert modes["rad_1r_hz"] > modes["tang_1t_hz"] > 0.0

    # Smaller chamber -> higher frequencies.
    small = acoustic_modes(a_e, lc_m=0.20, dc_m=0.15)
    assert small["tang_1t_hz"] > modes["tang_1t_hz"]

    # A stiff injector clears the advisory; a soft one in-band trips it.
    assert instability_prone(modes, dp_over_pc=0.25, thrust_n=1.0e6) is None
    assert instability_prone(modes, dp_over_pc=0.10, thrust_n=1.0e6) is not None

    # --- stability aids ---
    assert all(baffle_compartments_ok(n) for n in (3, 5, 7, 9))
    assert not any(baffle_compartments_ok(n) for n in (1, 2, 4, 0, -1))
    assert stiff_injector_dp_over_pc("stiff", 0.15) == 0.30
    assert stiff_injector_dp_over_pc("very_stiff", 0.15) == 0.42
    assert stiff_injector_dp_over_pc("nominal", 0.20) == 0.20
    assert stiff_injector_dp_over_pc("stiff", 0.35) == 0.35   # already stiffer than the floor

    assert aid_mass_kg(0.3) == 0.0
    mb_small, mb_big = aid_mass_kg(0.3, baffles=True), aid_mass_kg(0.6, baffles=True)
    assert 0.0 < mb_small < mb_big, (mb_small, mb_big)
    assert aid_mass_kg(0.3, baffles=True, baffle_compartments=9) > mb_small
    mc8, mc16 = (aid_mass_kg(0.3, cavities=True, cavity_count=8),
                 aid_mass_kg(0.3, cavities=True, cavity_count=16))
    assert 0.0 < mc8 < mc16

    assert aids_resolution(modes) is None
    assert aids_resolution(modes, cavities=True, cavity_count=0) is None
    assert "5-compartment" in aids_resolution(modes, baffles=True, baffle_compartments=5)
    assert "EVEN" in aids_resolution(modes, baffles=True, baffle_compartments=4)
    assert "Helmholtz" in aids_resolution(modes, cavities=True, cavity_count=12)

    print(f"combustion_stability.py smoke test OK - Vulcain a_e {a_e:.0f} m/s, "
          f"1L {modes['long_1l_hz']:.0f} Hz, 1T {modes['tang_1t_hz']:.0f} Hz "
          f"(published 2424), 1R {modes['rad_1r_hz']:.0f} Hz; "
          f"baffle mass @dc=0.3 m ~{mb_small:.1f} kg")
