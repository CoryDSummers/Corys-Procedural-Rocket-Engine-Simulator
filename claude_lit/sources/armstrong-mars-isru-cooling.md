# NASA TM-103729 — Cooling of In-Situ Propellant Rocket Engines for Mars Missions

## Identity

Elizabeth S. Armstrong (NASA Lewis Research Center), *Cooling of In-Situ Propellant Rocket
Engines for Mars Missions*, NASA Technical Memorandum 103729, January 1991 ("corrected
copy"). `literature/NASA TM-103729 - Cooling of In-Situ Propellant Rocket Engines for Mars
Missions.pdf` (NTRS accession **19910011920**; 98 PDF leaves, clean machine-quality OCR
throughout — no OCR-garbling caveat needed for this source, unlike several older scanned
NASA CRs already in `claude_lit`; printed page N = PDF leaf N+8, e.g. printed p.1 = leaf 9).
Tag: **`[Armstrong-MarsISRU]`**.

## Character

A parametric analytical cooling-trade STUDY, not a design-criteria monograph or a firing-
hardware report: it compares two candidate regenerative coolants — supercritical **carbon
monoxide** and supercritical **oxygen** — for a hypothetical high-pressure, pump-fed rocket
engine burning **CO/O2 propellants derived in-situ from Martian-atmosphere CO2** (via
zirconia-electrolyte dissociation), sized for a three-engine Mars ascent/descent vehicle.
Neither propellant, nor CO/O2 combustion, appears anywhere in `engine_designer/physics/
combustion.py`'s propellant-pair tables, and **no CO/O2 rocket engine has ever been built or
fired** — every combustion/Isp/heat-flux number in this report is a CEC (chemical-equilibrium)
computation, not a measurement. Flagged per the task brief: **this source's core subject
matter (CO/O2 propellant chemistry) does not map onto anything `engine_designer` currently
models**, and should not motivate adding a CO/O2 propellant pair on its own.

However, the paper's *method* is a real 1-D thermal/hydraulic parametric-optimization study
using REHTEP (Rocket Engine Heat Transfer Evaluation Program, a NASA-Lewis in-house code
coupling the CEC equilibrium-composition program for hot-gas-side properties with a "FLUID"
program for coolant properties), and it is validated — for regenerative cooling generally,
not for CO/O2 specifically — against **real LOX/RP-1 hot-fire thermocouple data**. That
validation step, plus a catalog of supercritical-fluid Nusselt-number correlations and a set
of generic coolant-channel-geometry design heuristics, is the transferable content; the
Mars-mission framing (huge vacuum-optimized area ratios, ISRU propellant production,
mission delta-V) is background only.

Structure: Abstract, Nomenclature, Ch.I Introduction, Ch.II Background (Mars-mission
context), Ch.III Thermophysical Properties of O2 and CO (property-curve comparison),
Ch.IV Heat Transfer Correlations for O2 and CO, Ch.V Thrust Chamber Contour Optimization,
Ch.VI Rocket Engine Heat Transfer Evaluation Program (REHTEP description + real-hardware
validation), Ch.VII Coolant Channel Geometry Optimization, Ch.VIII Discussion of Results,
Ch.IX Conclusions, Appendix A (thermophysical property tables), References.

## This note's extraction scope (98 pages)

**Read in full**: Abstract, Nomenclature (skimmed for unit definitions only), Ch.I
Introduction (p.1-5), Ch.IV Heat Transfer Correlations (p.23-28 — the correlation catalog,
genuinely transferable), Ch.VI REHTEP description + real LOX/RP-1 validation (p.39-45 — the
one real-hardware anchor in the document), Ch.VII Coolant Channel Geometry Optimization
(p.46-58 — the generic channel-geometry heuristics), Ch.VIII Discussion of Results (p.59-69),
Ch.IX Conclusions (p.70-72).

**Skimmed only (Mars-mission-specific background, no transferable design constants)**: Ch.II
Background (p.6-10 — ISRU production chemistry, mission delta-V, vehicle mass budget — pure
context, not cited below), Ch.III Thermophysical Properties (p.11-22 — CO-vs-O2 density/
viscosity/conductivity/cp/Pr curve comparisons; conclusion "cannot determine explicitly which
fluid is the better coolant from properties alone" noted but the curves themselves not
digitized), Ch.V Thrust Chamber Contour Optimization (p.29-38 — Rao-method nozzle contours
at area ratios 200/600/1200, driven entirely by the Martian-surface near-vacuum ambient
pressure of 689 Pa/0.1 psi; zero applicability to any earth-launched or `Engine_Configs/`
engine, not cited below).

**Not digitized**: Appendix A (p.73-86, ~14 pages of raw CO/O2 thermophysical-property data
tables at multiple pressures — pure numeric tables for two propellants `engine_designer`
doesn't model; skip unless a future CO- or O2-as-coolant feature is ever added). References
(p.87-98, titles not chased). Figures 25-32 (pressure-drop-vs-wall-temperature Pareto plots
for the channel-geometry parametric sweep) were read only via their OCR'd axis text and the
companion result tables (Tables VII-XI, which give the same numbers as clean text) — no
image rendering was needed or done; the specific optimum-configuration numbers quoted below
come from those text tables, not from digitizing the plots.

## Parameters — the paper's own engine/mission design point

| Parameter | Value |
|---|---|
| Propellants | CO (fuel) / O2 (oxidizer), both from Mars-atmosphere CO2 electrolysis (ISRU) |
| Mixture ratio (O/F) | 0.500 (vs. stoichiometric 0.571) |
| Chamber pressure | 22.0-22.1 MPa (3200 psia) |
| Thrust | 3 engines x 445 kN (100,000 lbf) |
| Vacuum Isp | 245-320 s (area-ratio dependent at MR 0.5) |
| Engine cycle | Gas generator (staged combustion also Pc-feasible at 22 MPa but rejected — "to limit the complexity of the system") |
| Design ambient back pressure | 689 Pa (0.1 psi) — Martian surface |
| Candidate exit area ratios evaluated | 200 / 600 / 1200 (huge — driven by near-vacuum ambient) |
| Max coolant inlet pressure | 42.0 MPa (6090 psia) — assumed "turn-of-the-century" turbopump capability |
| **Real anchor**: SSME coolant inlet pressure | 41.2 MPa (5978 psia) |
| Min coolant exit pressure | 25.4 MPa (3685-3690 psia) — Pc x ~1.15 injector-dP margin |
| Injector pressure drop (stability requirement) | 15% of Pc |
| Copper/copper-alloy hot-gas wall elastic-region limit | 778 K (1400 R) |
| Available coolant fraction of total flow | O2: 50.97/152.9 kg/s (33%); CO: 101.9/152.9 kg/s (67%) — MR 0.5 makes CO the much larger coolant reservoir |

## Key results

**A catalog of supercritical-fluid Nusselt-number correlations — the most transferable
content in this source** `[Armstrong-MarsISRU Ch.IV p.24-27]`: this file's existing single
Dittus-Boelter citation (`Nu = 0.023 Re^0.8 Pr^0.4`, `[Huzel eq. 4-12]`) is joined here by a
real, cited family of variable-property/supercritical corrections not previously in
`claude_lit`:
- **Petukhov** (ref. 22): `Nu0 = (f/8)·Re·Pr / [1.07 + 12.7·(f/8)^0.5·(Pr^0.667 - 1)]`, valid
  Pr 0.5-2000, Re 1e4-5e6, correlates results within ±10%; friction factor
  `f = (1.82·log10(Re) - 1.64)^-2`.
- **Notter & Sleicher** (ref. 25): `Nu0 = 5 + 0.015·Re^a·Pr^b`, `a = 0.88 - 0.24/(4+Pr)`,
  `b = 1/3 + 0.5·e^(-0.6·Pr)`, valid Pr 0.1-1e4, Re 1e4-1e6, within ±10% — the paper notes
  this and Petukhov's form agree with each other within 9%, i.e. two independent
  correlations cross-validate for constant-property supercritical flow.
- **Sieder & Tate** (ref. 26) viscosity-ratio variable-property correction:
  `Nu = 0.023·Reb^0.8·Prb^0.33·(μb/μw)^0.14`.
  **Petukhov's own variable-property correction**: `Nu = Nu0·(μb/μw)^n`, `n = 0.11` for
  heating, `0.25` for cooling.
- **Nusselt entrance-effect correction** (ref. 27): `Nu = 0.036·Re^0.8·Pr^0.33·(d/L)^0.55`;
  alternative entrance-effect forms from Spencer & Rousar (ref. 28): `1 + 2/(L/d)`,
  `1 + (A-d)/L`, `2.88/(L/d)^0.31`.
- **A "generalized" supercritical correlation** (refs. 29-31, eq. 4.8a/b) — originally
  developed and validated for **hydrogen** (matches 95% of available H2 data within ±20%)
  and separately validated against **supercritical methane** data (ref. 30) — a Nu0·φcur·
  φf·φr product form with explicit curvature (`R` = tube radius of curvature), entrance
  (`x/(L+15d)`), and roughness terms. The paper applies this correlation to **carbon
  monoxide by analogy** (Pr range 0.6-100 covers CO), explicitly because "no experimental
  data is available" for CO — this is the single most important caveat in the source (see
  Caveats below): the CO heat-transfer prediction throughout this report rests on an
  unvalidated cross-fluid analogy, a fact the authors themselves flag and recommend
  resolving with future heated-tube tests.
- **For oxygen specifically**, Spencer & Rousar's own dedicated correlation (ref. 28,
  eq. 4.12): `Nu = 0.0025·Ref^0.8·Prf^-0.75·(μb/μw)^0.6·(ρb/ρw)^-0.15` — built from 26
  candidate forms tested against real supercritical-O2 electrically-heated-tube data,
  matches >95% of test data within ±30%, **validated over 17-34 MPa and T>100K** — directly
  overlapping the paper's own 22-42 MPa design coolant-pressure range. This is the
  correlation actually used for the O2-cooling analysis (chosen over the generic form
  because it has real supercritical-O2 experimental backing).

**REHTEP validated against real LOX/RP-1 (kerosene) hot-fire data — the one real-engine
anchor in this document** `[Armstrong-MarsISRU Ch.VI p.41-44]`: at the NASA-Lewis Rocket
Engine Test Facility (Stand A), a **liquid-oxygen-cooled, copper, hydrocarbon-fueled
combustion chamber** (kerosene/LOX propellants) was hot-fired at two conditions — MR 2.2,
Pc 8.89 MPa (1290 psia) and MR 1.8, Pc 8.48 MPa (1230 psia) — with thermocouples at five
axial stations, four circumferential positions each. REHTEP's predicted hot-gas-side wall
temperatures matched the measured data within scatter, **once a soot-deposit layer
(0.025 mm / 0.001 in. at the first condition, 0.051 mm / 0.002 in. at the second, both
predicted by the separate SINDA thermal-network code from prior soot-thickness
measurements) was included on the hot-gas wall** — without the soot layer the code
over-predicts the measured temperatures. Two things worth flagging for `engine_designer`:
(1) this is a real, if narrow, precedent for **oxidizer-side (LOX) regenerative cooling of a
hydrocarbon-fueled copper chamber** — unusual relative to `engine_designer`'s implicit
fuel-side-cooling assumption for LOX/RP-1 configs, worth noting as a real-hardware existence
proof even though it's not itself a flight engine; (2) it is a second, independent
real-firing corroboration (distinct rig, distinct authors) that a **soot/deposit layer on
the order of tenths of a millimeter measurably changes predicted RP-1/LOX wall temperature**
— consistent in kind (not magnitude, these are much thinner than the microgram/cm² buildup
studied in `[Lewis-Deposits]`) with the coking-layer thermal-resistance theme already in
`topics/06`.

**Coolant-channel-geometry design heuristics — generic, not CO/O2-specific** `[Armstrong-
MarsISRU Ch.VII p.47-58]`:
- **Height-to-width aspect ratio**: for BOTH coolants, the pressure-drop-vs-wall-temperature
  Pareto front bottoms out at an aspect ratio of **7.5-8** (the paper's own stated practical
  ceiling): "the height-to-width ratio... should be kept below eight," with the heat-transfer
  benefit from increased surface area "starting to level out around an aspect ratio of six."
  This is framed as height/width (tall narrow channels); `[SP-8087]`'s existing citation in
  `topics/06` (width/height <2 typical, up to 8 "acceptable if height > 0.10 in") is the
  inverse framing but the same numeric ceiling of 8 — two independent NASA sources agreeing
  on an aspect-ratio-8 practical limit for milled/machined coolant channels, worth citing as
  mutual corroboration even though the ratio convention differs.
- **Land width (distance between adjacent coolant channels) should be kept roughly equal to
  channel width**: too-thin a land under-supports the hot-gas wall against pressure loads;
  too-wide a land increases the local thermal gradient and risks wall deformation. Stated
  qualitatively only — no dimensioned formula, a "roughly equal to" heuristic.
  A related, more explicit numeric guideline exists in `[Merkle-RegenCFD]`'s recommendation
  set (`topics/06 p.424`: land width >= 0.050 in) — this source doesn't contradict that, it
  just states the ratio-to-channel-width version of the same idea rather than an absolute
  minimum.
- **Channel count may only change by integer bifurcation factors** (2x, 3x, 4x, ...) along
  the chamber/nozzle contour, since continuously varying channel count is impractical to
  manufacture: "the total number of cooling channels should only increase or decrease by
  factors of integers." This is the milled/machined-channel-wall analog of `[SP-8120]`'s
  tube-splice-joint bifurcation concept for tube walls (different construction, same
  underlying manufacturing constraint) — both wall-construction families hit the same "a
  fixed passage count can't be tapered indefinitely" wall.
- **REHTEP optimum configurations found** (illustrative numbers, not directly transferable
  since they're CO/O2-at-22MPa-specific, but show the method's output shape): O2-cooling
  optimum at the throat — AR=8, width 0.594 mm, 292 channels, giving 9.11 MPa pressure drop
  at 702 K peak wall temp (max available O2 flow, 50.97 kg/s); CO-cooling optimum at the
  throat — AR=7.5, width 0.991 mm, 175 channels, giving 7.96 MPa pressure drop at only 581 K
  peak wall temp (max available CO flow, 101.9 kg/s). **Headline comparative finding**: at
  matched wall temperature, optimized CO cooling gives roughly a **threefold lower pressure
  drop than optimized O2 cooling** — attributed to CO's larger available coolant mass
  fraction (MR 0.5 means twice as much CO as O2 by mass) and its higher specific heat, not
  a fundamentally different heat-transfer mechanism. This particular comparison has zero
  transfer value to `engine_designer` (neither fluid is a modeled propellant), but the
  METHOD — parametrically sweep aspect ratio and channel width against a fixed pressure-drop
  budget and wall-temperature ceiling to find a Pareto-optimal channel geometry — is a real,
  reusable design-optimization pattern.

**Copper wall-temperature elastic-region limit, an independent corroboration** `[Armstrong-
MarsISRU Ch.VII p.47]`: "to keep a copper or copper-alloy chamber in its elastic region, the
hot-gas-side wall temperature should be kept below **778 K (1400 R)**." This sits close to
but is a distinct, independently-derived number from the **811 K (1000°F)** copper gas-side
max already cited from `[Wieseneck-J2]` in `topics/06` (different source, different author,
different decade) — the two values agree within ~4% (33 K), reasonable independent
corroboration of "copper chambers need to stay under roughly 780-810 K on the gas side to
avoid plastic deformation," not a contradiction.

**Injector pressure-drop-for-stability rule, an independent corroboration**: "a 15% pressure
drop is necessary across the injector" to ensure stable combustion `[Armstrong-MarsISRU
Ch.I p.3]`, restated as the coolant-exit-pressure constraint in Ch.VII. This is a real,
independent (uncited-derivation) restatement of the same 15-20% injector-dP-for-stability
rule already established in `claude_lit`'s injector reference — one more source landing in
the same band.

**Radiation-cooling cutoff location — engine-specific, not directly transferable**
`[Armstrong-MarsISRU Ch.VII p.47]`: for this specific engine's contour, radiation cooling
alone (no coolant) suffices beyond area ratio 16.57 (19.41 cm from the throat) — inside but
close to the upper end of `[Sutton]`'s general "area ratio 6-10" regen-to-radiation
transition range already cited in `topics/06`. Because this engine's overall nozzle runs to
area ratios of 200-2000 (a Mars-vacuum artifact), a transition at eps=16.57 is a small
fraction of the total nozzle length — not inconsistent with Sutton's rule, but not a new
data point worth citing as a design constant since it's this engine's own bespoke result,
not a general finding independently derived here.

## Design method

Not a source of new closed-form combustion or nozzle-contour equations (CEC equilibrium
chemistry + the Rao method of optimization are used exactly as already documented elsewhere
in `claude_lit`, with no new derivation). The REHTEP thermal/hydraulic march itself is
described only at the level of its two explicit pressure-loss equations — friction
(`f.p.l. = f·(avg ρ)·(avg V)²·Δx / (2·gc·avg d)`, `f = 4·(0.004 + 0.125/Re^0.32)`) and
momentum (`m.p.l. = (mdot/gc)²·[1/(ρ·A·N)|downstream - 1/(ρ·A·N)|upstream]`) — with the
actual hot-gas-side and coolant-side heat-transfer solve handled by referenced-but-not-
reproduced subroutines (CEC, FLUID). Treat this source's real design-method contribution as
(a) the Nusselt-correlation catalog above (reusable equations, fully given), and (b) the
generic channel-geometry-optimization *procedure* (parametrically sweep aspect ratio and
width against a fixed pressure-drop budget + wall-temperature ceiling), not as a source of
new sizing formulas for `engine_designer/physics/cooling/*`.

## Section map

- Abstract, Nomenclature: p.i-iv (leaf 1-5) — read.
- Ch.I Introduction: p.1-5 (leaf 9-13) — read in full; mission/engine framing + the
  15%-injector-dP and coolant-pressure-budget numbers above.
- Ch.II Background: p.6-10 (leaf 14-18) — skimmed; ISRU production chemistry and mission
  context only, not cited above.
- Ch.III Thermophysical Properties of O2 and CO: p.11-22 (leaf 19-30) — skimmed; property-
  curve comparison narrative only (density/viscosity/conductivity/cp/Pr), no digitized
  curves, conclusion ("cannot determine explicitly which is the better coolant from
  properties alone") noted but not independently cited as a design finding.
- Ch.IV Heat Transfer Correlations for O2 and CO: p.23-28 (leaf 31-36) — **read in full**,
  the correlation catalog above.
- Ch.V Thrust Chamber Contour Optimization: p.29-38 (leaf 37-46) — skimmed; Mars-vacuum-
  specific huge-area-ratio nozzle contours, not cited (zero engine_designer relevance).
- Ch.VI Rocket Engine Heat Transfer Evaluation Program: p.39-45 (leaf 47-53) — **read in
  full**, the REHTEP description + real LOX/RP-1 validation above.
- Ch.VII Coolant Channel Geometry Optimization: p.46-58 (leaf 54-66) — **read in full**, the
  channel-geometry heuristics + optimum-configuration tables above.
- Ch.VIII Discussion of Results: p.59-69 (leaf 67-77) — **read in full**, the CO-vs-O2
  overall comparison above.
- Ch.IX Conclusions: p.70-72 (leaf 78-80) — **read in full**.
- Appendix A Thermophysical Properties of CO and O2: p.73-86 (leaf 81-94) — not digitized;
  raw property-vs-temperature-and-pressure data tables for two unmodeled propellants.
- References: p.87-98 (leaf 95-98+) — not chased; titles not independently reviewed.

## Caveats

- **Propellant chemistry (CO/O2) does not map onto anything `engine_designer/physics/
  combustion.py` currently models** — no CO/O2 engine has ever flown or fired at scale; every
  combustion number in this report is a CEC computation, not a measurement. Do not use this
  source to justify adding a CO/O2 propellant pair without an independent literature check
  on real CO/O2 combustion behavior (flame speed, stability, completeness) this report
  doesn't address at all.
- **The carbon-monoxide heat-transfer correlation is an explicit, author-acknowledged
  analogy, not a validated result**: "since no experimental data is available [for CO], it
  is difficult to determine the best heat transfer correlation" — the H2/CH4-derived
  generalized correlation (eq. 4.8) is applied to CO purely because its functional form
  should, in principle, generalize to any supercritical Newtonian fluid in its stated Pr
  range. The paper's own conclusion explicitly calls for future heated-tube experiments
  before trusting this. Any CO-specific number in this source should be treated as
  unvalidated even by the source's own standard.
- **REHTEP's real-hardware validation is at a real but modest chamber pressure** (8.4-8.9
  MPa / ~1230-1290 psia) relative to the paper's own 22 MPa design point — the code is
  validated for regenerative cooling of a hydrocarbon/LOX chamber in general, not at the
  specific high-Pc condition the CO/O2 study actually explores.
- **The huge nozzle area ratios (200-2000) throughout Ch.V are a Mars-surface-ambient-
  pressure artifact** (689 Pa / 0.1 psi design back pressure) with zero applicability to any
  earth-launched or `Engine_Configs/`-catalog engine — none of those numbers should be
  treated as general nozzle-design guidance.
- **No new closed-form Bartz gas-side treatment** — hot-gas-side properties come from the
  CEC program (referenced, not reproduced); this source adds nothing to the gas-side
  heat-flux model `[Huzel eq. 4-13]`/`[Sutton]` already anchor in `topics/06`. Its
  contribution is entirely on the coolant (Nusselt-correlation) side and the channel-
  geometry-optimization procedure.
- **Clean OCR throughout** — unlike several older/lower-quality scans elsewhere in
  `claude_lit`, this 1991 TM's text extraction was unambiguous; no digit- or word-level
  cross-checking against rendered page images was needed for any number quoted above.
- Appendix A's ~14 pages of raw CO/O2 property tables were not transcribed — if a future
  session ever wants exact supercritical-CO or -O2 density/cp/k/mu/Pr values at specific
  (T, P) points, they exist there and would need a dedicated extraction pass.
