# AIAA 85-1694 — Orbital Maneuvering System Design Evolution

## Identity

C. Gibson and C. Humphries (NASA Lyndon B. Johnson Space Center), *Orbital Maneuvering
System Design Evolution*, AIAA-85-1694, 1985 (NTRS accession 19850008634).
`literature/AIAA 85-1694 - Orbital Maneuvering System Design Evolution.pdf` (17 PDF leaves;
fixed offset — printed page = PDF leaf + 639, i.e. the paper runs printed pp. 639–655; no
front matter, leaf 0 = p.639). Tag: `[OMS-DesignEvo]`.

## Character

A short (17-page) conference-paper design-history narrative of the Space Shuttle Orbital
Maneuvering System (OMS), written by two of the NASA JSC engineers who lived through its
evolution. Not a design monograph (no derivation, no sizing equations) — its value is
entirely **real engineering-tradeoff narrative and real numbers for two different real
design points**: (1) the original 1969–70 baseline, a **pumped LOX/LH2 OMS** sized for a
15,000–25,000-lb-payload-class vehicle, and (2) the final flown design, the
**pressure-fed, Earth-storable NTO/MMH (Aerozine-50 initially, MMH later) OMS** actually
used on the Shuttle Orbiter. The paper is essentially the missing "why" behind the well-known
fact that Shuttle flew storable hypergolics instead of the cryogenic baseline everyone
associates with the Shuttle main engines — directly relevant to this project's own
pressure-fed hypergolic work (`TR341_Config.cfg`) and to `topics/08-engine-cycles.md`'s
cycle/propellant-selection guidance.

Structure: Abstract (the whole design-evolution story compressed to one paragraph) →
Preliminary Design Considerations (early-1970s configuration-study numbers, LOX/LH2 →
storable-hypergolic transition) → Engine Critical Issue Investigations (post-Apollo NASA
technology contracts: bipropellant valve, two competing thrust-chamber cooling concepts,
acoustic-cavity stability, platelet injector) → Initial Subsystem Requirements Definition
(1972 mission-driven requirements once Rockwell/MDAC were on contract) → Trade Studies and
Design Approaches (the flown hardware's own design evolution: pod structure, propellant
acquisition/gaging, pressurization, the engine itself) → Conclusions (one paragraph) →
Acknowledgment. Read in full (all 17 leaves, all figures' caption/label text extracted;
plotted curves/photos not present — this paper has no data plots, only schematics/labeled
cutaway figures, and their caption text is fully captured below).

## Key results — why LOX/LH2 was rejected for the flown storable-hypergolic OMS

This is the paper's single most useful finding for this project. The switch away from the
original cryogenic baseline happened in **two separate real decision points**, each with a
distinct driver, not one blanket "storables are simpler" call:

1. **1970, first switch (015-series → 012/013-series configurations)** — the original
   1969–70 studies baselined LOX/LH2 tankage sized for **2000 ft/s delta-v (incl. 1500 ft/s
   on-orbit)** on a 15,000–25,000-lb-payload vehicle `[OMS-DesignEvo Abstract p.639]`. By
   1970, for a 50,000-lb-payload, 15×60-ft-bay Orbiter, "**internal volume constraints and
   concerns regarding the complexity of the O2/H2 OMS and RCS**" drove consideration of
   storable hypergolic (NTO/Aerozine-50) propellants matching the Apollo LM/CSM heritage
   `[OMS-DesignEvo p.646]` — i.e. the driver here was as much **system complexity from
   running two different propellant chemistries (cryo OMS + storable RCS) on one vehicle**
   as it was tank volume per se. The Abstract states the reasoning more simply: the switch
   was made "to minimize overall vehicle length and reduce subsystem development costs"
   `[OMS-DesignEvo Abstract p.639]`, using a single Apollo LM descent engine.
2. **1971, the decisive switch (013/040C-series, external-MPS-tank Orbiters)** — once
   external, expendable main-propulsion-system propellant tanks let the Orbiter itself
   shrink, the *reduction in OMS impulse requirement that followed* is explicitly named as
   the trigger: "for the smaller, lighter Orbiter with external main tanks, **sufficient
   internal volume for an oxygen/hydrogen OMS was a significant penalty; higher density
   storable propellants were also attractive from this standpoint**" `[OMS-DesignEvo p.646]`.
   This is the real quantifiable mechanism: LOX/LH2's low bulk density (dominated by LH2)
   costs disproportionately more *volume* per unit delta-v than a smaller vehicle can spare,
   even though it costs less *mass* — a volume-constrained, not mass-constrained, tradeoff.
   The same passage separately confirms a Shuttle-program-specific policy constraint at that
   time: "**to be consistent with Orbiter Shuttle philosophy at that time, only existing
   engines were considered**" `[OMS-DesignEvo p.646]` — i.e. the initial storable-engine
   candidates (LM ascent engine, LM descent engine, Agena) were picked from existing Apollo
   hardware, not designed fresh; the fresh 5000/6000-lbf OMS engine only entered the picture
   once those existing engines proved inadequate (see below).

**Why existing Apollo hypergolic engines were then rejected in favor of an all-new engine**
`[OMS-DesignEvo p.646, p.647-648]` — a second, distinct real design-tradeoff chain, this
time driven by duty-cycle/reusability limits of Apollo-heritage ablative-chamber hardware,
not propellant chemistry:
- LM ascent engine (LMAE): 3500 lbf thrust; its low thrust combined with its *maximum
  mission-duty-cycle firing duration of 500 sec* (demonstrated up to 900 sec in isolated
  tests) meant **three engines** were needed to meet the 1550-sec accumulated burn-time
  requirement for the 1500-ft/s on-orbit delta-v capability — an unattractive parts-count
  penalty.
- Once a new engine was seriously evaluated (Orbiter config 040C, two pods, 500 ft/s
  delta-v/pod at 250,000 lb on-orbit vehicle weight incl. 65,000-lb payload — total 2500
  ft/s achievable with auxiliary payload-bay tankage), the LMAE's thrust-to-weight ratio was
  found **marginal, with no growth margin**; its burn time to perform the *entire*
  delta-velocity requirement on a single engine was **2800 sec**, which would have required
  **a new ablative chamber** (i.e. the flight-proven Apollo ablative chamber's accumulated
  burn-time rating didn't cover the OMS's much longer reusable-vehicle duty cycle).
- The LM descent engine (LMDE) was also considered: its single-engine burn time for the
  full delta-v requirement was **995 sec**, "an indication of marginal engine capability to
  perform an engine-out deorbit burn without chamber modifications" — i.e. even the
  descent engine's more generous ablative-chamber rating was borderline for the
  single-engine-failure reliability case that drove the whole two-engine-redundancy
  philosophy (below).
- Refurbishment cost of either existing engine (needed for the OMS's 10-year/100-mission
  reuse requirement) was found to make **a new purpose-built reusable engine cost-effective
  outright**, and a new engine also bought margin for future requirement/vehicle growth.

**Net real-engine outcome**: a new 5000-lbf-thrust (later 6000-lbf, see below), reusable,
pressure-fed, Earth-storable NTO/Aerozine-50 (later MMH) engine, regeneratively cooled, with
GHe ambient-temperature pressurization from a single tank per pod `[OMS-DesignEvo p.646]`.

## Real parameter data — original LOX/LH2 baseline (rejected)

| Parameter | Value | Cite |
|---|---|---|
| Payload class | 15,000–25,000 lb | `[OMS-DesignEvo Abstract p.639]` |
| OMS delta-v (tankage sizing) | 2000 ft/s total, incl. 1500 ft/s on-orbit | `[OMS-DesignEvo Abstract p.639]` |
| Design life | 10 yr / 100 missions, multiflight reuse | `[OMS-DesignEvo Abstract, p.639]` |
| Redundancy philosophy | fail-operational/fail-safe | `[OMS-DesignEvo Abstract, p.640]` |
| 1970 conceptual-design payload | 50,000 lb, 15×60 ft bay | `[OMS-DesignEvo p.640]` |
| Usable propellant (loaded) | 22,000 lb | `[OMS-DesignEvo p.640]` |
| Tank volumes (5% residual/ullage margin) | LH2 tanks 1206 ft³ total, LO2 tank 261 ft³ | `[OMS-DesignEvo p.640]` |
| Engine | 2× gimbaled RL10A-3-3, forward-firing, mounted to a forward thrust bulkhead | `[OMS-DesignEvo p.640]` |
| RCS feed | shared O2/H2 feedline drawn from the OMS tanks; RCS gas generator downstream of OMS shutoff valve | `[OMS-DesignEvo p.640]` |

## Real parameter data — intermediate storable-hypergolic studies (NTO/Aerozine-50)

| Parameter | Value | Cite |
|---|---|---|
| 012-series tankage | 2000 ft/s delta-v @ Isp 310 s, MR 1.6, 31,300 lb usable propellant (single LM engines also investigated) | `[OMS-DesignEvo p.641]` |
| 013-series tankage | sized for 2000 ft/s @ Isp 310 s; loaded to provide 1396 ft/s actual | `[OMS-DesignEvo p.642]` |
| 040C config | 2 pods, 500 ft/s delta-v/pod @ 250,000 lb on-orbit weight (incl. 65,000-lb payload); 2500 ft/s total with auxiliary payload-bay tankage | `[OMS-DesignEvo p.642]` |
| Baseline engine (040C) | new 5000-lbf-thrust reusable Earth-storable engine, pressure-fed, GHe ambient-temp pressurant, 1 He tank/pod | `[OMS-DesignEvo p.642-643]` |
| Design goal | "15 hours life (100 missions)" with maintenance-free operation for 1 year — **caveat: OCR-uncertain reading, likely accumulated burn-time hours, not calendar; not independently verified this pass** | `[OMS-DesignEvo p.643]` |

## Real parameter data — final flown-configuration baseline engine (post-1972, NTO/MMH)

From Figure 10's baseline-summary box (this figure's text is heavily OCR-garbled — several
numeric fields below carry an explicit garbling caveat; see Caveats section):

| Parameter | Value | Cite |
|---|---|---|
| Thrust (vacuum) | ~6000 lbf (OCR reads "IS000 LB" — near-certainly garbled "6000 LB"; consistent with the paper's own stated ~6000-lbf nominal thrust design-driver reasoning and the real historical AJ10-190 OMS engine rating) | `[OMS-DesignEvo Fig.10 p.651]` |
| Specific impulse (vacuum) | ~313 s (OCR "31:L2 SEC", plausibly "313.2") | `[OMS-DesignEvo Fig.10 p.651]` |
| Chamber pressure | 121 psia (as OCR'd; treat with some caution — commonly cited secondary-source Pc for this engine class runs slightly higher, ~125–137 psia) | `[OMS-DesignEvo Fig.10 p.651]` |
| Mixture ratio | ~1.6 (OCR "1.U") | `[OMS-DesignEvo Fig.10 p.651]` |
| Delta-v capability | 1000 ft/s, 55,000-lb payload | `[OMS-DesignEvo Fig.10 p.651]` |
| Nozzle area ratio | 55:1 | `[OMS-DesignEvo p.648]` |
| Engine envelope | 44 in dia within a 50-in-dia allocated envelope | `[OMS-DesignEvo p.648]` |
| Regen chamber contraction ratio | 1:9 | `[OMS-DesignEvo p.649]` |
| Injection-plane-to-throat length | 15.9 in | `[OMS-DesignEvo p.649]` |
| Regen-to-radiation-cooled transition | 6:1 area ratio (bolted joint) | `[OMS-DesignEvo p.649]` |
| Regen coolant channels | 120 longitudinal milled rectangular channels, constant width / varying depth | `[OMS-DesignEvo p.649]` |
| Chamber materials | 304L stainless-steel liner + electroformed nickel shell (each independently load-bearing — liner/shell bond not structurally critical) | `[OMS-DesignEvo p.649]` |
| Nozzle extension | all-columbium, radiation-cooled, 6:1→55:1, 80%-bell contour, silicide oxidation-barrier coating applied after final machining | `[OMS-DesignEvo p.650]` |
| Nozzle extension construction | flange (forged bolt ring + forged/spun taper, 0.100 in → 0.050 in) + forward section (2 panels, butt-welded into a cone) + aft section (2 panels, 0.030 in thick) — panels bulge-formed to final contour after welding | `[OMS-DesignEvo p.650]` |
| Nozzle stiffening (design evolution) | originally 3 external stiffening rings near mid-nozzle → changed to a single flange at the nozzle exit only, driven by revised aerodynamic-loading magnitude/location and revised aero-noise expectations | `[OMS-DesignEvo p.652]` |
| Regen tech-demo Isp (predevelopment) | 317 s with an OME-sized nozzle | `[OMS-DesignEvo p.644-645]` |
| Ablative-columbium alt. chamber tech-demo Isp | slightly >310 s | `[OMS-DesignEvo p.645]` |
| Blowdown-mode stability limit | stable down to ~70 psia chamber pressure after simulated fuel-depletion condition | `[OMS-DesignEvo p.644-645]` |

## Key results — real engineering detail beyond the propellant/cycle choice

**Injector**: development used an X-doublet injector (from the technology contract), but the
**flight baseline switched to a like-on-like doublet pattern of 8 photo-etched platelets**
`[OMS-DesignEvo p.652, Fig.13 p.653]`. The reason is a real, instructive manufacturing
finding, not a performance one: the X-doublet injector could not be reliably reproduced — a
slight platelet-flatness variation caused minor stream-direction variations that measurably
degraded combustion-stability characteristics in a like-on-like injector built to nominally
the same pattern; because the difference was "subtle" and "almost impossible to define,"
the team abandoned the pattern that couldn't be manufactured repeatably rather than chase the
root cause. Construction: diffusion bond + redundant electron-beam weld of the faceplate to
the body `[OMS-DesignEvo Fig.13 p.653]`.

**Combustion stability**: acoustic cavities (Helmholtz-type resonators), not baffles, were
selected for this reusable/long-duration application specifically because cavities are
"easier to cool and, therefore, less subject to failure from either burnout or thermal
cycling" than baffles `[OMS-DesignEvo p.645]` — a direct real precedent for
`combustion_stability.py`'s baffle-vs-cavity tradeoff reasoning, tied explicitly to the
reusability requirement rather than to raw suppression effectiveness. A real, non-trivial
uncertainty is also stated plainly: even with demonstrated stability across "a relatively
wide range of cavity configurations" and developed analytical design techniques, "the
stability of an engine with or without acoustic cavities could not be predicted analytically
with confidence" `[OMS-DesignEvo p.645]` — stability testing, not calculation, closed this
loop. A specific real concern (regen-cooled fuel runs hotter than the ambient-temperature
propellant used in the extensive LM-ascent-engine-heritage cavity test base) drove a
dedicated follow-on technology program at closer-to-OME temperature conditions, which
confirmed cavities still worked and identified **doubly tuned cavity configurations that
suppressed the first and third tangential modes plus the first radial mode simultaneously**
`[OMS-DesignEvo p.645]`.

**Bipropellant valve**: originally quad-redundant (Apollo-SPS heritage), the flight design
**switched to a series-redundant valve** to cut weight/complexity `[OMS-DesignEvo
p.654-655]`. The stated justification for why series redundancy was acceptable here but
wasn't for Apollo SPS: unlike the single non-redundant Apollo SPS engine, the **OMS itself
has 2 engines redundant to each other**, plus reconfigurable tankage/interconnect lines, so
full functional redundancy against a failed-closed valve exists at the *system* level even
with only series (not quad) redundancy at the *component* level — a real illustration of
redundancy-philosophy trading off against engine-count/system architecture rather than
being fixed per-component. Mechanism: one fuel + one oxidizer poppet mechanically linked per
pair, 4 linked pairs, each driven by a piston actuator via a close-coupled 3-way solenoid
valve; pneumatic GN2 opens, nested counterwound helical compression springs close; **all
solenoid valves carry dual coils** because the most probable valve-open failure mode was
identified as a single solenoid-control-valve failure, and **a second GN2 storage tank was
added downstream of the pressure isolation valve** purely to guarantee one valve actuation
even if the isolation valve itself fails to open `[OMS-DesignEvo p.652-655]`. GN2 regulator
supply: 325 psia, sized for 10 engine purges + 40 valve actuations `[OMS-DesignEvo Fig.17
p.655]`.

**Pressurization/tankage**: single composite-aluminum He bottle per pod splitting into two
regulation branches (series-parallel regulators, isolation solenoids, quad check valves) —
later simplified to a **common regulation source for both oxidizer and fuel** once the
fail-safe-only criterion (see below) allowed removing a third regulation leg, which also
gave tighter mixture-ratio control by coupling the two propellant tanks' regulated flow path
`[OMS-DesignEvo p.647-648]`. Propellant tanks: annealed titanium; the acquisition system
evolved from simple point-sensor + refillable-trap (OMS-only) to a **compartmentalized
refillable trap** with capacitance-probe gaging once an OMS/RCS propellant interconnect was
added, so the trap could supply 1000 lb of propellant to the RCS while retaining the
capability to restart the OMS 10 times `[OMS-DesignEvo p.647, Fig.9 p.650]`.

**Reliability/redundancy architecture**: driven by Apollo experience, **two OMS engines**
(not more, not one) was set as the acceptable safety-level ground rule, meaning the system
was sized so that after any single engine failure the *other* engine alone could complete
the full mission — this, not any component-level factor, is what set the per-engine
thrust/total-impulse requirement `[OMS-DesignEvo p.647]`. A real corollary constraint: a
naively modular (fully separate propellant/pressurant per pod) system would drop to only
half impulse capacity on an engine failure unless *each* pod were separately sized for full
mission capacity — an excessive weight penalty — so **dry, isolated propellant interconnects
between the two pods** were mandated specifically to let *either* engine draw *all* the
propellant, at the cost of only doubly (not more) redundant interconnect valve components
`[OMS-DesignEvo p.647]`.

**Mission-sizing numbers** (1972 baseline, once Rockwell/MDAC were on contract)
`[OMS-DesignEvo p.647-648]`: reference mission = satellite delivery/retrieval to a
100-nmi circular orbit, due-east KSC launch, 65,000-lb payload; Orbiter inserted into a
50×100-nmi orbit, **90 ft/s** OMS circularization burn at apogee; ~6 days on station with
**12 orbit-maintenance burns at 4.5 ft/s each**; a **32 ft/s** terminal-phase-initiation burn
before retrieval; **250 ft/s** deorbit burn; anticipated on-orbit+descent total (excluding
maintenance burns) **372 ft/s**, but **1000 ft/s total delta-v capability was actually
provided**. Thrust-level selection reasoning: small maneuvers are more propellant-efficient
at low thrust, but low thrust increases burn time and thus total impulse for the (more
significant) large delta-v corrections, so **~6000 lbf was set as the nominal design point,
4000 lbf as the floor** `[OMS-DesignEvo p.648]`.

**RTLS abort propellant dump — a real design simplification cascade**
`[OMS-DesignEvo p.649-650]`: began as dedicated quad-redundant dump valves → simplified to
series valves once the ground rule was set that an RTLS abort need not tolerate *additional*
failures on top of the abort itself → ultimately the dedicated dump system was **deleted
entirely**, once analysis showed the dump could be accomplished through the existing OMS and
RCS engines via the propellant interconnect already present for other reasons — a real
example of an interconnect built for one purpose (engine-out redundancy) eliminating the need
for a whole separate subsystem built for another purpose (abort dump).

## Design method

Not a design-method source (no sizing equations, no derivations) — a real engineering-history
narrative. Its value is the same kind as `[NK-33-Mod]`/`[AEDC-J2S]`/`[F1-Man]`: real hardware
numbers and real decision rationale from an actual flown system, one layer earlier than those
(system/vehicle-integration and cycle/propellant-selection level, not component-performance
level).

## Section map

- Abstract: p.639 — read.
- Preliminary Design Considerations: p.639–643 — read in full.
- Engine Critical Issue Investigations: p.643–646 — read in full.
- Initial Subsystem Requirements Definition: p.646–648 — read in full.
- Trade Studies and Design Approaches: p.648–655 — read in full, incl. all figure
  caption/label text (Figs. 1–17).
- Conclusions / Acknowledgment: p.655 — read (one short paragraph each).

## Caveats

- **Figure 10's baseline-performance summary box is the most heavily OCR-garbled block in
  the document** (thrust, Isp, Pc, MR, and the propellant-mass figures) — the values quoted
  above for thrust/Isp/MR carry an explicit reading judgment cross-checked against (a) the
  paper's own earlier stated ~6000-lbf design-driver reasoning and (b) commonly-cited real
  AJ10-190/OMS-engine specs; treat them as "very likely correct within the OCR-plausible
  reading," not as a directly-transcribed number. The propellant-mass fields in the same
  figure (total lb / N2O4 lb / MMH lb) were too garbled to reconstruct with any confidence
  and are deliberately **not** quoted.
- **This is a secondary/narrative history source, not a primary design report or test data
  set** — it has no plotted test data, no tables of raw measurements, and no derivations; the
  real numbers it does carry (design points, tankage/mass/geometry figures, sequencing
  rationale) are the paper's own summary of prior design-study/technology-contract results,
  not first-hand data from those programs.
- The "15 hours life (100 missions)" design-goal figure `[p.643]` is flagged explicitly above
  as an OCR-uncertain reading (likely accumulated engine-burn-time hours) — do not treat as
  verified.
- The final baseline's chamber-pressure figure (121 psia) is somewhat below other commonly
  cited secondary-source values for this engine class (~125–137 psia); this note does not
  resolve the discrepancy (could be a stated OCR error, a different measurement station, or a
  genuine design-point difference at the time this paper was written vs. the ultimately-flown
  hardware — the paper post-dates first flight by several years so should describe the flown
  configuration, but no independent primary source was cross-checked this pass).
- OCR quality overall is mixed-to-poor throughout (a 1985 conference-proceedings scan): body
  paragraphs are mostly readable with some word-joining/character-substitution noise (the
  telltale "LO2/LH_" subscript-loss pattern flagged in the task brief is present throughout,
  along with frequent digit/letter confusions, e.g. "0" and "O", "1" and "I"/"l"); the
  boxed/labeled figure captions (Figs. 4, 5, 10, 11, 17) are the worst-affected regions.
  Numbers quoted in the body-text narrative (not inside a figure box) were generally cleaner
  and are trusted at face value; numbers from inside figure boxes carry the caveats noted
  above.
- No propulsion performance/heat-flux/structural *derivation* content exists in this paper to
  extract for `topics/*.md`'s quantitative-method sections — its citable content is entirely
  real design-point numbers and real decision narrative, appropriate for
  `topics/08-engine-cycles.md` (cycle/propellant selection) and `topics/11-propellants.md`
  (real storable-vs-cryogenic system-level tradeoff), not for the cooling/injector/turbopump
  *sizing-method* topic files.
