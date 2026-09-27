# NASA SP-8121 — Liquid Rocket Engine Turbopump Rotating-Shaft Seals

## Identity

NASA SP-8121, *Liquid Rocket Engine Turbopump Rotating-Shaft Seals*, NASA Space Vehicle
Design Criteria (Chemical Propulsion), February 1978. Author R. E. Burcham (Rocketdyne
Division, Rockwell International), edited by R. B. Keller Jr. (Lewis); reviewers P. F. Brown
(P&WA), P. S. Buckmann (Aerojet), L. P. Ludwig and J. Zuk (Lewis).
`literature/NASA SP-8121 - Liquid Rocket Engine Turbopump Rotating-Shaft Seals.pdf` (NTRS
19780022641; 168 PDF leaves, 78 MB scan). Fixed page offset: **printed page N = 0-indexed
leaf N+11** (= 1-indexed PDF page N+12), e.g. printed p.1 is leaf 12, printed p.103 is leaf
114. Confirmed from the page footers at several points. Tag: `[SP-8121]`.

**Technical note on this PDF**: unlike `[SP-8048]`, this scan **has an OCR text layer**
(`pymupdf` `page.get_text()` works). The running text is usable, with scattered dropped
letters ("eal" for "seal", etc.). The landscape tables (Table I, p.4-6) and every equation
come out of the text layer scrambled, though. Table I, equations (5) and (7)-(11), and
Figures 23-25, 43, 44 were **rendered to PNG and read by eye**. Every number in the tables
below comes from those renders, not from the text layer. One example of why: the text layer
reads the H-1 LOX-seal leakage as "10 SCFH", but the render shows 10 SCFM.

## Character

This monograph uses the same parallel §2 (State of the Art, narrative) / §3 (Design Criteria
in italics + Recommended Practices) structure as `[SP-8048]`/`[SP-8107]`/`[SP-8120]`, with
the two sections numbered to match. It is organised as three nested design tasks:
- **Seal System** (§2.1/§3.1): arrangement of seals, drains and purges. Covers pressure,
  thermal and vacuum environments, rubbing speed, cooling, drains, fluid separation, fail-safe
  provisions and purge.
- **Seal Assembly** (§2.2/§3.2): choosing the seal type against the pressure / speed /
  temperature / wear-life / leakage / misalignment envelope.
- **Seal Components** (§2.3/§3.3): materials, face-contact rubbing elements, segmented,
  hydrostatic/hydrodynamic, labyrinth, floating-ring and arch-bound elements, bellows / lip /
  elastomer / piston-ring secondaries, spring load and pressure balance.

The data base is 1960s-70s US flight and development turbopumps: Thor, Atlas, H-1, F-1, J-2,
J-2S, RL10, M-1, Titan III, NERVA/Phoebus and P&WA fluorine R&D. There is **no SSME seal
data**. SSME appears only as a 1978 "future requirement" (see Key results). The
monograph is **qualitative-to-semi-empirical**:
- The real quantitative content is Table I (46 real seals with diameter, pressure, speed,
  load, PV, balance ratio, leakage and engine).
- The per-fluid 3-hr-life limit curves (Figs 57-59) are also quantitative.
- So is a set of face-seal leakage equations (eqs. 5-11) with a recommended empirical gap.
- For labyrinths it gives flow-coefficient/leakage-function charts (Figs 43-44) plus
  geometry rules, **but no closed-form leakage equation in the text**. The formula is
  delegated to refs 54-65.

This is the **first seal source in `claude_lit/`**. `engine_designer/` currently has no
seal model at all. The only seal-adjacent constants are `turbopump_sizing.py`'s
`SHAFT_SPAN_FACTOR`/`MIN_BODY_OD_M`, which lump "bearings/seals" together.

## This note's extraction scope

**Read** (text layer and/or rendered):
- Introduction (p.1-2).
- §2 intro and **Table I (p.3-6, rendered)**.
- **§2.1 Seal System complete (p.7-15, incl. Figs 1-10 captions, Figs 4-6 rendered)**.
- **§2.2.1-2.2.5 (p.16-17, 32-48)**: pressure, temperature, speed, wear life, leakage incl.
  eqs. (1)-(11) rendered.
- **Table II (p.18-21)**, advantages/disadvantages of each seal type.
- §2.2.6-2.2.6.3 (p.48-49).
- **§2.3.1 Materials (p.55-60, incl. Table III)**.
- §2.3.2.1 face width (p.66-67).
- **§2.3.5 Clearance elements (labyrinth, floating-ring, arch-bound; p.78-89, Figs 43-45
  rendered)**.
- §2.3.7 Spring load (p.98-100).
- §2.3.8 Pressure balance (p.100-101).
- **All of §3.1 and §3.2.1-3.2.6 (p.103-112, incl. Figs 57-59 limit values)**.
- §3.3.4-3.3.5 (p.123-128).
- §3.3.6.4, §3.3.7, §3.3.8 incl. Table IV (p.131-132).
- References 1-28 (p.145-146).

**Not read**:
- Most of §2.3.2 (insert retention/distortion/lapped joints/spray coatings, p.67-74).
- §2.3.3 segmented shaft seals (p.74-75).
- §2.3.4 hydrostatic/hydrodynamic detail (p.75-78).
- §2.3.6 bellows/lip/elastomer/piston-ring secondaries (p.89-98).
- §2.2.7-2.2.9 vibration/contamination/mounting (p.50-55).
- The matching §3.2.7-3.3.3 and §3.3.6.1-3.3.6.3 criteria.
- Figs 26-29 (bar charts, which the text summarises), Figs 30-35 (property charts).
- Appendices A/B, references 29-76.

## Seal-type selection table

From §3.2.1 Recommended Practices `[SP-8121 §3.2.1 p.106]`, with temperature limits from
`[SP-8121 §3.2.2 p.108]` and pros and cons from `[SP-8121 Table II p.18-21]`.

| Seal type | Use it for | Temp. limits, °F | Key drawback |
|---|---|---|---|
| Face-contact, welded **metal bellows** | Cryogenic or reactive liquids up to **~500 psig**; the most common cryogenic seal | -423 to 1500 | Balance ratio drifts with pressure (bellows effective diameter changes); fatigue under oscillating pressure |
| Face-contact, **plastic lip** (Kel-F/Mylar) | Cryogenic liquids, vibration damping | -320 to 200 | Lower reliability than bellows |
| Face-contact, **metal piston ring** | High-pressure (**>500 psig**) cryogenic/reactive liquids where face-load control is critical | -423 to 1500 | High secondary leakage; hang-up; fretting |
| Face-contact, **elastomer** (O-ring/V-packing) | Lubricated fluids (RP-1, oil) up to **~1000 psig** | -65 to 500 | Unusable cryogenically; age-limited (except Viton A) |
| Circumferential shaft-riding **segmented carbon** | **Low-pressure (<100 psig)** purged intermediate or hot-gas seals | -423 to 1000 | Unbalanced radial pressure load; liquid leakage high (segments lift off) |
| Circumferential **floating-ring** controlled-gap | **High-pressure (>100 psig)** hot-gas or purge-gas seals, or **>4 hr** life, where extra leakage is acceptable | -423 to 1500 | Leaks more than segmented; gap sensitive to ring/shaft ΔT; risk of seizure |
| Circumferential **labyrinth** (clearance / wear-in) | High pressure and long life where reliability/economy dominate and extra leakage is acceptable | -423 to 1800 | Highest leakage |
| Face **hydrostatic / hydrodynamic / hybrid** | Combined high pressure + high speed + long life at minimum leakage (the 1978 "future" answer; limited cryogenic experience) | n/a | Distortion-sensitive; marginal stability in cryogens |

Supporting rules:
- Rubbing face-contact seals work at **up to ~500 psi or ~500 ft/s**, but wear life is
  limited to **~4 hr** `[SP-8121 §2 p.7, §2.2 p.16]`.
- **Above ~500 ft/s surface speed**, use clearance seals (floating-ring, labyrinth) or
  fluid-film seals `[SP-8121 §3.2.3 p.108]`.
- **Above ~4 hr wear life**, use clearance or fluid-film seals unless PV is low and
  lubrication is good `[SP-8121 §3.2.4 p.111]`.

## Real engine seal data (Table I, rendered)

`[SP-8121 Table I p.4-6]`. Table columns:
- Materials: nosepiece / mating ring / secondary or bellows / housing.
- Diameter, fluid pressure, shaft speed, rubbing speed.
- Spring load, total load, unit load, PV.
- Balance ratio (= effective closing area ÷ sealing-dam area).
- Tests: count, hours, wear life.
- Dynamic leakage, "measured or estimated maximum". Liquid leakage in SCFM is the
  gas-equivalent volume; §2.1.6 converts liquid leakage to gas volume for drain sizing.

The selection below keeps the flight engines and the most instructive R&D rows.

| Fluid | Seal type | Engine | Dia, in | P, psig | rpm | V, ft/s | Unit load, psi | PV ×10³ | Bal. | Wear life, hr | Dyn. leakage |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LOX | face, welded bellows (P692 / Cr-on-4130) | Thor | 2.630 | 225 | 6750 | 77 | 158 | 12.2 | 0.97 | 3 | 10 SCFM |
| LOX | face, welded bellows | H-1 | 2.630 | 200 | 6800 | 78 | 176 | 13.7 | 0.7 | 3 | 10 SCFM |
| LOX | face, welded bellows (P5N / Cr-on-Inco X, Inco 750 bellows) | J-2 | 2.974 | 200 | 8650 | 112 | 210 | 23.5 | 0.85 | 2 | 15 SCFM |
| LOX | face, welded bellows | J-2S | 2.935 | 200 | 9000 | 115 | 210 | 24 | 0.85 | 2 | 15 SCFM |
| LOX | face, welded bellows (LW-5 on Inco X) | M-1 | 6.902 | 450 | 4000 | 120 | 196 | 23.5 | 0.92 | 1.7 | 2.3 SCFM |
| LOX | face, welded bellows | RL10 | 1.70 | 400 | 12300 | 92 | 41 | 3.8 | 0.65 | NA | NA |
| LOX | face, **Mylar lip** secondary | **F-1** | 6.463 | 140 | 6000 | 170 | 51 | 8.7 | 0.7 | 3 | **25 SCFM** |
| LOX | face, Kel-F lip | Atlas | 2.630 | 250 | 10000 | 115 | 137 | 15.8 | 0.85 | 3 | 10 SCFM |
| LOX | face **hybrid** (annular-grooved) welded bellows | ADP (R&D) | 2.65 | 50 | 25000 | 290 | NA | NA | 0.6 | **10** | 15 SCFM |
| LOX | shaft-riding segmented carbon | M-1 | 4.33 | 385 | 6000 | 113 | NA | NA | NA | NA | **3.5 GPM** (liquid) |
| LH2 | face, welded bellows (P5N / Cr-on-Inco X) | J-2 | 2.950 | 200 | 28000 | 360 | 89 | 32 | 0.7 | 2 | **0.01 lbm/s** |
| LH2 | face, welded bellows | J-2S | 3.515 | 350 | 28000 | 430 | 101 | 43.5 | 0.7 | 2 | 0.02 lbm/s |
| LH2 | face, welded bellows | Phoebus | 2.531 | 150 | 34000 | 375 | 31 | 11.6 | 0.7 | 4 | 0.006 lbm/s |
| LH2 | face, metal piston ring | RL10 | 1.59-2.09 | 85-500 | 30800 | 214-280 | 50-76 | 12-16 | 0.55-0.75 | NA | NA |
| LH2 | shaft-clearance **arch-bound** segmented carbon | M-1 | 5.24 | 210 | 15500 | 385 | NA | NA | NA | NA | **50 GPM** (liquid) |
| LH2 | shaft-riding segmented carbon | NERVA | 3.0-3.5 | 150-600 | 22000-24000 | 312-367 | NA | NA | NA | 1 / 10+ | NA |
| GH2 -400°F | face, welded bellows | J-2 | 2.950 | 50 | 28400 | 434 | 29 | 12.6 | 0.7 | 2 | 3 SCFM |
| Hot gas H2+H2O 1000°F | shaft-riding segmented carbon | **J-2** (turbine) | 3.768 | 100 | 28400 | 460 | 62 | 28.6 | 1.5 | 2 | **20 SCFM** |
| Hot gas H2+H2O 1000°F | face, welded bellows | J-2 (LOX-pump turbine side) | 3.339 | 75 | 9000 | 130 | 40 | 5.2 | 0.8 | 3 | 3 SCFM |
| Hot gas 500°F GN2 | face, welded bellows | M-1 | 4.53 | 130 | 6000 | 120 | 38.6 | 4.6 | 0.95 | NA | NA |
| Hot gas A-50+N2O4 | face, welded bellows | Titan III | 2.668 | 95 | 25000 | 277 | 40 | 11 | 0.65 | 0.9 | NA |
| RP-1 | face, V-packing (Buna-N) | Atlas / Thor | 2.364 / 3.177 | 250 / 200 | 10000 / 6500 | 107 / 90 | 103 / 99 | 10.6 / 8.9 | 0.85 | 4+ | 5 cc/hr |
| RP-1 | face, welded bellows (AM-350) | H-1 | 3.174 | 200 | 7000 | 97 | 117 | 11.4 | 0.97 | 4+ | 2 cc/hr |
| RP-1 | face, O-ring (Viton A) | **F-1** | 6.497 | 300 | 6500 | 181 | 126 | 22.9 | 0.8 | 3 | **100 cc/hr** |
| RP-1 / hot gas 800°F | face, welded bellows | F-1 | 10.142 | 120 | 6500 | 280 | 81 | 22.8 | 0.65 | NA | NA |
| Hot gas LOX+RP-1 1000°F | shaft-riding segmented carbon | F-1 | 9.500 | 50 | 6500 | 270 | — | — | — | 4+ | NA |
| Hot gas LOX+RP-1 | shaft-riding segmented carbon | Atlas | 2.000 | 125 | 40000 | 350 | — | — | — | 4+ | NA |
| Hot gas LOX+RP-1 | shaft-riding **floating ring** (P33 carbon / WC-on-4340) | **H-1** | 3.000 | 160 | 29000 | 380 | — | — | — | 4+ | NA |

The table also covers N2O4 and A-50 (Titan III, 50 psig, face bellows), FLOX, and liquid
fluorine (0.62-1.82 in., up to 75,000 rpm R&D). Those rows are omitted here as outside the
tool's propellant set.

## Key results

**1. Seal pressure / speed envelope and the SSME gap** `[SP-8121 §2 p.7, §2.2.1 p.16-17,
§2.2.3 p.33]`:
- Primary shaft-seal pressure is normally held to **<500 psig** so that minimum-leakage face
  seals can be used. The maximum for current face-contact seals is 500 psig, and **most run
  at ~200 psig**.
- **Up to ~1000 psig** is feasible for face seals only at low speed, short life and small
  size.
- Floating-ring seals run **>1000 psig**, because their contact load barely rises with
  pressure.
- Segmented carbon seals are limited to **~100 psig** as dry-gas seals.
- Rubbing speeds reach **~450 ft/s** on LH2/GH2 and hot-gas seals. **LOX and RP-1 seals
  usually run <200 ft/s.**
- The 1978 **SSME** requirement was LOX to **650 psia**, hot (900°F) gas to **4000 psia**,
  **400 ft/s**, and **10 hr** wear life. The monograph says no existing design met all of
  these at once, and it pointed to hydrostatic/hydrodynamic face seals with **0.0001-0.0004
  in.** film gaps.

**2. Reducing high pump pressure before the seal** `[SP-8121 §2.1.1 p.12, §3.1.1 p.103]`:
- Pressures **>500 psig** are dropped with an upstream labyrinth or circumferential
  clearance seal plus a **low-pressure return bleed recirculating to the pump inlet**
  (Fig 10).
- The downstream side of the primary seal is held at a set pressure. Options are a
  drain-line relief valve (the J-2 LH2 pump primary-seal drain uses a **40 psid relief
  valve**, Fig 4, rendered) or an inert purge in the drain cavity.
- Upstream labyrinths also damp impeller discharge pressure pulses that fatigue bellows and
  lips.
- This is the seal-system counterpart of a balance-piston / impeller-bleed recirculation
  loss. It is a real pump-internal recirculation flow, separate from the (tiny) primary-seal
  leakage.

**3. Inter-propellant seal configurations** (§2.1.7 Fluid Separation) `[SP-8121 §2.1.7
p.14-15, §3.1.7-3.1.8 p.104-105, Figs 5-10 p.9-11]`.

Incompatible fluids on one shaft are separated by three things:
1. **Two face-contact primary seals**, which keep leakage low.
2. **Separate drains for each propellant**, venting to safe disposal.
3. An **inert-gas-purged intermediate seal** between the two drain cavities. This is either
   a purged double circumferential seal (Fig 6), two intermediate face seals with the purge
   between them (Fig 10a), or two intermediate ring seals (Fig 10b).

The purge pressure must exceed the **maximum drain back-pressure** so that it forms a
pressure barrier. A system that needs the purge to be fail-safe must have a **fail-proof
purge supply** `[SP-8121 §3.1.8 p.105]`. A rotating slinger, or shoulders on the
intermediate mating ring, keeps high-velocity leakage off the intermediate seal. Real
layouts:

| Figure | Engine / pump | Arrangement | Purge |
|---|---|---|---|
| Fig 5 | H-1 turbopump, LOX vs lube oil | 3 seals: 2 face seals + a labyrinth intermediate | **GN2**. The text says it "may not be effective in the event of a seal failure" |
| Fig 6 | F-1 turbopump, LOX vs RP-1 | 4 seals: 2 face seals + a double circumferential intermediate + slinger; LOX cavity drain in 3 places | **GN2** |
| Fig 7 | J-2 LOX turbopump, LOX vs H2-rich turbine gas | 4 seals: 2 face seals + purged double circumferential | Intermediate-seal purge (gas not named in the text) |
| Fig 8 | M-1 LOX turbopump | 4 face seals stacked radially | Minimum axial space |
| Fig 9 | P&WA R&D LF2 pump | Compact 4-seal | n/a |
| Fig 10a | Generic high pressure | 6 seals: 2 clearance pressure-breakdown seals, 2 primary face seals, 2 intermediate face seals with **helium purge** between | Helium |
| Fig 10b | P&WA FLOX/methane and H2/F2 studies, refs 3-5 | 6 seals: 2 face seals + 2 labyrinths + 2 ring seals | Ring seals **"center pressurized with helium"** as a helium dam for ground test |

Two practical cautions:
- Avoid two seals rubbing on one mating ring, because it overheats and distorts. Use
  separate mating rings `[SP-8121 §3.1.5 p.104]`.
- Dry-running intermediate seals should be circumferential seals cooled by the inert purge.

**Purge flow magnitudes: NOT given.** A full-text search for helium/purge/flowrate turns up
only qualitative purge requirements `[SP-8121 §2.1.9 p.15, §3.1.9 p.105]`:
- Cryogenic seal cavities are purged with GN2 or GHe before chilldown, to remove air and
  moisture.
- **Hydrogen systems use GHe only.** GN2 would freeze at LH2 temperature.
- Cavities exposed to H2/O2 turbine gas are purged of moisture, which would otherwise freeze
  on the next chilldown.
- Each purged cavity needs an inlet and an outlet port. The purge stays on after the test
  until the hardware is back at ambient.

**No lb/s or SCFM purge rate appears anywhere in the sections read.** An inter-propellant
helium purge rate for engine_designer will need a different source.

**4. Measured seal leakage is tiny relative to pump flow** `[SP-8121 Table I p.4-6]`.
Face-contact primary seals leak:
- **LOX: 2-25 SCFM** gas-equivalent. F-1 is the largest at 25 SCFM; J-2 is 15.
- **LH2: 0.006-0.02 lbm/s.** J-2 is 0.01, J-2S 0.02.
- **RP-1: 2-100 cc/hr.** F-1 is 100 cc/hr.
- **Hot-gas segmented carbon (J-2 turbine): 20 SCFM.**

Circumferential rubbing/clearance seals on **liquid** leak orders of magnitude more: the M-1
LOX segmented carbon seal leaks **3.5 GPM**, and the M-1 LH2 arch-bound seal **50 GPM**.

Derived fractions of pump flow (**not in the source**; the pump flows are approximate public
figures brought in only for scale, so trust the order of magnitude, not the digits):

| Seal | Leakage | Approx. pump flow | Fraction |
|---|---|---|---|
| J-2 LH2 | 0.01 lbm/s | ~80 lbm/s | **~1×10⁻⁴** |
| J-2 LOX | 15 SCFM of O2 ≈ 0.02 lbm/s (taking standard O2 density ≈ 0.084 lbm/ft³) | ~450 lbm/s | **~5×10⁻⁵** |
| F-1 LOX | 25 SCFM ≈ 0.035 lbm/s | ~3,900 lbm/s | **~1×10⁻⁵** |
| M-1 LH2 arch-bound | 50 GPM ≈ 0.5 lbm/s | several hundred lbm/s | **~10⁻³** |

So **primary-seal leakage as a flow/Isp loss is negligible (≤10⁻³)**. What matters for pump
efficiency is the pressure-breakdown recirculation bleed of item 2, and the wear-ring /
balance-piston leakage, which is `[SP-8109]`'s territory, not the shaft seal.

**5. Relative leakage of the clearance seal types** `[SP-8121 §2.3.5 p.78, §2.3.5.1.1
p.81, p.83]`:
- A labyrinth leaks about **10× an arch-bound segmented seal** and about **5× a floating-ring
  seal**.
- The floating ring is "the best compromise between sealing effectiveness and reliability
  for high-pressure, high-speed, long-life applications".
- A **step or staggered labyrinth leaks ~50% of a straight labyrinth.**
- Tooth sharpness (tip thickness / clearance) changes leakage by up to 20%.
- A 40° tooth angle of attack is optimal.
- Leakage is **proportional to operating clearance** (at constant flow coefficient) and
  **roughly proportional to diameter²**. So use the smallest diameter and the tightest
  clearance.

**6. PV / FV / PfV limits for face-contact seals, 3-hr life** `[SP-8121 §3.2.1 p.105-106,
§3.2.3 p.108, Figs 57-59 p.107-110]`. Each limit is a constant-product hyperbola fitted to
the successful current practice:

| Fluid | PfV limit (fluid psig × ft/s), Fig 57 | FV limit (lbf/in × ft/s), Fig 58 | PV limit (face psi × ft/s), Fig 59 |
|---|---|---|---|
| LOX | 60,000 | 2,000 | 25,000 |
| LH2 | 200,000 | 4,000 | 50,000 |
| GH2 | 50,000 | 1,500 | 20,000 |
| LF2 | 50,000 | 1,000 | 20,000 |
| RP-1 | 80,000 | 2,500 | 25,000 |
| Hot gas H2+H2O | 20,000 | 800 | 10,000 |

Worked example: a LOX face seal at 300 psig can rub at up to ~200 ft/s, and an LH2 face seal
at 400 psig at up to ~500 ft/s. Longer life requires a more conservative factor or a
non-contact seal.

Heat generation `[SP-8121 §2.2.3 eqs (1)-(2) p.35]`:
- q = F·V·f/J, or per unit area q' = P·V·f/J, with J = 777.6 ft·lbf/Btu.
- The friction coefficient f is **~0.05-0.4** for common seal materials.
- The interface pressure profile carries **0.2-0.8 of ΔP**.
- Rubbing faces have measured **>1000°F on LOX seals in -297°F fluid** `[SP-8121 §1 p.1]`.

**7. Face-seal leakage equations** `[SP-8121 §2.2.5 p.44-48, eqs (3)-(11), rendered]`. Units
are inch-lbm-psi-sec throughout. Symbols:
- h = effective leakage gap.
- r1, r2 = face inner / outer radius.
- b̄ = mean circumferential length; L = radial face length.
- μa = absolute viscosity; ρm = ρ/g.

The equations:
- **Regime criteria.** Molecular λ/h ≥ 1. Transition λ/h = 1 to 0.01. Laminar λ/h ≤ 0.01
  with leakage Re ≤ 1000 and rotational Re ≤ 2000. Turbulent otherwise.
- **Reynolds numbers.** Leakage Re = ẇ/(π d μ) (eq. 3). Rotational Re = r̄ωh/ν (eq. 4).
  Iterate, since you have to assume a regime first.
- **Molecular (eq. 5).** ẇ = 0.532 λ P̄ (P2−P1) b̄ h² / (R T μa L).
- **Laminar compressible (eqs 6b/7).** ẇ = b̄ h³ (P2²−P1²) / (24 R T μa L). The flow chokes at
  the exit above a pressure ratio of ~4:1 (Δr/h > 100).
- **Laminar liquid, no inertia (eq. 8).** ẇ = ρ π h³ (P2−P1) / (6 μa ln(r2/r1)). Covers
  cryogens at ~200 psi.
- **Laminar liquid with inertia (eq. 9).** ẇ = ρπh³/(6μa ln(r2/r1)) · [Pr1 − Pr2 + (3/20) ρm
  ω² (r2²−r1²)]. The centrifugal term matters for LOX at low pressure and high speed, not
  for LH2.
- **Turbulent liquid, no inertia (eq. 10).** ẇ = 26.8 g (h¹²/μa)^(1/7) [ρm (Pr2−Pr1) /
  (r1^(-3/4) − r2^(-3/4))]^(4/7). The text says most high-pressure cryogenic seals are in
  this regime.
- **Turbulent with rotation (eq. 11).** ẇ = 161 ρ (h⁹/(ρm³ μa ω³))^(1/4) [ (Pr1 − Pr2 +
  0.512 ρm((r2ω/2)² − (r1ω/2)²)) / (1.333 (r1^(3/4) − r2^(3/4))) ].

**Empirical closure (the load-bearing number)** `[SP-8121 §2.2.5 p.48, §3.2.5 p.111]`:
- **Dynamic leakage:** use eq. 9 or eq. 10 (whichever the Re dictates) with liquid inlet
  and an effective gap **h ≈ 200 µin**. This reproduces most measured values.
- h ≈ 100 µin applies if the design compensates for thermal distortion; up to 400 µin if
  thermal gradients are extreme.
- **Static leakage:** h ≈ 50 µin (25-50 µin for solid carbon rings, 50-100 µin for insert
  designs).
- Chilldown to -320°F can raise static leakage by up to **500%**.
- For two-phase flow, bracket the leakage by computing it for both liquid and gas.

**8. Labyrinth design rules** `[SP-8121 §2.3.5.1 p.79-86, §3.3.5.1 p.125-126, Figs 43-45
rendered]`.

Flow coefficient (Fig 43; water, 9.0-in. dia, 3600 rpm / 150 ft/s, radial clearance h
0.019-0.033 in.):
- φ = Q/(A√(2gΔH)), plotted against Re = Q·d/(A·ν) from 1.5×10⁴ to 1.2×10⁵.
- **Step labyrinths** (curves 1-3): **φ ≈ 0.25-0.35**.
- **Straight/grooved labyrinths** (curves 4-10): **φ ≈ 0.4-0.7**.
- φ rises with Re.
- Incompressible labyrinth data are scarce. Test or extrapolate.

Throttling leakage function (Fig 44, adapted from ref. 56, a Martin/Egli-type chart):
- Printed as ψ = √[(1−(P1/P2)²)/(n_t + ln(P1/P2))], with P1 downstream and P2 upstream.
- **The printed sign of the ln term is as transcribed and looks inconsistent with the
  curves.** Martin's classical form is n_t − ln(P1/P2). Read values off the curves, not the
  label.
- Read-off at pressure ratio ≲0.5: n_t = 1 → ~0.9, 2 → ~0.66, 3 → ~0.57, 4 → ~0.49,
  8 → ~0.36, 16 → ~0.27, 32 → ~0.21.
- All curves fall to 0 at P1/P2 = 1.
- There are diminishing returns in tooth count.

**The monograph gives no explicit ẇ = f(φ, ψ, A, P, ρ) equation.** The implied assembly is
the classical ẇ ≈ φ·A·ψ·√(P2·ρ2·g), which is an inference, not a quote.

Geometry rules:
- Teeth sharp: **0.005-0.015 in. tip radius**.
- **Optimum straight-labyrinth pitch ≈ 0.1 in. per 0.01 in. diametral clearance** (Fig 45:
  ~0.1 in. pitch at 0.010 in. rising to ~0.27 in. at 0.040 in.).
- **Cavity depth ≈ tooth pitch.**
- Use step or staggered teeth where possible.

Wear-in labyrinths:
- In non-oxidizing fluids, use **Inconel 600 / Hastelloy C / stainless honeycomb, foil
  0.002-0.005 in., 1/16-in. cell, depth 1-2× the width**, brazed to a support ring.
- **In LOX, use Kel-F** locked into a metal housing, with a 0.5-1.0 in. span between
  retention locks (J-2 and F-1 practice). Kel-F contracts about 4× as much as steel.

Erosion resistance rises roughly with **hardness^2.5** and linearly with strength. Use tool
steel, Stellite or maraging steel. Avoid Al, Monel, brass, bronze and plastic where erosion
is a risk.

**9. Floating-ring and arch-bound rules** `[SP-8121 §2.3.5.2-2.3.5.3 p.87-89, §3.3.5.2-3.3.5.3
p.126-128]`.

Floating-ring construction:
- A **carbon inner ring** shrink-fitted in a **steel outer ring**. The outer ring's thermal
  expansion is matched to the shaft so the gap stays constant.
- The interference fit's unit load must exceed the maximum fluid pressure.
- **Operating diametral clearance: 0.0005-0.001 in. per in. of diameter.**
- The shaft is hard-plated (hard chrome, chromium carbide, tungsten carbide).
- **Two or more machined anti-rotation tangs.** On the H-1 turbine, a ring that could rotate
  seized and failed under centrifugal load; tangs fixed it.
- Axial pressure load is partly balanced; low-pressure seals use a wave spring.

Arch-bound segments are sized **~0.001 in. smaller than the shaft** at operating conditions,
so that they wear in to a solid ring.

**10. Face-seal hardware numbers**:
- **Carbon nose height ≈ 0.050 in.** At a maximum wear rate of 0.020 in/hr this gives 2.5 hr.
  J-2 LOX/LH2 carbon faces wore **0.005-0.010 in/hr**, ±100% scatter `[SP-8121 §2.2.4 p.36]`.
- Operational engine seal life was ~2 hr, against 10 hr for SSME and 500-10,000 hr in other
  industries.
- A LOX hybrid grooved face seal demonstrated **>10 hr** wear life (ADP, Table I).
- Face width runs from **0.040 in. on a 0.615-in. seal to 0.160 in. on a 10.142-in. seal**,
  with ID/OD 0.87-0.97 `[SP-8121 §2.3.2.1 p.66]`.
- Face-seal axial travel is **±0.015 in.** (1-in. dia), **±0.050 in.** (3-6 in.), **±0.100
  in.** (10 in.) `[SP-8121 §2.2.6.1 p.49]`.
- Spring load is typically **~2 lbf/in. of face circumference**. The practical minimum is 0.3
  lbf/in. Up to 10 lbf/in. was used on the H-1 LOX and F-1 RP-1 seals, but >4 lbf/in. only
  where the fluid can absorb the friction heat `[SP-8121 §2.3.7 p.100]`.
- Recommended spring load by fluid `[SP-8121 §3.3.7 p.131-132]`, lbf/in.: LOX 2-4, LH2 1-2,
  GH2 1-2, hot gas 1-2, RP-1 1-4, LF2 2-3.
- Seals with **ΔP >100 psi must be pressure-balanced**. Recommended balance ratios
  `[SP-8121 §3.3.8 Table IV p.132]`:
  - high-P incompressible: 0.55-0.6
  - low-P incompressible: 0.6-0.7
  - high-P cryogenic: 0.65-0.7
  - low-P cryogenic: 0.8-0.9
  - choked compressible: 0.67-0.75
  - subsonic compressible: 0.6-0.7
- Interface pressure-profile factor `[SP-8121 §2.3.8 p.101]`: ~0.5 for parallel faces
  (0.2 divergent, 0.8 convergent); 0.50-0.67 for laminar compressible flow.
- Seal power loss "can become a significant portion of the total turbopump power" in small
  turbomachinery `[SP-8121 §2.3.7 p.99]`. This is qualitative only; no number is given.

**11. Materials** `[SP-8121 §2.3.1 p.55-60, Table III p.56]`:
- **Carbon (graphite) noses against a hard-chrome-plated or LW-5 (tungsten/chromium carbide)
  coated mating ring** are the universal face pair for LOX, LH2, RP-1 and hot gas. Grades:
  P692/P5N/P5AG in LOX, P5N/P03N in LH2, G39/CCA-72 in RP-1, G84/P2003/P33 in hot gas.
  Carbon has never ignited in LOX in these grades. In a 70 ft·lbf LOX impact test it
  pulverises without reacting.
- **Metal-to-metal rubbing in LOX/LF2 is avoided**: LOX pumps have exploded from it.
- Bellows and housings: **Inconel 718 / X-750 / AM-350 / 321 / 347**. The J-2 moved to
  Inconel 600/X-750/718 because 300/400-series stainless pitted in H2+H2O turbine gas.
- **Martensitic steels (17-7PH, AM-350, 4130, 4340) are not used as flexing elements at
  cryogenic temperature.** AM-350 bellows appear in the warmer RP-1, hot-gas and storable
  seals.
- Kel-F / Teflon / Mylar are LOX-compatible to ~1000 psi. Their compatibility is marginal at
  5000 psi. Service range is -320 to 600°F.
- Elastomers (Viton A, Buna-N) only from -65 to 500°F. **Viton A is the RP-1 / lube-oil
  standard.**
- Epon 901/B3 is the only epoxy used to bond carbon inserts in LOX (J-2).
- Inconel X-750/718 are acceptable in H2 below about -200°F. Above that, use stable
  austenitics (310/316/347/A286).

## Design method

This is a criteria/practices monograph. The sequence it prescribes is:

1. **Lay out the seal system at preliminary turbopump layout.** Do not add it afterwards.
   Settle drains, purges and pressure-breakdown bleeds.
2. **Pick the seal type** from the fluid, pressure, speed, temperature and life, using the
   §3.2.1 rules and the Fig 57-59 limits.
3. **Size the components**: face width, nose height, spring load, balance ratio, labyrinth
   pitch/teeth/clearance, floating-ring clearance.
4. **Estimate leakage** with eqs. 8-11 and h ≈ 200 µin (dynamic) or 50 µin (static).
5. **Size the drains** for the leakage of a single failed seal. For cryogens, convert the
   liquid leakage to gas volume, which is conservative.

For engine_designer the usable quantitative core is:
- **(a)** the seal-type selection thresholds (500 psig / 100 psig / 500 ft/s / 4 hr);
- **(b)** the PfV/PV/FV limit table as a warn-only plausibility check on a face seal sized
  at shaft diameter × rpm;
- **(c)** eqs. 8/10 with h = 200 µin for primary-seal leakage;
- **(d)** Figs 43/44 plus clearance ∝ leakage for labyrinth pressure-breakdown flows;
- **(e)** Table I real diameters, speeds and leakages as spot-check anchors (J-2, F-1, H-1).

Seal hardware for the 3D exterior is mostly internal to the pump housing. The externally
visible parts are the **drain lines, one per propellant, plus the intermediate-seal purge
inlet and outlet ports** (Figs 5-7, 10).

## Section map

- Front matter, Contents (p.v-vii), figure/table lists (p.viii-xi): read.
- §1 Introduction (p.1-2): read.
- §2 State of the Art intro + **Table I (p.3-6)**: read / rendered.
- §2.1 Seal System (p.7-15): pressure, thermal, vacuum, rubbing speed, cooling/lubrication,
  leakage drains, **fluid separation**, fail-safe, **purge requirements**. All read; Figs 4-6
  rendered.
- §2.2 Seal Assembly (p.16-55):
  - read: §2.2.1 Pressure (p.16-17 + Fig 26 p.31); **Table II (p.18-21)**; §2.2.2
    Temperature, §2.2.3 Speed incl. eqs 1-2 (p.32-35); §2.2.4 Wear Life (p.36-38); **§2.2.5
    Leakage incl. eqs 3-11 (p.38-48)**; §2.2.6-2.2.6.3 (p.48-49).
  - not read: Figs 11-22 (p.22-29); §2.2.7-2.2.9 (p.50-55).
- §2.3 Seal Components (p.55-102):
  - read: **§2.3.1 Materials + Table III (p.55-60)**; §2.3.2.1 face width (p.66-67); **§2.3.5
    Clearance elements (p.78-89)**; §2.3.7 Spring load (p.98-100); §2.3.8 Pressure balance
    (p.100-101).
  - not read: §2.3.1.5 onward past p.60; the rest of §2.3.2; §2.3.3; §2.3.4 (except §2.3.4.4
    Hybrid, p.78); §2.3.6 secondaries (p.89-98).
- §3 Design Criteria (p.103-132):
  - read: **§3.1 all (p.103-105)**; **§3.2.1-3.2.6 incl. Figs 57-59 (p.105-112)**; §3.3.4-3.3.5
    (p.123-128); §3.3.6.1 (p.128); §3.3.6.4-3.3.8 + Table IV (p.131-132).
  - not read: §3.2.7-3.3.3, §3.3.6.2-3.3.6.3.
- Appendix A (SI conversion, p.133), Appendix B Glossary (p.135-144): not read.
- References (p.145-150): refs 1-28 read (p.145-146).

## Caveats

- **No purge-flow numbers.** The monograph says what the inter-propellant helium/GN2 purge
  must do: exceed the drain back-pressure, be fail-proof, flush air and moisture before
  chilldown. It never says how much gas that takes. Any helium-purge mdot in engine_designer
  would be an unsourced Tier-3 estimate until another source (engine manuals, the SSME HPOTP
  literature) is found.
- **Leakage units are mixed.** Table I leakages mix SCFM (gas-equivalent of liquid leakage,
  standard conditions not defined in the text), lbm/s, GPM and cc/hr. The "fraction of pump
  flow" numbers above use approximate pump flows from outside this source and an assumed
  standard O2 density. They are order-of-magnitude only.
- **1978 vintage, pre-SSME data base.** The largest pressures in Table I are 700 psig (NERVA
  GH2 segmented carbon) and 600 psig (NERVA LH2, LF2 R&D), and the fastest rubbing speed is
  460 ft/s. Staged-combustion inter-propellant
  seals (SSME HPOTP at ~4000 psia hot gas) are explicitly beyond the state of the art
  described. Extrapolating these limits to ORSC/FFSC pumps is out of scope.
- **Limit curves are success envelopes, not failure data.** Figs 57-59 are "established by
  the relative success of the current applications", at ~3 hr wear life and with Table III
  materials. Trust their direction far more than the exact constants.
- **Leakage equations need h**, and h is empirical: 200 µin dynamic, with 100-400 µin
  plausible. Leakage scales as h³ (laminar) or h^(12/7) (turbulent), so the prediction is
  only good to within a factor of several.
- **Fig 44's printed ψ formula has a suspicious sign.** See Key results item 8. Use the
  plotted curves.
- **Table I rows were transcribed by eye** from 200-dpi renders of a landscape table. Values
  were checked against the (scrambled) text layer where it was legible. The H-1 LOX leakage
  mismatch between text layer and render (SCFH vs SCFM) was resolved in favour of the render.
- Roughly 40% of the monograph (secondary elements, hydrostatic detail, mounting, vibration)
  was not read. Those sections are detail-design content unlikely to matter for
  engine_designer's level of fidelity.
