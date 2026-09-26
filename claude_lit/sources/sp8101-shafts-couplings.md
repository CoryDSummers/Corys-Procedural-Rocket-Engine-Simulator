# NASA SP-8101 — Liquid Rocket Engine Turbopump Shafts and Couplings

## Identity

NASA SP-8101, *Liquid Rocket Engine Turbopump Shafts and Couplings*, NASA Space Vehicle Design
Criteria (Chemical Propulsion), September 1972. Written by L. K. Severud and C. C. Purdy
(Aerojet Liquid Rocket Co.), edited by R. B. Keller Jr. (Lewis); reviewed by J. T. Akin
(P&WA), J. O. Pfouts (Rocketdyne) and D. W. Drier (Lewis). `literature/NASA SP-8101 - Liquid
Rocket Engine Turbopump Shafts and Couplings.pdf` (NTRS 19740006328; 136 PDF leaves). Fixed
offset: **printed page N = `fitz` 0-based leaf index N+13** (= 1-based PDF page N+14), e.g.
printed p.6 (Table I) is leaf 19, printed p.79 (§3.2.1.2.1) is leaf 92, which I confirmed by
rendering. Tag: `[SP-8101]`.

**Technical note on this PDF**: it has a real text layer, unlike `[SP-8048]`. `fitz`
`get_text()` returns one word per line with frequent OCR substitutions ("tile" for "the",
"_" for dropped glyphs, run-together words on some pages). Joining the lines gives
greppable prose. The tables are garbled in the text layer, so Tables I-IV and VI (printed
p.6, 10, 12, 14, 47) were rendered to PNG and read by eye. Every number in the tables below
comes from those renders.

## Character

This monograph follows the same parallel-numbered layout as `[SP-8048]`/`[SP-8107]`/
`[SP-8120]`: §2 State of the Art (narrative, real-engine anecdotes) and §3 Design Criteria and
Recommended Practices (imperative "shall" italic text followed by "should" practices). The
§2.x and §3.x headings mirror 1:1. It has four parts: **2.1/3.1 Shaft Design** (speed, bearing and
seal location, size, discontinuities, environment, materials, structural analysis, fits/bolts/
locking, QC), **2.2/3.2 Shaft Dynamics** (whirl, critical speeds, instabilities, torsional
criticals, modelling, prediction accuracy, tuning, balancing), **2.3/3.3 Coupling Design**
(splines, curvic couplings, parallel-sided face couplings) and **2.4/3.4 Design Confirmation
Tests**.

The introduction (p.1) sets the monograph's framing: **"adequate strength and fatigue life ...
has not been a major problem in design because power torque loads relative to shaft size
generally have been low. However, the achievement of acceptable shaft dynamic characteristics
has required major design and development programs."** The authors are Aerojet engineers, so
most detailed examples come from the Titan XLR-87/XLR-91 and the M-1. F-1/J-2/RL10/H-1 appear
mostly in the safety-factor table, the anecdotes and the geared-vs-direct list. **No real
F-1/J-2/H-1/RL10 shaft diameter, torque, or critical-speed value is given anywhere.** This is
a criteria document. It is not a data book.

## This note's extraction scope

I read the full text of §1 (p.1-2), §2.1 (p.3-18), §2.2 (p.19-48, partly figure-only pages),
§2.3 (p.49-54), §2.4 (p.54-59), all of §3 (p.60-96) and the Glossary (p.109-113, part). Tables
I, II, III, IV and VI were rendered as images. **Not read**: the References list (p.97-108),
the Materials list past its first entries, the monograph index, and the content of figures
that have no text (Figs 1, 4, 6-8, 13, 14, 17, 19; their captions and surrounding text were
read).

## Parameter / results tables

**Table I — Demonstrated rolling-contact bearing DN and seal rubbing velocity** `[SP-8101
§2.1.1.3 p.6]`. In the text, "the current limit of DN for rolling-contact bearings in rocket
engines is approximately **1.0 to 2.0 million**":

| Engine | Environment | Bearing DN (million) | Seal rubbing velocity (ft/s / m/s) |
|---|---|---|---|
| J-1 | LH2 | 1.6 | 275 / 83.8 |
| M-1 | LH2 | 1.6 | 275 / 83.8 |
| M-1 | LOX | 0.5 | 86 / 26.2 |
| XLR-87-AJ-9 | Oil | 1.35 | 232 / 70.7 |
| ARES engine | N2O4, A-50 | 1.6 | 275 / 83.8 |
| XLR-87-AJ-3 | Oil | 1.19 | 204 / 62.1 |
| XLR-87-AJ-5 | Oil | 1.08 | 185 / 56.4 |

**Table III — Typical safety factors used in shaft design** `[SP-8101 §2.1.3.2 p.12]`:

| Engine | Yield SF | Ultimate SF |
|---|---|---|
| XLR-87-AJ-3/5 and XLR-91-AJ-3/5 | 1.0 | 1.25 |
| M-1 | 1.0 | 1.5 |
| XLR-87/91-AJ-9 | 1.0 | 1.4 |
| **J-2 and F-1** | **1.1** | **1.5** |
| ARES | 1.2 | 1.6 |
| **RL10** | **1.2** | **1.5** |

"Generally, the fatigue safety factors are not specified. Values of 1.25 and 1.33 have been
used."

**Table II — Materials successfully used for turbopump shafts** `[SP-8101 §2.1.2 p.10]` (X =
performed satisfactorily in that fluid):

| Material | H2 | O2 | N2O4 | A-50 | N2 | MIL-L-7808 oil | F2 |
|---|---|---|---|---|---|---|---|
| Inconel 718 | X | X | | | X | | |
| Inconel X | X | X | | | | | |
| K-monel | X | | | | | | |
| Rene 41 | X | | | | X | X | |
| CRES 300 | X | | | | | | |
| AM 350 | | | X | X | | | |
| 9310 | | | | | | X | |
| **4340** | | **X** | | | | | |
| 440C | | | | | | | X |

**Table IV — Typical shaft/bearing tolerances** `[SP-8101 §2.1.4.1 p.14]`: XLR-87-AJ-5
**40/55 mm bore** bearings (bearing ID ±0.0001 in, shaft OD ±0.0001 in, total ±0.0002 in /
±5.1 µm); M-1 **110/120 mm bore** (±0.00012 / ±0.00015, total ±0.00027 in / ±6.86 µm); RL10
fuel pump front and rear (±0.00010 / ±0.00025, total ±0.00035 in / ±8.89 µm). The bearing bore
*is* the shaft journal OD, matched to a few µm.

**Table VI — XLR-87-AJ-9 (Titan III) turbine shaft, calculated vs. measured natural
frequencies** `[SP-8101 §2.2.2.3 p.47]` (the text on p.46 calls it "Table VII", a typo).
Refined double-beam rotor/bearing/casing model, forward circular whirl: 200/220, 328/374,
456/530, >650 Hz (min/max-stiffness casing). Spin-test vibration buildup with tight fits:
200-215/260-270, 330-343/372-390, 407/440-450, >500 rps. Kinetic-energy share by mode (rotor
%/casing %): 198/220 Hz 7/93; 327/372 Hz 13/87; 403/480 Hz 4/96; **456/530 Hz 74/26**; 635/671
Hz 95/5. Only the upper two modes are rotor-dominated ("major" in the §3.2.1.2.1 sense).

## Key results

### 1. Shaft size is set by stiffness and DN, not by torsion (direct bearing on `SHAFT_ALLOWABLE_SHEAR_PA`)

- "For most rocket engine turbopumps, **shaft size at the bearing locations is governed by
  stiffness (critical-speed) criteria rather than by stress criteria.** Usually, the shaft size
  is made **as large as possible consistent with DN and seal-rubbing-velocity limitations**"
  `[SP-8101 §2.1.1.3 p.6]`. Design criterion: "The shaft diameter at bearing locations should
  be made as large as practical so that the rotor is as stiff as possible ... **Shaft torsional
  shear stress rarely is a controlling factor in establishing shaft diameter**" `[SP-8101
  §3.1.1.3 p.62]`.
- **Preliminary-design torsional allowable**: "the allowable shaft shear stress at locations of
  rolling-contact bearings often is taken as **two-thirds of the ultimate shear strength** of
  the shaft material" `[SP-8101 §2.1.1.3 p.7]`. This is the only explicit shaft shear
  allowable in the monograph. It is a *fraction of the material's ultimate shear*. It is not an
  absolute MPa value, so using it needs an ultimate-shear figure for the chosen shaft alloy from
  a materials source (MIL-HDBK-5 "A" values are what SP-8101 recommends, §3.1.2.1 p.67). SP-8101
  itself gives no alloy strength numbers.
- **Spline "boundary line" shear stress** (case-hardened ferrous material): **~65,000 psi
  (448 MN/m²) for a solid shaft, 95,000 psi (655 MN/m²) for a hollow shaft with bore = 75% of
  OD** `[SP-8101 §2.3.1 p.50]`. This is a real ceiling on torsional shear that has been
  practised in splined turbopump shafts. The tool's 200 MPa is ~45% of the solid-shaft figure.
- Hollow thin-wall shafts are checked for torsional (shear) buckling `[SP-8101 §2.1.1.3 p.7,
  §3.1.1.3 p.62]`. Thin-wall drum-type shafts (M-1 fuel turbopump) are limited by centrifugal
  stress instead: **outer wall speeds up to 1100 ft/s (335 m/s) demonstrated** `[SP-8101
  §2.1.1.3 p.7]`.
- **Hollow shaft wall at bearings**: when the shaft is the inner race, wall ≥ **2× a normal race
  thickness** (hardened). With a separate inner race, **shaft wall = race thickness** `[SP-8101
  §3.1.1.3 p.62]`. When DN limits the journal, the shaft can be machined as the bearing inner
  race (if hardenable) so that a larger diameter fits under the same DN.

### 2. Bearing bore vs. shaft diameter (bearing on `BEARING_BORE_OVER_SHAFT_FACTOR`)

SP-8101 gives no bore/shaft ratio > 1. Its geometry runs the other way: "shaft diameters at
bearing locations are **reduced** to keep DN values acceptable, allow shoulders for bearing
races" while the spans between have "numerous increases in cross section required to provide
maximum overall shaft bending stiffness" `[SP-8101 §2.1.1.4 p.7]`. The bearing bore equals
the journal OD to within ±2.5-6 µm (Table IV, p.14). The cited sizing logic is therefore:
**journal OD = bearing bore = the largest diameter the DN limit allows (≈1.0-2.0×10⁶ DN,
Table I; SP-8048 criterion ≤3.0×10⁶), then check torsion (≤ 2/3 ultimate shear) at that
diameter.** The torsion diameter is a lower bound, not the design value. The tool's "torsion
diameter × 1.15 = bore" has no support here. Real journals sit at or near the DN ceiling,
and the between-bearing shaft is *larger* than the journal.

Seal limits that can bind the same diameter: **face-contact seals run to 500 ft/s (152 m/s)**
in LH2/LOX/RP-1, **PV 40,000-80,000 psi·ft/s (84-168 MN/(m·s))**. "For rolling-contact
bearings, DN is a more restrictive factor than seal rubbing velocity." Fluid-film bearings
have no DN limit, so seal velocity becomes the limit there `[SP-8101 §2.1.1.3 p.7]`.

### 3. Critical-speed margin rules (the future rotordynamics check)

- **Supercritical-rotor rule (the main numeric criterion)** `[SP-8101 §3.2.1.2.1 p.79]`: "The
  lowest major critical speed whose mode shows a preponderance of the system potential energy
  to be due to **rotor bending** ... should be **no lower than 125 percent of the normal
  operating speed or 115 percent of the maximum overspeed, whichever is greater**."
- **Rigid-body/support modes below running speed are allowed** when the mode "involve[s]
  appreciable stator or bearing deformation": (1) **≤ 85% of the lowest steady-state operating
  speed**; (2) as low as practical; (3) traversed fast enough to limit response; (4) no
  self-excited whirl grows to untenable levels `[SP-8101 §3.2.1.2.1 p.79-80]`. Closer
  criticals need approval by full rotor/stator vibration test.
- Together these give an allowed operating band: **≥1/0.85 = 1.18× the last sub-running
  support-mode critical, and ≤1/1.25 = 0.80× the first bending critical** (or ≤ overspeed/1.15).
  Supercritical designs with flex-mounted bearings put criticals 1 and 2 (rigid-body
  translation/rotation) low and run "up to speeds just below the third critical (the first mode
  to contain significant shaft bending)" `[SP-8101 §2.1.1.1 p.4; §2.2.3 p.46 Fig.19]`.
- **Design/overspeed speed**: use the max 3-sigma steady-state speed for strength and HCF
  checks. If it is unknown, "**mechanical design speed exceed nominal maximum operating speed
  by a factor of 1.1 to 1.2**" `[SP-8101 §3.1.1.1.2 p.60]`. Start overshoot: good systems hold
  **≤3%**; 5-10% is common, and some reached **25%** `[SP-8101 §2.1.1.1 p.5]`. Criticals must
  also be kept clear of dwell and overshoot speeds.
- **Prediction accuracy** `[SP-8101 §2.2.2.3 p.45; §3.2.2.3 p.87]`: rotor/bearing-governed
  criticals **±5%**; rotor/bearing/casing-coupled **±10%** (with the §3.2.2.1 modelling
  conditions met); otherwise **±20%, sometimes ±50%**. Criterion: "calculated critical speeds
  should **never be considered more accurate than ±5 percent**." Response amplitudes and
  bearing loads can be **2-3×** the prediction. "Most turbopump operating speeds usually come
  within **15 to 20 percent** of a major critical speed."
- **Mount rigid-body modes** typically sit at **~5-10% of nominal shaft speed** and can be left
  out of high-speed response models `[SP-8101 §2.2.2.1.3 p.37]`.
- **Subcritical vs supercritical** `[SP-8101 §2.1.1.1 p.4-5; §3.1.1.1.1 p.60]`: "shafts should
  be designed purposely for either subcritical or supercritical operation." Subcritical design
  means no resonance passage, but it forces a large shaft diameter (high DN/seal speed), stiff
  bearings (usually cylindrical rollers) and a stiff housing, and it may cap speed and pump
  performance. Supercritical design lowers bearing loads but risks damage in transit and
  self-excited subsynchronous whirl, and "usually [is] limited in capability to throttle to low
  speeds safely." **Built-up/shrink-fit rotors should not run above the first
  significant-bending critical** unless damping prevents rubs or overloads `[SP-8101 §3.2.1.3
  p.81]`.
- **Torsional criticals** `[SP-8101 §2.2.1.4 p.30; §3.2.1.4 p.81]`: they "have not limited or
  controlled design" and are often not calculated. Criterion for geared or flexible-coupled
  systems: steady speed must not coincide with the first torsional natural frequency **or 1/2 or
  1/3 of it**. Tooth, vane and blade count × speed must also avoid a natural frequency.
- **Self-excited whirl frequency**: typically **40-50% of rotational speed** (aerodynamic,
  seal-clearance whirl). It was cured "in almost every instance" by stiffening the rotor or its
  support `[SP-8101 §2.2.1.3.1 p.29]`.
- **Component resonance rule**: natural frequencies of impellers, turbine wheels, housings,
  manifolds, mounts and long tie bolts must be kept off **1×, 2×, 3× shaft speed** `[SP-8101
  §3.1.1.1.3 p.61; §3.1.4.3.3 p.76]`. The same applies to the rotor axial rigid-body mode
  `[SP-8101 §3.1.3.1 p.69]`.
- **Preliminary dynamic loads**: axial vibration ≈ **5% of bearing thrust load**; torsional
  vibration ≈ **5% of nominal power torque**. Rotor-dynamic radial loads have sometimes been
  **2×** the response-analysis prediction `[SP-8101 §3.1.3.1 p.69; §2.1.3.1 p.12]`.
- **Bearing stiffness**: rolling-contact bearing damping is negligible, so stiffness governs.
  High-speed effects cut angular-contact radial stiffness by **~50%** at low radial load (40 mm
  15° bearings), which negates preload `[SP-8101 §2.2.2.1.4 p.38-39]`. Roller bearings follow
  R = A·δ^B (load-stiffening). Use the secant stiffness K = R/δ for whirl.

### 4. Real-engine shaft and dynamics data points (sparse)

- **Titan II XLR-87-AJ-5** built-up shaft (angular-contact bearings, asymmetric casing): rigid-
  mount shake-test fundamental bending **315-365 cps** (amplitude-dependent). Spin test in the
  casing showed dual peaks at **~290 and ~340 rps** (lateral, not circular, so gyroscopic
  stiffening was lost) `[SP-8101 §2.2.1.2 p.26]`. Shake test vs analysis: **340 vs 330 Hz**
  `[SP-8101 §2.4.1 p.54]`. Sporadic turbine-shaft bearing failures were "primarily associated
  with inadequate margins for whirl critical speeds" `[SP-8101 §1 p.1]`. The high-speed shaft
  weighed **~25 lb (11.3 kg)** and was balanced to 0.01 in·oz static. Pilot looseness of 0.001
  in allowed reassembly imbalance ~0.4 in·oz, **40×** spec, which led to a redesign `[SP-8101
  §2.2.2.1.5 p.41]`.
- **NERVA 3-stage-turbine turbopump** shake test 1st/2nd: **295/520 Hz** (analysis 305/522);
  **XLR-87-AJ-9** high-speed shaft **540 Hz** (analysis 517) `[SP-8101 §2.4.1 p.54]`.
- **XLR-87-AJ-9 turbine shaft**: see Table VI. Secondary (casing-dominated) criticals showed
  only 2-3× dynamic magnification. Loose fits shifted secondary criticals by up to **10%** and
  caused unstable "growling" response `[SP-8101 §2.2.1.2 p.23]`.
- **Geared vs direct drive**: "both XLR-87-AJ-5 and XLR-91-AJ-5 turbopumps and the **RL 10 and
  H-1** turbopumps are geared systems. However, because of power and speed limitations as well
  as added design complexity for geared designs, **the trend is away from gearboxes**"
  `[SP-8101 §2.1 p.3]`.
- **Real failures** `[SP-8101 §1 p.1; §2.1.4.2 p.15]`: **F-1 LOX pump metal ignition and
  catastrophic failure from fretting of the shaft-to-impeller splines**; **J-2 fuel-pump rotor
  tip rubs / turbine blade rubbing tied to disk vibration modes and subsynchronous shaft whirl**
  (disks redesigned to raise axial critical, rotor high-speed rebalanced); M-1 fuel turbine
  wheel dished from axial thermal gradient and rubbed the nozzle; subsynchronous whirl of the
  Mark 25, "E"-blade Mark 9 (catastrophic) and RL-129 LH2 pump. Axial tip motion can be **4-5×**
  the radial motion at the same location.
- **M-1 fit/thermal**: 440C bearings on Rene 41 (turbine end) and Inconel 718 (pump end) shaft
  needed **+0.0012 in and +0.002 in** extra room-temperature interference to hold at 20 K.
  XLR-87-AJ-9 Rene 41 shaft + M-50 bearing (matched expansion) changed fit by only 0.0002 in
  over a 280°F rise `[SP-8101 §2.1.4.1 p.14]`. Centrifugal growth materially eats bearing
  internal clearance above **1.0×10⁶ DN**.
- Titan II stage-1 turbopump bearing **soakback 560°F (566 K)** 10 min after shutdown `[SP-8101
  §2.1.1.5 p.8]`. Shaft thermal transients span **-420°F (22 K) to ~1400°F (1033 K)**.

### 5. Structural criteria

- **Safety factors on limit loads (criterion)**: **≥ 1.1 yield, 1.3 ultimate, 1.25 fatigue.
  Preferred 1.1 / 1.4 / 1.33** `[SP-8101 §3.1.3.2 p.70]`. Use statistically determined factors
  when data exist.
- HCF: von Mises (distortion-energy) effective stress, endurance strength knocked down for
  finish/size/temperature/notch/residual stress/corrosion/plating/reliability, and a modified
  Goodman diagram for mean + alternating stress. **Miner cumulative damage usage factor 0.70**
  `[SP-8101 §3.1.3.3 p.71]`.
- Thermal loads: add **+50°F (28 K) or 5% of max metal temperature, whichever is lower**, as the
  only thermal safety factor `[SP-8101 §3.1.1.5.1 p.64]`.
- Material data: MIL-HDBK-5 "A" values (95% confidence that 99% exceed). Minimum **5%
  reduction in area** and **>15 ft·lb (20.3 N·m) Charpy V-notch** at operating temperature
  `[SP-8101 §3.1.2.1 p.67; §3.1.2.4 p.68]`.
- Transition fillets: ideal radius **3× the smaller diameter**. Otherwise apply Kt from
  Peterson-type curves. Shaft surface finish **16 µin (0.41 µm) rms**; seal faces **10-20 µin**
  `[SP-8101 §3.1.1.4 p.63]`. Circular fillets are the norm (axial space), and the added
  stress concentration "rarely has been a limiting design factor" `[SP-8101 §2.1.1.4 p.8]`.

### 6. Materials

- Recommended high-strength shaft alloys to match the bearing steels (M-50, 440C, 52100):
  Inconel 718, 17-4PH, Rene 41, Waspaloy `[SP-8101 §2.1.2 p.10]`. See Table II for service
  history.
- **"Low-alloy steels such as 9310, 4340, 440C, and AM-350 should not be used at cryogenic
  temperatures"** `[SP-8101 §3.1.2.4 p.68]`. The state-of-the-art text says cryogenic
  temperatures embrittle 9310/4340/440C "sufficiently that they rarely are used as shaft
  materials in this environment" `[SP-8101 §2.1.2 p.10]`. **Yet Table II lists 4340 as
  satisfactory in oxygen service.** This matches `[Ch12-Materials]`'s "shaft: 4340" for the
  F-1 (a LOX/RP-1 pump whose shaft was not necessarily at LOX temperature throughout). An LH2
  shaft in the tool should not default to 4340.
- High-pressure GH2 embrittlement: avoid ferritic/martensitic steels, and avoid **Inconel 718,
  Inconel X, Waspaloy, Rene 41** where possible (they are "severely embrittled"). Recommended:
  300-series austenitic stainless, **A-286**, ARMCO 21-6-9, 22-13-5, and Al 6061-T6/7075-T73
  `[SP-8101 §2.1.1.5 p.8-9; §3.1.1.5.2 p.65]`.
- **No titanium in oxygen turbopumps** (rub ignition) `[SP-8101 §3.1.1.5 p.64]`. Stress-
  corrosion-prone steels to avoid: 17-4PH, 17-7PH, PH15-7Mo, AM-355, H-11, Vascojet 1000, and
  low-alloy steels above 180 ksi yield `[SP-8101 §3.1.1.5.3 p.66]`.
- Galling fixes: XLR-87-AJ-3 4610 shaft galled, so the -AJ-5 went to AM 350 nitrided to Rc58.
  An AM 350 bolt on a Rene 41 shaft galled and was fixed with a 7075 sleeve `[SP-8101 §2.1.2
  p.11]`.

### 7. Couplings and splines (dual-shaft / geared arrangements)

**Selection rule** `[SP-8101 §3.3 p.89]`: **splines** where there is torque but no axial load
and room for separate piloting; **curvic couplings** for highly loaded torque + axial joints
needing precision piloting; **parallel-sided face couplings** only for lightly loaded joints.
Splines are the most-used coupling (load capacity, cost, reliability). Fitted-bolt/friction-
flange/ball splines are rare, and ball splines have never flown `[SP-8101 §2.3 p.49-50]`.

**Splines** `[SP-8101 §2.3.1 p.49-50; §3.3.1 p.89-90]`:
- Standard: ANSI B92.1. **Main-drive: 14½° pressure angle, 30% stub tooth, even tooth count,
  full-fillet roots**. Accessory drives: 30°, 50% stub. Most fixed splines in service were 30°
  involute stub.
- **Teeth in contact**: assume **25%** (lightly loaded) or **50%** (highly loaded, tight
  tolerances and full inspection). Common practice is 50% for compressive and tooth-shear stress.
- **Length**: **2/3 to 1 shaft diameter** recommended. A fixed spline of face width 1/3 pitch
  diameter equals the shaft's shear strength (uniform load), and spacing error pushes practical
  face width to **≥2/3 pitch diameter**.
- Shear boundary **65 ksi solid / 95 ksi hollow (bore 0.75 OD)**. Initial sizing by bearing
  contact stress **4,500-20,000 psi (31-138 MN/m²)** depending on spline type.
- **Crowned splines tolerate 0.25-3° misalignment** (fully crowned: up to 3° in service).
- Oxidizer/monoprop inducers/impellers: splines straddled by centering pilots, Class 1 loose
  side-fit splines, pilots tight (interference) at operating temperature. Example: Al pumping
  element on Inconel X-750 shaft ≈ **0.001 in interference per inch of pilot diameter** (1-3 in
  pilots). "Clearly defined fretting normally is not allowed" in oxidizer pump splines. Keep
  splines away from main bearings so that bearing-failure heat does not destroy spline capacity
  `[SP-8101 §3.1.1.2 p.62]`.

**Curvic couplings** `[SP-8101 §2.3.2 p.50-52; §3.3.2 p.91-92]`:
- **Initial-sizing formula (ref. 143, 12.5%-of-diameter face, 150 ksi ultimate)**: **OD [in] =
  (T [in·lbf] / 1310)^(1/3)**, SI **OD [m] = (T [N·m] / 9.03×10⁶)^(1/3)**. I checked this
  against the monograph's own real example: **~800,000 in·lb (90 kN·m) through an 8.43-in mean
  diameter, 0.62-in face**. The formula gives OD = (90,000/9.03e6)^(1/3) = 0.215 m = 8.5 in,
  which is consistent.
- Disk OD / coupling OD **≤ 4** (normal 2; Titan III-M and SNAP-8 used 4, "unusual"). Coupling
  ID ≈ **0.75 × OD**. Tooth contact angle 20-30°, **30° recommended**. Ref-143 stress limits may
  be **doubled for short-life (≤1 h) designs**.
- **Retaining-bolt preload ≥ 1.5-2× the separating force** `[SP-8101 §3.1.4.3.2 p.75;
  §3.3.2.2 p.91]`. Preload is set by bolt elongation, not torque. XLR-87-AJ-9 torque scatter was
  195-330 lbf·ft for the same 0.009-in stretch `[SP-8101 §2.1.4.3 p.16]`.
- Built-up rotors are much softer than one-piece ones. A curvic joint can open under turbine-wheel
  moment and then lose stiffness. For dynamics models, use an equivalent-beam section of wall
  **t/F = 0.01-0.03** of tooth face width over the tooth whole depth `[SP-8101 §2.2.2.1.2 p.34;
  §3.2.2.1.2 p.83]`.
- Inspection: master-to-master contact ≥ 90% of theoretical, part contact ≥ 75% of tooth width
  `[SP-8101 §3.1.5.4 p.78]`.

**Parallel-sided face couplings** were used on early Titan III XLR-87-AJ-9 rotor joints and
**replaced by curvic couplings** because the pilot fit could not hold alignment `[SP-8101
§2.3.3 p.54]`.

### 8. Assembly, balancing, locking (brief)

- Balance to **50-100 µin (1.27-2.54 µm) eccentricity**. Balance in **≥ n+2 planes** for n
  bending criticals traversed. High-speed dynamic balancing is required above the first bending
  critical `[SP-8101 §3.2.4 p.88]`.
- Locking: crimp-type washers (**0.030-0.035 in** wall) preferred over tabs. No safety wire and
  no snap rings on rotating parts. Torque tolerance ±5%. An assembly/teardown torque difference
  **>25%** flags an inadequate joint `[SP-8101 §3.1.4.3 p.76-77]`.
- Shrink tight-fit parts on, never press them. Double piloting is only for non-operating
  thermal changes (e.g. pre-start chilldown) `[SP-8101 §3.1.4.1.5 p.73]`.

## Design method

This is a criteria monograph like `[SP-8048]`. It gives **no closed-form shaft-diameter
equation**. The implied preliminary procedure, assembled from §2.1.1.3 / §3.1.1.3 / §3.2.1.2.1,
is:
1. Pick speed from pump/turbine limits. Set mechanical design speed = 1.1-1.2 × max operating
   speed (or the 3-sigma speed).
2. Set each bearing journal (= bearing bore) as large as the DN limit (≈1.0-2.0×10⁶ demonstrated,
   ≤3.0×10⁶ per `[SP-8048]`) and the seal rubbing-speed limit allow. Size the shaft between
   bearings larger still, for bending stiffness.
3. Check torsion at the journals against **2/3 × ultimate shear strength** (with ultimate SF
   ≥1.3-1.4 on limit loads). Check hollow shafts for shear buckling and splines against 65/95
   ksi.
4. Choose subcritical or supercritical operation. Place the first rotor-bending critical
   **≥ max(1.25 × N_op, 1.15 × N_overspeed)**. Any support/rigid-body criticals below running
   speed must be **≤ 0.85 × the lowest steady speed**. Carry ±5% (at best) prediction
   uncertainty.
5. Size couplings: splines 2/3-1 D long, 50% of teeth in contact. Curvic OD = (T/9.03e6)^(1/3)
   m. Bolt preload 1.5-2× separating force.

## Section map

- §1 Introduction (p.1-2): read. Failure list.
- §2.1 Shaft Design, State of the Art (p.3-18): read in full. §2.1.1.1 speed / sub- vs
  supercritical / overshoot (p.4-5); §2.1.1.2 bearing/seal location (p.5-6); **§2.1.1.3 shaft
  size, Table I, 2/3-ultimate-shear rule (p.6-7)**; §2.1.1.4 discontinuities (p.7-8); §2.1.1.5
  environment (p.8-9); **§2.1.2 materials, Table II (p.9-11)**; **§2.1.3 structural, Table III
  safety factors (p.11-13)**; §2.1.4 fits (Table IV)/clearances/bolts/locking (p.13-17); §2.1.5
  QC (p.17).
- §2.2 Shaft Dynamics (p.19-48): read (text). Whirl classes (p.19-20), Table V Yamamoto forced
  whirls (p.21), major vs secondary criticals and XLR-87 spin data (p.23-26), self-excited whirl
  (p.27-30), torsional (p.30), modelling (p.31-44), **prediction accuracy (p.45)**, Table VI
  (p.47), tuning (p.46-48), balancing (p.48-49).
- §2.3 Coupling Design (p.49-54): read. Splines p.49-50, curvic p.50-53, face p.53-54.
- §2.4 Design Confirmation Tests (p.54-59): read. Shake-vs-analysis numbers p.54.
- §3.1 Shaft Design criteria (p.60-78): read in full. **§3.1.1.1.2 design speed 1.1-1.2× (p.60)**;
  **§3.1.1.3 shaft size (p.62)**; **§3.1.3.2 safety factors (p.70)**; §3.1.3.3 analysis (p.70-71);
  §3.1.4 fits/bolts/locking (p.72-77); §3.1.5 QC (p.77-78).
- §3.2 Shaft Dynamics criteria (p.79-88): read in full. **§3.2.1.2.1 critical-speed margins
  (p.79-80)**; §3.2.1.4 torsional (p.81); §3.2.2 modelling (p.82-87); §3.2.2.3 accuracy (p.87);
  §3.2.4 balancing (p.88).
- §3.3 Coupling criteria (p.89-92): read in full. **Curvic sizing formula p.91.**
- §3.4 Test criteria (p.92-96): read.
- References (p.97-108): not read. Glossary (p.109-113): partly read (DN = bore mm × rpm, as
  elsewhere). Materials list: first page only.

## Caveats

- **No real F-1/J-2/H-1/RL10/SSME shaft diameters, torques, rpm, spans or critical speeds.**
  Real dynamics numbers are Aerojet Titan (XLR-87/91) and NERVA only. The larger-engine content
  is limited to safety factors (Table III), DN (Table I: J-1/M-1) and failure anecdotes. 1972
  vintage, so pre-SSME (no fluid-film/hydrostatic bearing flight experience, and squeeze-film
  dampers "not yet ... used successfully in rocket engine turbomachinery," p.48).
- **The 2/3-ultimate-shear rule is a fraction of a material property.** SP-8101 gives no
  4340 (or other alloy) strength values, so turning it into a replacement for
  `SHAFT_ALLOWABLE_SHEAR_PA` needs a cited ultimate-shear value from a materials source. The
  65/95 ksi spline figures are absolute, but they are the "boundary line of spline practice"
  for case-hardened ferrous splines. They are not a plain-shaft allowable.
- **The 125%/115%/85% critical-speed rules** apply to *major* (synchronous, imbalance-excited)
  criticals, split by whether the mode's potential energy is mainly rotor bending (must sit
  above running speed) or stator/bearing deformation (may sit below running speed). Applying
  them needs a mode classification. A simple Jeffcott/beam estimate in the tool gives only the
  rotor-bending one.
- Table II (4340 satisfactory in oxygen) conflicts with the §3.1.2.4 criterion (no 4340 at
  cryogenic temperature). Both are quoted above. The criterion is the monograph's
  recommendation, and the table records past practice.
- Table numbering in the text drifts (p.46 cites "Table VII" for the table printed as Table VI;
  the list of tables says VI). OCR text is noisy, so every table value here was read from a
  rendered page image.
