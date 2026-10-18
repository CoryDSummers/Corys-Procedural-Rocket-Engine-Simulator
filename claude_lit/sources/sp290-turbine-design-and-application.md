# NASA SP-290 — Turbine Design and Application

## Identity

NASA SP-290, *Turbine Design and Application*, edited by Arthur J. Glassman (NASA Lewis
Research Center). NASA Scientific and Technical Information Program, **1994 reprint** of the
three-volume edition (Vol. 1 1972, Vol. 2 1973, Vol. 3 1975). Course notes from the Lewis
In-House Graduate Study Program course given 1968-69 and 1972-73. Chapter authors: Glassman
(Ch. 1-2, 4), Whitney & Stewart (Ch. 3), Stewart (Ch. 4), Katsanis (Ch. 5), McNally (Ch. 6),
Prust (Ch. 7), Roelke (Ch. 8), Goldman (Ch. 9), Rohlik (Ch. 10), Colladay (Ch. 11), Szanca &
Schum (Ch. 12). NTRS 19950015924 (N95-22341). LoC card 94-67487.
`literature/NASA SP-290 - Turbine Design and Application.pdf` (renamed 2026-10-18 from the
NTRS number). 392 PDF leaves (0-391). The text layer is the NTRS OCR and is good for prose
but garbles every equation and figure. Equations and figures cited below were read from
rendered page images unless marked otherwise.

**Printed page → leaf offset varies by chapter**, because unnumbered blank and plate leaves
were dropped differently in each volume:

| Chapters | Offset (leaf = printed + k) | Check |
|---|---|---|
| Front matter, Ch. 1-2 (p.1-67) | +5 | p.37 = leaf 42, p.62 = leaf 67 |
| Ch. 3 (p.69-99) | +4 | p.84 = leaf 88 |
| Ch. 4 (p.101-125) | +3 | p.101 = leaf 104 |
| Ch. 5-11 (p.127-349) | +2 | p.233 = leaf 235, p.287 = leaf 289 |
| Ch. 12 (p.351-390) | +1 | p.381 = leaf 382 |

Tag: `[SP-290]`. Cite as `[SP-290 Ch.N eq./Fig. p.NN]` (printed page).

## Character

SP-290 is a **general aerodynamic turbine textbook**. Its reference frame is NASA Lewis
air-breathing and space-power turbines, not rocket turbopumps. It is the general-theory
companion to `[SP-8110]`, the rocket-turbine design-criteria monograph, which gives the
Rocketdyne fleet data (Table I, U/C0 per engine) and the staging rules. SP-290 supplies the
derivations underneath those rules:
- efficiency definitions (total-to-static vs total-to-total) and how they relate;
- the velocity-diagram parameters (blade-jet speed ratio ν = U/C0, speed-work parameter λ)
  and how they map onto each other;
- idealized efficiency curves vs λ for 1, 1½, 2 and n stages, plus impulse, symmetrical and
  zero-exit-swirl diagram types;
- the "miscellaneous" loss correlations: tip clearance, **Daily-Nece disk friction**,
  partial-admission pumping and sector loss, and incidence.

The text is trustworthy as engineering-textbook material from a primary NASA turbine group.
The efficiency curves are **idealized analyses** (references to NACA/NASA reports, constant
loss-coefficient models). Use them for shape, optimum location and ratios, not absolute
level. Their plateau of about 0.88-0.90 total is 15-30 points above real rocket GG turbines.
There is **no rocket-turbine fleet data** (use `[SP-8110]` Table I and `[SP-8107]`
Table III). Rockets appear only in passing (nuclear-H2 turbopumps need many stages, Ch. 3
p.82; the M-1 fuel-turbine scale model and a 2-stage velocity-compounded turbine are cited
as references in Ch. 9). There is also **no Balje-type Ns-Ds efficiency chart for axial
turbines**. Specific diameter is defined, but the only efficiency-vs-specific-speed chart is
for radial-inflow turbines (Fig. 10-7).

## Turbine-efficiency parameters and loss correlations (the usable content)

Notation in SP-290: unprimed η = **static** (total-to-static, T-S) efficiency; primed η′ =
**total** (total-to-total, T-T) efficiency. Δh_id = ideal work from inlet total to exit
**static** pressure; Δh′_id = ideal work from inlet total to exit **total** pressure;
Δh′ = actual work (drop in total enthalpy). In SI, g = J = 1.

| Quantity | Relation | Cite |
|---|---|---|
| Static (T-S) efficiency | η = Δh′/Δh_id. Ideal gas: η = (T′_in − T′_ex)/(T′_in[1 − (p_ex/p′_in)^((γ−1)/γ)]) | `[SP-290 Ch.2 eq.2-48 p.40]` |
| Total (T-T) efficiency | η′ = Δh′/Δh′_id, with p′_ex (exit total) replacing p_ex | `[SP-290 Ch.2 eq.2-49 p.40]` |
| T-S vs T-T, loss bookkeeping | Δh_id = Δh′ + L_stator + L_rotor + V₂²/2. η′ is the same expression **without the leaving loss V₂²/2** | `[SP-290 Ch.3 eq.3-13, 3-14 p.75]` |
| Ideal-work ratio | Δh′_id = Δh_id·(η/η′) | `[SP-290 Ch.2 eq.2-95 p.53]` |
| Which to use | Use T-S when the exhaust kinetic energy is wasted (dumped to a plenum). Use T-T when it is useful downstream (jet engine). In a multistage turbine only the **last** stage's exit KE counts as lost. "Total efficiency is always higher than static efficiency, with the difference … increasing with increasing exit kinetic energy." | `[SP-290 Ch.2 p.39]` |
| Blade-jet speed ratio (= U/C0) | ν = U/V_j, V_j = √(2·Δh_id): the spouting velocity of the inlet-total to **exit-static** expansion | `[SP-290 Ch.2 eq.2-70-2-72 p.48]` |
| Speed-work parameter / loading | λ = U²/Δh′ (stage), ψ = 1/λ = Δh′/U²; for axial flow λ = U/ΔV_u | `[SP-290 Ch.2 eq.2-66-2-69 p.47-48]` |
| ν ↔ λ | **ν = √(λη/2)**, i.e. λ = 2ν²/η (η = static) | `[SP-290 Ch.2 eq.2-74 p.48]` |
| Overall parameters | λ̄ = U_av²/Δh̄′, ν̄ = U_av/√(2Δh̄_id) — **mean blade speed, not √ΣU²** | `[SP-290 Ch.2 eq.2-102, 2-103 p.54]` |
| Idealized single impulse stage | η = 4ν sin α₁ − 4ν²; ν_opt = sin α₁ / 2, which is 0.4-0.5 for α₁ 60-80°. At α₁ = 70° the maximum is η 0.88 at ν 0.47 | `[SP-290 Ch.2 eq.2-88, 2-89, Fig.2-12 p.51-52]` |
| Stage count from specific speed | n = (N_s,stage / N̄_s,overall)^(4/3) (no reheat, equal head per stage, incompressible) | `[SP-290 Ch.2 eq.2-109 p.56]` |
| Stage count from speed-work | **n = λ_stage / λ̄_overall** (constant U, equal work per stage) | `[SP-290 Ch.2 eq.2-111 p.57; Ch.3 eq.3-16 p.82]` |
| Multistage overall efficiency (no reheat) | η̄ = n / (1/η′_a + (n−2)/η′_i + 1/η_i); η̄′ = n / (1/η′_a + (n−1)/η′_i). a = first stage, i = general stage | `[SP-290 Ch.3 eq.3-18, 3-19 p.83]` |
| Reheat: overall vs stage efficiency (n equal stages, constant stage PR p′₂/p′₀ and η′_stg) | **η̄′ = {1 − [1 − η′_stg·(1 − (p′₂/p′₀)^((γ−1)/γ))]^n} / {1 − (p′₂/p′₀)^(n(γ−1)/γ)}**. Confirmed on the page image (leaf 47, 2026-10-18); p′₂/p′₀ is the **per-stage** ratio, n the stage count. Derivation is in the chapter's ref. 1 | `[SP-290 Ch.2 eq.2-52 p.42]` |
| Overall vs polytropic efficiency | **η̄ = [1 − (p_ex/p_in)^(η_p(γ−1)/γ)] / [1 − (p_ex/p_in)^((γ−1)/γ)]**. Confirmed on the page image (leaf 49, 2026-10-18); obtained by equating eq. 2-60 and 2-61 (actual temperature drop). Fig. 2-10 plots it for γ 1.4, PR 1-50. Derived from the equation (my arithmetic), γ 1.4: η_p 0.6 → η̄ 0.65 / 0.70 / 0.73 at PR 5 / 20 / 50; η_p 0.7 → 0.75 / 0.78 / 0.81. At γ 1.3 these fall by 0.01-0.02 | `[SP-290 Ch.2 eq.2-62, Fig.2-10 p.44]` |
| Specific speed / diameter | N_s = N·Q_ex^½ / H^¾, D_s = D·H^¼ / Q_ex^½. Q at the **exit**; H "usually" T-T ideal work, "sometimes" T-S. N_s·D_s = (K/π)·√(2gη′/η)·ν | `[SP-290 Ch.2 eq.2-91-2-96 p.52-53]` |
| Reynolds-number scaling | (1 − η′₁)/(1 − η′₂) = A + B·(Re₂/Re₁)^0.2, with A ≈ 0.3-0.4 and B ≈ 0.7-0.6 (A + B = 1). Pure-friction ideal exponent is 0.2; real machines 0.1-0.2 | `[SP-290 Ch.2 eq.2-141, 2-142 p.61-62]` |
| Tip clearance, unshrouded (Fig. 8-3, after Boeing D4-3220) | η/η₀ falls linearly with clearance/passage height c/h. Read visually at c/h = 0.03: reaction 0 → 0.951, 0.1 → 0.948, 0.2 → 0.944, 0.3 → 0.940, 0.4 → 0.935, 0.5 → 0.930, 0.6 → 0.921, 0.7 → 0.910 (±0.003). As a slope: **Δη/η₀ ≈ −k·(c/h), k ≈ 1.6 (impulse) to 3.0 (reaction 0.7)** | `[SP-290 Ch.8 Fig.8-3 p.228]` |
| Tip clearance, test data (Fig. 8-2) | Unshrouded single-stage impulse: ~0.95 at c/h 0.03, ~0.79 at 0.12 (k ≈ 1.75). Single-stage reaction: ~0.77 at 0.085 (k ≈ 2.7). Two-stage reaction: ~0.915 at 0.025 (k ≈ 3.4). "Losses … for the reaction turbines were about double that for the impulse turbine." Read visually | `[SP-290 Ch.8 Fig.8-2 p.227]` |
| Disk friction (Daily & Nece 1960) | Torque, **both faces**: M₀ = C_M·ρω²a⁵/2. **Power P_df = C_M·ρω³a⁵/2** (the ½ and "both sides of the disk" confirmed on the page image 2026-10-18, eq. 8-2/8-5/8-6/8-7). a = rim radius, R = ωa²ρ/μ, s = axial gap to casing. Handbook form: P_df = K_df·ρN³D_r⁵ | `[SP-290 Ch.8 eq.8-6-8-10 p.232-233]` |
| C_M, regime I (laminar, merged boundary layers) | 2π / ((s/a)·R) | `[SP-290 Ch.8 eq.8-9 p.233]` |
| C_M, regime II (laminar, separate boundary layers) | theoretical C_II/R^½ (Fig. 8-8a, read visually: C_II ≈ 2.55 at s/a 0.02 rising to ≈ 3.25 at s/a 0.28); empirical 3.70·(s/a)^0.1 / R^½ | `[SP-290 Ch.8 eq.8-11, 8-12, Fig.8-8 p.234-235]` |
| C_M, regime III (turbulent, merged) | theoretical 0.0622 / ((s/a)^¼·R^¼); empirical **0.080 / ((s/a)^(1/6)·R^¼)** | `[SP-290 Ch.8 eq.8-13, 8-14 p.235]` |
| C_M, regime IV (turbulent, separate) | theoretical C_IV/R^(1/5) (Fig. 8-8b, read visually: C_IV ≈ 0.074 at s/a 0.02 rising to ≈ 0.093 at s/a 0.28); empirical **0.102·(s/a)^0.1 / R^(1/5)** | `[SP-290 Ch.8 eq.8-15, 8-16, Fig.8-8 p.236]` |
| Which regime governs | SP-290 finds the regime by plotting C_M vs R for each s/a (Fig. 8-9) and matching slopes; regimes I/III hold at low R and small gaps, II/IV at high R. All four equations were re-read on the page images 2026-10-18 (leaves 235-238). **Derived** (my arithmetic, equating eq. 8-14 and 8-16): III → IV crossover at R* ≈ 0.0077·(s/a)^(−16/3), i.e. R* ≈ 3.6×10⁸ at s/a 0.01, 8.9×10⁶ at 0.02, 6.7×10⁴ at 0.05. So at turbopump Reynolds numbers (10⁷-5×10⁸) regime IV governs for s/a ≥ 0.02, and regime III only for very tight gaps (s/a ≈ 0.01) | `[SP-290 Ch.8 Fig.8-9 p.236]` |
| Disk friction with throughflow (coolant or leakage flow) | M/M₀ = 1 + 13.9·K₀·T/(s/a)^(1/8) (±5 %), with T = (Q/ωa³)·R^(1/5), K₀ ≈ 0.45 for s/a 0.025-0.12 | `[SP-290 Ch.8 eq.8-17-8-22 p.237-238]` |
| Partial-admission pumping loss (Stodola) | P_p = K_p·ρ·U_m³·l^1.5·D_m·(1 − ε). l = blade height, ε = active fraction of stator-exit area. **K_p = 3.63 m^-½** (0.0105 US) for an unenclosed rotor; ¼ to ½ of that when enclosed. **5.92 m^-½** (0.0171 US) back-solved from Klassen's enclosed-rotor test | `[SP-290 Ch.8 eq.8-23 p.239]` |
| Partial-admission sector loss (Stenning) | K_s = 1 − p/(3f) (p = rotor blade pitch, f = active nozzle arc length). **η_pa = η·(1 + K_w·K_s)/(1 + K_w)**, K_w = W₂/W₁ of the full-admission impulse rotor. Pumping loss comes on top | `[SP-290 Ch.8 eq.8-24-8-31 p.240-241]` |
| Incidence loss | L_i = (V₁²/2)·[1 − cos^n(i − i_opt)], n = 2 negative / 3 positive. i_opt ≈ −4 to −8° | `[SP-290 Ch.8 eq.8-35 p.245-246]` |

## Key results

1. **T-S vs T-T differ only by the last stage's leaving loss.** From the loss bookkeeping,
   1/η_TS − 1/η_TT = (V_ex²/2)/Δh′ exactly `[SP-290 Ch.3 eq.3-13/3-14 p.75; Ch.2 p.39]`.
   Equivalently η_TT ≈ η_TS / (1 − KE_ex/Δh_id). That second form is my rearrangement; it is
   approximate because Δh_id − Δh′_id equals the exit KE only to first order. SP-290 states
   the qualitative rule: total efficiency is always higher, and the gap grows with exit
   kinetic energy. For a 2-stage turbine with very low exit velocity, the measured gap was
   "only very slightly (1 or 2 percent)" `[SP-290 Ch.12 p.382]`.
2. **The H-1 62.5 % vs 70.2 % conflict (OQ) is consistent with a T-S vs T-T split.**
   - The two numbers need a leaving loss of 1/0.625 − 1/0.702 = 0.176 of actual work, i.e.
     11 % of the T-S isentropic work (my arithmetic).
   - With `[SP-8110]`'s H-1 C0 ≈ 3580 ft/s (sp8110 note, its own derivation), that is an
     exit velocity of about 0.33·C0 ≈ 1190 ft/s (360 m/s), about 0.9·U.
   - SP-290's idealized 2-stage curves at the H-1's overall speed-work parameter give a
     similar ratio. λ̄ = 2ν̄²/η ≈ 0.42 using ν̄ 0.36, or 0.56 using SP-8110's 0.42. Fig. 3-7
     then reads η̄′ ≈ 0.89 vs η̄ ≈ 0.80-0.81, a ratio of **1.10-1.11** against the H-1's
     0.702/0.625 = **1.12** `[SP-290 Ch.3 Fig.3-7 p.80]` (read visually).
   - So the two figures are plausibly the same turbine on two bases, with SP-8110 explicitly
     T-S. SP-290 cannot prove which basis SP-8107 used.
3. **Velocity ratio ↔ speed-work.** ν = √(λη/2) `[SP-290 eq.2-74 p.48]`. SP-290's overall
   parameters use the **mean** blade speed U_av `[eq.2-102/2-103 p.54]`. `[SP-8110 §2.1.3]`
   uses √ΣU² for multistage turbines. For n equal stages the two are linked as follows (my
   derivation from eq. 2-74 + 2-111, neglecting reheat):
   - (U/C0)_SP-8110 = √n·ν̄_SP-290;
   - λ_stage = n·λ̄ = 2·(U/C0)²_SP-8110 / η.

   **SP-8110's √ΣU² convention is therefore the per-stage loading basis.**
4. **Efficiency vs λ by diagram type, single stage** `[SP-290 Ch.3 Fig.3-4 p.77]`, read
   visually:
   - Total efficiency is flat at about 0.88-0.89 for λ ≳ 0.5 and falls steeply below about
     0.2: about 0.8 near λ 0.13 and about 0.6 near λ 0.05 (rough reads of a steep curve).
   - Static efficiency peaks at about 0.70-0.71 at λ = 0.5 for the impulse diagram (zero
     exit swirl there). The zero-exit-swirl diagram reaches about 0.72-0.73 at λ = 1.
   - "High total efficiencies … achievable with any of these diagram types for λ values
     greater than about 0.5."
   - At λ = 0.5, maximum total efficiency is at a stator exit angle α₁ ≈ 60° and maximum
     static at α₁ ≈ 75° (Fig. 3-5, p.78: η′ 0.865 at 60° falling to ~0.80 at 80°; η ~0.665 at
     60° rising to ~0.775 at 75°).
5. **One vs two stages** `[SP-290 Ch.3 p.80-81, Fig.3-7]`. These are printed text values,
   confirmed on the figure.
   - At λ̄ = 0.50, two stages gain **+2 points total and +9 points static** over one stage.
   - At λ̄ = 0.15, the gains are **+5 total and +24 static**.
   - The optimum 2-stage work split is 50:50 at λ̄ 0.5. It rises to **75:25 at λ̄ = 0.125**,
     where the optimum is impulse first and second stages plus an impulse second-stage stator,
     "a type of turbine known as **velocity compounded**": all expansion in the first stator,
     later rows only turn the flow.
   - Below λ̄ 0.125 the VC form is kept, with growing exit swirl.
6. **The real fleet fits this.** Mapping `[SP-8110 Table I]` points through λ = 2ν²/η (my
   arithmetic) gives:
   - F-1 (2-row VC, ν 0.20, η 0.605): λ ≈ 0.13;
   - J-2 fuel (2-row VC, 0.18, 0.601): λ ≈ 0.11;
   - J-2 ox (0.11, 0.484): λ ≈ 0.05.

   These sit right at or below SP-290's λ̄ = 0.125 velocity-compounded optimum. This is
   independent theoretical support for `[SP-8110 §3.1.4]`'s "VC below U/C0 ≈ 0.3" rule
   (`turbopump_sizing.UC0_VC_MAX`). The pressure-compounded H-1 (ν 0.36-0.42) sits at
   λ̄ ≈ 0.4-0.56, the 50:50 two-stage regime.
7. **1½-stage (downstream stator) turbines** pay a friction penalty on total efficiency. They
   gain static efficiency only below λ ≈ 0.35 `[SP-290 Ch.3 Fig.3-6 p.79]`.
8. **n-stage curves** `[SP-290 Ch.3 Fig.3-9 p.84]` (1-16 stages; **both axes logarithmic**).
   Impulse stages for λ < 0.5 and zero-exit-swirl stages above, equal stage work, constant
   blade speed (ref. 6, p.82). The limiting total efficiency is 0.88, reached when every stage
   is at λ = 1. At λ̄ ≤ 0.1, "either large increases in the number of stages are required … or
   … lower efficiencies must be expected" (p.83).

   Digitized 2026-10-18 by pixel scan of a 200 dpi render, calibrated on the axis ticks and
   corrected for a ≈ 0.9° page rotation (±0.02). Where adjacent curves merge into one line,
   the cell reads "≥" for that group.

   | λ̄ | 0.02 | 0.05 | 0.10 | 0.125 | 0.20 | 0.30 | 0.50 |
   |---|---|---|---|---|---|---|---|
   | **Static η̄**, n = 1 | < 0.10 | 0.22 | 0.38 | 0.44 | 0.58 | 0.68 | 0.77 |
   | n = 2 | 0.24 | 0.46 | 0.65 | 0.69 | 0.77 | 0.82 | ≈ 0.85 (merged) |
   | n = 3 | 0.37 | 0.60 | 0.74 | 0.77 | 0.83 | ≥ 0.86 (n ≥ 3) | |
   | n = 4 | 0.46 | 0.68 | 0.79 | 0.82 | ≥ 0.87 (n ≥ 4) | | |
   | n = 6 | 0.59 | 0.77 | 0.83 | 0.85 | | | |
   | **Total η̄′**, n = 1 | 0.25 | 0.44 | 0.61 | 0.66 | 0.74 | 0.79 | 0.84 |
   | n = 2 | 0.38 | 0.59 | 0.73 | 0.76 | 0.81 | 0.85 | ≥ 0.88 (n ≥ 2) |
   | n = 3 | 0.47 | 0.68 | 0.78 | 0.81 | ≥ 0.87 (n ≥ 3) | ≥ 0.88 | |
   | n = 4 | 0.54 | 0.73 | 0.82 | 0.84 | | | |
   | n = 6 | 0.63 | 0.78 | ≥ 0.87 (n ≥ 6) | ≥ 0.87 | | | |

   Curve identity was checked by tracing each line from the axis. The static n = 1 curve
   leaves the η̄ = 0.10 floor only at λ̄ ≈ 0.022. Further points from the same scan: static
   n = 1 ≈ 0.79 at λ̄ 0.4 and ≈ 0.81 at 0.7. All curves converge at ≈ 0.88-0.90 at λ̄ = 1.
   - **Fig. 3-9's n = 1 curve is not Fig. 3-4's single stage.** At λ 0.5, Fig. 3-4 (ref. 2,
     axial-inlet stage) gives total ≈ 0.88 / static ≈ 0.70. Fig. 3-9 (ref. 6, built from
     "general stage" efficiencies through eq. 3-18/3-19) gives ≈ 0.84 / 0.77. Use Fig. 3-9
     for the **ratio between stage counts at fixed λ̄**, not for absolute single-stage values.
   - Comparison (my arithmetic): at the F-1's λ̄ ≈ 0.13 (key result 6), the idealized
     pressure-compounded 2-stage static value is ≈ 0.69. The real 2-row VC F-1 turbine gives
     0.605 `[SP-8110 Table I]`, about 0.09 lower.
9. **Stage-count rules**: n = λ_stage/λ̄ and n = (N_s/N̄_s)^(4/3) `[SP-290 eq.2-109, 2-111
   p.56-57]`. Choose blade speed U from stress, compute λ̄ = U²/Δh′, then pick a target stage
   λ (≈ 0.5 for an impulse stage at its static optimum) and divide. Example (my arithmetic):
   the F-1's λ̄ 0.13 would need about 4 impulse stages at λ 0.5. Rocketdyne instead accepted
   a 2-row VC wheel at ~60 %, which is SP-290's 2-stage VC optimum at λ̄ 0.125.
10. **Reynolds correction**: (1 − η′₁)/(1 − η′₂) = 0.3-0.4 + 0.7-0.6·(Re₂/Re₁)^0.2
    `[SP-290 eq.2-142 p.62]`. A 10× Reynolds drop raises the loss by a factor 0.35 + 0.65·10^0.2
    ≈ 1.38 (my arithmetic). Boundary-layer analysis gives the same direction on height
    Reynolds number `[SP-290 Ch.7 Fig.7-12 p.221]`.
11. **Stator loss split** (one NASA cold-air stator, Ch. 7 Fig. 7-9): friction ≈ ½ of the
    total stator loss (≈ 2 % of stator ideal energy), trailing edge ≈ ¼, end wall ≈ 15 %,
    mixing ≈ 10 %. The loss coefficient falls slightly with rising velocity `[SP-290 Ch.7
    p.218]`. This is a single design and is labelled as such. Figures read visually
    2026-10-18 (±0.001 on the coefficient):
    - Fig. 7-9 (kinetic-energy loss coefficient e vs mean-section ideal after-mix critical
      velocity ratio 0.5 → 0.85): total ē₂,3D ≈ 0.042 → 0.034; ē₁,3D (before mixing)
      ≈ 0.038 → 0.031; mean-section friction + trailing edge ē₁,m ≈ 0.031 → 0.026;
      mean-section surface friction ē₁a,m ≈ 0.021 → 0.019 `[SP-290 Ch.7 Fig.7-9 p.218]`.
    - Fig. 7-8 (same kind of stator, ref. 8, stator area setting 70-130 %): ē₂,3D ≈ 0.033 →
      0.031; ē₁,m ≈ 0.025 → 0.023; ē₁a,m ≈ 0.017 → 0.019. Experiment and analysis agree
      within ≈ 0.002 `[SP-290 Ch.7 Fig.7-8 p.217]`.
    - Geometry optima (ref. 10, turbulent boundary layer; momentum-thickness ratio θ/θ_min):
      off-optimum height/spacing costs ≈ +30 % at (h/s)/(h/s)_opt = 0.2 but only ≈ +7 % at
      2.6 (Fig. 7-10); off-optimum solidity costs ≈ +35 % at 0.45 and ≈ +33 % at 1.6 of
      optimum, ≈ +5-8 % at 0.8 or 1.2 (Fig. 7-11); height Reynolds number gives θ ∝ Re_h^(−1/5)
      (text: "m = 1/5"), ≈ 0.88 at 2× Re_h `[SP-290 Ch.7 Fig.7-10-7-12 p.220-221]`.
      Stator-row figures only; the qualitative rule is "a too-low solidity is about as bad as
      a too-high one, and short blades (low h/s) are penalized hard".
12. **Tip clearance roughly doubles from impulse to reaction blading** `[SP-290 Ch.8 Fig.8-2,
    8-3 p.227-228]`.
    - Mitigation options are a recessed casing and a tip shroud. In one impulse turbine the
      shroud stopped helping below c/h ≈ 0.035, because of shroud/casing friction `[p.230]`.
    - The clearance gap scales with diameter, so the loss is worse for small turbines and
      for high hub/tip ratio `[p.230-231]`. This is the physical mechanism behind a
      size/pitchline penalty like `turbopump_efficiency`'s `pitchline_factor`.
13. **Disk friction is the Daily-Nece four-regime correlation**, with explicit C_M equations
    `[SP-290 Ch.8 p.231-238]`. "For a given blade speed, lower loss is obtained by having a
    smaller diameter and a higher rotative speed" `[p.233]`. Throughflow raises torque
    linearly in the throughflow number (eq. 8-22). Against these relations,
    `pump_meanline.DISK_CM_COEFF` runs **≈ 1.5-1.8× high** (verified; see Design method).
14. **Partial admission** `[SP-290 Ch.8 p.238-243]`.
    - It is chosen when full admission would give very short blades. Its losses can be
      smaller than the leakage and low-Re losses of the short-bladed full-admission design,
      and it permits a larger diameter and a higher ν at fixed rpm.
    - Klassen's test (Fig. 8-11, read visually): pumping + disk friction ≈ 0.10 of ideal
      work at ε ≈ 0.12, falling to ≈ 0.03-0.04 at ε ≈ 0.5. "Other" losses (sector + leakage)
      stay nearly constant at ≈ 0.04-0.05.
    - Stenning's predictions (Fig. 8-12, read visually, ±0.02/±0.03):
      - full admission peaks at η ≈ 0.69, ν ≈ 0.47;
      - nozzle arc/blade pitch f/p = 10: ≈ 0.64 at ν ≈ 0.43;
      - f/p = 2: ≈ 0.45 at ν ≈ 0.35;
      - f/p = 1: ≈ 0.32 at ν ≈ 0.26.
    - **The optimum ν falls as the admission arc shrinks**, because pumping and disk
      friction, which scale with U³, become a larger share `[p.242-243]`.
15. **Supersonic partial-admission turbine test data** `[SP-290 Ch.9 Fig.9-20 p.274-275]`.
    The turbine is Goldman's low-Reynolds-number, partial-admission, single-stage supersonic
    turbine (ch. 9 ref. 14, NASA TM X-2382, 1971), design PR **63** (inlet total to exit
    static). The figure plots static (T-S) efficiency (axis 0-0.40) against blade-jet speed
    ratio ν (0-0.24), with one branch per speed (20-100 % of design) and pressure ratios
    20-150 on each branch.
    - Digitized 2026-10-18 (pixel scan of a 200 dpi render, ±0.01). The **design line is at
      ν ≈ 0.216**. The 100 %-speed, PR-63 point is the peak, **η_TS ≈ 0.38-0.39 at
      ν ≈ 0.22**.
    - The envelope through the design-PR points (circles) is: η ≈ 0.09 at ν 0.04, 0.18 at
      0.08, 0.27 at 0.12, 0.34 at 0.16, 0.38 at 0.20. It is still rising at the design ν, so
      the turbine runs below its optimum ν. This is the stress- and speed-limited condition
      typical of rocket turbines.
    - "For any given speed, efficiency is maximum at about design pressure ratio and falls
      off rapidly as pressure ratio is decreased" (p.274). Read visually: at 90 % speed,
      dropping PR from 63 to 20 takes η from ≈ 0.375 to ≈ 0.275, while ν rises
      (≈ 0.197 → 0.216). At 60 % speed it goes from ≈ 0.30 to ≈ 0.22. PR 120-150 points sit
      on or just below the design-PR point.
    - The cause is shocks in the under-expanded stator nozzles (Fig. 9-21). A subsonic
      turbine's low-PR points would instead have fallen on the envelope (p.274).
    - This is the regime of small high-PR rocket GG/APU turbines. The 0.38-0.39 peak sits
      right beside `[SP-8110]`/`[SP-8107]`'s Agena LR81 (41 %) and A-7 (37 %) small-turbine
      values. So a **low-Re, partial-admission, supersonic single stage at PR ≈ 60 and
      ν ≈ 0.2 tops out near 0.4 T-S**, which is real test data, not an idealized curve.
16. **A real 2-stage axial turbine follows the idealized parabola** `[SP-290 Ch.12 Fig.12-21
    p.381-382]`. A 2-stage axial-flow test turbine, static efficiency vs ν, speeds 30-120 % of
    design.
    - Read by pixel scan 2026-10-18 (±0.02; markers scatter about ±0.02). Design ν ≈ 0.46.
      Peak **η_TS ≈ 0.82-0.83 at ν ≈ 0.45-0.50**.
    - Other points: ≈ 0.36-0.39 at ν 0.10, 0.58 at 0.20, 0.73 at 0.30, 0.78 at 0.35,
      0.80 at 0.60, 0.72 at 0.70, 0.65-0.66 at 0.75. All speed lines collapse onto one curve.
    - Normalized against the peak, these follow the ideal-impulse shape η/η_max = 2x − x²
      with x = ν/ν_opt (from eq. 2-88; my arithmetic): x 0.67 → 0.89 (curve 0.88); x 0.44 →
      0.69 (curve 0.70); x 0.22 → 0.39 (curve ≈ 0.44).
    - The text says total efficiency was only 1-2 % above static because of the two stages
      and low exit velocity (p.382). It also warns that the correlation is "not always as
      good": speed lines separate near limiting loading, especially at low ν.
17. **Radial-inflow turbines (Ch. 10, ref. 7 computed study; not used by the tool)**
    `[SP-290 Ch.10 Fig.10-7-10-11 p.286-289]`, read visually (±0.02-0.03).
    - Specific speed here is dimensionless N_s; 1.0 ≈ 129 in US units
      (ft^¾·lbm^¾/(min·s^½·lbf^¾)).
    - Fig. 10-7: the maximum-static-efficiency envelope peaks at **≈ 0.86-0.87 near N_s ≈
      0.55-0.7**, falling to ≈ 0.6 at N_s 0.25 and at 1.2. The corresponding total
      efficiency peaks at ≈ 0.91 near N_s 1.0. At fixed N_s the static efficiency spreads by
      "as much as 45 to 50 points" across geometries, and stator-exit angle is the prime
      determinant.
    - Optimum stator-exit angle (Fig. 10-8): 83° at N_s 0.2 → ≈ 72° at 0.8 → ≈ 52° at 1.35.
    - Optimum h₁/D₁ (Fig. 10-9): rises with N_s to ≈ 0.19 (U/V_cr 0.20), 0.16 (0.49) or 0.12
      (0.80) near N_s 1.0-1.2. Higher velocity level gives smaller h/D.
    - Optimum D_t2/D₁ (Fig. 10-10): 0.2 at N_s 0.15, linear to the 0.7 cap at N_s 0.6.
    - **Optimum ν (Fig. 10-11): ≈ 0.70 over N_s 0.3-0.8**, ≈ 0.62 at 0.13 and ≈ 0.55 at
      1.35. That is well above the axial impulse optimum of ≈ 0.47.
    - The text cautions that the computed values "do not necessarily represent achievable
      values" (p.287).
18. **Reheat effect**: multistage overall efficiency exceeds stage efficiency, so a
    higher-PR turbine "is helped by the reheat effect" `[SP-290 Ch.2 p.41-42]`. Polytropic
    efficiency removes it (eq. 2-62, Fig. 2-10). The two differ significantly at high PR and
    low efficiency, which is the rocket-GG-turbine regime (PR 15-30). For example (derived
    from eq. 2-62, γ 1.4): η_p 0.60 gives η̄ 0.70 at PR 20, a reheat credit of +0.10.

## Design method — what it gives `engine_designer`

Reference only; no code changes are proposed here.

- **Efficiency basis.** The tool's turbine power uses a total-inlet/static-exit PR, so T-S is
  the consistent basis (OQ H-1 entry). SP-290 eq. 3-13/3-14 supplies the conversion:
  η_TS = η_TT·Δh′/(Δh′ + V_ex²/2). A T-T anchor (if SP-8107 Table III is T-T) should be
  converted, not mixed. Item 2 above shows the H-1 pair is self-consistent with a leaving
  loss of ≈ 11 % of the isentropic work. That supports dropping `ETA_TURBINE_CEILING
  ["pressure_compounded_2stage"]` (0.76, fitted to 70.2 %) toward the T-S basis. It does not
  pin the new value.
- **A U/C0 curve, which `turbopump_efficiency` currently lacks** (AS ~154-155). SP-290 gives
  the functional form and the optimum locations, not real-rocket magnitudes:
  - single-row impulse: parabolic η = 4ν sin α₁ − 4ν², optimum ν = sin α₁/2 ≈ 0.47;
  - real-machine shape from Fig. 3-4 / Fig. 8-12 (full-admission peak ≈ 0.69 static at
    ν ≈ 0.47);
  - 2-stage / VC behaviour from Fig. 3-7 and the λ̄ = 0.125 VC optimum, and the n-stage ratios
    from Fig. 3-9 (key result 8);
  - **real-turbine confirmation of the normalized shape**: η/η_max ≈ 2x − x², x = ν/ν_opt,
    which the 2-stage test turbine follows within ≈ 0.01-0.05 (key result 16);
  - a real low-Re, partial-admission, supersonic small-turbine level of ≈ 0.38-0.39 T-S at
    ν ≈ 0.22 and PR 63, plus the off-design-PR drop (key result 15).

  A curve built this way would still need its magnitude fitted to `[SP-8110 Table I]` /
  Fig. 14 fleet points (which SP-8110's own Fig. 13 already shapes). SP-290's main
  contribution is the λ ↔ ν mapping and the T-S/T-T bookkeeping that make the fit
  consistent.
- **Staging** (AS ~169). `open_cycle_turbine_staging`'s VC/PC bands agree with SP-290's
  optimum-diagram analysis (key result 6). SP-290 adds the stage-count formula n = λ_stage/λ̄
  for a future n-stage option. It says nothing about the turbine-wheel-to-pump-impeller
  diameter ratio, so **`TURBINE_DMEAN_OVER_PUMP_D` 1.9 stays Tier 3**. The only related
  statements are the disk-friction scaling (smaller D and higher N is better) and the
  clearance-scales-with-diameter rule.
- **Partial admission** (`ADMISSION_FLOOR`). There is now a physical model to replace the
  fitted power-based floor if wanted:
  - sector loss, eq. 8-31, from the arc/pitch ratio;
  - pumping loss, eq. 8-23, with K_p 3.63 m^-½ (unenclosed) / ¼-½ of that (enclosed) /
    5.92 (one enclosed test);
  - plus the shift of the optimum ν downward as ε falls (Fig. 8-12).
- **Disk friction** (OQ 318-320). The SP-290 Daily-Nece equations are the citation
  `pump_meanline.DISK_CM_COEFF` lacked. **Discrepancy VERIFIED 2026-10-18.** The four
  regimes and the ½ were re-read on the page images (leaves 234-238). The tool code was read
  only around the constant (no change made).
  - **What the tool does.** `pump_meanline.py` line 79 sets `DISK_CM_COEFF = 0.0622`,
    commented "C_M = 0.0622 Re^-0.2 (both faces), Daily-Nece-type turbulent enclosed disk -
    Tier 3, no coefficient in the reference set". Line 410 computes
    `p_df = DISK_CM_COEFF * re_d**-0.2 * rho * omega**3 * r2**5`, with
    `re_d = omega*r2*r2/nu_kin` = SP-290's R (eq. 8-10) and r2 = the impeller tip radius.
    This P_df is added to the hydraulic power of the PUMP stage before η_m.
  - **What SP-290 gives.** P_df = M₀ω = **C_M·ρω³a⁵/2**, with M₀ the torque on **both**
    faces (eq. 8-2, 8-5-8-7; the ½ and "both sides of a disk" are printed on p.232). In
    regime IV (turbulent, separate boundary layers, eq. 8-16), C_M = 0.102·(s/a)^0.1·R^(−1/5).
    The power coefficient on the tool's R^−0.2 basis is therefore **0.051·(s/a)^0.1**.
  - **Ratio** (derived): tool / SP-290 regime IV = 0.0622 / (0.051·(s/a)^0.1)
    = 1.22·(s/a)^(−0.1). This is independent of R, because both use R^−0.2:

    | s/a | 0.01 | 0.02 | 0.05 | 0.10 | 0.20 |
    |---|---|---|---|---|---|
    | SP-290 IV coefficient 0.051(s/a)^0.1 | 0.0322 | 0.0345 | 0.0378 | 0.0405 | 0.0434 |
    | tool / SP-290 IV | 1.93 | **1.80** | **1.65** | **1.54** | 1.43 |

  - **Representative conditions** (my property values, not from SP-290). Each gives
    R = ωa²/ν:
    - RP-1 impeller, r2 0.20 m, 5,500 rpm, ν 2×10⁻⁶ m²/s: R ≈ 1.2×10⁷.
    - LOX impeller, r2 0.25 m, 5,500 rpm, ν 1.7×10⁻⁷: R ≈ 2.2×10⁸.
    - LH2 impeller, r2 0.15 m, 35,000 rpm, ν 1.9×10⁻⁷: R ≈ 4.4×10⁸.
    - F-1-class GG turbine disk, a 0.4 m, 5,500 rpm, gas at ρ ≈ 16 kg/m³ and μ ≈ 3×10⁻⁵ Pa·s:
      R ≈ 4.9×10⁷.

    All four are fully turbulent. With the III → IV crossover in the parameter table,
    **regime IV governs for any s/a ≥ 0.02**, so the ratio row above applies directly:
    **≈ 1.5-1.8× high for s/a 0.02-0.10** (≈ 1.4× at a wide 0.2 gap).
  - **Tight gaps.** For s/a ≈ 0.01, regime III governs below R ≈ 3.6×10⁸. Against the
    empirical eq. 8-14 (C_M/2 = 0.040·(s/a)^(−1/6)·R^(−1/4)), the tool is 1.62× high at
    R 10⁷ and 1.81× at 10⁸ (derived).
  - **Root cause.** 0.0622 is regime III's *theoretical* numerator (eq. 8-13, which goes
    with (s/a)^(−¼)·R^(−¼)). It was paired with regime IV's R^(−1/5) exponent, and the ½ of
    eq. 8-7 was dropped. With the ½ restored (0.0311), the tool would sit at **0.72-0.97×**
    SP-290 regime IV over s/a 0.2-0.01. So the dropped ½ accounts for nearly all of the
    excess.
  - **Does a turbine-disk relation apply to a pump impeller?** Yes, for the base
    no-throughflow case, arguably better than for a turbine disk. Daily-Nece is a
    fluid-agnostic smooth enclosed disk in a housing, Reynolds-scaled, and it was verified
    with a 20-in disk in **water and oil** (p.237). That is the pump's liquid regime, not
    hot gas. SP-290 does not cover four pump-specific features:
    1. the curved shroud/hub contour (not a flat disk);
    2. wall roughness (smooth disks only);
    3. an open (unshrouded) impeller's bladed front face;
    4. wear-ring leakage. The throughflow correction (eq. 8-17-8-22, M/M₀ = 1 + 13.9·K₀·T/
       (s/a)^(1/8), K₀ ≈ 0.45) assumes fluid entering near the centreline with **no swirl**
       and flowing **outward** (turbine coolant). A pump's front-shroud leakage flows
       **inward** from the swirling rim. Eq. 8-22 therefore cannot be borrowed to justify
       the 1.5-1.8× excess.
  - **Recommendation (for the main session, Tier 3 → cited):** replace the constant with
    SP-290 eq. 8-16 as written, P_df = 0.051·(s/a)^0.1·R^(−0.2)·ρω³a⁵. That needs an s/a
    assumption (e.g. 0.02-0.05 gives 0.035-0.038), or a regime-III/IV max for tight gaps.
    Alternatively keep 0.0622 and label it an explicit ≈ 1.5-1.8× roughness/leakage
    allowance with no SP-290 backing. Either way the disk-friction loss falls by about 35-45 %
    for a cited value. Because K_HYD was fitted with the current disk term in place, a refit
    would follow.

## Section map

- Front matter: preface p.iii (leaf 3), contents p.v-vi (leaf 4-5). Read.
- **Ch. 1** Thermodynamic and Fluid-Dynamic Concepts (Glassman): p.1-20 (leaf 6-25).
  **as-needed - not read (2026-10-18)** — equation of state, 1-D compressible-flow relations
  for varying area, critical velocity.
- **Ch. 2** Basic Turbine Concepts (Glassman): p.21-67 (leaf 26-72).
  - Turbine flow and energy transfer p.21-36 (leaf 26-41): Euler work equation, velocity
    diagrams, reaction definition, blade-row efficiency. **as-needed - not read
    (2026-10-18)**.
  - **Blade-row / turbine / stage efficiencies, T-S vs T-T, reheat, polytropic efficiency
    (Fig. 2-8 to 2-10, eq. 2-42 to 2-62): p.37-44 (leaf 42-49). Read; eq. 2-48/2-49, 2-52
    and 2-62 and Fig. 2-10 read visually** (2-52/2-62 confirmed on the page images
    2026-10-18; the OCR text garbles both).
  - **Dimensionless parameters, velocity-diagram parameters (λ, ψ, ν, φ), idealized
    η-vs-ν (Fig. 2-12), N_s/D_s, overall parameters, stage-count estimates, Fig. 2-13,
    equivalent conditions, Reynolds-number effect: p.45-62 (leaf 50-67). Read; eq. 2-67 to
    2-74, 2-94 to 2-103, 2-107 to 2-110 and 2-142 read visually.** Fig. 2-13 (p.55, leaf
    60) was read visually 2026-10-18. It is sketches only: blade/passage shape of 2-stage
    axial, 1-stage axial and radial turbines at N_s ≈ 0.25-1.1 (dimensionless; 1.0 ≈ 129 US
    units). Blades get taller (lower hub/tip ratio) with N_s. No efficiencies; not relevant
    beyond that.
  - Symbols p.63-67. Partly read.
- **Ch. 3** Velocity Diagrams (Whitney & Stewart): p.69-99 (leaf 73-103).
  - **Mean-section diagrams: diagram types (zero exit swirl / impulse / symmetrical, Fig.
    3-1 to 3-3), stage efficiency (eq. 3-12 to 3-15, Fig. 3-4, 3-5), 1½-stage (Fig. 3-6),
    2-stage including velocity-compounded and counter-rotating (Fig. 3-7, 3-8), n-stage
    (eq. 3-16 to 3-19, Fig. 3-9): p.69-84 (leaf 73-88). Read; Fig. 3-4 to 3-7 and eq. 3-17
    to 3-19 read visually; Fig. 3-9 digitized by pixel scan 2026-10-18 (key result 8).**
  - Radial variation of diagrams (free vortex etc.) p.84-95 (leaf 88-99) and computer
    programs p.95-96. **as-needed - not read (2026-10-18)**.
- **Ch. 4** Blade Design (Stewart & Glassman): p.101-125 (leaf 104-128). **as-needed - not
  read (2026-10-18)** — solidity (Zweifel loading coefficient) and blade-profile design. It
  overlaps `[SP-8110]` §2.3/§3.3.
- **Ch. 5** Channel Flow Analysis (Katsanis): p.127-155 (leaf 129-157). **as-needed - not
  read (2026-10-18)** — stream-function, potential-function and velocity-gradient blade-
  passage analyses.
- **Ch. 6** Introduction to Boundary-Layer Theory (McNally): p.157-191 (leaf 159-193).
  **as-needed - not read (2026-10-18)** — boundary-layer equations and solutions.
- **Ch. 7** Boundary-Layer Losses (Prust): p.193-223 (leaf 195-225).
  - Boundary-layer parameters and blade-row loss coefficients p.195-216 (leaf 197-218):
    momentum/energy thickness → kinetic-energy loss coefficients, trailing-edge and mixing
    losses, 2-D → 3-D end-wall conversion. **as-needed - not read (2026-10-18)**.
  - **Blade-row loss characteristics (loss breakdown Fig. 7-8, 7-9; geometry optima Fig.
    7-10 to 7-12, h/s, solidity, height Reynolds number): p.217-221 (leaf 219-223). Read;
    Fig. 7-8 to 7-12 read visually 2026-10-18 (key result 11).**
- **Ch. 8** Miscellaneous Losses (Roelke): **p.225-248 (leaf 227-250). Read in full.** Covers
  tip clearance (Fig. 8-1 to 8-5), disk friction (Daily-Nece regimes I-IV, throughflow, eq.
  8-1 to 8-22, Fig. 8-6 to 8-10), partial admission (pumping eq. 8-23, sector loss eq.
  8-24 to 8-31, Fig. 8-11, 8-12) and incidence (eq. 8-32 to 8-35, Fig. 8-13 to 8-16). All
  equations and Fig. 8-2, 8-3, 8-5, 8-8 to 8-12 were read visually. Disk-friction eq. 8-1
  to 8-22 and Fig. 8-8 to 8-10 were re-read on the page images 2026-10-18 (leaves 234-240)
  for the `DISK_CM_COEFF` check.
- **Ch. 9** Supersonic Turbines (Goldman): p.249-278 (leaf 251-280).
  - Method of characteristics and supersonic stator/rotor blade design, including rotor
    starting limits (Fig. 9-18, 9-19), p.249-274 (leaf 251-276): **as-needed - not read
    (2026-10-18)**.
  - **Supersonic turbine performance (Fig. 9-20 η vs ν for the PR-63 partial-admission
    turbine of TM X-2382) and references p.274-277 (leaf 276-279): read; Fig. 9-20
    digitized by pixel scan 2026-10-18 (key result 15).** Fig. 9-21 (stator-nozzle static
    pressure vs axial distance, p.276) was skimmed from the text layer only. It shows the
    under-expanded-nozzle shocks qualitatively, with no efficiency content.
- **Ch. 10** Radial-Inflow Turbines (Rohlik): p.279-306 (leaf 281-308). **Intro p.279-280
  and the specific-speed study p.286-289 (leaf 288-291): read; Fig. 10-7 to 10-11 read
  visually 2026-10-18 (key result 17).** Fig. 10-7 (computed static/total η vs N_s) is the
  only η-vs-N_s chart in the book; Fig. 10-8 to 10-11 give the optimum α₁, h/D, D-ratio and
  ν vs N_s. The rest is **as-needed - not read (2026-10-18)**. Radial turbines are not used
  in the tool.
- **Ch. 11** Turbine Cooling (Colladay): p.307-349 (leaf 309-351). **as-needed - not read
  (2026-10-18)** — gas-to-blade heat transfer, convection/film/transpiration blade cooling.
  Possibly useful for turbine-blade life (Round B of the burn-time work).
- **Ch. 12** Experimental Determination of Aerodynamic Performance (Szanca & Schum):
  p.351-390 (leaf 352-390). **Performance-map and equivalent-condition definitions
  p.374-375 and the ν correlation (eq. 12-14, Fig. 12-21) p.381-382: read; Fig. 12-21
  digitized by pixel scan 2026-10-18 (key result 16).** Test facilities and
  instrumentation are **as-needed - not read (2026-10-18)**.
- Report documentation page: leaf 391.

## Caveats

- **Idealized curves.** Fig. 2-12, 3-4 to 3-9 come from constant-loss-coefficient analyses
  (Lewis references, air-breathing scale) with a 0.88-0.90 total plateau. Real rocket GG
  turbines run 40-79 % T-S `[SP-8110 Table I]`. Use them for shape, optimum ν/λ and
  ratios (T-T/T-S, 2-stage vs 1-stage gains) only.
- **Blade-speed convention differs from SP-8110.** SP-290 uses U_av for overall parameters;
  SP-8110 uses √ΣU² for multistage. Convert before comparing (key result 3).
- Figure accuracy. Values marked "read visually" come from ~100-130 dpi renders: ±0.01-0.02
  on efficiency and ±0.02-0.03 on ν/λ. Fig. 3-9, 9-20 and 12-21 were digitized 2026-10-18 by
  pixel scan of 200 dpi renders, calibrated on the printed ticks. Fig. 3-9 has log-log axes
  and a ≈ 0.9° page rotation, which was corrected; curve identities were traced from the
  axis. Accuracy is ±0.01-0.02, and where adjacent curves merge only a "≥" bound is given.
  Every figure the note cites has now been viewed. Fig. 9-21, 10-12 and the Ch. 4-6/11
  figures were not, and are not cited.
- **Two idealized analyses disagree on the single stage.** At λ 0.5, Fig. 3-4 (ref. 2)
  gives T-T 0.88 / T-S 0.70, while Fig. 3-9's n = 1 curve (ref. 6) gives 0.84 / 0.77. Use
  each figure only for its own ratios (diagram type, stage count). Do not splice their
  absolute levels.
- Fig. 9-20 is **one** low-Re, partial-admission test turbine; Fig. 12-21 is
  **one** NASA 2-stage subsonic test turbine. They are real data but single machines.
- The `DISK_CM_COEFF` comparison (Design method) uses representative R and s/a values that
  I assumed. The ratio itself (1.22·(s/a)^−0.1 in regime IV) does not depend on R.
- The H-1 T-S/T-T reconciliation (key result 2) is a **consistency argument, not proof**.
  The required ≈ 360 m/s exit velocity (≈ 0.9·U) is high for a pressure-compounded stage.
  A different rating point remains possible.
- Partial-admission pumping exponents and coefficients are "quite uncertain". SP-290 says "a
  generally applicable expression for pumping-power loss is yet to be found" `[p.239]`, and
  the complete partial-admission optimization "cannot be done analytically at present"
  `[p.241]`. K_p ranges 0.9-5.9 m^-½ across sources.
- The tip-clearance correlation (Fig. 8-3, Boeing D4-3220) is valid for "small tip
  clearances" (≤ 0.03 of passage height plotted). Fig. 8-2's larger clearances are single
  NASA test turbines.
- The Daily-Nece regimes were validated with a 20-in disk in water and oil `[p.237]`. The
  hot-gas rocket turbine disk application is an extrapolation in fluid, not in Reynolds
  number.
- 1972-75 content, pre-SSME. No staged-combustion reaction-turbine data.
- Cross-links: `[SP-8110]` (rocket-turbine criteria, fleet Table I, Emmert VC loss
  procedure, η vs U/C0 Fig. 13/14); `[SP-8107]` Table III (efficiency per engine, basis
  ambiguous); `topics/09-turbopumps.md` (turbine staging and efficiency sections).
