"""Turbopump sizing + plumbing stage of _compute_pass.

Split verbatim out of the former single-file design.py; a value shared
between stages lives on the PassState `s` (see design/state.py)."""
import numpy as np

from .. import (cycles, geometry3d, manifold, plumbing, turbopump_sizing)
from .constants import (
    EXPANDER_TURBINE_PR,
)
from .checklist import _check


def turbopump_and_plumbing(self, s):
    """Turbopump preliminary sizing and procedural plumbing runs (computed line loss)."""
    # --- turbopump preliminary sizing (physics/turbopump_sizing.py) ---
    # Rotor speed / tip speed / stage count / turbine count + shaft arrangement,
    # the DERIVED pump/turbine efficiencies, the physical envelope, and the
    # assembly mass. NOTE: the mass that feeds the dry rollup (tp_sizing
    # "mass_kg") is the [SP-8107 Table I] specific-power trend on shaft power
    # (turbopump_sizing.turbopump_mass_kg); the envelope-volume x density
    # "mass_geometry_kg" is a cross-check only, used to rescale the rendered
    # envelope. The dry-mass modifier is EXACTLY 1.0 for the auto architecture.
    s.tp_sizing = None
    if s.cyc["has_turbopump"]:
        s.drive_gas = s.cyc.get("drive_gas")   # set by TAP_OFF / FRSC / ORSC / FFSC branches
        if self.cycle in cycles.STAGED_CYCLES:
            turbine_inlet_k = s.drive_gas["tin_k"]
            turbine_mdot = max(s.cyc["gg_mdot_kgs"], 1e-6)   # the solved preburner/turbine flow
            turbine_pr = s.cyc["turbine_pressure_ratio"]      # solved (staged_combustion.py)
        elif self.cycle == cycles.TAP_OFF:
            turbine_inlet_k = s.drive_gas["tin_k"]
            turbine_mdot = max(s.cyc["gg_mdot_kgs"], 1e-6)
            turbine_pr = s.cyc["turbine_pressure_ratio"]      # exhaust back pressure (turbine_exhaust.py)
        elif self.cycle == cycles.EXPANDER:
            turbine_inlet_k = 250.0  # heated-hydrogen expander turbine, far below combustion
            turbine_mdot = max(s.cyc["turbopump"]["mdot_fuel_kgs"], 1e-6)
            turbine_pr = EXPANDER_TURBINE_PR
        elif self.cycle == cycles.ELECTRIC_PUMP:
            turbine_inlet_k = 0.0     # no turbine
            turbine_mdot = 1e-6
            turbine_pr = 0.0
        else:  # GAS_GENERATOR
            turbine_inlet_k = s.gg_gas["tin_k"]
            turbine_mdot = max(s.cyc["gg_mdot_kgs"], 1e-6)
            turbine_pr = s.cyc["turbine_pressure_ratio"]      # exhaust back pressure (turbine_exhaust.py)
        # Actual specific work the turbine delivers = shaft power / turbine mass flow
        # (what pitchline sizing needs). Zero for electric pump-fed (no turbine).
        turbine_specific_work = (0.0 if self.cycle == cycles.ELECTRIC_PUMP
                                 else s.cyc["turbopump"]["power_total_w"] / turbine_mdot)
        s.tp_sizing = turbopump_sizing.size_turbopump(
            s.cyc, s.dp_fuel, s.dp_ox, s.rho_fuel, s.rho_ox, self.propellant_pair,
            self.target_vac_thrust_n, self.cycle,
            self.turbopump_arrangement, self.turbine_staging, self.turbopump_material_key,
            turbine_inlet_k=turbine_inlet_k, turbine_specific_work_j_kg=turbine_specific_work,
            turbine_pressure_ratio=turbine_pr, build_quality=s.build_quality,
            pump_stages_fuel=self.pump_stages_fuel, pump_stages_ox=self.pump_stages_ox,
            eta_pump_fuel_final=s.eta_pf, eta_pump_ox_final=s.eta_po, eta_turbine_final=s.eta_turb,
            motor_mass_kg=s.cyc.get("motor_mass_kg", 0.0),   # electric pump-fed: motor body in the envelope
            bearing_material_key=self.bearing_material_key,
            enforce_suction_limit=self.enforce_suction_limit, **s._suction_kw)
        s.turbopump_mass_kg = s.tp_sizing["mass_kg"] * s.tp_sizing["mass_modifier"]
        tp_detail = "; ".join(s.tp_sizing["warnings"])
        _check(s.checklist, s.warnings, "turbopump", "Turbopump sizing / material feasibility",
               not s.tp_sizing["warnings"],
               f"[turbopump] {tp_detail}",
               f"OK - {s.tp_sizing['arrangement'].replace('_', ' ')}, {s.tp_sizing['n_turbines']} "
               f"turbine(s), peak tip speed within {s.tp_sizing['material_display']} limit")

    # Procedural plumbing runs (physics/plumbing.py) rooted on the rings
    # sized above - resolved here for MASS, advisories and (for a run
    # connected to a turbopump port) the feed-line pressure loss; the render
    # re-resolves with its own wall-snapped ring radius (gui/mesh_builder.
    # build_plumbing_pieces), which only shifts where the pipe starts, not
    # its stored per-diameter lengths - so the mass here uses the physics
    # ring's nominal major_radius_m/outer_radius_m and matches the render
    # to within the ring-tube-radius buried stub (a connected run's auto
    # legs are re-solved there too and still land on the port). A run whose
    # host ring doesn't exist for this design is skipped with an advisory.
    # Runs after turbopump sizing: the pump ports come from its bodies.
    _plumbing_hooks = {"manifold_result": s.manifold_result,
                       "jacket_manifold_result": s.jacket_manifold_result}
    s.turbopump_ports = None
    if s.tp_sizing and s.tp_sizing.get("bodies"):
        _fuel_primary = plumbing.hook_for_host(_plumbing_hooks, "jacket_inlet") or \
            plumbing.hook_for_host(_plumbing_hooks, "fuel")
        _ox_hook = plumbing.hook_for_host(_plumbing_hooks, "ox")
        _dis = {"fuel_pump": _fuel_primary["inner_diameter_m"] if _fuel_primary else 0.0,
                "ox_pump": _ox_hook["inner_diameter_m"] if _ox_hook else 0.0}
        s.turbopump_ports = geometry3d.turbopump_ports(
            s.tp_sizing["bodies"],
            geometry3d.turbopump_origin_xyz(float(np.max(s.xs)), float(np.max(s.rs)),
                                            s.tp_sizing["assembly_od_m"]),
            s.tp_sizing, _dis)
    s.line_loss_computed = {"fuel": None, "ox": None}
    s.plumbing_results = []
    s.plumbing_mass_kg = 0.0
    s.plumbing_total_length_m = 0.0
    for _run_dict in (self.plumbing_runs or []):
        _run = plumbing.run_from_dict(_run_dict)
        _hook = plumbing.hook_for_host(_plumbing_hooks, _run.host)
        if _hook is None:
            _check(s.checklist, s.warnings, "plumbing", f"Plumbing run on '{_run.host}'", False,
                   f"Plumbing run rooted on '{_run.host}' has no such manifold ring in this "
                   f"design (e.g. jacket_return only exists under the F-1 split / J-2 layouts) - "
                   f"it is neither drawn nor counted.")
            continue
        _pump = plumbing.HOST_PUMP.get(_run.host, "fuel_pump")
        _port = None
        if _run.connect_to_pump:
            _port = (s.turbopump_ports or {}).get(_pump, {}).get("discharge")
            if _port is None:
                _check(s.checklist, s.warnings, "plumbing", f"Plumbing run on '{_run.host}' pump link",
                       False, f"Run on '{_run.host}' is set to connect to the "
                       f"{_pump.replace('_', ' ')}, but this design has no such turbopump "
                       f"port (pressure-fed?) - drawn with a free end, flat line loss kept.", "")
            elif _run.host == "fuel" and plumbing.hook_for_host(_plumbing_hooks, "jacket_inlet"):
                _check(s.checklist, s.warnings, "plumbing", "Fuel ring fed straight from the pump",
                       False, "The fuel injector ring is connected straight to the fuel pump on "
                       "a regeneratively cooled chamber - coolant normally passes through the "
                       "jacket (jacket_inlet ring) first. Allowed; check it is intended.", "")
        _res = plumbing.resolve_run(_run, _hook, _hook["major_radius_m"],
                                    manifold.ring_outer_radius_at(_hook, _run.attach_angle_deg),
                                    supercritical=(s._fuel_lh2 and _run.host != "ox"), port=_port)
        _m_total, _m_pipe, _m_flange = plumbing.plumbing_mass_kg(_hook, _res)
        s.plumbing_mass_kg += _m_total
        s.plumbing_total_length_m += _res["total_length_m"]
        _loss_pa, _loss_parts = plumbing.run_pressure_loss_pa(
            _res, _hook, plumbing.liquid_viscosity_pa_s(self.propellant_pair, _run.host))
        if _res["closes_on_port"]:
            # valve allowance at the run's slowest (largest-bore) pipe -
            # where a main valve would sit
            _v = min(_res["pipe_velocities_ms"])
            _leg_loss = _loss_pa + (plumbing.VALVE_AND_UNMODELED_K * 0.5
                                    * plumbing.feed_density_kg_m3(_hook) * _v * _v)
            _leg = "ox" if _pump == "ox_pump" else "fuel"
            s.line_loss_computed[_leg] = max(s.line_loss_computed[_leg] or 0.0, _leg_loss)
        s.plumbing_results.append({"host": _run.host, "role": _run.role, "n_pipes": len(_run.pipes),
                                 "pipe_dias_m": [2.0 * r for r in _res["pipe_radii_m"]],
                                 "pipe_velocities_ms": list(_res["pipe_velocities_ms"]),
                                 "total_length_m": _res["total_length_m"],
                                 "mass_kg": _m_total, "pipe_mass_kg": _m_pipe,
                                 "flange_mass_kg": _m_flange,
                                 "n_flanges": sum(1 for j in _res["joint_frames"] if j["flange"]),
                                 "connected_pump": _pump if _res["closes_on_port"] else None,
                                 "pressure_loss_pa": _loss_pa,
                                 "pressure_loss_parts_pa": _loss_parts,
                                 "advisories": list(_res["advisories"])})
        _check(s.checklist, s.warnings, "plumbing",
               f"Plumbing run on '{_run.host}' geometry ({len(_run.pipes)} pipes)",
               not _res["advisories"], " ".join(_res["advisories"]),
               f"OK - {_res['total_length_m']:.2f} m, {_m_total:.1f} kg"
               + (f", -> {_pump.replace('_', ' ')}, line loss {_loss_pa / 1e3:.0f} kPa"
                  if _res["closes_on_port"] else ""))
