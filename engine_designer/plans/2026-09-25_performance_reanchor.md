# Planned changes: P1 performance re-anchor (2026-09-25)

A committed copy of the approved plan so a later session can resume it. **Tick each box when
its commit lands** (with the commit hash).
Branch: `claude/friendly-rubin-un6ueo`, continuing after turbine-exhaust round 2 (e204a1b).

## Status
- [x] Commit 0: this document (405ac42)
- [x] Commit 1: regenerate equilibrium tables (wider eps grid + frozen Isp column); heat-transfer path unchanged - corpus bit-identical
- [ ] Commit 2: performance path on the tables (performance_state, ETA_CF split, re-solved calibrations, corpus report)
- [ ] Commit 3: docs (ASSUMPTIONS, COOLING_AUDIT P1, CLAUDE.md, README, OPEN_QUESTIONS option-C literature)

## Context
`combustion._TABLES` is the source of every Isp in `engine_designer`. It holds one Tc/γ/M row
per mixture ratio, with no chamber-pressure axis. For LOX/LH2 the γ and M values are "effective"
fits, not physical ones (`COOLING_AUDIT.md` open item P1). Everything sits on one fudge factor
per pair, and that shows up as known misses:
- RS-25 vacuum Isp 426 vs 455 s;
- RD-180 319 vs 338 s;
- Merlin 296 vs 311 s;
- Rutherford 303 vs 317 s;
- RL10 454 vs 442 s.

The baked Cantera equilibrium tables (`physics/property_data/combustion_equilibrium.json`)
already carry the following on a (Pc, MR) grid, but the performance path never reads them:
- shifting-equilibrium c\*;
- Isp at area ratios 10, 40 and 100;
- M and γ.

**Cory's decisions (2026-09-25):**
- **Loss model "A now, C-ready":** one fitted efficiency per pair for now, reported per engine.
  The regenerated tables also carry a frozen-chemistry Isp, so a kinetics/boundary-layer split
  (option C) can come later without regenerating again.
- **Regenerate the tables** with a wider range of area ratios.
- **List the literature** option C would need (see the last section).

**Scale (CLAUDE.md token rule):**
- about 15 files and 4 commits;
- a one-off Cantera run (needs a pip install, possibly a Python download);
- every Isp spot check and corpus golden moves, with a report per commit;
- 3 of the existing calibrations need re-solving.

Approving this plan is the y/n.

## Commit 0: planned-changes document
Write `engine_designer/plans/2026-09-25_performance_reanchor.md`: this plan, plus a per-commit
checklist. Commit and push it before any code. Same convention as round 2.

## Commit 1: regenerate the tables (heat-transfer path unchanged)
- **Install Cantera.** This machine only has Python 3.14, and Cantera may not publish a wheel
  for it.
  - First try a scratch venv with `pip install cantera coolprop`.
  - Otherwise `pip install uv`, then `uv python install 3.12` and build a 3.12 venv.
  - Last resort: Cory runs the script on Colab.
- **`tools/property_tables/generate_property_tables.py`:**
  - `EPS_GRID` becomes `[2, 3, 4, 6, 8, 10, 16, 25, 40, 60, 100, 150, 250]`.
  - Add a **frozen-expansion** Isp column, `isp_vac_frozen_s_by_eps`: composition fixed at the
    chamber value, isentropic expansion to the same area ratio. It's the lower bound, kept for
    option C.
  - Record Cantera's version in `meta`.
  - The Sutton Table 5-5 gate must still pass.
- **`physics/thermo_tables.py`:**
  - Load the new keys.
  - New `isp_vac_ideal_s(pair, mr, pc, eps, frozen=False)`: bilinear in (ln Pc, MR), then
    monotone interpolation in ln ε, clamped to 2–250 with a checklist row when outside.
  - Self-test:
    - frozen Isp ≤ shifting Isp;
    - Isp rises with area ratio;
    - the 10/40/100 values match the previous tables.
  - `gas_state` stays unchanged, so the heat-transfer path should keep the corpus check
    bit-identical. If a Cantera version change nudges values, report the diff.

## Commit 2: switch the performance path (the physics change)
- **New `combustion.performance_state(pair, mr, pc)`** for the 5 bipropellant pairs. It returns:
  - Tc, M and γ_s from the table (γ_s is the shifting isentropic exponent, used for area/pressure
    profiles);
  - `cstar_ideal`;
  - a callable for ideal vacuum CF(ε) = Isp_vac·g0 / c\*.

  Hydrazine and H2O2 keep the legacy `_TABLES` path; there are no equilibrium tables for them.
- **`design/combustion_stage.py`:**
  - `s.tc`, `s.gamma` and `s.m_molar` come from `performance_state`.
  - c\* = `cstar_ideal` × the existing efficiency chain (injector multiplier, completeness,
    staged penalty, film, baffles).
  - CF_vac = ideal CF(ε) × `lam_relative` × **`ETA_CF[pair]`**, a new per-pair fitted nozzle
    efficiency. It holds kinetics, boundary layer and anything else not modelled; option C
    would later replace it with separate terms.
  - CF_SL = CF_vac − ε·Pa/Pc, same form as now.
  - Pe/Pc still comes from ε with γ_s, for separation and the injection static pressure.
- **Efficiency split:**
  - `DEFAULT_ETA_CSTAR` becomes a real combustion efficiency: ~0.975–0.99 per pair, from
    `topics/03` (Huzel §4.2 ~0.975), cited.
  - `ETA_CF[pair]` is reverse-solved so each pair's existing `SPOT_CHECKS` anchor hits its
    real Isp:
    - LOX/RP-1: RD-111;
    - LOX/LH2: RL10A-3-3;
    - LOX/CH4: Raptor-2;
    - N2O4/MMH: Aestus;
    - A-50: AJ10-137.
  - Why split: pushing the whole Isp loss into c\* would oversize the throat and throw off the
    heat flux.
- **`validate/performance.py`:** `_predict` routes through `performance_state`; the tolerances
  stay unchanged.
  - New report-only table: for every corpus engine, model vs real Isp and the implied
    efficiency. That puts option A's residuals on record.
  - Rule: report any engine outside tolerance. Don't tune it.
- **Calibrations that must be re-solved (they are defined as reverse-solves):**
  - `BARTZ_ABS_FLUX_CALIBRATION["LOX/LH2"]` (0.66), against SSME's 118 MW/m². LOX/RP-1 is
    re-checked the same way.
  - `CHANNEL_DP_CALIBRATION` (0.93).
  - The `gas_centered_swirl` injector multiplier, which is defined as a ratio to the RP-1
    `DEFAULT_ETA_CSTAR`.
  - Review `ETA_CSTAR_CEILING` 0.99, which today blocks RD-180.
- **Watch, don't tune:**
  - GG-bleed checks (F-1 / RD-0110 / J-2);
  - Raptor 340–360 and BE-4 335–350 cycle bands;
  - tap-off drive gas (it now uses equilibrium γ/M);
  - acoustic modes;
  - turbine-exhaust checks (b), (d) and (i).
- **Corpus:** save `--report --diff` to
  `validation_engines/reports/2026-09-2x_performance_reanchor_before_after.txt`, A/B'd against a
  `git worktree` of the previous HEAD in the same environment. It includes a before/after
  real-Isp residual table for every corpus engine and Cory's designs. Then `--snapshot`.

## Commit 3: docs
- `ASSUMPTIONS.md`: rewrite the Tier-1 `_TABLES` row, split `DEFAULT_ETA_CSTAR` from the new
  `ETA_CF`, and update the re-solved calibration rows.
- `COOLING_AUDIT.md` P1: closed, with the before/after numbers.
- `CLAUDE.md`: change "performance path deliberately unchanged" to the new path, and add the
  generator's new columns.
- README.
- `OPEN_QUESTIONS`: the option-C literature list below.
- Tick the plan-document checklist.

## Verification
- `./verify_all.sh` all PASS after each commit, and `validate | grep -c '^ALL'` stays at 27.
- Commit 1: generator Sutton gate PASSED; `thermo_tables` self-test; corpus bit-identical (or a
  reported Cantera-version diff).
- Commit 2:
  - all 7 `SPOT_CHECKS` within 5 %, and the integration checks within 2 %;
  - expected: RS-25 → ~445 s, RD-180 → ~328 s, with each anchor exact;
  - every other move reported per engine;
  - `physics.combustion` / `isentropic` self-tests.
- The GUI only shows new numbers. `app.py` gets a syntax check; Cory eyeballs his designs' new
  Isp.

## Literature for option C (Cory to look for; not needed for this round)
Already in hand: `[STBE]` has one fully itemized LOX/RP-1 loss stack (ideal 345.4 → 322.1 s via
ERE/KIN/TDK/BLM), and `[Sutton §3.5]` gives typical loss magnitudes. Wanted, in priority order:
1. **JANNAF Rocket Engine Performance Prediction and Evaluation Manual**, CPIA Publication 246
   (1975). The standard ERE / ODK / TDK / BLM loss methodology, and the core source.
2. **TDK/ODK documentation**: Nickerson, Coats et al., *Two-Dimensional Kinetics (TDK)
   Nozzle Performance Computer Program* (NASA-funded SEA Inc. reports, NTRS). Gives kinetic
   losses vs Pc and throat size.
3. **Bray, K.N.C. (1959)**, "Atomic recombination in a hypersonic wind-tunnel nozzle", *J.
   Fluid Mech.* 6. The sudden-freezing criterion, a cheap stand-in for kinetics.
4. **Boundary-layer thrust loss**: the JANNAF BLM / NASA "TBL" or BLIMP-J program documentation
   (NTRS), or any NASA TN correlating BL thrust decrement with throat Reynolds number and
   area ratio.
5. **Measured per-engine loss breakdowns** (ERE / kinetic / BL / divergence) for RS-25 (SSME),
   RL10, J-2 and an RP-1 booster. These are the anchors that would tell B and C apart from A.
