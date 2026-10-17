# New propellant pairs: LOX/UDMH, N2O4/UDMH, LOX/RP-1 (subcooled)

## Context
Cory wants more fuel/oxidizer combinations in `engine_designer`. This round adds three pairs:
- **LOX/UDMH**: RD-119, RD-112/113/114/115 and LR79 S-3FH in RO.
- **N2O4/UDMH**: RD-253 (Proton) and RD-0208/0210. Most Soviet storables in RO use this pair.
- **LOX/RP-1 (subcooled)**: a separate dropdown entry at fixed densified temperatures (Cory's choice, instead of a temperature input). It matches RO's Merlin 1D+ / NK-33 `CooledLqdOxygen`/`CooledRP-1` configs.

Today a "pair" is just a string key, copied into about 25 per-pair dicts across `physics/`, `export/` and `gui/`. Many of those dicts silently fall back to a default when the key is missing. Performance comes from baked Cantera tables (`physics/property_data/combustion_equilibrium.json`). Cantera and CoolProp are not installed here, but the network is up, so a pinned venv works.

Two facts shape the subcooled pair:
1. Reactant temperature is not an input to the tables. Each reactant has a single fixed assigned enthalpy (O2(L) at 90.17 K, RP-1 at 298.15 K).
2. Propellant density is a per-pair constant (`PROPELLANT_DENSITIES`).

So the subcooled pair becomes its own table entry, built from new cold reactants, with its own densities.

**Branch**: `propellants/new-pairs`, stacked on `export/rp1-identity`. That branch rewrote `cfg_writer` and re-fit `cost_model`, and both files gain new pair entries here. The draft PR is based on `export/rp1-identity` and merges bottom-up, the same pattern as turbopump Rounds 0-2. No `EngineDesign` field is added, so there is no schema bump. Plan copy: `engine_designer/plans/2026-10-15_new_propellant_pairs.md`, with a per-commit checklist.

## Design decisions
- **Pair keys**: `"LOX/UDMH"`, `"N2O4/UDMH"` (ox/fuel, like `N2O4/MMH`), `"LOX/RP-1 (subcooled)"`.
- **Variant mechanism**: one new map in `physics/combustion.py`, `PAIR_VARIANT_OF = {"LOX/RP-1 (subcooled)": "LOX/RP-1"}`, plus `base_pair(pair)`.
  - Dicts whose value is the same physics as the base pair get an explicit alias entry, set in one place per dict as `d[k] = d[base]`. These are ETA_CF, L*, L_MID_BASE, beta band, GG/preburner gas, Bartz class, deposit factor, cost class, ignition and tap-off mixer.
  - Values that really differ get their own entries: densities, coolant table, suction temperatures and RF resource names.
  - Hard-coded checks change from `pair == "LOX/RP-1"` (`design/feed_stage.py:500`) to `base_pair(pair) == ...`. The same applies to any other `"LOX/RP-1"` literal the implementation grep finds.
- **Subcooled temperatures**: LOX 66 K, RP-1 266 K. These are the published Falcon 9 FT densified values (-207 °C / -7 °C). There is no claude_lit cite yet, so they go into ASSUMPTIONS as a calibrated estimate and into OPEN_QUESTIONS.
- **Subcooled densities** are computed, not hand-picked. They come from the saturation table's `rho_l` at those temperatures (LOX from CoolProp oxygen, RP-1 from the n-dodecane surrogate).
- **UDMH and N2O4 thermophysical data**: CoolProp has neither fluid. Coolant density, cp, viscosity and k, and the max coolant ΔT, are hand-cited from `literature/` (Sutton propellant table / Huzel). A reference-lookup is done at implementation time, and every number is cited in ASSUMPTIONS. They then go through the existing non-table fallback path that Aerozine-50 already uses. None is invented.
- **Isp**: `ETA_CF` for each UDMH pair is reverse-solved on one anchor (`validate/performance.solve_eta_cf`). The subcooled pair inherits LOX/RP-1's `ETA_CF` and `eta_c*` and is NOT re-tuned. Its only physics differences are colder reactants and denser propellants, and the spot check reports whether that alone reproduces Merlin 1D+.

## Commits

**C1: Generator and tables** (`tools/property_tables/generate_property_tables.py`, `physics/property_data/*.json`)
- Venv in `$CLAUDE_JOB_DIR/tmp`, pinned to `cantera==3.2.0 CoolProp==8.0.0` (matching the JSON meta).
- New `--merge-pairs P1,P2…` mode. It computes only the listed pairs and splices them into the existing JSON, so existing pairs stay byte-identical (verified with a diff of the old keys). The Sutton self-check still gates the write.
- `REACTANTS`: add `O2(L,66K)` and `RP-1(266K)`. Their enthalpy is the base enthalpy minus ∫cp dT, computed in the script with CoolProp (oxygen; n-dodecane for RP-1) and recorded in the meta.
- `PAIRS`:
  - `LOX/UDMH`: MR 0.8–3.0 (stoichiometric is about 2.13).
  - `N2O4/UDMH`: MR 1.4–4.0 (stoichiometric is about 3.07).
  - `LOX/RP-1 (subcooled)`: the LOX/RP-1 grid.
- `COOLANTS`: a `LOX/RP-1 (subcooled)` n-dodecane entry with a T grid from 264 K. The existing LOX/RP-1 grid is left untouched. Note: the surrogate freezes at 263.6 K, while real RP-1 freezes around 225 K.
- Single-point Cantera runs for the new pairs' fuel-rich GG gas and the N2O4/UDMH ox-rich ORSC preburner gas (RD-253). The command and its output are recorded for C3.

**C2: Pair registry** (`physics/combustion.py`)
- `_TABLES` entries, needed so `available_pairs()` lists the new pairs. They are legacy fallbacks only and commented as such.
- `PAIR_VARIANT_OF` and `base_pair`.
- `PROPELLANT_DENSITIES`.
- `ETA_CF`, `L_STAR_DEFAULT_M` and `L_MID_BASE` (UDMH pairs: the storable analog, flagged in ASSUMPTIONS).

**C3: Per-pair physics data**
- `design/constants.py`: `GG_GAS_PROPERTIES`, `GG_MIXTURE_RATIO`, `COOLANT_INLET_TEMP_K` (266 K for subcooled) and `OXIDIZER_INLET_TEMP_K`.
- `staged_combustion.py`: `PREBURNER_GAS_PROPERTIES` and `ORSC_GAS_PROPERTIES` (N2O4/UDMH).
- `cooling/coolant_props.py` and `cooling/channels.py`: UDMH coolant entries.
- `gas_side.py`: Bartz 1.0, marked as un-anchored.
- `wall.py`: deposit factor (subcooled = RP-1).
- `injectors._BETA_BAND_DEG`.
- `ignition.py`:
  - N2O4/UDMH: hypergolic.
  - LOX/UDMH: pyrotechnic default, also plausible for TEA-TEB and spark torch.
  - Subcooled: TEA-TEB.
- `cost_model.PAIR_CLASS`: chosen by checking RD-119 and RD-253 residuals against the RP-1 snapshot.
- `tap_off.MIXER_PAIRS` += subcooled.
- `design/suction_stage.py`: `PUMPED_PROPELLANTS` for the new pairs, and a per-pair auto inlet temperature (`PAIR_AUTO_PROPELLANT_TEMP_K`). With it, "0 = auto" resolves to 66 K / 266 K for the subcooled pair, so NPSH, pump heating and the jacket inlet see the cold propellant.
- `plumbing.OX_VISCOSITY_PA_S`: N2O4 if it is missing.

**C4: Export** (`export/cfg_writer.py`)
- `_RF_PROPELLANTS`:
  - LOX/UDMH → UDMH / LqdOxygen.
  - N2O4/UDMH → UDMH / NTO.
  - Subcooled → CooledRP-1 / CooledLqdOxygen.
- Volume ratios must use RealFuels' own resource densities, not the physics densities. RF converts by its own resource definitions, and the Merlin 1D+ ratio 0.3877/0.6123 at MR 2.36 implies about 835/1248.
- Fetch the RealFuels resource cfg (GitHub), add a cited `RF_RESOURCE_DENSITY`, and check it against the Merlin 1D+ and RD-253 ratios in `Engine_Configs/`.
- Existing pairs' rendered output stays unchanged unless RF's densities differ, and any difference is reported before changing it.

**C5: Validation** (`physics/validate/performance.py` `SPOT_CHECKS`)
- RD-119: 7.9 MPa, eps 102, MR 1.5, 362 s vac. Anchor for LOX/UDMH.
- RD-112: 14.7 MPa, eps 31.8, MR 1.704, 344/304 s. Independent cross-check for LOX/UDMH.
- RD-253: 14.7 MPa, eps 26.3, MR 2.67, 315.5/284.5 s. Anchor for N2O4/UDMH.
- RD-0210 header row: cross-check for N2O4/UDMH, if its eps is confirmed.
- Merlin 1D+: 10.8 MPa, eps 21.4, MR 2.36, 311/282 s. Subcooled check with inherited η.
- RD-111A: 318/276 s. Reported, not gated, because its gain came from a redesigned injector.
- A cross-check that misses tolerance is reported honestly, not tuned away.
- Cooling-robustness combos pick up the new pairs, and all must stay finite and converged.

**C6: Docs**
- ASSUMPTIONS rows for every new constant, tiered.
- README pair list.
- CLAUDE.md: the validate "7 real engines" text and the banner count.
- claude_lit `OPEN_QUESTIONS` (Merlin densified temps, UDMH coolant data).
- Plan copy.

GUI needs no code change: the dropdown, MR range, L* and igniter all come from the registry. `app.py` gets a syntax check only (no `$DISPLAY`), and Cory clicks through it.

## Expected results (sanity, not targets)
- Subcooled LOX/RP-1 Isp should come out a few tenths of a second below saturated at the same MR, because of the colder reactants.
- The subcooled gains show up elsewhere:
  - Denser propellant → lower pump power and smaller ducts.
  - Larger NPSH margin.
  - The RF volume ratio (in game, more propellant mass in the same tank).
- The tool has no tank model, so the densification benefit at the vehicle level isn't shown. This will be stated in README.

## Verification
- `./verify_all.sh`: every module passes. `python3 -m engine_designer.physics.validate | grep -c '^ALL'` still shows 32, and the new SPOT_CHECK rows print within tolerance.
- `python3 -m engine_designer.validation_engines.run_corpus --check`: bit-identical to golden, which proves existing pairs are unchanged.
- The JSON diff shows old pair keys byte-identical after the merge.
- A throwaway script runs `EngineDesign(pair=…).compute()` for each new pair × {pressure-fed, GG, ORSC (N2O4/UDMH), tap-off (subcooled)} and checks the output is finite, then renders all 3 export modes through `cfg_writer` (the brace/token checks pass).
- Cory runs the GUI: picks each new pair and checks the MR slider range, the default igniter and the export.

## Checklist (as landed)
- [x] C1 generator: `SUBCOOLED_REACTANTS` + `_add_subcooled_reactants`, `--merge-pairs`, three PAIRS, subcooled n-dodecane coolant grid from 264 K; tables merged (old pairs byte-identical - verified by JSON diff); Sutton self-check passed
- [x] C2 registry: `physics/propellant_pairs.py` (`PAIR_VARIANT_OF` / `base_pair` / `alias_variants`), `_TABLES` rows sampled from the new tables at 7 MPa, densities, `ETA_CF` 0.9852 (RD-119) / 0.9730 (RD-253), L*, L_MID_BASE; variants listed after their base pair
- [x] C3 per-pair physics: coolant props / channels / Bartz / deposit, GG + preburner gas (Cantera ORSC check), inlet temperatures, `auto_propellant_temp_k` (shared by suction + tap-off), ignition, injector beta band + `base_pair` suitability, cost class (from the RP-1 fit's own `_snapshot_class`), tap-off mixer pairs
- [x] C4 export: `_RF_PROPELLANTS` + `RF_RESOURCE_DENSITY_KG_M3` (RO_Resources.cfg + CRP), new pairs only; self-test reproduces Merlin 1D+ / RD-253 / RD-109 volume ratios
- [x] C5 validation: SPOT_CHECKS RD-119 / RD-112 / RD-253 / RD-0210 / Merlin 1D+ / RD-111A (`gated=False`), cooling-robustness wall-construction sweep + new pairs, thermo_tables self-test #10
- [x] C6 docs: ASSUMPTIONS (Tier 1 note, Tier 2 + Tier 3 rows), README, OPEN_QUESTIONS, generator docstring, CLAUDE.md
- [x] GUI: turbopump diagram tank labels from `PUMPED_PROPELLANTS` (also fixes A-50's swapped labels), temperature-slider hint text - syntax/Agg-checked only, Cory to click through
