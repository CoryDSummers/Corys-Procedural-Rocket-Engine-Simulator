# 02 — Nozzle contour design

## Scope

Shaping the divergent nozzle: conical vs bell, the Rao parabolic-approximation bell, the
%-bell convention, the wall-angle charts, and how contour choice maps to a divergence
efficiency. This is what `engine_designer/physics/nozzle_shapes.py` models.

## Key relations

**Conical nozzle** `[Huzel §4.3 p.89–90]`:
- Throat arc radius `R` = 0.5–1.5 × throat radius `Rt`.
- Convergent half-angle 20°–45° (Huzel worked examples use 20°–30°).
- Divergent half-angle α = 12°–18°; **15° is "almost a standard"** — the compromise of
  weight, length and performance.
- Length: `Ln = [ Rt·(√ε − 1) + R·(sec α − 1) ] / tan α`  `[Huzel eq. 4-7]`.
- Divergence / thrust-efficiency factor: **`λ = ½·(1 + cos α)`** `[Huzel eq. 4-8]`.
  α = 15° → λ = 0.983. The vacuum Cf of a 15° cone is 98.3 % of the ideal-nozzle Cf.

**Bell nozzle** `[Huzel §4.3 p.90–92]`, `[Sutton §3.4]`:
- Fast radial-flow expansion just downstream of the throat, then the wall turns the flow
  back toward axial. Contour changed gradually enough that no oblique shocks form.
- **%-bell convention**: a bell's length is quoted as a fraction of the length of a 15°
  half-angle conical nozzle *with the same throat area, same throat radius, and same
  expansion ratio*. An 80 % bell is 0.8 × that conical length.
- **Bell lengths beyond ~80 % add negligible performance** (Fig 4-12), and cost weight.

**Rao parabolic approximation** `[Huzel §4.3 p.91, Fig 4-13/4-14]`:
- Contour upstream of the throat: circular arc, radius **1.5·Rt**.
- Divergent contour: circular entrance arc of radius **0.382·Rt** from throat T to point N,
  then a **parabola** from N to exit E.
- Design inputs: throat diameter `Dt`; axial length `Ln` (or fractional length `Lf`);
  expansion ratio ε; **initial parabola wall angle θn**; **exit wall angle θe**.
- θn and θe are read from **Fig 4-14 as functions of ε**, parameterised by Lf
  (60/70/80/90/100 %). "No allowance is made for different propellant combinations; the
  effect of γ on the contour is small."

## Empirical correlations & typical values

**Rao wall angles vs ε (Fig 4-14, `[Huzel p.91]`, read off the chart — approximate):**

| ε | θn (Lf 60 % / 80 % / 100 %) | θe (Lf 60 % / 80 % / 100 %) |
|---|---|---|
| 5 | ~20° / ~21° / ~21° (curves bunched) | ~18° / ~14° / ~11° |
| 10 | ~25° / ~27° / ~28° | ~14° / ~10° / ~7° |
| 20 | ~30° / ~32° / ~33° | ~11° / ~7° / ~5° |
| 30 | ~33° / ~34° / ~29° | ~10° / ~5° / ~4° |
| 40 | ~37° / ~34° / ~30° | ~9° / ~4° / ~3.5° |

For θn the short bells (Lf 60 %) sit *above* the long ones; for θe the short bells sit
above too (they must turn the flow more sharply, then exit less axial). Precise anchor
point from the A-1 worked example: **ε 14, Lf 80 % → θn = 27.4°, θe = 9.8°**
`[Huzel Sample 4-2 p.96]`.

**%-bell length ratios** (from the same worked example, ε 14): an 80 % bell Ln = 102.4 in
vs a 15° cone of 128 in — i.e. 0.8×.

**Nozzle-type size comparison** `[Huzel Fig 4-15, ε 36]` (all scaled to same thrust, ε,
theoretical efficiency 98.3 %): conical = 100 % length; **80 % bell ≈ 74 % length**; spike
= 41 %; E-D = 41 %; R-F (Dp/Dt 5) = 25 %; H-F (Dp/Dt 10) = 14.5 %.

**Aerospike / annular** `[Huzel §4.3 p.92–95]`: altitude-compensating — the outer free-jet
boundary is set by ambient pressure, so Cf tracks the ideal (variable-area) nozzle rather
than dropping off at low Pe/Pa like a fixed bell. ε defined by projected area:
`ε = (Ae − Ap)/At` (eq 4-9). Disadvantages: higher cooling requirement (more surface, higher
flux), heavier structure, manufacturing difficulty.

**Real throat-radius design criteria** `[SP-8120 §3.1.1.1 p.65]`: bell-nozzle upstream wall
radius ratio Ru/Rt shall stay **> 0.6**; best efficiency/heat-load compromise is **Ru/Rt ≈
1.0**. Downstream: minimum tube-bend radius for tube-wall construction = **2× tube OD**
(ductile round tubes); narrative gives **Rd/Rt ≈ 0.4** as the real fabrication/length
compromise for tube-wall nozzles, and **Rd/Rt should not go below ~0.75** for 15°-half-angle
conical-divergence nozzles specifically (adverse-pressure-gradient heat-transfer concern). A
large-radius throat inlet (**Ru/Rt = 1.4**) has real precedent for aiding boundary-layer film
cooling through the throat.

**Real nonequilibrium-flow contour-control threshold** `[SP-8120 §3.1.2.1.1.2 p.66]`: when
chemical-kinetics losses matter (high-energy propellants, cited 5-10% loss otherwise), the
geometry from the throat to **area ratio ≈ 3** shall control the initial expansion rate to
hold composition near equilibrium — a specific, quotable threshold absent from `[Huzel]`/
`[Sutton]`'s treatment.

**Real separation-margin design criterion and closed-form correlation** `[SP-8120
§3.1.2.1.3 p.67-68, §2.1.2.1.3 p.17]`: if predicted exit wall pressure is **within 20% of
the separation pressure**, reduce area ratio or select a nonseparating contour — a real,
quotable safety margin, more specific than a bare Pe/Pamb threshold. A real closed-form
separation correlation (ref. 24): `Pwall/Pamb = 0.583·(Pamb/Pc)^0.195` — supersedes the
older flat "danger at Pe/Pamb = 0.4" rule of thumb cited in some other sources. Nonoptimum-
contour (canted-parabola) performance-loss tolerance: **~0.25%**.

**Real J-2 contour-manufacturing tolerances** `[SP-8120 §2.1.3 p.23, §3.1.3 p.70-71]`:
throat-diameter tolerance **±0.030 in. on a 14.7-in. throat**, circumferential contour
deviation **0.025 in./in.** (real large tube-wall-nozzle precedent); design-criteria wall-
angle tolerance downstream of the throat: **±1° for the first 10° of overturning, ±2° for
the rest of the nozzle**.

**Plug/aerospike — real (if non-closed-form) base-design guidance, a partial fill for the
"no base-flow physics anywhere" gap** `[SP-8120 §2.1.2.2/§3.1.2.2 p.20-23, 69]`: base bleed
introduced via a **porous plate** (favored, frees cavity volume for turbomachinery) or a
**deep-cavity base** (equal performance, radial injection) — highest base thrust comes from
introducing secondary flow with **minimum axial momentum**. Cycle-dependent guidance:
GG-cycle engines use truncated-ideal nozzles **with** base bleed (turbine exhaust dumped to
the base); topping/expander cycles must regeneratively cool the base plate **without** bleed,
or bleed only the minimum fuel needed. **Shrouded plug nozzles recommended for area ratio >
40 AND thrust < 1×10⁶ lbf**; very large engines should go unshrouded with a segmented
injector — a real, quotable selection criterion. Base-pressure prediction method: scale from
cold-flow model tests for truncated-ideal nozzles specifically (theoretical methods exist
only for other annular configurations); base heating "can be predicted only approximately and
must be verified experimentally" — still no closed-form base-pressure/heating equation, but a
real named methodology `[Aerospike-CR135231]` (which has zero base-flow content at all)
doesn't give either.

## Worked numbers

`[Huzel Sample 4-2 p.95–97]` A-1 stage, LOX/RP-1, Ftc 747 000 lbf SL, design SL Cf 1.531,
Pc 1000 psia, ε 14:
- At = 747000/(1.531·1000) = 487 in²; Dt = 24.9 in; Rt = 12.45 in
- De = √14·24.9 = 93.4 in; Re = 46.7 in
- L* = 45 in (LOX/RP-1) → Vc = 487·45 = 21 915 in³
- convergent cone (20° half-angle, εc 1.6, R = 1.5·Rt = 18.68 in): length 12.4 in,
  volume 7760 in³ → cylindrical section volume 14 155 in³ → cylindrical length 18.17 in →
  injector face to throat ≈ 31 in
- 80 % bell: throat-downstream arc R = 0.382·Rt = 4.75 in; Ln = 0.8·128 = 102.4 in;
  θn = 27.4°, θe = 9.8°; N at (Nc 2.19, Na 12.99) in

## Caveats

- The Rao contour skips the ~0.382·Rt throat fillet arc detail in some implementations
  (including `engine_designer`); this is a rendering / area-bookkeeping simplification, not
  a performance error.
- Fig 4-14 is a digitised chart read by eye; the numbers above are ±1–2°. For a precise
  contour use RPA or a method-of-characteristics solve (Huzel says "a computer program can
  be readily set up").
- `[Sutton §3.4]` treats the same material with modern framing (plug/aerospike/E-D
  comparisons, side-load discussion) and gives the loss-mechanism percentages — cross-read.

**Linear aerospike — real background material, NOT filling any current gap**
`[Aerospike-CR135231]`: a 1977 Rocketdyne NASA-Lewis study of a dual-fuel, modular,
split-combustor linear aerospike engine for a mixed-mode SSTO vehicle. `engine_designer` has
**no aerospike/plug-nozzle physics at all** (only conical and Rao-bell in
`nozzle_shapes.py`) — this source is reference material for a hypothetical future feature,
not a gap this batch fills. What makes a linear aerospike's contour genuinely different from
a bell: the contour is generated by a true method-of-characteristics solve of an ideal 2-D
planar spike (not a curve-fit to pre-computed bell families like Rao); the spike is
truncated and a shared "base closure" between module pairs replaces the missing tip — no
base-pressure/base-bleed/recirculation physics is given anywhere in the source, a real gap
relative to a full aerospike treatment; "automatic continuous altitude compensation" is
stated once as a known class property, never derived or quantified (no altitude-vs-Isp
curve). Throat geometry uses a "throat gap" (the narrow slot dimension) rather than a throat
radius. TVC has no gimbal at all — achieved purely by differential throttling between
opposing modules, via closed-form equivalent-gimbal-angle formulas, and the achievable
equivalent angles are small (single digits of degrees) even at ~50% throttling depth — a
real, quantified TVC-authority weakness vs. a gimbaled bell engine. Real point-design weight:
two ~4.5×10⁶ lbf-class engines at 20,070/22,850 kg. Scale mismatch: this study is orders of
magnitude larger than anything in `Engine_Configs/` or typically designed in
`engine_designer` — none of its absolute numbers should be reused without real scaling-law
justification.

## Implications for engine_designer

- `nozzle_shapes.py` `_THETA_N` (3×8, ~21–37°) and `_THETA_E` (3×8, ~26°→3°) tables on
  `_PERCENT_GRID = [60, 80, 100]` × `_EPS_GRID = [5, 10, 15, 20, 25, 30, 40, 50]` are
  **internally consistent and approximately track `[Huzel Fig 4-14]`**, but were not
  digitised from it. They can now be spot-checked against the chart values above and against
  the exact anchor **(ε 14, Lf 80 %) → (27.4°, 9.8°)** `[Huzel Sample 4-2]`. ASSUMPTIONS.md
  item #4 ("never checked against a real published Rao chart") can be downgraded to
  "cross-checked against Huzel Fig 4-14 to ±2°, anchored at ε 14 / 80 %."
- `reference_lambda(eps, %len=80)` and the `lam_relative = lam / reference` scoring: the
  80 %-bell reference is exactly the right baseline — `[Huzel Fig 4-12]` shows an 80 % bell
  captures essentially all the available Cf, so the propellant-pair calibration (which
  implicitly assumed a near-ideal nozzle) should be scored relative to it, not to λ = 1.
  This is the LMDE double-counting fix and the literature supports it.
- `cone_reference_length` using a 15° reference: matches the `[Huzel]` %-bell convention
  exactly (same throat area, throat radius, ε).
- `bell_percent_length` default 80 and the "beyond 80 % adds negligible performance" note in
  the README are both `[Huzel Fig 4-12]` / `[Sutton §3.4]` — good.
- Aerospike / E-D are declared out of scope (README "phase 2"); `[Huzel Fig 4-15]` gives the
  length-fraction data if that ever changes. `[Aerospike-CR135231]` (above) is now a real,
  much deeper reference if a linear-aerospike feature is ever attempted — real MOC contour
  method, cooling-circuit topology, structural layout, and differential-throttling TVC
  formulas, though it has no base-flow physics or altitude-compensation curve, and is
  scaled orders of magnitude larger than this project's typical engines. **`[SP-8120]`
  (2026-09-24 full read) partially fills the base-flow gap** — real base-bleed-vs-cavity
  design guidance, a real shrouded-vs-unshrouded selection criterion (eps>40 AND thrust<1e6
  lbf → shrouded), and a real (if non-closed-form) base-pressure prediction *methodology*
  (cold-flow-model scaling) — still no closed-form base-pressure equation from either
  source, but between the two there's now real design guidance where before there was none.
  Report-only.
- **Real, quotable separation-margin/contour-tolerance/throat-radius design criteria now
  exist from `[SP-8120]`** (2026-09-24 full read, see above): the 20%-of-separation-pressure
  margin rule and its closed-form `Pwall/Pamb` correlation are candidates if
  `nozzle_shapes.py`/`design.py` ever adds an explicit separation-margin check beyond
  whatever sea-level-flow-separation logic exists today; the real J-2 contour tolerances
  (±0.030 in./14.7 in., ±1°/±2° wall angle) are a real manufacturing-precedent anchor if a
  tolerance/manufacturability advisory is ever added. Report-only — no code changed.
