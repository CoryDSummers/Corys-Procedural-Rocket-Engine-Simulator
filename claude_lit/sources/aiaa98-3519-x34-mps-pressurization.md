# AIAA-98-3519 — Pressurization, Pneumatic, and Vent Subsystems of the X-34 Main Propulsion System

## Identity

A. Hedayat, T. E. Steadman, T. M. Brown and K. C. Knight (Propulsion Department, Sverdrup
Technology Inc., MSFC Group, Huntsville), with C. E. White Jr. and R. H. Champion Jr. (NASA
Marshall Space Flight Center), *Pressurization, Pneumatic, and Vent Subsystems of the X-34 Main
Propulsion System*, **AIAA-98-3519**, 34th AIAA/ASME/SAE/ASEE Joint Propulsion Conference,
Cleveland, July 13-15, 1998. A US Government work, not under copyright. NTRS accession
19980236000; the file was renamed from its numeric NTRS filename on 2026-10-18.
`literature/AIAA 98-3519 - Pressurization, Pneumatic, and Vent Subsystems of the X-34 MPS.pdf`
(11 PDF leaves: cover, then 10 numbered pages). Printed page = PDF leaf index, so leaf 4 is
p.4. Tag: `[X34-MPS]`.

It is one of three companion X-34 MPS papers from the same session. The other two are **not in
`literature/`**:
- AIAA-98-3517, McDonald et al., *Propellant Feed Subsystem*, which covers feed lines and
  engine-inlet conditions.
- AIAA-98-3518, Brown et al., *Propellant Management and Conditioning*.

The system overview is AIAA-97-3304 (Sgarlata & Winters).

## Character

This is a short conference paper by the MSFC/Sverdrup MPS analysis team. Its subject is the
**vehicle side** of a small reusable pump-fed LOX/RP-1 stage, flown by the NASA-MSFC
**Fastrac** 60 klbf gas-generator engine with a single-shaft turbopump. The other existing
Fastrac data in `claude_lit/` is `[Ch12-Materials]`'s one-piece silica-phenolic ablative
chamber and nozzle.

It covers four things:
- A pressurization-concept trade (regulators against orifices), with a vent/relief sizing
  check, run in GFSSP.
- A ROCETS transient of the chosen regulated helium system: bottle mass, pressure and
  temperature, and tank ullage histories.
- A ROCETS transient of the pneumatic-and-purge (P&P) subsystem: inter-propellant-seal (IPS)
  purge and engine spin start.
- A ground-fill analysis of the helium bottles.

Every number is a **design-analysis prediction (1998, before flight)**, not a measurement. The
X-34 never flew powered. Treat the values as a credible, internally consistent design point for a
real vehicle, not as test data.

The text layer is good. Every figure used here was rendered and **read visually**: Figs. 1-3
(schematics), Fig. 4, Figs. 5-11, Figs. 13-14. Values marked "~" are read off a plot. Figs. 17-18
(fill histories) have garbled axes, so only their text values are used.

## System parameters

`[X34-MPS p.1-2, p.5, p.7]` (SI with the original imperial units in parentheses)

| Item | Value |
|---|---|
| Engine | NASA-MSFC Fastrac, LOX/RP-1, single-shaft turbopump |
| Engine flow requirement | LOX **65.3 kg/s (144 lbm/s)**, RP-1 **29.9 kg/s (66 lbm/s)** → MR 2.18 (derived) |
| Propellant conditions (trade study) | LOX 90.4 K (-297 °F), 1,145 kg/m³ (71.5 lbm/ft³); RP-1 294 K (70 °F), 809 kg/m³ (50.5 lbm/ft³) |
| Tank volumes | LOX 8.51 m³ (300.6 ft³; aft and forward tanks), RP-1 5.34 m³ (188.5 ft³) |
| LOX tank ullage pressure | trade study: 379-421 kPa (55-61 psia, 58 ± 3); **final design 448 ± 21 kPa (65 ± 3 psia)** `[p.5]` |
| RP-1 tank ullage pressure | **345 ± 21 kPa (50 ± 3 psia, band 47-53)**. Held until the tank holds 3.44 kg (7.58 lbm) He, then blowdown to **179 kPa (26 psia) at end of burn** `[p.5-6]` |
| Tank proof pressure | 776 kPa (112.5 psia), about 1.7× the LOX operating pressure (derived) |
| Pressurant | helium, 4 bottles, 0.714 m³ (25.2 ft³) total, stored at **34.5 MPa (5,000 psia), 294 K (530 °R)**; **34.5 kg (76 lbm)** loaded |
| Before engine start | ground and captive-carry cooling drop the bottles to 31.6 MPa (4,580 psia), 269 K (485 °R) |
| Regulated pressure | 2.41 MPa (350 psia) at the regulator exit `[p.2, Fig. 1]` |
| Pressurant lines | main and LOX 25.4 OD / 21.1 ID mm (1.00 / 0.83 in). RP-1 19.1 / 15.7 mm (0.75 / 0.62 in), enlarged to **16.5 mm (0.65 in) ID** in the final design |
| Control | closed-loop solenoid bang-bang on tank-pressure sensors: **0.04 s signal delay + 0.05 s valve response**, linear area ramp `[p.5]` |
| P&P helium | forward 0.176 m³ (6.2 ft³) + aft 0.062 m³ (2.2 ft³) bottles; **11.6 kg (25.5 lbm)** at 34.5 MPa / 294 K `[p.7]` |
| P&P regulators | **IPS line 6.21 MPa (900 psia)**, **spin-start line 5.17 MPa (750 psia)**; lines 19.1 mm (0.75 in) OD, 16.5 mm (0.65 in) ID (the text is garbled at "ID of and 0.65 in") |
| LOX vent/relief | 57.2 mm (2.25 in) ID tubing, 63.5 mm (2.5 in) valve, exit orifice to limit GOX velocity. The RP-1 vent has no orifice `[p.4]` |

## Key results

1. **Tank pressures of a small pump-fed LOX/RP-1 stage**: LOX ullage 448 kPa (65 psia) ± 21 kPa,
   RP-1 345 kPa (50 psia) ± 21 kPa `[X34-MPS p.1, p.5]`.
   - In the transient the LOX ullage overshoots to 483 kPa (70 psia) at 6 s. The RP-1 ullage
     starts at 365 kPa (53 psia) and peaks at 400 kPa (58 psia) at 8 s `[p.6, Figs. 8, 10]`.
   - RP-1 pressurization **stops at 82 s** once the tank holds 3.44 kg (7.58 lbm) of helium.
     The ullage then blows down to 179 kPa (26 psia) by the end of the burn `[p.6, Figs. 10-11]`.
   - So the RP-1 pump inlet must tolerate about half its starting ullage pressure. RP-1's
     negligible vapor pressure is what allows this.
2. **Derived NPSP from ullage alone**: this is arithmetic done here, not in the paper. It ignores
   liquid head and line loss (neither is given) and takes the LOX vapor pressure as about 1 atm
   at 90.4 K.
   - LOX ≈ 448 - ~103 kPa ≈ 345 kPa ≈ **31 m (~100 ft)**.
   - RP-1 ≈ 345 kPa ≈ **43 m (~140 ft)** at the start of the burn, and ≈ 179 kPa ≈ **23 m
     (~74 ft)** at its end.
3. **Pressurant budget** `[p.5-6, p.9, Figs. 5-7, 9, 11]`:
   - Of the 34.5 kg (76 lbm) He loaded, the LOX tank takes **18.6 kg (41 lbm)** and the RP-1 tank
     **3.44 kg (7.58 lbm)**. The residual is **12.2 kg (27 lbm)**, so ~36 % is unused.
   - The bottles fall to 5.1 MPa (740 psia) and **133 K (240 °R)** by the end of pressurization,
     roughly 140 s on the figures' time axis.
   - Derived here: 144 + 66 lbm/s × ~140 s ≈ 13.3 t of propellant expelled for ~22 kg of helium,
     about **0.17 % of propellant mass**. The LOX would be ~94 % of the 9.7 t tank capacity.
   - Derived ideal-gas check: 18.6 kg He filling the 8.51 m³ LOX tank at 448 kPa implies a mean
     ullage temperature of ~99 K. That is consistent with cold, unheated helium over LOX.
4. **No pressurant heater or heat exchanger.** Helium goes from ambient bottles through
   regulators straight into both tanks. Bottle expansion cools it to 133 K by burnout, and the
   paper mentions no turbine-exhaust or other heater anywhere `[p.2, Figs. 1, 5-7]`.
   - The worst-case regulator-failure flows into the tanks are cold: **0.159 kg/s (0.35 lbm/s)
     at 214 K (-74 °F)** to LOX and **0.045 kg/s (0.10 lbm/s) at 201 K (-97 °F)** to RP-1 `[p.4]`.
   - The orifice options give 0.630 kg/s (1.39 lbm/s) at 220 K and 0.172 kg/s (0.38 lbm/s) at
     218 K.
5. **Trade-study outcome: regulators win** `[p.4-5, Fig. 4]`.
   - The vent/relief valve's probable response time is **0.5-1.0 s** (Fig. 4 shaded band).
   - Tank pressure rise time from 517 kPa (75 psia) to proof, read visually from Fig. 4:
     - Regulated LOX system: ~2.7 s at 0.283 m³ (10 ft³) ullage with helium at propellant
       temperature, ~1.1 s with helium at inlet temperature. At 0.133 m³ (4.7 ft³) ullage,
       ~1.25 s and ~0.5 s.
     - The orifice systems mostly reach proof in under 0.5-1 s.
     - RP-1, regulated, at the ~0.10 m³ (3.6 ft³) ullage case: ~2.0 / ~2.85 s.
   - Only the regulated system avoided overpressure at both high-ullage cases. Those cases are
     0.283 m³ (10 ft³, the minimum expected boil-off) and 0.538 m³ (19 ft³, the maximum
     boil-off).
   - The orifice options would also need the LOX vent exit orifice opened up. That gives sonic
     GOX in aluminum vent hardware, which is a **particle-impact ignition / aluminum-fire
     hazard**, so the orifice options were rejected `[p.4]`.
6. **LOX conditioning**: during controlled venting at altitude the LOX is conditioned to
   **88.9 K (160 °R)** by boil-off, slightly below its normal boiling point `[p.4]`.
7. **Inter-propellant-seal purge**: helium, run **"whenever propellants are provided to the
   engine"**. It is needed because LOX and RP-1 share the Fastrac's single pump shaft `[p.7]`.
   - Supply: regulated to 6.21 MPa (900 psia). The interface holds **5.03 MPa (730 psia)**,
     with a ~6.3 MPa (~920 psia) spike when the purge opens `[p.8, Fig. 14]`.
   - Total IPS helium is **~6.8 kg (15 lbm)** `[p.8, p.9 Summary]`.
   - Fig. 13, read visually: the purge starts ~900 s before engine start and reaches ~4 lbm at
     t = 0. It steps by ~1-2 lbm over the start, then rises linearly to ~15.5 lbm at 2,000 s.
   - Derived from those slopes: a steady IPS purge of **~2 g/s (~0.0045-0.005 lbm/s)**. This is
     the first real seal-purge flow magnitude in `claude_lit/` (compare `[SP-8121]`, which gives
     none). See Caveats for the time-axis inconsistency.
8. **Engine spin start**: helium from the same P&P bottles, regulated to 5.17 MPa (750 psia),
   drives the turbine during the first moments of pump operation.
   - It uses about **0.45 kg (1 lbm)**, delivered "very fast" at the start of the burn.
   - The interface pressure spikes to ~5.5 MPa (800 psia) when the spin-start solenoid opens
     `[p.7-8, Figs. 13-14]`.
   - The Fastrac's start is therefore a vehicle-supplied stored-gas spin start, not a tank-head
     start (compare `topics/15`'s start-method table).
9. **Ground fill of the helium bottles** `[p.8-9]`:
   - The fill is step-wise and limited by temperature. Supply is 37.9 MPa (5,500 psia), 294 K,
     through a 12.7 mm (0.5 in) ID line and valve.
   - The valve closes at any one of: 34.5 MPa, bottle wall 378 K (680 °R), or gas 444 K
     (800 °R). It reopens when the gas has cooled to 300 K (540 °R).
   - Pressurization bottles (76 lbm): **2.02 h**, 6 valve openings of 1-9 s.
   - P&P bottles (25.5 lbm): **2.5 h**, 6 openings of 1-4 s.
   - Bottles: SCI AC-5178 and Technical Products Group X600045.
10. **Bottle energy balance** used throughout: M c_p dT/dt = Σq + Σṁ_in H_in - Σṁ_out H_out, with
    q = ΔT/ΣR. The heat paths are inner free/forced convection, wall conduction and outer free
    convection `[p.5]`. It is a lumped-node method, not a correlation source.

## Design method

The vehicle-side pressurization sizing chain this paper shows:
1. Set the ullage pressure bands from the engine-inlet requirement. The requirement itself is in
   the companion feed paper AIAA-98-3517, not here.
2. Size the pressurant supply so the tank pressure stays inside a ± 21 kPa (± 3 psi) bang-bang
   band at the engine's flow.
3. Size the vent/relief so it passes the **worst failed-open pressurant flow** below proof
   **and** opens before the tank reaches proof (rise time > valve response, 0.5-1 s).
4. Run a lumped transient (helium energy balance) to get the helium load, the residual and the
   end-of-burn bottle temperature.

For engine_designer the useful outputs are the tank-pressure magnitudes, the
RP-1-blowdown-to-half idea, and the helium-purge/spin-start budgets. The tool does not model the
vehicle tanks.

## Section map

- Leaf 0: cover. Read.
- p.1 (leaf 1): Abstract and Introduction. Fastrac, helium storage conditions, tank pressure
  bands. Read.
- p.2 (leaf 2): Pressurization subsystems and the three-option trade study, including its
  assumptions list (flows, densities, tank volumes, orifice diameters). Read.
- p.3 (leaf 3): Figs. 1-3, schematics of the three options with line sizes. Read visually.
- p.4 (leaf 4): Vent/relief sizing, worst-case failure flows, GOX/aluminum hazard; Fig. 4 rise
  times to proof. Read; Fig. 4 read visually.
- p.5 (leaf 5): Trade conclusion; ROCETS pressurization transient, final requirements, valve
  timing, energy balance; initial and residual helium. Read.
- p.6 (leaf 6): Figs. 5-8 (bottle mass, pressure and temperature; LOX ullage); RP-1 blowdown
  text. Read visually.
- p.7 (leaf 7): Figs. 9-11 (LOX and RP-1 helium mass, RP-1 ullage); the pneumatic-and-purge
  subsystem (IPS, spin start, bottles, regulators); Fig. 12 schematic. Read visually.
- p.8 (leaf 8): Figs. 13-14 (IPS and spin-start helium usage and interface pressures); helium
  bottle fill analysis setup, Figs. 15-16. Read visually.
- p.9 (leaf 9): Fill results and Figs. 17-18 (axes garbled, text values used); Summary. Read.
- p.10 (leaf 10): Acknowledgments and references (AIAA-97-3304, 98-3517, 98-3518, GFSSP, ROCETS
  manual). Read.

## Caveats

- **These are predictions, not measurements.** The X-34 MPS was analysed before flight, and the
  vehicle never flew powered. The Fastrac engine was hot-fired, but this paper reports none of
  that test data.
- **No engine-inlet pressure requirement, NPSH/NPSP, feed-line loss or pump-inlet pressure** is
  given. Those are in AIAA-98-3517 (not in `literature/`). The tank ullage pressures here are
  upstream of the liquid head and the feed line, so they bound the pump-inlet pressure without
  equalling it.
- The **Fig. 13 time axis is inconsistent** with the text. The text says ~15 lbm of IPS helium
  "by the end of engine burn", but the plot runs to 2,000 s, while the pressurization figures
  end at ~140 s. The 2,000 s probably includes post-burn and descent purging. The ~2 g/s rate
  comes from the slope, so it does not depend on which reading is right. The *burn-only* IPS
  total does depend on it.
- The interface pressures are slightly odd against their regulator set points: the spin-start
  spike of ~800 psia exceeds its 750 psia regulator. They are reported as given.
- The helium-to-propellant ratio and the ullage-temperature figures in Key results 2-3 are
  derived here from the paper's own numbers, not stated by the paper.
- The paper has no seal geometry, leakage model or GN2 alternative, so the IPS purge figure is
  one total flow for one single-shaft LOX/RP-1 pump. Trust its order of magnitude (grams per
  second), not a scaling.
