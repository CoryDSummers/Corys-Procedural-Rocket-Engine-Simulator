"""
Renders an EngineDesign + its compute() result to RealFuels CONFIG text,
following the exact conventions used by H3-250K_Config.cfg / TR341_Config.cfg
(header spec table, design-premise comments, the two-patch shape: engine
definition :AFTER[RealismOverhaulEngines], optional RP-1 gating
:NEEDS[RP-0]:BEFORE[RealismOverhaulEnginesPost]).

Derived fields (export-time only - none of this feeds compute() or moves a
validate.py spot check):
  * `cost` / `entryCost` - estimated by physics/cost_model.py from the computed
    dry mass, chamber pressure, cycle complexity and chamber count (the caller
    can still override either). `cost` goes on the CONFIG block always; `cost`
    on a `ModuleEngineConfigs` CONFIG is a per-config recurring VAB delta.
    `entryCost` only appears in the RP-1 gating patch (RF's auto-RFUpgrade
    needs a `techRequired` to be meaningful without it).
  * The TESTFLIGHT ignition/cycle reliability curves are DERIVED from the design
    (physics/reliability.py) with the chosen controller tier as the anchor - a
    modern FFSC and a crude pressure-fed no longer get identical numbers.
  * `throttleResponseRate` / `varyIsp` / `varyMixture` / `residualsThresholdBase`
    still come straight from the controller tier (physics/controller_tech.py).
  * `massMult` defaults to 1.0 (host part's stock mass); the GUI usually passes
    a real ratio from result["computed_dry_mass_kg"] vs the host's stock mass.
  * `rated_burn_time_s` defaults to result["rated_burn_time_s"] (chamber-
    material-driven); `tested_burn_time_s` = rated x a controller-tier
    multiplier nudged by a reusability signal (physics/reliability.py
    derived_burn_times), except ablative chambers which get tested == rated.
  * `new_part_standalone`'s `+PART` clone explicitly sets `%RSSROConfig = True`
    on the new part. Without it, RealismOverhaul_Global_Config.cfg's
    zzzRealismOverhaul pass (`HAS[~RSSROConfig[]]`) prepends "non RO - " to
    the title, blanks/rewrites the description, and sets category to hidden
    (-1) or a "Non-RO" filter bucket - which also makes the part vanish from
    wherever RP-1's tech-node gating would otherwise place it, even though
    %techRequired was written correctly. This field is set per real part by
    RO's own mod-compat patches keyed on the DONOR part's actual name, not
    reliably inherited onto a renamed clone, so it must be set here too.
"""
from ..physics import controller_tech as controller_tech_mod
from ..physics import cost_model as cost_model_mod
from ..physics import cycles as cycles_mod
from ..physics import ignition as ignition_mod
from ..physics import injectors as injectors_mod
from ..physics import materials as materials_mod
from ..physics import reliability as reliability_mod
from ..physics.combustion import is_monopropellant, propellant_densities

# RF resource names per propellant pair. Ignitor resources now come from the
# chosen ignition system (physics/ignition.py), not a per-pair default.
# Hydrazine's "ox" is None - a monopropellant, not a fuel/oxidizer pair - render_cfg()
# branches on this to emit a single PROPELLANT block instead of a fuel/ox pair.
_RF_PROPELLANTS = {
    "LOX/RP-1": {"fuel": "RP-1", "ox": "LqdOxygen"},
    "LOX/LH2": {"fuel": "LqdHydrogen", "ox": "LqdOxygen"},
    "LOX/CH4": {"fuel": "LqdMethane", "ox": "LqdOxygen"},
    "N2O4/MMH": {"fuel": "MMH", "ox": "NTO"},
    "Aerozine-50/NTO": {"fuel": "Aerozine50", "ox": "NTO"},
    "Hydrazine": {"fuel": "Hydrazine", "ox": None},
    "H2O2": {"fuel": "HTP", "ox": None},
}


def _propellant_ratios(pair, mr):
    """Volumetric PROPELLANT ratio fields (RF convention) from a mass mixture ratio."""
    rho_fuel, rho_ox = propellant_densities(pair)
    # ratio_ox / ratio_fuel = MR * rho_fuel / rho_ox ; normalize to sum to 1.
    raw_ox = mr * rho_fuel / rho_ox
    total = 1.0 + raw_ox
    ratio_fuel = 1.0 / total
    ratio_ox = raw_ox / total
    return ratio_fuel, ratio_ox


def _throttle_isp_curve_block(result, throttle_floor):
    """Build a throttleIspCurve from the throttle-sweep separation onset, same
    style as H4-250K_Config.cfg. Returns None if the whole band is clean at
    sea level (onset <= throttle_floor) - no curve needed."""
    onset = result["separation_onset_throttle"]
    if onset is None or onset <= throttle_floor + 1e-9:
        return None
    ramp_end = min(onset + 0.15, 1.0)
    lines = [
        "\t\t\tuseThrottleIspCurve = true",
        "\t\t\tthrottleIspCurve",
        "\t\t\t{",
        f"\t\t\t\tkey = 0.00 0.001 0 0",
        f"\t\t\t\tkey = {onset:.2f} 0.001 0 0\t//separation onset from the design's throttle sweep",
        f"\t\t\t\tkey = {ramp_end:.2f} 0.85  0 0",
        f"\t\t\t\tkey = 1.00 1.00  0 0",
        "\t\t\t}",
        "\t\t\tthrottleIspCurveAtmStrength",
        "\t\t\t{",
        "\t\t\t\tkey = 0.0 0.02",
        "\t\t\t\tkey = 1.0 1.0",
        "\t\t\t}",
    ]
    return "\n".join(lines)


def _sanitize_part_name(s):
    """A KSP part `name` token: letters/digits/_/- only ('.' is a config path
    separator; spaces aren't allowed)."""
    import re
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", (s or "").strip()).strip("-")
    return cleaned or "CustomEngine"


def render_cfg(design, result, config_name, manufacturer="Fictional", mass_mult=1.0,
                rated_burn_time_s=None, tested_burn_time_s=None,
                ignitions=None, tech_node=None, entry_cost=None, cost=None,
                output_mode="additional_config", model_scale=None, new_part=None):
    """
    design: physics.design.EngineDesign
    result: design.compute()
    config_name: RF CONFIG `name` field, e.g. "MyEngine-100K"
    Returns the full .cfg file text as a string.

    `cost` / `entry_cost`: if not passed in, both are estimated from the design
    (physics/cost_model.py). `cost` is written on the CONFIG block always;
    `entry_cost` only appears in the RP-1 gating patch (RF's auto-RFUpgrade
    needs a `techRequired` to be meaningful).

    `output_mode`:
      "additional_config"   - append a CONFIG to the host part's
                              ModuleEngineConfigs (historical behaviour; output
                              is byte-for-byte unchanged from before).
      "new_part_in_place"   - additional_config PLUS a patch that rescales the
                              host part's model to this engine's length.
      "new_part_standalone" - a separate part that borrows the host model
                              (rescaled), with its own name / title / tech gating
                              (generated equivalent of TR341_Config.cfg).
    `model_scale`: uniform rescaleFactor multiplier (designed length / host model
      native height). None or ~1.0 -> no rescale patch emitted. Only consulted by
      the two new-part modes.
    `new_part`: dict for "new_part_standalone" - {name, title, manufacturer,
      description}; any missing key is derived from `config_name`.
    """
    _cost_est = cost_model_mod.estimate_cost(design, result)
    if cost is None:
        cost = _cost_est["cost"]
    if entry_cost is None:
        entry_cost = _cost_est["entry_cost"]

    host = design.host_model_engine_type
    if not host:
        raise ValueError("design.host_model_engine_type must be set (pick a host model)")

    if output_mode not in ("additional_config", "new_part_in_place", "new_part_standalone"):
        raise ValueError(f"unknown output_mode {output_mode!r}")
    _scaling = (output_mode in ("new_part_in_place", "new_part_standalone")
                and model_scale is not None and abs(model_scale - 1.0) > 1e-3)
    _standalone = output_mode == "new_part_standalone"

    np = dict(new_part or {})
    new_name = _sanitize_part_name(np.get("name") or config_name)
    new_title = np.get("title") or config_name
    new_mfr = np.get("manufacturer") or manufacturer or "Fictional"
    new_desc = np.get("description") or (
        f"Custom engine designed with engine_designer/. {design.propellant_pair} "
        f"{cycles_mod.CYCLE_DISPLAY[design.cycle]}, Pc "
        f"{design.chamber_pressure_pa / 1e6:.1f} MPa. Borrows the {host} model.")
    # In standalone mode the part mass is pinned by `origMass` (tonnes) on the
    # MODULE, exactly like TR341_Config.cfg, so rescaleFactor stays visual-only
    # and can't double-count mass; the CONFIG's massMult is then 1.0.
    config_mass_mult = 1.0 if _standalone else mass_mult
    # Selector the gimbal / gating patches attach to.
    if _standalone:
        target_selector = f"@PART[{new_name}]"
    else:
        target_selector = f"@PART[*]:HAS[#engineType[{host}]]"

    pair = design.propellant_pair
    rf = _RF_PROPELLANTS[pair]
    mono = is_monopropellant(pair)
    chamber_material = materials_mod.MATERIALS[design.material_key]

    if rated_burn_time_s is None:
        rated_burn_time_s = result["rated_burn_time_s"]
    if ignitions is None:
        ignitions = design.ignitions

    cycle_label = cycles_mod.CYCLE_DISPLAY[design.cycle]
    injector = injectors_mod.INJECTORS[design.injector_type]
    ign_sys = ignition_mod.IGNITION_SYSTEMS[design.ignition_system]
    ctrl = controller_tech_mod.CONTROLLER_TECHS[design.controller_tech_key]

    # TESTFLIGHT reliability + tested burn time are DERIVED from the design
    # (physics/reliability.py) with the controller tier as the anchor - a modern
    # FFSC and a crude pressure-fed no longer get identical curves. Export-time
    # only, so no compute()/validate.py number moves.
    # The RESOLVED chamber cooling method (physics/cooling.resolve_cooling_method)
    # - an explicit "ablative" on a non-ablative liner still gets the
    # char-consumption ratedBurnTime, and vice versa.
    _chamber_cooling = result["cooling"].get("chamber_cooling_method",
                                             chamber_material.cooling_method)
    _nozzle_cooling = result["cooling"].get("nozzle_cooling_method", "")
    _is_ablative = _chamber_cooling == "ablative"
    rel = reliability_mod.derived_reliability(design, result, ctrl)
    if tested_burn_time_s is None:
        rated_burn_time_s, tested_burn_time_s = reliability_mod.derived_burn_times(
            design, result, ctrl, rated_burn_time_s=rated_burn_time_s,
            is_ablative=_is_ablative)

    min_thrust_kn = result["thrust_vac_floor_n"] / 1e3
    max_thrust_kn = result["thrust_vac_n"] / 1e3
    isp_vac = result["isp_vac_engine_s"]
    isp_sl = result["isp_sl_engine_s"]

    if design.nozzle_type == "bell":
        nozzle_desc = (f"Bell ({design.bell_percent_length:.0f}% length, "
                        f"theta_n {result['theta_n_deg']:.1f} / theta_e {result['theta_e_deg']:.1f} deg)")
    else:
        nozzle_desc = f"Conical ({design.nozzle_half_angle_deg:.1f} deg half-angle)"

    header_lines = [
        "//\t" + "=" * 78,
        f"//\t{config_name}  -  designed with engine_designer/ (fictional, unless you renamed it)",
        "//",
        f"//\tPropellant: {pair}   Mixture ratio: "
        + ("N/A (monopropellant)" if mono else f"{design.mixture_ratio:.2f}"),
        f"//\tCycle: {cycle_label}   Chamber Pressure: {design.chamber_pressure_pa/1e6:.2f} MPa",
        f"//\tExpansion ratio: {design.expansion_ratio:.1f}   Nozzle: {nozzle_desc}",
        f"//\tInjector: {injector.display_name}   Ignition: {ign_sys.display_name}",
        f"//\tContraction ratio: {design.contraction_ratio:.2f}   L*: {design.lstar_m:.2f} m"
        + (f"   (combustion completeness {result['completeness_factor']:.2f}x - chamber may be "
           f"short for this propellant/injector)" if result['completeness_factor'] < 0.95 else ""),
        f"//\tChamber material: {materials_mod.MATERIALS[design.material_key].display_name} "
        f"(margin {result['material_margin']['margin_ratio']:.2f}x @ Tc {result['tc_k']:.0f} K)",
        f"//\tChamber cooling: {_chamber_cooling} "
        f"({result['cooling'].get('chamber_cooling_source', 'material-default')})   "
        f"Nozzle cooling: {_nozzle_cooling} "
        f"({result['cooling'].get('nozzle_cooling_source', 'material-default')})"
        + (f"\n//\tDump-cooled nozzle slice: {result['cooling']['dump_coolant_fraction']*100:.1f}% "
           f"of fuel, ~{result['cooling']['dump_coolant_dt_k']:.0f} K rise, Isp penalty "
           f"{result['cooling']['dump_isp_penalty_fraction']*100:.2f}%"
           if result["cooling"].get("dump_isp_penalty_fraction") else ""),
        f"//\tNozzle-extension material (past eps {design.cooling_transition_eps:.0f}): "
        f"{materials_mod.MATERIALS[design.bell_material_key].display_name} "
        f"(margin {result['bell_material_margin']['margin_ratio']:.2f}x @ local T "
        f"{result['t_local_at_transition_k']:.0f} K)",
        "//",
        f"//\tThrust (Vac): {max_thrust_kn:.1f} kN   Thrust (Vac, floor): {min_thrust_kn:.1f} kN",
        f"//\tISP: {isp_sl:.1f} SL / {isp_vac:.1f} Vac",
        f"//\tThrottle: {design.throttle_floor*100:.0f} - 100%",
        f"//\tmdot: {result['mdot_kgs']:.1f} kg/s",
        f"//\tEstimated dry mass: {result['computed_dry_mass_kg']:.1f} kg (chamber/nozzle wall "
        f"{result['chamber_wall_mass_kg']+result['bell_wall_mass_kg']:.1f} kg + turbopump "
        f"{result['computed_dry_mass_kg']-result['chamber_wall_mass_kg']-result['bell_wall_mass_kg']-result.get('stability_aid_mass_kg', 0.0)-result.get('injector_plate_mass_kg', 0.0)-result.get('manifold_mass_kg', 0.0)-result.get('plumbing_mass_kg', 0.0):.1f} kg"
        f" + injector plate {result.get('injector_plate_mass_kg', 0.0):.1f} kg"
        f" + manifold {result.get('manifold_mass_kg', 0.0):.1f} kg"
        + (f" + plumbing {result['plumbing_mass_kg']:.1f} kg" if result.get('plumbing_mass_kg', 0.0) > 0.0 else "")
        + (f" + stability aids {result['stability_aid_mass_kg']:.1f} kg" if result.get('stability_aid_mass_kg', 0.0) > 0.0 else "")
        + " - a LOWER BOUND, see physics/mass_model.py: no valves/actuators/mounting structure)",
        f"//\tRated / tested burn time: {rated_burn_time_s:.0f} / {tested_burn_time_s:.0f} s",
        "//",
    ]
    _sizing = result.get("turbopump_sizing")
    if _sizing:
        _fp = _sizing["fuel_pump"]
        _op = _sizing["ox_pump"]
        header_lines.append(
            f"//\tTurbopump: {_sizing['arrangement'].replace('_', ' ')}, {_sizing['n_turbines']}x "
            f"{_sizing['turbine_staging'].replace('_', ' ')} turbine, "
            f"{_fp['n_stages']}-stage fuel pump {_fp['n_rpm']:.0f} rpm / "
            f"{_op['n_stages']}-stage ox pump {_op['n_rpm']:.0f} rpm, {_sizing['material_display']}")
        header_lines.append(
            f"//\t  derived efficiency: fuel pump {_sizing['eta_pump_fuel']:.3f}, ox pump "
            f"{_sizing['eta_pump_ox']:.3f}, turbine {_sizing['eta_turbine']:.3f} "
            f"(overall {_sizing['eta_overall']:.3f}); assembly ~{_sizing['assembly_length_m']:.2f}x"
            f"{_sizing['assembly_od_m']:.2f} m, ~{_sizing['mass_kg']*_sizing['mass_modifier']:.0f} kg; "
            f"peak tip speed {max(_fp['u_tip_m_s'], _op['u_tip_m_s']):.0f} m/s "
            f"({'feasible' if _sizing['feasible'] else 'MARGINAL - see warnings'})")
        header_lines.append("//")

    _cyc = result.get("cycle_result") or {}
    _cname = _cyc.get("cycle")
    _cycle_note = ""
    if _cname == "electric_pump":
        _cycle_note = (
            f"battery {_cyc['battery_mass_kg']:.0f} kg + motor {_cyc['motor_mass_kg']:.0f} kg, "
            f"~{_cyc['electrical_energy_j']/3.6e6:.1f} kWh at {_cyc['electrical_power_w']/1e3:.0f} kW; "
            f"no turbine, no bleed - engine Isp = chamber Isp")
    elif _cname in ("frsc", "orsc", "ffsc"):
        _dg = _cyc.get("drive_gas", {})
        _boost = {"frsc": "fuel", "orsc": "ox", "ffsc": "both"}[_cname]
        _cycle_note = (
            f"{_cyc['preburner_gas_kind'].replace('_', '-')} preburner, "
            f"~{_cyc['preburner_flow_fraction']*100:.0f}% of flow ({_cyc['gg_mdot_kgs']:.1f} kg/s) "
            f"at ~{_dg.get('tin_k', 0):.0f} K; {_boost} pump(s) boosted > 2x Pc; "
            f"closed cycle - no dump loss")
    elif _cname in ("tap_off", "gas_generator"):
        _dg = _cyc.get("drive_gas", {})
        _cycle_note = (
            f"chamber tap-off gas film-cooled to ~{_dg.get('tin_k', 0):.0f} K, "
            if _cname == "tap_off" else "gas-generator ")
        _cycle_note += (f"bleed {_cyc['gg_flow_fraction']*100:.1f}% "
                        f"({_cyc['gg_mdot_kgs']:.1f} kg/s)")
        # physics/turbine_exhaust.py: where the spent drive gas goes. Its thrust
        # is already folded into the engine Isp/thrust above - RealFuels has no
        # separate exhaust stream, and (like RO's own LR-91) no roll module is
        # emitted for a canted exhaust nozzle.
        _te = result.get("turbine_exhaust")
        if _te:
            _cycle_note += (
                f"; turbine exhaust: {_te['mode'].replace('_', ' ')}, turbine PR "
                f"{_te['turbine_pressure_ratio']:.1f}, {_te['t_exhaust_k']:.0f} K, exhaust Isp "
                f"{_te['isp_vac_s']:.0f} s vac ({_te['isp_fraction_vac']*100:.0f}% of chamber)")
            if _te.get("hx_on"):
                _cycle_note += f", LOX->GOX heat exchanger {_te['hx_gox_kgs']:.2f} kg/s"
            if abs(_te.get("roll_torque_nm") or 0.0) > 0:
                _cycle_note += (f", canted {_te['cant_deg']:.0f} deg: "
                                f"{_te['roll_torque_nm']:.0f} N.m roll torque (not exported)")
    if _cycle_note:
        header_lines.append(f"//\tCycle detail: {_cycle_note}")
        header_lines.append("//")

    if result["warnings"]:
        header_lines.append("//\tWARNINGS from the design tool (review before using in a career save):")
        for w in result["warnings"]:
            header_lines.append(f"//\t  - {w}")
        header_lines.append("//")

    origmass_t = result["computed_dry_mass_kg"] / 1000.0
    _mode_desc = {
        "additional_config": f"additional CONFIG appended to the {host} part",
        "new_part_in_place": f"the {host} part, rescaled in place",
        "new_part_standalone": f"new standalone part '{new_name}' borrowing the {host} model",
    }[output_mode]
    header_lines.append(f"//\tOutput mode: {_mode_desc}")
    if _scaling:
        _L = result["profile_meta"]["total_length_m"]
        header_lines.append(
            f"//\t  model rescaleFactor x{model_scale:.4f} (design length {_L:.2f} m, "
            f"uniform scale)")
    if _standalone:
        header_lines.append(
            f"//\torigMass = {origmass_t:.4f} t - part mass pinned (TR341 convention); "
            f"CONFIG massMult = 1.0 and rescaleFactor is visual only.")
    else:
        header_lines.append(f"//\tmassMult = {mass_mult:.3f} (host part's stock mass x this multiplier). "
                             f"{'Estimated from the design physics above vs. the host part.' if abs(mass_mult - 1.0) > 1e-9 else 'Defaults to 1.0 (host part stock mass) unless the GUI computed a real ratio against the host.'}")
    if output_mode == "new_part_in_place" and _scaling:
        header_lines.append("//\t  NOTE: KSP scales part mass by rescaleFactor^3 - re-check "
                            "massMult against the rescaled host.")
    header_lines.append("//\t" + "=" * 78)
    header = "\n".join(header_lines)

    ignitor_lines = []
    for name, amount in ign_sys.rf_ignitor_resources:
        ignitor_lines.append("\t\t\tIGNITOR_RESOURCE")
        ignitor_lines.append("\t\t\t{")
        ignitor_lines.append(f"\t\t\t\tname = {name}")
        ignitor_lines.append(f"\t\t\t\tamount = {amount}")
        ignitor_lines.append("\t\t\t}")
    ignitor_block = "\n".join(ignitor_lines)
    if ign_sys.forces_single_ignition:
        ignitions = 1

    throttle_curve = _throttle_isp_curve_block(result, design.throttle_floor)
    throttle_curve_block = ("\n" + throttle_curve + "\n") if throttle_curve else ""

    pressure_fed_line = "\t\t\tpressureFed = True\n" if design.cycle == cycles_mod.PRESSURE_FED else "\t\t\tpressureFed = False\n"
    # A monopropellant uses a single positive-expulsion/surface-tension tank (no risk of
    # settling the "wrong" propellant) - matches MR-80B's real `ullage = False`. Bipropellant
    # designs keep the existing `ullage = True` convention (unchanged from before).
    ullage_line = "\t\t\tullage = False\n" if mono else "\t\t\tullage = True\n"

    if mono:
        propellant_block = f"""\t\t\tPROPELLANT
\t\t\t{{
\t\t\t\tname = {rf['fuel']}
\t\t\t\tratio = 1.0
\t\t\t\tDrawGauge = True
\t\t\t}}"""
    else:
        ratio_fuel, ratio_ox = _propellant_ratios(pair, design.mixture_ratio)
        propellant_block = f"""\t\t\tPROPELLANT
\t\t\t{{
\t\t\t\tname = {rf['fuel']}
\t\t\t\tratio = {ratio_fuel:.4f}
\t\t\t\tDrawGauge = True
\t\t\t}}

\t\t\tPROPELLANT
\t\t\t{{
\t\t\t\tname = {rf['ox']}
\t\t\t\tratio = {ratio_ox:.4f}
\t\t\t\tDrawGauge = False
\t\t\t}}"""

    # The CONFIG body (fields at 3-tab indent) - identical whether it sits inside
    # an `@MODULE[ModuleEngineConfigs]` patch (additional_config / in-place) or a
    # freshly-built `MODULE { name = ModuleEngineConfigs ... }` (standalone).
    config_inner = f"""\t\t\tname = {config_name}
\t\t\tdescription = Custom engine designed with engine_designer/. {pair} {cycle_label}, {injector.display_name} injector, {ign_sys.display_name} ignition, Pc {design.chamber_pressure_pa/1e6:.2f} MPa, {nozzle_desc.lower()} nozzle, throttles {design.throttle_floor*100:.0f}-100%.
\t\t\tspecLevel = concept
\t\t\tminThrust = {min_thrust_kn:.2f}
\t\t\tmaxThrust = {max_thrust_kn:.2f}
\t\t\tratedBurnTime = {rated_burn_time_s:.0f}
\t\t\theatProduction = 100
\t\t\tmassMult = {config_mass_mult}
\t\t\tcost = {cost}
\t\t\tthrottleResponseRate = {ctrl.throttle_response_rate}
\t\t\tvaryIsp = {ctrl.vary_isp}
\t\t\tvaryMixture = {ctrl.vary_mixture}
\t\t\tresidualsThresholdBase = {ctrl.residuals_threshold_base}
{pressure_fed_line}{ullage_line}\t\t\tignitions = {ignitions}

{ignitor_block}

{propellant_block}

\t\t\tatmosphereCurve
\t\t\t{{
\t\t\t\tkey = 0 {isp_vac:.1f}
\t\t\t\tkey = 1 {isp_sl:.1f}
\t\t\t}}
{throttle_curve_block}
\t\t\tTESTFLIGHT:NEEDS[TestLite|TestFlight]
\t\t\t{{
\t\t\t\ttestedBurnTime = {tested_burn_time_s:.0f}
\t\t\t\tratedBurnTime = {rated_burn_time_s:.0f}
\t\t\t\tsafeOverburn = true
\t\t\t\tignitionReliabilityStart = {rel['ignition_reliability_start']:.6f}
\t\t\t\tignitionReliabilityEnd = {rel['ignition_reliability_end']:.6f}
\t\t\t\tcycleReliabilityStart = {rel['cycle_reliability_start']:.6f}
\t\t\t\tcycleReliabilityEnd = {rel['cycle_reliability_end']:.6f}
\t\t\t}}"""

    if _standalone:
        _rescale_line = f"\t@rescaleFactor *= {model_scale:.4f}\n" if _scaling else ""
        engine_patch = f"""+PART[*]:HAS[#engineType[{host}]]:NEEDS[RealismOverhaul&RealFuels]:BEFORE[RealismOverhaulEngines]
{{
\t@name = {new_name}
\t%engineType = {new_name}
\t%category = Engine
\t%title = {new_title}
\t%manufacturer = {new_mfr}
\t%description = {new_desc}
\t%RSSROConfig = True
\t@tags ^= :$: engine-designer custom fictional
{_rescale_line}\t!MODULE[ModuleEngineConfigs],*{{}}
\t!MODULE[ModuleAlternator],*{{}}
\t!RESOURCE,*{{}}
}}


//\t{'-' * 78}
//\tEngine definition for the new part (its own #engineType[{new_name}]).
//\torigMass pins the part mass in tonnes (TR341 convention).
//\t{'-' * 78}
@PART[{new_name}]:NEEDS[RealismOverhaul&RealFuels]:AFTER[RealismOverhaulEngines]
{{
\tMODULE
\t{{
\t\tname = ModuleEngineConfigs
\t\ttype = ModuleEngines
\t\tmodded = false
\t\tconfiguration = {config_name}
\t\torigMass = {origmass_t:.4f}
\t\tCONFIG
\t\t{{
{config_inner}
\t\t}}
\t}}
}}
"""
    else:
        engine_patch = f"""@PART[*]:HAS[#engineType[{host}]]:NEEDS[RealismOverhaul&RealFuels]:AFTER[RealismOverhaulEngines]
{{
\t@MODULE[ModuleEngineConfigs]
\t{{
\t\tCONFIG
\t\t{{
{config_inner}
\t\t}}
\t}}
}}
"""
        if output_mode == "new_part_in_place" and _scaling:
            engine_patch = f"""//\t{'-' * 78}
//\tRescale the host model to the designed engine's length (uniform rescaleFactor).
//\t{'-' * 78}
@PART[*]:HAS[#engineType[{host}]]:NEEDS[RealismOverhaul&RealFuels]:BEFORE[RealismOverhaulEngines]
{{
\t@rescaleFactor *= {model_scale:.4f}
}}


""" + engine_patch

    gimbal_patch = ""
    if design.gimbal_mode == "custom":
        response_lines = ""
        if design.gimbal_response_speed_deg_s > 0:
            response_lines = (f"\t\t%useGimbalResponseSpeed = true\n"
                               f"\t\t%gimbalResponseSpeed = {design.gimbal_response_speed_deg_s:.1f}\n")
        gimbal_patch = f"""

//\t{'-' * 78}
//\tGimbal: custom override ({design.gimbal_range_deg:.1f} deg).
//\t{'-' * 78}
{target_selector}:NEEDS[RealismOverhaul&RealFuels]:AFTER[RealismOverhaulEngines]
{{
\t@MODULE[ModuleGimbal]
\t{{
\t\t%gimbalRange = {design.gimbal_range_deg:.1f}
{response_lines}\t}}
}}
"""
    elif design.gimbal_mode == "ungimballed":
        gimbal_patch = f"""

//\t{'-' * 78}
//\tGimbal: explicitly removed (matches real small RCS/vernier-class engines
//\tand boosters that use separate vernier chambers for TVC instead of
//\tgimballing the main chamber).
//\t{'-' * 78}
{target_selector}:NEEDS[RealismOverhaul&RealFuels]:AFTER[RealismOverhaulEngines]
{{
\t!MODULE[ModuleGimbal],*{{}}
}}
"""
    # design.gimbal_mode == "inherit" -> gimbal_patch stays "" (no export change,
    # matches H3-250K/H4-250K's "inherited from the part" convention)

    gating_patch = ""
    if tech_node:
        gating_patch = f"""

//\t{'-' * 78}
//\tRP-1 career tech-tree gating.  No-ops without RP-1 installed (:NEEDS[RP-0]).
//\tentryCost / cost estimated by the design tool (physics/cost_model.py) - tune to taste.
//\t{'-' * 78}
{target_selector}:NEEDS[RP-0]:BEFORE[RealismOverhaulEnginesPost]
{{
\t@MODULE[ModuleEngineConfigs]
\t{{
\t\t@CONFIG[{config_name}]
\t\t{{
\t\t\t%techRequired = {tech_node}
\t\t\t%entryCost = {entry_cost}
\t\t\t%cost = {cost}
\t\t}}
\t}}
}}
"""

    return header + "\n\n" + engine_patch + gimbal_patch + gating_patch


def write_cfg(path, *args, **kwargs):
    text = render_cfg(*args, **kwargs)
    with open(path, "w") as f:
        f.write(text)
    return text


def _balanced(text):
    """Every '{' has a matching '}' (ignoring braces in // comments)."""
    depth = 0
    for line in text.splitlines():
        code = line.split("//", 1)[0]
        depth += code.count("{") - code.count("}")
        if depth < 0:
            return False
    return depth == 0


if __name__ == "__main__":
    from ..physics.design import EngineDesign

    base = EngineDesign(host_model_engine_type="F1", tech_node="orbitalRocketry",
                        gimbal_mode="custom", gimbal_range_deg=5.0)
    res = base.compute()
    tn = base.tech_node

    # additional_config: unchanged shape - the historical patch.
    a = render_cfg(base, res, "TestEngine-1M", tech_node=tn,
                   output_mode="additional_config")
    assert _balanced(a), "additional_config: unbalanced braces"
    assert "@PART[*]:HAS[#engineType[F1]]:NEEDS[RealismOverhaul&RealFuels]:AFTER[RealismOverhaulEngines]" in a
    assert "@MODULE[ModuleEngineConfigs]" in a and "\t\tCONFIG\n\t\t{" in a
    assert "\t\t\tmassMult = 1.0" in a
    assert "+PART[" not in a and "@rescaleFactor" not in a
    assert "@PART[*]:HAS[#engineType[F1]]:NEEDS[RP-0]:BEFORE[RealismOverhaulEnginesPost]" in a

    # new_part_in_place: same CONFIG patch + a prepended rescale patch.
    b = render_cfg(base, res, "TestEngine-1M", output_mode="new_part_in_place",
                   model_scale=0.75)
    assert _balanced(b), "new_part_in_place: unbalanced braces"
    assert "@rescaleFactor *= 0.7500" in b
    assert ":BEFORE[RealismOverhaulEngines]\n{\n\t@rescaleFactor *= 0.7500\n}" in b
    assert "@MODULE[ModuleEngineConfigs]" in b  # CONFIG still appended to the host

    # new_part_standalone: a borrowed-model copy + its own engine definition.
    c = render_cfg(base, res, "TestEngine 1M!", tech_node=tn,
                   output_mode="new_part_standalone", model_scale=0.509,
                   new_part={"name": "", "title": "Test Engine 1M",
                             "manufacturer": "ACME", "description": "hi"})
    assert _balanced(c), "new_part_standalone: unbalanced braces"
    assert "+PART[*]:HAS[#engineType[F1]]:NEEDS[RealismOverhaul&RealFuels]:BEFORE[RealismOverhaulEngines]" in c
    assert "@name = TestEngine-1M" in c and "%engineType = TestEngine-1M" in c  # sanitized
    assert "@rescaleFactor *= 0.5090" in c
    assert "!MODULE[ModuleEngineConfigs],*{}" in c
    # RealismOverhaul_Global_Config.cfg's zzzRealismOverhaul pass prepends
    # "non RO - " to the title and hides/recategorizes any part missing this
    # field - the standalone clone must set it explicitly, it is NOT reliably
    # inherited from the +PART donor.
    assert "\t%RSSROConfig = True\n" in c
    assert "\tMODULE\n\t{\n\t\tname = ModuleEngineConfigs" in c
    assert "\t\torigMass = " in c and "\t\t\tmassMult = 1.0" in c
    assert "@PART[TestEngine-1M]:NEEDS[RealismOverhaul&RealFuels]:AFTER[RealismOverhaulEngines]" in c
    assert "@PART[TestEngine-1M]:NEEDS[RP-0]:BEFORE[RealismOverhaulEnginesPost]" in c
    assert "#engineType[F1]" not in c.split("AFTER[RealismOverhaulEngines]", 1)[1]  # gimbal/gating retargeted

    # model_scale ~1.0 -> no rescale line even in a new-part mode.
    d = render_cfg(base, res, "X", output_mode="new_part_standalone", model_scale=1.0004)
    assert "@rescaleFactor" not in d

    try:
        render_cfg(base, res, "X", output_mode="bogus")
        raise AssertionError("expected ValueError for bad output_mode")
    except ValueError:
        pass

    # Explicit "ablative" cooling on an ablative liner: the resolved method
    # drives the char-consumption ratedBurnTime, so tested ~ rated (the
    # "ablative, no extra time" pattern), and the header names the method.
    abl = EngineDesign(host_model_engine_type="F1", material_key="ablative_phenolic",
                        chamber_cooling_method="ablative")
    abl_res = abl.compute()
    e = render_cfg(abl, abl_res, "AblTest-1M", output_mode="additional_config")
    assert "Chamber cooling: ablative (explicit)" in e
    # ...while "ablative" on a copper (regen-spec) liner is physically meaningless
    # and HARD-BLOCKED (materials.allowed_cooling_methods): it runs regen, and the
    # header says so rather than claiming an explicit choice.
    cu_blk = EngineDesign(host_model_engine_type="F1", material_key="narloy_z",
                           chamber_cooling_method="ablative")
    e_cu = render_cfg(cu_blk, cu_blk.compute(), "AblTest-2M", output_mode="additional_config")
    assert "Chamber cooling: regenerative (material-default - explicit ablative BLOCKED)" in e_cu
    import re as _re
    _rt = int(_re.search(r"ratedBurnTime = (\d+)", e).group(1))
    _tt = int(_re.search(r"testedBurnTime = (\d+)", e).group(1))
    assert abs(_tt - _rt) <= max(2, 0.25 * _rt), (_rt, _tt)   # ~equal, not the 6-17x regen margin

    # Dump-cooled nozzle extension: the header names the dump-cooled slice.
    dmp = EngineDesign(host_model_engine_type="F1", propellant_pair="LOX/LH2", mixture_ratio=5.5,
                        chamber_pressure_pa=11.0e6, expansion_ratio=45.0, cycle="gas_generator",
                        nozzle_type="bell", bell_percent_length=80.0, material_key="narloy_z",
                        nozzle_cooling_method="dump", regen_nozzle_end_eps=45.0,
                        target_vac_thrust_n=1_140_000.0)
    dmp_res = dmp.compute()
    f = render_cfg(dmp, dmp_res, "DumpTest-1M", output_mode="additional_config")
    assert "Nozzle cooling: dump (explicit)" in f
    assert "Dump-cooled nozzle slice:" in f and "Isp penalty" in f

    print("cfg_writer.py self-checks: OK")
