# Export plumes: host-inherited + recolored, or generated from the design

(The previous plan in this file, the TestFlight burn-time round, is committed as
`engine_designer/plans/2026-10-16_testflight_burn_time.md`. PR #32 is awaiting Cory's test.)

## Context

Cory: "there is no rocket plume from any of the cfgs."

**Root cause (verified in upstream/):**
- Every tool export in standalone mode clones the host at `+PART[ROE-xxx]:BEFORE[RealismOverhaulEngines]`. This covers `Bell Model 8760_Config.cfg` and `RS-29_Config.cfg`.
- ROEngines adds plumes later, by the donor's *name*:
  - `Waterfall/<Propellant>/<engine>.cfg` uses `@PART[ROE-AJ10-transtar]:BEFORE[ROWaterfall]:NEEDS[Waterfall]` with a `ROWaterfall { template, audio, transform, position, rotation, scale, glow }` node.
  - `RealPlume/*.cfg` uses `:BEFORE[RealPlume]:NEEDS[!Waterfall]`.
- RO's processor (`RealismOverhaul/Waterfall_Configs/_Processor/`) turns any `@PART[*]:HAS[@ROWaterfall]` into ModuleWaterfallFX from `FOR[ROWaterfall]` onward.
- Our clone has a new name and no `ROWaterfall` node, so it never gets a plume. `cfg_writer.py` writes nothing plume-related.
- `additional_config` / `new_part_in_place` keep the host's plume, but in the host's propellant colour.

**Cory's request:** selectable plume options.
1. Inherit the host's plume and recolour it for the design's propellant (basic).
2. Generate the plume from the design: Pc, propellant, expansion and so on, placed on the model. This is the lead-up to the tool's own generated models, where the exit plane is known exactly.

## Design: new export field `plume_mode` (schema 23)

`EngineDesign.plume_mode`: `"host"` (default) | `"generated"` | `"none"`. Migration: a pre-23 file gets `"host"`.

### Data: `catalog/build_roengines_models.py` → new `catalog/roengines_plumes.json`
- Scrape `ROEngines/Waterfall/**/*.cfg` and `ROEngines/RealPlume/*.cfg` with `catalog/mmcfg.py`.
- Resolve each header's part selector against every ROEngines part name:
  - MM `|` alternatives and `*`/`?` wildcards (e.g. `ROE-Star37*`, `ROE-Algol1|ROE-Algol2`).
  - Record the pass and NEEDS.
- Per part:
  - The `ROWaterfall` node verbatim (incl. `ExtraTemplate` / `MainPlumeVariant`).
  - The propellant folder (Kerolox / Hydrolox / Methalox / Hypergolic / ...).
  - The RealPlume `PLUME` nodes and `powerEffectName`.
  - Plus the part's `rescaleFactor` (already parsed in `parse_file`).
- Derived tables, all from RO's own data (nothing hand-picked):
  - `TEMPLATE_BY_PAIR[pair][lower|upper]` = the template that ROEngines uses most often on real engines with that propellant pair. The pair → real engine join comes from `Engine_Configs` / `catalog.json`. The glow comes along with the template.
  - `AUDIO_BY_CLASS`: `pressure-fed-1` for pressure-fed. Pump-fed light/medium/heavy bands are fitted from the corpus as audio name vs. real thrust.
- Self-test asserts:
  - the AJ10-transtar → `waterfall-hypergolic-white-upper-1`, scale 0.82;
  - E1, RD-107 (an `ExtraTemplate`) and Star37 (a wildcard) are present;
  - the commit hash is recorded, the same as `roengines_models.json`.
- Licence note: only derived numbers and names leave ROEngines (CC BY-NC-ND), the same rule as the model heights.

### Mode 1, `host`: `export/plume.py` (new, pure)
- **Standalone clone (the bug fix).** Emit `@PART[<new>]:NEEDS[Waterfall]:BEFORE[ROWaterfall]` containing the donor's `ROWaterfall` node, written as literal values from the snapshot. A paste can't be used: the donor's own node is added in the same pass, so order isn't guaranteed.
  - The processor then strips the stock EFFECTS and builds the module.
  - RealPlume fallback: `@PART[<new>]:NEEDS[!Waterfall]:BEFORE[RealPlume]` with the donor's `PLUME` nodes and `%powerEffectName` on our CONFIG.
- **Recolour.** If the design's pair differs from the donor's folder, swap `template` / `glow` for `TEMPLATE_BY_PAIR[pair][role]` and keep the donor's `position` / `scale`. That matches RO's own practice: `MainPlumeVariant` inherits the parent scale (`18_late-initialize.cfg`), and the glow is re-sized automatically (`39_glow-resize.cfg`).
  - The one exception is RO's own cold-gas / monoprop factor of 12.65625 (`15_auto-config.cfg`), which applies to HTP / hydrazine monoprops.
  - Role = `burn_time.engine_role`, lower = booster.
- **additional_config / in_place.** These can't change the host's main plume for other configs. Use RO's own per-CONFIG mechanism:
  - add a `MainPlumeVariant { name = engdes-<config>; template; glowRecolor }` to the host's `ROWaterfall` at `:AFTER[ROWaterfall]` (before `zROWaterfall_10`, and after every `BEFORE[ROWaterfall]` node exists);
  - set `%rowaterfallVariant` on our CONFIG (`NEEDS[Waterfall&B9PartSwitch]`).
- If the donor has no plume data: fall back to `generated` and add an `export_issues` warning.

### Mode 2, `generated`: v1 in this round
- **Template:** the pair from `TEMPLATE_BY_PAIR`. lower vs. upper comes from the physics, not a guess: the sea-level Pe/Pa from `result` (over-expanded / sea-level → lower, vacuum → upper), cross-checked with `engine_role`.
- **Scale:** from the design's computed exit diameter, × a per-template normalisation `k_template` (plume scale per metre of exit diameter).
  - `k_template` is fitted on RO's own placements: ROEngines `scale × part rescaleFactor ÷ D_exit` for the validation-corpus engines that have a ROEngines plume (F-1, J-2, RS-25, RD-180, Merlin, RL10, Vulcain, Aestus, ...), with D_exit from the corpus' `compute()`.
  - Each `k` is reported with its scatter. A template with no anchor uses its folder's median and is flagged.
- **Position:**
  - Borrowed model: the donor's exit-plane anchor (its ROEngines plume position, which scales with the model).
  - No donor plume: the nozzle exit estimated from the model height on `thrustTransform`, with a warning.
  - Tool-generated models (future): the exit plane is exact from `geometry`.
- **Audio:** from cycle and thrust (`AUDIO_BY_CLASS`). **Glow:** from the template.
- This makes Pc, MR, eps and thrust move the export: regime, size and audio.
- **Out of scope here, Round P2 (outline only):** physics-*shaped* plumes. This means a per-design `EFFECTTEMPLATE`, with plume boundary expansion vs. altitude from the Prandtl–Meyer turning at the lip (`physics/isentropic.py`), shock-cell spacing, and afterburning / soot colour.
  - It needs Waterfall's base templates (not in `upstream/`; clone `post-kerbin-mining-corporation/Waterfall` as reference) plus plume literature. `claude_lit` has none; add it to `OPEN_QUESTIONS`.

### GUI and docs
- `gui/app.py`, Export section: a "Plume" combobox (Host plume, recoloured / Generated from design / None), plus a readout line: template · scale · source (donor X / fitted k ± scatter). Syntax and import check only.
- `cfg_writer` header comment line `Plume: ...`.
- README "Export" (plume semantics and the pass ordering), ASSUMPTIONS rows (`TEMPLATE_BY_PAIR`, `k_template` fit, AUDIO bands), CLAUDE.md (module list and the verify line for the plume snapshot).
- Memory: `reference_rf_rp1_export_semantics.md` gets one line on the ROWaterfall pass ordering.

## Critical files
- `engine_designer/catalog/build_roengines_models.py` (+ `roengines_plumes.json`), reusing `catalog/mmcfg.py`.
- `engine_designer/export/plume.py` (new), `export/cfg_writer.py` (`resolve_export` gains `plume`; `render_cfg` emits the blocks for all three output modes).
- `physics/design/engine.py` (field, schema 23, migration), `gui/project_io.py` (v23 round-trip test), `gui/app.py`.
- `verify_all.sh` (the plume snapshot self-test, if it isn't run inside `build_roengines_models`).

## Branch
`export/plumes`, STACKED on `testflight/burn-time` (both touch `cfg_writer` / schema). Draft PR, not merged until Cory tests in game. Plan copy goes to `engine_designer/plans/2026-10-16_export_plumes.md`.

## Verification
- `./verify_all.sh`: all PASS.
- `cfg_writer` self-test renders all 3 output modes × 3 plume modes and checks:
  - balanced braces;
  - standalone + host contains `@PART[<new>]:NEEDS[Waterfall]:BEFORE[ROWaterfall]` with the donor scale;
  - a LOX/RP-1 design on the AJ10-transtar donor gets a kerolox template;
  - additional_config writes `rowaterfallVariant` + a `MainPlumeVariant`;
  - `none` writes nothing.
- `k_template` fit: each anchor engine is reproduced within its reported scatter.
- Golden corpus is unchanged (export-only; `run_corpus --check` stays bit-identical).
- Re-export Bell Model 8760 (and RS-29) in both modes.
- **Cory, in game:** the plume appears on the standalone part, is kerolox-coloured on the Transtar model, is sized right at the nozzle exit, and still works with RealPlume-only installs if he has one.

## As built (2026-10-16) - deviations from the plan above

- The scraper is its own module, `catalog/build_roengines_plumes.py` (not folded into
  `build_roengines_models.py`), registered in `verify_all.sh` with `export/plume.py`.
- **Scale convention found in Waterfall's source** (`WaterfallEffect.InitializeEffect`,
  `SetParent(parent, worldPositionStays=true)`): a plume's world size is its `scale` and
  ignores the part's `rescaleFactor` unless `useRelativeScaling = true`. So:
  - k_template is fitted on `scale` itself (× rescaleFactor only for relative parts);
  - a rescaled clone / in-place host multiplies a non-relative plume's scale by the model
    scale (otherwise the shrunken nozzle kept the donor's full-size plume);
  - a generated plume writes `scale = k × exit diameter` and drops useRelativeScaling.
- k_template is fitted on every ROEngines part whose RO config header gives thrust / Pc /
  eps (exit diameter from At = F/(Pc CF_vac)), not only the validation-corpus engines - 37
  templates instead of ~8.
- Recolor rescales by k_new / k_old instead of RO's "inherit the parent scale": checked
  against RO's own 23 MainPlumeVariants, median miss 17 % vs 68 % for keeping the scale.

## Checklist
- [x] Scraper + `roengines_plumes.json` snapshot (self-test: Transtar, E1, RD-107, Star37 wildcard, recolor check)
- [x] `export/plume.py` (host / generated / none) + `cfg_writer` wiring + self-test (3 output modes × 3 plume modes)
- [x] Schema 23 `plume_mode` + project_io test; corpus re-snapshotted (inputs echo only)
- [x] GUI "Plume" dropdown + preview line (syntax/import only - no display here)
- [x] README "Plume", ASSUMPTIONS row, CLAUDE.md, OPEN_QUESTIONS (P2 literature)
- [ ] Cory: in-game check (plume visible on a standalone part, kerolox-coloured on the Transtar model, sized to the nozzle; RealPlume-only install if available)
- [ ] Round P2: physically shaped plumes (needs literature + Waterfall templates)
