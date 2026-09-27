# Turbopump 3D tab — true-scale casings of the whole assembly (E2a, separate view)

Approved plan copy, 2026-09-27. Branch `turbopump/e2a-3d-tab`.

## Checklist
- [x] C1 `preview3d_gl_core/turbopump_meshes.py` + self-test + re-export
- [x] C2 `gui/turbopump_scene.py` + self-test (+ discharge-cone length cap)
- [ ] C3 `gui/pieces_preview.py` + `app.py` Turbopump 3D tab + verify_all lines
- [ ] C4 docs (CLAUDE.md, README, ASSUMPTIONS, roadmap)

## Context
The 3D preview draws the turbopump as a "ghost": coaxial capped cylinders from fixed
factors (`turbopump_sizing._assemble_bodies`), shrunk/grown by `render_scale` (0.2-2x) to
the SP-8107 mass. Round 2's meanline already designs each pump in detail (D1/D_hub/D2/b2,
meridional hub/shroud, volute spiral + tongue, vaned diffuser r3/r4, stage count; axial:
tip/hub/chord/stages), but none of it is drawn in 3D.

Cory's call (2026-09-27): build the more accurate turbopump as its **own "Turbopump 3D"
tab**, NOT applied to the main 3D view yet. Scope answers: **whole assembly** (both pumps +
turbine(s) on their shaft(s), with an isolate selector) and **casings only** (internals —
bladed impellers, inducer helix, turbine blades — are a later round).

Consequences of "separate tab":
- Draw at **true meanline scale**; no need to fit the render-scaled ghost or its ports.
- **Zero physics change**: nothing in `physics/` or `mesh_builder.build_mesh_data` changes,
  so the corpus stays bit-identical and the main preview/Shape Lab are untouched.
- No `EngineDesign` field, no schema bump; the isolate choice is transient tab state.

## Design

### 1. `gui/preview3d_gl_core/turbopump_meshes.py` (new submodule — pure numpy)
Casing primitives, all with the shaft on the local x axis (same convention as the
revolved-engine primitives), each returning `list[MeshBuffers]`:
- `volute_scroll_pieces(x_m, spiral, r_tongue_m, floor_r_m, discharge_dia_m, color, ...)`:
  the meanline spiral table (`(theta_deg, r_outer)`, 36 pts) → per-station section radius
  `rs = max(floor, (r_outer - r_tongue)/2)`, centre radius `r_tongue + rs`, swept with the
  existing `mesh_primitives.scroll_manifold_mesh` over 360 deg; then a tangential discharge
  diffuser cone (`duct_meshes.frustum_mesh`) from the spiral's end section to the discharge
  bore, + a `duct_meshes.pipe_flange_pieces` flange at its exit.
- `collector_torus_pieces(...)`: constant-section toroidal collector (axial pumps — the
  meanline has no volute dict for them; the Detail tab uses the same 0.35 x r_tip section)
  via `mesh_primitives.manifold_ring_mesh` + the same tangential cone/flange.
- `revolved_housing_pieces(xs, rs, ...)`: thin wrapper over `revolve_to_buffers` +
  `end_cap_ring` for the inlet neck / shroud housing / axial barrel / bearing housings.
- Re-export in `preview3d_gl_core/__init__.py`; `self_test()` hooked into `__main__.py`
  (finite geometry, spiral section radius non-decreasing, cone start centred on the
  spiral's end section within 1e-9, cone axis tangent to the spiral, flange at cone exit).

### 2. `gui/turbopump_scene.py` (new — pure numpy, no Tk/GL; same split as `shape_lab_geometry.py`)
`build_turbopump_scene(result, isolate="assembly") -> {"pieces", "center", "half",
"components", "summary"}`:
- Reads `result["turbopump_sizing"]` (`fuel_pump`/`ox_pump` with `meanline`, `turbine`/
  `ox_turbine`, `arrangement`) and discharge/exhaust bores from `result["turbopump_ports"]`
  (true bores already).
- **True-scale layout** (`turbopump_layout(sizing)`, pure + tested): mirrors
  `_assemble_bodies`'s order — single-shaft/geared: fuel pump | bearing span | turbine |
  span | ox pump inline, each pump's inlet facing outboard; dual-shaft: two units offset in
  z by `TURBOPUMP_UNIT_GAP_OD_MULT` x the largest true OD (geometry3d's constant). Spans use
  `turbopump_sizing.SHAFT_SPAN_FACTOR`. Geared is drawn inline like the ghost (real gearbox
  = a later E2 item — say so in the summary line).
- **Centrifugal pump casing** (per `meanline["stage"]`, `["meridional"]`, `["volute"]`,
  `n_stages`): inlet flange + neck at the inducer tip dia (`inlet_eye_dia_m`, length 0.4 x
  tip dia — the Detail tab's convention) → shroud housing = meridional shroud curve offset
  by a render clearance → for multistage, a crossover barrel at r2 + clearance over stages
  1..n-1 → volute scroll on the last stage (starts at the vaned diffuser's r4 when fitted,
  via the meanline's own `r_tongue_m`) → back face + bearing-housing cylinder toward the
  turbine.
- **Axial pump casing** (`d_tip_m`, `chord_m`, `n_stages`): inlet neck → barrel at tip +
  clearance over inducer + inlet guide row + n x (rotor+stator) (the Detail tab's axial
  lengths) → collector torus + discharge cone.
- **Turbine casing** (`disk_od_m`, `disk_thickness_m`, `manifold_od_m`,
  `manifold_length_m`, true scale): rotor housing revolve, inlet manifold torus with a
  radial GG/preburner inlet flange stub, exhaust collector cone ending at the turbine
  exhaust port bore.
- **Fallbacks**: pump with no meanline (`pump_model="correlation"`) → true-scale cylinder of
  `volute_od_m` x `body_length_m` + a note in `summary`; electric pump-fed → motor body as a
  cylinder from `bodies`; pressure-fed / no sizing → empty scene + summary "no turbopump".
- Colours: pump = turbopump material colour, turbine = darkened (same as
  `mesh_builder.build_turbopump_pieces`), PBR stamped by mesh_builder's existing material
  helper. Each piece tagged with its component key (`fuel_pump`/`ox_pump`/`turbine`/
  `ox_turbine`/`shaft`); `isolate` filters and re-frames (`center`/`half` from the kept
  vertices).
- Render-only constants (housing clearance, flange lip/width, bearing-housing radius,
  axial collector section, turbine torus split) live at the top of this module with a
  "render-only, no physics" note.
- `__main__` self-test on corpus designs (loader pattern from `turbopump_detail`'s
  self-test): H-1 (single-shaft GG), F-1, J-2 (dual-shaft, axial fuel pump), RS-25
  (staged, multistage fuel), RL10 (geared expander), Rutherford (electric), F-1 with
  `pump_model="correlation"`, a pressure-fed design. Checks: non-empty, finite, every
  isolate option non-empty and framed around its own vertices, pump casing max radius
  within [0.5, 1.3] x the meanline volute OD/2 (true scale), discharge cone exit bore ==
  port dia, and the main `mesh_builder.build_mesh_data` output unchanged for one design.

### 3. `gui/pieces_preview.py` (new) + `gui/app.py` tab
- `PiecesPreview(ttk.Frame)`: the Shape Lab's GL-or-matplotlib pattern
  (`shape_lab._ShapeLabBase._build_preview_widget` / `_redraw`) as a reusable widget:
  `EnginePreviewGLFrame.update_meshes(pieces, center, half)` when GL is available, else a
  matplotlib `Poly3DCollection` fallback; X-ray + Engineering-shading toggles. Shape Lab is
  NOT refactored onto it this round (GUI-only code, can't be click-tested here) — noted as
  a follow-up.
- `app.py`: a "Turbopump 3D" tab right after "Turbopump Detail": toolbar with an Isolate
  combobox (Assembly / Fuel pump / Ox pump / Turbine [/ Ox turbine]) + a summary label
  (true-scale dims: overall length, largest OD, per-pump D2/volute OD, and the note "main
  3D view still shows the ghost envelope"). Registered in `_tab_frames` /
  `_tab_redraw_fns` so it redraws only when visible, like every other result tab.

### 4. Docs + wiring
- `verify_all.sh`: add `engine_designer.gui.turbopump_scene` (the core submodule is covered
  by the existing `preview3d_gl_core` entry) + `ast.parse` of `gui/pieces_preview.py`.
- `CLAUDE.md`: verify-list line, `turbopump_meshes.py` in the `preview3d_gl_core` split
  list, one sentence on the Turbopump 3D tab; `engine_designer/README.md` GUI tab list;
  `ASSUMPTIONS.md` arbitrary-tier entry for the render-only casing constants; roadmap:
  split E2 into "E2a pump/turbine casings — separate Turbopump 3D tab (done)" and the
  remaining items (main-view adoption, gearbox, internals, turbine meanline geometry).

## Branch / commits
Worktree `.claude/worktrees/e2a-pump-casings`, branch renamed to `turbopump/e2a-3d-tab`
(off `origin/main` 023df57), draft PR, not merged until Cory tests it. Plan copy committed
to `engine_designer/plans/2026-09-27_turbopump_3d_tab.md` with a checklist.
- C1 `turbopump_meshes.py` + self-test + re-export
- C2 `turbopump_scene.py` + self-test + verify_all line
- C3 `pieces_preview.py` + app.py tab
- C4 docs

## Verification
- `./verify_all.sh` all PASS; `run_corpus --check` bit-identical (proves no physics drift).
- `python3 -m engine_designer.gui.preview3d_gl_core` and `python3 -m
  engine_designer.gui.turbopump_scene` self-tests pass.
- Headless eyeball: render each corpus scene with matplotlib Agg `Poly3DCollection` to PNGs
  in `$CLAUDE_JOB_DIR/tmp` and inspect them (volute wraps and grows, discharge cone
  tangent, inlet faces outboard, dual-shaft units separated).
- `ast.parse` of `app.py` / `pieces_preview.py`. No `$DISPLAY` here: Cory runs the GUI,
  opens the Turbopump 3D tab (GL and, if possible, matplotlib fallback), tries each isolate
  option and X-ray, and reports back.
