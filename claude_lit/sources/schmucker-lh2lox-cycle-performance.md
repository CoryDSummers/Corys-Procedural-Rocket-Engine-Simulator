# NASA TM X-64749 — A Simple Performance Calculation Method for LH2/LOX Engines with Different Power Cycles

## Identity

Robert H. Schmucker (National Research Council associate, Astronautics Laboratory, Science
and Engineering), *A Simple Performance Calculation Method for LH2/LOX Engines with
Different Power Cycles*, NASA Technical Memorandum TM X-64749, George C. Marshall Space
Flight Center, February 16, 1973. NTRS accession 19730016059. File:
`literature/NASA TM X-64749 - A Simple Performance Calculation Method for LH2-LOX Engines
with Different Power Cycles.pdf` (renamed from the raw NTRS accession number per project
convention). Tag: `[Schmucker-CycleCalc]`.

**IMPORTANT — this PDF is truncated.** The title page's own "NO. OF PAGES" field states
**42**, and the report's own Table of Contents lists content running to printed page 34
(CONCLUSION p.33, REFERENCES p.34) plus Figures 7–17 (pp.17–32) covering the
"APPLICATION OF THIS CONCEPT FOR PERFORMANCE COMPARISON OF DIFFERENT TYPES OF ENGINES"
section — but the PDF actually on disk has only **23 pages** (`fitz` `page_count`
confirmed), and its content stops mid-derivation at printed page 16 (Figure 6 / equation
34, the last of the thermodynamic-property curve fits). **Everything from printed page 17
onward — the entire numeric cycle-comparison section, all worked "five different engine
types" (A, B, C, D1, D2 per the List of Illustrations captions), the actual Isp/pump-head/
turbine-efficiency/GG-temperature trade figures (Figs 10–17), and the CONCLUSION and
REFERENCES — is simply absent from this file.** No duplicate or fuller copy exists
elsewhere in `literature/` (checked). This note only covers what pages 1–16 contain: the
derivation of the calculation *method* itself (the power-balance equations and the LOX/LH2
thermodynamic-property curve fits), not the numeric cycle-vs-cycle comparison results the
paper's title and Summary promise. This gap should be flagged to Cory — reacquiring a
complete copy from NTRS would be needed to get the actual comparison numbers.

## Character

A short (42-page, of which 23 present) 1973 MSFC technical memo presenting a **closed-form,
hand-calculable power-balance method** (not a CEA-style full simulation) for estimating the
specific impulse of a LOX/LH2 rocket engine under two power-cycle architectures — gas
generator and staged combustion (called "preburner" in this report's own terminology, but
functionally a fuel-rich topping/staged-combustion turbine drive) — plus a self-contained
set of curve-fit thermodynamic-property approximations (c*, thrust coefficient C_F, exit
pressure ratio) specific to LOX/LH2, fit against exact one-dimensional equilibrium
solutions (attributed to the author's own Reference 1) rather than derived from a cruder
closed-form gasdynamic approximation. This is exactly the "trade rigor for
hand-calculability" character the task brief anticipated: no chemistry/equilibrium solver
is used at run time — the equilibrium chemistry is baked into three curve fits (eqs.
31/33/34 below), and everything else is an algebraic power/mass balance.

Companion in spirit to `[SP-8107]` (already the backbone of `claude_lit/topics/
08-engine-cycles.md`): SP-8107 states cycle comparisons and multiplier tables as
design-guide conclusions; this MSFC memo is the actual first-principles derivation of *why*
a staged-combustion cycle's pump discharge pressure must build up from Pc plus the turbine
pressure drop (SP-8107's "series turbine ΔP adds to pump discharge" rule), and *why* a gas
generator cycle's engine Isp is a bleed-fraction-weighted average of two different Isp
values (SP-8107's "Isp penalty from bled flow" rule) — SP-8107 states these as facts;
Schmucker gives the equation.

## Key results — the calculation method (pp.1–16, all that survives)

**Summary/Introduction** `[Schmucker-CycleCalc p.1]`: "A simple method for the calculation
of the specific impulse of an engine with a gas generator cycle is presented. The solution
is obtained by a power balance between turbine and pump... The solution method has been
applied to **five different engine types** leading to an optimization of the chamber
pressure and turbine pressure ratio associated with maximum performance." (The five-type
numeric comparison itself is in the missing pages 17+; only this one-sentence pointer to it
survives, plus the List-of-Illustrations captions naming engine types "A" and "D1" for
Figures 10, 12, 13, 16 — no comparison data.)

**Central simplifying assumption, stated explicitly** `[p.2]`: "To simplify the
calculations, no mixing and secondary chemical reaction of the turbine exhaust gases with
the combustion chamber gases are assumed. The expansion of both mass flows is calculated
independently." I.e. the GG/preburner exhaust stream and the main-chamber stream are two
separate, independently-expanded nozzle flows whose thrusts (and specific impulses) are
combined afterward — a genuine "simple method" simplification, not a mixed-gas equilibrium
solve. The injection point is chosen "where the main chamber nozzle's static wall pressure
and the turbine exit pressure are almost the same" (a matched-pressure injection
assumption).

**Gas-generator cycle power balance — the pump-side energy demand** `[pp.2–3, eqs.1–4]`:
pump shaft energy is built from oxidizer and fuel pump work,

    E_p = (1/η_p) [ ṁ_ox (p_p − p_i)/ρ_ox + ṁ_fu (p_p − p_i)/ρ_fu ]         (eq.1)

with the simplifying assumption **"both pump efficiencies are equal and pump inlet
pressures are small compared with the discharge pressure"** `[p.3]`, collapsing to a
function of the overall mixture ratio r = ṁ_ox/ṁ_fu (eq.3) and the two pump discharge
pressures/densities alone (eqs.2, 4).

**Turbine-side energy supply — the isentropic (de Saint-Venant–Wantzel) shortcut**
`[pp.4–5, eqs.5–6]`: turbine shaft energy from GG-gas enthalpy drop,

    E_t = ṁ_g η_t (c_p T)_g [ 1 − (p_te/p_g)^((γ_g−1)/γ_g) ]                (eq.6)

used **instead of a real enthalpy-drop/equilibrium lookup**, justified by an explicit
footnote: "Since the gas generator mixture ratio is normally very low, dissociation effects
can be neglected and therefore equation (6) is a reasonable equation with constant γ_g"
`[p.4 footnote]` — i.e. the simple isentropic-expansion formula is only valid *because* the
fuel-rich GG mixture ratio keeps the gas chemically simple (no dissociation to model).

**Setting E_p = E_t (steady state) yields the required GG mass flow** `[pp.5–6, eqs.7–10]`,
expressed as a **relative GG mass-flow fraction** k_m = ṁ_g/ṁ_total (eq.9) in terms of the
overall mixture ratio, pump discharge pressures/densities, and the GG total-enthalpy term
(c_p T)_g — this k_m is the cycle's core bleed-fraction output, playing the same role as
this project's own `GG_FLOW_FRACTION` check (`topics/08` "Isp penalty from bled flow").

**Relating GG mixture ratio, chamber mixture ratio, and overall mixture ratio** `[p.6,
eqs.11–12]`: given the GG mixture ratio r_g and the desired chamber mixture ratio r_c as
independent inputs, the overall (total-propellant) mixture ratio r is derived algebraically
from r_c, r_g, and k_m — i.e. k_m and r are found by solving a small closed system, not
picked independently.

**Linear pressure-drop-factor model for pump discharge pressure** `[p.6, eqs.13–14]`:

    p_p,ox = p_c (1 + k_ox)          p_p,fu = p_c (1 + k_fu)

with k_ox, k_fu **assumed constant within a given pressure range** — an explicit,
acknowledged simplification: "the results are not very sensitive to the pressure factors,
this statement contains little error" `[p.6]`. This is structurally identical to
`[SP-8107]`'s "P_discharge = Pc + Σ downstream pressure drops" relation already anchoring
`topics/08-engine-cycles.md`'s Key Relations section — Schmucker's k-factor form is the
same relation written as a multiplicative margin rather than an additive ΔP sum.

**Gas generator pressure and the minimum GG flow rate** `[pp.7–8, eqs.15–17]`: the GG
(turbine inlet) pressure is derived from the oxidizer pump discharge pressure (since the
oxidizer pump — "commonly lower than the fuel pressure" — sets the ceiling); a **minimum
GG mass flow** is derived from the constraint that the turbine's exit pressure cannot be
lower than the main-nozzle's local static pressure at the injection point (bounded below by
nozzle exit pressure p_e) — i.e. there's a floor on how little gas the turbine can be fed
before the exhaust can no longer be usefully injected into the expanding main-chamber flow.
Increasing GG flow above this minimum **lets the turbine pressure ratio decrease** for the
same required turbine power — a real, quantified trade between bleed-fraction and turbine
pressure ratio (more bleed flow → gentler turbine PR needed) that a hand-sizing exercise
could exploit.

**The engine-level Isp formula for the gas-generator cycle — the "Isp penalty" made
explicit** `[p.8, eq.18]`:

    I_sp,ggc = η_sp [ (1 − k_m) I_sp,c + k_m I_sp,g ]

a **mass-flow-weighted average of the main-chamber Isp and the (lower) GG-exhaust-stream
Isp**, scaled by an overall efficiency η_sp folding in "divergence, friction, etc." This is
the exact closed-form realization of `topics/08`'s existing qualitative "Isp penalty from
the bled flow" statement (currently modeled in `engine_designer` as
`engine_isp_with_gg_dump`, a mass-averaged blend per that topic file's own note) — a
genuinely portable, citable equation for that blend, from an independent 1973 source rather
than only SP-8107's tabulated ⅓–1%-at-1000-psia figure.

**Turbine pressure ratio solved from the power balance, then propagated to the main
nozzle** `[pp.8–9, eqs.19–21]`: eq.19 solves the turbine exit/GG pressure ratio p_te/p_g
directly from the power-balance requirement (a rearrangement of eqs.6–10 back into a
pressure ratio, given a chosen k_m); eqs.20–21 then chain this to the *main nozzle's*
pressure ratio, since the turbine-exhaust gas is expanded through the same main nozzle as
the primary chamber flow (per the earlier injection-point assumption).

**Staged combustion ("preburner") cycle — the key structural difference from GG** `[pp.9–11,
eqs.22–29]`: "For a low pressure drop in the turbine, according to equation (19), the
maximum possible flow rate in the preburner has to be used. This means that **the whole
fuel mass flow is injected into the preburner**" `[p.9]` — i.e. Schmucker's staged-
combustion model is the k_m→1 (all propellant through the turbine) limit of the same GG
framework, not a separate derivation; the preburner mixture ratio r_pb = ṁ_ox,pb/ṁ_fu,pb
(eq.23) plays the same role as r_g did for GG. Because the staged-combustion turbine
pressure drop is small (a low-PR "topping" turbine, per this project's own `[SP-8107]`
"< 1.5" figure already in `topics/08`), Schmucker **linearizes eq.19 by a power-series
expansion, keeping only the first-order term** `[p.10, eqs.25–26]` — an explicit, stated
simplification specific to the low-turbine-ΔP staged-combustion regime (not valid for the
GG cycle's larger pressure drop, which keeps the full exponential form).

**Staged-combustion pump discharge pressure — the "turbine ΔP adds to pump head" relation,
in closed form** `[p.11, eqs.27–28]`:

    p_p,pb ∝ p_c (1 + k_pb) × (p_te/p_c)^(...)          p_p,ox correspondingly

i.e. pump discharge pressure must supply **both** the chamber-pressure-plus-line-loss
margin **and** recover the turbine's own pressure drop, since in a closed (staged-
combustion) cycle the turbine exhaust re-enters the main chamber at a pressure close to Pc
rather than dumping overboard at low pressure. This is the exact mechanism behind
`[SP-8107]`'s already-cited "series turbine ΔP adds to the pump discharge pressure → high
head and power" rule in `topics/08` — again, the derivation SP-8107's design-guide table
states as a fact.

**Staged-combustion engine Isp — no bleed penalty, in closed form** `[p.11, eq.29]`:

    I_sp,sec = I_sp,c × η_sp

i.e. because *all* propellant passes through the main chamber at full tank-enthalpy
conditions (no separate lower-performance GG-exhaust stream), the staged-combustion engine
Isp is simply the main-chamber Isp times the same loss efficiency η_sp used for the GG
cycle's main-chamber term — the literal zero-Isp-penalty counterpart to `topics/08`'s
GG-cycle eq.18. This closed-form pairing (eq.18 vs eq.29) is the single most useful,
portable result recovered from this truncated copy: a matched, hand-calculable pair of Isp
formulas for the two cycles under the same overall framework, ready to be spot-checked
against a real engine pair (e.g. J-2 GG vs an SSME-class staged-combustion engine) if
`engine_designer`'s `cycles.py`/`staged_combustion.py` ever wants an independent
closed-form cross-check of its own `engine_isp_with_gg_dump` blend.

## Key results — LOX/LH2 thermodynamic-property curve fits (pp.12–16)

Rationale stated explicitly `[p.12]`: "it is practical to use 'approximations to
solutions' instead of 'solutions of approximate equations'" — i.e. Schmucker deliberately
avoids the de Saint-Venant-Wantzel closed-form gasdynamic relation for the *main-chamber*
performance number (unlike the GG-turbine calculation above, which does use it), because
that approximation "has the disadvantage that mixture ratio effects, etc., are omitted
almost completely... especially in the near of the impulse optimum" `[p.12]`. Instead, three
independent curve fits are given, each fit against exact 1-D equilibrium solutions
(reference not preserved in the extracted pages) over stated validity ranges:

**Characteristic velocity** `[p.13, eq.31]` — the cleanest-transcribed equation in this
source (digits legible, cross-checked against the stated validity text):

    c* = [3660 − 160·r] · (p_c / 700)^(−0.022)      [m/s]

valid **4 ≤ r ≤ 7** and, per the text immediately following, "chamber pressures between 500
N/cm² and 3000 N/cm²" (≈ 725–4350 psia) — "however, both limits may be extended without
decreasing the accuracy significantly" `[p.14]`. p_c in N/cm² (700 N/cm² ≈ 1000 psia is the
reference point used in Figure 4's own labeling). This is a real, portable, hand-calculable
LOX/LH2 c* correlation independent of any equilibrium-chemistry solver — a candidate
cross-check for `engine_designer/physics/combustion.py`'s baked equilibrium-table c* values
at LOX/LH2 conditions, though not yet checked against them in this pass.

**Effective thrust-coefficient exponent γ_F** `[pp.14–15, eqs.32–33]`: a defined parameter
γ_F, chosen to make the conventional C_F formula easier to evaluate by hand (eq.32
substitutes it into the standard thrust-coefficient equation in place of the true
isentropic exponent), curve-fit as a function of area ratio, chamber pressure and mixture
ratio:

    γ_F ≈ exp[ 0.00534·ln(A_e/A_t) + 0.234·(p_c/p_ref)^(−0.0555) − 0.0311·(r−3) ]

valid over the same 4≤r≤7 / 500–3000 N/cm² range plus **area ratio A_e/A_t from 50 to 500**
("again the limits may be extended") `[p.16]`. **Transcription caveat**: this equation's
exact coefficients are reconstructed from moderately garbled OCR (the source text shows
fragments like "fn - exp /A 0.00534 in ... + 0.234 /p \ -0.0555 - 0.0311(r-3)"); the
functional *form* (log-linear in ln(ε), power-law in Pc, linear in r) is clear and
consistent with eq.31's style, but individual digits (particularly the 0.234 coefficient
and whether p_c is normalized by 700 N/cm² as in eq.31) should be treated as
lower-confidence than eq.31's — do not hand this coefficient set to code without
re-verifying against a clean copy of the source.

**Exit/chamber pressure ratio vs. area ratio** `[p.16, eq.34]`, same reconstruction caveat
as eq.33:

    (p_e/p_c or p_c/p_e) ≈ exp[ (1.38 − 5.68×10⁻⁴·r)·ln(A_e/A_t) + 1.58·(p_c/p_ref)^(−0.125) − 0.1·(r−3) ]

(the OCR does not unambiguously resolve which pressure ratio, p_e/p_c or its reciprocal, is
on the left-hand side — the surrounding text calls it simply "the pressure ratio as a
function of the area ratio," consistent with either convention depending on sign). Same
validity ranges as eq.33 (r 4–7, Pc 500–3000 N/cm², ε 50–500).

**What these three curve fits collectively give**: a self-contained, hand-calculable
LOX/LH2 vacuum-Isp estimate (I_sp0 = c*·C_F/g, eq.30 — the ordinary relation, not novel)
across mixture ratio, chamber pressure and area ratio, without needing an equilibrium
solver — Figures 3–6 (pp.13–16, present in this copy but not independently re-read as
images; see Section map) plot the resulting Isp/c*/C_F/γ_F surfaces this feeds.

## Design method

This *is* a design method in the sense the project's template category means: a documented,
reproducible, hand-calculable procedure (power-balance algebra + three curve fits) for
estimating GG-cycle and staged-combustion-cycle engine Isp and pump/turbine pressures for a
LOX/LH2 engine, explicitly positioned by its own author as a fast preliminary-design tool
("permits an optimization of the principal design and a quick estimation of the effects of
the various parameters on engine performance" `[p.2]`) rather than a final-design or
CEA-replacement tool. The actual worked application of this method (the five engine types,
Figs 10–17) — which would have been the strongest evidence of the method's practical
output — is in the missing pages and not available here.

## Section map

- Cover/title page: leaf 0 — read.
- Technical Report Standard Title Page (abstract, "NO. OF PAGES 42"): leaf 1 — read; this is
  where the truncation was first suspected and then confirmed.
- Table of Contents (pp. i–iii, shows content to p.34): leaf 2 — read; used to establish the
  full document's real extent vs. what's present.
- List of Illustrations (Figs 1–9, pp.iv–v) and List of Illustrations Concluded (Figs 10–17,
  p.vi, captions only for Figs 10–17 since their pages are missing): leaves 3–4 — read;
  captions for the missing-page figures (naming engine types A, B?, C?, D1, D2? and giving
  their fixed parameters ε=500, r_c=6, η_sp=0.96, r_g=1, p_c≈1350 N/cm²≈2000 psia) are the
  only surviving trace of the numeric comparison section.
- Definition of Symbols (2 pages): leaves 5–6 — read; partially garbled subscript table, not
  fully reconstructed (see Caveats).
- SUMMARY / INTRODUCTION (p.1): leaf 7 — read.
- BASIC EQUATIONS FOR PERFORMANCE CALCULATION → Gas Generator Engine (pp.2–8, eqs.1–21,
  Fig.1 p.3): leaves 8–14 — read in full, the bulk of the citable content above.
- Staged Combustion Cycle Engine (pp.9–11, eqs.22–29, Fig.2 p.9): leaves 15–18 — read in
  full.
- Approximate Equations for the Thermodynamic Properties of O2/H2 (pp.12–16, eqs.30–34,
  Figs.3–6 pp.13–16): leaves 18–22 — read in full; this is the last content in the file.
- **MISSING: pp.17–34** — Figure 7 (pressure-ratio plot, captioned p.17 but not present),
  Figs.8–9 (GG enthalpy/temperature and isentropic exponent vs. mixture ratio, p.20),
  "APPLICATION OF THIS CONCEPT FOR PERFORMANCE COMPARISON OF DIFFERENT TYPES OF ENGINES"
  (pp.22–31, Figs.10–17 — the actual GG-vs-staged-combustion Isp comparisons, pump-head/
  turbine-efficiency sensitivity, GG-temperature effects, mixture-ratio and area-ratio
  sweeps, and a constant-thrust/exit-area comparison), "Improvement by More Precise
  Efficiency and Pressure Drop Equations" (pp.31–33), CONCLUSION (p.33), REFERENCES (p.34,
  5 numbered references per in-text citations "[1]"–"[5]", none of which could be read since
  the references page itself is absent).

## Caveats

- **This PDF is missing roughly half its content (pp.17–42 of a stated 42 pages) — see
  Identity above.** This is the single most important caveat: the paper's own Summary
  promises numeric results from "five different engine types" with an "optimization of the
  chamber pressure and turbine pressure ratio associated with maximum performance," which is
  precisely the GG-vs-staged-combustion Isp/T-W/pressure numeric comparison the task brief
  was looking for — and none of it survives in this copy. Only the *method* (equations)
  and the *property correlations* survive.
- **Definition of Symbols table (pp.vi–vii) is partially garbled by OCR/layout extraction**
  — several single-letter subscript definitions (i, min, ox, p, pb, sec, t appearing twice
  for both "throat" and "turbine", te, u, o) came out as a bare list with ambiguous
  letter-to-definition pairing in a few spots (e.g. it's unclear from the raw extraction
  whether "t" for "throat" and "t" for "turbine" are genuinely two different symbols the
  original used a diacritic/case difference to distinguish, or an OCR duplication). Subscript
  usage in the equations above was resolved by cross-referencing the surrounding prose, not
  by trusting this table alone.
- **Equations 1–29 (the power-balance method) are reconstructed from moderately-to-heavily
  garbled OCR** (subscripts and superscripts frequently detached from their base symbols and
  scattered onto adjacent lines, e.g. "P p Pox Pfu" for what is almost certainly
  p_p,ox/ρ_ox and p_p,fu/ρ_fu). The reconstructions above were built by combining the
  garbled fragments with standard rocket-engine power-balance conventions (matching e.g.
  `[SP-8107]`'s already-cited pump-discharge and turbine-PR relations) and the surrounding
  narrative prose, which in every case is much more legible than the equations themselves and
  was the primary source for the *qualitative* claims quoted above (e.g. the "whole fuel mass
  flow is injected into the preburner" and "results are not very sensitive to the pressure
  factors" statements are direct quotes, not reconstructions). Treat the **equation numbers,
  qualitative structure, and directly-quoted prose as reliable**; treat any **exact algebraic
  arrangement not shown as a direct quote** (e.g. the precise form of eqs.4, 8, 10, 12, 19,
  26–28 above) as a best-effort reconstruction consistent with the surviving fragments, not a
  verbatim transcription — do not treat this note as a substitute for re-deriving these from
  a clean copy if exact algebra is ever needed in code.
- **Equations 31/33/34 (the thermodynamic curve fits) are LOX/LH2-specific and only valid
  within stated ranges** (mixture ratio 4–7, chamber pressure 500–3000 N/cm² ≈ 725–4350
  psia, area ratio 50–500 for eqs.33–34) — not general-propellant correlations, and the
  paper itself notes these limits "may be extended without decreasing the accuracy
  significantly" but does not quantify how far.
- **Eq.31 (c*) is high-confidence (clean OCR, cross-checked against explicit validity-range
  prose); eqs.33–34 (γ_F, pressure ratio) are lower-confidence** — their coefficients came
  through OCR more garbled and are flagged individually above; do not use eqs.33/34's
  numeric coefficients in `engine_designer` code without independently re-verifying against
  a clean copy of the source.
- **No numeric cross-check against a real named 1973-era engine (J-2, RL10, etc.) survives
  in this copy** — the task brief's expectation of "real 1973-era LOX/LH2 engine data points
  used as worked examples" is not met by what's present; any such worked examples that may
  exist live in the missing Figures 10–17 / Application section.
- **Five references are cited in-text ([1]–[5], e.g. "Reference 1" for the exact
  one-dimensional equilibrium solutions eqs.31/33/34 were fit against, "Reference 5" for
  eq.34's power-relation form) but the References page (p.34) itself is missing**, so none of
  these upstream sources can be identified or chased from this copy.
- **The "preburner" terminology in this 1973 source predates and is functionally equivalent
  to what later literature (`[SP-8107]`, `[KBKhA]`, `[NK-33-Mod]`) calls "staged combustion"
  — this source does not distinguish fuel-rich (FRSC) from oxidizer-rich (ORSC) staged
  combustion** (the surviving pages describe only one flavor, structurally a fuel-rich
  topping cycle given the "whole fuel mass flow is injected into the preburner" framing);
  `engine_designer`'s FRSC/ORSC/FFSC distinction in `staged_combustion.py` is a later,
  finer-grained taxonomy than this 1973 memo uses.
