# [SECA-HT] — Heat Transfer in Rocket Engine Combustion Chambers and Regeneratively Cooled Nozzles

## Identity

- **Title**: *Heat Transfer in Rocket Engine Combustion Chambers and Regeneratively Cooled
  Nozzles*
- **Report**: **SECA-FR-93-18**, Final Report, 16 November 1993. Contract NAS8-38961 for
  NASA Marshall Space Flight Center (COR: Gil Wilhold; interests of Kevin Tucker and
  Dr. Ten-See Wang also acknowledged). Subcontract portion performed by Mississippi State
  University (Appendix B).
- **Authors**: not clearly identifiable from the OCR'd front matter/title page. The report's
  own reference list cites a Phase I predecessor, *"Heat Transfer in Rocket Engine
  Combustion Chambers and Regeneratively Cooled Nozzles," SECA-P-90-09* (1990), by
  **Chen, Y.S., J.A. Freeman, and R.C. Farmer** (SECA, Inc.) — plausibly the same team
  authored this Phase II follow-on, but that is inferred, not confirmed.
- **Extent**: 163 PDF leaves. Very figure-heavy (contour plots, line plots, schematics);
  OCR of plotted/contour-map content is largely garbled (rotated/mirrored text, scientific
  notation broken across lines) and was **not** trusted for this note. Paragraph prose
  (introduction, section narrative, conclusions, references) extracts cleanly and was the
  basis for everything below.
- **PDF leaf ↔ printed page**: printed page ≈ PDF leaf for the front half (leaf 5 ↔
  printed p.1); by the back matter this drifts by ~1 page (leaf 93 carries footer "94") —
  likely an uncounted figure-only leaf somewhere in Section 4 or 5. Treat page cites below
  as approximate.

## Character

**This is a CFD-methodology report, not a closed-form-correlation reference** — a
meaningfully different kind of source than `[TN-Dump]` or `[Huzel]`'s Bartz/Dittus-Boelter
treatment. It documents development of a **conjugate (fluid + solid) heat-transfer CFD
model**, built on the **FDNS** Navier–Stokes solver with a purpose-built variable-density
single-phase spray/injector submodel, for predicting wall heat transfer in the **SSME**
main combustion chamber and regeneratively-cooled nozzle — then validates that CFD tool
piecemeal against several real and subscale test datasets. It is explicitly a Phase II
report; Phase I (SECA-P-90-09, 1990) built the base SSME conjugate heat-transfer model.

I checked explicitly for the standard correlation vocabulary — **zero hits** anywhere in
the extractable text for "Bartz," "Dittus," "Reynolds number," "Prandtl," "Stanton," or
"recovery factor" (outside citations to other, unavailable works). This source's value is
in its **qualitative findings and cross-validation cases**, not in a reusable formula.

## Validation cases covered (no single "test article" — four independent datasets)

| Case (section) | What it is |
|---|---|
| SSME main + baffle injector elements (§3.2–3.3) | Unit injector-element flow/heat-transfer model; 525 main + 75 baffle elements in the real SSME MCC |
| P&W Subscale STME experiments (§4.1) | Subscale staged-combustion-cycle engine heat-transfer data |
| Rocketdyne Thrust Chamber Technology Program (§4.2) | 3.4-in-dia subscale **LOX/RP-1** motors, Air Force program, like-impinging circumferential-fan injectors |
| Film-cooling verification studies (§4.3) | Holden case, GASL case; air/H2 film cooling with finite-rate chemistry |
| PSU single coaxial injector experiments (§4.4) | GOX/GH2, Penn State University |

## Key results

- **Near-injector heat-flux reduction — three competing explanations, CFD-side.** Three
  prior heat-transfer predictions along the SSME chamber wall (Refs. 23–25, Figs. 29–31,
  ~p.58) all show reduced heat transfer near the injector face, but disagree on the cause:
  method 1 attributes it to film cooling, method 2 to combustion kinetics, method 3 to
  finite-rate vaporization. **This independently corroborates, from the CFD side, the same
  phenomenon `[TN-Dump]` found empirically** (its "first ~3 in from injector" over-cooled
  zone — direct test evidence that combustion takes a finite length to complete). Worth
  citing alongside `[TN-Dump]`'s finding rather than as a standalone claim.
- **Injector-geometry sensitivity, hydrocarbon-specific.** The Rocketdyne LOX/RP-1 subscale
  thrust-chamber tests found that **small changes to a like-impinging circumferential-fan
  injector configuration caused large changes in chamber-wall and nozzle heating** (§4.2,
  ~p.67). A real-hardware caution that hydrocarbon injector geometry is unusually sensitive
  for wall heat flux, not just for combustion efficiency.
- **RP-1 film-cooling mixing caution.** A film-cooled RP-1/O₂ case (RP-1 film modeled as
  inert C₂H₂) predicted the film was cold enough to give correct wall heating right at
  injection, but "mixes too fast" further downstream (~p.70) — i.e. the CFD model itself
  flags film-cooling *decay length* as harder to predict than the near-injection
  effectiveness. Relevant context (not a number to port) for `cooling.py`'s
  `film_effectiveness_profile` length-decay assumption.
- Reports its own injector mass-split for the Rocketdyne test motor's non-uniform-O/F case
  as three flow streams: 4.45 / 13.35 / 26.7 lb/sec (Fig. 35 caption, ~p.68) — a real
  subscale-motor injector flow split; minor standalone value.
- A reduced 8-reaction finite-rate H₂/O₂ combustion-kinetics mechanism with Arrhenius rate
  constants is tabulated (Table 2, ~p.88) — outside `engine_designer`'s scope (no detailed
  chemical-kinetics model exists or is planned), noted only for completeness.
- **Self-reported validation gaps**: the report repeatedly flags its own comparisons as
  qualitative rather than quantitatively verified — e.g. "the experiment did not provide
  enough detailed data to verify all of the assumptions required in this analysis" (~p.73)
  — and its conclusions (§6, ~p.92–94) recommend further validation against carefully
  selected, well-instrumented test cases, noting the PSU single-coaxial GOX/LOX dataset was
  still pending at time of writing.

## Design method — what to reuse

Little to directly port as a formula (see Character, above). Treat this source as
**converging qualitative evidence**, not a numeric-correlation source:
1. It backs the same near-injector under-heating phenomenon `[TN-Dump]` documented
   empirically — two independent sources (one test, one CFD) agreeing strengthens
   confidence in `cooling.py`'s existing length-decaying film-effectiveness treatment,
   even though neither source hands over a constant to plug in.
2. It's a documented real-world caution that **hydrocarbon injector-geometry changes drive
   outsized wall-heating changes** — more directly relevant to `injectors.py`/
   `combustion_stability.py` design-choice warnings than to a `cooling.py` constant.

## Section map

| Section | Approx. PDF leaf | Content |
|---|---|---|
| 1.0 Introduction | 5 | Phase I → Phase II background, objectives |
| 2.0 Technical Approach | 12–15 | FDNS conjugate-CFD approach; §2.2 spray-model rationale (supercritical O₂/H₂/steam globules, not classical droplet spray) |
| 3.0 Unit Injector & Combustion Chamber Analyses | 16–61 | §3.2 Main injector element (16), §3.3 Baffle injector element (~43), §3.4 Main combustion chamber streamtube (~50s) |
| 4.0 Overall Engine Heat Transfer | 62–91 | §4.1 P&W Subscale STME (62), §4.2 Rocketdyne Thrust Chamber Technology / LOX-RP-1 (67), §4.3 Film cooling verification (74), §4.4 PSU coaxial injector (79) |
| 5.0 Adaptive Grid Generation | 92 | EAGLE-code adaptive gridding, Mississippi State subcontract |
| 6.0 Conclusions and Recommendations | ~92–94 | Self-assessed validation gaps, recommended next test cases |
| 7.0 References | 94–97 | Incl. Phase I report SECA-P-90-09, FDNS code user's guide, NBS thermophysical-property notes |
| Appendix A | 98+ | Grid-generation code (POST) listing |
| Appendix B | — | Mississippi State University subcontract final report (adaptive gridding) |

## Caveats

- Figure/plot OCR is unreliable to unusable throughout — every quantitative claim above
  came from surrounding prose or a figure *caption*, never from reading plotted data or a
  contour map directly. No numeric table of h_g, Nu, or wall-temperature values could be
  reliably transcribed.
- This is a CFD-tool development-and-partial-validation report; its own conclusions
  describe several comparisons as qualitative rather than quantitatively verified — don't
  treat "predicted well" statements in this source as equivalent to a validated correlation.
- Authorship is inferred from the report's own citation of its Phase I predecessor, not
  confirmed from this document's front matter.
- Contains **no** propellant-class-specific gas-side heat-transfer coefficient of the kind
  `cooling.py`'s `BARTZ_ABS_FLUX_CALIBRATION` needs — this source cannot be used to derive
  or spot-check that constant.

## Regen passage geometry & coolant-side data (2026-09-23 re-read)

Targeted full-text re-read (pymupdf, all 163 leaves; every figure leaf touching wall heat
flux or the MCC/nozzle rendered and read visually). Cites: **printed** page, with PDF leaf
in parentheses. Leaf↔printed offset is 5 up to leaf 65 (printed 60) and 1 from leaf 66
(printed 65) onward — **printed pp. 61–64 are missing from this scan**, i.e. the §4.1
P&W subscale-STME prose and Figs. 31–33 (the TOC puts §4.1 at p.62). Whatever chamber /
coolant description §4.1 contained is not recoverable from this PDF.

**Bottom line: the report gives NO regen coolant-passage data for any engine.** No channel
count, width, depth, land width, liner thickness, aspect ratio, coolant flow split,
coolant-side h_c correlation, coolant Re/velocity, roughness, or regen-wall temperature
appears in prose, tables, or legible figure text. The words "Reynolds", "Prandtl",
"Dittus", "Bartz", "roughness", "land", "rib" do not occur; "channel" occurs only as
"fully developed channel flows" for PSU injector inlet turbulence (p.79 (80)). The Phase I
SSME conjugate regen model (SECA-P-90-09, Ref. 1) is where such inputs would live; it is
cited, not reproduced (p.1 (6)).

What IS stated (all SSME data is **injector-side**, not the MCC regen jacket):

| Item | Value (original) | SI | Cite |
|---|---|---|---|
| SSME MCC construction (labels only, no dimensions) | "slotted liner", "jacket", "throat ring", coolant inlet (aft) / coolant outlet (fwd), acoustic cavities | — | Fig. 2, p.3 (8) |
| SSME nozzle construction (labels only) | coolant inlet manifold, coolant outlet manifold, hatbands, jacket transfer ducts, drain lines; "a large number of regenerative cooling tubes in the nozzle" | — | Fig. 3, p.4 (9); p.8 (13) |
| SSME injector "coolant hydrogen" (H₂ cavity between injector plates; Fig. 1 labels a "coolant circuit" into the "hydrogen cavity") | 465 R, 3580 psia, ρ = 1.2298 lbm/ft³ | 258 K, 24.68 MPa, 19.70 kg/m³ | p.37 (42) |
| same, through 75 baffle-element sleeves | 19.3 lbm/s; 17.558 ft/s inflow | 8.75 kg/s; 5.35 m/s | p.37 (42) |
| baffle coolant H₂ temperature range | 465 → 450 R | 258 → 250 K | p.43 (48) |
| porous primary-plate transpiration H₂, whole MCC | 5.29 lbm/s at 465 R, 3584 psia; inlet 11.9 ft/s; exits MCC side at assumed fixed 666 R; typ. exit velocity 18.5 ft/s | 2.40 kg/s; 258 K; 24.71 MPa; 3.63 m/s; 370 K; 5.64 m/s | p.47–48 (52–53) |
| fuel-rich hot-gas (turbine exhaust) to 525 main elements | 241.3 lbm/s, O/F 0.8012, 1500 R, 3527 psia, ρ 0.7292 lbm/ft³; 0.45962 lbm/s/element, 954.77 ft/s, M 0.1776 | 109.5 kg/s; 833 K; 24.32 MPa; 11.68 kg/m³; 0.2085 kg/s; 291.0 m/s | p.28 (33) |
| main LOX | 877.62 lbm/s ÷ 600 elements, 200 R, 3450 psia, 68.0665 lbm/ft³, 111.50 ft/s | 398.1 kg/s; 111 K; 23.79 MPa; 1090 kg/m³; 33.99 m/s | p.28 (33) |
| element-wall BC model | q = U(T_a − T_i), U = 1/(t_w/k_w + 1/h); h from White (Ref. 18) tube-bank-in-crossflow Nu, averaged staggered/in-line; T_a = 1600 R hot gas or 465 R H₂ | 889 K / 258 K | p.24 (29) |
| computed element skin temps | main: 975 R (LOX dome), 1250 R (exhaust manifold near secondary plate), 911 R (between plates); baffle: 866 / 941 / 465 R, **1500 R estimated** in chamber along baffle | 542 / 694 / 506 K; 481 / 523 / 258 K; 833 K | p.28 (33); p.37 (42) |
| Rocketdyne LOX/RP-1 motor | 3.4 in dia; baseline MR 2.73; test "designed to provide a constant wall temperature" (value not given) | 86.4 mm | p.67 (68) |

Wall heat flux, **digitized from plots (±~2 Btu/in²·s)**; 1 Btu/in²·s = 1.635 MW/m²:

| Case | Throat-region peak | Cylinder plateau | Cite |
|---|---|---|---|
| "Subscale NLS Engine" (prior prediction, Refs. 23–25; propellant not stated in legible text) | test ~51, CFD ~52 Btu/in²·s at x ≈ −1 in (≈ 83–85 MW/m²) | ~24–31 (39–51 MW/m²) | Fig. 29, p.59 (64) |
| Rocketdyne hydrocarbon motor, "Case 2" (prior prediction) | exp ~43, pred ~41 (≈ 67–70 MW/m²) | ~7–9 (11–15 MW/m²) | Fig. 30, p.60 (65) |
| Rocketdyne circumferential-fan injector, original config, MR 2.38–3.16, "corrected" flux | test ~60–68 at throat (≈ 98–111 MW/m²); FDNS(2.73) ~54 (≈ 88 MW/m²) | test ~33–40 (54–65 MW/m²) | Fig. 37, p.69 (70) |

Minor erratum to the note above: the 4.45 / 13.35 / 26.7 lb/s injector split is the Fig. 36
caption (p.68 (69)), not Fig. 35 (Fig. 35 is subscale-STME nozzle species, p.66 (67)).
