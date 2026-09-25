# 05 — Injectors

## Scope

Injector types, the pressure-drop / stiffness rule, discharge coefficients, impingement
geometry, atomization, and throttling. Feeds `engine_designer/physics/injectors.py` and the
throttle-stability checks in `throttle.py`.

## Key relations

**Injection hydraulics** `[Huzel eq. 4-39/4-40 p.127–128]`, `[Sutton eq. 8-1/8-2/8-5]`:

    V   = ṁ / (A·ρ)                       injection velocity
    Q   = Cd·A·√(2·Δp/ρ)                  volume flow
    ṁ   = Cd·A·√(2·ρ·Δp)
    Δpi = ρ·V² / (2·g·Cd²)                injection pressure drop (Huzel form)

**β angle** (resultant momentum vector vs chamber axis) `[Huzel eq. 4-41 p.128]`,
`[Sutton eq. 8-6/8-7]`: from conservation of momentum over the impinging pair. Positive β
points toward the wall. For an axial resultant, `ṁ1·V1·sin γ1 = ṁ2·V2·sin γ2`.

**Injection momentum ratio** `[Huzel eq. 4-42]`: `Rm = (ṁ_ox·V_ox) / (ṁ_fuel·V_fuel)` —
a design parameter for predicting stability and performance.

**Water-test MR conversion** `[Sutton eq. 8-4]`:
`MR_actual = MR_water · √(ρ_ox/ρ_fuel) · √(Δp_ox/Δp_fuel)`.

## Empirical correlations & typical values

**Injector pressure drop** — the central number:
- `[Huzel §4.5 p.128]`: "the rule-of-thumb design value for injector pressure drop varies
  from **15 to 20 percent of the chamber-nozzle stagnation pressure**." Low Δp is good for
  feed-system weight; the *minimum* is set by combustion-stability considerations.
- `[Sutton §8.1]`: low Δp minimises feed weight / pump power; high Δp is used "often to
  increase the rocket's resistance to combustion instability and enhance atomization."
- Real engines `[Sutton Table 8-1]` (Δp_ox / Δp_fuel, psi, and vs Pc where Pc is known):

  | Engine | Δp ox | Δp fuel | injector type | Δp/Pc (approx) |
  |---|---|---|---|---|
  | RL10B-2 (expander) | 100 | 54 | concentric annular swirl + resonator | ~0.15 |
  | LE-7 (staged comb, Pc ~1917) | 704 | 154 | coax hollow post/sleeve + baffle + cavities | 0.08–0.37 |
  | R-4D-class RCS (Pc ~100) | 50 | 50 | drilled holes | ~0.5 (small thruster) |
  | RS-27 (GG, LOX/RP-1) | 156 | 140 | flat plate drilled rings + baffle | ~0.2 |
  | AJ-10 (pressure-fed, Pc 125) | 40 | 40 | showerhead outer + triplets/doublets + resonator | ~0.32 |

  Pattern: **~0.15–0.25 for normal medium/large engines; 0.3–0.5 for small thrusters and
  staged-combustion** (which needs a stiff injector because the turbine is in series).

**Discharge coefficient Cd** `[Sutton Table 8-2 p.279]`, `[Huzel §4.5 p.128]` ("ranges 0.5
to 0.92"):

| Orifice type | Cd |
|---|---|
| Sharp-edged orifice (>2.5 mm) | 0.61 |
| Sharp-edged orifice (<2.5 mm) | ~0.65 |
| Short tube, rounded entrance, L/D > 3 | 0.88–0.90 |
| Short tube, conical entrance | 0.70–0.82 |
| Short tube, spiral effect | 0.2–0.55 |
| Sharp-edged cone | 0.70–0.72 |

Well-rounded entrance + smooth bore → high Cd → lower Δp for a given velocity. Burrs and
malformed exits (inward burr, rounded exit) cause misimpingement and wall streaks/burnout
`[SP-8081 §2.1.2.3]`.

**Impingement geometry** `[Huzel §4.5 p.124–128]`:
- Included impingement angle: satisfactory design value **20°–45°**. Larger angles → better
  stability but risk of splash-back onto the injector face (burnout).
- β angle: hypergolics benefit from a small positive β (**2°–5°**) — recirculation and
  liquid-phase mixing along the wall boost performance. Cryogenics (gaseous-phase mixing
  dominant) should use a slightly negative β to avoid wall hot streaks.
- Droplet size falls with orifice size (at fixed injection velocity) → higher vaporization
  rate → **the largest practical number of injection elements is the most efficient**.

**Injector patterns** `[Huzel §4.5]`, `[Sutton §8.1]`:

| Pattern | Character | Notes |
|---|---|---|
| Showerhead | non-impinging, normal to face; relies on chamber turbulence | simplest; poor performance except some cryogenic combos |
| Doublet (unlike) | ox + fuel jets impinge in pairs | good liquid-phase mixing; β varies with MR (bad for large angles); common with LOX |
| Triplet | 2-on-1 symmetric | eliminates β-vs-MR variation; intimate mixing; high performance; widely used |
| Quintuplet (quincunx) | 4-on-1 symmetric | excellent mixing/performance |
| Self-impinging (like-on-like) | fuel-on-fuel, ox-on-ox pairs | good inherent stability, moderate performance; cryo + storable hypergolic |
| Coaxial hollow post | concentric tubes; gasified H2 annulus (~330 m/s) shears slow LOX core (<33 m/s) | dominant for LOX/GH2; **not used with storable bipropellants** (Δp for high velocity too high) |
| Ring slot | concentric annular slots → conical sheets impinging like doublets | — |
| Splash plate / platelet | streams deflected off plates / etched bonded plates with many small accurate orifices + internal passages | platelet is an Aerojet-patented construction, not a spray pattern |
| Premix | fuel + ox mixed in a small chamber before entering | premix-chamber L/D critical |
| Variable-area (pintle / movable sleeve) | injection slot area varies with thrust | LEM descent engine throttled **10:1** with very small MR change |

**Throttling** `[Huzel §4.5 p.126]`, `[Sutton §8.5]`: variable-area injectors hold Δp (and
so atomization/stability) across the range; aeration (inert gas into the manifold) has
achieved up to **100:1** throttle range. The stability floor for a fixed-area injector is
where Δp/Pc drops enough that chamber-pressure fluctuations feed back into the flow
(chugging — topic 14).

**Real throttling/stiffness data by program** `[Casiano-Throttling]` — a comprehensive
survey (AIAA 2009-5540) giving a much wider evidence base than `[Huzel]`/`[Sutton]`'s single
"15-20%" rule: nominal injector stiffness (Δp_inj/Pc) should be **~15-20% but can range
5-25%** depending on injector type/thermodynamics (leaf 2, refs 19,23) — this file's 15-20%
citation is the nominal point of a wider real band, not a hard rule. A fixed-geometry
injector generally throttles only **~2:1 to 3:1**; deep throttling (5:1+) needs
above-normal stiffness at minimum thrust. **Modified RL10A-1 (1964), a directly quantified
stiffness-vs-chug-onset triplet**: at MR 4.5, chug onset at 32% thrust for the lowest-Δp
injector (20% ox Δp/Pc), 25% thrust for mid-Δp (33%), never for the highest-Δp injector
(60%) — a real, load-bearing data point tying injector stiffness directly to a chug-onset
thrust fraction. **LMDE (Apollo descent engine)**, the deepest-throttled real pintle in the
survey: 10:1 requirement met via a single central pintle sleeve, MR held constant by
separate variable-area cavitating venturis upstream (decouples MR control from
injection-area/thrust control, active only below 70% thrust); >2800 tests incl. 31 bomb
tests with **no radial or tangential acoustic modes excited**, attributed to the pintle's
*annular* (not centrally-concentrated) reaction zone; 20 psi peak-to-peak Pc ripple during
throttle transitions in the 10-100 psia Pc range. **TR202 (closed-expander LOX/GH2 lunar
pintle, 2005)**: a real, quantified counterexample to constant-stiffness assumptions —
fuel injector stiffness rises from **20% at full thrust to 106% at minimum thrust** as the
variable-area orifice closes (stiffness is NOT constant across a variable-area throttle
range; it rises sharply toward minimum thrust as effective flow area shrinks faster than
Pc). Gas-injection (aeration) chug-suppression fractions are small and quantified: **GHe at
0.4% of LOX weight flow, or GOX at 4% of LOX weight flow**, eliminated oxygen-boiling-driven
chug on RL10A-1; general rule "gas injection flow rates for stabilization are generally <1%
of propellant flow." CECE (modified RL10, 2005-2008) demonstrated **13:1** throttle range
combining reduced injector flow area with GHe injection and LOX-manifold insulation — the
same two chug fixes validated on a flight-heritage engine 40+ years after RL10A-1. See
`topics/15-transients-and-controls.md` for the fuller real-engine throttle-ratio catalog
this paper supports.

**GG-specific** `[SP-8081 §2.1.2]`: coaxial elements act like mini hot-cores, more like UMR
below ~0.5 lb/s (0.23 kg/s) per element; small triplets at ~0.1 lb/s (0.045 kg/s) per
element give minimum streaking. UMR vs hot-core: same c\* at a given temperature.

**ORSC gas-liquid injector taxonomy** `[Bazarov p.3–4]` — extends the impinging/coax/pintle
set above with types specific to oxidizer-rich-staged-combustion (warm ox-rich gas + liquid
fuel at the main injector), each with a named real-engine home and failure mode:

| Type | Real engines | Character | Failure mode |
|---|---|---|---|
| Shear coaxial (unswirled) | Vulcain, RD-0120, SSME (LOX/H2) | simplest, tight packing | sensitive to Δp pulsation → self-oscillation, injector-face fatigue cracking |
| Swirl coaxial (liquid swirled) | RL-10 family (LOX/H2) | better/more uniform atomization | strong self-oscillation if film design is off |
| Bicentrifugal swirl (both swirled) | Buran OMS/RCS | highest atomization/mixing of the coax family | high sensitivity to chamber P/velocity disturbance, poor face thermal protection — not used at high Pc |
| Gas-centered, radial-drilled liquid | medium-thrust hypergolics | simple, tunable gas-stage acoustics | combustion sits at the face with hot-gas recirculation — needs dedicated face protection |
| Gas-centered, tangential-swirl liquid annulus | **RD-120/170/180/191** (this paper's baseline) | liquid film both atomizes and passively cools the face; gas cavity acts as a Helmholtz-like acoustic resonator | poor atomization at low Pc/gas density; most complex to size |

The last type (`[Bazarov]`'s subject) has the **lowest sensitivity to chamber-pressure
pulsation** of any type here, because the liquid film is wall-stabilized in the vortex
chamber rather than free-shear-atomized `[Bazarov p.4, eq.16-20 discussion]`.

**Real ORSC baseline-injector performance** `[Bazarov p.5–6, Table 3]` — a gas-centered-swirl
element scaled from the RD-170 patent, tested at Pc 2150 psia: **η_c\* = 0.97, η_CFv (vacuum
thrust coefficient) = 0.98**, ΔP_ox = ΔP_fuel = 226 psid (≈10.5 % of Pc each side) — a real
data point alongside `[Huzel]`'s 15–20 %/Pc rule, at the low end because this element type is
inherently stiffer against pulsation. Single-element sizing: 271-element RD-170 patent count
→ thrust/element ≈1700 lbf at full Pc 3720 psia; de-rated test article set throat dia. to a
manufacturable 1.0 in (vs. 0.7 in from literal thrust scaling) rather than scaling geometry
linearly — a real example of "round to a buildable/coolable size" overriding a pure scaling
law.

**Independent corroboration of the 15-20%-of-Pc rule (2026-09-24)** `[Armstrong-MarsISRU
§Ch.I p.3]`: a real "15% of Pc" injector-pressure-drop-for-stability rule cited in a 1991
NASA cooling-analysis report, a second independent corroboration of the existing `[Huzel]`
15-20%/Pc rule above from an unrelated source and application. **Real SSME main-injector
detail** `[SSME-Orientation p.28-34, 40-41]`: 600 coaxial elements + 42 flow shields + a
porous rigimesh transpiration-cooled faceplate — a real high-Pc staged-combustion injector
element-count anchor.

**Atomization-quality driver: velocity difference, not momentum ratio** `[Bazarov p.9–13]` —
cold-flow tests on the gas-centered-swirl element found that sweeping **momentum flux ratio**
(ρ_g·U_g²/ρ_l·U_l²) at fixed geometry/flow gave "little to no significant change" in spray
character, while sweeping the **gas/liquid differential velocity** ΔU = U_g,axial − U_l,film
drove clear atomization-quality trends. If `injectors.py` ever exposes a momentum-ratio
metric for coax/swirl-type elements, gas-liquid velocity difference may be the more
physically load-bearing number to surface, not momentum ratio alone. A related AFRL
gas-centered-swirl study got **c\* efficiency > 90 %** with drop sizes 3–4× finer than
equivalent shear-coaxial elements, but some geometry variants showed "chug" instability at
certain operating points (topic 14) — a concrete atomization-vs-stability tradeoff.

**Real shear-coaxial atomization measurements, LOX/GH2** `[PSU-CoaxAtom, Results]` — PDPA
laser-diagnostic measurements on a single shear-coaxial element (3.43mm LOX post ID, 3.78mm
recess, geometry comparable to SSME preburner elements), both hot-fire and cold-flow
(water/GN2): LOX core visually intact for **~50mm from the injector face (≈14.6× post ID)**
before a drop field forms — a concrete intact-core-length anchor for shear-coaxial LOX
breakup, useful if `engine_designer` ever wants an intact-core-length check (none exists
today). Drop-size PDF mode **20-30 µm**, D32/D10 both decreasing with radial distance from
centerline (largest drops on-axis). **A real, "counterintuitive" caution for any cold-flow-
based sizing rule**: matched-flowrate hot-fire sprays produced **larger** drops than a
cold-flow water/GN2 simulant, despite the hot-fire case's much higher Re/We (which by
classical atomization scaling should give smaller, not larger, drops) — the paper concludes
the combusting gas-phase velocity field must differ substantially from the cold-flow field,
altering the shear-atomization mechanism itself. **Cold-flow injector characterization
cannot be naively rescaled to predict real combusting spray behavior for this injector
type** — a real caution for any future cold-flow-calibrated Cd/atomization-time model.

**Injector/combustor-geometry effect on performance** `[CR-128318 abstract, p.82]` — a
96-element, 4-ring impinging-triplet LOX/GH₂ injector (Pc 225 psia, L\*=20 in, contraction
ratio 2.0) achieved **C\* efficiency ≈ 97 %, Isp efficiency ≈ 94 %** across 15 hot-fire tests
— a real triplet-element c\* data point at modest Pc, usable alongside `[Huzel]`/`[Sutton]`'s
general efficiency bands (topic 03). The same report's single-element cold-flow work found
mass-median atomization dropsize **100–225 μm** for this triplet geometry, confirming (over
an extended 50–260 psi range) a prior correlation that dropsize is inversely proportional to
a power of the gas dynamic parameter ρ_g·V_g² — and that **normalized dropsize distribution
is invariant with test condition** (a single dimensionless curve describes the whole matrix).
Single-element mixing efficiency peaked at hot-fire-equivalent MR 3–5 for this geometry and
improved with increasing collection distance from the face.

**Injector zoning as a passive film-cooling technique — a real quantified tradeoff**
`[TP2862-LOXRP1 Summary p.14-15]`: sealing the outer oxidizer ring of a 61-element O-F-O
triplet injector (making the near-wall combustion fuel-rich — the outer zone carried 26-30%
of total fuel but only 13-17% of total oxidizer) cut throat heat flux **47%** for only a
**4.5% C* efficiency cost** (99.5% UMR → 95-96.2% zoned). This is a real, hot-fire-measured
data point for trading injector-face design against wall heat load — distinct from added
film-coolant flow, achieved purely by injector-element pattern/zone choice. See
`topics/06-cooling-and-heat-transfer.md` for the accompanying heat-flux-magnitude and
c*-efficiency-anchor detail from the same source.

**Hydrocarbon injector-geometry sensitivity, wall-heating side** `[SECA-HT §4.2, ~p.67]` — a
CFD/test study of a LOX/RP-1 subscale motor found that **small changes to a like-impinging
circumferential-fan injector configuration caused large changes in chamber-wall and nozzle
heating**, not just combustion efficiency. A real-hardware caution that hydrocarbon injector
geometry is unusually sensitive for wall heat flux — worth flagging alongside any future
injector-geometry design-choice warning.

## Worked numbers

`[Huzel Sample 4-4-region p.131]` A-1 GG-style injector: V_ox = 1076 in/s (89.6 ft/s),
V_fuel = 9500 in/s (790 ft/s), injection momentum ratio Rm = (285.2·89.6)/(54.5·790) ≈ 0.6.
Note the fuel is injected ~9× faster than the oxidizer here (heavily fuel-rich GG).

## Caveats

- "15–20 % of Pc" is a rule of thumb for the *nominal* operating point; real engines run
  higher (up to ~35 %) when stability demands it, and small thrusters run 30–50 %.
- Cd values are for specific orifice geometries and Reynolds-number ranges; they shift with
  chamfer, entry radius and burrs (the reason cold-flow water tests are mandatory).
- The literature has no clean way to isolate "injector type" as a single efficiency
  multiplier — `[SP-8081]` and `[Sutton §8.1]` both say injector design is largely
  empirical, evaluated by hot firing.
- `[PSU-CoaxAtom]`'s findings are from a **uni-element, sub-scale optically-accessible rig**
  (one 3.43mm-post injector, not a full injector face) — real for that specific geometry, but
  not a universal shear-coaxial constant without checking scale sensitivity.
- `[Casiano-Throttling]` is a survey/review paper (its own restatement of ~118 underlying
  references), not primary data — treat its numbers as a reliable index of real program
  outcomes, and it's explicitly US-centric (Russian swirl-injector deep-throttling work is
  only lightly covered; `[Bazarov]` remains the better source for that). `[TP2862-LOXRP1]`'s
  zoning result (47% flux/4.5% C* tradeoff) is specific to one small-chamber 61-element
  injector's particular zone split (13-17%/26-30% ox/fuel diversion) — the paper itself notes
  a large thrust chamber wouldn't need as much core-MR shift to compensate, so treat the exact
  percentages as scale-specific, not universal.

## Implications for engine_designer

- `injectors.py` `dp_over_pc_nominal` (impinging 0.175, pintle 0.20, coaxial_swirl 0.15,
  catalyst_bed 0.12, platelet 0.25): the impinging value sits squarely in `[Huzel]`'s
  "15–20 % of Pc"; coax slightly below and platelet slightly above are both consistent with
  the pattern that higher-stiffness patterns run higher Δp. **Well-supported by the
  literature at the type level** even though the per-type spread is an estimate
  (ASSUMPTIONS.md item #10).
- `min_stable_dp_ratio` (chug/hydraulic-stability floor, 0.05–0.10): `[Sutton §9.3]` and
  `[Huzel §4.5]` both say increased injection Δp is the primary cure for chugging, and
  chugging is worst at low Pc (100–500 psia) — consistent with a floor expressed as a
  fraction of Δp/Pc. No literature number for the exact floor.
- `practical_min_throttle` (demonstrated deep-throttle ability): pintle 0.10 is backed by
  `[Sutton §8.1]` — the LEM descent engine variable-area concentric-tube injector throttled
  **10:1** with very small MR change. Catalyst-bed 0.08 = MR-80B (already cited). Impinging
  0.60 (fixed-area, can't throttle deep) is consistent with "variable-area injectors are
  needed to hold Δp across the range."
- `eta_cstar_multiplier` per injector type (0.97–1.02, ASSUMPTIONS.md item #10): the
  literature supports the *ordering* (showerhead worst; triplet/quintuplet/platelet best;
  self-impinging moderate) but gives no magnitudes — `[SP-8081 ref. 14]`'s "same c\* at a
  given temperature" for UMR vs hot-core suggests the true spread is small, which matches
  the tool's ±2 %.
- `atomization_time_modifier` (ASSUMPTIONS.md item #21): `[Huzel §4.5]` "droplet size falls
  with orifice size → higher vaporization rate → more elements = more efficient" supports
  finer patterns (platelet, coax) having shorter atomization time; magnitudes still an
  estimate.
- Coax-swirl `suited_pairs = LOX/LH2` only: `[Sutton §8.1]` explicitly — coaxial hollow-post
  "is not used with liquid storable bipropellants" because the Δp for high velocity is too
  high. The tool's suitability warning for coax on a storable is literature-backed.
- β angle (2°–5° positive for hypergolics, negative for cryo) is not currently modelled;
  `[Huzel eq. 4-41]` gives it if injector geometry is ever exposed.
- **ORSC/gas-centered-swirl element type**: `injectors.py` doesn't yet model this element
  family at all (its coax type covers shear/swirl coaxial, not the RD-120/170/180-style
  gas-centered swirl). `[Bazarov]`'s real η_c\*=0.97/η_CFv=0.98 pair is a directly-quotable
  efficiency anchor if this element type is ever added — same role as `[KBKhA]`'s RD-0110/
  RD-0124 table for the cycle constants (topic 08).
- **Momentum-ratio vs velocity-difference**: if `injectors.py`'s coax/swirl momentum-ratio
  metric is ever extended or re-derived, `[Bazarov]`'s cold-flow finding (ΔU dominates over
  momentum flux ratio for atomization quality) is worth checking against — the tool
  currently exposes momentum ratio (`Rm`), not a raw velocity-difference metric.
- `eta_cstar` for impinging-triplet LOX/GH₂ (`[CR-128318]`'s 97 %/94 % c\*/Isp efficiency)
  is a second real triplet-element anchor beyond the tool's existing calibrated pairs
  (topic 03) — consistent with, not a correction to, the current LOX/LH2 calibration.
- `min_stable_dp_ratio`'s "0.05-0.10" floor now has a real, directly quantified anchor
  point: `[Casiano-Throttling]`'s RL10A-1 32%/25%/never chug-onset triplet ties a specific
  injector-stiffness value (20/33/60% ox Δp/Pc) to a specific chug-onset thrust fraction —
  the first real data connecting *both* variables at once (prior sources gave each
  separately). Report-only — no code changed, but a real spot-check candidate if
  `min_stable_dp_ratio` is ever tuned against a named engine.
- `practical_min_throttle` for pintle-type injectors: `[Casiano-Throttling]`'s TR202 finding
  (stiffness rises from 20% to 106% across the throttle range) means a constant-Δp/Pc
  assumption for `dp_over_pc_nominal` breaks down badly near an injector's minimum-thrust
  point for variable-area types specifically — not currently modeled (the tool's
  `dp_over_pc_nominal` is a single per-type constant, not throttle-fraction-dependent).
  Flagged as a real gap if deep-throttle pintle modeling is ever added.
