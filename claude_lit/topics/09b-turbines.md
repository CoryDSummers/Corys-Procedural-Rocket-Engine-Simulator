# 09b — Turbines (turbopump drive turbines)

## Scope

Turbopump drive turbines:
- efficiency definitions and bookkeeping (total-to-static vs total-to-total);
- velocity ratio vs loading and staging selection;
- loss correlations (tip clearance, partial admission, disk friction, Reynolds);
- the real rocket-turbine fleet.

This file was split out of `09-turbopumps.md` on 2026-10-18, when adding `[SP-290]` would have
pushed that file past the 40 KB cap. Pumps, inducers, shafts, seals and the pump meanline stay in
`09`; turbine materials are in `09` and `12`; tap-off / GG drive gas is in `08` / `10`.

## Real rocket-turbine fleet and design criteria (`[SP-8110]`)

**Turbines — fleet data, all total-to-static** `[SP-8110 Table I p.10]`:

| Engine | Type | hp | rpm | Dm in | U ft/s | Tt1 °F | PR | U/C0 | η |
|---|---|---|---|---|---|---|---|---|---|
| F-1 | 2-row VC | 54,359 | 5,490 | 34.9 | 840 | 1550 | 16.3 | 0.20 | 60.5 % |
| H-1 (geared) | 2-stage PC | 4,007 | 32,800 | 9.0 | 1290 | 1200 | 17.7 | 0.42 | 62.5 % |
| J-2 fuel | 2-row VC | 8,749 | 26,052 | 12.5 | 1448 | 1200 | 6.35 | 0.18 | 60.1 % |
| J-2 ox | 2-row VC | 2,604 | 8,650 | 15.5 | 585 | 740 | 3.16 | 0.11 | 48.4 % |
| Atlas sustainer | 2-stage PC | 1,680 | 38,000 | 6.0 | 995 | 1075 | 25 | 0.39 | 46.3 % |
| M-1 fuel | 2-row VC | 74,138 | 12,961 | 23.2 | 1310 | 1000 | 3.87 | 0.19 | 65.0 % |
| RL10 A3-3 | 2-stage PC | 660 | 28,670 | 5.9 | 738 | −88 | 1.42 | 0.35 | 74.0 % |

- **Staging is chosen by the ACHIEVABLE U/C0, not by propellant** `[SP-8110 §3.1.4 p.83]`:
  - reaction above ~0.45
  - single-row impulse / pressure-compounded at ~0.30–0.45
  - 2-row velocity-compounded at ~0.20–0.30
  - below ~0.15, one or two more rows are worth +10 / +23 points

  U is capped by stress (fleet pitchline 1000–1500 ft/s). On a DIRECT-DRIVE shaft U is also
  capped by the pump shaft speed × a practical wheel size. That is why the slow F-1 (5,490 rpm)
  lands at 0.20, while the H-1's turbine is geared to 32,800 rpm and reaches 0.42.
  `[SP-8101 p.3]`: the H-1 and RL10 turbopumps are geared.
- **Idealized η vs U/C0 peaks** `[SP-8110 Fig 13 p.17]`: 1-row ~80 % at 0.42, 2-row ~69 % at
  0.23, 3-row ~54 % at 0.13. Real hardware runs 5–10 points lower.
- **Loss correlation** `[SP-8110 Fig 55]`: the 2-row VC η multiplier vs blade-size ratio
  Dm/An (shrouded ≈ 1.076 − 0.0455·Dm/An). The monograph's worked example reproduces the J-2
  fuel turbine's 60.1 %.
- **Frozen turbine-gas properties** `[SP-8110 Table III p.16]`: LOX/RP-1 at 1300 / 1500 °F has
  cp 0.648 / 0.656 Btu/lb·°R (≈ 2,710 / 2,750 J/kg·K) and γ 1.115 / 1.132. LOX/LH2 at
  1200 °F has cp 1.91 Btu/lb·°R (≈ 8,000), γ 1.364.
- **Structural criteria** `[SP-8110 §3.5-3.6]`:
  - design speed 1.10× max
  - burst ≥ 120 %, yield ≥ 105 %
  - blades ±15 % off resonance; rotor ±20 % off criticals
- **H-1 turbine η disagreement.** [SP-8110] gives 62.5 % T-S. [SP-8107 Table III] gives
  70.2 % and [H1-Man Fig 1-47] 69.6 % for the same Mark 3 turbine. Unresolved; see
  OPEN_QUESTIONS.

## Efficiency bookkeeping and loss correlations (`[SP-290]`, general turbine text)

`[SP-290]` is NASA Lewis's general turbine textbook (gas-turbine oriented, no rocket fleet data).
These are its relations that bear on the tool's turbine efficiency model.

**Total-to-static vs total-to-total.** They differ only by the last stage's leaving loss:
1/η_TS − 1/η_TT = (V_ex²/2)/Δh′ `[SP-290 Ch.3 eq. 3-13/3-14 p.75; Ch.2 p.39]`.
- A real 2-stage turbine with low exit velocity showed a 1-2 point gap `[Ch.12 p.382]`.
- Idealized 2-stage curves at the H-1's loading (λ̄ 0.42-0.56) give η_TT/η_TS ≈ 1.10-1.11
  `[Fig. 3-7]`.
- That makes the H-1 62.5 % vs 70.2 % disagreement above *consistent with* a T-S vs T-T split.
  It needs a leaving loss of ≈11 % of the isentropic work (V_ex ≈ 360 m/s ≈ 0.9 U, derived).
  That is high for a pressure-compounded stage, so a different rating point is still possible.

**Velocity ratio vs loading.** ν = √(λη/2), with stage loading λ = Δh′/U² `[eq. 2-74 p.48]`.
- SP-290 uses the mean blade speed. `[SP-8110]` uses √ΣU² for multistage turbines, so SP-8110
  U/C0 = √n · ν (derived).
- Single-row impulse ideal: η = 4ν·sin α − 4ν², peaking at ν = sin α/2 ≈ 0.47. That is the shape
  of SP-8110 Fig. 13's 1-row curve.
- Stage count n = λ_stage/λ̄ `[eq. 2-111]`.

**Staging gains** `[Fig. 3-7 p.80; p.81]`:
- At λ̄ 0.5, two stages beat one by +2 points total-to-total and +9 total-to-static.
- At λ̄ 0.15 the gains are +5 / +24.
- The optimum 2-stage turbine at low λ̄ becomes **velocity-compounded with a 75:25 work split at
  λ̄ = 0.125**. The F-1 (λ ≈ 0.13) and J-2 fuel turbine (≈0.11) sit at that optimum (derived),
  which independently supports the SP-8110 rule above.

**Tip clearance, unshrouded blades** `[Fig. 8-3 p.228]`: Δη = k·(clearance/passage height),
with k ≈ 1.6 for impulse rising to 3.0 at reaction 0.7. Reaction blading lost about twice as
much as impulse in tests `[Fig. 8-2]`.

**Partial admission** `[Ch.8 eq. 8-23, 8-24, 8-31; Fig. 8-12]`:
- Sector loss: η_pa = η·(1 + K_w·K_s)/(1 + K_w), with K_s = 1 − p/(3f).
- Pumping (windage) loss on the inactive arc: P_p = K_p·ρ·U³·l^1.5·D·(1 − ε).
  - K_p = 3.63 m^−½ for an unenclosed rotor.
  - ¼-½ of that when the inactive arc is enclosed.
  - 5.92 from one test.
- The optimum ν falls as the admitted arc shrinks: ≈0.47 at full admission to ≈0.26 at
  arc/pitch = 1.

**Reynolds number** `[eq. 2-142 p.62]`: (1 − η₁)/(1 − η₂) = A + B·(Re₂/Re₁)^0.2, with A 0.3-0.4
and B 0.7-0.6.

**Disk friction (Daily & Nece 1960)** `[Ch.8 eq. 8-7, 8-16 p.232-236]`:
- Four regimes (laminar/turbulent × merged/separate boundary layers).
- Turbulent, separate boundary layers (regime IV): C_M = 0.102·(s/a)^0.1 / R^0.2, with
  windage power P = C_M·ρ·ω³·a⁵/2.
- Smaller diameter at higher speed lowers disk friction.

**Small high-pressure-ratio partial-admission turbine** `[SP-290 Ch.9 Fig. 9-20 p.274-275]`.
This is the regime of small rocket GG/APU turbines:
- design ν ≈0.216;
- peak η_TS ≈0.38-0.39 at ν ≈0.22 and PR 63;
- at 90 % speed, dropping PR from 63 to 20 takes η from 0.375 to 0.275.
That matches the fleet's small-turbine values: Agena 41 %, A-7 37 %.

**Real 2-stage turbine vs the ideal parabola** `[Fig. 12-21 p.381]`: peak η_TS 0.82-0.83 at
ν 0.45-0.50. It follows 2x − x² (x = ν/ν_opt) within ≈0.01-0.05. That is a usable normalized
shape for an η(U/C0) curve.

**Static efficiency vs loading, n stages** `[Fig. 3-9 p.84]`: at λ̄ 0.125, η_TS = 0.44 / 0.69 /
0.77 / 0.82 for n = 1-4. Compare stage counts within this figure only, because its n = 1 level
differs from Fig. 3-4's single-stage curve.

**Not in SP-290:** a Balje-type Ns-Ds chart for axial impulse turbines. Its only η-vs-specific-
speed chart is for radial-inflow turbines `[Fig. 10-7]`.

## Implications for engine_designer

- **Turbine η curve (ASSUMPTIONS.md ~154-155):**
  - `turbopump_efficiency.py` uses staging ceilings (0.63 / 0.76 / 0.80) × fitted pitchline and
    admission factors.
  - `[SP-290]` gives the physical *shape*: η vs ν, staging gains vs λ̄, and the sector +
    pumping partial-admission loss. The magnitude must still be fitted to the `[SP-8110]` fleet.
  - The partial-admission pair (sector + pumping) is a candidate physical replacement for the
    fitted admission floor.
- **Basis of the 0.76 pressure-compounded ceiling.** The fleet table is all total-to-static.
  The H-1 70.2 % / 69.6 % values are probably total-to-total. Keep the ceiling on the T-S basis
  if it is re-fit (OPEN_QUESTIONS, H-1 item).
- **`TURBINE_DMEAN_OVER_PUMP_D` (1.9, Tier 3):** not answered by SP-290. It stays F-1-fitted.
- **`pump_meanline.DISK_CM_COEFF` (0.0622) — flagged.** With p = 0.0622·R^−0.2·ρ·ω³·r⁵ it reads
  about 1.5-1.8× higher than SP-290's regime-IV effective coefficient of 0.035-0.041 (s/a
  0.02-0.10, including the ½). 0.0622 appears to be the regime-III (merged-layer) numerator,
  which goes with R^−¼, not R^−0.2. **Confirmed 2026-10-18 on the page images:** tool/SP-290
  = 1.22·(s/a)^−0.1, i.e. 1.4-1.8× high for s/a 0.2-0.02, with the ½ dropped. Restoring the ½
  alone gives 0.72-0.97× of SP-290. **Adopted 2026-10-20 (lit-batch Round 3):** eq. 8-16 at
  s/a 0.05 (Tier 3 gap) plus the eq. 8-17-8-22 leakage-throughflow factor on the front shroud
  face; `K_HYD` refit 1.76 → 1.79. Regime IV alone failed the SP-8109 Fig. 6 grid (11 pts vs
  ±10); with throughflow it passes at 9.4.
- **RL10 turbine point** `[RL10-ROCETS]`: measured pump and jacket-exit pressures bound the
  RL10A-3-3A turbine PR at ≤1.50-1.58 (derived). That is consistent with `[SP-8110]`'s PR 1.42 at
  74 % T-S. The ROCETS report gives no turbine flow, bypass fraction or efficiency, so
  `ETA_EXPANDER_TURBINE` 0.55 still has only SP-8110's 74 % against it, which suggests it is low.
