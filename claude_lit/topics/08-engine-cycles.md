# 08 — Engine power cycles

## Scope

Gas generator, thrust-chamber tap-off, expander, staged combustion, pressure-fed: how each
routes the turbine working fluid, what pump discharge pressure it demands, its turbine
pressure ratio, its Isp penalty, and how the cycle choice feeds back onto turbopump stress.
Feeds `engine_designer/physics/cycles.py`, `expander.py`, and the cycle constants in
`design.py`.

## Key relations

**Pump discharge pressure** `[SP-8107 §3.1.1.1 p.99]`:

    P_discharge = Pc + Σ(downstream pressure drops)
    GG cycle:            + line losses + valve losses + regen-jacket ΔP + injector ΔP
    staged combustion:   + preburner injector ΔP + turbine ΔP + inter-component line losses

**Parallel vs series turbine** `[SP-8107 §2.1.1.4 p.20]`:
- *Parallel* with the chamber (GG, tap-off): turbine exhausts overboard (or at low
  pressure). Pump head and power stay relatively low. Isp penalty from the bled flow.
- *Series* with the chamber (expander, staged combustion): the turbine ΔP **adds** to the
  pump discharge pressure → high head and power, and pump discharge pressure becomes
  **more sensitive to pump/turbine efficiency**. No Isp penalty (all flow reaches the
  chamber).

**Turbine bleed Isp loss (GG cycle)** `[SP-8107 Table VI]`: engine Is loss ≈ **⅓ to 1 % at
1000 psia Pc, proportional to Pc**. The tool models this as a mass-averaged blend
(`engine_isp_with_gg_dump`, topic 09).

**A real closed-form GG-cycle/staged-combustion Isp derivation (2026-09-24)** `[Schmucker-
CycleCalc p.8 eq.18, p.11 eq.29]`: `I_sp,ggc = η_sp[(1−k_m)·I_sp,c + k_m·I_sp,g]` (k_m = the
GG-bled mass fraction) — the first hand-calculable equation form of the qualitative "Isp
penalty from bled flow" statement above; and its staged-combustion counterpart, `I_sp,sec =
I_sp,c · η_sp` (literal zero-bleed-penalty case, since the whole fuel flow reaches the main
chamber via the preburner). A companion derivation `[pp.9-11 eqs.24-28]` explicitly works out
*why* staged-combustion pump discharge must build up from Pc plus the turbine's own pressure
drop — the underlying mechanism behind `[SP-8107]`'s already-cited "series turbine ΔP adds to
pump discharge pressure" rule above, now with a real first-principles derivation behind it
rather than just a design-guide statement. **Caveat**: the source PDF on disk is truncated
(23 of the paper's real 42 pages) — the numeric GG-vs-staged-combustion comparison the paper's
own summary promises, and its real 1973-era LOX/LH2 worked examples, are NOT present in this
copy; only the derivation/methodology above survived. Re-acquiring a complete copy is the
obvious follow-up if that comparison data is ever wanted.

## Empirical correlations & typical values

**Cycle comparison** `[SP-8107 §2.1.1.4, Tables V–VI, Fig 11]`, `[Sutton §6.6]`:

| Cycle | Turbine | Pump discharge P ≈ | Optimum turbine PR | Isp penalty | Pc practical limit | Notes |
|---|---|---|---|---|---|---|
| **Gas generator** | parallel | **1.5 × Pc** | **~20** (minimise turbine flow) | ⅓–1 % at 1000 psia, ∝ Pc | none, but Pc kept < 1500 psi to limit turbine flow | most-used; component performance insensitive to other components; good uprating; carbon buildup on turbine nozzles with some fuel-rich propellants |
| **Tap-off** | parallel | ≈ GG | slightly < GG | ≈ GG (~0.5–1 s) | — | working fluid tapped near injector face where gas is relatively cool; more complex thrust chamber; J-2S development engine |
| **Expander** | series | **2.5 × Pc** | **< 1.5** | none | **~1000 psia** (power available from heated fuel) | H2 / light-hydrocarbon fuel only; not feasible at high thrust (heat per lb pumped falls); clean noncorrosive turbine fluid; RL10 |
| **Split expander** (P&W-specific) | series | higher than plain expander (2nd-stage pump work traded for turbine-inlet temp) | < 1.5 | none | **~900 psia demonstrated** (734-896 psia, two real LOX/CH4 point designs `[STBE-PW]`) | bypasses a fraction of fuel around the 2nd pump stage direct to injector; buys higher Pc than plain expander at the cost of worse injector atomization (larger L\* needed) |
| **Staged combustion** | series | **> 2.0 × Pc** (nonlinear) | **< 1.5** | none | **~3000 psia**; resultant pump discharge 7000–8000 psia | max performance; controls 5 valves; engine performance sensitive to component design; limited uprating |
| **Monopropellant GG** | parallel | ~1.5 × Pc | — | large at high Pc | — | needs a separate propellant unless a main propellant is a monopropellant; H2O2 lowest performance, hydrazine better |
| **Pressure-fed** | none | Pc + line + injector ΔP + tank margin | — | none | ~0.7–0.8 MPa (classic tanks); ~6.9 MPa (composite-overwrapped, SuperDraco) | no turbomachinery; the tank must supply the whole feed pressure |

**Real anchors:**
- J-2 (GG): Pc 787 psia, fuel-pump discharge/Pc = **1.6**, overall turbine PR = **19**
  `[SP-8107 p.25]`.
- RL10 (expander): Pc 400 psia, fuel-pump discharge/Pc = **2.5**, overall turbine PR = **1.4**
  `[SP-8107 p.25]`. RL10A-3-3 turbine inlet temp **−106 °F** (cold heated hydrogen)
  `[SP-8107 Table III]`.
- SSME (staged combustion): Pc 3237 psia, preburner turbine inlet pressure ~5880 psia,
  turbine PR 1.56–1.59, turbine efficiency 73–79 % (reaction turbines) `[SP-8107 Tables I,
  III]`.
- **GG-cycle turbine PR across the fleet**: 15.7–29, mean ~20 `[SP-8107 Table III]`.
- **GG-cycle turbine inlet temperature**: 1200–1450 °F (922–1061 K), most 1200–1240 °F;
  F-1 = 1450 °F (1061 K) `[SP-8107 Table III]`. "As high as practical (~1500 °F / 1089 K
  with an uncooled turbine and GG)" `[SP-8107 §3.2.3.1]`.
- **GG mixture ratio**: fuel-rich, MR 0.2–1.0 for normal bipropellants (hydrocarbons ~0.3,
  hydrogen 0.98–1.0); "energetic" fuels < 0.2 `[SP-8081 p.7]`. See topic 10.

**Real tap-off-cycle anchor — J-2S** `[AEDC-J2S §2.1/§2.1.1, §4.2]`: the first real hardware/
test data in this reference set for tap-off specifically (previously "one development engine,
J-2S" with no real numbers cited). Real hardware confirms a **series turbine arrangement for
the two pumps** (tapped gas drives the fuel turbine first via the Hot Gas Tapoff Duct, then a
separate Fuel Turbine Exhaust Bypass Duct carries it on to drive the oxidizer turbine, before
final overboard dump) — worth checking against whatever `cycles.py`/`design.py` currently
assumes about tap-off turbine staging (single combined turbine vs. two in series), since this
real engine uses two. Main-stage performance (3 of 11 test firings with clean data): c\* ≈
7720–7800 ft/s, Isp ≈ 433–434 lbf·s/lbm, thrust 230,000–271,000 lbf, MR 4.6–5.1 (vs. 5.5
design nominal) — the c\*/Isp/MR figures are trustworthy; **the reported Pc (1182–1279 psia)
is flagged uncertain** (notably higher than J-2S's commonly-cited ~700–850 psia nominal Pc;
the report doesn't unambiguously state the pressure-tap location, see
`sources/aedc-tr-70-204-j2s-altitude-test.md`). A real, concrete **spin-up solution**: a
one-shot solid-propellant turbine starter (SPTS) fires at main-stage start to spin the
turbines before tapped-gas flow alone can sustain them — the same "cold-start" problem any
tap-off or staged-combustion cycle without a dedicated spin-up GG has to solve. J-2S's defining
tap-off-enabled feature, a low-thrust **idle mode** (nominal 5000 lbf, MR 2.5, idle Pc only
18–31 psia) used for orbital-restart tank settling, is a real demonstrated use of tap-off's
"parallel, throttleable-independent-of-main-injector-flow" character that no other cycle in
the table above can do as simply.

**A real second LOX/CH4 tap-off data point, for a hydrocarbon fuel** `[STBE-PW leaf
341-344]`: a 1989 P&W preliminary-design study (Unique STBE Tap-Off, 750 Klbf SL thrust, Pc
2400 psia) gives a **tap-off flow rate of 132 lbm/s against a 2462 lbm/s injector flow —
~5.4% of injector flow tapped near the throat to drive the turbines**. This is a second
real tap-off anchor alongside `[AEDC-J2S]`'s J-2S numbers above, now for LOX/CH4 rather than
LOX/LH2 — useful if a tap-off bleed-fraction constant ever needs a hydrocarbon-fuel anchor
rather than only a hydrogen one (the existing `TAP_OFF_DUMP_ISP_FRACTION` remains otherwise
unsourced, per the caveat below).

**A new real cycle variant — the "split expander" cycle (P&W-specific, distinct from any
existing entry in this table)** `[STBE-PW leaf 28-29]`: "The split expander cycle differs
from the standard expander cycle used in the RL10 engine by separating a portion of the fuel
flow at the first-stage pump and directing that flow directly to the injector. The remainder
of the fuel flow completes the standard expander cycle... Since flow and temperature trade
proportionally in turbine power, the split expander low flowrate at the higher temperature
will provide the same turbine power. The pump work will be reduced due to the reduction in
flow through the second-stage pump. This reduced power requirement provides the capability
for a higher chamber pressure." I.e. a fraction of fuel bypasses the second pump stage
straight to the injector, letting the remaining (smaller) flow take the full regen-heat
pickup at a higher exit temperature — same turbine power at less second-stage pump work,
buying higher achievable Pc than a plain expander. Two real worked LOX/CH4 engines: a
**Derivative** (STME-derivative hardware, 706,500 lbf vac thrust, Pc 734 psia, eps 13.5) and
a **Unique** (clean-sheet, 750 Klbf, Pc 896 psia) — both well above `[SP-8107]`'s ~1000 psia
plain-expander Pc ceiling in the table below, confirming the cycle's own stated
higher-Pc-capability claim with real numbers. A real, quantified cycle-driven design
penalty: the Unique engine's minimum L\* (49 in) is explicitly **larger than the
gas-generator-cycle engines' (31.3-41 in) "mainly as a result of poorer atomization in the
split expander due to less available pressure drop across the injector elements"** `[leaf
262, 315]` — a real expander-cycle atomization/chamber-sizing tradeoff worth flagging
alongside `topics/04-chamber-sizing.md`'s L* discussion for any future expander-cycle
sizing check.

**A modern (2010) real anchor confirming the series-turbine arrangement persisted — J-2X**
`[J2X-Overview, Design Overview slide]`: J-2X, a GG-cycle (not tap-off) LOX/LH2 upper-stage
engine built on the **J-2S Mk 29 turbopump heritage** (same real pump family as `[AEDC-J2S]`),
confirms the **same series fuel→oxidizer turbine arrangement** carried forward into a modern
GG-cycle redesign — real, recent hardware evidence that this isn't just a 1970s tap-off-cycle
quirk. Real design point: 294,000 lbf vacuum thrust, Isp 448 s (min), MR 5.5, 500s duration,
dry weight 2,516 kg, 8 starts/2,600s life; throttle capability via a named "Oxidizer Turbine
Bypass Valve" (OTBV) rather than tap-off's parallel-flow throttling. Real turbopump design
changes from the J-2S heritage baseline: hydrostatic bearings adopted for the fuel turbopump
(after CFD showed low rotordynamic stability margins with the heritage bearing design), and
the LOX inducer changed from a shrouded 3-blade to an unshrouded 2-blade design after
subscale water-flow testing — concrete, test-driven inducer-design precedent relevant to
`engine_designer`'s NPSH/suction-specific-speed discussions (topic 09). Chamber/nozzle
construction: tube-wall regen main nozzle + a large passively-cooled nozzle extension boosted
by turbine exhaust gas — a **third real anchor** (after Vulcain HM-60 and J-2) for the
regen-nozzle + TEG-film-cooled-extension architecture already in `topics/06`/`topics/07`.

**Staged combustion vs GG — the KBKhA case** `[KBKhA Tables 1–2]`, LOX/kerosene, same thrust
class:

| | RD-0110 (GG) | RD-0124 (staged combustion) |
|---|---|---|
| Pc | 6.8 MPa | 15.53 MPa (×2.28) |
| Isp | 326 s | 359 s (+33 s) |
| LOX pump discharge P | 9.81 MPa | 33.28 MPa (×3.4) |
| Turbine inlet P | 5.79 MPa | 29.98 MPa |
| Turbine flowrate | 3.97 kg/s | 59.85 kg/s (closed cycle routes ~all flow through) |
| Turbine inlet T | 1050 K | fuel-rich (not tabulated) |
| Rotor speed | 18 400 rpm | 39 000 rpm (×2.1) |
| Turbopump weight | baseline | lower (higher power, less mass) |
| Feed-system weight | baseline | ~10 % heavier (boost pumps added) |

So going GG → staged combustion here: **Pc ×2.3 bought +33 s Isp but demanded LOX pump
discharge ×3.4 and rotor speed ×2.1** — the turbopump stress scales super-linearly with the
performance gain. Staged-combustion turbopumps need higher-strength materials, castings/HIP/
powder metallurgy, and cannot be developed by standalone component test (topic 09).

**A third real ox-preburner staged-combustion anchor — NK-33** `[NK-33-Mod Table I]`: real
Kuznetsov ox-rich-staged-combustion LOX/kerosene engine, Pc 2109 psia, **preburner Pc 4670
psia = 2.21× main-chamber Pc**, preburner MR 58 (deeply oxidizer-rich, as expected for an
ox-preburner), preburner outlet/turbine-inlet temp 670 °F (628 K). This sits alongside
`[SP-8107]`'s "may exceed 2.0×" and `[KBKhA]`'s 2.3×-Pc/3.4×-pump-discharge RD-0124 case as
a third, very concrete data point for the same pressure-multiplier question. **MR drifts
with throttle without an active control valve**: nominal MR 2.59 at 100 % power → 2.75 at
75 % Pc → 2.90 at 50 % Pc (an active MR valve, when used, gives ~20 % control range around
that). **Stability, for free**: NK-33's main chamber has had **zero baffles, acoustic
cavities, or other stability devices since very early NK-15 development**, with no recorded
combustion instability — achieved purely through injector-face propellant distribution
(coaxial fuel-swirl elements, outer row biased for mass/MR stratification). The *preburner*,
by contrast, does use injector-face baffles — i.e. on this engine the stability-critical
hardware is the small oxidizer-rich preburner, not the large MCC (topic 14).

**Real minimum-throttle fractions by cycle/architecture** `[Casiano-Throttling leaf 20-22]`
— fills a real gap this file previously had none of: **RD-170/RD-171** (Glushko, 4 chambers/
1 turbopump, 1,777,000 lbf vacuum thrust, staged combustion) **throttles to 56% of maximum
thrust**; **RD-180** (2 chambers, 933,400 lbf vacuum thrust) **throttles to 40%**. Both are
real, citable minimum-throttle numbers for large Russian multi-chamber staged-combustion
engines — a useful anchor if `cycles.py`/`design.py` ever wants a cycle-dependent throttle-
floor default rather than a single flat one. A real multiplicative-throttle-range example:
the Rocketdyne Advanced Maneuvering Propulsion Technology aerospike+inner-bell concept
(1967) individually throttled both its chambers 9:1, giving an **aggregate ~81:1 (9×9)**
effective range from independently-throttled multi-chamber architecture — a real precedent
for multi-chamber engines gaining throttle depth beyond any single chamber's own range.

**Advantages/disadvantages** `[SP-8107 Table V]`: GG — extensive experience, low component
interaction, good uprating, easy wide-range control; low performance, possible carbon
buildup. Expander — high performance, minimum components, clean fluid; Pc-limited to
~1000 psia, high system pressures, poor uprating, performance sensitive to component design.
Staged combustion — max performance, high Pc & throttling without penalty; needs higher pump
discharge pressures, limited uprating, performance sensitive to component design.

**Tripropellant/dual-mode architecture — background only, not a modeled cycle**
`[Tripropellant-CR150444 p.1, p.16, p.29]`: a 1977 Rocketdyne SSME-derivative concept study
for an engine that burns LOX+hydrocarbon (RP-1/CH4/C3H8) in "Mode 1" then switches to LOX/H2
in "Mode 2" — `engine_designer` has no tripropellant/mode-switching physics and this is not a
gap to fill, but two of its findings independently corroborate existing tool behavior: (1)
**RP-1 alone as regen coolant caps Pc at ~2000 psia** (coking at ~600°F) — at SSME-class Pc
(3237-4000 psia) RP-1 cannot survive as sole regen coolant, which is *why* H2 gets added in
some variants purely as a cooling workaround, not for performance — the same RP-1
Pc-vs-cooling constraint `cooling.py` already encodes, now corroborated from a completely
independent 1977 source (see `topics/06`). (2) **Fuel-rich LOX/hydrocarbon staged-combustion
preburners were found power-infeasible**: closing the power balance needed turbine inlet
temps **>2200 R**, exceeding 1977 turbine hardware capability with zero operating margin
even then — so only **LOX-rich** precombustors were carried forward for the hydrocarbon
variants. This is an independent, distinct-era engineering rationale for why real high-Pc
kerolox staged-combustion engines (RD-170/180-class) use LOX-rich rather than fuel-rich
preburners, consistent with what `staged_combustion.py` already models for kerolox FRSC/ORSC.

**Real SSME (FFSC) preburner/cycle detail, not previously in this file (2026-09-24)**
`[SSME-Orientation p.6, 19, 28-34]`: full real station-by-station propellant flow/energy
balance at 104.5% power level (pressures/temps/flowrates/rpm at every duct/pump/preburner/
turbine) — the most complete single real-engine full-cycle map in `claude_lit`. Real
combustion-device geometry: fuel preburner 264 coaxial elements/10.43in dia, oxidizer
preburner 120 elements/7.43in dia; preburner hot-gas mixture ratios **0.86 (fuel PB) / 0.60
(oxidizer PB)** — corroborates `[SP-8081]`'s existing 0.2-1.0 GG-mixture-ratio band
(`topics/10-gas-generators.md`). A real "two-stage combustion approximately 99.6% efficient"
figure is quoted — no c*-efficiency number for SSME existed anywhere in `claude_lit` before
this (`topics/03-combustion-and-cstar.md`). Real per-pump efficiency/turbine-PR table at
104.5% power: HPOTP pump eff. 71.8/75.8%, HPFTP 75.0%, turbine PR 1.50-1.53, turbine eff.
74.6-81.1% — runs a few points off `[SP-8107]`'s 1973 pre-operational SSME row (78.1/69.6%
pump, PR 1.56-1.59, 72.9-79.0% turbine); this is later, real, named-hardware data vs. a
pre-operational projection, worth a note if `validate.py`'s SSME turbopump spot-check
tolerance is ever tightened. Terminology flag: this source calls the 109% power point "FPL"
where `[SP-8107]` calls the same physical condition "EPL" — same condition, inconsistent
naming 25 years apart, unresolved.

**A real cycle-choice pairing rationale, tying cooling-method choice to cycle choice**
`[Quentmeyer-CR185257 §Comparison of Concepts/Conclusions p.8-9]`: TBC/transpiration-cooled-
throat liner concepts (minimize coolant heat pickup, since heat absorbed isn't needed for
anything) pair best with a **gas-generator cycle**; tubular-bundle/high-aspect-ratio-channel
concepts (maximize coolant heat pickup) are ideal for an **expander cycle** (where coolant heat
pickup directly drives the turbine). A real, citable design-tradeoff link between chamber-
liner cooling-architecture choice and cycle choice, complementary to the existing hydrogen-
embrittlement cycle-choice precedent already in `topics/12` (oxidizer-rich cycles chosen to
avoid H2-embrittlement of turbopump structure) — relevant to `staged_combustion.py`/
`expander.py`'s cycle-selection guidance if that's ever extended with a cooling-method
cross-check. Report-only — no code changed.

**A real system-level propellant/cycle-selection tradeoff history — pressure-fed hypergolic
chosen over pumped cryogenic** `[OMS-DesignEvo p.646-648]`: the Space Shuttle Orbital
Maneuvering System (OMS) was originally baselined (1969-70) as a **pumped LOX/LH2 system**
(2× gimbaled RL10A-3-3), then switched to a new **pressure-fed, Earth-storable NTO/MMH**
engine — real, dated engineering rationale in two separate steps, not one blanket call.
Step 1 (1970): system *complexity* from running a cryogenic OMS alongside a storable RCS on
one vehicle. Step 2 (1971, decisive): once external/expendable main-tank Orbiters let the
vehicle itself shrink, "sufficient internal volume for an oxygen/hydrogen OMS was a
significant penalty" even though LOX/LH2 cost less *mass* — a real, quantified **volume-
constrained, not mass-constrained** tradeoff (LOX/LH2's low bulk density, dominated by LH2,
costs disproportionately more volume per unit delta-v than a smaller vehicle can spare).
Existing Apollo hypergolic engines (LM ascent/descent) were then rejected in favor of an
all-new engine for a *third*, distinct reason: their ablative-chamber accumulated-burn-time
ratings (LMAE 500-900 s single-firing; LMDE 995 s) didn't cover the OMS's much longer
reusable-vehicle duty cycle (10-year/100-mission requirement) — a real **reusability-driven
ablative-vs-regen cooling-method decision**, distinct in kind from the propellant-chemistry
decision above, directly relevant to any future reusability framing for
`TR341_Config.cfg`-class pressure-fed hypergolic designs.

**Real redundancy-architecture rationale, tying engine count to component-level redundancy**
`[OMS-DesignEvo p.647, p.654-655]`: the OMS's **two-engine** ground rule (not one, not more)
is what actually set per-engine thrust/impulse sizing — after any single engine failure, the
*other* engine alone must complete the mission. This system-level redundancy is explicitly
why the flight bipropellant valve could move from Apollo-SPS's **quad-redundant** to
**series-redundant** (cutting weight/complexity): Apollo SPS was a single non-redundant
engine and needed full valve-level redundancy, while OMS has engine-level redundancy already,
so only series (not quad) component-level redundancy is needed to close the loop — a real
illustration of redundancy trading off against system architecture (engine count) rather
than being a fixed per-component rule. Combustion-stability hardware choice was also tied to
the reusability requirement rather than raw suppression performance: acoustic cavities (not
baffles) were selected specifically because they're "easier to cool and, therefore, less
subject to failure from either burnout or thermal cycling" (see `topics/14`).

## Caveats

- `[OMS-DesignEvo]` is a real engineering-history narrative (design-point numbers and
  decision rationale from an actual flown vehicle program), not a derivation source — no
  sizing equations. Its Fig. 10 baseline-performance summary box is heavily OCR-garbled;
  treat its thrust/Isp/Pc/MR figures as "very likely correct" reconstructions, not verbatim
  transcriptions (see `sources/aiaa-85-1694-oms-design-evolution.md`).
- The "k × Pc" pump-discharge multipliers are order-of-magnitude design guides from
  `[SP-8107]` for LOX/LH2 at MR 6 (Fig 11); the real value depends on jacket ΔP, injector
  ΔP, line losses and MR. J-2's 1.6 and RL10's 2.5 are the concrete anchors.
- `[J2X-Overview]` is a 2010 NASA program-status paper, not a design-criteria or correlation
  source — J-2X reached hardware/hot-fire-test maturity but never flew (Constellation was
  cancelled); treat its numbers as real late-development-stage hardware data, comparable in
  kind to `[AEDC-J2S]`, not flight-proven-in-service data.
- Expander feasibility is genuinely propellant- and thrust-dependent (`[SP-8107]`: H2 or
  light hydrocarbon; not at high thrust) — this is a real physical limit, not a modelling
  choice.
- Tap-off constants now have one real-hardware anchor (`[AEDC-J2S]`, J-2S altitude test
  data), but it's a single development engine's ground-test program (never flew
  operationally) with only 3 of 11 firings yielding clean main-stage numbers, and its
  reported Pc is itself flagged uncertain (tap-location ambiguity) — treat as corroborating
  context, not a tight quantitative calibration source.
- `[STBE-PW]` is a 392-page 1986-89 NASA Advanced Launch System booster-engine conceptual
  design study — all seven engines described (GG, split-expander, tap-off variants) are
  unbuilt/unflown design-point targets, not demonstrated hardware, unlike `[NK-33-Mod]`,
  `[Gubanov-1991]`, `[AEDC-J2S]`, or `[J2X-Overview]`. The "split expander" cycle name is
  this report's own P&W-specific usage. `[Tripropellant-CR150444]` is progress report #1 of
  an unfinished 9-month 1977 study — no final design, no hardware, no test data; its two
  corroborating findings (RP-1 cooling-Pc-limit, LOX-rich-preburner rationale) stand on their
  own as independent real-engineering conclusions, but the tripropellant/dual-mode
  architecture itself is background only. `[Casiano-Throttling]`'s RD-170/171/180 throttle
  fractions and multi-chamber aggregate-ratio example are the paper's own restatement of
  underlying references, not independently re-derived here.
- `[SSME-Orientation]` is Boeing-proprietary training material (June 1998) — treated per this
  project's licensing convention (derived facts only, no verbatim slide reproduction); see
  `topics/12`'s caveats for the FPL/EPL terminology-inconsistency flag.
- `[Schmucker-CycleCalc]` is a truncated PDF (23 of 42 real pages) — its derivation/methodology
  content above is trustworthy, but two lower-confidence curve fits in the surviving pages
  (effective γ_F and exit/chamber pressure ratio vs. area ratio) have OCR-uncertain
  coefficients per the source note and should not be used in code without re-verifying against
  a clean copy.

## Implications for engine_designer

> **STATUS (pump pressure-chain round, 2026-09-23):** the fixed multipliers below
> (`PREBURNER_DRIVE_MULT` 2.4 / `NON_DRIVE_MULT` 1.9 / `TURBINE_PR_STAGED` 1.9) are **GONE**.
> `staged_combustion.solve_staged_power_balance` builds discharge from this file's own
> `P_discharge = Pc + Σ drops` chain `[SP-8107 §3.1.1.1]` and SOLVES the turbine PR from a
> preburner-temperature input (SSME 1113 K `[ch12-materials]`, ox-rich 628 K `[NK-33-Mod]`),
> so discharge/Pc now emerges (SSME 42.5 vs 46.9 MPa, RD-0124 turbine inlet 29.5 vs 29.98 MPa)
> and rises with Pc. The expander fuel leg now carries its series turbine ΔP (RL10 2.64 vs
> 2.5 × Pc). The `[AEDC-J2S]` series-turbine note below is also acted on:
> `turbopump_sizing.split_turbine_work` splits dh by power for series (GG/tap-off) turbines.
> The bullets below are kept as history.

> **STATUS (per-cycle model round):** the `STAGED_COMBUSTION_PRESSURE_MULT` (1.6) and
> `STAGED_COMBUSTION_PRESSURE_RATIO` (40) corrections below are **DONE**. FRSC/ORSC/FFSC
> now live in `physics/staged_combustion.py` with `PREBURNER_DRIVE_MULT = 2.4` /
> `NON_DRIVE_MULT = 1.9` (asymmetric - only the pump feeding the preburner gets the big
> boost) and `TURBINE_PR_STAGED = 1.9` replacing the mislabelled 40. ORSC has its own
> (estimated, no-literature-anchor) `ORSC_GAS_PROPERTIES` table - hot, low-Cp,
> oxidiser-rich - calibrated to RD-180. Tap-off now uses the real main-chamber-MR
> combustion products (`combustion.mixture_cp_j_kgk`) film-cooled to ~1150 K, not the
> fuel-rich GG mix. FFSC (two preburners) and electric pump-fed (battery+motor, no
> turbine) are new cycles. All pinned by `validate.py::run_cycle_model_check()`.

- **`design.py` `STAGED_COMBUSTION_PRESSURE_MULT = 1.6`** (ASSUMPTIONS.md item #9): `[SP-8107
  Table VI]` says staged-combustion pump discharge pressure is "a nonlinear function of
  chamber pressure and **may exceed 2.0 times chamber pressure**", and `[KBKhA]` shows
  Pc ×2.3 → LOX pump discharge ×3.4. **The tool's 1.6 looks low** — 2.0 (or a nonlinear
  form) would better match the literature. This is the highest-value single correction in
  the cycle constants. **[DONE - now `PREBURNER_DRIVE_MULT = 2.4` on the preburner-feed
  pump only, `NON_DRIVE_MULT = 1.9` on the other, in `staged_combustion.py`.]** `[NK-33-Mod]`'s
  real preburner/MCC Pc ratio of **2.21×** is a third anchor, sitting comfortably between the
  tool's 1.9 (non-drive) and 2.4 (drive-pump) values — consistent with the direction already
  taken, not a further correction.
- **`design.py` `GG_PRESSURE_RATIO = 22.0`**: `[SP-8107]` "turbine pressure ratios of
  approximately **20**" for GG/tap-off; fleet range 15.7–29 `[Table III]`. 22 is fine (top
  of the mean band). `TAP_OFF_DUMP_ISP_FRACTION` — tap-off performance ≈ GG per `[SP-8107
  Table VI]`, so `TAP_OFF_DUMP_ISP_FRACTION = 0.80` vs `GG_DUMP_ISP_FRACTION = 0.55` says
  tap-off bleed is a better exhaust (tapped near the injector, cooler, more complete) —
  directionally right, magnitude unsourced.
- **`design.py` `GG_TIN_K = 1050`**: dead-on. `[KBKhA]` RD-0110 turbine inlet = **1050 K**
  exactly; `[SP-8107 Table III]` GG fleet 922–1061 K; `[SP-8081 Table I]` 811–1178 K. Cite
  `[KBKhA Table 2]` and `[SP-8107 Table III]`. ASSUMPTIONS.md item #6 can be upgraded from
  "representative" to "matches RD-0110 (KBKhA) and the SP-8107 GG-turbine fleet."
- **`design.py` `GG_ETA_TURBINE = 0.62`**: `[SP-8107 Table III]` GG-turbine efficiencies
  46–70 %, most 55–66 %. 0.62 is right in the band. Cite it.
- **`design.py` `STAGED_COMBUSTION_PRESSURE_RATIO = 40.0`**: if this is meant as the
  *turbine* pressure ratio it is very wrong — `[SP-8107]` says staged-combustion turbine PR
  is **< 1.5**. It is presumably the *preburner* pressure ratio (preburner pressure / Pc),
  which for SSME is ~1.8 (5880/3237). Either way, 40 needs re-checking against what it feeds.
  **[DONE - it was feeding the turbine `dh`, badly overstating enthalpy drop. Replaced by
  `staged_combustion.TURBINE_PR_STAGED = 1.9`, used for both the ideal `dh` and the
  derived-efficiency PR factor; tuned so the SSME entry in `run_turbopump_efficiency_check`
  still lands (derived turbine eta 0.80 vs real 0.79). The legacy constant remains in
  `design.py` but is unused by the staged branch.]**
- **`expander.py` feasibility check** (ASSUMPTIONS.md items #16–18): the literature strongly
  backs the *concept* — `[SP-8107 Table VI]`: expander "system limited to 1000-psia chamber
  pressure by power requirements and power available", "not feasible at high thrust level as
  heat transferred per pound of propellant pumped decreases", "limited to systems with H2 or
  light hydrocarbons as the main engine fuel." The tool's ability to compute a real
  feasibility *shortfall* (not just a warning string) matches how real expander engines
  (RL10, Vinci) are Pc/thrust-limited. `ETA_EXPANDER_TURBINE = 0.55` is low vs RL10's real
  74 % `[SP-8107 Table III]` — but RL10's turbine sees a combustion-heated... no, it's
  heated H2; RL10 turbine efficiency 74 % suggests 0.55 is conservative. Worth revisiting.
- **`cycles.py`** — tap-off and the staged cycles are **no longer** thin `gas_generator_result()`
  presets. `[SP-8107 Table VI]` confirms tap-off "performance same as bipropellant GG cycle"
  (so tap-off keeps `gas_generator_result()` as its OPEN-cycle builder, just with the real
  film-cooled chamber-products drive gas), while FRSC/ORSC/FFSC go through
  `staged_combustion.py` — closed cycles, no bleed Isp loss, which is why the tool excludes
  them from the `GG_FLOW_FRACTION` red-flag check. ORSC/FFSC reliability caveat matches
  `[KBKhA]`: oxidiser-rich turbines are a late-Soviet/Russian achievement (and full-flow a
  Raptor/BE-4-era one) needing special oxidation-tolerant design.
- **Tap-off turbine staging** `[AEDC-J2S]`: real J-2S hardware feeds the fuel and oxidizer
  turbines **in series** (one tapoff duct → fuel turbine → separate exhaust duct → oxidizer
  turbine → dump), not two parallel turbines each independently fed from the tap. If
  `cycles.py`'s tap-off builder currently sizes/derives the two turbines independently
  (as a symmetric GG-cycle preset would), this real precedent is worth checking against —
  report-only here, no code inspected/changed this pass.
- **`TAP_OFF_DUMP_ISP_FRACTION = 0.80`** (flagged in ASSUMPTIONS.md as "directionally right,
  magnitude unsourced"): `[AEDC-J2S]` doesn't give a tap-off bleed-fraction number directly
  (it's a test report, not a cycle-balance derivation), so this constant remains unanchored
  by real hardware data — the real MR/thrust/Isp numbers above can't be used to back out a
  bleed fraction without the engine's fuel-flow schedule, which this note didn't extract.
- **Electric pump-fed** (Rutherford) — new `physics/electric_pump.py`: battery + brushless
  motors, no turbine, no bleed, so engine Isp = chamber Isp. The trade is carried as mass
  (`battery_mass ∝ electrical_power × burn_time`), so it only pays off small/short-burn. The
  tool's derived pump efficiency is pessimistic at Rutherford pump scale and it models no
  boost pump, so the computed electric-hardware mass runs ~2× a real Rutherford — the
  `run_cycle_model_check()` band is deliberately wide and the direction (heavy) is the point.
- **`PRESSURE_FED_PC_TYPICAL_MAX_PA = 1.0e6`** (ASSUMPTIONS.md item #23): the warning band
  is grounded in real pressure-fed engines (Apollo SPS ~0.69, LM descent ~0.76, LM ascent
  ~0.83, R-4D ~0.69 MPa) — `[Sutton Table 8-1]` AJ-10 Pc 125 psia (0.86 MPa) and R-4D-class
  ~96 psia confirm the ~0.7–0.9 MPa cluster. The 6.9 MPa SuperDraco figure (composite tanks)
  is correctly noted in the warning rather than modelled.
- **`TAP_OFF_DUMP_ISP_FRACTION`** now has a second real hardware anchor beyond `[AEDC-J2S]`:
  `[STBE-PW]`'s LOX/CH4 tap-off engine bleeds ~5.4% of injector flow — a hydrocarbon-fuel
  data point (`[AEDC-J2S]` is LOX/LH2 only). Still not enough to back out a bleed-fraction
  number directly (neither source gives a full cycle-balance breakdown extractable from this
  note), so the constant remains unanchored in magnitude — report-only.
- **Split expander is a real, citable cycle variant `cycles.py`/`staged_combustion.py`
  doesn't model** — a second-pump-stage bypass fraction trading pump work for turbine-inlet
  temperature to buy higher Pc than a plain expander. Two real LOX/CH4 point designs exist
  (`[STBE-PW]`, 734/896 psia) if this is ever added as a distinct cycle option; the L*-penalty
  finding (worse atomization → larger required L* vs. GG-cycle engines at the same thrust
  class) is a real design cost to carry alongside it. Report-only — no code changed.
- **Cycle-dependent minimum-throttle-fraction defaults**: `[Casiano-Throttling]`'s RD-170/171
  (56%) and RD-180 (40%) real minimum-throttle numbers are a candidate anchor if
  `design.py`/`cycles.py` ever wants a cycle/architecture-dependent throttle floor rather than
  a single flat default — currently no such per-cycle throttle-floor concept exists in the
  tool. Report-only.
- **A real cooling-architecture-to-cycle-choice pairing rationale now exists**
  (`[Quentmeyer-CR185257]`, above: minimize-heat-pickup liner concepts → GG cycle;
  maximize-heat-pickup concepts → expander cycle) — a candidate cross-check if cycle-selection
  guidance is ever extended to consider chamber-cooling architecture. Report-only.
- **`validate.py`'s SSME spot-check now has a richer real-hardware reference point**
  (`[SSME-Orientation]`'s per-pump efficiency/turbine-PR table and 99.6% c* efficiency figure,
  above) alongside the existing `[SP-8107]` pre-operational numbers — a later, real,
  named-hardware data set if that spot-check's tolerance is ever revisited. Report-only.
- **A real closed-form Isp-vs-bleed-fraction formula now exists** (`[Schmucker-CycleCalc]`,
  above) if the tool's mass-averaged-blend `engine_isp_with_gg_dump` treatment is ever checked
  against a first-principles derivation rather than just `[SP-8107]`'s tabulated design-guide
  figure. Report-only — no code changed.
