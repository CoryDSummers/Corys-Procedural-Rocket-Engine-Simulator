# Fagherazzi (2019) — Design and Development of a Regenerative Cooling for Small Liquid Engines

## Identity

Matteo Fagherazzi, *Design and development of a regenerative cooling for small liquid
engines*, Master's Thesis in Aerospace Engineering, Università degli Studi di Padova
(supervisor Daniele Pavarin, co-supervisors Francesco Barato and Marco Santi), academic
year 2018/2019. `literature/Fagherazzi_Matteo_1153454.pdf` (156 PDF leaves; front matter
leaf 0-25, Chapter 1 "Introduction" starts leaf 26/printed p.1 — offset is leaf = printed + 21
through the body chapters, confirmed at multiple points, e.g. "Cooling technologies" §1.2 at
leaf 27/printed p.6). Tag: `[Fagherazzi-2019]`.

## Character

**A full end-to-end regenerative-cooling design thesis for a small (250-400 N, ~9-16.5 bar
Pcc) HTP (High Test Peroxide)/diesel swirl-injector engine** — combustion model (NASA CEA)
→ 1-D channel-by-channel heat-transfer/pressure-drop MATLAB model → sensitivity scenarios
→ mechanical/CAD design of an actual 3D-printed nozzle with bolted flanges, volute
manifolds, and seals → (incomplete, per the abstract) an experimental test campaign. This is
the **single most complete regen-cooling-and-manifold design methodology source in
`claude_lit/`** — more mathematically detailed than `[Marquardt-5981]` (which is a
cooling-method *selection* study with unreadable graphs) and more design-process-complete
than `[SP-8087]`-style monographs, though it is a **student thesis, not a peer-reviewed
industry design-criteria document** — see Caveats.

Structure: Ch.1 Introduction (cooling technologies, propellant choice, HTP background),
Ch.2 Mathematical model of heat transfer (CEA combustion model, channel/wall geometry,
Bartz-based heat-transfer model, empirical Nu correlations, pressure-loss model, then six
parametric-sensitivity "scenarios" and a "final motor configuration" worked example), Ch.3
The design process (3D-metal-printing constraints, final nozzle/flange/manifold-volute CAD,
structural FEM checks, sealing/gaskets, threaded joints), Ch.4 The prototype and test matrix
(assembly, feed system, test plan), Appendix A.

## This note's extraction scope

Read in full: Ch.1 §1.2 "Cooling technologies" (leaf 27-28); all of Ch.2 §2.4 "Mathematical
model" (leaf 43-72: geometry, channel geometry/wall-thickness sizing, heat-transfer theory,
Bartz + empirical Nu correlations, pressure-loss model) and §2.5 results/scenarios (leaf
72-93, esp. §2.5.4 channel-geometry scenario and §2.5.5 final motor configuration real
numbers); Ch.3 §3.3.1-3.3.2 (nozzle final configuration + **connection-flange volute/
distribution-system manifold design**, leaf 94-111). **Not read**: Ch.1 §1.3 propellant/HTP
history in detail (skimmed only, not relevant to cooling); Ch.3 §3.3.3-3.3.7 (closing flange,
sealing/gaskets, threaded joints, connection joints — skimmed only, not deep-read, mostly
mechanical-fastener sizing with no propulsion-physics content); all of Ch.4 (prototype/test
matrix) and Appendix A — not read, out of scope for a cooling/manifold-methodology extract.

## Key results — Wall construction: NO "sandwich" construction found

The user specifically asked about **Russian "sandwich" wall construction** (two thin face
sheets with a corrugated/ribbed core brazed between them for coolant passages, distinct from
discrete tube bundles or machined-channel-in-solid-wall construction). **This thesis does
not mention sandwich/double-wall construction anywhere** (confirmed by an explicit text
search for "sandwich" and "double wall"/"double-wall" across all 156 pages — zero hits). Its
own literature review of construction types (`[Fagherazzi-2019 §2.4.3 p.30-31]`) covers only
two families: **tubular channels** (the historical F-1-style tube-bundle nozzle, cites
heroicrelics.org for a real F-1 photo) and **machined/milled channels in a solid liner with a
bonded outer jacket** (end milling, water-jet milling, or electro-erosion to cut the channel,
then closeout by pressure-assisted braze, standard braze, electroplating, vacuum plasma
spray, explosive bonding, laser welding, or diffusion bonding) — the latter is what this
thesis itself uses (water-jet-milled rectangular channels, closed out with a bonded/3D-printed
outer jacket). **Conclusion for the user's question: sandwich construction is not covered by
this new source** — it remains uncited anywhere in `claude_lit/`. If Russian sandwich
construction is still wanted, a source specifically on Russian engine hardware (e.g. RD-170/
RD-180 chamber-wall descriptions) would be needed; none of this literature batch's other new
PDFs were confirmed to cover it either (see other `sources/*.md` notes from this batch).

## Key results — Channel/wall geometry and sizing method

- **Rectangular channel cross-section is explicitly stated as the industry-standard choice**
  ("the rectangular section configuration is the most widespread because it results to be the
  best compromise between effectiveness and cost of realization" `[Fagherazzi-2019 §2.4.3
  p.32]`) — direct corroboration for `engine_designer`'s `milled_channel` wall construction
  type already using an implicit rectangular-channel model.
- **Channel geometry parameterized by aspect ratio (AR) and channel width (w_ch), both
  varying with axial coordinate** via spline interpolation over `n` user-defined stations —
  the same design-freedom idea (allowing the coolant channel to be wider/shallower or
  narrower/deeper at different points along the nozzle) that a more detailed
  `engine_designer` channel model would need if extended beyond a single lumped
  `WALL_CONSTRUCTIONS` mass-factor.
- **Liner (hot-wall) thickness from a pressure-vessel hoop-stress relation** `[Fagherazzi-2019
  eq. 2.16, §2.4.3 p.32]`: `t_cs = Pcc·r_max·η_P / σ_UTS`, with `η_P = 2` "generally, for
  small motor" — a safety/pressure factor of 2 baked into the liner-thickness formula itself
  (distinct from, and stackable with, a separate structural safety factor). This is the same
  hoop-stress form as `[Huzel eq. 2-10]`/`mass_model.shell_mass_kg` already uses (`t =
  SF·Pc·r/σ`), corroborating that formula's applicability at small-engine scale too.
- **Channel-wall thickness from a pressurized-pipe relation** (UNI EN ISO 7098 form)
  `[Fagherazzi-2019 eq. 2.17]`: `t_pipe = (P·d_ext/(20σ_UTS) + P + c)·100/(100-tol%)`, with a
  5% manufacturing-tolerance derate and zero corrosion allowance for this application. Real
  worked numbers for a 20.55 mm max-radius engine: AISI 630 steel gives `t_cs = 0.048 mm`
  (liner) / `t_pipe = 0.498 mm` (channel wall); Inconel 718 gives `0.054 mm` / `0.603 mm`
  `[Fagherazzi-2019 Table 2.4]` — both far thinner than manufacturing tolerance allows, so the
  thesis fixes both to a practical **0.5 mm floor** driven by 3D-printing process capability,
  not by structural need. This is a real-hardware corroboration of the general principle (also
  seen in `[SP-8120]`'s minimum-passage-dimension finding and `[Marquardt-5981]`'s 0.062 in
  minimum) that **at small engine scale, minimum practical/manufacturable wall thickness
  governs, not calculated stress** — the structural formula is a lower bound that is rarely the
  binding constraint at this size.
- **Channel-wall stress equation** (adapted from a circular-tube formula, `[Fagherazzi-2019
  eq. 2.19]`): hoop stress from coolant pressure + thermal stress from the temperature
  gradient across the tube wall + bending stress from inter-channel pressure discontinuity —
  explicitly noted as only an order-of-magnitude estimate for non-circular (rectangular)
  channels since polygonal corners concentrate stress in a way circular sections don't.
- **Liner "butterfly" thermal-stress pattern** `[Fagherazzi-2019 eq. 2.20]`: `σ_w =
  2βEΔT/(1-ν)` — states plainly that **yield stress is often exceeded** by this formula in
  practice, i.e. real regen liners commonly run into local plastic/low-cycle-fatigue territory
  at the hot wall by design, not by mistake. This is a real corroboration for
  `engine_designer`'s existing throat low-cycle thermal-fatigue estimate in `mass_model.py`.
- **37 channels** used in the final design, chosen partly to leave room for thermocouple
  wells between channels, not purely for thermal/hydraulic optimum.
- **A real design-of-experiments scenario on AR and channel width** `[Fagherazzi-2019 §2.5.4,
  Table 2.7, Fig. 2.27-2.29]`: reducing channel cross-section increases heat flux and reduces
  peak wall temperature but pressure drop rises **more than exponentially** past a point of
  diminishing thermal return — i.e. there is a real optimum trading cooling performance
  against pressure loss, and it must be found numerically (no closed-form optimum exists per
  this thesis). A quoted **rule of thumb: maximum permissible regenerative-cooling pressure
  loss is 15-22% of coolant inlet pressure**, "depending on design requirements"
  `[Fagherazzi-2019 §2.5.4 p.59]` — this is a real, independent number for the jacket-ΔP
  fraction question already discussed in `topics/06b-cooling-methods-and-chemistry.md` (existing
  anchors: `[Sutton Table 8-1]` real jacket ΔP 100-540 psi across RS-27/RL10B-2/LE-7; the
  tool's `JACKET_DP_PA` scaled 1.0 for regen). A 15-22%-of-Pcoolant-inlet framing is a
  different (percentage-of-supply-pressure, not absolute-pressure) way to bound the same
  quantity, worth cross-referencing if `design.py` is ever changed to size jacket ΔP as a
  fraction of coolant supply pressure rather than a flat value.

## Key results — Heat-transfer model (largely corroborates existing `claude_lit` sources)

- **Gas-side**: identical Bartz form to `[Huzel eq. 4-13]`/`cooling.py`'s implementation,
  `[Fagherazzi-2019 eq. 2.35-2.36]`, plus an explicit **radiative gas-side term** for
  heteropolar combustion-product species (H2O, CO2) using the standard Δ(T/100)^3-4
  empirical form `[Fagherazzi-2019 eq. 2.39-2.41]` — the same "only H2O/CO2 radiate
  meaningfully, symmetric molecules like H2/O2/N2 don't" framing already noted from
  `[Sutton]` in `topics/06`. **80% convective / 20% radiative split on the gas side** is
  quoted from the literature `[Fagherazzi-2019 §2.4.5 p.44, citing ref 21]` — a concrete
  number for the convective/radiative heat-flux split not previously anchored numerically in
  `claude_lit` (existing `topics/06` only had "radiation is 5-35% of transferred heat"
  `[Sutton §8.2]`, a wider/vaguer band; 20% sits inside that band as a more specific point
  estimate for this class of engine, not a contradiction).
- **Coolant-side**: five different published Nu correlations coded and compared — Sieder-Tate
  (laminar, `[Fagherazzi-2019 eq. 2.48]`, and turbulent, `eq. 2.50`), a laminar/turbulent
  blend for the transition regime, Gnielinski (`eq. 2.51-2.52`, most broadly valid: 3000 <
  Re < 5e6), and two entrance-effect-corrected correlations for laminar/transitional/
  turbulent flow (`eq. 2.53-2.55`). This is a substantially richer coolant-side correlation
  set than `topics/06`'s existing single Dittus-Boelter-form citation — useful if
  `engine_designer/physics/cooling.py` is ever extended with a real coolant-side channel
  h_c model (it currently only has a coarse `WALL_CONSTRUCTIONS`-scaled proxy, not a real
  Nu correlation).
- **Only 0.5-5% of combustion energy reaches the walls** `[Fagherazzi-2019 §2.4.5 p.42, citing
  ref 2 = Sutton]` — exact match to the existing `[Sutton §8.2]` figure already in `topics/06`
  and already used as `validate.py::run_cooling_heat_flux_check()`'s gating band; this is a
  second independent citation of the same number, not a new one.
- **Soot-layer thermal resistance found to be too influential to trust**: the thesis initially
  modeled a hydrocarbon-combustion soot layer (empirical thickness correlations,
  `[Fagherazzi-2019 eq. 2.43-2.44]`, cited from an unspecified source) but **explicitly
  excluded it from final results** because its low conductivity (~0.07 W/m·K) perturbed
  predicted wall temperatures beyond literature-plausible ranges `[Fagherazzi-2019 §2.5.6
  p.67]` — an honest negative result: don't trust a thin-soot-layer correction without
  independent validation, even though the correlation exists in the literature.
- **Boundary layer never fully develops in a real variable-geometry regen channel**
  `[Fagherazzi-2019 §2.5.6 p.68]`: because channel cross-section and wall heat flux both vary
  continuously along the nozzle contour, the flow is "always inside the entry region" in a
  fully-developed-flow sense — meaning the many textbook Nu correlations (which assume
  fully-developed flow) are all technically misapplied to some degree in a real tapering
  nozzle jacket. Treated as an accepted, unavoidable modeling approximation, not a fixable
  error — useful context for how much precision to expect from *any* 1-D regen channel model
  including `engine_designer`'s own coarser one.
- **Working recommendation: avoid boiling in the bulk coolant, permit only local/incipient
  nucleate boiling** `[Fagherazzi-2019 §2.4.5 "Boiling phenomena" p.41-42]` — standard
  regen-cooling practice, consistent with (not new versus) existing sources, but with a
  concrete added caution for oxidizer coolants: "boiling can determine the decomposition and
  explosion" for HTP specifically — a peroxide-specific hazard note not applicable to
  RP-1/LH2/methane engine_designer already models, but relevant if a peroxide monopropellant/
  bipropellant coolant loop were ever added.

## Key results — Manifold ("distribution system") design: real corroboration for `manifold.py`

**The most directly relevant finding for `engine_designer/physics/manifold.py`**
`[Fagherazzi-2019 §3.3.2 "Distribution system" p.87-88]`: the thesis sizes its coolant supply
manifold as a **volute** (a scroll-shaped duct wrapping around the flange, splitting the
incoming flow into two symmetric halves feeding the channel bundle from both sides) using
the exact same design principle `manifold.py` already implements —
**constant-target-velocity cross-section sizing from the continuity equation**:

    A(θ) = ṁ(θ) / (ρ·v̄)

where `θ` is the angle around the volute and `ṁ(θ)` is the cumulative flow already
distributed to channels upstream of that angle (so the volute cross-section *shrinks* as flow
peels off into channels along its length) — a real, independently-arrived-at instance of
`manifold.py`'s own "cross-section from mdot/density/target feed velocity" approach, now with
a second real-design precedent beyond whatever anchored it originally. Design intent stated
explicitly: **avoid abrupt velocity changes between the supply volute and the cooling
channels**, and keep the volute's envelope clear of the o-ring seal lands and bolt circle. A
**circular cross-section is stated as hydraulically optimal, but a rectangular section was
chosen instead purely for machinability** (no CNC available in the thesis's shop) —
i.e. real design practice trades hydraulic optimality for manufacturing simplicity at small
scale, worth remembering as a caveat on any "optimal" manifold cross-section
`engine_designer` might suggest. Two volute variants were carried: a full variable-
cross-section optimized volute (`A(θ)` per the equation above) and a **simplified
constant-cross-section volute** (`A(θ) = const`) — the simplified version trades some flow
uniformity for much easier fabrication, a real, usable "cheap but good enough" fallback
option if `manifold.py` or its documentation wants to offer a non-optimal-but-simple sizing
mode.

A related real design constraint: the **inlet feeding channel had to be moved off-axis
(inclined) to route around the o-ring seal lands**, and the coolant **outlet fitting required a
90° flow-diversion elbow** to exit the flange radially rather than axially
`[Fagherazzi-2019 §3.3.1 p.78, Fig. 3.3-3.4]` — real evidence that manifold/fitting geometry
is frequently driven by seal/fastener-envelope packaging constraints, not by hydraulics alone;
a real-world caveat on the idealized picture of a "hook point" as a single clean attachment
vector (as `manifold.py`'s current per-propellant "hook point" data already flags as a
simplification for a future plumbing feature).

## Design method (partial usability for `engine_designer`)

Unlike `[SP-8120]`/`[Marquardt-5981]` (criteria/precedent sources with no reusable
closed-form constants), this thesis **is** a working closed-form + numerical design method,
but calibrated/validated only against its own small HTP/diesel engine (280 N, 9.87 bar Pcc) —
treat its correlation *choices* (which of the 5 Nu correlations to prefer, the AR/w_ch
optimization approach, the volute-sizing method) as reusable design **process**, and its
specific *numbers* (0.5 mm minimum wall, 37 channels, 15-22% ΔP/Pin, 20% radiative fraction)
as small-engine-scale data points to corroborate against, not as universal constants.

## Section map

- Ch.1 §1.1 rocket-engine-types overview: leaf 26-27 (printed p.1-5) — skimmed.
- **§1.2 Cooling technologies: leaf 27-28 (printed p.6-7) — read in full.**
- §1.3 Propellants / HTP history: leaf 29-42 (printed p.8-21) — skimmed (not
  cooling/manifold-relevant).
- **Ch.2 §2.3-2.4 Combustion model + Mathematical model (geometry, channel/wall sizing,
  heat-transfer theory, Bartz + Nu correlations, pressure losses): leaf 43-72 (printed
  p.22-50) — read in full.**
- **§2.5 Results (six scenarios + final motor configuration + final considerations): leaf
  72-93 (printed p.51-72) — read in full.**
- Ch.3 §3.1-3.2 Design specifications + 3D-printing process: leaf 94-98 (printed p.73-76) —
  read in full (process constraints relevant to minimum wall thickness).
- **§3.3.1-3.3.2 Nozzle final configuration + connection-flange manifold/volute design: leaf
  98-111 (printed p.77-88) — read in full.**
- §3.3.3-3.3.7 Closing flange, sealing/gaskets, threaded joints, connection joints: leaf
  109-122 (printed p.88-98) — skimmed only (mechanical-fastener/seal sizing, not
  propulsion-physics).
- Ch.4 Prototype and test matrix, Appendix A: leaf 123-156 (printed p.101-123+) — not read.

## Caveats

- **This is a master's thesis, not a peer-reviewed industry design-criteria document.** Its
  literature synthesis (construction types, correlation selection, design rules of thumb) is
  well-sourced and citable, but its own novel numerical results (the specific 15-22%
  pressure-loss rule, the 20% radiative fraction, the AR/w_ch optimization trends) come from
  a single small-engine numerical study, not validated real-hardware data or an
  industry-wide survey — treat with the same caution as `[EUCASS2023-035]` or any other
  single-team small-engine paper in this literature set, one tier below `[SP-8087]`/
  `[SP-8120]`/real-engine sources like `[NK-33-Mod]`/`[AEDC-J2S]`.
- **No sandwich/double-wall construction coverage** — confirmed absent by full-text search
  (see above). Do not cite this source for that topic.
- **Engine scale is very small** (250-400 N thrust, ~9-16.5 bar/130-240 psia Pcc, HTP/diesel)
  — smaller even than `[Marquardt-5981]`'s 20-10,000 lbf (89-44,500 N) range. Numbers here are
  most relevant to small-thruster/RCS-class `engine_designer` designs, not booster-class ones.
- **Swirl-injector convective coefficient is explicitly flagged as unvalidated**: the thesis's
  Bartz-based gas-side model is derived for axial combustion only; it notes "no empirical
  relations which quantify the convective coefficient are available for swirl combustions"
  and that experimental/numerical evidence suggests the real swirl-flow convective
  coefficient is higher than the axial-flow prediction used — i.e. its own swirl-engine
  results in §2.5.5 (Table 2.9, not extracted in detail here) likely underpredict wall heat
  flux somewhat.
- OCR/text quality is excellent (born-digital PDF, clean LaTeX/Word-style text layer, no OCR
  garbling) — direct quotes above are reliable transcriptions, not eye-reconstructions.
