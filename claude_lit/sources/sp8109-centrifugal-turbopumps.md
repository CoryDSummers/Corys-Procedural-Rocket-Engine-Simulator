# SP-8109 — Liquid Rocket Engine Centrifugal Flow Turbopumps

## Identity

- NASA SP-8109, *Liquid Rocket Engine Centrifugal Flow Turbopumps*, NASA Space Vehicle Design
  Criteria (Chemical Propulsion), December 1973.
- File: `literature/NASA SP-8109 - Liquid Rocket Engine Centrifugal Flow Turbopumps.pdf`
  (NTRS 19740020848; 124 PDF leaves).
- Fixed offset: **printed page N = PDF leaf N+12** (printed p.1 "INTRODUCTION" is leaf 13;
  corrected 2026-09-26, re-verified on leaves 13, 20, 29, 38, 54, 66, 77, 89, 99). The first
  pass of this note said +11, which was wrong. Printed-page cites were unaffected.
- The second copy `literature/sp8109.pdf` has a different scan offset. Cite printed pages.
- Tag: `[SP-8109]`.

## Character

Same monograph family and structure as `[SP-8120]`/`[SP-8107]`: a parallel §2 "State of the
Art" (narrative, p.3-59) and §3 "Design Criteria and Recommended Practices" (imperative
"shall"/"recommended", p.61-86), with matching subsection numbers (e.g. §2.2.1.2 Suction
Specific Speed ↔ §3.2.1.2).

Scope is specifically **centrifugal-flow** pump stages, as opposed to `[SP-8107]`'s system-level
whole-turbopump treatment. It covers impeller hydrodynamic and mechanical design,
housing/diffuser/volute design, and thrust-balance systems.

Real engines referenced throughout: Titan (LR-87/LR-91), Atlas, H-1, F-1, J-2/J-2S, X-8, NERVA,
M-1, and the Mark III/Mark 19/Mark 29 pump designations.

Structure:
- §1 Introduction (p.1-2)
- §2 State of the Art (p.3-59):
  - 2.1 Configuration Selection
  - 2.2 Pump Performance, incl. Speed/Critical Speed/Suction Specific Speed/Turbine Limits/
    Bearing-Seal Limits/Efficiency/Flow Range
  - 2.3 Impeller, incl. Hydrodynamic/Mechanical Design/Fabrication/Materials
  - 2.4 Housing, incl. Diffuser/Volute/Materials
  - 2.5 Thrust Balance System
- §3 Design Criteria (p.61-86, mirrors §2's subsection numbers)
- Appendix A Glossary (p.87-94), Appendix B Unit conversion (p.95-96), References (p.97-102)

**Nomenclature** `[App. A p.87-90; eq. 1-2 p.6; eq. 7 p.8]` (US units throughout):
- Ns = N·Q^½/H^¾ (rpm, gpm, ft)
- ψ = gH/u_t2² is the **actual** pump head over discharge-tip speed², not the Euler head.
- φ = c_m/u; δ = Dt1/Dt2; ν = inlet hub/tip.
- β2 is measured **from tangential**: 90° = radial blades; "backswept" = < 90°.
- The slip coefficient **M = c_u2∞/c_u2 ≥ 1**, the inverse of the usual slip factor σ.

## This note's extraction scope

- **First pass (2026-09-26 AM)**, read in full:
  - §2.2.1 Speed and its criteria mirror §3.2.1
  - §2.3 Impeller Hydrodynamic and Mechanical Design, incl. Table I
  - §3.2.2-3.2.3
- **Second pass (turbopump Round 2, 2026-09-26 PM)**, read in full from page renders (the text
  layer garbles every table and equation):
  - §2.3.1 again, with every figure digitized
  - §2.4 Housing (p.39-54) and §2.5 Thrust Balance (p.55-60)
  - §3.3 Impeller criteria (p.66-73), §3.4 Housing criteria (p.74-82), §3.5 Thrust Balance
    criteria (p.82-86)
  - §2.2.2-2.2.3 Efficiency/Flow Range
  - Glossary
- Not read: §2.1 in depth, §2.3.3-2.3.4 beyond the criteria, References.

## Key results — speed, suction, tip speed (first pass)

**Suction-specific-speed design limits** `[SP-8109 §3.2.1.2 p.63]`:
- "For a pump with an integral inducer, maximum suction specific speed of 40,000 for the inducer
  is recommended. Without an integral inducer, limit the Ss value to 12,000."
- NPSH margin: **NPSH ≥ 3·cm1²/2g** for low-vapor-pressure fluids (water, RP-1), **2.3·cm1²/2g**
  for LOX/LF2, and **1.3·cm1²/2g** for LH2.
- Used by `physics/inducer.py` (turbopump Round 1): K back-solved to 40,000; `Z_MIN`;
  `SS_NO_INDUCER`.

**Fig. 5 is NOT a fleet-Ss table.** The first pass of this note read "F-1 RP-1 ≈23,400, F-1 LOX
≈19,500, J-2 LOX ≈10,200, X-8 ≈11,000..." as corrected Ss values. Those numbers are the Fig. 5
legend's **impeller tip diameters Dt2 in inches** (23.4, 19.5, 10.2, 11.0). That paragraph and
its caveat are struck.
- The only Fig. 5 Ss is "Atlas sustainer RP-1, no inducer, Ss = 15000".
- The A/B/C bands are design Ss of 40000/20000/10000 with a coupled inducer and TSH = 0.
- Real Ss data for inducer pumps is in `[SP-8107 Table II]` (see `nasa-sp8107-turbopump-systems.md`).

**Critical speed practice** `[§2.2.1.1, §3.2.1.1 p.8-10, 63]`: two philosophies.
1. Keep all operating speeds below the first rigid-body critical (stiff bearings; the drawback
   named is "high bearing DN values").
2. Run above the first and second whirl criticals but below shaft bending (preloaded duplex ball
   bearings).

Both keep a **~20 % margin** to the nearest critical, and the criterion says the pump "shall not
operate continuously at a critical speed".

**Impeller tip-speed limits by material/fabrication** `[§2.3.2 p.37; §3.3.3 p.71-72]`:
- Shrouded cast LH2 impellers: 1400 fps (Inconel 718, or vacuum-melt/vacuum-cast Al).
- Open-face Ti-5Al-2.5Sn: 2500 fps in LH2.
- Shrouded diffusion-bonded Ti: 2870 fps (room-temperature spin only).
- Dense-fluid shrouded impellers are cast, < 1000 fps.
- Casting is preferred below 1400 fps. Shrouded impellers to 2200 fps are machined or
  diffusion-bonded Ti.
- **Open-face impellers above 2200 fps** `[§3.3.1.4 p.67-68]`.

**Mechanical losses** `[§2.2 p.8]`: η = η_h·η_v·η_m (eq. 3-6). Seal and bearing power is
negligible for impellers ≥ 10 in. and **up to 20 % of shaft power for impellers as small as
1.0 in.**

## Key results — impeller hydrodynamic design (Round 2 pass)

**Table I, impeller geometry and pump performance** `[SP-8109 Table I p.26]`:
- Columns are exactly as printed, except the derived b2/Dt2.
- The table has no flow, head, rpm, ψ or propellant columns.

| Pump | β2° | Z2 | Dt2 in | b2 in | *b2/Dt2* | BEP Ns | best η |
|---|---|---|---|---|---|---|---|
| Titan 87-5 fuel | 35 | 12 | 10.75 | 0.74 | .069 | 1130 | .72 |
| 87-5 oxidizer | 28 | 9 | 9.42 | 1.00 | .106 | 1860 | .75 |
| 91-5 fuel | 28 | 8 | 4.93 | 0.44 | .089 | 1750 | .74 |
| 91-5 fuel (exptl) | 28 | 9 | 4.75 | .48 | .101 | 1590 | .68 |
| 91-5 oxidizer | 35 | 12 | 8.75 | .53 | .061 | 945 | .62 |
| 87-3 fuel | 22.5 | 8 | 10.99 | .67 | .061 | 980 | .55 |
| 87-3 oxidizer | 22.5 | 8 | 9.87 | .94 | .095 | 1650 | .65 |
| 91-3 fuel | 22.5 | 6 | 4.35 | .40 | .092 | 1864 | .60 |
| 91-3 oxidizer | 22.5 | 8 | 8.33 | .64 | .077 | 1169 | .65 |
| Titan IIA fuel | 28 | 9 | 6.97 | .48 | .069 | 1440 | .68 |
| NERVA Mk III Mod III | 90 | 18 | 12.25 | .49 | .040 | 914 | .65 |
| NERVA Mk III Mod IV | 90 | 48 | 12.25 | .49 | .040 | 960 | .70 |
| NERVA Mk III Mod IV | 90 | 24 | 12.25 | .49 | .040 | 1000 | .70 |
| M-1 oxygen | 35 | 12 | 10.70 | .81 | .076 | 1125 | .66 |
| Atlas/H-1 Mark 3 fuel | 25 | 10 | 14.25 | .85 | .060 | 760 | .72 |
| F-1 Mark 10 oxidizer | 25 | 6 | 19.5 | 2.7 | .138 | 2140 | .74 |
| F-1 Mark 10 fuel | 25 | 6 | 23.4 | 1.7 | .073 | 1200 | .76 |
| J-2 Mark 15-O oxygen | 25 | 6 | 10.2 | 0.74 | .073 | 1600 | .81 |
| X-8 Mark 19 hydrogen | 90 | 24 | 11.0 | .43 | .039 | 670 | .67 |
| J-2S Mark 29-F hydrogen | 60 | 24 | 11.5 | .53 | .046 | 1000 | .76 |

**Design ψ/φ2 for the same pumps:**
- **Fig. 13 legend** `[p.24]`, as φ2d / ψd / Z2 / β2 / δ:
  - X-8 LH2: .0752 / .703 / 24 / 90 / .47
  - J-2 LOX: .104 / .448 / 6 / 25 / .66
  - F-1 LOX (experimental 12-blade): .125 / .487 / 12 / 35 / .81
  - H-1 RP-1: .048 / .613 / 10 / 25 / .44
  - H-1 LOX: .082 / .56 / 10 / 35 / .58
  - 350K LH2: .094 / .52 / 24 / 25 / .66
- **Fig. 5 legend** `[p.16]`, as Dt2 in / ψ / η:
  - X-8 11.0 / .703 / .666
  - Atlas booster RP-1 14.25 / .613 / .720
  - Atlas booster LOX 11.0 / .596 / .785
  - Atlas sustainer RP-1 (no inducer, Ss 15000) 8.60 / .589 / .700
  - Atlas sustainer LOX 7.7 / .560 / .670
  - F-1 RP-1 23.4 / .563 / .760
  - F-1 LOX 19.5 / .487 / .745
  - J-2 LOX 10.2 / .448 / .815
- F-1 LOX: doubling discharge blades 6 → 12 raised BEP ψ 0.42 → 0.49 with a slight η gain
  `[p.23]`.

**Slip, eq. 17** `[§2.3.1.3 p.31]`. SP-8109's own empirical correlation. It does **not** use
Wiesner; Busemann, Pfleiderer, Stanitz and Stodola are named as "widely accepted".

```
M = 1 + (1.37 + 0.23 sin β2)(φ2 + 0.05)^0.6 / [0.5 Z2 X_L^0.6 (1 + X_L/2)(1 − 0.12 δ)]
X_L = axial distance, impeller-inlet midpoint to discharge / discharge diameter
```

- With zero prewhirl, the Euler head gives ψ = η_h·(1 − φ2·cot β2)/M. This is the standard Euler
  form; SP-8109 names M and η_h but does not print this line.
- **Fig. 16** (the minimum-blade-number carpet, shrouded, δ = 0.65, zero prewhirl) is reproduced
  by eq. 17 with **X_L ≈ 0.25, η_h ≈ 0.82**. At β2 ≤ 45° the fit is within about −0.02/+0.00
  in ψ. At 90° it over-predicts by 0.014-0.034. These two values were fitted by the Round 2
  extraction, not printed.

**Fig. 16, digitized** `[p.30]`. BEP (φ2, ψ) at each (Z2, β2) node; ~, ±0.004 φ2, ±0.008 ψ.

| Z2 \ β2 | 20° | 25° | 30° | 35° | 40° | 45° | 60° | 90° |
|---|---|---|---|---|---|---|---|---|
| 3 | .097,.350 | .135,.321 | .170,.302 | – | – | ~.294,~.260 | – | – |
| 4 | .087,.418 | .120,.391 | .155,.371 | – | – | .272,.324 | – | – |
| 5 | .080,.467 | .109,.442 | .142,.422 | ~.179,~.404 | – | .253,.377 | – | – |
| 6 | .074,.502 | .101,.477 | .133,.457 | .169,.441 | – | .237,.419 | – | – |
| 8 | .062,.567 | .087,.539 | .115,.522 | .146,.511 | – | .208,.491 | – | – |
| 10 | .056,.594 | – | – | – | – | – | .270,.522 | – |
| 12 | .050,.624 | .066,.616 | .089,.605 | .112,.597 | .138,.590 | – | .250,.565 | – |
| 16 | .039,.666 | – | – | – | – | – | .203,.634 | – |
| 20 | .032,.690 | .047,.682 | .065,.677 | .080,.673 | .101,.670 | .120,.668 | .173,.667 | .251,.685 |
| 24 | – | – | – | .069,.697 | – | – | – | .219,.706 |
| 36 | – | – | – | .054,.730 | – | – | – | .157,.738 |
| 48 | – | – | – | .048,.743 | – | – | – | .136,.744 |

- Criterion: Z2 **≥** the Fig. 16 value for the design φ2 `[§3.3.1.2-3 p.66-67]`.
- Along a β2 line, ψ rises with Z2 and φ2 falls.

**Ranges and rules:**
- ψ runs 0.35 to > 0.70.
  - Low ψ (≈0.35) comes with 3-5 blades; high ψ (> 0.70) needs 20-60 blades `[§2.3.1.2 p.28]`.
  - High ψ suits low-Ns pumps; low ψ is accepted at high Ns for flow range.
- φ1 and φ2 run 0.05-0.30. φ2 is set by β2 (stress-limited) and the desired ψ `[p.28]`.
- c_m2 = **1-1.5 × c_m1** `[§3.3.1.2 p.66]`.
- ψ ≤ 0.5 with a vaned diffuser gives rising head to the lowest flow `[§3.2.3.1 p.65]`.
- Blade and fabrication limits:
  - **4-8 inlet blades**, with splitters added at the discharge as needed for ψ.
  - Inlet free area > 80 % of the annulus, exit > 85 % `[§3.3.1.3 p.67]`.
  - Machinable blade count ≤ **28·sin β2** `[§3.3.3 p.72]`.
  - Shrouded machined impellers need stage **Ns > 1000 and Dt2/b2 < 20** `[p.72]`.
  - Table I fleet b2/Dt2 is 0.039-0.138: dense-fluid pumps 0.06-0.14, LH2/NERVA 0.039-0.046.
- δ = Dt1/Dt2: higher δ (for higher Ss) costs η. At Ns 1500, Ss 10000 → δ 0.45 and Ss 40000 →
  δ 0.70 `[Fig. 8 p.19]`.
- Suction eq. 14: S's = (8147/φ1)·(NPSH/(c_m1²/2g))^(−3/4) `[p.27]`.
- Loading `[§3.3.1.3 p.67]`:
  - Suction-surface velocity gradient **G ≤ 3.5** (eq. 15).
  - Pressure-surface velocity > 0.
  - Over the first 20 % of the meridional length, W_s ≤ **1.2 × W1**.
  - **No de Haller W2/W1 limit is stated.**
- β2 choice `[§3.3.1.3 p.67]`: the H-Q curve must fall with rising flow. The zero-slope point
  must be ≥ **10 %**, and stall ≥ **15 %**, below the lowest required flow.
  - Backswept low-ψ impellers have wider, more stable range than radial ones `[p.29]`.
  - Many blades (M → 1) give the steepest slope.
- Measured shutoff ratios `[Fig. 13 p.24]`: backswept low-ψ pumps rise to shutoff at ψ/ψd
  ≈ **1.1-1.3** (F-1 LOX ~1.30, J-2 LOX ~1.21-1.27, H-1 ~1.10-1.12, 350K LH2 steepest). The
  radial high-ψ X-8 and NERVA curves **droop** (~0.86-0.93 at low flow).
- Off-design η/η_d `[Fig. 13]`: ≈0.25 at φ/φd 0.12, ≈0.45-0.5 at 0.25, ≈0.65-0.7 at 0.4,
  ≈0.82-0.85 at 0.55, flat 0.85-1.05. After that it falls, fastest for LH2.

**Size and Ss efficiency effects:**
- **Fig. 6** `[p.17]`: stage η vs stage Ns by Dt2 (ref. 48; ~, ±1 pt). Criterion: use it for
  preliminary size effects `[§3.2.2.1 p.64]`.

  | Dt2 | Ns 800 | 1000 | 1200 | 1600 | 2000 |
  |---|---|---|---|---|---|
  | 10 in | 68 | 73.5 | 77 | 80 | 81.5 |
  | 8 in | 67 | 73 | 75 | 78.5 | 79.5 |
  | 6 in | 62.5 | 68.5 | 71 | 74.5 | 76 |
  | 4 in | 57.5 | 63 | 66.5 | 69 | 69.5 |
  | 2 in | 53 | 58.5 | 61.5 | 64 | 64 |
  | 1 in | 50 | 55.5 | 57.5 | 60.5 | 60.5 |

- **Fig. 9** `[p.19]`: efficiency penalty (points) vs design Ss (water), from 10,000 to 60,000.
  Lines are straight in log Ss.
  - Ns 500: 0.05 → 1.3
  - Ns 1000: 0.2 → 2.6
  - Ns 2000: 0.4 → 5.1
  - Ns 3000: 1.0 → 7.6
  - Ns 4000: 1.3 → 10.0
- **Open vs shrouded** `[Fig. 21 p.35]`: each 1 % of blade-height tip clearance costs ~3 % η and
  ~3.5-4 % head relative to a shrouded impeller.
  - Shrouded is recommended except above 2200 fps `[§3.3.1.4]`.
  - Oxidizer pumps are less efficient than fuel pumps of the same size and Ns because of larger
    clearances `[p.15]`.
- **LH2** `[p.17-18]`: of the J-2S LH2 pump's η drop with speed, ~30 % is pressure-induced
  clearance change and the rest is heating by hot leakage recirculation. Criterion: evaluate LH2
  with enthalpy/entropy tables `[§3.2.2.1 p.64]`.

## Key results — housing, diffuser, volute, leakage (Round 2 pass)

**Volute** `[§2.4.1.3 p.47; §3.4.1.3 p.76]`:
- The goal is constant impeller-discharge static pressure around the wrap (minimum radial load).
- Constant moment of momentum (c_u·r = const) with a friction correction is the criterion
  (J-2S Mark 29 fuel pump; Titan).
- Constant mean velocity is a simplification: slightly different η, higher radial load.
- Asymmetric cross-section (one stable vortex); a circular section for structure.
- Exit cone included angle: **7-9° circular, 6° square, 11° two parallel walls**.
- Tongue: zero incidence at design flow.
- Vaned diffuser to tongue: radius ratio **> 1.05**, or virtually touching (otherwise bi-stable
  discharge pressure).
- **No volute velocity ratio, loss coefficient or volute OD/D2 is given.**

**Vaned diffuser** `[§2.4.1.2.2 p.42-46; §3.4.1.2.2 p.74-75]`:
- Use it when **ψ > 0.5, Ns < 1000** (§2 says Ns < 1500), or for maximum η / low weight.
- **+3 % η at Ns 1200**, more at lower Ns (ref. 4).
- η stays higher at low flow but falls faster above BEP.
- Diffuser stall at 45-50 % of BEP flow on low-Ns radial impellers.
- Vane width b3 = **0.9-1.0 b_t2** (eq. 19).
- Vane count is the prime nearest the impeller blade count, with no wave reinforcement
  (eq. 20/21).
- Throat velocity by conservation of momentum (Fig. 25, c_throat/c2 vs α2):
  - 10° → ~0.79, 20° → ~0.63, 30° → ~0.55, 40° → ~0.48.
- Diffusion factor **D ≤ 0.6** per stage (eq. 18); **R4/R3 ≤ 1.4** per vane ring; cone
  7-10°.
- Vaneless-only diffusers "result in the lowest efficiency and generally are not used"
  `[§2.2.2.2 p.20]`.

**Vaneless gap** `[Fig. 24 p.42]`: (D3−D2)/D2 vs α2.
- ~0.035 at 5°, ~0.07 at 10°, ~0.115 at 15°, ~0.195 at 20°.
- NERVA: a gap of 0.03 → 0.06 D gave +1.8 % η at Ns 980.

**Real diffuser types** `[Fig. 6 table p.17]`:
- Volute only: J-2 LOX, Redstone, Atlas sustainer RP-1.
- Vaneless + volute: Atlas sustainer LOX, XLR-129 (open face).
- Vaned + volute: H-1 LOX & RP-1, X-8.
- Vaned-diffuser pumps sit **above** their size curve; vaneless ones on or below it.

**Wear-ring leakage** `[§2.3.1.4 p.34; Fig. 22 p.36]`:
- Seal clearance **0.0005·Dt2** gives about **95 %** of zero-clearance η for the J-2 LOX pump at
  Ns 1500.
- Leak model: Q_L = K·(π·RC·D)·√(2g·Δh).
  - K ≈ 0.25-0.30 for stepped labyrinths.
  - K ≈ 0.4-0.7 for grooved seals (rising with clearance).
- Return holes ≈ 4 × the clearance area `[§3.5.2.1 p.84]`.
- **No leakage-%-of-flow value, disk-friction coefficient or radial-thrust K appears anywhere in
  SP-8109.** See `[Huzel]` §6.3 for leakage and volute-loss fractions.

**Housing structure** `[Table III p.52; §3.4.2 p.77]`:
- Yield FS ≥ 1.1, ultimate FS ≥ 1.4, burst 1.5 × limit pressure, proof ≥ 1.2.
- LCF life 4×, HCF 10×.
- Housings are "the major segment of pump weight".
- Materials are in Table IV. **No titanium in LOX.**

## Design method

SP-8109 gives real design criteria, fleet data and one slip correlation rather than a
closed-form meanline. Its directly usable numbers:
- the 40,000/12,000 Ss limits and 3.0/2.3/1.3 NPSH margins
- eq. 17 slip with the Fig. 16 blade carpet
- the Fig. 6 size-effect and Fig. 9 Ss-penalty curves
- the 0.0005·D seal clearance and Q_L model
- the fabrication limits (28 sin β2, Dt2/b2 < 20, 4-8 inlet blades)
- the vaned-diffuser selection rule and its +3 % gain
- the H-Q stability margins (10 %/15 %)

`[Huzel]` §6.3 supplies the worked step-by-step design method that complements these.

## Section map (printed pages; leaf = page + 12)

- §1 Introduction p.1-2. §2.1 Configuration Selection p.3-6 (skimmed).
- **§2.2.1 Speed p.6-14; §2.2.2 Efficiency, §2.2.3 Flow Range p.14-24: read.**
- **§2.3 Impeller (2.3.1 hydrodynamic incl. Table I p.26, Fig. 16 p.30, eq. 17 p.31; 2.3.2
  mechanical) p.25-38: read.** §2.3.3-2.3.4 Fabrication/Materials p.38-40 (via §3.3.3-3.3.4).
- **§2.4 Housing p.39-54: read** (casing, vaneless/vaned diffuser, interstage, volute,
  structure, materials).
- **§2.5 Thrust Balance p.55-60: read.**
- **§3.2 p.62-65; §3.3 Impeller p.66-73; §3.4 Housing p.74-82; §3.5 Thrust Balance p.82-86:
  read.**
- Appendix A Glossary p.87-90: read. References p.97-102: not read.

## Caveats

- **Figure readings are by eye** from 150-400 dpi renders (marked ~ where it matters).
  - Fig. 16 is ±0.004 φ2, ±0.008 ψ. Its Z2 = 60 and Z2 = 3 at 45° nodes are least certain.
  - Figs. 24-26 were pixel-traced.
- **Eq. 17 has no stated validity range, X_L or η_h.** The X_L 0.25 / η_h 0.82 fit to Fig. 16
  is the Round 2 extraction's own.
- The Fig. 13 line-style mapping for X-8 vs J-2 LOX is probable, not certain.
- The Ns threshold for vaned diffusers is inconsistent: 1000 (§3) vs 1500 (§2).
- 1973 vintage. The real examples are 1960s/early-70s hardware, pre-SSME.
- **Not in SP-8109:** Wiesner slip, a de Haller limit, disk-friction or volumetric-loss formulas,
  volute loss coefficients, housing OD/D2, and SSME/RL10/M-1 housing dimensions.
