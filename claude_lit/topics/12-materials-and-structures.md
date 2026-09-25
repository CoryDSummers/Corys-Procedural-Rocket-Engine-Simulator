# 12 — Materials and structures

## Scope

Material selection framework, high-temperature allowable stress, the wall thickness /
hoop-stress calculation, the safety-factor structure, and ablative regression. Feeds
`engine_designer/physics/materials.py` and `mass_model.py`. **Split 2026-09-24** (this file
exceeded the 40 KB lookup-budget cap): real structural design criteria and real-hardware data
for tube-wall retaining bands, propellant/coolant manifolds, tube-splice joints, nozzle
attachments, and turbine-exhaust manifolds now live in `topics/12b-structures-manifolds-and-
hardware.md` — this file keeps material selection, alloy properties, fatigue/embrittlement/
ignition data, and ablative/radiation material criteria.

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

**Inconel X-750 physical/thermal/mechanical properties** `[SMC-X750 Tables 2/3/5/13]`: the
alloy `[SP-8120]` names (alongside Inconel 718) as a real hatband material
(`topics/12b-structures-manifolds-and-hardware.md`) now has a citable properties source for
`materials.py`'s `inconel_x750` entry. Density 8.28 g/cm³ (8280 kg/m³); melting range
1393-1427°C; oxidized-surface emissivity 0.895 at 600°F rising to 0.925 at 2000°F (a real
cited figure, unlike `inconel_718`'s uncited 0.7 estimate). Thermal conductivity 83
Btu·in/(hr·ft²·°F) at 70°F (11.97 W/(m·K)), rising to 143 at 1200°F; mean CTE (from 70°F)
7.8e-6/°F at 800°F (1.40e-5/K); static-tension Young's modulus 31.0e3 ksi at 80°F
(2.14e11 Pa). Real cited yield strength (Table 13, solution-treated + furnace-cool
precipitation-treated - the condition aimed at real service strength rather than spring
temper) is 845 MPa at 1200°F and 530 MPa at 1500°F - both far above any working allowable
this tool would assign, matching `inconel_718`'s own already-heavily-derated
`allowable_stress_pa`. No table gives a strength value at the alloy's own claimed 1800°F
oxidation-resistance ceiling (only creep/rupture/fatigue curves extend that far) - the same
"real data stops short of the tool's max_service_temp_k" situation `inconel_718`'s
ASSUMPTIONS.md entry already flags. See `sources/smc067-inconel-x750.md` for full tables.

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
partial main-fuel-valve-housing coating. **RESOLVED 2026-09-24**: this source's own Table
2.6.3 gives GRCop-84's composition as Cu-6.7Cr-5.9Nb while its own §2.8 HEE table (below)
labels the same alloy Cu-8Cr-4Nb — not an internal inconsistency after all.
`[GRCop84-TM2005 Executive Summary p.1]` (the primary NASA source for this alloy) gives the
composition as **Cu-8 at.% Cr-4 at.% Nb** (atomic percent — literally where the "84" in
GRCop-84 comes from); converting to weight-% gives Cu-6.52Cr-5.83Nb, matching `[MatCh2]`'s
"Cu-6.7Cr-5.9Nb" to within ~0.2-0.3 percentage points. The two numbers were always the same
alloy in two different unit conventions.

**GRCop-84 real temperature-dependent tensile properties — a strong citation-upgrade
candidate (2026-09-24)** `[GRCop84-Tensile Tables 3-4]`: a genuine multi-specimen statistical
tensile program (5 independent powder lots, extruded AND HIPed, cryo 20-77K through ~1200K,
real least-squares regressions with 95%-CI terms). As-extruded baseline (mean regression):

| T (K) | Yield (MPa) | UTS (MPa) | Elongation % |
|---|---|---|---|
| 20 (LH2) | 291.3 | 644.9 | 17.8 |
| 77 (LN2) | 275.1 | 590.8 | 19.3 |
| 293 (RT) | 226.9 | 408.4 | 21.4 |
| 400 | 207.4 | 331.3 | 20.9 |
| 600 | 170.4 | 210.9 | 18.9 |
| 800 | 122.7 | 121.3 | 17.6 |
| 1000 | 52.3 | 62.5 | 19.1 |

(Full regressions: yield σ=297.4−0.312T+3.175e-4T²−2.506e-7T³ MPa; UTS σ=664.5−0.987T+
3.850e-4T² MPa, T in K. HIPed condition is systematically lower at low/mid T, converging with
extruded by ~900-1000K — no cryogenic data for HIPed, don't extrapolate below 293K.) **The
report's stated core advantage over NARloy-Z/Cu-Cr/Cu-Zr/Cu-Cr-Zr**: a braze/diffusion-bond
cycle (935-1000°C) knocks GRCop-84's yield down only ~10-15%, fairly flat cryo-to-600°C — by
contrast, unpublished P&W Rocketdyne data shows NARloy-Z loses "almost half" its strength from
the same cycle, since GRCop-84's Cr2Nb dispersion strengthening survives a braze cycle that
destroys precipitation strengthening. Long-term high-T exposure (500-1000°C, up to 6000 min):
strength actually INCREASES at 500°C (secondary Cr precipitation); even at 1000°C exposure,
"minimal loss in properties." Cold work adds up to +50% yield at RT but anneals out by
200-600°C — not a viable strengthening lever for a hot-wall liner. Real drawn-tubing RT data
(directly relevant to `WALL_CONSTRUCTIONS.tube_wall`): tube drawing does not degrade
properties vs. as-extruded (avg yield 245.7 MPa, UTS 420.0 MPa, elongation 22.8%). This is a
genuine candidate to upgrade `materials.py`'s currently Tier-3 GRCop-84 `allowable_stress_pa`
from an estimate to a cited temperature-dependent curve — report-only, no code changed.

**OFHC-copper low-cycle-fatigue (LCF) method + a real applied result** `[Miller-CuFatigue
§Fatigue Life Analysis eq.2 p.42; §Results p.39, 46]` — directly hits `mass_model.py`'s throat
low-cycle thermal-fatigue estimate, which currently has no cited method: the Manson Universal
Slopes equation, given in full, `Δε_t = (3.5·σ_u/E)·N̄_f^-0.12 + [ln(1/(1-RA))]^0.60·N̄_f^-0.60`
(general to any ductile metal, using short-term tensile σ_u/E/RA at the temperature of
interest), with an elevated-temperature derating factor "average life" = N̄_f/5 (cited to
Manson & Halford, NASA TM-X-52270 1967). **A real applied case**: a real regen OFHC-copper
LH2/LOX chamber throat, computed peak strain range 2.46% → predicted life 80 cycles vs.
**actual observed through-crack failure at cycle 39** — a real ~2x unconservative prediction,
explicitly framed by the source as within normal fatigue scatter, a useful order-of-magnitude
uncertainty anchor for any LCF-derived design margin. **A real, directly relevant finding**:
peak strain range and peak wall temperature were NOT co-located in that same test article (the
hottest element ran only ~521°C locally while the true 2.46%-peak-strain element saw only
970°F/521°C — coolant-vs-chamber pressure-differential bending redistributed plastic strain
toward the rib base) — if `mass_model.py`'s thermal-fatigue estimate ever infers fatigue risk
from a single hottest-wall-temperature station, this real example shows that proxy can miss
the true worst point. Cyclic hardening of annealed OFHC copper ≈30% stress increase over the
monotonic curve at 3% strain, 538°C. Caveat: pure annealed OFHC copper only (no NARloy-Z/
GRCop-84/Cu-Cr-Zr), one real test article (not a statistical dataset), method + one data
point, not a handbook curve; hold-time damage (relevant to longer-burn engines than this
report's ~2-second-pulse test article) is explicitly flagged unaddressed.

**Real chamber-liner life-enhancing design concepts, seven real approaches** `[Quentmeyer-
CR185257]` — a survey of hardware-tested life-extension techniques for a regen chamber liner,
distinct from (and complementary to) the alloy-selection framing above. **Thermal barrier
coating (TBC), the headline quantified result**: ZrO2 (0.076mm)+NiCr bond coat on an
electroformed-Cu liner survived **1450 cycles with no damage vs. 393 cycles for an uncoated
Amzirc liner** at the same geometry/conditions (caveat: substrate material also differs, not a
clean single-variable A/B); TBC cuts heat flux ~50% `[§Thermal Barrier Coatings p.3]`.
**Tungsten-reinforced liner**: W wire in a thin Cu wall → thermal conductivity only ~10% below
OFHC Cu, rupture strength ~80% higher than NARloy-Z at 867K, no damage after 400 cycles
`[§Tungsten-Reinforced Chamber Liner p.4]`. **High-aspect-ratio channels**: increasing channel
count 72→400 at the same coolant flow dropped throat wall temp 777K→444K; platelet-formed
liners achieved aspect ratio up to 15 `[§High-Aspect-Ratio Cooling Passages p.5, §Platelet-
Formed Chamber Liner p.8]`. **Low-stiffness closeout**: a sintered-Al+PTFE compliant layer
between liner and structural jacket gives an analytical (not tested) 3x life-enhancement
factor vs. a conventional Ni closeout `[§Low-Stiffness Closeout p.6]`.

**Manufacturer alloy datasheets — real primary properties for four alloys already named in
this file (2026-09-24)**: **304/304L stainless** `[SS304-TDS]` (not currently in
`materials.py`'s catalog — a candidate if a low-cost structural stainless entry is ever
added): RT UTS 90 ksi (620 MPa), CTE 16.6e-6/K, k=16.3 W/(m·K), no cold-embrittlement cliff
(Charpy toughness actually rises at cryo temps). **321/347/348 stainless** `[SS321-TDS]` — the
higher-value grades, since these are the turbine-exhaust/hot-gas-manifold alloys already named
via `[Ch12-Materials]`'s "347 CRES" F-1 citation above, now with real numbers behind that
name: max ASME code-use temp **1500°F (816°C)** vs. plain 304L's 800°F — the entire reason the
stabilized (Ti- or Cb+Ta-stabilized) grades exist; also resist polythionic-acid SCC where
unstabilized 304 sensitizes/cracks; 347/348 notably stronger than 321 at every temperature
(RT UTS 93.25 ksi vs. 321's 85 ksi). **Inconel 718** `[Inc718-TDS]` — real UTS/YS cliff
between 1200°F (1134 MPa) and 1300°F (1003 MPa), a ~12% drop over 100°F quantifying the
alloy's practical ~1300°F ceiling; cryogenic UTS RISES from RT to LH2 temp with ductility
maintained (no cryo embrittlement). **Explicit cross-check**: a full-text search of this
28-page datasheet for "hydrogen"/"embrittl" returned zero matches — it has NO HEE data
whatsoever, purely mechanical/thermal/physical properties; `[MatCh2]`'s HEE-index data above
remains the sole H2-embrittlement citation for 718. **Nickel 200/201** `[Ni200-TDS]` — real
cryogenic tensile data (UTS nearly doubles RT→LH2 temp with high ductility retained); Nickel
200 graphitizes 800-1200°F (not recommended in that range), Nickel 201 (low-C) resists
graphitization and is ASME-approved to 1250°F — the real reason two grades exist. **Important
disambiguation flagged by the fork that wrote this note**: this datasheet's own "hydrogen"
mentions are all chemical-corrosion-resistance context (dry-H2 annealing atmosphere), NOT
mechanical HEE data — `[MatCh2]`'s own table says pure nickel/Ni-rich alloys are *severely*
HEE-embrittled, the opposite implication from this datasheet's generally favorable corrosion
tone. **Do not conflate corrosion resistance with H2-embrittlement resistance for nickel** —
they are different mechanisms with different (in this case opposite-sounding) verdicts.

**Real self-cooled-chamber ablative and radiation-cooled material criteria — `[SP-8124]` full
read, 2026-09-24** `[SP-8124 §2.1/§3.1 (ablative), §2.2/§3.2 (radiation-cooled)]`: a genuinely
new, dimensioned set of design criteria complementing this file's existing Ablatives/
Radiation-cool bullets above. **Ablative**: silica/quartz surface-temperature limit **3000°F**
(to 3400°F under special conditions); a throat insert is required above **Pc>300 psi**;
insert material selection by temperature band (SiC/JTA ≤3600°F for <1000 lbf engines,
molybdenum w/ silicide coating for larger engines, pyrolytic graphite washers >3600°F); real
throat-insert geometry ratios (thickness/ID 0.2-0.3, length/thickness ≤6); a **1.25 char-depth
safety factor**; structural-shell temperature limits by material (titanium/stainless 800°F,
aluminum 350°F); fiberglass structural safety factors 1.5-1.8 vs. metal shell 1.25-1.5.
**Radiation-cooled**: columbium (C-103) recommended over 90Ta-10W/molybdenum; wall must
exceed ~2200°F for radiative balance; silicide coating limits 2800°F/1hr (3100°F/10min),
aluminide coating 2400°F (2800°F ceiling), coating thickness ≤8 mils; real emissivity data
(coated 0.75-0.85, bare refractory 0.2-0.4, V-grooved-uncoated 0.8) — extends this file's
existing anodized-aluminum emissivity numbers (0.1→0.9); real sublimation-rate data
(0.8%/hr@2600°F, 4%/hr@3000°F); real embrittlement/brittle-fracture hardware findings (SCb-291/
C-129Y embrittle, C-103 doesn't; molybdenum's ~70°F ductile-brittle transition causes real
pulsed-operation failures — a real, citable reason to avoid Mo for a pulsing radiation-cooled
design specifically, distinct from its high-temperature capability).

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
- `[Gubanov-1991]` is a 6-page conference status/policy paper by a real chief designer, not a
  materials or manufacturing source — despite being about Russian engines, it gives **no**
  wall-construction technical detail beyond "brazed-welded unit." OCR is rough (numeric
  tables have jumbled row alignment); the note flags which specific cells (RD-170 Pc,
  RD-0120 nozzle exit diameter) could not be cleanly extracted — don't treat those as
  authoritative, prefer `[Ch12-Materials]`/`[KBKhA]` where the same engine's numbers overlap.
- `[MatCh2]`'s HEE Index data is an accelerated RT-only (24°C, 34.5-69 MPa H2) laboratory
  screening method, not a design allowable — the source itself warns against using it for
  component design without full fracture-mechanics/crack-growth analysis, and explicitly not
  to extrapolate to high-temperature service. Its LOX/GOX ignition data carries the source's
  own "comparison purposes only, not standard values" caveat — real lot/batch variability
  exists. GRCop-84's composition mismatch vs. `[GRCop84-TM2005]` is now RESOLVED (see above)
  — was a unit-convention difference (at.% vs. wt.%), not an error.
- `[GRCop84-Tensile]`'s table above uses the mean regression (t-term=0), not the true
  lower-95%-CI design-minimum (~10-20 MPa lower on yield); braze-cycle-adjusted curves exist
  in the source but weren't fully reproduced numerically here. OCR was badly garbled for the
  two pages carrying the primary baseline regression equations (re-rendered as images and
  read visually for reliable coefficients) — secondary regressions (braze/rolled-plate/
  large-extrusion variants, ~30 more equations) were captured from OCR text only, not
  image-verified, so treat those specific numbers as lower-confidence than the baseline table.
- `[Miller-CuFatigue]` is pure annealed OFHC copper only (no NARloy-Z/GRCop-84/Cu-Cr-Zr), one
  single real test article — a method + one real data point, not a general design-allowable
  curve. `[Quentmeyer-CR185257]`'s seven life-enhancing concepts are likewise single-test-
  article comparisons that often confound multiple variables (substrate + coating changed
  together in the TBC case) — real, citable data points, not general design curves.
- The four manufacturer datasheets (`[SS304-TDS]`/`[SS321-TDS]`/`[Inc718-TDS]`/`[Ni200-TDS]`)
  are primary manufacturer references, but two (Special Metals Inc718/Ni200) have scrambled
  table cell-ordering in their raw text layer that required manual reconstruction against
  stated headers/footnotes — treat as reconstructed-but-verified, not a direct transcription.
- `[SP-8124]`'s ablative/radiation-cooled material criteria above are a scoped read (§2.1/§2.2/
  §3.1/§3.2 only, out of a 138-page monograph) — its cooling-architecture content (film-
  cooling model, interregen/heat-sink chambers) is in `topics/06b-cooling-methods-and-
  chemistry.md` instead; see that file's caveats for the source's overall extraction-scope
  limits.

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
- **Russian "sandwich" wall construction — CORRECTED 2026-09-24**: `[Ch12-Materials]` (this
  file's own primary source, §12.5.2 p.26-28) actually describes it — Cu-Cr liner, corrugated
  sheet-metal divider, brazed outer shell, a real RD-107 application, and a real F-1 Western
  example (Hastelloy-C lower nozzle extension). A six-source dedicated search (`[SP-8087]`,
  `[Gubanov-1991]`, `[Wieseneck-J2]`, `[Fagherazzi-2019]`, `[EUCASS-2023]`,
  `[ChannelWall-IAC19]`) came up empty because it never re-checked this already-distilled
  source; see `topics/06b-cooling-methods-and-chemistry.md`'s corrected paragraph and
  `sources/ch12-materials-liquid-propulsion.md` for the full detail. The remaining gap is
  narrower than previously stated: no channel/corrugation dimensions or structural formula
  exist anywhere in `claude_lit` yet — a Russian-specific *dimensioned design-criteria*
  source (not just a materials/construction survey) would still be needed for that.
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
- **`materials.py`'s GRCop-84 `allowable_stress_pa` now has a strong real citation-upgrade
  candidate**: `[GRCop84-Tensile]`'s cryo-through-1000K yield/UTS regression (above) is a
  genuine statistical multi-specimen program, not an estimate — a natural next step if this
  Tier-3 entry is ever upgraded. Also real: GRCop-84's braze-cycle strength retention (~85-90%)
  vs. NARloy-Z's (~50%) is a citable quantitative reason to prefer GRCop-84 specifically for a
  brazed/diffusion-bonded liner design. Report-only — no code changed.
- **`mass_model.py`'s throat low-cycle-fatigue estimate now has a real, citable method**:
  `[Miller-CuFatigue]`'s Manson Universal Slopes equation (above) is directly usable if that
  estimate is ever formalized past its current flat/estimated form — plus a real cautionary
  finding (peak strain and peak wall temperature don't co-locate in a real chamber) relevant
  if the fatigue estimate ever infers risk from a single hottest-station temperature proxy
  rather than a full strain-field solve. Report-only — no code changed.
- **Chamber-liner life-extension techniques** (`[Quentmeyer-CR185257]`'s TBC/tungsten-
  reinforced-liner/high-aspect-ratio-channel/low-stiffness-closeout concepts, above) are real
  but currently unmodeled design levers beyond alloy choice alone — none has an obvious single
  constant to cite into `materials.py` today (each is a construction-level choice, not a
  material property), flagged here as candidate future-feature material if chamber-liner
  life/reliability modeling is ever extended beyond a flat fatigue-cycle estimate.
- **Four new manufacturer-datasheet alloys are candidate `materials.py` catalog entries**:
  304/304L stainless (`[SS304-TDS]`, not currently in the catalog at all), 321/347/348
  stainless (`[SS321-TDS]`, real numbers now back the "347 CRES" name already used for the F-1
  hot-gas manifold), Inconel 718 (`[Inc718-TDS]`, confirms/extends the existing entry's
  mechanical properties — but adds NO HEE data, so the existing `[MatCh2]`-sourced HEE citation
  stays the sole source for that concern), Nickel 200/201 (`[Ni200-TDS]`). Report-only — no
  catalog edit made here.
- **`materials.py`'s `ABLATIVE_CONSUMPTION_RATE_M_S` and ablative-material `max_service_temp_k`
  now have real dimensioned NASA design criteria to check against**: `[SP-8124]`'s silica/
  quartz 3000°F limit, Pc>300psi throat-insert threshold, and 1.25 char-depth safety factor
  (above) are all real numbers the tool's current flat/estimated ablative model doesn't use.
  Similarly, `[SP-8124]`'s radiation-cooled coating-limit data (silicide 2800-3100°F, aluminide
  2400-2800°F) is a real citation candidate for any future radiation-cooled coating model.
  Report-only — no code changed.
