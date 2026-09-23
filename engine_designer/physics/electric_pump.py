"""
Electric pump-fed cycle: brushless DC motors driven by a battery run the
propellant pumps - no turbine, no preburner, no bled/dumped flow, so engine Isp
is the chamber Isp. The cost is carried as MASS: a battery sized for the whole
burn plus the motors.

Real reference: RocketLab Rutherford (LOX/RP-1, ~26 kN, Pc ~12 MPa, ~35 kg dry
including the electrical hardware). The trade only pays off at small scale /
short burn, because battery mass scales with burn TIME.

Simplified like physics/expander.py: pump shaft power from the same
turbopump.turbopump_power() call, then electrical energy = shaft power / drive
efficiency x burn time, then battery mass = energy / specific energy.
"""
from . import turbopump as tp

MOTOR_EFFICIENCY = 0.92          # brushless DC motor, shaft/electrical
INVERTER_EFFICIENCY = 0.97       # motor controller / ESC
BATTERY_SPECIFIC_ENERGY_J_KG = 7.2e5   # ~200 Wh/kg USABLE - a high-energy jettisonable
                                        # pack sized for the whole burn (Rutherford class;
                                        # aggressive but the pack is staged, not carried far)
MOTOR_SPECIFIC_POWER_W_KG = 10000.0    # aerospace BLDC + controller, electrical power per kg


def electric_pump_result(mdot, mr, pc, dp_fuel, dp_ox, rho_fuel, rho_ox,
                          eta_fuel, eta_ox, specific_power_w_kg, burn_time_s):
    tpump = tp.turbopump_power(mdot, mr, dp_fuel, dp_ox, rho_fuel, rho_ox,
                                eta_fuel, eta_ox, specific_power_w_kg)
    shaft_power_w = tpump["power_total_w"]
    electrical_power_w = shaft_power_w / (MOTOR_EFFICIENCY * INVERTER_EFFICIENCY)
    electrical_energy_j = electrical_power_w * max(burn_time_s, 0.0)
    battery_mass_kg = electrical_energy_j / BATTERY_SPECIFIC_ENERGY_J_KG
    motor_mass_kg = electrical_power_w / MOTOR_SPECIFIC_POWER_W_KG
    return {
        "cycle": "electric_pump",
        "has_turbopump": True,             # it has pumps (just no turbine)
        "turbopump": tpump,
        "gg_mdot_kgs": 0.0,
        "gg_flow_fraction": 0.0,
        "gg_dump_isp_fraction": 1.0,       # no dump
        "turbine_specific_work_j_kg": 0.0,  # no turbine
        "required_tank_pressure_pa": None,
        # electric-pump diagnostics:
        "battery_mass_kg": battery_mass_kg,
        "motor_mass_kg": motor_mass_kg,
        "electrical_power_w": electrical_power_w,
        "electrical_energy_j": electrical_energy_j,
    }


if __name__ == "__main__":
    # Rutherford-ish: LOX/RP-1, ~26 kN vac, Isp ~317 -> mdot ~8.4 kg/s, Pc 12 MPa,
    # burn 150 s. Expect battery+motor a real fraction of the ~35 kg dry mass.
    G0 = 9.80665
    mdot = 26_000.0 / (317.0 * G0)
    r = electric_pump_result(
        mdot, 2.5, 12.0e6,
        12.0e6 + 1.0e6, 12.0e6 + 0.5e6, 810.0, 1141.0, 0.65, 0.68, 20000.0, 150.0)
    tot = r["battery_mass_kg"] + r["motor_mass_kg"]
    assert 8.0 <= tot <= 90.0, tot   # electric hardware IS a heavy fraction at this Pc/burn
    assert r["turbine_specific_work_j_kg"] == 0.0
    print(f"electric_pump.py smoke test OK - {mdot:.1f} kg/s, "
          f"{r['electrical_power_w']/1e3:.0f} kW electrical, "
          f"battery {r['battery_mass_kg']:.1f} kg + motor {r['motor_mass_kg']:.1f} kg "
          f"({r['electrical_energy_j']/3.6e6:.1f} kWh)")
