# [Agena-CR120362] — Reusable Agena Study, Volume 2: Technical

## Identity

- **Title**: *Reusable Agena Study, Volume 2: Technical (Final Report)*
- **Authors**: W. K. Carter, E. W. Waller, S. S. Sagawa, J. E. Piper, C. V. Hopkins,
  S. A. Carter, D. A. Douglass, E. T. Fitzgerald, H. L. Jensen — Lockheed Missiles & Space
  Company, Sunnyvale CA
- **Report**: **NASA CR-120362**, LMSC-D383059 Vol II, Contract NAS8-29952, prepared for
  NASA Marshall Space Flight Center
- **Date**: Study period June–November 1973; final report distributed January 1974.
- **Extent**: 368 PDF leaves (front matter + 5 sections + references). Reasonably clean OCR
  text layer, though figures with embedded text (schematics) OCR poorly (garbled labels).
- **PDF leaf ↔ printed page**: front matter has no printed page numbers; Section 3 body
  text starts at PDF leaf 49 = printed page "3-1", i.e. leaf ≈ printed-page-number(within
  Section 3) + 48 for Section 3. No PDF bookmark/TOC (`get_toc()` returns empty) — the
  printed Contents list (PDF leaves 3–7) is the only navigation aid; used it to locate
  Section 3.3.2 (Propulsion Systems).

## Character

A **vehicle-level, engineering-economics study**, not a propulsion physics report: its
purpose is defining what changes the existing Agena upper stage (a 1960s-vintage USAF/NASA
vehicle) would need to fly reusably out of the Shuttle cargo bay — structural loads for
cargo-bay carriage, avionics augmentation, thermal control, ground/orbit operations,
reusability/refurbishment assessment, safety/abort, and program cost. The great majority of
the document (structures §3.3.1, avionics §3.3.3, thermal §3.3.4, Shuttle interface §3.3.5,
program/cost §3.5, safety §3.6, mission performance §3.7, ground/orbit ops §3.8, reuse
assessment §4) is vehicle-bus and mission-ops material with essentially nothing of use to
`engine_designer`'s chamber/injector/turbopump physics.

**However**, Section 3.3.2 "Propulsion Systems" (PDF leaves 85–122, printed pp. 3-37 to
3-74) IS a dedicated engine-design section covering the Bell Aerosystems **8096L** engine
(a pump-fed gas-generator hypergolic engine, HDA/MMH+silicone-oil, the proposed upgrade
from the existing Agena 8096 engine) in enough engineering depth to be citable: engine
performance derivation, injector redesign for combustion stability, hot-pump-restart
thermal analysis, and a start-system trade study. This sub-section is worth pulling
findings from; the rest of the document is not.

## Key results (from §3.3.2, the only propulsion-physics section)

- **Engine selection**: Bell 8096L, gas-generator pump-fed cycle (turbine + gearbox driving
  ox and fuel pumps), HDA (high-density acid, IRFNA-family oxidizer)/MMH propellants with
  1.5% hexamethyldisilazone (HMZ) silicone-oil additive to the fuel — the additive deposits
  a SiO₂ coating on the chamber wall that measurably cuts nozzle heat flux (Q/A), letting
  the existing regen-cooling design (oxidizer-cooled jacket) handle the switch from
  HDA/UDMH to HDA/MMH without a cooling redesign [Agena-CR120362 p.3-42].
- **Performance table (3.3.2-1, p.3-40)**: current 8096 (HDA/UDMH, ε=45, Pc=505 psia,
  Isp=295 s vac, MR=2.69) vs. proposed 8096L (HDA/MMH+SO, ε=100/150, Pc=484 psia, Isp=
  321/324 s vac, MR=2.03) vs. 8096B (NTO/MMH+SO, ε=100/150, Pc=486 psia, Isp=327/330 s,
  MR=1.78). All three: 16,000 lbf vacuum thrust.
- **Performance derivation breakdown (Table 3.3.2-2, p.3-41)** — a worked theoretical→test
  Isp bridge: ODK peak Isp (theoretical shifting-equilibrium) 335–346 s → core/barrier O/F
  split model (core O/F 2.1–3.54, barrier O/F 0.7–1.5, barrier flow 13–17% of total,
  overall TC O/F lower than core O/F — i.e. a fuel-rich wall-cooling barrier explicitly
  modeled as a separate mixture ratio from the core) → thrust-chamber Isp 302–334 s → c*
  test-vs-calc correlation (calc 5250 ft/s, test 5210 ft/s, ΔIsp −1.5 s applied) → net TC
  Isp → TPA loss of 5.0 s flat (turbopump bleed/friction penalty) → net engine Isp
  294.9–327.6 s. This barrier-cooling / core-vs-overall-O/F bookkeeping method is a
  reusable pattern for `engine_designer`'s film-cooling-fraction accounting even though the
  absolute numbers are specific to this small hypergolic engine.
- **Baffled injector for combustion stability** [p.3-42–3-43]: the 8096L injector was
  redesigned from the original 8096's flat-face injector to a **5-legged baffle**, driven
  by a stated bomb-test stability requirement — "a dynamically stable injector that will
  damp over-pressures induced by suitably sized bombs located in the most sensitive
  position within 40 msec to within ±5 psi of steady state pressure." This is a concrete,
  citable numeric bomb-test damping criterion (40 ms recovery to ±5 psi) from an actual
  flight-engine development program, usable as a real-world anchor point in
  `combustion_stability.md`'s baffle-injector discussion (though it's a specific program's
  acceptance spec, not a universal constant — flag as one data point, not a rule).
- **Turbopump comparison (Table 3.3.2-4, p.3-44)**: IRFNA/UDMH vs. HDA/MMH+SO pump
  requirements at same impeller diameter/speed — ox pump head rise 1340 ft, fuel pump 2150
  ft; capacities 146–180 GPM (ox) / 135–139 GPM (fuel); brake HP 178–212 (ox) / 159–169
  (fuel), total ≈347–371 HP; turbine flowrate 1.3–1.6 lb/s at 1050–1105 K gas temperature.
  Useful as one more small-engine (16 klbf) real turbopump data point, though this class of
  engine (hypergolic GG, sub-500-psia Pc) is likely already well covered by other sources
  in `claude_lit/`.
- **Hot pump restart (HPR) thermal analysis** [Tables 3.3.2-5/6, pp.3-45–3-46]: after
  shutdown, hot-gas-turbine heat soaks back into the pumps — current-8096 pump temp peaks
  ~220°F ~60 min after shutdown. For missions needing restart while the pump is still hot,
  boiling of the HDA oxidizer on contact with the hot pump housing was the failure mode of
  concern; mitigated passively via an 11-mil anodized stainless-steel pump housing/bearing
  support (vs. existing aluminum), holding peak bearing-support temp to ~209°F and requiring
  oxidizer tank pressure of 25–32 psia (vs. 17–23 psia for the cold-pump IRFNA baseline) to
  suppress boiling. A worked, quantified precedent for the general "hot-restart thermal
  margin" problem in pump-fed reusable/multi-start engines.
- **Start-system trade study** (Table 3.3.2-7, p.3-47): scored comparison of suction start
  (main-tank-head start), rechargeable start tanks (with/without dump), solid-propellant
  cartridges, and an electric-motor-pump-assembly (EMPA) start system across weight, cost,
  design/qual status, start transient behavior, mission flexibility, HPR impact, safety,
  reliability, reusability, and maintainability. Start tanks selected (roughly tied with
  suction start) to minimize hot-pump-restart development risk; final design uses
  pressurized bellows start tanks (1000 psia) for the gas generator during start, refilled
  automatically once the pump reaches rated speed, with 50,000-cycle bellows life. First
  burn always uses suction start (tanks launched dry for cargo-bay safety). A useful
  real-engine precedent if `engine_designer` ever adds an explicit start-system-type choice
  (it currently doesn't model start systems at all — see caveats).
- **TVC gimbal-rate sizing method** [p.3-48–3-49]: worked first-order gimbal dynamics —
  response time constant = J/B (J = engine gimballed inertia, 36/49/90 ft-lb-s² for the
  45:1/100:1/150:1 nozzle-extension options; B ≈ 650 ft-lb-s damping term for the existing
  hydraulic actuator/electronics), giving response times of 55/75/140 ms; minimum required
  gimbal rate set by not saturating the rate-gyro (3–5°/s) vs. available 15°/s. Not
  currently modeled anywhere in `engine_designer` (no TVC/gimbal actuator physics exists),
  but a clean worked example if that's ever added.

## Section map

| Section | PDF leaf(s) | Printed p. | Content | Engine-design relevance |
|---|---|---|---|---|
| 1–2 Intro/Summary | 0–48 | front matter, 1-1–2-21 | Study scope, vehicle concept, ground/flight ops overview, cost summary | None |
| 3.1–3.2 Requirements/current subsystems | 49–84 | 3-1–3-36 | Vehicle/mission requirements, existing Agena spaceframe/propulsion/avionics overview, structural design criteria | None (mentions propulsion system only as an overview figure) |
| **3.3.2 Propulsion Systems** | **85–99** | **3-37–3-51** | Engine selection & performance (8096/8096L/8096B), injector baffle redesign, turbopump comparison, hot-pump-restart analysis, start-system trade study, TVC gimbal sizing, pressurization/feed schematic | **The only citable engine-physics content — see Key results above** |
| 3.3.2.5–3.3.2.6 RCS / Prop Dev Status | ~100–118 | 3-52–3-74 | RCS thruster sizing (hydrazine monoprop, 8-18 lbf and 0.3-0.6 lbf thruster sets), non-impulse/residual propellant, component weight breakdown, development status table | Not checked in depth — RCS thruster-level detail (not main-engine); likely low value, not read |
| 3.3.3–3.3.5 Avionics/Thermal/Shuttle interface | ~123–170 | 3-75–3-152 | GN&C, DM&I, comms, EPS&D, thermal control, cargo-bay support structure | None |
| 3.4–3.8 Concept/Program/Safety/Performance/Ops | ~170–~310 | 3-153–3-272 | Vehicle configuration, schedules, cost, hazard analysis, abort/emergency dump, mission payload capability, ground & orbit operations | None |
| 4 Additional Considerations | ~310–~355 | 4-1–4-42 | Reusability/refurbishment assessment, reliability, special missions, growth/drop-tank configurations | None (refurbishment-frequency data is vehicle-bus, not engine-specific) |
| 5 Conclusions / References | ~355–368 | 5-1, R-1 | — | None |

## Caveats

- This is an **early-1970s pump-fed hypergolic engine** (Bell 8096L, 16,000 lbf, Pc ≈
  484–505 psia, ε 45–150:1) — small and low-chamber-pressure relative to most engines
  already anchoring `engine_designer`'s spot checks; the HDA/MMH(+SO)/NTO propellant
  combinations and the specific numbers here are unlikely to add a new validated data point
  unless `engine_designer` specifically wants an HDA-oxidizer or silicone-oil-additive
  propellant option (neither currently modeled).
  I did **not** cross-check whether HDA/MMH is already covered by an existing source or
  `physics/combustion.py` propellant-pair table — flagging that check as open if this
  engine is ever used as a spot-check candidate.
- The "40 ms to ±5 psi" bomb-test stability criterion (p.3-42) is a **program-specific
  acceptance spec** for this one engine's injector-redesign qualification, not a
  literature-derived general stability-margin standard — cite it as one real precedent, not
  as a universal number, if folded into `combustion_stability.md`.
- The TPA "5.0 s flat Isp loss" figure (Table 3.3.2-2) is a simple lumped bookkeeping term
  for this specific small GG-cycle engine's turbopump bleed/mechanical losses, not a
  derived or generalizable model.
- I only read Section 3.3.2 (Propulsion Systems) in depth; Sections 3.3.2.5–3.3.2.6 (RCS,
  propulsion development status) were seen only in the table-of-contents listing and are
  flagged above as unread/unlikely-relevant rather than confirmed irrelevant — if RCS
  monopropellant-thruster detail is ever wanted, that's the section to check.
- No PDF bookmark TOC exists (`doc.get_toc()` empty); navigation relied on the printed
  Contents pages (PDF leaves 3–7), which I've reproduced as the page-map basis above.
