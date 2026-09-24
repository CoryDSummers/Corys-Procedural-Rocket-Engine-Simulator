"""Chamber-detail stage of _compute_pass.

Split verbatim out of the former single-file design.py; a value shared
between stages lives on the PassState `s` (see design/state.py)."""
import numpy as np

from .. import (cycles, expander, geometry, nozzle_shapes, throttle, turbopump_sizing)
from .constants import (
    PA_SEA_LEVEL,
    TANK_HEAD_PA,
    EXPANDER_TURBINE_PR,
    SEPARATION_K,
)
from .checklist import _check


def contour(self, s):
    """Chamber geometry + the real nozzle contour. Runs right after the nozzle-
    performance stage: it depends only on the chamber mass flow and c* (known
    there), not on the cycle - which is what lets the unified thermal solve run
    on the REAL contour before the pump chain needs the jacket dP (2026-09-23
    audit; previously the pumps used a cheap conical pre-march)."""
    s.conv_half_angle = self.convergent_half_angle_deg
    s.geo = geometry.chamber_geometry(s.mdot, s.cstar, self.chamber_pressure_pa,
                                     self.expansion_ratio, self.lstar_m, self.contraction_ratio,
                                     s.conv_half_angle, self.chamber_wall_fillet_r_over_rt,
                                     self.chamber_sizing_method, s.chamber_sizing_rt_s, s.tc, s.m_molar)
    _check(s.checklist, s.warnings, "chamber geometry",
           "L* sufficient for a cylindrical section at this contraction ratio",
           not s.geo["cylindrical_volume_clamped"],
           f"L* {self.lstar_m:.2f} m is too small for a cylindrical chamber "
           f"section at contraction ratio {self.contraction_ratio:.2f} - the "
           f"convergent cone alone already accounts for that much volume. "
           f"Chamber length clamped to the convergent section only.")
    _check(s.checklist, s.warnings, "chamber geometry", "Convergent half-angle within 20-45 deg",
           20.0 <= s.conv_half_angle <= 45.0,
           f"Convergent-cone half-angle {s.conv_half_angle:.0f} deg is outside the "
           f"[Huzel 4.3] 20-45 deg range.")
    xs_conv, rs_conv, x_throat, conv_len = geometry.convergent_profile(
        s.geo["chamber_dia_m"], s.geo["throat_dia_m"], s.geo["chamber_length_m"], s.conv_half_angle,
        self.chamber_wall_fillet_r_over_rt)
    if self.nozzle_type == "bell":
        div_len = nozzle_shapes.bell_length(s.geo["throat_dia_m"] / 2.0, s.geo["exit_dia_m"] / 2.0,
                                             self.bell_percent_length)
        xs_div, rs_div, _ = nozzle_shapes.bell_profile_points(
            s.geo["throat_dia_m"] / 2.0, s.geo["exit_dia_m"] / 2.0, x_throat,
            s.theta_n_deg, s.theta_e_deg, div_len, n=30)
        s.xs = np.concatenate([xs_conv, xs_div[1:]])  # skip duplicate throat point
        s.rs = np.concatenate([rs_conv, rs_div[1:]])
        s.profile_meta = {"convergent_length_m": conv_len, "divergent_length_m": div_len,
                         "total_length_m": x_throat + div_len,
                         "theta_n_deg": s.theta_n_deg, "theta_e_deg": s.theta_e_deg}
    else:
        s.xs, s.rs, s.profile_meta = geometry.nozzle_profile(
            s.geo["chamber_dia_m"], s.geo["throat_dia_m"], s.geo["exit_dia_m"], s.geo["chamber_length_m"],
            s.conv_half_angle, self.nozzle_half_angle_deg,
            self.chamber_wall_fillet_r_over_rt,
        )


def chamber_detail(self, s):
    """Chamber-detail checks C1/C2: finite-contraction-ratio loss, stay time, L/D."""
    # C1 - finite-contraction-ratio chamber pressure loss.
    _cf_loss_pct = s.chamber_flow["pc_loss_fraction"] * 100.0
    _check(s.checklist, s.warnings, "chamber geometry", "Contraction ratio performance margin",
           self.contraction_ratio >= 1.6,
           f"Contraction ratio {self.contraction_ratio:.2f} is tight: the chamber gas reaches "
           f"M~{s.chamber_flow['mach']:.2f}, so the injector-end stagnation pressure sits "
           f"~{_cf_loss_pct:.0f}% above the nozzle Pc [Sutton 8.2]. The pump/tank must "
           f"supply that higher pressure"
           + (" (being modelled - apply_chamber_pressure_loss on)."
              if self.apply_chamber_pressure_loss
              else " (not fed into feed pressure here - enable apply_chamber_pressure_loss)."),
           f"OK - injector-end Pc ~{s.chamber_flow['injector_end_pressure_ratio']:.3f}x nozzle Pc")

    # C2 - real stay time and chamber L/D.
    _rho_gas = (self.chamber_pressure_pa * s.m_molar / (8314.462 * s.tc)) if s.tc > 0 else 0.0
    s.stay_time_s = (s.geo["chamber_volume_m3"] * _rho_gas / s.mdot) if s.mdot > 0 and _rho_gas > 0 else 0.0
    s.chamber_l_over_d = (s.geo["chamber_length_m"] / s.geo["chamber_dia_m"]
                        if s.geo["chamber_dia_m"] > 0 else 0.0)
    _check(s.checklist, s.warnings, "chamber geometry", "Gas stay time within 1-40 ms",
           0.001 <= s.stay_time_s <= 0.040 or s.stay_time_s == 0.0,
           f"Combustion-gas stay time {s.stay_time_s*1e3:.1f} ms is outside the typical "
           f"1-40 ms band [Sutton 8.10] - {'too short, combustion may not complete' if s.stay_time_s < 0.001 else 'a very large chamber volume for this flow'}.",
           f"OK - {s.stay_time_s*1e3:.1f} ms")
    _check(s.checklist, s.warnings, "chamber geometry", "Chamber cylindrical L/D reasonable",
           0.3 <= s.chamber_l_over_d <= 2.5 or s.chamber_l_over_d == 0.0,
           f"Chamber cylindrical L/D {s.chamber_l_over_d:.2f} is "
           f"{'long/narrow (non-isentropic pressure loss, injector-hole crowding)' if s.chamber_l_over_d > 2.5 else 'short/wide (atomization zone eats the volume, mixing length too short)'} "
           f"[claude_lit topic 04].",
           f"OK - L/D {s.chamber_l_over_d:.2f}")

    if self.cycle == cycles.EXPANDER:
        s.eta_pf, s.eta_po, s.eta_turb = turbopump_sizing.derive_expander_efficiencies(
            s.mdot, self.mixture_ratio, s.dp_fuel, s.dp_ox, s.rho_fuel, s.rho_ox,
            self.turbopump_material_key, EXPANDER_TURBINE_PR, s.build_quality,
            pump_stages_fuel=self.pump_stages_fuel, pump_stages_ox=self.pump_stages_ox,
            eta_pump_fuel_override=self.eta_pump_fuel, eta_pump_ox_override=self.eta_pump_ox,
            enforce_suction_limit=self.enforce_suction_limit, **s._suction_kw)
        s.cyc = expander.expander_result(
            self.propellant_pair, s.mdot, self.mixture_ratio, self.chamber_pressure_pa,
            s.dp_fuel, s.dp_ox, s.rho_fuel, s.rho_ox, s.eta_pf, s.eta_po,
            self.pump_specific_power_w_kg,
            s.xs, s.rs, s.geo["throat_dia_m"], s.cstar, s.mu_gas, s.cp_gas, s.pr_gas, s.t_aw_chamber_k,
            cutoff_area_ratio=s.regen_cut_eps, eta_turbine=s.eta_turb,
            # The turbine is driven by the heat the regen jacket actually picks
            # up in the unified thermal solve - film-corrected, method-aware
            # (0 without a regen chamber), bypass- and dump-aware - so it can
            # no longer exceed the reported wall heat (audit W9).
            heat_w=s.thermal["wall_heat_regen_w"], coolant_model=s.thermal["coolant_model"],
            t_inlet_k=s.coolant_inlet_k,
        )
        s.cyc["pump_discharge_fuel_pa"] = s.dp_fuel + TANK_HEAD_PA
        s.cyc["pump_discharge_ox_pa"] = s.dp_ox + TANK_HEAD_PA
        s.cyc["turbine_pressure_ratio"] = EXPANDER_TURBINE_PR
        _check(s.checklist, s.warnings, "expander", "Expander turbine power feasibility",
               s.cyc["feasibility_margin"] >= 1.0,
               f"Expander cycle is NOT feasible at this design point: available turbine "
               f"power ({s.cyc['available_turbine_power_w']/1e3:.1f} kW) is only "
               f"{s.cyc['feasibility_margin']*100:.0f}% of what the turbopump needs "
               f"({s.cyc['required_turbine_power_w']/1e3:.1f} kW). Lower Pc/thrust, use a "
               f"larger cooled nozzle area, or (most effectively) use LOX/LH2 - "
               f"real expander-cycle engines (RL10, Vinci) are limited to modest "
               f"thrust/Pc for exactly this reason.",
               f"OK - {s.cyc['feasibility_margin']*100:.0f}% margin")
        _check(s.checklist, s.warnings, "expander",
               "Expander propellant-pair realism (LOX/LH2 only)",
               self.propellant_pair == "LOX/LH2",
               "Expander cycle: no real engine has ever flown this propellant with this "
               "cycle - LH2's heat capacity and coking resistance are specifically why "
               "RL10/Vinci-class engines are LH2-only. A 'feasible' margin here reflects "
               "this tool's simplified heat-budget proxy (it doesn't model coking chemistry "
               "directly), not confirmation the combination is realistic.")

    throttle_grid = np.arange(max(self.throttle_floor, 0.05), 1.001, 0.02)
    s.rows = throttle.throttle_sweep(self.chamber_pressure_pa, s.pe_pc, PA_SEA_LEVEL,
                                    s.dp_injector, throttle_grid, SEPARATION_K)
    s.onset = throttle.separation_onset_throttle(s.rows)
    s.inj_ok = throttle.injector_stiffness_ok(s.rows, self.throttle_floor, s.injector.min_stable_dp_ratio)
