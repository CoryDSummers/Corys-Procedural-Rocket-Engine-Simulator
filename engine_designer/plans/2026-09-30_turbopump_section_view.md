# Turbopump Section tab (2026-09-30)

Branch `turbopump/section-view` off main, with a draft PR (not merged until Cory has clicked through it).

## Context
Cory asked how hard it would be to draw a cross-section of the designed turbopump in the style
of the Rocketdyne F-1 Mk-10 section (enginehistory.org RPE08.11 `TurbopumpXC.jpg`). That
drawing is a full-assembly cut through the shaft: hatched metal, volutes cut top and bottom at
different sizes, bearings, seals, a two-row turbine with its inlet torus, and leader labels.

The assessment was a moderate, GUI-only round:
- the E2a layout (`physics/turbopump_layout.py`) already holds every casing outline, scroll,
  torus and housing at true scale;
- the pump meanline holds the impeller, inducer and axial-row geometry.

What's missing (wall thickness E3, bearings Round 3, turbine meanline Round 3) is drawn as
labelled drawing-only placeholders.

## Checklist
- [x] C1 `physics/turbopump_layout.py`:
  - `shaft_bearing()` gives the torsion shaft, with the bearing bore recovered exactly from the
    sizing's DN and the OD from `BEARING_OD_BORE_MULT` 1.55.
  - Pump bearing housings are at least that OD. Before, the F-1's housing was narrower than its
    own shaft.
  - Per-component `stations` let the drawing place internals on the layout's own numbers.
  - Self-test: the bearing fits its housing.
  - Corpus bit-identical.
- [x] C2 `gui/turbopump_section.py` (pure-numpy `section_geometry` + Agg `draw_turbopump_section`):
  - Hatched casing bands from the revolved outlines, left open under scroll mouths and lifted to
    the shaft at open end walls.
  - Scrolls cut at u=0 (top) and u=pi (bottom: the discharge end).
  - Inlet flange and eye ring; meanline impeller hub disk / shroud / blade passage per stage,
    with crossover diaphragms.
  - Inducer and nose; axial rows and drum.
  - Seal plate, journal, bearing races and balls, carrier.
  - Labyrinth seals in the links; a stepped torsion shaft.
  - Turbine torus, GG stub, nozzle duct, and disks/rows by staging.
  - Motor stator, rotor and windings.
  - Two-tier leader labels sized in the axes' own data units; scale bar; caption with summary
    and honesty notes.
  - Self-test on 9 corpus cases (single shaft, dual, geared, motor, axial, correlation, casings
    mode); in `verify_all.sh`.
- [x] C3 `gui/app.py`: "Turbopump Section" tab with lazy redraw and the matplotlib navigation
  toolbar (zoom / pan / save PNG-SVG-PDF). Syntax/import-checked only - no `$DISPLAY` here.
- [x] C4 docs: ASSUMPTIONS rows (bearing OD; section proportions), README, CLAUDE.md, a roadmap
  line, and this plan.

## Not done (deliberately)
- Cored casting cavities, ribs, curvic couplings, bolt detail: no model behind them.
- An F-1-like end-mounted-turbine arrangement (ox-fuel-turbine). Our single-shaft order is
  fuel | turbine | ox; this would be a separate layout/port change.

## Verification
- `./verify_all.sh` all PASS; the corpus is bit-identical.
- Headless PNGs (`TURBOPUMP_SECTION_PNG_DIR=... python3 -m engine_designer.gui.turbopump_section`)
  reviewed for the F-1 (full and zoomed pump), J-2, RS-25 and Rutherford.
- Cory runs the GUI tab and reports back.
