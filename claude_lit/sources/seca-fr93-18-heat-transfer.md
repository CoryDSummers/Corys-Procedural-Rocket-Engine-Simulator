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
