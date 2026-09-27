# [Huzel] — Design of Liquid Propellant Rocket Engines (NASA SP-125)

## Identity

- **Title**: *Design of Liquid Propellant Rocket Engines*
- **Authors**: Dieter K. Huzel and David H. Huang, Rocketdyne Division, North American Aviation / Rockwell
- **Series**: NASA SP-125, Office of Technology Utilization, NASA, Washington D.C.
- **Edition**: 2nd edition (cover), 1971 printing; 1st edition 1967. This is the NASA SP-125,
  **not** the 1992 AIAA revision (*Modern Engineering for Design of Liquid-Propellant Rocket
  Engines*, Huang/Huzel/Arbit).
- **Extent**: ~460 printed pages, 469 PDF leaves. Scanned images + OCR text layer (decent
  quality; equations legible in rendered page images).
- **PDF leaf ↔ printed page**: `leaf ≈ printed page + 9` (printed p.1 = leaf 10).

## Character

Written "on the job" at Rocketdyne as a bridge between propulsion fundamentals and real
industry engine design. Its backbone is four running worked examples — the hypothetical
*Alpha vehicle* engines:

| Engine | Propellants | Cycle | Role |
|---|---|---|---|
| A-1 | LOX/RP-1, MR 2.35, Pc 1000 psia, ε 14 | gas generator | booster, 750 klbf |
| A-2 | LOX/LH2, MR 5.22, Pc 800 psia, ε 40 | gas generator | 150 klbf upper stage |
| A-3 | storable (N2O4/N2H4-UDMH) | pressure-fed | 16 klbf |
| A-4 | storable | pressure-fed | 7.5 klbf upper/space |

Numbers throughout are quantitative and stepwise — this is the source to copy a *design
procedure* from.

## Chapter map — "go here for X"

| § | Title | Printed p. | Feeds topic |
|---|---|---|---|
| **I** | Introduction to Liquid Propellant Rocket Engines | 1 | 01, 03, 11 |
| 1.1 | Generation of thrust; F = ṁ·ve/g + Ae(Pe−Pa) (eq 1-6); effective exhaust velocity c | 1 | 01 |
| 1.2 | Gas-flow processes; 8 ideal-flow assumptions; isentropic relations | 4 | 01 |
| 1.3 | Performance parameters Is, c\*, Cf and their interrelations | 10 | 01, 03 |
| 1.4 | Liquid rocket propellants | 18 | 11 |
| **II** | Rocket Engine Design Implements | 31 | 12, 13 |
| 2.1 | Major design parameters and their typical ranges | 31 | — |
| 2.4 | Stress analysis; design-limit / yield / **ultimate = 1.5× design-limit** load structure (eq 2-8…2-11); endurance limit 20–60 % of ultimate | 56 | 12 |
| 2.5 | Selection of materials; material groups; cryo & H2 embrittlement; thermal-shock figure of merit Ftu·k/(E·α) | 59 | 12 |
| **III** | Introduction to Sample Calculations (A-1…A-4) | 63 | all |
| **IV** | **Design of Thrust Chambers and Other Combustion Devices** | 81 | 02–07, 14 |
| 4.2 | Thrust-chamber performance parameters; c\* correction ~0.975, Cf correction 0.98–1.01 | 83 | 03 |
| 4.3 | Configuration layout: Vc = ṁ·V̄·ts (4-3), **L\* = Vc/At (4-4)**, Table 4-1 L\* by propellant, contraction ratio, conical & Rao bell contour, **λ = ½(1+cos α) (4-8)**, Fig 4-12 (thrust eff vs %bell), Fig 4-14 (θn, θe vs ε) | 86 | 02, 04 |
| 4.4 | Thrust-chamber cooling: 6 methods; **Bartz h_g (eq 4-13)**; Colburn Nu = C·Re^0.8·Pr^0.34; recovery factor 0.90–0.98; regen/film/transpiration/ablative/radiation; radiation q = ε·σ·Twg^4 | 98 | 06, 07 |
| 4.4 | **Tubular Wall Thrust Chamber Design** (extracted 2026-09-17): circular-tube combined stress (eq 4-27/4-28), longitudinal thermal inelastic-buckling (eq 4-29), elongated-tube bending term (eq 4-30, Fig 4-30), coax-shell combined stress (eq 4-31), passage pressure drop (eq 4-32); Fig 4-29/4-30 tube cross-sections; **Fig 4-31 shows tube shape morphing elongated↔circular along the chamber axis**; Sample Calc 4-4 (A-1/A-2 real Inconel-X tube numbers at the throat); **p.113-114 (PDF 122-123): tube manufacture - uniform round tubes cut to length, swaged by internal hydraulic pressure in a variable-section die, wax-filled, bent to contour in a fixture, trimmed, then arranged on a brazing core "to assure even distribution of the gaps between tubes" and furnace-brazed** (re-read 2026-09-23) | 107–114 | 06 |
| 4.5 | Injector design: 10 patterns; ΔPi = ρV²/(2g·Cd²) (4-40); **Cd 0.5–0.92**; **ΔP rule-of-thumb 15–20 % of Pc**; β angle; injection momentum ratio (4-42) | 121 | 05 |
| 4.6 | Gas-generating devices: gas temps 400–1000 °F (pressurant) / 1200–1700 °F (turbine drive); solid/mono/bipropellant GGs; solid burn rate R = k1·Pc^n | 131 | 10 |
| 4.7 | Ignition devices; TEA-TEB, pyrotechnic, hypergolic slug, spark; ignition detection methods | 136 | 15 |
| 4.8 | Combustion instability: modes & acoustic frequency (Fig 4-59: longitudinal N = ae/2Lc; tangential 0.59 ae/dc; radial 1.22 ae/dc); classes hi-freq/lo-freq/intermediate; peak-to-peak/Pc < 0.10 threshold | 143 | 14 |
| **V** | Design of Pressurized-Gas Propellant-Feed Systems | 151 | 08 |
| **VI** | **Design of Turbopump Propellant-Feed Systems** | 176 | 09 |
| 6.2 | Turbopump system performance & design parameters; specific speed, suction specific speed | 186 | 09 |
| 6.3–6.4 | Centrifugal / axial-flow pump design with efficiency charts | 204 | 09 |
| 6.5 | Turbine design: impulse vs reaction, pressure- vs velocity-compounding, U/C0 efficiency charts | 238 | 09 |
| 6.6 | Bearings, seals, gears — DN limits | 257 | 09 |
| **VII** | Design of Controls and Valves | 263 | 15, 16 |
| 7.3 | Engine thrust-level control | 267 | 15 |
| 7.4 | Mixture-ratio & propellant-utilization control | 268 | 15 |
| 7.5 | **Thrust-vector control**: gimbal-bearing design, actuator sizing, hinge moments, secondary injection | 272 | 16 |
| **VIII** | Design of Propellant Tanks (membrane stress, cryo insulation, filament-wound) | 329 | (out of tool scope) |
| **IX** | Interconnecting Components and Mounts | 353 | 16 |
| 9.6 | Design of gimbal mounts | 379 | 16 |
| **X** | Engine Systems Design Integration | 383 | 13, 15 |
| 10.2 | Dynamic analyses — start/shutdown transient sequencing | 384 | 15 |
| 10.3 | Design integration for engine-system calibration | 390 | 15 |
| 10.8 | Clustering of engines | 415 | — |
| **XI** | Design of Liquid Propellant Space Engines (restart, RCS, high-ε, ablative/radiation thrusters) | 429 | 06, 11 |

## Notation quirks

- `(Pc)ns` = chamber/nozzle stagnation pressure (what the tool calls Pc).
- `c*` written with an asterisk; `Cf` for thrust coefficient (not C_F).
- `λ` = divergence / thrust-efficiency factor for the nozzle (= the tool's `nozzle_divergence_efficiency`).
- `ε` and `εc` = expansion and **contraction** area ratio respectively.
- `rw` = O/F mixture ratio by mass; `IV` in OCR = ṁ (weight flow rate), a scan artefact.
- US customary throughout (psia, lb, in, °R, Btu). `g = 32.2 ft/s²` appears as a literal in
  most equations.

## Caveats

- Pre-SSME (1967/71): staged-combustion and expander cycles are covered lightly; no modern
  alloy allowable-stress data (NARloy-Z, GRCop, C-C, etc.); combustion tables are
  frozen-composition.
- Propellant combustion charts (figs 4-3…4-6) are for specific Pc values (1000 psia LOX/RP-1,
  800 psia LOX/LH2, 100 psia for the fluorine pairs) — read at those, interpolate with care.

## Regen passage geometry data (2026-09-23 re-read)

Keyword search (tubes, coolant velocity, F-1, J-2, RL10, H-1) of the text layer; the key
pages re-read from rendered images (leaf N = printed p.N-9 around ch.4). **Huzel names no
real engine's tube/channel geometry anywhere** - F-1/J-2 appear only in a Saturn V vehicle
listing. The only tube numbers are **Sample Calculation (4-4)** for the book's hypothetical
A-1 / A-2 stage engines. These are textbook DESIGN EXAMPLES, not hardware - usable as a
worked method and as order-of-magnitude analogs (A-1 ~ F-1/H-1-class LOX/RP-1, A-2 ~
J-2-class LOX/LH2), never as a real-engine spot check.

| Quantity | A-1 (LOX/RP-1, 747,000 lbf SL, Pc 1000 psia, eps 14) | A-2 (LOX/LH2, 149,500 lbf alt) |
|---|---|---|
| Throat dia Dt | 24.9 in (0.632 m) | 11.2 in (0.284 m) |
| Pass layout | **2-pass**, down alternate tubes, up adjacent | **1½-pass**: inlet manifold at **eps = 8**, down to eps = 30 and back, then through throat and chamber to injector |
| Tube material / wall t | Inconel X, **0.020 in (0.51 mm)** | Inconel X, **0.008 in (0.20 mm)** |
| Tube ID at throat | **0.855 in (21.7 mm)** | **0.185 in (4.70 mm)** |
| Tube count N | **94** (rounded even from 94.5) | **178** |
| Coolant flow | 827 lb/s (375 kg/s) = all fuel | 54.5 lb/s (24.7 kg/s) = all fuel |
| Throat coolant velocity | **87.6 ft/s (26.7 m/s)** | not computed |
| Throat coolant pressure | 1500 psia (10.3 MPa) | 1200 psia (8.27 MPa) (estimated) |
| Throat coolant bulk T | 600 °R (333 K), "up" tube | 135 °R (75 K) |
| T_wg / T_wc at throat | 1188 °R / ~1000 °R (660 / 556 K) | 1600 °R / 1204 °R (889 / 669 K) |
| Throat heat flux | 3.00 Btu/in²·s (4.9 MW/m²) | 19.10 Btu/in²·s (31.2 MW/m²) |
| Required h_c | 0.0075 Btu/in²·s·°F (22.1 kW/m²K) | 0.0179 Btu/in²·s·°F (52.7 kW/m²K) |

`[Huzel Sample Calc 4-4 p.109-113]`; A-1/A-2 thrusts `[Huzel Sample Calc 4-2 p.95]`, A-1 eps 14 `[Huzel Fig. 4-20 p.96]`.
Tube-count relation used: N = pi [Dt + 0.8 (d + 2t)] / (d + 2t) (0.8 = tube centers on a
circle); A-2's printed final substitution shows d = 0.17 in, but N = 178 is what d = 0.185 in
gives (typo only). A-1's N = 94.5 does not reproduce exactly from its own printed relations
(they give ~90 at d = 0.85 in) - treat the book's arithmetic as +/-5 %. Also: "Total
temperature increase for a typical thrust chamber design is of the order of **100 °F** [56 K]
between cooling jacket inlet and outlet" `[Huzel §4.4 p.110]` (RP-1 context, generic).
Tube forming: uniform round tubes cut, swaged by internal hydraulic pressure in a die,
wax-filled, bent to contour `[Huzel p.113-114, Fig. 4-31/4-32]`.

**NOT in Huzel** (for any real engine): tube/channel count, dimensions, land width, jacket
flow fraction, coolant inlet/outlet T/P, throat coolant velocity, separate-circuit layout.

## Turbopump pump design, ch. 6 §6.1-6.4 (turbopump Round 2 read, 2026-09-26)

Read from rendered pages, printed p.184-238 (leaf = printed + 9 in this chapter; printed 204 =
leaf 213). Only pp.215-219 were caught mid-example; those numbers are in SC 6-7 below.
Huzel's "A-1" (LOX/RP-1 booster) and "A-2" (LOX/LH2 upper stage) are its own fictional design
examples, modelled on F-1/H-1-class and J-2-class hardware.

**Definitions and ranges** `[Huzel §6.2-6.3 p.189-192, 204-210]`:
- ψ = ΔH/(u2²/g) (eq. 6-4) runs 0.2-0.7 for single-stage centrifugal, up to 1.5-2.0 for
  multistage axial.
- φ = cm2/u2 (eq. 6-5), 0.01-0.15.
- Impeller types by Ns: radial 500-1200 (r2/r1 2-3); Francis 1200-2400 (r2/r1 1.3-1.8); mixed
  flow 2200-3500; axial 3000-6000 (multistage), 6000-12000 for inducers.
- Euler head (eq. 6-26b/6-30): ΔH_i = (u2·cu2 − u1·cu1)/g; cu2 = u2 − cm2/tan β2 (6-28).
  β is measured from the tangential direction.
- **Slip / vane-number correction** (eq. 6-31 to 6-33): Huzel uses the single empirical
  **impeller vane coefficient e_v = cu2'/cu2, typical 0.65-0.75**. It lumps slip and hydraulic
  loss together; no Stodola/Pfleiderer/Wiesner.
- **Volute loss** (eq. 6-34): H_e = **0.10-0.30 ΔH**; ΔH_imp = ΔH + H_e − ΔH_ind.
- **Leakage** (eq. 6-35): Q_imp = Q + Q_e, with Q_e (wear rings) **1-5 % of Q_imp**
  (centrifugal) and **2-10 %** (axial, eq. 6-87).
- Inducer tip leakage Q_ee is 2-6 % (eq. 6-63).
- Design elements `[p.208-209]`:
  - eye cm1 10-60 ft/s
  - u2 200-1500 ft/s (strength-limited)
  - β1 8-30°
  - **β2 17-28°, average 22.5°, "the most important single design element, chosen first"**
    (head and capacity rise with β2 at a given u2)
  - LH2 pumps often use radial vanes (β2 = 90°) for higher ψ
- **Vane count** (eq. 6-44): z = β2/3 (β2 in degrees), usually 5-12, with splitters if the
  eye is crowded.
  - Passage divergence 10-14°. Inlet edge about 0.12 in.
- **Widths** (eq. 6-42/43): b1 = Q_imp/(3.12·π·d1·cm1·ε1) and b2 = Q_imp/(3.12·π·d2·cm2·ε2)
  (in, gpm, ft/s).
  - Contraction factors ε1 0.75-0.9, ε2 0.85-0.95.
- **Impeller disk stress** (eq. 6-41, Timoshenko): design at u2max = 1.25 × design u2.
- **Losses** `[p.194]`: hydraulic (friction and turbulence), disk friction ("transformed into
  heat and can appreciably increase the temperature of the fluid"), mechanical (bearings,
  seals), and leakage.
  - bhp = fhp + hp_h + hp_df + hp_m + hp_l (eq. 6-14).
  - Rocket pumps are 60-85 % efficient, about 10 % below industrial pumps `[p.195]`.
- **Fig. 6-23**, efficiency vs Ns by capacity (read ±1 pt; peak near Ns ~2500):

  | gpm | Ns 1000 | ~2500 | 4000 | 10000 |
  |---|---|---|---|---|
  | > 10000 | ~88 | 91.8 | ~90.5 | 84.6 |
  | 3000-10000 | ~85 | 89.8 | ~88.7 | 81.4 |
  | 1000-3000 | 80.9 | 87.2 | ~85.5 | 77.4 |
  | 500-1000 | 76.8 | 82.8 | ~81 | 73.3 |
  | 200-500 | 70.4 | 77.2 | ~76 | 69.6 |
  | 100-200 | 63.7 | 71.4 | ~70.5 | 64.8 |
  | < 100 | 57.5 | 66.0 | ~65 | 60.5 |

  These are industrial-class values; rocket pumps sit about 10 points lower.

**Volute and diffuser** `[p.219-222]`:
- Constant average velocity (eq. 6-69): a_θ = (θ/360)·a_v.
- Velocity c3' = **K_v·√(2gΔH)**, with **K_v 0.15-0.55** (lower at higher Ns) (eq. 6-70).
- Tongue angle ≈ α2'. **Tongue radius 5-10 % beyond r2.**
- b3 = 2.0 b2 (small, low-Ns pumps) to 1.6-1.75 b2 (higher Ns). Side-wall angle ≤ 60°.
- 70-90 % of the flow's kinetic energy is recovered as pressure in either volute type.
- Diffusing-vane volute: vane-tip radial gap 0.03-0.12 in; c3' = (d2/d3)·c2' (eq. 6-71).
  - Near-square passages diverging 10-12°.
  - Vane count has no common factor with the impeller count.
- Double volute (tongues 180° apart) reduces radial thrust.
- Casing hoop stress is St = p·a/a' (rough).

**Axial thrust** `[p.223-225]`:
- The balance chamber and back-shroud radial ribs are sized in eq. 6-74 to 6-78, with
  pv = p1 + 0.75 × the ideal centrifugal static rise (eq. 6-76).

**SC 6-2/6-3/6-4 (A-1 pumps, 7000 rpm, direct drive)** `[p.66, 191-196]`:

| | Q gpm | ΔH ft | Ns | Nss (test) | NPSHc ft | η | bhp |
|---|---|---|---|---|---|---|---|
| A-1 LOX | 12,420 | 2,930 | 1,980 | 37,230 | 58 | 70.7 % | 14,850 |
| A-1 RP-1 | 7,960 | 4,790 | 1,083 | 25,790 | 70 | 65.8 % | 11,790 |

Turbine: 27,140 bhp, 58.2 %, PR 23.7, 1400 °F.

**SC 6-7, A-1 LOX inducer + impeller (complete)** `[p.215-219]`:
- Given:
  - overall ψ 0.46
  - (Nss)imp 11,000; ψ_ind 0.06; rd 0.3; Li/dt 0.4
  - tip/hub taper half-angles 7°/14°; incidence ≤ 4°; Sv 2.2
  - Q_ee 0.032 Q, Q_e 0.035 Q, H_e 0.19 ΔH
  - β2 24°, e_v 0.74, ε1 0.82, ε2 0.88
- **Inducer:**
  - NPSH_imp = (N√Q/11000)^{4/3} = 293 ft
  - ΔH_ind = 293 − 58 = 235 ft
  - u_t = √(gΔH_ind/ψ_ind) = 355 ft/s, d_t = 11.62 in
  - d0t/d1t 12.19/11.05 in; d0h/d1h 2.33/4.65 in
  - Q_ind 13,040 gpm; cm0 37.2 ft/s; cm1 53.1 ft/s
  - u0 268 ft/s, u1 258.5 ft/s; cu1' 29.2 ft/s; β0' 7°45', β1' 13°03'
  - θ0t 9° (incidence 3°18'); z 3; Ci 26.57 in; Sv 2.18; φ_ind 0.0998
- **Impeller:**
  - u2 = √(gΔH/ψ) = 453 ft/s → d2 = 14.8 in
  - ΔH_imp = 1.19·2930 − 235 = 3252 ft; Q_imp 12,855 gpm
  - cu2' = (g·ΔH_imp + u1·cu1')/u2 = 248 ft/s → cu2 = cu2'/e_v = 335 ft/s
  - cm2 = (u2 − cu2)·tan β2 = 52.5 ft/s (**φ2 0.116**)
  - c2' 253.4 ft/s, α2' 11°58'; w2' 211.6 ft/s; β2' 14°22' (about 9.6° deviation)
  - b1 3.56 in; **b2 1.91 in (b2/d2 0.129)**; **z = 24/3 = 8**
- **SC 6-8 volute** (double volute, K_v 0.337):
  - c3' 146 ft/s; a_θ = 0.076·θ in² per volute (a180 13.68 in²)
  - tongue radius 7.77 in (1.05 r2); b3 = 1.75 b2 = 3.34 in
  - discharge nozzle 6.25 → 8 in, 10° included angle

**§6.4 axial-flow pumps** `[p.225-238]`:
- Except as inducers, rocket axial pumps are LH2 multistage.
  - A single-stage centrifugal H2 pump is limited to about 65,000 ft (2000 psi).
  - An axial stage gives 5,000-9,000 ft.
  - Axial capacity is at least ~5,500 gpm (vane height ≥ 0.5 in).
- **Fig. 6-50 selection (LH2):**
  - centrifugal at (Ns)1 = 500/stage for 1-2 stages, from ~250 gpm (b2 ≥ 0.2 in)
  - axial at (Ns)1 = 3000/stage for 1-12 stages, from ~5,500 gpm
  - either one in the overlap > 5,500 gpm and 30,000-65,000 ft
- Typical axial H2 values `[p.230]`:
  - rd 0.76-0.86
  - (Ns)1 3000-5000; (ψ)1 0.25-0.35 (at d_m)
  - rotor solidity 1-1.3, stator 1.5-1.8
  - z_r 14-20, z_s 35-45 (no common factor)
  - rotor-stator axial gap 0.02-0.05 d_t; tip clearance 0.005-0.010 in
  - LH2 volute 100-150 ft/s
- The design is set at d_m² = (d_t² + d_h²)/2 (eq. 6-79). cm is constant through all stages.
- ΔH = ΔH_ind − H_ee + n·(ΔH)1 (eq. 6-107).

**SC 6-10, A-2 LH2 axial pump (complete)** `[p.233-238]`:

Given:
- ΔH 44,800 ft; Q 6,080 gpm; NPSHc 135 ft
- (Nss)ind 53,400; ψ_ind 0.307; (Ns)1 3,250; (ψ)1 0.304
- rd 0.857; Q_e 0.06; H_e 0.08
- Sr 1.05, z_r 16; Ss 1.61; ε 0.88; i 4°, deviation 5°

Results:
- **N = 27,000 rpm**
- **7 stages + inducer, (ΔH)1 = 5,580 ft**
- u_m 768 ft/s; d_m 6.52 in; **d_t 7.0, d_h 6.0 in, vane height 0.5 in**
- ΔH_ind 6,240 ft needed (6,500 available); φ_ind 0.078
- cm 230 ft/s through all stages
- Rotor: β2' 19° (blade 23°), β3' 29°26' (blade 34°26'); Cr 1.346, Lr 0.645 in
- **Stator: z_s 41**, α3 36°40', α4 70°
- The A-2 engine table `[Table 3-3 p.69]` gives this pump **η 80 %, 6,100 bhp**. The A-2 LOX pump
  is 64 % at 8,600 rpm and 1,830 gpm.

**Real-style pump tables** `[Table 6-1 p.185]`:
- A geared LOX/RP-1 turbopump at 6,537 rpm:
  - LOX pump 3,257 gpm, 1,696 ft, 75.5 %
  - RP-1 pump 2,008 gpm, 2,751 ft, 72.1 %
  - NPSH required 35 ft each
- Turbine 31,740 rpm, 66.2 %, gear ratio 1:4.855.
- This matches the H-1/Thor class.

**Fluid properties** `[Table 6-3 p.188]` at pump conditions: LO2 71.17, LH2 4.43, RP-1
49.8-50.8 lb/ft³, plus storables with vapor pressure and viscosity. LH2 needs about +3 psi tank
pressure per °F of warming to hold NPSH `[p.345]`.
