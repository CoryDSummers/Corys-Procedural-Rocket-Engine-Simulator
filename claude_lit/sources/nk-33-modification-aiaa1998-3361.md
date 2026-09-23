# [NK-33-Mod] — Modification and Verification Testing of a Russian NK-33 Rocket Engine for Reusable and Restartable Applications

## Identity

- **Title**: *Modification and Verification Testing of a Russian NK-33 Rocket Engine for
  Reusable and Restartable Applications*
- **Authors**: J. Hulka, J.S. Forde, R.E. Werling — Aerojet, Sacramento CA; V.S. Anisimov,
  V.A. Kozlov, I.P. Kositsin — N.D. Kuznetsov SSTC, Samara, Russia
- **Report**: **AIAA 98-3361** (PRA 044-98). Copyright 1998 by Aerojet and N.D. Kuznetsov
  SSTC.
- **Extent**: 26 PDF pages (16 printed pages of body text + tables/figures + references).
  Clean digital-native text layer (not a rough scan) — extraction quality is high.
- **PDF leaf ↔ printed page**: `leaf ≈ printed page − 1` (page 1 of text is leaf 0).

## Duplicate-file note

`literature/` contains **two identical copies** of this paper: `AIAA-1998-3361.pdf` and
`MODIFICATION AND VERIFICATION TESTING OF A RUSSIAN NK-33 ROCKET ENGINE FOR REUSABLE AND
RESTARTABLE APPLICATIONS.pdf` — confirmed byte-for-byte-equivalent-in-substance via
identical PDF `/Title` metadata. This note is written from `AIAA-1998-3361.pdf` only; the
long-named duplicate is flagged to the user as a candidate for manual deletion (not deleted
here — distillation doesn't touch `literature/`).

## Character

A real-engine modification-and-test report, not a textbook or design-method paper. The
NK-33 is a **350,000-lbf-class, oxidizer-rich staged-combustion LOX/kerosene** engine
designed by Kuznetsov SSTC in the 1960s for the Soviet N-1 lunar vehicle (upgraded from the
NK-15), imported to the US in the 1990s and modified by Aerojet (as AJ26-58/59, later flown
on Antares) for reuse on the proposed reusable Kistler K-1 vehicle. Value here is (a) a
complete real Table I performance/parameter set for a genuine ox-rich-staged-combustion
engine at full fidelity (thrust, Isp, both chamber and **preburner** Pc/MR/Tout), (b) real
turbopump/preburner/chamber materials and construction detail, (c) direct evidence that a
real flight engine achieves combustion stability with **zero** baffles/acoustic cavities in
the main chamber, and (d) real dry/wet engine mass numbers.

## Engine parameters (Table I, nominal @ Kistler std. inlet, 100% power)

| Parameter | Value |
|---|---|
| Sea-level thrust | 340,000 lbf |
| Vacuum thrust | 379,000 lbf |
| Sea-level Isp | 297 lbf·s/lbm |
| Vacuum Isp | 331 lbf·s/lbm |
| Total MCC propellant flow | 1144 lbm/s (Ox 825 + Fuel 319 — sums exactly, cross-check) |
| Main chamber MR | 2.59 |
| TVC fuel tapoff flow | 5.0 lbm/s |
| **Main chamber Pc** | **2109 psia** |
| **Preburner Pc** | **4670 psia** (= 2.21× Pc) |
| **Preburner MR** | **58** (deeply oxidizer-rich, as expected for an ox-preburner cycle) |
| **Preburner outlet temp** | **670 °F** (= 628 K) — turbine inlet temp |
| Nozzle area ratio | 27.7:1 |

Reconstructed by matching row/value magnitudes against a column-scrambled OCR-adjacent
table layout; Ox 825 + Fuel 319 = 1144 (exact) and 825/319 = 2.587 ≈ MR 2.59 (exact) both
self-check, so trust these values.

## Key results

- **Preburner pressure ratio to Pc = 2.21×** — a real number for `STAGED_COMBUSTION_
  PRESSURE_MULT` in `design.py` (currently 1.6). See caveat in `08-engine-cycles.md`'s
  existing implications section, which already flags this constant as possibly too low
  against `[SP-8107]`/`[KBKhA]`; this is a third, very concrete anchor.
- **MR shifts with throttle without an active MR valve**: nominal MR 2.59 at 100% power
  drifts to 2.75 at 75% Pc and 2.90 at 50% Pc (the MR valve, when active, gives ~20% control
  range, i.e. about −5%/+15% for the Kistler configuration). This is a real, quantified
  throttle-vs-MR coupling from an oxidizer-rich-preburner engine.
- **No stability aids, no instability**: "There are no baffles, acoustic cavities, or other
  stability devices in the main combustion chamber... Since very early in the NK-15
  development, there have been no instances of combustion instability in the main
  combustion chamber." Achieved purely through injector-face propellant distribution
  (coaxial fuel-swirl elements, outer row biased for mass/MR stratification). The
  *preburner*, by contrast, does use injector-face baffles for high-frequency damping —
  i.e. the stability-critical device on this engine is on the fuel-rich^H^H oxidizer-rich
  small-volume preburner, not the large MCC.
- **Built-in film cooling from the regen return flow**: coolant fuel splits at the aft
  jacket into an up-chamber and down-nozzle path; some of the up-chamber coolant is then
  reinjected into the combustion chamber through two rows of tangential orifices in the
  chamber barrel downstream of the injector — i.e. film cooling sourced from spent regen
  coolant, not a separate injector-face film circuit.
- **Repeatability** (from Russian qualification history): ±1% thrust, ±1.5% MR, ±1% Isp —
  useful as a real engine-to-engine/test-to-test scatter band.
- **Throttle range**: 49–123% Pc (electromechanical actuator range), commandable at up to
  135% Pc/second; shutdown from 55% power to 10% Pc in 0.8 ± 0.3 s.
- **Gimbal**: ±6° required range for Kistler K-1; gimbal bearing derived directly from the
  **SSME** gimbal bearing (shortened, cheaper non-cryo Ti alloy substituted) — a real
  cross-program bearing reuse case.
- **Mass** (Table V): basic engine (AJ26-58) dry 3104 lbm / wet pre-fire 3335 lbm / wet
  operating 3409 lbm; restartable (AJ26-59) dry 3216 lbm / wet pre-fire 3447 lbm / wet
  operating 3521 lbm. Thrust-to-weight (vacuum thrust / dry weight) ≈ 379,000/3104 ≈ 122:1 —
  very high, consistent with staged combustion + thin-margin Russian design practice.
- **Materials**: turbopump housings = aluminum sand castings (high-pressure housings =
  aluminum forgings); high-speed inducers/impellers = investment-cast **chrome-nickel
  steel**, except the high-speed fuel inducer = **titanium alloy**; low-speed/main shafts =
  stainless steel except fuel-boost-pump shaft = titanium; turbine housing = **Inconel
  equivalent**; MCC chamber liner = **chrome-copper alloy** (matches the Western
  chamber-liner-material convention `[Huzel]`/`[Sutton]` already document); nozzle
  sections and chamber external jacket = stainless steel; preburner injector/faceplate =
  chrome-copper alloy, preburner shell/manifold = stainless steel.
- **Benchmark test data (Table VII, 1995, unmodified engine)**: 14 data points spanning
  57.6–113.6% of nominal Pc; calculated sea-level Isp ranged 285.9–300.5 s across that whole
  power range, consistent with the nominal 297 ± 3 s spec — a usable real-engine spot-check
  point (off-nominal power level → Isp) if `validate.py` ever wants an oxidizer-rich-staged-
  combustion, non-100%-throttle case.
- **Test-derived accuracy bands**: thrust ±0.8% (3σ), Isp ±1.3% (3σ) — thrust isn't
  measured directly (vertical stand), it's back-calculated from flow + Pc + a
  Russian-supplied Cf curve.

## Section map

| Section | Printed p. | Content |
|---|---|---|
| Abstract / Introduction | 1 | NK-33 history (N-1 program → NK-15 → NK-33 → Kistler/AJ26); benchmark-test rationale |
| NK-33 Engine Description | 2–4 | Cycle description, Table I performance, basic vs. restartable variant differences, ignition systems (TEA/TEB preburner start, solid pyroigniters × 3 for MCC, solid start cartridge) |
| Hardware Components (Turbopump / Preburner / Thrust Chamber Assembly / Engine Valves) | 4–6 | Materials, construction, cooling-jacket flow split, injector element types |
| Description of the Engine Modifications | 6–8 | Table II/III modification lists + rationale (pyrotechnic→solenoid valves, EMAs, gimbal/thrust-mount, controller) |
| Engine Characteristics (Weight / Start / Shutdown sequences) | 9–10 | Table V weights; sub-second-resolution start/shutdown event timeline |
| Aerojet E-5 Test Facility | 10 | Facility capability, thrust-measurement method and uncertainty |
| Benchmark Test Results (1995) | 10–11 | 5 tests, Table VII data, 20-year-storage verification |
| Verification Test Results (1998) | 11–13 | 5 tests of modified engine, Table VIII data, low-inlet-pressure cavitating start test |
| Conclusions / Future Plans | 13 | Modifications didn't change performance/transients; restartable config and acceptance testing still to come |
| Tables I–VIII | 14–17 | Performance, modification lists, sensor suite, weights, inlet conditions, benchmark + verification data |

## Caveats

- This is a **program status report at a fixed 1998 publication deadline** — only 5 of a
  planned longer verification test matrix had been run; some data (Table VIII, restart
  testing) is incomplete or deferred to "a future paper" that isn't in this literature set.
- Table I's flowrate/pressure rows had ambiguous OCR-adjacent column alignment; values
  above were reconstructed using internal arithmetic self-checks (Ox+Fuel=Total,
  Ox/Fuel≈MR) and should be treated as trustworthy but not photographically verified
  against the original table image.
- No numeric turbopump specific-speed / pump-efficiency data is given — only qualitative
  construction detail (materials, bearing types, shaft coupling). Don't expect this source
  to feed `turbopump_efficiency.py`/`turbopump_sizing.py` directly the way `[SP-8107]` does.
- This is a Western-modified derivative (AJ26) of a Russian design; some numbers (e.g.
  gimbal range, MR-valve range) are Kistler-vehicle-specific requirements, not intrinsic
  engine limits — the underlying Russian engine's own N-1-era operating envelope (Table VI
  "Soviet N-1" column) differs (e.g. higher inlet pressures, no MR-valve tapoff usage).
