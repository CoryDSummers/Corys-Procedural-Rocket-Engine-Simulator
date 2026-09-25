# NASA CR-185257 — Rocket Combustion Chamber Life-Enhancing Design Concepts

## Identity

R.J. Quentmeyer (Sverdrup Technology, Inc., Lewis Research Center Group, Brook Park,
Ohio), *Rocket Combustion Chamber Life-Enhancing Design Concepts*, NASA Contractor Report
185257 / AIAA-90-2116, prepared for NASA Lewis Research Center under Contract NAS3-25266,
July 1990. `literature/NASA CR-185257 - Rocket Combustion Chamber Life-Enhancing Design
Concepts.pdf` (NTRS accession 19900015867; 19 PDF leaves: leaf 0 title page, leaves 1-9 =
printed pages 1-9 body text incl. references start, leaves 10-11 = printed pages 10-11
references cont., leaves 12-17 = Figures 1-17 (scanned/rasterized, mostly captions-only
extractable), leaf 18 = Report Documentation Page). Tag: `[Quentmeyer-CR185257]`.

## Character

A short (11-page-of-text) AIAA-conference-paper-format survey/overview, not a data report:
it summarizes SEVEN distinct "life-enhancing" combustion-chamber-liner design concepts
being pursued across several concurrent NASA/Air Force Advanced Launch System (ALS) and
SSME-life-improvement programs, citing subscale-rocket-test results where available (most
of that underlying test data lives in the paper's own references, not reproduced here in
full — this paper gives headline numbers, not curves/tables). Author Quentmeyer is also a
named co-author on several of the report's own cited underlying studies (refs. 6-8, 20-21),
so this reads as an author's own round-up of his group's work circa 1990, aimed at framing
design tradeoffs for a low-cost, long-life ALS booster engine. Companion in character to the concurrently-authored `claude_lit/sources/miller-ofhc-copper-
cyclic-fatigue.md` source (being written in parallel in this batch, not read for this note) —
both concern combustion-chamber-liner thermal-cycling life, but this paper is a DESIGN-
CONCEPT survey (what geometry/material/coating changes extend life, with a few subscale
hot-fire cycle counts) rather than a materials-fatigue-curve source; no attempt was made to
cross-check numbers between the two, per task instructions.

Structure: Abstract, Introduction (SSME "thermal ratcheting" failure mechanism), Subscale
Rocket Engine Test Apparatus, Life-Enhancing Design Concepts (7 subsections: Thermal
Barrier Coatings, Tungsten-Reinforced Chamber Liner, Hot-Gas-Side Slots, Tubular-Bundle,
High-Aspect-Ratio Cooling Passages, Transpiration-Cooled Throat, Low-Stiffness Closeout),
Hydrocarbon-Fuels/Combustion-Chamber-Liner Materials Compatibility, Low-Cost Fabrication
Techniques (2 subsections: Vacuum-Plasma-Sprayed Liner, Platelet-Formed Chamber Liner),
Comparison of Concepts, Conclusions, References (31 citations, mostly other NASA
CR/TM/AIAA-paper leads — none independently chased for this note). Read in full; text
extraction via pymupdf was clean (unlike the OCR-noisy `[Lewis-Deposits]` scan) — this is a
typeset, not scanned, source, so quantitative claims below are direct transcriptions, not
OCR-disambiguated.

## Key results

**Failure mechanism — "thermal ratcheting"** `[Quentmeyer-CR185257 p.1]`: SSME main
combustion chamber (MCC) life falls well short of design life because cyclic thermal
strain progressively deforms and THINS the wall between the cooling passages and the
hot-gas side on each firing cycle (the wall bulges/creeps toward the hot-gas side under the
repeated thermal-gradient-induced plastic strain), eventually cracking. This ratcheting
term/mechanism description is a citable, precise framing of *why* liner fatigue life is
finite beyond a generic "thermal cycling" statement.

**Subscale test apparatus parameters** `[Quentmeyer-CR185257 p.2]`: LeRC's low-cost subscale
rocket rig (LOX/GH2, uncontoured cylindrical chamber, water-cooled centerbody forming the
throat) ran a **throat heat flux of ~97.1 MW/m² (33 Btu/in²·sec) at Pc = 4.14 MPa
(600 psia)**, with plans (as of 1990) to raise it to **250 MW/m² (85 Btu/in²·sec) at
Pc = 13.8 MPa (2000 psia)**. Thermal-cycling capability: the chamber (separately LH2-cooled)
can cycle from **28 K to a throat wall temperature of 800 K and back to LH2 temperature in
3.5 sec** — i.e. this rig is purpose-built for rapid low-cycle-fatigue screening, not steady
long-duration firing. Useful as a real reference heat-flux/Pc anchor point distinct from the
`engine_designer` full-scale-engine spot checks already in `physics/validate.py`.

**Thermal Barrier Coating (TBC) — quantified cycle-life result, the headline finding**
`[Quentmeyer-CR185257 §Thermal Barrier Coatings p.3]`: a **ZrO2** thermal-barrier coating,
applied as a 0.076 mm (0.003 in) layer with a 0.025 mm (0.001 in) NiCr bond coat, over an
electrodeposited-copper (ED Cu) liner (fabricated "inside out": TBC plasma-sprayed onto a
mandrel, bond coat applied, liner electroformed around it), showed **NO damage after 1450
thermal cycles** in the LeRC subscale rig. An UNCOATED liner of the same cooling-passage
geometry tested at the same conditions, but made of **Amzirc (Cu-0.15%Zr)**, **cracked after
393 thermal cycles** with visible deformation/thinning. Physically: at a coating surface
temperature of 1944 K (3500°R) the TBC reduces heat flux into the wall by **~50%**, plus
acts as an insulating temperature-drop layer, lowering the underlying metal wall temperature
and hence its plastic strain and raising its effective strength. **Caveat on this
comparison**: the two test articles differ in BOTH liner base material (Amzirc vs. ED Cu)
AND presence of the TBC/bond-coat/electroform fabrication — this is not a clean coated-vs-
uncoated same-substrate A/B pair, so the ~3.7x cycle-count improvement (393 → 1450+) should
be read as "TBC + this fabrication route gave a large, real, quantified life improvement in
matched-geometry subscale testing," not as an isolated coating-only effect size.

**Tungsten-reinforced chamber liner — quantified strength/conductivity tradeoff**
`[Quentmeyer-CR185257 §Tungsten-Reinforced Chamber Liner p.4]`: a copper-alloy liner with
0.020 cm (0.008 in) diameter tungsten wire, spaced at one wire diameter, embedded (via
arc-spray + HIP densification) within a 0.089 cm (0.035 in) thick copper wall gave:
(a) composite thermal conductivity only **~10% lower** than OFHC copper's, and
(b) **rupture strength ~80% higher than NARloy-Z (Cu-3.5%Ag-0.5%Zr) at 867 K (1560°R)** —
a real, quantified elevated-temperature strength comparison against the SSME's own
hot-wall liner alloy. Subscale hot-fire testing showed **no deformation or thinning of the
wall after 400 thermal cycles** (same throat-plane cross-section examined as the TBC study).
This is a DIFFERENT property (creep/rupture strength at 867 K, not room-temperature yield/
UTS) and a different composite (tungsten-wire-reinforced copper, not a monolithic alloy)
than `[MatCh2 Table 2.6.3]`'s NARloy-Z row (CTE 17.2, k 295.0, yield 192.0 MPa, UTS 314.0 MPa,
elongation 31.0% — presumably room-temperature figures) already in
`topics/12-materials-and-structures.md` — it should be treated as a separate, elevated-
temperature strength data point for NARloy-Z (implicitly: NARloy-Z's own 867 K rupture
strength = the tungsten-composite's rupture strength ÷ 1.80, though the paper does not state
NARloy-Z's absolute 867 K rupture-strength number, only the ratio), not a value to average
or reconcile against the room-temp MatCh2 table.

**Hot-gas-side slots** `[Quentmeyer-CR185257 §Hot-Gas-Side Slots p.4]`: a strain-relief
concept — EDM-cut slots (0.013 cm / 0.005 in wide, using a 0.010 cm / 0.004 in wire) through
each cooling-passage rib at each end of the chamber, to let the hot-gas-side wall expand
locally without inducing wall-thinning strain. Explicitly **not yet hot-fire tested** as of
this paper (1990) — a design proposal, not a validated result; flagged here only as a
concept, no life number available.

**High-aspect-ratio cooling passages — quantified wall-temperature reduction**
`[Quentmeyer-CR185257 §High-Aspect-Ratio Cooling Passages p.5]`: an analysis on the LeRC
subscale chamber found that increasing channel count from **72 (baseline) to 400** channels
at the throat, at the SAME coolant flow rate, reduced the **throat hot-gas-side wall
temperature from 777 K (1400°R) to 444 K (800°R)** — i.e. roughly a 43% reduction in
absolute wall temperature (or ~1.75x margin in temperature-above-coolant terms) purely from
increasing the "fin effect" via more/narrower channels. The demonstrated 400-channel throat
region used channels and ribs ~0.025 cm (0.01 in) wide with **aspect ratio (height/width)
~6**, at a 0.089 cm (0.035 in) wall thickness (kept equal to the baseline for a controlled
comparison; the paper notes the wall "could be much thinner" for further gains). Secondary
benefits noted: more heat pickup available for turbine drive (favors expander-cycle
pairing, see below) and coolant pressure drop can be traded down (lower coolant Mach number)
for only a minor wall-temperature penalty.

**Platelet-formed liner — highest cited aspect ratio** `[Quentmeyer-CR185257 §Platelet-
Formed Chamber Liner p.8]`: diffusion-bonded, chemically-etched flat platelet stacks
(formed into contoured segments, then welded) have achieved cooling-passage **aspect ratios
as high as 15** (vs. 6 in the machined high-aspect-ratio example above) per ref. 31, at
lower fabrication cost/risk than machining for very thin, accurate hot-gas-side walls.

**Transpiration-cooled throat** `[Quentmeyer-CR185257 §Transpiration-Cooled Throat p.5-6]`:
framed as one of the two BEST life-enhancing concepts (with TBC) because it can "virtually
eliminate" plastic strain in the throat — but historically not widely adopted due to
performance loss (coolant dumped into the hot-gas stream, unavailable for turbine drive) and
porous-media fabrication difficulty/clogging risk (esp. hydrocarbon carbon-deposit clogging,
directly echoing `[Lewis-Deposits]`'s coking findings already in `topics/06`). Platelet
fabrication is proposed as the enabler (accurately metered coolant flow through etched
platelets minimizes the performance loss). No subscale life-cycle number given for this
concept specifically (unlike TBC/tungsten-reinforced above).

**Low-stiffness closeout — quantified (analytical) life-enhancement factor**
`[Quentmeyer-CR185257 §Low-Stiffness Closeout p.6]`: replacing the conventional stiff
electroformed-nickel closeout between liner and structural jacket with compliant
intermediate layers (a sintered aluminum-alloy layer backed by a PTFE insulating layer, per
ref. 26) gave a **structural-analysis-predicted life-enhancement factor of 3x** vs. an
identical chamber with the conventional nickel closeout. An earlier fiberglass-overwrap
variant (ref. 25) showed some real life improvement in test but suffered hydrogen leaks from
copper-closeout ruptures, attributed to the fiberglass wrap being too compliant/low-
stiffness to adequately contain the liner. Note the 3x figure is ANALYTICAL (structural
model prediction), not a demonstrated hot-fire cycle count like the TBC/tungsten results
above.

**Hydrocarbon-fuel/copper compatibility — sulfur corrosion, NOT carbon coking**
`[Quentmeyer-CR185257 §Hydrocarbon-Fuels/Combustion-Chamber-Liner Materials Compatibility
p.7-8]`: trace **sulfur** (specifically mercaptan sulfur) in hydrocarbon fuel, not the base
fuel itself, was found to be what attacks copper cooling-passage walls — RP-1 contaminated
with **50 ppm mercaptan sulfur** produced copper-sulfide corrosion forming a rough,
flow-restricting, heat-transfer-degrading deposit on the channel wall (Fig. 15). **No
reaction was observed below 1 ppm sulfur content** in the fuel. A **gold coating** on the
cooling-channel wall was found to prevent the sulfur-copper reaction even with contaminated
fuel, at the cost of increased fabrication cost. **Practical conclusion stated directly**:
hydrocarbon-fuel cooling of copper-alloy liners requires the fuel to be "virtually
sulfur-free," or the passages need a protective coating (e.g. gold). **Important
distinction for `engine_designer`/`claude_lit` cross-referencing**: this is a DIFFERENT
degradation mechanism (chemical sulfur-copper corrosion, not carbon-precursor thermal
coking) from `[Lewis-Deposits]`'s carbon-deposit coking-temperature-band findings already in
`topics/06b-cooling-methods-and-chemistry.md` — both concern hydrocarbon-fuel/copper
compatibility, but the two failure modes, mitigations (sulfur spec / gold coating here, vs.
nickel plating + staying under a coking wall-temperature band there), and even the metal
under attack in each case, must not be conflated when folding into the topic file.

**Cycle-choice pairing recommendation — coolant heat pickup vs. cycle type**
`[Quentmeyer-CR185257 §Comparison of Concepts / Conclusions p.8-9]`: a real, explicitly
stated design-tradeoff link between cooling-liner-concept choice and ENGINE CYCLE choice:
TBC and transpiration-cooled-throat concepts MINIMIZE coolant heat pickup (the TBC insulates
the hot-gas side rather than passing heat to coolant; transpiration coolant is dumped
overboard into the exhaust, not routed to a turbine) and are explicitly said to be **"best
suited for the gas generator cycle"**; conversely, tubular-bundle and high-aspect-ratio
concepts MAXIMIZE coolant heat pickup (more hot-gas-side surface area / better fin effect)
and are explicitly said to be **"ideal for the expander cycle"** (more energy available to
drive the turbine). This is directly relevant to `engine_designer`'s cycle-selection
guidance (`physics/staged_combustion.py`/`expander.py`) as a real literature-stated pairing
rationale, distinct from (but complementary to) the existing hydrogen-embrittlement
cycle-choice precedent already noted in `topics/12-materials-and-structures.md`.

**Low-cost fabrication routes (VPS, platelet) — no life numbers, cost/risk claims only**
`[Quentmeyer-CR185257 §Low-Cost Fabrication Techniques p.8]`: two Vacuum-Plasma-Sprayed
(VPS) liner fabrication sequences (NARloy-Z sprayed liner-first/inside-out, or jacket-first/
outside-in with an integrally cast manifold) are described as cost-reduction routes for the
SSME MCC, explicitly noted to NOT by themselves reduce thermal strain vs. the current MCC
design (i.e. a fabrication-cost lever, not a life lever, unless combined with one of the
strain-reducing concepts above).

## Design method

Not a sizing/correlation source — no closed-form life-prediction equation, S-N curve, or
Coffin-Manson-type fatigue model is given (that underlying analysis lives in the paper's own
references, e.g. refs. 1-12 on SSME MCC life prediction, not reproduced here). The usable
outputs for `engine_designer` are: (1) real, quantified subscale hot-fire cycle-count
results for two specific life-enhancing concepts — TBC (393 → 1450+ cycles, differing
substrate) and tungsten-reinforced liner (400 cycles, no damage, no stated baseline
comparison point within this same test) — as qualitative/order-of-magnitude corroboration
that coating and composite-reinforcement approaches can multiply thermal-cycle life several-
fold, not as a fitted life-vs-strain curve; (2) a real elevated-temperature (867 K) rupture-
strength ratio between a tungsten-copper composite and NARloy-Z, usable only as a ratio, not
an absolute NARloy-Z rupture-strength value; (3) a quantified wall-temperature reduction from
channel-count/aspect-ratio scaling (72→400 channels, 777K→444K) as a real design-lever
magnitude for `physics/geometry.chamber_geometry`/cooling-channel sizing discussions,
though the underlying analysis method (presumably a 1-D fin/Bartz-type conduction model) is
not itself given; (4) a sulfur-content compatibility threshold (<1 ppm safe, 50 ppm caused
real observed corrosion) for hydrocarbon-fuel/copper-liner material-compatibility warnings,
distinct from the existing coking-temperature-band material advisory already in `topics/06`;
(5) a real, citable cooling-concept/engine-cycle pairing rationale (GG cycle ↔ TBC/
transpiration; expander cycle ↔ tubular-bundle/high-aspect-ratio) for cycle-selection
guidance text.

## Section map

- Abstract / Introduction (thermal-ratcheting failure mechanism, ALS program context): p.1
  — read.
- Subscale Rocket Engine Test Apparatus (heat flux/Pc/thermal-cycle-rate parameters): p.2 —
  read.
- Life-Enhancing Design Concepts intro: p.2 — read.
- Thermal Barrier Coatings (TBC ZrO2/NiCr, 393 vs. 1450 cycle result): p.3 — read, most
  citable single result in the paper.
- Tungsten-Reinforced Chamber Liner (wire geometry, conductivity/rupture-strength ratios,
  400-cycle result): p.4 — read.
- Hot-Gas-Side Slots (EDM slot geometry, not yet tested): p.4 — read.
- Tubular-Bundle (electroforming fabrication advantages, no quantified life number): p.4-5 —
  read.
- High-Aspect-Ratio Cooling Passages (72→400 channel wall-temperature result): p.5 — read.
- Transpiration-Cooled Throat (platelet-enabled, no quantified life number): p.5-6 — read.
- Low-Stiffness Closeout (fiberglass-overwrap history, sintered-Al+PTFE 3x analytical
  factor): p.6 — read.
- Hydrocarbon-Fuels/Combustion-Chamber-Liner Materials Compatibility (sulfur/copper
  corrosion, 1 ppm / 50 ppm thresholds, gold coating): p.7-8 — read.
- Low-Cost Fabrication Techniques — Vacuum-Plasma-Sprayed Liner, Platelet-Formed Chamber
  Liner (aspect ratio 15): p.8 — read.
- Comparison of Concepts (GG-cycle vs. expander-cycle pairing rationale): p.8-9 — read.
- Conclusions (restates the cycle-pairing and materials-compatibility conclusions): p.9 —
  read.
- References (31 citations — mostly other NASA CR/TM/AIAA-paper leads on SSME MCC life
  prediction, thrust-chamber fatigue, hydrocarbon-fuel/copper compatibility (refs. 13-15,
  27-30, several by the same "Rosenberg & Gage" pair — potential future-source leads, not
  chased here), and specific concept studies (ref. 22 tungsten-reinforced liner NASA TM-4214,
  ref. 23-24 tubular-bundle AIAA-90-2726/2727, ref. 31 platelet liner AIAA-90-2117 — several
  "to be published July 1990" companion AIAA papers from the SAME conference session as this
  one, likely all in the same `literature/` acquisition batch or a good future-target list)):
  p.9-11 — read (titles only, not chased).
- Figures 1-17 (crack photomicrograph, test apparatus schematic, TBC/tungsten-liner
  cross-sections, hot-gas-side-slot/tubular-bundle/high-aspect-ratio/transpiration/
  low-stiffness-closeout/VPS/platelet schematics, sulfur-corrosion photomicrograph): leaves
  12-17 — captions extracted as text (used above, e.g. Fig. 1's "thermal ratcheting" caption,
  Fig. 15's sulfur-corrosion identification); the schematic/photomicrograph IMAGE content
  itself not independently re-rendered/viewed, only the machine-readable caption text.
- Report Documentation Page: leaf 18 — read (confirms NASA CR-185257/AIAA-90-2116/NAS3-25266
  metadata used in Identity above).

## Caveats

- **Survey/overview paper, not a primary data report** — most of the seven concepts'
  underlying test/analysis data lives in the paper's own references (several marked "to be
  published" as of this July 1990 conference paper, i.e. companion AIAA-90-21xx papers from
  the same session), not reproduced here beyond the headline numbers this paper itself
  states. Treat every cycle-count/temperature/ratio number above as this paper's own summary
  figure, not independently re-derived or spot-checked against the underlying report.
- **TBC cycle-life comparison (393 vs. 1450 cycles) is NOT a controlled single-variable
  test** — it compares an uncoated Amzirc liner against a DIFFERENT base material (ED
  copper) WITH TBC+bond-coat+electroforming simultaneously; the large improvement is real
  and stated as same-geometry/same-conditions, but multiple design variables changed at
  once, not isolated coating-only effect.
- **Tungsten-reinforced liner's "no damage after 400 cycles" has no stated same-test
  baseline** — the paper does not report how many cycles an otherwise-identical
  non-reinforced liner would survive in the SAME test series; any comparison to the TBC
  study's 393-cycle Amzirc failure (different test, different liner design) would be this
  note's own inference, not the source's stated claim — not asserted as such above.
- **867 K tungsten-composite/NARloy-Z rupture-strength comparison is a RATIO only** — no
  absolute NARloy-Z rupture strength at 867 K is given in this source, and this is a
  different property (elevated-temperature rupture/creep strength) than `[MatCh2 Table
  2.6.3]`'s NARloy-Z row (which is presumably room-temperature yield/UTS) — do not average
  or directly reconcile the two without an explicit temperature/property match.
- **Low-stiffness-closeout 3x life factor is analytical (structural-model prediction),
  not a demonstrated hot-fire test result**, unlike the TBC/tungsten-reinforced cycle counts.
- **Hot-gas-side slots and transpiration-cooled throat carry NO quantified life numbers** in
  this source — framed qualitatively as promising/untested (slots) or historically
  under-adopted despite theoretical promise (transpiration), respectively.
- **Sulfur-corrosion findings are a DISTINCT failure mechanism from `[Lewis-Deposits]`'s
  carbon-coking findings** already in `topics/06b-cooling-methods-and-chemistry.md` — do not
  merge the 1 ppm/50 ppm sulfur thresholds here with `[Lewis-Deposits]`'s 600-800 K carbon-
  deposition temperature band; they address different chemistry (sulfur-copper corrosion vs.
  hydrocarbon thermal-decomposition coking) with different mitigations (fuel sulfur spec /
  gold coating vs. nickel plating / staying under a wall-temperature ceiling).
- **1990-vintage, SSME/ALS-booster-era context** — all subscale testing used LOX/GH2 in an
  uncontoured cylindrical rig; none of the reported cycle-count results were obtained on a
  hydrocarbon-fueled or fully-contoured production-geometry chamber, so treat the specific
  cycle numbers as rig-specific magnitude anchors, not directly transferable life
  predictions for a different propellant/geometry/duty-cycle combination.
- **No independent numeric cross-check possible against a real `Engine_Configs/` engine** —
  unlike `engine_designer`'s usual convention #1 spot-check practice, this source's cycle-
  life numbers are subscale-rig results with no direct real-engine Isp/thrust/Pc analog to
  reverse-solve against; they are cited as qualitative/magnitude design-lever evidence, not
  as inputs to a physics correlation.
