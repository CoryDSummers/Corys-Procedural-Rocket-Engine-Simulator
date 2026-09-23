# Marquardt NAS 7-103 — Thrust Chamber Cooling Techniques for Spacecraft Engines

## Identity

The Marquardt Corporation, *Thrust Chamber Cooling Techniques for Spacecraft Engines*,
Final Report, Volume I: Evaluation Procedure and Analyses, 15 July 1963. NASA Contract
NAS 7-103, Project 278, Report 5981. `literature/Marquardt Report 5981 - Thrust Chamber Cooling Techniques for Spacecraft Engines Vol I.pdf` (NTRS 19630011163; 116 PDF leaves, no
offset — this document's own printed page numbers track the PDF leaf index with a fixed
+9 shift: PDF leaf N = printed page N-9, e.g. printed p.1 "SUMMARY" is PDF leaf 10).
Tag: `[Marquardt-5981]`.

Note: `literature/duplicates/19710019929.pdf`, also added alongside this file, is a byte-identical
duplicate of `[Huzel]` (already covered by `sources/huzel-huang-sp125.md`) — confirmed via
`md5sum`, nothing new extracted from it.

## Character

A cooling-*method-selection* report, not a single-technique deep-dive like `[TN-Dump]`
(dump cooling) or a structural-criteria monograph like `[SP-8120]` (nozzle structure). Its
purpose is explicitly comparative: given a spacecraft mission's thrust/run-time/restart/
envelope requirements, screen all six thrust-chamber cooling techniques (regenerative, open
tube/dump, radiation, ablative, film, transpiration, plus heat sink) against each other and
pick the lightest/most applicable one — largely via a set of graphical (non-OCR-readable)
weight-estimation curves plus four worked design-study examples.

**Scope is small-to-medium spacecraft engines, not large boosters**: the design studies
span thrust levels of 20–10,000 lbf and chamber pressures mostly under ~300 psia (one
example runs a chamber pressure up to 1000 psia at Ae/At=800 as a hypothetical trade study,
but the four worked examples are all deep-space/orbital-maneuvering engines: earth-storable
hydrazine+N₂O₄ midcourse engines, an O₂/H₂ constant-thrust study, a Mars/Venus OF₂/B₂H₆
braking engine). Treat findings here as most trustworthy for **RCS/upper-stage/deep-space
engine scale**, not F-1/J-2/SSME-class boosters — cross-check against `[Huzel]`/`[Sutton]`/
`[SP-8120]` before applying to a large engine.

Structure: §I Summary, §II Introduction, §III Procedure Summary, §IV Propulsion System
Specification, **§V General Applicability Characteristics of Cooling Methods (printed p.9–22,
leaf 18–31)** — the core cooling-method-selection content, **§VI Preliminary Thrust Chamber
Weight Analysis (printed p.23–29, leaf 32–38)** — the parametric weight-curve method,
§VII Propulsion Performance Penalties (printed p.27–29, leaf 36–38), **§VIII Design Studies
(printed p.30–42, leaf 39–51)** — four fully worked examples, §IX References. Figures
(mostly graphs, printed p.46–92, leaf 55–101) are referenced throughout the text but are
**not numerically extractable by OCR** — axis labels and captions are legible, plotted curve
values are not.

## This note's extraction scope

Read in full: §V (General Applicability, leaf 18–31, all six cooling methods' feasibility
and operational limitations) and §VI-A/B (Preliminary Weight Analysis method and the
regen-cooled-chamber weight-curve breakdown, leaf 32–35) and §VIII Design Study 1 in full
(the earth-storable deep-space engine, leaf 39–45, the source of the concrete regen-cooling
numbers below) plus Design Study 2's discussion/conclusion (leaf 46–47). Design Studies 3
and 4 (leaf 47–51) were skimmed for their conclusions only. §VII (performance penalties) was
skimmed. Figure captions in the weight-curve section (leaf 80–88, fuel-manifold and
coolant-in-jacket weight curves) were read for their stated assumptions (material densities,
wall thicknesses) since the plotted curves themselves are not OCR-readable. §I–IV and §IX
were not deep-read (front matter / references).

## Key results — Cooling-method selection (§V)

**Regenerative cooling's three named limiting factors** `[Marquardt-5981 §V-B-1a p.12]`:
(1) coolant supply pressure requirement, (2) minimum practical coolant-passage dimension,
(3) maximum coolant temperature rise — expressed either as a maximum coolable nozzle
expansion ratio, or (for hydrogen specifically) as a percentage of a maximum allowable
enthalpy rise. A **feasibility map (Fig. 5)** plots these limits vs. chamber pressure and
thrust level for four propellant pairs (N₂O₄/N₂H₄, O₂/H₂, F₂/H₂, N₂O₄/Aerozine-50) — the
plotted boundaries themselves aren't OCR-legible, but the text states earth-storable
propellants below **250 psia** chamber pressure can use regenerative, radiative, *or*
ablative cooling; above that, or for long run times, film/transpiration become necessary.
For convective (regen) hydrogen cooling, all feasibility-map points assumed a **2000°R wall
surface temperature** as "a realistic level for currently developed rocket engine
construction materials" (1963-era assumption — cross-check against `[Ch12-Materials]`
before reusing as a modern material limit).

**Regenerative-cooling operational notes** `[Marquardt-5981 §V-B-1b p.12-13]`:
- **Restart**: no fundamental limitation beyond sequencing complexity.
- **Pulse/response**: poor response without a valve between coolant passages and injector;
  suitable for ΔV burns, not attitude-control/station-keeping pulsing.
- **Purging**: coolant jacket volume should be gas-purged after each operating cycle —
  three reasons given: slow jacket drain by evaporation, possible sporadic hypergolic
  reignition from residual coolant, and coolant freezing (space environment) blocking flow
  passages. This is a **plumbing-design constraint** directly relevant to jacket/manifold
  design: a regen-cooled engine intended for restart needs a purge path designed in, not
  bolted on later.
- **Throttling**: throttling ratio is limited by regen cooling and constrains the cooling
  envelope of applicability (quantified below in the Design Study 1 numbers).
- **Propellant/coolant ranking**: "**Hydrogen is the best coolant, followed by N₂H₄ and
  Aerozine-50 in that order.** Not much is known concerning diborane; pentaborane has only
  limited cooling potential."
- **Meteoroid tolerance** (space-environment-specific, not relevant to atmospheric/KSP
  engines but a striking real reliability data point): "Regenerative cooled chambers have
  been known to operate, without catastrophic results, with as much as **10 percent of the
  coolant passages containing holes**." External leaks in atmosphere are more serious.
- **Exterior wall temperature**: below 400°F for storable-liquid-cooled jackets, but can
  exceed 1000°F for hydrogen-cooled jackets (consistent with H₂'s much higher allowable
  bulk-temperature rise before the coolant itself becomes a materials problem).

**Open-tube (dump) cooling** `[Marquardt-5981 §V-B-2 p.14-15]`: explicitly gated on regen
feasibility — "a chamber that cannot be cooled with the total fuel flow by regenerative
methods cannot be cooled by a fraction of the fuel by dump procedures. Therefore, dump
cooling is limited to those areas wherein regenerative cooling is relatively easy" (high
thrust or low chamber pressure, where H₂ heat capacity isn't the limiting resource). Cites
"most investigators" using **~2% of total propellant flow** as the dump fraction, which at
O₂/H₂ MR=5:1 is a **12% increase in total hydrogen flow** — this is the same order of
magnitude as `[TN-Dump]`'s own dump-fraction treatment already in `topics/07-dump-cooling.md`,
corroborating rather than superseding it. Much faster restart/pulse response than regen
(lower coolant thermal mass); limited to thrust >10,000 lbf in general practice per this
source (a looser floor than the O₂/H₂-specific framing already in `[TN-Dump]`).

**Cross-method regime summary from Design Study 2** `[Marquardt-5981 §VIII-A-2 p.37-38]`,
an O₂/H₂ constant-thrust weight study spanning 20–10,000 lbf and 3–1000 s burn time:
**"Radiation cooling — low thrust, long run times. Ablative cooling — low thrust, run times
10 to 300 seconds. Regenerative cooling — high thrust, medium to long run times. Heat sink —
short run times."** — a compact rule-of-thumb regime map, consistent with (and a useful
plain-language restatement of) the more quantitative Fig. 5 feasibility map.

## Key results — Real regen-cooling design numbers (Design Study 1, earth-storable N₂H₄+EDA/N₂O₄ engine)

This worked example (500–2000 lbf thrust, N₂H₄+10% EDA fuel / N₂O₄ oxidizer, 40:1
expansion, deep-space midcourse engine) is the one place in this report where **concrete
regen-cooling numbers appear directly in text** (not buried in an unreadable graph)
`[Marquardt-5981 §VIII-A-1 p.34]`:

- **Minimum practical coolant passage dimension: 0.062 inch** (cited from the report's
  Volume II §III-A, not reproduced here — this is the only concrete minimum-passage-size
  figure anywhere in this note's extraction scope).
- **Allowable chamber-pressure range for 4:1 throttling**, at this minimum passage size:
  - F = 500 lbf: Pc_max = 60 psia, Pc_min = 30 psia
  - F = 2000 lbf: Pc_max = 240 psia, Pc_min = 120 psia

  i.e. for this propellant/thrust class, the *regen-coolable* Pc range scales roughly
  linearly with thrust at a fixed passage-size floor, and the throttle ratio (max/min = 4:1
  in both cases) is itself a *cooling*-imposed limit, not a combustion/injector one — a
  useful independent data point for anyone reasoning about `engine_designer`'s throttling
  feasibility relative to jacket geometry.
- **Cooled expansion ratio limited to Ae/At=10:1** for this engine class, with a
  radiation-cooled refractory-metal skirt assumed from 10:1 to 40:1 — i.e. **combined
  regen+radiation cooling past a material-driven cutoff eps**, the same architectural pattern
  as `EngineDesign.regen_nozzle_end_eps` already implements in `design.py`, corroborating
  that design pattern's real-hardware precedent (though for a much smaller/lower-Pc engine
  than the ones `[SP-8120]`/`[Huzel]` examples are drawn from).
- **Propellant supply pressure implied by fixed-orifice injectors**: Pc=60 psi → Psup=95
  psia; Pc=240 psi → Psup=700 psia (a large supply-pressure swing across the throttle range
  with fixed-area injectors — the report notes a variable-area injector could reduce this).
- Weight breakdown for this design explicitly itemizes **chamber reinforcement + cooling
  passages + manifolds + fuel held in cooling passages and manifolds** as the four
  mass-accounting buckets for a regen-cooled chamber — i.e. this source treats "manifold" as
  a **mass-budget line item**, not a hydraulic/structural design object like `[SP-8120]`'s
  vanes/splitters/dams/structural-supports treatment. Anyone wanting manifold *design*
  guidance (weld quality, flow distribution, structural support failure modes) should use
  `[SP-8120] §2.2.5.2` instead; this source only tells you a manifold has non-negligible
  mass and holds coolant that also has mass.

## Key results — Weight-model assumptions (§VI, figure captions)

The parametric weight-curve method (11 graphs, summed and multiplied by throat area to get
total mass — the same "sum of itemized component masses" spirit as `mass_model.py`, but via
un-digitizable 1963 hand-drawn graphs rather than closed-form terms) assumes, per its stated
inputs and figure captions:

- Regen-cooled chamber material: **Type 321 stainless steel** (density/strength baseline for
  all regen weight curves) `[Marquardt-5981 §VI-B p.24]`.
- Regen coolant-passage wall thickness: **0.010 inch** (Fig. 26/27 caption).
- Radiation-cooled columbium nozzle extension: **0.020 inch, 0.320 lb/in³** density
  (Fig. 27 caption) — consistent with columbium's real density (~0.310 lb/in³), corroborating
  this as a genuine material property rather than an arbitrary weight-study placeholder.
- Coolant density assumptions for jacket-volume weight curves (Fig. 31): **Aerozine-50 =
  56 pcf, Hydrazine = 61 pcf, Hydrogen = 0.1 pcf** — the very low hydrogen figure reflects
  hydrogen at jacket operating conditions (heated, low-density gas/supercritical fluid by the
  time it fills the hot-side jacket volume), not storage-tank liquid density (~4.4 pcf).
- Claimed accuracy of the overall weight-curve method: **±10-15%**, explicitly *not*
  intended to represent true shelf/flight weight (§VI-B p.24).
- Radiation-cooled-chamber assumptions used elsewhere in the report: wall emissivity 0.72,
  effective shape factor 1.0 in the chamber, minimum wall gage 0.020 in, material selection
  90% Ta–10% W above 2000°F / Haynes 25 below 2000°F, maximum allowable equilibrium wall
  temperature 3300°F (coating life limit, not a melting limit).
- Ablative material assumption: silica-fiber-reinforced phenolic, density 0.0625 lb/in³, char
  rate essentially independent of chamber pressure over 50–500 psia (though throat *erosion*
  rate is pressure-dependent and not separately correlated in this volume).

## Design method (none directly usable — graphical, not closed-form)

Like `[SP-8120]`, this source is **not a source of new closed-form constants** for
`engine_designer/physics/*.py`: its actual sizing method is eleven hand-drawn parametric
graphs (Figures 23–33) that aren't numerically extractable from the OCR'd PDF. What *is*
directly usable are the discrete numbers embedded in the surrounding text and figure
captions (quoted above): the 0.062 in minimum passage dimension, the Pc/throttle-ratio pairs
from Design Study 1, the material-thickness/density assumptions, and the qualitative
cooling-method regime map. Treat all of the above as **corroborating real-hardware context
for a small-engine design regime**, not as inputs to derive a new `mass_model.py` term or a
new cooling feasibility check — the existing `[TN-Dump]`/`[Huzel]`/`[SP-8120]` sources
already cover this ground more usably for the thrust range `engine_designer` typically
targets.

## Section map

- §I Summary: printed p.1 (leaf 10) — not read.
- §II Introduction: printed p.2-4 (leaf 11-13) — skimmed.
- §III Procedure Summary: printed p.5 (leaf 14) — skimmed.
- §IV Propulsion System Specification: printed p.6-8 (leaf 15-17) — skimmed (propellant
  list, mission-requirement checklist).
- **§V General Applicability Characteristics: printed p.9-22 (leaf 18-31) — read in full,
  see Key results above.**
- **§VI-A/B Weight Analysis method + regen weight-curve breakdown: printed p.23-24
  (leaf 32-34) — read in full.**
- §VI-C/D Radiation/Ablative weight-curve assumptions: printed p.25-26 (leaf 34-35) — read
  (assumptions only, not the curves themselves).
- §VII Performance Penalties: printed p.27-29 (leaf 36-38) — skimmed (film-cooling Isp loss
  ≈ percentage of coolant flow; throat-erosion Isp sensitivity; heat/pressure-loss Isp
  penalty).
- **§VIII-A-1 Design Study 1 (earth-storable deep-space engine): printed p.30-35
  (leaf 39-45) — read in full, the source of the concrete regen numbers above.**
- §VIII-A-2 Design Study 2 (O₂/H₂ constant thrust): printed p.36-37 (leaf 46-47) — read
  (conclusion/regime-map only).
- §VIII-A-3/4 Design Studies 3/4 (constant total impulse; Mars/Venus OF₂/B₂H₆ braking
  engine): printed p.38-42 (leaf 47-51) — skimmed, not deep-read.
- §VIII-B Combined Cooling Techniques and Advanced Concepts: printed p.43 (leaf 52) —
  not read.
- §IX References: printed p.44-45 (leaf 53-54) — not read.
- Figures 1-52 (graphs): printed p.46-92 (leaf 55-101) — capions/assumptions read where
  cited above; plotted curve data is not OCR-extractable.
- Table I (mission requirements), Table II (propellant vs. cooling applicability), Appendix
  A (nomenclature): printed p.93-95+ (leaf 102+) — not read.

## Caveats

- **Small-engine/spacecraft scope**: thrust range 20-10,000 lbf, chamber pressures mostly
  under ~300 psia in the worked examples. This is a materially different regime from
  `[Huzel]`/`[Sutton]`/`[SP-8120]`'s large-booster examples (F-1, J-2, H-1) — treat the
  concrete Pc/throttle numbers above as representative of *this* engine class, not a general
  design allowable for arbitrary thrust.
- **Figures are not numerically extractable**: this report's actual design method is
  graphical (11+ parametric curves); OCR captures axis labels and captions but not plotted
  values. Every number in this note came from body text or a figure caption, never from
  reading a curve.
- **1963 vintage**: predates most modern high-performance regen materials (no Inconel 718
  channel-wall, no modern additive-manufactured cooling-channel geometry) — the Type 321
  stainless / columbium / Ta-10W materials named are period-appropriate, not current best
  practice; cross-check against `[Ch12-Materials]` before treating any material choice here
  as current guidance.
- **"Manifold" here means mass, not design**: unlike `[SP-8120]`'s manifold section (vanes,
  splitters, dams, structural supports — a hydraulic/structural design source), this report
  only treats manifolds as a weight-accounting bucket. No hydraulic sizing, pressure-drop, or
  structural-support method for manifolds is given anywhere in this note's extraction scope.
- OCR quality is poor in the same way as other Pdf.Capture-scanned NASA-era reports already
  in `claude_lit/` (concatenated/split words, occasional misrecognized characters) —
  quotations above were reconstructed by eye; technical content is unambiguous but exact
  wording is paraphrase-grade.
