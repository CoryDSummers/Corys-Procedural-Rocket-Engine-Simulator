# [Gubanov-1991] — USSR Main Engines for Heavy-Lift Launch Vehicles: Status and Direction

## Identity

B. I. Gubanov (Chief Designer of the Energia Heavy-Lift Vehicle, Soviet Union), *USSR Main
Engines for Heavy-Lift Launch Vehicles: Status and Direction*, AIAA Paper 91-2510, 27th
Joint Propulsion Conference, June 24-26 1991, Sacramento CA. `literature/AIAA-1991-2510.pdf`
(6 PDF pages, 0-indexed leaves 0-5, no offset — leaf N = printed page N+1). Tag:
`[Gubanov-1991]`.

## Character

A short conference status/policy paper, not a technical design monograph — written by the
Energia vehicle's own chief designer, giving real specification tables for the RD-170,
RD-120, and RD-0120 engines (all flown on Energia/Zenit/Buran), plus a forward-looking
description of a **three-propellant engine concept** (tripropellant, oxygen/hydrogen/
kerosene — the RD-701 lineage), a family-lineage/reliability-philosophy discussion, and a
short failure-mode/emergency-protection-system discussion. OCR quality is rough (many
character-substitution errors — "RD-I70" for "RD-170", "kdsq cm" for "kg/sq cm", etc.) but
unambiguous once patterns are recognized.

**Sandwich-wall construction — explicitly NOT covered.** The user asked this batch of
literature to be reviewed with attention to "Russian sandwich construction." This paper does
**not** use the word "sandwich" anywhere, and its only description of chamber-wall
manufacture is a single generic sentence per engine: for RD-170, "The chamber is an
inseparable unit and manufactured with use of brazing and welding processes. It consists of
a main injector, a combustion chamber and a nozzle." For RD-0120: "The chamber is a
brazed-welded unit and consists of a main injector, a combustion chamber and a nozzle." No
cross-section, no layer structure, no comparison to tube-wall/channel-wall/milled-wall
construction, no drawing or figure of the wall itself is given or described in text. **This
source does not deliver what the user is looking for on that specific topic** — treat this
as a confirmed miss, not a partial answer: whatever "Russian sandwich construction" refers to
technically (two thin face-sheets with a corrugated/perforated core brazed between them,
forming coolant channels — a real historical Soviet chamber-wall technique used on some
engines) needs a different, more technical source (a materials/manufacturing paper, not a
program-status paper like this one).

## Key results — Real engine specifications

**RD-170** (four-chamber, oxidizer-rich staged combustion, LOX/kerosene, Energia/Zenit first
stages) `[Gubanov-1991 p.2]`:
- Thrust sea level / vacuum: 740 / 806 tonnes-force
- Isp sea level / vacuum: 309 / 337 s (table OCR is corrupted here — printed as
  "309 331... 250" with a stray "250" that doesn't parse cleanly to a third value; treat the
  309/vacuum-Isp pairing as the reliable read, cross-check against other RD-170 sources
  before using the middle number)
- Combustion chamber pressure: not cleanly OCR'd on this page (the pressure row is jumbled
  with the Isp row) — do not use a Pc number from this source for RD-170; use `[Ch12-Materials]`
  or another already-distilled source instead.
- Dry mass: 9755 kg
- Developed by Energomash Design Bureau, 1974-1990, under V.P. Glushko and V.P. Radovsky.
- Reusable up to 10 flights (or expendable variant). 804 engine firing tests (93,300 s total
  fire duration) prior to Jan 1 1991; 22 engines flight-tested on Zenit/Energia.
- Engine structure: 4 chambers, 1 HPTP (single shaft, axial single-stage reaction turbine +
  2-stage screw-centrifugal fuel pump + screw-centrifugal oxidizer pump), 2 low-pressure
  boost turbopumps (fuel and oxidizer, each single/two-stage hydraulic turbine driven off
  downstream HPTP flow), 2 preburners (oxidizer-rich generator gas, brazed-welded
  injector+housing units joined by a separable flange).
- **Cooling**: "The nozzle and the combustion chamber are cooled with full-flow kerosene
  entering the chamber main injector" — i.e. 100% of fuel flow is the regen coolant (a
  closed, full-flow staged-combustion cycle, no dump/bleed fraction), consistent with how
  `engine_designer`'s ORSC cycle model should already treat coolant flow fraction (no
  separate number given here beyond "full-flow").

**RD-120** (single-chamber, oxidizer-rich staged combustion, LOX/kerosene, Zenit second
stage) `[Gubanov-1991 p.2]`:
- Thrust vacuum: 85 tonnes-force; Isp vacuum: 350 s
- Combustion chamber pressure: 112.5 kg/cm² (OCR "112s" — read as 112.5)
- Dry mass: 166 kg
- Length 3870 mm, diameter 1950 mm

**RD-0120** (single-chamber, staged combustion, LOX/LH2, Energia core/second stage — the
Soviet SSME-class engine) `[Gubanov-1991 p.3]`:
- Thrust vacuum: 200 tonnes-force; Isp vacuum: 455 s
- Combustion chamber pressure: 223 kg/cm² (~21.9 MPa, ~3175 psia)
- Dry mass: 3450 kg
- Mixture ratio 6.1 (O/F), ±10% admissible deviation
- Burning time in flight: 500 s; throttling range 45-100%; nozzle area ratio 85.7:1
- Length 2420 mm, nozzle exit diameter... (OCR-jumbled dimension row, not extracted cleanly)
- Developed by Chemical Automatics Design Bureau, 1976-1990, chief designer A.D. Konopatov;
  drew on prior Soviet O2/H2 engines at 7.5 and 40 tonnes thrust plus RD-57 and RD-135
  research programs. ~800 firing tests, 165,000 s total fire duration, prior to Jan 1 1991.
- Engine structure: 1 chamber, HPTP (single shaft, 2-stage axial turbine + 3-stage
  centrifugal fuel pump + 2 oxidizer pumps), LPFTP (2-stage turbine driven by **gaseous
  hydrogen supplied from the combustion chamber coolant channel** — i.e. the regen-heated
  fuel drives the boost turbine, an expander-like bootstrap arrangement layered onto the
  staged-combustion cycle), LPOTP (2-stage axial pump + 2 hydraulic turbines, separate drive
  per stage, driven by LOX after the boost-pump preburner stage), 1 preburner (fuel-rich
  generator gas for HPTP turbine, brazed-welded housing + fuel manifold + injector).
- **Cooling**: "The combustion chamber and the nozzle are cooled with a certain portion of
  hydrogen supplied after the fuel pump" — a *partial* fuel flow, not full-flow like RD-170's
  kerosene cooling (no fraction quantified).

**Three-propellant (tripropellant) engine concept** `[Gubanov-1991 p.5]` (forward-looking
design study, not yet flown at time of writing — RD-701 lineage): dual-mode engine burning
O2+H2+kerosene at max thrust (200 tonnes vacuum, Isp 416 s) for first-stage-equivalent
operation, then switching to O2+H2 only at up to 40% partial thrust (Isp 462 s) for
second-stage-equivalent operation — kerosene is cut off and oxygen flow reduced at mode
transition, chamber pressure drops to ~140 kg/cm² in the second mode (vs. up to 350 kg/cm²
in the first mode). Single common combustion chamber and three-component injector serve both
modes. Cooling: "screening cooldown" (film/screen cooling) with hydrogen consumption up to
5% in the first mode. Turbopumps are oxidizer-rich-cycle (not hydrogen-rich) specifically to
avoid hydrogen-embrittlement cracking of turbopump structural elements at high stress — a
real, explicitly-stated materials-driven cycle choice. This concept engine directly reuses
RD-170's gas-generator/preburner mixing-element design, structural materials, and ignition
coatings.

## Key results — Reliability/failure philosophy (brief, lower priority for engine_designer)

Failure modes are grouped by time-to-develop: (1) fast failures (<0.02-0.04 s, mostly
turbopump — "30% of all failures" — too fast for reactive shutdown, need predictive/early-
diagnosis algorithms instead), (2) very fast structural-ignition/explosion failures
(~0.001-0.01 s, faster than pyrotechnic valve closing time), (3) slower failures (~0.1+ s,
e.g. tank leaks) that conventional performance-parameter-based shutdown logic can catch.
Notable real diagnostic techniques mentioned: electrostatic ignition-onset detection in
oxidizer passages (potential-difference spike between two probes), and running-engine
acoustic-signature monitoring for turbopump rotor blade cracks. Not directly relevant to
`engine_designer`'s scope (no reliability/health-monitoring model exists in the tool), but a
real data point that turbopump failures dominate (30%) LRE failure statistics — corroborates
why `engine_designer`'s existing turbopump-focused design checks (bearing DN, stress margins)
are a reasonable place to invest modeling effort.

## Design method (none — not a design monograph)

This is a status/overview paper, not a design-criteria or sizing-method source. Nothing here
gives a new formula or constant for `engine_designer/physics/*.py`. Its value is entirely
**real specification-table anchors** for RD-170/RD-120/RD-0120 (comparable in kind to
`[NK-33-Mod]`'s or `[KBKhA]`'s real-engine tables), plus the honest negative finding on
sandwich-wall construction above.

## Section map

- p.1: title/abstract (none) + start of RD-170 specification table and description — read
  in full.
- p.2: RD-170 engine-structure list + cooling sentence; RD-120 full specification + brief
  description; RD-0120 introduction/history — read in full.
- p.3: RD-0120 full specification + engine-structure list + cooling sentence; start of
  "Directions in Development of Main Engines" (programmatic trends, expendable vs. reusable
  philosophy) — read in full.
- p.4: launch-vehicle family table (payload vs. engine count for various vehicle classes);
  reliability/failure-classification discussion begins — read in full but low relevance to
  `engine_designer`.
- p.5: reliability discussion continues (diagnostic techniques); three-propellant engine
  concept description — read in full.

Every page of this 6-page paper was read in full; nothing was skimmed or skipped.

## Caveats

- **OCR quality is rough**: numeric tables in particular have jumbled row alignment (e.g.
  RD-170's Isp/Pc rows are interleaved with axis-label fragments from an adjacent figure).
  Treat any single number flagged above as uncertain with appropriate caution; the note says
  explicitly where a number could not be cleanly extracted (RD-170 Pc, RD-0120 nozzle exit
  diameter).
- **Not a materials or manufacturing source**: despite being about "Russian" engines, this
  paper gives no wall-construction technical detail beyond "brazed-welded unit" — do not cite
  this source for anything about sandwich/channel/tube-wall construction technique.
  `[SP-8120]` (already in this reference set) is a Western-practice nozzle-structure source;
  neither it nor this paper covers Russian sandwich-wall construction specifically — that
  remains an open gap in `claude_lit/` after this batch.
- **1991 vintage, USSR-collapse-adjacent**: written months before the Soviet Union's
  dissolution; the "Directions in Development" and reliability sections reflect Soviet-era
  institutional framing (five/twelve-engine batch qualification testing, etc.) that may not
  match current Russian industry practice.
- Real specification numbers here are useful **cross-check anchors** if `engine_designer`
  ever validates an RD-170/RD-120/RD-0120-class design, but note the Pc/dimension gaps above
  before treating any single figure as authoritative — prefer a cleaner-OCR source (e.g.
  `[Ch12-Materials]`, `[KBKhA]`) where the same engine's numbers overlap.
