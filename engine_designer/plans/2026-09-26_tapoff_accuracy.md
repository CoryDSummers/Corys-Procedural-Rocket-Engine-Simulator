# Plan: Tap-off cycle accuracy: STBE hot-gas-mixer re-anchor, tap temperature input, fairer turbine-material check

## Context
Cory asked how accurate the tool's tap-off cycle is. His RS-29 (LOX/RP-1 tap-off, 1.6 MN) is told
it needs a powder-metallurgy turbopump material.

He was explicit that **he does not want the tool to switch anything to Inconel automatically.**
The concern is accuracy. Nothing in this plan changes a design's chosen material. The material
work only makes the warning judge whatever the user picked correctly.

### What's wrong today
- **Temperature and composition.**
  - `design/feed_stage.py:221` drives the turbine with chamber-MR combustion products "film-cooled" to `min(Tc × 0.55, 1150 K)`.
  - Both constants are Tier 3. The "J-2S ~1,140 K" in ASSUMPTIONS has no source anywhere in claude_lit.
  - There's no user input.
- **A real tap-off design in hand says otherwise.** P&W STBE study, `[STBE-PW leaf 338 = p.317 §4.3.1.1; Table 4.3.1-2]`, LOX/CH4, 750 klbf SL, Pc 2,400 psia, MR 3.5:
  - "The tap-off provides **1.9 percent** of the O/F biased chamber flow to the mixer inlet where **cold methane mixes with the hot gases** to provide **2293 psia, 1800 R** gas."
  - 12.5 % of the methane goes via the fuel bypass valve to that hot-gas mixer.
  - Methane turbine, then oxygen turbine, in series. Exhaust through a 5:1 nozzle.
  - Total tap-off flow is 132 lbm/s, 5.4 % of the 2,462 lbm/s injector flow.
  - My rough energy balance (1.9 % hot gas at Tc plus 12.5 % of the fuel as cold methane) closes near 1,000 K, and the mixed flow is ≈ the 132 lbm/s.
- **So, against the tool:**
  - The real turbine gas is **1,000 K**, not 1,150 K.
  - It's **fuel-rich** (mixed MR ≈ 0.5, GG-like), not oxidizing chamber-MR gas.
  - About 60 % of the turbine flow is **pumped bypass fuel**.
  - Turbine inlet is **0.955 × Pc**, not the GG-borrowed 0.855 (`turbine_exhaust.TAP_OFF_TURBINE_INLET_PC_FRACTION`).
- **The claude_lit source note is wrong too.** It says "tapped near the throat" and misses the mixer and the 1,800 R. It gets fixed.
- **Material verdict too strict.**
  - The real F-1 turbine ran at 1,550 °F ≈ 1,116 K on Inconel 718 / Rene 41 disks with cast 713C blades `[SP-8110 p.3, Table II]`, with no powder metallurgy.
  - The tool's single-material rule warns Inconel 718 above ≈1,058 K.
  - The PM entry is also mislabelled "MAR-M / Rene PM"; MAR-M-246/247 are cast alloys.

### Sources
- **The hydrocarbon re-anchor needs no new source.** STBE (in `literature/`, re-read p.317 and 320–323 this session) plus SP-8110/SP-8107 cover it.
- **Wanted, not blocking: a J-2S tap-off gas temperature / pressure / tap-port source**, e.g. Rocketdyne's J-2S development or final report. Until then LOX/LH2 tap-off stays on today's model, flagged.

## Design

### 1. Hot-gas-mixer tap-off model (`tap_off_model`: "auto" | "mixer" | "legacy")
"auto" means mixer for the hydrocarbon pairs (LOX/CH4, LOX/RP-1) and legacy for everything else
(LH2 until a J-2S source; storables have no tap-off precedent). "legacy" = today, bit-identical.

**Mixer model**, in a new pure helper, e.g. `physics/tap_off.py` with an `__main__` self-test in `verify_all.sh`:
- **Target turbine inlet temperature.**
  - `EngineDesign.tap_off_tin_k` (0 = pair default: `TAP_OFF_MIXER_TIN_K` = 1,000 K for hydrocarbons `[STBE p.317]`).
  - User range 600 K up to the hot-tap temperature.
- **Hot tap.** Chamber products at an effective temperature `TAP_HOT_T_FRACTION × Tc`.
  - That fraction is back-solved once so STBE's split closes: 1.9 % hot, 12.5 % of fuel, → 1,800 R. It covers the "O/F-biased" tap zone.
  - Reverse-solved on a real design point (convention #1), Tier 2–3, reported.
- **Energy balance** fixes the dilution-fuel mass per kg of hot gas:
  - m_hot · cp_hot · (T_hot − T_mix) = m_f · [cp_l (T_sat − T_pump_out) + h_fg + cp_v (T_mix − T_sat)]
  - h_fg, T_sat, cp_l come from the baked `saturation_properties.json` / coolant tables (CH4, RP-1 n-dodecane surrogate).
  - T_pump_out is Round 2's `pump_heating`.
  - cp_v is Tier 3 per fuel.
- **Drive-gas properties** of the mix (mixed MR ≈ 0.3–0.6, GG-like): `GG_GAS_PROPERTIES[pair]` cp/gamma, re-evaluated at the mixer Tin.
  - Stated as an approximation: it's the equilibrium fuel-rich GG gas, whereas the real mix is products plus unreacted fuel.
- **Mass flows.**
  - Turbine flow = hot + dilution, solved by the existing power balance and thrust closure.
  - The hot share leaves the chamber upstream of the throat.
  - The dilution share is pumped by the fuel pump (bypass) and adds to fuel pump flow/power, like `GG_MIXTURE_RATIO` flow today.
  - C1 audits `cycles.gas_generator_result` / thrust closure to make sure neither share is double-counted or missed.
- **Turbine inlet pressure** `TAP_OFF_TURBINE_INLET_PC_FRACTION` → 0.955 `[STBE p.317: 2293/2400]` on the mixer path. Legacy keeps 0.855.
- **Result keys** `cycle_result["tap_off"]`: `hot_fraction`, `dilution_fraction_of_fuel`, `t_hot_k`, `t_mix_k`, `tin_source`, `model`.
- **Warn-only rows:**
  - The tap-off split vs STBE: hot 1.9 %, dilution 12.5 %, total ≈5.4 %.
  - Kerosene dilution: no RP-1 tap-off has flown; coking/soot in the mixer, as with a fuel-rich GG (the STBE was methane).
  - The Tin used, and whether it's default or user-set.

### 2. Fairer turbine-material verdict (never changes the user's choice)
- **Rotor material.** `turbopump_material_key` = rotor / disk / housing / impeller. Tip-speed caps, mass and rendering are unchanged.
- **New optional field** `turbine_blade_material_key` ("" = same as turbopump material, today's rule, bit-identical).
- **New `BLADE_MATERIALS` catalog.**
  - Entries: Inconel 718, Udimet 700, IN100 (cast), Alloy 713C (cast; F-1 blades), with the SP-8110 Fig. 30 AaN² rows stored for Round 3.
  - Each blade limit = the temperature where its Fig. 30 allowable falls to the fraction the F-1's 713C blades ran at (derived, one real anchor).
  - MAR-M-246 DS (SSME HPFTP) goes in as Tier 3, flagged.
- **Rotor catalog changes.**
  - Add `rene_41` (the F-1 disk alloy; Tier 3 limits).
  - Relabel PM "Powder-Metallurgy / HIP superalloy (high-strength disks & housings)"; the key is unchanged.
- **Rule when a blade alloy is set.**
  - Blade: gas Tin > 1.08 × blade limit warns.
  - Disk: gas Tin × `DISK_METAL_TEMP_FRACTION` (≈0.878, so the F-1's IN718 disks at 1,116 K just pass; Tier 3) > rotor limit warns.
  - The staged-preburner row (`feed_stage.py:312`) uses the same helper.
- **Warning text** names "lower the turbine gas temperature" alongside "a hotter-capable alloy". It never auto-selects one.

### 3. Schema, validation, docs
- **`SCHEMA_VERSION` 18:** `tap_off_model`, `tap_off_tin_k`, `turbine_blade_material_key`. No key migration.
  - A deliberate physics change for **hydrocarbon tap-off only**, since "auto" = mixer, like Round 1's suction default. `tap_off_model "legacy"` restores it.
- **New corpus engine** "STBE Tap-Off" (LOX/CH4, 750 klbf SL, 2,400 psia, MR 3.5, eps 35, 5:1 exhaust nozzle), cited in `build_corpus.py`.
- **New banner "ALL TAP-OFF CHECKS OK"** (32nd) in `validate/turbomachinery.py`:
  - (a) STBE: hot fraction, dilution share and mix Tin against the anchor (the hot-T fraction was solved on it, so this is a consistency check). Total turbine flow ≈5.4 % of injector flow, within ±25 % (the independent part); turbine inlet 0.955 × Pc.
  - (b) `tap_off_model "legacy"` is bit-identical to today (RS-29, J-2X row).
  - (c) `tap_off_tin_k` lower → more dilution / turbine flow, lower engine Isp (monotone).
  - (d) The J-2X LOX/LH2 tap-off row is unchanged ("auto" = legacy for LH2).
  - (e) F-1 hardware (1,116 K, IN718 disk + 713C blades): no temperature warning. IN718 blades: warns. "" blade: identical to today's rule.
- **Corpus.** RS-29 (hydrocarbon tap-off) changes by design:
  - `--report --diff` → `validation_engines/reports/`, then `--snapshot`.
  - Report RS-29's before/after: Tin, turbine flow, Isp, warnings.
- **Docs:**
  - ASSUMPTIONS: mixer model and constants with tiers; blade catalog derivation; `DISK_METAL_TEMP_FRACTION`; remove the untraced "J-2S ~1,140 K" claim or mark it unsourced.
  - `claude_lit/sources/pw-stbe-configuration-study.md` + `topics/08`: fix "near the throat", add the mixer, 1,800 R, 2,293 psia and 12.5 % bypass.
  - OPEN_QUESTIONS: J-2S tap-off source wanted; kerosene tap-off; blade alloy data.
  - CLAUDE.md: banner count 32, layout line.
  - README.

### 4. GUI (`gui/app.py`, syntax-check only here; Cory click-tests)
- A **"Tap-off model"** dropdown (auto / mixer / legacy).
- A **"Tap-off turbine gas temp [K] (0 = default)"** slider, next to the preburner sliders (l.1133).
- A **"Turbine blade material"** dropdown, first entry "Same as turbopump material", under "Turbopump material" (l.1059).
- **Turbopump details lines:** hot tap %, dilution %, mix Tin, and the blade/disk limits.

## Commits (each gated on `./verify_all.sh`)
- **C0:** branch `turbopump/tapoff-accuracy` off `origin/main` (PR #21 merged), `plans/2026-09-26_tapoff_accuracy.md`, draft PR to main.
- **C1:** `physics/tap_off.py` (pure + self-test) and constants.
- **C2:** wire it into `feed_stage` + the flow accounting, schema 18, the STBE corpus engine, the banner, and the corpus report/snapshot.
- **C3:** turbine-material split (catalog, suitability, plumbing through `turbomachinery_stage` / `turbopump_sizing.size_hardware`), with validate rows.
- **C4:** GUI.
- **C5:** docs + claude_lit fix + memory (roadmap: #21 merged, this round).

## Critical files
- New: `engine_designer/physics/tap_off.py`
- Modified:
  - `physics/design/feed_stage.py` (l.217–245 tap-off branch, l.312)
  - `physics/design/constants.py`
  - `physics/turbine_exhaust.py:79–83`
  - `physics/cycles.py` (`gas_generator_result` flow accounting)
  - `physics/turbopump_materials.py`
  - `physics/turbopump_sizing.py` (l.873, 1034)
  - `physics/design/turbomachinery_stage.py:55`
  - `physics/design/engine.py`
  - `physics/validate/turbomachinery.py`, `validate/__init__.py`
  - `validation_engines/build_corpus.py`
  - `gui/app.py`
  - `verify_all.sh`
- Reused:
  - `thermo_tables.saturation()` (h_fg, T_sat)
  - `suction_stage.pump_heating` (fuel temperature into the mixer)
  - `GG_GAS_PROPERTIES`
  - `_exhaust_back_pressure`, the thrust closure

## Verification
- `./verify_all.sh` all PASS; `validate | grep -c '^ALL'` = 32.
- The new `tap_off` self-test closes STBE's energy balance.
- The corpus diff is limited to hydrocarbon tap-off engines (RS-29 + the new STBE), reported in the PR.
- RS-29 recomputed on the mixer model at its **own** material (PM, unchanged), reporting Tin, turbine flow, Isp and the material rows. Plus a side-by-side of what IN718 + 713C would show, as information only.
- GUI: Cory runs it; no `$DISPLAY` here.

## Status checklist (per commit)
- [x] C0: branch `turbopump/tapoff-accuracy` off origin/main, this plan, draft PR
- [ ] C1: `physics/tap_off.py` mixer model (pure + self-test) + constants
- [ ] C2: wired into feed_stage + flow accounting, schema 18, STBE corpus engine, TAP-OFF banner, corpus report/snapshot
- [ ] C3: turbine blade/disk material split + validate rows
- [ ] C4: GUI (tap-off model, tap Tin slider, blade material, details lines)
- [ ] C5: docs + claude_lit STBE fix + memory
