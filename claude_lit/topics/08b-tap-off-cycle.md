# 08b — Tap-off cycle

## Scope

Thrust-chamber tap-off cycles: hot gas tapped from the main chamber, diluted to a turbine-safe
temperature, drives the turbines and is then dumped (J-2S: injected into the nozzle). Split out
of `08-engine-cycles.md` on 2026-10-18, when the J-2S batch pushed `08` past the 40 KB cap. The
cycle comparison table, GG / expander / staged-combustion material and turbine-staging rules
stay in `08`; turbine efficiency is in `09b`; the hot-gas mixer is `physics/tap_off.py`.

## Empirical data & real anchors

**Real tap-off-cycle anchor — J-2S** `[AEDC-J2S §2.1/§2.1.1, §4.2]`: the first real hardware/
test data in this reference set for tap-off specifically (previously "one development engine,
J-2S" with no real numbers cited). Real hardware confirms a **series turbine arrangement for
the two pumps** (tapped gas drives the fuel turbine first via the Hot Gas Tapoff Duct, then a
separate Fuel Turbine Exhaust Bypass Duct carries it on to drive the oxidizer turbine, before
final overboard dump) — worth checking against whatever `cycles.py`/`design.py` currently
assumes about tap-off turbine staging (single combined turbine vs. two in series), since this
real engine uses two. Main-stage performance (3 of 11 test firings with clean data): c\* ≈
7720–7800 ft/s, Isp ≈ 433–434 lbf·s/lbm, thrust 230,000–271,000 lbf, MR 4.6–5.1 (vs. 5.5
design nominal) — the c\*/Isp/MR figures are trustworthy. The reported Pc (1182–1279 psia) was
once flagged uncertain against a "~700–850 psia" nominal, but that range is the **J-2**'s. The
J-2S rated Pc is **1,200 psi** (J-2: 750) `[Vilja-J2S p.1]`, so AEDC's Pc is consistent
(resolved 2026-10-18).

**J-2S tap-off is a dilution scheme too** `[Vilja-J2S p.1, Fig. 2-3]`. Hot chamber gas is
"diluted with cold hydrogen" to the turbine inlet temperature. This is NOT raw chamber gas at
chamber MR, which is the picture behind the legacy `tap_off_model` (`TAP_OFF_TEMP_FRACTION`,
min(Tc × 0.55, 1150 K), chamber products not pumped). It is the same family as the STBE mixer
below.
- **Ports:** a single circumferential row of tap ports, hand-brazed into a chamber ring
  manifold (cast in production).
- **Path:** tap → hot-gas valve → fuel turbine → ox turbine in series, with a fixed bypass orifice
  in parallel with the ox turbine → exhaust injected into the nozzle. The solid-propellant gas
  generator feeds the fuel-turbine inlet.
- **Turbine inlet state.** Vilja gives no temperature, pressure or flow fraction. `[SP-8110
  Table I]` gives the J-2S (Mk 29-F) fuel turbine at **1,200 °F (922 K), 889 psia, PR 7.30,
  η 46 %**. With 1,200 psi Pc that is **0.74 × Pc** (derived), against the legacy model's
  0.855 × Pc and min(0.55·Tc, 1150 K).
  - Caveat: SP-8110's rating point may not be the 265K-lbf point (28,000 vs AEDC's 29,800 rpm).
- **Measured-balance tap-off temperature vs power level** `[J2S-Restart leaves 185-186]`. This
  is the first sourced LOX/LH2 tap-off temperature curve:
  - ≈1,620 °R (900 K) at rated thrust;
  - falling to a flat ≈1,260-1,270 °R (700-705 K) below ≈33 % thrust, with "1260 °R" at 10:1.
  - It is consistent with SP-8110's 922 K.
- **Where the dilution H2 enters** `[J2S-Restart leaves 21-22, 41-42]`. Jacket-exit coolant plus
  a valved fuel bypass mix in the injector-end **tap-off manifold** (a "coolant-rich manifold").
  There is no separate mixer vessel.
  - The tap port is NARloy-Z-lined and cooled by the surrounding coolant. It replaced an eroding
    321 CRES port.
  - One port sits ≈1.125 in (29 mm) from the injector face.
  - Still unknown: the tap-off flow fraction, the tap/turbine-inlet pressure and the port
    count. The 1968 spec in `[J2S-Boeing69]` gives none of them, only transducer full scales:
    fuel turbine inlet 0-1,500 psia, ox turbine inlet 0-200 psia `[p.10-517]`. The cycle data
    should be in Rocketdyne's R-7211 J-2S Interface Criteria Document, which we don't hold.
  - **Restart benefit** `[J2S-Boeing69 p.10-385]`: tap-off drive "relaxes the 4.5:1 EMR
    restraint during engine restart". It has no GG to keep in its flammability band. A real, concrete **spin-up solution**: a
one-shot solid-propellant turbine starter (SPTS) fires at main-stage start to spin the
turbines before tapped-gas flow alone can sustain them — the same "cold-start" problem any
tap-off or staged-combustion cycle without a dedicated spin-up GG has to solve. J-2S's defining
tap-off-enabled feature, a low-thrust **idle mode** (nominal 5000 lbf, MR 2.5, idle Pc only
18–31 psia) used for orbital-restart tank settling, is a real demonstrated use of tap-off's
"parallel, throttleable-independent-of-main-injector-flow" character that no other cycle in
the table above can do as simply.

**A real second LOX/CH4 tap-off data point, for a hydrocarbon fuel** `[STBE-PW leaf
341-344]`: a 1989 P&W preliminary-design study (Unique STBE Tap-Off, 750 Klbf SL thrust, Pc
2400 psia) gives a **tap-off flow rate of 132 lbm/s against a 2462 lbm/s injector flow
(~5.4%)**. The mechanism matters more than the number `[STBE-PW p.317 §4.3.1.1]`: the engine
taps **1.9 % of O/F-biased chamber gas** into a **hot-gas mixer** where **cold methane (12.5 %
of the pumped fuel, via the fuel bypass valve)** dilutes it to **1,800 R (1,000 K) at 2293 psia
(0.955 x Pc)**. The fuel-rich mix drives the methane turbine, then the oxygen turbine, in
series. So a hydrocarbon tap-off turbine does NOT see chamber gas "film-cooled" to ~1,150 K.
It sees GG-like fuel-rich gas at ~1,000 K, most of it pumped bypass fuel. (Corrected
2026-09-26: this passage and the source note first read it as "tapped near the throat".)
Implemented as `physics/tap_off.py` (the hot-gas mixer, default for LOX/CH4 and LOX/RP-1)
and gated by validate "TAP-OFF".


## Caveats

- Tap-off constants now have one real-hardware anchor (`[AEDC-J2S]`, J-2S altitude test
  data), but it's a single development engine's ground-test program (never flew
  operationally) with only 3 of 11 firings yielding clean main-stage numbers — treat as corroborating
  context, not a tight quantitative calibration source. (Its Pc is consistent with the 1,200 psi
  rating `[Vilja-J2S]`.)

## Implications for engine_designer

- **Tap-off turbine staging** `[AEDC-J2S]`: real J-2S hardware feeds the fuel and oxidizer
  turbines **in series** (one tapoff duct → fuel turbine → separate exhaust duct → oxidizer
  turbine → dump), not two parallel turbines each independently fed from the tap. If
  `cycles.py`'s tap-off builder currently sizes/derives the two turbines independently
  (as a symmetric GG-cycle preset would), this real precedent is worth checking against —
  report-only here, no code inspected/changed this pass. `[Vilja-J2S Fig. 2]` confirms the
  series arrangement and adds a fixed bypass orifice in parallel with the ox turbine.
- **Legacy LOX/LH2 tap-off picture is contradicted** (`tap_off_model` "legacy", which is
  LOX/LH2's default under "auto").
  - The J-2S also dilutes the tapped gas with cold H2 `[Vilja-J2S p.1]`.
  - The cited fuel-turbine inlet is 922 K at 0.74 × Pc `[SP-8110 Table I]` vs the legacy
    min(0.55·Tc, 1150 K) at 0.855 × Pc. The "J-2S ~1,140 K" note in ASSUMPTIONS.md did trace to
    nothing, but SP-8110 had the real value all along.
  - A hydrolox mixer (like the LOX/CH4 / LOX/RP-1 one) is the physically right extension.
    Its temperature target now has a source: 900 K rated, ≈700 K throttled `[J2S-Restart]`,
    below the legacy `TAP_OFF_TURBINE_LIMIT_K` 1,150 K. The H2 dilution flow split is still
    unsourced (OPEN_QUESTIONS). Report-only.
- **Tap-off throttling** `[Vilja-J2S p.2-4]`:
  - Throttle by modulating the hot-gas tap valve. There are no GG flammability limits, and the
    valve need not seal at closure. 6:1 was demonstrated.
  - Uprating needs "greater tapoff flows", which are "readily available". The eps-40 Isp drops
    436.0 → 434.5 s going from 265K to 320K lbf.
- **`TAP_OFF_DUMP_ISP_FRACTION = 0.80`** (flagged in ASSUMPTIONS.md as "directionally right,
  magnitude unsourced"): `[AEDC-J2S]` doesn't give a tap-off bleed-fraction number directly
  (it's a test report, not a cycle-balance derivation), so this constant remains unanchored
  by real hardware data — the real MR/thrust/Isp numbers above can't be used to back out a
  bleed fraction without the engine's fuel-flow schedule, which this note didn't extract.
