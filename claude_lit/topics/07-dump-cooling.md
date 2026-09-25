# 07 — Dump cooling

## Scope

Dump cooling as a distinct cooling mode: the concept, the coolant-passage sizing method, the
minimum coolant fraction, and the coolant-Isp recovery. Most content comes from one source —
`[TN-Dump]` (NASA TN D-3532) — for propellant-fraction dump cooling. Since 2026-09-24, this
file also covers the closely related but distinct **turbine-exhaust-gas film cooling** of a
nozzle extension (`[SP-8120]`'s real F-1 case) — a different coolant medium (turbine exhaust,
not propellant) but the same "secondary flow protects/cools an extension, then is ejected or
reintroduced" architecture, directly relevant to `EngineDesign.dump_coolant_fraction`'s
existing Vulcain-HM-60/J-2-anchored nozzle-extension dump cooling and to the planned
turbine-exhaust-handling feature (see `OPEN_QUESTIONS.md`).

## The concept

`[TN-Dump §Introduction]`, `[Huzel §4.4 p.98]`, `[Sutton §8.2]`:

- A fraction of one propellant (in practice, the fuel — hydrogen in a LOX/LH2 engine) is
  routed through cooling passages in the chamber/nozzle wall, then **dumped overboard
  through a convergent-divergent nozzle at the rear of the nozzle skirt** — not injected into
  the chamber.
- Key advantage: the **coolant jacket pressure drop is in *parallel* with the injector
  pressure drop, not in series**. The propellant tanks can therefore be pressurised to a
  lower value than for an equivalent regeneratively-cooled engine → lighter tanks, less
  pressurant, or smaller pumps.
- The heated coolant, expanded through its own C-D nozzle, **recovers some of its energy as
  thrust**. Heated hydrogen gives a very reasonable theoretical Isp so it "detracts little
  if any from the overall specific impulse."
- Design objective (opposite to regenerative cooling): raise the coolant to the **highest
  temperature the wall material allows, using the *minimum* coolant flow** — whereas regen
  design fixes the coolant flow and *minimises* the jacket ΔP.
- Status: `[Huzel]` "because of inherent problems, this method has only limited
  application." `[Sutton]` mentions it only in passing.

## Coolant-passage sizing method (`[TN-Dump]` Appendix B)

An iterative axial march (11 increments), solving at each station for the local
coolant-passage flow area that holds the flame-side wall temperature at the material limit
(2000 °R for 304 SS here), using **real temperature-dependent coolant transport properties**
because H2 density/Cp/viscosity change enormously as it heats down the passage:

1. Local gas-side heat flux from Bartz-type / Dittus-Boelter `h_g` (`Nu_f = 0.023·Re_f^0.8·
   Pr_f^0.4`, properties at film temperature `½(T_g,w,ad + T_w,g)`; recovery factor **0.88**).
   See topic 06.
2. Coolant-side `h_c` from the same Dittus-Boelter form for subcritical-pressure H2 gas/
   vapor.
3. Solve for the coolant velocity (hence passage area) that makes the coolant remove exactly
   that flux while holding the wall at the limit.
4. Advance one increment; update coolant thermodynamic state (temperature from the energy
   balance `Q = ṁ_c·Cp·ΔT`, pressure from momentum + friction ΔP — both terms matter because
   H2 density drops a lot along the passage).
5. Repeat to the exit.

Appendix C is the off-design version (other O/F and coolant flows, fixed geometry — can
report a **burnout location** where the coolant cannot hold the wall below the limit).
Appendix D is the spacer-helix geometry that turns the axial area schedule into a physical
passage.

## Key numbers (`[TN-Dump]`)

Test article: 500 lbf, Pc 100 psig, GH2/LOX, O/F 5, LH2 coolant; two concentric 0.100-in
304 SS shells, 0.10-in radial gap, 8 spiral passages, helix angle varied for locally-optimum
coolant velocity; L\* 20 in, contraction ratio 3, ε 2.5.

| Quantity | Value |
|---|---|
| Design coolant flow | 7 % of total propellant flow |
| **Min satisfactory coolant flow (uncoated)** | **7.5 %** |
| **Min satisfactory coolant flow (0.033-in Al2O3 coating)** | **6.9 %** |
| Effect of Al2O3 coating | jacket ΔP down ~20–30 psi; coolant outlet temp down ~90–100 °R at fixed flow |
| Over-cooled zones observed | first ~3 in from injector (finite combustion length); just downstream of throat |
| Coolant inlet | ~57–85 °R, 90–150 psia |
| Coolant outlet (304 SS wall) | see Fig 13/19 (chart) — a few hundred °R |
| **Projected with Mo inner shell** | flame-side wall limit 3160 / 3560 °R → coolant outlet 1575 / 1900 °R → **theoretical dumped-H2 Isp 510 / 560 s** — equal to or above the main-chamber Isp |

## Turbine-exhaust-gas film cooling of a nozzle extension — the real F-1 case
`[SP-8120 §2.2.2/§3.2.2, full read 2026-09-24]`

The single most valuable real-hardware precedent in this reference set for a turbine-exhaust
film-cooled extension — "the only example of a film (gas)-cooled extension in production."
**Real geometry**: the F-1's regeneratively cooled section extends to **area ratio 10:1**;
the turbine-exhaust film-cooled extension continues from **10:1 to 16:1** — a real, exact
expansion-ratio anchor for where turbine-exhaust film cooling picks up, directly relevant to
any `regen_nozzle_end_eps`-style cutoff for a future turbine-exhaust-film mode. Construction:
outer skin + inner **shingles** (overlapping, forming coolant slots) connected by Z-stringers,
all **Hastelloy C**.

**The core design problem and its real quantitative fix**: large separation between the main
gas stream and coolant-gas stream, plus nonparallel injection, caused the main flow to detach
and reattach downstream — destroying the film layer and burning out shingles at the
reattachment point. Fix: concentrate **~25-30% of the total film-coolant (turbine-exhaust)
flow at the attachment region**, leaving the rest for the remainder of the extension — a
real, citable coolant-distribution split, **determined experimentally** since "no analytical
technique available at the time would adequately predict the results." Real effectiveness
rule: minimum stream mixing (best film use) occurs with coolant injected **parallel to the
main gas stream, at the highest possible velocity, with the smallest gas-stream separation**.

**Real materials/failure-mode detail**: ductile shingle/structural materials required to
avoid low-cycle thermal fatigue — **Inconel 625, Hastelloy C, or 347 CRES**; the production
F-1 uses a dimpled-sheet shingle design (limits deflection both directions without letting
slots close or over-widen) after rigid shingles proved thermal-distortion-prone. Retaining
bands specific to hot extensions get insulation + scalloped weld joints to cut band
temperature/weight, and (design criterion) should be **overdesigned by 50%** during initial
design to cover start-transient-side-load uncertainty — a real, quotable design-margin
number.

**Real overall performance contribution and structural load** `[SP-8120 §2.2.5.3 p.48-51]`:
turbine-exhaust-gas thrust potential is typically **~0.5% of total engine thrust**
(**16,000 lbf potential for the F-1** specifically) — large enough that supporting structure
needs careful load analysis for large engines. A real safety-relevant finding: a
**looped-tube turbine-exhaust configuration must not be used with noncryogenic (storable)
propellants** — an experimental Atlas sustainer variant trapped RP-1 in exhaust-manifold
pockets during fuel-rich cutoff, and LOX/RP-1 gel detonated at the start of the next test;
cryogenic propellants (LH2) evaporate between runs and don't have this failure mode. Real
Titan turbine-exhaust-impingement side loads on an ablative extension: **90±20 lbf axial,
360±50 lbf lateral**, inducing a ~250 ft-lbf vehicle roll moment — a real dimensioned load
case for any turbine-exhaust-impingement structural analysis.

**Real F-1-specific detail from Rocketdyne's own engine manual (2026-09-24)** `[F1-Man §1-15..
1-23, §1-61..1-72; Fig 1-5/1-7]` — closes the acquisition item `OPEN_QUESTIONS.md` had flagged
for this exact source. **Real film/mainstream temperature gap**: nozzle-extension film-coolant
(turbine exhaust) temperature is **1,138°F**, vs. local core-gas static temperature at the
16:1 exit plane of **1,922°F** — a real, quantified number not previously in `claude_lit`.
**Real construction detail**: the extension's inner wall is built from **23 rows of
overlapping shingles** (the real hardware behind the qualitative shingle description above).
**Real turbine-exhaust manifold hydraulics**: a CRES torus of *decreasing* cross-section
inlet-to-exit, **15 omega expansion joints**, inlet splitter plates + exit flow vanes
specifically for uniform gas distribution into the extension. **Real heat-exchanger
architecture — a third, richer example of the pressurization-heat-exchanger pattern**: the F-1
carries BOTH oxidizer coils (LOX→GOX, ox-tank pressurization) AND helium coils (chilled He,
fuel-tank pressurization) in one shell — distinct from H-1's/J-2's single-propellant-only
exhaust heat exchangers. **Real igniter-placement anchor**: nozzle-extension pyrotechnic
igniters sit near the **11:1 area-ratio plane** — a second independent real area-ratio anchor
alongside the 10:1→16:1 boundary above. **Caveat**: no F-1-specific version of the
"~25-30%-at-attachment" film-coolant split above was found in this manual — that number stays
sourced to `[SP-8120]` alone, not independently corroborated by the engine's own manual.

## Turbine-exhaust disposal hardware — the real H-1 aspirator, duct and heat exchanger
`[H1-Man §1-39..1-51 p.1-25..1-28, targeted read 2026-09-24]`

The Saturn I/IB H-1 is the only engine in this reference set whose turbine-exhaust *disposal
hardware* is described part by part. The two models differ **only** in their exhaust system.
- **H-1C (inboard, fixed)** routes the exhaust out overboard through a **curved stainless
  duct with a bellows**.
- **H-1D (outboard, gimbaled)** uses an **aspirator**: a welded **Hastelloy C shell** fitted
  over the aft ~**20 in** of the nozzle. It is welded to the forward channel band, and its aft
  end is free and extends past the exit. It leaves a **0.440 in annular clearance** over the
  fuel-return manifold, and the GG exhaust leaves through that slot into the exit flow stream.
  This is the "annulus-at-exit" pattern `[SP-8120]` gives for the Atlas sustainer.

Both routes pass the fuel-rich exhaust through a **turbine exhaust hood** (a bellows elbow),
then a **LOX→GOX heat exchanger**. That is a helix-wound, four-coil shell, with three coils in
use, heating GOX for vehicle pressurisation. The exhaust then reaches the aspirator or duct.
[SP-8120]'s Titan I also has an oxidiser superheater in its exhaust path, so an exhaust heat
exchanger is a common feature, not a one-off.

**Real turbine back-pressure anchor** `[H1-Man Fig 1-47]`:
- turbine inlet **599 psia total**, exit **33.8 psia**, so PR ≈ **17.7** (total inlet /
  static exhaust);
- efficiency 69.6 %, 4,007 bhp;
- GG flow **17.22 lb/s at O/F 0.346** (Fig 1-28), about **2.3 %** of total engine flow.

That exit pressure lies between Titan I's **30 psi** `[SP-8120]` and a choked sea-level exit.
It is consistent with the exhaust exit needing to stay sonic at sea level, which requires
roughly p_amb / 0.55 ≈ 27 psia before duct losses.

## A second real `nozzle_injection` anchor and a real LOX-pressurization heat-exchanger use — J-2 (2026-09-24)

`[RPE-J2Blog]` (a secondary/enthusiast source — see Caveats — but internally consistent and
independently useful for two real dimensioned hardware facts): the J-2's LOX-turbine exhaust
(after passing both turbines in series via an 8in-diameter crossover duct) dumps into the
nozzle through eyelets of **total area 115 in²** at area-ratio stations **10.45-11.40** — a
second real, dimensioned anchor for `physics/turbine_exhaust.py`'s `nozzle_injection` mode,
alongside the existing F-1 case above (different engine family, same architectural pattern:
inject turbine exhaust into the supersonic nozzle stream at a similar area-ratio band).
Separately, a real historical design feature **not currently modeled anywhere in
`engine_designer`**: the J-2's turbine-exhaust duct routes through a heat exchanger used to
boil LOX for vehicle LOX-tank pressurization — the same architectural pattern as the H-1's
GOX-pressurization heat exchanger above (and Titan I's oxidizer superheater), now a third real
example, corroborating that a turbine-exhaust-duct heat exchanger for tank pressurization is a
common feature across engine families, not a one-off — worth flagging as a possible future
`turbine_exhaust.py` feature idea (a pressurization-gas heat-pickup mode) if that module is
ever extended, though no citation exists yet for sizing one.

## Caveats

- One tiny, low-Pc engine (the `[TN-Dump]` propellant-dump-cooling test article). The
  *method* and *correlations* generalise; the coolant-fraction numbers (6.9–7.5 %) do not
  scale to a full-size high-Pc engine.
- The report notes its original transport-property data were later found incorrect and
  re-fitted for data reduction (`[TN-Dump]` ref. 2, Svehla NASA SP-3011).
- Dump cooling's real-world niche is narrow (pressure-fed LOX/LH2); most designs pick regen,
  film, or radiation instead.
- `[H1-Man]` gives aspirator **geometry only**: no aspirator thrust, entrainment or
  back-pressure number. Any aspirator Isp is a model anchored on that geometry.
- `[SP-8120]`'s F-1 turbine-exhaust film-cooling content is real-hardware precedent, not a
  closed-form film-cooling-effectiveness formula — the 25-30% attachment-region split was
  itself experimentally determined, not derived, and is specific to the F-1's own geometry
  (large separation distance between main/coolant streams). Treat as a real anchor point and
  design-driver narrative, not a directly portable design equation.
- `[RPE-J2Blog]` is a secondary/enthusiast-researcher compilation (Rocket Propulsion Evolution,
  enginehistory.org), not a primary NASA/Rocketdyne document, with no inline footnotes tying
  individual claims to specific sources — treat its two facts above as plausible real hardware
  color to corroborate against, one tier below `[SP-8120]`/`[H1-Man]`, not a citation of record
  for a physics constant on its own.
- `[F1-Man]` (Rocketdyne's own F-1 familiarization manual, R-3896-1, 1967) is a scoped read of
  a 262-page manual (engine-overview/thrust-chamber/turbopump/ignition/GG-heat-exchanger
  sections + Section III performance tables read in full; shipping/logistics/maintenance
  narrative and Section II's garbled weight/CG/wiring tables skimmed only). No F-1 turbine
  efficiency percentage was found in the sections read (unlike `[H1-Man]`'s 69.6% for the H-1)
  — flagged as an open item if ever needed.

## Implications for engine_designer

- The tool's `README.md` lists dump cooling as a covered *cycle-adjacent concept* only in
  the nozzle-extension material logic; there is **no dump-cooling model**. If one is added:
  - It is a *feed-pressure* benefit, not a thrust cycle — model it as **jacket ΔP moving
    from series (added to pump discharge / tank pressure) to parallel (only needs to exceed
    ambient + its own nozzle back-pressure)**. This is the opposite of the current
    `design.py` treatment where `JACKET_DP_PA` always adds to the feed budget.
  - Credit a small coolant-Isp contribution, analogous to `engine_isp_with_gg_dump` in
    `turbopump.py`: `Isp_engine = (1−x)·Isp_chamber + x·Isp_dump`, with the dump fraction
    `x ≈ 0.07` and `Isp_dump` from a heated-H2 expansion (up to ~510–560 s for a
    refractory-metal wall per `[TN-Dump Fig 1]`, i.e. `dump_isp_fraction` well above the
    0.55 used for GG dump — dumped hot H2 is a much better exhaust than GG bleed).
  - The `[TN-Dump]` recovery factor **0.88** and Dittus-Boelter `Nu = 0.023·Re^0.8·Pr^0.4`
    are directly reusable in any coolant-channel model (topic 06 implications).
- The "first ~3 in over-cooled" observation is independent empirical support for the
  combustion-completeness curve in `combustion.py` (topic 03) — heat flux near the injector
  is genuinely lower than a zero-length-combustion model predicts.
- **The planned turbine-exhaust-handling feature** (`OPEN_QUESTIONS.md`, plan
  `~/.claude/plans/floofy-dazzling-liskov.md`) now has real F-1 hardware data for its
  "nozzle injection as extension film coolant" mode: the real eps=10→16 cutoff, the real
  ~25-30%-at-attachment coolant-split finding, real materials (Hastelloy C/Inconel 625/
  347 CRES), and the real ~0.5%-of-total-thrust turbine-exhaust performance contribution.
  This resolves that plan's item (0) (SP-8120's Hot-Gas Manifold/§2.2.5.3 reading) and gives
  a real F-1-specific number set that partially substitutes for item (b) (the separate
  Rocketdyne F-1 Familiarization Training Manual, still not acquired) — the area ratio
  where exhaust is injected (10:1, not the plan's estimated "~10") and GG-flow-fraction
  context are now real-sourced. Report-only — no code changed; `design.GG_DUMP_ISP_FRACTION`
  remains unmodified.
- **A real, dimensioned turbine-exhaust structural load case** now exists (`[SP-8120]`'s
  Titan 90±20/360±50 lbf side loads, ~250 ft-lbf roll moment) if a future feature ever adds
  turbine-exhaust-manifold structural sizing — none exists in `mass_model.py` today.
- **`[H1-Man]` (2026-09-24) closes the "aspirator" gap** (`OPEN_QUESTIONS.md` item (g)).
  The aspirator is now real hardware with real geometry. The planned turbine-exhaust feature
  can model it as a **choked annular slot at the main-nozzle exit lip**, sized from GG flow
  and checked against the 0.440 in gap on the 45.62 in-exit H-1. The feature can also:
  - model the H-1C curved duct as the plain sonic overboard exit;
  - model the heat exchanger as an in-line temperature drop;
  - anchor the turbine back pressure on 599→33.8 psia (turbine inlet ≈ **0.87 × Pc**).

  Report-only; no code changed.
- **`turbine_exhaust.py`'s `nozzle_injection` mode now has a second real hardware anchor**
  (`[RPE-J2Blog]`'s J-2 eyelet geometry, 115 in² at eps 10.45-11.40) alongside the existing F-1
  case — two independent real engines using the same architectural pattern at a similar
  area-ratio band. Report-only — no code changed.
- **A candidate future feature, not yet actionable**: a turbine-exhaust-duct heat exchanger for
  tank pressurization (real on H-1/J-2/Titan I/F-1, above) has no counterpart in
  `turbine_exhaust.py` today — flagged for awareness, no citation yet exists for sizing one.
- **`OPEN_QUESTIONS.md` item (b) (Rocketdyne F-1 Familiarization Training Manual) is now
  RESOLVED (2026-09-24)** — acquired and distilled (`[F1-Man]`, above). Its real turbine-PR
  anchor (≈16.3 uprated/≈15.8 baseline) is folded into `topics/09-turbopumps.md`; its real
  tube-count/bypass-split numbers are folded into `topics/12b-structures-manifolds-and-hardware.md`; its
  real GG feed-pressure-budget chain is folded into `topics/10-gas-generators.md`. Report-only
  — no code changed.
- **Applied 2026-09-25** (`engine_designer` turbine exhaust, round 2):
  - F-1 injection back pressure: 58 psia `[F1-Man]` -> `EXHAUST_INJECTION_PRESSURE_RATIO`,
    interim. Per-engine manifold/slot physics is wanted (`OPEN_QUESTIONS.md`).
  - Corpus F-1 chamber MR 2.40 (not the engine-overall 2.27).
  - Plausibility probes: exhaust temperature vs the 1,138 °F extension coolant, and duct bore
    vs the ~24 in heat-exchanger outlet end. The model gives 24.3 in, the first check on
    `TURBINE_EXHAUST_DUCT_MACH`.
  - The injection torus is now tapered (decreasing section `[F1-Man §1-18]`).
  - See `engine_designer/plans/2026-09-25_turbine_exhaust_round2.md` for the gas-film law and
    heat-exchanger items that follow.
