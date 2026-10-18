# Rocketdyne TA3-0337 — J-2S Restart Study (ATSS Task Final Report)

## Identity

J. (John) Vilja & Daniel Levack (Rockwell International, Rocketdyne Division, Canoga Park CA),
*J-2S Restart Study*, **Task Final Report, Advanced Transportation System Studies (ATSS),
Technical Area 3 "Alternate Propulsion Subsystem Concepts"**, contract **NAS8-39210** (NASA
MSFC), DCN 1-1-PP-02147, DR-4, document TA3-0337, **April 1993** (SF-298 at leaf 205: "Task
Final Report, September 1992 - April 1993"). The slides themselves carry footers
"JV/Bv 3/4/93-nn" and "TA3-03xx/04xx". **NTRS 19940016798.**
`literature/Rocketdyne (c.1993) - J-2S Restart Study.pdf` (md5 76259072...; renamed
2026-10-18; the cover and SF-298 date it April 1993, so the "c." in the filename can be
dropped). **206 PDF leaves**, mostly briefing slides rotated 90°/270° on the page. There are
**no printed page numbers**, so cites are by **leaf** (0-based). Tag: `[J2S-Restart]`.

Same authors, contract and year as `[Vilja-J2S]` (AIAA 93-2129,
`sources/vilja-aiaa93-2129-j2s.md`). That paper is the condensed public version of this study.
**RealismOverhaul already cites this document**: `Engine_Configs/J2_Config.cfg` lists it as
"Source 4" (the NTRS 19940016798 URL) for the J-2S config.

## Character

A **contractor briefing book**. Most slides come as a pair: one leaf of prose ("facing text")
followed by the chart or drawing. About 40 % of it is a component-by-component
**producibility review**: valves, ducts, castings and instrumentation, with materials, past test
problems and proposed fixes. The rest is:
- the J-2S baseline;
- the program plan, with cost and schedule;
- a short but valuable **10:1 throttling assessment**. It is the only part with cycle numbers,
  from Rocketdyne's J-2S off-design engine-balance code, anchored on engine J-115's 6:1 AEDC
  throttling data.

Text came from RapidOCR (mean confidence 0.87). Reading order inside slides is scrambled. On
several prose leaves the OCR lost whole lines, so the key ones were rendered and read upright.
**Every number in the tables below was read from the rendered page image.**

What it is best for:
- the **J-2S tap-off turbine-inlet temperature vs power level**;
- **main-injector LOX and fuel dP/Pc vs power level**, with the stability rule and the J-2S's
  real tested floor;
- **vacuum Isp vs power level**;
- **pump speeds vs thrust** (code vs test);
- **where the tap-off gas is diluted** (in the tap-off manifold, by jacket coolant plus
  fuel-bypass coolant);
- the **basic vs with-accessories dry weight**;
- life and endurance requirements;
- the hot-gas valve materials;
- 1992-dollar restart and production costs.

It does **not** give a tap-off flow fraction, a tap-off pressure, pump discharge pressures, an
engine-balance station table, turbine efficiencies or tube counts.

## J-2S rated parameters, life and test basis

Read visually: leaf 8 (headline), leaf 24 (endurance table), leaf 19 (history prose).

| Item | Value | Cite |
|---|---|---|
| Nominal vacuum thrust | 1,178.8 kN (265,000 lbf) | leaf 8 |
| Nominal vacuum Isp | 436 s | leaf 8 |
| Chamber pressure ("nozzle stagnation") | 8.27 MPa (1,200 psia) | leaf 8 |
| Mixture ratio (calibration) | 5.5; PU-commandable to 5.0 and 4.5 | leaf 7-8 |
| Nozzle area ratio | 40:1 | leaf 8 |
| **Basic engine dry weight** | **1,467.4 kg (3,235 lb)** | leaf 8 |
| Engine dry weight **including accessories** | 1,723.7 kg (3,800 lb) | leaf 8 |
| Production-configuration testing | 6 engines, 273 tests, 30,858 s (R&D configuration a further 10,756 s) | leaf 8 |
| Mainstage / low-thrust idle | > 21,400 s / > 6,600 s; "265 tests" in the leaf-19 prose vs 273 on leaf 8 | leaf 19-20 |
| Model-spec life | 30 starts / 3,750 s | leaf 191 |
| Endurance demonstrated (required) | 30 tests (30); 3,807.4 s (3,750); 1,503.9 s at high MR (1,500) | leaf 24 |
| Mission-duty tests | 3 "programmed mixture ratio; 470 sec. duration" tests | leaf 24 |
| Life extension demonstrated | 12,000 s and 30 starts between overhauls | leaf 19-20 |
| Uprate (analysis only) | > 1,423 kN (320,000 lbf), by structural strengthening + Pc increase | leaf 19, 179 |
| Starts | S-II version single start; S-IVB version 3 starts (3 SPGG cartridges) | leaf 9, 21 |

## Throttling assessment (engine-balance code, anchored on J-115 AEDC data)

The code was run at **1.7:1, 3:1, 5:1, 6:1 and 10:1** (= 60, 33, 20, 16.7 and 10 % thrust)
plus 100 % (leaf 179). The values below are **digitized from the plotted points** on leaves 182,
184 and 186, read visually. Precision is about ±0.3 percentage points for dP/Pc, ±0.1 s for
Isp and ±5 R for temperature.

| % nominal thrust | LOX inj dP/Pc | Fuel inj dP/Pc | Vacuum Isp (s) | Tap-off gas T (turbine inlet) |
|---|---|---|---|---|
| 100 | ~17.4 % | ~11.3 % | ~435.0 | ~1,620 R (900 K) |
| 60 (1.7:1) | ~10.5 % | ~11.3 % | ~434.1 | ~1,318 R (732 K) |
| 33 (3:1) | ~5.9 % | ~11.8 % | ~433.2 | ~1,277 R (709 K) |
| 20 (5:1) | ~3.6 % | ~12.7 % | ~432.2 | ~1,268 R (704 K) |
| 16.7 (6:1, "minimum tested") | ~3.0 % | ~13 % | ~431.8 | ~1,266 R (703 K) |
| 10 (10:1) | ~1.8 % | ~14 % | ~430.6 | ~1,262 R (701 K); text "1260 °R" |

**Pump speed vs thrust** (leaf 188, J-115 "throttling test results"; code points with the PU
valve closed, test data with it open and closed). Read visually from a hand-plotted chart, so
treat as ±200 rpm:

| Point | LOX pump | Fuel pump |
|---|---|---|
| ~265 klbf, code | ~8,800 rpm | ~28,800 rpm |
| ~255 klbf, test (PUV closed) | ~8,600 rpm | ~27,600 rpm |
| ~27 klbf (10:1), code | ~3,000 rpm | ~9,700 rpm |

Compare `[SP-8110 Table I]`'s Mark 29 design speeds: 9,050 rpm (ox) and 28,000 rpm (fuel).

## Key results

1. **Tap-off turbine-inlet temperature is about 1,620 R (900 K) at rated thrust, and falls to a
   plateau of about 1,260-1,270 R (700-705 K) below ~33 % thrust** `[J2S-Restart leaf
   185-186]`. "The tap-off cycle maintains satisfactory turbine temperatures over the entire
   throttling range... Even at the 10:1 extreme condition the temperature remains fairly stable
   at 1260 °R."
   - The contrast drawn: GG and staged-combustion turbines get cold enough at deep throttle to
     **ice**, and expander cycles lose turbine power.
   - The 100 % point sits 40 R below `[SP-8110 Table I]`'s J-2S fuel-turbine inlet of 1,200 °F
     (1,660 R, 922 K). That is consistent: one is an off-design-code point, the other a
     design-table value.
   - This is the **first sourced J-2S tap-off gas temperature** in `claude_lit/`. It replaces
     the withdrawn, unsourced "~1,140 K" note (OPEN_QUESTIONS tap-off follow-ups;
     ASSUMPTIONS `TAP_OFF_TEMP_FRACTION` / `TAP_OFF_TURBINE_LIMIT_K` row). The real LOX/LH2
     rated value, **900 K**, is **below** the legacy model's 1,150 K cap.
   - The plateau shows that at deep throttle the turbine-inlet temperature is held by the
     mixing (dilution) ratio, not by chamber temperature.
2. **Where the dilution happens** `[J2S-Restart leaf 21, 22, 41-42]` (read visually).
   - Drive gas "is tapped off through a set of ports from the combustion chamber and
     **immediately diluted with some of the cold hydrogen from the chamber coolant circuit**"
     (leaf 21).
   - The proposed cast tap-off manifold section (leaf 41-42) shows the port supplying hot gas
     "into the **coolant-rich manifold**". The section A-A flow arrows read "nozzle coolant
     plus bypass coolant". In the schematic (leaf 22), the **Fuel Bypass Valve** branches off
     the main fuel line and goes straight to this manifold at the chamber head.
   - So the dilution H2 is the **jacket-exit coolant plus a valved fuel bypass**, mixed in the
     **injector-end manifold that also houses the tap ports**. There is no separate mixer
     vessel, and the gas goes on through the Hot Gas Valve to the fuel turbine.
   - That closes `[Vilja-J2S]` key result 1/3's open "where is the dilution / is the fuel
     bypass the diluent" question.
3. **Tap-port hardware** `[J2S-Restart leaf 29, 33, 41-42]`.
   - The original port was "the only device of its kind ever tested". It was very
     labour-intensive (machined, hand-brazed), and "records indicated that this configuration
     had **life limiting erosion** issues early in the test program".
   - Redesign:
     - a **NARloy-Z-lined port** (forged NARloy-Z tap-off ring and port insert), "cooled
       sufficiently by the surrounding chamber coolant flow to operate without erosion or
       localized melting";
     - chamber tubes that end at the casting and are routed between the ports for cooling;
     - structure cast in **JBK-75** (a castable A-286 grade), replacing **321 CRES**.
   - Dimensions read off the (upside-down) drawing:
     - port centreline about **1.125 in (28.6 mm) from the injector-face plane**;
     - **Ø18.610 in (472.7 mm)** at the chamber wall at the port station;
     - manifold body Ø22.35-22.375 in.
   - The 1.125 in is the drawing's dimension between the injector plane and the port; the
     reading is not certain.
4. **10:1 throttling is limited by LOX-injector stiffness, not by the turbines or the tap-off
   gas** `[J2S-Restart leaf 179-182]`.
   - LOX-element dP/Pc falls roughly in proportion to thrust: about 17 % at rated, about
     **2 % at 10:1**. That is "below the rule-of-thumb minimum stability criteria of about
     5 percent (although this particular engine design was **stable at 3 percent in test**)",
     at the 6:1 point.
   - Fuel dP/Pc *rises* on throttle-down (about 11 → 14 %). The leaf 181 text says it "retains
     its pressure drop to chamber pressure ratio, ensuring injector stability from the
     **chug** mode".
   - Fix: increase LOX orifice resistance. Holding tap-off flow constant, that drops rated Pc
     to **about 1,000 psi (6.9 MPa)**. Alternatively, raise tap-off flow and pump discharge to
     keep Pc; the turbopumps' demonstrated 320 klbf uprate capability gives "more than
     adequate" margin.
   - Unaddressed: "secondary coolant and seal flows which may still require some additional
     modification".
   - Conclusion slide (leaf 180): "6:1 throttling is feasible with baseline configuration;
     10:1 throttling limited by injector stability."
5. **Throttling barely costs Isp** `[J2S-Restart leaf 183-184]`: about 435 → 430.6 s at 10:1
   (−1.0 %). The cause is "reductions in turbopump operating efficiencies at the off-design
   conditions". This is engine-balance code output, not test data.
6. **Engine-model validation** `[J2S-Restart leaf 187-188]`. The off-design code matched
   J-115's measured LOX and fuel pump speeds over about 27-265 klbf; leaf 179 says it "agreed
   very well with the test data all the way to the 6:1 previously tested".
7. **Idle is about 5 % thrust**, and a "**powered idle mode**" was developed to fill the gap
   between it and 6:1 `[J2S-Restart leaf 19]` (read visually). "Development was initiated on
   a powered idle mode which provided throttling in the region between normal idle mode
   (approx. 5% nominal thrust) and the 6:1 regime."
   - This disagrees with `[Vilja-J2S]`'s "stable down to 6,000 lbf" (about 2.3 %) and
     `[AEDC-J2S]`'s 5,000 lbf nominal (about 1.9 %). The 5 % here may be the normal tank-head
     idle level and the others the deepest stable points.
   - The Isp/MR at idle is not given.
   - Idle works through an injector manifold "which only passed oxidizer through the center
     rows of the injector" (leaf 21). The two-piece cast-injector drawing (leaf 38) labels a
     separate "idle mode oxidizer inlet" and compartment.
8. **Weight: the basic engine is 3,235 lb (1,467.4 kg) and 3,800 lb (1,723.7 kg) with
   accessories** `[J2S-Restart leaf 8]` (read visually). RO's J-2S config mass of
   1,467.37 kg (`massMult 0.9366`, header "mass w/o accessories?") is therefore **exactly this
   document's basic engine dry weight**. The guess in RO's header is confirmed, and the
   `[Vilja-J2S]` caveat that "the manufacturer number contradicts that guess" is **withdrawn**:
   Vilja's 3,800 lb is the with-accessories figure.
9. **Hot-gas (tap-off) throttle valve materials and problems** `[J2S-Restart leaf 107-110]`
   (read visually).
   - Materials: butterfly and shaft **René 41**, shaft bearings **Haynes 25**, housing
     **Inconel 625**.
   - Problems: the valve did not go fully closed (butterfly-to-housing interference; the gate
     was reworked to a smaller diameter); shaft bearings seized (the housing was redesigned to
     reduce thermal distortion, but the redesign was never tested); closed leakage varied from
     valve to valve.
   - The **hot-gas check valve** (leaf 127-128): its "springs lost load due to high gas
     temperature" and its flappers cracked in a thin section near the outer edge.
   - These are real hot-gas-service alloy precedents near a ~900 K H2/steam stream. René 41
     also appears in OPEN_QUESTIONS' turbine-alloy wish list. **The turbine's own blade and
     disk alloys are not given anywhere in this document.**
10. **Cooling-jacket topology** `[J2S-Restart leaf 43-48]`. Proposed producibility changes:
    - a cast integral jacket that includes the **fuel bypass manifold**, saving more than
      250 in of welding;
    - a **one-piece full-length jacket to the nozzle exit**, which reduces tube-to-tube braze
      and eliminates hatbands, with chem-milled waffle, honeycomb and rolled-tube-hatband
      alternatives;
    - a **cast tube turnaround**: "numerous cast triplets to turn the flow around from the
      **single down-pass tube to the two up-pass tubes**", which eliminates large forged
      rings and more than 485 in of pressure-vessel welding.

    This corroborates `[AEDC-J2S]`'s 180-down / 360-up (1:2) tube splice. **No tube count is
    stated here.**
11. **Turbopumps** `[J2S-Restart leaf 59-64]`.
    - Mk-29F fuel pump development problems:
      - inducer suction performance and blade fatigue, cured by recontouring;
      - pump-end ball-bearing unloading ("cocking" of the carrier, loss of preload and of the
        bearing-support pilot), to be fixed by a stiffer support plus a modern carrier,
        preload and anti-rotation design.
    - Mk-29F producibility change: a **cast titanium impeller** replacing a three-piece
      impeller machined from forgings.
    - The Mk-29O LOX pump ("perhaps the most successful oxidizer turbopump design") needs
      only new dynamic seals.
    - Turbine exhaust: there is a cast turbine-exhaust manifold option (leaf 51-52). The
      **oxidizer-tank repressurization heat exchanger sits in the ox turbine exhaust duct**,
      using a bifurcated two-tube coil after J-2 flow instability (leaf 167-168).
12. **Hydrogen tap-off tank pressurization** is a real J-2S function `[J2S-Restart leaf 24]`:
    1 "hydrogen tapoff pressurization performance point test", plus 2 heat-exchanger
    pressurization tests. The engine pneumatic helium tank is **700 in³ (11.5 L)**; an 886 in³
    tank is available (leaf 161-162; operating and proof pressures are referred to but not
    given).
13. **Restart cost and schedule (constant FY1992 $)** `[J2S-Restart leaf 193-198]` (read
    visually).
    - **Non-recurring to single-engine certification: $245M.** That is $140M manufacturing
      facilities activation (incl. $65M machine tools and $5M drawing update) plus $105M
      development/verification (incl. $65M hardware for 7 engines). A Rocketdyne test-facility
      refurbishment of $13M is separate.
    - Schedule: go-ahead FY94, CDR FY95, engine deliveries FY96-FY97, certification mid-FY98.
    - **Production unit cost** (fee excluded):
      - first unit ~$10.8M at 3/yr, falling to ~$8.2M at 30/yr;
      - 10-year average ~$9.6M at 3/yr, ~$7.0M at 14/yr, ~$6.3M at 30/yr.

      These are digitized and approximate, and do not include the producibility savings.
    - Development test matrix: 6 engines, **210 tests / 25,000 s**. Four engines go to the
      3,750 s spec life and two to 5,000 s.
14. **Producibility verdict** `[J2S-Restart leaf 175-176, 204]`. The engine could be built
    "to existing drawings"; "no material changes required"; only the electronics must be
    replaced. The study counts:
    - 24 producibility changes;
    - 20 fabrication-technique changes;
    - 12 material substitutions;
    - 11 reliability/operability enhancements.

## Section map

Physical order differs from the agenda (leaf 4: Background, Study Approach, Baseline, Restart
Program Plan, Throttling Assessment, Producibility Assessment). Grouped by agenda below.
"Facing text" = the prose leaf before each chart.

**Front matter**
- Leaf 0: cover. Read.
- Leaf 1-2: objectives. Read.
- Leaf 3, 5: blank.
- Leaf 4: agenda. Read.
- Leaf 205: SF-298. Read.

**J-2S Background**
- Leaf 7-8: Basic engine features / performance & weight. **Read visually.**
- Leaf 19-20: J-2S history (life extension, 6:1, powered idle, uprate). **Read visually.**
- Leaf 21-22: J-2S schematic plus tap-off/PU/idle/throttle prose. **Read visually.**
- Leaf 23-24: endurance, safety and performance testing table. **Read visually.**
- Leaf 25-26: J-2/J-2S application investigations (ALS 88, Shuttle Orbiter 71/72). **as-needed - not read (2026-10-18).**

**J-2S Study Approach**
- Leaf 12-16: groundrules and task flow. Read (OCR); no numbers.

**J-2S Baseline**
- Leaf 6, 9-10: baseline study configuration (265 klbf, 3 starts, idle, PU retained). Read (OCR).

**Producibility Assessment** (the bulk of the document)
- Leaf 28-36: overview, component list, in-depth reviews, general recommendations. Read (OCR).
- Leaf 37-38: two-piece cast injector (idle-mode ox compartment, brazed fuel sleeves). Read (OCR); drawing glanced.
- Leaf 39-42: cast tap-off manifold and **proposed tap-off manifold redesign**. **Read visually (41-42).** Leaf 40 drawing **as-needed - not read (2026-10-18).**
- Leaf 43-48: cast integral jacket with bypass manifold, full jacket to exit, cast tube turnaround. **Read visually (45, 47)**; leaf 43 OCR; drawings 44/46/48 **as-needed - not read (2026-10-18).**
- Leaf 49-52: cast fuel inlet manifold, cast turbine exhaust manifold. Read (OCR); drawings **as-needed - not read (2026-10-18).**
- Leaf 53-58: ASI and SPTS (RD-135 grain, NSI initiator). Read (OCR); drawings **as-needed - not read (2026-10-18).**
- Leaf 59-64: Mk-29F / Mk-29O turbopumps. **Read visually (59)**; 60, 63-64 OCR.
- Leaf 65-88: ducts (fuel/ox inlet scissors → wrap-around, discharge, bypass, idle-mode, ox turbine bypass, crossover, ox turbine exhaust, hot-gas tap-off duct, misc tubes/hoses). Prose read (OCR); duct drawings **as-needed - not read (2026-10-18).**
- Leaf 89-138: valves (MFV, MOV, PU, fuel bypass, **hot-gas tap-off valve 107-110**, idle-mode, anti-flood, relief, He fill check, **hot-gas check 127-128**, misc check valves/purges). Material/problem leaves 92, 96, 104, 108, 112, 116, 128, 136 read (OCR; 108 checked against text). Other drawings **as-needed - not read (2026-10-18).**
- Leaf 139-156: flight instrumentation (summary, sensor list, pressure/temperature/flow/speed sensor technology). **Leaf 142, 144 read visually** (see Caveats); 146 OCR; 147-156 **as-needed - not read (2026-10-18).**
- Leaf 157-166: pneumatic control assembly, helium tank, gimbal bearing, interface panels. Read (OCR); **162 read visually.**
- Leaf 167-168: ox-turbine-exhaust heat exchanger. **Read visually.**
- Leaf 169-176: producibility summary tables and conclusions. Read (OCR).

**Throttling Assessment**
- Leaf 178: divider.
- Leaf 179-188: 10:1 throttling examination, injector dP vs power, Isp vs power, turbine inlet T vs power, pump speeds code vs test. **All read visually.**

**Restart Program Plan**
- Leaf 190: divider.
- Leaf 191-192: groundrules. Read (OCR).
- Leaf 193-198: development cost elements, schedule, production costs. **194, 196, 198 read visually.**
- Leaf 199-202: test philosophy and test matrix. **202 read visually.**
- Leaf 203-204: conclusions. Read (OCR).

Blank / "preceding page blank" / divider leaves (11, 17-18, 27, 57, 61-62, 65, 93, 97, 101,
105, 109, 113, 117, 121, 125, 129, 133, 137, 143, 145, 159, 177, 189) have no content.

## Caveats

- **The throttling numbers are engine-balance code output.** Only the pump speeds (leaf 188)
  are overlaid with test data, and only down to 6:1 was tested. The 10:1 row is a prediction.
  All table values are digitized from small plots; trust trends to a few percent, not the last
  digit.
- **The 100 % Isp point plots at about 435 s**, not the headline 436 s (leaf 8). Same code, a
  slightly different rated point; the reason is unexplained.
- **No tap-off flow fraction or pressure anywhere.** The turbine-inlet temperature is the only
  tap-off state given. `[SP-8110 Table I]` remains the source for the J-2S turbine inlet
  pressure (fuel 889 psia, PR 7.30; ox 100 psia, PR 2.68).
- **Instrumentation-list ranges (leaf 142, 144) are not usable as operating data.** Read
  visually, they list:
  - pressures: fuel turbine inlet **25-46 psia** and ox turbine inlet **39-53 psia**, which
    are physically inconsistent with SP-8110's 889 / 100 psia at main stage (possibly idle-mode
    or mislabelled ranges); ox turbine exhaust 0-100 psia; both pump discharges 0-2,500 psia;
    chamber 0-1,500 psia; idle-mode Pc 0-50 psia;
  - temperatures: "fuel turbine inlet" −424/−418 °F and "oxidizer turbine inlet" −298/−284 °F.
    These are LH2/LOX-like ranges, so the measurement column appears shifted relative to the
    range column; they are probably the fuel- and ox-pump discharge temperatures, but that
    cannot be confirmed from the page. Ox turbine outlet 0 to +1,000 °F.

  Cite none of these as engine data.
- **Engine and test counts disagree inside the document.** 265 vs 273 production tests
  (leaf 19 vs 8). Restart engines: "six development + two certification" in the schedule
  prose (leaf 195), D1-D5 + C1-C2 on the chart (leaf 196), "Hardware (7 engines)" in the cost
  breakdown (leaf 194), and 6 engines in the test matrix (leaf 202).
- **Idle level conflicts across sources**: about 5 % here; about 2.3 % in `[Vilja-J2S]` (same
  authors, same year); about 1.9 % nominal in `[AEDC-J2S]`. Probably normal tank-head idle vs
  deepest demonstrated; not resolved by the text.
- **Costs are 1992 contractor estimates** for a never-executed restart, excluding fee,
  contingency, government support and propellants. Useful only as order-of-magnitude
  context, e.g. for `physics/cost_model.py`'s tap-off premium.
- About 150 producibility, drawing and sensor-technology leaves were logged from OCR only,
  per Cory's targeted-read rule for this document. They are flagged in the Section map.
