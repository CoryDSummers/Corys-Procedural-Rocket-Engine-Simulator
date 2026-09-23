# 15 — Transients and controls

## Scope

Engine start and shutdown sequencing, start-energy systems, shutdown water-hammer, throttle
response, and thrust / mixture-ratio control. Feeds `engine_designer/physics/ignition.py`,
`controller_tech.py`, `throttle.py`, and the export-time control fields.

## Key relations

**Turbopump time constant** `[SP-8107 eq. 15]`:

    τ ∝ I · N / Tq          I = rotating mass moment of inertia, N = design speed,
                            Tq = design shaft torque

Engine thrust buildup follows turbopump speed buildup; τ measures the response rate. Reduce
`I` (lighter rotor) or raise `Tq` (more turbine torque) → faster start.

**Shutdown surge (water-hammer)** `[SP-8107 §2.3.2.3]`: closing the main valve while the
pump decelerates produces an inlet pressure surge analogous to water hammer in a conduit.
Magnitude depends on propellant compressibility, inlet-line diameter & length, valve closure
rate, pump-flow decay rate, and line-material modulus. Surges of several hundred psi; the
pump inlet is usually the critical structure.

## Empirical correlations & typical values

**Start-energy systems** `[SP-8107 §2.2.6, §2.3.2.1, Table I]`:

| Method | Behaviour | Examples |
|---|---|---|
| Solid-propellant start cartridge | high-pressure high-energy gas rapidly accelerates the pumps; minimises the influence of turbopump inertia, head/flow characteristic and NPSH | H-1, MB-3, MA-5, YLR87 |
| **Tank-head start** | uses only vehicle-tank pressure to feed the GG initially; turbopump characteristics (inertia, head/flow stall, NPSH) matter a lot; slow | F-1, RL10, SSME |
| Pressurised-gas start tank | stored gas spins the turbine | J-2 (after tank-head start was abandoned) |
| Liquid-propellant (monopropellant) start tank | | A-7, LR87/LR91 |

**Tank-head-start failure mode** `[SP-8107 §2.3.2.1]`: the J-2 was originally tank-head
start. Simulation and test showed the fuel pump encountered the **stall discontinuity in its
head/flow curve**; stall dropped Q/N further; when **Q/N fell below ~⅓ of the design value,
hydrogen vaporised in the pump** → total loss of discharge pressure and fuel flow. Fix:
switch to a pressurised-gas start system.

**Ground vs altitude start** `[SP-8107 §2.3.2.1]`: at ground level, atmospheric pressure
lowers the turbine pressure ratio at low power → less torque → slower start. "A **10 %
increase in nozzle area or turbine flow may reduce start time as much as 50 %**." A hot-gas
valve (open at low power, restricting at mainstage) in series with the turbine is a positive
start-time reducer.

**Shutdown sequencing** `[SP-8107 §2.3.2.3]`: cut turbine power **first**, then close the
main propellant valves. A **500 ms cutoff is "fast" for a large engine**. LOX/RP-1 produces
higher surge pressures than LH2 (higher density → higher feed-system inertance). Valves
upstream of the pumps → pumps forced into deep cavitation, low surge (but surge upstream of
the valve to consider).

**Throttle response** `[SP-8107 §2.3.2.2]`, `[Sutton §8.5]`: response is set by the
turbopump time constant. **Throttling the hot turbine working fluid is slower than throttling
the liquid-line valves**; but liquid-line throttling forces the turbopump to a higher speed
(extra Δp) and can cause H2-pump flow-coefficient (vapor-formation) problems — mitigate by
recirculating H2 around the pump. Centrifugal pumps have ~2× the throttle range of axial
pumps; stable throttling to zero flow if Ns > ~2500; complete shutoff inadvisable except
< 10 s (trapped-propellant heating).

**Ignition systems** `[Huzel §4.7]`, `[SP-8081 §2.1.3.1]`:
- TEA-TEB slug, spark torch/plug, hypergolic self-ignition, single-shot pyrotechnic squib,
  catalytic (monopropellant).
- Most bipropellants do not autoignite → need an external energy source. Pyrotechnic
  cartridges usually doubled for redundancy; spark plugs where chilldown/restart is required
  (J-2). **LH2 is harder to ignite than RP-1** (spontaneous ignition temp ~1000 °F / 811 K;
  RP-1 ignites with GOX at room temperature).
- Best igniter location: within ~1 in (2.5 cm) of the injector face, where both propellants
  arrive simultaneously.
- Arrival sequence matters: prevent accumulation of unburned propellant before ignition
  (destructive pressure surge on light); maintain a fuel-rich mixture during shutoff to
  avoid chamber burnout `[Huzel §4.5 p.122]`. Minimise feed-line and manifold volume between
  valves and injector face to sharpen sequencing.

**Control points** `[SP-8107 §2.3.1.3]`:
- Most engines: **open-loop** turbopump power control — calibration orifices in the GG feed
  lines (J-2, F-1, H-1) or a pressure regulator on GG oxidizer flow (MA-5, MB-3).
- RL10: **closed-loop** thrust control — senses Pc, adjusts a turbine bypass valve.
- Closed-loop MR control: via the main propellant valves (MA-5 sustainer) or a pump-bypass
  valve (J-2 oxidizer-pump bypass).
- Orifice-in-GG-line + turbine-bypass control is **unsuitable for high-pressure staged
  combustion** (wide pump-discharge-pressure swings from the series arrangement).
- Component-tolerance effects are combined **root-sum-square**, not worst-case
  `[SP-8107 §2.3.1.2]`.

**Real demonstrated throttle ratios by engine/method — the first dense catalog in this
reference set** `[Casiano-Throttling]`, a comprehensive AIAA survey of essentially every US
(+ some Russian) throttleable LRE program: neither this file nor `topics/05-injectors.md`
previously had more than isolated single numbers (LMDE 10:1). Real flight/flight-heritage
anchors: **LMDE (Apollo descent engine) 10:1** (variable-area pintle + separate cavitating
venturis for MR control, >2800 tests incl. 31 bomb tests, no acoustic modes excited); **CECE
(modified RL10, 2005-2008) 13:1**, 5032s total run time, the deepest-throttled real
flight-heritage cryogenic pump-fed engine in the survey; **SSME throttled to 17% rated power
(6.4:1 from 100%)** in a 1997 X-33-support ground test with no instability at any level
tested — the binding constraint was **HPFTP pump-stall margin, not combustion stability**,
MR held fixed 3-4 to preserve that margin; **RD-170/171 throttles to 56% of max thrust,
RD-180 to 40%** (see `topics/08-engine-cycles.md`). Research/demonstrator (non-flight)
anchors, deeper but less representative of production hardware: dual-manifold F2/H2 study
12:1 subscale/29:1 full-scale; Bendix gas-injection study 35:1 (N2) /50:1 (He, considered
achievable); PWM continuous+pulse combined 100:1; a 1967 aerospike+bell multi-chamber
concept ~81:1 aggregate (9:1 × 9:1, two independently-throttled chambers). **Chug-
suppression by gas injection is small and quantified**: GHe at 0.4% of LOX weight flow, or
GOX at 4%, eliminated oxygen-boiling-driven chug on the 1964 RL10A-1 study; general rule
"gas injection flow rates for stabilization are generally <1% of propellant flow." A
**1-5 Hz fuel-side flow instability** on the same RL10A-1 study, tied to two-phase H2 in the
cooling jacket below 33% thrust, was stabilized by GHe/GH2 injection at ~20% of H2 weight
flow — a distinct low-frequency instability mode from the oxidizer-side chug above, both on
the same engine. Reducing Pc from 100% to 33% cost only ~3% Isp on RL10A-1; below 33% the
decay accelerated and chug (when present) cost an *additional* ~8%. See
`topics/05-injectors.md` for the accompanying injector-stiffness-vs-chug-onset data from the
same source.

**Number of ignitions in service** `[Huzel Ch. XI]`, real RO configs: 1 (expendable
boosters) to hundreds (long-life restartable upper-stage / RCS engines). Cryogenic restart
requires turbopump reconditioning (chilldown) because heat soaks back from the hot turbine
to the cold pump during coast `[SP-8107 §2.1.1.8]`.

## Caveats

- The tool does not model transients dynamically — ignition choice only sets export
  resources and a single-restart flag; controller tier only tunes export-time scalar fields.
- Start/shutdown numbers are engine-specific; the *mechanisms* (τ, stall, water-hammer,
  ground-vs-altitude torque) generalise.
- `[Casiano-Throttling]` is a survey/review paper restating ~118 underlying references, not
  primary data — treat as a reliable index of real program outcomes. Several of its deepest
  ratios (F2/H2 29:1, Bendix 35:1/50:1, aggregate 81:1) are small research/demonstrator
  engines explicitly framed by the paper as capability demonstrations, not flight heritage —
  LMDE (10:1), CECE (13:1), SSME (6.4:1), and RD-170/180/171 are the strongest flight/
  flight-program-relevant anchors. Explicitly US-centric; Russian deep-throttling
  swirl-injector work is only lightly covered.

## Implications for engine_designer

- **`controller_tech.py` `throttle_response_rate`** per tier (0.25–0.75): `[SP-8107
  §2.3.2.2]` confirms response is a real function of turbopump time constant τ ∝ I·N/Tq, and
  that liquid-line throttling responds faster than hot-gas throttling. The tier values are
  export-only scalars (ASSUMPTIONS.md Tier 3) — the literature supports that "better/newer
  control → faster response" but gives no mapping to a number. `digital_fadec`'s 0.6 is
  cited from this project's own `H3-250K_Config.cfg`.
- **`ignition.py` `forces_single_ignition` for pyrotechnic**: `[Huzel §4.7]` — a pyrotechnic
  squib "is designed for one start only and must be replaced after each firing." Correct.
- **`ignition.py` `plausible_pairs`**: `[SP-8081 §2.1.3.1]` / `[Huzel §4.7]` support the
  mappings — hypergolic self-ignition only for N2O4/MMH & A-50/NTO; catalytic only for
  hydrazine; spark torch for LOX/RP-1 & LOX/LH2; TEA-TEB for LOX/RP-1. LH2's higher
  spontaneous-ignition temperature is why it needs a stronger igniter than RP-1.
- **`ignition.py` `rf_ignitor_resources` ElectricCharge amounts**: `catalytic` = 0.01
  "matching MR-80B's real amount=0.005" — consistent with a catalyst bed needing almost no
  ignition energy (`[SP-8081 §2.2.2]`: the catalyst *is* the ignition).
- **`design.py` number of ignitions** (Model tab): `[Huzel Ch. XI]` / real configs confirm
  this varies from 1 to hundreds by engine role — a genuine design choice, correctly exposed.
  Cryogenic restart implies turbopump chilldown provisions `[SP-8107 §2.1.1.8]` — background
  for why restartable cryogenic engines carry extra system mass.
- **`throttle.py` `Pc ∝ throttle`, `Pe/Pc` throttle-independent, `dp_inj ∝ throttle²`**:
  consistent with `[Sutton §8.5]` (fixed throat → Pc tracks flow; injector Δp ∝ ṁ²) and
  `[SP-8107 §2.3.2.2]`. The sea-level flow-separation sweep uses the topic-01 separation
  criterion.
- A future dynamic-start model would use τ ∝ I·N/Tq `[SP-8107 eq. 15]` and could warn about
  the J-2-style H2-pump stall risk for tank-head-start designs.
- **`practical_min_throttle`/deep-throttle plausibility checks now have a much denser
  real-engine evidence base**: `[Casiano-Throttling]`'s catalog above (LMDE 10:1, CECE 13:1,
  SSME 6.4:1, RD-170/180 56%/40% minimums) is a candidate set of real per-engine/per-cycle
  anchors if the tool ever wants a plausibility check on a user-selected throttle range
  against real precedent, rather than the current single flat `practical_min_throttle` per
  injector type (topic 05). Also useful: SSME's real finding that **pump-stall margin, not
  combustion stability, was the binding low-thrust constraint** — a real precedent for
  gating deep throttle on turbopump behavior rather than only combustion/injector stability.
  Report-only — no code changed.
