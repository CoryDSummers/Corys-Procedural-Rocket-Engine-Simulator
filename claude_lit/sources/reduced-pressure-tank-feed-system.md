# Feed System Design for a Reduced Pressure Tank (Vanderbilt USRA-ADP)

## Identity

"7 — Feed System Design for a Reduced Pressure Tank," a chapter/section (numbered §7.x
throughout, own page footer "Vanderbilt University / USRA-ADP") from what is clearly a
multi-team NASA University Space Research Association Advanced Design Program (USRA-ADP)
compilation report — this PDF contains only the one student team's chapter, not the full
compilation. `literature/USRA-ADP N95-26310 - Feed System Design for a Reduced Pressure Tank.pdf` (NTRS 19950019890; 19 PDF leaves, no offset — printed page numbers
match PDF leaf index exactly, e.g. printed 7.1 = leaf 0). NASA accession N95-26310.
Tag: `[ReducedPressTank]`.

## Character

A **student capstone-design report**, not a peer-reviewed engineering source — this needs
to be stated plainly. It's a Vanderbilt University undergraduate/USRA Advanced Design
Program team's conceptual study of a **fictional tri-propellant (LOX/LH2/RP-1) single-stage-
to-orbit (SSTO) shuttle's fuel feed system**, explicitly built by adapting piping
configurations, diameters, and flow coefficients wholesale from a **National Launch System
(NLS) presentation** (ref. 1, "USAF/NASA, National Launch System, presented at NASA
Marshall 2/12/92" — an unpublished/internal presentation, not independently available to
cross-check) rather than deriving them from first principles. The design objective was
narrow: evaluate three concepts (as-is pressurized tank feed system / a fluid-recirculation
system / an external ground-based pressurized fuel supply, "LBPFS") for **reducing LOX tank
wall thickness by reducing required tank pressure**, and recommend one (LBPFS won). A small
1-D transient-flow computer model (Turbo Pascal, momentum-conservation ODE) was built to
simulate fill/startup velocity transients in the internal feed lines.

**Scope note relevant to `engine_designer`**: everything here is **vehicle-level plumbing**
— tank outlet through ~1000+ inch runs of 12"–20" trunk line, around cargo bays and other
tanks, to 5 engines — not engine-internal injector-feed manifold design (the domain of
`manifold.py`/`topics/12b-structures-manifolds-and-hardware.md`'s manifold section). The scale
mismatch (feet of 12-20" pipe vs. inches of injector-face manifold) means most of this
report's numbers are not directly reusable in `engine_designer`, which stops at the engine
inlet flange. Flag this loudly before citing anything from here for engine-internal
plumbing.

## Key results

**Tri-propellant SSTO concept and rationale** `[ReducedPressTank §7.3 p.7.1]`: motivated by
NASA's then-current interest (1994-95) in adapting a Russian-heritage tri-propellant
architecture (both LH2 and RP-1 burned with LOX, i.e. an RD-701-style engine/vehicle
concept) for a five-engine SSTO. Not itself a source of engine-cycle numbers — no engine
Isp/Pc/thrust data anywhere in this chapter.

**Real(ish) piping flow-coefficient (K-factor) table, from NLS data** `[ReducedPressTank
§7.4.1.1.3-7 p.7.3-7.9]` — the LOX/RP-1/LH2 feed systems are itemized component-by-component
(tank outlet, forward trunk, main trunk, POGO suppression baffle section, trunk manifold,
crossover assembly, center-engine manifold, prevalve, center-engine feedline, outer-engine
manifold, outer-engine prevalve, outer-engine feedline), each with a quantity, a **flow
coefficient** and a diameter. Representative values (all stainless steel, mostly insulated,
LOX system shown — RP-1 and LH2 systems use near-identical topology/values):
- Tank outlet assembly: K=1.08 (no diameter given — merges into trunk line)
- Forward trunk assembly (2 elbows + straight + 3 gimbals): K=0.886, 20" dia
- Main trunk line (4 flanged sections, ~900 in long for LOX): K=0.68 (LOX) / 0.68 (RP-1),
  20" dia
- POGO suppression baffle section: K≈0.0, 20" dia
- Trunk manifold (splits to center + outer engines): K=0.27 through-path / 0.77 branch,
  17" through / 8.5" branch
- Crossover assembly (3 gimbals): K=0.42, 8.5" dia
- Center-engine manifold (joins two crossover lines): K=0.56, 8.5" in / 12" out
- Center/outer-engine prevalve: K=0.1-0.17, 12" dia
- Center-engine feedline (3 gimbals + screen): K=1.08-1.26, 12" dia
- Outer-engine manifold: K=0.56, 17" in / 12" out
- Outer-engine feedline (3 gimbals + screen, x4): K=1.08-1.53, 12" dia

These are stated as adapted directly from NLS data (a six-engine booster-disconnect design)
with only the center-engine plumbing re-sized for the SSTO's single center engine — i.e.
**this is secondhand NLS data, not independently derived or verified**, and the report's
own error-analysis section admits "the largest error will probably be seen in the flow
coefficients" `[ReducedPressTank §7.4.1.1.9 p.7.10]`. Treat as a rough real-hardware-
derived order-of-magnitude reference for large feed-line K-factors (elbow/gimbal/manifold/
valve ~0.1-1.5 range), not a validated design table.

**Feedline design velocity and startup transient** `[ReducedPressTank §7.4.2.3-2.4
p.7.13-7.14]`: NASA-supplied design parameters for the (separate, recirculation-concept)
LOX feedline were **velocity ≈ 20 ft/s, diameter 26 in** — inconsistent with the 20 in
trunk-line diameter used in the main feed-system description above, an internal
inconsistency the report doesn't reconcile. Mass flow computed from this: 162.8 slug/s LOX
(density 2.208 slug/ft³ at -297°F ≈ liquid boiling point).

**Transient fill/startup time to 99% steady-state velocity** `[ReducedPressTank §7.4.1.2.3
p.7.12]` (from the team's own 1-D momentum-conservation transient model, Table 7.1's
pressure/length/K inputs): **LH2 0.51 s, LOX 2.73 s, RP-1 2.26 s**. Order-of-magnitude
plausible for line-fill transients of this length (LOX/RP-1 lines ~850-1100 in; LH2 line
only ~100 in, hence much faster) but this is the report's own simplified 1-D incompressible
single-diameter-pipe model, explicitly caveated by the authors as neglecting multi-branch
splitting and diameter changes — not independently validated.

**LOX tank wall-thickness vs. pressure (pressure-vessel design)** `[ReducedPressTank
§7.4.3.5 p.7.17]`: standard thin-wall pressure vessel formulas applied to the LOX tank's
cylindrical shell / ellipsoid cap / conical section, with assumed **allowable stress
S=50 ksi, joint efficiency E=1**, tank outer radius 201 in, outer diameter 402 in (bottom)
/ 219 in (top), cone half-angle 23°. States the conical section governs (highest stress),
and reduces to a simple linear relation for their specific geometry: **P [psi] =
0.0063 × t [in]** (i.e. every 1 psi of tank pressure needs ~0.0063 in of wall thickness in
this specific cone geometry at S=50 ksi) `[ReducedPressTank Eq.7.12 p.7.17]`. This is a
generic pressure-vessel-design method (nothing novel), but the concrete S=50 ksi allowable
and the worked P-vs-t constant are a real, if secondhand-plausible, numeric anchor for
"how much does 1 psi of ullage pressure cost in tank wall mass" reasoning — directly on-
topic for `topics/13-mass-and-budget.md`'s propellant/tank-mass-budget scope, **if** a tank-
mass model is ever added there (none currently exists per that file's current scope, which
is engine-side mass/cost only).

**Design concept: external ground-based pressurized supply to eliminate onboard tank
pressurization during startup** `[ReducedPressTank §7.4.3 p.7.15-7.16]` (LBPFS) — the
report's own recommended solution: supply LOX/LH2/RP-1 from ground-side pressurized
containers + turbopumps through the startup transient, then hand off to the vehicle's own
(now lower-pressure) tanks once steady state is reached, with a ground-umbilical disconnect
at handoff. This is a **conceptual vehicle-ops idea, not a quantified design** — the report
explicitly states "the actual LBPFS has not been designed" and gives no sizing, mass, or
pressure numbers for it. Not citable as a design method, only as a named architectural
pattern (ground-assisted startup to relax onboard tank pressure requirements).

## Design method

None directly portable to `engine_designer`. The tank-wall pressure-vessel formulas
(§7.4.3.5) are standard textbook thin-wall-vessel equations, not a new method; the flow-
coefficient table is scraped from an unpublished NLS source, not derived; the transient-fill
model is a toy 1-D momentum ODE the authors themselves flag as oversimplified. Nothing here
rises to the level of a spot-checkable closed-form constant for `physics/manifold.py` or
`physics/mass_model.py`.

## Section map

- §7.1 Summary/Abstract: leaf 0.
- §7.2 Glossary: leaf 0.
- §7.3 Background for SSTO Feed System: leaf 0.
- §7.4.1.1 Feed System Design (LOX/RP-1/LH2 piping-by-piping-section descriptions, flow
  coefficients, diameters): leaf 1-9 — read in full, source of the K-factor table above.
- §7.4.1.1.8 Feed System Assumptions / §7.4.1.1.9 Error Analysis: leaf 9 — read (admits NLS-
  sourced data, six-to-five-engine adaptation, largest error in flow coefficients).
- §7.4.1.2 Computer Feed System Model (momentum-conservation ODE, Turbo Pascal): leaf 9-12 —
  read; source of the 99%-steady-state transient times.
- §7.4.2 Fluid Recirculation Feed System (alternative concept, not recommended): leaf 12-15
  — read; source of the 20 ft/s, 26" feedline design parameters and the ~48 psi pump ΔP
  estimate for that concept (not reused in the recommended design).
- §7.4.3 Land Based Pressurized Fuel System (LBPFS, recommended concept) + §7.4.3.5 Weight
  Reduction (tank wall-thickness formulas): leaf 15-17 — read in full, source of the tank
  pressure-vessel numbers.
- §7.5 Recommendations, §7.6 References: leaf 17-18 — read.
- No figures were legible as separate images beyond captions (Figures 7.1-7.6 are schematics
  and a P-vs-t graph, all text-extractable captions only; the graphs' plotted curves were
  not re-extracted, but Eq. 7.12 in the body text gives the P-vs-t relation directly so
  nothing was lost by not re-digitizing Figure 7.6).

## Caveats

- **Coursework-grade source, not a rigorous engineering reference.** This is a NASA
  USRA-ADP undergraduate team's conceptual design chapter, explicitly built by adapting
  another (inaccessible, unpublished) NLS presentation's numbers rather than deriving its
  own. Every "real" number here (flow coefficients, pipe diameters, feedline velocity) is
  **secondhand from a source this note's author cannot independently verify.**
- **Internal inconsistency**: the main feed-system section (§7.4.1.1) uses 20 in trunk-line
  diameter; the separate recirculation-system section (§7.4.2.3) uses a NASA-supplied 26 in
  feedline diameter at 20 ft/s design velocity for what should be the same LOX feed line —
  the two sections were evidently written from different source data and never reconciled.
- **Wrong scale for `engine_designer`'s manifold.py.** This report's "feed system" is
  vehicle tank-to-engine plumbing (12-1100 in runs, 5-engine branching, POGO suppression,
  gimbaled sections for thermal/misalignment) — a completely different design object from
  `manifold.py`'s injector-face propellant intake manifold (inches, single engine). Any use
  of the K-factor table here for `engine_designer` would need to be clearly scoped as
  "order-of-magnitude large-feed-line K-factor precedent," not applied to injector-adjacent
  manifold sizing.
- **No engine-cycle, injector, combustion, or turbopump numbers anywhere** in this chapter —
  it is entirely a tank/plumbing/pressurization document. Low relevance to most of
  `claude_lit/topics/*.md` outside the tank-mass-budget angle.
- **Overall verdict**: low-to-marginal citable value. The one genuinely reusable number is
  the tank pressure-vs-wall-thickness relation (§7.4.3.5, S=50 ksi allowable, P=0.0063t for
  their specific cone geometry) as a concrete real-vessel-design anchor if a propellant-tank
  mass model is ever added to `engine_designer`'s scope (currently out of scope — that tool
  stops at the engine inlet flange). The flow-coefficient table is a weak secondary
  reference for feed-line K-factor magnitudes only. Do not treat anything here as validated
  or as superseding any existing `claude_lit` source.
