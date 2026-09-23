# SP-8109 — Liquid Rocket Engine Centrifugal Flow Turbopumps

## Identity

NASA SP-8109, *Liquid Rocket Engine Centrifugal Flow Turbopumps*, NASA Space Vehicle Design
Criteria (Chemical Propulsion), December 1973. `literature/NASA SP-8109 - Liquid Rocket Engine Centrifugal Flow Turbopumps.pdf` (NTRS 19740020848; 124 PDF leaves;
fixed offset: printed page N = PDF leaf N+11, e.g. printed p.1 "INTRODUCTION" is leaf 12).
Tag: `[SP-8109]`.

## Character

Same monograph family and structure as `[SP-8120]`/`[SP-8107]`: parallel §2 "State of the
Art" (narrative, p.3-59) / §3 "Design Criteria and Recommended Practices" (imperative
"shall"/"recommended", p.61-86) with matching subsection numbers (e.g. §2.2.1.2 Suction
Specific Speed ↔ §3.2.1.2). Scope is specifically **centrifugal-flow** pump stages (as
opposed to `[SP-8107]`'s system-level whole-turbopump treatment) — impeller hydrodynamic and
mechanical design, housing/diffuser/volute design, and thrust-balance systems. Real engines
referenced throughout: Titan (LR-87/LR-91), Atlas, H-1, F-1, J-2/J-2S, X-8, NERVA, M-1,
Mark III/Mark 19/Mark 29 pump designations.

Structure: §1 Introduction (p.1-2), §2 State of the Art (p.3-59: 2.1 Configuration Selection,
2.2 Pump Performance incl. Speed/Critical Speed/Suction Specific Speed/Turbine Limits/
Bearing-Seal Limits/Efficiency/Flow Range, 2.3 Impeller incl. Hydrodynamic/Mechanical
Design/Fabrication/Materials, 2.4 Housing incl. Diffuser/Volute/Materials, 2.5 Thrust
Balance System), §3 Design Criteria (p.61-86, mirrors §2's subsection numbers), Appendix A
Glossary (p.87-94), Appendix B Unit conversion (p.95-96), References (p.97-102).

## This note's extraction scope

Read in full: §2.2.1 Speed (Critical Speed, Suction Specific Speed, Turbine Limits, Bearing
and Seal Limits — leaf 19-27) and its design-criteria mirror §3.2.1 (leaf 74-75); §2.3
Impeller Hydrodynamic Design and Mechanical Design (leaf 36-50, incl. Table I real
impeller-geometry/performance data). Skimmed for structure/headers only: §2.1 Configuration
Selection, §2.2.2-2.2.3 (Efficiency/Flow Range state-of-art, though the design-criteria
mirror §3.2.2/3.2.3 was read in full since it was on the same pages as §3.2.1), §2.4 Housing
(diffuser/volute/casing), §2.5 Thrust Balance System (leaf 66-67, first page read for
structure/figure captions only), §2.3.3-2.3.4 Fabrication/Materials, Appendices. **Not
read**: the corresponding §3.3-3.5 design-criteria sections for impeller/housing/thrust-
balance (leaf ~76-97) beyond a header-level skim, References.

## Key results

**Real suction-specific-speed design limits (this monograph's own design criteria)**
`[SP-8109 §3.2.1.2 p.63]`: **"For a pump with an integral inducer, maximum suction specific
speed of 40,000 for the inducer is recommended. Without an integral inducer, limit the Ss
value to 12,000."** This is a *direct, real design-criteria citation* for
`engine_designer`'s planned NPSH/suction-specific-speed feature (see the
`i-want-you-to-flickering-codd.md` plan's `NSS_TARGET_US` constants) — the plan's
`lox_class: 40_000.0` seed value matches this monograph's integral-inducer recommendation
exactly, though this source frames 40,000 as a general inducer-equipped limit (not
LOX-specific) and gives no separate LH2-class number; the plan's `lh2_class: 58_000.0` still
rests on the two-anchor-point derivation from `[SP-8107]`-family data, not this source.
Also gives the required-NPSH margin recommendation directly: **NPSH ≥ 3·cm1²/2g for
low-vapor-pressure fluids (water, RP-1), 2.3·cm1²/2g for LOX/LF2, 1.3·cm1²/2g for LH2** — a
concrete margin-factor-by-propellant-class number with no counterpart yet in
`turbopump_sizing.py`.

**Real corrected suction-specific-speed data points** `[SP-8109 Fig. 4-5, §2.2.1.2 p.11-16]`:
a real fleet table (values are corrected Ss, roughly ×1000): F-1 RP-1 pump ≈23,400; F-1 LOX
pump ≈19,500; J-2 LOX pump ≈10,200; Atlas booster LOX ≈14,250; Atlas sustainer LOX ≈8,600;
Atlas sustainer RP-1 (no inducer) ≈15,000 (Ss); X-8 LH2 ≈11,000. **Caveat**: these real
fleet values (8,600-23,400) sit noticeably below the monograph's own 40,000 *recommended
maximum* for an integral inducer — i.e. 40,000 is an upper design limit, not a typical
achieved value; real hardware historically ran with more suction margin than the limit
allows. Cross-check any future Nss validate.py check against both the *limit* (40,000) and
these *typical achieved* values (~10,000-23,000) so a synthetic high-head-pump test case
isn't calibrated against an unrealistically aggressive Ss.

**Real critical-speed design practice** `[SP-8109 §2.2.1.1, §3.2.1.1 p.8-10, 63]`: two
distinct real design philosophies — (1) keep all operating speeds below the first
rigid-body whirl critical speed (needs stiff bearings, often roller bearings + ball bearings
for thrust — the disadvantage explicitly named is **"high bearing DN values"**, though no
DN number itself is given in this monograph — see `[SP-8048]` for the dedicated bearings
monograph, read separately), or (2) operate above the first/second whirl critical speeds
but below shaft-bending resonance (needs preloaded/duplex ball bearings, lower spring
rates). Both practices keep a **~20% margin** between operating speed and the nearest
critical speed — an explicit "shall not operate continuously at a critical speed" design
criterion `[§3.2.1.1]` with the 20% margin given as a firm recommendation, not just a
typical value.

**Real impeller tip-speed limits by material/fabrication** `[SP-8109 §2.3.2 p.37]`: **shrouded
cast impellers pumping LH2 limited to 1400 fps for Inconel 718 or vacuum-melt/vacuum-cast
aluminum**; a machined **open-face titanium (Ti-5Al-2.5Sn) impeller operated in LH2 to 2500
fps**; a **shrouded diffusion-bonded titanium impeller spun to 2870 fps at room temperature**
(spin-test only, not an operating limit). This is real, concrete tip-speed-vs-material data
directly relevant to `turbopump_sizing.py`'s tip-speed limits and `turbopump_materials.py`'s
rotor catalog — open-face titanium buys ~80% more tip speed than shrouded Inconel/aluminum
for the same LH2 service, a real trade the tool's rotor-material choice doesn't currently
capture if it only varies max-use-temperature and density (not shrouding-configuration
tip-speed limits).

**Real impeller geometry/performance table** `[SP-8109 Table I, p.26]`: a fleet-wide table of
discharge blade angle (22.5°-90°), blade count (6-48), tip diameter, and best pump/specific
efficiency (0.55-0.81) for ~20 real pump stages (Titan LR-87/-91 fuel/ox, NERVA, M-1, F-1,
J-2, J-2S, X-8) — a real cross-check table for `turbopump_efficiency.py`'s derived
pump-efficiency-vs-specific-speed relation.

**Real efficiency-scaling notes** `[SP-8109 §2.2.2 p.14-15]`: rocket-engine pumps are
inherently **lower-efficiency than commercial pumps at the same flowrate/Ns** because higher
rotating speeds require larger operating clearances (reactive propellants) and higher
suction specific speed requires larger inlet diameters, both of which cost efficiency —
mechanical losses (bearing+seal power) can be **up to 20% of shaft power for impellers as
small as 1.0 in diameter**, but are negligible for impellers ≥10 in.

**Bearing/seal/turbine speed limits are cross-referenced, not derived, in this monograph**
`[SP-8109 §2.2.1.3-1.4, §3.2.1.3-1.4]`: turbine speed limit is framed via `N²·Aa` (speed²
× rotor blade annulus area) reaching a material/temperature-dependent stress limit;
bearing/seal speed limits are explicitly deferred to reference monographs (ref. 43 for
bearings = **NASA SP-8048**, being read separately for this reason; ref. 44 for seals) —
confirms this monograph is not itself a source of bearing DN numbers, consistent with not
forcing a citation here for `turbopump_materials.py`'s `max_dn_mm_rpm` Tier-3 estimate.

## Design method

Like `[SP-8120]`/`[SP-8107]`, gives real design criteria/practices and real fleet data, not
closed-form sizing equations for chamber-adjacent physics — but it DOES give two genuinely
new, directly-usable numeric design limits not available elsewhere in this reference set:
the **40,000/12,000 suction-specific-speed limits** (§3.2.1.2) and the **3.0/2.3/1.3 NPSH
margin factors by propellant class** (same section) — both are real, quotable design
criteria suitable for direct use in the planned NPSH/suction-specific-speed feature.

## Section map

- §1 Introduction: p.1-2 (leaf 12-13) — read.
- §2.1 Configuration Selection: p.3-6 (leaf 14-17) — skimmed.
- **§2.2.1 Speed (Critical Speed 2.2.1.1, Suction Specific Speed 2.2.1.2, Turbine Limits
  2.2.1.3, Bearing and Seal Limits 2.2.1.4): p.6-14 (leaf 17-25) — read in full.**
- §2.2.2 Efficiency, §2.2.3 Flow Range: p.14-24 (leaf 25-35) — skimmed (state-of-art);
  design-criteria mirror read in full (see below).
- **§2.3 Impeller (Hydrodynamic Design 2.3.1, Mechanical Design 2.3.2): p.25-38
  (leaf 36-49) — read in full, incl. Table I.**
- §2.3.3 Fabrication, §2.3.4 Materials: p.38-40 (leaf 49-51) — skimmed.
- §2.4 Housing (Hydrodynamic Design, Casing, Diffusion System, Volute, Materials):
  p.39-55 (leaf 50-66) — not read, header/figure-caption skim only.
- §2.5 Thrust Balance System: p.55-59 (leaf 66-70) — first page read for structure/figure
  captions only, remainder not read.
- **§3.2.1 Speed, §3.2.2 Efficiency, §3.2.3 Flow Range (design criteria): p.62-65
  (leaf 73-76) — read in full.**
- §3.3 Impeller, §3.4 Housing, §3.5 Thrust Balance (design criteria): p.66-86
  (leaf 77-97) — not read.
- Appendix A Glossary, Appendix B Unit Conversion, References: p.87-102 — not read.

## Caveats

- **Real Ss fleet data (8,600-23,400) sits well below this monograph's own 40,000
  recommended limit** — don't treat 40,000 as a typical achieved value; it's an upper
  design bound. See Key results above for the calibration implication.
- **No bearing DN number given** — this monograph explicitly defers bearing speed limits to
  a separate reference (SP-8048, being read separately this round). Don't expect this
  source to resolve `turbopump_materials.py`'s unsourced `max_dn_mm_rpm` Tier-3 flag.
- 1973 vintage, real examples are 1960s/early-70s hardware (Titan, Atlas, F-1, J-2/J-2S,
  NERVA, M-1) — pre-SSME, pre-modern-additive-manufacturing impeller fabrication (though the
  diffusion-bonded-titanium example is notably advanced for its era).
- OCR quality: garbled in places (Pdf.Capture-style artifacts, e.g. "tile" for "the",
  "presstire" for "pressure", numeric/formula OCR occasionally unreliable in the equations
  quoted above) — technical content is unambiguous but exact symbol rendering in equations
  (7), (13), (17) etc. should be re-derived from context/dimensional analysis rather than
  trusted verbatim if ever implemented in code.
- Only ~40% of the document was deep-read this pass (Speed/Impeller sections); Housing
  (diffuser/volute design) and Thrust Balance System sections were not read in depth and may
  contain further useful design criteria for a future manifold/housing-focused pass.
