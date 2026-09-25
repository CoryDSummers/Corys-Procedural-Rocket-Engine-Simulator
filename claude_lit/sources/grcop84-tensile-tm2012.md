# NASA/TM—2012-217108 — Tensile Properties of GRCop-84

## Identity

David L. Ellis (NASA Glenn Research Center), William S. Loewenthal (Ohio Aerospace
Institute), Hee Man Yun (Cleveland State University), *Tensile Properties of GRCop-84*,
NASA Technical Memorandum NASA/TM—2012-217108, April 2012, 92 pages. NTRS accession
20120008551. `literature/NASA TM-2012-217108 - Tensile Properties of GRCop-84.pdf`. A
chapter from the final report on GRCop-84 for the Reusable Launch Vehicle (RLV) Second
Generation/Project Constellation Program. Tag: `[GRCop84-Tensile]`.

## Character

A rigorous, data-heavy multi-specimen tensile-test program (not a single-point datasheet)
covering GRCop-84 (Cu-8 at.% Cr-4 at.% Nb) across essentially every production form
(small/large extrusions, HIPed billets, rolled plate/sheet/foil, drawn tubing) and every
process condition of interest to a rocket-engine liner designer: as-produced, annealed,
two different simulated braze/diffusion-bonding thermal cycles, a simulated 100 hr/500°C
end-of-life exposure, long-term high-temperature exposures (600-1000°C, 100-6000 min) aimed
at creep-resistance improvement, cold work (up to 90% reduction), and strain-rate
sensitivity. The core dataset — five independent 60 lb powder lots ("true repeats") each
extruded into bars AND HIPed into cylinders, tensile tested from cryogenic (liquid
nitrogen 77 K / liquid hydrogen 20 K) through 1000-1200 K — gives real least-squares
polynomial regressions (with one-sided 95% lower-confidence-limit terms, i.e. real design
minimums, not just averages) for 0.2% offset yield strength, ultimate tensile strength,
elongation, and reduction of area vs. absolute temperature. This is the direct numeric
backbone `claude_lit/topics/12-materials-and-structures.md`'s existing `[MatCh2 Table
2.6.3]` GRCop-84 row (a single-point-per-property table) has been missing: a continuous,
statistically-grounded T-dependent strength curve plus a documented data-set size (31-32
degrees of freedom on the extruded regression, i.e. ~35 data points from 5 lots x ~7
temperatures; 19 degrees of freedom on the HIPed regression, i.e. ~23 points).

Structure: Summary, Introduction (liner-construction-method survey: milled/spun liner,
platelet liner, tube-wall liner — directly maps onto `engine_designer`'s
`WALL_CONSTRUCTIONS`), Experimental Procedure (chemistry, powder-size analysis, HIPing/
extrusion/rolling/tube-drawing process specs, thermal-exposure/braze-cycle specs, tensile
test-rig specs), Results (chemistry, baseline as-HIPed/as-extruded regressions, simulated-
braze regressions, -270 mesh powder comparison, large-extrusion isotropy study, rolled-
plate results, cold-worked foil, tube testing, long-term high-T exposures, strain-rate
sensitivity), Discussion (processing effects, cold-work effects, heat-treatment effects,
NARloy-Z/competitor-alloy comparison, strain-rate effects), Future Work, Summary and
Conclusions, References (53 citations, several to unpublished/"to be published" companion
NASA reports on creep, annealing, and low-cycle-fatigue of GRCop-84 — potential future
literature targets, not chased here).

## Key results

**Baseline as-extruded 0.2% offset yield strength vs. temperature — the headline curve**
`[GRCop84-Tensile Eq.2a p.21]`: lower-95%-confidence-limit regression
σ₀.₂%(T) = 297.4 − 0.312·T + 3.175×10⁻⁴·T² − 2.506×10⁻⁷·T³ − t(1−α,31)·10.92, T in Kelvin,
σ in MPa (set the last term to 0 for the regression MEAN rather than the lower bound).
Evaluated at the mean (t-term = 0):

| T (K) | T (°C) | Yield, extruded (MPa) | UTS, extruded (MPa) | Elongation, extruded (%) | R.A., extruded (%) |
|---|---|---|---|---|---|
| 20 (LH2) | −253 | 291.3 | 644.9 | 17.8 | 10.3 |
| 77 (LN2) | −196 | 275.1 | 590.8 | 19.3 | 21.7 |
| 293 | 20 | 226.9 | 408.4 | 21.4 | 44.8 |
| 400 | 127 | 207.4 | 331.3 | 20.9 | 46.9 |
| 500 | 227 | 189.4 | 267.2 | 20.0 | 45.1 |
| 600 | 327 | 170.4 | 210.9 | 18.9 | 40.8 |
| 700 | 427 | 148.6 | 162.2 | 18.0 | 35.2 |
| 800 | 527 | 122.7 | 121.3 | 17.6 | 29.4 |
| 900 | 627 | 91.1 | 88.1 | 17.8 | 24.6 |
| 1000 | 727 | 52.3 | 62.5 | 19.1 | 22.0 |

(mean-regression values, i.e. `t(1-α,ν)` term set to 0; the lower-95%-confidence-limit
version subtracts a further 10.92 MPa (yield) / 21.92 MPa (UTS) × the Student-t multiplier
— practically, roughly another 10-20 MPa off these means for a one-sided 95% design
minimum, since ν=31-32 gives t≈1.7 at 95%.) Companion **as-HIPed** regression
`[GRCop84-Tensile Eq.2b,3b p.21]`: σ₀.₂%,HIP(T) = 159.9 + 0.0565·T − 1.62×10⁻⁴·T²;
σUTS,HIP(T) = 448.5 − 0.405·T + 2.37×10⁻⁵·T² — consistently LOWER yield than extruded at
low/mid T (159.9 MPa vs. extruded's ~227 MPa at RT) but the two converge by ~900-1000 K
(HIPed yield 79.5/54.4 MPa vs. extruded 91.1/52.3 MPa at 900/1000 K) — i.e. extrusion's
mechanical working gives a real strength premium at low-to-mid T that the report attributes
to microstructural refinement (finer, elongated Cr₂Nb stringers) that anneals/coarsens away
at high T. **No cryogenic data exists for the HIPed condition** (insufficient HIPed
material was available for cryo testing) — do not trust the HIPed regression below room
temperature. **Full regression equations** (elongation/R.A., both conditions) are given in
Eqs. 2a-5b `[GRCop84-Tensile p.21-22]`; not all reproduced numerically above but captured
in the extracted equation set (see Design method below) for anyone needing the full
functional form.

**Real drawn-tubing room-temperature data — directly relevant to `tube_wall`
construction** `[GRCop84-Tensile Table 10 p.62]`: three GRCop-84 production-tubing
specimens (9.5 mm OD × 1.0 mm wall, drawn by LeFiell) tensile tested at room temperature
gave: modulus 114.7 GPa (avg of 113-116 GPa), 0.2% offset yield 245.7 MPa (avg of
243-248 MPa), UTS 420.0 MPa (avg of 417-422 MPa), strain-to-failure 22.8% (avg of
21.1-25.4%) — "consistent with annealed GRCop-84 sheet and the as-extruded GRCop-84 tensile
properties," i.e. drawing to tube form does NOT degrade tensile properties. This is a real,
directly-citable RT yield/UTS number specifically for the tube geometry
`engine_designer`'s `WALL_CONSTRUCTIONS` tube_wall option represents.

**Simulated braze/diffusion-bonding cycle effect — small, unlike competing Cu alloys**
`[GRCop84-Tensile Eq.6a-9b p.24-25; Discussion p.78; Summary p.84]`: two representative
thermal cycles were run (935°C/1715°F "low-temperature" braze, Table 1; 1000°C/1832°F
"high-temperature" braze, Table 2 — both slow-ramped, 2-6°C/min, to mimic a real large
thrust-cell braze/diffusion-bond, no actual braze alloy used). Effect on GRCop-84: yield
strength decrease "typically 20 to 35 MPa (3 to 5 ksi)," fairly uniform from cryogenic up
to ~600°C, with braze/as-extruded curves converging above 600°C. **By contrast, competing
precipitation-strengthened Cu alloys (NARloy-Z, Cu-Cr, Cu-Zr, Cu-Cr-Zr) "lose most of their
strength and are much inferior to GRCop-84 in the brazed condition"** — unpublished
Pratt & Whitney Rocketdyne NARloy-Z data (935°C braze + 482°C/900°F age) showed NARloy-Z
"loses almost half of its strength" from this cycle even with the recovery aging step,
vs. GRCop-84's ~20-35 MPa (roughly 10-15% of RT yield) loss. Only the OTHER
dispersion-strengthened alloy tested, GlidCop AL-15 LOX, matched GRCop-84's braze-cycle
strength retention — precipitation strengthening (NARloy-Z's mechanism) is inherently
vulnerable to a high-temperature braze/diffusion-bond cycle (particle coarsening/
overaging), dispersion strengthening (GRCop-84's Cr₂Nb Hall-Petch + Orowan mechanism) is
not. This is the report's stated "real advantage of GRCop-84" for a liner application
that requires post-liner brazing to a structural jacket. One caveat/localized anomaly: an
18.4 mm-thick plate batch given the 1000°C braze showed a dramatic reduction-in-area drop
(traced to >5 µm elemental Cr precipitates forming from the alloy's deliberate excess-Cr
content, at a weaker Cr-Cu interface than the normal Cr₂Nb-Cu interface) — ductility (10%+
elongation, 6%+ R.A.) remained USABLE but this is flagged by the authors themselves as
requiring caution/further investigation for a 1000°C+ processing route (Eq. citations
p.79-80).

**Long-term high-temperature exposure — GRCop-84 GAINS strength at 500°C, only mildly
degrades even near its melting point** `[GRCop84-Tensile Fig.49 p.81-82; Discussion
p.82-83]`: samples exposed 100-6000 min at 500, 600, 900, and 1000°C (homologous
temperatures 0.57-0.94 Tm, solidus ≈1080°C/1353K) then tensile tested at 500°C. At 500°C
exposure, yield AND UTS actually INCREASE beyond the upper 95% confidence interval for the
as-extruded baseline — an explicit surprise finding, attributed to precipitation of
previously-dissolved residual Cr from the Cu matrix (a slow secondary-precipitation
strengthening effect on top of the primary Cr₂Nb dispersion). At 600-1000°C exposure, yield
strength decreases only slightly (900/1000°C, 1000-3000 min exposures average slightly
below the lower 95% CI) while elongation actually INCREASES; reduction-in-area stays
"essentially unchanged" at all exposure temperatures. **Headline design statement**
`[Summary and Conclusions p.84]`: "GRCop-84 has a minimal loss in properties and retains
almost all of its as-produced strength, even after being exposed at 1000°C (1832°F) or
0.94 Tm" — a real, quantified thermal-stability claim well beyond typical precipitation-
hardened copper alloys, which the report explicitly predicts (not tested) would overage and
lose strength under an equivalent exposure.

**Cold work: strong RT strengthening, but anneals out well below typical hot-wall
temperatures** `[GRCop84-Tensile Effect of Cold Work p.75-76; Table 7-9 p.61-63]`: cold
work can raise GRCop-84's yield strength by up to 50% and UTS by up to 25% at room
temperature (saturating near ~50% cold reduction), e.g. 90% cold-rolled foil averaged
320.6 MPa yield / 424.2 MPa UTS / 8.2% elongation at RT (Table 7) vs. the as-extruded
baseline's 226.9 MPa yield / 408.4 MPa UTS / 21.4% elongation — i.e. cold work buys ~40%
more yield at the direct cost of more than half the ductility. But GRCop-84's matrix is
"nearly pure copper" (matrix chemistry confirmed via electrolytic extraction, Table 4: 100%
Cu at the ICP-AES detection limit, Cr/Nb entirely in the Cr₂Nb precipitate phase) and so
inherits pure copper's recovery/recrystallization behavior — the SAME 90% cold-rolled foil
loses virtually all of that cold-work benefit by 500°C (Table 9: yield collapses to
93.1 MPa avg, UTS to 106.9 MPa avg, essentially matching the annealed baseline's ~190 MPa/
267 MPa trend-line at 500°C only if you interpolate the ANNEALED curve, i.e. cold work is
NOT additive with the underlying strength at hot-wall-relevant temperatures). Recovery/
recrystallization onset is reported at 200-600°C depending on cold-work fraction — GRCop-84
was "purposefully optimized for use in the 300 to 800°C" range specifically BECAUSE cold
work is not a viable strengthening lever there; the report explicitly recommends against
relying on cold work for any liner application above ~200°C.

**Chemistry (composition confirmation)** `[GRCop84-Tensile Table 3 p.13]`: Cr 6.53-6.72
wt%, Nb 5.64-5.82 wt%, O 242-741 ppm, Fe 20-240 ppm, balance Cu — tightly controlled across
all powder lots over several years of production, giving confidence that the tensile
dataset reflects one consistent alloy chemistry, not lot-to-lot composition drift.

**Strain-rate sensitivity — small, matches OFHC copper** `[GRCop84-Tensile Table 11 p.73;
Effect of Strain Rate p.83]`: tested 2.8×10⁻⁵ to 8.3×10⁻³ /s at RT and 400°C on annealed
and 47% cold-rolled sheet. Yield/UTS sensitivity to strain rate (slope `m`, MPa per decade
of strain rate) is modest: as-annealed RT m=4.11 MPa/decade (yield), 14.28 (UTS); as-
annealed 400°C m=10.43/11.39; 47% cold-rolled RT m=24.58/20.60; 47% cold-rolled 400°C
m=5.61/10.10 — the report explicitly attributes this to the matrix being "nearly pure Cu,"
consistent with published OFHC copper strain-rate data over 10⁻⁴ to 3×10³ /s. Not a large
effect for `engine_designer` purposes (no rate-dependent yield model currently exists in
`materials.py` and this source doesn't obviously justify adding one).

**Fracture mode is consistent ductile microvoid coalescence across ALL conditions and
temperatures tested** `[GRCop84-Tensile p.22-23, p.85]`: SEM fractography (cryogenic
through 400°C, where oxidation prevents useful SEM above that) shows dimpled ductile
fracture in every condition — as-extruded, HIPed, brazed, large-extrusion, rolled plate —
with "no evidence of a weak interface between the Cu matrix and the Cr₂Nb that initiates
the voids" (i.e. the reinforcing Cr₂Nb precipitates do NOT act as crack-initiation sites
under normal conditions; the one exception being the anomalous coarse elemental-Cr
precipitates from the 1000°C braze plate batch noted above).

## Design method

Not a closed-form heat-transfer/stress-sizing method — this is a materials-property source,
not a thermal/structural design procedure. The directly usable outputs for
`engine_designer/physics/materials.py`'s GRCop-84 entry are: (1) the full continuous
0.2%-offset-yield-vs-temperature curve (mean regression above, plus a real lower-95%-
confidence-limit term for a genuine statistical design minimum rather than a single-point
"typical" value) spanning cryogenic (20 K) through 1000 K — this can directly replace or
validate the current Tier-3 (unvalidated-estimate) `allowable_stress_pa` entry for GRCop-84
with a REAL, statistically-grounded T-dependent curve; (2) the as-extruded vs. as-HIPed
split, letting a future refinement pick the right curve depending on which production
route a modeled liner assumes; (3) the drawn-tubing RT spot value (245.7 MPa yield /
420.0 MPa UTS) as a direct anchor for the `tube_wall` construction option specifically;
(4) a documented, small, quantified braze-cycle knockdown (20-35 MPa) if `engine_designer`
ever wants to model a post-braze allowable-stress derate distinctly from the as-produced
curve — currently no such distinction exists in the tool; (5) qualitative confirmation
that GRCop-84 is a poor candidate for cold-work-based strengthening above ~200°C (relevant
if `materials.py` or `ASSUMPTIONS.md` ever proposes a cold-worked-GRCop-84 variant).

## Section map

- Summary/Introduction (liner construction methods: milled, platelet, tube-wall — maps to
  `WALL_CONSTRUCTIONS`): p.1-2 (leaves 4-5) — read in full.
- Experimental Procedure (chemistry, powder, HIPing/extrusion/rolling/tube-drawing,
  thermal exposures, annealing study, simulated-braze-cycle tables 1-2, tensile-test rig
  incl. cryogenic/vacuum-foil setups): p.1-12 (leaves 4-15) — read in full (methodology
  skimmed at a slightly lower depth than the numeric results, per the task's guidance).
- Results — Chemistry/Powder Size (Tables 3-5): p.12-14 (leaves 15-17) — read, tables
  extracted.
- Results — Stress-Strain Behavior, Baseline As-HIPed/As-Extruded (Figs.8-16, regression
  Eqs.1-5b, the headline curves): p.15-23 (leaves 18-26) — read in full, all equations
  extracted via page-image rendering to resolve OCR-garbled exponents/coefficients (leaves
  24-25 rendered at 250 dpi and read as images — the prose-OCR text for these two pages was
  unusable, digit/exponent order scrambled).
- Results — Simulated Braze Cycles on Baseline (Eqs.6a-9b), -270 Mesh Powder Extrusions
  (Eqs.10a-13c), Large Extrusions (Table 6, Eqs.14-24), Rolled Plate (Eqs.25-36): p.24-45
  (leaves 27-48) — read; equation TEXT extracted via OCR (garbled coefficient order, not
  individually re-rendered as images since these are secondary/non-baseline results not
  needed at full numeric precision for this note) but narrative findings (magnitude of
  braze-cycle knockdown, isotropy conclusions, anomalous Cr-precipitate finding) captured
  from clean surrounding prose.
- Cold-Worked Foil (Tables 7-9), Tube Testing (Table 10), remaining results sections
  (leaves ~58-65, pages 55-62): tables extracted directly via targeted text search (not a
  sequential read of every intervening page — this report is long and repetitive across
  many product-form sub-sections; pages between the major results already summarized above
  and these targeted tables were not individually read).
- Strain Rate (Table 11, leaf 75/p.73): extracted via targeted search.
- Discussion (Effect of Processing/Cold Work/Heat Treatments — annealing, simulated
  brazing incl. the NARloy-Z comparison and Fig.48, long-term exposures incl. Fig.49),
  Effect of Strain Rate, Future Work: p.74-83 (leaves 77-87) — read in full.
- Summary and Conclusions: p.84 (leaf 87) — read in full.
- References (53 citations, several "to be published" NASA GRC companion reports on
  creep/annealing/low-cycle-fatigue of GRCop-84 — potential future literature targets, not
  chased): p.84-86 (leaves 87-89) — titles read, not chased.
- Report Documentation Page (abstract restatement): leaf 90 — read.
- Not individually read as images: the many product-form comparison figures (Figs.17-46,
  covering braze microstructure TEM/SEM, large-extrusion cross-sections, rolled-plate
  fractography, foil microstructure, strain-rate plots) — these are plot/micrograph
  content whose narrative conclusions were captured from the surrounding OCR'd prose (which
  was clean enough to trust for qualitative statements) but whose exact plotted curve
  shapes were not digitized; only the two pages with numerically load-bearing baseline
  regression equations (Eqs. 2-5, pages 24-25) were re-rendered as images to resolve OCR
  ambiguity.

## Caveats

- **The headline curve above is for the "baseline" as-extruded (or as-HIPed) material with
  NO subsequent braze/diffusion-bond cycle applied.** A real engine liner will almost
  certainly be brazed to a structural jacket; the report's own braze-cycle regressions
  (Eqs. 6-9, not fully reproduced above) show a real but modest ~20-35 MPa yield-strength
  knockdown from that step — if `engine_designer` ever wants a "manufactured, in-service"
  allowable stress rather than an "as-produced" one, the braze-cycle-adjusted curve (not
  the bare baseline table above) is the more representative source, and is available in
  this same document (Eqs. 6a/6b, 7a/7b) if a future extraction pass wants the exact
  coefficients.
- **HIPed-condition regression has NO cryogenic data** (insufficient HIPed material was
  available for cryogenic testing) — only extend the as-HIPed curve down to room
  temperature (293 K), not below. The as-extruded curve DOES include real cryogenic (77 K
  LN2, 20 K LH2) test points and is valid across the full 20-1000 K range shown.
  Confirmed by directly evaluating the polynomial: the HIPed elongation regression goes
  NEGATIVE below ~150 K, an unphysical extrapolation artifact.
  Confirmed by direct evaluation, not the report's own text.
- **These are LOWER-95%-CONFIDENCE-LIMIT regressions when the `t(1-α,ν)Sy.x` term is kept**
  — a genuine statistical design-minimum, appropriate for `allowable_stress_pa`-style use,
  but the report also gives the underlying REGRESSION MEAN (set that term to 0). The table
  in this note reproduces the MEAN values (t-term = 0) for readability; the true design
  minimum is roughly another 10-20 MPa lower (yield) depending on temperature and which of
  the two per-condition Student-t values (ν=31 or 32 for extruded, ν=19 for HIPed) is used
  at the desired confidence level — the integration pass should decide whether
  `engine_designer` wants the mean curve or the true statistical lower bound and cite
  accordingly.
- **Polynomial regressions are curve fits over the TESTED range (~20-1000/1200 K), not a
  physical model** — do not extrapolate meaningfully beyond ~1000-1100 K; the alloy's
  solidus is ~1080°C (1353 K) and the report itself only tested up to 1000°C (1273 K) for
  long-term exposures / annealing, with baseline tensile regression data apparently not
  extending past that.
- **This report supersedes/deliberately excludes earlier GRCop-84 tensile results**
  (References 8-9, differing due to a powder-supplier change) — if any existing
  `engine_designer` constant was sourced from an OLDER GRCop-84 tensile report or a generic
  "copper alloy" placeholder, this TM-2012-217108 dataset should take priority as the most
  rigorous, largest, and most recent (2012) tensile characterization of the actual
  currently-relevant GRCop-84 chemistry/process.
- **No thermal-conductivity, CTE, elastic-modulus (beyond the tube/foil spot values), creep,
  fatigue, or fracture-toughness data here** — this report is tensile-strength-only by
  design (companion "to be published" NASA GRC reports referenced for annealing behavior,
  creep properties, and low-cycle fatigue were NOT available/acquired for this note); the
  general-properties table already in `topics/12` (from the companion source
  `NASA TM-2005-213566`, distilled separately in this batch) remains the source for those
  other properties.
- **OCR was highly garbled for the four pages carrying the primary regression equations**
  (Eqs. 1-5b, pages 21-22 / leaves 24-25) — digit/exponent ordering was scrambled by the
  PDF's equation-image extraction. These two pages were independently re-rendered as
  250 dpi images and read visually to resolve the true coefficients; all numbers in the
  Key Results table above come from that image-verified read, not the raw OCR text. Later,
  secondary regression equations (braze/-270-mesh/large-extrusion/rolled-plate, Eqs. 6-36)
  were captured from OCR text only (not image-verified) since their narrative conclusions
  (magnitude of effects, statistical significance) were independently and clearly stated in
  surrounding prose — if a future user needs the EXACT coefficients for those secondary
  equations, re-render the corresponding pages as images first (this note flags but does
  not resolve them).
- **Statistical rigor is real but the underlying degrees of freedom are still modest** by
  general engineering standards — ~35 baseline as-extruded data points (5 powder lots ×
  ~7 temperatures) and ~23 as-HIPed points is a solid materials-test program but not a
  huge population; treat the lower-95%-confidence-limit curve as the intended
  design-minimum use case (that's explicitly why the authors computed it that way) rather
  than assuming enormous statistical margin beyond what's stated.
