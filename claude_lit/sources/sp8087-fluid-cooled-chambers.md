# NASA SP-8087 — Liquid Rocket Engine Fluid-Cooled Combustion Chambers

## Identity

NASA Space Vehicle Design Criteria (Chemical Propulsion) monograph SP-8087, *Liquid Rocket
Engine Fluid-Cooled Combustion Chambers*, April 1972. Written by N.E. Van Huff and David A.
Fairchild of Aerojet Liquid Rocket Company. `literature/NASA SP-8087 - Liquid Rocket Engine Fluid-Cooled Combustion Chambers.pdf` (NTRS 19730022965; 130 PDF leaves;
printed page N = PDF leaf N+15, e.g. printed p.4 "STATE OF THE ART" begins at leaf 19).
Tag: `[SP-8087]`.

## Character

Same NASA SP-8xxx design-criteria series as `[SP-8081]` (gas generators), `[SP-8107]`
(turbopumps), and `[SP-8120]` (nozzles) — same two-section structure: **§2 State of the
Art** (narrative, real-engine anecdotes, pp.4–53) and **§3 Design Criteria** (imperative
"shall"/"should"/"do not" rules, pp.54–94), with matching subsection numbers (§2.1.1.4
Channel Walls ↔ §3.1.1.4 Channel Walls, etc.). This is the single most directly relevant
monograph in the reference set for chamber/nozzle cooling-jacket construction and manifold
design specifically — unlike `[SP-8120]` (nozzle structure generally) or `[Huzel]`/`[Sutton]`
(broad textbook treatment), this document's entire scope is fluid-cooled combustion chamber
design.

Top-level structure (§2 State-of-the-Art page / §3 Design-Criteria page):

| Subject | §2 p. | §3 p. |
|---|---|---|
| **2.1/3.1 Regenerative Cooling** | 7–53 | 54–90 |
| — 2.1.1/3.1.1 Coolant Passages (basic requirements, number of passes, tubes, **channel walls incl. double-wall construction**, thermal/hydraulic) | 8–17 | 54–62 |
| — **2.1.2/3.1.2 Manifolds** (flow distribution, structure) | 19–20 | 62–63 |
| — 2.1.3/3.1.3 Chamber Reinforcement (throat, chamber, nozzle, interface flange) | 21–30 | 65–68 |
| — 2.1.4/3.1.4 Materials Compatibility | 27–30 | 68 |
| — 2.1.5/3.1.5 Structural Analysis (buckling, composite loads, tube compressive/fatigue strength) | 30–32 | 68–70 |
| — 2.1.6/3.1.6 Brazing | 33–37 | 70–75 |
| — 2.1.7–2.1.10/3.1.7–3.1.10 (Chamber Assembly, Laboratory Proof Testing, Operational Problems, Handling/Transportation) | 35–41 | 76–85 |
| 2.2/3.2 Transpiration Cooling | 43–48 | 85–91 |
| 2.3/3.3 Film Cooling | 49 | 91–93 |
| 2.4/3.4 Coatings | 51 | 93 |

## This note's extraction scope

Read in full: **§2.1.1/§3.1.1 Coolant Passages** (basic requirements, number of passes,
tube geometry/wall-thickness/bifurcation-joint criteria, **channel walls including
double-wall construction**, special thermal/hydraulic considerations) and **§2.1.2/§3.1.2
Manifolds** (flow distribution, structure) — the two sections most relevant to the
requesting session's flagged interest in manifolds and regenerative cooling. Also read
§2.1.3.1 Throat Reinforcement (State of the Art) in full, since it's the direct real-hardware
precedent for chamber structural-support method selection (cylindrical shell / brazed jacket
/ banded / double-wall / drilled-passageway, cross-referencing `[SP-8120]`'s retaining-band
content). **Not deep-read**: §2.1.3.2–2.1.10/§3.1.3.2–3.1.10 (chamber/nozzle/interface-flange
reinforcement beyond the throat, materials compatibility, structural analysis methodology,
brazing procedure detail, chamber assembly, proof testing, operational problems, handling) —
headers only, see Section map. §2.2–2.4/§3.2–3.4 (transpiration cooling, film cooling,
coatings) — not read at all, out of scope for this pass.

## Key results — §2.1.1/§3.1.1: Coolant passage configuration selection

**Configuration selection by heat flux and thrust, real design criterion** `[SP-8087
§3.1.1.1 p.54]` — the single most load-bearing quantitative criterion in this note:
- Max heat flux **< 12 Btu/in²·s (1.96 kJ/cm²·s)**: simple channel-wall design recommended.
- Max heat flux **10–25 Btu/in²·s (1.64–4.09 kJ/cm²·s)**: tubular construction recommended
  (advanced channel-wall techniques also usable).
- Max heat flux **> 25 Btu/in²·s (4.09 kJ/cm²·s)**: advanced channel-wall techniques should
  be used.
- **Thrust < 20,000 lbf (89.0 kN)**: simple channel-wall construction preferred regardless
  of heat flux.
- For **minimum weight**, tubular construction is recommended (i.e. there's an explicit
  weight-vs-simplicity tradeoff between tubular and channel-wall, not a strict heat-flux-only
  decision).

This is a genuinely new, directly-usable quantitative selection criterion — `[Marquardt-5981]`
gave a thrust-based cooling-*method* selection map (regen vs. radiation vs. ablative) but
nothing this specific on tubular-vs-channel-wall *construction type* selection within regen
cooling itself.

**Real-hardware wall-construction survey** `[SP-8087 §2.1 p.7]`, Table I: all major
production fluid-cooled thrust chambers use regenerative cooling; fluid cooling is limited
to large boosters/upper-stages/sustainers (one vernier exception); thrust range 1000 to
1.5 million lbf (4.45–6672 kN); max chamber pressure 1000 psia (6.90 MN/m²) across the
surveyed fleet. **All large thrust units use multi-pass tubular-wall construction** except
NERVA (U-shaped tubes brazed to a heavier outer shell, single-pass, driven by nuclear-heating
structural-jacket needs, not a normal design choice). Non-tubular real examples: **Atlas
vernier and Aerobee are double-walled; Agena uses drilled passageways** — all three are
**small, low-heat-flux units**, directly consistent with the §3.1.1.1 criterion above.

**Tube geometry criteria** `[SP-8087 §3.1.1.3.1 p.55]`: use the simplest tube geometry
possible (no taper → one-direction taper → both-direction taper, in that preference order).
**Maximum recommended taper: 3:1 by a pure reduction process (spinning/swaging); up to 6:1
if combined with an expansion process at the large end** (beyond 6:1, costs escalate). This
sharpens `[SP-8120]`'s F-1/general "6:1" note into an explicit criterion with the reasoning:
beyond 3:1 pure reduction, surface roughness and flow-area variation degrade badly.
**Tube wall thickness should exceed 0.010 in. (0.254 mm)** `[SP-8087 §3.1.1.3.2 p.56]` —
thinner walls are described as "a poor risk" even when thermal/structural analysis says
thinner would work, because of flaw sensitivity, erosion/corrosion, and handling-dent risk.
Real hardware corroboration: 0.010 in. was used but caused pinholing until raised to
0.016 in. `[SP-8087 §2.1.1.3 p.13]` (echoing `[AEDC-J2S]`'s and `[SP-8120]`'s real-hardware
wall-thickness anecdotes elsewhere in this reference set).

**Tube forming process detail** `[SP-8087 §2.1.1.3 p.12-13, Fig. 1]` (deep-read 2026-09-23):
individual tubes are formed from a single large cylindrical tube by alternating working
(**swaging, spinning, drawing, or expanding**) and heat-treating steps. Fig. 1(a) is a
double-taper round tube: 2D at the inlet -> reduced to D -> expanded to 6D, i.e. the **6:1
maximum = a 3:1 reduction + a 2:1 expansion**; a *pure* reduction beyond **3 1/2:1** caused
significant surface-roughness and flow-area variation (excessive flow losses). Fig. 1(b):
past a 3:1 taper the tube is **bifurcated** - the 3D round tube splits into two mirror
half-"D" tubes that each expand back to 3D (6D total pair width). After tapering the tube is
**bent to the chamber contour, then "spanked" (pressed) to the required design cross-section
at each longitudinal position** - round sections shown, "although oval shapes have been used
extensively". Bifurcation joints (Titan II Stage I, F-1) are persistent trouble spots
(fitup, weld dropthrough, center-wall deformation). Titan II Stage II retrofit: tube wall
thickened 0.024 -> 0.037 in over a 2 in transition in the combustion zone, combined with a
3 1/2:1 diameter ratio. **Fit-up**: stacked tubes produce unbrazeable gaps or overtight fits
from tolerance build-up, overcome by **shims, preferential use of over- and under-size
tubes, peening**, and vendor QC; **round or slightly oval tubes are easiest to fit up because
gaps can be seen** `[SP-8087 p.13-14]`. Implication: a real brazed bundle is *contiguous* -
every tube touches its neighbours across a braze seam at every station.

**Bifurcation joint criteria** `[SP-8087 §3.1.1.3.3 p.56, Fig. 6]`: two methods — (1) full
welding with tube ends formed into mirror-image "D" shapes, joined by an edge weld then a
butt weld to the primary tube (fit tolerance **0.003 in. / 0.076 mm**, do not force the
fit — center-wall deformation risk); (2) brazing, with secondary tubes inserted into the
primary tube (avoid forcing). This matches and adds construction-method detail to
`[SP-8120]`'s splice-joint criteria (which recommended the "D" shape for tubes over 0.5 in.
diameter and cold-side joggle placement) — the two sources corroborate rather than conflict.

## Key results — §2.1.1.4/§3.1.1.4: Channel walls, including "double-wall construction" (the NASA/Western name-equivalent to Russian sandwich construction)

**This monograph does NOT use the word "sandwich" anywhere** (confirmed by an explicit
text search across all 130 pages — the one "sandwich" hit is an unrelated porous-wall
context). The NASA-standard term for the functionally closest construction is
**"double-wall construction"** or "channel-wall construction," and it is described in a form
that is a real but much simpler/lower-performance cousin of the Russian sandwich wall
familiar from RD-170/RD-253-class engines:

**Two named channel-wall sub-types** `[SP-8087 §3.1.1.4 p.58]`:
1. **Dual concentric shells** forming a coolant passage between them, with the coolant
   channeled by a **helically-wrapped wire** inserted in the gap between the two shells —
   this is the "double-wall construction" proper. Axial flow used "whenever practical,"
   helical flow "when necessary" (for higher velocity in a fixed annular gap).
2. **Monolithic construction with drilled coolant passages** within a single shell (the
   Agena's method) — segments drilled separately then joined by manifolding into a
   monolithic chamber.

**Real double-wall implementations** `[SP-8087 §2.1.1.4 p.14]`: **Atlas vernier** — inner
shell spun to shape, a square wire helically hand-brazed to the inner shell, enclosed by a
split outer shell contoured to fit within 0.010 in., with weld joints at the splits pulling
the halves snugly against the wire. **Aerobee** — inner shell with a welded flow guide on
the cylindrical section; through the converging/diverging nozzle, the flow passage is a
helical groove machined into a four-piece filler-block assembly held against the inner
shell by compressed springs, all enclosed by a cylindrical outer shell. Neither design
experienced overheating at the helical-guide contact points (guide widths were sized to
minimize heat-flow blockage), and neither showed flow-separation or velocity-depression
problems in their high-aspect-ratio passages — though both *did* have early overheating at
the coolant entrance/convergent-section transition, fixed by passage redesign.

**Design criterion — Double-Wall Construction** `[SP-8087 §3.1.1.4.2 p.59]`: *"When the flow
guide is not attached to both walls, double-wall construction shall minimize interpassage
leaks."* Dimension the outer shell for a fit from slight interference to ±0.010 in.
(0.254 mm) clearance; prefer an interference fit where possible; if assembled in two halves,
design weld joints to pull the shells into contact. **If no flow bypass is tolerable, braze
or weld both shells to the guide** — braze gaps should be < 0.004 in. (0.102 mm), achieved
by tight tolerances, hand fitting, dissimilar-metal thermal-expansion tricks (greater
expansion for the internal shell), or rolling the external surface.

**Why the real Russian sandwich construction is a materially different (more advanced)
implementation of the same basic idea**: this NASA double-wall method uses a *single
helical channel* wound with wire between two shells — one long spiral passage, used only on
**small, low-heat-flux units** (per the §3.1.1.1 criterion table above: Atlas vernier and
Aerobee are exactly the "thrust < 20,000 lbf, low heat flux" case). The Russian sandwich
wall (used on high-Pc, high-heat-flux engines like RD-170/RD-253/RD-180's chamber, not
covered by name in this monograph since it's a 1972 US document) instead uses a **corrugated
or milled-fin core diffusion-bonded/brazed to both face sheets**, forming **many parallel
axial or near-axial channels** rather than one long helix — closer in spirit to this
monograph's "monolithic drilled-passage" or advanced "channel-wall" categories (which this
document explicitly defers to "refs. 5 through 8" and "advanced techniques" without detailing
them, since true high-heat-flux channel-wall/hot-wall milled-liner fabrication was still a
1968-69-era emerging technology at the time of writing — see the Introduction's own note that
"during 1968 and 1969, a resurgence of channel-wall concepts occurred... this effort is in
its development stage and therefore is not covered in detail in this monograph" `[SP-8087
§1 p.2]`). **Conclusion for the requesting session**: this NASA source confirms "double-wall"
is real 1960s-US low-thrust-engine practice and gives real design criteria for that specific
(helical-wire, single-channel) implementation, but it explicitly does NOT cover the
high-performance multi-channel diffusion-bonded construction that Russian engines are known
for — that would need a Russian-specific or more modern source (not yet in this reference
set; the Gubanov USSR-engines paper being read in parallel by another agent this session is
more likely to have it).

**Passage shape criterion** `[SP-8087 §3.1.1.4.1 p.58]`: rectangular channel width/height
ratio **< 2** in high-heat-flux regions (avoids corner velocity-depression effects); ratios
up to **8** acceptable if channel height **> 0.10 in. (2.54 mm)**. Aspect ratios > ~4 should
be checked for flow separation/eddy formation via full-scale plastic-model visual studies.

**Interchannel/land-area criterion** `[SP-8087 §3.1.1.4.3 p.59]`: land regions between
channels must not cause local gas-side overheating — examine 2-D thermal conduction effects
to size land width; for enhanced two-dimensional (fin) cooling, use highly conductive
materials and ensure intimate contact between flow guides and the heated wall.

## Key results — §2.1.1.5/§3.1.1.5: Special thermal and hydraulic criteria

- **Thermal margin**: operate heat-flux-limited coolants at **< 80% of mean burnout heat
  flux** `[SP-8087 §3.1.1.5.2 p.60]` when data exist; if no burnout data exists for a
  candidate coolant, acquire it experimentally before serious chamber design proceeds.
- If cooling margin **< 15%**, keep rectangular passage width/height < 2.0 or passage height
  ≥ 0.2 in. (5.08 mm) — a tighter version of the general passage-shape criterion above,
  triggered specifically by thin thermal margin.
- **Coolant velocity limits**: liquids **< 200 ft/s (61 m/s)**; gases **< Mach 0.3
  recommended, Mach 0.5 absolute maximum** (sonic choking risk at bends/contractions above
  that) `[SP-8087 §3.1.1.5.3 p.61]` — this exactly corroborates `[Sutton]`'s general gas-side
  Mach-0.3-ish guidance already in `topics/06-cooling-and-heat-transfer.md`/injectors
  content, now with an explicit liquid-velocity number this reference set didn't have before.
- **Wall temperature chemical limits** `[SP-8087 §3.1.1.5.4 p.61]`: RP-1 coking above
  **850°F (728 K)**; furfuryl alcohol residue above 600°F (589 K); Aerozine-50 detonation
  risk above 600°F (589 K) — the RP-1 figure (850°F/728K) is slightly higher than
  `[SP-8087's own culture-mate]` `[SP-8087 §2.1.1.5 p.16]` narrative figure of 800–900°F
  quoted earlier in the State-of-the-Art section for the same coolant, and both are in the
  same ballpark as this reference set's existing LOX/RP-1 coking-limit figure in
  `topics/06-cooling-and-heat-transfer.md` (~120 K ΔT coking limit framing) — a real,
  independent corroboration.

## Key results — §2.1.2/§3.1.2: Manifolds (the section flagged by the requesting session)

**Manifold roles and types** `[SP-8087 §2.1.2 p.19]`: the manifold's primary role is to
distribute coolant uniformly so no passage is starved. **Three manifold types**: inlet,
outlet, turnaround. Manifolding is frequently integral with structural supports and
interface flanges (e.g. the inlet manifold integral with the forward flange in two-pass
systems; the turnaround manifold integral with the aft flange when a nozzle extension bolts
on; the outlet manifold always integral with the forward flange).

**Real flow-maldistribution tolerance data point** `[SP-8087 §2.1.2.1 p.19]`: flow
variations **up to 20% have been tolerated in the first pass** of a multi-pass system,
because the coolant is coldest there and the thermal margin is widest near the inlet — but
this variation must be reduced before the final pass, typically via the natural balancing
effect of a common manifold at the turnaround. For **hydrogen-cooled systems** (large density
variation with temperature), flow uniformity is achieved almost exclusively by **analytical**
methods, with parallel circuits precisely tailored to local hydrogen properties at each
station — storable-coolant systems are comparatively easier since coolant density doesn't
vary as sharply.

**Inlet manifold (toroidal) design — two competing theories** `[SP-8087 §2.1.2.1 p.19-20]`:
(1) **variable area / constant flow velocity** (tapered torus) — equal inlet velocity to
every coolant passage, smaller physical size (less trapped propellant, less structural
load), but worse fabrication complexity and some pressure-drop-driven maldistribution
around the torus; (2) **constant area / variable flow velocity** — minimizes pressure loss
around the torus, but produces maldistribution because passages near the inlet see higher
velocity than passages opposite it. **Real-world torus design is a compromise between these
two extremes**, using smooth turns and (often) smooth vanes. Design criterion `[SP-8087
§3.1.2.1 p.62]`: an annular inlet manifold shape should lie *between* constant-area and
constant-velocity; a flow splitter at the torus inlet suppresses dynamic-head effects by
diverting a small portion of flow to feed local passages near the splitter itself.

**Turnaround manifold — common annulus vs. discrete passages** `[SP-8087 §2.1.2.1 p.20,
§3.1.2.1 p.62-63]`: **common annulus preferred for storable coolants** (evens out flow
distribution before the critical final pass); **discrete per-tube passages preferred for
hydrogen** (each channel's flow resistance must be balanced separately as a function of
*local* coolant properties, since a shared annulus can't do that). This is a real,
propellant-specific manifold-topology criterion this reference set didn't have before —
directly relevant to `manifold.py`'s existing `cooling_flow_topology` options
(`"single_pass_countercurrent"` vs. the real-F-1-sourced `"f1_split_reverse_flow"`), since
it gives a *propellant-class* rule (storable → common annulus, hydrogen → discrete circuits)
for which turnaround-manifold style is appropriate, beyond the two topologies the tool
currently models.

**Manifold structural criteria** `[SP-8087 §3.1.2.2 p.63]`: manifolds shall not cause
chamber distortion, form stress concentrations in thin members, or hinder assembly.
Distortion-minimization practices for arc welding: multiple weld passes rather than one,
minor peening (with an explicit caution to consult a structural analyst before peening, to
evaluate local permanent-yield consequences), step welding, minimizing weld material volume;
electron-beam welding preferred over arc welding where possible to further reduce distortion.
**Transition-section criterion**: avoid large bending discontinuities by tapering the
manifold wall over a short (0.5–1 in. / 1.27–2.54 cm) transition between thin cooled sections
and heavy manifolds (Fig. 8), or by asymmetric support of the thin section. This is a
concrete dimensioned number (0.5-1 in. taper length) this reference set's existing
`[SP-8120]` manifold-structural-supports content (weld-quality hierarchy, flutter mitigation)
did not have — the two sources are complementary: `[SP-8120]` covers vane/splitter/dam/tie
*attachment* quality, `[SP-8087]` covers the *thin-to-thick wall transition* geometry itself.

**Real interface-flange manifold construction, Fig. 8** `[SP-8087 §3.1.2.2 p.63-64]`: two
real configurations shown — (a) a **welded flange/manifold** (fuel turnaround manifold with
fully-penetrating welds to the aft coolant-tube ends, at the nozzle-extension attachment
surface); (b) a **brazed flange/manifold with a secondary cooling manifold** (furnace-braze
joint to the aft tubes, plus a separate turbine-exhaust manifold routing hot gas past the
fuel turnaround manifold to the nozzle-extension attachment flange) — a real example of two
manifolds (coolant turnaround + turbine-exhaust/hot-gas) co-located at the same structural
interface flange, which is exactly the kind of multi-manifold structural integration
`[SP-8120]`'s circumferential-manifold section discusses more abstractly.

## Key results — §2.1.3.1: Throat/chamber reinforcement methods (state-of-the-art survey)

**Six real structural-support methods for tubular-chamber throat reinforcement, Fig. 2**
`[SP-8087 §2.1.3.1 p.21-24]`: (a) cylindrical shell (Aerobee, Improved Titan Stage I);
(b) one-piece brazed jacket (J-2, F-1, H-1) or brazed-wire jacket (Improved Titan Stage II)
or bolt-on/weld-on corsets (Titan III Stage II / RL10); (c) banded (Atlas booster/sustainer —
this is the `[SP-8120]` retaining-band case); (d) U-tube integral shell (NERVA); (e)
double-walled inherent integral shell (Atlas vernier); (f) drilled-passageway inherent
integral shell (Agena). **Real comparative reliability finding**: chambers with *less rigid*
structural support (banded, cylindrical shell, wirewrap-only) have shown *more* tube-to-tube
hot-gas leaks after many tests (>15) than chambers with intimate brazed-jacket support —
though the report cautions the causation is entangled with brazing-technique era, not
support-rigidity alone. **Real one-piece brazed-jacket fabrication method** (F-1, J-2, H-1):
coolant tubes pressed against the jacket by a pressurized bag during brazing — described as
"costly and difficult" tooling/procedure development, corroborating this reference set's
existing F-1/J-2 fabrication-difficulty anecdotes from `[SP-8120]`. **Real fatigue failure
mode**: brazed-jacket tube crowns fatigue-cracked at the *aft end* of the jacket from cyclic
structural-resonance loads and a stress discontinuity there (Fig. 3) — fixed by adding
damping bands to the expansion nozzle AND by tapering the jacket thickness + increasing braze
contact in the aft 1-2 in. (2.54-5.08 cm) of the jacket. **Real Titan-sustainer corset
anecdote**: an epoxy-filled space between a split form-fitting shell and the wirewrapped tube
bundle carries shear loads; ground tests showed the corset prevented throat buckling from
asymmetric jet-separation side loads (up to 1.4× limit load) during simulated-altitude-test
termination — flown both with and without the corset, but its structural contribution was
demonstrated by test.

## Design method (mostly criteria/practices; a few genuinely new dimensioned numbers)

Like `[SP-8120]`, most of this monograph is qualitative design guidance and real-hardware
precedent rather than closed-form sizing equations. However, unlike `[SP-8120]`, this
document DOES give several directly-usable **dimensioned selection thresholds** not
available elsewhere in this reference set: the heat-flux/thrust-based tubular-vs-channel-wall
selection criterion (12 / 25 Btu/in²·s, 20,000 lbf), the 3:1/6:1 tube-taper limits, the
0.010 in. minimum tube-wall-thickness recommendation, the < 200 ft/s liquid / Mach 0.3-0.5
gas coolant-velocity limits, and the manifold-to-thin-wall transition taper length
(0.5-1 in.). These are genuinely new, citable numbers for `engine_designer/ASSUMPTIONS.md`
consideration (see topic-file implications) — a step up from `[SP-8120]`'s purely qualitative
criteria.

## Section map

- §1 Introduction: p.1-3 (leaf 16-18) — read (includes the important note that advanced
  channel-wall/hot-wall-liner fabrication was, as of 1972, "in its development stage" and
  "not covered in detail in this monograph").
- **§2.1.1/§3.1.1 Coolant Passages (incl. channel walls/double-wall construction): p.8-17,
  54-62 (leaf 23-32, 69-77) — read in full, see Key results above.**
- **§2.1.2/§3.1.2 Manifolds: p.19-20, 62-63 (leaf 34-35, 77-78) — read in full, see Key
  results above.**
- **§2.1.3.1 Throat Reinforcement (State of the Art only): p.21-24 (leaf 36-39) — read in
  full, see Key results above.**
- §2.1.3.2-3.1.3.3 Chamber/Nozzle Reinforcement, Interface Flange (State of the Art +
  Design Criteria): p.25-30, 65-68 (leaf 40-45, 80-83) — not read this pass.
- §2.1.4/§3.1.4 Materials Compatibility: p.27-30, 68 — not read.
- §2.1.5/§3.1.5 Structural Analysis (buckling, composite loads, tube compressive/fatigue
  strength): p.30-32, 68-70 — not read; likely candidate for a future pass if quantitative
  band/tube stress-allowable numbers are needed (this is exactly the gap `[SP-8120]`'s
  Caveats flagged as unfilled).
- §2.1.6/§3.1.6 Brazing: p.33-37, 70-75 — not read (braze-alloy selection, joint-gap/
  cleanliness/motion-restraint procedure, braze-cycle repeatability).
- §2.1.7-2.1.10/§3.1.7-3.1.10 (Chamber Assembly/Passage Degradation, Laboratory Proof
  Testing, Operational Problems incl. transient/heatsoak/drain-ports, Handling/
  Transportation): p.35-41, 76-85 — not read.
- §2.2/§3.2 Transpiration Cooling: p.43-48, 85-91 — not read (out of scope; this monograph's
  own scope note says it "concentrates on regenerative cooling").
- §2.3/§3.3 Film Cooling: p.49, 91-93 — not read.
- §2.4/§3.4 Coatings: p.51, 93 — not read.
- References: p.95-100 (not chased). Glossary: p.101-106 (not read).

## Caveats

- **1972 vintage, explicitly pre-advanced-channel-wall**: the monograph's own introduction
  says advanced non-tubular channel-wall/hot-wall-liner chambers were "in development" as of
  1968-69 and are "not covered in detail" — so this source's channel-wall content (double-wall,
  drilled-passageway) describes only the *simple*, lower-performance implementations used on
  small vernier/sustainer engines, not the high-heat-flux milled/electroformed liners that
  became standard on later engines (SSME, RS-68, modern methalox engines) or the Russian
  sandwich-wall construction. Treat the double-wall-construction content as historically
  accurate for its era and useful for *small, low-heat-flux engine* design, not as a general
  substitute for modern channel-wall/sandwich design guidance.
- **No "sandwich" terminology**: confirmed via full-document text search — if a future
  session needs Russian-sandwich-wall-specific design criteria (multi-channel diffusion-bonded
  core between face sheets, used on RD-170/253/180-class high-Pc engines), this source does
  not have it; a Russian-engine-specific source is needed instead.
- OCR quality is mixed: cleanly-typeset body-text paragraphs read well, but several pages
  (especially tables, e.g. leaf 24/26/32/75) are pure scanned-image/graphics pages with
  garbled or absent extractable text — those pages were skipped rather than force-transcribed.
  Some narrow-column dense-numbers passages (e.g. leaf 25's "Number of Passes" section) have
  visibly corrupted OCR with letters transposed/dropped; the technical content was
  reconstructed by inference from context and cross-reference to the parallel §3 criteria
  text, which is generally cleaner (design-criteria language is simpler and OCR'd better than
  the denser narrative prose).
- Real numeric values throughout (heat flux thresholds, tube taper ratios, wall thicknesses,
  velocity limits) are recommended *practices*, not universal physical limits — the monograph
  itself frames coolant-passage-configuration selection as historically driven more by
  "designer experience and fabrication knowledge" than by rigorous optimization (§2.1.1.1,
  explicit statement that two designers with the same requirements could reach equally valid
  but different designs).
