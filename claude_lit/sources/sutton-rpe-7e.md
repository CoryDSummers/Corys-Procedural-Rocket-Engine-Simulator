# [Sutton] — Rocket Propulsion Elements, 7th edition

## Identity

- **Title**: *Rocket Propulsion Elements*, **Seventh Edition**
- **Authors**: George P. Sutton and Oscar Biblarz
- **Publisher**: John Wiley & Sons, © 2001 (this file is the Wiley India authorised reprint)
- **Extent**: 20 chapters + 5 appendices + index; ~751 printed pages, 767 PDF leaves.
  Scanned + OCR; the PDF carries a full bookmark table of contents (use `get_toc()`).
- **PDF leaf ↔ printed page**: `leaf ≈ printed page + 15` (varies ±1; the bookmarks give
  exact leaf numbers).

## Character

The standard modern textbook. More conceptual framing and up-to-date hardware than
`[Huzel]`; weaker on stepwise "do this then this" procedure. Chapters 8, 9, 10 and 16 are
the liquid-engine design core; 11–15 are solid/hybrid (out of scope) and 18–20 are plumes /
electric / testing.

## Chapter map — "go here for X"

| Ch / § | Title | PDF leaf | Feeds topic |
|---|---|---|---|
| **2** | Definitions and Fundamentals; thrust, Is, energy/efficiency; §2.5 typical performance values | 42 | 01 |
| **3** | **Nozzle Theory and Thermodynamic Relations** | 60 | 01, 02 |
| 3.3 | Isentropic flow through nozzles (T/p/ρ/A ratios, throat conditions, Cf, c\*) | 67 | 01 |
| 3.4 | **Nozzle configurations**: cone (λ factor), bell/contoured (Rao), plug/aerospike/E-D; length & performance comparison | 90 | 02 |
| 3.5 | **Real nozzles**: divergence, boundary-layer, chemical-kinetics, two-phase, nonuniformity losses with typical % magnitudes; separation; side loads | 100 | 01 |
| 3.6 | Four performance parameters | 107 | 01 |
| **5** | **Chemical Rocket Propellant Performance Analysis** | 175 | 03, 11 |
| 5.3 | Nozzle expansion: **frozen vs shifting equilibrium** | 187 | 03, 11 |
| 5.4 | Computer analysis (NASA CEA / Lewis program, assumptions) | 194 | 03 |
| 5.5 | **Results of thermochemical calculations**: Is/Tc/c\* vs MR & Pc; **experimental Is 3–12 % below ideal, of which ~1–4 % is combustion**; Table 5-4 worked LOX/LH2 | 195 | 03, 11 |
| **6** | Liquid Propellant Rocket Engine Fundamentals | 212 | 08 |
| 6.6 | **Turbopump feed systems and engine cycles** (GG / staged combustion / expander / pressure-fed schematics, pros/cons) | 236 | 08 |
| 6.7 | Flow and pressure balance (engine power-balance method) | 242 | 08, 09 |
| 6.8 | RCS / attitude-control engines | 243 | 11 |
| **7** | **Liquid Propellants**: property tables (density, vapor pressure, viscosity, freezing/boiling, Cp), oxidizers, fuels, monopropellants, hypergolicity, hazards | 256 | 11 |
| **8** | **Thrust Chambers** | 283 | 02, 04, 05, 06, 12 |
| 8.1 | **Injectors**: types (doublet/triplet/coax/pintle/platelet); Q = Cd·A·√(2Δp/ρ) (8-1); **Table 8-2 Cd values**; β angle (8-6, 8-7); Table 8-1 real thrust-chamber data (RL10B-2, LE-7, R-4D-class, RS-27, AJ-10) | 286 | 05 |
| 8.2 | **Combustion chamber & nozzle**: Vc (8-8), **L\* = Vc/At (8-9), typical 0.8–3.0 m**; stay time 0.001–0.040 s; contraction-ratio pressure-loss note (<3× throat); heat-transfer distribution (peak at throat); cooling method overview; **cooling transition ε ~6–10** | 297 | 04, 06 |
| 8.3 | **Heat Transfer Analysis**: Bartz; coolant-side correlation; regen channel/tube design; film / transpiration / ablative / radiation with typical numbers; **0.5–5 % of energy to walls**; **50 W/cm² … 16 kW/cm²** | 323 | 06 |
| 8.4 | Starting and ignition | 335 | 15 |
| 8.5 | Variable thrust / throttling | 338 | 05, 15 |
| 8.6 | **Sample thrust-chamber design analysis** (worked end-to-end) | 339 | 02–06 |
| **9** | Combustion of Liquid Propellants | 357 | 03, 14 |
| 9.1 | Combustion process; atomization / vaporization-limited length | 358 | 03 |
| 9.3 | **Combustion Instability**: Table 9-2 (chug 10–400 Hz, buzz 400–1000 Hz, screech >1000 Hz); acoustic modes; frequency eq (9-1); **baffles (odd compartment count, <4000 Hz)**; Helmholtz absorber cavities (9-2); Pogo; rating bombs & pulse guns | 363 | 14 |
| **10** | **Turbopumps, Engine Design, Controls, Calibration, Integration, Optimization** | 377 | 09, 13, 15 |
| 10.1 | **Turbopumps**: Ns, suction specific speed & NPSH, inducers, pump & turbine types, gas-generator/preburner, cycle comparison, worked example | 377 | 09 |
| 10.3 | **Propellant budget** (usable, residual, boiloff, startup/shutdown, reserves) | 402 | 13 |
| 10.4 | Engine design procedure & parameter selection | 404 | 15 |
| 10.5 | Engine controls (thrust & MR control, valves, calibration orifices) | 411 | 15 |
| 10.7 | System integration & engine optimization (payload-sensitivity trade) | 426 | 13 |
| **16** | **Thrust Vector Control** | 623 | 16 |
| 16.1 | **TVC with a single nozzle**: gimbal vs hinge; Table 16-1 mechanisms & deflection ranges (**gimbal ±12°**); pitch moment F·L·sin δ; SSME gimbal (Table 16-2: **±10.5° op, 30 rad/s², 20°/s**); LITVC ±6°; jet vanes ±9° (0.5–3 % thrust loss) | 624 | 16 |
| 16.2 | TVC with multiple thrust chambers / nozzles (differential throttling, vernier) | 635 | 16 |
| App. 3 | Summary of key equations for ideal chemical rockets (one page) | leaf 746 | 01 |

## Notation quirks

- `c*` = characteristic velocity, `CF` = thrust coefficient, `c` = effective exhaust velocity.
- `k` (not γ) for specific-heat ratio; `M` for Mach and `9R` / `𝔐` (OCR-garbled) for molecular mass.
- SI primary with US customary in parentheses; some tables US-only.
- `L*` "pronounced el star"; Sutton notes it is somewhat deprecated in modern practice
  (chamber volume now scaled from prior similar designs) but still a useful proxy.

## Caveats

- OCR renders equations and some table cells poorly; the transcriptions in the topic files
  were checked against rendered page images. Re-render (`get_pixmap(dpi=200)`) before
  trusting any equation not already transcribed here.
- Chapters 11–15 (solid/hybrid) and 18–20 largely irrelevant to `engine_designer`.
