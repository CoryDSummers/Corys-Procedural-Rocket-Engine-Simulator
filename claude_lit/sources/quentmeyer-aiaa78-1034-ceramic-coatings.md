# AIAA 78-1034 — Investigation of the Effect of Ceramic Coatings on Rocket Thrust Chamber Life

## Identity

R. J. Quentmeyer, H. J. Kasper and J. M. Kazaroff (NASA Lewis Research Center), *Investigation
of the Effect of Ceramic Coatings on Rocket Thrust Chamber Life*, **AIAA Paper 78-1034**,
AIAA/SAE 14th Joint Propulsion Conference, Las Vegas, July 25-27, 1978. Also issued as **NASA
TM-78892** (1978), per `[Quentmeyer-CR185257]` ref. 20. DOI 10.2514/6.1978-1034. The NTRS
accession was not looked up. `literature/quentmeyer1978.pdf`, with the filename kept as
supplied. 16 PDF leaves:
- leaf 0: AIAA cover;
- leaves 1-7: printed pp.1-7 (text, with references on p.7);
- leaf 8: p.8, Tables I-II and Fig. 1;
- leaves 9-15: pp.9-15, Figs. 2-25.

Printed page = PDF leaf number (offset 0). Tag: `[Quentmeyer-78-1034]`.

**How it relates to the two other Quentmeyer notes:**
- `[Quentmeyer-TMX73665]` (AIAA 77-893, 1977) is this paper's ref. 1. It is the same rig, the
  same channel geometry and the same uncoated-OFHC baseline. This paper's uncoated **S/N 34
  (210 cycles)** is a row of that report's Table I, re-quoted here (Table I footnote a: "Results
  taken from ref. 1").
- `[Quentmeyer-CR185257]` (1990 survey) cites this paper as ref. 20, together with ref. 21:
  Quentmeyer, *Thrust Chamber Thermal Barrier Coating Techniques*, AGARD-CP-449 / **NASA
  TM-100933, 1988**, which is **not held**.
- **The CR-185257 headline TBC result is NOT from this paper**: 0.076 mm ZrO2 + 0.025 mm NiCr,
  no damage after 1450 cycles, against uncoated Amzirc at 393 cycles. This paper used:
  - a 0.203 mm coat, with only about 0.013 mm of it Nichrome;
  - an uncoated **OFHC** baseline at 210 cycles;
  - coated cylinders that lasted 80 and 659 cycles, both failing for reasons unrelated to the coating.

  So the 1450-cycle result comes from the later TM-100933 program, and the 393-cycle Amzirc
  baseline is `[Quentmeyer-TMX73665]` S/N 56. **This paper is primary for the 1978 test
  campaign and its thermal and structural analysis only.** Do not count its 659 cycles and
  CR-185257's 1450 cycles as independent confirmations of one result, and do not merge them.

## Character

A short primary experimental and analytical conference paper from the NASA Lewis
low-cycle-fatigue group. It has four parts:
1. **Two** ZrO2-coated electroformed-copper cylinders were thermally cycled in the
   `[Quentmeyer-TMX73665]` annular LOX/GH2 rig.
2. Post-test sectioning.
3. A 2-D SINDA thermal match to rib and backside thermocouples.
4. A 3-D BOPACE thermoviscoplastic finite-element strain analysis, fed into an isothermal
   strain-range-vs-life curve (classical LCF) to give *theoretical* lives.

What it is best for:
- (a) a real, quantified **coating thickness → hot-wall metal temperature / ΔT / heat-flux
  reduction** table for a regen-cooled copper wall (Table II);
- (b) real **coating erosion behaviour**: 0.203 mm erodes to a stable 0.061 mm within 80 cycles
  and stays adhered;
- (c) **strain-range maps** with and without coating;
- (d) a second physical confirmation of the "doghouse" wall-thinning failure mode, and that the
  coating suppresses it.

It is weak as a life-data source. The n is tiny (2 coated cylinders, 0 coating-caused
failures), and the 1900 and >10,000 cycle lives are classical-LCF *predictions*, which the
authors themselves call of "questionable" accuracy.

The text layer is a mix:
- pp.1-3 and 6 are OCR (two-column interleaving, but the numbers are legible);
- pp.4-5 and 7 have a clean text layer.
- **Tables I-II, Figs. 3, 15, 18-20 and 22-25 were rendered and read visually.** Table values
  below are transcribed from the image.

## Test conditions

`[Quentmeyer-78-1034 pp.2-3, 6-7; Fig. 3 p.9]`

| Item | Value |
|---|---|
| Rig | `[Quentmeyer-TMX73665]` annular chamber; water-cooled Amzirc-type centerbody forms the throat (ZrO2 flame-spray 0.076-0.127 mm on it), contraction = expansion area ratio 1.79, 7.5° expansion half-angle |
| Propellants / MR | LOX (70 showerhead tubes) + GH2 (porous Rigimesh face), **O/F 6.0** |
| Pc / thrust | **4.14 MPa (600 psia)** / ≈5.34 kN (1200 lbf); c* efficiency 93-96 % |
| Test section | 15.24 cm long, 6.60 cm ID cylinder; **72 milled channels 1.69 mm wide × 1.27 mm high, hot wall 0.89 mm, ribs 1.29 mm** (0.051 in; TMX73665 note says 1.27), ED-copper closeout |
| Coolant | LH2, 0.91 kg/s nominal (2.0 lbm/s) design; **1.0 kg/s (2.2 lbm/s) average** actual `[p.6-7]`; flow varies over each cycle (Fig. 8) |
| Cycle | **3.5 s: 1.7 s ignition→end of burn (hot wall reaches steady state) + 1.8 s chill back to LH2 temperature**; 70-90 cycles per LH2 tank |
| Coating (S/N 36, 37) | **ZrO2 plasma-sprayed on a mandrel + arc-plasma Nichrome (NiCr) bond/conductive layer, total 0.203 mm (0.008 in), Nichrome ≈ 0.0127 mm (0.0005 in)**; copper then electroformed onto it (copper-sulfate bath, rotating mandrel), channels milled, wax-filled, ED-Cu closeout; as-made surface finish 2 µm (80 µin) rms `[p.2]` |
| Uncoated baseline (S/N 34) | Same geometry, machined from a forged (wrought, annealed) **OFHC** copper billet `[p.2]` |
| Analysis | SINDA 2-D, 35-element half-channel at the throat plane `[p.4]`; BOPACE 3-D 9-element sector (95 nodes, 285 DOF) incl. plasticity, creep, stress relaxation `[p.5-6, Fig. 21]`; properties from `[CR134806-Props]` (= ref. 15); life curves from Conway et al. NASA CR-121259 (ref. 16) |

## Results tables

**Table I — cylinders and test results** `[Quentmeyer-78-1034 Table I p.8]` (read visually):

| S/N | Configuration | Test cycles | Remarks |
|---|---|---|---|
| 34 | Uncoated (OFHC) | **210** | Typical failure: crack in the cooling-passage wall in the throat region (result from `[Quentmeyer-TMX73665]`) |
| 36 | ZrO2 coating | **80** | Unrepairable crack in a manifold weld seam near the injector, testing terminated |
| 37 | ZrO2 coating | **659** | Throat burnout due to a passage blocked by plater's wax at two points |

**Table II — thermal-analysis results at the throat, steady state** `[Table II p.8]` (read
visually). T_gw is the hot-gas-side **coating** surface. T_mw is the hot-gas-side **metal** wall.
ΔT is metal hot wall to backside.

| S/N | Coating thickness | T_gw K (°R) | T_mw K (°R) | ΔT K (°R) | q MW/m² (Btu/in²·s) |
|---|---|---|---|---|---|
| 34 | none | — | **844 (1520)** | **556 (1000)** | **57.2 (35)** |
| 37 (cycle 5) | 0.203 mm (0.008 in) | **2922 (5260)** | **157 (282)** | **90 (162)** | **12 (7.3)** |
| 37 (cycle 576, eroded area) | 0.061 mm (0.0024 in) | **1878 (3380)** | **489 (880)** | **322 (580)** | **34 (21)** |

**Derived in this note, not stated in the source:** the effective conductance of the coating
(ZrO2 plus the Nichrome layer, in series) comes from q·t / (T_gw − T_mw):

| Coat | Conductance q/(T_gw−T_mw) | Effective k = q·t/(T_gw−T_mw) |
|---|---|---|
| 0.203 mm | 4,340 W/m²·K | **≈0.88 W/m·K** |
| 0.061 mm (eroded, roughened) | 24,500 W/m²·K | **≈1.49 W/m·K** |

These are back-outs of the SINDA model. The coating k that SINDA used as its own input is
**not stated** in the paper. Its source is presumably refs. 4-5 (NASA TN D-7392 / TN D-7055,
effective conductivities of metal-ceramic coatings measured in H2-O2 firings, not held). The
model was tuned to match rib thermocouples, so these k values are a model fit and not a measured
property.

**Fig. 24 — effective strain range (%) at the throat plane** `[Fig. 24 p.15]` (read visually;
a 4-row × 3-column grid across the half-channel, hot-gas surface at the bottom). Maximum per
cylinder:

| Cylinder | Max strain range | Location |
|---|---|---|
| Uncoated | **1.37 %** | hot-gas wall, rib centerline |
| 0.061 mm coat | **0.78 %** | hot-gas wall, rib centerline |
| 0.203 mm coat | **0.12 %** | hot-gas wall, cooling-passage centerline |

**Classical LCF life predictions** `[p.6, Fig. 25 p.15]`. Each strain range is read into the
isothermal curves of wrought annealed OFHC Cu (the uncoated case) or electroformed Cu (the coated
cases), 290-810 K, all environments:

| Case | Predicted life | Measured |
|---|---|---|
| Uncoated | **300 cycles** | 210 cycles |
| 0.061 mm coat | **1900 cycles** | — |
| 0.203 mm coat | **> 10,000 cycles** (off the curve) | — |

Approximate Fig. 25 curve reads (visual, about ±10 %):
- **OFHC**: ≈2.2 % at 10² cycles, ≈0.45 % at 10⁴.
- **E.F. Cu**: ≈1.4 % at 10², ≈0.55 % at 10⁴.
- The two curves cross near 1 % at ≈500 cycles. E.F. Cu is weaker at high strain and better at
  low strain.

## Key results

1. **Coating thickness sets the size of the wall-temperature and flux cut, against an uncoated
   57 MW/m² copper throat.** In each pair below, the first figure is for the 0.203 mm coat and the
   second for the eroded 0.061 mm coat. `[Quentmeyer-78-1034 Table II p.8; pp.5, 7 Summary item 5]`
   - Metal hot-wall temperature: 844 → 157 K (−81 %) and 844 → 489 K (−42 %).
   - Through-wall ΔT: 556 → 90 K and → 322 K.
   - Heat flux: 57.2 → 12 MW/m² (−79 %) and → 34 MW/m² (−41 %).
   - The paper rounds these to "≈80 %" and "≈40 %".
   - The 0.203 mm coat's surface is computed at **2922 K, "close to the melting temperature of
     zirconium-oxide"** `[p.5]`. That is why it eroded.
2. **Erosion behaviour.** `[pp.3-4; Fig. 15 p.13; p.7 items 2-3]`
   - The 0.203 mm coat eroded **non-uniformly**: about 55 % stayed fully intact in the S/N 36
     throat at 80 cycles, and about 30 % in S/N 37 at 659 cycles.
   - Where it eroded, it settled at a **stable, uniform 0.061 mm, including the Nichrome**,
     **within the first ≈80 cycles**. A throat rib thermocouple in S/N 37 rose from ≈150 K to
     ≈300 K over cycles 0-80 and then stayed flat to 659 (Fig. 15, visual).
   - The eroded surface was roughened to 8.6-9.7 µm rms (340-380 µin) but stayed "very well
     adhered".
   - Apart from the burnout spot, **no bare copper was exposed anywhere**: the coating did not
     spall.
   - The authors' reading: 0.203 mm "appeared to be too thick", and a coat applied at 0.061 mm
     "possibly" would not erode, though they say there is no evidence for that yet `[p.6]`.
3. **The coating suppresses the wall-thinning failure mode.** `[p.4, Figs. 16-17 p.13; p.7 item 4]`
   - S/N 37 at the throat after 659 cycles shows "virtually no deformation of the cooling
     passages".
   - Uncoated S/N 34 at 210 cycles shows the severely deformed, thinned passages typical of the
     `[Quentmeyer-TMX73665]` ratcheting mechanism.
   - The authors judge that, without the blocked passage, S/N 37 "would have endured several
     hundred more cycles".
   - Measured life is therefore **≥ 659 cycles coated vs 210 uncoated (≥ 3.1×)**. This is a
     censored lower bound, from one coated article.
   - The S/N 37 burnout itself shows the coating's limit. The wax-blocked passage ran hot, the
     copper underneath deformed progressively until the coating could no longer adhere, and the
     newly bare copper burned through on cycle 659 `[p.4]`. **A TBC does not protect a wall
     whose coolant side has failed.**
4. **Strain reduction.** `[p.6, Figs. 22, 24; p.7 item 6]`
   - Peak cyclic effective strain on the hot wall at the rib centerline was cut to about **½**
     (0.061 mm coat) and about **1/12** (0.203 mm coat) of the uncoated value.
   - The abstract states this as 50 % and 92 % reductions.
   - Peak strain occurs about **0.3 s after ignition**, and the minimum at about 2.2 s (after
     shutdown), at the times of maximum and minimum ΔT. So the governing strain is the
     **start-up thermal transient**, not the steady hold.
   - Mechanical strain components do not reverse within a cycle (radial positive throughout;
     hoop and axial negative). Strain range = max − min effective strain `[Fig. 23 p.14]`.
5. **Theoretical lives** `[p.6, Fig. 25; p.7 item 7]`: 300 cycles uncoated (measured 210, so
   the classical method **over-predicted by about 1.4×**), 1900 cycles for a stable 0.061 mm
   coat, and > 10,000 cycles for a stable 0.203 mm coat. The authors stress that the classical
   strain-range method does not capture channel-geometry change. They use it only to *compare*
   coated with uncoated `[p.5]`.
6. **Consistency check against `[Quentmeyer-TMX73665]` (derived here).**
   - That report's OFHC line, T_gw = 2511·N_f^−0.205 K, gives **839 K** at N_f = 210. This
     paper's SINDA value for S/N 34 is **844 K**. They agree, which is expected because it is
     the same data.
   - Inverting the same line at the eroded-coat T_mw of 489 K gives N_f ≈ **2,900 cycles**,
     against the paper's 1900-cycle strain-based prediction. That is the same order of
     magnitude.
   - The comparison is outside the line's data range, and the liner material differs
     (electroformed Cu, not OFHC), so it is not a validated life.
7. **Heat-flux anchor.** The uncoated S/N 34 cycle-203 analysis gives **57.2 MW/m² (35
   Btu/in²·s)** at the throat `[Table II]`. `[Quentmeyer-TMX73665]` quotes 54 MW/m² (33
   Btu/in²·s) as the average for the rig.
   - `[Quentmeyer-CR185257 p.2]` gives "97.1 MW/m² (33 Btu/in²·s)". That is internally
     inconsistent: 33 Btu/in²·s = 54 MW/m². Use 54-57 MW/m² for this rig.
8. **Fabrication route matters for adhesion** `[pp.1, 6]`. Spraying the ceramic onto a mandrel
   and electroforming the copper onto its rough back gives a better bond than spraying ceramic
   onto a smooth metal wall. The earlier coating literature (refs. 4-10) failed through spalling
   from CTE mismatch and low ceramic ductility. Graded or multilayer coats are the other
   mitigation the paper cites.
9. **Motivation framing** `[p.1]`: the SSME and the 89 kN Advanced Space Engine are "near the
   threshold of the cooling limit" for reusable LH2 regen. Beyond that limit, the available
   coolant ΔP can no longer hold the wall below its limit. Cooling schemes other than pure regen
   (TBCs) will be needed to cut the thermal strain.

## Design method

There is no closed-form correlation. The analysis chain is a methods template:
1. Measured rib and backside thermocouple histories.
2. SINDA 2-D conduction fit, with the gas-side h from unreported calorimeter data and the
   coolant-side h from LH2 correlations, varied around the channel periphery. Transient h is
   scaled with Pc and the LH2 flow, then nudged to fit.
3. BOPACE 3-D sector strain history.
4. Strain range read into isothermal Conway LCF curves.

For `engine_designer` the usable outputs are:
- the **Table II thickness → q / T_mw / ΔT reduction** triplet. It is a real regen-boundary
  anchor for the `zirconia` liner's flux-cut cross-check;
- the derived **effective coat k of about 0.9-1.5 W/m·K**;
- the **erosion-to-a-stable-≈0.06 mm** behaviour, a real bound on how thick a durable sprayed
  coat can usefully be;
- the **≥3.1× measured / 6.3× predicted (0.061 mm) life multipliers**, as magnitude evidence for
  a future TBC life lever.

## Section map

- Abstract and Introduction (SSME/ASE cooling limit, why coatings, earlier spalling history,
  objectives): p.1, leaf 1. Read.
- Apparatus and Test Procedure: chamber assembly, test section and fabrication sequence,
  instrumentation, injector, centerbody, facility, data recording, test procedure (3.5 s cycle):
  pp.2-3, leaves 2-3. Read.
- Test Results (Table I failures) and Post Destructive Analysis (erosion, burnout cause,
  0.061 mm stable coat, no deformation): pp.3-4, leaves 3-4. Read.
- Thermal Analysis (SINDA method, Table II values, 2922 K / 1878 K coat surfaces): pp.4-5,
  leaves 4-5. Read.
- Structural Analysis (BOPACE model and results, strain ratios, life predictions): pp.5-6,
  leaves 5-6. Read.
- Concluding Remarks; Summary of Results (7 items): pp.6-7, leaves 6-7. Read.
- References 1-16 (coating literature refs. 4-10, electroforming CR-72698, SINDA, BOPACE
  CR-143891, Armstrong CR-134979, Esposito CR-134806, Conway CR-121259): p.7, leaf 7. Read.
- Tables I-II and Fig. 1 (assembly schematic): p.8, leaf 8. **Read visually.**
- Fig. 2 (fabrication sequence) and Fig. 3 (wall cross-section dimensions, thermocouple
  locations): p.9, leaf 9. **Read visually.**
- Figs. 4-6 (instrumented cylinder, injector, coated centerbody photos): p.10, leaf 10. Read
  visually (photos, no data).
- Figs. 7-9 (facility schematic, Pc/LH2-flow trace for a cycle, firing photo): p.11, leaf 11.
  Read visually at low resolution. The Fig. 8 axes were not digitized.
- Figs. 10-13 (intact and eroded coating, burnout, wax blockage photos): p.12, leaf 12. Read
  visually.
- Figs. 14-17 (eroded surface; Fig. 15 rib T vs cycle; Fig. 16 coated section after 659 cycles;
  Fig. 17 uncoated deformed section after 210 cycles): p.13, leaf 13. **Read visually.**
- Figs. 18-23 (SINDA matches for S/N 34 and 37, eroded area, BOPACE model, effective-strain
  history, component strains): p.14, leaf 14. **Read visually.** Curve values were not digitized
  beyond the Table II steady states.
- Figs. 24-25 (strain-range grids; OFHC and E.F. Cu LCF curves): p.15, leaf 15. **Read
  visually.** Fig. 25 reads are approximate.

## Caveats

- **n = 2 coated cylinders, and neither failed because of the coating.** Coated life is
  censored: ≥ 659 cycles, set by a fabrication defect (the wax block). The 1900 and > 10,000
  cycle figures are classical-LCF predictions that over-predicted the uncoated case by about
  1.4×. Treat the life multipliers as direction plus order of magnitude only.
- **Not a clean single-variable comparison.** The baseline is wrought annealed OFHC; the coated
  liners are *electroformed* copper with different LCF curves (Fig. 25). This is the same kind
  of confound `[Quentmeyer-CR185257]` has with Amzirc vs ED Cu.
- **The temperatures and fluxes in Table II are SINDA projections** fitted to rib and backside
  thermocouples (best fit to the thermocouple nearest the hot wall). They are not measured
  surface values. The 0.203 mm case is at cycle 5; the eroded case is at cycle 576. The derived
  coat k reflects the model's own unstated coating-property input.
- **No hold-time or creep information.** The hot phase is 1.7 s, and peak strain is at +0.3 s.
  BOPACE includes creep, but no creep result or time-at-temperature effect is reported. This
  paper does nothing for the burn-duration life gap.
- **Effective strain ranges, not measured strains**, from a 9-element model. Only the
  throat-plane 2-D thermal field is used; the authors attribute the thermocouple mismatch to
  axial conduction.
- LOX/GH2 subscale annular rig, 4.14 MPa, 57 MW/m². Hydrocarbon (oxidizing, sooting) gas,
  higher flux (the SSME at about 131-147 MW/m²) and erosion/oxidation of the coat over long
  burns are all untested here.
