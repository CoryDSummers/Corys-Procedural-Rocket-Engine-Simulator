# Rocket Propulsion Evolution — Part 8.22: The Rocketdyne J-2 Engine (enginehistory.org)

## Identity

Kimble D. McCutcheon (compiler), *U.S. Manned Rocket Propulsion Evolution, Part 8.22: The
Rocketdyne J-2 Engine*, published on enginehistory.org (Aircraft Engine Historical Society,
Inc.), a section of a long-running multi-part web history of U.S. manned rocket propulsion
(Parts 1 through 9.50, V-2 through the Apollo Guidance Computer). Published 1 Jul 2021,
revised 3 Aug 2022. Saved locally as
`literature/Rocket Propulsion Evolution_ 8.22 - J-2 Engine.html` (single HTML page, ~50 KB,
born-digital text — no OCR needed) plus its image folder
`literature/Rocket Propulsion Evolution_ 8.22 - J-2 Engine_files/` (photos, cutaways, a
flow schematic, a start/shutdown timing chart — mostly small thumbnails linking to
full-resolution originals hosted online, not saved locally). Tag: `[RPE-J2Blog]`.

## Character

**A secondary, enthusiast/historical-society web article, not a primary NASA or Rocketdyne
engineering document.** It is compiled narrative prose (no inline footnotes tying individual
sentences to specific sources) backed by a plain reference list at the end citing real
primary sources: Bilstein's *Stages to Saturn* (NASA SP-4206), Dawson & Bowles' *Taming
Liquid Hydrogen* (NASA SP-2004-4230), two AEDC altitude-test reports (AEDC-TR-68-266,
AEDC-TR-67-86), Hunley's *Technology for U.S. Space-Launch Vehicles*, Kraemer's
*Rocketdyne: Powering Humans into Space*, Mulready's P&W history, and — most importantly for
the ASI failure narrative below — **Rocketdyne's own flight-failure-analysis report**,
*J-2 Engine AS-502 (Apollo 6) Flight Report, S-II and S-IVB Stages, Volumes 2 & 3*
(R-7450-2, Rocketdyne Division, 17 Jun 1968). Because there are no inline citations, it is
not possible to verify which specific claim traces to which reference — but the presence of
the actual Rocketdyne flight-failure report in the bibliography, combined with the
narrative's level of internal technical detail (valve names, timer names, specific duct
sizes) matching real J-2 hardware documentation style, makes the ASI-bellows failure
account in particular read as a faithful summary of that primary report rather than
invented color. Treat every number below as **plausible, second-hand, and unverified
against the primary source it likely came from** — useful for hardware-level detail and
narrative context, not as a citation of record for a physics constant.

Structure: Background, Development, a photo-gallery "walk-around" (captions only), a
component-by-component Description (thrust chamber / injector / ASI / fuel turbopump /
oxidizer turbopump / gas generator / start tank / MFV / MOV / PU valve / pneumatic package /
electrical package), an Operation section (Start Preparations / Start Sequence / Cutoff /
Malfunction Detection), a detailed narrative of the SA-502 (Apollo 6) in-flight ASI failure
and its resolution, References, and a cross-engine "Launch Vehicle Engine Specifications"
comparison table. Read in full (short HTML page, no extraction-scope tradeoff needed). Two
images (`J-2Start,ShutdownSeqT.jpg`, `J-2FlowSch_01T.jpg`) were also viewed directly, but only
small (~200x325 px) locally-saved thumbnails exist — the start/shutdown timing chart's axis
numbers are legible only as an approximate 0-2.0 s (start) / 0-1.0 s (shutdown) time-since-signal
scale with several labeled event rows (Engine Start, MOV/GG valve opens, mainstage), but the
per-event numeric timing values themselves are too small/blurry to read reliably and are
**not** quoted as numbers below — only the qualitative event ORDER, which matches and
confirms the text narrative.

## Key results — real hardware-level detail

**Thrust chamber dimensions** `[RPE-J2Blog, "Description"]`: throat area **170.4 in²**,
nozzle expansion ratio **27:1** (the comparison table separately gives **27.5** — a minor
internal inconsistency, flag both), combustion chamber diameter **18.6 in**, chamber length
(injector face to throat inlet) **8.0 in**, characteristic length L* = **24.6 in**, overall
thrust-chamber length (fuel-pump low-pressure-duct inlet to nozzle exit) **133 in**. Tubular
construction: LH2 fuel flows **down through 180 tubes**, **back up through 360 tubes** to the
injector — this is the real 180/360 two-pass tube count already anchored via `[Wieseneck-J2]`
(construction rationale) and encoded as `engine_designer/physics/design.py`'s
`"j2_mid_nozzle_inlet"` cooling topology; this source independently corroborates the same
180-down/360-up figure by name, with no new geometry beyond what's already captured (channel
count, land width, wall thickness are NOT given here).

**Injector** `[RPE-J2Blog, "Description"]`: "flattened conical," porous-faced injector with
concentric fuel orifices around oxidizer post orifices; fuel orifice area **25.0 in²**,
oxidizer orifice area **16.0 in²**; the porous sintered-metal screen face (Rigimesh) passes
**3-4% of the GH2 fuel flow** through it for injector-face cooling — a real, named face-cooling
bypass fraction (comparable in kind to the film-cooling fractions already tracked in
`physics/cooling.py`'s `film_cooling_fraction`, though this is face-cooling bleed through a
porous injector face, not a discrete film-cooling ring). **Injector development history**
`[RPE-J2Blog, "Development"]`: the original J-2 injector was a flat-faced copper
concentric-doublet/triplet design (Rocketdyne's earlier-engine style); despite no combustion
instability, gas-side heating patterns differed enough from LOX/RP-1 experience that the
copper face melted and vaporized (visibly greening the exhaust plume). MSFC pushed Rocketdyne
to adopt the Lewis Research Center / Pratt & Whitney RL10 "Rigimesh" porous-face approach;
Rocketdyne resisted using a competitor's technology until 1962, when it finally toured Lewis,
adopted the porous-face principle, and the green-flame problem disappeared. This ties the
already-used term "Rigimesh" (appears elsewhere in `claude_lit`'s injector material) directly
to its RL10/Lewis origin and gives a real example of an injector redesign driven purely by
gas-side thermal behavior differing between propellant pairs, not by combustion instability.

**Augmented Spark Igniter (ASI)** `[RPE-J2Blog, "Description"]`: mounted at the injector's
center, an integral part of the injector, and — notably — **remains lit for the ENTIRE burn
duration**, not just a start-transient pulse. Fuel and oxidizer are routed to a small ASI
combustion chamber and ignited by two energized spark plugs; oxidizer flow to the ASI is
controlled by a pneumatically-operated poppet valve mounted ON the main oxidizer valve (MOV).
An "ASI ignition monitor" senses ASI combustion during start and aborts the start sequence if
ignition isn't confirmed before the ignition-phase timer expires. This is a real, concrete
example of a continuously-burning (not pulse) torch igniter architecture — useful context for
`engine_designer`'s ignition-system options if a "continuous torch igniter" mode is ever
modeled distinctly from a one-shot pyrotechnic/spark-torch start.

**Turbopumps** `[RPE-J2Blog, "Description"]`: fuel turbopump (Rocketdyne MK15) — self-lubricated,
high-speed **axial-flow**, inducer + **7-stage** rotor/stator, direct-driven by a dedicated
**2-stage velocity-compounded turbine**; LH2 enters via an **8.0 in low-pressure duct**, exits
via a **4.0 in high-pressure duct**. Oxidizer turbopump — self-lubricated, high-speed,
**single-stage centrifugal**, direct-driven by its own dedicated 2-stage velocity-compounded
turbine; LOX enters via an **8.0 in low-pressure duct**, discharges via a **4.0 in
high-pressure duct** (same duct sizes as the fuel side, stated independently for each pump).
**Series-turbine gas coupling, with real duct size**: a single gas generator feeds the fuel
turbine first; the fuel turbine's exhaust is ducted via an **8 in diameter crossover duct** to
the oxidizer turbine inlet — i.e. one GG, series turbines, no separate oxidizer-side GG feed.
This corroborates the same series-turbine architecture already established for the related
J-2S via `[AEDC-J2S]`, now with a real J-2 crossover-duct diameter attached to it.
**Oxidizer-turbine exhaust dumped into the nozzle** — a real nozzle-injection anchor: turbine
exhaust gas (having already passed through both turbines in series) exits through eyelets of
**total area 115 in²** into the thrust chamber at **area-ratio stations 10.45 to 11.40**,
"thereby contributing slightly to the total thrust." This is a real, dimensioned example of
the `turbine_exhaust.py` `nozzle_injection` disposal mode — injection eps ~10.45-11.4, exit
port area 115 in² — a second real anchor for that mode alongside the existing F-1/H-1 data
already cited there (not previously sourced from the J-2 specifically). **Oxidizer turbine
bypass valve**: during start, this valve bypasses a percentage of oxidizer-turbine-bound gas
directly to the thrust chamber (skipping the oxidizer turbine) to prevent turbine overspeed
during spin-up; when the MOV reaches its first stage, the bypass valve closes, routing full
flow to the oxidizer turbine — but even fully "closed," a small fixed orifice in the valve
continues to bypass a small fraction of gas, doubling as "a calibration device for turbopump
performance balance and engine mixture ratio." A real, if narrow, example of a fixed bypass
orifice used for MR trim independent of the main PU valve.

**Turbopump power/speed (from the cross-engine spec table)** `[RPE-J2Blog, "Launch Vehicle
Engine Specifications" table]`: LOX turbopump **2,358 hp at 8,753 rpm**; LH2 turbopump
**7,977 hp at 28,130 rpm** — real, if secondhand, power/speed anchors for the J-2's two
independently-shafted, gas-coupled-in-series pump trains (no shared shaft, no gearbox). Same
table gives vacuum thrust 230,000 lbf, burn time 500 s, Pc 787 psi, MR 4.5-5.5, engine dry
weight 3,480 lb, T/W(SL) 66.1, propellant flow 544 lb/s (19.1 gal/s) — all consistent with
J-2 figures already established elsewhere in `claude_lit`, included here only as a secondary
cross-check, not a new anchor.

**Gas generator** `[RPE-J2Blog, "Description"]`: single GG, combustion chamber with 2 spark
plugs, a pneumatically-operated control valve housing mechanically-linked oxidizer and fuel
poppets that provide a deliberate **fuel lead** into the GG chamber (a real, named
start-sequencing safety feature — fuel arrives before oxidizer to avoid an oxidizer-rich
transient).

**Start tank** `[RPE-J2Blog, "Description"]`: a spherical **7,258 in³ GH2** start tank with a
concentric internal spherical **1,000 in³ GHe** tank, engine-mounted, used to spin both
turbopump turbines for start. Real in-flight restart mechanism: GH2 for start-tank
repressurization during mainstage is bled from the **thrust chamber fuel manifold inlet and
fuel injection manifold** (i.e. warmed regen-jacket-exit GH2), enabling the J-2's in-space
restart capability. Separately, **LOX tank pressurization uses LOX boiled by a heat exchanger
on the turbine exhaust duct** — a real example of turbine-exhaust waste heat being used for
propellant-tank pressurization (distinct from, and in addition to, the turbine exhaust's
thrust/nozzle-injection use above) — not currently modeled in `physics/turbine_exhaust.py`
but a real historical use case worth flagging as a possible future feature.

**Valve/sequencing hardware, real names and behavior** `[RPE-J2Blog, "Description",
"Start Sequence", "Cutoff"]`: **MFV** (main fuel valve) — spring-loaded-closed butterfly,
pneumatically opened, pneumatically-assisted closing; a sequence valve on the MFV triggers at
**~90% open** to route helium to the Start Tank Discharge Valve (STDV) control valve. **MOV**
(main oxidizer valve) — spring-loaded-closed butterfly, opens in **two discrete stages**
(unlike the single-stage MFV); a sequence valve on the MOV, once open, routes pressure to open
the GG control valve and to close the oxidizer turbine bypass valve (through a flow-restricting
orifice that paces the bypass valve's closing speed). **PU (propellant utilization) valve** —
electrically-operated, motor-driven, bypasses a percentage of LOX from the oxidizer-pump
discharge back to its inlet; nominal MR range **4.5:1 (full open) to 5.5:1 (full closed)** over
a **57° valve angle** travel — a real, dimensioned MR-trim valve geometry number. Two
redundant "thrust OK" pressure switches gate both the start-confirm and in-flight
low-thrust-cutoff logic (dual-channel safety interlock).

**Start/cutoff sequence — full valve/timer order** `[RPE-J2Blog, "Start Sequence", "Cutoff"]`:
narrated in prose, step by step (spark exciters -> He flow established -> bleed valves close ->
GG/O2-dome purges open -> MFV & ASI-O2 valve open on the ignition-phase control valve -> MFV
reaches 90% -> STDV control valve opens (gated by a start-tank-discharge delay timer AND a
stage-supplied mainstage-enable signal) -> both turbopumps spin up on start-tank GH2 -> ASI
ignition confirmed -> mainstage control valve opens MOV -> GG ignites -> chamber ignites via
the ASI torch -> mainstage transition on TPA speed + dual thrust-OK switches). Cutoff is
essentially the mirror image, LVDC-commanded, with a fast-shutdown valve that rapidly vents
the GG control valve's return line to accelerate GG shutdown, and most valves spring-closing
once their pneumatic opening pressure is released. This level of valve-sequencing/timer detail
is the single most useful NEW hardware content in this source relative to what's already in
`claude_lit` for the J-2 — neither `[Wieseneck-J2]` nor `[J2X-Overview]` describe start/cutoff
valve sequencing at all.

**ASI fuel-line failure (SA-502/Apollo 6) — a real, well-corroborated failure investigation**
`[RPE-J2Blog, "The Troublesome SA-502 (Apollo 6)"]`: two J-2 engines (S-II engine #2, S-IVB
single engine) both degraded/failed in the same 4 Apr 1968 flight. Root cause, per Rocketdyne's
own post-flight investigation (cited to R-7450-2 Vols. 2 & 3 in the reference list): the
stainless-steel ASI fuel line ran from the fuel inlet manifold to the injector-mounted ASI,
routed through **three flexible braided-stainless bellows sections** meant to absorb thermal
expansion and isolate engine vibration. Engineers hypothesized resonant vibration broke a
bellows, causing an LH2 leak (explaining an observed external temperature drop), followed by
hot combustion gas blowing backward out the break (explaining the later temperature rise and
Pc drop) while the ASI's LOX supply, now unopposed by fuel, began burning through the ASI and
injector metal itself, eventually punching a hole in the S-II engine's chamber wall. A
special vacuum-chamber vibration test was built in **two weeks**; **all 8 of 8** tested ASI
fuel lines ruptured under flight-representative vibration loads **in vacuum**, but the same
lines had passed extensive ground and Saturn-IB (denser local atmosphere at S-IVB altitude)
testing without failure across **289 prior J-2 ground tests** plus multiple earlier flights.
The explanation: in air, LH2's extreme cold liquefies the surrounding air, and the resulting
liquid-air film inside the braided bellows sheath acted as an (unintended) vibration-damping
medium — absent in the vacuum of space, allowing the bellows to reach destructive resonance.
Fix: replace the flexible bellows with rigid **S-turn** tubing sections plus more secure
external line mounting, validated at the AEDC J-4 high-altitude test cell, then flown
successfully starting with the first crewed Saturn V (Apollo 8, AS-503). This is a real,
internally-consistent, and (per the reference list) primary-source-backed engineering failure
story — a genuine example of an environment-dependent (vacuum vs. atmosphere) mechanical
resonance failure mode in cryogenic engine plumbing, worth a citation anywhere
`engine_designer` discusses flexible-line/bellows design margins, vibration isolation, or the
general hazard of ground-test conditions failing to reproduce a flight (vacuum) failure mode.

**Materials/embrittlement mitigation** `[RPE-J2Blog, "J-2 Development"]`: hydrogen
embrittlement of metal parts was mitigated by **copper or gold plating** (a dense coating that
hydrogen penetrates far more slowly than the bare base metal); duct flanges and pipe joints
used **Teflon-coated seals** to contain hydrogen against its tendency to leak through the
smallest imperfections. Real, if brief, materials-and-sealing detail with no quantitative
backing (no plating thickness, no leak rate) — context only.

## Design method

Not a derivation, correlation, or design-criteria source — a compiled historical narrative.
Its value to `engine_designer` is entirely in (a) real named hardware/valve/sequencing detail
not present in the more formal design-criteria or program-status sources already cited for the
J-2 (`[Wieseneck-J2]` covers cooling/materials only; `[J2X-Overview]` covers the later J-2X
derivative's program status, not J-2 valve sequencing), (b) a second real anchor for the
`turbine_exhaust.py` `nozzle_injection` disposal mode with actual eps/area numbers, and (c) a
genuinely useful, if secondhand, real engineering failure-investigation narrative (ASI bellows
resonance) that illustrates a vacuum-vs-atmosphere vibration failure mode relevant to any
cryogenic flex-line design discussion. No equations, no sizing method, no wall-thickness or
channel-geometry numbers beyond the already-known 180/360 tube count.

## Section map

- Background (LH2 program history, ARPA/RL10 competitive context): read.
- J-2 Development (hydrogen embrittlement mitigation, original injector failure & redesign):
  read.
- Photo gallery captions (walk-around, thrust-chamber construction, injector, ASI, turbopumps):
  read — component identification only, no additional numeric content beyond what's quoted
  above.
- Description (thrust chamber / injector / ASI / fuel TPA / oxidizer TPA / GG / start tank /
  MFV / MOV / PU valve / pneumatic package / electrical package): read in full, primary source
  of the hardware numbers above.
- J-2 Operation (Start Preparations, Start Sequence, Cutoff, Malfunction Detection): read in
  full.
- "The Troublesome SA-502 (Apollo 6)" (ASI fuel-line failure investigation): read in full.
- References (9 sources, incl. Rocketdyne's own R-7450-2 flight-failure report, two AEDC
  altitude-test reports, and NASA SP-4206/SP-2004-4230 histories): read (titles only, not
  independently chased/acquired).
- "Launch Vehicle Engine Specifications" comparison table (10 engines incl. J-2): read; only
  the J-2 column was extracted above (cross-check numbers, not new anchors).
- Images: two thumbnails viewed directly
  (`J-2Start,ShutdownSeqT.jpg`, `J-2FlowSch_01T.jpg`); both too small/low-resolution locally to
  extract new numeric content beyond confirming the text-narrated event order. Full-resolution
  originals are hosted online only (not saved to `literature/`), so were not accessed.

## Caveats

- **Secondary, enthusiast-history source, not a peer-reviewed or NASA/Rocketdyne
  design-criteria document.** No inline citations tie individual claims to specific
  references — the reference list at the end is a general bibliography, not a footnote
  apparatus. Confidence in any single number here should be LOWER than for a primary source
  like `[Sutton]`, `[SP-8107]`, or the AEDC/NASA CR reports already cited for the J-2/J-2S
  family (`[AEDC-J2S]`, `[Wieseneck-J2]`, `[J2X-Overview]`) — use this source for real
  hardware-level color and cross-checking, not as the sole citation for a physics constant.
- **The ASI-bellows failure narrative is the most credible single claim in this source**
  because it is explicitly attributed to Rocketdyne's own flight-failure-analysis report
  (R-7450-2 Vols. 2-3) in the bibliography and is internally detailed and self-consistent
  (timeline, "8 of 8 lines ruptured" test result, named fix) — still, this note could not
  independently verify the claim against the primary R-7450-2 report itself (not in
  `literature/`).
- **Minor internal inconsistency**: body text states nozzle expansion ratio "27:1," the
  cross-engine spec table at the bottom of the same page states "27.5" — both are quoted
  above; treat 27.5 (the table) as very slightly more likely to be the precise figure, since
  spec-comparison tables in this series tend to carry more decimal precision, but this is not
  resolved by anything else in the source.
- **No channel/tube dimensional detail beyond the 180/360 tube count** (no tube diameter, wall
  thickness, land width, coolant flow split, or measured jacket dP) — this source adds nothing
  to the geometric/thermal cooling-jacket picture already established via `[Wieseneck-J2]`'s
  2026-09-23 re-read; it only independently corroborates the tube COUNT by name.
- **Start/shutdown timing-chart images could not be read at usable resolution** — only small
  thumbnails were saved locally (full-resolution versions are hosted on enginehistory.org and
  were not fetched); the qualitative event ORDER shown in the chart matches the text narrative,
  but no specific timer/second values from the chart are quoted anywhere above.
- **No manifold, injector-orifice-count, or turbopump-impeller-stage dimensional detail beyond
  what's quoted** (e.g. no individual orifice diameters, no impeller/inducer blade counts,
  no bearing type) — checked specifically since these are common `engine_designer`-relevant
  gaps; not present in this source.
