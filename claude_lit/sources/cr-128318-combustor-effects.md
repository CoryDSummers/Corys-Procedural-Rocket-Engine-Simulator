# [CR-128318] — Experimental Investigation of Combustor Effects on Rocket Thrust Chamber Performance

## Identity

- **Title**: *Experimental Investigation of Combustor Effects on Rocket Thrust Chamber
  Performance*
- **Author**: W. H. Nurick, Rocketdyne (Div. of North American Rockwell), Advanced
  Programs, Canoga Park, CA
- **Report**: **NASA-CR-128318** / Rocketdyne report **R-8903**, NASA accession N72-33738
- **Contract**: NASw-2106, for NASA Manned Spacecraft Center, Houston
- **Date**: June 1972, interim report (first year of a planned multi-year program)
- **Extent**: 114 PDF leaves (~109 printed pages + refs). OCR is a 1970s typewritten
  document run through Paper Capture — body text is generally clean, but every data table
  and several figures (esp. printed pp. 87–95, PDF leaves ~89–97) render as scrambled
  column-major garbage. **This isn't just an OCR artifact**: the report itself carries a
  1973 NASA "Document Discrepancy Report" (PDF leaf 113) flagging pages 87–95 as
  "illegible when reproduced" in the original microfiche/paper distribution — the
  underlying scan is bad, not just the text layer.
- **PDF leaf ↔ printed page**: `leaf ≈ printed page + 3` for the body (leaf 7 = printed
  page 1); front matter (foreword/abstract/contents) is roman-numbered.

## Character

A first-year progress report from a Rocketdyne/NASA program (in support of the JANNAF
Liquid Rocket Thrust Chamber Performance standardization effort) built to **experimentally
isolate how non-uniform, striated injector mass/mixture-ratio distribution degrades
real thrust-chamber performance** relative to the ideal homogeneous-combustion analytical
methods of the day. It's not a design handbook — it's a diagnostic-instrumentation and
single-element-characterization study, with the actual hot-fire engine test campaign being
a validation step rather than the main event. The single-element cold-flow atomization/
mixing results (Task II) are the most broadly reusable content; the hot-fire summary
(Task IV) mostly confirms the design intent rather than adding new correlations.

## Test article (Task IV engine)

| Parameter | Value |
|---|---|
| Propellants | LOX / GH₂ |
| Injector | 96-element, 4-ring impinging **triplet** (ox/fuel/ox), outer ring fed
  separately from inner 3 (core) rings, + a separate 96-orifice film-coolant ring |
| Element geometry | included impingement angle 60°, impingement point 0.3 in from face,
  orifice L/D = 14:1, contoured inlets |
| Chamber | OFHC copper heat-sink calorimeter, **L\* = 20 in**, contraction ratio **2.0**,
  wall radius upstream of throat = 1.5×R_t, throat-to-nozzle transition radius = 1×R_t,
  15° conical nozzle, ε = 4 → 25 (mild-steel nozzle extension) |
| Nominal design point | Pc = 250 psia (225 psia as actually run), MR = 5 overall (core MR
  3.5–6, outer-zone MR 5–8), BLC (film coolant) 0–10 % of fuel, thrust ≈ 7000 lbf @ ε=25,
  test duration 2 s |
| Assumed / measured combustion quality | **C\* efficiency ≈ 97 %, Isp efficiency ≈ 94 %**
  across 15 valid hot-fire tests (4 hyperflows; first 2 were checkout-only) |

## Key results

- **C\* efficiency ≈ 97 %, Isp efficiency ≈ 94 %**, stated in the abstract and confirmed in
  the Performance discussion (p. 82/leaf 85): "the efficiencies are about 97%, which
  suggests the chamber is sufficiently long for near complete (or complete) vaporization of
  the LOX." This is a real, if crude (heat-sink, 2-s duration), LOX/GH₂ triplet-injector c\*
  data point at modest Pc (225 psia) and short L\* (20 in) — usable as a sanity check for
  `injectors.py`/`combustion.py`'s c\*-efficiency treatment of impinging triplet elements.
- **Wall static pressure vs area ratio matched the full-shifting-equilibrium prediction
  closely** (Fig. 39, test 547, Pc=222.9 psia, MR=5.5) — supports treating shifting
  equilibrium as the right analytical baseline for this propellant/MR/Pc regime, per
  `[Sutton]`'s frozen-vs-shifting framing.
- **Gas-side heat flux followed the Bartz-equation trend** (simplified infinite-conductivity
  calorimeter method, p.100/leaf 102), cross-checked via Biot number (`hδ/K`) per heat-flux
  segment to validate the "hot side follows cold side" assumption — **flagged as unreliable
  in the throat region specifically** (Biot number there reaches ≈0.26, "expected to be in
  considerable error [up] to 30%"), a concrete data point for how thin a calorimeter
  segment needs to be for a lumped-capacitance heat-flux measurement to be trustworthy near
  the throat.
- **Single-element atomization (impinging triplet, LOX/GH₂ simulants)**: mass median
  dropsize D fell in the **100–225 μm** range over hot-fire-equivalent MR 3–8, and — echoing
  Mehegan et al. (Ref. 2, cited) for impinging elements generally — **D is inversely
  proportional to a power of the gas dynamic parameter ρ_g·V_g²**, confirmed here over an
  extended range **50–260 psi** (vs. Mehegan's original 1.5–17 psi), for liquid/gas
  penetration parameter (X_p/D) in the 0.2–0.7 band where dropsize is insensitive to
  penetration. Normalized dropsize distribution (D/D̄) was invariant with test condition —
  a single dimensionless curve (Fig. 12) describes the whole matrix.
- **Single-element mixing efficiency (η_mix) peaked at hot-fire-equivalent MR 3–5** for this
  triplet geometry (Fig. 19), and **improved with increasing collection distance** (2 in →
  5 in) at fixed MR — attributed to the gas flowfield expanding faster than the liquid
  spray with axial distance, "partially counteracting the initial high concentration of gas
  near the center." At high liquid-penetration parameter (X_p/D), the liquid mass-flux
  profile becomes elliptical, "look[ing] like a liquid like-doublet injector element."
- **Full-scale injector manifold flow uniformity**: designed and measured to keep per-
  element flow deviation low across all 4 rings + BLC ring at ~1% design intent (Table 1);
  manifold injector supply pressure was only 2.72 psig above venturi throat (subcritical
  pressure ratio) in the characterization rig — a real example of a manifold sized for very
  low internal velocity specifically to guarantee per-element uniformity.

## Design/test method — what to reuse

- **Cold-flow modeling criteria for gas/liquid impinging elements**: match cold-flow to
  hot-fire on the **gas dynamic parameter (ρ_g·V_g²)** and the **liquid/gas penetration
  parameter (X_p/D_o)** (X_p defined via impingement angle, orifice diameter, density ratio,
  and MR); GHe was used as the GH₂ simulant specifically because matching hot-fire gas
  velocity in N₂ would exceed sonic limits. Where both parameters can't be matched
  simultaneously (as at the lowest MR point here), fall back to matching (X_p/D_o) and
  (ṁ/V_o) alone, valid only when ρ_g, V_g don't deviate far from hot-fire.
  This is the general "how do you cold-flow-test an injector element and trust the result"
  method, reusable well past LOX/GH₂ triplets.
- **Two-phase impact-probe mixing measurement**: stagnate the gas component at a probe tip
  (Baratron pressure), let liquid droplets pass down the probe and collect over a timed
  interval, and back out local gas/liquid mass flux from both; O₂-tracer sampling
  distinguishes injected gas from entrained ambient gas ingested into the plume.
- **Molten-wax atomization technique**: inject molten wax as the liquid-propellant simulant
  into a large pressurized vessel, freeze-catch the droplets, vacuum-dry, sieve-analyze for
  dropsize distribution and mass-median dropsize D̄ — a standard Rocketdyne technique of the
  era, cited as refined "over the past five years" before this report.
- **Heat-flux-from-calorimeter-segment method**: `q = ρ·δ·Cp·(dT/dθ)` (infinite-conductivity
  assumption), validity gated by Biot number `hδ/K` — the report's own worked caution that
  segments must be made thin enough (or the Biot number checked) near the throat, where h
  is highest, before trusting a lumped-capacitance heat-flux measurement there.

## Section map

| Section | Printed p. | Content |
|---|---|---|
| Foreword / Abstract | iii | Program summary, headline efficiencies |
| Task I: Injector & Thrust Chamber Design | 3 | 96-element triplet injector (Fig. 1, Table
  1–2), OFHC copper chamber (Fig. 3), instrumentation layout (Tables 3–5) |
| Task II: Injector Cold Flow Characterization | 19 | Impact-probe mixing rig, molten-wax
  atomization rig, manifold-uniformity rig; single-element test matrix (Table 6); results
  (Figs. 12–23, mostly legible) |
| Task III: Exhaust Gas Sampling System | 53 | Probe design, PVT + gas-chromatograph
  analysis method; caveat that air leakage prevented accuracy claims (p.108) |
| Task IV: Engine Performance Tests | 69 | Hot-fire facility (Cell 29B), 15 valid tests
  across 4 hyperflows, Table 13 results summary **(badly garbled/flagged-illegible OCR,
  pp.86–96)**, pressure profiles vs. shifting equilibrium (Fig. 39), Bartz/Biot heat-flux
  cross-check (Fig. 40–41) |
| Conclusions and Recommendations | 109 | All systems functional; 5 concrete instrumentation
  fixes recommended for the next test phase |
| References | 111 | Mehegan et al. (gas-augmented injectors, atomization/mixing
  correlation source), Burick AIAA 71-672 (coaxial injector atomization — not used in this
  report's own element type but a pointer for future coaxial-element work) |

## Caveats

- **This is a 1972 interim/first-year report** — it documents instrumentation development
  and a validation test series, not a mature design correlation set. No later NASA report
  completing this program was found in this pass; if one exists it would supersede Task
  IV's crude hot-fire summary.
- **Table 13 (the full per-test performance summary) and its surrounding pages are
  unreadable** in this scan — independently confirmed by the report's own 1973 NASA
  discrepancy filing. Only the abstract-level 94%/97% headline efficiencies and the
  narrative discussion around them are trustworthy from Task IV; do not attempt to
  back-derive per-test numbers from the garbled table.
- Test article is small (7000 lbf), short-duration (2 s), heat-sink hardware at modest Pc
  (225 psia) — the triplet element and c\*-efficiency numbers generalize as *typical*
  values for this element type/regime, not as a validated-analog spot-check target the way
  a production flight engine's config would be.
- The mixing/atomization correlations (dropsize ∝ power of ρ_g·V_g², penetration parameter)
  are Rocketdyne in-house correlations from the cited Mehegan reference, extended here to a
  wider pressure range — treat as "this report's own synthesis of prior work," not an
  independently-derived first-principles result.
