# NSMMS 2018 — Copper-Diamond Rocket Engine Liner Materials

## Identity

Biliyar N. Bhat (NASA Marshall Space Flight Center), Sion M. Pickard and Todd G. Johnson
(Global Technology Enterprises, Inc.), *Development of New Rocket Engine Liner Materials
Based on Copper Alloys with Diamond Particle Additions*, presented at NSMMS (National Space
& Missile Materials Symposium), June 27, 2018. `literature/NSMMS 2018 - Rocket Engine Liner
Materials Copper-Diamond Alloys.pdf` (NTRS accession 20180005537; 24 printed pages, 1:1 with
PDF page number — no offset). Tag: `[CuDiamond-Liner]`.

## Character

A short (24-page) conference-symposium paper, not a NASA numbered report — a status/overview
paper on an **early-TRL (research-stage) material family**: copper-diamond (Cu-D) particulate
composites, pitched explicitly as a **"next-generation"** successor to NARloy-Z and GRCop-84
for regeneratively-cooled combustion-chamber liners. No real engine has flown or even been
hot-fire-tested with a full Cu-D liner — the most advanced hardware demonstrated is a
sub-scale diffusion-bonded ring assembly (Figs. 9–12) and coupon-level thermal-cycling/tensile
testing. Authors are the actual NASA MSFC / GTE materials-development team (Bhat co-authored
the 2013 JANNAF paper that started this work; GTE's Pickard supplied most of the primary
thermal-conductivity/thermal-cycling data cited here from in-house testing, Refs. 5, 6, 9).

Structure: §1 Introduction (motivation: raise thermal conductivity beyond alloyed copper
without sacrificing high-temperature strength/creep resistance), §2 Thermal conductivity
modeling (differential-effective-medium/Bruggeman-Hasselman theory, phonon-scattering acoustic-
impedance-matching theory for interface coatings), §3 Processing (powder selection, diamond
coating selection, mixing, hot pressing vs. spark plasma sintering/FAST, machining, additive
manufacturing), §4 Properties (tensile, thermal conductivity, density, thermal-cycling
behavior — **the numeric core of this paper**), §5 Fabrication of Cu-D combustion chamber
liners (a real sub-scale SPS-diffusion-bonded ring-stack liner built at Penn State, plus a
discussion of additive-manufacturing compatibility piggybacking on MSFC's existing GRCop-84
SLM/DMLS chamber work), §6 Summary. 13 references, several unpublished/in-house (JANNAF
conference papers, an unpublished NASA Ames report, GTE in-house data 2014–2016) — this paper
itself is largely a synthesis of that underlying primary work, not first presentation of new
data in most cases.

## Key results — real material property numbers

**Baseline thermal conductivities for comparison** `[CuDiamond-Liner §3/§1 p.3]` (as-stated by
this paper, all "estimated" per its own wording):
- "Pure" copper (PM/consolidated route): **360 W/m·K** (can exceed 400 W/m·K for other forms)
- NARloy-Z (Cu-3wt%Ag-0.5wt%Zr): **320 W/m·K**
- GRCop-84 (Cu-8at%Cr-4at%Nb): **300 W/m·K** — stated as **25% lower than pure Cu** `[§1 p.2]`

**Cu-D composite thermal conductivity — the headline comparison** `[CuDiamond-Liner §4,
Table 5, p.11-12]`: measured (laser-flash, Netzsch Nanoflash LFA447) thermal conductivity for
various diamond volume fraction / matrix / processing combinations, at room temperature:

| Matrix | Diamond Vf% | Diamond size (µm) | Coating | Consol. method | k (W/m·K) |
|---|---|---|---|---|---|
| Pure Cu | 45 | 137 | refractory-carbide | electroplated, SPS | 438 |
| Pure Cu | 40 | 137 | refractory-carbide | powder-blend, hot press | 421 |
| Pure Cu | 55 | 192.5 | refractory-carbide | electroplated, SPS | 505 |
| Pure Cu | 55 | 273.5 | refractory-carbide | electroplated, SPS | **562** |
| Pure Cu | 40 | 273.5 | refractory-carbide | powder-blend, hot press | **563** (best in table) |
| NARloy-Z | 25.2 | 137 | none | powder-blend, SPS | 431 |
| NARloy-Z | 30.4 | 137 | none | powder-blend, SPS | 477 |
| NARloy-Z | 47 | 137 | none | powder-blend, SPS | 553 |
| NARloy-Z | 51 | 137 | refractory-carbide | powder-blend, SPS | 369 |
| NARloy-Z | 40 | 137 | refractory-carbide | powder-blend, hot press | 322 |
| NARloy-Z | 40 | 192.5 | none | powder-blend, hot press | 505 |

A separate best-case data point (§2, Fig. 2) for Vf=0.45, 137-micron diamond, well-dispersed:
**k > 540 W/m·K**, i.e. **~1.5× pure copper's 360 W/m·K**, at density **6.1 g/cm³** (>30%
lower than Cu alloys). Note the paper's own finding (**item 2, p.12**) that for the **NARloy-Z
matrix, uncoated diamond gives the highest conductivity** (coating actually *lowers* k in that
matrix — carbide forms naturally via the alloy's own Zr), whereas for a **pure-Cu matrix,
refractory-carbide-coated diamond is needed** for reliable high conductivity (uncoated gives
"highly variable and unreliable" results in pure Cu) — i.e. the coating decision is
matrix-dependent, not a universal rule.

**Density** `[CuDiamond-Liner §4 "Density" p.13]`: 40 vol% diamond in NARloy-Z lowers density
by **~30%** (abstract states ">25% lighter"); Table 5's measured NARloy-Z-matrix sample
densities range **6.2–7.7 g/cm³** vs. NARloy-Z's own (unstated in this paper, but per
`[MatCh2]`/`[GRCop84-TM2005]` already in `topics/12-materials-and-structures.md`, ~8.9 g/cm³
baseline) — density drops roughly in proportion to diamond volume fraction (diamond ρ ≈
3.5 g/cm³ vs. Cu ≈ 8.9 g/cm³).

**Tensile properties — the caveat that matters most for a "buildable liner material"
framing** `[CuDiamond-Liner Table 4, p.10]` (MSFC-tested, EDM-machined coupons):

| Sample | Diamond | Test condition | YS (ksi) | UTS (ksi) | Elongation |
|---|---|---|---|---|---|
| NARloy-Z baseline | 0 | 75°F, air | 18 | 45 | **33%** |
| NARloy-Z-30D | 30 vol%, uncoated | 75°F, air | 19 | 19 | **<1%** |
| NARloy-Z-40D | 40 vol%, uncoated | 75°F, air | 18–20 | 18–24 | **<1%** |
| NARloy-Z-40D | 40 vol%, uncoated | 935°F, GN2 | 11 | 11 | <1% |
| NARloy-Z-30(Ti-D) | 30 vol%, Ti-coated | 75°F, air | 12 | 12–13 | <1% |
| NARloy-Z-30(Cu-MoC-D) | 30 vol%, Cu-MoC-coated | 70°F, air | 18 | 23 | **2–3%** (best) |
| NARloy-Z-30(Cu-MoC-D) | 28 vol%, MoC+Cu-coated | 1000°F, 250psi He | 5–6 | 5–7 | 2–3% |
| NARloy-Z-40D diffusion-bonded | 40 vol%, uncoated | 70°F, air | 10 | 11 | <1% |

**This is the single most consequential real number for a "materials catalog" framing**: adding
diamond costs **roughly half the UTS** (45→18-24 ksi) and **collapses ductility from 33% to
generally <1%**, with copper-coated diamond (Cu-MoC-D) as the one combination that partially
recovers ductility (2–3%) at a UTS cost still down to ~23 ksi (vs. 45 ksi baseline). The paper
itself acknowledges: "As expected ductility is low, especially for uncoated diamonds"
`[§4 p.10]`. This directly counters a naive "just replace NARloy-Z with Cu-D, it conducts
better" framing — the composite trades away most of the base alloy's strength/ductility for
thermal conductivity, a real strength/ductility-vs-conductivity tradeoff any material-catalog
entry for this family should carry.

**Thermal cycling durability** `[CuDiamond-Liner §4 "Thermal Cycling Behavior" p.13-16, Tables
6-8]`: samples survived repeated LN2 quench cycles (RT ↔ −192°C) and a 450°C fast-cool cycle
with only **small (1.4–8.7%) drops in thermal conductivity** after 1–5 cycles — no evidence of
gross Cu-D interface debonding for well-processed (electroplated/coated) samples; the largest
degradation (8.7%) occurred for a **lower-quality M1-grade diamond** sample, i.e. diamond
quality/coating quality (not just Vf) governs cycling durability. Caveat: these cycle
temperatures (−192°C to 450°C, or −55 to 200°C for the CTE study) are milder than a real
chamber-liner's operating range (paper itself notes liner hot-side may exceed 500°C, cold-side
may approach LH2/LCH4 temperatures −253/−162°C) — **no cycling data exists yet at true
combustion-chamber-relevant extremes**.

**Manufacturing method** `[CuDiamond-Liner §3, §5 p.6-9, 17-21]`: exclusively **powder
metallurgy** — copper (or NARloy-Z/GRCop-84/Cu-Zr) alloy powder blended with diamond particles
(coated with a refractory carbide such as ZrC/MoC/HfC, optionally overcoated with Ni then Cu,
when the matrix lacks its own carbide-former like Zr or Cr) then consolidated by **hot
pressing** (~1 hr at ~980°C, 6 ksi, slow heat/cool) or **spark plasma sintering / FAST**
(~20 min at 950°C, 8 ksi, fast heat/furnace cool — the two techniques give comparable
conductivity for carbide-coated diamond in pure Cu, Table 3). Diamond is "the hardest material
known" — conventional machining is impractical; **EDM and waterjet cutting** are the
demonstrated machining routes, and cooling channels (typically 1-2mm) are better **built into
the die** than machined afterward. A sub-scale liner (2.5in ID × 2.75in OD × 1in tall rings,
30 vol% diamond in NARloy-Z) was successfully fabricated by stacking 8 SPS-made rings and
diffusion-bonding them (Figs. 9-12) — real hardware exists at coupon/sub-scale-ring level only,
**no full-scale chamber liner has been built or hot-fire tested** per this paper. The authors
explicitly expect **Cu-D powder to behave similarly to GRCop-84 powder in additive
manufacturing (SLM/DMLS)**, leveraging MSFC's existing GRCop-84 AM chamber work (Gradl et al.
refs 11-13), but this is stated as an expectation/roadmap (§5, "Fabrication of Cu-D Composite
Liner by Additive Manufacturing"), not a demonstrated result — no Cu-D part has actually been
additively manufactured per this paper.

**Interface physics (background, not a design number)**: thermal conductivity of the composite
is highly sensitive to **interfacial thermal resistance (ITR)** between diamond and matrix —
a simple dry powder blend of copper and diamond shows *no* conductivity improvement at all;
gains only appear when a carbide-forming element (Zr, Cr) is present in the matrix or the
diamond is pre-coated with a refractory carbide (ZrC, MoC, HfC), which chemically bonds and
acoustically impedance-matches the interface. ZrC is specifically flagged as forming a
coherent, high-conductivity, ductility-improving bond with copper (§3, driven by its more
negative free energy of formation, ΔG = −173 kJ/mol vs. −76 kJ/mol for Cr23C6).

## Design method

Not a sizing/design-procedure source (no wall-thickness, hoop-stress, or chamber-sizing
method) — this is a materials-development status paper. The one quasi-design content is the
thermal-conductivity prediction model (§2): the differential-effective-medium (Bruggeman/
Hasselman) equation relating composite conductivity to matrix/particle conductivity, diamond
volume fraction, and a dimensionless interface-resistance parameter β = ak/a (Kapitza radius /
particle radius) — useful only as a *modeling* reference, not calibrated against any specific
buildable design point beyond the coupon data in Table 5.

## Section map

- §1 Introduction: p.2 — read in full.
- §2 Thermal Conductivity of Cu-D Composites (incl. modeling, acoustic-impedance interface
  theory, Kapitza conductance): p.3-6 — read in full.
- §3 Processing of Copper-Diamond Composites (powder selection, coating selection, mixing,
  consolidation — HP/HIP/SPS, machining, AM intro): p.6-9 — read in full.
- §4 Properties of Copper-Diamond Composites (tensile Table 4, thermal conductivity Table 5,
  density, thermal cycling Tables 6-8): p.9-16 — read in full, the numeric core of this note.
- §5 Fabricating Cu-D Combustion Chamber Liners (SPS sub-scale liner build, AM/SLM/DMLS
  compatibility, bimetallic-chamber cladding process): p.17-21 — read in full.
- §6 Summary: p.23 — read.
- References (13, several unpublished/in-house JANNAF papers): p.24 — listed, not chased down.

## Caveats

- **Early-TRL research material, not a flight-proven or even full-scale-hot-fire-tested one.**
  No real engine anywhere uses a Cu-D composite liner; the most advanced demonstrated hardware
  is a sub-scale (2.5-2.75in dia) diffusion-bonded ring-stack liner, not a hot-fire-tested full
  chamber. Treat any property number here as a **coupon-level research result**, one tier below
  even GRCop-84's own citations (`[GRCop84-TM2005]`, `[GRCop84-Tensile]`) which back an
  alloy actually flying/tested in real engines.
- **Large strength/ductility cost for the conductivity gain**: UTS roughly halves (45→18-24
  ksi) and elongation collapses to generally <1% (33%→<1% for most variants, 2-3% best case)
  when diamond is added to NARloy-Z — this paper does not resolve whether that ductility loss
  is acceptable for a real regen-cooled liner's thermal-cyclic-fatigue life; no low-cycle-
  fatigue data is given for any Cu-D variant (contrast `[Miller-CuFatigue]`'s real OFHC-copper
  Manson-Universal-Slopes LCF method already in this reference set — no equivalent exists yet
  for Cu-D).
- **Conductivity numbers are "estimated"/single-lab measurements, not independently
  replicated**: the 300/320/360 W/m·K figures for GRCop-84/NARloy-Z/pure-Cu are given by this
  paper's own §1/§3 as reference baselines without a cited primary source distinct from the
  paper's own framing — cross-check against `[MatCh2]`'s and `[GRCop84-TM2005]`'s own thermal-
  conductivity numbers before treating these as the authoritative baseline values (this note
  does not attempt that cross-check; flagging it for the integration pass).
- **Coating strategy is matrix-dependent, not universal**: refractory-carbide coating helps in
  a pure-Cu matrix but is *unnecessary or even mildly detrimental* in NARloy-Z (which already
  supplies its own carbide-former, Zr) — don't apply a single blanket "always coat diamond"
  rule if this material family is ever added to a design tool's material catalog. For AM
  specifically, Cu-D has not actually been additively manufactured yet per this paper — only
  GRCop-84 has (the AM section for Cu-D is a stated expectation/roadmap, §5, not a demonstrated
  result).
- **No numbers for**: high-temperature creep resistance of Cu-D composites (mentioned only
  qualitatively — diamond addition is claimed not to hurt the matrix's own creep resistance,
  but no creep test data is given), fatigue life, hot-gas-side wear/erosion resistance, cost per
  unit mass or per liner (only diamond *powder* cost per carat is given, Fig. 16: 6-22 cents/ct
  for two grit grades), or any coolant-side pressure/velocity design limit specific to Cu-D
  channel walls.
- OCR/extraction note: this PDF has a clean text layer (born-digital or well-OCR'd); tables
  extracted cleanly except embedded equations (§2 eq. 1-3) which render as scrambled character
  runs in the raw text — the equations were reconstructed from context/description rather than
  the literal OCR string; no numeric table was affected by this issue.
