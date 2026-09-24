"""
Turbopump power balance and gas-generator flow fraction. Generalized copy of
the validated math in /home/cory/ksp_config/sim/engine_physics.py - same
formulas, no re-derivation.
"""


def pump_power(mdot, dp, rho, eta):
    """Shaft power [W] to raise `mdot` [kg/s] through `dp` [Pa] at density `rho`, efficiency `eta`."""
    return mdot * dp / (rho * eta)


def turbopump_power(mdot_total, mr, dp_fuel, dp_ox, rho_fuel, rho_ox, eta_fuel, eta_ox,
                     specific_power_w_kg):
    """
    Split total flow by mixture ratio and sum fuel + ox pump shaft power.

    specific_power_w_kg (shaft power per kg of turbopump ASSEMBLY mass, from
    the chosen physics/turbopump_tech.py tier) turns that power into a mass
    estimate - the turbopump's physical size/mass was previously never
    computed anywhere, even though dp_fuel/dp_ox (and hence this power
    number) already scale with chamber pressure. See turbopump_tech.py's
    docstring for exactly what each tier's specific power is sourced from.
    """
    mdot_fuel = mdot_total / (1.0 + mr)
    mdot_ox = mdot_total - mdot_fuel
    p_fuel = pump_power(mdot_fuel, dp_fuel, rho_fuel, eta_fuel)
    p_ox = pump_power(mdot_ox, dp_ox, rho_ox, eta_ox)
    power_total_w = p_fuel + p_ox
    return {
        "mdot_fuel_kgs": mdot_fuel, "mdot_ox_kgs": mdot_ox,
        "power_fuel_w": p_fuel, "power_ox_w": p_ox,
        "power_total_w": power_total_w,
        "turbopump_mass_kg": power_total_w / specific_power_w_kg,
    }


def gg_flow_fraction(pump_power_total_w, tin_k, cp, eta_turbine, pressure_ratio, gamma_gg):
    """
    Gas-generator mass flow needed to drive the turbopump, from a simple
    turbine specific-work model:
        dh = cp * Tin * eta_turbine * (1 - PR^(-(gamma-1)/gamma))
        mdot_gg = pump_power_total / dh
    """
    exponent = (gamma_gg - 1.0) / gamma_gg
    dh = cp * tin_k * eta_turbine * (1.0 - pressure_ratio ** (-exponent))
    mdot_gg = pump_power_total_w / dh
    return mdot_gg, dh


def engine_isp_with_gg_dump(chamber_isp, gg_flow_fraction_x, gg_dump_isp_fraction=0.55):
    """
    Mass-average the main-chamber Isp with the gas-generator-dump flow.
    gg_dump_isp_fraction is a documented engineering assumption (not
    derived): a skirt-dumped, fuel-rich, lower-pressure-ratio exhaust is
    assumed to deliver this fraction of the main chamber's specific impulse.

    gg_flow_fraction_x is CHAMBER-relative (mdot_gg / mdot_chamber, as
    cycles.gas_generator_result reports it): the GG draw is EXTRA propellant on
    top of the chamber flow, so the engine Isp is the total-flow average
        (mdot_c*Isp_c + mdot_gg*k*Isp_c) / (mdot_c + mdot_gg)
    = Isp_c * (1 + x*k) / (1 + x), and engine thrust = (mdot_c + mdot_gg) *
    that Isp. (Before 2026-09-24 this treated x as a share of TOTAL flow while
    thrust was chamber mdot x engine Isp - thrust came out x*(1-k) low and the
    reported mdot omitted the GG flow.)
    """
    x = gg_flow_fraction_x
    return chamber_isp * (1.0 + x * gg_dump_isp_fraction) / (1.0 + x)


def pressure_fed_tank_pressure(pc, dp_injector, margin_pa=0.3e6):
    """
    Required propellant tank pressure for a pressure-fed engine (no
    turbopump): chamber pressure + injector pressure drop + a margin for
    line losses / regulator droop over the burn.
    """
    return pc + dp_injector + margin_pa
