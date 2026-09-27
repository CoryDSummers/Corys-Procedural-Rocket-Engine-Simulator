# SP-8125 — Liquid Rocket Engine Axial-Flow Turbopumps

## Identity

NASA SP-8125, *Liquid Rocket Engine Axial-Flow Turbopumps*, NASA Space Vehicle Design
Criteria (Chemical Propulsion), April 1978. Authors D. D. Scheer (Lewis), M. C. Huppert
(Rocketdyne), F. Viteri and J. Farquhar (Aerojet); ed. R. B. Keller Jr. (foreword, leaf 2).
`literature/NASA SP-8125 - Liquid Rocket Engine Axial-Flow Turbopumps.pdf` (NTRS 19780023221;
129 PDF leaves). The cover's text layer is garbled; the SP number and date were confirmed by
rendering leaf 1 as an image ("NASA SP-8125 ... APRIL 1978"). Fixed offset: printed page N =
PDF leaf N+11 (1-based; fitz index N+10). For example, printed p.1 "INTRODUCTION" is leaf 12,
and Table I on p.4 is leaf 15. Tag: `[SP-8125]`.

## Character

This monograph belongs to the same family and uses the same structure as `[SP-8109]`
(centrifugal pumps, its ref. 1) and `[SP-8107]` (turbopump systems, its ref. 7, which holds
the pump-type selection and speed-selection criteria). §2 "State of the Art" is narrative
(p.3-67). §3 "Design Criteria and Recommended Practices" (p.68-92) gives the imperative
"shall"/"recommended" rules, and its subsection numbers mirror §2's. The whole monograph rests
on **five axial-flow LH2 pumps and no others**. Every axial rocket pump ever built into an
engine at that date was an LH2 pump:

- **Mark 9**: Phoebus nuclear engine, development.
- **Mark 15-F**: the **J-2 fuel pump**. It was the only one that saw operational service,
  on S-II and S-IVB.
- **Mark 25**: Phoebus, development.
- **Mark 26**: an experimental J-2 uprate of the 15-F.
- **M-1**: the Aerojet M-1 engine, development, terminated.

The monograph also uses some NASA Lewis research rotors (hub/tip 0.4/0.7/0.8) and Rocketdyne
research stages "A"-"E". **SSME and NERVA-flight pumps are not covered.** The SSME has
centrifugal pumps; Phoebus is the only nuclear application. Stage hydrodynamics is imported
from 1950s-60s axial-*compressor* practice (NASA SP-36, its ref. 18), and the monograph says
explicitly that it does not include later compressor technology.

Structure: §1 Introduction (p.1-2), §2 State of the Art (p.3-67), §3 Design Criteria
(p.68-92), App. A SI conversion (p.93), App. B Glossary (p.95-103), References (p.105-110).
§2 and §3 each contain:
- 2.1 Overall Turbopump Design (speed, rotor dynamics)
- 2.2 Stage Design (realm of operation; hydrodynamics: blade loading/stall margin/efficiency,
  velocity diagrams, blade angles, solidity, cavitation, off-design, clearances)
- 2.3 Pump Rotor Assembly (blades, blade attachment, rotor, axial thrust balance)
- 2.4 Pump Stator Assembly (vanes, vane attachment, stator/volute housings, bearing housings,
  interfaces/static seals)
- 2.5 Materials
- 2.6 Safety Factors

## This note's extraction scope

**Read in full:**
- §1-2.2 (leaf 12-46). This covers Table I (the fleet table), Fig. 1 (head/efficiency curves),
  Fig. 4 (Ns-Ds chart), Table II (stage design data), Table III (profile geometry) and Figs.
  7/9/11, all rendered to PNG and read visually.
- §2.3 Rotor Assembly (leaf 46-64).
- §2.4.1-2.4.4 (leaf 65-72).
- §2.5 Materials and Table IV, rendered (leaf 74-76).
- §2.6 Safety Factors (leaf 75-78).
- The §3 design criteria: §3.1-3.3.4 (leaf 79-96) and §3.4.5.2.3-3.5 (leaf 102-103).
- The glossary symbol definitions (leaf 109-112) and the first 13 references.

**Skimmed or not read:**
- §2.4.5 interfaces/static seals: skimmed.
- §3.4.1-3.4.5 stator/housing design criteria (leaf 97-101): skimmed at header level only.
- Leaf 87 (Fig. 31, the Goodman safety-factor diagram): figure only; its content is
  restated in the text.
- The remaining references: not read.

## Key results

**Real axial-pump fleet table** `[SP-8125 Table I p.4]`. Headrise is overall, inducer inlet
to volute discharge.

| Pump | Flow, gpm | Headrise, ft | Speed, rpm | Stages | Application |
|---|---|---|---|---|---|
| Mark 9 | 10,230 | 51,500 | 32,800 | inducer + 6 main | Phoebus (dev.) |
| **Mark 15-F** | **9,062** | **40,300** | **28,266** | **inducer + 7 main** | **J-2 (operational)** |
| Mark 25 | 18,500 | 62,000 | 34,000 | tandem inducer + 4 main | Phoebus (dev.) |
| Mark 26 | 9,000 | 40,000 | 24,000 | inducer + 7 main | J-2 (experimental) |
| M-1 | 62,300 | 56,500 | 13,225 | inducer + transition + 8 main | M-1 (dev.) |

**Stage design data** `[SP-8125 Table II p.17]`. Radii are in inches. The unit is not
printed in the table, but it is confirmed by the M-1 Ds cross-check below. ν = hub/tip ratio.
Tip-referenced flow and head coefficients are φ_T = V_m/U_T and ψ_T = g_c·H/U_T².
Ns = N·Q^½/H^¾ in rpm·gpm^½/ft^¾ (US units, glossary p.99-100). η is the *stage hydraulic*
efficiency. DF is the diffusion factor.

| Stage | r_H | r_T | ν | φ_T | ψ_T | Ns | Ds | η | DF rotor hub/tip | DF stator hub/tip |
|---|---|---|---|---|---|---|---|---|---|---|
| M-1 transition | 6.80 | 8.00 | 0.850 | 0.396 | 0.126 | 7640 | 0.0400 | 0.916 | .352/.037 | .392/.333 |
| M-1 main | 6.80 | 8.00 | 0.850 | 0.420 | 0.258 | 4470 | 0.0478 | 0.894 | .448/.598 | .477/.477 |
| Mark 9 (= Mark 15-F) | 2.99 | 3.61 | 0.829 | 0.294 | 0.226 | 4450 | 0.0511 | — | .52/.41 | .57/.54 |
| "A" | 3.13 | 3.63 | 0.861 | 0.390 | 0.279 | 4000 | 0.0511 | 0.87 | .58/.48 | .58/.56 |
| "B" | 3.13 | 3.63 | 0.861 | 0.390 | 0.316 | 3650 | 0.0533 | 0.87 | .64/.54 | .64/.62 |
| "C" | 3.13 | 3.63 | 0.861 | 0.390 | 0.338 | 3460 | 0.0538 | 0.86 | .68/.57 | .68/.66 |
| "D" (= Mark 26) | 3.13 | 3.63 | 0.861 | 0.390 | 0.35 | 3380 | 0.0542 | 0.84 | .72/.61 | .72/.70 |
| "E" (= Mark 25) | 3.13 | 3.63 | 0.861 | 0.465 | 0.35 | 3220 | 0.0500 | 0.85 | .53/.47 | .55/.50 |
| NASA ν=0.4 | 1.78 | 4.53 | 0.393 | 0.284 | 0.135 | 10650 | 0.0272 | 0.800 | .593/.223 | .577/.373 |
| NASA ν=0.7 (rotor only) | 3.15 | 4.50 | 0.700 | 0.294 | 0.282 | 4760 | 0.0429 | 0.937 | .693/.426 | — |
| NASA ν=0.8 (rotor only) | 3.60 | 4.50 | 0.800 | 0.466 | 0.391 | 3850 | 0.0436 | 0.955 | .631/.664 | — |

**Derived per-stage numbers (this note's arithmetic, NOT printed in the source).** These come
from Tables I+II: U_T = 2π·r_T·N/60, H_stage = ψ_T·U_T²/g, cross-checked against
H_stage = (N·Q^½/Ns)^{4/3}.

| Pump | Tip speed | Head/stage, from ψ_T | Head/stage, from Ns |
|---|---|---|---|
| Mark 15-F (J-2) | ~890 ft/s | ~5,600 ft | ~5,100 ft |
| Mark 9 | ~1,030 ft/s | ~7,500 ft | ~6,800 ft |
| M-1 main | ~920 ft/s | ~6,800 ft | ~6,700 ft |
| Mark 26 | ~760 ft/s | ~6,300 ft | ~5,900 ft |
| Mark 25 | ~1,080 ft/s | ~12,600 ft | ~16,200 ft |

- **Mark 15-F (J-2):** 7 stages × ~5,300 ft plus the inducer gives the tabulated 40,300 ft.
- **M-1:** the Ds check is D = 16 in, Q = 62,300 gpm, H ≈ 6,700 ft, giving Ds = 0.049 against
  the tabulated 0.0478.
- **Mark 26:** the "D" stage's ψ_T of 0.35 is higher, but it runs at a lower rpm.
- **Mark 25:** the two methods disagree. The Mark 25 inherits the "E" stage row, whose
  Ns-inferred head exceeds the tip-speed head. Its row is probably quoted at a different flow
  or density. Do not use it as an anchor.
- **Whole pump:** Ns ≈ 800-1,200 across the fleet. M-1 ≈ 900, which matches the monograph's
  own "approximately 900" `[§2.2.1 p.11]`.

**Implication for `turbopump_sizing.py`:**
- **The J-2's real LH2 pump is an AXIAL machine: 7 axial stages at ~5,100-5,600 ft/stage.**
  The tool's centrifugal `H_PER_STAGE_FT_TYPICAL = 6000` rule was anchored to reproduce "~7
  stages" on the J-2 LH2 pump, so it is calibrated against an axial pump's stage count, not a
  centrifugal one's.
- The tool's `HEAD_COEFFICIENT_PSI = 0.5` uses the *same definition* as SP-8125's ψ
  (g·H/U_tip²). Real axial mainstages run **ψ_T = 0.23-0.35** (research up to 0.39), which is
  roughly half the centrifugal 0.5, at **tip speeds of only ~760-1,080 ft/s**.

**Overall pump head/efficiency characteristics** `[SP-8125 Fig. 1 p.5]` (read off the plot):
- Peak *overall* efficiency (inducer inlet to volute discharge): M-1 ≈ 0.70, Mark 15-F ≈ 0.73,
  Mark 9 ≈ 0.73, Mark 26 ≈ 0.75, Mark 25 ≈ 0.79. Compare the *stage* hydraulic efficiencies
  of 0.84-0.92 in Table II.
- Overall head coefficient at the stall point: M-1 ≈ 2.35, Mark 15-F ≈ 1.95, Mark 25 ≈ 2.05,
  Mark 26 ≈ 2.85, Mark 9 ≈ 1.93. The reference velocity is not stated. It is presumably the
  inducer tip speed, since the abscissa is the inducer-inlet flow coefficient.
- Operating inducer-inlet flow coefficients are 0.06-0.11. The curves are steep, with an
  **abrupt head drop at stall**. This is why axial pumps have a narrow range `[§2.1 p.3]`.

**Axial vs centrifugal selection rule** `[SP-8125 §3.2.1 p.68-69; §2.1 p.3; §2.2.1 p.11]`:
- "It is recommended that an axial configuration be considered when **stage specific speeds
  are above approximately 3000** and when **throttleability and wide fixed-speed flow range
  are not required**." Ns here is US rpm·gpm^½/ft^¾, the same units as the tool's 2200 target.
- Axial is also recommended when uprating is expected and the competing centrifugal pump
  would need an extra stage, because adding axial stages is simple.
- Axial stages span Ns ≈ **3,200-11,000** (Fig. 4, a Balje Ns-Ds chart).
- The monograph itself stresses that the choice "was not incisive". A centrifugal pump could
  have met every Table I duty. The M-1's *whole-pump* Ns ≈ 900 sits in centrifugal territory
  "some decrease in efficiency being anticipated".
- Axial's stated advantages are potential efficiency, weight, packaging and ease of staging.
- Use has been **limited to LH2** (high volumetric flow and head) and to non-throttled
  service.

**Stage loading limits (design criteria)** `[SP-8125 §3.2.2-3.2.2.7 p.69-72]`:
- Parametric-study guides:
  - stage design **flow coefficient ≥ 0.25**
  - **hub/tip ≤ 0.9**
  - for hub/tip ≥ 0.8, blade **tip speed < 1,700 ft/s for high-strength Ti, < 1,500 ft/s for
    high-strength Ni-base alloys**
- **Diffusion factor** is the loading measure:
  - **0.45-0.55** maximum design-point DF (any radius, rotor or stator) for optimum
    efficiency
  - **0.55-0.60** allowed when the minimum stage count matters and stall margin permits
- **Stall criterion (hub/tip > 0.8):** DF = **0.75** or retardation factor w₂/w₁ = **0.50**.
  The permissible minimum-flow operating point is DF **0.70** / RF **0.55** `[§3.2.2.6 p.72]`.
  - The M-1 instead used an equivalent diffusion factor DF_eq = 2 as its stall criterion
    `[p.21]`.
- Free-vortex flow with a symmetric (R = 0.5) diagram at mean radius is recommended for
  hub/tip > 0.8.
- **For LH2, account for density increases above 6% by a linear flow-path taper** `[p.70]`.
  - The M-1 tapered its OD over stages 3-5. The Mark 25 tapered its whole flow path. The
    Mark 9/15-F/26 had no compressibility adjustment `[p.16]`.
- Solidity ≈ **0.75-1.9** `[p.71]`.
- Maximum suction-surface velocity **≤ 1.25 × relative inlet velocity** `[p.73]`.
  - The Mark 9/15-F/25 profiles held ≤ 1.2× `[p.38]`.
- Max thickness/chord **≤ 0.13**, with **0.10-0.11 preferred** `[p.73]`. Table III shows up to
  0.15 was used; the M-1 vane was forced to 0.15 for stress, at an estimated **2-3% pump
  performance loss** `[p.54]`.
- Radial tip clearance **≤ 2% of blade/vane height** `[p.72]`.
  - Actual running clearances: Mark 15-F rotor ≈ 0.005 in / stator 0.015 in; M-1 0.020 /
    0.049 in (shrouded vanes) `[p.34]`.
  - Mark 9 air tests: head and stall margin dropped as rotor tip clearance went 1.58% → 3.57%
    of blade height. The pump was insensitive to stator clearance over 0.95-3.25%.
- Axial row-to-row gap **≥ 10% of upstream chord** `[p.72]`.
- Mainstages "shall not be subject to cavitation": the inducer (see ref. 2 = SP-8052) must
  supply enough head for the first mainstage `[p.71-72]`.
  - The M-1 added a lightly loaded "transition" stage (ψ_T 0.126) for this purpose `[p.16, 27]`.

**Efficiency and loss notes** `[SP-8125 §2.2.2.1.2-2.2.2.3 p.22-26; Fig. 7 p.21]`:
- Pitchline stage efficiency (R = 0.5, σ = 1.5, profile loss only) peaks at ≈ 0.915 near
  φ ≈ 0.5-0.7 (Fig. 7).
- Blockage allowances: **4% of annulus** (M-1, end-wall only, with loss-data design method)
  vs **~10%** (Mark series, average-efficiency method).
- A 1° deviation-angle error in a 50%-reaction stage costs ≈ **8% of stage work** `[p.25]`.
- Design incidence: +3° on the Mark 9/15-F, chosen for cavitation; 0° on the Mark 25/26,
  chosen for low loss.

**Speed, bearings, seals and rotor dynamics** `[SP-8125 §2.1-2.1.2 p.8-10; §3.1.2 p.68]`:
- LH2-cooled ball/roller **bearing DN ≈ 2 × 10⁶ is "considered state-of-the-art limit for
  relatively short-life pumps"** `[p.8, citing SP-8048]`. This is a second real citation for
  `turbopump_materials.py`'s `max_dn_mm_rpm` Tier-3 estimate, for the LH2 case.
- Face-riding seals have run at up to **400 ft/s** surface speed `[p.8]`.
- **M-1 speed** was set by inducer cavitation at a design **Ss = 43,000** `[p.9]`.
- **Mark 15-F/26 speed** was limited by blade resonance, not by a strict design constraint.
- Two rotor-dynamic philosophies:
  1. **M-1: subcritical.** It used roller bearings plus a triple thrust ball set in a
     flexible housing. Predicted first critical was **16,000 rpm** against 13,225 rpm
     operating (≈ 21% margin). An accidental overspeed to **15,500 rpm** showed critical
     approach on the accelerometers, which validated the model.
  2. **Mark 9/15-F/25/26: supercritical.** These ran above the system criticals but below
     first rotor flexure, on ball bearings. All suffered **nonsynchronous whirl**.
     - Mark 15-F: up to **0.030 in p-p** radial displacement and turbine-disk/coupling
       alternating stress. Cured by **raising the ball-bearing axial preload**.
     - Mark 25: cured by switching single to **duplex ball bearings**.
- Criteria defer the numeric critical-speed margins to ref. 6 (SP-8101).

**Axial thrust balance** `[SP-8125 §2.3.4 p.47-53; §3.3.4 p.82-85]`:
- **Mark series: self-compensating "series-flow" balance piston.** Pump-discharge fluid passes
  two variable orifices in series. At nominal the bearings carry only preload.
  - Mark 15-F total piston travel **0.015 ± 0.001 in**, gapped and preloaded at LN2
    temperature.
  - Pistons sized for **2× calculated thrust**, to allow trimming during development.
- **M-1: single variable orifice** with a bias load toward the turbine, reacted by a triple
  ball-bearing set. It could take thrust reversal only up to one bearing's capacity.
- Criteria:
  - piston outer-diameter deflection **< 10% of total travel**
  - stops to prevent rubbing during start
  - return flow re-entered above vapor pressure (no two-phase flow)
  - LH2 stability improves with higher pressure, larger cavity area, smaller cavity volume
    and larger total ΔP
- **Mark 15-F instability history:** carbon orifice inserts broke and contaminated the
  bearing coolant, causing bearing failures. Fixed with leaded bronze.

**Rotor mechanical design, blades and safety factors**
`[SP-8125 §2.3.1-2.3.3, §2.6, §3.3.1-3.3.3 p.39-47, 64-67, 74-82]`:

Rotor types:
- **Mark 15-F/26: one-piece forging with integral blades.** This was the lowest cost and
  weight, and is preferred "size permitting".
- **Mark 9/25: built-up disks on tie-bolts.** These were ground-test pumps, chosen for easy
  staging.
- **M-1: four Inconel 718 forgings TIG-welded into a hollow drum, with 376 dovetailed
  mainstage blades.** The Mark 9 had 102 blades, machined integrally.

Loads and design speeds:
- Mechanical design speed is **≥ 10% above nominal**.
- An alternating torque of **~5% of steady** is superimposed.
- Torque capacity is effectively limited by bearing DN, because a bearing sits between the
  pump and the turbine.

Blade stress and vibration:
- Blades are checked on a modified Goodman diagram. The vibratory stress is assumed equal to
  the hydrodynamic steady stress (history: 0.3-1×), times the root-fillet stress-concentration
  factor. A fillet r = t_max gives K ≈ 1.1 `[p.80]`.
- Safety factors: **1.33 fatigue / 1.5 ultimate / 1.1 yield**, with **4× predicted cycles
  (LCF) and 10× (HCF)** `[p.67, 75]`.
- **Resonance margin ≥ 15%** of operating speed between blade natural frequencies and known
  excitations (Campbell diagram) `[p.40, 79]`.
- Flutter rules: torsional frequency parameter 2πf_t·C/w₁ ≥ 1.6 and flexural 2πf_b·C/w₁ ≥ 0.33
  `[p.79]`.
- **Mark 15-F first-stage rotor blades failed in fatigue at a 19-per-rev wake resonance.**
  Cutting ¼ in off the tip chord and tapering the leading edge fixed it with no noticeable
  performance change `[p.41-43]`. Stator vanes also cracked and were fixed by thickening the
  root.

Pressure and load factors:
- Proof factor **1.2**.
- Volute design pressure ≈ **1.2×** the hydrodynamic value.
- Limit-load factors: centrifugal 1.1, fluid 1.1, pressure 1.2, thermal 1.0, inertial 1.05
  `[p.66-67]`.
- Torque-wrench bolt preload scatters **3-4×** `[p.63]`.

Manufacturing:
- Profile tolerance ± 0.002 in and blade angles ± ¼°.
- Surface finish ≤ 63 µin rms. M-1 blades were typically 32 µin.

**Materials and hydrogen embrittlement** `[SP-8125 §2.5 p.63-64, Table IV p.65; §3.5 p.91-92]`:

| Pump | Rotor and blades | Other parts |
|---|---|---|
| Mark 9 | **310 CRES** | 310 CRES housings; Al 2024 balance piston |
| Mark 15-F / Mark 26 | **K-Monel** | 310 CRES volute/stator/housings; K-Monel piston; leaded-bronze orifice |
| Mark 25 | **K-Monel** | Inconel 718 piston |
| M-1 | **Inconel 718** rotor and mainstage blades and vanes; **Ti A110-AT-ELI (Ti-5Al-2.5Sn ELI)** transition rotor | 304/347 CRES housings; Al 7075-T73 piston |

- **H2 embrittlement case:** the M-1 Ti transition-rotor forgings showed only **1% elongation
  at LH2 temperature**, caused by excess hydrogen content. **Vacuum degassing raised it to
  10%.**
- Criteria:
  - **≥ 4% elongation (in 4 diameters) at LH2 temperature** for parts that may locally yield
  - **Charpy V-notch ≥ 12 ft-lbf at LH2 temperature** where impact is possible
- Non-galling, non-shattering rotating/stationary pairs in LH2:
  - K-Monel / leaded bronze
  - Inconel 718 (WC-plated) / leaded bronze
  - Ti-5Al-2.5Sn ELI / leaded bronze
- M-1 weld defects in the rotor propagated during testing. Their long-term effect was never
  established because the program ended.

**Life and duty** `[SP-8125 §2.1 p.3]`: M-1 design duration **500 s** per run, with a
**10,000 s** service life between overhauls. The monograph calls the short-life requirement "a
significant factor" in component development.

**J-2 start-transient stall of the Mark 15-F** `[SP-8125 §2.2.2.6 p.31-34, Fig. 12]`. The
monograph names three potential stall points: spin-down stall, LOX-dome-prime stall and
high-speed stall.
- **Spin-down stall:** chamber-tube warming vaporized fuel and raised the head demand.
  Mitigations were chamber chill, an up-to-8 s fuel lead, and cold N₂/He purges. J-2S/J-2X
  later used a coolant-tube bypass; the RL10 uses an overboard dump.
- **LOX-dome-prime stall:** Pc jumped to over 150 psi. It was fixed by reducing the initial
  main-oxidizer-valve opening and raising the spin-bottle pressure.
- **High-speed stall:** the MOV opened fully too early.

The monograph notes that the RL10 (centrifugal) had similar start problems, so these are a
system issue, not an axial-only one.

## Design method

This is a design-criteria monograph, not a closed-form sizing method. It gives the governing
dimensionless definitions:
- φ = V_a/U and ψ = g_c·H/U² = η_H·ΔV_u/U (eqs. 3-4)
- diffusion factors DF_R = 1 − w₂/w₁ + Δw_u/(2σw₁) and DF_S analogously (eqs. 5-6)
- retardation factor RF = w₂/w₁ (eqs. 7-8)
- a cavitation parameter τ_R = NPSH/(U²/2g_c) (eq. 14)
- Ns/Ss/Ds as in `[SP-8109]`

The recommended procedure, at 50%-streamline conditions `[§2.2.2 p.15-16]`:
1. Pick the profile type, velocity-diagram type, loading (DF) and solidity.
2. Sweep tip speed and φ, which sets hub/tip ratio.
3. Take the stage ψ from those, which gives the number of stages.
4. Trade diameter against length for stress, weight and critical speed.
5. Only then set blade angles per streamline and check off-design.

For LH2, compute head by summing isentropic-enthalpy increments with per-increment efficiency
(ref. 7, SP-8107 p.99-102), rather than using constant density `[p.11, 15]`.

What the tool can use directly for a future axial-LH2 option:
- ψ_T ≈ 0.23-0.35
- hub/tip ≈ 0.83-0.86 (≤ 0.9)
- φ ≥ 0.25 (fleet 0.29-0.47)
- tip-speed caps of 1,500 (Ni) / 1,700 (Ti) ft/s
- DF 0.45-0.60
- stage η_H 0.84-0.92 against overall pump η 0.70-0.79
- a selection gate of stage Ns > ~3,000 and no deep throttling

## Section map

- §1 Introduction: p.1-2 (leaf 12-13). Read.
- **§2.1 Overall Turbopump Design (Table I p.4, Fig. 1 p.5, Figs. 2-3 p.6-7), 2.1.1 Speed,
  2.1.2 Rotor Dynamics: p.3-10 (leaf 14-21). Read in full.**
- **§2.2 Stage Design: p.10-35 (leaf 21-46). Read in full.** Contents:
  - 2.2.1 Realm of Operation, Fig. 4 Ns-Ds, p.11-12
  - 2.2.2 Hydrodynamic Design, eqs. 3-4, p.15
  - Tables II/III, p.17-18
  - 2.2.2.1 Loading/Stall/Efficiency, Figs. 7-8, p.16-24
  - 2.2.2.2 Velocity Diagrams, p.24-25
  - 2.2.2.3 Blade Angles, p.25-26
  - 2.2.2.4 Solidity, Fig. 9, p.26-27
  - 2.2.2.5 Cavitation, Figs. 10-11, p.26-31
  - 2.2.2.6 Off-Design / J-2 start stall, Fig. 12, p.31-34
  - 2.2.2.7 Clearances, p.34-35
- **§2.3 Pump Rotor Assembly: p.35-53 (leaf 46-64). Read in full.** Contents:
  - blades and profiles, p.35-39
  - blade mechanical design (Goodman/Campbell), Figs. 16-19, p.39-43
  - attachment (M-1 dovetail), p.43-45
  - rotor, p.45-47
  - thrust balance, Figs. 22-25, p.47-53
- §2.4 Pump Stator Assembly: p.53-63 (leaf 64-74). §2.4.1-2.4.4 read. §2.4.5
  interfaces/static seals skimmed.
- **§2.5 Materials (Table IV p.65) and §2.6 Safety Factors: p.63-67 (leaf 74-78). Read in
  full.**
- **§3.1-3.3 Design Criteria (speed, rotor dynamics, stage design, rotor assembly): p.68-85
  (leaf 79-96). Read in full.** Fig. 31 (Goodman) and Figs. 32-33 (dovetail base fixity, vane
  virtual mass) were read via the text.
- §3.4 Stator Assembly criteria: p.85-91 (leaf 96-102). Header skim only, except
  §3.4.5.2.3 bolt safety factors (1.5 ult / 1.1 yield).
- **§3.5 Materials criteria: p.91-92 (leaf 102-103). Read in full.**
- App. A SI conversion (p.93), App. B Glossary (p.95-103; symbol list read), References
  (p.105-110; refs 1-13 read).

## Caveats

- **Only five pumps, all LH2, all 1960s designs.** Only the Mark 15-F flew. There is no LOX,
  RP-1 or CH4 axial main pump data, and no SSME data (the SSME HPFTP is centrifugal). Do not
  generalize the ψ, DF or tip-speed numbers to dense propellants. SP-8125 itself says
  centrifugal "is well suited for dense propellants" `[p.1]`.
- **Per-stage head, tip speed and whole-pump Ns in this note are derived** from Table I rpm
  plus Table II radii, ψ_T and Ns, not printed values. The Table II radius unit (inches) is
  inferred, but it checks out via the M-1 Ds and the whole-pump Ns ≈ 900 stated in the text.
- **The Mark 25 derived stage head is inconsistent** between the ψ_T and Ns routes (12.6k vs
  16.2k ft), so treat it as unreliable. The Mark 15-F, Mark 9, M-1 and Mark 26 agree within
  ~10%.
- **Fig. 1 efficiencies and head coefficients are read off a small plot** (±0.01-0.02). The
  overall head coefficient's reference tip speed is not stated.
- **Table II η is stage *hydraulic* efficiency.** It excludes inducer, volute, leakage,
  thrust-balance recirculation and mechanical losses, so it is 10-20 points above the
  overall pump efficiency. Do not feed it into `turbopump_efficiency.py` as a whole-pump
  number.
- **The stall DF 0.75 / RF 0.50 and operating DF 0.70 / RF 0.55 criteria are stated only for
  hub/tip > 0.8.**
- The quantitative critical-speed margin is deferred to SP-8101, bearing DN to SP-8048,
  inducer and Ss criteria to SP-8052, and speed and pump-type selection to SP-8107. This
  monograph gives only the M-1 example (≈ 21% subcritical margin) and the DN 2×10⁶ LH2 figure.
- OCR is clean on most text pages. Tables, figures and the cover were read from rendered PNGs.
  Equation symbols in the text layer are garbled, so eqs. 5-10 and 16-17 above were
  reconstructed from context and the glossary.
