"""Injector / cooling routing and turbomachinery-cycle stages of _compute_pass.

Split verbatim out of the former single-file design.py; a value shared
between stages lives on the PassState `s` (see design/state.py)."""
from .. import (combustion, combustion_stability, cooling, cycles, electric_pump,
                turbine_exhaust,
                geometry, injectors, materials, staged_combustion, turbopump_materials,
                turbopump_sizing, turbopump_tech, isentropic as iso, turbopump as tp)
from .constants import (
    G0,
    PA_SEA_LEVEL,
    LINE_LOSS_PA,
    TANK_HEAD_PA,
    GG_PRESSURE_RATIO,
    EXPANDER_TURBINE_PR,
    GG_GAS_PROPERTIES,
    GG_MIXTURE_RATIO,
    GG_DUMP_ISP_FRACTION,
    TAP_OFF_DUMP_ISP_FRACTION,
    TAP_OFF_TEMP_FRACTION,
    TAP_OFF_TURBINE_LIMIT_K,
    TAP_OFF_PRESSURE_RATIO,
    SEPARATION_K,
    GG_FLOW_FRACTION_TYPICAL_MAX,
    PRESSURE_FED_PC_TYPICAL_MAX_PA,
    BASE_RATED_BURN_TIME_S,
)
from .checklist import _check


def injector_and_cooling_routing(self, s):
    """Injector pressure drop, chamber flow, feed pressure, and per-section cooling-method resolution / cooled length / two-pass flags."""
    # Injector pressure drop. The catalog's dp_over_pc_nominal is the
    # calibrated NOMINAL fraction of Pc; injectors.derived_dp_pa() is what
    # it actually takes to push each stream through an orifice at a sane
    # injection velocity (rho*V^2/(2*Cd^2), Pc-independent). The larger of
    # the two wins - so a high-Pc engine keeps its nominal fraction, but a
    # low-Pc one is charged the real (higher) dP/Pc it needs, which then
    # propagates into the required pump discharge pressure below exactly
    # like the nominal value always has. Pressure-fed integration spot
    # checks are unaffected (their dp_injector feeds only the required tank
    # pressure, never Isp/thrust).
    s.orifice_cd = injectors.cd_for_orifice(self.orifice_type)
    s.dp_injector_nominal = s.injector.dp_over_pc_nominal * self.chamber_pressure_pa
    s.dp_injector_derived = max(
        injectors.derived_dp_pa(s.rho_fuel, injectors.INJECTION_VELOCITY_TARGET_MS["fuel"], s.orifice_cd),
        injectors.derived_dp_pa(s.rho_ox, injectors.INJECTION_VELOCITY_TARGET_MS["ox"], s.orifice_cd))
    # A 'stiff' / 'very_stiff' injector build raises the effective dP/Pc
    # (the primary injector-side stability cure - claude_lit/topics/05/14),
    # which then propagates into the required pump discharge pressure and
    # the element geometry exactly like the nominal value does. 'nominal'
    # leaves everything untouched.
    s.effective_dp_over_pc = combustion_stability.stiff_injector_dp_over_pc(
        self.injector_stiffness, s.injector.dp_over_pc_nominal)
    dp_injector_stiff = s.effective_dp_over_pc * self.chamber_pressure_pa
    s.dp_injector = max(s.dp_injector_nominal, s.dp_injector_derived, dp_injector_stiff)
    # Per-leg injector dP (fuel, ox) - the type's dp_ox_over_fuel ratio; 1.0
    # (every original catalog entry) leaves both equal to dp_injector.
    s.dp_injector_fuel, s.dp_injector_ox = injectors.dp_split(s.dp_injector, self.injector_type)
    # Finite-contraction-ratio chamber flow: the pump must supply the
    # injector-END pressure, which exceeds the nozzle-stagnation Pc that
    # sets thrust/Isp. Always computed & reported; only routed into the feed
    # chain when apply_chamber_pressure_loss is on.
    s.chamber_flow = combustion.chamber_flow(self.contraction_ratio, s.gamma)
    s.pc_feed = (self.chamber_pressure_pa * s.chamber_flow["injector_end_pressure_ratio"]
               if self.apply_chamber_pressure_loss else self.chamber_pressure_pa)
    # Looked up here (not just at the thermal-margin check further down) because the
    # chamber material's cooling_method now determines how much (if any) regen-jacket
    # pressure drop applies - a design with an ablative/radiative chamber has no active
    # cooling loop at all, so charging it JACKET_DP_PA (as every cycle used to,
    # unconditionally) was a real, previously undocumented inconsistency.
    s.chamber_material = materials.MATERIALS[self.material_key]
    s.bell_material = materials.MATERIALS[self.bell_material_key]
    # Cooling method per section: "auto" -> the material's own cooling_method
    # (historical, bit-identical); an explicit EngineDesign value overrides it.
    # HARD block (a deliberate exception to "warn, don't block"): an explicit
    # method the section's material can't physically be built for (regen on an
    # ablative, ablative on a metal, a regen C-C wall, ...) falls back to the
    # material's own method, and a FAILING checklist row says so. Old project
    # files are never rewritten - they coerce here, every compute.
    s.chamber_cooling, s.chamber_cooling_rejected = cooling.resolve_cooling_method_checked(
        self.chamber_cooling_method, s.chamber_material)
    s.nozzle_cooling, s.nozzle_cooling_rejected = cooling.resolve_cooling_method_checked(
        self.nozzle_cooling_method, s.bell_material)
    for _sec, _mat, _rej, _eff in (("Chamber", s.chamber_material, s.chamber_cooling_rejected,
                                    s.chamber_cooling),
                                   ("Nozzle/bell", s.bell_material, s.nozzle_cooling_rejected,
                                    s.nozzle_cooling)):
        _why = ("film is no longer a section method - use the film-cooling overlay "
                "(chamber film % / nozzle slot film %) on top of a base method"
                if _rej == "film" else
                f"it can only be built for: {', '.join(_mat.allowed_cooling_methods)}")
        _check(s.checklist, s.warnings, "materials",
               f"{_sec} cooling method compatible with material",
               _rej is None,
               f"{_sec} cooling method '{_rej}' is not physically possible on "
               f"{_mat.display_name} ({_why}). BLOCKED - using its own "
               f"'{_eff}' cooling instead.",
               f"OK - {_eff} on {_mat.display_name}")
    # The ONE "where does active cooling stop" number, shared by the flux
    # integration, the coolant march and the expander cycle's cooled-area
    # cutoff. Normally == the material-transition point (cooling_transition_eps,
    # clamped to the expansion ratio); a regeneratively- or dump-cooled nozzle
    # can push it further downstream with regen_nozzle_end_eps (SSME/RL10-style
    # full-length regen, or the slice a dump-cooled nozzle extension actually
    # cools). The bell-MATERIAL transition (eps_for_transition, further down)
    # is a separate concept and untouched by this.
    _cool_base_eps = min(self.cooling_transition_eps, self.expansion_ratio)
    if s.nozzle_cooling in ("regenerative", "dump") and self.regen_nozzle_end_eps > 0.0:
        s.cooled_length_eps = max(_cool_base_eps,
                                min(self.regen_nozzle_end_eps, self.expansion_ratio))
    else:
        s.cooled_length_eps = _cool_base_eps
    # J-2-style mid-nozzle inlet (cooling.march_coolant_two_pass): the
    # inlet must sit between the throat and the cooled end.
    s.two_pass = self.cooling_flow_topology == "j2_mid_nozzle_inlet"
    s.jacket_inlet_eps_eff = (min(max(self.jacket_inlet_eps, 1.0), s.cooled_length_eps)
                            if s.two_pass else None)
    # The J-2 layout's tube split IS its inlet ring (down tubes join the
    # up tubes there), so the user's tube_split_eps is ignored under it -
    # everywhere, physics and the 3D preview alike.
    s.split_eps_eff = 0.0 if s.two_pass else self.tube_split_eps


def turbomachinery_cycle(self, s):
    """Turbomachinery cycle branches (pump dP / efficiencies / GG) and thrust. The
    jacket dP they use is the real-contour thermal solve's (cooling_stage.thermal
    runs first); the expander cycle is completed in geometry_stage.chamber_detail."""
    # Per-propellant-pair turbine drive-gas properties (fuel-rich GG / preburner
    # gas), shared by every turbopump cycle branch below. See GG_GAS_PROPERTIES.
    s.gg_gas = GG_GAS_PROPERTIES[self.propellant_pair]

    # Build-quality multiplier on the DERIVED pump/turbine efficiency, and the
    # effective turbine staging (physics/turbopump_efficiency.py / _sizing.py).
    s.build_quality = turbopump_tech.TURBOPUMP_TECHS[self.turbopump_tech_key].build_quality_factor
    eff_staging = (turbopump_sizing.derive_turbine_staging(self.cycle, self.propellant_pair)
                   if self.turbine_staging in ("", "auto") else self.turbine_staging)
    s.eta_pf = s.eta_po = s.eta_turb = 0.0   # derived per turbopump cycle branch below
    s._suction_kw = dict(npsh_available_fuel_ft=max(0.0, float(self.npsh_available_fuel_ft or 0.0)),
                       npsh_available_ox_ft=max(0.0, float(self.npsh_available_ox_ft or 0.0)))

    if self.cycle == cycles.GAS_GENERATOR:
        s.dp_fuel = s.pc_feed + s.dp_injector_fuel + s.jacket_dp_pa + s.line_loss_fuel_pa - TANK_HEAD_PA
        s.dp_ox = s.pc_feed + s.dp_injector_ox + s.line_loss_ox_pa - TANK_HEAD_PA
        # Turbine PR: the flat cap, unless the exhaust's back pressure leaves
        # less (physics/turbine_exhaust.py).
        _pr = _exhaust_back_pressure(self, s, s.gg_gas["gamma"],
                                     turbine_exhaust.GG_TURBINE_INLET_PC_FRACTION,
                                     GG_PRESSURE_RATIO)
        s.eta_pf, s.eta_po, s.eta_turb = turbopump_sizing.derive_efficiencies(
            s.mdot, self.mixture_ratio, s.dp_fuel, s.dp_ox, s.rho_fuel, s.rho_ox,
            self.turbopump_material_key, eff_staging, s.gg_gas["tin_k"], s.gg_gas["cp"],
            s.gg_gas["gamma"], _pr, _pr, s.build_quality,
            pump_stages_fuel=self.pump_stages_fuel, pump_stages_ox=self.pump_stages_ox,
            eta_pump_fuel_override=self.eta_pump_fuel, eta_pump_ox_override=self.eta_pump_ox,
            enforce_suction_limit=self.enforce_suction_limit, **s._suction_kw)
        s.cyc = cycles.gas_generator_result(
            s.mdot, self.mixture_ratio, self.chamber_pressure_pa, s.dp_fuel, s.dp_ox,
            s.rho_fuel, s.rho_ox, s.eta_pf, s.eta_po, self.pump_specific_power_w_kg,
            s.gg_gas["tin_k"], s.gg_gas["cp"], s.eta_turb, _pr, s.gg_gas["gamma"],
            GG_DUMP_ISP_FRACTION, cycle_name=cycles.GAS_GENERATOR,
            gg_mixture_ratio=GG_MIXTURE_RATIO[self.propellant_pair],
        )
        _apply_exhaust(self, s, s.gg_gas, _pr)
        _check(s.checklist, s.warnings, "turbopump", "Gas-generator flow-fraction plausibility",
               s.cyc["gg_flow_fraction"] <= GG_FLOW_FRACTION_TYPICAL_MAX,
               f"GG flow fraction {s.cyc['gg_flow_fraction']*100:.1f}% is unusually high (typical "
               f"real GG-cycle engines bleed a few percent) - this chamber pressure/thrust "
               f"combination is putting an unusually large burden on the turbopump relative to "
               f"the main chamber, wasting a larger-than-normal share of propellant at reduced "
               f"(dumped-exhaust) Isp.",
               f"OK - {s.cyc['gg_flow_fraction']*100:.1f}% flow fraction")

    elif self.cycle == cycles.TAP_OFF:
        s.dp_fuel = s.pc_feed + s.dp_injector_fuel + s.jacket_dp_pa + s.line_loss_fuel_pa - TANK_HEAD_PA
        s.dp_ox = s.pc_feed + s.dp_injector_ox + s.line_loss_ox_pa - TANK_HEAD_PA
        # Tapped gas = main-chamber combustion products, film-cooled to a
        # turbine-tolerable temperature (NOT the fuel-rich GG mix).
        tap_tin_k = min(s.tc * TAP_OFF_TEMP_FRACTION, TAP_OFF_TURBINE_LIMIT_K)
        tap_gas = dict(tin_k=tap_tin_k, cp=combustion.mixture_cp_j_kgk(s.gamma, s.m_molar),
                       gamma=s.gamma)
        _pr = _exhaust_back_pressure(self, s, tap_gas["gamma"],
                                     turbine_exhaust.TAP_OFF_TURBINE_INLET_PC_FRACTION,
                                     TAP_OFF_PRESSURE_RATIO)
        s.eta_pf, s.eta_po, s.eta_turb = turbopump_sizing.derive_efficiencies(
            s.mdot, self.mixture_ratio, s.dp_fuel, s.dp_ox, s.rho_fuel, s.rho_ox,
            self.turbopump_material_key, eff_staging, tap_gas["tin_k"], tap_gas["cp"],
            tap_gas["gamma"], _pr, _pr, s.build_quality,
            pump_stages_fuel=self.pump_stages_fuel, pump_stages_ox=self.pump_stages_ox,
            eta_pump_fuel_override=self.eta_pump_fuel, eta_pump_ox_override=self.eta_pump_ox,
            enforce_suction_limit=self.enforce_suction_limit, **s._suction_kw)
        s.cyc = cycles.gas_generator_result(
            s.mdot, self.mixture_ratio, self.chamber_pressure_pa, s.dp_fuel, s.dp_ox,
            s.rho_fuel, s.rho_ox, s.eta_pf, s.eta_po, self.pump_specific_power_w_kg,
            tap_gas["tin_k"], tap_gas["cp"], s.eta_turb, _pr, tap_gas["gamma"],
            TAP_OFF_DUMP_ISP_FRACTION, cycle_name=cycles.TAP_OFF,
        )
        s.cyc["drive_gas"] = tap_gas
        _apply_exhaust(self, s, tap_gas, _pr)
        _check(s.checklist, s.warnings, "turbopump", "Gas-generator flow-fraction plausibility",
               s.cyc["gg_flow_fraction"] <= GG_FLOW_FRACTION_TYPICAL_MAX,
               f"GG flow fraction {s.cyc['gg_flow_fraction']*100:.1f}% is unusually high (typical "
               f"real GG-cycle engines bleed a few percent) - this chamber pressure/thrust "
               f"combination is putting an unusually large burden on the turbopump relative to "
               f"the main chamber, wasting a larger-than-normal share of propellant at reduced "
               f"(dumped-exhaust) Isp.",
               f"OK - {s.cyc['gg_flow_fraction']*100:.1f}% flow fraction")

    elif self.cycle in cycles.STAGED_CYCLES:
        # Closed staged combustion (FRSC / ORSC / FFSC): the preburner
        # temperature is a design input, the turbine PR is SOLVED so the drive
        # gas delivers the pump power, and each pump's discharge is built up
        # from the real pressure chain (main injector -> turbine -> preburner
        # injector -> jacket -> lines) - see staged_combustion.py's docstring.
        oxidizer_rich = self.cycle == cycles.ORSC

        def _staged_eff(dp_f, dp_o, gas, pr):
            return turbopump_sizing.derive_efficiencies(
                s.mdot, self.mixture_ratio, dp_f, dp_o, s.rho_fuel, s.rho_ox,
                self.turbopump_material_key, eff_staging, gas["tin_k"], gas["cp"],
                gas["gamma"], pr, pr, s.build_quality,
                pump_stages_fuel=self.pump_stages_fuel, pump_stages_ox=self.pump_stages_ox,
                eta_pump_fuel_override=self.eta_pump_fuel,
                eta_pump_ox_override=self.eta_pump_ox,
                enforce_suction_limit=self.enforce_suction_limit, **s._suction_kw)

        staged_balance = staged_combustion.solve_staged_power_balance(
            self.cycle, self.propellant_pair, s.mdot, self.mixture_ratio, s.pc_feed,
            s.dp_injector_fuel, s.dp_injector_ox, s.jacket_dp_pa, s.line_loss_fuel_pa,
            s.line_loss_ox_pa, TANK_HEAD_PA, s.rho_fuel, s.rho_ox,
            s.injector.dp_over_pc_nominal,   # preburner injector: same dP/P rule as the main one
            _staged_eff,
            tin_fuel_rich_k=max(0.0, float(self.preburner_tin_k or 0.0)),
            tin_ox_rich_k=max(0.0, float(self.ox_preburner_tin_k or 0.0)))
        s.dp_fuel = staged_balance["dp_fuel_pa"]
        s.dp_ox = staged_balance["dp_ox_pa"]
        s.eta_pf = staged_balance["eta_pump_fuel"]
        s.eta_po = staged_balance["eta_pump_ox"]
        s.eta_turb = staged_balance["eta_turbine"]
        s.cyc = staged_combustion.staged_combustion_result(
            self.cycle, self.propellant_pair, s.mdot, self.mixture_ratio, staged_balance,
            self.pump_specific_power_w_kg)
        s.drive_gas = s.cyc["drive_gas"]
        _pb_sides = ", ".join(
            f"{s['kind'].replace('_', '-')} PR {s['pr']:.2f} @ {s['gas']['tin_k']:.0f} K "
            f"(margin {s['power_available_w'] / max(s['power_required_w'], 1e-9):.2f})"
            for s in staged_balance["sides"])
        _check(s.checklist, s.warnings, "turbopump", "Staged-combustion power balance",
               staged_balance["feasible"],
               f"The preburner drive gas cannot power the pumps at this chamber pressure: "
               f"best achievable power margin {staged_balance['power_margin']:.2f} "
               f"({_pb_sides}) with the turbine PR searched up to "
               f"{staged_combustion.TURBINE_PR_MAX:.1f}. A hotter preburner (preburner "
               f"temperature inputs), better turbomachinery, or a lower Pc closes it - this "
               f"is the staged-cycle Pc ceiling [SP-8107 Table VI].",
               f"OK - {_pb_sides}; drive-pump discharge "
               f"{staged_balance['drive_discharge_over_pc']:.2f} x Pc")
        _band = staged_combustion.DRIVE_DISCHARGE_OVER_PC_BAND
        _pr_hi = max(s["pr"] for s in staged_balance["sides"])
        _check(s.checklist, s.warnings, "turbopump", "Staged-combustion turbine PR / discharge plausibility",
               (_pr_hi <= staged_combustion.TURBINE_PR_PLAUSIBLE_MAX
                and _band[0] <= staged_balance["drive_discharge_over_pc"] <= _band[1]),
               f"Turbine PR {_pr_hi:.2f} / drive-pump discharge "
               f"{staged_balance['drive_discharge_over_pc']:.2f} x Pc is outside real "
               f"staged-combustion practice (PR < ~{staged_combustion.TURBINE_PR_PLAUSIBLE_MAX:.1f}, "
               f"SSME 1.56-1.59; discharge ~2.1-2.3 x Pc - SSME/RD-0124/NK-33) - the turbine "
               f"is being asked for an unusually large pressure drop.",
               f"OK - PR {_pr_hi:.2f}, discharge {staged_balance['drive_discharge_over_pc']:.2f} x Pc")
        _tp_mat = turbopump_materials.MATERIALS[self.turbopump_material_key]
        _tin_hi = max(s["gas"]["tin_k"] for s in staged_balance["sides"])
        _check(s.checklist, s.warnings, "turbopump", "Preburner temperature vs turbine material",
               _tin_hi <= _tp_mat.max_use_temp_k,
               f"Preburner/turbine-inlet temperature {_tin_hi:.0f} K exceeds "
               f"{_tp_mat.display_name}'s {_tp_mat.max_use_temp_k:.0f} K service limit - "
               f"choose a hotter-capable turbopump material or a cooler preburner.",
               f"OK - {_tin_hi:.0f} K vs {_tp_mat.max_use_temp_k:.0f} K limit")
        # Closed cycle: ALL preburner exhaust rejoins the main flow at the main
        # injector - no dump loss, so engine Isp is the chamber Isp directly. The
        # eta_cstar mixing penalty was already applied above per cycle.
        s.isp_vac_eng = s.isp_vac_chamber
        s.isp_sl_eng = s.isp_sl_chamber
        if self.cycle == cycles.ORSC:
            _check(s.checklist, s.warnings, "propellant/cycle", "ORSC turbine-material caution",
                   False,
                   "Oxidizer-rich staged combustion needs an oxidizer-resistant "
                   "turbine (hot O2-rich gas is highly corrosive/erosive) - "
                   "historically achieved reliably only by late-Soviet/Russian "
                   "engines (RD-170 family). Treat reliability figures as "
                   "optimistic for other eras/manufacturers.")
        elif self.cycle == cycles.FFSC:
            _check(s.checklist, s.warnings, "propellant/cycle", "FFSC development complexity",
                   False,
                   "Full-flow staged combustion uses TWO preburners (one fuel-rich, "
                   "one oxidizer-rich), one per turbopump, with nearly all of both "
                   "propellants gasified before the main injector - the highest "
                   "plumbing/valve count and the hardest cycle to develop. Only "
                   "Raptor / RD-270 / (partly) BE-4 have flown or run it.")

    elif self.cycle == cycles.EXPANDER:
        # The expander turbine sits IN SERIES on the fuel leg (pump -> jacket ->
        # turbine -> main injector), so its pressure drop adds to the fuel-pump
        # discharge: turbine exit = injector inlet, turbine inlet = exit x PR
        # [SP-8107 3.1.1.1; RL10 fuel discharge ~2.5 x Pc, SP-8107 p.25].
        s.dp_fuel = ((s.pc_feed + s.dp_injector_fuel) * EXPANDER_TURBINE_PR + s.jacket_dp_pa
                   + s.line_loss_fuel_pa - TANK_HEAD_PA)
        s.dp_ox = s.pc_feed + s.dp_injector_ox + s.line_loss_ox_pa - TANK_HEAD_PA
        # Needs the nozzle profile for cooled-area, so this is computed further down
        # (after geo/profile) and cyc is filled in there; placeholder for now.
        s.cyc = None
        s.isp_vac_eng = s.isp_vac_chamber
        s.isp_sl_eng = s.isp_sl_chamber

    elif self.cycle == cycles.PRESSURE_FED:
        # The tanks feed the regen jacket too: its dP (0 without a jacket) and
        # the computed feed-line loss (== LINE_LOSS_PA with no plumbing run)
        # belong in the required tank pressure (audit W10).
        s.cyc = cycles.pressure_fed_result(
            s.pc_feed, s.dp_injector + s.jacket_dp_pa,
            max(s.line_loss_fuel_pa, s.line_loss_ox_pa))
        s.isp_vac_eng = s.isp_vac_chamber
        s.isp_sl_eng = s.isp_sl_chamber
        _check(s.checklist, s.warnings, "turbopump", "Pressure-fed chamber pressure plausibility",
               self.chamber_pressure_pa <= PRESSURE_FED_PC_TYPICAL_MAX_PA,
               f"Chamber pressure {self.chamber_pressure_pa/1e6:.2f} MPa is unusually high for "
               f"a pressure-fed design - classic real examples (Apollo SPS, LM descent/ascent "
               f"engine, R-4D) cluster at 0.7-0.8 MPa. Only modern composite-overwrapped tank "
               f"technology (e.g. SpaceX SuperDraco, ~6.9 MPa) reaches this high, implying a "
               f"much heavier/higher-tech tank than this tool models.",
               f"OK - {self.chamber_pressure_pa/1e6:.2f} MPa within the classic pressure-fed range")

    elif self.cycle == cycles.ELECTRIC_PUMP:
        # Battery + motor drive the pumps - no turbine, no bled flow. dp is
        # Pc-based (no preburner boost). cyc is built provisionally here so the
        # turbopump sizing has something to work with; it is rebuilt with the
        # real burn time (for the battery) after rated_burn_time_s is known.
        s.dp_fuel = s.pc_feed + s.dp_injector_fuel + s.jacket_dp_pa + s.line_loss_fuel_pa - TANK_HEAD_PA
        s.dp_ox = s.pc_feed + s.dp_injector_ox + s.line_loss_ox_pa - TANK_HEAD_PA
        s.eta_pf, s.eta_po, s.eta_turb = turbopump_sizing.derive_efficiencies(
            s.mdot, self.mixture_ratio, s.dp_fuel, s.dp_ox, s.rho_fuel, s.rho_ox,
            self.turbopump_material_key, eff_staging, 300.0, 1000.0, 1.3,
            2.0, 2.0, s.build_quality,
            pump_stages_fuel=self.pump_stages_fuel, pump_stages_ox=self.pump_stages_ox,
            eta_pump_fuel_override=self.eta_pump_fuel, eta_pump_ox_override=self.eta_pump_ox,
            enforce_suction_limit=self.enforce_suction_limit, **s._suction_kw)
        s.cyc = electric_pump.electric_pump_result(
            s.mdot, self.mixture_ratio, self.chamber_pressure_pa, s.dp_fuel, s.dp_ox,
            s.rho_fuel, s.rho_ox, s.eta_pf, s.eta_po, self.pump_specific_power_w_kg,
            BASE_RATED_BURN_TIME_S)
        s.isp_vac_eng = s.isp_vac_chamber
        s.isp_sl_eng = s.isp_sl_chamber

    else:
        raise ValueError(f"unknown cycle {self.cycle!r}; choices: {cycles.CYCLES}")

    s.turbine_exhaust = getattr(s, "turbine_exhaust", None)
    if (self.cycle not in (cycles.GAS_GENERATOR, cycles.TAP_OFF)
            and turbine_exhaust.effective_mode(self.turbine_exhaust_mode)
            != turbine_exhaust.DEFAULT_MODE):
        _check(s.checklist, s.warnings, "turbopump", "Turbine exhaust handling",
               False,
               f"turbine_exhaust_mode '{self.turbine_exhaust_mode}' only applies to open cycles "
               f"(gas generator / tap-off); a {self.cycle.replace('_', ' ')} engine sends its "
               f"turbine exhaust into the main chamber - ignored.", "")

    # Total engine flow: an open cycle's GG / tap-off draw is EXTRA propellant on
    # top of the chamber flow s.mdot (dumped overboard, not through the throat);
    # staged/expander/electric/pressure-fed engines put everything through the
    # chamber. Thrust = total flow x the total-flow-averaged engine Isp.
    s.mdot_total = s.mdot + (s.cyc["gg_mdot_kgs"]
                             if self.cycle in (cycles.GAS_GENERATOR, cycles.TAP_OFF) else 0.0)
    s.thrust_vac = s.mdot_total * s.isp_vac_eng * G0
    s.thrust_sl = s.mdot_total * s.isp_sl_eng * G0
    s.thrust_vac_floor = s.thrust_vac * self.throttle_floor

    s.separated_100pct = iso.is_separated(s.pe_pa, PA_SEA_LEVEL, SEPARATION_K)


def _exhaust_back_pressure(self, s, gamma, inlet_pc_fraction, pr_cap):
    """Turbine PR for an open cycle (physics/turbine_exhaust.py): the exhaust
    must leave sonic into its discharge (sea-level or vacuum ambient for an
    overboard duct / aspirator, the local main-nozzle static pressure for
    nozzle injection), which sets the turbine outlet pressure; PR = inlet /
    outlet, capped at the old flat value. Stashes the pieces on s for
    _apply_exhaust."""
    s.te_mode = turbine_exhaust.effective_mode(self.turbine_exhaust_mode)
    s.te_separated_sl = iso.is_separated(s.pe_pa, PA_SEA_LEVEL, SEPARATION_K)
    s.te_ambient_pa = turbine_exhaust.design_ambient_pa(s.te_separated_sl)
    s.te_inject_eps = min(max(float(self.turbine_exhaust_inject_eps), 1.5),
                          float(self.expansion_ratio))
    s.te_local_static_pa = (self.chamber_pressure_pa
                            * iso.pe_over_pc_from_eps(s.te_inject_eps, s.gamma))
    s.te_discharge_pa = turbine_exhaust.discharge_pressure_pa(
        s.te_mode, s.te_ambient_pa, s.te_local_static_pa)
    s.te_p_in_pa = inlet_pc_fraction * self.chamber_pressure_pa
    s.te_p_out_req_pa = turbine_exhaust.required_turbine_outlet_pa(gamma, s.te_discharge_pa,
                                                                 s.te_mode)
    # A baked exhaust-duct run's computed loss (previous pass) replaces the
    # lumped duct allowance when it is the larger of the two.
    s.te_duct_loss_pa = (s.line_loss_override or {}).get("turbine_exhaust")
    if s.te_duct_loss_pa is not None:
        s.te_p_out_req_pa = max(
            s.te_p_out_req_pa,
            s.te_discharge_pa / turbine_exhaust.critical_pressure_ratio(gamma) + s.te_duct_loss_pa)
    pr, s.te_pr_limited = turbine_exhaust.turbine_pressure_ratio(
        s.te_p_in_pa, s.te_p_out_req_pa, pr_cap)
    s.te_pr_cap = pr_cap
    return pr


def _apply_exhaust(self, s, gas, pr):
    """Build the turbine-exhaust stream for the solved GG / tap-off flow and
    fold its thrust into the engine Isp (total-flow average; replaces the
    flat GG/TAP_OFF_DUMP_ISP_FRACTION)."""
    exh = turbine_exhaust.exhaust_stream(
        s.te_mode, mdot_kgs=s.cyc["gg_mdot_kgs"], tin_k=gas["tin_k"], cp=gas["cp"],
        gamma=gas["gamma"], dh_actual_j_kg=s.cyc["turbine_specific_work_j_kg"],
        p_turbine_out_pa=s.te_p_in_pa / pr, discharge_pa=s.te_discharge_pa,
        main_exit_static_pa=s.pe_pa, main_exit_dia_m=s.geo["exit_dia_m"],
        nozzle_eps=self.turbine_exhaust_nozzle_eps, cant_deg=self.turbine_exhaust_cant_deg,
        hx_gox_kgs=max(0.0, float(self.turbine_exhaust_hx_gox_kgs or 0.0)),
        hx_he_kgs=max(0.0, float(self.turbine_exhaust_hx_he_kgs or 0.0)),
        lox_pair=self.propellant_pair.startswith("LOX/"))
    exh.update(turbine_inlet_pa=s.te_p_in_pa, turbine_pressure_ratio=pr,
               pr_cap=s.te_pr_cap, back_pressure_limited=s.te_pr_limited,
               inject_eps=s.te_inject_eps if s.te_mode == "nozzle_injection" else None,
               duct_loss_computed_pa=s.te_duct_loss_pa,
               design_ambient_pa=s.te_ambient_pa)
    k_vac = exh["isp_vac_s"] / s.isp_vac_chamber
    k_sl = exh["isp_sl_s"] / s.isp_sl_chamber if s.isp_sl_chamber > 0 else 0.0
    exh["isp_fraction_vac"], exh["isp_fraction_sl"] = k_vac, k_sl
    if exh["mode"] == "nozzle_injection":
        # the gas film this stream lays on the nozzle wall downstream of the
        # manifold - applied by the NEXT pass's thermal solve (compute())
        exh["film_carry"] = dict(
            film_ratio=turbine_exhaust.film_mdot_ratio_to_fuel(exh["mdot_kgs"], s.mdot_fuel_kgs),
            inject_eps=s.te_inject_eps, t_k=exh["t_exhaust_k"], mdot_kgs=exh["mdot_kgs"],
            cp=exh["cp"], slot_area_m2=exh.get("slot_area_m2", 0.0),
            slot_velocity_ms=exh.get("slot_velocity_ms", 0.0),
            slot_density_kg_m3=exh.get("slot_density_kg_m3", 0.0))
        exh["gas_film_applied"] = getattr(s, "gas_film_phi", None) is not None
        gf = getattr(s, "gas_film_info", None)
        exh["gas_film"] = gf
        if gf is not None:
            lo, hi = turbine_exhaust.GAS_FILM_VELOCITY_RATIO_BAND
            vr = gf["velocity_ratio_c_over_g"]
            # informational: real F-1/J-2 slots run well below SP-8124's
            # flow-minimising band, so this is a note, never a warning
            _gf_note = (f"Exhaust film {gf['slot_h_m']*1e3:.1f} mm slot, effectiveness "
                        f"{gf['eta_exit']:.2f} at the exit; coolant/core velocity ratio "
                        f"{vr:.2f} (SP-8124's flow-minimising band {lo:.2f}-{hi:.2f}"
                        f"{'' if lo <= vr <= hi else ' - outside it, so more film flow is needed per unit effectiveness than an optimised slot'}). "
                        f"Correlation valid to ~{turbine_exhaust.GAS_FILM_VALID_SLOT_HEIGHTS:.0f} "
                        f"slot heights (x/S at exit {gf['x_over_s_exit']:.0f}); beyond that it "
                        f"over-predicts wall temperature (conservative).")
            _check(s.checklist, s.warnings, "turbopump", "Turbine-exhaust gas film (TN D-3836)",
                   True, _gf_note, _gf_note)
    s.cyc["gg_dump_isp_fraction"] = k_vac           # now computed, not the flat 0.55 / 0.80
    s.cyc["turbine_pressure_ratio"] = pr
    s.cyc["turbine_exhaust"] = exh
    s.turbine_exhaust = exh
    x = s.cyc["gg_flow_fraction"]
    s.isp_vac_eng = tp.engine_isp_with_gg_dump(s.isp_vac_chamber, x, k_vac)
    s.isp_sl_eng = tp.engine_isp_with_gg_dump(s.isp_sl_chamber, x, k_sl)

    _p = lambda pa: f"{pa/1e3:.0f} kPa"
    _check(s.checklist, s.warnings, "turbopump", "Turbine exhaust back pressure",
           pr >= turbine_exhaust.TURBINE_PR_LOW_WARN,
           f"The {exh['mode'].replace('_', ' ')} exhaust has to leave sonic into "
           f"{_p(s.te_discharge_pa)}, which holds the turbine outlet at {_p(exh['p_turbine_out_pa'])} "
           f"and leaves the turbine only PR {pr:.1f} (inlet {_p(s.te_p_in_pa)}): each kg of drive "
           f"gas does little work, so the GG flow balloons. Raise Pc, or inject the exhaust into "
           f"the nozzle further downstream (lower static pressure).",
           (f"OK - PR {pr:.1f}, "
            + (f"back-pressure limited (outlet {_p(exh['p_turbine_out_pa'])}, exhaust leaves sonic "
               f"into {_p(s.te_discharge_pa)})" if s.te_pr_limited
               else f"at the {s.te_pr_cap:.0f} cap (discharge {_p(s.te_discharge_pa)})")))
    if exh["hx_on"]:
        _coils = " + ".join(filter(None, [
            f"{exh['hx_gox_kgs']:.2f} kg/s GOX" if exh["hx_gox_kgs"] > 0.0 else "",
            f"{exh['hx_he_kgs']:.2f} kg/s He" if exh["hx_he_kgs"] > 0.0 else ""]))
        _check(s.checklist, s.warnings, "turbopump", "Exhaust heat-exchanger outlet temperature",
               exh["t_exhaust_k"] >= turbine_exhaust.EXHAUST_T_FLOOR_K,
               f"The exhaust heat exchanger ({_coils}, {exh['hx_duty_w']/1e3:.0f} kW) chills "
               f"the turbine exhaust to {exh['t_exhaust_k']:.0f} K, below "
               f"~{turbine_exhaust.EXHAUST_T_FLOOR_K:.0f} K where fuel-rich exhaust starts "
               f"condensing heavy species/water in the duct. Heat less GOX/He.",
               f"OK - exhaust {exh['t_turbine_exit_k']:.0f} -> {exh['t_exhaust_k']:.0f} K "
               f"({_coils})")
    elif (self.turbine_exhaust_hx_gox_kgs or 0.0) > 0.0:
        _check(s.checklist, s.warnings, "turbopump", "Exhaust heat exchanger",
               False,
               f"A LOX->GOX exhaust heat exchanger was requested but {self.propellant_pair} has "
               f"no liquid oxygen to heat - ignored.", "")
    if exh["mode"] == "nozzle_injection":
        _inj_ok = float(self.turbine_exhaust_inject_eps) < float(self.expansion_ratio)
        _check(s.checklist, s.warnings, "cooling", "Turbine-exhaust injection station",
               _inj_ok,
               f"turbine_exhaust_inject_eps {self.turbine_exhaust_inject_eps:.1f} is at or past "
               f"the nozzle exit (eps {self.expansion_ratio:.1f}) - clamped to the exit; pick "
               f"an area ratio inside the nozzle (F-1: 10 on a 16:1 bell).",
               f"OK - exhaust enters the nozzle at eps {s.te_inject_eps:.1f} "
               f"(local static {_p(s.te_local_static_pa)}); "
               + ("fuel is non-cryogenic: drain the exhaust manifold - an Atlas looped-tube "
                  "exhaust manifold trapped RP-1 that detonated on the next start [SP-8120]"
                  if not self.propellant_pair.startswith("LOX/LH2") else "cryogenic fuel"))
