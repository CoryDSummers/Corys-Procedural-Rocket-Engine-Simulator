# True-scale turbopump casings in the main 3D view (E2b) + tighter assembly spacing

Approved plan copy, 2026-09-27. Branch `turbopump/e2a-3d-tab` (draft PR #25).

## Checklist
- [x] C1 `physics/turbopump_layout.py` + `layout_pieces` + Turbopump 3D tab onto it + spacing fix
- [x] C2 `turbopump_geometry_model` (schema 19) + ports/origin wiring + golden re-snapshot (added keys only)
- [x] C3 main preview / Shape Lab / matplotlib fallback + self-tests
- [x] C4 app.py "Use in main 3D view" checkbox (on the Turbopump 3D tab, not a dropdown)
- [x] C5 docs + plan copy + memory

## Context
E2a (PR #25, draft, untested) added a separate **Turbopump 3D** tab that draws the whole
assembly's casings at true meanline scale. The main 3D view still draws the "ghost": capped
cylinders sized to the specific-power mass (`turbopump_sizing` `bodies` × `render_scale`),
placed by `geometry3d.turbopump_origin_xyz`. Its ports (`geometry3d.turbopump_ports`) anchor
the plumbing. A `connect_to_pump` run's pipe length sets that leg's line loss, and on open
cycles the turbine exhaust port anchors the exhaust duct.

Cory asked for two things (2026-09-27):
1. **A toggle that applies the new model to the main 3D view.** He picked the **real geometry
   option**: a saved design setting. When on, the main view (and the Shape Lab) draws the
   casings, and the ports move to the real flanges, so plumbing lands on them. Pump-connected
   line losses and the exhaust duct then follow. The default stays the envelope, bit-identical.
2. **The "large empty part".** It is bare shaft between components. Each span is
   `SHAFT_SPAN_FACTOR` 0.30 × the LARGEST outer diameter in the assembly, which the big
   turbine sets, e.g. 0.69 m of 114 mm shaft between the F-1 fuel pump and turbine. Dual-shaft
   designs also get a band of `TURBOPUMP_UNIT_GAP_OD_MULT` 1.15 × the largest outer diameter
   between units (about 1 m of nothing on the RS-25). Cory picked **tighten + fill**.

Scale (per CLAUDE.md's token rule): a medium multi-file round of ~5 commits touching 1 new
physics module and ~8 existing files (`turbopump_scene.py`, `turbopump_meshes.py`,
`mesh_builder.py`, `shape_lab_geometry.py`, `preview3d.py`, `geometry3d.py`,
`turbomachinery_stage.py`, `engine.py`, `app.py`) plus docs. No file over 50 KB is read
whole; `app.py` and `mesh_builder.py` are read by section only.

## Design

### 1. `physics/turbopump_layout.py` (new, pure; the ONE source of casing geometry)
Ports now depend on casing geometry, so the geometry math has to live in `physics/`
(design.py can't import `gui/`).
- **What moves:** the math half of `gui/turbopump_scene.py`'s builders
  (`centrifugal_pump_casing`, `axial_pump_casing`, `envelope_pump_casing`, `turbine_casing`,
  the motor, `_units`), plus `turbopump_meshes.volute_sections` and the discharge-cone
  length/exit math from `volute_scroll_pieces`.
- **What each builder returns:** a mesh-free local spec per component:
  - housing polyline (xs, rs)
  - inlet flange (centre, dir, bore)
  - scroll stations (x, u_start, wrap, handed, centre r, tube r)
  - discharge cone (start, end, r0, r1) and flange
  - turbine inlet torus and GG stub
  - `od_m`, `length_m`, `r_link_m`, summary numbers
- **Discharge exit:** one analytic `scroll_exit(...)` gives pos/dir/dia. The mesher uses it
  too, so the drawn flange and the port can't drift apart.
- **Constants:** the render constants (clearances, flange lip, bearing housing, torus split,
  cone caps) move here unchanged.
- **Discharge orientation:** each pump scroll starts at `u_start` so its discharge ends at
  u = π, the −y side facing the engine axis. Handedness is chosen so the discharge points
  ±z away from the assembly centre, which is the ghost's own convention. The turbine
  exhaust scroll ends at −y the same way.
- **`build_layout(sizing, discharge_dia_by_pump, turbine_exhaust_dia_m)`:** places the
  components in unit order (same order as today) and returns local placements
  (x0, sx, dz), the link housings, `length_m`, `radial_extent_m`, and per-component
  `od_m`/`center`.
  - **Gap fix / spans:** span between neighbours = `SHAFT_SPAN_FACTOR` × the SMALLER
    neighbour's `od_m`.
  - **Gap fix / fill:** each span is drawn as a bearing/seal housing that tapers from one
    neighbour's `r_link_m` to the other's, not a bare rod. The turbine's `r_link` is its
    hub-housing radius.
  - **Gap fix / dual-shaft:** unit gap = ½ unit-0 OD + ½ unit-1 OD + `UNIT_CLEARANCE_OD_MULT`
    (0.10) × the largest OD, sized from the real casing extents.
- **`place_layout(layout, profile_x_max, profile_r_max)`:**
  - origin x = the ghost's 0.03 × length.
  - origin y = r_max + the layout's −y extent + the 0.04 × r_max standoff.
- **`ports_from_layout(placed)`:** same dict shape as `geometry3d.turbopump_ports`
  (`fuel_pump`/`ox_pump` inlet + discharge, and `turbine.exhaust` when the exhaust diameter
  is above 0), each with base/pos/dir/dia_m.
  - `pos` = the flange face.
  - `base` = one stub length back, along the neck or cone.
  - Inlet bore = the eye diameter; discharge bore = the ring feed bore. Both are the same
    as the ghost's.
- **`pump_points_from_layout(placed)`:** the pump casing centres, for the Shape Lab's rays.
- **`self_test()`:**
  - All corpus arrangements lay out with finite values.
  - Each port dir is a unit vector, and each port pos equals its flange centre.
  - Discharge dirs point ±z away from the assembly centre.
  - Single-shaft spans are ≤ the old spans (F-1 gap < 0.69 m).
  - Dual-shaft unit envelopes don't overlap.
  - A pressure-fed design gives None.
- Added to `verify_all.sh` and the CLAUDE.md verify list.

### 2. Meshing: `preview3d_gl_core/turbopump_meshes.py` + `gui/turbopump_scene.py`
- New `layout_pieces(placed_or_local_layout, pump_rgb, turb_rgb, flange_rgb)` →
  `[(component_key, [MeshBuffers])]`. It reuses `revolve_polyline_pieces`,
  `scroll_manifold_mesh`, `frustum_mesh`, `manifold_ring_mesh`, `pipe_flange_pieces` and
  `place_pieces`, but takes its numbers from the layout spec.
- `volute_scroll_pieces` keeps its signature but gets its exit from
  `turbopump_layout.scroll_exit`.
- `turbopump_scene.build_turbopump_scene` becomes thin: `build_layout` at the local origin
  → `layout_pieces` → `_tag`/isolate/frame, as today. The tab always shows casings,
  whatever the toggle. Its summary note says whether the main view is using them.
- The tab's self-test is kept. It adds the tightened-span checks.

### 3. Design setting + physics wiring (schema 19)
- **The setting:** `EngineDesign.turbopump_geometry_model: str = "envelope"`
  (`"envelope" | "casings"`).
  - Schema 19, no key migration; an old file gets "envelope", bit-identical.
  - Round-trip it in the `project_io` self-test.
- **Design pipeline** (`design/turbomachinery_stage.py`, where `s.turbopump_ports` is built
  today): when "casings" and the sizing has bodies, it builds the layout, runs
  `place_layout`, then `s.turbopump_ports = ports_from_layout(...)` and
  `s.turbopump_layout = placed`. Everything downstream reads `s.turbopump_ports`
  unchanged: connected-run line loss, the implicit exhaust duct seed, plumbing mass.
  "envelope" keeps the existing code path untouched.
- **Result:** `rollup_stage` exports `"turbopump_layout"` (None in envelope mode) and the
  input.
- **Placement:** `geometry3d.turbopump_origin_for_result(result)` returns the layout's origin
  when `result["turbopump_layout"]` is present. It stays the ONE placement every consumer
  uses.
- **Pumps without meanline geometry:** with `pump_model "correlation"` there is no meanline,
  so the layout uses the true-scale envelope cylinder (volute OD × body length, as the tab
  does now). Its ports sit on that cylinder like the ghost's, and a warn-only info row
  explains this.
- **Unchanged by design:** turbopump MASS is still the specific-power / SP-8107 rollup; the
  casing wall/mass model is E3. Say so in the checklist row and ASSUMPTIONS.

### 4. Views
- **Main 3D preview** (`mesh_builder.build_turbopump_pieces`): when there is a
  `turbopump_layout`, draw `layout_pieces` placed at its origin, with the turbopump
  material's colours and PBR stamping as today. Skip `turbopump_port_stub_pieces` there;
  the flanges ARE the ports. Otherwise draw the ghost as today.
  - Self-test: the existing ghost assertions stay for envelope mode. Add a casings case:
    every port pos lies within 1 mm of a drawn flange vertex ring, and a connected run's
    last waypoint equals its port pos.
- **Shape Lab** (`shape_lab_geometry.ghost_turbopump_from_result`): same switch, in
  `GHOST_TURBOPUMP_RGB`, with pump points from `pump_points_from_layout`.
- **matplotlib fallback** (`gui/preview3d.py`): in casings mode, draw the layout pieces as
  `Poly3DCollection` triangles (the `pieces_preview` pattern) instead of `plot_surface`
  grids, and grow the axis cube from their extents.

### 5. GUI (`gui/app.py`, syntax-check only here)
- **Dropdown:** "Turbopump 3D geometry (envelope = mass-sized ghost, casings = true-scale
  meanline casings — moves pump/turbine ports + plumbing)", values `["envelope", "casings"]`.
  - It goes in the turbopump section next to "Pump model". It follows the
    `pump_model_var` pattern: `_add_dropdown`, read in the design-from-widgets block
    (~l.2020), set in load (~l.3146).
- **Turbopump 3D tab:** the summary note changes to say whether the main view is showing
  these casings.

### 6. Docs
- **CLAUDE.md:** new verify line; one sentence on the setting in the turbopump paragraph
  (default envelope; casings moves ports/line loss).
- **README:** one paragraph.
- **ASSUMPTIONS.md:** the casing constants' Tier-3 row now says they place ports in casings
  mode; new row for the tightened span / unit clearance.
- **Roadmap:** E2b "main-view adoption" ticked as the opt-in option; still open: gearbox,
  Round-3 turbine casings, E3 walls/mass retiring `render_scale`.
- **Plan copy:** `engine_designer/plans/2026-09-27_turbopump_casings_main_view.md` with the
  checklist.
- **Memory:** update the roadmap memory.

## Branch / commits
Continue on `turbopump/e2a-3d-tab` (draft PR #25). It is unmerged and untested, and this
builds directly on it, so one PR avoids another stacked-merge tangle. Update the PR body.
- C1 `physics/turbopump_layout.py` + `turbopump_meshes.layout_pieces` + `turbopump_scene`
  onto it (the tab's only visible change is the tighter spacing) + verify line
- C2 the setting, schema 19, `turbomachinery_stage`/`rollup`/`geometry3d` origin +
  project_io round-trip
- C3 main preview / Shape Lab / matplotlib fallback casings drawing + self-tests
- C4 `app.py` dropdown + tab note
- C5 docs + plan copy + memory

## Verification
- `./verify_all.sh` all PASS. `run_corpus --check` stays bit-identical, since the default
  envelope doesn't change physics.
- The `turbopump_layout`, `turbopump_scene`, `mesh_builder` and `project_io` self-tests
  pass.
- **Casings sweep:** every corpus/user design recomputed with `turbopump_geometry_model=
  "casings"`, all finite. Report the per-design change in connected-run line loss, plumbing
  mass and Pc/Isp where a run is pump-connected: that is the intended physics change, shown
  to Cory rather than snapshotted.
- **Headless renders** (matplotlib Agg of the main-view pieces: engine + casings + plumbing)
  for F-1, J-2, RS-25 and one user design with connected runs, to eyeball that:
  - the pipes land on the flanges
  - the discharges face the engine
  - the spans are tighter and filled
  - the dual-shaft units sit closer
- `ast.parse` on `app.py`/`pieces_preview.py`. No `$DISPLAY` here: Cory click-tests the
  dropdown, the main 3D view, the Shape Lab and the tab.
