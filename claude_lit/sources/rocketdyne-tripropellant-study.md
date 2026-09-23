# Tripropellant Engine Study (Rocketdyne, NASA CR-150444)

## Identity

Rocketdyne Division of Rockwell International, *Tripropellant Engine Study, Bimonthly
Technical Progress Report No. 1*, NASA contract NAS8-32613, Rocketdyne report ASR77-213,
prepared for NASA Marshall Space Flight Center, 9 October 1977. D. B. Wheeler (Project
Engineer), F. M. Kirby (Program Manager). NASA CR-150444. `literature/NASA CR-150444 - Tripropellant Engine Study.pdf` (NTRS 19780002263)
(35 PDF leaves, ~34 numbered report pages). Tag: `[Tripropellant-CR150444]`.

## Character

An early-stage (first of presumably several bimonthly) NASA contractor progress report,
**not a final report or a design-criteria monograph** — it covers only the first ~5.5 weeks
(22 Aug-30 Sep 1977) of a planned 9-month study. Its subject is a **dual-mode/tripropellant
engine derived from Space Shuttle Main Engine (SSME) hardware**: an engine that burns
LOX/hydrocarbon (RP-1, CH4, or C3H8) in "Mode 1" then sequentially switches to LOX/H2 in
"Mode 2," explicitly to minimize new-hardware development cost for a dual-mode/SSTO-relevant
booster application by maximizing reuse of existing (1977-era, still-in-development) SSME
components. Content is preliminary: theoretical performance tables, turbine drive-gas
thermo data, chamber/nozzle cooling parametrics for candidate coolants, and 12-of-15
candidate engine-cycle power balances — no finalized engine design, no hardware test data
(this is analysis-only, pre-any-testing). Two prior related studies are cited as references
(`R-3909`/NAS8-4011, 1963; NASA CR-135141, Jan 1977) that this report builds on but that are
not themselves in `literature/`.

## Key results — dual-mode/tripropellant engine concept

**Core architecture concept** [p.1, p.3-4 (Introduction/Summary)]: A single thrust chamber
(built on SSME architecture) that burns **two different propellant combinations
sequentially, not simultaneously**, within one flight: "Mode 1" = LOX + a hydrocarbon fuel
(RP-1, CH4, or C3H8) for the high-thrust/high-density booster-type portion of flight, then
"Mode 2" = LOX/H2 for the high-Isp upper-stage-type portion — motivated by SSTO vehicle
studies showing this sequential-burn strategy beats either propellant combination alone for
a single-stage vehicle (dense propellant early to minimize tank/structure volume+mass at
liftoff, high-Isp LH2 later when vehicle mass is lower and Isp matters more). Two engine
classifications distinguished [p.21, "TASK III"]:
- **Series burn** (the primary configuration studied, and the one NASA's contract monitor
  explicitly asked Rocketdyne to prioritize [p.29]): the engine burns Mode 1 hydrocarbon
  propellants to completion, then transitions and burns Mode 2 LOX/H2 to completion — true
  sequential dual-mode operation, the "tripropellant" case (LOX + hydrocarbon + H2 all used
  across the mission, never LOX+hydrocarbon+H2 simultaneously in the chamber).
- **Parallel burn**: does NOT require sequential switching of fuels; instead the *second*
  fuel (H2) is used continuously, from the start, purely **as a coolant** — routed through
  the regen jacket and then dumped/burned — to compensate for a primary hydrocarbon fuel's
  inadequate cooling capacity, while the *primary combustion* stays on the hydrocarbon
  throughout. Described as "actually a simplified version of the dual mode engine," and the
  single-mode engines derivable as a subset of the dual-mode engine formulations.

**Why hydrocarbon-only cooling is the limiting factor, not combustion itself** [p.16
"Hydrocarbon Fuel Cooling," p.6 Summary]: This is the single most load-bearing finding for
why a *tripropellant* engine (not just a two-mode switchable one) is attractive: **RP-1 as
sole regen coolant limits Pc to ~2000 psia** because of coolant bulk-temperature-rise limits
and resultant coking at ~600°F (cited from a 1963 predecessor study, Ref. 1). At the SSME's
actual chamber pressure (~3237-4000 psia in this study), RP-1 alone cannot survive as
regen coolant. CH4 and C3H8 were found cooling-feasible at full SSME-class Pc. **This is why
H2 gets injected into Mode-1 combustion at all** in some cycle variants: not for its
performance, but so a hydrocarbon-fueled high-Pc SSME-derived chamber can still be
adequately regen-cooled — i.e. the tripropellant concept is as much a **cooling-capability
workaround** as a performance optimization. (This directly matches `engine_designer`'s own
finding, in `physics/cooling.py`, that regen-cooling margin is propellant- and
Pc-dependent — RP-1's low thermal conductivity/coking limit is a real, citable constraint
this source corroborates from a completely independent 1977 source.)

**Delivered-performance efficiency assumptions used** [p.6]: η_c* = 0.98, η_CF = 0.9859 for
LOX/hydrocarbon combinations; η_c* = 0.9915, η_CF = 0.9859 for LOX/H2 — real Rocketdyne
engineering-judgment efficiency factors for this era/class of high-Pc engine, usable as a
loose cross-check against `engine_designer`'s own `eta_cstar` defaults for the LOX/RP-1 and
LOX/H2 propellant pairs (not independently derived here, just Rocketdyne's assumed values
for this concept study).

## Key results — real performance/Pc/MR numbers

**Theoretical performance table** (Table 1, [p.6]), Pc = 3000 psia, ε = 35:1, MR chosen for
peak Isp:

| Propellants | Fuel density (lb/ft³) | Optimal MR | Isp SL (s) | Isp vac (s) |
|---|---|---|---|---|
| O2/H2 | 4.4 | 6.0 | 410 | 450.4 |
| O2/RP-1 | 50.0 | 2.8 | 328 | 358 |
| O2/CH4 | 26.4 | 3.5 | 335.3 | 368 |
| O2/C3H8 | 36.6 | 3.0 | 331.3 | ~353* |

(*OCR-garbled digit on the last Isp-vac entry, "331. Y3" in raw text — table transcribed as
best-legible; treat the O2/C3H8 vac-Isp figure as approximate only.) These are theoretical
(shifting-equilibrium ODE, JANNAF program) numbers, not delivered/measured — actual delivered
Isp uses the η_c*/η_CF factors above.

**Gas-generator secondary-flow (turbine exhaust dumped into main nozzle) Isp** (Table 2,
[p.7]):

| Propellants (turbine exhaust) | Isp SL (s) | Isp vac (s) |
|---|---|---|
| O2/H2 | 248.2 | 282.7 |
| O2/C3H8 | 122.2 | 142.7 |
| O2/CH4 | 121.5 | 141.6 |

**Turbine drive-gas characteristics** (Table 3, [p.9]), evaluated at T=2000R, PR=1.6, both
LOX-rich and fuel-rich preburner/GG conditions, giving MR, γ, Cp, and the f(γ,PR) turbine
work-availability function for O2/H2, O2/RP-1, O2/CH4, O2/C3H8 — useful only as a period
reference table, not independently re-derived here (values given: e.g. O2/H2 fuel-rich
MR=1.14, γ=1.345, Cp=1.78, f=0.113; full table has all four pairs at both LOX-rich and
fuel-rich conditions).

**Coolant-flowrate feasibility for O2/RP-1 at SSME-class Pc, H2 as coolant** [p.10-15,
summary table p.18]: at Pc = 3237 psia, MR = 2.8, chamber mass flow w_c = 1455 lb/sec,
combustion temp T0 = 6512°F: an up-pass parallel H2-cooling circuit requires **18.5 lbm/s
nozzle + 15.3 lbm/s chamber = 33.8 lbm/s total (44% of the O2/H2 SSME's own H2 coolant flow)
with no assumed carbon-layer benefit**, dropping to **12.2 lbm/s total (16% of SSME flow) if
a carbon deposit layer on the hot-gas wall is assumed** (Rocketdyne explicitly took the
conservative no-carbon-layer case for engine-balance work, flagging the carbon-layer credit
as real but too uncertain to bank on). A downpass series circuit needs slightly more (19.0
lbm/s no-coating / 14.6 lbm/s with coating) because it loses the curvature-enhancement
benefit to the coolant heat-transfer coefficient in the throat region, and its
peak-temperature location shifts to near the nozzle exit (ε~94, x≈94") rather than near the
nozzle-chamber attach point, due to larger bulk temperature rise along the series path.
Up-pass parallel cooling was the one selected for the candidate engine systems and assumed
valid (with only minor property-driven differences) across all three hydrocarbon fuels.
Hydrocarbon-fuel-as-coolant results (CH4, C3H8) parametrics given in Fig. 6-9 at Pc=3230
psia but not reduced to a single comparison table in this report (values embedded in
now-garbled OCR'd chart pages, not independently extractable as clean numbers).

**Cycle-balance finding — fuel-rich preburner infeasibility for LOX/hydrocarbon staged
combustion** [p.29, "TASK III"]: of the 12 (of 15 candidate) engine systems power-balanced
in this report period, the **staged-combustion cycles using fuel-rich LOX/hydrocarbon
preburner gas as turbine drive were found power-limited** — turbine inlet temperatures
exceeding **2200 R** were required to close the power balance (vs. the LOX/H2 SSME baseline
which does not need such extreme fuel-rich preburner temperatures for the same power), and
even so, no operating margin remained (100% of available fuel already committed to the
preburner, no headroom for turbopump-performance shortfall). Rocketdyne's conclusion: these
temperatures exceed then-available turbine hardware capability, so **only LOX-rich
precombustors would be carried forward** for the hydrocarbon-fueled staged-combustion cycle
variants (concepts 12 and 13B were revised on this basis) — i.e. a real, concrete finding
that **fuel-rich preburner LOX/hydrocarbon staged combustion (the FRSC scheme
`engine_designer`'s `physics/staged_combustion.py` already models for kerolox, per real
engines like the F-1-derivative/Russian-heritage LOX-rich designs) is a real turbine-thermal
constraint specifically for the hydrocarbon fuels considered here**, reinforcing why most
real high-Pc kerolox staged-combustion engines (RD-170/180, etc.) use **LOX-rich** (not
fuel-rich) preburners — this source gives an independent 1977 engineering rationale (turbine
inlet temp ceiling around/above 2200 R being judged infeasible) for that real-world choice,
consistent with what `engine_designer` already encodes.

## Structural/injector implications of switching propellant combinations in one chamber

The report is far short (progress report #1 of an unfinished 9-month study) of resolving
hardware-level injector or structural implications — **Task V (SSME Component Adaptability)
had "just been initiated" with no results yet [p.27], and Task IV (Control Requirements,
which would cover valve/sequencing needs for the Mode-1-to-Mode-2 transition) had not yet
started any work [p.27]** — so this source gives **no real injector redesign data** for
switching propellant combinations in one chamber. What it does establish, as design
*constraints* future tasks would need to resolve (flagged in the report's own "Work
Planned" section, not yet solved):
- The transition inherently requires **feeding two entirely different fuel systems (and
  potentially different mixture ratios/flowrates) to what is nominally the same injector
  face**, since the study explicitly reuses SSME injector/chamber hardware across modes
  rather than proposing a dual injector — a real unresolved hardware-sharing question this
  source flags but does not answer (Task V's stated scope, not yet executed within this
  report period).
- **Cooling-circuit compatibility across modes** is a real, already-identified design driver
  (Task II's entire content): whichever coolant is chosen must work adequately in the *same*
  regen jacket geometry across both Mode 1 (hydrocarbon combustion, hydrocarbon or H2
  coolant) and Mode 2 (LOX/H2 combustion, H2 coolant) — this is explicitly why RP-1 (Pc-
  limited to 2000 psia as sole coolant) was judged a poorer Mode-1 fuel choice than CH4/C3H8
  for a shared-hardware high-Pc chamber, and why H2 injection into Mode-1 combustion (using
  H2 purely as coolant, then burning it) was carried forward as a real cycle option in the
  "parallel burn" configuration.
- No structural (thermal-cycling, chamber-wall-fatigue-from-two-different-hot-gas-property
  regimes, injector-orifice-erosion-from-two-fluids) analysis appears anywhere in this
  report — entirely out of scope for this first bimonthly period.

## Design method

Not a design-equation/correlation source for direct reuse — a preliminary systems-study
progress report. Its numbers (Tables 1-3, the coolant-flowrate summary table on p.18, the
2200 R turbine-inlet-temperature finding) are useful as **period-authentic real engineering
figures for a specific, real (if never-built) NASA-funded dual-mode/tripropellant SSME-
derivative concept**, not as a generalizable sizing method.

## Section map

- Introduction (program objectives, task structure): leaf 3-5 — read.
- Summary + Task I (Performance Determination — Tables 1-3): leaf 6-9 — read in full.
- Task II (Chamber Cooling Studies — H2/hydrocarbon coolant analysis, coolant-flowrate
  summary table, carbon-layer discussion): leaf 10-22 — read; parametric chart pages
  (Fig. 2-9) skimmed, most numeric content OCR-garbled (bitmap-derived charts, not
  extractable text) beyond what's summarized above.
- Task III (Cycle and Power Balance — series/parallel burn definitions, 15 candidate
  systems, fuel-rich-preburner infeasibility finding): leaf 23-29 — read; Fig. 10-13 (engine
  schematics/ground-rules/candidate-system-list figures) and the Table 4 component-flowrate
  results page are present but rendered as unreadable OCR noise (scanned figure/table
  artwork, not machine-legible text) — their content is not independently verifiable from
  this extraction beyond what the surrounding body text describes.
- Tasks IV-VI (Control Requirements, SSME Component Adaptability, Component Test Plans):
  leaf 27-30 — read; each explicitly states no work was done/no results to report this
  period.
- Program expenditures, symbol nomenclature, references: leaf 32-34 — skimmed.

## Caveats

- **This is progress report No. 1 of an incomplete 9-month study** — covers ~5.5 weeks of
  work (22 Aug-30 Sep 1977) only. No final engine design, no hardware, no test data. Later
  bimonthly reports (No. 2+) and/or a final report are NOT in `literature/` — if found later,
  they would supersede/extend this note.
- **No tripropellant/dual-mode engine physics exists anywhere in `engine_designer` today.**
  This source is background/context only per the requesting instructions — flagged loudly:
  do not treat any number here as validating or calibrating existing single-propellant-pair
  physics beyond the RP-1-cooling-limit and LOX-rich-vs-fuel-rich-preburner corroborations
  noted above, which stand on their own as independent real-engineering findings applicable
  to `engine_designer`'s *existing* kerolox staged-combustion and cooling models.
  Tripropellant/mode-switching itself is out of scope for any current `engine_designer`
  feature.
- **OCR/scan quality is poor** — this is a 1977 typewriter-composed report reproduced via
  NASA CASI microfiche/scan, with visible character-substitution errors throughout (e.g.
  "P " for "Pc", "1 ." for "Is", stray "^" and OCR noise), and several full pages (schematic
  figures, Table 4, the candidate-system list Fig. 13) rendered as pure positional-glyph
  noise with no recoverable text at all. Every number quoted above was cross-checked against
  legible surrounding sentence context; anything not independently legible (e.g. Table 4's
  actual component flowrate/pressure/temperature values, the 15-candidate-system list detail
  beyond what body text describes) is reported as unavailable rather than guessed.
- **Efficiency factors (η_c*, η_CF) and the 2200 R turbine-temperature figure are Rocketdyne
  engineering judgments for this 1977 study**, not independently re-derived or cited to a
  deeper source within this report — treat as period-authentic real design assumptions, not
  as generically validated constants.
