"""
Turbine-exhaust handling for open cycles (gas generator / tap-off): where the
turbine's spent drive gas goes, what it costs the turbine in back pressure,
and what thrust it gives back. Replaces the old flat GG_DUMP_ISP_FRACTION
(0.55) / TAP_OFF_DUMP_ISP_FRACTION (0.80) with a small physical model.

Three real disposal modes (EngineDesign.turbine_exhaust_mode):

- "overboard_duct" (default): a duct carries the exhaust overboard.
  turbine_exhaust_nozzle_eps = 1 is a plain sonic duct exit (RS-68, the H-1C's
  curved duct [H1-Man §1-49]). > 1 is a shaped exhaust nozzle (LR-87/LR-91 -
  the LR-91's swivelling roll nozzle, 865 lbf [RO LR91 header]). A cant angle
  trades axial thrust for a side force / roll torque (reported only; no KSP
  roll module is exported, matching RO's own LR-91).
- "aspirator": the H-1D's Hastelloy C shroud over the aft ~20 in of the main
  nozzle, the exhaust leaving through a 0.440 in annular slot at the exit lip
  into the plume edge [H1-Man §1-51]; also the Atlas sustainer
  "annulus-at-exit" pattern [SP-8120]. Modelled as a CHOKED annular slot
  discharging to ambient at the exit plane. The entrainment ("aspiration")
  benefit is NOT modelled - no source quantifies it.
- "nozzle_injection": the exhaust is injected into the main nozzle at
  turbine_exhaust_inject_eps through a manifold (F-1, eps 10:1, feeding a
  gas-film-cooled extension to 16:1 [SP-8120]; J-2 "cat-eyes" at eps
  10.45-11.40, 115 in2 [J-2 history, literature/]). It expands with the main
  flow to the nozzle exit AND acts as a gas film on the wall downstream
  (the film is applied by the design's thermal solve, see
  film_mdot_ratio_to_fuel).

The physics, in order:
1. Exhaust gas: the same ideal gas the turbine-work model uses (cp, gamma
   from GG_GAS_PROPERTIES or the tap-off gas), so R = cp (gamma-1)/gamma.
   Turbine exit total temperature = Tin - dh_actual / cp.
   An optional LOX->GOX heat exchanger (the H-1's pressurant heater
   [H1-Man §1-47]; Titan I superheater [SP-8120]) takes
   mdot_gox * LOX_TO_GOX_DH_J_KG out of the stream.
2. Back pressure: the exhaust must leave SONIC into whatever it discharges
   into - ambient (sea level if the main nozzle runs attached at sea level,
   else vacuum) for overboard/aspirator, the local main-nozzle static
   pressure for injection. So the exhaust-exit total pressure must be
   >= p_discharge / p*/p0(gamma), and the turbine outlet sits
   EXHAUST_DUCT_PRESSURE_RATIO above that (duct/heat-exchanger/slot losses +
   margin, reverse-solved on the H-1) - or, for injection,
   EXHAUST_INJECTION_PRESSURE_RATIO (manifold + shingle slots, an interim
   lumped value reverse-solved on the F-1's 58 psia). Turbine PR = min(cap, p_in / p_out),
   p_in = turbine-inlet fraction x Pc. A vacuum-discharging exhaust hits the
   old flat cap (GG_PRESSURE_RATIO 22, now a CAP).
3. Exhaust thrust: ideal isentropic expansion of the exhaust from its exit
   total pressure through the mode's exit (sonic slot / shaped nozzle /
   the main nozzle down to its exit static pressure), times
   EXHAUST_THRUST_EFFICIENCY (reverse-solved on the F-1's 16,000 lbf
   turbine-exhaust thrust potential [SP-8120]).

Pure functions + a __main__ self-test; physics/design/feed_stage.py
dispatches here.
"""
import math

import numpy as np

from . import isentropic as iso

MODES = ("overboard_duct", "aspirator", "nozzle_injection")
MODE_LABELS = {
    "overboard_duct": "Overboard duct / exhaust nozzle (RS-68, LR-87, LR-91, H-1C)",
    "aspirator": "Aspirator shroud at the nozzle exit (H-1D, Atlas sustainer)",
    "nozzle_injection": "Injection into the main nozzle (F-1, J-2)",
}
DEFAULT_MODE = "overboard_duct"

PA_SEA_LEVEL = 101325.0

# Turbine inlet total pressure as a fraction of main-chamber (injector-end)
# Pc. Tier 2, the mean of two real anchors: H-1 turbine inlet 599.0 psia total
# vs injector-end Pc 689.3 psia (200K rating) = 0.869 [H1-Man Fig 1-47/1-18],
# and F-1 945 psia (MD128/174 uprated) vs 1,125 psia = 0.840 [F1-Man Fig
# 3-14/1-7].
GG_TURBINE_INLET_PC_FRACTION = 0.855
# Tap-off drive gas is bled from the main chamber through a tapoff valve and
# film/mix cooling - Tier 3: no turbine-inlet pressure in hand for the J-2S
# ([AEDC-J2S] gives sensor ranges only). Taken equal to the GG value.
TAP_OFF_TURBINE_INLET_PC_FRACTION = GG_TURBINE_INLET_PC_FRACTION

# Turbine outlet total pressure / exhaust-exit total pressure: duct, heat-
# exchanger and slot losses plus a choking margin, lumped. Tier 2, REVERSE-
# SOLVED on the H-1 (a sea-level booster whose exhaust leaves sonic through
# an aspirator slot / duct exit to sea-level ambient): turbine exit 33.8 psia
# = 233.04 kPa [H1-Man Fig 1-47] vs the sonic-to-sea-level requirement
# 101325 / p*/p0(1.13) = 175.2 kPa -> 1.330. Independent check: Titan I
# exhaust at 30 psi [SP-8120] (sea-level booster, through a superheater) is
# within ~13% of the 33.8 psia this gives (self-test).
EXHAUST_DUCT_PRESSURE_RATIO = 1.330

# The same lumped ratio for NOZZLE INJECTION: turbine outlet total pressure /
# the total pressure the exhaust has left when it leaves the injection slots
# sonic into the local main-nozzle static pressure (duct + hot-gas manifold +
# shingle-slot / eyelet losses). Tier 2 INTERIM, REVERSE-SOLVED on the F-1:
# turbine exit 58 psia static [F1-Man Fig 1-16/3-14] vs the eps-10 static of
# the real 1,125 psia chamber (pe/pc 0.0119 at the corpus F-1's gamma 1.218 ->
# 13.4 psia): 58 / 13.4 = 4.32 = this / p*/p0(1.13) -> 2.50. Pinned as a
# RATIO to the local static, so it carries across Pc. It is one engine's
# lumped loss, not per-engine physics: a real replacement would compute the
# torus (decreasing section, splitter plates, exit vanes [F1-Man §1-18]) and
# slot/eyelet dP from geometry - the F-1's 23 rows of shingle slots, the J-2's
# 115 in^2 of eyelets [RPE-J2Blog] - see claude_lit/OPEN_QUESTIONS.md.
EXHAUST_INJECTION_PRESSURE_RATIO = 2.50
# Thrust efficiency of the exhaust stream vs its ideal isentropic expansion
# (non-parallel exit, mixing with the main-flow boundary layer, duct swirl,
# non-ideal frozen gas). Tier 2, REVERSE-SOLVED through the full pipeline on
# the validation-corpus F-1 in nozzle_injection mode at eps 10 against its
# real 16,000 lbf turbine-exhaust thrust potential [SP-8120 §2.2.5.3] (see
# validate/turbine_exhaust_checks.py, which pins it). Independent
# plausibility checks: LR-91 865 lbf [RO header], and the theoretical fuel-
# rich GG exhaust Isp dumped into a main nozzle, 141.6 s (O2/CH4) and 282.7 s
# (O2/H2) [Tripropellant-CR150444 Table 2].
EXHAUST_THRUST_EFFICIENCY = 0.96

# LOX -> GOX pressurant heat-exchanger enthalpy rise per kg of oxygen: from
# ~90 K liquid to ~300 K gas. Tier 3 - a standard O2 property value (NIST
# webbook order of magnitude: ~213 kJ/kg latent + ~0.92 kJ/kg-K x ~200 K
# sensible), NOT from a claude_lit source; no H-1 GOX flow or outlet
# temperature is published either ([H1-Man] describes the hardware only).
LOX_TO_GOX_DH_J_KG = 4.0e5
# Warn when the heat exchanger chills the exhaust below this: fuel-rich
# hydrocarbon exhaust starts condensing heavy species / water well above
# ambient. Tier 3, an arbitrary-but-reasonable warn threshold.
EXHAUST_T_FLOOR_K = 450.0
# A turbine left with less pressure ratio than this by its back pressure is
# doing little work per kg - warn (the GG flow balloons). Tier 3 threshold.
TURBINE_PR_LOW_WARN = 6.0


def effective_mode(mode):
    """Unknown/blank -> the default (overboard duct)."""
    return mode if mode in MODES else DEFAULT_MODE


def gas_constant_j_kgk(cp, gamma):
    """Specific gas constant of the ideal drive gas the turbine model uses."""
    return cp * (gamma - 1.0) / gamma


def critical_pressure_ratio(gamma):
    """Sonic static / total pressure, p*/p0 = (2/(gamma+1))^(gamma/(gamma-1))."""
    return (2.0 / (gamma + 1.0)) ** (gamma / (gamma - 1.0))


def design_ambient_pa(main_nozzle_separated_at_sl):
    """The ambient the overboard/aspirator exhaust is designed to leave into:
    sea level for an engine whose main nozzle runs attached at sea level (a
    booster), vacuum for one that separates there (an upper-stage nozzle)."""
    return 0.0 if main_nozzle_separated_at_sl else PA_SEA_LEVEL


def discharge_pressure_pa(mode, ambient_pa, local_static_pa):
    """Static pressure the exhaust discharges into, per mode."""
    return local_static_pa if effective_mode(mode) == "nozzle_injection" else ambient_pa


def exhaust_loss_ratio(mode):
    """Turbine outlet / exhaust-exit total pressure for the mode: the
    injection manifold + slots (F-1-anchored) or the plain duct / aspirator
    slot (H-1-anchored)."""
    return (EXHAUST_INJECTION_PRESSURE_RATIO if effective_mode(mode) == "nozzle_injection"
            else EXHAUST_DUCT_PRESSURE_RATIO)


def required_turbine_outlet_pa(gamma, discharge_pa, mode=DEFAULT_MODE):
    """Turbine outlet total pressure needed for the exhaust to leave sonic
    into discharge_pa after the mode's lumped duct/manifold/slot losses."""
    return discharge_pa / critical_pressure_ratio(gamma) * exhaust_loss_ratio(mode)


def turbine_pressure_ratio(p_in_pa, p_out_required_pa, pr_cap):
    """(PR, back_pressure_limited): the turbine takes the full cap unless the
    exhaust's back pressure leaves it less."""
    if p_out_required_pa <= 0.0:
        return pr_cap, False
    pr_avail = p_in_pa / p_out_required_pa
    if pr_avail < pr_cap:
        return max(pr_avail, 1.05), True
    return pr_cap, False


def _mach_from_pressure_ratio(p0_over_p, gamma):
    return math.sqrt(2.0 / (gamma - 1.0) * (p0_over_p ** ((gamma - 1.0) / gamma) - 1.0))


def exhaust_stream(mode, *, mdot_kgs, tin_k, cp, gamma, dh_actual_j_kg, p_turbine_out_pa,
                   discharge_pa, main_exit_static_pa, main_exit_dia_m,
                   nozzle_eps=1.0, cant_deg=0.0, roll_arm_m=None,
                   hx_gox_kgs=0.0, lox_pair=True, pa_sl=PA_SEA_LEVEL):
    """The spent-drive-gas stream: state, back pressure, exit, thrust and Isp.

    mdot_kgs          turbine (GG / tap-off) flow
    dh_actual_j_kg    turbine specific work actually extracted (cycles result)
    p_turbine_out_pa  turbine outlet total pressure (= p_in / PR)
    discharge_pa      static pressure the exit discharges into (design point)
    main_exit_static_pa / main_exit_dia_m   main nozzle exit (injection mode
                      expands to its static; aspirator slot rides its lip)
    nozzle_eps / cant_deg / roll_arm_m      overboard exhaust-nozzle options
    """
    mode = effective_mode(mode)
    r_gas = gas_constant_j_kgk(cp, gamma)
    m_molar = iso.R_UNIVERSAL / r_gas
    t_turb_out = tin_k - dh_actual_j_kg / cp
    hx_on = hx_gox_kgs > 0.0 and lox_pair and mdot_kgs > 0.0
    hx_dt = hx_gox_kgs * LOX_TO_GOX_DH_J_KG / (mdot_kgs * cp) if hx_on else 0.0
    t_exh = t_turb_out - hx_dt
    p_exit_total = p_turbine_out_pa / exhaust_loss_ratio(mode)

    cstar = iso.c_star(max(t_exh, 1.0), gamma, m_molar)
    crit = critical_pressure_ratio(gamma)
    cant = math.radians(cant_deg) if mode == "overboard_duct" else 0.0
    if mode == "nozzle_injection":
        # expands with the main flow down to the main-nozzle exit static
        pr = p_exit_total / max(main_exit_static_pa, 1.0)
        if pr > 1.0 / crit:
            mach = _mach_from_pressure_ratio(pr, gamma)
            eps_eff = iso.area_ratio_from_mach(mach, gamma)
            pe_pc = 1.0 / pr
        else:
            eps_eff, pe_pc = 1.0, crit
    elif mode == "aspirator":
        eps_eff, pe_pc = 1.0, crit                       # choked annular slot
    else:
        eps_eff = max(1.0, float(nozzle_eps))
        pe_pc = crit if eps_eff <= 1.0 + 1e-9 else iso.pe_over_pc_from_eps(eps_eff, gamma)

    cf_vac = iso.cf_vacuum(gamma, pe_pc, eps_eff)
    throat_area = mdot_kgs * cstar / p_exit_total if p_exit_total > 0 else 0.0
    exit_area = eps_eff * throat_area
    isp_vac_ideal = cstar * cf_vac / iso.G0
    isp_vac = isp_vac_ideal * EXHAUST_THRUST_EFFICIENCY * math.cos(cant)
    # sea level: the pressure-area term against ambient, along the axis
    isp_sl = isp_vac - (pa_sl * exit_area / mdot_kgs / iso.G0 * math.cos(cant)
                        if mdot_kgs > 0 else 0.0)
    isp_sl = max(isp_sl, 0.0)
    exit_static = p_exit_total * pe_pc
    f_vac_total = isp_vac_ideal * EXHAUST_THRUST_EFFICIENCY * mdot_kgs * iso.G0
    side_force = f_vac_total * math.sin(cant)
    arm = roll_arm_m if roll_arm_m is not None else 0.5 * main_exit_dia_m

    out = dict(
        mode=mode, mdot_kgs=mdot_kgs, gas_constant_j_kgk=r_gas, m_molar=m_molar,
        gamma=gamma, cp=cp, tin_k=tin_k,
        t_turbine_exit_k=t_turb_out, hx_on=hx_on, hx_gox_kgs=hx_gox_kgs if hx_on else 0.0,
        hx_delta_t_k=hx_dt, hx_duty_w=hx_gox_kgs * LOX_TO_GOX_DH_J_KG if hx_on else 0.0,
        t_exhaust_k=t_exh,
        p_turbine_out_pa=p_turbine_out_pa, p_exit_total_pa=p_exit_total,
        p_exit_static_pa=exit_static, discharge_pa=discharge_pa,
        cstar_ms=cstar, eps_eff=eps_eff, cf_vac=cf_vac,
        throat_area_m2=throat_area, exit_area_m2=exit_area,
        isp_vac_s=isp_vac, isp_sl_s=isp_sl,
        thrust_vac_n=isp_vac * mdot_kgs * iso.G0, thrust_sl_n=isp_sl * mdot_kgs * iso.G0,
        cant_deg=math.degrees(cant), side_force_n=side_force,
        roll_torque_nm=side_force * arm, roll_arm_m=arm,
        aspirator_gap_m=None, aspirator_slot_dia_m=None,
        choked_at_design=p_exit_total * crit >= discharge_pa * (1.0 - 1e-9),
    )
    if mode == "nozzle_injection" and throat_area > 0:
        # the injection slots are the stream's sonic throat (it leaves them
        # sonic into the local static): slot area, gas speed and density there
        # feed the TN D-3836 gas-film correlation (gas_film_effectiveness_profile)
        v_slot = math.sqrt(2.0 * gamma / (gamma + 1.0) * r_gas * max(t_exh, 1.0))
        out.update(slot_area_m2=throat_area, slot_velocity_ms=v_slot,
                   slot_density_kg_m3=mdot_kgs / (throat_area * v_slot))
    if mode == "aspirator" and main_exit_dia_m > 0:
        # the choked slot's area is its sonic throat; it rides just outside the
        # main exit lip (the H-1's is over the fuel-return manifold [H1-Man])
        out["aspirator_slot_dia_m"] = main_exit_dia_m
        out["aspirator_gap_m"] = throat_area / (math.pi * main_exit_dia_m)
    return out


def film_mdot_ratio_to_fuel(mdot_exhaust_kgs, mdot_fuel_chamber_kgs):
    """Exhaust flow / chamber fuel flow - REPORT ONLY since 2026-09-25 (the
    gas film used to be run through the liquid nozzle-slot law with this as
    its strength; it now uses gas_film_effectiveness_profile)."""
    return mdot_exhaust_kgs / mdot_fuel_chamber_kgs if mdot_fuel_chamber_kgs > 0 else 0.0


# Gas-film (injection mode) constants. Prandtl number of the fuel-rich exhaust
# for its thermal diffusivity alpha = mu / (rho Pr) - Tier 3, a typical
# combustion-gas value; mu is plumbing.EXHAUST_GAS_VISCOSITY_PA_S.
EXHAUST_GAS_PRANDTL = 0.7
# Effectiveness ceiling right at the slot - Tier 3 guard (the correlation runs
# to eta = 1 at x = 0; a real slot lip / mixing never gives a perfect wall).
GAS_FILM_ETA_MAX = 0.95
# [TN-D3836] correlates out to ~100 slot heights downstream; past that its
# prediction is CONSERVATIVE (over-predicted wall temperature) - reported.
GAS_FILM_VALID_SLOT_HEIGHTS = 100.0
# SP-8124's flow-minimising gaseous film / core velocity ratio band [SP-8124
# §3.5.3 p.88] - an informational comparison, not a check.
GAS_FILM_VELOCITY_RATIO_BAND = (0.9, 1.15)


def gas_film_effectiveness_profile(xs_m, rs_m, throat_dia_m, inject_eps, hg_w_m2k, mdot_c_kgs,
                                   cp_c, slot_area_m2, v_gas_ms, alpha_c_m2_s):
    """Turbine-exhaust gas film on the nozzle wall downstream of the injection
    station - the modified Hatch-Papell correlation of [TN-D3836 p.8-9] in its
    tangential-injection working form (K = 0, f(Vg/Vc) = 1, no angle term):

        eta(x) = exp[ -( integral_0^x h_g L ds ) / (mdot_c cp_c) * (S Vg / alpha_c)^(1/8) ]

    L = local circumference 2 pi r, s = wall arc length from the slot, S = slot
    height = slot area / the injection-station circumference, Vg = main-gas
    velocity at the slot (held constant, as [TN-D3836] did), alpha_c = coolant
    thermal diffusivity. The integrated h_g L (not a local value) is that
    report's key finding for an accelerating nozzle flow. eta is capped at
    GAS_FILM_ETA_MAX. Returns dict(phi = 1 - eta per station (1 upstream of
    the slot), eta, i_slot, slot_h_m, x_over_s (per station, 0 upstream),
    i_valid_end = last station within GAS_FILM_VALID_SLOT_HEIGHTS), or None
    if the slot lies beyond the contour or the inputs are degenerate."""
    xs = np.asarray(xs_m, dtype=float)
    rs = np.asarray(rs_m, dtype=float)
    hg = np.asarray(hg_w_m2k, dtype=float)
    n = len(xs)
    if (n < 2 or throat_dia_m <= 0 or mdot_c_kgs <= 0 or cp_c <= 0 or slot_area_m2 <= 0
            or v_gas_ms <= 0 or alpha_c_m2_s <= 0):
        return None
    rt = 0.5 * throat_dia_m
    thr = int(np.argmin(rs))
    i_slot = next((i for i in range(thr + 1, n) if (rs[i] / rt) ** 2 >= inject_eps), None)
    if i_slot is None:
        return None
    slot_h = slot_area_m2 / (2.0 * math.pi * rs[i_slot])
    seg = np.hypot(np.diff(xs), np.diff(rs))
    s_arc = np.concatenate([[0.0], np.cumsum(seg)])
    hl = hg * 2.0 * math.pi * rs
    integ = np.concatenate([[0.0], np.cumsum(0.5 * (hl[1:] + hl[:-1]) * seg)])
    integ = np.where(np.arange(n) >= i_slot, integ - integ[i_slot], 0.0)
    group = (slot_h * v_gas_ms / alpha_c_m2_s) ** 0.125 / (mdot_c_kgs * cp_c)
    eta = np.where(np.arange(n) >= i_slot, np.minimum(np.exp(-integ * group), GAS_FILM_ETA_MAX),
                   0.0)
    x_over_s = np.where(np.arange(n) >= i_slot, (s_arc - s_arc[i_slot]) / slot_h, 0.0)
    within = np.nonzero((np.arange(n) >= i_slot) & (x_over_s <= GAS_FILM_VALID_SLOT_HEIGHTS))[0]
    return dict(phi=1.0 - eta, eta=eta, i_slot=i_slot, slot_h_m=slot_h, x_over_s=x_over_s,
                i_valid_end=int(within[-1]) if len(within) else i_slot)


# --------------------------------------------------------------------------
# Hardware: the duct bore, the mode's termination (overboard exhaust nozzle /
# aspirator shroud + inlet collar / injection manifold torus), the optional
# heat-exchanger can, and their mass. Geometry/mass only - the performance
# above never reads it. The duct RUN itself is a physics/plumbing.py run on
# the "turbine_exhaust" host (rooted on hardware["exhaust"], closed onto the
# turbine's exhaust port), massed there.
# --------------------------------------------------------------------------
# Duct gas velocity target, as a Mach number at the turbine exit state. Tier 3
# (typical hot-gas ducting keeps M ~0.2-0.3 to hold friction/bend losses down;
# not from a claude_lit source).
TURBINE_EXHAUST_DUCT_MACH = 0.25
# Hot-gas hardware material: Haynes 230 stands in for [SP-8120]'s Hastelloy C /
# Inconel 625 / 347 CRES and [H1-Man]'s Hastelloy C aspirator (closest catalog
# Ni superalloy; density/allowable from materials.py).
EXHAUST_HARDWARE_MATERIAL = "haynes_230"
EXHAUST_SHEET_MIN_GAUGE_M = 1.0e-3     # shroud / nozzle / can sheet floor - Tier 3
# Overboard exhaust-nozzle placement: axial station as a fraction of the
# throat -> exit length, standing off the wall by this x its exit dia. Tier 3
# cosmetic (RS-68/LR-87 ducts run aft alongside the bell).
OUTLET_STATION_FRACTION = 0.6
OUTLET_STANDOFF_EXIT_DIA_MULT = 1.0
OUTLET_HALF_ANGLE_DEG = 15.0           # conical exhaust-nozzle divergence - Tier 3
# Heat-exchanger can around the duct (H-1 [H1-Man §1-47]): dia / length as
# multiples of the duct bore; mass = 2 x the can shell (coils + manifolds
# lumped). Tier 3 - [H1-Man] gives the construction, no dimensions.
HX_CAN_DIA_DUCT_MULT = 2.5
HX_CAN_LENGTH_DUCT_MULT = 3.0
HX_MASS_SHELL_MULT = 2.0
INJECTION_MANIFOLD_TAPER_BLEND = 0.5
# Aspirator annulus at its forward (inlet) end is sized for the duct velocity;
# it narrows linearly to the choked exit slot.


def _material():
    from . import materials
    return materials.MATERIALS[EXHAUST_HARDWARE_MATERIAL]


def duct_state(exh):
    """Gas density / sonic speed / velocity / full-flow bore of the exhaust duct
    at the turbine-exit state."""
    r_gas, g = exh["gas_constant_j_kgk"], exh["gamma"]
    t = max(exh["t_turbine_exit_k"], 1.0)
    rho = exh["p_turbine_out_pa"] / (r_gas * t)
    a = math.sqrt(g * r_gas * t)
    v = TURBINE_EXHAUST_DUCT_MACH * a
    area = exh["mdot_kgs"] / (rho * v) if rho > 0 and v > 0 else 0.0
    return dict(rho_kg_m3=rho, sonic_ms=a, velocity_ms=v, dia_m=2.0 * math.sqrt(area / math.pi))


def _sheet_t(pressure_pa, radius_m, mat):
    from . import mass_model
    return max(mass_model.wall_thickness_m(pressure_pa, radius_m, mat.allowable_stress_pa),
               EXHAUST_SHEET_MIN_GAUGE_M)


def _station_at_eps(xs, rs, throat_r, eps):
    """First supersonic station index with (r/rt)^2 >= eps (else the exit)."""
    it = int(min(range(len(rs)), key=lambda i: rs[i]))
    for i in range(it, len(rs)):
        if (rs[i] / throat_r) ** 2 >= eps:
            return i
    return len(rs) - 1


def size_hardware(exh, *, xs, rs, throat_dia_m, inject_eps=10.0,
                  aspirator_fwd_length_frac=0.30, aspirator_overhang_frac=0.05,
                  nozzle_eps=1.0, cant_deg=0.0, attach_angle_deg=0.0):
    """Exhaust hardware for the stream `exh` (exhaust_stream's dict + its
    "mode") on the main contour (xs, rs; engine axis +x, injector at x=0).
    Returns a dict with:
      mode, duct {rho_kg_m3, sonic_ms, velocity_ms, dia_m}, material
      exhaust     the plumbing hook the "turbine_exhaust" run roots on (a
                  manifold.py-shaped ring dict; the overboard outlet is a
                  point "ring" whose tube radius is the duct bore)
      manifold    injection torus ring dict, or None
      aspirator   {"xs", "r_inner", "r_outer", "thickness_m", "gap_exit_m",
                   "collar"} or None
      outlet      overboard exhaust nozzle {"pos", "dir", "throat_dia_m",
                   "exit_dia_m", "length_m", "cant_deg", "thickness_m"} or None
      hx          {"dia_m", "length_m", "mass_kg"} or None
      mass_kg     termination + heat-exchanger mass (the duct run is massed
                  by plumbing.py)
    """
    from . import manifold
    mode = effective_mode(exh.get("mode"))
    mat = _material()
    duct = duct_state(exh)
    d_duct = duct["dia_m"]
    mdot = exh["mdot_kgs"]
    p_out = exh["p_turbine_out_pa"]
    xs = [float(x) for x in xs]
    rs = [float(r) for r in rs]
    rt = 0.5 * float(throat_dia_m)
    it = int(min(range(len(rs)), key=lambda i: rs[i]))
    x_t, x_e, r_e = xs[it], xs[-1], rs[-1]
    ang = math.radians(attach_angle_deg)
    rho_scale = mat.density_kg_m3 / manifold.MANIFOLD_DENSITY_KG_M3
    out = dict(mode=mode, duct=duct, material=EXHAUST_HARDWARE_MATERIAL, manifold=None,
               aspirator=None, outlet=None, hx=None, mass_kg=0.0)

    def _ring(x, r_wall, v, taper_blend=0.0):
        r_flow = manifold.required_flow_radius_m(0.5 * mdot, duct["rho_kg_m3"], v)
        wall = max(manifold.manifold_wall_thickness_m(p_out, r_flow, mat.allowable_stress_pa),
                   EXHAUST_SHEET_MIN_GAUGE_M)
        ring = manifold._assemble(mdot, v, attach_angle_deg, r_wall + r_flow + wall, x,
                                  r_flow, wall, p_out, taper_blend=taper_blend, split=True)
        ring["mass_kg"] *= rho_scale
        return ring

    if mode == "nozzle_injection":
        i = _station_at_eps(xs, rs, rt, inject_eps)
        # the F-1 torus narrows from its inlet round the engine [F1-Man
        # §1-18]; half-way between constant area and constant velocity, the
        # SP-8087 "between the two" convention the fuel/ox rings use
        ring = _ring(xs[i], rs[i], duct["velocity_ms"], taper_blend=INJECTION_MANIFOLD_TAPER_BLEND)
        out["manifold"] = out["exhaust"] = ring
        out["mass_kg"] += ring["mass_kg"]
    elif mode == "aspirator":
        l_noz = x_e - x_t
        x0 = x_e - max(0.0, min(1.0, aspirator_fwd_length_frac)) * l_noz
        x1 = x_e + max(0.0, aspirator_overhang_frac) * 2.0 * r_e
        gap_e = exh.get("aspirator_gap_m") or 0.0
        i0 = min(range(len(xs)), key=lambda k: abs(xs[k] - x0))
        r0 = rs[i0]
        a_in = mdot / (duct["rho_kg_m3"] * duct["velocity_ms"])
        h0 = max(a_in / (2.0 * math.pi * r0), gap_e)
        n = 24
        sx, sr = [], []
        for k in range(n + 1):
            x = x0 + (x1 - x0) * k / n
            r_wall = _interp(x, xs, rs) if x <= x_e else r_e
            f = min(1.0, (x - x0) / max(x_e - x0, 1e-9))
            sx.append(x)
            sr.append(r_wall + h0 + (gap_e - h0) * f)
        th = _sheet_t(exh["p_exit_total_pa"], max(sr), mat)
        area = sum(2.0 * math.pi * 0.5 * (sr[k] + sr[k + 1]) * math.hypot(
            sx[k + 1] - sx[k], sr[k + 1] - sr[k]) for k in range(n))
        collar = _ring(x0, r0 + h0, duct["velocity_ms"])
        out["aspirator"] = dict(xs=sx, r_inner=sr, r_outer=[r + th for r in sr],
                                thickness_m=th, gap_exit_m=gap_e, annulus_inlet_m=h0,
                                collar=collar, shroud_mass_kg=area * th * mat.density_kg_m3)
        out["exhaust"] = collar
        out["mass_kg"] += out["aspirator"]["shroud_mass_kg"] + collar["mass_kg"]
    else:
        # overboard: a point hook at the exhaust nozzle's inlet, beside the bell
        x = x_t + OUTLET_STATION_FRACTION * (x_e - x_t)
        r_wall = _interp(x, xs, rs)
        a_t = exh["throat_area_m2"]
        d_t = 2.0 * math.sqrt(max(a_t, 0.0) / math.pi)
        d_ex = d_t * math.sqrt(max(1.0, float(nozzle_eps)))
        r_hook = r_wall + OUTLET_STANDOFF_EXIT_DIA_MULT * max(d_ex, d_duct) + 0.5 * d_duct
        cant = math.radians(cant_deg)
        u_r = (0.0, math.cos(ang), math.sin(ang))
        ndir = (math.cos(cant), math.sin(cant) * u_r[1], math.sin(cant) * u_r[2])
        conv = max(0.0, 0.5 * (d_duct - d_t)) / math.tan(math.radians(45.0))
        div = max(0.0, 0.5 * (d_ex - d_t)) / math.tan(math.radians(OUTLET_HALF_ANGLE_DEG))
        th = _sheet_t(p_out, 0.5 * d_duct, mat)
        length = conv + div
        mean_r = 0.25 * (d_duct + d_ex)
        out["outlet"] = dict(pos=(x, r_hook * u_r[1], r_hook * u_r[2]), dir=ndir,
                             inlet_dia_m=d_duct, throat_dia_m=d_t, exit_dia_m=d_ex,
                             converge_length_m=conv, length_m=length, cant_deg=cant_deg,
                             thickness_m=th,
                             mass_kg=2.0 * math.pi * mean_r * max(length, d_duct) * th
                             * mat.density_kg_m3)
        k = th / (0.5 * d_duct) if d_duct > 0 else 0.0
        out["exhaust"] = {
            "attach_axial_station_m": x, "attach_radial_offset_m": r_hook,
            "attach_angular_position_deg": attach_angle_deg,
            "attach_direction_xyz": (-1.0, 0.0, 0.0),
            "inner_diameter_m": d_duct, "mdot_kgs": mdot,
            "design_feed_velocity_ms": duct["velocity_ms"],
            "flow_radius_m": 0.5 * d_duct, "outer_radius_m": 0.5 * d_duct * (1.0 + k),
            "wall_thickness_m": th, "feed_wall_thickness_m": th, "thin_wall_ratio": k,
            "major_radius_m": r_hook, "feed_pressure_pa": p_out, "mass_kg": 0.0,
            "point_hook": True,
        }
        out["mass_kg"] += out["outlet"]["mass_kg"]
    if exh.get("hx_on"):
        d_can = HX_CAN_DIA_DUCT_MULT * d_duct
        l_can = HX_CAN_LENGTH_DUCT_MULT * d_duct
        th = _sheet_t(p_out, 0.5 * d_can, mat)
        m = HX_MASS_SHELL_MULT * (math.pi * d_can * l_can + 0.5 * math.pi * d_can ** 2) * th \
            * mat.density_kg_m3
        out["hx"] = dict(dia_m=d_can, length_m=l_can, thickness_m=th, mass_kg=m,
                         gox_kgs=exh.get("hx_gox_kgs", 0.0), duty_w=exh.get("hx_duty_w", 0.0))
        out["mass_kg"] += m
    return out


def _interp(x, xs, rs):
    if x <= xs[0]:
        return rs[0]
    for k in range(1, len(xs)):
        if xs[k] >= x:
            f = (x - xs[k - 1]) / max(xs[k] - xs[k - 1], 1e-12)
            return rs[k - 1] + f * (rs[k] - rs[k - 1])
    return rs[-1]


def _self_test():
    print("physics/turbine_exhaust.py self-test")
    ok = True
    psi = 6894.757

    # (1) H-1 back pressure: sea-level booster, sonic exit to sea level,
    # turbine inlet 0.855 x 689.3 psia -> exit 33.8 psia, PR ~17.7 [H1-Man].
    g_rp1, cp_rp1 = 1.13, 2100.0
    p_in = GG_TURBINE_INLET_PC_FRACTION * 689.3 * psi
    p_req = required_turbine_outlet_pa(g_rp1, discharge_pressure_pa("aspirator", PA_SEA_LEVEL, 0.0))
    pr, limited = turbine_pressure_ratio(p_in, p_req, 22.0)
    c1 = abs(p_req / psi - 33.8) / 33.8 < 0.01 and limited and abs(pr - 17.7) / 17.7 < 0.02
    print(f"  (1) H-1 turbine exit {p_req/psi:.1f} psia (real 33.8), PR {pr:.2f} (real ~17.7), "
          f"back-pressure limited={limited}  [{'OK' if c1 else 'FAIL'}]")
    ok &= c1
    # (1b) Titan I independent check: 30 psi [SP-8120] within 15 %
    c1b = abs(p_req / psi - 30.0) / 30.0 < 0.15
    print(f"  (1b) Titan I exhaust 30 psi vs model {p_req/psi:.1f} psia  [{'OK' if c1b else 'FAIL'}]")
    ok &= c1b
    # (1c) vacuum discharge -> the flat cap
    pr_v, lim_v = turbine_pressure_ratio(p_in, required_turbine_outlet_pa(g_rp1, 0.0), 22.0)
    c1c = pr_v == 22.0 and not lim_v
    print(f"  (1c) vacuum discharge -> PR cap {pr_v:.1f}  [{'OK' if c1c else 'FAIL'}]")
    ok &= c1c

    # (1d) F-1 injection back pressure [F1-Man Fig 1-16/3-14]: eps-10 static
    # of the real 1,125 psia chamber (pe/pc 0.01193) -> turbine exit 58 psia;
    # inlet 0.855 x 1,125 -> PR vs the real 945/58 = 16.3
    p_stat = 1125.0 * psi * 0.01193
    p_req_f1 = required_turbine_outlet_pa(g_rp1, discharge_pressure_pa("nozzle_injection", 0.0,
                                                                         p_stat), "nozzle_injection")
    pr_f1, lim_f1 = turbine_pressure_ratio(GG_TURBINE_INLET_PC_FRACTION * 1125.0 * psi,
                                           p_req_f1, 22.0)
    c1d = abs(p_req_f1 / psi - 58.0) / 58.0 < 0.01 and lim_f1 and abs(pr_f1 - 16.3) / 16.3 < 0.05
    print(f"  (1d) F-1 injection turbine exit {p_req_f1/psi:.1f} psia (real 58), PR {pr_f1:.2f} "
          f"(real 16.3)  [{'OK' if c1d else 'FAIL'}]")
    ok &= c1d

    # (2) H-1 aspirator slot gap ~0.440 in [H1-Man §1-51]: 17.22 lb/s at the
    # turbine's 4007 hp, 45.62 in exit. Plausibility band x0.6-1.5 (the slot
    # is modelled sonic at the exit dia; the real clearance rides outside the
    # fuel-return manifold).
    mdot = 17.22 * 0.45359
    dh = 4007.0 * 745.7 / mdot
    a = exhaust_stream("aspirator", mdot_kgs=mdot, tin_k=1050.0, cp=cp_rp1, gamma=g_rp1,
                       dh_actual_j_kg=dh, p_turbine_out_pa=p_req, discharge_pa=PA_SEA_LEVEL,
                       main_exit_static_pa=60e3, main_exit_dia_m=45.62 * 0.0254)
    gap_in = a["aspirator_gap_m"] / 0.0254
    c2 = 0.6 * 0.440 <= gap_in <= 1.5 * 0.440 and a["choked_at_design"]
    print(f"  (2) H-1 aspirator gap {gap_in:.3f} in (real 0.440), exhaust {a['t_exhaust_k']:.0f} K, "
          f"Isp vac/SL {a['isp_vac_s']:.0f}/{a['isp_sl_s']:.0f} s  [{'OK' if c2 else 'FAIL'}]")
    ok &= c2

    # (3) mode ordering at one operating point (vacuum Isp): injection
    # (expands to the main exit) and a shaped overboard nozzle both beat the
    # sonic duct (== aspirator); injection gains as the main exit static
    # pressure drops (a longer main nozzle); cant costs axial Isp and makes a
    # roll torque.
    kw = dict(mdot_kgs=mdot, tin_k=1050.0, cp=cp_rp1, gamma=g_rp1, dh_actual_j_kg=dh,
              p_turbine_out_pa=p_req, discharge_pa=PA_SEA_LEVEL, main_exit_static_pa=20e3,
              main_exit_dia_m=1.16)
    inj = exhaust_stream("nozzle_injection", **kw)
    duct = exhaust_stream("overboard_duct", **kw)
    noz = exhaust_stream("overboard_duct", nozzle_eps=4.0, **kw)
    cant = exhaust_stream("overboard_duct", nozzle_eps=4.0, cant_deg=20.0, **kw)
    inj_lo = exhaust_stream("nozzle_injection", **dict(kw, main_exit_static_pa=5e3))
    c3 = (inj["isp_vac_s"] > duct["isp_vac_s"] and noz["isp_vac_s"] > duct["isp_vac_s"]
          and inj_lo["isp_vac_s"] > inj["isp_vac_s"]
          and abs(duct["isp_vac_s"] - a["isp_vac_s"]) < 1e-9
          and cant["isp_vac_s"] < noz["isp_vac_s"] and cant["roll_torque_nm"] > 0
          and duct["roll_torque_nm"] == 0.0)
    print(f"  (3) Isp vac: injection {inj['isp_vac_s']:.0f} (to 20 kPa) / {inj_lo['isp_vac_s']:.0f} "
          f"(to 5 kPa), nozzle eps4 {noz['isp_vac_s']:.0f} > duct {duct['isp_vac_s']:.0f} "
          f"(= aspirator); 20 deg cant {cant['isp_vac_s']:.0f} s, "
          f"roll torque {cant['roll_torque_nm']:.0f} N.m  [{'OK' if c3 else 'FAIL'}]")
    ok &= c3

    # (4) heat exchanger lowers the exhaust temperature by duty / (mdot cp),
    # only on a LOX pair
    hx = exhaust_stream("overboard_duct", hx_gox_kgs=0.5, **kw)
    hx_off = exhaust_stream("overboard_duct", hx_gox_kgs=0.5, lox_pair=False, **kw)
    want = 0.5 * LOX_TO_GOX_DH_J_KG / (mdot * cp_rp1)
    c4 = (abs((duct["t_exhaust_k"] - hx["t_exhaust_k"]) - want) < 1e-9
          and hx["isp_vac_s"] < duct["isp_vac_s"] and hx_off["t_exhaust_k"] == duct["t_exhaust_k"])
    print(f"  (4) heat exchanger 0.5 kg/s GOX: exhaust {duct['t_exhaust_k']:.0f} -> "
          f"{hx['t_exhaust_k']:.0f} K (-{want:.0f} K), non-LOX pair ignored  "
          f"[{'OK' if c4 else 'FAIL'}]")
    ok &= c4

    # (5) the exhaust leaves sonic into its discharge at the design point
    c5 = all(x["choked_at_design"] for x in (duct, noz, a))
    print(f"  (5) exhaust exit choked at the design discharge pressure  [{'OK' if c5 else 'FAIL'}]")
    ok &= c5

    # (7) gas film [TN-D3836]: on a toy eps-16 bell, the film decays
    # monotonically from the slot, is absent upstream of it, and strengthens
    # with more flow or a higher cp (the mdot_c cp_c denominator)
    xs_g = np.linspace(0.0, 1.0, 81)
    rs_g = 0.1 + 0.3 * xs_g                    # throat at x=0, eps 16 at the exit
    hg_g = np.full(81, 2000.0)
    base_g = (xs_g, rs_g, 0.2, 10.0, hg_g)
    g1 = gas_film_effectiveness_profile(*base_g, 5.0, 2100.0, 0.01, 2800.0, 1e-4)
    g2 = gas_film_effectiveness_profile(*base_g, 10.0, 2100.0, 0.01, 2800.0, 1e-4)
    g3 = gas_film_effectiveness_profile(*base_g, 5.0, 4200.0, 0.01, 2800.0, 1e-4)
    i0 = g1["i_slot"]
    c7 = (g1 is not None and np.all(g1["phi"][:i0] == 1.0)
          and np.all(np.diff(g1["eta"][i0:]) <= 1e-12) and g1["eta"][i0] == GAS_FILM_ETA_MAX
          and np.allclose(g2["eta"][i0 + 1:], g3["eta"][i0 + 1:])
          and np.all(g2["eta"][i0:] >= g1["eta"][i0:]) and g2["eta"][-1] > g1["eta"][-1]
          and gas_film_effectiveness_profile(*base_g, 0.0, 2100.0, 0.01, 2800.0, 1e-4) is None)
    print(f"  (7) gas film: eta {g1['eta'][i0]:.2f} at the slot -> {g1['eta'][-1]:.2f} at the "
          f"exit (2x flow: {g2['eta'][-1]:.2f}), slot {g1['slot_h_m']*1e3:.0f} mm  "
          f"[{'OK' if c7 else 'FAIL'}]")
    ok &= bool(c7)

    # (6) hardware: a toy bell contour; each mode sizes its termination
    import numpy as _np
    xs_c = list(_np.linspace(0.0, 1.0, 81))
    rt, re_ = 0.1, 0.1 * math.sqrt(8.0)
    rs_c = [0.18 if x < 0.3 else (0.18 - (0.18 - rt) * (x - 0.3) / 0.1 if x < 0.4 else
            rt + (re_ - rt) * ((x - 0.4) / 0.6) ** 0.8) for x in xs_c]
    hw = {m: size_hardware(dict(exhaust_stream(m, **kw), mode=m), xs=xs_c, rs=rs_c,
                           throat_dia_m=2 * rt, inject_eps=4.0, nozzle_eps=4.0, cant_deg=10.0)
          for m in MODES}
    inj_r = hw["nozzle_injection"]["manifold"]
    asp = hw["aspirator"]["aspirator"]
    outl = hw["overboard_duct"]["outlet"]
    c6 = (inj_r is not None and inj_r["major_radius_m"] > inj_r["flow_radius_m"]
          and abs(asp["r_inner"][-1] - re_ - asp["gap_exit_m"]) < 1e-9
          and asp["annulus_inlet_m"] >= asp["gap_exit_m"]
          and outl["exit_dia_m"] > outl["throat_dia_m"]
          and hw["overboard_duct"]["exhaust"]["point_hook"]
          and all(h["mass_kg"] > 0 and h["duct"]["dia_m"] > 0 for h in hw.values()))
    print(f"  (6) hardware: duct {hw['aspirator']['duct']['dia_m']*1e3:.0f} mm; injection ring "
          f"{inj_r['flow_radius_m']*1e3:.0f} mm bore; aspirator {asp['annulus_inlet_m']*1e3:.0f} -> "
          f"{asp['gap_exit_m']*1e3:.1f} mm annulus; outlet {outl['throat_dia_m']*1e3:.0f} -> "
          f"{outl['exit_dia_m']*1e3:.0f} mm  [{'OK' if c6 else 'FAIL'}]")
    ok &= c6

    print("ALL TURBINE-EXHAUST SELF-TESTS OK" if ok else "*** TURBINE-EXHAUST SELF-TEST FAILED ***")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if _self_test() else 1)
