# Masters, Armstrong & Price — High-Pressure Calorimeter Chamber Tests for LOX/RP-1

## Identity

P.A. Masters, E.S. Armstrong, H.G. Price (NASA Lewis Research Center), *High-Pressure
Calorimeter Chamber Tests for Liquid Oxygen/Kerosene (LOX/RP-1) Rocket Combustion*, NASA
Technical Paper 2862, December 1988. `literature/NASA TP-2862 - High-Pressure Calorimeter Chamber Tests for LOX-RP-1 Rocket Combustion.pdf` (NTRS 19890006608; 20 pages, born-digital
with OCR-garbled figure text — body text is clean but scanned tables/plot labels are
mangled, e.g. "5" reads as "s", "C*" reads as "C_ff"). Tag: `[TP2862-LOXRP1]`.

## Character

A real experimental hot-fire heat-flux measurement paper — exactly the kind of ground-truth
data source `06-cooling-and-heat-transfer.md`'s Bartz-calibration discussion is built to be
checked against, in contrast to the CFD-methodology papers (`[Merkle-RegenCFD]`, `[SECA-HT]`)
already in this reference set. Two water-cooled copper calorimeter chambers (33.0 cm short /
43.2 cm long, 6.59 cm throat diameter, 15° half-angle nozzle beyond throat) with segmented
circumferential coolant passages (26 or 34 axial measuring stations) were fired at NASA
Lewis's Rocket Engine Test Facility with 37-element and 61-element O-F-O (oxidizer-fuel-
oxidizer) triplet-impinging injectors, at three nominal Pc levels (4.1, 8.3, 13.8 MPa abs =
600/1200/2000 psia) across O/F = 1.8–3.3. Each axial station's individual coolant flow and
inlet/outlet ΔT gives a true **measured axial heat-flux profile**, not a Bartz-predicted one
— this is calorimetry, not a correlation paper. A second injector variant with the outer
ring's oxidizer orifices sealed (fuel-rich outer zone = passive film-cooling barrier, "zoned
combustion") was also tested for its heat-flux and C* effect.

## Key results

**Test matrix / conditions** `[TP2862-LOXRP1 p.2, Table III p.9]`: uniform-mixture-ratio (UMR)
tests at Pc≈4.3 MPa (627 psia, short chamber, 37-elem injector 1) and Pc≈8.9 MPa (1287 psia,
short chamber, injector 2), O/F 2.4–3.3. Long-chamber/61-element zoned-combustion tests at
Pc≈8.3 MPa (1200 psia) and Pc≈13.5–14.1 MPa (1962–2051 psia, injector 4), O/F 1.77–2.9. All
LOX/RP-1 (ambient-temperature kerosene).

**Absolute measured throat heat flux, UMR case** `[TP2862-LOXRP1 Fig.8, p.10]`: at nominal Pc
= 4.3 MPa abs (627 psia), measured throat Q/A rises from ~4 to ~11×10³ Btu/(in²·s) (roughly
6.5–18 MW/m²) over O/F = 2.4–3.0 — this is the primary usable *magnitude* anchor point, a
real measured LOX/RP-1 throat heat flux at a Pc directly relevant to `engine_designer`'s
target range. At the higher-Pc test (8.87 MPa abs = 1287 psia, O/F=3.32) the measured value
was scaled to a *projected* 6.4 kW/cm² (39.6 Btu/in²·sec) at 8.87 MPa via a `Q/A ∝ Pc^0.8`
scaling relation taken from ref. 7 (Cook, NASA CR-159790) — flag this 6.4 kW/cm² figure as
a *derived/scaled* number, not a raw calorimeter reading, though the scaling exponent itself
(0.8) is independently corroborated by the paper's own Pc-sweep data (next point).

**Empirical Pc-scaling exponent, directly measured (not assumed)** `[TP2862-LOXRP1 p.11,
Fig.9]`: comparing curves at different Pc within this dataset, the authors find **Q/A ∝
Pc^(0.8–1.0)** in the combustion (cylindrical) section of the chamber, and **Q/A ∝
Pc^(0.7–0.8)** in the throat/divergent section — i.e. the *measured* throat-region exponent
(0.7–0.8) sits at or slightly below the classical Bartz Pc^0.8 prediction, while the
upstream combustion-section exponent runs as high as 1.0. This is a genuinely useful,
directly-measured data point for validating/refining any Pc-scaling assumption in
`cooling.py`'s heat-flux model, distinct from and independent of the ref.-7 scaling relation
used elsewhere in the paper for cross-comparison.

**Bartz/design-prediction comparison — the single most citable finding**
`[TP2862-LOXRP1 p.11, "Concluding Remarks" & Summary of Results item 2, p.15]`: at Pc = 13.65
MPa abs (1980 psia), **the measured throat heat flux was approximately 60% higher than the
"design prediction"** (from reference 9, Labotz/Rousar/Vaeler NASA CR-165177) — reproduced
independently at two different Pc/O·F combinations (scaled 4.32→13.65 MPa data vs. raw
13.65 MPa data), both landing at the same ~60% figure. The paper does not use the word
"Bartz" explicitly in the text extracted here, and "reference 9's design prediction" is not
itself stated to be a pure unmodified Bartz correlation — but this is exactly the kind of
independent real-engine under-prediction magnitude (design tool under-predicting real
measured throat Q/A by ~60%) that corroborates `cooling.py`'s rationale for needing a
calibration factor (`BARTZ_ABS_FLUX_CALIBRATION`) rather than trusting a flat/uncalibrated
Bartz coefficient — same qualitative direction as the `[EUCASS-2023]` CFD finding already in
`06-cooling-and-heat-transfer.md` (uncalibrated Bartz under-predicting wall temp by ~100 K),
now from real calorimeter hardware instead of CFD. **Caveat**: this is a comparison against
another paper's *design prediction*, not a first-principles Bartz recomputation done by
these authors — the exact correlation/coefficients behind ref. 9's "design prediction" are
not given in the extracted text, so this 60% figure should be cited as "measured throat Q/A
exceeded a contemporary 1980s LOX/hydrocarbon design-tool prediction by ~60%," not as "Bartz
under-predicts LOX/RP-1 by 60%" without that caveat.

**Carbon deposition (coking) knocks down the gas-side heat transfer coefficient** — a
distinct, well-quantified, and directly relevant finding for `cooling.py`'s LOX/RP-1
material-limit discussion (`[TP2862-LOXRP1 Fig.10 p.12, Fig.12 p.13, Summary items 3-4
p.15]`):
- UMR injector, Pc = 4.32 MPa abs (627 psia): soot-coated throat h_g is **~40% lower** than
  the soot-free (clean-wall) calculated h_g, across O/F = 2.0–3.2.
- Zoned/fuel-rich-outer-zone injector, Pc = 13.8 MPa abs (2000 psia): soot-coated throat h_g
  is **~60% lower** than soot-free, an even larger knockdown at the higher pressure/fuel-film
  condition.
- Soot forms as a real physical carbon layer on the calorimeter wall whose thickness the
  paper describes as varying with axial location; deposit thermal resistance R_d is modeled
  with an empirical fit (their eq. 10, from ref. 7/Cook CR-159790): R_d = e^(1.17 − 0.726·G)
  [cm²·s·K/kcal] where G is propellant mass velocity (or R_d = e^(0.90 − 0.051·G) in
  in²·s·°R/Btu units) — a usable closed-form deposit-resistance correlation if `cooling.py`
  ever wants to model coking-layer thermal resistance explicitly, though it is a 1970s-era
  empirical fit from a single referenced source (ref. 7), not independently re-derived here.
- Framing: the authors explicitly conclude (Concluding Remarks, p.15) that **both zoned
  combustion and carbon-deposit buildup act as beneficial passive thermal barriers** for
  long-term hydrocarbon-engine operation — carbon deposition is presented as a wall-temperature
  *reducer*, not purely a fouling problem, a nuance worth flagging if `cooling.py`'s
  LOX/RP-1 coking discussion currently treats coking as a pure liability (reduced coolant-
  side heat pickup / regen degradation) without this compensating hot-gas-side benefit.

**Zoned (fuel-rich outer-zone) combustion vs. uniform mixture ratio (UMR)** — a real
measured film-cooling-like effect via injector design, not additive film cooling
`[TP2862-LOXRP1 Summary p.1 & p.14-15]`:
- Sealing the outer ring of oxidizer orifices on a 61-element O-F-O injector (fig. 5b) made
  the near-wall combustion gas fuel-rich; the outer zone carried 26–30% of total fuel flow
  but only 13–17% of total oxidizer flow.
- Result: **throat heat flux reduced by 47%**, at the cost of only a **4.5% reduction in
  C* efficiency** (η_c*): unmodified/UMR injector C*_eff ≈ 99.5% (at Pc=4.1 MPa, injectors 1-2)
  vs. modified/zoned injector C*_eff ≈ 95–96.2% (injectors 3-4, across the O/F range tested;
  96.3% specifically quoted at 13.8 MPa abs).
  → this 99.5% UMR-injector C* efficiency is itself a directly citable real LOX/RP-1 c*
  efficiency data point for `03-combustion-and-cstar.md`, from a well-instrumented NASA test
  program with a good (triplet O-F-O) injector — useful as an upper-bound/high-quality-
  injector anchor distinct from whatever numbers are already tabulated there.
- Total integrated heat load over the whole calorimeter for zoned combustion was **53% of**
  the total UMR heat load at matched Pc/O-F (comparing plot II [zoned, Pc=8.11 MPa,
  O/F=2.93] against plot I [UMR, Pc=8.87 MPa, O/F=3.32] after Pc/O-F normalization via a
  `(Pc)^0.8·(O/F_ref/O/F)^n` correction) — i.e. roughly a **halving of total chamber heat
  load** from injector zoning alone, corroborating the throat-specific 47% figure at the
  whole-chamber-integral level.
- Heat-flux-ratio (zoned/UMR) at the throat was essentially flat with O/F and largely
  independent of Pc across 4.14/8.3/13.8 MPa abs (fig. 15) — a mixture-ratio- and
  pressure-insensitive ~0.5x knockdown factor for this specific zoning geometry.

**Axial heat-flux distribution shape** `[TP2862-LOXRP1 Fig.9 p.11, Fig.11 p.11-12, Fig.13
p.13-14]`: heat flux rises from the injector face, peaks sharply at the throat, and falls off
through the divergent section; the paper explicitly notes that "the variations upstream of
the throat indicate that the injector characteristics affect the heat flux until combustion
is complete" — i.e. the combustion-zone (cylindrical-section) flux profile is injector-
dependent, not purely geometric, while post-throat divergent-section decay rate differs
between the two chamber geometries tested (different divergent contours). No tabulated
numeric axial-profile data was extractable from this OCR pass (figures 8/9/11/13 are
plots, not tables, and plot-axis/curve labels are OCR-garbled) — only the qualitative shape
and the specific numeric callouts above are reliably extractable from this text layer.

## Design method

Not a design-method paper — a measurement/calorimetry report. It does give one usable
closed-form empirical relation (deposit thermal resistance R_d vs. mass velocity G, eq. 10,
sourced from ref. 7/Cook CR-159790, not independently derived here) and the Pc-scaling
exponents noted above, but no chamber-sizing or cooling-jacket design procedure.

## Section map

Summary (p.1) — Introduction (p.1-2, motivation: high-Pc LOX/hydrocarbon engine studies for
1970s-80s mixed-mode SSTO/HLLV concepts) — Symbols (p.2) — Apparatus: Chamber / Injector and
Resonator / Test Facility (p.3-6, incl. injector geometry Tables I-II) — Test Procedure
(p.6-7, Table III test conditions) — Short Calorimeter with Uniform Mixture Ratio (p.7-8,
Fig.8-9, the Bartz/design-prediction ~60%-high comparison) — Carbon Deposits with Uniform
Mixture Ratio (p.9-10, Fig.10, the 40% h_g knockdown, eq. 3-10 heat-transfer/resistance
formulation) — Long Calorimeter with Nonuniform Mixture Ratio (p.10-11, zoned-combustion
setup and Fig.11 axial profiles) — Carbon Deposits with Nonuniform Mixture Ratio (p.11-12,
Fig.12, the 60% h_g knockdown for zoned injector) — Comparison of Zoned and Uniform Mixture
Ratio Combustion (p.12-13, Fig.13-14, the 47% throat-flux reduction / 4.5% C* cost /
99.5%→95-96% C*_eff numbers) — Heat Flux Ratio of Zoned to Uniform Combustion (p.13-14,
Fig.15) — Concluding Remarks (p.14) — Summary of Results (p.14-15, 4 numbered findings) —
References (p.15, 11 refs, notably ref.7=Cook CR-159790 "Advanced Cooling Techniques for
High Pressure Hydrocarbon-Fueled Engines" and ref.9=Labotz/Rousar/Vaeler CR-165177 "High-
Density Fuel Combustion and Cooling Investigation," the source of both the R_d correlation
and the "design prediction" the ~60%-high comparison is measured against) — Report
Documentation Page (p.18).

## Caveats

- **OCR/text-layer quality is uneven**: body prose extracts cleanly, but every figure's
  axis labels, legend tables, and in-figure numeric callouts are badly mangled by the PDF's
  text layer (e.g. "C*" renders as "C_ff," digits are transposed/merged, table columns
  interleave). All numeric figures cited above were cross-checked against the surrounding
  prose (which restates key figure values as sentences) rather than read directly off a
  garbled figure/table block — treat any number NOT independently confirmed in body prose
  (i.e., axial-profile curve values, Table III's per-run O/F list) as unreliable from this
  extraction pass; a `get_pixmap()`-based visual re-read of Figures 8, 9, 11, and 13 would
  be needed to pull precise axial heat-flux numbers if that level of detail is ever wanted.
- **The "~60% higher than design prediction" finding is a comparison against another 1980
  paper's design tool** (ref. 9, Labotz/Rousar/Vaeler CR-165177), not a from-scratch Bartz
  recomputation by these authors — the exact correlation/constants behind that "design
  prediction" are not given in the extracted text. Useful as corroborating real-hardware
  evidence that period design tools under-predicted LOX/hydrocarbon throat heat flux, but
  should not be quoted as "Bartz is 60% low for LOX/RP-1" without noting this indirection.
- **Small-scale, short-duration calorimeter hardware**: 6.59 cm throat diameter (small even
  by upper-stage standards), water-cooled instrumented calorimeter rather than a flight-like
  regen jacket, tests run as steady-state hot-fire points rather than long-duration burns —
  the carbon-deposit-thickness/coking numbers are for this specific small chamber's test
  durations and may not directly scale to full-size RP-1 engine jacket coking rates.
- **Zoned-combustion injector is a specific one-off geometry** (61-element triplet with the
  outer oxidizer ring sealed) sized for these particular small chambers; the paper itself
  notes that for *large* thrust chambers the core mixture ratio would not need to shift as
  much as it did here to compensate for the fuel-rich outer zone (13-17% oxidizer / 26-30%
  fuel diverted to the outer zone in this small-chamber test) — the 47%-flux/4.5%-C*eff
  tradeoff numbers are specific to this injector's zone split, not a universal LOX/RP-1
  zoning result.
- **No explicit tabulated coolant-side (regen jacket) design data** — this paper measures
  hot-gas-side heat flux via a water-cooled calorimeter's coolant temperature rise; it does
  not report or validate coolant-side film coefficients, jacket ΔP, or channel geometry
  design rules beyond the generic Dittus-Boelter-type coolant h_c formula (eq. 6, cited to
  ref. 10, Swenson/Kakarala/Carver 1965) used only as an intermediate step to back out the
  hot-gas-side wall temperature.
