# [STBE-PW] — Space Transportation Booster Engine Configuration Study, Final Report

## Identity

Pratt & Whitney Government Engine Business, *Space Transportation Booster Engine
Configuration Study, Final Report (DR4), Includes Design Definition Document (DR8) and
Environmental Analysis (DR10)*, FR-19691-4 Volume II, 1 December 1989 (design work
completed 31 March 1989), Contract NAS8-36857 Modification No. 10, prepared for NASA
Marshall Space Flight Center. NASA doc ID `19930003253`. `literature/PW FR-19691-4 - Space Transportation Booster Engine Configuration Study.pdf`
(392 PDF pages/leaves, 0-indexed; leaf 0 = title page; no PDF bookmark/TOC — the printed
front-matter Table of Contents at leaves 8-19 was read directly instead). Tag: `[STBE-PW]`.

**Page citation convention for this note**: leaf index (0-indexed PDF page), since the
document's own printed page numbers restart/jump across front-matter (roman-numeral) and
body (arabic) sections and OCR frequently drops or garbles the footer numeral. Where a
clean printed-page footer was directly legible it is given too, e.g. `[STBE-PW leaf 35
p.16]`. A rough mapping for the technical body (Section 4 onward) is
`printed_page ≈ leaf_index − 19`, confirmed at leaves 30/32/35/44 (11/13/16/25) but **do
not trust it past leaf ~150** — it visibly drifts (leaf 158's own footer reads "137", 2
off from the formula) once the document interleaves unnumbered fold-out figure pages.
Always prefer the leaf index for re-finding a passage.

## Character

A **massive (392-page), late-Reagan-era NASA Advanced Launch System (ALS) booster-engine
trade study and preliminary design report** — not a textbook or a compact real-engine
survey like most other sources in this reference set. It is one of a small number of
sources in `claude_lit/` giving **real, fully-worked conceptual designs for multiple
distinct 600-750 Klbf-class booster engines side by side, all from the same design team
using the same methodology and JANNAF-standard performance-prediction procedure** — gas
generator, split expander (a P&W-specific expander-cycle variant, not the same as the
`RL10`/`[AEDC-J2S]` engines already in this reference set), and tap-off cycles, each
carried through preliminary turbopump/combustor/nozzle/controls design with real numeric
performance tables. This is engineering-report prose (numbered subsections down to 5
levels, e.g. §4.2.2.4.2), dense with tables and figure call-outs; OCR quality is fair
to poor in places (numeric tables in particular — many digit substitutions, e.g. "IBM"
for a pressure figure, "l" for "1") and pages with only figures/schematics extract as
near-empty or as garbled axis-label fragments. This note deep-reads the technical design
sections (§4) and skims/skips essentially all of the programmatic/cost/schedule content
(§3, §5, most of Volume III's counterpart cost data referenced but not present in this
PDF).

**Scope note — this document covers *booster*-class engines (STBE), not the STME
(Space Transportation Main Engine) upper-stage/core-vehicle H2/O2 engine it's explicitly
derived from/compared against** — STME numbers appear throughout only as a "common
hardware" comparison baseline, never as this document's own subject.

## Key results — Engine trade study & candidate configurations

**Seven all-gas-generator candidate configurations** compared for lowest life-cycle cost
`[STBE-PW leaf 25, Table 1-1]` (625 Klbf sea-level thrust target, varying propellant/
coolant/Pc/eps):

| Config | Propellant | Coolant | MR | Pc (psia) | Isp vac/SL (s) | eps | Length/Dia (in) | Weight (lb) |
|---|---|---|---|---|---|---|---|---|
| STBE-1A | LOX/RP-1 | RP-1 | 2.90 | 1275 | 316.0/264.3 | 25 | 152/98 | 6750 |
| STBE-1B | LOX/RP-1 | LOX | 2.90 | 1667 | 318.4/273.5 | 35 | 155/98 | 6745 |
| STBE-2 | LOX/RP-1 | LH2 | 3.12 | 3500 | 360.1/318.2 | 55 | 143/84 | 6925 |
| STBE-3 | LOX/CH4 | CH4 | 3.57 | 2333 | 341.5/302.6 | 40 | 143/88 | 6655 |
| STBE-4 | LOX/CH4 | LH2 | 3.64 | 3500 | 369.5/326.5 | 55 | 143/84 | 6845 |
| STBE-5 | LOX/C3H8 | C3H8 | 3.20 | 2333 | 333.9/291.4 | 40 | 143/88 | 6650 |
| STBE-6 | LOX/C3H8 | LH2 | 3.38 | 3500 | 363.2/321.0 | 55 | 143/84 | 6885 |

A real, directly citable **thrust-class/eps/MR/Isp table across three hydrocarbon fuels
(RP-1, methane, propane) at matched thrust and varying cooling-fluid strategy** — useful
cross-check anchor for `engine_designer`'s propellant-pair Isp/eps defaults
(`topics/11-propellants.md`).

**Overall trade-study result**: LOX/methane/hydrogen tripropellant gas generator won on
life-cycle cost initially `[leaf 26]`; **explicit, stated engineering reasons methane beat
propane and RP-1** `[leaf 28, Table 1-4]`: highest combustion efficiency, more predictable
heat flux, cleaner GG gas, simpler injector design, self-purging (reduces cleaning),
very stable combustion, good coolant with high coking-onset temperature, allows
transpiration cooling, allows coaxial gaseous-fuel injection, improves injector-face
cooling, lower environmental spill impact (volatile, non-toxic, disperses readily). This
is a rare **explicit real-program methane-vs-RP1-vs-propane coolant/injector rationale**,
not just a performance number — directly citable for any `engine_designer` propellant-
selection guidance text.

Program then pivoted (bipropellant beat tripropellant on cost once vehicle-contractor
studies matured, and NASA relaxed the engine-life requirement from 100 to 30 missions
`[leaf 28]`) to LOX/methane bipropellant gas generator, then (late 1987) to a P&W-novel
**"split expander" cycle** found more cost-effective than gas generator, then finally to
matching an STME-derivative (LO2/H2 core engine) design constraint, producing the final
selected-configuration set carried to full preliminary design in §4.0 `[leaf 34]`:
Derivative LOX/CH4 GG, Unique LOX/CH4 GG, Common LOX/CH4 GG, Unique LOX/RP-1 GG,
Derivative LOX/CH4 Split Expander, Unique LOX/CH4 Split Expander, Unique LOX/CH4 Tap-Off.

## Key results — Split Expander cycle (new cycle variant, not elsewhere in claude_lit)

**Definition, in the report's own words** `[leaf 28-29]`: "The split expander cycle
differs from the standard expander cycle used in the RL10 engine by separating a portion
of the fuel flow at the first-stage pump and directing that flow directly to the
injector. The remainder of the fuel flow completes the standard expander cycle... Since
flow and temperature trade proportionally in turbine power, the split expander low
flowrate at the higher temperature will provide the same turbine power. The pump work
will be reduced due to the reduction in flow through the second-stage pump. This reduced
power requirement provides the capability for a higher chamber pressure." I.e. **a
bypass around the second pump stage lets a smaller fraction of fuel take the full
regen-heat pickup at higher exit temperature, feeding the turbine at the same power while
cutting second-stage pump work — trading pump work for turbine-inlet temperature to raise
achievable Pc versus a plain expander.** This is a genuinely new cycle-topology datum for
`topics/08-engine-cycles.md` (existing coverage has GG/tap-off/expander/staged combustion/
pressure-fed but not this specific bypass variant).

Two real worked split-expander engines, both LOX/CH4:

**Derivative STBE Split Expander** (STME-derivative, uses STME's H2/O2 hardware where
possible) `[leaf 250, Fig 4.2.1.1-1]`:
- vs. its STME H2/LOX baseline side by side: STME (H2/LOX) MR 6.0, Pc 896 psia, Isp
  vac/SL 433.9/326.3 s, eps 28, 5084 lb; **Derivative STBE (CH4/LOX)** MR 3.5, Pc 734
  psia, thrust vac/SL 706,500/600,032 lbf, Isp vac/SL 327.7/278.3 s, eps 13.5, length 140
  in, dia 104 in, weight 6193 lb.
- Regen jacket split: at design power level, methane pump at 17,181 rpm to 5195 psia;
  **81.2% of fuel flow regen-cools the milled-channel copper-alloy main chamber** (from
  eps 5.48 back to the injector face), remainder cools the tubular stainless-steel nozzle
  (eps 5.48 down to eps 35) then feeds the GG `[leaf 151]`.
- Nozzle brazed-tube design table (Haynes 230, 1170 tubes, 80 in length, eps 2.40→13.5)
  `[leaf 270]`: min wall thickness ≥0.013 in, 0.2%-yield tube-stress margin =1.0 (i.e.
  design-limited at yield), coolant Mach ≤0.5, max wall-temp limit 2260 R, min ultimate
  temperature margin ≥375 R. Methane coolant enters tube assembly at 572 R/4452 psia,
  exits 883 R/4030 psia (Δp 426 psid nozzle-only leg cited separately from chamber leg)
  `[leaf 270-271]`.
- Turbine-bypass-valve (TBV) + jacket-bypass-valve (JBV) trim the thrust and MR by
  routing some fuel around the turbine / around the nozzle jacket respectively — the
  cycle's actual throttle mechanism `[leaf 272, 281]`. Trim set at 706,500 lbf vacuum
  thrust ground-calibration point; ±3% thrust/MR achievable open-loop `[leaf 281]`.
- Start sequence: LOX lead (oxidizer injector primed before fuel valve opens, to avoid
  turbine temperature spikes from LOX phase change and to avoid unburned-fuel buildup)
  `[leaf 279]`, helium spin-assist, dual electric-spark oxygen/methane torch igniters.

**Unique STBE Split Expander** (clean-sheet, no STME hardware constraint), 750 Klbf SL
thrust, Pc 896 psia design point:
- Combustor/injector table `[leaf 316, Table 4.2.2.4-1]`: chamber L* (min) 49 in, fuel
  flow 577.2 lb/s, ΔP_fuel 75.4 psi, LOX flow 2020.1 lb/s, ΔP_LOX 58.1 psi, 1632
  injector elements, spud ID 0.303 in, annular gap 0.03 in. **L* explicitly stated as
  larger than the gas-generator-cycle engines' (31.3-41 in) "mainly as a result of poorer
  atomization in the split expander due to less available pressure drop across the
  injector elements"** `[leaf 262, 315]` — a real, quantified cycle-driven L*/atomization
  penalty worth flagging for any expander-cycle L*/chamber-sizing guidance.
- Main chamber: 720 (some text says 630 for the Derivative variant, 720 for Unique —
  the two counts appear on adjacent leaves for the two different engines) double-tapered
  Haynes 230 tubes brazed together with a structural jacket brazed to the backside to
  carry hoop loads `[leaf 317, 320]`. Coolant enters via a manifold below the throat,
  flows *forward* (counter to gas flow) to the throat, "providing the coolest fuel at the
  throat where wall heat flux is highest" — i.e. countercurrent cooling routed so coldest
  coolant meets hottest wall station, an explicit real-engine design rationale for
  `topics/06-cooling-and-heat-transfer.md`'s flow-topology discussion.
- Acoustic stability cavity: a machined coolant-exit-manifold cavity connected to the
  combustion chamber through small tubes pressed/swaged between the Haynes 230 tubes
  before brazing, with a minimal coolant bleed purging the cavity to prevent hot-gas
  ingestion `[leaf 320]` — a real "acoustic-tube-through-cooling-tube-bank" liner
  construction method, distinct from `[Sutton]`'s generic Helmholtz-cavity description.
- Cooling design guidelines (750K lbf SL, 896 psia Pc design point) `[leaf 321]`: max
  stress <0.2% yield, ultimate tube temperature margin ≥375 R, coolant Mach ≤0.5. Methane
  enters at 241 R/5315 psia, exits at 626 R/3975 psia; max predicted hot-wall temperature
  2170 R, max heat flux 21 Btu/in²-sec; max coolant Mach only 0.2 (well under the 0.5
  design limit) `[leaf 321, 323]`.
- **Real turbopump performance tables at both power levels** `[leaf 335, 337, Tables
  4.2.2.6-3/-4]` — CH4 turbopump: 2-stage centrifugal pump, turbine efficiency (T/T) 0.867
  (NPL)/0.883 (DPL), pump-stage efficiencies 0.787/0.594 (stage 1/2) at NPL rising to
  0.780/0.584 at DPL, speed 9689/11409 rpm, suction specific speed 1351/1355 (stage 1),
  head coefficient 0.504-0.624, turbine pressure ratio (T/T) 1.90 (NPL)/2.11 (DPL). O2
  turbopump: single-stage centrifugal, turbine efficiency (T/T) 0.875/0.877, pump
  efficiency 0.795/0.796, speed 4054/5134 rpm, suction specific speed 1384/1396, turbine
  PR (T/T) 1.29/1.46. **A real, complete, per-stage Ns/efficiency/head-coefficient/tip-
  speed dataset for an expander-class turbopump at two power levels** — directly useful
  for `topics/09-turbopumps.md`'s and `turbopump_efficiency.py`'s Ns-vs-efficiency curve
  cross-check (this is an *expander-cycle* pump, lower turbine PR/available power than a
  GG or staged-combustion pump, consistent with the cycle's known lower feed pressures).

## Key results — Gas Generator cycle engines (three variants, all LOX/CH4, plus one LOX/RP-1)

**Derivative STBE GG** (STME-derivative) `[leaf 35, Fig 4.1.1.1-1]`: MR 2.7, Pc 2250
psia, thrust vac/SL 711,823/644,898 lbf, Isp vac/SL 328.4/297.5 s, eps 28, dia 91 in,
length 99 in, weight 6960 lb. GG gas conditions 1688 psia/1800 R `[leaf 38]`. Common
hardware with STME (§4.1.1.2, Table 4.1.1.2-2, `leaf 36`): turbomachinery flow-path
castings/bearings/seals, GG injector/chamber/liner, tubular nozzle, main injector,
80% of ducting — **items redesigned for the booster-specific derivative**: combustion
chamber, oxidizer pump, oxidizer turbine, fuel turbine, GG valves, gimbal. This is a
real "engine family / hardware commonality" case study — a data point for how much of a
turbopump-class engine redesign is genuinely propellant/thrust-class-specific vs.
reusable across a family, relevant to any future `engine_designer` "derivative engine"
feature discussion.

**Oxidizer turbopump (DGGOT)** materials and real bearing DN data `[leaf 40-41,43-44]`:
rotating thrust piston forged Inconel 718 vs. stationary Bearium B-10 (leaded bronze)
insert; ball bearing DN 0.88×10⁶, roller bearing DN 1.06×10⁶ (LOX-side). Critical-speed
summary: pump pitch mode at 99% design speed (7016 rpm), turbine bounce at 199% (14,556
rpm), 1st bending at 740% design speed (95.5% rotor strain energy) — i.e. the rotor is
run well subcritical of its fundamental bending mode by design (>6× design speed margin,
vs. the report's own >20%-margin design goal stated elsewhere).

**Fuel turbopump (DGGFT)** materials `[leaf 41]`: pump impeller Titanium; turbine
disk/shaft Super A-286; turbine blades and vanes MAR-M-247; housings Inco 718, MAR-M-247,
and Haynes 230. Ball/roller bearing DN 0.64×10⁶/0.78×10⁶ (fuel side — lower than the LOX
side's 0.88/1.06×10⁶, consistent with `[SP-8048]`'s already-noted DN-vs-lubricity
ranking, and a second independent real-engine DN data point beyond that source's fleet
table). Fundamental bending mode pushed to 149% above design speed (subcritical rotor
design goal, distinct from the oxidizer pump's supercritical-with-large-margin approach)
`[leaf 44]`.

**Unique STBE GG** (clean-sheet 750 Klbf) combustor/injector table `[leaf 159, Table
4.1.2.4-1]`: chamber L* (min) 31.3 in (the minimum meeting a stated **98.0%
characteristic-velocity efficiency target** — a real, explicit c*-efficiency design
criterion, not just an assumed value), fuel flow 502.1 lb/s, ΔP_fuel 168.0 psi, LOX flow
1816.3 lb/s, ΔP_LOX 167.3 psi, 395 injector elements, element ID 0.366 in, annular gap
0.021 in. Throat dia 15.04 in, injector dia 23.79 in, contraction ratio 2.5 `[leaf 161]`.
Acoustic liner design (Table 4.1.2.4-2, `leaf 159`): 30% acoustic absorption at the first
tangential mode frequency (1212 Hz), aperture gas temp 2000 R, aperture gas MW 22.4,
hole diameter 0.10 in, hole length 0.35 in, open area ratio 0.05, backing cavity depth
0.6 in, liner length 4.0 in — a complete real Helmholtz-liner geometry, useful cross-check
for `topics/14-combustion-stability.md`'s Helmholtz-cavity-aid sizing (currently backed
mainly by `[NASA-TN-Acoustic]`'s parametric data — this is a real applied design point).

Milled-channel chamber cooling design guidelines (Unique STBE GG thrust chamber) `[leaf
161]`: liner wall thickness ≥0.35 in, passage aspect ratio ≤5.0, passage land width
≥0.050 in, cooling enhancement claimed from passage curvature, coolant Mach ≤0.5. The
**same four guidelines (aspect ratio ≤5.0, land width ≥0.050 in, coolant Mach ≤0.5, wall-
temp/stress margins) recur essentially unchanged across every engine variant in this
report** (Derivative GG, Unique GG, Tap-Off) — i.e. these read as P&W in-house standard
regen-channel design rules of the era, not case-specific results; a strong candidate
citation for any `cooling.py` channel-geometry sanity-check limits.

**Unique LOX/RP-1 GG engine** `[leaf 231, Fig 4.1.4.1-1]`: MR 2.75, Pc 1500 psia, thrust
vac/SL 863,191/750,000 lbf, Isp vac/SL 316.0/274.6 s, eps 25, dia 99 in, length 149 in.
Fuel-side split: RP-1 pump at 8524 rpm to 2283 psia; **72.0% of RP-1 flow regen-cools the
milled-channel copper-alloy chamber** (eps 3.28 back to injector face), remainder cools
the tubular stainless-steel nozzle (eps 3.28 down to eps 7.85) then the GG `[leaf 233]`.
Oxidizer pump at 5645 rpm to 2091 psia; GG gas 1400 psia/1800 R. Full engine-balance
performance table at DPL/NPL (`[leaf 242]`, Tables 4.1.4.5-1/-2): main chamber Pc 1501.2
psia (DPL)/1291.9 psia (NPL), MR 3.12 (DPL, main-chamber-only, vs. 2.75 overall engine MR
— i.e. **the main-chamber MR runs richer-oxidizer than the overall engine MR because the
GG leg is fuel-rich** at MR 0.114/0.118), ideal Isp 345.4/345.9 s dropping to delivered
322.1/322.6 s vacuum after ERE/KIN/TDK/BLM loss breakdown (a real, fully-itemized
frozen-vs-shifting/kinetics/boundary-layer Isp loss stack, directly comparable in kind to
`[Sutton]`'s efficiency-factor framework in `topics/03-combustion-and-cstar.md`) — a full
JANNAF-standard station-by-station engine-balance printout (pump inlet/exit, valve
inlets/exits, injector-inlet pressure/temp/flow/enthalpy/density) is also reproduced
verbatim in the source at `[leaf 245-248]` for anyone needing a real complete GG-cycle
mass/energy balance to validate against.

## Key results — Tap-Off cycle engine (real LOX/CH4 tap-off, distinct from J-2S's LOX/LH2)

Unique STBE Tap-Off, 750 Klbf SL thrust, Pc 2400 psia, MR (overall) 3.5 `[leaf 341-344,
Tables 4.3.1-2/4.3.2-1]`: throat area 178.9 in², injector flow rate 2462 lbm/s, throat
flow rate 2329 lbm/s, **tap-off flow rate 132 lbm/s — i.e. ~5.4% of injector flow is
tapped off the main chamber near the throat to drive the turbines**, eps 35. Coolant
(methane, full-flow, counterflow through both nozzle tube bank and chamber machined
passages, discharging into the injector) enters at 239 R/5055 psia, exits at 450 R/2607
psia (ΔP 2448 psid, ΔT 211 R, total heat pickup 97,342 Btu/s). Same cooling-guideline set
as the GG engines (liner wall ≥0.030 in for the machined-passage chamber leg, ≥0.013 in
for the tube-wall nozzle leg, aspect ratio ≤5.0, land width ≥0.050 in, coolant Mach ≤0.5,
tube stress <0.2% yield, ultimate temp margin ≥375 R) `[leaf 341]`. Control valves: fuel
bypass valve (FBV), hot-gas valve (HGV), main oxidizer valve (MOV) set thrust/MR
open-loop `[leaf 340]`. Start sequence uses the same oxidizer-lead philosophy as the GG
engines (LOX injector primed before fuel valve opens) `[leaf 340]`; continuous-burning
torch igniter development lineage traced to 1957 P&W work, used on RL10 and XLR-129
`[leaf 321]` (a real historical igniter-heritage note).

This **tap-off fraction (~5.4% of injector/throat flow) is a second real data point**
alongside `[AEDC-J2S]`'s J-2S tap-off hardware numbers already in `topics/08-engine-
cycles.md`, and for a *different* propellant pair (LOX/CH4 vs. LOX/LH2) — useful if
`engine_designer`'s tap-off cycle model ever needs a hydrocarbon-fuel anchor rather than
only a hydrogen one.

## Key results — GOX heat exchanger (tank pressurization) real hardware

Split-expander-engine GOX heat exchanger `[leaf 329]`: 5× Haynes 214 stainless steel
tubes (3/8 in dia, 0.015 in wall, 42.5 ft long each) wrapped in parallel around a
7-inch beryllium-copper exhaust duct with trip-strip roughened walls, tubes packed in
powdered copper for structural isolation while retaining thermal contact — explicitly
to "eliminate a category 1 failure mode" (accidental O2/hot-gas mixing). Sized for 10.1
lbm/s O2 flow, heated to 400 R for tank pressurization. A real, fully-dimensioned
propellant-tank-pressurization heat-exchanger design, not previously represented in this
reference set (no existing topic file covers pressurization-system hardware in this much
detail) — flagged here in case a future `engine_designer` feature ever touches
autogenous-pressurization heat exchangers.

## Section map

**Front matter** (leaves 0-23): title page, table of contents, list of illustrations
(multiple pages), list of tables, foreword, introduction, overall study approach — read
in full (short, orients the whole document's structure; no bookmarked PDF TOC exists so
this was necessary).

**§1.0 Evolution of STBE During Phase A** (leaves 24-29): candidate-configuration trade
table (Table 1-1), trajectory/programmatic ground rules, tripropellant→bipropellant→
split-expander→derivative-STBE narrative, methane-vs-RP-1/propane rationale (Table 1-4)
— read in full.

**§2.0 Engine Requirements and Configurations** (leaf 30): one-paragraph pointer to a
separate interim report (FR-19691-1) that is NOT in this PDF — the requirements/
configuration *derivation* work isn't reproduced here, only its *results* in §1 and §4.
Read in full (it's one paragraph).

**§3.0 Configuration Evaluation and Selection Criteria** (leaves 32-33): same — a
one-paragraph pointer to FR-19691-1 for the LCC evaluation methodology detail. Skimmed
(confirmed there's no additional technical content, only a pointer).

**§4.0 Design Definition of Selected Engine Configurations** (leaves 34-332, the bulk of
the document): **deep-read**, selectively:
- §4.1.1 Derivative GG (leaves 34-49): engine design conditions, cycle description,
  flowpath, engine operation/start sequence, oxidizer + fuel turbopump hardware/
  materials/bearing-DN/rotordynamics — read in full.
- §4.1.2 Unique GG (leaves 137-161+): turbopump trade figures (multiple boost-pump
  configuration variants — diameter/speed schematics only, not deep-read individually),
  combustor/injector design table, acoustic liner table, main injector/chamber
  construction, cooling design guidelines — read in full for the tables/guidelines,
  skimmed the boost-pump-configuration-comparison figures (schematic dimension call-outs
  only, no new design *method*, just trade-study geometry sketches).
- §4.1.3 Common GG (leaves ~195-230): flowpath narrative, cost section header — skimmed;
  did not deep-read the STME/STBE hardware-commonality-evaluation tables in full (lower
  priority — this variant's hardware is a subset of what §4.1.1/4.1.2 already cover).
- §4.1.4 Unique LOX/RP-1 GG (leaves 231-249): design conditions, cycle/flowpath
  description, full DPL/NPL engine-balance performance tables (component-level, station-
  by-station) — read in full.
- §4.2.1 Derivative Split Expander (leaves 250-283): design conditions vs. STME baseline,
  cycle description, turbopump critical-speed summary, combustor/injector table, nozzle
  tube-geometry/cooling-performance table, controls/valve-sequencing description — read
  in full.
- §4.2.2 Unique Split Expander (leaves 283-338): design conditions, turbopump hardware
  description (mechanically identical to §4.1.1's, per the text), combustor/injector
  table, chamber tube-bank/acoustic-cavity construction, cooling guidelines/performance,
  GOX heat exchanger, full turbopump performance tables (both power levels, per-stage
  Ns/efficiency/head-coefficient data) — read in full.
- §4.3 Unique Tap-Off (leaves 283 [cycle intro, interleaved with §4.2.2 numbering in the
  PDF], 339-344): engine operation/start sequence, cooling design guidelines/performance,
  cost-section header, full cycle performance table — read in full for the technical
  content, skimmed the cost paragraph.

**§5.0 STBE Programmatic Analyses and Plans** (leaves ~332-392, not individually opened
beyond confirming via the ToC that it is logic networks / schedules / facility interface
requirements / environmental impact analysis): **skipped entirely** — pure program-
management content, explicitly out of scope per this task's framing (skim/skip
programmatic-cost-schedule sections).

**Not read at all**: Volume I (Executive Summary) and Volume III (Program Cost
Estimates) are referenced by this document but are separate PDF volumes not present in
`literature/` — nothing to read.

## Design method

This is a preliminary-design *report*, not a design-criteria monograph like `[Huzel]` or
`[SP-8087]` — it applies standard methods (JANNAF-standard performance prediction chain:
1-D equilibrium → bell-nozzle method-of-characteristics → 1-D kinetics → 2-D equilibrium →
boundary-layer-loss program → engine steady-state balance, shown schematically at `[leaf
343, Fig 4.3.2-1]`) rather than deriving new ones. Its value here is entirely **real,
fully-worked conceptual-design data points across several engine cycles/propellants at a
consistent thrust class and design philosophy**, plus a handful of explicit, stated
design rules that recur across all the variants (the cooling-channel geometry guideline
set noted above) which read as period P&W in-house design practice even though the report
never cites them to an external standard.

## Caveats

- **OCR quality is uneven and table-heavy pages are the worst-affected.** Numeric tables
  in particular (e.g. the LOX/RP-1 GG engine-balance printout at `[leaf 245]`) show
  digit-substitution errors throughout (e.g. "IST" for "1ST", stray periods/commas in
  numbers). Every number quoted above was cross-checked for internal consistency (e.g.
  vacuum thrust ≈ Isp × flow rate) where the components were legible, but treat any single
  isolated figure with the same caution `[Gubanov-1991]`'s note recommends for this kind
  of OCR-scanned report.
- **No PDF bookmarks/TOC** — navigation relied on the printed front-matter ToC (leaves
  8-19) plus text search; the leaf-number page-citation convention above should be used
  to re-locate any passage rather than the document's own (partially garbled, non-
  monotonic-looking-in-OCR) printed page numbers.
- **§4.1.3 (Common GG engine) was only skimmed, not deep-read** — if a future need arises
  specifically for the STME/STBE common-hardware trade-off numbers (cost/weight penalty
  of forcing one engine design to serve both the H2/O2 core vehicle and the CH4/O2
  booster), leaves ~195-230 should be read in full; this note only captures the
  §4.2.1.1-adjacent side-by-side STME-vs-Derivative-STBE table at `[leaf 250]`, not the
  dedicated §4.1.3 common-engine section.
- **§5.0 (programmatic/cost/schedule) was not opened at all** beyond the front-matter
  ToC — if program-cost numbers are ever wanted (DDT&E cost, TFU production cost,
  operations cost — brief examples appear incidentally in §4's per-engine cost
  subsections, e.g. Tap-Off DDT&E $1400M / TFU $11.1M / ops $0.155M per flight-engine at
  `[leaf 342]`), those numbers are scattered through §4's "Engine Costs" subsections
  (already partially captured above where encountered) rather than needing §5 itself.
- **All designs are 1986-1989 vintage conceptual/preliminary designs, never built or
  flown.** None of these STBE engines exist as hardware — treat every number as a design-
  point *target*, not a demonstrated/flight-proven value, unlike `[NK-33-Mod]`,
  `[Gubanov-1991]`, `[AEDC-J2S]`, or `[J2X-Overview]`'s real flown/tested engines.
- **The "split expander" cycle name is P&W-specific** to this report's usage; do not
  confuse with a generic "split flow" description elsewhere — the definition quoted above
  (leaves 28-29) is this document's own and should be cited precisely if used.
- Component material choices (Inconel 718, Waspaloy, MAR-M-247, Super A-286, Titanium,
  Haynes 230, 440C bearings, Bearium B-10) are all **late-1980s P&W turbopump/chamber
  material selections for a specific thrust/Pc class** — consistent in kind with, but not
  cross-validated against, `[Ch12-Materials]`'s broader survey; worth a targeted
  cross-check if either source's alloy choice for a given component ever needs
  corroboration.
