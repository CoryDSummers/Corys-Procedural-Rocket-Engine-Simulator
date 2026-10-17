# TestFlight export: realistic burn time and reliability (approved 2026-10-16)

(The export / RP-1 identity round in this file earlier is finished: PR #29. This plan replaces it.)

## Context

Cory asked how the exported TestFlight numbers are calculated. Tracing it showed:

- `ratedBurnTime` is a flat 200 s × (thermal margin ÷ 1.15), clamped to 0.3–3×. For an ablative chamber it equals the user's target. It has no link to engine role, size, or any mechanism that actually limits life.
- `testedBurnTime` is rated × a controller-tier multiplier (6/10/14/17), clamped to 3–30×. Those anchors are *total* qualification time (Merlin 1970 s, Vulcain 2 10,000 s). In RO's `TestFlight_Generic_Engines.cfg`, though, tested is where the **single-burn** failure curve reaches 2× (and 100× at 2.5 × tested). Across 477 real RO TESTFLIGHT blocks, tested/rated has a median of **3.0** (10th percentile 1.5, 90th 9.6), so our exports are far too forgiving of overburn.
- Reliability: each tier's failure gap × cycle difficulty × design risk factors (Tier 3). TestFlight's per-second failure rate is (1 − cycleRel) ÷ rated, so cycleRel means the chance of surviving one rated burn.
- `techTransfer` is never written. RO format: `techTransfer = A,B:50&C:25`.
- **Correction:** `clusterMultiplier` is for one part that *represents N separate engines* (LMDE comment, RO_SuggestedMods). Multi-chamber engines such as RD-107 don't use it. So the per-chamber risk term stays, and clusterMultiplier is **not** written.

Cory wants a realistic, engine-performance view: rated burn time should come from the physics, and changing the design should be able to raise it.

## Core idea (as in real engines)

- **Rated** = the mission duty the engine is qualified for. This is a design target, as ablatives already have, with a default fitted from RO by role and size. It is **capped** by the shortest physical life limit ÷ a life factor.
- **Tested** = how far that life limit goes beyond rated: the single-burn duration the hardware could demonstrate. It is bounded by an RO-corpus-fitted band.
- **Reliability** is cut when rated runs close to the life limit (thin margin).
- The GUI gets a **"Burn-time limits"** table: each mechanism, its allowable time, which one limits the design, and the design lever that relieves it. This is warn-only: if the target exceeds the limit, the rating is capped and a warning is shown.

**Decided (Cory):** rated = duty target capped by physics life. Sequence: distill only the two PDFs added today → update this plan with what they give → begin Round A.

## Step 0 — distill the two PDFs added 2026-10-16 (scale: about 76 pages total)

- `literature/NASA CR-134806.pdf` (1.1 MB, about 54 pages). This is Esposito & Zabora's liner-alloy creep and low-cycle-fatigue properties.
- `literature/19770024295.pdf` (3.1 MB, about 22 pages). The NTRS accession number suggests the 1977 Quentmeyer thrust-chamber fatigue-life report; confirm from the text.
- Method follows `claude_lit/PROVENANCE.md`: extract the text with the existing `v/` pymupdf venv into `$CLAUDE_JOB_DIR/tmp` and read it a section at a time. Rename the numeric file to `<Report ID> - <Title>.pdf`.
- For each source: write a `sources/<slug>.md` note, fold findings into `topics/materials*.md` and `topics/cooling*.md` with `[Tag p.NN]` cites, and update the README citation table and topic index, the PROVENANCE batch entry and OPEN_QUESTIONS.
- Then edit Round B's table in this plan (which mechanisms now have data) before starting Round A.

## Round A — corpus fits + plumbing (no new literature needed)

Branch: `testflight/burn-time`, stacked on `propellants/mon-variants`. Draft PR.

- **A1 `catalog/build_testflight_corpus.py` → `testflight_corpus.json`.** For each RO CONFIG that has a TESTFLIGHT block: rated, tested, the four reliabilities, ignitions, techTransfer, maxThrust, propellants, pressureFed. Joined to `rp1_snapshot.json` for tech-node year and the Turbo/PF tag. Reuses `catalog/mmcfg.py`. Add it to `verify_all.sh` with a self-test (F-1 165/2250, H-1 155, RL10 rows present).
- **A2 Tested/rated fit.** Medians by group (pump vs. pressure-fed, booster vs. upper stage, restartable, era) replace `tested_to_rated_multiplier` as the base. Controller tiers become a ± nudge inside the corpus band. Report the scatter honestly.
- **A3 Rated-duty default.** New field `rated_burn_time_target_s`, where 0 = the corpus-fitted default for this role and thrust. Role is inferred from expansion ratio, altitude/sea-level Isp, and ignitions. It is merged with `ablative_target_burn_time_s` so there is one target for every cooling type, with a schema bump and migration. In Round A the life cap is today's thermal-margin proxy, written as a single "chamber thermal" limit row.
- **A4 Reliability anchors.** Compare `BASE_BY_CYCLE` and tier values with the corpus's cycleReliabilityEnd by cycle and era. Re-fit only where the data clearly back it, and record that in ASSUMPTIONS.
- **A5 `techTransfer`.** Write it from `rp1_ecm_parents` with a new `testflight_transfer_pct` (default 50, the most common RO value). Sanitize it the same way as the ECM parents.
- **A6 GUI.** Rated-target spinbox, the limits table (one row for now), and the tested/rated readout showing where it sits in the corpus band. Syntax- and import-check only; there is no display here.

## Round B — physics life limits (needs literature, see search list)

Each mechanism → allowable single-burn time (s) and the design lever:

| Mechanism | Physics | Lever(s) | Literature status |
|---|---|---|---|
| Chamber liner creep / stress-rupture | Robinson life fraction 4·t/t_r at the solved wall temperature and hoop stress `[ASR72-238]` | material, coolant velocity, film, TBC, Pc | Ni/Fe: have `[ASR72-238]`. **Copper: still need it.** CR-134806 turned out to have no creep data; the wanted refs are in OPEN_QUESTIONS |
| Liner cycle life (caps ignitions) | `[Quentmeyer-TMX73665]` T_gw–N_f, ignitions ≤ N_f/4 | wall temperature (material, cooling) | **have** (distilled 2026-10-16, topics/17) |
| RP-1 coking build-up | deposit rate(T_wall) → added resistance → time to reach the wall limit | coolant velocity, wall temperature, Ni plating | have `[hydrocarbon-fuel-deposits]` |
| Turbine blade stress-rupture | Larson–Miller at turbine inlet temperature, blade centrifugal stress | GG/preburner Tin, blade alloy, tip speed | have SP-8110 limits; **need** LMP curves |
| Bearing life | L10 from DN, load, speed | rpm, bearing material | have SP-8048; **need** a life equation (Zaretsky) |
| Seal wear | SP-8121 3-hour wear-life curves | seal type, rpm | have SP-8121 |
| Radiative coating oxidation | coating life(T) | material, film | **need** silicide / Ir-Re life data |
| Ablative char | existing | target / material | done |
| Low-cycle fatigue | existing throat fatigue | caps `ignitions`, not time | done |

Each mechanism gets a validate row anchored on a real engine (F-1 / H-1 / RL10 / SSME ratings and life figures from the manuals already in claude_lit). The life factor is cited (SP-8110: ≥4 on cycles).

## Critical files

- `physics/reliability.py`, `physics/controller_tech.py` (tier nudges)
- `physics/design/rollup_stage.py` (rated cap), `physics/design/engine.py` (fields, schema)
- `export/cfg_writer.py` (TESTFLIGHT block, techTransfer)
- `catalog/build_testflight_corpus.py` (new), `catalog/mmcfg.py` (reuse)
- `gui/app.py` (target and limits table)
- ASSUMPTIONS.md / README / CLAUDE.md

## Verification

- `./verify_all.sh`: all PASS. The new corpus module self-test runs. In `reliability.py`, the self-test checks that tested/rated falls within the corpus 10–90 % band for representative designs and that rated ≤ the life cap.
- `run_corpus.py --check`: rated burn time is a compute() output, so expect deliberate movement. Save `--report --diff` and re-snapshot.
- Export F-1-like, H-1-like and RL10-like designs, then compare rated and tested with the real RO rows.
- Cory: click through the GUI, then in game check the TestFlight failure curve (tested burn time appears in the RF picker description).

## Implementation notes (what changed vs. the plan while building)

- **Wall-life anchor is calibrated, not "margin 1.0".** In the tool's own thermal model, 3 of
  the 10 regen/radiative corpus engines (RD-180 0.71, Raptor-2 0.81, Rutherford 0.72) run below
  margin 1.0 at their real duty. So `THERMAL_LIFE_MARGIN_REF` = 0.69 was reverse-solved so that
  all of them carry their real RO ratedBurnTime uncapped (`validate/burn_time_checks.py`).
- The life anchor uses the corpus duty (`duty_default_s`), NOT the user's target, so raising the
  target cannot raise the life.
- **A4 found the old cycle multipliers double-counted.** RO's ORSC and FRSC failure gaps are
  both ~1.43-1.5x same-era pump-fed engines. That equals the existing Pc term at the staged
  median of 16 MPa × 1.13. OX_RICH_EXTRA is retired. Pressure-fed 0.66 and expander 0.70 are
  fitted.
- **The reliability-cut item was dropped.** By construction rated ≤ life / 4, so the headroom
  is never below the life factor. The existing fatigue risk term already uses ×4 (now cited).
- **clusterMultiplier is not written.** RO uses it only for N separate engines on one part.
- **techTransfer** uses raw parent config names (RO writes `F-1-1.5M`). Only the ECM key is
  RealFuels-sanitized.
- **Corpus engines** carry their real RO duty and RP-1 node as inputs, plus a plausibility
  metric.
- **Schema 22 migration.** The old 200 s default (including files older than the field) is kept
  only for ablative designs. A user-changed value is kept. Otherwise 0 = auto.

## Checklist

- [x] Step 0: distill NASA TM X-73665 + CR-134806 (ee0af5b, topics/17, OPEN_QUESTIONS gap: Cu creep)
- [x] A1 `catalog/build_testflight_corpus.py` + rp1_snapshot node years
- [x] A2 tested/rated fit (`burn_time.TESTED_FIT_*`), tier -> `era_year`
- [x] A3 duty target + wall-life cap (`burn_time.py`, rollup_stage, schema 22), validate banner 33
- [x] A4 reliability cycle factors fitted (`reliability.refit_cycle_gaps`)
- [x] A5 techTransfer export (`testflight_transfer_pct`)
- [x] Corpus engines get real duty; report `validation_engines/reports/2026-10-16_testflight_burn_time.txt`, golden re-snapshotted
- [x] A6 GUI: Cooling > "Burn Time (duty & life)" slider + limits table, transfer-% field, load notice (syntax/import only - no display here)
- [x] Docs: README, ASSUMPTIONS, CLAUDE.md
- [ ] Cory: GUI click-through + in-game TestFlight check
- [ ] Round B (needs the literature in OPEN_QUESTIONS)
