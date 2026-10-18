# NASA CR-190786 — An RL10A-3-3A Rocket Engine Model Using the Rocket Engine Transient Simulator (ROCETS) Software

## Identity

Michael Binder (Sverdrup Technology, Inc., NASA Lewis Research Center Group, Brook Park, Ohio),
*An RL10A-3-3A Rocket Engine Model Using the Rocket Engine Transient Simulator (ROCETS)
Software*, **NASA CR-190786**, July 1993, Final Contractor Report. Contract NAS3-25266,
WU-593-12-00, performing-org report E-9585. Project manager Frank D. Berkopec (NASA Lewis
Propulsion Technology Division). NTRS accession 19950017370; renamed from its numeric NTRS
filename on 2026-10-18.

File: `literature/NASA CR-190786 - An RL10A-3-3A Rocket Engine Model Using ROCETS.pdf`. It has
**16 PDF leaves**:
- leaf 0 cover, leaf 1 blank;
- leaves 2-12 = printed pp. 1-11 (**printed page = leaf − 1**);
- leaf 13 = SF-298 documentation page, leaf 14 mailer back cover, leaf 15 blank.

Tag: `[RL10-ROCETS]`.

## Character

This is a short (5 text pages + 7 table/figure pages) **system-model validation report**, not a
design report. NASA Lewis built a steady-state and a transient model of the RL10A-3-3A
in ROCETS, from Pratt & Whitney design data:
- performance maps;
- line volumes and resistances;
- heat-transfer correlations, supplied under contract (Ref. 2 = P&W FR-15876).

The report checks the steady-state model against **five P&W test-stand points** (Tables 1-5) and
the transient model against Atlas/Centaur **AC-69 flight telemetry** for the start (Figs. 4-7).

What it is best for:
- **The test-stand columns of Tables 1-5.** These are real measured RL10A-3-3A station
  pressures, the turbine-inlet (≈ jacket-outlet) H2 temperature, LOX pump speed, and pump
  inlet volumetric flows at five mixture ratios (MR 4.67-5.63) near rated thrust. They are the
  only RL10 *station* data in `claude_lit/`.
- **Fig. 1 / Fig. 2 flow-path topology:**
  - a calibrated orifice ahead of the jacket;
  - a five-volume jacket;
  - a cavitating venturi;
  - the turbine with a parallel bypass valve (FTBV);
  - the fuel shutoff valve and then the injector;
  - on the LOX side, the MRV and a LOX bypass valve in parallel.

What it does not give:
- tube count or geometry;
- heat flux;
- jacket-only dP;
- pump discharge temperatures;
- turbine efficiency, turbine pressure ratio or bypass fraction;
- c\*, expansion ratio or throat area.

The heat-transfer and turbomachinery maps are described but **not tabulated**.

Trust: the test columns are real P&W test data, but the report names no test, stand or date.
The ROCETS columns are model output, within 4 % of test, and should not be cited as engine data.

Text layer: good on pp. 1-5 (one word per line, but correct). Tables 1-5 (leaves 7-8) were
**read visually from 150-dpi renders**. The text layer garbles several digits, e.g. TP5
venturi inlet "609.78" where the page reads **809.78**. Figs. 1-7 (leaves 9-12) were also read
visually; curve values taken from them are approximate.

## Steady-state test data (Tables 1-5)

`[RL10-ROCETS Tables 1-5 pp.6-7]`. All pressures are static psia. The ROCETS column is the
model, and the error column is (ROCETS − test)/test. Thrust, MR and tank conditions are
**model inputs**: the model's FTBV and MRV areas are varied until the target thrust and MR are
reached `[p.3-4]`. They are presumably the test conditions, but the table does not say so
explicitly.

**Inputs:**

| Input | TP1 | TP2 | TP3 | TP4 | TP5 |
|---|---|---|---|---|---|
| Thrust, lbf (kN) | 16,603 (73.85) | 16,588 (73.79) | 16,458 (73.21) | 16,376 (72.84) | 16,555 (73.64) |
| Inlet O/F (MR) | 5.63 | 5.55 | 4.99 | 4.67 | 5.42 |
| Fuel tank P, psia (kPa) | 27.00 (186.2) | 27.00 (186.2) | 26.50 (182.7) | 26.20 (180.6) | 27.00 (186.2) |
| Fuel tank T, °R (K) | 38.60 (21.44) | 38.60 (21.44) | 38.50 (21.39) | 38.50 (21.39) | 38.50 (21.39) |
| LOX tank P, psia (kPa) | 35.80 (246.8) | 35.30 (243.4) | 35.80 (246.8) | 36.00 (248.2) | 35.50 (244.8) |
| LOX tank T, °R (K) | 174.70 (97.06) | 174.70 | 174.70 | 174.70 | 174.70 |

**Measured test values** (ROCETS error in brackets):

| Output (test data) | TP1 | TP2 | TP3 | TP4 | TP5 |
|---|---|---|---|---|---|
| Fuel pump discharge P, psia (MPa) | 1061.40 (7.318) [−2.65 %] | 1068.90 (7.370) [−2.80 %] | 1112.50 (7.670) [−2.61 %] | 1143.10 (7.881) [−2.81 %] | 1076.90 (7.425) [−2.76 %] |
| Fuel pump inlet vol. flow, gpm | 580.60 [+1.08 %] | 588.90 [+0.77 %] | 634.90 [+0.89 %] | 667.40 [+0.91 %] | 598.40 [+0.67 %] |
| Venturi inlet P (≈ jacket outlet), psia (MPa) | 800.45 (5.519) [−0.06 %] | 808.56 (5.575) [−0.57 %] | 839.53 (5.788) [−0.40 %] | 860.85 (5.935) [−0.71 %] | 817.10 (5.634) [−0.90 %] |
| **Turbine inlet T, °R (K)** | **439.32 (244.1)** [−3.24 %] | 432.92 (240.5) [−3.13 %] | 390.35 (216.9) [−2.07 %] | **368.93 (205.0)** [−2.48 %] | 420.63 (233.7) [−2.25 %] |
| Fuel injector manifold P, psia (MPa) | 534.19 (3.683) [−1.17 %] | 535.67 (3.693) [−1.27 %] | 540.20 (3.725) [−0.69 %] | 543.65 (3.748) [−0.46 %] | 537.03 (3.703) [−1.28 %] |
| LOX pump discharge P, psia (MPa) | 613.80 (4.232) [−2.54 %] | 619.10 (4.269) [−2.78 %] | 647.70 (4.466) [−2.08 %] | 665.90 (4.591) [−1.76 %] | 624.50 (4.306) [−2.72 %] |
| LOX pump shaft speed, rpm | 12,697.0 [−0.94 %] | 12,747.0 [−1.02 %] | 13,040.1 [−0.91 %] | 13,236.5 [−0.94 %] | 12,798.0 [−1.01 %] |
| LOX pump inlet vol. flow, gpm | 205.82 [+0.57 %] | 205.59 [+0.24 %] | 199.61 [+0.43 %] | 196.34 [+0.42 %] | 204.33 [+0.20 %] |
| LOX injector plenum P, psia (MPa) | 532.50 (3.671) [−1.24 %] | 532.67 (3.673) [−1.27 %] | 531.50 (3.665) [−0.76 %] | 530.93 (3.661) [−0.48 %] | 532.04 (3.668) [−1.17 %] |
| **Chamber P (inj. face static), psia (MPa)** | **472.35 (3.257)** [−0.77 %] | 472.96 (3.261) [−0.79 %] | 475.48 (3.278) [−0.36 %] | 476.80 (3.287) [−0.08 %] | 473.03 (3.261) [−0.67 %] |

### Derived from the test columns (this note's arithmetic, not in the source)

Psia differences between stations are converted at 6894.757 Pa/psi. Mass flows use
**saturated-liquid density at the TANK temperature**, from the project's own CoolProp table
(`engine_designer/physics/property_data/saturation_properties.json`): LH2 69.44 kg/m³ at
21.44 K, LOX 1106.3 kg/m³ at 97.06 K. This neglects suction-line heat leak and pump-inlet
pressure.
- **Validation check:** the flow ratio derived this way reproduces the input MR within 0.4 %
  (5.65 / 5.56 / 5.01 / 4.69 / 5.44 against 5.63 / 5.55 / 4.99 / 4.67 / 5.42). So the
  densities are adequate.
- **Topology:** per Fig. 1 / Fig. 2, the calibrated orifice and the coolant inlet manifold sit
  between the fuel-pump discharge and the jacket, and the venturi sits right after jacket
  volume 5. "Pump → venturi inlet" therefore spans orifice + inlet manifold + jacket.

| Derived quantity | TP1 | TP2 | TP3 | TP4 | TP5 |
|---|---|---|---|---|---|
| LH2 flow, kg/s (lbm/s) | 2.544 (5.61) | 2.580 (5.69) | 2.781 (6.13) | 2.924 (6.45) | 2.622 (5.78) |
| LOX flow, kg/s (lbm/s) | 14.37 (31.7) | 14.35 (31.6) | 13.93 (30.7) | 13.70 (30.2) | 14.26 (31.4) |
| Isp from thrust / total flow, s | ≈445.3 | ≈444.4 | ≈446.7 | ≈446.8 | ≈444.8 |
| Fuel pump discharge / Pc | 2.247 | 2.260 | 2.340 | 2.397 | 2.277 |
| LOX pump discharge / Pc | 1.299 | 1.309 | 1.362 | 1.397 | 1.320 |
| **Pump discharge → venturi inlet dP (orifice + inlet manifold + jacket)**, psi (MPa) | **261.0 (1.80)** | 260.3 (1.80) | 273.0 (1.88) | 282.2 (1.95) | 259.8 (1.79) |
| same, / Pc | 0.552 | 0.550 | 0.574 | 0.592 | 0.549 |
| Venturi inlet → fuel injector manifold dP (venturi + turbine‖FTBV + line + shutoff valve), psi (MPa) | 266.3 (1.84) | 272.9 (1.88) | 299.3 (2.06) | 317.2 (2.19) | 280.1 (1.93) |
| Upper bound on turbine total PR (venturi inlet / fuel inj. manifold) | ≤1.50 | ≤1.51 | ≤1.55 | ≤1.58 | ≤1.52 |
| Fuel injector dP (manifold − Pc), psi (MPa); / Pc | 61.8 (0.426); 0.131 | 62.7 (0.432); 0.133 | 64.7 (0.446); 0.136 | 66.9 (0.461); 0.140 | 64.0 (0.441); 0.135 |
| LOX injector dP (plenum − Pc), psi (MPa); / Pc | 60.2 (0.415); 0.127 | 59.7 (0.412); 0.126 | 56.0 (0.386); 0.118 | 54.1 (0.373); 0.114 | 59.0 (0.407); 0.125 |
| LOX pump discharge → plenum dP (MRV ‖ LOX bypass + lines), psi (MPa) | 81.3 (0.56) | 86.4 (0.60) | 116.2 (0.80) | 135.0 (0.93) | 92.5 (0.64) |

The Isp row assumes the tank-density flows are the engine's whole consumption. The ~0.5 %
density uncertainty makes the 0.1-s differences meaningless. Its level agrees with the
source's "approximately 445 seconds" `[p.2]`.

## Key results

1. **Engine description** `[RL10-ROCETS p.2]`:
   - LOX/LH2 **expander cycle**: chamber heat into a regen jacket, and the heated H2 drives the
     turbine;
   - the turbine drives the fuel and LOX pumps **through a gearbox**;
   - rated **16,500 lbf (73,395 N)**, Isp ≈445 s;
   - fuel turbopump design speed **30,000 rpm**, LOX pump **12,000 rpm** (a 2.5:1 design
     ratio, derived here);
   - **Pc nominally 475 psia (3.28 MPa)**;
   - flows ≈6 lbm/s H2 and ≈30 lbm/s O2 at rated thrust.

   The -3-3A is "not intended to be throttled". Pc is set by turbine-bypass flow (FTBV) through a
   pneumatic servo that prevents start overshoot, and MR control is available for propellant
   utilization. It starts on **tank head plus jacket heat pickup, with no boost pumps**.
   `Engine_Configs/RL10_Config.cfg`'s RL10A-3-3A header (73.4 kN vac, Pc 3.28 MPa, 444.4 s vac,
   MR 5.0, eps 61) is consistent with this.
2. **Flow-path topology** `[RL10-ROCETS Fig. 1 p.8; Fig. 2 p.9]`, read visually.

   *Fuel side:*
   - Two-stage fuel pump. An **interstage cooldown valve** and a **discharge cooldown valve**
     vent to vacuum during chilldown.
   - The **calibrated orifice** is a fixed restriction between the pump and the jacket.
   - Coolant inlet manifold → **jacket, lumped as 5 volume/resistance pairs**, entering at the
     nozzle end → **cavitating venturi** → turbine inlet volume.
   - Fuel turbine and **FTBV in parallel** → turbine discharge volume → resistance → **fuel
     shutoff valve** → fuel injector manifold → injector.

   *LOX side:* LOX pump → cutwater resistance → **MRV and LOX bypass valve in parallel** →
   LOX injector plenum → injector.

   Pump-discharge "cutwater" resistances are modelled explicitly on every pump.
3. **Measured RL10A-3-3A station data at five MRs** (table above), all near 16,400-16,600 lbf
   and Pc 472-477 psia `[Tables 1-5 pp.6-7]`. Headline values at the MR 5.63 point:
   - **fuel pump discharge 1,061 psia (7.32 MPa) = 2.25 × Pc**;
   - venturi inlet (≈ jacket exit) **800 psia (5.52 MPa)**;
   - **turbine inlet 244 K (439 °R)**;
   - fuel injector manifold 534 psia;
   - LOX pump discharge 614 psia (1.30 × Pc);
   - LOX pump 12,697 rpm.

   As MR falls from 5.63 to 4.67:
   - turbine inlet T falls to **205 K**, since more H2 picks up the same jacket heat;
   - fuel flow rises ~15 %;
   - LOX pump speed rises ~4 %;
   - every pump discharge pressure rises.
4. **Jacket dP upper bound** (derived; see the table). Fuel pump discharge minus venturi
   inlet is **1.79-1.95 MPa (260-282 psi, 0.55-0.59 × Pc)**, and that span also includes the
   calibrated orifice and coolant inlet manifold. The RL10A-3-3A jacket-alone dP is therefore
   **≤ ~1.8-1.95 MPa** `[derived from Tables 1-5 pp.6-7 + Fig. 1 p.8]`. This matches in
   magnitude `[Sutton Table 8-1]`'s RL10B-2 jacket dP of 253 psi (1.74 MPa) at Pc 640 psia.
5. **Turbine pressure ratio bound** (derived). Venturi inlet / fuel injector manifold is
   **≤1.50-1.58**, and that span also includes the cavitating venturi, line and shutoff-valve
   losses. So the true turbine PR is below ~1.5 at the -3-3A rating. This is consistent with
   `[SP-8110 Table I p.10]` / `[SP-8107 Table III]`'s RL10 A3-3 PR 1.42 (η_T-S 74.0 %, 2-stage
   pressure-compounded, Tt1 −88 °F (206 K) / −106 °F, Pt1 708 psia at Pc 400 psia).
6. **Injector stiffness** (derived) at rated conditions: fuel dP **13-14 % of Pc** and LOX dP
   **11-13 % of Pc**, on a gas-H2 / liquid-LOX coaxial injector (the injector type is not
   stated here; RL10 lineage, see `[RPE-J2]`). Both sit just under the 15-20 % "rule" in
   `topics/05-injectors.md`. Fuel dP rises and LOX dP falls as MR drops.
7. **Model method** `[p.2-3]`:
   - **Pumps:** head-coefficient / efficiency vs flow-coefficient maps from test (Shepherd).
     The LOX pump uses a 5th-order polynomial fit, with leakage from the pump stages to the
     gearbox included.
   - **Turbine:** an efficiency vs velocity-ratio map, with turbine dP modelled as a
     compressible orifice.
   - **Valves and ducts:** fluid resistances.
   - **Volumes:** each carries density and internal energy as states.
   - **Solution:** a Newton-Raphson Jacobian solve.
   - **Steady-state heat transfer:** an **empirical P&W map of heat-transfer rate vs Pc and
     MR** (not reproduced).
   - **Transient heat transfer:** a **5-node jacket model** with **Bartz gas-side and Colburn
     coolant-side** coefficients plus wall thermal capacity.
8. **Accuracy** `[p.3; Fig. 3 p.10]`. The steady-state model is within **4 %** of test on
   every measured parameter. Of the 50 parameter-points, 52 % are within 1 %, 20 % within
   1-2 %, 24 % within 2-3 % and 4 % within 3-4 %; these shares were checked against the
   tables here. The worst parameter is the turbine inlet temperature (TP1/TP2 −3.2 %). The
   **transient model driven to steady state matches within 4 % except turbine inlet
   temperature, within 7 %**. The author calls the theoretical Bartz/Colburn jacket model
   less accurate than the empirical map, and Lewis was working to improve it `[p.4]`.

   For `engine_designer`, this is a real-world measure of how far a Bartz + Colburn
   five-node expander jacket lands on turbine inlet temperature even with P&W's own
   geometry: about 7 %.
9. **Start transient** `[p.3-4; Figs. 4-7 p.11]`. The ROCETS curve parallels AC-69 flight data
   but accelerates **~0.3-0.4 s late**.
   - Flight Pc jumps at ~1.85 s after MES and reaches ~450-470 psia by ~2.1 s (FTBV servo dip
     circled). ROCETS rises at ~2.25 s. Both settle near ~480 psia by ~3 s.
   - LOX pump speed: flight ≈12,500-13,500 rpm (noisy signal) by ~2.1 s.
   - LOX pump discharge settles ~650 psia; venturi inlet settles ~850 psia.

   These are visual reads of the curves. Mechanisms:
   - For the first **0.30 s** there is **0.5-1.5 lbm/s** through the pumps at fuel-pump speed
     **< 2,000 rpm**. The pump *dissipates* energy, so a pressure drop forms across it, and the
     empirical maps do not capture this.
   - Cavitation loss at the discharge cutwaters is modelled as simple resistances.
   - H2 vaporization in the interstage cooldown valve vent dominates bootstrap timing.
   - The missing FTBV servo dynamics explain the curve-shape mismatch near full thrust.

   There is no throttled mainstage transient data for the engine.

## Section map

- p.1 (leaf 2) Abstract; Introduction (purpose, ROCETS background, P&W data source). Read.
- p.2 (leaf 3) Introduction cont.; Description of RL10A-3-3A Rocket Engine (thrust, Isp, rpm,
  Pc, flows, control); Description of RL10 Model in ROCETS (pump/turbine maps, heat-transfer
  approach). Read.
- p.3 (leaf 4) Model description cont. (transient 5-node Bartz/Colburn jacket; valves; states;
  Newton-Raphson); Steady-state model predictions vs test data; Start transient vs flight data.
  Read.
- p.4 (leaf 5) Discussion of Results (FTBV/MRV areas, transient heat-transfer accuracy, start
  sensitivities: cooldown valves, cutwater cavitation, low-speed pump dissipation); Concluding
  Remarks. Read.
- p.5 (leaf 6) References (6: Felder & Binder AIAA 91-3556; **P&W FR-15876 RL10A-3-3A design
  report, Jan 1982**; NASA CR-184099 ROCETS spec; Shepherd; Bartz 1957; Holman). Read.
- pp.6-7 (leaves 7-8) Tables 1-5, test points 1-5, ROCETS vs test. Read visually (150 dpi).
- p.8 (leaf 9) Fig. 1, RL10A-3-3A simplified schematic. Read visually.
- p.9 (leaf 10) Fig. 2, ROCETS model configuration (component/volume/resistance network). Read
  visually.
- p.10 (leaf 11) Fig. 3, error histogram. Read visually.
- p.11 (leaf 12) Figs. 4-7, Pc / venturi inlet P / LOX pump speed / LOX pump discharge P vs time
  from MES, ROCETS vs AC-69 flight. Read visually (approximate curve reads only).
- leaf 13 SF-298 (report numbers, contract, project manager). Read. Leaves 0, 1, 14, 15: cover,
  blanks and mailer.

## Caveats

- **Test-point provenance is thin.** The report gives no test stand, test number or date, and
  no measurement uncertainty. "Test data" are P&W test-stand values. The thrust and MR rows are
  model inputs; the report implies they are the test's own, but does not say so.
- **The station names are measurement locations, not component boundaries.** "Venturi inlet"
  is taken as ≈ jacket outlet from Fig. 1 / Fig. 2's topology. The pump → venturi dP is
  therefore an *upper bound* on jacket dP, because the calibrated orifice is inside that span
  (the orifice's own dP is not given). Likewise the turbine PR is an upper bound.
- **Missing quantities.** The source gives no turbine inlet *pressure*, turbine flow, FTBV
  bypass fraction or turbine efficiency. So `ETA_EXPANDER_TURBINE` (0.55) cannot be
  back-solved from this source alone. `[SP-8110]` / `[SP-8107]`'s 74 % (RL10 A3-3, T-S) remains
  the only RL10 turbine-efficiency figure in `claude_lit/`.
- **No heat transfer data.** There is no jacket heat load, throat heat flux, tube count/geometry
  or wall temperature. The steady-state jacket heat is an empirical P&W map that is not
  reproduced here. The turbine-inlet temperature is the only thermal measurement.
- **No pump temperatures.** There are no pump discharge temperatures and no jacket-inlet coolant
  temperature (tank 21.4 K only).
- **No performance-split data.** There is no c\*, CF, throat area or expansion ratio. The Isp
  row in the derived table is this note's arithmetic, ±~1 %.
- **Flow derivation.** Mass flows use tank-temperature saturated density from the project's
  CoolProp table. They are validated by reproducing MR within 0.4 %, but they are derived
  values.
- **Variant.** This is the RL10A-3-3A (Pc ~475 psia). `[SP-8107]` / `[SP-8110]` /
  `[SP-8087]` rows are the earlier RL10A-3-3 at Pc 400 psia (SP-8087's "300 psia" row is older
  still), and Sutton's row is the RL10B-2 at 640 psia. Scale with care when combining them.
- **Figure reads.** The Fig. 4-7 values above are visual reads of small plots, good to roughly
  ±20 psia / ±0.1 s.
