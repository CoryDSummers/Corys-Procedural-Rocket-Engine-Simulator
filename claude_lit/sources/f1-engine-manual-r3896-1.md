# [F1-Man] — F-1 Rocket Engine Technical Manual, Engine Data

## Identity

- **Title**: Rocketdyne *F-1 Rocket Engine*, Technical Manual — Engine Data. Section I
  (Description and Operation), Section II (Interface Design Criteria / weights /
  instrumentation), Section III (Performance).
- **Report**: **R-3896-1** (Rocketdyne), originally issued **31 March 1967**, through
  **Change No. 12 (12 May 1972)**. Covers the uprated 1,522,000 lbf (sea level) F-1 as
  installed on Saturn V S-IC (five engines, 7,610,000 lbf cluster thrust).
- **File**: `literature/R3896-1_(Technical_Manual-Engine_Data)_F-1_Rocket_Engine_31_Mar_1967.pdf`
  (9.3 MB, 262 PDF leaves, scanned with an imperfect OCR text layer — numeric tables
  frequently interleave label and value columns out of physical print order; this note
  flags every place that reordering created ambiguity).
- **Extent read**: **scoped, not exhaustive** (2026-09-24), per this batch's brief. Read in
  full: the engine overview (§1-1..1-8), propellant feed system / thrust chamber assembly
  description (§1-9..1-23, incl. the tube-wall, injector, oxidizer-dome and nozzle-extension
  paragraphs), turbopump description (§1-24..1-39), ignition system (§1-55..1-60), the
  gas-generating system / GG / heat exchanger (§1-61..1-72), and Section III's nominal
  thrust-chamber/turbopump/heat-exchanger performance tables (Fig 3-13, 3-14, 3-20) plus
  the component-replacement performance-deviation table (Fig 3-45). **Skimmed only**:
  valve/duct/interface-panel hardware detail with no cooling/exhaust relevance (§1-40..1-54),
  thermal-insulation and purge/drain systems (§1-104..1-116), the entire logistics/shipping/
  maintenance-flow narrative (§1-134..1-255, largely irrelevant to `engine_designer`),
  Section II's wiring/instrumentation-tap tables and weight/CG charts (mostly OCR-garbled
  numeric tables or hand-drawn curves, not read as images), Section III's re-orificing
  formulas, engine-influence-coefficient tables (Fig 3-39) and start/stop valve-timing
  tables (narrative-adjacent, not physics-load-bearing for this tool). **Not read at all**:
  the Appendix (Manual Data Supplements, mostly change-log material).
- **Page reference**: printed page numbers (`1-6B`, `3-7`, ...) are the manual's own,
  appearing in the OCR footer of each leaf; paragraph numbers (`1-14`, `3-38`) are the
  manual's own numbered-paragraph scheme.

## Character

A field/engineering technical manual, structurally identical in kind to `[H1-Man]` (same
Rocketdyne report-numbering family, `R-36xx`/`R-38xx`) but far more complete for the F-1:
where `[H1-Man]` was only a *targeted* read closing specific gaps, this manual's Section I
gives a genuine part-by-part hardware description of the entire thrust chamber, turbopump
and gas-generating system, and Section III gives real tabulated nominal performance values
(not just one operating point) plus real component-swap performance-sensitivity data. It
supersedes `[SP-8120]`'s F-1 nozzle-extension narrative with much more physical construction
detail, and gives the F-1's own turbine/GG operating point directly (previously only
`[H1-Man]`'s H-1 and `[SP-8120]`'s qualitative F-1 mentions existed in `claude_lit`).

## Key parameters

| Parameter | Value | Where |
|---|---|---|
| Sea-level thrust (rated) | 1,522,000 lbf | Fig 1-5, p.1-6 |
| Sea-level Isp | 265.3 s (265.1 s baseline) | Fig 1-5 / Fig 3-1 |
| Engine (overall) mixture ratio | 2.27:1 | Fig 1-5, §1-8 |
| Thrust-chamber-only mixture ratio | 2.40:1 | Fig 1-7, p.1-8 |
| Total propellant flow | 5,737 lb/s (fuel 1,756 + ox 3,981) | Fig 1-5 |
| Thrust-chamber-only flow | 5,569 lb/s (ox 3,933 + fuel 1,636) | Fig 1-7 |
| Chamber (injector-end) pressure | 1,125 psia | Fig 1-5/1-7 |
| Chamber gas (stagnation) temperature | 5,970°F | Fig 1-5/1-7/3-13 |
| Throat gas static temperature | 5,328°F | Fig 3-13, p.3-7 |
| Nozzle exit (16:1) gas static temperature | 1,922°F | Fig 3-13 |
| Nozzle expansion ratio | 10:1 (regen chamber) → **16:1** (full, w/ extension) | Fig 1-7, §1-4 |
| Nozzle exit pressure (16:1, sea level) | 9.6 psia | Fig 1-5/1-7 |
| Engine envelope | ~12.5 ft dia × 19.2 ft long, ~18,600 lb dry | §1-5 |
| **Primary chamber tubes** | **178**, 1-3/32 in OD Inconel-X, hydraulically formed, above the 3:1 area-ratio plane | §1-15, p.1-8 |
| **Secondary chamber tubes** | **356**, 1 in OD, same material, from 3:1 to 10:1 plane; 2 secondary tubes brazed to each primary tube at the 3:1 splice | §1-15/1-16 |
| **Regen coolant (fuel) split at fuel-down tube** | **30%** bypasses direct to injector manifold (orificed plug above the inlet slot); **70%** continues down for regenerative cooling, returns via the fuel return manifold + adjacent fuel-return (fuel-up) tubes | §1-16, p.1-8 |
| Jacket (fuel) prefill volume | 105 gal (ethylene glycol solution, 103-105 gal capacity) | Fig 1-7/3-13 |
| Jacket pressure drop | 244 psia (Fig 1-7) / 265→242 psid (Fig 3-13, baseline→MD128/174) | Fig 1-7/3-13 |
| Injector pressure drops | oxidizer 309 psia, fuel 97 psia (Fig 1-7); oxidizer 312 psid, fuel 96 psid (Fig 3-13) | Fig 1-7/3-13 |
| **Nozzle-extension (turbine-exhaust film) inner-wall shingles** | **23 rows** of overlapping shingles forming the inner wall, creating injector slots | §1-23, p.1-9B |
| **Turbine exhaust manifold** | CRES torus, decreasing cross-section inlet→exit, **15 omega expansion joints**, inlet splitter plates + exit flow vanes for uniform distribution; welded to a flame shield welded to the chamber outer wall | §1-18, p.1-9A |
| Nozzle-extension coolant (turbine exhaust) gas temperature | 1,138°F | Fig 1-5/1-7 |
| GG combustor pressure (injector end) | 980 psia | Fig 1-27 |
| GG mixture ratio | **0.416:1** | Fig 1-27 |
| GG combustor temperature | 1,453°F | Fig 1-27 |
| **GG total flow** | **167 lb/s** (fuel 118 + ox 49); a second table gives 172 lb/s at the turbine | Fig 1-27 / Fig 3-14 |
| GG combustor pressure drop | 33.5 psia | Fig 1-27 |
| GG injector pressure drops | oxidizer 250 psia, fuel 145 psia | Fig 1-27 |
| GG ball-valve pressure drops | oxidizer 55 psia, fuel 200 psia | Fig 1-27 |
| GG orifice pressure drops | oxidizer 261 psia, fuel 375 psia | Fig 1-27 |
| GG line pressure drops | oxidizer 76 psia, fuel 43 psia | Fig 1-27 |
| GG envelope / weight | 18×24×28 in, ~220 lb | §1-64 |
| **Turbine inlet temperature** | **1,453°F** | Fig 1-16/3-14 |
| **Turbine inlet pressure (total)** | **945 psia** (MD128/174-uprated engines); **918 psia** baseline | Fig 3-14, p.3-7 |
| **Turbine exit (static) pressure** | **58 psia** | Fig 1-16/3-14 |
| Turbine brake horsepower | 53,146 bhp (uprated) / 52,926 bhp (baseline) | Fig 1-16/3-14 |
| Turbine/pump shaft speed | 5,492 rpm (uprated) / 5,488 rpm (baseline) | Fig 1-16/3-14 |
| Turbopump weight / length / diameter | 3,150 lb / 5 ft / 4 ft | Fig 1-16 |
| Oxidizer pump inlet / discharge pressure | 65 / 1,602 psia | Fig 1-16/3-14 |
| Fuel pump inlet / discharge pressure | 45 / 1,870 psia | Fig 1-16/3-14 |
| Oxidizer/fuel pump required power | 30,270-30,332 / 22,656-22,814 bhp | Fig 3-14 |
| Bearing coolant flow (parallel / series system) | 5.5 / 3.5 gpm | Fig 1-16 |
| Heat exchanger envelope | 43 in dia max (40 in at turbine outlet → 24 in at turbine exhaust manifold), 58 in long | §1-72 |
| Heat exchanger coils | **oxidizer coils AND helium coils** (both, in one shell) | §1-71/1-72, Fig 1-31 |
| Heat-exchanger LOX/He flow (nominal test-eval input) | LOX 4 lb/s (-288°F in → 470°F out); He 0.6 lb/s (-345°F in → 255°F out) | Fig 3-29, p.3-26 |
| Heat exchanger duty | boils LOX coils → GOX (oxidizer tank pressurization); chills helium coils (expanded for fuel-tank pressurization) | §1-62/1-72 |
| Injector | CRES 31-ring plate-type: 16 fuel + 15 oxidizer ring grooves alternating; 13 compartments (2 circular + 12 radial baffles) | §1-19, p.1-9A |
| Injector fuel/oxidizer rings | 14 copper fuel rings (fuel-on-fuel doublet impingement) + 2 circular fuel-cooled copper baffles; 15 copper oxidizer rings (ox-on-ox doublet) + 12 radial fuel-cooled copper baffles | §1-19 |
| Ignition system | 5 igniters per start: 2 pyrotechnic (GG), 2 pyrotechnic (nozzle extension, near the **11:1** area-ratio plane), 1 hypergol (main chamber) | §1-56/1-60 |
| Hypergol igniter charge | 403 ± 10 g pyrophoric fluid, 85% triethylborane / 15% triethylaluminum; burst diaphragms 350(+25,-75)/500(+25,-75) psig | §1-58 |

## Key results — thrust chamber and tube-wall regen jacket (§1-11..1-23, p.1-6B..1-9B)

- **The real F-1 tube count and split point, with a real bypass fraction.** The chamber
  is **178 primary tubes** (1-3/32 in OD Inconel-X) above the 3:1 area-ratio plane
  (~30 in below the throat centerline plane), splicing to **356 secondary tubes** (1 in OD,
  same alloy) from 3:1 down to the 10:1 plane, with 2 secondary tubes brazed to each
  primary tube at the splice. This corroborates and sharpens `[SP-8087 Table III]`'s
  existing F-1 Inconel-X/0.018-in-wall anchor with real tube diameters, counts and the
  exact splice-plane area ratio.
- **A real, dimensioned regen bypass-fraction anchor.** Every other primary tube is a
  "fuel-down" tube, slotted at the fuel-inlet-manifold end; an **orificed plug** diverts
  **30%** of that tube's fuel straight to the fuel injector manifold (bypassing the
  jacket), while the remaining **70%** continues down the tube for regenerative cooling,
  turns at the fuel return manifold, and comes back up through the adjacent "fuel-up"
  return tubes to the injector manifold. This is a real, primary-source number for
  `manifold.py`'s bypass-fraction physics (`ASSUMPTIONS.md`'s "manifold bypass-fraction"
  check) — a genuinely new data point beyond anything in `[SP-8087]`/`[Fagherazzi-2019]`.
- **The turbine exhaust manifold**, feeding the nozzle extension, is a **CRES torus of
  decreasing cross-sectional area** (inlet to exit) with **15 omega expansion joints**
  for thermal growth, **splitter plates at the inlet** and **flow vanes at the exit**
  specifically "to contribute to the uniform distribution of the exhaust gases into the
  nozzle extension." It is welded to a flame shield, itself welded to the thrust chamber's
  outer wall. This is real hot-gas-manifold hydraulic-design detail (splitters + exit
  vanes for maldistribution control) directly relevant to `[SP-8120]`'s and
  `[SP-8087]`'s manifold-hydraulics material, now with an F-1-specific implementation.
- **The nozzle extension's inner wall is built from 23 rows of overlapping shingles**,
  and the "injector slots" that inject turbine-exhaust film coolant into the main stream
  are the gaps this overlap creates — a concrete construction detail behind `[SP-8120]`'s
  "shingle" narrative (`[SP-8120]` names the shingle concept and its dimpled-sheet fix;
  this manual gives the real row count on the actual F-1 production article). Outer/inner
  walls are nickel-base alloy, separated by Z-sections, with CRES reinforcing channel
  bands (hatbands) on the outer wall.
- **Nozzle-extension film-coolant (turbine exhaust) temperature is 1,138°F**, entering the
  cavity between the double walls, while the **local core-gas static temperature at the
  16:1 exit plane is 1,922°F** (isentropically expanded down from the 5,970°F/5,328°F
  stagnation/throat-static chamber gas) — i.e. the film runs roughly 800°F below the local
  free-stream static temperature it's shielding the wall from, a real quantified
  film/mainstream temperature gap for this specific engine and area ratio, not previously
  in `claude_lit`.
- **A real engine-level vs. chamber-level mixture-ratio split**: engine (overall) MR is
  2.27:1 but thrust-chamber-only MR is 2.40:1, because the fuel-rich (MR 0.416) GG bleed
  dilutes the blended engine ratio. A clean, real illustration of the GG-bleed MR-dilution
  effect already modeled qualitatively in `engine_cycles`/`gas_generators` topics.
- **Nozzle-extension pyrotechnic igniters sit near the 11:1 area-ratio plane** — a second,
  independent real area-ratio anchor (alongside `[SP-8120]`'s already-cited 10:1→16:1
  regen/extension boundary) for where combustion/reignition activity happens on the real
  F-1 nozzle-extension film.

## Key results — gas generator, turbine and heat exchanger (§1-24..1-39, §1-61..1-72)

- **A real F-1 turbine back-pressure anchor, independent of `[H1-Man]`'s H-1 number.**
  Turbine inlet **945 psia total** (uprated MD128/174 engines; 918 psia baseline) against
  a turbine exit **58 psia static**, giving **PR ≈ 16.3** (uprated) or **≈15.8**
  (baseline) — comparable to, but distinct from, the H-1's 599→33.8 psia (PR ≈17.7)
  `[H1-Man]`. Two independent real fleet data points now exist for GG/turbine PR at
  similar (~1,000-1,500 psia GG Pc) scale.
- **GG mixture ratio 0.416:1** (fuel-rich LOX/RP-1), combustor temperature 1,453°F,
  combustor (injector-end) pressure 980 psia, with a full real pressure-drop breakdown:
  injector ΔP (ox 250/fuel 145 psia), ball-valve ΔP (ox 55/fuel 200 psia), calibration
  orifice ΔP (ox 261/fuel 375 psia), and line ΔP (ox 76/fuel 43 psia) — a complete,
  real GG feed-pressure-budget chain, richer than `[SP-8081]`'s generic GG design tables
  for this specific real engine.
- **GG total flow 167 lb/s is 2.91% of total engine flow (5,737 lb/s)** — computed here,
  not printed directly. This differs from `[H1-Man]`'s H-1 GG fraction (2.26-2.31%),
  giving a second real fleet data point for GG-bleed-fraction scaling and corroborating
  that fuel-rich GG bleed fraction is engine-specific, not a fixed universal constant.
- **The F-1 heat exchanger has BOTH oxidizer coils AND helium coils in one shell** — a
  genuinely new architectural fact vs. `[H1-Man]`'s H-1 heat exchanger (LOX→GOX only,
  no helium) and vs. the J-2's LOX-only exhaust heat exchanger noted via `[RPE-J2Blog]`.
  The oxidizer coils boil LOX to GOX for oxidizer-tank pressurization; the helium coils
  chill/expand helium for fuel-tank pressurization. Envelope: 43 in dia (tapering 40→24 in
  turbine-outlet-to-manifold end) × 58 in long. This is a third real "turbine-exhaust-duct
  heat exchanger" example (after H-1/J-2), now with the added helium-circuit variant —
  strengthens the case (already flagged in `topics/07-dump-cooling.md`) that a
  pressurization-gas heat-pickup mode is a common real architecture, not a one-off.
- **A real, dimensioned thrust-vector sensitivity to nozzle-extension/injector
  replacement** (Fig 3-45, component-replacement deviations): swapping the nozzle
  extension can shift thrust vector up to 0.31 in lateral / 2.8 min angular; combined
  injector+extension replacement is bounded at 0.42 in / 21.0 min. Swapping the "Turbine
  Exhaust System Duct With Heat Exchanger" carries a real ±27.0 kilo-lb thrust, 0.003 MR,
  0.66 s Isp deviation budget; nozzle-extension replacement alone carries ±15.0 kilo-lb
  thrust / 0.60 s Isp. These are real hardware-tolerance/build-variation numbers, not
  physics constants, but a useful sanity check on how much a real turbine-exhaust-hardware
  swap can move headline performance.

## Design method

This is a description/data manual, not a design-derivation textbook — it gives real
hardware numbers and operating points, not sizing equations (Section III's re-orificing
and influence-coefficient material is a *test-data-correction* method, not a from-scratch
design method, and was only skimmed). Treat every number above as a real, cited anchor
point, not a transferable formula.

## Section map (printed pages)

- §1-1..1-8 engine overview, physical description (p.1-1)
- §1-9..1-13 propellant feed system / thrust chamber assembly description (p.1-6B)
- Fig 1-5/1-5A engine leading particulars / performance schematic (p.1-6/1-6A)
- §1-14..1-16 thrust chamber body description — tube counts, bypass split (p.1-8)
- Fig 1-7 thrust chamber leading particulars (p.1-8)
- Fig 1-8 thrust chamber and nozzle extension (photo/diagram, p.1-9)
- §1-17..1-19 fuel inlet manifold, turbine exhaust manifold, injector description (p.1-9A)
- §1-20..1-23 oxidizer dome, gimbal bearing, nozzle-extension description (p.1-9B)
- §1-24..1-39 turbopump description (oxidizer pump, fuel pump, turbine, seals) (p.1-11..1-18)
- Fig 1-16 turbopump leading particulars (p.1-16)
- §1-55..1-60 ignition system (igniters) (p.1-21..1-24)
- §1-61..1-68 gas-generating system, GG, GG ball valve, GG injector/combustor (p.1-25..1-28)
- Fig 1-27 GG leading particulars (p.1-25)
- §1-71/1-72 heat exchanger description (p.1-29)
- Fig 3-1 nominal engine performance values at sea level (p.3-1)
- Fig 3-13/3-14 nominal thrust-chamber/turbopump performance values (p.3-7)
- Fig 3-20 nominal heat-exchanger performance values (p.3-14)
- Fig 3-29 heat-exchanger performance evaluation/prediction input data (p.3-26)
- Fig 3-39 engine influence coefficients (skimmed only, p.3-40)
- Fig 3-45 deviations in engine performance due to component replacement (p.3-51/3-53)

## Caveats

- **This is a scoped read, not exhaustive.** Section II (weights/CG/instrumentation-tap
  tables, mostly hand-drawn charts or garbled numeric tables) and most of the
  logistics/maintenance narrative in Section I (§1-134 onward) were skimmed only, per the
  brief; a future targeted read could still mine Section II's real weight/CG table if
  needed.
- **OCR table-reordering risk, same pattern as `[H1-Man]`.** Fig 3-13/3-14's parameter/
  value pairs occasionally interleave two adjacent parameters' labels and values (e.g. a
  "Thrust chamber wall temperature at throat" row appears immediately beside the
  1,138°F nozzle-extension-coolant value already independently confirmed in Fig 1-5/1-7 —
  this note deliberately did **not** cite a throat-wall-temperature number from Fig 3-13
  because the OCR order made it impossible to confirm which figure it truly belongs to).
  Treat any number from a dense two-column Section III table as provisional unless it is
  corroborated by a cleaner narrative-paragraph statement elsewhere in the manual (as done
  above for every number that is cited).
- **No turbine efficiency percentage was found for the F-1** (unlike `[H1-Man]`'s 69.6%
  for the H-1) in the sections read; only bhp, inlet/exit conditions and flow are given.
  A future read of Fig 1-16/3-14's full context or Section II might close this.
- **No explicit GG-gas mass fraction directed to the nozzle-extension film vs. any
  overboard/other path is stated** — the manual describes all GG/turbine exhaust as
  routed to the nozzle extension via the turbine exhaust manifold (no aspirator- or
  duct-style overboard option exists on the F-1, unlike the H-1's two exhaust-disposal
  variants) but gives no fraction split within the extension's own coolant flow (i.e. no
  F-1-specific version of `[SP-8120]`'s "~25-30% at the attachment region" split is stated
  here — that number remains sourced to `[SP-8120]` alone).
- Some figures (Fig 1-5A performance schematic, Fig 2-9 series heat-exchanger flow/
  temperature charts) are hand-drawn charts whose OCR text is scattered axis-label
  fragments, not usable as citable numbers; they were not re-rendered as images for this
  batch given the volume of clean narrative/tabular text already available elsewhere in
  the manual.
- Weight/dimension figures for the whole engine (18,600 lb dry, 12.5 ft dia × 19.2 ft
  long) are well-known public figures, included here only for completeness/cross-check,
  not as a novel finding.
