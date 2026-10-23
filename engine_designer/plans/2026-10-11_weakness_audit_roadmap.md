# Roadmap: engine_designer weakness audit + phased plan (2026-10-11)

Master roadmap. Supersedes the ordering in `2026-09-25_turbopump_fidelity_roadmap.md`, whose Round 3+ / E3+ items are folded into Phase 4 below. Each phase gets its own plan-mode round, branch off `origin/main` and draft PR; tick boxes here as items land.

## Status
- [ ] Phase 0: unblock
- [ ] Phase 1: trustworthy numbers
- [ ] Phase 2: KSP export
- [ ] Phase 3: port contract + field registry
- [ ] Phase 4: turbopump workspace + turbine meanline
- [ ] Phase 5: depth, as wanted

## Context
Cory asked for the tool's weak points and a roadmap for what comes next. His answers set the frame:
- **Goal:** a "middle ground" that gives an accurate *design approximation* of real engines. Physics fidelity is a high priority, but the bar stops short of anything CFD-class or minutes-long to compute.
- **Qt6/C++ GUI:** in progress now. The Python physics gets ported once its depth is satisfactory. That makes the Python physics the reference implementation, so port-readiness matters.
- **Pain points:** "can't trust the numbers" and "every round costs more." Cory also wants tooltips on every knob, and wants the turbopump panel split into its own Shape-Lab-style workspace.
- **KSP export:** hasn't been used in a while. It had issues in the past and its current bugs are unknown.
- **Next physics interest:** turbine meanline (Round 3) and turbopump design customizability.
- **Decisions made:**
  1. Trust before turbopump features.
  2. Merge PR #27, then redo the nesting refactor fresh as schema 21.
  3. Keep one Python field registry that both GUIs read; prototype the turbopump workspace in Tk.
  4. Retire most legacy model switches.

The audit covered physics, architecture/port-readiness and usability/export/testing, run in parallel. I verified the two headline bugs in the code myself.

## Weaknesses (ranked)

### A. Numbers you can't trust (physics)
1. **HIGH, verified: dry mass is 3-11× too heavy, and that mass is exported.**
   - Cause: `physics/design/structure_stage.py:36-43` sizes both the chamber and the extension with `mass_model.shell_mass_kg(..., chamber_pressure_pa, ...)`, i.e. flat Pc all the way to the exit. The local-pressure thickness right below it is used for *rendering only*.
   - Model results: RS-25 35.8 t (real ~3.3 t), F-1 25.4 t (real ~8.4 t), RL10 478 kg (real ~135 kg).
   - It feeds `origMass` in the exported cfg (`export/cfg_writer.py:324`).
2. **HIGH, verified: the expander turbine power has the wrong form.**
   - `physics/expander.py:96-100` uses power = min(Q_wall, absorbable) × η, and it is live via `geometry_stage.py:100`.
   - The correct form is ṁ·η·cp·T_in·(1−PR^-(γ-1)/γ). With the current form the RL10-class thrust ceiling can never bind.
   - The validate row only checks margin ≥ 1, so the test can't catch this.
3. **HIGH: the regen Isp credit is double-counted and applied after thrust sizing.**
   - `ETA_CF[LOX/LH2]` was fitted without the credit, then `cooling_stage.py:430-439` adds +1.5% after mass flow is already set.
   - Result: RL10 Isp is +2.4% on its own anchor, and RL10 and Rutherford miss their target thrust.
4. **HIGH: the validation gates can't catch these problems.**
   - Corpus pass/fail is only vacuum Isp ±5% and thrust ±1% (thrust is an input).
   - Mass, jacket dP and pump pressure have no reference band.
   - SPOT_CHECKS are tautological, because they run on the same engines `ETA_CF` was solved on.
5. **MED: kerolox Isp runs 3.5-9% low.**
   - Cause: there is one lumped `ETA_CF` per pair, with no kinetic/boundary-layer split, even though the tables already carry a frozen-Isp column.
6. **MED: real flight engines read as thermally infeasible.**
   - RD-180 chamber margin 0.74 (1,087 K vs 800 K); Raptor 0.84; Rutherford 0.72.
   - Likely causes: no film belts and no RP-1/CH4 throat-flux anchor.
7. **MED: LH2 jacket dP is 3-5× too high.**
   - RL10 12.1 MPa vs ~1-2 MPa real; J-2's band was widened to absorb it.
   - Cause: passages are sized on inlet velocity.
8. **MED: new designs default to a different jacket model than the one validated.**
   - `regen_channel_model` defaults to `"flat"` (flat 1.6 MPa); the corpus validates `"channels"`.
9. **MED: the staged-combustion cycle doesn't close at high Pc.**
   - RD-180 power margin 0.92, discharge 3.56×Pc; the 800 K ox-rich preburner temperature is unsourced.
10. **LOW-MED: smaller gaps.**
    - Sea-level Isp of vacuum nozzles is exported as a 1.0 s placeholder.
    - Storables have zero vapor pressure.
    - Aerozine-50 has no coolant data.
    - Monoprop tables are legacy.
    - Iteration loops have no convergence reporting; worst case is 30 passes, and the thrust closure exits after 6 iterations with no flag.

### B. Every round costs more (architecture)
1. **HIGH: the branch collision.**
   - `refactor/design-inputs` and PR #27 both claim schema 20 and share 31 files, including all of golden.
   - The refactor is 17 commits behind, and local `main` is 75 commits stale.
2. **HIGH: the golden check is bit-exact on the entire result dict.**
   - It compares floats by `repr`, plus 337 English strings, totalling 2.4 MB. 34 commits have had to re-snapshot it.
   - It can't serve as a C++ port oracle, and any wording change forces a re-snapshot.
3. **HIGH: the result is untyped and not JSON-safe.**
   - About 1,740 string keys, consumed through 1,168 subscripts.
   - Mixed `np.float64`/`np.bool_` values and inf/NaN; `json.dumps(result)` fails.
4. **MED: stage state is implicit.** `PassState` is an empty attribute bag holding about 225 names written by 21 stages.
5. **MED: `EngineDesign` is flat with sentinel defaults.** 132 fields; 52 use 0 = auto and 10 use "auto"; `plumbing_runs` is a list of untyped dicts.
6. **MED: seven model switches keep the old behaviour alive; none is in the corpus.**
7. **MED: schema migration is unversioned and lossy.**
   - `from_dict` never reads `schema_version`, and unknown keys are dropped silently.
   - `project_io` lives in `gui/`, but physics imports it.
8. **MED: the GUI holds business logic.**
   - Cost, massMult and model scale are computed in `app.py:3358-3413`.
   - The cooling-method filter is duplicated.
   - `_on_control_change` and `_refresh_widgets_from_design` are hand-mirrored.
   - `_build_layout` is 1,515 lines.
   - `mesh_builder` re-runs physics: flow network, plumbing resolve, manifold sizing.
9. **LOW-MED: constants and docs.**
   - Constants are duplicated: `PA_SEA_LEVEL` 3×, `PC_REF_PA` 2×, a subsonic-Mach solver 2×.
   - 78 data tables are Python literals.
   - CLAUDE.md is 48 KB (~12k tokens every session) and mixes rules with changelogs.

### C. Usability and the KSP export
1. **HIGH: the default host is a template that doesn't exist in KSP.** It is `catalog[0]` = `EXAMPLE` (`NEEDS[DONOTRUNME]`), so a fresh export silently does nothing.
2. **HIGH: exports are never checked to load and go stale silently.**
   - The config name isn't sanitized (`"TestEngine 1M!"` ends up in `@CONFIG[...]`).
   - There is no version/hash stamp; re-rendering RS-29 today changes Isp by 3 s, mass, rpm and warnings.
3. **HIGH: the hand-made configs aren't dogfooded.**
   - The tool can't reproduce H3/H4/TR341: no SUBCONFIG, no multi-CONFIG, no pressurant.
   - Three generated cfgs have no project file.
   - The corpus copy of RS-29 is schema 4, while the live file is schema 15.
4. **HIGH: the warnings are noisy.**
   - The default design fails 6 of 64 checks, two of which contradict each other.
   - Real engines fail 10-16 checks (RS-25 "TEA-TEB unusual for LOX/LH2", "~31 pump stages").
   - So users learn to ignore warnings.
5. **MED: hard-coded export fields.**
   - `ullage=True` for every biprop, `heatProduction`, the throttle-curve shape.
   - Missing `techTransfer` (used by 207/315 real configs).
   - Tested/rated burn time is 14× (the RO median is 3×).
   - Entry cost is not done the RP-1 way (`@ENTRYCOSTMODS`).
   - Loading a project marks cost as overridden.
6. **MED: the input surface lacks guidance.**
   - ~165 controls, 0 tooltips, no basic/advanced split.
   - The 315-entry host dropdown has no search.
   - No presets from real engines, no undo, no unsaved-changes prompt, no A/B comparison, and only one sweep.
7. **HIGH: no CI and no human quickstart.**
   - CI is PR-review bots only; nothing runs `verify_all.sh`.
   - The top-level README is 42 bytes; the engine_designer README is 65 KB with no design→export→GameData walkthrough.

### Not weaknesses / leave alone
- Physics never imports the GUI.
- SciPy use is tiny (3× `brentq` + 1 interpolator), and there's no randomness: very portable.
- Property tables are already JSON.
- Migration fixtures cover schemas 3/4/7/17.
- `compute()` takes 0.05-0.4 s, which is fine.
- Start transients, rotor critical speeds and CFD-class models are out of scope by Cory's fidelity bar.

## Roadmap
Each phase is its own branch and draft PR off `origin/main`, gets its own plan-mode round with a per-commit checklist (convention #3), and goes through `./verify_all.sh` before review.

### Phase 0: Unblock (small, do first)
- [ ] **0.1** Merge PR #27 and update local `main`. Retire the `refactor/design-inputs` branch; Phase 3 redoes it.
- [ ] **0.2** CI: a GitHub Action that runs `verify_all.sh` on push/PR. Add elapsed time per module to `verify_all.sh`.
- [ ] **0.3** Golden in two modes:
  - `--check` stays exact for refactors.
  - New `--check-tol`: per-key-path relative/absolute tolerances, numbers only, with checklist rows compared as codes rather than prose.
  - New `--report --gate`: fails when a *validated* metric leaves its cited band.
  - Deliberate physics changes then need a report diff, not a 2.4 MB re-snapshot.
- [ ] **0.4** Tag a Python release (`py-legacy-models`), then retire `regen_circuit_style`, `suction_model=legacy`, `pump_model=correlation` and `coolant_inlet_model=table`. Old files migrate with a load-time notice. Keep the `flat` jacket model and tap-off `legacy` (still needed for LOX/LH2).

### Phase 1: Trustworthy numbers (top priority)
Goal: real engines reproduce within about 5-10%, with gates that would have caught the bugs above.
- [ ] **1.1** Mass: size `shell_mass_kg` on local static pressure, using the same profile as the rendering, plus the min-gauge floor. Add RO/cited dry mass to every corpus engine and gate at about ×1.5. Fix the "LOWER BOUND" header wording.
- [ ] **1.2** Expander: make turbine power the enthalpy drop across the solved PR from the jacket-outlet state, and validate the ceiling against RL10A-3-3/RL10B-2 and Vinci-class engines.
- [ ] **1.3** Regen credit: either fold it into the `ETA_CF` fit or apply it before sizing ṁ, so the anchors re-close and thrust hits its target.
- [ ] **1.4** Gates: tighten vacuum Isp to about ±2.5%. Add sea-level Isp, mass, jacket dP and pump-discharge bands where a citation exists. Move SPOT_CHECKS anchors off the fitted engines (holdout set).
- [ ] **1.5** Default `regen_channel_model` to `"channels"` (migrate with a notice). Size LH2 passages on mass flux, aiming for RL10/J-2 jacket dP of about 1-2 MPa.
- [ ] **1.6** Nozzle losses: split into kinetic (frozen-vs-equilibrium column, Bray freeze point) and boundary-layer (Re^-0.2) parts, re-solving `ETA_CF` as the residual. Target: kerolox Isp within 2.5%.
- [ ] **1.7** Warning hygiene: add severity tiers (error/warn/info). The default design should pass clean, and corpus engines should show ≤2 warnings. Triage the false positives (TEA-TEB, stage count, the contradictory default rows). Add a corpus check on warning counts.
- [ ] **1.8** Convergence: add a `convergence` block to the result (iterations, residual, converged) for thrust closure, the coolant loop and the staged solvers, with a warn row when something doesn't converge.
- [ ] **1.9** Literature triage of the 13 new PDFs (lit-integrator, one per paper). Read the J-2 manual R-3825-1B, the J-2S study and quentmeyer1978 first: they likely give J-2 jacket dP, tap-off gas data, a dry-mass anchor and copper-liner fatigue data. The other NTRS reports get triaged against the open questions (nozzle-loss split, ox-rich preburner temperature, RP-1 flux, SECA channel geometry).
- [ ] **1.10** Thermal feasibility of real engines: add cited film fractions (RD-180) and an RP-1/CH4 throat-flux anchor so flown engines read as feasible. Source the ox-rich preburner temperature at high Pc.

### Phase 2: KSP export you can use
- [ ] **2.1** Drop template hosts from the catalog, refuse export to a missing/template host, and sanitize the config name everywhere it is used.
- [ ] **2.2** Add a ModuleManager-grammar linter in the `cfg_writer` self-test, plus a manual "loads in KSP" checklist per release (Cory runs it; it can't be tested here).
- [ ] **2.3** Stamp each export with tool version, schema, git hash and design hash. Always save the project JSON next to the cfg. Add "re-export all + diff".
- [ ] **2.4** Derive or expose fields:
  - Expose `ullage`; derive `techTransfer` from the host family.
  - Re-anchor tested/rated burn time to the RO distribution (median 3×).
  - Export the attached-flow sea-level Isp instead of 1.0.
  - RP-1 `@ENTRYCOSTMODS`.
  - Store the cost-overridden flag in the project.
- [ ] **2.5** Dogfood: add SUBCONFIG + multi-CONFIG export. Add H3-250K/H4-250K/TR341 as corpus targets that must reproduce the hand cfgs within X%. Re-save RS-29/RS-30/TRW-270 at the current schema.
- [ ] **2.6** A one-page `QUICKSTART.md`: install → New from RS-25 → change Pc → read the checklist → export → GameData → verify in the VAB.

### Phase 3: Port contract and field registry (enables tooltips, reduces per-round cost)
- [ ] **3.1** Redo the nesting refactor fresh on main as schema 21. Replace 0-means-auto with `None`/enums, add a typed `PlumbingRun`, and use ordered `migrate_N_to_N+1` functions keyed on `schema_version` that return warnings and never drop unknown keys silently. Move `project_io` to `physics/`.
- [ ] **3.2** **Field registry** (`physics/fields.py`): one entry per input with label, units, range/step, group, basic/advanced, tooltip, and "affects" (which outputs and stages it drives).
  - Tk builds its widgets and tooltips from it, which retires the hand-mirrored control/refresh pair.
  - Qt reads it via `dump_fields.py`.
  - The tooltip texts get written here once; that is Cory's tooltip request.
- [ ] **3.3** Result contract: add `result_to_json()` (native types, tagged inf/NaN), a generated JSON Schema (`dump_result_schema.py`), and checklist rows as `{code, severity, params}` with display text rendered separately.
- [ ] **3.4** Move cost/massMult/model scale out of `app.py` into `export/`. Put the flow network and resolved plumbing runs in `result`, so `mesh_builder` is geometry-only.
- [ ] **3.5** Make `PassState` a slotted dataclass, or per-stage output dataclasses. Add `physics/units.py` for the duplicated constants. Export the 78 literal tables to JSON.
- [ ] **3.6** Cut CLAUDE.md down to rules/conventions/pointers (≤150 lines); move round histories into `plans/` and the topic docs.
- [ ] **3.7** Per-stage fixtures (`dump_fixtures.py`) and corpus cases covering every remaining model switch: this is the C++ port oracle. Refresh the Qt migration plan's survey numbers.

### Phase 4: Turbopump workspace + turbine meanline (Cory's next interest)
- [ ] **4.1** **Turbopump Lab**: a separate Shape-Lab-style window built on `_ShapeLabBase` (`gui/shape_lab.py:88`). It takes over the left Turbopump input tab and its intent sliders, and hosts Detail, 3D and Section as views, all driven from the registry so Qt can mirror it.
- [ ] **4.2** Round 3: turbine meanline (velocity triangles, stage count, reaction, blade height, pitchline) plus blade/disk stress. Replace the correlation turbine η and close the known TURBOPUMP_FLOW quirks 1/2/5 (one sizing for both efficiency and the drawn machine; shared-shaft rpm cap on the expander path).
- [ ] **4.3** Customizability: let the user override pump/turbine geometry choices (stage count, impeller type, inducer, turbine type, shaft arrangement, gearbox), each with a computed consequence. Warn, don't block.
- [ ] **4.4** E3 casing walls by hoop stress. Then follow the roadmap's Round 4 geometry-derived mass, which retires `render_scale` and the envelope default.

### Phase 5: Depth, as wanted
In rough value order:
- [ ] Storables (vapor pressure, A-50 coolant data, a monoprop refresh).
- [ ] Throttling with pump-turbine matching and MR drift.
- [ ] GG/preburner/start hardware as plumbing hosts (E4).
- [ ] Qt-side UX: presets from the corpus, undo, unsaved-changes prompt, A/B compare, a general sensitivity sweep.

Explicitly out of scope: CFD-class flow, start transients beyond what TestFlight needs, rotor dynamics.

## Verification
- **Doc-only change:** check that the pointer paths in CLAUDE.md resolve, and that `./verify_all.sh` still passes (it should be unaffected).
- **Each later phase:** its own plan defines its checks. In general: `verify_all.sh` passes; `run_corpus --report --diff` is saved to `validation_engines/reports/`; the new gates (mass band, tighter Isp, warning count) pass. GUI items are syntax-checked only here and handed to Cory to click through. Export items get Cory's in-game load check.
