# [MatCh2] — Chapter 2: Aerospace Materials Characteristics

## Identity

- **Title**: *Chapter 2: Aerospace Materials Characteristics* (with sub-sections by
  multiple contributing authors)
- **Lead author**: Biliyar N. Bhat, NASA Marshall Space Flight Center (chapter editor/
  primary author of §2.1, §2.4, §2.9 intro attribution notwithstanding — see per-section
  authors below); other sections credited to named co-authors within the text.
- **Source**: NASA Technical Reports Server document `literature/NASA Ch2 - Aerospace Materials Characteristics.pdf` (NTRS 20180001137) — same multi-author
  aerospace-materials reference volume that Chapter 12 ("Materials for Liquid Propulsion
  Systems", `[Ch12-Materials]`) belongs to. This is the **general aerospace-materials**
  chapter (metals/composites survey across aircraft, spacecraft, launch vehicles,
  propulsion), not propulsion-specific — cross-reference `sources/
  ch12-materials-liquid-propulsion.md` for the sibling propulsion-focused chapter.
- **Extent**: 145 PDF pages (leaf = printed page − 1). Born-digital, clean text layer, a
  handful of pure-graphic figure pages with unreadable embedded chart text (values
  extracted instead from nearby data tables where available).
- **Per-section authorship** (chapter is a compilation, not single-authored):
  §2.2 Aluminum Alloys — Awadh B. Pandey (Pratt & Whitney); §2.3 Titanium Alloys — Sesh
  Tamirisakandala, Ernie M. Crist, Patrick A. Russo (RTI International Metals); §2.4
  Steels — Biliyar N. Bhat (MSFC); §2.5 Superalloys — Michael V. Nathal (NASA Glenn); §2.6
  Copper Alloys — David L. Ellis (NASA Glenn); §2.7 Damage Tolerance — unattributed in
  extracted pages; §2.8 Hydrogen Embrittlement — Jonathan A. Lee (MSFC); §2.9 Oxygen-Rich
  Environments — Samuel Edgar Davis (MSFC); §2.10–2.11 Polymers/Composites — unattributed
  in extracted pages.
- **Character**: A **general aerospace-materials primer**, organized by material class
  (Al, Ti, steel, superalloy, Cu, then cross-cutting damage-tolerance/H2-embrittlement/
  O2-compatibility/polymer-composite chapters), aimed at aircraft-structure and
  general-aerospace readers first, propulsion second. Unlike `[Ch12-Materials]` (a
  component-by-real-engine historical survey), this chapter gives **quantitative
  composition and property tables per alloy class**, plus two chapters — Hydrogen
  Embrittlement (§2.8) and Oxygen-Rich Environments (§2.9) — that are **directly and
  heavily propulsion-relevant** with real quantitative screening data (HEE indexes,
  oxygen ignition thresholds) not found in `[Ch12-Materials]` or `[Huzel]`.
- **Extraction scope for this note**: per the assigning task, only content specifically
  useful for chamber/nozzle/turbopump material selection was extracted — the aluminum
  alloy (§2.2, mostly aircraft-skin/Al-Li tank alloys), titanium alloy (§2.3, mostly
  jet-engine/airframe-focused, qualitative-only for engine-relevant properties), damage
  tolerance (§2.7), and polymer/composite (§2.10–2.11) sections were reviewed and found to
  be generic aircraft-structure content with no rocket-engine-specific numbers, and are
  **not** extracted here (their content, if ever needed, is a future look, not covered).

## Key results

### Table 2.5.1 — superalloy compositions (§2.5, p.48)

Weight-% compositions for alloys `engine_designer` already references or could reference:

| Alloy | Base | Ni | Fe | Cr | Co | Al | Ti | Nb | Mo | W | Ta | Re | C |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **IN-718** | Ni-Fe | Bal | 18.5 | 18.5 | – | 0.5 | 0.9 | 5.1 | 3.0 | – | – | – | 0.040 |
| Waspaloy | Ni | Bal | 2.0 | 19.5 | 13.5 | 1.4 | 3.0 | – | 4.3 | – | – | – | 0.070 |
| Udimet 720 | Ni | Bal | – | 18.0 | 14.7 | 2.5 | 5.0 | – | 3.0 | 1.3 | – | – | 0.030 |
| Rene 88DT | Ni (powder) | Bal | – | 16.0 | 13.0 | 2.1 | 3.7 | 0.7 | 4.0 | 4.0 | – | – | 0.0 |
| IN-738 | Ni (cast) | Bal | – | 16.0 | 8.5 | 3.4 | 3.4 | 0.9 | 1.8 | 2.6 | 1.8 | – | 0.170 |
| Mar-M247 | Ni (cast) | Bal | – | 8.5 | 10.0 | 5.5 | 1.5 | – | 0.7 | 10.0 | 3.0 | – | 0.160 |
| CMSX-4 | Ni (single-crystal) | Bal | – | 6.5 | 10.0 | 5.6 | 1.0 | – | 0.6 | 6.0 | 6.0 | 3.0 | 0.1 |
| Haynes 188 | Co (sheet) | 22 | 3.0 | 22.0 | Bal | – | – | – | – | 14.0 | – | – | 0.100 |
| Hastelloy-X | Ni-Fe (sheet) | Bal | 18.5 | 22.0 | 1.5 | – | – | – | 9.0 | 0.6 | – | – | 0.100 |
| **Inconel 625** | Ni (sheet) | Bal | 2.5 | 21.5 | – | 0.2 | 0.2 | 3.6 | 9.0 | – | – | – | 0.050 |

**Rocket-turbopump application note** `[MatCh2 §2.5.3 p.49]`: turbopump blades/disks/
housings are described as directly analogous to jet-engine turbine hardware; **IN-718 and
single-crystal (SX) superalloys are named as real turbopump examples**. If the propellant
is hydrogen, **alloy strength may have to be sacrificed for hydrogen-embrittlement
resistance** — a direct statement of the strength-vs-H2-resistance trade this chapter's
§2.8 quantifies below.

**Superalloy strengthening/processing background** `[§2.5.1–2.5.2 p.45–48]`: Ni-base
superalloys are γ (FCC matrix) + γ' (Ni3Al precipitate) — γ' long-range order gives the
strength/creep resistance; Cr in γ gives oxidation resistance via Cr2O3 scale (good to
~1000°C, beyond which Al2O3-forming alloys are needed instead); Mo/W/Re solid-solution
-strengthen γ, Ti/Nb/Ta strengthen γ'. Fe-Ni alloys (IN-718) additionally use γ"
(Ni3Ti,Nb). Directional solidification (DS) and single-crystal (SX) casting exist
specifically to eliminate transverse grain boundaries for creep strength at turbine-blade
temperatures — SX offers the best creep resistance but at highest cost, restricting it to
the highest stress/temperature components (i.e., turbine blades, not disks/housings).
Coatings (aluminizing, NiCoCrAlY overlay, yttria-stabilized-zirconia TBC) are standard for
turbine airfoils/combustor parts.

### Table 2.6.3 — rocket-engine chamber-liner Cu alloys (§2.6.3, p.53)

The single most directly-usable table for `engine_designer/physics/turbopump_materials.py`
and `materials.py`'s copper-alloy chamber-liner options — **real room-temperature
properties for current and candidate rocket-engine liner alloys**:

| Alloy | Composition | CTE (1/K ×10⁻⁶) | Thermal cond. (W/m·K) | Compr. yield (MPa) | Tensile yield (MPa) | UTS (MPa) | Elong. % |
|---|---|---|---|---|---|---|---|
| GRCop-84 (annealed) | Cu-6.7Cr-5.9Nb | 15.3 | 285.4 | 311.8 | 196.2 | 368.0 | 21.7 |
| GlidCop AL-15 (hard drawn) | Cu-0.3 Al2O3 | 16.6 | 365.2 | 432.9 | 464.5 | 464.5 | 20.5 |
| Zirconium Copper C15000 (HD+aged) | Cu-0.15 Zr | 16.9 | 366.9 | 464.0 | 501.9 | 510.9 | 19.5 |
| Chromium Copper C18200 (HD+aged) | Cu-0.9 Cr | 17.6 | 323.6 | 450.0 | 441.8 | 495.2 | 18.3 |
| Cu-Cr-Zr C18150 (HD+aged) | Cu-1Cr-0.1Zr | 16.5 | 323.9 | 501.4 | 549.9 | 564.4 | 11.2 |
| **NARloy-Z** (solutioned+aged) | Cu-3Ag-0.5Zr | 17.2 | 295.0 | — | 192.0 | 314.0 | 31.0 |

Note: GRCop-84's composition is given here as **Cu-6.7Cr-5.9Nb** (differs from the
Cu-6.7Cr-5.9Nb-vs-sometimes-quoted Cu-8Cr-4Nb naming inconsistency seen elsewhere in this
same source's own §2.8 HEE table below — see Caveats). NARloy-Z's own real chamber
application: SSME hot-wall liner, **20 MPa chamber pressure, ~3000°C flame**, entirely
survivable only via active regen cooling exploiting NARloy-Z's high conductivity + good
elevated-temp strength `[§2.6.3 p.52]`. **Copper is also used as a deliberate hydrogen
diffusion barrier** on Ni-based alloys susceptible to H2 embrittlement, and the SSME uses
copper for preburner baffles and partial main-fuel-valve-housing coating `[p.53]`.

### Table 2.8.2/2.8.3 — Hydrogen Environment Embrittlement (HEE) Index, real alloys tested at 24°C, 5–10 ksi (34.5–69 MPa) H2 `[§2.8.4–2.8.5 p.68–77]`

This is the chapter's most load-bearing new content: **quantitative, real, per-alloy
hydrogen-embrittlement screening data** — exactly the kind of number `[Ch12-Materials]`'s
survey only gestures at qualitatively. HEE Index = property ratio (Notched Tensile
Strength, Reduction of Area, or Elongation) measured in H2 vs. air/He; 1.0 = no effect, 0 =
total loss. Qualitative bands (Table 2.8.1): Negligible 1.0–0.97, Small 0.96–0.90, High
0.89–0.70, Severe 0.69–0.50, Extreme 0.49–0.0.

| Material (heat treat) | Test pressure MPa | HEE category | NTS ratio |
|---|---|---|---|
| 4340 (austenitized 1652°F) | 34.5 | **Extreme** | 0.35 |
| 17-4 PH | 69.0 | **Extreme** | 0.18 |
| 17-7 PH | 69.0 | **Extreme** | 0.22 |
| 18Ni-250 Maraging | 69.0 | **Extreme** | 0.12 |
| 440C | 69.0 | **Extreme** | 0.50 |
| Ti-6Al-4V (annealed) | 69.0 | High | 0.79 |
| Ti-6Al-4V (STA) | 69.0 | **Severe** | 0.58 |
| Ti-5Al-2.5Sn (ELI) | 69.0 | High | 0.81 |
| K-Monel (precipitated) | 69.0 | **Extreme** | 0.45 |
| K-Monel (annealed) | 69.0 | High | 0.73 |
| Copper (OFHC) | 69.0 | **Negligible** | 0.99 |
| Aluminum Bronze | 68.9 | **Negligible** | 1.02 |
| Be-Cu alloy 25 | 69.0 | Small | 0.93 |
| **GRCop-84** (Cu-8Cr-4Nb) | 34.5 | **Negligible** | 1.00 |
| **NARloy-Z** (Cu-3Ag-0.5Zr) | 40.0 | **Negligible** | 1.10 (>1, i.e. H2 exposure slightly *raised* NTS in this test) |
| Haynes 230 | 34.5 | High | 0.76 |
| Inconel 625 | 34.5 | High | 0.76 |
| Inconel 700 | 69.0 | **Extreme** | 0.45 |
| **Inconel 718 (ST @1750°F)** | 34.5 | **Extreme** | 0.53 |
| **Inconel 718 (ST @1750°F)** | 69.0 | **Extreme** | 0.46 |
| **Inconel 718 (ST @1900°F)** | 34.5 | **Small** | **0.92** |
| Inconel X-750 | 48.2 | **Extreme** | 0.26 |
| Rene 41 | 34.5/69.0 | **Extreme** | 0.36/0.27 |
| Waspaloy (PM) | 34.5 | Small | 0.95 |
| A-286 (ST @1640°F) | 69.0 | **Negligible** | 0.97 |
| A-286 (ST + Aged) | 69.0 (thermal-charged) | **Severe** | 0.51 |
| Incoloy 903 (ST only) | 34.5 | Negligible | 0.98 |
| Incoloy 903 (ST + Aged) | 24.0 (T.C.) | Severe | 0.55 |

**The single most important, directly actionable finding in the whole chapter**:
**Inconel 718's own HEE resistance flips categories (Extreme → Small) purely from
solutionizing temperature — 1750°F gives NTS ratio ~0.46–0.53 (Extreme), while 1900°F
gives ~0.92 (Small)** `[§2.8.4 Table 2.8.2, p.70; also §2.8.6 Fig 2.8.5 crack-growth-rate
corroboration, p.76]`. This directly explains and quantifies `[Ch12-Materials]`'s J-2
turbopump anecdote (double-vacuum melt + high-temp homogenization fixed a 718
short-transverse-property shortfall) — same alloy, same underlying heat-treat-sensitivity
mechanism, now with actual index numbers. **Aging treatments generally raise strength but
worsen HEE** — seen consistently across A-286, Incoloy 903, and by implication most PH
alloys — a real, quantified strength-vs-H2-resistance trade-off, not just a qualitative
rule of thumb.

**Cross-cutting HEE observations** `[§2.8.5 p.71–73]`:
- **Copper and copper-rich alloys are not susceptible to HEE** unless they contain oxygen/
  Cu2O (then hydrogen reacts with the oxide to form steam internally, causing "steam
  embrittlement" even without external stress — a distinct HRE-type mechanism, not the
  usual HEE). Both real chamber-liner Cu alloys (GRCop-84, NARloy-Z) test **negligible**
  HEE — reinforces that they're a doubly-good chamber-material choice (high conductivity
  AND H2-immune) independent of the propellant being LH2.
- **Pure nickel is severely embrittled by hydrogen**; Ni-rich binary alloys (Ni-Cu, Ni-Fe,
  Ni-Co, Ni-W) are similarly susceptible. K-Monel (Ni-Cu) — despite being cited in
  `[Ch12-Materials]` as the real J-2/F-1-era LH2-pump-inducer choice for its "guaranteed
  cryo ductility" — is itself only **High/Extreme** category depending on heat treat, not
  H2-immune; the ductility argument is about cryogenic embrittlement, a separate mechanism
  from hydrogen-gas-environment (HEE) embrittlement specifically.
- **Titanium reacts with hydrogen to form brittle hydrides (Hydrogen Reaction
  Embrittlement, HRE)** — a distinct, irreversible-damage mechanism from HEE that can
  occur without applied stress, worst above ~250°C (480°F); small hydride amounts
  (40–80 ppm H2) are usually tolerable.
- **Austenitic stainless steels generally resist HEE better than ferritic; martensitic and
  precipitation-hardening (PH) steels — e.g. 17-4PH — are extremely susceptible.**
  Directly confirms `[Ch12-Materials]`'s own caveat about 17-4PH/15-5PH's poor H2/cryo
  performance in valve poppets.
- **Wrought/PM superalloys are generally slightly less HEE-susceptible than cast
  polycrystalline superalloys of similar composition** `[p.73]`.
- **Heat-treat-condition-sensitive alloys**: A-286, JBK-75, Incoloy 903 — the note's own
  worked example above.
- **Low-cycle fatigue (LCF) life can drop by ~10× in strain-controlled H2 testing** at
  ~1.2% strain range for susceptible PM superalloys at room temperature — high-cycle
  fatigue (HCF, ≥10⁶ cycles) is comparatively unaffected because it's dominated by
  crack-initiation time at low strain amplitude, not propagation `[§2.8.6 p.75–76]`.
- **Reducing HEE risk**: lower operating stress (bigger cross-section, avoid stress
  raisers), reduce residual stress (anneal/preheat/post-weld heat treat, low-stress
  grinding) `[§2.8.7 p.79]`.

### Table 2.9.1/2.9.2 — LOX/GOX material ignition thresholds `[§2.9.3–2.9.4 p.84–87]`

Real NASA-MSFC test data, two independent test methods (Promoted Ignition Test =
vertical-rod sustained-burn threshold pressure; Mechanical Impact Test = plummet-drop
ignition threshold pressure):

| Material | Promoted Ignition threshold, psi (kPa) | Mech. Impact threshold GOX, psi | Mech. Impact threshold LOX, psi |
|---|---|---|---|
| 2024/2090/2219/5052 Al | 15 (103) | 500–1500 (3447–10342) | 50–1500 |
| 6061 Al | 15 (103) | 15 (103) | 15 (103) |
| **Titanium** | **<15 (103)** | <15 | <15 |
| **Magnesium** | **<15 (103)** | <15 | <15 |
| Brass | 10,000 (68948) | 10,000 | 10,000 |
| Copper 12200 | 10,000 (68948) | 10,000 | 10,000 |
| **Inconel 718** | **500 (3447)** | 10,000 | 10,000 |
| Monel K-400/K-500 | 10,000 (68948) | 10,000 | 10,000 |
| Nickel | 10,000 (68948) | 10,000 | 10,000 |
| SS 17-4 | 400 (2758) | 5,000 | 5,000 |
| SS 304/304L | 500/250 (3447/1724) | 10,000 | 10,000 |
| SS 316/316L | 400/250 (2758/1724) | 10,000 | 10,000 |
| SS 420 | 750 (5171) | 10,000 | 10,000 |
| SS 440C | 3,000 (20684) | 10,000 | 10,000 |
| Haynes 214 | 1,000 (6895) | 10,000 | 10,000 |

**Directly actionable for LOX-side material advisories**: **titanium and magnesium ignite
at essentially any pressure (<15 psi/103 kPa) in the Promoted Ignition Test** — an
absolute red flag for any LOX-wetted titanium part (contradicts titanium's otherwise
excellent cryo/strength properties — it must be excluded from LOX flow paths on ignition
grounds alone, not a strength/toughness issue). **Inconel 718's own Promoted-Ignition
threshold (500 psi) is surprisingly low relative to stainless/nickel/copper alloys** —
a second real reason (beyond §2.8's H2-embrittlement heat-treat sensitivity) that 718 is
not an unconditionally safe universal turbopump alloy; it needs the same case-by-case
oxygen-compatibility review as any borderline metal at the system's real operating
pressure. **Copper, nickel, Monel, and brass are essentially non-ignitable up to the test
ceiling (10,000 psi/69 MPa)** — reinforces copper alloys' (GRCop-84/NARloy-Z) role as a
doubly-safe choice for oxidizer-side hardware too, not just chamber liners.

Pressure and temperature both **increase** ignition probability and burn severity — real
burn-rate data (Table 2.9.2) for 304/316/347/303 stainless rods show burn length/rate
increasing with test pressure (e.g., 316 SS: 500 psi → 1.7 in burn / 0.3 in/s; 1000 psi →
12 in (full) / 0.4 in/s). Liquid oxygen is **more reactive than gaseous oxygen at the same
nominal conditions** despite being colder, because of its higher molecular density
`[§2.9.4 p.86]`.

**Real ignition-mechanism catalog for LOX system design** `[§2.9.5 p.88–91]`: contamination/
FOD (the most common and dreaded ignition source), particle impact, rapid pressurization
(adiabatic heat-of-compression — worse for polymers than metals), mechanical impact,
friction (incl. valve/regulator chatter causing metal-to-metal rubbing), static discharge,
electrical arc, external heat, external hazards. Mitigations given per mechanism (filter
elements, limited pressurization rate, burying nonmetals behind metal in the flow path,
minimizing rotating/sliding-part count, cleanliness procedures per MSFC-SPEC-164C).

**Oxygen Compatibility Assessment (OCA)** `[§2.9.6 p.92–93]`: NASA's formal 10-step
hazards-analysis process for qualifying materials/designs for LOX/GOX service (worst-case
conditions → flammability at worst case → ignition-mechanism probability → kindling-chain
severity → documented mitigations). Not a numeric design rule but the real-world process
this chapter's data tables (2.9.1/2.9.2/2.9.3) feed into.

## Section map

| Section | Printed p. | Content | Extracted here? |
|---|---|---|---|
| 2.1 Introduction | 1–2 | Material-class taxonomy | No (context only) |
| 2.2 Aluminum Alloys | 3–29 | Classification, temper, Al-Li tank alloys (2195/2050/etc.), DRA composites | No — aircraft-structure/tank-skin focus, no chamber/nozzle/turbopump relevance found |
| 2.3 Titanium Alloys | 30–40 | α/α+β/β classification, TMP, jet-engine/airframe applications | No — qualitative-only, jet-engine-not-rocket focus; no engine-relevant property table found |
| 2.4 Steels | 41–45 | Ultra-high-strength, fracture-toughness, maraging, corrosion-resistant, Ni-Cr steel classes + Table 2.4.1 composition/application table | Partial — Table 2.4.1 real steel compositions (4340, 300M, D6-AC, A-286, 17-4PH etc.) noted in passing, not reproduced in full (overlaps `[Huzel]`'s existing coverage in topic 12) |
| 2.5 Superalloys | 46–50 | γ/γ' metallurgy, processing (casting/DS/SX/coatings), Table 2.5.1 compositions, turbopump application note | **Yes** — Table 2.5.1 + turbopump note above |
| 2.6 Copper Alloys | 51–54 | Aircraft bearing alloys, spacecraft chamber-liner alloys (Table 2.6.3), electronics | **Yes** — Table 2.6.3 + NARloy-Z/copper-as-H2-barrier notes |
| 2.7 Damage Tolerance | 55–62 | Fracture mechanics test standards, generic damage-tolerance factors | No — generic, no rocket-engine-specific content found |
| 2.8 Hydrogen Embrittlement | 63–80 | HEE/IHE/HRE classification, HADOS mechanism theory, HEE Index screening method, Tables 2.8.2/2.8.3 real alloy data, controlling factors | **Yes** — the chapter's most valuable section for this tool |
| 2.9 Oxygen-Rich Environments | 80–95 | Fire triangle, real NASA oxygen mishaps, ignition/burn test methods, Tables 2.9.1–2.9.3 real ignition thresholds, ignition-mechanism catalog, OCA process | **Yes** |
| 2.10 Polymers and Composites | 95–116 | Polymer types/processing/aging, composite manufacturing | No — no rocket-engine-hardware-specific content found (seals/ablatives covered better by `[Sutton]`/`[Ch12-Materials]`) |
| 2.11 Composites for Launch Vehicles | 117–145 | Carbon-fiber vs Al comparison, launch-vehicle-specific composite allowables methodology, fatigue | No — structural-tank/fairing focus, not chamber/nozzle/turbopump |

## Caveats

- This is a **general aerospace-materials primer chapter**, not a propulsion-specific
  source — most of its ~145 pages (aluminum, titanium, damage tolerance, polymers/
  composites) were reviewed and found to have **no rocket-engine-hardware-specific
  content** worth extracting per this note's assigned scope; only §2.5 (superalloys), §2.6
  (copper alloys), §2.8 (hydrogen embrittlement) and §2.9 (oxygen compatibility) yielded
  citable material.
- **GRCop-84 composition inconsistency within this same source**: Table 2.6.3 (§2.6.3, the
  chamber-liner properties table) states composition as **Cu-6.7Cr-5.9Nb**, while Table
  2.8.2 (§2.8.4, the HEE-index table) labels the same alloy **Cu-8Cr-4Nb**. Both numbers
  are the source document's own text, not an extraction error here — flag this
  discrepancy rather than silently picking one; GRCop-84's commonly-cited nominal
  composition elsewhere is Cu-8Cr-4Nb (atomic %) which is consistent with Table 2.8.2's
  labeling, so Table 2.6.3's "Cu-6.7Cr-5.9Nb" may be a weight-%-vs-atomic-% mismatch
  rather than a real compositional difference — not resolved here.
- **HEE Index data (§2.8) is an accelerated laboratory screening method, not a design
  allowable** — the chapter itself repeatedly warns the index should not be used for
  component design without full fracture-mechanics/crack-growth analysis, particularly for
  materials rated High/Severe/Extreme. Treat the HEE Index numbers above as *relative
  ranking* data (which alloy is more/less H2-resistant than another) rather than as inputs
  to a quantitative margin calculation.
- **HEE test conditions are narrow**: room temperature (24°C), 34.5–69 MPa (5–10 ksi) H2
  pressure only. The chapter explicitly warns this data should **not** be extrapolated to
  high-temperature service (e.g. a hot turbine housing) — a different, unquantified regime.
- **Table 2.9.1/2.9.2 LOX/GOX ignition data carries the source's own explicit caveat**:
  "data for comparison purposes only, not to be considered standard values for listed
  material" — occasional test series showed ignition at lower pressures than tabulated,
  i.e. real lot/batch variability exists and the numbers are not hard qualification limits.
- No stress-vs-temperature curves, fatigue S-N data, or creep-rupture data for any of the
  superalloys/copper alloys in Table 2.5.1/2.6.3 — those are composition and single-point
  RT tensile/thermal properties only, same limitation flagged for `[Ch12-Materials]` in its
  own source note.
- Some figure-only pages (e.g. Fig. 2.8.2–2.8.6, trend curves for HEE Index vs. temperature/
  pressure/strain-range) could not be read as numeric data — described qualitatively above
  from the surrounding body text, not digitized from the plots themselves.
