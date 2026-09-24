# The J-2X Upper Stage Engine: From Design to Hardware

## Identity

Thomas Byrd (NASA MSFC, Ares Projects Office, Deputy Manager, J-2X Upper Stage Engine
Element), *The J-2X Upper Stage Engine: From Design to Hardware*, AIAA Joint Propulsion
Conference paper, July 2010 (program-status paper; presentation-deck version appended after
the paper text in the same PDF). `literature/AIAA JPC 2010 - The J-2X Upper Stage Engine From Design to Hardware.pdf` (NTRS 20100034922; 36 PDF leaves; leaf 0-17 =
the written paper, leaf 18+ = a companion briefing-slide deck covering similar ground more
tersely, with some numbers not in the paper text itself). Tag: `[J2X-Overview]`.

## Character

A NASA program-status/overview paper (not a design-criteria monograph or a physics/
correlation source) on the J-2X engine — a modern (2006-2010-era) gas-generator-cycle
LOX/LH2 upper-stage engine developed for the Constellation program's Ares I/Ares V vehicles,
explicitly built on the **J-2/J-2S/RS-68 heritage lineage** (same engine family as
`[AEDC-J2S]`, already in this reference set). J-2X never flew (Constellation was cancelled),
but the engine reached full hardware/hot-fire-test maturity, so this is real, if
late-in-development, hardware data — comparable in kind to `[AEDC-J2S]` or `[NK-33-Mod]`,
one program's real numbers, not a cross-engine survey.

Structure: Abstract/Introduction, J-2X Mission and Requirements, Heritage as Point of
Departure, Development and Production, Development Testing Highlights (turbopump,
gas-generator, nozzle-extension, valve/avionics subsections), Manufacturing Highlights, Test
Facilities, Conclusion — followed by a slide-deck restatement with a compact "Design
Overview" summary slide (the single most useful page for real numbers, see below).

## This note's extraction scope

Read in full (short paper, 36 leaves total, no extraction-scope tradeoff needed): the
complete written paper (leaf 0-17) and the slide deck's "Design Overview"/"Engine
Hardware" summary slides (leaf 19-20), which give the most compact real-number table in the
whole source. The remaining slide-deck pages (leaf 21+, mostly bare test-photo captions with
no additional numeric content) were skimmed only.

## Key results — real J-2X design/program numbers

**Top-level design point** `[J2X-Overview, Design Overview slide, leaf 19]`:
- Vacuum thrust: **294,000 lbf (1307 kN)**; specific impulse: **448 s (minimum)**; mixture
  ratio: **5.5**; run duration: **500 s**; dry weight: **5,535 lbm (2,516 kg)**; envelope:
  **120 in dia × 185 in long**; life: **8 starts / 2,600 s**. Ares V variant additionally
  requires **on-orbit restart at 82% thrust, MR 4.5** (a throttled/off-nominal-MR restart
  point) — a real example of a single engine design needing two distinct rated operating
  points for two different missions.
- Development testing exercised **274,000 lbf and 294,000 lbf** thrust levels (primary) and
  a **secondary/GG-test thrust level of 240,000 lbf** noted separately in the workhorse-GG
  discussion — i.e. real multi-point throttling was part of the qualification envelope, not
  just the single rated point.

**Cycle architecture, confirmed real hardware** `[J2X-Overview, Design Overview slide, leaf
19; body text, leaf 3-6]`: **LOX/LH2 gas-generator cycle** with **series turbines** (fuel
turbine then oxidizer turbine, matching `[AEDC-J2S]`'s real J-2S series-turbine finding on
the same engine lineage) and **throttle capability implemented via a LOX turbine bypass
valve** (a real, named hardware solution — the "Oxidizer Turbine Bypass Valve," OTBV — for
GG-cycle throttling, distinct from a propellant-utilization trim valve). Helium spin start
(pressurized-gas turbine spin-up, not a solid-propellant starter like J-2S's SPTS) with
on-orbit restart capability. Open-loop, pneumatically-actuated valves; onboard engine
controller with health monitoring.

**Chamber/nozzle construction, real hardware** `[J2X-Overview, Design Overview slide, leaf
19; body text, leaf 10-11]`: **tube-wall regeneratively-cooled main nozzle** plus a **large
passively-cooled metallic nozzle extension boosted/cooled by turbine exhaust gas (TEG)** —
i.e. the same regen-nozzle + TEG-film-cooled-extension architecture already anchored in
`topics/07-dump-cooling.md`/`topics/06-cooling-and-heat-transfer.md` via Vulcain HM-60/J-2,
now with a third, more recent (2010) real data point. The nozzle extension is **10 ft
diameter at the exit, ~8 ft long** — among the largest passively-cooled nozzle extensions
built at the time — peak operating temperature **~2,000°F**, coated (a commercially
available thermal-emissivity coating, tested on Haynes 230 panels machined to the extension's
actual orthogrid wall geometry) for a **1,600 s / 6-start service life** (certified to 2×
that: 3,200 s / 12 starts). Nozzle side-loading from asymmetric start/shutdown pressure
distribution was characterized via subscale cold-flow wind-tunnel testing — a real
engineering concern for any regen-to-radiation/dump-cooled nozzle transition, corroborating
`[SP-8120]`'s general side-load/retaining-band concerns already in `topics/12`.

**Turbopump, real hardware/design decisions** `[J2X-Overview, body text, leaf 8]`: point of
departure was the **J-2S Mk 29 turbopump design** (same real hardware family as
`[AEDC-J2S]`). Real design changes made from that heritage baseline: (1) **hydrostatic
bearings adopted for the fuel turbopump** after CFD showed low rotordynamic stability
margins with the heritage bearing design — first proven on the USAF/NASA Integrated
Powerhead Demonstration (IPD) engine (~30 test firings, 2005-2006) but not flown until J-2X;
(2) the **LOX pump inducer was changed from the heritage shrouded 3-bladed design to a more
contemporary unshrouded 2-bladed design** after subscale water-flow testing — a real,
concrete inducer-blade-count/shrouding change driven by test data, useful context for
`engine_designer`'s own inducer-related NPSH/suction-specific-speed discussions (topic 09/
the earlier NPSH plan).

**Gas generator, real hardware** `[J2X-Overview, body text, leaf 7]`: a **43-element**
workhorse GG injector was iterated (tested with straight and 90°-elbow chamber
configurations, and against 5 different hot-gas-discharge-duct lengths to the fuel turbine)
specifically to resolve a **real combustion-stability issue in the GG-to-turbine discharge
duct** — a concrete example of GG *duct* geometry (not just the GG chamber/injector itself)
being a combustion-stability variable requiring physical iteration, not just analysis.

**Real program-scale context** `[J2X-Overview, body text, leaf 6]`: heritage J-2 accumulated
**~3,000 single-engine firings, 419 cluster tests, 110 duration tests, 470,000+ seconds**
hot-fire time historically; J-2X's own planned test program was **223 engine tests** (132
development + 32 certification + 7 flight-engine + 15 stage-integration + 17 contingency +
20 rework) — a real comparison point for how much a "heritage-derived new engine" program
scales down from the original full development campaign.

## Design method

Not a design-equation or correlation source — a program-status paper. Its value is entirely
**real, recent (2010) hardware design-point numbers and real engineering decisions** for a
GG-cycle LOX/LH2 upper-stage engine in the direct J-2/J-2S lineage, useful primarily as (a) a
third real anchor for the tube-wall-regen + TEG-film-cooled-extension architecture already
in `topics/06`/`topics/07`, and (b) a modern counterpart to `[AEDC-J2S]`'s 1970-vintage
series-turbine/tap-off findings, confirming the series-turbine arrangement persisted into a
2010-era GG-cycle (non-tap-off) redesign of the same pump heritage.

## Section map

- Abstract/Introduction, J-2X Mission and Requirements, Heritage as Point of Departure:
  leaf 0-2 — read.
- Development and Production: leaf 3 — read.
- Development Testing Highlights (turbopump: leaf 6-9; gas generator: leaf 6-7; nozzle
  extension: leaf 10-11; valves/avionics: leaf 12): read in full.
- Manufacturing Highlights: leaf 13-14 — read (real hardware-completion status, not
  technical data — e.g. "1,500 of 1,600 engine drawings released" — skimmed for content,
  no numbers pulled into Key results).
- Test Facilities (SSC stands A1/A2/A3): leaf 15-16 — skimmed (facility-readiness status,
  not engine design data).
- Conclusion: leaf 17 — read.
- Slide deck (title slide, Design Overview, Engine Hardware, then bare test-photo captions):
  leaf 18-35 — Design Overview (leaf 19) and Engine Hardware (leaf 20) slides read in full
  (the compact real-number summary quoted above); remaining photo-caption slides skimmed
  only, no additional numeric content found.

## Caveats

- **J-2X never flew** (Constellation program cancelled before flight) — treat all numbers as
  real, tested, late-development-stage hardware data, not flight-proven-in-service data like
  the baseline J-2 or (partially) J-2S.
- **Program-status paper, not an engineering-analysis paper** — no derivation, correlation,
  or sizing method is given anywhere in this source; every number above is a stated design
  point or test result, not something independently derivable from the text.
- The slide deck (leaf 18+) duplicates and lightly extends the written paper rather than
  adding a fully independent data set — the "Design Overview" slide's numbers were the only
  material not already implicit in the paper's own text.
- No "sandwich"/dual-wall chamber-construction content (J-2X uses tube-wall, not sandwich,
  construction) — flagged for completeness since this source was pulled in the same
  literature batch as sources specifically covering that topic.
- OCR/text quality: clean, born-digital PDF (AIAA conference paper + NASA slide deck), no
  reconstruction caveats needed for any quoted number.

## Regen passage geometry data (2026-09-23 re-read)

Keyword search of all 36 leaves (tube, channel, coolant, regen, jacket, MCC, hot wall, land).
Leaf numbers 0-based as elsewhere in this note. **No dimensional or coolant-state numbers
exist in this paper**; what it does establish is construction and circuit-component topology:

- **MCC = channel wall (slotted liner), not tubes** `[J2X-Overview, body text, leaf 13]`: "The
  jacket consists of three machined forgings electron beam (EB) welded together, further
  machined, then plated ... The **liner has been fully slotted** and plated. All components
  are prepared for **Hot Isostatic Press (HIP)** assembly" - i.e. a milled-slot liner
  HIP-bonded to a forged jacket; slide leaf 28 captions the "MCC Jacket - note the machined
  coolant holes" and "MCC Throat Support Halves / Shear Pins (5 of 12 complete)".
- **Regen nozzle = brazed tube wall with 3 flat bands** `[J2X-Overview, body text, leaf 13;
  slide leaf 29]`: "All **three flatbands** around the braze tubes were ready for plating ...
  the regenerative nozzle tubes were fully alloyed for braze"; "forward base ring";
  "E10001 tube stack and flat bands" photo.
- **Separate MCC coolant feed is implied, not described** `[J2X-Overview, body text, leaf 13]`:
  a named **"MCC coolant duct"** is listed among propellant ducts bent to final contour -
  evidence the MCC coolant is ducted separately from the nozzle tube bundle, but no
  flow split, direction or pass count is given.
- Nozzle extension: passively (radiation + TEG film) cooled, injected supersonically via a
  manifold; turbine exhaust manifold base ring is a separate part (leaf 10-11, 13).

**NOT in this paper**: MCC channel count/width/depth/land/hot-wall thickness; nozzle tube
count, diameter or wall; coolant flow or fuel fraction; jacket inlet/outlet T or P; coolant
velocity; circuit flow directions.
