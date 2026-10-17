# Export fix: KSP / ModuleManager / RealFuels / RP-1 identity, gating and cost

## Context

Cory reported three problems with the exported `.cfg`: there's no visible way to set the RP-1 tech node, it's unclear what name / title / manufacturer mean, and there's no description field. I checked the exporter (`engine_designer/export/cfg_writer.py`, GUI `gui/app.py`) against the vendored `upstream/RP-1` and `upstream/ROEngines` trees and against the RealFuels C# source (`KSP-RO/RealFuels`: `ModuleEngineConfigs.cs`, `EntryCosts/*.cs`). The labels are confusing, and there are also real bugs in what gets exported.

### How the pieces actually work (verified)

| Field | Lives on | What KSP / RF / RP-1 do with it |
|---|---|---|
| part `name` | PART | Internal ID. No spaces or dots. It's the `@PART[...]` selector, and RP-1's TREE-Parts and ENTRYCOSTMODS key on it. |
| part `title` | PART | The name shown in the VAB. |
| `manufacturer` | PART | The VAB manufacturer line and filter. |
| part `description` | PART | The VAB part-info text. |
| `engineType` | PART | RO's own key (`@PART[*]:HAS[#engineType[X]]`). The clone gets its own, so RO's FOR-pass title/config patches skip it. |
| CONFIG `name` | ModuleEngineConfigs | The entry in the RF engine-config picker. It's also the global key for `techRequired`, the RF unlock database, ENTRYCOSTMODS and TestFlight, so it must be unique across every installed engine. |
| CONFIG `description` | CONFIG | The text shown in the RF picker. |
| CONFIG `techRequired` | CONFIG | Gates the config in RF's `Validate`. |
| CONFIG `cost` | CONFIG | A **delta** on top of the part cost. Example: the H-1 part costs 392 and its configs add 0, +21 or +67. AJ10-153 is −62. |
| CONFIG `entryCost` | CONFIG | **Never read by RF.** Config entry cost is `EntryCostDatabase.GetCost(cfgName)`, which comes only from `ENTRYCOSTMODS { cfgName = cost[, parentCfg...] }` and is 0 when there's no entry. |
| PART `TechRequired` / `cost` / `entryCost` / `RP0conf` | PART | RP-1 sets these per part name in `TREE-Parts.cfg :FOR[xxxRP0]`. `NonRP0.cfg :FOR[zzzRP-0]` relabels any part that has no `RP0conf`. |
| `ModuleTagList { tag = EngineLiquidTurbo / EngineLiquidPF }` | PART | RP-1 KCT launch-cost multiplier: ×4 for pump-fed, ×1.75 for pressure-fed (`SCMData/CostModifiers.cfg`). |
| `PARTUPGRADE RFUpgrade_<cfg>` | root | **Not auto-created by RF**; RP-1 writes them by hand in TREE-Engines. Only the tree icon. With no ECM entry its cost is 0, and RF auto-unlocks it once the node is researched. |

### Bugs this explains

1. **The standalone part is broken in RP-1.** The `+PART` clone inherits ROEngines' `ROESetEngineDefaults` (`TechRequired = start`, `cost = 1`, `entryCost = 1`) and has no `RP0conf`. RP-1 then shows the title as "non RP-0 - Bell Model 8760" and appends "(PART NOT SUPPORTED BY RP-0)" to the description. The part sits in `start` (or in ORPHANS under NoNonRP0), costs about 13 funds, and has no turbo tag. The tech node is only ever written on the CONFIG.
2. **`%entryCost` on the CONFIG does nothing.** As a result, every exported config is free once its node is researched.
3. **The cost has the wrong meaning and scale.** The cost model returns delta-sized numbers (8–60 for a 1.4 MN engine) but they are treated as the engine's cost.
4. **The identity UI is confusing.** "New Part Identity" has three unlabeled Entry boxes under one shared label. RS-29 got the title "Rocketdyne" because the manufacturer was typed into the title box. Bell Model 8760 kept the default CONFIG name `MyEngine-100K`, which collides with every other un-renamed export. There's no field for either description. The tech node is in a separate "Export & Metadata" section at the bottom that starts collapsed. Its current saved value is `tech_node = ''`, so no gating was written.
5. **User text can break the patch.** Spaces in a CONFIG name break `@CONFIG[...]` and the RF/ECM keys (RF sanitizes `.` and `_` to `-`). A `//` or a brace in a description silently truncates the patch.

The existing tech-node suggestions were checked against the vendored `RP0TechTree.cfg` (332 nodes) and all are valid.

6. **The model variant can't be chosen** (Cory, mid-planning: "use the XLR-11 upgraded model with a really long bell instead of the default"). ROEngines puts variants on one part as `ModuleB9PartSwitch` SUBTYPEs. Each SUBTYPE toggles transforms and can move `NODE`s. Each RF CONFIG then picks its variant with `LinkB9PSModule[<moduleID>] { subtype = X }`.
   - Example: `ROE-XLR11` has `moduleID = model` with subtypes `rm3` and `rm5`, and its own patch sets `@CONFIG,* { %LinkB9PSModule[model] { subtype = rm5 } }` plus `XLR11-RM-3 → rm3`.
   - Across ROEngines there are 16 `nozzle` switchers (LR105 XNA3/NA3/NA6, LR87, LR91, RL10, H-1, M-1…), 5 `model`, and a number of `meshSwitch*`/`engineSwitch` ones.
   - Those links are written against the donor's part **name**. The exporter writes no link, so a standalone clone falls back to the first SUBTYPE (for XLR-11, `rm3`). In additional_config mode the CONFIG gets whatever ROE's `@CONFIG,*` default patch adds, which depends on pass order.
   - `roengines_models.json` stores one height per part, so a longer-bell variant is also scaled wrong.

## Approach

Work on a new branch, `export/rp1-identity`, off `origin/main`, with a draft PR that isn't merged until Cory tests it. Save a copy of this plan with a per-commit checklist to `engine_designer/plans/2026-10-15_export_rp1_identity.md`. Hand-written H3/H4/TR341 files are **not** touched (Cory's call).

### C1 — RP-1 snapshot (`engine_designer/catalog/build_rp1_snapshot.py` → `rp1_snapshot.json`)
Modelled on `build_roengines_models.py`: it finds `upstream/RP-1` automatically, records the commit, and outputs derived numbers only (RP-1 is CC-BY-NC-SA).
- Tech nodes from `RP0TechTree.cfg`: `id`, `title`, parent ids.
- Engine part costs from `TREE-Parts.cfg`: part name → TechRequired, cost, tag.
- Config deltas and tech from `TREE-Engines.cfg`: cfg → techRequired, cost delta.
- `ECM-Engines.cfg`: cfg → entry cost and parents.
- Per-config `maxThrust`, `pressureFed`, `PROPELLANT` names, parsed from `Engine_Configs/` with a small brace parser, plus engineType → part names from `roengines_models.json`.

The self-test checks it parses and that known rows are present, for example `ROE-AJ10-transtar` cost 138, the H-1 part cost 392 and `orbitalRocketry1976`'s title. Add it to `verify_all.sh` and the CLAUDE.md module list.

### C1b — Model variants in the ROEngines snapshot (`catalog/build_roengines_models.py`)
- For each part, record `variants`: its `ModuleB9PartSwitch` modules, excluding effect-only ones (`throttleColor`, `heatColor`, plume/exhaust switches). Each entry stores `moduleID`, `switcherDescription`, and SUBTYPEs as `{name, transforms, node_bottom_m / node_top_m if a NODE moves}`.
- Add `linked_configs`: subtype → the RO/ROE CONFIG names that select it, scraped from `LinkB9PSModule[...]` in ROE PartConfigs and in `Engine_Configs/`, including the `@CONFIG,*` default. This lets the dropdown read "rm5 — used by XLR11-RM-5, RM-13-8K, RM-13-10K".
- Per-variant `native_height_m` uses the subtype's moved bottom/top node when there is one. Otherwise it falls back to the part height and sets `height_from_part = true`. A variant that only toggles transforms has no measurable length without the mesh, so the GUI says so and points to the existing "reference height" override.
- The self-test checks that `ROE-XLR11` has `model: [rm3, rm5]` with `XLR11-RM-3 → rm3`, and that LR105 has `nozzle: [XNA3, NA3, NA6]`. Rebuild the committed snapshot.

### C2 — Re-fit the cost model (`physics/cost_model.py`)
- `estimate_cost` returns the **absolute** engine cost: part cost plus config delta, joined over the snapshot rows. The fit is log-linear in vacuum thrust, with a pumped vs. pressure-fed factor and a propellant-class factor. The existing cycle-complexity multipliers stay as labelled estimates where the data are too thin. The self-test reports RMS log error and per-class residuals honestly, with loose gates.
- Entry cost keeps its form. It is sanity-checked against ECM root entries (those with no parents) and reported, not gated.
- Add `host_part_cost(engine_type)`, the median TREE-Parts cost over that engineType's part names, or `None`.
- `ASSUMPTIONS.md`: change the cost rows' tier and citation to the RP-1 snapshot fit, with its scatter.

### C3 — `export/cfg_writer.py`
- Add `_cfg_token()`, which turns the CONFIG name and part name into `[A-Za-z0-9-]` (spaces, `.` and `_` become `-`). Add `_cfg_value()`, which turns descriptions and titles into a single line with no braces and no `//`.
- **Standalone mode**, when a tech node is set: add a new `@PART[<new>]:NEEDS[RP-0]:AFTER[xxxRP0]` patch with `%TechRequired`, `%cost = <absolute>`, `%entryCost = 0`, `%RP0conf = true` and `%MODULE[ModuleTagList] { tag = EngineLiquidTurbo | EngineLiquidPF }`. The CONFIG `cost` becomes 0. This follows RP-1's own engine-part convention, where the part entry cost is 0 and the config carries the ECM.
- **additional_config / in-place**: CONFIG `%cost = absolute − host_part_cost`. If the host cost is unknown, write 0 and add a warning.
- Every mode with a tech node gets a gating patch with `%techRequired` and `%cost`, without `%entryCost`. It also gets a root `ENTRYCOSTMODS:NEEDS[RP-0] { <cfg> = <entry>[, parents] }`. A root node is used, rather than an `@` patch, so it works no matter when RP-1's own node is created; RF's `FillHolders` reads every ENTRYCOSTMODS node.
- When `rp1_tree_icon` is on: add `PARTUPGRADE:NEEDS[RP-0] { name = RFUpgrade_<cfg>  partIcon = <host part_name | new part>  techRequired  entryCost = 0  cost = 0  title  basicInfo  manufacturer = Engine Upgrade  description }`, in RP-1's TREE-Engines format.
- **Model variant link.** For each chosen `{moduleID: subtype}` in `design.host_model_variants`, add a separate, non-RP-0-gated patch: `<target_selector>:NEEDS[RealismOverhaul&RealFuels]:BEFORE[RealismOverhaulEnginesPost] { @MODULE[ModuleEngineConfigs] { @CONFIG[<cfg>] { !LinkB9PSModule[<id>],* {}  LinkB9PSModule[<id>] { subtype = <name> } } } }`. It runs after every `AFTER[RealismOverhaulEngines]` patch, including ROE's `@CONFIG,*` default, so the choice always wins and isn't duplicated. In standalone mode the clone keeps the donor's B9PS modules, so the link is all it needs. Model scale uses the selected variant's height. An unknown moduleID or subtype is a warn row and is written anyway.
- CONFIG `description` comes from a new `config_description` field (blank keeps the current auto text). Part description comes from `new_part_description`.
- `export_issues(design, result)` returns warn-only strings, which the GUI and the header both show:
  - default or empty CONFIG name;
  - no tech node: "RP-1 will label this part 'non RP-0' and leave it in start";
  - host part cost unknown;
  - text was sanitized.
- Self-test: add asserts per mode for each of the blocks above, check there's no `%entryCost` inside a CONFIG, check `_balanced`, and check that hostile text (spaces, `//`, `{`) is sanitized.

### C4 — Design fields and save files (`physics/design/engine.py`, `gui/project_io.py`)
- New fields: `config_description: str = ""`, `rp1_ecm_parents: str = ""` (comma list, tech-transfer discount parents), `rp1_tree_icon: bool = True`, and `host_model_variants: dict = {}` (`{moduleID: subtype}`, empty = the part's own default). Changing the host clears it. Because it feeds model scale, it goes through `_on_control_change`, not the export-only path.
- Bump `SCHEMA_VERSION` to the next free number. Main is at 19, and PR #27 / `refactor/design-inputs` both claim 20, so note the collision in the PR. Migration: an older file's `cost` was delta-scale, so it's reset to the new estimate and a one-time warning row is shown.
- Run the `project_io` round-trip self-test.

### C5 — GUI (`gui/app.py`, syntax/import check only, no `$DISPLAY`)
Replace "New Part Identity" and the collapsed "Export & Metadata" with one **"Export (KSP / RP-1)"** section that starts open. Each field gets its own label and one-line hint, and fields are enabled per output mode:
- **Host model variant** (in the Host Model section, under the host dropdown): one dropdown per switcher the chosen host has, for example "Nozzle: NA6 (used by LR105-NA-6)". The first entry is "(part default)". When the variant's height came from the part rather than a moved node, a note appears beside the dropdown.
- **Engine config:** CONFIG name ("RF picker entry; must be unique - also the RP-1/TestFlight key", with a live sanitized preview) and config description.
- **New part** (standalone only; greyed with a reason otherwise): part name (internal ID, preview), title (VAB name), manufacturer, and part description (multi-line).
- **RP-1 career:** tech node combobox showing `id — title` from the snapshot, still free-typed; entry cost; engine cost (absolute, with the computed config delta shown); ECM parent configs; and a "Show in tech tree" checkbox.
- `_on_export`: if `export_issues` is non-empty, show a warning dialog with Continue/Cancel. It warns but never blocks.

### C6 — Docs
- README export section: the field table above, the MM pass order used (`BEFORE[RealismOverhaulEngines]` clone → `AFTER[RealismOverhaulEngines]` engine → `BEFORE[RealismOverhaulEnginesPost]` config gating → `AFTER[xxxRP0]` part gating, before `zzzRP-0`'s NonRP0 pass), and the ENTRYCOSTMODS note.
- Update CLAUDE.md (export bullet, module list) and ASSUMPTIONS.md.
- Add a memory note: "CONFIG entryCost is dead in RF; use ENTRYCOSTMODS".

## Critical files
- `engine_designer/export/cfg_writer.py` — rendering, sanitizing, `export_issues`.
- `engine_designer/physics/cost_model.py` — absolute-cost re-fit and `host_part_cost`.
- `engine_designer/catalog/build_rp1_snapshot.py` (new) and `rp1_snapshot.json` (new). Reuse `build_roengines_models.py`'s upstream auto-detect and its `roengines_models.json` part_name map.
- `engine_designer/physics/tech_tree.py` — suggestions plus node titles from the snapshot.
- `engine_designer/physics/design/engine.py`, `engine_designer/gui/project_io.py` — fields, schema, migration.
- `engine_designer/gui/app.py` — the export section.

## Verification
- `./verify_all.sh` all PASS. That covers the new `catalog.build_rp1_snapshot` module, `physics.cost_model`'s fit report, `export.cfg_writer`'s per-mode asserts, `gui.project_io`'s round-trip and migration, and `validate`, whose banner count must be unchanged.
- `run_corpus.py --check`: bit-identical expected, since cost is export-only. If anything moves, investigate before snapshotting.
- Export an XLR-11-hosted design with variant `model: rm5` in standalone and additional_config modes. Check the link patch sits at `BEFORE[RealismOverhaulEnginesPost]` and that the scale uses rm5's moved bottom node.
- Re-export `Bell Model 8760.json` in all three modes with tech node `orbitalRocketry1986`. Diff by hand against RP-1's own ROE-AJ10-transtar TREE-Parts/TREE-Engines/ECM entries for the same shape.
- Cory checks in game, which can't be done here: the chosen variant's model shows on the part, the part shows with the right title (no "non RP-0"), sits in the chosen node with its icon, the RF picker charges the entry cost, and the VAB cost is sensible. The GUI section also has to be clicked through by Cory.

## Checklist (branch `export/rp1-identity`)
- [x] C1 `catalog/mmcfg.py` parser + `build_rp1_snapshot.py` / `rp1_snapshot.json` (+ verify_all.sh)
- [x] C1b ROEngines variants + alt parts in `roengines_models.json`; `catalog.host_model_parts` / `host_native_height_m`
- [x] C2 `cost_model.py` absolute-cost re-fit (self-test re-fits from the snapshot); ASSUMPTIONS rows
- [x] C3 `cfg_writer.resolve_export` / `export_issues`; clone ONE named part; RP-1 PART placement; CONFIG delta; ENTRYCOSTMODS; PARTUPGRADE icon; LinkB9PSModule variant patch; sanitizing
- [x] C4 schema 21 fields + cost reset migration; project_io round-trip test
- [x] C5 GUI: host part + variant pickers, unified "Export (KSP / RP-1)" section, live export notes, export Continue/Cancel dialog (syntax/import + pyflakes only - no display here)
- [x] C6 README "Export", ASSUMPTIONS, CLAUDE.md, UPSTREAM_REPOS.md; corpus re-snapshot (inputs-only diff, report saved)
- [ ] Cory: click through the GUI section; in game - part title has no "non RP-0", sits in the chosen node, RF picker charges the entry cost, VAB cost sensible, chosen model variant shows
