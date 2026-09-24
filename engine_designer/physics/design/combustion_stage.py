"""Combustion + nozzle performance stages of EngineDesign._compute_pass.

Split verbatim out of the former single-file design.py; a value shared
between stages lives on the PassState `s` (see design/state.py)."""
from .. import (combustion, combustion_stability, cooling, cycles, injectors,
                nozzle_shapes, staged_combustion, isentropic as iso)
from .constants import (
    G0,
    PA_SEA_LEVEL,
    LINE_LOSS_PA,
    ETA_CSTAR_CEILING,
    FILM_COOLING_ETA_CSTAR_PENALTY,
)
from .checklist import _check


def combustion_setup(self, s):
    """Warnings/line-loss setup, combustion state, c* efficiency (incl. the film c* penalty), gas transport properties, chamber sizing method."""
    s.warnings = []
    s.checklist = []
    # Feed-line loss per pump leg (pump discharge -> ring): the flat
    # LINE_LOSS_PA unless a previous pass computed it from a connected run.
    s._llo = s.line_loss_override or {}
    s.line_loss_fuel_pa = s._llo["fuel"] if s._llo.get("fuel") is not None else LINE_LOSS_PA
    s.line_loss_ox_pa = s._llo["ox"] if s._llo.get("ox") is not None else LINE_LOSS_PA

    mr_lo, mr_hi = combustion.mr_bounds(self.propellant_pair)
    _check(s.checklist, s.warnings, "propellant/cycle", "Mixture ratio within table range",
           mr_lo <= self.mixture_ratio <= mr_hi,
           f"Mixture ratio {self.mixture_ratio:.2f} is outside the "
           f"literature-anchored table range [{mr_lo}, {mr_hi}] for "
           f"{self.propellant_pair} - the tables are CLAMPED at that edge, so combustion "
           f"numbers are the edge value, not extrapolated.")

    s.tc, s.gamma, s.m_molar = combustion.combustion_state(self.propellant_pair, self.mixture_ratio)
    s.rho_fuel, s.rho_ox = combustion.propellant_densities(self.propellant_pair)

    mach = iso.mach_from_area_ratio(self.expansion_ratio, s.gamma)
    s.pe_pc = iso.pe_over_pc(mach, s.gamma)
    s.pe_pa = s.pe_pc * self.chamber_pressure_pa

    s.injector = injectors.INJECTORS[self.injector_type]

    # Combustion completeness vs. L* (residence time = L*/c*_ideal, using the IDEAL
    # c* - before any efficiency multiplier - specifically to avoid a circular
    # dependency: completeness feeds eta_cstar, so it can't also depend on the
    # eta_cstar-scaled c*). See combustion.completeness_factor's docstring.
    cstar_ideal = iso.c_star(s.tc, s.gamma, s.m_molar, eta_cstar=1.0)
    s.residence_time_s = self.lstar_m / cstar_ideal
    s.completeness = combustion.completeness_factor(
        self.lstar_m, self.propellant_pair, s.injector.atomization_time_modifier)
    required_length_m = combustion.L_MID_BASE[self.propellant_pair] * s.injector.atomization_time_modifier
    s.required_time_s = required_length_m / cstar_ideal

    s.eta_cstar = (combustion.DEFAULT_ETA_CSTAR[self.propellant_pair]
                 * s.injector.eta_cstar_multiplier * s.completeness)
    if self.cycle in cycles.STAGED_CYCLES:
        s.eta_cstar *= staged_combustion.STAGED_ETA_CSTAR_PENALTY[self.cycle]
    s.film_fraction = max(0.0, self.film_cooling_fraction)
    if s.film_fraction > 0.0:
        # film_cooling_fraction is a fraction of FUEL flow; its share of the
        # TOTAL flow (the c* basis) is f/(1+MR) - the old code applied it to
        # total flow, overstating the curtain's cost (1+MR)x vs the nozzle-slot
        # film and dump bleed, which were already on this basis (audit W3).
        s.eta_cstar *= (1.0 - FILM_COOLING_ETA_CSTAR_PENALTY * s.film_fraction
                        / (1.0 + self.mixture_ratio))
    if self.injector_baffles:
        # Baffle blades span the injector face and consume film coolant -
        # a small c* hit [claude_lit/topics/14].
        s.eta_cstar *= (1.0 - combustion_stability.BAFFLE_CSTAR_PENALTY)
    s.eta_cstar = min(s.eta_cstar, ETA_CSTAR_CEILING)
    s.cstar = iso.c_star(s.tc, s.gamma, s.m_molar, s.eta_cstar)

    # Combustion-gas transport properties + recovery temp (physics/combustion.py
    # derives these, not tabulated) - computed this early because the
    # regen-jacket pre-march below (for the pump-feed jacket dP estimate) now
    # needs them for the same computed-absolute Bartz flux the authoritative
    # cooling model further down uses; both must agree.
    # 2026-09-23: from the chemical-equilibrium tables at the ACTUAL (MR, Pc) -
    # frozen cp / viscosity / Prandtl, and the equilibrium Tc as the heat-
    # transfer stagnation temperature (see heat_transfer_gas_properties).
    s.ht_gas = combustion.heat_transfer_gas_properties(
        self.propellant_pair, self.mixture_ratio, self.chamber_pressure_pa)
    s.mu_gas = s.ht_gas["mu_pa_s"]
    s.pr_gas = s.ht_gas["prandtl"]
    s.cp_gas = s.ht_gas["cp_j_kgk"]
    s.tc_ht = s.ht_gas["tc_k"]
    s.gamma_ht = s.ht_gas["gamma"]
    # chamber (M ~ 0) recovery temperature = the stagnation temperature; the
    # per-station T_aw(M) lives in the thermal solve.
    s.t_aw_chamber_k = s.tc_ht

    # Chamber sizing method (physics/geometry.chamber_geometry). "lstar" is the
    # historical path. "residence_time" sizes Vc from a target combustion stay
    # time; chamber_residence_time_ms == 0 falls back to the stay time implied
    # by this pair's [Huzel Table 4-1] L* default, which reproduces the L*
    # sizing exactly (combustion.residence_time_from_lstar_s).
    s.chamber_sizing_rt_s = 0.0
    if self.chamber_sizing_method == "residence_time":
        s.chamber_sizing_rt_s = (
            self.chamber_residence_time_ms / 1000.0 if self.chamber_residence_time_ms > 0.0
            else combustion.residence_time_from_lstar_s(
                combustion.l_star_default_for_pair(self.propellant_pair), s.tc, s.cstar, s.m_molar))


def nozzle_performance(self, s):
    """Nozzle contour + divergence efficiency, Cf, chamber Isp, mass flow."""
    # --- nozzle contour + divergence efficiency: conical vs bell ---
    # lam_relative scores the chosen nozzle AGAINST an 80%-bell reference at this
    # same expansion ratio, matching what combustion.DEFAULT_ETA_CSTAR's calibration
    # (physics/validate.py) implicitly assumes - see nozzle_shapes.reference_lambda's
    # docstring. Applying the raw lam directly here would double-count the divergence
    # loss the calibration already absorbed (this was the LMDE-comparison bug).
    s.theta_n_deg = s.theta_e_deg = None
    if self.nozzle_type == "bell":
        s.theta_n_deg, s.theta_e_deg = nozzle_shapes.bell_angles(self.expansion_ratio, self.bell_percent_length)
        s.lam = nozzle_shapes.bell_divergence_efficiency(s.theta_e_deg)
    elif self.nozzle_type == "conical":
        s.lam = iso.nozzle_divergence_efficiency(self.nozzle_half_angle_deg)
    else:
        raise ValueError(f"unknown nozzle_type {self.nozzle_type!r}; choices: conical, bell")
    lam_reference = nozzle_shapes.reference_lambda(self.expansion_ratio)
    s.lam_relative = s.lam / lam_reference

    cf_vac_eff = iso.cf_vacuum(s.gamma, s.pe_pc, self.expansion_ratio) * s.lam_relative
    cf_sl_eff = cf_vac_eff - self.expansion_ratio * (PA_SEA_LEVEL / self.chamber_pressure_pa)

    s.isp_vac_chamber = iso.isp_from_cf(s.cstar, cf_vac_eff)
    s.isp_sl_chamber = iso.isp_from_cf(s.cstar, cf_sl_eff)
    s.sl_isp_unphysical = s.isp_sl_chamber <= 0
    if s.sl_isp_unphysical:
        # The ideal fully-attached-flow formula goes unphysical (even negative) far
        # into over-expansion - real flow separates long before this. Clamp to a
        # small positive nominal value; the separated_100pct warning below explains why.
        s.isp_sl_chamber = 1.0

    # Chamber flow for the target thrust. An open cycle (GG / tap-off) re-runs
    # with s.mdot_scale != 1 so chamber + turbine-exhaust thrust lands ON the
    # target (EngineDesign.compute); everything else runs at scale 1.0.
    s.mdot = self.target_vac_thrust_n * s.mdot_scale / (s.isp_vac_chamber * G0)
