# EUCASS 2023-035 — Design of the Regenerative Cooling System for a 4kN LOX/Ethanol Engine

## Identity

Antoni Barredo Juan & Alberto López Platero (ISAE-SUPAERO, Université de Toulouse),
*Design of the regenerative cooling system for a 4kN LOX/Ethanol student-built liquid rocket
engine*, Aerospace Europe Conference 2023 – 10th EUCASS – 9th CEAS, DOI
10.13009/EUCASS2023-035. `literature/EUCASS2023-035.pdf` (15 PDF leaves, printed pages 1–15
match the PDF leaf+1 exactly, no offset). Tag: `[EUCASS-2023]`.

## Character

A short, modern (2023), fully-worked conference paper describing a **1D regenerative-cooling
channel design/optimization tool**, built in Python for the PERSEUS student project's
MINERVA LOX/Ethanol engine (ASTREOS 2 sounding rocket, CNES). Not a survey or design-criteria
monograph like `[SP-8120]`/`[Marquardt-5981]` — a single coherent design methodology paper
with real governing equations, a validation exercise against independent CFD, and one
worked-example channel-geometry optimization with numeric results. No section numbering
beyond `1. Introduction` / `2. Modelling approach` (2.1 Hot gas side, 2.2 Coolant flow, 2.3
Film cooling, 2.4 System) / `3. Validation` / `4. Results` (4.1 GA optimization, 4.2 Film
cooling) / `5. Conclusion`. No manifold-design content at all — the paper only models flow
*inside* the channels, not how coolant is distributed to/from them (see Caveats).

**Scale**: a **4 kN thrust, Pc = 20 bar, O/F = 1.4** student engine (MINERVA/ASTREOS 2) — this
is small-engine-scale like `[Marquardt-5981]`, not a large-booster source. The CFD validation
case is a different, larger LOX/Methane engine (Pc 56 bar) from CIRA, used only to check the
*shape* of the model's predictions, not to anchor MINERVA-specific numbers.

## Key results — Heat-transfer model (all equations as given, SI units unless noted)

**Governing balance** `[EUCASS-2023 Eq.1, p.2]`: the same three-resistance chain as
`[Huzel eq. 4-10]`/`cooling.py`, but with an explicit added radiation term:

    q = h_g(T_aw - T_w,g) + q_rad = (kappa_w/t_w)(T_w,g - T_w,c) = h_c(T_w,c - T_c)

**Adiabatic wall temperature** `[Eq.2]`: `T_aw = T_g(1 + r(gamma-1)/2 * M^2)`, recovery
factor **r = Pr^(1/3)** for turbulent boundary layers (cites Bartz) — a *different* recovery-
factor form than `[Huzel]`'s flat 0.90–0.98 range/`[TN-Dump]`'s 0.88; worth noting as an
alternative functional form, not just a different constant.

**Bartz gas-side h_g** `[Eq.3-5, p.2-3]`: presented in the same functional form already in
`cooling.py`/`[Huzel eq. 4-13]` — `h_g = C*{mu^0.2*cp*Pr^-0.6}_g0 * p_c^0.8 * (c*)^-0.8 *
D_t^-0.2 * (A/At)^-0.9 * delta`, with **C = 0.026** (matches Huzel's Bartz constant) and the
correction factor `delta` as its own closed-form expression (Eq.5) rather than a chart lookup
(`[Huzel Fig 4-24]`, never digitized in this reference set) — **this closed-form `delta` is a
directly usable alternative to `[Huzel]`'s undigitized figure** if `cooling.py` ever wants an
explicit sigma/delta correction instead of its current calibrated-anchor approach. The paper
explicitly flags Bartz's C=0.026 as engine-specific and cites a companion source (Kirchberger
2014) saying it "can be reduced by up to 25%" for a small hydrocarbon engine — a real,
citable data point that the Bartz constant is *not* universal, consistent with why
`cooling.py` calibrates its absolute-flux anchor per propellant class rather than trusting a
single flat Bartz constant.

**Radiation** `[Eq.6-7, p.3]`: separate H2O/CO2 partial-pressure-based correlations (Taw/100)^3.5,
explicitly *not* a T^4 law — the paper itself flags this as likely underestimating radiation at
lower temperatures. Different in form from `[Huzel eq. 4-38]`'s `q = eps*sigma_SB*T^4`; not
recommended as a replacement, just noted as an alternative simplified model in use elsewhere.

**Coolant-side**: Darcy-Weisbach pressure drop (`Eq.8`, standard, matches conventional
practice), Colebrook friction factor (`Eq.9`), single-phase Sieder-Tate correlation (`Eq.11`,
same functional family as `[Huzel eq 4-12]`'s Dittus-Boelter/Colburn form already in
`topics/06`), then a full **two-phase nucleate-boiling treatment** absent from anything else
in this reference set: Chen's superposition model (`Eq.13-20`, forced-convection + nucleate-
pool-boiling with enhancement/suppression factors F/S), a **critical-heat-flux (CHF)
correlation** (modified Tong correlation, `Eq.26-27`, valid range 1–50 bar / 2.5–8mm hydraulic
diameter / 4–60 MW/m² — i.e. explicitly scoped to small-channel high-flux regimes), plus
roughness (`Eq.21`, relevant to additively-manufactured chamber walls) and channel-curvature
(`Eq.22`) correction factors, and a rib/fin efficiency correction (`Eq.24-25`) for the fin
effect of the mid-wall structure between channels.

**Film cooling** `[§2.3, p.6-7]`: liquid-film heat-up (Grisson correlation) then gaseous-film
mixing (cites the **NASA SP-8124 Appendix B model** — a *different* NASA SP monograph, "Liquid
Rocket Engine Self-Cooled Combustion Chambers," not yet in this reference set — flagged as a
literature gap, see Caveats) for the post-vaporization regime.

## Key results — Validation finding (real, quantified model error)

`[§3, p.7-8]`: the paper's own model, run on a CIRA LOX/Methane CFD reference case (Pc 56 bar,
O/F 3.35, 96 channels, 20 g/s/channel, coolant inlet 155 bar/110 K), **overpredicts peak
gas-side heat-transfer coefficient by 42% and peak heat flux by 37.6%** using the standard
Bartz C=0.026; tuning the Bartz constant down brings heat-flux error to 8%. Predicted wall
temperature averaged **~100 K high** vs. the CFD reference. Coolant total pressure drop:
65.35 bar (uncalibrated model) vs. 45 bar (calibrated) vs. 35.6 bar (CFD reference) — i.e.
even the *calibrated* 1D model overpredicts jacket dP by ~26% against a 3D conjugate-heat-
transfer CFD truth case. **This is a real, citable magnitude for how far an uncalibrated
Bartz-based 1D regen model can miss** — directly relevant context for how much
`cooling.py`'s own per-propellant-class `BARTZ_ABS_FLUX_CALIBRATION` anchoring matters (this
paper's finding is independent real-world corroboration that flat/uncalibrated Bartz constants
are unreliable enough to need exactly that kind of anchoring).

## Key results — MINERVA worked design (channel geometry optimization, real numbers)

`[§4, p.9-13]`, coolant inlet 30 bar / 300 K, target: throat wall temp < 1260 K (25% margin
below Inconel 718 melting point), maximize coolant saturation margin, avoid exceeding CHF.
**Number of channels fixed at Nch = 57** (a geometric/manufacturing constraint, not derived).
Optimized (regen-only) result: **final jacket pressure drop ≈ 4 bar**, saturation margin only
**18.84 K** (flagged by the authors as undesirably low — regen cooling alone cannot satisfy
CHF everywhere on this small high-heat-flux engine). Adding **film cooling at 7% of coolant
mass flow** (Table 2, "case 5") drops max wall temp from 1124.5 K to 948 K, raises the
saturation margin to 57.5 K, and drops pressure drop slightly to 3.8 bar — film cooling
supplementing an undersized regen-only design, on a *bipropellant* (LOX/Ethanol, no dedicated
film coolant) small engine. Channel aspect ratio (height/width) and hot-wall thickness were
solved via a genetic-algorithm (NSGA-II) multi-objective optimization, not a closed-form
sizing method — hot-wall thickness converges to its own minimum bound (1 mm, a manufacturing
constraint) in every case; channel width/AR vary by axial region (Table 1: AR 0.6→1.2, width
2.2mm→1.2mm→2.7mm from chamber to throat to nozzle exit).

## Design method

Directly usable as a **worked example of the same Bartz+Dittus-Boelter-family 1D regen model
`engine_designer/physics/cooling.py` already implements**, extended with real two-phase
nucleate-boiling/CHF treatment `cooling.py` does not attempt (`engine_designer` assumes
single-phase coolant throughout; this paper's CHF-margin framing — "regen alone can't clear
CHF near the throat on a small high-heat-flux engine, add film cooling" — is a real,
independently-derived instance of exactly the same regen+film architectural pattern already
implemented via `film_effectiveness_profile`/`dump_coolant_fraction`, corroborating rather
than motivating a new feature). The closed-form Bartz `delta` correction (Eq.5) is the one
piece of genuinely new, directly-transcribable math here if `cooling.py` ever wants Huzel's
undigitized Fig 4-24 sigma-correction as an explicit formula instead of an anchor-calibrated
shape.

## Section map

Whole 15-page paper read in full (no unread sections) — this is a short, single-topic
conference paper with no appendices or supplementary material beyond the reference list
(read for one flagged cross-reference: NASA SP-8124, see Caveats).

## Caveats

- **No manifold-design content whatsoever.** This paper only models 1D flow *inside* the
  cooling channels between a fixed inlet and outlet boundary condition — it says nothing
  about how coolant is distributed to or collected from the channel array (no header/torus/
  manifold geometry, sizing, or flow-distribution treatment). If the user's "manifolds"
  interest was meant to include *this* source, it doesn't deliver on that axis — see
  `[SP-8120] §2.2.5.2` (vanes/splitters/dams/structural supports) or the propellant-intake/
  regen-jacket-manifold treatment already in `engine_designer/physics/manifold.py` instead.
- **No Russian "sandwich" wall-construction content.** Only milled-channel wall construction
  (the type MINERVA is actually built with) is discussed; tube-wall, coax-shell, or sandwich/
  double-wall construction are not mentioned at all.
- **Small-engine, unvalidated-for-this-propellant scope**: MINERVA itself (4 kN, LOX/Ethanol)
  has no experimental cooling data of its own — the paper's only validation is against a
  *different* engine (LOX/Methane, CIRA CFD, Pc 56 bar) run through the same code, explicitly
  described by the authors as validating "the code's system," not the specific ethanol
  two-phase correlations. Treat all MINERVA-specific numbers (4 bar dP, 18.84 K margin, Nch=57,
  channel dimensions) as an illustrative design-space example for a specific small engine, not
  a general design allowable.
- **Uncited literature gap flagged, not filled**: the paper's own gaseous-film-cooling model
  cites **NASA SP-8124, "Liquid Rocket Engine Self-Cooled Combustion Chambers" (Sep 1977)**
  Appendix B — a real NASA SP-8xxx monograph not yet in this reference set's citation table.
  Worth acquiring if a future session wants the primary NASA film-cooling design-criteria
  source directly (this paper only cites its Appendix B model, not the full monograph).
- Ethanol-specific two-phase boiling correlations (Chen/Gungor-Winterton/Cooper) are
  explicitly flagged by the authors as validated only at 10-40 kW/m² heat flux for saturated
  ethanol, while rocket-engine heat flux reaches the MW/m² range — a **two-orders-of-magnitude
  extrapolation the authors themselves call out as unvalidated**, not a hidden caveat.
- Radiation correlation (Eq.6-7) is explicitly non-physical at low temperature (missing T^4
  scaling) per the authors' own admission — don't treat as a general radiation model.
