# 13 — Mass estimation and propellant budget

## Scope

Estimating engine dry mass (especially the turbopump), the turbopump equivalent-weight
factor, and the propellant budget (residuals, boiloff, startup/shutdown, reserves). Feeds
`engine_designer/physics/mass_model.py` and `turbopump.py`.

## Key relations

**Wall / shell mass** `[Huzel §2.4]` (topic 12): `t = SF·Pc·r/σ`, shell mass = Σ(frustum
lateral area × local `t` × ρ). This is `mass_model.shell_mass_kg`.

**Turbopump mass from specific power** `[SP-8107 Table I]`, `[turbopump.py]`:

    m_turbopump = P_turbopump / specific_power

**Turbopump equivalent-weight factor** `[SP-8107 §2.1.2, §3.1.1.5]`: in system trades the
turbopump is charged not just its dry mass but an *equivalent weight* that also captures its
effect on tank pressurisation, feed-line mass and propellant residuals — used to pick
rotational speed and stage count. (Concept, not a single formula in the monograph.)

## Empirical correlations & typical values

**Turbopump-assembly specific power** `[SP-8107 Table I, mid-1973]` — "specific horsepower,
hp/lbm"; **× 1644 ≈ W/kg**:

| Engine | hp/lbm | ≈ W/kg |
|---|---|---|
| A-7 (Redstone) | 2.22 | 3 650 |
| MA-5 booster | 3.59 | 5 900 |
| MB-3 (Thor) | 5.40 | 8 900 |
| LR87-AJ-3 (Titan I) | 5.11 | 8 400 |
| YLR81-BA-11 (Agena) | 5.81 | 9 550 |
| MA-5 sustainer | 7.27 | 12 000 |
| J-2 (whole assy / one unit) | 7.73 / 21.60 | 12 700 / 35 500 |
| H-1 (Saturn IB) | 7.98 | 13 100 |
| RL10A-3-3 (Centaur) | 9.03 | 14 800 |
| YLR87-AJ-7 (Gemini-Titan) | 10.70 | 17 600 |
| **F-1 (Saturn IC)** | **16.6** | **27 300** |
| SSME (EPL, whole / one unit) | 50.0 / 108.9 | 82 000 / 179 000 |

**Turbopump-assembly masses** `[SP-8107 Table I]`: F-1 3150 lbm (1429 kg); J-2 305 / 369
lbm; RL10A-3-3 76.1 lbm (34.5 kg); YLR81-BA-11 (Agena) 60.5 lbm — smallest. SSME 555 / 701
lbm.

**Thrust-chamber masses** `[Sutton Table 8-1]`: RL10B-2 < 150 lbf (< 68 kg) sea-level
weight; RS-27 730 lbf (331 kg); AJ-10 137 lbf (62 kg); LE-7 1560 lbf. Gimbal-mount weight:
RL10B-2 < 10 lbf, RS-27 70 lbf, AJ-10 23 lbf, LE-7 57.3 lbf — i.e. the gimbal mount is
~2–10 % of the thrust-chamber mass.

**Real whole-engine mass/T-W anchor — NK-33** `[NK-33-Mod Table V]`: basic engine (AJ26-58)
dry 3104 lbm / wet pre-fire 3335 lbm / wet operating 3409 lbm; restartable variant (AJ26-59)
dry 3216 lbm. Vacuum thrust/dry-weight ≈ 379,000 lbf / 3104 lbm ≈ **122:1** — a very high
real T/W ratio (ox-rich staged combustion + thin-margin Russian design practice), useful as
a sanity-check upper bound if the tool's own T/W output for a staged-combustion design is
ever compared against a real engine.

**Propellant budget** `[Sutton §10.3]` — the usable propellant is the loaded propellant
minus: trapped/residual propellant in lines and tanks, boiloff (cryogens), startup and
shutdown transient consumption, unusable ullage, outage (MR-control tolerance), and flight
performance reserve. Each is a small percentage; together they can be several percent of the
load. (The tool doesn't model propellant/tank mass — RealFuels does — but this is why
`Isp` alone doesn't set stage performance.)

**Component tolerance stack-up** `[SP-8107 §2.3.1.2]`: effects of component manufacturing
tolerances on required turbopump operating range are combined **root-sum-square** (√Σ of
squares), not worst-case algebraic sum, assuming Gaussian distributions.

## Caveats

- Specific-power figures are turbopump *assembly* as flown; a W/kg derived from a
  component-only mass (Table II) will differ.
- SSME rows are pre-operational projections (mid-1973).
- The tool's dry mass is an explicit **lower bound** — it omits injector, valves, actuators,
  lines, mounting structure, flanges, gimbal bearing, and manufacturing margin beyond one
  flat safety factor. `[Sutton Table 8-1]` gimbal-mount weights (~2–10 % of chamber mass)
  are one concrete omitted item.

## Implications for engine_designer

- **`turbopump_tech.py` specific power** — the single strongest new backing from this
  literature set (also in topic 09):
  - `advanced = 70000 W/kg` (ASSUMPTIONS.md item #41, "NOT independently sourced"): `[SP-8107
    Table I]` SSME (EPL) = 50.0–108.9 hp/lbm ≈ **82 000–179 000 W/kg**. 70 000 is
    *conservative* for SSME-class staged combustion. Upgrade the flag to "bracketed below
    SSME assembly figure (SP-8107 Table I)."
  - `mature = 36000 W/kg` (from F-1): `[SP-8107 Table I]` F-1 assembly = 16.6 hp/lbm ≈
    **27 300 W/kg** (3150 lbm assembly). The 36 000 figure is closer to J-2's single-unit
    21.6 hp/lbm ≈ 35 500 W/kg. Both are defensible mature-GG numbers; the ~25 % spread is
    real and depends on which engine and whether "assembly" or "unit". Cite `[SP-8107 Table
    I]` and note the range.
  - `early_simple = 1300 W/kg` (from V-2): `[SP-8107 Table I]` A-7 (Redstone, earliest US
    turbopump) = 2.22 hp/lbm ≈ **3 650 W/kg**; the V-2 is earlier still, so 1300 as a lower
    anchor is consistent.
- **`mass_model.py` `SAFETY_FACTOR = 1.5`**: = `[Huzel eq. 2-10]` ultimate factor (topic 12).
- **Gimbal-mount mass**: `[Sutton Table 8-1]` gives ~2–10 % of thrust-chamber mass — a
  concrete number for a future addition to the dry-mass model (currently omitted). Gimbal
  actuator loads/rates are in topic 16.
- **`turbopump.py` mass = P/specific_power** is exactly the `[SP-8107 Table I]` "specific
  horsepower" relation — the right form.
- **RSS tolerance stacking** `[SP-8107 §2.3.1.2]` is the same statistical principle behind
  TESTFLIGHT-style residuals modelling (`residualsThresholdBase` in
  `controller_tech.py` / export) — worth noting if that model is ever made physical rather
  than a per-tier constant.
