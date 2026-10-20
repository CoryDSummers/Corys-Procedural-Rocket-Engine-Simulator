# AFRPL-TR-69-149 — USAF Propellant Handbooks: Hydrazine Fuels, Volume I

## Identity

Walter R. Marsh & Bruce P. Knox (Bell Aerosystems Co., Buffalo NY), *USAF Propellant Handbooks:
Hydrazine Fuels, Volume I*, **AFRPL-TR-69-149**, March 1970, contract F04611-69-C-0005, Air
Force Rocket Propulsion Laboratory. DTIC **AD507864**. It was originally CONFIDENTIAL; some
leaves still carry "(C)" or "(This page is Unclassified)" markings, and it is now publicly
released. File: `literature/AFRPL-TR-69-149 - USAF Propellant Handbook Hydrazine Fuels Vol
I.pdf`, renamed from `AD507864.pdf` on 2026-10-18. The PDF has **543 leaves**.

Page numbering is section-relative ("2.3-13", "2.4-1", "6-16"), and the OCR text layer
captures few of these numbers. **Every cite below is therefore `§section, leaf N`** (leaf = the
0-based PDF page). There is no table of contents. The topic index is Table 1.1-1 (leaf 6), and
the section 2 contents list is on leaf 9.

Tag: `[USAF-Hydrazine]`.

## Character

A Bell Aerosystems compilation of critically evaluated property data for the hydrazine family
(ammonia, DETA, N2H4, MMH, UDMH, 50-50 / Aerozine-50, and 15 MHF/MAF/BA/BAF/MGGP blends).
- For every property, the authors review all the measurements they know of (Aston, Scott,
  Aerojet, Rocketdyne, Barger, Ahlert, ...) and say which they trust.
- They then publish a **least-squares fit with its standard deviation and validity range**,
  plus a one-page **Property Summary Sheet** of "selected best values" at 298 K.
- The handbook flags its own weak data, for example "provisional", "rather dubious", or
  "should be considered as provisional data only".
- That makes it the right source for **SI property correlations** (vapor pressure, density,
  viscosity, cp, thermal conductivity, surface tension) of the four fuels `engine_designer`
  uses: N2H4, MMH, UDMH and A-50.
- It also has the 1950s-60s **thermal-stability / regen-coolant explosion** experience
  (§5.3.6, §6.2) and monopropellant catalyst-bed practice (§6.3, §6.6).

It does **not** tabulate hydrazine decomposition-gas temperature, molecular weight or gamma
versus ammonia dissociation. It has no MMH/UDMH regen-coolant heat-transfer or burnout
correlations. Volume II (not in `literature/`) covers the remaining blends.

**Reading method.** The text layer is NTRS-era OCR. Running text is mostly fine, but
**equations are badly garbled**: dropped terms, lost signs, merged digits.
- The four Property Summary Sheets (leaves 70, 112, 147, 183) and the N2H4 / MMH / UDMH
  equation pages (leaves 74, 88, 97, 113, 118, 125, 134, 140, 148, 151, 152, 167, 168, 176-177)
  were **read visually from rendered page images**.
- The N2H4 density, viscosity, cp and surface-tension equations (leaves 74, 75, 88, 98, 107)
  and **every A-50 equation** (leaves 184, 189, 190, 200, 201, 209, 214) were first taken from
  the text layer, then **read visually 2026-10-18** (300 dpi crops where digits were small)
  and re-checked numerically against the summary sheets' 298 K values and the stated NBP.
  That pass corrected the A-50 VP leading constant (9.55878 -> **9.55828**), recovered the
  A-50 viscosity K form and the quadratic term of the A-50 k °R form, and found two misprints
  in the A-50 heat-of-formation working (Caveats). MMH eq. 2.4-1 and UDMH eq. 2.5-1 were
  re-spot-checked on the image the same day and are unchanged.

## Property tables (selected best values, 298 K, SI with source units in parentheses)

From the Property Summary Sheets: N2H4 §2.3.1 leaf 70, MMH §2.4.1 leaf 112, UDMH §2.5.1 leaf
147, 50-50 §2.6.1 leaf 183. All read visually.

| Property | N2H4 | MMH | UDMH | A-50 (50/50 wt N2H4/UDMH) |
|---|---|---|---|---|
| Formula weight, g/mol | 32.048 | 46.072 | 60.102 | 41.805 (C0.6956H5.3911N2.0) |
| Melting point | 274.68 K (34.75 °F) | 220.78 K (-62.27 °F) | 215.94 K (-70.94 °F) | 267.6 K (22.0 °F) (binary curve; Aerojet: 18-21 °F by composition) |
| Normal boiling point | 387.37 K (eq. 2.3-1) | 360.80 K | 335.47 K (ICT gives 63 °C = 336.15 K) | 343 K nominal (70 °C; the eq. gives 343.13 K, the extra precision is "not warranted") |
| Critical T | 653 K (380 °C; 1896 data, "doubtful") | 585 K (312 °C; Aerojet) | 523 K (250 °C; Barger) | 607 K (334 °C; mixture-rule pseudocritical, "rather dubious") |
| Critical P | 14.7 MPa (145 atm) | 8.24 MPa (81.3 atm) | 5.98 MPa (59 atm, from eq. 2.5-2 at Tc; Barger measured 53.5 atm) | 11.9 MPa (117.5 atm, from eq. 2.6-2 at Tc) |
| Critical density | 231 kg/m³ | 290 kg/m³ (est.) | 275 kg/m³ | not available |
| Vapor pressure | 1.892 kPa (14.19 mmHg) | 6.60 kPa (49.47 mmHg) | 22.28 kPa (167.1 mmHg) | 18.45 kPa (138.4 mmHg) |
| Liquid density | 1003.7 kg/m³ | 870.2 kg/m³ | 786.1 kg/m³ | 898.7 kg/m³ |
| Viscosity | 9.13e-4 Pa·s (0.913 cP) | 7.75e-4 Pa·s (0.775 cP) | 4.92e-4 Pa·s (0.492 cP) | 8.09e-4 Pa·s (0.809 cP) |
| cp liquid | 3078 J/kg·K (0.7356 cal/g·K) | 2930 J/kg·K (0.7002) | **2946 J/kg·K (0.704) on the sheet, but eq. 2.5-10 gives 2806 (0.6706)**, see Caveats | 3063 J/kg·K (0.732) |
| Thermal conductivity | **0.490 W/m·K** (eq. 2.3-12; provisional; the sheet's "7.86e-5 cal/cm·s·K" is the Btu/ft·s·°R value) | **0.248 W/m·K** (5.92e-4 cal/cm·s·K) | **0.157 W/m·K** (3.76e-4 cal/cm·s·K) | **0.286 W/m·K** (6.83e-4 cal/cm·s·K) |
| Surface tension | 66.45 mN/m | 33.83 mN/m | 24.09 mN/m | 29.10 mN/m |
| Sonic velocity | 2074 m/s | 1548 m/s | 1247 m/s | 1612 m/s |
| Heat of vaporization | 43.4 kJ/mol (10.38 kcal/mol, calc. at 298 K); 9.34 kcal/mol at NBP | 40.37 kJ/mol (9.648 kcal/mol, measured, 298 K); 8.894 at NBP | 35.00 kJ/mol (8.366 kcal/mol, measured, 298 K); 7.797 at NBP (calc.) | 33.67 kJ/mol (8.048 kcal/mol at NBP, calc.) |
| **ΔHf° liquid, 298 K** | **+50.43 kJ/mol (+12.054 kcal/mol) = +1574 kJ/kg** | **+54.84 kJ/mol (+13.106 kcal/mol) = +1190 kJ/kg** | **+51.63 kJ/mol (+12.339 kcal/mol) = +859 kJ/kg** | **+50.85 kJ/mol (12.153 kcal/mol, ideal mixing) / +51.51 kJ/mol (12.310 kcal/mol with heat of mixing) per 41.805 g = 1216 / 1232 kJ/kg** |
| Heat of combustion (to CO2(g) + H2O(l) + N2) | 148.635 kcal/mol | 312.0 kcal/mol (text) | 473.701 kcal/mol (text; the sheet's "437.7" is a digit transposition) | 312.112 kcal/mol |

### Temperature correlations (T in K unless noted)

All are least-squares fits from the source. SI conversions: 1 mmHg = 133.322 Pa; 1 atm =
101,325 Pa; 1 g/cc = 1000 kg/m³; 1 cP = 1e-3 Pa·s; 1 cal/g·K = 4184 J/kg·K;
1 cal/cm·s·K = 418.4 W/m·K.

**Vapor pressure** (log = log10):

| Fluid | Low range (up to NBP) | High range (NBP to Tc) | Fit quality, cite |
|---|---|---|---|
| N2H4 | log P(mmHg) = -6.50603 - 653.880/T + 0.047914·T - 4.9886e-5·T² (2.3-1; Scott + Hieber + Chang, 15-114 °C) | log P(atm) = 4.73294 - 1457.79/T - 145452.1/T² (2.3-4; ICT / Lobry de Bruyn data) | sd 1.71 mmHg, avg 2.3 %; §2.3.3.1 leaf 74 (visual) |
| MMH | log P(mmHg) = 7.11158 - 1104.571/T - 152227.6/T² (2.4-1; Aston + Aerojet) | log P(atm) = 4.5106 - 1355.07/T - 98237.8/T² (2.4-2; forced through NBP and Tc) | sd 1.28 mmHg, avg 0.40 %; §2.4.3.1 leaves 113, 118 (visual) |
| UDMH | log P(mmHg) = 6.73578 - 875.89/T - 140001.0/T² (2.5-1; -35 °C to NBP) | log P(atm) = 4.9439 - 1659.84/T (2.5-2; Barger, forced through NBP) | sd 4.54 mmHg, avg 5.4 %; §2.5.3.1 leaves 148, 151 (visual) |
| A-50 | log P(mmHg) = 9.55828 - 2820.587/T **+** 181627.9/T² (2.6-1; Aerojet + Bell, -10 to 71 °C, **46 % ullage**) | log P(atm) = 5.2379 - 2086.62/T **+** 99387.3/T² (2.6-2; Rocketdyne, small ullage, forced to join the Aerojet/Bell curve) | §2.6.3.1 leaves 184, 189. Read visually 2026-10-18: both "+" signs confirmed; the leading constant is **9.55828** (the earlier text-layer reconstruction 9.55878 was off by 5e-4). 9.55828 gives 138.4 mmHg at 298.15 K and NBP 343.13 K exactly; eq. 2.6-2 gives 117.5 atm at 607 K. °R forms: 2.6-1a log P(psia) = 7.84466 - 5077.049/T_R + 588473.7/T_R²; 2.6-2a 6.4051 - 3755.91/T_R + 322015.7/T_R² |

Evaluated (kPa): at 293.15 K, N2H4 1.40 / MMH 4.98 / UDMH 17.5 / A-50 15.0. At 350 K,
25.7 / 68.8 / 161 / 124.

**A-50 vapor pressure depends on ullage.** Because it is a mixture, the vapor is mostly UDMH
(§2.6.3.1 leaf 184). At 26.7 °C, Bell measured 3.96 psia (27.3 kPa) at 25 % ullage and
3.06 psia (21.1 kPa) at 75 % ullage. The true (zero-ullage) value is the higher one.

**Saturation temperature at jacket pressures** (inverting the high-range fits; derived here):

| P | N2H4 | MMH | UDMH | A-50 |
|---|---|---|---|---|
| 0.5 MPa | 442 K | 417 K | 391 K | 405 K |
| 1.0 MPa | 472 K | 448 K | 420 K | 438 K |
| 2.0 MPa | 507 K | 485 K | 455 K | 476 K |
| 3.45 MPa | 540 K | 519 K | 487 K | 511 K |

Compare `[Sutton Table 8-5]`, quoted in `coolant_props.py`: UDMH boils at 400 K at 1 MPa and
489 K at 3.45 MPa. This source gives 420 K at 1 MPa, about 20 K higher, and agrees at 3.45 MPa.

**Liquid density** (g/cc):
- **N2H4**: ρ = 1.23078 - 6.2668e-4·T - 4.5284e-7·T² (2.3-5; Ahlert and others, 0-177 °C;
  sd 0.0011 g/cc, avg 0.089 %). °R form 2.3-5a: ρ(lb/ft³) = 76.8353 - 0.021735·T_R -
  8.7254e-6·T_R².
  - Read visually 2026-10-18. The text layer had dropped the T² term; the earlier value
    4.5285e-7 had been converted from the °R form, the printed K coefficient is 4.5284e-7.
    Either reproduces the sheet's 1.0037 at 298.15 K (§2.3.3.2 leaf 74, visual).
- **MMH**: ρ = 1.15034 - 9.3949e-4·T (2.4-3; -52 to +84 °C; sd 0.0026). Above that range,
  saturated densities up to Tc are a provisional curve (Fig. 2.4-4) (§2.4.3.2 leaf 118,
  visual).
- **UDMH**: ρ = 1.06041 - 7.7507e-4·T - 4.8648e-7·T² (2.5-3). Linear alternative:
  1.09450 - 1.0343e-3·T (2.5-4). Range: melting point to 60 °C; Fig. 2.5-4 continues to the
  critical point (§2.5.3.2 leaf 151, visual).
- **A-50**: ρ = 1.17423 - 9.2417e-4·T (2.6-3; 0-70 °C; sd 0.0003, avg 0.023 %). Gives
  **903.3 kg/m³ at 20 °C** and 898.7 at 25 °C. MIL-P-27402A accepts **894-903 kg/m³ at
  25 °C** (§2.6.3.2 leaf 189; §2.6.6.2 leaf 214).

**Viscosity**:

| Fluid | Fit | Range, quality, cite |
|---|---|---|
| N2H4 | log μ(cP) = 3.1788 - 0.015384·T + 1.5395e-5·T² (2.3-9) | melting point to 177 °C; sd 0.032 cP, avg 2.48 %, probable accuracy ±3 %; §2.3.3.5 leaf 75 (read visually 2026-10-18) |
| MMH | log μ(cP) = -7.9944 + 6123.96/T - 1.7458e6/T² + 1.8509e8/T³ (2.4-7) | melting point to 80 °C; avg 1.84 %; §2.4.3.5 leaf 125 (visual) |
| UDMH | log μ(cP) = -0.25411 - 623.532/T + 181151.8/T² (2.5-7) | -55 to 60 °C; avg 1.6 %; §2.5.3.5 leaf 152 (visual). Printed without "log"; the figure (leaf 165) and the 0.4925 cP check confirm log10 |
| A-50 | log μ(cP) = -0.28445 - 501.489/T + 166602.5/T² (2.6-6); °R form 2.6-6a: log μ(lb/ft·s) = -3.4572 - 902.540/T_R + 539754.2/T_R² | 0-70 °C (Aerojet + Schluter, Schluter double-weighted); sd 0.009 cP, avg 0.7 %; §2.6.3.5 leaf 190 (read visually 2026-10-18, 300 dpi). The K form, illegible in the text layer, is clear on the image; both give 0.8086 cP at 298.15 K |

**Liquid cp** (cal/g·K):
- **N2H4**: 0.88415 - 1.3949e-3·T + 3.0074e-6·T² (2.3-15; Scott + Hough; sd 0.0024 cal/g·K;
  good to ~356 K (640 °R), "extrapolation not advised") (§2.3.5.4 leaf 98, read visually
  2026-10-18).
  - Commercial-grade (2.5 % H2O, 0.5 % NH3) above that range: 0.29512 + 2.0193e-3·T -
    1.8559e-6·T² (2.3-16; Ahlert, 58-191 °C = 331-464 K; sd 0.004, avg 0.31 %); propellant
    grade is 1.3 % above anhydrous at 350 K (leaf 107, read visually 2026-10-18).
- **MMH**: use the **°R form 2.4-10a, 0.6534 - 1.2801e-5·T_R + 1.8487e-7·T_R²**. It
  reproduces the sheet's 0.7002 at 298 K and is valid from the melting point to 124 °C.
  - The printed K form (2.4-10: 0.6528 - 1.7284e-5·T + 3.9142e-7·T²) gives 0.682 and is
    inconsistent; probably a misprint.
  - In K the °R form is 0.6534 - 2.3042e-5·T + 5.9898e-7·T² (§2.4.5.4 leaf 140, visual).
- **UDMH**: 0.4071 + 8.838e-4·T (2.5-10, linear; 0.6706 = 2806 J/kg·K at 298 K).
  - Data: Aston (smoothed, ≤ 298 K) plus Rocketdyne 1.7-71 °C, labelled provisional.
  - In Fig. 2.5-12 the Rocketdyne points sit 0.7-4.5 % above Aston (§2.5.5.4 leaves 176-177,
    visual).
- **A-50**: 0.51241 + 7.3624e-4·T (2.6-11; Rocketdyne, 2.2-49.2 °C; ±2.8 % band, avg
  0.76 %; sample 51.3 % N2H4 / 48.3 % UDMH / 0.4 % H2O) (§2.6.5.4 leaf 214, read visually
  2026-10-18).

**Liquid thermal conductivity** (cal/cm·s·K; ×418.4 = W/m·K):

| Fluid | Fit | Source, range, cite | W/m·K at 273 / 298 / 350 / 400 K |
|---|---|---|---|
| N2H4 | 2.1067e-4 + 6.5541e-6·T - 1.1179e-8·T² (2.3-12) | Rocketdyne graph, origin unexplained, "provisional", 25-127 °C; §2.3.3.7 leaf 88 (visual) | 0.488 / 0.490 / 0.475 / 0.437 |
| MMH | 3.4025e-4 + 2.200e-6·T - 4.545e-9·T² (2.4-9) | Rocketdyne, 24 points, -17 to 152 °C, avg 1.51 %, max 4.0 %; §2.4.3.7 leaf 134 (visual) | 0.252 / 0.248 / 0.232 / 0.206 |
| UDMH | 6.7975e-4 - 1.0187e-6·T (2.5-9) | Rocketdyne, -18 to 122 °C, avg 1.6 %; §2.5.3.7 leaf 167 (visual) | 0.168 / 0.157 / 0.135 / 0.114 (400 K is just past the 395 K range) |
| A-50 | 7.1983e-4 + 3.7467e-7·T - 1.6736e-9·T² (2.6-9) | Rocketdyne, 10-152 °C, avg 0.78 %; §2.6.3.7 leaves 200-201 (read visually 2026-10-18) | 0.292 / 0.286 / 0.270 / 0.252 |

For A-50 the °R form 2.6-9a (leaf 201) is K(Btu/ft·s·°R) = 4.8338e-5 + 1.3978e-8·T_R -
3.4686e-11·T_R². The text layer had lost its quadratic term; on the image it is present, and
it reproduces the sheet's 4.58e-5 Btu/ft·s·°R at 536.67 °R (derived), consistent with the K
form.

**Surface tension** (dyn/cm = mN/m):
- **N2H4**: 139.903 - 0.24637·T (2.3-10; Bernard + Baker, only 21-40 °C; sd 0.9 dyn/cm)
  (leaf 88, read visually 2026-10-18).
- **MMH**: 63.480 - 0.09944·T (2.4-8; -40 to 60 °C) (leaf 125).
- **UDMH**: 56.705 - 0.1094·T (2.5-8; -54 to 50 °C) (leaf 167).
- **A-50**: 105.960 - 0.41606·T + 5.3088e-4·T² (2.6-8; Bell capillary rise, 1.5-58 °C,
  claimed ±1.0 %) (leaf 200, read visually 2026-10-18).

## Key results

1. **Storable vapor pressure curves: OQ "storable-propellant vapor pressure" closed for the
   fuels.** The VP fits for N2H4, MMH, UDMH and A-50 are above, all the way to the critical
   point `[USAF-Hydrazine §2.3.3.1 leaf 74; §2.4.3.1 leaves 113, 118; §2.5.3.1 leaves 148,
   151; §2.6.3.1 leaves 184, 189]`.
   - They match `[Sutton Table 7-1]`'s two UDMH points: UDMH 0.1093 MPa at 339 K, where eq.
     2.5-2 gives ~0.115 MPa.
   - N2O4 is **not** covered; it is an oxidizer and belongs in a different handbook volume.
2. **UDMH thermal conductivity is 0.157 W/m·K at 298 K, falling to 0.135 at 350 K.**
   - That is ~22 % below the 0.20 W/m·K the tool carries over from MMH
     (`cooling/coolant_props.COOLANT_TRANSPORT`, Tier 3) `[USAF-Hydrazine §2.5.3.7 leaf 167]`.
   - **MMH itself is 0.248 W/m·K at 298 K** `[§2.4.3.7 leaf 134]`. The tool's 0.20 is
     MMH at ~400 K, so it sits low for a 290-350 K jacket.
   - The UDMH/MMH ratio is about 0.63.
3. **UDMH liquid properties confirm the tool's current constants.**
   - cp 2806 J/kg·K at 298 K by eq. 2.5-10, against the tool's 2810.
   - ρ 786 kg/m³ at 298 K, against 784.
   - μ 4.92e-4 Pa·s, against 4.8e-4.
   - Cite: `[§2.5.3.2 leaf 151; §2.5.3.5 leaf 152; §2.5.5.4 leaf 176]`. The sheet's
     cp 0.704 does not match its own fit; see Caveats.
4. **A-50 density is 903.3 kg/m³ at 20 °C and 898.7 at 25 °C.** The MIL-P-27402A acceptance
   band is 894-903 kg/m³ at 25 °C `[§2.6.3.2 leaf 189; §2.6.6.2 leaf 214]`. The project's 903
   is the 20 °C value (and the spec's upper edge); 900 is also inside spec. Choose 903 vs 900
   by reference temperature, not by data error.
5. **Liquid heats of formation, 298 K:**
   - N2H4 +12.054 kcal/mol (+50.43 kJ/mol). This is the mean of two routes, 12.103 (via the
     hydrate) and 12.005 `[§2.3.5.1 leaf 97, visual]`.
   - MMH +13.106 kcal/mol (+54.84 kJ/mol) `[§2.4.5.1 leaf 135]`.
   - UDMH +12.339 kcal/mol (+51.63 kJ/mol), from a heat of combustion of 473.701 kcal/mol
     (Aston/Donovan mean) `[§2.5.5.1 leaf 168]`.
   - A-50 **+12.310 kcal/mol per 41.805 g (294.5 cal/g = 1232 kJ/kg)**. This includes an
     endothermic heat of mixing of 3.75 cal/g (+0.157 kcal/mol). Ideal mixing alone gives
     12.153 `[§2.6.5.1 leaf 209]`.
6. **Hydrazine decomposition stoichiometry** `[§2.3.4.1 leaf 97, visual]`:
   - Step 1: 3 N2H4 → 4 NH3 + N2, exothermic, 144,300 Btu per lb-mol of reaction as written
     (≈ 80.2 kcal per 3 mol N2H4). The source labels it "Btu/lb", but only per lb-mol is
     consistent with ΔHf.
   - Step 2: 4 NH3 → 2 N2 + 6 H2, endothermic, 79,200 (≈ 44.0 kcal).
   - Overall, with X the fraction of NH3 dissociated: 3 N2H4 → 4(1-X) NH3 + (1+2X) N2 + 6X H2.
     The printed equation reads "+ 6 H2", but the hydrogen balance needs 6X.
   - **No table of Tc, M or gamma versus X is given** (see Caveats).
   - From the stoichiometry alone (derived here, not a source number): **M = 96.13/(5 + 4X)
     g/mol**, i.e. 19.2 at X = 0, 13.7 at X = 0.5, 10.7 at X = 1.
   - **The tool's 11.0 g/mol implies X ≈ 0.93, almost fully dissociated NH3.** Because step 2
     is endothermic, that is the cold end of the range. It sits awkwardly with the tool's
     1400 K (ASSUMPTIONS ~149). The pair is a calibration, not a physical state.
7. **Hydrazine as a regenerative coolant failed in practice.** "Attempts to use hydrazine as a
   regenerative coolant have been generally unsuccessful ... due to uncontrolled thermal
   explosions in the cooling passages" `[§5.3.6.1 leaf 505]`.
   - Underlying reports: Bartz, Noel & Grant, JPL Pub. 111, 1957; Kimball, Bell 1959.
   - Bell twice detonated **pressurized liquid hydrazine at 250 °F (394 K)** through burnout
     of an electrically heated wire in pool-boiling heat-transfer tests.
   - Liquid MMH and UDMH have no recorded explosions. Card-gap tests on all three were
     negative.
   - MHF-1 (MMH/N2H4/hydrazinium nitrate) "has been known to detonate violently when heated
     to approximately 500 °F (533 K) in ... regenerative cooling passages" `[§4.2.3.1 leaf
     433]`.
   - The blend programme existed to give fuels "better thermal stability than hydrazine, for
     use as a regenerative coolant" `[§1.1 leaf 7]`.
8. **Thermal stability temperatures** `[§6.2.3.1-6.2.3.2 leaves 513-515]`:
   - Olin's literature review: hydrazine "does not decompose at an explosive rate below
     500 °F" (533 K). Later industry experience put **the safe operating limit 150 °F lower,
     about 350 °F (450 K)**.
   - Measured activation energies scatter widely: 7, 19 and 72.7 kcal/mol, depending on
     purity and wall passivation. Measured rates are ~0.04-0.09 %/h at 171-275 °C in glass or
     quartz.
   - **UDMH**: spontaneous decomposition (no air, sprayed into a hot flask) at **740 °F
     (666 K)**; self-ignition in air at 454 °F (508 K); activation energy 28.7 kcal/mol,
     controlled by gas-phase thermal energy rather than the wall.
   - UDMH "is not sensitive to shock and is thermally stable" `[§2.5.2.1 leaf 148]`.
   - MMH is "much superior to hydrazine with respect to freezing point, stability, storage
     and as a coolant" `[§2.4.2.1 leaf 113]`.
   - MMH storage gassing: 0.45 mmHg/day at 160 °F with 10 % ullage `[§6.2.3.3 leaf 516]`.
9. **Hydrazine vapor flammability** `[§5.3.4 leaf 501]`:
   - A decomposition flame can be sustained in hydrazine vapor **without air** above about
     150 °F (339 K), at 35-100 % vapor concentration. Hydrazine has no rich flammability limit.
   - Spontaneous ignition of hydrazine/air: 520 °F (544 K) in glass, 315 °F (430 K) on
     stainless steel.
   - N2O4 vapor in air makes UDMH, MMH and N2H4 ignite at room temperature above 8, 11 and
     14 vol % NO2 respectively `[leaf 502]`.
10. **Monopropellant reactor practice** `[§6.3.1, §6.5, §6.6.1 leaves 519-530]`:
    - Shell 405 (Ir on alumina) specification: start at 0 °F, ignition delay < 0.5 s,
      0.065 lb/s·in² (45.7 kg/s·m²) bed loading, support inert to NH3/H2 up to 1200 °C.
    - Long-duration showerhead-injector loading is **0.045 lb/s·in² (31.6 kg/s·m²)**. Staged
      tube injectors approach 0.2 (141 kg/s·m²).
    - **Injector ΔP of 10-20 % of Pc** gave stable thruster operation.
    - Catalyst particle size should be < 1/8 of the reactor diameter, with fine 20-30 mesh
      granules on top (≤ ~0.3 in deep).
    - Thermal beds needed ≥ 1000 °F (811 K) to sustain N2H4 decomposition (TRW). JPL's
      Co/alumina reactor restarts spontaneously above 400 °F (478 K) `[§1.1 leaf 7]`.
    - JPL's thermal UDMH decomposition needed L* = 5000 in (127 m) for smooth running, with
      c* ≈ 3200 ft/s (975 m/s) at 300 psia (2.07 MPa). The minimum L* was 2100 in (53 m).
11. **Critical points, for the jacket boiling-vs-supercritical question** (table above):
    - MMH 585 K / 8.24 MPa and UDMH 523 K / 5.98 MPa are experimental but "reasonably good
      estimates" given decomposition.
    - N2H4's 653 K / 14.7 MPa dates from 1896. A-50's 607 K is a mixture-rule pseudocritical,
      and the source warns against using it in an equation of state.

## Implications for engine_designer (for the integration pass; no edits made)

- **`thermo_tables.saturation()` / the suction model** (OQ "storable vapor pressure"): the
  §2.3-2.6 low-range fits give the hydrazine-family fuels a cited vapor pressure. The suction
  model currently assumes zero for storables. N2O4 still needs its own source.
- **`cooling/coolant_props.COOLANT_TRANSPORT`**:
  - UDMH k: 0.20 → ~0.15 (0.157 at 298 K, 0.135 at 350 K), cited.
  - MMH k: 0.20 is below this source's 0.248 at 298 K and 0.232 at 350 K.
  - MMH μ: 5.8e-4 is this source's value at ~315 K (7.76e-4 at 298 K, 3.70e-4 at 350 K).
  - All four fuels now have T-dependent fits if the property path ever moves off constants.
- **`FUEL_CP_J_KGK` / UDMH cp 2810 / ρ 784**: confirmed (Key result 3). These can move from a
  Sutton single point to `[USAF-Hydrazine]`.
- **`MAX_COOLANT_DELTA_T_K` 150 K for MMH/UDMH (ASSUMPTIONS ~222, ~286)**: no direct regen
  limit for MMH/UDMH exists here. The source bounds it:
  - A 293 K inlet + 150 K = 443 K outlet is under hydrazine's ~450 K "safe operating" figure.
  - It is far under UDMH's 666 K spontaneous decomposition.
  - It is below both critical temperatures (MMH 585 K, UDMH 523 K).
  - **But in a low-pressure (pressure-fed) jacket the binding limit is boiling, not
    decomposition.** Saturation at 1 MPa is 420 K for UDMH and 448 K for MMH, so a 150 K rise
    from 293 K would boil UDMH below ~1.5 MPa. That is a real-physics reason to tie the
    storable limit to jacket pressure, not a flat ΔT. The tool should warn, not block.
- **Hydrazine `_TABLES` 1400 K / 1.30 / 11.0 (ASSUMPTIONS ~149)**: not closed (Key result 6).
  The M(X) relation shows 11.0 g/mol means X ≈ 0.93, which is inconsistent with a hot 1400 K
  state. A catalytic-decomposition performance source (CEA / Schmitz / RRC NAS 7-372) is still
  needed.
- **A-50 export density 903 vs 900** (OQ "export densities"): 903 = 20 °C; 899 = 25 °C;
  spec 894-903 at 25 °C.
- **Heats of formation for the Cantera/CEA reactant definitions** (MMH, UDMH, N2H4, A-50
  blend with heat of mixing): Key result 5. The MON-x dissolved-NO enthalpy is an oxidizer
  question and is **not** here.

## Section map

- Front matter, cover / notices / abstract / acknowledgements: leaves 0-4. Abstract read
  (lists the 21 propellants).
- **§1.0 Introduction (1.1 General: history, blends for regen-coolant stability, JPL hydrazine
  monoprop; 1.2 Scope; 1.3 Instructions) + Table 1.1-1 subject index: leaves 5-9. Read.**
- §2.1 Ammonia (property sheet, VP, density, viscosity, k, critical constants, heat capacity,
  logistics): leaves 10-~58. **as-needed - not read (2026-10-18)**. NH3 liquid properties,
  e.g. for an NH3-coolant or decomposition-product question.
- §2.2 Diethylenetriamine (DETA): leaves ~59-68. **as-needed - not read (2026-10-18)**. A
  MAF-blend ingredient, not used by the tool.
- **§2.3 Hydrazine: leaves 69-110.** Read: 2.3.1 summary sheet (leaf 70, visual); 2.3.2.3
  spec; 2.3.3.1-2.3.3.2 VP/density (leaves 73-74, visual); 2.3.3.5 viscosity (leaf 75, visual);
  2.3.3.6-2.3.3.7 surface tension, k (leaf 88, visual); 2.3.4.1 decomposition reactions and
  2.3.5.1 heat of formation (leaf 97, visual); 2.3.5.2-2.3.5.5 melting point, critical
  constants, cp, ΔHvap (leaves 98, 107, visual).
  - Sonic velocity / compressibility (leaf 75), dielectric constant, refractive index, other
    chemical reactions, logistics (leaves 107-110) and the figure pages (76-87, 90-96, 99-106):
    **as-needed - not read (2026-10-18)**. Figures only plot the fitted data.
- **§2.4 MMH: leaves 111-145.** Read: summary sheet (leaf 112, visual); 2.4.2-2.4.3.2 intro,
  VP, density (leaves 113, 118, visual); 2.4.3.4-2.4.3.6 compressibility, viscosity, surface
  tension (leaf 125, visual); 2.4.3.7 k (leaf 134, visual); 2.4.5.1-2.4.5.5 ΔHf, critical
  constants, cp, ΔHvap (leaves 135, 140).
  - Gas solubility, logistics/analysis/shipping (leaves 141-145) and figure pages:
    **as-needed - not read (2026-10-18)**.
- **§2.5 UDMH: leaves 146-181.** Read: summary sheet (leaf 147, visual); 2.5.2-2.5.3.3 intro,
  spec, VP, density, sonic (leaves 148, 151, visual); 2.5.3.4-2.5.3.5 compressibility,
  viscosity (leaf 152, visual); 2.5.3.6-2.5.3.7 surface tension, k (leaf 167, visual);
  2.5.4.1 oxidation/explosion and 2.5.5.1 ΔHf (leaf 168, visual); 2.5.5.3-2.5.5.5 critical
  constants, cp, ΔHvap (leaves 175-177, visual).
  - Gas solubility, logistics (leaves 178-181) and figure pages: **as-needed - not read
    (2026-10-18)**.
- **§2.6 50-50 blend (Aerozine-50): leaves 182-216.** Read: summary sheet (leaf 183, visual);
  2.6.2-2.6.3.5 intro, spec, VP (ullage effect), density, sonic, compressibility, viscosity
  (leaves 184, 189-190, visual); 2.6.3.6-2.6.3.7 surface tension, k (leaves 200-201, visual);
  2.6.3.10 distillation; 2.6.5.1-2.6.5.5 ΔHf with heat of mixing, melting point,
  pseudocritical, cp, ΔHvap (leaves 201, 209, 214, visual); 2.6.6.2 spec density band (leaf
  214, visual).
  - Gas solubility, logistics (leaves 215-216) and figure pages: **as-needed - not read
    (2026-10-18)**.
- §2.7-2.21 MHF-3, MAF-3, MAF-4 (Hydyne), MAF-1, MAF-2, MAF-5, MGGP-1, MHF-1, MHF-2, MHF-4,
  MHF-5, MHF-5B, MHF-6, BA-1014, BAF-1185: leaves 217-381. **as-needed - not read
  (2026-10-18)**. Property sheets for blends the tool does not model.
- §3.0 Ternary blend systems (3.2 N2H4-UDMH-H2O; 3.3 N2H4-MMH-H2O; 3.4 N2H4-MMH-HN with
  detonability; 3.5 N2H4-HN-H2O; 3.6 N2H4-NH3-H2O; 3.7 UDMH-DETA-CH3CN; 3.8; 3.9 refs):
  leaves 382-422. **as-needed - not read (2026-10-18)**. Composition-property diagrams; read
  3.2 if off-nominal A-50 or water-contaminated hydrazine matters.
- §4.0 Handling, storage, compatibility (4.1 intro; 4.2 handling/transfer/disposal; 4.3
  storability and pressure-rise data incl. MHF-3 tables; 4.4 materials compatibility; 4.5
  refs): leaves 423-483. **as-needed - not read (2026-10-18)**. Only the 4.2.3.1 MHF-1
  regen-passage detonation remark (leaf 433) and a skim of 4.3 (leaves 443-457: 160 °F storage
  pressure rise vs. tank alloy) were read. 4.4 is the materials-compatibility source if the
  tool ever needs one.
- §5.0 Safety (5.1 intro; 5.2 toxicity, exposure limits, protection, detection; 5.3 fire and
  explosion hazards; 5.4 refs): leaves 484-508. **5.3.4-5.3.6 (leaves 501-505) read: vapor
  flammability/decomposition flame, N2O4-vapor ignition, regen-coolant explosions, shock
  insensitivity. 5.1-5.3.3 and 5.4 refs (leaf 508 skimmed for the Bartz JPL-111 citation):
  as-needed - not read (2026-10-18).** Toxicology and fire-fighting.
- **§6.0 Catalysts and catalytic decomposition (6.1 intro; 6.2 thermal stability and
  decomposition; 6.3 catalytic decomposition, Shell 405 and others; 6.5 thermal decomposition,
  thermal beds; 6.6 reactor design technology): leaves 509-530. Read.**
  - 6.4 radiolytic decomposition (leaves 523-525) and 6.7 refs (531-534): **as-needed - not
    read (2026-10-18)**.
- §7.0 Appendices (7.1 index of propellants/acronyms; 7.2 units and conversion factors; 7.3
  terminology): leaves 535-542. **as-needed - not read (2026-10-18)**.

## Caveats

- **Inconsistencies in the source itself, all caught by checking the summary sheet against
  the fits:**
  - The N2H4 sheet lists k = 7.86e-5 under "cal/cm·s·K". That number is the Btu/ft·s·°R value;
    the true value is 1.17e-3 cal/cm·s·K = 0.490 W/m·K.
  - The UDMH sheet lists cp 0.704 at 298 K, while its own eq. 2.5-10 gives 0.6706. Fig.
    2.5-12's Rocketdyne aluminum-calorimeter points sit near 0.69-0.70 at 300-310 K and
    Aston's near 0.65. Use the fit; uncertainty is ~±4 %.
  - The UDMH sheet's heat of combustion "437.7" is a transposition of the text's 473.701.
  - The MMH cp K-form coefficients are inconsistent with the °R form and the sheet. Use the °R
    form.
  - The N2H4 decomposition equation prints "6 H2" for "6X H2".
  - The A-50 heat of mixing is printed as "0.157 cal/mole"; it is kcal/mol.
  - In the A-50 ΔHf working (leaf 209, visual) the sum line prints UDMH as "12.399" (the table
    above it and §2.5.5.1 give 12.339; only 12.339 yields the printed 12.153) and the mixing
    line prints "12.153 + 0.257" (the text gives 0.157; only 0.157 yields the printed 12.310).
    The final 12.310 kcal/mol / 294.5 cal/g is self-consistent and unaffected.
- **N2H4 thermal conductivity is "provisional"**: a Rocketdyne graph whose origin the authors
  could not trace. The MMH, UDMH and A-50 values are measured (Rocketdyne concentric-cylinder
  cell, 1.5-4 % scatter).
- **Critical constants are weak.** All four fuels decompose near Tc, and A-50's value is a
  mixture-rule estimate. Use them for a boiling-vs-supercritical warning, not an equation of
  state.
- **Vapor-pressure fits above NBP** for MMH and UDMH are forced through the NBP and the
  (uncertain) critical point. The A-50 values depend on ullage.
- The A-50 fits rest on Aerojet/Rocketdyne/Bell data from samples of 47.5-51.4 % N2H4,
  0.4-1.2 % H2O; spec composition varies by ~±1 %.
- **Thermal-stability numbers are glass-ampoule and spray-flask tests, not heated-tube coolant
  tests.** The hydrazine explosion history is anecdotal (two Bell burnout events plus JPL's
  report). The source has no MMH/UDMH regen heat-transfer, burnout, or coking/deposit data.
- **Not answered here**: hydrazine decomposition-gas Tc / gamma / M versus X, N2O4 / MON
  properties, and storable TSH / thermodynamic suppression.
- A-50 equations and N2H4 density/viscosity/cp/surface-tension: read visually 2026-10-18
  (previously text-layer only). One coefficient changed (A-50 VP 9.55878 -> 9.55828, a 0.1 %
  change in P, no effect on any 298 K table value) and the N2H4 density T² coefficient is now
  the printed 4.5284e-7 rather than the °R-converted 4.5285e-7. No value in the 298 K
  property table, the critical constants or the heats of formation changed.
