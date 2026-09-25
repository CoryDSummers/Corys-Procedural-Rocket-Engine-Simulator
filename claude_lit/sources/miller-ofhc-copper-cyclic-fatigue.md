# NASA CR-134841 — Cyclic Fatigue Analysis of Rocket Thrust Chambers, Vol. I: OFHC Copper Chamber Low Cycle Fatigue

## Identity

Roy W. Miller (Atkins & Merrill Inc., Ashland, Mass.), *Cyclic Fatigue Analysis of Rocket
Thrust Chambers: Volume I — OFHC Copper Chamber Low Cycle Fatigue*, NASA Contractor
Report **NASA CR-134841**, NASA Lewis Research Center, contract **NAS 3-17807**,
project manager H.G. Price, June 1974. `literature/NASA CR - Cyclic Fatigue Analysis of
Rocket Thrust Chambers Vol I - OFHC Copper.pdf` (NTRS 19740026129; 67 PDF pages: page 0
title page, page 1 contents, page 2 preface, page 3 summary, pages 4-66 body/appendices/
references). Tag: `[Miller-CuFatigue]`.

The title-page OCR that produced the current filename garbled the CR number (misread as
"CR-134806"-ish); the true, cleanly legible number from the title-page image is
**NASA CR-134841** — use that number when citing, though no rename was performed here
per the task instructions. Companion report: *Volume II* covers a high-cycle-fatigue
attitude-control thrust chamber (elastic/near-elastic regime) — not held in `literature/`,
not read for this note. The underlying finite-element tool this report demonstrates,
RETSCP ("Rocket Engine Thermal Strain with Cyclic Plasticity"), is documented in a
separate companion report, Miller's own NASA CR-134640 (June 1974, Ref. 1) — also not in
`literature/`.

## Character

A short (48 body pages + appendices), narrowly-scoped **case-study demonstration** of a
3-D finite-element elasto-plastic strain analysis method (the RETSCP program) applied to
ONE specific real hardware article: the throat section of a small regeneratively-cooled
LOX/LH2 combustion chamber that was fatigue-tested to failure at NASA Lewis. It is NOT a
general design-allowable/design-criteria document (unlike `[SP-8087]`/`[SP-8120]`) — it
gives one worked real analysis-vs-test comparison, a citable Coffin-Manson-family
low-cycle-fatigue (LCF) life-prediction equation (Manson's "Universal Slopes" method) and
real isothermal LCF test data for annealed OFHC copper at 538°C (1000°F), plus a real
measured strain range and a real observed cycles-to-failure for a real copper regen
chamber. Directly fills the "throat low-cycle thermal-fatigue estimate" gap `mass_model.py`
is described as carrying (per `CLAUDE.md`'s own Layout section) with an actual quantitative
example rather than a hand-picked constant.

Structure: Preface, Summary, Introduction, Combustion Chamber Configuration (Chamber
Geometry / Operating Conditions / Test Results), Strain Analysis (Finite Element Model /
Temperature Distribution / Material Properties / Structural Analysis / RETSCP Program
Execution / Results), Fatigue Life Analysis (Material Properties / Fatigue Damage /
Results), Concluding Remarks, Appendix A (symbols), Appendix B (sample RETSCP input,
raw punch-card-format numeric listing — not usefully OCR'able, not needed), Appendix C
(sample RETSCP output, same), References (19 citations). Read in full (narrative text);
Appendices B/C are raw finite-element input/output number dumps in a legacy card-image
format that OCR renders as unreadable noise — skimmed, not needed for any citable claim.
Two key figures (Fig. 1 chamber geometry, Fig. 17 the isothermal-fatigue log-log plot) were
rendered as page images and read directly since their content (dimensions; digitized
data-point positions) doesn't survive as PDF text.

## Key results

**Real hardware: a small LOX/LH2 regen thrust chamber, not a full flight engine**
`[Miller-CuFatigue, Combustion Chamber Configuration p.7; Operating Conditions p.9-10]`:
overall chamber length 15 in (38.1 cm), OFHC copper liner with **60 milled axial coolant
passages**, structural jacket is an **electroformed nickel closeout** (not a generic
"nickel alloy" — electroforming is the specific real fabrication method named). Throat
station geometry (Fig. 1 inset): throat bore 2.6 in dia (6.6 cm), copper-liner channel
land width 0.088 in (0.224 cm), channel width 0.115 in (0.292 cm), a 0.035 in (0.089 cm)
dimension at the hot-gas-side wall (liner thickness/rib region). Coolant flows nozzle-end
to injector-end (i.e., counterflow, coolant enters near the exit and exits near the
injector). Combustion gas at the throat: static pressure **347 psia (2.39 MPa)**,
adiabatic wall temperature **6143°R (3413 K)** — a hydrogen-oxygen chamber. Coolant (LH2):
inlet **50°R (28 K)** at **1066 psia (7.35 MPa)**; at the throat during steady firing,
**132°R (73 K)** and **1045 psia (7.21 MPa)**. Start transient: chamber pressure ramps to
**610 psia (4.21 MPa)** over **2.25 s** (a step transient forced by facility limits);
steady-state operating phase **2.0 s**; measured thrust during that phase **4686 lbf
(20,840 N)**; shutdown transient **1.75 s**; hydrogen bypass/precool flow maintained for
**2.1 s** between pulses, producing a uniform 50°R (28 K) precool state before each firing.
**This is a small (~5000-lbf-class) instrumented lab test article**, not a production
engine — treat the absolute thrust/geometry numbers as characterizing the test article
only, while the strain-range/fatigue-life relationship they produced is the generally
citable result.

**Real test program and observed failure** `[Miller-CuFatigue, Test Results p.11]`: the
chamber was fired in pulse trains of 1,1,1,1,5,4,3,11,1,2,3,5,3,2 pulses each, for a
**total of 43 cycles**. Visual inspection after the 43rd pulse found a **through-crack**
from the coolant passage into the combustion-chamber interior at the throat; the crack
"probably occurred on the **thirty-ninth cycle**" (correlated to a change in test-cell
acoustic noise pattern at that pulse). **Total accumulated steady-state run time was less
than 80 seconds** across all 43 cycles — i.e. this is a genuinely short-duration,
pulse-count-dominated (not creep/hold-time-dominated) fatigue problem. A real, physically
important companion observation: **coolant-channel bulging and hot-gas-side surface
roughening were observed after only a few cycles**, and measured copper temperatures
**increased progressively with each successive firing** as testing proceeded — i.e. the
chamber's own thermal state degraded cycle-over-cycle due to the accumulating plastic
deformation, a real coupled fatigue-thermal feedback the static single-cycle FEA below
does not itself capture (it instead re-tunes its thermal boundary conditions to match the
20th-cycle data specifically, treated as representative of "average" life — see below).

**The headline quantitative result — real measured/predicted strain range and life**
`[Miller-CuFatigue, Results p.39; Fatigue Life Analysis Results p.46]`: the 3-D FE model
(34-element throat cross-section, thermal loads from the 20th test cycle — chosen as
"approximately one half of the chamber life" and thus assumed representative of "average"
conditions) computed a **maximum effective total strain range of 2.46%**, occurring at the
hot-gas-side surface centered under a rib (i.e., under the land between coolant channels),
where the local maximum copper temperature at that specific element was **970°F (521°C)**.
**Strain range values were generally between 2.0% and 2.5% throughout the hot portion of
the copper liner** — i.e. 2.46% is the peak of a fairly flat high-strain plateau, not an
isolated spike. Using this 2.46% value against isothermal LCF test data for annealed OFHC
copper at 1000°F (538°C) (Ref. 10, plotted in the report's own Fig. 17), the **predicted
fatigue life was 80 cycles**. The **actual observed failure (through-crack) occurred at
cycle 39** — i.e. **the model over-predicted the real chamber's life by roughly a factor of
2** (unconservative direction). The report frames this itself as within the expected
scatter of fatigue test data ("the comparison... indicates the degree of scatter which is
associated with fatigue test results") rather than as a validated, tightly-bounded
prediction — this is a real, quantified example of LCF life-prediction uncertainty for a
regen copper chamber, useful as an order-of-magnitude/factor-of-~2 uncertainty anchor for
any similar prediction `engine_designer` might make, not as a precision-calibrated method.

**A subtlety directly relevant to any single-hot-station fatigue proxy**
`[Miller-CuFatigue, Results p.39-40, Fig. 15]`: **the location of peak strain range does
NOT coincide with the location of peak temperature.** The absolute peak computed copper
temperature anywhere in the model was **1493°R (829 K, ≈1033°F/556°C)**, at a *different*
element than the one carrying the peak 2.46% strain range (which itself sees only
970°F/521°C locally). The report attributes this to the pressure-load contribution: the
coolant-side-vs-chamber-side pressure differential loads the rib/wall locally like a
plate in bending, shifting incompressible plastic strain toward the rib base along the
hot wall independently of where the temperature itself peaks. **Practical implication**:
a chamber-fatigue proxy built only from the hottest-wall-temperature station (as a
`mass_model.py`-style single-station thermal-fatigue estimate would naturally do) can miss
the true worst LCF location, because pressure-load-driven strain redistribution and
peak wall temperature are not co-located — the true worst point requires a coupled
thermal+pressure elasto-plastic structural solve, which this report explicitly frames as
the reason a full FE analysis (rather than a temperature-only screening check) was needed
at all.

**Real hot tensile "hold strain" finding, but small for this article**
`[Miller-CuFatigue, Results p.40-41; Concluding Remarks p.47]`: as the copper's thermal
strain relaxes from the start-transient peak toward steady state, the relaxation can be
severe enough to produce a small amount of *additional* tensile plastic yielding under HOT
conditions (a "tensile hold strain" state) — described as "the first known computation of
tensile hold strains at hot engine test conditions" for this type of analysis. The report
explicitly states this hold-strain damage mode was judged small and NOT separately
analyzed here only because **total accumulated steady-state run time was under 80
seconds**; it states plainly that "for other configurations with longer test firings, hot
tensile hold periods could be quite damaging as predicted by the strain range partitioning
method [Ref. 14 = Manson]." This is a real, explicit caveat that this report's own
fatigue-life number (80 predicted / 39 actual cycles) applies to a SHORT-duration-per-cycle
engine and would need a hold-time-damage correction (strain-range partitioning, not
included here) for a longer-burn design — directly relevant since RP-1/RO-style engines
typically burn far longer per cycle than this ~2-second-per-pulse LH2/LOX lab article.

**The life-prediction equation used — Manson's Universal Slopes method**
`[Miller-CuFatigue, Fatigue Life Analysis p.42, eq. 2]`, given in full:

    Δε_t = (3.5·σ_u/E)·N̄_f^-0.12 + [ln(1/(1-RA))]^0.60 · N̄_f^-0.60          (2)

where Δε_t is total strain range, σ_u is ultimate tensile strength, E is modulus of
elasticity, RA is reduction-in-area — all from a **short-term tensile test at the
temperature of interest**, and N̄_f is cycles to failure. This is the classic Manson
"Universal Slopes" LCF relation (cited to Manson's own 1966 *Thermal Stress and Low-Cycle
Fatigue* textbook, Ref. 15) — a real, complete, directly-usable Coffin-Manson-family
equation, not merely referenced qualitatively. **Elevated-temperature correction**: for
LCF life prediction at elevated temperature, the report states the "average" life is
defined as **N̄_f/5** — i.e. equation (2) evaluated with the material's own
elevated-temperature short-term properties is divided by a flat factor of 5 to get a more
realistic elevated-temperature cyclic life estimate, a correction "based on comparison with
a great deal of experimental data" (Ref. 16 — Manson & Halford, NASA TM-X-52270, 1967), not
independently re-derived in this report. The 538°C (1000°F) OFHC-copper isothermal fatigue
data used to anchor the actual chamber life prediction is itself real independent test
data, cited to Conway, Stentz & Berling, *High Temperature, Low-Cycle Fatigue of
Copper-Base Alloys in Argon, Part I* — NASA CR-121259 (Jan. 1973, Ref. 10) — a real,
separately-published copper-alloy LCF-curve source that is a candidate future literature
target if a from-scratch fatigue curve (rather than this report's already-applied "one
strain range, one predicted life" example) is ever wanted for `engine_designer`.

**Digitized real data points from Fig. 17** (isothermal fatigue of annealed OFHC copper,
log-log Δε_t (%) vs. N_f) `[Miller-CuFatigue, Fig. 17 p.44]` — read directly from the page
image since the plot is not text-extractable; approximate, not precision-digitized:
the 538°C (1000°F) test-data curve (filled circles, Ref. 10) passes roughly through
(Δε_t≈2.0%, N_f≈110), (≈1.5%, ≈170), (≈1.1%, ≈250), (≈1.0%, ≈700), (≈0.85%, ≈1300),
(≈0.75%, ≈1900) — i.e. **at the report's own predicted-vs-actual strain range of ~2.0-2.5%,
real 538°C OFHC-copper isothermal LCF life is on the order of 100-250 cycles** in the raw
test data (before the report's own "average life ÷5" derating is applied to the
Universal-Slopes fit, which is what actually produced the 80-cycle prediction plotted as
the dashed curve). A separate room-temperature dataset (open circles, Ref. 12) sits roughly
an order of magnitude higher in strain range for the same cycle count — a real, large
citable temperature effect: **OFHC copper's LCF strain-range capability at 538°C is roughly
5-10x lower than at room temperature** for a given target cycle life, consistent with (and
quantifying) the qualitative "elevated temperature reduces LCF life" statement already
implicit in `topics/12`'s general Cu-alloy content.

**Cyclic hardening magnitude for annealed OFHC copper** `[Miller-CuFatigue, Material
Properties p.21, 23]`: comparing virgin (monotonic) vs. cyclic stress-strain curves for
annealed OFHC copper at 1000°F (538°C), the report states cyclic hardening raises stress
by **about 30%** at 3% strain relative to the virgin material's monotonic curve (strain
hardening occurs within the first few cycles and is accounted for in the analysis by using
already-cyclic — not virgin — stress-strain data, rather than modeling hardening
cycle-by-cycle).

**Full Table II material-property set used in the FE model** `[Miller-CuFatigue, Table II
p.28]` — real, quantitative, temperature-dependent input data for OFHC copper vs. the
(unspecified-alloy) nickel structural jacket, given in a bilinear yield-stress form
σ_y = σ_0 − λ_1·T:

| Property | Nickel | Copper |
|---|---|---|
| Thermal expansion coeff. | 7.2×10⁻⁶ in/in-°F (13.0×10⁻⁶ m/m-°C) | 9.8×10⁻⁶ in/in-°F (17.6×10⁻⁶ m/m-°C) |
| Modulus of elasticity | 30.0×10⁶ psi (20.7×10¹⁰ N/m²) | cold: 16.6×10⁶ psi (11.4×10¹⁰ N/m²); hot: 10.0×10⁶ psi (6.9×10¹⁰ N/m²) |
| Poisson's ratio | 0.31 | 0.33 |

Copper yield stress (σ_y = σ_0 − λ_1·T), bilinear "large-strain"/"small-strain" branches,
hot vs. cold regimes: large-strain-hot σ_0=9,200 psi (63.4 MPa), λ_1=4.63 psi/°F
(5.75×10⁴ Pa/°C); small-strain-hot σ_0=6,000 psi (41.4 MPa), λ_1=2.63 psi/°F
(3.26×10⁴ Pa/°C); large-strain-cold σ_0=17,700 psi (117 MPa), λ_1=0; small-strain-cold
σ_0=11,000 psi (75.8 MPa), λ_1=0. Nickel yield stress: σ_0=55,000 psi (379 MPa), λ_1=0
(temperature-independent over the range modeled). (Plastic-modulus-ratio bilinear-curve
coefficients are also tabulated but are RETSCP-program-internal curve-fit parameters, not
independently meaningful outside that program — not reproduced here.) Nickel jacket
thermocouples were surface-mounted on the outer wall; copper-liner thermocouples were
located **0.050 in (0.127 cm) from the hot-gas-side surface**, centered circumferentially
within the ribs.

## Design method

This is a **case-study application, not a generalizable design-allowable source**. It
gives: (1) a complete, real, directly-usable LCF life equation (Manson's Universal Slopes,
eq. 2 above) with a stated elevated-temperature "÷5 average life" correction factor,
applicable to any ductile metal given short-term tensile properties (σ_u, E, RA) at the
temperature of interest; (2) one real worked example of that method applied to a real
regeneratively-cooled OFHC copper LH2/LOX chamber, giving a real predicted-vs-actual
cycle-life comparison (80 predicted vs. 39 actual, ~2x unconservative) as a citable
uncertainty magnitude for this class of prediction; (3) a real total strain range value
(2.46% peak, 2.0-2.5% plateau) for a real annealed-OFHC-copper regen throat under
realistic pressure+thermal cycling, i.e. a real order-of-magnitude "how much strain does a
regen copper throat actually see per cycle" anchor if `engine_designer` ever wants to
estimate cycle life from a computed wall-temperature swing rather than leaving thermal
fatigue as a purely qualitative flag; (4) an explicit caveat that hold-time (long-burn)
damage is a SEPARATE, unaddressed damage mode for engines with longer per-cycle burn
durations than this ~2-second test article. It does NOT give: a general "safe" strain
range or cycle-life design target/allowable (this is one measured data point, not a
handbook curve); a closed-form ΔT-to-strain-range conversion (that requires the full 3-D
elasto-plastic FE solve this report demonstrates, not a formula); or any treatment of
modern chamber alloys (NARloy-Z, GRCop-84, Cu-Cr-Zr) — it is specifically about **annealed
OFHC copper** (pure, unalloyed copper), an older/softer material than the copper-silver-
zirconium or copper-chromium-niobium alloys `[Ch12-Materials]`/`[MatCh2]` document for
SSME-era and later chambers.

## Section map

- Preface / Summary: p.2-3 — read.
- Introduction: p.4-6 — read.
- Combustion Chamber Configuration — Chamber Geometry (Fig. 1, p.7-8, read as image for
  dimensions), Operating Conditions (p.9-10, incl. Fig. 2 operating-cycle plot, caption/
  narrative read, plot not independently digitized), Test Results (p.11) — read.
- Strain Analysis — Finite Element Model (Fig. 3, p.12-16), Temperature Distribution
  (Table I temperature-difference data + Fig. 5, p.17-21), Material Properties (Figs. 6-9
  stress-strain curves, p.21-27, narrative read; curves not independently digitized beyond
  the ~30% cyclic-hardening figure stated in text), Structural Analysis (p.28-30, incl.
  Table II read as page image p.28), RETSCP Program Execution (p.31-32) — all read.
- Results (Figs. 10-16, p.32-41) — read; Figs. 10-14 (stress-strain hysteresis loops,
  strain-range convergence) and Fig. 16 (hoop-stress distribution) skimmed as captions/
  narrative only, not independently digitized (no additional citable numbers beyond what's
  stated in the prose, which is captured above).
- Fatigue Life Analysis — Material Properties (p.42-44, incl. eq. 2 and Fig. 17 read as
  page images), Fatigue Damage (p.44-46), Results (p.46) — read in full, the core content
  of this note.
- Concluding Remarks: p.47-48 — read.
- Appendix A (symbols): p.49 — read.
- Appendix B (sample RETSCP input, raw card-image numeric listing): p.50-56 — skimmed;
  pure OCR noise (columns of punch-card-format numbers), no citable content beyond what
  the section's own prose intro states (already captured under RETSCP Program Execution).
- Appendix C (sample RETSCP output, same raw-listing format): p.57-63 — skimmed, same as
  above.
- References (19 citations): p.64-66 — read in full; several are real, independently
  citable candidate future sources (Ref. 10: Conway/Stentz/Berling NASA CR-121259, 1973,
  OFHC-copper-family LCF data at 538°C; Ref. 17: the same authors' NASA CR-121261, 1973, on
  zirconium-copper thermal-mechanical strain cycling with hold-time/notch effects; Ref. 19:
  Shoji, NASA CR-121213, 1973, "Advanced Hydrogen/Oxygen Thrust Chamber Design Analysis" —
  none acquired or read beyond their reference-list titles).

## Caveats

- **One real test article, one real result — not a statistical or handbook dataset.** The
  80-predicted/39-actual cycle comparison is a single case study; the report itself frames
  the ~2x gap as within normal fatigue-test scatter, not as a validated, bounded prediction
  method. Do not treat "predicted life ÷2" as a general correction factor for
  `engine_designer` — it is this one article's result.
- **Annealed OFHC (pure) copper only** — no NARloy-Z, GRCop-84, Cu-Cr-Zr, or any modern
  chamber-liner alloy is analyzed or referenced. Pure copper is softer and has different
  (generally lower) strength/higher ductility than these dispersion-/precipitation-
  strengthened alloys; the specific strain-range and cycle-count numbers above should NOT
  be applied directly to a modern-alloy chamber design without their own material data —
  only the *method* (Universal Slopes eq. 2 + the "÷5" elevated-temp correction) and the
  *qualitative* findings (peak-strain/peak-temperature non-collocation; hold-time as a
  separate long-burn damage mode; large room-temp-vs-538°C LCF strength gap) generalize.
- **Small, short-burn (~2 s per pulse, <80 s total accumulated run time) lab test
  article** — the report explicitly flags that hold-time (creep-like) damage, which
  becomes significant for LONGER individual burns, was judged negligible here only because
  of the short pulse duration and was NOT analyzed with the strain-range-partitioning
  method it cites as the correct tool for that case. Any RO/RP-1-style engine with
  multi-second-to-multi-minute burns per cycle would need that separate hold-time damage
  term this report doesn't provide.
- **No general design allowable given.** This report demonstrates an ANALYSIS METHOD
  against one real test case; it does not state a recommended design strain range, safety
  factor, or target cycle-life for chamber design purposes (unlike, e.g., `[SP-8087]`'s
  hydraulic/manifold design criteria elsewhere in this reference set).
- **Universal Slopes / "N̄_f/5" derating factor is itself cited to other sources
  (Manson 1966; Manson & Halford 1967), not independently re-derived here** — treat both
  as established literature method, correctly applied and correctly cited, but this report
  is not their origin.
- **OCR quality is generally good for narrative text** (clean 1974 NASA CR typesetting)
  but **completely fails on numeric tables/appendices that are card-image number listings**
  (Appendices B/C) and on some superscript/subscript-heavy inline equations elsewhere in
  the body text (handled here by rendering the specific pages — 0, 8, 29, 43, 44 — as
  images and reading them directly rather than trusting the raw OCR text layer). Table II
  and Fig. 17 in particular were read from page images, not the text layer, because the
  text layer scrambles table row/value alignment.
- **No treatment of the coolant-channel bulging/degradation mechanism itself** — the report
  observes bulging and progressive hot-gas-side surface roughening as testing proceeded,
  and notes it caused progressively rising measured copper temperatures, but does not
  model or quantify that geometric-degradation feedback loop; it re-anchors its own thermal
  boundary conditions to 20th-cycle (roughly mid-life) measured data as a way of sidestepping
  rather than modeling this drift. A tool wanting to model channel bulging over chamber
  life would need a different source.
