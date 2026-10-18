# NASA/TM-2000-210237 — Thermophysical and Thermomechanical Properties of Thermal Barrier Coating Systems

## Identity

Dongming Zhu (Ohio Aerospace Institute, Brook Park) and Robert A. Miller (NASA Glenn Research
Center), *Thermophysical and Thermomechanical Properties of Thermal Barrier Coating Systems*,
**NASA/TM-2000-210237** (performing-org report E-12356, WU-714-04-20-00), July 2000. It is an
invited paper for the 24th Annual Cocoa Beach Conference (American Ceramic Society), Jan 23-28,
2000. NTRS accession 20000083966. Renamed 2026-10-18 from its numeric NTRS filename.
- File: `literature/NASA TM-2000-210237 - Thermophysical and Thermomechanical Properties of
  Thermal Barrier Coating Systems.pdf`.
- 22 PDF leaves: leaf 0 = cover, 1 = CASI page, 2-18 = printed pp.1-17, 19 = SF 298, 20-21 blank.
- **Printed page = leaf − 1.**
- Tag: `[Zhu-TBC]`.

## Character

A short invited conference review from NASA Glenn's TBC group. The application is **gas
turbines and diesel engines, not rockets**. It summarises their laser heat-flux test method
and gives:
- one fitted **conductivity-change-kinetics equation** (Eq. 1) for plasma-sprayed
  ZrO2-8wt%Y2O3, with its source curves (Fig. 4);
- modelled through-thickness conductivity profiles (Fig. 5);
- an elastic-modulus evolution law (Eq. 2) and one profile figure (Fig. 6);
- a modelled stress-relaxation figure (Fig. 7);
- a qualitative failure-mechanism discussion (sintering + creep → tensile stress on cooldown
  → vertical cracking / delamination; bond-coat oxidation → spallation).

Most numbers come from the authors' own earlier reports (refs. 9, 11, 17, 18). This TM is a
digest, not the primary dataset. The text layer is a clean NTRS OCR. The equations on leaf 8
and Figs. 4-7 were **rendered and read visually**. Read in full.

**Best for:** a real, cited conductivity for *sprayed* (porous) yttria-stabilised zirconia, as
opposed to dense bulk zirconia; how fast that conductivity rises with time at temperature; and
the as-sprayed versus sintered modulus.

**It does NOT report** density, porosity percentage, CTE, emittance/emissivity, specific heat
or Poisson's ratio. Do not cite it for any of those.

## Property table — plasma-sprayed ZrO2-8wt%Y2O3 TBC

| Property | Value | Conditions / note | Cite |
|---|---|---|---|
| Intrinsic (dense) k, ZrO2-8wt%Y2O3 | **≈2.5 W/m·K** | material value; porosity lowers it | `[Zhu-TBC p.5]` |
| As-sprayed (initial) coating k | **≈1.0 W/m·K** | "typical plasma-sprayed" coat; from Miller & Leissler NASA TP-3296 (ref. 17) | `[Zhu-TBC p.5]` |
| Sintered k after ~30 h, 254 µm coat, 640 kW/m² (64 W/cm²) | **≈1.08 / 1.18 / 1.44 W/m·K** (data scatter to ~1.50) at surface 990 / 1100 / 1320 °C | the plateaux are temperature-dependent. Read visually from Fig. 4. | `[Zhu-TBC Fig. 4 p.8]` |
| Through-thickness average k after 20,000 s, surface 1315.5 °C | **⟨k⟩ = 1.170 / 1.215 / 1.277 W/m·K** at interface 871 / 982 / 1093 °C | printed in the Fig. 5(b) legend. Local k ≈1.45 at the surface, falling to ≈1.03-1.12 at the interface. | `[Zhu-TBC Fig. 5b p.9]` |
| As-sprayed compressive modulus, low stress | **34-64 GPa** | rises to **100-120 GPa** at higher stress-strain as microcracks close (ref. 11) | `[Zhu-TBC p.10]` |
| Modulus under laser sintering | **70 GPa initial → ≈125 GPa ("assumed final") at the surface in ≈20 h** | inner layers lag. Deep layers plateau at ≈0.3 on the normalised (E−E0)/(Einf−E0) axis (read visually, Fig. 6). | `[Zhu-TBC p.11, Fig. 6 p.12]` |
| Modelled in-plane compressive stress, thick TBC under a large gradient | near-surface layers peak at ≈800-1000 MPa within the first hours, then relax by creep. Inner layers rise to ≈600 MPa and hold. | model, not measured. Read visually from Fig. 7. Depth stations run to 1.56 mm, so the coating is ≥1.5 mm thick. | `[Zhu-TBC Fig. 7 p.13]` |
| System tested | ZrO2-8wt%Y2O3 / NiCrAlY bond coat / CMSX-4 single-crystal superalloy | Fig. 9. Interface ≈1100 °C, 35 h laser test plus a reheat. | `[Zhu-TBC Fig. 9 p.14]` |

## Key results

1. **Sprayed zirconia conducts much less heat than dense zirconia.** The intrinsic value is
   ≈2.5 W/m·K. A plasma-sprayed coat starts at ≈1 W/m·K because of its pores and microcracks
   `[Zhu-TBC p.5]`. Sintering raises it, but only to ≈1.1-1.45 W/m·K over tens of hours at
   990-1320 °C surface temperature `[Zhu-TBC Fig. 4 p.8]`.
2. **Conductivity-change kinetics, Eq. 1** (constants read visually from leaf 8)
   `[Zhu-TBC Eq. 1a-1b p.7]`:
   - (k_c − k_c⁰)/(k_c^inf − k_c⁰) = 102.2 · exp(−68228/RT) · [1 − exp(−t/τ)]
   - τ = 572.5 · exp(41710/RT)
   - k_c⁰ = initial k; k_c^inf = k at infinite time; τ = relaxation time.
   - The paper gives no units. Taking R = 8.314 J/mol·K, T in K and τ in s reproduces Fig. 4
     (derived here, not stated):
     - τ ≈ 3.7 h at 1320 °C, 6.1 h at 1100 °C and 8.4 h at 990 °C.
     - The saturation fraction is 0.59 / 0.26 / 0.15 at those three temperatures.
     - With k⁰ = 1.0, the Fig. 4 plateaux imply **k^inf ≈ 1.74 W/m·K**. That value is derived
       here and is not printed in the paper.
   - The prefactor 102.2·exp(−68228/RT) reaches 1 at ≈1500 °C. The fit therefore cannot be
     extrapolated above roughly that surface temperature.
3. **Sintering is fastest at first and near the hot face.** Fast early microcrack sintering
   gives the steep initial rise. The surface densifies faster than the cooler interface, so a
   k gradient builds through the thickness. A lower interface temperature gives a slightly
   lower average k, but the differences are small `[Zhu-TBC p.7-8, Fig. 5]`.
4. **EB-PVD coatings** sinter in-plane: the columnar grains "weld" together and form surface
   wedge cracks. Their long-term k rise is attributed to intra-columnar micropores closing.
   No EB-PVD numbers are given here (that is ref. 16) `[Zhu-TBC p.5]`.
5. **The modulus roughly doubles with sintering**, from 34-64 GPa as-sprayed to 70 → ≈125 GPa
   at the laser-sintered surface in ≈20 h. A higher modulus raises the thermal stress at a
   given strain, so the spallation driving force grows with time at temperature
   `[Zhu-TBC p.10-11, Eq. 2, Fig. 6]`.
6. **Life mechanism: time-at-temperature and cycling interact.**
   - Sintering and creep strains put the coat into tension on cooldown, which drives vertical
     cracks under LCF. Those cracks turn into delamination near the bond coat.
   - **Longer heating cycles or higher temperatures measurably speed up crack growth**
     `[Zhu-TBC p.12-13]`, from diesel-transient tests (refs. 20-21).
   - Bond-coat oxidation lowers adhesion: a 35 h laser exposure followed by one reheat gave
     buckling and spallation `[Zhu-TBC p.13, Fig. 9]`.
   - This is the qualitative "hold time shortens TBC life" statement. **No life equation or
     cycles-to-failure numbers are given.**
7. **Life prediction must be dynamic.** The delamination driving force rises and the
   resistance falls with time, so a life model needs time-evolving properties rather than
   as-sprayed constants `[Zhu-TBC p.2, Fig. 2 p.3]`.

## Relevance to engine_designer (report-only)

- `materials.LINER_MATERIALS["zirconia"].thermal_conductivity_w_mk` is 2.0 (ASSUMPTIONS.md
  zirconia-liner row, Tier 2 "bulk YSZ").
  - That sits between this source's dense intrinsic value (2.5) and its *sprayed-coating*
    values (1.0 as-sprayed, ≤1.45 sintered at ≤1320 °C, k^inf ≈1.74 derived).
  - The liner models a sprayed coat (0.076-0.25 mm per `[Quentmeyer-CR185257]` /
    `[TN-D3836]`), so 2.0 overstates k by ≈1.4-2×.
  - The computed thickness (`required_liner_resistance_m2k_w` × k) is therefore conservative
    by the same factor. As arithmetic, not a code result: the 0.15 mm C-103 case would need
    roughly 0.075-0.11 mm at k = 1.0-1.45.
  - Using 2.0 also widens the documented ~7 % vs ~50 % flux-cut gap in
    `validate.run_zirconia_liner_check` check (e), in the direction that makes the liner look
    weaker.
- **Burn-time scale:** at the liner's own 1500 K (1227 °C) service limit, τ is about 4.5 h.
  - One 500 s burn moves k only ~3 % of the way to its plateau (≈+0.01 W/m·K).
  - So sintering is a **cumulative multi-hour life effect**, not an in-burn one. It matters
    for a reusable/TestFlight life model (Round B "coatings") and not for a single-burn
    thermal solve.
  - Quentmeyer's coated-liner surface ran at ≈1944 K (1671 °C) `[Quentmeyer-CR185257 p.3]`.
    That is above where Eq. 1 is valid (item 2), so a rocket throat TBC lies outside this fit.
- `LinerMaterial.max_practical_thickness_m` (1.0 mm, Tier 3, "~4× the thickest cited").
  Figs. 6-7 model a thick plasma-sprayed TBC with depth stations to 1.16 and 1.56 mm. This
  shows >1 mm sprayed YSZ exists, in diesel service, with its own vertical-crack/LCF failure
  mode. It is a context point, not a rocket-liner limit.
- `LinerMaterial.max_service_temp_k` (1500 K, Tier 3). Not directly cited here. The paper does
  run coat surfaces at 990-1320 °C (1263-1593 K) for 30+ h without reported failure, so 1500 K
  is plausible-to-conservative as a surface temperature for an hours-scale exposure.
- **Not supplied:** `density_kg_m3` (5700), CTE, emissivity. ASSUMPTIONS ~237 gets nothing here.

## Section map

- Leaf 0-1: cover, CASI ordering page. Read.
- Abstract, p.1 (leaf 2). Read.
- Introduction, p.2-3 (leaves 3-4): two-layer TBC (YSZ top coat + bond coat), Fig. 1 micrographs
  (plasma-sprayed vs EB-PVD), Fig. 2 dynamic-life schematic. Read (Fig. 1 is a micrograph,
  caption only).
- Sintering and creep, p.4-5 (leaves 5-6): mechanisms (splat sliding, microcrack sintering;
  EB-PVD column welding). Read.
- Thermal conductivity, p.5-9 (leaves 6-10): intrinsic and as-sprayed k, the laser rig (Fig. 3),
  Eq. 1 kinetics, Fig. 4 k(t) at three temperatures, Fig. 5 through-thickness k. **Read visually**
  (leaves 8-10).
- Elastic modulus, p.10-12 (leaves 11-13): as-sprayed modulus range, Eq. 2, Fig. 6 E(t, depth).
  **Read visually** (leaf 13).
- Thermal fatigue and creep interactions, p.11-14 (leaves 12-15): Fig. 7 modelled stress
  relaxation, Fig. 8 vertical-crack micrograph, Fig. 9 delamination/buckling after 35 h. Read;
  Fig. 7 read visually, Figs. 8-9 caption only.
- Concluding remarks, p.15 (leaf 16). Read.
- References 1-21, p.15-17 (leaves 16-18). Read. Leads include: NASA CR-167868 (creep of
  plasma-sprayed zirconia), CR-182230 (TBC life-prediction model, Phase II), TP-3296
  (as-sprayed k source), TM-209069 (k and E evolution under high heat flux), TP-3676 (thick-TBC
  thermal fatigue).
- SF 298 (leaf 19). Read. Leaves 20-21 are blank.

## Caveats

- **Gas-turbine/diesel context.** The test heat flux is 0.64 MW/m², about 100× below a rocket
  throat (54 MW/m² in `[Quentmeyer-TMX73665]`). Exposure times are hours to days, against
  minutes per rocket burn. The substrate is a superalloy with a NiCrAlY bond coat, not copper
  with a NiCr bond coat.
- Eq. 1's units are not stated. The R / τ-in-seconds reading above is inferred from agreement
  with Fig. 4, and **k^inf ≈1.74 is derived**, not printed.
- Fig. 4 plateau values, the Fig. 6 deep-layer plateau and the Fig. 7 stress magnitudes were
  read visually from scanned plots, to about ±0.02 W/m·K and ±50 MPa.
- Fig. 5's coating thickness and heat flux are not stated. Its 444 K drop (1315.5 → 871 °C)
  across a coat with ⟨k⟩ ≈1.17 cannot be the 254 µm / 0.64 MW/m² Fig. 4 case. Treat Fig. 5 as
  an illustrative model.
- Only plasma-sprayed ZrO2-8wt%Y2O3 is quantified. The EB-PVD discussion is qualitative.
- No density, porosity %, CTE, emittance or cycles-to-failure data appear anywhere in the paper.
