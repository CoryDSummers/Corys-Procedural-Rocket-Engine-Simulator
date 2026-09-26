# 14 — Combustion stability

## Scope

Chugging / buzzing / screeching, the acoustic-mode formulas, feed-system coupling and Pogo,
and the fixes (injector Δp, baffles, Helmholtz cavities). The tool models only the hydraulic-
chug proxy (`min_stable_dp_ratio` in `injectors.py`, `throttle.py`); this file is the
reference if acoustic modelling is ever added.

## Key relations

**Stability threshold** `[Huzel §4.8 p.144]`, `[Sutton §9.3]`: smooth combustion = chamber-
pressure fluctuations within **±5 %** (peak-to-peak / mean < 0.10) of mean Pc. Above that,
random = "rough combustion", organised periodic = "combustion instability".

**Chamber acoustic-mode frequency** `[Huzel §4.8 Fig 4-59 p.144]`:

    longitudinal:  N = a_e / (2·Lc)
    tangential:    N = 0.59 · a_e / dc
    radial:        N = 1.22 · a_e / dc

`a_e` = speed of sound in the chamber gas, `Lc` = chamber length (injector face to throat),
`dc` = chamber diameter.

**General frequency estimate** `[Sutton eq. 9-1]`:

    f = a / λ = (1/λ) · √( k · R' · T / M )

`λ` = wavelength (distance travelled per cycle, depends on mode), `a` = acoustic velocity.
**Smaller chambers → higher frequencies.**

**Helmholtz-resonator absorber frequency** `[Sutton eq. 9-2]`:

    f = (a / 2π) · √( A / ( (L + ΔL) · V ) )

`A` = restrictor area, `V` = cavity volume, `L` = orifice length, `ΔL` = empirical
end-correction 0.05–0.9 (varies with L/d and edge condition).

## Empirical correlations & typical values

**Table 9-2 — Principal types of combustion instability** `[Sutton §9.3 p.348]`:

| Type | Names | Frequency (Hz) | Cause |
|---|---|---|---|
| Low frequency | **chugging**, feed-system instability | **10–400** | pressure coupling between the propellant feed system (or entire vehicle) and the combustion chamber |
| Intermediate | **buzzing**, acoustic, entropy waves | **400–1000** | structural/manifold vibration, flow eddies, MR fluctuations, feed-system resonances |
| High frequency | **screaming / screeching / squealing** | **> 1000** | combustion-process pressure waves + chamber acoustic resonance |

**Chugging** `[Sutton §9.3 p.349]`: from feed-system elasticity. Common at **low Pc
(100–500 psia)**. Causes: pump cavitation, gas entrapment, tank-pressurisation fluctuations,
support/line vibration. **Cured by increased injection pressure drop + feed-line damping.**
**Pogo** is a special chug: **5–25 Hz** (Sutton) / 10–50 Hz longitudinal vehicle-engine
coupling. Damped by a partially gas-filled **pogo accumulator** on the feed line (SSME LOX
line, between the two O2 turbopumps); pump-side mitigation = steep head/flow curves.

**Buzzing** `[Sutton §9.3 p.350]`: rarely > 5 % perturbation, low energy — "more noisy and
annoying than damaging", but can trigger high-frequency instability. Most prevalent in
medium engines (2000–250 000 N / 500–60 000 lbf).

**Screeching** `[Sutton §9.3 p.352]`: highest energy, **can destroy an engine in < 1 s**.
Isolated to the combustion chamber. Modes: longitudinal (organ-pipe) + transverse (tangential
+ radial). **Transverse predominates in large liquid rockets, near the injector; tangential
is the most damaging.** During instability: heat-transfer rates rise **4–10×**, instantaneous
pressure peaks ~**2×** stable. Driven by acoustically-stimulated variations in droplet
vaporization/mixing and local detonations. **Popping** (random high-amplitude disturbance
with hypergolics, pressure ratio up to 7:1, µs rise time) can trigger it — cured by injector
redesign.

**Rating techniques** `[Sutton §9.3 p.354]`: nondirectional **bombs** (250-grain PETN/RDX in
a Teflon/nylon case), **pulse guns** (10/15/20/40/80-grain pistol powder, directional, fired
in sequence ~150 ms apart with increasing intensity), inert-gas flows, off-MR operation,
inert-gas slugs, deliberate hard start. Measure the recovery time after a known
overpressure. `[Huzel §4.8]`: monitor 3-axis vibratory acceleration → auto engine cutoff
above a cumulative-oscillation limit.

**Control of instabilities** `[Sutton §9.3 p.356–358]`:
- *Chugging*: eliminate feed-system resonance; **increase injection Δp**; add feed-line
  damping devices.
- *High frequency*: alter the injector (hole pattern/sizes, **increase injection Δp**) OR
  increase acoustic damping. Modern practice favours damping.
- **Injector face baffles**: number of compartments is **always ODD** (an even number acts
  as nodal lines and *enhances* standing modes). Designed to suppress frequencies **below
  ~4000 Hz** ("damaging instability is rare above 4000 Hz"). SSME main injector: 5-compartment
  baffle (75 lengthened concentric-sleeve elements).
- **Acoustic absorbers (Helmholtz resonators)**: discrete cavities at the injector "corner"
  — a pressure antinode for *all* resonant modes and a velocity node (favourable for
  absorption). Modern practice favours absorbers over baffles.
- **Damping sources**: the exhaust nozzle is the main damper of longitudinal modes;
  combustion itself is the main damper of transverse modes (liquid→gas volume change +
  momentum imparted to droplets); wall friction is negligible.
- Concentric-tube (coax) H2/O2 is more stable if the H2 gas is warm and its injection
  velocity is ≥ **10×** the LOX velocity.

**Real example** `[Sutton Table 9-3]` Vulcain HM-60 (LOX/LH2, 1008 kN vac, Pc 10 MPa, MR
5.6): first tangential mode T1 = 2424 Hz; L1T1 = 3579 Hz; modes up to R2 = 8774 Hz.
`[Huzel Fig 4-60]` shows vibration amplitude vs MR for a 150 000-lbf LOX/RP-1 engine — a
sharp boundary between stable and unstable regions.

**Historical** `[Huzel §4.8 p.143]`: the A-4 / V-2 never had instability in 4000+ launches —
attributed to its low performance level and/or chamber geometry.

**Real high-Pc engine with zero stability hardware — NK-33** `[NK-33-Mod]`: "There are no
baffles, acoustic cavities, or other stability devices in the main combustion chamber...
Since very early in the NK-15 development, there have been no instances of combustion
instability." Achieved purely through injector-face propellant distribution (coaxial
fuel-swirl elements, outer row biased for mass/MR stratification) at Pc 2109 psia — a real
counter-example to "high Pc needs baffles/cavities," and a reminder that injector-face
design alone can achieve stability without added hardware. The engine's *preburner*, by
contrast, does use injector-face baffles — the stability-critical device on this engine is
the small oxidizer-rich preburner, not the large MCC (see topic 08).

**Atomization-vs-stability tradeoff, gas-centered-swirl elements** `[Bazarov p.9–13]`: a
related AFRL study of converger/diverger/prefilmer gas-centered-swirl variants got c\*
efficiency > 90 % with mean drop sizes 3–4× finer than equivalent shear-coaxial elements,
but some geometry variants showed **"chug" instability** at certain operating points — a
concrete case where the finest-atomizing variant of an element family isn't automatically
the most stable one.

**Real large parametric screech-suppression program, 20,000-lbf class**
`[NASA-TN-Acoustic, Summary of Results]`: a large NASA Lewis test program (~17 underlying
single-variable studies) across LOX/GH2 (concentric-tube injector) and earth-storable
N2O4/(50-50 N2H4-UDMH) (impinging injector), giving real quantified stability/performance
tradeoffs at much finer granularity than `[Sutton]`'s Table 9-2 boundary data:
- **Recessing the oxidizer post 0.1 in gave +50°R screech-temperature margin AND +3% C\*
  efficiency** — a rare case where a stability fix also improved performance, directly
  relevant to `injectors.py`'s coaxial/shear-element recess parameter if one exists.
- **Extending the oxidizer tube fully stabilized a 100-element injector, at a ~4% C\* cost**
  — a real, quantified stability-vs-performance tradeoff for post-extension length.
- A stability parameter combining hydrogen injector ΔP, propellant densities, oxidizer
  orifice diameter, and O/F had a **critical value of 4.4** (above stable, below unstable)
  for an 85%-radial-face-coverage injector.
- **Injector-face baffles**: 2-in baffles gave full stability down to 55°R H2 temperature
  with as few as 3 compartments; 1-in baffles needed compartment size < 4.5 in for even
  marginal stability. For the earth-storable pair, 1-in baffles needed compartment size
  < 3.5 in against a 41-grain bomb rating — **baffle compartment size has a real, quantified
  maximum before stability is lost**, and it's propellant-pair/rating-method-dependent.
- **Acoustic liners**: absorption coefficient ≥ 0.25 (including flow-past-aperture effects)
  eliminated screech at the LOX/GH2 engine's worst condition; a **17%-partial-length liner
  fully suppressed screech** — a full-length liner was not required. Liner-absorption theory
  only matched experiment when flow-past-orifice effects were included in the calculation.
- A **porous injector faceplate bleeding ~5% of hydrogen flow** cut the screech transition
  temperature by 25°R at a 1-2% C\* cost — a transpiration-style stability/performance
  tradeoff distinct from a baffle.
- For earth-storables specifically: injector-side fixes (velocity ratio, impingement angle,
  triplet orientation) gave little stability improvement — the program's own conclusion was
  that "no major improvement seems likely through changes in the propellant-injection
  process" for this pair, and energy-*absorption* devices (liners/baffles) were needed
  instead. An oxidizer-fuel-oxidizer triplet was less stable AND more erosive to chamber
  hardware than a fuel-oxidizer-fuel triplet — a real materials/durability caution tied to
  triplet orientation, not just a stability one.

**Real complete Helmholtz-liner design geometry, applied to a real 750 Klbf engine**
`[STBE-PW leaf 159, Table 4.1.2.4-2]`: a full applied design point complementing
`[Sutton eq. 9-2]`'s general formula and `[NASA-TN-Acoustic]`'s parametric absorption-
coefficient data above — 30% acoustic absorption targeted at the first tangential mode
frequency (1212 Hz), aperture gas temp 2000 R, aperture gas MW 22.4, hole diameter 0.10 in,
hole length 0.35 in, open area ratio 0.05, backing cavity depth 0.6 in, liner length 4.0 in.
A real, complete input/output geometry set for a Helmholtz liner sized against a specific
real engine's first-tangential-mode frequency, useful as a worked cross-check if
`combustion_stability.py`'s Helmholtz-cavity sizing is ever validated against a real design
point rather than only the parametric `[NASA-TN-Acoustic]` data.

**A real "acoustic-tube-through-cooling-tube-bank" stability-cavity construction method**
`[STBE-PW leaf 320]`: a different real engine in the same P&W study (Unique STBE Split
Expander) uses a machined coolant-exit-manifold cavity connected to the combustion chamber
through small tubes pressed/swaged between the Haynes 230 regen tubes before brazing, with a
minimal coolant bleed purging the cavity to prevent hot-gas ingestion — a real construction
method for an acoustic absorption cavity integrated into a tube-wall chamber's own cooling
tube bank, distinct from `[Sutton]`'s generic corner-cavity description above.

**A real program-specific bomb-test stability acceptance criterion** `[Agena-CR120362 p.3-42
to 3-43]`: the Bell 8096L (a small 16,000 lbf hypergolic GG-cycle engine, unrelated to the
main real-engine anchors above) was redesigned from a flat-face injector to a 5-legged
baffle to meet a stated qualification spec — "a dynamically stable injector that will damp
over-pressures induced by suitably sized bombs located in the most sensitive position
**within 40 msec to within ±5 psi of steady state pressure**." A concrete, numeric bomb-test
damping criterion from an actual flight-engine development program — cite as one real
program's acceptance spec, not a universal stability-margin standard.

**A real, distinct hybrid instability mode: "resurging"** `[OME-Platelet §XII.E-H, leaf
287-315]` — a real Space Shuttle OME (hypergolic, X-doublet injector) development program's
dominant stability problem, distinct from the chugging/buzzing/screeching taxonomy above:
periodic (~400 Hz) bursts of high-frequency (2000-7000 Hz) instability, each burst a
three-phase cycle (a rapidly-growing spinning first-tangential "burnoff" detonation wave
makes exactly one circuit of the chamber and consumes accumulated unburned propellant → a
"blowdown" pressure decay → a slow "accumulation" pressure recovery before the next burst).
Root cause: the X-doublet is "a good atomizing, poor mixing element" — its concentric-ring
spray leaves a persistent unmixed/unburned propellant cloud downstream of the face (matching
a real measured low-heat-flux near-injector zone, `topics/06b`), which periodically ignites
via the spinning wave and burns off in one detonation-wave circuit. **The fix that worked**:
welding three dams into each injector face-ring manifold at the acoustic-null points under
the opposing propellant's "pie" manifold, breaking circumferential acoustic communication
between injector sectors via the ring manifolds — a real, mechanistically distinct fix from
baffles or corner cavities (it targets the *manifold's* acoustic path, not the chamber gas).
**Acoustic cavities alone did NOT damp resurging and may even promote it**, by damping the
very high-frequency modes that would otherwise keep unburned propellant mixed and burning
continuously — a real, counter-intuitive case where the standard high-frequency-instability
fix (cavities) makes a *different* instability mode worse. Real, quantified geometric levers:
**injector overlap** (injector-ring radius in excess of chamber radius), tested −0.007 to
+0.25 in, consistently *improved* stability for both tested injectors — a real, load-bearing
parameter not previously represented here. Explicitly flagged as **X-doublet-specific, not
platelet-construction-generic**: the splash-plate and unlike-doublet elements (also built as
platelets in the same program) showed different, classical acoustic-mode-coupling stability
behavior instead — don't conflate "platelet injector" with "X-doublet element pattern."

**Real chamber acoustic-mode frequency table, undistorted vs. cavity-damped**
`[OME-Platelet §XII.A, leaf 272]`: 1-L 1400 Hz, 1-T 3100 Hz, 2-T 5200 Hz, 1-R 6500 Hz, 3-T
7100 Hz, 4-T 9000 Hz, 1-T+1-R 9100 Hz — the flight-baseline dual-tuned acoustic cavity
distorts/suppresses the 1-T mode to a measured **~2600 Hz**. **Real dual-tuned cavity
design, the flight-adopted baseline**: eight 1-T cavities (1.5 in deep, 18% of injector face
area) + four 3-T cavities (0.4 in deep, 9% of face area) — **stability margin 80%** (cavity
area 80% greater than the minimum required for stable operation), a real quantified
acoustic-cavity design-margin figure. A dedicated follow-on program (at closer-to-flight
regen-fuel temperature, hotter than the ambient-temperature propellant used in the extensive
prior test base) confirmed cavities still worked and found **doubly tuned cavity
configurations that suppress the first and third tangential modes plus the first radial mode
simultaneously** `[OMS-DesignEvo p.645]`.

**A real cavity-vs-baffle selection rationale tied to reusability, not suppression power**
`[OMS-DesignEvo p.645]`: acoustic cavities (Helmholtz-type), not baffles, were selected for
this reusable/long-duration application specifically because cavities are "easier to cool
and, therefore, less subject to failure from either burnout or thermal cycling" than
baffles — a direct real precedent tying stability-hardware choice to a reusability/duty-cycle
requirement rather than pure suppression effectiveness. A real, stated uncertainty: even with
demonstrated stability across "a relatively wide range of cavity configurations," "the
stability of an engine with or without acoustic cavities could not be predicted analytically
with confidence" — stability testing, not calculation, closed the loop.

## Caveats

- **Resurging** (`[OME-Platelet]`) is real but specific to the X-doublet element's poor
  near-face mixing on a low-Pc (125 psia) hypergolic OME — its exact numeric fixes (dam
  placement, cavity dimensions) are that engine's own resolution, not universal
  requirements; 294 of the program's 362 full-scale firings were stability troubleshooting,
  so treat this as a troubleshooting-heavy development report, not a clean reference dataset.
- Frequency formulas are estimates from chamber geometry and sound speed; real behaviour
  depends on the coupled feed-system + structure + combustion dynamics.
- Stability is fundamentally empirical — new injectors must reuse proven stable geometry and
  be hot-fire tested over the full operating envelope `[Sutton §9.3, Huzel §4.8]`.
- The tool does **not** model acoustic instability at all; only the hydraulic-chug proxy.
- `[NASA-TN-Acoustic]`'s quantified findings (recess depth, baffle compartment size, liner
  absorption coefficient) are for a specific 20,000-lbf-class engine family — the program's
  own authors caution that "complete confidence in stable operation is not possible until
  the effects of scaling factors such as chamber size are determined," i.e. these numbers
  may not scale linearly to much larger or smaller engines. This note leans on the paper's
  own 36-item Summary of Results rather than the underlying body sections/figures — if a
  specific test matrix or plotted curve is needed later, the body sections weren't deep-read
  this pass (see `sources/nasa-tn-acoustic-instability-1968.md`).

## Implications for engine_designer

- **`injectors.py` `min_stable_dp_ratio`** (hydraulic-chug / stiffness floor; ASSUMPTIONS.md
  item #10): the physics is exactly right — `[Sutton §9.3]` and `[Huzel §4.5, §4.8]` both
  name **increased injection pressure drop** as the primary cure for chugging, and chugging
  is worst at low Pc (100–500 psia). The tool's floor expressed as a fraction of Δp/Pc
  (0.05–0.10) captures "the injector must stay stiff enough that chamber-pressure
  fluctuations don't feed back into the flow." No literature number for the exact fraction,
  but the concept is textbook.
- **`throttle.py` `dp_inj ∝ throttle²`** (orifice scaling) and the injector-stiffness sweep:
  `[Sutton eq. 8-2]` `ṁ = Cd·A·√(2ρΔp)` → `Δp ∝ ṁ²` at fixed area → `Δp ∝ throttle²`. Exact.
  So deep throttle collapses injector stiffness (Δp/Pc falls faster than Pc) → chug risk —
  the tool models this correctly.
- **`practical_min_throttle`** (demonstrated deep-throttle ability, separate from hydraulic
  stability): supported by `[Sutton §8.5]` — fixed-area injectors can't throttle deep;
  variable-area (pintle) injectors hold Δp across the range (LEM descent engine, 10:1).
- **Acoustic modelling is not present** — if added, `[Huzel Fig 4-59]` (mode frequencies)
  and `[Sutton Table 9-2]` (frequency bands) are the starting point; a design could warn if
  the estimated first tangential frequency `0.59·a_e/dc` falls in a range that historically
  needed baffles/cavities (< ~4000 Hz per `[Sutton §9.3]`).
- **Baffle/cavity design choices** (odd compartment count, corner-mounted cavities, suppress
  < 4000 Hz) are the kind of "warn, don't block" design-consequence guidance the tool gives
  for other choices — a candidate for an "injector stability aids" note if injector geometry
  is ever exposed.
- **A real, complete Helmholtz-liner geometry now exists** (`[STBE-PW]`, above) if
  `combustion_stability.py`'s cavity sizing is ever spot-checked against an applied real-
  engine design point rather than only `[NASA-TN-Acoustic]`'s parametric test data —
  report-only, no code changed.
- **A real, distinct instability mode ("resurging") and injector-overlap parameter now
  exist** (`[OME-Platelet]`, above) — neither is modeled by `combustion_stability.py` today
  (which covers acoustic modes and baffle/cavity stability aids, not manifold-acoustic-path
  coupling or injector-ring/chamber-radius overlap). Not actionable without a manifold-
  acoustic model the tool doesn't have; noted for awareness only, and as a real example that
  a single element type (X-doublet) can have an instability mode unrelated to the classical
  chugging/buzzing/screeching taxonomy above. Report-only.
- **A real bomb-test acceptance-criterion number** (`[Agena-CR120362]`'s 40ms-to-±5psi) could
  anchor a future stability-rating-method discussion if the tool ever models bomb-test-style
  qualification criteria, alongside `[Sutton]`'s existing rating-technique survey above —
  cite as one program's spec, not a general standard. Report-only.
