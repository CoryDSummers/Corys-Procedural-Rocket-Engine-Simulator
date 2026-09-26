# ASR72-238 — Space Shuttle Orbit Maneuvering Engine Reusable Thrust Chamber, Final Data Dump

## Identity

Rocketdyne (A Division of North American Rockwell), *Space Shuttle Orbit Maneuvering Engine
Reusable Thrust Chamber, Final Data Dump*, Report ASR72-238, Contract NAS9-12802, prepared
for NASA Manned Spacecraft Center, Houston. Approved by R. D. Paster (SS/OME Project
Engineer) and R. W. Helsel (SS/OME Program Manager), Advanced Programs. No explicit
publication date survives in the extracted text; internally dated by its references — Ref. 1
is Rocketdyne's own *Preliminary Data Dump* ASR72-147, July 1972; Ref. 4 is an internal
Rocketdyne report dated September 1972; propellant costs are quoted at "August 1972
government supplied price list" — so this Final Data Dump is almost certainly late 1972.
`literature/ASR72-238 - Space Shuttle OME Reusable Thrust Chamber Final Data Dump.pdf`
(NTRS 19730005057; 213 PDF leaves, clean text layer for the narrative body — not a poor OCR
scan like some other sources in this set — but the data tables are raster/rotated-text pages
whose extracted text layer is garbled; read those via rendered page images instead, see
below). Tag: `[ASR72-238]`.

**Page-numbering note**: printed page N ≈ PDF leaf N+10 (0-indexed) for the narrative body
(printed pp. 1–36, leaf 11–46) and the Tables section (printed pp. 37–~91, leaf 47–~101).
This offset **does not hold** across the Figures section (printed pp. 110–205, which the
document's own List of Illustrations promises but which — combined with the Appendix A's own
independent "A-1, A-2, ..." page series starting at leaf 200 — doesn't reconcile to a single
linear leaf-offset formula for a document with only 213 leaves total). Cites below to leaves
past ~101 give the leaf number directly rather than relying on the formula.

## Character

Not a single-engine design report — a **comparative parametric trade study** ("data dump")
sizing the pressure-fed Space Shuttle Orbiter's Orbital Maneuvering Engine (OME, nominal
6000 lbf thrust class, ~3500–10,000 lbf range explored) across **7 candidate propellant
combinations** (NTO/MMH, NTO/50-50, LOX/MMH, LOX/50-50, LOX/N₂H₄, LOX/RP-1, LOX/C₃H₈
(liquid propane)) **× 2 cooling concepts** (regenerative + supplemental film + a radiation-
cooled nozzle extension, vs. dump/film cooling with a radiation-cooled extension), over
ranges of chamber pressure (75–200 psia), expansion ratio, and mixture ratio. Two full point
designs (with layout drawings, Figs. 1–2 — not independently extractable, plot/drawing
content) were carried far enough to produce real weight, envelope, life (creep/fatigue), and
interface-pressure numbers; delivered performance follows the JANNAF procedure (one-
dimensional kinetic performance + boundary-layer/divergence losses + vaporization efficiency
+ mixture-ratio-stratification loss from film cooling). The study closes with an explicit
recommendation: **regeneratively cooled NTO/MMH**, on development-risk/complexity/
reliability/safety grounds even though LOX/MMH gives the lightest system and LOX/C₃H₈/
LOX/MMH the highest performance.

This is a real, apples-to-apples **regen-vs-dump/film cooling comparison at a single fixed
engine class** (unlike `[TN-Dump]`, which is the deep single-cooling-concept treatment of
dump cooling already in this reference set, or `[Marquardt-5981]`, which surveys cooling
*feasibility* across the small-spacecraft-engine thrust range generically) — the first source
in `claude_lit` giving real side-by-side Δweight/ΔIsp numbers for the *same* thrust/Pc/
propellant holding only the cooling method fixed (Table 3). It is also the first source with
a real hypergolic (NTO/MMH, NTO/50-50) OME injector-type/pressure-drop-criteria table, and a
real study-level propellant-combination selection rationale spanning complexity, reliability,
safety, development risk, ecology, program cost/schedule, and logistics — categories this
project's `claude_lit` topic files don't currently have comparative data for at all.

## This note's extraction scope

**Read in full** (clean text layer, leaf 11–46): the entire narrative body — Introduction and
Summary, Point Designs, Parametric Data (Ground Rules and Assumptions, Envelope/Weight/
Inlet-Pressure/Performance Parametric Data), Sensitivity Data, Technological and Operational
Factors (Complexity, Reliability, Maintainability, Safety, Development Risk, Ecology),
Comparison, Program Comparison (Development Program, Maintenance, Logistics, Program Cost and
Schedule Comparison Summary), Conclusions and Recommendations, References.

**Read via rendered page images** (table pages are raster/rotated text, OCR-garbled in the
extracted text layer): Table 1 (Data Dump Configuration — the full trade matrix of thrust ×
Pc × MR × ε per propellant), Table 2 (OME Point Design Characteristics — the central
real-number payoff, transcribed in full, all 10 propellant/cooling-method columns), Table 3
(Overall OME Design Point Comparison of Cooling Methods, and of Propellant Combinations —
Δweight breakdown), Tables 4–6 (General / Regenerative-Cooled / Dump-Film-Cooled Chamber
Ground Rules), Table 7 (envelope functional-form only, low information value), Table 12
(Injector Pressure Drop Criteria — injector pattern by propellant pair), Table 13 (OME
Parametric Regenerative Cooling Data, all pages — jacket ΔP, film-coolant flow fraction,
subcooling margin, combustion-zone length across all 7 propellant pairs), Table 24 (Typical
Mixture Ratio and Chamber Pressure Tolerances, NTO/MMH). Also read via rendered image:
Fig. 6 (SS/OME Creep Damage, Regenerative Cooled Chamber — real material stress/rupture
curves) and Fig. 7 (Regeneratively Cooled Thrust Chamber Cycle Life Capability — real
fatigue-cycle-count-by-station curve). Appendix A's introductory method text (Regenerative
Cooling Analysis, Film Coolant Analysis, Structural and Life Analysis — leaf 200–202) was
read via the clean text layer.

**Not read / skimmed only for headers**: Tables 8–11 (combustor-length influence, trade
factors, weight functions — narrative already covers their conclusions), Tables 14–23 (the
full performance-summary tables per propellant/cooling combination — Table 2's point-design
row already gives the same delivered-Isp numbers at the design points; Tables 14–23 are the
same data spread across the full parametric sweep, not independently distilled), Tables
25–42 (Operating Sensitivity, Complexity/Reliability/Safety/Maintainability-by-propellant
score sheets, Combustion Products, Development/Maintenance/Logistics cost tables — narrative
text in Technological and Operational Factors / Program Comparison already summarizes their
conclusions in prose), and essentially all ~90 result plots (Figs. 8–96 — parametric curves
of Isp/weight/envelope/pressure vs. thrust/Pc/ε/MR; only Figs. 6–7 were rendered and read).
Appendix Tables A-1/A-2/A-3 and Figs. A-1 through A-13 are mostly diagrams/plots with little
extractable text beyond the method description already captured; not further pursued given
the document's scale and the inherently repetitive nature of a parametric data dump (the same
handful of variables re-tabulated across dozens of Pc/thrust/MR/ε combinations — this note
captures the representative numbers, not an exhaustive transcription).

## Key results

### Point-design comparison, Table 2 (all at F = 6000 lbf, 50-in. static exit diameter,
7° gimbal, 70%-bell nozzle; cooling-method codes: R/F/R = regen + supplemental film +
radiation-cooled extension, D/F/R = dump/film + radiation-cooled extension, R/R = regen
(no supplemental film) + radiation-cooled extension) `[ASR72-238 Table 2, leaf 48]`:

| Propellant | Cooling | Pc (psia) | ε | MR | Isp (s) | Wt (lb) | Length (in) | Liner | Extension | Film cool. (%) | Jacket ΔP (psi) | Inj. ΔP ox/fuel (psi) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NTO/50-50 | R/F/R | 125 | 72 | 1.6 | 313.9 | 185 | 73 | CRES | Cb/Ti | 2.9 | 21 | 23/27 |
| NTO/50-50 | D/F/R | 125 | 72 | 1.3 | 297.9 | 150 | 70 | CRES | Cb/Ti | 13.5 | 6 | 23/30 |
| NTO/MMH | R/F/R | 125 | 72 | 1.65 | 313.0 | 185 | 73 | CRES | Cb/Ti | 2.0 | 16 | 23/27 |
| NTO/MMH | D/F/R | 125 | 72 | 1.65 | 304.8 | 150 | 71 | CRES | Cb/Ti | 8.4 | 6 | 23/30 |
| O₂/MMH | R/F/R | 100 | 58 | 1.2 | 331.6 | 210 | 74 | CRES | Cb/Ti | 2.6 | 14 | 18/18 |
| O₂/MMH | D/F/R | 100 | 58 | 1.0 | 318.5 | 180 | 72 | CRES | Cb/Ti | 9.4 | 7 | 18/18 |
| O₂/C₃H₈ (liquid propane) | R/R | 100 | 58 | 2.6 | 339.3 | 258 | 77 | **Copper** | Ti | 0 | 20 | 23/23 |
| O₂/RP-1 | R/R | 100 | 58 | 2.5 | 324.0 | 223 | 86 | CRES | Cb/Ti | 0 | 3 | 23/23 |
| O₂/N₂H₄ | R/R | 100 | 58 | 0.8 | 331.5 | 207 | 77 | CRES | Cb/Ti | 0 | 11 | 18/18 |
| O₂/50-50 | R/F/R | 100 | 58 | 1.2 | 328.3 | 210 | 72 | CRES | Cb/Ti | 2.7 | 17 | 18/18 |

Notable real-hardware facts embedded in the full table (not shown in the condensed columns
above): contraction ratio is **2** for every single point design regardless of propellant or
cooling method; **O₂/C₃H₈ is the one propellant pair using a copper liner** (all others use
CRES) "because of its good propellant compatibility" (a real hydrocarbon-vs-CRES material
choice made for chemical-compatibility reasons, not thermal ones, per the narrative); channel
count and minimum channel height vary enormously with cooling method — e.g. NTO/MMH goes
from **180 channels / 0.062 in.** (R/F/R) to **514 channels / 0.025 in.** (D/F/R) at the same
Pc/ε, i.e. the dump/film design needs nearly 3× the channel count at less than half the
minimum channel height to hit its (lower) coolant-side heat-flux/life requirement; **LOX/RP-1,
LOX/N₂H₄, and LOX/C₃H₈ all use zero supplemental film cooling** (0%) even in the "regen +
film" family — corroborating the narrative's statement that film cooling was specifically
*not* used for these three because of high RP-1/propane decomposition temperatures and
LOX/N₂H₄'s low mixture ratio; LOX/RP-1's regen jacket ΔP is only **3 psi** — the lowest of any
propellant/cooling combination in the table, vs. 21 psi for NTO/50-50 R/F/R.

### Cooling-method and propellant Δweight comparison, Table 3 `[ASR72-238 Table 3, leaf 49]`:

At fixed nominal design MR, switching from regen (with film) to pure dump/film cooling costs
delivered Isp and *reduces* engine weight but *increases* total OMS system weight once
propellant/tankage effects are folded in — regen wins overall:

| Propellant (nominal MR) | Regen Isp (s) | Film Isp (s) | ΔW_Is (Isp-driven ΔOMS weight, lb) | Regen engine wt (lb) | Film engine wt (lb) | Net ΔOMS weight, film − regen (lb) |
|---|---|---|---|---|---|---|
| NTO/MMH (1.65) | 313.1 | 304.8 | +681 | 185 | 150 | **+540** |
| NTO/50-50 (1.60) | 313.9 | 297.9 | +1312 | 185 | 150 | **+1136** |
| O₂/MMH (1.20) | 330.9 | 318.0 | +877 | 210 | 180 | **+712** |

(the regen NTO/MMH's own Isp figure appears as 313.1 s here vs. 313.0 s in Table 2 — a ~0.1 s
discrepancy likely reflecting the original document's own rounding between the two tables, not
an extraction error). Total OMS (system) weight by propellant combination, regen cooling,
6000 lbf class: **NTO/MMH 27,350 lb, NTO/50-50 27,300 lb, O₂/MMH 27,050 lb, O₂/50-50 27,240 lb,
O₂/RP-1 27,790 lb** — i.e. LOX/MMH gives the *lightest* OMS system of the five compared, and
LOX/RP-1 the heaviest, despite LOX/RP-1's lower Isp penalty being partly offset by its lower
required film-coolant/complexity overhead; this system-level weight, not thrust-chamber
weight alone, is what the study's final recommendation is actually optimizing.

### Ground rules `[ASR72-238 Tables 4–6, leaf 50–52]`:

- **General** (Table 4): contraction area ratio = 2 (confirmed independently of Table 2's own
  column, applied as a blanket ground rule); nozzle length = 70% of the equivalent 15°
  half-angle cone; 7° throat-gimbal ring; minimum life 1000 cycles / 15 hours (both carrying
  a safety factor of 4 in the life analysis, per the narrative); radiation-skirt transition
  from **coated columbium** (1600°F < T ≤ 2400°F) to **coated titanium** (T ≤ 1600°F) — the
  same Cb→Ti radiative-cooling material transition logic already documented for other engines
  in `topics/12-materials-and-structures.md`, here with an explicit temperature-band criterion
  attached; quad-redundant series/parallel ball valve, pneumatically actuated.
- **Regen-cooled chamber** (Table 5): **channel-wall construction with electroformed nickel
  closeout** on the outer wall (uppass cooling, i.e. coolant flows toward the injector);
  **CRES liner for all propellants except LOX/C₃H₈, which uses copper** (compatibility, not
  thermal, per the narrative); **0.03-in. constant hot-wall thickness**, described explicitly
  as "a near-minimum fabrication wall thickness"; radiation-cooling nozzle-attach area ratio
  set by a **< 1 Btu/in²-sec** heat-flux criterion at that station, with real ε values tabulated
  per Pc (e.g. ε_R = 6/7/8/11 at Pc = 75/100/125/150 psia); propane and RP-1 both use a
  **coolant bypass circuit** — propane specifically to keep the regen inlet area ratio low
  while still fully vaporizing all the propane in the nozzle before it reaches the bypass
  point, RP-1 to limit channel height/chamber weight while avoiding excessive jacket ΔP; max
  coolant bulk temperature = boiling point − 50°F for MMH/50-50, 280°F flat for N₂H₄.
- **Dump/film-cooled chamber** (Table 6): a **short INCO liner press-fitted into the
  columbium shell** (constant-width, constant-depth channels, optionally spiralled for
  distribution); insulated to limit the *outer* wall temperature to 600°F, insulation extends
  to ε = 3 where the nozzle becomes radiation-cooled (assisted by the film coolant injected
  by the liner); same Cb→Ti transition-point logic as the regen design; same coolant bulk-
  temperature limit as regen (i.e. bulk-temperature design criterion is cooling-method-
  agnostic in this study, only the mechanism for meeting it differs).

### Injector type and stability ΔP criteria, Table 12 `[ASR72-238 Table 12, leaf 58]`:

| Propellant combination | Injector pattern | Stability min. ΔP/Pc (orifice) |
|---|---|---|
| NTO/50-50, MMH | Unlike doublet | 15% |
| LOX/50-50, MMH | Like doublet | 15% |
| LOX/RP-1 | Like doublet | 15% |
| LOX/N₂H₄ | Like doublet | 15% |
| LOX/C₃H₈ | **Concentric tube (regen)** OR **like doublet (film)** | 15% |

A real, propellant-pair-resolved corroboration of the 15–20% injector-ΔP-for-stability rule
already documented generically from `[Huzel]`/`[Sutton]`/`[SP-8081]` in
`topics/05-injectors.md` — here pinned at exactly **15%** across every single propellant
combination studied, on a real hypergolic pressure-fed OME. Also a real example of injector
*type* varying by **cooling method, not just propellant** for the same pair (LOX/C₃H₈'s
concentric-tube/coaxial element used specifically for the regen design, switching to like-
doublet for the film-cooled design) — a design-choice interaction this project's injector
topic file doesn't currently document. Elsewhere in the narrative: unlike-doublet used for
NTO/amine pairs, like-doublet for LOX/amines and LOX/RP-1, coaxial for LOX/C₃H₈; LOX-oxidizer
injectors have center-mounted LOX with provision for electrical spark ignition, and all
injectors have acoustic-cavity provisions for combustion-stability suppression.

### Real regen-cooling jacket parametric data, Table 13 (all values `[ASR72-238 Table 13,
leaf 59–62]`, at the 6000 lbf design point unless noted, jacket ΔP in psi, film-coolant flow
as % of total propellant flow, T_sub = subcooling margin below the coolant's boiling
point, °F):

| Propellant | Pc range tested (psia) | Jacket ΔP range (psi) | Film coolant flow (%) | T_sub range (°F) |
|---|---|---|---|---|
| NTO/MMH | 100–200 | 12–34 | 2.0 (flat) | 50–81 |
| NTO/50-50 | 75–200 | 10–36 | 2.0–3.7 | 50–62 |
| O₂/MMH | 75–125 | 10–24 | 2.0–2.7 | 50–57 |
| O₂/50-50 | 100 | 14–16 | 2.0–4.6 | 50–64 |
| O₂/N₂H₄ | 75–125 | 10–21 | **0** | 50–111 |
| O₂/C₃H₈ | 75–125 | 19–22 | (not tabulated in this pass) | (not tabulated) |
| O₂/RP-1 | 75–200 | **5–8** | **0** | (blank in source — no subcooling limit applies) |

The **zero film-coolant-fraction rows for O₂/N₂H₄ and O₂/RP-1** across their entire tested
Pc/thrust range are a real, tabulated confirmation of the narrative's qualitative statement
(§Point Designs) that supplemental film cooling was deliberately *not used* for these
propellants; LOX/RP-1's jacket ΔP is dramatically lower (5–8 psi) than every hypergolic or
LOX/amine combination (10–36 psi) at the same thrust class — a real data point that
LOX/RP-1's regen circuit runs at much lower coolant-side pressure loss than the amine-fuel
designs in this study, plausibly a channel-geometry/velocity choice rather than a coolant-
property difference per se (RP-1's own thermophysical coolant data is covered separately by
`[NISTIR6646-RP1]`/`[Akhmedova-RP1]`/`[Huber-RP1RP2]`/`[Outcalt-RP1RP2]`).

### Mixture-ratio/Pc off-nominal envelope, Table 24 `[ASR72-238 Table 24, leaf 82]` (NTO/MMH,
regen/film cooling, nominal MR = 1.65, nominal Pc = 125 psia): calibrated-engine tolerance is
only ±0.02 MR / ±2.5 psia; stacking inlet-pressure excursions (±4 psi each side) widens this
to ±0.15 MR / ±4.8 psia; adding inlet-pressure-and-temperature exclusions (40–90°F, ΔT ≤ 10°F
max) gives ±0.16 MR / ±5.4 psia; a single oxidizer-or-fuel regulator malfunction (upstream
regulator +10 psia) widens MR to **+0.34** (i.e. up to MR ≈ 1.99 — matching the narrative's
"mixture ratios as high as 1.8–2 o/f") and Pc to 133 psia (max); a ball-valve malfunction
(single flow path closed, minimum inlet pressures, max inlet temperature) gives the *worst-
case low* Pc bound of **116.6 psia (min)**. A real, itemized worst-case mixture-ratio/
chamber-pressure stack-up methodology (calibration → nominal excursions → regulator
malfunction → valve malfunction, each adding its own MR/Pc delta) that could inform how
`engine_designer` frames its own off-nominal MR/Pc margin checks, if it ever adds one.

### Real material creep and fatigue life data, Figs. 6–7 `[ASR72-238 Fig. 6–7, leaf 109–110]`
(regeneratively cooled chamber, 15-hour/1000-cycle life requirement with safety factor 4):
real creep-rupture stress data at the maximum hot-gas-wall stress level for three real regen-
chamber candidate materials — **Haynes 188 at 47 ksi, Inconel 625 at 50 ksi, CRES at 34
ksi** — plotted as temperature vs. 4·(operating time)/(rupture time); at 15 hours' operation
with SF 4, none of the three approaches its rupture-damage limit even near 1300°F, leading
the study to conclude "no significant creep damage on regen. chamber" for any of these three
candidate liner materials. Real fatigue-cycle-count-by-axial-station data (including 60 hours
of cumulative operation): predicted fatigue life is **lowest at the throat (~1.3×10⁴
cycles)**, rising to **~4–5×10⁴ cycles a few inches downstream in the nozzle** and **~10⁵
cycles at the injector end** — i.e. the throat is confirmed as the fatigue-critical station
(consistent with every other chamber-fatigue source already in this reference set, e.g.
`[Miller-CuFatigue]`), and even the worst-case throat prediction (~1.3×10⁴ cycles) clears the
1000-cycle requirement with roughly a **13× margin** before the analysis's own stated SF of 4
is even applied — a real, quantified example of how much margin a regen-chamber life analysis
can carry beyond its nominal safety factor.

### Real hardware/system detail (narrative, leaf 13–15, 27–30):

- **Quad-redundant propellant valve**: series-parallel arrangement of four ball-type valves;
  a single fuel-valve failure costs **1 psi Pc / 2% thrust** and **+4% MR**; a single
  bipropellant-path failure costs **~2.5% thrust** with negligible MR shift; loss of
  electrical/pneumatic control on one side raises valve ΔP by **~5 psi**.
- **Valve mounting orientation chosen to minimize duct weight differs by cooling method**:
  perpendicular to the chamber axis for the regen-cooled chamber, parallel to the axis for the
  film-cooled chamber — a real example of a propellant-routing/weight tradeoff driven purely
  by chamber cooling-method choice, independent of the propellant itself.
  Injector-to-chamber joint is **welded** (not bolted) specifically to eliminate two seals
  (fuel-to-hot-gas, fuel-to-ambient) and improve reliability, even though this makes combustor
  replacement harder — an explicit reliability-vs-maintainability tradeoff call.
- **Gimbal ring**: titanium, hollow-rectangular cross-section (for combined bending/torsional
  stiffness), located at the throat plane, self-aligning spherical bearings at 4 pivot points,
  ±7° pitch/yaw.
- **Injector pressure-drop budget** (leaf 24): all non-injector, non-jacket component ΔP =
  **1.05 × Pc** (throat-stagnation correction for the 2:1 contraction-ratio engine) **+ 19 psi
  oxidizer-side / + 15 psi fuel-side**; minimum injector orifice ΔP = 15% of Pc at off-design
  (matches Table 12 above); feed-system pressure drops were explicitly "patterned after the
  pressure drops of the LM Ascent Engine" — a real cross-program design-heritage borrowing
  worth noting given this project's own hypergolic pressure-fed lander-thruster work
  (`TR341_Config.cfg`).
- **Combustion products / ecology** (leaf 36–37): OME combustion-product NOₓ/CO emissions at
  the 6000 lbf/50-in.-exit design point were compared against 1975 heavy-duty-vehicle emission
  standards and found acceptable for all 7 propellant combinations; LOX/50-50 produces ~3×
  the NOₓ of NTO/MMH; LOX/RP-1 produces ~2× the CO of NTO/MMH and visibly sooty exhaust from
  unburned carbon — real, if dated (1972 vintage) environmental-comparison numbers, of low
  direct relevance to `engine_designer` physics but noted for completeness.

### Development-risk / qualitative comparison conclusions (leaf 21–35):

Regenerative cooling was judged superior to dump/film on **every** qualitative axis studied
(complexity, reliability, safety, development risk) except raw simplicity — "the resultant
cost savings during development and operation is negligible" for the film-cooled system's
simplicity advantage. Propellant preference order: NTO/MMH ≈ NTO/50-50 (least complex, most
reliable/safe, lowest development risk) > LOX/RP-1 > LOX/MMH ≈ LOX/50-50 (roughly tied, LOX/
MMH gives the lightest system but has the least available technology base of the two).
Critical technology gaps flagged for LOX/RP-1: **combustion performance and heat flux with
carbon deposition as a function of chamber length "not available"** at the time of this study
(a real, dated (1972) gap that `[Lewis-Deposits]`/`[TP2862-LOXRP1]` in this reference set
partially closed decades later) and no prior multi-restart-capable ignition-system development
for LOX/RP-1 or LOX/Amine combinations (an augmented spark igniter, ASI, was assumed necessary
for all non-hypergolic pairs — LOX/H₂ ASI heritage existed, LOX/RP-1 had "some work," LOX/
amines had none). Final recommendation: **regeneratively cooled NTO/MMH**.

## Design method

**Delivered-performance methodology** (JANNAF procedure, leaf 24–26): one-dimensional
kinetic (ODK) performance as the primary basis (ODF, one-dimensional frozen, used instead at
very low mixture ratios — e.g. the film-coolant boundary layer itself — where ODK becomes
inaccurate for carbon-bearing propellants because of significant unburned-carbon content),
plus separately calculated boundary-layer (drag + heat-transfer) and nozzle-divergence losses,
plus propellant-vaporization loss as a function of chamber length, plus mixture-ratio-
stratification loss from film cooling (computed via a stream-tube analysis assuming a linear
MR profile from zero at the wall to core MR, and 100% film-cooling effectiveness). A flat
**core-mixing efficiency of 0.986** was applied uniformly across all 7 propellant
combinations, described as "reasonable ... through appropriate sizing and spacing of injector
elements" — i.e. an assumed constant, not a measured/derived value, for this parametric study.
LOX/RP-1's own vaporization efficiency could not be computed at all ("computer program
inability to model the RP-1 combustion process") — instead a fixed **20-in. combustor length**
was assumed for all LOX/RP-1 point designs to hit an assumed **η_vap ≈ 97.5%**, empirically
based rather than derived, a real example of 1970s-era combustion-modeling limitations for
kerosene-class fuels specifically (contrast with the cleaner-modeling amine/hydrazine/hydrogen
fuels in the same study).

**Thermal/life analysis** (Appendix A, leaf 200–202): regen-jacket design starts from a
radiation-cooling analysis fixing the coolant-inlet area ratio (the Cb-nozzle-attach point),
then sizes channel count/width by fabrication considerations, then determines per-station
coolant velocity from **empirical burnout heat-flux correlations** (not further specified in
the extracted text — likely propellant-family-specific, unnamed in this pass), then sizes film
coolant (if any) to hold the bulk-temperature-rise limit at the assumed off-design envelope
(±10% Pc, ±12% MR), with any film-coolant fraction below 2% floored to exactly 2% regardless
of the computed requirement. Structural/life analysis used the finite-element method for
stress from pressure/force/thermal-gradient loads, combining **fatigue and creep damage
fractions** (Miner's-rule-style linear damage summation implied, not spelled out
mathematically in the extracted text) into a single life prediction, with the dump/film-cooled
chamber's dominant failure mode identified as **creep** (driven by the high axial thermal
gradient where the film coolant decomposes) rather than fatigue — the opposite of the
regen-cooled chamber, where fatigue dominates but with large margin (see Fig. 7 result above).
This creep-vs-fatigue failure-mode split by cooling method (not just by material) is a real,
if qualitatively stated, design-method finding not previously captured from any other source
in this reference set.

## Section map

- Foreword / Abstract: printed p. ii (leaf 2–3) — read.
- Table of Contents / List of Illustrations / List of Tables: printed p. iii–ix (leaf 4–10) —
  read (used to plan the extraction).
- Introduction and Summary: printed p. 1–2 (leaf 11–12) — read.
- Point Designs: printed p. 3–8 (leaf 13–18) — read.
- Parametric Data (Ground Rules, Envelope/Weight/Inlet-Pressure/Performance Parametric Data):
  printed p. 9–16 (leaf 19–26) — read.
- Sensitivity Data: printed p. 17–20 (leaf 27–30) — read.
- Technological and Operational Factors (Complexity, Reliability, Maintainability, Safety,
  Development Risk, Ecology): printed p. 21–27 (leaf 31–37) — read.
- Comparison / Program Comparison (Development Program, Maintenance, Logistics, Program Cost
  and Schedule Comparison Summary): printed p. 28–34 (leaf 38–44) — read.
- Conclusions and Recommendations: printed p. 35 (leaf 45) — read.
- References: printed p. 36 (leaf 46) — read.
- Table 1 (Data Dump Configuration): printed p. 37 (leaf 47) — read via rendered image.
- Table 2 (OME Point Design Characteristics): printed p. 38 (leaf 48) — read via rendered
  image (full transcription, all 10 columns).
- Table 3 (Overall OME Design Point Comparison): printed p. 39 (leaf 49) — read via rendered
  image.
- Tables 4–7 (Ground Rules, Envelope Functions): printed p. 40–43 (leaf 50–53) — read via
  rendered image (Table 7 low information value, functional-form only).
- Tables 8–11: printed p. 44–47 (leaf 54–57) — not read; narrative already covers their
  conclusions.
- Table 12 (Injector Pressure Drop Criteria): printed p. 48 (leaf 58) — read via rendered
  image.
- Table 13 (OME Parametric Regenerative Cooling Data, 4 pages): printed p. 49–52 (leaf
  59–62) — read via rendered image, all 4 pages.
- Table 14 (Engine Performance, methodology summary): printed p. 53 (leaf 63) — covered by
  the narrative's own JANNAF-procedure description; table itself not separately rendered.
- Tables 15–23 (Performance Summary tables per propellant/cooling combination): printed
  p. 54–71 (leaf 64–81) — not read; Table 2's point-design rows already give the design-point
  delivered-Isp numbers.
- Table 24 (Typical MR and Pc Tolerances): printed p. 72 (leaf 82) — read via rendered image.
- Tables 25–31 (Operating Sensitivity, Complexity/Reliability/Safety/Maintainability
  comparisons): printed p. 73–81 (leaf 83–91) — not read; narrative Technological and
  Operational Factors section covers the same ground in prose.
- Tables 32–42 (Combustion Products, cost/schedule/logistics tables): printed p. 99–109
  (leaf position not confirmed past ~leaf 101 — offset breaks down here, see Identity note) —
  not read; narrative Ecology/Program Comparison sections cover the same ground in prose.
- Figures 1–5 (engine layout drawings, hot-wall-temperature-profile plots): referenced in the
  narrative (Point Designs section) but not independently rendered — plot/drawing content,
  not separately extractable text.
- Figs. 6–7 (creep damage / fatigue life curves): leaf 109–110 — read via rendered image.
- Figs. 8–96 (remaining parametric plots): not read.
- Appendix A (Thermal/Life Analysis method text): leaf 200–202 — read via clean text layer.
- Appendix Tables A-1/A-2/A-3, Figs. A-1 through A-13: leaf 203–212 — not read (diagram/plot
  content, OCR-garbled where text-based).

## Caveats

- **This is an analytical parametric trade study, not a test report** — unlike e.g.
  `[AEDC-J2S]` or `[NK-33-Mod]` in this reference set, none of these numbers come from actual
  hot-fire or altitude testing; they are 1972-vintage Rocketdyne design-analysis predictions
  (JANNAF-procedure performance, finite-element structural/life analysis). Treat magnitudes as
  a real engineering design team's best contemporary estimate, not as validated hardware data.
- **The data-table pages are raster/rotated-text scans** whose extracted text layer is
  OCR-garbled (unlike the narrative body, which has a clean text layer) — every quantitative
  table cited above was read by rendering the PDF page to an image and reading it visually,
  not by trusting `page.get_text()`. Cross-check any further table extraction from this
  document the same way; don't trust the raw text layer for Tables 1–42.
- **Document date is inferred, not stated** — no explicit publication date survives in the
  extracted Foreword/title-page text; inferred as late 1972 from internal reference dates
  (see Identity). If an exact date is later needed, it may be on a cover page not captured by
  this note's page renders.
- **The leaf-offset formula (printed page N ≈ leaf N+10) only holds through roughly the
  Tables section** (printed p. 1–~91, leaf 11–~101) — it does not reliably extend to the
  Figures section or Appendix A; navigate those by leaf-number search (e.g. `APPENDIX A` was
  located at leaf 200 by text search, not by formula) if returning to this document.
- **This study predates the production Space Shuttle OMS/RCS engine selection** — the real
  flight OMS engine (Aerojet AJ10-190) used N₂O₄/MMH, consistent with this study's own
  regen-NTO/MMH recommendation, but this document's specific point design (channel-wall CRES
  liner, electroformed-nickel closeout, Cb/Ti radiation nozzle) should not be assumed to
  describe the actual flight hardware without independent confirmation — it's a contractor
  study input to that eventual decision, not a description of the engine that flew.
- Combustion-products/ecology and program-cost/schedule/logistics content (leaf 33–44) was
  read but is of low relevance to `engine_designer` physics; included in this note for
  completeness/honesty about scope, not because it's expected to be cited from
  `topics/*.md`.
