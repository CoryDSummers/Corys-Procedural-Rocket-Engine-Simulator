# [SS321-TDS] — ATI 321/ATI 347/ATI 348 Technical Data Sheet

## Identity

- **Title**: *ATI 321™/ATI 347™/ATI 348™ — Stainless Steel: Austenitic (UNS S32100,
  S34700, S34800)*, Technical Data Sheet, Version 1 (2/18/2014)
- **Publisher**: Allegheny Technologies Incorporated (ATI), Pittsburgh, PA
- **Source**: `literature/ati_321_347_348_tds_en2_v1.pdf`, 11 pages. Born-digital, clean text
  extraction throughout (no OCR needed; all 11 pages read in full).
- **Character**: A manufacturer technical data sheet for the Ti/Cb-stabilized austenitic
  grades of 18-8 stainless (321 = Ti-stabilized, 347/348 = Cb+Ta-stabilized, 348 = 347 with
  restricted Co/Ta for nuclear service) — the grades whose whole reason for existing is
  resisting intergranular ("sensitization") corrosion after exposure in the 800–1500°F
  (427–816°C) chromium-carbide-precipitation range, where unstabilized 304/304L would
  degrade. Higher-value than a typical mill sheet for this project because 321/347-family
  CRES steels are the named real F-1 hot-gas-manifold/turbine-exhaust-hardware material
  class per `[Ch12-Materials]`'s "≥20% ductility at elevated temperature" hot-gas-manifold
  design criterion (topics/12 §"hot-gas manifold" content, real examples cited there: 347
  CRES, Hastelloy C, Inconel 625, L-605) — directly relevant to `physics/turbine_exhaust.py`
  duct/manifold material selection.

## Composition (Table 1, wt%, per ASTM A240)

| Element | 321 | 347 | 348 |
|---|---|---|---|
| C | 0.08 max | 0.08 max | 0.08 max |
| Mn | 2.00 max | 2.00 max | 2.00 max |
| P | 0.045 max | 0.045 max | 0.045 max |
| S | 0.030 max | 0.030 max | 0.030 max |
| Si | 0.75 max | 0.75 max | 0.75 max |
| Cr | 17.00–19.00 | 17.00–19.00 | 17.00–19.00 |
| Ni | 9.00–12.00 | 9.00–12.00 | 9.00–12.00 |
| Cb (Nb)+Ta | – | 10×C min–1.00 max | 10×C min–1.00 max |
| Ta | – | – | 0.10 max |
| Ti | 5×(C+N) min–0.70 max | – | – |
| Co | – | – | 0.20 max |
| N | 0.10 max | – | – |
| Fe | balance | balance | balance |

High-carbon variants (321H/347H/348H, UNS S32109/S34709/S34809) exist with a different
minimum-stabilizer formula and higher strength above 1000°F; 347H is the grade with an
ASME-code-recognized elevated allowable stress over standard 347.

## Physical properties

| Property | 321 | 347 | 348 |
|---|---|---|---|
| Density | 7.92 g/cm³ (0.286 lb/in³) | 7.96 g/cm³ (0.288 lb/in³) | 7.96 g/cm³ (0.289 lb/in³) |

Common to all three grades (sheet states physical properties "may be considered the same"
across all three):
- Modulus of elasticity in tension: 28×10⁶ psi (193 GPa)
- Magnetic permeability: <1.02 at 200 Oe, annealed (essentially non-magnetic; rises with
  cold work and in welds containing ferrite)
- Melting range: 2550–2635°F (1398–1446°C)

**Mean CTE** (from 20°C):

| Range, °C (°F) | ×10⁻⁶/°C | ×10⁻⁶/°F |
|---|---|---|
| 20–100 (68–212) | 16.6 | 9.2 |
| 20–600 (68–1112) | 18.9 | 10.5 |
| 20–1000 (68–1832) | 20.5 | 11.4 |

**Thermal conductivity**:

| Range, °C (°F) | W/(m·K) | Btu·in/(hr·ft²·°F) |
|---|---|---|
| 20–100 (68–212) | 16.3 | 112.5 |
| 20–500 (68–932) | 21.4 | 147.7 |

**Specific heat** (0–100°C / 32–212°F): 500 J/(kg·K) = 0.12 Btu/(lb·°F).

**Electrical resistivity** rises from 72 µΩ·cm at 20°C to 126 µΩ·cm at 900°C (68–1652°F) —
seven-point table given, monotonic rise.

## Mechanical properties

**Minimum room-temperature properties per ASTM A240/ASME SA-240** (annealed, all three
grades identical spec minimums):

| Grade | 0.2% YS | UTS | Elongation (2 in.) | Hardness max (plate/sheet/strip) |
|---|---|---|---|---|
| 321 | 30,000 psi (205 MPa) | 75,000 psi (515 MPa) | 40% | 217 HB / 95 Rb / 95 Rb |
| 347 | 30,000 psi (205 MPa) | 75,000 psi (515 MPa) | 40% | 201 HB / 92 Rb / 92 Rb |
| 348 | 30,000 psi (205 MPa) | 75,000 psi (515 MPa) | 40% | 201 HB / 92 Rb / 92 Rb |

**Typical elevated-temperature tensile properties, ATI 321 (0.036 in./0.9 mm sheet)**:

| Test temp °F (°C) | 0.2% YS, psi (MPa) | UTS, psi (MPa) | Elong. % |
|---|---|---|---|
| 68 (20) | 31,400 (215) | 85,000 (590) | 55.0 |
| 400 (204) | 23,500 (160) | 66,600 (455) | 38.0 |
| 800 (427) | 19,380 (130) | 66,300 (455) | 32.0 |
| 1000 (538) | 19,010 (130) | 64,400 (440) | 32.0 |
| 1200 (649) | 18,890 (130) | 55,800 (380) | 28.0 |
| 1350 (732) | 19,000 (130) | 41,500 (285) | 26.0 |
| 1500 (816) | 17,200 (115) | 26,000 (180) | 45.0 |

**Typical elevated-temperature tensile properties, ATI 347/348 (0.060 in./1.54 mm sheet)** —
notably stronger than 321 at every temperature, especially room temperature:

| Test temp °F (°C) | 0.2% YS, psi (MPa) | UTS, psi (MPa) | Elong. % |
|---|---|---|---|
| 68 (20) | 36,500 (250) | 93,250 (640) | 45.0 |
| 400 (204) | 36,600 (250) | 73,570 (505) | 36.0 |
| 800 (427) | 29,680 (205) | 69,500 (475) | 30.0 |
| 1000 (538) | 27,400 (190) | 63,510 (435) | 27.0 |
| 1200 (649) | 24,475 (165) | 52,300 (360) | 26.0 |
| 1350 (732) | 22,800 (155) | 39,280 (270) | 40.0 |
| 1500 (816) | 18,600 (125) | 26,400 (180) | 50.0 |

**Fatigue**: endurance limit ≈35% of tensile strength for both 321 and 347 (no discrete
S-N table given, just this ratio rule and reference to graphical creep/stress-rupture
curves not further digitized here).

**Charpy V-notch impact** (annealed 347, 1 hr hold at test temp): 90 ft-lb (122 J) at 24°C,
66 ft-lb (89 J) at -32°C, 57 ft-lb (78 J) at -62°C — "321 would be expected to be similar."
Good low-temperature toughness retention, consistent with austenitic-steel behavior broadly
(cf. `[SS304-TDS]`'s similar cryogenic-toughness callout for 304/304L).

**Oxidation resistance** (ATI 347, mill-finish, ambient-air exposure, weight-gain data
representative of all three grades per the sheet):

| Exposure | 1300°F | 1350°F | 1400°F | 1450°F | 1500°F |
|---|---|---|---|---|---|
| 168 hr | 0.032 mg/cm² | 0.046 | 0.054 | 0.067 | 0.118 |
| 500 hr | 0.045 | 0.065 | 0.108 | 0.108 | 0.221 |
| 1,000 hr | 0.067 | – | 0.166 | – | 0.338 |
| 5,000 hr | – | – | 0.443 | – | – |

## Key qualitative results relevant to hot-hardware selection

- **Maximum ASME code-use temperature**: 1500°F (816°C) for 321/347/348 (matching 304's own
  code ceiling) vs. only 800°F (427°C) for unstabilized 304L — the entire reason the
  stabilized grades exist is to extend usable Section VIII/III service temperature while
  avoiding sensitization-driven intergranular corrosion.
- **Stress corrosion cracking**: 321/347/348 remain SCC-susceptible in halides just like 304
  (similar nickel content is the driver) — chloride ion + residual tensile stress +
  temperature above ~120°F (49°C) is the classic SCC triad; not recommended for marine
  exposure despite passing the 100-hr 5% salt-spray test.
- **Polythionic acid SCC resistance**: a distinct, real advantage of the stabilized grades —
  they resist the sensitization that causes non-stabilized 304 to crack from polythionic
  acids formed when sulfide-containing (H₂S) environments contact sensitized grain
  boundaries on cooldown. Directly relevant to any GG/turbine-exhaust hardware exposed to
  sulfur-bearing combustion products.
- **Heat treatment**: anneal 1800–2000°F (982–1093°C); ATI 321 sometimes needs an additional
  "stabilizing anneal" at 1550–1650°F (843–899°C) for maximum corrosion resistance since
  titanium stabilization is less complete than columbium stabilization; not hardenable by
  heat treatment (solid-solution strengthened/cold-work strengthened only, same family as
  304/304L, unlike the age-hardenable Ni-superalloys in the other three datasheets).
- **Weldability**: designed to resolidify with a small ferrite fraction to resist hot
  cracking; Cb-stabilized (347/348) grades are more prone to hot cracking than Ti-stabilized
  (321); matching filler metals available for both families.

## Caveats

- No hydrogen-embrittlement or LOX/GOX-compatibility data at all (same gap as `[SS304-TDS]`)
  — for that, `[MatCh2]`'s HEE-index and promoted-ignition-test tables (already in
  `topics/12`) remain the only cited source in this reference set; this datasheet notes
  austenitic stainless "resists HEE better than martensitic/PH steels" only implicitly
  through its own family classification, not through a stated HEE test.
- The oxidation-resistance and creep/stress-rupture data are for 347 only, extrapolated by
  the manufacturer itself ("these results should be interpreted only as a general indication
  ... representative of all three grades") — not independently measured for 321/348.
- Creep/stress-rupture curves (pages 7–8) are plots, not digitized numeric tables — captions/
  context read, plotted values not extracted.
- Manufacturer's own disclaimer: "data are typical ... should not be construed as maximum or
  minimum values for specification or final design" except where explicitly tied to
  ASTM A240/ASME SA-240 minimums (the room-temperature table above).

## Implications for `engine_designer`

Not currently a named alloy in `materials.py`'s catalog (same gap `[SS304-TDS]` flags) —
this datasheet is the citable primary source if a stabilized-CRES turbine-exhaust-duct or
hot-gas-manifold entry is ever added, distinguishing it from plain 304/304L by its higher
code-use temperature (1500°F/816°C vs. 800°F/427°C) and superior creep/stress-rupture/
sensitization resistance — directly on-point for `physics/turbine_exhaust.py`'s duct/
manifold material context and the `[Ch12-Materials]`-sourced F-1 hot-gas-manifold "347 CRES"
real-hardware citation already in `topics/12`. Report-only — no code touched.
