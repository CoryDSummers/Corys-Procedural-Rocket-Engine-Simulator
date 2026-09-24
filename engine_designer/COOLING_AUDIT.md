# Cooling-physics audit (2026-09-23)

A full review of every cooling path in `engine_designer/`. It checked the physics against real engines, fixed the bugs it found, and records what is still missing. It was prompted by inconsistent wall temperatures and margins, film/dump/Isp costs, jacket dP and coolant temperatures, checklist rows that disagreed with the numbers, and LOX/LH2 thermal properties that looked wrong across mixture ratio.

**How to re-check any of this:**

```
./verify_all.sh                                                        # full suite (validate: 26 banners)
python3 -m engine_designer.validation_engines.run_corpus --report      # real engines vs cited data + probes
python3 -m engine_designer.validation_engines.run_corpus --report --diff   # ... and change vs golden/
```

- The real-engine corpus is in `validation_engines/engines/`. `build_corpus.py` regenerates it; every number is cited or flagged as a stand-in.
- Frozen copies of Cory's own designs are in `validation_engines/user_designs/`.
- The before/after of this round is in `validation_engines/reports/2026-09-23_cooling_audit_before_after.txt`.

## Root causes, in one paragraph

Most symptoms came from five things:

1. The "computed" throat wall temperature was circular. The flux model assumed T_wg = 0.25·T_aw, and the design then inverted that flux back out.
2. T_aw was taken as 0.9·Tc. It should be T_s + r(T0 − T_s), which is about 0.99·Tc at the throat.
3. LOX/LH2 heat-transfer properties were derived from the *performance* table's effective γ and M. Those values break mass balance and push γ in the wrong direction with MR, so h_g swung about 1.7× across MR.
4. LH2 coolant properties paired liquid density and viscosity with gas cp, and the inlet was 100 K.
5. The same quantity was computed several different ways in different places, and a per-propellant flux calibration (LH2 0.55) was hiding the errors.

## Findings and status

| ID | Finding | Status / where |
|---|---|---|
| G1 | LOX/LH2 `_TABLES` M exceeds the mass-balance ceiling (M_H2·(1+MR)) at MR ≤ 5.5; γ rises with MR | **Fixed for heat transfer.** `combustion.heat_transfer_gas_properties` reads Cantera equilibrium tables (`tools/property_tables/`, self-checked against Sutton Table 5-5). The *performance* table is untouched; see open item P1 |
| G2 | cp is neither frozen nor equilibrium; Eucken Pr too high; μ fit about half the real value | **Fixed.** Frozen cp, mixture-averaged μ/λ and frozen Pr come from the tables (LOX/LH2 MR 6: cp 3789, μ 1.0e-4, Pr 0.62) |
| G3 | T_aw = 0.9·Tc | **Fixed.** Per-station T_aw = T_s + r(T0 − T_s) with r = Pr^(1/3) (`cooling.adiabatic_wall_temperature_profile`). `recovery_temperature()` was corrected too |
| G4 | Bartz σ fixed at 1; calibration applied in some paths and not others | **Fixed.** Real σ(T_wg/T0, M) is iterated in the solve (`cooling.bartz_sigma`). Calibration and deposit factor are applied once, to the one h_g |
| G5 | MR outside the table silently clamped; the checklist said "extrapolated" | **Fixed wording.** The row now says clamped, and the gas-table clamp is reported |
| C1 | Constant coolant properties; LH2 liquid ρ/μ with gas cp; plain Dittus–Boelter | **Fixed.** `CoolantModel` uses CoolProp tables (para-H2, CH4, n-dodecane as the RP-1 surrogate), an enthalpy march, Sieder–Tate with the wall-viscosity term plus a laminar floor, and the [EUCASS-2023 Eq. 24–25] rib/fin factor |
| C2 | LH2 inlet 100 K; SSME coolant ΔT 23 K | **Fixed.** Inlet is 45 K [TN-Dump]; SSME-class ΔT is now about 140 K |
| C3 | A-50/N2H4/HTP: silent ΔT = 0, TypeError in dump sizing, KeyError in the expander | **Fixed.** Generic fallback plus a checklist warning; one shared limit fallback; expander uses `.get`. Covered by the new 193-combination sweep in validate |
| W1 | Circular throat T_wg: radiative/uncooled chambers showed a fake cool wall | **Fixed.** Radiation equilibrium for radiative/uncooled stations; coupled balance for regen; no inversion anywhere |
| W2 | Dump-slice heat charged to both the regen jacket (plus regen credit) and the dump bleed | **Fixed.** The regen jacket stops at the transition; the dump slice has its own auto-sized bleed, subtracted from jacket flow |
| W3 | Chamber-film c* penalty on the total-flow basis, (1+MR)× too big | **Fixed.** Now 0.5·f/(1+MR) |
| W4 | Pumps sized on a conical pre-march dP; real-contour dP thrown away | **Fixed.** The real contour is built before the pump chain; one march feeds pumps, GUI and structure |
| W5 | Film temperature from the pre-march ΔT | **Fixed.** The post-jacket film temperature is iterated inside the solve |
| W6 | Two throat fluxes, three T_wc, two wall thicknesses; flux taken as max(profile), not at the throat | **Fixed.** One solve; throat values at the throat station; the reported coolant-side wall is the solved one |
| W7 | Throat row warned below 1.15×, peak row failed only below 1.0×; burn time ignored the peak; wrong film eps reported | **Fixed.** Both rows use `THIN_MARGIN_THRESHOLD`; burn time uses min(throat, peak) |
| W8 | Regen credit scaled with ΔT/limit (bypass inflated it) and applied to GG-averaged Isp | **Fixed.** 0.5 × Q_regen / (ṁ·cp·Tc), capped at 1.5%, chamber stream only |
| W9 | Expander turbine heat ignored film, bypass and method | **Fixed.** Turbine heat is the solve's regen heat; absorbable heat uses enthalpy |
| W10 | Jacket dP keyed only on chamber method; pressure-fed ignored jacket dP | **Fixed.** Pressure-fed tank pressure includes jacket dP. The dump bleed is a parallel branch that never governs pump discharge (its dP is reported) |
| W11 | Wall-energy fraction used ½ṁc*² (about 5× too small for LH2), so every LH2 engine read 7–25% | **Fixed.** Now ṁ·cp·Tc: F-1 0.4%, SSME 1.2%, RL10 4.3%, all inside [Sutton 8.2]'s 0.5–5% band |
| W12 | Milled channels had a fixed 1.5 mm hot wall while tube walls were structurally sized (1800 K across an Inconel wall) | **Fixed.** Huzel eq. 4-27/4-28 sizing for every construction, floors 0.20 mm tube [Huzel] / 0.5 mm channel [Fagherazzi] |
| W13 | A "regenerative" nozzle with `regen_nozzle_end_eps = 0` had nothing cooling the bell, and was checked against the local gas temperature | **Now explicit.** Those stations are solved uncooled (radiation equilibrium), with a warn-only checklist row saying so |
| V1 | Validation engine definitions disagreed between checks | **Partly fixed.** The corpus holds one cited definition per engine. The validate checks keep their own historical definitions (open item P3) |
| V2 | validate stopped at the first failing check | **Fixed.** It runs every check and fails at the end |
| — | Flux calibration LH2 0.55 / CH4 0.75 | **Retired, then LH2 re-solved (follow-up below).** The old factors compensated for bugs. Once the coolant side was fixed, raw Bartz read the SSME at 164 against 118, so LOX/LH2 is now **0.66, reverse-solved to the one cited SSME design point** (Cory's call; Tier 2). RP-1 keeps its cited deposit factor; CH4 is 1.0 (no anchor) |

## Before → after (corpus)

Pre-audit golden → this round. Full per-metric detail is in the report file.

| design | q throat MW/m² | T_wg throat K | margin | coolant ΔT K | jacket dP MPa | Isp vac s |
|---|---|---|---|---|---|---|
| engines/AJ10-137 | 3.185 → 2.077 | - | 1.867 | 0 | 0 | 313.9 |
| engines/Aestus | 5.935 → 9.882 | 812.9 → 847 | 1.353 → 1.299 | 140.8 → 247 | 3.906 → 4.463 | 308.1 |
| engines/F-1 | 17.1 → 14.6 | 868.8 → 1097 | 1.439 → 1.14 | 85.39 → 67.26 | 0.6452 → 1.282 | 302.1 → 299.4 |
| engines/J-2 | 14.13 → 38.5 | 548.4 → 1119 | 2.006 → 0.9829 | 42.38 → 120.6 | 1.544 → 2.851 | 418 → 421.5 |
| engines/LMAE | 4.572 → 2.534 | - | 1.849 | 0 | 0 | 310.2 |
| engines/Merlin-1D | 30.91 → 31.64 | 944.1 → 799.1 | 0.8474 → 1.001 | 148.7 → 124.5 | 1.688 → 1.753 | 301.8 → 299.1 |
| engines/RD-180 | 65.02 → 53.93 | 1424 → 1272 | 0.5618 → 0.6288 | 127.5 → 91.63 | 0.8559 → 0.9995 | 322.6 → 318.1 |
| engines/RL10A-3-3 | 10.74 → 31.67 | 442.7 → 834 | 2.485 → 1.319 | 100.4 → 291.3 | 3.047 → 11.53 | 448.5 → 453.5 |
| engines/RS-25 | 43.31 → 142.2 | 816.5 → 1019 | 0.9798 → 0.7848 | 47.37 → 140.9 | 0.6825 → 1.715 | 423.6 → 426.5 |
| engines/Raptor-2 | 72.83 → 125 | 1296 → 1350 | 0.6946 → 0.6669 | 112.3 → 206 | 0.9109 → 1.673 | 349.7 → 347.1 |
| engines/Rutherford | 51.39 → 28.97 | 2038 → 1839 | 0.6134 → 0.6797 | 599.7 → 314.9 | 6.458 → 6.169 | 302.8 |
| engines/Vulcain | 27.84 → 91.65 | 622.3 → 801.1 | 1.286 → 0.9986 | 46.98 → 92.91 | 0.5689 → 1.082 | 429.9 → 429.1 |
| user_designs/AJ-90k | 9.659 → 0.8216 | 1308 → 2131 | 0.9556 → 0.5865 | 25.7 → 0 | 0 | 445.4 → 454.3 |
| user_designs/LR-100 | 20.22 → 17.11 | 865.1 → 1039 | 1.272 → 1.059 | 115.6 → 91.71 | 0.8287 → 1.299 | 331.8 → 328.6 |
| user_designs/RS-29 | 33.42 → 23.85 | 1155 → 1464 | 1.082 → 0.8541 | 96.94 → 71.22 | 0.6099 → 1.036 | 315.7 → 312.9 |
| user_designs/RS-29A | 33.42 → 23.58 | 1181 → 1483 | 1.058 → 0.8431 | 113.3 → 82.63 | 0.5096 → 1.001 | 316.3 → 313 |
| user_designs/RS-29C | 27.93 → 26.64 | 904.7 → 794.9 | 0.8843 → 1.006 | 84.55 → 71.48 | 0.587 → 1.024 | 305.8 → 308.8 |
| user_designs/RS-30 | 38.42 → 22.63 | 1841 → 1782 | 0.679 → 0.7016 | 76.84 → 52.27 | 0.5669 → 0.8515 | 314.8 → 312.4 |
| user_designs/TRW-270 | 3.754 → 6.155 | 676.2 → 746.4 | 1.627 → 1.474 | 0 → 202.8 | 1.6 | 303.6 |
| user_designs/j-2_test_bed | 21.25 → 47.92 | 717.3 → 1393 | 1.743 → 0.8973 | 28.75 → 71.86 | 0.4847 → 1.166 | 415.3 → 417.1 |

Every design now closes both self-consistency probes: throat q = h_g(T_aw,f − T_wg) to 1.00, and jacket Q_regen = ṁ·Δh to 1.000. Before the fixes, several designs were off by 16–80%.

### What changed for Cory's designs

- **AJ-90k.** The chamber is a schema-7 "film" chamber, migrated to uncooled Inconel plus film. The old circular path showed 1308 K; the real radiation-equilibrium answer is about 2130 K, well over Inconel's 1250 K. It needs a regen jacket or much more film.
- **RS-29 / RS-29A.** At 12 MPa with RP-1 at 35 m/s, the Inconel throat runs about 1460–1480 K (limit 1250 K). RS-29 also has a stainless bell from ε 12 to 18 that is "regenerative" but has no jacket past `regen_nozzle_end_eps` = 12, and it reaches about 2170 K. Levers: faster coolant, a copper-alloy liner, film, and extending the regen end to ε 18.
- **RS-29C.** The NARloy-Z variant now clears, about 1.0×.
- **RS-30.** The Inconel regen throat runs about 1780 K.
- **j-2 test bed.** The throat is about 1390 K. The Inconel bell from ε 14 to 27.5 is uncooled (regen end 0) and reaches about 2300 K.
- **LR-100.** About 1.06×, a thin margin.
- **TRW-270.** OK. Its Aerozine-50 regen jacket used to be silently zero; it now solves with generic fallback coolant properties, and the checklist warns about that.

## Follow-up: coolant-side gap closed (2026-09-23)

**The problem.** After the audit, the SSME coolant-side throat wall was about 800 K against [Wieseneck-J2]'s 478 K. That is an effective h_c about 2× low.

**What the model experiments showed.**
- The staged-combustion cycle itself contributes about 0%. In this model the cycle doesn't touch the cooling circuit.
- Jacket pressure is worth only about 4–15%.
- Channel count matters a lot. But **no cited SSME channel geometry exists** in any source in `literature/`: three focused re-reads covered Wieseneck, SECA-FR-93-18, SP-8087, Sutton, Huzel, the J-2X paper, AEDC J-2S, IAC-19 and Merkle.
- What the literature *does* give is the mechanism. [Wieseneck-J2 p.24–25] says the SSME design relied on H2 coolant-side enhancement:
  - roughness about 1.45–1.55× at 200 µin;
  - curvature from 1.0 up to about 1.9× through the throat turn;
  - "more than doubled" in the high-flux region.

**What was done.**
- **Roughness and curvature factors.** `coolant_side_htc` now applies [EUCASS-2023] Eq. 21 (roughness; same Haaland friction and 6 µm roughness as the jacket dP) and Eq. 22 (curvature). The bend geometry comes from the real contour (`profile.bend_segments`): "+" on the throat arc, "−" at the cylinder-to-convergent fillet, and only where the wall radius is under 2 throat diameters.
- **Roughness cap.** Eq. 21 extrapolates to about 1.9–2.0× at SSME Reynolds numbers, so the roughness factor is capped at Wieseneck's measured 1.55× (`ROUGHNESS_FACTOR_MAX`).
- **LOX/LH2 h_g factor 0.66.** The colder wall then drew 164 MW/m² at the SSME throat against the cited 118. With Cory's approval, a single LOX/LH2 h_g factor of 0.66 was reverse-solved to that point.
- **J-2 tube count.** The J-2 corpus engine now uses its cited 360 up / 180 down tubes [AEDC-J2S].

**Result.**

| SSME check | Model | Cited |
|---|---|---|
| Throat flux | 118.9 MW/m² | 117.7 design point |
| Coolant-side wall | 376–390 K | 478 ± 150 K |
| Gas-side wall | 562–572 K | < 811 K copper limit |
| J-2 throat flux | 32.7 MW/m² | 28–57 band |

The SSME Wieseneck wall comparison is a **gate again** in validate (26/26 pass).

**Auto-sizer: deliberately not changed.**
- At the 8:1 aspect-ratio cap, adding channels *raises* mass flux; it does not restore the target velocity. A cited count only exists for the J-2.
- LH2's 95 m/s at inlet density (G ≈ 5000–6700 kg/m²·s) was left alone.

| design | q throat MW/m² | T_wg throat K | margin | coolant ΔT K | jacket dP MPa |
|---|---|---|---|---|---|
| engines/F-1 | 14.6 → 15.65 | 1097 → 973.5 | 1.14 → 1.284 | 67.26 → 68.62 | 1.282 |
| engines/J-2 | 38.5 → 32.65 | 1119 → 690.4 | 0.9829 → 1.593 | 120.6 → 93.06 | 2.851 → 3.712 |
| engines/Merlin-1D | 31.64 → 32.94 | 799.1 → 722 | 1.001 → 1.108 | 124.5 → 125.7 | 1.753 |
| engines/RD-180 | 53.93 → 58.73 | 1272 → 1109 | 0.6288 → 0.7215 | 91.63 → 93.29 | 0.9995 |
| engines/RL10A-3-3 | 31.67 → 24.73 | 834 → 550.5 | 1.319 → 1.998 | 291.3 → 208.5 | 11.53 → 8.966 |
| engines/RS-25 | 142.2 → 118.9 | 1019 → 571.7 | 0.7848 → 1.399 | 140.9 → 111 | 1.715 → 1.509 |
| engines/Raptor-2 | 125 → 148 | 1350 → 1039 | 0.6669 → 0.8659 | 206 → 221.7 | 1.673 → 1.718 |
| engines/Vulcain | 91.65 → 74.92 | 801.1 → 413.2 | 0.9986 → 1.936 | 92.91 → 70.33 | 1.082 → 0.9494 |
| user_designs/LR-100 | 17.11 → 17.77 | 1039 → 968.8 | 1.059 → 1.135 | 91.71 → 93.44 | 1.299 |
| user_designs/RS-29 | 23.85 → 25.85 | 1464 → 1328 | 0.8541 → 0.9413 | 71.22 → 73.05 | 1.036 |
| user_designs/RS-29A | 23.58 → 25.76 | 1483 → 1334 | 0.8431 → 0.937 | 82.63 → 84.6 | 1.001 |
| user_designs/RS-29C | 26.64 → 27.85 | 794.9 → 727.1 | 1.006 → 1.1 | 71.48 → 72.38 | 1.024 |
| user_designs/RS-30 | 22.63 → 24.1 | 1782 → 1686 | 0.7016 → 0.7414 | 52.27 → 53.63 | 0.8515 |
| user_designs/j-2_test_bed | 47.92 → 43 | 1393 → 902.3 | 0.8973 → 1.385 | 71.86 → 58.38 | 1.166 → 1.028 |

Full detail: `validation_engines/reports/2026-09-23_coolant_side_followup_before_after.txt`.

**Remaining limits.**
- RP-1 and CH4 have no cited throat-flux anchor. Raptor-2 and RD-180 still read hot on their stand-in copper walls.
- The Inconel-walled RS-29 / RS-29A / RS-30 remain over their limit at the throat: about 1330 K and 1690 K against 1250 K.

## Follow-up: tube-wall structural row false alarm (2026-09-24)

**The problem.** The "Jacket overpressure vs. channel-wall structural margin" row (tube_wall / coax_shell) added the hoop stress to Huzel's eq 4-28 thermal-restraint stress. It then held the sum to `allowable_stress_pa / 1.5`, a yield value taken near the material's *max service temperature*. That failed every real tube-wall engine in the corpus: F-1 at 423 vs 133 MPa, J-2 at 990 vs 67, RL10A-3-3 at 761 vs 67. It also failed Huzel's own Sample Calc 4-4 and Cory's H-1-class stainless design (456 vs 67 MPa). On that same H-1 the "Throat thermal-fatigue cycle life" row, working from the same through-wall gradient, gave about 95,000 cycles.

**Root cause: the criterion, not the stress.** The thermal-restraint stress comes from an imposed strain, so it is *secondary* and self-limiting. Once the hot face yields, the stress stops growing and turns into cyclic plastic strain, which is a low-cycle-fatigue limit (the fatigue row), not a burst limit. Only the *primary* hoop stress from the net coolant-vs-gas ΔP is load-controlled. This is the standard primary/secondary classification (ASME BPVC Sec. III). Tier 2: it is a standard principle, but no source in `claude_lit/` states it.

**What was done.**
- `structure_stage.wall_structure`: pass/fail now checks primary hoop against allowable/SF only. The governing station is chosen by hoop utilisation. Combined, hoop and thermal stresses are still reported. The row text quotes the throat thermal-restraint stress and, when hoop + thermal is above yield, points to the fatigue row.
- `mass_model.regen_hot_wall_thickness_m`: the wall is t* (the min-combined-stress gauge that matches Huzel A-1) but never thinner than the gauge that carries the hoop load, `SF·|ΔP|·r/σ`. It is used by both the thermal solve's throat wall and the structural check. It is a no-op on the whole corpus's throat walls; it thickens only the structural gauge at the end-of-cooling station where t* left the hoop load over the allowable.
- `validate/structures.py`: Huzel A-1/A-2 primary hoop ≤ F_ty/SF and his elastic rule combined ≤ F_ty. The real F-1 / J-2 / RL10 (from `validation_engines/engines/`) must pass the row, and a coax_shell J-2 must still trip it. Banner count stays 26.

**Corpus.** 7 designs flip from FAIL to PASS on this row (F-1, J-2, RL10A-3-3, LR-100, RS-29, RS-29A, j-2_test_bed); RS-29C gets new OK text only. There are no thermal, mass or performance changes. Golden files were patched only on the changed keys, so they stay valid in Cory's environment. Full detail: `validation_engines/reports/2026-09-24_tube_wall_secondary_stress_before_after.txt`.

## Open items / where more information is needed

1. **Coolant-side heat transfer: resolved.** See the follow-up above. What's left is data: real per-engine channel geometry, jacket flow split and coolant inlet state. None of it is in `literature/`; SSME MCC geometry is likely in SECA-P-90-09, the Phase I report, which isn't in the collection.
2. **P1 – performance table.** The LOX/LH2 γ/M columns in `combustion._TABLES` are effective performance numbers, not physical ones. The equilibrium tables also carry c* and Isp at ε 10/40/100, so a re-anchored performance path is possible. That changes every Isp spot check and `DEFAULT_ETA_CSTAR`, so it needs its own plan. Symptoms today: RS-25 vacuum Isp is 6% low (427 vs 455); RD-180 is 6% low (318 vs 338).
3. **P2 – RL10 jacket dP.** With the real H2 expansion and auto-sized channels (224 at the 1.2 mm pitch floor), the full-length RL10 jacket reads about 11.5 MPa. The real RL10 has 180 larger tubes. Per-engine channel data would fix this; set `regen_channel_count` in the corpus if a cited count becomes available.
4. **P3 – validate definitions.** validate's COOLING_CHECKS still uses its historical stand-ins (F-1 as NARloy-Z at 7.77 MN, "RL10-class" at 3.2 MPa). Migrating them to load from the corpus JSONs would remove the drift.
5. **Literature gaps.** Cooling data is cited only for F-1 / J-2 / SSME. Still needed: throat flux, coolant ΔT, jacket dP, liner thickness and coolant velocity for RL10, Vulcain, RD-180, Merlin, Raptor, Rutherford, Aestus. Also NASA SP-8124 (film effectiveness) and an RP-1 coking rate model (see `claude_lit/OPEN_QUESTIONS.md`).
6. **Hydrazine and H2O2** have no equilibrium table (catalytic decomposition is non-equilibrium). They keep the legacy derived gas properties, flagged `gas_property_source = legacy`.
7. **Thermal ratcheting (Bree diagram).** Not modelled. With x = hoop/σy and y = thermal/σy, a Bree check would flag ratcheting where xy > 1. With today's room-temperature k/E/σy it would flag the real J-2 and RL10 too, so it needs temperature-dependent k(T), E(T) and σy(T) per material first. The SSME-style "dog-house" throat failure is the classic example of this mechanism.

## Structure after this round

- `physics/cooling/` package:
  - gas_side, profile, coolant_props, coolant_state, methods, dump, radiation, regen_credit, film, channels, wall, march
  - **thermal_solve** (the unified per-station solve)
- `physics/design/` package:
  - constants, checklist, state, engine
  - 17 stages in `*_stage.py`; `cooling_stage.thermal` runs before the pump chain
- `physics/validate/` package: 26 checks, all run; the failure summary prints at the end.
- `physics/thermo_tables.py` plus `physics/property_data/*.json`: generated by `tools/property_tables/generate_property_tables.py`. Kept and re-runnable locally or on Colab; never hand-edited.
- `validation_engines/`: the corpus plus `run_corpus.py`; its `--check` is part of `verify_all.sh`.
