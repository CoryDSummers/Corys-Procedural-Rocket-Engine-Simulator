# 01 — Nozzle flow and performance

## Scope

How thrust, specific impulse, characteristic velocity and thrust coefficient relate; the
ideal 1-D isentropic model and the real-nozzle losses layered on top of it; altitude
effects and flow separation. This is the layer `engine_designer/physics/isentropic.py`
implements exactly; the value here is the loss breakdown and the typical correction-factor
magnitudes.

## Key relations

**Thrust** `[Huzel §1.1 eq. 1-6 p.2]`, `[Sutton §2.2]`:

    F = (ṁ/g)·ve + Ae·(Pe − Pa)          [US customary form; SI drops the /g]
      = ṁ·c                               where c = effective exhaust velocity
    c = ve + Ae·(Pe − Pa)/ṁ               (c = ve only when Pe = Pa)

`ṁ·ve/g` is *momentum thrust*, `Ae·(Pe−Pa)` is *pressure thrust*. The nozzle's job is to
convert chamber pressure into gas momentum so the pressure-thrust term is small.

**Specific impulse**: `Is = F/(ṁ·g) = c/g` (s). `Is,tc = c*·Cf/g` `[Huzel eq. 1-31c]`.

**Characteristic velocity** `[Huzel eq. 1-32a p.83]`, `[Sutton §3.6]`:

    c* = √( g·γ·R·Tc / M ) / Γ            Γ = γ·√( (2/(γ+1))^((γ+1)/(γ−1)) )  (Vandenkerckhove)
       = Pc·At / ṁ                         (operational definition)

c* depends almost entirely on chamber temperature once the propellant/MR fixes γ and M
`[Huzel §4.2]`. It **peaks at a combustion temperature somewhat below the maximum** —
i.e. slightly below the stoichiometric MR — because M rises with Tc.

**Thrust coefficient** `[Sutton §3.3–3.6]`:

    Cf = f(γ, Pe/Pc, ε) + (Pe − Pa)/Pc · ε
    Cf,vac  = momentum term + ε·Pe/Pc
    Cf(Pa)  = Cf,vac − ε·Pa/Pc

`Is = c*·Cf/g`. c* carries combustion quality; Cf carries nozzle/expansion quality.

**8 ideal-flow assumptions** `[Huzel §1.2 p.3]`: homogeneous gas, perfect gas, adiabatic
(and, if reversible, isentropic), frictionless, steady flow, 1-D flow, uniform velocity
across each normal section, chemical equilibrium established in the chamber and **frozen**
(not shifting) in the nozzle. Real design applies empirical correction factors to results
from these assumptions.

## Empirical correlations & typical values

**Real-nozzle loss budget** — experimental Is is generally **3–12 % below ideal**
`[Sutton §5.5 p.180]`; of that, **only ~1–4 % is combustion inefficiency**, the rest is
nozzle losses. Loss mechanisms `[Sutton §3.5]`: divergence (non-axial exit velocity),
boundary-layer/friction, chemical-kinetics (finite recombination rate), two-phase flow
(condensed species), flow nonuniformity, nozzle misalignment/side loads.

**c\* correction factor** (good chamber + injector, frozen composition) `[Huzel §4.2 p.85]`:
~**0.975** for both LOX/RP-1 and LOX/LH2. (The tool's per-pair `DEFAULT_ETA_CSTAR` of
0.94–0.955 is this same quantity, calibrated against real engines.)

**Overall Cf correction factor** (effective contour) `[Huzel §4.2 p.86]`: **0.98** for
LOX/RP-1 at sea level; **1.01** for LOX/LH2 in vacuum. (A number >1 reflects that the
theoretical Cf used as the baseline omitted some real gains.)

**Conical divergence factor** `[Huzel eq. 4-8 p.90]`: `λ = ½·(1 + cos α)`. For α = 15°,
λ = 0.983 → a 15° cone gives 98.3 % of the ideal exit momentum / vacuum Cf. See topic 02.

**Flow separation** (sea-level over-expansion): the Summerfield criterion — separation when
`Pe/Pa` drops below roughly **0.35–0.4** for kerolox/hydrolox `[Sutton §3.5]`,
`[isentropic.py comment]`. Below that the jet detaches from the wall inside the nozzle and
the simple `Ae·(Pe−Pa)` penalty no longer applies (shock structure, side loads).

**Nozzle area ratios** in service: up to ~285 (RL10B-2), ~400 developed `[Sutton §8.2]`.
Very large ε buys little Is and costs length/mass; extendible nozzle cones mitigate this.

## Worked numbers

`[Huzel Sample 4-1 p.85]`, A-1 stage, LOX/RP-1, MR 2.35, Pc 1000 psia, ε 14:
- from combustion chart: Tc = 6000 °F (6460 °R), M = 22.5, γ = 1.222
- theoretical c* = √(32.2·1.222·6460·1544/22.5) / 0.7215 = **5810 ft/s**
- design c* = 5810 × 0.975 = **5660 ft/s**
- theoretical vacuum Cf (γ 1.222, ε 14) = 1.768 → SL = 1.768 − 14·14.7/1000 = 1.562
- design SL Cf = 1.562 × 0.98 = **1.531**
- design SL Is = 5660 × 1.531 / 32.2 = **270 s**

A-2 stage, LOX/LH2, MR 5.22, Pc 800 psia, ε 40: theoretical c* 7670 → design 7480 ft/s;
vacuum Cf 1.876 × 1.01 = 1.895; **design vacuum Is = 440 s** `[Huzel Sample 4-1 p.86]`.

`[Sutton Table 5-4 p.181]`, LOX/LH2, Pc 773.3 psia, MR 5.551, shifting equilibrium:
c* = 2332.1 m/s (7651 ft/s); chamber T 3389 K, M 12.7, k 1.14; throat T 3184 K.

## Caveats

- c\* correction factors and Is losses are quoted for "good" designs and frozen composition;
  shifting-equilibrium calculations give a few percent higher ideal Is (topic 03).
- Huzel's charts are frozen-composition at specific Pc values; interpolating to other Pc
  introduces small errors (Pc dependence of Tc/γ/M is real but weak).
- The separation constant (0.35–0.4) is a band, not a sharp value; real onset depends on
  wall contour and boundary-layer state.

## Implications for engine_designer

- `isentropic.py` already implements `vandenkerckhove`, `cf_vacuum`, `cf_at_ambient`,
  `c_star`, `nozzle_divergence_efficiency`, `is_separated` — all exact textbook forms with
  the right constants (`R_UNIVERSAL = 8314.46`, `G0 = 9.80665`). No change indicated; this
  file is the citation backing (`[Sutton §3.3–3.6]`, `[Huzel §1.1–1.3]`).
- `SEPARATION_K = 0.4` (`design.py`, Tier 3) sits at the top of the cited 0.35–0.4 band
  `[Sutton §3.5]` — defensible; a value of 0.35 would be equally citable and slightly more
  conservative (predicts separation sooner).
- The `[Sutton §5.5]` split — "experimental Is is 3–12 % below ideal, of which only ~1–4 %
  is combustion" — is the physical justification for keeping `DEFAULT_ETA_CSTAR` in the
  0.94–0.99 range and scoring nozzle divergence *separately* (which the tool does, relative
  to an 80 %-bell reference — see topic 02). It confirms the LMDE double-counting fix was
  the right call.
- `ETA_CSTAR_CEILING = 0.99` (`design.py`) is consistent with "~1 % combustion loss" being
  the practical floor `[Sutton §5.5]`.
