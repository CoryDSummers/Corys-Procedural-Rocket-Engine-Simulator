# AIAA 93-2129 — J-2S Rocket Engine

## Identity

J. O. Vilja, G. L. Briley & T. H. Murphy (Rockwell International Corp., Rocketdyne Division,
Canoga Park CA), *J-2S Rocket Engine*, **AIAA 93-2129**, AIAA/SAE/ASME/ASEE 29th Joint
Propulsion Conference, Monterey CA, June 1993. DOI 10.2514/6.1993-2129. The production-restart
study it reports was MSFC contract **NAS8-39210**. `literature/vilja1993.pdf` (filename kept as
delivered; md5 9de1c396...; **6 PDF leaves**: leaf 0 = AIAA cover, leaves 1-5 = printed pp.1-5,
so printed page = leaf number). Tag: `[Vilja-J2S]`.

The "J-2X" in this paper is the **1960s J-2X tap-off test bed** (a modified J-2), not the 2000s
GG-cycle J-2X of `[J2X-Overview]` (`sources/j2x-upper-stage-engine.md`).

## Character

A short **retrospective overview paper** written by Rocketdyne 20+ years after the program, to
pitch the J-2S for 1990s launch-system studies. Prose plus one schematic (Fig. 2), one
tap-off-manifold sketch (Fig. 3), a J-2 vs J-2S feature comparison (Fig. 4), a test log
(Table 1) and a performance-options table (Table 2). It gives **no** cycle-balance numbers: no
tap-off flow, no turbine inlet temperature or pressure, no pump discharge pressures, no
efficiencies.

It is best for:
- the **headline rated parameters** (thrust, Isp, Pc, eps, weight, envelope) from the
  manufacturer;
- the **cycle topology** (Fig. 2: tap-off → hot-gas valve → fuel turbine → oxidizer turbine in
  series with a bypass orifice → nozzle injection);
- the **throttling and idle-mode mechanisms**;
- **Isp vs expansion ratio** at fixed MR, at two thrust levels.

The text layer is a good NTRS/AIAA OCR. Both tables, Fig. 2, Fig. 3 and the leaf-1 headline
paragraph were **read visually** from rendered page images, and every number below was checked
against the image. Read in full.

## Rated parameters and performance options

**Headline (text)** `[Vilja-J2S p.1]`, J-2 values in the second column as the paper gives them:

| Item | J-2S | J-2 (per this paper) |
|---|---|---|
| Vacuum thrust | 1,178.8 kN (265,000 lbf) | 1,023.1 kN (230,000 lbf) |
| Vacuum Isp | 436 s | **427 s in the text, 425.0 s in Table 2** (internal inconsistency) |
| Expansion ratio | 40 | 27.5 |
| Chamber pressure | **8.27 MPa (1,200 psi)** | 5.17 MPa (750 psi) |
| Cycle | main-chamber **tap-off** | gas generator |
| Envelope | "physically an identical replacement of the J-2" | — |

**Table 2, "J-2S Provides a Range of Performance Options"** `[Vilja-J2S Table 2, p.5]`. All Isp
values are at MR 5.5. Read visually.

| Column | eps | Vac thrust | Vac Isp (s) | Weight w/ accessories | Length from gimbal plane | Exit dia |
|---|---|---|---|---|---|---|
| J-2 baseline | 27.5 | 1,023.1 kN (230K lbf) | 425.0 | 1,566.7 kg (3,454 lb) | 2.946 m (116 in) | 2.032 m (80 in) |
| **J-2S baseline** | **40** | **1,178.8 kN (265K)** | **436.0** | **1,723.7 kg (3,800 lb)** | 2.946 m (116 in) | 2.032 m (80 in) |
| J-2S nozzle replacement | 80 | 1,212.1 kN (272.5K) | 448.3 | 1,703.2 kg (3,755 lb) | 4.369 m (172 in) | 2.845 m (112 in) |
| J-2S nozzle replacement | 105 | 1,223.3 kN (275K) | 452.8 | 1,748.6 kg (3,855 lb) | 4.978 m (196 in) | 3.251 m (128 in) |
| J-2S uprated | 40 | 1,423.4 kN (320K) | 434.5 | 1,868.8 kg (4,120 lb) | 2.946 m (116 in) | 2.032 m (80 in) |
| J-2S uprated | 80 | 1,456.8 kN (327.5K) | 446.8 | 1,832.5 kg (4,040 lb) | 4.369 m (172 in) | 2.845 m (112 in) |
| J-2S uprated | 105 | 1,467.9 kN (330K) | 451.4 | 1,905.1 kg (4,200 lb) | 4.978 m (196 in) | 3.251 m (128 in) |

The uprated Pc is not given.

**Derived values (this note's arithmetic, not stated in the paper):**
- Baseline mass flow = 265,000 / 436 = 607.8 lb/s = **275.7 kg/s**.
- Baseline thrust/weight = **69.7**.
- With `[AEDC-J2S]`'s 12.192 in throat, vacuum CF = F / (Pc·At) = **1.89**.

**Test log** `[Vilja-J2S Table 1, p.4]` (production configuration only). Read visually; the
rows sum to the totals.

| Engine | Stand | Tests | Tank-head idle pre-M/S (s) | post-M/S (s) | Powered idle (s) | Main stage (s) |
|---|---|---|---|---|---|---|
| J111 | Delta-2A | 29 | 1,503.1 | 30.0 | 0 | 827.0 |
| J111 | AEDC J-4 | 5 | 592.8 | 0 | 0 | 34.0 |
| J112 | Delta-2A | 24 | 160.0 | 0 | 0 | 4,298.4 |
| J112 | AEDC J-4 | 57 | 3,649.1 | 59.3 | 252.4 | 352.6 |
| J113 | Delta-2A | 99 | 190.0 | 40.0 | 0 | **11,508.8** |
| J114 | Delta-2A | 19 | 0 | 0 | 0 | 4,445.4 |
| J115 | Delta-2A | 3 | 0 | 0 | 0 | 402.5 |
| J115 | AEDC J-4 | 14 | 478.1 | 11.1 | 0 | 332.2 |
| J116 | Delta-2A | 23 | 0 | 0 | 0 | 1,691.9 |
| **Totals** | | **273** | 6,573.1 | 140.4 | 252.4 | **23,892.8** |

The grand total is 6,713.5 tank-head idle + 252.4 powered idle + 23,892.8 main stage =
**30,858.7 s**, which matches the text's "273 times for a total of 30,858 sec". That total
excludes **10,756 s on the J-2X test bed** `[Vilja-J2S p.3]`.

## Key results

1. **Tap-off cycle, stated in one sentence** `[Vilja-J2S p.1]`: "Hot gas from the main chamber
   is **diluted with cold hydrogen** to achieve the desired turbine inlet temperature. After
   expansion in the turbines, the hot gas is injected into the nozzle downstream of the throat,
   the same as the hot gas in the J-2 gas generator cycle engine."
   - So the J-2S drive gas is **chamber gas plus extra cold H2**. That is a dilution scheme, not
     raw chamber gas at chamber MR.
   - The paper does not say where the dilution happens. It could be a fuel-rich near-wall zone or
     film at the tap station, or a separate mixing flow. Fig. 2 draws **no separate mixer**: the
     tap-off manifold goes straight to the hot-gas valve and on to the fuel turbine.
   - It gives **no tap-off temperature, pressure or flow fraction**.
2. **Tap-off port hardware** `[Vilja-J2S p.1, Fig. 3 p.2]` (read visually).
   - The tap-off ports are "the only additional complexity" over the J-2. They were added to the
     combustion chamber and **hand brazed** on the test engines; production would use "a less
     labor-intensive casting".
   - Fig. 3 shows a cutaway **ring manifold** with a single circumferential row of small, evenly
     spaced round ports on its inner face (about 20 are visible across the half-ring drawn) and
     one flanged outlet duct. The total port count, port diameter and axial station are **not
     stated**.
   - Fig. 2 draws the tap at the forward (injector-end) part of the chamber.
   - The production-restart study lists the **tap-off manifold** among the parts to convert to
     castings `[p.4]`.
3. **Series turbines, confirmed by schematic** `[Vilja-J2S Fig. 2, p.2]` (read visually). The
   gas path is tap-off manifold → **Hot Gas Valve** → fuel turbine (two rows drawn) → crossover →
   **oxidizer turbine** (two rows drawn) → nozzle exhaust manifold on the bell.
   - A fixed **Bypass Orifice** sits in parallel with the oxidizer turbine. Part of the
     fuel-turbine exhaust skips the ox turbine; this is `[AEDC-J2S]`'s "Fuel Turbine Exhaust
     Bypass Duct".
   - The **SPGG** (solid-propellant gas generator) discharges into the fuel-turbine inlet.
   - Fuel path: fuel pump → **Main Fuel Valve** → jacket inlet manifold at a mid-nozzle station
     → tubes → injector. The turbine exhaust enters the nozzle at that same station, on the
     opposite side, as on the J-2.
   - A **Fuel Bypass Valve** branches off the main fuel line up to the chamber head. This matches
     `[AEDC-J2S]`'s thrust-chamber bypass (fuel around the tubes in idle), but the paper does not
     say what it is for, and does not say whether it supplies the tap-off dilution H2.
   - Oxidizer side: a **Propellant Utilization Valve** (LOX discharge → pump inlet), the **Main
     Oxidizer Valve**, and an **Idle Mode Valve** feeding a separate ox-dome manifold.
   - The two turbines are drawn on separate shafts, each pump direct-driven by its own turbine.
4. **Throttling is done on the hot gas** `[Vilja-J2S p.2]`. "Throttling was accomplished by
   modulating the tapoff valve."
   - This was simple because "gas generator flammability limit concerns were not applicable in
     this cycle".
   - The hot-gas throttling valve was not hard to produce, since it "was not required to
     completely seal at closure".
   - **6:1 throttling was demonstrated** at AEDC J-4 (also p.3).
   - The J-2X (2000s) instead throttles with a LOX-turbine bypass on a GG cycle `[J2X-Overview]`.
5. **Idle mode** `[Vilja-J2S p.2]`. Idle is a **pressure-fed** mode, meant for a propellant
   settling burn and rapid thermal conditioning.
   - It was kept stable by "only supplying liquid oxidizer to the **inner rows** of the main
     injector by way of a separate manifold in the oxidizer dome". Shrinking the effective
     oxidizer orifice area gave stable combustion **as low as 26.7 kN (6,000 lbf)**, about
     2.3 % of rated thrust (this note's arithmetic).
   - Hydrogen went to **all** injector elements, giving enough film cooling that "no chamber
     erosion was observed".
   - Table 1 separates **tank-head idle** (6,713.5 s total, mostly before main stage) from
     **powered idle** (252.4 s, one engine, at AEDC). The text does not explain the difference.
   - Compare `[AEDC-J2S]`'s nominal 5,000 lbf / MR 2.5 idle with its "full-face oxidizer"
     configuration. The two papers describe **different idle ox-injection configurations**
     (inner rows vs full face), presumably different stages of development.
6. **The J-2 to J-2S simplifications** `[Vilja-J2S p.1, Fig. 4 p.3]`:
   - SPGG multiple start replaces the H2 spin-start bottle; it was tested in simulated
     three-start missions.
   - The tap-off turbine drive replaces the gas generator.
   - No engine bleeds and no recirculating valves.
   - **Zero NPSP**, versus the J-2's NPSP "start box".
   - 16 vehicle-engine interfaces, versus 26 on the J-2.
   - Bellows were removed from the high-pressure cryogenic ducts.
   - A **"single stage centrifugal" fuel pump** replaces the J-2's axial LH2 pump, giving
     "greater operating range and greater insensitivity from propellant inlet condition
     excursions" and a much simpler chill. `[AEDC-J2S]` calls the same pump "1.5-stage
     centrifugal", probably counting the inducer as a half stage.
7. **Development economy** `[Vilja-J2S p.3]`. Six engines, 273 tests and 30,858 s were enough to
   enter flight certification, against 31 development engines for the J-2. Sea-level testing
   was at SSFL (Delta-2A) and altitude testing at AEDC J-4.
   - SSFL testing found and fixed a **"fluid dynamic coupling phenomenon" at 4,400 Hz**.
   - One engine (J113) logged **11,508.8 s main stage in 99 tests** (Table 1). That is a real
     single-engine accumulated-duty point relevant to `physics/burn_time.py`'s tested-life
     framing.
8. **Uprating** `[Vilja-J2S p.4, Table 2]`. Raising turbomachinery output (Pc) takes the engine
   to **"over 320,000 lb" vacuum with only minor modifications**. These are:
   - stronger turbine blades and manifolds, oxidizer volute and impeller, and fuel pump volute;
   - stronger turbine-exhaust gas manifolds and main valve housings;
   - thrust-chamber forward manifolds changed to **Inconel 718**;
   - larger main-valve actuators.

   "Greater tapoff flows are readily available to provide the increased turbopump power
   requirements without perturbing the basic operation of the remainder of the engine cycle."
   At eps 40 the uprated engine **loses 1.5 s Isp** (436.0 → 434.5 s) despite its higher Pc.
   That is consistent with a larger tap-off/turbine-flow fraction, though the paper does not
   say so explicitly.
9. **Isp vs expansion ratio at MR 5.5** `[Table 2]`:
   - baseline: 436.0 (eps 40) / 448.3 (eps 80) / 452.8 (eps 105);
   - uprated: 434.5 / 446.8 / 451.4.

   A 105:1 nozzle "would match the specific impulse performance of the SSME". These are
   manufacturer predictions for the nozzle options; only the eps-40 baseline is test-backed.
10. **Production restart** `[Vilja-J2S pp.3-4]`. The engine could be built "from existing
    drawings"; "no material changes were required", and only the electronics needed updating.
    - Producibility upgrades: castings for manifolds (incl. the tap-off manifold), die forgings
      and NC machining.
    - First production engines 4 years after go-ahead, with a six-engine demo/cert program.

## Section map

- Leaf 0: AIAA cover. Read.
- p.1 (leaf 1): Abstract, Introduction, Engine Description (headline parameters, tap-off
  principle, centrifugal fuel pump, SPGG start, tap-off ports); Fig. 1 photo (sea-level
  hot-fire). Read; headline paragraph read visually.
- p.2 (leaf 2): Fig. 2 engine schematic, Fig. 3 tap-off manifold sketch, throttling and
  idle-mode paragraphs. Read visually.
- p.3 (leaf 3): Fig. 4 J-2 vs J-2S feature comparison, Engine Development Program, Production
  Restart (start). Read visually.
- p.4 (leaf 4): Table 1 test log, Production Restart (end), Engine Uprating Potential. Read;
  Table 1 read visually.
- p.5 (leaf 5): Table 2 performance options, Conclusions. Read; Table 2 read visually.

No references list.

## Caveats

- **An overview paper, not a design report.** It has no cycle-balance data: no tap-off
  temperature, pressure or flow fraction, no turbine or pump numbers, no c*, no jacket or tube
  data. For those, use `[SP-8110 Table I]` (J-2S Mark 29 fuel turbine 1,200 °F / 889 psia /
  PR 7.30 / 46.0 %; ox turbine 740 °F / 100 psia / PR 2.68 / 56.1 %;
  `sources/sp8110-turbines.md`) and `[AEDC-J2S]` (pump head/flow/rpm, 180/360 tubes, test
  c*/Isp).
  - This paper does not confirm or contradict SP-8110's turbine numbers.
  - It does supply the **1,200 psi Pc** that SP-8110's 889 psia turbine inlet can be compared
    against: 889/1,200 = **0.74 × Pc** at the fuel-turbine inlet (cross-source arithmetic; the
    SP-8110 rating point may not be the 265K point, since its 28,000 rpm differs from
    `[AEDC-J2S]`'s 29,800 rpm at 265K).
- **Pc 1,200 psi resolves `[AEDC-J2S]`'s flagged "Pc too high" caveat.** AEDC's measured
  1,182-1,279 psia main-stage Pc agrees with this rated 1,200 psi. The "~700-850 psia" figure
  that `topics/08-engine-cycles.md` cited for the J-2S (now `08b-tap-off-cycle.md`, corrected 2026-10-18) is a J-2-class number (750 psi here). RO's
  `Engine_Configs/J2_Config.cfg` J-2S header gives 8.58 MPa (1,244 psia, from Sutton's *History*),
  3.7 % above this paper.
- **Internal inconsistencies:**
  - J-2 Isp is 427 s in the text but 425.0 s in Table 2.
  - The text says the 105:1 engine would be "40 in. longer and 34 in. wider", but Table 2 gives
    +80 in length (196 vs 116) and +48 in exit diameter (128 vs 80) for 105:1. Neither 80:1
    (+56 / +32) nor 105:1 matches the text exactly.
  - Table 2 weights are not monotonic: the 80:1 nozzle-replacement engine (3,755 lb) is lighter
    than the 40:1 baseline (3,800 lb), and the uprated 80:1 (4,040) is lighter than the uprated
    40:1 (4,120). This may reflect a different extension construction; it is unexplained.
- **Weight vs RealismOverhaul:** this paper's J-2S is **3,800 lb (1,723.7 kg) with
  accessories**, heavier than the J-2's 3,454 lb (1,566.7 kg). The J-2 figure matches RO's J-2
  dry mass exactly. RO's J-2S config instead uses massMult 0.9366 → 1,467.4 kg, with the header
  comment "mass w/o accessories? lighter than standard J-2 makes more sense anyway".
  **Resolved 2026-10-18:** `[J2S-Restart leaf 8]` gives a basic dry weight of 3,235 lb
  (1,467.4 kg) and 3,800 lb with accessories. RO's mass is exactly the basic dry weight, so the
  guess was right and there is no contradiction.
- **Idle thrust vs RO:** RO's J-2S throttleCurve holds idle at 5 % thrust (13,250 lbf). This
  paper gives stable idle down to 6,000 lbf (about 2.3 %) and `[AEDC-J2S]` gives 5,000 lbf
  nominal (about 1.9 %). But `[J2S-Restart leaf 19]` calls normal idle "approx. 5 %", with a
  "powered idle" developed between that and 6:1. So RO's 5 % is a sourced value, and the
  sources disagree with each other (open). RO's 6:1 main-stage throttle (minThrust =
  maxThrust/6) matches this paper.
- A 1993 sales-oriented retrospective. The uprate and nozzle-option rows are **predictions**
  from 1960s-70s studies, not test data.
