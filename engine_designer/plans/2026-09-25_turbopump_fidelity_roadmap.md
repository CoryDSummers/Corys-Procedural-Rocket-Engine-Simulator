# Roadmap: high-fidelity turbopump modeling (2026-09-25)

A committed copy of the approved roadmap so a later session can resume it. **This is a roadmap,
not one round:** each round below gets its own plan through plan mode (convention #3), and its
own `plans/*.md` doc if it spans several commits. **Tick each box when its round lands** (with
the commit hash).

Branch: `worktree-turbopump-fidelity`, cut from `origin/main` @ 83bcd41. The worktree is
`.claude/worktrees/turbopump-fidelity/`. It's a **separate test branch**: a draft PR to `main`
that stays unmerged until Cory has tested it. Keep it current by merging `origin/main` into it.
No rebase, no force-push.

How to test the branch:
```
cd /home/cory/ksp_config/.claude/worktrees/turbopump-fidelity && python3 -m engine_designer.gui.app
```
For an A/B comparison, run the same command from `/home/cory/ksp_config` (main-equivalent) on the
same design file.

## Status
- [x] Commit 0: this document
- [ ] Round 0: groundwork (distill new PDFs, acquire SP-8052/8110/8125/8121/8101, vapor-pressure table columns, F-1 pump-power fix)
- [ ] Round 1: suction side (inducer.py, computed NPSHr + thermodynamic suppression, tank/line/boost pump)
- [ ] E1: pump placement/orientation/mounting + clash check (can run alongside Round 1)
- [ ] Round 2: pump meanline hydraulics + pump heating into the thermal solve
- [ ] Round 3: turbine meanline + blade/disk stress
- [ ] E2: volute scroll + real casings
- [ ] E3: hoop-stress casing walls (retires `render_scale`)
- [ ] Round 4: rotor mechanics + geometry-derived mass
- [ ] E4: GG/preburner/start hardware as plumbing hosts
- [ ] E5: PBR materials, X-ray internals, flow through the pump
- [ ] Round 5: off-design maps + transients

## Context
Cory asked what a *highly in-depth* turbopump model would need, starting from where the tool is
today, and then about exterior modelling as well. This is the gap analysis and staged roadmap.

### What exists today (verified in code, 2026-09-25)
- `physics/turbopump_sizing.py` — 1-D by-hand sizing per [SP-8107 2.1.1]/[Huzel Ch VI]:
  - Ns target 2200 → rpm; head coefficient psi 0.5 → tip speed; 6000 ft/stage → stage count.
  - Inlet eye from a flow coefficient.
  - Optional NPSH cap (`suction_limited_rpm`) with NSS targets 40k/58k. NPSH-required uses a
    historical anchor × margin factor.
  - Turbine U/C0 by staging; single/dual/geared shaft arrangement by rule.
  - Torsion-sized shaft diameter plus a bearing-DN check.
  - Mass from the [SP-8107 Table I] specific-power trend; the geometric envelope is scaled to
    that mass, not the other way round.
- `turbopump_efficiency.py` — pump η = peak × Ns-bell × size penalty. Turbine η = staging ceiling ×
  pitchline × admission × PR factor. Both are calibrated to SP-8107 Tables II/III within ±8 %.
- `turbopump_materials.py` (rotor and bearing catalogs), `turbopump_tech.py` (build-quality tier).
- `staged_combustion.py` solves the preburner power balance and turbine PR. `expander.py` and
  `turbine_exhaust.py` cover the other cycles' turbine drive and exhaust.
- The GUI has a turbopump systems diagram. The 3D view has a ghost envelope and pump ports.

### Known gaps
1. **No real cavitation physics.** NPSHr is anchored, not computed. There is no inducer, no
   thermodynamic suppression, no tank/suction line and no boost pump. Rotor speed is therefore
   over-predicted for high-head pumps. That inflates diameters, which is why mass has to come from
   specific power.
2. **No blade-level hydraulics.** There are no velocity triangles, slip, blade angles, outlet
   width or volute/diffuser, and no loss breakdown. Efficiency is a fitted curve.
3. **Turbine is a correlation.** There are no nozzle/rotor triangles, reaction, blade heights,
   partial-admission arc or loss model. There are no blade or disk stresses.
4. **No rotor mechanics.** There are no critical speeds, no bearing sizing or L10 life, no seals
   or inter-propellant seal, and no axial-thrust balance. `BEARING_BORE_OVER_SHAFT_FACTOR` is
   unsourced.
5. **No thermal coupling.** Pump inefficiency heating isn't fed into the jacket inlet
   (`design/constants.py` fixes `COOLANT_INLET_TEMP_K`). Bearing coolant flows, turbine heat soak
   and LOX-side hazards aren't modelled.
6. **Design point only.** There are no H-Q/η maps, no pump–turbine matching off design, no
   throttle line and no spin-up/start transient.
7. **Calibration item:** F-1 pump power is ~20 % low (OPEN_QUESTIONS, `validate` turbine-exhaust
   (i)).
8. **Missing data:** `property_data/coolant_properties.json` has no vapor-pressure column, which
   NPSH needs.

## Internal rounds

### Round 0 — groundwork (literature + calibration + data)
- **Literature.** Identify the five undistilled NTRS PDFs in `literature/` (19700026405,
  19730005057, 19770020235, 19850008634, 20180005537; their metadata has no titles). Distill any
  turbopump ones via `lit-integrator`.
- **Sources to acquire.** Priority order:
  - SP-8052 *Turbopump Inducers*
  - SP-8110 *Turbines*
  - SP-8125 *Axial-Flow Turbopumps* (J-2/SSME LH2 pumps)
  - SP-8121 *Rotating-Shaft Seals*
  - SP-8101 *Shafts and Couplings*
  - the unread §2.2/§3.2 of SP-8048
  - textbooks: Brennen *Hydrodynamics of Pumps* (free; cavitation, inducers, rotordynamics),
    Gülich *Centrifugal Pumps* (loss models)
- **Per-component validation data** is the hard part. Needed: rpm, D2, stages, head, flow, η,
  NPSHr and power for each of:
  - SSME HPFTP/HPOTP/LPFTP/LPOTP
  - J-2 Mk15-F/-O
  - F-1 Mk10
  - RL10
  - RD-170/NK-33 (KBKhA and NK-33-Mod are already distilled)
- **Data table:** add saturation vapor pressure (and ρ_v, h_fg for thermodynamic suppression) to
  `tools/property_tables/generate_property_tables.py` and regenerate. Never hand-edit the table.
- **Calibration:** root-cause the F-1 pump-power shortfall before building anything on top.

### Round 1 — suction side (highest leverage; fixes the rpm → diameter → mass chain)
- New `physics/inducer.py`:
  - flow coefficient, blade tip angle, cavitation number, head-breakdown criterion
  - computed NPSHr (SP-8052 / Brennen)
  - thermodynamic suppression (Stepanoff B-factor) for LH2/LOX
- Tank pressure + suction line + boost pump (SSME-style LPxTP) → computed NPSHa. This merges with
  the pending "lines round" and reuses `plumbing.run_pressure_loss_pa`.
- The NPSH cap becomes on by default once NPSHa is computed. Keep a bit-identical legacy path
  behind a flag or schema, per the corpus-golden workflow.

### Round 2 — pump meanline hydraulics
- Impeller velocity triangles: inlet/outlet blade angles, Wiesner slip, blade count, b2, Euler
  head.
- Volute/diffuser sizing.
- Loss build-up: incidence, friction, diffusion, disk friction, wear-ring leakage → volumetric
  efficiency, recirculation.
- η is built from these losses. The existing Ns-bell stays as a cross-check row, not deleted.
- Axial-pump option for LH2 (SP-8125).
- Pump enthalpy rise → propellant temperature at the jacket inlet and injector. This couples into
  the unified thermal solve (`cooling/thermal_solve.py`) through the existing multi-pass
  `_compute_pass`. It must stay ONE solve.

### Round 3 — turbine meanline + hot-section structures
- Nozzle and rotor triangles, degree of reaction, blade heights, partial-admission arc.
- Loss model: Soderberg or Kacker–Okapuu, tip clearance, leaving loss.
- Gas properties from the existing preburner/GG gas data.
- η is built from the losses. The current ceiling model stays as a cross-check.
- Blade centrifugal + gas-bending stress, rotating-disk stress/burst margin, creep versus turbine
  inlet temperature. These use `turbopump_materials.py`.

### Round 4 — rotor mechanics + geometry-derived mass
- Shaft critical speeds: Jeffcott first, then transfer matrix. Report sub- vs supercritical
  (the SSME HPFTP runs supercritical).
- Bearing sizing, stiffness and L10 life (SP-8048), plus bearing coolant flow.
- Seals and the LOX/fuel inter-propellant seal with helium purge (SP-8121). This matters for
  single-shaft designs.
- Axial-thrust balance (balance piston, SP-8109) and radial loads.
- Mass built from component geometry: pressure-containment housings plus rotor disks. The
  specific-power mass becomes the cross-check instead of the source. This is only credible after
  Rounds 1–2 fix the diameters.

### Round 5 — off-design + transients
- H-Q/η maps from similarity laws plus the meanline slope, and pump–turbine operating-point
  matching.
- Throttle line; stall and cavitation margins along it.
- Spin-up from rotor polar inertia; start modes (tank-head, spinner, solid cartridge). Ties to
  `claude_lit/topics/15-transients-and-controls.md`.

## Exterior modelling track (runs alongside Rounds 1–5)

### What exists
- `turbopump_sizing._assemble_bodies` lays out coaxial bounding cylinders (pump, turbine, disk)
  sized from fixed factors: `VOLUTE_OD_FACTOR` 1.6, `INDUCER_LEN_FACTOR`, `DISK_OD_FACTOR`,
  `MANIFOLD_*_FACTOR`.
- The cylinders are then shrunk or grown by `render_scale` (clamped 0.2–2×) to match the
  specific-power mass. The exterior is cosmetic and follows the mass, not the reverse.
- Placement is fixed: `geometry3d.turbopump_origin_xyz` uses a fraction of engine length plus a
  standoff, with the shaft parallel to the engine axis. Dual-shaft units are spread by
  `TURBOPUMP_UNIT_GAP_OD_MULT`.
- Only the port stubs (`geometry3d.turbopump_ports`, drawn by
  `mesh_builder.turbopump_port_stub_pieces`) use true bores. They sit on render-scaled bodies.
- There are no mounts, housings for bearings or seals, or turbine inlet manifold. The GG or
  preburner isn't attached to the turbine, and there are no clearance checks.

### What in-depth exterior modelling needs
- **E1 — Placement and mounting.** Independent of the internal rounds.
  - User-set pump position: azimuth, axial station, standoff.
  - Shaft orientation: parallel to the engine axis (J-2/H-1) or tangential/perpendicular (F-1
    Mk10).
  - Mounting struts/brackets to the chamber or thrust structure as meshes with an estimated mass.
  - A clearance/clash check (warn-only) against the nozzle, manifolds, hatbands and plumbing,
    including the gimbal sweep envelope.
  - These are new `EngineDesign` fields with a schema bump. The single placement function
    `turbopump_origin_for_result` becomes the one place that reads them, so both previews, the
    Shape Lab and pump-connected runs follow automatically.
- **E2 — Real casings from real internals.** Follows Rounds 1–3.
  - Volute scroll: spiral casing whose area grows with wrap angle (constant-velocity or
    angular-momentum law per [SP-8109]/Stepanoff), with a cutwater/tongue and a tangential
    discharge diffuser cone. The discharge port direction then becomes tangential, not radial.
  - Inducer inlet housing with an axial inlet flange; multistage axial barrel plus crossover
    ducts for LH2 pumps.
  - Turbine inlet torus or partial-admission arc manifold; turbine exhaust collector feeding the
    existing `turbine_exhaust` port.
  - Bearing and seal housings, drain and helium-purge ports, gearbox case (geared/RL10 class).
- **E3 — Pressure-containment wall sizing.**
  - Casing wall thickness from hoop stress at local pressure: inlet/discharge on the pump side,
    inlet temperature and pressure on the turbine side (reuses the `manifold.py` hoop-stress
    pattern).
  - Flange and bolt-circle sizing at the ports.
  - Walls plus rotor give the geometry-derived mass of Round 4, so `render_scale` can be
    retired. Specific power becomes the cross-check.
- **E4 — Cycle-specific hardware on the pump.**
  - GG bolted to the turbine manifold (F-1/H-1).
  - Preburner sitting on the turbine, with a hot-gas duct to the main injector (SSME powerhead,
    RD-180).
  - Start hardware: spin-start gas inlet, solid start cartridge.
  - Tap-off/bleed ports.
  - New `plumbing.HOSTS` entries (GG/preburner → turbine inlet, pump → GG feed), so these become
    editable runs in the Plumbing tab like the existing hosts.
- **E5 — Rendering and flow visualization.**
  - Per-component PBR materials (aluminum pump casing, Inconel turbine housing, insulation
    blanket on hot turbines).
  - X-ray layer tags so internals (impeller, inducer, turbine disk) show through the
    translucent casing.
  - `flow_network` extended through the pump: inlet → discharge temperature rise from
    Round 2's enthalpy rise.

### Honest limits
- All of this lives in the tool's own 3D preview, Shape Lab, mass and clearance checks. The
  exported `.cfg` still borrows an existing RO host model, so KSP's look doesn't change unless a
  custom model export is added. That is out of scope here.
- New geometry math goes in the testable split (`preview3d_gl_core/*`, `gui/mesh_builder.py`,
  `physics/geometry3d.py`) with self-tests. Visual output is screenshot-checkable only in the
  cloud Xvfb sandbox; clicking through is Cory's to check.

## Order
1. Round 0 plus Round 1 first. Suction physics is the single change that unlocks credible
   diameters, and every later round depends on it.
2. E1 can run in parallel with Round 1.
3. E2/E3 follow Rounds 2–3; E3 is what lets Round 4 retire `render_scale`.
4. E4/E5 come last; Round 5 closes the roadmap.

## Cross-cutting rules each round follows
- **Spot checks.** Every new submodel gets a `validate` spot check against a real turbopump
  (convention #1). Every uncited constant gets a tiered entry in `ASSUMPTIONS.md`.
- **Warn, don't block.** Cavitation, critical-speed and burst margins are checklist rows, not hard
  stops.
- **Schema and GUI.** New `EngineDesign` fields need a schema bump, a `project_io` round-trip and
  a Turbopump tab in the GUI. The GUI can only be syntax-checked here (no `$DISPLAY`).
- **Reports.** After each physics change: `./verify_all.sh`, then `run_corpus --report --diff`
  saved to `validation_engines/reports/`, then `--snapshot`.
- **Verification.** `./verify_all.sh` all PASS, `run_corpus --check` bit-identical on the legacy
  path, and new spot checks for J-2 / SSME / F-1 / RL10 pump rpm, NPSHr, η and power within cited
  bands.
