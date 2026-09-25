# NASA/TM—2005-213566 — GRCop-84: A High-Temperature Copper Alloy for High-Heat-Flux Applications

## Identity

David L. Ellis (NASA Glenn Research Center, Cleveland OH), *GRCop-84: A High-Temperature
Copper Alloy for High-Heat-Flux Applications*, NASA/TM—2005-213566, February 2005, WBS
22-794-20-77, report number E-15011. `literature/NASA TM-2005-213566 - GRCop-84
High-Temperature Copper Alloy for High-Heat-Flux Applications.pdf` (NTRS accession
20050123582; 30 PDF leaves: leaf 0 cover, leaves 1-3 front matter/availability notice, leaves
4-24 = printed pages 1-21 body text, leaf 25 = printed p.22 Bibliography, leaves 26-27 = a
second numbered-reference list + the Report Documentation Page/abstract, leaves 28-29 blank).
Tag: `[GRCop84-TM2005]`.

## Character

A short (21-page body) narrative review/executive-summary paper written by the alloy's own
developer, synthesizing roughly 15 years of GRCop-84 (Cu-Cr-Nb) development work spread across
~19 earlier internal NASA reports and conference papers (see Bibliography) rather than
presenting new primary test data of its own. It is almost entirely QUALITATIVE and
FIGURE-based — 23 figures plotting GRCop-84 against NARloy-Z (the SSME main combustion chamber
liner baseline alloy), GlidCop AL-15/AL-35, Cu-Cr-Zr (C18150), Zr-Cu (C15000), Cr-Cu (C18200),
AMZIRC, and pure copper across thermal expansion, thermal conductivity, electrical resistivity,
tensile strength (room temperature to ~1000 °C, as-extruded/as-HIPed/aged/post-braze
conditions), creep (Larson-Miller parameter), low-cycle fatigue, oxidation/blanching
resistance, joining methods, and two sub-scale hot-fire liner test campaigns — plus two small
numeric tables (friction-stir-weld and metal-spun-liner tensile data). Structure: Executive
Summary, Introduction, Production, Microstructure, Thermal Expansion, Thermal Conductivity,
Tensile Strength, Creep Rates and Lives, Low-Cycle Fatigue Lives, Oxidation Resistance and
Coatings, Joining, Component Testing, Summary, Contact Information, References (19 entries),
Bibliography (19 entries), Report Documentation Page. Read in full — short enough that no
extraction-scope tradeoff was needed; all body-text pages extracted cleanly with pymupdf
`get_text()` (no OCR/garbling issues — this is a clean digital-native PDF, unlike the
1980s-vintage scanned CRs elsewhere in this batch).

**This is the likely originating narrative source for the numeric Cu-alloy comparison table
already cited secondhand in `topics/12-materials-and-structures.md` from `[MatCh2 Table
2.6.3]`** (GRCop-84 CTE 15.3×10⁻⁶/K, thermal conductivity 285.4 W/m·K, yield 196.2 MPa, UTS
368.0 MPa, elongation 21.7%, listed there as "annealed"). Critically, **this TM itself does not
state any of those five numbers as single tabulated values** — it gives ranges, percentage
deltas relative to NARloy-Z/pure copper, and un-digitized plot figures instead (see Caveats and
the cross-check subsection below). So this source corroborates the *comparative story* MatCh2's
table tells (GRCop-84 beats NARloy-Z in creep/LCF/strength stability, has lower CTE and
somewhat lower thermal conductivity than pure Cu) reasonably well, but cannot independently
verify MatCh2's exact decimal figures — those most likely trace to one of this paper's own
underlying data reports (Ellis & Keller, *Thermophysical Properties of GRCop-84*, NASA/CR-2000-
210055, Ref. 12 in the Bibliography) or to the companion tensile-properties report in this same
literature batch, NASA/TM-2012-217108 (*Tensile Properties of GRCop-84*, being distilled
separately — not read here, flagged as a likely closer numeric match if that note is available).

## Key results

**Composition — resolves an inconsistency already flagged in `topics/12`** `[GRCop84-TM2005
Executive Summary p.1; Introduction p.1]`: GRCop-84 is explicitly and repeatedly given as
**Cu-8 at.% Cr-4 at.% Nb** — ATOMIC percent, not weight percent (the "84" in the name literally
encodes "8 at.% Cr, 4 at.% Nb"). `topics/12` currently flags that `[MatCh2]`'s own Table 2.6.3
gives GRCop-84's composition as "Cu-6.7Cr-5.9Nb" while its §2.8 HEE table labels the same alloy
"Cu-8Cr-4Nb," calling this "an internal inconsistency... possibly a weight-%-vs-atomic-%
mismatch, not resolved here." **Converting this TM's atomic-% composition to weight percent
(standard atomic weights Cu 63.546, Cr 51.996, Nb 92.906; basis Cu-88/Cr-8/Nb-4 at.%) gives
Cu-6.52Cr-5.83Nb wt.%** — within ~0.2-0.3 percentage points of MatCh2's "Cu-6.7Cr-5.9Nb," i.e.
the same alloy expressed in the two different convention bases, not a real inconsistency. This
is a genuine resolution, not just a corroboration: **MatCh2's Table 2.6.3 entry is a weight-%
conversion of the same Cu-8Cr-4Nb (at.%) alloy this TM defines**, and both of MatCh2's own
composition labels are correct once the units are recognized as different bases.

**Microstructure / strengthening mechanism** `[GRCop84-TM2005 Microstructure p.5]`: GRCop-84's
strength comes from a **~14 vol% dispersion of the intermetallic compound Cr2Nb** (formed at a
2:1 Cr:Nb atomic ratio), stable to at least 800 °C with no significant coarsening even after a
1000 °C/30 min exposure (94% of the alloy's melting point) — grain size (2-7 µm as-extruded,
ASTM 11-15) stays essentially pinned. Quantified strengthening split: **~2/3 Hall-Petch
(grain-refinement), ~1/3 Orowan (dispersion) strengthening** `[ref. 7, Anderson et al. 1995]`.
This directly explains why GRCop-84 resists the strength/grain-growth loss that afflicts
precipitation-strengthened competitors (NARloy-Z, Cu-Cr, AMZIRC) at the same elevated
temperatures — those alloys' precipitates either coarsen or dissolve; Cr2Nb does neither.

**Fabrication route — new process detail not in `[MatCh2]`** `[GRCop84-TM2005 Production p.1-2]`:
Cu-Cr-Nb alloys REQUIRE rapid-solidification processing — conventional (slow-cooled) casting
lets Cr2Nb precipitates grow past 1 cm diameter, destroying the dispersion-strengthening effect.
Production route: elemental Cu/Cr/Nb melted together, then **argon gas atomization** (chosen
over chill-block melt spinning for industrial-scale volume/cost/cooling-rate balance) to powder
(<106 µm, ~40 µm mean, for extrusion/HIP; <53 or <44 µm for vacuum plasma spray/VPS), then
consolidated by **direct extrusion**, **hot isostatic pressing (HIP)**, or **VPS** (the latter
used by NASA Marshall for full liner shapes including a full-scale SSME MCC liner geometry, with
the ability to co-deposit a NiCrAlY functionally-graded coating layer on the hot wall in the same
spray operation). Iron contamination from the chromium feedstock was found to measurably degrade
thermal conductivity; spec tightened to <50 ppm Fe (required) / <20 ppm Fe (desired), recovering
~7% room-temperature thermal conductivity. Post-consolidation, GRCop-84 forms/rolls/bends/stamps
like a conventional copper alloy (forming-limit diagrams exist at RT and 200 °C); **tube drawing
demonstrated down to 0.3 cm OD × 0.08 cm wall (0.125 in OD × 0.030 in wall)**, specifically for
RP-1 fuel-compatibility testing — directly relevant to any regen-cooling tube-wall-construction
context in `engine_designer`'s `hatbands.py`/`tube_bundle.py`.

**Thermal expansion (CTE) — qualitative only, no absolute number stated** `[GRCop84-TM2005
Thermal Expansion p.7]`: GRCop-84 has **the lowest CTE of any competitor alloy examined**, about
**7% lower than pure copper** in the hot-wall temperature range (typically 400-600 °C hot-wall
vs near-room-temperature cold wall/lands in a H2-fueled engine, producing >1% thermal strain
through the wall). This directly reduces thermally-induced creep stress and LCF strain range —
the paper states a **2- to 100-times life increase** from substituting GRCop-84 for other Cu
alloys, "depending on the failure mechanism" (a wide, application-dependent range, not a single
multiplier). **No absolute CTE value (e.g. MatCh2's 15.3×10⁻⁶/K) appears anywhere in this TM's
text** — Figure 9 is a plot, not digitized here (see Caveats), so MatCh2's exact figure cannot be
independently confirmed from this source, only its qualitative "GRCop-84 has the lowest CTE"
ranking.

**Thermal conductivity** `[GRCop84-TM2005 Thermal Conductivity p.8]`: GRCop-84's thermal
conductivity is **305-320 W/m·K (176-185 BTU/h·ft·°F), i.e. 75-84% of pure copper's**, "over the
operating temperature range of an MCC liner" — comparable to NARloy-Z near room temperature but
falling further below NARloy-Z at hot-wall temperatures. The resulting wall-temperature penalty
vs. NARloy-Z for a real rocket-engine liner analysis is **typically ≤35 °C (65 °F)** — small
relative to GRCop-84's ~200 °C (360 °F) higher usable-temperature ceiling over NARloy-Z, i.e. the
strength/creep/LCF gain far outweighs the conductivity cost in a real design trade. Room-
temperature electrical conductivity ≈ 67% IACS for as-extruded material; a polynomial fit for
electrical resistivity vs. temperature is given (Fig. 11, cryogenic range) but not reproduced
here as it's not directly load-bearing for `engine_designer`'s thermal solve. **Cross-check**:
MatCh2's single-point 285.4 W/m·K sits just below this TM's stated 305-320 W/m·K operating-range
band — same order of magnitude and roughly consistent (MatCh2's "annealed" condition/reference
temperature isn't stated, so an exact reconciliation isn't possible from this TM alone), not a
contradiction, but also not an exact match; treat MatCh2's decimal-precision figure as sourced
from underlying tabulated data this narrative TM doesn't itself reproduce.

**Tensile strength** `[GRCop84-TM2005 Tensile Strength p.10-11]`: GRCop-84 was deliberately
optimized for HIGH-temperature strength at the cost of low-temperature strength — it is
inferior to Cu-Be and most other precipitation-strengthened Cu alloys at low temperature, but
"retains good strength to above 700 °C while other precipitation-strengthened copper-based
alloys generally lose most of their strength between 300 and 450 °C." After exposure to very
high temperatures (935-1000 °C, e.g. simulating a braze cycle), GRCop-84's strength loss is
small and nearly uniform (**20-35 MPa / 3-5 ksi**), unlike AMZIRC (fully recrystallizes, drops to
near pure-copper strength) or NARloy-Z (only partially recovers strength via re-aging, and even
then GRCop-84's yield strength is described as "still only half that of NARloy-Z" — i.e. NARloy-Z
after re-aging remains at HALF of GRCop-84's yield across the full temperature range, the
inverse framing of the same comparison). **In the 673-973 K (752-1292 °F) hot-wall design range**
(Fig. 12), GRCop-84 (as-extruded or as-HIPed) has a **yield strength 50-100 MPa (7-17 ksi) higher
than NARloy-Z**. Cold/warm working can push GRCop-84's room-temperature yield strength **above
400 MPa (58 ksi)**. After a 500 °C/100 hr exposure simulating 400 SSME missions, samples showed a
statistically significant strength INCREASE, not decrease — further evidence of thermal
stability rather than degradation. **Cross-check against `[MatCh2]`'s "annealed" 196.2 MPa yield
/ 368.0 MPa UTS / 21.7% elongation for GRCop-84 vs. 192.0 MPa yield / 314.0 MPa UTS / 31.0%
elongation for NARloy-Z**: MatCh2's near-parity yield values (196.2 vs 192.0 MPa, only ~4 MPa
apart) do NOT show the "50-100 MPa higher" gap this TM states — but that gap is explicitly stated
for the **673-973 K hot-wall temperature range**, not room temperature, and this TM separately
states GRCop-84's low-temperature strength is comparatively unremarkable ("inferior... to most
other precipitation-strengthened copper-based alloys" at low temperature). **This reconciles
rather than contradicts**: MatCh2's "annealed" figures read as room-temperature values, where
GRCop-84's strength advantage over NARloy-Z has not yet manifested per this TM's own account —
the two sources are describing different temperature regimes, not disagreeing about the same one.
UTS (368.0 vs 314.0 MPa, GRCop-84 ~17% higher) and elongation (21.7% vs 31.0%, GRCop-84 lower,
consistent with this TM's own Fig. 16/17 statement that GRCop-84's elongation/reduction-in-area
trail "many other low-alloy copper-based alloys" though it stays "over 5%" even when degraded)
are both directionally consistent with this TM's qualitative story.

**Creep** `[GRCop84-TM2005 Creep Rates and Lives p.14]`: tested 500-800 °C (932-1472 °F). GRCop-
84's creep life is **1 to 3 orders of magnitude longer than NARloy-Z** at the same temperature,
or equivalently **~15% more sustained load at the same creep life**. Creep behavior: mostly
secondary (steady-state) creep with a gradual tertiary transition before failure; creep
elongation at failure typically **8-14%**. A Larson-Miller comparison (Fig. 18) ranks GlidCop
AL-15/AL-35 (alumina dispersion-strengthened) as equal-to-or-better than GRCop-84, with GRCop-84
clearly ahead of NARloy-Z (before and after a 935 °C simulated braze cycle) — i.e. GRCop-84 is
not the single best copper alloy for creep in absolute terms, but is a large, clear improvement
specifically over the SSME-baseline NARloy-Z.

**Low-cycle fatigue (LCF)** `[GRCop84-TM2005 Low-Cycle Fatigue Lives p.15]`: LCF life is
"minimally influenced" by temperature up to 600 °C (the highest temperature tested), attributed
to the Cr2Nb dispersion retarding persistent-slip-band formation. GRCop-84's LCF life is
comparable to AMZIRC but **clearly superior (in some cases by over an order of magnitude) to
NARloy-Z, GlidCop, and pure copper** — LCF is called out as "the primary property driving design
of most liners for reusable launch vehicles," making this one of the most consequential
citable findings for a regen-chamber thermal-fatigue design context (parallel to
`mass_model.py`'s throat low-cycle thermal-fatigue estimate).

**Oxidation resistance and blanching** `[GRCop84-TM2005 Oxidation Resistance and Coatings
p.16-17]`: below 700 °C, GRCop-84 forms a protective Cr-Nb-oxide sublayer beneath the outer
copper-oxide scale, reducing its oxidation rate to **almost an order of magnitude below pure
copper** (NARloy-Z's oxidation rate is "almost identical" to pure copper — i.e. NARloy-Z gets
NO oxidation-resistance benefit that GRCop-84 gets). Above 700 °C the mechanism changes and
GRCop-84's oxidation rate converges back to that of copper/NARloy-Z — reinforcing 700 °C as
GRCop-84's real service-limit inflection point from a second, independent mechanism (oxidation)
beyond the strength-retention framing in the Executive Summary. **Blanching** (a H2-fueled-
engine-specific failure mode: rapid hot-wall oxidizing/reducing cycling forms a low-conductivity
"copper sponge" that promotes local hot spots and cracking) is inherently reduced but NOT
eliminated in bare GRCop-84 relative to NARloy-Z — a protective coating (NiCrAlY, applied as a
functionally-graded material via VPS, or a Cu-17Cr chromia-forming coating) is still required for
multi-use/reusable-vehicle service life; NiCrAlY was found superior to Cu-Cr coatings under
cyclic-oxidation and sulfidation testing (incl. a 5-atm high-sulfur JP-8 combustion-environment
compatibility test, relevant if GRCop-84 were ever considered for a hydrocarbon-fueled rather
than H2-fueled liner).

**Joining** `[GRCop84-TM2005 Joining p.18; Table I-II p.18-19]`: GRCop-84 has been successfully
friction-stir-welded (FSW, self-to-self only), inertia-welded (to 310/316 stainless steel, with
LCF specimens failing in the base GRCop-84 rather than the weld joint — the weld is NOT the
limiting feature), electron-beam-welded, diffusion-bonded, and brazed (compatible with
conventional copper brazes). **Real quantified FSW joint-efficiency data** `[Table I]`: room-
temperature FSW butt-weld yield 203.6 MPa / UTS 403.4 MPa / elongation 18.0% / RA 20.3%, vs.
as-rolled base-plate yield 225.6 MPa / UTS 403.1 MPa / elongation 23.8% / RA 41.9% — FSW retains
**90.3% of base yield, 100.2% of base UTS (i.e. UTS essentially unaffected), 75.2% of base
elongation, 48.4% of base reduction-in-area**. A second FSW-plus-metal-spinning liner-preform
weld-region dataset `[Table II]` shows, unusually, the FSW+spun material retaining MORE strength
at 538 °C (1000 °F) than as-rolled plate at the same temperature (157.3/176.6 MPa yield/UTS vs.
107.8/138.9 MPa for as-rolled) — likely a grain-refinement effect from the combined forming +
FSW deformation, not a general "welding improves strength" result. This is real, quantified
joint-strength-derating data — a useful anchor if `engine_designer` ever needs a welded/brazed-
joint strength knockdown factor for a copper-alloy liner rather than assuming parent-metal
allowable everywhere.

**Component/hot-fire testing — real validation of the blanching-resistance claim**
`[GRCop84-TM2005 Component Testing p.20]`: an uncoated VPS liner accumulated 142 s over 11 hot-
fire tests (≤30 s each) at O2:H2 = 7:1 (mixture ratio limited specifically to avoid blanching)
with no detectable surface change. A NiCrAlY-FGM-coated liner accumulated 340 s over 17 tests: a
follow-on **nominal 5000-lbf-thrust NiCrAlY-coated GRCop-84 liner survived 108 hot-fire tests,
including 8 at STOICHIOMETRIC O2:H2 ratio** (the specific condition that "would degrade an
uncoated NARloy-Z liner in a few seconds due to blanching") with no detectable damage, and no
hot-wall cracks — contrasted explicitly against 1970s NARloy-Z liners of similar scale/testing
that DID crack. This is the paper's single most concrete real-hardware demonstration: a
GRCop-84 + NiCrAlY-FGM liner surviving a wall-material failure mode (blanching) that is
essentially guaranteed to destroy an uncoated (or even coated) NARloy-Z liner at the same
operating point.

**Headline design-limit number** `[GRCop84-TM2005 Executive Summary p.1; Summary p.21]`: GRCop-
84 is characterized throughout as usable "up to approximately 700 °C (1292 °F)" (973 K) — stated
independently in the Executive Summary, in the tensile-strength discussion, and again in the
oxidation-mechanism-change discussion (three independent restatements, the same
cross-check-via-repetition pattern used to validate `[Lewis-Deposits]`'s numbers in this same
batch). This is the single number most directly relevant to `materials.py`'s
`max_service_temp_k` framing for a GRCop-84 entry, and it is well-corroborated within this
source alone.

## Design method

Not a sizing/allowable-stress handbook — no closed-form CTE/conductivity/allowable-stress
equations are given; all quantitative comparisons are relative (percent differences, order-of-
magnitude multipliers) or read off un-digitized plots. The usable outputs for `engine_designer`
are: (1) the resolved atomic-%-vs-weight-% composition basis for GRCop-84 (Cu-8Cr-4Nb at.% ≈
Cu-6.5Cr-5.8Nb wt.%, reconciling the `[MatCh2]`-flagged inconsistency); (2) a real, independently
stated 700 °C (973 K) service-temperature ceiling, corroborating whatever value `materials.py`
currently assigns; (3) real fabrication-route detail (powder metallurgy via gas atomization +
extrusion/HIP/VPS) establishing GRCop-84 as a conventionally-manufacturable liner material, not
an exotic one-off; (4) real FSW joint-efficiency knockdown factors (90.3%/100.2%/75.2%/48.4% of
base yield/UTS/elongation/RA) as a citable joint-strength derating anchor if ever needed; (5) a
real hot-fire-tested precedent (108 tests incl. 8 stoichiometric) for GRCop-84+NiCrAlY surviving
a wall-failure mode (blanching) that destroys uncoated NARloy-Z, useful qualitative backing for
any coating-recommendation logic tied to material choice; (6) the LCF-life-is-liner-life-limiting
framing, reinforcing why `mass_model.py`'s throat LCF estimate is the right kind of check to have
for a copper-alloy chamber liner specifically.

## Section map

- Cover/front matter/availability notice: leaves 0-3 — read (metadata only).
- Executive Summary + Introduction + Production (composition, fabrication route): leaf 4-5
  (printed p.1-2) — read in full.
- Figures 1-5 (extrusion/rolling/forming/VPS photos): leaf 6-7 (printed p.3-4) — read captions,
  images not independently re-rendered (photographic, not data plots).
- Microstructure: leaf 8-9 (printed p.5-6) — read in full, incl. Figs. 6-8 captions.
- Thermal Expansion: leaf 10 (printed p.7) — read in full; Fig. 9 plot not digitized (no axis
  values extractable as text, and the qualitative "~7% lower than Cu" claim is stated in prose).
- Thermal Conductivity + electrical resistivity: leaf 11-12 (printed p.8-9) — read in full;
  Fig. 10 plot and Fig. 11 polynomial-fit equations captured directly from extracted text
  (the resistivity fits are printed as text/equations, not embedded in a raster image).
- Tensile Strength: leaf 13-16 (printed p.10-13) — read in full, Figs. 12-17 captions.
- Creep Rates and Lives: leaf 17 (printed p.14) — read in full, Fig. 18 caption.
- Low-Cycle Fatigue Lives: leaf 18 (printed p.15) — read in full, Fig. 19 caption.
- Oxidation Resistance and Coatings: leaf 19-20 (printed p.16-17) — read in full, Figs. 20-21
  captions.
- Joining (incl. Tables I-II numeric data): leaf 21-22 (printed p.18-19) — read in full, this
  is the only section with standalone numeric tables in the entire body text.
- Component Testing: leaf 23 (printed p.20) — read in full, Fig. 23 caption.
- Summary + Contact Information + References (19) + Bibliography (19): leaf 24-25 (printed
  p.21-22) — read in full (titles only for the cited reports, not chased further; several,
  e.g. Ellis & Keller's NASA/CR-2000-210055 *Thermophysical Properties of GRCop-84*, are
  plausible sources for MatCh2's exact decimal-precision CTE/conductivity figures but were not
  independently acquired here).
- Report Documentation Page (abstract, restates the "up to 700°C" headline): leaf 27 — read.
- Leaves 28-29 (blank trailing pages): not applicable.

## Caveats

- **This is a narrative review/executive summary by the alloy's own developer, not an
  independent third-party data source or a properties handbook** — every comparative claim
  ultimately traces back to the author's own or NASA-internal prior work (References/
  Bibliography), most of which is not itself in `claude_lit`. Treat this TM as a well-organized
  index into that underlying work, not as the primary data itself.
- **No absolute numeric values for CTE, thermal conductivity, yield/UTS/elongation are given as
  clean tabulated entries anywhere in the body text** (except the two small FSW/metal-spinning
  tables) — everything else is a plot (not digitized here), a percentage delta, or an
  order-of-magnitude comparison. This means `[MatCh2 Table 2.6.3]`'s specific decimal figures
  (15.3×10⁻⁶/K CTE, 285.4 W/m·K, 196.2/368.0 MPa yield/UTS, 21.7% elongation) are only
  DIRECTIONALLY/ORDER-OF-MAGNITUDE corroborated here, not independently reproduced — see the
  per-property cross-check notes above (thermal conductivity: roughly consistent but not an
  exact match; yield strength: reconciled once the room-temperature vs. 673-973K
  temperature-regime distinction is accounted for, not a straightforward match or mismatch).
- **A tensile-properties companion source for GRCop-84 exists in this same literature batch**:
  `literature/NASA TM-2012-217108 - Tensile Properties of GRCop-84.pdf`, being distilled
  separately (not read for this note, per task instructions) — that source is a much more
  likely candidate for MatCh2's exact decimal tensile figures than this 2005 narrative TM, and
  should be checked for a tighter cross-check once its own source note exists.
- **All figures (14 of them, plotting CTE/conductivity/strength/creep/LCF/oxidation-rate
  vs. temperature) were read only via their captions, not digitized as images** — captions
  capture the qualitative trend and any numbers explicitly stated in prose, but exact curve
  values/slopes are not extracted. If a future need arises for, e.g., the exact GRCop-84
  yield-strength-vs-temperature curve, Fig. 12/15 would need to be re-rendered as a pixmap and
  read visually.
- **"50-100 MPa higher than NARloy-Z" (Fig. 12) is stated for the 673-973 K hot-wall design
  range specifically** — do not apply this delta at room temperature, where this TM's own text
  says GRCop-84's low-temperature strength is unremarkable relative to competing
  precipitation-strengthened alloys.
- **Even bare/uncoated GRCop-84 is explicitly NOT a substitute for a coating in reusable/
  multi-use service** — the "inherently more resistant to blanching than NARloy-Z" finding
  is a reduction in a failure mode, not elimination; all of the paper's strongest hot-fire
  validation (108 tests, 8 stoichiometric) was with a NiCrAlY functionally-graded coating, not
  bare GRCop-84. Any `engine_designer` materials entry citing GRCop-84's blanching resistance
  for a LOX/LH2 chamber should carry the same caveat.
- **Clean digital-native PDF, no OCR issues** — unlike several other sources in this literature
  set (e.g. `[Lewis-Deposits]`), no cross-checking against duplicate restatements was needed for
  extraction-fidelity reasons; the composition/temperature repetitions cited above were checked
  for genuine cross-source corroboration purposes, not OCR-error mitigation.
