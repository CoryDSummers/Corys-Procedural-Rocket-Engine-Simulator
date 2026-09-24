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
   margin, reverse-solved on the H-1). Turbine PR = min(cap, p_in / p_out),
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
# Pc. Tier 2, single real anchor: H-1 turbine inlet 599.0 psia total vs
# injector-end Pc 689.3 psia (200K rating) = 0.869 [H1-Man Fig 1-47/1-18].
GG_TURBINE_INLET_PC_FRACTION = 0.869
# Tap-off drive gas is bled from the main chamber through a tapoff valve and
# film/mix cooling - Tier 3: no turbine-inlet pressure in hand for the J-2S
# ([AEDC-J2S] gives sensor ranges only). Taken equal to the GG value.
TAP_OFF_TURBINE_INLET_PC_FRACTION = 0.869

# Turbine outlet total pressure / exhaust-exit total pressure: duct, heat-
# exchanger and slot losses plus a choking margin, lumped. Tier 2, REVERSE-
# SOLVED on the H-1 (a sea-level booster whose exhaust leaves sonic through
# an aspirator slot / duct exit to sea-level ambient): turbine exit 33.8 psia
# = 233.04 kPa [H1-Man Fig 1-47] vs the sonic-to-sea-level requirement
# 101325 / p*/p0(1.13) = 175.2 kPa -> 1.330. Independent check: Titan I
# exhaust at 30 psi [SP-8120] (sea-level booster, through a superheater) is
# within ~13% of the 33.8 psia this gives (self-test).
EXHAUST_DUCT_PRESSURE_RATIO = 1.330

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


def required_turbine_outlet_pa(gamma, discharge_pa):
    """Turbine outlet total pressure needed for the exhaust to leave sonic
    into discharge_pa after the lumped duct/slot losses."""
    return discharge_pa / critical_pressure_ratio(gamma) * EXHAUST_DUCT_PRESSURE_RATIO


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
    p_exit_total = p_turbine_out_pa / EXHAUST_DUCT_PRESSURE_RATIO

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
    if mode == "aspirator" and main_exit_dia_m > 0:
        # the choked slot's area is its sonic throat; it rides just outside the
        # main exit lip (the H-1's is over the fuel-return manifold [H1-Man])
        out["aspirator_slot_dia_m"] = main_exit_dia_m
        out["aspirator_gap_m"] = throat_area / (math.pi * main_exit_dia_m)
    return out


def film_mdot_ratio_to_fuel(mdot_exhaust_kgs, mdot_fuel_chamber_kgs):
    """Injection-mode gas film strength, expressed like the nozzle slot film
    (cooling.nozzle_film_effectiveness_profile's film_mdot_ratio = fraction of
    the chamber FUEL flow). Tier 3 - that effectiveness law was written for a
    liquid-fuel film and has no cp/temperature term (SP-8124 missing); a hot
    gas film is weaker per kg than a vaporising liquid one, so treat the
    resulting wall temperatures as optimistic."""
    return mdot_exhaust_kgs / mdot_fuel_chamber_kgs if mdot_fuel_chamber_kgs > 0 else 0.0


def _self_test():
    print("physics/turbine_exhaust.py self-test")
    ok = True
    psi = 6894.757

    # (1) H-1 back pressure: sea-level booster, sonic exit to sea level,
    # turbine inlet 0.869 x 689.3 psia -> exit 33.8 psia, PR ~17.7 [H1-Man].
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

    print("ALL TURBINE-EXHAUST SELF-TESTS OK" if ok else "*** TURBINE-EXHAUST SELF-TEST FAILED ***")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if _self_test() else 1)
