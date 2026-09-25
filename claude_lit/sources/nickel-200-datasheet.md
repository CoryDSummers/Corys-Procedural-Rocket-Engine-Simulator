# [Ni200-TDS] — Nickel 200 & 201 (Special Metals technical bulletin)

## Identity

- **Title**: *Nickel 200 & 201*, technical bulletin
- **Publisher**: Special Metals Corporation
- **Source**: `literature/nickel-200.pdf`, 20 pages. Born-digital text throughout (no OCR
  needed); same PDF text-layer table-scrambling issue as `[Inc718-TDS]` (numeric columns
  separated from headers) — numbers below reconstructed against stated column headers/
  footnotes, same caveat applies. Read in full (all 20 pages).
- **Character**: A standard alloy-producer datasheet covering **two related grades**:
  Nickel 200 (commercially pure, ≥99.0% Ni+Co, standard carbon) and Nickel 201 (the
  low-carbon, 0.02% C max version, used instead of 200 above 600°F/315°C to avoid
  graphitization embrittlement). Composition, physical/thermal constants, extensive
  mechanical-property tables (room, elevated, cryogenic tensile; fatigue; creep/rupture;
  impact; shear/torsion/compressive/bearing strength), and a substantial corrosion-resistance
  section (atmospheric, caustic, halide/halogen-acid environments) for both grades.

## Composition

**Nickel 200** (UNS N02200/W.Nr. 2.4060 & 2.4066, Table 1): Ni+Co 99.0% min, Cu 0.25% max,
Fe 0.40% max, Mn 0.35% max, C 0.15% max, Si 0.35% max, S 0.01% max. Commercially pure
(~99.6%) wrought nickel.

**Nickel 201** (UNS N02201/W.Nr. 2.4061 & 2.4068, Table 28): identical to 200 except
**C 0.02% max** (vs. 0.15% max) — the low-carbon version, specifically to suppress
graphite precipitation at elevated temperature.

## Physical constants — Nickel 200 (Table 2)

- Density: 0.321 lb/in³ (8.89 g/cm³, 8890 kg/m³)
- Melting range: 2615–2635°F (1435–1446°C)
- Specific heat: 0.109 Btu/(lb·°F) (456 J/(kg·°C))
- Curie temperature: 680°F (360°C)

Nickel 201 (Table 29) shares the same density (0.321 lb/in³, 8.89 g/cm³), specific heat
(0.109 Btu/(lb·°F), 456 J/(kg·°C)), and Curie temperature (680°F/360°C) as Nickel 200 — the
low-carbon variant doesn't change bulk physical constants, only elevated-temperature
metallurgical stability.

## Thermal properties — Nickel 200 (Table 3, annealed)

| Temp, °C (°F) | Electrical resistivity, µΩ·m | CTE (from 70°F/21°C), µm/(m·°C) | Thermal conductivity, W/(m·°C) |
|---|---|---|---|
| -100 (-148) | 11.3 | 75.5 | 0.050 |
| 20 (68) | – | 70.3 | 0.096 |
| 100 (212) | 13.3 | 66.5 | 0.130 |
| 200 (392) | 13.9 | 61.6 | 0.185 |
| 400 (752) | 14.8 | 55.4 | 0.330 |
| 600 (1112) | 15.5 | 59.7 | 0.400 |
| 800 (1472) | 16.2 | 64.0 | 0.460 |
| 1000 (1832) | 16.9 | 68.2 | 0.510 |
| 1100 (2012) | 17.1 | – | 0.540 |

(Note: thermal conductivity column values as extracted are anomalously low — 0.05–0.54 in
whatever unbracketed unit the source table uses; the raw text gives the column header only as
"W/m·°C" with no ×-multiplier shown, but pure nickel's real room-temperature thermal
conductivity is ~70-90 W/(m·K), not 0.096 — this strongly suggests a units/scaling
inconsistency in the extracted table (possibly a decimal-point or unit-prefix artifact from
the PDF's column-scrambling). **Flagged, not resolved** — do not use this thermal-conductivity
column without independently cross-checking against a cleanly-tabulated nickel-conductivity
source; the CTE and resistivity columns in the same table look self-consistent and plausible
and are trusted here.)

A second physical-constants block (p.1, apparently an earlier/duplicate low-temperature
extension of the same table) gives thermal conductivity in Btu·in/(hr·ft²·°F) instead,
ranging 389–533 across -200°F to 2000°F with a minimum around 600–800°F (389) — this
alternate-unit table is internally more plausible in relative shape (a shallow dip then rise)
but the units column header ("Btu•in/ft2•h•°F") suggests real nickel thermal conductivity
values in the 390-530 range, i.e. roughly 56-77 W/(m·K), which IS in the right ballpark for
pure nickel — use this second table's values in preference to the Table 3 column flagged
above.

**Nickel 201 thermal properties** (Table 30, annealed) follow the same qualitative pattern —
resistivity ~13-15 µΩ·m in the 100-500°C range, CTE ~56-88 µm/(m·°C) (highest at low
temperature, dipping mid-range), thermal conductivity rising from 0.040 to 0.515 W/(m·°C) —
same units-ambiguity caveat as Table 3 above applies equally here.

## Mechanical properties — Nickel 200

**Nominal mechanical properties by product form** (Table 5, room temperature) — wide ranges
reflecting temper/cold-work state:

| Form/condition | UTS, ksi (MPa) | 0.2% YS, ksi (MPa) | Elongation, % | Hardness |
|---|---|---|---|---|
| Rod, hot-finished | 55-90 (380-620) | 15-45 (105-310) | 55-35 | 60-85 HRB |
| Rod, cold-drawn | 75-98 (520-675) | 40-100 (275-690) | 35-10 | 65-110 HRB |
| Rod, annealed | 45-70 (310-480) | 15-30 (105-210) | 55-40 | 55-75 HRB |
| Sheet, hard | 90 min. HRB | 70-105 (480-725) | 15-2 | – |
| Sheet, annealed | 70 max. HRB | 15-30 (105-210) | 55-40 | – |
| Wire, spring temper | – | 105-135 (725-930) | 15-2 | – |

**Torsional strength** (1-in. dia. cold-drawn rod): breaking strength 81.0 ksi (558 MPa) at
341°/in (13.4°/mm) twist.

**Shear strength** (double shear, annealed bar, RT): ~41.0-45.0 ksi (283-310 MPa), falling to
26.5-28.5 ksi (183-197 MPa) at 1000°F (540°C) after 0.5 hr, and to 27.0-29.0 ksi (186-200 MPa)
after 24 hr at 1000°F — real elevated-temperature degradation data, useful if a
plumbing-fitting/fastener shear check is ever needed.

**Compressive yield strength**: annealed 26.0 ksi (179 MPa); cold-drawn 24% reduction
27.0 ksi (186 MPa) — nickel's compressive and tensile yield are close (typical for FCC
metals), unlike some anisotropic/textured materials.

**Low-temperature (cryogenic) tensile properties, annealed bar** (Table 13, 0.750-in.
diameter):

| Temp, °F (°C) | UTS, ksi (MPa) | YS, ksi (MPa) | Elongation, % | RA, % |
|---|---|---|---|---|
| -423 (-253) | 110.0 (758) | 37.5 (259) | 60 | 70 |
| -300 (-184) | 90.0 (621) | 27.5 (190) | 61 | 75 |
| -200 (-129) | 78.0 (538) | 24.0 (165) | 57 | 68 |
| -100 (-73) | 71.0 (490) | 22.0 (152) | 51 | 65 |
| 0 (-18) | 66.0 (455) | 21.5 (148) | 49 | 65 |
| 70 (21) | 64.0 (441) | 21.0 (145) | 48 | 66 |

**A large, real strength gain at LH2 temperature**: UTS nearly *doubles* from RT (64.0 ksi)
to -423°F/-253°C (110.0 ksi) while elongation and reduction-of-area both stay high (60% and
70% respectively) — i.e. **no cryogenic embrittlement**, the same qualitative pattern already
noted for 304/304L and Inconel 718 in this batch's other two notes, and directly relevant
given `[Ch12-Materials]`'s own real-hardware note (already in `topics/12`) that Monel/
nickel-family alloys were the J-2/F-1-era real choice for cryogenic LH2-pump inducers on
cryogenic-ductility grounds.

**Metallurgical limitation — graphitization**: "Prolonged exposure in the temperature range
of 800°-1200°F (425°-650°C) will precipitate graphite. For this reason, the alloy is not
recommended for service in the 600°-1200°F (315°-650°C) range. Nickel 201 is used instead."
This is Nickel 200's single defining service-temperature limitation and the entire reason
Nickel 201 (low-carbon) exists as a separate grade.

## Mechanical properties — Nickel 201

Room-temperature mechanical properties (Table 31) are similar in range to Nickel 200 (not
separately reproduced here — same qualitative Rod/Sheet/Wire structure). The key differentiator
is high-temperature capability: **"Due to its low carbon content, Nickel 201 is resistant to
graphitization so it can be used at temperatures above 600°F. Nickel 201 is approved for
construction of pressure vessels and components under ASME Boiler and Pressure Vessel Code
Section VIII, Division 1... approved for service up to 1250°F."** — a real, code-recognized
max service temperature of 1250°F (677°C) for Nickel 201, vs. Nickel 200's practical ceiling
of ~600°F (315°C) before graphitization risk.

## Corrosion resistance (both grades)

Extensive qualitative + real test-data section (~6 pages): Nickel 200/201 is "highly
resistant to many corrosive media," particularly strong in reducing environments and
"unexcelled in resistance to caustic alkalies" (real application: caustic soda handling,
chemical shipping drums). Passive oxide film gives usable oxidizing-condition resistance.
Real test data given for: atmospheric exposure (marine/rural/industrial, two test series),
sodium hydroxide isocorrosion charts, dry fluorine corrosion (Nickel 201 has "outstanding
resistance to dry fluorine" — used for anhydrous HF/fluorine-handling equipment), dry
chlorine/dry hydrogen corrosion tables, and hydrogen chloride gas corrosion at elevated
temperature. **Nickel 201 and INCONEL alloy 600 are named as "the most practical alloys for
service in chlorine or hydrogen chloride at elevated temperatures."**

**Important disambiguation — "hydrogen" mentions in this datasheet are chemical-corrosion
context, not mechanical hydrogen-environment embrittlement (HEE)**: the word "hydrogen"
appears repeatedly (dry chlorine/dry hydrogen atmosphere tests, hydrogen chloride gas
corrosion, annealing-atmosphere dry-hydrogen practice, and a metallurgical note that a
carbon-solubility-in-nickel curve, Fig. 9, was itself generated by heating test nickel in wet
hydrogen/hydrogen-methane mixtures) — **none of this is HEE mechanical-property data** (no
notched-tensile-strength-in-H2 testing, no NTS ratio, nothing comparable to `[MatCh2]`'s HEE
Index methodology already covering Inconel 718/GRCop-84/NARloy-Z/etc. in `topics/12`). This
datasheet gives zero HEE-relevant data for Nickel 200/201, same gap pattern as `[Inc718-TDS]`
— but for pure nickel `[MatCh2]`'s own table (already in `topics/12`) already covers the
answer directionally: **"Pure nickel and Ni-rich binary alloys are severely embrittled"** by
gaseous hydrogen per the HEE mechanism — a real, separate, and considerably less favorable
finding than this chemical-corrosion-resistance section's generally positive tone about
"hydrogen" environments would suggest if read out of context. **This is worth flagging
loudly**: Nickel 200/201's real chemical resistance to hydrogen chloride gas / dry hydrogen
atmospheres (a corrosion-resistance property) must not be confused with its HEE
susceptibility (a mechanical hydrogen-gas-environment-embrittlement property, per `[MatCh2]`)
— they are different mechanisms with opposite practical implications for a design choice
touching gaseous H2.

## Caveats

- Same PDF table-scrambling extraction issue as `[Inc718-TDS]` — numeric tables reconstructed
  against stated headers/footnotes; the thermal-conductivity units ambiguity in Table 3/30
  (flagged above) is a real, unresolved extraction gap, not fabricated data — treat that one
  column with particular caution.
- General mill datasheet, not a propulsion-specific report. No mention of rocket-engine or
  aerospace-component use as a headline application (contrast `[Inc718-TDS]`'s explicit
  "liquid fueled rockets" line) — Nickel 200/201's stated applications are chemical
  processing, electronics, and caustic-handling equipment; "aerospace and missile components"
  is mentioned once in passing (p.1) with no further detail.
- No LOX/GOX ignition-sensitivity data (contrast `[MatCh2]`'s own promoted-ignition table,
  which does include "Nickel" as "essentially non-ignitable up to 10,000 psi" — a real,
  favorable data point for pure nickel already in `topics/12`, corroborating rather than
  contradicting this datasheet's generally favorable corrosion-resistance framing).
- No HEE mechanical-embrittlement data (confirmed above) — `[MatCh2]`'s "severely embrittled"
  finding for pure nickel remains the only HEE-relevant citation for this alloy family in
  this reference set, and it cuts the opposite direction from this datasheet's generally
  favorable "hydrogen" chemical-corrosion-resistance framing — don't conflate the two.

## Implications for `engine_designer`

Nickel 200/201 is not currently a named alloy in `materials.py`'s catalog per a quick
cross-check against `topics/12`'s existing coverage (which centers on Inconel/X-750/Cu-alloys/
superalloys) — this datasheet would be the citable source if a commercially-pure-nickel entry
is ever added (e.g. for caustic/chemical-compatible plumbing, or leveraging its real cryogenic
ductility for an LH2-side component per the `[Ch12-Materials]` cryogenic-inducer precedent).
Any such addition **must carry `[MatCh2]`'s "severely embrittled" HEE finding as a loud
caveat** for gaseous-hydrogen contexts (GG/turbine hardware, LH2 vapor-phase regions) even
though this datasheet's own corrosion-resistance data (dry hydrogen atmosphere, hydrogen
chloride gas) reads favorably — those are unrelated mechanisms, per the disambiguation above.
Report-only — no code changed.
