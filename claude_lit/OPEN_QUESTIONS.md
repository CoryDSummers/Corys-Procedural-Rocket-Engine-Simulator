# claude_lit — open questions and pending citation upgrades

This file tracks **live open items only**: literature gaps still unfilled and citation
upgrades still unapplied. It is not a history log (that's `PROVENANCE.md`)
and not a per-source note (that's `sources/*.md`). Check it before starting new literature
extraction work, or before trusting/tweaking an `engine_designer/ASSUMPTIONS.md` constant.

When an item here gets resolved (a gap gets filled by a new source, a citation gets applied
to `ASSUMPTIONS.md`), move it out of this file and into the relevant `PROVENANCE.md`
entry or `ASSUMPTIONS.md` line — this file should shrink over time, not just grow.

Scope note: this file covers `claude_lit`/literature matters only. It says nothing about
other, unrelated `engine_designer` work that may be happening in parallel sessions (mass
model, gas generator, manifold-plumbing feature work, etc.) — this session has no visibility
into that and makes no claims about it.

## Housekeeping

- **Two topic files now well exceed `README.md`'s documented 40 KB lookup-budget cap**,
  after the 2026-09-23 batch's additions and the 2026-09-24 SP-8120 deep-read integration:
  `topics/06-cooling-and-heat-transfer.md` (~52 KB) and `topics/12-materials-and-structures.md`
  (~48 KB). `README.md`'s own convention says to split an over-cap file into sub-topic files
  and update the index + cross-references — not done yet, now overdue (deferred twice
  deliberately rather than risking a rushed cross-reference update under time pressure — this
  should be the next housekeeping task, not deferred a third time). Natural split candidates:
  topic 06 could separate "real construction-type/manifold/structural" content from
  "heat-transfer correlations/Bartz" content; topic 12 could separate "turbopump/chamber alloy
  surveys" from "structural criteria (retaining bands, manifolds, hoop stress, hot-gas
  manifold)". Whoever does this should grep the repo for both filenames first (code comments,
  `ASSUMPTIONS.md`, other `sources/*.md`/
  `topics/*.md` cross-references) before renaming anything.

## Open literature gaps

- **Oxidiser-rich preburner temperature at high Pc (RD-170/180, Raptor ox side) — OPEN
  (2026-09-23).** `staged_combustion.py` now SOLVES the turbine PR from a preburner
  temperature input, and the only sourced ox-rich value is NK-33's **628 K**
  `[NK-33-Mod Table I]` (which also reproduces RD-0124's 29.98 MPa turbine inlet
  `[KBKhA]`). At 628 K an RD-180-class (26.7 MPa) ORSC and a 30 MPa FFSC ox side do not
  close (need ~>730 K); `validate.py` sets **800 K, unsourced**, for those two cases. Wanted:
  a real RD-170/RD-180/RD-191 or Raptor ox-rich preburner outlet temperature and preburner
  pressure (plus ideally turbine PR), to replace the 800 K estimate and check the solved
  preburner/Pc (~2.16 at 800 K). Also useful: NK-33 pump/turbine efficiencies, since the
  tool comes out 18 % low on NK-33 preburner/Pc (1.81 vs 2.21).

- **Russian "sandwich" wall construction — PARTIALLY RESOLVED (2026-09-24), narrowed to a
  dimensioned-design-criteria gap.** A six-source dedicated search (`[SP-8087]`,
  `[Gubanov-1991]`, `[Wieseneck-J2]`, `[Fagherazzi-2019]`, `[EUCASS-2023]`,
  `[ChannelWall-IAC19]`) came up empty across two rounds, but that search never re-checked
  `[Ch12-Materials]` — already in `claude_lit` since an *earlier* batch (2026-09-14), before
  this question was first asked. It turns out to have real construction detail: Cu-Cr inner
  liner, **corrugated sheet-metal divider**, brazed outer shell (alloy steel/stainless/
  Ni-base), the corrugations forming coolant passages; joining method is a post-WWII
  **pressure-brazing** technique ("solder-welding" in Russian usage), replacing an
  originally-bolted (leaky) 1930s design; real application named — RD-107-class engines use
  it for the expansion nozzle specifically. Also surfaced: the **F-1's lower nozzle
  extension is itself sandwich construction** (Hastelloy-C), so the technique isn't
  exclusively Soviet. See `topics/06-cooling-and-heat-transfer.md`'s corrected paragraph and
  `sources/ch12-materials-liquid-propulsion.md` for the full detail and exact quotes.
  **What's still missing** (the narrowed remaining gap): no channel/corrugation pitch,
  height, or wall-thickness numbers, no cross-section dimensions, no structural/thermal
  formula — `[Ch12-Materials]` gives the construction concept and materials, not dimensioned
  design criteria the way `[SP-8087]` does for tube/channel-wall. **Resolving the remaining
  gap still needs a Russian-specific (or Volvo/Vulcain-specific) dimensioned design source**
  — a US design-criteria monograph or a Russian program-status/policy paper won't have it.
  **Process lesson**: when a new "search for X across the literature" question comes up,
  check it against *already-distilled* sources too, not just newly-added ones — a keyword
  search across existing `sources/*.md` notes (or the original PDFs) would have caught this
  immediately instead of two rounds later.
- **NASA SP-8124**, *Liquid Rocket Engine Self-Cooled Combustion Chambers* (Sep 1977) — cited
  by `[EUCASS-2023]`'s gaseous-film-cooling model (its Appendix B specifically) but not
  itself in `literature/` or `claude_lit/`. This is the primary NASA film-cooling design-
  criteria monograph (parallel to `[SP-8087]` for regen cooling) and is currently only known
  second-hand through one paper's citation of one appendix. Worth acquiring if film-cooling
  design criteria are ever needed in depth. **Now needed (2026-09-23)**: it is the top
  acquisition for the turbine-exhaust feature below, as the source of film-effectiveness
  correlations for a gaseous turbine-exhaust film on a nozzle extension. **Needed twice over
  (2026-09-23, later)**: `engine_designer` now models film at TWO sites (chamber curtain +
  a post-jacket liquid-fuel nozzle-extension slot, `cooling.film_effectiveness_profile` /
  `nozzle_film_effectiveness_profile`) with Tier-3 constants (eta_f0 = min(0.75, 7f),
  decay 2.5 x local diameter, product combination) — SP-8124's correlations would let
  both be anchored instead of estimated.
- **`[Huzel Fig 4-24]`** (the Bartz `σ` boundary-layer-property-variation correction chart) —
  referenced repeatedly across `topics/06-cooling-and-heat-transfer.md` but never digitized
  from the source PDF. `[EUCASS-2023]`'s Eq. 5 gives an alternative closed-form `delta`
  correction that may already cover this need for `cooling.py` — **check that first** before
  spending effort rendering/transcribing the original Huzel chart.
- **Coolant-side h_c for the coupled throat wall balance (added 2026-09-23)** — `cooling.coolant_side_htc` is plain Dittus-Boelter on fixed, near-room-temperature coolant properties (`COOLANT_TRANSPORT`, RP-1 mu 7.5e-4 Pa.s). Since the chamber margin now uses a coupled balance (`ASSUMPTIONS.md`, `solve_wall_balance` row), h_c directly sets the wall temperature, and the SSME-class check reads its coolant-side wall ~120 K warmer than `[Wieseneck-J2]`'s 478 K. Wanted: (1) bulk-temperature-dependent RP-1 viscosity/conductivity at jacket pressure (no source in the set yet); (2) a wall-to-bulk property correction (Sieder-Tate / Gnielinski, `[Fagherazzi-2019 §2.4.5]`, already in hand) — then re-check the `GAS_SIDE_DEPOSIT_FACTOR` F-1 cross-check, which currently absorbs any h_c error. Nucleate boiling (`[EUCASS-2023]` Chen/Tong) is NOT the answer for RP-1 regen: the jacket runs far above RP-1's ~2 MPa critical pressure.
- **`[Sutton §8.3]`** (coolant-side channel-design treatment, leaves 323-334) — still unread.
  The last remaining piece needed for a real `milled_channel` structural-stress formula
  (`tube_wall` and `coax_shell` now have real Huzel-sourced formulas, added in the
  2026-09-17 batch — see `topics/06`'s "Tube-wall structural design" section).
- **`[SP-8087]`'s own unread §2.1.5/§3.1.5** (Structural Analysis: buckling, composite loads,
  tube compressive/fatigue strength) — flagged in its own source note
  (`sources/sp8087-fluid-cooled-chambers.md`) as the most likely place to find a real
  band-stress-allowable or tube-fatigue formula, if `[SP-8120]`'s qualitative retaining-band
  criteria (`topics/12-materials-and-structures.md`) are ever turned into a real check.
- **`[SP-8048]`'s unread §2.2/§3.2** (bearing component/race/cage design — ~85% of that
  84-page monograph; only ~15 pages were rendered/read this round, targeted at DN-limit and
  materials content specifically since it's an image-only scan with no text layer). Most
  likely place to find a real bearing-bore/shaft-diameter sizing formula, if one exists
  anywhere in this monograph — `turbopump_sizing.py`'s `shaft_diameter_m()`/
  `BEARING_BORE_OVER_SHAFT_FACTOR = 1.15` remain unconfirmed by any source so far.
- **`[SP-8109]`'s unread Housing (§2.4/§3.4, diffuser/volute/casing) and Thrust Balance
  System (§2.5/§3.5) sections** — only ~40% of this monograph was deep-read this round
  (Speed and Impeller sections). Housing/volute design criteria could add further real
  manifold-adjacent numbers alongside `[SP-8087]`'s existing manifold content.

- **Manifold sizing numbers (2026-09-22 re-anchoring round)** — the manifold velocities are
  now tied to cited PRINCIPLES (`[SP-8087 §2.1.2.1/§3.1.2.1]` constant-area vs constant-
  velocity torus + "lie between them"; `[Fagherazzi]` no abrupt volute-to-channel velocity
  change; `[SP-8087 §3.1.1.5.3]` 61 m/s liquid-coolant limit), but four NUMBERS are still
  Tier 3 and each has a named source type that would pin it:
  (a) a real **manifold velocity-head / injector-dP ratio** (`manifold_velocity_head_fraction`
  = 0.04) — look for injector-manifold design criteria (Huzel & Huang SP-125's injector
  chapter wasn't searched for this; `[SP-8109]`'s unread Housing/volute §2.4/§3.4 above is the
  other candidate). **Update 2026-09-24**: `[SP-8120]`'s full read added a THIRD, more
  conservative real velocity criterion (60 fps liquid/Mach 0.25 gas, `§3.2.5.1`) that
  actively conflicts with `[SP-8087]`'s 200 ft/s/Mach 0.3-0.5 — still no velocity-head/dP
  ratio number from either source, and now two unreconciled absolute-velocity numbers instead
  of one; (b) the **taper blend** (0.5) and far-side floor (0.15) — a real torus
  drawing with inlet and far-side bores (J-2/F-1 thrust-chamber manifold drawings,
  heroicrelics.org detail pages); (c) the **J-2's real fuel-inlet-manifold area ratio**
  (`jacket_inlet_eps` default 8) and its **manifold bore** — the J-2 engine manual / R-3825
  would have both; would also give a real J-2 jacket dP for `validate.run_two_pass_cooling_
  check`'s currently-wide [0.2, 5] MPa band; (d) **LH2 speed of sound at jacket conditions** —
  needed to apply SP-8087's gas criterion (Mach 0.3 recommended / 0.5 max) to LH2 manifolds
  instead of skipping the check; any NIST-style parahydrogen property table.
- **Warm-GH2 density in regen hydrolox injector-feed rings** — the fuel reaching a regen
  hydrolox engine's injector manifold is warm hydrogen GAS after the jacket, but `manifold.py`
  sizes every fuel ring at liquid LH2 density (71 kg/m^3), so that ring's bore/velocity is off
  in an unknown-magnitude direction (same mdot at much lower density -> bigger bore at a fixed
  velocity, or much higher velocity at a fixed head). Needs a jacket-outlet hydrogen
  temperature/density source (no hydrogen injection temperature exists in `claude_lit` - checked
  2026-09-22) plus a real-gas property model; out of scope for the re-anchoring round.
- **Turbine-exhaust handling: IMPLEMENTED 2026-09-24** (`engine_designer/physics/
  turbine_exhaust.py`).
  - Modes: overboard duct (with an optional shaped / canted exhaust nozzle, which covers the
    LR-91 roll nozzle), H-1D aspirator, and F-1/J-2 nozzle injection with a gas film.
  - The flat `GG_DUMP_ISP_FRACTION = 0.55` is retired. Turbine back pressure is anchored on
    `[H1-Man]`; exhaust Isp is pinned on the F-1's 16,000 lbf `[SP-8120]`.
  - Still Tier 3 and still wanting sources: gas-film effectiveness (SP-8124, item a), the
    LR-91 GG flow (the model under-predicts its 865 lbf by ~40%, item d), the heat-exchanger
    GOX duty (item h), and the duct Mach and hardware constants (`ASSUMPTIONS.md`).
  - The original acquisition list is kept below for those follow-ups. It was written against
    the planned (pre-implementation) version of the feature: three modes (overboard duct
    RS-68/H-1/Merlin, nozzle injection F-1/J-2X/Vulcain, roll nozzle LR-91), with
    `design.GG_DUMP_ISP_FRACTION = 0.55` unsourced. Needed, in priority order:
  (0) **DONE 2026-09-24**: `[SP-8120]` §2.2.5.3 Hot-Gas Manifold and §2.2.5.1 Manifold
  Hydraulics are now fully read (see `topics/07-dump-cooling.md`'s new "Turbine-exhaust-gas
  film cooling" section and `topics/12-materials-and-structures.md`'s new hot-gas-manifold
  content) — real F-1 numbers now in hand: eps 10:1→16:1 film-cooled-extension cutoff, a real
  ~25-30%-at-attachment coolant-split finding, real Hastelloy-C/Inconel-625/347-CRES
  materials, real ~0.5%-of-total-thrust turbine-exhaust performance contribution, real omega-
  joint thermal-growth/failure precedent, and a real safety-relevant design criterion (never
  use looped-tube introduction with storable propellants). `topics/06`/`07` are no longer
  empty of turbine-exhaust-film data. `[SP-8081]` §2.1.1 exhaust outlet and `[SP-8107]`/
  `[Huzel]` turbine-exhaust-ducting content remain unread/unchecked against this question —
  lower priority now that SP-8120 gave the richest real-hardware anchor;
  (a) **SP-8124** (entry above), for film effectiveness;
  (b) **Rocketdyne F-1 Engine Familiarization Training Manual (R-3896-1)**: still worth
  acquiring for TEG manifold drawings/extension wall temps in more depth, but its headline
  numbers (the injection area ratio, ~10:1 — now confirmed exactly 10:1 by `[SP-8120]`) are
  now real-sourced without it;
  (c) **J-2X nozzle-extension TEG film-cooling papers** (NTRS search), for modern film
  effectiveness + the Isp recovery of the injected exhaust;
  (d) **LR-91 / Titan II stage-2 engine description** (Aerojet manual, NTRS/DTIC): GG flow,
  roll-nozzle area ratio/exit conditions, swivel range, roll thrust. The RO header already
  gives "100,000 lbf chamber + 865 lbf turbine" as a reverse-solve anchor;
  (e) **NASA SP-8110** *Liquid Rocket Engine Turbines*: exhaust back-pressure vs. turbine
  PR (only needed for the optional back-pressure coupling);
  (f) **RS-68 / Vulcain GG exhaust-duct data** (AIAA development papers), to check
  overboard mode and to confirm whether each engine ducts overboard or reinjects;
  (g) **"aspirator": DONE 2026-09-24** via `[H1-Man]`.
  - It is the H-1D's Hastelloy C shroud over the aft ~20 in of the nozzle.
  - The exhaust leaves through a 0.440 in annular slot at the exit lip.
  - The H-1C instead uses a curved overboard duct.
  - Geometry is real; no aspirator thrust or entrainment number exists, so its Isp stays a
    choked-slot model.

  (h) **Exhaust heat exchanger** (LOX→GOX, H-1 `[H1-Man §1-47]`; Titan I superheater
  `[SP-8120]`):
  - The heat-exchanger duty (GOX flow, outlet temperature) is not given anywhere.
  - The heat-exchanger temperature drop and mass in `engine_designer` are Tier 3 until a
    stage-pressurisation source is found.
  Anything left unfound is calibrated purely by reverse-solving against RO headers (say which).

## Pending `ASSUMPTIONS.md` citation upgrades

Real citations now exist for the following, but no `engine_designer/ASSUMPTIONS.md` or code
edit has actually been made — `claude_lit`'s standing rule is "report-only, propose no
edits," so these are sitting in topic-file prose waiting for whoever next touches the code.

- **NPSH/suction-specific-speed feature plan** (see the historical plan file's
  `NSS_TARGET_US["lox_class"] = 40_000.0` seed value): now has a direct real-criterion
  citation, `[SP-8109 §3.2.1.2]` — *"For a pump with an integral inducer, maximum suction
  specific speed of 40,000 for the inducer is recommended. Without an integral inducer,
  limit the Ss value to 12,000."* Also gives real NPSH margin factors by propellant class
  (3.0× water/RP-1, 2.3× LOX/LF2, 1.3× LH2, all ×`cm1²/2g`) with no counterpart in
  `turbopump_sizing.py` yet. `lh2_class: 58_000.0` still rests on the older F-1/J-2
  two-anchor-point derivation, not this source — only the `lox_class` seed is directly
  confirmed. Real fleet Ss data (8,600-23,400 across F-1/J-2/Atlas/X-8) sits well below the
  40,000 ceiling — don't calibrate a future validate.py check against 40,000 as if it were a
  typical value; it's an upper design bound.
- **`turbopump_materials.py` `BEARING_MATERIALS.max_dn_mm_rpm`** (~1.2M-2.4M, previously
  flagged Tier-3 with no citation at all): now has a real blanket citation, `[SP-8048
  §3.1.2]` — one-piece cages required above 1.0×10⁶ DN, angular-contact ball bearings
  recommended for 1.0-3.0×10⁶ DN, rolling-element bearings not recommended above 3.0×10⁶ DN
  without prior qualification testing. Note the tool's numbers are *more conservative* than
  this real ceiling — applying this citation doesn't necessarily mean changing the numbers,
  just documenting them against a real source instead of "general aerospace rolling-element-
  bearing knowledge." This monograph gives a single blanket ceiling, not a per-material
  breakdown, so it validates the tool's overall order-of-magnitude but not its 440C/Cronidur
  30/Si3N4 gradation specifically.
- **Real impeller tip-speed-by-shrouding data** `[SP-8109 §2.3.2]`: open-face titanium
  (Ti-5Al-2.5Sn) ran to 2500 fps in real LH2 service vs. 1400 fps for shrouded cast Inconel
  718/aluminum — ~80% more tip speed for the same service. Not a citation *upgrade* exactly
  (no existing tool constant claims otherwise), but a real shrouding-configuration trade
  `turbopump_materials.py`'s rotor catalog doesn't currently capture (it varies max-use-
  temperature and density, not shrouding vs. tip-speed) — flagged here as a candidate model
  extension.

- **`materials.py`'s copper chamber-liner alloys** (GRCop-84, NARloy-Z, Cu-Cr-Zr, GlidCop
  AL-15, Zr-Cu, Cr-Cu): now have a real quantitative properties table, `[MatCh2 Table 2.6.3]`
  — CTE, thermal conductivity, tensile yield, UTS, elongation, all at room temperature. First
  numeric source for these exact alloys in this reference set (prior sources named them but
  gave no properties). No high-temperature or fatigue/creep data though — still a gap if
  those are ever needed.
- **Any future hydrogen-embrittlement material advisory**: `[MatCh2 Table 2.8.2/2.8.3]` gives
  real quantitative HEE Index data by alloy/heat-treat, including the directly actionable
  finding that Inconel 718 flips from Extreme (0.46-0.53) to Small (0.92) HEE susceptibility
  purely from solutionizing temperature (1750°F vs 1900°F) — explains `[Ch12-Materials]`'s
  existing J-2 718-forging anecdote with real numbers. Not yet applied to any code (no H2-
  embrittlement advisory currently exists in `materials.py`/`turbopump_materials.py`).
- **Any future LOX-compatibility material advisory**: `[MatCh2 Table 2.9.1/2.9.2]` gives real
  ignition-threshold data — titanium/magnesium ignite at any pressure in LOX/GOX service (an
  absolute red flag), Inconel 718's own threshold (500 psi) is surprisingly low. Not yet
  applied to any code (no LOX-ignition-compatibility check currently exists).
- **Bearing DN Tier-3 flag** (`turbopump_materials.py` `max_dn_mm_rpm`): `[SP-8048 §3.1.2]`'s
  citation (see above) now has a second independent real-hardware anchor, `[STBE-PW]`'s
  1989 GG-cycle turbopump fleet data (0.64-1.06×10⁶ DN across LOX/fuel bearings) — both
  sitting comfortably inside SP-8048's 1.0-3.0×10⁶ band.
- **`cooling.py`'s `BARTZ_ABS_FLUX_CALIBRATION` LOX/RP-1 anchor**: now has independent
  real-hardware corroboration (`[TP2862-LOXRP1]`'s ~60%-high calorimeter finding), alongside
  the existing `[EUCASS-2023]` CFD corroboration — one hardware source, one CFD source,
  agreeing that uncalibrated design predictions under-predict real LOX/hydrocarbon throat
  heat flux. Strengthens confidence in the calibration approach; doesn't change any number.

## Cooling audit 2026-09-23 - literature needed (engine_designer/COOLING_AUDIT.md)

- **Coolant-side heat transfer: RESOLVED 2026-09-23** by `[EUCASS-2023]` Eq. 21-22
  roughness/curvature factors (the mechanism `[Wieseneck-J2 p.24-25]` says the SSME design
  used) plus a LOX/LH2 h_g factor reverse-solved to the SSME design flux. STILL WANTED (a
  2026-09-23 re-read of Wieseneck, SECA-FR-93-18, SP-8087, Sutton, Huzel, J-2X, AEDC-J2S,
  IAC-19 and Merkle found none of it): REAL channel geometry (count, width, height, land,
  hot-wall thickness), jacket flow split and coolant inlet state for SSME MCC, RL10, F-1,
  Vulcain. The SSME MCC model data is likely in **SECA-P-90-09** (SECA-FR-93-18's Phase I
  report, its Ref. 1) - not in `literature/`. Cited so far: J-2S 180 down / 360 up tubes
  `[AEDC-J2S]`, F-1 Inconel-X 0.018 in tube wall `[SP-8087 Table III]`, LE-7 288 channels
  x 0.05 in and RS-27 292 tubes x 0.45 in `[Sutton Table 8-1]`.
- **Throat-flux anchors for LOX/RP-1 and LOX/CH4** (both run raw Bartz; RP-1 with the
  cited deposit factor). SECA-FR-93-18 Fig. 37 shows a Rocketdyne 3.4-in LOX/RP-1 motor at
  ~98-111 MW/m2 measured throat flux but gives no chamber pressure - find it.
- **Real-engine cooling data for the corpus** (`engine_designer/validation_engines/`):
  cited throat heat flux, coolant ΔT, jacket dP, liner thickness for RL10A-3-3, Vulcain,
  RD-180, Merlin-1D, Raptor-2, Rutherford, Aestus (only F-1 / J-2 / SSME have any today).
- **RP-1 in CoolProp is an n-dodecane surrogate** - a real RP-1 property set (NIST
  RP-1 surrogate model, Huber et al.) would firm up the kerosene jacket.
- Still open from before: NASA SP-8124 film effectiveness; RP-1 coking rate model.

## Where to look before re-deriving or re-searching

- `README.md`'s citation table + topic-file index is the map of what's already covered by
  which source.
- Each `topics/*.md` file's own "Implications for engine_designer" section is pre-filtered
  for actionability — read that before the rest of the topic file.
- Every `sources/*.md` note has an explicit "extraction scope" section stating exactly which
  pages were deep-read vs. skimmed vs. not-read at all — resume an existing source's unread
  sections (see the gaps list above) instead of re-reading it whole from scratch.
