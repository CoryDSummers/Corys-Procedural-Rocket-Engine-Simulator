# AEDC-TR-70-204 — Altitude Developmental Testing of the J-2S Rocket Engine

## Identity

C. E. Pillow (ARO, Inc.), *Altitude Developmental Testing of the J-2S Rocket Engine in
Rocket Development Test Cell (J-4) (Tests J4-1001-06, -07, -11, and -15)*, AEDC-TR-70-204,
September 1970. Sponsored by NASA/MSFC; engine built by Rocketdyne (North American
Rockwell); test facility AEDC (Arnold AFS, TN). `literature/AEDC-TR-70-204 - Altitude Developmental Testing of the J-2S Rocket Engine.pdf` (NTRS 874400; 118 PDF leaves; no
fixed offset found — leaf 6 is printed p."iii", leaf 9 is printed p.1 SECTION I, i.e. printed
page N ≈ PDF leaf N+8 in the body text; front matter numbering is roman and doesn't follow
this rule). Tag: `[AEDC-J2S]`.

## Character

A real-hardware **altitude facility test report** for the J-2S, the only US flight-qualified
**tap-off-cycle** engine (an uprated derivative of the tap-off-cycle J-2 used on Saturn
IB/V's S-IVB stage, though the J-2S itself only reached ground-test maturity, never flying
operationally). This is the first source in `claude_lit/` with real tap-off-cycle hardware
detail and real engine performance numbers — prior tap-off coverage in
`topics/08-engine-cycles.md` is generic (`[Sutton]` §6.6/Ch.10 concept-level description
only, no real engine).

Eleven firings across four test periods (J4-1001-06/-07/-11/-15), conducted Aug–Oct 1969 at
simulated altitudes of 80,000–108,000 ft. Primary objectives were **idle-mode
characterization** (J-2S's defining tap-off-cycle-enabled feature: a low-thrust "idle" state
before full main-stage ignition, used for orbital-restart tank settling/ullage) and
main-stage performance confirmation — not a design/derivation document like `[SP-8081]`/
`[SP-8107]`, closer in spirit to `[NK-33-Mod]` (real single-engine test-program report) but
for a **tap-off**, not staged-combustion, cycle.

Structure: §I Introduction (p.1), §II Apparatus (p.1–5, includes the engine-description
subsection with all the real hardware numbers below), §III Procedure (p.5–6), §IV Results
and Discussion (p.6–16, per-firing narrative with occasional real performance numbers),
§V Summary of Results (p.16–17), References (p.17), then Appendixes: I Illustrations
(figures, mostly plots — same OCR-unextractable-curve caveat as other AEDC/NASA reports
already in this reference set), II Tables (engine component/orifice/modification lists),
III Instrumentation List (sensor ranges — useful for real sensor full-scale ranges, e.g.
fuel turbine inlet temperature range), IV Performance calculation method (referenced but not
read this pass).

## This note's extraction scope

Read in full: §II Apparatus / engine description (leaf 9–12, all the real J-2S component
numbers below), the Fig. 4/5/6/7 schematic captions (tap-off/bypass valve schematic and
start/shutdown sequence, leaf 30–36), and §IV's per-firing narrative for every firing that
reports a calculable main-stage performance number (leaf 17–21, firings 06A/07A/07B/07C).
Skimmed: remaining per-firing narratives (11A/11B/11C/15A/15B/15C, leaf 20–27) for idle-mode-
specific findings only (most lack usable performance numbers — see Caveats). Table I (major
engine components, leaf 78) and Table III engine modifications (leaf 80, tap-off-valve
mechanical-stop-length changes) were read. The Instrumentation List (Appendix III, leaf
93–115+) was skimmed for sensor ranges only. **Not read**: §V Summary of Results itself,
Appendix IV (performance-calculation method), Table II (orifice list), Table IV (modification
list detail beyond what's quoted), and the bulk of the individual firing plots (Figs. 10–53 —
axis labels/captions only, not the plotted traces).

## Key results — J-2S tap-off cycle hardware (real numbers)

**Engine performance envelope** `[AEDC-J2S §2.1 p.1]`: designed for **idle mode at nominal
5000 lbf thrust, mixture ratio 2.5**, or **main stage at any precalibrated thrust level
between 230,000 and 265,000 lbf at mixture ratio 5.5**. Minimum idle-mode duration before
transition to main stage: **1 sec**. From main stage the engine can shut down or transition
back to idle mode before shutdown — i.e. the tap-off cycle's idle capability is explicitly a
**restart/settling feature**, not just a startup-sequencing artifact.

**Tap-off/bypass valve hardware, real schematic** `[AEDC-J2S Fig. 4–5, leaf 30–34]`: a
**Hot Gas Tapoff Valve** bleeds combustion gas from the thrust chamber to the turbines; a
**Thrust Chamber Bypass Valve** routes fuel around the thrust chamber body (rather than
through the cooling tubes) when the tapoff valve is closed/idle. Table I (major-component
list, leaf 78) confirms distinct physical parts: **Thrust Chamber Bypass Valve**, **Hot Gas
Tapoff Valve**, **Thrust Chamber Bypass Duct**, **Fuel Turbine Exhaust Bypass Duct**, **Hot
Gas Tapoff Duct**, and separately an **Oxidizer Turbine Exhaust Duct** — i.e. the real J-2S
plumbing has the fuel turbine fed directly from the tapoff duct, with a *separate* exhaust
duct for the oxidizer turbine, consistent with a **series turbine arrangement** (tapped gas
drives the fuel turbine first, then continues to drive the oxidizer turbine downstream,
before final overboard dump) — worth checking against however `staged_combustion.py`/
`design.py` currently models tap-off turbine staging, if at all.

**Start/shutdown sequencing, real event order** `[AEDC-J2S Fig. 6–7, leaf 36]`:
- **Start**: engine start signal → main fuel valve opens → idle-mode oxidizer valve opens →
  (idle mode runs ≥1 sec) → main-stage start signal → solid-propellant turbine starter (SPTS)
  fires → **hot gas tapoff valve opens** → main oxidizer valve opens (first stage, then
  ramped fully open) → **thrust chamber bypass valve closes** (in that order — tapoff valve
  opens *before* the bypass valve closes, i.e. there's a brief overlap window) → main stage.
- **Shutdown**: cutoff signal → main oxidizer valve closes → **hot gas tapoff valve closes**
  → **thrust chamber bypass valve opens** → main fuel valve closes (last) → helium control
  solenoid deenergizes.
- This confirms the tap-off cycle needs a **solid-propellant turbine starter** to get the
  turbines spinning before there's enough chamber pressure to self-sustain via tapped gas —
  the same "spin-up problem" any hot-gas-tap or staged-combustion cycle without a separate
  spin-up gas generator has to solve, and a real concrete example of one solution (small solid
  motor, one-shot, used only at start).

**Real component data** `[AEDC-J2S §2.1.1 p.1–3]`:
- Thrust chamber: tubular-walled bell nozzle, 18.6 in combustion-chamber diameter, throat
  diameter 12.192 in, **L\* = 35.4 in**, expansion ratio **39.62**, overall length (injector
  flange to nozzle exit) 108.6 in. Cooling: fuel flows down 180 tubes then up 360 tubes to
  the injector (a **1:2 tube-count splice**, i.e. every downcomer tube splits into two
  upcomer tubes at the turnaround — real-hardware corroboration of `[SP-8120]`'s tube-splice-
  joint design criteria already in `topics/12-materials-and-structures.md`, on the exact
  cycle/engine family SP-8120's own J-2/J-2S band-redesign anecdote references), plus film
  cooling inside the chamber.
- Injector: concentric-orificed (fuel orifices around oxidizer post orifices), **porous-faced,
  transpiration-cooled** — ~**3.5% of main-stage fuel flow** cools the injector face by
  transpiration through the porous material. Fuel/oxidizer injector orifice areas: 19.2 /
  5.9 sq in. During idle mode, oxidizer is supplied through a top-mounted diffuser that
  disperses it across the whole face (a *"full-face oxidizer flow"* injector configuration
  was specifically the subject of this test series, replacing an earlier configuration that
  had idle-mode oxidizer injection temperatures spike **up to 1500°F** during transition —
  the new full-face design cut that transition spike to **<10°F**, a striking real fix for an
  idle-mode-specific thermal problem `[AEDC-J2S §4.1, leaf 15]`).
- Fuel turbopump: 1.5-stage centrifugal pump, direct-drive 2-stage turbine, self-lubricated;
  at the 265,000-lbf rated point: **60,300 ft LH2 head rise, 9750 gpm, 29,800 rpm**.
- Oxidizer turbopump: single-stage centrifugal pump, direct-drive 2-stage turbine,
  self-lubricated; at the 265,000-lbf rated point: **3250 ft LOX head rise, 3310 gpm,
  10,500 rpm**.
- Main oxidizer valve: two-stage pneumatic butterfly valve — first stage to a nominal
  ~10.5–12 deg gate angle (varied across this test series, see modifications below) for
  initial main-stage phase, second stage ramps fully open to accelerate to rated thrust — a
  real two-step throttle-up sequence, not a single valve stroke.
- Propellant utilization valve: motor-driven sleeve valve on the oxidizer turbopump,
  bypasses LOX from discharge back to pump inlet to trim mixture ratio (the real MR-control
  mechanism behind the MR variations seen in the test-point table below).

**Real main-stage performance data points** (calculated from t-0+7.5 to t-0+8.5 sec averages
per firing) `[AEDC-J2S §4.2, leaf 17–19]`:

| Firing | Pc (psia) | c* (ft/s) | Isp (lbf·s/lbm) | Thrust (lbf) | MR |
|---|---|---|---|---|---|
| 06A | — (not stated) | ~7800 | ~434 | ~230,000 | ~4.6 (off-nominal, orificing error) |
| 07B | 1182 | ~7740 | ~433 | ~249,000 | ~4.9 |
| 07C | 1279 | ~7720 | ~434 | ~271,000 | ~5.1 |

Nominal design MR at main stage is 5.5 (null propellant-utilization-valve position ≈5.0 in
these particular tests per text) — real test MRs cluster 4.6–5.1, i.e. these particular
firings ran fuel-rich of the 5.5 design point. **Caveat on the Pc column**: 1182–1279 psia is
notably higher than the ~700–850 psia chamber pressure typically cited for J-2/J-2S in
secondary literature; this note does not know whether the report's "PC-2P" tap is true
nozzle-stagnation chamber pressure or a higher-pressure tap nearer the injector face (a
pressure-drop-elevated reading) — treat the **c\*/Isp/thrust/MR figures as the trustworthy
real numbers** from this table, and treat the Pc figures with caution until cross-checked
against a source that states the tap location unambiguously (Appendix IV, not read this
pass, likely has the actual reduction method and may resolve this).

**Idle-mode real numbers** `[AEDC-J2S Abstract, §4, leaf 5, 14–27]`: idle-mode chamber
pressure ran **18–31 psia** across different firings (vs. 5000 lbf/MR 2.5 nominal idle-mode
design point) — two orders of magnitude below main-stage Pc, consistent with idle mode being
a genuine low-power tap-off-throttled state, not just a valve-sequencing pause. Idle-mode
duration to reach "stabilized" operation (chamber pressure oscillations <±1 psi) ranged
20–70 sec across firings and several never stabilized at all (unsteady/superheated
propellant-flow issues at the flowmeters repeatedly prevented idle-mode performance
calculation — this test series had real difficulty getting clean idle-mode data, which is
itself informative: idle-mode operation of a tap-off engine is evidently harder to
characterize/stabilize than main-stage operation). Maximum thrust-chamber-temperature rise
rate during idle mode: **6°F/sec**, at high-oxidizer (45 psia) / low-fuel (27 psia) pump-inlet
conditions.

**Real reliability/failure data**: three of the eleven firings were prematurely cut off by
the **vibration safety cutoff system** (>150 g rms, 960–6000 Hz) during transition from idle
to main stage, specifically when **liquid fuel was present at the injector during oxidizer-
dome-prime** (chamber pressure ≈100 psia) — a real, repeated failure mode tied to propellant
*phase* (liquid vs. superheated/gas) at the injector during the idle→main-stage transition,
not a component defect. One firing (07A) showed an apparent **+7% chamber-pressure
measurement error** suspected caused by icing of the Pc measurement tap (cross-connected to
a purge line) — a real instrumentation-caveat worth remembering when trusting any single
Pc-derived performance number from a cryogenic-engine altitude test.

## Design method

Not a design-method source — this is a test report, not a design monograph. No new sizing
equations or design criteria are given; the value here is entirely **real hardware
parameters and real operational/sequencing precedent** for a tap-off-cycle engine family
(J-2/J-2S), directly comparable in kind to `[NK-33-Mod]`'s real-engine data for staged
combustion or `[KBKhA]`'s real RD-0110/RD-0124 tables for GG vs. staged combustion.

## Section map

- §I Introduction: p.1 (leaf 9) — read.
- §II Apparatus (2.1 Test Article incl. 2.1.1 J-2S Rocket Engine component descriptions,
  2.2 Test Cell, 2.3 Instrumentation): p.1–5 (leaf 9–14) — read in full for 2.1.1; 2.2/2.3
  skimmed.
- §III Procedure: p.5–6 (leaf 14–15) — skimmed.
- **§IV Results and Discussion (per-firing narrative, 4.2.1–4.2.11): p.6–16 (leaf 15–27) —
  firings with usable performance numbers (06A, 07B, 07C) read in full; remainder (07A, 11A,
  11B, 11C, 15A, 15B, 15C) skimmed for idle-mode/tapoff-specific findings only.**
- §V Summary of Results: p.16–17 — not read.
- References: p.17 — not read.
- Appendix I Illustrations (Figs. 1–53): p.21–66+ (leaf 29–74+) — schematics (Figs. 3–7) read
  in full for captions/labels; performance-trace plots (Figs. 10–53) captions/axis-labels only,
  plotted curves not OCR-extractable.
- Appendix II Tables (I major components, II orifices, III/IV modifications): p.72–77+
  (leaf 78–83) — Table I and Table III read; Table II/IV not read.
- Appendix III Instrumentation List: p.86+ (leaf 93–115+) — skimmed for sensor full-scale
  ranges only (e.g. fuel turbine inlet temperature sensor range -300 to 2400°F).
- Appendix IV (performance-calculation method, referenced but page range not confirmed) —
  not read; would likely resolve the Pc-tap-location question flagged above.

## Caveats

- **This is a development/troubleshooting test report, not a clean data set**: many of the
  eleven firings failed to produce usable idle-mode performance data (superheated propellant
  at flowmeters, unstable flow, premature cutoffs) — the table of main-stage numbers above is
  drawn from only 3 of 11 firings; the rest either lack a clearly stated performance number or
  were skimmed rather than deep-read for this note.
- **Chamber-pressure tap-location ambiguity** (flagged above): the ~1180–1280 psia Pc values
  reported for main-stage firings are notably high vs. commonly-cited J-2S nominal chamber
  pressure; don't treat as a directly comparable "rated Pc" figure without resolving the tap
  location (Appendix IV, not read this pass).
- **1969-era hardware, uprated-development engine**: J-2S never flew operationally (Saturn
  program wound down before it was needed) — treat this as real hardware data from a mature
  ground-test program, not flight-proven-in-service data like the baseline J-2.
- OCR quality is mixed: body-text paragraphs are clean, but tables (esp. Table I part-number
  lists and the Appendix III instrumentation list) are visually garbled by OCR column-merging
  — numeric test-point data quoted above came from clean narrative-paragraph text, not from
  reconstructing a garbled table.
- Figures are plots; OCR captures captions/axis labels only, not plotted values (same
  limitation as `[Marquardt-5981]` and other scanned reports in this reference set).
