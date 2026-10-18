# NASA CR-135356 — Preburner of Staged Combustion Rocket Engine

## Identity

M. C. Yost (project engineer), Rockwell International, Rocketdyne Division, *Preburner of
Staged Combustion Rocket Engine*, Final Report, **NASA CR-135356**, Rocketdyne report
**RI/RD78-114**, February 1978 (work July 1975 - December 1977). Contract **NAS3-19713**, NASA
Lewis Research Center. NASA project managers A. Pavli and H. Price. Rocketdyne program manager
H. Diem, project manager A. T. Zachary, senior project engineer P. C. Dennies. NTRS accession
**19780016336** (N78-24279). Report documentation page: 280 pp. `literature/NASA CR-135356 -
Preburner of Staged Combustion Rocket Engine.pdf` (renamed 2026-10-18 from its numeric NTRS
filename). The PDF is a microfiche scan of **303 leaves** (0-302). The fiche bookmarks are only
scan-tile names. Many leaves are large fold-out drawings, so the printed-page-to-leaf offset
**is not constant**. Spot points: printed p.1 (Introduction) = leaf 14, p.7 = leaf 16, p.14 =
leaf 25, p.19 = leaf 34, p.25 = leaf 40, p.27 = leaf 42, p.36 = leaf 52, p.61 = leaf 79,
p.106 = leaf 150, p.153 = leaf 201, p.156-157 = leaves 204-205, p.165-166 = leaves 213-214,
p.194-198 = leaves 242-246, p.248 = leaf 295, p.253 = leaf 300, p.255 (References) = leaf 302.
Appendix A and the distribution list are not in the scan. Tag: `[CR135356-Preburner]`.

## Character

This is a NASA-Lewis contractor final report covering design, fabrication and hot-fire test of
the combustion devices for Rocketdyne's **Advanced Space Engine (ASE)**. The ASE was a
20,000 lbf (88.9 kN) **LOX/LH2 fuel-rich staged-combustion** orbit-transfer-vehicle engine,
"extrapolated from the SSME and J-2 designs" `[p.1]`. The hardware tested was:
- A single **fuel-rich LOX/GH2 preburner**: 15 recessed shear-coaxial elements, Inconel 625
  combustor with a GH2-cooled liner and six quarter-wave acoustic cavities.
- Its exhaust split into two ducts (ox-turbopump and fuel-turbopump branches), feeding
  **orifice turbine simulators**. No turbopumps were run.
- The main injector and a Zr-Cu channel-wall chamber from the earlier Advanced Thrust Chamber
  Technology program (`NASA CR-135221`, not in `claude_lit/`).
- An A-286 tube nozzle to eps 175 and a mild-steel heat-sink extension to eps 400, run with a
  GN2 diffuser/ejector.

It is primary test data. The most useful items are:
- Measured preburner gas temperatures vs mixture ratio, with a plotted theoretical curve.
- Duct-to-duct and in-duct temperature spreads, i.e. the hot-streak and uniformity reality of
  a fuel-rich H2 preburner.
- Preburner c*, design and test preburner Pc vs main Pc, and the design preburner pressure
  distribution (injector dP).

Main-chamber performance and heat transfer are secondary bonuses. **Everything here is
hydrogen. There is no hydrocarbon or oxidizer-rich data**, so soot/coking and ox-rich
temperature are not covered.

Scan quality: the text layer is badly garbled on many leaves (NTRS OCR), and the RapidOCR
re-reads are mostly good. **Every number in the tables below was confirmed against a rendered
page image.** Figs 101, 111 and 130 were also digitized from 200-dpi pixel traces with tick
marks located by pixel scan, giving ±10-15 K and ±0.01 MR.

## Preburner design point and test data

**Design point**, `[CR135356-Preburner Table 2 p.7; Table 40 p.248]` (identical tables), read
visually:

| Parameter | Value |
|---|---|
| Preburner chamber pressure | 2328 N/cm² = **23.3 MPa** (3377 psia) |
| Combustion temperature | **1053 K** (1896 °R) |
| Mixture ratio O/F | **0.82** (at engine MR 6.5, the top of the 5.5-6.5 excursion) |
| Total flow | 4.16 kg/s (9.18 lb/s) |
| Fuel (GH2) inlet temperature | 239 K (431 °R) = mixed-mean chamber + nozzle coolant outlet |
| Oxidizer (LOX) inlet temperature | 91 K (163 °R) |
| Main chamber (Table 1/41) | 88.9 kN, Pc 1380 N/cm² = 13.8 MPa (2000 psia), MR 6.0, eps 175 regen / 400 uncooled, ERE 98 % |
| Preburner Pc / main Pc | **1.69** (derived, 2328/1380) |

**Worst-case (maximum engine point) design analysis**, `[Table 7 p.35; p.27; Fig. 17 p.36]`,
read visually:

| Item | Value |
|---|---|
| Preburner Pc / Tc / total flow | 3034 N/cm² (4400 psi) / **1129 K** (printed "(2050 R)") / 5.153 kg/s |
| Liner coolant | GH2 at 281 K, 45 g/s, 0.76 mm annulus. Liner is Inconel 625, 0.89 mm thick; hot-gas bore 6.032 cm |
| Pressure distribution, Fig. 17 | **Ox manifold 3723 N/cm² (5400 psi); fuel manifold 3447 (5000); fuel at element/liner-annulus 3389 (4915); combustor and both exhaust branches 3023 (4385)** |
| Derived injector dP / Pc at that point | **ox ≈ 0.23; fuel ≈ 0.14 (manifold) / 0.12 (element-annulus station)** (derived, from Fig. 17) |
| Wall temperatures, Fig. 16 | Structural shell ≤ 450 K (350 °F) behind the liner. Liner hot face 1122 K (1560 °F). Uncooled transition/branch wall reaches **1139 K (1590 °F)** = gas temperature |

The text on p.27 gives the worst case as "**1383 K (2030 R)**", but 2030 °R = 1128 K. Table 7
gives 1129 K with "(2050 R)". **The 1383 K is a typo.** The worst-case gas is about
**1128-1139 K**.

**Preburner injector element**, `[§Preburner Injector p.14, p.19; Table 3 p.25; Table 4]`,
read visually. Table 3 compares it with the SSME elements:

| | SSME OPB | SSME FPB | Phase B full-scale PB | **ASE** |
|---|---|---|---|---|
| Flow per element, kg/s | 0.204 | 0.204 (0.525 lb/s printed) | 0.330 | **0.284** |
| Fuel inlet T, K | 164 | 164 | 69 | 239 |
| Ox inlet T, K | 114 | 114 | 106 | 108 |
| Pc, N/cm² (psia) | 3623 (5254) | 3570 (5178) | 2413 (3500) | 2335 (3386) |
| Ox post velocity, m/s | 25.1 | 24.3 | 24.4 | 26.2 |
| Fuel sleeve / post-end / recess velocity, m/s | 358 / 255 / 210 | 369 / 262 / 216 | 364 / 259 / 213 | 290 / 227 / **213** |
| LOX post recess, mm | 2.54 | 2.54 | 2.54 | 2.54 |
| Fuel sleeve gap, mm | 0.648 | 0.58 | 0.69 | 1.50 |
| Face area per element, mm² | 160.6 | 162.6 | 192.9 | 194.8 |

The injector has **15 elements** in two concentric rows. Element pitch is about 12.5 mm and the
faceplate is solid copper (NARloy-A as built `[p.106]`). The ASE's larger fuel sleeve gap is
"principally the result of higher temperature of the fuel".

**Preburner-only test summary**, `[Table 27 p.156]`, read visually. Pc is at the injector end.
c* is corrected for the estimated turbine-simulator orifice growth:

| Test / slice | Pc, N/cm² (psia) | MR O/F | c*, m/s | Avg gas T, K |
|---|---|---|---|---|
| 026 / 1 s | 1461.3 (2119.3) | 0.589 | 2030 | 703 |
| 028 / 3 s | 1507.7 (2186.7) | 0.851 | 2152 | 1067 |
| 029 / 1 s | 2296.6 (3330.8) | 0.648 | 2006 | 825 |
| 030 / 3 s | 2312.4 (3353.7) | 0.740 | 2056 | 952 |
| 031 / 1 s | 2276.8 (3302.1) | 0.781 | 2128 | 1051 |
| 031 / 2 s | 2270.7 (3293.3) | 0.798 | 2140 | 1071 |
| 031 / 4 s | 2259.1 (3276.4) | 0.814 | 2180 | 1087 |
| 031 / 7 s | 2245.9 (3257.3) | 0.828 | 2262 | 1117 |

"Average gas temperature" is the mass-weighted mean of the two exhaust-duct readings.

**Theoretical preburner temperature vs MR**, `[Fig. 111 p.165]`, digitized. The basis is LOX
plus near-ambient GH2, which is what the test program used. The report states neither the
fuel inlet temperature nor the Pc basis for the curve:

| MR O/F | 0.2 | 0.3 | 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 | 1.0 |
|---|---|---|---|---|---|---|---|---|---|
| Theoretical T, K (±10) | 531 | 623 | 719 | 811 | 904 | 997 | 1093 | 1185 | 1280 |

The curve is almost linear at **about 935 K per unit O/F** (derived slope). The dashed fit
through the good-LOX-quality staged-combustion tests (009-011) runs **~15 K under it**: 795 vs
811 K at MR 0.5, 889 vs 904 K at 0.6, 1171 vs 1185 K at 0.9. That is a measured/theoretical
temperature ratio of **~0.98-0.99** (derived).

**Duct-to-duct and in-duct spread**, `[Fig. 101 p.157]` digitized; `[Tables 36-37
p.196-197]` read visually:

| Source | MR | O2-turbine duct | H2-turbine duct | Note |
|---|---|---|---|---|
| Fig. 101 lines, 2275 N/cm² preburner-only | 0.80 | 893 K | 1037 K | mass-weighted average 973 K |
| Fig. 101 lines, 2275 N/cm² preburner-only | 0.90 | ~1000 K | ~1245 K | average ~1125 K; **spread ~245 K** |
| Table 36/37, test 017 (staged-combustion) | 0.595 | 861 (A), 875 (G) K | 942 (M), 930 (N), 919 (U) K | igniter-inlet station 852 / 895 K |
| Table 36/37, test 021 | 0.590 | 827 (B), 868 (F) K | 932 (M), 899 (O), 926 (P) K | |
| Table 36/37, test 022 | 0.564 | 822 (B), 853 (F) K | 934 (M), 876 (O), 917 (P) K | |
| Table 36/37, test 016 | 0.529 | 797 (A), 812 (G) K | 852 (N), 850 (U) K | |

Each probe letter is a thermocouple at a different immersion depth (Fig. 129). B, O and U are
nearest the duct wall.

## Key results

1. **First real hot-fire LOX/H2 fuel-rich preburner T-vs-MR data in `claude_lit/`.** The
   design is 1053 K at O/F 0.82 and 23.3 MPa `[CR135356-Preburner Table 2 p.7]`. Measured
   mass-averaged duct temperatures span **703-1117 K over MR 0.59-0.83** `[Table 27 p.156]`.
   The theoretical curve is ~531 K at MR 0.2, ~904 K at 0.6 and ~1280 K at 1.0 `[Fig. 111
   p.165]`.
   - This brackets `PREBURNER_GAS_PROPERTIES` LOX/LH2 `tin_k` 1113 K (`[ch12-materials]`
     SSME ~840 °C), which here corresponds to MR ≈ 0.83-0.85.
   - It also brackets the SSME fuel-preburner value in `[SSME-Orientation p.28-34]`: 1310 °F
     = 983 K at MR 0.86, with colder ~164 K fuel.
   - The design point vs the theoretical curve is 1053 K vs ~1111 K at MR 0.82, a 58 K gap.
     That gap is consistent in size with the colder 239 K design fuel vs the ~ambient test
     GH2. An ideal-mixing estimate gives ~50 K (derived, not from the report).
2. **Delivered temperature tracks theory closely once LOX quality is good.** Staged-combustion
   tests 009-011 sit ~15 K (1-2 %) under the theoretical line `[Fig. 111 p.165]`.
   - The earlier preburner-only tests fell up to ~100-160 K low at the same MR.
   - The report attributes this to **mixed-phase (two-phase) LOX from poor pre-test LOX bleed
     and chill**, which gives poorer combustion efficiency and lower gas temperature `[p.166]`.
   - Points flagged "partial GOX flow" fall to ~430-470 K at MR ≈ 0.35-0.40.
   - A preburner Tin therefore depends on feed-system conditioning as well as on MR.
3. **Turbine-inlet non-uniformity is real and large in a short, single-preburner, split-duct
   layout.**
   - In preburner-only testing at 2275 N/cm², the **H2-turbine duct ran ~145-245 K hotter
     than the O2-turbine duct** at MR 0.8-0.9 `[Fig. 101 p.157]`. The report did not
     investigate the cause, and later staged-combustion tests did not show it to that
     extent `[p.154]`.
   - In the later tests the H2 duct still ran ~60-90 K hotter than the O2 duct at
     MR 0.56-0.60 `[Tables 36-37 p.196-197]`.
   - Within a duct, probes nearest the wall read lower. The report attributes this to the
     combustor **liner-sleeve GH2 coolant** (dumped at the combustor exit) not being fully
     mixed into the core flow `[p.194]`.
   - The design intent was a **mixing uniformity Em ≈ 95 %**, from SSME preburner cold-flow
     correlations `[Fig. 11 p.24; p.23]`.
   - Em falls linearly from ~95.5 % at (ρg/ρl)^(2/3)(Vg/Vl) = 0.5 to ~83.5 % at 6.9 `[Fig. 11
     p.24]`, read visually.
4. **Hot-streak control was handled at the element level**, `[p.14, p.106]`:
   - The element fuel flow is metered by the post/sleeve annulus.
   - The feed slots are narrower (0.89 mm) than the annulus (1.50 mm) so they act as a filter
     against plugging. A 6 % slot restriction costs only 2 % of fuel flow (SSME cold flow).
   - The report states the reason: "a reduction in element fuel flowrate raises the element
     mixture ratio and produces the potential for high temperature streaks".
   - Brazed spacer wires keep each LOX post concentric in its sleeve "so hot streaks from
     fuel starvation could be avoided".
   - This is the preburner counterpart of `[SP-8081]`'s uniform-MR (UMR) injector philosophy.
5. **Preburner combustion completeness by design.** The CICM model predicts complete
   atomization within 12.7 mm of the face, 60-104 µm drops, and **complete vaporization and
   reaction within 76 mm (3.0 in)** of the face `[p.19; Figs 8-10]`. The recess is 2.5 mm and
   the H2 recess velocity is 213 m/s. Measured preburner c* is **2006-2262 m/s** `[Table 27
   p.156]`. **No theoretical preburner c* is given**, so η_c* for the preburner cannot be
   formed from this report.
6. **Preburner / main-chamber pressure ratio.**
   - Design: 23.3 / 13.8 MPa = **1.69** (derived) `[Table 2; Table 1]`.
   - In the eps-400 tests the preburner ran **22.5-23.0 MPa against main-chamber
     injector-end Pc 15.4-15.8 MPa**, a ratio of **1.45-1.47** (derived) `[Table 42 p.253]`.
     The turbines were simulated by orifices whose size set that drop, and the orifices grew
     ("stretching") from the hot gas `[p.154]`. So the test ratio is a hardware-configuration
     number, not a turbine-power result.
   - For comparison, `staged_combustion.py` gives preburner/Pc 1.67 on the SSME vs 1.82 real
     (`ASSUMPTIONS.md`).
7. **Preburner injector dP at the maximum point**, derived from Fig. 17: **ox ~23 % of Pc,
   fuel ~12-14 % of Pc** `[Fig. 17 p.36]`.
   - The preburner-only flow balance at MR 0.65 shows a fuel injection velocity of 240.8 m/s
     `[Table 26 p.153]`.
   - That flow balance does not cleanly separate valve and injector drops, so no injector
     dP/Pc is taken from it.
8. **Liner coolant fraction.**
   - The design liner sleeve takes "only **2 %** of the preburner fuel flow" `[p.27]`.
   - The test flow balance shows sleeve coolant **0.136 kg/s plus face coolant 0.163 kg/s of
     2.757 kg/s total H2**, i.e. 4.9 % + 5.9 % (derived) `[Table 26 p.153]`.
   - Hence "core MR" 0.684 vs overall MR 0.650. Excluding both coolant streams gives about
     0.729 (derived).
9. **Preburner stability.**
   - The recessed coaxial element is "inherently stable", and a Priem analysis agreed.
   - Six L-shaped quarter-wave cavities with 11 % open area and 15.5 mm depth are tuned to
     the 1T mode at about **16,000 Hz** `[p.46; Figs 25-26]`.
   - Kistler data from the last two preburner tests showed 80-90 N/cm² p-p, **< 4 % of Pc**
     `[p.154]`.
   - The feed-system-coupled (chug) power-transmission factor is 0.41, "higher resistance to
     this instability mode than … the SSME units" `[leaf 78, p.~60]`.
10. **Life and structural criteria for the preburner.**
    - Service-free life of 60 thermal cycles or 2 h; 300 cycles or 10 h between overhauls
      `[p.7]`.
    - Safety factors of **1.1 on yield, 1.4 on ultimate, 4.0 on life**, with total creep
      limited to 1.0 % `[p.34 (leaf 50)]`.
    - Fatigue and creep damage are summed as 4φf + φc. The worst combustor point, 1078 K, has
      N_f 10,000, t_r 200 h and a damage sum of 0.32 `[Table 9 p.36]`.
    - Materials are Inconel 625 for H2-embrittlement resistance, 304L CRES posts, and NARloy-A
      or copper faceplates.
11. **Start/shutdown hazards specific to a fuel-rich preburner**, `[p.152, p.161]`:
    - Test 18 burned out the injector ox side. The ox-manifold helium purge was too low at
      the manifold despite a high regulator lockup, so GH2 backed up into the LOX side and
      ignited when the LOX valve opened.
    - A spurious electrical pulse later reopened the preburner LOX valve while fuel was
      decreasing. The resulting high-MR excursion burned off the duct thermocouples and the
      turbine-simulator orifices.
    - The fix was positive simultaneous LOX-valve shutoff and a relocated LOX bleed.
12. **Main chamber with hot preburner gas as fuel.**
    - η_c* ranged 98.5-99.7 % and Isp at eps 400 was **4665-4723 N·s/kg (475.7-481.6 s)**
      at Pc 15.4-15.8 MPa, MR 5.75-6.43 `[Table 42 p.253]`.
    - Chamber heat input was **~40 % higher** than the same-family chamber with ambient-GH2
      fuel (`CR-135221`).
    - Calculable effects account for part of that: contraction ratio 3.64 vs 4.02 and contour
      4.8 %, Pc and wall temperature 9.8 %, fuel injection velocity 3.2 % `[p.200; leaf 253]`.
    - The remaining ~18.6 % is attributed to hot-gas-injector effects: earlier or enhanced
      combustion and higher near-face turbulence, estimated at 10-30 %.
    - Chamber heat input was nearly independent of MR over 4.7-6.4 and ~7 % below the design
      value.

## Design method

The preburner element sizing logic is the SSME preburner practice, transferred:
- Low flow per element and close spacing.
- An LOX post recessed one sleeve-gap-scale distance, about 2.5 mm, with the H2 held at about
  213 m/s through the recess, so the LOX jet is fully atomized before the annular gas jet
  expands.
- A rounded-entrance ox control orifice meters the LOX. The post/sleeve annulus meters the H2.

The element is checked by:
- CICM (Coaxial Injection Combustion Model) vaporization length.
- A cold-flow mixing-uniformity correlation, Em vs (ρg/ρl)^(2/3)(Vg/Vl) `[p.19-24]`.

The liner gas-side h uses a pipe-flow (Dittus-Boelter-type) relation with a 20 % safety factor.
The coolant side uses McCarthy-Wolf `[leaf 49]`.

## Section map

- Report documentation page, foreword, contents, lists of figures/tables: leaves 1-10. Read.
- Summary: pp.(unnumbered), leaves 11-13. Read.
- Introduction, Table 1 (thrust-chamber conditions): p.1-3, leaves 14-15. Read.
- Discussion / Design and Analysis intro, Table 2: p.5-7, leaf 16. Read visually.
- Ignition systems (spark/torch GOX/GH2 igniters, Figs 2-5): p.7-13, leaves 17-24.
  **as-needed - not read (2026-10-18)**. Igniter hardware drawings.
- **Preburner injector (element design, CICM performance, Figs 8-11, Tables 3-4, thermal and
  structural Figs 12-14, Tables 5-6): p.14-27, leaves 25-42. Read.** Table 3 and Fig. 11 read
  visually; Figs 8-10 and 12-14 not viewed (results are quoted in the text).
- **Preburner combustor (liner, Figs 15-17, Tables 7-9, life method): p.27-37, leaves 42-53.
  Read.** Figs 16-17 and Tables 7, 9 read visually.
- Main injector (modified for hot-gas fuel, Table 10-11, Figs 18-23 mixing efficiency): p.37-45,
  leaves 53-61. **as-needed - not read (2026-10-18)**. Element parameters vs SSME main
  injector; mixing-efficiency correlation.
- Injector simulator; Combustion stability (Priem, acoustic cavity, feed-system analog model,
  stability maps, Tables 12-14 incl. ASE vs J-2S idle mode): p.46-61, leaves 62-79. Read in
  part (leaves 62, 78-79). Analog-model figures (leaves 63-77) not read.
- LOX control valves (ball valves, actuation): p.61-63, leaves 78-82. Skimmed.
- Combustion chamber, regen nozzle, 400:1 extension, staged-combustion system assembly and duct
  loads (mostly drawings, Table 15): p.64-98, leaves 83-142. **as-needed - not read
  (2026-10-18)**. Hardware drawings and duct load table.
- Hardware fabrication (parts list Table 16, main injector rework, preburner injector and
  combustor build, turbine/injector simulators, valves, nozzle): p.99-117, leaves 143-161. Read
  in part (leaves 150, 152). Brazing (PAL-7), proof test, orifice-plate rework.
- Test: plan, facility, diffuser/ejector, instrumentation (Tables 17-19): p.118-139, leaves
  162-189. **as-needed - not read (2026-10-18)**. Facility and instrumentation detail.
- Oxidizer valve tests (Tables 20-23): p.140-149, leaves 190-198. **as-needed - not read
  (2026-10-18)**. Valve leak/flow tests.
- **Preburner tests (Tables 24-27, Figs 99-102): p.150-154, leaves 199-206. Read.** Tables 26-27
  and Fig. 101 read visually.
- **Staged combustion assembly tests (Tables 28-29, Figs 103-111): p.154-166, leaves 207-214.
  Read.** Fig. 111 read visually.
- Staged combustion assembly with 400:1 nozzle (Tables 30-35, performance, boundary-layer
  rakes, nozzle wall pressures): p.166-193, leaves 214-241. Read in part (Table 42 summary
  only). Boundary-layer drag deficit about 2 %; method-of-characteristics wall pressures agree.
- **Preburner gas temperatures (Figs 128-131, Tables 36-37): p.194-199, leaves 242-247. Read.**
  Tables and Figs 129-130 read visually.
- Heat transfer (chamber/nozzle heat input, correlations, separated-flow nozzle extension,
  rib thermocouples, Figs 132-166, Tables 38-39): p.200-246, leaves 248-293. Read in part
  (leaves 248, 253). The rest is **as-needed - not read (2026-10-18)**: transient nozzle
  heat-sink h ratios and throat rib wall temperatures.
- **Program summary and conclusions, Tables 40-43: p.247-254, leaves 294-301. Read.**
- References: p.255, leaf 302. Read. Ref. 1 = CR-135221 (Advanced Thrust Chamber
  Technology), Ref. 10 = CR-121236 (ASE Preliminary Design); neither is in `literature/`.

## Caveats

- **Hydrogen only.** None of this transfers directly to LOX/RP-1 or LOX/CH4 fuel-rich
  preburners: there are no soot/coking findings and no cp/γ/molecular weight. It does nothing
  for the **ox-rich** preburner gap. The report gives **no gas composition, cp, γ or molecular
  weight**. Any such numbers must be computed (CEA/Cantera), not cited from here.
- **The MR basis is inconsistent between Table 27 and Figs 101/111 / Table 36.**
  - The same preburner-only tests plot at MRs ~0.06-0.10 higher in Figs 101/111 than Table 27
    lists. For example, test 031 is MR 0.781-0.828 in Table 27 but 0.922 in Tables 36-37.
  - Excluding the liner-sleeve and face-coolant H2 (Table 26 ratio 0.729/0.650 ≈ 1.12) would
    roughly explain it, but **the report does not say**.
  - Against Fig. 111's theoretical line, Table 27's late test-031 slices would sit on theory
    at Table 27's MRs and ~100 K under at the figure's MRs.
  - The staged-combustion tests (Tables 36-37, 42, and the Fig. 111 diamonds) share one
    consistent basis.
- Fig. 111's theoretical curve is for the test conditions (near-ambient GH2), not the 239 K
  design fuel. Its Pc and fuel temperature are not stated. Digitized values are ±10-15 K.
- Fig. 101's legend reads "3000 PSI" under 2275 N/cm², but the text and the test log say
  3300 psia. 2275 N/cm² = 3300 psi.
- Tests were short, 1-8 s for preburner-only. Many duct thermocouples were "not stabilized"
  (Table 37), and the main-injector-inlet single thermocouples are downstream of heat-absorbing
  ducting, so they are not averages.
- The test preburner/main-Pc ratio was set by orifice turbine simulators, and the orifices
  enlarged during the series, so it is not a turbine-power-balance datum.
- Printed-text typos: worst-case "1383 K (2030 R)" on p.27 should be ≈1128 K; Table 7 has
  "1129 K (2050 R)". SSME FPB flow in Table 3 is printed 0.204 kg/s (0.525 lb/s), and
  0.525 lb/s = 0.238 kg/s, so one of the two is wrong.
