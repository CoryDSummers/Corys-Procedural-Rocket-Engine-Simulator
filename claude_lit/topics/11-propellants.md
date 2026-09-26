# 11 — Propellants

## Scope

Per-pair anchor values (MR, Tc, γ, M, c\*, Isp), densities, hypergolicity, monopropellants,
and the frozen-vs-shifting distinction. Feeds `engine_designer/physics/combustion.py`
(`_TABLES`, `PROPELLANT_DENSITIES`, `MONOPROPELLANT_PAIRS`).

## Key relations

Combustion state feeds c\* and everything downstream (topics 01, 03):
`c* = √(g·γ·R·Tc/M) / Γ`. High c\* / Isp needs **low product molecular weight** (H-rich) or
**high heat of reaction** (high Tc) `[Sutton §5.5]`.

## Anchor values by pair

All from `[Huzel]` frozen-composition charts and worked examples, and `[Sutton Table 5-4]`
and `[Sutton Table 8-1]` real engines. **These are the numbers `combustion.py` should
reproduce.**

### LOX / RP-1

| Source | Pc | MR | Tc | γ | M | c\* | Is (vac) |
|---|---|---|---|---|---|---|---|
| `[Huzel Fig 4-3 / Sample 4-1]` | 1000 psia | 2.35 | 6000 °F = 3589 K | 1.222 | 22.5 | 5810 ft/s ideal → 5660 design | ~289 s (SL Is 270 at ε 14) |
| `[Sutton Table 8-1]` RS-27 (GG) | ~500–700 psia | 2.27 (engine) | — | — | — | 5540 ft/s | 294 s |
| `[SP-8107]` RD-111 class (F-1 GG) | 1122 psia | ~2.27 | — | — | — | — | F-1 ~304 s |
| `validate.py` anchor | RD-111, 7.85 MPa, ε 18, MR 2.39 | | | | | | 309.5 s vac / 268.0 SL |

Density: RP-1 ≈ 810 kg/m³, LOX ≈ 1141 kg/m³.

**RP-1 vs. RP-2 real property differences (2026-09-24)**: `[Outcalt-RP1RP2]`'s real measured
data: "viscosities of RP-1 are between 3 and 5% lower than those of RP-2 at the same
temperatures, whereas their density, speed of sound, and adiabatic compressibility values
differ by less than 1%" — attributed to RP-2's higher C16-alkane content vs. RP-1's C14
ceiling. `[Huber-RP1RP2]` gives real surrogate compositions for both (4-component models,
`topics/06b-cooling-methods-and-chemistry.md` has the full data) — the tool only models a single
generic RP-1 entry today; RP-2's slightly higher density/lower viscosity would be a minor,
low-priority addition if a distinct RP-2 propellant pair is ever wanted. Report-only.

### LOX / LH2

| Source | Pc | MR | Tc | γ | M | c\* | Is (vac) |
|---|---|---|---|---|---|---|---|
| `[Huzel Fig 4-4 / Sample 4-1]` | 800 psia | 5.22 | 5580 °F = 3355 K | 1.213 | 12.0 | 7670 ft/s ideal → 7480 design | 440 s (at ε 40) |
| `[Sutton Table 5-4]` (shifting) | 773 psia | 5.55 | chamber 3389 K / throat 3184 K | chamber 1.14 / throat 1.15 | 12.7–12.8 | 2332 m/s = 7651 ft/s | — |
| `[Sutton Table 8-1]` RL10B-2 (expander) | — | 5.88 | — | — | — | 7578 ft/s | 462 s |
| `[Sutton Table 8-1]` LE-7 (staged comb) | 1917 psia | 6.0 | — | — | — | 5594.8 ft/s* | 445.6 s |
| `validate.py` anchor | RL10A-3-3, 2.72 MPa, ε 61, MR 5.0 | | | | | | 442.2 s vac / 186.0 SL |

\*LE-7's low tabulated c\* looks like a units/transcription artefact in `[Sutton Table 8-1]`;
7578 (RL10B-2) is the reliable LOX/LH2 c\* anchor.
Density: LH2 ≈ 71 kg/m³ (Sutton uses 4.4 lbm/ft³ = 70.5), LOX ≈ 1141 kg/m³.
Note chamber γ = 1.14 `[Sutton]` vs the tool's effective γ ≈ 1.19 — the tool value is a
nozzle-averaged effective ratio, legitimately higher (see topic 03).

### N2O4 / MMH  (and Aerozine-50 / NTO)

| Source | Pc | MR | c\* | Is (vac) |
|---|---|---|---|---|
| `[Sutton Table 8-1]` R-4D-class RCS (N2O4/MMH) | ~96 psia | 2.0 | 5180 ft/s | 290 s |
| `[Sutton Table 8-1]` AJ-10-118I (N2O4/A-50) | 125 psia | 1.90 | 5606 ft/s | 320 s |
| `[Huzel Fig 4-6]` N2O4 / N2H4-UDMH | 100 psia | ~1.6–2.6 (chart) | — | — |
| `validate.py` anchors | Aestus (N2O4/MMH) 1.1 MPa ε 84 MR 1.9 → 306.0 s vac; AJ10-137 (A-50/NTO) 0.68 MPa ε 62.5 MR 1.6 → 314.5 s vac | | | |

Density: MMH ≈ 880 kg/m³, A-50 ≈ 903 kg/m³, N2O4 ≈ 1440 kg/m³.
`[SP-8081 p.7]` calls A-50, UDMH and hydrazine "energetic" propellants — they release energy
by exothermic decomposition before oxidation, which is why their GG mixture ratios are < 0.2
and why A-50 ≈ MMH energetically (the basis for the tool copying the MMH table for A-50).

### LOX / CH4 and LOX / RP-1 / C3H8 — real 7-way booster-engine trade data

`[STBE-PW leaf 25, Table 1-1]`: a real 1989 P&W trade study of seven 625-Klbf-class booster
engines across three hydrocarbon fuels (RP-1, methane, propane) and varying coolant/Pc/eps —
a directly citable cross-check anchor spanning fuels this reference set didn't previously
have side-by-side at matched thrust:

| Config | Propellant | Coolant | MR | Pc (psia) | Isp vac/SL (s) | eps |
|---|---|---|---|---|---|---|
| STBE-1A | LOX/RP-1 | RP-1 | 2.90 | 1275 | 316.0/264.3 | 25 |
| STBE-1B | LOX/RP-1 | LOX | 2.90 | 1667 | 318.4/273.5 | 35 |
| STBE-2 | LOX/RP-1 | LH2 | 3.12 | 3500 | 360.1/318.2 | 55 |
| STBE-3 | LOX/CH4 | CH4 | 3.57 | 2333 | 341.5/302.6 | 40 |
| STBE-4 | LOX/CH4 | LH2 | 3.64 | 3500 | 369.5/326.5 | 55 |
| STBE-5 | LOX/C3H8 | C3H8 | 3.20 | 2333 | 333.9/291.4 | 40 |
| STBE-6 | LOX/C3H8 | LH2 | 3.38 | 3500 | 363.2/321.0 | 55 |

**Explicit, stated engineering rationale for methane beating RP-1 and propane** `[STBE-PW
leaf 28, Table 1-4]` — a rare real-program justification, not just a performance number:
highest combustion efficiency, more predictable heat flux, cleaner GG gas, simpler injector
design, self-purging (reduces cleaning), very stable combustion, good coolant with a **high
coking-onset temperature** (vs. RP-1's ~600°F limit), allows transpiration cooling, allows
coaxial gaseous-fuel injection, improves injector-face cooling, lower environmental spill
impact (volatile, non-toxic, disperses readily). Directly citable for any `engine_designer`
propellant-selection guidance text if a LOX/CH4-vs-LOX/RP-1 tradeoff advisory is ever added.

### N2O4 / Aerozine-50 — real Apollo-era pressure-fed hypergolic engines

`[ApolloPP-1195 Table I, p.9]`: a 1966 NASA MSC survey gives real side-by-side specs for all
three Apollo primary-propulsion engines — the first real pressure-fed hypergolic engine data
in this reference set (prior N2O4/MMH-family coverage above is all pump-fed real-engine
Δp/Isp data, not pressure-fed):

| Parameter | SPS (Aerojet) | LEM Descent (TRW) | LEM Ascent (Bell) |
|---|---|---|---|
| Thrust, lbf | 21,500 | 10,500→1050 (throttleable 10:1) | 3500 |
| Mixture ratio | 2.0 | 1.6 | 1.6 |
| Chamber pressure, psia | 100 | 100 | 150 |
| Chamber/nozzle material | Ablative | Ablative | Ablative (fully — no radiation extension) |
| Nozzle extension | Radiation-cooled columbium, ε 6→62.5 | Radiation-cooled Cb ε 6→40 / Ti ε 40→62.5 | none |
| Injector | Aluminum, baffled unlike-doublet | Inconel, coaxial/variable-area (pintle-like) | Aluminum, flat/baffled triplet |
| Film-cooling fraction | 7% (showerhead) | n/a (inherent to variable geometry) | 29% (unlike-doublet barrier, MR 1.05) |
| Ae/At | 62.5 | 47.5 | 45.4 |
| Dry weight, lb | 650 | 350 | 210 |

All three are pressure-fed, ablatively-cooled, N2O4/Aerozine-50 (50% UDMH/50% hydrazine), a
deliberate reliability-driven package: storable propellants (no cryogenic zero-g venting
problem), ablative chambers ("rugged... high resistance to sudden failure" — graceful
degradation vs. burn-through), pressure-fed (no turbopump complexity), and redundant
series-parallel valve topology on every moving part. See `topics/05-injectors.md` and
`topics/06b-cooling-methods-and-chemistry.md` for the barrier-cooling-MR and ablative-liner
detail this table doesn't capture, and `topics/08-engine-cycles.md` for a real later (Shuttle
OMS) design-history case of why a *newer* program moved away from this exact propellant/
cycle combination for a larger reusable vehicle.

### Hydrazine (monopropellant)

- Catalytic decomposition over a bed (Shell 405 / Aerojet S-405 iridium catalyst
  `[SP-8081 §2.2.2]`); no mixture ratio, one propellant block.
- Representative decomposition state (partial NH3 dissociation): the tool uses Tc 1400 K,
  γ 1.30, M 11.0 — a chosen single point, verified only by Is match.
- `validate.py` anchor: MR-80B (Mars Landing Engine), 2.4 MPa, ε 27.2 → **223.0 s vac**,
  79.0 s SL; tool reproduces 222.4 s.
- `[Huzel Table 4-1]`: "H2O2/RP-1 including catalyst bed" needs L\* 60–70 in — a hydrazine
  catalyst bed is comparably long.
- Deepest-throttling of any injector option (MR-80B: 100 % to ~8 %) `[validate.py / MR-80B]`.

## General facts

- **Experimental Is is 3–12 % below ideal; only ~1–4 % of that is combustion** `[Sutton
  §5.5]`. This is the envelope `DEFAULT_ETA_CSTAR` lives in.
- **Frozen vs shifting**: shifting-equilibrium ideal Is is a few percent above frozen
  `[Sutton §5.3]`. The classic `[Huzel]` charts are frozen; a CEA run defaults to shifting.
- Propellant density drives *tank* and *turbopump* design far more than combustion: IRFNA
  98 lbm/ft³ down to LH2 4.4 lbm/ft³ — a 22:1 range `[SP-8107 §2.1.1.3]`.
- Hypergolic pairs (N2O4/MMH, N2O4/A-50) self-ignite on contact → simpler ignition, but
  injector design differs from non-hypergolic (small positive β angle helps, topic 05)
  `[Huzel §4.5, Sutton §7]`.
- `[Sutton Ch. 7]` has quantitative property tables (vapor pressure, viscosity, freezing/
  boiling points, Cp) — leaves 257–280, not transcribed here.
- **A real volume-constrained (not mass-constrained) propellant tradeoff** `[OMS-DesignEvo
  p.646]`: LOX/LH2's low bulk density (dominated by LH2, the same 22:1 density range cited
  above) can cost more *tankage volume* per unit delta-v than a small/volume-limited vehicle
  can spare, even when it costs less *mass* — the real reason the Space Shuttle OMS switched
  from a pumped LOX/LH2 baseline to pressure-fed storable NTO/MMH once the Orbiter itself
  shrank (external, expendable main tanks). See `topics/08-engine-cycles.md` for the full
  design-history narrative.

## Caveats

- `[Huzel]` charts are single-Pc, frozen-composition; interpolating Pc introduces small
  errors.
- The tool's Aerozine-50/NTO table is a verbatim copy of N2O4/MMH — chemically defensible
  (A-50 ≈ MMH energetically) but not independently sourced (ASSUMPTIONS.md item #2).
- Hydrazine's single-point decomposition state (ASSUMPTIONS.md item #3) is a modelling
  choice, not from a decomposition reference; it's calibrated only against MR-80B's Is.
- `[STBE-PW]`'s 7-way trade table is from unbuilt/unflown 1986-89 conceptual designs, not
  demonstrated hardware — treat as design-point targets from a single design team's
  methodology, not flight-proven Isp/MR/eps values the way the RD-111/RL10A-3-3/Aestus/
  AJ10-137/MR-80B `validate.py` anchors above are.

## Implications for engine_designer

- `combustion.py` `_TABLES` cross-check targets:
  - LOX/RP-1 @ MR 2.35 → Tc ≈ 3589 K, M ≈ 22.5, γ ≈ 1.222 `[Huzel Sample 4-1]`.
  - LOX/LH2 @ MR ~5.5 → chamber Tc ≈ 3355–3389 K `[Huzel / Sutton Table 5-4]`; effective γ
    1.19 acceptable (chamber value 1.14).
  - N2O4/MMH @ MR ~1.9–2.0 → c\* ≈ 5180 ft/s (1579 m/s), matches Aestus calibration.
  - A-50/NTO @ MR ~1.9 → c\* ≈ 5606 ft/s (1709 m/s), Is ≈ 320 s `[Sutton AJ-10]`.
  - Hydrazine → Is ≈ 223 s (MR-80B).
- `PROPELLANT_DENSITIES` cross-check: RP-1 810 / LOX 1141 / LH2 71 / MMH 880 / A-50 903 /
  N2O4 1440 kg/m³ — all consistent with `[Sutton §7]` / `[SP-8107 §2.1.1.3]` (LH2 4.4 lbm/ft³
  = 70.5 kg/m³; IRFNA 98 lbm/ft³).
- `L_MID_BASE` per pair (topic 03): could be sanity-anchored to `[Huzel Table 4-1]` L\*
  ranges (LOX/RP-1 needs the most chamber length; LOX/LH2 the least among cryo).
- A future LOX/CH4 addition (README "phase 2") would need its own frozen-composition table +
  a real-engine spot-check per the project convention — `[Sutton Ch. 5]` has LOX/CH4
  performance charts. `[STBE-PW]`'s real 7-way trade table above (real MR/Isp/eps at matched
  Pc across RP-1/CH4/C3H8) is a directly usable cross-check point if/when that addition is
  calibrated, alongside its explicit methane-selection rationale (coking-onset temperature,
  combustion cleanliness) for any propellant-choice advisory text.
