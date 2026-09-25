# Planned changes: turbine exhaust, round 2 (2026-09-25)

A saved copy of the approved plan, so a later session can pick the work up if this one runs out
of tokens. **Tick each box when its commit lands** (and put the commit hash beside it).
Branch: `claude/friendly-rubin-un6ueo`, restarted from `origin/main` at b97c4b0 after PR #10 merged.

## Status
- [ ] Commit 0: this document
- [ ] Commit 1: z-fighting fix (overboard exhaust nozzle vs duct pipe)
- [ ] Commit 2: F-1 injection back pressure + corpus F-1 fixes + [F1-Man] probes
- [ ] Commit 3: gas-film law from [TN-D3836] (modified Hatch-Papell)
- [ ] Commit 4: heat exchanger recalibration (F-1 can) + helium coil (schema 10) + GUI
- [ ] Docs: ASSUMPTIONS / README / CLAUDE.md / OPEN_QUESTIONS (spread across 2-4)

## Context
Round 1 (three exhaust modes; merged as PR #10) is done. Since then Cory has distilled a large
literature batch into `claude_lit/` on `main` (commit b97c4b0), including:
- `[F1-Man]` (R-3896-1);
- `[SP-8124]`;
- `[TN-D3836]`.

Checking the model against `[F1-Man]` shows several gaps.

| Quantity | Model F-1 today | Real F-1 `[F1-Man]` |
|---|---|---|
| Turbine pressure ratio | 22 (hits the cap) | 945 → 58 psia = **16.3** |
| Turbine exit pressure | 38.8 psia | **58 psia** |
| GG flow | 57.5 kg/s (2.19 % of total flow) | **75.7 kg/s (2.91 %)** |
| Turbine specific work | 501 kJ/kg | 508 kJ/kg ✓ |
| Exhaust / film temperature | 811 K | **888 K (1,138 °F)** |
| Duct bore | 26.6 in | ~24 in (heat-exchanger outlet end) ✓ |
| Heat-exchanger can | 66 in dia × 80 in long | **43 in × 58 in** |
| GOX outlet temperature | 300 K (fixed 400 kJ/kg) | **516 K (470 °F)** at 4 lb/s; plus **He 0.6 lb/s, 63 → 397 K** |
| Mixture ratio used by the corpus | 2.27 (the engine-overall ratio) | chamber **2.40** |

Two other problems:
- The injection-mode gas film borrows a liquid-film decay law with no cp term, which is optimistic.
  `[TN-D3836]` now gives a real gas-film correlation (modified Hatch-Papell).
- **Z-fighting:** the overboard exhaust nozzle draws an inlet "collar" cylinder, and its end
  disk, over the same stretch where the duct pipe starts. `plumbing.resolve_run` starts the
  pipe polyline at the hook centre. Coincident cylinders plus two disks ~2 mm apart flicker.

**Cory's decisions:**
- Do all four literature items and the z-fighting fix.
- Add the helium coil.
- The injection back-pressure anchor is an interim calibration. Record that the real per-engine
  physics (manifold + slot/eyelet pressure drop from geometry) is wanted later.
- **Write a planned-changes document into the repo before any code**, so it survives running out
  of tokens.

**Branch:** PR #10 is merged, so restart `claude/friendly-rubin-un6ueo` from `origin/main`
(`git checkout -B claude/friendly-rubin-un6ueo origin/main`). This picks up Cory's literature
batch and the RS-29.json edit. Force-push with lease is fine, since the branch holds only
merged history.

**Scale (CLAUDE.md token rule):** about 15 files, five commits, one corpus re-snapshot and one
Xvfb screenshot pass. Approving this plan is the y/n.

## Commit 0: planned-changes document (first, before any code)
- New `engine_designer/plans/2026-09-25_turbine_exhaust_round2.md` (create the directory). It holds:
  - this plan's content: the table above, each change with its constant name, anchor and
    expected numbers;
  - a checklist with a status box per commit, ticked as each commit lands.
- Commit and push immediately.
- CLAUDE.md gets a one-line pointer to `engine_designer/plans/`.

## Commit 1: z-fighting fix (small, independent)
- In `gui/mesh_builder.turbine_exhaust_termination_pieces` (overboard branch), pass
  `inlet_xyz = pos`. The collar then drops out through `exhaust_nozzle_mesh`'s existing
  zero-length-collar handling.
- Add a `with_inlet_cap=False` parameter to `gui/preview3d_gl_core/duct_meshes.exhaust_nozzle_mesh`,
  so the pipe's own root end disk closes the inlet.
  - The pipe root radius is the flow bore, which equals the nozzle's start radius: a seam, not an
    overlap.
- The Shape Lab gets the fix automatically through `shape_lab_geometry.exhaust_termination_fn`.
- Self-test in `mesh_builder`: every overboard nozzle vertex lies on the downstream side of the
  hook plane (dot with the nozzle direction ≥ −1e-9). No nozzle geometry may overlap the duct's
  first leg.
- Verify: an Xvfb screenshot before/after, zoomed on the joint. Also pixel-diff a closed-cycle
  design; it must be unchanged.

## Commit 2: F-1 back pressure + corpus fixes + probes (physics, one corpus re-snapshot)
1. **Injection back pressure:** add `EXHAUST_INJECTION_PRESSURE_RATIO` to
   `physics/turbine_exhaust.py`. It replaces `EXHAUST_DUCT_PRESSURE_RATIO` in
   `required_turbine_outlet_pa` for `nozzle_injection` only, via a `mode` argument.
   - Reverse-solve it so that the turbine exit / local main-nozzle static pressure at the
     injection station matches the real F-1: 58 psia against the eps-10 static pressure at the
     real 1,125 psia Pc. That is a ratio of about 3.8, so the constant is about 2.2. Pinning it
     as a ratio makes it independent of the corpus Pc.
   - Label it **Tier 2 interim**: a lumped manifold + shingle-slot loss.
   - Add an OPEN_QUESTIONS entry: replace this with per-engine physics. That means a torus loss
     plus a slot or eyelet dP computed from geometry, using the J-2 eyelet area (115 in²) and the
     F-1 23-row shingle slots. Add an ASSUMPTIONS row that says the same.
   - Keep `GG_PRESSURE_RATIO = 22` as the cap.
2. **Turbine inlet fraction:** set `GG_TURBINE_INLET_PC_FRACTION` to the mean of the two anchors,
   H-1 0.869 and F-1 945/1125 = 0.840, giving 0.855 (Tier 2, two anchors).
   - The H-1 check (a) must stay within tolerance: its exit pressure is set by the outlet side, so
     only the PR moves, from 17.7 to about 17.4.
3. **Corpus F-1** (`validation_engines/build_corpus.py`):
   - Set `mixture_ratio` to 2.40 [F1-Man Fig 1-7], noting that 2.27 is the engine-overall ratio.
   - Set the turbine-exhaust fields as needed, and update the notes/gaps: drop the "HX not
     modelled" line, since the HX gets set in Commit 4.
   - `run_corpus --report --diff` goes to `validation_engines/reports/2026-09-25_f1_manual_anchors_before_after.txt`,
     then run `--snapshot`.
4. **New `validate/turbine_exhaust_checks.py` rows** (the banner count stays 27):
   - (h) The F-1 in injection mode gives turbine PR 16.3 ±10 % and exit pressure within ±15 % of
     58 psia, scaled to the corpus Pc.
   - (i) F-1 plausibility, all [F1-Man]:
     - GG share of total flow within ×0.5–2 of 2.91 %. The model is low because pump power is low;
       note that and don't retune.
     - Exhaust temperature within ±15 % of 888 K.
     - Duct bore within ×0.7–1.4 of 24 in. This is the first check on `TURBINE_EXHAUST_DUCT_MACH`.
5. **Injection torus taper:** it becomes `taper_blend = 0.5`, per the F-1's "decreasing cross-section"
   [F1-Man §1-18] and the SP-8087 "between the two" convention.
6. **ASSUMPTIONS citation upgrade:** `manifold_bypass_fraction` 30 % now cites [F1-Man §1-16]; remove
   the "not yet applied" note.
7. Update the claude_lit topic 07 and topic 10 "Implications" bullets: record that the anchors are
   now applied in code.

## Commit 3: gas-film law from TN D-3836 (physics)
- New `turbine_exhaust.gas_film_effectiveness_profile(xs, rs, hg, inject_eps, mdot_c, cp_c,
  slot_h_m, v_g, alpha_c)`. It computes η(x) = exp[−(∫hg·2πr ds)/(ṁc·cp,c) · (S·Vg/αc)^(1/8)].
  - This is the working form with K = 0 and tangential injection [TN-D3836 p.8-9].
  - The integral runs from the injection station.
  - The profile returns φ = 1 − η, clipped to the film floor.
  - Past 100 slot heights it stays as-is: the source says the result is conservative there.
    Report the station where that happens.
- **Inputs**, built in `cooling_stage.py`, which replaces the current
  `nozzle_film_effectiveness_profile` call for the gas film:
  - hg from `cooling/gas_side.bartz_hg_profile`, the same calibrated h_g the thermal solve uses;
  - Vg from the isentropic Mach at each station;
  - ṁc, cp, T and slot height from the film carry. `exhaust_stream` now also returns the injection
    velocity and density: the exhaust expanded from `p_exit_total` to the local static pressure.
    The slot area is A = ṁ/(ρ·Vc) and S = A/(2π·r_inj);
  - αc = μ/(ρ·Pr), using `plumbing.EXHAUST_GAS_VISCOSITY_PA_S` and a Tier-3 Pr of 0.7.
- **Report** in `result["turbine_exhaust"]`:
  - slot height and area;
  - Vc/Vg, plus a warn-only row when it falls outside SP-8124's 0.9–1.15 flow-minimising band
    (advisory only);
  - η at the exit.
- **J-2 plausibility** (row (j)): the modelled injection slot area on the J-2 corpus is within
  ×0.5–2 of the real 115 in² eyelets [RPE-J2Blog].
- Check (b) keeps "wall with film < overboard". The film-carry key structure is unchanged.
- ASSUMPTIONS: the gas film moves from the borrowed Tier-3 liquid law to Tier 2 (a real
  correlation, extrapolated). Name the caveats: N₂ coolant, 60 psia, small motor, K = 0 is an
  empirical fit.
- The liquid films (chamber curtain / nozzle slot) are **unchanged**. SP-8124 App. B is
  graph-based, so leave an OPEN_QUESTIONS note.
- Corpus report and re-snapshot. Commits 2 and 3 can share one snapshot if run back to back;
  keep a separate report file for each.

## Commit 4: heat exchanger recalibration + helium coil (physics + GUI)
- `LOX_TO_GOX_DH_J_KG` is recomputed for 90 K liquid to **516 K** at pump-discharge pressure
  (supercritical), using CoolProp in a throwaway scratch venv script, expected ~6e5. Rename the
  anchor: Tier 2 outlet temperature [F1-Man Fig 3-29]; the property value is standard.
  - Add `HE_HX_DH_J_KG = 5193 × (397 − 63)` ≈ 1.73e6 (the F-1 He coil [F1-Man Fig 3-29]; ideal
    monatomic cp).
- New field `turbine_exhaust_hx_he_kgs` (default 0), with SCHEMA_VERSION 10:
  - The `project_io` migration and self-test assert that old files load as 0.
  - `exhaust_stream(hx_he_kgs=)`: duty and ΔT add both coils.
  - The helium coil is allowed for any pair (it's pressurant only); the LOX coil stays LOX-pair only.
- **Can sizing:** `HX_CAN_DIA_DUCT_MULT` becomes 1.62 and `HX_CAN_LENGTH_DUCT_MULT` becomes 2.18,
  reverse-solved so the corpus F-1 duct (26.6 in) gives the real 43 in × 58 in.
  - The real can tapers 40 → 24 in. Draw it as a cone: inlet 1.5× the duct bore, outlet 0.9×,
    with `preview3d_gl_core` ray/cone meshes, still clear of the pipe.
  - `HX_MASS_SHELL_MULT` stays Tier 3; no weight is published.
  - Be honest that duty does not size the can: there is one dimensioned anchor and no
    heat-transfer sizing, so this stays an ASSUMPTIONS note.
- **Corpus F-1:** GOX 1.81 kg/s and He 0.27 kg/s (4 and 0.6 lb/s). The heat-exchanger ΔT is
  expected to be ~10 K. Probe (i) then compares the post-HX temperature with 888 K.
- **GUI:**
  - `gui/app.py`: a helium-flow slider next to the GOX slider in the "Turbine Exhaust" section,
    with sync/load bindings, following the GOX pattern.
  - `gui/turbopump_diagram.py`: the HX box label lists both coils.
  - `export/cfg_writer.py`: the note lists the helium flow.
- Self-test (4) is extended: the helium coil lowers T, and a non-LOX pair still gets the helium duty.

## Docs (spread across commits 2–4)
- ASSUMPTIONS rows for each new or changed constant.
- README exhaust paragraph.
- CLAUDE.md: the `turbine_exhaust.py` layout sentence (gas film = TN-D3836; HX = F-1-anchored + He
  coil) and the plans pointer.
- OPEN_QUESTIONS:
  - per-engine injection dP physics (**Cory's ask**);
  - F-1 pump power under-predicted (GG flow 24 % low; a turbopump-calibration item, not this round);
  - SP-8124 liquid-film curves.
- Tick the plan document's checklist in each commit.

## Verification
- `./verify_all.sh`: ALL MODULES PASSED after every commit; `validate | grep -c '^ALL'` = 27.
- The `physics.turbine_exhaust` self-test covers the gas-film profile (monotone decay; stronger
  with more flow or cp), both HX coils, and the injection pressure ratio.
- Corpus: save `--report --diff` for each physics commit and summarise the shifts for Cory.
  Expected: F-1 PR 22 → ~16–17, GG flow up ~6 %, Isp down a few tenths of a second (still inside
  its band); the J-2 moves similarly. Overboard/aspirator designs (RS-29 family, Merlin, RS-68)
  are unaffected except by the inlet-fraction change (small). Then `--snapshot`.
- `project_io` v9 → v10 round-trip; `cfg_writer` brace/token checks.
- Xvfb: screenshot the overboard joint (z-fight gone), the tapered HX can, and the injection mode.
  Pixel-diff a closed cycle to show no change. `app.py` and `shape_lab.py` are syntax/import only;
  **Cory clicks through** the new helium slider and the overboard view.
- Push after each commit to `claude/friendly-rubin-un6ueo`. No PR unless asked.

## Answer to Cory's question 2 (HX size today, to relay)
The can is sized from the duct bore alone:
- duct bore = √(4ṁ / (π·ρ·V)), with V = Mach 0.25 × the sonic speed at the turbine-exit state,
  ρ = p/(R·T), and R = cp(γ−1)/γ;
- can diameter = 2.5 × bore; can length = 3 × bore;
- wall = the hoop-stress thickness at turbine-outlet pressure, with a 1 mm floor;
- mass = 2 × (side + ½ end area) × wall × Haynes 230 density.

The GOX duty (ṁ_GOX × 400 kJ/kg) only lowers the exhaust temperature. It does not change the size.
All of these multipliers were Tier-3 guesses, which is why the F-1 came out 66 × 80 in against
the real 43 × 58 in.
