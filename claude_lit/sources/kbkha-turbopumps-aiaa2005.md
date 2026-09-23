# [KBKhA] — Turbopumps for Gas Generator and Staged Combustion Cycle Rocket Engines

## Identity

- **Title**: *Turbopumps for Gas Generator and Staged Combustion Cycle Rocket Engines*
- **Authors**: Y. Demyanenko, A. Dmitrenko, A. Ivanov, V. Pershin — Konstruktorskoe Buro
  Khimavtomatiky (KBKhA / Chemical Automatics Design Bureau), Voronezh, Russia
- **Publication**: **AIAA 2005-3946**, 41st AIAA/ASME/SAE/ASEE Joint Propulsion Conference &
  Exhibit, 10–13 July 2005, Tucson, Arizona. © 2005 KBKhA, published by AIAA with permission.
- **Extent**: 8 pages, born-digital (clean text; figures are schematics and one bar chart —
  not machine-readable but captions are complete).

## Character

A comparative case study: one GG-cycle engine (**RD-0110**) and its staged-combustion
replacement (**RD-0124**), same thrust class, same propellants (LOX/kerosene), same
manufacturer. It is the single best source for *what changes in the turbopump when you go
from open to closed cycle*, with real side-by-side numbers.

## The two engines

| Parameter | RD-0110 (GG cycle) | RD-0124 (staged combustion) |
|---|---|---|
| Application | Soyuz 3rd stage | Soyuz-2 / Angara upper stages |
| Engine thrust | 298.03 kN | 294.3 kN |
| Specific impulse | 326 s | 359 s (**+33 s**) |
| Chamber pressure | 6.8 MPa | 15.53 MPa (**×2.28**) |
| Chambers per turbopump | 4 | 4 |
| Feed system | one main turbopump, no boost pumps | main turbopump + LOX & kerosene turbo-axial boost pumps |
| Payload benefit of the upgrade | — | +950 kg to the launch vehicle |

## Table 2 — pump & turbine parameters (the core data)

| | RD-0110 | RD-0124 |
|---|---|---|
| LOX pump inlet pressure | 0.28 MPa | (matched via boost pump) |
| **LOX pump discharge pressure** | 9.81 MPa | **33.28 MPa** (×3.4) |
| LOX pump flowrate | 64.5 kg/s | 65.46 kg/s |
| Kerosene pump inlet pressure | 0.14 MPa | (matched via boost pump) |
| **Kerosene pump discharge pressure** | 14.32 MPa | 36.56 MPa |
| Kerosene pump flowrate | 29.3 kg/s | 29.91 kg/s |
| **Turbine inlet pressure** | 5.79 MPa | 29.98 MPa |
| Turbine discharge pressure | 0.42 MPa | 17.55 MPa |
| **Turbine flowrate** | 3.97 kg/s | **59.85 kg/s** (closed cycle routes ~all flow through turbine) |
| **Turbine inlet temperature** | **1050 K** | (fuel-rich; not tabulated) |
| Rotor speed | 18 400 rpm | 39 000 rpm (×2.1) |

Key derived relations stated in the paper:
- Pc ×2.3 → LOX pump discharge pressure ×3.4 (super-linear).
- RD-0124 turbopump is **higher power and lower weight** than RD-0110's, but the RD-0124
  feed **system** is ~10 % heavier overall because of the added boost pumps.
- RD-0124 turbopump is significantly **smaller** in envelope than RD-0110's.

## Design & materials contrast (from §V, §VII)

- **GG-cycle turbopump (RD-0110)**: single shaft, double-inlet back-to-back centrifugal
  impellers with inducers (good suction performance without boost pumps), fuel-rich
  supersonic turbine, **aluminium-alloy** housings/impellers/inducers, milled+brazed
  shrouded impellers, bronze floating-ring seals, cast nickel-alloy integrally-bladed
  turbine wheel, sub-critical rotor, axial thrust self-balanced (low turbine-cavity
  pressure + double-inlet pumps).
- **Staged-combustion turbopump (RD-0124)** — KBKhA's 10-point design concept: minimum
  parts / welds / external flanges; extensive **castings + HIP**; **powder metallurgy** for
  high-load parts; **vaneless gas distributor** for oxidizer-rich turbines; floating-ring
  seals; axial-thrust-balance device integral with the impeller main disc; full-range
  high-speed rotor testing. **Stainless-steel** cast housings/impellers, cast nickel-alloy
  turbine housing, **blisk** high-strength-nickel turbine wheel with EDM blades, oxidation-
  tolerant coatings.
- Special attention areas for closed-cycle turbopumps: strength margins, suction
  performance, rotor dynamics, thrust balance, **prevention of turbine-part ignition in the
  oxidizer-rich environment**.
- Development: GG turbopumps can be tested standalone at near-operating conditions;
  staged-combustion turbopumps cannot (component interaction dominates, especially in
  start/shutdown transients) → KBKhA uses sub-component development on substitute hardware
  in two phases.
- Turbopump failures historically = 50–70 % of all engine failures during development.

## Section map

| § | Content |
|---|---|
| I | KBKhA history: first turbopump 1955; 68 turbopumps built; thrust 15–2000 kN; open → closed cycle for Isp |
| II | Feed-system milestone timeline (Fig 1): GG 1955–61 → staged combustion 1961→; addition of ejector then turbo-axial boost pumps |
| III | RD-0110 / RD-0124 feed schematics (Figs 4, 5) |
| IV | Turbopump operability comparison (Table 2; Fig 6 bar chart of 7 relative stress/speed parameters) |
| V | Turbopump design schemes (Figs 8, 9) |
| VI | Development-test peculiarities |
| VII | Materials & manufacturing (casting, HIP, powder metallurgy) |
| VIII | Conclusion |

## Caveats

- Two data points, one propellant pair (LOX/kerosene), one design bureau. Excellent for the
  *direction and magnitude* of cycle → turbopump-stress effects; not a general correlation.
- Figures 6–9 are schematics / bar charts — the numeric ratios in Fig 6 are not labelled in
  the text.
