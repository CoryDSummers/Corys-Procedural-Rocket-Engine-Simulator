# Merkle, Li & Sankaran (Purdue) — Analysis of Regen Cooling in Rocket Combustors

## Identity

C. L. Merkle, D. Li, V. Sankaran (Purdue University, West Lafayette, IN), *Analysis of Regen
Cooling in Rocket Combustors*, conference paper, work performed under NASA Space Act
Agreement NCC8-200 (references cite 2003 AIAA papers, so this paper is ~2003-2004).
`literature/Merkle et al (Purdue) - Analysis of Regen Cooling in Rocket Combustors.pdf` (NTRS 20040075891; 8 PDF leaves, born-digital, clean text layer, no OCR issues).
Tag: `[Merkle-RegenCFD]`.

## Character

A short CFD-methodology paper, the same character as `[SECA-HT]` already in this reference
set: it demonstrates a coupled 3-D CFD capability (the authors' in-house "GEMS" solver) for
conjugate heat transfer between a regen coolant passage, a copper wall, and a hot-gas
boundary — it is **not** a correlation source and gives **no Bartz/Dittus-Boelter-type
formula, no design rule, and no manifold content of any kind** (checked specifically, per
the user's interest in manifolds — this paper only ever discusses a single straight coolant
passage segment, never manifold/distribution geometry). Read in full (only 8 pages).

The paper's own scope is narrower than its title suggests: this is a **preliminary,
short-passage, non-curved, non-film-cooled** demonstration case — the authors explicitly
call the results "preliminary" and describe follow-on work (adding curvature, film cooling,
and comparing compressible-hydrogen vs. incompressible-hydrocarbon coolant behavior) as
future work, not yet done in this paper.

## Key results

**Computational setup** (not a real-engine case — a generic/idealized geometry)
`[Merkle-RegenCFD p.2-3]`: 640 rectangular coolant passages spaced around a combustor
perimeter, water as a coolant surrogate for RP-1 ("the almost incompressible character of
the water should give a reasonably qualitative simulation" of hydrocarbon cooling — an
explicit modeling choice, not a claim that water and RP-1 behave identically), copper
combustor wall, hot gas modeled as a non-reacting perfect gas at 3000 K / 500 m/s (a boundary
condition, not a combustion simulation), coolant entering at 300 K / 10 m/s. Simulated
passage length very short (100 mm) — explicitly acknowledged as insufficient to reach
steady thermal conditions; the paper studies **entrance-region** behavior only.

**The one genuinely interesting physical finding** `[Merkle-RegenCFD p.4-5]`: wall
temperature at the hot-gas/copper interface **does not increase monotonically along the
flow direction** near the passage entrance — it rises sharply at the very inlet, then
*decreases slightly* over the next ~50 mm (an entry-length effect, attributed to the
copper's high thermal conductivity rapidly redistributing the initial thermal shock away
from the interface), before resuming a slow increase further downstream. This non-monotonic
entrance behavior is a real, physically-grounded CFD finding, but it is (a) specific to a
copper wall's high conductivity relative to the coolant's, and (b) only demonstrated for the
first 100 mm of a passage — the paper does not claim or show what happens over the full
length of a real cooling jacket. Not directly portable as a number, but useful qualitative
context: **local entrance-region wall temperature trends can be non-monotonic even under
steady heating**, a nuance `cooling.py`'s length-along-contour heat-flux treatment doesn't
need to model but should not be assumed to contradict if ever spot-checked against detailed
CFD.

**Strong tangential (circumferential) non-uniformity** `[Merkle-RegenCFD p.4-5, Fig 5]`: at
a fixed axial station, wall temperature varies significantly between the plane centered on a
coolant passage and the plane on the symmetry line *between* two adjacent passages (the
"land") — the land runs hotter, as expected, since it's the point of maximum hot-gas-to-wall
distance from any coolant channel. This is a real, if unsurprising, 3-D effect that
1-D/axisymmetric wall-heat-flux models (like `cooling.py`'s current contour-average
treatment) cannot capture by construction — flagged as a known simplification, not a new
finding to act on.

## Design method

None — no closed-form correlation, no new Bartz/Dittus-Boelter-type constant, no coolant-
channel sizing method. This paper exists to validate a CFD code's coupled-physics capability
qualitatively, not to produce a design rule.

## Section map

Entire 8-page paper read in full: Abstract, Introduction (p.1), Computational Model (p.2),
Results and Discussion (p.3-6), Summary and Conclusions (p.7), References (p.8).

## Caveats

- **Not a correlation or calibration source** — like `[SECA-HT]`, this cannot be used to
  derive or spot-check `cooling.py`'s `BARTZ_ABS_FLUX_CALIBRATION` or any other quantitative
  constant. Treat strictly as qualitative/corroborating context for the *shape* of near-
  entrance wall-temperature behavior, not a source of numbers.
- **Idealized, non-real-engine geometry**: 640 uniform straight passages, water-as-RP-1
  surrogate, non-reacting perfect-gas hot side, no film cooling, no curvature — none of the
  numbers in this paper (3000 K, 300 K, 10 m/s, 500 m/s, 100 mm) represent a real engine and
  should never be cited as if they were.
- **Explicitly preliminary/short-passage**: the authors themselves flag the 100 mm length as
  too short to reach representative downstream conditions — don't extrapolate the entrance-
  region non-monotonic-temperature finding to claim anything about full-length jacket
  behavior.
- **No manifold content whatsoever** — checked specifically per the user's interest in
  manifold literature; this paper only ever models one interior segment of one coolant
  passage.
