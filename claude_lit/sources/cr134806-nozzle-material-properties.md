# NASA CR-134806 — Thrust Chamber Life Prediction, Vol. I: Mechanical and Physical Properties of High Performance Rocket Nozzle Materials

## Identity

John J. Esposito and Ronald F. Zabora (Boeing Aerospace Company, Seattle), *"Thrust Chamber
Life Prediction" Volume I — Mechanical and Physical Properties of High Performance Rocket
Nozzle Materials*, **NASA CR-134806**, Boeing report D180-18673-1, contract **NAS3-17838** Task I
final report, March 1975. NASA technical monitor: R. J. Quentmeyer. Technical leader: W. H.
Armstrong.
- File: `literature/NASA CR-134806 - Thrust Chamber Life Prediction Vol I - Properties of High
  Performance Rocket Nozzle Materials.pdf`. Renamed on 2026-10-16 from `NASA CR-134806.pdf`.
- 54 PDF pages: report documentation page, foreword, contents, 37 body pages, 4 reference
  pages, distribution list.
- Tag: `[CR134806-Props]`.
- Cited as Ref. 8 by `[Quentmeyer-TMX73665]`.
- Not the same report as `[Miller-CuFatigue]` (NASA CR-134841). That note's text mentions a
  "CR-134806-ish" OCR misread of its own filename.

## Character

A **properties compilation** (a literature search with "engineering judgment"), not a test
program and not a life method. It covers six candidate high-conductivity liner and closeout
metals: **Amzirc, NARloy-Z, OFHC copper, electroformed (EF) copper, fine silver and EF
nickel**.
- **Typical** room-temperature tables, plus property-vs-temperature curves from 27.6 K to
  810.9 K (−410 to 1000 °F).
- Static and cyclic stress-strain curves, and LCF strain-range vs. cycles-to-fracture curves at
  810 K, ε̇ = 0.002 s⁻¹.
- The authors stress that the data were "very limited", so **only typical (not minimum design)
  properties** were set.

**It contains NO creep or stress-rupture data.** Its reference list points to where such data
lived:
- D. C. Jerome & W. H. Armstrong, *NARloy Z Creep Test Report*, Boeing memo 5-9430-H-1357,
  July 1973 (internal).
- Conway, Stentz & Berling, *High-Temperature Low-Cycle Fatigue of Copper-Base Alloys in Argon,
  Part III — Thermal-Mechanical Strain Cycling, Hold-Time and Notch Fatigue*, Mar-Test
  MTI-R003-2-3, Dec 1973. This is the hold-time series, NAS3-16753, of which Part I is NASA
  CR-121259.

Text layer: room-temperature tables legible, the property-vs-temperature figures are not.
Three of the five LCF figures were rendered as images and read visually: Amzirc, NARloy-Z and
OFHC (Figs. 10, 19, 27). EF copper (Fig. 34), silver (Fig. 41) and the property-vs-T curves were
not digitized.

## Room-temperature typical properties

`[CR134806-Props §2.1-2.6 pp.4, 12, 19, 25, 30, 35]` (MPa from the source's MN/m². When the OCR'd
MPa digits and the ksi value disagree, the ksi value is used and the cell is marked *)

| Material / condition | UTS MPa | YS 0.2 % MPa | Elong % | RA % | E GPa | ν | ρ kg/m³ | c_p J/kg·K | k W/m·K | CTE 294-533 K, 10⁻⁶/K |
|---|---|---|---|---|---|---|---|---|---|---|
| Amzirc, annealed | 241 | 46 | 40 | 88 | 115 | 0.34 | 8885 | 385 | 390 | 17.2 |
| Amzirc, ¼-hard | 338 | 296 | 20 | 51 | 115 | 0.34 | ″ | ″ | ″ | ″ |
| Amzirc, ½-hard | 344 | 317 | 25 | 81 | 115 | 0.34 | ″ | ″ | ″ | ″ |
| **NARloy-Z, solution treated + aged** | **314** | **192** | 31 | 54 | **127** | 0.34 | **9134** | 373 | **295** | **17.2** |
| OFHC Cu, annealed | 221* (32 ksi) | 53 | 45 | 80 | 114 | 0.33 | 8913 | 386 | 390 | 17.2 |
| OFHC Cu, ¼-hard | 331* (48 ksi) | 310 | 20 | 66 | 114 | 0.33 | ″ | ″ | ″ | ″ |
| OFHC Cu, ½-hard | 344 | 317 | 25 | 80 | 114 | 0.33 | ″ | ″ | ″ | ″ |
| EF copper, as formed | 227 | 107 | 20 | 53 | 114 | 0.33 | 8913 | 385 | ~390 | (not legible) |
| Fine silver, as drawn | 289 | 283 | 5 | 85 | 71 | 0.37 | 10490 | 237 | 400 | 19.5 |
| EF nickel (sulfamate), as formed | 551 | 344 | 20 | — | 193 | 0.34 | ~8900 | 444 | 90 | 12.2 |

The source's EF-nickel density cell reads 8913, the same digits as copper, which is likely a
transcription error in the source.

## Low-cycle fatigue at 810 K

Total strain range vs. cycles to fracture, ε̇ = 0.002 s⁻¹, read from the figures to about ±10 %
`[CR134806-Props Figs. 10, 19, 27 pp.11, 18, 24]`:

| Material | Δε @ 10² | Δε @ 10³ | Δε @ 10⁴ |
|---|---|---|---|
| Amzirc ½-hard (curve labelled valid 5-870 K) | ≈7 % | ≈2.3 % | ≈0.85 % |
| NARloy-Z | ≈6 % | ≈2.0 % | ≈0.6 % |
| OFHC Cu, annealed | ≈2.2 % | ≈0.8 % | ≈0.42 % |

By strain range: Amzirc ≳ NARloy-Z ≫ annealed OFHC, about a 3× ratio at 10³ cycles. The same
uniaxial-basis ordering appears in `[Quentmeyer-TMX73665]`'s Ref. 6 comparison, which that
chamber test then contradicts on a wall-temperature basis.

**Design requirement quoted** `[§1.0 p.2]`: a future reusable high-Pc nozzle "may have the
requirement that it be capable of operating for **300 major thermal cycles for a total duration
of 10 hours**". The same passage gives SSME-class throat flux 80-100 Btu/in²·s (131-164 MW/m²)
against about 20 Btu/in²·s for then-current high-performance nozzles.

## Section map

§1.0 introduction (life-requirement framing) · §2.1 Amzirc (RT table p.4, Figs. 1-10) · §2.2
NARloy-Z (p.12, Figs. 11-19) · §2.3 OFHC (p.19, Figs. 20-27) · §2.4 EF copper (p.25, Figs.
28-34) · §2.5 fine silver (p.30, Figs. 35-41) · §2.6 EF nickel (p.35, table only) · §3.0
references (34, incl. the creep and hold-time sources above).

## Caveats

- **Typical, not design-minimum**, by the authors' own statement. Use these for physics and
  property inputs, not as allowables.
- LCF curves are isothermal, uniaxial, at 810 K and a 0.002 s⁻¹ strain rate. Real chamber
  ratcheting failures rank materials differently (`[Quentmeyer-TMX73665]`).
- No creep or stress-rupture data, so it does **not** close the copper-liner creep gap. The
  plan expected it would. It only points to the 1973 creep and hold-time reports listed above.
- Property-vs-temperature curves (k, E, UTS, YS vs. T) exist in the PDF but were not digitized
  in this pass. Render Figs. 4/5/6 (Amzirc), 14/15/16 (NARloy-Z) or 23/24/25 (OFHC) if a
  temperature-dependent value is needed.
