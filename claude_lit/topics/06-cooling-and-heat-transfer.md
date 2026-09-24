# 06 — Cooling and wall heat transfer

## Scope

Gas-side heat transfer to the chamber/nozzle wall, coolant-side heat pickup, and the
cooling methods (regenerative, film, transpiration, ablative, radiation). **Stale-note
correction (2026-09-14): as of Phase 7, `cooling.py` HAS a real Bartz-gas-side h_g +
computed hot-gas-wall-temperature + radiation-equilibrium + regen-Isp-credit model with a
per-propellant-class-calibrated absolute wall-heat-flux profile — this is no longer "the
tool's biggest modelling gap."** This file remains the correlation/typical-value reference
for that code and for anything not yet covered (real coolant-channel/boundary-layer CFD,
which the tool still doesn't attempt).

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

**Regenerative cooling's limiting factors and feasibility bounds** `[Marquardt-5981 §V-B-1
p.12-13]` (a 1963 small-spacecraft-engine, 20–10,000 lbf, cooling-method-selection study —
treat magnitudes as representative of that scale, not large boosters): three named limits —
coolant supply pressure, minimum practical coolant-passage dimension, and maximum coolant
temperature rise (expressed as a max coolable expansion ratio, or for H2 specifically a max
allowable enthalpy rise). Earth-storable propellants below **~250 psia Pc** can use
regenerative, radiative, *or* ablative cooling — consistent with `[Sutton]`'s own "ablative
< ~250 psi" threshold in the table below, now cross-corroborated from an independent 1963
source. A worked earth-storable design (N2H4+EDA/N2O4, 500–2000 lbf, 40:1 expansion) gives
concrete numbers: **minimum practical coolant-passage dimension 0.062 in**; regen-coolable
Pc range scales with thrust at that passage floor (F=500 lbf → Pc 30–60 psia; F=2000 lbf →
Pc 120–240 psia, both a cooling-imposed 4:1 throttle ratio); and **cooled expansion ratio
capped at 10:1**, with a radiation-cooled refractory-metal skirt from 10:1 to 40:1 — the same
regen-then-radiation architecture `EngineDesign.regen_nozzle_end_eps` already implements,
now with a real (if small-engine) precedent. Cross-method regime summary from the same
source: "radiation — low thrust, long run times; ablative — low thrust, 10–300 s; regen —
high thrust, medium-long run times; heat sink — short run times."

**Regen-cooling plumbing/operational notes** `[Marquardt-5981 §V-B-1b p.12-13]`: coolant
jacket volume should be **gas-purged after each operating cycle** on a restart-capable
engine (drain-by-evaporation, hypergolic-reignition, and freezing risks from residual
coolant) — a purge path is a plumbing-design input, not something added after the fact.
Coolant preference ranking: **H2 best, then N2H4, then Aerozine-50**. Exterior jacket wall
temperature stays under 400°F for storable-liquid-cooled jackets but can exceed 1000°F for
hydrogen-cooled jackets. Real reliability data point: regen chambers have operated without
catastrophic failure with up to **10% of coolant passages holed** (space vacuum environment
— external leaks in atmosphere are more serious). Dump/open-tube cooling is explicitly gated
on regen feasibility ("a chamber that cannot be regen-cooled with the total fuel flow cannot
be dump-cooled by a fraction of it") — dump is only viable where regen is already easy (high
thrust or low Pc), corroborating rather than superseding `[TN-Dump]`'s own ~2% dump-fraction
treatment in `topics/07-dump-cooling.md`.

**Real construction-type selection criterion (tube vs. channel wall)** `[SP-8087 §3.1.1.1
p.54]` — a genuinely new, dimensioned decision rule this reference set didn't have before:
max heat flux **< 12 Btu/in²·s** → simple channel-wall recommended; **10-25 Btu/in²·s** →
tubular recommended (advanced channel-wall also usable); **> 25 Btu/in²·s** → advanced
channel-wall techniques should be used; **thrust < 20,000 lbf** → simple channel-wall
preferred regardless of heat flux; for **minimum weight**, tubular is recommended (an
explicit weight-vs-simplicity tradeoff, not a strict heat-flux-only decision). Real
wall-construction survey: all major production fluid-cooled chambers (1000-1.5M lbf, up to
1000 psia Pc) use multi-pass tubular construction except small/low-heat-flux units (Atlas
vernier, Aerobee: double-walled; Agena: drilled passageways) — directly consistent with the
above criterion. **Tube geometry**: max taper 3:1 by pure reduction (spinning/swaging), up
to 6:1 combined with an expansion process (beyond 6:1 costs escalate) `[SP-8087 §3.1.1.3.1
p.55]`; **minimum tube wall thickness 0.010 in** — thinner is "a poor risk" even when
analysis says it would work, due to flaw sensitivity/erosion/handling-dent risk; real
hardware needed raising 0.010 in to 0.016 in after pinholing `[SP-8087 §3.1.1.3.2 p.56,
§2.1.1.3 p.13]`. **Channel aspect ratio**: width/height < 2 in high-heat-flux regions
(avoids corner velocity-depression); up to 8 acceptable if height > 0.10 in `[SP-8087
§3.1.1.4.1 p.58]`. **Coolant velocity limits**: liquids < 200 ft/s; gases < Mach 0.3
recommended, 0.5 absolute max (choking risk at bends above that) `[SP-8087 §3.1.1.5.3
p.61]`. **Thermal margin**: operate heat-flux-limited coolants at < 80% of mean burnout
flux `[SP-8087 §3.1.1.5.2 p.60]`. **Wall temperature chemical limits**: RP-1 coking above
850°F (728 K); furfuryl-alcohol-residue above 600°F; Aerozine-50 detonation risk above
600°F `[SP-8087 §3.1.1.5.4 p.61]` — consistent with this file's existing LOX/RP-1 ~120K-ΔT
coking-limit framing.

**RP-1 coking — real onset/peak band and rate data, not just a single threshold**
`[Lewis-Deposits, Abstract; Kerosene Fuel Tests p.5-7; Concluding Remarks p.12]`: a dedicated
UTRC/NASA-Lewis electrically-heated test-tube rig (not a firing engine, same character as
`[TN-Dump]`'s rig) measured **substantial RP-1 deposit formation between 600 and 800 K, with
peak deposit RATE occurring near 700 K** — a real, independently-measured band that sits
close to but is subtly different from `[SP-8087]`'s single-point 850°F (728 K) figure above:
728 K lands near this report's own measured *peak*, not its *onset* (600 K), suggesting
SP-8087's number is better read as a "significant/design-limiting" threshold than a true
onset. **Deposit rate is non-monotonic (bell-shaped) with wall temperature — it FALLS OFF
again above ~800 K**, so a flat "coking above X K" model understates the real physics; the
hottest wall station is not necessarily the worst one for fouling accumulation. Real rate
magnitude: **400-600 µg/cm²·hr for RP-1 at 500-800 K wall temp** (10-minute test exposure,
"not anticipated" to be this high per the authors); deposit rate falls with increasing
coolant velocity and is essentially **pressure-independent from 13.8 to 34.5 MPa** (136-340
atm) — i.e. the coking limit shouldn't need a Pc-dependent correction across typical/high
chamber-pressure ranges. **Nickel plating cuts the RP-1 deposit rate by ~10× (to ~50
µg/cm²·hr)** — bare copper is framed as *actively catalyzing* coking, not just a passive
substrate, a real quantified mitigation lever beyond "stay under the wall-temp limit."
More-refined JP-7 fuel (lower sulfur, deoxygenated) gave **no improvement over RP-1** — fuel
refinement alone is not a reliable mitigation on this rig; the wall material mattered far
more than fuel grade. Propane fouls worse than either kerosene fuel at any given wall temp
and shows a distinct near-critical-point (366 K) thermal instability with a copper-dendrite
deposit morphology — a different, more severe failure mode than kerosene's surface coke.
Caveat: fixed 10-minute test exposure, not directly extrapolable to a real engine's full
burn duration without a time-dependent fouling model this report doesn't provide — treat the
rate numbers as an order-of-magnitude anchor, not a life-prediction formula.

**Real LOX/RP-1 calorimeter data corroborates the Bartz under-prediction issue from real
hardware, not just CFD** `[TP2862-LOXRP1 p.11, "Concluding Remarks"; Summary p.15]`: NASA
Lewis water-cooled copper calorimeter chambers (37/61-element O-F-O triplet injectors, Pc
4.1-13.8 MPa) measured throat heat flux **~60% higher than a contemporary (1980) LOX/
hydrocarbon design-tool prediction**, reproduced independently at two Pc/O-F combinations —
the same qualitative direction as `[EUCASS-2023]`'s CFD finding above (uncalibrated Bartz
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
any framing of coking as a pure liability. A **real LOX/RP-1 c* efficiency anchor**: the
unmodified 37-element triplet injector achieved **C*_eff ≈ 99.5%** at Pc≈4.1 MPa — a
high-quality-injector upper-bound data point for `topics/03-combustion-and-cstar.md`.
Separately, **sealing a triplet injector's outer oxidizer ring** (fuel-rich outer zone, a
passive film-cooling effect achieved through injector design rather than added film flow)
**cut throat heat flux by 47% for only a 4.5% C* efficiency cost** (99.5%→95-96.2%), halving
total integrated chamber heat load at matched Pc/O-F — a real, quantified injector-zoning
film-cooling tradeoff distinct from (and corroborating in kind) `film_effectiveness_profile`.

**Russian "sandwich" wall construction — CORRECTION (2026-09-24): real construction detail
was already in `claude_lit` all along, in `[Ch12-Materials]`, just never checked against this
question.** Six sources were searched *specifically for this* across two earlier rounds —
`[SP-8087]`, `[Gubanov-1991]`, `[Wieseneck-J2]`, `[Fagherazzi-2019]`, `[EUCASS-2023]`,
`[ChannelWall-IAC19]` — and all six genuinely came up empty (detail below). But
`[Ch12-Materials]` was distilled in an *earlier* batch (2026-09-14), before this question was
ever asked, and was never re-checked against it — a real gap in the search process, not in
the literature itself. Its §12.5.2 (printed p.26-28) gives real engineering detail:
**construction** — Cu-Cr (Cu~3%Cr) inner liner with milled slots/channels for channel-wall,
or a **corrugated sheet-metal divider** between the Cu-Cr liner and an outer shell (alloy
steel/stainless/Ni-base) for sandwich-wall, the corrugations themselves forming the coolant
flow passages; **joining method** — originally (1930s) just bolted together with tolerated
inter-channel leakage, replaced post-WWII by a pressure-brazing method the Russians call
"solder-welding," the development that "made possible effective, efficient and reliable
rocket engines"; **real application** — channel-wall is usually used for the *combustion
chamber*, while "for medium-performance engines, such as the RD-107, the expansion *nozzle*
is a sandwich structure"; **tradeoffs stated** — channel-wall/sandwich both reputedly cheaper
to fabricate than tubular, but heavier. A real complication for the "Russian" framing: the
source's own Figure 12-24 shows the **F-1's lower nozzle extension is ALSO sandwich
construction** (Hastelloy-C, dump-cooled with turbine exhaust) — so face-sheet-plus-
corrugated-core sandwich construction is not exclusive to Soviet practice, just bonded
differently (the source separately describes a modern Volvo/Vulcain nozzle-extension sandwich
design joined by laser welding, not brazing). **What's still missing**: no channel/corrugation
pitch, height, or wall-thickness numbers, no cross-section drawing dimensions, no structural
formula — this is real construction-concept-and-materials detail, not the dimensioned design
criteria `[SP-8087]`-style monographs give for tube/channel-wall. **The six-source "not
found" search below remains accurate for that deeper level of detail** — it just wasn't the
whole picture, since it never checked the one already-distilled source that names the
technology at all.

Original six-source search (still valid, now understood as incomplete rather than
exhaustive): `[SP-8087]` (NASA's dedicated fluid-cooled-chamber design-criteria monograph —
confirmed via full-text search, the word "sandwich" never appears; its closest concept is
**"double-wall construction"**, a single-helical-channel design used only on small
low-heat-flux units like the Atlas vernier/Aerobee, explicitly NOT the high-heat-flux
multi-channel construction Russian engines like RD-170/RD-253/RD-180 are known for —
SP-8087's own introduction says advanced channel-wall fabrication was still "in development"
and "not covered in detail" as of 1972); `[Gubanov-1991]` (a paper by Energia's own chief
designer, giving real RD-170/RD-120/RD-0120 spec tables — but its only chamber-construction
description is one generic sentence per engine, "the chamber is a brazed-welded unit," no
cross-section or layer detail at all); `[Wieseneck-J2]` (Rocketdyne's own V-2/Redstone→
tubular→channel-wall lineage narrative uses "double wall" for the same generic Western
1940s-50s category as SP-8087, not the Soviet construction); `[Fagherazzi-2019]` (a 156-page
regen-cooling thesis with its own construction-type literature review — covers only tubular
and machined-channel families, zero hits for "sandwich" or "double wall"); `[EUCASS-2023]`
(only discusses the milled-channel type it actually built); `[ChannelWall-IAC19]` (NASA
MSFC's 2019 channel-wall-nozzle manufacturing survey — modern 2012-2019 US
additive-manufacturing/water-jet-milling fabrication processes for milled-channel and
bimetallic walls, a different technology entirely, no corrugated/finned-core geometry or
Russian practice mentioned; it does give real hot-fire wall-temperature anchors instead —
peak measured hotwall temp ~1,350°F for RP-1-cooled Inconel 625 and ~1,300°F for GH2-cooled
JBK-75, both at real Pc up to ~1,240 psig — a real complement to the material max-use-temp
limits already cited from `[Huzel]`/`[Sutton]`).

**Remaining gap, narrowed**: a dimensioned design-criteria source (channel/corrugation
geometry, wall thickness, structural formula) for sandwich-wall construction specifically —
not the construction concept or materials, which `[Ch12-Materials]` now covers.

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
`film_effectiveness_profile`/`dump_coolant_fraction` already implements.

**Richer coolant-side correlation set + real convective/radiative split** `[Fagherazzi-2019
§2.4.5 p.42-44]`: five published Nu correlations compared (Sieder-Tate laminar/turbulent, a
laminar-turbulent transition blend, Gnielinski [most broadly valid, 3000 < Re < 5e6], and two
entrance-effect-corrected forms) — substantially richer than this file's single
Dittus-Boelter-form citation, useful if `cooling.py` is ever extended with a real coolant-side
h_c correlation instead of its current `WALL_CONSTRUCTIONS`-scaled proxy. A real **80%
convective / 20% radiative gas-side split** is quoted (citing Sutton) — a specific point
estimate sitting inside the existing "radiation is 5-35% of transferred heat" `[Sutton §8.2]`
band, not a contradiction. **A real jacket-ΔP rule of thumb**: maximum permissible
regenerative-cooling pressure loss is **15-22% of coolant inlet pressure**, "depending on
design requirements" `[Fagherazzi-2019 §2.5.4 p.59]` — a percentage-of-supply-pressure framing
of the same jacket-ΔP question this file's existing `[Sutton Table 8-1]`/`[TN-Dump]`/
`[Wieseneck-J2]` absolute-pressure anchors already address, worth cross-referencing if
`design.py`'s `JACKET_DP_PA` is ever changed to scale with coolant supply pressure. A real,
useful negative finding: **channel cross-section reduction increases heat flux/lowers wall
temp but pressure drop rises faster-than-exponentially past a point of diminishing thermal
return** — no closed-form optimum exists, it must be found numerically (as `[EUCASS-2023]`
also does via a genetic algorithm). Also confirms the general principle (also seen in
`[SP-8120]`'s and `[Marquardt-5981]`'s minimum-passage findings) that **at small-engine scale,
minimum manufacturable wall thickness governs, not calculated stress** — a real worked
example found the structurally-required liner/channel-wall thickness (0.05-0.6 mm) far below
the practical 0.5 mm 3D-printing floor actually used.

**Real P&W in-house regen-channel design-rule set, recurring unchanged across 7 real
engines** `[STBE-PW leaf 161, 270, 321, 341]`: a 1989 Pratt & Whitney booster-engine
configuration study (seven fully-worked 600-750 Klbf-class LOX/CH4, LOX/RP-1 engines across
gas-generator, split-expander, and tap-off cycles) applies the **same four channel-geometry
guidelines to every variant** — passage aspect ratio ≤5.0, passage land width ≥0.050 in,
coolant Mach ≤0.5, 0.2%-yield tube-stress margin ≥1.0 with ultimate-temperature margin ≥375
R — strongly suggesting these read as period P&W standard practice rather than case-specific
results. A real worked point (Unique STBE Split Expander, LOX/CH4, Pc 896 psia): max
predicted hot-wall temp 2170 R, max heat flux 21 Btu/in²-sec, coolant Mach only 0.2 (well
under the 0.5 limit) — a real design margin, not a limiting case. Also: the Unique STBE GG
engine's minimum L* (31.3 in) is explicitly stated as the smallest value meeting a **98.0%
characteristic-velocity efficiency target** — a real, explicit c*-efficiency design
criterion rather than an assumed L* value, useful alongside `topics/04-chamber-sizing.md`'s
existing L* discussion. Separately, the Unique Split Expander's main chamber routes coolant
**countercurrent to the gas flow specifically "to provide the coolest fuel at the throat
where wall heat flux is highest"** `[leaf 320]` — an explicit real-engine rationale for
countercurrent regen routing, corroborating (not new to) the cooling-flow-topology choice
`cooling.py` already defaults to.

**CFD entrance-region corroboration, minor** `[Merkle-RegenCFD p.4-5]`: an idealized
straight-passage CFD case (water-as-RP-1-surrogate, non-reacting hot-gas boundary, not a real
engine) found wall temperature near a coolant passage's entrance **rises sharply, dips
slightly over the next ~50mm (copper's high conductivity redistributing the initial thermal
shock), then resumes increasing** — a real but narrow, geometry-specific CFD finding; not
portable as a number, and (like `[SECA-HT]`) not a correlation source. Also confirmed a
land-vs-passage-centerline circumferential wall-temperature non-uniformity that any 1-D/
axisymmetric model (including `cooling.py`'s contour-average treatment) cannot capture by
construction — a known, accepted simplification, not a new finding to act on.

**Coolant-side ΔT limits** (from the tool's own expander model, representative): LOX/LH2
~500 K, LOX/RP-1 ~120 K (coking limit), N2O4/MMH ~150 K. `[TN-Dump]` shows LH2 coolant going
from ~57–85 °R inlet to 1575–1900 °R outlet with a refractory-metal wall — a ΔT of ~800–1000
K is achievable for hydrogen.

## Worked numbers

`[Huzel Sample 4-7 p.121]` radiation-cooled A-4 nozzle extension at ε = 8: `h_gc = 7.1×10⁻⁵
Btu/in²·s·°R`, `T_aw = 4900 °R`, emissivity 0.95 → solve `7.1×10⁻⁵·(4900 − T_wg) = 0.95·σ_SB
·T_wg^4` → **T_wg = 2660 °R**, heat flux = 0.159 Btu/in²·s. (Low flux — this is why nozzle
extensions past ε ~6–10 can use radiation cooling and a cheaper/simpler material.)

`[TN-Dump]` GH2/LOX, Pc 100 psig, O/F 5: min satisfactory LH2 coolant flow 7.5 % of total
propellant flow (uncoated 304 SS wall, 2000 °R flame-side limit); 6.9 % with 0.033-in Al2O3.

**Near-injector under-heating — CFD-side corroboration** `[SECA-HT §4, ~p.58]`: a SSME
conjugate-heat-transfer CFD study (FDNS Navier-Stokes solver) found the same near-injector
wall-heat-flux reduction that `[TN-Dump]` measured empirically, though the three prior CFD
predictions it compares disagree on the *cause* (film cooling / combustion kinetics /
finite-rate vaporization). Two independent sources — one hardware test, one CFD — agreeing
on the phenomenon (not the mechanism) strengthens confidence in treating "combustion takes a
finite length to complete near the injector" as physically real, which is what motivates
`cooling.py`'s length-decaying `film_effectiveness_profile`. **Caveat**: `[SECA-HT]` is a
CFD-methodology report, not a correlation source — it has no Bartz/Dittus-Boelter-type
formula or calibration constant of its own (confirmed by an explicit text search: zero hits
for "Bartz," "Dittus," "Reynolds," "Prandtl," "Stanton," or "recovery factor" outside
citations to unavailable works). It cannot be used to derive or spot-check `cooling.py`'s
`BARTZ_ABS_FLUX_CALIBRATION` — treat it as qualitative/corroborating evidence only.

A related `[SECA-HT §4.3, ~p.70]` finding: a film-cooled RP-1/O₂ CFD case predicted correct
wall heating right at injection but found the film "mixes too fast" further downstream —
i.e. even a purpose-built CFD tool finds film-cooling *decay length* harder to predict than
near-injection effectiveness. Relevant context (not a portable number) for the shape of
`film_effectiveness_profile`'s length-decay assumption.

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
- `[SECA-HT]` has no coolant-channel correlation of its own and self-reports several of its
  own validations as qualitative rather than quantitatively verified — don't treat its
  "predicted well" statements as equivalent to a validated correlation.
- `[Marquardt-5981]`'s numbers are small-spacecraft-engine scale (20–10,000 lbf, mostly
  <300 psia) and its actual sizing method is 11 hand-drawn parametric weight/feasibility
  graphs that are **not OCR-extractable** — only the discrete numbers quoted in body text
  and figure captions (above) are usable; don't infer curve shapes from it. 1963 vintage:
  named materials (Type 321 SS, columbium, Ta-10W) predate modern channel-wall alloys.
- `[SP-8087]` is 1972-vintage and explicitly pre-advanced-channel-wall (its own introduction
  says high-heat-flux non-tubular chambers were "in development" and "not covered in detail")
  — its double-wall/channel-wall content describes only simple small-engine implementations,
  not modern milled-liner or Russian sandwich-wall practice. Real numbers (heat-flux
  thresholds, taper ratios, velocity limits) are recommended practices from designer
  experience, not universal physical limits, per the monograph's own framing.
- `[Wieseneck-J2]` is a Rocketdyne viewgraph-style presentation (no formal report number
  found) with most actual charts OCR-unreadable — only body-text captions were usable; its
  "double wall" reference is the same generic Western category as `[SP-8087]`'s, not Russian
  sandwich construction. Pre-hardware SSME design-point projections (~1970), not flight data.
- `[EUCASS-2023]` and `[Fagherazzi-2019]` are both small-engine (4 kN / 250-400 N) single-team
  papers, one tier below a NASA design-criteria monograph or real-engine data — treat their
  own novel numerical claims (15-22% ΔP rule, 20% radiative split, CHF margins) as
  small-engine-scale data points to corroborate against, not universal constants. Neither has
  any manifold-design content (checked specifically) — both only model flow inside the
  channels, not distribution to/from them.
- `[Merkle-RegenCFD]`, like `[SECA-HT]`, is a CFD-methodology demonstration, not a
  correlation source — cannot be used to derive or spot-check `BARTZ_ABS_FLUX_CALIBRATION`.
  Its geometry (640 uniform passages, water surrogate, non-reacting hot gas, 100mm length) is
  idealized, not a real engine; none of its numbers should be cited as real-hardware data.
- `[Lewis-Deposits]` is a standalone electrically-heated test-tube rig (not a firing engine),
  fixed 10-minute exposure only — its deposit-rate magnitudes are not directly extrapolable
  to a real engine's full burn duration. `[TP2862-LOXRP1]`'s "~60% higher than design
  prediction" finding is a comparison against another paper's design tool, not a from-scratch
  Bartz recompute, and its OCR-garbled figures mean only prose-restated numbers are trusted
  here (no tabulated axial heat-flux profile was extractable). `[STBE-PW]`'s channel-geometry
  guideline set is stated but never cited to an external standard — read as in-house period
  practice, not a universally validated design criterion. `[ChannelWall-IAC19]` has no
  heat-transfer or structural design method at all (pure manufacturing-process/test-campaign
  survey) — cannot calibrate or validate anything in `cooling.py`.

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
  2026-09-23 — film stopped being a section method; see the film-overlay bullet below.)
- **`cooling_transition_eps` default 6.0**: directly `[Sutton §8.2 p.286]` — "radiation
  cooling is used ... for diverging nozzle exhaust sections beyond an area ratio of about
  **6 to 10**." The tool's default of 6 is the conservative (earlier-transition) end of the
  cited range. Well-supported; ASSUMPTIONS.md item #37 can cite this.
- **Regen Isp benefit (0.1–1.5 %)** `[Sutton §8.2]` is not modelled — a future addition
  could credit a small Isp bump for regeneratively-cooled designs.
- **`regen_nozzle_end_eps` / `cooled_length_eps` cutoff pattern** now has independent
  real-hardware precedent from `[Marquardt-5981]`'s Design Study 1 (regen to 10:1, radiation
  skirt 10:1→40:1) in addition to the existing `[Sutton]` 6-10 range — no code change implied,
  just a second corroborating source for the same architecture (report-only).
  `[Marquardt-5981]` also names a **minimum practical regen coolant-passage dimension
  (0.062 in for a small hydrazine engine)** and a restart-engine **jacket-purge
  requirement** — neither has any counterpart in `cooling.py`/`mass_model.py` today (no
  minimum-channel-size check, no purge-volume/purge-path concept at all). Both are
  small-engine-scale findings and not urgent for the thrust range `engine_designer`
  typically targets, but worth flagging if a future feature adds real coolant-channel
  geometry sizing (see also `[Sutton §8.3]`'s channel-design treatment, already flagged
  above as unread).
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
- **Coolant manifold design content lives in `topics/12-materials-and-structures.md`**
  (real numbers from `[SP-8087]`'s manifolds section and `[Fagherazzi-2019]`'s volute-sizing
  method) rather than duplicated here — this file covers heat transfer and jacket-wall
  structure; manifold inlet/outlet/turnaround design sits alongside `[SP-8120]`'s existing
  manifold-structural-supports content there.
- **Russian sandwich wall construction remains unmodeled and uncited** after this literature
  batch (see the dedicated paragraph above, now checked against 6 sources total) —
  `WALL_CONSTRUCTIONS` in `cooling.py` still only has `milled_channel`/`tube_wall`/
  `coax_shell`; a fourth "sandwich" type (many diffusion-bonded parallel channels between two
  face sheets, distinct from a single helical-wire double-wall channel) would need a
  Russian-specific source not yet acquired. Report-only — no code changed.
- **RP-1 coking limit now has real rate/onset-band data, not just a single-point temperature
  threshold** (`[Lewis-Deposits]`, `[TP2862-LOXRP1]`) — `cooling.py`'s RP-1 coking framing
  currently just uses the single `[SP-8087]` 850°F(728K) figure. If a future feature wants a
  fouling-resistance/service-life estimate rather than a binary coking-limit flag, the real
  400-600 µg/cm²·hr rate band and the non-monotonic (falls off above ~800K) shape are now
  available. Report-only — no code changed.
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
- **Film cooling as an overlay at two sites (2026-09-23)**: `[Huzel §4.4 p.98–99]`'s
  "film … alone or with regen" is now literal — film is not a section method but an overlay
  on any of them (`EngineDesign._film_phi`): the chamber curtain (face, or a convergent ring —
  the `[TP2862-LOXRP1]` injector-zoning result is the passive-film analog) and a supersonic
  nozzle-extension slot anchored on the real F-1 film start at eps 10 `[SP-8120]`, both fed
  post-jacket fuel at jacket-exit temperature. The `[EUCASS-2023 §4.2]` regen + 7 %-film case
  (peak wall 1124 → 948 K) is reproduced *in order of magnitude* by a LOX/RP-1 analog (−175 K,
  `validate.py::run_film_overlay_check`) — the near-exact match is coincidental, not a
  calibration. The decay law (`[SECA-HT §4.3]`: decay length is the hard part) and the
  product-combination rule remain Tier 3; **NASA SP-8124 is still the missing source** for a
  real film-effectiveness correlation at either site (`OPEN_QUESTIONS.md`). Hard-blocked
  material/method combos (`materials.Material.allowed_cooling_methods`) follow the
  method-selection table above: ablatives never carry a regen jacket.
