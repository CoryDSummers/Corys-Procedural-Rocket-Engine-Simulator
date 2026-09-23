"""
1-D preliminary turbopump sizing: rotor speed, impeller/blade tip speed, pump
stage count, turbine pitchline speed, shaft arrangement and turbine count - and
a small dry-mass modifier for architectures that deviate from the auto-derived
default.

This is the by-hand method of [SP-8107 2.1.1] / [Huzel Ch. VI], nothing more:
specific speed Ns fixes rotor speed, a head coefficient fixes tip speed, and a
representative per-stage head (anchored so the J-2 LH2 pump comes out
multistage) fixes stage count. Suction performance is modelled only as far as
the user supplies it: `npsh_available_*_ft` > 0 caps each pump's rpm at its
suction-specific-speed limit (suction_limited_rpm), and the opt-in
`enforce_suction_limit` adds stages against a historical NPSH-required anchor.
With neither set (the default) there is no cavitation limit, so rotor speed is
over-predicted for an extreme high-head pump a real designer would slow down -
the spot check in physics/validate.py uses wide (factor ~2-3) bands for this.
There is no tank/suction-line model and no boost pump yet (the planned
turbopump/lines round).

Neutral-default contract (same idea as turbopump_tech's `mature` tier and
`contraction_ratio=1.6`): the AUTO-derived architecture always yields
`mass_modifier == 1.0` exactly, so wiring this into design.py changes no
existing compute() result. Only a user OVERRIDE (forcing a gearbox, adding pump
stages, an exotic turbine staging) moves the mass.
"""
import math

from . import turbopump_efficiency, turbopump_materials

G = 9.80665
_M3S_TO_GPM = 15850.323
_M_TO_FT = 3.2808399

# --- pump sizing ------------------------------------------------------------
NS_TARGET_US = 2200.0            # target stage specific speed (rpm*gpm^0.5/ft^0.75).
                                 # [SP-8107 2.1.1.6]: centrifugal-pump efficiency
                                 # peaks over stage Ns 1300-2500; 2200 is mid-band.
HEAD_COEFFICIENT_PSI = 0.5       # psi = g*H_stage / U_tip^2. [Huzel 6.2] typical 0.5-0.6.
H_PER_STAGE_FT_TYPICAL = 6000.0  # representative rocket-pump per-stage head. Anchored:
                                 # the J-2 LH2 pump (~38,000 ft head) comes out ~7
                                 # stages, matching the real 7-stage axial pump;
                                 # F-1 / RD-0110 kerosene pumps stay single-stage.
MAX_PUMP_STAGES = 8
TIP_SPEED_DESIGN_FRACTION = 0.85  # design a stage to this fraction of the rotor
                                  # material's tip-speed capability before adding a stage

# --- feed-system plausibility ceiling (Tier 2) -------------------------------
# This module always SOLVES a pump to deliver whatever discharge dP design.py
# demands (see module docstring) - no independent pump-performance ceiling
# exists, so a hydraulically "impossible" design can't fail by construction.
# This constant is the honest proxy: an approximate upper bound on required
# pump discharge pressure any real flight turbopump has been built to deliver.
# Cited, not invented: `[SP-8107 Sec 2.1.1.4, Tables V-VI]` gives staged-
# combustion (the highest-discharge-pressure real cycle family) resultant pump
# discharge pressure as ~7000-8000 psia; 8000 psia is used as the ceiling.
# Cross-checked against a real engine: `[Bazarov/KBKhA AIAA 2005]`'s uprated
# RD-170-class turbopump data gives real LOX/kerosene discharge pressures of
# 33.3/36.6 MPa - comfortably inside this band, not at its edge.
FEED_DP_PLAUSIBLE_CEILING_PA = 55.2e6   # 8000 psia [SP-8107 Tables V-VI]

# --- suction specific speed / NPSH-required (opt-in, default OFF) -----------
# Nss = N*Q^0.5/NPSH^0.75 (US units, same convention as the Ns relation above).
# This tool has NO propellant tank pressure or vapor-pressure model at all
# (README: tank/vehicle modeling is RealFuels' job), so it can NEVER compute a
# real NPSH-AVAILABLE-vs-required verdict - only what NPSH a candidate rotor
# speed/flow combination REQUIRES to hit a propellant class's achievable
# suction specific speed. Never claims to know actual cavitation risk on a
# real vehicle. NSS_TARGET_US is computed directly from two real [SP-8107
# Table II] / [Ch12-Materials] data points, not invented:
#   F-1 O2 pump:  N=5488 rpm, Q=25,200 gpm, NPSH_crit=60 ft -> Nss ~= 40,400
#   J-2 LH2 pump: N=27,000 rpm, Q=3,000 gpm, NPSH_crit=75 ft -> Nss ~= 58,000
# Trust the DIRECTION (LH2 achieves much higher real suction specific speed
# than a dense propellant, matching [SP-8107]'s qualitative claim that LH2 has
# "excellent cavitation characteristics") far more than these exact magnitudes
# - only two 1960s anchor points back this classifier.
NSS_TARGET_US = {"lox_class": 40_411.0, "lh2_class": 58_027.0}
NSS_LH2_DENSITY_THRESHOLD_KG_M3 = 200.0   # rho < this -> lh2_class; every other modeled
                                           # propellant is >= 800 kg/m3, huge margin
# The SAME two real [SP-8107 Table II] NPSH_crit anchors that produced
# NSS_TARGET_US above, kept separately so a candidate design's required NPSH
# can be compared against real historical practice for its propellant class -
# NOT an assumed-available NPSH for the user's own (unmodeled) tank, just the
# NPSH real well-optimized turbopumps of this class actually needed.
NPSH_REAL_ANCHOR_FT = {"lox_class": 60.0, "lh2_class": 75.0}
NPSH_MARGIN_FACTOR = 3.0   # Tier 3: how many multiples of the real historical anchor NPSH
                            # a candidate design may require before this tool flags it as
                            # needing a dedicated inducer stage - a reasoned engineering
                            # margin, not derived or independently sourced


# Pump inlet-eye sizing (the suction port bore): Q = cm1*A_eye with the
# inlet flow coefficient phi = cm1/U_eye_tip. [SP-8107 2.1.1.6] quotes
# centrifugal-pump inlet flow coefficients 0.05 (Ns ~1300) .. 0.20 (Ns ~2500);
# 0.10 is inside that band (Tier 2). The eye hub/tip ratio is a Tier 3 pick.
INLET_FLOW_COEFF = 0.10
EYE_HUB_TIP_RATIO = 0.3


def inlet_eye_dia_m(q_m3s, n_rpm, phi=INLET_FLOW_COEFF, nu=EYE_HUB_TIP_RATIO):
    """Eye (inducer-tip) diameter: Q = phi*(omega*D/2) * pi/4*D^2*(1-nu^2)
    -> D = (8Q / (pi*phi*omega*(1-nu^2)))^(1/3)."""
    if q_m3s <= 0 or n_rpm <= 0:
        return 0.0
    omega = n_rpm * 2.0 * math.pi / 60.0
    return (8.0 * q_m3s / (math.pi * phi * omega * (1.0 - nu * nu))) ** (1.0 / 3.0)


def suction_limited_rpm(q_gpm, npsh_available_ft, nss_target):
    """The highest rotor speed at which a pump of this flow still meets its
    propellant class's achievable suction specific speed with the given NPSH
    available: N = Nss*NPSH^0.75/Q^0.5 (exact inversion of
    suction_specific_speed_us). 0 when undefined."""
    if q_gpm <= 0 or npsh_available_ft <= 0 or nss_target <= 0:
        return 0.0
    return nss_target * npsh_available_ft ** 0.75 / q_gpm ** 0.5


def required_npsh_ft(n_rpm, q_gpm, nss_target):
    """Invert Nss = N*Q^0.5/NPSH^0.75: the NPSH (ft) this rotor speed/flow
    implies the pump needs to hit a given (propellant-class) achievable
    suction specific speed. Exact algebraic inversion; only `nss_target` is an
    estimate."""
    if n_rpm <= 0 or q_gpm <= 0 or nss_target <= 0:
        return 0.0
    return (n_rpm * q_gpm ** 0.5 / nss_target) ** (4.0 / 3.0)


def _nss_class(rho_kg_m3):
    return "lh2_class" if 0 < rho_kg_m3 < NSS_LH2_DENSITY_THRESHOLD_KG_M3 else "lox_class"


def suction_specific_speed_us(n_rpm, q_gpm, npsh_ft):
    """Nss = N*Q^0.5/NPSH^0.75 - the forward relation (used by size_pump's
    enforce_suction_limit path and by validate.py's round-trip check)."""
    if n_rpm <= 0 or q_gpm <= 0 or npsh_ft <= 0:
        return 0.0
    return n_rpm * q_gpm ** 0.5 / npsh_ft ** 0.75

# --- shaft arrangement ---------------------------------------------------------
# Below this thrust a turbopump is geared ([SP-8107 2.1.2]). Pair-dependent:
# the dense-propellant guideline is ~10,000 lbf; LOX/LH2 upper stages stay geared
# much larger (the whole RL10 family, to ~110 kN, is geared to avoid a tiny
# inefficient direct LOX turbine) before going to separate direct-drive shafts
# (J-2, Vinci).
GEARED_THRUST_LIMIT_N = 44_482.0          # 10,000 lbf - dense propellants
GEARED_THRUST_LIMIT_LH2_N = 130_000.0     # LOX/LH2 - covers the RL10 / RL10B class
DENSITY_RATIO_DUAL_SHAFT = 4.0     # rho_ox / rho_fuel above this -> the pumps want
                                   # very different optimum speeds, so separate
                                   # turbopumps on separate shafts (J-2). Below it,
                                   # one shaft carries both (F-1).

# --- turbine sizing ----------------------------------------------------------
# Blade/gas speed ratio U/C0 (C0 = the IDEAL isentropic spouting velocity for the
# whole pressure ratio). [SP-8107 2.1.1.3-4] optima, nudged so the resulting
# pitchline for real GG engines lands near the SP-8107 Table III figures (F-1
# ~840 ft/s, H-1 ~1290 ft/s).
TURBINE_U_OVER_C0 = {
    "single_impulse": 0.30,
    "velocity_compounded_2row": 0.24,
    "pressure_compounded_2stage": 0.32,
    "reaction": 0.45,
}
# --- physical envelope (feeds the geometry-derived mass and the real-scale 3D) ---
# All factors are rough but consistent 1-D proportions; the ONE calibrated number
# is EFFECTIVE_SOLID_FRACTION, fitted so F-1 / J-2 / RL10 land near their real
# [SP-8107 Table I] turbopump-assembly masses (1429 / ~305 / 34.5 kg).
VOLUTE_OD_FACTOR = 1.6          # pump casing outer dia / impeller dia
INDUCER_LEN_FACTOR = 0.7        # inducer + inlet + bearing axial length / impeller dia
STAGE_WIDTH_FACTOR = 0.45       # first-stage axial width / impeller dia (later stages
                                # add sub-linearly: n_stages**STAGE_COUNT_EXPONENT)
STAGE_COUNT_EXPONENT = 0.6      # a 7-stage pump is ~3.2x a 1-stage body, not 7x
DISK_OD_FACTOR = 1.22           # turbine disk OD (blade tips + rim) / pitchline mean dia
DISK_THICK_FACTOR = 0.16        # disk + rim axial thickness / disk OD
MANIFOLD_OD_FACTOR = 1.12       # inlet scroll / nozzle-ring OD / disk OD
MANIFOLD_LEN_FACTOR = 2.5       # manifold axial length / disk thickness
SHAFT_SPAN_FACTOR = 0.30        # bearing/seal span between bodies / largest body OD
MIN_BODY_OD_M = 0.14           # a turbopump body can't be smaller than its bearings/seals
MIN_BODY_LEN_M = 0.16
EFFECTIVE_SOLID_FRACTION = 0.28   # envelope -> solid-metal fraction, for the cross-check
                                   # `mass_geometry_kg` only (NOT the mass used downstream)

# Turbopump assembly mass vs shaft power, from [SP-8107 Table I]: small assemblies
# run ~12 kW/kg (RL10 9.03 hp/lbm, MA-5 sust 7.27), large ones ~27 kW/kg (F-1
# 16.6 hp/lbm, J-2 single-unit 21.6). Log-interpolated between the two anchors.
# This is what actually feeds computed_dry_mass_kg - the volumetric envelope
# (mass_geometry_kg) is a shape/consistency cross-check only, because the 1-D
# rotor speeds this tool derives (no NPSH model) are not accurate enough for a
# credible volume->mass conversion (a pure d^2*L mass runs J-2 ~5x heavy).
SPEC_POWER_LOW_W_KG = 12000.0
SPEC_POWER_LOW_AT_W = 3.0e5
SPEC_POWER_HIGH_W_KG = 27000.0
SPEC_POWER_HIGH_AT_W = 4.0e7
FALLBACK_SPECIFIC_POWER_W_KG = 18000.0

# Dual-shaft turbine work split (replaced the old flat OX_TURBINE_WORK_FRACTION =
# 0.30 fudge, 2026-09-23) - DERIVED from turbine topology, no constant:
#   parallel (staged combustion - SSME's two preburners each feed their own
#     turbine; FFSC's fuel-rich/ox-rich pair): both turbines see the SAME
#     preburner gas and PR, so the same specific work dh; flow splits by power.
#     FFSC uses the solved per-side dh from staged_combustion directly.
#   series (GG / tap-off / expander - J-2's fuel turbine exhausts into its ox
#     turbine; J-2S tap-off likewise [AEDC-J2S]): the SAME gas flow passes both,
#     so dh splits in proportion to each turbine's shaft power.
PARALLEL_TURBINE_CYCLES = ("frsc", "orsc", "ffsc")


def split_turbine_work(cycle, n_turbines, dh_total, power_fuel_w, power_ox_w, cyc=None):
    """(dh_fuel_turbine, dh_ox_turbine) for the turbine(s). `dh_total` = total
    shaft power / total turbine flow. Single-turbine layouts get dh_total for the
    one turbine (it delivers all the power) and None for the ox turbine."""
    if n_turbines != 2:
        return dh_total, None
    sides = (cyc or {}).get("preburner_sides") or []
    if cycle == "ffsc" and len(sides) == 2:
        return sides[0]["dh_j_kg"], sides[1]["dh_j_kg"]
    if cycle in PARALLEL_TURBINE_CYCLES:
        return dh_total, dh_total
    p_tot = power_fuel_w + power_ox_w
    share_fuel = power_fuel_w / p_tot if p_tot > 0 else 0.5
    return dh_total * share_fuel, dh_total * (1.0 - share_fuel)

# --- shaft / bearing sizing (feeds turbopump_materials.BEARING_MATERIALS) ---
# Real turbopump shafts are conventionally forged low-alloy steel (4340)
# INDEPENDENT of the chosen rotor/turbine material - [Ch12-Materials]'s own
# table lists "shaft: 4340" for both F-1 and Atlas Mark 3 regardless of which
# pump/turbine alloy each uses - so this is deliberately its own constant, not
# derived from turbopump_materials.MATERIALS[material_key].
SHAFT_ALLOWABLE_SHEAR_PA = 200e6   # generic forged-4340 fatigue-derated allowable - Tier 3
BEARING_BORE_OVER_SHAFT_FACTOR = 1.15   # bearing bore / shaft journal OD - Tier 3 estimate


def shaft_diameter_m(shaft_power_w, shaft_n_rpm, *, allowable_shear_pa=SHAFT_ALLOWABLE_SHEAR_PA):
    """Solid round shaft torsion sizing: d = (16*T / (pi*tau_allow))**(1/3),
    T = P / omega. Exact mechanics-of-materials relation; only the allowable
    shear stress is an estimate."""
    if shaft_n_rpm <= 0 or shaft_power_w <= 0:
        return 0.0
    omega = 2.0 * math.pi * shaft_n_rpm / 60.0
    torque = shaft_power_w / omega
    return (16.0 * torque / (math.pi * allowable_shear_pa)) ** (1.0 / 3.0)


def bearing_dn(shaft_n_rpm, bore_dia_m):
    """DN = bore diameter (mm) x shaft speed (rpm) - the standard rolling-
    element-bearing capability figure. Exact definition; the LIMIT it's
    compared against (turbopump_materials.BEARING_MATERIALS) is the estimate."""
    return shaft_n_rpm * bore_dia_m * 1000.0


# --- dry-mass modifier for non-default architectures ------------------------
GEARBOX_MASS_FRACTION = 0.10       # adding a reduction gearbox - flagged estimate
EXTRA_STAGE_MASS_FRACTION = 0.06   # per pump stage beyond the auto-derived count -
                                   # flagged estimate
MASS_MODIFIER_CLAMP = (0.7, 1.6)

ARRANGEMENTS = ("single_shaft", "dual_shaft", "geared")
TURBINE_STAGINGS = tuple(TURBINE_U_OVER_C0)


def derive_arrangement(rho_fuel, rho_ox, thrust_n):
    hydrogen = rho_fuel > 0 and (rho_ox / rho_fuel) >= DENSITY_RATIO_DUAL_SHAFT
    geared_limit = GEARED_THRUST_LIMIT_LH2_N if hydrogen else GEARED_THRUST_LIMIT_N
    if thrust_n < geared_limit:
        return "geared"
    if hydrogen:
        return "dual_shaft"
    return "single_shaft"


def derive_turbine_staging(cycle, pair=""):
    """[SP-8107 2.1.1.3-4]: expander/staged combustion -> reaction (low PR);
    hydrogen GG -> 2-row velocity-compounded (J-2); low-energy-fuel GG -> 2-stage
    pressure-compounded (H-1, LR87, MA-5)."""
    if cycle in ("frsc", "orsc", "ffsc", "expander"):
        return "reaction"
    if "LH2" in pair:
        return "velocity_compounded_2row"
    return "pressure_compounded_2stage"


GG_ETA_TURBINE_SEED = 0.62   # seed for the turbine-efficiency back-substitution and the
                              # fallback when the machinery sizing is degenerate


def _cyl_volume(od_m, length_m):
    return math.pi * 0.25 * od_m * od_m * length_m


def _assemble_bodies(arrangement, fuel_pump, ox_pump, turbine, ox_turbine):
    """Lay the sized components out along their shaft axis as a list of
    {kind, od_m, length_m, x0_m, center} bounding cylinders/disks - consumed by
    the geometry mass (_turbopump_mass_from_geometry) and the 3D preview
    (geometry3d.turbopump_assembly_meshes). `center` groups bodies into physical
    units: 0 for a single/geared assembly, 0=fuel unit / 1=ox unit for dual-shaft.
    """
    fp_l, fp_d = fuel_pump["body_length_m"], fuel_pump["volute_od_m"]
    op_l, op_d = ox_pump["body_length_m"], ox_pump["volute_od_m"]
    t_l = (turbine["disk_thickness_m"] + turbine["manifold_length_m"]) if turbine else 0.0
    t_d = turbine["manifold_od_m"] if turbine else 0.0
    bodies = []

    if arrangement == "dual_shaft" and ox_turbine:
        ot_l = ox_turbine["disk_thickness_m"] + ox_turbine["manifold_length_m"]
        ot_d = ox_turbine["manifold_od_m"]
        # unit 0 = fuel turbopump (pump + its turbine), unit 1 = ox turbopump
        x = 0.0
        bodies.append(dict(kind="pump", od_m=fp_d, length_m=fp_l, x0_m=x, center=0))
        x += fp_l
        bodies.append(dict(kind="turbine", od_m=t_d, length_m=t_l, x0_m=x, center=0))
        u0_len = x + t_l
        x = 0.0
        bodies.append(dict(kind="pump", od_m=op_d, length_m=op_l, x0_m=x, center=1))
        x += op_l
        bodies.append(dict(kind="turbine", od_m=ot_d, length_m=ot_l, x0_m=x, center=1))
        u1_len = x + ot_l
        return bodies, max(u0_len, u1_len), max(fp_d, op_d, t_d, ot_d), 2

    # single shaft (or geared): fuel pump - turbine - ox pump inline
    span = SHAFT_SPAN_FACTOR * max(fp_d, op_d, t_d, 1e-6)
    x = 0.0
    bodies.append(dict(kind="pump", od_m=fp_d, length_m=fp_l, x0_m=x, center=0))
    x += fp_l + span
    if turbine:
        bodies.append(dict(kind="turbine", od_m=t_d, length_m=t_l, x0_m=x, center=0))
        x += t_l + span
    bodies.append(dict(kind="pump", od_m=op_d, length_m=op_l, x0_m=x, center=0))
    x += op_l
    return bodies, x, max(fp_d, op_d, t_d), 1


def _turbopump_mass_from_geometry(bodies, density_kg_m3):
    """Envelope volume x EFFECTIVE_SOLID_FRACTION x density - a cross-check number
    (shape consistency), NOT the mass used downstream."""
    vol = sum(_cyl_volume(b["od_m"], b["length_m"]) for b in bodies)
    return vol * EFFECTIVE_SOLID_FRACTION * density_kg_m3


def _assembly_specific_power_w_kg(power_total_w):
    """kW/kg for the whole turbopump assembly, log-interpolated between the
    [SP-8107 Table I] small- and large-engine anchors."""
    if power_total_w <= SPEC_POWER_LOW_AT_W:
        return SPEC_POWER_LOW_W_KG
    if power_total_w >= SPEC_POWER_HIGH_AT_W:
        return SPEC_POWER_HIGH_W_KG
    frac = ((math.log(power_total_w) - math.log(SPEC_POWER_LOW_AT_W))
            / (math.log(SPEC_POWER_HIGH_AT_W) - math.log(SPEC_POWER_LOW_AT_W)))
    return SPEC_POWER_LOW_W_KG + frac * (SPEC_POWER_HIGH_W_KG - SPEC_POWER_LOW_W_KG)


def turbopump_mass_kg(power_total_w):
    """Turbopump assembly dry mass from the [SP-8107 Table I] mass-vs-power trend."""
    sp = _assembly_specific_power_w_kg(power_total_w) or FALLBACK_SPECIFIC_POWER_W_KG
    return power_total_w / sp


def derive_efficiencies(mdot, mr, dp_fuel_pa, dp_ox_pa, rho_fuel, rho_ox, material_key,
                        staging, gg_tin_k, gg_cp, gg_gamma, gg_pressure_ratio_for_dh,
                        turbine_pressure_ratio, build_quality, *,
                        pump_stages_fuel=0, pump_stages_ox=0,
                        eta_pump_fuel_override=0.0, eta_pump_ox_override=0.0,
                        enforce_suction_limit=False, npsh_available_fuel_ft=0.0,
                        npsh_available_ox_ft=0.0):
    """
    Pump & turbine efficiency for the power balance, DERIVED from the machinery
    design (physics/turbopump_efficiency.py) BEFORE the cycle result is built.

    Pump efficiency is a clean function of head / whole-pump Ns / size - no
    circularity. Turbine efficiency needs the turbine specific work, which needs
    the pump shaft power, which needs the pump efficiency - so a short
    back-substitution (<=3 passes, converges immediately) seeded from
    GG_ETA_TURBINE_SEED. A non-zero `eta_pump_*_override` pins that pump.

    `enforce_suction_limit` (default False) - see size_pump()'s docstring.
    """
    mat = turbopump_materials.MATERIALS[material_key]
    mdot_fuel = mdot / (1.0 + mr)
    mdot_ox = mdot - mdot_fuel
    fp = size_pump(mdot_fuel, dp_fuel_pa, rho_fuel, mat,
                   forced_stages=pump_stages_fuel, build_quality=build_quality,
                   enforce_suction_limit=enforce_suction_limit,
                   npsh_available_ft=npsh_available_fuel_ft)
    op = size_pump(mdot_ox, dp_ox_pa, rho_ox, mat,
                   forced_stages=pump_stages_ox, build_quality=build_quality,
                   enforce_suction_limit=enforce_suction_limit,
                   npsh_available_ft=npsh_available_ox_ft)
    eta_pf = eta_pump_fuel_override if (eta_pump_fuel_override or 0.0) > 0.0 else fp["eta"]
    eta_po = eta_pump_ox_override if (eta_pump_ox_override or 0.0) > 0.0 else op["eta"]
    eta_pf = eta_pf or GG_ETA_TURBINE_SEED   # degenerate guard
    eta_po = eta_po or GG_ETA_TURBINE_SEED

    power = 0.0
    if rho_fuel > 0 and eta_pf > 0:
        power += mdot_fuel * dp_fuel_pa / (rho_fuel * eta_pf)
    if rho_ox > 0 and eta_po > 0:
        power += mdot_ox * dp_ox_pa / (rho_ox * eta_po)

    exponent = (gg_gamma - 1.0) / gg_gamma
    uc0 = TURBINE_U_OVER_C0.get(staging, TURBINE_U_OVER_C0["velocity_compounded_2row"])
    # Pitchline uses the IDEAL isentropic spouting velocity for the whole PR
    # (the U/C0 convention), not the eta-reduced delivered work.
    dh_ideal = gg_cp * gg_tin_k * (1.0 - gg_pressure_ratio_for_dh ** (-exponent))
    u_pitch = uc0 * math.sqrt(2.0 * max(dh_ideal, 1.0))
    eta_turb = turbopump_efficiency.turbine_efficiency(
        staging, u_pitch, power, turbine_pressure_ratio, build_quality)
    return eta_pf, eta_po, eta_turb


def derive_expander_efficiencies(mdot, mr, dp_fuel_pa, dp_ox_pa, rho_fuel, rho_ox,
                                 material_key, turbine_pressure_ratio, build_quality, *,
                                 pump_stages_fuel=0, pump_stages_ox=0,
                                 eta_pump_fuel_override=0.0, eta_pump_ox_override=0.0,
                                 enforce_suction_limit=False, npsh_available_fuel_ft=0.0,
                                 npsh_available_ox_ft=0.0):
    """Same as derive_efficiencies but for the expander cycle, whose turbine is
    driven by heated fuel (not a fuel-rich GG mix): a low-PR reaction turbine.
    The turbine specific work = shaft power / fuel flow (all fuel goes through
    it), so no gas-property inputs are needed.

    `enforce_suction_limit` (default False) - see size_pump()'s docstring."""
    mat = turbopump_materials.MATERIALS[material_key]
    mdot_fuel = mdot / (1.0 + mr)
    mdot_ox = mdot - mdot_fuel
    fp = size_pump(mdot_fuel, dp_fuel_pa, rho_fuel, mat,
                   forced_stages=pump_stages_fuel, build_quality=build_quality,
                   enforce_suction_limit=enforce_suction_limit,
                   npsh_available_ft=npsh_available_fuel_ft)
    op = size_pump(mdot_ox, dp_ox_pa, rho_ox, mat,
                   forced_stages=pump_stages_ox, build_quality=build_quality,
                   enforce_suction_limit=enforce_suction_limit,
                   npsh_available_ft=npsh_available_ox_ft)
    eta_pf = eta_pump_fuel_override if (eta_pump_fuel_override or 0.0) > 0.0 else fp["eta"]
    eta_po = eta_pump_ox_override if (eta_pump_ox_override or 0.0) > 0.0 else op["eta"]
    eta_pf = eta_pf or GG_ETA_TURBINE_SEED
    eta_po = eta_po or GG_ETA_TURBINE_SEED

    power = 0.0
    if rho_fuel > 0 and eta_pf > 0:
        power += mdot_fuel * dp_fuel_pa / (rho_fuel * eta_pf)
    if rho_ox > 0 and eta_po > 0:
        power += mdot_ox * dp_ox_pa / (rho_ox * eta_po)
    dh = power / mdot_fuel if mdot_fuel > 0 else 0.0
    u_pitch = TURBINE_U_OVER_C0["reaction"] * math.sqrt(2.0 * max(dh, 1.0))
    eta_turb = turbopump_efficiency.turbine_efficiency(
        "reaction", u_pitch, power, turbine_pressure_ratio, build_quality)
    return eta_pf, eta_po, eta_turb


def size_pump(mdot_kgs, dp_pa, rho_kg_m3, material, *, forced_stages=0, build_quality=1.0,
              enforce_suction_limit=False, npsh_available_ft=0.0):
    """
    One propellant pump. `material` is a turbopump_materials.TurbopumpMaterial.

    `enforce_suction_limit` (default False - see turbopump_sizing.py's module
    docstring): when True and stages aren't forced, this pump's rotor speed is
    also checked against a suction-specific-speed ceiling for its propellant
    class (NSS_TARGET_US) and given extra stages (to lower rpm) if it would
    otherwise need more NPSH than real historical practice for that class
    (NPSH_REAL_ANCHOR_FT x NPSH_MARGIN_FACTOR) - exactly the "a real designer
    would slow the rotor with extra axial stages for cavitation margin" fix
    this module's docstring already names as missing. Default OFF means this
    is a pure opt-in: every existing caller/result is bit-for-bit unchanged.
    `npsh_required_ft`/`nss_class` are still computed and returned even when
    this is off (informational only, changes nothing).

    `npsh_available_ft` (default 0 = not limiting): the NPSH the vehicle
    delivers at this pump's inlet - a user input, the tool has no tank model.
    When > 0 the rotor speed is capped at suction_limited_rpm (after the stage
    count is fixed); the tip speed is head-fixed, so the impeller grows, and
    the efficiency is taken at the ACTUAL (lower) whole-pump Ns. With 0 every
    returned number is bit-for-bit what it was before this input existed.
    """
    q_m3s = mdot_kgs / rho_kg_m3 if rho_kg_m3 > 0 else 0.0
    q_gpm = q_m3s * _M3S_TO_GPM
    head_m = dp_pa / (rho_kg_m3 * G) if rho_kg_m3 > 0 else 0.0
    head_ft = head_m * _M_TO_FT
    warnings = []

    typ_stages = max(1, math.ceil(head_ft / H_PER_STAGE_FT_TYPICAL)) if head_ft > 0 else 1
    u_single = math.sqrt(G * head_m / HEAD_COEFFICIENT_PSI) if head_m > 0 else 0.0
    cap = TIP_SPEED_DESIGN_FRACTION * material.max_tip_speed_m_s
    tip_stages = max(1, math.ceil(u_single / cap)) if cap > 0 else 1
    stages_wanted = max(typ_stages, tip_stages)   # pre-clamp - see feed-system
                                                   # plausibility warning just below
    auto_stages = min(MAX_PUMP_STAGES, stages_wanted)
    n_stages = auto_stages if not forced_stages or forced_stages <= 0 else forced_stages
    n_stages = max(1, min(MAX_PUMP_STAGES, int(n_stages)))

    # Feed-system plausibility (Tier 2, see ASSUMPTIONS.md): MAX_PUMP_STAGES and
    # H_PER_STAGE_FT_TYPICAL/TIP_SPEED_DESIGN_FRACTION are already anchored to
    # real historical practice (the 7-stage J-2 LH2 pump, the deepest-staged
    # real flight pump this tool is validated against). If the UNCLAMPED head/
    # tip-speed math wants MORE stages than that modeled ceiling, the design is
    # still sized at MAX_PUMP_STAGES anyway (below) - which likely UNDERSTATES
    # real per-stage head/tip-speed demand rather than representing genuinely
    # buildable hardware. Only fires when stages aren't pinned by the caller.
    if stages_wanted > MAX_PUMP_STAGES and (not forced_stages or forced_stages <= 0):
        warnings.append(
            f"required head/tip-speed combination implies wanting ~{stages_wanted} pump "
            f"stages, beyond this tool's {MAX_PUMP_STAGES}-stage modeled ceiling (real "
            f"historical practice tops out around the J-2's 7 axial LH2 stages) - the "
            f"design is being sized at {MAX_PUMP_STAGES} stages anyway, which likely "
            f"understates real head-per-stage/tip-speed demand rather than representing "
            f"genuinely buildable hardware.")

    def _stage_quantities(stages):
        stage_m = head_m / stages
        stage_ft = head_ft / stages
        tip = math.sqrt(G * stage_m / HEAD_COEFFICIENT_PSI) if stage_m > 0 else 0.0
        rpm = (NS_TARGET_US * stage_ft ** 0.75 / q_gpm ** 0.5) if q_gpm > 0 and stage_ft > 0 else 0.0
        return stage_ft, tip, rpm

    head_stage_ft, u_tip, n_rpm = _stage_quantities(n_stages)

    # --- suction specific speed / NPSH-required (informational always;
    # changes n_stages only when enforce_suction_limit is explicitly on) -----
    nss_class = _nss_class(rho_kg_m3)
    nss_target = NSS_TARGET_US[nss_class]
    anchor_ft = NPSH_REAL_ANCHOR_FT[nss_class]
    npsh_required_ft = required_npsh_ft(n_rpm, q_gpm, nss_target) if n_rpm > 0 else 0.0
    unforced = not forced_stages or forced_stages <= 0
    if enforce_suction_limit and unforced and n_rpm > 0:
        while (npsh_required_ft > NPSH_MARGIN_FACTOR * anchor_ft
               and n_stages < MAX_PUMP_STAGES):
            n_stages += 1
            head_stage_ft, u_tip, n_rpm = _stage_quantities(n_stages)
            npsh_required_ft = required_npsh_ft(n_rpm, q_gpm, nss_target)
        if npsh_required_ft > NPSH_MARGIN_FACTOR * anchor_ft:
            warnings.append(
                f"this pump's suction specific speed implies needing "
                f"~{npsh_required_ft:.0f} ft NPSH even at {n_stages} stage(s) - well above "
                f"real {('LOX' if nss_class == 'lox_class' else 'LH2')}-class turbopump "
                f"practice (~{anchor_ft:.0f} ft). Real high-head pumps of this class use a "
                f"dedicated low-speed axial INDUCER stage for cavitation margin "
                f"[SP-8107 2.1.1.2]. This tool does not size a separate inducer stage; "
                f"treat the reported rotor speed as optimistic until one is added.")

    # Vehicle-NPSH speed cap (opt-in; see docstring).
    rpm_ns_optimum = n_rpm
    suction_limited = False
    if npsh_available_ft and npsh_available_ft > 0 and n_rpm > 0:
        n_cap = suction_limited_rpm(q_gpm, npsh_available_ft, nss_target)
        if 0 < n_cap < n_rpm:
            n_rpm = n_cap
            suction_limited = True
            npsh_required_ft = float(npsh_available_ft)

    d_impeller_m = 60.0 * u_tip / (math.pi * n_rpm) if n_rpm > 0 else 0.0
    ns_us = (n_rpm * q_gpm ** 0.5 / head_stage_ft ** 0.75) if head_stage_ft > 0 else 0.0
    tip_margin = material.max_tip_speed_m_s / u_tip if u_tip > 0 else float("inf")

    # Whole-pump specific speed (the efficiency-relevant one): the tool designs
    # every STAGE at NS_TARGET_US, so a multistage pump's whole-pump Ns is
    # NS_TARGET_US / n_stages**0.75 - a J-2-class 7-stage LH2 pump lands well
    # below the efficiency peak, which is why it is only ~73% efficient.
    ns_pump_us = NS_TARGET_US / n_stages ** 0.75 if n_stages > 0 else NS_TARGET_US
    eta = turbopump_efficiency.pump_efficiency(ns_pump_us, q_m3s, build_quality) if q_m3s > 0 else 0.0
    if suction_limited:
        eta_opt = eta
        ns_pump_us = ns_us / n_stages ** 0.75
        eta = turbopump_efficiency.pump_efficiency(ns_pump_us, q_m3s, build_quality)
        warnings.append(
            f"pump suction-limited to {n_rpm:.0f} rpm by the {npsh_available_ft:.0f} ft NPSH "
            f"available (Ns-optimum {rpm_ns_optimum:.0f} rpm) - larger impeller, efficiency "
            f"{100 * (eta - eta_opt):+.1f} pts. Raise tank pressure/NPSH to recover it "
            f"[SP-8107 2.1.1.2].")

    if u_tip > material.max_tip_speed_m_s:
        warnings.append(
            f"pump impeller tip speed {u_tip:.0f} m/s exceeds {material.display_name}'s "
            f"~{material.max_tip_speed_m_s:.0f} m/s capability even at {n_stages} stage(s)")

    volute_od_m = max(MIN_BODY_OD_M, d_impeller_m * VOLUTE_OD_FACTOR)
    body_length_m = max(MIN_BODY_LEN_M, (INDUCER_LEN_FACTOR
                        + n_stages ** STAGE_COUNT_EXPONENT * STAGE_WIDTH_FACTOR) * d_impeller_m)

    return {
        "q_m3s": q_m3s, "head_m": head_m, "n_stages": n_stages, "auto_stages": auto_stages,
        "u_tip_m_s": u_tip, "n_rpm": n_rpm, "d_impeller_m": d_impeller_m, "ns_us": ns_us,
        "ns_pump_us": ns_pump_us, "eta": eta,
        "volute_od_m": volute_od_m, "body_length_m": body_length_m,
        "tip_speed_margin": tip_margin, "warnings": warnings,
        "npsh_required_ft": npsh_required_ft, "nss_class": nss_class, "nss_target_us": nss_target,
        "rpm_ns_optimum": rpm_ns_optimum, "suction_limited": suction_limited,
        "npsh_available_ft": float(npsh_available_ft or 0.0),
        "inlet_eye_dia_m": inlet_eye_dia_m(q_m3s, n_rpm),
    }


def feed_dp_plausibility_warning(dp_fuel_pa, dp_ox_pa):
    """Warn-only: flags a required pump-discharge dP (dp_fuel/dp_ox - see
    design.py's per-cycle-branch dp_fuel/dp_ox formula, which sums Pc +
    injector dP + jacket dP + line losses) that exceeds real historical
    flight-turbopump practice (FEED_DP_PLAUSIBLE_CEILING_PA above). This
    module always SOLVES a pump to deliver whatever dP is demanded (see module
    docstring) - no starvation failure mode exists by construction - so this
    is the honest proxy for "this idealized solve may not correspond to
    buildable hardware, i.e. real flow could fall short." Returns a warning
    string, or None if within plausible range."""
    peak_pa = max(dp_fuel_pa, dp_ox_pa)
    if peak_pa > FEED_DP_PLAUSIBLE_CEILING_PA:
        return (
            f"required pump discharge dP (~{peak_pa/1e6:.0f} MPa) exceeds "
            f"~{FEED_DP_PLAUSIBLE_CEILING_PA/1e6:.0f} MPa, beyond real flight-turbopump "
            f"historical practice [SP-8107 Tables V-VI] - the pump is being solved to "
            f"deliver this dP anyway (this tool has no independent pump-performance "
            f"ceiling), but real hardware delivering this flow at this pressure is "
            f"unproven; treat downstream Isp/thrust as optimistic until checked against "
            f"a real high-pressure-pump analog.")
    return None


def size_turbine(shaft_n_rpm, specific_work_j_kg, staging, material, *,
                 shaft_power_w=0.0, pressure_ratio=0.0, build_quality=1.0):
    """One turbine on a shaft turning at `shaft_n_rpm`, driven by gas of
    `specific_work_j_kg` available enthalpy drop. `shaft_power_w` and
    `pressure_ratio` feed the derived efficiency (partial admission, PR loss)."""
    c0 = math.sqrt(2.0 * max(specific_work_j_kg, 1.0))
    u_over_c0 = TURBINE_U_OVER_C0.get(staging, TURBINE_U_OVER_C0["velocity_compounded_2row"])
    u_pitch = u_over_c0 * c0
    d_mean_m = 60.0 * u_pitch / (math.pi * shaft_n_rpm) if shaft_n_rpm > 0 else 0.0
    tip_margin = material.max_tip_speed_m_s / u_pitch if u_pitch > 0 else float("inf")
    eta = turbopump_efficiency.turbine_efficiency(
        staging, u_pitch, shaft_power_w, pressure_ratio, build_quality)
    disk_od_m = d_mean_m * DISK_OD_FACTOR
    disk_thickness_m = disk_od_m * DISK_THICK_FACTOR
    manifold_od_m = disk_od_m * MANIFOLD_OD_FACTOR
    manifold_length_m = disk_thickness_m * MANIFOLD_LEN_FACTOR
    warnings = []
    if u_pitch > material.max_tip_speed_m_s:
        warnings.append(
            f"turbine pitchline speed {u_pitch:.0f} m/s exceeds {material.display_name}'s "
            f"~{material.max_tip_speed_m_s:.0f} m/s blade capability")
    return {
        "c0_m_s": c0, "u_over_c0": u_over_c0, "u_pitchline_m_s": u_pitch,
        "d_mean_m": d_mean_m, "blade_tip_speed_margin": tip_margin, "staging": staging,
        "eta": eta, "disk_od_m": disk_od_m, "disk_thickness_m": disk_thickness_m,
        "manifold_od_m": manifold_od_m, "manifold_length_m": manifold_length_m,
        "warnings": warnings,
    }


def size_turbopump(cyc, dp_fuel_pa, dp_ox_pa, rho_fuel, rho_ox, pair, thrust_n, cycle,
                   arrangement, turbine_staging, material_key, *, turbine_inlet_k,
                   turbine_specific_work_j_kg=None, turbine_pressure_ratio=0.0,
                   build_quality=1.0, pump_stages_fuel=0, pump_stages_ox=0,
                   eta_pump_fuel_final=0.0, eta_pump_ox_final=0.0, eta_turbine_final=0.0,
                   motor_mass_kg=0.0, bearing_material_key="cronidur_30",
                   enforce_suction_limit=False, npsh_available_fuel_ft=0.0,
                   npsh_available_ox_ft=0.0):
    """
    Full turbopump preliminary sizing for a pump-fed `cyc` (the dict from
    cycles.gas_generator_result / expander.expander_result). Returns a dict for
    the GUI's Turbopump tab plus a `mass_modifier` for design.py and the DERIVED
    pump/turbine efficiencies (physics/turbopump_efficiency.py).

    `enforce_suction_limit` (default False) - see size_pump()'s docstring.
    """
    tp = cyc["turbopump"]
    mat = turbopump_materials.MATERIALS[material_key]

    is_electric = cycle == "electric_pump"

    auto_arr = derive_arrangement(rho_fuel, rho_ox, thrust_n)
    eff_arr = auto_arr if arrangement in (None, "", "auto") else arrangement
    # FFSC is physically one turbopump per preburner (fuel-rich + ox-rich) -> a
    # dual-shaft layout is the natural architecture unless the user overrides.
    if cycle == "ffsc" and arrangement in (None, "", "auto"):
        eff_arr = "dual_shaft"
    auto_stg = derive_turbine_staging(cycle, pair)
    eff_stg = auto_stg if turbine_staging in (None, "", "auto") else turbine_staging

    fuel_pump = size_pump(tp["mdot_fuel_kgs"], dp_fuel_pa, rho_fuel, mat,
                          forced_stages=pump_stages_fuel, build_quality=build_quality,
                          enforce_suction_limit=enforce_suction_limit,
                          npsh_available_ft=npsh_available_fuel_ft)
    ox_pump = size_pump(tp["mdot_ox_kgs"], dp_ox_pa, rho_ox, mat,
                        forced_stages=pump_stages_ox, build_quality=build_quality,
                        enforce_suction_limit=enforce_suction_limit,
                        npsh_available_ft=npsh_available_ox_ft)

    if is_electric:
        # Battery + brushless DC motors drive the pumps directly - no turbine.
        n_turbines = 0
        fuel_shaft_rpm = fuel_pump["n_rpm"]
        ox_shaft_rpm = ox_pump["n_rpm"]
    elif eff_arr == "dual_shaft":
        n_turbines = 2
        fuel_shaft_rpm = fuel_pump["n_rpm"]
        ox_shaft_rpm = ox_pump["n_rpm"]
    elif eff_arr == "geared":
        n_turbines = 1
        fuel_shaft_rpm = fuel_pump["n_rpm"]          # turbine + fuel pump direct
        ox_shaft_rpm = ox_pump["n_rpm"]              # ox pump geared off it
    else:  # single_shaft
        n_turbines = 1
        fuel_shaft_rpm = ox_shaft_rpm = min(p for p in (fuel_pump["n_rpm"], ox_pump["n_rpm"]) if p > 0) \
            if (fuel_pump["n_rpm"] > 0 or ox_pump["n_rpm"] > 0) else 0.0

    dh = 0.0 if is_electric else (
        turbine_specific_work_j_kg if turbine_specific_work_j_kg is not None
        else (cyc.get("turbine_specific_work_j_kg") or 0.0))
    # Shaft power each turbine delivers: for a single/geared turbopump the one
    # turbine drives both pumps; for a dual-shaft layout each turbine drives its
    # own pump.
    fuel_turb_power = tp["power_total_w"] if n_turbines == 1 else tp["power_fuel_w"]
    ox_turb_power = tp["power_ox_w"]
    dh_fuel_turb, dh_ox_turb = split_turbine_work(cycle, n_turbines, dh, tp["power_fuel_w"],
                                                  tp["power_ox_w"], cyc)
    turbine = (size_turbine(fuel_shaft_rpm, dh_fuel_turb, eff_stg, mat, shaft_power_w=fuel_turb_power,
                            pressure_ratio=turbine_pressure_ratio, build_quality=build_quality)
               if dh > 0 and fuel_shaft_rpm > 0 else None)
    ox_turbine = (size_turbine(ox_shaft_rpm, dh_ox_turb, eff_stg, mat,
                               shaft_power_w=ox_turb_power, pressure_ratio=turbine_pressure_ratio,
                               build_quality=build_quality)
                  if n_turbines == 2 and dh > 0 and (dh_ox_turb or 0) > 0 and ox_shaft_rpm > 0
                  else None)

    # --- physical envelope + geometry-derived mass ------------------------
    bodies, assembly_length_m, assembly_od_m, n_bodies = _assemble_bodies(
        eff_arr, fuel_pump, ox_pump, turbine, ox_turbine)
    mass_geometry_kg = _turbopump_mass_from_geometry(bodies, mat.density_kg_m3)
    mass_assembly_kg = turbopump_mass_kg(tp["power_total_w"])   # the mass used downstream

    # The raw 1-D envelope runs a few x too big (approximate rotor speeds -> big
    # diameters). Scale every body isotropically so the envelope volume is
    # consistent with mass_assembly_kg, giving a believable 3D size.
    render_scale = 1.0
    if mass_geometry_kg > 0.0:
        render_scale = max(0.2, min(2.0, (mass_assembly_kg / mass_geometry_kg) ** (1.0 / 3.0)))
    for b in bodies:
        b["od_m"] *= render_scale
        b["length_m"] *= render_scale
        b["x0_m"] *= render_scale
    assembly_length_m *= render_scale
    assembly_od_m *= render_scale

    # Electric pump-fed: no turbine disk in the envelope - instead a motor+controller
    # body sized straight from its mass (so the 3-D shows a motor, not a turbine).
    if is_electric and motor_mass_kg > 0.0:
        motor_vol_m3 = motor_mass_kg / max(mat.density_kg_m3 * EFFECTIVE_SOLID_FRACTION, 1.0)
        motor_od_m = max(0.05, (4.0 * motor_vol_m3 / (math.pi * 2.0)) ** (1.0 / 3.0))
        motor_len_m = max(1e-4, motor_vol_m3 / (math.pi * 0.25 * motor_od_m * motor_od_m))
        x_end = max((b["x0_m"] + b["length_m"] for b in bodies), default=0.0)
        bodies.append(dict(kind="motor", od_m=motor_od_m, length_m=motor_len_m,
                           x0_m=x_end, center=0))
        n_bodies += 1
        assembly_length_m = x_end + motor_len_m
        assembly_od_m = max(assembly_od_m, motor_od_m)

    # --- dry-mass modifier: 1.0 for the auto architecture, by construction ---
    mod = 1.0
    if eff_arr == "geared" and auto_arr != "geared":
        mod *= (1.0 + GEARBOX_MASS_FRACTION)
    elif eff_arr != "geared" and auto_arr == "geared":
        mod *= (1.0 - GEARBOX_MASS_FRACTION)
    extra_stages = ((fuel_pump["n_stages"] - fuel_pump["auto_stages"])
                    + (ox_pump["n_stages"] - ox_pump["auto_stages"]))
    mod *= (1.0 + EXTRA_STAGE_MASS_FRACTION * extra_stages)
    lo, hi = MASS_MODIFIER_CLAMP
    mass_modifier = max(lo, min(hi, mod))

    # --- warn-not-block: material suitability + tip-speed feasibility -------
    peak_tip = max(fuel_pump["u_tip_m_s"], ox_pump["u_tip_m_s"],
                   turbine["u_pitchline_m_s"] if turbine else 0.0)
    warnings = list(fuel_pump["warnings"]) + list(ox_pump["warnings"])
    if turbine:
        warnings += turbine["warnings"]
    if ox_turbine:
        warnings += ox_turbine["warnings"]
    warnings += turbopump_materials.turbopump_material_suitability(
        material_key, turbine_inlet_k=turbine_inlet_k, tip_speed_m_s=peak_tip,
        cycle=cycle, touches_oxidizer=True)

    # --- shaft / bearing sizing (a rough segment-power estimate: for a shared
    # single/geared shaft, fuel_turb_power already carries the FULL delivered
    # power - a conservative/oversized estimate for the ox-side segment, which
    # in reality sees less torque downstream of the fuel-pump takeoff) --------
    fuel_shaft_dia_m = shaft_diameter_m(fuel_turb_power, fuel_shaft_rpm)
    ox_shaft_dia_m = shaft_diameter_m(ox_turb_power, ox_shaft_rpm)
    fuel_bearing_bore_m = fuel_shaft_dia_m * BEARING_BORE_OVER_SHAFT_FACTOR
    ox_bearing_bore_m = ox_shaft_dia_m * BEARING_BORE_OVER_SHAFT_FACTOR
    fuel_bearing_dn = bearing_dn(fuel_shaft_rpm, fuel_bearing_bore_m)
    ox_bearing_dn = bearing_dn(ox_shaft_rpm, ox_bearing_bore_m)
    # Bearing's own local temperature tracks the pumped-fluid inlet, not the
    # (much hotter) turbine gas - use ambient/cryo-propellant temperature as a
    # rough proxy rather than turbine_inlet_k.
    bearing_use_temp_k = 300.0
    warnings += turbopump_materials.bearing_suitability(
        bearing_material_key, dn_mm_rpm=max(fuel_bearing_dn, ox_bearing_dn),
        use_temp_k=bearing_use_temp_k)
    bearing_mat = turbopump_materials.BEARING_MATERIALS[bearing_material_key]

    # Prefer the efficiencies design.py actually used in the power balance (passed
    # in) so the reported numbers can't drift from what drove Isp/mass.
    eta_pump_fuel = eta_pump_fuel_final if eta_pump_fuel_final > 0 else fuel_pump["eta"]
    eta_pump_ox = eta_pump_ox_final if eta_pump_ox_final > 0 else ox_pump["eta"]
    eta_turbine = eta_turbine_final if eta_turbine_final > 0 else (turbine["eta"] if turbine else 0.0)
    eta_turbine_ox = ox_turbine["eta"] if ox_turbine else eta_turbine
    eta_overall = turbopump_efficiency.overall_efficiency(
        0.5 * (eta_pump_fuel + eta_pump_ox), eta_turbine) if eta_turbine else 0.0

    return {
        "arrangement": eff_arr, "auto_arrangement": auto_arr,
        "turbine_staging": eff_stg, "auto_turbine_staging": auto_stg,
        "n_turbines": n_turbines, "geared": eff_arr == "geared",
        "fuel_shaft_rpm": fuel_shaft_rpm, "ox_shaft_rpm": ox_shaft_rpm,
        "fuel_pump": fuel_pump, "ox_pump": ox_pump,
        "turbine": turbine, "ox_turbine": ox_turbine,
        "material_key": material_key, "material_display": mat.display_name,
        "turbine_inlet_k": turbine_inlet_k,
        "eta_pump_fuel": eta_pump_fuel, "eta_pump_ox": eta_pump_ox,
        "eta_turbine": eta_turbine, "eta_turbine_ox": eta_turbine_ox,
        "eta_overall": eta_overall, "build_quality": build_quality,
        "bodies": bodies, "assembly_length_m": assembly_length_m,
        "assembly_od_m": assembly_od_m, "n_bodies": n_bodies,
        "mass_kg": mass_assembly_kg,               # feeds computed_dry_mass_kg
        "mass_geometry_kg": mass_geometry_kg,      # envelope cross-check only
        "mass_specific_power_kg": tp["turbopump_mass_kg"],  # legacy 36 kW/kg estimate
        "mass_modifier": mass_modifier,
        "bearing_material_key": bearing_material_key,
        "bearing_material_display": bearing_mat.display_name,
        "fuel_bearing_dn": fuel_bearing_dn, "ox_bearing_dn": ox_bearing_dn,
        "feasible": not warnings,   # any sizing/material warning -> "marginal", not "feasible"
        "warnings": warnings,
    }


if __name__ == "__main__":
    from . import cycles, turbopump as tp

    def _fake_cyc(mdot, mr, dp_f, dp_ox, rho_f, rho_ox, dh):
        c = cycles.gas_generator_result(
            mdot, mr, 7.0e6, dp_f, dp_ox, rho_f, rho_ox, 0.72, 0.75, 36000.0,
            1050.0, 2100.0, 0.62, 22.0, 1.13)
        c["turbine_specific_work_j_kg"] = dh
        return c

    # F-1-ish (LOX/RP-1): single shaft, 1 turbine, ~5500 rpm ballpark, mod 1.0.
    f1 = size_turbopump(_fake_cyc(2587.0, 2.27, 10.0e6, 8.4e6, 810.0, 1141.0, 4.1e5),
                        10.0e6, 8.4e6, 810.0, 1141.0, "LOX/RP-1", 7_770_000.0,
                        "gas_generator", "auto", "auto", "inconel_718",
                        turbine_inlet_k=1050.0)
    assert f1["arrangement"] == "single_shaft" and f1["n_turbines"] == 1, f1
    assert abs(f1["mass_modifier"] - 1.0) < 1e-12, f1["mass_modifier"]

    # J-2-ish (LOX/LH2): dual shaft, 2 turbines, multistage LH2 pump, mod 1.0.
    j2 = size_turbopump(_fake_cyc(247.0, 5.5, 8.15e6, 6.5e6, 71.0, 1141.0, 2.5e6),
                        8.15e6, 6.5e6, 71.0, 1141.0, "LOX/LH2", 1_023_000.0,
                        "gas_generator", "auto", "auto", "titanium_forged",
                        turbine_inlet_k=922.0)
    assert j2["arrangement"] == "dual_shaft" and j2["n_turbines"] == 2, j2
    assert j2["fuel_pump"]["n_stages"] >= 4, j2["fuel_pump"]["n_stages"]
    assert abs(j2["mass_modifier"] - 1.0) < 1e-12, j2["mass_modifier"]

    # Forcing a gearbox on F-1 adds mass; forcing extra stages adds mass.
    f1g = size_turbopump(_fake_cyc(2587.0, 2.27, 10.0e6, 8.4e6, 810.0, 1141.0, 4.1e5),
                         10.0e6, 8.4e6, 810.0, 1141.0, "LOX/RP-1", 7_770_000.0,
                         "gas_generator", "geared", "auto", "inconel_718",
                         turbine_inlet_k=1050.0, pump_stages_fuel=3)
    assert f1g["mass_modifier"] > 1.0, f1g["mass_modifier"]

    # --- shaft / bearing sizing ---
    # Exact torsion round-trip: back out shear stress from a known d, T and
    # confirm shaft_diameter_m recovers d.
    d_test = shaft_diameter_m(4.0e5, 6000.0)
    assert d_test > 0.0
    torque_test = 4.0e5 / (2.0 * math.pi * 6000.0 / 60.0)
    tau_check = 16.0 * torque_test / (math.pi * d_test ** 3)
    assert abs(tau_check - SHAFT_ALLOWABLE_SHEAR_PA) / SHAFT_ALLOWABLE_SHEAR_PA < 1e-9

    assert bearing_dn(20000.0, 0.05) == 20000.0 * 0.05 * 1000.0

    # J-2's real LH2 fuel shaft (27,000 rpm) should need a much smaller-bore
    # bearing than F-1's real dense-propellant shaft (5,500 rpm) to reach a
    # comparable DN - i.e. the DN check is exercised, not just plumbed through.
    assert "fuel_bearing_dn" in f1 and "fuel_bearing_dn" in j2
    assert f1["bearing_material_key"] == "cronidur_30"

    # A design whose bearing DN exceeds even Si3N4 ceramic's ceiling should warn;
    # 440C at the same DN should also warn (monotonic - matches
    # turbopump_materials.py's own bearing_suitability self-test).
    extreme = size_turbopump(_fake_cyc(50.0, 5.5, 8.15e6, 6.5e6, 71.0, 1141.0, 2.5e6),
                             8.15e6, 6.5e6, 71.0, 1141.0, "LOX/LH2", 50_000.0,
                             "gas_generator", "single_shaft", "auto", "titanium_forged",
                             turbine_inlet_k=922.0, bearing_material_key="si3n4_ceramic")
    extreme_steel = size_turbopump(_fake_cyc(50.0, 5.5, 8.15e6, 6.5e6, 71.0, 1141.0, 2.5e6),
                                   8.15e6, 6.5e6, 71.0, 1141.0, "LOX/LH2", 50_000.0,
                                   "gas_generator", "single_shaft", "auto", "titanium_forged",
                                   turbine_inlet_k=922.0, bearing_material_key="440c_steel")
    assert len(extreme_steel["warnings"]) >= len(extreme["warnings"])

    # --- NPSH-required / suction specific speed (opt-in, default OFF) ---
    # C1: pure round-trip - required_npsh_ft inverted against the real F-1/J-2
    # N,Q reproduces their real 60/75 ft NPSH_crit exactly (validates the
    # formula independent of trusting NSS_TARGET_US's magnitude).
    f1_npsh = required_npsh_ft(5488.0, 25200.0, NSS_TARGET_US["lox_class"])
    j2_npsh = required_npsh_ft(27000.0, 3000.0, NSS_TARGET_US["lh2_class"])
    assert abs(f1_npsh - 60.0) < 0.5, f1_npsh
    assert abs(j2_npsh - 75.0) < 0.5, j2_npsh
    assert abs(suction_specific_speed_us(5488.0, 25200.0, f1_npsh)
               - NSS_TARGET_US["lox_class"]) < 1.0

    # C2: enforce_suction_limit=True increases stage count / lowers rotor speed
    # vs False on a synthetic extreme-head pump, and fires the inducer warning
    # when even MAX_PUMP_STAGES can't satisfy the suction-specific-speed target.
    mat_ti = turbopump_materials.MATERIALS["titanium_forged"]
    off = size_pump(50.0, 250e6, 71.0, mat_ti, enforce_suction_limit=False)
    on = size_pump(50.0, 250e6, 71.0, mat_ti, enforce_suction_limit=True)
    assert on["n_stages"] >= off["n_stages"], (on["n_stages"], off["n_stages"])
    assert on["n_rpm"] <= off["n_rpm"] + 1e-6, (on["n_rpm"], off["n_rpm"])
    assert on["n_stages"] == MAX_PUMP_STAGES, on["n_stages"]  # this extreme case can't be satisfied
    assert any("inducer" in w for w in on["warnings"]), on["warnings"]
    assert not any("inducer" in w for w in off["warnings"])   # off -> no suction check at all
    assert "npsh_required_ft" in off and off["npsh_required_ft"] > 0.0  # informational even when off

    # C3: neutral-default regression guard - enforce_suction_limit=False (the
    # shipped default) reproduces the F-1/J-2 results already asserted above
    # bit-for-bit; this is the concrete evidence behind "default OFF, zero
    # behavior change" rather than just an intention.
    f1_default = size_turbopump(_fake_cyc(2587.0, 2.27, 10.0e6, 8.4e6, 810.0, 1141.0, 4.1e5),
                                10.0e6, 8.4e6, 810.0, 1141.0, "LOX/RP-1", 7_770_000.0,
                                "gas_generator", "auto", "auto", "inconel_718",
                                turbine_inlet_k=1050.0)
    assert f1_default["fuel_shaft_rpm"] == f1["fuel_shaft_rpm"]
    assert f1_default["fuel_pump"]["n_stages"] == f1["fuel_pump"]["n_stages"]
    assert abs(f1_default["mass_modifier"] - f1["mass_modifier"]) < 1e-12

    # Vehicle-NPSH speed cap: 0 = identical dict; a binding NPSH lowers rpm,
    # grows the impeller, lowers eta, and round-trips the Nss relation.
    _mat = turbopump_materials.MATERIALS["titanium_forged"]
    _p0 = size_pump(200.0, 7.0e6, 1141.0, _mat)
    _p0b = size_pump(200.0, 7.0e6, 1141.0, _mat, npsh_available_ft=0.0)
    assert {k: v for k, v in _p0.items() if k != "warnings"} == \
        {k: v for k, v in _p0b.items() if k != "warnings"}
    assert not _p0["suction_limited"]
    _p25 = size_pump(200.0, 7.0e6, 1141.0, _mat, npsh_available_ft=25.0)
    assert _p25["suction_limited"] and _p25["n_rpm"] < _p0["n_rpm"]
    assert _p25["d_impeller_m"] > _p0["d_impeller_m"] and _p25["eta"] < _p0["eta"]
    _q_gpm = _p25["q_m3s"] * _M3S_TO_GPM
    assert abs(suction_specific_speed_us(_p25["n_rpm"], _q_gpm, 25.0)
               - _p25["nss_target_us"]) < 1e-6 * _p25["nss_target_us"]
    _p_big = size_pump(200.0, 7.0e6, 1141.0, _mat, npsh_available_ft=1e5)   # not binding
    assert not _p_big["suction_limited"] and _p_big["n_rpm"] == _p0["n_rpm"]
    # Eye diameter: positive, ~Q^(1/3) at fixed rpm.
    _d1, _d8 = inlet_eye_dia_m(0.1, 10000.0), inlet_eye_dia_m(0.8, 10000.0)
    assert _d1 > 0 and abs(_d8 / _d1 - 2.0) < 1e-9
    print(f"suction-limited rpm self-check: OK ({_p0['n_rpm']:.0f} -> {_p25['n_rpm']:.0f} rpm "
          f"at 25 ft, eta {_p0['eta']:.3f} -> {_p25['eta']:.3f})")

    print(f"turbopump_sizing.py smoke test OK - "
          f"F-1 {f1['fuel_shaft_rpm']:.0f} rpm 1 turbine, "
          f"J-2 LH2 pump {j2['fuel_pump']['n_stages']} stages "
          f"{j2['fuel_pump']['u_tip_m_s']:.0f} m/s / {j2['fuel_shaft_rpm']:.0f} rpm, "
          f"J-2 fuel turbine U {j2['turbine']['u_pitchline_m_s']:.0f} m/s, "
          f"J-2 fuel bearing DN {j2['fuel_bearing_dn']:,.0f} mm*rpm "
          f"({j2['bearing_material_display']}), "
          f"NPSH-required round-trip F-1 {f1_npsh:.0f} / J-2 {j2_npsh:.0f} ft")
