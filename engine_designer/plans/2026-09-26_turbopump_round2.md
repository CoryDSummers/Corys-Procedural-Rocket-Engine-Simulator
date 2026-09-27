# Planned changes: turbopump fidelity Round 2 — pump meanline, directional design intent, "Turbopump Detail" tab (2026-09-26)

A committed copy of the approved plan so a later session can resume it. **Tick each box when its
commit lands** (with the commit hash). This is Round 2 of
`plans/2026-09-25_turbopump_fidelity_roadmap.md`, extended at Cory's request with directional design
controls, a visual "Turbopump Detail" tab and the axial LH2 pump option.
Branch: `turbopump/round-2`, cut from `turbopump/round-1` @ 70d09f6 (stacked). Draft PR based on
`turbopump/round-1`. It is not merged until Cory has tested it, and not before PRs #18 and #19.

## Status
- [x] C0: this document + draft PR (513e7e1, PR #20)
- [x] C1 (65e8c30): literature (SP-8109 §2.3.1/§2.4/§3.3-3.4 + Table I, Huzel §6.3-6.4, SP-8125 blade design, pump discharge-T anchors)
- [x] C2 (d7a003d): `physics/turbopump_intent.py` + `physics/pump_meanline.py` (pure, self-tests; corpus bit-identical)
- [x] C3 (4d14a67): meanline + intent wired into sizing, schema 17, PUMP MEANLINE validate banner, corpus report + snapshot
- [x] C4 (b7cca25): pump heating → jacket inlet (`coolant_inlet_model`, second pass), anchors, corpus report + snapshot
  - Pump outlet T: the isentropic enthalpy rise is marched in increments on the coolant tables,
    with η on the isentropic head [SP-8107 eq. 17]. Charging every increment's loss separately
    over-heated the SSME HPFTP by 5 K; the chosen basis lands within 1.4 K. LOX has no table,
    so it uses (Δp/ρcp)(1/η − 1 + Tβ), reproducing the HPOTP's +10.6 K; it is reported only.
  - Runs just before the turbopump sizing stage (the expander's pump η is set in geometry_stage).
  - Up to 3 corrective passes, under-relaxed (the RL10 expander oscillates), each refreshing the
    nozzle-injected film carry. They merge with the existing line-loss/film second pass.
  - Anchors: corpus RS-25 jacket inlet 52.2 K vs the real MCC coolant inlet 52.0 K; J-2 31 K
    in [TN-Dump]'s measured 32-47 K band.
  - Knock-on: the colder, denser LH2 inlet raises channels-mode jacket dP ~1.5-1.8x (J-2
    3.3 → 4.9 MPa, RL10 9.3 → 12.1). Channels are sized at the INLET coolant velocity; the
    Round 1 45 K inlet was hiding this. Two plausibility bands widened with comments, and an
    OPEN_QUESTIONS item for a later cooling round.
  - The mesh_builder colour-scale self-test pins the table inlet, since it needs a narrow-range
    jacket.

**Where the implementation departed from the plan, and why:**
- **Pump type "auto" = centrifugal**, not an LH2 rule. Every LH2 pump designed after the J-2S
  (SSME, RL10, Vulcain, LE-7) is centrifugal, and SP-8125 §3.2.1 rules out axial where
  throttling is needed. The corpus J-2 sets `pump_type_fuel="axial"` explicitly (Mark 15-F,
  [SP-8125 Table I]).
- **Impeller eye.** Taken from the SP-8109 Fig. 5 fleet trend, δ = 0.69·(Ns/1570)^0.45 ×
  (Ss_design/38k)^0.32, not from Round 1's inducer tip (which at φ_opt is oversized). The design
  Ss is the Ss the pump actually needs at its NPSH available [SP-8109 §3.3.1.1], so ample NPSH
  gives a smaller eye and less Fig. 9 penalty. That fixed the pipeline H-1 and J-2 LOX
  efficiencies.
- **Blade count.** Huzel's β2/3, then more blades until c_m2 ≥ c_m1 [SP-8109 §3.3.1.2], up to
  max(12, 28·sin β2).
- **Mass.** A non-neutral intent scales turbopump mass by its geometry-mass ratio to the same
  machine at neutral intent, clamped 0.6–1.6 (Tier 3 until Round 4). The full slider ends hit
  the clamp.
- **Performance.** The staged-combustion solvers re-size the pumps thousands of times per
  compute. The meanline has an exact-argument cache, a secant φ2 solve and an Aitken-accelerated
  η_h iteration. Raptor-2 went from 67 s to under 0.4 s.
- **Calibration.**
  - K_HYD 1.76 on 7 real centrifugal pumps (rms 0.031); K_AX 2.49 on J-2 Mark 15-F / M-1
    (rms 0.025).
  - Axial DF comes from the profile loss only; K_AX scales the returned efficiency, not the
    loading.
  - Axial stage Ns 4,450 [SP-8125 Table II].
  - Wear-ring clearance floor 0.006 in and mechanical loss 15 % at 1 in, both fitted so the size
    effect follows SP-8109 Fig. 6 within ±10 pts.
- **Validation adjustments, each justified in its file:**
  - RL10 LOX pump gated ±0.13, like the RL10 fuel pump. The tool designs a 2-in 33k-rpm
    direct-drive impeller where the real one is geared at 12,100 rpm.
  - The suction check's discharge-equality row compares on the correlation pump model.
  - The baffle row tests the stability-aid mass, not total dry mass, which also moves with
    turbopump/plumbing re-sizing.
- **Known limitations** (OPEN_QUESTIONS):
  - Small (2–6 in) impellers run ~5–8 pts optimistic against Fig. 6.
  - At the neutral stage Ns 2,200, LH2 multistage pumps get wide outlets (b2/D2 ~0.18–0.22,
    beyond Table I's 0.14). A warn row suggests "efficient".
- [ ] C4: pump heating → jacket inlet (`coolant_inlet_model`, second pass), anchors, corpus report + snapshot
- [x] C5 (52421c9): GUI: `gui/turbopump_detail.py` + right-notebook tab + left "Design intent" section
  - Panels A-F plus a caption, drawn from the meanline; headless self-test renders 8 cases;
    `app.py` is syntax/import-checked only (no display here).
  - The impeller face shows blades + splitters, a realistic ~130° wrap, and a volute spiral
    growing in the rotation direction up to the tongue.
  - The machinable-blade warning now fires only when z > 28·sin β2 AND the tip speed is
    above the ~1,400 ft/s casting limit [SP-8109 §3.3.3]; otherwise the impeller is cast.
  - The axial H-Q sketch is normalised on its own design value and shows a stall dip.
- [x] C6: docs (ASSUMPTIONS, OPEN_QUESTIONS, topics/09, CLAUDE.md, README, roadmap tick, memory)

## Context
Rounds 0 and 1 are done (PRs #18 and #19, both awaiting Cory's GUI test). Round 2 in the roadmap
(`engine_designer/plans/2026-09-25_turbopump_fidelity_roadmap.md`) is pump meanline hydraulics plus
pump heating into the thermal solve. Cory added two asks:
1. **Directional design controls.** The user sets design *intent* (priorities and trade-offs) and
   the tool derives the exact geometry, rather than the user typing blade angles.
2. **A visual tab** that describes the turbopump in depth once blade-level detail exists: impeller
   blades, inducer, volute, velocity triangles, and where the efficiency goes.

What exploration found:
- **`turbopump_sizing.size_pump` (l.561) has no blade geometry.**
  - rpm = `NS_TARGET_US` 2200 × H^0.75/√Q.
  - Tip speed = √(gH/ψ), with `HEAD_COEFFICIENT_PSI` 0.5.
  - D = 60u/(πn). The envelope is a fixed multiple of D (`VOLUTE_OD_FACTOR` 1.6 etc.).
  - η is one lumped number: `turbopump_efficiency.pump_efficiency` = 0.78 × Ns-bell × size ×
    build quality, fitted to 9 `_PUMP_ANCHORS` (l.145).
  - There is no design-intent input anywhere. 2200 and 0.5 are hard-coded.
- **Coolant inlet temperature is a constant** (`design/constants.py:164` `COOLANT_INLET_TEMP_K`,
  e.g. LH2 45 K with pump heating baked in implicitly). It is set in `cooling_stage.py:127`,
  *before* the pumps are sized (`engine.py:658-671`). Pump heating therefore needs the existing
  multi-pass `_compute_pass` pattern, still ONE thermal solve per pass.
- **Literature gap.** `claude_lit` has no meanline correlations: slip, blade angles, b2, volute
  sizing and loss build-up are all missing. SP-8109 §2.3.1 was only partly read; §2.4 (housing,
  diffuser, volute, p.39-55) and §3.3-3.4 (impeller and housing design criteria, p.66-80) were not
  read. Both SP-8109 and Huzel are local PDFs.
- **GUI pattern to reuse.** `gui/turbopump_diagram.py` and `gui/injector_face.py` are Tk-free
  `draw_*(ax, result)` modules with an Agg `__main__` self-test in `verify_all.sh`. A right-notebook
  tab = a `Figure` + `FigureCanvasTkAgg` + a `_redraw_*` method registered in
  `_tab_frames/_tab_redraw_fns/_tab_dirty` (`app.py:1532-1562`).

Branch `turbopump/round-2`, cut from `turbopump/round-1` (stacked, like #19 on #18). Draft PR based
on `turbopump/round-1`. Not merged until Cory tests it.

## Design

### 1. Directional design intent (new `physics/turbopump_intent.py`, pure)
- Four sliders, −1 … +1, default 0. **At 0, every derived parameter equals today's constant**, so
  geometry is unchanged by default.
- Two dropdowns.
- Each slider end is bounded by a cited real-hardware range. The exact bounds are fixed in C1 from
  SP-8109 Table I / §3.3 and SP-8052.

| Intent (user sees) | What it drives |
|---|---|
| **Efficient ◄► Compact** (`pump_priority`) | Ns target (≈1,500–3,000), head coefficient ψ, blade count → rpm, D2, mass, η |
| **Stable/throttleable ◄► Max head** (`pump_head_curve`) | outlet blade angle β2 (backswept ~20° ↔ ~40°+), splitters → H-Q slope, slip, η |
| **Conservative ◄► Aggressive suction** (`suction_aggressiveness`) | inducer cavitation number K (Round 1's 0.0145 at 0), tip clearance, NPSH margin → suction-limited rpm |
| **Stress margin ◄► Max tip speed** (`tip_speed_aggressiveness`) | `TIP_SPEED_DESIGN_FRACTION` (0.85 at 0) → stage count vs. rotor stress margin |
| Inducer: auto / on / off | off = no-inducer suction limit (`inducer.SS_NO_INDUCER`) |
| Diffuser: auto / volute / vaned + volute | volute-only vs. vaned diffuser loss, and OD |

- `intent_parameters(design) → dict` is the one mapping, printed in the GUI as a readout, e.g.
  "Compact +0.5 → Ns 2,650, ψ 0.55, 7 blades: −9 % pump mass, −2 pts η".
- The existing exact overrides (stages, η pins, NPSH override) stay.

### 2. Pump meanline (new `physics/pump_meanline.py`, pure)
Per stage, from `size_pump`'s Q, H_stage, n, D2 and the intent parameters:
- Inlet and outlet velocity triangles (U, W, C, and the angles).
- Blade count and β2 from intent. Slip uses whatever SP-8109/Huzel cite (Wiesner is the fallback,
  flagged Tier 3 if uncited). φ2 is solved so the slipped Euler head matches the target ψ; b2 follows.
- Loss build-up, as head fractions:
  - incidence
  - blade-channel friction
  - diffusion (W1/W2)
  - diffuser/volute
  - wear-ring leakage → volumetric η
  - disk friction
  - mechanical (SP-8109's "up to 20 % for ~1 in impellers")

  η_pump = η_hydraulic × η_volumetric × η_mechanical.
- **Calibration:** one hydraulic-loss multiplier, reverse-solved so all 9 `_PUMP_ANCHORS` stay
  within the existing ±0.08 tolerance and the SP-8109 Table I stages are reported. The Ns-bell
  `pump_efficiency` stays as a cross-check row, not deleted (per the roadmap).
- **Geometry export for the drawing:**
  - meridional outline (inducer, hub/shroud, stage stack, volute section)
  - blade camber lines, as a log-spiral blend of β1 → β2
  - splitters
  - volute spiral area schedule and tongue
  - an approximate H-Q curve from the meanline (Euler line minus losses), labelled a sketch; full
    maps are Round 5
- New field `pump_model` "meanline" (default) | "correlation" (bit-identical to Round 1, same
  pattern as `suction_model`).
- **Axial pump option (included, Cory's call).** A new per-leg field `pump_type_{fuel,ox}` takes
  auto / centrifugal / axial.
  - "auto" chooses axial only for LH2, when centrifugal would need ≥ `MAX_PUMP_STAGES`-scale head
    or SP-8125's selection rule says so. Exact rule is from C1; J-2/M-1 are the precedent.
  - Axial is warn-only on dense propellants.
  - The axial meanline uses SP-8125's stage flow/head coefficients φ_T/ψ_T: rotor + stator rows per
    stage, hub/tip ratio, blade angles from the triangles, and the stage count from ψ_T and the tip
    speed limit.
  - η = SP-8125's stage hydraulic η (which excludes inducer, volute, leakage and mechanical) × the
    same volumetric/mechanical/volute terms as centrifugal.
  - Anchors: the J-2 LH2 axial pump (`_PUMP_ANCHORS` 7 stages, η 0.73) plus the SP-8125 Table II
    stages.
  - The Detail tab draws axial pumps as a multi-row meridional section plus an unwrapped blade
    cascade (rotor/stator profiles), instead of the impeller face view.

### 3. Pump heating → jacket inlet
- Pump outlet temperature = inlet T + ΔP/(ρ·η·cp), using the coolant table's cp. The boost pump's
  heating is included. Tank T is Round 1's `propellant_temp_*` (NBP default).
- The fuel pump outlet T becomes the jacket `coolant_inlet_k` through a second `_compute_pass`: pass 1
  uses the constant; pass 2 runs only if the computed T differs by more than 0.5 K. This keeps one
  thermal solve per pass.
- New field `coolant_inlet_model` "computed" | "table". "table" gives the old constant, and
  the "correlation" pump model forces "table", so legacy stays bit-identical.
- Anchors to find in C1: SSME HPFTP discharge T, J-2 fuel pump discharge T, and RL10 if cited.
  With no anchor, the check is plausibility only, and says so.

### 4. "Turbopump Detail" tab (new `gui/turbopump_detail.py`, Tk-free, Agg self-test)
- Leg selector: fuel / ox pump (and turbine side placeholders for Round 3).
- Panels, drawn to scale from the meanline export:
  - **A. Meridional half-section:** inducer → impeller stage(s) → diffuser/volute, shaft,
    bearings/seals as blocks, labelled dimensions (D1, D2, b2, inducer tip).
  - **B. Impeller face view:** blades and splitters as camber curves, inducer blades overlaid,
    volute spiral and tongue.
  - **C. Velocity triangles:** inlet and outlet, U/W/C arrows, β angles, ideal vs. slipped Cu2.
  - **D. Where the power goes:** a waterfall from Euler head to delivered head (slip, incidence,
    friction, diffusion, volute, leakage, disk, mechanical), with the Ns-bell η as a marker.
  - **E. Suction:** NPSHa vs NPSHr bars (Round 1 data), Ss, TSH, margin, and the suction-limited
    rpm drop.
  - **F. H-Q sketch:** design point, shutoff head, rising or falling curve, a stability flag.
  - A caption box of short plain-language notes per part, plus the intent readout.
  - For an axial leg, panel B becomes the unwrapped rotor/stator cascade, and panel A the multi-row
    meridional section.
- The drawing stays in the testable module, and the Tk wiring stays in `app.py`.
- A "Design intent" collapsible section goes on the left Turbopump tab (sliders with end labels,
  two dropdowns).

### Checklist and validation (warn, don't block)
- **New rows:**
  - rising H-Q curve at the design point (throttling unstable)
  - β2 or blade count outside SP-8109 Table I's range
  - b2/D2 too thin to cast or machine
  - volute throat velocity
- **New banner "ALL PUMP MEANLINE CHECKS OK" (31st):**
  - meanline η within ±0.08 of every `_PUMP_ANCHORS` entry
  - SP-8109 Table I stages: β2/Z/ψ reproduce within ranges (reported)
  - intent at 0 gives geometry identical to Round 1
  - monotonicity: Compact → higher rpm, smaller D, lower η
  - pump-heating anchors or plausibility
  - legacy switch is bit-identical

## Commits (each gated on `./verify_all.sh`)
- **C0:** `plans/2026-09-26_turbopump_round2.md` (this plan + checklist), branch, draft PR.
- **C1, literature (Cory said yes; about 75 pages):**
  - SP-8109 §2.3.1 (finish), §2.4, §3.3-3.4 and Table I transcription: about 45 pages.
  - Huzel §6.3-6.4 (pump design): about 15 pages.
  - SP-8125 blade-angle/design-criteria sections and Table II rows, for the axial option: about
    15 pages.
  - Pump discharge temperature anchors.
  - One `lit-integrator` agent per source, in parallel; then I integrate into `topics/09`, the
    source notes and `PROVENANCE`.
- **C2:** `physics/turbopump_intent.py` + `physics/pump_meanline.py`, pure, with self-tests.
  Corpus bit-identical (not yet wired).
- **C3:** wire the meanline + intent into `size_pump` and `derive_efficiencies`.
  - `EngineDesign` schema 17 fields: `pump_model`, the 4 intent sliders, `inducer_mode`,
    `diffuser_type`, `pump_type_fuel/ox`.
  - Validate banner.
  - Legacy bit-identity check, corpus `--report --diff` → `reports/`, then `--snapshot`.
- **C4:** pump heating → jacket inlet (`coolant_inlet_model`, second pass), validate anchors, corpus
  report and snapshot.
- **C5:** GUI: new `gui/turbopump_detail.py` (+ `verify_all.sh`), right-notebook tab, left "Design
  intent" section, result lines. Syntax check for `app.py`. The self-test PNGs are inspected here
  and sent to Cory for a first look.
- **C6:** docs: ASSUMPTIONS (intent mapping table, slip/loss constants and tiers), OPEN_QUESTIONS,
  CLAUDE.md (banner count 31, layout), README, roadmap tick, memory.

## Critical files
- New:
  - `physics/turbopump_intent.py`, `physics/pump_meanline.py`
  - `physics/validate/pump_meanline.py`
  - `gui/turbopump_detail.py`
- Modified:
  - `physics/turbopump_sizing.py` (`size_pump`, `_stage_quantities`)
  - `physics/turbopump_efficiency.py` (cross-check only)
  - `physics/design/engine.py` (fields, schema 17, pass logic)
  - `design/cooling_stage.py:127`, `design/feed_stage.py`, `design/rollup_stage.py`
  - `gui/app.py` (tab registration at 1532-1562; Turbopump input section around 917)
  - `verify_all.sh`, `validation_engines/`
- Reused:
  - `inducer.py` (K, SS_NO_INDUCER, suction spec)
  - `thermo_tables` coolant cp
  - `_PUMP_ANCHORS`
  - `_compute_pass` multi-pass
  - `gui/turbopump_diagram.py` pattern

## Verification
- `./verify_all.sh` all PASS after every commit; `validate | grep -c '^ALL'` = 31.
- C2 is corpus bit-identical.
- C3/C4: legacy (`pump_model="correlation"`) bit-identical vs the Round 1 golden. The per-engine
  diff summary covers η, rpm, D2, TP mass, jacket inlet T and Isp.
- The detail tab's Agg self-test renders every cycle case; I view the PNGs myself.
- Cory tests the Tk tab and sliders (no `$DISPLAY` here).
