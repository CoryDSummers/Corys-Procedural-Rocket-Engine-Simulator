# [Huzel] — Design of Liquid Propellant Rocket Engines (NASA SP-125)

## Identity

- **Title**: *Design of Liquid Propellant Rocket Engines*
- **Authors**: Dieter K. Huzel and David H. Huang, Rocketdyne Division, North American Aviation / Rockwell
- **Series**: NASA SP-125, Office of Technology Utilization, NASA, Washington D.C.
- **Edition**: 2nd edition (cover), 1971 printing; 1st edition 1967. This is the NASA SP-125,
  **not** the 1992 AIAA revision (*Modern Engineering for Design of Liquid-Propellant Rocket
  Engines*, Huang/Huzel/Arbit).
- **Extent**: ~460 printed pages, 469 PDF leaves. Scanned images + OCR text layer (decent
  quality; equations legible in rendered page images).
- **PDF leaf ↔ printed page**: `leaf ≈ printed page + 9` (printed p.1 = leaf 10).

## Character

Written "on the job" at Rocketdyne as a bridge between propulsion fundamentals and real
industry engine design. Its backbone is four running worked examples — the hypothetical
*Alpha vehicle* engines:

| Engine | Propellants | Cycle | Role |
|---|---|---|---|
| A-1 | LOX/RP-1, MR 2.35, Pc 1000 psia, ε 14 | gas generator | booster, 750 klbf |
| A-2 | LOX/LH2, MR 5.22, Pc 800 psia, ε 40 | gas generator | 150 klbf upper stage |
| A-3 | storable (N2O4/N2H4-UDMH) | pressure-fed | 16 klbf |
| A-4 | storable | pressure-fed | 7.5 klbf upper/space |

Numbers throughout are quantitative and stepwise — this is the source to copy a *design
procedure* from.

## Chapter map — "go here for X"

| § | Title | Printed p. | Feeds topic |
|---|---|---|---|
| **I** | Introduction to Liquid Propellant Rocket Engines | 1 | 01, 03, 11 |
| 1.1 | Generation of thrust; F = ṁ·ve/g + Ae(Pe−Pa) (eq 1-6); effective exhaust velocity c | 1 | 01 |
| 1.2 | Gas-flow processes; 8 ideal-flow assumptions; isentropic relations | 4 | 01 |
| 1.3 | Performance parameters Is, c\*, Cf and their interrelations | 10 | 01, 03 |
| 1.4 | Liquid rocket propellants | 18 | 11 |
| **II** | Rocket Engine Design Implements | 31 | 12, 13 |
| 2.1 | Major design parameters and their typical ranges | 31 | — |
| 2.4 | Stress analysis; design-limit / yield / **ultimate = 1.5× design-limit** load structure (eq 2-8…2-11); endurance limit 20–60 % of ultimate | 56 | 12 |
| 2.5 | Selection of materials; material groups; cryo & H2 embrittlement; thermal-shock figure of merit Ftu·k/(E·α) | 59 | 12 |
| **III** | Introduction to Sample Calculations (A-1…A-4) | 63 | all |
| **IV** | **Design of Thrust Chambers and Other Combustion Devices** | 81 | 02–07, 14 |
| 4.2 | Thrust-chamber performance parameters; c\* correction ~0.975, Cf correction 0.98–1.01 | 83 | 03 |
| 4.3 | Configuration layout: Vc = ṁ·V̄·ts (4-3), **L\* = Vc/At (4-4)**, Table 4-1 L\* by propellant, contraction ratio, conical & Rao bell contour, **λ = ½(1+cos α) (4-8)**, Fig 4-12 (thrust eff vs %bell), Fig 4-14 (θn, θe vs ε) | 86 | 02, 04 |
| 4.4 | Thrust-chamber cooling: 6 methods; **Bartz h_g (eq 4-13)**; Colburn Nu = C·Re^0.8·Pr^0.34; recovery factor 0.90–0.98; regen/film/transpiration/ablative/radiation; radiation q = ε·σ·Twg^4 | 98 | 06, 07 |
| 4.4 | **Tubular Wall Thrust Chamber Design** (extracted 2026-09-17): circular-tube combined stress (eq 4-27/4-28), longitudinal thermal inelastic-buckling (eq 4-29), elongated-tube bending term (eq 4-30, Fig 4-30), coax-shell combined stress (eq 4-31), passage pressure drop (eq 4-32); Fig 4-29/4-30 tube cross-sections; **Fig 4-31 shows tube shape morphing elongated↔circular along the chamber axis**; Sample Calc 4-4 (A-1/A-2 real Inconel-X tube numbers at the throat); **p.113-114 (PDF 122-123): tube manufacture - uniform round tubes cut to length, swaged by internal hydraulic pressure in a variable-section die, wax-filled, bent to contour in a fixture, trimmed, then arranged on a brazing core "to assure even distribution of the gaps between tubes" and furnace-brazed** (re-read 2026-09-23) | 107–114 | 06 |
| 4.5 | Injector design: 10 patterns; ΔPi = ρV²/(2g·Cd²) (4-40); **Cd 0.5–0.92**; **ΔP rule-of-thumb 15–20 % of Pc**; β angle; injection momentum ratio (4-42) | 121 | 05 |
| 4.6 | Gas-generating devices: gas temps 400–1000 °F (pressurant) / 1200–1700 °F (turbine drive); solid/mono/bipropellant GGs; solid burn rate R = k1·Pc^n | 131 | 10 |
| 4.7 | Ignition devices; TEA-TEB, pyrotechnic, hypergolic slug, spark; ignition detection methods | 136 | 15 |
| 4.8 | Combustion instability: modes & acoustic frequency (Fig 4-59: longitudinal N = ae/2Lc; tangential 0.59 ae/dc; radial 1.22 ae/dc); classes hi-freq/lo-freq/intermediate; peak-to-peak/Pc < 0.10 threshold | 143 | 14 |
| **V** | Design of Pressurized-Gas Propellant-Feed Systems | 151 | 08 |
| **VI** | **Design of Turbopump Propellant-Feed Systems** | 176 | 09 |
| 6.2 | Turbopump system performance & design parameters; specific speed, suction specific speed | 186 | 09 |
| 6.3–6.4 | Centrifugal / axial-flow pump design with efficiency charts | 204 | 09 |
| 6.5 | Turbine design: impulse vs reaction, pressure- vs velocity-compounding, U/C0 efficiency charts | 238 | 09 |
| 6.6 | Bearings, seals, gears — DN limits | 257 | 09 |
| **VII** | Design of Controls and Valves | 263 | 15, 16 |
| 7.3 | Engine thrust-level control | 267 | 15 |
| 7.4 | Mixture-ratio & propellant-utilization control | 268 | 15 |
| 7.5 | **Thrust-vector control**: gimbal-bearing design, actuator sizing, hinge moments, secondary injection | 272 | 16 |
| **VIII** | Design of Propellant Tanks (membrane stress, cryo insulation, filament-wound) | 329 | (out of tool scope) |
| **IX** | Interconnecting Components and Mounts | 353 | 16 |
| 9.6 | Design of gimbal mounts | 379 | 16 |
| **X** | Engine Systems Design Integration | 383 | 13, 15 |
| 10.2 | Dynamic analyses — start/shutdown transient sequencing | 384 | 15 |
| 10.3 | Design integration for engine-system calibration | 390 | 15 |
| 10.8 | Clustering of engines | 415 | — |
| **XI** | Design of Liquid Propellant Space Engines (restart, RCS, high-ε, ablative/radiation thrusters) | 429 | 06, 11 |

## Notation quirks

- `(Pc)ns` = chamber/nozzle stagnation pressure (what the tool calls Pc).
- `c*` written with an asterisk; `Cf` for thrust coefficient (not C_F).
- `λ` = divergence / thrust-efficiency factor for the nozzle (= the tool's `nozzle_divergence_efficiency`).
- `ε` and `εc` = expansion and **contraction** area ratio respectively.
- `rw` = O/F mixture ratio by mass; `IV` in OCR = ṁ (weight flow rate), a scan artefact.
- US customary throughout (psia, lb, in, °R, Btu). `g = 32.2 ft/s²` appears as a literal in
  most equations.

## Caveats

- Pre-SSME (1967/71): staged-combustion and expander cycles are covered lightly; no modern
  alloy allowable-stress data (NARloy-Z, GRCop, C-C, etc.); combustion tables are
  frozen-composition.
- Propellant combustion charts (figs 4-3…4-6) are for specific Pc values (1000 psia LOX/RP-1,
  800 psia LOX/LH2, 100 psia for the fluorine pairs) — read at those, interpolate with care.

## Regen passage geometry data (2026-09-23 re-read)

Keyword search (tubes, coolant velocity, F-1, J-2, RL10, H-1) of the text layer; the key
pages re-read from rendered images (leaf N = printed p.N-9 around ch.4). **Huzel names no
real engine's tube/channel geometry anywhere** - F-1/J-2 appear only in a Saturn V vehicle
listing. The only tube numbers are **Sample Calculation (4-4)** for the book's hypothetical
A-1 / A-2 stage engines. These are textbook DESIGN EXAMPLES, not hardware - usable as a
worked method and as order-of-magnitude analogs (A-1 ~ F-1/H-1-class LOX/RP-1, A-2 ~
J-2-class LOX/LH2), never as a real-engine spot check.

| Quantity | A-1 (LOX/RP-1, 747,000 lbf SL, Pc 1000 psia, eps 14) | A-2 (LOX/LH2, 149,500 lbf alt) |
|---|---|---|
| Throat dia Dt | 24.9 in (0.632 m) | 11.2 in (0.284 m) |
| Pass layout | **2-pass**, down alternate tubes, up adjacent | **1½-pass**: inlet manifold at **eps = 8**, down to eps = 30 and back, then through throat and chamber to injector |
| Tube material / wall t | Inconel X, **0.020 in (0.51 mm)** | Inconel X, **0.008 in (0.20 mm)** |
| Tube ID at throat | **0.855 in (21.7 mm)** | **0.185 in (4.70 mm)** |
| Tube count N | **94** (rounded even from 94.5) | **178** |
| Coolant flow | 827 lb/s (375 kg/s) = all fuel | 54.5 lb/s (24.7 kg/s) = all fuel |
| Throat coolant velocity | **87.6 ft/s (26.7 m/s)** | not computed |
| Throat coolant pressure | 1500 psia (10.3 MPa) | 1200 psia (8.27 MPa) (estimated) |
| Throat coolant bulk T | 600 °R (333 K), "up" tube | 135 °R (75 K) |
| T_wg / T_wc at throat | 1188 °R / ~1000 °R (660 / 556 K) | 1600 °R / 1204 °R (889 / 669 K) |
| Throat heat flux | 3.00 Btu/in²·s (4.9 MW/m²) | 19.10 Btu/in²·s (31.2 MW/m²) |
| Required h_c | 0.0075 Btu/in²·s·°F (22.1 kW/m²K) | 0.0179 Btu/in²·s·°F (52.7 kW/m²K) |

`[Huzel Sample Calc 4-4 p.109-113]`; A-1/A-2 thrusts `[Huzel Sample Calc 4-2 p.95]`, A-1 eps 14 `[Huzel Fig. 4-20 p.96]`.
Tube-count relation used: N = pi [Dt + 0.8 (d + 2t)] / (d + 2t) (0.8 = tube centers on a
circle); A-2's printed final substitution shows d = 0.17 in, but N = 178 is what d = 0.185 in
gives (typo only). A-1's N = 94.5 does not reproduce exactly from its own printed relations
(they give ~90 at d = 0.85 in) - treat the book's arithmetic as +/-5 %. Also: "Total
temperature increase for a typical thrust chamber design is of the order of **100 °F** [56 K]
between cooling jacket inlet and outlet" `[Huzel §4.4 p.110]` (RP-1 context, generic).
Tube forming: uniform round tubes cut, swaged by internal hydraulic pressure in a die,
wax-filled, bent to contour `[Huzel p.113-114, Fig. 4-31/4-32]`.

**NOT in Huzel** (for any real engine): tube/channel count, dimensions, land width, jacket
flow fraction, coolant inlet/outlet T/P, throat coolant velocity, separate-circuit layout.
