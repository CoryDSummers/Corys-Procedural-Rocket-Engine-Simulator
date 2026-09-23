# 04 — Chamber sizing (L*, contraction ratio, shape)

## Scope

Sizing the combustion chamber: characteristic length L\*, contraction area ratio εc, stay
time, chamber shape, and the surface area to be cooled. Feeds
`engine_designer/physics/geometry.py`.

## Key relations

**Chamber volume** `[Huzel eq. 4-3 p.86]`, `[Sutton eq. 8-8]`:

    Vc = ṁ_tc · V̄ · ts          V̄ = mean specific volume (ft³/lb), ts = stay time (s)

**Characteristic length** `[Huzel eq. 4-4 p.86]`, `[Sutton eq. 8-9 p.284]`:

    L* = Vc / At

The chamber volume `Vc` **includes everything up to the throat plane — the cylindrical
section plus the convergent-cone frustum** (both sources state this explicitly). L\* is "the
length a chamber of the same volume would have if it were a straight tube with no converging
section" `[Sutton]`.

**Stay time** `[Sutton eq. 8-10]`: `ts = Vc / (ṁ · V̄)`. Since `At ∝ ṁ·V̄` for a given
propellant, **L\* is essentially a proxy for stay time** `[Huzel §4.3 p.87]`.

**Chamber wall surface area** `[Huzel eq. 4-6 p.89]`:

    A_total ≈ 2·Lc·√(π·εc·At)  +  csc θ · (εc − 1) · At     (cylinder + convergent cone)

## Empirical correlations & typical values

**Recommended L\* by propellant** `[Huzel Table 4-1 p.87]`:

| Propellant combination | L\* (in) | L\* (m) |
|---|---|---|
| ClF3 / hydrazine-base fuel | 30–35 | 0.76–0.89 |
| LF2 / hydrazine | 24–28 | 0.61–0.71 |
| LF2 / LH2 (GH2 injection) | 22–26 | 0.56–0.66 |
| LF2 / LH2 (LH2 injection) | 25–30 | 0.64–0.76 |
| **H2O2 / RP-1** (incl. catalyst bed) | **60–70** | 1.52–1.78 |
| Nitric acid / hydrazine-base fuel | 30–35 | 0.76–0.89 |
| **N2O4 / hydrazine-base fuel** | **30–35** | 0.76–0.89 |
| LOX / ammonia | 30–40 | 0.76–1.02 |
| LOX / LH2 (GH2 injection) | 22–28 | 0.56–0.71 |
| LOX / LH2 (LH2 injection) | 30–40 | 0.76–1.02 |
| **LOX / RP-1** | **40–50** | 1.02–1.27 |

`[Sutton §8.2 p.284]`: "Typical values for L\* are between **0.8 and 3.0 m** (2.6 to 10 ft)
for several bipropellants and higher for some monopropellants." Sutton adds that L\* is
somewhat deprecated in modern practice (chamber volume now scaled from prior similar
designs) but remains a useful proxy.

Real engines `[Sutton Table 8-1]`: RL10B-2 L\* 30.7 in (0.78 m); R-4D-class 18 in (0.46 m);
RS-27 (LOX/RP-1) 38.7 in (0.98 m); AJ-10 (N2O4/A-50) 30.5 in (0.77 m); LE-7 not tabulated.
`[TN-Dump]`: 20 in (0.51 m) for a 500-lbf GH2/LOX engine. Small thrusters genuinely need
much smaller L\* than the table minima because L\* is a fixed length, not scale-relative.

**Contraction area ratio εc = Ac/At:**
- `[Huzel §4.3 p.87]`: pressurized-gas-fed low-thrust engines **2–5**; turbopump-fed
  high-thrust / high-Pc engines **1.3–2.5**.
- `[Sutton §8.2 p.283]`: gas acceleration pressure loss "becomes appreciable when the
  chamber area is less than three times the throat area" — i.e. εc < 3 starts to cost
  performance; real engines accept that for mass/envelope reasons.
- Real engines `[Sutton Table 8-1]`: RL10B-2 2.87, LE-7 6.0, R-4D-class 1.67, RS-27 2.54.
  `[TN-Dump]` = 3.

**Chamber shape** `[Huzel §4.3 p.87–88]`, `[Sutton §8.2]`: sphere has the smallest
surface/volume (least cooling area, ~half the wall thickness of a cylinder for equal
strength) but is hard to build and generally lower-performing → **cylindrical chamber with a
flat injector** is standard US practice. Long/narrow → higher non-isentropic pressure loss,
longer envelope, injector-hole crowding. Short/wide → the atomization zone occupies too much
of the volume and the mixing/combustion zone is too short.

**Convergent half-angle**: Huzel worked examples use 20°–30°; `[Huzel §4.3]` cites 20°–45°
for the convergent cone.

## Worked numbers

`[Huzel Sample 4-2 p.96]` A-1, LOX/RP-1: At 487 in², L\* 45 in → Vc 21 915 in³. Convergent
cone (20° half-angle, εc 1.6, R 1.5·Rt = 18.68 in): length 12.4 in, volume 7760 in³.
Cylindrical section: 21 915 − 7760 = 14 155 in³ → length 14 155/(1.6·487) = 18.17 in →
**injector face to throat ≈ 31 in**. This is exactly the `Vc = L*·At` including the cone,
then subtract the cone frustum to get the cylinder length — the pattern `geometry.py` uses.

## Caveats

- L\* tables are for "essentially complete combustion" with a good injector; a poorer
  injector needs more L\*, a better one less. The only way to pin the minimum is a hot
  firing `[Huzel §4.3]`.
- L\* is only comparable within one propellant combination and a narrow Pc / MR range
  `[Sutton §8.2]` — it does not carry γ, M or injector quality.
- The `[Huzel Table 4-1]` minima (~22 in) are for large chambers; genuinely small thrusters
  operate far below them (see topic 05 on catalyst beds, and `geometry.py`'s small-engine
  fix).

## Implications for engine_designer

- `geometry.py::chamber_geometry` computes `At = ṁ·c*/Pc`, `Ac = CR·At`,
  `Vc_total = L*·At` **including the convergent cone**, then subtracts the frustum volume to
  get the cylindrical length — this is exactly `[Huzel Sample 4-2]`. The docstring's
  size-independence bug fix (old `Lc = L*·At/Ac` cancelled `At`) is correct: L\* is a fixed
  length, and the worked example confirms the volume-then-subtract approach.
- L\* slider range down to 0.02 m: justified — small thrusters need L\* well below the
  `[Huzel Table 4-1]` bipropellant minima (0.5–1.8 m). The `LSTAR_TYPICAL_M = (0.02, 3.0)`
  warning band's upper end matches `[Sutton]`'s "0.8–3.0 m"; the lower end is a small-engine
  allowance not in the literature (flag stays, but it's physically necessary).
- `contraction_ratio` default 1.6 and `CONTRACTION_RATIO_TYPICAL = (1.3, 6.0)`: the low end
  matches `[Huzel]`'s "1.3–2.5 for turbopump-fed"; the high end (6.0) matches LE-7's 6.0
  `[Sutton Table 8-1]` and Huzel's "2–5 for pressure-fed". Well-supported.
- `CONVERGENT_HALF_ANGLE_DEG = 30.0` (Tier 3): inside `[Huzel]`'s cited 20°–45° convergent
  range; 20° would match the worked examples more closely but 30° is defensible.
- The completeness curve (topic 03) is the mechanism by which L\* affects c\* in the tool;
  `[Huzel Fig 4-7]` (c\* → asymptote with L\*) is its shape.
- Per-pair L\* defaults for the tool's five pairs could be seeded from `[Huzel Table 4-1]`:
  LOX/RP-1 40–50 in (1.0–1.3 m), LOX/LH2 22–40 in (0.56–1.0 m), N2O4/MMH ≈ N2O4/hydrazine
  30–35 in (0.76–0.89 m), Aerozine-50/NTO same, Hydrazine (monoprop, catalyst bed) high —
  H2O2/RP-1 "incl. catalyst bed" is 60–70 in, so a hydrazine catalyst bed is plausibly
  0.5–1.5 m.
