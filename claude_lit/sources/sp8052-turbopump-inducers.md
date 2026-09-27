# SP-8052 — Liquid Rocket Engine Turbopump Inducers

## Identity

NASA SP-8052, *Liquid Rocket Engine Turbopump Inducers*, NASA Space Vehicle Design Criteria
(Chemical Propulsion), May 1971. Author Jakob K. Jakobsen (Rocketdyne Division, North American
Rockwell); edited by Russell B. Keller Jr. (Lewis); reviewed by J. Farquhar III (Aerojet),
W. E. Young (Pratt & Whitney), M. J. Hartmann and C. H. Hauser (Lewis).
`literature/NASA SP-8052 - Liquid Rocket Engine Turbopump Inducers.pdf` (NTRS 19710025474;
116 PDF leaves; clean text layer, but equations and Table I needed page renders).
**Page offset: printed p.N = PDF leaf N+11** (0-based leaf index; printed p.1 "INTRODUCTION"
= leaf 12). **One exception: printed p.63 and p.64 are swapped in the scan** (p.64 = leaf 74,
p.63 = leaf 75), so §3.2.8's continuation, §3.2.9 and §3.2.10.1 sit on leaf 75, *after* the
§3.3 page. Tag: `[SP-8052]`.

## Character

Same monograph family and layout as `[SP-8109]`/`[SP-8107]`/`[SP-8048]`: a §2 "State of the Art"
narrative (p.3-48) and a matching §3 "Design Criteria and Recommended Practices" (p.49-86, the
criteria in italic plus "recommended" practices), using the same subsection numbers (e.g.
§2.1.3 Inlet Tip Diameter ↔ §3.1.3). Written by Rocketdyne, so the real hardware is Rocketdyne's:
Thor **Mark 3** LOX, J-2 **Mark 15** (LOX, and the LH2 "Mark 15-F" axial-flow pump), X-8
**Mark 19** LOX, F-1 **Mark 10** LOX/fuel, and Phoebus **Mark 9** LH2. There's no SSME (1971),
and no RL10, H-1 or M-1 inducer data.

What it actually gives: **one real inducer design/performance table** (Table I, 6 inducers);
the **Brumfield optimum-flow-coefficient / maximum-suction-specific-speed relations** with
closed-form constants; the **NPSH factor Z ≈ 3** rule; **two real thermodynamic-suppression-head
(TSH) values**; a **tip-clearance Ss/ψ loss correlation**; and a full set of blade-geometry,
mechanical, material, vibration and structural design rules with numbers. It has **no rpm,
flowrate, NPSH or tip-diameter table** for the engines. Table I is dimensionless apart from Ss,
which is in US units.

## This note's extraction scope

**Read in full:** §1 Introduction; §2 opening incl. **Table I** (page render); §2.1 Inlet-eye
and leading-edge geometry (§2.1.1-2.1.15, incl. the equation page p.12 and p.17 rendered);
§2.2 flow-channel/blade geometry (§2.2.1-2.2.10); §2.3 inlet line; §2.4 mechanical design;
§2.5 materials; §2.6 vibration; §2.7 structural; **all of §3** (p.49-86); the Glossary (p.92-98,
for units and definitions). **Skimmed:** References p.87-89 (titles only, used to flag one
discrepancy below); Fig. 15/16 S′s-D′s charts (rendered and read for axes and curve families,
not digitized). **Not read:** References p.90-91; the NASA monograph list.

## Parameter table — Table I "Basic Inducer Types: Design and Performance Summary" `[SP-8052 Table I p.4]`

φ and ψ are based on **inlet tip blade speed**. Ss is **in water**, at **10% head dropoff from
noncavitating head**, US units (rpm, gpm, ft).

| Engine / pump | Fluid | Head type | Meridional geometry | φ_d | ψ_d | β_tip (inlet) | **Ss (water)** | ν = hub/tip | Blades | LE sweep |
|---|---|---|---|---|---|---|---|---|---|---|
| Thor Mark 3 (a) | LOX | Low | cyl. tip + hub | 0.116 | 0.075 | 14.15° | **28,500** | 0.31 | 4 | radial, rounded tips |
| J-2 Mark 15 (b) | LOX | Low | cyl. tip, tapered hub | 0.109 | 0.11 | 9.75° | **34,300** | 0.20 | 3 | swept back |
| X-8 Mark 19 (c) | LOX | Low | tapered tip + hub | 0.106 | 0.10 | 9.8° | **31,200** | 0.23 | 3 | swept back |
| X-8 Mark 19 (d) | LOX | Low | **shrouded** | 0.05 | 0.063 | 5.0° | **58,000** | 0.19 | 2 | swept forward |
| J-2 Mark 15 (e) | LH2 | High | cyl. tip, tapered hub | 0.0942 | 0.21 | 7.9° | **43,200** | 0.42 | 4+4 (splitters) | swept back |
| J-2 Mark 15 (f) | LH2 | High | tapered tip + hub | 0.0735 | 0.20 | 7.35° | **44,200** | 0.38 | 4+4 | swept back |

Definitions (Glossary p.95-98): Ss = n·Q^½/(NPSH)^¾ [rpm, gpm, ft]; φ = c_m/u_tip;
**ψ = ΔH/(u²/g)**. Note that it's u²/g, not u²/2g. K = (p_s − p_v)/(ρw₁²/2g), the blade-tip
cavitation number. τ = 2g·NPSH/u², the cavitation parameter. Z = 2g·NPSH_tank/c_m², the NPSH
factor. Q′ = Q/(1−ν²), the flow corrected to zero hub blockage, and S′s = Ss/(1−ν²)^½.

Other real per-engine numbers in the text:
- **TSH, F-1 Mark 10 LOX pump: 11 ft at 163 °R, inducer tip speed 300 ft/s. TSH, J-2 Mark 15-F
  LH2 pump: 250 ft at 38 °R, tip speed 900 ft/s** `[SP-8052 §2.1.4 p.16]`. The text calls both
  "presently established empirical values", used "with considerable reservation" on other pumps.
- F-1/J-2-size inducers leave the leading edge **0.005-0.010 in. thick** rather than knife-sharp
  `[SP-8052 §2.1.6 p.21]`.
- Phoebus Mark 9 and J-2 Mark 15-F axial-flow LH2 pumps were sized with a rotor **alternating
  shear stress = 5% of steady** `[SP-8052 §2.7.4 p.48]`.
- Reference 40's title calls the Mark 10 (F-1) LOX inducer models **"17-Inch"** `[SP-8052 ref. 40
  p.88]`. See Caveats for the conflict with the 300 ft/s figure.

## Key results

**1. Suction-performance optimization: the Brumfield criterion, zero prewhirl**
`[SP-8052 §2.1.3 p.12-13; §3.1.3.1 p.50-51]`:
- τ = K + Kφ² + φ² (eq. 2)
- S′s = 8147·φ^½·τ^−¾ (eq. 3)
- Ss = S′s·(1−ν²)^½ (eq. 4)
- Optimum: K = 2φ²_opt/(1−2φ²_opt) (eq. 5), i.e. **φ_opt = [K/(2(1+K))]^½** (eq. 6)
- **max S′s = 5055/[(1+K)^¼·K^½]** (eq. 7)

I checked the constant by substitution: 8147 × 2^−¼ × 1.5^−¾ = 5055. Suction specific speed is
"limited only by the minimum cavitation number K* at which the blade will operate". **K* of
0.01-0.006 has been measured for very thin blades with β ≈ 5° and wedge angle ≈ 2°**
`[p.12]`. Those K* values give max S′s ≈ 50,400 (K=0.01) to 65,200 (K=0.006); **this range is my
evaluation of eq. 7, not a number quoted in the text.**

Inverse form for design: given S′s, φ_opt ≈ (3574/S′s)/{[1+√(1+16(3574/S′s)²)]/2} (eq. 63). The
divisor → 1 for φ_opt ≲ 0.10, so φ_opt ≈ 3574/S′s. For example, S′s = 40,000 → φ_opt ≈ 0.089.
The OCR of eq. 63's inner term is unreliable; re-derive it from eq. 62 before coding it
`[§3.1.3.1 p.51]`.

Inlet tip diameter: **D = 0.37843·[Q/((1−ν²)·n·φ)]^⅓ ft** (Q in gpm, n in rpm; eq. 8/65). The tip
diameter is held cylindrical for at least one axial blade spacing (πD/N·sinβ) downstream of the
leading edge. The inlet duct is constant-diameter for the same length upstream, **doubled when
there's an inlet elbow** `[§3.1.3.2 p.54]`.

**Cross-check (my calculation, not in the source):** feeding each Table I φ_d into eq. 5 → eq. 7
→ eq. 4 reproduces the tabled water Ss to 1-8% for four of the six inducers:

| Inducer | Predicted Ss | Tabled Ss |
|---|---|---|
| Thor | 28,700 | 28,500 |
| J-2 LOX | 31,600 | 34,300 |
| X-8 (c) | 32,300 | 31,200 |
| J-2 LH2 (f) | 44,600 | 44,200 |

It misses the other two by about ±20%: shrouded X-8 (d) predicts 69,900 vs 58,000, and J-2 LH2
(e) predicts 34,000 vs 43,200. **Brumfield-at-design-φ is therefore a usable ~±10% (worst
±20%) estimator of achievable water-basis Ss from the flow coefficient alone.**

**Blade-level cavitation limits** `[SP-8052 §2.1.5 p.20-21]`: supercavitating
K_min = 2·sinα·sin(β−α)/(1+cosβ) (eq. 29). Its maximum over incidence is **tan²(β/2)**, at
α = β/2 (eq. 30). **"Because of blade thickness and boundary-layer blockage, in actual operation
with a real fluid the attained values of K are approximately two to three times greater than
the maximum values of K_min."** This is a real knockdown factor, 2-3×, from ideal to achieved
cavitation number. Small blade angles are the lever.

**2. NPSH-required relations** `[SP-8052 §2.1.4 p.14, 17; §3.0 p.49; §3.1.4 p.54]`:
- NPSH_required = (n·Q′^½/S′s*)^{4/3} (eq. 10), where S′s* is the **characteristic cold-water**
  suction specific speed, "assuming … characteristic suction performance is independent of the
  pump fluid".
- NPSH_available = NPSH_tank + TSH − H_loss (eq. 68). This is the design-criteria form: the TSH
  credit is added to the tank NPSH.
- **NPSH factor rule:** Z = 2g·NPSH_tank/c_m² (eq. 19); TSH = (Z_opt − Z)·c_m²/2g (eq. 20);
  **NPSH_required = NPSH_tank + TSH = Z_opt·c_m²/2g** (eq. 21); **Z_opt = 3(1−2φ²_opt) ≈ 3**
  (eq. 22).

In words, an ideal fluid needs about **3 inlet meridional velocity heads** of NPSH. This is the
same "3·c_m1²/2g" factor `[SP-8109 §3.2.1.2]` gives for low-vapor-pressure fluids. SP-8109's
2.3 (LOX) and 1.3 (LH2) factors are the TSH-credited versions of this Z.

§3.0 also gives an alternative hydrofoil-based estimate: K = C_p − 1 and
1 + τ = (1+K)(1+φ²) = C_p(1+φ²) (eqs. 60-61). C_p is about **1.3-1.5 for an uncambered
airfoil**, raised by the blockage factor squared `[§3.0 p.49]`.

**Inlet-line velocity limits** `[SP-8052 §2.3.2 p.32; §3.3.2 p.64]`: the theoretical maximum is
c_m,max = √(2g·NPSH_tank) (eq. 56). Design so the line velocity stays **10-15% below
√(2g·NPSH_tank) for LH2**, and **below √(2g·NPSH_tank/3) for all other propellants** (eq. 57).
This is the Z = 3 rule applied to the feed line, and it plugs directly into a plumbing/
feed-line velocity check.

**3. Thermodynamic suppression (TSH), the LOX/LH2 "thermodynamic effect"**
`[SP-8052 §2.1.4 p.13-17; §3.1.4 p.54]`:
- Which fluids show it: LH2, LOX, N2O4 and hot (>200 °F) water. For "ideal" fluids (cold water,
  hydrocarbon and amine fuels such as RP-1) the limit is always leading-edge cavitation with no
  TSH.
- For LH2, TSH "may be so strong that the swallowing capacity is limited only by cavitation in
  the inlet duct", i.e. by c_m²/2g = NPSH_tank,min.
- TSH is inferred, never measured directly. The text gives the thermal-cavitation parameter
  α = (ρ_v·L/ρ_L)²/(C_L·T)·J (eq. 14; the grouping comes from OCR, so re-derive it before coding),
  the thermal diffusivity κ_L = k_L/(ρ_L·C_L) (eq. 15), and Holl's thermal factor β = α/√κ_L
  (eq. 16). It also gives a dimensionless-group form, TSH/α = C·(L_c/α)^m1·(αU_c/κ_L)^m2·(L_c/S)^m3
  (eq. 17), then says: **"no such relationship with well-established values for the constants
  and exponents has been found"** `[p.15-16]`. The cavity-pressure cavitation number K_c (eq. 18)
  stays roughly constant in venturi tests. Ruggeri-Moore correlations (refs. 24-27) exist but
  "do not allow successful prediction … without … reference data" on the same pump `[p.16]`.
- **Design practice:** "An empirical allowance for TSH is added to the tank NPSH value … based
  on previous experience with the fluid. No theoretical prediction is attempted" `[p.16]`. The
  two anchors are the ones above: F-1 LOX 11 ft at 163 °R and 300 ft/s tip; J-2 LH2 250 ft at
  38 °R and 900 ft/s tip. TSH rises "almost as a linear function of vapor pressure" with
  temperature, and rises with rpm at fixed φ `[p.16]`.
- **Two-phase LH2:** current LH2 pumps pump two-phase hydrogen at up to **20% inlet vapor volume
  fraction** at design φ. The limit is choking, when the blade-passage flow area falls below the
  upstream area `[p.17]`.

**4. Tip clearance** `[SP-8052 §2.2.8 p.30; §3.2.8 p.62-63; §3.4.6 p.70-71]`:
- **Ss = Ss,0·(1 − k_s·√(c/L))** with **k_s = 0.50-0.65** (eq. 54).
- **ψ = ψ₀·(1 − k_ψ·√(c/L))** with **k_ψ = 1.0** (eq. 55).
- c is the radial clearance and L the blade radial length. The correlation comes from inducers
  with a cylindrical tip.
- **Minimum practical c/L: 0.005 for fuel pumps, 0.020 for oxidizer pumps** (LOX needs larger
  clearance to avoid metal rub, or a Kel-F liner, e.g. Fig. 20: 0.107 in. → 0.005 in. with a
  0.100 in. Kel-F foam coat).
- **Clearance area should never exceed 3% of the flow area; 1-1.5% is common practice.**
- Evaluated at those minimum c/L values (my arithmetic):

  | Pump | Ss loss | ψ loss |
  |---|---|---|
  | Fuel (c/L 0.005) | ≈3.5-4.6% | ≈7% |
  | Oxidizer (c/L 0.020) | ≈8-9% | ≈14% |

  This is a real, propellant-dependent Ss penalty that the current flat NSS target ignores.
- Clearance is "the source of the first visual occurrence of cavitation". It lowers Ss at partial
  head dropoff but not at supercavitation. Opening the clearance to cure cavitation oscillations
  is "the most ineffective and most harmful" fix `[§2.4.11 p.40]`.

**5. Head rise and efficiency** `[SP-8052 §2 p.3; §2.1.12 p.22; §3.1.10 p.57; §2.2.6 p.28;
§3.2.6 p.62]`:
- **Low-head inducer: ψ ≤ 0.15. High-head: ψ ≥ 0.15.**
- A pure flat-plate (constant-lead) inducer is capped at **ψ ≈ 0.075** by its limited turning.
  Anything more needs camber that starts at zero at the leading edge and grows monotonically,
  approximately β(z) = β₁ + (β₂−β₁)(z/L_ax)² (eq. 74).
- The high-head inducer is "actually an axial-flow impeller with an integral inducer", with
  solidity 2.0-2.5; the J-2 LH2 inducers are ψ ≈ 0.20-0.21.
- **Blade (hydraulic) efficiency for the turning-angle design is assumed at 0.85.** The inducer
  is sized so Euler head × 0.85 = required head. That is the only inducer efficiency number in
  the monograph.
- Other efficiency effects:
  - A 160 µin surface finish cut efficiency by 5.9% (chordwise striations) or 7.2% (spanwise)
    vs a 2 µin finish `[§2.1.13 p.23]`. The recommended finish is ≤25 µin rms `[§3.1.13 p.58]`.
  - Shrouded inducers perform "slightly worse" than unshrouded `[§2.2.9 p.31]`.
- Worked number (my arithmetic, not stated in the source): at the J-2 LH2 inducer's 900 ft/s
  tip speed, ψ = 0.21 ⇒ ΔH ≈ 0.21·900²/32.174 ≈ 5,300 ft of LH2.

**6. Geometry rules (design criteria)** `[SP-8052 §3.1-3.2 p.50-63]`:
- **Hub/tip ν = 0.2-0.4 for a rear-drive (overhung) inducer, 0.5-0.6 when driven from the inlet
  end** (the full pump torque then goes through the inducer hub) `[§3.1.2 p.50]`. The low-head
  hub taper is 8-12° `[§2.1.2 p.11]`.
- **Incidence/blade-angle ratio α/β = 0.35 (thin blades) to 0.50 (thick); 0.425 preferred**. Use
  a higher value if a wide flow range is needed `[§3.1.9 p.57]`.
- The blade stays inside the cavity up to **110% of design flow**. The wedge angle is
  α_w = β − β_w with β_w = arctan(1.10·φ_d) (eqs. 69-70). Above Ss ≈ 40,000 the blade must
  exactly match the computed free-streamline cavity boundary `[§3.1.5 p.55]`.
- LE radius ≤ 0.01·t (eq. 71); TE radius about 0.02·t, typically 0.025-0.050 in.
  `[§3.1.6 p.56, §3.2.4 p.61]`.
- **Leading-edge sweepback raises Ss by 10-25%** `[§2.1.7 p.21]`. Unshrouded inducers sweep back,
  shrouded ones sweep forward `[§3.1.7 p.56]`.
- **Blade count 2-5, with 3 or 4 preferred and odd numbers preferred** (to avoid alternate-blade
  cavitation). The impeller blade count should be a multiple of the inducer's `[§3.1.14 p.59]`.
- **Solidity σ = 2.5 for a low-head inducer; 2.0-2.5 for the flat-plate inlet region of a
  high-head inducer.** Anything below σ ≈ 2.0 in the inlet region "has resulted in unsatisfactory
  performance" `[§2.1.15 p.24; §3.1.15 p.59]`.
- No backflow requires the local ψ < 1 everywhere (c_z = 0 at ψ = 1) `[§3.2.1 p.60]`.
- Inducer-impeller axial gap ≥ blade gap = L_ax/σ (eqs. 76-77) `[§3.2.3.2 p.61]`.
- Deviation angle by a modified Carter's rule, δ = M·Δβ/σ^b, with M = 0.25-0.35 and b ≈ 0.5
  for inducers (eqs. 48-53). Blade-angle tolerance ±½°; target within 5% of design `[§2.2.7
  p.29; §3.2.7 p.62]`.
- **Backflow sets in at ≈90% of design flow or less.** A backflow deflector helps between 20% and
  90% flow and hurts above nominal. Prewhirl by ~10% recirculation raised throttled Ss by up to
  50%, but is still experimental `[§2.3.5 p.33-34]`.
- **Cavitation-induced oscillations run at 5-40 Hz**, with no stability criterion known
  `[§2.4.11 p.39]`.

**7. Structural and vibration criteria** `[SP-8052 §2.6-2.7 p.43-48; §3.6-3.7 p.76-86]`:
- Mechanical design speed = **max(110% of max speed, 120% of nominal)** `[§3.7.1 p.79]`.
- Alternating blade load = **20-30% of the steady hydrodynamic load** (20% "has given satisfactory
  results") `[§2.7.1 p.45; §3.7.1 p.79]`.
- **Radial load = 30% of inducer axial thrust**, unless better data exist `[§2.7.1 p.46;
  §3.4.6 p.71]`. Dynamic axial forces are also taken as 30% of steady `[§3.4.5.1 p.68]`.
- **Safety factors: fatigue 1.5, ultimate 1.5, yield 1.1** at the mechanical design speed
  `[§3.7.5.3 p.85]`.
- **Hub burst speed ≥ 1.20 × and yield speed ≥ 1.05 × the mechanical design speed**
  `[§3.7.3.3 p.82]`. Burst speed n_burst = n·√(σ_AT,burst/σ_AT), with σ_AT,burst = f_b·F_tu and
  the burst factor f_b read from Fig. 21 (elongation × design factor f_d = σ_AT/σ*_MT)
  (eqs. 82-84).
- Spin proof test when the design speed exceeds 60% of burst: ≥2 min, with ≥10% margin to burst
  `[§3.7.7 p.86]`.
- **Blade resonance margin ≥ 15%** vs fixed-wake forcing. Only 1st and 2nd harmonics matter
  `[§3.6.2 p.76]`.
- Virtual-mass frequency drop: **about 4% in LH2 and 24-31% in LOX** (two designs)
  `[§3.6.4.4 p.78]`.
- Cavitation oscillations fall at 1-100 Hz, below the natural frequencies of rigid high-head
  blades `[§2.6 p.43]`.
- Shaft allowable alternating shear τ_alt/τ₀ = 0.05 (eq. 86) `[§3.7.4 p.83]`. Add 10-15% to the
  structurally required shaft diameter to allow for later redesign `[§3.4.3.1 p.67]`.
- Typical balance is 0.01 oz·in per plane for a 10-15 lb part at about 30,000 rpm
  `[§3.4.10 p.73]`.

**8. Materials** `[SP-8052 §2.5 p.40-43; §3.5 p.73-76]`:
- **Ti-5Al-2.5Sn ELI for LH2 inducers.** Ti-6Al-4V is not used below −320 °F (notch toughness).
- Annealed Ti-6Al-4V for RP-1 (it replaced an aluminum inducer for erosion resistance).
- **No titanium in any oxidizer pump** (LOX, LF2, FLOX, N2O4, IRFNA).
- Oxidizer pumps use aluminum (7079-T6, 7075-T73, 2024-T4, 2014-T6), 304/347 stainless,
  K-Monel or Inconel 718. K-Monel or Inconel 718 is used for low-speed cavitating LOX inducers.
- Aluminum needs an anodic coat of 70-300 µin, never >500 µin (fatigue).
- These are useful rules for `turbopump_materials.py`'s rotor catalog (propellant compatibility).

## Design method

This is a real, step-by-step sizing procedure — unusual for the SP-80xx series — that maps
almost one-to-one onto a code model `[SP-8052 §3.1.3.1 p.50-54]`:

1. **Case A (Q, n and NPSH all given).** Compute S′s = n·Q′^½/NPSH^¾, then φ_opt from eq. 62/63,
   then K_d = 2φ²_opt/(1−2φ²_opt) (eq. 64), then D_opt (eq. 65). K_d is the cavitation number the
   blade must survive; it must stay ≥ an empirical K* (thin blades reach 0.006-0.01).
   **Case B (only two of Q, n, NPSH given).** Pick K* from experience, then
   φ_opt = √(K*/(2(1+K*))) (eq. 66), then max S′s = 5055/(K*^½(1+K*)^¼) (eq. 67). That fixes the
   rpm or NPSH.
2. Fig. 15/16 (S′s-D′s charts, p.52-53) plot the same relations with lines of constant K, φ and
   τ/φ² (= Z). They're used to check an existing design, re-rate for a new fluid (via Z), or
   pick φ_opt and D.
3. Add the TSH allowance to the tank NPSH (eq. 68), or equivalently use a fluid-specific Z < 3
   (eqs. 19-22).
4. Set β_tip from α/β = 0.425 at φ_d; set the wedge angle so the blade sits inside the cavity to
   110% flow (eqs. 69-70); use a constant-lead flat-plate inlet (λ = r·tanβ); σ ≈ 2.5; 3 blades.
5. Camber the channel region for the head requirement: Euler head × 0.85 blade efficiency, with
   deviation from Carter's rule. Check for no backflow using simple radial equilibrium (eqs.
   33-41).
6. Degrade for tip clearance (eqs. 54-55), then run the structural and vibration checks in §3.6-3.7.

## Section map

- §1 Introduction: p.1-2 (leaf 12-13). Read.
- **§2 opening, inducer classification, Table I: p.3-6 (leaf 14-17). Read, Table I rendered.**
- **§2.1 Inlet-eye and leading-edge geometry (2.1.1 casing, 2.1.2 hub, 2.1.3 tip diameter
  (Brumfield), 2.1.4 thermodynamic effects/TSH, 2.1.5 blade profile/cavity theory,
  2.1.6-2.1.15 LE sharpness, sweep, cant, angle, lead, thickness, camber, finish, number,
  solidity): p.7-24 (leaf 18-35). Read in full.**
- §2.2 Flow channel and blade geometry (channel flow, discharge, impeller matching, TE,
  deviation, **2.2.8 clearance losses**, shrouding): p.24-31 (leaf 35-42). Read.
- §2.3 Inducer inlet line (velocity limit, heat transfer, bypass, backflow/prewhirl):
  p.31-34 (leaf 42-45). Read.
- §2.4 Mechanical design and assembly (incl. 2.4.11 cavitation-induced oscillations):
  p.34-40 (leaf 45-51). Read.
- §2.5 Materials, §2.6 Vibration, §2.7 Structural: p.40-48 (leaf 51-59). Read.
- **§3.0 Head-rise capability, §3.1 inlet/LE design criteria incl. §3.1.3 sizing procedure and
  Fig. 15/16 S′s-D′s charts: p.49-59 (leaf 60-70). Read in full.** Charts viewed, not digitized.
- §3.2 Flow channel criteria: p.59-63 (leaf 70-73, 75). Read. p.63 = leaf 75 (scan order swap).
- §3.3 Inlet line criteria: p.64-65 (leaf 74, 76). Read.
- §3.4 Mechanical: p.65-73 (leaf 76-84). Read.
- §3.5 Materials, §3.6 Vibration, §3.7 Structural: p.73-86 (leaf 84-97). Read.
- References: p.87-91 (leaf 98-102). Titles skimmed to p.89 only.
- Glossary: p.92-98 (leaf 103-109). Read for units and definitions.

## Caveats

- **Table I Ss values are cold-water, 10%-head-dropoff numbers, not flight-fluid values.** For
  LH2, the flight suction capability is far higher because of TSH (250 ft on the J-2 Mark 15-F).
  Don't compare a TSH-inclusive "effective" Ss, such as `turbopump_sizing.py`'s
  `NSS_TARGET_US["lh2_class"] = 58,027` back-solved from the J-2's flight NPSH, against these
  water values as if they were the same quantity.
- **The 58,000 in Table I is an X-8 LOX shrouded 2-bladed low-speed inducer**, not LH2. It is
  numerically near the code's `lh2_class` 58,027 only by coincidence. The J-2 **LH2** inducers
  test at 43,200-44,200 in water.
- **The F-1 "300 ft/sec" inducer tip speed looks inconsistent.** At `[SP-8107]`'s 5,488 rpm it
  implies a ≈12.5 in. tip. With `[SP-8107]`'s 25,200 gpm that gives φ ≈ 0.24, about 2× anything in
  Table I. Reference 40 describes "17-Inch Mark 10 LOX Inducers"; a 17 in. tip gives ≈407 ft/s
  and φ ≈ 0.096, which fits Table I. Treat the 300 ft/s (and therefore the F-1 TSH's speed
  context) as approximate. The J-2 LH2 900 ft/s is self-consistent: at 27,000 rpm it gives
  D ≈ 7.6 in. and, with Table I (e)'s φ/ν, Q ≈ 10,000 gpm. **That rpm comes from `[SP-8107]` via
  the code, not from this monograph.**
- **No per-engine rpm, flow, NPSH or tip-diameter table.** The only absolute numbers are the two
  TSH/tip-speed pairs. Engine-level N, Q and NPSH must still come from `[SP-8107]` Table II /
  `[SP-8109]`.
- **TSH is explicitly unpredictable** a priori. The monograph's own recommended practice is an
  empirical per-fluid allowance from similar pumps. Any TSH model built on eqs. 14-17 would be
  beyond what this source supports. It gives the functional form but no constants.
- Some equations were garbled in the OCR text layer. I checked eqs. 2-8, 19-22 and 54-55 on
  rendered pages, and checked eq. 7's 5055 constant algebraically. Eqs. 14, 63 and 86 were not
  render-checked and should be re-derived before coding.
- The Brumfield-vs-Table-I cross-check (1-8% on 4 of 6 inducers) is **my own computation**. The
  source doesn't claim that agreement.
- The data is 1971 Rocketdyne hardware (Thor, J-2, X-8, F-1, Phoebus). There is no SSME, RL10,
  RD-series or modern high-Ss (>60k) inducer data.
