# claude_lit — distilled rocket-engine design reference

Knowledge extracted from the primary sources in `/home/cory/ksp_config/literature/`,
organised for fast lookup while continuing to build `engine_designer/`. Read this file first,
then jump to the topic file you need. Started from six sources (2026-09-05); five more were
added 2026-09-14; three more added 2026-09-16; eleven more added 2026-09-19/20; ten more
added 2026-09-23 (35 sources total — see `PROVENANCE.md`).

## Why this exists

`engine_designer/ASSUMPTIONS.md` tiers ~40 of the tool's constants as "calibrated estimate"
or "arbitrary-but-reasonable default" — not traceable to a primary source. The project's
standing rule (see `CLAUDE.md` and the spot-check-real-engines memory) is that no
performance / mass / efficiency number is trusted unless it comes from a real analog or
first principles. These notes are the primary-source backing: they turn "I guessed X" into
"Huzel & Huang §4.4 eq. 4-13 gives X."

**These notes are reference, not instructions to change code.** Each topic file ends with an
`## Implications for engine_designer` section naming the real file + constant a value could
back, replace, or add — but proposing no edits. Any actual change still goes through the
tool's plan-mode + spot-check convention.

## Citation key

| Tag | Document | What it's best for |
|---|---|---|
| `[Huzel]` | Huzel & Huang, *Design of Liquid Propellant Rocket Engines*, NASA SP-125, 2nd ed. 1971 | The stepwise design procedure; conical/bell nozzle layout; Bartz; L\* table; four worked engines (A-1…A-4) |
| `[Sutton]` | Sutton & Biblarz, *Rocket Propulsion Elements*, 7th ed., Wiley 2001 | Modern framing; engine cycles; frozen vs shifting equilibrium; combustion-instability Table 9-2; TVC (Ch. 16); real thrust-chamber table (8-1) |
| `[TN-Dump]` | Pavli et al., *Design and Cooling Performance of a Dump-Cooled Rocket Engine*, NASA TN D-3532, Aug 1966 | The one deep treatment of dump cooling; Dittus-Boelter coolant/gas-side correlations; empirical evidence of finite combustion length |
| `[KBKhA]` | Demyanenko et al. (KBKhA), *Turbopumps for Gas Generator and Staged Combustion Cycle Rocket Engines*, AIAA 2005-3946 | Real RD-0110 (GG) vs RD-0124 (staged combustion) side-by-side parameter tables |
| `[SP-8081]` | NASA SP-8081, *Liquid Propellant Gas Generators*, Mar 1972 | Entire document is GG design: hot-streak control, UMR vs hot-core injectors, Table I of real GG parameters |
| `[SP-8107]` | NASA SP-8107, *Turbopump Systems for Liquid Rocket Engines*, Aug 1974 | System-level turbopump design; NPSH; cycle→pump/turbine effects; Tables I–III of real turbopump/pump/turbine data; start/shutdown/Pogo |
| `[CR-128318]` | Nurick (Rocketdyne), *Experimental Investigation of Combustor Effects on Rocket Thrust Chamber Performance*, NASA-CR-128318, Jun 1972 | Real LOX/GH2 impinging-triplet c\*/Isp efficiency data point; single-element cold-flow atomization/mixing correlations; calorimeter heat-flux measurement caveats |
| `[SECA-HT]` | *Heat Transfer in Rocket Engine Combustion Chambers and Regeneratively Cooled Nozzles*, SECA-FR-93-18, Nov 1993 | CFD-methodology report (not a correlation source) — corroborates `[TN-Dump]`'s finite-combustion-length finding; hydrocarbon injector-geometry heat-flux sensitivity caution |
| `[Ch12-Materials]` | Halchak, Cannon & Brown, *Materials for Liquid Propulsion Systems* (book chapter, c.2016) | Real alloy-per-real-engine survey by component (injector/chamber/turbopump/valves/ducts) from Goddard through post-2010s additive manufacturing; selection framework, not a properties handbook; **real Russian sandwich-wall construction detail** (Cu-Cr liner + corrugated-sheet divider + pressure-brazed/"solder-welded" outer shell, RD-107 real application, real F-1/Vulcain Western sandwich examples) |
| `[NK-33-Mod]` | Hulka et al. (Aerojet/Kuznetsov SSTC), *Modification and Verification Testing of a Russian NK-33 Rocket Engine...*, AIAA 98-3361 | Real ox-rich-staged-combustion engine: full Table I performance incl. preburner Pc/MR/Tout, zero-baffle main-chamber stability, real materials, real dry/wet masses |
| `[Bazarov]` | Long, Bazarov & Anderson (Purdue), *Main Chamber Injectors for Advanced Hydrocarbon Booster Engines*, AIAA 2003-3361 | ORSC gas-liquid injector taxonomy; real gas-centered-swirl element efficiency (η_c\*, η_CFv) and sizing method; cold-flow atomization-driver finding |
| `[SP-8120]` | NASA SP-8120, *Liquid Rocket Engine Nozzles*, Jul 1976 | **Fully read 2026-09-24.** Nozzle structural design criteria/practices: tube-wall retaining bands, tube splice joints, manifold vanes/splitters/dams/structural supports, manifold hydraulics, hot-gas (turbine-exhaust) manifold, coolant-return manifold, nozzle attachments; real F-1/J-2/H-1/Titan/Atlas failure-mode-and-fix precedent; the real F-1 turbine-exhaust film-cooled nozzle extension (eps 10:1→16:1, ~25-30%-at-attachment coolant split); real nozzle-configuration criteria (throat radii, separation margin, contour tolerances, plug-nozzle base design) |
| `[Marquardt-5981]` | The Marquardt Corp., *Thrust Chamber Cooling Techniques for Spacecraft Engines*, Vol. I, NAS 7-103 Report 5981, Jul 1963 | Cooling-method selection/feasibility for small spacecraft engines (20–10,000 lbf): regen limiting factors, real Pc/throttle-ratio and min-passage-size numbers, regen→radiation cooled-eps cutoff, jacket-purge/coolant-ranking plumbing notes |
| `[AEDC-J2S]` | Pillow (ARO, Inc.), *Altitude Developmental Testing of the J-2S Rocket Engine in Rocket Development Test Cell (J-4)*, AEDC-TR-70-204, Sep 1970 | Real tap-off-cycle hardware/test data (the only US flight-qualified tap-off engine): series fuel→oxidizer turbine arrangement, solid-propellant turbine starter spin-up, real main-stage c\*/Isp/thrust/MR, idle-mode (restart-settling) performance, real tube-splice count |
| `[SP-8087]` | NASA SP-8087, *Liquid Rocket Engine Fluid-Cooled Combustion Chambers*, Apr 1972 | The dedicated regen-cooling chamber-design monograph: real tube-vs-channel-wall heat-flux/thrust selection criteria, tube taper/thickness/velocity limits, real manifold hydraulic design (maldistribution tolerance, torus philosophies, propellant-class turnaround topology), "double-wall construction" (NASA's Western cousin to Russian sandwich, explicitly NOT the same), six-method throat-reinforcement survey |
| `[Gubanov-1991]` | Gubanov (Chief Designer, Energia), *USSR Main Engines for Heavy-Lift Launch Vehicles: Status and Direction*, AIAA 91-2510, Jun 1991 | Real RD-170/RD-120/RD-0120 spec tables from Energia's own chief designer; tripropellant (RD-701-lineage) concept; honest negative finding — no Russian sandwich-wall construction detail given anywhere |
| `[EUCASS-2023]` | Barredo Juan & López Platero (ISAE-SUPAERO), *Design of the regenerative cooling system for a 4kN LOX/Ethanol student-built liquid rocket engine*, EUCASS 2023-035 | Modern worked 1D regen-channel design tool; real quantified Bartz-calibration-error magnitude (37-42% overprediction uncalibrated); two-phase nucleate-boiling/CHF treatment; closed-form Bartz sigma-correction alternative to Huzel's undigitized chart |
| `[Fagherazzi-2019]` | Fagherazzi, *Design and development of a regenerative cooling for small liquid engines*, Master's Thesis, Università degli Studi di Padova, 2018/19 | The most complete regen-cooling+manifold design methodology in this reference set: five compared Nu correlations, real liner/channel hoop-stress sizing, a volute-manifold sizing method that independently corroborates `manifold.py`'s existing approach, 15-22%-of-inlet-pressure jacket-ΔP rule |
| `[Wieseneck-J2]` | Wieseneck (Rocketdyne), untitled J-2/SSME regenerative-cooling presentation, c.1970 | Real J-2-class vs. SSME-design-point heat-flux anchors; double-wall→tubular→channel-wall construction lineage; real material Pc limits (OFHC copper ~4000 psi, NARloy); 0.1×Pc jacket-ΔP rule |
| `[Merkle-RegenCFD]` | Merkle, Li & Sankaran (Purdue), *Analysis of Regen Cooling in Rocket Combustors*, ~2003-04 | CFD-methodology paper (not a correlation source, like `[SECA-HT]`) — idealized entrance-region conjugate-heat-transfer finding, non-monotonic near-inlet wall temperature |
| `[SP-8109]` | NASA SP-8109, *Liquid Rocket Engine Centrifugal Flow Turbopumps*, Dec 1973 | Real suction-specific-speed design limits (40,000/12,000) and NPSH margin factors by propellant class — direct citations for the pending NPSH feature plan; real impeller tip-speed-by-material/shrouding data; real 20%-critical-speed-margin criterion |
| `[SP-8048]` | NASA SP-8048, *Liquid Rocket Engine Turbopump Bearings*, Mar 1971 | The dedicated bearings monograph (image-scan, no text layer — read via rendered page images): a real, citable bearing DN ceiling (3.0×10⁶ DN) for `turbopump_materials.py`'s previously-unsourced Tier-3 estimate; real achieved-DN fleet data, coolant-lubricity ranking, 440-C baseline material confirmation |
| `[PSU-CoaxAtom]` | Pal, Moser, Ryan, Foust & Santoro (Penn State), *Shear Coaxial Injector Atomization Phenomena for Combusting and Non-Combusting Conditions*, NASA-CR-193339, c.1993 | Real PDPA-measured LOX-core breakup length and drop-size data for a shear-coaxial element; a real "counterintuitive" finding that hot-fire sprays produce larger drops than a matched cold-flow simulant |
| `[NASA-TN-Acoustic]` | Conrad, Bloomer, Wanhainen & Vincent (NASA Lewis), *Interim Summary of Liquid Rocket Acoustic-Mode-Instability Studies at a Nominal Thrust of 20,000 Pounds*, NASA TN, Dec 1968 | A large real parametric screech-suppression test program (LOX/GH2 + earth-storable): real recess-depth/baffle-compartment-size/liner-absorption-coefficient tradeoffs at fine granularity |
| `[J2X-Overview]` | Byrd (NASA MSFC), *The J-2X Upper Stage Engine: From Design to Hardware*, AIAA 2010 | Real modern (2010) GG-cycle J-2S-heritage hardware data: confirms the series-turbine arrangement persisted into a modern redesign, real hydrostatic-bearing/inducer-redesign decisions, third real anchor for the tube-wall-regen + TEG-cooled-extension architecture |
| `[Casiano-Throttling]` | Casiano, Hulka & Yang, *Liquid-Propellant Rocket Engine Throttling: A Comprehensive Review*, AIAA 2009-5540 | The first dense real-engine throttle-ratio/stability catalog in this reference set: LMDE 10:1, CECE 13:1, SSME 6.4:1, RD-170/171 56%/RD-180 40% minimums, RL10A-1 injector-stiffness-vs-chug-onset triplet, small quantified gas-injection chug-suppression fractions |
| `[ChannelWall-IAC19]` | Gradl & Protz (NASA MSFC), *Channel Wall Nozzle Manufacturing Technology Advancements for Liquid Rocket Engines*, IAC-19-C4.3.5x52522 | Modern (2012-2019) AM/water-jet-milling channel-wall manufacturing survey; confirms the Russian-sandwich gap is still open (checked specifically, not the same technology); real Inconel 625/JBK-75 hot-fire wall-temperature test anchors |
| `[Lewis-Deposits]` | Roback, Szetela & Spadaccini (UTRC), *Deposit Formation in Hydrocarbon Rocket Fuels — Executive Summary Report*, NASA CR, 1983 | Real RP-1 coking onset/peak temperature band (600-800K, peak ~700K) and rate data (400-600 µg/cm²·hr), pressure-independence, nickel-plating mitigation (~10× rate reduction) — the first rate/mechanism data behind the single-point coking threshold already cited from `[SP-8087]` |
| `[TP2862-LOXRP1]` | Masters, Armstrong & Price (NASA Lewis), *High-Pressure Calorimeter Chamber Tests for LOX/RP-1 Rocket Combustion*, NASA TP-2862, 1988 | Real calorimeter hot-fire heat-flux data: ~60%-high Bartz/design-tool under-prediction (hardware corroboration of `[EUCASS-2023]`'s CFD finding), measured Pc-scaling exponent, soot-coating h_g knockdown, real 99.5% LOX/RP-1 c\* anchor, zoned-injector 47%-flux/4.5%-C\*-cost film-cooling tradeoff |
| `[MatCh2]` | Multiple authors incl. Bhat, Nathal, Ellis, Lee, Davis (NASA/industry), *Chapter 2: Aerospace Materials Characteristics* (book chapter, c.2016) | Real quantitative Cu-alloy chamber-liner properties table (GRCop-84/NARloy-Z/Cu-Cr-Zr), real Hydrogen Environment Embrittlement Index data by alloy (Inconel 718's heat-treat-dependent HEE flip), real LOX/GOX material ignition-threshold data (titanium/magnesium red flag, Inconel 718's low threshold), real superalloy composition table |
| `[Aerospike-CR135231]` | Diem & Kirby (Rocketdyne), *Linear Aerospike Engine Study, Final Report*, NASA CR-135231, 1977 | Background-only reference for a nozzle type `engine_designer` doesn't model: real MOC spike-contour method, cooling-circuit topology, structural layout, differential-throttling TVC formulas — no base-flow physics or altitude-compensation curve |
| `[STBE-PW]` | Pratt & Whitney, *Space Transportation Booster Engine Configuration Study, Final Report*, FR-19691-4 Vol. II, 1989 | Seven real fully-worked 600-750 Klbf-class booster engine conceptual designs (GG/split-expander/tap-off, LOX/RP-1/CH4): real 7-way propellant trade table, a new "split expander" cycle variant, second real LOX/CH4 tap-off data point, real regen-channel design-rule set recurring across all variants, second real bearing-DN fleet anchor, real applied Helmholtz-liner geometry |
| `[Tripropellant-CR150444]` | Rocketdyne, *Tripropellant Engine Study, Bimonthly Technical Progress Report No. 1*, NASA CR-150444, 1977 | Background-only for an unmodeled dual-mode/tripropellant architecture; independently corroborates the RP-1-cooling-Pc-limit finding and the LOX-rich-vs-fuel-rich-preburner infeasibility rationale already reflected in `cooling.py`/`staged_combustion.py` |
| `[Agena-CR120362]` | Carter et al. (Lockheed Missiles & Space Co.), *Reusable Agena Study, Volume 2: Technical*, NASA CR-120362, 1974 | Mostly vehicle-bus/mission-ops material, low relevance overall; one citable pocket (Bell 8096L propulsion section): a real bomb-test stability acceptance criterion, a hot-pump-restart thermal-margin precedent, a start-system trade study |

Full identity, scope and chapter maps: `sources/*.md`. Page references in the topic files
use the printed page number of the source (`[Huzel §4.4 p.100]`), not the PDF leaf.

## Topic files

| File | Covers | Primary sources |
|---|---|---|
| `topics/01-nozzle-flow-and-performance.md` | Thrust equation, Isp, C\*, C_F, effective exhaust velocity, real-nozzle loss breakdown, altitude effects, separation | `[Huzel]` Ch. I & §4.2, `[Sutton]` Ch. 3 & 5 |
| `topics/02-nozzle-contour-design.md` | Conical λ = ½(1+cos α), Rao parabolic-approximation bell, %-bell definition, θn/θe vs ε, length ratios, aerospike (out of scope, real reference background), real throat-radius/separation-margin/contour-tolerance design criteria, plug-nozzle base-design guidance | `[Huzel]` §4.3, `[Sutton]` §3.4 & §8.2, `[Aerospike-CR135231]`, `[SP-8120]` |
| `topics/03-combustion-and-cstar.md` | C\* efficiency, combustion vs nozzle loss split, frozen vs shifting equilibrium, MR effects, completeness / stay time, real LOX/RP-1 c\* anchor | `[Sutton]` Ch. 5 & 9, `[Huzel]` §4.2, `[CR-128318]`, `[TP2862-LOXRP1]` |
| `topics/04-chamber-sizing.md` | L\* = Vc/At, L\* table by propellant, contraction ratio, stay time, chamber shape, wall area | `[Huzel]` §4.3, `[Sutton]` §8.2 |
| `topics/05-injectors.md` | Types (impinging/doublet/triplet/coax/pintle/platelet/ORSC swirl), ΔP/Pc 15–20 %, Cd 0.5–0.92, β angle, momentum ratio, throttling, real shear-coaxial breakup-length/drop-size data, real throttle-stiffness-vs-chug data, zoned-injector film cooling | `[Huzel]` §4.5, `[Sutton]` §8.1, `[SP-8081]` §2.1.2, `[Bazarov]`, `[CR-128318]`, `[SECA-HT]`, `[PSU-CoaxAtom]`, `[Casiano-Throttling]`, `[TP2862-LOXRP1]` |
| `topics/06-cooling-and-heat-transfer.md` | Bartz h_g (eq 4-13), Dittus-Boelter, recovery factor, regen / film / ablative / radiation, transition ε ~6–10, heat-flux magnitudes, small-engine regen feasibility limits + jacket-purge/plumbing notes, real tube/channel-wall selection criteria, Bartz-calibration-error magnitude (CFD + real-calorimeter corroboration), real RP-1 coking rate/onset data, real regen-channel design rules, Russian sandwich construction NOT found (checked against 6 sources, see topic's dedicated paragraph) | `[Huzel]` §4.4, `[Sutton]` §8.2–8.3, `[TN-Dump]`, `[SECA-HT]`, `[Marquardt-5981]`, `[SP-8087]`, `[Wieseneck-J2]`, `[EUCASS-2023]`, `[Fagherazzi-2019]`, `[Merkle-RegenCFD]`, `[Lewis-Deposits]`, `[TP2862-LOXRP1]`, `[ChannelWall-IAC19]`, `[STBE-PW]` |
| `topics/07-dump-cooling.md` | Dump-cooling concept, coolant-passage sizing method, min coolant fraction, coolant-Isp recovery, refractory-metal potential, real F-1 turbine-exhaust-gas film-cooled nozzle extension | `[TN-Dump]` (whole), `[Huzel]` §4.4, `[Sutton]` §8.2, `[SP-8120]` |
| `topics/08-engine-cycles.md` | GG / tap-off / expander / split-expander / staged combustion / pressure-fed; pump-discharge ≈ k·Pc; turbine PR ~20 vs <1.5; Isp loss; cycle→turbopump stress; real J-2S tap-off hardware/test data; modern J-2X GG-cycle real anchor; real throttle-ratio catalog; tripropellant background | `[Sutton]` §6.6 & Ch. 10, `[SP-8107]` §2.1.1.4, `[KBKhA]`, `[NK-33-Mod]`, `[AEDC-J2S]`, `[J2X-Overview]`, `[Casiano-Throttling]`, `[STBE-PW]`, `[Tripropellant-CR150444]` |
| `topics/09-turbopumps.md` | Ns, suction specific speed / NPSH, tip-speed limits, turbine staging & U/C0, real efficiency & specific-power tables, mass, real suction-specific-speed and bearing-DN design limits (two independent fleet anchors), real expander-cycle turbopump performance data | `[SP-8107]` (whole), `[KBKhA]`, `[Huzel]` Ch. VI, `[Sutton]` §10.1, `[Ch12-Materials]`, `[NK-33-Mod]`, `[SP-8109]`, `[SP-8048]`, `[STBE-PW]` |
| `topics/10-gas-generators.md` | Hot-streak control, fuel-rich MR 0.2–1.0, UMR vs hot-core, stay time 2–10 ms, Tin 800–1200 K, Table I real GGs, materials | `[SP-8081]` (whole), `[Huzel]` §4.6, `[KBKhA]` |
| `topics/11-propellants.md` | Per-pair MR / Tc / γ / M / c\* / Isp anchors, density, hypergolics, monopropellants, frozen vs shifting, real LOX/CH4-RP1-C3H8 7-way trade table | `[Sutton]` Ch. 5 & 7, `[Huzel]` figs 4-3…4-6, `[STBE-PW]` |
| `topics/12-materials-and-structures.md` | Selection framework, hoop-stress wall t = SF·P·r/σ, safety-factor structure (1.5 ultimate), ablative regression, cryo/H2 embrittlement (real HEE index data), real turbopump/chamber alloys by era, real Cu-alloy properties table, real LOX-ignition thresholds, tube-wall retaining-band/splice-joint and manifold structural-support design criteria, real manifold hydraulic design + volute-sizing corroboration, real hot-gas (turbine-exhaust) manifold structural precedent, real manifold-velocity criterion, real RD-170/120/0120 specs | `[Huzel]` §2.4–2.5, `[Sutton]` §8.2–8.3, `[Ch12-Materials]`, `[SP-8120]`, `[AEDC-J2S]`, `[SP-8087]`, `[Fagherazzi-2019]`, `[Gubanov-1991]`, `[MatCh2]` |
| `topics/13-mass-and-budget.md` | Turbopump specific power (hp/lbm → W/kg), equivalent-weight factor, propellant budget, dry-mass scaling | `[SP-8107]` Tables I–II, `[Sutton]` §10.3, `[KBKhA]`, `[NK-33-Mod]` |
| `topics/14-combustion-stability.md` | Chug/buzz/screech frequency bands (Table 9-2), acoustic-mode formulas, baffles (odd count), Helmholtz cavities, Pogo, rating bombs, real 20,000-lbf-class screech-suppression test-program data, real applied Helmholtz-liner geometry, real bomb-test criterion | `[Sutton]` §9.3, `[Huzel]` §4.8, `[SP-8107]` §2.3.2, `[NK-33-Mod]`, `[Bazarov]`, `[NASA-TN-Acoustic]`, `[STBE-PW]`, `[Agena-CR120362]` |
| `topics/15-transients-and-controls.md` | Turbopump time constant, tank-head vs solid-cartridge vs pressurised-gas start, shutdown water-hammer, throttle response, control points, real demonstrated throttle-ratio catalog by engine | `[SP-8107]` §2.3, `[Huzel]` Ch. VII & X, `[Casiano-Throttling]` |
| `topics/16-gimbal-and-tvc.md` | Gimbal vs hinge, ±10.5–12° typical, pitch moment F·L·sin δ, actuator loads/rates, LITVC / jet vanes, alignment | `[Sutton]` Ch. 16, `[Huzel]` §7.5 & §9.6 |

No topic file was folded — the original six sources gave enough for 16 distinct files,
though 07, 13, 15 and 16 are shorter than the physics-core files. The five 2026-09-14
sources folded into existing topic files rather than creating new ones — each is a
real-engine/real-test data point or corroborating source for an existing topic, not a new
subject area.

## How to use these notes

- Working on `engine_designer/physics/<module>.py`? Open the topic file(s) whose table row
  names that module and read the `## Implications for engine_designer` section first.
- Need a real number to anchor a new propellant / cycle / material? The topic files pull the
  literature's own typical-value tables and worked examples verbatim, with page cites.
- Need the derivation or a chart the notes only summarise? The `sources/*.md` file says which
  chapter and PDF leaf to open. A helper for reading the PDFs (pymupdf in a venv) was built
  at `$CLAUDE_JOB_DIR/tmp/` during the extraction session; rebuild it if the job is gone —
  `python3 -m venv v && v/bin/pip install pymupdf`, then `page.get_text()` / `get_pixmap()`.
- Every quantitative claim in a topic file carries a `[Tag §x.y p.NN]` cite. If a number has
  no cite, treat it as the note author's synthesis, not the source's.
- Wondering what's still unresolved, or which `ASSUMPTIONS.md` constants now have a real
  citation waiting to be applied? Check `OPEN_QUESTIONS.md` before starting new work.

- **Lookup budget — read sections, not files.** `grep -n` the term across `topics/`, then read
  only the matching `##` section (Read with offset/limit); read a whole topic file only as a
  fallback. Go to a `sources/*.md` note only when the topic file lacks the detail, and to a raw
  PDF only when distilling a new source — never for a routine lookup.
- **Ignore `literature/duplicates/`.** It holds md5-confirmed byte-identical copies of PDFs
  already distilled under another filename; never diff, distill or cite from it.
- **Topic-file size cap: 40 KB.** When an addition would push a `topics/*.md` file past it,
  split it into sub-topic files, update the table above, and grep the repo for the old
  filename (code comments, `ASSUMPTIONS.md`, `sources/*.md` link to topic files by name).
- Extraction dates/methods and the cross-check history live in `PROVENANCE.md` (moved out of
  this index 2026-09-22 so every lookup's first read stays small).
