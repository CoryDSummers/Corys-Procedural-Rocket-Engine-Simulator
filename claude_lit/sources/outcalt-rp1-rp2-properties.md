# Outcalt, Laesecke & Brumback (2009) — Thermophysical Properties Measurements of Rocket Propellants RP-1 and RP-2

## Identity

Stephanie L. Outcalt, Arno Laesecke (NIST, Boulder CO), Karin J. Brumback (Yale
University), *Thermophysical Properties Measurements of Rocket Propellants RP-1 and RP-2*,
Journal of Propulsion and Power, Vol. 25, No. 5, September-October 2009, pp. 1032-1040, DOI
10.2514/1.40543. 9 printed pages (PDF leaves 0-8, one-to-one with printed pages 1032-1040).
`literature/Outcalt & al. 2009 1032.pdf.pdf`. Tag: `[Outcalt-RP1RP2]`.

## Character

A NIST/AIAA measurement paper providing real measured **density, speed of sound, and
viscosity** data for RP-1 and RP-2 — the actual experimental dataset that
`[Huber-RP1RP2]` (same NIST group, same batch of AFRL fuel samples) fits its surrogate
mixture models against, and that `[Akhmedova-RP1]` references for context on RP-1 vs RP-2
compositional differences. Companion to the larger NIST report NISTIR 6646 (Magee et al.
2007) — **being distilled separately in this same batch by another agent; not read for
this note.** This is a pure measurement/correlation paper (three separate instruments,
three separate property classes), not a surrogate-modeling or design-method paper.

Read in full (all 9 pages) — short enough that no extraction-scope tradeoff was needed.
Text-layer extraction (pymupdf `get_text()`) was clean throughout; some Greek-letter symbol
glyphs (ρ, ν, α_p, β_s) render as stray characters or drop out in the raw extracted text
(e.g. equation nomenclature lines), but every quantitative value in the data tables
extracted cleanly and unambiguously.

## Key results

**Test samples and composition difference** `[Outcalt-RP1RP2 Test Samples, p.1032]`: both
fuels supplied by AFRL Fuels Branch (Wright-Patterson), analyzed by GC-MS-IR. **RP-1
sample: alkanes up to C14 (methyltridecane isomers) + ~1% (peak area) aromatic content
(1-methylnaphthalene). RP-2 sample: alkanes up to C16 (hexadecane), no reported aromatic
hydrocarbons, lower sulfur than RP-1** (RP-1 also carries a pink dye additive RP-2 lacks).
Critical-temperature estimate from constituent range: RP-1 ≈ 639-772 K (n-undecane to
1-methylnaphthalene); RP-2 upper bound ≈ 722 K (hexadecane) — the paper explicitly expects
**RP-2 to have a LOWER critical temperature than RP-1** despite RP-2's heavier average
molecule, because RP-2 lacks RP-1's higher-Tc aromatic tail component.

**Atmospheric-pressure density + speed of sound** `[Outcalt-RP1RP2 Table 1, p.1033]`, DSA
5000 instrument, 278.15-343.15 K, 0.083 MPa (Boulder altitude), uncertainty 0.1% (both
properties):
| T (K) | RP-1 ρ (kg/m³) | RP-1 w (m/s) | RP-2 ρ (kg/m³) | RP-2 w (m/s) |
|---|---|---|---|---|
| 278.15 | 815.50 | 1381.3 | 817.10 | 1383.3 |
| 293.15 | 804.59 | 1321.7 | 806.23 | 1324.1 |
| 313.15 | 790.05 | 1245.0 | 791.67 | 1247.4 |
| 333.15 | 775.44 | 1171.1 | 777.07 | 1173.8 |
| 343.15 | 768.09 | 1135.6 | 769.80 | 1138.2 |

RP-2 is consistently ~0.2-0.3% denser and ~0.15-0.2% faster in sound speed than RP-1 at
every measured temperature — a small but real, monotonic difference.

**Derived adiabatic compressibility** `[Outcalt-RP1RP2 Table 1, eq.1, p.1033]`: computed
from ρ and w via β_s = 1/(ρw²); rises from ~642.7 TPa⁻¹ (278.15 K) to ~1009.7 TPa⁻¹
(343.15 K) for RP-1 (RP-2 slightly lower at each T, e.g. 639.19 vs 642.67 TPa⁻¹ at
278.15 K) — density and sound-speed effects both increase compressibility with T, and RP-2
being marginally denser/stiffer makes it marginally less compressible than RP-1 throughout.

**Compressed-liquid density, 270-470 K, to 40 MPa** `[Outcalt-RP1RP2 Tables 2-3, p.1034-
1035]`, automated vibrating-tube densimeter, expanded uncertainty 0.64-0.81 kg/m³ (k=2).
Representative endpoints:
- RP-1: 843.2 kg/m³ (270 K, 40 MPa) down to 668.0 kg/m³ (470 K, 0.083 MPa).
- RP-2: 844.0 kg/m³ (270 K, 40 MPa) down to 670.2 kg/m³ (470 K, 0.083 MPa).
RP-2 is denser than RP-1 by a roughly constant small margin (~0.1-0.3%) across the entire
270-470 K / 0-40 MPa grid — consistent with, and a direct extension of, the atmospheric-
pressure comparison above. Tables give full isothermal pressure sweeps every 20 K, plus a
density value extrapolated to 0.083 MPa at each isotherm (via a fitted 2nd-order polynomial
on data ≤10 MPa) for cross-checking consistency against the atmospheric-pressure DSA 5000
data — the two independent instruments/datasets agree to within their combined
uncertainty.

**Viscosity — the property most sensitive to RP-1/RP-2 compositional difference**
`[Outcalt-RP1RP2 Table 4, p.1036]`, open capillary (Ubbelohde) viscometer, 293.15-373.15 K,
atmospheric pressure, expanded uncertainty 1.5% (k=2):
| T (K) | RP-1 ν (mm²/s) | RP-1 η (mPa·s) | RP-2 ν (mm²/s) | RP-2 η (mPa·s) |
|---|---|---|---|---|
| 293.15-293.38 | 2.166 | 1.743 | 2.267 | 1.828 |
| 313.12-313.15 | 1.549 | 1.225 | 1.607 | 1.272 |
| 333.15 | 1.173 | 0.9100 | 1.215 | 0.9446 |
| 353.15 | 0.9335 | 0.7103 | 0.9683 | 0.7383 |
| 373.15-373.16 | 0.7678 | 0.5727 | 0.7916 | 0.5918 |

**THE HEADLINE QUANTITATIVE RP-1 vs RP-2 COMPARISON** `[Outcalt-RP1RP2 Results/Data
Correlation, p.1035-1036]`, stated explicitly: "**the viscosity values exhibit the greatest
difference between the two fuels**... The viscosities of RP-1 are between **3 and 5% lower**
than those of RP-2 at the same temperatures, whereas their density, speed of sound, and
adiabatic compressibility values differ by **less than 1%**." The paper attributes this
directly to RP-2's higher fraction of larger alkane molecules (up to C16 vs. RP-1's C14),
noting viscosity is far more sensitive than density/sound-speed to molecular size/shape/
polarity differences between similar hydrocarbon mixtures.

**Fitted correlations** — all reproduce the measured data within/near experimental
uncertainty and are given with full regression parameters + standard deviations:
- **Speed of sound**: quadratic polynomial in T `[Table 5]` — fits with AAD 3.9×10⁻³%
  (RP-1) / 2.9×10⁻³% (RP-2). Extrapolation checked reasonable to 470 K.
- **Atmospheric density**: Rackett equation `[Table 6]` — since RP-1/RP-2 critical
  temperatures weren't independently known, the Rackett "critical temperature" parameter
  was left as a free regression fit rather than constrained (RP-1 fitted value: 574.26 K;
  RP-2: 575.46 K — NOT the true thermodynamic Tc, just the Rackett-equation fit parameter).
- **Compressed-liquid density**: Tait equation `[Table 7]`, fit to within **0.07% (RP-1)**
  / **0.05% (RP-2)** across the full measured T-P grid; the authors note the Tait form's
  well-known reliable extrapolation behavior (cross-checked in an earlier paper of theirs
  to remain valid to 100 MPa given data only to 40 MPa) but caution here against
  extrapolating temperature more than ~20 K beyond the measured 270-470 K range.
- **Viscosity**: two forms fit — Vogel-Fulcher-Tammann (VFT, `Table 8`, 3 parameters, RMS
  0.104% RP-1 / 0.19% RP-2) and a 5-parameter DIPPR/NIST-ThermoData-Engine form (`Table 9`,
  RMS 0.093% RP-1 / 0.14% RP-2) — the DIPPR form's parameters are individually less
  statistically significant (large standard errors relative to fitted values, since 5
  parameters were fit to only 9 data points per fluid) but is preferred for extrapolation
  because VFT systematically over-predicts viscosity when extended above the measured
  range (VFT has no inflection point, unlike real liquid viscosity-T curves).
- **Isobaric thermal expansivity** α_p: derived analytically by differentiating the Tait
  equation; isotherms for both fluids cross near ~70 MPa (a common real-liquid feature,
  slightly lower pressure for RP-2) — only isotherms 270-390 K actually cross at that single
  point; higher-T isotherm crossovers shift to higher pressure.

## Design method

This is the primary numeric source for `engine_designer` to ground/cross-check a baked
RP-1 (or RP-2) coolant density/viscosity/speed-of-sound table: real NIST measurements
(Tables 1-4) plus fitted, low-error correlations (Rackett/Tait/quadratic/VFT-or-DIPPR forms,
with full parameter tables) spanning 270-470 K and 0-40 MPa — squarely the pressure/
temperature envelope relevant to a regen-cooling jacket. Where `engine_designer`'s baked
Cantera/CoolProp tables need an independent sanity check for RP-1 liquid-phase transport/
thermodynamic properties in that range, this paper's Tables 2 (RP-1 density), 4 (RP-1
viscosity), and 1 (RP-1 speed of sound/atmospheric density) are the ground-truth numbers to
check against. The quantified RP-1-vs-RP-2 differences (viscosity 3-5% lower for RP-1,
density/sound-speed <1% different) also directly support treating RP-1 and RP-2 as
near-interchangeable for bulk thermal/hydraulic jacket sizing, with viscosity being the one
property where a real, non-negligible (3-5%) difference should be expected if the two are
ever distinguished.

## Section map

- Introduction, Test Samples (leaves 0-1, pp.1032-1033): read — composition differences,
  critical-temperature estimates, measurement program overview.
- Experimental — three instruments (DSA 5000 density/sound-speed analyzer, automated
  compressed-liquid densimeter, capillary viscometer), calibration, uncertainty budgets
  (leaves 1-2, pp.1033-1034): read in full.
- Results — Tables 1-4 (all measured data) (leaves 1-4, pp.1033-1036): read in full,
  transcribed representative values and both endpoints of each table above.
- Data Correlation — speed of sound, density (Rackett/Tait), viscosity (VFT/DIPPR forms),
  isobaric thermal expansivity (leaves 4-7, pp.1036-1038): read in full, including all
  regression-parameter tables (5-9).
- Conclusions (leaf 7, p.1038): read — restates the headline density/viscosity comparison
  and the extrapolation caveats.
- References (22 citations, incl. the authors' own prior methyl-/propylcyclohexane
  instrument-validation paper and Outcalt & McLinden's densimeter design paper): leaf 8 —
  read (titles only, not chased as new sources).

## Caveats

- **Measured T-P range (270-470 K density/sound speed; 293-373 K viscosity, all ≤40 MPa) is
  well below the ~650-700 K thermal-decomposition onset** documented independently in
  `[Akhmedova-RP1]` — this paper has NO high-temperature (>470 K) density or viscosity data,
  and does not address thermal stability/decomposition at all. Do not extrapolate its
  correlations into the decomposition regime.
- **Single sample of each fuel** — the paper's own Data Correlation section explicitly
  warns: "Because of the variability in samples of rocket propellants... the correlations
  provided here are specific to the samples studied in this work and should not be
  generically applied to hydrocarbon rocket propellants" — a direct, source-stated caution
  against treating any of these fitted correlations as universal RP-1/RP-2 properties.
  Extrapolation is also explicitly discouraged wherever thermal restructuring (cracking)
  might occur.
- **No thermal conductivity data whatsoever** in this paper — that property is covered by
  the companion `[Akhmedova-RP1]` paper (and the still-unpublished-at-the-time Perkins
  paper it references) in this same NIST measurement program.
- **Rackett-equation "critical temperature" fit parameters (574-575 K) are NOT the true
  thermodynamic critical temperatures of RP-1/RP-2** (which the paper itself estimates
  elsewhere at 639-772 K from constituent-species Tc range) — they are free regression
  parameters of the Rackett correlating equation, left unconstrained specifically because
  the true Tc wasn't independently known; do not confuse the two numbers if ever citing
  this paper's Table 6.
- **DIPPR-form viscosity correlation parameters (Table 9) are individually not
  statistically significant** (standard errors comparable to or exceeding the fitted
  values) since 5 free parameters were regressed against only 9 measured points per fluid;
  the paper keeps this form anyway for its better extrapolation behavior versus the
  better-determined-but-worse-extrapolating VFT form (Table 8) — treat DIPPR-form
  extrapolations with the same caution the authors themselves apply.
- **A larger companion NIST report exists in this same extraction batch**: NISTIR 6646
  (Magee et al. 2007) — being distilled separately by another agent in parallel; not read
  for this note.
- No chamber/nozzle/injector/regen-jacket geometry or heat-transfer-correlation content —
  purely a fluid-property measurement/correlation paper (density, speed of sound,
  viscosity, and their derived thermodynamic quantities only).
