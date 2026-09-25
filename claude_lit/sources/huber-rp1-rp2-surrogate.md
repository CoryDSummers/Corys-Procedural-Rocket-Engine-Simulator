# Huber, Lemmon, Ott & Bruno (2009) — Preliminary Surrogate Mixture Models for the Thermophysical Properties of Rocket Propellants RP-1 and RP-2

## Identity

M.L. Huber, E.W. Lemmon, L.S. Ott, T.J. Bruno (NIST Thermophysical Properties Division,
Boulder CO), *Preliminary Surrogate Mixture Models for the Thermophysical Properties of
Rocket Propellants RP-1 and RP-2*, Energy & Fuels 2009, 23, 3083-3088, DOI
10.1021/ef900216z, published on the web 05/19/2009. 6 printed pages (journal pp.
3083-3088; PDF leaves 0-5, one-to-one with printed pages).
`literature/huber.energy&fuels.2009.p3983.pdf.pdf`. Tag: `[Huber-RP1RP2]`.

## Character

A short (6-page) NIST paper developing **surrogate mixture models** — small sets (4-5) of
real, well-characterized hydrocarbon compounds whose combined thermodynamic/transport
properties (via a REFPROP-style mixture EOS + extended corresponding-states transport
model) are tuned to reproduce measured RP-1 and RP-2 bulk properties. This is exactly the
kind of composition model that would underlie any REFPROP-family (and, by extension, a
Cantera/CoolProp-based) RP-1/RP-2 property correlation — directly relevant context for
`engine_designer/physics/property_data/*.json`'s baked coolant tables. Same NIST group,
same AFRL RP-1/RP-2 characterization program, as the companion papers in this same
extraction batch: `[Outcalt-RP1RP2]` (the underlying measured density/sound-speed/
viscosity data this paper fits against) and `[Akhmedova-RP1]` (a related thermal-
conductivity variability study, citing this paper's model as "Huber's correlation model").
Also a companion to the larger NIST report NISTIR 6646 (Magee et al. 2007) — **being
distilled separately in this same batch by another agent; not read for this note.**

Read in full (all 6 pages) — short enough that no extraction-scope tradeoff was needed.
Text-layer extraction (pymupdf `get_text()`) was clean throughout (occasional ligature
artifacts like "ﬂuid"→"ﬂuid" rendered correctly as Unicode; no OCR needed).

## Key results

**RP-1 vs RP-2 — what actually differs, per specification and per real samples**
`[Huber-RP1RP2 Introduction, p.3083]`: RP-2 originated as an ultralow-sulfur (<100 ppb
mass/mass) RP-1 reformulation ("UL RP-1") developed for reusable engines; it ended up
adopted as its own spec with the RP-1 sulfur limit correspondingly lowered from 500 to 30
ppm. RP-1 and RP-2 share identical specifications for distillation behavior, viscosity,
density, freezing point, and net heat of combustion — but RP-2 commonly has lower aromatic
content in practice despite an identical spec limit. Real samples used in this study: RP-1
had 24 major GC-MS peaks (>1% area) spanning C11-C15 (predominantly linear/branched
paraffins + 1-2-ring cyclic paraffins); RP-2 had 28 major peaks spanning C11-C16 with
**no significant aromatic or olefin content** — i.e. the real RP-2 sample skewed to larger
molecules than the real RP-1 sample.

**Surrogate compositions — the actual real-hydrocarbon composition model**
`[Huber-RP1RP2 Table 2, p.3086]` (mole fractions):
| Component | RP-1 surrogate | RP-2 surrogate |
|---|---|---|
| α-methyldecalin | 0.354 | 0.354 |
| 5-methylnonane | 0.150 | 0.084 |
| 2,4-dimethylnonane | 0.000 | 0.071 |
| n-dodecane | 0.183 | 0.158 |
| heptylcyclohexane | 0.313 | 0.333 |

The RP-1 surrogate is thus **4 real components** (α-methyldecalin, 5-methylnonane,
n-dodecane, heptylcyclohexane); the RP-2 surrogate adds a 5th (2,4-dimethylnonane),
otherwise reusing the same 4 species at slightly different fractions. Both surrogates were
selected via multiproperty nonlinear regression (minimizing summed squared % deviation vs.
measured distillation curve + density + speed of sound + viscosity + thermal conductivity)
starting from a candidate pool of 18 representative compounds (Table 1: 5-methylnonane
through n-hexadecane, C10-C16, spanning linear/branched/mono-/dicyclic paraffin families,
each picked to represent a whole "x-methylnonane"/"x,y-dimethylnonane"-type isomer family
found in the real GC-MS analysis). Each candidate species required its own fitted
Helmholtz-form (Span-Wagner-style) EOS plus viscosity/thermal-conductivity surfaces
(extended corresponding-states with n-dodecane as reference fluid) before mixture
regression was possible.

**Calculated bulk properties of each surrogate** `[Huber-RP1RP2 Table 3, p.3086]`:
| Property | RP-1 surrogate | RP-2 surrogate |
|---|---|---|
| MW | 163.5 | 164.6 |
| Formula | C₁₁.₆₆H₂₃.₃₂ | C₁₁.₇₄H₂₃.₄₀ |
| H/C ratio | 2.00 | 1.99 |
| Heat of combustion | -7.18×10⁶ J/mol | -7.23×10⁶ J/mol |
| Density @ 288.7 K (60°F), 101.325 kPa | 808.1 kg/m³ | 809.5 kg/m³ |
| Speed of sound @ 288.7 K | 1330.9 m/s | 1330.3 m/s |
| Thermal conductivity @ 288.7 K | 112.76 mW/m·K | 111.34 mW/m·K |
| Viscosity @ 288.7 K | 1.90 mPa·s | 1.98 mPa·s |
| Initial boiling point | 475.6 K | 476.7 K |
| Kinematic viscosity @ 238.7 K (-30°F) | 0.098 cm²/s | 0.106 cm²/s |
| Tc | 677 K | 678 K |
| pc | 2210 kPa | 2204 kPa |
| ρc | 235 kg/m³ | 240 kg/m³ |

These calculated density/kinematic-viscosity/hydrogen-aromatic-olefin-content/heat-of-
combustion values were checked to meet the MIL-DTL-25576E military specification for both
fuels. Critical-point values (Tc, pc, ρc) are model-calculated from the surrogate
composition — RP-1 and RP-2 are essentially indistinguishable in Tc/pc within this model
(677 vs 678 K; 2210 vs 2204 kPa), though ρc differs slightly more (235 vs 240 kg/m³).

**Model accuracy vs. real measured data (the headline validation numbers)**
`[Huber-RP1RP2 Conclusions, p.3087]`, at 95% confidence level, against the measured data of
`[Outcalt-RP1RP2]` (density, sound speed, viscosity) and the companion thermal-conductivity
measurements (Perkins, in preparation at time of writing / related to `[Akhmedova-RP1]`)
and distillation curves (Bruno & Smith; Ott et al.):
- **Density: within 0.4%** (measured 270-470 K, to 40 MPa, experimental uncertainty 0.1%;
  at atmospheric pressure the RP-1/RP-2 surrogate models deviate from data by only 0.1%,
  at the level of experimental uncertainty).
- **Speed of sound: within 2%** (atmospheric pressure only, experimental uncertainty
  0.1% — none of the surrogate models tested, including this one, reach experimental
  uncertainty for this property).
- **Viscosity: within 2%** (experimental uncertainty ~1.5%) — described as "one of the most
  sensitive [properties] to the compositional differences between RP-1 and RP-2."
- **Thermal conductivity: within 4%** (measured 300-550 K, to 60 MPa, transient hot-wire,
  experimental uncertainty ~1%).
- **Distillation curve (volatility): within 0.5%**.
- **Range of applicability: T to 800 K, P to 60 MPa** — bounded by the validity range of
  the constituent pure-fluid equations of state, not independently re-verified against RP-1/
  RP-2 data across that full range in this paper.

**Comparison against two prior published RP-1 surrogates** `[Huber-RP1RP2 p.3086-3087]` —
this paper's stated motivation/contribution is that it beats both:
- **Farmer et al. (13-component surrogate, incl. 3 aromatic species + 2 unspecified
  polycyclic paraffins)**: overpredicts distillation temperatures by >20 K; overpredicts
  viscosity by 18-30% (largest deviations at lowest temperatures); density within 0.5%
  (comparable to this work).
- **Huang & Sobel (6-component, ~80 mol% linear alkanes, developed for endothermic
  fuel-cooled applications)**: underpredicts density by 6-8%; underpredicts viscosity by
  up to ~20% at low temperature; thermal conductivity overpredicted with larger positive
  deviations than this work's model; distillation-curve shape slightly off but temperatures
  within 1.5%.
- A third comparison, the "raw peak analysis surrogate" (just the ≥1%-area GC-MS peaks
  renormalized to 100%, not independently property-modeled), performs worst across every
  property — underscoring that naively using only the major detected peaks (without
  choosing representative species per chemical family and re-fitting) is NOT an adequate
  surrogate-construction method.

**RP-1 vs RP-2 real property differences, as reflected through the fitted models**
`[Huber-RP1RP2 p.3086-3087]` (citing `[Outcalt-RP1RP2]`'s measured data): RP-1 density is
about 0.2% LOWER than RP-2 at atmospheric pressure; RP-1 atmospheric-pressure viscosity is
3.3-4.9% LOWER than RP-2 over 293.4-373.15 K (largest difference at lowest temperature);
RP-1 speed of sound is very slightly LOWER than RP-2 (differences <0.3%, "not greatly
affect[ed]" by the compositional difference); RP-1 thermal conductivity is "slightly
greater" than RP-2's at similar conditions; distillation curves for the two fuels are
"almost identical."

## Design method

This paper is not itself a component-by-component design tool, but its outputs are directly
usable groundwork for `engine_designer`: (1) a real, citable 4-5-component hydrocarbon
composition model for RP-1/RP-2 (Table 2 above) — the kind of surrogate a Cantera-based
combustion/property calculation could adopt directly rather than treating RP-1 as a single
pseudo-species; (2) calculated reference-condition bulk properties (Table 3 above) as a
sanity-check anchor for any baked RP-1/RP-2 coolant property table; (3) real,
quantified model-accuracy bounds (density 0.4%, speed of sound/viscosity 2%, thermal
conductivity 4%, distillation 0.5%) as a citable uncertainty envelope for property-table
generation from a surrogate-composition approach generally; (4) the quantified RP-1-vs-RP-2
property differences (viscosity most sensitive, ~3-5% lower for RP-1; density/sound speed
differ <1%) as real grounds for treating RP-1 and RP-2 as *slightly* but not dramatically
different coolants if `engine_designer` ever distinguishes them.

## Section map

- Introduction (leaves 0-1, pp.3083-3084): read — RP-1/RP-2 history, spec background, prior
  surrogate literature survey (Farmer et al., Huang & Sobel).
- Modeling — surrogate development procedure, candidate compound selection (Table 1),
  chemical analysis summary (leaves 1-3, pp.3084-3085): read in full.
- Results — surrogate compositions (Table 2), calculated properties (Table 3), and
  comparison figures 1-5 discussed in prose (leaves 3-5, pp.3085-3087): read in full;
  figures themselves (deviation plots for density/sound speed/viscosity/thermal
  conductivity, and distillation curves) referenced only via their prose discussion, not
  independently re-rendered as images.
- Conclusions (leaf 5, p.3087): read — restates the headline accuracy numbers and range of
  applicability.

## Caveats

- **Explicitly "preliminary"** (title) — a single AFRL sample of each fuel was used to fit
  each surrogate; the paper's own final paragraph flags "future work is needed to determine
  how much variability there is for different samples of the two rocket propellants" as an
  open question, i.e. the authors themselves do not claim this surrogate generalizes across
  all real-world RP-1/RP-2 production lots. (`[Akhmedova-RP1]`, same NIST group, later
  quantifies part of that variability for thermal conductivity specifically: ~2-4% between
  two samples.)
- **Candidate-compound selection favored data availability over exact chemical match** — for
  each detected isomer family (e.g. "x-methylnonanes"), a single representative species was
  chosen partly based on which compound had the most reliable existing property data, not
  purely on which was chemically most representative; explicitly acknowledged as a modeling
  simplification.
- **Range of applicability (800 K / 60 MPa) is inherited from constituent pure-fluid EOS
  validity, not independently validated against RP-1/RP-2 property data across that whole
  range** in this paper — the underlying measured data used for fitting only extended to
  550 K (thermal conductivity) / 470 K (density/speed of sound, per `[Outcalt-RP1RP2]`).
- **This paper does not itself present new thermal-conductivity measurements** — it cites a
  companion Perkins paper ("in preparation" at time of writing) and depends on
  `[Akhmedova-RP1]`'s NIST group's parallel thermal-conductivity work for that property's
  fit target.
- **A larger companion NIST report exists in this same extraction batch**: NISTIR 6646
  (Magee et al. 2007) — being distilled separately by another agent in parallel; not read
  for this note. This paper's own earlier RP-1 surrogate work (cited as ref 24, using an
  "atypical" RP-1 sample) is explicitly disavowed here as "of limited usefulness" for not
  representing current as-delivered RP-1 — a caution against assuming any single published
  RP-1 property number/model is universally representative.
- No chamber/nozzle/injector/regen-jacket geometry or heat-transfer-correlation content —
  purely a fluid-composition/property-modeling paper.
