# Planned changes: turbopump fidelity Round 1 — the suction side (2026-09-26)

A committed copy of the plan so a later session can resume it. **Tick each box when its
commit lands** (with the commit hash). This is Round 1 of
`plans/2026-09-25_turbopump_fidelity_roadmap.md`.
Branch: `turbopump/round-1`, cut from `turbopump/round-0` @ 11f61f0 (stacked: it needs Round 0's
saturation table and pump-pair sizing). Draft PR based on `turbopump/round-0`, so its diff is
Round 1 only. It is not merged until Cory has tested it, and not before PR #18.

Plan mode was switched off before a plan was presented, so this doc is the plan of record. Cory
reviews it in the draft PR.

## Status
- [ ] C0: this document + draft PR
- [ ] C1: `physics/inducer.py` (Brumfield / NPSHr / TSH / tip clearance / tip diameter), pure + self-test
- [ ] C2: suction wiring (tank → line → boost → NPSHa; cap on by default; legacy switch), GUI,
      schema 16, SUCTION validate banner, corpus report + snapshot
- [ ] C3: docs + literature (SP-8107 Table II transcription, topics/09, ASSUMPTIONS,
      OPEN_QUESTIONS, CLAUDE.md, README, roadmap tick, memory)

## Context
Today:
- Rotor speed comes from Ns alone. The only cavitation limit is a user-typed
  `npsh_available_*_ft` (0 = off) against a flat per-class `NSS_TARGET_US`
  (40,411 LOX / 58,027 LH2, back-solved from NPSH_crit).
- The LH2 value was back-solved with **Q = 3,000 gpm, but the real J-2 LH2 pump flows 8,530 gpm**
  [SP-8107 Table II]. The LH2 constant is therefore wrong. It is kept only on the legacy path.
- The pump inlet is a flat `TANK_HEAD_PA` 0.3 MPa. There is no tank, no vapor pressure, no
  suction line and no boost pump.

Prototype (corpus, default inputs, the model below):
- **The F-1 LOX cap lands at 5,502 rpm, against the real 5,488.** The real F-1 was designed at its
  suction limit, which is a good sign for the calibration.
- The cap binds on the LOX pump of RS-25, RD-180, Vulcain, Merlin, Raptor, Rutherford and the
  RS-29 family.
  - RS-25 and RD-180 really do need boost pumps.
  - Vulcain's LOX pump moves 22.7k → 15.7k rpm, toward its real ~13.6k.
- LH2 and RP-1 legs never bind at 0.3 MPa. LH2's low density turns 0.2 MPa of margin into
  ~900 ft of head.

## Model (C1: `physics/inducer.py`, pure functions)
- **Brumfield optimum** [SP-8052 §2.1.3 eq. 2-7]:
  - φ_opt = √(K/(2(1+K)))
  - max S′s = 5055/((1+K)^¼K^½)
  - Ss = S′s·√(1−ν²)
- **Design cavitation number** `DESIGN_CAVITATION_NUMBER` 0.0145 (Tier 2). Back-solved so
  Brumfield at ν 0.3 gives [SP-8109 §3.2.1.2]'s recommended max inducer Ss of 40,000 (water). It
  sits inside [SP-8052 p.12]'s measured thin-blade K* of 0.006-0.01 × the 2-3× "attained" factor.
  φ_opt = 0.0845, inside Table I's 0.074-0.116.
- **Tip clearance** [SP-8052 eq. 54]: Ss × (1 − 0.575·√(c/L)); c/L fuel 0.005, ox 0.020 (the
  minimum practical values). That is −4 % fuel, −8 % ox.
- **Thermodynamic suppression head (TSH)** [SP-8052 §2.1.4 p.16]:
  - Empirical anchors: LOX 11 ft at 163 °R, LH2 250 ft at 38 °R.
  - Scaled ∝ p_v(T), from "almost a linear function of vapor pressure", using
    `thermo_tables.saturation`.
  - No speed scaling (Tier 3 omission).
  - CH4, RP-1 and the storables get 0 (no data; conservative). CH4 → OPEN_QUESTIONS.
- **NPSHr at rpm n** (flight): max[(n√Q/Ss_eff)^{4/3} − TSH, Z_min·c_m²/2g]
  - Z_min = 2.3 LOX, 1.3 LH2, 3.0 otherwise [SP-8109 §3.2.1.2]. This floors the TSH credit.
  - c_m = φ·πDn/60, with D from [SP-8052 eq. 8].
  - Both terms ∝ n^{4/3}, so the **suction-limited rpm inverts exactly**.
- **Inducer tip diameter** [SP-8052 eq. 8]: this replaces `inlet_eye_dia_m`'s φ 0.10 guess on
  the computed path (the pump inlet port bore).

## Wiring (C2)
- **New `EngineDesign` fields** (schema 16; no migration, old files get the computed model):
  - `suction_model` "computed" | "legacy". Legacy is bit-identical to today (flat 0.3 MPa inlet,
    `NSS_TARGET_US` cap only if the user sets NPSH).
  - Per leg `tank_pressure_{fuel,ox}_pa`. 0 = auto = `TANK_HEAD_PA`, the old net inlet, so pump dP is
    unchanged by default.
  - Per leg `propellant_temp_{fuel,ox}_k`. 0 = auto: saturated at 1 atm (NBP) for cryogens,
    293.15 K for NBP > 250 K.
  - Per leg `suction_head_{fuel,ox}_m`, plus `suction_accel_g` 1.0.
  - `suction_line_length_m` (0 = none).
  - Per leg `boost_pump_rise_{fuel,ox}_pa` (0 = none).
  - The existing `npsh_available_*_ft` > 0 remains a user override of the computed NPSHa.
    `enforce_suction_limit` is honored only on the legacy path.
- **New stage `design/suction_stage.py`**, run before the turbomachinery cycle:
  - p_inlet = p_tank + ρ·g0·a·h − suction-line loss.
  - The suction-line loss is a new `plumbing.suction_line_loss_pa`: Darcy friction reusing
    `cooling._darcy_friction` / `PIPE_ROUGHNESS_M` / `liquid_viscosity_pa_s`, plus an entrance and
    prevalve K. The line is sized at `SUCTION_LINE_VELOCITY_OF_LIMIT` × the [SP-8052 eq. 57]
    velocity limit. It is a straight lumped duct until E1 adds a drawable suction host.
  - NPSHa = (p_inlet − p_v)/ρg.
  - The main pump inlet = p_inlet + boost rise.
  - Every `- TANK_HEAD_PA` in the pump-dP build becomes the per-leg main-pump inlet pressure. The
    staged solver takes a (fuel, ox) inlet pair.
- **Boost pump (SSME style)**:
  - It is sized by `size_pump` at the tank NPSHa, so it comes out slow and suction-limited.
  - Its drive is a hydraulic turbine off the main discharge. It is carried as extra main-pump
    head: rise/(η_boost·η_drive).
  - η_drive: LOX 0.677, fuel 0.58 [SSME-Orientation LPOTP/LPFTP].
  - The discharge report stays physical.
- **`size_pump(suction=SuctionSpec)`**: threaded through `size_pump_pair` /
  `derive_efficiencies` / `derive_expander_efficiencies` / `size_turbopump`, alongside the existing
  `npsh_available_*` kwargs.
- **Checklist (warn, don't block)**, per leg:
  - NPSHa vs NPSHr: margin, suction-limited rpm drop, and the tank-pressure or boost rise that
    would restore the Ns-optimum speed.
  - NPSHa ≤ 0 → red row (the propellant boils at the inlet).
  - Storable with no vapor-pressure data → info row.
- **Rollup keys**: `suction` {per leg: p_tank, T, p_v, NPSHa, NPSHr, TSH, margin, line loss,
  boost}.
- **GUI**: a "Pump suction" group plus result lines. Syntax check only here.
- **validate, new banner "ALL PUMP SUCTION CHECKS OK" (30th)**:
  - Every inducer-equipped SP-8107 Table II pump runs at or below the model cap at its own
    NPSH_min. LR81 IRFNA is report-only (storable, TSH unknown).
  - F-1 LOX real/cap in [0.85, 1.0].
  - RD-0110 [KBKhA] under its cap.
  - Brumfield vs SP-8052 Table I, 4 of 6 within 10 %.
  - The TSH anchors reproduce.
  - The corpus F-1 is not limited; ox rpm within 10 % of 5,488.
  - The RS-25 LOX pump is limited without its boost pumps and freed with them.
  - Legacy mode reproduces the Round 0 golden (checked once by hand at C2).
- **Corpus**:
  - RS-25 gets its real inlets and boost rises [SSME-Orientation p.52-71]: LOX 100 → 380 psia,
    LH2 30 → 250 psia.
  - `--report --diff` goes to `reports/`, then `--snapshot`.

## Verification
- `./verify_all.sh` all PASS after every commit.
- C1 is bit-identical (`run_corpus --check`).
- C2:
  - Run the corpus in legacy mode against the Round 0 golden (bit-identical) before
    re-snapshotting.
  - The report diff is summarised per engine.
  - `validate | grep -c '^ALL'` = 30.
- GUI is syntax-checked only (no `$DISPLAY`). Cory should open an F-1 and an RS-25-class design,
  toggle computed/legacy, and try a boost pump.
