# [SMC-X750] — INCONEL alloy X-750

## Identity

- **Title**: *INCONEL® alloy X-750* (technical bulletin), Publication No. SMC-067
- **Publisher**: Special Metals Corporation, Copyright 2004 (Sept 04)
- **Source**: `www.specialmetals.com` — the manufacturer's own standard mill datasheet
  (uploaded directly by Cory; the local `literature/` copy of this PDF was not reachable
  from this cloud session — the folder is git-ignored, and the network policy also blocks
  `specialmetals.com`, so it was read from the user-uploaded file instead of the project's
  `literature/` tree).
- **Extent**: 28 pages. Born-digital, clean text and tables throughout.
- **Character**: A standard alloy-producer datasheet — composition limits, physical/thermal
  constants, and mechanical properties (tensile/yield/creep/rupture/fatigue) broken out by
  the several AMS-specified heat treatments this precipitation-hardenable alloy uses. No
  rocket-engine service/test data of its own; the one propulsion-specific claim ("used
  extensively in rocket-engine thrust chambers", p.1) is the manufacturer's own marketing
  text, not a validated engine citation — trust it directionally (this alloy really is used
  in thrust chambers/hot structure) but don't treat it as a real-engine data point the way
  `[NK-33-Mod]` or `[AEDC-J2S]` are.

## Key results

INCONEL alloy X-750 (UNS N07750 / W.Nr. 2.4669) is a precipitation-hardenable Ni-Cr-Fe
superalloy, hardened by γ' = Ni₃(Al,Ti) precipitates formed during heat treatment (p.20).
Composition (Table 1): Ni+Co ≥70%, Cr 14–17%, Fe 5–9%, Ti 2.25–2.75%, Al 0.40–1.00%,
Nb+Ta 0.70–1.20%.

**Physical constants (Table 2)**: density 0.299 lb/in³ = 8.28 g/cm³ (8280 kg/m³); melting
range 2540–2600°F (1393–1427°C); emissivity, oxidized surface, 0.895 at 600°F and 0.925 at
2000°F.

**Thermal properties (Table 3)**, material triple-heat-treated (2100°F/3hr, A.C. +
1550°F/24hr, A.C. + 1300°F/20hr, A.C.):

| Temp, °F | Mean linear expansion, /°F ×10⁻⁶ (from 70°F) | Thermal conductivity, Btu·in/(hr·ft²·°F) |
|---|---|---|
| 70 | – | 83 |
| 200 | 7.0 | 89 |
| 400 | 7.2 | 98 |
| 600 | 7.5 | 109 |
| 800 | 7.8 | 120 |
| 1000 | 8.1 | 131 |
| 1200 | 8.4 | 143 |
| 1400 | 8.8 | 154 |
| 1600 | 9.3 | 164 |
| 1800 | 9.8 | – |

Conversions used elsewhere in this project: k[W/(m·K)] = k[Btu·in/(hr·ft²·°F)] × 0.144228;
CTE[/K] = CTE[/°F] × 1.8 (equal-size increments, °F→°R vs. K→... i.e. a temperature
*difference* of 1°F = 1.8× smaller than 1 K's worth of expansion-per-degree, so the
numeric coefficient scales up by 1.8 going from per-°F to per-K).

**Modulus of elasticity (Table 5)**, Poisson's ratio 0.29:

| Temp, °F | Static tension, 10³ ksi | Dynamic tension, 10³ ksi | Static torsion, 10³ ksi |
|---|---|---|---|
| 80 | 31.0 | 31.0 | 11.0 |
| 500 | 28.7 | 29.1 | 10.2 |
| 1000 | 25.0 | 26.7 | 9.0 |
| 1200 | 23.0 | 25.5 | 8.1 |
| 1350 | 21.0 | 24.4 | – |
| 1500 | 18.5 | 23.2 | – |
| 1600 | – | 22.1 | – |
| 1800 | – | 20.0 | – |

**High-temperature tensile/yield strength** varies significantly by heat treatment (Table 6
summarizes ten AMS-specified treatments for different product forms/service ranges). Two
representative real data points, from Table 13 (¾-in. hot-rolled round, solution-treated +
furnace-cool precipitation-treated 1800°F/1hr, A.C. + 1350°F/8hr, F.C. to 1150°F — the
treatment aimed at "optimum tensile properties" below 1100°F, closest of the tabulated
conditions to a real chamber-liner/hot-structure use case):

| Test temp, °F | Tensile strength, ksi (MPa) | Yield strength (0.2% offset), ksi (MPa) | Elongation, % |
|---|---|---|---|
| Room | 195.5 (1348) | 140.0 (965) | 24.0 |
| 800 | 173.0 (1193) | 131.5 (907) | 21.0 |
| 1000 | 168.5 (1162) | 128.0 (883) | 13.0 |
| 1200 | 143.0 (986) | 122.5 (845) | 6.0 |
| 1350 | 114.0 (786) | 107.0 (738) | 5.0 |
| 1500 | 77.3 (533) | 76.8 (530) | 10.0 |

For the maximum-creep/rupture-strength triple heat treatment (2100°F/2-4hr + 1550°F/24hr +
1300°F/20hr, AMS 5668, aimed at service above 1100°F), rupture/creep data (Figures 14–20)
extend usefully to 1800°F, but as rupture-life-vs-stress-vs-time curves, not a single
yield-strength table entry — e.g. at 1800°F the alloy still shows a measurable (though low,
single-digit-ksi) rupture strength at 10–100 hr life (Figure 16).

No table in this datasheet gives a single tensile/yield number at exactly 1800°F — the
qualitative "useful strength up to 1800°F" claim (p.1) is supported only by the creep/
rupture/fatigue/hardness curves that extend that far (Figs. 2, 11, 14–20), not by a discrete
strength value.

## Caveats

- This is a general mill datasheet, not a propulsion-specific report — no chamber, nozzle,
  or turbopump application data of its own (contrast `[SP-8120]`, which independently names
  X-750 as a real F-1/J-2-era nozzle hatband alloy alongside Inconel 718).
- All mechanical-property tables are heat-treatment-specific; the alloy's usable strength
  varies by roughly 2× depending on which of the ~10 AMS treatments is used. The values
  pulled into `claude_lit/topics/12-materials-and-structures.md` use the solution-treated +
  furnace-cool precipitation-treated condition (Table 13) as the single representative
  condition, since it's the treatment aimed at real service strength rather than spring/
  wire-specific tempering.
- No single number exists for strength at the datasheet's own claimed 1800°F ceiling — any
  `materials.py` entry using 1800°F (1255 K) as `max_service_temp_k` is, like the existing
  `inconel_718` entry, extending past the last quantitative table point (1500°F here).
