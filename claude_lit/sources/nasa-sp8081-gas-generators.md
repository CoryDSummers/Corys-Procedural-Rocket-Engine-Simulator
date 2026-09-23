# [SP-8081] — Liquid Propellant Gas Generators (NASA SP-8081)

## Identity

- **Title**: *Liquid Propellant Gas Generators*
- **Series**: NASA SP-8081, NASA Space Vehicle Design Criteria (Chemical Propulsion)
- **Author**: Howard C. Zehetner, Rocketdyne Division, North American Rockwell; edited by
  Russell B. Keller, Jr., NASA Lewis. Reviewers from Aerojet, Bell Aerospace, NASA Lewis.
- **Date**: March 1972. NTIS price $3.00.
- **Extent**: body to ~printed p.99, 116 PDF leaves. Scanned + OCR; OCR layer has no spaces
  between words (readable but slow — use a word-rejoin filter). Few equations; this is a
  practice / criteria document, not a formula source.
- **PDF leaf ↔ printed page**: `leaf ≈ printed page + 12` (State-of-the-Art body starts
  printed p.3 = leaf ~15).

## Character

The entire document is **turbine-drive gas-generator design**. Design-Criteria monograph
format: §2 *State of the Art* (narrative, with real-hardware history) and §3 *Design
Criteria and Recommended Practices* (the same content restated as firm rules — usable as a
checklist), decimally parallel. Auxiliary-power, pressurization and preburner GGs are
explicitly out of scope.

## The one theme

**Hot streaking / turbine-inlet temperature stratification.** Turbines have hard temperature
limits; local combustion temperature can far exceed the mixed-gas temperature; any design
that lets combustion happen near a wall, or that mixes hot and cold streams too slowly,
causes a burnout. Everything in the monograph is in service of controlling where combustion
happens and how fast hot and cool streams mix. Combustion *efficiency* is ~100 % in a GG
(large fuel excess) and is not the problem — mixing is.

## Table I — Design Characteristics of Operational Gas Generators for Turbine Drive (printed p.4)

Real GG parameters for F-1, M-1, J-2, H-1, E-1, Atlas (sustainer/MA-2/MA-3), Thor, Titan II
(1st/2nd), Jupiter, Redstone, Navaho, Vanguard:

| Quantity | Range across the fleet |
|---|---|
| Gas temperature | 1000–1660 °F (811–1178 K); most cluster **1200–1400 °F (922–1033 K)** |
| Chamber pressure | 450–1100 psi (3.1–7.6 MN/m²) |
| Stay (residence) time in chamber | **2.3–10.5 msec** |
| Turbine power | 371 BHP (Agena) … 117 000 BHP / 87 MW (M-1) |
| Injector types used | doublet, triplet, coaxial, poppet, swirl-nozzle, jet-stream |
| Chamber materials | Hastelloy C, N-155, CRES (347 stainless), Nickel, Aluminium, Haynes 25 |
| Flow path | mostly "Reverse", some "Axial" |

F-1 GG example: LOX/RP-1, 170 lb/s (77.25 kg/s), 1500 °F (1089 K), 1000 psi, doublet
injector (CRES/copper), Hastelloy C chamber, reverse flow, 55 000 BHP (41 MW).

## Design facts worth reusing

- **Mixture ratio**: "normal" bipropellants run **fuel-rich MR 0.2–1.0** (hydrocarbons ~0.3
  low end, hydrogen 0.98–1.0 high end). "Energetic" propellants (Aerozine-50, UDMH,
  hydrazine) run MR < 0.2 and can suffer reaction instability / flameout; 1000–1400 °F
  (811–1033 K) is the range conducive to that instability.
- **Why fuel-rich**: (1) a fuel-rich hot streak is far less damaging than an oxidizer-rich
  one; (2) turbine specific propellant consumption is better with low-molecular-weight
  fuel-rich gas.
- **Oxidizer-rich bipropellant GGs**: studied, essentially no Western applications as of
  1972 (chamber-burning risk, NO₂ decomposition losses, corrosive HNO₃ atmosphere with
  N₂O₄). (Later a Soviet/Russian speciality — see `[KBKhA]`.)
- **Vaporization + mixing timescales are several milliseconds** — much slower than a thrust
  chamber. Consequence: GGs need finer-stream injectors and mechanical mixing devices; the
  combustion zone is wider and the mixing zone much longer than in a thrust chamber.
- **Chamber sizing**: L\*, stay time, and volumetric loading have all been tried; **stay
  time is the most useful**. Atlas-sustainer GG data: below 3–4 msec mixing is inadequate
  and hot spots appear; above 6–10 msec the safe-operation margin grows with stay time.
- **Injector evolution**: hot-core injector (all oxidizer central + enough fuel for a
  near-stoichiometric core, rest of fuel dilutes around the outside) → **uniform-mixture-
  ratio (UMR)** injector (every element at the overall MR; a multitude of small hot zones
  quenched fast by intimately-mixed excess fuel). Nearly every hot-core GG (Navaho, Atlas
  MA-3, Thor, Jupiter, J-2, Titan I/II) had a long, severe failure history; UMR streaking
  problems were "an order of magnitude easier to solve."
- **UMR vs hot-core** (ref. 14 comparison, LOX/RP-1): at a given MR, UMR gives higher
  temperature and higher c\*; at a given temperature, c\* is the same.
- **Element flow limits**: coaxial elements act like mini hot-cores; they behave more like
  UMR below ~0.5 lb/s (0.23 kg/s) per element. Small triplets at ~0.1 lb/s (0.045 kg/s) per
  element give minimum streaking. M-1's large concentric-tube UMR elements caused
  temperature gradients 42 in (107 cm) downstream of the injector.
- **Mixing chambers**: reverse-flow (stagnate then reverse direction) achieves <50 °F
  (28 K) outlet variation at 1400 °F rated, at ~⅓ the pressure loss of the turbulence-ring
  approach. "Momentum separation" — a hot, high-velocity core does not turn as readily as
  cool gas, so mixing must be finished inside the chamber before the outlet.
- **Potential-core length** (ref. 3 theory): axial-flow `X = 4.55·H` (H = radius of the
  larger wall / passage enlargement); a separate reverse-flow correlation is given at ref. 3
  p.460. Mixing completes a short distance beyond. "No evidence this theory has been used to
  design a new GG, but even in its simplest form it gives more guidance than thrust-chamber
  parameters."
- **Materials**: 1200 °F (922 K) service → 347 CRES; higher temp or weight saving →
  Hastelloy C (J-2, F-1), N-155, Hastelloy X, Haynes 25 (brittle). Atlas S-4 GG ran 347
  CRES at 1400 °F, later reduced to 1200 °F to avoid coking.
- **Thermal protection**: early F-1 had a regeneratively-cooled GG; modern practice is
  **uncooled solid wall + film cooling** (crucial in the burning zone before mixing is
  complete).
- **Ignition**: most GG propellants do not autoignite; pyrotechnic cartridges (usually two
  for redundancy); spark plugs where chilldown/restart is needed (J-2). LH2 is harder to
  ignite than RP-1 (spontaneous ignition temp ~1000 °F / 811 K vs RP-1 igniting with GOX at
  room temperature).

## Section map (State-of-the-Art page / Design-Criteria page)

- 2.1 Bipropellant GGs (3 / 67): 2.1.1 Chamber (shape, size, exhaust outlet, mixing
  baffles/turbulence rings, mounts, thermal protection, materials, fabrication); 2.1.2
  Injector (types, elements, orifices, film-cooling orifices, poppet valves, manifolds,
  interpropellant seals, materials); 2.1.3 Accessories (igniters, boss, flanges, fasteners,
  auxiliary injectors, drains)
- 2.2 Monopropellant GGs (45 / 80): chamber, catalyst bed/pack (silver screen for H2O2,
  iridium for hydrazine — iridium supply-limited), injector, accessories
- 2.3 Common problems (61 / 87): pressure & temperature measurement (thermocouple survival
  in hot streaks; tap placement)
- 2.4 Testing (62 / 88)

## Caveats

- Practice/criteria, not equations — few closed-form relations. Pair with `[Huzel]` §4.6 and
  `[Sutton]` §10.1 for the turbine-drive power balance.
- 1972 vintage; predates staged-combustion preburner practice (which is a different beast —
  see `[KBKhA]`).
