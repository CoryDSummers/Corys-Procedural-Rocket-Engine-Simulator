# 12b — Structural hardware: retaining bands, manifolds, tube counts, attachments

## Scope

**Split out of `topics/12-materials-and-structures.md` on 2026-09-24** (that file exceeded
the 40 KB lookup-budget cap). `topics/12-materials-and-structures.md` keeps material
selection/properties/alloy data; **this file** covers real structural design criteria and
real-hardware data for tube-wall retaining bands, propellant/coolant manifolds, tube-splice
joints, nozzle attachments, and turbine-exhaust (hot-gas) manifolds. Feeds
`engine_designer/physics/hatbands.py`, `manifold.py`, and `mass_model.py`.

## Empirical correlations & typical values

**Tube-wall nozzle retaining bands** `[SP-8120 §2.2.1.1/§3.2.1.1 p.27-31, 71-72]`: a
tube-bundle nozzle wall has essentially no resistance to side loads (startup, flow
separation, mechanical attachments) on its own - either a continuous shell or intermittent
rigid retaining bands must react all hoop/side/gimbal loads instead, by explicit design
criterion ("do not require the tube bundle to withstand any loads from exhaust gas or
mechanical forces"). Bands go downstream of the continuous-shell region, since wall pressure
(and thus required support) drops rapidly aft of the throat. Two band cross-sections are
recommended: simple flat bands where buckle resistance can be low (near the throat), stiffer
profiles where it must be high (near the exit). **Real F-1 data**: instrumented, hot-fired
tube-to-band joints measured axial stress-concentration factors up to 2.2 (analysis: up to
2.8 axial / 2.45 bending) on F-1's rectangular bands; **thinning the band cross-section at
the band edge reduced the concentration** - the only quantitative fix given. **Real J-2 to
J-2S fix**: an early J-2 aft-band buckling failure (from startup side loads - a transient
load case, not steady-state) was first patched expensively/heavily, then properly redesigned
lighter-and-buckle-resistant for J-2S once time allowed. Band material must be braze-
compatible with the tube alloy; Inconel 718 and Inconel X-750 are the named real band alloys,
using a controlled post-braze furnace cooldown to develop mechanical properties. A real
failure-mode catalog (Fig. 15) attributes most tube damage under bands to high-low tube
alignment (excess braze gap or forced crown depression), inconsistent band-to-tube contact
angle, concentrated external loads, or fabrication-induced (weld-shrinkage) interference -
fixed in practice with shim stock rather than forcing the fit. Tube splice joints (where one
tube becomes two downstream to match increasing nozzle circumference) should be avoided where
possible; if required, use a high-ductility tube alloy (347 CRES or nickel) for a higher
taper ratio before splicing is needed, and always put any joggle on the cold-gas side of the
tube, never the hot-gas side (hot-side joggles are a crown-depression/stress-concentration
risk exactly where wall temperature is already highest).

**Real splice-count corroboration — J-2S** `[AEDC-J2S §2.1.1 p.1-3]`: real J-2S hardware
(same engine family as SP-8120's J-2/J-2S band-redesign anecdote above) uses exactly this
splice pattern in practice — fuel flows down **180** tubes then up **360** tubes to the
injector, i.e. every downcomer tube splices into two upcomer tubes at the turnaround (a 1:2
splice ratio) to match the increasing nozzle circumference toward the throat/chamber. A
concrete real-hardware instance of the `[SP-8120]` splice-joint design criteria just above,
on the exact engine SP-8120's own anecdote references.

**Real F-1 tube counts, splice plane, and a real fuel bypass-fraction citation (2026-09-24)**
`[F1-Man §1-15/1-16 p.1-8]` (Rocketdyne's own engine manual, closing an `OPEN_QUESTIONS.md`
acquisition item): a real, exact tube-splice instance for the F-1 — **178 primary tubes**
(1-3/32in OD, Inconel-X) above the 3:1 area-ratio plane, splicing to **356 secondary tubes**
(1in OD) from 3:1 down to 10:1, 2 secondary tubes brazed per primary tube at the splice — a
second real splice-count anchor alongside `[AEDC-J2S]`'s J-2S 180→360 example just above (both
real engines use a 1:2 splice ratio, corroborating the pattern), and sharpens `[SP-8087 Table
III]`'s existing generic F-1 tube-wall citation with real counts/diameters/splice-plane
location. **A real, dimensioned fuel bypass-vs-cooling split**: at each fuel-down tube, an
orificed plug diverts **30%** of the flow straight to the injector manifold while **70%**
continues down for regen cooling, returning via the fuel-up tubes — a genuinely new real
citation for `manifold.py`'s `manifold_bypass_fraction` parameter (used in the F-1-sourced
`"f1_split_reverse_flow"` cooling-flow topology below), which previously had no cited real
fraction behind it.

**Manifold structural supports** `[SP-8120 §2.2.5.2.4/§3.2.5.2.4 p.47-48, 79-80]`: vanes,
splitters, dams, and structural ties inside large thin-wall manifolds fail from differential
thermal stress, vibration fatigue, resonant flutter, or static-pressure loading - and the
monograph stresses that such a failure is as much a *combustion*/performance risk as a
structural one ("often produces a maldistribution of fluid flow and results in performance
loss, combustion instability, or wall overheating"). Toroidal manifold shells "breathe" under
pressure and are more flexible than their supporting structure, so ties must either flex with
the shell while staying locally rigid, or mount on one side only with clearance elsewhere.
**Attachment weld quality ranking, worst to best**: fillet weld ("generally unacceptable") <
full-penetration fillet weld ("usually acceptable") < butt weld ("good... first choice") <
integral casting/parent-metal construction ("excellent... failure free"). Attachment location
itself is called "extremely critical" since fatigue failure there is the most common failure
mode. Real example: an 80%-cross-section dam in the H-1 engine's fuel-return manifold fixed a
nonuniform-inlet-flow problem that had been causing **measured engine performance to change
test-to-test** - a concrete case of a manifold structural/hydraulic fix directly resolving a
performance problem, not just a durability one.

**Real manifold hydraulic/distribution design criteria** `[SP-8087 §2.1.2/§3.1.2 p.19-20,
62-64]` — this is NASA's dedicated fluid-cooled-chamber monograph and the single most
load-bearing new source for manifold design specifically, complementing `[SP-8120]`'s
structural-supports content above with real hydraulic/distribution numbers. **Three manifold
types**: inlet, outlet, turnaround — manifolding is frequently integral with structural
supports/interface flanges (inlet manifold integral with the forward flange in two-pass
systems; turnaround integral with the aft flange when a nozzle extension bolts on). **Real
flow-maldistribution tolerance**: up to **20% flow variation has been tolerated in the first
pass** of a multi-pass system (coldest coolant, widest thermal margin there), but must be
reduced before the final pass — typically via the natural balancing effect of a common
manifold at the turnaround. **Hydrogen systems require analytical (not empirical) flow-
balancing** due to hydrogen's large density variation with temperature; storable-coolant
systems are comparatively easier. **Two competing toroidal inlet-manifold design
philosophies**: (1) variable-area/constant-velocity (tapered torus) — equal velocity to
every passage, smaller/lighter, but harder to fabricate and prone to pressure-drop-driven
maldistribution around the torus; (2) constant-area/variable-velocity — minimizes pressure
loss but produces maldistribution (passages near the inlet see higher velocity than passages
opposite it). **Real practice is a compromise between the two**, using smooth turns/vanes; a
flow splitter at the torus inlet suppresses dynamic-head effects locally. **A real,
propellant-specific turnaround-manifold-topology rule**: common annulus preferred for
storable coolants (evens flow before the critical final pass); discrete per-tube/per-channel
circuits preferred for hydrogen (each channel's resistance must be balanced separately as a
function of *local* coolant properties) — directly relevant to `manifold.py`'s existing
`cooling_flow_topology` options (`"single_pass_countercurrent"` vs. the real-F-1-sourced
`"f1_split_reverse_flow"`), giving a propellant-class rule for which style is appropriate
beyond the two topologies the tool currently models. **A concrete manifold-to-thin-wall
transition criterion**: taper the manifold wall over a short **0.5-1 in transition** between
thin cooled sections and heavy manifolds to avoid bending discontinuities (or use asymmetric
support of the thin section) — complements rather than duplicates `[SP-8120]`'s
vane/splitter/dam *attachment*-quality criteria, since this is the thin-to-thick wall
transition geometry itself. Real interface-flange examples: a welded fuel-turnaround
manifold (fully-penetrating welds to the aft tube ends) and a brazed flange with a *separate*
turbine-exhaust manifold routing hot gas past the fuel turnaround manifold to the same
nozzle-extension attachment — a real two-manifolds-at-one-structural-interface example.

**Real manifold-volute-sizing corroboration for `manifold.py`** `[Fagherazzi-2019 §3.3.2
p.87-88]`: an independent thesis sizes its own coolant supply manifold as a volute (splitting
incoming flow into two symmetric halves feeding the channel bundle) using the **exact same
constant-target-velocity continuity-equation approach `manifold.py` already implements** —
`A(θ) = ṁ(θ)/(ρ·v̄)`, where the cross-section shrinks as flow peels off into channels along
the volute's length — a real, independently-arrived-at second precedent for that design
pattern. Design intent: avoid abrupt velocity changes between the supply volute and the
channels, keep the envelope clear of seal lands/bolt circles. A **circular cross-section is
hydraulically optimal but a rectangular section is often chosen purely for machinability** —
real design practice trading hydraulic optimality for manufacturing simplicity at small
scale. A **simplified constant-cross-section volute** (`A(θ) = const`) is a real, usable
"cheap but good enough" fallback if a non-optimal-but-simple sizing mode is ever wanted. Real
packaging constraint: the coolant inlet had to be moved off-axis to route around o-ring seal
lands, and the outlet needed a 90° flow-diversion elbow to exit radially — concrete evidence
that manifold/fitting geometry is frequently seal/fastener-envelope-driven, not purely
hydraulic, a real-world caveat on `manifold.py`'s per-propellant "hook point" simplification.

**Real six-method throat/chamber structural-support survey** `[SP-8087 §2.1.3.1 p.21-24]`:
(a) cylindrical shell (Aerobee, Improved Titan Stage I); (b) one-piece brazed jacket (J-2,
F-1, H-1) or bolt-on/weld-on corsets (Titan III Stage II/RL10); (c) banded (Atlas
booster/sustainer — the `[SP-8120]` retaining-band case above); (d) U-tube integral shell
(NERVA); (e) double-walled inherent integral shell (Atlas vernier); (f) drilled-passageway
inherent integral shell (Agena). **Real comparative reliability finding**: chambers with
*less rigid* support (banded, cylindrical shell, wirewrap-only) showed *more* tube-to-tube
hot-gas leaks after many tests than chambers with intimate brazed-jacket support (though
entangled with brazing-technique era, not support-rigidity alone, per the source's own
caution). **Real fabrication method** (F-1/J-2/H-1's one-piece brazed jacket): tubes pressed
against the jacket by a pressurized bag during brazing, "costly and difficult" — corroborating
`[SP-8120]`'s own F-1/J-2 fabrication-difficulty anecdotes. **Real fatigue mode**: brazed-
jacket tube crowns fatigue-cracked at the jacket's *aft end* from cyclic structural-resonance
loads and a stress discontinuity there — fixed by adding damping bands to the expansion
nozzle AND tapering the jacket thickness / increasing braze contact over the aft 1-2 in. A
real Titan-sustainer corset (epoxy-filled space between a split shell and the wirewrapped
tube bundle, carrying shear loads) prevented throat buckling from asymmetric jet-separation
side loads up to 1.4× limit load in ground tests.

**Real SSME hardware anchors for structural/mass-model plausibility checks (2026-09-24)**
`[SSME-Orientation]` (Boeing/Rocketdyne training material, June 1998, Block IIA — derived facts
only per this project's convention for licensed reference material, no verbatim reproduction):
real tube/channel/band counts on an SSME-class design, not previously available anywhere in
`claude_lit` — MCC liner **430 milled slots**; nozzle **1,080 brazed tubes + 9 hatbands** — a
direct plausibility anchor for `hatbands.py`/`tube_bundle.py`. Real turbopump architecture
(stage counts, not previously in `topics/09`): LPOTP 6-stage axial hydraulic turbine
(LOX-driven, not gas); LPFTP 2-stage axial gas turbine; HPOTP double-entry back-to-back main
impeller + 3-stage cantilevered turbine; HPFTP 3-stage centrifugal pump + 2-stage turbine. Real
per-pump efficiency/PR table at 104.5% power level: HPOTP pump eff. 71.8/75.8%, HPFTP 75.0%,
turbine PR 1.50-1.53, turbine eff. 74.6-81.1% — runs a few points off `[SP-8107]`'s 1973
pre-operational SSME row (78.1/69.6% pump, PR 1.56-1.59, 72.9-79.0% turbine); worth a note if
`validate.py`'s SSME turbopump spot-check tolerance is ever tightened, since this is later,
real, named-hardware data vs. a pre-operational projection. Real combustion-device geometry:
fuel preburner 264 coaxial elements/10.43in dia (hot-gas MR 0.86); oxidizer preburner 120
elements/7.43in dia (MR 0.60) — corroborates `[SP-8081]`'s existing 0.2-1.0 GG-mixture-ratio
band (`topics/10-gas-generators.md`); main injector 600 coaxial elements + 42 flow shields +
porous rigimesh transpiration-cooled faceplates. **Corroboration**: MCC max hot-gas wall temp
1,000°F at 100% power exactly matches `[Wieseneck-J2]`'s existing 1000°F copper figure
(`topics/06-cooling-and-heat-transfer.md`), now confirmed against real as-flown hardware
rather than a 1970s pre-hardware design point. Caveat: this source has no failure/anomaly-
history content anywhere in its 105 pages (unlike the F-1 turbine-exhaust-detonation
precedent in `topics/07-dump-cooling.md`) — no comparable safety-lesson data point exists
in it.

**Real manifold-velocity design criterion — `[SP-8120]` full read, 2026-09-24** `[SP-8120
§3.2.5.1 p.78]`: *"Keep the fluid velocities in the manifold as low as possible, preferably
**less than 60 fps for liquids and less than Mach 0.25 for gases**."* This is **more
conservative** than `[SP-8087]`'s already-cited limits above (200 ft/s liquid, Mach 0.3
recommended/0.5 max) — two independent NASA design-criteria monographs give different
numbers for what may or may not be exactly the same quantity (general circumferential
distribution-manifold velocity here vs. `[SP-8087]`'s coolant-jacket-passage velocity
specifically) — flagged as a real, unresolved discrepancy rather than silently picking one.
Narrative context: real observed maldistribution (tube starvation, inadequate local film
coolant) has occurred at **liquid velocities of 50-100 fps and gas velocities of Mach
0.25-0.4** — the 60 fps/Mach 0.25 criterion sits at the low end of a real observed
maldistribution-onset band, not an arbitrary round number. Real inlet-configuration fixes:
multiple tangential inlets, multiple low-velocity radial inlets, or turning vanes/deflector
plates for single-inlet designs; taper the manifold cross-section (or bore a torus
off-center for low-volume production) to fix along-manifold pressure variation. Even a
well-tuned tapered/vaned inlet still shows a real residual pressure rise at the manifold's
final stagnation point — fixed by adding flow resistance downstream of the bleedoff ports
there, not further inlet tuning.

**Real hot-gas (turbine-exhaust) manifold structural/thermal-growth precedent — `[SP-8120]`
full read, 2026-09-24** `[SP-8120 §2.2.5.3/§3.2.5.3 p.48-53, 80-82]`: real historical survey
of turbine-exhaust disposal by engine (Atlas booster canted-duct fix for boattail fires;
Atlas sustainer/Saturn-S-1B looped-tube-into-main-jet; F-1's film-cooling use, above; J-2's
"cat-eyes" dump into the main stream, tubes downstream partially film/primarily regen
cooled; Titan's superheater-then-impingement-on-ablative-extension routing). **Real F-1
hot-gas-manifold thermal-growth/failure detail**: tapered hot-gas torus rigidly attached to
the cooled exit ring, **"omega" expansion joints** for thermal growth (potential radial
growth **~0.5 in.**); recurring real failure at the omega-joint/outer-ring intersection
(tension cracks from ring bending) — fixed by doublers distributing load over a longer base.
A separate tube-denting failure from flame-shield/retaining-band interference was fixed by
increasing clearance from **a few thousandths of an inch to ~0.4 in.** Real material rule by
thermal-load severity: elastic/low-thermal-load designs can use relatively brittle materials
(Waspaloy, Rene 41); high-thermal-load hot-gas manifolds (like F-1's) need materials
retaining **≥20% ductility at elevated temperature** — real examples 347 CRES, Hastelloy C,
Inconel 625, L-605. **Design criterion, safety-relevant**: the looped-tube/gap turbine-
exhaust-introduction method must **not** be used with noncryogenic propellants (real Atlas
RP-1-trapping/LOX-RP-1-gel-detonation precedent, detailed in `topics/07-dump-cooling.md`) —
use an annulus-at-exit or film-cooled-extension method instead for storable propellants.

**Real F-1 / J-2 exhaust-manifold SHAPE — photos + the F-1 cutaway (web, 2026-09-25)**:
the F-1 thrust-chamber photo and the F-1 manifold cutaway (the latter the `[SP-8120]`
§2.2.5.3 figure — torus, flame shield, retaining-band "interference area", return manifold,
"rigid intermittent support", omega joint, nozzle extension), both reproduced on
enginehistory.org, *Rocket Propulsion Evolution* §8.12
(`https://www.enginehistory.org/Rockets/RPE08.11/RPE08.12.shtml`: `F-1ThrustChamber.jpg`,
`F-1ExManNozzleExt.jpg`), and a J-2 museum photo (Science Museum Group object 1977-0402,
`https://coimages.sciencemuseumgroup.org.uk/745/48/large_1977_0402_0001.jpg`). Read off them:
**both engines feed the torus TANGENTIALLY at ONE inlet** — the F-1's heat-exchanger duct drops
down the chamber side and turns through a large elbow straight into the torus, which then
narrows one way round (a volute/scroll — `[F1-Man §1-18]`'s "decreasing (from inlet to exit)
cross-sectional area"); the J-2's duct comes down through a bellows and elbow the same way. The
F-1 torus sits outboard and slightly FORWARD of the chamber/extension joint and feeds aft-inboard
through a short neck into the extension's double wall; the flame shield lies on the tubes under
it. Raised omega-joint bands are visible round the F-1 torus. Photos give shape and proportion,
not dimensions — no area-vs-angle law or section sizes (`OPEN_QUESTIONS.md`).

**Real coolant-return-manifold and nozzle-attachment braze/tolerance numbers — `[SP-8120]`
full read, 2026-09-24** `[SP-8120 §2.2.5.4/§2.2.6 p.53-57]`: real tube-to-manifold joint
comparison — square tube ends into slots (corner-filler/braze-peeling/oil-canning problems)
vs. **circular tube ends into round holes with the tube end expanded in place** (the real
F-1 technique, much more successful, stays within tight braze-gap tolerance). Real
dimensioned brazing tolerances with no equivalent elsewhere in this reference set: **maximum
satisfactory braze gap 0.004-0.006 in.**, **braze-joint length ≥1 tube diameter** for
acceptable strength. Real nozzle-attachment finding: attachments braze on **one side only**
of a tube produce *lower* local stress than two-sided brazing (Fig. 48); welding attachments
to age-hardenable structural members must happen **before** the furnace-braze cycle, not
after (post-braze welding destroys the member's braze-induced strength). Real large-chamber
extension-joint numbers: flanges up to **120 in. diameter**, real-hardware
**out-of-roundness up to 1.5% of flange diameter** (compensated by oversized/radial-slotted
bolt holes), bolt spacing = bolt-head diameter + 2× flange thickness, seals tolerating up to
**50% crush/compression** from flange waviness.

**A next-generation chamber-liner material candidate — copper-diamond composites**
`[CuDiamond-Liner §4, Table 4-5, p.9-13]` (filed here rather than in
`topics/12-materials-and-structures.md`, which is already slightly over its lookup-budget
cap — this is a materials entry by subject, just parked in the sibling file for space):
an early-TRL (research-stage) NASA MSFC/GTE material family, copper (or NARloy-Z/GRCop-84)
powder blended with refractory-carbide-coated diamond particles, hot-pressed or spark-
plasma-sintered. Real measured thermal conductivity up to **~540-563 W/m·K** — roughly **1.5×
pure copper's 360 W/m·K** and nearly **double GRCop-84's 300 W/m·K** — at a density **~30%
lower** than NARloy-Z-class alloys. **The real cost that matters for a "just swap the liner
material" framing**: adding diamond costs roughly **half the UTS** (NARloy-Z baseline 45 ksi
→ 18-24 ksi with 30-40 vol% diamond) and **collapses ductility from 33% elongation to
generally <1%** (copper-coated diamond partially recovers to 2-3% at ~23 ksi UTS) — a real
strength/ductility-vs-conductivity tradeoff, not a strict upgrade. Manufacturing is powder
metallurgy only (diamond's hardness rules out conventional machining — EDM/waterjet only);
the most advanced hardware built is a sub-scale (2.5-2.75in dia) diffusion-bonded ring-stack
liner — **no full-scale chamber has been built or hot-fire tested**, and no low-cycle-fatigue
data exists for any Cu-D variant (contrast `[Miller-CuFatigue]`'s real OFHC-copper LCF method
already cited in `topics/12`). Treat any Cu-D property number as a coupon-level research
result, one tier below even GRCop-84's own citations, which back a flying/tested alloy.

## Caveats

- `[SP-8120]` is a **criteria/practices monograph, not a sizing-equation source** — it gives
  design rules ("shape and size the retaining bands for start-transient, overexpansion, and
  gimbal loads") and real-hardware precedent, but no closed-form band-thickness, weld-
  allowable-stress, or splice-geometry equations. The F-1's measured 2.2–2.8 axial / 2.45
  bending stress-concentration factors are real but specific to F-1's own rectangular-band
  geometry, not a general design allowable. 1976 vintage — predates SSME/RS-25, so its
  real-hardware retaining-band/manifold examples are 1960s Saturn/Apollo/ICBM-generation
  (F-1, J-2/J-2S, H-1, Titan, Atlas), though the failure physics itself (weld fatigue,
  thermal-cycling band buckling, tube-to-band stress concentration, turbine-exhaust thermal
  growth, manifold maldistribution) is geometry/loading-driven, not material-era-dependent.
  **Now fully read as of 2026-09-24** (previously only the retaining-bands and vanes/
  splitters/dams sections were deep-read) — the newly-read manifold-velocity criterion
  (60 fps/Mach 0.25) is still just a stated threshold, not derived, and conflicts with
  `[SP-8087]`'s own 200 ft/s/Mach 0.3-0.5 criterion without either source reconciling the
  difference (flagged above, not resolved). Full extraction scope/section map: `sources/
  sp8120-liquid-rocket-nozzles.md`.
- `[SP-8087]` DOES give several genuinely new dimensioned numbers `[SP-8120]` lacks here
  (manifold maldistribution tolerance, manifold transition-taper length — plus heat-flux
  construction-selection thresholds and tube-taper limits, covered in `topics/06b-cooling-
  methods-and-chemistry.md`) — but is still 1972-vintage and explicitly pre-advanced-
  channel-wall (its own introduction says high-heat-flux non-tubular fabrication was "in
  development" and "not covered in detail"). OCR quality is mixed: cleanly-typeset criteria
  text reads well, but several table pages are pure scanned-image/graphics with garbled or
  absent text.
- `[Fagherazzi-2019]`'s manifold/volute content is from a single small-engine (250-400 N)
  master's thesis, one tier below a NASA design-criteria monograph — its correlation
  *choices* and design *process* (volute-sizing method, construction-type comparison) are
  well-sourced and reusable, but its own novel numerical results are a single-team data
  point, not an industry survey.
- The four manufacturer datasheets and `[GRCop84-Tensile]`/`[Miller-CuFatigue]`/
  `[Quentmeyer-CR185257]` cited in `topics/12-materials-and-structures.md` are single-test-
  article or single-lot sources — not repeated here since none of their content lives in
  this file.
- `[SSME-Orientation]` is Boeing-proprietary/training-only material (June 1998) — treated per
  this project's `upstream/ROEngines`-style licensing convention (derived facts only, no
  verbatim slide-text reproduction). Terminology flag: it calls the 109% power point "FPL"
  where `[SP-8107]` calls the same physical condition "EPL" — same condition, inconsistent
  naming 25 years apart across two Rocketdyne-lineage sources, unresolved.

## Implications for engine_designer

- **`mass_model.py` `jacket_structure_mass_kg()` / `WALL_CONSTRUCTIONS`**: today this is a
  single flat `mass_factor` add for `tube_wall`/`coax_shell` vs. a zero-add `milled_channel`
  reference (per CLAUDE.md's Layout section) — it has no explicit retaining-band, splice-
  joint, or manifold-structural-support model at all (confirmed: no `retaining_band`/
  `band_spacing`/`splice` sizing logic exists in `mass_model.py`/`design.py`/`cooling.py`
  today, only the terms "tube_wall"/"tube bundle" as a wall-construction *choice*). `[SP-8120]`
  is real design guidance for exactly this gap — a future feature could size a *notional*
  band count/spacing from the "shape bands for start-transient/overexpansion/gimbal loads"
  criterion and add a stress-concentration advisory (warn-don't-block, per CLAUDE.md
  convention #2) modeled on the real F-1 2.2–2.8x factor when `wall_construction ==
  [UPDATE 2026-09-23: now implemented as `physics/hatbands.py` - band spacing marched from a
  first-principles fixed-fixed tube-span bending model (SP-8120 p.29's "unsupported tube
  length" rule), band section sized for hoop tension + thin-ring buckling, flat/tee/hat/
  channel/box sections per Fig. 40, auto flat->stiff escalation; all magnitudes Tier 3 - see
  ASSUMPTIONS.md.] Original note:   "tube_wall"` — but `[SP-8120]` gives no formula to size band thickness/spacing from first
  principles, so any such feature would need its own reverse-solved or first-principles
  derivation, not a value lifted from this source. Report-only here; no code changed.
- **`manifold.py`'s existing `cooling_flow_topology`/`size_jacket_manifolds`/volute-sizing
  approach is now doubly corroborated**: `[SP-8087]` gives a real propellant-class rule
  (storable → common annulus, hydrogen → discrete per-channel circuits) for turnaround-
  manifold topology beyond the tool's current two named topologies, and `[Fagherazzi-2019]`
  independently arrives at the exact same constant-target-velocity `A(θ)=ṁ(θ)/(ρ·v̄)`
  volute-sizing continuity equation the tool already uses. Both are report-only findings
  (no code changed) but meaningfully de-risk the existing design pattern — two independent
  real/near-real sources converge on it rather than it being a one-off choice.
- **`manifold.py`'s target-velocity constant now has two conflicting real-source candidates**
  (`[SP-8120]` full read, 2026-09-24): 60 fps liquid/Mach 0.25 gas (general distribution
  manifold) vs. `[SP-8087]`'s existing 200 ft/s liquid/Mach 0.3-0.5 gas (coolant-jacket-
  passage specifically). Neither source reconciles the difference — a real open question if
  `manifold.py`'s velocity target is ever tightened against a literature source rather than
  its current first-principles constant-velocity approach, which sidesteps the question by
  not needing an absolute target at all. Report-only.
- **Real hot-gas (turbine-exhaust) manifold structural precedent now exists** (`[SP-8120]`,
  above) if `mass_model.py`/a future feature ever sizes turbine-exhaust-manifold structure —
  real omega-joint thermal-growth numbers, a real material-ductility rule (≥20% elongation
  for high-thermal-load hot-gas manifolds), and a real safety-relevant design criterion
  (never use looped-tube turbine-exhaust introduction with storable propellants). See
  `topics/07-dump-cooling.md` for the accompanying F-1 turbine-exhaust film-cooling-extension
  content this pairs with. Report-only — no code changed. **Applied 2026-09-25**: the
  nozzle_injection manifold is now a tangentially-fed scroll (`manifold.RING_KIND_SCROLL`,
  full-flow inlet — the corpus F-1's lands on the real 24 in), on an outlet neck + flame shield
  read off the cutaway (Tier 3), with the F-1's 15 omega joints drawn (`ASSUMPTIONS.md`
  "Injection SCROLL manifold"); the ductile-material rule is already met (Haynes 230).
- **A currently-unflagged real design tension worth surfacing**: `[SP-8120]`'s explicit
  criterion that manifold/band structural failures are as much a *combustion-instability/
  performance* risk as a structural one (the H-1 dam anecdote: a purely hydraulic/structural
  fix eliminated a measured performance variation) has no counterpart anywhere in the tool's
  `combustion_stability.py`/`injectors.py` advisories — those model acoustic modes and
  injector-pattern stability, not manifold-flow-maldistribution-driven instability. Not
  actionable without a manifold flow model the tool doesn't have; noted for awareness only.
- **`hatbands.py`/`tube_bundle.py` now have a real SSME-class plausibility anchor**:
  `[SSME-Orientation]`'s real 430-milled-slot MCC / 1,080-tube-9-hatband nozzle counts (above)
  are a citable real-hardware data point at a scale between the tool's existing F-1/J-2
  anchors and a modern high-Pc engine. Report-only — no code changed.
- **`manifold.py`'s `manifold_bypass_fraction` (`f1_split_reverse_flow` topology) now has a
  real citation**: `[F1-Man]`'s real 30%/70% fuel bypass-vs-cooling split (above) is the exact
  parameter this real-F-1-sourced topology already models — previously an uncited Tier-3
  value, now backed by Rocketdyne's own engine manual. `ASSUMPTIONS.md`'s `manifold_bypass_
  fraction` entry already carries the correct 30% number (from an informal web source,
  heroicrelics.org) — this is a citation-QUALITY upgrade (informal web source → primary
  Rocketdyne manual), not a new number, and hasn't been applied to `ASSUMPTIONS.md` yet.
- **`OPEN_QUESTIONS.md` item (b) (Rocketdyne F-1 Familiarization Training Manual) is now
  RESOLVED (2026-09-24)** — acquired and distilled (`[F1-Man]`, above). See `topics/07-dump-
  cooling.md`/`topics/09-turbopumps.md`/`topics/10-gas-generators.md` for the rest of what it
  contributed. Report-only — no code changed.
