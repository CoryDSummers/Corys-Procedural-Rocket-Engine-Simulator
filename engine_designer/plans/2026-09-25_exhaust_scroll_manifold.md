# Planned changes: turbine-exhaust scroll manifold (2026-09-25)

A committed copy of the approved plan so a later session can resume it. **Tick each box when
its commit lands** (with the commit hash).
Branch: `claude/friendly-rubin-un6ueo`, continuing after 368bb77 (schema 14). The plan text
below says "schema 11"; the branch had moved on to 14 by the time it was approved, so the
migration lands as **schema 15**.

## Status
- [ ] Commit 0: this document
- [ ] Commit 1: scroll torus + tangential duct entry (manifold/turbine_exhaust/plumbing, schema 15, scroll mesh, validate row (k), corpus report)
- [ ] Commit 2: outlet neck + flame shield (geometry, mass, drawing, corpus report)
- [ ] Commit 3: omega-joint bands (cosmetic)
- [ ] Commit 4: docs (ASSUMPTIONS, CLAUDE.md, README, claude_lit, OPEN_QUESTIONS)

## Context
Cory asked for a closer look at the shape of the nozzle-injection exhaust manifold, using photos of the J-2
(Science Museum 1977-0402) and the F-1. Sources checked:
- the J-2 photo;
- the F-1 thrust-chamber photo and the F-1 manifold cutaway, both from enginehistory.org RPE 8.12;
- the cutaway matches the [SP-8120 §2.2.5.3] text: flame shield, retaining-band interference, omega joint;
- [F1-Man §1-18]: "torus of decreasing (from inlet to exit) cross-sectional area … 15 omega expansion
  joints … splitter plates at the inlet and flow vanes at the exit".

**What the real hardware shows:**
- **Single tangential inlet, flow one way round (a scroll).** On the F-1 the heat-exchanger duct drops down
  the chamber side, turns through a large elbow and runs *tangentially* into the torus. The torus then
  shrinks steadily round the engine. The J-2 has the same layout: the duct comes down through a bellows,
  then an elbow, then a tangential entry.
- **Inlet bore = duct bore.** The F-1 manifold end of the heat exchanger is 24 in [F1-Man §1-72].
- **The torus sits outboard and slightly forward.** It feeds aft-inboard through a short **neck** into the
  gap between the extension's walls. A **flame shield** runs forward over the tubes. The J-2 torus sits on a
  flat base ring.
- **15 raised omega expansion joints** are visible on the F-1 torus.

**What the tool does now:**
- `turbine_exhaust.size_hardware` builds the injection torus with `manifold._assemble(split=True)`. That
  is a **T-split header**: each half is sized on *half* the flow and tapers symmetrically to 180° at
  `INJECTION_MANIFOLD_TAPER_BLEND` 0.5.
- The inlet bore is therefore the duct bore ÷ √2: about 17 in on the corpus F-1, against the real 24 in.
- The duct joins **radially** (`plumbing.root_frame`, poloidal 0).
- There is no neck, flame shield or joints.

**Cory's decisions:**
- Scope: all four items (scroll, tangential entry, neck and flame shield, omega bands).
- Taper law: **constant velocity**, meaning the area follows the flow still left in the torus.

**Scale (CLAUDE.md token rule):**
- about 12 files, 5 commits (plan doc, 3 code, docs);
- corpus F-1 and J-2 goldens move (mass and envelope only; Isp and film physics unchanged);
- schema 10 → 11.

Approving this plan is the y/n.

## Commit 0: planned-changes document
`engine_designer/plans/2026-09-25_exhaust_scroll_manifold.md`: this plan plus a per-commit checklist.
Commit and push it before any code.

## Commit 1: scroll torus + tangential entry (physics + drawing, which are coupled)
**`physics/manifold.py`: a scroll ring kind next to the split header.**
- `scroll_area_fraction(phi_along_flow_deg, blend)` = `max(1 − blend·φ/360, MANIFOLD_TAPER_MIN_AREA_FRACTION)`.
  The 0.15 floor is reached at about 306°.
- `_assemble(..., kind="scroll", scroll_dir=±1)`:
  - sized on the **full** mdot at the inlet;
  - `inner_diameter_m` = the inlet bore (no √2);
  - `attach_direction_xyz` = the ring tangent, pointing against the flow;
  - `min_flow_radius_m` taken at the tail;
  - new fields `ring_kind` and `scroll_dir`.
- `ring_flow_radius_at` / `ring_outer_radius_at` / `tapered_ring_mass_kg` dispatch on `ring_kind`.
  Split and collar rings stay bit-identical.
- Self-tests: taper is monotonic along the flow; inlet bore = full-flow bore; mass at blend 0 = the
  closed-form full ring; the tail sits at the floor.

**`physics/turbine_exhaust.py`:**
- The injection torus becomes a scroll at `EXHAUST_SCROLL_TAPER_BLEND = 1.0` (constant velocity, Cory's
  call). It replaces `INJECTION_MANIFOLD_TAPER_BLEND` 0.5.
- New `EXHAUST_SCROLL_DIR = +1`, a fixed handedness (Tier 3).
- The inlet angle follows the duct run's attach angle, so the fat end is always where the duct lands.

**`physics/plumbing.py`:**
- `PlumbingRun.root_mode`: "auto" | "surface" | "tangential".
  - "auto" means tangential on a scroll hook and surface everywhere else.
  - A tangential root starts at the scroll's inlet face and leaves along −tangent, so no reducer is needed.
  - Round-trips through `run_to_dict` / `run_from_dict`.
- `seed_route_to_port` for a scroll hook builds a tangent leg (about 1.5 × dia), a 90° elbow pitched
  forward, then an axial leg to the standoff station; the existing auto legs close onto the port. That is
  the F-1 photo's route. It picks the inlet angle so the elbow lands at the port-standoff angle
  (θ0 = θ_S + atan(L/R_c)).
- `run_pressure_loss_pa`: `SCROLL_ENTRY_K = 0.0` for a tangential root. Continuous flow at the scroll's
  design velocity means no Borda-Carnot split dump (Tier 3). Surface roots keep `RING_ENTRY_K` 1.0.
- Self-tests: tangential root direction ⟂ radial, run leaves along −t, entry loss 0, dict round-trip.

**Schema 11 (`design/engine.py`, `gui/project_io.py`):**
- A **baked** `turbine_exhaust` run in a file older than 11 gets `root_mode="surface"`, so its drawn radial
  T is kept. This covers Cory's uncommitted `RS-29.json`, which is never edited; the migration happens on
  load only.
- A warn-only checklist row: "radial T into a tangential scroll: *Route to pump* re-seeds a tangential
  entry".

**Drawing:**
- `gui/preview3d_gl_core/mesh_primitives.py`: new `scroll_manifold_mesh(x0, center_r[], tube_r[],
  u_start, u_span, …)`. It is an open arc swept round the engine axis with a capped tail (reusing
  `_tube_end_disk`); the inlet face is left open for the duct. Self-test: watertight apart from the inlet
  rim, and normals point outward.
- `gui/mesh_builder.py`:
  - `ring_mesh_for` dispatches on `ring_kind`.
  - `turbine_exhaust_termination_pieces` uses `angle_deg` for the scroll's inlet, as the overboard nozzle
    already does.
  - The Flow-view ring loop runs one way, 0 → 360° from the inlet, for a scroll.
- The Shape Lab gets this for free through `exhaust_termination_fn`.
- `gui/shape_lab.py`: a "Tangential inlet" checkbox (sets `root_mode`) for scroll hosts. Syntax check only.

**Validate:** new turbine-exhaust row (k), inside the existing banner so the count stays 27. The corpus
F-1 scroll inlet bore is checked against the real 24 in [F1-Man §1-72]; expected about 24.3 in, +1 %.

**Corpus:**
- `--report --diff` saved to `reports/2026-09-2x_exhaust_scroll_manifold_before_after.txt`, then
  `--snapshot`.
- Expect F-1 and J-2 manifold mass and duct-length changes only.

## Commit 2: outlet neck + flame shield (geometry + mass + drawing)
**`turbine_exhaust.size_hardware` (nozzle_injection):**
- The torus centre moves **forward** of the injection station and **outboard** of the wall by constants
  read off the cutaway (`NECK_AXIAL_OFFSET_TUBE_R_MULT`, `NECK_RADIAL_GAP_TUBE_R_MULT`, Tier 3 "drawing-read").
- The neck is an annular passage from the torus's aft-inboard quadrant to the wall at `inject_eps`. Its
  width is `NECK_WIDTH_TUBE_DIA_FRAC` × the inlet tube diameter. It has two walls, sheet gauge from
  `_sheet_t` at the turbine outlet pressure.
- The flame shield is one sheet from the torus's forward-inboard tangent onto the wall, over
  `FLAME_SHIELD_LENGTH_TUBE_R_MULT` × the tube radius, at `EXHAUST_SHEET_MIN_GAUGE_M`. Haynes 230 as today.
- The same construction stands in for the J-2 base ring.
- Returned as `manifold["neck"]` (section polylines + mass) and added to `mass_kg`.
- The injection station, gas-film slot and all performance are **unchanged**.

**Drawing:** `mesh_builder` draws the neck and shield as `revolve_closed_section` pieces (an existing
primitive), role "exhaust".

**Self-test and corpus:** neck mass > 0 and it ends on the wall at `inject_eps`. Report saved, then
snapshot.

## Commit 3: omega-joint bands (cosmetic)
- `turbine_exhaust.OMEGA_JOINT_SPACING_M` is reverse-solved so the corpus F-1 torus gets exactly 15 joints
  [F1-Man §1-18]. Count = `max(4, round(circumference / spacing))`. Tier 2 for the F-1 anchor, Tier 3 for
  scaling by circumference. The count is stored on the hardware dict; no mass.
- `mesh_builder` draws each joint as a short raised band (1.06 × the local tube radius, 0.12 × the local
  diameter wide) via `scroll_manifold_mesh` over a small arc.
- Self-test: corpus F-1 gives 15.
- No corpus change (golden check stays bit-identical, since the count is informational). If it isn't,
  snapshot with a note.

## Commit 4: docs
- `ASSUMPTIONS.md` rows:
  - scroll law and handedness;
  - `SCROLL_ENTRY_K`;
  - neck / flame-shield constants (drawing-read);
  - omega spacing;
  - `INJECTION_MANIFOLD_TAPER_BLEND` marked retired.
- `CLAUDE.md` turbine_exhaust sentence (scroll, tangential root, neck, schema 11).
- `README`.
- `claude_lit`: note the J-2 photo, the F-1 photo and the cutaway (URLs) in `topics/12b` and the F-1
  source note.
- `OPEN_QUESTIONS`: splitter plates / exit vanes not modelled; real scroll area law still wanted.
- Tick the plan checklist.

## Verification
- `./verify_all.sh` all PASS after each commit, and `validate | grep -c '^ALL'` = 27.
- Self-tests: manifold, plumbing, turbine_exhaust, `preview3d_gl_core`, `mesh_builder`,
  `shape_lab_geometry`, and `project_io` (a v10 file with a baked exhaust run migrates to surface root).
- Corpus: only F-1 and J-2 move in commits 1 and 2, reports saved; `run_corpus --check` passes after
  each snapshot.
- If `xvfb-run` + PyOpenGL are available locally, render F-1 and J-2 previews to PNG for a before/after
  look. Otherwise the GUI is syntax-checked only, and Cory checks the scroll, elbow route, neck, bands and
  the Lab checkbox.
