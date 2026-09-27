# SP-8110 — Liquid Rocket Engine Turbines

## Identity

NASA SP-8110, *Liquid Rocket Engine Turbines*, NASA Space Vehicle Design Criteria (Chemical
Propulsion), January 1974. Written by S. B. Macaluso (Rocketdyne), edited by R. B. Keller Jr.
(Lewis). `literature/NASA SP-8110 - Liquid Rocket Engine Turbines.pdf` (NTRS 19740026132;
160 PDF leaves; fixed offset: **printed page N = PDF leaf N+12**, e.g. printed p.1
"INTRODUCTION" is leaf 13, Table I on printed p.10 is leaf 22). Tag: `[SP-8110]`.

## Character

Same monograph family and layout as `[SP-8107]`/`[SP-8109]`/`[SP-8120]`: §2 "State of the
Art" (narrative, p.3-77) and §3 "Design Criteria and Recommended Practices" (p.79-122) use
matching subsection numbers (§2.1.4 Staging ↔ §3.1.4). Scope is **axial-flow** turbines for
rocket turbomachinery only: preliminary design (pressure ratio, U/C0, staging),
aerothermodynamic point design (the Emmert loss-coefficient procedure the F-1 and J-2
turbines were designed with), blade geometry, and mechanical/structural design (blades,
disks, shafts, casings, rotordynamics). It is written from Rocketdyne experience. Turbine
designations are Rocketdyne "Mark" numbers: Mark 3 = H-1, Mark 4 = Atlas sustainer,
Mark 10 = F-1, Mark 15-F/-O = J-2 fuel/ox, Mark 29 = J-2S/J-2X, Mark 25 = NERVA. RL10 A3-3
and Agena LR81 are also covered. It predates the SSME (the SSME is mentioned only as "next
generation"), so it contains **no SSME HPFTP/HPOTP data**. It also has no Titan
LR87/LR91 turbine data.

Structure: §1 Introduction (p.1-2); §2.1 Preliminary Design (p.13-18: engine performance vs
PR/flow, gas properties, isentropic velocity ratio, staging); §2.2 Aerothermodynamic Point
Design (p.19-29: energy balance, partial admission, stage reaction, intake manifold); §2.3
Nozzle/Vane/Blade Geometry (p.29-43); §2.4 Mechanical Design & Structural Analysis
(p.43-71: blading, nozzle, stator, rotor/disk/shaft/fasteners, casing/manifold); §2.5
Integration (p.71-77: rotordynamics, bearings/seals, exhaust ducts, problem areas); §2.6-2.7
Materials/Instrumentation (p.77); §3 Design Criteria (p.79-122, mirrors §2); App. A Glossary
(p.123-135); App. B units (p.137); References (p.139-142).

## This note's extraction scope

Read in full, with tables and figures rendered to PNG and read visually (the text layer
garbles every table): §1; §2.1 all, including **Table I** (fleet turbine design data,
p.10), Table II (materials, p.11), Table III (gas properties, p.16), and Figs 13/14 (η vs
U/C0, p.17; digitized by pixel scan); §2.2 all (Figs 16-20, eqs 1-15); §2.3.8 shrouding/
clearance (Table V, Fig 29); §2.4.1 blading mechanical design (Fig 30 AaN², eq 20-27,
Figs 33-34); §2.4.4 disk/shaft/fasteners (Fig 38, eqs 30-37); §2.4.5 casing configuration
by pressure class; §2.5 rotordynamics/exhaust ducts; Table VI (materials problems, p.78);
§3.1-3.2 all, including Figs 51-57 and worked example Tables VII/VIII; §3.3.5-3.3.8;
§3.4-3.6 (design-criteria numbers). Skimmed only: §2.3.1-2.3.7 and §3.3.1-3.3.4 (blade
profile construction: circular-arc/parabolic layouts, Zweifel, O/p, exit deviation, Figs
21-28). Not read: App. A-B, References.

## Real turbine data — Table I `[SP-8110 Table I p.10]`

All efficiencies are **total-to-static, η_t(T-S)**. VC = velocity-compounded, PC =
pressure-compounded. "Stages" = rotors on the shaft; a 2-row VC is 1 stage with 2 rotor
rows.

| Engine | Mark | Status | Type | Stg | hp | rpm | Dm in | Fluid | U ft/s | Tt1 °F | Pt1 psia | PR | U/C0 | η % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Redstone | 2 | former prod | 2-row VC | 1 | 793 | 4 840 | 20.00 | H2O2 | 423 | 680 | 390 | 22 | – | 39.0 |
| **H-1** | 3 | prod | **PC** | 2 | 4 007 | 32 800 | 9.00 | LOX/RP-1 | 1290 | 1200 | 600 | 17.7 | 0.42 | **62.5** |
| Atlas sustainer | 4 | prod | PC | 2 | 1 680 | 38 000 | 6.00 | LOX/RP-1 | 995 | 1075 | 760 | 25 | 0.39 | 46.3 |
| AR (aircraft rkt) | 5 | former prod | impulse | 1 | 209 | 27 000 | 7.64 | H2O2 | 878 | 1364 | 480 | 22 | – | – |
| E-1 | 6 | former dev | 2-row VC | 1 | 14 860 | 8 900 | 22.06 | LOX/RP-1 | 857 | 1400 | 650 | 25 | 0.20 | 62.0 |
| Nuclear | 9 | former prod | PC | 6 | 11 500 | 32 800 | 7.90 | GH2 | 1132 | 60 | 800 | 15.2 | – | – |
| **F-1** | 10 | prod | **2-row VC** | 1 | 54 359 | 5 490 | 34.90 | LOX/RP-1 | 840 | 1550 | 929 | 16.3 | 0.20 | **60.5** |
| H-2 | 14 | former dev | 2-row VC | 1 | 7 650 | 14 300 | 16.07 | LOX/RP-1 | 1000 | 1700 | 525 | 11.5 | 0.21 | 58.9 |
| **J-2 ox** | 15-O | prod | 2-row VC | 1 | 2 604 | 8 650 | 15.50 | LOX/LH2 | 585 | 740 | 62 | 3.16 | 0.11 | **48.4** |
| **J-2 fuel** | 15-F | prod | 2-row VC | 1 | 8 749 | 26 052 | 12.50 | LOX/LH2 | 1448 | 1200 | 620 | 6.35 | 0.18 | **60.1** |
| X-8 ox | 19-O | former dev | impulse | 1 | 750 | 32 800 | 6.00 | LOX/LH2 | 860 | 1200 | 450 | 9.0 | – | – |
| X-8 fuel | 19-F | former dev | PC | 2 | 4 000 | 27 000 | 9.00 | LOX/LH2 | 1160 | 1200 | 410 | 16.4 | – | – |
| NERVA | 25 | former prod | PC | 5 | 21 000 | 34 000 | 7.97 | GH2 | 1180 | 60 | 1000 | 10 | – | 79.0 |
| J-2X | 29-F | former dev | 2-row VC | 1 | 12 700 | 28 050 | 12.50 | LOX/LH2 | 1535 | 1050 | 920 | 7 | – | – |
| J-2S fuel | 29-F | former dev | 2-row VC | 1 | 10 810 | 28 000 | 10.5 | LOX/LH2 | 1288 | 1200 | 889 | 7.30 | – | 46.0 |
| J-2S ox | 29-O | former dev | 2-row VC | 1 | 3 263 | 9 050 | 15.5 | LOX/LH2 | 613 | 740 | 100 | 2.68 | – | 56.1 |
| M-1 ox | M-1 | former dev | 2-row VC | 1 | 24 665 | 3 530 | 33.0 | LOX/LH2 | 508 | 763 | 194 | 1.62 | 0.13 | 54.0 |
| M-1 fuel | M-1 | former dev | 2-row VC | 1 | 74 138 | 12 961 | 23.18 | LOX/LH2 | 1310 | 1000 | 904 | 3.87 | 0.19 | 65.0 |
| **RL10** | A3-3 | prod | **PC** | 2 | 660 | 28 670 | 5.90 | GH2 | 738 | −88 | 708 | 1.42 | 0.35 | **74.0** |
| Agena | LR81-BA-11 | prod | impulse, partial adm. | 1 | 365 | 24 800 | 7.89 | IRFNA/UDMH | 855 | 1400 | 475 | 37.7 | 0.18 | 41.0 |

Other hardware facts from the text:
- **F-1**: "two-row velocity-compounded … 60 000 horsepower at a design speed of 5600 rpm"
  for the 30-in-pitch-diameter alternate Mark 10 `[§1 p.1; §2 p.9]`. The production turbine
  is 56 000 hp `[§2.4.5.1 p.68]`, Dm 34.9 in (Table II lists 35-in and 30-in versions). It has
  shrouded impulse blades on fir-tree roots, curvic couplings, a Rene 41 nozzle, alloy 713C
  blades and Inconel 718/Rene 41 disks `[p.3, Table II]`.
- **H-1 Mark 3**: 2-stage PC with rotor blades welded to the disks. Also used on Thor,
  Jupiter and the Atlas booster. It drives both pumps through a **4.83:1 gearbox**
  `[§2 p.3]`.
- **J-2**: the fuel and ox turbines are **series-installed on two shafts**. The Mark 15-F
  exhaust is the Mark 15-O working fluid `[p.3, 9]`.
- **RL10 A3-3**: 2-stage, fully shrouded, labyrinth-sealed, with an aluminium case and
  integral disk/blades. Exit guide vanes cut discharge-whirl loss `[p.9]`.
- **Agena LR81-BA-11**: single-row, partial admission, 1400 °F IRFNA/UDMH `[p.9]`.

**Blade-row geometry** `[SP-8110 Table IV p.31]` (Dm = pitch dia, Z = vane/blade count,
H = height, b = axial width, all in inches; dual values are entrance/exit):

| Turbine | Dm | Nozzle Z/H/b | 1st rotor Z/H/b | Stator Z/H/b | 2nd rotor Z/H/b |
|---|---|---|---|---|---|
| Mark 10 (F-1) | 34.90 | 61 / 1.55 / 3.00 | 119 / 1.862-2.484 / 1.50 | 130 / 2.604-3.372 / 1.50 | 109 / 3.683-4.223 / 1.50 |
| Mark 15-F (J-2 fuel) | 12.50 | 43 / 0.42 / 0.700 | 97 / 0.53 / 0.596 | 115 / 0.640-0.770 / 0.596 | 93 / 0.88 / 0.585 |
| M-1 fuel | 23.00 | 37 / 1.492 / 2.175 | 80 / 1.741 / 1.350 | 67 / 1.931-2.309 / 1.360 | 78 / 2.683 / 1.500 |

**Clearances** `[SP-8110 Table V p.42]`:

| Turbine | Row | Axial clearance (in) | Axial (% chord) | Tip clearance (in) | Tip (% blade height) |
|---|---|---|---|---|---|
| F-1 | 1st rotor | 0.476 | 32 | 0.030 | 0.7 |
| F-1 | 2nd rotor | 0.342 | 23 | – | – |
| J-2 ox | 1st rotor | 0.150 | 20 | 0.010 | 0.8 |
| J-2 ox | 2nd rotor | 0.150 | 20 | 0.012 | 0.7 |
| J-2 fuel | 1st rotor | 0.100 | 17 | 0.0075 | 1.4 |
| J-2 fuel | 2nd rotor | 0.090 | 15 | 0.008 | 0.9 |

**Working-fluid (frozen) properties** `[SP-8110 Table III p.16]`. The monograph says these
are "reference data only".

| Fluid | Source Pc (psi) | Tt1 °F → γ / cp (Btu/lb·°R) / R (ft·lbf/lbm·°R) |
|---|---|---|
| LOX/RP-1 | 1000 | 1100: 1.097/0.635/44; 1300: 1.115/0.648/52; 1500: 1.132/0.656/59; 1600: 1.140/0.660/63; 1700: 1.148/0.662/67 |
| LOX/LH2 | 1500 | 1000: 1.374/1.998/423; 1200: 1.364/1.910/396; 1500: 1.348/1.802/362; 1700: 1.337/1.738/341; 1900: 1.326/1.687/323 |
| LF2/LH2 | 750 | 900-1700: γ 1.395-1.366, cp 2.765-2.192, R 626-457 |
| FLOX/CH4 | 750 | 1300-2100: γ 1.176-1.242, cp 0.857-0.791, R 100-117 |
| Hydrogen | – | 700-1100: γ 1.396-1.388, cp 3.48-3.53, R 766 |
| N2O4/A-50 | 1500 | 1700-1850: γ 1.248-1.260, cp 0.726-0.694, R 112-111 |

The LOX/RP-1 R of 44-67 corresponds to MW ≈ 23-35. That is heavier than a simple
equilibrium fuel-rich mix, so it presumably reflects frozen heavy-hydrocarbon products.
The values are internally consistent (γ = cp/(cp − R/J)).

My own consistency check (not the source's) using these properties with
C0 = √(2·g·J·Δhs), Δhs = cp·T·[1 − PR^−(γ−1)/γ]:
- **F-1** (1500-1600 °F, PR 16.3): C0 ≈ 4230-4390 ft/s, so U/C0 = 840/C0 ≈ **0.19-0.20**.
  Matches Table I.
- **J-2 fuel** (1200 °F, PR 6.35): C0 ≈ 7860 ft/s, so U/C0 ≈ **0.184**. Matches.
- **H-1** (1200 °F, PR 17.7): C0 ≈ 3580 ft/s, so the single-stage U/C0 = 0.36. The
  multistage convention √(ΣU²)/C0 (below) gives 0.51. Table I's 0.42 matches neither, so
  treat the H-1 U/C0 as ±0.07.

## Key results

**1. Velocity-ratio definition** `[SP-8110 §2.1.3 p.15]`: U/C0 = pitchline velocity /
isentropic spouting velocity. For a **multistage turbine, U = √(ΣU_i²)** over the stages. So
pressure-compounding N equal-diameter stages raises the effective U/C0 by √N at fixed
blade speed. That is the whole point of pressure compounding.

**2. Staging-selection rules (design criteria)** `[SP-8110 §3.1.4 p.83]`, quoted:
- "Reaction staging should be specified for design isentropic velocity ratios **above
  0.45**."
- "**two-row velocity-compounded** impulse staging is recommended for a design velocity
  ratio between **0.20 and 0.30**."
- "A **single-row impulse** stage delivers best performance at velocity ratios between
  **0.30 and 0.40**."
- "For design velocity ratios **below 0.15**, estimated incremental gains of **10 and 23
  points** in overall turbine efficiency can be realized by adding one and two rows,
  respectively, to a single-row design."
- When the spouting velocity forces a sub-optimal U/C0 because stress caps U: "developing
  turbine design power with the **highest allowable pitchline velocity and least number of
  turbine stages**."

Supporting statements from §2.1.3-2.1.4 `[p.15-18]`:
- Impulse staging is normal below U/C0 0.35 at supersonic (high) PR.
- Reaction staging is for PR < 2 and U/C0 > 0.45.
- **GG and tap-off two-row designs run at U/C0 0.10-0.40, with η 35-65%.**
  **Staged-combustion and expander turbines can exceed 80%** because low PR allows a better
  U/C0.
- **Pitchline velocities of current designs are 1000-1500 ft/s**, with inlet temperatures of
  1000-1500 °F for LOX/RP-1 and LOX/LH2. Turbines have run **uncooled at 1700 °F**.
- Production turbines have been limited to 1- and 2-row machines for size and weight.
  Three or more rotors need outboard bearings. Five- and six-stage nuclear hydrogen
  turbines exist (Mark 25/Mark 9).

Other cycle-level criteria:
- `[§3.1.1 p.79/82]`: GG turbines should be designed for **minimum mass flow**; staged-
  combustion turbines for the **lowest PR**. If stress or size caps U on a high-PR GG
  turbine, **evaluate series turbines on dual shafts**: splitting the PR lowers each
  turbine's C0 and raises U/C0 (the J-2 solution).
- For low-PR staged-combustion turbines, **use reaction designs with 35-50% reaction**.

**3. η vs U/C0 by staging type** `[SP-8110 Fig. 13 p.17]` ("typical curves", log-log,
turbine stage η_t(T-S) in %, digitized by pixel scan):

| U/C0 | 0.05 | 0.07 | 0.10 | 0.12 | 0.14 | 0.16 | 0.18 | 0.20 | 0.22 | 0.25 | 0.30 | 0.35 | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3-row impulse | 30 | 40 | 50 | 53 | **54** | 49 | 44 | (ends ≈0.19, 40) | | | | | | | | | |
| 2-row impulse (VC) | 24 | 31 | 43 | 49 | 54 | 59 | 63 | 66 | **69** | 68 | ≈60 (ends ≈0.28) | | | | | | |
| 1-row impulse | 16 | 21 | 30 | 36 | 41 | 46 | 51 | 55 | 59 | 64 | 73 | 78 | **80** | (falls; ends ≈0.55) | | | |
| Reaction | | | | | | | | | | 54 (start) | 62 | 69 | 74 | 84 | 90 | 95 | **95** |

Peaks are about 54% at 0.13 (3-row), 69% at 0.23 (2-row VC), 80% at 0.42 (1-row) and 95%
at 0.75-0.8 (reaction). **These are idealized comparison curves.** The real fleet sits
5-10 points below them: F-1 60.5% at 0.20 against the curve's 66%.

**4. Real efficiency data vs U/C0** `[SP-8110 Fig. 14 p.17]` (digitized): Mark 10 F-1 2-row
VC @Tt1 1470 °F (0.20, 61.0%); Mark 3 H-1 2-row PC @1200 °F (0.45, 62.3%); 2-row air (ref.
5) (0.30, 61.9%); 3-stage (ref. 4) (0.22, 69.6%); Mark 15-F J-2 fuel VC @1200 °F (0.18,
56.9%); Mark 15-O J-2 ox VC (0.10, 45.0%); M-1 fuel VC (0.19, 62.0% predicted); M-1 ox VC
(0.13, 52.0%); RL10 2-stage PC (0.35, 73.7%); Agena 1-row partial admission (0.18, 40.7%);
single-row ref. 6 (0.20, 50.9%); single-row ref. 7 shrouded (0.145, 46.1%) vs
**unshrouded (0.19, 38.3%)**. The J-2 fuel and ox points in Fig. 14 (56.9/45.0%) sit 3
points below their Table I values (60.1/48.4%), probably a different operating point.

**5. Two-row VC efficiency map** `[SP-8110 Fig. 53 p.84]`, the monograph's recommended
preliminary-design chart. It assumes mean dia ≥ 10 in, nozzle angle 12-23°, shrouded
blades, controlled clearances, conventional profiles and full admission. η(T-S) in % vs U/C0
for **Dm/An** (nozzle outlet mean dia / nozzle nominal outlet area, 1/in;
Dm/An = 1/(π·Hn·sin α2) `[Fig. 55]`), pixel-digitized:

| U/C0 | 0.06 | 0.08 | 0.10 | 0.12 | 0.14 | 0.16 | 0.18 | 0.20 | 0.22 | 0.24 | 0.26 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Dm/An = 0 | 31.2 | 39.6 | 47.3 | 54.2 | 60.5 | 65.8 | 70.3 | 74.0 | 77.1 | 79.5 | 81.3 (→82.5 @0.28) |
| 1 | 29.4 | 37.6 | 44.9 | 51.4 | 57.2 | 62.1 | 66.2 | 69.7 | 72.4 | 74.4 | 76.0 |
| 2 | 27.5 | 35.1 | 41.9 | 48.1 | 53.5 | 58.1 | 61.8 | 65.0 | 67.6 | 69.3 | 70.4 |
| 3 | 25.9 | 33.0 | 39.2 | 45.0 | 50.0 | 54.0 | 57.4 | 60.4 | 62.6 | 64.3 | 65.1 |
| 4 | 24.1 | 30.6 | 36.4 | 41.8 | 46.4 | 50.2 | 53.3 | 56.0 | 57.9 | 59.2 | 59.8 |
| 5 | 22.1 | 28.1 | 33.5 | 38.4 | 42.6 | 46.1 | 48.9 | 51.3 | 53.0 | 54.0 | 54.4 |

Dm/An is a blade-size proxy: short nozzle blades or a shallow nozzle angle give a high
Dm/An and lower efficiency. The J-2 fuel turbine has Hn 0.42 in and sin α 0.233
(Table VIII), so Dm/An = 3.25, and the chart reads about 56% at U/C0 0.18 against the
real 60.1%. **Direction is right, magnitude about 4 points conservative** (my check). The
F-1's nozzle angle is not given, so its Dm/An can't be computed from this source.

**6. Loss mechanisms and prediction method (Emmert procedure)** `[SP-8110 §2.2.1 p.19-25,
§3.2.1 p.85-89]`. This is the procedure used to design the J-2 and F-1 turbines.
- Isentropic drop per element (eq. 1b): Δhs = (RT/J)·γ/(γ−1)·[1 − (ps2/pt1)^((γ−1)/γ)].
- Effective expansion energy (eq. 2): Δhes = φ²·Δhs, where φ² = f(blade deflection angle θ,
  axial width b) from **Fig. 16**. φ² ≈ 0.955 at θ ≈ 0-20°, ≈ 0.945 at 60°, ≈ 0.91-0.925
  at 100°, and at 140° ≈ 0.885 (b = 2.0 in) down to ≈ 0.835 (b = 0.5 in).
- Kinetic-energy coefficient (eq. 3): **ψ² = 2φ² − 1**.
- Corrected inlet kinetic energy (eq. 4): Δhev = Δhv·ψ²·Ci·Cm.
  - Ci (incidence) comes from Fig. 17: 1.0 at 0°, about 0.97 at ±10°, about 0.8 at −30° or
    +35°, and 0.6 at −40° (sharp-edged blades).
  - Cm (inlet relative Mach) comes from Fig. 18: 1.0 at M = 1, ≈ 0.97 at 1.4, ≈ 0.93 at 1.7
    and ≈ 0.855 at 2.2.
- Diagram factors (eqs. 8-9): Ed1 = (U/c1)(2cos α1 − U/c1) and Ed2 = (U/w2)(2cos α2 − U/w2).
  Diagram work (eq. 10) is Δhwd = Σ(Δhe1·Ed1 + Δhe2·Ed2), and **η_td = Δhwd/Δhs**
  (eq. 11).
- **Final η(T-S) = εd·η_td** `[§3.2.1 p.88-89]`. The diagram-efficiency factor εd comes from
  **Fig. 55** (0.15-in tip clearance; Rocketdyne and published test points). Pixel-digitized
  as straight lines: **shrouded (least-mean-square) εd ≈ 1.076 − 0.0455·(Dm/An)**, with the
  shroud scatter band ±0.03; **open-clearance (unshrouded) εd ≈ 1.000 − 0.046·(Dm/An)**.
  This is the monograph's closest thing to a blade-size/leakage loss correlation.
- **Worked example** `[Tables VII/VIII p.86-87]`: a one-stage, 2-row VC LOX/LH2 turbine,
  6.22 lb/s, 26 100 rpm, 1200 °F, 600 psia to 100 psia static, U = 1424 ft/s, 5900 hp. Its
  geometry is identical to Mark 15-F (J-2 fuel) in Table IV.
  - Per-row values: nozzle exit M 1.28 and α 13.5°; velocity ratios 0.20 (nozzle), 0.31
    (1-R), 0.43 (S), 0.62 (2-R).
  - Blading work per row is 351/207/136/79 Btu/lb, 773 total.
  - φ²: nozzle 0.941/0.920, 1-R 0.832, S 0.847, 2-R 0.880. ψ² (corrected): 0.646, 0.688,
    0.725.
  - **Reaction per the 10% rule** (below): nozzle to rotor 1 at 123 psia, stator exit
    107.8, rotor 2 exit 100.2 psia.
  - My back-calculation: overall Δhs ≈ 1185 Btu/lb, so η_td ≈ 0.65. With εd(3.25, LMS)
    ≈ 0.93 that gives η(T-S) ≈ 0.60, which reproduces Table I's 60.1%. The sheet's 5900 hp
    implies about 0.57, so the power line may be a different rating.
- **T-S vs T-T** `[§2.2.1 p.25]`: GG turbines are quoted total-to-static, with exit kinetic
  energy charged to the turbine. Expander and topping turbines, whose exhaust feeds the
  chamber, are quoted total-to-total.

**7. Partial admission** `[SP-8110 §2.2.2 p.25-28, §3.2.2 p.90-93]`:
- **Windage/pumping loss (eq. 12): η_LW = 5.6×10⁻⁵·(U/C0)²·ρ·N·(1−F)/F**, where F is the
  active admission fraction and ρ the gas density.
- Stenning scavenging/momentum loss (eq. 13): η_TSM = [(1 + K(1 − p/3f))/(1 + K)]·η_FA,
  where K = wheel exit/entry velocity ratio, p = blade pitch, f = nozzle arc length and
  η_FA = full-admission efficiency.
- Combined (eq. 14): η_PA = η_TSM − η_LW. Units for eq. 12 aren't stated; presumably
  lbm/ft³ and rpm, but verify before coding.
- **Fig. 20** (NASA-Lewis 3.75-in single-row turbine, PR 2.5-3.5): at the design U/C0 ≈ 0.38,
  η is about **68.5% at 100% admission, 65% at 51%, 62.5% at 31% and 56% at 12%**. At
  U/C0 0.20 all arcs sit at about 46-49%. Peak η shifts to lower U/C0 as admission falls.
- **Fig. 57** (50%-admission turbine, arc arrangement): 100% admission peaks about 78% at
  U/C0 ≈ 0.48. One continuous 180° arc gives ≈ 68%; 2 arcs ≈ 65%; 3 arcs ≈ 62.5%; 6 arcs
  ≈ 57%; 85 arcs ≈ 46%. **Use one continuous arc** `[§3.2.2.2]`.
- A small first-stage arc loses at least 50% of the exit kinetic energy before a second
  stage. **"a small arc of admission should be avoided in applications requiring high
  turbine efficiencies"** `[§3.2.2.1 p.92]`.
- High-PR, high-energy gases tolerate partial-admission losses better than low-PR subsonic
  turbines `[p.28]`.

**8. Stage reaction** `[SP-8110 §2.2.3 p.28-29, §3.2.3 p.93-94]`:
- Reaction blading uses 25-50% reaction for U/C0 > 0.40 and subsonic PR. The design
  criterion is **35-50% for best efficiency**.
- **2-row VC turbines are not pure impulse: 10% total reaction, ⅔ on the second stator
  and ⅓ on the second rotor, none on the first rotor**. This prevents adverse root
  pressure gradients.

**9. Tip clearance and shrouding** `[SP-8110 §2.3.8 p.41-43, Fig. 29, §3.3.8 p.101]`:
- **Shrouded rotors give +2 to 6 points** over unshrouded in impulse staging.
- Production turbines of **≥ 500 hp (J-2, F-1, M-1) are shrouded**. Unshrouded blades go
  in machines of ≤ 400 hp with blades < 0.5 in tall.
- **Recommended tip clearance is 1% of blade height** (honeycomb/labyrinth seals installed
  at zero clearance where possible). Unshrouded tips should be recessed ≥ 0.005 in into a
  casing groove.
- Fig. 29 (my straight-line fit): η_c/η_0 drops about **1.7% per 1% (clearance/height)
  for a one-stage impulse turbine** (≈ 0.95 at 3.5%, ≈ 0.81 at 11.8%) and about **2.7%
  per 1% for a one-stage reaction turbine** (≈ 0.97 at 1.2%, ≈ 0.78 at 8%).
- Axial stator-rotor gap of 15-35% of vane chord; **minimum loss at 0.25 chord**.

**10. Intake manifold** `[SP-8110 §2.2.4 p.29, §3.2.4 p.94]`:
- GG turbines: manifold Δp ≤ 2% of available inlet pressure (single radial inlet: 2-5%
  historically).
- Staged-combustion turbines use a no-loss axial-entry manifold.
- Size for Mach 0.25-0.30 with 10-20% (§2 says 10-25%) extra area. Constant-diameter tori
  are preferred to constant-velocity ones.

**11. Blading structural criteria** `[SP-8110 §2.4.1 p.43-52, §3.4 p.102-106]`:
- **Mechanical-design speed = 1.10 × predicted maximum** (so centrifugal loads are 1.20×).
  Pressures and torques are also 1.20×; thermal loads are at the predicted maximum.
- Safety factors: **FS_u 1.5, FS_y 1.1** on minimum-guaranteed (99%/95%) properties for
  manifolds, casings, shafts, supports and fasteners. **1.4 on strain** for low-cycle
  fatigue, or **≥ 4 on cycles** for long life.
- **Preliminary blade-stress sizing by AaN²** (annulus area × speed²): Aa·N² = π·Dm·H·N²
  (eq. 21). The allowable (eq. 20, as printed) is (AaN²)allow = (Ftu/FS)·Kt − R2·σp·
  (1800g/(π·ρ·R0·R1²)). The printed Kt placement looks garbled; re-derive before use.
- **Fig. 30 allowable AaN² (in²·rpm², ×10⁹)** at blade+shroud/solid-blade weight ratio
  0.85 (ratio 0.70 values in brackets, roughly 15-20% higher):

| Material | ~100 °F | 600 °F | 1000 °F | 1200 °F | 1500 °F |
|---|---|---|---|---|---|
| Ti 6-2-4-2 (wrought) | 82 [96] | 58 [68] | – | – | – |
| Udimet 630 (wrought) | 57 [68] | ≈53 | 43 [51] | ≈28 [37] | – |
| IN 100 (cast) | 45 [52] | 38 | ≈35 | ≈29 | 22 [27] |
| Udimet 700 (wrought) | 51 [62] | ≈35 | ≈31 | ≈28 | 16 [20] |
| Inconel 718 (wrought) | 35 [43] | ≈33 | ≈31 | ≈27 | 5 [5] |
| Alloy 713C (cast) | 26 [30] | 24 [29] | 24 [29] | ≈21 | 12 [14] |

  My cross-check with Table IV: the F-1 second rotor is about 13×10⁹ (π·34.9·3.95·5490²).
  The first rotor is about 7×10⁹. 713C allows about 21-24×10⁹ at the 1000-1300 °F that
  the downstream rows plausibly see, so both have margin there. At the full 1550 °F inlet
  total temperature the allowable falls to about 10-12×10⁹, so the second rotor only
  clears if its relative metal temperature is well below inlet. That is plausible after
  nozzle expansion, but this source doesn't state it.
- **Blade Goodman limits** `[Fig. 33 p.51]`: alternating stress ≤ endurance/1.33; mean
  stress ≤ the smaller of Ftu/1.5 and Fty/1.1.
- **Resonance margin ±15%** on blade critical speeds `[Fig. 34, §3.4.1.1.7]`.
- Vibratory stress = R·σ_gas-bending, with **R = 1.0** when nonresonant. At resonance
  (eq. 27), use R2 = 0.25 with mode receptiveness factors 0.87/0.066/0.041 for bending
  modes 1-3.
- Minimum Kt 1.25 when the root fillet radius equals the local blade thickness.
- Blade thickness tolerance ±0.003-0.004 in.
- Radial-equilibrium (free-vortex) blading is required above 1-in blade height.

**12. Disk, shaft and rotor criteria** `[SP-8110 §2.4.4 p.55-65, §3.4.4 p.109-112]`:
- **Burst speed ≥ 120% of mechanical-design speed.** **Yield speed ≥ 105%.** Safety
  factor 1.1 on yield for peak radial and rim compressive tangential stress.
- Burst speed: Nb = Nd·√(Fb·Ftu/σAT) (eq. 34). For elongation < 2-3%, use
  Nb = Nd·√(Ftu/σ'tmax) (eq. 35).
- The burst factor Fb comes from Fig. 38 as a function of elongation and design factor
  Fd = σA/σtmax. Fd = 1 gives Fb = 1. At 1% elongation Fd 0.95 gives ≈ 0.82 and
  Fd 0.3-0.5 gives ≈ 0.15-0.22. All curves converge to about 0.77-0.97 at 20% elongation.
- Stress concentration for splines/eccentric holes: Kt = 1.4 − 0.02e (e = elongation, %).
- Preliminary neck sizing: radial stress ≈ 90% of yield minus 10-20 ksi for thermal
  stress.
- **Operate ≤ 85% of the lowest 2nd-or-higher diametral disk critical speed.**
- Spin-test if the design speed is > 50% of burst, spinning to ≤ 90% of burst.
- Shaft (modified Soderberg, eq. 37): FS 1.5. Alternating torque = 5% of steady.
- Fastener separation margin of 1.5. Curvic-coupling pitch dia = 0.4-0.5 × turbine pitch
  dia.
- **Rotordynamics: no steady operation within ±20% of any critical speed** `[§2.5.1.2]`.
  Maximum operating speed ≤ 80% of the lowest synchronous critical if possible
  `[§3.5.1.2]`.
- Manifold proof test at 1.2 × mechanical-design pressure, scaled by the ratio of
  room-temperature to operating-temperature property.
- Rotor balance: a low-speed (1000-2000 rpm) multiplane balance is adequate for most 1-
  and 2-row turbines.

**13. Casing and manifold construction by inlet pressure** `[SP-8110 §2.4.5 p.65-71,
§3.4.5 p.112-114]`:
- Below 500 °F and low power: the diaphragm carries the loads.
- Below 100 psi: sheet-metal unitized manifold and casing (J-2 ox).
- Up to 500 psi (1000 psi max): welded torus and casing (F-1 production). Welded
  assemblies distort and crack near 1000 psi.
- Above 500 psi or above 1200 °F: separate the manifold and nozzle from the casing
  (alternate Mark 10, M-1).
- High-pressure manifolds split the inlet flow both ways round the torus.
- **Don't mount the gas generator on the turbine manifold** `[§3.5.4.5.2]`.
- Exhaust ducts should be axial or carry straightener vanes. Duct turning caused
  last-rotor pressure gradients, vibration and a choked, reduced turbine flow `[§2.5.3,
  §3.5.3]`.

**14. Materials** `[SP-8110 Table II p.11, Table VI p.78, §3.6 p.121]`:
- Blades: Stellite 21 (cast; Mark 3/4/15-O/29-O), **alloy 713C** (cast; Mark 10/15-F/29-F),
  Inconel X-750, Inconel 718.
- Disks: 16-25-6, X-750, Rene 41, Inconel 718.
- Nozzles and manifolds: Hastelloy B/C, Rene 41, X-750, 19-9DL, Stellite 21, 310/321.
- Blade attachment: welded (Mark 3/4), integral (Mark 9/25) or fir-tree (the rest).
- Use 347/321 for welded stainless and avoid 310. Weld Rene 41 with Hastelloy W filler.
- Table VI failure fixes: an Inconel 718 disk forging failed spin test from poor
  ductility, fixed by raising the solution heat-treat from 1750 to 1950 °F. Alloy 713C
  thermal-fatigue cracking was fixed with finer equiaxed grain. Rene 41 manifold weld
  cracking was fixed with Hastelloy W filler and an inert-atmosphere anneal.

**Parametric examples** `[Figs 51-52 p.80-81]`:
- Fig. 51: a 2-stage LOX/LH2 topping-type turbine (1550 °F, 25 000 rpm, 67.3 lb/s, PR
  1.45-1.58) is predicted at **η(T-S) 68-71%**. Efficiency falls about 2 points as PR goes
  from 1.46 to 1.58, and each extra 100 ft/s of U adds 0.5-1 point.
- Fig. 52: 32 000 rpm, PR 1.51, 178.8 lb/s LOX/LH2 over U 1200-1700 ft/s. This is an
  SSME-class topping turbine example, not read in detail.

**F-1 torque map** `[Fig. 56 p.91]`: torque parameter Tq/(Pt1·Ae·Dm) against speed
parameter Dm·N/√(RT1) for PR 12-22. It is a linear falling family of lines, and the
monograph recommends this format over U/C0-η plots for engine-system use.

## Design method

The monograph supplies:
- the staging rules (§3.1.4);
- an η-vs-U/C0 family by row count (Fig. 13) and a two-row-VC map with a blade-size axis
  (Fig. 53);
- a complete row-by-row loss-coefficient procedure (Emmert: φ²(θ, b), ψ² = 2φ² − 1, Ci, Cm,
  diagram factors, εd(Dm/An)) with a worked J-2-fuel-class example;
- closed-form partial-admission windage and scavenging losses;
- the AaN² blade-stress screen with material curves, and burst, yield and critical-speed
  margins.

This is enough to replace a per-staging efficiency ceiling with η = f(U/C0, rows, blade
size, shroud, admission), anchored on the Table I fleet.

**Implication for engine_designer** (for the main session, not a code change):
- Staging should key on the **computed U/C0**, not on propellant or cycle. The F-1 (direct
  drive, 5490 rpm, U 840 ft/s, C0 about 4200 ft/s) lands at U/C0 0.20, which is 2-row VC
  territory. The geared H-1 (32 800 rpm, U 1290 ft/s) lands at about 0.36 single-stage (0.51
  √ΣU²), which is pressure-compounded or single-row territory.
- `turbopump_efficiency.ETA_TURBINE_CEILING["pressure_compounded_2stage"] = 0.76` is
  fitted to "H-1 70.2%" `[SP-8107 Table III]`. **SP-8110 Table I and Fig. 14 give the same
  Mark 3 turbine η(T-S) = 62.5%** (1200 °F, 600 psia, PR 17.7, U/C0 0.42), and the Atlas
  sustainer Mark 4 PC gives 46.3%. The two sibling monographs disagree by 8 points on the H-1;
  it may be a T-T vs T-S basis or a different H-1 rating, and needs resolving before the
  PC ceiling is trusted.
- The anchor list's J-2 fuel PR 7.3 and ox PR 2.5 don't match SP-8110's J-2 values (6.35
  and 3.16). 7.30 and 2.68 are SP-8110's **J-2S** Mark 29 values; worth rechecking against
  SP-8107.

## Section map

- §1 Introduction: p.1-2 (leaf 13-14). Read.
- §2 intro and Figs 1-10 (turbine assemblies): p.3-9 (leaf 15-21). Read; figure pages are
  image-only.
- **Table I Design Data: p.10 (leaf 22). Read visually; the text layer is garbled.**
- Table II Materials: p.11 (leaf 23). Read visually.
- Fig. 11 (cycles and installations): p.12 (leaf 24). Not viewed.
- **§2.1 Preliminary Design (2.1.1 PR/flow/engine performance with Fig. 12 tau factor,
  2.1.2 gas properties with Table III, 2.1.3 U/C0 with Figs 13-14, 2.1.4 Staging): p.13-18
  (leaf 25-30). Read in full.**
- **§2.2 Aerothermodynamic Point Design (2.2.1 Emmert energy balance with Figs 15-19 and eqs
  1-11; 2.2.2 Partial Admission with Fig. 20 and eqs 12-14; 2.2.3 Stage Reaction with eq. 15;
  2.2.4 Intake Manifold): p.19-29 (leaf 31-41). Read in full.**
- §2.3 Nozzle/Vane/Blade Geometry (Table IV p.31; 2.3.1-2.3.7 profile construction, Zweifel
  0.70-1.15, trailing-edge coefficient ≥ 0.90, unguided turning 8-12° at root / ≤ 15° at
  tip): p.29-41 (leaf 41-53). Table IV read visually; the rest skimmed.
- **§2.3.8 Blade Shrouding and Clearance (Table V, Fig. 29): p.41-43 (leaf 53-55). Read.**
- **§2.4.1 Blading (AaN² Fig. 30, eqs 20-27, Figs 31-34): p.43-52 (leaf 55-64). Read.**
- §2.4.2-2.4.3 Nozzle/Stator: p.53-55 (leaf 65-67). Read.
- **§2.4.4 Rotor: disk/burst (Fig. 38, eqs 28-36, Fig. 39), shaft (eq. 37), fasteners,
  torque transmission: p.55-65 (leaf 67-77). Read.**
- §2.4.5 Casing/Manifold/Diaphragm: p.65-71 (leaf 77-83). Read.
- §2.5 Integration (rotordynamics, bearings/seals, exhaust ducts, problem areas): p.71-77
  (leaf 83-89). Read.
- §2.6-2.7 Materials/Instrumentation and Table VI: p.77-78 (leaf 89-90). Read; Table VI
  visually.
- **§3.1 Preliminary Design criteria (Figs 51-53; §3.1.4 staging rules): p.79-84 (leaf
  91-96). Read in full.**
- **§3.2 Aerothermodynamic criteria (Tables VII-VIII worked example, Figs 54-57): p.85-95
  (leaf 97-107). Read in full.**
- §3.3 Blade geometry criteria: p.95-102 (leaf 107-114). §3.3.5-3.3.8 read; the rest
  skimmed.
- **§3.4 Mechanical/structural criteria: p.102-115 (leaf 114-127). Read.**
- §3.5-3.7 Integration/materials/instrumentation criteria: p.115-122 (leaf 127-134). Read.
- App. A Glossary p.123-135, App. B p.137, References p.139-142. Not read, except the
  glossary definition An = "nozzle nominal outlet area".

## Caveats

- **1974, Rocketdyne-centric, pre-SSME.** There is no SSME HPFTP/HPOTP, Titan LR87/LR91,
  RS-68 or Russian data; use `[SP-8107]` Table III and other sources for those. The
  "reaction > 80%" statements for staged-combustion turbines are forward-looking. The
  only reaction example is the illustrative Fig. 51 (68-71% predicted).
- **Fig. 13 is idealized.** Its reaction curve peaks near 95%. Use it for curve **shape**
  and peak location by row count, not magnitude. Real fleet points (Table I, Fig. 14) run
  5-10 points lower.
- **The H-1 efficiency conflicts with `[SP-8107]`** (62.5% here vs 70.2% there). The H-1
  U/C0 of 0.42 also doesn't reproduce from Table III properties under either the single-U
  or √ΣU² convention (my check). See Design method.
- Table I mixes production, former-production and never-flown development turbines (E-1,
  H-2, X-8, M-1, J-2S, J-2X). Status is in the table. The "J-2X" here is the 1960s J-2
  derivative, not the 2000s Ares engine.
- All digitized figure values (Figs 13, 14, 20, 29, 30, 38, 53, 55, 57) are my pixel or
  visual reads of scanned plots. Expect ±1 point on η and ±0.01 on U/C0; the log-log
  Fig. 13 is worse at its ends.
- Several equations are OCR- or print-ambiguous: eq. 20 (Kt placement), and the units of
  eq. 12's ρN term are not stated. Re-derive before coding.
- Table III LOX/RP-1 molecular weights (R 44-67, so MW 23-35) look heavy for fuel-rich GG
  gas, and the monograph itself says the table is not for formal design. Don't substitute
  it for the tool's Cantera-baked tables; it's useful only for reproducing SP-8110's own
  U/C0 numbers.
- Fig. 53's Dm/An = 1/(π·Hn·sin α2) needs the nozzle exit angle, which Table IV doesn't
  give for the F-1. Only the J-2 fuel turbine (Table VIII) can be placed on the chart
  directly.
