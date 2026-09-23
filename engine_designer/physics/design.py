"""
EngineDesign: the one object the GUI and the config exporter both talk to.
Takes the user's chosen inputs, calls the physics modules, and returns a
single results dict via compute(). No new physics is derived here - this
is composition + the documented engine-level assumption constants (the
same role /home/cory/ksp_config/sim/h4_report.py played for the H-4 report).
"""
import math
from dataclasses import dataclass, field

import numpy as np

from . import (combustion, combustion_stability, cooling, cycles, electric_pump, expander,
               geometry, geometry3d, gimbal, hatbands, ignition, injectors, isentropic as iso, manifold,
               mass_model, materials, nozzle_shapes, plumbing, staged_combustion, throttle, turbopump as tp,
               turbopump_materials, turbopump_sizing, turbopump_tech)

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
GG_PRESSURE_RATIO = 22.0      # GG/tap-off turbine pressure ratio - fleet 15.7-29, mean ~20
                              # ([SP-8107 Table III]; J-2 overall 19, F-1 16.4). Also shared.
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
GG_DUMP_ISP_FRACTION = 0.55
TAP_OFF_DUMP_ISP_FRACTION = 0.80   # tapped chamber-region gas is much closer to design MR than a GG mix
# Tap-off drive gas: MAIN-CHAMBER combustion products (chamber MR), tapped near
# the injector face and film-cooled down to a turbine-tolerable temperature
# ([SP-8107]: "tapped near injector face where gas is relatively cool"). tin_k =
# min(Tc * TAP_OFF_TEMP_FRACTION, TAP_OFF_TURBINE_LIMIT_K); cp/gamma from the real
# combustion state (combustion.mixture_cp_j_kgk), NOT the fuel-rich GG_GAS_PROPERTIES.
TAP_OFF_TEMP_FRACTION = 0.55
TAP_OFF_TURBINE_LIMIT_K = 1150.0
TAP_OFF_PRESSURE_RATIO = 18.0      # "slightly < GG" ([SP-8107 Table VI]); GG is 22
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
# pair - used only as the base of the coolant-side wall-temperature estimate
# for the chamber material check. Cryogenic fuels enter cold; storables and
# kerosene near ambient. Coarse (Tier 3): a real jacket inlet also sees pump
# discharge heating.
COOLANT_INLET_TEMP_K = {
    "LOX/LH2": 100.0,
    "LOX/RP-1": 300.0,
    "LOX/CH4": 112.0,          # liquid methane near its boiling point
    "N2O4/MMH": 290.0,
    "Aerozine-50/NTO": 290.0,
    "Hydrazine": 290.0,
    "H2O2": 290.0,
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


def _check(checklist, warnings, category, name, passed, fail_detail, pass_detail="OK"):
    """Record one design check into BOTH the flat `warnings` list (failures
    only - exact legacy content/order, consumed by gui/app.py's Warnings box
    AND export/cfg_writer.py's .cfg header comments) and the new structured
    `checklist` list (every check, pass or fail - consumed only by the GUI's
    Checklist tab). One call site keeps the two from ever silently drifting
    apart."""
    checklist.append({"category": category, "name": name, "passed": passed,
                       "detail": fail_detail if not passed else pass_detail})
    if not passed:
        warnings.append(fail_detail)


@dataclass
class EngineDesign:
    propellant_pair: str = "LOX/RP-1"
    mixture_ratio: float = 2.34
    chamber_pressure_pa: float = 8.0e6
    expansion_ratio: float = 14.0
    nozzle_type: str = "conical"          # "conical" or "bell"
    nozzle_half_angle_deg: float = 15.0   # conical mode
    bell_percent_length: float = 80.0     # bell mode (60-100)
    cycle: str = cycles.GAS_GENERATOR
    material_key: str = "narloy_z"
    bell_material_key: str = "inconel_718"        # nozzle-extension material, checked at a
                                                   # cooler LOCAL temperature, not Tc (see below)
    cooling_transition_eps: float = 6.0           # area ratio where the bell MATERIAL changes
                                                   # (chamber vs nozzle-extension material split,
                                                   # and the bell-material local-temp check).
                                                   # Also the default active-cooling cutoff -
                                                   # see regen_nozzle_end_eps to push it further.
    # Cooling method per section (physics/cooling.resolve_cooling_method_checked).
    # "auto" = infer from the section's material (historical behaviour); an
    # explicit value ("regenerative"/"dump"/"radiative"/"ablative"/"uncooled")
    # decouples the scheme from the material choice - but ONLY within that
    # material's allowed_cooling_methods: a physically meaningless combo (regen on
    # an ablative, ablative on a metal, ...) is HARD-BLOCKED - coerced to the
    # material's default with a failing checklist row. Film is an overlay (the
    # film_cooling_fraction / nozzle_film_* fields), not a method.
    chamber_cooling_method: str = "auto"
    nozzle_cooling_method: str = "auto"
    regen_nozzle_end_eps: float = 0.0             # >0 (and nozzle_cooling in ("regenerative",
                                                   # "dump")): push active cooling (flux
                                                   # integration, coolant march, expander cooled-
                                                   # area cutoff) past cooling_transition_eps out
                                                   # to this expansion ratio (clamped to
                                                   # expansion_ratio) - a full-length regen nozzle
                                                   # (SSME/RL10) or the dump-cooled slice a
                                                   # nozzle_cooling_method="dump" design actually
                                                   # cools. 0.0 = stop at cooling_transition_eps
                                                   # (today's behaviour / no dump-cooled slice).
                                                   # Independent of the bell-MATERIAL transition,
                                                   # which stays at cooling_transition_eps.
    dump_coolant_fraction: float = 0.0            # nozzle_cooling_method=="dump" only: fraction
                                                   # of fuel flow bled through the dump-cooled
                                                   # nozzle-extension slice (eps_for_transition ->
                                                   # cooled_length_eps) and ejected overboard.
                                                   # 0.0 = auto-size to the pair's coking/boiling
                                                   # coolant-dT limit (cooling.
                                                   # size_dump_coolant_fraction).
    cooling_flow_topology: str = "single_pass_countercurrent"  # | "f1_split_reverse_flow"
                                                   # | "j2_mid_nozzle_inlet"
                                                   # (physics/manifold.size_jacket_manifolds).
                                                   # j2_mid_nozzle_inlet (2026-09-22) is the one
                                                   # topology with its OWN thermal march
                                                   # (cooling.march_coolant_two_pass: inlet at
                                                   # jacket_inlet_eps, down 1/2-count tubes to
                                                   # the cooled end, back up the full-count
                                                   # tubes to the injector - the real J-2's
                                                   # 180 down / 360 up), in "channels" mode.
                                                   # For the other two topologies:
                                                   # Geometry/mass only - march_coolant's
                                                   # detailed thermal march stays topology-
                                                   # independent; see manifold_bypass_fraction
                                                   # for the one lumped-thermal approximation
                                                   # that IS modeled (down+return leg treated
                                                   # as one combined thermal unit, not two
                                                   # separately-mapped streams - deferred).
                                                   # Also sets the 3D tube-drawing style
                                                   # (REGEN_CIRCUIT_STYLE_BY_TOPOLOGY).
    manifold_bypass_fraction: float = manifold.MANIFOLD_BYPASS_FRACTION_DEFAULT
                                                   # f1_split_reverse_flow only: fraction of
                                                   # fuel routed directly to the injector
                                                   # manifold, bypassing the cooling jacket
                                                   # entirely - real F-1 value (heroicrelics.
                                                   # org F-1 thrust chamber page), Tier 2.
                                                   # User slider 0-60%. No-op under
                                                   # single_pass_countercurrent.
    jacket_inlet_eps: float = 8.0                  # j2_mid_nozzle_inlet only: nozzle area
                                                   # ratio of the mid-nozzle fuel inlet
                                                   # manifold (clamped to 1..cooled end). The
                                                   # real J-2 puts it partway down the nozzle
                                                   # (heroicrelics cutaway) but no area-ratio
                                                   # figure exists in this repo - Tier 3,
                                                   # arbitrary default (claude_lit/
                                                   # OPEN_QUESTIONS.md).
    film_cooling_fraction: float = 0.0            # CHAMBER film curtain: fraction of fuel flow
                                                   # injected as a wall film near the injector
                                                   # face - buys down the local gas-side heat
                                                   # flux / wall temperature there, at a small
                                                   # c*/Isp cost (that fuel burns off-mixture-
                                                   # ratio at the wall). 0.0 = none; real engines
                                                   # run ~2-10%. An OVERLAY on any chamber
                                                   # cooling method (regen + film, ablative +
                                                   # film, ...). Tapped POST-JACKET (the F-1
                                                   # curtain): it does not reduce the regen
                                                   # jacket's coolant flow.
    chamber_film_inject_area_ratio: float = 0.0   # where the chamber curtain enters: 0.0 = the
                                                   # injector face; > 1 = a film ring in the
                                                   # CONVERGENT section at that (subsonic) area
                                                   # ratio - protects the throat harder, leaves
                                                   # the barrel unfilmed.
    nozzle_film_fraction: float = 0.0             # SECOND, independent film site: fraction of
                                                   # fuel flow injected through a slot on the
                                                   # SUPERSONIC nozzle wall at
                                                   # nozzle_film_inject_eps (F-1 / J-2X film-
                                                   # cooled-extension practice). Post-jacket fuel;
                                                   # it never burns in the chamber, so it is
                                                   # costed like dump flow (cooling.
                                                   # dump_cooling_isp_penalty_fraction), not as a
                                                   # c* loss. 0.0 = off. Tier 3 (no film
                                                   # correlation in hand - SP-8124 missing).
    nozzle_film_inject_eps: float = 10.0          # supersonic area ratio of that slot. 10.0 = the
                                                   # F-1's real film-cooled-extension start
                                                   # (10:1 -> 16:1 exit) [SP-8120].
    # Regenerative coolant-channel design (physics/cooling.py). "flat" keeps the
    # legacy flat JACKET_DP_PA (1.6 MPa) - the neutral default, so no existing
    # design or spot check moves. "channels" runs the 1-D counterflow coolant
    # march: a real coolant-side wall temperature and a real Darcy-Weisbach
    # jacket pressure drop (which then feeds pump discharge -> turbine work ->
    # open-cycle Isp). The channel_* knobs are "auto" (0) unless the user forces
    # a value.
    regen_channel_model: str = "flat"            # "flat" | "channels"
    regen_channel_count: int = 0                 # 0 = auto (throat-scaled pitch)
    regen_channel_aspect_ratio: float = 0.0      # 0 = auto (size to target coolant velocity)
    regen_channel_land_fraction: float = 0.0     # 0 = auto (0.35)
    # Throat coolant velocity the channel/tube height is sized to (channels mode).
    # 0 = auto, the per-pair cooling.TARGET_COOLANT_VELOCITY_MS (RP-1 35 m/s).
    # Faster coolant -> higher h_c -> cooler coupled throat wall, at a jacket-dP
    # (pump power) cost; warned above SP-8087's 200 ft/s liquid limit.
    regen_coolant_velocity_ms: float = 0.0
    # Cooled-wall construction (physics/cooling.WALL_CONSTRUCTIONS). "milled_channel"
    # is the reference the channel model is calibrated to (all factors 1.0, so a
    # milled design is bit-identical to before this field existed). "tube_wall" /
    # "coax_shell" scale coolant-side h_c, jacket dP and jacket structural mass.
    wall_construction: str = "milled_channel"
    # 3D-preview-only rendering options for wall_construction=="tube_wall" (no
    # physics/mass effect either way - purely carried through to the result's
    # cooling dict for gui/preview3d_gl.py to consume; a no-op for
    # milled_channel/coax_shell, which don't render exposed discrete tubes).
    chamber_tube_jacket: bool = False   # cover the chamber/throat body with a
                                         # smooth jacket instead of showing its
                                         # tubes - real tube-wall engines often
                                         # wrap the chamber in a reinforcing band.
    tube_split_eps: float = 0.0         # area ratio where the visual tube count
                                         # doubles (1 tube -> 2), matching the
                                         # real F-1's 178 -> 356 bifurcation at
                                         # its 3:1 plane. 0.0 = no split.
    tube_hatbands: bool = False         # discrete reinforcing bands wrapped
                                         # around the tube bundle at intervals,
                                         # on the tube-wall chamber/throat body -
                                         # matches real tube-wall engines (e.g.
                                         # F-1) whose hatbands wrap the thrust
                                         # chamber itself, not a separate
                                         # bolted-on nozzle extension.
    tube_hatbands_on_extension: bool = False  # also continue the bands onto
                                         # the nozzle extension (bell), past
                                         # the body. No-op if there's no
                                         # separate extension.
    tube_hatband_count: int = 0         # 0 = structural auto: bands marched at
                                         # the allowable unsupported tube span
                                         # (physics/hatbands.py, SP-8120 p.29).
                                         # >0 = place exactly this many bands,
                                         # evenly spaced across the active span
                                         # (body, or body+extension), each still
                                         # structurally sized; a too-long gap warns.
    tube_hatband_width_m: float = 0.0   # 0 = auto (sized from each band's
                                         # tributary span, widened if needed to
                                         # carry its load). >0 = exact full axial
                                         # footprint width of each band, in meters.
    tube_hatband_shape: str = "auto"    # hatbands.BAND_SHAPE_CHOICES: "auto" =
                                         # lightest passing section per band
                                         # (flat near the throat, stiffer toward an
                                         # overexpanded exit - SP-8120 Fig. 40), or
                                         # force flat/tee/hat/channel/box everywhere.
    tube_hatband_material: str = "inconel_718"  # materials.MATERIALS key for the
                                         # bands (SP-8120: braze-compatible, age-
                                         # hardenable Inconel 718 / X-750).
    flange_thickness_m: float = 0.0     # 0 = auto (throat-diameter-scaled
                                         # default, preview3d_gl_core.
                                         # FLANGE_HALF_WIDTH_THROAT_DIA_MULT x 2).
                                         # >0 = exact FULL axial thickness of the
                                         # bolted-flange-joint collar (along the
                                         # chamber-to-exit axis), in meters.
                                         # 3D-preview-only (has_real_joint gated)
                                         # - no physics/mass effect, same
                                         # character as tube_hatband_width_m.
    flange_width_m: float = 0.0         # 0 = auto (throat-diameter-scaled
                                         # default, FLANGE_HEIGHT_THROAT_DIA_MULT).
                                         # >0 = exact radial extent - how far the
                                         # flange's OD rim reaches beyond the
                                         # wall - in meters.
    flange_bolt_count: int = 0          # 0 = auto (throat-diameter-based
                                         # spacing, BOLT_SPACING_THROAT_DIA_MULT).
                                         # >0 = place exactly this many bolts
                                         # instead.
    regen_circuit_style: str = "single_pass_upflow"  # DEPRECATED, ignored (kept so
                                         # old project files still load): the 3D tube-
                                         # drawing style is now derived from
                                         # cooling_flow_topology via
                                         # REGEN_CIRCUIT_STYLE_BY_TOPOLOGY and reported
                                         # as result["cooling"]["regen_circuit_style"].
    injector_type: str = "impinging"
    # Combustion-stability aids (physics/combustion_stability.py). Each defaults
    # to the no-op value, so no existing design or spot check moves. They RESOLVE
    # the acoustic-mode advisory and carry a consequence: baffles cost a small c*
    # and some mass; cavities cost mass; a stiffer injector costs feed pressure
    # (-> pump power/mass) and finer/fewer orifices.
    injector_baffles: bool = False
    baffle_compartments: int = 5                  # odd, >= 3 (even enhances tangential modes)
    acoustic_cavities: bool = False
    acoustic_cavity_count: int = 12
    injector_stiffness: str = "nominal"           # nominal | stiff | very_stiff
    # Injector / chamber detail (all default to the historical behaviour):
    orifice_type: str = "sharp_edged"            # physics/injectors.CD_BY_ORIFICE_TYPE key -
                                                   # sharp_edged == the old flat Cd 0.65
    impingement_angle_deg: float = 30.0          # included angle of an impinging element;
                                                   # feeds the resultant beta-angle calc + a
                                                   # 20-45 deg plausibility warn
    # Procedural plumbing runs (physics/plumbing.py) baked from the Shape Lab
    # (gui/shape_lab.py): a list of plumbing.run_to_dict() dicts - each a
    # manifold-rooted chain of pipe segments with per-joint flanges, keyed by
    # `host` (which manifold ring it grows from: "jacket_inlet" is the test
    # bed). Plain dicts, not dataclasses, so dataclasses.asdict / from_dict /
    # __eq__ / JSON all work unchanged; compute() normalises each through
    # plumbing.run_from_dict (clamping) before resolving. The ONLY collection-
    # valued field on this class - note compute()'s "inputs" snapshot is a
    # shallow copy, so this list is shared with the result (read-only there).
    # Replaced the earlier dead-stored manifold_intake_angle_deg /
    # manifold_bend_radius_tube_dia_mult / manifold_rotation_deg fields
    # (schema 3 -> 4; those keys are silently dropped from old files).
    plumbing_runs: list = field(default_factory=list)
    # Per-ring manifold sizing (schema 5 -> 6: were one global
    # manifold_velocity_head_fraction / manifold_taper_blend, now copied into
    # every ring by from_dict when an old file carries them).
    # Injector-feed rings: velocity head 0.5*rho*V^2 as a fraction of that
    # leg's own injector dP (physics/manifold.py velocity_from_head_fraction) -
    # 1-15% sliders. Direction cited (slow header -> uniform orifice feed,
    # SP-8087/SP-8120/CR-128318), value Tier 3.
    fuel_manifold_head_fraction: float = 0.04
    ox_manifold_head_fraction: float = 0.04
    # Split/tapered header rings: 0 = constant area, 1 = constant velocity
    # (area follows the draining flow). SP-8087 Sec.3.1.2.1: a real torus lies
    # BETWEEN the two - 0.5 is that midpoint (Tier 3). physics/manifold.py
    # taper_area_fraction. The jacket turnaround collar/band has no knobs.
    fuel_manifold_taper_blend: float = 0.5
    ox_manifold_taper_blend: float = 0.5
    jacket_inlet_taper_blend: float = 0.5
    jacket_inlet_velocity_mult: float = 1.0      # jacket-inlet ring velocity / the local
                                                   # coolant-passage velocity (0.5-2.0). 1.0 =
                                                   # Fagherazzi's matched velocity (no abrupt
                                                   # change ring -> passages); Tier 3.
    apply_chamber_pressure_loss: bool = False    # when True, the pump must supply the
                                                   # (higher) injector-end pressure for a
                                                   # finite contraction ratio; always computed
                                                   # & shown, only fed into feed pressure here
    convergent_half_angle_deg: float = 30.0      # convergent-cone half angle ([Huzel] 20-45)
    ignition_system: str = "tea_teb"
    throttle_floor: float = 0.6
    target_vac_thrust_n: float = 500_000.0
    host_model_engine_type: str = ""   # catalog entry to bind the exported CONFIG onto
    lstar_m: float = 1.0
    contraction_ratio: float = 1.6
    # Chamber sizing method (physics/geometry.chamber_geometry). "lstar" = the
    # historical L**At volume. "residence_time" sizes the chamber volume from a
    # target combustion stay time instead; chamber_residence_time_ms == 0 uses
    # the stay time implied by this pair's L* default (identical result).
    chamber_sizing_method: str = "lstar"          # "lstar" | "residence_time"
    chamber_residence_time_ms: float = 0.0        # 0 = auto (from the pair's L* default)
    chamber_wall_fillet_r_over_rt: float = 0.0    # round the cylinder->convergent
                                                   # corner with an R = (this)*Rt arc;
                                                   # 0.0 = historical sharp corner
    turbopump_tech_key: str = "mature"    # physics/turbopump_tech.py - now supplies only a
                                           # build_quality_factor multiplier on the DERIVED
                                           # efficiency (early 0.93 / mature 1.00 / advanced 1.04)
    eta_pump_fuel: float = 0.0            # 0.0 = derive from the machinery design
                                           # (physics/turbopump_efficiency.py); a value in
                                           # (0, 1] pins that pump's efficiency manually
    eta_pump_ox: float = 0.0
    pump_specific_power_w_kg: float = 36000.0  # FALLBACK ONLY - turbopump mass is
                                                # geometry-derived (physics/turbopump_sizing.py);
                                                # this is used only if the geometry is degenerate
    # Turbopump architecture (physics/turbopump_sizing.py). "auto" derives the
    # arrangement/staging from propellant pair + cycle + thrust; a concrete
    # override is the only thing that moves computed_dry_mass_kg (the auto
    # architecture is mass_modifier == 1.0 by construction).
    turbopump_arrangement: str = "auto"   # auto | single_shaft | dual_shaft | geared
    turbine_staging: str = "auto"         # auto | single_impulse | velocity_compounded_2row
                                           #      | pressure_compounded_2stage | reaction
    turbopump_material_key: str = "inconel_718"  # physics/turbopump_materials.py catalog key
    bearing_material_key: str = "cronidur_30"  # physics/turbopump_materials.py BEARING_MATERIALS key
    enforce_suction_limit: bool = False   # opt-in NPSH-required/suction-specific-speed check
                                           # (physics/turbopump_sizing.py) - REQUIRED-only, never
                                           # claims to know actual cavitation risk (no tank model)
    # NPSH the VEHICLE delivers at each pump inlet (ft) - a user input, the tool
    # has no tank model. 0 = not limiting (default, bit-identical to before);
    # > 0 caps that pump's rotor speed at its suction-specific-speed limit
    # (turbopump_sizing.suction_limited_rpm): bigger impeller, lower efficiency.
    npsh_available_fuel_ft: float = 0.0
    npsh_available_ox_ft: float = 0.0
    # Staged-combustion preburner temperatures (K) - DESIGN INPUTS; the turbine
    # PR is solved from them (physics/staged_combustion.solve_staged_power_balance).
    # 0 = the pair default (staged_combustion.PREBURNER_GAS_PROPERTIES /
    # ORSC_GAS_PROPERTIES). preburner_tin_k = the fuel-rich preburner (FRSC, FFSC
    # fuel side); ox_preburner_tin_k = the oxidiser-rich one (ORSC, FFSC ox side).
    preburner_tin_k: float = 0.0
    ox_preburner_tin_k: float = 0.0
    pump_stages_fuel: int = 0             # 0 = auto (derived); >0 overrides
    pump_stages_ox: int = 0
    controller_tech_key: str = "baseline"  # physics/controller_tech.py catalog key - export-time only
    gimbal_mode: str = "inherit"          # "inherit" | "custom" | "ungimballed"
    gimbal_range_deg: float = 6.0         # only meaningful in "custom" mode
    gimbal_response_speed_deg_s: float = 0.0  # 0 = don't emit useGimbalResponseSpeed/gimbalResponseSpeed
    tech_node: str = ""                   # RP-1 %techRequired - empty = no tech-tree gating
    entry_cost: float = 10000.0
    cost: float = 20.0
    ignitions: int = 1                    # export-time only (like tech_node/entry_cost/cost) -
                                           # forced to 1 at export if the chosen ignition system's
                                           # forces_single_ignition is True (see ignition.py)

    # --- export output shape (export/cfg_writer.py) - all export-time only ---
    # "additional_config"  : append a CONFIG to the host part's ModuleEngineConfigs
    #                        (the historical behaviour - a new variant on someone
    #                        else's part, host model at native size).
    # "new_part_in_place"  : additional_config + a patch that rescales the host
    #                        part's model to this engine's computed length.
    # "new_part_standalone": a separate part (own name/title/tech gating) that
    #                        BORROWS the host part's model, rescaled - generated
    #                        equivalent of TR341_Config.cfg.
    output_mode: str = "additional_config"
    config_name: str = "MyEngine-100K"       # RF CONFIG `name` (was GUI-only export_name_var)
    host_model_reference_height_m: float = 0.0  # 0 = auto (catalog/roengines_models.json);
                                                 # >0 overrides it (m). Used only when a mode
                                                 # rescales the model.
    new_part_name: str = ""                  # standalone mode; blank -> derived from config_name
    new_part_title: str = ""                 # blank -> config_name
    new_part_manufacturer: str = "Fictional"
    new_part_description: str = ""           # blank -> auto one-liner

    # --- project-file (de)serialisation (gui/project_io.py) ---
    SCHEMA_VERSION = 8   # 8 (2026-09-23): film became an OVERLAY - "film" is no longer a
                         # section cooling method (migrated in from_dict below); new
                         # chamber_film_inject_area_ratio / nozzle_film_* fields default off.
                         # 7 (2026-09-23): tube_hatband_shape/_material added; hatband
                         # count 0 now = structural auto (physics/hatbands.py) - no key
                         # migration needed, a v6 file's new fields take defaults.

    def to_dict(self):
        """JSON-serialisable snapshot of every design input (all fields are
        str/float/int/bool). Wrapped with a schema version for forward-compat."""
        import dataclasses
        return {"schema_version": EngineDesign.SCHEMA_VERSION,
                "design": dataclasses.asdict(self)}

    @classmethod
    def from_dict(cls, data):
        """Rebuild an EngineDesign from `to_dict()` output (or a bare field
        dict). Unknown keys are dropped; missing keys take their default -
        so a file saved by an older OR newer tool version still loads."""
        import dataclasses
        payload = data.get("design", data) if isinstance(data, dict) else {}
        payload = dict(payload)
        # Schema 5 -> 6: the global manifold head fraction / taper blend became
        # per-ring fields - an old file's value seeds every ring it applied to.
        for _old, _news in (("manifold_velocity_head_fraction",
                             ("fuel_manifold_head_fraction", "ox_manifold_head_fraction")),
                            ("manifold_taper_blend",
                             ("fuel_manifold_taper_blend", "ox_manifold_taper_blend",
                              "jacket_inlet_taper_blend"))):
            if _old in payload:
                for _new in _news:
                    payload.setdefault(_new, payload[_old])
        # Schema 7 -> 8: "film" was a section cooling method; it is now the film
        # OVERLAY. A film-cooled-only wall IS an uncooled wall + a curtain, so the
        # section becomes "uncooled" (or "auto" if its material can't be uncooled,
        # e.g. an ablative) and gets at least the reference film fraction - the
        # chamber via film_cooling_fraction, the nozzle via a slot at the old
        # material-transition eps. Applied whenever "film" appears (it is invalid
        # at every schema now), so it is idempotent.
        _ref = cooling.FILM_MDOT_RATIO_REFERENCE
        for _field, _mat_field in (("chamber_cooling_method", "material_key"),
                                   ("nozzle_cooling_method", "bell_material_key")):
            if payload.get(_field) != "film":
                continue
            _mat = materials.MATERIALS.get(
                payload.get(_mat_field, getattr(cls, _mat_field, "")))
            payload[_field] = ("uncooled" if _mat is None
                               or "uncooled" in _mat.allowed_cooling_methods else "auto")
            if _field == "chamber_cooling_method":
                payload["film_cooling_fraction"] = max(
                    float(payload.get("film_cooling_fraction", 0.0) or 0.0), _ref)
            else:
                payload["nozzle_film_fraction"] = max(
                    float(payload.get("nozzle_film_fraction", 0.0) or 0.0), _ref)
                payload.setdefault("nozzle_film_inject_eps",
                                   float(payload.get("cooling_transition_eps", 6.0)))
        known = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in payload.items() if k in known})

    def _film_phi(self, xs, rs, throat_dia_m):
        """(combined, chamber, nozzle) per-station film flux multipliers on the
        contour: the chamber curtain (film_cooling_fraction, at the injector face
        or a convergent ring at chamber_film_inject_area_ratio) and the nozzle-
        extension slot (nozzle_film_fraction at nozzle_film_inject_eps),
        combined by cooling.combined_film_phi. Both are overlays on whatever
        section cooling method is in effect. No slot film -> combined ==
        chamber, bit-identical to the single-site model."""
        phi_c = cooling.film_effectiveness_profile(
            xs, rs, throat_dia_m, max(0.0, self.film_cooling_fraction),
            inject_area_ratio=(self.chamber_film_inject_area_ratio
                               if self.chamber_film_inject_area_ratio > 1.0 else None))
        phi_n = cooling.nozzle_film_effectiveness_profile(
            xs, rs, throat_dia_m, max(0.0, self.nozzle_film_fraction),
            self.nozzle_film_inject_eps)
        if not np.any(phi_n < 1.0):
            return phi_c, phi_c, phi_n
        return cooling.combined_film_phi(phi_c, phi_n), phi_c, phi_n

    def compute(self):
        """The one entry point. A design with a plumbing run connected to a
        turbopump port (plumbing.PlumbingRun.connect_to_pump) has a circular
        dependency - line loss -> pump dP -> pump size -> port position -> run
        geometry -> line loss - broken with ONE extra pass: pass 1 uses the
        flat LINE_LOSS_PA, pass 2 re-runs with pass 1's computed per-leg
        losses (the pump barely moves, so it converges; the residual is
        reported as line_loss_residual_pa). No connected run -> one pass,
        bit-identical to before."""
        result = self._compute_pass(None)
        computed = result.get("line_loss_computed") or {}
        if any(v is not None for v in computed.values()):
            result = self._compute_pass(computed)
            again = result.get("line_loss_computed") or {}
            result["line_loss_residual_pa"] = max(
                (abs((again.get(k) or 0.0) - (computed.get(k) or 0.0)) for k in computed),
                default=0.0)
        return result

    def _compute_pass(self, line_loss_override):
        warnings = []
        checklist = []
        # Feed-line loss per pump leg (pump discharge -> ring): the flat
        # LINE_LOSS_PA unless a previous pass computed it from a connected run.
        _llo = line_loss_override or {}
        line_loss_fuel_pa = _llo["fuel"] if _llo.get("fuel") is not None else LINE_LOSS_PA
        line_loss_ox_pa = _llo["ox"] if _llo.get("ox") is not None else LINE_LOSS_PA

        mr_lo, mr_hi = combustion.mr_bounds(self.propellant_pair)
        _check(checklist, warnings, "propellant/cycle", "Mixture ratio within table range",
               mr_lo <= self.mixture_ratio <= mr_hi,
               f"Mixture ratio {self.mixture_ratio:.2f} is outside the "
               f"literature-anchored table range [{mr_lo}, {mr_hi}] for "
               f"{self.propellant_pair} - combustion numbers are extrapolated.")

        tc, gamma, m_molar = combustion.combustion_state(self.propellant_pair, self.mixture_ratio)
        rho_fuel, rho_ox = combustion.propellant_densities(self.propellant_pair)

        mach = iso.mach_from_area_ratio(self.expansion_ratio, gamma)
        pe_pc = iso.pe_over_pc(mach, gamma)
        pe_pa = pe_pc * self.chamber_pressure_pa

        injector = injectors.INJECTORS[self.injector_type]

        # Combustion completeness vs. L* (residence time = L*/c*_ideal, using the IDEAL
        # c* - before any efficiency multiplier - specifically to avoid a circular
        # dependency: completeness feeds eta_cstar, so it can't also depend on the
        # eta_cstar-scaled c*). See combustion.completeness_factor's docstring.
        cstar_ideal = iso.c_star(tc, gamma, m_molar, eta_cstar=1.0)
        residence_time_s = self.lstar_m / cstar_ideal
        completeness = combustion.completeness_factor(
            self.lstar_m, self.propellant_pair, injector.atomization_time_modifier)
        required_length_m = combustion.L_MID_BASE[self.propellant_pair] * injector.atomization_time_modifier
        required_time_s = required_length_m / cstar_ideal

        eta_cstar = (combustion.DEFAULT_ETA_CSTAR[self.propellant_pair]
                     * injector.eta_cstar_multiplier * completeness)
        if self.cycle in cycles.STAGED_CYCLES:
            eta_cstar *= staged_combustion.STAGED_ETA_CSTAR_PENALTY[self.cycle]
        film_fraction = max(0.0, self.film_cooling_fraction)
        if film_fraction > 0.0:
            eta_cstar *= (1.0 - FILM_COOLING_ETA_CSTAR_PENALTY * film_fraction)
        if self.injector_baffles:
            # Baffle blades span the injector face and consume film coolant -
            # a small c* hit [claude_lit/topics/14].
            eta_cstar *= (1.0 - combustion_stability.BAFFLE_CSTAR_PENALTY)
        eta_cstar = min(eta_cstar, ETA_CSTAR_CEILING)
        cstar = iso.c_star(tc, gamma, m_molar, eta_cstar)

        # Combustion-gas transport properties + recovery temp (physics/combustion.py
        # derives these, not tabulated) - computed this early because the
        # regen-jacket pre-march below (for the pump-feed jacket dP estimate) now
        # needs them for the same computed-absolute Bartz flux the authoritative
        # cooling model further down uses; both must agree.
        mu_gas = combustion.gas_viscosity_pa_s(m_molar, tc)
        pr_gas = combustion.prandtl(gamma)
        cp_gas = combustion.mixture_cp_j_kgk(gamma, m_molar)
        t_aw_chamber_k = cooling.recovery_temperature(tc)

        # Chamber sizing method (physics/geometry.chamber_geometry). "lstar" is the
        # historical path. "residence_time" sizes Vc from a target combustion stay
        # time; chamber_residence_time_ms == 0 falls back to the stay time implied
        # by this pair's [Huzel Table 4-1] L* default, which reproduces the L*
        # sizing exactly (combustion.residence_time_from_lstar_s).
        chamber_sizing_rt_s = 0.0
        if self.chamber_sizing_method == "residence_time":
            chamber_sizing_rt_s = (
                self.chamber_residence_time_ms / 1000.0 if self.chamber_residence_time_ms > 0.0
                else combustion.residence_time_from_lstar_s(
                    combustion.l_star_default_for_pair(self.propellant_pair), tc, cstar, m_molar))

        # --- nozzle contour + divergence efficiency: conical vs bell ---
        # lam_relative scores the chosen nozzle AGAINST an 80%-bell reference at this
        # same expansion ratio, matching what combustion.DEFAULT_ETA_CSTAR's calibration
        # (physics/validate.py) implicitly assumes - see nozzle_shapes.reference_lambda's
        # docstring. Applying the raw lam directly here would double-count the divergence
        # loss the calibration already absorbed (this was the LMDE-comparison bug).
        theta_n_deg = theta_e_deg = None
        if self.nozzle_type == "bell":
            theta_n_deg, theta_e_deg = nozzle_shapes.bell_angles(self.expansion_ratio, self.bell_percent_length)
            lam = nozzle_shapes.bell_divergence_efficiency(theta_e_deg)
        elif self.nozzle_type == "conical":
            lam = iso.nozzle_divergence_efficiency(self.nozzle_half_angle_deg)
        else:
            raise ValueError(f"unknown nozzle_type {self.nozzle_type!r}; choices: conical, bell")
        lam_reference = nozzle_shapes.reference_lambda(self.expansion_ratio)
        lam_relative = lam / lam_reference

        cf_vac_eff = iso.cf_vacuum(gamma, pe_pc, self.expansion_ratio) * lam_relative
        cf_sl_eff = cf_vac_eff - self.expansion_ratio * (PA_SEA_LEVEL / self.chamber_pressure_pa)

        isp_vac_chamber = iso.isp_from_cf(cstar, cf_vac_eff)
        isp_sl_chamber = iso.isp_from_cf(cstar, cf_sl_eff)
        sl_isp_unphysical = isp_sl_chamber <= 0
        if sl_isp_unphysical:
            # The ideal fully-attached-flow formula goes unphysical (even negative) far
            # into over-expansion - real flow separates long before this. Clamp to a
            # small positive nominal value; the separated_100pct warning below explains why.
            isp_sl_chamber = 1.0

        mdot = self.target_vac_thrust_n / (isp_vac_chamber * G0)

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
        orifice_cd = injectors.cd_for_orifice(self.orifice_type)
        dp_injector_nominal = injector.dp_over_pc_nominal * self.chamber_pressure_pa
        dp_injector_derived = max(
            injectors.derived_dp_pa(rho_fuel, injectors.INJECTION_VELOCITY_TARGET_MS["fuel"], orifice_cd),
            injectors.derived_dp_pa(rho_ox, injectors.INJECTION_VELOCITY_TARGET_MS["ox"], orifice_cd))
        # A 'stiff' / 'very_stiff' injector build raises the effective dP/Pc
        # (the primary injector-side stability cure - claude_lit/topics/05/14),
        # which then propagates into the required pump discharge pressure and
        # the element geometry exactly like the nominal value does. 'nominal'
        # leaves everything untouched.
        effective_dp_over_pc = combustion_stability.stiff_injector_dp_over_pc(
            self.injector_stiffness, injector.dp_over_pc_nominal)
        dp_injector_stiff = effective_dp_over_pc * self.chamber_pressure_pa
        dp_injector = max(dp_injector_nominal, dp_injector_derived, dp_injector_stiff)
        # Per-leg injector dP (fuel, ox) - the type's dp_ox_over_fuel ratio; 1.0
        # (every original catalog entry) leaves both equal to dp_injector.
        dp_injector_fuel, dp_injector_ox = injectors.dp_split(dp_injector, self.injector_type)
        # Finite-contraction-ratio chamber flow: the pump must supply the
        # injector-END pressure, which exceeds the nozzle-stagnation Pc that
        # sets thrust/Isp. Always computed & reported; only routed into the feed
        # chain when apply_chamber_pressure_loss is on.
        chamber_flow = combustion.chamber_flow(self.contraction_ratio, gamma)
        pc_feed = (self.chamber_pressure_pa * chamber_flow["injector_end_pressure_ratio"]
                   if self.apply_chamber_pressure_loss else self.chamber_pressure_pa)
        # Looked up here (not just at the thermal-margin check further down) because the
        # chamber material's cooling_method now determines how much (if any) regen-jacket
        # pressure drop applies - a design with an ablative/radiative chamber has no active
        # cooling loop at all, so charging it JACKET_DP_PA (as every cycle used to,
        # unconditionally) was a real, previously undocumented inconsistency.
        chamber_material = materials.MATERIALS[self.material_key]
        bell_material = materials.MATERIALS[self.bell_material_key]
        # Cooling method per section: "auto" -> the material's own cooling_method
        # (historical, bit-identical); an explicit EngineDesign value overrides it.
        # HARD block (a deliberate exception to "warn, don't block"): an explicit
        # method the section's material can't physically be built for (regen on an
        # ablative, ablative on a metal, a regen C-C wall, ...) falls back to the
        # material's own method, and a FAILING checklist row says so. Old project
        # files are never rewritten - they coerce here, every compute.
        chamber_cooling, chamber_cooling_rejected = cooling.resolve_cooling_method_checked(
            self.chamber_cooling_method, chamber_material)
        nozzle_cooling, nozzle_cooling_rejected = cooling.resolve_cooling_method_checked(
            self.nozzle_cooling_method, bell_material)
        for _sec, _mat, _rej, _eff in (("Chamber", chamber_material, chamber_cooling_rejected,
                                        chamber_cooling),
                                       ("Nozzle/bell", bell_material, nozzle_cooling_rejected,
                                        nozzle_cooling)):
            _why = ("film is no longer a section method - use the film-cooling overlay "
                    "(chamber film % / nozzle slot film %) on top of a base method"
                    if _rej == "film" else
                    f"it can only be built for: {', '.join(_mat.allowed_cooling_methods)}")
            _check(checklist, warnings, "materials",
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
        if nozzle_cooling in ("regenerative", "dump") and self.regen_nozzle_end_eps > 0.0:
            cooled_length_eps = max(_cool_base_eps,
                                    min(self.regen_nozzle_end_eps, self.expansion_ratio))
        else:
            cooled_length_eps = _cool_base_eps
        # J-2-style mid-nozzle inlet (cooling.march_coolant_two_pass): the
        # inlet must sit between the throat and the cooled end.
        two_pass = self.cooling_flow_topology == "j2_mid_nozzle_inlet"
        jacket_inlet_eps_eff = (min(max(self.jacket_inlet_eps, 1.0), cooled_length_eps)
                                if two_pass else None)
        # The J-2 layout's tube split IS its inlet ring (down tubes join the
        # up tubes there), so the user's tube_split_eps is ignored under it -
        # everywhere, physics and the 3D preview alike.
        split_eps_eff = 0.0 if two_pass else self.tube_split_eps

        # Regen-jacket pressure drop. "flat" (default) uses the legacy constant so
        # nothing already validated moves. "channels" runs the coolant-channel
        # march here (on a cheap conical-profile approximation of the contour -
        # the divergent section past the throat contributes almost nothing to
        # jacket dP, and only eps <= cooling_transition_eps of it is cooled at
        # all) so the pump-feed chain below sees the real jacket dP. The
        # authoritative coolant-side wall temperature / coolant dT are re-marched
        # further down on the real (bell) contour with the film-cooling factor.
        coolant_march_pre = None
        if (self.regen_channel_model == "channels"
                and chamber_cooling == "regenerative"):
            _geo_pre = geometry.chamber_geometry(
                mdot, cstar, self.chamber_pressure_pa, self.expansion_ratio,
                self.lstar_m, self.contraction_ratio, self.convergent_half_angle_deg,
                self.chamber_wall_fillet_r_over_rt, self.chamber_sizing_method,
                chamber_sizing_rt_s, tc, m_molar)
            _xs_pre, _rs_pre, _ = geometry.nozzle_profile(
                _geo_pre["chamber_dia_m"], _geo_pre["throat_dia_m"], _geo_pre["exit_dia_m"],
                _geo_pre["chamber_length_m"], self.convergent_half_angle_deg,
                self.nozzle_half_angle_deg, self.chamber_wall_fillet_r_over_rt)
            _film_phi_pre = self._film_phi(_xs_pre, _rs_pre, _geo_pre["throat_dia_m"])[0]
            _q_pre = cooling.absolute_heat_flux_profile(
                _xs_pre, _rs_pre, _geo_pre["throat_dia_m"], self.chamber_pressure_pa, cstar,
                mu_gas, cp_gas, pr_gas, t_aw_chamber_k, pair=self.propellant_pair,
                transition_area_ratio=cooled_length_eps) * _film_phi_pre
            # Bypass-aware down-leg flow, mirroring mdot_coolant_jacket_kgs
            # below (not yet defined at this point in compute() - mdot_fuel_kgs
            # itself doesn't exist yet either, hence the local recomputation).
            _mdot_fuel_pre = mdot / (1.0 + self.mixture_ratio)
            _mdot_coolant_pre = (_mdot_fuel_pre * (1.0 - self.manifold_bypass_fraction)
                                  if self.cooling_flow_topology == "f1_split_reverse_flow"
                                  else _mdot_fuel_pre)
            _pre_kw = dict(n_channels=self.regen_channel_count,
                           aspect_ratio=self.regen_channel_aspect_ratio,
                           target_velocity_ms=self.regen_coolant_velocity_ms,
                           land_fraction=self.regen_channel_land_fraction,
                           transition_area_ratio=cooled_length_eps,
                           t_inlet_k=COOLANT_INLET_TEMP_K.get(self.propellant_pair, 290.0),
                           construction=self.wall_construction)
            coolant_march_pre = cooling.march_coolant(
                _xs_pre, _rs_pre, _q_pre, _geo_pre["throat_dia_m"],
                _mdot_coolant_pre, self.propellant_pair, split_eps=split_eps_eff,
                **_pre_kw)
            if two_pass:
                # This cheap conical contour has ONE throat->exit segment, so
                # it resolves no mid-nozzle down pass at all. Keep its single-
                # pass dP as the baseline (what every validated pump-feed
                # number is pinned to) and ADD the two-pass increment, measured
                # on a finely resampled copy of the same cone - zero down-pass
                # length still reproduces the single-pass value exactly.
                _xs_f = np.linspace(float(_xs_pre[0]), float(_xs_pre[-1]), 241)
                _rs_f = np.interp(_xs_f, _xs_pre, _rs_pre)
                _q_f = cooling.absolute_heat_flux_profile(
                    _xs_f, _rs_f, _geo_pre["throat_dia_m"], self.chamber_pressure_pa, cstar,
                    mu_gas, cp_gas, pr_gas, t_aw_chamber_k, pair=self.propellant_pair,
                    transition_area_ratio=cooled_length_eps) * self._film_phi(
                    _xs_f, _rs_f, _geo_pre["throat_dia_m"])[0]
                _tp_f = cooling.march_coolant_two_pass(
                    _xs_f, _rs_f, _q_f, _geo_pre["throat_dia_m"], _mdot_coolant_pre,
                    self.propellant_pair, inlet_area_ratio=jacket_inlet_eps_eff, **_pre_kw)
                _sp_f = cooling.march_coolant(
                    _xs_f, _rs_f, _q_f, _geo_pre["throat_dia_m"], _mdot_coolant_pre,
                    self.propellant_pair, **_pre_kw)
                _base_dp = coolant_march_pre["jacket_dp_pa"]
                coolant_march_pre = dict(_tp_f)
                coolant_march_pre["jacket_dp_pa"] = (
                    _base_dp + max(0.0, _tp_f["jacket_dp_pa"] - _sp_f["jacket_dp_pa"]))
            jacket_dp_base_pa = coolant_march_pre["jacket_dp_pa"]
        else:
            jacket_dp_base_pa = JACKET_DP_PA
        jacket_dp_pa = jacket_dp_base_pa * JACKET_DP_FRACTION_BY_COOLING_METHOD.get(
            chamber_cooling, 1.0)

        # Per-propellant-pair turbine drive-gas properties (fuel-rich GG / preburner
        # gas), shared by every turbopump cycle branch below. See GG_GAS_PROPERTIES.
        gg_gas = GG_GAS_PROPERTIES[self.propellant_pair]

        # Build-quality multiplier on the DERIVED pump/turbine efficiency, and the
        # effective turbine staging (physics/turbopump_efficiency.py / _sizing.py).
        build_quality = turbopump_tech.TURBOPUMP_TECHS[self.turbopump_tech_key].build_quality_factor
        eff_staging = (turbopump_sizing.derive_turbine_staging(self.cycle, self.propellant_pair)
                       if self.turbine_staging in ("", "auto") else self.turbine_staging)
        eta_pf = eta_po = eta_turb = 0.0   # derived per turbopump cycle branch below
        _suction_kw = dict(npsh_available_fuel_ft=max(0.0, float(self.npsh_available_fuel_ft or 0.0)),
                           npsh_available_ox_ft=max(0.0, float(self.npsh_available_ox_ft or 0.0)))

        if self.cycle == cycles.GAS_GENERATOR:
            dp_fuel = pc_feed + dp_injector_fuel + jacket_dp_pa + line_loss_fuel_pa - TANK_HEAD_PA
            dp_ox = pc_feed + dp_injector_ox + line_loss_ox_pa - TANK_HEAD_PA
            eta_pf, eta_po, eta_turb = turbopump_sizing.derive_efficiencies(
                mdot, self.mixture_ratio, dp_fuel, dp_ox, rho_fuel, rho_ox,
                self.turbopump_material_key, eff_staging, gg_gas["tin_k"], gg_gas["cp"],
                gg_gas["gamma"], GG_PRESSURE_RATIO, GG_PRESSURE_RATIO, build_quality,
                pump_stages_fuel=self.pump_stages_fuel, pump_stages_ox=self.pump_stages_ox,
                eta_pump_fuel_override=self.eta_pump_fuel, eta_pump_ox_override=self.eta_pump_ox,
                enforce_suction_limit=self.enforce_suction_limit, **_suction_kw)
            cyc = cycles.gas_generator_result(
                mdot, self.mixture_ratio, self.chamber_pressure_pa, dp_fuel, dp_ox,
                rho_fuel, rho_ox, eta_pf, eta_po, self.pump_specific_power_w_kg,
                gg_gas["tin_k"], gg_gas["cp"], eta_turb, GG_PRESSURE_RATIO, gg_gas["gamma"],
                GG_DUMP_ISP_FRACTION, cycle_name=cycles.GAS_GENERATOR,
                gg_mixture_ratio=GG_MIXTURE_RATIO[self.propellant_pair],
            )
            isp_vac_eng = tp.engine_isp_with_gg_dump(isp_vac_chamber, cyc["gg_flow_fraction"],
                                                      GG_DUMP_ISP_FRACTION)
            isp_sl_eng = tp.engine_isp_with_gg_dump(isp_sl_chamber, cyc["gg_flow_fraction"],
                                                     GG_DUMP_ISP_FRACTION)
            _check(checklist, warnings, "turbopump", "Gas-generator flow-fraction plausibility",
                   cyc["gg_flow_fraction"] <= GG_FLOW_FRACTION_TYPICAL_MAX,
                   f"GG flow fraction {cyc['gg_flow_fraction']*100:.1f}% is unusually high (typical "
                   f"real GG-cycle engines bleed a few percent) - this chamber pressure/thrust "
                   f"combination is putting an unusually large burden on the turbopump relative to "
                   f"the main chamber, wasting a larger-than-normal share of propellant at reduced "
                   f"(dumped-exhaust) Isp.",
                   f"OK - {cyc['gg_flow_fraction']*100:.1f}% flow fraction")

        elif self.cycle == cycles.TAP_OFF:
            dp_fuel = pc_feed + dp_injector_fuel + jacket_dp_pa + line_loss_fuel_pa - TANK_HEAD_PA
            dp_ox = pc_feed + dp_injector_ox + line_loss_ox_pa - TANK_HEAD_PA
            # Tapped gas = main-chamber combustion products, film-cooled to a
            # turbine-tolerable temperature (NOT the fuel-rich GG mix).
            tap_tin_k = min(tc * TAP_OFF_TEMP_FRACTION, TAP_OFF_TURBINE_LIMIT_K)
            tap_gas = dict(tin_k=tap_tin_k, cp=combustion.mixture_cp_j_kgk(gamma, m_molar),
                           gamma=gamma)
            eta_pf, eta_po, eta_turb = turbopump_sizing.derive_efficiencies(
                mdot, self.mixture_ratio, dp_fuel, dp_ox, rho_fuel, rho_ox,
                self.turbopump_material_key, eff_staging, tap_gas["tin_k"], tap_gas["cp"],
                tap_gas["gamma"], TAP_OFF_PRESSURE_RATIO, TAP_OFF_PRESSURE_RATIO, build_quality,
                pump_stages_fuel=self.pump_stages_fuel, pump_stages_ox=self.pump_stages_ox,
                eta_pump_fuel_override=self.eta_pump_fuel, eta_pump_ox_override=self.eta_pump_ox,
                enforce_suction_limit=self.enforce_suction_limit, **_suction_kw)
            cyc = cycles.gas_generator_result(
                mdot, self.mixture_ratio, self.chamber_pressure_pa, dp_fuel, dp_ox,
                rho_fuel, rho_ox, eta_pf, eta_po, self.pump_specific_power_w_kg,
                tap_gas["tin_k"], tap_gas["cp"], eta_turb, TAP_OFF_PRESSURE_RATIO, tap_gas["gamma"],
                TAP_OFF_DUMP_ISP_FRACTION, cycle_name=cycles.TAP_OFF,
            )
            cyc["drive_gas"] = tap_gas
            isp_vac_eng = tp.engine_isp_with_gg_dump(isp_vac_chamber, cyc["gg_flow_fraction"],
                                                      TAP_OFF_DUMP_ISP_FRACTION)
            isp_sl_eng = tp.engine_isp_with_gg_dump(isp_sl_chamber, cyc["gg_flow_fraction"],
                                                     TAP_OFF_DUMP_ISP_FRACTION)
            _check(checklist, warnings, "turbopump", "Gas-generator flow-fraction plausibility",
                   cyc["gg_flow_fraction"] <= GG_FLOW_FRACTION_TYPICAL_MAX,
                   f"GG flow fraction {cyc['gg_flow_fraction']*100:.1f}% is unusually high (typical "
                   f"real GG-cycle engines bleed a few percent) - this chamber pressure/thrust "
                   f"combination is putting an unusually large burden on the turbopump relative to "
                   f"the main chamber, wasting a larger-than-normal share of propellant at reduced "
                   f"(dumped-exhaust) Isp.",
                   f"OK - {cyc['gg_flow_fraction']*100:.1f}% flow fraction")

        elif self.cycle in cycles.STAGED_CYCLES:
            # Closed staged combustion (FRSC / ORSC / FFSC): the preburner
            # temperature is a design input, the turbine PR is SOLVED so the drive
            # gas delivers the pump power, and each pump's discharge is built up
            # from the real pressure chain (main injector -> turbine -> preburner
            # injector -> jacket -> lines) - see staged_combustion.py's docstring.
            oxidizer_rich = self.cycle == cycles.ORSC

            def _staged_eff(dp_f, dp_o, gas, pr):
                return turbopump_sizing.derive_efficiencies(
                    mdot, self.mixture_ratio, dp_f, dp_o, rho_fuel, rho_ox,
                    self.turbopump_material_key, eff_staging, gas["tin_k"], gas["cp"],
                    gas["gamma"], pr, pr, build_quality,
                    pump_stages_fuel=self.pump_stages_fuel, pump_stages_ox=self.pump_stages_ox,
                    eta_pump_fuel_override=self.eta_pump_fuel,
                    eta_pump_ox_override=self.eta_pump_ox,
                    enforce_suction_limit=self.enforce_suction_limit, **_suction_kw)

            staged_balance = staged_combustion.solve_staged_power_balance(
                self.cycle, self.propellant_pair, mdot, self.mixture_ratio, pc_feed,
                dp_injector_fuel, dp_injector_ox, jacket_dp_pa, line_loss_fuel_pa,
                line_loss_ox_pa, TANK_HEAD_PA, rho_fuel, rho_ox,
                injector.dp_over_pc_nominal,   # preburner injector: same dP/P rule as the main one
                _staged_eff,
                tin_fuel_rich_k=max(0.0, float(self.preburner_tin_k or 0.0)),
                tin_ox_rich_k=max(0.0, float(self.ox_preburner_tin_k or 0.0)))
            dp_fuel = staged_balance["dp_fuel_pa"]
            dp_ox = staged_balance["dp_ox_pa"]
            eta_pf = staged_balance["eta_pump_fuel"]
            eta_po = staged_balance["eta_pump_ox"]
            eta_turb = staged_balance["eta_turbine"]
            cyc = staged_combustion.staged_combustion_result(
                self.cycle, self.propellant_pair, mdot, self.mixture_ratio, staged_balance,
                self.pump_specific_power_w_kg)
            drive_gas = cyc["drive_gas"]
            _pb_sides = ", ".join(
                f"{s['kind'].replace('_', '-')} PR {s['pr']:.2f} @ {s['gas']['tin_k']:.0f} K "
                f"(margin {s['power_available_w'] / max(s['power_required_w'], 1e-9):.2f})"
                for s in staged_balance["sides"])
            _check(checklist, warnings, "turbopump", "Staged-combustion power balance",
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
            _check(checklist, warnings, "turbopump", "Staged-combustion turbine PR / discharge plausibility",
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
            _check(checklist, warnings, "turbopump", "Preburner temperature vs turbine material",
                   _tin_hi <= _tp_mat.max_use_temp_k,
                   f"Preburner/turbine-inlet temperature {_tin_hi:.0f} K exceeds "
                   f"{_tp_mat.display_name}'s {_tp_mat.max_use_temp_k:.0f} K service limit - "
                   f"choose a hotter-capable turbopump material or a cooler preburner.",
                   f"OK - {_tin_hi:.0f} K vs {_tp_mat.max_use_temp_k:.0f} K limit")
            # Closed cycle: ALL preburner exhaust rejoins the main flow at the main
            # injector - no dump loss, so engine Isp is the chamber Isp directly. The
            # eta_cstar mixing penalty was already applied above per cycle.
            isp_vac_eng = isp_vac_chamber
            isp_sl_eng = isp_sl_chamber
            if self.cycle == cycles.ORSC:
                _check(checklist, warnings, "propellant/cycle", "ORSC turbine-material caution",
                       False,
                       "Oxidizer-rich staged combustion needs an oxidizer-resistant "
                       "turbine (hot O2-rich gas is highly corrosive/erosive) - "
                       "historically achieved reliably only by late-Soviet/Russian "
                       "engines (RD-170 family). Treat reliability figures as "
                       "optimistic for other eras/manufacturers.")
            elif self.cycle == cycles.FFSC:
                _check(checklist, warnings, "propellant/cycle", "FFSC development complexity",
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
            dp_fuel = ((pc_feed + dp_injector_fuel) * EXPANDER_TURBINE_PR + jacket_dp_pa
                       + line_loss_fuel_pa - TANK_HEAD_PA)
            dp_ox = pc_feed + dp_injector_ox + line_loss_ox_pa - TANK_HEAD_PA
            # Needs the nozzle profile for cooled-area, so this is computed further down
            # (after geo/profile) and cyc is filled in there; placeholder for now.
            cyc = None
            isp_vac_eng = isp_vac_chamber
            isp_sl_eng = isp_sl_chamber

        elif self.cycle == cycles.PRESSURE_FED:
            cyc = cycles.pressure_fed_result(pc_feed, dp_injector, LINE_LOSS_PA)
            isp_vac_eng = isp_vac_chamber
            isp_sl_eng = isp_sl_chamber
            _check(checklist, warnings, "turbopump", "Pressure-fed chamber pressure plausibility",
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
            dp_fuel = pc_feed + dp_injector_fuel + jacket_dp_pa + line_loss_fuel_pa - TANK_HEAD_PA
            dp_ox = pc_feed + dp_injector_ox + line_loss_ox_pa - TANK_HEAD_PA
            eta_pf, eta_po, eta_turb = turbopump_sizing.derive_efficiencies(
                mdot, self.mixture_ratio, dp_fuel, dp_ox, rho_fuel, rho_ox,
                self.turbopump_material_key, eff_staging, 300.0, 1000.0, 1.3,
                2.0, 2.0, build_quality,
                pump_stages_fuel=self.pump_stages_fuel, pump_stages_ox=self.pump_stages_ox,
                eta_pump_fuel_override=self.eta_pump_fuel, eta_pump_ox_override=self.eta_pump_ox,
                enforce_suction_limit=self.enforce_suction_limit, **_suction_kw)
            cyc = electric_pump.electric_pump_result(
                mdot, self.mixture_ratio, self.chamber_pressure_pa, dp_fuel, dp_ox,
                rho_fuel, rho_ox, eta_pf, eta_po, self.pump_specific_power_w_kg,
                BASE_RATED_BURN_TIME_S)
            isp_vac_eng = isp_vac_chamber
            isp_sl_eng = isp_sl_chamber

        else:
            raise ValueError(f"unknown cycle {self.cycle!r}; choices: {cycles.CYCLES}")

        thrust_vac = mdot * isp_vac_eng * G0
        thrust_sl = mdot * isp_sl_eng * G0
        thrust_vac_floor = thrust_vac * self.throttle_floor

        separated_100pct = iso.is_separated(pe_pa, PA_SEA_LEVEL, SEPARATION_K)

        conv_half_angle = self.convergent_half_angle_deg
        geo = geometry.chamber_geometry(mdot, cstar, self.chamber_pressure_pa,
                                         self.expansion_ratio, self.lstar_m, self.contraction_ratio,
                                         conv_half_angle, self.chamber_wall_fillet_r_over_rt,
                                         self.chamber_sizing_method, chamber_sizing_rt_s, tc, m_molar)
        _check(checklist, warnings, "chamber geometry",
               "L* sufficient for a cylindrical section at this contraction ratio",
               not geo["cylindrical_volume_clamped"],
               f"L* {self.lstar_m:.2f} m is too small for a cylindrical chamber "
               f"section at contraction ratio {self.contraction_ratio:.2f} - the "
               f"convergent cone alone already accounts for that much volume. "
               f"Chamber length clamped to the convergent section only.")
        _check(checklist, warnings, "chamber geometry", "Convergent half-angle within 20-45 deg",
               20.0 <= conv_half_angle <= 45.0,
               f"Convergent-cone half-angle {conv_half_angle:.0f} deg is outside the "
               f"[Huzel 4.3] 20-45 deg range.")

        # C1 - finite-contraction-ratio chamber pressure loss.
        _cf_loss_pct = chamber_flow["pc_loss_fraction"] * 100.0
        _check(checklist, warnings, "chamber geometry", "Contraction ratio performance margin",
               self.contraction_ratio >= 1.6,
               f"Contraction ratio {self.contraction_ratio:.2f} is tight: the chamber gas reaches "
               f"M~{chamber_flow['mach']:.2f}, so the injector-end stagnation pressure sits "
               f"~{_cf_loss_pct:.0f}% above the nozzle Pc [Sutton 8.2]. The pump/tank must "
               f"supply that higher pressure"
               + (" (being modelled - apply_chamber_pressure_loss on)."
                  if self.apply_chamber_pressure_loss
                  else " (not fed into feed pressure here - enable apply_chamber_pressure_loss)."),
               f"OK - injector-end Pc ~{chamber_flow['injector_end_pressure_ratio']:.3f}x nozzle Pc")

        # C2 - real stay time and chamber L/D.
        _rho_gas = (self.chamber_pressure_pa * m_molar / (8314.462 * tc)) if tc > 0 else 0.0
        stay_time_s = (geo["chamber_volume_m3"] * _rho_gas / mdot) if mdot > 0 and _rho_gas > 0 else 0.0
        chamber_l_over_d = (geo["chamber_length_m"] / geo["chamber_dia_m"]
                            if geo["chamber_dia_m"] > 0 else 0.0)
        _check(checklist, warnings, "chamber geometry", "Gas stay time within 1-40 ms",
               0.001 <= stay_time_s <= 0.040 or stay_time_s == 0.0,
               f"Combustion-gas stay time {stay_time_s*1e3:.1f} ms is outside the typical "
               f"1-40 ms band [Sutton 8.10] - {'too short, combustion may not complete' if stay_time_s < 0.001 else 'a very large chamber volume for this flow'}.",
               f"OK - {stay_time_s*1e3:.1f} ms")
        _check(checklist, warnings, "chamber geometry", "Chamber cylindrical L/D reasonable",
               0.3 <= chamber_l_over_d <= 2.5 or chamber_l_over_d == 0.0,
               f"Chamber cylindrical L/D {chamber_l_over_d:.2f} is "
               f"{'long/narrow (non-isentropic pressure loss, injector-hole crowding)' if chamber_l_over_d > 2.5 else 'short/wide (atomization zone eats the volume, mixing length too short)'} "
               f"[claude_lit topic 04].",
               f"OK - L/D {chamber_l_over_d:.2f}")

        xs_conv, rs_conv, x_throat, conv_len = geometry.convergent_profile(
            geo["chamber_dia_m"], geo["throat_dia_m"], geo["chamber_length_m"], conv_half_angle,
            self.chamber_wall_fillet_r_over_rt)
        if self.nozzle_type == "bell":
            div_len = nozzle_shapes.bell_length(geo["throat_dia_m"] / 2.0, geo["exit_dia_m"] / 2.0,
                                                 self.bell_percent_length)
            xs_div, rs_div, _ = nozzle_shapes.bell_profile_points(
                geo["throat_dia_m"] / 2.0, geo["exit_dia_m"] / 2.0, x_throat,
                theta_n_deg, theta_e_deg, div_len, n=30)
            xs = np.concatenate([xs_conv, xs_div[1:]])  # skip duplicate throat point
            rs = np.concatenate([rs_conv, rs_div[1:]])
            profile_meta = {"convergent_length_m": conv_len, "divergent_length_m": div_len,
                             "total_length_m": x_throat + div_len,
                             "theta_n_deg": theta_n_deg, "theta_e_deg": theta_e_deg}
        else:
            xs, rs, profile_meta = geometry.nozzle_profile(
                geo["chamber_dia_m"], geo["throat_dia_m"], geo["exit_dia_m"], geo["chamber_length_m"],
                conv_half_angle, self.nozzle_half_angle_deg,
                self.chamber_wall_fillet_r_over_rt,
            )

        if self.cycle == cycles.EXPANDER:
            eta_pf, eta_po, eta_turb = turbopump_sizing.derive_expander_efficiencies(
                mdot, self.mixture_ratio, dp_fuel, dp_ox, rho_fuel, rho_ox,
                self.turbopump_material_key, EXPANDER_TURBINE_PR, build_quality,
                pump_stages_fuel=self.pump_stages_fuel, pump_stages_ox=self.pump_stages_ox,
                eta_pump_fuel_override=self.eta_pump_fuel, eta_pump_ox_override=self.eta_pump_ox,
                enforce_suction_limit=self.enforce_suction_limit, **_suction_kw)
            cyc = expander.expander_result(
                self.propellant_pair, mdot, self.mixture_ratio, self.chamber_pressure_pa,
                dp_fuel, dp_ox, rho_fuel, rho_ox, eta_pf, eta_po,
                self.pump_specific_power_w_kg,
                xs, rs, geo["throat_dia_m"], cstar, mu_gas, cp_gas, pr_gas, t_aw_chamber_k,
                cutoff_area_ratio=cooled_length_eps, eta_turbine=eta_turb,
            )
            cyc["pump_discharge_fuel_pa"] = dp_fuel + TANK_HEAD_PA
            cyc["pump_discharge_ox_pa"] = dp_ox + TANK_HEAD_PA
            cyc["turbine_pressure_ratio"] = EXPANDER_TURBINE_PR
            _check(checklist, warnings, "expander", "Expander turbine power feasibility",
                   cyc["feasibility_margin"] >= 1.0,
                   f"Expander cycle is NOT feasible at this design point: available turbine "
                   f"power ({cyc['available_turbine_power_w']/1e3:.1f} kW) is only "
                   f"{cyc['feasibility_margin']*100:.0f}% of what the turbopump needs "
                   f"({cyc['required_turbine_power_w']/1e3:.1f} kW). Lower Pc/thrust, use a "
                   f"larger cooled nozzle area, or (most effectively) use LOX/LH2 - "
                   f"real expander-cycle engines (RL10, Vinci) are limited to modest "
                   f"thrust/Pc for exactly this reason.",
                   f"OK - {cyc['feasibility_margin']*100:.0f}% margin")
            _check(checklist, warnings, "expander",
                   "Expander propellant-pair realism (LOX/LH2 only)",
                   self.propellant_pair == "LOX/LH2",
                   "Expander cycle: no real engine has ever flown this propellant with this "
                   "cycle - LH2's heat capacity and coking resistance are specifically why "
                   "RL10/Vinci-class engines are LH2-only. A 'feasible' margin here reflects "
                   "this tool's simplified heat-budget proxy (it doesn't model coking chemistry "
                   "directly), not confirmation the combination is realistic.")

        throttle_grid = np.arange(max(self.throttle_floor, 0.05), 1.001, 0.02)
        rows = throttle.throttle_sweep(self.chamber_pressure_pa, pe_pc, PA_SEA_LEVEL,
                                        dp_injector, throttle_grid, SEPARATION_K)
        onset = throttle.separation_onset_throttle(rows)
        inj_ok = throttle.injector_stiffness_ok(rows, self.throttle_floor, injector.min_stable_dp_ratio)

        # --- gas-side heat transfer: real Bartz h_g -> computed wall temperature ---
        # A real Bartz gas-side coefficient (physics/cooling.py, fed by the
        # combustion-gas transport properties physics/combustion.py now derives)
        # gives the throat heat flux and a gas-side-only hot-wall temperature
        # from q = h_g*(T_aw - T_wg) [Huzel eq. 4-10/4-13]. How that becomes the
        # number the material thermal-margin check sees depends on the cooling
        # method:
        #   radiative  -> the wall really does run at the gas-side / radiation-
        #                 equilibrium temperature (no coolant loop).
        #   regen/dump -> the coolant PINS the wall down; it can't be hotter than
        #                 the gas-side-only value, and normally sits near the
        #                 max(cooling_effectiveness proxy, coolant-inlet + coolant
        #                 rise + through-wall conduction rise). This keeps the
        #                 proxy as a floor (no regression) while letting a genuinely
        #                 cool big/low-Pc wall earn margin and a low-conductivity
        #                 liner at high Pc lose it.
        #   ablative   -> keep the proxy (ablatives run hot by design and erode).
        eps_for_transition = min(self.cooling_transition_eps, self.expansion_ratio)
        mdot_fuel_kgs = mdot / (1.0 + self.mixture_ratio)
        mdot_ox_kgs = mdot - mdot_fuel_kgs
        # Flow actually passing through the regen jacket - under
        # f1_split_reverse_flow, manifold_bypass_fraction of the fuel goes
        # straight to the injector (never enters the jacket at all), matching
        # manifold.size_jacket_manifolds's own internal mdot_down formula
        # (duplicated here rather than imported, to avoid coupling into that
        # module's own concurrent development - see ASSUMPTIONS.md). All
        # OTHER mdot_fuel_kgs uses (injector geometry, manifold ring sizing,
        # dump cooling) correctly keep the FULL flow - all fuel reaches the
        # injector regardless of which path it took.
        mdot_coolant_jacket_kgs = (mdot_fuel_kgs * (1.0 - self.manifold_bypass_fraction)
                                    if self.cooling_flow_topology == "f1_split_reverse_flow"
                                    else mdot_fuel_kgs)

        # Computed-absolute Bartz flux profile (Phase 7) - AUTHORITATIVE. Real
        # per-station Bartz h_g (fed real combustion-gas transport properties),
        # calibrated per propellant class against real engines
        # (cooling.BARTZ_ABS_FLUX_CALIBRATION) rather than shape-normalised to
        # the old flat, propellant-agnostic area-average anchor - see that
        # constant's module comment for the LOX/RP-1-vs-LOX/LH2 finding that
        # drove the per-class (not flat) calibration.
        q_profile_w_m2 = cooling.absolute_heat_flux_profile(
            xs, rs, geo["throat_dia_m"], self.chamber_pressure_pa, cstar,
            mu_gas, cp_gas, pr_gas, t_aw_chamber_k, pair=self.propellant_pair,
            transition_area_ratio=cooled_length_eps)
        # Fuel-film cooling: a length-decaying curtain multiplier on the gas-side
        # flux (physics/cooling.film_effectiveness_profile) - strongest near the
        # injector face, recovering toward 1.0 down the nozzle - times the
        # optional nozzle-extension slot film (nozzle_film_effectiveness_profile).
        # An OVERLAY on every section method: the SAME film-reduced q profile feeds
        # the regen march, the dump sizing and the wall checks, so regen + film
        # genuinely interact. film_flux_factor is its cooled-zone area-average,
        # kept for the schematic / readout.
        film_phi, chamber_film_phi, nozzle_film_phi = self._film_phi(xs, rs, geo["throat_dia_m"])
        nozzle_film_active = bool(np.any(nozzle_film_phi < 1.0))
        q_profile_w_m2 = q_profile_w_m2 * film_phi
        film_flux_factor = cooling.area_weighted_mean(
            xs, rs, film_phi, throat_dia_m=geo["throat_dia_m"],
            transition_area_ratio=cooled_length_eps)
        q_throat_w_m2 = float(np.max(q_profile_w_m2))
        q_chamber_avg_w_m2 = cooling.area_weighted_mean(
            xs, rs, q_profile_w_m2, throat_dia_m=geo["throat_dia_m"],
            transition_area_ratio=cooled_length_eps)

        # Reported comparison ONLY: the pre-Phase-7 flat, propellant-agnostic
        # area-average anchor. Nothing downstream uses this any more.
        q_chamber_avg_anchor_w_m2 = (
            cooling.reference_area_avg_flux_w_m2(self.chamber_pressure_pa) * film_flux_factor)
        q_throat_abs_w_m2 = q_throat_w_m2                    # kept as an alias - same value now
        q_chamber_avg_abs_w_m2 = q_chamber_avg_w_m2          # kept as an alias - same value now

        hg_throat_w_m2k = cooling.bartz_hg(
            geo["throat_dia_m"], self.chamber_pressure_pa, cstar,
            mu_gas, cp_gas, pr_gas, area_ratio=1.0)
        # A film curtain lowers the EFFECTIVE adiabatic-wall (driving) temperature
        # the throat sees, not just the flux: T_aw,film = T_aw - eta_f*(T_aw - T_film),
        # with eta_f = 1 - film_phi at the throat and the film fuel entering near
        # its jacket-inlet temperature. Without this the mechanical q = h_g*(T_aw -
        # T_wg) inversion would read a HOTTER wall from a lower film-reduced flux.
        _throat_idx = int(np.argmin(rs))

        wall_heat_w = cooling.wall_heat_total_w(
            xs, rs, q_profile_w_m2, throat_dia_m=geo["throat_dia_m"],
            transition_area_ratio=cooled_length_eps)
        cp_fuel = cooling.FUEL_CP_J_KGK.get(self.propellant_pair)
        coolant_delta_t_k = cooling.coolant_temp_rise_k(wall_heat_w, mdot_coolant_jacket_kgs, cp_fuel)
        coolant_limit_k = cooling.coolant_limit_k(self.propellant_pair)
        coolant_inlet_k = COOLANT_INLET_TEMP_K.get(self.propellant_pair, 290.0)

        # Film fuel is tapped POST-JACKET (the F-1 curtain): with an active jacket
        # (regenerative / dump chamber) it enters at the jacket EXIT temperature -
        # the flat energy-balance estimate, since the flux profile (and so this
        # rise) doesn't depend on T_film; with no jacket it comes straight off the
        # fuel manifold at the inlet temperature. Per-station film T_aw feeds the
        # full-length wall balance; its throat value is the historical throat line.
        _t_film_k = coolant_inlet_k + (
            coolant_delta_t_k if chamber_cooling in ("regenerative", "dump") else 0.0)
        t_aw_film_profile_k = (cooling.film_adiabatic_wall_temp(t_aw_chamber_k, film_phi, _t_film_k)
                               if np.any(film_phi < 1.0)
                               else np.full(len(xs), float(t_aw_chamber_k)))
        t_aw_throat_k = float(t_aw_film_profile_k[_throat_idx])
        t_wg_gas_side_k = cooling.wall_gas_temperature(q_throat_w_m2, hg_throat_w_m2k, t_aw_throat_k)

        # Coolant-channel march on the REAL contour + film factor (authoritative
        # for the coolant-side wall temp and coolant dT; the pump-feed chain
        # above already used the cheap early estimate). Regenerative "channels"
        # mode only - otherwise coolant_march stays None and the legacy proxy runs.
        coolant_march = None
        channel_geometry = None
        if (self.regen_channel_model == "channels"
                and chamber_cooling == "regenerative"):
            if two_pass:
                coolant_march = cooling.march_coolant_two_pass(
                    xs, rs, q_profile_w_m2, geo["throat_dia_m"], mdot_coolant_jacket_kgs,
                    self.propellant_pair, inlet_area_ratio=jacket_inlet_eps_eff,
                    n_channels=self.regen_channel_count,
                    aspect_ratio=self.regen_channel_aspect_ratio,
                    target_velocity_ms=self.regen_coolant_velocity_ms,
                    land_fraction=self.regen_channel_land_fraction,
                    transition_area_ratio=cooled_length_eps, t_inlet_k=coolant_inlet_k,
                    construction=self.wall_construction)
            else:
                coolant_march = cooling.march_coolant(
                    xs, rs, q_profile_w_m2, geo["throat_dia_m"], mdot_coolant_jacket_kgs,
                    self.propellant_pair, n_channels=self.regen_channel_count,
                    aspect_ratio=self.regen_channel_aspect_ratio,
                    target_velocity_ms=self.regen_coolant_velocity_ms,
                    land_fraction=self.regen_channel_land_fraction,
                    transition_area_ratio=cooled_length_eps, t_inlet_k=coolant_inlet_k,
                    construction=self.wall_construction, split_eps=split_eps_eff)
            coolant_delta_t_k = coolant_march["coolant_delta_t_k"]
            # Per-station channel geometry across the WHOLE contour, for the 3D
            # preview's rib pattern only - re-derives n_channels/channel_height
            # the identical way march_coolant did internally (channel_count/
            # channel_target_height_m), then a separate additive function
            # (channel_geometry_profile) fans that out per station. Doesn't
            # feed any lumped number above; coolant_march's own outputs are
            # already final by this point.
            _n_ch_visual = cooling.channel_count(geo["throat_dia_m"], self.regen_channel_count)
            _land_fraction_visual = (self.regen_channel_land_fraction
                                     if self.regen_channel_land_fraction > 0
                                     else cooling.CHANNEL_LAND_FRACTION_DEFAULT)
            _channel_height_visual, _ = cooling.channel_target_height_m(
                geo["throat_dia_m"], _n_ch_visual, mdot_coolant_jacket_kgs, self.propellant_pair,
                _land_fraction_visual, aspect_ratio_override=self.regen_channel_aspect_ratio,
                target_velocity_ms=self.regen_coolant_velocity_ms)
            channel_geometry = cooling.channel_geometry_profile(
                xs, rs, _n_ch_visual, _channel_height_visual, _land_fraction_visual,
                throat_dia_m=geo["throat_dia_m"], split_eps=split_eps_eff)

        # NOTE (2026-09-17): f1_split_reverse_flow's bypassed flow used to be
        # handled by a post-hoc rescale here (coolant_delta_t_k divided by
        # (1-bypass_fraction) after the fact). That's gone - mdot_coolant_jacket_kgs
        # (defined above, near mdot_fuel_kgs) now feeds the REAL reduced down-
        # leg flow directly into both the flat-mode proxy and the authoritative
        # march_coolant() call, so coolant_delta_t_k (and, new this round,
        # t_wc_throat_k/jacket_dp_pa/n_channels/channel_dh_throat_m - previously
        # untouched by the old rescale) all now correctly reflect the real
        # reduced flow from the source, not an approximation applied afterward.
        # Still a simplification, unchanged from before: this models the down-
        # leg and return-leg as one combined thermal unit sharing the same wall
        # heat-flux profile/channel geometry (one march_coolant() call, one
        # direction), not two independently-modeled interleaved streams - see
        # ASSUMPTIONS.md and regen_circuit_style's own TODO for that larger gap.

        # Through-wall conduction rise across a representative hot-wall land
        # (physics/materials.through_wall_delta_t_k - the first real use of a
        # material's thermal conductivity). Also feeds the fatigue check below.
        throat_hoop_thickness_m = mass_model.wall_thickness_m(
            self.chamber_pressure_pa, geo["throat_dia_m"] / 2.0,
            chamber_material.allowable_stress_pa)
        throat_wall_thickness_m = min(throat_hoop_thickness_m, REGEN_HOT_WALL_THICKNESS_M)
        through_wall_delta_t_k = materials.through_wall_delta_t_k(
            q_throat_w_m2, throat_wall_thickness_m, chamber_material.thermal_conductivity_w_mk)


        # Nozzle-extension material at cooling_transition_eps. For a RADIATIVELY
        # cooled extension (no coolant loop) the real check is the radiation-
        # equilibrium wall temperature - h_gc*(T_aw - T_wg) balanced against
        # emissivity*sigma*T_wg^4 [Huzel eq. 4-38] - not just the local gas
        # temperature. An actively-cooled extension keeps the local-gas-static
        # basis (much cooler than Tc this far down the nozzle).
        mach_transition = iso.mach_from_area_ratio(eps_for_transition, gamma)
        t_local = tc * iso.static_temperature_ratio(mach_transition, gamma)
        bell_wall_temp_k = None
        bell_wall_temp_eps = None
        if nozzle_cooling in ("radiative", "uncooled"):
            t_aw_local_k = t_local + cooling.RECOVERY_FACTOR * (tc - t_local)
            hg_local_w_m2k = cooling.bartz_hg(
                geo["throat_dia_m"], self.chamber_pressure_pa, cstar,
                mu_gas, cp_gas, pr_gas, area_ratio=max(eps_for_transition, 1.0))
            bell_wall_temp_k = cooling.radiative_wall_temperature(
                hg_local_w_m2k, t_aw_local_k, bell_material.emissivity)
            bell_wall_temp_eps = eps_for_transition
            # Film overlay on a passive extension (the F-1 architecture): the film
            # lowers the local driving temperature, T_aw,film = T_aw - eta_f*(T_aw -
            # T_film) - the same T_aw-only convention as the coupled wall balance -
            # and it DECAYS downstream, so the hottest point can move off the
            # transition station. Evaluate every extension station and keep the
            # worst. No film anywhere on the extension -> the single-point check
            # above, unchanged.
            _rt_b = geo["throat_dia_m"] / 2.0
            _thr_b = int(np.argmin(rs))
            _eps_st = (np.asarray(rs) / _rt_b) ** 2
            _ext = [i for i in range(_thr_b + 1, len(rs)) if _eps_st[i] >= eps_for_transition]
            _ext_eps = np.concatenate([[eps_for_transition], _eps_st[_ext]])
            # each point takes its own station's film value; the transition point
            # takes the first extension station's (a slot AT the transition covers
            # it, one further downstream doesn't) - no interpolation across the slot
            _fp = np.asarray(film_phi)
            _ext_phi = (np.concatenate([[_fp[_ext[0]]], _fp[_ext]]) if _ext
                        else np.ones(1))
            if np.any(_ext_phi < 1.0):
                bell_wall_temp_k = None
                for _e, _ph in zip(_ext_eps, _ext_phi):
                    _m = iso.mach_from_area_ratio(max(float(_e), 1.0 + 1e-9), gamma)
                    _tl = tc * iso.static_temperature_ratio(_m, gamma)
                    _taw = cooling.film_adiabatic_wall_temp(
                        _tl + cooling.RECOVERY_FACTOR * (tc - _tl), float(_ph), _t_film_k)
                    _hg = cooling.bartz_hg(geo["throat_dia_m"], self.chamber_pressure_pa, cstar,
                                           mu_gas, cp_gas, pr_gas, area_ratio=max(float(_e), 1.0))
                    _tw = cooling.radiative_wall_temperature(_hg, _taw, bell_material.emissivity)
                    if bell_wall_temp_k is None or _tw > bell_wall_temp_k:
                        bell_wall_temp_k, bell_wall_temp_eps = _tw, float(_e)
        bell_material_margin = materials.thermal_margin(
            self.bell_material_key, t_local, wall_temp_k=bell_wall_temp_k)
        _bell_basis = ((f"radiative equilibrium ~{bell_wall_temp_k:.0f} K"
                        + (f" (hottest extension station, eps {bell_wall_temp_eps:.1f}, "
                           f"with film)" if bell_wall_temp_eps != eps_for_transition else ""))
                       if bell_wall_temp_k is not None else f"local gas T {t_local:.0f} K")
        _check(checklist, warnings, "materials", "Nozzle-extension material thermal margin",
               not bell_material_margin["warning"],
               f"[nozzle extension] {bell_material_margin['warning']}",
               f"OK - {bell_material_margin['margin_ratio']:.2f}x margin ({_bell_basis})")

        # --- coolant-side capacity, regen Isp credit, throat fatigue life ---
        # (wall_heat_w / coolant_delta_t_k / through_wall_delta_t_k were computed
        # above for the material thermal-margin check.)
        jet_power_w = 0.5 * mdot * cstar ** 2
        wall_heat_energy_fraction = wall_heat_w / jet_power_w if jet_power_w > 0 else 0.0
        regen_cooled = chamber_cooling == "regenerative"
        regen_ok = (not regen_cooled) or cooling.regen_feasible(coolant_delta_t_k, self.propellant_pair)
        limit_txt = (f"~{coolant_limit_k:.0f} K" if coolant_limit_k is not None
                     else "the coking/boiling")
        regen_pass_detail = (f"OK - ~{coolant_delta_t_k:.0f} K coolant rise" if regen_cooled
                             else f"n/a - {chamber_cooling} cooling")
        _check(checklist, warnings, "cooling", "Regen jacket coolant capacity",
               regen_ok,
               f"Regen-jacket coolant temperature rise (~{coolant_delta_t_k:.0f} K) exceeds "
               f"{limit_txt} limit for {self.propellant_pair}: this chamber pressure/size drives "
               f"more heat into the wall than the fuel flow can carry away. Add film-cooling "
               f"assist, lower Pc, or move the cooling transition earlier.",
               regen_pass_detail)

        # Throat low-cycle thermal fatigue: the hot face runs hotter than the
        # coolant side by through_wall_delta_t_k (across a ~1 mm channel-wall
        # land, not the full hoop thickness); that gradient yields the wall every
        # firing and cracks it over enough start/stop cycles - the SSME throat
        # story. Only meaningful for an ACTIVELY cooled metal wall (a big
        # through-wall gradient held cycle after cycle); ablative liners char/
        # erode and radiative walls run near-isothermal, so the check is skipped
        # for those (the numbers are still reported). Warn-not-block.
        throat_thermal_stress_pa = mass_model.thermal_stress_pa(
            through_wall_delta_t_k, chamber_material.youngs_modulus_pa, chamber_material.cte_per_k)
        throat_fatigue_cycles = mass_model.low_cycle_fatigue_cycles(
            throat_thermal_stress_pa, chamber_material.youngs_modulus_pa)
        fatigue_threshold = max(self.ignitions * FATIGUE_CYCLE_MARGIN, FATIGUE_CYCLE_FLOOR)
        fatigue_relevant = chamber_cooling in ("regenerative", "dump")
        _check(checklist, warnings, "cooling", "Throat thermal-fatigue cycle life",
               (not fatigue_relevant) or throat_fatigue_cycles >= fatigue_threshold,
               f"Estimated throat low-cycle thermal-fatigue life ~{throat_fatigue_cycles:,.0f} "
               f"cycles (through-wall dT ~{through_wall_delta_t_k:.0f} K -> thermal stress "
               f"~{throat_thermal_stress_pa/1e6:.0f} MPa) is thin next to {self.ignitions} "
               f"planned ignition(s). A high-Pc regen throat is life-limited by cracking - "
               f"lower Pc, add film cooling, or a more fatigue-resistant liner.",
               (f"OK - ~{throat_fatigue_cycles:,.0f} thermal cycles" if fatigue_relevant
                else f"n/a - {chamber_cooling} cooling"))

        # Regenerative Isp credit [Sutton 8.2]: only for a PUMP-FED regen chamber
        # (a pressure-fed engine has no head budget for a full-flow jacket, and
        # the propellant-pair Isp spot checks all run pressure-fed - so those
        # stay bit-for-bit unchanged). Applied to the engine Isp after the cycle
        # branch, so mdot (from isp_vac_chamber) is untouched; thrust is bumped.
        regen_isp_bonus = (
            cooling.regen_isp_bonus_fraction(coolant_delta_t_k, self.propellant_pair)
            if regen_cooled and cyc["has_turbopump"] else 0.0)
        if regen_isp_bonus > 0.0:
            isp_vac_eng *= (1.0 + regen_isp_bonus)
            isp_sl_eng *= (1.0 + regen_isp_bonus)
            thrust_vac = mdot * isp_vac_eng * G0
            thrust_sl = mdot * isp_sl_eng * G0
            thrust_vac_floor = thrust_vac * self.throttle_floor

        # Dump cooling (nozzle extension only - real engines dump-cool skirts, not
        # main chambers): a small coolant bleed absorbs the nozzle-extension's
        # wall heat and is ejected overboard at the lip instead of returning to
        # the injector - Vulcain HM-60 / J-2 style. Sized (or user-pinned via
        # dump_coolant_fraction) to hold that slice's coolant dT within the pair's
        # coking/boiling limit, with a net Isp penalty for ejecting it at a lower
        # effective specific impulse than the core exhaust. No penalty (and no
        # cooled slice) unless regen_nozzle_end_eps has actually extended cooling
        # past the material transition - see that field's comment.
        dump_coolant_fraction_eff = 0.0
        dump_mdot_kgs = 0.0
        dump_coolant_dt_k = 0.0
        dump_isp_penalty_fraction = 0.0
        if nozzle_cooling == "dump" and cooled_length_eps > eps_for_transition:
            wall_heat_ext_w = max(0.0, wall_heat_w - cooling.wall_heat_total_w(
                xs, rs, q_profile_w_m2, throat_dia_m=geo["throat_dia_m"],
                transition_area_ratio=eps_for_transition))
            dump_limit_k = cooling.coolant_limit_k(self.propellant_pair) or 200.0
            dump_coolant_fraction_eff = (
                self.dump_coolant_fraction if self.dump_coolant_fraction > 0.0
                else cooling.size_dump_coolant_fraction(
                    wall_heat_ext_w, mdot_fuel_kgs, cp_fuel, dump_limit_k))
            dump_mdot_kgs = dump_coolant_fraction_eff * mdot_fuel_kgs
            dump_coolant_dt_k = cooling.coolant_temp_rise_k(wall_heat_ext_w, dump_mdot_kgs, cp_fuel)
            dump_isp_penalty_fraction = cooling.dump_cooling_isp_penalty_fraction(dump_mdot_kgs, mdot)
        if dump_isp_penalty_fraction > 0.0:
            isp_vac_eng *= (1.0 - dump_isp_penalty_fraction)
            isp_sl_eng *= (1.0 - dump_isp_penalty_fraction)
            thrust_vac = mdot * isp_vac_eng * G0
            thrust_sl = mdot * isp_sl_eng * G0
            thrust_vac_floor = thrust_vac * self.throttle_floor
        dump_ok = (dump_coolant_dt_k <= 0.0
                  or dump_coolant_dt_k <= (cooling.coolant_limit_k(self.propellant_pair) or 1e9))
        _check(checklist, warnings, "cooling", "Dump-cooled nozzle coolant capacity",
               dump_ok,
               f"Dump-cooled nozzle coolant temperature rise (~{dump_coolant_dt_k:.0f} K) exceeds "
               f"the coking/boiling limit for {self.propellant_pair}: raise dump_coolant_fraction "
               f"or shorten the dump-cooled slice (lower regen_nozzle_end_eps).",
               (f"OK - ~{dump_coolant_dt_k:.0f} K coolant rise, {dump_coolant_fraction_eff*100:.1f}% "
                f"of fuel, Isp penalty {dump_isp_penalty_fraction*100:.2f}%"
                if nozzle_cooling == "dump" and cooled_length_eps > eps_for_transition
                else "n/a - no dump-cooled nozzle slice"))

        # Nozzle-extension slot film: post-jacket fuel injected on the supersonic
        # wall never burns in the chamber, so - like dump flow - it is costed as a
        # low-velocity stream that recovers only DUMP_THRUST_RECOVERY_FRACTION of
        # the core Isp (the same physics as the F-1's turbine-exhaust film), not
        # as a c* loss. The chamber curtain keeps its c* penalty (it does burn,
        # off-mixture-ratio, inside the chamber - see eta_cstar above).
        nozzle_film_isp_penalty_fraction = 0.0
        if nozzle_film_active:
            nozzle_film_isp_penalty_fraction = cooling.dump_cooling_isp_penalty_fraction(
                self.nozzle_film_fraction * mdot_fuel_kgs, mdot)
            isp_vac_eng *= (1.0 - nozzle_film_isp_penalty_fraction)
            isp_sl_eng *= (1.0 - nozzle_film_isp_penalty_fraction)
            thrust_vac = mdot * isp_vac_eng * G0
            thrust_sl = mdot * isp_sl_eng * G0
            thrust_vac_floor = thrust_vac * self.throttle_floor
        _slot_eps = self.nozzle_film_inject_eps
        _slot_ok = (self.nozzle_film_fraction <= 0.0 or nozzle_film_active)
        _check(checklist, warnings, "cooling", "Nozzle film slot on the nozzle wall",
               _slot_ok,
               f"Nozzle film slot at eps {_slot_eps:.1f} is not on the supersonic nozzle "
               f"(needs 1 < eps < {self.expansion_ratio:.1f}) - the "
               f"{self.nozzle_film_fraction*100:.1f}% slot film is ignored.",
               (f"OK - {self.nozzle_film_fraction*100:.1f}% of fuel as a slot film at eps "
                f"{_slot_eps:.1f}, Isp cost {nozzle_film_isp_penalty_fraction*100:.2f}%"
                if nozzle_film_active else "n/a - no nozzle slot film"))
        _film_total = max(0.0, self.film_cooling_fraction) + (
            max(0.0, self.nozzle_film_fraction) if nozzle_film_active else 0.0)
        _check(checklist, warnings, "cooling", "Total film-coolant fraction plausible",
               _film_total <= FILM_TOTAL_FRACTION_WARN,
               f"Total film coolant is {_film_total*100:.1f}% of the fuel flow (chamber curtain "
               f"+ nozzle slot) - above ~{FILM_TOTAL_FRACTION_WARN*100:.0f}% the c*/Isp cost "
               f"usually outweighs the cooling; real engines run ~2-12% (F-1 ~10-12%).",
               f"OK - {_film_total*100:.1f}% of fuel as film" if _film_total > 0.0
               else "n/a - no film cooling")

        # Injector element geometry (physics/injectors.py) + chamber acoustic
        # modes (physics/combustion_stability.py) - detail for the Injectors tab.
        injector_geometry = injectors.element_geometry(
            mdot_fuel_kgs, mdot_ox_kgs, rho_fuel, rho_ox, dp_injector, self.injector_type,
            cd=orifice_cd, dp_fuel_pa=dp_injector_fuel, dp_ox_pa=dp_injector_ox,
            included_angle_deg=self.impingement_angle_deg)

        # Propellant intake manifold sizing (physics/manifold.py) - real
        # cross-section from mdot/density/target feed velocity, mass from
        # hoop stress against the actual local feed pressure (pc_feed + this
        # leg's injector dP - NOT pump discharge pressure, which is
        # upstream of the manifold and undefined on the pressure-fed branch).
        # Each ring's velocity puts its dynamic head at the user's fraction
        # of that leg's own injector dP (manifold.velocity_from_head_fraction).
        fuel_feed_velocity_ms = manifold.velocity_from_head_fraction(
            self.fuel_manifold_head_fraction, dp_injector_fuel, rho_fuel)
        ox_feed_velocity_ms = manifold.velocity_from_head_fraction(
            self.ox_manifold_head_fraction, dp_injector_ox, rho_ox)
        # Each header ring's taper INLET follows the user's pipe: the first
        # plumbing run rooted on that host sets its inlet angle (else the
        # defaults - fuel 0, ox 180, jacket 0).
        _inlet_angles = {}
        for _rd in (self.plumbing_runs or []):
            _r0 = plumbing.run_from_dict(_rd)
            if _r0.pipes and _r0.host not in _inlet_angles:
                _inlet_angles[_r0.host] = float(_r0.attach_angle_deg)
        manifold_result = manifold.size_manifolds(
            mdot_fuel_kgs, mdot_ox_kgs, rho_fuel, rho_ox, pc_feed,
            dp_injector_fuel, dp_injector_ox, geo["chamber_dia_m"],
            feed_velocity_target_ms={"fuel": fuel_feed_velocity_ms,
                                      "ox": ox_feed_velocity_ms},
            taper_blend={"fuel": self.fuel_manifold_taper_blend,
                         "ox": self.ox_manifold_taper_blend},
            inlet_angles_deg={k: v for k, v in _inlet_angles.items() if k in ("fuel", "ox")})
        manifold_mass_kg = manifold_result["total_mass_kg"]
        _fuel_thin_warn = manifold.thin_wall_warning(
            manifold_result["fuel"]["thin_wall_ratio"], "Fuel")
        _check(checklist, warnings, "manifold", "Fuel manifold thin-wall approximation validity",
               not _fuel_thin_warn, _fuel_thin_warn or "",
               f"OK - t/r {manifold_result['fuel']['thin_wall_ratio']:.2f}")
        _ox_thin_warn = manifold.thin_wall_warning(
            manifold_result["ox"]["thin_wall_ratio"], "Ox")
        _check(checklist, warnings, "manifold", "Ox manifold thin-wall approximation validity",
               not _ox_thin_warn, _ox_thin_warn or "",
               f"OK - t/r {manifold_result['ox']['thin_wall_ratio']:.2f}")
        _fuel_bore_warn = manifold.bore_vs_chamber_warning(
            manifold_result["fuel"]["inner_diameter_m"], geo["chamber_dia_m"], "Fuel")
        _check(checklist, warnings, "manifold", "Fuel manifold bore vs. chamber packaging",
               not _fuel_bore_warn, _fuel_bore_warn or "", "OK")
        _ox_bore_warn = manifold.bore_vs_chamber_warning(
            manifold_result["ox"]["inner_diameter_m"], geo["chamber_dia_m"], "Ox")
        _check(checklist, warnings, "manifold", "Ox manifold bore vs. chamber packaging",
               not _ox_bore_warn, _ox_bore_warn or "", "OK")
        _fuel_lh2 = self.propellant_pair == "LOX/LH2"
        _fuel_vel_warn = manifold.velocity_cap_warning(fuel_feed_velocity_ms, "Fuel",
                                                        supercritical=_fuel_lh2)
        _check(checklist, warnings, "manifold", "Fuel manifold feed velocity vs. SP-8087 limit",
               not _fuel_vel_warn, _fuel_vel_warn or "",
               f"OK - {fuel_feed_velocity_ms:.1f} m/s"
               + (" (LH2: SP-8087 liquid limit n/a, gas Mach criterion not modelled)"
                  if _fuel_lh2 else ""))
        _ox_vel_warn = manifold.velocity_cap_warning(ox_feed_velocity_ms, "Ox")
        _check(checklist, warnings, "manifold", "Ox manifold feed velocity vs. SP-8087 limit",
               not _ox_vel_warn, _ox_vel_warn or "",
               f"OK - {ox_feed_velocity_ms:.1f} m/s")

        # Regen-cooling JACKET's own coolant-supply ring(s) (physics/manifold.
        # size_jacket_manifolds) - distinct from the injector-feed rings just
        # above. jacket_inlet_pressure_pa reuses the same formula already used
        # by the jacket-overpressure check further down (pc_feed + injector dP
        # + jacket_dp_pa - "the JACKET-INLET pressure...matching real counter-
        # flow regen routing"), computed here unconditionally rather than only
        # inside that check's own gated block. jacket_return_pressure_pa is
        # lower by the down-leg's own (Tier-3, arbitrary-symmetric-split) share
        # of the jacket's total pressure drop - only meaningful/used under
        # f1_split_reverse_flow. cooled_length_eps (not eps_for_transition -
        # see that field's own comment for why they can differ) is split out
        # separately here rather than reusing the mass-rollup section's own
        # split (further down, split at a DIFFERENT eps) - see ASSUMPTIONS.md.
        jacket_inlet_pressure_pa = pc_feed + dp_injector_fuel + jacket_dp_pa
        # Share of the jacket dP spent before the return/turnaround ring: the
        # two-pass march's REAL down-pass share when it ran; the Tier-3
        # symmetric split otherwise (f1_split_reverse_flow, or flat mode).
        _march_for_split = coolant_march or coolant_march_pre
        if (two_pass and _march_for_split and _march_for_split.get("jacket_dp_pa", 0) > 0
                and "jacket_dp_down_pa" in _march_for_split):
            jacket_return_split_fraction = (_march_for_split["jacket_dp_down_pa"]
                                            / _march_for_split["jacket_dp_pa"])
        else:
            jacket_return_split_fraction = manifold.JACKET_RETURN_SPLIT_FRACTION
        jacket_return_pressure_pa = (jacket_inlet_pressure_pa
                                      - jacket_dp_pa * jacket_return_split_fraction)

        # --- Chamber material thermal margin (throat hot-gas wall) ---
        # Sits here, below the jacket pressures, so the coupled solve can size
        # the tube wall it conducts through the same way the jacket-overpressure
        # check does. What the check compares depends on the cooling method:
        #   radiative  -> the gas-side / radiation-equilibrium temperature.
        #   regen, "channels" model (a real coolant march ran) -> COUPLED series-
        #                 resistance balance (cooling.solve_wall_balance): gas film
        #                 -> wall -> coolant film -> bulk coolant, all at the throat.
        #                 The wall temperature responds to coolant velocity (h_c),
        #                 wall thickness and conductivity. Gas side = raw Bartz h_g
        #                 x the per-class flux calibration x the carbon-deposit
        #                 credit (cooling.GAS_SIDE_DEPOSIT_FACTOR, RP-1 only).
        #   regen "flat" / dump -> legacy: the coolant pins the wall no
        #                 hotter than the gas-side value, floored by the
        #                 cooling_effectiveness proxy (unchanged, so every flat-mode
        #                 spot check stays bit-identical).
        #   ablative   -> proxy (ablatives run hot by design and erode).
        # The integrated flux profile, coolant dT and fatigue dT are NOT re-derived
        # from the coupled flux (documented Tier-3 inconsistency, ASSUMPTIONS.md).
        chamber_heat_flux_factor = materials.contraction_ratio_heat_flux_factor(self.contraction_ratio)
        cool_method = chamber_cooling
        hot_wall_thickness_m = throat_wall_thickness_m
        h_g_throat_effective_w_m2k = None
        t_wc_throat_coupled_k = None
        q_throat_wall_balance_w_m2 = None
        coolant_velocity_throat_ms = None
        if cool_method in ("radiative", "uncooled"):
            # No active coolant loop - the wall runs at the gas-side-only temp.
            t_wg_throat_k = t_wg_gas_side_k
        elif cool_method in ("regenerative", "dump") and coolant_march is not None:
            deposit_factor = cooling.GAS_SIDE_DEPOSIT_FACTOR.get(self.propellant_pair, 1.0)
            h_g_throat_effective_w_m2k = (
                hg_throat_w_m2k
                * cooling.BARTZ_ABS_FLUX_CALIBRATION.get(self.propellant_pair, 1.0)
                * deposit_factor)
            if self.wall_construction == "tube_wall":
                # Same min-combined-stress tube wall the jacket-overpressure check
                # sizes at the throat (tube radius, net coolant-vs-Pc differential
                # at the topology's jacket pressure) - a thinner tube runs cooler.
                _jp_throat_pa = (jacket_return_pressure_pa
                                 if self.cooling_flow_topology in ("f1_split_reverse_flow",
                                                                   "j2_mid_nozzle_inlet")
                                 else jacket_inlet_pressure_pa)
                _r_tube_throat_m = cooling.channel_hydraulic_geometry(
                    geo["throat_dia_m"],
                    cooling.channel_count_at_station(_n_ch_visual, 1.0, split_eps_eff),
                    _channel_height_visual, _land_fraction_visual)["dh_m"] / 2.0
                _k_per_m = (mass_model.thermal_stress_pa(
                    q_throat_w_m2 / chamber_material.thermal_conductivity_w_mk,
                    chamber_material.youngs_modulus_pa, chamber_material.cte_per_k,
                    nu=mass_model.POISSON_RATIO)
                    if chamber_material.thermal_conductivity_w_mk > 0 else 0.0)
                hot_wall_thickness_m, _ = mass_model.min_combined_stress_thickness_m(
                    _jp_throat_pa - self.chamber_pressure_pa, _r_tube_throat_m, _k_per_m,
                    mass_model.TUBE_WALL_MIN_THICKNESS_M, REGEN_HOT_WALL_THICKNESS_M)
            t_wg_throat_k, t_wc_throat_coupled_k, q_throat_wall_balance_w_m2 = (
                cooling.solve_wall_balance(
                    h_g_throat_effective_w_m2k, t_aw_throat_k,
                    coolant_march["h_c_throat_w_m2k"], coolant_march["t_bulk_throat_k"],
                    hot_wall_thickness_m, chamber_material.thermal_conductivity_w_mk))
            coolant_velocity_throat_ms = coolant_march["v_throat_ms"]
        elif cool_method in ("regenerative", "dump"):
            proxy_k = tc * chamber_material.cooling_effectiveness * chamber_heat_flux_factor
            coolant_side_k = coolant_inlet_k + coolant_delta_t_k + through_wall_delta_t_k
            t_wg_throat_k = min(t_wg_gas_side_k, max(proxy_k, coolant_side_k))
        else:  # ablative - proxy path (fallback), erodes rather than melts
            t_wg_throat_k = None

        margin = materials.thermal_margin(self.material_key, tc,
                                          heat_flux_factor=chamber_heat_flux_factor,
                                          wall_temp_k=t_wg_throat_k)
        if h_g_throat_effective_w_m2k is not None:
            _deposit_txt = (" incl. carbon-deposit credit"
                            if cooling.GAS_SIDE_DEPOSIT_FACTOR.get(self.propellant_pair, 1.0) < 1.0
                            else "")
            _margin_basis = (
                f"coupled throat wall balance: gas h_g ~{h_g_throat_effective_w_m2k/1e3:.1f} "
                f"kW/m2K{_deposit_txt}, coolant ~{coolant_velocity_throat_ms:.0f} m/s "
                f"(h_c ~{coolant_march['h_c_throat_w_m2k']/1e3:.1f} kW/m2K, coolant-side wall "
                f"~{t_wc_throat_coupled_k:.0f} K), {hot_wall_thickness_m*1e3:.2f} mm wall")
            _margin_fail = ((margin["warning"] or "") + f" Basis: {_margin_basis}. Levers "
                            f"that lower it: faster coolant (Coolant velocity; SP-8087 caps "
                            f"liquids at ~61 m/s, at a jacket-dP cost), a thinner wall, a "
                            f"liner rated hotter or more conductive (e.g. GRCop-84), or more "
                            f"film cooling.")
        else:
            _margin_basis = (f"computed wall temp ~{t_wg_throat_k:.0f} K vs T_aw {t_aw_chamber_k:.0f} K"
                             if t_wg_throat_k is not None
                             else f"proxy (ablative), CR heat-flux factor {chamber_heat_flux_factor:.2f}x")
            _margin_fail = margin["warning"] or ""
        if chamber_cooling != chamber_material.cooling_method:
            _margin_basis += (f"; explicit {chamber_cooling} cooling on a "
                              f"{chamber_material.cooling_method}-spec liner")
        _check(checklist, warnings, "materials", "Chamber material thermal margin",
               not margin["warning"], _margin_fail,
               f"OK - {margin['margin_ratio']:.2f}x margin ({_margin_basis})")

        # Full-length coupled wall balance ("channels" regen only): the throat
        # series-resistance balance above, repeated at EVERY cooled station with
        # that station's calibrated Bartz h_g (x the same carbon-deposit credit),
        # its film-lowered T_aw (both film sites), and the march's local coolant
        # h_c / bulk temperature. This is where the chamber curtain's barrel
        # protection - and a convergent film ring's shift of it - actually shows.
        # Warn-only NEW row: the throat margin row above, the rated burn time and
        # the fatigue check stay throat-based (so every spot check is unchanged).
        # Tier 3: one wall thickness (the throat's) and single-phase coolant
        # everywhere; the march's flux is not re-derived from the coupled one.
        t_wg_profile_k = None
        peak_wall_temp_k = None
        peak_wall_temp_zone = None
        peak_wall_temp_eps = None
        peak_wall_margin_ratio = None
        if h_g_throat_effective_w_m2k is not None and "h_c_profile_w_m2k" in coolant_march:
            _hg_prof = cooling.bartz_hg_profile(
                xs, rs, geo["throat_dia_m"], self.chamber_pressure_pa, cstar, mu_gas, cp_gas,
                pr_gas, pair=self.propellant_pair) * cooling.GAS_SIDE_DEPOSIT_FACTOR.get(
                    self.propellant_pair, 1.0)
            _rs_a = np.asarray(rs, dtype=float)
            _eps_prof = (_rs_a / (geo["throat_dia_m"] / 2.0)) ** 2
            _supersonic = np.arange(len(rs)) > _throat_idx
            _is_bell = _supersonic & (_eps_prof > eps_for_transition)
            _k_prof = np.where(_is_bell, bell_material.thermal_conductivity_w_mk,
                               chamber_material.thermal_conductivity_w_mk)
            _limit_prof = np.where(_is_bell, bell_material.max_service_temp_k,
                                   chamber_material.max_service_temp_k)
            t_wg_profile_k = np.full(len(rs), np.nan)
            for _kk in np.unique(_k_prof):          # solve_wall_balance_profile takes one k
                _sel = _k_prof == _kk
                t_wg_profile_k[_sel] = cooling.solve_wall_balance_profile(
                    _hg_prof[_sel], t_aw_film_profile_k[_sel],
                    coolant_march["h_c_profile_w_m2k"][_sel],
                    coolant_march["t_bulk_profile_k"][_sel],
                    hot_wall_thickness_m, float(_kk))[0]
            if np.any(np.isfinite(t_wg_profile_k)):
                # rank stations by how close each runs to ITS material's limit
                _ratio = np.where(np.isfinite(t_wg_profile_k),
                                  t_wg_profile_k / _limit_prof, -np.inf)
                _ip = int(np.argmax(_ratio))
                peak_wall_temp_k = float(t_wg_profile_k[_ip])
                peak_wall_temp_eps = float(_eps_prof[_ip])
                peak_wall_margin_ratio = float(_limit_prof[_ip]) / peak_wall_temp_k
                _barrel_end = int(np.flatnonzero(
                    np.isclose(_rs_a, _rs_a[0], rtol=1e-6)
                    & (np.arange(len(rs)) <= _throat_idx)).max())
                if abs(_ip - _throat_idx) <= 1 or peak_wall_temp_eps <= PEAK_WALL_THROAT_ZONE_EPS:
                    peak_wall_temp_zone = "throat"
                elif _ip <= _barrel_end:
                    peak_wall_temp_zone = "chamber barrel"
                elif _ip < _throat_idx:
                    peak_wall_temp_zone = "convergent section"
                else:
                    peak_wall_temp_zone = "nozzle"
        _check(checklist, warnings, "cooling", "Peak wall temperature along cooled length",
               peak_wall_margin_ratio is None or peak_wall_margin_ratio >= 1.0,
               (f"Hottest cooled-wall station is in the {peak_wall_temp_zone} (area ratio "
                f"~{peak_wall_temp_eps:.1f}): coupled wall balance ~{peak_wall_temp_k:.0f} K, "
                f"over that section's material limit ({peak_wall_margin_ratio:.2f}x). Levers: "
                f"more chamber film (or a convergent film ring for the throat region), faster "
                f"coolant, a thinner or more conductive liner."
                if peak_wall_margin_ratio is not None else ""),
               (f"OK - hottest station ~{peak_wall_temp_k:.0f} K in the {peak_wall_temp_zone} "
                f"({peak_wall_margin_ratio:.2f}x margin)"
                if peak_wall_margin_ratio is not None
                else "n/a - needs the 'channels' regen model"))
        if coolant_velocity_throat_ms is not None:
            _v_warn = manifold.velocity_cap_warning(coolant_velocity_throat_ms, "Throat coolant",
                                                    supercritical=_fuel_lh2)
            _check(checklist, warnings, "cooling", "Throat coolant velocity vs. SP-8087 limit",
                   _v_warn is None,
                   (f"Throat coolant-passage velocity ~{coolant_velocity_throat_ms:.0f} m/s "
                    f"exceeds SP-8087's {manifold.LIQUID_VELOCITY_MAX_MS:.0f} m/s liquid-coolant "
                    f"limit [SP-8087 Sec.3.1.1.5.3] - expect erosion and a steep jacket-dP / "
                    f"pump-power cost. Lower Coolant velocity or add film cooling instead."),
                   (f"OK - {coolant_velocity_throat_ms:.0f} m/s" if not _fuel_lh2
                    else f"n/a - supercritical LH2 ({coolant_velocity_throat_ms:.0f} m/s)"))
        _jbody_xs, _jbody_rs, _, _, _ = geometry.split_profile_by_area_ratio(
            xs, rs, geo["throat_dia_m"], cooled_length_eps)
        x_jacket_end_m = float(_jbody_xs[-1])
        local_bore_dia_m = 2.0 * float(_jbody_rs[-1])
        x_jacket_inlet_forward_m = (manifold_result["ox"]["attach_axial_station_m"]
                                     + manifold_result["ox"]["outer_radius_m"]
                                     + manifold.MANIFOLD_AXIAL_RING_GAP_M)

        # Local coolant-passage height at the jacket end sizes the split
        # topology's small turnaround collar (manifold.TURNAROUND_BORE_*);
        # None (no "channels" geometry) -> manifold's throat-dia fallback.
        turnaround_passage_height_m = (
            float(np.interp(x_jacket_end_m, xs, channel_geometry["height_m"]))
            if channel_geometry is not None else None)
        # Jacket-inlet ring velocity = the coolant-PASSAGE velocity at the
        # ring's own station (cooling.passage_velocity_ms - pure, so it works
        # in both regen channel models): SP-8087's constant-velocity torus
        # [SP-8087 Sec.2.1.2.1 p.19-20] / Fagherazzi's "no abrupt velocity
        # change between the supply volute and the channels". Station: the
        # bell end for single-pass, the forward (chamber) station for the
        # F-1 split topology.
        # J-2 layout: the mid-nozzle inlet station, and the DOWN-tube velocity
        # there (down + up tubes share the circumference -> ~3x faster).
        x_jacket_mid_inlet_m, jacket_mid_inlet_dia_m = None, None
        if two_pass:
            _jin_xs, _jin_rs, _, _, _ = geometry.split_profile_by_area_ratio(
                xs, rs, geo["throat_dia_m"], jacket_inlet_eps_eff)
            x_jacket_mid_inlet_m = float(_jin_xs[-1])
            jacket_mid_inlet_dia_m = 2.0 * float(_jin_rs[-1])
            jacket_inlet_velocity_ms = cooling.down_pass_velocity_ms(
                jacket_mid_inlet_dia_m, geo["throat_dia_m"], mdot_coolant_jacket_kgs,
                self.propellant_pair, n_channels=self.regen_channel_count,
                aspect_ratio=self.regen_channel_aspect_ratio,
                target_velocity_ms=self.regen_coolant_velocity_ms,
                land_fraction=self.regen_channel_land_fraction)
        else:
            _jin_station_dia_m = (geo["chamber_dia_m"]
                                  if self.cooling_flow_topology == "f1_split_reverse_flow"
                                  else local_bore_dia_m)
            jacket_inlet_velocity_ms = cooling.passage_velocity_ms(
                _jin_station_dia_m, geo["throat_dia_m"], mdot_coolant_jacket_kgs,
                self.propellant_pair, n_channels=self.regen_channel_count,
                aspect_ratio=self.regen_channel_aspect_ratio,
                target_velocity_ms=self.regen_coolant_velocity_ms,
                land_fraction=self.regen_channel_land_fraction, split_eps=split_eps_eff)
        # User trim on the matched velocity (1.0 = Fagherazzi's match).
        _jin_vmult = min(max(self.jacket_inlet_velocity_mult, 0.5), 2.0)
        jacket_inlet_velocity_ms *= _jin_vmult
        jacket_manifold_result = manifold.size_jacket_manifolds(
            mdot_fuel_kgs, rho_fuel, self.cooling_flow_topology, self.manifold_bypass_fraction,
            jacket_inlet_pressure_pa, jacket_return_pressure_pa, geo["chamber_dia_m"],
            local_bore_dia_m, x_jacket_inlet_forward_m, x_jacket_end_m,
            feed_velocity_target_ms=jacket_inlet_velocity_ms,
            turnaround_passage_height_m=turnaround_passage_height_m,
            throat_dia_m=geo["throat_dia_m"], taper_blend=self.jacket_inlet_taper_blend,
            inlet_angle_deg=_inlet_angles.get("jacket_inlet", 0.0),
            mid_inlet_x_m=x_jacket_mid_inlet_m, mid_inlet_dia_m=jacket_mid_inlet_dia_m,
            turnaround_velocity_ms=cooling.passage_velocity_ms(
                local_bore_dia_m, geo["throat_dia_m"], mdot_coolant_jacket_kgs,
                self.propellant_pair, n_channels=self.regen_channel_count,
                aspect_ratio=self.regen_channel_aspect_ratio,
                target_velocity_ms=self.regen_coolant_velocity_ms,
                land_fraction=self.regen_channel_land_fraction,
                split_eps=split_eps_eff))
        jacket_manifold_mass_kg = jacket_manifold_result["total_mass_kg"]

        _jin_thin_warn = manifold.thin_wall_warning(
            jacket_manifold_result["jacket_inlet"]["thin_wall_ratio"], "Jacket inlet")
        _check(checklist, warnings, "manifold", "Jacket inlet manifold thin-wall approximation validity",
               not _jin_thin_warn, _jin_thin_warn or "",
               f"OK - t/r {jacket_manifold_result['jacket_inlet']['thin_wall_ratio']:.2f}")
        if two_pass:
            _clamped = abs(jacket_inlet_eps_eff - self.jacket_inlet_eps) > 1e-9
            _check(checklist, warnings, "cooling", "J-2 mid-nozzle inlet station",
                   not _clamped,
                   f"Jacket inlet area ratio {self.jacket_inlet_eps:.1f} lies outside the cooled "
                   f"nozzle (throat .. eps {cooled_length_eps:.1f}) - clamped to "
                   f"{jacket_inlet_eps_eff:.1f}"
                   + (" (a zero-length down pass: this is single-pass cooling with a turnaround "
                      "collar)." if jacket_inlet_eps_eff >= cooled_length_eps else "."),
                   f"OK - inlet at eps {jacket_inlet_eps_eff:.1f}, down tubes to eps "
                   f"{cooled_length_eps:.1f}")
            _check(checklist, warnings, "cooling", "J-2 layout tube split",
                   not (self.tube_split_eps and self.tube_split_eps > 0),
                   "tube_split_eps is ignored under the J-2 mid-nozzle inlet layout - the two-"
                   "pass circuit sets its own tube counts (1 down : 2 up, the real J-2's 180/360).",
                   "OK")
            _check(checklist, warnings, "cooling", "J-2 layout two-pass march",
                   self.regen_channel_model == "channels" or chamber_cooling != "regenerative",
                   "The J-2 two-pass coolant march (cooling.march_coolant_two_pass) only runs in "
                   "the \"channels\" regen model - the \"flat\" model keeps its lumped jacket dP "
                   "and coolant dT, so only the manifold geometry reflects this layout.",
                   "OK")
        _jin_vel_warn = manifold.velocity_cap_warning(
            jacket_inlet_velocity_ms, "Jacket inlet", supercritical=_fuel_lh2)
        _check(checklist, warnings, "manifold", "Jacket inlet manifold velocity vs. SP-8087 limit",
               not _jin_vel_warn, _jin_vel_warn or "",
               f"OK - {jacket_inlet_velocity_ms:.1f} m/s (= {_jin_vmult:.2f} x local "
               "coolant-passage velocity)"
               + (" (LH2: SP-8087 liquid limit n/a, gas Mach criterion not modelled)"
                  if _fuel_lh2 else ""))
        _jin_bore_warn = manifold.bore_vs_chamber_warning(
            jacket_manifold_result["jacket_inlet"]["inner_diameter_m"], geo["chamber_dia_m"],
            "Jacket inlet")
        _check(checklist, warnings, "manifold", "Jacket inlet manifold bore vs. chamber packaging",
               not _jin_bore_warn, _jin_bore_warn or "", "OK")
        if jacket_manifold_result.get("jacket_return"):
            _jret_thin_warn = manifold.thin_wall_warning(
                jacket_manifold_result["jacket_return"]["thin_wall_ratio"], "Jacket return")
            _check(checklist, warnings, "manifold",
                   "Jacket return manifold thin-wall approximation validity",
                   not _jret_thin_warn, _jret_thin_warn or "",
                   f"OK - t/r {jacket_manifold_result['jacket_return']['thin_wall_ratio']:.2f}")
            _jret_bore_warn = manifold.bore_vs_chamber_warning(
                jacket_manifold_result["jacket_return"]["inner_diameter_m"], local_bore_dia_m,
                "Jacket return")
            _check(checklist, warnings, "manifold",
                   "Jacket return manifold bore vs. local nozzle packaging",
                   not _jret_bore_warn, _jret_bore_warn or "", "OK")

        _beta_warn = injectors.beta_warning(injector_geometry["beta_deg"], self.propellant_pair)
        _check(checklist, warnings, "injector", "Injector resultant beta angle",
               not _beta_warn, _beta_warn or "",
               f"OK - beta {injector_geometry['beta_deg']:+.1f} deg"
               + ("" if 20.0 <= self.impingement_angle_deg <= 45.0
                  else f" (impingement angle {self.impingement_angle_deg:.0f} deg outside 20-45)"))
        _check(checklist, warnings, "injector", "Impingement angle within 20-45 deg",
               20.0 <= self.impingement_angle_deg <= 45.0,
               f"Impingement included angle {self.impingement_angle_deg:.0f} deg is outside the "
               f"satisfactory 20-45 deg range [Huzel 4.5] - too shallow mixes poorly, too steep "
               f"risks splash-back onto the injector face.")
        a_e_ms = combustion_stability.speed_of_sound(gamma, m_molar, tc)
        chamber_acoustics = combustion_stability.acoustic_modes(
            a_e_ms, geo["chamber_length_m"], geo["chamber_dia_m"])
        # Raw advisory uses the EFFECTIVE dP/Pc (a stiff injector build clears it
        # here, exactly as raising injector dP does in real practice). If it
        # still fires, injector-face baffles and/or corner Helmholtz cavities
        # can resolve it (aids_resolution). Warn-not-block either way.
        stability_advisory = combustion_stability.instability_prone(
            chamber_acoustics, effective_dp_over_pc, self.target_vac_thrust_n)
        stability_resolution = None
        if stability_advisory:
            stability_resolution = combustion_stability.aids_resolution(
                chamber_acoustics, baffles=self.injector_baffles,
                baffle_compartments=self.baffle_compartments,
                cavities=self.acoustic_cavities, cavity_count=self.acoustic_cavity_count)
        stability_ok = (not stability_advisory) or (stability_resolution is not None)
        _stability_pass_detail = (
            f"OK - resolved: {stability_resolution}" if stability_resolution
            else f"OK - 1T ~{chamber_acoustics['tang_1t_hz']:.0f} Hz, 1L "
                 f"~{chamber_acoustics['long_1l_hz']:.0f} Hz"
                 + ("" if self.injector_stiffness == "nominal"
                    else f" (stiff injector dP/Pc {effective_dp_over_pc:.2f})"))
        _check(checklist, warnings, "stability", "Combustion acoustic-mode margin",
               stability_ok, stability_advisory or "", _stability_pass_detail)
        _check(checklist, warnings, "stability", "Baffle compartment count",
               (not self.injector_baffles)
               or combustion_stability.baffle_compartments_ok(self.baffle_compartments),
               f"Injector-face baffle has {self.baffle_compartments} compartments - use an ODD "
               f"count >= 3 (SSME used 5). An even number sits on the tangential-mode nodal "
               f"lines and ENHANCES the standing mode.",
               f"OK - {self.baffle_compartments}-compartment baffle" if self.injector_baffles
               else "n/a - no baffle")

        stability_aid_mass_kg = combustion_stability.aid_mass_kg(
            geo["chamber_dia_m"], baffles=self.injector_baffles,
            baffle_compartments=self.baffle_compartments,
            cavities=self.acoustic_cavities, cavity_count=self.acoustic_cavity_count)
        stability_result = {
            "modes": chamber_acoustics,
            "advisory": stability_advisory,
            "resolution": stability_resolution,
            "resolved": stability_ok,
            "effective_dp_over_pc": effective_dp_over_pc,
            "injector_stiffness": self.injector_stiffness,
            "baffles": self.injector_baffles,
            "baffle_compartments": self.baffle_compartments,
            "cavities": self.acoustic_cavities,
            "cavity_count": self.acoustic_cavity_count,
            "aid_mass_kg": stability_aid_mass_kg,
        }

        cooling_result = {
            "chamber_cooling_method": chamber_cooling,
            "nozzle_cooling_method": nozzle_cooling,
            # the explicit method that was HARD-BLOCKED for that section's
            # material (None = honoured) - cooling.resolve_cooling_method_checked
            "chamber_cooling_rejected": chamber_cooling_rejected,
            "nozzle_cooling_rejected": nozzle_cooling_rejected,
            "wall_construction": self.wall_construction,
            "chamber_tube_jacket": self.chamber_tube_jacket,
            "tube_split_eps": split_eps_eff,
            "tube_hatbands": self.tube_hatbands,
            "tube_hatbands_on_extension": self.tube_hatbands_on_extension,
            "tube_hatband_count": self.tube_hatband_count,
            "tube_hatband_width_m": self.tube_hatband_width_m,
            "flange_thickness_m": self.flange_thickness_m,
            "flange_width_m": self.flange_width_m,
            "flange_bolt_count": self.flange_bolt_count,
            "regen_circuit_style": REGEN_CIRCUIT_STYLE_BY_TOPOLOGY.get(
                self.cooling_flow_topology, "single_pass_upflow"),
            "cooled_length_eps": cooled_length_eps,
            "regen_nozzle_end_eps": self.regen_nozzle_end_eps,
            "dump_coolant_fraction": dump_coolant_fraction_eff,
            "dump_mdot_kgs": dump_mdot_kgs,
            "dump_coolant_dt_k": dump_coolant_dt_k,
            "dump_isp_penalty_fraction": dump_isp_penalty_fraction,
            "chamber_cooling_source": (
                f"material-default - explicit {chamber_cooling_rejected} BLOCKED"
                if chamber_cooling_rejected else
                "explicit" if self.chamber_cooling_method not in ("", "auto")
                else "material-default"),
            "nozzle_cooling_source": (
                f"material-default - explicit {nozzle_cooling_rejected} BLOCKED"
                if nozzle_cooling_rejected else
                "explicit" if self.nozzle_cooling_method not in ("", "auto")
                else "material-default"),
            "q_profile_w_m2": q_profile_w_m2,
            "q_throat_w_m2": q_throat_w_m2,
            "q_chamber_avg_w_m2": q_chamber_avg_w_m2,
            "q_chamber_avg_anchor_w_m2": q_chamber_avg_anchor_w_m2,   # pre-Phase-7 anchor, reported only
            "q_profile_abs_w_m2": q_profile_w_m2,      # alias - q_profile_w_m2 IS the absolute profile now
            "q_throat_abs_w_m2": q_throat_abs_w_m2,
            "q_chamber_avg_abs_w_m2": q_chamber_avg_abs_w_m2,
            "wall_heat_total_w": wall_heat_w,
            "wall_heat_energy_fraction": wall_heat_energy_fraction,
            "coolant_delta_t_k": coolant_delta_t_k,
            "coolant_limit_k": coolant_limit_k,
            "regen_cooled": regen_cooled,
            "regen_ok": regen_ok,
            "hg_throat_w_m2k": hg_throat_w_m2k,
            "t_aw_chamber_k": t_aw_chamber_k,
            "t_wg_throat_k": t_wg_throat_k,
            # Coupled throat wall balance ("channels" + regen only; None otherwise):
            "t_wc_throat_k": t_wc_throat_coupled_k,
            "q_throat_wall_balance_w_m2": q_throat_wall_balance_w_m2,
            "h_g_throat_effective_w_m2k": h_g_throat_effective_w_m2k,
            "coolant_velocity_throat_ms": coolant_velocity_throat_ms,
            "hot_wall_thickness_m": hot_wall_thickness_m,
            "bell_wall_temp_k": bell_wall_temp_k,
            "film_cooling_fraction": film_fraction,
            "film_flux_factor": film_flux_factor,                 # cooled-zone area-average
            "film_flux_factor_effective": film_flux_factor,       # explicit alias
            "film_effectiveness_profile": film_phi,               # COMBINED (both sites)
            "chamber_film_profile": chamber_film_phi,
            "nozzle_film_profile": nozzle_film_phi,
            "chamber_film_inject_area_ratio": self.chamber_film_inject_area_ratio,
            "nozzle_film_fraction": (self.nozzle_film_fraction if nozzle_film_active else 0.0),
            "nozzle_film_inject_eps": self.nozzle_film_inject_eps,
            "nozzle_film_isp_penalty_fraction": nozzle_film_isp_penalty_fraction,
            "film_temperature_k": _t_film_k,                       # post-jacket film fuel temp
            "t_aw_film_profile_k": t_aw_film_profile_k,
            "film_cooled_length_eps": eps_for_transition,
            # full-length coupled wall balance ("channels" regen only, else None)
            "t_wg_profile_k": t_wg_profile_k,
            "peak_wall_temp_k": peak_wall_temp_k,
            "peak_wall_temp_zone": peak_wall_temp_zone,
            "peak_wall_temp_eps": peak_wall_temp_eps,
            "peak_wall_margin_ratio": peak_wall_margin_ratio,
            "bell_wall_temp_eps": bell_wall_temp_eps,
            "regen_isp_bonus_fraction": regen_isp_bonus,
            "through_wall_delta_t_k": through_wall_delta_t_k,
            "throat_thermal_stress_pa": throat_thermal_stress_pa,
            "throat_fatigue_cycles": throat_fatigue_cycles,
            "regen_channel_model": self.regen_channel_model,
            "jacket_dp_pa": jacket_dp_pa,
            "coolant_channels": (coolant_march["n_channels"] if coolant_march else None),
            "coolant_channel_dh_throat_m": (coolant_march["channel_dh_throat_m"] if coolant_march else None),
            "coolant_exit_t_k": (coolant_march["coolant_exit_t_k"] if coolant_march else None),
            "coolant_side_wall_t_throat_k": (coolant_march["t_wc_throat_k"] if coolant_march else None),
            "channel_land_fraction": (_land_fraction_visual if channel_geometry else None),
            "channel_width_profile_m": (channel_geometry["width_m"] if channel_geometry else None),
            "channel_height_profile_m": (channel_geometry["height_m"] if channel_geometry else None),
            "channel_dh_profile_m": (channel_geometry["dh_m"] if channel_geometry else None),
            # Per-station bulk coolant velocity mdot/(rho*total passage area) -
            # the same expression march_coolant uses per segment.
            "coolant_velocity_profile_ms": (
                mdot_coolant_jacket_kgs / (cooling.COOLANT_DENSITY_KG_M3.get(
                    self.propellant_pair, cooling._COOLANT_DENSITY_FALLBACK)
                    * np.maximum(channel_geometry["total_area_m2"], 1e-12))
                if channel_geometry else None),
            "jacket_inlet_velocity_ms": jacket_inlet_velocity_ms,
            "jacket_dp_down_pa": (coolant_march.get("jacket_dp_down_pa") if coolant_march else None),
            "coolant_turnaround_t_k": (coolant_march.get("coolant_turnaround_t_k")
                                       if coolant_march else None),
            "coolant_channels_down": (coolant_march.get("n_channels_down") if coolant_march else None),
        }

        # Dry-mass estimate: chamber/nozzle wall mass from a real thin-wall pressure-vessel
        # hoop-stress formula (physics/mass_model.py), split by material at the same
        # eps_for_transition point already used above and for rendering
        # (geometry.split_profile_by_area_ratio), plus turbopump mass (already computed
        # for pump-fed cycles). A LOWER BOUND on real dry mass - no injector/valves/
        # actuators/mounting structure. See physics/mass_model.py's module docstring.
        # (bell_material was looked up above for the nozzle-extension thermal check.)
        body_xs, body_rs, ext_xs, ext_rs, has_extension = geometry.split_profile_by_area_ratio(
            xs, rs, geo["throat_dia_m"], eps_for_transition)
        chamber_wall_mass_kg = mass_model.shell_mass_kg(
            body_xs, body_rs, self.chamber_pressure_pa,
            chamber_material.allowable_stress_pa, chamber_material.density_kg_m3)
        bell_wall_mass_kg = 0.0
        if has_extension:
            bell_wall_mass_kg = mass_model.shell_mass_kg(
                ext_xs, ext_rs, self.chamber_pressure_pa,
                bell_material.allowable_stress_pa, bell_material.density_kg_m3)
        # Per-station wall thickness (pointwise, not the segment-average
        # shell_mass_kg integrates for mass) - for the 3D preview's solid-shell
        # offset. Purely additive: doesn't feed any mass/thermal number above
        # (shell_mass_kg, just above, keeps its own flat-Pc approximation for
        # BOTH pieces unchanged - this pointwise profile is a rendering-only
        # refinement on top of it).
        #
        # The chamber/convergent/throat stations run near chamber pressure
        # throughout - real static pressure stays close to Pc until the
        # throat, so flat Pc is a fine approximation there. Past the throat,
        # BOTH the body piece's own diverging-bell portion (up to
        # eps_for_transition) and the separate EXTENSION piece instead use
        # the LOCAL isentropic static pressure at each station's own area
        # ratio (iso.pe_over_pc_from_eps) - thickness is proportional to
        # pressure x radius, and flat chamber pressure applied all the way to
        # a large-eps station (where the real static pressure has dropped to
        # a small fraction of Pc) made the RENDERED wall balloon into an
        # increasingly absurd flare as area ratio grew, despite real nozzle
        # walls being thin precisely because they run at low local pressure,
        # not from a material difference. Applying flat Pc to only the body
        # piece's OWN diverging stations (while the extension already used
        # local pressure) produced a large spurious thickness step right at
        # the body/extension joint - large enough to render as a visible
        # kink/bump in the 3D preview even with the bridging frustum that
        # smooths the two pieces' outer walls together.
        throat_r_m = geo["throat_dia_m"] / 2.0
        if throat_r_m > 0 and len(body_rs) > 1:
            body_throat_idx = int(np.argmin(body_rs))
            body_local_eps = np.clip((body_rs / throat_r_m) ** 2, 1.0 + 1e-6, None)
            body_pressure_pa = np.array([
                self.chamber_pressure_pa * iso.pe_over_pc_from_eps(float(e), gamma)
                for e in body_local_eps])
            body_pressure_pa[:body_throat_idx] = self.chamber_pressure_pa
        else:
            body_pressure_pa = self.chamber_pressure_pa
        body_wall_thickness_m = mass_model.wall_thickness_profile_m(
            body_rs, body_pressure_pa, chamber_material.allowable_stress_pa)
        if has_extension:
            ext_local_eps = (np.clip((ext_rs / throat_r_m) ** 2, 1.0 + 1e-6, None)
                             if throat_r_m > 0 else np.full_like(ext_rs, 1.0 + 1e-6))
            ext_pressure_pa = np.array([
                self.chamber_pressure_pa * iso.pe_over_pc_from_eps(float(e), gamma)
                for e in ext_local_eps])
            ext_wall_thickness_m = mass_model.wall_thickness_profile_m(
                ext_rs, ext_pressure_pa, bell_material.allowable_stress_pa)
        else:
            ext_wall_thickness_m = np.zeros(0)
        # --- jacket/coolant overpressure vs. wall structural margin
        # (structural PLAUSIBILITY flag, NOT a buckling analysis - see
        # ASSUMPTIONS.md). The coolant jacket runs at roughly the pump-discharge
        # pressure, nearly flat along its length in this model (no axial jacket-
        # pressure-drop profile exists - only one lumped jacket_dp_pa), while
        # local gas static pressure keeps falling past the throat
        # (iso.pe_over_pc_from_eps). The net differential between them can load
        # the wall inward rather than the outward/tension direction its
        # thickness was sized for - the real "liner buckling near the nozzle
        # exit" consideration.
        #
        # Per wall_construction (cooling.WALL_CONSTRUCTIONS), the physically
        # correct FORMULA differs - `[Huzel "Tubular Wall Thrust Chamber
        # Design" p.107-109]` (see claude_lit/topics/06-cooling-and-heat-
        # transfer.md):
        #   - tube_wall: eq 4-27/4-28, a circular tube's combined hoop (net
        #     Pco-Pg x the TUBE's own local radius / thickness) + longitudinal
        #     thermal-restraint stress. Sign-agnostic - no "reversal" framing
        #     needed. Huzel's own A-1 sample calc shows Pco=1500psia >
        #     Pg=562psia AT THE THROAT too, so net-inward loading is normal
        #     near-everywhere past the injector for a real tube/coax design,
        #     not just a downstream edge case - evaluated at both the throat
        #     (where heat flux, hence the thermal term, peaks) and the worst-
        #     reversal station (end of active cooling), taking the max.
        #   - coax_shell: eq 4-31, the SAME two terms but with the full local
        #     shell radius (a continuous shell, not discrete tubes) - this is
        #     the one case where the tool's original, since-corrected full-
        #     radius hoop-stress attempt was actually the right formula.
        #   - milled_channel: kept as the clamped rectangular-plate-strip
        #     approximation from the prior round (span = channel width,
        #     reversal-gated only) - no citation covers a thermal term
        #     combined with plate-bending for milled channels yet
        #     (`[Sutton Sec 8.3]`, still unread).
        # In all three cases, wall THICKNESS is still the tool's generic
        # Pc-derived shell thickness (mass_model.wall_thickness_m using the
        # FULL local radius) - a pre-existing gap this round does not fix; see
        # ASSUMPTIONS.md.
        jacket_overpressure_active = (chamber_cooling == "regenerative"
                                       and self.regen_channel_model == "channels"
                                       and channel_geometry is not None
                                       and jacket_dp_pa > 0.0 and throat_r_m > 0)
        jacket_overpressure_ok = True
        jacket_overpressure_detail = ""
        jacket_worst_station_eps = None
        jacket_pressure_at_worst_station_pa = None
        jacket_local_gas_pressure_at_worst_station_pa = None
        jacket_overpressure_worst_station = None
        jacket_combined_stress_pa = None
        jacket_hoop_stress_pa = None
        jacket_thermal_stress_pa = None
        # --- longitudinal thermal inelastic buckling (Huzel eq 4-29) - a
        # DIFFERENT failure mode from the pressure/hoop check above: thermal-
        # restraint-driven buckling of the tube's hot-gas-side "zone I"
        # against its cooler, much more massive backside "zone II" - not a
        # coolant-vs-gas pressure differential. tube_wall only (the extracted
        # Huzel text gives no coax-shell buckling analogue). Real, citable
        # formula (mass_model.longitudinal_buckling_stress_pa), but E_c
        # (compression tangent modulus) has NO data for any material in this
        # codebase today - reports "n/a" per material rather than estimating
        # a cross-material ratio with no real grounding. See ASSUMPTIONS.md.
        buckling_active = False
        buckling_ok = True
        buckling_detail = ""
        buckling_material_name = None
        if jacket_overpressure_active:
            worst_eps = max(cooled_length_eps, 1.0 + 1e-6)
            worst_r_m = throat_r_m * math.sqrt(worst_eps)
            p_local_gas_worst_pa = self.chamber_pressure_pa * iso.pe_over_pc_from_eps(worst_eps, gamma)
            # Reuses the already-computed, topology-aware manifold pressure
            # variables (design.py:1290-1292) instead of recomputing the same
            # formula independently - single_pass_countercurrent (default)
            # uses jacket_inlet_pressure_pa (algebraically identical to the
            # old recomputation, zero behavior change); f1_split_reverse_flow
            # uses jacket_return_pressure_pa (lower, by the down-leg's own
            # share of jacket_dp_pa) instead of always assuming full inlet
            # pressure at the worst/aft station - resolves the "somewhat
            # conservative under f1_split_reverse_flow" gap noted in
            # ASSUMPTIONS.md's coolant_delta_t_k rescale entry.
            # j2_mid_nozzle_inlet: the aft (worst) station is at the
            # turnaround too - same return-pressure reasoning.
            jacket_pressure_pa = (jacket_return_pressure_pa
                                   if self.cooling_flow_topology in ("f1_split_reverse_flow",
                                                                     "j2_mid_nozzle_inlet")
                                   else jacket_inlet_pressure_pa)
            worst_material = chamber_material if worst_eps <= eps_for_transition else bell_material
            t_worst_m = max(
                mass_model.wall_thickness_m(p_local_gas_worst_pa, worst_r_m, worst_material.allowable_stress_pa),
                mass_model.MIN_WALL_THICKNESS_M)
            t_throat_m = max(
                mass_model.wall_thickness_m(self.chamber_pressure_pa, throat_r_m,
                                             chamber_material.allowable_stress_pa),
                mass_model.MIN_WALL_THICKNESS_M)
            jacket_worst_station_eps = worst_eps
            jacket_pressure_at_worst_station_pa = jacket_pressure_pa
            jacket_local_gas_pressure_at_worst_station_pa = p_local_gas_worst_pa

            if self.wall_construction in ("tube_wall", "coax_shell"):
                # q at the worst-reversal station, interpolated from the
                # already-computed absolute heat-flux profile (diverging side
                # only - eps isn't monotonic across the throat). q AT the
                # throat is exactly q_throat_w_m2 by definition (its max).
                throat_idx_full = int(np.argmin(rs))
                full_local_eps = (np.clip((rs / throat_r_m) ** 2, 1.0 + 1e-6, None)
                                   if throat_r_m > 0 else np.full_like(rs, 1.0 + 1e-6))
                div_eps = full_local_eps[throat_idx_full:]
                div_q = q_profile_w_m2[throat_idx_full:]
                q_worst_w_m2 = (float(np.interp(worst_eps, div_eps, div_q))
                                 if len(div_eps) > 1 else q_throat_w_m2)

                def _combined_stress(radius_m, t_m, p_local_gas_pa, q_w_m2, material):
                    net_dp = jacket_pressure_pa - p_local_gas_pa
                    s_hoop = mass_model.hoop_stress_pa(net_dp, radius_m, t_m)
                    dt_thru_k = (q_w_m2 * t_m / material.thermal_conductivity_w_mk
                                 if material.thermal_conductivity_w_mk > 0 else 0.0)
                    s_thermal = mass_model.thermal_stress_pa(
                        dt_thru_k, material.youngs_modulus_pa, material.cte_per_k,
                        nu=mass_model.POISSON_RATIO)
                    return net_dp, s_hoop, s_thermal, s_hoop + s_thermal

                if self.wall_construction == "tube_wall":
                    n_ch_worst = cooling.channel_count_at_station(
                        _n_ch_visual, worst_eps, split_eps_eff)
                    n_ch_throat = cooling.channel_count_at_station(
                        _n_ch_visual, 1.0, split_eps_eff)
                    radius_worst_m = cooling.channel_hydraulic_geometry(
                        2.0 * worst_r_m, n_ch_worst, _channel_height_visual,
                        _land_fraction_visual)["dh_m"] / 2.0
                    radius_throat_m = cooling.channel_hydraulic_geometry(
                        2.0 * throat_r_m, n_ch_throat, _channel_height_visual,
                        _land_fraction_visual)["dh_m"] / 2.0
                    formula_name = "Huzel eq 4-27/4-28, tube_wall"
                else:  # coax_shell
                    radius_worst_m = worst_r_m
                    radius_throat_m = throat_r_m
                    formula_name = "Huzel eq 4-31, coax_shell"

                # Wall thickness: the one minimising the SAME combined stress
                # (Huzel eq 4-27+4-28: |Pco-Pg|*r/t + K*t -> t* = sqrt(|dP|*r/K),
                # mass_model.min_combined_stress_thickness_m), sized against the
                # local tube/shell radius and the NET coolant-vs-gas differential
                # the wall really carries. Replaces (2026-09-23) sizing against
                # local GAS pressure alone, which left a nozzle-exit tube at the
                # gauge floor while holding ~Pc-class coolant pressure - a
                # "thicker wall" warning nothing could act on. Floor: tube_wall
                # uses the cited real tube gauge (TUBE_WALL_MIN_THICKNESS_M,
                # Huzel A-2); coax_shell keeps the generic MIN_WALL_THICKNESS_M.
                # Cap: the existing REGEN_HOT_WALL_THICKNESS_M precedent (a
                # coax_shell liner is backed by an outer jacket not modeled here,
                # never a lone ~15mm pressure vessel).
                t_floor_m = (mass_model.TUBE_WALL_MIN_THICKNESS_M
                             if self.wall_construction == "tube_wall"
                             else mass_model.MIN_WALL_THICKNESS_M)

                def _sized_thickness(radius_m, p_local_gas_pa, q_w_m2, material):
                    k_per_m = (mass_model.thermal_stress_pa(
                        q_w_m2 / material.thermal_conductivity_w_mk, material.youngs_modulus_pa,
                        material.cte_per_k, nu=mass_model.POISSON_RATIO)
                        if material.thermal_conductivity_w_mk > 0 else 0.0)
                    return mass_model.min_combined_stress_thickness_m(
                        jacket_pressure_pa - p_local_gas_pa, radius_m, k_per_m,
                        t_floor_m, REGEN_HOT_WALL_THICKNESS_M)

                t_construction_worst_m, t_limit_worst = _sized_thickness(
                    radius_worst_m, p_local_gas_worst_pa, q_worst_w_m2, worst_material)
                t_construction_throat_m, t_limit_throat = _sized_thickness(
                    radius_throat_m, self.chamber_pressure_pa, q_throat_w_m2, chamber_material)

                net_worst, hoop_worst, thermal_worst, combined_worst = _combined_stress(
                    radius_worst_m, t_construction_worst_m, p_local_gas_worst_pa,
                    q_worst_w_m2, worst_material)
                net_throat, hoop_throat, thermal_throat, combined_throat = _combined_stress(
                    radius_throat_m, t_construction_throat_m, self.chamber_pressure_pa,
                    q_throat_w_m2, chamber_material)

                if self.wall_construction == "tube_wall":
                    buckling_active = True
                    # Evaluate at whichever station has the bigger THERMAL
                    # term specifically (not necessarily the same station the
                    # combined-stress check above picks - buckling is driven
                    # purely by the thermal-restraint term, which typically
                    # peaks at the throat where heat flux is highest).
                    if thermal_throat >= thermal_worst:
                        buckling_material = chamber_material
                        buckling_thermal_pa = thermal_throat
                        buckling_t_m, buckling_r_m = t_construction_throat_m, radius_throat_m
                    else:
                        buckling_material = worst_material
                        buckling_thermal_pa = thermal_worst
                        buckling_t_m, buckling_r_m = t_construction_worst_m, radius_worst_m
                    buckling_material_name = buckling_material.display_name
                    if buckling_material.e_c_pa is not None:
                        s_c_pa = mass_model.longitudinal_buckling_stress_pa(
                            buckling_material.youngs_modulus_pa, buckling_material.e_c_pa,
                            buckling_t_m, buckling_r_m, nu=mass_model.POISSON_RATIO)
                        buckling_limit_pa = 0.9 * s_c_pa
                        buckling_ok = buckling_thermal_pa <= buckling_limit_pa
                        if not buckling_ok:
                            buckling_detail = (
                                f"Longitudinal thermal-restraint stress (~{buckling_thermal_pa/1e6:.0f} MPa) "
                                f"exceeds 0.9x the critical inelastic-buckling stress "
                                f"(~{buckling_limit_pa/1e6:.0f} MPa of {s_c_pa/1e6:.0f} MPa, Huzel eq 4-29) "
                                f"for {buckling_material_name}'s hot-gas-side tube wall. Consider a lower "
                                f"heat flux there (film cooling, larger throat), a thicker wall, or a "
                                f"material with a higher compression tangent modulus.")
                    else:
                        buckling_detail = (f"n/a - no compression tangent-modulus (E_c) data for "
                                            f"{buckling_material_name}; see ASSUMPTIONS.md")

                # Governing station = the one furthest over ITS OWN allowable
                # (the two stations can be different materials), not the one
                # with the bigger raw stress - that hid e.g. a copper throat
                # over its lower allowable behind a larger exit stress.
                util_throat = combined_throat / (chamber_material.allowable_stress_pa
                                                 / mass_model.SAFETY_FACTOR)
                util_worst = combined_worst / (worst_material.allowable_stress_pa
                                               / mass_model.SAFETY_FACTOR)
                if util_throat >= util_worst:
                    station_name = "throat"
                    station_eps = 1.0
                    net_dp_pa, hoop_pa, thermal_pa, combined_pa = (
                        net_throat, hoop_throat, thermal_throat, combined_throat)
                    station_material, station_t_m = chamber_material, t_construction_throat_m
                    station_t_limit = t_limit_throat
                else:
                    station_name = "cooled_length_end"
                    station_eps = worst_eps
                    net_dp_pa, hoop_pa, thermal_pa, combined_pa = (
                        net_worst, hoop_worst, thermal_worst, combined_worst)
                    station_material, station_t_m = worst_material, t_construction_worst_m
                    station_t_limit = t_limit_worst

                allowable_pa = station_material.allowable_stress_pa / mass_model.SAFETY_FACTOR
                jacket_overpressure_ok = combined_pa <= allowable_pa
                jacket_overpressure_worst_station = station_name
                jacket_combined_stress_pa = combined_pa
                jacket_hoop_stress_pa = hoop_pa
                jacket_thermal_stress_pa = thermal_pa
                if not jacket_overpressure_ok:
                    station_desc = ("the throat" if station_name == "throat"
                                     else f"the end of active cooling (area ratio ~{station_eps:.1f})")
                    if self.wall_construction == "coax_shell":
                        # Large-radius thin liner: r/t is inherently large (a
                        # continuous shell at full chamber radius, sized thin
                        # for heat transfer per Huzel's own description of the
                        # inner shell as structurally separate from the outer
                        # jacket) - almost ANY meaningful net pressure
                        # differential produces high stress here, at nearly
                        # any cooling extent, not just extreme designs. This
                        # matches real history: coax-shell construction was
                        # only ever used on small/early engines (V-2, early
                        # Atlas - see cooling.WALL_CONSTRUCTIONS's own
                        # comment), never scaled up. Expected/near-universal
                        # for this construction, not a marginal edge case.
                        mitigation = ("this construction only models the inner liner, not a "
                                       "supporting outer structural jacket that would share the "
                                       "load in a real design - consider tube_wall or "
                                       "milled_channel construction instead for a chamber this size")
                        framing = ("a large-radius thin shell inherently has a high stress-per-"
                                    "unit-pressure ratio - this is expected/near-universal for "
                                    "coax_shell at this scale, matching why real coax-shell "
                                    "designs stayed small (V-2/early-Atlas class), not a marginal "
                                    "or unusual result")
                    elif station_t_limit == "floor":
                        # Thermal-limited: the best wall is thinner than the
                        # gauge floor allows; thermal term grows with t.
                        mitigation = ("the thermal-restraint term dominates and grows with wall "
                                       "thickness (dT = q*t/k), so the wall is already at its "
                                       f"~{t_floor_m*1e3:.1f} mm minimum - consider a higher-"
                                       "conductivity liner (a copper alloy such as GRCop-84/"
                                       "NARloy-Z) or less throat heat flux (film cooling, lower Pc)")
                        framing = "worth a closer structural look"
                    elif station_t_limit == "cap":
                        # Pressure-limited: the best wall is thicker than a
                        # regen hot wall can be.
                        mitigation = ("the hoop term dominates and the wall is already at its "
                                       f"~{REGEN_HOT_WALL_THICKNESS_M*1e3:.1f} mm regen hot-wall "
                                       "maximum - consider more/narrower tubes there (tube count, "
                                       "tube split), lower jacket pressure (shorter cooled length, "
                                       "less jacket dP) or a stronger alloy")
                        framing = "worth a closer structural look"
                    else:
                        mitigation = ("no single wall thickness carries both the pressure and the "
                                       "thermal load in this material (this is already the minimum-"
                                       "stress thickness) - consider a stronger or higher-"
                                       "conductivity alloy, more/narrower tubes, or less heat flux")
                        framing = "worth a closer structural look"
                    jacket_overpressure_detail = (
                        f"At {station_desc}, combined hoop + thermal-restraint stress "
                        f"({formula_name}) is ~{combined_pa/1e6:.0f} MPa (hoop "
                        f"~{hoop_pa/1e6:.0f} MPa from a ~{net_dp_pa/1e6:.1f} MPa net jacket-vs-gas "
                        f"differential + thermal-restraint ~{thermal_pa/1e6:.0f} MPa) against a "
                        f"~{allowable_pa/1e6:.0f} MPa allowable ({station_material.display_name}, "
                        f"SF {mass_model.SAFETY_FACTOR:.1f}), with the wall at its minimum-stress "
                        f"thickness ~{station_t_m*1e3:.2f} mm. This uses a real handbook stress "
                        f"formula ({formula_name}), not a proxy - {framing}. {mitigation[:1].upper() + mitigation[1:]}.")
            else:
                # milled_channel: unchanged clamped-plate-strip proxy.
                n_ch_worst = cooling.channel_count_at_station(
                    _n_ch_visual, worst_eps, split_eps_eff)
                channel_width_worst_m = cooling.channel_hydraulic_geometry(
                    2.0 * worst_r_m, n_ch_worst, _channel_height_visual,
                    _land_fraction_visual)["width_m"]
                net_dp_pa = jacket_pressure_pa - p_local_gas_worst_pa
                # Long clamped rectangular-plate-strip approximation (span =
                # channel width b, aspect ratio >> 1 since channels run the
                # wall's full length): peak bending stress at the clamped rib
                # edge, sigma_max = q * b^2 / (2 * t^2), the standard clamped-
                # clamped beam-strip result (M_support = q*b^2/12 per unit
                # width, section modulus t^2/6). Tier 3: the formula SHAPE is a
                # standard plate/beam-strip result, not invented, but has no
                # real-engine spot check in this codebase (see ASSUMPTIONS.md).
                equivalent_bending_stress_pa = (
                    net_dp_pa * channel_width_worst_m ** 2 / (2.0 * t_worst_m ** 2)
                    if channel_width_worst_m > 0 else 0.0)
                allowable_pa = worst_material.allowable_stress_pa / mass_model.SAFETY_FACTOR
                jacket_overpressure_ok = not (net_dp_pa > 0.0 and equivalent_bending_stress_pa > allowable_pa)
                jacket_overpressure_worst_station = "cooled_length_end"
                jacket_combined_stress_pa = equivalent_bending_stress_pa
                if not jacket_overpressure_ok:
                    jacket_overpressure_detail = (
                        f"Near the end of active cooling (area ratio ~{worst_eps:.1f}), estimated "
                        f"jacket/coolant pressure (~{jacket_pressure_pa/1e6:.1f} MPa) exceeds local "
                        f"hot-gas static pressure (~{p_local_gas_worst_pa/1e6:.1f} MPa) - the net load on "
                        f"the channel-land wall there REVERSES direction. Modeled as a clamped-strip "
                        f"bending stress across the ~{channel_width_worst_m*1000:.1f} mm channel width, "
                        f"this reversed ~{net_dp_pa/1e6:.1f} MPa differential is "
                        f"~{equivalent_bending_stress_pa/1e6:.0f} MPa against a "
                        f"~{allowable_pa/1e6:.0f} MPa allowable ({worst_material.display_name}, SF "
                        f"{mass_model.SAFETY_FACTOR:.1f}) - but this is a coarse clamped-plate-strip "
                        f"proxy, NOT a real buckling/FEA analysis, and this codebase has no real-engine "
                        f"spot check for it yet. Treat this as 'worth a closer structural look', not a "
                        f"validated failure prediction. Consider more/narrower channels (smaller span), "
                        f"tapering the actively-cooled length, or a thicker wall there.")
        _check(checklist, warnings, "cooling", "Jacket overpressure vs. channel-wall structural margin",
               jacket_overpressure_ok, jacket_overpressure_detail,
               "n/a - only evaluated in \"channels\" regen mode with an active jacket"
               if not jacket_overpressure_active
               else "OK - stress stays within margin at the evaluated stations")
        _check(checklist, warnings, "cooling", "Tube-wall longitudinal thermal buckling margin",
               buckling_ok, buckling_detail,
               "n/a - only evaluated for tube_wall construction with an active jacket"
               if not buckling_active
               else (buckling_detail if buckling_detail else "OK - thermal-restraint stress stays "
                     "under 0.9x the critical buckling stress"))

        # --- tube_wall: swaged-tube taper limit + structural hatbands -------
        # A brazed tube bundle is contiguous: each tube is swaged/expanded to a
        # taper and "spanked" to fill the local pitch [Huzel p.113-114; SP-8087
        # Sec.2.1.1.3 p.12-13, Fig. 1]. Its width therefore tracks the local
        # circumference / tube count, and one tube's max/min width ratio over its
        # run is limited: 3.5:1 by pure reduction, 6:1 with a 2:1 expansion; past
        # that a bifurcation (tube_split_eps) is needed.
        tube_taper_ratio = 0.0
        hatband_result = None
        hatband_mass_kg = 0.0
        hatband_banded_fraction = 0.0
        is_tube_wall = (self.wall_construction == "tube_wall"
                        and chamber_cooling in ("regenerative", "dump"))
        if is_tube_wall and throat_r_m > 0:
            _n_tube_base = cooling.channel_count(geo["throat_dia_m"], self.regen_channel_count)

            def _n_tubes_at(r_m):
                return cooling.channel_count_at_station(
                    _n_tube_base, max((r_m / throat_r_m) ** 2, 1.0), split_eps_eff)

            _i_throat = int(np.argmin(rs))
            _eps_all = np.maximum((rs / throat_r_m) ** 2, 1.0)
            _cooled = np.ones(rs.size, dtype=bool)
            _cooled[_i_throat:] = _eps_all[_i_throat:] <= cooled_length_eps * (1 + 1e-9)
            if self.chamber_tube_jacket:
                _cooled[:_i_throat] = False      # chamber is a continuous jacket, not tubes
            _n_st = np.array([_n_tubes_at(r) for r in rs])
            for _n in np.unique(_n_st[_cooled]):
                _w = rs[_cooled & (_n_st == _n)] / _n
                if _w.size >= 2 and _w.min() > 0:
                    tube_taper_ratio = max(tube_taper_ratio, float(_w.max() / _w.min()))
            _check(checklist, warnings, "cooling", "Tube taper within swage/expand limit (SP-8087)",
                   tube_taper_ratio <= 6.0,
                   f"A single cooling tube must taper {tube_taper_ratio:.1f}:1 along its run - past "
                   f"SP-8087's 6:1 limit for a swaged (3:1) + expanded (2:1) tube. Add a tube "
                   f"bifurcation (Tube split area ratio) so the tube count doubles downstream.",
                   f"OK - max tube taper {tube_taper_ratio:.1f}:1"
                   + (" (beyond 3.5:1 pure reduction - needs an expansion step, SP-8087)"
                      if tube_taper_ratio > 3.5 else ""))

            if self.tube_hatbands:
                _band_mat = materials.MATERIALS.get(self.tube_hatband_material,
                                                     materials.MATERIALS["inconel_718"])
                _tube_h_m, _ = cooling.channel_target_height_m(
                    geo["throat_dia_m"], _n_tube_base, mdot_coolant_jacket_kgs,
                    self.propellant_pair,
                    (self.regen_channel_land_fraction if self.regen_channel_land_fraction > 0
                     else cooling.CHANNEL_LAND_FRACTION_DEFAULT),
                    aspect_ratio_override=self.regen_channel_aspect_ratio,
                    target_velocity_ms=self.regen_coolant_velocity_ms)
                # Bands run aft of the THROAT over the body's tube wall (plus the
                # extension if toggled): SP-8120 Sec.2.2.1 - a continuous structural
                # shell is normal practice over the chamber/throat, bands take over
                # downstream where wall pressure falls. The chamber (upstream of the
                # throat) keeps the tube_wall continuous-jacket mass below.
                _x0 = float(xs[_i_throat])
                _x1 = (float(ext_xs[-1]) if (self.tube_hatbands_on_extension and has_extension
                                              and len(ext_xs)) else float(body_xs[-1]))
                hatband_result = hatbands.size_bands(
                    xs, rs, _x0, _x1, self.chamber_pressure_pa, gamma, _band_mat,
                    chamber_material, _n_tubes_at, _tube_h_m,
                    shape=(self.tube_hatband_shape
                           if self.tube_hatband_shape in hatbands.BAND_SHAPE_CHOICES else "auto"),
                    count_override=self.tube_hatband_count,
                    width_override_m=self.tube_hatband_width_m,
                    p_amb_pa=0.0 if separated_100pct else PA_SEA_LEVEL,
                    tube_crest_offset_m=_tube_h_m + 2.0 * hatbands.TUBE_WALL_T_REF_M)
                hatband_mass_kg = hatbands.hatband_mass_kg(hatband_result["bands"])
                # SP-8120: bands REPLACE the continuous structural shell where they
                # run, so the tube_wall "structural jacket" mass extra is dropped over
                # the banded fraction of the body's wall area.
                _bx, _br = np.asarray(body_xs, float), np.asarray(body_rs, float)
                if _bx.size >= 2 and hatband_result["n_bands"] > 0:
                    _ds = np.hypot(np.diff(_bx), np.diff(_br))
                    _da = 2.0 * np.pi * 0.5 * (_br[1:] + _br[:-1]) * _ds
                    _xm = 0.5 * (_bx[1:] + _bx[:-1])
                    _in = (_xm >= (hatband_result["shell_end_x_m"] or _x0)) & (_xm <= _x1)
                    hatband_banded_fraction = (float(_da[_in].sum() / _da.sum())
                                               if _da.sum() > 0 else 0.0)
                _check(checklist, warnings, "cooling", "Hatband structural adequacy (SP-8120)",
                       hatband_result["all_ok"],
                       "Hatbands: " + " ".join(hatband_result["advisories"]),
                       f"OK - {hatband_result['n_bands']} bands "
                       f"({'/'.join(hatband_result['shapes_used']) or 'none'}), "
                       f"{hatband_mass_kg:.1f} kg, carry all hoop load"
                       + (f"; worst ring-buckling margin "
                          f"{hatband_result['worst_buckling_margin']:.2f}"
                          if np.isfinite(hatband_result['worst_buckling_margin']) else ""))
        cooling_result["tube_taper_ratio"] = tube_taper_ratio
        cooling_result["hatbands"] = hatband_result
        cooling_result["hatband_mass_kg"] = hatband_mass_kg

        # Extra jacket structure for a non-milled wall construction (tube bundle
        # + jacket / coax outer shell), on top of the bare hoop-stress shell.
        # Only where there's an active coolant loop; milled_channel factor 1.0 -> 0.
        # Structural hatbands replace that shell over the banded fraction (above).
        jacket_structure_mass_kg = 0.0
        if chamber_cooling in ("regenerative", "dump"):
            jacket_structure_mass_kg = mass_model.jacket_structure_mass_kg(
                chamber_wall_mass_kg,
                cooling.JACKET_MASS_CONSTRUCTION_FACTOR.get(self.wall_construction, 1.0)
            ) * (1.0 - hatband_banded_fraction)
        turbopump_mass_kg = cyc["turbopump"]["turbopump_mass_kg"] if cyc["has_turbopump"] else 0.0

        # --- feed-system pump plausibility (structural PLAUSIBILITY flag - see
        # ASSUMPTIONS.md / turbopump_sizing.FEED_DP_PLAUSIBLE_CEILING_PA). The
        # pump is always SOLVED to deliver whatever dp_fuel/dp_ox was just
        # computed above (no starvation failure mode exists by construction -
        # see turbopump_sizing.py's module docstring); this instead flags when
        # the DEMAND itself falls outside real flight-turbopump historical
        # practice [SP-8107 Tables V-VI], the honest proxy for "real hardware
        # may not deliver this flow." Only meaningful where a pump exists
        # (pressure-fed has none - that's a tank-pressure question instead).
        feed_plausibility_detail = ""
        if cyc["has_turbopump"]:
            feed_plausibility_detail = turbopump_sizing.feed_dp_plausibility_warning(dp_fuel, dp_ox) or ""
        _check(checklist, warnings, "turbopump", "Feed-system pump plausibility",
               not feed_plausibility_detail, feed_plausibility_detail,
               "n/a - no turbopump (pressure-fed)" if not cyc["has_turbopump"]
               else f"OK - required dP within {turbopump_sizing.FEED_DP_PLAUSIBLE_CEILING_PA/1e6:.0f} MPa "
                    "of real flight-turbopump practice")

        # --- turbopump preliminary sizing (physics/turbopump_sizing.py) ---
        # Rotor speed / tip speed / stage count / turbine count + shaft arrangement,
        # the DERIVED pump/turbine efficiencies, the physical envelope, and the
        # assembly mass. NOTE: the mass that feeds the dry rollup (tp_sizing
        # "mass_kg") is the [SP-8107 Table I] specific-power trend on shaft power
        # (turbopump_sizing.turbopump_mass_kg); the envelope-volume x density
        # "mass_geometry_kg" is a cross-check only, used to rescale the rendered
        # envelope. The dry-mass modifier is EXACTLY 1.0 for the auto architecture.
        tp_sizing = None
        if cyc["has_turbopump"]:
            drive_gas = cyc.get("drive_gas")   # set by TAP_OFF / FRSC / ORSC / FFSC branches
            if self.cycle in cycles.STAGED_CYCLES:
                turbine_inlet_k = drive_gas["tin_k"]
                turbine_mdot = max(cyc["gg_mdot_kgs"], 1e-6)   # the solved preburner/turbine flow
                turbine_pr = cyc["turbine_pressure_ratio"]      # solved (staged_combustion.py)
            elif self.cycle == cycles.TAP_OFF:
                turbine_inlet_k = drive_gas["tin_k"]
                turbine_mdot = max(cyc["gg_mdot_kgs"], 1e-6)
                turbine_pr = TAP_OFF_PRESSURE_RATIO
            elif self.cycle == cycles.EXPANDER:
                turbine_inlet_k = 250.0  # heated-hydrogen expander turbine, far below combustion
                turbine_mdot = max(cyc["turbopump"]["mdot_fuel_kgs"], 1e-6)
                turbine_pr = EXPANDER_TURBINE_PR
            elif self.cycle == cycles.ELECTRIC_PUMP:
                turbine_inlet_k = 0.0     # no turbine
                turbine_mdot = 1e-6
                turbine_pr = 0.0
            else:  # GAS_GENERATOR
                turbine_inlet_k = gg_gas["tin_k"]
                turbine_mdot = max(cyc["gg_mdot_kgs"], 1e-6)
                turbine_pr = GG_PRESSURE_RATIO
            # Actual specific work the turbine delivers = shaft power / turbine mass flow
            # (what pitchline sizing needs). Zero for electric pump-fed (no turbine).
            turbine_specific_work = (0.0 if self.cycle == cycles.ELECTRIC_PUMP
                                     else cyc["turbopump"]["power_total_w"] / turbine_mdot)
            tp_sizing = turbopump_sizing.size_turbopump(
                cyc, dp_fuel, dp_ox, rho_fuel, rho_ox, self.propellant_pair,
                self.target_vac_thrust_n, self.cycle,
                self.turbopump_arrangement, self.turbine_staging, self.turbopump_material_key,
                turbine_inlet_k=turbine_inlet_k, turbine_specific_work_j_kg=turbine_specific_work,
                turbine_pressure_ratio=turbine_pr, build_quality=build_quality,
                pump_stages_fuel=self.pump_stages_fuel, pump_stages_ox=self.pump_stages_ox,
                eta_pump_fuel_final=eta_pf, eta_pump_ox_final=eta_po, eta_turbine_final=eta_turb,
                motor_mass_kg=cyc.get("motor_mass_kg", 0.0),   # electric pump-fed: motor body in the envelope
                bearing_material_key=self.bearing_material_key,
                enforce_suction_limit=self.enforce_suction_limit, **_suction_kw)
            turbopump_mass_kg = tp_sizing["mass_kg"] * tp_sizing["mass_modifier"]
            tp_detail = "; ".join(tp_sizing["warnings"])
            _check(checklist, warnings, "turbopump", "Turbopump sizing / material feasibility",
                   not tp_sizing["warnings"],
                   f"[turbopump] {tp_detail}",
                   f"OK - {tp_sizing['arrangement'].replace('_', ' ')}, {tp_sizing['n_turbines']} "
                   f"turbine(s), peak tip speed within {tp_sizing['material_display']} limit")

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
        _plumbing_hooks = {"manifold_result": manifold_result,
                           "jacket_manifold_result": jacket_manifold_result}
        turbopump_ports = None
        if tp_sizing and tp_sizing.get("bodies"):
            _fuel_primary = plumbing.hook_for_host(_plumbing_hooks, "jacket_inlet") or \
                plumbing.hook_for_host(_plumbing_hooks, "fuel")
            _ox_hook = plumbing.hook_for_host(_plumbing_hooks, "ox")
            _dis = {"fuel_pump": _fuel_primary["inner_diameter_m"] if _fuel_primary else 0.0,
                    "ox_pump": _ox_hook["inner_diameter_m"] if _ox_hook else 0.0}
            turbopump_ports = geometry3d.turbopump_ports(
                tp_sizing["bodies"],
                geometry3d.turbopump_origin_xyz(float(np.max(xs)), float(np.max(rs)),
                                                tp_sizing["assembly_od_m"]),
                tp_sizing, _dis)
        line_loss_computed = {"fuel": None, "ox": None}
        plumbing_results = []
        plumbing_mass_kg = 0.0
        plumbing_total_length_m = 0.0
        for _run_dict in (self.plumbing_runs or []):
            _run = plumbing.run_from_dict(_run_dict)
            _hook = plumbing.hook_for_host(_plumbing_hooks, _run.host)
            if _hook is None:
                _check(checklist, warnings, "plumbing", f"Plumbing run on '{_run.host}'", False,
                       f"Plumbing run rooted on '{_run.host}' has no such manifold ring in this "
                       f"design (e.g. jacket_return only exists under the F-1 split / J-2 layouts) - "
                       f"it is neither drawn nor counted.")
                continue
            _pump = plumbing.HOST_PUMP.get(_run.host, "fuel_pump")
            _port = None
            if _run.connect_to_pump:
                _port = (turbopump_ports or {}).get(_pump, {}).get("discharge")
                if _port is None:
                    _check(checklist, warnings, "plumbing", f"Plumbing run on '{_run.host}' pump link",
                           False, f"Run on '{_run.host}' is set to connect to the "
                           f"{_pump.replace('_', ' ')}, but this design has no such turbopump "
                           f"port (pressure-fed?) - drawn with a free end, flat line loss kept.", "")
                elif _run.host == "fuel" and plumbing.hook_for_host(_plumbing_hooks, "jacket_inlet"):
                    _check(checklist, warnings, "plumbing", "Fuel ring fed straight from the pump",
                           False, "The fuel injector ring is connected straight to the fuel pump on "
                           "a regeneratively cooled chamber - coolant normally passes through the "
                           "jacket (jacket_inlet ring) first. Allowed; check it is intended.", "")
            _res = plumbing.resolve_run(_run, _hook, _hook["major_radius_m"],
                                        manifold.ring_outer_radius_at(_hook, _run.attach_angle_deg),
                                        supercritical=(_fuel_lh2 and _run.host != "ox"), port=_port)
            _m_total, _m_pipe, _m_flange = plumbing.plumbing_mass_kg(_hook, _res)
            plumbing_mass_kg += _m_total
            plumbing_total_length_m += _res["total_length_m"]
            _loss_pa, _loss_parts = plumbing.run_pressure_loss_pa(
                _res, _hook, plumbing.liquid_viscosity_pa_s(self.propellant_pair, _run.host))
            if _res["closes_on_port"]:
                # valve allowance at the run's slowest (largest-bore) pipe -
                # where a main valve would sit
                _v = min(_res["pipe_velocities_ms"])
                _leg_loss = _loss_pa + (plumbing.VALVE_AND_UNMODELED_K * 0.5
                                        * plumbing.feed_density_kg_m3(_hook) * _v * _v)
                _leg = "ox" if _pump == "ox_pump" else "fuel"
                line_loss_computed[_leg] = max(line_loss_computed[_leg] or 0.0, _leg_loss)
            plumbing_results.append({"host": _run.host, "role": _run.role, "n_pipes": len(_run.pipes),
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
            _check(checklist, warnings, "plumbing",
                   f"Plumbing run on '{_run.host}' geometry ({len(_run.pipes)} pipes)",
                   not _res["advisories"], " ".join(_res["advisories"]),
                   f"OK - {_res['total_length_m']:.2f} m, {_m_total:.1f} kg"
                   + (f", -> {_pump.replace('_', ' ')}, line loss {_loss_pa / 1e3:.0f} kPa"
                      if _res["closes_on_port"] else ""))

        # Rated burn time: ablative chambers are capped by char consumption (the SAME
        # hoop-stress-derived chamber wall thickness used for its mass above ALSO caps how
        # long it can fire before burning through) - matches the real "ablative, no extra
        # time" pattern (testedBurnTime approx= ratedBurnTime) found in RealismOverhaul
        # reference configs. Every other material scales a flat baseline by chamber thermal
        # margin instead (see BASE_RATED_BURN_TIME_S's comment above). Computed before the
        # dry-mass sum because the electric pump-fed cycle's battery mass scales with it.
        if chamber_cooling == "ablative":
            chamber_wall_thickness_m = mass_model.wall_thickness_m(
                self.chamber_pressure_pa, geo["chamber_dia_m"] / 2.0, chamber_material.allowable_stress_pa)
            consumption_rate_m_s = (chamber_material.ablative_consumption_rate_m_s
                                     or materials.ABLATIVE_CONSUMPTION_RATE_M_S)
            # Film overlay on an ablative (LMDE/AJ10-style injector film): char
            # recession taken as ~proportional to the local wall heat flux, so the
            # film's throat flux multiplier scales the rate (Tier 3 - direction
            # sound, magnitude unanchored). No chamber film -> x1.0, unchanged.
            consumption_rate_m_s *= float(film_phi[_throat_idx])
            rated_burn_time_s = mass_model.ablative_rated_burn_time_s(
                chamber_wall_thickness_m, consumption_rate_m_s)
        else:
            margin_mult = margin["margin_ratio"] / materials.THIN_MARGIN_THRESHOLD
            margin_mult = max(RATED_TIME_MARGIN_MULT_MIN, min(RATED_TIME_MARGIN_MULT_MAX, margin_mult))
            rated_burn_time_s = BASE_RATED_BURN_TIME_S * margin_mult

        # Electric pump-fed: size the battery + motor for the whole burn and add
        # their mass. (cyc was built provisionally in the cycle branch; rebuild it
        # now with the real burn time.)
        battery_motor_mass_kg = 0.0
        if self.cycle == cycles.ELECTRIC_PUMP:
            cyc = electric_pump.electric_pump_result(
                mdot, self.mixture_ratio, self.chamber_pressure_pa, dp_fuel, dp_ox,
                rho_fuel, rho_ox, eta_pf, eta_po, self.pump_specific_power_w_kg, rated_burn_time_s)
            battery_motor_mass_kg = cyc["battery_mass_kg"] + cyc["motor_mass_kg"]
            _check(checklist, warnings, "turbopump", "Electric pump-fed hardware mass",
                   battery_motor_mass_kg <= 0.6 * (chamber_wall_mass_kg + bell_wall_mass_kg
                                                   + turbopump_mass_kg + 1e-6),
                   f"Battery + motor ({battery_motor_mass_kg:.0f} kg) is a large fraction of the "
                   f"engine dry mass - electric pump-fed only pays off at small scale / short "
                   f"burn (battery mass scales with burn time). Real electric pump-fed engines "
                   f"(Rutherford) are small and stage their batteries.",
                   f"OK - battery {cyc['battery_mass_kg']:.0f} kg + motor {cyc['motor_mass_kg']:.0f} kg")
            if self.propellant_pair == "LOX/LH2":
                _check(checklist, warnings, "propellant/cycle", "Electric pump-fed with LH2",
                       False,
                       "LH2's very high pump head makes electric pump-fed impractical - the "
                       "real electric pump-fed engine (Rutherford) is kerolox. Treat this "
                       "combination as unflown.")

        # I3 - injector-plate mass (a real, previously-uncounted term - see
        # mass_model.injector_plate_mass_kg). Always on.
        injector_plate_mass_kg = mass_model.injector_plate_mass_kg(
            geo["chamber_dia_m"], self.chamber_pressure_pa)
        _face_area_m2 = np.pi * (geo["chamber_dia_m"] / 2.0) ** 2
        _elem_density = (injector_geometry["n_elements"] / _face_area_m2
                         if _face_area_m2 > 0 else 0.0)
        _check(checklist, warnings, "injector", "Injector element crowding",
               _elem_density <= mass_model.MAX_ELEMENT_DENSITY_PER_M2,
               f"~{_elem_density:,.0f} elements/m^2 on the injector face exceeds a buildable "
               f"~{mass_model.MAX_ELEMENT_DENSITY_PER_M2:,.0f}/m^2 (F-1 ~8000, SSME ~4000) - "
               f"the pattern is over-crowded; use larger orifices or a wider chamber.",
               f"OK - ~{_elem_density:,.0f} elements/m^2")

        computed_dry_mass_kg = (chamber_wall_mass_kg + bell_wall_mass_kg + turbopump_mass_kg
                                + battery_motor_mass_kg + stability_aid_mass_kg
                                + injector_plate_mass_kg + jacket_structure_mass_kg
                                + manifold_mass_kg + jacket_manifold_mass_kg + plumbing_mass_kg
                                + hatband_mass_kg)

        _check(checklist, warnings, "manifold", "Manifold structural mass fraction",
               manifold_mass_kg <= manifold.MANIFOLD_MASS_DRY_FRACTION_WARN
                                    * max(computed_dry_mass_kg, 1e-6),
               f"Manifold mass ({manifold_mass_kg:.0f} kg) is a large fraction of dry mass - "
               f"raise the feed-velocity target or lower chamber pressure to lighten it.",
               f"OK - {manifold_mass_kg:.0f} kg")

        _check(checklist, warnings, "manifold", "Jacket manifold structural mass fraction",
               jacket_manifold_mass_kg <= manifold.MANIFOLD_MASS_DRY_FRACTION_WARN
                                           * max(computed_dry_mass_kg, 1e-6),
               f"Jacket manifold mass ({jacket_manifold_mass_kg:.0f} kg) is a large fraction "
               f"of dry mass - raise the feed-velocity target or lower chamber pressure to "
               f"lighten it.",
               f"OK - {jacket_manifold_mass_kg:.0f} kg")

        if plumbing_results:
            _check(checklist, warnings, "plumbing", "Plumbing structural mass fraction",
                   bool(plumbing_mass_kg <= manifold.MANIFOLD_MASS_DRY_FRACTION_WARN
                        * max(computed_dry_mass_kg, 1e-6)),
                   f"Plumbing (feed pipes + flanges) mass ({plumbing_mass_kg:.0f} kg) is a large "
                   f"fraction of dry mass - shorten the runs or drop flanges.",
                   f"OK - {plumbing_mass_kg:.1f} kg over {plumbing_total_length_m:.2f} m")

        _check(checklist, warnings, "chamber geometry",
               "Combustion completeness vs. L*/atomization", completeness >= 0.95,
               f"Chamber residence time ({residence_time_s*1000:.2f} ms) is short relative to "
               f"what {self.propellant_pair} with {injector.display_name} typically needs "
               f"(~{required_time_s*1000:.2f} ms) - combustion doesn't fully complete before "
               f"the throat, derating c* efficiency by a factor of {completeness:.2f}. "
               f"Increase L* or use a finer-atomization injector (pintle/platelet).",
               f"OK - {completeness:.2f}x completeness")
        _check(checklist, warnings, "injector", "Injector stiffness at throttle floor",
               inj_ok is not False,
               f"Injector stiffness at the {self.throttle_floor*100:.0f}% throttle floor "
               f"is below {injector.display_name}'s ~{injector.min_stable_dp_ratio:.2f} "
               f"dP/Pc chug threshold - this design is not stable that deep.",
               "OK - stable at floor throttle" if inj_ok else
               "Not evaluated (no exact match in the throttle sweep grid)")
        _check(checklist, warnings, "injector", "Injector practical minimum throttle",
               self.throttle_floor >= injector.practical_min_throttle,
               f"{injector.display_name} doesn't typically demonstrate throttling down to "
               f"{self.throttle_floor*100:.0f}% in real engines (representative practical "
               f"minimum ~{injector.practical_min_throttle*100:.0f}%) - this is separate from "
               f"the dP/Pc stiffness check above: an injector can be hydraulically stable at a "
               f"flow it was never actually engineered to reach.")
        inj_suit_warning = injectors.suitability_warning(self.injector_type, self.propellant_pair)
        _check(checklist, warnings, "injector", "Injector type suitability for propellant pair",
               not inj_suit_warning, inj_suit_warning or "")
        ign_warning = ignition.plausibility_warning(self.ignition_system, self.propellant_pair)
        _check(checklist, warnings, "ignition", "Ignition system plausibility",
               not ign_warning, ign_warning or "")

        # Monopropellant/bipropellant cross-checks. A "catalyst bed" only makes sense for a
        # monopropellant (it's a decomposition element, not a two-stream injector) and vice
        # versa; a monopropellant thruster is pressure-fed in every real design (no real
        # engine pumps a single decomposing propellant through a gas-generator/staged/
        # expander turbopump cycle).
        is_mono = combustion.is_monopropellant(self.propellant_pair)
        if is_mono and self.injector_type != "catalyst_bed":
            mono_injector_mismatch_detail = (
                f"{injector.display_name} is a bipropellant injector type; "
                f"{self.propellant_pair} is a monopropellant - a catalyst bed is "
                f"the real analog.")
        elif not is_mono and self.injector_type == "catalyst_bed":
            mono_injector_mismatch_detail = (
                f"Catalyst-bed decomposition doesn't apply to a bipropellant "
                f"combustion chamber ({self.propellant_pair}).")
        else:
            mono_injector_mismatch_detail = ""
        # if/elif above are mutually exclusive by construction (at most one can ever
        # fire) - merged into one checklist entry rather than two so the checklist
        # doesn't show a row that's trivially "passed" for whichever branch didn't apply.
        _check(checklist, warnings, "injector", "Injector type matches mono/bipropellant class",
               not mono_injector_mismatch_detail, mono_injector_mismatch_detail)
        _check(checklist, warnings, "propellant/cycle", "Monopropellant requires pressure-fed cycle",
               not (is_mono and self.cycle != cycles.PRESSURE_FED),
               f"Monopropellant thrusters are pressure-fed in every real design - "
               f"{cycles.CYCLE_DISPLAY[self.cycle]} has no real analog here.")
        _check(checklist, warnings, "chamber geometry", "Contraction ratio within typical range",
               CONTRACTION_RATIO_TYPICAL[0] <= self.contraction_ratio <= CONTRACTION_RATIO_TYPICAL[1],
               f"Contraction ratio {self.contraction_ratio:.2f} is outside the typical "
               f"{CONTRACTION_RATIO_TYPICAL[0]}-{CONTRACTION_RATIO_TYPICAL[1]} range.")
        _check(checklist, warnings, "chamber geometry", "L* within typical range",
               LSTAR_TYPICAL_M[0] <= self.lstar_m <= LSTAR_TYPICAL_M[1],
               f"L* {self.lstar_m:.2f} m is outside the typical "
               f"{LSTAR_TYPICAL_M[0]}-{LSTAR_TYPICAL_M[1]} m range.")
        sl_separation_note = " sl Isp/thrust are nominal placeholders, not physical." if sl_isp_unphysical else ""
        _check(checklist, warnings, "nozzle/aero", "Sea-level nozzle flow attachment",
               not separated_100pct,
               f"Nozzle is separated at sea level even at 100% throttle "
               f"(Pe/Pa={pe_pa/PA_SEA_LEVEL:.3f}) - this is a vacuum/high-altitude "
               f"nozzle, not suited to a sea-level-igniting stage.{sl_separation_note}")
        _check(checklist, warnings, "nozzle/aero", "Expansion ratio validity",
               self.expansion_ratio > 1.0, "Expansion ratio must be > 1.")

        gimbal_warning = gimbal.plausibility_warning(self.gimbal_mode, self.gimbal_range_deg)
        gimbal_pass_detail = ("OK - inherits host part's gimbal" if self.gimbal_mode == "inherit" else
                               "OK - explicitly ungimballed" if self.gimbal_mode == "ungimballed" else
                               f"OK - {self.gimbal_range_deg:.1f} deg within typical band")
        _check(checklist, warnings, "gimbal", "Gimbal range plausibility",
               not gimbal_warning, gimbal_warning or "", gimbal_pass_detail)

        return {
            "inputs": dict(self.__dict__),
            "tc_k": tc, "gamma": gamma, "m_molar": m_molar, "eta_cstar": eta_cstar,
            "completeness_factor": completeness,
            "residence_time_s": residence_time_s, "required_time_s": required_time_s,
            "cstar_ms": cstar, "pe_pc": pe_pc, "pe_pa": pe_pa,
            "nozzle_divergence_efficiency": lam,
            "nozzle_efficiency_vs_reference": lam_relative,
            "theta_n_deg": theta_n_deg, "theta_e_deg": theta_e_deg,
            "mdot_kgs": mdot,
            "isp_vac_chamber_s": isp_vac_chamber, "isp_sl_chamber_s": isp_sl_chamber,
            "isp_vac_engine_s": isp_vac_eng, "isp_sl_engine_s": isp_sl_eng,
            "thrust_vac_n": thrust_vac, "thrust_sl_n": thrust_sl,
            "thrust_vac_floor_n": thrust_vac_floor,
            "separated_at_100pct_sl": separated_100pct,
            "cycle_result": cyc,
            "geometry": geo,
            "profile_xs_m": xs, "profile_rs_m": rs, "profile_meta": profile_meta,
            "throttle_sweep": rows,
            "separation_onset_throttle": onset,
            "injector_stiffness_ok_at_floor": inj_ok,
            "material_margin": margin,
            "bell_material_margin": bell_material_margin,
            "chamber_heat_flux_factor": chamber_heat_flux_factor,
            "t_local_at_transition_k": t_local,
            "eps_for_transition": eps_for_transition,
            "cooling": cooling_result,
            "injector_geometry": injector_geometry,
            "chamber_acoustics": chamber_acoustics,
            "stability": stability_result,
            "stability_aid_mass_kg": stability_aid_mass_kg,
            "injector_dp_pa": dp_injector,
            "injector_dp_nominal_pa": dp_injector_nominal,
            "injector_dp_derived_pa": dp_injector_derived,
            "injector_dp_fuel_pa": dp_injector_fuel,
            "injector_dp_ox_pa": dp_injector_ox,
            "orifice_cd": orifice_cd,
            "chamber_flow": chamber_flow,
            "pc_feed_pa": pc_feed,
            "stay_time_s": stay_time_s,
            "chamber_l_over_d": chamber_l_over_d,
            "convergent_half_angle_deg": conv_half_angle,
            "injector_plate_mass_kg": injector_plate_mass_kg,
            "manifold_result": manifold_result,
            "manifold_mass_kg": manifold_mass_kg,
            "jacket_manifold_result": jacket_manifold_result,
            "jacket_manifold_mass_kg": jacket_manifold_mass_kg,
            "plumbing_results": plumbing_results,
            "turbopump_ports": turbopump_ports,
            "line_loss_fuel_pa": line_loss_fuel_pa,
            "line_loss_ox_pa": line_loss_ox_pa,
            "line_loss_source": {"fuel": "computed" if _llo.get("fuel") is not None else "flat",
                                 "ox": "computed" if _llo.get("ox") is not None else "flat"},
            "line_loss_computed": line_loss_computed,
            "line_loss_residual_pa": 0.0,
            "plumbing_mass_kg": plumbing_mass_kg,
            "plumbing_total_length_m": plumbing_total_length_m,
            "cooling_flow_topology": self.cooling_flow_topology,
            "jacket_inlet_eps_effective": jacket_inlet_eps_eff,
            "jacket_return_split_fraction": jacket_return_split_fraction,
            "manifold_bypass_fraction": self.manifold_bypass_fraction,
            "turbopump_sizing": tp_sizing,
            "chamber_wall_mass_kg": chamber_wall_mass_kg,
            "bell_wall_mass_kg": bell_wall_mass_kg,
            "body_wall_thickness_m": body_wall_thickness_m,
            "ext_wall_thickness_m": ext_wall_thickness_m,
            "jacket_structure_mass_kg": jacket_structure_mass_kg,
            "hatband_mass_kg": hatband_mass_kg,
            "jacket_overpressure_ok": jacket_overpressure_ok,
            "jacket_worst_station_eps": jacket_worst_station_eps,
            "jacket_pressure_at_worst_station_pa": jacket_pressure_at_worst_station_pa,
            "jacket_local_gas_pressure_at_worst_station_pa": jacket_local_gas_pressure_at_worst_station_pa,
            "jacket_overpressure_worst_station": jacket_overpressure_worst_station,
            "jacket_combined_stress_pa": jacket_combined_stress_pa,
            "jacket_hoop_stress_pa": jacket_hoop_stress_pa,
            "jacket_thermal_stress_pa": jacket_thermal_stress_pa,
            "computed_dry_mass_kg": computed_dry_mass_kg,
            "rated_burn_time_s": rated_burn_time_s,
            "warnings": warnings,
            "checklist": checklist,
        }
