"""
Per-cycle behavior: gas generator, pressure-fed, tap-off, fuel-rich staged
combustion (FRSC), oxidizer-rich staged combustion (ORSC), full-flow staged
combustion (FFSC), expander, and electric pump-fed.

Note: propellant TANK mass/pressure rating is RealismOverhaul/RealFuels
territory (procedural tanks handle that as separate parts) - this module
only models what belongs to the ENGINE itself. For a pressure-fed engine
that means: no turbopump hardware, and a reported required feed pressure
(useful for the player picking a matching RO tank) - not a tank-mass model.

Each cycle now has its own physics:
  - GAS_GENERATOR / TAP_OFF: open cycles, `gas_generator_result()` here. Tap-off
    differs in the drive-gas source (main-chamber products, film-cooled) and a
    better dump-Isp fraction - `physics/design.py` supplies the tap-off gas.
  - FRSC / ORSC / FFSC: closed staged-combustion cycles - `physics/staged_combustion.py`
    (fuel-rich vs oxidiser-rich vs both preburners, asymmetric pump discharge).
  - EXPANDER: `physics/expander.py` (turbine driven by regen-coolant heat).
  - ELECTRIC_PUMP: `physics/electric_pump.py` (battery+motor drives the pumps,
    no turbine, no bleed).
"""
from . import turbopump as tp

GAS_GENERATOR = "gas_generator"
PRESSURE_FED = "pressure_fed"
TAP_OFF = "tap_off"
FRSC = "frsc"
ORSC = "orsc"
FFSC = "ffsc"
EXPANDER = "expander"
ELECTRIC_PUMP = "electric_pump"

CYCLES = [GAS_GENERATOR, PRESSURE_FED, TAP_OFF, FRSC, ORSC, FFSC, EXPANDER, ELECTRIC_PUMP]

# Single source of truth for human-readable cycle names - shared by the GUI
# dropdown and the .cfg header text, so they can't drift apart.
CYCLE_DISPLAY = {
    GAS_GENERATOR: "gas generator",
    PRESSURE_FED: "pressure-fed",
    TAP_OFF: "tap-off",
    FRSC: "fuel-rich staged combustion (FRSC)",
    ORSC: "oxidizer-rich staged combustion (ORSC)",
    FFSC: "full-flow staged combustion (FFSC)",
    EXPANDER: "expander",
    ELECTRIC_PUMP: "electric pump-fed",
}

# Cycles whose turbopump is driven by a combustion-gas turbine fed from a
# preburner/GG/tap-off (turbine-work math in gas_generator_result / staged_combustion).
GG_FAMILY_CYCLES = (GAS_GENERATOR, TAP_OFF, FRSC, ORSC, FFSC)
# Closed staged-combustion cycles (preburner exhaust rejoins the main chamber).
STAGED_CYCLES = (FRSC, ORSC, FFSC)
# Cycles with no overboard turbine-exhaust dump -> no bleed Isp penalty.
CLOSED_CYCLES = (FRSC, ORSC, FFSC, EXPANDER, ELECTRIC_PUMP, PRESSURE_FED)


def gas_generator_result(mdot, mr, pc, dp_fuel, dp_ox, rho_fuel, rho_ox,
                          eta_fuel, eta_ox, specific_power_w_kg, gg_tin_k, gg_cp, gg_eta_turbine,
                          gg_pressure_ratio, gg_gamma, gg_dump_isp_fraction=0.55,
                          cycle_name=GAS_GENERATOR, gg_mixture_ratio=None):
    """
    Open GG / tap-off cycle. With `gg_mixture_ratio` given (a real GG), the GG's
    own propellant draw is PUMPED too: the pumps move mdot + mdot_gg, split at the
    GG mixture ratio, and mdot_gg itself depends on that pump power - solved by
    fixed-point iteration (converges in a few passes; mdot_gg is a few % of mdot).
    `gg_mixture_ratio=None` (tap-off: the turbine gas is already-pumped chamber
    flow) keeps the pumps on chamber mdot only.
    """
    mdot_fuel_c = mdot / (1.0 + mr)
    mdot_ox_c = mdot - mdot_fuel_c
    mdot_gg = 0.0
    for _ in range(12 if gg_mixture_ratio is not None else 1):
        if gg_mixture_ratio is not None:
            fuel_p = mdot_fuel_c + mdot_gg / (1.0 + gg_mixture_ratio)
            ox_p = mdot_ox_c + mdot_gg * gg_mixture_ratio / (1.0 + gg_mixture_ratio)
            mdot_p, mr_p = fuel_p + ox_p, ox_p / fuel_p
        else:
            mdot_p, mr_p = mdot, mr
        tpump = tp.turbopump_power(mdot_p, mr_p, dp_fuel, dp_ox, rho_fuel, rho_ox, eta_fuel,
                                    eta_ox, specific_power_w_kg)
        prev = mdot_gg
        mdot_gg, dh = tp.gg_flow_fraction(tpump["power_total_w"], gg_tin_k, gg_cp,
                                           gg_eta_turbine, gg_pressure_ratio, gg_gamma)
        if abs(mdot_gg - prev) <= 1e-6 * max(mdot_gg, 1e-9):
            break
    gg_fraction = mdot_gg / mdot
    return {
        "cycle": cycle_name,
        "has_turbopump": True,
        "turbopump": tpump,
        "gg_mdot_kgs": mdot_gg,
        "gg_flow_fraction": gg_fraction,
        "gg_dump_isp_fraction": gg_dump_isp_fraction,
        "turbine_specific_work_j_kg": dh,  # for physics/turbopump_sizing.py (turbine pitchline)
        "required_tank_pressure_pa": None,  # turbopump handles the pressure rise; tanks stay low-pressure
    }


def pressure_fed_result(pc, dp_injector, tank_margin_pa=0.3e6):
    """No turbopump: the propellant tanks themselves must supply chamber pressure
    plus injector pressure drop plus a line-loss/regulator-droop margin."""
    p_tank = tp.pressure_fed_tank_pressure(pc, dp_injector, tank_margin_pa)
    return {
        "cycle": PRESSURE_FED,
        "has_turbopump": False,
        "turbopump": None,
        "gg_mdot_kgs": 0.0,
        "gg_flow_fraction": 0.0,
        "gg_dump_isp_fraction": 0.0,
        "turbine_specific_work_j_kg": 0.0,
        "required_tank_pressure_pa": p_tank,
    }
