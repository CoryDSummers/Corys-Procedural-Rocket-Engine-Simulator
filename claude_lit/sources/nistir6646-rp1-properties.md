# NISTIR 6646 — Thermophysical Properties Measurements and Models for Rocket Propellant RP-1: Phase I

## Identity

Joseph W. Magee, Thomas J. Bruno, Daniel G. Friend, Marcia L. Huber, Arno Laesecke, Eric W.
Lemmon, Mark O. McLinden, Richard A. Perkins, Jörg Baranski, Jason A. Widegren (NIST
Physical and Chemical Properties Division, Chemical Science and Technology Laboratory),
*Thermophysical Properties Measurements and Models for Rocket Propellant RP-1: Phase I*,
NISTIR 6646, February 2007. Funded by NASA John H. Glenn Research Center.
`literature/nistir6646.pdf` (124 PDF leaves; printed-page numbering runs 5 pages behind the
PDF leaf index for the body — printed p.N is roughly PDF leaf N+5, e.g. printed p.28 ≈ leaf 33).
Tag: `[NISTIR6646-RP1]`.

## Character

The primary NIST reference establishing a real, citable **surrogate-mixture** thermophysical
property model for RP-1 — the direct upstream ancestor of the kind of RP-1 fluid model that
NIST REFPROP / CoolProp-style property packages would draw from (see verdict below). Unlike
`[Lewis-Deposits]` (a standalone electrically-heated deposit-rate test rig) or `[SP-8087]`
(a design-criteria monograph stating a single coking-temperature threshold), this is a
first-principles metrology report: real NIST lab measurements (Archimedes-buoyancy density,
transient hot-wire thermal conductivity, capillary and torsional-crystal viscometry, plus
contracted flow-calorimeter heat-capacity and constant-volume-piezometer density measurements
from Azerbaijan State Oil Academy) on **actual RP-1 fuel samples**, combined into a
**14-component surrogate mixture model** with a full extended-corresponding-states / Helmholtz
mixture-model treatment. It explicitly frames itself as "Phase I" — a first sample's worth of
data, expecting later phases (not found elsewhere in `literature/`) to explore batch-to-batch
variation.

Structure: §1 Introduction (objective/scope/organization) → §2 Property Modeling (the EOS/
surrogate-mixture method) → §3 Chemical Characterization (GC-MS composition tables + thermal
decomposition kinetics) → §4 Density → §5 Heat Capacity → §6 Thermal Conductivity → §7
Viscosity → §8 Project Workshop (Dec 2003, NASA/AF/industry stakeholder list) → §9 Summary
and Recommendations → §10 References → Appendix A (chemical-characterization procedure
detail) → Appendix B (computational/molecular-structure detail for each of the 20 candidate
surrogate compounds, most not making the final 14-component cut).

## This note's extraction scope

**Scoped read, 2026-09-24, given the 124-page length** (per this note's assignment brief).
Read in full: front matter, §1 Introduction (objective/scope), the entirety of §2 Property
Modeling (the surrogate-mixture method and its stated accuracy), Table 2 (the surrogate
composition itself), the opening of §3 Chemical Characterization plus Table 7 (thermal
decomposition kinetics), all of §4 Density (methodology + Tables 8–9 sample values), all of §5
Heat Capacity (methodology only — see caveat below), all of §6 Thermal Conductivity narrative
(methodology, decomposition/deposit findings, uncertainty statement) plus representative rows
of Table 10 at several temperatures, all of §7 Viscosity narrative (methodology, batch-variation
finding, elevated-pressure results) plus Table 11 in full and representative Table 12 rows, all
of §8 (skimmed — workshop attendee list, no technical content beyond confirming the December
2003 date and stakeholder breadth), and all of §9 Summary and Recommendations.

**Not deep-read**: the bulk of Table 1 (a multi-page reference bibliography of prior RP-1/jet-
fuel property and thermal-decomposition studies — titles/authors only, useful as a *pointer*
list for future literature hunts, not chased here), the full numeric body of Tables 3–6
(detailed GC-MS peak-by-peak chemical characterization down to individual trace constituents —
Table 2's already-fitted surrogate composition supersedes these for `engine_designer` purposes),
the full ~800-row body of Table 10 (thermal conductivity vs. T/P/ρ — representative rows at
~300 K, 400 K, 450 K, and ~650 K were sampled; the full table is a genuine future-deep-read
target if `engine_designer` ever wants a real λ(T,P) lookup rather than a headline range), the
full body of Table 12 (viscosity×density at elevated pressure — representative rows sampled),
§10 References (a numbered list, 1–~86+, cross-referenced from Table 1 and the text; not
independently chased), and Appendices A/B (procedural GC-MS-IR chemical-characterization detail
and molecular-structure renderings for the 20 candidate surrogate compounds — useful only if a
future need arises to second-guess or extend the surrogate composition itself, not for a
coolant-property lookup).

## Key results

**The stated motivation — real, quotable uncertainty numbers on why this report exists**
`[NISTIR6646-RP1 §1.2 p.2-3]`: NASA's own sensitivity study found that **property uncertainties
accounted for 70% of the uncertainty in a portion of the propulsion system design**, and prior
to this project, "differences in RP-1 properties from different sources amounted to as much as
**60%**." This is a strong, citable justification for treating RP-1 coolant properties as a
real design uncertainty driver, not a settled input — directly relevant framing for any
`ASSUMPTIONS.md` discussion of confidence tiers on RP-1 coolant-property constants.

**The surrogate mixture — a real, citable composition** `[NISTIR6646-RP1 §2 p.7; Table 2 p.28]`:
RP-1 (a "kerosene, complex hydrocarbon mixture of several hundred components") is modeled as a
**14-component surrogate mixture** fitted (not measured directly) to reproduce the RP-1 sample's
measured density, heat capacity, thermal conductivity, viscosity, and one boiling point:

| Fluid | Formula | MW | Mole % |
|---|---|---|---|
| 3-ethyl-4,4-dimethyl-2-pentene | C9H18 | 126.24 | 9.98 |
| Cyclodecene | C10H18 | 138.25 | 2.11 |
| 2-methylnonane | C10H22 | 142.28 | 2.32 |
| 2-methylnaphthalene | C11H10 | 142.20 | 5.10 |
| 2-methyldecalin | C11H20 | 152.28 | 22.35 |
| 3-methyldecane | C11H24 | 156.31 | 10.84 |
| 1-dodecene | C12H24 | 168.32 | 2.64 |
| Cyclododecane | C12H24 | 168.32 | 4.27 |
| 4-methyl-4-undecene | C12H24 | 168.32 | 10.45 |
| n-dodecane | C12H26 | 170.33 | 1.93 |
| Heptylcyclohexane | C13H26 | 182.35 | 14.22 |
| 1-tridecene | C13H26 | 182.35 | 1.45 |
| 2,7,10-trimethyldodecane | C15H32 | 212.41 | 10.38 |
| n-hexadecane | C16H34 | 226.44 | 1.95 |

Overall: **molar mass 164.6 g/mol, H/C ratio 1.95, approximate formula C11.8H23.0**; by mole %:
27.4% alkanes, 26.6% alkenes, 18.5% monocyclic paraffins, 22.4% bicyclic paraffins, 5.1%
aromatics. Explicitly **not the real compositional makeup** — "a mixture that approximates the
behavior of the RP-1 sample," fitted via a multi-property regression, not a GC-MS assay result
(the real chemical-analysis-derived composition is in Tables 3–6, not deep-read here). Fit
quality: reproduces the measured **density to within 0.3%, heat capacity to within 7%, thermal
conductivity to within 3%, viscosity to within 3% at atmospheric pressure and 10% at 60 MPa,
and the boiling point to 0.5%** `[§2 p.7]`.

**The underlying property-modeling method — real, citable EOS/mixture framework**
`[NISTIR6646-RP1 §2 p.4-6]`: each of the 14 surrogate components gets its own equation of state
(a 12-term short-form Helmholtz-energy EOS reduced by that component's critical temperature and
critical density, with coefficients as functions of acentric factor — fitted originally against
normal alkanes C4–C36 and cross-checked against branched alkanes). The mixture as a whole uses
an **excess Helmholtz-energy mixture model** (the same NIST approach used for natural-gas and
refrigerant mixtures) with the excess (binary-interaction) term set to zero for lack of
experimental binary data — i.e. **ideal mixing of the 14 pure-component EOSs**, not a fully
independent binary-fitted mixture model. For **transport properties** (viscosity, thermal
conductivity), the model uses an **extended corresponding-states approach mapped onto
n-dodecane as the reference fluid** — NIST developed a dedicated n-dodecane EOS + viscosity/
thermal-conductivity correlation specifically for this project (published separately in *Energy
& Fuels*), valid from the triple point to the onset of decomposition and to 200 MPa, with
stated uncertainties of **0.2% in density (≤200 MPa), 1% in heat capacity, 0.5% in sound speed,
0.2% in vapor pressure, 0.5% in saturated-liquid viscosity, 3% in compressed-liquid viscosity,
2% in vapor viscosity, 3% in liquid thermal conductivity, 5% in vapor thermal conductivity**
`[§2 p.6]`. **This n-dodecane-as-reference-fluid corresponding-states architecture is exactly
the kind of building block a REFPROP/CoolProp-style hydrocarbon property package would
implement or draw from** — see verdict below.

**Density — real measured values** `[NISTIR6646-RP1 §4.1 p.33-36; Tables 8-9]`: atmospheric-
pressure Archimedes-buoyancy measurements, uncertainty ±0.10% (k=2): **original RP-1 sample
813.2 kg/m³ at 2.9°C, 799.0 kg/m³ at 23.3°C, 785.0 kg/m³ at 43.1°C** (all ~83 kPa under N2
blanket); a repeat 9 days apart at 25°C varied <0.15%, indicating no gross sample degradation
over a 10-day hold. An **ultra-low-sulfur RP-1 sample averaged 0.28% higher density** than the
original sample across the same temperature range — a real, quantified batch-to-batch
composition effect. **Elevated-pressure density** `[§4.2 p.37]`: measured with a constant-volume
piezometer up to **745 K and 60 MPa** (contracted to ASOA/Abdulagatov & Azizov), uncertainty
0.5 kg/m³ below 623 K, 0.1% above 623 K — this elevated-P/T dataset (not tabulated in this
report; privately communicated to NIST) is what actually extends the density model into
regen-jacket-relevant P/T space, not the atmospheric Table 8/9 values.

**Heat capacity — methodology only, no data table in this Phase I report**
`[NISTIR6646-RP1 §5 p.38]`: Cp measured with a flow calorimeter up to **671 K and 60 MPa**,
again contracted to ASOA (Abdulagatov/Azizov), uncertainty **2% below 573 K, 3-4% above 573 K**.
**No heat-capacity data table or figure is published in this report** — unlike density,
thermal conductivity, and viscosity, Section 5 is narrative-only; the measured Cp values were
used directly in the surrogate-mixture fitting (stated fit accuracy 7%, see above) but are not
themselves tabulated here. A future deeper read of Appendix A/B or the referenced Abdulagatov/
Azizov contract reports would be needed for actual Cp(T,P) numbers.

**Thermal conductivity — real measured values and a real decomposition/deposit finding
directly relevant to the coking discussion in `topics/06`** `[NISTIR6646-RP1 §6 p.39-48;
Table 10]`: transient hot-wire measurements along 9 isotherms, **300 K to 700 K, pressures up
to 70 MPa**, uncertainty **<0.5% at 300-450 K, ~1.0% at 550 K, ~4% at 650 K** (the 650 K
increase in uncertainty is explicitly attributed to *sample composition change during the
measurement*, not instrument error). Representative measured values (radiation-corrected λc):
**≈0.111 W/(m·K) at ~300 K/atmospheric, ≈0.127 W/(m·K) at ~300 K/63 MPa, ≈0.117 W/(m·K) at
~400 K/68 MPa, ≈0.112 W/(m·K) at ~450 K/69 MPa, dropping to ≈0.068 W/(m·K) at ~649 K at a much
lower density (0.484 g/cm³ vs. ~0.83 g/cm³ at 300 K, reflecting substantial thermal expansion/
approach to the vapor-liquid transition region)** — thermal conductivity falls with both rising
T and falling ρ, roughly by half from 300 K to 650 K over this pressure range.

**Real decomposition/coking corroboration, independent of `[Lewis-Deposits]`'s wall-deposit
rig** `[NISTIR6646-RP1 §3 p.29; §6 p.40-42]`: the report states outright that RP-1 "may be
thermally unstable at temperatures above **600 K**." During thermal-conductivity testing,
**rapid decomposition was observed at 700 K** — chemical analysis (GC-MS-IR) of samples
recovered after the 650 K and 700 K isotherms showed a **significant increase in aromatic and
naphthalenic compounds** relative to the pre-test fluid, i.e. bulk thermal cracking/
recombination chemistry, not just a wall-surface effect. A time-resolved test *held at 650 K
for 9 hours* showed cell pressure rising from 13.1 to 14.8 MPa and thermal conductivity
increasing measurably (~0.3% over the hold, ~2% attributable to composition change once T/P
effects are backed out) — a real, quantified **bulk-fluid decomposition rate at 650 K**,
distinct in character from `[Lewis-Deposits]`'s wall-surface carbon-deposition-rate data (that
source measures deposit mass on a heated tube wall; this one measures bulk-fluid composition
drift in a static sample cell). **Visible solid deposits were found on the 4 µm hot wires after
the 700 K measurement** — spherical/beaded, up to 8× the wire diameter, apparently molten but
nonvolatile at test temperature; the deposit's thermal conductivity (probed indirectly via a
post-test toluene calibration check, which matched toluene reference data even with the deposit
present) is inferred to be **close to toluene's** (i.e., an aromatic-like solid), and the
deposit was **not soluble in toluene at 300 K** — a real, independent physical/chemical
description of the coking deposit's character, corroborating (from a completely different
apparatus/method) the aromatic-enrichment coking chemistry `[Lewis-Deposits]` and `[TP2862-
LOXRP1]` establish from the deposit-mass-rate side.

**Real bulk-fluid thermal-decomposition KINETICS — a genuinely new number vs. `[Lewis-
Deposits]`'s wall-deposit-rate framing** `[NISTIR6646-RP1 §3 Table 7 p.32]`: separate isothermal
kinetics measurements on RP-1 gave first-order-style rate constants and half-lives (note: these
temperatures are in **°C**, i.e. this is a *hotter* regime than the 600-800 K *wall-temperature*
coking band in `[Lewis-Deposits]`/`[SP-8087]`):

| T (°C) | T (K) | k (s⁻¹) | t½ (min) |
|---|---|---|---|
| 375 | 648 | (6.92 ± 0.75)×10⁻⁵ | 167 |
| 400 | 673 | (2.00 ± 0.23)×10⁻⁴ | 58 |
| 425 | 698 | (3.85 ± 0.53)×10⁻⁴ | 30 |
| 500 | 773 | (1.07 ± 0.17)×10⁻³ | 11 |

This is **bulk (homogeneous) thermal decomposition half-life**, not a wall-surface deposit-rate
correlation — a different physical quantity than `[Lewis-Deposits]`'s µg/cm²·hr wall-fouling
rate, but a real, quotable time-temperature decomposition-severity anchor if `engine_designer`
ever needs a residence-time-at-temperature framing for RP-1 thermal margin (e.g., a coolant
staying at 673 K for a fraction of its 58-minute half-life during a burn is a very different
risk than staying at 648 K for the same duration, given the ~3× rate change per 25 K step
visible in this table — consistent with an Arrhenius-type steep temperature sensitivity).

**Viscosity — real measured values and a real batch-to-batch variability finding**
`[NISTIR6646-RP1 §7.1 p.58-63; Table 11]`: atmospheric-pressure kinematic viscosity of the
"original" RP-1 sample (anomalously high olefin content) measured by capillary viscometry,
**7.667 mm²/s at 243.3 K down to 1.126 mm²/s at 333.15 K**, fit to a 4-term modified-Arrhenius
correlation (ln ν = A + B/T + C/T² + D/T³, A=−7.812, B=5.530×10³, C=−1.503×10⁶, D=1.801×10⁸,
all data within 1.1% of the fit). **Real batch-variation finding**: three other RP-1-family
samples (a second normal-grade batch, an ultra-low-sulfur batch, and a TS-5 batch), measured
only at 298.15 K and 313.15 K, all showed viscosities **7-10% higher** than the original
sample's correlation — a real, quantified illustration that RP-1 viscosity is not a single fixed
number even nominally within-spec, motivating the report's own recommendation (below) for
systematic batch-variation studies. **Elevated-pressure viscosity** `[§7.2 p.63-68; Table 12]`:
torsional-crystal viscometer, up to **65.7 MPa**, isotherms near 295 K, 297 K (repeat), and
400 K; the surrogate-mixture model **over-predicts** measured viscosity across this range, by
**3.5% (400 K, 0.1 MPa) to as much as 11.7% (295 K, 41.5 MPa)** — the report frames this as
"satisfactory" agreement given the surrogate's compositional complexity and notes the
experimental uncertainty itself widens substantially at the highest pressures (impedance-
analyzer resolution limits), e.g. a −9.2% deviation point carries an uncertainty band of −15%
to −0.3%.

**Summary and Recommendations** `[NISTIR6646-RP1 §9 p.74]`: the report explicitly recommends
(1) systematic study of RP-1 property variation **across different production lots/batches**
(motivated directly by the viscosity/density batch-variation findings above) to support more
robust engine designs tolerant of batch-to-batch RP-1 variability, and (2) longer-term,
extending the same surrogate-mixture-modeling methodology to other kerosene-type jet fuels. No
"Phase II" report of this series was found in `literature/` as of this extraction.

## Design method

Not a component-sizing source in the Huzel/Sutton sense. Its "design method" is the **surrogate-
mixture property-modeling architecture itself**: (1) chemically characterize a real RP-1 sample
by GC-MS, (2) select ~14-20 candidate pure hydrocarbon compounds spanning the identified
compound classes, (3) build/borrow a short-form Helmholtz EOS for each pure component reduced
by its own critical temperature/density and acentric factor, (4) mix them ideally (excess term
zero, for lack of binary data) for thermodynamic properties, (5) map transport properties onto
a single well-characterized reference fluid (n-dodecane) via extended corresponding states, and
(6) fit the 14 components' mole fractions to best reproduce a real sample's measured density,
heat capacity, thermal conductivity, viscosity, and boiling point simultaneously. This is the
general pattern any RP-1 property implementation (REFPROP, CoolProp, or a hand-rolled table)
would need to replicate or approximate if it wants RP-1 support beyond a single-compound
kerosene surrogate (e.g. n-dodecane alone, or a simpler 2-3-component blend) — see verdict.

## Section map

- §1 Introduction (Objective/Scope/Organization): p.2-3 — read in full.
- §2 Property Modeling (EOS method, mixture model, surrogate-fitting method and its accuracy):
  p.4-7 — read in full; Table 1 (bibliography, p.8-27): titles/authors skimmed only, not chased.
- §3 Chemical Characterization: p.29 (intro) + Table 7 (decomposition kinetics, p.32) — read;
  Tables 3-6 (detailed GC-MS peak tables): skimmed only, not transcribed (superseded by Table 2
  for `engine_designer` purposes).
- §4 Density (§4.1 atmospheric, §4.2 elevated pressure): p.33-37, Tables 8-9 — read in full.
- §5 Heat Capacity: p.38 — read in full (narrative only, no data table present in this report).
- §6 Thermal Conductivity: p.39-48 — read in full; Table 10 (full ~800-row data table, p.47-57):
  representative rows sampled at ~300 K/multiple pressures, ~350 K, ~400 K, ~450 K, and ~649 K;
  full table not transcribed — flagged as a future deep-read target for an actual λ(T,P) lookup.
- §7 Viscosity (§7.1 atmospheric, §7.2 elevated pressure): p.58-68 — read in full; Table 11 (all
  four samples' atmospheric kinematic viscosities): read in full; Table 12 (elevated-pressure
  viscosity×density, p.66): representative rows sampled, not fully transcribed.
- §8 Project Workshop: p.69-73 — skimmed (attendee/affiliation list only, no technical content).
- §9 Summary and Recommendations: p.74 — read in full.
- §10 References: p.75+ — not read (numbered list, cross-referenced from Table 1 and body text;
  not independently chased for this note).
- Appendix A (Discussion of Chemical Characterization) and Appendix B (Computational
  Characterization of Surrogate Mixture Compounds, incl. molecular-structure figures for the 20
  candidate compounds): not read this pass — flagged as a target only if the surrogate
  composition itself (Table 2) is ever questioned or needs extending to a Phase II-style update.

## Caveats

- **This is "Phase I" of an intended multi-phase study — a single RP-1 sample plus three
  comparison samples, not a definitive multi-batch consensus property set.** The report's own
  headline finding is that RP-1 properties vary meaningfully batch-to-batch (0.28% density,
  7-10% viscosity between samples tested here) — treat any single number pulled from this report
  as representative of *a* RP-1 sample from 2003-2004, not a universal constant.
- **No heat-capacity data table is published in this report** (§5 is methodology-only) — Cp(T,P)
  numbers for RP-1 are not directly extractable from this source as read; only the fit-quality
  statement (surrogate reproduces measured Cp within 7%) is available without a deeper dig into
  the underlying ASOA contract data or a hypothetical Phase II report.
- **The surrogate model over-predicts elevated-pressure viscosity by up to ~12%** and is
  systematically high on thermal conductivity at low density/high temperature (4-12% high along
  the 650 K isotherm) — this is a real, stated model-vs-measurement gap, not a hidden one; any
  downstream property table built from "the NIST RP-1 model" inherits these specific known
  weak spots (elevated-P viscosity, high-T/low-density thermal conductivity).
- **Density/heat-capacity/viscosity elevated-pressure data below 745 K were measured under an
  ASOA subcontract and are not tabulated in this report** — only the piezometer/flow-calorimeter
  method and uncertainty are given; the actual P-ρ-T and P-Cp-T data tables live in
  (unpublished-here) ASOA communications, not in this PDF.
- **Data above 600 K were explicitly excluded from the surrogate-mixture fitting process**
  "due to concerns about thermal decomposition during measurement" (§2 p.7) — i.e. the 14-
  component surrogate model itself is fitted against sub-600 K data and is not claimed by the
  authors to be valid into the decomposition regime, even though some raw measurements (thermal
  conductivity, decomposition kinetics) extend to 650-773 K.
- **Two distinct, not-directly-comparable "coking" datasets exist in `claude_lit` now**: this
  report's 650-700 K findings are BULK fluid decomposition (composition drift in a static/
  circulating fluid sample, observed via GC-MS-IR and a hot-wire-adjacent solid deposit) at
  temperatures at or above the bulk fluid's own bulk temperature, whereas `[Lewis-Deposits]`'s
  600-800 K finding is WALL-SURFACE carbon deposition rate as a function of *wall* temperature
  with cooler bulk flow — related chemistry, different physical setup; do not conflate the two
  when citing a "RP-1 coking limit."
- **OCR quality is generally good** (a clean, modern 2007 NIST-typeset PDF; equations rendered
  as inline images/symbols in a few spots came through partially garbled, e.g. the transient
  hot-wire heat-conduction equation in §6, but all narrative text and every number quoted above
  was read cleanly from extracted text, not reconstructed from a rendered image).
- **No RP-1-mixture critical point (Tc, Pc, ρc) is stated anywhere in the body text as a single
  headline number** — critical parameters exist only implicitly, per-component, inside each of
  the 14 surrogate compounds' individual equations of state (used to build the mixture EOS);
  there is no single "RP-1 critical point ≈ X K, Y MPa" quote extractable from this report as
  read. If `engine_designer`/`thermo_tables.py` needs a single-point RP-1 critical-property
  estimate, this source does not directly supply one (though the underlying n-dodecane
  reference-fluid EOS, cited separately in *Energy & Fuels*, would).

## Verdict on citability for `thermo_tables.py`'s baked RP-1 coolant-property table

**Yes — this is a real, traceable, and highly plausible upstream citation for whatever RP-1
liquid-phase property model underlies `engine_designer/physics/property_data/*.json`'s RP-1
coolant entries.** This report is NIST's own foundational RP-1 surrogate-mixture property
model: a 14-component mixture built on a proper Helmholtz-energy equation of state per
component, an extended-corresponding-states transport-property model anchored to a dedicated
NIST n-dodecane reference-fluid EOS/viscosity/thermal-conductivity correlation (the same
n-dodecane correlation NIST published separately and that REFPROP/CoolProp-class packages are
built to consume), fitted against real measured density/heat-capacity/thermal-conductivity/
viscosity data over 300-700+ K and up to 70 MPa. This is exactly the kind of primary source a
Cantera/CoolProp-based coolant-property generation pipeline (per `CLAUDE.md §2`'s description
of `tools/property_tables/generate_property_tables.py`) would either directly implement (if
RP-1 is modeled as this NIST surrogate mixture, or as a REFPROP RP-1 predefined mixture derived
from it) or approximate (if RP-1 is instead represented by a single proxy compound like
n-dodecane alone, which this report's own corresponding-states architecture would justify as a
reasonable single-compound stand-in, with the stated caveat that a bare n-dodecane proxy misses
the 26.6% alkene / 22.4% bicyclic-paraffin / 5.1% aromatic content the real 14-component
surrogate carries). Either way, this is not too narrow or off-topic to cite — it is a
first-order match for the underlying physics the design doc names, and its explicit, tabulated
accuracy/uncertainty bounds (density 0.3%, Cp 7%, λ 3%, viscosity 3-10%) are exactly the kind
of number that should accompany any RP-1 coolant-property constant pulled into
`ASSUMPTIONS.md` or `topics/06b-cooling-methods-and-chemistry.md`.
