# 06b — Cooling methods, coolant chemistry, and film cooling

## Scope

**Split out of `topics/06-cooling-and-heat-transfer.md` on 2026-09-24** (that file exceeded the
40 KB lookup-budget cap). `topics/06-cooling-and-heat-transfer.md` keeps the core Bartz/
Dittus-Boelter/radiation-cooling relations, the tube-wall structural-design equations, heat-
flux magnitudes, and the Bartz-calibration-error corroboration. **This file** covers: cooling-
method feasibility/construction-selection criteria, RP-1 as a fuel (coking, corrosion, and its
NIST-grade coolant thermophysical properties), film cooling (correlations and architecture),
the coolant-side (h_c) correlation catalog, and the Russian-sandwich-wall-construction
literature search. Feeds the same `engine_designer/physics/cooling.py`/`manifold.py`/
`thermo_tables.py` as the parent file.

## Empirical correlations & typical values

**Regenerative cooling's limiting factors and feasibility bounds** `[Marquardt-5981 §V-B-1
p.12-13]` (a 1963 small-spacecraft-engine, 20–10,000 lbf, cooling-method-selection study —
treat magnitudes as representative of that scale, not large boosters): three named limits —
coolant supply pressure, minimum practical coolant-passage dimension, and maximum coolant
temperature rise (expressed as a max coolable expansion ratio, or for H2 specifically a max
allowable enthalpy rise). Earth-storable propellants below **~250 psia Pc** can use
regenerative, radiative, *or* ablative cooling — consistent with `[Sutton]`'s own "ablative
< ~250 psi" threshold (`topics/06-cooling-and-heat-transfer.md`'s cooling-method-selection
table), now cross-corroborated from an independent 1963 source. A worked earth-storable design
(N2H4+EDA/N2O4, 500–2000 lbf, 40:1 expansion) gives concrete numbers: **minimum practical
coolant-passage dimension 0.062 in**; regen-coolable Pc range scales with thrust at that
passage floor (F=500 lbf → Pc 30–60 psia; F=2000 lbf → Pc 120–240 psia, both a cooling-imposed
4:1 throttle ratio); and **cooled expansion ratio capped at 10:1**, with a radiation-cooled
refractory-metal skirt from 10:1 to 40:1 — the same regen-then-radiation architecture
`EngineDesign.regen_nozzle_end_eps` already implements, now with a real (if small-engine)
precedent. Cross-method regime summary from the same source: "radiation — low thrust, long
run times; ablative — low thrust, 10–300 s; regen — high thrust, medium-long run times; heat
sink — short run times."

**Regen-cooling plumbing/operational notes** `[Marquardt-5981 §V-B-1b p.12-13]`: coolant
jacket volume should be **gas-purged after each operating cycle** on a restart-capable
engine (drain-by-evaporation, hypergolic-reignition, and freezing risks from residual
coolant) — a purge path is a plumbing-design input, not something added after the fact.
Coolant preference ranking: **H2 best, then N2H4, then Aerozine-50**. Exterior jacket wall
temperature stays under 400°F for storable-liquid-cooled jackets but can exceed 1000°F for
hydrogen-cooled jackets. Real reliability data point: regen chambers have operated without
catastrophic failure with up to **10% of coolant passages holed** (space vacuum environment
— external leaks in atmosphere are more serious). Dump/open-tube cooling is explicitly gated
on regen feasibility ("a chamber that cannot be regen-cooled with the total fuel flow cannot
be dump-cooled by a fraction of it") — dump is only viable where regen is already easy (high
thrust or low Pc), corroborating rather than superseding `[TN-Dump]`'s own ~2% dump-fraction
treatment in `topics/07-dump-cooling.md`.

**Real construction-type selection criterion (tube vs. channel wall)** `[SP-8087 §3.1.1.1
p.54]` — a genuinely new, dimensioned decision rule this reference set didn't have before:
max heat flux **< 12 Btu/in²·s** → simple channel-wall recommended; **10-25 Btu/in²·s** →
tubular recommended (advanced channel-wall also usable); **> 25 Btu/in²·s** → advanced
channel-wall techniques should be used; **thrust < 20,000 lbf** → simple channel-wall
preferred regardless of heat flux; for **minimum weight**, tubular is recommended (an
explicit weight-vs-simplicity tradeoff, not a strict heat-flux-only decision). Real
wall-construction survey: all major production fluid-cooled chambers (1000-1.5M lbf, up to
1000 psia Pc) use multi-pass tubular construction except small/low-heat-flux units (Atlas
vernier, Aerobee: double-walled; Agena: drilled passageways) — directly consistent with the
above criterion. **Tube geometry**: max taper 3:1 by pure reduction (spinning/swaging), up
to 6:1 combined with an expansion process (beyond 6:1 costs escalate) `[SP-8087 §3.1.1.3.1
p.55]`; **minimum tube wall thickness 0.010 in** — thinner is "a poor risk" even when
analysis says it would work, due to flaw sensitivity/erosion/handling-dent risk; real
hardware needed raising 0.010 in to 0.016 in after pinholing `[SP-8087 §3.1.1.3.2 p.56,
§2.1.1.3 p.13]`. **Channel aspect ratio**: width/height < 2 in high-heat-flux regions
(avoids corner velocity-depression); up to 8 acceptable if height > 0.10 in `[SP-8087
§3.1.1.4.1 p.58]`. **Coolant velocity limits**: liquids < 200 ft/s; gases < Mach 0.3
recommended, 0.5 absolute max (choking risk at bends above that) `[SP-8087 §3.1.1.5.3
p.61]`. **Thermal margin**: operate heat-flux-limited coolants at < 80% of mean burnout
flux `[SP-8087 §3.1.1.5.2 p.60]`. **Wall temperature chemical limits**: RP-1 coking above
850°F (728 K); furfuryl-alcohol-residue above 600°F; Aerozine-50 detonation risk above
600°F `[SP-8087 §3.1.1.5.4 p.61]` — consistent with this file's ~120K-ΔT coking-limit
framing below.

**RP-1 coking — real onset/peak band and rate data, not just a single threshold**
`[Lewis-Deposits, Abstract; Kerosene Fuel Tests p.5-7; Concluding Remarks p.12]`: a dedicated
UTRC/NASA-Lewis electrically-heated test-tube rig (not a firing engine, same character as
`[TN-Dump]`'s rig) measured **substantial RP-1 deposit formation between 600 and 800 K, with
peak deposit RATE occurring near 700 K** — a real, independently-measured band that sits
close to but is subtly different from `[SP-8087]`'s single-point 850°F (728 K) figure above:
728 K lands near this report's own measured *peak*, not its *onset* (600 K), suggesting
SP-8087's number is better read as a "significant/design-limiting" threshold than a true
onset. **Deposit rate is non-monotonic (bell-shaped) with wall temperature — it FALLS OFF
again above ~800 K**, so a flat "coking above X K" model understates the real physics; the
hottest wall station is not necessarily the worst one for fouling accumulation. Real rate
magnitude: **400-600 µg/cm²·hr for RP-1 at 500-800 K wall temp** (10-minute test exposure,
"not anticipated" to be this high per the authors); deposit rate falls with increasing
coolant velocity and is essentially **pressure-independent from 13.8 to 34.5 MPa** (136-340
atm) — i.e. the coking limit shouldn't need a Pc-dependent correction across typical/high
chamber-pressure ranges. **Nickel plating cuts the RP-1 deposit rate by ~10× (to ~50
µg/cm²·hr)** — bare copper is framed as *actively catalyzing* coking, not just a passive
substrate, a real quantified mitigation lever beyond "stay under the wall-temp limit."
More-refined JP-7 fuel (lower sulfur, deoxygenated) gave **no improvement over RP-1** — fuel
refinement alone is not a reliable mitigation on this rig; the wall material mattered far
more than fuel grade. Propane fouls worse than either kerosene fuel at any given wall temp
and shows a distinct near-critical-point (366 K) thermal instability with a copper-dendrite
deposit morphology — a different, more severe failure mode than kerosene's surface coke.
Caveat: fixed 10-minute test exposure, not directly extrapolable to a real engine's full
burn duration without a time-dependent fouling model this report doesn't provide — treat the
rate numbers as an order-of-magnitude anchor, not a life-prediction formula.

**Real closed-form gaseous-film-cooling effectiveness correlation — `[TN-D3836]` (2026-09-24)**
`[TN-D3836 §Analytical Procedure p.8-9]`: a real closed-form modified Hatch-Papell
correlation for a tangential coolant slot with hot gas faster than the coolant (Vg>Vc, the
typical case): `η = exp[-(hgLX/(ẇc·cp,c) - K)·(S·Vg/αc)^(1/8)]`, `η = (Tg-Tw)/(Tg-Tc)`. Three
empirical modifications were needed to fit near-throat/convergent-section injection (vs.
flat-plate or upstream-chamber injection): **K=0** (not 0.04), driving temperature **Tg =
local hot-gas STATIC temperature** (not recovery/total), and **hgL = an INTEGRATED AVERAGE**
h_g from injection to each downstream station (not a constant evaluated at injection).
**Validity range: ~100 slot heights downstream of injection** (covers the throat region;
degrades gracefully — over-predicts wall temp, stays conservative — beyond that). Real
coolant-fraction data: tested N2 fractions 0.316-0.573 (a poor coolant); scaled to H2 (14x
specific heat) gives an estimated 0.023-0.041 equivalent, with the paper's own final estimate
at "something less than 2%" pure film flow (~1% combined with regen) — Isp degradation "very
small," potentially even a net gain with H2 coolant (the same dumped-heated-coolant argument
as `[TN-Dump]`). A real, transferable slot-lip design finding `[TN-D3836 §Considerations on
Design of Film-Coolant Injector p.22-25]`: unsupported/spacer-supported tangential-slot lips
develop compressive hoop stress above yield on firing and **shrink ~3% on quench** — a real
restart-engine hazard (the slot narrows after firing). Fix: a corrugated lip nested in
tube-wall corrugations, supports at the tube valleys (coolest point of the contour), so
thermal expansion OPENS rather than closes the slot.

**SP-8124's own film-cooling model — closing the `OPEN_QUESTIONS.md`-flagged gap, 2026-09-24**
`[SP-8124 Appendix A (gas film)/Appendix B (liquid film); §3.5.2 p.86]`: NASA's own
self-cooled-chamber design-criteria monograph gives a full entrainment-based integral model
for both gas- and liquid-film cooling — real closed-form pieces exist (a liquid-film-length
equation `L = (1/Λ)·ln[1+Λ·Wc/(...)]`, an entrainment-flow-ratio integral, a first-order
monopropellant vapor-decomposition decay `f_v = exp(-λτ)`), but film EFFECTIVENESS itself and
two augmentation factors are read off empirical graphs (Figs. A-2, B-1), not closed algebraic
functions — a different (entrainment-mechanism) framing of the same problem `[TN-D3836]`
solves via curve-fit, not a simpler alternative to it. One directly portable number: a real
H2-film-cooling firing-data entrainment-fraction multiplier **ψ_m = 3-4 at injection, decaying
linearly to ~1.75 at the throat**. Likely the primary source underlying `[EUCASS-2023]`'s
Appendix-B film-cooling citation. **`OPEN_QUESTIONS.md`'s "SP-8124 still missing" gap is now
resolved** — not with one clean equation, but with two independent real sources (`[TN-D3836]`'s
closed-form correlation, `[SP-8124]`'s entrainment model) whose basic architecture
(effectiveness decays with entrainment/distance; near-injection behavior differs from
far-field) corroborates.

**A new cooling architecture: interregen/heat-sink and adiabatic-wall chambers** `[SP-8124
§2.3/§3.3, §2.4/§3.4]`: distinct from regen/film/ablative/radiation, real self-cooled-chamber
design criteria include a heat-sink-liner architecture (beryllium ≤1800°F or copper ≤1100°F
liner), real 30-40%-fuel-flow film-cooling design practice with a real **94% c* efficiency at
38% film fraction** data point, and radiation-cooled-extension starting at area ratio **3-10**
(a second real precedent for `regen_nozzle_end_eps`, alongside `[SP-8120]`'s F-1 ε=10
example). Real hot-restart temperature limits: 900°F (MMH) / 700°F (A-50) before a restart is
unsafe. Not currently modeled in `engine_designer` — no heat-sink/interregen method exists in
`WALL_CONSTRUCTIONS` — report-only, a real but currently out-of-scope architecture.

**RP-1 as a real regenerative coolant — NIST thermophysical property sources (2026-09-24)**:
four companion NIST-grade papers give the primary literature basis a Cantera/CoolProp-style
RP-1 coolant-property pipeline (`thermo_tables.py`'s baked tables) would draw from.
`[NISTIR6646-RP1 §2, §4-7]` (the foundational report): a real 14-component RP-1 surrogate
mixture (n-dodecane-anchored, extended-corresponding-states transport model), real measured
density (813→785 kg/m³, 2.9-43°C), thermal conductivity (~0.11-0.13 W/(m·K) at 300K falling to
~0.068 near 649K), viscosity (7.667→1.126 mm²/s, 243-333K), and bulk thermal-decomposition
kinetics (half-life 167min@648K → 11min@773K — a DIFFERENT quantity from `[Lewis-Deposits]`'s
wall-surface deposit-rate data above, don't conflate). Stated model uncertainty: density 0.3%,
Cp 7%, λ 3%, viscosity 3% (atm)/10% (60 MPa). `[Huber-RP1RP2]` gives a simpler, complementary
4-component surrogate (α-methyldecalin/5-methylnonane/n-dodecane/heptylcyclohexane), stated
accuracy vs. real data (density 0.4%, viscosity 2%, thermal conductivity 4%), and a real
RP-1-vs-RP-2 property-difference summary (RP-2 ~3-5% higher viscosity, <1% different
density/sound-speed — RP-2's higher C16-alkane content vs. RP-1's C14 ceiling). `[Outcalt-
RP1RP2]` gives the primary MEASURED density/speed-of-sound/viscosity tables (270-470K, to
40 MPa) both surrogates are fit against, plus fitted Rackett/Tait/DIPPR-viscosity correlations
— explicitly cautioned by its own authors as "sample-specific... should not be generically
applied." `[Akhmedova-RP1]` adds real measured thermal conductivity (292-732K, 0.1-60 MPa) and
the headline **batch-to-batch compositional-variability finding**: two real RP-1 samples
differ by ~2-4% in thermal conductivity along the same isobar — a real, citable uncertainty
bound on any single RP-1 λ value — plus independent thermal-decomposition-onset corroboration
at ~650K (consistent with `[Lewis-Deposits]`'s existing 600-800K wall-coking band, different
rig/mechanism). None of these four give data above ~700-800K — they characterize RP-1 strictly
as a liquid-phase coolant, not a combustion propellant.

**Sulfur corrosion of copper by RP-1 — a second, distinct hydrocarbon-fuel/copper-
compatibility mechanism** `[Quentmeyer-CR185257 §Hydrocarbon-Fuels/Combustion-Chamber-Liner
Materials Compatibility p.7-8]`: mercaptan sulfur at 50 ppm in RP-1 causes copper-sulfide
corrosion/deposit on a copper chamber liner; no reaction below 1 ppm sulfur; a gold coating
prevents it. This is a CHEMICALLY DIFFERENT mechanism from the carbon-coking/deposit-formation
physics `[Lewis-Deposits]`/`[TP2862-LOXRP1]` establish above/in `topics/06` (thermal
decomposition of the fuel itself, not fuel-impurity attack on the wall metal) — don't conflate
the two; a real design needs both a wall-temperature coking limit AND a fuel-sulfur-spec check.

**Real independent corroboration of existing design constants (background source)**
`[Armstrong-MarsISRU §Ch.IV, §Ch.VII p.24-28, 47-49]`: mostly background (Mars-ISRU CO/O2
propellant chemistry has no transfer value to any propellant pair `engine_designer` models),
but its cooling-methodology content is transferable and real: a richer supercritical-fluid
Nusselt-correlation catalog (Petukhov, Notter-Sleicher, Sieder-Tate viscosity correction,
Spencer-Rousar's dedicated supercritical-O2 fit, validated 17-34 MPa/T>100K/±30%) complementing
`[Fagherazzi-2019]`'s existing set below; independent corroboration of a **coolant-channel
aspect-ratio practical ceiling of 8** (matches `[SP-8087]`'s own number despite an opposite
width/height framing convention); independent ~4% corroboration of the **811K (1000°F) copper
hot-gas-wall elastic limit** (`[Wieseneck-J2]`, `topics/06-cooling-and-heat-transfer.md`) via a
778K figure; and a second independent corroboration of the **15-20% injector-dP-for-stability
rule** (`topics/05-injectors.md`). A real LOX-side (oxidizer-side) regen-cooling precedent:
NASA's in-house REHTEP 1-D thermal code was validated against real LOX/RP-1 hot-fire
thermocouple data (MR 1.8-2.2, Pc 8.4-8.9 MPa) — a real precedent for oxidizer-side regen
cooling of a hydrocarbon copper chamber, plus a second independent real-firing corroboration
that a thin soot layer measurably raises predicted wall temperature.

**Russian "sandwich" wall construction — CORRECTION (2026-09-24): real construction detail
was already in `claude_lit` all along, in `[Ch12-Materials]`, just never checked against this
question.** Six sources were searched *specifically for this* across two earlier rounds —
`[SP-8087]`, `[Gubanov-1991]`, `[Wieseneck-J2]`, `[Fagherazzi-2019]`, `[EUCASS-2023]`,
`[ChannelWall-IAC19]` — and all six genuinely came up empty (detail below). But
`[Ch12-Materials]` was distilled in an *earlier* batch (2026-09-14), before this question was
ever asked, and was never re-checked against it — a real gap in the search process, not in
the literature itself. Its §12.5.2 (printed p.26-28) gives real engineering detail:
**construction** — Cu-Cr (Cu~3%Cr) inner liner with milled slots/channels for channel-wall,
or a **corrugated sheet-metal divider** between the Cu-Cr liner and an outer shell (alloy
steel/stainless/Ni-base) for sandwich-wall, the corrugations themselves forming the coolant
flow passages; **joining method** — originally (1930s) just bolted together with tolerated
inter-channel leakage, replaced post-WWII by a pressure-brazing method the Russians call
"solder-welding," the development that "made possible effective, efficient and reliable
rocket engines"; **real application** — channel-wall is usually used for the *combustion
chamber*, while "for medium-performance engines, such as the RD-107, the expansion *nozzle*
is a sandwich structure"; **tradeoffs stated** — channel-wall/sandwich both reputedly cheaper
to fabricate than tubular, but heavier. A real complication for the "Russian" framing: the
source's own Figure 12-24 shows the **F-1's lower nozzle extension is ALSO sandwich
construction** (Hastelloy-C, dump-cooled with turbine exhaust) — so face-sheet-plus-
corrugated-core sandwich construction is not exclusive to Soviet practice, just bonded
differently (the source separately describes a modern Volvo/Vulcain nozzle-extension sandwich
design joined by laser welding, not brazing). **What's still missing**: no channel/corrugation
pitch, height, or wall-thickness numbers, no cross-section drawing dimensions, no structural
formula — this is real construction-concept-and-materials detail, not the dimensioned design
criteria `[SP-8087]`-style monographs give for tube/channel-wall. **The six-source "not
found" search below remains accurate for that deeper level of detail** — it just wasn't the
whole picture, since it never checked the one already-distilled source that names the
technology at all.

Original six-source search (still valid, now understood as incomplete rather than
exhaustive): `[SP-8087]` (NASA's dedicated fluid-cooled-chamber design-criteria monograph —
confirmed via full-text search, the word "sandwich" never appears; its closest concept is
**"double-wall construction"**, a single-helical-channel design used only on small
low-heat-flux units like the Atlas vernier/Aerobee, explicitly NOT the high-heat-flux
multi-channel construction Russian engines like RD-170/RD-253/RD-180 are known for —
SP-8087's own introduction says advanced channel-wall fabrication was still "in development"
and "not covered in detail" as of 1972); `[Gubanov-1991]` (a paper by Energia's own chief
designer, giving real RD-170/RD-120/RD-0120 spec tables — but its only chamber-construction
description is one generic sentence per engine, "the chamber is a brazed-welded unit," no
cross-section or layer detail at all); `[Wieseneck-J2]` (Rocketdyne's own V-2/Redstone→
tubular→channel-wall lineage narrative uses "double wall" for the same generic Western
1940s-50s category as SP-8087, not the Soviet construction); `[Fagherazzi-2019]` (a 156-page
regen-cooling thesis with its own construction-type literature review — covers only tubular
and machined-channel families, zero hits for "sandwich" or "double wall"); `[EUCASS-2023]`
(only discusses the milled-channel type it actually built); `[ChannelWall-IAC19]` (NASA
MSFC's 2019 channel-wall-nozzle manufacturing survey — modern 2012-2019 US
additive-manufacturing/water-jet-milling fabrication processes for milled-channel and
bimetallic walls, a different technology entirely, no corrugated/finned-core geometry or
Russian practice mentioned; it does give real hot-fire wall-temperature anchors instead —
peak measured hotwall temp ~1,350°F for RP-1-cooled Inconel 625 and ~1,300°F for GH2-cooled
JBK-75, both at real Pc up to ~1,240 psig — a real complement to the material max-use-temp
limits already cited from `[Huzel]`/`[Sutton]`).

**Remaining gap, narrowed**: a dimensioned design-criteria source (channel/corrugation
geometry, wall thickness, structural formula) for sandwich-wall construction specifically —
not the construction concept or materials, which `[Ch12-Materials]` now covers.

**Richer coolant-side correlation set + real convective/radiative split** `[Fagherazzi-2019
§2.4.5 p.42-44]`: five published Nu correlations compared (Sieder-Tate laminar/turbulent, a
laminar-turbulent transition blend, Gnielinski [most broadly valid, 3000 < Re < 5e6], and two
entrance-effect-corrected forms) — substantially richer than a single Dittus-Boelter-form
citation, useful if `cooling.py` is ever extended with a real coolant-side h_c correlation
instead of its current `WALL_CONSTRUCTIONS`-scaled proxy. A real **80% convective / 20%
radiative gas-side split** is quoted (citing Sutton) — a specific point estimate sitting
inside the existing "radiation is 5-35% of transferred heat" `[Sutton §8.2]` band, not a
contradiction. **A real jacket-ΔP rule of thumb**: maximum permissible regenerative-cooling
pressure loss is **15-22% of coolant inlet pressure**, "depending on design requirements"
`[Fagherazzi-2019 §2.5.4 p.59]` — a percentage-of-supply-pressure framing of the same
jacket-ΔP question `[Sutton Table 8-1]`/`[TN-Dump]`/`[Wieseneck-J2]`'s absolute-pressure
anchors already address (`topics/06-cooling-and-heat-transfer.md`), worth cross-referencing
if `design.py`'s `JACKET_DP_PA` is ever changed to scale with coolant supply pressure. A real,
useful negative finding: **channel cross-section reduction increases heat flux/lowers wall
temp but pressure drop rises faster-than-exponentially past a point of diminishing thermal
return** — no closed-form optimum exists, it must be found numerically (as `[EUCASS-2023]`
also does via a genetic algorithm). Also confirms the general principle (also seen in
`[SP-8120]`'s and `[Marquardt-5981]`'s minimum-passage findings) that **at small-engine scale,
minimum manufacturable wall thickness governs, not calculated stress** — a real worked
example found the structurally-required liner/channel-wall thickness (0.05-0.6 mm) far below
the practical 0.5 mm 3D-printing floor actually used.

**Real P&W in-house regen-channel design-rule set, recurring unchanged across 7 real
engines** `[STBE-PW leaf 161, 270, 321, 341]`: a 1989 Pratt & Whitney booster-engine
configuration study (seven fully-worked 600-750 Klbf-class LOX/CH4, LOX/RP-1 engines across
gas-generator, split-expander, and tap-off cycles) applies the **same four channel-geometry
guidelines to every variant** — passage aspect ratio ≤5.0, passage land width ≥0.050 in,
coolant Mach ≤0.5, 0.2%-yield tube-stress margin ≥1.0 with ultimate-temperature margin ≥375
R — strongly suggesting these read as period P&W standard practice rather than case-specific
results. A real worked point (Unique STBE Split Expander, LOX/CH4, Pc 896 psia): max
predicted hot-wall temp 2170 R, max heat flux 21 Btu/in²-sec, coolant Mach only 0.2 (well
under the 0.5 limit) — a real design margin, not a limiting case. Also: the Unique STBE GG
engine's minimum L* (31.3 in) is explicitly stated as the smallest value meeting a **98.0%
characteristic-velocity efficiency target** — a real, explicit c*-efficiency design
criterion rather than an assumed L* value, useful alongside `topics/04-chamber-sizing.md`'s
existing L* discussion. Separately, the Unique Split Expander's main chamber routes coolant
**countercurrent to the gas flow specifically "to provide the coolest fuel at the throat
where wall heat flux is highest"** `[leaf 320]` — an explicit real-engine rationale for
countercurrent regen routing, corroborating (not new to) the cooling-flow-topology choice
`cooling.py` already defaults to.

**CFD entrance-region corroboration, minor** `[Merkle-RegenCFD p.4-5]`: an idealized
straight-passage CFD case (water-as-RP-1-surrogate, non-reacting hot-gas boundary, not a real
engine) found wall temperature near a coolant passage's entrance **rises sharply, dips
slightly over the next ~50mm (copper's high conductivity redistributing the initial thermal
shock), then resumes increasing** — a real but narrow, geometry-specific CFD finding; not
portable as a number, and (like `[SECA-HT]`) not a correlation source. Also confirmed a
land-vs-passage-centerline circumferential wall-temperature non-uniformity that any 1-D/
axisymmetric model (including `cooling.py`'s contour-average treatment) cannot capture by
construction — a known, accepted simplification, not a new finding to act on.

**Near-injector under-heating — CFD-side corroboration** `[SECA-HT §4, ~p.58]`: a SSME
conjugate-heat-transfer CFD study (FDNS Navier-Stokes solver) found the same near-injector
wall-heat-flux reduction that `[TN-Dump]` measured empirically, though the three prior CFD
predictions it compares disagree on the *cause* (film cooling / combustion kinetics /
finite-rate vaporization). Two independent sources — one hardware test, one CFD — agreeing
on the phenomenon (not the mechanism) strengthens confidence in treating "combustion takes a
finite length to complete near the injector" as physically real, which is what motivates
`cooling.py`'s length-decaying `film_effectiveness_profile`. **Caveat**: `[SECA-HT]` is a
CFD-methodology report, not a correlation source — it has no Bartz/Dittus-Boelter-type
formula or calibration constant of its own (confirmed by an explicit text search: zero hits
for "Bartz," "Dittus," "Reynolds," "Prandtl," "Stanton," or "recovery factor" outside
citations to unavailable works). It cannot be used to derive or spot-check `cooling.py`'s
`BARTZ_ABS_FLUX_CALIBRATION` — treat it as qualitative/corroborating evidence only.

A related `[SECA-HT §4.3, ~p.70]` finding: a film-cooled RP-1/O₂ CFD case predicted correct
wall heating right at injection but found the film "mixes too fast" further downstream —
i.e. even a purpose-built CFD tool finds film-cooling *decay length* harder to predict than
near-injection effectiveness. Relevant context (not a portable number) for the shape of
`film_effectiveness_profile`'s length-decay assumption.

**Coolant-side ΔT limits** (from the tool's own expander model, representative): LOX/LH2
~500 K, LOX/RP-1 ~120 K (coking limit), N2O4/MMH ~150 K. `[TN-Dump]` (`topics/06-cooling-and-
heat-transfer.md`) shows LH2 coolant going from ~57–85 °R inlet to 1575–1900 °R outlet with a
refractory-metal wall — a ΔT of ~800–1000 K is achievable for hydrogen.

**A second real hydrocarbon/hypergolic film-cooling Isp-tax data point**
`[OME-Platelet §III.C.2.c, leaf 12]`: fuel film cooling at **~8% of fuel flow costs ~1 sec
Isp** on a like-doublet hypergolic OME injector, alongside `[TP2862-LOXRP1]`'s LOX/RP-1
zoned-injector number already cited above (`topics/06`) — a second real propellant-family
data point for `film_effectiveness_profile`/`dump_coolant_fraction`'s Isp-cost framing.

**Real 1960s ablative-chamber ply schedule** `[ApolloPP-1195 Fig. 18]` (label transcription,
illustrative material names not a verified BOM): the Apollo LEM ascent engine's fully-
ablative chamber (no radiation-cooled extension at all — unlike SPS/LM-descent, which
transition to radiation-cooled columbium/titanium skirts) builds up zone-by-zone from
distinct material systems: asbestos/phenolic-silica felt at the throat (HT-427 bond),
Irish Refrasil/EC-201 phenolic further aft ("302" bond), transitioning to filament-wound
glass-roving/epoxy-novolac at the nozzle-extension boundary. A real, if terse, example of a
multi-material ablative ply layup rather than one uniform material — no ply thickness/
erosion-rate numbers given, so not a sizing method, but real corroboration that "ablative"
covers a zoned material system in practice, not a single compound.

## Caveats

- `[Marquardt-5981]`'s numbers are small-spacecraft-engine scale (20–10,000 lbf, mostly
  <300 psia) and its actual sizing method is 11 hand-drawn parametric weight/feasibility
  graphs that are **not OCR-extractable** — only the discrete numbers quoted in body text
  and figure captions (above) are usable; don't infer curve shapes from it. 1963 vintage:
  named materials (Type 321 SS, columbium, Ta-10W) predate modern channel-wall alloys.
- `[SP-8087]` is 1972-vintage and explicitly pre-advanced-channel-wall (its own introduction
  says high-heat-flux non-tubular chambers were "in development" and "not covered in detail")
  — its double-wall/channel-wall content describes only simple small-engine implementations,
  not modern milled-liner or Russian sandwich-wall practice. Real numbers (heat-flux
  thresholds, taper ratios, velocity limits) are recommended practices from designer
  experience, not universal physical limits, per the monograph's own framing.
- `[Fagherazzi-2019]` is a single small-engine (250-400 N) master's thesis, one tier below a
  NASA design-criteria monograph or real-engine data — treat its own novel numerical claims
  (15-22% ΔP rule, the channel-cross-section negative finding) as small-engine-scale data
  points to corroborate against, not universal constants. It has no manifold-design content
  (checked specifically) — it only models flow inside the channels, not distribution to/from
  them.
- `[Merkle-RegenCFD]`, like `[SECA-HT]`, is a CFD-methodology demonstration, not a
  correlation source — cannot be used to derive or spot-check `BARTZ_ABS_FLUX_CALIBRATION`.
  Its geometry (640 uniform passages, water surrogate, non-reacting hot gas, 100mm length) is
  idealized, not a real engine; none of its numbers should be cited as real-hardware data.
- `[Lewis-Deposits]` is a standalone electrically-heated test-tube rig (not a firing engine),
  fixed 10-minute exposure only — its deposit-rate magnitudes are not directly extrapolable
  to a real engine's full burn duration. `[STBE-PW]`'s channel-geometry guideline set is
  stated but never cited to an external standard — read as in-house period practice, not a
  universally validated design criterion. `[ChannelWall-IAC19]` has no heat-transfer or
  structural design method at all (pure manufacturing-process/test-campaign survey) — cannot
  calibrate or validate anything in `cooling.py`.
- `[TN-D3836]` is a 1967 small-experimental-engine paper; its correlation's three empirical fit
  modifications (K=0, static Tg, integrated hgL) are curve-fits to that specific rig, not
  first-principles-derived — trust the correlation's FORM more than its exact coefficients on
  a different engine. `[SP-8124]`'s film-cooling model needs empirical graphs (Figs. A-2/B-1)
  not transcribed here — only the one portable number (ψ_m entrainment multiplier) and the
  closed-form pieces (liquid-film-length equation) are captured; a fully closed-form model
  would need a future deeper read of those figures (or refs. 76/81/103/107, SP-8124's own
  likely graph sources).
- `[NISTIR6646-RP1]`/`[Huber-RP1RP2]`/`[Outcalt-RP1RP2]`/`[Akhmedova-RP1]` are all real primary
  measurement/model sources but explicitly caution against generic application beyond their own
  tested sample/range (270-800K, to 60MPa) — real RP-1 is a variable petroleum-derived mixture,
  not a single fixed compound, so batch-to-batch variability (2-4% on thermal conductivity
  alone, `[Akhmedova-RP1]`) is real and irreducible.
- `[Quentmeyer-CR185257]`'s TBC/tungsten-reinforced/high-aspect-ratio comparisons (cited in
  `topics/12-materials-and-structures.md`) are single-test-article results, not a statistical
  dataset; its sulfur-corrosion finding above is a clean, standalone rig result.
- `[Armstrong-MarsISRU]` is 98 pages on Mars-ISRU (CO/O2) propellant cooling — its propellant
  chemistry and huge Mars-vacuum-optimized nozzle contours (area ratio 200-2000) have zero
  transfer value; only its generic supercritical-fluid correlation catalog and corroborating
  design constants (above) are cited here.

## Implications for engine_designer

- **`film_effectiveness_profile`'s decay-length constant now has two real candidate sources**
  (`[TN-D3836]`'s closed-form modified-Hatch-Papell correlation, `[SP-8124]`'s entrainment
  model) to ground it against, though neither is a drop-in replacement: `[TN-D3836]` needs
  Vg/Vc and entrainment-parameter inputs the tool doesn't currently compute, and `[SP-8124]`'s
  key augmentation factors are graph-only. Report-only — no code changed; a future feature
  could adapt either into a real Tier-1/2 decay law.
- **Film cooling as an overlay at two sites (2026-09-23)**: `[Huzel §4.4 p.98–99]`'s
  "film … alone or with regen" is now literal — film is not a section method but an overlay
  on any of them (`EngineDesign._film_phi`): the chamber curtain (face, or a convergent ring —
  the `[TP2862-LOXRP1]` injector-zoning result, `topics/06-cooling-and-heat-transfer.md`, is
  the passive-film analog) and a supersonic nozzle-extension slot anchored on the real F-1
  film start at eps 10 `[SP-8120]`, both fed post-jacket fuel at jacket-exit temperature. The
  `[EUCASS-2023 §4.2]` regen + 7 %-film case (peak wall 1124 → 948 K) is reproduced *in order
  of magnitude* by a LOX/RP-1 analog (−175 K, `validate.py::run_film_overlay_check`) — the
  near-exact match is coincidental, not a calibration. The decay law (`[SECA-HT §4.3]`: decay
  length is the hard part) and the product-combination rule remain Tier 3; **NASA SP-8124 is
  no longer missing — RESOLVED 2026-09-24** (see above), and a second independent closed-form
  correlation, `[TN-D3836]`, was found in the same batch. Hard-blocked material/method combos
  (`materials.Material.allowed_cooling_methods`) follow the method-selection table in
  `topics/06-cooling-and-heat-transfer.md`: ablatives never carry a regen jacket.
- **`regen_nozzle_end_eps` / `cooled_length_eps` cutoff pattern** now has independent
  real-hardware precedent from `[Marquardt-5981]`'s Design Study 1 (regen to 10:1, radiation
  skirt 10:1→40:1) in addition to the existing `[Sutton]` 6-10 range — no code change implied,
  just a second corroborating source for the same architecture (report-only).
  `[Marquardt-5981]` also names a **minimum practical regen coolant-passage dimension
  (0.062 in for a small hydrazine engine)** and a restart-engine **jacket-purge
  requirement** — neither has any counterpart in `cooling.py`/`mass_model.py` today (no
  minimum-channel-size check, no purge-volume/purge-path concept at all). Both are
  small-engine-scale findings and not urgent for the thrust range `engine_designer`
  typically targets, but worth flagging if a future feature adds real coolant-channel
  geometry sizing (see also `[Sutton §8.3]`'s channel-design treatment, flagged as unread in
  `topics/06-cooling-and-heat-transfer.md`).
- **Russian sandwich wall construction remains unmodeled** after this literature batch (see
  the dedicated paragraph above, now checked against 6 sources total) — `WALL_CONSTRUCTIONS`
  in `cooling.py` still only has `milled_channel`/`tube_wall`/`coax_shell`; a fourth
  "sandwich" type (many diffusion-bonded parallel channels between two face sheets, distinct
  from a single helical-wire double-wall channel) would need a Russian-specific source not
  yet acquired. Report-only — no code changed.
- **RP-1 coking limit now has real rate/onset-band data, not just a single-point temperature
  threshold** (`[Lewis-Deposits]`, `[TP2862-LOXRP1]`) — `cooling.py`'s RP-1 coking framing
  currently just uses the single `[SP-8087]` 850°F(728K) figure. If a future feature wants a
  fouling-resistance/service-life estimate rather than a binary coking-limit flag, the real
  400-600 µg/cm²·hr rate band and the non-monotonic (falls off above ~800K) shape are now
  available. Report-only — no code changed.
- **A real RP-1-coolant-property citation candidate for `thermo_tables.py`'s baked tables**:
  `[NISTIR6646-RP1]`/`[Huber-RP1RP2]`/`[Outcalt-RP1RP2]`/`[Akhmedova-RP1]` are all plausible
  real citations for whatever surrogate-mixture model underlies the RP-1 coolant property data
  — a future citation-upgrade pass could confirm which (if any) matches the actual Cantera/
  CoolProp implementation and cite it directly in `ASSUMPTIONS.md`. Report-only.
- **A new fuel-compatibility advisory candidate**: `materials.py`/RP-1-compatibility checks
  have no fuel-sulfur-spec awareness; `[Quentmeyer-CR185257]`'s real 50ppm-corrosion/1ppm-safe/
  gold-coating-mitigation data is a candidate for a future advisory distinct from the existing
  coking-temperature check. Report-only — no code changed.
