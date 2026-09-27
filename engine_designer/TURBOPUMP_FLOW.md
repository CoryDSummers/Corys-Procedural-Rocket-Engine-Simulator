# Turbopump calculation flow

As of 2026-09-27: `main` with turbopump Rounds 0-2 and the tap-off accuracy round (PRs #21, #22).

This is a map of **what the turbopump maths does, in what order, and what feeds back into what**
inside one `EngineDesign.compute()` call. Boxes name **file · function** (paths under
`engine_designer/physics/` unless marked `gui/`). Line numbers are left out because they drift.
Each box also carries the one-line model it evaluates.

For the *numbers* (constants, tiers, sources) see `ASSUMPTIONS.md`. For the cooling side that
feeds the pumps, see `COOLING_AUDIT.md`. **Update this file whenever a turbopump round changes
the chain.**

Diagram legend (GitHub renders the Mermaid blocks):

| Shape / colour | Meaning |
|---|---|
| amber box | turbopump-relevant stage or function |
| diamond | a model switch or cycle branch |
| cylinder | a baked table or catalogue that is read |
| dashed arrow | a value fed back into the **next** pass or iteration |

Contents:
1. [Overview and outer loops](#1-overview-and-outer-loops)
2. [Suction and hydraulics inputs](#2-suction-and-hydraulics-inputs)
3. [Inside size_pump](#3-inside-size_pump)
4. [Cycle branches](#4-cycle-branches-the-power-balance)
5. [Final hardware sizing, pump heating, rollup](#5-final-hardware-sizing-pump-heating-rollup)
6. [Outputs](#6-outputs)
7. [Model switches](#7-model-switches)
8. [Loops and iterations](#8-loops-and-iterations)
9. [Known quirks found while tracing](#9-known-quirks-found-while-tracing)

---

## 1. Overview and outer loops

```mermaid
flowchart TD
    IN[/"EngineDesign inputs<br/>Pc, MR, thrust, cycle, pump sliders, materials"/]

    subgraph TC["compute() - thrust closure: open cycles rescale chamber flow, up to 6 iterations"]
        subgraph CP["_compute_passes - pass 1, optional pass 2, up to 3 coolant-inlet passes"]
            subgraph PASS["_compute_pass - one pipeline pass, values shared on PassState s"]
                S1["1 combustion_setup<br/>propellant densities - picks up last pass line loss"]
                S2["2 nozzle_performance<br/>chamber mdot = F x scale / (Isp x g0)"]
                S3["3 geometry_stage.contour"]
                S4["4 injector_and_cooling_routing<br/>injector dP, Pc feed, feed line loss"]
                S5["5 cooling_stage.thermal<br/>jacket dP, wall heat, coolant inlet T"]
                S6["6 suction_stage.pump_suction<br/>NPSH available per leg"]
                S7["7 suction_stage.pump_hydraulics<br/>design intent to meanline specs"]
                S8["8 feed_stage.turbomachinery_cycle<br/>pump dP, efficiencies, turbine flow, thrust"]
                S9["9 geometry_stage.chamber_detail<br/>expander cycle completed here"]
                S10["10-17 thermal reporting, nozzle extension, regen Isp,<br/>manifolds, margins, stability, structure, hatbands"]
                S18["18 suction_stage.pump_heating<br/>pump outlet temperatures"]
                S19["19 turbomachinery_stage.turbopump_and_plumbing<br/>hardware sizing, mass, ports, plumbing"]
                S20["20 rollup_stage.burn_time_and_mass<br/>electric rebuild, dry mass"]
                S21["21 rollup_stage.checks_and_result"]
                S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7 --> S8 --> S9 --> S10 --> S18 --> S19 --> S20 --> S21
            end
        end
    end

    IN --> S1
    S21 --> R[/"result dict"/]
    S18 -. "fuel pump outlet T becomes jacket inlet T" .-> S5
    S19 -. "line_loss_computed from pump-connected runs" .-> S1
    S8 -. "film_carry when exhaust is nozzle-injected" .-> S5
    R -. "thrust error: scale chamber mdot" .-> S2

    class S6,S7,S8,S9,S18,S19,S20 tp
    classDef tp fill:#fde68a,stroke:#b45309,color:#1f2937
```

**What triggers pass 2** (`EngineDesign._compute_passes`), in any combination:
- a plumbing run connected to a pump port produced `line_loss_computed`. It is consumed by
  `combustion_setup` and, for the exhaust duct, by `feed_stage._exhaust_back_pressure`;
- nozzle-injected turbine exhaust produced a `film_carry`, consumed by `cooling_stage.thermal`;
- `coolant_inlet_model = "computed"` with `pump_model = "meanline"`, where the fuel-pump outlet
  differs from the jacket inlet used by more than `COOLANT_INLET_TOLERANCE_K` (0.5 K).

If the coolant inlet triggered it, up to 3 more passes run. Each is under-relaxed as
T = ½(T + T_new), and the loop stops once both the inlet and the film flow are stable.

---

## 2. Suction and hydraulics inputs

Stages 6 and 7 (`design/suction_stage.py`). These produce the pump **inlet pressure** that every
pump dP starts from, the **boost-pump drive head** charged to pump power, and the per-leg specs
`size_pump` is later called with.

```mermaid
flowchart TD
    SL["_legacy: inlet = TANK_HEAD_PA, no boost, no suction dict"]
    INT["turbopump_intent.from_design / intent_parameters<br/>4 sliders + inducer_mode, diffuser_type, pump_type<br/>to Ns target, psi, beta2, tip-speed fraction, cavitation number k"]
    SM{"suction_model = legacy<br/>or pressure-fed?"}
    SL --> INT --> SM
    SM -- "yes" --> OUTL["stop: size_pump uses the legacy Nss-class suction"]
    SM -- "no, per leg" --> T["inlet temperature: user value, else NBP for a cryogen, else 293 K"]
    SAT[("saturation_properties.json<br/>thermo_tables.saturation")]
    SAT --> PV["vapour pressure p_v"]
    T --> PV
    PV --> PIN["p_inlet = p_tank + rho g a h - suction line loss<br/>p_tank 0 means TANK_HEAD_PA - loss from plumbing.suction_line_loss_pa"]
    PIN --> BQ{"boost_pump_rise_*_pa > 0?"}
    BQ -- "yes" --> BP["inducer.make_spec + size_pump for the boost stage<br/>drive head = rise / (eta_boost x BOOST_DRIVE_EFFICIENCY)"]
    BP --> BD[/"s.boost_drive_dp: added to pump POWER, never discharge"/]
    BQ -- "no" --> MI
    BP --> MI["main pump inlet = p_inlet + boost rise"]
    MI --> NP["NPSH available = (main inlet - p_v) / (rho g)<br/>npsh_available_*_ft > 0 overrides it"]
    NP --> SPEC["inducer.make_spec: SuctionSpec<br/>Brumfield Ss, TSH scaled by vapour pressure, Z floor"]
    SPEC --> SK[/"s._suction_kw: suction_fuel / suction_ox"/]
    MI --> PI[/"s.pump_inlet_pa"/]

    HM{"pump_model = meanline?"}
    INT --> HM
    HM -- "yes" --> HS["pump_hydraulics: pump_meanline.HydraulicsSpec per leg<br/>Ns target, psi, beta2, tip fraction, diffuser, pump type, viscosity"]
    HS --> SK
    HM -- "no: correlation" --> SKN["no HydraulicsSpec: the Ns-bell efficiency path"]

    class INT,BP,SPEC,HS,NP tp
    classDef tp fill:#fde68a,stroke:#b45309,color:#1f2937
```

---

## 3. Inside size_pump

`turbopump_sizing.size_pump` is called for every pump, many times per pass:
- the power balance (§4), via `size_pump_pair`;
- each staged-solver trial;
- the boost pump;
- the final hardware sizing (§5).

It is exact-arg cached on the meanline side (`pump_meanline._exact_cache`).

```mermaid
flowchart TD
    IN[/"mdot, dP, rho, material, SuctionSpec, HydraulicsSpec, shaft rpm cap"/]
    IN --> QH["Q = mdot / rho, H = dP / (rho g)"]
    QH --> ST["stage count = max(ceil(H / 6000 ft), tip-speed stages), cap 8<br/>axial: pump_meanline.axial_stage_count - pump_stages_* forces it"]
    ST --> SQ["per stage: u_tip = sqrt(g H_stage / psi)<br/>rpm = Ns_target x H_stage^0.75 / Q^0.5"]
    SQ --> SUC{"SuctionSpec given?<br/>(suction_model computed)"}
    SUC -- "yes" --> CAP1["NPSH required = inducer.npsh_required_ft<br/>= max((N sqrt(Q) / Ss)^(4/3) - TSH, Z floor)<br/>rpm = min(rpm, inducer.suction_limited_rpm)"]
    SUC -- "no: legacy" --> CAP2["Nss class by density<br/>enforce_suction_limit: add stages until NPSHr is within 3x anchor<br/>npsh_available_*_ft caps rpm"]
    CAP1 --> SH
    CAP2 --> SH
    SH["shared-shaft cap: rpm = min(rpm, shaft_rpm_cap)"]
    SH --> D2["D2 = 60 u_tip / (pi rpm)<br/>tip-speed margin vs the rotor material"]
    D2 --> EC["eta = turbopump_efficiency.pump_efficiency<br/>Ns bell x size penalty x build quality"]
    EC --> HY{"HydraulicsSpec given?<br/>(pump_model meanline)"}
    HY -- "centrifugal" --> ML["pump_meanline.design_centrifugal<br/>SP-8109 eq. 17 slip, blade count, b2, loss build-up"]
    HY -- "axial" --> AX["pump_meanline.design_axial<br/>SP-8125 stage triangles"]
    HY -- "no" --> OUT
    ML --> OUT
    AX --> OUT
    OUT[/"pump dict: rpm, stages, D2, u_tip, eta, NPSHr, suction_limited, meanline"/]

    PAIR["size_pump_pair: size both pumps -<br/>single shaft: re-size the faster pump at the slower rpm"]
    PAIR --> IN

    class CAP1,ML,AX,EC,PAIR tp
    classDef tp fill:#fde68a,stroke:#b45309,color:#1f2937
```

When the meanline runs, its `eta` replaces the correlation value, which is kept as
`eta_correlation`.

---

## 4. Cycle branches: the power balance

Stage 8, `design/feed_stage.turbomachinery_cycle`. Every turbopump cycle shares the same core:

```mermaid
flowchart TD
    SET["common setup<br/>GG_GAS_PROPERTIES[pair], build quality,<br/>effective_arrangement (single / dual / geared shaft), turbine staging"]
    DP["pump rise<br/>fuel dP = Pc feed + injector dP + jacket dP + line loss - pump inlet<br/>ox dP = Pc feed + injector dP + line loss - pump inlet"]
    DE["turbopump_sizing.derive_efficiencies<br/>size_pump_pair at CHAMBER mdot, dP + boost drive head<br/>power = sum mdot dP / (rho eta)<br/>c0 = sqrt(2 cp Tin (1 - PR^-(g-1)/g))<br/>open cycles: U/C0 picks staging, pitch capped by achievable speed<br/>eta_turb = turbopump_efficiency.turbine_efficiency"]
    SET --> CY{"cycle"}

    CY -- "gas generator" --> GG1["_exhaust_back_pressure<br/>turbine PR = min(22, 0.855 Pc / sonic back pressure)"]
    GG1 --> DP
    CY -- "tap-off" --> TO0{"tap_off.resolve_model<br/>auto: mixer for LOX/CH4, LOX/RP-1"}
    TO0 -- "mixer" --> TOM["tap_off.mixer_split<br/>hot tap at 0.890 Tc + cold pumped fuel to tap_off_tin_k (0 = 1000 K)<br/>dilution = cp_hot (T_hot - T_mix) / fuel enthalpy rise<br/>inlet 0.955 Pc, fuel-rich GG gas properties, pumped at mixed MR"]
    TO0 -- "legacy" --> TOL["chamber gas at min(0.55 Tc, 1150 K)<br/>inlet 0.855 Pc, not pumped"]
    TOM --> TOP["_exhaust_back_pressure, PR cap 18"]
    TOL --> TOP
    TOP --> DP
    DP --> DE

    DE --> GGR["cycles.gas_generator_result<br/>turbine flow = P / (cp Tin eta_t (1 - PR^-k))<br/>fixed point up to 12 iterations when the turbine flow is pumped"]
    GGR --> TOF["tap-off only: _finish_tap_off<br/>cyc.tap_off split + checklist rows"]
    GGR --> AE
    TOF --> AE["_apply_exhaust<br/>turbine_exhaust.exhaust_stream: exhaust Isp, film_carry"]

    CY -- "FRSC / ORSC / FFSC" --> SC["staged_combustion.solve_staged_power_balance<br/>pressure chain: turbine out = Pc feed + injector dP,<br/>turbine in = out x PR, discharge = preburner inlet + jacket + lines<br/>per side: scan PR 1.05-3.0 (80 pts), bisect 40x for available = required<br/>FFSC: 4 Gauss-Seidel sweeps - every trial calls derive_efficiencies"]
    SC --> SCR["staged_combustion_result<br/>+ power-balance, PR, preburner-temperature rows"]

    CY -- "expander" --> EX1["fuel dP = (Pc feed + injector dP) x 1.4 + jacket dP + line loss - inlet<br/>s.cyc left empty here"]
    EX1 --> EX2["stage 9 geometry_stage.chamber_detail<br/>derive_expander_efficiencies (pumps sized independently)<br/>expander.expander_result: power from regen wall heat, feasibility margin"]

    CY -- "electric pump" --> EL1["GG-style dP - derive_efficiencies with a dummy gas"]
    EL1 --> EL2["electric_pump_result<br/>electrical power = shaft / (eta_motor eta_inverter), battery + motor"]

    CY -- "pressure-fed" --> PF["pressure_fed_result: no turbopump - suction, hydraulics, heating skipped"]

    AE --> J["rejoin: mdot_total = chamber + turbine flow (open cycles)<br/>thrust = mdot_total x engine Isp x g0"]
    SCR --> J
    EX2 --> J
    EL2 --> J
    PF --> J

    GGT[("GG_GAS_PROPERTIES, coolant tables")]
    GGT --> SET
    GGT --> TOM

    class DE,GGR,TOM,SC,EX2,EL2 tp
    classDef tp fill:#fde68a,stroke:#b45309,color:#1f2937
```

Notes:
- The efficiency calls always use **dP + boost drive head**, so the boost pump's drive head is
  charged to pump power.
- The staged solver is the expensive path: each PR trial fully re-sizes both pumps, including
  the meanline.

---

## 5. Final hardware sizing, pump heating, rollup

Stages 18-20. The power balance fixed the efficiencies, powers and turbine flow. This part
builds the machine, its mass and its ports, then works out how hot the pumped propellant leaves.

```mermaid
flowchart TD
    PH["stage 18 suction_stage.pump_heating<br/>fuel: fuel_pump_outlet_k, 12-step isentropic march on the coolant table,<br/>h_out = h0 + dh_s / eta (boost stage first)<br/>LOX: dT = dP / (rho cp) x (1/eta - 1 + T beta)"]
    PH --> PHO[/"s.pump_heating: fuel outlet T feeds the next pass jacket inlet"/]

    DISP{"turbine inputs by cycle"}
    DISP -- "GG / tap-off / staged" --> T1["Tin = drive gas, turbine mdot = cyc gg_mdot_kgs, PR = cyc PR"]
    DISP -- "expander" --> T2["Tin = 250 K, turbine mdot = fuel mdot, PR = 1.4"]
    DISP -- "electric" --> T3["no turbine - motor body"]
    T1 --> STP
    T2 --> STP
    T3 --> STP
    STP["turbopump_sizing.size_turbopump<br/>1 size_pump_pair at the PUMPED flows, plain dP<br/>2 shaft rpm by arrangement (single = min, dual = 2 turbines, geared)<br/>3 split_turbine_work (series / parallel / FFSC per side)<br/>4 size_turbine: c0 = sqrt(2 dh), u = U/C0 x c0, D_mean = 60 u / (pi rpm)<br/>5 _assemble_bodies + geometry mass"]
    STP --> MASS["mass<br/>turbopump_mass_kg(power): specific-power trend<br/>x mass_modifier: gearbox, extra stages, intent mass ratio (clamp 0.7-1.6)<br/>render scale = (mass / geometry mass)^(1/3)"]
    MAT[("turbopump_materials: MATERIALS, BLADE_MATERIALS")]
    MAT --> CHK
    STP --> CHK["turbopump_material_suitability<br/>no blade alloy: one rule for disk and blades<br/>blade alloy set: blade limit from SP-8110 Fig. 30 + disk at 0.878 Tin<br/>bearing_suitability: shaft d from torque, DN = rpm x bore"]
    CHK --> SC2["suction_checks, hydraulics_checks<br/>NPSH, temperature, boost, head curve, impeller outlet, axial stall"]
    STP --> TEH["turbine_exhaust.size_hardware (open cycles)<br/>duct, scroll, exhaust nozzle, HX"]
    STP --> PORTS["geometry3d.turbopump_ports<br/>pump inlet / discharge / turbine exhaust hook points"]
    PORTS --> PL["plumbing runs, incl. the default exhaust duct<br/>plumbing.run_pressure_loss_pa"]
    PL --> LLC[/"line_loss_computed: used by the next pass"/]
    MASS --> RU["stage 20 rollup_stage.burn_time_and_mass<br/>electric: battery + motor rebuilt at the rated burn time<br/>dry mass += turbopump + battery/motor + exhaust hardware"]
    TEH --> RU

    class PH,STP,MASS,CHK,SC2,RU tp
    classDef tp fill:#fde68a,stroke:#b45309,color:#1f2937
```

The reported pump and turbine efficiencies are the **power-balance** values from §4. The
`size_turbopump` re-size is used for geometry, rpm and ports (see quirk 1).

---

## 6. Outputs

```mermaid
flowchart LR
    subgraph ROWS["checklist rows (warn, don't block)"]
        R1["turbomachinery_cycle<br/>GG flow fraction, tap-off drive gas, tap-off Tin vs practice,<br/>staged power balance / PR / preburner T, expander feasibility,<br/>turbine PR and exhaust temperature"]
        R2["suction_checks / hydraulics_checks<br/>propellant temperature, NPSH, boost, head curve, impeller outlet"]
        R3["size_turbopump warnings<br/>tip speed, material temperature, bearing DN"]
        R4["tubes_and_hatbands: feed dP plausibility<br/>plumbing: drawn feed-line loss"]
    end
    subgraph KEYS["result keys"]
        K1["cycle_result: turbopump powers, gg_mdot_kgs, tap_off, preburner_sides, expander, battery"]
        K2["turbopump_sizing: pumps, turbines, bodies, mass, efficiencies"]
        K3["suction, pump_inlet_pa, pump_discharge_*_pa, pump_intent, pump_heating"]
        K4["coolant_inlet_t_k / _source, line_loss_*, thrust_closure_scale,<br/>coolant_inlet_residual_k, line_loss_residual_pa, turbine_exhaust"]
        K5["turbopump_ports, turbine_exhaust_hardware"]
    end
    subgraph GUI["gui/ consumers"]
        G1["app.py Turbopump details text"]
        G2["turbopump_detail.py Turbopump Detail tab"]
        G3["turbopump_diagram.py systems diagram"]
        G4["mesh_builder.py 3D preview, shape_lab_geometry.py Shape Lab"]
    end
    K1 --> G1
    K2 --> G1
    K3 --> G1
    K4 --> G1
    K2 --> G2
    K3 --> G2
    K1 --> G3
    K2 --> G3
    K2 --> G4
    K5 --> G4
```

The turbopump mass rolls into `computed_dry_mass_kg`. `structure_stage.tubes_and_hatbands` first
sets a provisional value, which `turbopump_and_plumbing` replaces.

---

## 7. Model switches

| Field | Values (default first) | What it changes | Where (§) |
|---|---|---|---|
| `suction_model` | computed / legacy | computed: tank → line → boost → NPSHa, inducer NPSHr caps rpm, pump heating on. Legacy: `TANK_HEAD_PA` inlet, Nss class, no boost, no heating (so no computed coolant inlet) | 2, 3, 5 |
| `pump_model` | meanline / correlation | meanline: `HydraulicsSpec`, meanline efficiency, intent mass ratio, computed coolant inlet possible. Correlation: Ns-bell efficiency (the Round 1 path) | 2, 3, 1 |
| `pump_type_fuel/ox` | auto (= centrifugal) / centrifugal / axial | axial: scaled Ns target and psi, `axial_stage_count`, `design_axial`, axial stall row | 3 |
| `pump_priority`, `pump_head_curve`, `suction_aggressiveness`, `tip_speed_aggressiveness` | −1 … +1, 0 = neutral | Ns target, psi, beta2, tip-speed fraction, cavitation number | 2 |
| `inducer_mode`, `diffuser_type` | auto / on / off; auto / volute / vaned | inducer off = the no-inducer Ss (`SS_NO_INDUCER`); volute vs vaned diffuser losses | 2, 3 |
| `tap_off_model` | auto / mixer / legacy | auto = mixer for LOX/CH4 + LOX/RP-1, legacy otherwise. Mixer: 1,000 K fuel-rich gas, 0.955 Pc, pumped dilution | 4 |
| `tap_off_tin_k` | 0 = 1,000 K | mixer turbine inlet temperature (legacy: overrides the 0.55 Tc / 1150 K rule) | 4 |
| `coolant_inlet_model` | computed / table | computed: fuel pump outlet T becomes the jacket inlet (extra passes) | 1, 5 |
| `turbine_staging` | auto / a named staging (e.g. single_impulse, velocity_compounded_2row) | open cycles: auto staging from the achievable U/C0; closed cycles: the rule-based staging | 4 |
| `turbopump_arrangement` | auto / single_shaft / dual_shaft / geared | shared-shaft rpm cap, number of turbines, work split, gearbox mass | 3, 4, 5 |
| `turbine_exhaust_mode` | overboard_duct / aspirator / nozzle_injection | turbine back pressure (PR), exhaust Isp, film carry (pass 2) | 1, 4 |
| `turbine_blade_material_key` | "" = same as turbopump material | splits the temperature check into blade + disk | 5 |
| `eta_pump_fuel/ox`, `pump_stages_fuel/ox`, `enforce_suction_limit`, `npsh_available_*_ft` | 0 = derived | pin the pump efficiency / stage count; legacy suction options; NPSHa override | 2, 3, 4 |

---

## 8. Loops and iterations

Listed innermost first.

| Loop | Where | Converges on | Cap / tolerance |
|---|---|---|---|
| Legacy suction stage-add | `size_pump` (legacy + `enforce_suction_limit`) | NPSHr within 3× the anchor | 8 stages |
| Shared-shaft re-size | `size_pump_pair` | both pumps at one rpm | one re-size |
| Pumped turbine flow | `cycles.gas_generator_result` | GG / mixer flow that is itself pumped | 12 iterations, 1e-6 relative (1 iteration if not pumped) |
| Staged PR search | `staged_combustion.solve_staged_power_balance` | PR where turbine power available = required | 80-point scan + 40 bisections per side; FFSC 4 sweeps |
| Pass 2 | `_compute_passes` | pump-connected line loss, exhaust film, coolant inlet | one pass; line loss only reports a residual after it |
| Coolant-inlet passes | `_compute_passes` | jacket inlet T = fuel pump outlet T, stable film flow | 3 more passes, 0.5 K, under-relaxed ½ |
| Thrust closure | `compute()` | chamber + exhaust thrust = target (open cycles) | 6 iterations, 1e-9 |

Worst case: 6 thrust iterations × 5 passes = 30 full pipeline passes. Staged-combustion designs
are the slow ones, because the PR search re-sizes the pumps at every trial.

---

## 9. Known quirks found while tracing

These are recorded here for a decision; they were **not** changed in this documentation round.

1. **Two different pump sizings.** `derive_efficiencies` sizes the pumps at the **chamber** flow
   with **dP + boost drive head**. `size_turbopump` re-sizes them at the **pumped** flow (which
   includes the GG / mixer draw) with **plain dP**. So the drawn machine's rpm and D2 are not
   exactly the machine that set the efficiencies used in the power balance.
2. **The expander efficiency path ignores the shaft arrangement.** `derive_expander_efficiencies`
   sizes the pumps independently, while `size_turbopump` then applies the shared-shaft cap.
3. **Coolant-inlet pass count.** `COOLANT_INLET_MAX_EXTRA_PASSES = 2` is commented "beyond the
   first corrective pass", but the loop is `range(2 + 1)`, which allows 3.
4. **Stale docstring.** `derive_efficiencies` says "a short back-substitution (<=3 passes)", but
   the code runs a single pass.
5. **The pitchline cap only reaches the fuel turbine.** `size_turbopump` passes
   `u_pitch_max_m_s` to the fuel turbine only, so a dual-shaft ox turbine is uncapped.
