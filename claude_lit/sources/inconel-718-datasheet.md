# [Inc718-TDS] — INCONEL alloy 718 (Special Metals technical bulletin SMC-045)

## Identity

- **Title**: *INCONEL® alloy 718*, technical bulletin, Publication No. SMC-045
- **Publisher**: Special Metals Corporation, Copyright 2007 (Sept 07)
- **Source**: `literature/inconel-alloy-718.pdf`, 28 pages. Born-digital text throughout (no
  OCR needed), but the PDF's text layer scrambles table structure badly — numeric columns
  extract as long runs of bare numbers disconnected from their row/column headers. Read in
  full (all 28 pages); numeric tables quoted below were reconstructed by matching value
  counts/ordering against each table's stated column headers and footnotes, cross-checked
  against publicly-known INCONEL 718 property ranges for plausibility. Same manufacturer and
  document family as the already-distilled `[SMC-X750]` (Inconel X-750, SMC-067) —
  identical disclaimer boilerplate, table style, and heat-treatment-condition structure.
- **Character**: A standard alloy-producer datasheet — composition limits, physical/thermal
  constants, and an extensive mechanical-properties section (room, elevated, and cryogenic
  tensile properties broken out by product form, heat treatment, and orientation; impact,
  fatigue, creep/rupture, and weld-property tables). The datasheet's own text explicitly
  names "components for liquid fueled rockets" as a real application (p.1) — the same kind
  of manufacturer marketing-text caveat `[SMC-X750]`'s note already flags (directionally
  trustworthy, not a validated real-engine data point).

## Composition (Table 1, wt%)

| Element | Range |
|---|---|
| Ni + Co | 50.00–55.00 |
| Cr | 17.00–21.00 |
| Fe | balance |
| Nb + Ta | 4.75–5.50 |
| Mo | 2.80–3.30 |
| Ti | 0.65–1.15 |
| Al | 0.20–0.80 |
| Co | 1.00 max |
| C | 0.08 max |
| Mn | 0.35 max |
| Si | 0.35 max |
| P | 0.015 max |
| S | 0.015 max |
| B | 0.006 max |
| Cu | 0.30 max |

UNS N07718/N07719, W.Nr. 2.4668. Age-hardenable via γ′/γ″ Ni₃(Al,Ti)/Ni₃Nb precipitates,
requiring a solution anneal (to dissolve Al/Ti/Nb) followed by a precipitation-hardening age.

## Physical constants (Table 2)

- Density: 0.296 lb/in³ annealed, 0.297 lb/in³ annealed+aged (8193 / 8221 kg/m³)
- Melting range: 2300–2437°F (1260–1336°C)
- Specific heat at 70°F: 0.104 Btu/(lb·°F) (435 J/(kg·K))
- Curie temperature: <-320°F (<-196°C) annealed; -170°F (-112°C) annealed+aged
- Permeability at 200 Oe, 70°F: 1.0013 annealed, 1.0011 annealed+aged (essentially
  non-magnetic, same family behavior as `[SMC-X750]`'s X-750 and the 321/347/348 grades in
  `[SS321-TDS]`)

## Thermal properties (Table 5, annealed 1800°F/1hr + aged 1325°F/8hr F.C. to 1150°F, 18 hr
total age)

| Temp, °F | Mean linear expansion (from 70°F), ×10⁻⁶/°F | Thermal conductivity, Btu·in/(hr·ft²·°F) | Electrical resistivity, ohm·circ mil/ft |
|---|---|---|---|
| -320 | – | 70 | 5.9 |
| 70 | – | 77 | – |
| 200 | 7.31 | 86 | 762 |
| 400 | 7.53 | 98 | 772 |
| 600 | 7.74 | 111 | 775 |
| 800 | 7.97 | 123 | 784 |
| 1000 | 8.09 | 135 | 798 |
| 1200 | 8.39 | 147 | 805 |
| 1400 | 8.91 | 160 | 802 |
| 1600 | – | 173 | 799 |
| 1800 | – | 185 | 801 |
| 2000 | – | 196 | 811 |

(Extraction note: the raw text interleaves two similar-looking numeric columns — annealed
vs. annealed+aged values differ only slightly at each temperature per the table's own
footnote structure; the table above uses the annealed+aged column, the condition closest to
real service use. Converting: k[W/(m·K)] = k[Btu·in/(hr·ft²·°F)] × 0.1442, so 77 →
~11.1 W/(m·K) at 70°F rising to ~28.3 W/(m·K) at 2000°F; CTE[/K] = CTE[/°F] × 1.8, so
7.31×10⁻⁶/°F → 1.32×10⁻⁵/K at 200°F.)

## Modulus of elasticity (Tables 3–4)

Room/near-room (~70-80°F): Young's modulus 29.0×10³ ksi (200 GPa), Poisson's ratio ≈0.29–0.30
across both low-temperature and elevated-temperature tables. Falls to 25.8×10³ ksi (178 GPa)
at 800°F, 23.7×10³ ksi (163 GPa) at 1200°F, 17.4×10³ ksi (120 GPa) at 1800°F, 14.3×10³ ksi
(99 GPa) at 2000°F — the modulus degrades substantially above ~1400°F, consistent with the
alloy's practical upper service-temperature limit sitting around 1300°F (see mechanical data
below) rather than its much higher melting range.

## Mechanical properties — two standard heat treatments

Two solution-anneal/age combinations dominate the datasheet, matching `[SMC-X750]`'s own
two-condition structure:

1. **1700–1850°F anneal + 1325°F/8hr age, F.C. to 1150°F, hold 18hr total** (AMS 5596/5589) —
   "optimum" for rupture life, notch-rupture life, and rupture ductility; also gives the
   highest room-temperature tensile/yield strength and highest fatigue strength (fine grain).
2. **1900–1950°F anneal + 1400°F/10hr age, F.C. to 1200°F, hold 20hr total** (AMS 5597/5590/
   5664) — preferred for tensile-limited applications: best transverse ductility in heavy
   sections, impact strength, and low-temperature notch-tensile strength; but more prone to
   notch brittleness in stress rupture.

**AMS 5596 sheet/strip/plate minimums** (1700–1850°F treatment): RT UTS 180 ksi (1241 MPa),
RT YS 150 ksi (1034 MPa), elongation 12% min; at 1200°F: UTS ≥140–145 ksi (965–1000 MPa)
depending on thickness, YS ≥115–120 ksi (793–827 MPa), elongation 5% min.

**Representative room/elevated-temperature tensile data, hot-rolled round, 1750°F anneal +
age** (Table 9, 4-in. diameter, longitudinal): RT UTS 199.5 ksi (1375 MPa), RT YS 178.0 ksi
(1227 MPa), 15.0% elongation, 24.0% RA, Rc 44; at 1200°F: UTS 167.0 ksi (1151 MPa), YS
152.5 ksi (1051 MPa), 13.0% elongation.

**Full temperature sweep, 5/8-in. hot-rolled round, 1800°F anneal + age** (Table 20,
-320°F to 1300°F):

| Test temp, °F | UTS, ksi (MPa) | YS, ksi (MPa) | Elongation, % | RA, % |
|---|---|---|---|---|
| -320 | 237.0 (1634) | 173.5 (1196) | 26.0 | 27.0 |
| -60 | 201.5 (1389) | 158.0 (1089) | 23.0 | 33.5 |
| 80 | 190.5 (1313) | 153.5 (1058) | 22.0 | 32.5 |
| 1200 | 164.5 (1134) | 145.0 (1000) | 28.0 | 59.2 |
| 1300 | 145.5 (1003) | 133.0 (917) | 22.0 | 34.0 |

This table is the single most useful data point in the datasheet for a chamber/turbopump
material margin check: **strength holds up well from cryogenic through 1200°F, then drops
sharply between 1200°F and 1300°F** (UTS falls from 164.5 to 145.5 ksi, a ~12% drop over just
100°F) — a real, quantified cliff consistent with 718's commonly-cited ~1300°F practical
service ceiling (vs. the datasheet's own broader "-423° to 1300°F" material description on
p.1) and independently consistent with `[SMC-X750]`'s finding that Inconel X-750's own
quantitative strength tables likewise stop providing discrete numbers right around where
qualitative "usable to 1800°F" claims begin (though 718's real ceiling, ~1300°F, is
considerably lower than X-750's ~1800°F oxidation-resistance claim — these are two distinct
alloys in the same product family with different high-temperature capability, not
interchangeable numbers).

**Low-temperature (cryogenic) short-transverse forging data** (Table 21, both heat
treatments): from RT down to -423°F (20 K, liquid-hydrogen temperature), UTS rises
substantially — 1800°F-anneal condition: RT UTS 187.0 ksi (1289 MPa) → -423°F UTS 237.2 ksi
(1635 MPa), with YS also rising (165.9 → 194.9 ksi) and elongation holding at 11.5–17%,
i.e. **no cryogenic embrittlement cliff** — 718 gets stronger, not more brittle, down to LH2
temperature, the same qualitative cryogenic-toughness pattern already noted for 304/304L
(`[SS304-TDS]`) and typical of the FCC-nickel-superalloy/austenitic-steel family broadly.
Notch/unnotch tensile strength ratio stays 1.19–1.45 (>1, i.e. notch-strengthening, not
notch-weakening) across this whole range for the 1800°F-anneal condition — a real,
quantified fracture-toughness margin at cryogenic temperature.

**Corrosion resistance** (brief, qualitative, one paragraph): "excellent corrosion
resistance to many media...similar to that of other nickel-chromium alloys...a function of
composition" — Ni resists many inorganic/organic reducing media and chloride-ion SCC; Cr
resists oxidizing media and sulfur compounds; Mo contributes pitting resistance. No
quantitative corrosion-rate tables (unlike the extensive ones in `[Ni200]`).

## Key gap check: hydrogen-embrittlement / HEE data — NOT PRESENT

**A full-text keyword search of all 28 pages for "hydrogen"/"embrittl" (any case) returned
zero matches.** This datasheet is purely a mechanical/thermal/physical-properties reference
— it contains no hydrogen-compatibility, HEE-index, or LOX/GOX-ignition data of any kind.
This confirms the gap already flagged in `topics/12-materials-and-structures.md`:
`[MatCh2]`'s HEE-index table (§2.8.4-2.8.5) — which shows Inconel 718's HEE resistance
flipping from **Extreme** (NTS ratio 0.46–0.53) at a 1750°F solution anneal to **Small**
(NTS ratio ~0.92) at a 1900°F solution anneal — remains the *only* source for that finding in
this reference set. Notably, this datasheet's own two standard heat treatments bracket
exactly that solutionizing-temperature range (1700–1850°F vs. 1900–1950°F, matching
`[MatCh2]`'s 1750°F/1900°F test points almost exactly) — i.e. **the same two heat treatments
this datasheet recommends for different mechanical-property priorities (rupture-life-optimized
vs. tensile/ductility-optimized) also happen to be the two heat treatments that give
dramatically different hydrogen-environment embrittlement resistance**, per `[MatCh2]`. This
datasheet itself never makes that connection or mentions H₂ service at all — the two sources
are complementary (this one for the mechanical/thermal numbers at each heat treatment,
`[MatCh2]` for which heat treatment is H2-safe), not overlapping or redundant.

## Caveats

- Table-structure extraction from this PDF's text layer is unreliable (numbers separated
  from row/column labels); all numeric tables above were manually reconstructed by matching
  value order/count against stated headers and footnotes, then sanity-checked against
  publicly-known INCONEL 718 property ranges. Treat any single cell with more caution than a
  cleanly-tabulated source (contrast `[SS304-TDS]`/`[SS321-TDS]`, whose PDFs extracted
  cleanly).
- This is a general mill datasheet, not a propulsion-specific report — the "used in liquid
  rocket engine components" line (p.1) is unreferenced manufacturer marketing text.
- All mechanical-property tables are heat-treatment- and product-form-specific; the same
  caveat `[SMC-X750]` already carries (~2× strength variation depending on treatment) applies
  here too.
- No hydrogen-compatibility data (confirmed above) — do not use this datasheet alone to make
  any H2-service judgment about Inconel 718; `[MatCh2]` remains the citation for that.
- No LOX/GOX ignition-sensitivity data either (contrast `[MatCh2]`'s own promoted-ignition
  test data already flagging 718's surprisingly low 500 psi threshold) — this datasheet does
  not address oxygen compatibility at all.

## Implications for `engine_designer`

`materials.py`'s existing `inconel_718` entry already carries an uncited/derated
`allowable_stress_pa` per `ASSUMPTIONS.md`'s Tier-3 flag (topics/12's Caveats section
reiterates this). This datasheet now gives that entry a **real, cited source for its
temperature-dependent mechanical-property *shape*** — in particular the real UTS/YS cliff
between 1200°F and 1300°F (Table 20 above) is a directly usable data point for setting or
sanity-checking a temperature-dependent strength derating curve, and the real density
(8193–8221 kg/m³ vs. whatever `materials.py` currently uses — worth a direct diff),
thermal conductivity (~11.1 W/(m·K) at 70°F rising to ~28.3 W/(m·K) at 2000°F), and CTE
values are all now backed by a primary manufacturer source rather than a generic textbook
figure. The HEE-relevant finding above (same alloy, two very different H2-embrittlement
outcomes depending on which of *this datasheet's own two standard heat treatments* is used)
is worth a note wherever `materials.py`/`ASSUMPTIONS.md` currently treats "Inconel 718" as a
single undifferentiated material — real mill practice already distinguishes the two
treatments for other reasons (rupture-life vs. tensile/ductility priority), so specifying
"1900°F+ solution anneal" as the H2-service-safe condition costs nothing on top of an
already-real manufacturing choice. Report-only — no code changed.
