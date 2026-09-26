# 13133-F-1 — Space Shuttle OME Platelet Injector Program, Final Report

## Identity

Aerojet Liquid Rocket Company (A Division of Aerojet-General Corporation), *Space
Shuttle Orbital Maneuvering Engine Platelet Injector Program, Final Report*, Report
13133-F-1, Contract NAS 9-13133, prepared for NASA Lyndon B. Johnson Space Center,
Primary Propulsion Branch, c. 1975 (the report itself is undated on its cover but its
Bibliography's last monthly-progress entry is May 1975 and cites a "1974 WSTF Test
Report" as already issued 1 April 1975).
`literature/13133-F-1 - Space Shuttle OME Platelet Injector Program Final Report.pdf`
(NTRS accession 19770020235; 322 PDF leaves, leaf 0 = cover, leaf 12 = printed "Page 1"
of the Introduction — printed page N ≈ PDF leaf N+11 through the main body; front matter
and later sections drift from this offset and are cited by section/leaf instead where
ambiguous). Tag: `[OME-Platelet]`.

## Character

A real-hardware **development and test program final report** for the platelet-face
injector used on the Space Shuttle Orbital Maneuvering System (OMS) engine — a
pressure-fed, N₂O₄/MMH, ~6000 lbf-class, Pc = 125 psia, MR = 1.65, vacuum-Isp-315-sec
engine. This is the **first source in `claude_lit/` with real platelet-injector
construction detail**: a photoetched, diffusion-bonded stack of thin metal plates
forming both the injection orifices *and* the propellant manifolding in a single
bonded unit — a fourth injector-construction technique alongside the drilled-plate/
impinging, pintle and coax-swirl types already covered in `topics/05-injectors.md`.

The program proceeded through three thrust scales — unielement (6 lbf single-element
screening, 88 hot firings), subscale (600 lbf multi-element, 87 hot firings + 14 cold
flow), and full scale (6000 lbf, 362 firings at ALRC plus separately-reported altitude
testing at NASA/WSTF in 1973-74, not itself included in this report) — each building on
the last. Five basic injector element patterns were tried (X-doublet/XD, unlike-doublet/
UD, splash plate/SP, like-doublet/LD, vortex/VTX — the last never hot-fired), converging
on an **X-doublet with tangential fans (XDT)** as the flight-pattern choice: lower
peak performance than the splash plate but dramatically better combustion-stability
behavior. A distinct integral-baffle platelet injector (3 oxidizer-cooled radial
baffles, platelet stack sectioned into 3 pie slices for bonding) and a non-platelet
EDM-drilled like-doublet injector (built on a separate IR&D program) were also tested
for comparison. The bulk of the full-scale program effort — and of this report — is
combustion-stability troubleshooting (the "resurging" instability unique to the
X-doublet pattern) rather than routine performance characterization.

## This note's extraction scope

Given the document's size (322 leaves), the following passes were made:

**Read in full**: Introduction (leaf 12-14); Summary §II (leaf 15-19, all subsections
A-C); Results and Conclusions §III (leaf 20-27, all subsections A-C incl. fabrication/
performance/heat-transfer/stability/transients/evacuation-purge); Recommendations §IV
(leaf 28-33); Application of Results §V (leaf 34-36); Contributions of OME to OMS §VI
(leaf 37-40) — these six sections are the report's own dense, numbered executive
digest and contain most of the citable real numbers below. Unielement Program §VII
(leaf 41-72, design/patterns/spray-mixing-tests/hot-fire narrative, Table I patterns and
Table II hot-firing log — the latter's numeric columns are OCR-garbled, narrative text
only was usable). Subscale Program §VIII design point and thruster-design-summary
(leaf 84-89, Tables III-IV) and Results §E (leaf 110-127, performance/compatibility/
stability incl. Tables VI-VIII stability-test summaries). Full Scale Testing and
Demonstration Program §IX: Introduction/Facility/Chambers/Cavity Configuration (leaf
129-143), **Injectors §E in full including the platelet-face fabrication description**
(leaf 144-158, 162), Test Series Description §F for Series 1-4 (leaf 168-174, the
resurging-discovery and face-ring-dam-fix narrative). Full Scale Performance §X in full
(leaf 205-227, incl. Table-XII-derived performance-comparison prose, the ERE/energy-
release-efficiency definition, and real nozzle-divergence-efficiency ETAD values). Full
Scale Heat Transfer §XI in full (leaf 253-278). Full Scale Combustion Stability §XII in
full (leaf 282-315, incl. the complete resurging mechanism description). Bibliography
(leaf 317-321, skimmed — monthly-progress-report titles only, no extractable technical
content beyond confirming program chronology).

**Skimmed only** (narrative confirmed consistent with the Results/Conclusions summary
already read, no new extractable numbers found on a keyword pass): Unielement hot-fire
Table II raw data, remainder of Subscale Program §VIII (Objective/Approach, Cold Flow —
leaf 90-109), Test Series Description §F Series 5 onward (leaf 175-204, further stability
troubleshooting sequences — same resurging phenomenon, additional cavity/overlap
permutations already captured in §XII's systematic treatment).

**Not read**: the raw test-by-test performance data appendix (Table XIV, leaf ~228-252 —
individual-test numeric listings, OCR-garbled tabular data, superseded by the narrative
performance comparisons already extracted from §X); Table II (unielement orifice-size
detail) and Table IV (subscale modifications) beyond what's quoted in prose; the bulk of
plotted figures (captions/axis-labels only — plotted curves are not OCR-extractable, the
same limitation noted for every scanned report already in this reference set).

Overall: roughly two-thirds of the document's leaves were read for text content: the
executive-summary sections (§I-VI, ~14% of the document) essentially in their entirety,
the platelet-construction and full-scale-performance/heat-transfer/stability sections
(§IX-XII, the report's technical core) in full, and the earlier unielement/subscale
development sections in a mix of full-read (design/results prose) and skim (raw test
tables).

## Key results — real platelet-injector design/hardware data

**The platelet construction method itself** `[OME-Platelet §IX.E.3, leaf 158]`: "The
injector face consisted of a stack of six plates, varying in thickness from .006 to
.008 in. These platelets were individually photoetched and then bonded together to
form a single platelet stack which was then bonded onto the injector body." Propellant
orifices *and* flow passages are photoetched into or through each platelet before
diffusion bonding — the manifold as well as the injection elements can be built into
the platelet stack itself, even at the smallest (0.650 in dia × 0.150 in thick)
unielement scale `[§VII.B, leaf 42]`. The full-scale XDT pattern comprised **867
elements of the XD-0 (X-doublet) type**; the integral-baffle variant had its platelet
stack **sectioned into three pie slices** for separate bonding onto a baffled body
`[§IX.E.4, leaf 158]`.

**Real, measured benefits of the platelet approach** `[§VI.A, leaf 38-39]`:
- **Cycle life**: 1500 thermal cycles demonstrated twice in subscale testing without
  structural damage.
- **Rework speed**: a pattern could be machined off the face and a completely new
  pattern (from existing photoetch artwork) bonded back on **within three days** — used
  repeatedly in the program (e.g. XDT-2 → XDT-2A after adding face-ring dams, described
  below, "in less than three days" `[§IX.F, leaf 172]`).
- **Baffle compatibility**: platelet fabrication was successfully applied to a
  three-bladed, oxidizer-cooled integral-baffle injector.
- **Fabrication risk**: no significant fabrication problems with the baseline bonding
  procedure; one inadvertent process deviation produced four leaking injectors —
  i.e. the bonding process is real but has a documented failure mode if deviated from.
- **Regen-chamber compatibility**: milled-slot inner liner with an **electroformed
  nickel external wall/jacket** was demonstrated as a fabricable regen-chamber
  construction (used for both the workhorse "A-1" and demonstration "A-2" chambers).

**Injector manifold hydraulics, real layout** `[§IX.E.2, leaf 146]`: oxidizer enters
centrally and is fed radially outward into three "pie" manifolds, then through
"downcomers" into concentric face-ring manifolds; fuel is fed radially inward from a
circumferential manifold, likewise through three pie manifolds and downcomers into the
ring manifolds — a real concentric-ring-manifold-plus-pie-manifold topology for a
platelet-stack injector, distinct in kind from the tapered-torus manifolds this
project's `manifold.py` already models for tube-wall regen engines.

**Real element-pattern design parameters** `[§VIII.B.2, leaf 87]`: each element type
uses a **cant angle** (element centerline rotated off-radial) chosen to maximize spray
overlap between adjacent elements while maintaining a reducing (fuel-rich) atmosphere
along the chamber wall — real optimized cant angles were **25° for splash plate, 30°
for X-doublet, 45° for unlike-doublet**. Injector pressure drop target: **30-35 psid**
at Pc = 125 psia (≈24-28% of Pc) `[§VIII.B.1, leaf 87]` — notably at the high end of, or
slightly above, the generic 15-20%-of-Pc rule already cited from `[Huzel]`/
`[Armstrong-MarsISRU]` in `topics/05-injectors.md`; a real hypergolic-pressure-fed data
point for that design rule's upper bound.

**Real performance data (nominal OMS point: Pc = 125 psia, MR = 1.65, 55:1 vacuum area
ratio, extrapolated from sea-level/altitude test data)** `[§X.C, leaf 222-223]`: eight
of eleven tested injector configurations delivered **313-315 sec** vacuum Isp at a
16-in. chamber length; the mixed-element pattern (60% X-doublet / 40% splash plate)
reached **319-320 sec** (highest of any configuration, but combustion-unstable); the
non-platelet like-doublet comparison injector reached an equivalent **314.7 sec**
(platelet vs. conventional-drilled injectors are performance-equivalent for this
propellant/thrust class). WSTF altitude-test results matched or slightly exceeded the
ALRC sea-level extrapolations for every configuration cross-checked.

**Real energy-release-efficiency (ERE) trends** `[§III.C.2, leaf 12]` `[§X.B, leaf
196-199]`:
- Delivered Isp is monotonically increasing with mixture ratio (1.4-1.9 tested range)
  and with chamber pressure (90-150 psia tested range) — part of the Pc trend is
  reduced nozzle kinetic loss, part is real ERE increase.
- Increasing axial chamber length from 12 to 16 in gave **~+4 sec Isp** across all
  injector types (finite mixing/combustion length, consistent with this reference set's
  other finite-combustion-length findings, e.g. `[TN-Dump]`, `[SECA-HT]`).
- **Fuel film cooling at ~8% of fuel flow costs ~1 sec Isp** with the like-doublet
  injector `[§III.C.2.c, leaf 12]` — a second real hydrocarbon/hypergolic film-cooling
  Isp-tax data point alongside `[TP2862-LOXRP1]`'s zoned-injector LOX/RP-1 number
  already in `topics/06b`.
- Removing the 4-in L* section cost 2-3 sec Isp for either injector type.
- Warming propellant from 40 to 110°F improved Isp by 0.2-1.2 sec.

**Real nozzle divergence efficiency (ETAD) values**, TDK-computed for the actual test
nozzles used `[§X.D, leaf 226]`:

| Nozzle | Area ratio | ETAD |
|---|---|---|
| 15° conical | 2:1 | 0.9840 |
| 15° conical | 2.6:1 | 0.9865 |
| Rao contoured, cut off | 20:1 | 0.9390 |
| OMS flight nozzle | 55:1 | 0.9906 |

(A real illustration that a *low-area-ratio, truncated* Rao bell can have a distinctly
lower divergence efficiency than a full-length high-area-ratio bell — the 20:1 cut-off
contour underperforms even the 2:1 conical here, because it's a truncated section of a
much larger design contour, not a proportionally-scaled small bell.)

**Real heat-flux/thermal data** `[§III.C.3, leaf 12]` `[§XI.B-F, leaf 254-278]`:
- Maximum gas-side regen-chamber wall temperature at the throat: **765°F** at nominal
  conditions with the prototype (XDT) injector; estimated flight-chamber cycle life at
  that condition: **1350 cycles**.
- Gas-side wall temperature sensitivity: **+18°F per 0.1 increase in mixture ratio**,
  **+70°F per 25 psi increase in chamber pressure**. Coolant (fuel) bulk temperature
  rise: **164°F nominal**, **+10°F per 0.1 MR increase**, independent of Pc.
- Burnout safety factor (heat-flux-ratio basis) at flight nominal conditions: **~1.40**
  — with some tested points at calculated safety factor <1.00 surviving without failure,
  i.e. real evidence the analytical method itself carries conservatism margin.
- Typical cylindrical-section gas-side heat flux (uncooled full-scale hardware): **~2.0
  Btu/in²·sec (~3.2 MW/m²)**; a **low-mixture-ratio near-injector zone persisting 5-7
  in downstream** of the face never exceeded **1.1 Btu/in²·sec** with the X-doublet
  pattern (real evidence of the injector's poor near-face mixing, distinct in kind from
  but consistent with `[TN-Dump]`'s finite-combustion-length finding — here the effect
  is element-pattern-dependent rather than universal, since the splash-plate/unlike-
  doublet patterns showed high flux from the forward end instead).
- Injector face flux (calculated from a local 3-D conduction model): **1.5-2.0
  Btu/in²·sec**; measured face temperatures typically **500-750°F** (X-doublet:
  400-700°F; splash plate ran markedly hotter, **800-1000°F locally**, `[§VII.E, leaf
  76]`, `[§VIII.E.2, leaf 112-115]`).
- Acoustic-cavity gas temperature: **800-1400°F with the XDT-1 pattern** vs.
  **1800-2200°F with XDT-2** (outer fuel-element orientation difference); splash-plate
  subscale testing showed cavity temps around **2200°F** vs. **~300°F for X-doublet**
  under comparable conditions — a real, large (order-of-magnitude) cavity-temperature
  sensitivity to injector-element choice at the chamber periphery.
- Integral-baffle heat pickup: measured bulk temperature rise **12°F** (vs. 18°F
  predicted) at steady state; baffle-average flux **~1.5-1.6 Btu/in²·sec**; oxidizer
  coolant pressure drop through the baffle was **115 psid** measured vs. **48 psid**
  predicted — attributed to weld penetration into the flow passages (a real fabrication-
  tolerance-vs.-design-prediction gap for regen-cooled baffles).

**Real combustion-stability data**:
- **Real chamber acoustic mode frequency table** (full-scale, undistorted) `[§XII.A,
  leaf 272]`: 1-L 1400 Hz, 1-T 3100 Hz, 2-T 5200 Hz, 1-R 6500 Hz, 3-T 7100 Hz, 4-T
  9000 Hz, 1-T+1-R 9100 Hz. The baseline dual-tuned acoustic cavity distorts/suppresses
  the 1-T mode to a measured **~2600 Hz**.
- **Real dual-tuned acoustic cavity design**, the flight-adopted baseline `[§III.C.4.a,
  leaf 13]`: eight 1-T cavities (1.5 in deep, 18% of injector face area) + four 3-T
  cavities (0.4 in deep, 9% of face area), circumferential housing. **Stability margin
  of this baseline: 80%** (cavity area 80% greater than the minimum required for stable
  operation) — a real, quantified acoustic-cavity design-margin figure.
- **Injector overlap** (injector-ring radius in excess of chamber radius) tested from
  −0.007 to +0.25 in; increased overlap consistently *improved* stability for both
  tested injectors — a real, load-bearing geometric parameter for face-ring/cavity
  interaction not previously represented in this reference set's combustion-stability
  coverage (`topics/14`).
- **Resurging** — a hybrid instability apparently unique to the X-doublet pattern,
  described and root-caused in detail `[§XII.E-H, leaf 287-315]`: periodic (~400 Hz)
  bursts of high-frequency (2000-7000 Hz, typically 2200-2700 Hz) instability, each
  burst having three phases (a rapidly-growing spinning 1-T "burnoff" detonation wave
  that makes exactly one circuit of the chamber and consumes accumulated unburned
  propellant → a "blowdown" pressure decay → a slow "accumulation" pressure recovery
  before the next burst). Root cause: the X-doublet is "a good atomizing, poor mixing
  element" — its concentric-ring spray leaves a persistent unmixed/unburned propellant
  cloud downstream of the face (matching the measured low-heat-flux near-injector zone
  above), which periodically ignites via a spinning 1-T wave and burns off in a single
  detonation-wave circuit. **The single most effective fix**: welding three dams into
  each face-ring manifold at the acoustic-null points under the opposing propellant's
  "pie" manifold, breaking circumferential acoustic communication between injector pie
  sectors via the ring manifolds — this eliminated resurging in configurations that had
  it repeatedly, and the fix's rework (machine off face, weld dams, rebond) was done
  in under three days, a second real demonstration of platelet rework speed. Acoustic
  cavities alone do *not* damp resurging and may even *promote* it, by damping the very
  high-frequency acoustic modes that would otherwise keep unburned propellant mixed and
  burning continuously.

## Design method

Not a from-scratch design monograph like `[SP-8081]`/`[SP-8087]`/`[SP-8107]`, but a real
applied performance-evaluation method is documented in full:
- **JANNAF-style energy release efficiency (ERE)** extraction `[§X.D, leaf 224]`:
  perfect-injector Isp = one-dimensional-kinetics (ODK) Isp minus boundary-layer loss
  minus divergence loss (via the ETAD table above); the energy-release loss is the gap
  between perfect-injector and measured Isp; ERE = [Isp(ODE) − ΔIsp(ERL)] / Isp(ODE).
- **Extrapolation across nozzle area ratios via a two-zone stream-tube model**
  `[§X.D, leaf 224-225]`: the energy-release loss for any test condition is reproduced
  by an equivalent mixture-ratio-maldistributed two-zone stream tube, parameterized by
  a single mixing-efficiency-like factor Em (O/F in each zone = Em·O/F and O/F/Em,
  weighted by a mass-fraction split); Em is then held fixed while re-evaluating ODK Isp
  at the target (flight) area ratio — allowing performance measured on a small sea-level
  test nozzle to be extrapolated to a very different flight-nozzle area ratio (2:1 or
  20:1 test nozzles → 55:1 OMS flight nozzle here).
- **Cant-angle and element-pattern selection method**: unielement screening (spray +
  mixing "milk maid" cold-flow tests using water/Freon simulants matched by density
  ratio to the real propellants, quantified via a Mixing Efficiency and a Rupe Number)
  → subscale multi-element confirmation → full-scale demonstration, at three
  successive thrust scales, is itself a real, load-bearing design/qualification
  methodology for a new injector-element type, independent of the platelet-specific
  findings above.

## Section map

- I. Introduction: leaf 12-14 — read.
- II. Summary (A. Unielement, B. Subscale, C. Full Scale): leaf 15-19 — read.
- III. Results and Conclusions (A. Unielement, B. Subscale, C. Full Scale incl.
  Fabrication/Performance/Heat Transfer/Stability/Transients/Evacuation-Soakout-Purge):
  leaf 20-27 — read.
- IV. Recommendations (A. based on Unielement/Subscale/ALRC, B. based on WSTF):
  leaf 28-33 — read.
- V. Application of Results (5-10 lb vernier / 10-1000 lb RCS / 6000 lb OMS-class
  applications): leaf 34-36 — read.
- VI. Contributions of OME to OMS (Injector/Chamber/Acoustic Cavity/Engine Operation):
  leaf 37-40 — read.
- VII. Unielement Program (A. Intro, B. Design, C. Spray Tests, D. Mixing Tests, E. Hot
  Fire Tests, F. Conclusions): leaf 41-72 — read (Table II hot-firing-log numeric
  columns OCR-garbled, prose read in full).
- VIII. Subscale Program (A. Objective/Approach, B. Design incl. Tables III-IV, C. Cold
  Flow, D. Hot Testing, E. Results incl. Tables VI-VIII): leaf 84-127 — B and E read in
  full; A/C/D (leaf 90-109) skimmed.
- IX. Full Scale Testing and Demonstration Program (A. Intro, B. Facility, C. Chambers,
  D. Cavity Configuration, E. Injectors incl. platelet-fabrication description, F. Test
  Series Description, G. Test Summary, H. Conclusions): leaf 129-204 — A-E (leaf
  129-167) and F Series 1-4 (leaf 168-174) read in full; F Series 5+ (leaf 175-204)
  skimmed (repeats already-captured resurging/cavity-geometry findings); G/H not
  separately read (content folded into §X-XII and the Summary sections already read).
- X. Full Scale Performance (A. Intro, B. Data Analysis Results, C. Performance
  Comparison, D. Analysis and Extrapolation Techniques): leaf 205-227 — read in full.
- XI. Full Scale Heat Transfer (A. Intro, B. Chamber Heat Fluxes, C. Correlating
  Coefficient, D. Mini-Skirt, E. Cavity Environment, F. Injector Face Environment,
  G. Baffle Heat Transfer): leaf 253-278 — read in full.
- XII. Full Scale Combustion Stability (A. Intro, B. Hardware Description, C. X-Doublet
  Injectors, D. X-Doublet Testing, E. Description of Resurging, F. Factors Influencing
  Resurging, G. Mechanism of Resurging, H. Summary): leaf 282-315 — read in full.
- Bibliography (monthly progress reports M-1 through M-32, WSTF test reports S-1/-2/-3,
  program plans, oral review list): leaf 316-321 — skimmed (titles only, confirms
  program chronology; no additional extractable technical content).
- Data appendix (Table XIV test-by-test performance listing, pages 218-242 per the
  report's own pagination): leaf ~228-252 — not read (OCR-garbled numeric tables,
  superseded by the narrative comparisons already extracted from §X).

## Caveats

- **This is a troubleshooting-heavy development report**, not a clean single-point
  design reference — a large fraction of the full-scale program (294 of 362 firings
  were stability-bombed) was iterative combustion-stability fixing rather than routine
  characterization; treat the specific numeric fixes (face-ring dams, cavity geometry)
  as *this engine's* resolution, not universal platelet-injector requirements.
- **X-doublet-specific findings, not platelet-generic**: resurging is explicitly
  attributed to the X-doublet element's atomization/mixing character, not to the
  platelet *construction* method itself — the splash-plate and unlike-doublet elements
  (also built as platelets) showed different (and in the splash-plate's case, worse)
  stability behavior via classical acoustic-mode coupling instead. Don't conflate
  "platelet injector" with "X-doublet element pattern" when citing this source. The
  platelet construction's benefits (cycle life, rework speed, fabrication feasibility,
  baffle compatibility) are load-bearing findings; the resurging/stability data is
  element-pattern-specific.
- **OCR quality**: body-text paragraphs are clean; numeric data tables (Table I, II,
  III, IV, XIV) are visually garbled by OCR column-merging on scanned tabular layouts —
  every numeric figure quoted above came from clean narrative-paragraph or single-line
  callout text, not from reconstructing a garbled table, except where explicitly noted
  (the ETAD and acoustic-mode-frequency tables above were both cleanly OCR'd as simple
  short lists, unlike the wider multi-column data tables).
- **Not this program's own reported WSTF altitude-test results**: this report
  documents the ALRC ground-test program and *references* two separate WSTF (White
  Sands Test Facility) final reports (13133-S-1 covering 1973 testing, 13133-S-3
  covering 1974 testing) which are not part of this PDF and were not sought out for
  this note — WSTF-only findings (e.g. detailed purge-effectiveness data, the complete
  1974 flight-specification-compliance determination) are outside this note's scope.
- **1970s hypergolic OMS-class engine, not a high-performance booster/upper-stage
  engine**: Pc = 125 psia is very low compared to this reference set's typical LOX/
  hydrocarbon or LOX/LH2 engines (hundreds to thousands of psia); heat-flux and
  cooling-margin numbers here are not directly comparable in magnitude to a
  gas-generator- or staged-combustion-cycle engine's regen-chamber numbers elsewhere in
  `claude_lit` — useful primarily for the hypergolic-pressure-fed, low-Pc design space
  this project's `TR341_Config.cfg` (a hypergolic pressure-fed lunar-lander thruster)
  occupies, and for the platelet-construction/resurging findings that are propellant-
  and Pc-class-independent in kind.
- **Nomenclature churn**: the report's own injector-naming scheme (XDT-1/XDT-1A/-B/-C,
  DXDT1-1/-2, XDT2-A, etc.) tracks *serial rework history* on a small number of physical
  injector bodies, not distinct designs — see `[§IX.E.1, leaf 158]`'s own explanation
  before trusting any cross-reference between injector "names" in this note or the
  source.
