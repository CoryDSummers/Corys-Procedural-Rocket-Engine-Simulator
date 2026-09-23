"""
Injector-type dropdown catalog. Same shape/status as materials.py: standard
propulsion-engineering figures, an engineering estimate rather than a
derived quantity (there isn't a clean single-variable real RO engine to
isolate injector type the way RD-111/RL10/Aestus isolated propellant pair
in validate.py).

eta_cstar_multiplier is applied on TOP of combustion.DEFAULT_ETA_CSTAR[pair]
(itself already calibrated assuming a generic/impinging-class injector),
so impinging is ~1.00 (the baseline) and the others are relative to that.
"""
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Injector:
    key: str
    display_name: str
    eta_cstar_multiplier: float
    dp_over_pc_nominal: float
    min_stable_dp_ratio: float
    practical_min_throttle: float  # deepest throttle this injector TYPE has demonstrated in
                                    # real engines - "ability", distinct from min_stable_dp_ratio's
                                    # "stability" (a hydraulically-stable flow an injector was
                                    # never actually designed to reach is still unrealistic)
    atomization_time_modifier: float  # scales combustion.L_MID_BASE - finer atomization
                                       # (<1.0) needs a shorter L* for the same combustion
                                       # completeness than the impinging baseline (1.0)
    relative_cost_factor: float
    suited_pairs: tuple  # empty tuple = suited to anything
    stability_note: str
    # --- element-pattern detail (added; defaulted so the 5 originals are unchanged) ---
    dp_ox_over_fuel: float = 1.0   # oxidiser-leg injector dP / fuel-leg dP. Real engines
                                    # vary widely ([Sutton Table 8-1]: RS-27 1.1, RL10B-2
                                    # 1.85, LE-7 ~4.6). 1.0 = both legs equal (the original
                                    # single-dP behaviour).
    symmetric_pattern: bool = False  # triplet / quintuplet / self-impinging: the element is
                                      # momentum-balanced so the resultant beta angle is ~0
                                      # regardless of mixture ratio ([topics/05]).
    pattern_note: str = ""          # spray-pattern description for the Injectors detail pane


INJECTORS = {
    "impinging": Injector(
        key="impinging",
        display_name="Impinging (like-on-like / unlike doublet)",
        eta_cstar_multiplier=1.00,
        dp_over_pc_nominal=0.175,
        min_stable_dp_ratio=0.10,
        practical_min_throttle=0.60,
        atomization_time_modifier=1.00,
        relative_cost_factor=1.0,
        suited_pairs=(),
        stability_note="Classic and cheap, but prone to combustion instability without "
                        "baffles/acoustic cavities - not modeled as a hard requirement here, "
                        "just worth knowing.",
    ),
    "pintle": Injector(
        key="pintle",
        display_name="Pintle",
        eta_cstar_multiplier=0.97,
        dp_over_pc_nominal=0.20,
        min_stable_dp_ratio=0.06,
        practical_min_throttle=0.10,
        atomization_time_modifier=0.85,
        relative_cost_factor=1.2,
        suited_pairs=(),
        stability_note="Built for deep throttling and stable combustion (LMDE/Merlin/TR-201 "
                        "lineage) - stays stable far deeper into throttle than the others.",
    ),
    "coaxial_swirl": Injector(
        key="coaxial_swirl",
        display_name="Coaxial swirl / shear coaxial",
        eta_cstar_multiplier=1.01,
        dp_over_pc_nominal=0.15,
        min_stable_dp_ratio=0.10,
        practical_min_throttle=0.50,
        atomization_time_modifier=0.75,
        relative_cost_factor=1.3,
        suited_pairs=("LOX/LH2",),
        stability_note="The standard for cryogenic gas/liquid pairs (SSME, RS-68, Vulcain) - "
                        "excellent atomization for a gas/liquid combo specifically.",
    ),
    "catalyst_bed": Injector(
        key="catalyst_bed",
        display_name="Catalyst bed (monopropellant decomposition)",
        eta_cstar_multiplier=1.00,
        dp_over_pc_nominal=0.12,
        min_stable_dp_ratio=0.05,
        practical_min_throttle=0.08,
        atomization_time_modifier=1.00,
        relative_cost_factor=0.8,
        suited_pairs=("Hydrazine",),
        stability_note="Not really an 'injector' - a Shell 405/Aerojet-S405-class spontaneous "
                        "catalyst bed that decomposes the monopropellant on contact. Extremely "
                        "simple and reliable, and the deepest-throttling option here by far "
                        "(real monoprop thrusters demonstrate ~8% throttle), but decomposition "
                        "is inherently less energetic than bipropellant combustion - lower Isp "
                        "ceiling no matter how good the bed is.",
    ),
    "platelet": Injector(
        key="platelet",
        display_name="Platelet (photo-etched, diffusion-bonded)",
        eta_cstar_multiplier=1.02,
        dp_over_pc_nominal=0.25,
        min_stable_dp_ratio=0.10,
        practical_min_throttle=0.40,
        atomization_time_modifier=0.70,
        relative_cost_factor=1.8,
        suited_pairs=(),
        stability_note="Modern, precise element control - high efficiency and good deep-"
                        "throttle stability, at higher cost/complexity.",
    ),
    # --- explicit element-pattern subtypes ([Huzel 4.5], [Sutton 8.1] pattern table).
    # eta_cstar_multiplier ordering (showerhead worst -> triplet/quintuplet best) is
    # literature-backed; the exact +-2% spread is an estimate, same tier as the 5 above.
    "showerhead": Injector(
        key="showerhead",
        display_name="Showerhead (non-impinging axial jets)",
        eta_cstar_multiplier=0.96,
        dp_over_pc_nominal=0.20,
        min_stable_dp_ratio=0.12,
        practical_min_throttle=0.70,
        atomization_time_modifier=1.20,
        relative_cost_factor=0.7,
        suited_pairs=(),
        stability_note="Simplest possible pattern; relies on chamber turbulence to mix. "
                        "Poor performance except a few cryogenic combinations.",
        symmetric_pattern=True,
        pattern_note="Non-impinging jets normal to the face - no impingement point, "
                      "so the resultant beta angle is ~0.",
    ),
    "unlike_triplet": Injector(
        key="unlike_triplet",
        display_name="Unlike triplet (2-on-1)",
        eta_cstar_multiplier=1.015,
        dp_over_pc_nominal=0.18,
        min_stable_dp_ratio=0.09,
        practical_min_throttle=0.55,
        atomization_time_modifier=0.90,
        relative_cost_factor=1.1,
        suited_pairs=(),
        stability_note="Symmetric 2-on-1 - eliminates the beta-vs-mixture-ratio variation "
                        "of a doublet. High performance, widely used.",
        symmetric_pattern=True,
        pattern_note="Two outer jets impinge symmetrically on one centre jet - "
                      "momentum-balanced, resultant beta ~0 at any MR.",
    ),
    "quintuplet": Injector(
        key="quintuplet",
        display_name="Quintuplet (4-on-1 quincunx)",
        eta_cstar_multiplier=1.02,
        dp_over_pc_nominal=0.20,
        min_stable_dp_ratio=0.10,
        practical_min_throttle=0.50,
        atomization_time_modifier=0.85,
        relative_cost_factor=1.3,
        suited_pairs=(),
        stability_note="4-on-1 symmetric - excellent mixing and performance.",
        symmetric_pattern=True,
        pattern_note="Four outer jets on one centre jet - highly symmetric, resultant "
                      "beta ~0.",
    ),
    "self_impinging": Injector(
        key="self_impinging",
        display_name="Self-impinging (like-on-like doublets)",
        eta_cstar_multiplier=1.00,
        dp_over_pc_nominal=0.18,
        min_stable_dp_ratio=0.09,
        practical_min_throttle=0.55,
        atomization_time_modifier=1.00,
        relative_cost_factor=1.0,
        suited_pairs=(),
        stability_note="Fuel-on-fuel and ox-on-ox pairs - good inherent stability, "
                        "moderate performance. Common on cryo + storable hypergolic.",
        symmetric_pattern=True,
        pattern_note="Each fan is one propellant impinging on itself; the two fans then "
                      "interdiffuse - no unlike impingement point, resultant beta ~0.",
    ),
    "coax_post": Injector(
        key="coax_post",
        display_name="Shear coaxial hollow post (GH2/LOX)",
        eta_cstar_multiplier=1.01,
        dp_over_pc_nominal=0.15,
        min_stable_dp_ratio=0.10,
        practical_min_throttle=0.50,
        atomization_time_modifier=0.75,
        relative_cost_factor=1.4,
        suited_pairs=("LOX/LH2",),
        stability_note="Concentric tubes: a fast gasified-H2 annulus shears a slow LOX "
                        "core. Dominant for LOX/GH2 (SSME, RS-68, Vulcain, LE-7).",
        dp_ox_over_fuel=1.9,   # LOX core needs a much stiffer feed than the H2 annulus
                                # ([Sutton Table 8-1]: RL10B-2 1.85, LE-7 ~4.6)
        pattern_note="No impingement - the gas annulus atomises the liquid core by shear. "
                      "'beta angle' does not apply.",
    ),
    "gas_centered_swirl": Injector(
        key="gas_centered_swirl",
        display_name="Gas-centered swirl (ORSC, RD-120/170/180/191-family)",
        # Reverse-solved (not hand-picked) so a full RD-180-parameter design with this
        # injector reproduces RD-180's real 338.4 s vacuum Isp - see validate.py's
        # run_gas_centered_swirl_injector_check(). Seed was the naive
        # eta_c*/DEFAULT_ETA_CSTAR ratio = 0.97/0.955 ~= 1.016 [Bazarov p.5-6 Table 3],
        # which is NOT itself the calibration (Bazarov's 0.97 is a sub-scale single-element
        # test article's own c* efficiency, not measured against the same RD-111 baseline
        # DEFAULT_ETA_CSTAR["LOX/RP-1"] is calibrated against).
        eta_cstar_multiplier=1.016,
        dp_over_pc_nominal=0.105,      # [Bazarov p.5-6 Table 3]: dP_ox=dP_fuel=226 psid at
                                        # Pc 2150 psia -> ~10.5% each leg - real ORSC data,
                                        # not an estimate (lower than the impinging norm
                                        # because this element is inherently stiffer)
        min_stable_dp_ratio=0.06,      # [Bazarov p.4]: the vortex-stabilised liquid film
                                        # gives this element the LOWEST chamber-pressure-
                                        # pulsation sensitivity of any type surveyed -
                                        # qualitative finding, not a specific number
        practical_min_throttle=0.47,   # RD-180's real "100% to 47%" [Engine_Configs/
                                        # RD180_Config.cfg] - NOTE this is really an ORSC-
                                        # cycle/ox-rich-turbine turndown limit, not a
                                        # property of the injector element itself; attached
                                        # here only because it's the sole per-type throttle
                                        # field the tool has
        atomization_time_modifier=0.75,  # thin rotating liquid film - comparable fineness
                                          # to coax_post/coaxial_swirl
        relative_cost_factor=1.6,      # [Bazarov p.4]: "most complex to size" of the
                                        # surveyed taxonomy
        suited_pairs=("LOX/RP-1",),    # [Bazarov]'s paper is LOX/RP-1-only (RD-170/180/191
                                        # family); NOT extended to LOX/CH4 (BE-4-class) -
                                        # that would be inference beyond the source
        stability_note="The RD-120/170/180/191 element: liquid fuel enters tangentially "
                        "into an open vortex chamber around a warm oxidiser-rich gas core. "
                        "The resulting rotating liquid film both atomises finely AND "
                        "passively cools/protects the injector face, and the gas cavity "
                        "acts as a Helmholtz-like acoustic resonator - the lowest "
                        "sensitivity to chamber-pressure pulsation of any element type "
                        "surveyed, but the most complex to size [Bazarov].",
        dp_ox_over_fuel=1.0,           # Bazarov's baseline design: both legs equal (226/226 psid)
        symmetric_pattern=True,        # no impingement point - same convention as coax_post
        pattern_note="No impingement - a tangentially-fed liquid film atomises off the "
                      "gas-core/vortex-chamber interface. 'Beta angle' does not apply.",
    ),
}


def available_injectors():
    return list(INJECTORS.keys())


def suitability_warning(injector_key, propellant_pair):
    inj = INJECTORS[injector_key]
    if inj.suited_pairs and propellant_pair not in inj.suited_pairs:
        return (f"{inj.display_name} is unusual for {propellant_pair}; it's typically used "
                f"for {', '.join(inj.suited_pairs)}. Efficiency numbers may be optimistic.")
    return None


# --- element-level hydraulics (Huzel eq. 4-39/4-40, Sutton eq. 8-1/8-2/8-5) ---
# Derived geometry for the new "Injectors" GUI tab: injection velocities,
# orifice count/diameter, per-element momentum ratio. Same epistemic status as
# the catalog above - the hydraulic RELATIONS are exact, the target velocities
# and Cd are standard-practice values, not calibrated. Spot-checked at the
# TYPE level in validate.py's run_injector_geometry_check() (F-1 element count,
# etc.).
CD_DEFAULT = 0.65                     # sharp-edged drilled orifice [Sutton Table 8-2]
# Discharge coefficient by orifice geometry [Sutton Table 8-2 p.279]. A rounded
# short tube passes far more flow for the same dP than a sharp-edged hole - so
# it needs a LOWER dP for a target injection velocity.
CD_BY_ORIFICE_TYPE = {
    "sharp_edged": 0.65,          # sharp-edged drilled hole < 2.5 mm (the original default)
    "sharp_large": 0.61,          # sharp-edged drilled hole > 2.5 mm
    "short_tube_rounded": 0.88,   # short tube, well-rounded entrance, L/D > 3
    "conical_entrance": 0.76,     # short tube, conical entrance
    "sharp_cone": 0.71,           # sharp-edged cone
}
INJECTION_VELOCITY_TARGET_MS = {      # representative liquid injection velocities
    "fuel": 22.0,                    #   [Huzel Sample 4-4 region; Sutton 8.1]
    "ox": 26.0,
}
IMPINGEMENT_ANGLE_BAND_DEG = (20.0, 45.0)  # satisfactory included angle [Huzel 4.5]
# Nominal orifice diameter scales with the injector type's atomization fineness
# (finer pattern -> smaller holes, more of them -> more surface area to vaporize).
# Base is an impinging-doublet figure: real large boosters run ~2-4 mm holes
# (F-1 ~6000 orifices at this flow), platelets run sub-mm. Illustrative, not
# calibrated - only the ORDER of the element count is spot-checked.
ORIFICE_DIA_BASE_MM = 2.6


def orifice_velocity_ms(dp_pa, rho_kg_m3, cd=CD_DEFAULT):
    """Jet velocity through an orifice at pressure drop dp: V = Cd*sqrt(2*dp/rho)
    [Huzel eq. 4-40 / Sutton eq. 8-1]."""
    if rho_kg_m3 <= 0 or dp_pa <= 0:
        return 0.0
    return cd * math.sqrt(2.0 * dp_pa / rho_kg_m3)


def derived_dp_pa(rho_kg_m3, target_velocity_ms, cd=CD_DEFAULT):
    """Pressure drop needed to inject at `target_velocity_ms`:
    dp = rho * V^2 / (2 * Cd^2)  [Huzel eq. 4-39]. Independent of Pc - so at
    low Pc this can exceed the catalog's dp_over_pc_nominal fraction, which is
    exactly why small/low-Pc engines run dp/Pc ~ 0.3-0.5 [Sutton Table 8-1]."""
    if rho_kg_m3 <= 0 or target_velocity_ms <= 0 or cd <= 0:
        return 0.0
    return rho_kg_m3 * target_velocity_ms ** 2 / (2.0 * cd ** 2)


def required_dp_pa(pc_pa, injector_key):
    """The catalog's nominal injector pressure drop: dp_over_pc_nominal * Pc."""
    return INJECTORS[injector_key].dp_over_pc_nominal * pc_pa


def cd_for_orifice(orifice_type):
    """Discharge coefficient for an orifice geometry key ([Sutton Table 8-2]);
    falls back to the sharp-edged default for an unknown key."""
    return CD_BY_ORIFICE_TYPE.get(orifice_type, CD_DEFAULT)


def dp_split(dp_total_pa, injector_key):
    """Split a single injector pressure drop into (fuel-leg, ox-leg) using the
    injector type's `dp_ox_over_fuel` ratio. The fuel leg keeps `dp_total_pa`
    (the historical single value) and the ox leg is scaled - so a ratio of 1.0
    returns (dp_total, dp_total) unchanged."""
    r = INJECTORS[injector_key].dp_ox_over_fuel
    return dp_total_pa, dp_total_pa * r


def beta_angle_deg(momentum_ratio, included_angle_deg, symmetric):
    """
    Resultant momentum-vector angle beta (deg) of an unlike-impinging element vs
    the chamber axis [Huzel eq. 4-41], reduced to a symmetric split: for two
    streams each at half the included angle from the axis,
        tan(beta) = ((Rm - 1) / (Rm + 1)) * tan(included/2)
    Positive beta points toward the wall. A symmetric pattern (triplet /
    quintuplet / self-impinging / showerhead) is momentum-balanced by
    construction -> beta = 0 at any mixture ratio.
    """
    if symmetric or momentum_ratio <= 0:
        return 0.0
    gamma = math.radians(included_angle_deg / 2.0)
    return math.degrees(math.atan((momentum_ratio - 1.0) / (momentum_ratio + 1.0)
                                   * math.tan(gamma)))


# Preferred resultant-beta bands by propellant class [Huzel 4.5 / claude_lit topic 05]:
# hypergolics like a small POSITIVE beta (2-5 deg) - wall recirculation aids
# liquid-phase mixing; cryogenics want a slightly NEGATIVE beta to avoid wall
# hot streaks (gaseous-phase mixing dominates).
_BETA_BAND_DEG = {
    "N2O4/MMH": (1.0, 6.0),
    "Aerozine-50/NTO": (1.0, 6.0),
    "LOX/LH2": (-4.0, 1.5),
    "LOX/CH4": (-3.0, 3.0),     # cryogenic gas/liquid, between hydrolox and kerolox
    "LOX/RP-1": (-2.0, 6.0),
    "Hydrazine": (-6.0, 6.0),   # monopropellant - not really impinging; wide band
    "H2O2": (-6.0, 6.0),        # monopropellant - not really impinging; wide band
}


def beta_warning(beta_deg, propellant_pair):
    """Warn (string) if the resultant beta angle is outside the band that
    propellant class prefers; None if it's fine or the pair is unlisted."""
    band = _BETA_BAND_DEG.get(propellant_pair)
    if band is None:
        return None
    lo, hi = band
    if lo <= beta_deg <= hi:
        return None
    want = ("a small positive beta (2-5 deg)" if lo >= 0
            else "a slightly negative beta (~0 or below)")
    return (f"Resultant injection beta angle {beta_deg:+.1f} deg is outside the "
            f"{lo:+.0f} to {hi:+.0f} deg band {propellant_pair} prefers - it wants "
            f"{want}. Adjust the impingement angle or element momentum ratio.")


def element_geometry(mdot_fuel_kgs, mdot_ox_kgs, rho_fuel, rho_ox, dp_pa, injector_key,
                      *, cd=CD_DEFAULT, dp_fuel_pa=None, dp_ox_pa=None,
                      included_angle_deg=30.0):
    """
    Derived injector element geometry at the given per-stream mass flows,
    densities and (actual) injector pressure drop.

    `dp_fuel_pa` / `dp_ox_pa` override the single `dp_pa` per leg (see
    dp_split()); `cd` is the orifice discharge coefficient (see cd_for_orifice()).
    Both default to the historical single-dP, sharp-edged behaviour.

    Returns a dict: per-stream injection velocities, orifice diameter and count,
    element (impinging-pair) count, per-element injection momentum ratio
    Rm = (mdot_ox*V_ox)/(mdot_fuel*V_fuel) [Huzel eq. 4-42], the resultant beta
    angle [Huzel eq. 4-41], the satisfactory impingement-angle band, and a
    per-type note.
    """
    inj = INJECTORS[injector_key]
    dpf = dp_pa if dp_fuel_pa is None else dp_fuel_pa
    dpo = dp_pa if dp_ox_pa is None else dp_ox_pa
    v_fuel = orifice_velocity_ms(dpf, rho_fuel, cd)
    v_ox = orifice_velocity_ms(dpo, rho_ox, cd)
    d_orifice_m = ORIFICE_DIA_BASE_MM * 1e-3 * inj.atomization_time_modifier
    a_orifice = math.pi * (d_orifice_m / 2.0) ** 2

    def n_orifices(mdot, rho, v):
        if v <= 0 or rho <= 0 or a_orifice <= 0:
            return 0
        a_total = mdot / (rho * v)          # total flow area to pass mdot at velocity v
        return max(1, round(a_total / a_orifice))

    n_fuel = n_orifices(mdot_fuel_kgs, rho_fuel, v_fuel)
    n_ox = n_orifices(mdot_ox_kgs, rho_ox, v_ox)
    n_elements = max(1, round((n_fuel + n_ox) / 2.0))
    rm = ((mdot_ox_kgs * v_ox) / (mdot_fuel_kgs * v_fuel)
          if mdot_fuel_kgs > 0 and v_fuel > 0 else 0.0)
    beta_deg = beta_angle_deg(rm, included_angle_deg, inj.symmetric_pattern)

    if inj.pattern_note:
        note = inj.pattern_note
    elif injector_key == "pintle":
        note = ("annular pintle slot, not discrete orifices - counts are "
                "equivalent-orifice figures for the same flow area")
    elif injector_key == "catalyst_bed":
        note = "catalyst bed (monopropellant decomposition), not an orifice pattern"
    elif injector_key == "coaxial_swirl":
        note = ("shear-coaxial: the fuel (gas) side really injects far faster than "
                "this liquid-velocity estimate - fuel figures are indicative only")
    else:
        note = f"{2 * n_elements} orifices in ~{n_elements} impinging pairs"

    return {
        "v_fuel_ms": v_fuel,
        "v_ox_ms": v_ox,
        "orifice_dia_mm": d_orifice_m * 1e3,
        "n_fuel_orifices": n_fuel,
        "n_ox_orifices": n_ox,
        "n_elements": n_elements,
        "momentum_ratio": rm,
        "beta_deg": beta_deg,
        "symmetric_pattern": inj.symmetric_pattern,
        "impingement_angle_band_deg": IMPINGEMENT_ANGLE_BAND_DEG,
        "included_angle_deg": included_angle_deg,
        "cd": cd,
        "note": note,
    }


if __name__ == "__main__":
    # Headless smoke test - hydraulics only, no GUI.
    # F-1-class: mdot ~2580 kg/s total, MR 2.27, LOX/RP-1, Pc 7 MPa, impinging.
    mdot = 2580.0
    mr = 2.27
    mdot_f = mdot / (1.0 + mr)
    mdot_o = mdot - mdot_f
    dp = required_dp_pa(7.0e6, "impinging")
    geo = element_geometry(mdot_f, mdot_o, 810.0, 1141.0, dp, "impinging")
    assert 15.0 < geo["v_fuel_ms"] < 80.0, geo["v_fuel_ms"]
    assert 15.0 < geo["v_ox_ms"] < 80.0, geo["v_ox_ms"]
    # F-1 really had ~6000 orifices / a few thousand elements - order of magnitude.
    assert 1000 < geo["n_elements"] < 25000, geo["n_elements"]
    assert 0.3 < geo["momentum_ratio"] < 4.0, geo["momentum_ratio"]

    # derived_dp is Pc-independent; at low Pc it exceeds the nominal fraction.
    dp_lo_flat = required_dp_pa(1.0e6, "impinging")
    dp_lo_derived = derived_dp_pa(810.0, INJECTION_VELOCITY_TARGET_MS["fuel"])
    assert dp_lo_derived > dp_lo_flat, (dp_lo_derived, dp_lo_flat)

    for key in available_injectors():
        g = element_geometry(mdot_f, mdot_o, 810.0, 1141.0,
                              required_dp_pa(5.0e6, key), key)
        assert g["n_elements"] >= 1 and g["note"]

    # --- I1: Cd by orifice type + split fuel/ox dP ---
    assert cd_for_orifice("sharp_edged") == 0.65 and cd_for_orifice("short_tube_rounded") == 0.88
    assert cd_for_orifice("unknown") == CD_DEFAULT
    # a rounded short tube needs LESS dP for the same target velocity
    assert derived_dp_pa(810.0, 22.0, cd_for_orifice("short_tube_rounded")) < \
           derived_dp_pa(810.0, 22.0, cd_for_orifice("sharp_edged"))
    f_dp, o_dp = dp_split(1.0e6, "impinging")
    assert f_dp == o_dp == 1.0e6                       # ratio 1.0 -> unchanged
    f_dp, o_dp = dp_split(1.0e6, "coax_post")
    assert o_dp > f_dp == 1.0e6                        # ox leg stiffer

    # --- I2: pattern subtypes + beta angle ---
    assert "unlike_triplet" in INJECTORS and INJECTORS["unlike_triplet"].symmetric_pattern
    g_sym = element_geometry(mdot_f, mdot_o, 810.0, 1141.0, required_dp_pa(7e6, "unlike_triplet"),
                              "unlike_triplet")
    assert abs(g_sym["beta_deg"]) < 1e-9              # symmetric -> beta 0
    g_dbl = element_geometry(mdot_f, mdot_o, 810.0, 1141.0, required_dp_pa(7e6, "impinging"),
                              "impinging", included_angle_deg=30.0)
    assert g_dbl["beta_deg"] != 0.0                   # unlike doublet at Rm != 1
    assert beta_warning(8.0, "LOX/LH2") is not None and beta_warning(0.0, "LOX/LH2") is None
    assert beta_warning(3.0, "N2O4/MMH") is None and beta_warning(0.0, "N2O4/MMH") is not None

    print(f"injectors.py smoke test OK - F-1-class impinging: {geo['n_elements']} elements, "
          f"V_fuel {geo['v_fuel_ms']:.0f} m/s, V_ox {geo['v_ox_ms']:.0f} m/s, "
          f"Rm {geo['momentum_ratio']:.2f}, beta {g_dbl['beta_deg']:+.1f} deg, "
          f"orifice {geo['orifice_dia_mm']:.2f} mm; {len(INJECTORS)} patterns")
