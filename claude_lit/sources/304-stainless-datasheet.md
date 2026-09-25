# [SS304-TDS] — 304/304L Stainless Steel Data Sheet (Rolled Alloys)

## Identity

- **Title**: *304/304L* Data Sheet
- **Publisher**: Rolled Alloys (rolledalloys.com), copyright line reads "© 2026 Rolled
  Alloys 04/26" — a mill-distributor datasheet, most likely a typo for 2016/04/16 on the
  original scan (the file itself carries no other date marker); treat the copyright year as
  unreliable but the content as a standard, current 304/304L mill reference regardless.
- **Source**: `literature/304-304L_Stainless_Steel_Data_Sheet_RolledAlloys.pdf`, 1 page.
  Born-digital, clean text extraction (no OCR needed).
- **Character**: A one-page manufacturer/distributor datasheet — composition limits, a
  handful of physical constants, and a room-temperature + elevated/cryogenic-temperature
  tensile-property table, per ASTM A240. No design methodology, no rocket-specific content;
  this is the shortest and least detailed of the four datasheets in this batch.

## Composition (Table, wt%, per ASTM A240)

| Element | Min | Max |
|---|---|---|
| Ni | 8.0 | 11.0 |
| Cr | 18.0 | 20.0 |
| Mn | – | 2.0 |
| Si | – | 0.75 |
| C | – | 0.03 |
| S | – | 0.03 |
| P | – | 0.045 |
| N | – | 0.10 |
| Fe | – | balance |

UNS S30400 (304) / S30403 (304L); W.Nr./EN 1.4301/1.4307. 304L differs only in the lower
carbon cap (0.03% max shown here is actually the 304L limit — the sheet gives one combined
composition table for both grades, consistent with its own statement that "most products
are dual certified as 304/304L").

## Physical properties (room temperature unless noted)

- Density: 0.285 lb/in³ (7889 kg/m³)
- Melting range: 2550–2590°F (1399–1421°C)
- Poisson's ratio: 0.3
- Electrical resistivity: 28.3 µΩ·in
- CTE (68–212°F): 9.2 µin/(in·°F) → 16.6×10⁻⁶/K
- Thermal conductivity (at 212°F/100°C): 9.4 Btu/(hr·ft·°F) → 16.3 W/(m·K)
- Modulus of elasticity (68°F): 29×10⁶ psi (200 GPa)

## Mechanical properties

**Minimum room-temperature properties (per ASTM A240, condition A)**: UTS 75 ksi (517 MPa),
0.2% YS 30 ksi (207 MPa), elongation 40%, hardness max 201 HB (a second near-identical row in
the sheet gives the same UTS/YS/elongation with no hardness cap listed — likely the plate vs.
sheet/strip A240 split, not separately labeled in the extracted text).

**Typical low- and elevated-temperature tensile properties** (minimum values per the sheet's
own header note):

| Temp, °F | UTS, ksi | 0.2% YS, ksi | Charpy V-notch, ft-lb |
|---|---|---|---|
| -425 | 250 | 100 | 85 |
| -320 | 230 | 70 | 85 |
| -100 | 150 | 50 | – |
| 70 | 90 | 35 | – |
| 150 | – | – | – |
| 400 | 70 | 23 | – |
| 800 | 66 | 19 | – |
| 1200 | 48 | 15.5 | 13 |
| 1500 | 23 | 13 | – |

(Table extracted with a small ambiguity: a "150" row appears in the raw text between -100
and 400°F with no associated UTS/YS values — likely a stray temperature label from a
differently-formatted source table; not fabricated here, just flagged as an extraction gap.)

Qualitative notes: "excellent strength and toughness at cryogenic temperatures" is called
out as a named feature — consistent with 304/304L's Charpy impact energy actually *rising*
at -425°F (85 ft-lb) vs. 1200°F (13 ft-lb) in the table above, i.e. no low-temperature
ductile-to-brittle impact-toughness cliff for this austenitic grade, unlike ferritic/
martensitic steels.

## Caveats

- One-page distributor datasheet, not a primary mill-test-report or a NASA/AIAA design
  source — treat as a convenient, standard reference for 304/304L bulk properties, same tier
  as a materials handbook entry, not a validated engine citation.
- No high-temperature creep/rupture, fatigue, or hydrogen-compatibility data at all — this
  sheet is strictly composition + a single tensile-vs-temperature table + a few physical
  constants.
- The extracted temperature table has the one row-alignment ambiguity noted above; the other
  rows parsed cleanly and pair sensibly with well-known 304/304L behavior (e.g. RT UTS 90 ksi
  0.2%YS 35 ksi, RT elongation 40% match publicly-known typical 304 mill-test values).

## Implications for `engine_designer`

304/304L is not currently a named alloy in `materials.py`'s catalog (per a quick cross-check
against `topics/12-materials-and-structures.md`'s existing coverage, which centers on
Inconel/X-750/Cu-alloys/superalloys for hot-section parts) — this datasheet would be the
citable source if a low-cost structural/manifold/plumbing-line stainless entry is ever added
(distinct from the higher-temperature-capable 321/347/348 stabilized grades covered in
`[SS321-TDS]`, which explicitly name 304L's 800°F/427°C Section VIII code-use ceiling as the
reason the stabilized grades exist for hotter service). Report-only — no code touched.
