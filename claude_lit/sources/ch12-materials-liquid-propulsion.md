# [Ch12-Materials] — Materials for Liquid Propulsion Systems

## Identity

- **Title**: *Materials for Liquid Propulsion Systems* (Chapter 12)
- **Authors**: John A. Halchak (Consultant, Los Angeles), James L. Cannon (NASA Marshall
  Space Flight Center), Corey Brown (Aerojet Rocketdyne, West Palm Beach)
- **Source**: A chapter from an AIAA-style multi-author reference volume on liquid rocket
  propulsion (chapter numbering / cross-references to "chapter 11" on solid motors and its
  own reference list citing sources through 2015-16 — likely *Encyclopedia of Aerospace
  Engineering* or a "Progress in Astronautics and Aeronautics"-family volume; exact volume
  title not present in the extracted pages). No date given in-text; newest reference is a
  Dec 2015 NASA news release on 3-D printing (ref. 27), so authored ~2016.
- **Extent**: 58 PDF pages (leaf = printed page − 1, i.e. leaf 0 ↔ printed p.1). Born-digital
  PDF, clean text layer, no OCR issues.
- **Character**: Not a quantitative design-equation source (contrast `[Huzel]`, `[Sutton]`).
  It is a **historical materials survey**, organized by engine component, walking chronologically
  from Goddard's 1920s-30s rockets through the V-2, 1950s ICBM engines, Apollo-era engines,
  SSME, and 2000s-2010s technology-demonstrator/additive-manufacturing programs. Its value
  here is the **specific alloy named per real component per real engine**, with a little
  numeric context (temperature, pressure, HP, RPM) attached to each — a materials-selection
  cross-check list, not a stress/allowable-property handbook.

## Selection framework (§12.3–12.4, p.7–14)

Five factors drive material selection for any component: **(1)** engine size, **(2)** duty
cycle (expendable vs. reusable), **(3)** propellants, **(4)** turbine drive cycle, **(5)**
stage (booster vs. upper stage) `[Ch12-Materials p.14]`. Higher Pc → tighter material
constraints for two reasons: specific strength (strength/weight) becomes dominant, and
high-strength alloys tend to be harder to fabricate and more prone to toughness/ductility/
environmental-compatibility problems `[p.14]`.

Component-level criteria stated explicitly `[p.14]`:
- Rotating pump parts: high specific strength **and** ductility.
- Pump housings: castability + adequate specific strength (castings are usually the
  cheapest production route).
- Ducting/lines: specific strength + weldability + formability.
- LOX valve poppets/seats: LOX-ignition resistance is mandatory.
- Combustion-chamber liners: good thermal conductivity **and** thermal-fatigue resistance.
- Nozzles: the cooling method chosen (regen / film / ablation / radiation) dictates the
  material family (conventional alloy / refractory metal / ceramic composite /
  silica-phenolic ablative respectively).

## Injector materials (§12.5.1, p.15–20)

| Engine / era | Injector material |
|---|---|
| V-2 (1940s) | 18 "burner cups," Cr-V alloy steel; injector nozzles brass, threaded into cups |
| Redstone A6/A7 (early 1950s) | Flat-faced concentric-ring injector: 4130 Cr-Mo steel rings, nickel-plated, pure-copper brazed into a nickel-plated 4130 body — first US engine free of combustion instability |
| Larger baffled engines (Atlas-era, Fig 12-12/12-13) | OFHC copper rings brazed into an austenitic stainless-steel backing body; also seen: aluminum-alloy baffled bodies |
| RL-10 (first H2 engine) | Transpiration-cooled injector face using **"Rigimesh"** — multiple layers of fine austenitic-stainless-steel screen, diffusion-bonded into a porous sheet (adapted from a commercial filter product) |
| J-2, Vulcain, Russian kerosene staged-combustion engines | Coaxial (tube-in-tube) elements for gas/liquid mixing. J-2: 614 concentric-tube-post elements, austenitic stainless steel |
| Modern (post-2010s) | Additive-manufactured (SLM) Inconel injectors — parts that needed hundreds of pieces built as 1-2 pieces; hot-fire tested in LOX/LH2 "with no noticeable loss of performance" vs. conventional `[p.20, ref. 18]` |

## Combustion chamber / nozzle materials (§12.5.2, p.21–35)

Wall architectures in use: tubular, channel-wall, sandwich-wall, solid one-piece
(sometimes ceramic-coated), ablative — cooled regen/dump/film/radiation/ablative
`[p.21]`. Material families seen across all of these: Al alloys, low-alloy steel,
stainless steel, pure nickel, Ni-base alloys, Co-base alloys, Ti alloys, Cu alloys, Nb
alloys, carbon-carbon, ceramic-matrix composites, glass-phenolic, beryllium, refractory
metals.

**Sandwich-wall construction — real detail, added 2026-09-24** `[p.26-28]`: this source was
distilled before a later session's dedicated 6-source search for Russian "sandwich" wall
construction, and was never re-checked against that question — this note previously
compressed the finding into a single table row. The full text: "In the Soviet Union, channel
wall or sandwich wall combustion chamber-nozzle configurations were used. Usually the inner
liner was a copper-chromium (Cu~3%Cr) alloy into which slots or channels were milled and then
this was brazed to a cover/close-out sheet of low alloy steel, stainless steel, or
nickel-base alloy... Usually, the channel-wall design is used for the combustion chamber...
For medium-performance engines, such as the **RD-107**, the expansion nozzle is a sandwich
structure in which the inner liner is a Cu-Cr alloy, **a corrugated sheet metal is used as
the divider** and the outer shell can be alloy steel, stainless steel or nickel-base alloy.
The entire assembly is brazed and the corrugations provide flow passages for coolant
circulation." `[p.26-27]`. Historical joining-method development: "Originally, in the 1930's
time period, the liner and outer shell were only bolted together and the resultant leakage
between channels simply tolerated. Following WWII, a **pressure brazing** method was
developed to securely bond the milled channel wall liner to the outer shell. The development
of this brazing method, termed **"solder-welding" in Russia**, was a technological
improvement that made possible effective, efficient and reliable rocket engines." `[p.27]`.
Figure 12-21 (p.27) illustrates both the channel-wall and corrugation-sandwich
configurations side by side (inner liner Cu-Cr alloy in both); Figure 12-22 (p.28) is a photo
of a real RD-107 engine's copper-alloy inner liner. Tradeoffs stated: channel-wall/sandwich
both "reputed to be cheaper to fabricate than tubular configurations," but "heavier than
tubular nozzles" `[p.27]`. **Sandwich construction is not exclusively Soviet**: Figure 12-24
(p.28) shows the **F-1's lower nozzle extension is also sandwich construction** (Hastelloy-C,
dump-cooled with turbine exhaust, vs. the tubular alloy-X750 upper chamber/nozzle) — a real
Western sandwich-construction example, just not called out as such in the running text. A
modern Volvo/Vulcain nozzle-extension sandwich design is also described (p.29-31): milled-
channel liner closed out by a stainless-steel cover sheet joined by **burn-through laser
welds**, not brazing — a different, more modern joining method for the same face-sheet-plus-
core concept. **What this source does NOT give**: no channel/corrugation pitch, height, or
wall-thickness numbers, no cross-section dimensions, no structural/thermal formula — this is
real construction-concept-and-materials detail (what it's made of, how it's joined, which
real engines use it), not the dimensioned design criteria a monograph like `[SP-8087]` gives
for tube/channel-wall construction. A genuinely dimensioned source is still the open gap if
one is ever needed.

| Engine | Chamber/nozzle construction & material |
|---|---|
| V-2 (1940s) | Welded double-wall sheet metal, 6000-series low-alloy steel (0.9Cr-0.15V-0.3C-1.0Mn); triple-wall at the burner-cup end |
| Redstone A6/A7 | 4130 low-alloy (Cr-Mo) sheet-metal chamber; **aluminum-alloy LOX dome** (only after the first test-stand explosion — the original alloy-steel LOX dome was below its ductile-brittle transition at −290°F and shattered on startup shock `[p.24]`, a direct materials-selection failure anecdote) |
| Early tubular US engines | Nickel 200, 316/347 stainless, Inconel 600/X-750, A-286 tubes, hand- then furnace-brazed |
| F-1 | Tubular chamber/nozzle + upper extension: **alloy X-750** tubes; lower nozzle extension: **sandwich, Hastelloy-C**, dump-cooled with turbine exhaust |
| SSME | Channel-wall chamber, copper-alloy hot wall: **Narloy-Z** (Cu-3%Ag-0.5%Zr) — better strength and thermal fatigue than prior Cu alloys while retaining ~80% of pure-Cu thermal conductivity; "the key to obtaining the combustion efficiency of the SSME" `[p.26]`. Nozzle: brazed tubular, **1080 tubes of A-286 stainless brazed to a 718-alloy backup shell** (a challenging braze given the A-286/718 CTE mismatch) |
| Vulcain (Volvo Aero) | Tubular nozzle: square-cross-section **Inconel 600** tubes, spiral-wrapped (no taper needed), joined by **GTA fillet welds, not brazed**. Newer uprated-Vulcain extension: milled-channel sandwich, laser-welded, stainless steel |
| Russian designs (RD-107 family, etc.) | Channel-wall or corrugated-sandwich; inner liner **Cu-3%Cr** alloy; outer shell low-alloy steel / stainless / Ni-base, pressure-brazed ("solder-welding" in Russian usage) |
| Apollo SPS (AJ10) | Nozzle: **C-103 niobium alloy**; nozzle extension: welded **Ti-6Al-4V** sheet |
| RL-10B2, Vinci | Carbon-carbon nozzle extensions |
| Aestus (Europe) | Nozzle extension: **Haynes 25** sheet |
| RS-68, Gemini SE-6, Apollo-CM SE-8 | Ablative: glass-phenolic (RS-68) or carbon-cloth-/glass-cloth-/silica-cloth-phenolic |
| MC-1 / Fastrac (60K) | One-piece ablative chamber+nozzle: tape-wrapped **silica-phenolic** liner + filament-wound carbon-epoxy overwrap; single-use, replaced every flight |
| Small thrusters | Beryllium combustion chambers (unique heat capacity / radiative behavior) |

## Turbopump materials (§12.6, p.36–50)

The chapter's richest table-worthy content — a materials/performance table by engine
generation:

| Turbopump | Era | Power / speed | Pump-side materials | Turbine-side materials |
|---|---|---|---|---|
| Goddard | late 1930s | — | Impellers: brass/steel; housings: Al 2017 (4Cu-0.5Mn-0.5Mg) and Dowmetal (Mg-Al-Mn) — Mg in O2 service flagged as an unrecognized risk at the time | Turbine: machined Al 2017, GOX-driven |
| V-2 (A-4) | 1940s | 665 HP @ 3800 rpm | Housings/impellers: cast **Al-13Si-0.3Mn ("Silumin")**; shaft/steam manifold: low-alloy steel | Turbine disk: Al-2Mg-1.4Mn; blades: permanent-mold-cast **13X (Al-13Si)** — the as-cast oxide skin acted as a thermal barrier for the ~56 s burn; H2O2-decomposition steam drive |
| Redstone A6/A7 | early 1950s | 836 HP @ 4840 rpm | Impellers/housings: **356-T6 cast Al** (upgrade from Silumin) | Turbine disk: 7075 Al; blades: retained 13X cast-Al design |
| Atlas Mark 3 | late 1950s | Pump 2550 HP @ 6700 rpm; turbine 30,000 rpm | Impellers/housings: **Tens-50 cast Al** (precursor to A357); inducers: 7075-Al forgings; shaft: 4340 low-alloy steel; gears: carburized 9310 | Turbine disks: forged **16-25-6** (Fe-16Cr-25Ni-6Mo) early austenitic superalloy; blades: investment-cast **Stellite 21** (Co-27Cr-5Mo-2.5Ni), welded to disk |
| F-1 (Mark 10) | late 1950s | 53,000 HP @ 5500 rpm; 25,000 GPM LOX / 15,600 GPM RP-1 | Housing/impellers: **Tens-50 Al** castings in highly-chilled molds (unprecedented strength/ductility at that casting size); LOX inducer: **Monel K-500** forging; fuel inducer: 7075-T73 forging; shaft: 4340 forged bar | Turbine disk/manifold: **Rene 41** (Ni-19Cr-12Co-10Mo-3Ti-1.5Al-0.12C) — welding required post-weld vacuum heat treat; blades: **713C** investment castings |
| J-2 (Mark 15 fuel TPA) | early 1960s, GG cycle | 7900 HP @ 27,000 rpm; 3000 GPM LH2, 1238 psi discharge | Inducer/rotor/stator: **Monel K-500** forgings (chosen for guaranteed cryo ductility as a simple Cu-Ni alloy); pump outlet manifold: 410 SS sheet | Turbine discs: **alloy 718** forgings — one of the first-ever 718 forging applications; initial short-transverse property shortfall fixed by double-vacuum melt + high-temp homogenization; blades: 713C investment castings; inlet manifold: Hastelloy-C sheet |
| SSME HPFTP (original, 1970s) | 1970s | 70,000 HP @ 38,000 rpm, 6800 psi discharge; turbine gas ~840°C/1550°F H2-rich | — | Blades: cast **MAR-M-246** (directionally solidified) on **Waspaloy** hubs — susceptible to hydrogen embrittlement |
| SSME alternate HPOTP / Block II HPFTP | 1990s–2001 | first flights 1995 / 2001 | Eliminated 293 welds via fine-grained investment castings; **silicon-nitride (Si3N4) ceramic** rolling-element bearings | **Single-crystal alloy (PW1480)** thin-wall hollow-airfoil blades — eliminated the MAR-M-246 blade-cracking/H2-embrittlement problem |
| RS-68 fuel TPA | 2000s | — | Housing: **centrifugally cast alloy 625** | — |
| 3-D-printed LH2 TPA demo | 2015 | 90,000 rpm design speed, for a 35K-lbf expander engine | 45% fewer parts than a conventionally welded/assembled pump of similar duty | — |

Cross-cutting turbopump notes:
- **Bearings**: races/rolling elements historically 440C stainless or 52100 (1C-1.5Cr)
  steel; **Cronidur 30** (15Cr-0.5Ni-0.4N-0.3C) stainless adopted for SSME and RS-68
  bearings; newer designs use **Si3N4 ceramic** rolling elements, "virtually eliminating
  bearing wear and fatigue concerns" `[p.45]`.
- **Gears** (when an indirect gear-driven pump is used, e.g. RL-10, Atlas MA-2/3/5):
  carburized **9310** low-alloy steel — hard case, tough core.
- **SSME fuel-side impellers**: 3 stages of forged **Ti-5Al-2.5Sn-ELI**; diffusers/
  crossovers between stages cast **A357** aluminum on SSME, later switched to
  **F-357** (a beryllium-free version of A357) on newer pumps.
- **Turbine housings generally**: Ni-base superalloys Inconel 625/718; precipitation-
  hardening iron-base stainless A-286 and Incoloy 903; Co-base Haynes 188.
- **H2 embrittlement mitigation** on hydrogen-side turbine hardware: gold or copper
  coatings, or iron-based overlays, both chosen for hydrogen impermeability `[p.49]`.
- **RLV-era (late 1990s-2000s) advanced-materials programs** (not yet flight-standard at
  time of writing): **Al/Cu metal-matrix composites (MMC)** proposed for turbopump
  housings — housings are "a very high percentage of a turbopump's total weight," and MMC
  offers high specific strength + tailorable properties; **C/SiC ceramic-matrix-composite
  (CMC)** turbine blisks — demonstrated damage-tolerant (kept running with a cracked
  blade in test) and rated to **2000°F (1093°C)**, vs. **1200°F (649°C)** for nickel-alloy
  turbines — a **~450°C headroom jump** if ever qualified. A 7.6-inch CMC blisk was
  rig-tested `[p.46-47]`.

## Valves (§12.7, p.51–54)

- Housings: cast **A356/A357** or wrought **7075/2024** aluminum (heat-treat must avoid
  stress-corrosion-cracking-susceptible tempers); for higher strength, Ni-base **625/718**
  or titanium (**Ti-6Al-4V**, or **Ti-5Al-2.5Sn-ELI** for LH2 service).
- Poppets: precipitation-hardening stainless **17-4PH / 15-5PH** are the traditional
  choice, but their hydrogen-environment-embrittlement susceptibility and poor cryogenic
  toughness limit their use in H2/cryo service.
- Seals: hard-on-soft pairing — metal against a polymer/elastomer (Teflon, **Kel-F**), or
  a hard(-coated, e.g. tungsten-carbide) metal against a soft metal (a copper alloy). LOX
  service requires both mating surfaces to be independently oxygen-compatible.
- Worked example: **SSME Main Fuel Valve** — housing **Ti-5Al-2.5Sn**, ball/shaft **718**,
  main ball seal **Kel-F** `[p.52]`.

## Lines and ducts (§12.8, p.54–55)

- Default material: **austenitic stainless steel** (weldability, formability, corrosion
  resistance).
- High-Pc staged-combustion engines: **alloy 718** favored for high-specific-strength
  ducting under high discharge pressure.
- **F-1 cost anecdote**: four articulated stainless-steel ducts (>$100,000 total) were
  redesigned into four rigid **6061 aluminum** ducts (~$5,000 total) — a concrete
  material-substitution-driven cost win, not a performance-driven one `[p.55]`.
- Modern: **DMLS** (laser-sintered) **alloy 625** used for the J-2X gas-generator exhaust
  duct at reduced cost/schedule vs. conventional fabrication, hot-fire tested and NDE'd
  successfully `[p.55]`.

## Section map

| Section | Printed p. | Content |
|---|---|---|
| 12.1–12.2 Introduction, propellant/cycle overview | 1–12 | Engine taxonomy, cycle schematics (expander/GG/staged-combustion), historical engine-program survey (Goddard → V-2 → US/Soviet Cold War programs → Apollo → SSME) |
| 12.3 General design considerations for materials selection | 13 | Pressure-fed vs. pump-fed; Table 12.1 real pressure-fed engines (thrust/Pc) |
| 12.4 Materials (general) | 20–21 | The 5-factor selection framework and component-level criteria (above) |
| 12.5 Thrust chamber materials | 21 | Overview; 12.5.1 Injectors (22–26); 12.5.2 Chambers/nozzles/extensions (27–41) |
| 12.6 Turbopump materials | 42–56 | 12.6.1 Intro; 12.6.2 sample turbopump configurations by era (the table above); 12.6.3 turbine drive materials; 12.6.4 pump-element materials |
| 12.7 Valves | 57–60 | Housing/poppet/seal materials, worked SSME valve example |
| 12.8 Lines and ducts | 60–61 | Default materials, F-1 cost anecdote, DMLS example |
| 12.9 Summary + References | 61–65 | AM outlook; 30 numbered references (mostly AIAA papers, NASA reports, and Rocketdyne "Threshold Journal" articles — several are private-communication interviews with retired Peenemünde/NASA engineers, not independently checkable) |

## Caveats

- **No stress/temperature-limit property tables** — this is a "what alloy was used where
  and why" survey, not a materials-properties handbook. Every number above is a real
  historical design choice with page-cited context, not a generic allowable-stress or
  max-service-temperature figure a reader could plug into a margin calculation.
- Several factual claims are sourced to **private communications** (refs 7, 8 — retired
  Peenemünde engineers interviewed in 2002) rather than a citable published document;
  treat V-2-era specifics (steel composition, "high-frequency vibrations" instability
  description) as oral-history-grade, not primary-source-grade.
- The chapter is a **survey of what has been built**, not a **selection recipe** — it
  gives no quantitative crossover criteria for choosing, e.g., channel-wall vs. tubular,
  or Narloy-Z vs. a nickel-base alloy. Any code implication is "here is a real material
  this class of component actually uses," not "here is the equation that picks it."
- Two temperature figures worth flagging for a spot-check: SSME turbine inlet gas
  "~840°C (1550°F)" `[p.44]` and the C/SiC-vs-Ni-alloy turbine temperature-limit
  comparison "2000°F (1093°C) vs. 1200°F (649°C)" `[p.46]` — both stated without a cited
  source of their own within the chapter (i.e., they're the chapter authors' own figures).
