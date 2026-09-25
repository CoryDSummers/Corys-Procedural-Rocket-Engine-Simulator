# 03 — Combustion and characteristic velocity (c*)

## Scope

What sets the chamber gas state (Tc, γ, M) and how completely the propellant burns; the
split between combustion loss and nozzle loss; frozen vs shifting equilibrium; the
residence-time / chamber-length dependence of combustion completeness. Feeds
`engine_designer/physics/combustion.py`.

## Key relations

**c\*** (see topic 01): `c* = √(g·γ·R·Tc/M) / Γ`. For a fixed propellant/MR, γ and M fall
in a known band and **c\* tracks Tc** `[Huzel §4.2]`. c\* peaks slightly fuel-rich of
stoichiometric because M rises faster than Tc near the peak.

**Delivered vs ideal** `[Sutton §5.5 p.180]`:

    Is,experimental ≈ (0.88 to 0.97) · Is,ideal
    of the 3–12 % shortfall, only ~1–4 % is combustion inefficiency
    → η_c* (combustion efficiency) ≈ 0.96–0.99 for a good chamber; the rest is nozzle loss

**Chamber pressure loss from gas acceleration** `[Sutton §5.4, Table 5-4]`: a narrow chamber
(cross-section only a little above throat area) loses ~126 psi (≈16 % of 773 psia)
accelerating the gas from the injector to the throat. Contraction ratio ≥ ~3 makes this
negligible `[Sutton §8.2 p.283]`.

**Combustion completeness vs chamber volume** `[Huzel §4.3 Fig 4-7]`, `[Sutton §8.2]`:
c\* rises with L\* (equivalently with stay time) to an **asymptotic maximum**. Past that,
more L\* only adds mass, cooled area and wall friction. The minimum stay time at which
performance plateaus defines the chamber volume for "essentially complete combustion."

**Frozen vs shifting equilibrium** `[Sutton §5.3]`:
- *Frozen*: gas composition fixed at the chamber value through the whole expansion.
- *Shifting*: composition re-equilibrates (recombination releases energy) as T and p drop
  in the nozzle → a few percent higher ideal Is than frozen.
- Real engines fall between (finite kinetics); "frozen" is the conservative assumption Huzel
  and the classic charts use.

## Empirical correlations & typical values

**η_c\* (c\* efficiency) anchors:**
- `[Huzel §4.2]`: ~0.975 for LOX/RP-1 and LOX/LH2 (good chamber + injector, frozen
  composition).
- `[TN-Dump]` design assumption: 97 % for GH2/LOX at 100 psig.
- `[SP-8081]`: GG combustion efficiency "normally 100 %" (huge fuel excess).
- `engine_designer/physics/validate.py` calibrated per pair against real engines: LOX/RP-1
  0.955 (RD-111), LOX/LH2 0.94 (RL10A-3-3), N2O4/MMH 0.90 (Aestus), Aerozine-50/NTO 0.9435
  (AJ10-137), Hydrazine 0.80 (MR-80B, catalytic decomposition).
- **Real LOX/RP-1 c\* efficiency anchor, well-instrumented NASA test** `[TP2862-LOXRP1
  Summary p.14-15]`: a 37-element O-F-O triplet injector achieved **C\*_eff ≈ 99.5%** at
  Pc≈4.1 MPa (627 psia) — a high-quality-injector upper-bound data point, above the tool's
  existing LOX/RP-1 0.955 calibration anchor (which is a different, real engine — RD-111 —
  not a contradiction, just a reminder that 0.955 is one real engine's number, not a ceiling).
  A companion fuel-rich-zoned injector on the same rig gave 95-96.2% at only a 4.5%-efficiency
  cost for a 47% throat-heat-flux reduction (see `topics/05-injectors.md` and `topics/06`).

**Stay time** `[Huzel §4.3 p.87]`, `[Sutton §8.2 p.284]`: **0.001–0.040 s** across thrust
chamber types and propellants (`ts = Vc/(ṁ·V̄)`, V̄ = mean specific volume). Corresponding
L\* range 15–120 in `[Huzel]`.

**Real chamber Tc / γ / M anchors** (frozen or near-frozen):
- LOX/RP-1, Pc 1000 psia, MR 2.35: Tc ≈ 6000 °F (3589 K), M ≈ 22.5, γ ≈ 1.222
  `[Huzel Fig 4-3 / Sample 4-1]`.
- LOX/LH2, Pc 800 psia, MR 5.22: Tc ≈ 5580 °F (3355 K), M ≈ 12, γ ≈ 1.213 `[Huzel Fig 4-4]`.
- LOX/LH2, Pc 773 psia, MR 5.55 (shifting): chamber T 3389 K, M 12.7, k 1.14; throat T 3184
  K, k 1.15 `[Sutton Table 5-4]`.
- N2O4/N2H4-UDMH, Pc 100 psia: see `[Huzel Fig 4-6]` (chart, not transcribed).

**High Is / high c\*** when: low average product molecular weight (hydrogen-rich) **or**
large heat of reaction / high Tc `[Sutton §5.5]`.

**Finite combustion length — empirical** `[TN-Dump §Results p.16–17]`: the dump-cooled
engine's measured heat flux was consistently *below* the zero-combustion-length prediction
over the **first ~3 in (of an 8-in injector-to-throat length)** for every one of 14 firings
— direct evidence that combustion is not complete at the injector face and that a
completeness curve vs axial position / chamber length is physically real.

**Injector effect on c\*** `[SP-8081 ref. 14]`: at a given MR, a UMR injector gives higher
temperature and higher c\* than a hot-core injector; at a given temperature the c\* is the
same — i.e. injector type shifts *where on the MR–c\* curve you sit*, not the curve itself.

**Real triplet-injector LOX/GH2 anchor** `[CR-128318 abstract, p.82]`: a 96-element, 4-ring
impinging-triplet injector (Pc 225 psia, L\*=20 in, contraction ratio 2.0, heat-sink hardware,
2-s firings) achieved **C\* efficiency ≈ 97 %, Isp efficiency ≈ 94 %** across 15 valid hot-fire
tests — "the efficiencies are about 97%, which suggests the chamber is sufficiently long for
near complete (or complete) vaporization of the LOX." A second, independent real data point
in the same `[Sutton §5.5]` 0.96–0.99-combustion-efficiency band cited above, for a different
element type/propellant combination than the tool's existing calibrated pairs. The same test
series found wall static pressure vs. area ratio matched the **full-shifting-equilibrium**
prediction closely, supporting shifting equilibrium as the right analytical baseline for this
propellant/MR/Pc regime (consistent with `[Sutton]`'s frozen-vs-shifting framing above).

**Real SSME c* efficiency — no number existed for this engine before (2026-09-24)**
`[SSME-Orientation p.6]`: "two-stage combustion approximately **99.6%** efficient" —a real,
high, citable c*-efficiency anchor for LOX/LH2 staged combustion at SSME-class Pc, filling a
gap this file previously had no SSME-specific data point for.

**A real LOX/LH2 c* curve fit — a candidate cross-check for `combustion.py`'s baked table
(2026-09-24)** `[Schmucker-CycleCalc p.13 eq.31]`: `c* = [3660−160r]·(p_c/700)^−0.022 m/s`,
valid for MR 4≤r≤7, Pc 500-3000 N/cm² — a clean, high-confidence closed-form fit (unlike two
other lower-confidence curve fits in the same source, flagged in its own note as OCR-uncertain
and not to be used without re-verification). Not yet checked against `combustion.py`'s baked
equilibrium-table c* at matching LOX/LH2 conditions — a candidate spot-check, not yet done.

## Worked numbers

`[Sutton Table 5-4]` LOX/LH2, Pc 773.3 psia, MR 5.551, chamber/throat area ratio 1.580,
shifting equilibrium: c\* = 2332.1 m/s. Chamber-end Mach 0.413 (already significant → the
~126 psi acceleration loss). Product mole fractions at chamber: H2O 0.636, H2 0.294, OH
0.032, H 0.034, O 0.002, O2 0.002 — i.e. ~7 % of the mass is unrecombined radicals whose
energy shifting equilibrium would recover.

## Caveats

- The classic charts (`[Huzel]` figs 4-3…4-6) are frozen-composition at one Pc each. A CEA
  run gives shifting-equilibrium values a few percent higher.
- η_c\* lumps mixing, vaporization, kinetics and (in the tool's calibration) any residual
  nozzle-model error into one number anchored on a real engine's real Is. Trust it for the
  calibrated pairs; treat it as an estimate for anything new until spot-checked.
- Aerozine-50/NTO thermochemistry: `[Huzel]` gives an N2O4/hydrazine-base chart; the tool
  currently copies the N2O4/MMH table. Chemically defensible (A-50 = 50/50 N2H4/UDMH, close
  to MMH energetically) but not independently sourced.

## Implications for engine_designer

- `combustion.py` `_TABLES` (6-point Tc/γ/M vs MR, linearly interpolated, Pc neglected) is a
  reasonable stand-in for the `[Huzel]` charts / a CEA run. Cross-check: LOX/RP-1 at MR 2.35
  should give Tc ≈ 3589 K, M ≈ 22.5, γ ≈ 1.222 `[Huzel Sample 4-1]`; LOX/LH2 at MR ~5.5
  should give chamber Tc ≈ 3355–3389 K `[Huzel / Sutton Table 5-4]`. (The tool's γ ≈ 1.19
  for LOX/LH2 is a nozzle-averaged effective value, higher than Sutton's chamber k = 1.14 —
  fine, as long as it's used consistently in `vandenkerckhove`.)
- `DEFAULT_ETA_CSTAR` per pair (ASSUMPTIONS.md item #1): the values are calibrated
  end-to-end against real engines and land in the `[Sutton §5.5]` "0.96–0.99 combustion, up
  to ~12 % total shortfall" envelope (the lower tool values absorb some nozzle-model
  residual too). This is the honest state — the file's own caveat is right.
- `completeness_factor(lstar, pair, atomization_mod)` / `L_MID_BASE` / `COMPLETENESS_*`
  (ASSUMPTIONS.md items #19, #20): the *shape* (c\* rises to an asymptote with L\*) is
  `[Huzel Fig 4-7]` — correct. The per-pair characteristic length `L_MID_BASE` (0.010–0.030
  m) is a chosen curve reference. `[TN-Dump]`'s "first ~3 in of an 8-in chamber" gives an
  order-of-magnitude sanity check: combustion-completion length is a few centimetres for
  GH2/LOX at low Pc, consistent with `L_MID_BASE[LOX/LH2] = 0.015 m`. A stronger model would
  tie it to a vaporization/mixing length (droplet size, injection velocity) per `[Sutton
  §9.1]` / `[Huzel §4.5]`.
- `STAGED_COMBUSTION_ETA_PENALTY = 0.985` (2-stage mixing loss on top of η_c\*): plausible
  in the "~1–4 % combustion loss" band `[Sutton §5.5]`; no direct source, flag remains.
- **Applied 2026-09-25 (P1 performance re-anchor):** bipropellant Isp now runs on the Cantera
  shifting-equilibrium tables (c*, Isp, pe/pc at eps 2-250, real Pc dependence); `DEFAULT_ETA_CSTAR`
  is this file's `[Huzel §4.2]` ~0.975 for every bipropellant, and the nozzle loss is a separate
  per-pair `ETA_CF` reverse-solved on the spot-check anchors. The frozen-vs-shifting framing above
  is now concrete: the tables carry both expansions (`isp_vac_frozen_s_by_eps`).
