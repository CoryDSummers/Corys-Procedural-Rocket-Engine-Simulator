"""Pump-suction stage of _compute_pass (turbopump Round 1).

Builds each pump leg's inlet conditions from the vehicle side - tank ullage
pressure + liquid head - suction-line loss (+ an optional SSME-style boost
pump) - and the propellant's vapor pressure at its inlet temperature
(thermo_tables.saturation, the Round 0 table), then hands size_pump an
inducer.SuctionSpec per leg (the NPSH available + the Brumfield/TSH model of
the NPSH required). Runs before feed_stage.turbomachinery_cycle, which
subtracts the per-leg main-pump inlet pressure (s.pump_inlet_pa) from each pump
dP and adds the boost-drive head (s.boost_drive_dp) to each pump's power.

suction_model "legacy" leaves everything as it was before Round 1: inlet =
TANK_HEAD_PA on both legs, no specs (size_pump's legacy npsh_available /
enforce_suction_limit path), no boost pump - bit-identical."""
from .. import (cycles, inducer, plumbing, pump_meanline, thermo_tables, turbopump_intent,
                turbopump_materials, turbopump_sizing, turbopump_tech)
from .constants import G0, TANK_HEAD_PA
from .checklist import _check

_FT = 3.2808399
_M3S_TO_GPM = 15850.323
SUCTION_MODELS = ("computed", "legacy")
# The pumped (fuel, oxidizer) of each propellant pair, by the saturation table's
# names (thermo_tables.SATURATION keys: LOX / LH2 / CH4 / RP-1). Pair strings are
# not uniformly oxidizer-first ("Aerozine-50/NTO"), hence the explicit map. A
# propellant with no saturation data (the storables) gets zero vapor pressure.
PUMPED_PROPELLANTS = {
    "LOX/RP-1": ("RP-1", "LOX"),
    "LOX/LH2": ("LH2", "LOX"),
    "LOX/CH4": ("CH4", "LOX"),
    "N2O4/MMH": ("MMH", "N2O4"),
    "Aerozine-50/NTO": ("A-50", "N2O4"),
    "Hydrazine": ("N2H4", ""),
    "H2O2": ("", "H2O2"),
}
# Auto inlet temperature: a propellant boiling below this is a cryogen, stored
# saturated at 1 atm (its normal boiling point); anything else sits at ambient.
CRYOGEN_NBP_MAX_K = 250.0
AMBIENT_STORAGE_K = 293.15
# Boost-pump drive efficiency (drive-turbine shaft power / the hydraulic power it
# takes from the main pump), [SSME-Orientation p.52-71] Key Performance
# Parameters at NPL: LPOTP hydraulic turbine 67.7 %, LPFTP gas turbine 58.0 %.
BOOST_DRIVE_EFFICIENCY = {"ox": 0.677, "fuel": 0.58}


def _legacy(self, s):
    s.pump_inlet_pa = {"fuel": TANK_HEAD_PA, "ox": TANK_HEAD_PA}
    s.boost_drive_dp = {"fuel": 0.0, "ox": 0.0}
    s.suction = {}


def pump_suction(self, s):
    """Per-leg NPSH available and the SuctionSpecs size_pump caps rpm with."""
    s._suction_kw = dict(npsh_available_fuel_ft=max(0.0, float(self.npsh_available_fuel_ft or 0.0)),
                         npsh_available_ox_ft=max(0.0, float(self.npsh_available_ox_ft or 0.0)))
    _legacy(self, s)
    s.pump_intent = turbopump_intent.from_design(self)
    if self.suction_model == "legacy" or self.cycle == cycles.PRESSURE_FED:
        return
    ind_kw = dict(has_inducer=s.pump_intent.inducer, k=s.pump_intent.cavitation_number)
    names = PUMPED_PROPELLANTS.get(self.propellant_pair, ("", ""))
    mdot_fuel = s.mdot / (1.0 + self.mixture_ratio)
    material = turbopump_materials.MATERIALS[self.turbopump_material_key]
    build_quality = turbopump_tech.TURBOPUMP_TECHS[self.turbopump_tech_key].build_quality_factor
    specs = {}
    for leg, prop, rho, mdot in (("fuel", names[0], s.rho_fuel, mdot_fuel),
                                 ("ox", names[1], s.rho_ox, s.mdot - mdot_fuel)):
        has_vp = bool(prop) and thermo_tables.has_saturation(prop)
        t_user = float(getattr(self, f"propellant_temp_{leg}_k") or 0.0)
        if t_user > 0:
            t_k = t_user
        elif has_vp:
            nbp = thermo_tables.saturation_temperature(prop, 101_325.0)
            t_k = nbp if nbp < CRYOGEN_NBP_MAX_K else AMBIENT_STORAGE_K
        else:
            t_k = AMBIENT_STORAGE_K
        sat = thermo_tables.saturation(prop, t_k) if has_vp else None
        p_v = sat["p_sat_pa"] if sat else 0.0
        p_tank = float(getattr(self, f"tank_pressure_{leg}_pa") or 0.0) or TANK_HEAD_PA
        head_pa = rho * G0 * float(self.suction_accel_g) * float(getattr(self, f"suction_head_{leg}_m"))
        npsh_tank_m = (p_tank + head_pa - p_v) / (rho * G0) if rho > 0 else 0.0
        line_pa, line = plumbing.suction_line_loss_pa(
            mdot, rho, npsh_tank_m, float(self.suction_line_length_m or 0.0),
            plumbing.liquid_viscosity_pa_s(self.propellant_pair, leg), lh2=prop == "LH2")
        p_inlet = p_tank + head_pa - line_pa
        npsh_inlet_ft = (p_inlet - p_v) / (rho * G0) * _FT if rho > 0 else 0.0
        rise = max(0.0, float(getattr(self, f"boost_pump_rise_{leg}_pa") or 0.0))
        boost = None
        if rise > 0 and rho > 0 and mdot > 0:
            bspec = inducer.make_spec(prop, leg, t_k, npsh_inlet_ft, **ind_kw)
            bp = turbopump_sizing.size_pump(mdot, rise, rho, material, build_quality=build_quality,
                                            suction=bspec)
            eta_d = BOOST_DRIVE_EFFICIENCY[leg]
            drive = rise / (max(bp["eta"], 1e-3) * eta_d)
            s.boost_drive_dp[leg] = drive
            boost = dict(rise_pa=rise, n_rpm=bp["n_rpm"], rpm_ns_optimum=bp["rpm_ns_optimum"],
                         d_impeller_m=bp["d_impeller_m"], n_stages=bp["n_stages"],
                         eta=bp["eta"], drive_efficiency=eta_d, drive_head_pa=drive,
                         shaft_power_w=mdot * rise / (rho * max(bp["eta"], 1e-3)),
                         npsh_required_ft=bp["npsh_required_ft"],
                         suction_limited=bp["suction_limited"],
                         inlet_eye_dia_m=bp["inlet_eye_dia_m"])
        main_inlet = p_inlet + rise
        npsh_main_ft = (main_inlet - p_v) / (rho * G0) * _FT if rho > 0 else 0.0
        override = s._suction_kw[f"npsh_available_{leg}_ft"]
        if override > 0:
            npsh_main_ft = override
        spec = inducer.make_spec(prop, leg, t_k, npsh_main_ft, **ind_kw)
        specs[leg] = spec
        s.pump_inlet_pa[leg] = main_inlet
        s.suction[leg] = dict(
            propellant=prop, t_k=t_k, t_clamped=bool(sat and sat["t_clamped"]),
            has_vapor_pressure=has_vp, p_vapor_pa=p_v, p_tank_pa=p_tank, head_pa=head_pa,
            line_loss_pa=line_pa, line_bore_m=line["bore_m"], line_velocity_ms=line["velocity_ms"],
            p_inlet_pa=p_inlet, npsh_tank_ft=npsh_tank_m * _FT, npsh_inlet_ft=npsh_inlet_ft,
            npsh_available_ft=npsh_main_ft, npsh_override=override > 0,
            main_pump_inlet_pa=main_inlet, tsh_ft=spec.tsh_ft, ss_water=spec.ss_water,
            z_min=spec.z_min, boost=boost)
    s._suction_kw.update(suction_fuel=specs["fuel"], suction_ox=specs["ox"])


def pump_hydraulics(self, s):
    """turbopump Round 2: one pump_meanline.HydraulicsSpec per leg from the
    directional design intent (turbopump_intent), handed to size_pump with the
    suction specs. pump_model "correlation" (or a pressure-fed engine) adds
    nothing - the Round 1 Ns-bell path, bit-identical."""
    if getattr(self, "pump_model", "meanline") != "meanline" or self.cycle == cycles.PRESSURE_FED:
        return
    it = s.pump_intent
    for leg, rho in (("fuel", s.rho_fuel), ("ox", s.rho_ox)):
        mu = plumbing.liquid_viscosity_pa_s(self.propellant_pair, leg)
        s._suction_kw[f"hydraulics_{leg}"] = pump_meanline.HydraulicsSpec(
            ns_target_us=it.ns_target_us, psi=it.psi, beta2_deg=it.beta2_deg,
            tip_speed_fraction=it.tip_speed_fraction, diffuser=it.diffuser,
            pump_type=it.pump_type(leg), nu_kin=mu / rho if rho > 0 else 2.0e-7, leg=leg,
            neutral=it.neutral)


def suction_checks(self, s):
    """Warn-only checklist rows, once the pumps are sized (s.tp_sizing)."""
    if not s.suction or not s.tp_sizing:
        return
    for leg in ("fuel", "ox"):
        su = s.suction[leg]
        pump = s.tp_sizing.get(f"{leg}_pump") or {}
        name = f"{leg.capitalize()} pump"
        prop = su["propellant"] or leg
        if su["t_clamped"]:
            _check(s.checklist, s.warnings, "turbopump", f"{name} propellant temperature",
                   False,
                   f"{name}: {prop} inlet temperature {su['t_k']:.1f} K is outside the saturation "
                   f"table (triple point .. 0.98 Tc) - vapor pressure evaluated at the nearest edge.")
        if su["npsh_available_ft"] <= 0:
            _check(s.checklist, s.warnings, "turbopump", f"{name} suction (NPSH)", False,
                   f"{name}: the inlet is AT OR BELOW the {prop} vapor pressure "
                   f"({su['p_vapor_pa'] / 1e3:.0f} kPa at {su['t_k']:.1f} K vs "
                   f"{su['main_pump_inlet_pa'] / 1e3:.0f} kPa) - the pump would vapor-lock. Raise "
                   f"tank pressure, subcool the propellant or add a boost pump [SP-8107 2.1.1.2]. "
                   f"Rotor speed left at its specific-speed optimum.")
            continue
        vp_note = ("" if su["has_vapor_pressure"] else
                   f" ({prop}: no vapor-pressure data - taken as zero, so NPSH available is "
                   f"optimistic)")
        q_gpm = pump.get("q_m3s", 0.0) * _M3S_TO_GPM
        spec = s._suction_kw[f"suction_{leg}"]
        if pump.get("suction_limited"):
            npsh_opt = inducer.npsh_required_ft(pump["rpm_ns_optimum"], q_gpm, spec)
            dp_fix = (max(0.0, npsh_opt - su["npsh_available_ft"]) / _FT
                      * getattr(s, f"rho_{leg}") * G0)
            _check(s.checklist, s.warnings, "turbopump", f"{name} suction (NPSH)", False,
                   f"{name} SUCTION-LIMITED: {su['npsh_available_ft']:.0f} ft NPSH available "
                   f"(TSH credit {su['tsh_ft']:.0f} ft) holds it to {pump['n_rpm']:,.0f} rpm "
                   f"instead of its specific-speed optimum {pump['rpm_ns_optimum']:,.0f} rpm - a "
                   f"larger, heavier, less efficient pump. About {dp_fix / 1e5:.1f} bar more at "
                   f"the pump inlet (tank pressure, liquid head or a boost pump) restores the "
                   f"optimum [SP-8052 / SP-8107 2.1.1.2].{vp_note}")
        else:
            _check(s.checklist, s.warnings, "turbopump", f"{name} suction (NPSH)", True, "",
                   f"OK - {su['npsh_available_ft']:.0f} ft available vs "
                   f"{pump.get('npsh_required_ft', 0.0):.0f} ft required at "
                   f"{pump.get('n_rpm', 0.0):,.0f} rpm (TSH credit {su['tsh_ft']:.0f} ft){vp_note}")
        b = su["boost"]
        if b:
            _check(s.checklist, s.warnings, "turbopump", f"{name} boost pump",
                   su["npsh_inlet_ft"] > 0,
                   f"{name} boost pump: its own inlet is at or below the {prop} vapor pressure - "
                   f"it cannot run on this tank NPSH either.",
                   f"OK - boost pump +{b['rise_pa'] / 1e5:.1f} bar at {b['n_rpm']:,.0f} rpm, eta "
                   f"{b['eta']:.2f}; its hydraulic drive costs the main pump "
                   f"{b['drive_head_pa'] / 1e5:.1f} bar of head (drive eta "
                   f"{b['drive_efficiency']:.2f}, SSME-anchored)")


WIDE_OUTLET_B2_OVER_D2 = 0.15   # above every SP-8109 Table I impeller (0.039-0.138)


def hydraulics_checks(self, s):
    """Warn-only rows for the meanline (turbopump Round 2), once the pumps are
    sized: H-Q stability against the throttle floor, an unusually wide impeller
    outlet, and a summary row per leg."""
    if not s.tp_sizing:
        return
    floor = max(0.05, min(1.0, float(getattr(self, "throttle_floor", 1.0) or 1.0)))
    for leg in ("fuel", "ox"):
        pump = s.tp_sizing.get(f"{leg}_pump") or {}
        ml = pump.get("meanline")
        if not ml:
            continue
        name = f"{leg.capitalize()} pump"
        hq = ml["hq"]
        if ml["type"] == "axial":
            ok = hq["x_stall"] <= 0.85 * floor
            _check(s.checklist, s.warnings, "turbopump", f"{name} head curve", ok,
                   f"{name} (axial): the blading stalls (diffusion factor 0.75) near "
                   f"{hq['x_stall']:.0%} of design flow - within 15 % of the {floor:.0%} throttle "
                   f"floor. Axial LH2 pumps suit non-throttled engines [SP-8125 §3.2.1, §3.2.2.6]; "
                   f"pick a centrifugal pump or raise the throttle floor.",
                   f"OK - axial stall near {hq['x_stall']:.0%} of design flow, below the "
                   f"{floor:.0%} throttle floor with margin")
            summary = (f"axial, {ml['n_stages']} stages + inducer, tip {ml['d_tip_m'] * 1000:.0f} mm, "
                       f"hub/tip {ml['hub_tip']:.2f}, {ml['z_rotor']}/{ml['z_stator']} blades/vanes, "
                       f"DF {max(ml['df_rotor'], ml['df_stator']):.2f}")
        else:
            st = ml["stage"]
            x0 = hq["x_zero_slope"]
            ok = hq["rising_to_shutoff"] or x0 <= 0.9 * floor
            _check(s.checklist, s.warnings, "turbopump", f"{name} head curve", ok,
                   f"{name}: the head/flow curve flattens (zero slope) near {x0:.0%} of design flow "
                   f"- SP-8109 wants that point >= 10 % below the lowest operating flow "
                   f"({floor:.0%} throttle floor): risk of surge at deep throttle. Move 'Stable <-> "
                   f"Max head' toward stable (lower beta2 / psi) [SP-8109 §3.3.1.3, Fig. 13].",
                   ("OK - rising to shutoff (falling H-Q curve everywhere)" if hq["rising_to_shutoff"]
                    else f"OK - zero-slope point {x0:.0%} of design flow, below the {floor:.0%} "
                         f"throttle floor") + f"; shutoff head {hq['shutoff_ratio']:.2f} x design")
            ratio = st["b2_m"] / st["d2_m"] if st["d2_m"] > 0 else 0.0
            if ratio > WIDE_OUTLET_B2_OVER_D2:
                _check(s.checklist, s.warnings, "turbopump", f"{name} impeller outlet", False,
                       f"{name}: impeller outlet {ratio:.2f} x its diameter wide - wider than any "
                       f"real SP-8109 Table I impeller (0.04-0.14): a mixed-flow-like stage at "
                       f"specific speed {st['ns_stage_us']:,.0f}. Real LH2 multistage pumps run "
                       f"slower stages (SSME HPFTP ~1,100); 'Efficient <-> Compact' toward efficient "
                       f"lowers it.")
            summary = (f"centrifugal, {ml['n_stages']} stage(s), {st['z']} blades"
                       f"{' (' + str(st['z_inlet']) + ' full + splitters)' if st['splitters'] else ''}, "
                       f"beta2 {st['beta2_deg']:.0f} deg, D2 {st['d2_m'] * 1000:.0f} mm, "
                       f"b2 {st['b2_m'] * 1000:.1f} mm, {ml['diffuser']} diffuser")
        _check(s.checklist, s.warnings, "turbopump", f"{name} hydraulics", True, "",
               f"OK - {summary}; meanline eta {pump['eta']:.3f} (Ns-bell correlation "
               f"{pump['eta_correlation']:.3f})")


# --- pump heating (turbopump Round 2 C4) -----------------------------------------
PUMP_HEATING_STEPS = 12          # [SP-8107 p.14, §3.1.1.1]: incremental isentropic method
# LOX has no baked coolant table: cp and the volume-expansion coefficient beta for the
# (1/eta - 1 + T beta) liquid heating relation - Tier 3 property values near 90-110 K
# (reproduces the SSME HPOTP main-stage rise, +10.6 K [SSME-Orientation p.19]).
LOX_CP_J_KGK = 1700.0
LOX_BETA_PER_K = 0.0045


def fuel_pump_outlet_k(pair, t_in_k, p_in_pa, p_out_pa, eta, steps=PUMP_HEATING_STEPS):
    """Liquid temperature after a pump raising p_in -> p_out at efficiency eta.
    The isentropic enthalpy rise is marched in increments (dh_s = dp / rho along
    the isentrope - the compressible-liquid method of [SP-8107 §3.1.1.1 eq. 17]),
    and eta is taken on that isentropic head: h_out = h_in + dh_s / eta (the
    (1 - eta) loss heats the fluid). Uses the baked coolant tables
    (thermo_tables) - the three fuels they carry (LH2, CH4, RP-1). Reproduces
    the SSME HPFTP (23.7 -> 51.5 K at 298 -> 5,956 psia, eta 0.75) within ~1.5 K."""
    if eta <= 0 or p_out_pa <= p_in_pa:
        return t_in_k
    t, p = t_in_k, p_in_pa
    h0 = h = thermo_tables.coolant_state(pair, t, p)["h_j_kg"]
    dp = (p_out_pa - p_in_pa) / steps
    for _ in range(steps):
        rho = thermo_tables.coolant_state(pair, t, p)["rho_kg_m3"]
        h += dp / rho
        p += dp
        t = thermo_tables.coolant_temperature_from_enthalpy(pair, h, p)
    return thermo_tables.coolant_temperature_from_enthalpy(pair, h0 + (h - h0) / eta, p_out_pa)


def lox_pump_rise_k(dp_pa, rho, eta, t_k):
    """LOX temperature rise across a pump (no LOX table): dT = dp/(rho cp) *
    (1/eta - 1 + T beta) - the loss heating plus the liquid's compression heating."""
    if eta <= 0 or dp_pa <= 0 or rho <= 0:
        return 0.0
    return dp_pa / (rho * LOX_CP_J_KGK) * (1.0 / eta - 1.0 + t_k * LOX_BETA_PER_K)


def pump_heating(self, s):
    """Each pump's outlet temperature (tank T -> boost pump -> main pump), once the
    pump rises and efficiencies are known. The fuel pump's outlet is the regen
    jacket's coolant inlet (coolant_inlet_model "computed", applied on a second
    compute pass - see EngineDesign.compute)."""
    s.pump_heating = {}
    if not s.suction or self.cycle == cycles.PRESSURE_FED:
        return
    pair = self.propellant_pair
    for leg, dp, eta, rho in (("fuel", getattr(s, "dp_fuel", 0.0), s.eta_pf, s.rho_fuel),
                              ("ox", getattr(s, "dp_ox", 0.0), s.eta_po, s.rho_ox)):
        su = s.suction.get(leg) or {}
        if not su or not dp or eta <= 0:
            continue
        t_in = su["t_k"]
        b = su.get("boost")
        p0 = su["p_inlet_pa"]
        main_in = s.pump_inlet_pa[leg]
        p_out = main_in + dp
        if leg == "fuel" and thermo_tables.has_coolant_table(pair):
            t_b = fuel_pump_outlet_k(pair, t_in, p0, main_in, b["eta"]) if b else t_in
            t_out = fuel_pump_outlet_k(pair, t_b, main_in, p_out, eta)
            method = "incremental isentropic (coolant table)"
        elif leg == "ox" and su.get("propellant") == "LOX":
            t_b = t_in + (lox_pump_rise_k(b["rise_pa"], rho, b["eta"], t_in) if b else 0.0)
            t_out = t_b + lox_pump_rise_k(dp, rho, eta, t_b)
            method = "liquid (1/eta - 1 + T beta) relation"
        else:
            continue
        s.pump_heating[leg] = dict(t_tank_k=t_in, t_after_boost_k=t_b, t_out_k=t_out,
                                   dt_k=t_out - t_in, p_out_pa=p_out, method=method)
