# Acting on the 2026-10-18 literature batch — immediate fixes + stepped rounds

## Context
The 2026-10-18 batch (12 new `claude_lit` sources) logged a set of code implications in
`claude_lit/OPEN_QUESTIONS.md` ("2026-10-18 batch — citation upgrades / code flags"). Nothing was
changed in `engine_designer/`. This plan turns those findings into work:
- **one immediate round**: citations and stale docs, bit-identical, plus a few small cited value
  fixes with almost no golden impact;
- **a stepped sequence of physics rounds**, ordered by trust impact and golden blast radius, and
  slotted against the master roadmap (`docs/roadmap-2026-10`, unmerged, all items open).

Conventions for every round:
- its own branch off `origin/main`;
- plan copy in `engine_designer/plans/`, with a per-commit `## Checklist`;
- spot-check vs real engines, warn-don't-block;
- `./verify_all.sh` green;
- for any physics change, save `run_corpus.py --report --diff` to
  `validation_engines/reports/YYYY-MM-DD_<topic>.txt`, then `--snapshot`;
- draft PR, not merged until Cory tests.

**Execution note:** Cory will run this plan in a separate conversation. That session should copy
this file to `engine_designer/plans/2026-10-18_lit_batch_followups.md` and then take one round at
a time, each through its own plan-mode pass. The code locations below were mapped on 2026-10-18;
re-grep before editing.

## Step 0 — land the literature batch (prerequisite)
- Branch `lit/2026-10-18-batch` off `origin/main`. Commit:
  - `claude_lit/` (12 notes, topics, README / PROVENANCE / OPEN_QUESTIONS);
  - the renamed `literature/` PDFs and the duplicate move;
  - the CLAUDE.md topic count.
- Leave out unrelated working-tree files: `RS-29_Config.cfg`, `Bell Model 8760*`, `design.json`.
- Draft PR. The physics rounds below cite its tags, so they branch after it merges, or stack on it.

## Round 1 — IMMEDIATE: citations + stale docs (bit-identical, no golden change)
Comment, docstring and ASSUMPTIONS.md edits only. `run_corpus --check` must stay bit-identical.
- `staged_combustion.py:47-55`: LOX/LH2 preburner `tin_k` 1113 K. Add a cite to the
  `[CR135356-Preburner Fig. 111]` Tin-vs-MR curve (1113 K ≈ MR 0.83-0.85). cp / γ stay Tier 3.
- `design/constants.py:65-72, 91`:
  - GG LOX/LH2 922 K: add `[J2-Man Fig 2-20]` (1,450 ± 50 °F mainstage redline).
  - Fix the stale LOX/RP-1 comment (it says 2100 / 1.13; the code has 2735 / 1.126).
- `design/constants.py:134-136` + `feed_stage.py` docstring (legacy tap-off): the "J-2S ~1,140 K
  unsourced" note becomes: real J-2S 922 K / 889 psia / 0.74 × Pc `[SP-8110 Table I]`, 900 K
  rated / ≈700 K throttled `[J2S-Restart]`; the legacy formula is contradicted (dilution scheme).
- `combustion.py:81-92` (Hydrazine): note that (1400 K, 11.0) is an Is-calibration pair, not a
  physical state (M = 96.13/(5+4X) → X ≈ 0.93) `[USAF-Hydrazine §2.3.4.1]`.
- `turbine_exhaust.py:124-141`: add the J-2 / J-2S exchanger envelopes `[J2-Man §2.1.9]`,
  `[J2S-Boeing69]` as second anchors (comment only; the F-1 values stay).
- `injectors.py` coax rows (0.10 / 0.50): add the J-2S tested-stable LOX ΔP/Pc 3 % at 6:1
  `[J2S-Restart]` as context. Values unchanged.
- `design/constants.py:47` `TANK_HEAD_PA`: cite `[X34-MPS]` (LOX 448 / RP-1 345→179 kPa) and
  `[J2S-Boeing69]` (207 / 269 kPa inlet).
- Stale docstrings:
  - `validate/cooling_layouts.py:99` says [0.2, 5] MPa; the code is 10.
  - `run_corpus.py` docstring (delta table → `reports/`).
  - `cooling/channels.py:126` "throat velocity" — it actually uses inlet density.
- ASSUMPTIONS.md rows for all of the above, plus `MAX_COOLANT_DELTA_T_K`'s storable caveat
  (saturation, `[USAF-Hydrazine]`).
- Then tick the matching OPEN_QUESTIONS "pending upgrade" bullets.

## Round 2 — IMMEDIATE: zirconia liner conductivity (warn-only path, no golden)
- **Zirconia liner** (`materials.py:617-649`). Cory's choice: the **sintered** value.
  - k 2.0 → **1.3 W/m·K**, the middle of the `[Zhu-TBC Fig. 4 p.8]` sintered plateau (1.08-1.44
    at 990-1320 °C) and the Fig. 5b through-thickness averages (1.17-1.28). Tier 2 with the cite;
    conservative for a fresh coat (≈1.0).
  - Max thickness 1.0 mm stays Tier 3, with the 0.061 mm stable / 0.203 mm cited.
  - Tmax 1500 K cited as plausible `[Zhu-TBC]`.
  - Validate `run_zirconia_liner_check`:
    - (e) re-anchors to `[Quentmeyer-78-1034 Table II]` (−41 % at 0.061 mm), still
      informational;
    - (c) re-verified (the C-103 coat thins by ≈2.0/1.3).
  - No golden uses a liner, so `--check` stays identical. ASSUMPTIONS.md row updated.
- Storable coolant transport moved to Round 4. Cory chose **temperature-dependent** properties,
  which belong in the new storable property module.

## Stepped physics rounds (after 0-2), in recommended order

**Round 3 — Pump disk-friction correction** (no roadmap item; prerequisite for Round 8).
- **Decided (Cory, 2026-10-18): switch to SP-290.**
  - `pump_meanline.py:79, :409-412` becomes `[SP-290 eq. 8-16]` (Daily-Nece regime IV):
    P = 0.102·(s/a)^0.1·Re^−0.2·ρω³r⁵/2, with a stated s/a (Tier 3; 0.02-0.05, pick one and say so).
  - Background: 0.0622 was a hand-picked Round 2 value. It is the regime-III numerator with the
    regime-IV exponent and the ½ dropped, so it reads 1.4-1.8× high. Its excess is partly
    absorbed by `K_HYD`; the total pump η is anchored, the loss split isn't.
  - Note in ASSUMPTIONS that real rough / leaky impellers may exceed the smooth-disk value
    (uncited).
- Refit `K_HYD` (currently 1.76) by scanning `fit_report(k_hyd=x)` for minimum rms over
  `CENTRIFUGAL_ANCHORS`. Commit a small `refit_k_hyd()` helper so the next refit isn't by hand.
- Re-check validate PUMP MEANLINE (a) ±0.08, (c) b2/D2, (d) Fig. 6 grid, (i) J-2 axial;
  TURBOPUMP-EFFICIENCY; FEED/PUMP CALIBRATION.
- Every pump-fed golden changes: report + snapshot.

**Round 4 — Storable (hydrazine-family) property module** (roadmap Phase 5 "Storables" / A10,
pulled forward).
- New `physics/storable_props.py` (pure functions, own self-test, added to verify_all), holding
  the `[USAF-Hydrazine]` temperature fits, all confirmed on the page images, for N2H4 / MMH /
  UDMH / A-50:
  - vapor pressure;
  - ρ(T), μ(T), k(T), cp(T);
  - critical constants.
  CoolProp lacks these fluids. The fits are coded with leaf cites, not hand-edited JSON.
- **Temperature-dependent coolant transport (Cory's choice).**
  - `cooling/coolant_state.py` `CoolantModel` (:37-53) and `cooling/coolant_props.py`
    `COOLANT_TRANSPORT` / `COOLANT_DENSITY_KG_M3` / `FUEL_CP_J_KGK` (:23-74) take storable
    properties from `storable_props` at the local coolant T, instead of the flat constants.
  - h = ∫cp dT replaces cp·T for those pairs.
  - Add the missing `Aerozine-50/NTO` coolant pair (today it falls to the generic fallback).
  - MON variants keep aliasing to N2O4/MMH.
  - The flat constants stay as the fallback for pairs with no fit (H2O2, Hydrazine monoprop).
- `suction_stage.py:26`: storables stop taking zero vapor pressure (NPSH available becomes real).
- New warn-only "jacket coolant boiling" row in `design/cooling_stage.py`: jacket-exit T vs
  T_sat(jacket P) plus a thermal-stability ceiling (N2H4 ~450 K, UDMH 666 K).
  `MAX_COOLANT_DELTA_T_K` storable entries become the min of the three. Warn only.
- Validate: a new "STORABLE PROPERTY" check against the handbook's own 298 K / NBP / summary-sheet
  values, plus a jacket-boiling plausibility row. Goldens change for Aestus (N2O4/MMH regen) and
  the N2O4/UDMH / LOX/UDMH user designs: report + snapshot.

**Round 5 — LH2 channels-mode jacket ΔP** (= roadmap 1.5).
- `cooling/march.py:131-137, 296-300`: feed the unused `rho_sizing_kg_m3` parameter (mass-flux /
  mean-density sizing) so LH2 passages aren't sized at the dense inlet.
- Target the real bounds: RL10A-3-3A ≤ 1.8-1.95 MPa `[RL10-ROCETS]`, J-2 ~1-2 MPa.
- Tighten `validate/cooling_layouts.py:162` (10 MPa) and the `cooling_flux.py:103` RL10 band
  (0.5-8). Make the RL10 band a gated corpus `reference` row.
- Goldens: J-2, RL10A-3-3, RS-25, Vulcain, LH2 user designs.

**Round 6 — Warm-GH2 injector-ring density** (no roadmap item).
- `design/manifold_stage.py:18-42, 159`: for regen LOX/LH2, size the fuel injector ring and the
  jacket-return bore with `thermo_tables.coolant_state("LOX/LH2", T_jacket_exit, P)`, not
  liquid 71 kg/m³.
- Also fix the `size_jacket_manifolds` ρ inconsistency (bore uses `rho_fuel`, velocity uses
  `_rho_in`).
- Spot-check vs the J-2 forward manifold (67-127 K, 5.4-6.4 MPa, `[J2-Man]`) and RL10
  (205-244 K, `[RL10-ROCETS]`). Run after Round 5, because it uses the march's exit state.
- Goldens: LH2 regen engines.

**Round 7 — LOX/LH2 tap-off mixer** (roadmap 0.4 / 1.9; lets the legacy model retire).
- `tap_off.py:81` `MIXER_PAIRS` += LOX/LH2, with LOX/LH2 defaults:
  - Tin 900 K rated `[J2S-Restart]`;
  - turbine inlet 0.74 × Pc `[SP-8110]`;
  - hot-tap fraction re-back-solved on the J-2S, flagged Tier 3 because the H2 split is
    unsourced.
- Validate `tap_off_checks.py` (d) changes from "J-2X auto → legacy, identical" to a J-2S spot
  check: Pc 1,200 psi, 265 klbf, Isp 436 s, turbine inlet ≈922 K. Add J-2S to the validation
  corpus.
- No existing golden uses a LOX/LH2 tap-off.

**Round 8 — Turbine efficiency from SP-290** (= roadmap 4.2 "turbine meanline", after Round 3).
- `turbopump_efficiency.py:40-64, 98-136`:
  - η(ν) normalized parabola 2x − x² `[SP-290 Fig. 12-21]`;
  - staging gains vs λ̄ `[Fig. 3-7/3-9]`;
  - partial admission as sector + pumping loss (eq. 8-23/8-24), replacing the fitted
    `ADMISSION_FLOOR`;
  - small-high-PR anchor `[Fig. 9-20]`;
  - total-to-static everywhere (H-1 anchor 70.2 → 62.5 % T-S, ceiling 0.76 refit).
- Validate TURBOPUMP-EFFICIENCY anchors keep ±0.08. All pump-fed goldens change.

**Deferred** (wait on literature or lower value; listed in OPEN_QUESTIONS):
- LOX/LH2 preburner Tin(MR) input;
- hydrazine monoprop table refresh (needs CEA / NAS 7-372);
- hydrolox acoustic screening row (TN-D4733 W ≥ 4.4, warn-only);
- J-2 manifold bores / jacket ε (needs the R-3825-1 Data Manual);
- burn-time Round B (creep literature).

## Verification (every round)
- `./verify_all.sh` all PASS. `python3 -m engine_designer.physics.validate | grep -c '^ALL'` =
  33, or 34 once Round 4 adds a banner (update the CLAUDE.md count).
- Round 1: `run_corpus.py --check` bit-identical. Round 2 onward: a `--report --diff` file in
  `validation_engines/reports/`, then `--snapshot`, with the deltas explained in the plan copy.
- GUI rows (Rounds 2/4/6) can only be syntax/import-checked here; Cory clicks through.

## Checklist
Each round is its own branch and draft PR, and gets its own plan-mode pass before it starts.
- [x] Step 0: literature batch committed on `lit/2026-10-18-batch` (draft PR)
- [x] Round 1: citations + stale docs on `lit/round1-citations`, stacked on Step 0. Bit-identical.
  Code locations re-grepped 2026-10-18 (they had moved since this plan was written):
  - `staged_combustion.py:48-53`;
  - `design/constants.py`: ~47 `TANK_HEAD_PA`, ~60-92 GG gas, ~120-130 legacy tap-off;
  - `design/feed_stage.py:458` docstring; `tap_off.py:79`;
  - `combustion.py:81-92`; `turbine_exhaust.py:124-141`;
  - `injectors.py`: `coaxial_swirl` ~79, `coax_post` ~188;
  - `validate/cooling_layouts.py:99` (vs :162); `cooling/channels.py:129`;
    `validation_engines/run_corpus.py:19-20`.

  Runtime checklist strings (e.g. `feed_stage.py:522`) are left alone so the change stays
  bit-identical.
- [x] Round 2: zirconia liner k 1.3 on `lit/round2-zirconia`, stacked on Round 1. No golden uses a
  liner, so `run_corpus --check` stays bit-identical (no report or snapshot needed). Before → after:
  - C-103 coat 0.152 → 0.099 mm;
  - Ti-6Al-4V requirement 877 → 570 mm (still capped at 1.0 mm);
  - check (e) re-anchored to `[Quentmeyer-78-1034 Table II]`: 8.4 % / 22.7 % at 0.061 / 0.203 mm
    (real regen 41 % / 79 %).
- [ ] Round 3: pump disk friction (SP-290) + `K_HYD` refit
- [ ] Round 4: storable property module + temperature-dependent coolant transport
- [ ] Round 5: LH2 channels-mode jacket ΔP
- [ ] Round 6: warm-GH2 injector-ring density
- [ ] Round 7: LOX/LH2 tap-off mixer
- [ ] Round 8: SP-290 turbine efficiency
