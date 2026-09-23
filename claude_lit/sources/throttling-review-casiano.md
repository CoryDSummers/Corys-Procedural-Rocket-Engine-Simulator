# Casiano, Hulka & Yang — Liquid-Propellant Rocket Engine Throttling: A Comprehensive Review

## Identity

Matthew J. Casiano (NASA Marshall Space Flight Center), James R. Hulka (Jacobs Engineering,
ESTS Group), Vigor Yang (Georgia Institute of Technology), *Liquid-Propellant Rocket Engine
Throttling: A Comprehensive Review*, AIAA 2009-5540, 45th AIAA/ASME/SAE/ASEE Joint
Propulsion Conference & Exhibit, 2-5 August 2009. `literature/AIAA 2009-5540 - Liquid-Propellant Rocket Engine Throttling A Comprehensive Review.pdf` (NTRS 20090037061; 61 PDF
leaves: leaves 0-38 are the paper body + references, leaves 39-60 are the companion
conference presentation slides — redundant with the paper, not separately extracted). Tag:
`[Casiano-Throttling]`.

## Character

A survey paper, not a design-equation source: it reviews essentially every US (plus a few
Russian) throttleable liquid rocket engine development program from the late 1930s through
2009, organized by **throttling methodology** (eight categories: high-pressure-drop
fixed-geometry injectors, dual-manifold injectors, gas injection, multiple chambers, pulse
modulation, throat throttling, variable-area injectors, hydrodynamically dissipative
injectors), each with per-program case studies pulling real throttle ratios, chug
frequencies/amplitudes, performance numbers, and stability outcomes from the underlying
~118 references. Its value here is as a **dense catalog of real throttle-ratio
achievements and quantified stability-vs-throttle tradeoffs by program/engine** —
complementary to, not overlapping with, `[SP-8107]`'s already-cited turbopump-time-constant/
start-sequencing content in `topics/15-transients-and-controls.md`, and to
`[Sutton §8.5]`'s general Pc∝throttle / Δp_inj∝throttle² relations already cited there. No
overlap found with existing `topics/05-injectors.md` content beyond confirming the
"15-20% of Pc" injector-stiffness rule already cited from `[Huzel]`/`[Sutton]` (this paper
cites the same rule, sourced to its own refs [19],[23], with an explicit wider range of
5-25% depending on injector type/thermodynamic conditions).

## Key results (throttle-ratio and stability data by real program)

**Table I (leaf 3-6) — the paper's own summary table** lists ~25 programs/engines with
rated thrust, rated Pc, MR, demonstrated throttle range, propellants, and injector type in
one place; worth returning to directly if a specific program's parameters are needed beyond
what's excerpted below.

**High-pressure-drop (fixed-geometry) injectors** (leaf 2, 7-13):
- **A fixed-geometry single injector generally throttles only ~2:1 to 3:1**; deep
  throttling (5:1+) needs higher-than-usual injector Δp to hold a minimum stiffness at
  min thrust (leaf 2). Nominal injector stiffness (Δp_inj/Pc) should be **~15-20%** to
  avoid instability, but can range **5-25%** depending on injector type/thermodynamics
  (leaf 2, refs 19,23) — a wider band than `[Huzel]`'s flat 15-20%, worth folding into
  `topics/05-injectors.md`'s caveat that the rule is nominal-point-only.
- **Modified RL10A-1 (NASA LeRC, 1964)**, leaf 7-11: throttled 100%→10% thrust (later
  3.3%-100% per Table I). Three injector variants tested — shear coax (33% ox Δp/Pc),
  swirl coax low (20%) and high (60%) ox Δp/Pc. **Chug onset at MR 4.5: 32% thrust for the
  lowest-Δp injector, 25% for mid-Δp, never for the highest-Δp injector** — a direct,
  quantified injector-stiffness-vs-chug-onset-threshold data triplet. Peak chug amplitude
  ~80% Pc peak-to-peak at low-thrust/low-MR. Restabilized below ~40 psia (~10% thrust) due
  to LOX gasification increasing effective Δp (two-phase flow through the orifices).
  Pressure-fed (pumps inoperative) mode reached **3% thrust at Pc 10-15 psia**, MR 2-6;
  700°R jacket-outlet temp at MR=5 was the safe coking/erosion limit. Reducing Pc 100%→33%
  cost **~3% Isp**; below 33% the decay accelerated, plus chug cost an **additional ~8%**
  performance when present. A **1-5 Hz fuel-side flow instability** appeared below 33%
  thrust tied to two-phase H2 in the cooling jacket; **GHe or GH2 injection at ~20% of H2
  weight flow** stabilized it. Separately, **helium injection at 0.4% of LOX weight flow,
  or GOX injection at 4% of LOX weight flow, eliminated the oxygen-boiling-driven chug**
  (leaf 19) — real, small, quantified gas-injection fractions for chug suppression.
- **SSME (1997 X-33 support test)**, leaf 11: throttled down to **17% rated power (6.4:1
  from 100%)**; normal operating range is 65-109% RPL. No combustion instability at any
  level tested (17/22/27/40/45/50%). MR held 3-4 (fixed) to keep margin from HPFTP boilout/
  stall — **the fuel-pump stall margin, not combustion, was the binding constraint** at
  low thrust.
- **CECE (Common Extensible Cryogenic Engine, modified RL10, 2005-2008)**, leaf 12-13: a
  real, citable, best-in-class number — **13-to-1 throttle range demonstrated, 5032 s
  total run time** across Demo 1.0/1.5/1.6. Modifications: reduced oxidizer injector flow
  area + reduced outer-row MR, plus a fuel turbine bypass and a variable-area cavitating
  venturi. Chug at low power was fixed by (a) LOX-manifold insulation (reduces onset
  power level) and (b) GHe injection (eliminated chug outright) — same fixes as the 1964
  RL10A-1 study, now validated on a flight-heritage engine 40+ years later.

**Dual-manifold (dual-orifice) injectors** (leaf 13-19):
- General principle: two fixed injector circuits (primary+secondary) per propellant;
  above a transition thrust both flow, below it only primary flows — changes effective
  injection area in one step rather than continuously varying orifice geometry.
- **High Energy Advanced Throttling Concept Study (F2/H2)**: subscale injectors throttled
  **12:1**, full-scale **29:1** (leaf 14) — among the deepest ratios in the whole survey.
- **Chamber Technology for Space Storable Propellants (1964-69, FLOX/space-storable)**,
  leaf 15: **10:1** throttle range repeatedly demonstrated; **c\* efficiency 92-98% across
  the whole range**; primary/secondary transition at 49% thrust. One instability event (170
  Hz, 13% p-p Pc oscillation at 90% thrust) traced to trapped purge-gas two-phase flow
  through the injector, fixed by a purge-system change — not an inherent dual-manifold
  stability problem.
- **XLR-129 (Reusable Rocket Engine Program, staged combustion, 1967-72)**, leaf 16-17:
  design goal 5:1 throttle at 96% theoretical Isp nominal / 94% throttled. Achieved: **Isp
  efficiency ~93% at 100% power, ~90% at 20% power (missed the 94% requirement)**; **c\*
  efficiency ~98% nominal, ~96% throttled**. Preburner chug at 20% power (11% p-p Pc,
  75-150 Hz) traced to low secondary-circuit LOX Δp + excess secondary manifold volume —
  **never eliminated even at 90% primary flow split / ~60% mass-weighted Δp/Pc**; a
  redesign cutting secondary manifold volume 20-40% was predicted (and later demonstrated)
  to fix it. A rare case in this paper of a *quantified, unresolved* stability limit for a
  specific throttling architecture.
- **Advanced Expander Test Bed (1990, LOX/H2 expander)**, leaf 18: **requirement 5:1, goal
  20:1**; a 25 klbf TCA using the same dual-manifold injector was tested to a **20:1**
  throttling capability (1996, data proprietary) — the deepest expander-cycle throttle
  figure in the survey.

**Gas injection (propellant aeration/foaming)** (leaf 18-20):
- Mechanism: injecting a low-density (often inert) gas into the liquid propellant lowers
  bulk density, which *raises* injector Δp at a given mass flow (Δp ∝ 1/ρ at fixed flow) —
  raises chug margin and can raise performance for fixed-geometry injectors. Russian
  experience: gas injection can trigger high-frequency pressure fluctuations as a downside
  (leaf 18, ref 4).
- **Bendix Corp. Throttling Concept Study (1965)**, leaf 20: **35:1 demonstrated with N2
  gas; 50:1 considered achievable with He** — the single deepest gas-injection ratio cited,
  storable propellants (A-50/N2O4), stable and efficient across the whole range. Evolved
  into the "Bimode Bipropellant Attitude Control System" (pulsing + continuous throttling).
- Required gas injection flow rates for stabilization are **generally <1% of propellant
  flow** (leaf 33 summary) — consistent with the RL10A-1 0.4%/4% figures above.
- Rocketdyne SE-10 (LMDE competitor) used He gas injection but retained 200-500 Hz chug
  and intermittent popping regardless; first-tangential-mode instability was fixed instead
  by a Y-shaped baffle (leaf 20) — a case where gas injection alone did NOT solve the
  stability problem.

**Multiple chambers** (leaf 20-22):
- **RD-170/RD-171** (Glushko, 4 chambers, 1 turbopump, 1,777,000 lbf vacuum thrust):
  **throttles to 56% of maximum thrust**.
- **RD-180** (2 chambers, 933,400 lbf vacuum thrust): **throttles to 40% of maximum
  thrust**. Both are real, citable minimum-throttle-fraction numbers for large Russian
  staged-combustion multi-chamber engines, useful alongside `topics/08` cycle content.
- Rocketdyne Advanced Maneuvering Propulsion Technology engine (aerospike + inner bell,
  1967 design): both the 3.3 klbf and 30 klbf chambers individually throttle **9:1**,
  giving an aggregate **effective throttling ratio of ~81:1** (9×9) — a real example of
  multiplicative throttle-range gain from independently-throttled multi-chamber
  architectures. Combustion efficiency 98-100% across the segment's tested range (650→72
  psia Pc).

**Pulse-width modulation (PWM)** (leaf 22-23):
- Continuous (non-pulsed) throttle achieved down to **12% rated thrust**; PWM pulsing
  extended effective deep-throttle range to **100:1** (combined continuous+PWM dual-mode
  approach) — a concrete number for a "how deep can combined continuous+pulse throttling
  go" question. Pulse performance was measured 100%→20% thrust with 150 ms pulses; ignition
  transients spiked to **300% of rated Pc**. Performance during short pulses was
  measurably worse than steady-state at the same average thrust — shorter pulses degrade
  performance further (a real transient-vs-efficiency tradeoff for RCS-style pulsing).

**Throat throttling (mechanical pintle or gas injection at the throat)** (leaf 24-26):
- Historically one of the *first* LRE throttling methods (1947 Reaction Motors study).
  **Gives the highest chamber pressure — and highest theoretical performance — at low
  thrust** of any method surveyed, because at fixed feed pressure, throat restriction
  raises Pc. Major drawbacks: pintle cooling/vibration, and impossible to get correct
  injector Δp across the whole range from a fixed-Pc feed system since Pc itself is the
  control variable (leaf 24, leaf 34 summary).
- 1947 RMI unit: 6.25:1 throttle range, but **L\* had to vary 43.5-272 in** across the
  range (a single compromise L\* chamber was used) — real magnitude for how much L*
  swings if chamber volume is fixed but throat area is throttled.
- Throat gas-injection sub-method: **effectiveness scales with √(T_secondary/T_primary)**
  (UAC finding); a secondary-to-primary stagnation temperature ratio of ~4-5 essentially
  kills throttling effectiveness (both Rocketdyne F-1 testing and UAC thrust-vectoring
  experiments confirmed this) — a real inverse relationship between injectant temperature
  and throat-throttling authority. Low-MW, low-γ gas (helium ideal) is most effective per
  unit mass injected.

**Variable-area injectors, incl. LMDE pintle** (leaf 26-32):
- **LMDE (Apollo Lunar Module Descent Engine)**, leaf 27-29 — the paper's flagship real
  case: **10:1 throttle requirement**, single central pintle varying both fuel-annulus and
  oxidizer-radial-hole area simultaneously via one moving sleeve. MR held constant via
  separate **variable-area cavitating venturis** in the propellant feed lines upstream of
  the injector (decouples MR control from injection-area/thrust control) — cavitation
  regime active only below 70% thrust; above that, ordinary system Δp control took over.
  Duty cycle: full-thrust braking phase → 60% braking → slow reduction to 40% at flare-out
  → ~25% during hover. **>2800 tests including 31 bomb (dynamic-stability) tests: no
  radial or tangential acoustic modes detected** — attributed to the pintle's *annular*
  (not centrally concentrated) reaction zone geometry naturally not exciting the 1st
  radial mode. Low-frequency Pc oscillations of **20 psi peak-to-peak in the 10-100 psia
  Pc range** occurred during throttling transitions (not a full instability, but a real
  transient-Pc-ripple magnitude).
- **MIRA 150A (TRW, Surveyor attitude control, 1965)**, leaf 29: single-element coaxial
  pintle, ablative-cooled (regen wasn't viable across the full 5:1 range due to coolant-
  flow incompatibility at low end). **84 starts across 4 configs demonstrated 6.8:1
  throttling.**
- **NACA 1955 study**, leaf 27: triplet impinging-jet injector — 96% efficiency at full
  thrust, sharp drop below 20% thrust, tested **12:1**. Swirl-cup injector — 90% at full
  thrust, also sharp drop below 20%, tested **18.5:1**. Both show the same qualitative
  "cliff" below ~20% thrust for early variable-area designs.
- **TR202 (NGST, closed-expander LOX/GH2 lunar-descent pintle, 2005-era)**, leaf 30-31: a
  **10:1** demonstrated range with independent turbopumps + variable-area pintle for full
  MR/thrust decoupling. Real quantified stiffness number: **fuel injector stiffness rises
  from 20% at full thrust to 106% at minimum thrust** as the variable-area orifice closes
  — i.e. injector stiffness (Δp/Pc) is NOT constant across a variable-area throttle range,
  it rises sharply toward minimum thrust as the effective flow area shrinks faster than Pc.
  This has "no effect on cycle balance because there is more power margin at lower throttle
  settings" for this expander design.
- Project MX-794 follow-on (1951), leaf 26: plunger-type variable-area injector,
  **27:1 continuous throttling range** demonstrated — one of the deepest single-injector
  continuous ratios in the survey, at the cost of lower performance than fixed-orifice
  injectors of comparable size (piston-leakage-driven MR drift was the main loss mechanism).

**Hydrodynamically-dissipative injectors** (leaf 32): swirl/vortex-tube injectors that
throttle by varying effective discharge coefficient rather than physical area — common in
Russian practice, usually combined with dual-manifold; PSU/Bazarov (2001) demonstrated a
dual-inlet swirl LOX/GH2 injector achieving good stiffness with 10:1-class throttling
(matches the entry already in `topics/05-injectors.md` §Table under `[Bazarov]`/`[PSU-
CoaxAtom]` — same PSU program, complementary throttling-specific data point not yet in
that file: throttling behavior there is quantified via *discharge-coefficient variation*,
not just flow-rate variation).

## Design method

Not a closed-form design-equation source — no derivation of Δp-vs-throttle-ratio sizing
formulas, chug-onset criteria, or pintle-area schedules is given (the paper cites
`[Sutton]`/`[Huzel]` for those, already in this reference set). Its unique value is the
**breadth of real quantified throttle-ratio/stability/performance outcomes by program**,
organized by throttling *methodology* rather than by engine — useful as an evidence base
for "what throttle ratio is actually achievable by method X" claims, and for chug-onset
Δp/Pc thresholds tied to specific injector stiffness values (the RL10A-1 32%/25%/never
triplet is the paper's most directly load-bearing single data point for that purpose).

## Section map

- Abstract + Introduction (mission motivation, 10:1 lunar descent / 1.3:1 Venus launch /
  100:1 ballistic-missile-defense examples): leaf 0-2.
- Table I (25-program summary table — thrust, Pc, MR, throttle range, propellants,
  injector type, program dates/orgs): leaf 3-6.
- §A High-Pressure-Drop Injectors (Project Thumper, MX-794, RL10A-1 mod, ARES, X-33/SSME
  support tests, CECE): leaf 2, 7-13.
- §B Dual-Manifold Injectors (triplet dual-manifold, F2/H2 study, Chamber Technology for
  Space Storables, Reusable Rocket Engine Program/XLR-129, Throttleable Primary Injector
  HIPERTHIN, Advanced Expander Test Bed): leaf 13-19.
- §C Gas Injection (NACA foamed-propellant, RL10A-1 mod chug-elimination-by-gas-injection,
  Bendix study, SE-10/other engines): leaf 18-20.
- §D Multiple Chambers (Rocketdyne aerospike+bell study, RD-170/171/180): leaf 20-22.
- §E Pulse Modulation (PWM, satellite rendezvous studies, Bendix): leaf 22-24.
- §F Throat Throttling (RMI 1947 restrictor bulb, gas-injection-at-throat models): leaf
  24-26.
- §G Variable Area Injection (RMI 1950 variable-thrust program, MX-794 follow-on, NACA
  1955 triplet/swirl-cup, **LMDE**, MIRA 150A, AFIT gaseous study, TR202): leaf 26-32.
- §H Hydrodynamically Dissipative Injectors (PSU/Bazarov swirl injector): leaf 32.
- §III Summary and Conclusions (per-method recap, no new numbers beyond what's captured
  above): leaf 32-35.
- References (118 entries, mostly primary NASA/AIAA/contractor reports per program — a
  good index if a specific program's original source report is ever needed): leaf 35-38.
- Leaves 39-60: companion conference presentation slides — same content as the paper body
  in bullet form, **not separately extracted** (confirmed redundant by spot-checking
  slides at leaf 39/40/45/50/55/60).

## Caveats

- **Survey/review paper, not primary data** — every number above is the paper's own
  restatement of an underlying reference (its own refs [19]-[118]); treat as a reliable
  index of real program outcomes, not as independently re-derived or re-verified data. If
  a specific number needs tighter provenance (e.g. exact CECE test conditions), the
  underlying reference (numbered in the text) should be chased.
- **US-centric**: explicitly "a detailed survey of LRE throttling methods centered around
  engines from the United States" (abstract) — Russian deep-throttling swirl-injector work
  (Bazarov et al.) is only lightly covered via the PSU collaboration case; `[Bazarov]`
  (already in this reference set, `topics/05-injectors.md`) remains the better source for
  Russian ORSC/swirl-injector throttling detail specifically.
- No cooling/heat-transfer design methodology beyond qualitative statements ("cooling
  ability decreases at lower thrusts," "total chamber heat load fits pc^0.8 across
  throttling range" per leaf 33) — no new numeric anchor for `topics/03` or the cooling
  topic file beyond what's already cited from `[SP-8107]`/`[Huzel]` there.
- Several of the deepest ratios cited (F2/H2 29:1, Bendix gas-injection 35:1/50:1,
  aggregate 81:1 multi-chamber) are from **small research/demonstrator engines, not flown
  hardware** — the paper itself frames these as capability demonstrations, not flight
  heritage; the LMDE (10:1) and RD-170/180/CECE numbers are the strongest flight/flight-
  program-relevant anchors.
- OCR/extraction quality: clean, standard AIAA-paper-format PDF text extraction via
  PyMuPDF; no garbling encountered in the body text read.
