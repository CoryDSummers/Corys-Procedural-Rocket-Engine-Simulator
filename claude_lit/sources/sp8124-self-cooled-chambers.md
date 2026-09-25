# NASA SP-8124 — Liquid Rocket Engine Self-Cooled Combustion Chambers

## Identity

NASA Space Vehicle Design Criteria (Chemical Propulsion) monograph SP-8124, *Liquid Rocket
Engine Self-Cooled Combustion Chambers*, September 1977. Written by R.L. Ewen and H.M. Evensen
(Aerojet Liquid Rocket Company) under NASA Lewis Research Center direction (same design-criteria
program as `[SP-8087]`/`[SP-8107]`/`[SP-8109]`/`[SP-8048]`/`[SP-8081]`/`[SP-8120]`, all already in
`claude_lit`). `literature/NASA SP-8124 - Liquid Rocket Engine Self-Cooled Combustion
Chambers.pdf` (138 PDF leaves; printed-page numbering runs 11 pages behind the PDF leaf index —
printed p.N ≈ PDF leaf N+11, confirmed against the Introduction/§2 boundary). Tag: `[SP-8124]`.

**This closes a named literature gap.** `claude_lit/OPEN_QUESTIONS.md` had flagged this exact
monograph as wanted-but-unacquired since it is cited (Appendix B specifically) by
`[EUCASS-2023]`'s gaseous/liquid-film-cooling model — see that source's own note,
`sources/eucass2023-regen-cooling-design.md`, "Caveats" section. It is the parallel film-/
ablative-/radiation-cooling design-criteria monograph to `[SP-8087]`'s regen-cooling monograph.

## Character

Same two-parallel-section structure as every SP-8xxx monograph in this set: **§2 State of the
Art** (narrative, real-hardware/program history, pp.3–60) and **§3 Design Criteria and
Recommended Practices** (imperative "shall"/"should" statements, decimally numbered to match §2
1:1, pp.61–88). Two appendices follow with the only closed-form math in the document: **Appendix
A, Analytical Model for Gas Film Cooling** (pp.89–94) and **Appendix B, Analytical Model for
Liquid Film Cooling** (pp.95–100). Appendix C is a units-conversion table, Appendix D a glossary,
followed by 112 numbered references and the standard SP-8xxx monograph list.

"Self-cooled" is this monograph's own coined umbrella term for FIVE distinct wall-temperature-
control methods that all share one thing — **no fluid flow within the chamber wall supplied from
an external source** (i.e., not regenerative cooling) `[SP-8124 §1 p.1]`:

1. **Ablative** — fiber-reinforced resin liner pyrolyzes endothermically, releasing gas that acts
   as a transpiration coolant as it flows through the char to the surface.
2. **Radiation-cooled** — thin refractory-metal wall in thermal equilibrium, external radiation
   losses balance convective heating.
3. **Interegen (internally regenerative)** — heat is conducted *axially* (not radially, unlike
   true regen) from the throat forward to a liquid-film-coolant region near the injector, which
   absorbs it via sensible + latent heat.
4. **Heat sink** — chamber wall heat capacity limits surface temperature for a short duration;
   treated jointly with interegen since flight heat-sink designs are physically near-identical to
   monolithic interegen chambers (both typically beryllium).
5. **Adiabatic wall** — no self-cooling at all; wall runs at the local adiabatic wall temperature
   set by combustion products + injector film cooling / peripheral mixture-ratio control.

A sixth, closing section, **§2.5/§3.5 Heat Transfer to the Chamber Wall**, is common to all five
types: Stanton-number evaluation (laminarization/reverse-transition), film-cooling analysis, and
film-coolant injection technique — this is where the Appendix A/B analytical models are invoked.

**Envelope**: self-cooled chambers have been used primarily at **Pc < 150 psi and thrust <
20,000 lbf** `[SP-8124 §2 p.3]` — this monograph is explicitly a *small-engine* design-criteria
source (attitude-control thrusters, upper-stage/lunar-module RCS, one or two larger examples up
to ~25,000 lbf), not a booster-engine source like `[SP-8087]`/`[SP-8120]`.

## This note's extraction scope

**Fully read**: §2.5/§3.5 Heat Transfer to the Chamber Wall (both Stanton-number and film-cooling
analysis, pp.51–60/82–88) and **Appendix A + Appendix B in full** (the two analytical models —
this is the primary target of the acquisition, since it's what `[EUCASS-2023]` cites). Also fully
read: all of **§3 Design Criteria** for all five chamber types (§3.1 Ablative pp.61–69, §3.2
Radiation-Cooled pp.69–73, §3.3 Interegen/Heat-Sink pp.73–79, §3.4 Adiabatic-Wall pp.79–81) — the
imperative "shall"/"should" criteria themselves, not just the narrative behind them.

**Read (State-of-the-Art narrative, real-hardware/program detail)**: §2.1.1 Ablative liner
material selection and surface regression (pp.6–11), §2.2 Radiation-Cooled Chambers thermal
design/materials/attachments in full (pp.24–32), §2.3 Interegen and Heat-Sink Chambers in full
(pp.33–42), §2.4 Adiabatic-Wall Chambers in full (pp.43–50).

**Skimmed only** (real-engine survey Tables I/IV/VI/VIII, "basic features of typical operational
engines" — text-extracted as scrambled/column-mangled OCR, not independently re-rendered as
images; their headline numbers — thrust/Pc ranges, propellants, materials — were recovered from
the surrounding narrative prose instead, which restates them): §2.1.2/§2.1.3 Ablative structural
design and fabrication detail beyond what's needed to corroborate §3.1's criteria (pp.14–23,
mostly figure captions/attachment-joint evolution narratives); Tables II/III/V/VII/IX (material
property tables — silica/phenolic prepreg properties, refractory-metal mechanical properties,
bulk-graphite properties, fiber-reinforced-graphite-composite properties) noted by cross-material
comparison in the narrative but not transcribed cell-by-cell.

**Not read**: Appendix C (unit conversions), Appendix D (glossary), References (112 entries, not
chased), the closing "NASA Space Vehicle Design Criteria Monographs Issued to Date" list.

## Key results — §2.5/§3.5 and Appendices A/B: Heat transfer and film cooling (the primary target)

### Convective heat-flux formulation and Stanton-number evaluation

**Baseline heat-flux equation** `[SP-8124 §2.5 p.51; §3.5 eq.6 p.82]`: `q_c = h_g(T_aw − T_w)`,
with the criteria-section (enthalpy-based) form for use with dissociating/high-energy propellants
mandatory above ~5500°R combustion temperature: `q_c = ρ·u_e·St·(H_aw − H_w)` — **enthalpy
difference replaces `Cp·ΔT` whenever chemical reactions in the boundary layer matter**
(explicitly flagged as important for O₂/H₂, F₂/H₂, FLOX/methane). A **Lewis-number correction**
is required whenever Le is not near unity: multiply the computed flux by `1 + (Le−1)·Σ[Hⱼ°(Cⱼ,aw
− Cⱼ,w)]/(H_aw − H_w)` `[§3.5 p.83]` — a real, quotable non-unity-Lewis-number correction with no
counterpart elsewhere in this reference set (`[SP-8124]`'s own narrative notes this correction "is
ignored or assumed small in present design practice," i.e. it's a real criterion routinely
skipped even by NASA-era designers).

**Mass-addition correction** `[SP-8124 §3.5 eq.7 p.83]`: with transpiration/reactive-wall mass
addition, `q_w = q_c − (ρv)_w·(H_w − H_c)` — the wall heat flux is NOT equal to the boundary-layer
convective flux when the wall itself is adding mass to the boundary layer (ablative/transpiration
case specifically); part of the convective flux instead goes to raising the injected mass's own
enthalpy.

**Stanton-number correlation, criteria form** `[SP-8124 §3.5.1 eq.8-9 p.83-84]`: `St = Cg·Re⁻⁰·²·
Pr⁻⁰·⁶` (turbulent, variable coefficient Cg = Cg(x) — flat constant-coefficient Bartz, `Cg=0.026`,
is explicitly a **design-criteria non-recommendation**: "typically underpredicts... in the
cylindrical section... but overpredicts in the throat region"); `St = 0.318·Re⁻⁰·⁸·Pr⁻⁰·⁶`
(laminarized regime). This is the SAME critique of the flat-coefficient Bartz approach that
motivates `engine_designer`'s own `BARTZ_ABS_FLUX_CALIBRATION` per-propellant-class calibration —
independent 1977 NASA corroboration that a single Bartz constant is known-wrong across the
converging section, not just at the throat.

**Laminarization/reverse-transition — a real, dimensioned design table** `[SP-8124 §3.5.1
p.84-85]`: below a chamber-pressure×thrust product `Pc·F < 200,000 lbf²/in²`, boundary-layer
reverse transition and laminarization (Stanton number reduced by a factor of 2–3 vs. turbulent at
the same Reynolds number) become a real design concern — **this threshold sits inside the
thrust/Pc envelope most self-cooled (small) chambers actually occupy**, unlike large
regen-cooled boosters. Real dimensioned Reynolds-number table (properties at Eckert reference
temperature) for laminarized-vs-turbulent limits by convergence angle/contraction ratio at the
throat and just upstream:

| Location | Convergence angle | Contraction ratio | Re (laminarized limit) | Re (turbulent limit) |
|---|---|---|---|---|
| Throat | 30° | 7.75 | 0.5×10⁶ | 1.0×10⁶ |
| Throat | 45° | 9.76 | 0.9×10⁶ | 2.1×10⁶ |
| Throat | 60° | 4.29 | 0.9×10⁶ | 2.1×10⁶ |
| Upstream (ε=1.23–1.34) | 30° | 7.75 | 0.75×10⁶ | 1.5×10⁶ |
| Upstream | 60° | 4.29 | 1.3×10⁶ | 2.6×10⁶ |

A real closed-form acceleration parameter is given for checking whether a specific contour
laminarizes `[§2.5.1 eq.4-5]`: `K = (μ/(ρ_e·u_e²))·[u_e·du/dx + 0.4·(u_e/r)·dr/dx] ≥ 3.3×10⁻⁶`
triggers laminarization if sustained ~100–200 momentum thicknesses; equivalently for
one-dimensional isentropic flow, `K·Re = 2/M²·[1−1/ε²]^0.4/(sinβ)` where β is the local
wall-tangent angle and ε the local area ratio — large convergence angles, large contraction
ratios, and small throat radii of curvature all promote laminarization.

### The film-cooling analytical models — Appendix A (gas) and Appendix B (liquid)

**This is the closed-form content `[EUCASS-2023]` cites** (its "gaseous-film mixing... for the
post-vaporization regime" cites this monograph's Appendix B, which itself contains BOTH the
liquid-film-length treatment and a downstream gas-mixing-layer treatment that reuses Appendix A's
framework — confirmed against `[EUCASS-2023]`'s own description). **Important nuance for anyone
expecting a single portable equation**: this is NOT a simple closed-form exponential-decay
effectiveness-vs-distance formula (unlike, e.g., `cooling.py`'s own
`film_effectiveness_profile`'s `eta_f0·exp(−x/(2.5·D))`-style Tier-3 model). It is an
**entrainment-based integral model with two empirical graphical correlations** (Figures A-2/B-1)
at its core, requiring evaluation along the actual chamber contour:

**Gas film cooling — Appendix A** `[SP-8124 App.A pp.89-92]`:
1. Entrainment flow ratio (closed-form integral): `W_E/W_c = (W/W_c)·[(2·r_i/s_i)·∫f·ψ_m(x)·dx −
   1]`, where `f = f(u_c/u_e)` is a **reference entrainment fraction read from a graph** (Fig.
   A-1), `ψ_m(x)` is an **empirical entrainment-fraction multiplier** (also graphical, Fig. 17 in
   the main text — see design-criteria recommended values below), `r_i`/`s_i` are the injection
   radius/mixing-layer height, and the integral runs over "effective contour distance" `x`.
2. Effectiveness: `η = f(W_E/W_c)`, **read from Figure A-2** ("Film-coolant effectiveness as a
   function of entrainment flow ratio") — i.e. the effectiveness-vs-entrainment relationship
   itself is an empirical CURVE, not a closed algebraic function.
3. Adiabatic wall enthalpy from effectiveness: `H_aw = H_o,e − η(H_o,e − H_c) −
   (1−Pr_w^(1/3))(H_o,e − H_e)/(1+(MR)_e)`, with a **reactive** model (accounting for combustion
   in the mixing layer, mixture-ratio-at-wall derived from η) and a **non-reactive** model
   (simple Cp-weighted mixing) both given as alternatives.

**Liquid film cooling — Appendix B** `[SP-8124 App.B pp.95-99]` — this DOES contain a genuine
closed-form equation for the liquid-covered length, unlike the gas-film effectiveness step:
1. **Liquid film length**: `L = (1/Λ)·ln[1 + Λ·W_c/(V·(ρu)_av/144·St·B·a)]`, where `Λ = Λ(X_e)`
   is a **liquid entrainment parameter read from Figure B-1**, `X_e = δ(ρ_e/g)^0.5·u_e·
   (T_e/T_if)^0.25/σ` is the **entrainment correlation parameter** (a genuine closed-form
   algebraic quantity — density, velocity, temperature ratio, surface tension), `δ` is an
   **empirical entrainment augmentation factor** (see design values below), `B` is a
   heat-transfer/blowing parameter derived from `St`, wall heat flux, and vaporization enthalpy,
   and `a = a(X_e, X_r)` is a **heat-transfer augmentation factor for liquid-surface roughness**
   (also read from Fig. B-1). The liquid-film interface temperature `T_if` is the saturation
   temperature at the local vapor partial pressure `p_v = P_ch/[(MW)_c/(B·(MW)_e) + 1]`.
2. **Downstream of the liquid film**: a mixing-layer entrainment model structurally identical to
   Appendix A's, with its own empirical entrainment fraction `ψ_L` (similar role to `ψ_r`),
   its own shape factor `θ` for the mixing-layer profile (two piecewise-linear regimes depending
   on whether `W_E` exceeds `(W_E)_L + 0.6·W_c`), and (for monopropellant coolants specifically) a
   **first-order thermal-decomposition model**: `f_v = exp(−λ·τ)` (fraction of coolant remaining
   as vapor, undecomposed), where `τ` is the core-flow transit time and `λ` is an **empirical
   decomposition rate constant** — a genuinely new closed-form monopropellant-vapor-decay
   treatment absent from every other cooling source in this reference set.

**Design-criteria recommended EMPIRICAL VALUES for the above models** `[SP-8124 §3.5.2 p.86-87]`
(the numbers that make the models usable without independent test data — Tier-3-equivalent,
NASA-recommended defaults for a specific real-hardware precedent, hydrogen film cooling):
- Entrainment-fraction multiplier `ψ_m`: **3 to 4 at the coolant injection point**, decaying
  **linearly with axial distance in the convergent section to ~1.75 at the throat**, then
  further decaying downstream per Figure 17 (a real digitizable curve — normalized multiplier vs.
  area ratio out to ε≈28, asymptoting toward ~0.3–0.5 by ε≈16-28).
- Liquid-film entrainment fraction: `ψ_L = 0.025 to 0.06` (for a uniform-entrainment assumption,
  `ψ_m=1`), from rocket-firing data analysis.
- Liquid-injection entrainment augmentation factor `δ`: **1.0 to 1.6** for orifice injection
  parallel to the core flow; **as low as 0.4 for swirl injection** — swirl injection reduces
  entrainment loss (consistent with `§2.5.3`'s narrative finding that circumferential/swirl
  velocity components reduce coolant entrainment via centrifugal effects holding the coolant on
  the wall).
- Monopropellant (MMH) decomposition: critical wall temperature for onset **~550°F**;
  decomposition rate constant `λ ≈ 3000 sec⁻¹`.
- Velocity-ratio optimum (design target, both narrative and criteria) `[§2.5.3 p.59-60; §3.5.3
  p.88]`: **gaseous** film-coolant/core-stream velocity ratio for MINIMUM coolant flow at fixed
  effectiveness = **1.0 to 1.05** (a *broader* maximum-effectiveness plateau exists at 1.15–1.5,
  but that isn't the flow-minimizing point); the criteria section gives a slightly different
  practical range, **0.9 to 1.15**, for slot-height sizing. Deviating from this range sharply
  increases required coolant flow (Figure 14: up to ~30% flow penalty by ratio 0.5 or 1.5).

### Film coolant injection — real, dimensioned design criteria

`[SP-8124 §2.5.3 p.58-59; §3.5.3 p.88]`: minimum practical liquid-film orifice diameter **~0.015
in.** (0.010 in. demonstrated but "difficult to machine accurately... susceptible to plugging"),
**maximum center-to-center orifice spacing 0.25–0.30 in.** for uniform circumferential coverage;
where that spacing can't be met with practical orifice sizes, use swirl (unless the injector is
baffled) or impinging-pair tangential-fan patterns instead. **Liquid film impingement angle: 25°
to 35°** (below 28° leaves uncooled areas near the injector per transparent-chamber visual
tests; above 35° causes instability/droplet entrainment loss) — the design-criteria section
narrows this slightly to **25° to 35° for axially-injected liquid film**. **Gaseous film coolant**
should be injected parallel to the wall through slots, with rib thickness between slots minimized
consistent with structural needs.

## Key results — §3.1/§2.1: Ablative chambers (design criteria)

**Surface temperature limits by material** `[SP-8124 §3.1.1.1.1 p.61]`: **silica/quartz liners
limited to ~3000°F** surface temperature in general; up to **~3400°F** permitted only under
special circumstances (Pc < 125 psi, short firing duration, nonstreaking injectors, subject to
experimental verification) — **above Pc > 300 psi, surface temperature is no longer the limiting
condition** (gas shear becomes limiting instead) and a **throat insert is required**. Water-vapor
content is the key liner-compatibility driver: **silica or quartz reinforcement required whenever
combustion products exceed 33% water vapor by content**; carbon/graphite reinforcement must not
be used without an effective non-oxidizing boundary layer (fuel-film or barrier cooling).

**Throat insert material selection by temperature** `[SP-8124 §3.1.1.2 p.63-64]`: **KT silicon
carbide or JTA graphite composite** for wall temps ≤3600°F in water-vapor-rich combustion products
(SiC cracks more, JTA erodes slightly more; both restricted to engines **<1000 lbf thrust**);
**molybdenum with an oxidation-resistant silicide coating** for larger engines; **pyrolytic
graphite (PG) washers** for >3600°F, provided a fuel-rich boundary zone can be generated. Real
throat-insert geometry criteria: thickness-to-ID ratio **0.2 to 0.3**, length-to-thickness ratio
**≤6**, smallest OD at the aft end (so a radial crack can't eject the insert), external support
sleeve of graphite (CTE-matched, slightly lower than the insert) or tungsten (with a silicone-
rubber elastomeric cushion at the interface).

**Char-depth safety factor** `[SP-8124 §3.1.1.1.3 p.62]`: a **1.25 safety factor on predicted char
depth** to account for local injector characteristics and material-property uncertainty (unless
explicitly modeled elsewhere) — a real, quotable design margin for any ablative-liner sizing.

**Structural-shell temperature limits** `[SP-8124 §3.1.1.3.1 p.64]`: fiberglass/epoxy 300°F,
fiberglass/phenolic 500°F, fiberglass/polyimide 700°F, aluminum 350°F, **titanium 800°F,
stainless steel 800°F**.

**Fiber orientation by zone** `[SP-8124 §3.1.1.1.4 p.63]`: chamber 6°–60° to the wall (30°/45°
recommended, low angle for low radial conductivity/axial expansion); throat 30°–60° (45° typical
when the insert extends into the divergent section); divergent nozzle 15°–45° to the gas-side
wall.

**Structural factors of safety** `[SP-8124 §3.1.2.2.1 p.66]`: metal structural shells **1.25 to
1.50**; fiberglass structural shells **1.5 to 1.8** (higher because fabrication-quality-dependent
properties are less well characterized than metals').

**Fabrication debulking criteria** `[SP-8124 §3.1.3.1 p.68]`: tape-wrapped-on-male-mandrel
components need **≥85% debulking** (of final cured density); warp-cut tape needs **≥90%**;
matched-metal-die-molded precut fabric debulked in steps of **≤2 in. thickness per step**.

**Real erosion/regression narrative anchors** `[SP-8124 §2.1.1.1 pp.17-18]`: magnesium-hydroxide/
phenolic liners at 100 psi/1000 lbf (N₂O₄/A-50, MR 1.6) could not sustain firings beyond **100
seconds** due to excessive throat erosion; asbestos/phenolic shrinks significantly perpendicular
to laminate on cooldown (unsuitable for restart-capable engines, though it works as a Titan-II
nozzle-extension liner where cracks/delaminations are tolerated).

## Key results — §3.2/§2.2: Radiation-cooled chambers (design criteria)

**Materials** `[SP-8124 §3.2.1.1 p.69; §2.2 p.24]`: **columbium alloys (C-103 named specifically)
are the recommended wall material** — the 90Ta-10W alloy is NOT recommended (much denser, and its
high-temperature strength can't be used because no coating exists for it yet); molybdenum and its
alloys are NOT recommended (structural/embrittlement problems, discussed below). **Wall
temperature must exceed ~2200°F for radiation losses to balance convective heating from typical
combustion products** `[§2.2 p.24]` — the basic constraint that drives the whole materials
selection (only refractory metals/alloys have adequate high-temperature strength at that
temperature).

**Coating temperature limits — a real, dimensioned pair of numbers** `[SP-8124 §3.2.1.2.1 p.70]`:
**silicide coatings**: max **2800°F for 1 hour**, up to **3100°F for 10 minutes**; **aluminide
coatings**: max **2400°F, absolute ceiling 2800°F**. Silicides recommended for earth-storable
propellants (R512E named), self-healing via new SiO₂ film formation each firing; **diffusion-
bonded aluminides recommended specifically for fluorine/halogen-fluoride oxidizers**. **Coating
thickness must not exceed 8 mils** `[§3.2.1.2.2 p.71]` (too thick → spalling/cracking under
thermal cycling); applied by slurry+vacuum-diffusion or pack cementation (plasma spray NOT
recommended for small-chamber interiors — too porous, no metallic bond).

**Real emissivity numbers** `[SP-8124 §2.2.1.2 p.38-39; §2.2.1.3 p.39]`: silicide/aluminide
coatings (the same ones used internally for oxidation resistance) give external emissivity
**0.75 to 0.85**; bare refractory-metal surfaces have low native emissivity **0.2 to 0.4**;
**V-grooving raised emittance to 0.8** on an SCb-291 chamber without a coating. Real coating
sublimation-rate data in vacuum: **0.8%/hr by weight at 2600°F, 4.0%/hr at 3000°F** (10⁻⁵ mmHg) —
negligible below 2400°F ("virtually unlimited life"), but this bounds practical operating
temperature near 2800°F for anything but short-duration duty cycles. A more advanced (not yet
state-of-the-art at time of writing) **80Hf-20Ta cladding on 90Ta-10W** was evaluated for up to
**3800°F** with earth-storable oxidizers.

**Embrittlement/ductility real-hardware findings** `[SP-8124 §2.2.1.1 p.37; §2.2.2.1 pp.38-39]`:
SCb-291 and C-129Y columbium alloys (both containing ~10% tungsten) suffered brittle coating-
induced failures in a real four-coating/three-substrate test program; **C-103 (negligible
tungsten) did not**. Molybdenum's brittle-to-ductile transition temperature is raised to
**~70°F** by recrystallization (occurring below 2500°F in all refractory metals/alloys), meaning
a molybdenum chamber's normal operating range straddles the transition zone — **molybdenum
chambers have failed in pulsed operation from start-transient pressure spikes exceeding nominal
Pc by more than an order of magnitude**, striking brittle-fracture-initiated cracks. **90Ta-10W
and columbium have the lowest brittle-to-ductile transition temperatures** of the surveyed
materials and best resist repeated altitude-ignition pressure-spike energy absorption + thermal
shock. Unalloyed tungsten is explicitly NOT a suitable wall material despite good high-temp
strength/conductivity, due to its high ductile-to-brittle transition temperature.

**Injector/chamber attachment thermal-isolation criterion** `[SP-8124 §3.2.2.2.1 p.72]`: cool the
chamber/injector interface **below 350°F during operation, below 500°F after shutdown** (via film/
barrier cooling), OR make the injector of the same high-temperature material with manifolds
located remote from the injector face, OR use a thermal barrier with the seal located far forward
and a minimized heat-conduction path through bolts (with bolt heads shielded from wall radiation).

**Real weld-joint reinforcement number** `[SP-8124 §3.2.2.2.3 p.73]`: **increase chamber-wall
thickness 50% at a weld joint**, over a distance of **2.5× the greater wall thickness** — a real,
dimensioned local-thickening rule for welded columbium/tantalum-alloy attachments.

## Key results — §3.3/§2.3: Interegen and heat-sink chambers (design criteria)

**Material selection** `[SP-8124 §3.3.2.1 p.76]`: **beryllium** recommended for N₂O₄/hydrazine-
type propellants with reduced wall temperatures or very limited thermal cycling (real operating
window: **1800°F for beryllium** without restart requirements, **1100°F for copper** chambers).
**Copper / bimetallic copper-with-Inconel-liner** recommended instead where duty cycle/thermal-
gradient severity risks beryllium low-cycle-fatigue failure. Real beryllium-alloy elongation
numbers: **3.0% hoop elongation readily obtainable at room temperature, up to 4.5% with special
processing**; recommended **Fe/(Al+Si) impurity ratio ≈ 1.4** for good high-temperature strength
in hot-pressed beryllium.

**Hot-restart temperature limits — real demonstrated numbers** `[SP-8124 §3.3.1.3 p.77; §2.3.1.3
p.42]`: demonstrated successful hot-restart firings up to **900°F initial wall temp with MMH**,
**700°F with A-50 (N₂O₄/hydrazine blend)**. Heated-strip lab tests (not fully representative of
real chamber cooldown) showed no detonation up to 1000°F for B2H6, 800–900°F for MHF-3/MMH.

**Real design-practice anchor — film-fraction and c\* efficiency** `[SP-8124 §2.3.1.1 p.46-47]`:
most interegen designs to date used **30–40% of the fuel flow (about 15% of total propellant
flow) as film coolant** — justified specifically at the low chamber pressures typical of this
architecture, where core-flow-burned-film-coolant can still deliver good performance. One real
cited result: **94% c\* efficiency with ~38% of fuel flow used as film coolant** — a real,
quotable design tradeoff point between film-cooling fraction and combustion efficiency, directly
comparable in kind to `engine_designer`'s own film-cooling-vs-performance framing.

**Real radiation-cooled-extension-start area ratio for interegen designs** `[SP-8124 §2.3.1.2
p.49]`: radiation-cooled nozzle extensions on interegen chambers typically start at **area ratio
3 to 10** — a second real precedent (alongside `[SP-8120]`'s F-1 film-cooled-extension-start at
ε=10) for where an active-cooling-to-passive-cooling transition happens on a real chamber,
though for a different transition type (interegen-to-radiation, not regen-to-film).

**Low-cycle fatigue design rule** `[SP-8124 §3.3.2.2.1 p.77]`: in the limiting single-restart-
after-complete-cooldown case (full strain reversal), **operating thermal strain must stay below
the worst (hoop or longitudinal) room-temperature elongation** of the material — i.e. size the
allowable thermal strain range directly against the material's own measured ductility, not an
arbitrary margin.

## Key results — §3.4/§2.4: Adiabatic-wall chambers (design criteria)

Scope explicitly limited to **fluorinated-oxidizer engines** (CTF, FLOX, F₂) — "conventional
chambers made of coated refractory alloy are no longer adequate, even with film or barrier
cooling" for these propellants at high combustion temperature/Pc; all cited programs are R&D, no
flight-proven adiabatic-wall design existed at time of writing `[SP-8124 §2.4 p.44]`.

**Materials — pyrolytic graphite vs. fiber-reinforced graphite composite** `[SP-8124 §3.4.1.1
p.79-80; §2.4.1.1 p.45-46]`: **pyrolytic graphite (PG) surface regression is about one order of
magnitude LESS than conventional bulk graphites** in fluorinated-oxidizer service — PG coatings
(≤0.025 in. thick, on a smooth substrate, thermal-expansion-matched) are very effective at
minimizing surface regression. Free-standing PG limited to simple shapes, large transition radii
(≥0.5 in.), small expansion ratios (sea level only), Pc ≤100 psi, and wall-thickness/radius-of-
curvature ratio ≤0.06 — beyond that, fiber-reinforced graphite composite (carbon/carbon) is
required. Real interlaminar-shear/block-tensile numbers `[§2.4.2.1 p.48]`: interlaminar shear
strength **~600 to 1800 psi**, block-tensile (normal to reinforcement plane) about **half of
that** — the chief structural weakness of this material class, driving delamination risk.

**Wall-material regression/corrosion selection method** `[SP-8124 §3.4.1.1 p.79]`: use a plot of
carbon corrosion characteristics vs. propellant mixture ratio (Fig. 11, CTF-oxidizer example at
6000°F/500 psi) to determine whether the design will see material regression or carbon buildup;
mitigate regression via wall-mixture-ratio control or a PG coating; **no corrective action is
recommended if carbon buildup is predicted** other than changing the fuel or boundary-layer
mixture-ratio control — a real, honestly-stated gap in this monograph's own guidance.

**Real fiber-orientation/fabrication criterion** `[SP-8124 §2.4.2.1 p.50-51]`: small angle
(5°-10° to the inner surface) considered best for adiabatic-wall chambers, though tape-wrapped
components often need 30°-45° immediately downstream of the throat for adequate shear area.
Fibrous-graphite-composite elongation is **~0.5% or less** — real bending-moment-induced fracture
precedent exists where an attachment design mechanically restrained the forward chamber liner in
hoop while the rest was free to expand, fracturing the chamber.

## Design method

Unlike `[Huzel]`/`[Sutton]`, this monograph gives real design *criteria* (imperative
"shall"/"should" thresholds) and real-hardware precedent rather than closed-form sizing equations
— EXCEPT in §2.5/§3.5 and Appendices A/B, which are the one place in the document with genuine
mathematical models (Stanton-number correlations, entrainment-based film-cooling models). Even
there, the practically usable numbers (entrainment-fraction multiplier `ψ_m`, liquid-injection
augmentation factor `δ`, effectiveness-vs-entrainment-ratio relationship) are EMPIRICAL — read off
graphs (Figures A-1, A-2, B-1, 14, 17) fitted to specific hydrogen-film-cooling or MMH/A-50
liquid-film rocket-firing test data, not derived from first principles. Treat this monograph
exactly as `[SP-8120]`'s own note treats itself: real design thresholds and real-hardware failure/
fix precedent for four passive-cooling architectures, PLUS one genuinely reusable
(if graph-dependent) analytical film-cooling framework for the fifth (common-to-all) heat-transfer
section.

## Section map

| Subject | §2 (State of Art) | §3 (Design Criteria) | This note's coverage |
|---|---|---|---|
| 2.1/3.1 Ablative Chambers | pp.3-23 | pp.61-69 | §2.1.1 (Liner) read; §2.1.2/2.1.3 (structural/fab detail) skimmed; §3.1 fully read |
| 2.2/3.2 Radiation-Cooled Chambers | pp.24-32 | pp.69-73 | Fully read, both sections |
| 2.3/3.3 Interegen and Heat-Sink Chambers | pp.33-42 | pp.73-79 | Fully read, both sections |
| 2.4/3.4 Adiabatic-Wall Chambers | pp.43-50 | pp.79-81 | Fully read, both sections |
| 2.5/3.5 Heat Transfer to the Chamber Wall | pp.51-60 | pp.82-88 | Fully read, both sections — the primary extraction target |
| Appendix A — Analytical Model for Gas Film Cooling | pp.89-94 | — | Fully read (equations + Figs. A-1/A-2 referenced, not independently re-rendered as images) |
| Appendix B — Analytical Model for Liquid Film Cooling | pp.95-100 | — | Fully read (equations + Fig. B-1 referenced, not independently re-rendered as images) |
| Appendix C — Unit Conversions | p.101 | — | Not read (standard conversion factors) |
| Appendix D — Glossary | pp.103-112 | — | Not read (terminology only; referenced obliquely via table footnotes "Identified in Appendix D") |
| References (112 entries) | pp.113-120 | — | Not read/chased; several (refs. 76, 81, 103, 107) are the actual origin of the Appendix A/B entrainment models and could be worth acquiring directly if the graphical correlations (Figs. A-1/A-2/B-1) are ever needed as digitized curves rather than named ranges |
| Tables I/IV/VI/VIII (real-engine surveys, ablative/radiation/interegen-heat-sink/adiabatic-wall) | — | — | Skimmed only — OCR text-extraction scrambled the columns; headline numbers recovered from surrounding narrative instead (see Key Results sections above) |
| Tables II/III/V/VII/IX (material property tables) | — | — | Not transcribed cell-by-cell; qualitative comparisons only (e.g. PG vs. bulk graphite regression rate, interlaminar shear range) captured from narrative |

## Caveats

- **Small-engine scope**: this monograph's own stated envelope is Pc < 150 psi, thrust < 20,000
  lbf `[§2 p.3]` — nearly the opposite end of the design space from `[SP-8087]`/`[SP-8120]`'s
  large regen-cooled boosters. Any `engine_designer` engine outside that envelope (which is most
  of the tool's real-engine validation corpus) is extrapolating this source's design criteria,
  not applying them within their demonstrated range — flag this explicitly if any of the above
  numbers (e.g. the 2200°F radiation-cooling threshold, the ψ_m entrainment-multiplier defaults)
  are ever applied to a large staged-combustion or gas-generator engine design.
- **The film-cooling models are NOT simple closed-form equations** — this is the single most
  important caveat for anyone hoping to directly port SP-8124's film-cooling treatment into
  `cooling.py`'s existing `film_effectiveness_profile`/`nozzle_film_effectiveness_profile`
  functions. The effectiveness-vs-entrainment-ratio relationship (Fig. A-2) and the liquid
  entrainment parameter Λ(Xe) (Fig. B-1) are both EMPIRICAL CURVES, not algebraic functions — to
  use this model as-designed would require either digitizing those figures (not done this pass —
  they were not independently re-rendered as images) or substituting a curve-fit approximation.
  The entrainment-fraction multiplier ψ_m(x) (Fig. 17) IS captured as real numeric recommended
  values above (3-4 at injection, decaying to 1.75 at throat) and is the most directly portable
  single number if a length-decay anchor point is wanted.
- **The recommended empirical constants (ψ_m, δ, ψ_L) are anchored to ONE real precedent each** —
  hydrogen film cooling (`[SP-8124 ref. 81]`, an H₂/O₂-firing dataset) for ψ_m, and orifice/swirl
  MMH-type liquid injection (`[SP-8124 ref. 51]`) for δ. The monograph itself is explicit that
  "considerable effort will be necessary to characterize the effects of flow turning and
  acceleration, coolant injection from configurations other than continuous slots, and core
  injection and combustion" — i.e. even NASA's own 1977 assessment treats these as
  propellant/configuration-specific numbers, not universal constants.
- **No milled-channel/tube-wall/coax-shell regen-cooling content whatsoever** — this monograph is
  scoped to explicitly exclude fluid-supplied-from-an-external-source cooling by its own
  definition (§1). `[SP-8087]` remains the sole regen-jacket structural/hydraulic design-criteria
  source in this reference set; SP-8124 is purely complementary (film/ablative/radiation/
  interegen/adiabatic), not overlapping.
- **Tables I/IV/VI/VIII (real-engine surveys) were not independently re-rendered as images** —
  their exact per-engine numeric cells (individual thrust/Pc/propellant/material entries for each
  named engine) were not transcribed; only the aggregate ranges and specific numbers repeated in
  the surrounding narrative prose are captured here. If a future session wants a specific named
  engine's exact Table I/IV/VI/VIII row (e.g. the Apollo LEM RCS engine's precise Pc, or the
  Viking Orbiter '75 interegen chamber's exact thrust), it should re-render those table pages
  (PDF leaves 15, 36, 46, 56) as images rather than relying on `get_text()`.
- **1977 vintage, pre-dates modern refractory-metal coating/additive-manufacturing developments**
  — like `[SP-8120]`'s own caveat, the real-hardware failure modes and material selection logic
  (embrittlement, recrystallization brittleness, char-depth safety factors) are geometry/
  chemistry-driven and remain applicable, but specific coating systems (R512E, Durak KA, R508C)
  and alloy availability (SCb-291, C-129Y) reflect late-1960s/1970s aerospace-materials practice,
  not current commercial availability.
- **OCR quality is mixed**: clean in the main narrative and Design Criteria sections, but the
  survey tables (Tables I/IV/VI/VIII) and several equation-heavy Appendix A/B pages render with
  scrambled column order, dropped/garbled Greek-letter subscripts (e.g. "ψ_m" appears as
  "l_r@m"/"_rn"/"if_m" across different OCR passes; "δ" and "Λ" are similarly inconsistent), and
  occasional digit substitution (e.g. "8" for a Greek delta symbol context, "il_5" for numeric
  ranges). All quantitative claims above were cross-checked against at least one repeated
  restatement in prose (the Design Criteria section usually restates the State-of-the-Art
  section's key number in imperative form) before being included; the exact symbolic notation of
  the Appendix A/B equations should be treated as a best-effort reconstruction of the underlying
  physical relationship, not a verbatim transcription — re-render pages 100-111 (PDF leaf
  numbering) as images before using any equation from this note in a load-bearing calculation.
