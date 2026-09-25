"""
2D turbopump systems / flow diagram for the GUI's "Turbopump" tab: tanks ->
pump(s) -> turbine(s) -> gas generator / preburner -> main chamber (or the
overboard dump), with each box annotated by the numbers physics/turbopump_sizing.py
and physics/cycles.py produce.

Kept independent of Tkinter (matplotlib Agg-testable) like gui/schematic.py -
see the __main__ block. A future 3D turbopump shape would be a separate module;
this is the information-dense view.
"""
from matplotlib.patches import FancyBboxPatch

_NEUTRAL = "#dcdcdc"
_OK = "#cfe8cf"
_WARN = "#f4e2b8"
_BAD = "#f0cccc"
_OXRICH = "#f0d9c0"           # oxidiser-rich preburner box (distinct from the fuel-rich yellow)
_FLOW = dict(arrowstyle="-|>", lw=1.4, color="#666666", shrinkA=3, shrinkB=3)
_SHAFT = dict(arrowstyle="-", lw=2.4, color="#333333", linestyle=(0, (5, 2)), shrinkA=3, shrinkB=3)

# Canvas
_W, _H = 12.0, 12.0
_XF, _XO = 2.7, 9.3           # fuel-side / ox-side column centres
_MID = 6.0


def _box(ax, cx, cy, w, h, text, color, *, fontsize=7.2):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                 boxstyle="round,pad=0.02,rounding_size=0.08",
                                 linewidth=1.1, edgecolor="#444444", facecolor=color, zorder=3))
    head, _, rest = text.partition("\n")
    ax.text(cx, cy + h / 2 - 0.14, head, ha="center", va="top", fontsize=fontsize + 0.6,
            fontweight="bold", zorder=4)
    if rest:
        ax.text(cx, cy + h / 2 - 0.44, rest, ha="center", va="top", fontsize=fontsize, zorder=4)


def _flow(ax, p0, p1, label=None, style=None):
    ax.annotate("", xy=p1, xytext=p0, arrowprops=style or _FLOW, zorder=2)
    if label:
        ax.text((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, label, ha="center", va="center",
                fontsize=6.2, color="#666666",
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9), zorder=4)


_EXHAUST_BOX_TEXT = {
    "overboard_duct": "OVERBOARD\nDUCT",
    "aspirator": "ASPIRATOR\n(exit slot)",
    "nozzle_injection": "INTO NOZZLE\n(film)",
}


def _exhaust_box(ax, result):
    """Open cycles: where the turbine exhaust goes (physics/turbine_exhaust.py),
    its own Isp, and a heat-exchanger box when there is one."""
    te = result.get("turbine_exhaust") or {}
    mode = te.get("mode", "overboard_duct")
    text = _EXHAUST_BOX_TEXT.get(mode, "OVERBOARD\nDUMP")
    if te:
        text += f"\n{te['isp_vac_s']:.0f} s vac"
    label = f"exhaust PR {te['turbine_pressure_ratio']:.0f}" if te else "exhaust"
    if te.get("hx_on"):
        # turbine -> heat exchanger -> disposal, stacked down the left margin
        _hx_coils = " + ".join(filter(None, [
            f"{te['hx_gox_kgs']:.2f} kg/s GOX" if te["hx_gox_kgs"] > 0.0 else "",
            f"{te['hx_he_kgs']:.2f} kg/s He" if te["hx_he_kgs"] > 0.0 else ""]))
        _box(ax, 1.4, 3.3, 2.0, 0.8, f"HEAT EXCH.\n{_hx_coils}", _NEUTRAL,
             fontsize=5.8)
        _box(ax, 1.4, 1.9, 2.0, 1.1, text, _NEUTRAL, fontsize=6.2)
        _flow(ax, (_XF, 4.15), (1.9, 3.7), label)
        _flow(ax, (1.4, 2.9), (1.4, 2.45))
    else:
        _box(ax, 1.4, 3.3, 2.0, 1.1, text, _NEUTRAL, fontsize=6.2)
        _flow(ax, (_XF, 4.15), (1.9, 3.8), label)


def draw_turbopump_diagram(ax, result):
    ax.clear()
    ax.set_xlim(0, _W)
    ax.set_ylim(0, _H)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    cyc = result["cycle_result"]
    inp = result["inputs"]
    pc_mpa = inp["chamber_pressure_pa"] / 1e6
    ox_name, fuel_name = inp["propellant_pair"].split("/")

    _box(ax, _XF, 11.0, 2.7, 1.0, f"FUEL TANK\n{fuel_name}", _NEUTRAL, fontsize=7)
    _box(ax, _XO, 11.0, 2.7, 1.0, f"OX TANK\n{ox_name}", _NEUTRAL, fontsize=7)

    if not cyc["has_turbopump"]:
        _box(ax, _MID, 11.0, 2.4, 1.0, "PRESSURANT\n(He)", _NEUTRAL, fontsize=7)
        ptank = cyc.get("required_tank_pressure_pa")
        ptxt = f"\nrequires tank pressure ~{ptank/1e6:.1f} MPa" if ptank else ""
        _box(ax, _MID, 3.2, 5.6, 1.6,
             f"MAIN CHAMBER\nPc {pc_mpa:.1f} MPa - {result['thrust_vac_n']/1e3:,.0f} kN vac{ptxt}",
             _NEUTRAL, fontsize=8)
        _flow(ax, (_XF, 10.4), (_XF + 0.8, 4.0), "fuel")
        _flow(ax, (_XO, 10.4), (_XO - 0.8, 4.0), "ox")
        _flow(ax, (_MID - 0.9, 10.6), (_XF + 0.3, 10.6))
        _flow(ax, (_MID + 0.9, 10.6), (_XO - 0.3, 10.6))
        ax.set_title("Turbopump / feed system - pressure-fed (no turbomachinery)", fontsize=9)
        return

    s = result["turbopump_sizing"]
    tp = cyc["turbopump"]
    fp, op, turb, ox_turb = s["fuel_pump"], s["ox_pump"], s["turbine"], s["ox_turbine"]
    status = _BAD if not s["feasible"] else (_WARN if s["warnings"] else _OK)
    tp_mass = (result["computed_dry_mass_kg"] - result["chamber_wall_mass_kg"]
               - result["bell_wall_mass_kg"])

    def _pump_txt(tag, pump, mdot, power_w, eta):
        lim = (100.0 / pump["tip_speed_margin"]) if pump["tip_speed_margin"] else 0.0
        return (f"{tag}\n{pump['n_stages']}-stage - {pump['n_rpm']:,.0f} rpm - eta {eta:.2f}\n"
                f"tip {pump['u_tip_m_s']:.0f} m/s ({lim:.0f}% of limit)\n"
                f"{mdot:.1f} kg/s - {power_w/1e3:,.0f} kW")

    _box(ax, _XF, 8.9, 3.2, 1.9,
         _pump_txt("FUEL PUMP", fp, tp["mdot_fuel_kgs"], tp["power_fuel_w"], s["eta_pump_fuel"]),
         status, fontsize=7)
    _box(ax, _XO, 8.9, 3.2, 1.9,
         _pump_txt("OX PUMP", op, tp["mdot_ox_kgs"], tp["power_ox_w"], s["eta_pump_ox"]),
         status, fontsize=7)
    _flow(ax, (_XF, 10.45), (_XF, 9.9))
    _flow(ax, (_XO, 10.45), (_XO, 9.9))

    cycle_name = cyc["cycle"]
    staging_short = s["turbine_staging"].replace("_", " ")
    two_turb = s["n_turbines"] == 2
    is_staged = cycle_name in ("frsc", "orsc", "ffsc")

    # --- electric pump-fed: battery + motor in place of the turbine ----------
    if cycle_name == "electric_pump":
        bat = cyc.get("battery_mass_kg", 0.0)
        mot = cyc.get("motor_mass_kg", 0.0)
        kwe = cyc.get("electrical_power_w", 0.0) / 1e3
        kwh = cyc.get("electrical_energy_j", 0.0) / 3.6e6
        _box(ax, _MID, 5.3, 4.0, 2.0,
             f"BATTERY + MOTOR\n{bat:.0f} kg battery ({kwh:,.1f} kWh) + {mot:.0f} kg motor\n"
             f"{kwe:,.0f} kW electrical - drives both pumps\nno turbine - no bleed",
             _WARN, fontsize=7)
        _flow(ax, (_MID - 1.4, 5.7), (_XF + 0.2, 8.0), style=_SHAFT)
        _flow(ax, (_MID + 1.4, 5.7), (_XO - 0.2, 8.0), style=_SHAFT)
        _box(ax, _MID, 1.9, 5.6, 1.5,
             f"MAIN CHAMBER\nPc {pc_mpa:.1f} MPa - {result['thrust_vac_n']/1e3:,.0f} kN vac - "
             f"Isp = chamber Isp", _NEUTRAL, fontsize=8)
        _flow(ax, (_XF - 0.7, 7.9), (_XF + 1.0, 2.65), "fuel")
        _flow(ax, (_XO + 0.6, 7.9), (_XO - 1.7, 2.65), "ox")
        ax.set_title(
            f"Turbopump - electric pump-fed - {s['arrangement'].replace('_', ' ')} - "
            f"0 turbines - battery+motor ~{bat + mot:.0f} kg - "
            f"{'FEASIBLE' if s['feasible'] else 'MARGINAL (see Checklist)'}", fontsize=8.5)
        return

    turb_txt = (f"{'FUEL ' if two_turb else ''}TURBINE\n{staging_short} - eta {s['eta_turbine']:.2f}\n"
                f"{turb['u_pitchline_m_s']:.0f} m/s - U/C0 {turb['u_over_c0']:.2f}\n"
                f"gas inlet {s['turbine_inlet_k']:.0f} K") if turb else "TURBINE\n(sizing n/a)"
    _box(ax, _XF + 1.1, 5.1, 3.3, 1.9, turb_txt, status, fontsize=7)

    if s["arrangement"] == "geared":
        _box(ax, _MID + 1.9, 5.1, 1.8, 1.1, "GEARBOX\n(ox pump)", _WARN, fontsize=6.8)
        _flow(ax, (_XF + 2.75, 5.1), (_MID + 1.0, 5.1), style=_SHAFT)
        _flow(ax, (_MID + 2.8, 5.4), (_XO - 0.4, 8.0), style=_SHAFT)
        _flow(ax, (_XF - 0.7, 8.0), (_XF + 0.1, 5.9), style=_SHAFT)
    elif two_turb and ox_turb:
        ot_txt = (f"OX TURBINE\n{staging_short}\n{ox_turb['u_pitchline_m_s']:.0f} m/s - "
                  f"U/C0 {ox_turb['u_over_c0']:.2f}")
        _box(ax, _XO, 5.1, 3.2, 1.7, ot_txt, status, fontsize=7)
        _flow(ax, (_XO, 5.95), (_XO, 7.95), style=_SHAFT)
        _flow(ax, (_XF + 0.5, 6.05), (_XF - 0.3, 7.95), style=_SHAFT)
    else:  # single_shaft, one turbine feeding both pumps
        _flow(ax, (_XF, 5.95), (_XF, 7.95), style=_SHAFT)
        _flow(ax, (_XF + 2.7, 5.4), (_XO - 0.3, 8.0), style=_SHAFT)

    pbf_pct = cyc.get("preburner_flow_fraction", cyc.get("gg_flow_fraction", 0.0)) * 100.0
    gg_frac = cyc.get("gg_flow_fraction", 0.0) * 100.0
    gg_mdot = cyc.get("gg_mdot_kgs", 0.0)
    if cycle_name == "expander":
        _box(ax, _MID + 0.3, 8.9, 2.9, 1.4, "REGEN JACKET\nfuel-cooled wall\nheat drives turbine",
             _NEUTRAL, fontsize=6.6)
        _flow(ax, (_XF + 1.6, 8.9), (_MID - 1.1, 8.9), "fuel")
        _flow(ax, (_MID + 0.3, 8.2), (_XF + 1.6, 6.05), "warm H$_2$")
        _flow(ax, (_XF + 1.1, 4.15), (_MID - 0.6, 4.0), "turbine exhaust -> injector")
    elif cycle_name == "tap_off":
        tin = s["turbine_inlet_k"]
        _box(ax, _MID, 7.0, 3.2, 1.2,
             f"CHAMBER TAP-OFF\nfilm-cooled ~{tin:.0f} K\nbleed {gg_frac:.1f}% - {gg_mdot:.1f} kg/s",
             _WARN, fontsize=6.6)
        _flow(ax, (_MID + 1.4, 2.35), (_MID + 0.9, 6.4), "tapped gas\nnear injector face")
        _flow(ax, (_MID - 0.3, 6.4), (_XF + 1.9, 6.05), "hot gas")
        _exhaust_box(ax, result)
    elif cycle_name == "ffsc":
        _box(ax, _XF + 1.1, 7.0, 2.8, 1.0,
             f"FUEL-RICH\nPREBURNER ~{pbf_pct:.0f}% flow", _WARN, fontsize=6.2)
        _box(ax, _XO, 7.0, 2.8, 1.0, "OX-RICH\nPREBURNER (ox unit)", _OXRICH, fontsize=6.2)
        _flow(ax, (_XF + 1.1, 6.5), (_XF + 1.1, 6.05), "hot gas")
        _flow(ax, (_XO, 6.5), (_XO, 5.95), "hot O$_2$-rich gas")
        _flow(ax, (_MID, 4.05), (_MID, 2.65), "both preburner exhausts -> injector (no dump)")
        ax.text(_MID, 9.9, "FFSC: both propellants fully preburned - both pumps boosted > 2x Pc",
                ha="center", fontsize=6.0, color="#a05a00")
    elif cycle_name in ("frsc", "orsc"):
        ox_rich = cycle_name == "orsc"
        label = "OX-RICH PREBURNER" if ox_rich else "FUEL-RICH PREBURNER"
        boosted = "ox pump boosted" if ox_rich else "fuel pump boosted"
        _box(ax, _MID, 7.0, 3.2, 1.3,
             f"{label}\n~{pbf_pct:.0f}% of total flow - {gg_mdot:.1f} kg/s\n{boosted} > 2x Pc",
             _OXRICH if ox_rich else _WARN, fontsize=6.4)
        _flow(ax, (_XF + 1.6, 8.3), (_MID - 1.2, 7.4), "fuel")
        _flow(ax, (_XO - 1.6, 8.3), (_MID + 1.2, 7.4), "ox")
        _flow(ax, (_MID - 0.3, 6.35), (_XF + 1.9, 6.05), "hot gas")
        _flow(ax, (_XF + 1.1, 4.15), (_MID - 0.6, 4.0), "preburner exhaust -> injector (no dump)")
        boost_x = _XO if ox_rich else _XF
        ax.text(boost_x, 7.95, "^ boosted", ha="center", fontsize=6.0, color="#a05a00")
    else:  # gas_generator
        _box(ax, _MID, 7.0, 3.0, 1.2, f"GAS GENERATOR\nbleed {gg_frac:.1f}% - {gg_mdot:.1f} kg/s",
             _NEUTRAL, fontsize=6.8)
        _flow(ax, (_XF + 1.6, 8.3), (_MID - 1.2, 7.3), "fuel")
        _flow(ax, (_XO - 1.6, 8.3), (_MID + 1.2, 7.3), "ox")
        _flow(ax, (_MID - 0.3, 6.4), (_XF + 1.9, 6.05), "hot gas")
        _exhaust_box(ax, result)

    _box(ax, _MID, 1.6, 5.6, 1.5,
         f"MAIN CHAMBER\nPc {pc_mpa:.1f} MPa - {result['thrust_vac_n']/1e3:,.0f} kN vac",
         _NEUTRAL, fontsize=8)
    _flow(ax, (_XF - 0.7, 7.9), (_XF + 1.0, 2.35))
    _flow(ax, (_XO + 0.6, 7.9), (_XO - 1.7, 2.35))

    ax.set_title(
        f"Turbopump - {cycle_name.replace('_', ' ')} - {s['arrangement'].replace('_', ' ')} - "
        f"{s['n_turbines']} turbine(s) - overall eta {s['eta_overall']:.2f} - "
        f"~{tp_mass:,.0f} kg - {'FEASIBLE' if s['feasible'] else 'MARGINAL (see Checklist)'}",
        fontsize=8.5)


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from ..physics.design import EngineDesign

    cases = {
        "gg_single": dict(propellant_pair="LOX/RP-1", mixture_ratio=2.27, chamber_pressure_pa=7.0e6,
                          expansion_ratio=16, nozzle_type="bell", cycle="gas_generator",
                          target_vac_thrust_n=7_770_000.0),
        "gg_dual": dict(propellant_pair="LOX/LH2", mixture_ratio=5.5, chamber_pressure_pa=5.4e6,
                        expansion_ratio=27.5, nozzle_type="bell", cycle="gas_generator",
                        target_vac_thrust_n=1_023_000.0),
        "frsc": dict(propellant_pair="LOX/LH2", mixture_ratio=6.0, chamber_pressure_pa=18.0e6,
                     expansion_ratio=69, nozzle_type="bell", cycle="frsc",
                     turbopump_material_key="powder_met_superalloy", target_vac_thrust_n=2_000_000.0),
        "orsc": dict(propellant_pair="LOX/RP-1", mixture_ratio=2.72, chamber_pressure_pa=25.5e6,
                     expansion_ratio=36, nozzle_type="bell", cycle="orsc",
                     turbopump_material_key="monel_k500", target_vac_thrust_n=4_150_000.0),
        "ffsc": dict(propellant_pair="LOX/LH2", mixture_ratio=3.6, chamber_pressure_pa=30.0e6,
                     expansion_ratio=40, nozzle_type="bell", cycle="ffsc",
                     turbopump_material_key="powder_met_superalloy", target_vac_thrust_n=2_200_000.0),
        "tap_off": dict(propellant_pair="LOX/LH2", mixture_ratio=5.5, chamber_pressure_pa=9.22e6,
                        expansion_ratio=92, nozzle_type="bell", cycle="tap_off",
                        target_vac_thrust_n=1_307_000.0),
        "electric_pump": dict(propellant_pair="LOX/RP-1", mixture_ratio=2.5, chamber_pressure_pa=12.0e6,
                              expansion_ratio=10, nozzle_type="bell", cycle="electric_pump",
                              material_key="inconel_718", target_vac_thrust_n=26_000.0),
        "expander_geared": dict(propellant_pair="LOX/LH2", mixture_ratio=5.5, chamber_pressure_pa=3.2e6,
                                expansion_ratio=61, nozzle_type="bell", cycle="expander",
                                target_vac_thrust_n=73_000.0),
        "pressure_fed": dict(propellant_pair="N2O4/MMH", mixture_ratio=1.9, chamber_pressure_pa=1.0e6,
                             expansion_ratio=60, nozzle_type="bell", cycle="pressure_fed",
                             material_key="ablative_phenolic", target_vac_thrust_n=40_000.0),
    }
    for tag, kw in cases.items():
        result = EngineDesign(**kw).compute()
        fig, ax = plt.subplots(figsize=(7.5, 7))
        draw_turbopump_diagram(ax, result)
        out = f"/tmp/engine_designer_turbopump_{tag}.png"
        fig.savefig(out, dpi=95)
        plt.close(fig)
        print(f"turbopump_diagram.py rendered {tag} -> {out}")
    print("turbopump_diagram.py headless smoke test OK")
