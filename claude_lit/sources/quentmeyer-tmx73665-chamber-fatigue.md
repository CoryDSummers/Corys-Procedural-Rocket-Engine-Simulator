# NASA TM X-73665 — Experimental Fatigue Life Investigation of Cylindrical Thrust Chambers

## Identity

R. J. Quentmeyer (NASA Lewis Research Center), *Experimental Fatigue Life Investigation of
Cylindrical Thrust Chambers*, **NASA TM X-73665**, presented at the 13th AIAA/SAE Propulsion
Conference, Orlando, July 11-13, 1977 (NTRS accession 19770024295, N77-31239). `literature/NASA
TM X-73665 - Experimental Fatigue Life Investigation of Cylindrical Thrust Chambers.pdf` (22 PDF
pages: CASI disclaimer, cover, 7 text pages with Table I, 13 figure pages). Renamed on
2026-10-16 from its numeric NTRS filename. Tag: `[Quentmeyer-TMX73665]`.

This is NOT the same document as `[Quentmeyer-CR185257]`, which is the same author's 1990
survey of liner life-enhancing concepts. This one is the earlier primary test program, and that
1990 survey's "393 cycles uncoated Amzirc" baseline traces back to it (cylinder S/N 56, Table I).

## Character

A short primary experimental report: **22 milled-channel cylindrical liners** (12 OFHC copper,
7 Amzirc, 3 NARloy-Z) were thermally cycled in one LOX/GH2 test rig, and 21 of them were run to
failure. That makes it the first set in `claude_lit/` with *many* real thrust-chamber
cycles-to-failure points (contrast `[Miller-CuFatigue]`, which has one test article). It gives:
- a post-test destructive analysis of the failure mechanism;
- empirical **wall-temperature → cycles-to-failure** power-law fits;
- a material ranking that **disagrees** with the uniaxial isothermal strain-test ranking.

Text layer: good on pp.3-9, Table I is legible, and the figure pages are noise. Figs. 17 and 19
(the correlations) were rendered as images and read visually. Read in full.

## Test conditions

`[Quentmeyer-TMX73665 §Apparatus p.2; §Test Procedure p.3]`

| Item | Value |
|---|---|
| Propellants / MR | LOX + ambient GH2 (porous Rigimesh face, 70 LOX showerhead tubes), O/F 6.0 |
| Chamber pressure | 4.14 MPa (600 psia) |
| Thrust | ≈5.34 kN (1,200 lbf); annular chamber, contraction = expansion area ratio 1.79 |
| Throat heat flux (avg) | **54 MW/m²** (33 Btu/in²·s) |
| Liner | ID 6.60 cm; 10.16 or 15.24 cm long; **72 milled channels 1.69 mm wide × 1.27 mm high, hot wall 0.89 mm, ribs 1.27 mm**; electrodeposited-Cu closeout |
| Coolant | LH2, separately supplied, ≈0.91 kg/s nominal (flow varied over each cycle) |
| Thermal cycle | **3.5 s: 1.7 s hot (wall reaches steady state) + 1.8 s chill back to LH2 temperature** |
| c* efficiency | 93-96 % |
| Failure criterion | first through-wall crack (audible hiss + vapour streak during chill-down) |

The centerbody (water-cooled Amzirc with a 0.076-0.127 mm flame-sprayed ZrO2 coat) had its coat
replaced every 100-200 cycles and **failed by LCF itself after 1000-2000 cycles** `[p.3]`.

## Key results

**Cycles to failure, Table I** `[Quentmeyer-TMX73665 Table I p.7]` (N.I. = no instrumentation):

| Material | Cylinders: N_f |
|---|---|
| OFHC copper | 817 (N.I.), 120, 236, 150, 168, 220 (N.I.), 210, 220, 98 (N.I.), 56, 177, **2044 (no failure, test stopped)** |
| Amzirc, ½-hard | 944, 505, 381, 119, 340, 106 |
| Amzirc, ½-hard then aged 482 °C / 4 h | **393** (the `[Quentmeyer-CR185257]` TBC baseline) |
| NARloy-Z (hot spun, solution annealed, aged) | 556, 688, 679 (N.I.) |

**Life vs. temperature correlations** (log-log straight lines through each material's
instrumented points, **in °R**; K forms are derived here by dividing the coefficient by 1.8)
`[Quentmeyer-TMX73665 Figs. 15-17, 19 pp.20-22]`:

| Correlation | °R form (source) | K form (derived) |
|---|---|---|
| Steady hot-gas-wall temperature, OFHC Cu | T_gw = 4520 · N_f^-0.205 | T_gw = 2511 · N_f^-0.205 |
| Steady hot-gas-wall temperature, ½-hard Amzirc | T_gw = 5650 · N_f^-0.229 | T_gw = 3139 · N_f^-0.229 |
| Max hot-wall-to-backside ΔT, OFHC Cu | ΔT = 3290 · N_f^-0.178 | ΔT = 1828 · N_f^-0.178 |
| Max hot-wall-to-backside ΔT, ½-hard Amzirc | ΔT = 4550 · N_f^-0.226 | ΔT = 2528 · N_f^-0.226 |

Check: OFHC at N_f = 2044 gives 947 °R ≈ 526 K, against the measured no-failure point at 514 K
(925 °R). T_gw and ΔT are *projected* from rib and backside thermocouples with a 35-element 2-D
SINDA model at the throat plane, so they are not measured hot-wall values `[§Post Test Thermal
Analysis p.4-5]`. The circumferential scatter in steady rib temperature was ±21 °C (±70 °F).

**Material ranking flips with the basis** `[p.5-6]`:
- By wall temperature, ½-hard Amzirc ≈ OFHC copper (one line fits both), while **NARloy-Z and
  aged Amzirc are best**.
- By strain range in the uniaxial isothermal tests (Conway et al., Ref. 6 = NASA CR-121259), at
  a 2 % strain range: **OFHC 130, NARloy-Z 930, ½-hard Amzirc 1,400 cycles**, so Amzirc is best.
- The author's conclusion: chamber life rankings "do not agree" with uniaxial, isothermal
  rankings.

**Failure mechanism, every cylinder** `[§Post Test Destructive Analysis p.4]`:
- Each cycle thins the coolant-channel hot wall at the channel centreline and bulges it toward
  the chamber axis, producing the **"doghouse"** channel shape.
- It ends in **tensile rupture**, not a classic fatigue crack. Recrystallised fine grains appear
  at the crack. OFHC and Amzirc strain-softened; NARloy-Z held or gained hardness.
- Hypothesised chain:
  1. Hot-wall compressive plastic strain on heat-up, against the cool closeout.
  2. Coolant-over-chamber pressure bias plus first-yield on the hot side give a **net outward
     ratchet each cycle**.
  3. Necking-like thinning follows.
  4. The deformed channel's larger flow area lowers coolant h_c, and the roughened hot wall
     raises h_g. Both raise the wall temperature and accelerate failure.
- Hannum et al. (AIAA 76-685) blame creep rupture plus thermal ratcheting. Rocketdyne's SSME
  subscale analysis calls it "strain-induced creep".

**Life requirements quoted** `[Introduction p.1]`:
- SSME: Pc 20.7 MPa, throat flux 131-147 MW/m², **life requirement 55 thermal cycles**.
- Orbit Transfer Vehicle thrust chamber: **200-300 cycles**.

## Section map

p.1 abstract and introduction (SSME/OTV requirements, history of copper-chamber LCF work) ·
p.2 apparatus (chamber, test section, instrumentation, injector) · p.3 centerbody, facility,
data, test procedure · p.3-4 results and destructive analysis (mechanism) · p.4-6 post-test
thermal analysis and correlations · p.6 concluding remarks · p.7 references and Table I ·
pp.8-20 figures (Fig. 15-17 T_gw vs N_f; Fig. 19 ΔT vs N_f).

## Caveats

- **One rig, one heat flux, one Pc, short holds.** The 1.7 s hot phase means this is
  low-cycle data with almost **no creep hold time**. It says nothing directly about how
  *burn duration* (time at temperature per cycle) shortens life. That is the gap a burn-time
  model needs; see `OPEN_QUESTIONS.md`.
- The wall temperatures are model-projected, not measured, and the fits are one straight line
  through about 6-9 points per material. Trust the exponent (≈ -0.2: a 10 % hotter wall costs
  roughly 40 % of the cycles) more than the coefficient.
- NARloy-Z and aged Amzirc have only 2-3 instrumented points and no fitted line.
- Annular geometry with a hydrogen-cooled outer cylinder. The same author warns that a
  reasonable life prediction must account for channel geometry change, the resulting
  wall-temperature drift and property changes during life. A single-temperature correlation
  does not.
