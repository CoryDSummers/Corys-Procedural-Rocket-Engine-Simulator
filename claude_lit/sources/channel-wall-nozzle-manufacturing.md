# Gradl & Protz (NASA MSFC) — Channel Wall Nozzle Manufacturing Technology Advancements

## Identity

Paul R. Gradl and Dr. Christopher S. Protz (NASA Marshall Space Flight Center, Propulsion
Systems Department, Component Technology Development/ER13), "Channel Wall Nozzle
Manufacturing Technology Advancements for Liquid Rocket Engines," IAC-19-C4.3.5x52522,
70th International Astronautical Congress, Washington D.C., 21-25 October 2019.
`literature/IAC-19-C4.3.5x52522 - Channel Wall Nozzle Manufacturing Technology Advancements.pdf` (NTRS 20190033314; 16 PDF pages, cleanly OCR'd/text-native — no scan-quality
issues). U.S. Government work, public domain. Tag: `[ChannelWall-IAC19]`.

## Character

A manufacturing-process survey and hot-fire test-campaign summary paper, not a heat-transfer
or structural-design-method paper. Its subject is entirely **how** channel-wall nozzles get
built (additive manufacturing, machining, bonding techniques and the materials used with
each), not how they're thermally/structurally sized. No equations, no heat-flux
correlations, no coolant-side design method anywhere in the text — every design-relevant
number in this source is a real anchor point (test Pc/MR/duration/wall-temperature/material)
rather than a derivable formula. Short and fully readable in one pass; no chart-only/OCR
loss (unlike `[Wieseneck-J2]`/`[Marquardt-5981]`).

## Key results

**Five NASA-prioritized CWN fabrication technologies** `[ChannelWall-IAC19 p.3]`, matching
`cooling.py`'s `WALL_CONSTRUCTIONS` category boundary but describing HOW a milled_channel
wall gets manufactured/closed-out, not a new wall-construction category itself:
1. **Laser Wire Direct Closeout (LWDC)** — a wire-fed laser deposition process that welds a
   filler wire directly across the open channel span while the nozzle rotates, forming the
   structural closeout jacket and sealing the channels in one operation, no channel filler
   material or separate jacket needed. Explicitly framed as eliminating the "tight tolerance
   structural jacket and additional operations compared to traditional manufacturing, such
   as **brazing** or structural plating closeout" `[p.4]`.
2. **Blown Powder Directed Energy Deposition (DED)** — coaxial laser + powder-blown melt
   pool, robot/gantry-driven; used both for near-net-shape liner/manifold preforms AND
   (the paper's main current focus) for building a **monolithic nozzle with fully integral
   coolant channels in a single AM build** — no separate liner + closeout + bonding step at
   all.
3. **Arc-based DED** — pulsed-wire MIG-welding-based, coarser features/larger deposited
   bead than laser DED, but higher deposition rate; used for liner/jacket preforms in
   Inconel 625, Haynes 230, JBK-75.
4. **Water Jet Milling (WJM)** — a *subtractive*, non-AM channel-forming technique: a blind
   high-pressure abrasive water-jet process (with industry partner Ormond LLC) that mills
   the channels into a preformed liner, explicitly compared against traditional slitting-saw
   slotting. Advantages cited `[p.6-7]`: can cut channel shapes slotting cannot (bifurcated
   channels, dovetail channels for bond enhancement, integral turnarounds, integral
   instrumentation ports), lower cutting load enabling thinner-walled channels, faster on
   hard-to-machine superalloys, and — notably — WJM inherently produces **squared channel
   ends** at the liner extremities, where traditional slitting-saw slotting leaves a rounded
   end requiring a secondary end-mill operation to square (relevant to cooling coverage at
   the nozzle's forward/aft boundaries). Earlier WJM process iterations produced *tapered*
   channel sidewalls (narrower near the hot wall — a cooling concern, since it reduces
   coolant contact area exactly where flux is highest); this was fixed in later process
   development to produce square, perpendicular sidewalls matching slotting practice.
5. **Explosive Bonding / Explosive Welding (EXW)** — a solid-state bonding process (flyer
   plate accelerated by explosive charge into a backer, kinetic-energy bond, self-cleaning
   via a stripping plasma jet at the bond interface) used for **dissimilar-metal (bimetallic)
   axial hotwall joints** and channel closeout; cited advantages are low tooling cost,
   looser closeout-shell tolerances than brazing, and scalability to large conical nozzle
   shapes.

**Material catalog for CWN liners/closeouts, with rationale** `[ChannelWall-IAC19 Table 1,
p.8]`: Inconel 625 (high strength, easily weldable, non-hydrogen service), Haynes 230 (high
temp + strength, oxidation resistance), SS347 (good H2 resistance, lower strength/cost),
JBK-75 (an A-286 derivative, good H2 resistance, lower density, high strength, "high-strength
hydrogen resistant material... with good weldability characteristics desired for additive
manufacturing" `[p.7]`), **NASA HR-1** (derived from JBK-75, "excellent hydrogen resistance,
high strength, and readily weldable" — the alloy NASA is carrying forward into its larger
RAMPT-project CWN work `[p.11]`), and **C-18150 (Cu-Cr-Zr)** as the copper-alloy liner
choice for bimetallic (high-heat-flux hotwall) designs, paired with a Monel 400 or Inconel
625 closeout jacket in the LWDC bimetallic builds. This is a useful cross-check set for
`turbopump_materials.py`/chamber-material catalogs beyond the GRCop-84/NARloy/CuCrZr set
already covered elsewhere in `claude_lit`.

**Bimetallic (radial and axial) construction concept** `[ChannelWall-IAC19 p.4]`: explicit
description of two bimetallic strategies — *radial* bimetallic (copper-alloy liner along the
full nozzle length, dissimilar-material structural jacket/closeout over it) vs. *axial*
bimetallic (copper alloy only at the forward, highest-heat-flux end of the nozzle, then an
axial transition to a lower-conductivity, higher-strength/weight material further downstream
where flux has dropped enough to tolerate it). This axial-transition concept is directly
relevant to `EngineDesign.regen_nozzle_end_eps`'s "bell-material transition" cutoff logic —
this paper gives a real, named manufacturing precedent (explosive-bonded or LWDC axial
joints) for exactly that kind of downstream material changeover, though it gives no
eps/area-ratio number for where the transition should occur.

**Real hot-fire test anchors** `[ChannelWall-IAC19 §3, p.8-10, Table 2]`: 9 subscale nozzles
(~2 klbf thrust class TCA at MSFC Test Stand 115) tested Dec 2017-Jun 2019, 229 tests total,
10,142 s accumulated. Real operating envelope reached: **Pc up to 1,240 psig (LOX/RP-1,
DED Inconel 625 nozzle) and up to 1,225 psig (LOX/GH2, LWDC bimetallic)**; mixture ratios up
to **MR 8.0** (deliberately extreme, durability-stress test) and up to **MR 6.6** in the
initial LOX/GH2 series; continuous single-burn durations of **180 s (LOX/GH2)** and **60 s
(LOX/RP-1)**; cyclic multi-start testing at **30 s burn / 25 s purge, 7 cycles**. Measured
**peak hotwall temperature ~1,350°F for the RP-1-cooled Inconel 625 integral-channel DED
nozzle and ~1,300°F for the GH2-cooled JBK-75 nozzle** `[Fig. 16, p.10]`, both peaking near
the forward (highest-heat-flux) end of the nozzle — real, flight-relevant wall-temperature
numbers for Inconel-625/JBK-75-class nozzle-extension alloys under GOX-rich real-propellant
conditions, usable as an additional real-engine-style anchor for
`cooling.py`'s wall-temperature-limit checks on those alloys (which currently mostly cite
Huzel/Sutton generic material limits, not a real regen-nozzle test data point at this
specific alloy/temperature combination). No Pc/MR/Isp/thrust design-point table for a named
flight engine, though — this is test-article data on a fixed generic contour, not a
production-engine spec sheet.

**Cumulative durability results**: JBK-75 DED integral-channel nozzle: 114 hot-fire starts,
4,170 s, LOX/GH2. Inconel 625 DED integral-channel nozzle: 28 starts, 1,072 s, LOX/RP-1 (Pc
up to 1,240 psig). LWDC monolithic nozzles (Inconel 625/Haynes 230/SS347): 15 starts, 1,400
s. LWDC bimetallic nozzles (C-18150 liner/Monel 400 or Inconel 625 closeout): 72 starts,
3,500 s. All nozzles reported leak-free and undamaged after every test — a real
demonstrated-durability data point for AM/LWDC-built regen hardware, not a failure-mode
finding.

**Manifold content is present but only at the "process step" level, not sizing detail**
`[ChannelWall-IAC19 p.9, Fig. 12-13]`: subscale nozzles were built as 3-piece assemblies
(DED/LWDC channel-closed-out liner + a separately-fabricated forward manifold + aft
manifold), joined by electron-beam (EB) welding with final-machined interfaces. Blown Powder
DED is also cited as being explored for direct manifold fabrication (Fig. 2's process-tree
lists "Direct build and/or simplified attachment of manifolds" as a design driver, and Fig. 7
shows a DED-built nozzle manifold preparation). This is fabrication-process content only —
no manifold cross-section, flow-area, coolant-distribution-ring geometry, or sizing method of
any kind (nothing usable for `manifold.py`'s `size_jacket_manifolds`).

## Design method

Not applicable — this is a manufacturing-process and test-campaign survey, not a derivation
or sizing-method source. No heat-flux correlation, no structural formula, no coolant-channel
sizing rule anywhere in the text.

## Section map

- p.1 (Abstract/Intro): overview of CWN manufacturing challenge and AM technology framing —
  read.
- p.2 (§1 Introduction, Fig. 1): CWN cross-section terminology (inner liner, coolant channel
  lands/ribs, closeout and jacket, hotwall/coldwall) — read.
- p.3-4 (Fig. 2, taxonomy): full process-tree of liner forming / slotting / closeout-jacket /
  manifold fabrication options considered — read.
- p.4-6 (§2.1 LWDC): Laser Wire Direct Closeout process description, monolithic vs bimetallic
  — read.
- p.6 (§2.2 Blown Powder DED): coaxial laser-powder DED, integral-channel focus — read.
- p.6-7 (§2.3 Supporting technologies): arc-based DED, Water Jet Milling, explosive bonding —
  read.
- p.7-8 (§2.4 Material Selection, Table 1): full material catalog and rationale — read.
- p.8-10 (§3 Hot-fire Testing, Table 2, Fig. 12-16): test-campaign summary, Pc/MR/duration/
  wall-temperature real data — read.
- p.10-12 (§4 Current and Future Development): scale-up to 35 klbf and half-scale RS-25-size
  (~44" dia) hardware, RAMPT project — read.
- p.12 (§5 Conclusions): summary, no new data — read.
- p.13-16 (Acknowledgements, References [1]-[27]): citation list only, not read for content
  (secondary sources not independently pulled).

## Caveats

- **This paper does NOT address Russian/Soviet "sandwich" wall construction.** Checked
  specifically per the open gap noted in `claude_lit/topics/06-cooling-and-heat-transfer.md`
  (the paragraph on the never-found diffusion-bonded/brazed corrugated-core Soviet
  multi-channel wall). This is a *different* technology entirely: modern NASA/U.S.-industry
  **additive-manufacturing and water-jet-milling** processes for building milled-channel
  (`milled_channel` in `cooling.py`'s `WALL_CONSTRUCTIONS`) and tube-adjacent bimetallic
  walls circa 2012-2019. No corrugated/finned-core sandwich geometry, no diffusion-bonding-
  of-a-stamped-core process, and no Russian engine or Russian manufacturing practice is
  mentioned anywhere in the text. The Russian-sandwich-wall gap remains open after this
  source; a Russian-specific source is still needed to fill it.
- **No heat-transfer or structural design method** — every number here is a manufacturing-
  process description or a real test-campaign data point (Pc, MR, duration, wall temp), not
  a derivable correlation. Cannot be used to validate or calibrate `cooling.py`'s Bartz
  h_g / wall-temperature solve the way `[Huzel]`/`[Sutton]` or the Bartz-calibration real
  engines are used.
- **Test-article data, not a named production engine** — the 9 subscale nozzles tested here
  are generic ~2 klbf-class research hardware on a fixed chamber contour, not a flight
  engine with a public spec sheet; cannot be added to `physics/validate.py`'s `SPOT_CHECKS`
  (no Isp/thrust/eps design-point to reproduce), only used as a qualitative wall-temperature/
  operating-envelope anchor.
- **JBK-75/NASA HR-1 are not yet in `turbopump_materials.py`'s or any other catalog** in
  `engine_designer/` (unconfirmed without checking, but likely a gap) — this source gives a
  materials-selection rationale (H2 resistance vs. strength vs. weldability) that could seed
  a future addition if those alloys are wanted as nozzle-liner/closeout choices, but this
  paper alone doesn't give quantitative mechanical/thermal properties (yield strength, k,
  CTE) for either — only qualitative "good/excellent hydrogen resistance" language. A
  materials-property source (e.g. its own reference [15], Chen/Panda/Bhat 1994 on NASA HR-1)
  would be needed for numeric properties.
- Single-team (NASA MSFC) authorship, IAC conference paper (not journal-peer-reviewed at the
  same bar as an AIAA journal article) — treat as credible NASA-program-status reporting, not
  an independently-validated design-criteria document.

## Regen passage geometry data (2026-09-23 re-read)

Full-text keyword search of all 16 leaves (channel width/height/depth, land, rib, hotwall
thickness, aspect, coolant, in./mm, RS-25/SSME/J-2X/RL10/RS-68/Vulcain). **Null result**: the
paper gives no channel count, width, depth, land width, hot-wall thickness, coolant flow,
coolant inlet/outlet T or P, or coolant velocity for either its subscale test nozzles or any
flight engine, and names no flight engine's channel-wall nozzle. Only qualitative geometry:
Fig. 1 labels (inner liner / hotwall / coolant channel / lands (ribs) / closeout-jacket /
coldwall) `[ChannelWall-IAC19 p.2]`; WJM early process gave tapered sidewalls (narrower at the
hotwall), later squared `[p.6]`. The existing hot-wall temperatures (~1,350 °F / ~1,300 °F,
Fig. 16 p.10) remain the only numbers here relevant to the coolant-side model.
