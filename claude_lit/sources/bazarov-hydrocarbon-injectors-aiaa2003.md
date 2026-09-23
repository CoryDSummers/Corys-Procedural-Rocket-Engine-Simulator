# [Bazarov] — Main Chamber Injectors for Advanced Hydrocarbon Booster Engines

## Identity

- **Title**: *Main Chamber Injectors for Advanced Hydrocarbon Booster Engines*
- **Authors**: Matthew R. Long (grad student), Vladimir G. Bazarov (visiting professor —
  the Bazarov of Russian swirl-injector-dynamics theory), William E. Anderson (asst.
  professor) — Purdue University School of Aeronautics and Astronautics
- **Report**: AIAA Paper 2003-3361, 39th AIAA/ASME/SAE/ASEE Joint Propulsion Conference &
  Exhibit, Huntsville AL, July 20–23, 2003. Funded by NASA MSFC (Grant NAG8-1894).
- **Extent**: 13 PDF pages, born-digital (not scanned) — clean-ish OCR/text layer but with
  frequent ligature corruption (`O/F`→`OIF`, `lb/s`→`Ibis`, `φ`→`rp`, `Π`→`IT`); treat any
  garbled symbol/equation as approximate, cross-check against the described physics.
- **PDF page = printed page** (both 1–13).

## Character

Not a general injector-design reference — a specific Purdue/AFRL R&D paper motivated by a
real capability gap: the **oxidizer-rich staged-combustion (ORSC) cycle** (LOX/kerosene,
warm oxidizer-rich gas + liquid fuel at the main injector) has 40+ years of Russian flight
heritage (NK-33/43/39, RD-120/170/180/191, RD-58) but **no published Western design
methodology** for its main-chamber injector as of 2003. The paper (a) surveys real
gas-liquid injector element types and their use/stability tradeoffs, (b) designs a
single-element "baseline" ORSC injector scaled from RD-170 patent + cycle data, (c)
presents the swirl-injector steady-state and dynamic-response theory used to size it, and
(d) reports early cold-flow (N₂/H₂O simulant) atomization results. This is the closest
real-world analog to `engine_designer/physics/injectors.py`'s element-geometry model
(velocities, orifice/momentum-ratio parameters, Cd, element subtypes).

## Real ORSC engines cited (p.2) — useful cross-check anchors

| Engine | F_vac (lbf) | Isp (s) | Pc (psia) | Role |
|---|---|---|---|---|
| NK-33 | 368,000 | 331 | 2150 | N-1 stage 1 (single chamber) |
| NK-43 | 394,517 | 346 | 2113 | N-1 stage 2 |
| NK-39 | 91,497 | 352 | 1360 | N-1 stage 3 |
| RD-120 | 187,266 | 350 | 2350 | Zenit stage 2 |
| RD-170 | 1,776,670 | 337 | 3553 | Energia / Zenit-3SL (4-chamber) |
| RD-180 | 933,407 | 337.8 | 3771 | Atlas III/V (2-chamber) |
| RD-191 | 467,603 | 337 | 3800 | Angara |
| RD-58 | 19,109 | 361 | 1131 | Proton/Energia upper stages — ORSC test-bed engine |

## Injector-element taxonomy (p.3–4) — extends the impinging/coax/pintle set

Classified by flow arrangement (gas outside/liquid inside vs. gas inside/liquid outside)
and whether flows are swirled:

1. **Shear coaxial** (neither swirled): simplest, tight packing, decent atomization. Used
   LOX/H2 staged combustion (Vulcain, RD-0120, SSME). Downside: sensitive to ΔP pulsation,
   prone to self-oscillation/"vibro-activity" → injector-face fatigue cracking.
2. **Swirl coaxial** (inner liquid swirled, outer gas unswirled): conical hollow liquid
   film atomized by surrounding gas — better/more uniform atomization, higher ṁ per
   element than shear coax. More complex; can form strong self-oscillations if the film
   design is off. LOX/H2 engines (RL-10 family).
3. **Bicentrifugal coaxial swirl** (both flows swirled): highest atomization/mixing
   efficiency of the coaxial family. Used in medium/low-thrust LOX/H2 or LOX/kerosene
   (Buran OMS/RCS). Downside: high sensitivity to chamber P/velocity disturbances + poor
   injector-face thermal protection → not used in high-thrust, high-Pc chambers.
4. **Gas-centered, liquid via radial drilled orifices into the gas core**: simple, good
   atomization/mixing, tunable gas-stage acoustics, mature design heritage. Used in
   medium-thrust, medium-Pc **hypergolic** engines. Downside: combustion zone sits right
   at the injector face with hot-gas reverse-flow recirculation → needs dedicated
   injector-face protection (e.g. a low-flow fuel swirl injector around the element).
5. **Gas-centered, liquid via tangential ports into an open vortex/swirl chamber around
   the gas core** ("axial gas core / centrifugal liquid annulus") — **this paper's
   baseline type**, the RD-120/170/180 family element. Forms a fuel-rich liquid film at
   the vortex-chamber periphery that both improves atomization (thin rotating film vs.
   coax's thicker sheet) and passively cools/protects the injector face; the gas cavity
   doubles as a half-wave acoustic (Helmholtz-like) resonator, bleeding acoustic energy
   from the chamber to the gas manifold. **Lower sensitivity to chamber-pressure
   pulsation than any other type here** because the liquid film is stabilized on the
   vortex-chamber wall rather than free-shear-atomized. Poor atomization at low Pc/gas
   density, but works well at the high Pc ORSC engines run at. More complex to size/model
   than the others (this paper's own subject).

## Baseline injector design method (p.4–6) — what to reuse

Scaled from three open sources (RD-170 patent US 6,244,041 B1, Manski et al. cycle data,
Sutton & Biblarz): RD-170 patent showed 271 total elements (incl. baffle/near-wall) →
thrust/element ≈ 1700 lbf at RD-170's full Pc 3720 psia. Test article de-rated to
**Pc = 2150 psia** for facility safety; throat diameter set to a manufacturable/coolable
1.0 in (vs. the 0.7 in a literal thrust/element scale-down would give) → single-element
vacuum thrust ≈ 3000 lbf, contraction ratio 2.25 (RD-170 itself: 1.61).

| Parameter | Value |
|---|---|
| Pc, injector face / throat entrance | 2263 / 2150 psia |
| C_Fv (vac thrust coeff.) | 1.83, η_CFv = **0.98** |
| c* | 5860 ft/s, **η_c\* = 0.97** |
| Isp_vac | 317.0 s |
| ΔP_ox / ΔP_f | 226 / 226 psid (each ≈ 10.5 % of Pc) |
| U_ox / U_f | 400 / 204 ft/s |
| O/F (main injector) | 2.87:1 (vs. 55.5:1 at the ORPB feeding it fuel-lean warm gas) |
| Throat / exit dia., ε_n | 1.0 in / 4.15 in, ε = 17.2 |

`η_c* = 0.97` and `η_CFv = 0.98` are real, directly-quotable ORSC/gas-centered-swirl
efficiency anchors — same role as `[KBKhA]`'s RD-0110/RD-0124 table for
`combustion.py`/`design.py`'s efficiency constants.

**Swirl-stage sizing** (Bayvel swirl-injector model, ref. 13): non-dimensional geometric
characteristic `A = R_in·R_n / (n·r_in²)` (eq. 9) sets the liquid-fill fraction φ of the
nozzle cross-section via `A = (1-φ)·√φ / φ^1.5`-type relation (eq. 8–9, garbled in OCR —
treat as "standard Bayvel swirl theory", cite the mechanism not the exact algebra); φ then
gives liquid vortex-core radius, film radius at the nozzle, and axial velocity (eq. 10–15).
Because this baseline design fixes the vortex-chamber bore equal to the nozzle exit bore
("straight bore"/open type), the swirl solution is uniquely determined by mass flow + ΔP —
no free geometric parameter to iterate, which is why the paper calls it the *simplified*
open-swirl case.

**Atomization (Kelvin-Helmholtz) correlations** (eq. 2–5, cited from other shear-coaxial
work, *not* validated here for the gas-centered-swirl baseline): SMD
`d32|μ=0 = C1·σ/(ρ_g·|U_g−U_l|²)`, with liquid-viscosity correction via C2; mass-stripping
rate `∂ṁ/∂S = C3·|U_g−U_l|·√(ρ_g·ρ_l)` with viscosity correction C4. For shear-coaxial:
C1=62, C2=0.035, C3=0.17, C4=−0.16 (dimensional empirical constants — units-dependent, not
portable without checking Long/Bazarov's unit system).

**Injector dynamic response** (eq. 16–20): total complex response function Π built from
tangential-channel (Πr), vortex-chamber (Πvn), nozzle (Πn), and closed-end/feedback (Πvc)
sub-responses. Key qualitative result: the **open** (through-flow, no closed end) swirl
injector has the *lowest* pulsation response of all swirl-injector variants — no reflected
waves, so Πvn/Πn ≈ 1 (pure phase shifters) and Πvc becomes quasi-stationary. This is the
mechanism behind item 5's superior chamber-pressure-pulsation immunity above.

## Cold-flow test findings (p.9–13)

- Two candidate correlating parameters tested: **differential velocity** ΔU =
  U_g,axial − U_l,film (eq. 22) and **momentum flux ratio** MFR = ρ_g·U_g²/(ρ_l·U_l²)
  (eq. 23). Result: **ΔU dominates** — the MFR survey (fixed geometry/ṁ, chamber P swept)
  showed "little to no significant change" in spray character, while the ΔU survey drove
  clear atomization-quality trends. Direct implication for `injectors.py`: if it exposes
  a momentum-ratio metric for coax/swirl-type elements, gas-liquid **velocity difference**
  may be the more physically load-bearing knob to check/display, not MFR alone.
- Gas as little as 0.07 lb/s N₂ was enough to collapse the pure-liquid conical swirl sheet
  into an atomized spray once gas flow started.
- Fine, symmetric sprays at gas:liquid ≈ 0.15:1 mass ratio; measured SMD ≈ 65 μm.
- A related Sierra Engineering/AFRL gas-centered-swirl study (converger/diverger/prefilmer
  exit variants, refs. 7–8) got **c\* efficiency > 90 %** with mean drop sizes 3–4× finer
  than equivalent shear-coaxial elements, but some variants showed **"chug" instability**
  at certain operating points — a concrete stability-vs-atomization tradeoff data point.

## Section map

| Section | p. | Content |
|---|---|---|
| Abstract / Nomenclature | 1 | Full symbol table |
| History of ORSC cycle & injectors | 2–4 | Real-engine table above; 5-type taxonomy |
| Selection of geometry & operating conditions | 4–5 | RD-170-patent-scaled baseline sizing, Tables 1–3 |
| Injector design analysis | 5–9 | Swirl sizing (Bayvel), atomization correlations, dynamic response Π |
| Cold flow tests | 9–13 | AFRL facility, ΔU vs. MFR surveys, patternation/PDPA results |
| Summary & Conclusions | 13 | — |
| References | 13 | 17 refs, several are other Bazarov papers (dynamics/self-pulsation/stability) worth knowing exist if deeper injector-dynamics material is ever needed |

## Caveats

- A **status report on ongoing research**, not a validated final design — the paper says
  its own equations "will be verified in tests later this year." Treat the sizing method
  as methodology, not as validated-against-hardware numbers (unlike `[TN-Dump]`, which is
  a full built-and-fired test report).
- The atomization SMD correlations (C1–C4) are explicitly for shear-coaxial elements,
  imported for comparison — do not apply them to the paper's own gas-centered-swirl
  baseline without the same caveat the paper itself gives.
- Single-element, sub-scale (3000 lbf vs. RD-170's 465,000 lbf/chamber), de-rated Pc
  (2150 vs. 3720 psia) — geometry and ΔP numbers don't scale directly to a full engine.
- OCR/rendering artifacts on multi-part equations (esp. eq. 8–15, the swirl-theory core)
  are worse than the prose — re-derive from a primary swirl-injector-theory source
  (Bayvel & Orzechowski, *Liquid Atomization*, ref. 13) before hard-coding any of them.
