# MON-3 / MON-10 / MON-25 variants of N2O4/MMH

## Context
Cory asked about MMH/NTO. It already exists as "N2O4/MMH" (exports `MMH` + `NTO`, anchored on Aestus). But most real RO MMH engines burn **MON**, which is NTO with a few % nitric oxide dissolved in it:
- **MON-3/MMH** (10 configs): Aestus, AJ10-190 (Shuttle OMS), AJ10 Transtar, R-4D-11, R-40, R-42, LEROS-4, RS-88, XLR-132, XLR-81.
- **MON-10/MMH**: TD-339 (Surveyor vernier).
- **MON-25**: no RO engine burns it, but RF defines the resource (low-freezing, -55 °C).

Today those engines can only be designed and exported as N2O4/MMH, so they get the wrong RF resource. Cory chose "Add MON variants".

This round uses the variant mechanism from the previous round (`physics/propellant_pairs.py`): same combustion, injector and turbine physics as the base pair, plus its own equilibrium table, oxidizer density and RF resource.

**Branch**: `propellants/mon-variants`, STACKED on `propellants/new-pairs` (PR #30), which it needs for `propellant_pairs.py` and the generator's `--merge-pairs`. The draft PR is based on that branch. Merge order: #29 → #30 → this one. There is no new `EngineDesign` field, so no schema bump. A plan copy goes in `engine_designer/plans/2026-10-16_mon_variants.md` with a checklist.

## Design decisions
- **Pair keys**: `"MON-3/MMH"`, `"MON-10/MMH"`, `"MON-25/MMH"`. All three go in `PAIR_VARIANT_OF` → `"N2O4/MMH"`, so `available_pairs()` lists them right after N2O4/MMH, and every per-pair dict without an explicit entry aliases to it. That covers ETA_CF, L*, L_MID, beta band, ignition (hypergolic), Bartz, cost class, GG/preburner gas, the coolant (still MMH) and the inlet temps.
- **Chemistry** (generator): a new reactant `NO(L)` with N=1, O=1. Its assigned enthalpy is ΔHf°(NO, g, 298 K) = +90,291 J/mol [NIST-JANAF] minus ΔHvap(NO) ≈ 13.8 kJ/mol at its 121.4 K boiling point [NIST Webbook], which gives about +76.5 kJ/mol. The heat of solution of NO in N2O4 (really N2O3 formation) is neglected. ASSUMPTIONS records this as a Tier-2 estimate.
  - Oxidizer blends are mass fractions: MON-x = `{"N2O4(L)": 1-x/100, "NO(L)": x/100}`.
  - MR grid = N2O4/MMH's (1.2–3.0).
  - A sensitivity run with NO at its gas-phase enthalpy instead is recorded in the generator meta / OPEN_QUESTIONS, expected to shift Isp by less than about 0.3 s for MON-3. That bounds the error from the neglected heat-of-solution term.
- **Densities** (`combustion.PROPELLANT_DENSITIES`): the fuel keeps MMH's 880. The oxidizer is N2O4/MMH's physics density (1440) × RF's MON-x/NTO density ratio from `RO_Resources.cfg` (MON3 1436.3, MON10 1444.1, MON25 1455.4 vs NTO). This is the same "scale the base by a cited ratio" method the subcooled density used.
- **η**: inherited from N2O4/MMH, not re-tuned. The Aestus anchor (η_CF 0.9088) stays on N2O4/MMH, so the existing corpus stays bit-identical. The MON spot checks then show whether the chemistry change alone reproduces the MON engines.

## Changes (one commit plus a docs commit)
1. **Generator** `tools/property_tables/generate_property_tables.py`:
   - Add `NO(L)` to `REACTANTS`, with a cite comment.
   - Add three `PAIRS` entries.
   - No `COOLANTS` entry, since MMH isn't in CoolProp; it uses the same fallback as base N2O4/MMH.
   - Run `--merge-pairs "MON-3/MMH,MON-10/MMH,MON-25/MMH"` in the pinned venv (`$CLAUDE_JOB_DIR/tmp/ctv`, recreate if gone: cantera==3.2.0, CoolProp==8.0.0). The Sutton self-check must pass, and a JSON diff must show old keys byte-identical.
2. **`physics/propellant_pairs.py`**: three `PAIR_VARIANT_OF` entries, and extend the self-test.
3. **`physics/combustion.py`**: `PROPELLANT_DENSITIES` entries (the rest aliases), plus a docstring line.
4. **`cooling/coolant_props.py`**: no density entry needed, since the coolant is the fuel (MMH), and MMH is unchanged → alias. Confirm `design/suction_stage.PUMPED_PROPELLANTS` aliases correctly (storables take the no-saturation path).
5. **Export** `export/cfg_writer.py`:
   - `_RF_PROPELLANTS`: MMH / MON3, MON10, MON25.
   - `RF_RESOURCE_DENSITY_KG_M3`: add MON3/10/25, cited from RO_Resources.cfg.
   - Add the variants to `_RF_DENSITY_PAIRS`.
   - Self-test: render all three, and reproduce one real config's volume ratio (Aestus or AJ10-190 PROPELLANT ratios in `Engine_Configs/`).
6. **Validation** `physics/validate/performance.py` `SPOT_CHECKS`, all with inherited η:
   - AJ10-190 MON-3: 0.86 MPa, eps 55, MR 1.65, 316 s vac. Gated cross-check.
   - TD-339 MON-10: 1.72 MPa, eps 85, MR 1.5, 287 s vac. Gated cross-check.
   - Aestus re-run as MON-3, `gated=False` (reported only). It shows the MON-3 vs N2O4 shift on the anchor itself.
   - Any miss is reported honestly. If AJ10-190 or TD-339 falls outside tolerance, it goes to `gated=False` with a note rather than re-tuning η.
   - `thermo_tables.py` self-test: MON-x Tc/Isp vary monotonically with NO fraction, and each sits within a few seconds of N2O4/MMH.
   - The cooling-robustness sweep adds MON-3/MMH.
7. **Docs**:
   - ASSUMPTIONS: Tier-2 rows for the NO(L) enthalpy, the MON densities, inherited η, and MON-25 un-anchored.
   - README pair list ("thirteen" pairs).
   - CLAUDE.md: the validate engine list, the robustness count and the in-flight paragraph.
   - OPEN_QUESTIONS: the NO heat-of-solution term, and a possible MON-1 variant for Aerozine-50 (LMDE / AJ10-137, not in scope).
   - Update the memory file.

GUI: no code change (dropdown, MR range and igniter all come from the registry). `app.py` gets a syntax check only, and Cory clicks through it.

## Expected results (sanity, not targets)
- MON-3 Isp is about +0.5–1 s over N2O4 at the same MR, and Tc slightly higher (NO adds energy).
- MON-25 gains a few s.
- Volume ratios shift slightly from the denser oxidizer.

## Verification
- `./verify_all.sh`: all PASS. `python3 -m engine_designer.physics.validate | grep -c '^ALL'` = 32, and the new rows print.
- `python3 -m engine_designer.validation_engines.run_corpus --check`: bit-identical (N2O4/MMH untouched).
- The JSON diff shows old pair keys byte-identical.
- A throwaway smoke test: `EngineDesign(pair="MON-x/MMH")` pressure-fed and GG, `.compute()` finite, then all 3 cfg export modes render.
- Cory runs the GUI: the MON entries appear under N2O4/MMH, the igniter is hypergolic, and the export shows `MON3`.

## Checklist / outcome (2026-10-16)
- [x] Generator: `NO(L)` reactant + 3 `PAIRS`, `--merge-pairs` run (Sutton gate OK, 8 old pairs byte-identical).
      Deviation: NO enthalpy via N2O3(l) (60.1 kJ/mol) instead of NO(g) - dHvap (76.5) - better physics; both bounds recorded.
- [x] `propellant_pairs` variants + self-test; `combustion` densities; export resources + RF densities (AJ10-190/Aestus/TD-339 ratios reproduced).
- [x] Aliases added to the per-pair dicts the subcooled round had filled explicitly (coolant density, jacket velocity,
      Bartz calibration, coolant/oxidizer inlet temps); suction tank names; plumbing ox viscosity via `base_pair`.
- [x] Spot checks: AJ10-190 -6.3 %, R-40 +1.5 %, TD-339 +3.2 %, Aestus-as-MON-3 -0.2 % - all REPORTED (`gated=False`):
      identical on plain N2O4/MMH, so the spread is the one Aestus ETA_CF, not MON chemistry (OPEN_QUESTIONS).
- [x] thermo_tables self-test #11; robustness sweep 361 combos, 0 bad.
- [x] verify_all PASS, validate 32 banners, corpus bit-identical.
- [x] Docs: ASSUMPTIONS, README, OPEN_QUESTIONS, CLAUDE.md, memory.
- [ ] Cory: GUI click-through (MON entries under N2O4/MMH, hypergolic igniter, export shows MON3).
