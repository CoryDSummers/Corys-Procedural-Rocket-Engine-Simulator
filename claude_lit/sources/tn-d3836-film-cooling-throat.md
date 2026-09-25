# NASA TN D-3836 — Gaseous-Film Cooling of a Rocket Motor with Injection Near the Throat

## Identity

James G. Lucas and Richard L. Golladay (Lewis Research Center, Cleveland, Ohio), *Gaseous-
Film Cooling of a Rocket Motor with Injection Near the Throat*, NASA Technical Note
TN D-3836, February 1967 (report prepared Oct. 14, 1966; work unit 122-29-07-03-22).
`literature/NASA TN D-3836 - Gaseous-Film Cooling of a Rocket Motor with Injection Near the
Throat.pdf` (NTRS 19670008176 — filename just renamed from the raw accession number; 34 PDF
leaves: leaf 0 cover, leaf 1 tech-library verso, leaves 2-33 = printed pages 1-32 body/
appendices/references — printed page number = PDF leaf index − 1 throughout, confirmed
against two rendered page images). Tag: `[TN-D3836]`. Explicitly a **continuation** of the
same authors' earlier NASA TN D-1988 (1963, their own "reference 5"), which tested the same
gaseous-film-cooling correlation with coolant injected further upstream, in the *cylindrical
combustion-chamber* section — this report moves the injection point into the *convergent
nozzle*, ~1 inch upstream of the throat, "in a region of high velocity and high acceleration
of the hot gases" (p.3). Text is clean, well-OCR'd throughout (a crisp 1967 NASA TN scan);
the one dense equation set (p.8-9) was independently confirmed against rendered page images
since its subscript-heavy layout garbled badly in plain-text extraction.

## Character

A small-scale, single-variable experimental study — the counterpart in this reference set to
`[TN-Dump]`'s dump-cooling rig, from the same lab and era, but testing a distinct cooling
mode: **gaseous-film cooling of an ADIABATIC (uncooled) wall**, not a combined film+regen
design. The downstream nozzle test article is a thin (0.060 in), instrumented, spun
low-carbon-nickel shell insulated on the outside (glass-fiber + plaster shell) specifically
to force it toward its adiabatic-equilibrium temperature — i.e. this measures how hot an
*unprotected* wall gets with only a film-coolant curtain shielding it, isolating film-cooling
effectiveness from any coolant-side heat removal. Test motor: a JP-4/gaseous-oxygen engine
rated to 500 psia/3700 lbf but run here at a fixed and comparatively low **Pc = 60 psia**,
stoichiometric mixture ratio, in a 10-ft altitude tank (p.3-4); 40-element concentric
(O-around-F) injector, three rows; water-cooled, ZrO2-coated combustion chamber upstream of
the interchangeable research-nozzle test section. Coolant: **nitrogen**, injected
**tangentially** through a thin annular slot located ~1 in upstream of the throat (chosen to
place the slot at/near the point of maximum nozzle heat flux, p.6-7), at ambient temperature.
Two slot heights tested: **0.045 in and 0.040 in**. Structure: Summary, Introduction,
Experimental Apparatus and Procedure, Analytical Procedure (the correlation), Results and
Discussion (equilibrium-temperature accuracy, coolant-flow/slot-height trends, data
correlation), Considerations on Design of Film-Coolant Injector, Concluding Remarks, Summary
of Results, Appendix A (symbols), Appendix B (correlation-scheme comparison), References.
Read in full (32 printed pages, short).

## Key results

**The correlation — a real, quotable gaseous-film-cooling effectiveness-vs-distance formula**
`[TN-D3836 Analytical Procedure p.8-9]`, the modified Hatch-Papell equation (originating in
refs. 3-4, NASA TN D-130 and TN D-299):

    ln η = ln[(Tg − Tw)/(Tg − Tc)] = −[(hgLX)/(ẇc·cp,c) − K]·(S·Vg/αc)^(1/8)·f(Vg/Vc)
                                      + ln cos(0.8·β_eff)

with

    f(Vg/Vc) = 1 + 0.4·tan⁻¹(Vg/Vc − 1)              for Vg/Vc ≥ 1.0
    f(Vg/Vc) = (Vc/Vg)^{1.5[(Vc/Vg) − 1]}             for Vg/Vc ≤ 1.0

— `η` = cooling effectiveness, `Tg`/`Tw`/`Tc` = hot-gas/wall/coolant temperatures, `hg` =
hot-gas heat-transfer coefficient, `L` = cooled width (local nozzle circumference), `X` =
axial distance downstream of the injection slot, `ẇc`/`cp,c` = coolant mass flow/specific
heat, `S` = slot height, `Vg`/`Vc` = hot-gas/coolant velocity, `αc` = coolant thermal
diffusivity, `β_eff` = an effective injection-angle term (radians) for non-tangential
injection. For this study's tangential injection with `Vg > Vc` always, `f(Vg/Vc) = 1` and
`ln cos(0.8·β_eff) = 0` (both terms vanish), so the working form reduces to
`η = exp[−(hgLX/ẇc·cp,c − K)·(SVg/αc)^(1/8)]`. Under the original flat-plate conditions of
ref. 3, `K = 0.04`.

**Three specific, quantified modifications were needed to fit this near-throat-injection
data** `[TN-D3836 Analytical Procedure p.9; Appendix B p.28-31]` — the citable "how do you
adapt Hatch-Papell to a real converging-nozzle throat region" answer:
1. **K: 0.04 → 0.** Chosen purely to shift the data onto the correlating line ("solely to
   move the data curves to higher values of the correlating parameter," p.31) — not
   physically derived; the authors attribute the *need* for a change in K to possible
   pressure-gradient effects, coolant-film-thickness variation along the nozzle, hot-gas
   radiation, and stream-mixing/interaction at the injection point from the thick slot lip,
   but explicitly state "the true total effect is an undefinable combination of many
   conditions" (p.19-20).
2. **Driving temperature `Tg`: local hot-gas STATIC temperature, not recovery/total
   temperature** — even though the authors flag this "violates the heat-flow model from
   which the [Hatch-Papell] equation was derived" (p.31-32) and adopt it "except for the
   considerably better appearance of correlation with static values." Local static
   temperatures (from an equilibrium-composition thermochemistry code, ref. 7) ranged
   **5780°R at the station nearest injection down to 4727°R at the furthest station**
   (11 stations, Table I, p.10).
3. **`hgL` term: an INTEGRATED AVERAGE from the injection station to each downstream
   station, `(hgL)ₓ`, not a constant value evaluated at the injection point** (as the
   original flat-plate model used) — the paper walks through four intermediate failed
   attempts (constant `hgL` with total `Tg`; constant `hgL` with local `hg`; averaged `hg`
   between injection and local stations; integrated `(hgL)ₓ` with total `Tg`) before finding
   integrated `(hgL)ₓ` + local static `Tg` (+ K=0) is what actually correlates (curve
   progression A→F, Fig. 17, p.29-31). This integrated-average-heat-input framing (not an
   instantaneous local flux) is the report's core physical argument for why a converging,
   accelerating flow field needs a different treatment than the flat-plate original.

**Validity range: correlates from the slot out to ~100 slot heights downstream, then
degrades** `[TN-D3836 Data Correlation p.20-22; Concluding Remarks/Summary p.24-26]`: "the
distance along the nozzle over which satisfactory correlation was obtained includes the
entire region surrounding the throat, the area of greatest interest in auxiliary cooling
schemes" (p.20) — i.e. the correlation is validated for exactly the zone `engine_designer`'s
`nozzle_film_fraction`/`nozzle_film_inject_eps` targets (a throat-adjacent slot). Beyond
that, "it has been suggested that this correlation should be replaced by a boundary-layer
form of correlation at about **100 slot heights** downstream of the coolant injection slot,"
which eliminates the last 4-5 measuring stations from consideration (p.21-22) — a real,
quantified length scale (in slot-height units, i.e. proportional to `S`, not a fixed physical
distance) for where a simple exponential-decay film model like this one stops being
trustworthy. Practical framing offered: **using the equation beyond its validated range still
gives conservative (over-predicted) wall temperatures**, not unconservative ones (p.22) — a
usable fallback framing if `engine_designer` ever needs to bound rather than eliminate error
past a decay cutoff.

**Real coolant-fraction numbers, and the explicit N2→H2 scaling argument (the "poor coolant"
caveat)** `[TN-D3836 Concluding Remarks p.24-26]`: the tested nitrogen film-coolant-to-total
mass-flow ratios (`wc/wg`) ranged from **0.316 to 0.573** — very high, because N2 is
explicitly called "a poor coolant" for this purpose (low specific heat, high molecular
weight) and was chosen only for availability/cost/inertness, not because it represents a
flight design. The authors give a direct, quantified extrapolation to a flight coolant:
hydrogen has "a specific heat 14 times that of nitrogen," so **to a first approximation,
switching to H2 would cut the required coolant-to-propellant mass-flow ratio by a factor of
14**, bringing this test's 0.316-0.573 range down to **0.023-0.041 (2.3-4.1%)** — and H2's
much higher sonic velocity would additionally let the injector better match coolant-to-hot-
gas velocity (reducing turbulent mixing losses), pushing the true number even lower. Their
own final estimate for pure gaseous-film cooling alone (no regen) at this engine's Pc: **"a
coolant flow of something less than 2 percent of the propellant flow."** Two further,
directly citable design notes: (a) as chamber pressure rises, **the required film-coolant
FRACTION should fall slightly**, because the coolant demand scales with `hg`, and `hg` scales
with propellant flow only to the **0.8 power** (i.e. sub-linearly, so the ratio
coolant-flow/propellant-flow shrinks as propellant flow — and hence Pc — increases); (b) in
"most foreseeable" real applications, film cooling would be used *in combination with*
convective (regenerative) wall cooling rather than alone, which "would probably lower the
film-coolant flow ratio to the **1-percent range**." **Isp impact**: "the degradation to be
expected in engine performance would be very small with a film-coolant flow rate of around 1
percent" — and with H2 coolant specifically (vs. the heavier-molecular-weight combustion
products of any real chemical rocket), the authors suggest performance "degradation could
conceivably become an enhancement," because heated H2 has very high specific impulse of its
own — the same qualitative Isp-recovery argument `[TN-Dump]` makes for dumped/ejected H2
coolant, here applied to a film-cooling curtain instead of a dump-cooled jacket.

**Slot-lip thermal-mechanical design — a real, quantified failure mode and mitigation**
`[TN-D3836 Considerations on Design of Film-Coolant Injector p.22-25]`: a tangential
injection slot needs a thin lip exposed on its hot-gas side, and that lip is identified as
"a critical component" independent of the earlier `[TN-D3836]`/ref. 5 finding. Real
geometry: lip-support spacers equal in height to the slot height (**0.040 or 0.045 in**),
~**0.025 in** wide, ~**0.12 in** long, spaced ~**0.32 in** apart circumferentially, producing
about **15% blockage of the slot's flow area**; the lip's hot-gas-facing surface carried a
flame-sprayed **zirconia (ZrO2) coating ~0.010 in thick** for extra thermal protection, total
lip thickness (incl. coating) ~0.07 in. Even with spacer support, the lip still: buckled
slightly between supports; developed circumferential **compressive hoop stress above the
material's yield point** from restrained thermal expansion; and, upon quenching by cold
purge gas at shutdown, **shrank ~3% from its original diameter** — meaning slot height GROWS
after each firing, a real problem for a **restartable engine** (subsequent firings start with
a different, larger slot gap than designed unless the lip is also restrained against inward
motion). **Real mitigation for tube-wall (regen) construction**: a **corrugated lip** nested
into the tube-wall corrugations, following the tube contours — this reverses the failure
direction (circumferential thermal expansion would OPEN rather than close the slot, so it
can't choke coolant flow the way a flat annular lip can) and additionally lands the lip
support structure "in the valleys of the tube wall where heat-transfer coefficients and wall
temperatures are lowest" — i.e. deliberately locating a structural feature at the locally
coolest point of the contour, a real transferable design principle for any lip/hardware that
must penetrate a jacketed wall. **Alternative injection geometries** suggested where a
tangential slot's lip can't be adequately cooled: an angled slot, a series of angled holes,
or a porous wall section — explicitly traded off against **worse downstream cooling
performance** (per ref. 4, Papell TN D-299) than a well-executed tangential slot. Also: the
discrete lip-support spacers were found to **disturb circumferential coolant uniformity for
a "considerable distance downstream"** of the injection point (visible as a discoloration
pattern, Fig. 16) — a real, photographed footprint of discrete injector-lip hardware on the
downstream film-coolant distribution, not just a local/negligible effect.

**An unexplained non-monotonic "coolant flow depression" anomaly** `[TN-D3836 Trends of
Measured Wall Temperature p.13-16]`: with the 0.045-in slot, wall temperature vs. coolant
flow curves showed "a pronounced and unexpected depression" of **200-250°R** at coolant flows
of ~0.70-0.71 lb/sec — i.e. lower wall temperature than the general trend predicted, at a
SPECIFIC coolant flow rate, not a monotonic effectiveness improvement. If real/predictable
this would let a coolant flow "some 25 percent below the higher flow at which the same wall
temperature will result" be used — a genuine coolant-optimization opportunity — but the
authors state plainly "the reasons for the existence of this effect are unknown," data with
the 0.040-in slot at nominally the same coolant flow gave scatter of up to **470°R** at a
single station across three otherwise-identical firings, and they explicitly could not
determine "any functional relation" explaining it. **Treat as a reported curiosity, not a
usable design lever** — the source itself withholds confidence in it.

**Test-condition real numbers usable as magnitude anchors**: hot-gas velocity at the slot
assumed constant at **2450 ft/s** across the whole coolant-flow range tested (the correlation
was found insensitive to this — a 24% velocity change moved the correlating parameter only
9.9%, p.10-11); measured adiabatic wall temperatures across the full test matrix ranged from
roughly **850°R (near injection, high coolant flow) to ~2300°R (far downstream, low coolant
flow)** (Table II); firings were run 46-50 sec to approach thermal equilibrium (terminal
wall-temp slope only 0.7-1.6 °R/sec by 46 sec, confirmed against one 80-sec run, p.12);
circumferential wall-temperature nonuniformity was typically **±100-150°R** (p.12-13).

## Design method

A step-by-step, real film-cooling-effectiveness design procedure, distinct in kind from the
Bartz/Dittus-Boelter regen-side correlations already in `topics/06`: (1) get local hot-gas
static temperature, velocity and transport properties from an equilibrium-composition
thermochemistry solution at each axial station of interest; (2) get local hot-gas heat-
transfer coefficient `hg` at each station (Bartz-type or equivalent); (3) form the
INTEGRATED AVERAGE of `hg·L` (L = local circumference) from the injection point out to each
downstream station X — this integrated-average framing, not a local/instantaneous value, is
the paper's central methodological finding; (4) evaluate the correlating group
`(hgLX)/(ẇc·cp,c)·(S·Vg/αc)^(1/8)` with K=0 (this study's fitted value; K=0.04 for the
original flat-plate case); (5) for tangential injection with `Vg > Vc`, `f(Vg/Vc)=1` and the
injection-angle term drops out, so effectiveness `η = exp(−that group)`; (6) recover wall
temperature `Tw = Tg − η·(Tg − Tc)`. Valid out to ~100 slot heights downstream of injection;
beyond that, treat predictions as conservative upper bounds only, not a trustworthy design
number. This is exactly the closed-form "downstream distance → effectiveness" relation that
`OPEN_QUESTIONS.md`/`topics/06b-cooling-methods-and-chemistry.md` had flagged NASA SP-8124 as the
still-missing source for — see report summary below for how directly it can substitute.

## Section map

- Summary: p.1 — read.
- Introduction (incl. the ref-5 chamber-injection vs. this report's throat-adjacent-injection
  distinction, and the regenerative-cooling-pressure-limit motivation from ref. 1): p.2-3 —
  read.
- Experimental Apparatus and Procedure (motor, injector, nozzle/slot hardware, spacer/lip
  geometry, instrumentation): p.3-7 — read in full.
- Analytical Procedure (the Hatch-Papell equation, both f(Vg/Vc) branches, the K/Tg/hgL
  modification rationale): p.8-9 — read, and independently confirmed against rendered page
  images (this is the load-bearing equation of the whole note).
- Table I (hot-gas static temperature by station) / Table II (full firing-by-firing data,
  slot height/coolant flow/wall temps): p.10-11 — read.
- Results and Discussion — equilibrium-temperature accuracy and circumferential uniformity:
  p.12-13 — read.
- Trends of Measured Wall Temperature with coolant flow/slot height (incl. the unexplained
  depression anomaly), Figs. 6-10: p.13-16 — read.
- Data Correlation, Figs. 11-14 (the K=0.04→0 fit; ~100-slot-height validity limit): p.16-22
  — read.
- Considerations on Design of Film-Coolant Injector (lip thermal/mechanical design, corrugated-
  lip mitigation, alternative injection geometries): p.22-25 — read.
- Concluding Remarks (N2→H2 coolant-fraction scaling argument, Pc-scaling, Isp impact):
  p.24-26 — read.
- Summary of Results: p.25-26 — read.
- Appendix A (symbols): p.27 — read.
- Appendix B (Samples of Various Attempted Data Correlation Schemes — the curve-A-through-F
  progression showing why the integrated-hgL + static-Tg + K=0 combination was chosen), Table
  III (experimental hg by station), Figs. 17-18: p.28-31 — read.
- References (8 citations, incl. the authors' own earlier NASA TN D-1988 (ref. 5) and the
  underlying Hatch-Papell originals NASA TN D-130 (ref. 3) / TN D-299 (ref. 4), none yet in
  `claude_lit`, all clearly named potential follow-up sources for a deeper film-cooling
  correlation dive): p.32 — read (titles only, not chased).

## Caveats

- **Adiabatic-wall test, not a combined film+regen design article** — the downstream nozzle
  wall in this experiment is deliberately uncooled/insulated to reach its equilibrium
  temperature; this measures pure film-cooling effectiveness, not a jacket-plus-film system.
  Real applications (per the authors' own Concluding Remarks) would combine film with regen,
  which would change the required coolant fraction (they estimate down to ~1%) but that
  combined case is not itself tested here.
- **Nitrogen coolant, not a flight propellant** — the report is explicit that N2 was chosen
  only for cost/availability/inertness and is "a poor coolant" by mass-flow-ratio economy;
  the quoted 0.316-0.573 coolant fractions are NOT representative of a flight design. The
  ~14x-lower H2 estimate (→2.3-4.1%, or "<2%" per the authors' own final estimate) is a
  first-order scaling argument stated explicitly as an approximation ("to a first
  approximation"), not a second experimental data point — treat it as a plausible, source-
  stated estimate, not a validated H2 result.
- **Very low chamber pressure (60 psia) and small scale (500-3700 lbf motor)** — none of the
  quantitative coolant-fraction or wall-temperature numbers should be assumed to scale
  directly to a large, high-Pc engine; only the CORRELATION FORM (modified Hatch-Papell) and
  its fitted modification pattern (K→0, static Tg, integrated hgL) are argued to generalize,
  and even that argument rests on a single engine/geometry.
- **K=0, and the static-vs-total-temperature substitution, are BOTH stated by the authors
  themselves to be empirical fits without an agreed physical justification** — not derived
  constants. The static-temperature substitution is explicitly flagged as violating the
  model's own derivation ("there is no good reason for the use of static values ... except
  for the considerably better appearance of correlation," p.31-32). Any reuse of K=0 for a
  different geometry/propellant/injection scheme is unsupported without a fresh fit.
  Similarly, the two `f(Vg/Vc)` branches and the `ln cos(0.8·β_eff)` injection-angle term are
  reused from refs. 3/4 verbatim, not independently re-validated by this report (both are
  irrelevant here since `Vg > Vc` always and injection is tangential, so they were never
  actually exercised against this dataset).
- **The unexplained "coolant flow depression" anomaly** should not be treated as a usable
  optimization — the authors themselves could not find a functional relation for it, and a
  parallel dataset at nominally the same flow condition showed scatter (~470°R at one
  station) large enough to call the whole low-coolant-flow regime's data quality into
  question in that range.
- **~100-slot-height validity limit is itself a "suggestion" cited from elsewhere in the
  correlation literature** (attributed generically, not to a specific named reference with a
  page number), applied here as a post-hoc explanation for why the last 4-5 measuring
  stations didn't fit — not independently derived or proven by this report's own data beyond
  observing that those stations correlate poorly.
- **No coolant-side pressure-drop, manifold, or slot-lip stress-formula content** — the
  lip thermal-mechanical findings (yield-exceeding hoop stress, ~3% shrinkage) are reported
  as observed outcomes, not backed by a closed-form stress equation in this report (unlike
  e.g. `[Huzel]`'s tube-wall stress formulas already in `topics/06`).
- **1967-vintage, small-team single-facility study** — one rig, one propellant pair, one
  injector, two slot heights only; no independent replication by another lab is cited within
  the document (only continuity with the same authors' own earlier TN D-1988).
