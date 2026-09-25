# 16 — Gimbal and thrust-vector control

## Scope

Thrust-vector control mechanisms, typical deflection ranges, the side-force / moment
relation, actuator loads and rates, and thrust-vector alignment. Feeds
`engine_designer/physics/gimbal.py`. Mostly from `[Sutton Ch. 16]`, with `[Huzel §7.5,
§9.6]`.

## Key relations

**Pitch / yaw moment from a deflected nozzle** `[Sutton §16.1 Fig 16-2]`:

    M = F · L · sin δ

`F` = thrust, `L` = distance from the gimbal pivot to the vehicle CG, `δ` = thrust-vector
deflection angle. Side force ∝ `sin δ`. **Roll control cannot be obtained from a single
gimbal** (only pitch + yaw) — it needs two or more rotary vanes or two or more separately
hinged nozzles `[Sutton §16.1 p.609]`.

- **Hinge** = rotation about one axis only.
- **Gimbal** = a universal joint = two axes (pitch + yaw).

## Empirical correlations & typical values

**Table 16-1 — TVC mechanisms** `[Sutton §16.1 p.611]` (L = used with liquid engines):

| Mechanism | Max deflection | Thrust/Isp penalty | Notes |
|---|---|---|---|
| **Gimbal or hinge** | **±12°** | very small | simple, proven; low torque, low power; needs flexible propellant piping (bellows); large actuators for high slew rate |
| Movable nozzle (flexible bearing) | ±12° | negligible | no sliding/moving seals; high actuation force; torque rises sharply at low temperature (stiff elastomer) |
| Movable nozzle (rotary ball + gas seal) | ±20° | none (if whole nozzle moves) | sliding hot-gas spherical seal; limited duration |
| Jet vanes | ±9° | **0.5–3 %** | vane erosion; gives roll control with a single nozzle; extends engine length |
| Liquid-side injection (LITVC) | **±6°** | injectant Isp nearly offsets weight | toxic liquids for high performance; low-vector-angle applications only |
| Hot-gas-side injection (HGITVC) | — | low | needs special hot-gas valves (C-C or rhenium); "technology not yet proven" as of 2001 |
| Hinged auxiliary thrust chambers | — | low | fed from the main turbopump; small moments; roll control |
| Turbine-exhaust-gas swivel | — | low | roll control only |

**Real gimbal — SSME gimbal bearing** `[Sutton Table 16-2 p.615]` (ball-and-socket universal
joint, Ti-6Al-6V-2Sn, 11 in dia × 14 in, 105 lbf assembly):

| Parameter | Value |
|---|---|
| Engine weight supported | ~7000 lbf |
| Thrust transmitted | 512 000 lbf |
| **Operational max angular motion** | **±10.5°** |
| Maximum angular capability (incl. tolerances/alignment margin) | ±12.5° |
| **Max angular acceleration** | **30 rad/s²** |
| **Max angular velocity** | **20°/s**; min 10°/s |
| Coefficient of friction (88–340 K) | 0.01–0.2 |
| Operational cycles to ±10.5° | 200 (+ 1400 non-operational) |

**Independent corroboration (2026-09-24)** `[SSME-Orientation p.10-11]`: matches this table's
±12.5° capability / 200-operational/1,400-nonoperational-cycle figures exactly, and adds
material detail Sutton's table lacks — 6Al-6V-2Sn Ti with Fabroid inserts.

**Actuator sizing — IUS solid-motor flexible-bearing TVC** `[Sutton Table 16-3 p.616]`
(4° + 0.5° margin, or 7.5°; two redundant electromechanical ball-screw actuators): stall
force ≥ 1.9 kN (430 lbf); no-load speed ≥ 8.13 cm/s; stiffness ≥ 28.9 kN/cm; frequency
response > 3.2 Hz at 100° phase lag; system weight ≤ 22.4 kg.

**Alignment** `[Sutton §16.1 p.617]`: the neutral thrust vector should pass through the
vehicle CG; the geometric centreline of the diverging section is taken as the thrust
direction. Achievable alignment accuracy ~**0.25°** and axis offset ~0.020 in for small
nozzles.

**Movable nozzles are the most efficient** of the mechanical-deflection types — no
significant thrust/Isp reduction, weight-competitive `[Sutton §16.1 p.613]`.

**Gimbal-mount mass** `[Sutton Table 8-1]`: ~2–10 % of thrust-chamber mass (RL10B-2 < 10
lbf, RS-27 70 lbf, AJ-10 23 lbf, LE-7 57.3 lbf).

**Historical / vehicle practice** `[Sutton §16.1 p.609]`: many US vehicles use gimbals;
several Soviet launch vehicles use multiple hinges (e.g. 4 hinges). **Gimbal range does not
scale with thrust** — the SSME transmits 512 000 lbf through ±10.5°; small missiles use
similar ranges.

## Caveats

- Deflection ranges in Table 16-1 are typical maxima; *operational* deflection during flight
  is much smaller (SSME: ±10.5° capability, actual operating deflections "much smaller").
- Actuator numbers are for two specific vehicles (SSME, IUS) — they show the *shape* of the
  requirement (stall force, slew rate, stiffness, bandwidth), not a universal formula.
- `[Huzel §7.5, §9.6]` covers gimbal-bearing structural design and hinge-moment calculation
  in more procedural detail (leaves ~281, ~388) — not transcribed here.

## Implications for engine_designer

- **`gimbal.py` `GIMBAL_RANGE_TYPICAL_DEG = (2.0, 11.5)`** (ASSUMPTIONS.md item #38): **well
  supported.** `[Sutton Table 16-1]` gives gimbal/hinge max **±12°**; `[Sutton Table 16-2]`
  gives SSME operational **±10.5°** (±12.5° capability). The tool's upper bound of 11.5°
  sits between operational and capability — a defensible "plausibility" ceiling. The lower
  bound (~2°) matches small vernier/thrust-misalignment-correction ranges. Cite `[Sutton
  §16.1, Table 16-1, Table 16-2]`.
- **"Gimbal range does NOT scale with thrust"** (`gimbal.py` docstring / README): confirmed
  verbatim by `[Sutton §16.1 p.609]` — SSME at 512 klbf uses ±10.5°, small missiles use
  similar. The tool's soft plausibility check (warn if outside ~2–11.5°, regardless of
  thrust) is exactly the right design.
- **Ungimballed option** (matches real small RCS/vernier engines and boosters using separate
  vernier chambers): `[Sutton §16.1]` — auxiliary/vernier thrust chambers and jet vanes are
  how single-nozzle vehicles get roll control; a booster can legitimately be ungimballed if
  TVC comes from elsewhere.
- **Custom `gimbalRange` + response speed** (matches `H3-250K-V` / `TR341`): `[Sutton Table
  16-2/16-3]` gives real actuator envelopes — max angular velocity ~20°/s, acceleration
  ~30 rad/s², bandwidth > 3.2 Hz. If the tool ever validates a user's response-speed input,
  these are the anchors.
- **Gimbal-mount mass** (~2–10 % of chamber mass, `[Sutton Table 8-1]`): a concrete number
  for the dry-mass model, which currently omits the gimbal bearing and actuators
  (ASSUMPTIONS.md — mass model is an explicit lower bound). See topic 13.
- **Actuator power / TVC as a system cost**: not modelled; `relative_cost_factor` is tracked
  but not combined into a cost model. `[Sutton Table 16-1]` "low power" for gimbal vs "high
  actuation forces" for movable nozzle is the kind of design-consequence the tool surfaces
  for other choices.
