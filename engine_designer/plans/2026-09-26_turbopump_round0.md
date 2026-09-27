# Planned changes: turbopump fidelity Round 0 (2026-09-26)

A committed copy of the approved plan so a later session can resume it. **Tick each box when
its commit lands** (with the commit hash). This is Round 0 of
`plans/2026-09-25_turbopump_fidelity_roadmap.md`.
Branch: `turbopump/round-0`, cut from `origin/main` @ 0f65442; draft PR to `main`, not merged
until Cory has tested it.

## Status
- [x] C0: this document + draft PR
- [x] C1: literature (SP-8052 / SP-8110 / SP-8125 / SP-8121 / SP-8101 downloaded + distilled + integrated; H-1 pump discharge pressures from [H1-Man Fig 1-44]) (feee118)
- [x] C2: saturation-property table (`saturation_properties.json` + `thermo_tables.saturation`) (b735058)
- [x] C3: F-1 feed-system + pump/turbine calibration (corpus-wide shift + report) (9d0cb17)
- [x] C4: docs (ASSUMPTIONS, OPEN_QUESTIONS, CLAUDE.md, README, roadmap tick). ROUND COMPLETE.

**Where C3 deviated from the plan below, and why:**
- **No injector ox/fuel dP split.** Only the F-1 documents one. The per-leg feed-loss fit
  already absorbs the ox/fuel asymmetry, and both engines land within 10 % without it.
- **Staging rule.** It is keyed on the ACHIEVABLE U/C0 [SP-8110 §3.1.4], not on "high PR →
  velocity-compounded". [H1-Man Fig 1-44] showed the H-1 is pressure-compounded at PR 17.7,
  because it is geared.
- **Two extra constants moved, both cited:**
  - LOX/RP-1 GG gas cp 2100 → 2735 [SP-8110 Table III]. The correct staging exposed it: the
    old η 0.76 had been masking a 23 % low cp.
  - `EXHAUST_THRUST_EFFICIENCY` re-solved on its F-1 pin (0.96 → 0.868).
- **No corpus input change.** The new check builds the F-1 at its real injector-end Pc
  instead.
- **No pump-η curve re-fit.** Only the anchor data were corrected; the real-Ns residuals are
  within about ±0.04.
- **Feed loss is scoped to open cycles.** Staged / expander / electric / pressure-fed keep the
  flat 0.5 MPa, because their chains are pinned separately.

## Context
Findings from the read-only investigation:
- **The five untitled NTRS PDFs are already distilled** (bc1aeed, on main). They cover Shuttle
  OMS/OME, Apollo SPS/DPS/APS and copper-diamond liners; none is turbopump material.
- **The five wanted NASA monographs are public on NTRS:**
  - SP-8052 inducers (19710025474)
  - SP-8110 turbines (19740026132)
  - SP-8125 axial-flow pumps (19780023221)
  - SP-8121 shaft seals (19780022641)
  - SP-8101 shafts/couplings (19740006328)
- **F-1 pump power is ~27 % low, not the ~20 % OPEN_QUESTIONS says** (model 28.8 MW vs ~39.5 MW
  real). The turbine term partly hides it (462 vs 508 kJ/kg), so OPEN_QUESTIONS' "turbine work
  matches" is wrong. Root causes, from running `compute()` on the corpus F-1:

  | Term | Model ox/fuel | Real ox/fuel [F1-Man Fig 3-14] |
  |---|---|---|
  | Feed Pc | 982/982 psia | 1,125 injector-end |
  | Injector dP (0.175·Pc, split 1.0) | 172/172 psi | 309/97 (ratio ~3.2) |
  | Jacket dP | –/194 | –/244 |
  | Line + valve (flat `LINE_LOSS_PA` 0.5 MPa) | 72.5/72.5 | ~168/~404 |
  | Pump dP | 1,183/1,377 | 1,537/1,825 |
  | Pump η (`ETA_PUMP_PEAK` 0.78, bell = 1 at Ns 2200) | 0.78/0.78 | 0.746/0.726 |
  | Turbine | pressure-compounded η 0.76 | velocity-compounded η 0.605 |

  Setting real dP + real η reproduces the real pump power within ~1 %. Fixing only the pump side
  would overshoot GG flow ~9 %, so the turbine staging has to be fixed too. Secondary: the fuel
  pump is evaluated at its own optimum 8,699 rpm on a single shaft reported at 4,724 (real
  5,492).
- **Cory chose FULL calibration** of the F-1 fix in this round.
- Coolant tables are fuel-only and keyed by pair. There is no oxidizer table and no saturation
  data. Rerunning the generator rewrites the combustion tables too.

## Commits (each gated on `./verify_all.sh`; physics commits also on `run_corpus`)

### C1 — literature
- Download the five PDFs into `literature/` as `NASA SP-80xx - <Title>.pdf`.
- One `lit-integrator` per PDF writes a `claude_lit/sources/*.md` note. Tags: [SP-8052],
  [SP-8110], [SP-8125], [SP-8121], [SP-8101].
- The main session then integrates:
  - `topics/09-turbopumps.md`, adding a "Real turbopump component data" table plus
    Implications
  - `08`/`15`, where relevant
  - `README.md` citation-key table, `PROVENANCE.md`, `OPEN_QUESTIONS.md`
- Also read [H1-Man]'s pump discharge pressures from the PDF, as the feed-loss fit's second
  anchor. J-2 fuel discharge/Pc = 1.6 comes from [SP-8107 Table V].
- Brennen: add only if a free copy downloads. Gülich: ask Cory.

### C2 — saturation-property table (new file; existing tables untouched → bit-identical)
- Generator:
  - add a `SATURATION` fluid list (Oxygen, ParaHydrogen, Methane, and n-Dodecane as the RP-1
    surrogate)
  - add `build_saturation_tables()` (CoolProp, Q=0/1): p_sat, ρ_l, ρ_v, h_fg
  - add a `--saturation-only` flag that writes only `property_data/saturation_properties.json`
    and never imports Cantera
- `thermo_tables.saturation(fluid_or_propellant, t_k)` interpolates ln p against 1/T; also add
  `has_saturation()`. Self-test against the normal boiling points.
- Storables (N2O4, MMH, UDMH, N2H4, H2O2) are not in CoolProp: documented gap,
  `has_saturation` → False.

### C3 — F-1 feed-system + pump/turbine calibration
1. **Per-leg feed loss.** Replace flat `LINE_LOSS_PA` with a per-leg valve/orifice/line loss
   scaled with Pc, reverse-solved on the F-1 and cross-checked on J-2/H-1, with a floor at the
   old 0.5 MPa. A pump-connected plumbing run still replaces its leg's line term, with no double
   count.
2. **Injector split.** Give impinging injectors an ox/fuel dP split from the F-1 (~3.2), unless
   it breaks the injector-geometry checks; in that case apply it only to the pump-dP
   accounting.
3. **Corpus feed Pc.** Take the F-1's from the cited injector-end Pc; prefer changing the corpus
   input over the global default.
4. **Pump η.** Evaluate each pump at the shared shaft rpm on single-shaft assemblies, then
   re-fit the bell so all `_PUMP_ANCHORS` stay within tolerance.
5. **Turbine staging.** An open-cycle GG turbine at a high PR → 2-row velocity-compounded
   ([SP-8107]/[SP-8110]); check against J-2/H-1.
6. **validate (i).** Check F-1 pump powers (30.3k/22.7k bhp), discharge pressures (1,602/1,870
   psia) and GG share (2.91 %), each ±10 %, plus J-2 fuel discharge/Pc ≈ 1.6.
7. **Corpus.** `run_corpus --report --diff` → `validation_engines/reports/`, reviewed, then
   `--snapshot`.

### C4 — docs
- ASSUMPTIONS entries for every new or re-fit constant.
- OPEN_QUESTIONS: close and correct the F-1 item; add the storables vapor-pressure gap.
- CLAUDE.md and README updates, the roadmap tick, and the memory entry.

## Verification
- `./verify_all.sh` all PASS after every commit.
- C2: `run_corpus --check` bit-identical.
- C3: the new F-1 checks pass; the corpus diff is committed, and every engine that moves by more
  than 1 % in Isp or mass is summarised.
- GUI: syntax only here. Cory should open an F-1-class design and sanity-check the turbopump
  numbers.
