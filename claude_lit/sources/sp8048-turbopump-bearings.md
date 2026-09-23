# NASA SP-8048 — Liquid Rocket Engine Turbopump Bearings

## Identity

NASA SP-8048, *Liquid Rocket Engine Turbopump Bearings*, NASA Space Vehicle Design Criteria
(Chemical Propulsion), March 1971. `literature/NASA SP-8048 - Liquid Rocket Engine Turbopump Bearings.pdf` (NTRS 19710018535; 84 PDF leaves; fixed offset
printed page N = PDF leaf N+5, e.g. printed p.3 is leaf 8, printed p.31 is leaf 36 — confirmed
by rendering and reading multiple pages). Tag: `[SP-8048]`.

**Technical note on this PDF**: unlike every other source in this reference set, this file is
a **pure image scan with no text layer at all** (1998 "Image Alchemy" scan, confirmed via
`fitz`: every page's `get_text()` returns an empty string). It cannot be read or grepped as
text — every citation below came from rendering a page to a PNG (`pymupdf`
`page.get_pixmap()`) and reading it visually. This note's extraction is therefore narrower
and more page-budget-limited than a text-searchable source; see extraction scope below.

## Character

Same parallel-numbered §2 (State of the Art, narrative) / §3 (Design Criteria, imperative
"shall") structure as `[SP-8120]`/`[SP-8107]` — this is the same NASA monograph series,
Cover TOC confirms the section-numbering mirrors 1:1 between State-of-the-Art and Design
Criteria (e.g. §2.1.2 Speed Capability ↔ §3.1.2 Speed Capability). Two top-level parts:
**Bearing Assembly Design** (§2.1/§3.1: load, speed, stiffness, misalignment, bore, internal
clearance, cooling, mounting, materials, testing) and **Bearing Component Design** (§2.2/§3.2:
rolling element, race, cage design) — this note only covers the first part.

This is the single most likely source in `claude_lit/`'s literature set to carry a real,
citable bearing-DN design limit — `engine_designer/physics/turbopump_materials.py`'s
`BEARING_MATERIALS.max_dn_mm_rpm` values (~1.2M/1.5M/2.4M) are flagged in `ASSUMPTIONS.md` as
an unsourced Tier-3 estimate. **This monograph does give a real, explicit numeric DN
criterion — see Key results below.**

## This note's extraction scope

Rendered and read (page-image, printed page numbers): title page; contents (p.v); p.3
(introduction to the two-part structure); **p.12-13 (§2.1.2 Speed Capability, State of the
Art, incl. Table III speed limits and two real uprating-failure anecdotes)**; **p.16
(§2.1.7 Cooling, State of the Art, incl. real coolant-lubricity ranking and DN achieved with
PTFE cages)**; **p.19-20 (§2.1.9 Bearing Materials, State of the Art)**; **p.31 (§3.1.1 Load
Capability + §3.1.2 Speed Capability, Design Criteria — the numeric DN design rule)**;
p.46 (§3.1.8.7.1 Clamping Loads + §3.1.9/§3.1.9.1 Bearing Materials, Design Criteria,
Corrosion Resistance). **Not rendered/read**: §2.1.1 Load Capability (State of the Art, full
text), §2.1.3-2.1.6 (Stiffness/Misalignment/Bore/Internal Clearance) beyond the one paragraph
visible on p.13, §2.1.8/§3.1.8 Bearing Mounting beyond the clamping-loads paragraph on p.46,
§2.1.10/§3.1.10 Testing, all of §2.2/§3.2 Bearing Component Design (rolling element/race/cage
detail design), References, Glossary, Table VI (materials-choices table referenced on p.46
but not rendered), and Figures 3, 8, 9, 18 (referenced in text, not rendered). This is a
~15-page sample of an 84-page monograph, chosen to target the DN-limit and
materials-selection content specifically per the requesting task's priority.

## Key results

**The numeric DN design criterion** `[SP-8048 §3.1.2 p.31]` (imperative "shall" text: "The
bearing shall satisfy the speed requirements of the application"), followed by four concrete
recommendations:
1. **One-piece cages should be used for speeds over 1.0×10⁶ DN.**
2. **Angular-contact ball bearings should be used for speeds between 1.0×10⁶ and 3.0×10⁶
   DN.**
3. Reference 8 should be consulted for maximum speeds with cylindrical roller bearings.
4. **Rolling-element bearings should not be used for speeds over 3.0×10⁶ DN without prior
   testing.**

This is a real, citable **ceiling of 3.0×10⁶ mm·rpm** for rolling-element bearings in
general (without dedicated qualification testing), with **1.0-3.0×10⁶ DN** as the
angular-contact-ball recommended operating band. This is noticeably **more permissive**
than `engine_designer/physics/turbopump_materials.py`'s current flagged-estimate
`max_dn_mm_rpm` values (~1.2M for 440C steel, up to ~2.4M for the most capable material) —
the tool's numbers may be conservative relative to this real 1971 NASA design criterion, or
the tool's per-material gradation (steel vs. Cronidur 30 vs. ceramic) may be a reasonable
finer-grained scheme *within* this document's single blanket ceiling. Either way, this gives
`ASSUMPTIONS.md`'s Tier-3 DN-limit entry a real citation to point to for the first time.

**Real achieved/tested DN data points** `[SP-8048 §2.1.2 p.12-13]` (Table III, "Speed Limits
for Bearings"):

| Bearing type | Existing max turbopump DN (million) | Existing max test DN (million) | Limiting factor | Test coolant |
|---|---|---|---|---|
| Conrad-type ball | 1.6 | 1.6 | Cage weakness | Liquid hydrogen |
| Angular-contact ball | 2.05 | 3.0 | Heat generation | Liquid hydrogen |
| Cylindrical roller | 1.6 | 1.6 | Roller guidance, cage slippage | RP-1 |

Real uprating anecdotes: **Atlas/Thor** turbine-shaft thrust bearings (Conrad, phenolic
cages) ran fine at 1.2×10⁶ DN, but failed when speed/load rose ~10% for **H-1** engine
service — fixed by switching to split-inner-ring bearings with one-piece bronze cages.
**J-2** fuel-pump bearings at **1.6×10⁶ DN** with extended-life requirements suffered cage
failures (two-piece riveted Armalon/PTFE-glass-fabric cages) — fixed by switching to a
one-piece (otherwise identical) cage design. Both anecdotes reinforce the design criterion's
own emphasis on one-piece cages above 1.0×10⁶ DN.

**Coolant/lubricant ranking** `[SP-8048 §2.1.7 p.16]`, descending bearing-lubricating
ability: **RP-1 > liquid oxygen > liquid hydrogen > N₂O₄ > IRFNA > EDA > UDMH > N₂H₄ >
50-50 N₂H₄-UDMH**. For high-speed turbopumps, angular-contact ball bearings with one-piece,
outer-land-riding cages of self-lubricating PTFE-containing materials are preferred, and
have been **tested successfully to 3.0×10⁶ DN**. Typical coolant flow: 0.1 gpm RP-1 for
low-load/low-speed bearings up to 150 gpm liquid hydrogen for large high-speed bearings.

**Bearing materials** `[SP-8048 §2.1.9 p.19-20, §3.1.9.1 p.46]`: **AISI 440-C steel is the
real baseline** for races and rolling elements in propellant-cooled turbopump bearings
(cages are plastics, sometimes CRES- or aluminum-reinforced) — this directly corroborates
`turbopump_materials.py`'s existing `440c_steel` entry as period-correct and still the
default recommendation as of this monograph ("the most commonly used race material...none
has been found with the combination of hardness, corrosion resistance, fatigue life, and
availability displayed by 440-C"). Design-criteria text (§3.1.9.1) makes this an imperative:
"the rolling element, race, and cage materials **shall** be resistant to or protected from
corrosion under all operating conditions," with 440-C named as the default answer. Other
materials surveyed but not yet design-recommended in 1971: nickel-based alloys (corrosion
resistant, but soft), sintered carbides (corrosion resistant and hard, but brittle), and
Stellite Star-J (investigated for cryogenic service, "testing has not produced design
recommendations" — i.e. inconclusive, not adopted). **No ceramic (Si3N4-class) bearing
material appears anywhere in this monograph** — consistent with the real history that
ceramic turbopump bearings are a later (SSME-era-and-after) development; `[Ch12-Materials]`
remains the correct source for that later material.

**Clamping-load real numbers** `[SP-8048 §2.1.8 p.24, §3.1.8.7.1 p.46]`: real bearing-race
retaining-nut/bolt clamping loads — **50,000 lbf** tension-bolt clamping load used in the
**J-2S** engine; **800 ft-lb** clamping-nut torque used in the **F-1** engine turbopump; a
real Atlas-sustainer-turbopump gear/race fretting failure was eliminated by increasing
clamping-nut torque to 200 ft-lb. Not directly a shaft/DN quantity, but a real precedent for
the general principle (also in `[SP-8120]`'s retaining-band content) that under-clamped
rotating hardware in a turbopump is a recurring real failure mode, fixed by adequate
preload/torque rather than by a geometry change.

## Design method

Like `[SP-8120]`, this is a **criteria/practices monograph, not a closed-form sizing
source** — the one quantitative design rule extracted (the 1.0×10⁶/3.0×10⁶ DN bands) is a
recommended operating envelope, not a formula. No bearing bore/shaft-diameter sizing
equation was found in the sections read; `engine_designer/physics/turbopump_sizing.py`'s own
`shaft_diameter_m()` (torsion-based, `SHAFT_ALLOWABLE_SHEAR_PA = 200e6`) and
`BEARING_BORE_OVER_SHAFT_FACTOR = 1.15` remain unconfirmed by this source — not found in the
~15 pages read, and may or may not appear in the unread §2.1.1/§2.1.3-2.1.6/§3.2 sections.

## Section map

- Title page, Contents (p.v): rendered/read.
- §1 Introduction (p.1-3): p.3 rendered/read (partial); p.1-2 not read.
- §2.1 Bearing Assembly Design, State of the Art (p.4-23): **§2.1.2 Speed Capability (p.12-13)
  and §2.1.7 Cooling (p.16) and §2.1.9 Bearing Materials (p.19-20, partial) rendered/read.**
  §2.1.1 Load Capability, §2.1.3 Stiffness (p.13, partial only), §2.1.4 Misalignment
  Tolerance, §2.1.5 Bore, §2.1.6 Internal Clearance, §2.1.8 Bearing Mounting (p.24 partial —
  race retention/clamping only), §2.1.10 Testing — not rendered.
- §2.2 Bearing Component Design (p.23-30): not rendered at all.
- §3.1 Bearing Assembly Design, Design Criteria (p.31-52): **§3.1.1 Load Capability + §3.1.2
  Speed Capability (p.31) and §3.1.8.7.1 Clamping Loads + §3.1.9/§3.1.9.1 Bearing Materials
  (p.46) rendered/read.** Remaining subsections (§3.1.3-3.1.7, most of §3.1.8, §3.1.10) not
  rendered.
- §3.2 Bearing Component Design, Design Criteria (p.52-68): not rendered.
- References (p.69-72), Glossary (p.73-76), Monograph list (p.77+): not rendered.

## Caveats

- **No text layer**: every quotation above was transcribed by eye from a rendered page
  image, not OCR or copy-paste — technical content and numbers were read carefully, but this
  note cannot be grepped/cross-checked against the source PDF's own text the way other
  `claude_lit` sources can.
- **~85% of the monograph is unread** (only ~15 of 84 pages were rendered, targeted
  specifically at speed/DN, cooling, and materials content per this task's priority) — the
  rolling-element/race/cage detail-design sections (§2.2/§3.2) and the bore/misalignment/
  stiffness sections are completely unexplored and may contain additional relevant criteria
  (e.g. a shaft-sizing method, if one exists in this monograph, is most likely in an unread
  section).
- **1971 vintage**: no ceramic bearing materials (Si3N4-class) appear — this monograph
  predates that technology; `[Ch12-Materials]` (c.2016) remains the source for
  ceramic-bearing real-engine precedent (SSME HPOTP/Block II HPFTP).
- **The 3.0×10⁶ DN ceiling is a blanket rolling-element limit**, not broken out by bearing
  material the way `turbopump_materials.py`'s `BEARING_MATERIALS` dict is — this document
  doesn't give per-material DN numbers, so it can validate the tool's overall ceiling
  order-of-magnitude but not its material-by-material gradation.
