# Turbopump placement + orthogonal routing (roadmap E1, minus mounts/clash check)

Branch `turbopump/e1-placement` off `origin/main` (c6c476a); draft PR, not merged until Cory
has run the GUI. Approved plan below, then the checklist and the as-built deviations.

## Checklist
- [x] C1 placement transform, bit-identical (b319fb1)
- [x] C2 orthogonal auto legs + seed fixes; report `2026-09-30_e1_orthogonal_legs_before_after.txt`, re-snapshot (7e4d442)
- [x] C3 fields (schema 20), span-aware default, clock-together, wiring; report `2026-09-30_e1_placement_before_after.txt`, re-snapshot (3c76193)
- [x] C4 GUI placement section (cc207af) - syntax/import-checked only, Cory to click through
- [x] C5 docs (ASSUMPTIONS, roadmap, README, CLAUDE.md, TURBOPUMP_FLOW, this copy)
- [x] C6 head mount + pump orientation (roll / flip / radial preset), engine-aligned port frame, stub-aware hull; corpus additions only, report `2026-10-01_e1_head_mount_roll_before_after.txt`, re-snapshot (bb4b61e) - follow-up request 2026-10-01, plan `~/.claude/plans/lets-consider-the-positioning-linked-sunset.md`
- [x] C7 GUI: mount / head offset / radial / roll / flip controls (aefd644) - syntax/import-checked only
- [x] C8 docs (ASSUMPTIONS row, README, CLAUDE.md, TURBOPUMP_FLOW, this copy)
- [x] C9 free mount (hand-set height + offset, clearance warn row), `turbopump_head_offset_m` -> `turbopump_offset_m`, + `turbopump_height_m`; corpus = input-key rename + addition only, report `2026-10-01_e1_free_mount_before_after.txt`, re-snapshot (3594e6b) - Cory 2026-10-01: "I meant for the turbopump to be able be adjusted higher than the combustion chamber"; chose free height + sideways, keep the head mount
- [x] C10 GUI: free in the mount dropdown, height + shared offset sliders sized to the engine, seed-on-switch (c4c373c) - syntax/import-checked + handlers stub-tested only
- [x] C11 docs (ASSUMPTIONS row, README, CLAUDE.md, TURBOPUMP_FLOW, this copy)
- [ ] Cory GUI test: placement sliders, main 3D view, Shape Lab "Route to pump", RS-29.json, mount dropdown / roll / flip / offset, free mount height / offset sliders + seeding + clash warn row
- [ ] Rest of E1 (deferred): mounting struts/brackets + mass, clash check incl. gimbal sweep

## As built (deviations from the plan)
- Auto-leg U-jog (`MANHATTAN_JOG_DIA_MULT` 3 bores) when S lies straight behind the last pipe;
  shorter straight entry (`AUTO_ENTRY_MIN_DIA_MULT` 1 bore) when the run already faces the port
  inside the standoff; S-bends preferred; fold-in threshold 0.5 bore (plan: 0.25); stale ratio
  1.0 (plan: 2.0) - all found on the corpus' default exhaust ducts.
- Overboard exhaust nozzle with no baked duct clocks onto the turbine exhaust port's axis
  (`plumbing.overboard_outlet_on_port_axis`, `turbine_exhaust.size_hardware(outlet_radius_m=)`),
  a baked run sets the nozzle's angle - otherwise the tangential exhaust port forced a U-shaped
  default duct. The scroll seed aims at the nearest reachable point on a tangential port's axis
  (plan: S + 3 bores, which swung the F-1 duct 4 m out).
- The "end lies inside the manifold ring's radius" heuristic checks user pipes only; auto legs
  get `auto_leg_clearance_advisories` against the real contour.
- A "Turbopump placement" checklist row and a `run_corpus` probe "turbopump wall clearance"
  (all 16 turbopump corpus engines clear, 12-185 mm).
- C6/C7 follow-up (2026-10-01, Cory: "turbopump above the chamber like the NK-33" + "rotate the
  turbopump itself for better pipe placement"; chose presets + roll + flip, advisory-only export
  height, same branch / schema 20): planned as separate orientation and head-mount commits,
  landed as one (they share the solver rewrite). Not planned: the ghost's port nozzle stubs
  join the placement hull (an axial inlet stub hit the injector dome on a head mount), but only
  when aimed AT the obstacle - counting every stub pushed a default side mount ~0.3 m out where
  an aft inlet stub overlapped the bell; casing boxes now span everything drawn along the shaft
  (a flipped casings head mount poked 4.5 mm into the dome). Known gap: on a head mount the
  turbine-exhaust Route-to-pump lands but routes poorly (warn-only rows) - its seeds assume a
  side-mounted pump.
- The "was X" Isp values on user_designs/RS-29 in `--report --diff` are a pre-existing report
  quirk (also in the 2026-09-26 tap-off report); `--check` shows Isp unchanged.

## Context
Turbopump placement is hard-coded and gives awkward geometry. Cory confirmed three symptoms:
1. **Pump hangs far outboard.** `geometry3d.turbopump_origin_xyz` (geometry3d.py:85-89) and
   `turbopump_layout.place_layout` (:417-428) measure the standoff from the contour's GLOBAL max radius,
   usually the bell exit, even though the pump sits at the injector end (x = 0.03 L).
   - F-1: the pump axis is about 2.35 m off the engine axis, against a chamber radius of 0.58 m.
   - J-2: about 1.29 m, against 0.23 m.
2. **Diagonal feed/exhaust pipes.** The auto leg A in `plumbing.resolve_run` (:483-515) is a straight
   line in any direction. The default exhaust duct is seeded at one attach angle and then overridden to
   another (`turbomachinery_stage.py:155-156`).
3. **Wrong side / clocking.** Azimuth is fixed at +Y and the shaft is always parallel to the engine axis.
   The envelope turbine-exhaust direction (geometry3d.py:197-201) can flip between designs, and it
   disagrees with casings mode.

Approved scope: "Placement + routing".
- A better default rule and user placement fields.
- Orthogonal auto legs with warn-only advisories.
- Mounting struts and the clash check stay deferred (rest of E1).

The new default applies to every design, followed by a corpus re-snapshot. Branch `turbopump/e1-placement`
off origin/main with a draft PR. Fields stay flat, SCHEMA_VERSION 19 -> 20. The unmerged local branch
`refactor/design-inputs` also claims 20, so whichever merges second renumbers to 21 and adds these
4 fields to `inputs/paths.FIELD_PATHS`.

## Design

**New EngineDesign fields** (engine.py, next to `turbopump_geometry_model` :454):

| Field | Default | Meaning |
|---|---|---|
| `turbopump_azimuth_deg` | 0.0 | Clock about +x. Same convention as `attach_angle_deg`: 0 = +Y, increasing toward +Z. |
| `turbopump_axial_station_frac` | 0.0 | Assembly midpoint ÷ engine length. 0 = auto. |
| `turbopump_standoff_m` | 0.0 | Gap between the obstacle envelope and the assembly's engine-side reach. 0 = auto, 4 % of the local radius. |
| `turbopump_shaft_orientation` | "axial" | "axial" or "tangential". |

GUI labels stay neutral, with no engine names. The roadmap's "tangential = F-1 Mk10" is likely wrong, since
the F-1 shaft is parallel to the chamber, and nothing in claude_lit sources it.

**Transform.** Define the frame vectors:
- e_x = (1,0,0)
- e_r(φ) = (0, cos φ, sin φ)
- e_θ(φ) = (0, −sin φ, cos φ)

Rotation matrices (columns):
- R_axial = [e_x | e_r | e_θ]
- R_tangential = [e_θ | e_r | −e_x]

Both have det = +1. With φ = 0, R_axial = I.

The local frame keeps today's layout:
- Shaft along x_L.
- Engine side on −y_L.
- Dual-unit spread along z_L.

World coordinates: point = O + R·p_L, direction = R·d_L, normal = R·n_L.

**Default rule (span-aware):**
- Assembly centre: C = (x_s, 0, 0) + ρ·e_r(φ), and O = C − R·c_L.
- Auto x_s = 0.03·x_max + half the world-x extent. For an axial shaft this reproduces today's start.
- ρ = max over bodies of [reach_b + r_env(span_b) + gap_b].
- r_env is the max of three things over the body's world-x span:
  - the contour radius (interpolated, clamped);
  - ring bands for fuel/ox/jacket_inlet/return, the exhaust scroll and the aspirator collar;
  - the aspirator shroud and the overboard outlet.
- Legacy identity (asserted in a test): if r_env ≡ r_max, φ = 0 and the shaft is axial, then
  ρ = 1.04·r_max + od/2, today's formula exactly.
- Expected result: F-1 ~2.35 → 1.56 m, J-2 ~1.29 → 0.68 m.

**Clock-together.**
- The exhaust hardware `attach_angle_deg` becomes φ (turbomachinery_stage.py:101).
- Default ring-inlet angles (manifold_stage.py:36-49, :165) become fuel φ, ox φ+180, jacket φ.
- Bit-identical at φ = 0.

**Manhattan auto legs** (`plumbing._manhattan_targets(W, t_prev, S, P, p_dir, frame, d_port)`). Each port
dict gains a `frame` (rows e_x, e_r, e_θ). Route from the last waypoint W to the standoff point S:
1. Decompose S − W along the frame axes.
2. Merge any component under 0.25·d (`MANHATTAN_MIN_LEG_DIA_MULT`).
3. Order the ≤3 axis segments by this ranking:
   - The last segment must not lie on the port axis (unless collinear with −p̂, then it merges with leg B).
   - No reversal against t_prev.
   - Prefer continuing t_prev.
   - Outward radial first, inward radial last.
   - Fixed tie-break (x, r, θ).
4. Then leg B: S → P, as today.

Still re-solved by every caller, so the run always lands on the port.

**Warn-only advisories:**
- **Oblique:** auto leg > 20° (`AUTO_LEG_OBLIQUE_DEG`) from every frame axis.
- **Clearance:** `auto_leg_clearance_advisories`, 8 samples per leg, flags r < contour r(x).
- **Stale saved run:** the auto legs' excess length over (standoff + approach)·d is more than
  max(2 × the user pipes' length, 10·d). Message: "pump probably moved - Route to pump re-seeds".
  Saved runs are never mutated automatically.

## Commits (each: `./verify_all.sh` green)

**C1. Placement transform (bit-identical refactor).**
- `geometry3d.py`:
  - Add `turbopump_rotation(az, orient)`, `place_point` and `place_dir`.
  - `turbopump_body_centers`, `turbopump_pump_points`, `turbopump_ports` and
    `turbopump_assembly_meshes` accept a `{origin_xyz, rotation}` dict or the legacy tuple.
  - The legacy path is untouched when there is no rotation.
  - Move `_discharge_sign` here as the shared `discharge_sign`.
- `turbopump_layout.py`:
  - `to_world`, `dir_to_world` and `pump_points_from_layout` apply `layout["rotation"]`.
  - `build_layout` stores `reach_m` per placement.
- `preview3d_gl_core/turbopump_meshes.py`: add `transform_pieces(pieces, O, R)`, applied in
  `layout_pieces` (:192) after `place_pieces`.
- `gui/turbopump_scene.py:50` forces the identity, so the separate tab is unchanged.
- Self-tests: rotated ports sit on their flange faces, |dir| = 1, bores are unchanged, and
  R = I reproduces the old output exactly.
- The corpus `--check` must report bit-identical.

**C2. Orthogonal auto legs and seed fixes (`plumbing.py`, `turbomachinery_stage.py`).**
- `resolve_run` :483-515: replace the leg loop with `_manhattan_targets`, and add the oblique and
  stale advisories.
- `seed_route_to_port` (:834) gains `fixed_attach_angle_deg=None`. A point hook gets a forward stub
  to S's station, and the auto legs finish the route.
- `_seed_scroll_route`: when p̂ ⊥ e_x, aim at a point on the port axis, so the approach is one straight
  line into the port.
- `turbomachinery_stage.py:151-156`: pass the fixed angle and delete the post-seed override.
- Update the self-test asserts at plumbing.py :1190 and :1286-1293. New invariants:
  - every auto leg lies on a frame axis;
  - no turn > 90°;
  - a fresh seed gives no stale advisory, and the same seed with the port moved 1 m gives one.
- Corpus: save `--report --diff` → `validation_engines/reports/2026-09-30_e1_orthogonal_legs_before_after.txt`,
  then `--snapshot`.

**C3. Fields, default rule and wiring.**
- `engine.py`: the 4 fields; schema 20 plus a changelog line. A v19 file loads with every field on auto.
- `geometry3d.py`:
  - New `obstacle_bands`, `envelope_r_max`, `boxes_from_bodies`, and
    `turbopump_placement(boxes, length, xs, rs, *, azimuth_deg, axial_station_frac, standoff_m,
    shaft_orientation, bands)`, returning origin, rotation, x_span, axis radius, resolved standoff,
    station and governing body.
  - `turbopump_origin_for_result` and the new `turbopump_placement_for_result` read
    `result["turbopump_placement"]`, falling back to the legacy rule.
  - Envelope turbine exhaust becomes a deterministic tangential port on the −y_L rim, matching the
    casings scroll.
- `turbopump_layout.place_layout(layout, xs, rs, **placement_kw)` uses component and link boxes.
- `turbomachinery_stage.py`:
  - One placement solve serves both modes (:116-136).
  - `size_hardware(attach_angle_deg=φ)`.
  - Store `s.turbopump_placement`.
  - Add the clearance advisory for connected runs.
- `manifold_stage.py`: ring-inlet defaults follow φ.
- `rollup_stage.py:308`: export `turbopump_placement`.
- Consumers pass the placement dict:
  - `mesh_builder.py:1114-1115`; turn the regression test at :1888-1906 into invariants.
  - `preview3d.py:149-170`; the extent uses √(Y²+Z²).
  - `shape_lab_geometry.py:196-200`.
- `run_corpus._consistency`: new probe "turbopump clear of contour and rings".
- `gui/project_io.py`: round trip a v19 file (fields go to auto) and a non-default placement.
- Corpus: save `--report --diff` → `reports/2026-09-30_e1_placement_before_after.txt`, review, then `--snapshot`.

**C4. GUI (`gui/app.py`; syntax-check only, no $DISPLAY).**
- New `CollapsibleSection` "Turbopump Placement (3D)" after `sec_tp_config` (:984-990), with the same
  pressure-fed gate.
- Controls:
  - azimuth slider, 0-360°;
  - axial station slider, 0-1, "0 = auto";
  - standoff slider, 0-1 m, "0 = auto";
  - shaft orientation dropdown;
  - read-only label with the resolved placement.
- Write-back in :2003-2035, load in :3132-3158.

**C5. Docs.**
- ASSUMPTIONS Tier 3: update rows :320 and :324; add rows for the placement rule, MANHATTAN_*,
  AUTO_LEG_OBLIQUE_DEG and AUTO_LEG_STALE_*.
- README.
- CLAUDE.md: geometry paragraph and schema 20.
- TURBOPUMP_FLOW.md: the PORTS box gains placement; exhaust angle = φ.
- Roadmap :26: mark E1 partial, with mounts and the clash check deferred.
- Plan copy with a per-commit checklist at `engine_designer/plans/2026-09-30_turbopump_e1_placement.md`.
- Memory: update `project_turbopump_fidelity_roadmap`.

## Risks / expected churn
- **Corpus physics.** No corpus design has a baked plumbing run (`line_loss_computed` is None), so Pc,
  Isp, pump ΔP and pump power must NOT move. If they do, that's a bug.
- **Corpus keys expected to move:**
  - placement, port and frame keys;
  - for open cycles: the default exhaust duct's `plumbing_*` mass and length → dry mass, TWR and cost.
  - The duct's loss is only reported; back pressure comes from `EXHAUST_DUCT_PRESSURE_RATIO`.
- **Outside the corpus:** top-level `RS-29.json` has a connected turbine_exhaust run. Its duct loss
  (and turbine back pressure) will change, and it should show the stale advisory.
- **Not covered by the obstacle envelope:** gimbal sweep, hatbands and plumbing; that's the deferred
  clash check. Long render-scaled assemblies (RD-180, L 3.25 m > x_max) can still reach the bell;
  tangential orientation is the workaround until E3 retires `render_scale`.

## Verification
1. `./verify_all.sh` after every commit. C1 must report the corpus bit-identical.
2. New self-test matrix: 7 layout-corpus engines × φ ∈ {0, 90, 215} × {axial, tangential} ×
   {envelope, casings}. Invariants:
   - no body inside r_env + gap;
   - ports on the drawn flanges, with directions = ±frame axes;
   - Route-to-pump runs land on their ports with every auto leg orthogonal;
   - the legacy identity holds.
3. Review each `--report --diff` before snapshotting: only geometry, mass and derived keys may move.
4. `py_compile` gui/app.py, plus a screenshot under xvfb if the venv allows. Then Cory checks:
   - the sliders;
   - the main 3D view;
   - Shape Lab "Route to pump";
   - loading `RS-29.json`.
5. Push the branch and open a draft PR; it isn't merged until Cory has tested it.
