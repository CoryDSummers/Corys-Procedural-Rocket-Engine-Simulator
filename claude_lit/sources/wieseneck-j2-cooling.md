# Wieseneck (Rocketdyne) — Regenerative Cooling for J-2 / Space Shuttle Engine

## Identity

Henry C. Wieseneck (North American Rockwell, Rocketdyne Division, Canoga Park, CA),
untitled technical presentation on regenerative cooling for liquid rocket thrust chambers,
framed around the J-2 engine and the (then-in-development) Space Shuttle Main Engine.
`literature/Wieseneck (Rocketdyne c.1970) - Regenerative Cooling for J-2 and Space Shuttle Engine.pdf` (NTRS 19700030313; 32 PDF leaves, ~1970 — no explicit date or report number found
in the extracted text; content places it squarely in the SSME early-design-study era,
pre-hardware). No NASA CR/TN/TM number is legible anywhere in the extracted text — this
appears to be a standalone Rocketdyne viewgraph-style presentation, not a numbered report.
Tag: `[Wieseneck-J2]`.

## Character

A management/technical-overview presentation (chart-by-chart narrative captions, most
actual figures/charts are OCR-unextractable line drawings and bar charts — same limitation
as `[Marquardt-5981]`). Purpose: argue that regenerative cooling, proven on J-2-class
engines, scales up to meet the Space Shuttle Main Engine's much harsher requirements
(3000 psia Pc, 4× J-2's heat flux). Real content is in body-text captions under each chart,
not in the (unreadable) charts themselves.

Very short (32 leaves, many blank/chart-only pages) — read in full.

## Key results

**Real heat-flux and Pc anchors** `[Wieseneck-J2 p.6, 12]`: current (~1970) O2/H2 engines
(J-2, "5-2S" [OCR-garbled J-2S], M-1) experience heat fluxes of **17–35 Btu/in²·sec**; the
Space Shuttle Engine design point is **72 Btu/in²·sec at 3000 psia Pc** — stated as "four
times as high" as J-2's. This is a useful additional real-engine anchor point for
`claude_lit/topics/06-cooling-and-heat-transfer.md`'s existing heat-flux-magnitude table
(currently `[Huzel]`/`[Sutton]` 0.5–50 Btu/in²·sec / <50–>16,000 W/cm² range) — SSME's
72 Btu/in²·sec sits at the high end but within that band, and the J-2-class 17–35 range is a
concrete mid-thrust bipropellant-hydrogen data point.

**Construction-method taxonomy, historical progression** `[Wieseneck-J2 p.2, 20]`: "The
thrust chambers used for the early V-2 and Redstone rockets utilized a **simple double wall
construction**. Later chambers utilized **tubular construction**. Current engines rely on
both tubes and **channel wall constructions**. The latter is a modification of the earlier
double wall technique." This gives a real historical lineage: double-wall (V-2/Redstone,
1940s-50s) → tubular (mainstream mid-century) → channel-wall (SSME-era and later), with
channel wall explicitly framed as a *descendant of* double-wall, not an unrelated invention.
**Note**: this "double wall" is a generic early construction category, not specifically the
Soviet "sandwich" wall (see Caveats) — no Russian-specific construction detail appears
anywhere in this source.

**Channel-wall advantages over tubular** `[Wieseneck-J2 p.20]`, stated plainly as
Rocketdyne's own rationale for the SSME-era shift away from tube walls: channel wall (a)
gives a **smooth hot-gas wall** (vs. the corrugated/round-tube hot surface), reducing heat
load; (b) allows tightly-controlled, machined flow areas (vs. tube-forming tolerances); (c)
is more rugged/durable; and (d) — the "chief advantage" — **takes full advantage of the
thrust-chamber wall material's thermal conductivity**, because flow/area variations in any
one channel are smoothed out by lateral conduction to adjacent channels through the solid
wall land — a self-correcting effect tube walls (thin, low-conductivity paths between tubes)
don't have. Tubular construction is stated to have been used "almost exclusively" for nickel
and stainless-steel chambers (lower-conductivity alloys), consistent with channel-wall's
conductivity-dependent advantage being most valuable for high-conductivity copper alloys.

**Real material/temperature/pressure limits** `[Wieseneck-J2 p.16, 18]`: conduction-limit
wall-thickness analysis assumed a **400°F coolant-side wall temperature** (stated as
"typical of the SSME throat"); max gas-side wall temperature **1000°F for the two copper
materials analyzed, 1400°F for nickel and stainless steel**. **Stainless steel and nickel are
called out as unacceptable for high-Pc operation**; **annealed OFHC copper can reach chamber
pressures approaching ~4000 psi**; a copper alloy (**NARloy**) — high strength + high
thermal conductivity — is named as the enabling material for the SSME's Pc regime. The
**coolant pressure-drop practical limit is stated as ΔP ≈ 0.1 × Pc** (one-tenth of chamber
pressure) — a real, if simply-stated, design rule directly comparable to `design.py`'s
`JACKET_DP_PA` treatment (topic 06 already has real jacket-ΔP anchors of 100–540 psi across
RS-27/RL10B-2/LE-7; at Pc 3000 psi, this source's 0.1×Pc rule implies ~300 psi for SSME-class
— consistent with, not contradicting, that existing anchor band).

**Reliability claim** `[Wieseneck-J2 p.4]`: "over 4000 applications of regeneratively cooled
engines" across US space boosters and ballistic missiles, with **failure-free operation on
all of these flights** — a broad reliability claim (not attributable to a specific engine),
useful as qualitative context but not a citable failure-rate number.

**No manifold-specific content**: this source discusses chamber-wall construction and
material/thermal limits only; it does not describe coolant manifold/inlet-distribution
design at all (checked specifically per the user's interest in manifolds — nothing found).

## Design method

Not a derivation source — this is an overview/advocacy presentation citing Rocketdyne's own
internal design charts (unreadable) rather than deriving new equations. The value is in the
real numeric anchors and the construction-method rationale quoted above, comparable in kind
to `[Marquardt-5981]`'s figure-caption-derived numbers.

## Section map

- p.1 (leaf 0): Introduction — read.
- p.2 (leaf 2): Regeneratively cooled thrust chamber, construction-method taxonomy — read.
- p.4 (leaf 4): Engine launches / reliability claim — read.
- p.5-7 (leaf 5-7): charts, OCR-unreadable — captions embedded in surrounding text pages,
  no separate caption text found.
- p.6 (leaf 6): Thermal characteristics of propulsion systems, real heat-flux numbers —
  read.
- p.11-12 (leaf 11-12): Performance gain from regeneration (chart, mostly unreadable) / Space
  Shuttle Engine intro — read.
- p.16 (leaf 16): Allowable regenerative cooling regimes — material limits — read.
- p.18 (leaf 18): O2/H2 regenerative cooling feasibility limits — read.
- p.20 (leaf 20): Construction methods (tube vs. channel) — read.
- p.22 (leaf 22): Recent Rocketdyne regenerative cooling contracts (context only, no
  extractable data) — read.
- p.30 (leaf 30): Space Shuttle requirements / conclusion — read.
- Remaining leaves (1, 3, 5, 7-10, 13-15, 17, 19, 21, 23-29, 31): blank or OCR-unreadable
  chart-only pages — skimmed, nothing extractable.

## Caveats

- **Chart-only pages are not OCR-extractable** — same limitation as `[Marquardt-5981]` and
  other scanned-report sources in this reference set; only the body-text captions
  surrounding each chart were usable.
- **No formal report number found** — cannot confirm this document's official NASA
  accession/report identity beyond its NTRS accession ID (`19700030313`, an NTRS-style ID). Treat as
  a real Rocketdyne technical presentation, not a peer-reviewed or design-criteria document.
- **"Double wall" ≠ Russian "sandwich" construction**: this source's V-2/Redstone "double
  wall" reference is a generic early Western construction category (two shells with a
  cooling-fluid gap between them, structurally simple), not the specific Soviet diffusion-
  bonded corrugated/finned "sandwich" wall construction the user asked about — no Russian-
  specific construction technique appears anywhere in this source. See `[AIAA-1991-2510]`
  (Gubanov) if that source is distilled separately for the actual Russian construction
  detail.
- Pre-hardware SSME context (design-point projections, not as-built/flown data) — the
  72 Btu/in²·sec and 3000 psia figures are design targets circa ~1970, not flight-validated
  SSME numbers (though they turned out to be close to the eventual real engine).
