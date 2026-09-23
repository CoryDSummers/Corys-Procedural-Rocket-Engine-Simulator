# NASA TN — Interim Summary of Liquid Rocket Acoustic-Mode-Instability Studies at 20,000 lbf

## Identity

E. William Conrad, Harry E. Bloomer, John P. Wanhainen, David W. Vincent (NASA Lewis
Research Center), *Interim Summary of Liquid Rocket Acoustic-Mode-Instability Studies at a
Nominal Thrust of 20 000 Pounds*, NASA Technical Note, December 1968.
`literature/NASA TN (1968) - Interim Summary of Liquid Rocket Acoustic-Mode-Instability Studies at 20000 lbf.pdf` (NTRS 19690005052; 95 PDF leaves; body text printed page N ≈ PDF leaf N+4, e.g.
printed p.1 SUMMARY is leaf 5; printed p.82 SUMMARY OF RESULTS is leaf 86). Tag:
`[NASA-TN-Acoustic]`.

## Character

A large (multi-year, multi-reference-paper) experimental program summary on high-frequency
combustion instability ("screech") at NASA Lewis, consolidating results from ~17 underlying
NASA TN/TM reports (refs. 5-21, each covering one variable in depth) into one interim
synthesis across two propellant combinations: LOX/GH2 (concentric-tube injector) and
earth-storable N2O4 / (50% N2H4-50% UDMH) (impinging injector), both at ~20,000 lbf thrust.
Directly relevant to `claude_lit/topics/14-combustion-stability.md` (chug/buzz/screech,
acoustic modes, baffles, Helmholtz cavities, already covered via `[Sutton]`/`[Huzel]`/
`[SP-8107]`/`[NK-33-Mod]`/`[Bazarov]`) — this is the first source in this reference set with
a large real *screech-suppression parametric test program* rather than a design-criteria
narrative or a single-engine anecdote.

Structure: Summary (p.1), Introduction (p.2-3), Symbols (p.4), Apparatus (Engine
Installations/Engine/Injectors, p.5-11), Screech-Rating Devices (p.12), Instrumentation
(p.13-14), Procedure (p.15-16), Results and Discussion — split into **Energy Generation:
Hydrogen-Oxygen Propellants** (p.17-30ish), **Energy Generation: Earth-Storable Propellants**
(p.30-46ish), and **Energy Dissipation Studies** (nonfiring acoustic studies, liner
application for both propellant families, variable-resonator-volume liner studies,
injector-face baffles for both propellant families, nozzle-area radial distribution, porous
injector faceplates) (p.46-82), Summary of Results (36 numbered findings, p.82-86),
Concluding Remarks (p.86-87), References (p.87-90).

## This note's extraction scope

Read in full: front matter (Summary/Introduction/Symbols/Apparatus, leaf 0-11), the tail end
of the injector-faceplate energy-dissipation discussion (leaf 85), and the full 36-item
**Summary of Results** + Concluding Remarks + References (leaf 85-93) — this is where every
quantitative finding of the whole 90-page program is distilled into short numbered
statements, so it captures the paper's real content efficiently without needing to read
every intervening results subsection's full narrative. The detailed body sections (Energy
Generation for both propellant families, Energy Dissipation/liner-design body text, leaf
17-85) were **not separately deep-read** — their conclusions are captured via the Summary
of Results list, which restates each one as a numbered finding; if a specific liner-design
formula or a specific figure's plotted curve is needed later, go to the relevant body
subsection directly (see Section map).

## Key results — real screech-suppression findings (Summary of Results, 36 items)

**Injector/energy-generation side (LOX/GH2, concentric-tube injector)**:
- Hydrogen-injection temperature margin is a good dynamic-stability metric; screech
  temperature could be pushed below 60°R (33.3 K, the facility's minimum) by using an
  **oxygen/hydrogen injection area ratio below 0.5**.
- **Decreasing contraction ratio improved stability** (higher chamber pressure/flow at fixed
  contraction ratio is destabilizing).
- A **stability parameter** `w = ΔpH·ρH / (ρO·DO²·(O/F))^(some form)` (see the paper's own
  nomenclature) had a critical value of **4.4**: above 4.4 stable, below unstable, for an
  85%-radial-face-coverage injector — a real correlating parameter combining hydrogen
  injector ΔP, propellant densities, oxidizer orifice diameter, and O/F.
- **Weight flow per element above 0.6 lbf/sec (0.272 kg/sec)** (achieved by reducing element
  count) gave stable operation down to the facility's 60°R minimum hydrogen temperature —
  at a performance cost.
- **Recessing the oxidizer post 0.1 in (0.254 cm)** below the faceplate gave +50°R (27.8 K)
  screech-temperature margin AND +3% C* efficiency (a rare "both stability and performance
  improve" result) — directly relevant to `injectors.py`'s coaxial/shear-element recess
  parameter if one exists.
- **Extending the oxidizer tube** fully stabilized a previously-unstable 100-element
  injector, but cost ~4% C* efficiency across the O/F range — a real, quantified
  stability-vs-performance tradeoff for oxidizer-post extension length.
- Raising oxygen-injection temperature from 140-240°R (77.8-133.3 K) *hurt* stability
  (screech temperature rose ~50°R/27.8 K) — propellant inlet temperature is a real stability
  lever, not just a performance one.
- Adding 30 wt% fluorine to oxygen had no significant stability effect but gave +1-3%
  performance.
- Diverting 10-20% of hydrogen for film cooling had [effect noted but not fully captured in
  this extraction pass — see leaf 86-87 for the full item].

**Injector/energy-generation side (earth-storable, impinging injector)**:
- Peak performance occurred at **velocity ratio 0.5-0.7** at both 100 and 300 psia chamber
  pressure — about **25% less than JPL's "uniform mixture ratio distribution" criterion**
  predicted, a real discrepancy between a classical injector-design criterion and measured
  performance.
- Impingement angle from 38° to 120° had **no significant effect** on performance or
  stability. The oxidant-to-radial-fuel-velocity ratio (Vo/VFr) gave the best stability
  correlation for this propellant combination — better than impingement angle itself.
- Extending fuel impingement distance from 0.5 to 1 in (1.27-2.54 cm) had only a minor
  destabilizing effect, no significant performance change.
- Alternating-grid-pattern injectors were generally *less* stable but 1-2% higher C*
  efficiency than circular-pattern injectors at equal thrust-per-element — a real
  stability/performance tradeoff tied to injector *pattern*, not just element type.
- An oxidizer-fuel-oxidizer triplet was less stable but slightly higher-performing than a
  fuel-oxidizer-fuel triplet, and **notably more erosive to chamber hardware** — a real
  materials/durability caution for triplet-orientation choice.
- **Net conclusion for earth-storables**: "no major improvement seems likely through changes
  in the propellant-injection process" — injector-side fixes worked well for LOX/GH2 but
  poorly for this earth-storable pair; energy-*absorption* devices (below) were needed
  instead.

**Energy-dissipation side (both propellant families) — acoustic liners, baffles**:
- Acoustic liners with **absorption coefficient ≥ 0.25** (calculated including the effect of
  flow past the liner apertures) were needed to eliminate screech in the LOX/GH2 engine at
  its most unstable condition (60°R H2 injection temp).
- **A 17%-partial-length liner at the injector end** fully suppressed instability — a
  full-length liner was NOT required for this combustor.
- Liner absorption theory matched experiment only when **flow-past-aperture effects (280
  ft/sec / 85.3 m/s in this test) were included** in the absorption-coefficient calculation
  — a real caveat that liner sizing without a flow-past-orifice correction will be wrong.
- **Injector-face baffles**: 2-in (5.08 cm) baffles gave full stability down to 55°R
  (30.6 K) H2 temperature with as few as 3 compartments; 1-in (2.54 cm) baffles gave only
  marginal stability at 55°R when the maximum baffle-cavity dimension was under 4.5 in
  (11.43 cm). For earth-storables with 1-in baffles, the maximum compartment dimension had
  to stay under 3.5 in (8.89 cm) for stability against a 41-grain (2657 mg) bomb rating —
  i.e. **baffle compartment size has a real, quantified maximum before stability is lost**,
  and that maximum is propellant/rating-method-dependent (bigger margin for LOX/GH2 than for
  the tested earth-storable pair).
- A **porous (sintered-screen) injector faceplate**, bleeding ~5% of total hydrogen flow
  through the face for cooling/damping, cut the screech transition temperature by 25°R
  (13.9 K) at O/F 5.0, at a cost of 1-2% C* efficiency — another real stability-for-Isp
  tradeoff, this time via a porous/transpiration-style faceplate rather than a baffle.
- A **simulated plug nozzle (annular flow)** gave +20°R (11.1 K) hydrogen-temperature margin
  vs. a conventional C-D nozzle — nozzle *type* itself is a real (if secondary) stability
  lever.

## Design method

Not a closed-form design-equation source (no orifice-sizing or baffle-length formula is
derived here) — this is an empirical parametric-test-program summary. Its value is
real quantified stability/performance tradeoffs (recess depth, baffle length/compartment
size, liner absorption coefficient, area ratio thresholds) for a specific 20,000-lbf-class
engine family, directly comparable in kind to `[Sutton]` Table 9-2's stability-boundary
data already in `topics/14-combustion-stability.md`, but at much finer granularity for the
specific injector/liner/baffle variables tested.

## Section map

- Summary/Introduction/Symbols: leaf 0-4 (printed p.i-4) — read.
- Apparatus (engine installations, engine, injectors): leaf 5-11 (printed p.5-11) — read.
- Screech-Rating Devices, Instrumentation, Procedure: leaf 12-15 — not deep-read (methodology
  only, not results).
- Results and Discussion — Energy Generation: Hydrogen-Oxygen Propellants (injection areas,
  element size, oxidizer tube extension/recess, oxygen temperature, fluorine addition, film
  cooling): printed p.17-46ish (leaf ~21-50) — **not separately deep-read this pass**; findings
  captured via the Summary of Results list (see Key results above). Read directly if a
  specific figure/correlation plot is needed.
- Results and Discussion — Energy Generation: Earth-Storable Propellants (velocity ratio,
  impingement angle/distance, grid pattern, triplet orientation): printed p.30-46ish — same,
  not separately deep-read, captured via Summary of Results.
- Results and Discussion — Energy Dissipation Studies (nonfiring acoustic studies, liner
  application for both propellant families, variable-resonator-volume liner studies,
  injector-face baffles for both propellant families, nozzle-area radial distribution, porous
  injector faceplates): printed p.46-82 (leaf ~50-85) — tail end (porous faceplate subsection,
  leaf 85) read directly; remainder captured via Summary of Results only.
- **Summary of Results (36 numbered findings): printed p.82-86 (leaf 85-89) — read in full,
  the primary source of Key results above.**
- **Concluding Remarks: printed p.86-87 (leaf 89-90) — read in full.**
- References (41 entries, mostly internal NASA TN/TM cross-references to the underlying
  single-variable studies this synthesis draws on): printed p.87-90 (leaf 90-93) — read
  (titles/authors only, not chased further).

## Caveats

- **This note leans heavily on the Summary of Results list rather than the underlying body
  sections** — each numbered finding is a real result, but the body text (not read this
  pass) would have the actual figures, exact test matrices, and error bars behind each
  number. Treat the numbers above as trustworthy top-line findings, not as a substitute for
  reading the specific body subsection if fine-grained data is needed later.
- **1968 vintage, 20,000-lbf-class engines specifically** — the paper itself cautions that
  "complete confidence in stable operation is not possible until the effects of scaling
  factors such as chamber size are determined" — i.e. the authors themselves flag that these
  findings may not scale linearly to larger or smaller engines.
- No manifold, regenerative-cooling, or "sandwich"/dual-wall chamber-construction content —
  flagged here only for completeness since this source was pulled in the same literature
  batch as sources specifically covering those topics.
- OCR quality: clean for body-text paragraphs (this is a well-scanned NASA TN); occasional
  minor character misrecognition (e.g. stray "'" characters) in headers/numbers, but numeric
  values quoted above were double-checked against the surrounding sentence context.
