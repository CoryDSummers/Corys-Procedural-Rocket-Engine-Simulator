# NASA SP-8120 — Liquid Rocket Engine Nozzles

## Identity

NASA Space Vehicle Design Criteria (Chemical Propulsion) monograph SP-8120, *Liquid Rocket
Engine Nozzles*, July 1976. `literature/NASA SP-8120 - Liquid Rocket Engine Nozzles.pdf` (NTRS 19770009165; 126 PDF leaves; printed-page
numbering runs ~13 pages behind the PDF leaf index — printed p.N is PDF leaf N+13).
Tag: `[SP-8120]`.

## Character

One of the standard NASA SP-8xxx design-criteria series (same series as `[SP-8081]` gas
generators and `[SP-8107]` turbopumps already in this reference set). Two parallel numbered
sections that track each other 1:1: **§2 State of the Art** (narrative, pp.3–63) explains
*why*, with real-engine failure/fix anecdotes; **§3 Design Criteria** (pp.65–89) is the
prescriptive, imperative-mood distillation ("shall...", "do not...") of the same subsections
— read §3 first for the rule, §2 for the reasoning and the anecdote behind it. Appendix A is
a glossary, Appendix B a units conversion table, followed by references and a list of all
SP-8xxx monographs issued to date (this document predates `[SP-8081]`/`[SP-8107]` by several
years — 1972/1974 vs. 1976 — but overlaps their scope only at the injector/manifold
interface, not turbopumps or GG design).

Full top-level structure (§2 State-of-the-Art page / §3 Design-Criteria page):

| Subject | §2 p. | §3 p. |
|---|---|---|
| 2.1 Nozzle Configuration (throat geometry, bell/plug contour, tolerances) | 3–24 | 65–70 |
| **2.2 Nozzle Structure** | **25–63** | **71–89** |
| — 2.2.1 Regeneratively Cooled Nozzles and Extensions (retaining bands, splice joints) | 27–33 | 71–72 |
| — 2.2.2 Film-Cooled Extensions | 34–37 | 73–75 |
| — 2.2.3 Ablation-Cooled Extensions | 37–40 | 76–77 |
| — 2.2.4 Radiation-Cooled Extensions | 40–42 | 77 |
| — **2.2.5 Circumferential Manifolds** (hydraulics, vanes/splitters/dams/structural supports, hot-gas manifold) | **42–55** | **78–83** |
| — 2.2.6 Nozzle Attachments | 55–57 | 83–84 |
| — 2.2.7 Instrumentation Provisions | 57–60 | 85–87 |
| 2.3 Testing (full-scale, model) | 60–63 | 87–89 |

## This note's extraction scope

**Fully read, 2026-09-24** (previously only §2.2.1/§3.2.1 and §2.2.5.2/§3.2.5.2 were deep-read;
everything else was headers-only). The remaining ~70% — §2.1/§3.1 (nozzle configuration:
throat/bell/plug geometry, contour tolerances), §2.2.2/§3.2.2 (film-cooled extensions —
the real F-1 turbine-exhaust-gas nozzle extension), §2.2.3/§3.2.3 (ablation-cooled
extensions), §2.2.4/§3.2.4 (radiation-cooled extensions), §2.2.5.1/§3.2.5.1 (manifold
hydraulics), §2.2.5.3/§3.2.5.3 (hot-gas manifold — real turbine-exhaust-introduction
schemes and F-1/J-2/Titan/Atlas real hardware), §2.2.5.4/§3.2.5.4 (coolant-return
manifold), §2.2.6/§3.2.6 (nozzle attachments), §2.2.7/§3.2.7 (instrumentation), and
§2.3/§3.3 (testing) — was read in full via pymupdf (clean OCR throughout, no image
rendering needed). All key results below.

**Why this matters beyond general completeness**: §2.2.2 (Film-Cooled Extensions) and
§2.2.5.3 (Hot-Gas Manifold) are exactly the SP-8120 content flagged as needed reading for
the planned turbine-exhaust-handling feature (`OPEN_QUESTIONS.md`, plan
`~/.claude/plans/floofy-dazzling-liskov.md`) — this pass resolves that reading item.

## Key results — §2.2.1 / §3.2.1: Regeneratively cooled nozzle structure

**The core structural problem** `[SP-8120 §2.2.1 p.27]`: a tube-wall nozzle's tube bundle has
"little resistance to external loads arising from side loads during startup, flow
separation, or mechanical forces from attachments" — the tubes alone cannot react these
loads, so either a continuous outer shell or intermittent rigid **retaining bands** are
required. Continuous shell is normally used near the chamber/throat; bands take over
downstream because wall pressure (and thus required support) drops rapidly aft of the
throat, and bands there give a real weight/cost/fabrication win (less braze alloy, easier
braze tolerance control, reduced moment at the gimbal for a lower nozzle-aft-end weight).

**Band sizing rules as stated** `[SP-8120 §2.2.1.1 p.29]` (PDF leaf 43): bands are normally
solid metal straps (fiberglass wrap / wire winding also possible), sized "to withstand all
internal-pressure hoop loads and external loads such as gas-flow separation, side loads, and
accessory attachments"; the tube-to-band braze ties the bundle to the band "so that the
nozzle reacts to loads as a unit"; the braze joint must also carry the **axial** load from
nozzle pressure acting on a diverging section. **"Required retainer band spacing is
determined by analyzing the unsupported tube length that can be allowed at operating
(pressurized) conditions. Retainer band width depends primarily on band dimensions
necessary to withstand the required operational loads."** Fig. 40 (PDF leaf 86, viewed as an
image 2026-09-23): (a) low buckling resistance = a flat strap with chamfered/thinned edges,
or a trapezoidal strap thick in the middle; (b) high buckling resistance = a square-crowned
sheet-metal **hat** (feet brazed to the tubes, webs ~0.6-0.8x the width tall), a hat closed
around a **round tube** (closed section), and a round-crowned **omega**.

**Design criterion §3.2.1.1.1 "Structural Adequacy"** (imperative, p.71): *"Retaining bands
shall accept all nozzle hoop loads... Shape and size the retaining bands for start-transient,
overexpansion, and gimbal loads. Do not require the tube bundle to withstand any loads from
exhaust gas or mechanical forces. Make the bands rigid rather than flexible."* — i.e. the
band, not the tube wall, is the load path; the tube wall's job is purely to hold pressure/
transfer heat.

**Design criterion §3.2.1.1.2 "Tube-Bundle Rigidity"** (p.71): two band cross-sections
recommended (Fig. 40) — a simple flat band for low buckle-resistance regions (near the
throat) vs. a stiffer profile for high buckle-resistance regions (near the exit); most
nozzles use the simple type near the throat and the stiffer type near the exit.

**Design criterion §3.2.1.1.3 "Tube Support"** (p.71–72): each band must support each tube
radially; minimize braze-gap tolerance stack; never force a band against tubes via local
external load, manifold interference, or an inconsistent band-to-tube contact angle (these
are the three real failure modes catalogued in Fig. 15, below); shim excess gaps rather than
force-fitting; never place a band over/adjacent to a tube-shape discontinuity (stress
concentrator); use a **thinned band cross-section at the band edge** — the single specific
fix cited for the F-1 stress-concentration finding below.

**Real failure-mode catalog, Fig. 15** `[SP-8120 §2.2.1.1 p.29–30]` — six documented root
causes of retaining-band-related tube damage, all from real hardware experience:
1. High-low tube alignment → excessive braze-joint gap → inadequate bonding + overstress of
   the tubes the band actually contacts.
2. High-low tube alignment (forced interference) → local tube crown depression when the band
   is forced to the low-tube dimension to control braze gap.
3. Variable/inconsistent band-to-tube contact angle → nonuniform circumferential braze gaps
   → poor joints or dented tubes.
4. Nondistributed (concentrated) external load → local tube damage.
5. Band loading from improper hardware fit or differential weld shrinkage during fabrication
   → local tube interference/damage.
6. Fix for (1)/(3): shim stock inserted between band and tube to close excess gaps.

**Real quantitative data point — F-1 engine** `[SP-8120 §2.2.1.1 p.31]`: the F-1 nozzle used
*rectangular* retaining bands. Instrumented, hot-fire-tested tube-to-band intersections
measured **axial stress-concentration factors up to 2.2** (analysis: up to **2.8** axial,
**2.45** bending — measured value is likely an underestimate since strain-gage placement in
a sharp corner is difficult). No design change was made to the F-1 nozzle despite this — but
tube failures did occasionally occur at the tube-to-band joint after many test firings.
**Reducing the band thickness specifically at the band edge reduced the stress
concentration** (this is the mechanism behind the §3.2.1.1.3 "thin band section at the edge"
criterion above, and the Fig. 40(a)-vs-(b) low/high-buckle-resistance geometry choice).

**Real failure/fix — J-2 → J-2S** `[SP-8120 §2.2.1.1 p.29]`: an early J-2 engine suffered
localized buckling of an aft retaining band from nozzle side loads at *startup* (a transient
load, not steady-state — consistent with §3.2.1.1.1's explicit call-out of start-transient
loads as a sizing case). The original fix was structurally adequate but expensive and heavy.
For the J-2S (an improved J-2 variant), the band was **redesigned for buckling resistance
while being lighter and easier to fabricate** — cited as a case where an early, expensive/
heavy fix was later replaced by a better-engineered, lighter one once there was time to
redesign properly rather than patch.

**Material note** `[SP-8120 §2.2.1.1 p.31]`: retaining-band material must be braze-compatible
with the tube material (as-supplied or plated). A controlled furnace-braze cooldown cycle
successfully produces the needed mechanical properties in age-hardenable band alloys —
**Inconel 718 and Inconel X-750** are named. Braze-cycle witness coupons are used to verify
post-braze mechanical properties.

**Vibration/fatigue** `[SP-8120 §2.2.1.1 p.30]`: nozzle structural vibration modes are
"very difficult to predict"; vibrational stress superimposed on tube pressure + thermal
stress has caused joint cracks at the retainer-band-to-tube intersection in real hardware.
Best practice found: strain gages at suspected high-stress tube-to-band intersections during
nominal hot-fire, used to predict fatigue life empirically rather than relying on analysis
alone (analytical methods per refs. 34/37 predict natural frequency and dynamic load, but the
monograph frames test-derived strain data as the more trustworthy fatigue-life input).

**§2.2.1.2/§3.2.1.2 Tube Splice Joints** (p.31–33, 72): when a fixed tube count can't be
tapered/formed enough to match the nozzle's increasing circumference toward the exit, tubes
are "spliced" — one incoming tube becomes two (or more) outgoing tubes downstream (a
bifurcation joint), most common in the nozzle and rare in the chamber. Criterion: *avoid
splice joints entirely where possible* (single continuous tubes preferred); if unavoidable,
use a high-ductility tube material (**347 CRES or nickel**) to allow a higher taper ratio
before splicing is needed; contour the splice smoothly; put any joggle (offset) on the
*cold*-gas side of the tube, never the hot-gas side (Fig. 41) — a joggle on the hot side is a
stress-concentration/crown-depression risk right where wall temperature is highest; for
tubes over 0.5 in. diameter, prefer a "D"-shaped splice joint over a rectangular one
(Fig. 16(b) vs. 16(a)).

## Key results — §2.1 / §3.1: Nozzle Configuration (newly read, 2026-09-24)

Mostly overlaps `[Huzel]`/`[Sutton]`'s bell/conical treatment already in `topics/02-nozzle-
contour-design.md`, but with real dimensioned numbers and a real methodology those sources
don't give:

**Throat wall radii — real design criteria** `[SP-8120 §3.1.1.1 p.65]`: bell-nozzle upstream
wall radius ratio Ru/Rt **shall stay > 0.6**; best compromise of efficiency vs. throat
surface area is **Ru/Rt ≈ 1.0**. Downstream wall: for tube-wall nozzles, minimum tube-bend
radius = **2× tube OD** for round tubes of stainless/nickel/copper (ductile materials);
`[SP-8120 §2.1.1.2 p.11]`'s narrative additionally gives **Rd/Rt ≈ 0.4** as "a good compromise
between fabrication difficulty and minimum nozzle length for tube-wall construction," and
(for 15°-half-angle conical-divergence nozzles specifically) Rd/Rt should not go below
**~0.75** to avoid an adverse pressure gradient increasing downstream-wall heat transfer.
Real large-radius-inlet finding: Ru/Rt = 1.4 has been shown effective for **boundary-layer
film cooling through the throat** — a real precedent if `engine_designer` ever wants a
throat-inlet-radius-vs-cooling tradeoff.

**Real chemical-kinetics (nonequilibrium) design rule** `[SP-8120 §3.1.2.1.1.2 p.66]`: when
nonequilibrium losses matter (high-energy propellants like F2/H2 — narrative cites 5-10%
performance loss otherwise), the geometry from the throat to **area ratio ≈ 3** shall control
the initial expansion rate to keep composition near equilibrium, using simple large-radius
circular arcs (< ε 3) or arc+straight-segment combinations (> ε 3) — a specific, quotable
area-ratio threshold for where kinetics-driven contour control matters, absent from
`[Huzel]`/`[Sutton]`'s treatment.

**Real overexpansion/separation design margin** `[SP-8120 §3.1.2.1.3 p.67-68]`: if the
predicted exit wall pressure is **within 20% of the separation pressure**, the design
criterion is to reduce area ratio or select a nonseparating contour — a real, quotable
safety-margin percentage for flow-separation risk, more specific than `topics/01`'s existing
`Pe/Pamb` separation-onset correlation. The nonoptimum-contour performance-loss tolerance for
choosing a canted-parabola over rigorous optimization is **~0.25%** `[§3.1.2.1.2 p.67]`.
Real separation correlation (narrative, `[SP-8120 §2.1.2.1.3 p.17]`, ref. 24): `Pwall/Pamb =
0.583·(Pamb/Pc)^0.195` — an explicit closed-form alternative to the older flat "danger of
separation at Pe/Pamb = 0.4" rule of thumb.

**Real J-2 contour-tolerance anchor** `[SP-8120 §2.1.3 p.23]`: throat-diameter tolerance
**±0.030 in. on a 14.7-in. throat** (~±0.2%), circumferential contour-deviation tolerance
**0.025 in./in.** — a real large-tube-wall-nozzle manufacturing precedent. Design-criteria
counterpart `[§3.1.3 p.70-71]`: wall-angle tolerance **±1° for the first 10° of overturning,
±2° for the rest of the nozzle** downstream of the throat.

**Plug/aerospike nozzle — real design guidance (partial fill for the open aerospike-base-flow
gap)** `[SP-8120 §2.1.2.2/§3.1.2.2 p.20-23, 69]`: this is a genuinely useful complement to
`[Aerospike-CR135231]`'s finding that no base-flow physics exists anywhere in that source —
SP-8120 has real (if qualitative/methodological, not closed-form) base-design guidance:
**base bleed introduced via a porous plate** (favored — frees the cavity volume for
turbomachinery) vs. a **deep-cavity base** (equal performance, normal-to-axis secondary-flow
injection) — highest base-thrust performance comes from introducing secondary flow with
**minimum axial momentum**. Real cycle-dependent guidance: GG-cycle engines use truncated
ideal nozzles **with** base bleed (turbine exhaust dumped to the base); topping/expander
cycles must **regeneratively cool the base plate without bleed**, or bleed only the minimum
fuel needed to cool it. **Shrouded plug nozzles recommended for area ratio > 40 AND thrust <
1×10⁶ lbf**; very large engines should use unshrouded with a segmented injector — a real,
quotable shroud-vs-unshrouded selection criterion `[Aerospike-CR135231]` didn't have (that
source's dual-fuel split-combustor architecture is unrelated to this single-propellant
plug-nozzle treatment). **Base-pressure prediction method**: scale from cold-flow model
tests (ref. 32) for truncated ideal nozzles specifically — theoretical methods (refs. 33/34)
exist only for other annular configurations or examining exit-flowfield effects on base
pressure; base heating rates "can be predicted only approximately and must be verified
experimentally" — i.e. still no closed-form base-pressure/base-heating equation, but a real
named prediction *methodology* (cold-flow-model scaling) neither `[Aerospike-CR135231]` nor
any other source in this reference set gives. Real overexpansion/shock-impingement design
approach for booster-application plug nozzles: use truncated-ideal contours to minimize
incident-shock strength during low-altitude operation; where shocks are still expected,
analyze for boundary-layer separation and size the cooling circuit for the resulting
separated-flow heat flux.

## Key results — §2.2.2-2.2.4 / §3.2.2-3.2.4: Extension structure (newly read, 2026-09-24)

**§2.2.2 Film-Cooled Extensions — the real F-1 turbine-exhaust-gas nozzle extension, the
single most valuable finding in this pass for the planned turbine-exhaust-handling feature**
`[SP-8120 §2.2.2/§3.2.2 p.34-37, 73-75]`: "the nozzle extension for the F-1 engine is the
only example of a film (gas)-cooled extension in production." Real geometry: the
**regeneratively cooled section extends to area ratio 10:1, the film-cooled extension to
16:1** — a real, exact expansion-ratio anchor for where turbine-exhaust film cooling picks
up on the highest-thrust single-chamber engine ever operational. Construction: an outer skin
connected by "Z" stringers to inner **shingles** (all Hastelloy C), overlapping to form slots
through which turbine exhaust gas flows, shielding the shingles from the main hot gas.
**The core design problem and its real quantitative fix**: large separation distance between
the main gas stream and the coolant-gas stream, plus nonparallel coolant injection, caused
the main flow to detach and reattach downstream, destroying the protective film layer at the
reattachment point and burning out shingles there. Fix: concentrate a large fraction of the
total film-coolant flow **at the attachment region** — **experimentally determined to be
about 25-30% of the total coolant-gas flow** — while leaving enough for the rest of the
extension. **No analytical technique available at the time could predict this split; it had
to be determined by full-scale hot-firing.** This 25-30%-at-attachment split is a real,
citable film-cooling-distribution data point directly relevant to any turbine-exhaust
film-cooling model. Real effectiveness rule (citing refs. 44/45): minimum stream mixing (most
effective film use) occurs when the gaseous film coolant is injected **parallel to the main
gas stream, at the highest possible velocity, with the smallest gas-stream separation**.
**Real materials/failure-mode detail**: rigid shingle designs are subject to thermal
distortion → local liner failure; the production F-1 design uses a **dimpled-sheet** shingle
that limits deflection both directions without letting slots close or over-open. Ductile
shingle/structural materials required to avoid low-cycle thermal fatigue: **Inconel 625,
Hastelloy C, or 347 CRES**. Circumferential turbine-gas maldistribution caused local coolant
starvation and shingle warping — fixed by adding holes in the Z-stringer members to improve
crossflow distribution. Fusion welding of Z-members to shingles caused hot-gas-side
protrusions → boundary-layer interruption → erosion/failure; fixed by spot/seam welds ground
flush. **Retaining-band thermal management specific to hot extensions**: bands scalloped
along the weld joint + insulation inserted underneath to reduce band operating temperature
and weight (design criterion, `[§3.2.2.3.3 p.75]`: **overdesign aft retaining bands by 50%
during initial design** to cover uncertainty in start-transient side loads — a real,
quotable design-margin number with no equivalent elsewhere in this reference set). Band
spacing directly controls extension contour/gas-flow quality after repeated firings — widely
spaced bands let the boundary layer detach at intermediate points (excessive erosion),
closely spaced bands don't.

**§2.2.3 Ablation-Cooled Extensions** `[SP-8120 §2.2.3/§3.2.3 p.37-40, 76-77]`: real Titan
extension construction — tape-wound ablative liner (strong enough alone to carry hoop loads
from internal wall pressure, 28→13 psi at the ε=15:1 exit) backed by a **glass-cloth/
honeycomb-sandwich structure that is 20% of total nozzle weight**, added purely for
start-transient/gimbal support, not hoop-load capacity. Attachment: a simple flat horizontal
flange with a stepped liner interface, silicone-RTV seal, bolted — **all loads must route
through the external glass-wrap/honeycomb structure, never through the ablative liner
itself** (design criterion) — a real Titan failure mode when inserts were bonded directly
into the ablative composite instead of into bonded aluminum flange segments (insufficient
insert length for shear, and ablative-material creep made torque requirements unmeetable).
Honeycomb channels must interconnect via drilled passages to vent pyrolysis-gas pressure
buildup (a real structural-failure mode otherwise).

**§2.2.4 Radiation-Cooled Extensions — real material temperature bands** `[SP-8120
§2.2.4/§3.2.4 p.40-42, 77]`: **below 2000°F**: titanium alloy AMS 4917 (low-temp), cobalt-base
L-605 or stainless N-155 (no protective coating needed). **Above 2000°F**: refractory metals
required — columbium C-103 with a NAA-85 aluminide oxidation-barrier coating is the named
real example; refractory-metal extensions have had "much greater" development problems than
standard metals. Real emissivity finding: anodizing/roughening aluminum raises emissivity
from **0.1 (clean) to 0.9 (dark anodized)**, reducing wall temperature by as much as **100°F**
— a real, quantified radiative-cooling material-finish lever with no counterpart in
`cooling.py`'s flat emissivity treatment. Joint/seal guidance: elastomeric seals workable to
500°F; above that, pressure-assisted seals (Naflex/K-seals) for flight hardware, tadpole-type
asbestos/wire-mesh seals for development hardware. Nonyielding flange designs + closely
spaced high-temp clamping bolts (Rene 41 named) minimize joint cracking/leaking from flange
yielding under refractory-extension thermal loads.

## Key results — §2.2.5.1 / §3.2.5.1: Manifold Hydraulics (newly read, 2026-09-24)

**Real manifold-velocity design criterion — directly relevant to `manifold.py`'s velocity
target, a candidate answer to the open "manifold velocity-head/injector-dP ratio" question**
`[SP-8120 §3.2.5.1 p.78]`: *"Keep the fluid velocities in the manifold as low as possible,
preferably **less than 60 fps for liquids and less than Mach 0.25 for gases**."* This is
**more conservative** than `[SP-8087]`'s already-cited limits (200 ft/s liquid, Mach 0.3
recommended/0.5 absolute max for gas) — two independent NASA design-criteria monographs
giving different numbers for what reads as a similar quantity (general distribution-manifold
velocity vs. `[SP-8087]`'s coolant-jacket-passage velocity specifically), worth flagging as
a real discrepancy rather than silently picking one if `manifold.py` ever wants a literature-
sourced velocity target. Narrative context `[§2.2.5.1 p.42]`: weight limits force minimum
manifold volume and high velocity; **liquid velocities of 50-100 fps and gas velocities of
Mach 0.25-0.4 have resulted in real maldistribution** (tube starvation, inadequate local film
coolant) — i.e. the 60 fps/Mach 0.25 design criterion sits right at the low end of a real
observed maldistribution-onset band, not an arbitrary round number. Real inlet-configuration
fixes for static-pressure variation near a manifold inlet: multiple tangential inlets,
multiple low-velocity radial inlets, or a single/multiple radial inlet with turning vanes or
deflector plates (Fig. 24) — all lower the local inlet velocity or spread the momentum
input. Real fix for along-manifold static-pressure variation: taper the manifold
cross-section (constant-velocity philosophy) — for low-volume production, a circular torus
bored off-center to vary cross-section approximates the same effect cheaply. Even with a
well-designed tapered/turning-vane inlet, a real residual pressure *rise* still occurs at the
manifold's final stagnation point (opposite the inlet) — addressed by increasing flow
resistance in/downstream of the bleedoff ports there, not by further inlet tuning.

## Key results — §2.2.5.3 / §3.2.5.3: Hot-Gas Manifold (newly read, 2026-09-24) — the second
## major finding for the planned turbine-exhaust-handling feature

**Real historical survey of turbine-exhaust disposal methods by engine** `[SP-8120 §2.2.5.3
p.48-50]`: Atlas booster engines originally ducted turbine exhaust axially → fuel-rich
exhaust caused boattail fires; fixed by **canting the exhaust ducts outward** into the
slipstream. Atlas *sustainer*: exhaust conducted around the nozzle end and **entrained into
the main jet, ejected axially** (the `looped-tube`/`annulus-at-exit` pattern SP-8120's
design-criteria section formalizes below). Saturn S-1B's four gimbaled H-1D engines used the
same Atlas-sustainer-style disposal. **F-1**: turbine exhaust used as film coolant for the
nozzle extension (detailed above). **J-2**: turbine exhaust dumped into the main gas stream
through **"cat-eyes"** (long narrow openings between coolant tubes); the tubes just
downstream of the dump point are "partially film cooled but primarily regeneratively cooled"
— real confirmation that J-2's turbine-exhaust handling is a hybrid, not pure film cooling.
**Titan stage I**: turbine exhaust leaves the turbine at **1200°F, 30 psi**, passes through
an oxidizer superheater (extracting heat to raise pressurant temperature) before impinging
on the ablative nozzle extension — real measured **side loads from this impingement: 90±20
lbf axial, 360±50 lbf lateral**, inducing an axisymmetric vehicle roll moment of
**~250 ft-lbf** (corrected on Titan II by an additional small roll-control nozzle using
turbine exhaust — impingement of *that* nozzle's exhaust on the main extension's ablative
surface during swiveling caused local heating/structural damage, fixed by bonding low-density
silica matt over the exposed area). **Real overall-performance contribution**: turbine
exhaust gas thrust potential is typically **~0.5% of total engine thrust** — for large
engines (**16,000 lbf potential for the F-1** specifically) this is large enough that the
supporting structure needs careful load analysis. **Real safety hazard, noncryogenic
propellants specifically**: a looped-tube turbine-exhaust configuration on an experimental
Atlas sustainer engine let RP-1 get trapped in exhaust-manifold pockets during fuel-rich
cutoff; **LOX/RP-1 gel formation from the trapped fuel caused detonations at the start of the
following test** — cryogenic propellants (J-2's LH2) evaporate between runs and don't have
this failure mode. This is a real, concrete, safety-relevant finding: **the looped-tube
turbine-exhaust-into-nozzle configuration should not be used with noncryogenic (storable)
propellants** — directly codified as a design criterion below.

**F-1 turbine-exhaust manifold — real thermal-growth/failure-mode detail** `[SP-8120 §2.2.5.3
p.50-52]`: the F-1's manifold is a tapered hot-gas torus rigidly attached to the cooled exit
ring, with **"omega" expansion joints** around the torus shell for thermal growth (potential
radial growth **~0.5 in.**). The recurring real failure area: intersection of the omega
joints with the outer ring (tension cracks from ring-bending under restraint) — fixed by
adding doublers to distribute load over a longer base, increasing cycle life. A separate real
tube-denting failure mode: manifold fabrication/operational distortion caused interference
between the flame shield and the tube retaining band — fixed by increasing the flame-shield-
to-band clearance from **a few thousandths of an inch to about 0.4 in.** Sliding-pin/A-frame
designs (proven in turbojets/ramjets) were considered for the F-1 but dropped in favor of the
production omega-joint design once thermal stresses were reduced enough via other means;
an early sliding-pin/slotted-clevis F-1 exhaust-manifold variant failed from a combination of
insufficient clearances, oversized mechanical loads, and undersized pins — abandoned for
schedule reasons, not fundamental infeasibility. **Real material selection rule by thermal-
stress severity**: for designs kept elastic (low thermal load), relatively brittle materials
suffice (Waspaloy, Rene 41, per turbojet precedent); for high-thermal-load designs like the
F-1 exhaust manifold, materials retaining **≥20% ductility at elevated temperature** are
required — real examples: **347 CRES, Hastelloy C, Inconel 625, L-605**.

**Real hot-gas-manifold design criteria (§3.2.5.3, p.80-82)**: introduce turbine exhaust
either through gaps in the nozzle wall (looped-tube, Fig. 45(a)) or parallel to the main jet
through an annulus at the nozzle exit (Fig. 45(b)), or via a film-cooled extension (F-1
style) — **the looped-tube/gap method shall NOT be used for noncryogenic propellants**
(codifying the real Atlas RP-1-trapping detonation finding above); use the annulus-at-exit
method or a film-cooled extension instead. Thermal growth: use sliding-pin, A-frame, or
similar designs allowing unrestrained expansion, or absorb deflection in bending via a
flexible member (F-1's flame shield, or a flexible baseplate per Fig. 46); distribute thermal
loading at highly-stressed points with doublers; specify ductile materials (≥20% elongation)
per the real-hardware findings above; allow larger-than-normal clearances to account for
weld shrinkage and braze/operational distortion. Seals: self-energizing pressure-actuated
seals recommended for hot-gas manifolds specifically (vs. the broader flange-seal guidance
in §2.2.6/§3.2.6 below).

## Key results — §2.2.5.4 / §3.2.5.4: Coolant-Return Manifold (newly read, 2026-09-24)

`[SP-8120 §2.2.5.4/§3.2.5.4 p.53-55, 82]`: continuous manifolds (tubes inserted into slots or
round holes) are preferred over Titan-style integral-flange 180°-elbow return manifolds —
elbows are harder to drain/clean and don't provide a support ring for nozzle attachments.
**Real tube-to-manifold joint comparison**: square tube ends into slots (needed filler/
powder in corners since tubes couldn't be made with sharp-enough corners; braze-joint
peeling; "oil canning" of flat tube walls; hard tolerance control) vs. **circular tube ends
into round holes with the tube end expanded in place (the real F-1 technique)** — much more
successful bonds, stayed within tight braze-gap tolerance. Real braze-gap/joint-length
numbers: **maximum satisfactory braze gap 0.004-0.006 in.**; **braze-joint length ≥1 tube
diameter** usually gives acceptable joint strength — real dimensioned brazing tolerances with
no equivalent elsewhere in this reference set. Furnace brazing (with production-run braze-
sample witness coupons) strongly preferred over hand brazing for reliability. Real
overheating asymmetry: the down-tube/manifold joint runs hotter than the up-tube/manifold
joint, because the thinner, just-developing boundary layer on the up-tube side gives a higher
liquid-side film coefficient there.

## Key results — §2.2.6 / §3.2.6: Nozzle Attachments (newly read, 2026-09-24)

`[SP-8120 §2.2.6/§3.2.6 p.55-57, 83-84]`: attachments should connect to a nozzle structural
member (retaining band, manifold) rather than directly to tubes; where direct tube
attachment is unavoidable, braze (not weld) and braze on **one side only** (Fig. 48) — a real
counterintuitive-sounding but load-tested finding that two-sided brazing produces *higher*
local tube stress than one-sided. Welding attachments to age-hardenable structural members
must happen **before** the furnace-braze cycle, not after — welding after braze-hardening
destroys the member's braze-induced strength (a real, specific fabrication-sequencing
criterion). Real large-chamber extension-joint numbers: flanges up to **120 in. diameter**;
real-hardware **flange out-of-roundness up to 1.5% of flange diameter**, compensated by
oversized/radial-slotted bolt holes + alignment tools; recommended bolt spacing = bolt-head
diameter + 2× flange thickness; seals must tolerate **up to 50% crush/compression** from
flange waviness.

## Key results — §2.2.7 / §2.3 (Instrumentation, Testing) — brief, low `engine_designer`
## relevance (newly read, 2026-09-24)

Mostly hardware-instrumentation-installation practice (thermocouple/pressure-tap/strain-gage
mounting techniques for real hot-fire test articles) with no design constants relevant to
`engine_designer`'s physics — noted for completeness, not integrated into any topic file.
One real number worth flagging: cold-flow model testing of nozzles is limited by test-gas γ
mismatch (real exhaust γ 1.1-1.3 vs. air's 1.4; CF4's γ=1.2 helps but adds up to 3%
nonequilibrium-expansion loss of its own) and by **air condensation at area ratios above
~15** at 100 psi total pressure — real, useful caveats if `engine_designer`'s own
verification/testing methodology discussion ever needs them, but not a design constant.
Real separated-flow ground-testing precedent (§2.3.1.1/§3.3.1.1): the **J-2's real eps=27:1
nozzle** suffered large unsteady side loads from flow separation during both startup and
steady-state ground testing, requiring nozzle-structure strengthening, removable test-stand
restraining arms, and a bolt-on diffuser to eliminate mainstage separation — a real
concrete instance of the separation-margin design criterion above actually mattering on
flight hardware.

## Key results — §2.2.5.2 / §3.2.5.2: Manifold vanes, splitters, dams, structural supports

**Context** `[SP-8120 §2.2.5.2 p.45]`: large propellant/coolant manifolds are built with thin
walls to save weight and have low allowable pressure drop, both of which favor high-velocity,
flow-maldistribution-prone geometry. Vanes/splitters/dams fix the hydraulic maldistribution;
structural ties keep the thin, flexible manifold shell from failing against the (comparatively
rigid) supporting structure. Often one physical member does both jobs at once.

**§2.2.5.2.1/§3.2.5.2.1 Turning Vanes** (p.45, 78–79): hydrodynamic pressure-distribution
theory (ref. 49) is not accurate enough alone for final sizing on large, expensive, long-
lead-time manifolds — criterion is to design by the theory *and* build in **removable plugs
in auxiliary turning vanes** so the pressure profile can be tuned experimentally (measuring
various plug-removed combinations) without having to physically move/recontour a vane.
Real example: the F-1 turbine-exhaust-gas manifold (film-coolant distribution) used this
method (Fig. 27).

**§2.2.5.2.2/§3.2.5.2.2 Flow Splitters** (p.46, 79): explicitly framed as **a fix for an
existing design that can't be redesigned, not a first choice** — splitters are sensitive to
upstream flow conditions (worse if a variable-position valve changes those conditions in
operation) and a poorly-placed splitter (geometric center of a nonsymmetrical flow) can
*increase* maldistribution rather than fix it. Criterion for new designs: avoid needing a
splitter at all via a symmetrical manifold entrance or lower entrance velocity; if one must
be used, size/locate it experimentally against the measured pressure profile across the full
operating range, not analytically.

**§2.2.5.2.3/§3.2.5.2.3 Dams** (p.47, 79): used to decouple pressure perturbations and "fix"
a manifold's pressure profile — typically a partial or full dam placed at/near the flow
stagnation point opposite the manifold inlet, or between multiple inlets. **Real example:
H-1 engine** fuel-return manifold — nonuniform inlet flow was causing variable cross-velocity
and variable injector-face flow distribution, with **measured engine performance changing
test-to-test**. An **80%-cross-section-area dam** placed opposite the upstream fuel inlet
"considerably reduced" the cross-velocity/stagnation-point variation and **eliminated the
performance changes** — a concrete, quantified example of a manifold hydraulic fix directly
resolving an engine-performance (not just structural) problem.

**§2.2.5.2.4/§3.2.5.2.4 Structural Supports** (p.47–48, 79–80) — the section flagged by the
requesting session:
- **Failure modes** (p.47): differential thermal stress; vibration fatigue; resonant
  flutter; excessive static-pressure loading. Consequence framing is explicit and important:
  *"Even when the failure does not result in a direct structural failure of the nozzle, it
  often produces a maldistribution of fluid flow and results in performance loss, combustion
  instability, or wall overheating."* — i.e. a structural-support failure is as much a
  combustion/performance risk as a structural one.
- **Toroidal manifold shells "breathe"** under internal pressure variation (they're more
  flexible than the supporting structure) — flow distributors/structural ties must either be
  flexible enough to grow with the shell while still locally rigid enough to support it, or
  mounted on one side of the structure with clearance left elsewhere on the circumference (a
  design escape when a rigid all-around tie can't accommodate the breathing).
- **Attachment weld quality ranking** (p.47, Fig. 30, confirmed again as the §3 criterion):
  from worst to best — **fillet weld** ("generally unacceptable" per §2, "avoid... except
  under light loading and low vibration" per §3) → **full-penetration fillet weld** ("much
  better, usually acceptable" / "next choice") → **butt weld** ("a good joint" / "first
  choice when it can be used") → **integral casting** ("excellent where it could be used" /
  criterion: "use integral vanes, splitters, dams, and structural ties whenever possible").
  Attachment location is called out as "extremely critical, since fatigue failure at the
  attachment location is a common failure mode."
- **Flutter mitigation** (Fig. 31): flat surfaces are "extremely subject to flutter," large
  curved sections have also failed from fatigue; adding a splitter in conjunction with vanes,
  or dedicated flutter dampeners, produces a vibration-resistant structure. Criterion: "avoid
  large unsupported sections, particularly flat ones... incorporate flutter dampeners" if one
  must be used.
- **Dam welding** (Fig. 32): partial welds are simplest but most fatigue-prone; continuous
  internal welds and internal-external welds are structurally very good but need weld access
  (limits use to locations adjacent to a manifold); **integral dams (part of the parent
  metal) are "the best design from a structural standpoint and have in general been failure
  free."** Criterion splits by accessibility: use Fig. 32(a)/(b)/(c) joints where internally
  accessible, Fig. 32(d)/(e) where not.
- **General criterion** (§3.2.5.2.4, p.79–80): *"External supports or heavier walls are
  recommended over internal supports whenever possible."*

## Design method (none — this is a criteria/practices monograph, not a sizing-equation source)

Unlike `[Huzel]`/`[Sutton]`, SP-8120 gives design *rules and real-hardware precedent*, not
closed-form sizing equations for band thickness, weld allowable stress, or splice-joint
geometry — "shape and size the retaining bands for start-transient, overexpansion, and
gimbal loads" is a *requirement*, not a formula. Bands/supports are sized by structural
analysis against those load cases (ref. 37/69 cited for the analysis method, not reproduced
in the monograph itself) plus the empirical weld/geometry hierarchy above. Treat this source
as **qualitative design guidance and real-hardware failure-mode/fix precedent**, not a source
of new quantitative constants for `engine_designer/physics/*.py`.

## Section map

**Fully read as of 2026-09-24** — every numbered subsection of §2/§3 has now been read
(only §1 Introduction, the appendices, and the reference list remain unread, all
low-value: front matter, glossary/unit-conversion tables, and a citation list).

- §1 Introduction: p.1–2 (not read — 2-paragraph orientation, no technical content per the
  §2 opening paragraph's own recap).
- **§2.1/§3.1 Nozzle Configuration (throat/bell/plug geometry, contour tolerances,
  separation, plug-nozzle base design): p.3–24, 65–70 — read in full 2026-09-24, see Key
  results above.**
- **§2.2.1/§3.2.1 Regen nozzle structure (retaining bands, splice joints): p.27–33, 71–72 —
  read in full, see Key results above.**
- **§2.2.2/§3.2.2 Film-Cooled Extensions (the real F-1 turbine-exhaust-gas nozzle
  extension): p.34–37, 73–75 — read in full 2026-09-24, see Key results above.**
- **§2.2.3/§3.2.3 Ablation-Cooled Extensions: p.37–40, 76–77 — read in full 2026-09-24.**
- **§2.2.4/§3.2.4 Radiation-Cooled Extensions: p.40–42, 77 — read in full 2026-09-24.**
- **§2.2.5.1/§3.2.5.1 Manifold Hydraulics: p.42–45, 78 — read in full 2026-09-24, see Key
  results above.**
- **§2.2.5.2 Vanes/Splitters/Dams/Structural Supports: p.45–48, 78–80 — read in full, see
  Key results above.**
- **§2.2.5.3/§3.2.5.3 Hot-Gas Manifold (real turbine-exhaust-introduction schemes, F-1/J-2/
  Titan/Atlas real hardware): p.48–53, 80–82 — read in full 2026-09-24, see Key results
  above.**
- **§2.2.5.4/§3.2.5.4 Coolant-Return Manifold: p.53–55, 82 — read in full 2026-09-24.**
- **§2.2.6/§3.2.6 Nozzle Attachments: p.55–57, 83–84 — read in full 2026-09-24.**
- **§2.2.7/§3.2.7 Instrumentation Provisions: p.57–60, 85–87 — read in full 2026-09-24, low
  `engine_designer` relevance (hardware-test-instrumentation practice, not design physics).**
- **§2.3/§3.3 Testing: p.60–63, 87–89 — read in full 2026-09-24, low relevance beyond the
  real J-2 ground-test separation precedent noted above.**
- Appendix A Glossary: p.91–98 (not read — terminology only). Appendix B Unit conversions:
  p.99 (not read — standard unit-conversion factors).
- References: p.101–106 (not read — ref. 35/36/37/49/69/etc. cited above are internal
  cross-references the monograph itself makes, not independently chased here; none appear
  to be primary sources not already better-covered elsewhere in `claude_lit`).

## Caveats

- 1976 vintage — predates SSME/RS-25 (first flight 1981), so unlike `[Ch12-Materials]` this
  source has **no SSME-era structural data**; all real-hardware examples above (F-1, J-2/
  J-2S, H-1, Titan, Atlas) are 1960s Saturn/Apollo/ICBM-generation engines. Treat as
  historically dated but still directly applicable: the physical failure modes (weld
  fatigue, thermal-cycling band buckling, tube-to-band stress concentration, turbine-exhaust
  thermal growth, manifold maldistribution) are geometry/loading-driven, not
  material-era-dependent.
- OCR quality on this PDF is poor in places (concatenated/mis-split words, e.g. "Struc-
  tural" split across lines with no space, sporadic misrecognized characters, e.g. "F-l" for
  "F-1") — all quotations above were reconstructed by eye from the raw extracted text; treat
  exact wording as a paraphrase-grade reconstruction, not a verbatim scan, though the
  technical content itself is unambiguous. No figures were re-rendered as images this pass
  (unlike Fig. 40 in the earlier §2.2.1 extraction) — all newly-read content came from clean
  body-text OCR without needing image rendering.
- **Still a criteria/practices monograph, not a sizing-equation source, even after the full
  read** — genuinely new *dimensioned* numbers did turn up this pass (60 fps/Mach 0.25
  manifold-velocity criterion; 0.004-0.006 in. braze-gap tolerance; ≥1 tube-diameter braze-
  joint length; ±0.030 in./14.7 in. and 0.025 in./in. J-2 contour tolerances; ±1°/±2° wall-
  angle tolerances; 20%-of-separation-pressure margin; 50%-overdesign retaining-band-margin
  rule; area-ratio-≈3 nonequilibrium-control threshold), but there is still no closed-form
  equation for band thickness, weld allowable stress, splice-joint geometry, manifold-
  velocity-head-vs-Δp relationship, or plug-nozzle base pressure — every new number above is
  either a real-hardware measured data point or a stated design-criteria *threshold*, not a
  derivable formula.
- Plug/aerospike base-design content (§2.1.2.2) is real and useful but still not a
  closed-form base-pressure model — "scale from cold-flow model tests" and "predicted only
  approximately, must be verified experimentally" are the monograph's own honest framing;
  `[Aerospike-CR135231]`'s complete absence of base-flow physics is only partially offset by
  this source's real but qualitative guidance.
- The real 60 fps/Mach 0.25 manifold-velocity criterion (§3.2.5.1) and `[SP-8087]`'s
  200 ft/s / Mach 0.3-0.5 criterion (already cited in `topics/12`) are **not reconciled** —
  both are real NASA design-criteria numbers for what may or may not be exactly the same
  quantity (general distribution manifold vs. coolant-jacket-passage velocity); flagged as a
  real discrepancy in `topics/12`'s integration, not silently resolved.
