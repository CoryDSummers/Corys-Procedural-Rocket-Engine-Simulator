# 06 — Cooling and wall heat transfer

## Scope

Gas-side heat transfer to the chamber/nozzle wall, coolant-side heat pickup, and the
cooling methods (regenerative, film, transpiration, ablative, radiation). **Stale-note
correction (2026-09-14): as of Phase 7, `cooling.py` HAS a real Bartz-gas-side h_g +
computed hot-gas-wall-temperature + radiation-equilibrium + regen-Isp-credit model with a
per-propellant-class-calibrated absolute wall-heat-flux profile — this is no longer "the
tool's biggest modelling gap."** This file remains the correlation/typical-value reference
for that code and for anything not yet covered (real coolant-channel/boundary-layer CFD,
which the tool still doesn't attempt). **Split 2026-09-24** (this file exceeded the 40 KB
lookup-budget cap): cooling-method feasibility/construction-selection criteria, RP-1
coking/corrosion/coolant-property chemistry, film cooling, and the coolant-side (h_c)
correlation catalog now live in `topics/06b-cooling-methods-and-chemistry.md` — this file
keeps the core Bartz/Dittus-Boelter/radiation-cooling relations, the tube-wall structural-
design equations, heat-flux magnitudes, and the Bartz-calibration-error corroboration.

## Key relations

**Gas-side heat flux** `[Huzel eq. 4-10 p.100]`:

    q = h_g · (T_aw − T_wg)

- `T_aw` (adiabatic / recovery wall temperature) = `Tc · r`, where **r = turbulent boundary-
  layer recovery factor, 0.90–0.98** `[Huzel §4.4 p.100]`. `[TN-Dump App. B]` selected
  **0.88** ("δ increases with Reynolds number to ~0.90 in turbulent flow").
- `T_wg` = hot-gas-side local wall temperature.

**Gas-side coefficient — Bartz** `[Huzel eq. 4-13 p.100]`:

    h_g = { (0.026 / Dt^0.2) · (μ^0.2·Cp / Pr^0.6) · ((Pc)ns·g / c*)^0.8 · (Dt/R)^0.1 }
          · (At / A)^0.9 · σ

- `R` = radius of curvature of the nozzle contour at the throat.
- `σ` = correction factor for property variation across the boundary layer; `σ = f(T_wg/Tc,
  γ, local Mach)`, tabulated in `[Huzel Fig 4-24]`.
- **The `(At/A)^0.9` term** is the exact area-ratio dependence — `h_g` is highest at the
  throat (`A = At` → term = 1) and falls toward the exit.
- Simplified: `h_g ∝ (mass velocity)^0.8` → `h_g ∝ Pc^0.8` and `∝ (1/local diameter)^1.8`
  `[Huzel eq. 4-11]`.

**Colburn / Dittus-Boelter form** (both gas and coolant side) `[Huzel eq. 4-12]`,
`[TN-Dump App. B eq. B3]`:

    Nu = C · Re^0.8 · Pr^N          C ≈ 0.023–0.026, N = 0.34 (Colburn) or 0.4 (Dittus-Boelter)
    Nu = h·D/k,  Re = ρ·V·D/μ,  Pr = μ·Cp/k

**Radiation cooling** `[Huzel eq. 4-38 p.121]`: `q = ε · σ_SB · T_wg^4`, with
`σ_SB = 0.3337×10⁻¹⁴ Btu/in²·s·°R⁴` (= 5.67×10⁻⁸ W/m²·K⁴). Design finds the `T_wg` that
satisfies both this and the wall's structural capability.

**Regenerative Isp benefit** `[Sutton §8.2 p.288]`: the heat the coolant absorbs is not
wasted — it augments the propellant's energy content before injection, **raising exhaust
velocity 0.1–1.5 %**.

**Tube-wall structural design** `[Huzel "Tubular Wall Thrust Chamber Design" p.107–114]`
(2026-09-17 addition — rendered leaves 116–123 as page images; OCR alone was too garbled
for the dense equations):

Real tube cross-sections are NOT uniform along the chamber/nozzle — `[Huzel Fig 4-31
p.113]` explicitly shows tube shape morphing from flattened/elongated ovals (away from
the throat, where circumference is larger relative to a fixed tube count) to fully
circular (at the throat, where stress is highest and circular is structurally
preferred): *"for easier fabrication and lower stress, tube cross sections of circular
shape are preferred. However, other shapes are often used to meet certain flow-area
requirements"* (p.107). Manufacturing: tubes start as uniform round stock, are wax-
filled and internally hydroformed (swaged in a die under internal hydraulic pressure)
into the tapered/flattened shape, then bent to the chamber contour `[Fig 4-31/4-32]`.
The tubes are then arranged on a brazing fixture (core) with "great care ... to assure even
distribution of the gaps between tubes" and furnace-brazed `[Huzel p.113-114]`; SP-8087 adds
the per-station "spanking" to round/oval section, the 6:1 = 3:1 reduction + 2:1 expansion
taper limit (3 1/2:1 pure-reduction ceiling) and shim/oversize-tube/peening fit-up
`[SP-8087 §2.1.1.3 p.12-13, Fig. 1]`. **Implication for engine_designer**: the brazed bundle
is contiguous (tubes touch at every station, flattening to ovals where pitch outgrows tube
height) - `gui/preview3d_gl_core/tube_bundle.py` draws it that way since 2026-09-23, and
`design.py` warns when a constant-count tube segment's width taper exceeds 3.5:1 / 6:1.

Combined stress at a circular tube's inner wall, maximum at the throat (`[Huzel Fig
4-29 p.107]`):

    S_t = (Pco − Pg)·r/t                    [hoop stress, net pressure, eq 4-27 p.107]
        + E·a·q·t / (2·(1−v)·k)             [longitudinal thermal-restraint stress, eq 4-28 p.108]

  - `Pco` = coolant pressure, `Pg` = **local** combustion gas static pressure (not Pc) —
    the net differential is used directly, works for either sign, no "reversal" special-
    casing needed, unlike the plate-bending proxy `design.py` currently uses.
  - `r` = the **tube's own local radius** (d/2, a few tenths of an inch — NOT the
    chamber radius), `t` = tube wall thickness.
  - No adjacent-tube bending term for a circular tube design — explicit in the source's
    own variable list: *"M_A = bending moment caused by discontinuity ... (no effect of
    pressure differential between adjacent tubes for circular tube design)"* (p.108).

Longitudinal thermal **inelastic buckling** criterion for the tube's hot-gas-side "zone
I" (restrained by the cooler, much-more-massive backside "zone II") `[Huzel eq. 4-29
p.108]` — a REAL, citable buckling formula the tool currently has none of:

    S_c = 4·E_t·E_c·t / [ (√E_t + √E_c)² · √(3·(1−v²)) · r ]

  `E_t`/`E_c` = tangential modulus at wall temperature / from the compression stress-
  strain curve at wall temperature. Design rule: the longitudinal thermal stress (eq
  4-28) should stay below `0.9·S_c`.

**Elongated tube design** (`[Huzel Fig 4-30 p.107]`, used wherever geometry forces a
non-circular cross-section) adds a bending-moment term from the pressure differential
BETWEEN ADJACENT TUBES (not coolant-vs-gas) `[Huzel eq. 4-30 p.109]`:

    M_A = K_A · (L²/12) · ΔP_adjacent        (standard clamped-beam-strip form)

  - `K_A` = dimensionless empirical design constant, **range 0.3–0.5, "based on test
    results"** — not derived, an honest admission of estimate-status in the source
    itself (matches this project's own Tier-3 framing).
  - `L` = length of the flat portion of the elongated cross-section, `ΔP_adjacent` =
    `Pco1 − Pco2` between neighboring tubes (e.g. a double-pass circuit where adjacent
    tubes carry coolant in opposite directions at different local temperature/pressure).
  - Substituted into the combined-stress equation above as an added `+ 6·M_A/t²` term.

**Coax-shell (single annular gap) design** `[Huzel eq. 4-31 p.109]` — directly matches
this tool's existing `wall_construction="coax_shell"` category:

    S_c = (Pco − Pg)·R/t + E·a·q·t / (2·(1−v)·k)

  Same structure as the tube-wall combined stress, but `R` = the shell's own radius —
  i.e. the FULL local chamber/nozzle radius, since a coax shell is a continuous shell,
  unlike discrete tubes. **This is the one case where using the full local radius as the
  lever arm is the physically correct real-engine formula** — confirming that
  `milled_channel`/`tube_wall` need a LOCAL span (channel width / tube radius) but
  `coax_shell` genuinely doesn't.

**Cooling-passage pressure drop** `[Huzel eq. 4-32 p.109]` — standard Darcy-Weisbach
form, cross-validating `cooling.py`'s existing `_darcy_friction`/`march_coolant`:

    ΔP = f · (L/d) · (ρ·V²)/(2g)

**Real sample-calculation anchor** `[Huzel Sample Calc 4-4 p.110–113]` — A-1 (LOX/RP-1,
Pc 1000 psia) and A-2 (LOX/LH2, Pc 800 psia) engines, both Inconel X circular tubes at
the throat:
- **A-1**: d=0.855 in, t=0.020 in, N=94 tubes; Pco=1500 psia, Pg=562 psia; combined
  `S_t = 52,500 + 15,000·M_A` psi; `F_ty=82,000` psi @ 1000°F allowable → `M_A,max = 1.88`
  in-lb/in.
- **A-2**: d=0.185 in, t=0.008 in, N=178 tubes; Pco=1200 psia, Pg=443 psia; combined
  `S_t = 68,750 + 93,900·M_A` psi (93,900 already folds in the `/t²` division);
  `F_ty=81,000` psi @ 1200°R allowable → `M_A,max = 0.131` in-lb/in.
- **OCR caveat**: several intermediate-algebra digits in this sample calc (leaf 120
  especially, the A-1 diameter-solve steps) came from a poor-quality scan and were NOT
  independently re-verified digit-by-digit against a rendered image. The final `d`/`t`/
  `N`/`M_A,max` summary numbers above ARE confirmed clean against the rendered page image
  (leaf 122) and are trustworthy; don't treat the dropped intermediate steps as exact.

## Empirical correlations & typical values

**Heat-transfer intensity (heat flux) magnitudes:**
- `[Huzel §4.4 p.98]`: 0.5–50 Btu/in²·s from hot gas to wall; combustion temps 4000–6000 °F.
- `[Sutton §8.2–8.3 p.283]`: **< 50 W/cm² (0.3 Btu/in²·s) to > 16 kW/cm² (100 Btu/in²·s)**.
  High end = nozzle throat of large bipropellant chambers; low end = gas generators, nozzle
  exit sections, small low-Pc chambers.
- **Only 0.5–5 % of the total energy generated reaches the walls** `[Sutton §8.2 p.285]`.
  For a 10 000-lbf engine, wall heat rejection is 0.75–3.5 MW.
- Radiation is **5–35 % of the transferred heat**; convection dominates; conduction from gas
  is negligible `[Sutton §8.2]`.
- **Peak heat flux is always at the nozzle throat**; lowest near the exit `[Sutton Fig 8-8]`.
- Cooling is *easier* at large thrust (wall area grows slower than volume) and more critical
  at small thrust `[Sutton §8.2, Huzel §4.4]`.
- Higher Pc → higher heat flux → this often sets the **material / cooling limit on maximum
  practical Pc** `[Sutton §8.2, Huzel §4.4]`.

**Cooling-method selection** `[Huzel §4.4 p.98–99]`, `[Sutton §8.2]`:

| Method | When used | Notes |
|---|---|---|
| Regenerative | bipropellant, medium–large thrust, **high Pc & high heat flux**; turbopump-fed (pressure budget available) | most widely used; adds 0.1–1.5 % to exhaust velocity; tubular or channel wall; coolant velocity highest at the throat by restricting passage area; axial/tubular jacket practical only for coolant flow > ~9 kg/s |
| Film / transpiration | high local heat flux, alone or with regen; near injector and toward throat | transpiration = film cooling through porous walls |
| Ablative | **low Pc (< ~250 psi)**, short duration, pressure-fed; nozzle extensions | needs fuel-rich exhaust (no free O2/OH); not effective at high Pc, long duration, or oxidative exhaust; **worst at 4–15 % duty cycle for pulsing** (max liner pyrolysis, `[Sutton Fig 8-10]`) |
| Radiation | **low heat flux**: monopropellant chambers, gas generators, **nozzle sections beyond area ratio ~6–10**, small bipropellant thrusters | needs refractory alloys good to 2600–3500 °R; works at Pc < 250 psi |

**Real LOX/RP-1 calorimeter data corroborates the Bartz under-prediction issue from real
hardware, not just CFD** `[TP2862-LOXRP1 p.11, "Concluding Remarks"; Summary p.15]`: NASA
Lewis water-cooled copper calorimeter chambers (37/61-element O-F-O triplet injectors, Pc
4.1-13.8 MPa) measured throat heat flux **~60% higher than a contemporary (1980) LOX/
hydrocarbon design-tool prediction**, reproduced independently at two Pc/O-F combinations —
the same qualitative direction as `[EUCASS-2023]`'s CFD finding below (uncalibrated Bartz
under-predicting wall temp by ~100 K), now from real fired hardware. Caveat: this is a
comparison against another paper's design-tool prediction, not a from-scratch Bartz
recompute — cite as "measured throat Q/A exceeded a contemporary design-tool prediction by
~60%," not as "Bartz under-predicts LOX/RP-1 by 60%." The same dataset gives a **directly
measured Pc-scaling exponent**: Q/A ∝ Pc^(0.8-1.0) in the cylindrical/combustion section,
Pc^(0.7-0.8) at the throat — the throat exponent sits at or slightly below the classical
Bartz Pc^0.8 term `[Huzel eq. 4-11]` already cited above, a real cross-check for that
assumption. **Carbon deposition (soot) knocks down the measured gas-side h_g by ~40% (UMR
injector, Pc 4.3 MPa) to ~60% (zoned injector, Pc 13.8 MPa)** vs. the soot-free calculated
value — the paper frames both coking and injector-zoning as *beneficial passive thermal
barriers* for long-term hydrocarbon-engine wall temperature, a nuance worth holding against
any framing of coking as a pure liability (see `topics/06b-cooling-methods-and-chemistry.md`
for the full RP-1-coking-chemistry picture). A **real LOX/RP-1 c* efficiency anchor**: the
unmodified 37-element triplet injector achieved **C*_eff ≈ 99.5%** at Pc≈4.1 MPa — a
high-quality-injector upper-bound data point for `topics/03-combustion-and-cstar.md`.
Separately, **sealing a triplet injector's outer oxidizer ring** (fuel-rich outer zone, a
passive film-cooling effect achieved through injector design rather than added film flow)
**cut throat heat flux by 47% for only a 4.5% C* efficiency cost** (99.5%→95-96.2%), halving
total integrated chamber heat load at matched Pc/O-F — a real, quantified injector-zoning
film-cooling tradeoff distinct from (and corroborating in kind) `film_effectiveness_profile`.

**Radiation-cooling materials** `[Huzel §4.4 p.121]`: Mo-0.5Ti and 90Ta-10W good to 3500 °R
(need MoSi2 coating on Mo for emissivity + oxidation); Ti alloys and Haynes 25 to 2600 °R.
Iridium coating on rhenium walls for oxidation resistance `[Sutton §8.2 p.287]`.

**H2 coolant-side enhancement built into the SSME design** `[Wieseneck-J2 p.24-25]`
(2026-09-23 re-read): wall roughness raised H2 h_c ~1.45-1.55x at 200 µin (5.1 µm; three
mass-velocity curves), and passage curvature from ~1.0 (10° turn) to ~1.9 (80-90° turn);
combined "more than doubled" in high-flux regions and "incorporated in the SSME design".
The same page set gives the generic channel-wall envelope for NARloy near 3000 psi: hot
wall ~0.01 in (stress minimum) to ~0.04 in (conduction maximum) `[p.17, read off chart]`,
and a practical coolant dP limit of ~0.1·Pc `[p.18-19]`. **No SSME or J-2 channel
count / dimension / flow split appears anywhere in the document**; nor in `[SECA-HT]`,
`[SP-8087]`, `[Sutton]`, `[Huzel]` (its A-1/A-2 are textbook examples, not hardware),
`[J2X-Overview]`, `[AEDC-J2S]`, `[ChannelWall-IAC19]` or `[Merkle-RegenCFD]` (re-read the
same day). Cited real passage data found: J-2S 180 down / 360 up tubes `[AEDC-J2S]`; F-1
Inconel-X 0.018 in tube wall, 2-pass `[SP-8087 Table I/III]`; J-2 and RL10 1½-pass CRES 347
`[SP-8087 Table I]`; LE-7 288 channels × 0.05 in, 540 psi jacket dP; RS-27 292 tubes ×
0.45 in, 100 psi; RL10B-2 253 psi `[Sutton Table 8-1 p.273]`; generic throat coolant
velocity 6-24 m/s `[Sutton §8.3 p.292]`.

**Real heat-flux anchors, J-2-class vs. SSME design point** `[Wieseneck-J2 p.6, 12]`: current
(~1970) O2/H2 engines (J-2, J-2S, M-1) run **17-35 Btu/in²·sec**; the Space Shuttle Main
Engine design point is **72 Btu/in²·sec at 3000 psia Pc** ("four times as high" as J-2) —
concrete mid-thrust and high-thrust bipropellant-hydrogen data points inside the existing
`[Huzel]`/`[Sutton]` 0.5-50/<50->16,000 W/cm² band. **Real construction-method lineage**:
"early V-2/Redstone chambers used simple double-wall construction; later chambers used
tubular construction; current engines rely on both tubes and channel-wall construction, [a]
modification of the earlier double-wall technique" `[Wieseneck-J2 p.2, 20]` — channel wall's
"chief advantage" is taking full use of the wall material's thermal conductivity, since flow
variation in one channel is smoothed by lateral conduction to neighbors through the solid
land (tube walls, thin low-conductivity paths between tubes, don't have this self-correcting
effect); tubular was used "almost exclusively" for lower-conductivity nickel/stainless
chambers. Real material limits: **annealed OFHC copper reaches ~4000 psi** Pc; **NARloy**
(high-strength, high-conductivity copper alloy) named as the SSME-enabling material;
stainless/nickel called unacceptable for high-Pc service; coolant-side wall temp assumed
400°F (SSME throat), gas-side max 1000°F (copper) / 1400°F (nickel/stainless). Real
**coolant ΔP practical limit ≈ 0.1 × Pc** — at Pc 3000 psi (SSME-class) implies ~300 psi,
consistent with (not contradicting) the existing 100-540 psi `[Sutton Table 8-1]` jacket-ΔP
band below.

**Real, quantified Bartz-calibration-error magnitude** `[EUCASS-2023 §3, p.7-8]`: an
uncalibrated Bartz model (C=0.026) run against a CFD reference case (LOX/Methane, Pc 56 bar)
**overpredicted peak heat-transfer coefficient by 42%, peak heat flux by 37.6%, and average
wall temperature by ~100 K**; even after tuning the Bartz constant down, jacket pressure
drop was still overpredicted by ~26% vs. the CFD truth case. This is real, independent
corroboration — from a source with no connection to this tool — that flat/uncalibrated Bartz
constants are unreliable enough to need per-propellant-class anchoring, exactly the approach
`cooling.py`'s `BARTZ_ABS_FLUX_CALIBRATION` already takes. The paper also gives a **closed-
form alternative to `[Huzel Fig 4-24]`'s undigitized sigma-correction chart** (its own `delta`
correction, Eq.5) and adds a full two-phase nucleate-boiling/critical-heat-flux (CHF)
treatment (Chen correlation + modified Tong CHF correlation, valid 1-50 bar / 2.5-8mm
hydraulic diameter / 4-60 MW/m²) that `cooling.py` doesn't attempt (single-phase coolant
only). A real worked example on its own small engine found **regen cooling alone could not
clear CHF near the throat** (saturation margin only 18.8 K) — adding film cooling at 7% of
coolant flow raised the margin to 57.5 K and dropped peak wall temp from 1124.5 K to 948 K, a
real independent instance of exactly the regen+film architectural pattern
`film_effectiveness_profile`/`dump_coolant_fraction` already implements (see
`topics/06b-cooling-methods-and-chemistry.md` for the film-cooling-model detail).

**Real regen-vs-dump/film system-level weight comparison, same engine class**
`[ASR72-238 Table 3, leaf 49]`: a 1972 Rocketdyne 6000-lbf-class OME trade study, three
propellant pairs at fixed MR, holding thrust/Pc/expansion ratio fixed and varying only the
cooling method — the first apples-to-apples same-engine regen-vs-dump/film comparison in
this reference set. Dump/film costs delivered Isp (e.g. NTO/MMH 313.0→304.8 s) and *reduces*
thrust-chamber weight (185→150 lb) but *increases* total propulsion-system weight once
propellant/tankage effects are folded in (**net +540 lb for NTO/MMH, +1136 lb for NTO/50-50,
+712 lb for O2/MMH**) — regen wins at the system level despite its heavier chamber, the
opposite of what a chamber-weight-only comparison would suggest. Real cooling-method
hardware detail at the same design point: NTO/MMH goes from **180 channels / 0.062 in. min.
height** (regen+film) to **514 channels / 0.025 in.** (dump/film) — nearly 3× the channel
count at under half the minimum height for the lower-heat-flux-tolerant dump/film design.
**LOX/RP-1, LOX/N2H4, and LOX/C3H8 all use zero supplemental film cooling** even in the
"regen+film" family (high propellant decomposition temperature for the first two RP-1/N2H4
cases, per the narrative) — LOX/RP-1's jacket ΔP is only **3-8 psi** across its whole tested
Pc range, dramatically lower than every amine-fuel combination (10-36 psi) at the same
thrust class. Real Cb→Ti radiation-nozzle-extension transition criterion, more specific than
this file's existing "area ratio ~6-10" rule: **coated columbium for 1600°F < T ≤ 2400°F,
coated titanium for T ≤ 1600°F** `[Tables 4-6, leaf 50-52]`.

**Real material creep/fatigue-life data for regen-chamber liner candidates**
`[ASR72-238 Figs. 6-7, leaf 109-110]`: at the maximum hot-gas-wall stress level (15-hour/
1000-cycle life requirement, safety factor 4), real creep-rupture data for three candidate
materials — **Haynes 188 at 47 ksi, Inconel 625 at 50 ksi, CRES at 34 ksi** — none approaches
its rupture-damage limit even near 1300°F, concluding "no significant creep damage on regen.
chamber" for any of the three. Real fatigue-cycle-count-by-station data: predicted fatigue
life is **lowest at the throat (~1.3×10⁴ cycles)**, rising to **~4-5×10⁴ cycles** a few
inches downstream and **~10⁵ cycles** at the injector end — the throat confirmed
fatigue-critical (consistent with `[Miller-CuFatigue]` elsewhere in this reference set), with
roughly **13× margin** over the 1000-cycle requirement before the analysis's own SF of 4 is
even applied — a real, quantified example of how much margin a regen-chamber life analysis
can carry. **A real creep-vs-fatigue failure-mode split by cooling method**: the same
study's structural/life analysis found the **dump/film-cooled chamber's dominant failure
mode is creep** (driven by the high axial thermal gradient where the film coolant
decomposes), the opposite of the **regen-cooled chamber, where fatigue dominates** — a real,
if qualitative, design-method finding not previously captured from any other source in this
reference set (Appendix A, leaf 200-202).

## Worked numbers

`[Huzel Sample 4-7 p.121]` radiation-cooled A-4 nozzle extension at ε = 8: `h_gc = 7.1×10⁻⁵
Btu/in²·s·°R`, `T_aw = 4900 °R`, emissivity 0.95 → solve `7.1×10⁻⁵·(4900 − T_wg) = 0.95·σ_SB
·T_wg^4` → **T_wg = 2660 °R**, heat flux = 0.159 Btu/in²·s. (Low flux — this is why nozzle
extensions past ε ~6–10 can use radiation cooling and a cheaper/simpler material.)

`[TN-Dump]` GH2/LOX, Pc 100 psig, O/F 5: min satisfactory LH2 coolant flow 7.5 % of total
propellant flow (uncoated 304 SS wall, 2000 °R flame-side limit); 6.9 % with 0.033-in Al2O3.

## Caveats

- Bartz `σ` needs `[Huzel Fig 4-24]` (function of `T_wg/Tc`, γ, Mach) — not transcribed
  here; render leaf 111 if implementing.
- The `[TN-Dump]` quantitative coolant fractions are for a tiny low-Pc engine and do not
  scale; the *correlations* (Dittus-Boelter, recovery factor 0.88–0.90) do.
- `[Sutton §8.3]` has the full coolant-side channel-design treatment (channel geometry,
  pressure drop, thermal stress) — read leaves 323–334 before building a real regen model.
  **Update 2026-09-17**: this is now specifically the `milled_channel` complement — the
  `tube_wall` and `coax_shell` construction types have their own real, extracted equations
  above (`[Huzel]`'s Tubular Wall / Coaxial Shell sections), so `[Sutton §8.3]` is only
  still-needed for the milled-channel rectangular-slot case.
- `[Wieseneck-J2]` is a Rocketdyne viewgraph-style presentation (no formal report number
  found) with most actual charts OCR-unreadable — only body-text captions were usable; its
  "double wall" reference is the same generic Western category as `[SP-8087]`'s, not Russian
  sandwich construction. Pre-hardware SSME design-point projections (~1970), not flight data.
- `[EUCASS-2023]` is a small-engine (4 kN) single-team paper, one tier below a NASA
  design-criteria monograph or real-engine data — treat its own novel numerical claims (20%
  radiative split, CHF margins) as a small-engine-scale data point to corroborate against,
  not a universal constant.
- `[TP2862-LOXRP1]`'s "~60% higher than design prediction" finding is a comparison against
  another paper's design tool, not a from-scratch Bartz recompute, and its OCR-garbled
  figures mean only prose-restated numbers are trusted here (no tabulated axial heat-flux
  profile was extractable).

## Implications for engine_designer

- **`manifold.py` turnaround collar (2026-09-22)**: `f1_split_reverse_flow`'s `jacket_return`
  ring now follows `[SP-8087 §2.1.2.1 p.20]`'s common-annulus turnaround - bore sized from the
  local coolant-passage height (`TURNAROUND_BORE_PASSAGE_MULT`, Tier 3), flush on the wall,
  instead of a header sized on the whole down-leg mdot.
- **`cooling.py` (added)** now implements the "minimal real model" this section sketched
  below: a wall heat-flux DISTRIBUTION along the contour from the `(At/A)^0.9` Bartz shape
  (`RECOVERY_FACTOR = 0.9` carried for context), plus its integral (`wall_heat_total_w`) and
  the regen-jacket coolant delta-T it implies. Magnitude is normalised so the cooled-zone
  area-average equals `expander.py`'s existing `5 MW/m² @ Pc 4 MPa` anchor (the two models
  can't disagree on total heat). It is a shape + one anchor, NOT a coolant-channel /
  boundary-layer / CFD solve - absolute throat flux is under-resolved by the tool's coarse
  contour, so `validate.py::run_cooling_heat_flux_check()` gates on the jet-power-to-wall
  fraction ([Sutton 8.2] 0.5-5%) and shape sanity, not on absolute MW/m². A
  regen-jacket coolant-capacity warning (warn, never block) fires when the coolant delta-T
  exceeds the pair's coking/boiling limit. Rendered on the 2-D schematic (contour tinted by
  flux, cooling-regime bands, wall-temp margin).
- **`materials.py` `cooling_effectiveness` (flat "assumed_wall_temp = Tc · fraction",
  0.25–0.60; ASSUMPTIONS.md item #11)** is the coarsest proxy in the tool. `[Huzel eq. 4-10]`
  gives the real relation: `T_wg` is where `h_g·(Tc·r − T_wg)` balances the coolant's heat-
  removal capacity. A minimal real model would (a) use recovery factor `r ≈ 0.90` instead of
  1.0 (the tool currently assumes `T_aw ≈ Tc`, which is ~10 % pessimistic), and (b) compute
  `h_g` from Bartz at the throat and scale by `(At/A)^0.9` along the contour.
  **CORRECTION (2026-09-23 cooling audit):** (a) was implemented as `T_aw = 0.9·Tc`, which
  misreads the recovery factor - it applies to the DYNAMIC part only,
  `T_aw = T_s + r (T0 − T_s)`, i.e. ≈ T0 in the chamber and ≈ 0.99·T0 at the throat (the
  "~10 % pessimistic" remark applies to a high-Mach station, not the throat). engine_designer
  now uses the per-station form with `r = Pr^(1/3)`, the full Bartz σ, and chemical-
  equilibrium transport properties; with those, raw Bartz meets `[Wieseneck-J2]`'s J-2 and
  SSME throat fluxes with no calibration (engine_designer/COOLING_AUDIT.md).
- **`materials.py` `BARTZ_AREA_RATIO_EXPONENT = 0.9`** is not an approximation — it is the
  literal `(At/A)^0.9` term in `[Huzel eq. 4-13]`. ASSUMPTIONS.md item #12 can note "the 0.9
  exponent is the exact Bartz area-ratio term (Huzel eq. 4-13); only the `WALL_TEMP_DAMPING
  = 0.5` and the `[0.5, 1.6]` clamp are the tool's own judgment." The CR heat-flux factor
  `(1.6/CR)^0.9` is a reasonable read of that term applied to the *chamber* section (where
  `A/At = CR`).
- **`expander.py` heat-pickup proxy** `flux = 5.0e6·(Pc/4.0e6)^0.8` W/m² (ASSUMPTIONS.md
  item #16): the `Pc^0.8` exponent is exactly `[Huzel eq. 4-11]` (`h_g ∝ Pc^0.8`). The
  reference value `5 MW/m²` at Pc 4 MPa is in the `[Sutton]` band (up to 16 kW/cm² =
  160 MW/m² at the throat of large chambers; 5 MW/m² = 0.5 kW/cm² is a sane
  chamber-average). Tuning it to make RL10-class feasible and large kerolox infeasible is
  consistent with `[SP-8107]`'s statement that the expander cycle is "limited to ~1000 psia
  Pc by the power available from heated fuel" and "not feasible at high thrust as heat
  transferred per pound of propellant pumped decreases."
- **`design.py` `JACKET_DP_PA = 1.6e6` scaled by cooling method** {regen 1.0, dump 0.2,
  ablative 0.0, radiative 0.0} (ASSUMPTIONS.md item #29): `[Huzel §4.4 p.99]` confirms
  ablative/radiation chambers have *no active coolant loop* → zero jacket ΔP is correct.
  `[TN-Dump]` shows a real regen-style jacket ΔP of ~90–140 psi (0.6–1.0 MPa) for a small
  low-Pc engine; 1.6 MPa for a full-size high-Pc regen jacket is reasonable. `[Sutton
  Table 8-1]`: real jacket ΔP 100 psi (RS-27), 253 psi (RL10B-2), 540 psi (LE-7) — i.e.
  0.7–3.7 MPa, so 1.6 MPa is mid-range. (The unsourced film 0.2 fraction was retired
  2026-09-23 — film stopped being a section method; see `topics/06b-cooling-methods-and-
  chemistry.md`'s film-overlay bullet.)
- **`cooling_transition_eps` default 6.0**: directly `[Sutton §8.2 p.286]` — "radiation
  cooling is used ... for diverging nozzle exhaust sections beyond an area ratio of about
  **6 to 10**." The tool's default of 6 is the conservative (earlier-transition) end of the
  cited range. Well-supported; ASSUMPTIONS.md item #37 can cite this.
- **Regen Isp benefit (0.1–1.5 %)** `[Sutton §8.2]` is not modelled — a future addition
  could credit a small Isp bump for regeneratively-cooled designs.
- **Radiation material temp limits**: `materials.py` `niobium_c103` (max 1650 K), `haynes_230`
  (1400 K), `rhenium_iridium` (2200 K) — `[Huzel §4.4]` gives Ti/Haynes-25 ≈ 1444 K
  (2600 °R), Mo-Ti / Ta-W ≈ 1944 K (3500 °R). C-103 at 1650 K and Re-Ir at 2200 K are
  consistent with "refractory alloys 2600–3500 °R"; Haynes 230 at 1400 K matches Haynes 25.
- **`design.py`'s jacket-overpressure check (added 2026-09-16) should be redesigned
  per construction type**, now that real formulas exist for two of the three
  `WALL_CONSTRUCTIONS`: it currently applies one generic clamped-plate-strip bending
  proxy (channel width as span) uniformly, gated to `regen_channel_model="channels"`
  only. That proxy was itself a correction of an even cruder full-chamber-radius hoop-
  stress version — `[Huzel eq. 4-27]`/`[eq. 4-31]` above show BOTH were incomplete
  simplifications of two genuinely different real formulas: `tube_wall` wants `[Huzel
  eq. 4-27]` (net `Pco−Pg` × the tube's own local radius / thickness — no "reversal"
  framing needed, the net form handles either sign), while `coax_shell` wants `[Huzel
  eq. 4-31]` (same structure but with the FULL local shell radius as the lever arm,
  confirming the tool's *original*, since-corrected full-radius approach was actually
  right for coax_shell specifically, just wrong for tube_wall/milled_channel).
  `milled_channel` still has no citable formula (the closest is `[Sutton §8.3]`,
  flagged above as unread) — the current plate-bending proxy is the most defensible
  stand-in for that construction only, not the other two.
- **How the eq. 4-27 + 4-28 sum is judged (2026-09-24)**: Huzel's Sample Calc 4-4 holds
  the combined stress to `F_ty` *at wall temperature with no safety factor* (82 ksi A-1,
  81 ksi A-2, p.110-113). That is an elastic design rule for his sample, not a burst
  criterion. The thermal term is a secondary, imposed-strain stress: once the hot face
  yields it stops growing and becomes cyclic plastic strain, a low-cycle-fatigue limit.
  `structure_stage.py` therefore gates on the PRIMARY hoop term (eq. 4-27) vs allowable/SF
  only and routes the thermal term to the throat fatigue row. Holding the sum to the
  tool's max-service-temperature `allowable_stress_pa`/1.5 had failed the real F-1, J-2
  and RL10. The primary/secondary split itself (ASME Sec. III practice) has no citation in
  this collection yet; SP-8087 §2.1.5/§3.1.5 (structural analysis, not yet distilled) is
  the likely source.
- **A real longitudinal thermal-buckling check is now addable** (`[Huzel eq. 4-29]`,
  `S_c = 4·E_t·E_c·t / [(√E_t+√E_c)²·√(3(1−v²))·r]`, design rule `S_1 < 0.9·S_c`) — a
  genuinely different failure mode from the pressure-reversal check (thermal-restraint-
  driven buckling of the tube's hot-gas-side "zone I" against its cooler backside "zone
  II", not a coolant-vs-gas pressure differential), and the tool currently has no
  buckling check of any kind. Needs `E_t`/`E_c` (tangential moduli, elastic vs. from the
  compression stress-strain curve at wall temperature) — neither is in `materials.py`
  today, only `thermal_conductivity_w_mk`/`cte`/`allowable_stress_pa`; would need new
  per-material fields (a real gap, not an estimate to paper over).
- **`[Huzel]`'s Sample Calculation 4-4 (A-1/A-2 engines, real Inconel X tube numbers at
  the throat — see above)** is a genuine real-engine spot-check anchor for whichever of
  the above gets implemented, replacing the "this codebase has no real-engine spot check
  for it yet" caveat the current jacket-overpressure warning text and ASSUMPTIONS.md
  entry both carry.
- **Coolant manifold design content lives in `topics/12b-structures-manifolds-and-
  hardware.md`** (real numbers from `[SP-8087]`'s manifolds section and
  `[Fagherazzi-2019]`'s volute-sizing method) rather than duplicated here — this file
  covers heat transfer and jacket-wall structure; manifold inlet/outlet/turnaround design
  sits alongside `[SP-8120]`'s existing manifold-structural-supports content there.
- **`BARTZ_ABS_FLUX_CALIBRATION`'s LOX/RP-1 anchor now has independent real-hardware
  corroboration** (`[TP2862-LOXRP1]`'s ~60%-high calorimeter finding) alongside the existing
  `[EUCASS-2023]` CFD corroboration — two independent sources, one hardware, one CFD, agreeing
  that uncalibrated design predictions under-predict real LOX/hydrocarbon throat heat flux.
  Strengthens confidence in the per-propellant-class calibration approach; no new number to
  apply (the calibration is already anchored to real engines, not to either of these papers).
- **Tube cross-section SHAPE varies along the contour** (`[Huzel Fig 4-31]` — elongated/
  flattened near larger-circumference stations, circular at the throat), which
  `cooling.py`'s `channel_target_height_m()`/`channel_hydraulic_geometry()` doesn't model
  at all today: channel HEIGHT is sized once at the throat and held constant along the
  whole march: only width varies, purely from local circumference. A real model would
  let the cross-section's aspect ratio/shape itself change with station, driven by the
  same structural/flow-area logic Huzel describes, not just scale a fixed-height
  rectangle. Separately, `EngineDesign.tube_split_eps` (doubling channel count partway
  down the nozzle, matching real practice like the F-1's 178→356 split) exists as a GUI
  field but is currently **purely cosmetic** — used only by the 3D-preview renderer
  (`gui/preview3d_gl.py`/`preview3d_gl_core.py`), never by the real channel-flow physics
  in `cooling.py`. Making it real physics is a natural companion to the shape-taper work.
