# NASA TN D-4733 — Effect of Chamber Pressure, Flow per Element, and Contraction Ratio on Acoustic-Mode Instability in Hydrogen-Oxygen Rockets

## Identity

John P. Wanhainen, Charles E. Feiler and C. Joe Morgan (NASA Lewis Research Center), *Effect
of Chamber Pressure, Flow per Element, and Contraction Ratio on Acoustic-Mode Instability in
Hydrogen-Oxygen Rockets*, **NASA TN D-4733**, August 1968 (manuscript dated April 26, 1968;
Lewis job 128-31-06-05-22, E-4355). NTRS accession 19680021046. `literature/NASA TN D-4733 -
Effect of Chamber Pressure, Flow per Element, and Contraction Ratio on Acoustic-Mode
Instability in H2-O2 Rockets.pdf` (39 PDF leaves). Renamed on 2026-10-18 from its numeric
NTRS filename. **Printed page N = PDF leaf N+2** (printed p.1 SUMMARY is leaf 3; p.33 is
leaf 35). Tag: `[TN-D4733]`.

This is a different document from `[NASA-TN-Acoustic]` (Conrad, Bloomer, Wanhainen & Vincent,
the Dec 1968 interim summary of the whole Lewis 20,000-lbf screech program). That summary
restates this TN's headline results: "decreasing contraction ratio improved stability" and
"stability parameter critical value 4.4". This TN is the primary source for both. It gives
the **exact form** of the parameter, which that note left as "(some form)". Its Ref. 1 is
NASA TN D-3373 (Wanhainen, Parish & Conrad 1966, the injection-velocity-ratio screech study).
Its Ref. 2 is NASA TN D-4040 (Feiler & Heidmann 1967, the GH2 response-factor model).
Neither is in `literature/`.

## Character

A short primary experimental report. It tests one 20,000-lbf (89 kN) LOX/GH2 engine with one
421-element concentric-tube (shear-coaxial) injector and four throat diameters. The engine is
rated by **hydrogen-injection-temperature ramping**: LH2 and warm GH2 are mixed upstream, the
mix is ramped colder (denser) until the chamber spontaneously screeches, and the H2
temperature at that instant is the stability margin. A lower transition temperature means a
more stable combustor. Three test series vary two of {Pc, flow per element, contraction
ratio} at a time so that each effect can be separated (Table I).

What it gives:
- the measured stability boundaries (Figs. 6-9);
- the full data table, about 110 tests (Table II);
- an empirical correlating parameter, with its scatter;
- a response-factor-model interpretation that **attributes the whole effect to hydrogen-
  injector stiffness**.

Trustworthy for its own rig. It is a single chamber diameter, and every test is below the
critical pressure of oxygen (the authors' own caveat). Best for: the direction and mechanism
of Pc / contraction-ratio / element-flow effects on hydrolox coaxial-injector screech, a real
correlating formula, a real 1T frequency data point, and a CR-vs-c* efficiency point.

Text layer is clean NTRS OCR for prose. The equations and Table I were missing or garbled in
the text layer, and Table II leaves 14-19 are RapidOCR. **The following were read visually
from rendered pages:**
- the correlating parameter and eqs. (1)-(2) (leaves 28, 34, 35);
- Table I (leaf 11);
- Table II (a), U.S. units (leaves 14-15);
- Figs. 2, 6, 7, 8, 9, 13, 14, 15, 17, 18 and 19.

## Test article and matrix

`[TN-D4733 §Apparatus pp.3-7; Table I p.9]`

| Item | Value |
|---|---|
| Propellants | LOX + GH2 (LH2/GH2 mixed in a swirl mixer outside the injector; intervening manifold volume 1140 in³ = 0.0187 m³) |
| Chamber | Cylindrical heat-sink, ID 10.78 in (27.36 cm), cylinder length ≈ 12.75 in (32.38 cm); mild steel + 0.030 in (0.76 mm) flame-sprayed ZrO2; ≈ 3 s runs |
| Nozzle | Convergent half-angle 30°; contraction ratio varied by throat diameter + subsonic length |
| Standard engine | CR 1.9, ≈ 20,000 lbf (88.96 kN) sea level at Pc 300 psia (2070 kPa) |
| Injector | 421-element concentric-tube; 0.50 in (1.27 cm) OFHC copper heat-sink faceplate; H2 injection area 4.62 in² (29.8 cm²), O2 0.89 in² (5.74 cm²) → **O2/H2 area ratio 0.19** |
| Element (Fig. 2, read visually) | O2 orifice **D_O = 0.052 in (1.32 mm)**; tube tip OD 0.125 in (3.17 mm); H2 annulus OD 0.172 in (4.37 mm). (Check: 421 × π/4·0.052² = 0.89 in² and 421 × π/4·(0.172²−0.125²) = 4.62 in², so both areas match the stated totals.) |
| Instability criterion | Periodic Pc waveform above the 10-15 psi (69-103 kPa) peak-to-peak noise; transducers flat ±10 % to 10 kHz |

**Table I — nominal test conditions** (read visually, leaf 11):

| Series | Varied / held | Pc, psia (kPa) | Flow per element, lb/s (kg/s) | Thrust/element, lbf (N) | CR | Throat dia., in (cm) |
|---|---|---|---|---|---|---|
| A | Pc & flow/element; CR held | 125 / 190 / 300 / 380 (862 / 1310 / 2070 / 2620) | 0.064 / 0.096 / 0.152 / 0.192 (0.0291 / 0.0436 / 0.069 / 0.0872) | 20 / 30 / 48 / 60 (89 / 133 / 214 / 267) | 1.9 | 7.82 (19.85) |
| B | CR & flow/element; Pc held | 300 (2070) | 0.064 / 0.096 / 0.152 / 0.192 | 20 / 30 / 48 / 60 | 4.5 / 3.0 / 1.9 / 1.5 | 5.04 / 6.22 / 7.82 / 8.78 (12.8 / 15.8 / 19.85 / 22.3) |
| C | CR & Pc; flow/element held | 475 / 300 / 235 (3275 / 2070 / 1620) | 0.152 (0.069) | 48 (214) | 3.0 / 1.9 / 1.5 | 6.22 / 7.82 / 8.78 |

## Screech-transition results

`[TN-D4733 Figs. 6-9 pp.11, 19-20; text p.18-21]`

| Condition | H2 transition temperature at O/F 5 | Source |
|---|---|---|
| Series A, CR 1.9, Pc 125-380 psia (all four flows) | **140 °R (78 K)**, one line for all Pc | text p.18 + Fig. 6 |
| Series B, Pc 300 psia, CR 1.5 (0.192 lb/s/element) | **118 °R (66 K)** | text p.18 |
| Series B, CR 1.9 (0.152) | ≈ 140 °R (78 K) | Fig. 7, read visually |
| Series B, CR 3.0 (0.096) | ≈ 190-200 °R (≈ 105-110 K), read visually ±10 °R | Fig. 7 |
| Series B, CR 4.5 (0.064) | **240 °R (133 K)** | text p.18 |
| Series C, fixed 0.152 lb/s/element: CR 1.5 / 1.9 / 3.0 at Pc 235 / 300 / 475 | ≈ 125 / 135 / 205 °R (≈ 69 / 75 / 114 K), read visually | Fig. 8 |
| O2 injection temperature 140 → 240 °R (78 → 133 K; ρ_O 1200 → 871 kg/m³), O/F 4.75-5.5 | T_H,tr rose ≈ **50 °R (27.8 K)**, from ≈ 150 to ≈ 200 °R | text p.21 + Fig. 9 |

On every boundary the transition temperature **rises roughly linearly with O/F**, so a lower
O/F is more stable. The slope steepens with CR (Fig. 7).

**Representative Table II rows** (U.S. units, read visually, leaves 14-15; "transition" rows):

| Test | CR | T_H, °R | Pc, psia | ΔP_H, psi (ΔP_H/Pc) | ΔP_O, psi (ΔP_O/Pc) | O/F | η_c*, % | W_cr |
|---|---|---|---|---|---|---|---|---|
| 38 | 1.5 | 121 | 239 | 24.7 (10.3 %) | 129.0 (54 %) | 4.92 | 100.8 | 4.386 |
| 326 | 1.5 | 115 | 346 | 40.0 (11.6 %) | 246.4 (71 %) | 4.80 | 98.7 | 4.423 |
| 57 | 1.9 | 145 | 198 | 19.5 (9.8 %) | 73.2 (37 %) | 5.13 | 99.1 | 4.674 |
| 333 | 1.9 | 135 | 358 | 39.5 (11.0 %) | 181.5 (51 %) | 5.11 | 100.9 | 4.701 |
| 255 | 3.0 | 261 | 270 | 12.5 (4.6 %) | 68.9 (26 %) | 5.35 | 93.2 | 4.324 |
| 493 | 3.0 | 135 | 501 | 23.7 (4.7 %) | 153.2 (31 %) | 3.66 | 101.8 | 3.701 |
| 275 | 4.5 | 270 | 317 | 11.0 (3.5 %) | 47.3 (15 %) | 5.76 | 91.7 | 3.697 |

The ΔP/Pc percentages are computed here from the tabulated psi values. They are not printed
in the source.

## Key results

1. **Throttling total flow at fixed geometry does not move the boundary.** Series A at CR 1.9
   shows one transition line for Pc 125-380 psia (862-2620 kPa) and 0.064-0.192 lb/s per
   element. The reason: Pc and the injector ΔP vary together, so their ratio is constant.
   `[TN-D4733 §Stability Characteristics p.18; §Application p.33]`
2. **Decreasing contraction ratio lowers the transition temperature (more stable), at fixed
   Pc or at fixed flow per element.** At Pc 300 psia and O/F 5, CR 4.5 gives 240 °R (133 K)
   and CR 1.5 gives 118 °R (66 K). The series B and C curves are "about the same".
   `[TN-D4733 p.18, Figs. 7-8 pp.19-20]`
3. **Contraction ratio has no direct acoustic role in this data.** CR "does not appear
   independently" in the correlation. Its effect enters only through its effect on total flow,
   and therefore on Pc or on the hydrogen-injector ΔP. Since both Pc and ΔP are nearly
   proportional to flow, the CR effect is the same whichever of them is allowed to vary.
   `[TN-D4733 §Application and Interpretation p.33]`
4. **Correlating parameter** (exact form, read visually):

       W_cr = (2g·ΔP_H/ρ_H)^1/2 · ρ_O · D_O^1.25 · (1/(O/F))^1/2

   Terms: ΔP_H = H2 injector ΔP, ρ_H = H2 injection density, ρ_O = O2 injection density,
   D_O = O2 orifice diameter. The value is **4.4 lbm/(s·in^0.75)** at the boundary: above it is
   stable, below it unstable. The standard deviation is 9 % on this data and 17.5 % on the Ref. 1
   data (four D_O values, 0.052-0.110 in, plus recessed-post data).

   In SI this is ≈ **31.4 kg/(s·m^0.75)**. That number is converted here (×7.13); it is not
   printed, but it agrees with Fig. 14's dual axis. The O2-temperature series fits 5.9. The
   authors attribute that to injector deterioration and exclude it.
   `[TN-D4733 §Correlation p.26-28, Figs. 14-15; Summary of Results item 4 p.34]`
5. **The parameter replaced Ref. 1's constant injection-velocity-ratio criterion.** The H2
   velocity term became (2gΔP_H/ρ_H)^1/2, as the response-factor model suggests. This
   correlated the recessed-element data better. It also shows that stability depends on
   **O2 density and jet diameter, not O2 velocity**. The D_O^1.25 exponent and the O/F
   exponent are best fits to the data, and "other forms … would similarly correlate".
   `[TN-D4733 p.28]`
6. **Interpretive form.** For T_H between 65 and 130 °R (36-72 K), the authors approximate
   P ≈ ρ·T_H² as a fit to NBS para-H2 data. That gives eq. (2):
   T_H,tr ≈ (Pc / 2gΔP_H)^1/2 · (1/(ρ_O·D_O^1.25)) · (O/F)^1/2.

   **The transition temperature scales as 1/√(ΔP_H/Pc).** The hydrogen-injector stiffness is
   "the real determinant of the screech boundary at any given chamber-pressure condition".
   Raising ΔP_H by area **or by orifice hydraulic characteristics** stabilises. A denser O2 or
   a larger O2 jet also stabilises.
   `[TN-D4733 §Application p.32-33, eqs. 1-2]`
7. **Design rule from the data.** Thrust can be scaled up by enlarging the throat and the flow
   without losing stability margin; the margin actually improves. "Increasing the nozzle throat
   diameter and simultaneously decreasing the chamber pressure to maintain thrust constant is
   a technique to improve the stability of an engine." `[TN-D4733 p.33]`
8. **Element flow matters only through ΔP_H.** In series B, more flow per element at fixed
   Pc and fixed injector area raises ΔP_H/Pc and stabilises. In series A, more flow per
   element at fixed CR leaves the boundary unchanged. The model curves (Figs. 17-18) show the
   **H2 transition density rising almost linearly with total flow**: about 0.2 → 0.65 lb/ft³
   (≈ 3 → 10.5 kg/m³) over 25 → 85 lb/s (≈ 11 → 39 kg/s), read visually.

   At fixed H2 area, that makes the boundary approximately a **constant H2 injection
   velocity**, even though the O2 velocity varied 3:1. For this element, a derived check of
   eq. (4) at W_cr = 4.4, D_O = 0.052 in and ρ_O ≈ 1140-1200 kg/m³ gives a critical H2
   velocity of ≈ 230-245 m/s at O/F 5 (≈ 210-270 m/s over O/F 4-6). This is arithmetic done
   here, not a source value. `[TN-D4733 §Response-Factor Model p.30-32, Figs. 17-19]`
9. **Response-factor model.** It follows Ref. 2's in-phase-addition model, with three
   coupling processes: H2 flow, LOX-drop vaporisation and nozzle flow. Only the H2 response
   was varied; **the O2 response was held invariant and still fit**.
   - The H2 response factor needed for instability is **N_H2 = 2.39 at O/F 5.5**, at an
     evaluation frequency of 3400 Hz.
   - The H2 time delay τ_b was refit from 0.00009 s (Ref. 2) to **0.00008 s**.
   - Below Pc ≈ 225 psia (1550 kPa) the model predicts that the stability limit **rises** as
     Pc falls, at constant flow and varying nozzle area (Fig. 19). This is a prediction; the
     series C data start at 235 psia.

   `[TN-D4733 pp.29-32]`
10. **Screech mode and frequency.** The dominant mode, triggered spontaneously, was **1T at a
    calculated 3000-3500 Hz** (depending on O/F) in the 27.36 cm chamber. Lesser peaks appeared
    at ≈ 3800 Hz (2L), 6800 Hz and 7200 Hz. At Pc ≈ 135-200 psia the mode later shifted to
    **2T at 5500-6000 Hz**. The amplitude was about the same at every Pc. CR had no apparent
    effect on the amplitude or the mode.

    (Derived here: 1T = 0.586·a/D implies a ≈ 1400-1630 m/s. That is a usable real data point
    for `combustion_stability.py`'s 1T formula. 2T/1T ≈ 1.7 is consistent with 3.054/1.841.)
    `[TN-D4733 §Screech Characteristics p.21, Figs. 10-12 pp.22-24]`
11. **Performance at the transition point.**
    - Series A: η_c* ≈ 100 % over the whole Pc / flow-per-element range (transient data;
      scatter sometimes exceeds 100 %).
    - **Series B: CR 4.5 gave ≈ 94 %, about 5 points below CR 1.5 / 1.9.** The authors
      attribute this to lower flow per element (larger LOX drops at lower injection velocity)
      plus lower chamber gas velocity, both lengthening the LOX vaporisation length.
    - Series C, CR 3.0 at constant flow per element: −1 to −2 % in 3 of 4 tests, which is
      within data accuracy.

    So the CR-4.5 penalty is mostly a flow-per-element / injection-velocity effect, not a CR
    effect. `[TN-D4733 §Combustion Performance pp.21-26, Fig. 13]`
12. **Oxygen temperature is a real lever.** Warming the LOX from 140 to 240 °R (78-133 K) is
    strongly destabilising: T_H,tr rises ≈ 50 °R (27.8 K) (Summary item 3; the Fig. 9 trend).
    `[TN-D4733 p.21, Fig. 9 p.20]`
13. **Scope limits stated by the authors.** The parameter "may change as other injector or
    chamber parameters are varied". It was evaluated only in one chamber diameter, and only
    below the oxygen critical pressure (≈ 731 psia / 5.04 MPa; that value is the standard
   property, not printed in the source). `[TN-D4733 pp.34, Summary item 6]`

## Design method

Within the data range, the authors propose W_cr as "a useful design tool". It predicts the
change in the screech limit for any change in:
- H2 injection area or O2 injection area;
- O/F;
- O2 temperature or density;
- Pc;
- O2-post recess;
- contraction ratio;
- flow per element and number of elements.

Procedure:
1. Compute W_cr = (2gΔP_H/ρ_H)^1/2·ρ_O·D_O^1.25·(O/F)^-1/2 at the design point. The H2
   injection density comes from the H2 injection temperature and pressure.
2. Require W_cr > 4.4 lbm/(s·in^0.75) for stability.
3. Equivalently, require T_H above the T_H,tr of eq. (2).

`[TN-D4733 p.33-34]`

**Applies only to concentric-tube LOX/GH2 elements of this family, sub-critical LOX, in a
≈ 27 cm chamber.**

## Section map

- Cover, title page, abstract: leaves 0-2 (p.ii). Read.
- Summary: p.1 (leaf 3). Read. The parameter's equation is image-only here.
- Introduction: p.2 (leaf 4). Read. Covers objectives, the response-factor framing, and the
  standard engine.
- Symbols: p.3 (leaf 5). Read. Gives W_cr units lbm/(in^3/4·s).
- Apparatus (test facility, engine, H2 temperature controller/mixer, instrumentation), Figs.
  1-4: p.3-8 (leaves 5-10). Read. Fig. 2 (element geometry) read visually.
- Procedure + Table I: p.9-11 (leaves 11-13). Read. Table I read visually. Fig. 5
  (oscillograph) seen only as text.
- **Results — Stability Characteristics (Figs. 6-9; series A/B/C plus O2 temperature):
  p.11-21 (leaves 13-23). Read. Figs. 6-9 read visually.**
- Table II Experimental Data (a) U.S. units: p.12-14 (leaves 14-16). Leaves 14-15 read
  visually; leaf 16 (O2-temperature series) OCR only. Table II (b) SI units: p.15-17 (leaves
  17-19). **as-needed - not read (2026-10-18)**; it duplicates (a).
- Screech Characteristics (Figs. 10-12, spectra): p.21-24 (leaves 23-26). Read. Spectra seen
  only as text.
- Combustion Performance (Fig. 13): p.21-26 (leaves 23-28). Read. Fig. 13 read visually.
- **Correlation of Stability Data (Figs. 14-15): p.26-28 (leaves 28-30). Read visually.**
- Application of Response-Factor Model (Figs. 16-19): p.28-32 (leaves 30-34). Read. Figs.
  17-19 read visually; Fig. 16 (response factor vs H2 density) not rendered.
- **Application and Interpretation (eqs. 1-2, design rules): p.32-34 (leaves 34-36). Read
  visually.**
- Summary of Results (8 items): p.34-35 (leaves 36-37). Read.
- References (7): p.35 (leaf 37). Read.

## Caveats

- **The stability rating is by H2 injection temperature. It is not a bomb rating, and it is
  not an absolute stable/unstable verdict for flight hardware.** It measures how much margin
  remains before *spontaneous* 1T onset as the H2 is made colder and denser. Real hydrolox
  regen engines inject H2 that is far warmer than 60-140 °R, so they sit on the stable side of
  this mechanism by construction. The data say nothing about bomb-triggered or other-mode
  stability.
- **One chamber diameter (27.36 cm), one injector family, Pc ≤ 501 psia (3.45 MPa), all
  sub-critical LOX.** The authors flag both limits themselves. Scaling W_cr = 4.4 to a
  large-diameter or supercritical (SSME/RS-25-class) chamber is unsupported. 1T frequency
  falls with diameter, and the response-factor model is frequency-dependent.
- The form of W_cr is semi-empirical. The D_O^1.25 and O/F^-1/2 exponents are best fits, the
  constant may shift with other geometry, and the scatter is 9-17.5 %. The O2-temperature
  series gave 5.9 because of an apparently degraded injector. That shows how much the
  constant can move on the "same" hardware.
- The P ≈ ρ·T_H² closure (eq. 1-2 temperature form) holds only for 36-72 K hydrogen. Use the
  ρ_H form of W_cr otherwise.
- Performance data were taken under transient (temperature-ramp) conditions, with
  instrument-time-constant scatter, so some η_c* values exceed 100 %. Treat the CR-4.5 ≈ 5-point
  c* penalty as directional.
- The Table II ΔP/Pc percentages, the SI value of W_cr (31.4), the critical H2 velocity
  (≈ 230-245 m/s) and the implied sound speed are this note's own arithmetic. They are not
  source-printed numbers.
- Values read off figures (Figs. 7-8 CR 3.0 lines, Figs. 17-18 densities) are ±5-10 % visual
  reads. The text-quoted values (140, 118, 240 °R; 50 °R; 4.4; 9 %/17.5 %; 2.39; 0.00008 s;
  3000-3500 Hz) are exact.
