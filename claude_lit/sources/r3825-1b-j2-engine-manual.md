# R-3825-1B — Technical Manual, Operating Instructions, J-2 Rocket Engine

## Identity

- **Title**: Rocketdyne *Technical Manual — Operating Instructions, J-2 Rocket Engine*, for
  J-2 Part No. 103826, S/N J-2036-1 through J-2152 (Saturn S-II and S-IVB stages).
- **Report**: **R-3825-1B** (Rocketdyne Division, Rockwell International / North American
  Rockwell, Canoga Park), manual issued 11 July 1969 (the cover's basic date is 6 May 1970),
  through **Change No. 9 (15 March 1975)**. The file name's date, 9 May 1975, is the last
  change. The list of effective pages gives 778 pages in total.
- **Contract / accession**: none printed on the leaves read. This is the "-1B" volume of the
  R-3825 family. The **descriptive and performance data are in a different volume**,
  R-3825-1, *J-2 Rocket Engine Data Manual*, which this volume points to [J2-Man Intro §6
  p.xx, leaf 24]. Maintenance is R-3825-3, parts R-3825-4 and GSE R-3825-5.
- **File**: `literature/R-3825-1B_TECHNICAL_MANUAL_OPERATING_INSTRUCTIONS_J-2_ROCKET_ENGINE_05-09-1975.pdf`
  (792 PDF leaves, a microfiche scan with a partial OCR text layer; 298 leaves were re-OCR'd
  for this batch). The text dump is `.lit_work/text/I_j2_manual.txt`.
- **Page reference**: the manual numbers pages by section (`xv`, `1-207`, `2-31`, `3-305`),
  with inserted `A/B/C` pages, so there is **no constant printed-page-to-leaf offset**.
  Anchors: p.xv = leaf 19, p.1-207 = leaf 260, p.2-1 = leaf 265, p.2-63 = leaf 355,
  p.3-2 = leaf 359, p.3-124 = leaf 500, p.3-240 = leaf 643, p.3-285 = leaf 693,
  p.3-305 = leaves 714-716 (fold-out), p.A-1 = leaf 781. Cites below give the printed page
  and the leaf.
- **Extent read**: **TARGETED (2026-10-18)**. The brief limited the read to the open
  literature gaps (jacket manifold, injector dP, jacket outlet H2 state, turbine exhaust,
  pump discharge pressure/temperature, purge flows, heat exchanger, performance/weight,
  start/cutoff timing). Every figure cited was **read visually** from a rendered page
  image; none of the numbers come from the OCR text alone.
- Tag: **[J2-Man]**

## Character

This is an **operating-instructions** manual, not a data manual. It tells field crews what
the engine needs at its interfaces (purge gases, inlet propellant conditions, start-tank
and helium-tank charge), what it delivers at its interfaces (heat-exchanger and GH2
tank-pressurization outputs), the operating limits that trigger a cutoff, valve-timing
acceptance limits, and long procedures for checkout, leak testing, drying and handling.
It is in the same report family as `[F1-Man]` (R-3896-1). Unlike `[F1-Man]`, it has **no
hardware-description chapter and no nominal performance tables**. Those are in R-3825-1,
which is not in `literature/`.

What it is good for is real **interface envelopes** and **limits**. These are acceptance
bands (min/max PU or EMR, engine-to-engine spread), not single nominal points. They are
real Rocketdyne requirements on the flight engine, so trust them highly as bands. Do not
read a band edge as a nominal value. Two forms in §3.8 carry **illustrative entries**
(engine "J-2XXX"). These look like real test data (thrust, MR, Isp, start/cutoff times, dry
weight), but the manual presents them as form examples (Caveats).

## Interface and operating data (all read visually)

### Purges (Fig 2-1..2-4, p.2-2..2-5, leaves 266-269)

| Purge | Gas / pressure / temperature at the customer connect | Reference flow |
|---|---|---|
| Turbopump + GG (purge manifold system) | He, 82-130 psia (0.57-0.90 MPa), 50-200 °F | **6 SCFM** |
| Ox dome + GG ox injector (engine pneumatic system) | He (from engine He tank in flight), ≥600 psia (4.1 MPa), 50-200 °F | **230 SCFM** |
| **Ox turbopump intermediate-seal cavity** (engine pneumatic) | He (from engine He tank / regulator in flight), ≥600 psia, 50-200 °F | **2,600-7,000 SCIM** (≈0.12-0.32 g/s He, derived) |
| Ox dome, facility line (port CO3a), ground only | N2, 415-675 psia (2.9-4.7 MPa), 100-200 °F | 175-230 SCFM |
| Thrust-chamber jacket purge / preconditioning | He ≤200 psia, 50-200 °F (S-IVB), or ambient (S-II) | ≥80 SCFM |
| Thrust-chamber jacket purge (S-IVB ground, low pressure) | He 27-29 psia | 35 SCFM |
| Thrust-chamber jacket purge (S-II ground) | N2 165-215 psia, 100-200 °F | 100 SCFM |
| **Thrust-chamber pre-chill** (§2.1.8, p.2-15) | He ≤1,000 psia, **-420 to -300 °F** (22-89 K) | **10-25 lb/min** (0.076-0.19 kg/s) |
| Thrust-chamber diffuser (facility, test only) | N2 ≥40 °F | ≥0.1 lb/s |

Fig 2-1..2-4 also give the timing. The turbopump/GG purge must be at operating pressure
within **0.2 s of cutoff** and run ≥10 min. Ox-dome and intermediate-seal purges switch to
the engine helium tank for start, mainstage and the cutoff transient. The jacket pre-chill
runs at least 7.5 min before booster ignition and at most 30 min (stage limit) [§2.1.8
p.2-15]. Required throat temperature at start: -300 to +150 °F (S-II and S-IVB
single-start), -300 to -80 °F (S-IVB restart) [§2.1.8.f]. The static-test limit is
-300 to -150 °F jacket temperature (CS1) [Fig 2-20 sh.2 p.2-61].

### Heat exchanger outputs (§2.1.9, Figs 2-13/2-14/2-14A, p.2-15..2-30D, leaves 280-301)

The J-2 exchanger has **two stage-dependent configurations**:

- **S-IVB: two helium coils.** Cold He enters at 300-425 psia and -110 to -410 °F (later
  400±30 psia, -410±10 °F). It is heated for **ox-tank pressurization** at **0.05-0.34
  lb/s** (0.023-0.154 kg/s).
- **S-II: one LOX coil with a 0.184-in orifice**, boiling LOX to GOX at **0.8-3.0 lb/s**
  (0.36-1.36 kg/s).

| Output (at customer connect) | Low flow | High flow | Where |
|---|---|---|---|
| He outlet T, max-PU band, 10-90 s (pre-MD366/371) | 50-700 °F (283-644 K) @0.05 | -100-560 °F (200-567 K) @0.34 | Fig 2-13 sh.1, p.2-21 |
| He outlet T, min-PU band, same | 0-515 °F (255-542 K) | -150-400 °F (172-478 K) | same |
| He outlet T, ≥90 s, MD371, EMR 5.5 | 420-640 °F (489-611 K) | 260-480 °F (400-522 K) | Fig 2-13 sh.5, p.2-24A |
| He outlet T, ≥90 s, MD371, EMR 4.8 | 329-543 °F (438-557 K) | 169-383 °F (349-468 K) | same |
| He outlet P, 10-90 s | 290-425 psia (2.0-2.9 MPa) | 15-375 psia | Fig 2-13 sh.3, p.2-23 |
| GOX outlet T, ≥60 s, MD371, EMR 5.5 | 95-440 °F (308-500 K) @0.8 | -140-20 °F (178-267 K) @3.0 | Fig 2-14A sh.2, p.2-30B |
| GOX outlet T, same, EMR 4.8 | 25-318 °F (269-432 K) | -219 to -47 °F (134-229 K) | same |
| GOX outlet P, ≥60 s, MD371, EMR 5.5 | 945-1,175 psia (6.5-8.1 MPa) | 540-770 psia | Fig 2-14A sh.4, p.2-30D |
| GOX outlet P, same, EMR 4.8 | 768-998 psia | 412-642 psia | same |

Pre-MD371 S-II curves (Fig 2-14 sh.1/5) bound the same space. At 3.0 lb/s the GOX outlet
can be as cold as **-298 °F**, i.e. not fully vaporized/superheated. A PU or EMR step needs
**5 s** to settle into the band (10 s from fully closed to fully open).

### GH2 tank-pressurization tap = forward fuel manifold (Figs 2-15/15A/15B, p.2-31..2-34D, leaves 302-310)

The H2 tank-pressurization line connects to the **thrust-chamber forward fuel manifold**
[Fig 3-32 sh.14 p.3-124, leaf 500, leak points F32/F33]. The engine schematic [Fig 3-71
p.3-305, leaf 714] shows the line leaving the chamber head beside the ASI. It therefore
delivers **jacket-exit hydrogen**.

| Output (customer connect, 0.4-3.0 lb/s, flat vs flow) | Value | Where |
|---|---|---|
| GH2 temperature, max-PU band (pre-MD366/371) | -232 to -289 °F (**126.5-94.8 K**) | Fig 2-15 sh.1, p.2-31 |
| GH2 temperature, min-PU band | -278 to -340 °F (100.9-66.5 K) | same |
| GH2 temperature, MD371, EMR 5.5 / 4.8 | -232 to -289 °F / -260 to -320 °F (126.5-94.8 K / 110.9-77.6 K) | Fig 2-15A sh.3, p.2-34C |
| GH2 temperature, MD366, EMR 5.0 / 4.5 | -252 to -272 °F / -311 to -333 °F (115.4-104.3 K / 82.6-70.4 K) | Fig 2-15B sh.1, p.2-34D |
| GH2 total pressure at **zero** tap flow, 230K engines, EMR 5.5 / 4.8 | **790-925 psia** (5.45-6.38 MPa) / 690-825 psia | Fig 2-15A sh.2, p.2-34B |
| same, 225K engines, EMR 5.5 / 4.8 | 760-895 psia / 660-795 psia | Fig 2-15A sh.1, p.2-34A |
| same at 3.0 lb/s, 230K, EMR 5.5 | 645-825 psia | Fig 2-15A sh.2 |

### Engine start requirements (Figs 2-5, 2-7, 2-8, 2-9, 2-11; §2.1.6-2.1.7; leaves 272-281)

| Item | Value | Where |
|---|---|---|
| LOX inlet NPSH minimum | 26 ft (7.9 m) pre-start, 10 ft for 0-1 s after STDV, then 28 → 31.9 ft (8.5 → 9.7 m) by 3 s; 34-38.3 ft with He injection | Fig 2-5, p.2-8 |
| LOX inlet total pressure | 33-45 psia flight (0.23-0.31 MPa), ≤55 psia ground; 23 psia floor 0-1 s | Fig 2-5 |
| LOX inlet temperature | not colder than -298 °F (89.8 K) | Fig 2-5 note 3 |
| LH2 inlet NPSH minimum | 150 ft (45.7 m) pre-start, 15 ft for 0-1 s, then 155 → 164 ft (47.2 → 50.0 m) | Fig 2-9, p.2-12 |
| LH2 inlet total pressure | 27/28-38 psia flight, ≤46 psia ground; 22.5 psia floor 0-1 s | Fig 2-9 |
| LH2 inlet temperature | not colder than -424 °F (19.8 K) | Fig 2-9 note 3 |
| Flight safe-start box | fuel 27-38 psia × ox 33-45 psia | Fig 2-7, p.2-10 |
| LOX pump discharge temperature at start | ≥3 °F subcooled. Safe region -298 °F to ~-285 °F at 33-45 psia discharge (saturation -280.8 °F @35 psia, -278.5 °F @45 psia) | Fig 2-8, p.2-11 |
| Fuel recirculation (chill-down) | 0.9-2.0 lb/s, ≥3 min subcooled at the engine inlet, ≥5 min total | §2.1.5.2, p.2-10 |
| Start tank (GH2) at start | 1,200-1,400 psia, -300 to -140 °F. Restart engines: 1,325±75 psia, -170±30 °F | Fig 2-11, p.2-16 |
| Engine helium tank at start | 2,800-3,450 psia (19.3-23.8 MPa). He regulator outlet 400±25 psig | §2.1.6 p.2-11; §2.5.15 p.2-47 |

### Operating limits and timing (Fig 2-20, Fig 1-11, Fig 3-30; leaves 260-261, 352-355, 474)

| Item | Value | Where |
|---|---|---|
| Ratings named | "230K" and "225K" engines | Fig 2-20 sh.3 |
| Fuel-turbopump overspeed cutoff | **29,000 rpm** (230K) / **28,000 rpm** (225K) | Fig 2-20 sh.3, p.2-62 |
| Fuel-turbine inlet temperature (GG hi-lo cutoff) | ≥180±30 °F within 0.5 s of mainstage. **≤2,000±50 °F (1,367 K) from 0.5 to 3.5 s**, then **≤1,450±50 °F (1,061 K)** | same |
| Mainstage confirmation | 730 psia thrust-chamber pressure (sea level; reads 15 psi high from purge bias) within 10 s of STDV signal | Fig 2-20 sh.4, p.2-63 |
| Vibration safety cutoff | 150 g rms, 960-6,000 Hz, 70 ms delay, 2-of-3 voting | same |
| Start signal → ASI valve open; bleed valves closed | ≤100 ms; ≤120/200 ms | Fig 1-11 sh.1, p.1-207 |
| MFV open (signal → motion / motion) | 60±30 / 80±50 ms (110±50 post-MD333) | same |
| STDV open | 100±20 / 105±20 ms | same |
| MOV first stage / second stage (MD265) | 50±20 / 50±25 ms; 560±70 / 1,675±25 ms | same |
| GG valve (ox side) open | 140±10 / 50±30 ms | same |
| Cutoff: MOV close / MFV close | 60±15 / 120±15 ms; 90±25 / 225±25 ms | Fig 1-11 sh.2, p.1-208 |
| Cutoff: GG valve ox side close | 75-125 ms / 35 ms. Fuel poppet closed ≤500 ms, and ≥10 ms after the ox poppet | same |
| Sequence timers | start-tank discharge delay 0.640±0.030 s (1.000±0.040 MD205); ignition phase 0.450±0.030 s; sparks de-energize 3.30±0.20 s; He control de-energize 1.00±0.11 s | Fig 3-30, p.3-104 |
| **Engine service life** | **3,750 s mainstage** (STDV open → cutoff) | §2.5.7, p.2-41 |
| He-regulator cycle life | 2,000 additional cycles (post-MD333 retrofit) / 5,000 cycles (new) | §2.5.8, p.2-41 |
| Fuel-pump seal He leakage acceptance | primary ≤9-10 scim (accept up to 350); secondary ≤75 (S-II) / ≤110 (S-IVB) scim, reject >500 | Fig 1-9/1-10, p.1-206F |

### Form-example performance and weight (Figs 3-76, 3-81; leaves 753, 761)

| Item | Value | Where |
|---|---|---|
| Steady state (illustrative, "SIVB 20x" test, 60 s slice) | 225,637 lbf (1,003.7 kN), MR 5.535, Isp 420.0 s | Fig 3-81, p.3-345 |
| Same test, 400 s slice | 181,297 lbf (806.4 kN), MR 4.607, Isp 428.9 s | same |
| Start signal → mainstage initiate / → 90 % thrust | 2.616 s / 3.307 s | same |
| Max thrust build-up rate; cutoff → 5 % thrust; cutoff impulse | 6,670 lbf/10 ms; 0.680 s; 43,480 lbf·s (193 kN·s) | same |
| Dry weight, spec / as delivered (illustrative) | 3,480 lb (1,578 kg) spec / 3,420 lb (1,551 kg) net, arm +28.6 in aft of gimbal | Fig 3-76, p.3-337 |

## Key results

1. **Jacket-exit hydrogen temperature, sourced at last.** The J-2 bleeds GH2 for LH2-tank
   pressurization from the **thrust-chamber forward fuel manifold** [J2-Man Fig 3-32 sh.14
   p.3-124; Fig 3-71 p.3-305]. At the customer connect that gas is **-232 to -340 °F
   (≈67-127 K)**, flat with tap flow and set by mixture ratio. At EMR 5.5 it is 95-127 K,
   at EMR 4.8 it is 78-111 K [Fig 2-15/15A/15B p.2-31..2-34D]. Higher MR (less fuel) gives
   hotter gas. The tap line probably adds a little heat, so treat this as an
   upper-bound-ish proxy for jacket-outlet temperature. It answers `OPEN_QUESTIONS`
   "Warm-GH2 density in regen hydrolox injector-feed rings": at ~100 K and ~5.5-6.4 MPa,
   hydrogen is a warm supercritical gas, not 71 kg/m³ liquid. `manifold.py` sizes the
   J-2's fuel injector ring at liquid density. **Derived (not checked against a table):**
   the real density is several times lower.
2. **Forward fuel manifold (injector-inlet) pressure envelope.** With zero tap flow (no
   line loss) the customer-connect total pressure is the forward-manifold pressure:
   **790-925 psia (5.45-6.38 MPa) at EMR 5.5 and 690-825 psia at EMR 4.8** on 230K engines,
   and 760-895 / 660-795 psia on 225K engines [Fig 2-15A sh.1-2 p.2-34A/B]. **Derived,
   rough:** against the 787 psia Pc in `[RPE-J2Blog]`, the J-2 fuel-injector dP is roughly
   0-140 psi (0-0.95 MPa), i.e. ≲18 % of Pc. That is consistent with the
   `[Huzel]`/`[SP-8107]` 15-20 % rule and in the right range for a coax-post LH2 injector.
   This narrows `OPEN_QUESTIONS` "injector manifold pressure vs injector dP (fuel)" but
   does not close it: it is a band, and Pc is not in this manual.
3. **LOX pump discharge lower bound.** The S-II heat exchanger takes LOX from the ox
   high-pressure duct through a 0.184-in orifice [Fig 3-71]. Its GOX outlet still reaches
   **1,175 psia (8.1 MPa) at 0.8 lb/s, EMR 5.5** [Fig 2-14A sh.4 p.2-30D]. **Derived:**
   J-2 LOX pump discharge at EMR 5.5 is therefore above ~1,175 psia, ≥1.5 × Pc
   (787 psia). This only bounds `OPEN_QUESTIONS` "LOX pump discharge". The manual gives no
   fuel or LOX discharge value, only instrument ranges (fuel 0-1,500, LOX 0-1,500/2,000
   psia) [Fig 2-19 sh.1 p.2-48M].
4. **Real J-2 exhaust heat-exchanger duty, both configurations** (§2.1.9 and the table
   above). The **S-IVB J-2 heats cold helium in two coils** (0.05-0.34 lb/s, -410 °F in →
   up to 700 °F out, 300-425 psia). The **S-II J-2 boils LOX in one coil** (0.8-3.0 lb/s,
   out at -298 to +440 °F). This corrects the "LOX-only" J-2 picture in `topics/07`
   (sourced to `[RPE-J2Blog]`): the S-IVB engine is a helium heater. Together with
   `[F1-Man]` (LOX + He in one shell) and `[H1-Man]` (LOX only), there are now four real
   exchanger configurations. These are second anchors for `turbine_exhaust.LOX_TO_GOX_DH_J_KG`
   / `HE_HX_DH_J_KG`. Still missing: **no size, coil area or weight**
   (`HX_MASS_SHELL_MULT` stays Tier 3).
5. **Real purge flows for the inter-propellant seal and helium budget.** The **LOX-turbopump
   intermediate-seal cavity purge is helium at ≥600 psia, 2,600-7,000 SCIM**
   (≈0.12-0.32 g/s, derived), supplied in flight by the engine's own helium tank
   [Fig 2-1/2-4 p.2-2/2-5]. Turbopump + GG purge: 6 SCFM He at 82-130 psia. Ox dome + GG
   ox injector: 230 SCFM He at ≥600 psia, only for the 1 s cutoff transient and fuel lead
   in flight. Jacket pre-chill: 10-25 lb/min cold He. The engine helium tank holds
   2,800-3,450 psia at start. This closes `OPEN_QUESTIONS` "Seal purge flow rates
   (2026-09-26)" for one real LOX/LH2 engine, the number Round 4 seals needs to cost a
   helium purge. Cross-check `[SP-8121]`'s J-2 seal table: J-2 turbine segmented carbon
   seal at 20 SCFM (`topics/09` line ~289).
6. **Real J-2 engine life number.** **Service life 3,750 s of mainstage** [§2.5.7 p.2-41].
   That is 7.5 × the ~500 s S-IVB/S-II flight duty `[RPE-J2Blog]`, a real duty-to-life
   ratio for `physics/burn_time.py` / `topics/17` alongside `[Vilja-J2S]`'s 11,509 s on one
   J-2S. Component lives also given: He-regulator 5,000 cycles, start-tank fracture-mechanics
   pressure-cycle life [§2.5.15A].
7. **Turbine-inlet temperature limits.** The fuel-turbine inlet (= GG outlet) is allowed
   **2,000 ± 50 °F (≈1,370 K) for 3 s of start, then 1,450 ± 50 °F (≈1,060 K)** in
   mainstage [Fig 2-20 sh.3 p.2-62]. This is a real hot-gas ceiling for an LH2-fuel-rich GG
   turbine, comparable to the F-1's 1,453 °F inlet `[F1-Man]`, and a spot-check value for
   GG-Tin defaults on LOX/LH2. Fuel-pump overspeed cutoff: 29,000 / 28,000 rpm, vs
   `[SP-8125]`'s 28,266 rpm design speed.
8. **Real suction requirements for both J-2 pumps.** LOX NPSH 26 ft pre-start and
   28-31.9 ft in mainstage. LH2 NPSH 150 ft pre-start and 155-164 ft in mainstage, both
   with a 1 s post-STDV relaxation to 10 / 15 ft [Fig 2-5/2-9]. These are flight interface
   minima, a direct check on `inducer.py` / `suction_stage.py` NPSH-required for the J-2
   corpus engine, next to `[SP-8107]`'s J-2 H2 130/75 ft (`topics/09` line ~67).
9. **Start/cutoff valve timing in ms.** Full Fig 1-11 / Fig 3-30 table above. Start to 90 %
   thrust 3.307 s and cutoff to 5 % 0.680 s (form example) [Fig 3-81]. This adds real J-2
   numbers to `topics/15`'s qualitative J-2 start description (`[SP-8107 §2.3.2.1]`).

## Design method

None. The manual gives interface requirements and acceptance bands, not design equations.
The one quantitative method is the start-tank **fracture-mechanics pressure-cycle-life
procedure** [§2.5.15A, p.2-47..2-48K: cycle counting from Pmin to Pmax, cycles below 150
psig range ignored, flaw-growth-rate charts per tank vendor]. It concerns a pressure vessel
and was not read in detail.

## Section map

- Front matter: TOC, list of illustrations (leaves 4-18) — Read visually (TOC).
- Introduction §1-6, Figs 1-6 (p.xv-xxiii, leaves 19-28) — Read (manual family, MD system,
  Fig 5 engine photo).
- **Section I, Operating Requirements** (p.1-1..1-211, leaves 29-264):
  - Figs 1-1/1-2 scheduled / nonscheduled field activities (p.1-2..1-9) —
    **as-needed - not read (2026-10-18)**: activity/constraint tables.
  - §1.1 inspections, §1.2 electrical tests, §1.3-1.5 leak/functional checks, §1.6 covers
    (p.1-10..1-195, leaves ~37-240) — **as-needed - not read (2026-10-18)**: field
    inspection and checkout activity tables.
  - Figs 1-3..1-8E damage limits, transducer voltage limits, solenoid resistances
    (p.1-198..1-206E, leaves ~241-258) — **as-needed - not read (2026-10-18)**:
    maintenance acceptance limits.
  - Figs 1-9/1-10 fuel-turbopump seal He leakage limits (p.1-206F, leaf 259) — Read visually.
  - Fig 1-11 valve operating time limits (p.1-207/208, leaves 260-261) — Read visually.
  - Fig 1-12 MOV second-stage ramp time vs orifice flow; Figs 1-13/1-14 drying limits
    (p.1-209..1-211, leaves 262-264) — **as-needed - not read (2026-10-18)**.
- **Section II, General Requirements** (p.2-1..2-64, leaves 265-357):
  - §2.1.1-2.1.3 fluid/pressurant specs and purge requirements, Figs 2-1..2-4 (leaves
    265-269) — Read visually.
  - §2.1.3.6-2.1.5 start-tank purge, ox/fuel feed conditioning (leaves 270-271, 275) —
    Read (fuel conditioning) / skimmed.
  - Figs 2-5, 2-7, 2-8, 2-9 start requirements (leaves 272, 275-277) — Read visually.
  - Figs 2-6/2-6A ox inlet temperature vs pressure; Fig 2-10 fuel inlet temperature vs
    pressure (leaves 273-274, 278) — **as-needed - not read (2026-10-18)**: inlet
    subcooling envelopes.
  - §2.1.6-2.1.8 helium tank, start tank, thrust-chamber pre-chill; Fig 2-11 (leaves 276,
    279-281) — Read visually.
  - Fig 2-12 start-tank max pressurization rate (leaves 282-285) — **as-needed - not read
    (2026-10-18)**: ground-fill rate charts.
  - §2.1.9 / Figs 2-13, 2-14, 2-14A heat-exchanger outputs (leaves 280, 286-301) — Read
    visually (sheets 2-13 #1/3/5, 2-14 #1/5, 2-14A #1/2/4; the rest checked via OCR only).
  - §2.1.10 / Figs 2-15, 2-15A, 2-15B fuel-tank pressurization (leaves 302-310) — Read
    visually (2-15 #1/3, 2-15A #1-3, 2-15B #1).
  - §2.2 electrical requirements (leaves 305, 311) — **as-needed - not read (2026-10-18)**:
    AC/DC power, PU valve and MRCV electrical.
  - §2.3-2.4 environmental/desiccant, maintenance (seals, fasteners, torque, lockwire)
    (leaves 312-315) — **as-needed - not read (2026-10-18)**.
  - §2.5.1-2.5.6 safety directives (leaves 315-317) — **as-needed - not read (2026-10-18)**.
  - §2.5.7-2.5.8 engine and component service life (leaf 317) — Read visually.
  - §2.5.9 gimbal limitations, Fig 2-17 (leaves 318-320) — **as-needed - not read
    (2026-10-18)**: gimbal-bearing and inlet-duct cycle-life chart.
  - §2.5.10-2.5.14 checkout after storage, exit igniters, film-cooled diffuser, side-load
    arm, restart requirements (leaves 321-324) — **as-needed - not read (2026-10-18)**.
  - §2.5.15-2.5.15A helium regulator, start-tank pressure-cycle life, Figs 2-18..2-18F
    (leaves 325-336) — Skimmed (leaf 325 read visually).
  - §2.5.16A flight operation constraints (leaf 337) — **as-needed - not read (2026-10-18)**.
  - Fig 2-19 static-test instrumentation list with calibration ranges (leaves 338-349) —
    Read visually (sheets 1, 4, 7, 8, 10, 11). Ranges only, no operating values.
  - §2.5.18 / Fig 2-20 static-test operating limits (leaves 350-355) — Read visually.
  - §2.6-2.7 documentation, applicable specifications (leaves 356-357) — **as-needed - not
    read (2026-10-18)**.
- **Section III, Operating Procedures** (p.3-1..3-363, leaves 358-780):
  - §3.1-3.2 inspection and uninstalled-engine checkout (leak, flow, sequence, GG/exhaust,
    thrust-chamber tests; p.3-2..3-110, leaves 358-~480) — **as-needed - not read
    (2026-10-18)**, except Figs 3-29/3-30 recorder assignments and timer times (leaves
    473-474), Read visually.
  - Fig 3-32 engine leak-test points (p.3-111..3-124, leaves ~487-500) — sheet 14 (leaf 500)
    Read visually: it locates the H2 tank-pressurization tap on the forward fuel manifold.
  - §3.3 stage-installed engine tests (p.3-110..3-238, leaves ~480-642) — **as-needed -
    not read (2026-10-18)**.
  - §3.4-3.5 storage/shipment, servicing and drying (p.3-239..3-284D, leaves 643-692) —
    **as-needed - not read (2026-10-18)**.
  - §3.6 handling, installation, film-cooled diffuser (p.3-285..3-304, leaves 693-712) —
    **as-needed - not read (2026-10-18)**.
  - §3.7 Fig 3-71 engine (fluid) schematic (p.3-305, fold-out, leaves 714-716) — Read
    visually: purge orifices 0.024 in nom, fuel-pump primary-seal purge 0.013 in, HX ox
    orifice 0.184 in, OTBV/turbine bypass duct, H2 tank-pressurization tap.
  - §3.7 Fig 3-72 electrical schematic (p.3-306+, 24 sheets, leaves 713, 717-~740) —
    **as-needed - not read (2026-10-18)**.
  - §3.8 log book, Figs 3-73..3-96 forms (p.3-329..3-363, leaves ~741-780) — Figs 3-76
    (leaf 753) and 3-81 (leaf 761) Read visually. Other forms **as-needed - not read
    (2026-10-18)**.
- Appendix: manual data supplements (p.A-1.., leaves 781-791) — **as-needed - not read
  (2026-10-18)**: change log.

## Caveats

- **This volume does not answer most of the hardware-geometry gaps it was pulled for.**
  The data manual R-3825-1 (not in `literature/`) is the right source for these. Not found
  here:
  - the **jacket fuel-inlet manifold area ratio and bore**: the manual names only a "thrust
    chamber fuel inlet manifold" and a "forward fuel manifold" as leak points;
  - **tube count or geometry**;
  - **jacket dP**;
  - **ox-turbine exit pressure** or exhaust-manifold pressure: only an instrument range
    TG4 0-100 psia, so the exit pressure is below 100 psia;
  - **eyelet count/area**, **exhaust duct diameter** or **manifold area law**;
  - **fuel-pump discharge pressure** (instrument range 0-1,500 psia only) and **pump
    discharge temperatures in mainstage** (only the LOX start-condition Fig 2-8);
  - **heat-exchanger size or weight**;
  - **nominal Pc/MR/flows/pump speeds/GG conditions**.
  These stay open. Point `OPEN_QUESTIONS` at R-3825-1 instead of R-3825-1B.
- **Bands, not nominals.** Every interface curve is a min/max-PU (or EMR 4.8 vs 5.5)
  acceptance envelope including engine-to-engine spread. Use band centres with care.
  "Customer connect" values sit downstream of engine-side lines and orifices: GH2 tap
  temperatures and pressures approximate the forward manifold only roughly, and HX outlet
  pressures sit downstream of the 0.184-in orifice.
- **Form-example numbers (Fig 3-76, 3-81).** The manual shows these as worked entries on
  blank forms for engine "J-2XXX". They are plausible (225.6 klbf at MR 5.535 and Isp
  420.0 s, then 181.3 klbf at MR 4.607 and Isp 428.9 s, matching the J-2's real PU shift),
  but cite them as illustrative, not as a specific engine's acceptance data. The column
  header says "KIPS" while the entries are in lbf.
- **Derived numbers.** These are this note's own arithmetic, not the manual's: unit
  conversions, the fuel-injector dP estimate (uses `[RPE-J2Blog]`'s 787 psia Pc), the LOX
  discharge ≥1,175 psia bound, and the SCIM → g/s purge conversion (He at ~0.166 kg/m³
  standard density, basis of "SCIM" not stated).
- **Configuration dependence.** Values change with MD (modification) numbers: MD366/MD371
  (two-position MRCV replacing the PU valve), MD333, MD265 and others. The tables cite the
  variant each value belongs to. Fig 2-13/2-14 sheets not listed in the Section map were
  only OCR-checked.
- Overlap, cross-links:
  - `[RPE-J2Blog]`: Pc 787 psi, 180/360 tubes, 115 in² eyelets, GH2 bleed "from the fuel
    manifold". This manual confirms the bleed point by leak-test code.
  - `[Wieseneck-J2]`: J-2 heat flux and tube lineage.
  - `[SP-8110]`: J-2 turbines.
  - `[SP-8125]`: Mk 15-F LH2 pump.
  - `[SP-8121]` / `[SP-8048]`: J-2 seals and bearings.
  - `[AEDC-J2S]` / `[Vilja-J2S]`: J-2S.
  Nothing here duplicates those notes' numbers.
