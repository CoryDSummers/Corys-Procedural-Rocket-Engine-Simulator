# SSME Orientation — Rocketdyne/Boeing Training Presentation (June 1998)

## Identity

Rocketdyne Propulsion & Power (Boeing), *Space Transportation System Training Data — Space
Shuttle Main Engine Orientation* ("Abbreviated SSME Orientation Course" handout), June 1998,
document no. BC98-04. `literature/SSME_PRESENTATION.pdf` (105 PDF pages/leaves, 0-indexed
0-104: leaf 0 cover, leaves 1-4 forward/table-of-contents/list-of-illustrations, leaf 5
acronyms, leaves 6-102 body slides with a printed footer page number 1-98, leaves 103-104
blank/back matter). Every body slide carries a "BOEING PROPRIETARY" watermark and the cover
states "Use this data for training purposes only" — see Caveats for how this note treats
that marking. Tag: `[SSME-Orientation]`.

Cited elsewhere in this reference set below as `[SSME-Orientation p.NN]`, where NN is the
**printed footer page number** (1-98, visible at the bottom of each body slide), not the raw
PDF leaf index — offset is PDF leaf index = printed page + 5 (e.g. printed p.44 = leaf 49).

## Character

A ~1998-vintage internal Rocketdyne/Boeing training slide deck (PowerPoint exported to PDF),
not a peer-reviewed report or a NASA contractor deliverable — it is the closest thing in
`claude_lit` to a manufacturer's own systems-level orientation briefing for a single named,
fully-flight-proven engine (SSME/RS-25, "Block IIA" configuration with the Large-Throat MCC
introduced in the mid-1990s). Unlike every other SSME-touching source already in this
reference set (`[SP-8107]`'s 1973 pre-operational projections, `[Ch12-Materials]`'s later
materials retrospective, `[Wieseneck-J2]`'s pre-hardware 1970s design study, `[Sutton]`'s
textbook-level gimbal/TVC table), this is the one source giving a **complete, internally
consistent, real Block-IIA-hardware station-by-station propellant flow schematic** (pressure/
temperature/flowrate/rpm at every major duct, pump, preburner and turbine, both fuel and
oxidizer sides) at a single named operating point (104.5% RPL = Nominal Power Level, NPL) —
essentially a full engine-cycle mass/energy balance for one real staged-combustion engine,
plus per-component geometry (injector element counts, cooling-channel/tube counts, pump/
turbine stage counts) not previously present in `claude_lit`.

**Extraction scope**: text extraction (`fitz`/PyMuPDf `get_text()`) was clean and complete on
every slide (no zero-length or garbled pages except the two intentionally-blank trailing
leaves) — this deck's body text (paragraph narrative + tabulated "Key Performance Parameters"
callouts) was read in full, all 105 pages. The one page rendered as an image for cross-check
was the "Block IIA SSME Propellant Flow Schematic" (printed p.19, leaf 24) — a dense
diagram whose station labels/values are individually meaningful (pressure/temp/flowrate/rpm
at ~25 points around the flow loop) but whose raw text extraction returns the numbers in
document z-order rather than diagram-spatial order, making station attribution unreliable
from text alone; that one page was re-rendered at 200 dpi and read visually to correctly pair
each number with its labelled station (values below are taken from that visual read and
cross-checked against the separate per-component "Key Performance Parameters" tables that
restate several of the same numbers in unambiguous tabular form). All other diagram-only
slides (component-cutaway line art with callout labels, no numeric content, e.g. the "Typical
SSME – View 1-8" photographs/exploded-parts diagrams, gimbal-bearing/flex-joint assembly
drawings, controller block diagrams, start/shutdown valve-position strip charts whose curves
are drawn as vector art but whose axis numbers extracted cleanly as text) were skimmed for
their axis/label text only, not re-rendered as images, since no additional numeric content
beyond what extracted cleanly as text was expected or found there.

## Key results

### Engine-level operating parameters (largely corroborating existing `[SP-8107]`/`[Sutton]`
citations, but from real Block IIA flight hardware rather than 1973 pre-operational
projections or a pre-hardware design study — genuinely independent confirmation)

`[SSME-Orientation p.4-6]`: SSME is a staged-combustion LOX/LH2 engine. Four named power
levels, all as %RPL: **Minimum Power Level (MPL) 67% = 316,100 lbf**, **Rated Power Level
(RPL) 100% = 470,800 lbf** (vacuum; 376,600 lbf sea level), **Nominal Power Level (NPL) 104.5%
= 491,900 lbf**, **Full Power Level (FPL) 109% = 512,900 lbf** — throttle range stated as
"67 to 109" (%), variable in ~1% (~4,700 lbf) increments. **Terminology note**: this deck's
"FPL" (109%) is the same physical operating point `[SP-8107]`'s tables label "EPL" — a real
naming discrepancy between two Rocketdyne-lineage sources worth flagging if either tag's
109%-point numbers are ever compared side by side.

- **Pc ≈ 3,008 psia at FPL (109%)** `[p.4,6]` — vs. **2,865 psia at NPL (104.5%)** from the
  per-component tables `[p.41,45]` and **2,871 psia** shown at the MCC on the flow schematic
  `[p.19]` (small internal rounding across slides, all self-consistent to within ~0.2%).
- **MR ≈ 6.032 (O/F) nominal** `[p.6]`, matching `[SP-8107]`'s already-cited figure exactly.
- **Expansion ratio 69:1** (nozzle exit/throat) `[p.4,6,49]`; MCC-internal contraction ratio
  is separately given as **2.66:1** and the MCC's own (throat-to-nozzle-attach-flange) area
  ratio as **4.48:1** `[p.45]` — i.e. 69:1 is throat-to-FULL-nozzle-exit, 4.48:1 is only the
  short MCC divergent section up to the nozzle-attach flange, with the bolted-on tubular
  nozzle providing the remaining ~15.4× expansion (69/4.48).
- **Isp ≈ 452 s vacuum** `[p.4,6]` — matches the figure already cited elsewhere in this set.
- **Two-stage combustion efficiency ≈ 99.6%** `[p.6]` — a genuinely new number for this
  reference set (no `c*`-efficiency figure for SSME was previously captured in
  `topics/03-combustion-and-cstar.md`'s survey); stated as a single headline "high
  efficiency" bullet, not broken into a separate preburner-vs-MCC contribution or tied to a
  measured `c*`, so treat as a real but low-precision (2-sig-fig-class) anchor.
- **Dry weight ≈ 7,480 lb** `[p.5,10]` — new to this reference set for SSME (existing
  `topics/13-mass-and-budget.md` cites SSME turbopump-assembly mass, not whole-engine mass).
- **Program cumulative reliability (as of this 1998 edition): >2,660 starts, >832,500 sec
  total hot-fire time** `[p.5]` — a real fleet-experience anchor, not a component-level
  reliability figure; useful only as qualitative "this engine has an enormous flight/test
  heritage" context, not a failure-rate number (see Caveats — no anomaly/failure-history
  content is in this deck at all).
- **Simple, tank-head start** `[p.6]`: "no start tanks, turbine spinners, pyrotechnics,
  pressure ladders, etc." — only propellant head (from vehicle tank pressure) plus spark
  igniters are needed to begin flow and ignition; corroborates the tank-head-start engine
  list already in `topics/15-transients-and-controls.md` (F-1, RL10, SSME).
- **Controller update rate: 50 Hz (every 20 ms)** `[p.90]` — closed-loop control of thrust
  (via MCC pressure vs. a thrust reference, driving the oxidizer preburner oxidizer valve,
  OPOV) and of MR (via a fuel flowmeter, driving the fuel preburner oxidizer valve, FPOV) —
  a real, named closed-loop control architecture with two independent control loops
  (thrust and MR use different, near-independent valves), not previously captured with this
  much loop-architecture detail in `topics/15`.
- **Dual-redundant fail-operate/fail-safe controller architecture** `[p.90,92]`: first
  failure → "fail-operate" mode (normal capability, reduced redundancy); second failure →
  "fail-safe" mode (throttling/MR control suspended, main propellant valves frozen at last
  commanded position, engine pneumatically shut down). A Flight Acceleration Safety Cutoff
  System (FASCOS) independently monitors turbopump-mounted accelerometers and cuts the
  engine off if vibration exceeds a preset amplitude for a preset time — a real, named
  health-monitoring/safety-cutoff mechanism worth a qualitative note in
  `topics/15-transients-and-controls.md` if that file ever covers engine health monitoring,
  though it's system-architecture rather than a physics constant.
- **Real full-engine mass/energy balance at NPL (104.5% RPL)** `[p.19]` (the Block IIA
  Propellant Flow Schematic, visually re-read — see Extraction scope): confirms self-
  consistency of the whole engine cycle — MCC bulk gas temperature ~6,000°F at Pc 2,871
  psia; total propellant flow to the MCC/nozzle ≈ 1,085 lb/sec (of which ≈ 1,085 lb/sec ≈
  73+47+... splits shown for the fuel-side film/coolant/hot-gas legs), consistent with
  F/Isp = 491,900/452 ≈ 1,088 lb/sec — a good independent cross-check that the vacuum-thrust
  and Isp figures above are mutually consistent with the real mass flow. This is the single
  most complete real-engine full-cycle station map in `claude_lit` and could seed a future
  `validate.py` per-station spot-check if ever wanted (not attempted here — out of scope for
  a source note).

### Combustion devices — new geometry not previously in `claude_lit`

`[SSME-Orientation p.28-34, 40-41]` (Fuel Preburner, Oxidizer Preburner, Main Injector):

| Element | Injector dia (in) | Coaxial elements | Baffle-cooling elements | Combustor length (in) | Injector-end P (psia) | Combustion T (°F) | Hot-gas MR (O/F) | Material |
|---|---|---|---|---|---|---|---|---|
| Fuel preburner | 10.43 | 264 | 24 | 4.37 | 4,793 | 1,310 | 0.86 | NARloy-A liner, Inconel 625 faceplate |
| Oxidizer preburner | 7.43 | 120 | 15 | 4.25 | 4,812 | 871 | 0.60 | NARloy-A liner, Inconel 625 faceplate |
| Main injector | 17.74 (face dia) | 600 | — | — | 2,865 (Pc) | — | 6.03 (MCC) | 347 CRES rigimesh faceplates |

All at 104.5% RPL (NPL). Both preburners use "trivane"-style baffles (3 baffles) for
combustion stabilization, cooled by dedicated non-oxygen-carrying injector elements (24 of
264 fuel-PB elements, 15 of 120 ox-PB elements) — a real, named baffle-cooling design detail
not previously present in `topics/14-combustion-stability.md`'s SSME entry (which currently
only notes the main injector's 5-compartment baffle pattern). **Preburner hot-gas MR is
fuel-rich (<1.0), consistent with the 0.2-1.0 GG/preburner-MR range already cited from
`[SP-8081]` in `topics/10-gas-generators.md`** — 0.86 (fuel PB) and 0.60 (ox PB) both sit
inside that band, real corroboration for a staged-combustion (not just GG) engine.

**Main injector element geometry**: 600 coaxial (shear-coaxial, LOX-center-post/fuel-annulus)
elements, each injecting LOX from its center post and hot fuel-rich preburner gas through its
annulus; 42 flow shields bolted to the outer element row for erosion protection; coolant
(cold GH2 that migrated through the double-walled hot gas manifold) enters through a separate
porous rigimesh transpiration-cooled primary/secondary faceplate pair, not through the main
600 elements themselves — a three-fluid-stream injector (LOX + hot preburner gas + cold
transpiration-cooling GH2), a real design pattern worth flagging in
`topics/05-injectors.md`'s SSME/shear-coaxial entry if that file's injector-type survey is
ever extended to include transpiration-cooled faceplates as a distinct sub-feature.

**Ignition**: augmented spark igniter (ASI) system — 6 total spark igniters (2 each in MCC
and both preburners, for redundancy), each a self-contained 26 VDC-in / 10 kV, 50 sparks/sec
unit `[p.78]`. ASI chambers use two impinging streams of oxidizer (heavy, slow, toward
center) and eight tangential fuel streams (light, fast, "whirlpool" around the oxidizer) for
a fuel-rich cooling shroud + positive ignition + mixing `[p.76]`; igniters switch off after
**4.4 seconds** once the ASI flame is self-sustaining, to avoid intermittent blowback
`[p.76]` — a real, quantified spark-duration figure not previously in this reference set
(useful if `engine_designer`'s ignition-system feature ever wants a real spark-igniter
duty-cycle anchor beyond a qualitative "ASI" description).

### Main Combustion Chamber — real cooling-channel count

`[SSME-Orientation p.44-46]`: NARloy-Z liner with **430 milled slots** (vertical, up-pass
single-pass regenerative cooling) closed out by electrodeposited nickel, structural Inconel
718 jacket, JBK-75 cast coolant manifolds. Injector-end diameter 17.74 in, throat area 93.02
in², injector-end-to-throat length 14.7 in, contraction ratio 2.66:1. At NPL: coolant inlet
5,647 psia / -366°F, coolant exit 4,441 psia / +17°F, coolant flowrate 29 lb/sec, **max
hot-gas wall temperature 1,000°F** — the last figure exactly matches the "1000°F (copper)"
gas-side wall-temp figure already cited from `[Wieseneck-J2]` in `topics/06`, now confirmed
against real as-flown Block IIA hardware rather than a 1970s pre-hardware design-point
projection. **430 milled channels is new, real, citable geometry** not previously present
anywhere in `claude_lit`'s SSME coverage (`[Ch12-Materials]`/`[Wieseneck-J2]` describe the
NARloy-Z liner material and design-point heat flux but not the real channel count).

### Nozzle — real tube count and hatband count

`[SSME-Orientation p.48-51]`: **1,080 stainless-steel tubes**, brazed to themselves and to a
structural jacket, single up-pass cooling (fuel from 3 transfer ducts entering at 6 points via
"steerhorns"). **9 hatbands** welded around the jacket for hoop strength. Attach-point area
ratio 4.5:1, exit area ratio 69:1, length (throat-to-exit) 121 in, exit diameter 90.3/94.0 in
(inside/outside). At NPL: inlet pressure 5,624 psia, discharge pressure 5,420 psia, coolant
flowrate 46.6 lb/sec, max hot-gas wall temp 950°F. A Flow Recirculation Inhibitor (FRI) —
braided Nextel 312 sleeve filled with Saffil batting, rated to 2,600°F — prevents recirculating
hot exhaust gas from reaching the MCC/nozzle bellows joint seal. **The 1,080-tube and
9-hatband counts are new, real, citable structural/cooling geometry** — directly relevant to
`hatbands.py`'s structural-band-count model (a real 9-band SSME nozzle is a concrete
plausibility anchor for that module's band-spacing/count output on an SSME-class engine, not
previously available) and to `tube_bundle.py`'s contiguous-swaged-tube count for a real
LOX/H2 staged-combustion nozzle.

### Turbopumps — real stage counts, real per-pump operating-point table

`[SSME-Orientation p.52-71]` gives a complete "Key Performance Parameters" table for all four
turbopumps at NPL (104.5% RPL) — the fullest single-source real-hardware turbopump dataset
for SSME in this reference set (more complete than `[SP-8107]`'s Table I/II/III, which are
1973 pre-operational projections):

| Turbopump | Pump inlet flow (lb/s) | Pump inlet P (psia) | Pump discharge P (psia) | Pump eff. (%) | Turbine flow (lb/s) | Turbine inlet T (°F) | Turbine PR | Turbine eff. (%) | Speed (rpm) | Turbine hp |
|---|---|---|---|---|---|---|---|---|---|---|
| LPOTP (LOX boost) | 935 | 100 | 417 | 67.7 | 187 | -272 | — | 67.7 | 5,050 | 1,614 |
| LPFTP (LH2 boost) | 155 | 30 | 290 | 71.3 | 29 | -17 | 1.30 | 58.0 | 15,400 | 3,330 |
| HPOTP (main impeller / preburner-boost impeller, two rows) | 1,122 / 111 | 380 / 3,910 | 4,045 / 6,970 | 71.8 / 75.8 | 62 | 870 | 1.53 | 74.6 | 22,220 | 22,880 |
| HPFTP | 155 | 250 | 5,950 | 75.0 | 145 | 1,330 | 1.50 | 81.1 | 34,360 | 63,080 |

**These pump/turbine efficiency and PR figures corroborate, but don't exactly match,**
`[SP-8107]`'s already-cited pre-operational SSME row (O₂ 78.1%/H₂ 69.6% pump efficiency,
turbine PR 1.56-1.59, turbine efficiency 72.9-79.0%) — this deck's real Block IIA HPOTP pump
efficiency (71.8-75.8%) runs a few points lower than `[SP-8107]`'s 1973 projection, and HPFTP
turbine efficiency (81.1%) runs a few points higher than `[SP-8107]`'s 79.0% — small,
plausible real-hardware-vs-projection deltas (a few percentage points), not a contradiction,
but worth noting if `validate.py`'s SSME turbopump-efficiency spot-check is ever tightened:
this deck is the more authoritative (real, later, named-hardware) source of the two.

**Total turbine horsepower ≈ 22,880 + 63,080 = 85,960 hp** at NPL across the two high-pressure
turbopumps — for a rough cross-check against `[SP-8107]`'s SSME specific-power figure (50.0/
108.9 hp/lbm already cited in `topics/09`/`topics/13`), 85,960 hp / (555+701 lb, the two
HPTP masses already cited from `[SP-8107]`) ≈ 68-155 hp/lbm depending on which mass row is
used — broadly consistent with, and bracketed by, the existing 50.0-108.9 hp/lbm range,
though this is an approximate cross-check (NPL not FPL/EPL, and this deck gives no HPTP mass
of its own to pair with its own horsepower figures).

**Real pump/turbine architecture** (stage counts, new to this reference set):
- LPOTP: axial-flow inducer-type pump, direct-driven by a **6-stage axial-flow hydraulic
  turbine** powered by LOX tapped from HPOTP discharge (a liquid-driven, not gas-driven,
  turbine — unusual and worth flagging: this is a hydraulic, not a hot-gas, turbine)
  `[p.52]`.
- LPFTP: axial-flow inducer-type pump, direct-driven by a **2-stage axial-flow gas turbine**
  powered by GH2 from the MCC cooling-jacket exit (i.e. driven by regen-heated coolant gas,
  not preburner exhaust) `[p.56]`.
- HPOTP: **double-entry, back-to-back centrifugal main impeller** (split 50/50 flow to both
  ends of the impeller for balanced axial thrust and improved suction performance) plus a
  separate single-entry preburner-oxidizer boost impeller on the same shaft, driven by a
  **3-stage cantilevered turbine** off the oxidizer preburner `[p.60,62]`. Axial thrust
  balance uses self-regulating orifice/balance-cavity pairs (not thrust bearings) reacting
  to impeller axial shift — the bearings react axial load only transiently during spin-up/
  spin-down.
- HPFTP: **3-stage centrifugal pump** with 2 interstage diffusers, driven by a **2-stage
  turbine** off the fuel preburner `[p.68,70]`; a spring-loaded carbon lift-off seal
  prevents LH2 leakage into the turbine end pre-start, lifted by pump discharge pressure once
  running.

None of these stage counts (LPOTP 6-stage hydraulic turbine, LPFTP 2-stage gas turbine, HPOTP
3-stage cantilevered turbine + double-entry main impeller, HPFTP 3-stage centrifugal pump +
2-stage turbine) were previously captured in `topics/09-turbopumps.md`, which currently only
carries SSME's aggregate specific-power/efficiency numbers from `[SP-8107]`, not its real
architecture.

### Gimbal bearing, flex joints, POGO suppression — corroboration + minor new detail

- **Gimbal bearing** `[p.10-11]`: ±12.5° angular capability, real duty cycle **200
  operational cycles to 10.5°, 1,400 nonoperational cycles**, ~11×14 in, ~105 lb,
  6Al-6V-2Sn titanium alloy with Fabroid (PTFE-lined) inserts at the sliding ball-and-socket
  contact surfaces. This corroborates `[Sutton Table 16-2]`'s already-cited SSME gimbal entry
  (±10.5° operational, ±12.5° capability) with the added real duty-cycle-count and
  material/mass detail Sutton's table doesn't carry.
- **Flexible bellows joints** `[p.14-15]`: multi-ply thin-sheet Inconel 718/ARMCO 21-6-9
  bellows with an internal flow liner (prevents flow impingement on the bellows convolutions,
  itself a fatigue/vibration risk) — real operating points e.g. LPO discharge duct 423 psia
  / -294°F / ±13° / 200+1,400 cycles; LPF discharge duct 279 psia / -420°F / ±11.5° /
  200+1,400 cycles. New, minor detail (duct flex-joint design, not core engine physics).
- **POGO suppression** `[p.72-75]`: a 0.6 ft³ hollow metal-sphere accumulator on the LOX
  low-pressure duct, pressurized by GOX (from the HPOTP-driven heat exchanger coil) with a
  helium pre/post-charge — corroborates the pogo-accumulator entry already cited from
  `[SP-8107]` in `topics/09` ("partially gas-filled pogo accumulator... SSME LOX line"),
  now with the real accumulator volume (0.6 ft³) and a described liquid/gas-interface
  control mechanism (an inverted standpipe with six small exit holes) not previously in this
  reference set.

## Design method

Not a sizing/correlation source — no closed-form equations, only real as-flown-hardware
operating-point tables and qualitative system-architecture description. Its value to
`engine_designer` is entirely as (a) a real full-engine-cycle mass/energy-balance anchor for
a LOX/LH2 staged-combustion engine at a named operating point (useful if a future
`validate.py` full-pipeline SSME spot-check is ever extended beyond the existing isolated
component checks), (b) real component geometry (injector element counts, cooling-channel/
tube counts, turbopump stage counts) usable as plausibility anchors the way `[SP-8107]`'s
turbopump-assembly-level numbers already are, and (c) qualitative systems-engineering
patterns (dual-redundant fail-operate/fail-safe controller, closed independent thrust/MR
control loops, tank-head start, FASCOS vibration cutoff) that could inform a future
`topics/15-transients-and-controls.md` health-monitoring/redundancy discussion, though none
of it is a derivable physics constant.

## Section map

(Printed footer page numbers; PDF leaf index = printed page + 5.)

- Forward / Table of Contents / List of Illustrations / Acronyms: p.i-v (leaves 1-5) — read.
- Shuttle Propulsion System (vehicle-level context: SRB/ET/OMS/RCS): p.1-3 — read; mostly
  out of scope for `engine_designer` (SSME-only tool), not carried into Key results above.
- SSME Introduction, Highlights, Typical Throttling Profile: p.4-7 — read in full, most of
  the engine-level headline numbers above.
- Main Propulsion System / SSME Component Location overview diagrams: p.8-9 — skimmed
  (labelled cutaway diagrams, no numeric content beyond component names).
- Gimbal Bearing, Flexible Joints: p.10-15 — read.
- Powerhead, Propellant Flow Analysis (1-3 of 3), Hot Gas Manifold: p.16-25 — read in full,
  including the Block IIA Propellant Flow Schematic (p.19, visually re-rendered — see
  Extraction scope).
- Fuel Preburner, Oxidizer Preburner, Heat Exchanger: p.28-39 — read in full (including the
  per-component "Block IIA Operating Parameters" tables).
- Main Injector, Main Combustion Chamber, Nozzle: p.40-51 — read in full.
- Low-Pressure Oxidizer/Fuel Turbopumps, HPOTP Pump/Turbine/Seals, HPFTP Pump/Turbine:
  p.52-71 — read in full (all four "Key Performance Parameters" tables).
- POGO Accumulator Pressurizing System, POGO Suppression Accumulator: p.72-75 — read.
- ASI Injector/Combustion Chamber, ASI Spark Igniter: p.76-79 — read.
- Control System Interface, Pneumatic Control Assembly, Propellant Valve Hydraulic Actuator,
  Hydraulic Servovalve Operation, Hydraulic Actuator Piston Configuration: p.80-89 — read;
  mostly valve-actuation mechanism description, no physics constants for `engine_designer`.
- Controller, Controller Functional Organization: p.90-93 — read in full (controller update
  rate, redundancy architecture, FASCOS).
- Engine Valve Sequence at Start / at Shutdown (strip-chart diagrams): p.94-95 — skimmed;
  axis labels (0-100% valve position, 0-7 sec) extracted as text but the curve SHAPES
  themselves are vector art not independently digitized — no numeric sequencing data beyond
  axis ranges was captured (see Caveats).
- Typical SSME – View 7, View 8 (labelled cutaway photos): p.96-97 — skimmed, no new
  numeric content.
- Trailing blank pages (p.98 onward, incl. a Table-of-Contents-listed but absent "SSME
  Complete Fluid Schematic" at p.99): leaves 103-104 — confirmed blank/absent in this PDF;
  not chased further (the TOC lists it but this particular PDF export appears to end before
  that slide).

## Caveats

- **"BOEING PROPRIETARY" / "Use this data for training purposes only" marking** — this is
  vendor training material, not a published report; per this project's existing convention
  for vendored/restricted reference material (the same treatment `UPSTREAM_REPOS.md` applies
  to the CC BY-NC-ND-licensed `upstream/ROEngines`), this note reports only DERIVED facts and
  numbers, never reproduces slide prose verbatim at length, and the source PDF itself is
  reference/study material only — never to be redistributed.
- **No failure/anomaly/mishap-history content at all** — despite being a 1998-vintage
  training deck (well after several well-documented real SSME hardware issues, e.g. HPFTP
  turbine-blade cracking, HPOTP bearing wear, addressed by the Block I/II/IIA upgrade
  sequence this very deck's "Block IIA" labeling implies), this orientation course is
  purely descriptive of the CURRENT (Block IIA) as-designed hardware and control
  architecture — it contains no discussion of prior failure modes, root causes, or
  design-iteration history. Unlike `[TN-Dump]`'s F-1 turbine-exhaust detonation finding
  already cited in `topics/07-dump-cooling.md`, there is no comparable safety-lesson data
  point anywhere in this source.
- **Single named operating point for most tables (104.5% RPL / NPL)**, not FPL (109%) or MPL
  (67%) — the engine-level headline numbers (thrust levels, Pc, expansion ratio, Isp) are
  given at multiple power levels, but essentially all of the per-component "Key Performance
  Parameters" tables (preburners, main injector, MCC, nozzle, all four turbopumps) are given
  ONLY at NPL. No off-design (throttled, MPL/67%) component-level data is present in this
  deck — if a throttle-range component-level study is ever wanted, this source can't supply
  it (see `[Casiano-Throttling]`/`[throttling-review-casiano.md]` already in this reference
  set for that instead).
- **"FPL" (this source) vs. "EPL" (`[SP-8107]`) naming inconsistency** for the 109% power
  point — both appear to refer to the same physical operating condition (real SSME 109%
  rated thrust level), but the terminology differs across sources; flagged above, not
  resolved (no direct evidence either source is wrong, just inconsistent Rocketdyne-lineage
  naming across a 25-year gap between the two documents).
- **The Propellant Flow Schematic (p.19) numbers were read from a re-rendered image**, not
  from raw text extraction, specifically because raw extraction returns diagram-label text
  in an order that does not preserve the diagram's spatial station-to-value pairing; the
  visual read paired each number with its nearest arrow/label by inspection and was
  cross-checked against the separately-tabulated per-component Key Performance Parameters
  pages wherever the same station appears in both (e.g. MCC Pc, preburner flow rates,
  turbopump inlet/discharge pressures) — no discrepancy was found between the two
  presentations of shared values, giving reasonable confidence in the schematic reading, but
  a handful of schematic-only values (e.g. the LPOTP/LPFTP-side duct flow splits not
  independently tabulated elsewhere) rest on that single visual read alone.
- **Total turbine-horsepower-to-specific-power cross-check above is approximate** — this
  deck gives NPL turbine horsepower but no turbopump-assembly MASS of its own; the
  cross-check against `[SP-8107]`'s SSME specific-power figure necessarily mixes a real NPL
  horsepower number from this source with a 1973 pre-operational mass estimate from a
  different source, so the resulting hp/lbm range (68-155) is a plausibility bound, not a
  precision figure.
- **No injector orifice diameters, cooling-channel cross-section dimensions (width/depth/
  land), or coolant velocity data** — the real 430 MCC channels and 1,080 nozzle tubes are
  COUNTS only; this source gives no per-channel geometry, so it cannot directly feed
  `cooling.py`'s channel-width/aspect-ratio sizing model, only serve as a real-count
  plausibility anchor for whatever channel count `engine_designer` derives for an SSME-class
  design.
- **Engine Valve Sequence at Start/Shutdown strip charts (p.94-95) are vector-art curves**,
  not extracted as numeric data — only the axis ranges (0-7 sec, 0-100% valve position, and
  for shutdown "Typical Shutdown from 67% Power Level") were captured; the actual valve-
  position-vs-time curve shapes for MFV/MOV/CCV/FPOV/OPOV during start/shutdown were not
  digitized and are not available from this note.
