# 12c — Thermal-barrier coatings (ZrO2) on chamber liners and nozzle extensions

## Scope

Sprayed zirconia thermal-barrier coatings (TBCs) on hot-gas walls. Covered here:
- their conductivity and how it drifts with time at temperature;
- the heat-flux and wall-temperature cuts they buy on a regen copper liner;
- erosion and spall behaviour;
- their effect on liner cycle life.

This file was split out of `12-materials-and-structures.md` on 2026-10-18, when the 2026-10-18 batch
(`[Zhu-TBC]`, `[Quentmeyer-78-1034]`) would have pushed that file further past the 40 KB cap.
Related material lives elsewhere:
- copper-liner fatigue and the doghouse failure: `17-engine-life-and-duty.md`;
- alloy selection: `12`;
- radiation-cooled silicide/aluminide coating limits: `12` / `[SP-8124]`.

engine_designer uses a TBC in one place: the radiative nozzle-extension liner
(`materials.LINER_MATERIALS["zirconia"]`, `cooling/radiation.py`, ASSUMPTIONS.md row "LinerMaterial").

## Key relations

**Coat as a series conduction resistance.** R = t / k. The cut a coat buys depends on the
boundary behind it:
- **Regen copper wall:** the coolant side holds the metal cold. Adding R lowers the flux nearly in
  proportion, so a thin coat gives a large cut. Measured: 0.203 mm gave −80 % flux and 0.061 mm
  gave −40 % `[Quentmeyer-78-1034 Table II p.8]`.
- **Radiation-cooled shell:** it can only reject εσT⁴. The same R moves the shell temperature
  much less (the tool's own check gives ~7 % at 0.076 mm). The two contexts are not
  interchangeable; see Implications.

**Conductivity drifts up with time at temperature (sintering)** `[Zhu-TBC Eq. 1 p.7]`:

(k − k⁰)/(k^∞ − k⁰) = 102.2·exp(−68228/RT)·[1 − exp(−t/τ)], with τ = 572.5·exp(41710/RT).

- The paper prints no units. R = 8.314 J/mol·K with τ in seconds reproduces its Fig. 4
  (τ ≈ 3.7 h at 1320 °C). That reading is ours, not the paper's.
- The fit is for plasma-sprayed ZrO2-8wt%Y2O3 and is not valid above ~1500 °C.
- **Sintering is a multi-hour effect.** A 500 s burn at 1500 K moves k only ~3 % of the way to
  its plateau (derived). It matters for accumulated engine life, not for a single burn.

## Empirical correlations & typical values

**Conductivity of ZrO2-(7-8)wt%Y2O3** `[Zhu-TBC]`

| Condition | k, W/m·K | Cite |
|---|---|---|
| Fully dense | ≈2.5 | `[Zhu-TBC p.5]` |
| Plasma-sprayed, as-sprayed | ≈1.0 | `[Zhu-TBC p.5]` |
| Sintered plateau, 254 µm coat, 0.64 MW/m², surface 990 / 1100 / 1320 °C | ≈1.08 / 1.18 / 1.44 | `[Zhu-TBC Fig. 4 p.8]` |
| Through-thickness average (same three tests) | 1.170 / 1.215 / 1.277 | `[Zhu-TBC Fig. 5b p.9]` |
| Implied k^∞ from Eq. 1 (derived) | ≈1.74 | — |
| Effective coat + Nichrome, back-solved from a LOX/GH2 firing (derived; the SINDA input is unstated): 0.203 mm / 0.061 mm | ≈0.88 / ≈1.49 | `[Quentmeyer-78-1034 Table II p.8]` |

**Elastic modulus:** 34-64 GPa as-sprayed, rising from 70 to ≈125 GPa after ≈20 h of sintering
`[Zhu-TBC p.10-11]`. A stiffer sintered coat carries more thermal-mismatch stress.

**Regen copper liner, LOX/GH2 rig throat, steady state** `[Quentmeyer-78-1034 Table II p.8]`.
The liner is electroformed Cu with a ~0.013 mm Nichrome bond layer.

| Coat | Coat surface T | Metal hot-wall T | Through-wall ΔT | Heat flux |
|---|---|---|---|---|
| none (OFHC) | — | 844 K | 556 K | 57.2 MW/m² |
| 0.203 mm as-sprayed | 2922 K, near ZrO2 melting | 157 K | 90 K | 12 MW/m² (−79 %) |
| 0.061 mm, stable after erosion | 1878 K | 489 K | 322 K | 34 MW/m² (−41 %) |

**Erosion and adhesion** `[Quentmeyer-78-1034 pp.3-4, Fig. 15 p.13]`
- The 0.203 mm coat eroded non-uniformly where its surface ran near melting.
- It settled at a stable, uniform **0.061 mm within ≈80 cycles**, and stayed well bonded with no
  spalling to bare copper.
- The one bare spot was a burnout caused by a wax-blocked coolant passage. A TBC does not protect
  a wall whose coolant side has failed `[p.4]`.

**Life**
- **1978, 0.203 mm coat** `[Quentmeyer-78-1034]`:
  - Coated electroformed-Cu liners reached ≥659 and 80 cycles, both failures unrelated to the
    coating. Uncoated OFHC reached 210 cycles, the re-quoted `[Quentmeyer-TMX73665]` S/N 34.
  - Classical LCF predicted 300 / 1900 / >10,000 cycles and over-predicted the uncoated case 1.4×
    `[Table I p.8, p.6]`.
  - The coat suppressed the doghouse thinning: peak strain fell to ½ and 1/12 `[Figs. 16-17 p.13]`.
  - Peak strain occurs ~0.3 s after ignition, so the start transient governs, not the hold `[p.6]`.
- **1988, 0.076 mm coat** `[Quentmeyer-CR185257 §Thermal Barrier Coatings p.3]`, as quoted from
  NASA TM-100933, which we don't hold:
  - 1450 cycles with no damage, vs 393 for uncoated Amzirc (`[Quentmeyer-TMX73665]` S/N 56); flux
    cut ~50 %.
  - The substrate also differs, so this is not a clean single-variable A/B.
  - **This is a separate program from the 1978 paper.** Cite the two separately, never as one
    result confirmed twice.
- **Crack growth** `[Zhu-TBC p.12-13]`: longer heating cycles and higher temperatures speed it up,
  and spallation is driven by bond-coat oxidation. These are gas-turbine/diesel results with no
  rocket cycle count.

**Applied thicknesses on record:**
- 0.061 mm, stable after erosion `[Quentmeyer-78-1034]`;
- 0.076 mm `[Quentmeyer-CR185257]`;
- 0.203 mm as-sprayed `[Quentmeyer-78-1034]`;
- 0.254 mm in the Zhu tests `[Zhu-TBC]`;
- ~0.25 mm flame-sprayed `[TN-D3836 p.22-25]`;
- up to 1.56 mm modelled for diesel service `[Zhu-TBC Figs. 6-7]` (context only, not rocket).

## Caveats

- Zhu & Miller is gas-turbine/diesel data at surface temperatures ≤1320 °C over tens of hours.
  A rocket throat coat surface runs much hotter (2922 K computed above), so Eq. 1 cannot be
  extrapolated there.
- Quentmeyer 1978 has two coated articles and no coating-caused failure. Its life numbers are
  censored or predicted.
- Neither source gives density/porosity, CTE or **emittance**, which a radiative liner face needs.
- Both effective-k back-solves above are our arithmetic on a model output.

## Implications for engine_designer

- **`LINER_MATERIALS["zirconia"].thermal_conductivity_w_mk` = 2.0 is high for a sprayed coat.**
  - Every cited sprayed value is 0.9-1.5 W/m·K; 2.0 sits between those and fully dense (2.5).
  - So the computed liner thickness is conservative by ~1.4-2×: the buildable C-103 case's 0.15 mm
    would be ~0.075-0.11 mm at k 1.0-1.45.
  - Candidate re-cite: k ≈ 1.0 as-sprayed `[Zhu-TBC p.5]`, or ≈1.2-1.4 sintered for a long-life
    engine.
  - **Adopted 2026-10-18 (lit-batch Round 2): k = 1.3 sintered** (Cory's choice). The C-103 coat
    is now 0.099 mm.
- **`validate.run_zirconia_liner_check` check (e)** compares against CR-185257's unqualified "~50 %".
  - `[Quentmeyer-78-1034 Table II]` is a better regen-boundary anchor: a documented −41 % at a
    stated 0.061 mm, and −79 % at 0.203 mm.
  - The check stays informational, because the regen vs radiative contexts differ (Key relations).
  - **Re-anchored 2026-10-18 (Round 2).** At k 1.3 the tool's radiative liner cuts 8.4 % / 22.7 %
    at 0.061 / 0.203 mm.
- **`max_practical_thickness_m` (1.0 mm, Tier 3):** the cited rocket coats are 0.06-0.25 mm. A
  0.2 mm coat at a throat-like flux eroded back to 0.06 mm. 1 mm stays an uncited upper bound for a
  cooler nozzle-extension location.
- **`max_service_temp_k` (1500 K, Tier 3):** sprayed coats ran 1263-1593 K surface for 30+ h
  without reported failure `[Zhu-TBC]`. That makes 1500 K plausible-to-conservative for a
  long-life coat. A short-burn surface near 2900 K erodes rather than fails outright
  `[Quentmeyer-78-1034]`.
- **A regen-chamber TBC is still an unmodeled life lever.** It cuts metal temperature and strain,
  and the start transient dominates strain. Candidate data for a future liner-coating option on
  regen chambers is in the tables above.
