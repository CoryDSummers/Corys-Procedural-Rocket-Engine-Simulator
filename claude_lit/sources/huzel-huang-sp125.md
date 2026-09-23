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
