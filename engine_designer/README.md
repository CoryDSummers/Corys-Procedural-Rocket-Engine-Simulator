# RO Engine Designer (v1.7)

Interactive tool for designing custom RealismOverhaul/RealFuels rocket engines,
inspired by the *Children of a Dead Earth* engine designer: pick propellants,
chamber pressure, expansion ratio, nozzle shape, feed cycle, injector type,
ignition system, turbopump technology, engine controller/avionics tier, gimbal,
and a chamber/nozzle material, watch a live 2D schematic, 3D preview, and
checklist update, then export a RealFuels `.cfg` (with optional RP-1
tech-tree gating) bound onto an existing RealismOverhaul engine model.

See `ASSUMPTIONS.md` for an honest, itemized accounting of exactly which
numbers in this tool are validated vs. calibrated estimates vs. reasonable
defaults - "how much of this is magic numbers," worked file-by-constant.

See `COOLING_AUDIT.md` (2026-09-23) for the full cooling-physics audit. It covers:
- **The fix:** one unified per-station thermal solve replacing the old circular wall
  temperature, chemical-equilibrium gas properties, real coolant properties and
  corrected T_aw / Bartz sigma.
- **Before/after numbers:** for 12 real engines and the saved user designs.
- **Remaining gaps.** The biggest is coolant-side h_c, which runs about 2x low against
  the SSME's cited design wall.

Validate the physics against real engines with
`python3 -m engine_designer.validation_engines.run_corpus --report`.
Regenerate the property tables with `tools/property_tables/generate_property_tables.py`
(Cantera + CoolProp, runs locally or on Colab).

## Running it

```
cd /home/cory/ksp_config
pip install -r engine_designer/requirements.txt
python3 -m engine_designer.gui.app
```

**Needs a real display** (a desktop session, or `ssh -X`). This tool was built
in a sandbox with no `$DISPLAY`, so `app.py` could only be syntax-checked and
import-checked there, not actually clicked through — run it on your machine
and let me know if anything misbehaves.

`requirements.txt` includes `PyOpenGL`/`pyopengltk`, which power the 3D
Preview tab's GPU-rendered orbit-camera view (mouse-drag to orbit, scroll to
zoom) and its heat-flux colormap overlay checkbox. These additionally need a
working OpenGL context at runtime (a GPU + drivers + `$DISPLAY`, same
standing constraint as Tkinter itself) — on Linux this sometimes also needs
an OS-level package (`libgl1`/mesa) that `pip` can't install for you. If
`PyOpenGL`/`pyopengltk` aren't importable, or the GL widget fails to
initialize, the app **automatically falls back** to the older
matplotlib-rendered 3D preview (`gui/preview3d.py`, still shipped
unmodified) with a label explaining why — installing the GL packages is
optional, not required to keep using the tool. The GL rendering path itself
could not be exercised in this sandbox at all (no display, packages not
installed) — only its pure-math mesh/camera/colormap layer
(`gui/preview3d_gl_core.py`) was actually run and self-tested; the GL widget
layer (`gui/preview3d_gl.py`) was only syntax-checked. Please exercise the
orbit drag, scroll zoom, and heat-flux toggle yourself and report back.

The GL preview draws in layers (`gui/preview3d_gl_core/render_layers.py`):
an opaque pass, then a translucent pass. The **X-ray** checkbox above the 3D
view (and in the Shape Lab toolbar) moves the structural parts into the
translucent pass: they fade by viewing angle, so faces go clear while
silhouettes stay visible. The opacity slider sets how see-through the faces
are. Pieces are batched per layer and material, so a tube-wall bundle is one
draw call instead of hundreds. With X-ray and Flow off, the render is
pixel-identical to the old single-pass renderer (checked headlessly under
Xvfb + Mesa).

The **Flow** checkbox shows the propellant plumbing by temperature, with a
colorbar above the view. Ticking it also turns on X-ray, which can be unticked
again. A dropdown next to it picks the color scale:
- **Coolant (fit)** (default): the whole colormap spans this design's
  regen-jacket temperature range, so a jacket rise of a few tens of K shows as
  a full blue-to-red gradient.
- **All streams (fit)**: spans every drawn fuel/ox stream.
- **Absolute (log 20-4000 K)**: fixed, so a color means the same temperature
  on every design.

On a fit scale, streams outside the range are drawn in its end colors, and
the legend names them (e.g. "ox 90 K below scale"). Switching scales only
recolors from each vertex's stored temperature; no mesh is rebuilt.
- **Tinted hardware:** every drawn regen tube (or the milled-channel jacket),
  manifold ring and plumbing pipe is tinted by the temperature of the
  propellant inside it and turns semi-transparent.
- **One stream per tube:** a bright stream runs inside each drawn tube; on a
  milled-channel jacket, one per drawn channel. Two-pass (J-2) designs:
  - tube wall: the down tubes carry the down leg;
  - milled channels: every third channel carries it.
- **Gaps are filled:** a jacket stretch with no drawn tubes, such as the
  smooth chamber-jacket option, gets streams at the real channel count, so
  the flow stays continuous.
- **The hot gas is not drawn:** the chamber and nozzle stay plain X-ray walls.
- **Uncooled tubes:** tubes drawn on an uncooled nozzle extension carry no
  coolant, so they stay untinted and get no stream.

The colors come from `physics/flow_network.py`. In "channels" regen mode the
jacket temperatures are the coolant march's own values. In any other mode only
the total coolant temperature rise is known, so it is spread along the jacket
by absorbed heat, and the legend says "approx.". Feed lines appear only where a plumbing run or the default jacket-inlet duct
is drawn.

Before first use (or after `Engine_Configs/` changes), rebuild the host-model
catalog:

```
python3 -m engine_designer.catalog.build_catalog
```

The host-model *dimension* snapshot (`catalog/roengines_models.json`, used to
scale a borrowed model on export) is committed and rarely needs rebuilding; to
refresh it, clone `KSP-RO/ROEngines` and:

```
ROENGINES_DIR=/path/to/ROEngines python3 -m engine_designer.catalog.build_roengines_models
```

To re-run the physics self-checks and per-propellant spot-checks against real
RO engines:

```
python3 -m engine_designer.physics.isentropic
python3 -m engine_designer.physics.validate      # 5 propellant spot checks + GG-bleed,
                                                 # wall-heat-flux (Bartz h_g + computed
                                                 # wall temp), injector-geometry,
                                                 # combustion-stability, chamber-detail
                                                 # (C1-C6), turbopump-sizing,
                                                 # per-cycle-model and explicit-cooling
                                                 # spot checks (13 banners) - all must
                                                 # print "... OK" / "... WITHIN TOLERANCE"
```

To re-run the nozzle-contour, cooling, cycle and turbopump-sizing module self-checks:

```
python3 -m engine_designer.physics.nozzle_shapes
python3 -m engine_designer.physics.combustion
python3 -m engine_designer.physics.cooling
python3 -m engine_designer.physics.combustion_stability
python3 -m engine_designer.physics.injectors
python3 -m engine_designer.physics.staged_combustion
python3 -m engine_designer.physics.electric_pump
python3 -m engine_designer.physics.turbopump_materials
python3 -m engine_designer.physics.turbopump_efficiency
python3 -m engine_designer.physics.turbopump_sizing
python3 -m engine_designer.gui.schematic
python3 -m engine_designer.gui.preview3d          # matplotlib fallback preview
python3 -m engine_designer.gui.preview3d_gl_core  # OpenGL preview's pure-numpy math layer
python3 -m engine_designer.gui.injector_face
python3 -m engine_designer.gui.turbopump_diagram
```

`gui/preview3d_gl.py` (the OpenGL widget itself) can only be syntax-checked
here, never imported or run — it needs `PyOpenGL`/`pyopengltk` and a live
display:

```
python3 -c "import ast; ast.parse(open('engine_designer/gui/preview3d_gl.py').read())"
```

## What this tool covers

- **Propellant pairs**: LOX/RP-1, LOX/LH2, **LOX/CH4** (methalox), N2O4/MMH,
  Aerozine-50/NTO (storable hypergolics), and two monopropellants —
  **Hydrazine** and **H2O2** (high-test peroxide) — no mixture ratio, one
  `PROPELLANT` block, always pressure-fed, decomposed over a catalyst bed
  instead of combusted. Since the 2026-09-25 P1 re-anchor the five bipropellants
  run on Cantera shifting-equilibrium tables at the actual MR **and chamber
  pressure** (ideal c*, Isp and exit pressure at area ratios 2–250), times a cited
  combustion efficiency (0.975) and one reverse-solved nozzle efficiency per pair
  (`ETA_CF`). Each pair is anchored on a real RO engine (RD-111, RL10A-3-3,
  Raptor-2 + BE-4, Aestus, AJ10-137/Apollo SPS, MR-80B/Mars Landing Engine,
  Sprite/de Havilland HTP JATO respectively — see `physics/validate/`); the other
  corpus engines' residuals (RS-25 −1.8 %, RD-180 −3.7 %, Merlin −4.8 %, ...) are in
  `validation_engines/reports/2026-09-25_performance_reanchor_before_after.txt`.
  The two monopropellants reuse the entire bipropellant pipeline via a deliberate
  trick (a single-point combustion table that always returns the same
  decomposition state) rather than a parallel code path — see
  `physics/combustion.py`'s `is_monopropellant`/`MONOPROPELLANT_PAIRS`. The
  Sprite anchor is a rough one (its chamber pressure is a guess in the source
  config), so its spot check runs at a widened ±8% tolerance.
- **Isp-vs-mixture-ratio**: the Combustion Chamber tab shows the vacuum-Isp peak
  MR for the current design and an "Optimize MR" button that jumps the slider
  there (`physics/mixture_ratio.py` — a pure sweep over `compute()`, no physics
  constant, moves no spot check). With the equilibrium tables every pair has a
  real interior optimum (e.g. LOX/LH2 ~4.75, LOX/RP-1 ~2.8, LOX/CH4 ~3.4 at
  7 MPa / eps 40); real LOX/LH2 engines still run richer for tank-density
  reasons. (Before 2026-09-25 the old hand table put the LOX/LH2 "optimum" at
  its low edge - an artifact of its effective gamma/M.)
- **Cycles**: gas generator, pressure-fed, tap-off, fuel-rich staged combustion
  (FRSC), oxidizer-rich staged combustion (ORSC), full-flow staged combustion
  (FFSC), expander, and electric pump-fed. Each cycle now has its own physics,
  not a shared preset with tweaked constants:
  - **gas generator** - fuel-rich GG; its turbine exhaust leaves the engine
    through one of three real disposal modes (below).
  - **tap-off** - turbine driven by *main-chamber* combustion products tapped
    near the injector face, film-cooled to ~1150 K (`combustion.mixture_cp_j_kgk`
    gives the real chamber-products Cp); still an open cycle, same exhaust modes.
  - **Turbine-exhaust handling** (open cycles, `physics/turbine_exhaust.py`,
    Turbopump tab -> "Turbine Exhaust"):
    - The three modes:
      - **overboard duct**: RS-68 / H-1C sonic duct exit, or a shaped exhaust
        nozzle with an optional cant (LR-87 / LR-91 roll nozzle). Roll torque is
        reported but not exported, as in RO.
      - **aspirator**: the H-1D Hastelloy C shroud with a 0.440 in annular exit
        slot [H1-Man].
      - **nozzle injection**: F-1 at eps 10, J-2 cat-eyes at eps 10.9. The
        exhaust also lays a gas film on the nozzle wall downstream, applied by
        a second compute pass. The manifold is a **tangentially-fed scroll**
        like the real F-1 / J-2: one inlet sized on the full flow (the F-1's
        lands on its real 24 in), tapering one way round, sitting forward of
        the injection station on an outlet neck over a flame shield, with the
        F-1's 15 omega expansion joints drawn. The duct leaves it along the
        tangent (a pre-schema-15 baked run keeps its old radial T, with a
        warning; the Shape Lab's "Tangential inlet" box / Route to pump fix it).
    - The exhaust must leave **sonic** into its discharge (sea level, vacuum,
      or the local nozzle static pressure). That sets the turbine outlet
      pressure, so the turbine PR = min(22 cap, inlet / outlet); the H-1 lands
      on its real 33.8 psia / PR 17.7.
    - The exhaust's own Isp is an ideal expansion times a 0.96 efficiency
      pinned on the F-1's 16,000 lbf. It replaces the old flat 0.55 / 0.80
      dump fractions.
    - Optional exhaust heat exchanger with a LOX->GOX coil (H-1, F-1; LOX
      pairs only) and/or a helium coil (F-1; any pair): the duties add and
      lower the exhaust temperature. Outlet temperatures and the can's size
      are anchored on the real F-1 [F1-Man]; the can is drawn tapered.
    - Injection mode: back pressure anchored on the F-1's 58 psia turbine
      exit (interim lumped loss); the exhaust's gas film on the extension
      uses the TN D-3836 (modified Hatch-Papell) correlation.
    - Hardware (termination, the auto-routed duct to the new turbine exhaust
      port, the heat-exchanger can) is massed and drawn. The duct is a
      `turbine_exhaust` plumbing host, editable in the Shape Lab.
    - Open cycles **close on the target thrust**: chamber flow is rescaled so
      chamber + exhaust thrust = target.
  - **FRSC / ORSC / FFSC** (`physics/staged_combustion.py`) - *closed* cycles:
    the preburner exhaust rejoins the main chamber, so **no bleed Isp penalty**
    (engine Isp = chamber Isp). FRSC burns a fuel-rich preburner (~20 % of flow
    at MR 6) feeding the fuel pump's leg; ORSC an oxidiser-rich preburner (~75 %
    of flow at MR 2.7, cool ~628 K O2-rich gas) feeding the ox pump's leg; FFSC
    runs *both* (one turbopump each, two turbines, ~all of both propellants
    preburned). The **preburner temperature is a design input** (Turbopump tab;
    0 = the pair default - SSME's 1113 K and NK-33's 628 K are sourced) and the
    **turbine pressure ratio is solved** so the drive gas exactly powers the
    pumps; the pump discharge is built up from the real pressure chain (main
    injector -> turbine -> preburner injector -> jacket -> lines), so
    discharge/Pc emerges and rises with Pc. When no PR closes the balance the
    checklist warns - that's the staged-cycle Pc ceiling (e.g. an RD-180-class
    26.7 MPa ORSC needs a preburner hotter than 628 K).
  - **expander** (`physics/expander.py`) - turbine driven by regen-coolant heat
    pickup; **can make a design infeasible** (a real computed shortfall, not
    just a warning) exactly like real expander engines (RL10, Vinci) being
    limited to modest thrust/Pc. The turbine is in series on the fuel leg, so
    its pressure drop adds to the fuel-pump discharge (RL10 ~2.5 x Pc).
  - GG propellant is pumped too: the pumps carry chamber flow + the GG's own
    draw, split at the GG mixture ratio ([SP-8081]).
  - **electric pump-fed** (`physics/electric_pump.py`) - battery + brushless
    motors drive the pumps, no turbine, no bleed. The cost is carried as
    **mass**: a battery sized for the whole burn plus the motors, added to the
    dry mass. Only pays off at small scale / short burn (battery mass scales
    with burn *time*); the tool warns when the electric hardware dominates.
  ORSC and FFSC also carry a standing reliability caveat (oxidiser-rich
  turbomachinery is historically hard - late-Soviet/Russian ORSC, and only
  Raptor/BE-4-era FFSC). Per-cycle behaviour is spot-checked end-to-end against
  RD-180, SSME, RD-0124, J-2X, Rutherford and a Raptor-like design in
  `validate.py::run_cycle_model_check()`.
- **Nozzle shape**: Conical (adjustable half-angle) or **Bell** (Rao
  thrust-optimized-parabola contour, adjustable 60-100% length) — a bell is
  shorter than an equivalent-performance cone, with its own curved schematic
  and a divergence efficiency scored **relative to an 80%-bell reference**
  (not a flat fudge factor, and not double-counted against the propellant-pair
  calibration - see `physics/nozzle_shapes.py`'s `reference_lambda`). The
  `(theta_n, theta_e)` table is digitized from Sutton & Biblarz Fig. 3-14 and
  cross-checked against real F-1 / J-2 / RS-25 bells (`validate.py` C6); the
  contour includes the ~0.382*Rt throat arc the bare parabola skipped.
- **Injector type**: impinging, pintle, coaxial swirl, platelet, or (for
  Hydrazine) catalyst bed — the monopropellant decomposition analog, and the
  deepest-throttling option of any of them (8%, matching the real MR-80B) —
  each
  with its own combustion-efficiency multiplier, nominal injector dP/Pc, and
  minimum stable dP/Pc for deep throttle (pintle is deliberately the most
  throttle-forgiving). A pair/injector mismatch (e.g. coaxial swirl on a
  storable hypergolic) warns, doesn't block. See `physics/injectors.py`.
- **Injectors tab** (`gui/app.py` + `physics/injectors.py` +
  `physics/combustion_stability.py`): the injector-type dropdown (the film-
  cooling sliders now live on the Cooling tab), and a live detail panel with **derived element geometry**
  (injection velocities, orifice count/diameter from `mdot = Cd*A*sqrt(2*rho*dP)`
  at a target velocity, per-element momentum ratio `Rm`, satisfactory
  impingement-angle band), the **feed-pressure breakdown** (nominal vs
  velocity-derived injector dP -> the larger wins -> pump discharge -> fuel/ox
  shaft rpm), and the **chamber acoustic modes** (1L/1T/1R from the chamber-gas
  sound speed and chamber geometry, `[Huzel Fig 4-59]`; a warn-not-block flag
  when 1T is in the historically troublesome band and the injector is soft).
- **Combustion-stability aids** (Injectors tab): the acoustic-mode advisory is
  actionable now - toggle an **injector-face baffle** (odd compartment count,
  even warns per `[Sutton 9.3]`), **corner Helmholtz cavities** (count), or an
  **extra-stiff injector** (dP/Pc pushed to ~0.30 / ~0.42). Each resolves the
  advisory and carries its cost: baffles a small c\* hit + mass, cavities mass,
  a stiffer injector more pump discharge pressure (-> turbine work -> a touch of
  GG-bleed Isp). All default to off/nominal.
- **Injector views**: the 2D Schematic now draws a **side-profile injector
  block** (domed manifold on the chamber head, feed stubs, baffle blades
  reaching downstream into the chamber, cavity pockets), and the 3D Preview
  shows an **integrated domed injector cap** at the head. A dedicated **Injector
  Face** output tab still gives the face-on element pattern.
- **Element pattern + resultant beta angle**: the injector-type dropdown now
  includes the real element patterns (showerhead / unlike doublet-triplet-
  quintuplet / self-impinging / shear-coax post) each with its own mixing
  quality; the tool derives the **resultant beta angle** from the stream momenta
  (`[Huzel eq. 4-41]`) and warns if it's outside the band that propellant class
  wants (hypergolic slightly positive, cryo slightly negative). Symmetric
  patterns force beta ~ 0.
- **Split fuel/ox injector dP + orifice Cd**: separate feed-leg dP per stream
  (from the type's `dp_ox_over_fuel`, e.g. ~1.9 for a coax post) and a
  discharge-coefficient choice by orifice geometry (`[Sutton Table 8-2]`:
  sharp-edged 0.61-0.65, rounded short tube 0.88, ...) - both feed the derived
  injection velocities, orifice counts and pump head.
- **Injector-plate mass**: a real clamped-plate mass term (bore area x
  Pc-scaled thickness x density) now counts toward dry mass - previously zero.
  An element-crowding check warns when orifices per m^2 of face exceed a
  buildable ceiling.
- **Injector dP feeds the pump head both ways now**: the catalog's nominal
  dP/Pc fraction OR the dP it actually takes to inject at a sane velocity
  (`rho*V^2/(2*Cd^2)`, Pc-independent), whichever is larger - so a low-Pc engine
  is charged the real (higher) dP/Pc it needs, exactly like real small engines.
- **Throttle depth is checked two ways**: `min_stable_dp_ratio` (would this
  flow chug - hydraulic stability) and the new `practical_min_throttle` (has
  this injector TYPE actually been engineered/demonstrated to throttle this
  deep in a real engine - "ability," separate from "stability"). Pintle's
  practical minimum (10%) is far deeper than impinging's (60%).
- **Nozzle-extension material**: the bell past a "cooling transition"
  expansion ratio (adjustable, default eps 6) can use a different, typically
  cheaper/simpler material than the chamber, checked against the actual
  cooler LOCAL gas temperature at that point (isentropic T/Tc relation) -
  not the chamber's Tc, which would be needlessly pessimistic for a skirt.
  The same transition point also feeds the expander cycle's cooled-area
  cutoff, so "where does cooling change" is one concept, not two hidden
  constants.
- **3D preview tab**: a live-updating 3D surface-of-revolution of the same
  profile the 2D schematic draws (`physics/geometry3d.py` + `gui/preview3d.py`)
  - a basic shape (no wall thickness, no injector/flange detail), rotatable
  with the mouse.
- **Manifold rings** (`physics/manifold.py`): each header ring (fuel/ox
  injector feed, regen-jacket inlet) is sized on HALF its flow (fed at one
  inlet, split two ways) and tapers round each branch as flow drains out -
  between SP-8087's constant-area and constant-velocity extremes, per its own
  design criterion. Injector-feed ring velocity = the velocity whose head is a
  set fraction of that leg's injector dP; jacket-ring velocity = the local
  coolant-passage velocity (SP-8087 constant-velocity torus / Fagherazzi);
  both warn above SP-8087's 61 m/s liquid-coolant limit (not applied to LH2).
  Every ring has its OWN sizing knobs on the Plumbing tab (fuel/ox: velocity
  head % + taper; jacket inlet: velocity x the matched passage velocity +
  taper). A pipe leaves the ring at the ring's own inlet bore and cones out
  through a reducer to its own bore (per pipe, default = the full-flow feed
  bore `inner_diameter_m`); the ring's inlet/far-side bores are shown in the
  Injector readout.
- **Cooling-jacket flow topology**: single-pass countercurrent (inlet ring at
  the bell end), F-1 split reverse-flow (forward inlet + bypass + aft
  turnaround), or **J-2 mid-nozzle inlet** (`j2_mid_nozzle_inlet`, inlet ring at
  `jacket_inlet_eps`, down 1/2-count tubes to the cooled end, back up the full
  count to the injector - the real J-2's 180/360). The J-2 layout runs its own
  two-pass coolant march (`cooling.march_coolant_two_pass`) in the "channels"
  regen model; the 3D view starts its down tubes at the inlet ring (the tube
  split - `tube_split_eps` is ignored there) and draws the aft turnaround as
  the same end band as the F-1 layout. The 3D tube-drawing style (single pass /
  F-1 double pass / J-2 two pass) follows this topology automatically.
- **Procedural plumbing / Shape Lab** (`physics/plumbing.py`, `gui/shape_lab.py`,
  `gui/shape_lab_geometry.py`, `gui/mesh_builder.build_plumbing_pieces`): the
  **Plumbing** tab holds the per-ring manifold sizing sliders (one group each
  for the fuel ring, ox ring and jacket inlet ring - see "Manifold rings"
  above) and one row per
  manifold ring the tool sizes (`plumbing.HOSTS`: jacket inlet, jacket return,
  fuel injector-feed, ox injector-feed - colour swatch matching the ring's tint
  in the 3D view, a status line "no ring: <why>" / "no run" / "run: N pipes,
  N flanges, length, mass", an "Edit in Shape Lab..." button and "Clear run").
  Edit swaps the whole window for an editor rooted on that REAL ring of the
  loaded design, at real scale. A run = the manifold root (position around
  the engine axis + poloidal position around the ring's tube; the first pipe
  leaves along the torus surface normal) + a chain of pipe segments (length in
  its own pipe diameters, yaw/pitch ±90° relative to the previous pipe, per-joint
  elbow radius, flange-at-end, and its own bore x the feed bore with a live
  bore/velocity readout) + one shared flange style (lip/width in pipe diameters,
  bolt count or auto), with flanges allowed at the manifold joint, every pipe
  joint and the open end. Pipe 1 starts at the ring's inlet bore and cones
  (reducer) to its own bore; flanges are sized at their local bore. Add pipe /
  Remove last / a "Pipe k" selector (selected pipe tinted), toggleable pale
  ghosts of the chamber wall and of the turbopump assembly (placed exactly where
  the main preview draws it, now with inlet/discharge nozzle stubs at its pump
  ports) with a thin straight "ray" from an unconnected run's free end to the
  pump it will feed (fuel pump for the jacket/fuel rings, ox pump for the ox
  ring). **Connect to pump** closes the run onto that pump's discharge port:
  two AUTO legs (drawn lighter) go from the last pipe to a straight standoff
  in front of the port and into it, re-solved on every redraw so the line
  always lands on the port; **Route to pump** seeds an editable orthogonal
  route (radial out, axial to the pump, auto legs finish it). A connected
  run's computed pressure loss (Darcy friction + elbow/reducer K + a ring-entry
  dump, plus a valve allowance in `design.py`) REPLACES the flat 0.5 MPa line
  loss for that pump leg (two-pass `compute()`); the summary line shows it.
  And a live advisory line
  (pipe too short for its elbow, pointing into the chamber, ...). **Bake** stores the run
  on `EngineDesign.plumbing_runs` (saved with the project), recomputes, and the
  main 3D preview then draws it in place of the old fixed auto duct; pipes +
  flanges count in the dry-mass rollup and the checklist. Every node carries
  `kind`/`role` tags (`manifold[coolant_supply_manifold]` → `pipe[coolant_supply]`)
  so later features (ox/fuel injector-feed lines, J-2-style gimballing feed
  ducts, GG exhaust) reuse the same model with a different `host`. Lengths
  are stored per pipe diameter so a run survives the ring being resized by a
  physics change. A row whose ring doesn't exist for the current design (no
  regen jacket; jacket return only under the F-1 split / J-2 topologies) is disabled
  with the reason; a future host (turbopump ports, GG exhaust manifold) is one
  more `HOSTS`/`HOST_LABELS` entry and gets its row for free.
- **Cooling method per section** (`physics/cooling.resolve_cooling_method_checked`):
  `chamber_cooling_method` and `nozzle_cooling_method` are independent
  `EngineDesign` choices - `auto` (infer from the section's material, the
  historical behaviour) or an explicit `regenerative` / `dump` /
  `radiative` / `ablative` / `uncooled`. The resolved method - not the material -
  now drives the jacket-dP fraction, the char-consumption-vs-margin
  `ratedBurnTime`, the regen Isp credit and the throat-fatigue check.
- **Material/cooling compatibility is HARD-BLOCKED** (the one deliberate
  exception to "warn, don't block"): each material lists the methods it can
  physically be built for (`materials.Material.allowed_cooling_methods` - no
  regen on an ablative or C-C wall, no ablative on a metal, no radiative copper).
  An explicit impossible choice runs the material's own method instead, with a
  failing "cooling method compatible with material" checklist row; the GUI
  dropdown only lists allowed methods. Merely *risky* combos stay allowed and
  the thermal margin warns. `film` is no longer a method - see film overlay below.
- **Regenerative nozzle continuation** (`EngineDesign.regen_nozzle_end_eps`):
  a regeneratively-cooled nozzle can keep active cooling running past the
  `cooling_transition_eps` bell-MATERIAL split, out to this expansion ratio -
  a full-length regen nozzle (SSME, RL10) rather than a jacket that stops where
  the material changes. Feeds the real coolant march (wall temp, coolant dT)
  and, for the expander cycle, the real turbine heat pickup / feasibility
  margin. 0.0 (default) = stop at the material transition, unchanged.
- **Dump cooling** (`nozzle_cooling_method="dump"`, nozzle-extension only): a
  coolant bleed absorbs the extension's wall heat and is ejected overboard at
  the lip instead of returning to the injector - Vulcain HM-60 / J-2 style.
  `dump_coolant_fraction` (0 = auto-size to the pair's coking/boiling limit)
  sets the bled fraction of fuel; the net Isp cost accounts for the dumped
  stream still contributing some thrust, not the full loss of that flow. Needs
  `regen_nozzle_end_eps` set past the material transition for there to be a
  cooled slice at all - a full-length dump-cooled Vulcain/J-2-class nozzle
  costs ~1% Isp vs the same design radiatively cooled.
- **Cooled-wall construction** (`EngineDesign.wall_construction`): `milled_channel`
  (SSME/RS-25 MCC, the reference the channel model is calibrated to), `tube_wall`
  (F-1/J-2/RL10 brazed formed-tube bundle - hotter coolant-side wall, higher
  jacket dP, extra braze/jacket mass) or `coax_shell` (V-2/early Atlas double
  shell - gentle on dP, worst heat transfer, heaviest). Factors are Tier 3;
  `milled_channel` is bit-identical to before the field existed.
- **Tube-wall construction detail** (2026-09-23, `physics/hatbands.py` +
  `gui/preview3d_gl_core/tube_bundle.py`): tubes are drawn as a CONTIGUOUS
  brazed bundle - swaged/"spanked" ellipses that fill the local pitch, round
  where the pitch binds and flattened ovals downstream [Huzel p.113-114;
  SP-8087 Sec.2.1.1.3]; a per-tube taper advisory warns past SP-8087's 6:1
  swage+expand limit (fix: a tube split). **Structural hatbands** (SP-8120
  retaining bands) carry all hoop load aft of the throat: a continuous shell
  where the allowable tube span is short, then bands marched at that span,
  each sized (hoop + sea-level ring buckling) as flat / tee / hat / channel /
  box - or "auto", the lightest passing section (flat near the throat, stiffer
  toward an overexpanded exit) - with real dry mass, in a chosen material.
  Magnitudes Tier 3 (see ASSUMPTIONS.md); `validate.py`'s hatband check is a
  plausibility check, not a spot check.
- **2D schematic cooling overlay** (`physics/cooling.py` + `gui/schematic.py`):
  the engine contour is tinted by a **wall heat-flux distribution** (real
  per-station Bartz h_g x (T_aw-T_wg), peak at the throat), coloured bands
  above it mark which **cooling regime** applies where (the resolved chamber /
  nozzle method), and the outline carries the wall-temp margin. The flux
  magnitude is the same computed-absolute profile the expander cycle's heat
  pickup integrates, so the two never contradict.
- **Real Bartz gas-side coefficient + computed wall temperature**
  (`physics/cooling.py` + `physics/combustion.py`): a real `h_g` from the Bartz
  correlation `[Huzel eq. 4-13]`, fed by combustion-gas transport properties
  (viscosity from the Bartz M/T estimate, Prandtl from the Eucken relation - both
  DERIVED, not tabulated). It gives the throat flux, a recovery temperature
  `T_aw = 0.90*Tc`, and a **computed hot-gas-wall temperature** from
  `q = h_g*(T_aw - T_wg)`. For a **radiatively** cooled surface the wall temp is
  the radiation-equilibrium solve `h_gc*(T_aw - T_wg) = eps*sigma*T_wg^4`
  `[Huzel eq. 4-38]`; for a regen/dump wall the coolant pins it near the
  `cooling_effectiveness` proxy but never above the gas-side-only value. This
  is what the chamber/nozzle-extension material thermal-margin checks now use.
  Spot-checked (throat `h_g`, flux and `T_wg`) against F-1 / SSME / RL10 in
  `validate.py::run_cooling_heat_flux_check()`.
- **Regenerative Isp credit** (`[Sutton 8.2]`, 0.1-1.5%): the coolant carries
  wall heat back into the propellant enthalpy - applied only to pump-fed regen
  chambers, and scaled within the band by how hard the coolant is working.
- **Throat low-cycle thermal-fatigue estimate** (`physics/mass_model.py`): the
  through-wall gradient (`q * t / k`, the first real use of a material's thermal
  conductivity) drives a thermal stress `E*alpha*dT/(2(1-nu))` and a
  Coffin-Manson/Basquin cycle count - the SSME-throat-cracking regime. Warns
  (never blocks) when the estimated life is thin next to the planned ignition
  count. Trust the direction (higher Pc / lower-k liner = far shorter life),
  not the absolute number.
- **Film cooling is an OVERLAY** on whatever each section's method is (Cooling
  tab, "Fuel Diversion for Cooling") - regen + film, ablative + film, an uncooled
  or radiative extension + a slot film all combine in the same flux / wall-
  temperature math - at **two independent sites**, both fed with post-jacket
  fuel (the F-1 curtain; the jacket's coolant flow isn't reduced):
  - the **chamber curtain** (`film_cooling_fraction`), at the injector face or,
    with `chamber_film_inject_area_ratio` > 1, a convergent film ring - a
    **length-decaying curtain** (`physics/cooling.film_effectiveness_profile`),
    strongest at injection, recovering toward 1x downstream; costs c*.
  - a **nozzle-extension slot** (`nozzle_film_fraction` at
    `nozzle_film_inject_eps`, default 10 = the F-1) - `nozzle_film_effectiveness_profile`;
    it never burns in the chamber, so it's costed like dump flow.
  The film lowers both the local flux and the local driving temperature
  (`T_aw,film`, at the jacket-exit film temperature), feeding the throat check,
  the extension check (worst filmed station) and - "channels" regen model - a
  **full-length coupled wall balance** that reports the hottest cooled station
  and its zone (barrel / convergent / throat / nozzle). Ablative + film extends
  the char-limited burn time. Off by default; zero film is bit-identical. Tier 3 -
  no film-effectiveness correlation is in hand (NASA SP-8124 is the missing
  source); `validate.py::run_film_overlay_check()` pins direction/plausibility.
- A **regen-jacket coolant-capacity** check warns (never blocks) when a
  regen-cooled chamber's coolant temperature rise exceeds the pair's
  coking/boiling limit.
- **Ignition system**: TEA-TEB slug, spark torch, hypergolic self-ignition,
  a single-shot pyrotechnic squib, or catalytic (no separate igniter -
  Hydrazine) — picking a propellant pair suggests a sensible default; an
  implausible pairing warns. See `physics/ignition.py`.
- **Chamber contraction ratio, L\* and convergent half-angle** are adjustable
  sliders. L* now goes down to 0.02 m (was 0.5 m) - small thrusters genuinely
  need L* around 0.02-0.2 m for a sane chamber shape, since L* is a fixed
  length, not a scale-relative quantity (see `physics/geometry.py`'s docstring
  for the small-engine chamber-geometry bug this fixes). Picking a propellant
  seeds a sensible per-pair L* (`[Huzel Table 4-1]`).
- **Chamber sizing method**: `lstar` (Vc = L\**At, the historical path) or
  `residence_time` (size Vc from a target combustion stay time in ms; 0 = the
  stay time implied by the pair's L* default, which reproduces the L* sizing
  exactly - `combustion.residence_time_from_lstar_s`, pinned by `validate.py` C4).
- **Chamber contour fillets**: a **throat-radius fillet** instead of a sharp
  corner, plus an optional **cylinder->convergent-cone wall fillet**
  (`chamber_wall_fillet_r_over_rt`, 0 = sharp) whose removed gas volume is
  subtracted from the convergent volume so `L**At = Vc_total` stays exact.
- **Finite contraction ratio costs performance too, not just wall heat**: the
  tool computes the chamber-end Mach and the injector-end stagnation-pressure
  rise (`[Sutton Table 5-4]`: ~8% at CR 1.6, ~16% at a very tight chamber) and
  warns when CR < ~2.5. A checkbox routes that higher pressure into the required
  pump/tank discharge.
- **Stay-time and chamber L/D checks** (`[Sutton eq. 8-10]` 1-40 ms; long/narrow
  vs short/wide) - warn-not-block.
- **Materials**: 10 chamber/nozzle materials (NARloy-Z, Inconel 718, stainless
  steel, Niobium C-103, ablative phenolic, GRCop-84, Rhenium-Iridium, Haynes
  230, Carbon-Carbon composite, Molybdenum TZM) with a thermal-margin check
  that **warns but never blocks** a thermally marginal choice. Contraction
  ratio now has a real effect here: chamber-wall heat flux scales with a
  damped Bartz area-ratio term `(1.6/CR)^0.9`, referenced/neutral at CR=1.6,
  so a tighter chamber genuinely runs a hotter wall (see
  `physics/materials.py::contraction_ratio_heat_flux_factor`). Each material
  shows a live details box (density, cost, cooling method/effectiveness,
  thermal conductivity, tech-era hint), and the 3D preview colors the
  chamber and nozzle-extension surfaces by their actual chosen material
  (real-world-plausible metal/composite tones), fully opaque.
- **Left-side input tabs**: the control panel is grouped into 5 tabs by design
  concern - Combustion Chamber, Engine Bell, Turbopump, Gimbal, Model (host
  part/thrust target/controller) - rather than one long scrolling list.
  Readout/Warnings/Export stay below the tabs, visible regardless of which
  tab is active. Adding a future tab is a self-contained block in the same
  shape as the existing ones.
- **Turbopump efficiency is DERIVED, not picked** (`physics/turbopump_efficiency.py`):
  pump efficiency comes from the whole-pump specific speed `Ns` (a bell peaking
  at Ns ~2200, so a multistage LH2 pump lands well below peak) and pump size;
  turbine efficiency from the staging type's efficiency ceiling (2-row
  velocity-compounded / 2-stage pressure-compounded / reaction), pitchline
  speed, whether it runs partial admission, and pressure ratio. The curve
  SHAPES are calibrated to `[SP-8107 Table II / III]` real efficiencies (F-1
  pump 72.6/74.6 %, turbine 60.5 %; J-2 73/80 %, 60 %; H-1 turbine 70 %; RL10
  74 %; SSME 74-79 %) and pinned by `validate.py::run_turbopump_efficiency_check()`.
  The early/mature/advanced tier is now just a **build-quality multiplier**
  (x0.93 / x1.00 / x1.04) on the derived value; `mature` = x1.00 so an F-1
  recovers its real ~0.73 with no boost. The fuel/ox η sliders are an optional
  manual override (0 = use derived). **Turbopump mass** follows the
  `[SP-8107 Table I]` mass-vs-power trend (~12 kW/kg small, ~27 kW/kg large),
  spot-checked against F-1 1429 kg / J-2 ~305 kg / RD-0110 ~90 kg.
  Two plausibility checks (warn, never block) round this out: a
  **GG flow-fraction** check (only for the open GAS_GENERATOR/TAP_OFF
  cycles, where a high bleed fraction is a real Isp-wasting red flag - FRSC/
  ORSC are closed cycles that recover all preburner flow, so they're
  excluded), and a **pressure-fed chamber-pressure** check (real classic
  pressure-fed engines - Apollo SPS, LM descent/ascent engine, R-4D - all
  cluster at 0.7-0.8 MPa; modern composite-overwrapped tanks like SpaceX
  SuperDraco can reach ~6.9 MPa, noted in the warning rather than modeled).
  The **3D preview draws the turbopump at its real computed size** - a blocky
  assembly (pump volute(s) + turbine disk + shaft) sized from the 1-D machinery
  dimensions and scaled so its volume matches the estimated mass, coloured by
  the chosen turbopump material, mounted beside the injector end. Dual-shaft
  designs show two separate units.
- **Turbopump preliminary sizing** (`physics/turbopump_sizing.py`): on top of
  the mass estimate, a 1-D `Ns` / head-coefficient / tip-speed sizing pass
  ([SP-8107 2.1.1] / [Huzel Ch. VI]) derives, per pump, a **rotor speed**,
  **impeller tip speed** (as a % of the chosen turbopump material's
  capability), and a **stage count** (anchored so the J-2 LH2 pump comes out
  ~7 stages); per turbine, a **pitchline speed / U-C0** from the staging type;
  and the **shaft arrangement** (single-shaft / dual-shaft / geared) + **turbine
  count** from propellant pair + cycle + thrust ([SP-8107 2.1.2]). "auto"
  derives all of it; overriding any of it is the ONLY thing that moves computed
  dry mass (a documented gearbox / extra-stage modifier; the auto architecture
  is exactly 1.0). Optional per-pump **inlet NPSH available** inputs (0 = not
  limiting, the default) cap a pump's rpm at its suction-specific-speed limit
  (bigger impeller, lower efficiency) - the NPSH comes from the user, the tool
  still has no tank model. Otherwise rotor speed is a preliminary estimate - `validate.py`'s
  `run_turbopump_sizing_check()` spot-checks it against real J-2 / F-1 /
  RD-0110 numbers with wide bands. Warns (never blocks) on tip-speed over the
  material limit, turbine gas too hot for the material, titanium wetted by an
  oxidiser, and staged-combustion / ORSC material demands.
- **Turbopump materials** (`physics/turbopump_materials.py`): a 6-entry catalog
  (aluminium, 17-4PH stainless, Inconel 718, forged titanium, powder-met
  superalloy, Monel K-500) with density, service temp, tip-speed capability
  (forged Ti = the [SP-8107 3.2.1.3] 853 m/s anchor), strength class and
  oxygen compatibility - drives the sizing warnings above.
- **Turbopump tab** (right-side output notebook): a 2-D systems/flow diagram,
  rendered per cycle - GG/tap-off show the overboard dump; FRSC a fuel-rich
  preburner + boosted fuel pump; ORSC an oxidiser-rich preburner (distinct
  colour) + boosted ox pump; FFSC two preburners feeding two turbines; electric
  pump-fed a battery+motor box in place of the turbine. Each box is annotated
  with the sizing numbers and tinted by feasibility. `gui/turbopump_diagram.py`
  (Agg-testable, headless smoke test covers all cycles).
- **Engine controller/avionics**: a tier catalog (electromechanical, baseline,
  digital FADEC, dual-redundant fail-operational) driving `throttleResponseRate`,
  `varyIsp`/`varyMixture`, `residualsThresholdBase` on export - purely
  export-time, never affects computed Isp/thrust. See
  `physics/controller_tech.py`.
- **Design-derived TestFlight reliability** (`physics/reliability.py`,
  export-time only): the exported `ignitionReliability*` / `cycleReliability*`
  are DERIVED from the design - the controller tier is the anchor, then the
  failure gap `1 - value` is scaled by the cycle's inherent difficulty
  (pressure-fed easy -> FFSC/ORSC hard) and inflated for high chamber pressure,
  oxidiser-rich turbomachinery, deep throttling, many restarts, a
  tip-speed-marginal or fatigue-marginal design, and multi-chamber layouts.
  Clamped into the real RO-corpus band (cycleReliabilityStart runs 0.63 min /
  0.97 median / 0.9997 max across ~300 configs). A low-complexity GG/pressure-fed
  design at the `baseline` tier still exports ~0.970, matching every `.cfg`
  written before; a fresh FFSC exports ~0.84. `testedBurnTime` is
  `rated x` a controller-tier multiplier nudged by a reusability signal.
- **Cost model** (`physics/cost_model.py`, export-time only): a CER-style
  `cost` / `entryCost` estimate from the computed dry mass (`mass^0.55`),
  chamber pressure, cycle complexity, chamber count, and the blended
  `relative_cost_factor`s of the chosen material / injector / turbopump tier /
  controller tier (previously tracked but never combined). Calibrated so a
  ~1.4 MN kerolox GG lands near this project's own `H3-250K` gating values
  (`cost` 20 / `entryCost` 15000). The GUI shows the estimate and auto-fills the
  export fields; typing a value overrides it (a "Reset cost to estimate" button
  hands it back). `cost` is written on the CONFIG block; `entryCost` only in the
  RP-1 gating patch.
- **Gimbal**: inherit the host part's existing gimbal untouched (default,
  matches `H3-250K`/`H4-250K`), set a custom `gimbalRange`/response speed
  (matches `H3-250K-V`/`TR341_Config.cfg`), or go explicitly ungimballed
  (matches real small RCS/vernier-class engines and boosters that use
  separate vernier chambers for TVC). A soft plausibility check warns if a
  custom range falls outside the ~2-11.5 deg band real engines cluster in -
  note real gimbal range does NOT scale with thrust. See `physics/gimbal.py`.
- **RP-1 tech-tree gating**: an editable combobox (type any node, or pick
  from real RP-1 engine-tech-node suggestions fetched from RP-1's own
  `TREE-Engines.cfg`, contextually ordered by propellant/cycle) plus entry
  cost/cost fields, wired into the export's existing `%techRequired`/
  `%entryCost`/`%cost` patch. See `physics/tech_tree.py`.
- **Checklist tab**: every design check's pass/warn status (not just
  currently-failing ones), grouped by category in a `ttk.Treeview`, with
  plain PASS/WARN text (not color alone) for accessibility.
- **Throttle**: a floor down to 10% of max, with a sea-level flow-separation
  sweep and an injector-type-specific stiffness check.
- **Every slider has a paired typable entry box** sharing the same underlying
  variable — type an exact value or drag, both stay in sync.
- **The control panel scrolls** (Canvas+Scrollbar, mouse-wheel bound) now that
  there are enough controls to overflow a window.
- **Project New / Save / Load** — a **File menu** (New `Ctrl+N`, Open `Ctrl+O`,
  Save `Ctrl+S`, Save As `Ctrl+Shift+S`, Export .cfg `Ctrl+E`, Quit `Ctrl+Q`)
  plus the same three buttons beneath the tabs. Save writes the whole design as
  a JSON project file (including the export settings: output mode, CONFIG name,
  host-model reference height, new-part name/title/manufacturer) and reload
  brings every dropdown, slider, checkbox and entry back exactly
  (`gui/project_io.py` + `EngineDesign.to_dict`/`from_dict`, `schema_version` 2,
  so a file from an older or newer tool version still loads: unknown keys
  dropped, missing keys default). `Ctrl+S` re-saves the loaded file in place;
  the title bar shows its name. Load suppresses the per-widget recompute storm
  (`self._loading` guard) and does one recompute at the end.
- **Export** — three output modes (Model tab → "Output mode"):
  - *Additional CONFIG on host part* (default): the historical shape — an
    `@PART[*]:HAS[#engineType[<host>]]` patch appending a `CONFIG` to the host
    part, same two-patch style as `H3-250K_Config.cfg` / `H4-250K_Config.cfg`,
    plus the optional RP-1 gating patch. Host model at native size.
  - *New engine — rescale host part in place*: the above **plus** a
    `@rescaleFactor *= k` patch sizing the host model to the designed engine's
    computed length.
  - *New standalone part (borrow host model)*: a generated equivalent of
    `TR341_Config.cfg` — `+PART[*]:HAS[#engineType[<host>]]` copies the host
    part, renames it, re-tags `%engineType`, rescales the model, strips the old
    configs, and a second patch adds a fresh `MODULE { ModuleEngineConfigs }`
    with the CONFIG and `origMass` (part mass pinned in tonnes, TR341
    convention, so `rescaleFactor` is visual-only). Its own gimbal / RP-1
    gating patches target the new part.
  The rescale factor is **uniform** = designed length ÷ host model native
  height. Native height comes from `catalog/roengines_models.json` (scraped
  `node_stack_top/bottom` span × `rescaleFactor` from `KSP-RO/ROEngines`
  `PartConfigs/*.cfg` — ~150 engines), overridable per-export via the
  "Host model reference height [m]" field (0 = auto). No known height and no
  override → export emits no rescale patch.
- **Dry-mass estimate**: chamber and nozzle-extension wall mass now comes from
  a real thin-wall pressure-vessel hoop-stress formula (`t = safety_factor *
  Pc * r / allowable_stress`, locally varying along the profile), plus the
  already-computed turbopump mass - the same "derive a real physical
  consequence from chamber pressure" pattern used for turbopump mass. Every
  material now has a cited (or honestly flagged as extrapolated/estimated)
  high-temperature allowable stress. `massMult` in the exported `.cfg` is
  this computed mass divided by the chosen host part's own real stock dry
  mass (from `catalog.json`) when available, falling back to 1.0. **An
  explicit LOWER BOUND**, not a complete mass model - see
  `physics/mass_model.py`.
- **Cooling fix + rated burn time**: the regen-jacket pressure drop
  (`JACKET_DP_PA`) used to apply unconditionally to every pump-fed cycle
  regardless of the chosen material's actual cooling method - a real,
  previously undocumented inconsistency (an ablative or radiative chamber has
  no active coolant loop at all). It's now scaled by cooling method
  (full for regenerative, a small fraction for film, zero for
  ablative/radiative). Rated burn time is no longer a flat 200s: ablative
  chambers derive it from the SAME hoop-stress wall thickness divided by a
  real, cited char-consumption rate (matching the "ablative, no extra time"
  pattern found in real RealismOverhaul configs, where tested burn time is
  essentially equal to rated for ablative engines); every other material
  scales a baseline by chamber thermal margin. Tested burn time uses a new
  per-controller-tier `tested_to_rated_multiplier` (6-17x, spanning 4 real
  cited engines: Saturn V F-1, RD-180, Merlin 1D, Vulcain 2) instead of a
  flat rated x20.
- **Number of ignitions**: exposed as a real design choice (Model tab),
  forced to 1 for single-shot igniters (matching `ignition.py`'s
  `forces_single_ignition`) - real RO configs show this varies enormously by
  engine role, from 1 (expendable boosters) to hundreds (long-life
  restartable upper-stage/RCS engines).

## What this tool does NOT cover (phase 2)

- Propellant pairs beyond the current seven (e.g. HAN- or ADN-based "green"
  monopropellants, subcooled/densified variants as distinct resources, 98% HTP
  as its own hotter pair). LOX/CH4 and H2O2 are now real (calibrated against
  Raptor-2/BE-4 and Sprite); the methalox cycles no longer use a LOX/LH2
  stand-in.
- A dual-nozzle SUBCONFIG export workflow (only one CONFIG per export).
- CUDA/GPU acceleration (not needed — this workload is closed-form algebra
  and root-finding, effectively instant on CPU).
- A procedurally generated 3D model (stated as future work) — for now, the
  exported engine visually renders as whatever real RO part you pick as the
  "host model", optionally uniformly rescaled to the designed engine's computed
  length (see Export, above).
- Propellant **tank** mass/pressure-rating modeling — that's RealismOverhaul/
  RealFuels' job via its own procedural tank parts; this tool only models the
  engine itself, though a pressure-fed design does report the tank pressure
  your tanks will need to supply.
- Hard material/injector/ignition gating (everything only warns here, matching
  the decision made for this tool — unlike Children of a Dead Earth's
  confirmed hard material gate).
- Engine dry mass IS now estimated (see the Dry-mass bullet above), but as an
  explicit LOWER BOUND: no injector/valves/actuators/mounting structure/
  flanges, no manufacturing margin beyond one flat safety factor, and no
  wall-thickness tapering along the nozzle (a single locally-varying
  thickness driven by chamber pressure only, not the lower local nozzle
  pressure). Cost IS now estimated (see the Cost-model bullet above) - a
  CER-style `mass^0.55 x cycle x Pc x material/injector/turbopump/controller`
  formula calibrated to this project's own gating values, not a full
  bottom-up cost breakdown.
- Turbopump rotor speed / tip speed / stage & turbine count / shaft arrangement
  / efficiency / mass / physical size ARE now derived (1-D `Ns` sizing +
  `physics/turbopump_efficiency.py` + the SP-8107 mass-vs-power trend), but
  NPSH available is a user input (no tank / vapor-pressure model), and an
  axial-pump Ns target for LH2 isn't modelled, so rotor speed is a
  preliminary estimate (validated against real engines with wide
  bands) and the volumetric envelope is scaled to the mass rather than trusted
  as an absolute dimension. There is still no real coolant-channel /
  bearing / lubrication / start-transient model.
- Wall heat transfer IS now estimated (`physics/cooling.py`): a real Bartz
  gas-side `h_g` from derived transport properties, a computed hot-gas-wall
  temperature, a radiation-equilibrium solve for uncooled surfaces, and a
  through-wall-gradient fatigue estimate. The **coolant SIDE** now has an
  optional 1-D counterflow channel march (`regen_channel_model = "channels"` on
  the Combustion Chamber tab; default `"flat"` keeps the legacy flat 1.6 MPa
  jacket dP so nothing already validated moves): channel geometry (count sized
  by a throat-scaled pitch; height sized to a target coolant velocity; aspect /
  land-fraction knobs), a Dittus-Boelter coolant-side `h_c`, a coupled
  series-resistance wall solve (coolant-side wall temp = coolant bulk +
  `q/h_c` + through-wall conduction), and a **real Darcy-Weisbach jacket
  pressure drop** that replaces the flat constant and feeds pump discharge ->
  turbine work -> open-cycle Isp. One calibration scalar (`CHANNEL_DP_CALIBRATION`)
  pins the reference regen design to ~1.6 MPa; `validate.py` gates the
  channels-mode jacket dP for F-1/SSME/RL10 (wide bands) and asserts the
  neutral-default contract. Film cooling is now a length-decaying curtain
  (flux multiplier + a throat driving-temperature reduction) rather than a flat
  knockdown, but transpiration cooling, multi-pass jackets, coolant-property
  variation along the march and two-phase / supercritical-pseudo-critical
  effects are still not modelled. **The gas-side flux-profile magnitude is now
  computed-absolute** (`cooling.absolute_heat_flux_profile`: real Bartz h_g x
  (T_aw-T_wg), station by station - not shape-normalised to a flat anchor),
  calibrated PER PROPELLANT CLASS against real engines
  (`cooling.BARTZ_ABS_FLUX_CALIBRATION`: LOX/RP-1 and LOX/LH2 independently
  anchored against F-1 and SSME/RL10 respectively; a flat single-constant
  calibration was tried first and rejected - it could not bring both
  propellant classes within band at once, since real Bartz h_g depends on
  Pc/c* and hydrogen's much higher gas cp, not Pc alone). This also means the
  tool now captures a real Bartz effect it never modelled before: `h_g ~
  1/Dt^0.2`, so smaller/lower-Pc chambers of the SAME pair genuinely run
  hotter walls per unit Pc than larger ones - expect NARloy-Z thermal-margin
  warnings on small/medium regen designs that a flat anchor previously hid,
  and higher (more realistic) expander-cycle feasibility margins for small
  LH2 designs. `expander.py`'s turbine heat pickup integrates the identical
  profile (asserted exactly in `validate.py`). See ASSUMPTIONS.md for the
  full derivation and the rejected flat-constant approach.
- Multi-chamber/clustered engines (e.g. RD-170's 4 chambers on 1 turbopump,
  or RD-107/108's vernier-chamber TVC arrangement) - one engine, one chamber,
  one nozzle per design.

## Layout

```
physics/     pure computation: isentropic gas dynamics (+ conical AND bell
             nozzle contours), combustion tables (7 pairs incl. LOX/CH4 +
             H2O2), mixture_ratio (Isp-vs-MR sweep), cooling (Bartz h_g +
             optional coolant-channel march), materials, injectors, ignition
             systems, turbopump/GG + turbopump_tech (tech tiers),
             controller_tech (avionics tiers), reliability (design-derived
             TestFlight numbers, export-time), cost_model (CER-style cost /
             entryCost, export-time), gimbal (plausibility check), tech_tree
             (real RP-1 node names), chamber geometry, geometry3d (3D preview +
             symbolic turbopump block), mass_model (hoop-stress wall
             thickness/mass + ablative rated-burn-time), throttle sweep, and
             design/ (EngineDesign, the one object everything else calls;
             also to_dict/from_dict for the project file - a package since
             2026-09-23: engine.py + 17 compute stages in *_stage.py).
             cooling/ and validate/ are packages too; thermo_tables.py +
             property_data/ = the baked Cantera/CoolProp property tables
validation_engines/  real-engine corpus (cited) + frozen user designs, golden
             snapshots, run_corpus.py (--check / --report / --snapshot)
catalog/     build_catalog.py scrapes Engine_Configs/*.cfg into catalog.json,
             the "pick a host model" data source (RO parts are individually
             modeled - no generic reskinnable part exists, so "pick a model"
             means picking an existing part's #engineType to bind onto);
             build_roengines_models.py scrapes KSP-RO/ROEngines PartConfigs into
             roengines_models.json (native rendered height per #engineType) so
             the exporter can rescale a borrowed model

gui/         app.py (Tkinter shell - left-side input Notebook: Combustion
             Chamber, Injectors, Engine Bell, Turbopump, Gimbal, Model;
             right-side output Notebook: 2D Schematic, 3D Preview, Injector
             Face, Checklist, Turbopump; New/Save/Load + Export beneath the
             tabs) + project_io.py (JSON design save/load, pure/headless) +
             schematic.py (matplotlib 2D outline + wall heat-flux / cooling-
             zone overlay + face-on injector inset - draws either contour type
             automatically from whatever points design.py provides;
             independently unit-testable headlessly - see schematic.py's
             __main__) + preview3d.py (matplotlib 3D surface, colored by actual
             material, + injector-head disc/elements/baffle spokes) +
             injector_face.py (face-on injector-plate view: element pattern,
             baffle compartments, Helmholtz cavities) +
             turbopump_diagram.py (matplotlib 2D systems/flow diagram) +
             shape_lab.py (in-window Shape Lab: PlumbingLabPanel editor for a
             physics/plumbing.py run on any real manifold ring, opened per
             host from app.py's Plumbing tab, plus the
             synthetic-ring fallback panel; Tk, display needed) +
             shape_lab_geometry.py (its scenes incl. the ghost turbopump +
             free-end->pump ray, pure numpy, headless-tested) +
             mesh_builder.py (OpenGL-preview per-part mesh assembly incl.
             build_plumbing_pieces, shared by the Lab and the main preview)
physics/     ... plumbing.py (manifold-rooted procedural pipe runs: data model,
             geometry resolve, per-joint elbows/flanges, mass, advisories),
             cooling.py (Bartz h_g + computed wall temp + radiation
             equilibrium + regen Isp credit), combustion_stability.py (chamber
             acoustic modes + selectable stability aids: baffles / Helmholtz
             cavities / stiffer injector), turbopump_efficiency.py
             (derived pump & turbine efficiency), turbopump_sizing.py (1-D
             Ns/tip-speed sizing + envelope + geometry mass),
             turbopump_materials.py (rotor-material catalog) - all with headless
             __main__ smoke tests
export/      cfg_writer.py renders an EngineDesign + its result into RF text
             (engine config, optional gimbal patch, optional RP-1 gating patch)
```
