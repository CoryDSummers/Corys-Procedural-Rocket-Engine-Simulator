# [SP-8107] — Turbopump Systems for Liquid Rocket Engines (NASA SP-8107)

## Identity

- **Title**: *Turbopump Systems for Liquid Rocket Engines*
- **Series**: NASA SP-8107, NASA Space Vehicle Design Criteria (Chemical Propulsion)
- **Authors**: A. J. Sobin and W. R. Bissell, Rocketdyne Division, Rockwell International;
  edited by Russell B. Keller, Jr., NASA Lewis. Reviewers from Aerojet, Pratt & Whitney,
  NASA Lewis.
- **Date**: August 1974. NTIS price $6.25.
- **Extent**: body to ~printed p.136, appendices/refs to p.153, 168 PDF leaves. Scanned +
  spaceless OCR (rejoin words when reading). Key tables were cross-checked against rendered
  page images.
- **PDF leaf ↔ printed page**: `leaf ≈ printed page + 14` (State-of-the-Art body starts
  printed p.12 = leaf ~26).

## Character

The **system-level** turbopump design-criteria monograph — selection logic, limits, typical
ranges, and start/shutdown/Pogo integration. Component detail (inducers, pumps, turbines,
gears, bearings, seals, rotordynamics) lives in companion monographs (SP-8052, SP-8109,
SP-8110, …). Design-Criteria monograph format (§2 State of the Art ↔ §3 Design Criteria,
decimally parallel).

## Tables I–III — real hardware data (printed pp. 3–5, mid-1973)

### Table I — Turbopump assemblies

| Engine | Application | Thrust (lbf) | Pc (psia) | Arrangement | Overall eff (%) | Weight (lbm) | **Specific hp (hp/lbm)** | Start system |
|---|---|---|---|---|---|---|---|---|
| A-7 | Redstone | 78 000 | 318 | single shaft, turbine middle | 26.4 | 332 | 2.22 | liquid monoprop start tank |
| MB-3 | Thor | 170 000 | 594 | geared turbine | 46.0 | 562 | 5.40 | solid start cartridge |
| LR87-AJ-3 | Titan I 1st | 150 000 | 585 | geared | 45.8 | 720 | 5.11 | liquid start tanks |
| H-1 | Saturn IB | 205 000 | 702 | geared turbine | 47.0 | 520 | 7.98 | solid start cartridge |
| MA-5 sustainer | Atlas | 57 000 | 706 | geared turbine | 35.0 | 229 | 7.27 | solid start cartridge |
| MA-5 booster | Atlas | 330 000 | 577 | geared turbine | 48.0 | 875 | 3.59 | solid start cartridge |
| **F-1** | Saturn IC | 1 522 000 | 1122 | single shaft, turbine on end | 44.6 | 3150 | **16.6** | tank head |
| YLR81-BA-11 | Agena | 16 000 | 506 | geared | 20.0 | 60.5 | 5.81 | solid start cartridge |
| YLR87-AJ-7 | Gemini-Titan 1st | 215 000 | 784 | geared | 38.1 | 484 | 10.70 | solid start cartridge |
| RL10A-3-3 | Centaur | 15 000 | 400 | geared O₂ pump | 42.0 | 76.1 | 9.03 | tank head |
| J-2 | Saturn S-II/S-IVB | 230 000 | 787 | dual turbopump, series turbines | 37.4 / 44.9 | 305 / 369 | 7.73 / **21.60** | pressurised-gas start tank |
| SSME (EPL) | Space Shuttle | 512 300 | 3237 | dual turbopump, parallel turbines | 56.5 / 58.5 | 555 / 701 | 50.0 / **108.9** | tank head |

Conversion: **hp/lbm × 1644 ≈ W/kg** (745.7 W/hp ÷ 0.4536 kg/lbm). So F-1 ≈ 27 300 W/kg,
J-2 high figure ≈ 35 500 W/kg, SSME 50–108.9 hp/lbm ≈ **82 000–179 000 W/kg**.

### Table II — pumps: real efficiencies (η_pump)

A-7 O₂ 72 % / alcohol 70 %; MB-3 O₂ 79 % / RJ-1 72 %; H-1 O₂ 77.8 % / RP-1 71.8 %; MA-5
sustainer ~64 %; MA-5 booster ~74 %; **F-1 O₂ 74.6 % / RP-1 72.6 %**; YLR87 N₂O₄ / A-50
68 %; RL10 O₂ 62.9 % / H₂ 55.0 %; J-2 O₂ 80.0 % / H₂ 73.0 %; SSME O₂ 78.1 / 69.6 %,
H₂ 74.1 %. Also: NPSH_min (contractually specified, max acceptable) 12–132 ft; NPSH_crit
(at 2 % discharge-pressure drop) 11–75 ft; LH2 pumps high NPSH (J-2 H₂ 130/75), LOX pumps
low (F-1 O₂ 65/60).
**F-1 O₂ pump**: 1600 psia discharge, 3097 ft head, 4070 lbm/s, 25 200 gpm, 5488 rpm,
30 200 hp. **F-1 RP-1 pump**: 1856 psia, 5168 ft, 1715 lbm/s, 5488 rpm, 22 100 hp.
(F-1 Pc 1122 psia → O₂ discharge/Pc = 1.43, RP-1 discharge/Pc = 1.65.)

### Table III — turbines

| Engine | Working fluid | Type | Inlet T (°F) | PR | η (%) | Pitchline (ft/s) |
|---|---|---|---|---|---|---|
| A-7 | H₂O₂ | 2-row velocity-comp | 740 | 21.2 | 37.2 | 412 |
| MB-3 | O₂/RJ-1 | 2-stage pressure-comp | 1204 | 17.6 | – | 1200 |
| LR87-AJ-3 | O₂/RP-1 | 2-stage pressure-comp | 1334 | 17.8 | 63.6 | 1035 |
| H-1 | O₂/RP-1 | 2-stage pressure-comp | 1200 | 17.7 | 70.2 | 1290 |
| MA-5 sustainer | O₂/RP-1 | 2-stage pressure-comp | 1075 | 25.0 | 46.3 | 995 |
| F-1 | O₂/RP-1 | 2-row velocity-comp | 1450 | 16.4 | 60.5 | 840 |
| YLR81-BA-11 | IRFNA/UDMH | impulse, partial admission | 1400 | 37.7 | 41.0 | 855 |
| YLR87-AJ-7 | N₂O₄/A-50 | 2-stage pressure-comp | 1667 | 17.8 | 56.0 | 980 |
| RL10A-3-3 | H₂ (expander) | 2-stage pressure-comp | −106 | 1.42 | 74.0 | 782 |
| J-2 | O₂/H₂ | 2-row velocity-comp | 760 (ox) / 1200 (fuel) | 2.5 / 7.3 | 48.4 / 60.1 | 590 / 1480 |
| SSME (EPL) | O₂/H₂ (staged comb) | reaction | 1101 (ox) / 1391 (fuel) | 1.59 / 1.56 | 72.9 / 79.0 | 1363 / 1661 |

So: **GG-cycle turbine inlet temp clusters 1200–1450 °F (922–1061 K)**, efficiency 46–70 %
(most 55–66 %); storables run hotter (~1650 °F / 1180 K). Expander/staged-combustion
turbines: PR 1.4–1.6, efficiency 73–79 %.

## Design relations & limits worth reusing

- **Specific speed**: `Ns = N·Q^½ / H^¾` (rpm·gpm^½/ft^¾). Below Ns 2000–3000, raising speed
  raises pump efficiency. Centrifugal-pump efficiency peaks at stage Ns 1300 (φ_it1 = 0.05)
  to 2500 (φ_it1 = 0.20). Axial-pump efficiency drops below Ns 2000, flat 2000–10 000.
- **Pump headrise**: `H = 144·[(Po)2 − (Po)1] / ρ1` (psia → ft). For high-pressure H₂ pumps
  (>2000 psi rise) use incremental isentropic enthalpy rise instead (compressibility).
- **Critical NPSH** = the value where headrise is 2 % below the noncavitating value. Fixes:
  raise tank pressure, lower pump speed, or redesign inlet (larger diameter, lower flow
  coefficient — used on the J-2 H₂ pump).
- **Tip-speed limits (forged titanium)**: 2800 ft/s unshrouded centrifugal; 2000 ft/s
  shrouded centrifugal (1700–2300 by design); 1500 ft/s inducers & axial rotors. Only H₂
  pumps approach these.
- **Turbine-drive-cycle effect on pump discharge pressure** (§2.1.1.4, Table V/VI, Fig 11):

  | Cycle | Turbine vs chamber | Pump discharge P ≈ | Turbine PR | Isp loss from bleed | Pc practical limit |
  |---|---|---|---|---|---|
  | Gas generator | parallel | **1.5 × Pc** | ~20 | ⅓–1 % at 1000 psia, ∝ Pc | none (but Pc kept <1500 psi to limit turbine flow) |
  | Tap-off | parallel | ~ GG | slightly < GG | ~ GG | more complex thrust chamber |
  | Expander | series | **2.5 × Pc** | < 1.5 | none | ~1000 psia (heat available) |
  | Staged combustion | series | **> 2.0 × Pc** (nonlinear) | < 1.5 | none | ~3000 psia; resultant discharge 7000–8000 psia |
  | Monopropellant GG | parallel | ~1.5 × Pc | – | large at high Pc | – |

  J-2 (GG): Pc 787 psia, fuel-pump discharge/Pc = 1.6, overall turbine PR = 19.
  RL10 (expander): Pc 400 psia, fuel-pump discharge/Pc = 2.5, overall turbine PR = 1.4.
- **Turbine staging**: GG & tap-off → two-row velocity-compounded; expander & staged
  combustion → two-stage pressure-compounded or reaction. Low-energy fuels (LOX/RP-1,
  N₂O₄/A-50) → pressure-compounded; H₂ → velocity-compounded (exceptions: F-1 & Redstone,
  low pitchline; RL10 & SSME, PR only 1.4–1.6). Turbine efficiency ≈ f(pitchline velocity)
  for given inlet temp & PR; small low-hp turbines use partial admission and gain efficiency
  with rotational speed.
- **Overall turbopump efficiency** (η_pump·η_turbine): 35–48 % for GG-era engines, ~60 % for
  SSME (needs high-Ns pumps + reaction turbines).
- **Turbine inlet temperature**: "as high as practical (~1500 °F with an uncooled turbine
  and GG)"; cooled turbines allow higher.
- **Geared turbopump** for engine thrust < 10 000 lbf.
- **Throttling**: centrifugal pumps ≈ 2× the throttle range of axial pumps; stable
  throttling to zero flow if Ns > ~2500; complete shutoff inadvisable except <10 s (trapped
  propellant heating).

## Transients & controls (§2.3)

- **Turbopump time constant** τ ∝ I·N / Tq (rotating inertia × speed ÷ shaft torque). Reduce
  inertia or raise torque → faster start.
- **Start methods**: solid-propellant start cartridge (H-1) — rapid, turbopump
  characteristics matter little; **tank-head start** (F-1) — turbopump characteristics
  matter a lot; **pressurised-gas start** (J-2, after tank-head start was abandoned because
  the fuel pump hit its head/flow stall discontinuity, Q/N dropped below ~⅓ design, and H₂
  vaporised in the pump). Ground-level atmospheric pressure lowers turbine PR at low power →
  less torque; "a 10 % increase in nozzle area or turbine flow may reduce start time as much
  as 50 %."
- **Shutdown**: cut turbine power first, then close main valves. 500 msec cutoff is "fast
  for a large engine." Surge pressures of several hundred psi (water-hammer analogy). LOX/
  RP-1 → higher surge than LH2 (density / feed-system inertance).
- **Pogo** (§2.3.2.4): 5–25 Hz longitudinal vehicle-system instability. Pump inlet
  compliance (vapor pockets on inducer vane leading edges) + inertance + suction-line
  inertance = a low-damped resonant system; when a vehicle structural mode matches a pump
  suction mode, Pogo can occur. Pump-side mitigation: steep head/flow curves. Fix: pogo
  accumulator on the feed line (SSME LOX line, between the two O₂ turbopumps).
- **Control** (§2.3.1.3): most engines open-loop — calibration orifices in the GG feed lines
  (J-2, F-1, H-1) or a pressure regulator on GG oxidizer flow (MA-5, MB-3). RL10 is
  closed-loop thrust control (senses Pc, adjusts turbine bypass valve). Component-tolerance
  stack-up is **root-sum-square**, not worst-case algebraic.

## Section map (State-of-the-Art page / Design-Criteria page)

- 2.1 Preliminary design (12 / 99): system requirements (headrise/flowrate, NPSH, propellant
  properties, **turbine drive cycle §2.1.1.4**, throttling, efficiency, weight/size,
  conditioning, life/reliability/cost); selection of system type (number of units,
  equivalent-weight factor, rotational speed, arrangement, pump config, turbine config)
- 2.2 Detail design & integration (48 / 112): limits to rotational speed (inducer cavitation
  / suction specific speed, bearing DN, seal rubbing speed, turbine-blade centrifugal
  stress, gear pitchline velocity); pump design; turbine design; mechanical integration
  (bearing placement, rotor attachment, housing, axial thrust balance, thermal barriers);
  system interfaces; **start systems §2.2.6** (tank head, pressurised-gas start tanks,
  liquid-propellant start tanks, solid-propellant start cartridge)
- 2.3 Design evaluation (87 / 131): design-point & off-design system balance; control
  constraints; **system dynamic analysis §2.3.2** (start, throttling, shutdown, Pogo);
  development testing

## Caveats

- System-level; component formulas are referenced out to companion monographs. Pair with
  `[Huzel]` Ch. VI and `[Sutton]` §10.1 for pump/turbine internal design.
- Tables I–III are "best available data as of mid-1973"; SSME rows are pre-operational
  projections.
