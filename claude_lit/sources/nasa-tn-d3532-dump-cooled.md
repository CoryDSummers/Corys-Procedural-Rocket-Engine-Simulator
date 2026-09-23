# [TN-Dump] — Design and Cooling Performance of a Dump-Cooled Rocket Engine

## Identity

- **Title**: *Design and Cooling Performance of a Dump-Cooled Rocket Engine*
- **Authors**: Albert J. Pavli, Jerome K. Curley, Philip A. Masters, R. M. Schwartz — NASA
  Lewis Research Center, Cleveland OH
- **Report**: **NASA TN D-3532** (confirmed from PDF metadata subject field)
- **Date**: August 1966 (work completed 10 March 1966). Clearinghouse price $2.00.
- **Extent**: ~45 printed pages + covers, 48 PDF leaves. Older scan; OCR rough (equations
  garble badly — all are standard forms cited to named references).
- **PDF leaf ↔ printed page**: `leaf ≈ printed page + 2`.

## Character

A single-engine design-and-test report. Builds and fires a **500-lbf, 100-psig-Pc,
GH2/LOX** engine with **LH2 dump coolant**, 14 firings (last 4 with an Al₂O₃ refractory
coating). The value here is (a) the *dump-cooling design method* worked in Appendix B, and
(b) as a worked cooling case with real Dittus-Boelter correlations and recovery-factor
values that apply to regenerative cooling too.

## Test article

| Parameter | Value |
|---|---|
| Thrust / Pc | 500 lbf / 100 psig |
| Propellants | GH2 + LOX; design O/F = 5 (16.67 % fuel, φ = 0.63) |
| Coolant | LH2, design flow = 7 % of total propellant flow |
| Injector | 19-element concentric-tube (coaxial): LOX core, GH2 annulus |
| Chamber | contraction ratio 3, injector-to-throat 8 in, **L\* = 20 in**, ε = 2.5, ~10.94 in overall, 15° convergent |
| Wall | two concentric 0.100-in 304 SS shells, 0.10-in radial coolant gap, 8 helical spacers giving 8 spiral coolant paths; helix angle varied along length for locally-optimum coolant velocity |
| Design wall-temp target | 2000 °R flame-side (304 SS limit) |
| Assumed c\* efficiency | 97 %; assumed Cf efficiency 0.983; momentum pressure loss ~2 % |

## Key results

- **Minimum satisfactory coolant flow: 7.5 % of total propellant flow (uncoated), 6.9 %
  (with 0.033-in Al₂O₃ coating).** Not the floor — the report says a passage redesign using
  its own method would go lower.
- Uncoated engine failed by melting through the inner shell just upstream of the throat
  after firing 10; repaired + coated, 4 more firings then failed through the repair weld.
- Refractory coating (0.033-in Al₂O₃): lowers jacket ΔP ~20–30 psi and coolant outlet
  temperature ~90–100 °R at fixed flow.
- **Two over-cooled zones**: first ~3 in from injector, and just downstream of the throat.
  The first-3-in zone is direct empirical evidence that **combustion takes a finite length
  to complete** — the analysis assumed all combustion in zero length and consistently
  over-predicted heat flux there for every firing.
- **Projected potential** (analytical, molybdenum inner shell instead of 304 SS): max
  flame-side wall temp 3560 / 3160 °R for two thicknesses → coolant outlet 1900 / 1575 °R →
  theoretical dumped-H2 Isp up to 560 / 510 s (Fig 1) — i.e. **coolant Isp can equal or
  exceed the main-chamber Isp** with a refractory-metal shell.

## Design method (Appendix B) — what to reuse

Iterative march along the engine axis (11 increments), solving for local coolant-passage
width to hold flame-side wall temperature at the material limit, using **real
temperature-dependent coolant transport properties** (density, Cp, viscosity of H2 change
enormously as it heats):

- **Gas-side heat-transfer coefficient**: `Nu_f = 0.023 · Re_f^0.8 · Pr_f^0.4`
  (Dittus-Boelter), properties at film temperature `T_f,g = ½(T_g,w,ad + T_w,g)`.
  B = 0.023, M = 0.8, N = 0.4 "as is current practice."
- **Adiabatic (recovery) wall temperature** uses recovery factor δ that "increases with
  Reynolds number to approximately 0.90 in turbulent flow; a value of **0.88** was
  selected."
- **Coolant-side heat-transfer coefficient**: same Dittus-Boelter form (`Nu = 0.023 Re^0.8
  Pr^0.4`) for subcritical-pressure H2 gas/vapor (ref. Hendricks et al., ARS J 1962).
- **Coolant-passage pressure drop** = momentum term + frictional term (both significant
  because H2 density changes a lot down the passage).
- Appendix C = off-design prediction; "compensated analytical" curves account for the
  depressed-heat-flux first-3-in zone.
- Appendix C compares four heat-flux criteria; **Curve 3 ≈ the "simplified Bartz equation"**
  (Bartz, *Jet Propulsion* 27(1), Jan 1957, pp. 49–51 — ref. 13) with B = 0.026 constant;
  throat Reynolds number 0.275×10⁶ (low, because Pc is only 100 psig).

## Section map

| Section | Printed p. | Content |
|---|---|---|
| Summary + Introduction | 1 | Dump-cooling concept (Rocketdyne, unpublished): coolant through a C-D nozzle instead of into the chamber → jacket ΔP in **parallel** with injector ΔP → lower tank pressure / lighter tanks; Fig 1 = theoretical vacuum Isp of dumped H2 vs H2 temperature (infinite-area-ratio nozzle) |
| Apparatus | 4 | injector, chamber contour (Fig 3), double-shell construction, instrumentation |
| Procedure / Firing Description | 8 | LH2 precool; 10-s firings; Table I = 14 firings (O/F 2.27–5.46, coolant flow, % of propellant flow, chamber total temp ~5235–5360 °R) |
| Results and Discussion | 15 | measured vs analytical heat flux / coolant temp / pressure (Figs 11–20); Fig 20 = projected performance with Mo shell |
| Appendix A | 27 | symbols |
| Appendix B | 32 | **coolant-passage design method** (above) |
| Appendix C | 41 | off-design performance prediction; Bartz comparison |
| Appendix D | 42 | coolant-passage geometry (spacer helix) |
| Appendix E | 44 | data collection; Table II experimental data |
| References | 45 | incl. NASA TN D-66 (regen-cooling capability), Svehla NASA SP-3011 (H2-O2 transport props), Bartz 1957 |

## Caveats

- Single design point, tiny engine (100 psig Pc, ε 2.5) — quantitative numbers (min coolant
  fraction, jacket ΔP) do not scale directly; the *method* and the *correlations* generalise.
- The report itself flags that its original transport-property data (Appendix B) were later
  found incorrect and re-fitted for the data reduction (ref. 2, Svehla).
