"""The EngineDesign dataclass: every design input (fields), project-file
(de)serialisation, and compute() - which runs the stage pipeline in
physics/design/*_stage.py."""
from dataclasses import dataclass, field

import numpy as np

from .. import (cooling, cycles, manifold, materials)

from . import (combustion_stage, feed_stage, cooling_stage, geometry_stage, manifold_stage, margins_stage, structure_stage, turbomachinery_stage, rollup_stage)
from .state import PassState


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
    # Turbine-exhaust handling, open cycles only (gas generator / tap-off) -
    # physics/turbine_exhaust.py. Closed cycles ignore it (warn row if set).
    turbine_exhaust_mode: str = "overboard_duct"  # "overboard_duct" (RS-68 / LR-87 / LR-91 /
                                                   # H-1C) | "aspirator" (H-1D shroud + annular
                                                   # exit slot [H1-Man]) | "nozzle_injection"
                                                   # (F-1 / J-2: into the main nozzle + a gas
                                                   # film on the wall downstream).
    turbine_exhaust_nozzle_eps: float = 1.0       # overboard only: 1.0 = plain sonic duct exit;
                                                   # > 1 = shaped exhaust nozzle (LR-87/LR-91).
    turbine_exhaust_cant_deg: float = 0.0         # overboard only: exhaust-nozzle cant off the
                                                   # engine axis - axial thrust x cos, side force
                                                   # / roll torque reported (LR-91 roll nozzle).
    turbine_exhaust_inject_eps: float = 10.0      # nozzle_injection: supersonic area ratio of the
                                                   # exhaust manifold (F-1 10:1 [SP-8120]; J-2
                                                   # 10.45-11.40 cat-eyes).
    aspirator_fwd_length_frac: float = 0.30       # aspirator: shroud start, as a fraction of the
                                                   # throat-to-exit length forward of the exit
                                                   # (H-1D: ~20 in forward of the exit on its
                                                   # 8:1 bell [H1-Man §1-51]). Geometry only.
    aspirator_overhang_frac: float = 0.05         # aspirator: shroud extension past the exit, as
                                                   # a fraction of the exit diameter (Tier 3 -
                                                   # [H1-Man] says "extending beyond", no size).
    turbine_exhaust_hx_gox_kgs: float = 0.0       # LOX->GOX pressurant heat exchanger in the
                                                   # exhaust (H-1 [H1-Man §1-47]): GOX flow it
                                                   # heats, kg/s. 0 = none. LOX pairs only.
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
    SCHEMA_VERSION = 9   # 9 (2026-09-24): turbine_exhaust_* / aspirator_* fields added
                         # (physics/turbine_exhaust.py) - no key migration; a v8 file's
                         # new fields take defaults (overboard duct, sonic exit, no HX).
                         # 8 (2026-09-23): film became an OVERLAY - "film" is no longer a
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
        """The one entry point. Two circular dependencies are broken with ONE
        extra pass each (both ride the same second pass):
        - a plumbing run connected to a turbopump port (plumbing.PlumbingRun.
          connect_to_pump): line loss -> pump dP -> pump size -> port position
          -> run geometry -> line loss. Pass 1 uses the flat LINE_LOSS_PA, pass
          2 pass 1's computed per-leg losses (residual: line_loss_residual_pa).
        - turbine exhaust injected into the nozzle (turbine_exhaust_mode
          "nozzle_injection"): its gas film cools the nozzle wall, but the
          GG/tap-off flow and exhaust temperature are only known after the
          pump stage, which runs after the thermal solve. Pass 2 applies pass
          1's film (residual: turbine_exhaust["film_residual_kgs"]).
        Neither -> one pass, bit-identical to before.

        Open cycles (gas generator / tap-off) then CLOSE ON THE TARGET THRUST:
        their turbine flow is extra propellant whose exhaust adds (a little)
        thrust, so the chamber flow is rescaled until chamber + exhaust thrust
        (with every Isp adjustment) equals target_vac_thrust_n (thrust is ~linear
        in chamber flow: 2-3 iterations; reported as thrust_closure_scale).
        Closed cycles keep target = chamber-flow sizing, unchanged."""
        from .. import cycles as _cycles
        open_cycle = self.cycle in (_cycles.GAS_GENERATOR, _cycles.TAP_OFF)
        scale = 1.0
        for _ in range(6 if open_cycle else 1):
            result = self._compute_passes(scale)
            if not open_cycle:
                break
            err = self.target_vac_thrust_n / result["thrust_vac_n"]
            if abs(err - 1.0) < 1e-9:
                break
            scale *= err
        if open_cycle:
            result["thrust_closure_scale"] = scale
        return result

    def _compute_passes(self, mdot_scale):
        """One (or two - see compute()) full pipeline passes at a chamber-flow scale."""
        result = self._compute_pass(None, mdot_scale=mdot_scale)
        computed = result.get("line_loss_computed") or {}
        need_ll = any(v is not None for v in computed.values())
        te = result.get("turbine_exhaust") or {}
        te_carry = te.get("film_carry")
        if need_ll or te_carry:
            result = self._compute_pass(computed if need_ll else None, te_film=te_carry,
                                        mdot_scale=mdot_scale)
            if need_ll:
                again = result.get("line_loss_computed") or {}
                result["line_loss_residual_pa"] = max(
                    (abs((again.get(k) or 0.0) - (computed.get(k) or 0.0)) for k in computed),
                    default=0.0)
            if te_carry and result.get("turbine_exhaust"):
                result["turbine_exhaust"]["film_residual_kgs"] = abs(
                    result["turbine_exhaust"]["mdot_kgs"] - te_carry["mdot_kgs"])
        return result

    def _compute_pass(self, line_loss_override, te_film=None, mdot_scale=1.0):
        """One full compute pass, as an ordered pipeline of stage functions
        (physics/design/*_stage.py). Values handed from one stage to a later
        one live on the PassState `s`; see design/state.py."""
        s = PassState()
        s.line_loss_override = line_loss_override
        s.te_film_carry = te_film
        s.mdot_scale = mdot_scale
        combustion_stage.combustion_setup(self, s)
        combustion_stage.nozzle_performance(self, s)
        geometry_stage.contour(self, s)
        feed_stage.injector_and_cooling_routing(self, s)
        cooling_stage.thermal(self, s)             # unified thermal solve, before the pumps
        feed_stage.turbomachinery_cycle(self, s)
        geometry_stage.chamber_detail(self, s)
        cooling_stage.thermal_reporting(self, s)
        cooling_stage.nozzle_extension_thermal(self, s)
        cooling_stage.coolant_capacity_and_isp(self, s)
        manifold_stage.injector_and_manifolds(self, s)
        margins_stage.thermal_margins(self, s)
        manifold_stage.jacket_manifolds_and_stability(self, s)
        structure_stage.wall_structure(self, s)
        structure_stage.tubes_and_hatbands(self, s)
        turbomachinery_stage.turbopump_and_plumbing(self, s)
        rollup_stage.burn_time_and_mass(self, s)
        return rollup_stage.checks_and_result(self, s)
