# 17 — Engine life, duty cycle and burn-time limits

## Scope

What limits how long, and how many times, a liquid engine can fire. It covers:
- thrust-chamber liner low-cycle fatigue and the ratcheting ("doghouse") failure;
- time-at-temperature (creep) damage;
- the life factors real programmes design to;
- duty requirements quoted by real programmes.

It supports a design-derived TestFlight `ratedBurnTime` / `testedBurnTime` and an ignition-count
cap (`engine_designer/plans` TestFlight round, 2026-10-16).

Related material lives elsewhere and is not repeated here:
- alloy selection and the copper-alloy property table: `12-materials-and-structures.md`;
- RP-1 coking / deposit rates: `06b-cooling-methods-and-chemistry.md`;
- turbine blade and disk limits: `09-turbopumps.md`;
- ablative char sizing: `12` / `[SP-8124]`.

## Key relations

**Duty requirements vs. ratings.** Real programmes specify life as **cycles AND accumulated
hours**, separately:

| Programme | Life requirement | Source |
|---|---|---|
| SSME main chamber | 55 thermal cycles (Pc 20.7 MPa, throat flux 131-147 MW/m²) | `[Quentmeyer-TMX73665 p.1]` |
| Orbit Transfer Vehicle chamber (study) | 200-300 thermal cycles | `[Quentmeyer-TMX73665 p.1]` |
| Future reusable high-Pc nozzle (NASA LeRC framing) | 300 major thermal cycles, 10 h total | `[CR134806-Props §1.0 p.2]` |
| Shuttle OME regen chamber (study ground rule) | 1000 cycles / 15 h, **SF 4 on both** | `[ASR72-238 Table 4, Fig. 6-7]` |

A single-mission (expendable) rating is a different thing from these accumulated-life numbers.
Rating vs. accumulated life is exactly the gap between RO's `ratedBurnTime` (one mission's
burn) and the hardware's total life.

**Life factors.**
- Turbine: **≥ 4 on cycles** for long life, or 1.4 on strain for LCF `[SP-8110 §2.4.1]`.
- OME regen chamber: SF 4 applied to both cycle life and creep life `[ASR72-238]`.
- Creep damage is summed as a time fraction: plotted as 4·(operating time)/(rupture time)
  against temperature at the peak hot-wall stress. This is Robinson's linear life-fraction
  rule with SF 4 `[ASR72-238 Fig. 6]`.

**Chamber-liner cycle life vs. hot-wall temperature (copper alloys, LOX/H2, 1.7 s hot holds)**
`[Quentmeyer-TMX73665 Figs. 15-17, 19]`, coefficients converted from °R to K:
- OFHC copper: T_gw = 2511 · N_f^-0.205 K, ΔT_max = 1828 · N_f^-0.178 K
- ½-hard Amzirc: T_gw = 3139 · N_f^-0.229 K, ΔT_max = 2528 · N_f^-0.226 K
- NARloy-Z and aged Amzirc fall **above** these lines: 556-688 cycles at points hotter than the
  OFHC line.

Inverted for OFHC: N_f = (2511 / T_gw)^(1/0.205). That gives about 2,000 cycles at 525 K, about
200 at 850 K and about 30 at 1,100 K. Life is steep in temperature: **+10 % wall temperature ≈
−37 % cycles**.

## Empirical data & typical values

**Cycles to failure, 22 milled-channel liners** at Pc 4.14 MPa and 54 MW/m²
`[Quentmeyer-TMX73665 Table I]`:

| Material | Cycles to failure |
|---|---|
| OFHC copper | 56-817, median ≈ 170; one unfailed at 2044 cycles, 514 K wall |
| ½-hard Amzirc | 106-944 |
| Aged Amzirc | 393 |
| NARloy-Z | 556-688 |

**Uniaxial isothermal LCF at 810 K** (strain range at 10³ cycles) `[CR134806-Props Figs. 10, 19,
27]`:
- Amzirc ½-hard ≈ 2.3 %
- NARloy-Z ≈ 2.0 %
- annealed OFHC ≈ 0.8 %

At a 2 % strain range: OFHC 130, NARloy-Z 930, Amzirc 1,400 cycles (Conway et al., quoted in
`[Quentmeyer-TMX73665 p.6]`).

**Real-chamber failure mechanism** `[Quentmeyer-TMX73665 p.4]`. In every liner the coolant-channel
hot wall thins at the channel centre and bulges inward ("doghouse"), then fails in **tensile
rupture**. It is a cyclic ratchet, not a crack started by pure LCF.
- Two feedbacks drive the late-life acceleration: the larger deformed channel lowers h_c, and
  the roughened wall raises h_g.
- Hannum et al. attribute it to creep rupture plus thermal ratcheting.
- Rocketdyne attributes it to "strain-induced creep".

**Coated liners, same rig** `[Quentmeyer-78-1034]`, with full data in `12c-thermal-barrier-coatings.md`:
- A 0.203 mm ZrO2 coat (eroded to a stable 0.061 mm) cut the metal hot-wall temperature from
  844 K to 489 K.
- Coated electroformed-Cu reached ≥659 cycles, vs 210 for uncoated OFHC. That is censored data:
  both coated articles failed for reasons unrelated to the coating.
- Inverting the OFHC line above at 489 K gives ≈2,900 cycles (derived). That is extrapolated
  past the fit range and on a different copper.
- **Peak strain occurs ≈0.3 s after ignition**, so the start transient sets the strain range,
  not the hold `[Quentmeyer-78-1034 p.6]`.
- Approximate isothermal strain ranges `[Fig. 25]`: OFHC ≈2.2 % at 10² and 0.45 % at 10⁴ cycles;
  electroformed Cu ≈1.4 % and 0.55 %.
- TBC conductivity also rises over hours at temperature from sintering `[Zhu-TBC Eq. 1]`. That
  is a slow, accumulated-life effect, not a per-burn one.

**Accumulated duty on one real engine** `[Vilja-J2S Table 1]`: J-2S engine J113 ran
11,508.8 s mainstage in 99 tests. Across the program: 273 tests, 30,858 s, plus tank-head idle
(6,713 s) and powered idle (252 s) run separately.

**J-2S life rating vs demonstration** `[J2S-Restart leaves 19, 24, 191]`:
- Model-spec life: 30 starts / 3,750 s.
- Endurance demonstration: 3,807.4 s, including 1,503.9 s at high MR.
- Mission-duty tests: 470 s each.
- Life extension demonstrated to 12,000 s and 30 starts. That backs RO's J-2S
  `testedBurnTime` of 12,000 s; the rated life is about ⅓ of the demonstrated.

**J-2 service life** `[J2-Man §2.5.7 p.2-41]`: 3,750 s mainstage, about 7.5× a ~500 s flight
duty. That is the same 3,750 s as the J-2S model spec above. The 1968 J-2S spec states it as
3,750 s mainstage + 3,500 s idle, 30 starts `[J2S-Boeing69]`.

**Staged-combustion preburner life targets** `[CR135356-Preburner p.7, p.34, Table 9 p.36]`
(1978 LOX/LH2 Advanced Space Engine):
- 60 cycles / 2 h service-free; 300 cycles / 10 h between overhauls.
- SF 4.0 on life, 1.1 on yield, 1.4 on ultimate; creep ≤1 %.
- Damage summed as 4φ_f + φ_c. That is the same SF-4 life-fraction rule as `[ASR72-238]`.

**One real applied LCF prediction** `[Miller-CuFatigue]`: predicted 80 cycles, actual through-crack
at cycle 39 (OFHC, Manson Universal Slopes). Life analyses are typically within about 2×.

**Creep in Ni/Fe liners** `[ASR72-238 Fig. 6]`. At 15 h with SF 4, Haynes 188 (47 ksi), Inconel
625 (50 ksi) and CRES (34 ksi) all stay below the rupture-damage limit up to about 1300 °F, so
there is "no significant creep damage" in that design. The cycle life at the throat is
≈1.3×10⁴ cycles, about 13× the requirement before SF.

**Bearings and seals** (time-limited rotating parts, already distilled):
- J-2 fuel-pump bearings at 1.6×10⁶ DN, with extended-life requirements, had cage problems
  `[SP-8048]`.
- Seal types are rated against per-fluid **3-hour** wear-life curves, and floating-ring seals
  are recommended for lives over 4 h `[SP-8121 §2.2]`.

## Caveats

- `[Quentmeyer-TMX73665]` is about **2 s** cycles at one heat flux. Its correlations give
  cycles, **not** a time-at-temperature life, and nothing here yet gives copper-liner creep or
  hold-time data. So *burn duration* is still unanchored for copper liners (`OPEN_QUESTIONS.md`).
- Its wall temperatures are model-projected, the fits run through about 6-9 points, and the
  material ranking reverses between the temperature basis (this chamber) and the strain basis
  (uniaxial). Don't port a uniaxial ranking onto chamber life without saying so.
- `[CR134806-Props]` values are **typical**, not design minimums.
- The OME creep result is for Ni/Fe alloys at 15 h. It does not transfer to copper, which creeps
  at a much lower homologous temperature.

## Implications for engine_designer

Report-only. No code was changed by this distillation.

- **`mass_model.low_cycle_fatigue_cycles` / `cooling_stage.throat_fatigue_cycles`** (generic
  Coffin-Manson coefficients, Tier 3) now have a **real-chamber anchor**. A validate row could
  check that the tool's throat fatigue estimate for an OFHC- or Amzirc-class liner falls within
  about 3× of the T_gw–N_f line at the solved hot-wall temperature. An alternative is to use
  that correlation directly for copper liners. Its exponent (−0.205) is the most trustworthy
  part.
- **Ignition cap for the TestFlight round:** `ignitions ≤ N_f / 4` (`[SP-8110]` /
  `[ASR72-238]` SF 4) is a cited rule that turns the throat fatigue life into an
  `ignitions` limit.
- **Rated burn time:** a time-at-temperature limit (creep) can use Robinson's 4·t/t_r form
  `[ASR72-238]`. For Ni/Fe liners the cited result is "not limiting at 15 h". Copper liners still
  need rupture data (Jerome & Armstrong 1973 NARloy-Z creep memo; Conway et al. hold-time
  report, Mar-Test MTI-R003-2-3).
- **`materials.py` `narloy_z`** differs from the cited typical room-temperature values
  `[CR134806-Props §2.2]`:

  | Property | `materials.py` | CR-134806 |
  |---|---|---|
  | k (W/m·K) | 325 | 295 |
  | E (GPa) | 115 | 127 |
  | ρ (kg/m³) | 9000 | 9134 |
  | CTE (10⁻⁶/K) | 18.5 | 17.2 |

  This is a citation-upgrade candidate (`OPEN_QUESTIONS.md`). The tool's k may be intended as a
  hot-wall value; check before changing.
- An **Amzirc / OFHC liner** entry would now have cited properties if the material catalog
  ever adds them.
