# 12 — Materials and structures

## Scope

Material selection framework, high-temperature allowable stress, the wall thickness /
hoop-stress calculation, the safety-factor structure, and ablative regression. Feeds
`engine_designer/physics/materials.py` and `mass_model.py`.

## Key relations

**Thin-wall pressure vessel** `[Huzel §2.4 p.58]`:

    cylinder (hoop stress):   t = P · r / σ_allow          (t = P·D / (2·σ))
    sphere:                   t = P · D / (4·σ_allow)

With the tool's safety factor: `t = SF · Pc · r / σ_allow` (`mass_model.py`), locally varying
`r` along the profile.

**Load / safety-factor structure** `[Huzel §2.4 eq. 2-8…2-11 p.57]`:

    design limit load = largest of:  1.2 × (normal steady working load)
                                     1.2 × (normal transient, e.g. start/stop)
                                     1.1 × (occasional transient, e.g. irregular start)
                                     1.0 × (mandatory malfunction load)
    yield load    = 1.1 × design limit load
    ultimate load = 1.5 × design limit load      ← this is the "1.5" the tool uses
    proof-test load = 1.0 × design limit load
    endurance limit (fatigue) = 20–60 % of ultimate tensile strength
    stress concentration at a discontinuity = +100–300 % of mean section stress

So the *effective* margin over the nominal steady working load is ~1.5 × 1.2 = **1.8**
(ultimate factor × design-limit factor). Real programs use 1.25–4× depending on human-rating
`[mass_model.py comment]`.

**Ablative regression**: `wall_life = wall_thickness / regression_rate` `[mass_model.py]`.

**Radiation-cooled wall**: `q = ε·σ_SB·T_wg^4` sets the equilibrium wall temperature; the
material must have short-time strength at that temperature (topic 06).

## Empirical correlations & typical values

**Material-selection factors** `[Huzel §2.5 p.59]`: function/size/shape; mechanical
properties (strength, stiffness, hardness, ductility — with emphasis on temperature
extremes); physical/chemical (density, thermal conductivity, specific heat, expansion
coefficient, Poisson ratio, strength-to-weight, corrosion resistance, propellant
compatibility vs T); fabrication (forge/cast/weld/machine/form); cost/availability;
standards.

**Temperature effects** `[Huzel §2.5]`:
- Tensile and yield strength **increase** with decreasing temperature; ductility **suffers**.
- Elevated temperature → creep and strength reduction; low temperature → embrittlement.
- **Cryogenic / LH2** needs: low-temperature-embrittlement resistance (notched/unnotched
  tensile ratio — 2014-T6 Al at −423 °F is 0.94 longitudinal / 0.83 transverse); thermal-
  shock resistance (figure of merit **Ftu·k / (E·α)** — ~5–8 for stainless, ~40–48 for
  2014-T6 Al); hydrogen-embrittlement resistance (worst at intermediate temperature for
  steels and Ti); chemical-reaction resistance (H2 forms hydrides with Ti, U).

**Material groups** `[Huzel §2.5]`:
- Low-alloy steels (AISI 4130/4140/4340): −60 to 600 °F, not for corrosive environments;
  pins, bolts, shafts, mounts, injector bodies, some pressure vessels.
- Austenitic stainless 300-series: best corrosion resistance; cryo + storable; regen tubes,
  manifolds, injector bodies/domes, valve bodies, ducts, tanks.
- Martensitic stainless 400-series: hardenable.
- (Superalloys, refractory metals, ablatives covered by application context, not a
  systematic table — SP-125 is pre-SSME.)

**Radiation-cool material limits** `[Huzel §4.4 p.121]`: Mo-0.5Ti and 90Ta-10W good to
3500 °R (1944 K), need MoSi2 coating on Mo; Ti alloys and Haynes 25 to 2600 °R (1444 K).
Iridium-on-rhenium for oxidation resistance `[Sutton §8.2 p.287]`.

**Ablatives** `[Sutton §8.2–8.3 p.288–289]`: oriented fibers (glass, Kevlar, carbon) in an
organic matrix (epoxy/phenolic); gases pyrolyse out and form a protective film, fibers +
matrix residue form a hard char that keeps the contour. **Carbon-carbon loses load
capability at ~3700 K (6200 °F)**; oxidises to CO/CO2 so best with fuel-rich exhaust; used
for nozzle throat inserts and extensions. Ablative works well only at **low Pc, short
duration, non-oxidative exhaust**. **Pulsing is worse than continuous firing** for the same
cumulative time — max liner consumption at **4–15 % duty cycle** `[Sutton Fig 8-10]`.

**Real worked stress example** `[Huzel Sample 2-2 p.57]`: AISI 4340 HT-180 — ultimate 185
ksi RT / 178 ksi at 300 °F; yield 170 ksi RT / 150 ksi at 300 °F. Sphere, 7238 in³, working
2000 psia, malfunction 2450 psia → design limit 2450, yield pressure 2695, ultimate 3675 →
wall thickness 0.124 in (ultimate governs).

**Material-selection framework (5-factor)** `[Ch12-Materials p.14]` — a modern (c.2016)
complement to `[Huzel]`'s pre-SSME treatment above. Five factors drive per-component
material choice: engine size, duty cycle (expendable vs. reusable), propellants, turbine
drive cycle, stage (booster vs. upper). Higher Pc tightens material constraints for two
reasons: specific strength (strength/weight) becomes dominant, and high-strength alloys tend
to be harder to fabricate and more toughness/ductility/environment-compatibility-limited.
Component-level criteria stated explicitly: rotating pump parts need high specific strength
**and** ductility; pump housings need castability + adequate specific strength (castings are
usually the cheapest route); LOX valve poppets/seats must be LOX-ignition-resistant; chamber
liners need thermal conductivity **and** thermal-fatigue resistance; nozzle material family
follows directly from the cooling method chosen (regen -> conventional alloy, film ->
similar, ablation -> silica-phenolic, radiation -> refractory metal/ceramic).

**Real turbopump materials by engine generation** `[Ch12-Materials, section 12.6, p.36-50]`
— the single richest real-alloy-per-real-engine table in this literature set, extending
`[Huzel]`'s pre-1971 coverage into the SSME/RS-68/3D-printing era:

| Turbopump | Pump-side materials | Turbine-side materials |
|---|---|---|
| V-2 (A-4), 1940s | Housings/impellers: cast Al-13Si-0.3Mn ("Silumin") | Disk: Al-2Mg-1.4Mn; blades: cast 13X (Al-13Si), as-cast oxide skin as a thermal barrier |
| Atlas Mark 3, late 1950s | Impellers/housings: Tens-50 cast Al; inducers: 7075-Al forgings | Disks: forged 16-25-6 (Fe-16Cr-25Ni-6Mo); blades: investment-cast Stellite 21 (Co-27Cr-5Mo-2.5Ni) |
| F-1 (Mark 10) | Housing/impellers: Tens-50 Al castings (highly-chilled molds); LOX inducer: Monel K-500 forging | Turbine disk/manifold: Rene 41 (Ni-19Cr-12Co-10Mo-3Ti-1.5Al-0.12C); blades: 713C investment castings |
| J-2 (Mark 15) | Inducer/rotor/stator: Monel K-500 (guaranteed cryo ductility) | Turbine discs: alloy 718 forgings - one of the first-ever 718 forging applications (double-vacuum melt + high-temp homogenization fixed a short-transverse-property defect) |
| SSME HPFTP (original) | - | Blades: cast MAR-M-246 (directionally solidified) on Waspaloy hubs - H2-embrittlement-prone |
| SSME alternate HPOTP / Block II | 293 welds eliminated via fine-grained investment castings; Si3N4 ceramic bearings | Single-crystal PW1480 thin-wall hollow-airfoil blades - eliminated the MAR-M-246 cracking/embrittlement problem |
| SSME fuel-side impellers | 3 stages forged Ti-5Al-2.5Sn-ELI; diffusers cast A357 Al, later F-357 (Be-free) | - |
| RS-68 fuel TPA | Housing: centrifugally cast alloy 625 | - |

Cross-cutting notes `[Ch12-Materials p.45, 49]`: bearings historically 440C/52100 steel then
**Cronidur 30** (15Cr-0.5Ni-0.4N-0.3C) adopted for SSME/RS-68, then newer designs using
**Si3N4 ceramic** rolling elements ("virtually eliminating bearing wear and fatigue
concerns"). Turbine housings generally: Inconel 625/718, A-286, Incoloy 903, Haynes 188.
H2-embrittlement mitigation on hydrogen-side turbine hardware: gold/copper coatings or
iron-based overlays. **C/SiC ceramic-matrix-composite turbine blisks** demonstrated
damage-tolerant (kept running with a cracked blade in rig test) and rated to **2000 F
(1093 C)** vs. **1200 F (649 C)** for nickel-alloy turbines - a ~450 C headroom jump if ever
qualified, not yet flight-standard as of writing.

**Chamber-liner and injector materials** `[Ch12-Materials, section 12.5, p.15-35]`: SSME
hot-wall liner is **Narloy-Z** (Cu-3%Ag-0.5%Zr) - "the key to obtaining the combustion
efficiency of the SSME," retaining ~80% of pure-Cu thermal conductivity with better
strength/thermal fatigue than prior Cu alloys. Russian designs (RD-107 family) use
**Cu-3%Cr** inner liners. Apollo SPS (AJ10) nozzle: **C-103 niobium alloy**. Modern
(post-2010s) additive-manufactured (SLM) **Inconel** injectors have replaced
hundreds-of-pieces conventional builds with 1-2 printed pieces, hot-fire tested in LOX/LH2
"with no noticeable loss of performance."

**Tube-wall nozzle retaining bands** `[SP-8120 §2.2.1.1/§3.2.1.1 p.27-31, 71-72]`: a
tube-bundle nozzle wall has essentially no resistance to side loads (startup, flow
separation, mechanical attachments) on its own - either a continuous shell or intermittent
rigid retaining bands must react all hoop/side/gimbal loads instead, by explicit design
criterion ("do not require the tube bundle to withstand any loads from exhaust gas or
mechanical forces"). Bands go downstream of the continuous-shell region, since wall pressure
(and thus required support) drops rapidly aft of the throat. Two band cross-sections are
recommended: simple flat bands where buckle resistance can be low (near the throat), stiffer
profiles where it must be high (near the exit). **Real F-1 data**: instrumented, hot-fired
tube-to-band joints measured axial stress-concentration factors up to 2.2 (analysis: up to
2.8 axial / 2.45 bending) on F-1's rectangular bands; **thinning the band cross-section at
the band edge reduced the concentration** - the only quantitative fix given. **Real J-2 to
J-2S fix**: an early J-2 aft-band buckling failure (from startup side loads - a transient
load case, not steady-state) was first patched expensively/heavily, then properly redesigned
lighter-and-buckle-resistant for J-2S once time allowed. Band material must be braze-
compatible with the tube alloy; Inconel 718 and Inconel X-750 are the named real band alloys,
using a controlled post-braze furnace cooldown to develop mechanical properties. A real
failure-mode catalog (Fig. 15) attributes most tube damage under bands to high-low tube
alignment (excess braze gap or forced crown depression), inconsistent band-to-tube contact
angle, concentrated external loads, or fabrication-induced (weld-shrinkage) interference -
fixed in practice with shim stock rather than forcing the fit. Tube splice joints (where one
tube becomes two downstream to match increasing nozzle circumference) should be avoided where
possible; if required, use a high-ductility tube alloy (347 CRES or nickel) for a higher
taper ratio before splicing is needed, and always put any joggle on the cold-gas side of the
tube, never the hot-gas side (hot-side joggles are a crown-depression/stress-concentration
risk exactly where wall temperature is already highest).

**Inconel X-750 physical/thermal/mechanical properties** `[SMC-X750 Tables 2/3/5/13]`: the
alloy `[SP-8120]` names above (alongside Inconel 718) as a real hatband material now has a
citable properties source for `materials.py`'s `inconel_x750` entry. Density 8.28 g/cm³
(8280 kg/m³); melting range 1393-1427°C; oxidized-surface emissivity 0.895 at 600°F rising
to 0.925 at 2000°F (a real cited figure, unlike `inconel_718`'s uncited 0.7 estimate).
Thermal conductivity 83 Btu·in/(hr·ft²·°F) at 70°F (11.97 W/(m·K)), rising to 143 at 1200°F;
mean CTE (from 70°F) 7.8e-6/°F at 800°F (1.40e-5/K); static-tension Young's modulus 31.0e3
ksi at 80°F (2.14e11 Pa). Real cited yield strength (Table 13, solution-treated + furnace-
cool precipitation-treated - the condition aimed at real service strength rather than
spring temper) is 845 MPa at 1200°F and 530 MPa at 1500°F - both far above any working
allowable this tool would assign, matching `inconel_718`'s own already-heavily-derated
`allowable_stress_pa`. No table gives a strength value at the alloy's own claimed 1800°F
oxidation-resistance ceiling (only creep/rupture/fatigue curves extend that far) - the same
"real data stops short of the tool's max_service_temp_k" situation `inconel_718`'s
ASSUMPTIONS.md entry already flags. See `sources/smc067-inconel-x750.md` for full tables.

**Real splice-count corroboration — J-2S** `[AEDC-J2S §2.1.1 p.1-3]`: real J-2S hardware
(same engine family as SP-8120's J-2/J-2S band-redesign anecdote above) uses exactly this
splice pattern in practice — fuel flows down **180** tubes then up **360** tubes to the
injector, i.e. every downcomer tube splices into two upcomer tubes at the turnaround (a 1:2
splice ratio) to match the increasing nozzle circumference toward the throat/chamber. A
concrete real-hardware instance of the `[SP-8120]` splice-joint design criteria just above,
on the exact engine SP-8120's own anecdote references.

**Manifold structural supports** `[SP-8120 §2.2.5.2.4/§3.2.5.2.4 p.47-48, 79-80]`: vanes,
splitters, dams, and structural ties inside large thin-wall manifolds fail from differential
thermal stress, vibration fatigue, resonant flutter, or static-pressure loading - and the
monograph stresses that such a failure is as much a *combustion*/performance risk as a
structural one ("often produces a maldistribution of fluid flow and results in performance
loss, combustion instability, or wall overheating"). Toroidal manifold shells "breathe" under
pressure and are more flexible than their supporting structure, so ties must either flex with
the shell while staying locally rigid, or mount on one side only with clearance elsewhere.
**Attachment weld quality ranking, worst to best**: fillet weld ("generally unacceptable") <
full-penetration fillet weld ("usually acceptable") < butt weld ("good... first choice") <
integral casting/parent-metal construction ("excellent... failure free"). Attachment location
itself is called "extremely critical" since fatigue failure there is the most common failure
mode. Real example: an 80%-cross-section dam in the H-1 engine's fuel-return manifold fixed a
nonuniform-inlet-flow problem that had been causing **measured engine performance to change
test-to-test** - a concrete case of a manifold structural/hydraulic fix directly resolving a
performance problem, not just a durability one.

**Real manifold hydraulic/distribution design criteria** `[SP-8087 §2.1.2/§3.1.2 p.19-20,
62-64]` — this is NASA's dedicated fluid-cooled-chamber monograph and the single most
load-bearing new source for manifold design specifically, complementing `[SP-8120]`'s
structural-supports content above with real hydraulic/distribution numbers. **Three manifold
types**: inlet, outlet, turnaround — manifolding is frequently integral with structural
supports/interface flanges (inlet manifold integral with the forward flange in two-pass
systems; turnaround integral with the aft flange when a nozzle extension bolts on). **Real
flow-maldistribution tolerance**: up to **20% flow variation has been tolerated in the first
pass** of a multi-pass system (coldest coolant, widest thermal margin there), but must be
reduced before the final pass — typically via the natural balancing effect of a common
manifold at the turnaround. **Hydrogen systems require analytical (not empirical) flow-
balancing** due to hydrogen's large density variation with temperature; storable-coolant
systems are comparatively easier. **Two competing toroidal inlet-manifold design
philosophies**: (1) variable-area/constant-velocity (tapered torus) — equal velocity to
every passage, smaller/lighter, but harder to fabricate and prone to pressure-drop-driven
maldistribution around the torus; (2) constant-area/variable-velocity — minimizes pressure
loss but produces maldistribution (passages near the inlet see higher velocity than passages
opposite it). **Real practice is a compromise between the two**, using smooth turns/vanes; a
flow splitter at the torus inlet suppresses dynamic-head effects locally. **A real,
propellant-specific turnaround-manifold-topology rule**: common annulus preferred for
storable coolants (evens flow before the critical final pass); discrete per-tube/per-channel
circuits preferred for hydrogen (each channel's resistance must be balanced separately as a
function of *local* coolant properties) — directly relevant to `manifold.py`'s existing
`cooling_flow_topology` options (`"single_pass_countercurrent"` vs. the real-F-1-sourced
`"f1_split_reverse_flow"`), giving a propellant-class rule for which style is appropriate
beyond the two topologies the tool currently models. **A concrete manifold-to-thin-wall
transition criterion**: taper the manifold wall over a short **0.5-1 in transition** between
thin cooled sections and heavy manifolds to avoid bending discontinuities (or use asymmetric
support of the thin section) — complements rather than duplicates `[SP-8120]`'s
vane/splitter/dam *attachment*-quality criteria, since this is the thin-to-thick wall
transition geometry itself. Real interface-flange examples: a welded fuel-turnaround
manifold (fully-penetrating welds to the aft tube ends) and a brazed flange with a *separate*
turbine-exhaust manifold routing hot gas past the fuel turnaround manifold to the same
nozzle-extension attachment — a real two-manifolds-at-one-structural-interface example.

**Real manifold-volute-sizing corroboration for `manifold.py`** `[Fagherazzi-2019 §3.3.2
p.87-88]`: an independent thesis sizes its own coolant supply manifold as a volute (splitting
incoming flow into two symmetric halves feeding the channel bundle) using the **exact same
constant-target-velocity continuity-equation approach `manifold.py` already implements** —
`A(θ) = ṁ(θ)/(ρ·v̄)`, where the cross-section shrinks as flow peels off into channels along
the volute's length — a real, independently-arrived-at second precedent for that design
pattern. Design intent: avoid abrupt velocity changes between the supply volute and the
channels, keep the envelope clear of seal lands/bolt circles. A **circular cross-section is
hydraulically optimal but a rectangular section is often chosen purely for machinability** —
real design practice trading hydraulic optimality for manufacturing simplicity at small
scale. A **simplified constant-cross-section volute** (`A(θ) = const`) is a real, usable
"cheap but good enough" fallback if a non-optimal-but-simple sizing mode is ever wanted. Real
packaging constraint: the coolant inlet had to be moved off-axis to route around o-ring seal
lands, and the outlet needed a 90° flow-diversion elbow to exit radially — concrete evidence
that manifold/fitting geometry is frequently seal/fastener-envelope-driven, not purely
hydraulic, a real-world caveat on `manifold.py`'s per-propellant "hook point" simplification.

**Real six-method throat/chamber structural-support survey** `[SP-8087 §2.1.3.1 p.21-24]`:
(a) cylindrical shell (Aerobee, Improved Titan Stage I); (b) one-piece brazed jacket (J-2,
F-1, H-1) or bolt-on/weld-on corsets (Titan III Stage II/RL10); (c) banded (Atlas
booster/sustainer — the `[SP-8120]` retaining-band case above); (d) U-tube integral shell
(NERVA); (e) double-walled inherent integral shell (Atlas vernier); (f) drilled-passageway
inherent integral shell (Agena). **Real comparative reliability finding**: chambers with
*less rigid* support (banded, cylindrical shell, wirewrap-only) showed *more* tube-to-tube
hot-gas leaks after many tests than chambers with intimate brazed-jacket support (though
entangled with brazing-technique era, not support-rigidity alone, per the source's own
caution). **Real fabrication method** (F-1/J-2/H-1's one-piece brazed jacket): tubes pressed
against the jacket by a pressurized bag during brazing, "costly and difficult" — corroborating
`[SP-8120]`'s own F-1/J-2 fabrication-difficulty anecdotes. **Real fatigue mode**: brazed-
jacket tube crowns fatigue-cracked at the jacket's *aft end* from cyclic structural-resonance
loads and a stress discontinuity there — fixed by adding damping bands to the expansion
nozzle AND tapering the jacket thickness / increasing braze contact over the aft 1-2 in. A
real Titan-sustainer corset (epoxy-filled space between a split shell and the wirewrapped
tube bundle, carrying shear loads) prevented throat buckling from asymmetric jet-separation
side loads up to 1.4× limit load in ground tests.

**Real chamber-liner copper-alloy property table** `[MatCh2 Table 2.6.3 p.53]` — the first
real quantitative room-temperature properties table for these exact alloys in this
reference set (`[Ch12-Materials]`/`[Huzel]`/`[Sutton]` name the alloys but give no numbers):

| Alloy | Composition | CTE (×10⁻⁶/K) | Therm. cond. (W/m·K) | Tensile yield (MPa) | UTS (MPa) | Elong. % |
|---|---|---|---|---|---|---|
| GRCop-84 (annealed) | Cu-6.7Cr-5.9Nb | 15.3 | 285.4 | 196.2 | 368.0 | 21.7 |
| GlidCop AL-15 | Cu-0.3 Al2O3 | 16.6 | 365.2 | 464.5 | 464.5 | 20.5 |
| Zr-Cu C15000 | Cu-0.15 Zr | 16.9 | 366.9 | 501.9 | 510.9 | 19.5 |
| Cr-Cu C18200 | Cu-0.9 Cr | 17.6 | 323.6 | 441.8 | 495.2 | 18.3 |
| Cu-Cr-Zr C18150 | Cu-1Cr-0.1Zr | 16.5 | 323.9 | 549.9 | 564.4 | 11.2 |
| **NARloy-Z** | Cu-3Ag-0.5Zr | 17.2 | 295.0 | 192.0 | 314.0 | 31.0 |

NARloy-Z's real application context: SSME hot-wall liner, 20 MPa chamber pressure, ~3000°C
flame, survivable only via active regen cooling exploiting its high conductivity + good
elevated-temp strength. **Copper is also a deliberate hydrogen-diffusion barrier** on
H2-embrittlement-susceptible Ni-based alloys — SSME uses copper for preburner baffles and
partial main-fuel-valve-housing coating. Caveat: this source's own Table 2.6.3 gives
GRCop-84's composition as Cu-6.7Cr-5.9Nb while its own §2.8 HEE table (below) labels the
same alloy Cu-8Cr-4Nb — an internal inconsistency in the source itself (possibly a
weight-%-vs-atomic-% mismatch), not resolved here.

**Real quantitative hydrogen-embrittlement (HEE) screening data by alloy** `[MatCh2 §2.8.4-
2.8.5 p.68-77]` — the single most load-bearing new content in this batch for materials
selection: HEE Index = notched tensile strength ratio in H2 vs. air (1.0 = no effect, 0 =
total loss), tested at room temperature, 34.5-69 MPa H2. Qualitative bands: Negligible
1.0-0.97, Small 0.96-0.90, High 0.89-0.70, Severe 0.69-0.50, Extreme 0.49-0.0.

| Material (heat treat) | HEE category | NTS ratio |
|---|---|---|
| 4340, 17-4PH, 17-7PH, 18Ni-250 maraging, 440C | **Extreme** | 0.12-0.50 |
| Ti-6Al-4V (annealed) | High | 0.79 |
| Ti-6Al-4V (STA) | **Severe** | 0.58 |
| K-Monel (precipitated) | **Extreme** | 0.45 |
| Copper (OFHC) | **Negligible** | 0.99 |
| **GRCop-84** | **Negligible** | 1.00 |
| **NARloy-Z** | **Negligible** | 1.10 |
| Haynes 230 | High | 0.76 |
| Inconel 625 | High | 0.76 |
| **Inconel 718 (ST @1750°F)** | **Extreme** | 0.46-0.53 |
| **Inconel 718 (ST @1900°F)** | **Small** | **0.92** |
| Waspaloy (PM) | Small | 0.95 |
| A-286 (ST only) | Negligible | 0.97 |
| A-286 (ST + Aged) | **Severe** | 0.51 |

**The single most actionable finding**: **Inconel 718's own HEE resistance flips from
Extreme to Small purely from solutionizing temperature — 1750°F gives NTS ratio ~0.46-0.53,
1900°F gives ~0.92.** This directly explains and quantifies `[Ch12-Materials]`'s J-2
turbopump anecdote above (double-vacuum melt + high-temp homogenization fixed a 718
short-transverse-property shortfall) — same alloy, same heat-treat-sensitivity mechanism,
now with real index numbers. **Aging treatments generally raise strength but worsen HEE**
(A-286, and by implication most PH alloys) — a real, quantified strength-vs-H2-resistance
trade. Cross-cutting findings: **copper/copper-rich alloys are not HEE-susceptible** unless
they contain oxygen (Cu2O + H2 → internal steam embrittlement, a distinct mechanism) —
reinforcing GRCop-84/NARloy-Z as a doubly-good chamber-liner choice (conductivity AND
H2-immune) independent of whether the propellant is LH2. **Pure nickel and Ni-rich binary
alloys are severely embrittled**; **K-Monel is only High/Extreme category** despite being
`[Ch12-Materials]`'s real J-2/F-1-era LH2-pump-inducer choice for cryogenic ductility — that
choice is about a *different* mechanism (cryo embrittlement), not H2-gas-environment (HEE)
immunity, worth not conflating. **Titanium forms brittle hydrides (HRE)**, a distinct
irreversible mechanism from HEE, worst above ~250°C. **Austenitic stainless resists HEE
better than martensitic/PH steels** (17-4PH extremely susceptible) — confirms
`[Ch12-Materials]`'s own caveat about 17-4PH/15-5PH's poor H2/cryo valve-poppet performance.
Caveat: HEE Index is an accelerated RT-only screening method, not a design allowable — the
source itself warns against extrapolating to high-temperature service or using it directly
in a margin calculation without full fracture-mechanics analysis.

**Real LOX/GOX material ignition thresholds** `[MatCh2 §2.9.3-2.9.4 p.84-87]`: NASA-MSFC
Promoted Ignition Test (sustained-burn threshold pressure) and Mechanical Impact Test data —
**titanium and magnesium ignite at essentially any pressure (<15 psi/103 kPa)** — an
absolute red flag for any LOX-wetted titanium part, independent of and in addition to §2.8's
H2-embrittlement concern. **Inconel 718's own Promoted-Ignition threshold (500 psi) is
surprisingly low** relative to stainless/nickel/copper alloys (all non-ignitable up to the
10,000 psi test ceiling) — a second real reason (beyond heat-treat-sensitive HEE) that 718
is not an unconditionally safe universal turbopump alloy; it needs the same case-by-case
oxygen-compatibility review as any borderline metal at the system's real operating pressure.
**Copper, nickel, Monel, and brass are essentially non-ignitable up to 10,000 psi** —
reinforces copper alloys' (GRCop-84/NARloy-Z) role as a doubly-safe choice for oxidizer-side
hardware too. Liquid oxygen is *more* reactive than gaseous oxygen at the same nominal
conditions (higher molecular density). NASA's 10-step Oxygen Compatibility Assessment (OCA)
process is the real qualification framework this data feeds into. Caveat: the source itself
states "data for comparison purposes only, not to be considered standard values" — real
lot/batch variability exists.

**Real superalloy composition table** `[MatCh2 Table 2.5.1 p.48]` — IN-718, Waspaloy,
Udimet 720, Rene 88DT, IN-738, Mar-M247, CMSX-4, Haynes 188, Hastelloy-X, Inconel 625 weight-%
compositions, a candidate cross-check if `turbopump_materials.py`'s catalog is ever extended
with named alloy compositions rather than just properties. Rocket-turbopump application note:
**IN-718 and single-crystal (SX) superalloys are named as real turbopump blade/disk/housing
examples**; for hydrogen service, alloy strength may have to be sacrificed for
H2-embrittlement resistance — a direct statement of the §2.8 trade above.

**Real RD-170/RD-120/RD-0120 specifications** `[Gubanov-1991 p.2-3]` (Energia vehicle's own
chief designer, real spec tables — but see Caveats: this source explicitly does NOT cover
Russian "sandwich" wall construction, despite being the most likely-looking source by name):
**RD-170** (4-chamber ox-rich staged combustion, LOX/kerosene): thrust 740/806 tf SL/vac,
dry mass 9755 kg, 804 firing tests/93,300 s total pre-1991, full-flow kerosene regen cooling
("the nozzle and combustion chamber are cooled with full-flow kerosene entering the chamber
main injector"). **RD-120** (single-chamber ox-rich staged combustion, LOX/kerosene, Zenit
2nd stage): thrust 85 tf vac, Isp 350 s, Pc 112.5 kg/cm², dry mass 166 kg. **RD-0120**
(staged combustion, LOX/LH2, the Soviet SSME-class engine): thrust 200 tf vac, Isp 455 s, Pc
223 kg/cm² (~21.9 MPa), dry mass 3450 kg, MR 6.1, throttling 45-100%, partial-hydrogen regen
cooling ("a certain portion of hydrogen supplied after the fuel pump"), with a real
expander-like bootstrap: its LPFTP boost turbine is driven by gaseous hydrogen tapped from
the combustion-chamber coolant channel. Its chamber construction is described only as "an
inseparable unit... manufactured with use of brazing and welding processes" — no
cross-section or layer detail. Also a real materials-driven cycle-choice precedent: a
tripropellant (O2/H2/kerosene) concept engine uses an oxidizer-rich (not hydrogen-rich)
cycle specifically to avoid hydrogen-embrittlement cracking of turbopump structural
elements — a real, explicitly-stated example of the propellant/cycle-choice materials
interaction this topic file's cryo-embrittlement content already discusses.

**Real manifold-velocity design criterion — `[SP-8120]` full read, 2026-09-24** `[SP-8120
§3.2.5.1 p.78]`: *"Keep the fluid velocities in the manifold as low as possible, preferably
**less than 60 fps for liquids and less than Mach 0.25 for gases**."* This is **more
conservative** than `[SP-8087]`'s already-cited limits above (200 ft/s liquid, Mach 0.3
recommended/0.5 max) — two independent NASA design-criteria monographs give different
numbers for what may or may not be exactly the same quantity (general circumferential
distribution-manifold velocity here vs. `[SP-8087]`'s coolant-jacket-passage velocity
specifically) — flagged as a real, unresolved discrepancy rather than silently picking one.
Narrative context: real observed maldistribution (tube starvation, inadequate local film
coolant) has occurred at **liquid velocities of 50-100 fps and gas velocities of Mach
0.25-0.4** — the 60 fps/Mach 0.25 criterion sits at the low end of a real observed
maldistribution-onset band, not an arbitrary round number. Real inlet-configuration fixes:
multiple tangential inlets, multiple low-velocity radial inlets, or turning vanes/deflector
plates for single-inlet designs; taper the manifold cross-section (or bore a torus
off-center for low-volume production) to fix along-manifold pressure variation. Even a
well-tuned tapered/vaned inlet still shows a real residual pressure rise at the manifold's
final stagnation point — fixed by adding flow resistance downstream of the bleedoff ports
there, not further inlet tuning.

**Real hot-gas (turbine-exhaust) manifold structural/thermal-growth precedent — `[SP-8120]`
full read, 2026-09-24** `[SP-8120 §2.2.5.3/§3.2.5.3 p.48-53, 80-82]`: real historical survey
of turbine-exhaust disposal by engine (Atlas booster canted-duct fix for boattail fires;
Atlas sustainer/Saturn-S-1B looped-tube-into-main-jet; F-1's film-cooling use, above; J-2's
"cat-eyes" dump into the main stream, tubes downstream partially film/primarily regen
cooled; Titan's superheater-then-impingement-on-ablative-extension routing). **Real F-1
hot-gas-manifold thermal-growth/failure detail**: tapered hot-gas torus rigidly attached to
the cooled exit ring, **"omega" expansion joints** for thermal growth (potential radial
growth **~0.5 in.**); recurring real failure at the omega-joint/outer-ring intersection
(tension cracks from ring bending) — fixed by doublers distributing load over a longer base.
A separate tube-denting failure from flame-shield/retaining-band interference was fixed by
increasing clearance from **a few thousandths of an inch to ~0.4 in.** Real material rule by
thermal-load severity: elastic/low-thermal-load designs can use relatively brittle materials
(Waspaloy, Rene 41); high-thermal-load hot-gas manifolds (like F-1's) need materials
retaining **≥20% ductility at elevated temperature** — real examples 347 CRES, Hastelloy C,
Inconel 625, L-605. **Design criterion, safety-relevant**: the looped-tube/gap turbine-
exhaust-introduction method must **not** be used with noncryogenic propellants (real Atlas
RP-1-trapping/LOX-RP-1-gel-detonation precedent, detailed in `topics/07-dump-cooling.md`) —
use an annulus-at-exit or film-cooled-extension method instead for storable propellants.

**Real coolant-return-manifold and nozzle-attachment braze/tolerance numbers — `[SP-8120]`
full read, 2026-09-24** `[SP-8120 §2.2.5.4/§2.2.6 p.53-57]`: real tube-to-manifold joint
comparison — square tube ends into slots (corner-filler/braze-peeling/oil-canning problems)
vs. **circular tube ends into round holes with the tube end expanded in place** (the real
F-1 technique, much more successful, stays within tight braze-gap tolerance). Real
dimensioned brazing tolerances with no equivalent elsewhere in this reference set: **maximum
satisfactory braze gap 0.004-0.006 in.**, **braze-joint length ≥1 tube diameter** for
acceptable strength. Real nozzle-attachment finding: attachments braze on **one side only**
of a tube produce *lower* local stress than two-sided brazing (Fig. 48); welding attachments
to age-hardenable structural members must happen **before** the furnace-braze cycle, not
after (post-braze welding destroys the member's braze-induced strength). Real large-chamber
extension-joint numbers: flanges up to **120 in. diameter**, real-hardware
**out-of-roundness up to 1.5% of flange diameter** (compensated by oversized/radial-slotted
bolt holes), bolt spacing = bolt-head diameter + 2× flange thickness, seals tolerating up to
**50% crush/compression** from flange waviness.

## Caveats

- `[Huzel]` (1967/71) predates NARloy-Z, GRCop-84, Inconel 718 as chamber materials, and has
  **no systematic high-temperature allowable-stress table** for the exotic alloys the tool
  uses. Those numbers must come from modern sources (the ones ASSUMPTIONS.md already cites),
  not from this literature set.
- The thermal-shock figure of merit and notched/unnotched ratio are comparative indices, not
  design allowables.
- `[Sutton]` treats materials only in passing (§8.3) — mostly ablative and C-C.
- `[Ch12-Materials]` is a **historical survey, not a properties handbook** — no stress or
  max-service-temperature tables. Every alloy above is a real historical design choice with
  page-cited context, not a generic allowable a reader could plug into a margin calculation.
  Two temperature figures in it (SSME turbine inlet gas ~840 °C/1550 °F; the C/SiC-vs-Ni
  2000 °F/1200 °F comparison) are stated without their own cited source within the chapter —
  treat as the chapter authors' own figures, not independently re-verified here. Several
  V-2-era specifics are sourced to private interviews with retired Peenemünde engineers
  (oral-history-grade, not primary-source-grade).
- `[SP-8120]` is a **criteria/practices monograph, not a sizing-equation source** — it gives
  design rules ("shape and size the retaining bands for start-transient, overexpansion, and
  gimbal loads") and real-hardware precedent, but no closed-form band-thickness, weld-
  allowable-stress, or splice-geometry equations. The F-1's measured 2.2–2.8 axial / 2.45
  bending stress-concentration factors are real but specific to F-1's own rectangular-band
  geometry, not a general design allowable. 1976 vintage — predates SSME/RS-25, so unlike
  `[Ch12-Materials]` all its real-hardware retaining-band/manifold examples are 1960s Saturn/
  Apollo/ICBM-generation (F-1, J-2/J-2S, H-1, Titan, Atlas), though the failure physics
  itself (weld fatigue, thermal-cycling band buckling, tube-to-band stress concentration,
  turbine-exhaust thermal growth, manifold maldistribution) is geometry/loading-driven, not
  material-era-dependent. **Now fully read as of 2026-09-24** (previously only the retaining-
  bands and vanes/splitters/dams sections were deep-read) — the newly-read manifold-velocity
  criterion (60 fps/Mach 0.25) is still just a stated threshold, not derived, and conflicts
  with `[SP-8087]`'s own 200 ft/s/Mach 0.3-0.5 criterion without either source reconciling
  the difference (flagged above, not resolved). Full extraction scope/section map: `sources/
  sp8120-liquid-rocket-nozzles.md`.
- `[SP-8087]` DOES give several genuinely new dimensioned numbers `[SP-8120]` lacks (heat-flux
  construction-selection thresholds, tube-taper limits, manifold maldistribution tolerance,
  manifold transition-taper length) — but is still 1972-vintage and explicitly pre-advanced-
  channel-wall (its own introduction says high-heat-flux non-tubular fabrication was "in
  development" and "not covered in detail"), and does NOT cover Russian sandwich-wall
  construction (confirmed via full-text search — see `topics/06`'s dedicated paragraph on
  this). OCR quality is mixed: cleanly-typeset criteria text reads well, but several table
  pages are pure scanned-image/graphics with garbled or absent text.
- `[Gubanov-1991]` is a 6-page conference status/policy paper by a real chief designer, not a
  materials or manufacturing source — despite being about Russian engines, it gives **no**
  wall-construction technical detail beyond "brazed-welded unit." OCR is rough (numeric
  tables have jumbled row alignment); the note flags which specific cells (RD-170 Pc,
  RD-0120 nozzle exit diameter) could not be cleanly extracted — don't treat those as
  authoritative, prefer `[Ch12-Materials]`/`[KBKhA]` where the same engine's numbers overlap.
- `[Fagherazzi-2019]`'s manifold/volute content is from a single small-engine (250-400 N)
  master's thesis, one tier below a NASA design-criteria monograph — its correlation
  *choices* and design *process* (volute-sizing method, construction-type comparison) are
  well-sourced and reusable, but its own novel numerical results are a single-team data
  point, not an industry survey.
- `[MatCh2]`'s HEE Index data is an accelerated RT-only (24°C, 34.5-69 MPa H2) laboratory
  screening method, not a design allowable — the source itself warns against using it for
  component design without full fracture-mechanics/crack-growth analysis, and explicitly not
  to extrapolate to high-temperature service. Its LOX/GOX ignition data carries the source's
  own "comparison purposes only, not standard values" caveat — real lot/batch variability
  exists. GRCop-84's composition is given inconsistently within the source itself (see the
  Cu-alloy table note above) — flagged, not resolved.

## Implications for engine_designer

- **`mass_model.py` `t = SAFETY_FACTOR · Pc · r / σ`** is the exact `[Huzel §2.4]` thin-wall
  hoop-stress form. Correct.
- **`mass_model.py` `SAFETY_FACTOR = 1.5`** (ASSUMPTIONS.md item #27): this is precisely
  `[Huzel eq. 2-10]`'s **ultimate load factor = 1.5 × design-limit load**. ASSUMPTIONS.md
  can cite it directly. Note that a fuller treatment multiplies by the design-limit factor
  (1.2× over nominal working load), giving an *effective* factor of ~1.8 over the steady
  operating load — a future refinement could apply `1.5 × 1.2` if the "load" the tool feeds
  is the nominal steady chamber pressure rather than a design-limit pressure.
- **`materials.py` `allowable_stress_pa`** for the modern alloys (ASSUMPTIONS.md items
  #24–26): **this literature set cannot back these** — `[Huzel]` is pre-SSME and has no such
  table. The topic file's honest statement: keep the sources ASSUMPTIONS.md already cites
  (Cal Poly thesis + NASA for NARloy-Z; materials DBs for C-103; NASA GRC for GRCop-84;
  Haynes Intl for Haynes 230), and keep the "derated/interpolated, Tier 3" flag for
  Inconel 718 / stainless / Re-Ir / C-C / Mo-TZM. **2026-09-24**: the new `inconel_x750`
  entry's `density`/`thermal_conductivity_w_mk`/`youngs_modulus_pa`/`cte_per_k`/`emissivity`
  are real cited `[SMC-X750]` numbers (an improvement over the uncited "standard textbook
  figure" tier the other entries in this bucket carry) - only its `allowable_stress_pa`
  stays in the same Tier-3 derated-judgment-call bucket as `inconel_718`'s, since the cited
  yield data sits far above any number this tool would assign as a working allowable.
- **`materials.py` radiation-cool `max_service_temp_k`**: C-103 1650 K, Haynes 230 1400 K,
  Re-Ir 2200 K, Mo-TZM 1950 K, C-C 1900 K — consistent with `[Huzel §4.4]` (Ti/Haynes-25 ≈
  1444 K; Mo-Ti/Ta-W ≈ 1944 K) and `[Sutton]` (C-C loses strength ~3700 K but the tool
  derates it hard for oxidation). C-C's 1900 K in the tool is *very* conservative vs
  Sutton's 3700 K structural limit — defensible because C-C oxidises in any exhaust with
  free O2/OH.
- **`materials.py` `ABLATIVE_CONSUMPTION_RATE_M_S = 1.5e-4` (0.15 mm/s)** (ASSUMPTIONS.md
  item #28): `[Sutton §8.2]` doesn't give a rate but confirms the regime — ablative is for
  low Pc, short duration; **pulsing at 4–15 % duty cycle maximises consumption**. The tool's
  flat, flux-independent rate is a coarse proxy; `[Sutton Fig 8-10]` says a real model would
  make it duty-cycle-dependent (worse for pulsed engines) and the tool's own docstring
  already notes it should scale with heat flux / Pc.
- **`materials.py` thermal-margin heuristic** `assumed_wall_temp = Tc · cooling_effectiveness
  · heat_flux_factor`: the recovery-factor refinement (`Tc · 0.90` instead of `Tc`) from
  `[Huzel §4.4]` (topic 06) applies here too — the tool currently assumes recovery factor
  1.0, ~10 % pessimistic.
- **`controller_tech.py` tested/rated burn-time multiplier** and **`design.py` rated burn
  time**: `[Sutton Fig 8-10]` (pulsing worse than continuous) is relevant background for why
  ablative "tested ≈ rated" (no margin from intermittent operation) while metal chambers get
  a larger tested/rated ratio.
- **`turbopump_materials.py`'s rotor-material catalog**: `[Ch12-Materials]`'s real
  per-engine-generation table above is a candidate source for adding named historical
  entries (Rene 41, alloy 718, MAR-M-246/Waspaloy, single-crystal PW1480, Stellite 21,
  Tens-50/Monel K-500 pump-side alloys) alongside whatever generic tiers the module already
  carries — report-only per this file's own rule; no catalog edit made here. The Cronidur 30
  / Si3N4-ceramic bearing progression and the C/SiC blisk 2000 °F vs. 1200 °F headroom figure
  are also real numbers worth a future look if `turbopump_materials.py` ever models bearings
  or exotic turbine-blade options.
- **`mass_model.py` chamber-liner material assumption**: `[Ch12-Materials]` confirms
  Narloy-Z (SSME) and Cu-3%Cr (Russian designs) as the real hot-wall liner alloys — matches
  the Western chamber-liner convention `[Huzel]`/`[Sutton]` already document (topic 06); no
  new number, just a second independent confirmation.
- **`mass_model.py` `jacket_structure_mass_kg()` / `WALL_CONSTRUCTIONS`**: today this is a
  single flat `mass_factor` add for `tube_wall`/`coax_shell` vs. a zero-add `milled_channel`
  reference (per CLAUDE.md's Layout section) — it has no explicit retaining-band, splice-
  joint, or manifold-structural-support model at all (confirmed: no `retaining_band`/
  `band_spacing`/`splice` sizing logic exists in `mass_model.py`/`design.py`/`cooling.py`
  today, only the terms "tube_wall"/"tube bundle" as a wall-construction *choice*). `[SP-8120]`
  is real design guidance for exactly this gap — a future feature could size a *notional*
  band count/spacing from the "shape bands for start-transient/overexpansion/gimbal loads"
  criterion and add a stress-concentration advisory (warn-don't-block, per CLAUDE.md
  convention #2) modeled on the real F-1 2.2–2.8x factor when `wall_construction ==
  [UPDATE 2026-09-23: now implemented as `physics/hatbands.py` - band spacing marched from a
  first-principles fixed-fixed tube-span bending model (SP-8120 p.29's "unsupported tube
  length" rule), band section sized for hoop tension + thin-ring buckling, flat/tee/hat/
  channel/box sections per Fig. 40, auto flat->stiff escalation; all magnitudes Tier 3 - see
  ASSUMPTIONS.md.] Original note:   "tube_wall"` — but `[SP-8120]` gives no formula to size band thickness/spacing from first
  principles, so any such feature would need its own reverse-solved or first-principles
  derivation, not a value lifted from this source. Report-only here; no code changed.
- **`manifold.py`'s existing `cooling_flow_topology`/`size_jacket_manifolds`/volute-sizing
  approach is now doubly corroborated**: `[SP-8087]` gives a real propellant-class rule
  (storable → common annulus, hydrogen → discrete per-channel circuits) for turnaround-
  manifold topology beyond the tool's current two named topologies, and `[Fagherazzi-2019]`
  independently arrives at the exact same constant-target-velocity `A(θ)=ṁ(θ)/(ρ·v̄)`
  volute-sizing continuity equation the tool already uses. Both are report-only findings
  (no code changed) but meaningfully de-risk the existing design pattern — two independent
  real/near-real sources converge on it rather than it being a one-off choice.
- **`manifold.py`'s target-velocity constant now has two conflicting real-source candidates**
  (`[SP-8120]` full read, 2026-09-24): 60 fps liquid/Mach 0.25 gas (general distribution
  manifold) vs. `[SP-8087]`'s existing 200 ft/s liquid/Mach 0.3-0.5 gas (coolant-jacket-
  passage specifically). Neither source reconciles the difference — a real open question if
  `manifold.py`'s velocity target is ever tightened against a literature source rather than
  its current first-principles constant-velocity approach, which sidesteps the question by
  not needing an absolute target at all. Report-only.
- **Real hot-gas (turbine-exhaust) manifold structural precedent now exists** (`[SP-8120]`,
  above) if `mass_model.py`/a future feature ever sizes turbine-exhaust-manifold structure —
  real omega-joint thermal-growth numbers, a real material-ductility rule (≥20% elongation
  for high-thermal-load hot-gas manifolds), and a real safety-relevant design criterion
  (never use looped-tube turbine-exhaust introduction with storable propellants). See
  `topics/07-dump-cooling.md` for the accompanying F-1 turbine-exhaust film-cooling-extension
  content this pairs with. Report-only — no code changed.
- **Russian "sandwich" wall construction — CORRECTED 2026-09-24**: `[Ch12-Materials]` (this
  file's own primary source, §12.5.2 p.26-28) actually describes it — Cu-Cr liner, corrugated
  sheet-metal divider, brazed outer shell, a real RD-107 application, and a real F-1 Western
  example (Hastelloy-C lower nozzle extension). A six-source dedicated search (`[SP-8087]`,
  `[Gubanov-1991]`, `[Wieseneck-J2]`, `[Fagherazzi-2019]`, `[EUCASS-2023]`,
  `[ChannelWall-IAC19]`) came up empty because it never re-checked this already-distilled
  source; see `topics/06`'s corrected paragraph and `sources/ch12-materials-liquid-
  propulsion.md` for the full detail. The remaining gap is narrower than previously stated:
  no channel/corrugation dimensions or structural formula exist anywhere in `claude_lit` yet
  — a Russian-specific *dimensioned design-criteria* source (not just a materials/
  construction survey) would still be needed for that.
- **`materials.py`'s copper-alloy chamber-liner options now have a real numeric properties
  table**: `[MatCh2 Table 2.6.3]` gives real CTE/thermal-conductivity/yield/UTS/elongation for
  GRCop-84, NARloy-Z, Cu-Cr-Zr, and three other real chamber-liner Cu alloys — the first
  quantitative source for these exact alloys in this reference set (prior sources named them
  but gave no properties). Report-only — no code changed, but a directly-usable citation if
  `materials.py`'s `allowable_stress_pa`/`thermal_conductivity_w_mk` entries for these alloys
  are ever upgraded from their current Tier-3/estimated status.
- **A real, quantified answer to "does Inconel 718 need special heat treatment for H2
  service?"**: `[MatCh2]`'s HEE Index data shows 718 flips from Extreme (NTS 0.46-0.53 @
  1750°F solutionizing) to Small (0.92 @ 1900°F) HEE susceptibility purely from processing
  temperature — directly relevant if `materials.py`/`turbopump_materials.py` ever models
  heat-treatment-condition as a material sub-choice rather than a single flat entry per alloy
  name. Also directly explains `[Ch12-Materials]`'s existing J-2 718-forging anecdote with
  real numbers instead of just a historical note.
- **A real LOX-compatibility red flag for titanium, independent of the tool's existing
  checks**: `[MatCh2]`'s ignition-threshold table shows titanium ignites at essentially any
  pressure in LOX/GOX service — if `materials.py` or any future LOX-wetted-component advisory
  doesn't already exclude titanium from oxidizer-side flow paths, this is a real, citable
  reason to add that check (distinct from titanium's H2-embrittlement/HRE concern on the fuel
  side). Inconel 718's own surprisingly-low 500 psi ignition threshold is a second, separate
  reason 718 isn't an unconditionally safe universal choice. Report-only — no code changed.
- **A currently-unflagged real design tension worth surfacing**: `[SP-8120]`'s explicit
  criterion that manifold/band structural failures are as much a *combustion-instability/
  performance* risk as a structural one (the H-1 dam anecdote: a purely hydraulic/structural
  fix eliminated a measured performance variation) has no counterpart anywhere in the tool's
  `combustion_stability.py`/`injectors.py` advisories — those model acoustic modes and
  injector-pattern stability, not manifold-flow-maldistribution-driven instability. Not
  actionable without a manifold flow model the tool doesn't have; noted for awareness only.
