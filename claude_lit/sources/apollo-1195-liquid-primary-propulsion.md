# Apollo Working Paper No. 1195 — Apollo Spacecraft Liquid Primary Propulsion Systems

## Identity

G. L. Spencer, J. C. Smithson et al. (Propulsion Analysis Section), *Apollo Spacecraft
Liquid Primary Propulsion Systems*, NASA Program Apollo Working Paper No. 1195, Manned
Spacecraft Center, Houston, February 7, 1966. NTRS accession 19700026405.
`literature/Apollo Working Paper 1195 - Apollo Spacecraft Liquid Primary Propulsion
Systems.pdf` (45 PDF leaves; printed pages start at leaf 5 = p.1, run through p.40 at
leaf 44 — printed page N = PDF leaf N+4 for the body). Tag: `[ApolloPP-1195]`.

## Character

A short (9 pages of running text + 31 pages of figures, no appendices) internal MSC
**familiarization/survey** document, not a design monograph or test report — closer in
spirit to a condensed textbook chapter than to `[H1-Man]`/`[F1-Man]`'s deep hardware
manuals. It exists to give a reader unfamiliar with the Apollo spacecraft a compact tour
of its three **primary liquid propulsion systems**: the Service Propulsion System (SPS,
Aerojet-General, 21,500 lbf fixed-thrust, in the Service Module), and the two Lunar
Excursion Module (LEM) engines — the Descent Propulsion System (DPS, TRW Systems,
throttleable 1050–10,500 lbf) and the Ascent Propulsion System (APS, Bell Aerosystems,
fixed 3500 lbf). All three are **pressure-fed, ablatively-cooled, hypergolic
N2O4/Aerozine-50 (50% UDMH / 50% hydrazine)** engines — directly on-topic for this
project's existing `TR341_Config.cfg` (a TRW-style hypergolic pressure-fed pintle
lander thruster) and for `engine_designer/`'s pressure-fed-cycle support. This is the
first source in `claude_lit/` giving **real Apollo-program hypergolic-pressure-fed
engine data** (prior hypergolic/pressure-fed coverage elsewhere in the reference set is
generic).

The document's value here is almost entirely **Table I** (a dense parameter table
comparing all three engines side by side: thrust, MR, Pc, materials, injector type,
system pressures, dimensions, Ae/At, dry weight, burn time, TVC) plus real qualitative
design-philosophy statements (why hypergolic/ablative/pressure-fed/redundant was chosen)
and labeled figures giving real injector-barrier-cooling mixture ratios and real ablative
liner ply layups that Table I's summary numbers don't capture.

## This note's extraction scope

Read in full: all running text (leaf 5–11, printed p.1–8 — Mission Requirements, Design
Philosophy, Basic Features, Pressurization and Propellant Feed Systems,
Chamber-Injector Compatibility and Ablation, SPS Operation, DPS Operation, APS
Operation) and Table I (leaf 12–13, printed p.9). All 31 figure pages (leaf 14–44) were
extracted via `get_text()` (mostly blank — these are photos/line-art with only a
caption line of OCR-able text) and a representative subset (11 of the 31) rendered to
PNG and viewed directly to check for labeled dimensional/material data a caption alone
wouldn't carry: Fig. 11–12 (LEM descent/ascent engine photos — no data, decorative),
Fig. 17 (descent engine cross section, ablative-section/extension boundary labeled but
undimensioned), Fig. 18 (**ascent engine cross section — real ablative-liner ply
material callouts**, see Key results), Fig. 19 (**SPS injector cross section — baffle
hub/pattern-between-baffles confirmed**), Fig. 20 (**ascent engine injector orifice
plate — real barrier-zone MR = 1.05 label**), Fig. 21 (**descent engine variable-area
injector detail — moving-sleeve/annular-fuel-orifice/impingement-zone labels,
pintle-like mechanism confirmed**), Fig. 26–27 (descent engine flow-control valve/
system — rack-and-pinion shutoff, cavitating-venturi throttle valve, propellant-
temperature-compensation actuator labeled, no new numbers), Fig. 28 (**descent oxidizer
flow-control valve exploded view — explicitly labeled "Pintle Assembly"**). The
remaining ~20 figure pages (SPS/LEM whole-vehicle photos, pressurization-system
schematics for all three engines, SPS thrust-chamber/nozzle-extension figures, ascent
engine flow control) were not rendered/viewed — their captions (extracted via
`get_text()`) are in the Figures list on leaf 3–4 and none appeared, from caption text
alone, likely to carry data beyond what Table I already states. Given the document's
short length (9 real pages of text) this counts as an essentially-complete read of the
substantive content.

## Key results

**Design philosophy (real rationale, not just numbers)** `[ApolloPP-1195 p.2]`: all
three engines share four deliberate reliability-driven design choices, explicitly
crew-safety-motivated: (1) **storable propellants** at ambient temperature — avoids
cryogenic long-term-storage/zero-g venting problems; (2) **ablative combustion
chambers** — chosen specifically for "rugged nature... and high resistance to sudden
failure" (i.e. graceful degradation vs. burn-through, not just simplicity); (3)
**pressure-fed** — eliminates turbopump complexity; (4) **redundant components** on
every moving part in the pressurization/feed system, so a single failed-open or
failed-closed valve doesn't abort the mission — achieved via a **series-parallel valve
topology**: a failed-open valve is caught by a second valve in series, a failed-closed
valve is bypassed by a second valve in parallel, with paired oxidizer/fuel valves
mechanically linked to one actuator for correct relative timing.

**Table I — real Apollo engine specifications** `[ApolloPP-1195 Table I, p.9]`:

| Parameter | SPS (Aerojet-General) | LEM Descent (TRW) | LEM Ascent (Bell Aerosystems) |
|---|---|---|---|
| Thrust, lbf | 21,500 | 10,500 to 1050 (throttleable) | 3500 |
| Mixture ratio | 2.0 | 1.6 | 1.6 |
| Chamber pressure, psia | 100 | 100 (text) / *"100"* col header ambiguous, see caveat | 150 |
| Propellants | N2O4 / 50-50 UDMH-hydrazine (all three) | | |
| Chamber & nozzle material | Ablative — high-silica/phenolic | Ablative — high-silica/phenolic | Ablative — high-silica/phenolic |
| Nozzle extension material | Radiation-cooled, columbium, Ae/At = 6→62.5 | Radiation-cooled, columbium Ae/At=6→40, titanium Ae/At=40→62.5 | **Fully ablative** (asbestos/microballoon) — no radiation-cooled extension |
| Injector material | Aluminum | Inconel | Aluminum |
| Injector pattern | Concave/baffled, unlike-doublet | Coaxial/variable-area, fuel-sheet/radial-oxidizer | Flat/baffled, triplet (2 fuel + 1 ox), unlike-doublet |
| Film-cooling fraction | 7% of total flow (showerhead) | none stated ("NA" — variable-area injector has no distinct film-coolant flow) | 29% of total flow (unlike-doublet) |
| Tank pressure, psia | 175 | 225 | 210 |
| Interface pressure, psia | 165 | 210 | ~205 (garbled) |
| Injector Δp (ox/fuel), psia | ox 44 / fuel 47 | variable, 110→11 | not tabulated clearly (OCR-garbled row) |
| Overall length, in | 62 | 67 | 51 |
| Dry weight, lb | 650 | 350 | 210 |
| L* (chamber length), in | ~34 (OCR-uncertain digit) | 36 | 24 |
| Contour, % bell | 70 | 67 | 72 |
| Ae/At (expansion ratio) | 62.5 | 47.5 | 45.4 (OCR-uncertain last digit) |
| Max chamber dia, in | 18 | 14 | 8 |
| Throat dia, in | 12 | 8 | 5 |
| Exit dia, in | 98 | 58 | 31 |
| Throat area, in² | 122 | 54 | 16 |
| Exit area, in² | 7595 | 2664 | 750 |
| Max mission burn time, sec | 500 | 1030 | 465 |
| Number of starts | 8 | 2 | 2 |
| TVC | Gimballed, ±8.5° pitch / ±6° yaw | Gimballed, ±6° pitch / ±6° yaw | None (fixed) |

(Table transcribed from OCR'd columns; several individual digits are uncertain due to
column-merge OCR garbling — cross-check any single cell against the PDF leaf 12–13
before using it as a hard design input. The MR/thrust/material/injector-type/burn-time/
TVC entries above are the ones this note is confident in; a few numeric cells noted
"OCR-uncertain" should be re-read from the source image if precision matters.)

**Chamber-injector compatibility / ablation control** `[ApolloPP-1195 p.3-4]`: states the
general design problem directly — high performance requires high combustion
temperature, which drives high ablation rates, which reduces nozzle area ratio
(erosion), degrades performance, and forces a thicker/heavier ablative chamber. The
universal fix across all three engines is a **fuel-rich barrier layer isolating the hot
combustion core from the chamber wall**, implemented differently per engine:
- SPS: a ring of **showerhead fuel orifices** adjacent to the chamber wall (7% of total
  flow, per Table I).
- LEM ascent: a **low-mixture-ratio unlike-doublet ring** adjacent to the wall (29% of
  total flow) — confirmed by Fig. 20's real label: **"E-1 CONFIGURATION, BARRIER O/F =
  1.05"** on the ascent-engine injector orifice plate, i.e. the barrier zone runs at
  MR≈1.05 against a bulk/core MR of 1.6 — a real, specific number for a fuel-rich
  cooling-barrier mixture ratio on a hypergolic engine, useful precedent for any
  `engine_designer` film-cooling-ring MR choice on a hypergolic pair.
- LEM descent: because of its **variable-area concentric injector** (a moving sleeve
  varying the annular fuel-orifice open area in step with a cavitating-venturi throttle
  valve, confirmed in Fig. 21/26–28), "no specific portion of the fuel can be considered
  as the film coolant" — i.e. film cooling is inherent to how the variable geometry
  works rather than a separately-metered fraction, and the report explicitly does not
  give it a %-of-flow number (Table I marks this cell "NA").

**Pressurization architecture, per engine** `[ApolloPP-1195 p.4-7]`:
- **SPS**: helium stored ambient-temperature at **4000 psia** in two spherical tanks,
  isolated by continuous-duty solenoid valves, regulated by two parallel dual-stage
  regulators (only one of the four regulator stages normally active — the other three
  are pure redundancy), heat-exchanger-conditioned to approach tank propellant
  temperature before entering the propellant tanks. Fuel/oxidizer each in two
  series-connected cylindrical tanks (an upstream "storage tank" + downstream "sump
  tank" with a zero-gravity retention reservoir at the sump tank's feed-line outlet).
- **DPS**: helium stored **cryogenically** in a vacuum-jacketed dewar at ~100 psia/10°R
  initial, reaching ~1250 psia/32°R at operational conditions via heat-leak + standby
  time — explicitly a weight-saving trade (denser cold helium storage) accepted at the
  cost of pressurization-system complexity (two heat exchangers: one external using
  fuel as the heat source, one internal to maintain storage-vessel pressure). Fuel/ox
  each in two parallel tanks with slosh baffles and crossover lines.
- **APS**: helium stored ambient at **3500 psia** in two spherical tanks, each behind
  its own one-shot explosive shutoff valve (fired once, pre-first-start) rather than a
  reusable solenoid valve as in SPS/DPS — a real design difference reflecting the APS's
  single-mission-segment/no-restart-needed role (2 starts total per Table I) vs. SPS's
  8-start requirement.

**LEM descent engine throttling mechanism, real hardware detail**
`[ApolloPP-1195 p.6, Fig. 21/26-28]`: a **variable-area concentric (pintle-style)
injector mechanically linked to cavitating-venturi flow-control valves** — confirmed by
Fig. 28's explicit label "**Pintle Assembly**" on the oxidizer flow-control-valve
exploded view. When throttling down, the throttle actuator simultaneously reduces the
propellant-flow-control-valve flow area AND moves the injector orifice area, keeping
injection velocity roughly constant as flow drops (i.e. deliberately avoiding the low
injection-velocity/poor-atomization problem a fixed-geometry injector would have at deep
throttle). **Below 70% thrust, the flow control valves cavitate**, which decouples
propellant flow rate from downstream pressure changes — i.e. cavitation is used
*deliberately* as a flow-regulation mechanism at the low end of the throttle range, not
treated as a failure mode. Engine start/shutdown can be commanded at any throttle
setting. This is a real, early (1966) precedent for a pintle/cavitating-venturi
combination doing exactly the kind of deep, wide-range throttling
(10,500→1050 lbf, 10:1) that `[Casiano-Throttling]` catalogs for later engines (LMDE
10:1 — this LEM descent engine almost certainly *is* the "LMDE" `[Casiano-Throttling]`
cites, confirming that entry's real mechanism).

**Ablative liner real material callouts, LEM ascent engine** `[ApolloPP-1195 Fig. 18]`
(figure-label transcription, not running text — treat as illustrative real material
names, not a verified BOM): chamber/throat region built up as **asbestos/2223 phenolic-
silica felt, 0° tape wrap** with **HT-427 bond**, an **Irish Refrasil/EC-201 phenolic,
50° tape wrap**, **"302" bond**, transitioning at the nozzle-extension boundary to
**filament-wound glass roving/epoxy-novolac** with a **302-glass-supported (.002")
film bond**, a **tension-butt glass tape wrap/2223 phenolic** exit section, and an
**asbestos/V-204 phenolic-silica-spheres felt rosette** insulation detail near the
throat. This is a real, if terse, snapshot of a 1960s ablative-liner ply schedule
(multiple distinct ablative/insulative material systems used zone-by-zone rather than
one uniform material) — useful corroboration for `claude_lit/topics/06b`'s ablative-
material discussion, though not detailed enough (no ply thickness/density/erosion-rate
numbers) to derive a sizing method from.

**Injector real hardware detail** `[ApolloPP-1195 Fig. 19-21]`: the SPS injector
(Fig. 19) is confirmed baffled with a distinct **"baffle hub"** and an "injector pattern
between baffles" callout — i.e. the unlike-doublet elements are arranged in the gaps
between radial acoustic baffles, standard combustion-stability practice. The descent
engine injector (Fig. 21) shows a **moving sleeve** riding over an **annular fuel
orifice**, with **oxidizer orifices** arranged around it and an explicit
**"impingement zone"** label where fuel and oxidizer streams meet — real geometric
confirmation of a pintle-type unlike-impinging (not coaxial-swirl) atomization
mechanism, despite Table I's own summary calling the descent injector pattern
"coaxial/variable area."

## Design method

Not a design-method source. No sizing equations, correlations, or worked examples are
given anywhere in the document — it is a descriptive survey. The value here is entirely
**real 1966-vintage Apollo-program engine parameters and design-rationale statements**
for three pressure-fed hypergolic ablative engines, comparable in kind to how
`[NK-33-Mod]`/`[AEDC-J2S]`/`[H1-Man]`/`[F1-Man]` supply real numbers for pump-fed
engines elsewhere in this reference set — this is the first pressure-fed hypergolic
real-engine data point in `claude_lit`.

## Section map

- Untitled intro / Mission Requirements: p.1 (leaf 5) — read.
- Design: Philosophy, Basic features, Pressurization and Propellant Feed Systems,
  Chamber-Injector Compatibility and Ablation: p.2–4 (leaf 6–8) — read in full.
- Service Propulsion System / Operation: p.4-5 (leaf 8-9) — read in full.
- Descent and Ascent Propulsion Systems / Descent Propulsion System Operation / Ascent
  Propulsion System Operation: p.5-8 (leaf 9-11) — read in full.
- Table I — Apollo Spacecraft Engine Specifications (2 pages): p.9 (leaf 12-13) — read
  in full, several individual cells OCR-uncertain (see Caveats).
- Figures 1-31 (contents list on leaf 3-4; figure pages leaf 14-44): captions extracted
  via `get_text()` for all; 11 of 31 rendered to PNG and visually inspected (Fig. 11,
  12, 17, 18, 19, 20, 21, 26, 27, 28 — see extraction scope above for what each showed);
  remaining ~20 (whole-vehicle photos, SPS/DPS/APS pressurization-system schematics not
  independently informative beyond running text, SPS thrust-chamber/nozzle-extension
  figures, ascent-engine flow-control schematic) not rendered.
- No appendices, references section, or index in this document.

## Caveats

- **This is a survey/familiarization paper, not a design or test report** — it gives no
  derivations, no test data, no uncertainty bounds, and states specifications as flat
  numbers with no source citation of its own (presumably drawn from contractor design
  data circa 1966, pre-flight — treat all Table I numbers as **design/nominal values,
  not flight-verified performance**, since this predates any Apollo flight).
- **OCR quality is poor and inconsistent** — this is a 1966 typewriter-font mimeograph-
  style document scanned to PDF, and character substitution (0/O, 1/l/I, rn/m) is
  pervasive, worse in Table I's dense multi-column numeric layout than in running text.
  Several individual Table I cells (Pc units-of-agreement across columns, a couple of
  Ae/At last digits, the ascent-engine injector-Δp row) could not be read with full
  confidence from the extracted text alone; this note flags each such cell inline
  above rather than silently rounding or guessing. Re-render the leaf-12/13 page at
  high DPI and inspect directly before treating any single flagged digit as exact.
- **No figure gives a dimensioned engineering drawing** — all figures are either
  photographs (no data) or labeled schematic/exploded-view line art (component names
  and a few flags like the barrier-MR label, but no dimensions, tolerances, or
  material-thickness numbers). This document cannot support a chamber/injector/valve
  *sizing* method the way `[SP-8087]` or `[Bazarov]` can — it only supplies real
  top-level parameters and real material/mechanism *names*.
- **Scope is narrow by design**: covers only the SPS/DPS/APS *primary* propulsion
  systems, explicitly excluding the Reaction Control System (RCS) thrusters (mentioned
  only in passing, as a settling-thrust source for the SPS) and all non-propulsion
  spacecraft systems.
- The descent-engine Table I row calling the injector pattern "coaxial/variable area"
  reads as somewhat inconsistent with Fig. 21's own impingement-zone/annular-orifice
  detail (more pintle-like than coaxial-swirl in the conventional sense) — flagged
  above, not resolved; likely a terminology looseness in the era rather than an error,
  but worth keeping in mind if citing "coaxial" as the descent engine's injector
  taxonomy elsewhere.
- No mention anywhere in the document of turbopumps, regenerative cooling, or any
  pump-fed hardware — entirely consistent with all three engines being pressure-fed,
  but noted so a reader doesn't expect turbopump data here.
