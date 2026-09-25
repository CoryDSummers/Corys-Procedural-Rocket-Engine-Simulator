# Akhmedova-Azizova, Abdulagatov & Bruno (2009) — Effect of RP-1 Compositional Variability on Thermal Conductivity at High Temperatures and High Pressures

## Identity

L.A. Akhmedova-Azizova (Azerbaijan State Oil Academy), I.M. Abdulagatov, T.J. Bruno
(NIST Thermophysical Properties Division, Boulder CO), *Effect of RP-1 Compositional
Variability on Thermal Conductivity at High Temperatures and High Pressures*, Energy &
Fuels 2009, 23, 4522-4528, DOI 10.1021/ef900435b, published on the web 07/29/2009. 7
printed pages (journal pp. 4522-4528; PDF leaves 0-6, one-to-one with printed pages).
`literature/akhmedova-azizova.2009.p4522.pdf.pdf`. Tag: `[Akhmedova-RP1]`.

## Character

A short (7-page), data-dense NIST thermal-conductivity measurement paper — a coaxial-
cylinder (steady-state, not transient hot-wire) apparatus measuring RP-1's thermal
conductivity λ(T,P) from 292 to 732 K at pressures to 60 MPa. The paper's stated purpose,
per its title, is not just to report λ(T,P) but to demonstrate how much **compositional
variability between real RP-1 batches** changes the measured thermal conductivity — using
two real AFRL-supplied RP-1 samples that differ markedly in olefin/aromatic content. This
is a companion piece (same NIST group, same underlying AFRL RP-1/RP-2 characterization
program) to `[Huber-RP1RP2]` and `[Outcalt-RP1RP2]` (both in this same extraction batch)
and to a larger NIST report, NISTIR 6646 (Magee et al., *Thermophysical Properties
Measurements and Models for Rocket Propellant RP-1: Phase I*, 2007) — the "Magee et al."
reference cited throughout this paper as the only other published RP-1 thermal-conductivity
dataset. **NISTIR 6646 itself (`literature/nistir6646.pdf`) is being distilled separately
in this same batch by another agent — not read for this note.**

Read in full (all 7 pages) — short enough that no extraction-scope tradeoff was needed.
Text-layer extraction (pymupdf `get_text()`) was clean throughout; no OCR/rasterization
needed.

## Character — samples

Two RP-1 samples ("A" and "B"), both supplied by AFRL (Wright-Patterson), analyzed by
GC-MS-IR:
- **Sample A** — chemically *unusual*: ~20% of identified compounds had a double bond or
  aromatic ring (high olefin + aromatic content) — explicitly **not representative of
  on-specification RP-1**. This is the *same physical sample* used by Magee et al.
  (NISTIR 6646) for the only other published λ(RP-1) dataset.
- **Sample B** — typical, low-olefin/low-aromatic — representative of as-delivered RP-1.
- Both samples: <30 ppm (mass/mass) total sulfur, pale-red dye cast (azobenzene-4-azo-2-
  naphthol), kerosene-like viscosity/odor.
- The thermal-conductivity measurements themselves (Table 3, below) were made **only on
  sample A** — sample B's conductivity is only available via Huber's correlation model
  (`[Huber-RP1RP2]`, then "in preparation") used as a comparison overlay in Figure 1, not
  independently measured in this paper.

## Key results

**Apparatus/method** `[Akhmedova-RP1 Experimental Section p.4524-4525]`: coaxial-cylinder
steady-state technique — heat generated in an inner emitting cylinder (d2=10.98 mm) is
conducted radially through a thin (0.97 mm) fluid annulus to an outer receiving cylinder
(d1=12.92 mm), length 150 mm. Rayleigh number kept <500 (critical Ra=1000) via the thin
gap, verified experimentally by confirming λ is independent of ΔT (1-3 K) and heating
power. **No radiation correction was applied** to the reported data (explicitly stated,
twice) — RP-1's optical absorption properties (refractive index, absorption coefficient)
at high temperature are unknown, so the coupled radiation-conduction problem couldn't be
solved even numerically; Magee et al.'s data likewise lack this correction.

**Test matrix**: 8 isobars — 0.1, 6, 10, 20, 30, 40, 50, 60 MPa — over 292-732 K (sample
A only). Stated uncertainties (95% CL, k=2): thermal conductivity 2% (below 600 K), 4-5%
(above 650 K, where decomposition adds uncertainty); pressure 0.05%; temperature 30 mK.
Because no radiation correction is applied, the TRUE uncertainty on the reported λ values
is stated to be "larger than 2%" even in the low-temperature range — an unquantified extra
margin, not folded into the stated 2%/4-5% figures.

**Measured λ(T,P) table** `[Akhmedova-RP1 Table 3, p.4527]` — full digitized data across
all 8 isobars, 292-732 K. Representative values (sample A):
- 0.1 MPa: λ = 0.113 W·m⁻¹·K⁻¹ at 293.15 K, falling monotonically to 0.074 W·m⁻¹·K⁻¹ at
  692 K and 0.074 at 733 K (near-flat/scattered above the decomposition onset — see below).
- 60 MPa: λ = 0.131 W·m⁻¹·K⁻¹ at 293.05 K, falling to 0.092 W·m⁻¹·K⁻¹ at 733 K.
- At fixed T (e.g. ~293 K), λ **increases from 0.113 (0.1 MPa) to 0.131 W·m⁻¹·K⁻¹
  (60 MPa)** — roughly +16% over that 0-60 MPa span, "small deviation from linearity."
- At fixed P, λ decreases monotonically with T (standard hydrocarbon-liquid behavior).
- Points above ~650-690 K are flagged in Table 3 itself with an asterisk: "uncertainty is
  4-10% and more" — these high-T points are for a partially-decomposed fluid, not pristine
  RP-1.

**Thermal-decomposition onset — a real, independently corroborated threshold**
`[Akhmedova-RP1 Abstract; Results and Discussion p.4526]`: "the onset of the effects of
thermal decomposition (chemical reaction) on the thermal conductivity of RP-1 ... was found
above approximately 650 K." Below 600 K, repeat runs (same sample, reheated) agreed within
experimental uncertainty (2-2.5%) with no hysteresis. Above ~630 K, repeat runs on the SAME
sample showed 5-10%+ divergence, and pressure itself was observed to drift (0.1-0.2 MPa/hr
at 650 K) — a direct kinetic signature of ongoing chemical reaction in the sealed cell.
After completing a run to ~730 K, the cell was found coated with a black carbonaceous
deposit. **This 650 K decomposition-onset figure is consistent with, and adds an
independent NIST measurement corroborating, the coking-onset band (600-800 K, peak ~700 K)
already documented from a completely different rig type (electrically-heated flow tube) in
`[Lewis-Deposits]`** already in `topics/06`.

**Thermal-decomposition kinetics — quantified rate constants** `[Akhmedova-RP1 Table 1,
p.4523]`: pseudo-first-order decomposition rate constants k (s⁻¹) measured by a separate
ampule-reactor protocol, both samples:
| T (K) | Sample A k (s⁻¹) | Sample B k (s⁻¹) |
|---|---|---|
| 648.15 | (6.92±0.75)×10⁻⁵ | (1.13±0.04)×10⁻⁵ |
| 673.15 | (2.00±0.23)×10⁻⁴ | (1.19±0.33)×10⁻⁴ |
| 698.15 | (3.85±0.53)×10⁻⁴ | (3.08±0.77)×10⁻⁴ |
| 723.15 | (5.84±1.33)×10⁻⁴ | — |
| 773.15 | (1.07±0.17)×10⁻³ | (5.84...)* |

(*table OCR/formatting at 773.15K for sample B garbled in extraction — see Caveats.)
Sample A (the high-olefin sample) decomposes **~6× faster at 648 K** than sample B —
directly attributing the faster decomposition rate to olefin/aromatic content. Practical
guidance given in the text: fluids are "relatively stable" for property measurement up to
~673 K; above that, residence time matters; near 773 K, residence times must be kept under
2-3 minutes in a typical property-measurement instrument.

**Compositional shift upon thermal stress — real ASTM-2789 hydrocarbon-type data**
`[Akhmedova-RP1 Table 2, p.4525]`: sample A, unstressed vs. after exposure to 784.15 K
(volume fractions):
| Fraction | Unstressed | After 784.15 K |
|---|---|---|
| Paraffins | 40.3% | 4.0% |
| Monocycloparaffins | 32.8% | 12.6% |
| Dicycloparaffins | 19.4% | 9.0% |
| Aromatics (1 ring) | 5.7% | 41.5% |
| Indanes/tetralins | 0.8% | 12.7% |
| Naphthalenes | 1.0% | 20.2% |

A dramatic paraffin→aromatic/naphthalene conversion — the fluid that has undergone thermal
stress above ~730 K is chemically a very different mixture from as-delivered RP-1, which is
directly relevant to any assumption that a regen-jacket coolant retains constant properties
along its flow path if wall temperatures locally exceed ~650-700 K.

**THE HEADLINE COMPOSITIONAL-VARIABILITY FINDING** `[Akhmedova-RP1 Results and Discussion
p.4526]`: comparing sample A's measured λ against Huber's correlation model
(`[Huber-RP1RP2]`) evaluated for sample B (the more typical composition): **"the thermal
conductivity of the second RP-1 sample (B) calculated with the correlation model is
systematically LOWER (by about 2-4% along the isobar at 10 MPa) than for the first RP-1
sample (A)."** This is the paper's own explicit "compositional variability" bound —
directly citable as an uncertainty envelope for any single RP-1 thermal-conductivity number
used in a coolant model: **expect real batch-to-batch RP-1 thermal conductivity to vary by
at least ~2-4% purely from composition**, even before considering the much larger
(5-10%+) swings once wall/bulk temperature exceeds ~650 K decomposition onset.

**Empirical predictive scaling model** `[Akhmedova-RP1 eq.3, p.4527-4528]`: Viswanath-Rao
form λ(P,T)/λ₀(P,T₀) = (T/T₀)⁻ⁿ, fit to this work's sample-A data with T₀ = 293 K and
**n = 0.55** (compare: literature n ranges 0.6 for alcohols to 0.943 for paraffins — RP-1's
fitted n=0.55 falls slightly outside/below that homologous-series range, consistent with
being a complex mixture rather than a pure compound). This equation reproduces the
measured data to AAD 0.4-2.5% (depending on pressure) across the FULL measured range
(292-732 K, 0.1-60 MPa) — i.e. it usefully extrapolates even through the decomposition
region, though only in a curve-fit sense (it does not model the underlying chemistry).

**Cross-check against literature (Magee et al./NISTIR 6646)** `[Akhmedova-RP1 Results and
Discussion p.4526-4527]`: AAD between this paper's data and the Magee et al. correlation
(sample-A-based) = 1.0% over 292-630 K (max deviation 3.8%, bias -0.2%); above 630 K,
deviations grow to 5-10%+ due to decomposition. Huber's correlation model's own stated
accuracy for λ (both samples) is ~3%, valid to ~600 K (a tighter upper bound than this
paper's own 732 K measurement ceiling).

## Design method

Not a design-correlation source for chamber/nozzle sizing — the usable outputs for
`engine_designer` are: (1) a real measured RP-1 λ(T,P) lookup table (Table 3, 292-732 K,
0.1-60 MPa) as an alternative/cross-check to a Cantera/CoolProp-generated coolant property
table; (2) a real, independently-derived thermal-decomposition-onset threshold (~650 K) that
corroborates (from a completely different apparatus/mechanism) the coking-limit band already
cited from `[Lewis-Deposits]`/`[SP-8087]` in `topics/06`; (3) the explicit
**compositional-variability bound (~2-4% at fixed T,P between two real batches)**, directly
usable as an "any single RP-1 property number carries at least this much real batch-to-batch
uncertainty" caveat wherever a baked RP-1 coolant thermal-conductivity value is quoted or
used in `engine_designer/physics/property_data/*.json`; (4) the simple power-law scaling
model (n=0.55, T₀=293 K) as a cheap way to extrapolate a single reference-condition λ value
across temperature if a fuller table isn't wanted.

## Section map

- Abstract/Introduction (leaf 0, pp.4522-4523): read — states the measurement envelope,
  headline uncertainty numbers, and the single prior literature dataset (Magee et al.).
- Experimental Section — RP-1 samples, chemical analysis method, decomposition kinetics
  protocol, thermal conductivity apparatus (leaves 0-3, pp.4522-4525): read in full,
  including Table 1 (decomposition rate constants) and Table 2 (ASTM-2789 hydrocarbon-type
  shift).
- Results and Discussion (leaves 3-6, pp.4525-4528): read in full, including Table 3 (full
  λ(T,P) data table, all 8 isobars) and the compositional-variability comparison,
  correlation cross-checks, and the n=0.55 predictive model derivation.
- Conclusions (leaf 6, p.4528): read — restates the headline findings.
- Figures 1-3 (λ-T at two isobars w/ 3 runs and 2 surrogate-model overlays; λ-P at 5
  isotherms; % deviation plot vs. surrogate model): referenced in the text discussion above
  but not independently re-rendered as images — all quantitative claims came from prose/
  table text, not digitized from the plots.

## Caveats

- **No radiation correction applied** to any reported λ value — the paper states plainly
  that the true uncertainty is therefore larger than the quoted 2% (low-T) / 4-5% (high-T)
  figures, by an unquantified amount, because RP-1's optical absorption properties at high
  temperature aren't characterized.
- **Sample A (the one actually measured across the full T-P grid, Table 3) is explicitly
  non-representative of on-specification RP-1** — it has an unusually high olefin/aromatic
  content (~20% of identified compounds). The "typical" sample B was NOT independently
  measured for thermal conductivity in this paper; its properties here come only from
  a Huber-correlation-model overlay (evaluated for sample B's chemistry), not from raw
  data on sample B. Treat sample A's absolute λ values as upper-bound-ish for a "typical"
  fuel, per the paper's own 2-4%-higher finding.
- **Above ~650-690 K the fluid is chemically decomposing during measurement** — those
  high-T λ values (flagged with an asterisk in Table 3, "uncertainty 4-10% and more") are
  properties of a partially cracked, compositionally-drifting fluid, not pristine RP-1; not
  a stable/repeatable "material property" in the usual sense above that band.
  Real-engine regen-jacket coolant temperatures approaching or exceeding this threshold
  should not be assumed to retain a fixed-composition RP-1 thermal conductivity.
  This 650 K onset is corroborated independently by `[Lewis-Deposits]`'s coking-rate rig
  (600-800 K onset/peak band, different apparatus/mechanism) — treat the two together as
  converging evidence, not a single point estimate.
  Because a rate-constant table entry for sample B at 773.15 K was garbled by the PDF text
  extraction (columns misaligned in Table 1's bottom row), that one specific number was not
  transcribed with confidence above and should be re-checked against the source PDF (leaf 1)
  if ever needed precisely; every other number in this note was verified directly from clean
  extracted text.
- **Only two samples compared** — the "2-4% compositional variability" bound is a real,
  citable finding, but it rests on exactly two AFRL samples (one of them explicitly
  atypical), not a broad statistical survey of production RP-1 lots. Treat it as a lower
  bound on real variability, not a comprehensive spec.
- **A larger companion NIST report exists in this same extraction batch**: NISTIR 6646
  (Magee et al. 2007, *Thermophysical Properties Measurements and Models for Rocket
  Propellant RP-1: Phase I*) — being distilled separately by another agent in parallel; not
  read for this note, but is the source of the "Magee et al." comparison data/correlation
  referenced throughout this paper (and is the origin of the same sample-A fluid used here).
- No chamber/nozzle/injector/regen-jacket geometry content whatsoever — a pure fluid-
  property measurement paper.
