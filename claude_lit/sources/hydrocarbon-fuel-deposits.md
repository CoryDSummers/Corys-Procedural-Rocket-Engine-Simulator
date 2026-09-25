# NASA-CR-168334 — Deposit Formation in Hydrocarbon Rocket Fuels (Executive Summary)

## Identity

R. Roback, E.J. Szetela, L.J. Spadaccini (United Technologies Research Center, East
Hartford CT), *Deposit Formation in Hydrocarbon Rocket Fuels — Executive Summary Report*,
NASA Contractor Report (UTRC report no. R81-915216-2), NASA Lewis Research Center,
project manager Philip A. Masters, summary report covering work 4/1980-5/1981 (contract
NAS3-22765 era; work unit YOS8912). `literature/NASA CR-168334 - Deposit Formation in Hydrocarbon Rocket Fuels.pdf` (NTRS 19830026888; 23 PDF leaves: leaf 0
title page, leaf 1 report documentation page, leaves 2-14 = printed pages 1-13 body text,
leaves 15-20 = Figures 1-8, leaves 21-22 blank/back cover). Tag: `[Lewis-Deposits]`.

## Character

A short (13-page) executive-summary report on a dedicated experimental program to measure
thermal decomposition (coking) limits and carbon deposition RATES on regeneratively-cooled
chamber wall material, using an electrically-heated duplex copper/Inconel test-tube rig
(not a real firing engine — a standalone heat-transfer/fuel-stability test bench, closely
paralleling how `[TN-Dump]`/`[Marquardt-5981]` are used elsewhere in `claude_lit`). Directly
fills the coking-mechanism gap flagged in `claude_lit/topics/06b-cooling-methods-and-chemistry.md`
— that file currently only has a single derived wall-temperature threshold (RP-1 coking
"above 850°F / 728K" from `[SP-8087]`) and an ad hoc "~120K ΔT" framing with no underlying
rate data or mechanism description. This report is the first source in the batch giving
(a) an independently measured onset/peak-deposition temperature band, (b) real deposit-rate
magnitudes (µg/cm²·hr) as a function of wall temperature and velocity, and (c) a real
material-selection mitigation (nickel plating) with a quantified rate reduction.

Structure: Report Documentation Page (abstract), Introduction, Test Facility and Test
Hardware, Experimental Results and Discussion (Kerosene Fuel Tests, Propane Tests,
Nickel-Plated Tube Tests), Deposit Morphology (SEM/SEMP analysis), Concluding Remarks,
References, Figures 1-8. Read in full — short enough that no extraction-scope tradeoff was
needed. OCR is noisy throughout (character substitutions, garbled words like "Depwit" for
"Deposit", numbers occasionally split across line breaks) but all quantitative claims below
were cross-checked against at least two independent restatements of the same number within
the body text (the abstract, the results section, and the concluding remarks each restate
the key figures, which is how OCR noise was resolved).

## Key results

**Test matrix / rig** `[Lewis-Deposits, Abstract p.1; Facility p.3]`: duplex test tube —
inner wall 0.254 cm ID x 0.366 cm OD oxygen-free high-conductivity copper (No. 102, 99.95%
pure), outer wall Inconel 600 sheath (0.056 cm thick, drawn down over the copper),
overall OD 0.478 cm. Resistance-heated (40 kVA AC), ~95% of power generated directly in the
copper so the radial temperature gradient across the duplex wall stayed small (calculated
inner-vs-outer-wall ΔT only ~1-15 K across the whole test matrix, confirmed by calibration
tests to within 10 K). Ten thermocouples spot-welded to the outer Inconel wall at 2.54 cm
spacing. Test envelope: pressure **136-340 atm** (13.8-34.5 MPa), fluid (bulk) velocity
**6-30 m/s** (up to 36.6 m/s for propane), tube wall temperature **422-821 K** (abstract
range; body text also gives 422-811K). Fuels tested: RP-1, deoxygenated JP-7 (as a
"more-refined RP-1 simulator"), commercial-grade propane, chemically-pure propane. Input
heat flux to the tube varied 173-1460 W/cm² to achieve the target wall temperature.

**Coking onset / peak temperature — the headline number** `[Lewis-Deposits, Abstract p.1;
Kerosene Fuel Tests p.5-6; Concluding Remarks p.12]`, stated three times consistently:
"substantial deposit formation occurs with RP-1 fuel at wall temperatures **between 600 and
800K**, with **peak deposit formation occurring near 700K**." At the lowest test condition
(wall temp 422K, velocity 6.1 m/s, 10-minute duration) NO significant temperature rise or
deposit was observed at all (confirmed by post-test microscopic sectioning) — i.e. 422K is
clean, no further testing was done at that temperature. The thermal-resistance buildup rate
(computed from measured wall-temperature RISE during a fixed 10-minute test at fixed heat
flux) also peaked at tube locations where the **initial wall temperature was ~700K**, and
this peak rate *decreased* as fluid velocity increased. **Practical implication for
engine_designer's RP-1 hot-wall-temperature limit**: this is real rate/onset data
corroborating (not just asserting) a coking ceiling — 700K (~800°F/427°C) is the measured
worst-case (peak rate) temperature, with the onset band starting at 600K (~621°F/327°C) and
extending to 800K (~980°F/527°C) where deposition rate falls off again (see below). This
sits close to, but is a slightly WIDER/lower-onset framing than, `[SP-8087]`'s single-point
"RP-1 coking above 850°F (728K)" figure already in `topics/06` — 850°F≈728K is near this
report's OWN peak (700K) rather than its onset (600K), suggesting `[SP-8087]`'s number may
be describing a "significant/design-limiting" threshold rather than the true onset.

**Deposit rate FALLS OFF above ~700-800K, not monotonic** `[Lewis-Deposits, Kerosene Fuel
Tests p.6-7; Concluding Remarks p.12]`: carbon deposition rate (from CO2 burnoff
measurement) "increases with increasing temperature, reaches a maximum at an initial wall
temperature of approximately 600 to 700K, and then falls off as temperature is increased
further." This non-monotonic (bell-shaped) rate-vs-temperature behavior is a real, citable
qualitative finding — a flat "above X K, coking occurs" threshold model understates the
actual physics; a single hottest-station design check at, e.g., the throat is not
necessarily the worst point for coking accumulation if it runs hotter than ~800K, since the
chemistry itself becomes rate-limited/burns through the deposit-forming window at very high
wall temperature. (The report does not identify the high-temperature mechanism further —
likely deposit-forming precursor depletion or a shift toward gas-phase/volatile products
rather than surface-adherent coke — this is left unstated in the source.)

**Deposit RATE magnitudes** `[Lewis-Deposits, Kerosene Fuel Tests p.7; Concluding Remarks
p.12]`: for RP-1, carbon deposition rates of **400-600 µg/cm²·hr** at wall temperatures of
500-800K, for only a 10-minute test duration ("not anticipated" to be this high — an
explicit surprise finding by the authors). Deposit rate **decreases with increasing fluid
velocity** at fixed wall temperature (higher coolant velocity = thinner boundary layer / more
convective sweeping = less deposit buildup — consistent with standard fouling theory).
Pressure has only a weak effect: RP-1 tests at 340 atm vs. 136 atm showed **no significant
change** in wall-temperature-rise behavior; deposit rate "increased slightly" with pressure
over that range, i.e. **deposit formation is essentially pressure-independent from 136 to
340 atm (13.8-34.5 MPa)** — useful for engine_designer since it means the coking limit
shouldn't need a Pc-dependent correction across typical/high chamber-pressure ranges.

**Nickel plating cuts deposit rate by an order of magnitude — the mitigation finding**
`[Lewis-Deposits, Nickel-Plated Tube Tests p.9-10; Concluding Remarks p.12]`: electroless
nickel plating on the inside (hot-gas/fuel-contact) surface, tested with RP-1 at conditions
that produced high copper-surface deposition, gave average carbon deposition rates of
**~50 µg/cm²·hr** — "an order-of-magnitude lower than corresponding rates on copper" (vs.
the 400-600 µg/cm²·hr band above). Wall temperature rises during the 10-minute tests were
correspondingly much smaller than with bare copper. SEM/microprobe analysis of the
nickel-plated surface after test found little-to-no deposit, and elemental analysis showed
only nickel/phosphorus (electroless-plating-bath constituents) — no copper, carbon, oxygen,
or sulfur — confirming the nickel surface itself, not just its lower roughness, suppresses
deposit nucleation. **Mechanistic framing** `[Introduction p.2; Nickel-Plated Tube Tests
p.9]`: "a copper surface probably promotes deposit formation to as great an extent as any
deposit-forming precursor contained in the fuels" — i.e. bare copper is not a passive
substrate, it actively catalyzes coking, a real citable finding relevant to any regen-cooled
copper-alloy (e.g. NARloy, GRCop) chamber liner design discussion.

**No benefit from more-refined fuel (JP-7)** `[Lewis-Deposits, Kerosene Fuel Tests p.7-8;
Concluding Remarks p.12]`: deoxygenated JP-7 (dissolved O2 sparged below 5 ppm with N2, an
order-of-magnitude lower sulfur content than RP-1, meets a stringent thermal-stability spec)
was tested expecting improved thermal stability over RP-1. **No improvement was obtained**
— JP-7 deposits were actually "darker and more uniform" than RP-1's under microscopy, though
deposit-rate magnitude was "generally of the same order" as RP-1. An unsparged-JP-7
diagnostic test (checking whether dissolved-O2 removal interacted badly with antioxidant/
lubricity additives) gave similar deposit formation, so the negative result wasn't an
artifact of the sparging process. Testing with JP-7 was suspended as offering no thermal-
stability benefit. **Implication**: fuel refinement/purity alone (lower sulfur, lower
dissolved oxygen) is NOT a reliable coking mitigation for this rig/fuel-pair — the wall
material (nickel plating) mattered far more than the fuel grade.

**Propane fouls worse than kerosene fuels, and near-critical propane shows thermal
instability** `[Lewis-Deposits, Propane Tests p.8-9; Concluding Remarks p.12-13]`: commercial
and chemically-pure propane both produced heavier, blacker, more uniform deposits than the
kerosene-type fuels (RP-1/JP-7) at any given wall temperature, and carbon-deposition rates
for propane (400-600 µg/cm²·hr at 422/589K test points, similar magnitude to RP-1's peak
band but measured at LOWER wall temperatures) were "generally higher than those obtained for
either of the kerosene fuels at any given wall temperature." Little difference was found
between commercial-grade and chemically-pure propane. A distinct instability was observed at
high wall temperature (700-811K): tests had to be terminated prematurely because wall
temperature fluctuated excessively and exceeded the 866K rig safety cutoff; this was traced
to the propane's BULK fluid temperature exceeding its **critical point (366K)**, in a regime
(bulk temp 400-500K at 136 atm) where propane's specific heat "changes very rapidly and
passes through a maximum" — i.e. near-critical transport-property swings (density,
viscosity, thermal conductivity) likely drove erratic local heat transfer, not the coking
deposit itself. **A dendritic (tree-like) copper-filament deposit morphology** unique to
propane was also observed at high wall temp — SEM/microprobe showed the filaments were
primarily COPPER (with carbon concentrated at the base), i.e. the copper substrate itself
was being eroded/redeposited, a qualitatively different and more severe failure mode than
the kerosene fuels' surface-coke buildup.

**Deposit morphology is non-uniform and unpredictable** `[Lewis-Deposits, Kerosene Fuel
Tests p.6; Deposit Morphology p.10-11; Concluding Remarks p.12-13]`: post-test sectioning of
RP-1-fouled tubes showed deposit coverage ranging from bare specks to connected islands to
essentially full coverage, with no pattern correlating to test conditions — the authors
explicitly state this non-uniformity made "a determination of the point of incipient deposit
formation impossible," i.e. there is no crisp threshold temperature in the data, only a
statistical band (600-800K, peak near 700K). SEM imaging (5000x) showed deposits are
NOT smooth continuous films but discrete ~0.5 µm spherical agglomerated particles (kerosene
fuels, "coke"-like) or dendritic filaments (propane) over a fused substrate — surface
roughness and composition vary along the tube length and would be expected to affect local
heat transfer non-uniformly (i.e. a uniform fouling-resistance assumption along a real
cooling channel is itself an approximation). Also: deposition rate changes with TIME, so
test/exposure duration matters to any rate correlation (all rig data here is for a fixed
10-minute exposure — not directly extrapolable to multi-minute-to-hour real engine burn
durations without a time-dependence model this report doesn't provide).

## Design method

Not a sizing/correlation source in the Bartz/Dittus-Boelter sense — no closed-form deposit-
rate-vs-(T,P,V) equation is given (the report explicitly notes data scatter precluded even a
clean graphical trend for propane at high temperature). The usable outputs are: (1) a real
measured coking onset/peak temperature band for RP-1 (600-800K onset, peak ~700K) as a
independent corroboration/refinement of the single-point `[SP-8087]` 850°F(728K) figure
already cited in `topics/06`; (2) real deposit RATE magnitudes (400-600 µg/cm²·hr for RP-1,
similar-or-higher for propane) as an order-of-magnitude anchor if `engine_designer` ever
wants a fouling-resistance/service-life estimate rather than a binary coking-limit flag; (3)
a real, quantified material mitigation (nickel plating, ~10x rate reduction) as a citable
design lever beyond "just stay under the wall-temp limit"; (4) the pressure-independence and
velocity-dependence (higher coolant velocity → less deposit) findings, both directly
actionable for a regen-channel design tool that already computes coolant velocity.

## Section map

- Report Documentation Page (title, authors, abstract): leaf 1 — read.
- Introduction: leaf 2-3 — read.
- Test Facility and Test Hardware: leaf 3-5 — read.
- Experimental Results and Discussion — Kerosene Fuel Tests: leaf 5-8 — read in full, most
  of the citable content above.
- Propane Tests: leaf 8-9 — read.
- Nickel-Plated Tube Tests: leaf 9-10 — read.
- Deposit Morphology (SEM/SEMP analysis): leaf 10-12 — read.
- Concluding Remarks: leaf 12-13 — read (restates all key numbers, used to cross-check OCR).
- References (9 citations, incl. the authors' own earlier full report NASA CR-165405 Aug
  1981, and Wagner & Shoji AIAA-75-1247 on regenerative cooling techniques — both potential
  future-source leads, not yet in `claude_lit`): leaf 14 — read (titles only, not chased).
- Figures 1-8 (test apparatus schematic, duplex tube cross-section, wall-temperature-
  distribution plots, thermal-resistance-buildup-rate plot, carbon-deposition-rate-vs-
  temperature plot for RP-1, propane wall-temp comparison, SEM photomicrographs, SEMP
  elemental maps): leaf 15-20 — OCR/rasterized garbage (scanned plot axes, not text); not
  independently re-read as images. All numeric claims above came from body-text narrative
  cross-checked against the Concluding Remarks restatement, not reconstructed from these
  plots — so the specific onset/peak temperatures and rate magnitudes are captured, but no
  attempt was made to digitize exact curve shapes (e.g. the precise rate-vs-temperature
  bell-curve shape in Fig. 5, or the velocity-dependence slope).

## Caveats

- **This is a standalone electrically-heated test-tube rig, not a firing rocket engine** —
  no combustion, no real gas-side heat-flux profile; the tube is heated directly by resistive
  power to hit a TARGET wall temperature. Directly analogous in character to `[TN-Dump]`'s
  small-engine rig already cited in `topics/06` — real coolant-side wall/deposit physics, but
  not a full-engine validation.
- **Fixed 10-minute test duration** — deposition rate is explicitly noted to change with
  time; these rate magnitudes (400-600 µg/cm²·hr) are NOT directly extrapolable to a real
  engine's full burn duration (seconds to many minutes) without a time-dependent fouling
  model this report doesn't provide. Treat the rate numbers as a magnitude/order-of-
  magnitude anchor, not a design life-prediction formula.
- **Only 136-340 atm (13.8-34.5 MPa) and 422-821K tested** — outside this Pc/T range
  (e.g. very low-Pc engines, or wall temps below 422K) the report offers no data; the
  "pressure-independent" finding is only established across that specific pressure band.
- **Copper-vs-nickel-plated comparison is qualitative "similar conditions," not a matched
  controlled pair** — the report states nickel tests were run "at conditions which resulted
  in high rates of carbon deposition on copper" but doesn't claim bit-for-bit identical
  test points; treat the ~10x reduction as a real, large, and clearly-stated effect, not a
  precision-calibrated ratio.
- **OCR quality is poor** (scanned 1983-vintage NASA CR, "Depwit Formation" title-page
  garbling, split/duplicated digits in places like "811K"/"821K" abstract-vs-body
  discrepancy). All quantitative claims above were confirmed present in at least two
  independent restatements within the body text (abstract, results narrative, concluding
  remarks each repeat the key figures) before being included; figures/tables (leaf 15-20)
  were not independently re-rendered as images to cross-check plotted values, so anything
  not stated as a number in the prose (e.g. exact curve shapes) is not captured here.
- **Executive-summary-level report** (13 pages) — the authors' own full report is a separate
  NASA Contractor Report CR-165405 (Aug. 1981, same three authors, cited as Ref. 7) which
  likely has the complete data tables/figures and possibly a fitted rate correlation; not
  acquired or read for this note — flagged as a potential follow-up literature target if a
  quantitative coking-rate correlation (not just onset temperature) is ever needed.
- **No regenerative-cooling-JACKET geometry, channel-design, or manifold content** — this is
  purely a fuel-stability/deposit-chemistry study; no channel-width, aspect-ratio, or
  pressure-drop treatment (unlike `[SP-8087]`/`[Sutton §8.3]` already in `topics/06`).
