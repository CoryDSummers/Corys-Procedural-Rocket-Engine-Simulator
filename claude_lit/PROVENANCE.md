# claude_lit — provenance & cross-check history

Moved out of `README.md` on 2026-09-22 so the index read on every lookup stays small. Nothing here is needed for a routine lookup; it records when/how each source was extracted and cross-checked. New extraction batches append a dated section at the end.

## Cross-check status (2026-09-05)

Nine extracted numbers were checked against `engine_designer/physics/validate.py`
`SPOT_CHECKS` and the tool's own constants. **No contradictions found** — every literature
value is consistent with an already-validated real engine or an existing tool constant:

| Extracted value | Literature | Tool | Verdict |
|---|---|---|---|
| Conical divergence factor λ(15°) | 0.983 `[Huzel eq. 4-8]` | `isentropic.py` self-check asserts ≈ 0.983 | exact match |
| LOX/RP-1 Tc @ MR 2.35, 1000 psia | 3589 K `[Huzel Sample 4-1]` | `_TABLES` interp ≈ 3609 K | +0.6 %, within tolerance |
| LOX/LH2 vac Isp vs ε | 440 s @ ε 40 `[Huzel]`, 442 s @ ε 61 (RL10A-3-3), 462 s @ ε 285 (RL10B-2 `[Sutton]`) | validate.py anchors RL10A-3-3 at 442.2 s | monotonic in ε, consistent |
| Injector ΔP / Pc | 15–20 % of Pc `[Huzel §4.5]`; real 0.15–0.35 `[Sutton Table 8-1]` | `injectors.py` impinging `dp_over_pc_nominal` 0.175 | in band |
| GG turbine inlet temp | 1050 K (RD-0110, `[KBKhA Table 2]`); GG fleet 922–1061 K `[SP-8107 Table III]` | `design.py` `GG_TIN_K = 1050` | exact match |
| GG turbine efficiency | 46–70 %, most 55–66 % `[SP-8107 Table III]` | `design.py` `GG_ETA_TURBINE = 0.62` | mid-band |
| Advanced turbopump specific power | SSME 82 000–179 000 W/kg `[SP-8107 Table I]` | `turbopump_tech.py` `advanced` 70 000 W/kg | conservative, now sourced |
| Nozzle cooling-transition ε | radiation cooling beyond ε 6–10 `[Sutton §8.2]` | `design.py` `cooling_transition_eps` default 6.0 | conservative end of range |
| Gimbal deflection range | ±12° gimbal `[Sutton Table 16-1]`, ±10.5° op SSME `[Table 16-2]` | `gimbal.py` `GIMBAL_RANGE_TYPICAL_DEG` (2.0, 11.5) | 11.5 between operational and capability |

Two constants the literature lets us **upgrade** from "unsourced/estimate" toward "sourced":
`turbopump_tech.py` `advanced` specific power (ASSUMPTIONS.md item #41 — now bracketed by
`[SP-8107 Table I]`) and `design.py` `GG_TIN_K` (item #6 — matches `[KBKhA]` and `[SP-8107]`
exactly). One constant the literature suggests may be **too low**: `design.py`
`STAGED_COMBUSTION_PRESSURE_MULT = 1.6` vs `[SP-8107 Table VI]` "> 2.0 × Pc" and `[KBKhA]`
Pc ×2.3 → pump discharge ×3.4. See `topics/08-engine-cycles.md` implications.

## Provenance

**First batch, extracted 2026-09-05.** `literature/` and `Engine_Configs/` are read-only
references and were not modified. The two textbooks were sampled at the equation / chart /
worked-example pages; the four monographs were read more completely. Scanned-page OCR was
cross-checked against rendered page images for every transcribed equation and table.

**Second batch, extracted 2026-09-14.** Five new PDFs added to `literature/` since the first
batch were read and distilled into the five sources tagged `[CR-128318]`, `[SECA-HT]`,
`[Ch12-Materials]`, `[NK-33-Mod]`, `[Bazarov]` above, using a `pymupdf` venv (poppler-utils/
pypdf aren't installed in this sandbox — rebuild per the "How to use these notes" section if
needed). **Duplicate-file finding**: `literature/AIAA-1998-3361.pdf` and `literature/
MODIFICATION AND VERIFICATION TESTING OF A RUSSIAN NK-33 ROCKET ENGINE FOR REUSABLE AND
RESTARTABLE APPLICATIONS.pdf` are the same paper (identical PDF `/Title` metadata) — only the
former was read; the latter is an unflagged duplicate and a candidate for manual deletion
(not deleted here — distillation doesn't touch `literature/`). No cross-check-status table
entry was added for this batch: none of the five sources' extracted numbers directly
contradicted or newly-anchored a `validate.py` `SPOT_CHECKS` constant beyond what's already
noted inline in the relevant topic files' `## Implications for engine_designer` sections
(the NK-33 preburner-pressure-ratio anchor in `topics/08-engine-cycles.md` is the closest
candidate, and it confirms a change already made rather than suggesting a new one).

**Third batch, extracted 2026-09-16.** One new PDF, `literature/NASA SP-8120 - Liquid Rocket Engine Nozzles.pdf` (NTRS 19770009165; NASA
SP-8120, *Liquid Rocket Engine Nozzles*, Jul 1976), requested by name for two specific
sections (tube-wall retaining bands and manifold structural supports) needed for a real
design issue being worked in a parallel session. Distilled with the same `pymupdf` venv
method as the second batch; tagged `[SP-8120]`. Unlike the prior two batches, this source's
two requested sections (§2.2.1/§3.2.1 retaining bands + splice joints, §2.2.5.2/§3.2.5.2
manifold vanes/splitters/dams/structural supports) were read in full, but the remaining
~70% of the document (nozzle-contour tolerances, film/ablation/radiation-cooled *extension*
structure specifically, hot-gas/coolant-return manifold drainage and seals, nozzle
attachments, instrumentation, testing) was scanned for section headers only and not
deep-read — see `sources/sp8120-liquid-rocket-nozzles.md`'s Section map if one of those
areas is needed later. Folded entirely into `topics/12-materials-and-structures.md` (no new
topic file — this is real-hardware structural design precedent for an existing topic, not a
new subject area). No `validate.py`/`ASSUMPTIONS.md` constant was added or changed: `[SP-8120]`
is a criteria/practices source with no sizing equations, and it identifies a genuine modeling
gap (`mass_model.py` has no retaining-band/splice/manifold-structural-support model at all)
rather than a number to cross-check against one that exists.

**A second new PDF, also added 2026-09-16** (same batch as SP-8120, user asked to review
"regenerative cooling and plumbing"): `literature/Marquardt Report 5981 - Thrust Chamber Cooling Techniques for Spacecraft Engines Vol I.pdf` (NTRS 19630011163), The Marquardt Corp.,
*Thrust Chamber Cooling Techniques for Spacecraft Engines*, Vol. I, Report 5981, Jul 1963 —
tagged `[Marquardt-5981]`. A third file added in the same drop, `literature/duplicates/19710019929.pdf`,
turned out to be a **byte-identical duplicate of `[Huzel]`** (confirmed via `md5sum`) and
needed no extraction. `[Marquardt-5981]` was read via a fork (pymupdf venv, same method as
prior batches) focused on its cooling-method-selection section (§V, read in full) and one
fully-worked earth-storable design study (§VIII-A-1, read in full) — the source of its only
concrete regen-cooling numbers; the report's actual sizing method is 11 hand-drawn parametric
weight/feasibility graphs that are not OCR-extractable, so only text/caption-embedded numbers
were usable. Folded entirely into `topics/06-cooling-and-heat-transfer.md` (no new topic
file — same subject area as `[TN-Dump]`/`[Huzel]`/`[Sutton]`, corroborating rather than
superseding them). No `validate.py`/`ASSUMPTIONS.md` constant was added or changed: this
source's numbers are small-spacecraft-engine scale (20–10,000 lbf) and its own regen→
radiation cooled-eps cutoff (10:1) and coolant-passage-size/purge findings corroborate
existing tool patterns and flag two small unmodeled gaps (no minimum-channel-size check, no
purge-path concept) rather than giving a number to cross-check against an existing
`SPOT_CHECKS` entry.

**A fourth new PDF, also added 2026-09-16**, requested by name: `literature/AEDC-TR-70-204 - Altitude Developmental Testing of the J-2S Rocket Engine.pdf` (NTRS 874400),
Pillow (ARO, Inc.), *Altitude Developmental Testing of the J-2S Rocket Engine in Rocket
Development Test Cell (J-4)*, AEDC-TR-70-204, Sep 1970 — tagged `[AEDC-J2S]`. The user asked
for it specifically for tap-off-cycle information; it is the first source in this reference
set with real tap-off-cycle hardware/test data (prior tap-off coverage in
`topics/08-engine-cycles.md` was `[Sutton]`-level concept description with no real engine
numbers). Read via a fork (pymupdf venv, same method as prior batches), focused on the
engine-description section (read in full) and the per-firing results narrative (read in full
for the 3 of 11 firings with clean main-stage performance numbers; skimmed for idle-mode
findings in the rest). Folded into `topics/08-engine-cycles.md` (real anchors, caveats, and
an implications note on the real series fuel→oxidizer turbine arrangement and the still-
unanchored `TAP_OFF_DUMP_ISP_FRACTION`) and `topics/12-materials-and-structures.md` (a real
1:2 tube-splice-count corroboration of `[SP-8120]`'s splice-joint criteria, on the very same
J-2/J-2S engine family). No new topic file. No `validate.py`/`ASSUMPTIONS.md` constant was
added or changed: this is a development/troubleshooting test report (only 3 of 11 firings
gave clean performance data, and its own chamber-pressure readings are flagged uncertain due
to an unresolved pressure-tap-location ambiguity), so it's treated as real corroborating
hardware context rather than a tight calibration source.

**Fifth batch, extracted 2026-09-17.** No new PDF — a targeted re-read of an already-catalogued
source, `[Huzel]`, at the user's specific request (with a page number given by the user: PDF
leaf 122, section starting leaf 116, "Tubular Wall Thrust Chamber Design"). The first batch's
pass over `[Huzel]` §4.4 covered the cooling-METHOD-selection content (Bartz, Dittus-Boelter,
recovery factor) but not this tube/coax-shell STRUCTURAL-design sub-section — a real gap, not
a duplicate. Rendered leaves 116–123 as page images (pymupdf venv, same method as prior
batches) since the dense stress equations and Sample Calculation 4-4's numeric tables were too
OCR-garbled to transcribe reliably from text alone. Extracted: circular-tube combined stress
(eq 4-27/4-28), a longitudinal thermal inelastic-buckling criterion (eq 4-29 — a genuinely new
buckling formula this reference set didn't have before), the elongated-tube bending term (eq
4-30, driven by adjacent-tube pressure differential, with its own admittedly-estimated `K_A`
constant), the coax-shell combined-stress equation (eq 4-31), the cooling-passage pressure-drop
equation (eq 4-32), and Sample Calculation 4-4's real Inconel-X tube numbers for the A-1/A-2
engines at the throat. Folded entirely into `topics/06-cooling-and-heat-transfer.md` (no new
topic file) with a substantial `## Implications for engine_designer` addition: this round's
own `design.py` jacket-overpressure check (added 2026-09-16, the same session) used a generic
plate-bending proxy for lack of a better citation at the time — these equations show it should
instead be split per `wall_construction` type (`tube_wall` → eq 4-27's net-pressure/local-
tube-radius form, `coax_shell` → eq 4-31's full-local-radius form, `milled_channel` → still
needs `[Sutton §8.3]`, not yet read), and Sample Calc 4-4 gives a real spot-check anchor that
check currently lacks. No `validate.py`/`ASSUMPTIONS.md` change made in this batch — the
citations are ready but the code redesign they motivate is a separate, not-yet-planned
implementation step.

**Sixth batch, extracted 2026-09-19/20.** The user added a large batch of new PDFs to
`literature/` and asked for a general review "paying particular attention to manifolds,
regenerative cooling, and Russian 'sandwich' construction." Thirteen new files were found;
two were confirmed duplicates via `md5sum`/metadata and needed no extraction:
`literature/duplicates/19750012398.pdf` (byte-identical to the already-distilled `[SP-8107]`) and
`literature/duplicates/20160008869 (1).pdf` (byte-identical to the already-distilled `[Ch12-Materials]`).
The remaining eleven were distilled in parallel via forks (pymupdf venv; one fork,
`[SP-8048]`, required rendering page images and reading them visually since that 1971 scan
has no text layer at all) into the eleven new sources tagged `[SP-8087]`, `[Gubanov-1991]`,
`[EUCASS-2023]`, `[Fagherazzi-2019]`, `[Wieseneck-J2]`, `[Merkle-RegenCFD]`, `[SP-8109]`,
`[SP-8048]`, `[PSU-CoaxAtom]`, `[NASA-TN-Acoustic]`, `[J2X-Overview]` above, then integrated
by hand into `topics/05`, `06`, `08`, `09`, `12`, `14` and this file.

**The headline finding for the user's specific ask**: Russian "sandwich" wall construction
(two thin face sheets with a corrugated/finned core diffusion-bonded or brazed between them,
forming many parallel coolant channels — used on high-Pc engines like RD-170/RD-253/RD-180)
was searched for explicitly across every new source, including `[Gubanov-1991]` (a paper by
Energia's own chief designer, the single most likely-looking candidate by name) — **it was
not found in engineering detail anywhere**. `[SP-8087]` (NASA's dedicated fluid-cooled-
chamber monograph) confirmed the closest Western concept is "double-wall construction," a
functionally much simpler single-helical-channel design used only on small low-heat-flux
units (Atlas vernier, Aerobee), explicitly not the high-heat-flux multi-channel Russian
construction; `[Gubanov-1991]` itself gives real RD-170/RD-120/RD-0120 spec tables but only
one generic sentence per engine on chamber construction ("brazed-welded unit," no
cross-section); `[Wieseneck-J2]` and `[Fagherazzi-2019]` independently confirmed the same
negative (their own "double wall"/construction-type literature reviews don't cover it
either). **This remains an open gap in `claude_lit` — a Russian-specific materials/
manufacturing source, not a US design-criteria or program-status document, would be needed
to fill it.** See `topics/06-cooling-and-heat-transfer.md`'s dedicated paragraph for the
full search summary.

**Manifolds and regenerative cooling, by contrast, were well served by this batch**:
`[SP-8087]`'s §2.1.2/§3.1.2 gave real, dimensioned manifold hydraulic-design criteria (20%
first-pass flow-maldistribution tolerance, two competing toroidal inlet-manifold design
philosophies, a real propellant-class turnaround-topology rule, a 0.5-1 in manifold-to-thin-
wall transition-taper criterion) that complement rather than duplicate `[SP-8120]`'s existing
manifold-structural-supports content; `[Fagherazzi-2019]`'s thesis independently arrived at
the *exact same* constant-target-velocity volute-sizing continuity equation
`manifold.py` already implements, a real second precedent for that design pattern.
`[SP-8087]` also gave several genuinely new dimensioned regen-cooling numbers (tube-vs-
channel-wall selection thresholds by heat flux/thrust, tube taper/thickness limits, coolant
velocity limits) that `[SP-8120]` didn't have; `[EUCASS-2023]` gave a real, quantified
Bartz-calibration-error magnitude (independent corroboration that `cooling.py`'s per-
propellant-class calibration approach is necessary, not optional) plus a two-phase CHF
treatment `cooling.py` doesn't attempt; `[Fagherazzi-2019]` also gave a richer coolant-side
Nu-correlation set and a real jacket-ΔP-as-fraction-of-inlet-pressure rule (15-22%).

**Two more consequential findings, outside the user's three flagged topics but from the same
batch**: `[SP-8109]` gave a real, quotable suction-specific-speed design limit (40,000 with
an integral inducer / 12,000 without) that directly backs the pending NPSH/suction-specific-
speed feature plan's seed value — previously that constant rested only on a two-anchor-point
derivation. `[SP-8048]` (the dedicated NASA bearings monograph) gave a real bearing DN
ceiling (3.0×10⁶ DN for rolling-element bearings without dedicated qualification testing) —
`turbopump_materials.py`'s `max_dn_mm_rpm` values were previously flagged in
`ASSUMPTIONS.md` as an unsourced Tier-3 estimate with no citation at all; this is the first
real citation for that flag, though the tool's per-material gradation still isn't confirmed
by this monograph's single blanket ceiling.

No `validate.py`/`ASSUMPTIONS.md` constant was changed in this batch — every finding above is
report-only, following this file's standing rule that literature notes propose no edits.
The two most actionable next steps this batch surfaces (upgrading the NPSH plan's citation
and the bearing-DN Tier-3 flag) are both additions to existing planned/flagged work, not new
code changes made here.

**2026-09-23 targeted re-read (no new PDFs).** User pointed at three already-distilled
sources for tube-wall construction detail: `[Huzel]` p.113-114 (PDF 122-123, swage/hydroform
-> bend -> brazing-fixture gap distribution), `[SP-8087]` §2.1.1.3 p.12-14 (PDF 28-30, Fig. 1
tube taper/bifurcation, "spanking", fit-up) and `[SP-8120]` §2.2.1.1 p.29 + Fig. 40 (PDF 43,
86, band spacing/width rule and band cross-sections, Fig. 40 read as a rendered image).
Text via the pymupdf venv, figures rendered with `page.get_pixmap()`. Folded into the
existing source notes and topics 06/12; drove `physics/hatbands.py` and the contiguous-tube
rendering. No validate.py spot-check constant came from these (no dimensioned band data).

## Seventh batch, extracted 2026-09-23

User asked for a review of "several new PDFs." Diffed `literature/` (40 PDF files) against
`claude_lit/sources/*.md` coverage via md5sum + title extraction. Found 9 "new"-looking
filenames were actually duplicates or renamed copies of already-covered sources (confirmed
via md5sum where sizes matched, or first-page-title extraction otherwise): the Gubanov AIAA
paper, the dump-cooled TN, the Bazarov hydrocarbon-injector paper, the KBKhA turbopump paper,
SP-8081 gas generators, the AEDC J-2S report, the CR-128318 combustor-effects report, the
SECA heat-transfer report, and Chapter 12 materials all arrived a second time under different
filenames. `sp8109.pdf` (distinct md5 from the already-covered `NASA SP-8109 - Liquid Rocket Engine Centrifugal Flow Turbopumps.pdf`) turned out
to be a redundant *image-only, no-text-layer* rescan of the same SP-8109 monograph — not even
useful as a supplement, since the already-covered copy has an OCR text layer and this one
doesn't.

**10 genuinely new sources**, dispatched to 10 parallel `lit-integrator` forks (each wrote
only its own `sources/*.md` note; the main session did the `topics/*.md`/`README.md`
integration pass afterward, per the established convention):

- `[Casiano-Throttling]` — a comprehensive AIAA throttling-methods survey; the first dense
  real-engine throttle-ratio/stability catalog in this reference set (LMDE 10:1, CECE 13:1,
  SSME 6.4:1, RD-170/171/180 minimums, RL10A-1 injector-stiffness-vs-chug-onset data).
- `[ChannelWall-IAC19]` — checked specifically against the still-open Russian-sandwich-wall
  gap (per the user's earlier explicit request); confirmed NOT the same technology (modern
  US AM/water-jet-milling processes) — the gap remains open after a sixth source checked.
  Gave real Inconel-625/JBK-75 hot-fire wall-temperature test anchors instead.
- `[Lewis-Deposits]` — real RP-1 coking onset/peak band (600-800K, peak ~700K) and rate data
  (400-600 µg/cm²·hr), the first rate/mechanism data behind the single-point `[SP-8087]`
  850°F coking threshold already cited in topic 06.
- `[TP2862-LOXRP1]` — real calorimeter hot-fire data independently corroborating
  `[EUCASS-2023]`'s CFD finding that uncalibrated Bartz/design-tool predictions under-predict
  real LOX/hydrocarbon throat heat flux (~60% high here, ~100K wall-temp-low there) — one
  hardware source, one CFD source, agreeing. Also a real 99.5% LOX/RP-1 c* anchor and a real
  zoned-injector 47%-flux/4.5%-C*-cost film-cooling tradeoff.
- `[MatCh2]` — real quantitative Cu-alloy chamber-liner properties (first numeric table for
  GRCop-84/NARloy-Z/Cu-Cr-Zr in this reference set) and real Hydrogen Environment
  Embrittlement Index data — the single most actionable new number: Inconel 718's HEE
  resistance flips from Extreme to Small purely from solutionizing temperature (1750°F vs
  1900°F), directly explaining `[Ch12-Materials]`'s existing J-2 718-forging anecdote with
  real index numbers. Also real LOX/GOX ignition thresholds (titanium/magnesium red flag).
- `[Aerospike-CR135231]` — background-only reference for a nozzle type `engine_designer`
  doesn't model at all (no aerospike/plug-nozzle physics exists); real MOC contour method,
  cooling topology, and differential-throttling TVC formulas, explicitly flagged as not
  filling any current gap.
- `[STBE-PW]` — a 392-page 1989 P&W booster-engine conceptual-design study, the richest single
  new source: seven real fully-worked engines (GG/split-expander/tap-off, three hydrocarbon
  fuels) giving a new "split expander" cycle variant, a second real LOX/CH4 tap-off data
  point, a regen-channel design-rule set recurring unchanged across all seven variants, a
  second independent bearing-DN fleet anchor, and a real applied Helmholtz-liner geometry.
- `[Tripropellant-CR150444]` — background-only for an unmodeled dual-mode/tripropellant
  architecture; independently corroborates (from a completely separate 1977 source) both the
  RP-1-cooling-Pc-limit finding already in `cooling.py` and the LOX-rich-vs-fuel-rich-
  preburner-infeasibility rationale already in `staged_combustion.py`.
- `[Agena-CR120362]` — mostly vehicle-bus/mission-ops material with low relevance to
  `engine_designer`, as predicted before reading; one citable pocket (a small hypergolic
  engine's propulsion section) gave a real bomb-test stability acceptance criterion and a
  hot-pump-restart thermal-margin precedent.
- `[ReducedPressTank]` — reviewed and explicitly assessed as low-value (a coursework-grade
  USRA student report adapting secondhand, unverifiable NLS piping data at the wrong scale
  for `manifold.py`'s injector-face-manifold domain); the fork correctly said so rather than
  overstating its usefulness. Not folded into any topic file.

Folded into `topics/02, 03, 05, 06, 08, 09, 11, 12, 14, 15` with `[Tag §x.y p.NN]`-style
cites; `README.md`'s citation table, topic-file index, and intro source count updated
(35 sources total). No `validate.py`/`ASSUMPTIONS.md` constant was changed — every finding
is report-only, per this file's standing rule. The most actionable follow-ups this batch
surfaces: the real Cu-alloy properties table and HEE index data for `materials.py`, the two
independent real bearing-DN fleet anchors, and the real Bartz-under-prediction corroboration
from actual fired hardware (not just CFD) for `cooling.py`'s calibration approach.

## 2026-09-23 — targeted re-read for regen passage geometry (engine_designer cooling audit follow-up)

Three parallel lit-integrator passes (pymupdf text + rendered images for garbled/rotated
tables) re-read `[Wieseneck-J2]` (all 32 leaves; several leaves previously marked "nothing
extractable" are image-only text with real content - corrected in its note),
`[SECA-HT]` (all 163 leaves; printed pp. 61-64 missing from the scan),
`[SP-8087]`, `[Sutton]`, `[Huzel]`, `[J2X-Overview]`, `[AEDC-J2S]`, `[ChannelWall-IAC19]`
and `[Merkle-RegenCFD]` for real channel/tube counts, dimensions, lands, hot-wall
thickness, jacket flow split and coolant state. Each touched note gained a "Regen passage
geometry ... (2026-09-23 re-read)" section. Result: almost no real SSME/F-1/RL10 passage
geometry exists in the collection; the key find is `[Wieseneck-J2 p.24-25]`'s H2
roughness/curvature enhancement, which engine_designer now implements
(COOLING_AUDIT.md follow-up). Folded into `topics/06`; gaps into `OPEN_QUESTIONS.md`.

## 2026-09-23 — numeric filenames renamed; duplicates moved to `literature/duplicates/`

At the user's request, all 24 unique NTRS-accession-numbered PDFs in `literature/` (e.g.
`19890006608.pdf`) were renamed to `<Report ID> - <Title>.pdf`, with titles taken from each
file's `sources/*.md` Identity section. The first page was checked for the three with no prior path
reference (CR-128318, CR-120362 Agena, SECA-FR-93-18). Every `literature/...` path in `sources/*.md`
and in this file was rewritten, and each now carries its NTRS accession number (`(NTRS 19890006608)`) so it stays traceable.
The three md5-confirmed duplicates named above (`19710019929.pdf` = `[Huzel]`, `19750012398.pdf` =
`[SP-8107]`, `20160008869 (1).pdf` = `[Ch12-Materials]`) moved unchanged into
`literature/duplicates/`, which future literature reviews ignore (rule added to `CLAUDE.md` §3,
`README.md` and the `lit-integrator` agent). No content changed.

## 2026-09-24 — correction: Russian sandwich-wall construction was already in `claude_lit`

User pointed out that `[Ch12-Materials]` (Halchak et al., distilled 2026-09-14 — *before* the
"is Russian sandwich construction anywhere in claude_lit?" question was first asked in a
later batch) actually names and describes the technology in its §12.5.2. The prior six-source
"not found anywhere" conclusion (`topics/06-cooling-and-heat-transfer.md`, `OPEN_QUESTIONS.md`)
was accurate for the sources it checked but incomplete as a claim about `claude_lit` as a
whole, because it only checked sources added *after* the question existed and never swept
already-distilled sources. Re-read `[Ch12-Materials]` p.26-28 directly (pymupdf) and found
real detail: Cu-Cr inner liner + corrugated-sheet-metal divider + brazed outer shell, a
post-WWII pressure-brazing joining method ("solder-welding" in Russian usage) replacing an
originally-bolted 1930s design, real application on RD-107-class engines (sandwich for the
nozzle, channel-wall for the chamber), and — a genuine surprise — the **F-1's own lower
nozzle extension is sandwich construction too** (Hastelloy-C), so the technique isn't
exclusively Soviet. Corrected `topics/06`'s dedicated paragraph, expanded
`sources/ch12-materials-liquid-propulsion.md` with the full quotes/detail, updated
`README.md`'s `[Ch12-Materials]` citation-table description, and narrowed (not closed)
`OPEN_QUESTIONS.md`'s gap entry to what's actually still missing: dimensioned design
criteria (channel/corrugation geometry, wall thickness, structural formula), which
`[Ch12-Materials]` still doesn't give. **Process lesson recorded in `OPEN_QUESTIONS.md`**:
a "search the literature for X" request should sweep already-distilled sources
(`sources/*.md` or the original PDFs), not just newly-added ones.

Also answered a second question this same turn (no file changes): how deep was the
`[SP-8120]` extraction (third batch, 2026-09-16)? Only the two sections requested by name at
the time — §2.2.1/§3.2.1 (retaining bands + splice joints) and §2.2.5.2/§3.2.5.2 (manifold
vanes/splitters/dams/structural supports) — were read in full; the remaining ~70% of the
84-page monograph (nozzle-contour tolerances, film/ablation/radiation-cooled extension
structure, hot-gas/coolant-return manifold drainage/seals, nozzle attachments,
instrumentation, testing) was only scanned for section headers, not deep-read. See
`sources/sp8120-liquid-rocket-nozzles.md`'s Section map for exactly which headers.

## 2026-09-24 — SP-8120 deep read (the remaining ~70%)

User asked to finish the SP-8120 deep read after the two prior corrections this session (the
Ch12-Materials sandwich-construction miss, and the SP-8120-depth question). Read every
remaining numbered subsection of §2 (State of the Art) and §3 (Design Criteria) via pymupdf
— clean OCR throughout, no image rendering needed. This is now the **first fully-read
NASA SP-8xxx monograph** in `claude_lit` (SP-8087/SP-8107/SP-8109/SP-8048/SP-8081 all still
have unread sections, per `OPEN_QUESTIONS.md`).

Two findings stand out as directly resolving previously-flagged needs rather than just
adding background:
- **§2.2.2/§3.2.2 (Film-Cooled Extensions) and §2.2.5.3/§3.2.5.3 (Hot-Gas Manifold)** are
  exactly the reading item flagged as needed for the planned turbine-exhaust-handling
  feature (`OPEN_QUESTIONS.md` item (0), plan `~/.claude/plans/floofy-dazzling-liskov.md`) —
  this resolves that item with real F-1 numbers: the film-cooled extension runs from area
  ratio 10:1 (end of regen) to 16:1, ~25-30% of turbine-exhaust coolant flow concentrated at
  the attachment region (experimentally determined, no analytical method existed), real
  Hastelloy-C/Inconel-625/347-CRES materials, ~0.5%-of-total-thrust real performance
  contribution, real omega-joint thermal-growth failure/fix precedent, and a real safety-
  relevant design criterion (never use looped-tube turbine-exhaust introduction with
  noncryogenic propellants — a real Atlas RP-1-trapping/LOX-RP-1-gel-detonation precedent).
  Folded into `topics/07-dump-cooling.md` (cooling physics) and `topics/12-materials-and-
  structures.md` (manifold structure/thermal-growth).
- **§2.2.5.1/§3.2.5.1 (Manifold Hydraulics)** gave a third real manifold-velocity criterion
  (60 fps liquid/Mach 0.25 gas) that actively conflicts with `[SP-8087]`'s already-cited
  200 ft/s/Mach 0.3-0.5 — flagged as a real, unresolved discrepancy in `topics/12` and
  `OPEN_QUESTIONS.md` rather than silently picking one.

Also folded: §2.1/§3.1 Nozzle Configuration real design criteria (throat-radius ratios,
a real nonequilibrium area-ratio-≈3 threshold, a real 20%-of-separation-pressure margin
rule + closed-form `Pwall/Pamb` correlation, real J-2 contour-manufacturing tolerances, and
real — if non-closed-form — plug/aerospike base-design guidance that partially offsets
`[Aerospike-CR135231]`'s total absence of base-flow physics) into `topics/02-nozzle-contour-
design.md`; §2.2.3/§2.2.4 (ablation/radiation-cooled extension structure) and §2.2.5.4/
§2.2.6 (coolant-return manifold, nozzle attachments — real braze-gap/joint-length
tolerances, F-1's real tube-to-manifold technique) into `topics/07`/`topics/12`. §2.2.7/§2.3
(instrumentation, testing) were read but yielded little of `engine_designer` relevance
beyond a real J-2 ground-test separation precedent — noted in the source file, not folded
into any topic file.

No `validate.py`/`ASSUMPTIONS.md` constant was changed — every finding is report-only, per
this file's standing rule.

## 2026-09-24 batch — Inconel X-750 datasheet

Cory asked to add Inconel X-750 to `materials.py`'s catalog. The `literature/` folder isn't
reachable from this cloud session (git-ignored; the fresh checkout has no local copy), and
`specialmetals.com` is blocked by this session's network egress policy, so Cory uploaded the
source PDF directly rather than it living in `literature/`: Special Metals Corporation,
*INCONEL alloy X-750*, Publication No. SMC-067 (Sept 2004) — the standard mill datasheet.
Extracted into `sources/smc067-inconel-x750.md` (tag `[SMC-X750]`) and folded into
`topics/12-materials-and-structures.md` (a new subsection near the existing `[SP-8120]`
hatband-material mention, plus an `## Implications for engine_designer` update). This
directly backs a new `materials.py` `inconel_x750` entry (density, thermal conductivity,
CTE, Young's modulus, and emissivity are real cited numbers; `allowable_stress_pa` stays a
Tier-3 derated judgment call, same bucket as `inconel_718`'s, since real cited yield data
sits far above any reasonable working allowable) — see `ASSUMPTIONS.md` for the exact tier
notes on each field.

## 2026-09-24 batch — H-1 engine manual (targeted)

Cory's turbine-exhaust feature (overboard duct / H-1 aspirator / F-1-J-2 nozzle injection)
needed the aspirator source that `OPEN_QUESTIONS.md` item (g) was waiting on.
`literature/H-1C-D_Manual.pdf` (Rocketdyne R-3620-1, 14.4 MB) was already on disk but had
never been distilled.

- **Method.** Cory approved a targeted read only. The PDF has an OCR text layer, so it was read
  with a throwaway stdlib script: zlib-decompress each content stream and join the `Tj`/`TJ`
  string operands. No pymupdf. That text was grepped for the exhaust system, GG, turbine and
  chamber-characteristic sections.
- **Output.** Extracted into `sources/h1-engine-manual-r3620-1.md` (tag `[H1-Man]`), and
  folded into:
  - `topics/07-dump-cooling.md` (a new "Turbine-exhaust disposal hardware" section);
  - `topics/10-gas-generators.md` (implications).
- Report-only here. The code use happens in the turbine-exhaust feature's own commits.

## 2026-09-24 batch — seventeen new sources (ninth extraction round)

Cory added a large new batch of PDFs to `literature/` and asked for a review. Diffed against
`sources/*.md`'s existing coverage (37 notes) rather than assuming everything was new, per
`CLAUDE.md` §3. Found 17 genuinely new sources, plus two files confirmed NOT new:
- `MAIN CHAMBER INJECTORS FOR ADVANCED HYDROCARBON BOOSTER ENGINES.pdf` title-matches
  `[Bazarov]`, already distilled.
- `sp8109.pdf` is a different (image-only, no text layer) scan of the same NASA SP-8109
  monograph already distilled as `sources/sp8109-centrifugal-turbopumps.md` (117pp vs. 124pp
  from a different scan pass) — strictly worse than the already-distilled copy, nothing
  gained from re-reading it.

Six numeric NTRS-accession filenames were renamed to `<Report ID> - <Title>.pdf` per
convention (`19670008176.pdf` → `NASA TN D-3836 - ...pdf`, etc. — the NTRS number is noted in
each source's own note). Distillation was parallelized across 12 `lit-integrator` forks (one
per source, or grouped for the short manufacturer datasheets and the three shorter RP-1
property papers); the `topics/*.md`/`README.md`/`OPEN_QUESTIONS.md` integration pass was done
personally afterward with all 17 new tags in hand at once, per the standing convention.

**Headline find — NASA SP-8124** (*Liquid Rocket Engine Self-Cooled Combustion Chambers*, Sep
1977, tag `[SP-8124]`): closes a gap explicitly flagged in `OPEN_QUESTIONS.md` (previously
known only second-hand via `[EUCASS-2023]`'s film-cooling citation). Gives a real
entrainment-based gas-/liquid-film-cooling model (Appendix A/B — closed-form pieces exist, but
the effectiveness curve itself is graph-based, not a single algebraic function), real ablative
and radiation-cooled chamber material criteria, and a new interregen/heat-sink chamber
architecture not previously in `claude_lit`. Folded into `topics/06` (cooling architecture/
film model), `topics/12` (ablative/radiation materials), and `topics/02` (nozzle-configuration
criteria — throat-radius ratios, separation-margin correlation, J-2 contour tolerances,
plug/aerospike base-design guidance).

**A second, independent closed-form film-cooling correlation — NASA TN D-3836** (Lucas &
Golladay, 1967, tag `[TN-D3836]`): a real modified Hatch-Papell correlation for near-throat
film-coolant injection, with three documented empirical fit modifications and a stated
validity range (~100 slot heights downstream). Between this and `[SP-8124]`, the
`OPEN_QUESTIONS.md` "SP-8124 still missing" gap is now resolved — folded into `topics/06`.

**Materials/structures — a dense sub-batch, folded into `topics/12`**:
- `[Miller-CuFatigue]` (NASA CR-134841, Miller 1974): the Manson Universal Slopes low-cycle-
  fatigue equation plus a real applied case (predicted 80 cycles vs. actual failure at cycle
  39) — the first citable method for `mass_model.py`'s throat fatigue estimate.
- `[Quentmeyer-CR185257]` (AIAA-90-2116, 1990): seven real hardware-tested chamber-liner
  life-extension concepts (TBC: 1450 vs. 393 cycles; tungsten-reinforced liner; high-aspect-
  ratio channels; low-stiffness closeout), a real RP-1 sulfur-corrosion-of-copper mechanism
  distinct from carbon coking, and a cooling-architecture-to-cycle-choice pairing rationale.
- `[GRCop84-TM2005]`/`[GRCop84-Tensile]` (Ellis et al., NASA Glenn, 2005/2012): resolves a
  previously-flagged internal composition "inconsistency" in `[MatCh2]` (turned out to be
  at.% vs. wt.% of the same alloy, not an error), and gives a real statistical multi-specimen
  temperature-dependent yield/UTS/elongation regression (cryo through 1000K) — a strong
  citation-upgrade candidate for `materials.py`'s Tier-3 GRCop-84 allowable stress.
- Four manufacturer alloy datasheets (`[SS304-TDS]`, `[SS321-TDS]`, `[Inc718-TDS]`,
  `[Ni200-TDS]`): real primary property data for alloys already named elsewhere in
  `claude_lit`. Notably, `[Inc718-TDS]` was confirmed to carry ZERO hydrogen-embrittlement
  data (mechanical/thermal only — `[MatCh2]` remains the sole HEE citation), and `[Ni200-TDS]`
  surfaced a real conflation risk (its favorable corrosion-resistance framing for hydrogen
  service is a DIFFERENT mechanism from `[MatCh2]`'s severe-HEE finding for nickel — flagged
  loudly in both the source note and `topics/12` so the two aren't merged).

**RP-1 as a regenerative coolant — four NIST-grade property papers, folded into `topics/06`**
(`[NISTIR6646-RP1]`, `[Akhmedova-RP1]`, `[Huber-RP1RP2]`, `[Outcalt-RP1RP2]`): give the
primary literature basis for whatever surrogate-mixture model underlies `thermo_tables.py`'s
baked RP-1 coolant-property tables — real measured density/viscosity/thermal-conductivity
data, two independent surrogate composition models, and a real citable batch-to-batch
compositional-variability bound (~2-4% on thermal conductivity alone). A companion finding
distinguishes RP-1's bulk thermal-DECOMPOSITION kinetics (a different quantity) from
`[Lewis-Deposits]`'s existing wall-surface deposit-RATE data — flagged explicitly not to
conflate the two.

**Background/corroboration sources**: `[Armstrong-MarsISRU]` (NASA TM-103729, Mars-ISRU
cooling study) is mostly background (its CO/O2 propellant chemistry has zero transfer value)
but contributed a richer supercritical-fluid Nu-correlation catalog and three independent
corroborations of existing design constants (aspect-ratio-8 channel ceiling, 811K copper
wall-temp limit, 15-20% injector-dP rule) — folded into `topics/06`/`topics/05`.
`[SSME-Orientation]` (Rocketdyne/Boeing training deck, 1998, Boeing-proprietary — derived
facts only, no verbatim reproduction) gave the most complete single real-engine full-cycle
station-by-station flow/energy-balance map in `claude_lit`, real turbopump stage-count
architecture, real hatband/tube counts, and the first SSME c*-efficiency number (99.6%) —
folded across `topics/03`, `topics/05`, `topics/08`, `topics/09`, `topics/10`, `topics/12`,
`topics/16`. `[RPE-J2Blog]` (a secondary enthusiast source, Rocket Propulsion Evolution) gave
real J-2 start/cutoff valve-sequencing detail, a second real dimensioned anchor for
`turbine_exhaust.py`'s `nozzle_injection` mode, and a well-documented vacuum-vibration
ASI-bellows flight-failure case — folded into `topics/07`, flagged explicitly as one tier
below the primary NASA/Rocketdyne sources already cited for the J-2.

No `engine_designer/` code or `ASSUMPTIONS.md` was touched — every finding above is
report-only, per this file's standing rule. `OPEN_QUESTIONS.md` was updated to mark the
SP-8124 gap resolved and add new pending-citation-upgrade candidates (GRCop-84 tensile data,
the RP-1 property papers vs. `thermo_tables.py`); the `topics/06`/`topics/12` file-size-cap
housekeeping flag was updated again, since this batch pushed both further over the 40KB cap.

## 2026-09-24 batch — two more sources (F-1 engine manual + a cycle-performance TM)

Cory added two more PDFs shortly after the seventeen-source batch above. Diffed against
`sources/*.md` (54 notes) as usual — both genuinely new. One numeric NTRS filename
(`19730016059.pdf`) was renamed to `NASA TM X-64749 - A Simple Performance Calculation
Method for LH2-LOX Engines with Different Power Cycles.pdf` per convention. Distilled via two
parallel `lit-integrator` forks; integration pass done personally.

**Headline find — the Rocketdyne F-1 Engine Familiarization Training Manual, R-3896-1** (tag
`[F1-Man]`): this is EXACTLY the source `OPEN_QUESTIONS.md` had flagged as item (b) of the
turbine-exhaust-handling feature's acquisition list for several batches running. A scoped read
of the 262-page manual gave real, previously-unavailable numbers: turbine-exhaust manifold
hydraulics (a decreasing-cross-section torus, 15 omega expansion joints, splitter plates/exit
vanes), a real film/mainstream temperature gap (1,138°F film vs. 1,922°F core at the 16:1
exit plane), 23-row shingle construction, a real F-1 heat-exchanger architecture (both LOX
AND helium coils in one shell, a richer third example of the pressurization-heat-exchanger
pattern already seen on H-1/J-2/Titan I), real tube counts and splice plane (178 primary →
356 secondary tubes at the 3:1 area-ratio plane, matching `[AEDC-J2S]`'s J-2S 180→360
1:2-splice pattern), a real turbine PR anchor (≈16.3 uprated / ≈15.8 baseline, independent of
`[H1-Man]`'s H-1 PR≈17.7), and a real GG feed-pressure budget chain (richer per-component
detail than `[SP-8081]`'s generic tables). **The single most load-bearing find**: a real,
dimensioned **30%/70% fuel bypass-vs-cooling split** at each fuel-down tube — a direct real
citation for `manifold.py`'s `manifold_bypass_fraction` parameter, which the tool's own
F-1-sourced `f1_split_reverse_flow` cooling topology already uses but previously had no cited
real fraction behind. Folded into `topics/07` (turbine-exhaust/cooling), `topics/09`
(turbine PR), `topics/10` (GG feed-pressure budget), and `topics/12` (tube counts, bypass
fraction). No F-1 turbine efficiency percentage was found in the sections read — flagged as
an open item.

**NASA TM X-64749** (Schmucker, MSFC, 1973, tag `[Schmucker-CycleCalc]`): a "simple
performance calculation method" comparing LOX/LH2 engine power cycles. **The PDF on disk is
truncated** — the title page and the report's own table of contents claim 42 pages, but the
file has only 23 PDF pages and the extracted text stops mid-derivation; the entire numeric
GG-vs-staged-combustion comparison section the paper's summary promises, and its real
1973-era worked engine examples, are simply absent from this copy. What survives (pp.1-16) is
still useful: a real closed-form GG-cycle Isp formula and its staged-combustion counterpart
(the k_m→1 limit of the same framework), a real derivation of why staged-combustion pump
discharge must build up from Pc plus the turbine's own ΔP (the mechanism behind `[SP-8107]`'s
already-cited design-guide rule), and a clean real LOX/LH2 c* curve fit — flagged as a
candidate cross-check for `combustion.py`'s baked equilibrium table, not yet checked. Two
other curve fits in the surviving pages are flagged OCR-uncertain, not for use without
re-verification. Folded into `topics/08` (cycle Isp derivation) and `topics/03` (c* curve
fit). Re-acquiring a complete copy is the obvious follow-up if the missing numeric comparison
is ever wanted.

No `engine_designer/` code or `ASSUMPTIONS.md` was touched. `OPEN_QUESTIONS.md`'s item (b)
(F-1 manual) is now marked resolved.

## 2026-09-24 — housekeeping: split `topics/06` and `topics/12`

Cory asked to fix the overdue 40 KB topic-file-cap violation flagged (and re-flagged, twice)
in `OPEN_QUESTIONS.md` across the last three literature batches, and to leave a clear pointer
for other agents/sessions about the new layout.

- **`topics/06-cooling-and-heat-transfer.md`** (was ~66 KB) was split. It keeps the core
  Bartz/Dittus-Boelter/radiation-cooling relations, the tube-wall/coax-shell structural-
  design equations (Huzel eq. 4-27..4-32, the A-1/A-2 sample calc), heat-flux magnitudes,
  the cooling-method-selection table, and the Bartz-calibration-error corroboration —
  deliberately kept together in the same-named file because `engine_designer/physics/
  mass_model.py` (3 docstrings) and `ASSUMPTIONS.md` (1 entry) point at this filename by
  name for the structural-design content, so no `engine_designer/` edit was needed. New
  file **`topics/06b-cooling-methods-and-chemistry.md`** (~36 KB) took cooling-method
  feasibility/construction-selection criteria, RP-1 chemistry (coking, sulfur corrosion,
  NIST coolant properties), film cooling, the coolant-side correlation catalog, and the
  Russian-sandwich-construction search. Result: ~31 KB / ~36 KB, both under cap.
- **`topics/12-materials-and-structures.md`** (was ~69 KB) was split. It keeps material
  selection/properties/alloy data (Ch12-Materials tables, MatCh2 HEE/ignition/superalloy/
  Cu-alloy data, both GRCop-84 sources, Miller-CuFatigue, Quentmeyer, the four manufacturer
  datasheets, SP-8124's ablative/radiation criteria, Gubanov's RD-170/120/0120 specs). New
  file **`topics/12b-structures-manifolds-and-hardware.md`** (~28 KB) took the structural/
  hardware cluster: SP-8120's retaining bands, AEDC-J2S's/F1-Man's tube-splice/bypass-
  fraction data, SP-8087's manifold hydraulics and six-method structural-support survey,
  Fagherazzi's volute-sizing corroboration, and SSME-Orientation's hardware anchors. Result:
  ~43 KB / ~28 KB — `12` itself is still a little over cap even after trimming (its
  remaining material-properties content is dense), a materially better outcome than 69 KB
  but not a perfect fix; flagged honestly rather than forcing an awkward third split.
- **One `engine_designer/` edit, a pure path-string fix**: `ASSUMPTIONS.md`'s
  `manifold_bypass_fraction` entry cited `claude_lit/topics/12-materials-and-structures.md`'s
  SP-8120 H-1 manifold content, which moved to `12b` — the one-word path was corrected
  (`12` → `12b`), zero physics/number change. Also added a note there that `[F1-Man §1-16]`
  now gives the same 30% figure a primary-source citation (Rocketdyne's own manual) instead
  of the current informal-web-source one — flagged as a pending citation-quality upgrade,
  not applied.
- **Cross-references fixed across the repo**: ~20 pointers in `sources/*.md`, `OPEN_
  QUESTIONS.md`, and other `topics/*.md` files that cited content which moved were updated
  to the new filename; pointers to content that *stayed* in the original-named files were
  left alone (checked individually, not assumed). `PROVENANCE.md`'s own older historical
  entries were deliberately left unchanged — a history log describes the layout as it was
  at the time, the same way a git log entry isn't rewritten when files later move.
- **`README.md`**: the `06`/`12` index rows were trimmed to their new scope, two new rows
  added for `06b`/`12b`, and the topic-file count note updated (16 → 18 files).
- **`OPEN_QUESTIONS.md`**: the Housekeeping section's "overdue" warning was rewritten to
  record the split as done.

No physics, no `ASSUMPTIONS.md` number, and no `validate.py` behavior changed — purely a
documentation reorganization.

## 2026-09-25 — web photos: F-1 / J-2 turbine-exhaust manifold shape (no new PDF)

Cory supplied a J-2 museum photo (Science Museum Group 1977-0402) and an F-1 callout photo
(heroicrelics.org — HTTP-only, not fetchable from this sandbox); the F-1 thrust-chamber photo
and the F-1 manifold cutaway were fetched instead from enginehistory.org *Rocket Propulsion
Evolution* §8.12 (`F-1ThrustChamber.jpg`, `F-1ExManNozzleExt.jpg`) and viewed as images. No
text extraction and no new citation tag: the findings (tangential single inlet / scroll,
forward-outboard placement on a neck, flame shield, visible omega joints) were folded into
`topics/12b` ("Real F-1 / J-2 exhaust-manifold SHAPE") and a caveat in
`sources/f1-engine-manual-r3896-1.md`, and applied in `engine_designer` (`ASSUMPTIONS.md`
"Injection SCROLL manifold"). Photos give shape and proportion only, not dimensions.

## 2026-09-25 — five new PDFs: Apollo primary propulsion, Shuttle OME (×2), Shuttle OMS
## design history, copper-diamond liner materials

Five new NTRS-numeric-named PDFs were found sitting undistilled in `literature/` (per the
project's standing "diff new PDFs against `sources/*.md` coverage first" convention). Cory
confirmed the token-cost estimate (two of the five are 213pp/322pp) and approved distilling
all five now. Renamed to the `<Report ID> - <Title>.pdf` convention (NTRS number kept in each
source note): `Apollo Working Paper 1195 - Apollo Spacecraft Liquid Primary Propulsion
Systems.pdf`, `ASR72-238 - Space Shuttle OME Reusable Thrust Chamber Final Data Dump.pdf`,
`13133-F-1 - Space Shuttle OME Platelet Injector Program Final Report.pdf`, `AIAA 85-1694 -
Orbital Maneuvering System Design Evolution.pdf`, `NSMMS 2018 - Rocket Engine Liner Materials
Copper-Diamond Alloys.pdf`. Read/drafted by 5 parallel `lit-integrator` subagents (one per
source, per the project's standing parallel-subagent convention for independent sources);
the topic-file/README/PROVENANCE integration pass below was done by the main session
afterward, with all five tags in hand at once for cross-referencing, per the same convention.

- **`[ApolloPP-1195]`** (1966 NASA MSC survey): the first real pressure-fed hypergolic engine
  data in `claude_lit` — a Table I spec comparison across the SPS/LM-descent/LM-ascent
  engines (N2O4/Aerozine-50, all pressure-fed/ablative), a real fuel-rich barrier-cooling MR
  (1.05 vs. bulk 1.6, LM ascent), real confirmation of the LM descent engine's pintle-type
  variable-area injector, and a real 1960s multi-material ablative-liner ply schedule. Folded
  into `topics/11-propellants.md` (new N2O4/Aerozine-50 subsection), `topics/05-injectors.md`
  (barrier-cooling MR), and `topics/06b-cooling-methods-and-chemistry.md` (ablative ply
  schedule).
- **`[ASR72-238]`** (1972 Rocketdyne, 213pp, ~2/3 deep-read — data tables required rendering
  to page images, OCR-garbled as raster/rotated text): a real comparative trade study, 7
  propellant combinations × regen vs. dump/film cooling, same 6000-lbf-class OME. Folded
  into `topics/06-cooling-and-heat-transfer.md` (real regen-vs-dump/film Δweight comparison,
  real material creep/fatigue-life data, Cb→Ti transition criterion), `topics/05-injectors.md`
  (real 15%-of-Pc injector-ΔP corroboration across all 7 pairs; injector type varying by
  cooling method for LOX/C3H8), and `topics/03-combustion-and-cstar.md` (a real 1970s
  RP-1-specific combustion-modeling limitation).
- **`[OME-Platelet]`** (c.1975 Aerojet, 322pp, ~2/3 deep-read — executive-summary sections
  and the full-scale-program technical core read in full, raw per-firing data tables
  skimmed/skipped): the first real platelet-injector (photoetched/diffusion-bonded plate
  stack) construction detail in `claude_lit`. Folded into `topics/05-injectors.md` (a fourth
  real injector-construction technique, cant angles, a real 24-28%-of-Pc pressure-drop
  anchor), `topics/03-combustion-and-cstar.md` (real JANNAF ERE performance-extraction
  method/data), and `topics/14-combustion-stability.md` (a new instability mode, "resurging,"
  its real fix, a real dual-tuned acoustic-cavity design, and a real chamber acoustic-mode
  frequency table).
- **`[OMS-DesignEvo]`** (1985 NASA JSC, 17pp, read in full): a real engineering-history
  narrative for why the Shuttle OMS switched from a pumped LOX/LH2 baseline to pressure-fed
  storable NTO/MMH (a real volume-constrained, not mass-constrained, tradeoff) and why
  Apollo-heritage ablative engines were rejected for a longer reusable duty cycle. Folded
  into `topics/08-engine-cycles.md` (the design-history narrative + redundancy-architecture
  rationale), `topics/11-propellants.md` (the volume-constrained tradeoff), and
  `topics/14-combustion-stability.md` (the cavity-vs-baffle reusability rationale).
- **`[CuDiamond-Liner]`** (2018 NASA MSFC/GTE, 24pp, read in full): an early-TRL
  "next-generation" copper-diamond composite chamber-liner material candidate — real
  measured thermal conductivity up to ~560 W/m·K (vs. GRCop-84's 300) at a real, large
  strength/ductility cost (UTS roughly halved, elongation collapsing to generally <1%).
  Filed into `topics/12b-structures-manifolds-and-hardware.md` rather than
  `topics/12-materials-and-structures.md` — the latter is already slightly over its 40 KB
  cap (see the 2026-09-24 split entry above), so this materials-by-subject entry was parked
  in the sibling file for space, flagged explicitly in both the topic file and README.

No `ASSUMPTIONS.md` numbers were changed and no `validate.py` behavior changed — this batch
is report-only, consistent with `claude_lit`'s standing convention. All touched topic files
were re-checked against the 40 KB cap after integration; none of the eight touched files
(`03`, `05`, `06`, `06b`, `08`, `11`, `12b`, `14`) crossed it (`12` remains at its pre-existing
~43 KB, untouched this batch).

## 2026-09-26 batch — five NASA turbopump design-criteria monographs (turbopump Round 0)

Downloaded from NTRS by report ID and renamed to the `<Report ID> - <Title>.pdf` convention.
The NTRS accession numbers are in each source note.
- SP-8052 inducers (19710025474)
- SP-8110 turbines (19740026132)
- SP-8125 axial-flow pumps (19780023221; its cover text layer is garbled, so the SP number was
  confirmed from a rendered page)
- SP-8121 shaft seals (19780022641)
- SP-8101 shafts and couplings (19740006328)

Method: one `lit-integrator` agent per PDF, in parallel. Each extracted text with pymupdf and
rendered the tables and figures that come out OCR-garbled to PNG, reading them by eye.
SP-8110 Figs 13/53/55 were digitized by pixel scan. Values derived from the sources rather
than printed in them are marked as such in the notes. The integration into
`topics/09-turbopumps.md` was done by the main session: a new "Real component data & design
criteria" section plus Round 0 implications. `topics/12-materials-and-structures.md` was not
touched, because it is still over its 40 KB cap; the seal-material and H₂-embrittlement items
went into topic 09.

Unlike most `claude_lit` batches, this one DID change `engine_designer` numbers, in the same
round (turbopump Round 0, commit 9d0cb17):
- the LOX/RP-1 GG gas cp `[SP-8110 Table III]`
- the open-cycle turbine staging rule `[SP-8110 §3.1.4]`
- the J-2 turbine-anchor pressure ratios `[SP-8110 Table I]`

Each is recorded in ASSUMPTIONS.md. Coverage: SP-8052, SP-8110 and SP-8125 were read in
design-relevant depth. For SP-8121, about 60 % was read (secondary-element, mounting and
hydrostatic detail was skipped). SP-8101 was read in §1–§3.
