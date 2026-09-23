# 10 — Gas generators

## Scope

Design of the bipropellant gas generator that produces turbine-drive gas: hot-streak /
temperature-stratification control, mixture ratio, injector type, chamber sizing by stay
time, materials, ignition. Almost entirely from `[SP-8081]`, with `[Huzel §4.6]` and
`[KBKhA]` for cross-check. Feeds the GG constants in `engine_designer/physics/design.py` and
`turbopump.py`.

## The governing problem

`[SP-8081 §1]`: **hot streaking.** Turbines have hard temperature limits; local combustion
temperature far exceeds the mixed-gas temperature; the designer's job is to control *where*
combustion happens and *how fast* hot and cool streams mix, so the gas reaching the turbine
is uniform. Combustion *efficiency* is ~100 % in a GG (huge fuel excess) and is not the
problem. This makes GG chamber design fundamentally different from thrust-chamber design.

## Key relations

There are few closed-form relations — `[SP-8081]` is a practice/criteria document. The
turbine-drive power balance is in topic 09. The one theoretical result:

**Potential-core (unmixed-flow) length** `[SP-8081 §2.1.1.1, ref. 3]`:

    axial-flow:     X = 4.55 · H          H = radius of the larger wall / passage enlargement
    reverse-flow:   a separate correlation, ref. 3 p.460

Mixing completes a short distance beyond the potential core. "No evidence this theory has
been used to design a new GG, but even in its simplest form it gives more guidance than
thrust-chamber parameters."

## Empirical correlations & typical values

**Real GG parameters** `[SP-8081 Table I p.4]` (F-1, M-1, J-2, H-1, Atlas, Thor, Titan II,
Jupiter, Redstone, Navaho, Vanguard):

| Quantity | Range | Notes |
|---|---|---|
| Gas temperature | 1000–1660 °F (811–1178 K) | most **1200–1400 °F (922–1033 K)**; F-1 = 1500 °F (1089 K) |
| Chamber pressure | 450–1100 psi (3.1–7.6 MN/m²) | |
| Stay (residence) time | **2.3–10.5 msec** (chamber only, not ducts/manifold) | |
| Turbine power | 371 BHP (Agena) … 117 000 BHP / 87 MW (M-1); F-1 55 000 BHP / 41 MW | |
| Chamber materials | Hastelloy C (J-2, F-1), N-155, 347 CRES, Nickel, Aluminium, Haynes 25 | 347 CRES for ~1200 °F; higher-strength for hotter/lighter |
| Flow path | mostly reverse-flow | |

Cross-check: `[KBKhA Table 2]` RD-0110 turbine inlet temp **1050 K** (right in the band);
`[Huzel §4.6]` gives 1200–1700 °F (922–1200 K) for turbine drive, 400–1000 °F for tank
pressurization; `[SP-8107 §3.2.3.1]` "as high as practical (~1500 °F / 1089 K uncooled)".

**Mixture ratio** `[SP-8081 p.7]`:
- "Normal" bipropellants: **fuel-rich, MR 0.2–1.0** — hydrocarbons at the low end (~0.3),
  hydrogen at the high end (0.98–1.0).
- "Energetic" propellants (Aerozine-50, UDMH, hydrazine): MR **< 0.2**. Prone to reaction
  instability / flameout; the 1000–1400 °F (811–1033 K) window is conducive to that
  instability (below 811 K they don't react fast enough for pulses; above 1033 K they react
  so fast accumulations don't form).
- **Why fuel-rich**: (1) a fuel-rich hot streak is far less damaging than an oxidizer-rich
  one; (2) turbine specific propellant consumption is better with low-molecular-weight
  fuel-rich gas. Oxidizer-rich bipropellant GGs: essentially no Western applications as of
  1972 (chamber-burning risk); later a Soviet/Russian speciality (`[KBKhA]`, ORSC).

**Chamber sizing** `[SP-8081 §2.1.1.2]`: L\*, stay time and volumetric loading have all been
tried; **stay time is the most useful**. Atlas-sustainer data: below **3–4 msec** mixing is
inadequate and hot spots appear; above **6–10 msec** the safe-operation margin grows with
stay time. Duct + turbine-manifold stay time adds a lot more (F-1 chamber 5 msec, manifold
14 msec) — matters for thermal cracking of the fuel, not for hot-spot prevention (the gas
must be mixed *before* leaving the chamber).

**Injector: hot-core vs UMR** `[SP-8081 §2.1.2.1]`:
- *Hot-core*: all oxidizer + enough fuel for a near-stoichiometric central core; the rest of
  the fuel dilutes around the outside. Strong initial stratification. Nearly every hot-core
  GG (Navaho, Atlas MA-3, Thor, Jupiter, J-2, Titan I/II) had a long, severe failure
  history.
- *UMR (uniform mixture ratio)*: every element injects at the overall GG MR → a multitude of
  small hot zones quenched fast by intimately-mixed excess fuel. Streaking problems, when
  they occur, are "an order of magnitude easier to solve." The modern default for normal
  propellants.
- UMR vs hot-core (`[SP-8081]` ref. 14, LOX/RP-1): at a given MR, UMR gives higher
  temperature and higher c\*; **at a given temperature the c\* is the same** — injector type
  moves where you sit on the MR–c\* curve, not the curve.
- Element flow limits: coaxial elements behave like mini hot-cores, more like UMR below
  ~0.5 lb/s (0.23 kg/s) per element; small triplets at ~0.1 lb/s (0.045 kg/s) per element
  give minimum streaking. M-1's large concentric-tube UMR elements caused temperature
  gradients 42 in (107 cm) downstream of the injector.
- Elements that enshroud the oxidizer in fuel (triplet, quincunx) give minimum hot-streak
  tendency; unlike-doublets give highly nonuniform MR and bad streaking.

**Mixing devices** `[SP-8081 §2.1.1.1, §2.1.1.4]`:
- *Reverse-flow mixing chamber*: force the flow to stagnate then reverse direction. Achieves
  < 50 °F (28 K) outlet temperature variation at 1400 °F rated, at ~⅓ the pressure loss of
  the turbulence-ring approach. "Momentum separation" — a hot, high-velocity core doesn't
  turn as readily as cool gas.
- *Turbulence rings*: effective at mixing wall film coolant with excess fuel; not effective
  at mixing a hot core. Overheat if placed below the flame front; keep within 2 in (5 cm) of
  the injector or use a conical (not flat-orifice) ring to limit pressure drop and edge
  heating.
- UMR injector + adequate flow-reversal area: temperature variations < 100 °F (56 K).

**Thermal protection** `[SP-8081 §2.1.1.6]`: early F-1 had a regeneratively-cooled GG;
modern practice is **uncooled solid wall + film cooling** (crucial in the burning zone
before mixing is complete). `[Huzel §4.6]`: solid-propellant GGs (turbine spinners / start
cartridges) run > 2000 °F, burn rate `R = k1·Pc^n`.

**Materials** `[SP-8081 §2.1.1.7]`: 1200 °F (922 K) service → 347 CRES; higher temp or
weight saving → Hastelloy C (J-2, F-1), N-155, Hastelloy X, Haynes 25 (brittle). Atlas S-4
GG ran 347 CRES at 1400 °F, later reduced to 1200 °F to avoid coking.

**Ignition** `[SP-8081 §2.1.3.1]`: most GG propellants do not autoignite; pyrotechnic
cartridges (usually two, for redundancy); spark plugs where chilldown/restart is needed
(J-2). LH2 is harder to ignite than RP-1 (spontaneous ignition temp ~1000 °F / 811 K; RP-1
ignites with GOX at room temperature). Best igniter location: within ~1 in (2.5 cm) of the
injector face, where both propellants arrive simultaneously.

## Caveats

- `[SP-8081]` is 1972 and treats only turbine-drive GGs. Staged-combustion *preburners* are
  a different animal (higher pressure, oxidizer-rich options, `[KBKhA]`).
- Numbers are for the historical fleet (LOX/RP-1, LOX/LH2, storables); no LOX/CH4.
- The potential-core mixing theory is qualitative; `[SP-8081]` explicitly says it has never
  been used to design a production GG.

## Implications for engine_designer

- **`design.py` GG_TIN_K = 1050**: exactly RD-0110 `[KBKhA Table 2]`, and in the middle of
  the `[SP-8081 Table I]` fleet band (811–1178 K, most 922–1033 K) and the `[SP-8107 Table
  III]` GG-turbine band (922–1061 K). Cite all three. (Same point as topic 08/09.)
- **`design.py` GG turbine drive-gas Cp/γ/Tin**: now a per-propellant-pair table
  (`GG_GAS_PROPERTIES`), not three globals. `[SP-8081]`/`[Huzel §4.6]` don't tabulate Cp/γ
  for GG gas, so the values come from the fuel-rich gas composition per pair:
  - LOX/RP-1: 1050 K / 2100 / 1.13 - fuel-rich hydrocarbon gas, unchanged; reproduces F-1
    (~3.0%) and RD-0110 (4.2%, `[KBKhA Table 2]` 3.97 of 93.8 kg/s) GG bleed.
  - LOX/LH2: 922 K / 8000 / 1.36 - hydrogen-rich gas at GG MR ~0.9 (~47% H2 / 53% H2O by
    mass gives Cp ~8000, γ ~1.36); Tin = J-2 fuel-turbine inlet 1200 °F `[SP-8107 Table
    III]`. The old single kerolox Cp (2100) applied here over-predicted GG bleed ~5x
    (7.6% vs the real J-2 ~1.3%). Spot-checked in `validate.py::run_gg_flow_fraction_check`
    against the J-2 bleed and the `[SP-8107 Table VI]` Isp-loss band.
  - storables (N2O4/MMH, A-50/NTO): 1150 K / 2800 / 1.22 - documented estimate (hotter
    turbine per YLR87-AJ-7 `[SP-8107 Table III]`; no storable GG bleed data point to
    calibrate against).
- **GG mixture ratio is not a variable in the tool** — `[SP-8081 p.7]` shows it's a real
  design choice (0.2–1.0 for normal pairs, < 0.2 for energetic). A future addition could
  expose GG MR and derive `GG_TIN_K` from it (higher MR → higher turbine inlet temp → more
  turbine work per unit flow → smaller bleed fraction, but hotter turbine).
- **`GG_FLOW_FRACTION_TYPICAL_MAX = 0.07`** warning: `[SP-8081 Table I]` doesn't give bleed
  fractions directly, but the GG turbine powers (F-1 41 MW driving pumps that move ~1900 kg/s
  of propellant at ~77 kg/s GG flow → ~4 %) are consistent with a few-percent bleed being
  normal and 7 % being a warn-worthy red flag. `[SP-8107 Table VI]`: GG Isp loss ⅓–1 % at
  1000 psia.
- **Injector `eta_cstar_multiplier` for GG-style operation**: `[SP-8081 ref. 14]`'s "same
  c\* at a given temperature for UMR vs hot-core" supports the tool's small (±2 %) injector
  efficiency spread (topic 05).
- **Ablative / burn-time for uncooled GG-adjacent parts**: `[SP-8081 §2.1.1.6]` "modern GGs
  are uncooled solid wall + film cooling" — relevant to how `mass_model.py` and the
  rated-burn-time logic treat film-cooled vs regen-cooled chambers.
