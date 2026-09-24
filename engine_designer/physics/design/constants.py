"""Engine-level assumption constants used by EngineDesign.compute() (moved verbatim
from the former single-file design.py)."""
from .. import (isentropic as iso)

G0 = iso.G0
PA_SEA_LEVEL = 101_325.0

# Engine-level assumption constants (not user-exposed sliders - same role as
# the fixed constants in sim/h4_report.py). Combustion efficiency (eta_cstar)
# is looked up per propellant pair (combustion.DEFAULT_ETA_CSTAR) and then
# adjusted by the chosen injector's multiplier (injectors.py) - see that
# module for why it isn't one universal number.
JACKET_DP_PA = 1.6e6           # regen jacket pressure drop (fuel side only) - the FULL
                                # value for a real regenerative jacket; scaled down (or to
                                # zero) below for materials whose cooling_method has no such
                                # jacket at all, via JACKET_DP_FRACTION_BY_COOLING_METHOD
JACKET_DP_FRACTION_BY_COOLING_METHOD = {
    "regenerative": 1.0,   # a real full-flow regen jacket - JACKET_DP_PA applies as-is
    "dump": 0.2,           # dump cooling pumps a small bleed through the skirt tubes and
                            # dumps it overboard - a manifold stream, not the full jacket
                            # - a reasoned fraction, not independently sourced (Tier 3).
                            # (Film is no longer a section method - it is the film-overlay
                            # fields, tapped post-jacket, so it adds no jacket dP of its own.)
    "ablative": 0.0,       # no active cooling loop at all
    "radiative": 0.0,      # no active cooling loop at all
    "uncooled": 0.0,       # no active cooling loop at all
}
LINE_LOSS_PA = 0.5e6
TANK_HEAD_PA = 0.3e6           # slight positive tank head, subtracted from required pump dP
# Pump efficiency used to be two flat constants here (0.72/0.75) - now a per-design
# choice (EngineDesign.eta_pump_fuel/eta_pump_ox, suggested by physics/turbopump_tech.py's
# tier catalog) since real RO configs never expose distinct pump fields anyway (it's always
# implicit in the final Isp/thrust), so there's no "real" flat constant to fix here.
GG_ETA_TURBINE = 0.62         # FALLBACK ONLY - GG/tap-off turbine efficiency is now DERIVED
                              # per design (physics/turbopump_efficiency.py: staging ceiling
                              # x pitchline x admission x PR); this is the seed / degenerate
                              # fallback. Fleet 46-70%, most 55-66% ([SP-8107 Table III]).
GG_PRESSURE_RATIO = 22.0      # GG turbine pressure-ratio CAP - fleet 15.7-29, mean ~20
                              # ([SP-8107 Table III]; J-2 overall 19, F-1 16.4). Since
                              # 2026-09-24 the actual PR is min(this, turbine inlet / the
                              # outlet pressure the exhaust's back pressure needs) -
                              # physics/turbine_exhaust.py (H-1: 17.7 [H1-Man]).
EXPANDER_TURBINE_PR = 1.4            # ACTUAL expander turbine PR (RL10 1.42) - efficiency only.
# Turbine drive-gas thermodynamic properties, PER PROPELLANT PAIR, for the GG /
# tap-off / staged-combustion-preburner turbine-work model in turbopump.py
# (dh = cp*Tin*eta*(1 - PR^-((g-1)/g)); mdot_gg = pump_power / dh). cp & gamma are
# for the FUEL-RICH turbine gas, NOT the main-chamber mixture; tin_k is the GG /
# turbine-inlet temperature. These used to be three globals (1050 K / 2100 / 1.13)
# calibrated only to fuel-rich LOX/RP-1 gas - applying them to LOX/LH2 (whose
# fuel-rich GG gas is hydrogen-rich, ~4x the cp) over-predicted GG bleed flow ~5x.
#   LOX/RP-1  - unchanged 1050 K / 2100 / 1.13. Reproduces F-1 (~3.0%) and RD-0110
#               (4.2%, [KBKhA Table 2]: 3.97 of 93.8 kg/s) GG bleed fractions.
#   LOX/LH2   - H2-rich gas at GG MR ~0.9 (~47% H2 / ~53% H2O by mass -> cp ~8000,
#               gamma ~1.36); tin_k = J-2 fuel-turbine inlet 1200 F = 922 K
#               ([SP-8107 Table III], claude_lit/sources/nasa-sp8107). Spot-checked
#               in validate.py against the J-2 GG bleed and the [SP-8107 Table VI]
#               GG Isp-loss band (1/3-1% at 1000 psia, proportional to Pc).
#   storables - documented ENGINEERING ESTIMATE, not spot-checked (no storable GG
#               bleed-fraction data point in the reference set). Hotter turbine per
#               YLR87-AJ-7 (N2O4/A-50) inlet 1667 F = 1181 K [SP-8107 Table III];
#               very-fuel-rich hydrazine-family gas is lighter/more H2-bearing than
#               kerosene soot, so cp is nudged up from the kerolox value.
GG_GAS_PROPERTIES = {
    "LOX/RP-1":        dict(tin_k=1050.0, cp=2100.0, gamma=1.13),
    "LOX/LH2":         dict(tin_k=922.0,  cp=8000.0, gamma=1.36),
    "LOX/CH4":         dict(tin_k=1050.0, cp=3200.0, gamma=1.20),   # estimate - fuel-rich methane
                                                                    # GG gas: more CO/H2 than
                                                                    # kerosene soot, well below
                                                                    # hydrolox's 8000; no methalox
                                                                    # GG-bleed data point to calibrate
    "N2O4/MMH":        dict(tin_k=1150.0, cp=2800.0, gamma=1.22),   # estimate - see note above
    "Aerozine-50/NTO": dict(tin_k=1150.0, cp=2800.0, gamma=1.22),   # estimate - see note above
    "Hydrazine":       dict(tin_k=1050.0, cp=2100.0, gamma=1.13),   # monopropellant: pressure-fed
                                                                    # only, never reaches a turbine
                                                                    # branch - harmless placeholder
    "H2O2":            dict(tin_k=1050.0, cp=2100.0, gamma=1.13),   # monopropellant placeholder
}
# GG mixture ratio (ox/fuel) - how the GG's own propellant draw splits between
# the two pumps (the GG flow is PUMPED too; cycles.gas_generator_result). [SP-8081
# p.7]: fuel-rich MR 0.2-1.0, "hydrocarbons at the low end (~0.3), hydrogen at the
# high end (0.98-1.0)"; energetic storables < 0.2 (0.15 = inside that bound, Tier 3).
# The GG temperature is NOT derived from this (GG_GAS_PROPERTIES stays the input).
GG_MIXTURE_RATIO = {
    "LOX/RP-1": 0.3, "LOX/CH4": 0.3, "LOX/LH2": 0.9,
    "N2O4/MMH": 0.15, "Aerozine-50/NTO": 0.15, "Hydrazine": 0.15, "H2O2": 0.15,
}
# RETIRED 2026-09-24: the turbine-exhaust Isp is now COMPUTED per disposal mode
# (physics/turbine_exhaust.py: overboard duct / aspirator / nozzle injection) and
# stored as cycle_result["gg_dump_isp_fraction"]. These flat values are only the
# placeholder cycles.gas_generator_result stores before feed_stage overwrites it.
GG_DUMP_ISP_FRACTION = 0.55
TAP_OFF_DUMP_ISP_FRACTION = 0.80
# Tap-off drive gas: MAIN-CHAMBER combustion products (chamber MR), tapped near
# the injector face and film-cooled down to a turbine-tolerable temperature
# ([SP-8107]: "tapped near injector face where gas is relatively cool"). tin_k =
# min(Tc * TAP_OFF_TEMP_FRACTION, TAP_OFF_TURBINE_LIMIT_K); cp/gamma from the real
# combustion state (combustion.mixture_cp_j_kgk), NOT the fuel-rich GG_GAS_PROPERTIES.
TAP_OFF_TEMP_FRACTION = 0.55
TAP_OFF_TURBINE_LIMIT_K = 1150.0
TAP_OFF_PRESSURE_RATIO = 18.0      # "slightly < GG" ([SP-8107 Table VI]); GG is 22. A CAP since
                                   # 2026-09-24, like GG_PRESSURE_RATIO (turbine_exhaust.py)
SEPARATION_K = 0.4
CONVERGENT_HALF_ANGLE_DEG = 30.0
ETA_CSTAR_CEILING = 0.99
# Fuel-film cooling (EngineDesign.film_cooling_fraction): the wall film burns
# off the design mixture ratio, so it costs c* efficiency (~half the film fuel's
# contribution). The gas-side FLUX reduction is now a length-decaying curtain
# model in physics/cooling.film_effectiveness_profile (was a flat knock-down
# here). Tier 3 "warn/inform, direction is right", defaulting to 0.0 (off) so no
# existing design or spot check moves.
FILM_COOLING_ETA_CSTAR_PENALTY = 0.5
# Warn (don't block) above this total film fraction (chamber curtain + nozzle
# slot, of fuel flow). Real engines: ~2-10% typical, F-1 ~10-12% [claude_lit
# topics/06]; 25% is a generous sanity bound, not a sourced limit (Tier 3).
FILM_TOTAL_FRACTION_WARN = 0.25
# Labelling only (which zone the full-length wall-balance peak is reported in):
# stations within this local area ratio of the throat, either side, count as
# "throat" - a fillet-rounded throat spans several contour stations.
PEAK_WALL_THROAT_ZONE_EPS = 1.2

# 3D tube-drawing style, derived from the physics jacket topology (the old
# separate regen_circuit_style dropdown could disagree with it). The J-2 style
# draws the F-1's interleaved down/up tubes, with the down tubes starting at
# the mid-nozzle inlet ring.
REGEN_CIRCUIT_STYLE_BY_TOPOLOGY = {
    "single_pass_countercurrent": "single_pass_upflow",
    "f1_split_reverse_flow": "f1_double_pass",
    "j2_mid_nozzle_inlet": "j2_two_pass",
}

# Representative coolant (fuel) inlet temperature into the regen jacket, per
# pair - the inlet state of the coolant march (and of the real-property coolant
# tables it reads). Cryogenic fuels enter cold; storables and kerosene near
# ambient. A real jacket inlet also sees pump-discharge heating.
# LOX/LH2 (2026-09-23 audit, C2): 45 K, the warm end of [TN-Dump]'s measured
# ~57-85 R (32-47 K) LH2 jacket inlet (pump-discharge H2 is a few K above the
# tank). The old 100 K (unsourced) is already a thin supercritical gas
# (~19 kg/m3 at 8 MPa vs ~53 at 45 K), which mis-sized every LH2 jacket.
COOLANT_INLET_TEMP_K = {
    "LOX/LH2": 45.0,
    "LOX/RP-1": 300.0,
    "LOX/CH4": 112.0,          # liquid methane near its boiling point
    "N2O4/MMH": 290.0,
    "Aerozine-50/NTO": 290.0,
    "Hydrazine": 290.0,
    "H2O2": 290.0,
}
# Representative OXIDIZER inlet temperature at the engine, per pair - used ONLY
# by physics/flow_network.py (the 3D preview's flow visualization), never by
# any sizing/performance calc. LOX at its normal boiling point (90.2 K, a
# physical property); storable oxidizers at ambient. Tier 3, same caveat as
# COOLANT_INLET_TEMP_K above (no pump-discharge heating, no subcooling).
# Monopropellants have no oxidizer stream (absent -> None).
OXIDIZER_INLET_TEMP_K = {
    "LOX/LH2": 90.0,
    "LOX/RP-1": 90.0,
    "LOX/CH4": 90.0,
    "N2O4/MMH": 290.0,
    "Aerozine-50/NTO": 290.0,
}
CONTRACTION_RATIO_TYPICAL = (1.3, 6.0)
LSTAR_TYPICAL_M = (0.02, 3.0)   # widened from (0.5, 3.0) - verified: a 100N-class thruster needs
                                # L*~0.02m for a sane chamber aspect ratio, a 10kN-class needs
                                # ~0.15-0.2m, large GG boosters want ~0.9-1.3m - L* is a fixed
                                # LENGTH (not scale-relative), so small engines genuinely need a
                                # much smaller L*, not just a formula fix (see geometry.py docstring)
GG_FLOW_FRACTION_TYPICAL_MAX = 0.07  # real GG-cycle engines typically bleed a few percent of total
                                      # flow to drive the turbopump; a reasonable engineering band,
                                      # not independently sourced from one specific validated engine
                                      # (same tier as CONTRACTION_RATIO_TYPICAL/LSTAR_TYPICAL_M) -
                                      # only meaningful for OPEN cycles (GAS_GENERATOR/TAP_OFF) where
                                      # the bled flow is dumped at reduced Isp, not FRSC/ORSC, which
                                      # recover all preburner flow at the main injector (no dump loss)
PRESSURE_FED_PC_TYPICAL_MAX_PA = 1.0e6  # real classic pressure-fed engines cluster ~0.69-0.83 MPa
                                         # (Apollo SPS/AJ10-137 ~0.69 MPa, LM descent engine ~0.76 MPa
                                         # at full thrust, LM ascent engine ~0.83 MPa, R-4D ~0.69 MPa) -
                                         # modern composite-overwrapped tank tech (SpaceX SuperDraco,
                                         # ~6.9 MPa) can exceed this, but implies a much heavier/
                                         # higher-tech tank than this tool models

# Rated burn time (non-ablative materials): scaled from a flat baseline by how much chamber
# thermal margin the design has, referenced at materials.THIN_MARGIN_THRESHOLD (1.15) - the
# same "thin margin" line materials.py already warns at - so a just-barely-OK material choice
# reproduces the tool's traditional flat default, a comfortable margin extends it, and a
# marginal/warned choice shortens it. Clamped to a modest range so extreme margins don't
# produce absurd results. All Tier 3 - a reasoned engineering coupling, not a derived formula
# (real rated burn time depends heavily on mission role/size this tool doesn't model either).
BASE_RATED_BURN_TIME_S = 200.0
RATED_TIME_MARGIN_MULT_MIN = 0.3
RATED_TIME_MARGIN_MULT_MAX = 3.0

# Throat low-cycle thermal-fatigue check (physics/mass_model.py). The gradient
# that fatigues the wall acts across the HOT face (~1 mm channel-wall land),
# not the full hoop-stress thickness, so the estimate uses a representative
# hot-wall thickness. Warn-not-block when the estimated cycle life is thin
# relative to the planned ignition count (or an absolute floor).
REGEN_HOT_WALL_THICKNESS_M = 1.5e-3
FATIGUE_CYCLE_MARGIN = 4.0
FATIGUE_CYCLE_FLOOR = 20.0
