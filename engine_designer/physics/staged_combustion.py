"""
Closed staged-combustion cycles: fuel-rich (FRSC), oxidiser-rich (ORSC), and
full-flow (FFSC). Distinct from a gas generator because:

  * the turbine drive gas is a PREBURNER product - fuel-rich (H2- or
    hydrocarbon-rich, FRSC), oxidiser-rich (O2-rich, heavy, low Cp - ORSC),
    or both (one preburner per turbopump - FFSC);
  * nearly all of one propellant (FRSC/ORSC) or both (FFSC) is routed through the
    preburner and turbine, then rejoins the main chamber - there is NO overboard
    dump, so no bleed Isp penalty;
  * the turbine sits in SERIES with the chamber, so its pressure drop ADDS to the
    discharge pressure of the pump that feeds the preburner.

Pressure chain + power balance (`solve_staged_power_balance`) - the literature's
own prescription, `P_discharge = Pc + sum(downstream drops)`, staged combustion
"+ preburner injector dP + turbine dP + line losses" [SP-8107 3.1.1.1 p.99]:

    P_turb_out  = pc_feed + main-injector dP of that leg   (hot gas enters the MCC)
    P_turb_in   = P_turb_out * PR                          (= preburner pressure)
    P_pb_inj_in = P_turb_in * (1 + preburner injector dP/P)
    discharge   = P_pb_inj_in + regen jacket dP (fuel leg) + line loss

The preburner temperature is a DESIGN INPUT (pair default below, user-
overridable); the turbine PR is SOLVED so that the drive gas delivers exactly the
pump shaft power. Pump discharge / Pc therefore EMERGES, and rises non-linearly
with Pc (SP-8107 Table VI: "a nonlinear function of chamber pressure and may
exceed 2.0 times chamber pressure"). When no PR in [TURBINE_PR_MIN,
TURBINE_PR_MAX] closes the balance the design is infeasible at that Tin - the
staged-cycle Pc ceiling - reported (warn-only) as a power margin < 1, the same
way expander.py reports an expander shortfall.

Replaces the fixed PREBURNER_DRIVE_MULT (2.4 x Pc) / NON_DRIVE_MULT (1.9 x Pc)
discharge multipliers and the fixed TURBINE_PR_STAGED (1.9) of the previous
round - design.py added injector/jacket/line dP ON TOP of those real
discharge/Pc ratios, double-counting (SSME fuel pump came out at 86.9 MW vs the
real HPFTP's ~52 MW [ch12-materials]). The real discharge/Pc figures survive as
a reported plausibility band only (DRIVE_DISCHARGE_OVER_PC_BAND).

Same honesty tier as physics/expander.py: a 1-D model, not a preburner-chemistry
solve. Pinned by validate.py::run_staged_power_balance_check() (SSME, RD-0124,
NK-33) and run_cycle_model_check().
"""
from . import turbopump as tp

# --- preburner drive-gas thermodynamic properties -----------------------------
# FUEL-RICH preburner gas (FRSC, and the fuel side of FFSC). Distinct from the
# skirt-dumped GG-dump mix in design.GG_GAS_PROPERTIES: a higher-pressure,
# turbine-limited preburner.
#   LOX/LH2 tin_k = 1113 K: SSME HPFTP turbine gas "~840 C / 1550 F H2-rich"
#     [ch12-materials] (claude_lit/sources/ch12-materials-liquid-propulsion.md).
#     SOURCED. (Was 950 K, an estimate.) cp/gamma remain Tier-3 estimates.
#   everything else: Tier-3 estimates (unchanged).
PREBURNER_GAS_PROPERTIES = {
    "LOX/LH2":         dict(tin_k=1113.0, cp=8500.0, gamma=1.37),
    "LOX/RP-1":        dict(tin_k=900.0,  cp=2400.0, gamma=1.15),
    "LOX/CH4":         dict(tin_k=900.0,  cp=3400.0, gamma=1.22),  # fuel-rich methane preburner
    "N2O4/MMH":        dict(tin_k=950.0,  cp=2900.0, gamma=1.20),
    "Aerozine-50/NTO": dict(tin_k=950.0,  cp=2900.0, gamma=1.20),
    "Hydrazine":       dict(tin_k=950.0,  cp=2900.0, gamma=1.20),  # unused (monoprop = pressure-fed)
    "H2O2":            dict(tin_k=950.0,  cp=2900.0, gamma=1.20),  # unused (monoprop = pressure-fed)
}

# OXIDISER-RICH preburner gas (ORSC, and the ox side of FFSC). A real ox-rich
# preburner runs at a very high MR (NK-33: MR 58 [NK-33-Mod Table I]) - the gas
# is ~all O2 with a few % CO2/H2O, and it runs COOL because hot O2 attacks the
# turbine:
#   LOX/RP-1 tin_k = 628 K: NK-33 preburner outlet / turbine inlet 670 F
#     [NK-33-Mod Table I]. SOURCED. Independently reproduces RD-0124's real
#     turbine-inlet pressure (29.98 MPa [KBKhA Table 2]) through the solved PR.
#     (Was 1500 K, uncited and calibrated to RD-180 - that value made RD-0124's
#     turbine inlet ~21 MPa.)
#   cp 1050 / gamma 1.35: O2 ideal-gas properties near 600 K (cp ~1000-1050 J/kgK,
#     gamma ~1.35) plus a few % combustion products - DERIVED from standard gas
#     tables for the MR~58 composition, Tier 2.
#   LOX/CH4, LOX/LH2: the SAME O2-dominated gas and the same NK-33 temperature -
#     a TRANSFER (the ox-rich turbine-temperature limit is set by hot-O2 attack,
#     not by the fuel), not an independent source. Tier 3.
#   Storables: unchanged Tier-3 estimates (NTO-rich gas is not O2).
# A high-Pc ORSC design (RD-180 class, 26.7 MPa) does NOT close at 628 K - it
# needs ~>730 K; that is the model telling the user a hotter preburner is needed,
# and the user sets EngineDesign.preburner_tin_k accordingly. No literature
# source for the RD-170/180 preburner temperature is in claude_lit/ yet.
ORSC_GAS_PROPERTIES = {
    "LOX/RP-1":        dict(tin_k=628.0,  cp=1050.0, gamma=1.35),
    "LOX/LH2":         dict(tin_k=628.0,  cp=1050.0, gamma=1.35),
    "LOX/CH4":         dict(tin_k=628.0,  cp=1050.0, gamma=1.35),
    "N2O4/MMH":        dict(tin_k=1100.0, cp=1400.0, gamma=1.25),
    "Aerozine-50/NTO": dict(tin_k=1100.0, cp=1400.0, gamma=1.25),
    "Hydrazine":       dict(tin_k=1100.0, cp=1400.0, gamma=1.25),  # unused
    "H2O2":            dict(tin_k=1100.0, cp=1400.0, gamma=1.25),  # unused
}

# --- turbine pressure-ratio search bounds ------------------------------------
TURBINE_PR_MIN = 1.05          # numerical floor of the PR search - not a physical claim
TURBINE_PR_MAX = 3.0           # search ceiling - Tier 3. Real staged turbines run < ~2
                               # ([SP-8107] "< 1.5" optimum; SSME 1.56-1.59 [SP-8107 Table III])
TURBINE_PR_PLAUSIBLE_MAX = 2.0  # above this the checklist flags an unusually high PR
_PR_SCAN_POINTS = 80
_PR_BISECT_ITERS = 40
_FFSC_OUTER_ITERS = 4

# Real drive-pump discharge / Pc - REPORTED plausibility band only, never an input:
# SSME fuel 46.9/20.6 = 2.28 [ch12-materials]; RD-0124 LOX 33.28/15.53 = 2.14
# [KBKhA Table 2]; NK-33 preburner/Pc 2.21 [NK-33-Mod]; [SP-8107 Table VI] "> 2.0".
DRIVE_DISCHARGE_OVER_PC_BAND = (1.6, 3.5)

# --- preburner flow fraction ---------------------------------------------
PREBURNER_TRICKLE = 0.08      # for FRSC the fuel-rich preburner also burns a small
                               # slug of oxidiser (and vice-versa for ORSC); this is
                               # that slug as a fraction of the OTHER propellant's flow

# --- c* mixing penalty, per cycle -----------------------------------------
STAGED_ETA_CSTAR_PENALTY = {
    "frsc": 0.985,   # two-stage-combustion mixing loss on top of eta_cstar
    "orsc": 0.985,
    "ffsc": 0.993,   # full preburning of both propellants -> better main-injector mixing
}


def preburner_gas(cycle, pair, oxidizer_rich, tin_override_k=0.0):
    """The drive-gas dict for this cycle/side. `tin_override_k` > 0 replaces the
    pair-default preburner temperature (EngineDesign.preburner_tin_k)."""
    table = ORSC_GAS_PROPERTIES if oxidizer_rich else PREBURNER_GAS_PROPERTIES
    gas = dict(table[pair])
    if tin_override_k and tin_override_k > 0.0:
        gas["tin_k"] = float(tin_override_k)
    return gas


def preburner_flow_fraction(cycle, mr):
    """Fraction of total mdot routed through the preburner(s) + turbine(s).
    mdot_fuel = mdot/(1+mr); mdot_ox = mdot - mdot_fuel (per unit total mdot)."""
    f_fuel = 1.0 / (1.0 + mr)
    f_ox = 1.0 - f_fuel
    if cycle == "frsc":
        return min(1.0, f_fuel + PREBURNER_TRICKLE * f_ox)
    if cycle == "orsc":
        return min(1.0, f_ox + PREBURNER_TRICKLE * f_fuel)
    return 1.0   # ffsc: essentially all of both


def _preburner_sides(cycle, mr, gas_fuel_rich, gas_ox_rich):
    """The preburner(s) of this cycle. Each side: which propellant is its main
    (drive) leg, the per-unit-mdot flow of each propellant into it, its gas, and
    which pump(s) its turbine powers."""
    f_fuel = 1.0 / (1.0 + mr)
    f_ox = 1.0 - f_fuel
    t = PREBURNER_TRICKLE
    if cycle == "frsc":
        return [dict(kind="fuel_rich", drive="fuel", flow_fuel=f_fuel, flow_ox=t * f_ox,
                     gas=gas_fuel_rich, powers=("fuel", "ox"))]
    if cycle == "orsc":
        return [dict(kind="oxidizer_rich", drive="ox", flow_fuel=t * f_fuel, flow_ox=f_ox,
                     gas=gas_ox_rich, powers=("fuel", "ox"))]
    # ffsc: all fuel (less a slug) + an ox slug to the fuel-rich side, and vice
    # versa - sums to exactly all of both propellants, as preburner_flow_fraction says.
    return [dict(kind="fuel_rich", drive="fuel", flow_fuel=f_fuel * (1.0 - t), flow_ox=t * f_ox,
                 gas=gas_fuel_rich, powers=("fuel",)),
            dict(kind="oxidizer_rich", drive="ox", flow_fuel=t * f_fuel, flow_ox=f_ox * (1.0 - t),
                 gas=gas_ox_rich, powers=("ox",))]


def _available_dh(gas, eta_turb, pr):
    exponent = (gas["gamma"] - 1.0) / gas["gamma"]
    return gas["cp"] * gas["tin_k"] * eta_turb * (1.0 - pr ** (-exponent))


def solve_staged_power_balance(cycle, pair, mdot, mr, pc_feed, dp_injector_fuel, dp_injector_ox,
                               jacket_dp_pa, line_loss_fuel_pa, line_loss_ox_pa, tank_head_pa,
                               rho_fuel, rho_ox, preburner_inj_dp_frac, efficiency_fn,
                               tin_fuel_rich_k=0.0, tin_ox_rich_k=0.0, boost_drive_dp_pa=(0.0, 0.0)):
    """
    Close the staged-combustion pressure chain + power balance (see module
    docstring). `efficiency_fn(dp_fuel, dp_ox, gas, pr) -> (eta_pf, eta_po, eta_turb)`
    (design.py wraps turbopump_sizing.derive_efficiencies) - re-evaluated per trial
    PR, since pump efficiency depends on head and turbine efficiency on PR.

    `tin_fuel_rich_k` / `tin_ox_rich_k` > 0 override the pair-default temperature
    of the fuel-rich / oxidiser-rich preburner (EngineDesign.preburner_tin_k /
    ox_preburner_tin_k) - separate, since FFSC runs one of each.

    `tank_head_pa`: the main-pump INLET pressure - one value for both legs, or a
    (fuel, ox) pair (turbopump Round 1: computed per leg by design/suction_stage).
    `boost_drive_dp_pa` (fuel, ox): extra head each main pump delivers to drive a
    low-pressure boost pump's hydraulic turbine - charged in the pump POWER and
    efficiency, never in the discharge pressure. (0, 0) = no boost pump.
    Returns a flat dict (see the end of this function).
    """
    th_f, th_o = (tank_head_pa if isinstance(tank_head_pa, (tuple, list))
                  else (tank_head_pa, tank_head_pa))
    bd_f, bd_o = boost_drive_dp_pa
    gas_fr = preburner_gas(cycle, pair, False, tin_fuel_rich_k)
    gas_or = preburner_gas(cycle, pair, True, tin_ox_rich_k)
    sides = _preburner_sides(cycle, mr, gas_fr, gas_or)
    f_fuel = 1.0 / (1.0 + mr)
    f_ox = 1.0 - f_fuel
    mdot_fuel, mdot_ox = f_fuel * mdot, f_ox * mdot

    def pressures(prs):
        """Per-side preburner pressures and per-propellant main discharge."""
        out = []
        for side, pr in zip(sides, prs):
            dp_inj = dp_injector_fuel if side["drive"] == "fuel" else dp_injector_ox
            p_out = pc_feed + dp_inj
            p_in = p_out * pr
            out.append(dict(p_turb_out=p_out, p_turb_in=p_in,
                            p_pb_inj_in=p_in * (1.0 + preburner_inj_dp_frac)))
        # Main (drive-leg) discharge of each propellant: the preburner it drives,
        # else the plain liquid path to the main injector.
        disch = {"fuel": pc_feed + dp_injector_fuel + jacket_dp_pa + line_loss_fuel_pa,
                 "ox": pc_feed + dp_injector_ox + line_loss_ox_pa}
        for side, p in zip(sides, out):
            leg = side["drive"]
            extra = jacket_dp_pa if leg == "fuel" else 0.0
            line = line_loss_fuel_pa if leg == "fuel" else line_loss_ox_pa
            disch[leg] = p["p_pb_inj_in"] + extra + line
        return out, disch

    def evaluate(prs):
        p_sides, disch = pressures(prs)
        dp_f = disch["fuel"] - th_f
        dp_o = disch["ox"] - th_o
        # pump efficiencies from the main legs; turbine efficiency per side
        etas = [efficiency_fn(dp_f + bd_f, dp_o + bd_o, s["gas"], pr)
                for s, pr in zip(sides, prs)]
        eta_pf, eta_po = etas[0][0], etas[0][1]
        p_fuel = mdot_fuel * (dp_f + bd_f) / (rho_fuel * eta_pf)
        p_ox = mdot_ox * (dp_o + bd_o) / (rho_ox * eta_po)
        # Trickle/slug flow into a preburner that is NOT its propellant's main leg
        # must reach that preburner's injector - charged as a boost-stage head on
        # top of that propellant's main discharge (the SSME HPOTP preburner-boost
        # stage; RD-0124's kerosene pump kick stage).
        boost = {"fuel": 0.0, "ox": 0.0}
        for s, p in zip(sides, p_sides):
            if s["drive"] != "fuel" and s["flow_fuel"] > 0:
                boost["fuel"] = max(boost["fuel"], p["p_pb_inj_in"] + line_loss_fuel_pa)
                p_fuel += (s["flow_fuel"] * mdot * max(0.0, p["p_pb_inj_in"] + line_loss_fuel_pa
                                                       - disch["fuel"]) / (rho_fuel * eta_pf))
            if s["drive"] != "ox" and s["flow_ox"] > 0:
                boost["ox"] = max(boost["ox"], p["p_pb_inj_in"] + line_loss_ox_pa)
                p_ox += (s["flow_ox"] * mdot * max(0.0, p["p_pb_inj_in"] + line_loss_ox_pa
                                                   - disch["ox"]) / (rho_ox * eta_po))
        pump_power = {"fuel": p_fuel, "ox": p_ox}
        side_res = []
        for s, pr, p, eta in zip(sides, prs, p_sides, etas):
            mdot_t = (s["flow_fuel"] + s["flow_ox"]) * mdot
            dh = _available_dh(s["gas"], eta[2], pr)
            req = sum(pump_power[k] for k in s["powers"])
            side_res.append(dict(kind=s["kind"], drive=s["drive"], pr=pr, gas=dict(s["gas"]),
                                 mdot_turbine_kgs=mdot_t, dh_j_kg=dh, eta_turbine=eta[2],
                                 power_required_w=req, power_available_w=mdot_t * dh,
                                 powers=s["powers"], **p))
        return dict(sides=side_res, disch=disch, dp_fuel=dp_f, dp_ox=dp_o,
                    eta_pf=eta_pf, eta_po=eta_po, pump_power=pump_power, boost=boost)

    def solve_side(i, prs):
        """Solve side i's PR with the other sides' PRs held; returns (pr, closed)."""
        def margin(pr):
            trial = list(prs)
            trial[i] = pr
            s = evaluate(trial)["sides"][i]
            return s["power_available_w"] - s["power_required_w"], \
                s["power_available_w"] / max(s["power_required_w"], 1e-9)
        step = (TURBINE_PR_MAX - TURBINE_PR_MIN) / (_PR_SCAN_POINTS - 1)
        prev = None
        best_pr, best_ratio = TURBINE_PR_MIN, -1.0
        for k in range(_PR_SCAN_POINTS):
            pr = TURBINE_PR_MIN + k * step
            g, ratio = margin(pr)
            if ratio > best_ratio:
                best_pr, best_ratio = pr, ratio
            if g >= 0.0:
                if prev is None:
                    return pr, True
                lo, hi = prev, pr
                for _ in range(_PR_BISECT_ITERS):
                    mid = 0.5 * (lo + hi)
                    if margin(mid)[0] >= 0.0:
                        hi = mid
                    else:
                        lo = mid
                return hi, True
            prev = pr
        return best_pr, False

    prs = [1.5] * len(sides)
    closed = [False] * len(sides)
    for _ in range(_FFSC_OUTER_ITERS if len(sides) > 1 else 1):
        for i in range(len(sides)):
            prs[i], closed[i] = solve_side(i, prs)
    ev = evaluate(prs)

    sides_out = ev["sides"]
    margins = [s["power_available_w"] / max(s["power_required_w"], 1e-9) for s in sides_out]
    main = sides_out[0]
    mdot_turb = sum(s["mdot_turbine_kgs"] for s in sides_out)
    eta_turb = (sum(s["eta_turbine"] * s["mdot_turbine_kgs"] for s in sides_out)
                / max(mdot_turb, 1e-9))
    return {
        "feasible": all(closed),
        "power_margin": min(margins),
        "sides": sides_out,
        "turbine_pressure_ratio": main["pr"],
        "preburner_pressure_pa": max(s["p_turb_in"] for s in sides_out),
        "pump_discharge_fuel_pa": ev["disch"]["fuel"],
        "pump_discharge_ox_pa": ev["disch"]["ox"],
        "boost_discharge_fuel_pa": ev["boost"]["fuel"],   # 0 = no trickle boost on this leg
        "boost_discharge_ox_pa": ev["boost"]["ox"],
        "dp_fuel_pa": ev["dp_fuel"],
        "dp_ox_pa": ev["dp_ox"],
        "eta_pump_fuel": ev["eta_pf"],
        "eta_pump_ox": ev["eta_po"],
        "eta_turbine": eta_turb,
        "power_fuel_w": ev["pump_power"]["fuel"],
        "power_ox_w": ev["pump_power"]["ox"],
        "mdot_turbine_kgs": mdot_turb,
        "drive_discharge_over_pc": max(ev["disch"][s["drive"]] for s in sides_out) / pc_feed,
    }


def staged_combustion_result(cycle, pair, mdot, mr, balance, specific_power_w_kg):
    """
    Closed staged-combustion cycle result from a solved `balance`
    (solve_staged_power_balance). Returns the 8 keys every cycle builder returns
    (so design.py / the GUI / turbopump_sizing treat it uniformly) plus
    staged-combustion-specific diagnostics.
    """
    oxidizer_rich = cycle == "orsc"
    mdot_fuel = mdot / (1.0 + mr)
    power_total = balance["power_fuel_w"] + balance["power_ox_w"]
    tpump = {
        "mdot_fuel_kgs": mdot_fuel, "mdot_ox_kgs": mdot - mdot_fuel,
        "power_fuel_w": balance["power_fuel_w"], "power_ox_w": balance["power_ox_w"],
        "power_total_w": power_total,
        "turbopump_mass_kg": power_total / specific_power_w_kg,
    }
    main = balance["sides"][0]
    pbf = preburner_flow_fraction(cycle, mr)
    kind = "full_flow" if cycle == "ffsc" else ("oxidizer_rich" if oxidizer_rich else "fuel_rich")
    return {
        "cycle": cycle,
        "has_turbopump": True,
        "turbopump": tpump,
        "gg_mdot_kgs": balance["mdot_turbine_kgs"],
        "gg_flow_fraction": pbf,
        "gg_dump_isp_fraction": 1.0,        # closed cycle - no dump loss
        "turbine_specific_work_j_kg": main["dh_j_kg"],
        "required_tank_pressure_pa": None,
        # staged-combustion diagnostics:
        "preburner_flow_fraction": pbf,
        "preburner_gas_kind": kind,
        "oxidizer_rich": oxidizer_rich,
        "drive_gas": dict(main["gas"]),
        "turbine_pressure_ratio": balance["turbine_pressure_ratio"],
        "preburner_pressure_pa": balance["preburner_pressure_pa"],
        "pump_discharge_fuel_pa": balance["pump_discharge_fuel_pa"],
        "pump_discharge_ox_pa": balance["pump_discharge_ox_pa"],
        "boost_discharge_fuel_pa": balance["boost_discharge_fuel_pa"],
        "boost_discharge_ox_pa": balance["boost_discharge_ox_pa"],
        "drive_discharge_over_pc": balance["drive_discharge_over_pc"],
        "power_margin": balance["power_margin"],
        "feasible": balance["feasible"],
        "preburner_sides": balance["sides"],
    }


if __name__ == "__main__":
    # Headless self-test. A fixed-efficiency stub stands in for design.py's
    # derive_efficiencies wrapper, so this module stays import-light.
    def _eff(dp_f, dp_o, gas, pr):
        return 0.72, 0.76, 0.78

    def _solve(cycle, pair, mdot, mr, pc, tin=0.0, rf=71.0, ro=1141.0, tin_fr=0.0):
        dp_inj = 0.175 * pc
        return solve_staged_power_balance(cycle, pair, mdot, mr, pc, dp_inj, dp_inj, 1.6e6,
                                          0.5e6, 0.5e6, 0.3e6, rf, ro, 0.175, _eff,
                                          tin_fuel_rich_k=tin_fr, tin_ox_rich_k=tin)

    ssme = _solve("frsc", "LOX/LH2", 514.0, 6.0, 20.6e6)
    # the ox-rich override must not touch an FRSC's fuel-rich preburner
    assert _solve("frsc", "LOX/LH2", 514.0, 6.0, 20.6e6, tin=400.0)["sides"][0]["gas"]["tin_k"] == 1113.0
    assert ssme["feasible"] and 1.2 <= ssme["turbine_pressure_ratio"] <= 2.0, ssme["turbine_pressure_ratio"]
    assert 1.8 <= ssme["drive_discharge_over_pc"] <= 2.8, ssme["drive_discharge_over_pc"]
    # closure: available == required at the solved PR (bisection tolerance)
    s0 = ssme["sides"][0]
    assert abs(s0["power_available_w"] / s0["power_required_w"] - 1.0) < 1e-3

    rd0124 = _solve("orsc", "LOX/RP-1", 83.0, 2.6, 15.7e6, rf=810.0)
    assert rd0124["feasible"] and rd0124["sides"][0]["kind"] == "oxidizer_rich"

    # Pc sweep: drive discharge / Pc rises monotonically with Pc (the SP-8107
    # "nonlinear" discharge) until the balance stops closing.
    last = 0.0
    for pc in (8e6, 12e6, 16e6, 20e6):
        r = _solve("orsc", "LOX/RP-1", 500.0, 2.6, pc, rf=810.0)
        assert r["drive_discharge_over_pc"] > last, (pc, r["drive_discharge_over_pc"])
        last = r["drive_discharge_over_pc"]

    # A very high-Pc ox-rich kerolox design at the sourced 628 K does NOT close
    # (the RD-180-class case - it needs a hotter preburner).
    hot = _solve("orsc", "LOX/RP-1", 1350.0, 2.72, 26.66e6, rf=810.0)
    assert not hot["feasible"] and hot["power_margin"] < 1.0, hot["power_margin"]
    assert _solve("orsc", "LOX/RP-1", 1350.0, 2.72, 26.66e6, tin=850.0, rf=810.0)["feasible"]

    ffsc = _solve("ffsc", "LOX/CH4", 650.0, 3.55, 30.0e6, rf=422.0)
    assert len(ffsc["sides"]) == 2
    assert abs(sum(s["mdot_turbine_kgs"] for s in ffsc["sides"]) - 650.0) < 1e-6

    assert ORSC_GAS_PROPERTIES["LOX/RP-1"]["tin_k"] < PREBURNER_GAS_PROPERTIES["LOX/LH2"]["tin_k"]
    assert preburner_flow_fraction("ffsc", 3.6) == 1.0
    print(f"staged_combustion.py self-test OK - SSME-like FRSC PR "
          f"{ssme['turbine_pressure_ratio']:.2f}, fuel discharge/Pc {ssme['drive_discharge_over_pc']:.2f}; "
          f"RD-0124-like ORSC PR {rd0124['turbine_pressure_ratio']:.2f}; RD-180-class at 628 K "
          f"margin {hot['power_margin']:.2f} (infeasible, as expected); FFSC PRs "
          f"{ffsc['sides'][0]['pr']:.2f}/{ffsc['sides'][1]['pr']:.2f} "
          f"(feasible={ffsc['feasible']})")
