# NASA-CR-193339 — Shear Coaxial Injector Atomization Phenomena

## Identity

S. Pal, M.D. Moser, H.M. Ryan, M.J. Foust, R.J. Santoro (Penn State Propulsion Engineering
Research Center), *Shear Coaxial Injector Atomization Phenomena for Combusting and
Non-Combusting Conditions*, NASA-CR-193339, c. 1993 (Penn State/NASA MSFC Contract
NAS 8-38862). `literature/NASA CR-193339 - Shear Coaxial Injector Atomization Phenomena.pdf` (NTRS 19940007054; 39 PDF leaves, printed page = leaf + 1 for the
body text, i.e. leaf 0 is the title page, leaf 1 is printed p.ii Abstract). Tag: `[PSU-CoaxAtom]`.

## Character

A short, focused experimental paper (not a design monograph) reporting real LOX drop-size/
velocity measurements downstream of a single (uni-element) shear-coaxial injector, for both
actual LOX/GH2 hot-fire combustion and a water/GN2 cold-flow simulant, using Phase Doppler
Particle Analyzer (PDPA) laser diagnostics. Directly relevant to `claude_lit/topics/
05-injectors.md`'s coaxial-injector coverage — this is real quantitative atomization data,
not a design-rule source. No manifold, regenerative-cooling, or sandwich-wall content.

Structure: Abstract, Introduction, Experimental (rig description, hot-fire + cold-flow
setups, PDPA technique), Results and Discussion (Hot-Fire Studies, Cold Flow Measurements,
Hot-Fire/Cold-Flow Comparison), Summary, Nomenclature, References. Read in full — the paper
is short enough that no extraction-scope tradeoff was needed.

## Key results

**Injector geometry** `[PSU-CoaxAtom, Experimental, leaf 5]`: single shear-coaxial element,
LOX post inner diameter **3.43 mm**, LOX post **recessed 3.78 mm** below the fuel annulus
exit; fuel (GH2) annulus inner diameter 4.19 mm, outer diameter 7.11 mm. The paper notes
these dimensions are **comparable to the SSME preburner fuel/oxidizer element geometry** —
i.e. this is genuinely representative small-scale hardware, not an arbitrary lab rig.
Chamber throat diameter 11.36 mm (interchangeable to vary Pc).

**Real test conditions** `[PSU-CoaxAtom, Results, leaf 14]`: hot-fire chamber pressure
**2.67 MPa**; cold-flow "ambient" reference **0.1 MPa** (a 26.3× Pc ratio between the two
test conditions, called out explicitly as *not* the primary driver of the atomization
difference — Pc mainly sets gas density, not the shear mechanism itself).

**LOX core intact length — a real breakup-length data point** `[PSU-CoaxAtom, Results, leaf
6]`: laser-sheet flow visualization showed the LOX jet core appeared visually intact for
about **50 mm from the injector face** (≈ 14.6 × the 3.43 mm post ID); a drop field
(post-breakup spray) was evident only downstream of that. This is a concrete
L_intact/d_post ≈ 14.6 anchor for shear-coaxial LOX-core breakup length, useful context if
`engine_designer` ever wants an intact-core-length check for coaxial injectors (none exists
today).

**Drop size distribution** `[PSU-CoaxAtom, Results, leaf 10-11]`: PDPA measurement range
4-164 µm; probability-density-function peak (mode) at **20-30 µm** for the hot-fire case,
mono-modal and positively skewed. Sauter mean diameter (D32) and arithmetic mean diameter
(D10) both **decrease with radial distance** from the centerline for the steady-state
chamber-pressure period (largest drops near the spray axis, smallest toward the edge).

**Cold-flow trends** `[PSU-CoaxAtom, Results, leaf 12]`: for three water/GN2 flow
conditions (liquid velocities 2.9/14.3/28.3 m/s at a fixed gas annulus velocity of 293 m/s),
D32 is maximum at the centerline, decreases with radial distance to a minimum, then
increases slightly near the spray edge; **D32 near the spray center increases with liquid
flow rate** (i.e. with decreasing gas-to-liquid momentum ratio) — poorer atomization at
lower momentum ratio, consistent with atomization theory. Near the spray edge, D32 for all
three flow rates converges to nearly the same value.

**The headline finding — hot-fire sprays produce LARGER drops than a matched cold-flow
simulant** `[PSU-CoaxAtom, Results/Discussion, leaf 14-15]`: comparing the hot-fire case to
a cold-flow case with matched mass flowrates/velocities for both propellants (only Reynolds
and Weber numbers differed by more than an order of magnitude, due to LOX vs. water having
very different viscosity/surface tension), the **measured hot-fire drop size was larger**
than the cold-flow case — despite the hot-fire case's much higher Re/We, which by classical
atomization scaling should produce *smaller* drops, not larger. The paper calls this
explicitly **"counterintuitive"** and concludes the combusting gas-phase velocity field must
be substantially different from the cold-flow gas-phase field, altering the shear
atomization mechanism itself — i.e. **cold-flow injector characterization cannot be
naively rescaled to predict real combusting spray behavior for this injector type**, a
caution directly relevant to any cold-flow-based sizing rule.

## Design method

Not a design/sizing-equation source — an experimental characterization paper. No orifice
Cd, breakup-length correlation, or drop-size prediction formula is derived; the value is
the real measured numbers above (breakup length, drop-size range/mode, and the hot-fire-
vs-cold-flow discrepancy finding) as real-hardware corroboration or caution for any
existing coaxial-injector atomization treatment.

## Section map

- Abstract/Introduction: leaf 1-4 — read.
- Experimental (rig, hot-fire + cold-flow setup, PDPA technique): leaf 4-9 — read.
- Results and Discussion (Hot-Fire Studies, Cold Flow Measurements, Hot-Fire/Cold-Flow
  Comparison): leaf 10-16 — read in full, see Key results above.
- Summary/Acknowledgement: leaf 16 — read.
- Nomenclature: leaf 17 — read.
- References: leaf 18-20 — skimmed (citation list only).
- Figures/Tables (referenced throughout, e.g. Figs. 4-11, Tables 1-5): leaf 21-38 — not
  separately read; all numeric findings above came from body-text narrative, not
  reconstructed from plotted figures.

## Caveats

- **Uni-element, sub-scale rig** — a single injector element in a small optically-accessible
  chamber, not a full injector face; drop-size/breakup findings are for this one element's
  specific geometry (3.43 mm LOX post) and should not be treated as universal shear-coaxial
  constants without checking scale sensitivity.
- **c. 1993 CFD/diagnostic-era paper** — cites contemporaneous coaxial-injector cold-flow
  literature (Zaller, Eroglu & Chigier, Hardalupas et al.) as corroboration for the cold-flow
  radial-profile trends; no claim of currency beyond the specific LOX/GH2 measurements.
  OCR quality is clean (born-digital-quality scan; NASA-CR series), no reconstruction caveats
  needed for the quoted numbers.
- No manifold, regenerative-cooling, or "sandwich"/dual-wall chamber-construction content —
  flagged here only for completeness since this source was pulled in the same literature
  batch as sources specifically covering those topics.
