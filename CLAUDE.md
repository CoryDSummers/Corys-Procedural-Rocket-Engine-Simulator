## Cost & Token Safety
- **Token Constraints**: You must always inform the user and ask for explicit confirmation before starting any task that will consume a large amount of tokens.
- **Trigger Actions**: This includes reading files larger than 50KB, processing entire deep directories, or running long, multi-step automated refactoring tasks.
- **Format**: State the estimated scale of the task (e.g., "This requires reading 3 large files...") and wait for a `y/n` confirmation.

# KSP RealismOverhaul/RP-1 engine modding

Two related but separate lines of work in this directory. Read this file first in any
new session before exploring further — it should make re-exploration unnecessary for
routine continuation work.

`upstream/` holds local shallow clones of the three upstream GitHub repos this project
builds on (`KSP-RO/RealismOverhaul`, `KSP-RO/RP-1`, `KSP-RO/ROEngines`) — reference/study
material only, never redistributed. See `UPSTREAM_REPOS.md` for what's in each, exact
commit hashes, licensing, and a precise pointer into RP-1's tech-tree file
(`RP0TechTree.cfg`) for `TechRequired` node IDs.

## 1. Fictional custom engines (standalone RO/RF add-on `.cfg` files)

- `H3-250K_Config.cfg` / `H3-250K-V_Config.cfg` — "H-3-250K" (1975 uprate of RO's
  `H-2-250K`), booster (eps~12) + sustainer (16AR) + vacuum (H-3-250K-V) variants on the
  stock H-1 part. RP-1-gated at `orbitalRocketry1972`/`1976`.
- `H4-250K_Config.cfg` — "H-4-250K" (~1978 clean-sheet follow-on), base (eps~14) +
  `SUBCONFIG 20AR` (eps~20) on the H-1 part. Numbers came from a one-off Python test bed at
  `sim/` (isentropic.py/engine_physics.py/h4_report.py) — frozen, not touched since. RP-1
  gated at `orbitalRocketry1976`.
- `TR341_Config.cfg` — "TR-341", a TRW-style hypergolic pressure-fed lunar-lander thruster
  (pintle, MON10/MMH), sized for a cluster of 4 landing a ~3.5 t probe. RP-1 gated at
  `advancedUncrewedLanding`. Needs its `TR341_HOST_PART` placeholder bound to a real part
  name before it does anything (see the file's own header) - the model-binding gap that
  motivated `engine_designer/`'s "pick a host model" catalog feature.
- `Engine_Configs/` is a **read-only reference copy** of RealismOverhaul's actual engine
  configs (~424 files) - the source of every real-engine number used anywhere in this
  project (spec-table headers, real Isp/Pc/eps figures). Never modify it; it's there to
  grep/read for reference data and spot-check targets. Confirmed byte-identical to the
  full upstream `upstream/RealismOverhaul` clone as of that repo's `25a536b` (see
  `UPSTREAM_REPOS.md` §4) - this flat copy remains the one `build_catalog.py` actually
  scrapes; no need to point it at `upstream/` instead.
- `H1_Config.cfg` at the top level is a stray duplicate of `Engine_Configs/H1_Config.cfg` -
  harmless, never edited.

**Convention that shaped all of the above**: never invent an Isp/thrust/mass number from
nothing - derive it from a real analog engine in `Engine_Configs/`, or (for the H-4) from
first-principles isentropic-flow calculations in a throwaway Python script, and say which.

## 2. `engine_designer/` - interactive custom-engine design tool

A standalone Python/Tkinter app (unrelated to the files above except that it can export
configs in the same style) for designing NEW custom engines from scratch: propellant,
chamber pressure, expansion ratio, nozzle shape (conical/Rao-bell), cycle (gas generator/
pressure-fed/tap-off/FRSC/ORSC/FFSC/expander/electric pump-fed - each with its own physics
in `physics/staged_combustion.py` / `expander.py` / `electric_pump.py`), injector type, ignition system, materials
(separate chamber + nozzle-extension choices), L*/contraction ratio - with a live 2D
schematic, a live 3D preview, and RF `.cfg` export (three output modes: append a CONFIG to
an existing RO part, or spin up a new standalone part that borrows an existing part's model
uniformly rescaled to the designed engine's length). Projects save/load as JSON via the
File menu.

**Start here, not by re-reading the code:**
- `engine_designer/README.md` - what it covers, what it doesn't, how to run it and its
  verification suite.
- `engine_designer/ASSUMPTIONS.md` - a full audit of every constant that ISN'T derived,
  tiered by confidence (validated / calibrated estimate / arbitrary-but-reasonable
  default). Read this before trusting or tweaking any specific number.

**Load-bearing conventions - apply these to any future addition to this tool:**
1. **Any new propellant pair or engine-physics addition gets spot-checked against a real
   RealismOverhaul engine** from `Engine_Configs/` before it's trusted - find a real engine
   with the right propellant, pull its real Pc/eps/MR/Isp from its header comment, solve for
   what `eta_cstar` (or equivalent) reproduces its real Isp, and add it to
   `physics/validate.py`'s `SPOT_CHECKS`. This is what caught a real double-counting bug
   once (nozzle-divergence efficiency was being applied twice) - it's not optional rigor.
2. **Warn, don't block**, for every cross-cutting design-choice check (material thermal
   margin, injector/propellant suitability, ignition plausibility, expander feasibility,
   monopropellant/bipropellant injector mismatch). This is a modding aid, not a hard
   simulator - the user picks, the tool tells them the consequence.
   **One deliberate exception (2026-09-23, Cory's call): physically meaningless
   material/cooling-method combos are HARD-BLOCKED** - regen on an ablative, ablative on a
   metal, a regen C-C/refractory wall, radiative copper (`materials.Material.
   allowed_cooling_methods` + `cooling.resolve_cooling_method_checked`: coerced to the
   material's own method + a failing checklist row; the GUI dropdown only lists allowed
   ones). Block only where the *construction doesn't exist*; merely risky combos stay
   warn-only. Don't extend blocking to anything else without asking.
3. **Plan mode before any non-trivial feature**: every round of work on this tool
   (bell nozzles, injector types, new cycles, the 3D preview, new propellant pairs) went
   through `EnterPlanMode` → a written plan → `ExitPlanMode` approval before implementation.
   Keep doing this for anything touching more than one file or adding new physics.
4. **This sandbox has no `$DISPLAY`.** `gui/app.py` and its Tkinter code can only be
   syntax/import-checked and code-reviewed here, never actually clicked through - say so
   explicitly, and ask the user to run it and report back rather than claiming it works.
   The same applies to `gui/preview3d_gl.py` (the OpenGL 3D-preview widget) - and there
   `PyOpenGL`/`pyopengltk` (see `requirements.txt`) aren't even installed here, so that
   module can't be imported at all, only syntax-checked; its pure-numpy mesh/camera/
   colormap math lives separately in the `gui/preview3d_gl_core/` package (split by
   geometry-operation kind: `hardware_constants.py`/`profile_geometry.py`/
   `mesh_primitives.py`/`duct_meshes.py`/`tube_bundle.py`/`shell_mesh.py`/
   `camera_color.py`, re-exported unchanged through `__init__.py`, with `__main__.py`
   running every submodule's own self-test as one combined banner), and its per-part
   mesh assembly (what used to be `preview3d_gl.py`'s own ~830-line `_build_mesh_data`
   method - it never touched `self`) lives in `gui/mesh_builder.py`. Both are runnable/
   self-tested here (no OpenGL/Tk import) - keep new 3D-preview math/mesh-assembly logic
   in that split when extending it, per the same testable/untestable line this round
   established.
5. Run the full verification suite after any physics change. Prefer
   `./verify_all.sh` from the repo root — it runs every module below, keeps full
   output in `verify_output.log`, and prints only a PASS/FAIL line per module
   (full output inline only for a failing one), which is far cheaper on tokens
   than running each command separately. Use the individual commands only when
   debugging a specific failure in detail:
   ```
   cd /home/cory/ksp_config
   python3 -m engine_designer.physics.isentropic
   python3 -m engine_designer.physics.nozzle_shapes
   python3 -m engine_designer.physics.geometry3d
   python3 -m engine_designer.physics.combustion
   python3 -m engine_designer.physics.mixture_ratio
   python3 -m engine_designer.physics.cooling
   python3 -m engine_designer.physics.combustion_stability
   python3 -m engine_designer.physics.injectors
   python3 -m engine_designer.physics.manifold       # propellant intake manifold sizing/mass
   python3 -m engine_designer.physics.plumbing       # procedural manifold-rooted pipe runs
                                                     # (chained segments, per-joint elbows/
                                                     # flanges, mass) - the Shape Lab's model
   python3 -m engine_designer.physics.mass_model     # pre-existing self-test, not previously
                                                     # listed here - added while touching it
   python3 -m engine_designer.physics.hatbands       # structural tube-bundle retaining bands
                                                     # (section polygons, span march, sizing)
   python3 -m engine_designer.physics.staged_combustion  # solved preburner power balance / pressure chain
   python3 -m engine_designer.physics.electric_pump
   python3 -m engine_designer.physics.reliability
   python3 -m engine_designer.physics.cost_model
   python3 -m engine_designer.physics.turbopump_materials
   python3 -m engine_designer.physics.turbopump_efficiency
   python3 -m engine_designer.physics.turbopump_sizing
   python3 -m engine_designer.physics.validate      # the important one - 7 real engines
                                                     # (incl. Raptor-2 methalox, Sprite HTP),
                                                     # both isolated and full-pipeline;
                                                     # also GG-bleed, wall-heat-flux (Bartz
                                                     # h_g + computed wall temp), injector-
                                                     # geometry, combustion-stability,
                                                     # turbopump-sizing, turbopump-
                                                     # efficiency and per-cycle-model
                                                     # (RD-180/SSME/J-2X/Rutherford/...)
                                                     # real-engine spot checks
   python3 -m engine_designer.catalog.build_catalog
   python3 -m engine_designer.catalog.build_roengines_models  # validates/rebuilds the
                                                     # roengines_models.json model-height
                                                     # snapshot (auto-finds upstream/ROEngines;
                                                     # falls back to ROENGINES_DIR/../ROEngines)
   python3 -m engine_designer.export.cfg_writer  # 3 output-mode renders + brace/token checks
   python3 -m engine_designer.gui.schematic
   python3 -m engine_designer.gui.preview3d          # matplotlib 3D preview (kept as fallback)
   python3 -m engine_designer.gui.preview3d_gl_core  # OpenGL preview's pure-numpy mesh/camera/
                                                     # colormap layer - no OpenGL/pyopengltk/Tk
                                                     # import, so this IS runnable/self-tested here
   python3 -m engine_designer.gui.mesh_builder       # per-part mesh-assembly logic split out of
                                                     # the OpenGL-only preview3d_gl.py - newly
                                                     # testable here for the same reason as
                                                     # preview3d_gl_core above
   python3 -m engine_designer.gui.shape_lab_geometry # Shape Lab scenes: the REAL jacket-inlet
                                                     # ring + plumbing run (build_plumbing_scene,
                                                     # via mesh_builder.build_plumbing_pieces) and
                                                     # the synthetic fallback ring (pure numpy, no
                                                     # Tk/OpenGL) - same testable split as above
   python3 -m engine_designer.gui.injector_face
   python3 -m engine_designer.gui.turbopump_diagram
   python3 -m engine_designer.gui.project_io   # design save/load round-trip
   python3 -c "import ast; ast.parse(open('engine_designer/gui/app.py').read())"  # GUI: syntax only
   python3 -c "import ast; ast.parse(open('engine_designer/gui/preview3d_gl.py').read())"  # GL
                                                     # widget layer: syntax only - imports OpenGL/
                                                     # pyopengltk + needs a live display, neither
                                                     # available here
   python3 -c "import ast; ast.parse(open('engine_designer/gui/shape_lab.py').read())"  # Shape
                                                     # Lab window: syntax only - Tk/matplotlib-3D
                                                     # window needs a live display, not available
                                                     # here (though the module itself imports fine)
   ```
   All should exit 0. `validate.py` should print "ALL ... WITHIN TOLERANCE" twice plus
   "ALL GG-BLEED CHECKS OK", "ALL COOLING CHECKS OK", "ALL INJECTOR-GEOMETRY CHECKS OK",
   "ALL GAS-CENTERED-SWIRL INJECTOR CHECKS OK", "ALL COMBUSTION-STABILITY CHECKS OK",
   "ALL CHAMBER-DETAIL CHECKS OK", "ALL TURBOPUMP-SIZING CHECKS OK",
   "ALL BEARING-DN PLAUSIBILITY CHECKS OK" (a plausibility check, not a validated spot check
   - see its own docstring), "ALL TURBOPUMP-EFFICIENCY CHECKS OK", "ALL CYCLE-MODEL CHECKS OK",
   "ALL EXPLICIT-COOLING CHECKS OK", "ALL CR-SENSITIVITY CHECKS OK", "ALL MASS MODEL
   SENSITIVITY CHECKS OK", "ALL JACKET-OVERPRESSURE PLAUSIBILITY CHECKS OK", "ALL
   JACKET-OVERPRESSURE SAMPLE-CALC SPOT CHECKS OK", "ALL MANIFOLD BYPASS-FRACTION CHECKS OK",
   "ALL TWO-PASS COOLING CHECKS OK" (the J-2 layout, 2026-09-22), "ALL FEED-SYSTEM
   PLAUSIBILITY CHECKS OK" and "ALL HATBAND PLAUSIBILITY CHECKS OK" (structural retaining
   bands + swaged-tube taper, 2026-09-23 - plausibility, not a spot check) and "ALL COUPLED
   WALL-TEMPERATURE CHECKS OK" ("channels"-mode throat wall balance with the RP-1 carbon-deposit
   h_g credit - F-1/SSME plausibility + lever monotonicity + flat-mode pin, 2026-09-23) and "ALL
   COOLING-COMPATIBILITY CHECKS OK" (material x method hard block + the schema-8 "film" migration)
   and "ALL FILM-OVERLAY CHECKS OK" (two-site post-jacket film overlay - plausibility incl. an
   [EUCASS-2023] regen+7%-film analog, not a spot check; both 2026-09-23) and "ALL PUMP
   PRESSURE-CHAIN CHECKS OK" (solved staged-combustion power balance vs SSME/RD-0124/NK-33 +
   RL10 expander discharge/Pc, 2026-09-23) (25 banners
   total - the old "15" here had drifted stale;
   `python3 -m engine_designer.physics.validate | grep -c '^ALL'` is the quick count).

**Layout**: `physics/` (all computation - `design.py`'s `EngineDesign.compute()` is the one
entry point everything else calls; incl. `cooling.py` = real Bartz gas-side h_g (transport
props derived in `combustion.py`) + computed hot-gas-wall temperature + radiation-equilibrium
solve + regen Isp credit + `absolute_heat_flux_profile` (the AUTHORITATIVE wall-heat-flux
distribution since Phase 7 - real per-station Bartz h_g x (T_aw-T_wg), calibrated PER
PROPELLANT CLASS against real engines via `BARTZ_ABS_FLUX_CALIBRATION` - LOX/RP-1 and LOX/LH2
independently anchored, since a single flat constant can't fit both; `expander.py`'s turbine
heat pickup integrates the identical profile) + `solve_wall_balance` ("channels"-mode coupled throat wall temperature: gas film ->
wall -> coolant, RP-1 carbon-deposit h_g credit `GAS_SIDE_DEPOSIT_FACTOR`, user coolant velocity
`EngineDesign.regen_coolant_velocity_ms` - the chamber thermal margin's driver in that mode) +
`film_effectiveness_profile`
(length-decaying fuel-film curtain flux multiplier, replacing the old flat knockdown) - film is an
OVERLAY on every section method (NOT a method since 2026-09-23), at TWO sites combined by
`combined_film_phi`: the chamber curtain (`film_cooling_fraction`, face or a convergent ring at
`chamber_film_inject_area_ratio`) + a nozzle-extension slot (`nozzle_film_fraction` at
`nozzle_film_inject_eps`, `nozzle_film_effectiveness_profile`, Isp-costed like dump flow), both
fed POST-JACKET fuel at jacket-exit temp; `film_adiabatic_wall_temp` lowers T_aw per station
(throat check, worst-station extension check, and `solve_wall_balance_profile` = the
"channels"-mode FULL-LENGTH coupled wall balance on the march's per-station
`h_c_profile_w_m2k`/`t_bulk_profile_k`, reporting the hottest station + zone as a warn-only row);
all glued in `EngineDesign._film_phi` + `resolve_cooling_method_checked`
(the explicit per-section `chamber_cooling_method`/`nozzle_cooling_method` choice, `"auto"`
= infer from the material, which drives jacket-dP fraction / rated burn time / regen credit /
fatigue routing in `design.py`) + `WALL_CONSTRUCTIONS` (`EngineDesign.wall_construction`:
milled_channel ref / tube_wall / coax_shell - scales coolant-side h_c, jacket dP and
`mass_model.jacket_structure_mass_kg`) + `EngineDesign.regen_nozzle_end_eps` (extends active
regen OR dump cooling past the bell-material transition to a full-length regen nozzle or a
dump-cooled slice, via one shared `cooled_length_eps` cutoff also fed to
`expander.cooled_surface_area`) + `dump_cooling_isp_penalty_fraction`/`size_dump_coolant_fraction`
(`EngineDesign.dump_coolant_fraction` - nozzle-extension-only dump cooling, ejected overboard for
a net Isp cost, Vulcain HM-60/J-2 anchored); `combustion_stability.py` =
chamber acoustic modes (1L/1T/1R) + selectable stability aids (injector-face baffles /
corner Helmholtz cavities / stiffer injector) that resolve the acoustic advisory and carry
a mass/c*/feed-pressure cost; `injectors.py` also derives element geometry (velocities,
orifice count, momentum ratio, resultant beta angle), element-pattern subtypes, Cd by
orifice geometry and a per-stream fuel/ox dP split; `manifold.py` sizes the propellant intake
manifold itself (real fuel/ox tori upstream of the injector orifices - every header ring is
SPLIT (sized on half its mdot, fed at one inlet) and TAPERED round each branch
(per-ring `fuel_/ox_manifold_taper_blend`/`jacket_inlet_taper_blend`, 0 = constant area .. 1 = constant velocity, SP-8087 §3.1.2.1's
"between the two"; `ring_flow_radius_at`/`ring_outer_radius_at`; `outer_radius_m` = the inlet
max, `inner_diameter_m` = the FULL-flow feed bore the pipe carries); injector-ring velocity
from per-ring `fuel_/ox_manifold_head_fraction` (head = f x that leg's injector dP), jacket-ring
velocity = the local coolant-passage velocity (`cooling.passage_velocity_ms`) x `jacket_inlet_velocity_mult`
(schema 6: an old file's global head fraction/taper seeds every ring), all warned
against SP-8087's 61 m/s liquid limit (not LH2) - see ASSUMPTIONS.md; mass from hoop stress
against `pc_feed` + that leg's injector dP; each per-propellant result also carries a frozen, data-only "hook point" -
attachment position/direction/bore/mdot - for a future plumbing/piping feature) AND the
regen-cooling jacket's own coolant-supply ring(s) (`size_jacket_manifolds`, fuel only -
`EngineDesign.cooling_flow_topology`: "single_pass_countercurrent", one ring at the bell
end; real-J-2-sourced "j2_mid_nozzle_inlet", an inlet ring at `jacket_inlet_eps` + the aft
turnaround collar, with its OWN two-pass march (`cooling.march_coolant_two_pass`: down n/2
tubes to the cooled end, back up n - the J-2's 180/360 - "channels" regen model only; 3D down
tubes start at the inlet ring = its tube split, `tube_split_eps` ignored; aft return drawn as the
F-1's end band); the 3D tube-drawing style is DERIVED from the topology
(`design.REGEN_CIRCUIT_STYLE_BY_TOPOLOGY`: single_pass_upflow/f1_double_pass/j2_two_pass - the old
`regen_circuit_style` field + dropdown are deprecated/ignored); vs. real-F-1-sourced "f1_split_reverse_flow", a forward jacket-inlet ring + an aft
jacket-return turnaround ring - a small common-annulus collar flush on the wall, bore =
`TURNAROUND_BORE_PASSAGE_MULT` x local coolant-passage height, NOT a header-sized torus; split by `manifold_bypass_fraction`; geometry/mass only, plus
one lumped-thermal approximation treating the down/return legs as a single combined thermal
unit rather than modeling both interleaved streams - see ASSUMPTIONS.md); `plumbing.py` =
procedural plumbing built ON those hook points (`EngineDesign.plumbing_runs`, the one list-valued
field: each run = a manifold root (`host` = "jacket_inlet"/"jacket_return"/"fuel"/"ox", attach
angle around the engine axis + poloidal angle around the ring tube) + a chain of `PipeSegment`s
(length x its own pipe dia, yaw/pitch +/-90 deg vs. the previous pipe's frame, per-joint elbow radius,
flange-at-end, `bore_scale` = own bore / the hook's full-flow feed bore; pipe 1 starts at the ring's
local inlet bore and cones to its own bore through a reducer, `REDUCER_LENGTH_DIA_MULT`) + one shared
flange style (sized per joint at the local bore); `resolve_run` gives waypoints/joint frames/advisories,
`plumbing_mass_kg` adds pipe+flange mass to the dry rollup; edited in the Shape Lab
(`gui/shape_lab.py`'s `PlumbingLabPanel`, opened per host from `gui/app.py`'s **Plumbing** tab -
one status/Edit/Clear row per `plumbing.HOSTS` entry, labels/hints/roles in `HOST_LABELS`/
`HOST_MISSING_HINT`/`HOST_*_ROLE`, so a new host is one dict entry each; that tab also holds the
per-ring manifold sizing sliders (fuel / ox / jacket inlet groups); runs are seeded from `default_run_for_host` = the old auto-drawn
jacket-inlet duct), drawn by `gui/mesh_builder.build_plumbing_pieces` in BOTH the Lab and the main
3D preview, where a baked jacket_inlet run replaces the legacy auto duct; the Lab also ghosts the
turbopump (placed via `geometry3d.turbopump_origin_for_result`, shared by both previews, the Lab
and design.py); each pump has inlet/discharge HOOK POINTS (`geometry3d.turbopump_ports` ->
`result["turbopump_ports"]`: pos/dir/bore; inlet = eye dia `turbopump_sizing.inlet_eye_dia_m`,
discharge = the downstream ring's feed bore) drawn as nozzle stubs; a run with `connect_to_pump`
gets two AUTO legs closing it onto `plumbing.HOST_PUMP[host]`'s discharge port (re-solved per
caller, so it always lands on the port; "Route to pump" = `plumbing.seed_route_to_port`), an
unconnected run still gets the straight ray; a connected run's `plumbing.run_pressure_loss_pa`
(+ `VALVE_AND_UNMODELED_K`) REPLACES the flat `design.LINE_LOSS_PA` for that pump leg via a
two-pass `compute()` (`_compute_pass`; no connected run = one pass, bit-identical); per-pump
`npsh_available_fuel_ft`/`_ox_ft` (0 = off) cap pump rpm at the suction-specific-speed limit
(`turbopump_sizing.suction_limited_rpm`); every node carries `kind`/`role` tags for future features
to walk); `combustion.py` adds `chamber_flow`
(finite-contraction-ratio chamber Mach + injector-end Pc rise), per-pair L* defaults and
`residence_time_from_lstar_s` (the residence-time chamber-sizing method's L*-equivalent);
`geometry.chamber_geometry` sizes chamber volume by L* OR by a target combustion residence
time, and its contour carries a throat-radius fillet + an optional cylinder->convergent
wall fillet (`chamber_wall_fillet_r_over_rt`, volume-corrected so L**At stays exact);
`nozzle_shapes.py`'s bell `(theta_n,theta_e)` table is the Sutton Fig 3-14 Rao-TOP
digitization (validate.py C6 vs F-1/J-2/RS-25) and its contour now includes the ~0.382*Rt
throat arc; `hatbands.py` = structural tube-wall retaining bands [SP-8120]: continuous shell aft of the
throat until the allowable tube span (fixed-fixed tube beam) reaches 3 band widths, then bands
marched at that span, each a flat/tee/hat/channel/box polygon section sized for hoop (bands carry
ALL hoop load) + sea-level ring buckling, "auto" = lightest passing (flat near throat, stiff at an
overexpanded exit); `design.py` adds their mass (replacing the tube_wall jacket extra over the
banded area) and a per-tube taper advisory (SP-8087 6:1 swage+expand limit); `gui/mesh_builder`
draws the sized sections, and `tube_bundle.py` draws tubes as CONTIGUOUS swaged ellipses that fill
the pitch (neighbours touch across a braze seam) [Huzel p.113-114; SP-8087 Sec.2.1.1.3];
`mass_model.py` also carries the throat
low-cycle thermal-fatigue estimate and the injector-plate mass; `staged_combustion.py` = FRSC/ORSC/FFSC preburner model: preburner Tin is a design input (`EngineDesign.preburner_tin_k`/`ox_preburner_tin_k`, 0 = pair default), the turbine PR is SOLVED (`solve_staged_power_balance`) and pump discharge is BUILT from the real pressure chain [SP-8107 3.1.1.1] - no PR closes = warn-only Pc ceiling; the expander fuel leg likewise carries its series turbine dP, GG flow is pumped too (`design.GG_MIXTURE_RATIO`), and dual-shaft turbine work splits by topology (`turbopump_sizing.split_turbine_work`),
`electric_pump.py` = battery+motor mass model, `expander.py` = regen-heat turbine,
`turbopump_efficiency.py` = DERIVED pump & turbine efficiency (Ns / staging / pitchline),
`turbopump_sizing.py` = 1-D Ns/tip-speed/stage/turbine-count sizing + envelope + mass,
`turbopump_materials.py` = rotor-material catalog), `catalog/` (`build_catalog.py` scrapes
`Engine_Configs/` into the "pick a host model" data; `build_roengines_models.py` scrapes
`KSP-RO/ROEngines` `PartConfigs/*.cfg` into `roengines_models.json` = native rendered
height per `#engineType`, the input to export model-scaling - committed snapshot; ROEngines
itself is vendored locally at `upstream/ROEngines` (auto-detected, see `UPSTREAM_REPOS.md`)
for convenience but never redistributed - only derived numbers ever leave it, per its
CC BY-NC-ND license), `gui/` (Tkinter shell + File menu w/ Ctrl+S/O/N/E + matplotlib 2D
schematic w/ cooling overlay + a side-view injector block on the chamber head, 3D view with
a domed injector cap, a face-on Injector Face tab, and a 2D turbopump systems diagram),
`export/` (`cfg_writer.render_cfg` renders to RF `.cfg` text; `output_mode` =
`additional_config` (default, append a CONFIG to the host part - unchanged),
`new_part_in_place` (+ a `@rescaleFactor` patch), or `new_part_standalone` (a `+PART` copy
that borrows the host model rescaled, own `#engineType`/gating, `origMass`-pinned mass -
generated `TR341_Config.cfg`); uniform model scale = design length / host native height).

## 3. `claude_lit/` — distilled literature reference for `engine_designer/`

`literature/` holds raw source PDFs (textbooks, NASA reports, AIAA papers); `claude_lit/`
is the distilled, cited reference actually consulted when trusting or adding physics in
`engine_designer/`. **Read `claude_lit/README.md` first** — it has the citation-key table
(one row per source, tagged `[Huzel]`/`[Sutton]`/`[Bazarov]`/etc.), the topic-file index
(16 files under `claude_lit/topics/`, one per physics domain — injectors, cooling, engine
cycles, turbopumps, materials, combustion stability, ...) and the lookup-budget rules
(section-targeted reads, 40 KB topic-file cap). `claude_lit/PROVENANCE.md` records when each
source was extracted and by what method (moved out of the README index 2026-09-22). `claude_lit/sources/*.md` has
one identity/character/key-results/caveats note per source PDF. `claude_lit/OPEN_QUESTIONS.md`
tracks live unfilled literature gaps and pending `ASSUMPTIONS.md` citation upgrades — check it
before starting new literature work.

**Before trusting or tweaking any `ASSUMPTIONS.md` constant, or adding new physics/a new
propellant pair/a new engine-physics feature**: check the relevant `claude_lit/topics/*.md`
file's `## Implications for engine_designer` section first — it already maps literature
findings onto specific files/constants, and flags what's real data vs. an engineering
estimate. This is the same spot-check discipline as convention #1 above, one layer earlier.

**If new PDFs appear in `literature/`** (the user adds papers, or asks for a review of
what's new): diff the new files against `claude_lit/sources/*.md`'s existing coverage first
— don't assume every PDF in `literature/` has been distilled. **Skip `literature/duplicates/`**
entirely: it holds md5-confirmed byte-identical copies of already-distilled PDFs, never to be
distilled or diffed. Numeric NTRS-accession filenames get renamed to
`<Report ID> - <Title>.pdf` (the NTRS number goes in the source note). This sandbox has no
`poppler-utils`/`pypdf`; build a throwaway reader with `python3 -m venv v && v/bin/pip
install pymupdf` (`import fitz; page.get_text()` / `page.get_pixmap()` for OCR-garbled
pages), matching the method `claude_lit/PROVENANCE.md` documents. For each
new source: write a `sources/<slug>.md` note in the exact format of an existing one (Identity
/ Character / a parameter or results table / Key results / Design method if applicable /
Section map / Caveats), pick a short bracket tag, then fold citable findings into the
relevant `topics/*.md` file(s) with `[Tag §x.y p.NN]`-style cites, and update `README.md`'s
citation-key table + topic-file index, and append a dated batch entry to `PROVENANCE.md`. Parallel forks/subagents (one
per paper) work well for the reading/note-drafting step since each source is independent;
do the `topics/*.md` + `README.md` integration pass yourself afterward since it needs all
the new tags in hand at once for cross-referencing.

**Numbers with no real citation** (e.g. a plausible-but-unverified engineering figure like a
bearing DN limit) still get added when useful, but must say so loudly in `ASSUMPTIONS.md` at
the appropriate tier, per the "never invent a number from nothing, and say which" rule above
— trust the *direction* of an under-cited estimate far more than its magnitude, and prefer
reverse-solving a new constant against a real engine in `Engine_Configs/` (convention #1)
over hand-picking it, even when a literature source suggests a seed value.

## Detailed history

`~/.claude/plans/i-m-wanting-to-mod-rippling-wadler.md` has the full round-by-round design
log (why each feature was built the way it was, bugs found and root-caused, real engines
researched) if a past decision's reasoning is ever needed in detail. The current *state* is
fully captured in the code plus this file plus `engine_designer/README.md`/`ASSUMPTIONS.md`
- that plan file should rarely need re-reading for routine continuation work.
