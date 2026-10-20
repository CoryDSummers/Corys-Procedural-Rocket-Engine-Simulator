# D5-15772-2 — Systems Description, J-2S Improvement Study

## Identity

The Boeing Company, Aerospace Group, Southeast Division (Saturn V systems integration; study
manager **J. E. Martin**), *Systems Description - J-2S Improvement Study*, document
**D5-15772-2**, **April 30, 1969**. Contract **NAS8-5608, Schedule II, Part VII, Task 10**
(NASA MSFC), issued to the Space Division, Launch Systems Branch. Stage-contractor inputs are
folded in: North American Rockwell Space Division (S-II, from SD-69-82-1), McDonnell Douglas
(S-IVB, from DAC-56749), IBM (IU, from 69-K44-0001); D5-15772-4 / -8 and D5-16793 are companion
volumes not held. Every engine number in it is quoted from **Rocketdyne report R-7211, "J-2S
Interface Criteria Document"** (rev. 7 May 1968), which is not in `literature/`.
`literature/J-2S_Study_30_April_69.pdf` (filename kept as delivered; md5 991c8add...;
**1,453 PDF leaves**, leaf 0-1452; a byte-identical copy sits in `literature/duplicates/`).
No NTRS/DTIC accession known. Tag: `[J2S-Boeing69]`.

Page-to-leaf offsets (printed page "s-N" → leaf): front matter leaves 0-53 (cover 0, title 1,
abstract iii = 3, contents iv-ix = 4-9, illustration/table lists 10-31, abbreviations 32-43,
references xliv-lii = 44-52, foreword liii = 53); §1 1-1 = leaf 54; **§2: leaf = 55 + N**;
§3: 115 + N; **§4: 119 + N**; **§5: 163 + N**; §6: 193 + N; §7: 197 + N; §8: 297 + N;
§9: 315 + N; **§10 has no fixed offset** (fold-outs; 10-1 = leaf 320, 10-103 = 419, 10-424 =
736, 10-547 = 846, 10-1010 = 1304); §11 11-1 = 1312; §12 12-1 = 1320; App. A: 1333 + N.
Cites below give the printed page and the leaf.

## Character

A **vehicle-integration** study (Phase C-preparatory) of putting J-2S engines in the Saturn V
S-II (5 engines) and S-IVB (1 engine) stages: trade studies, four design missions, stage
modifications, GSE/KSC impact, cost and schedule. It is overwhelmingly stage-side. The engine
content is concentrated in **§4 "J-2S Engine Description"** (pp.4-1 to 4-44, leaves 120-163),
which is a near-verbatim **condensed engine model specification** (Rocketdyne-letterhead
figures, "shall" language) reproduced from R-7211, plus scattered stage-interface numbers in
§10 (pressurant tap pressures/temperatures, NPSH, flows, turbine speed, drop weights).

Trustworthiness: high for what it states, since it is the contractual interface spec, but these
are **1968 specification values** (minimum/maximum guarantees and 3-sigma bands), not test
data, and the S-II and S-IVB contractors occasionally quote slightly different R-7211 revisions
(see Caveats). It contains **no cycle-balance data at all**: no chamber pressure for main stage,
no tap-off gas temperature/pressure/flow, no turbine or pump efficiencies, no pump discharge
pressures, no tube counts, no materials. Its best uses are:
- the **specification-level** J-2S envelope: thrust calibration range, Isp vs MR, engine flows,
  weights (dry/burnout/wet, with and without accessories), service life, rated durations;
- the **idle mode** as specified (flows, MR, Isp, Pc, thrust, durations, restart behaviour);
- **NPSH requirements** and inlet-pressure start boxes (suction model anchors);
- the **engine-supplied tank pressurant**: GOX/helium heat-exchanger outlet envelopes and the
  GH2 tap pressure/temperature, which bound pump discharge / injector-manifold pressures;
- transients (start/cutoff impulse, decay times, start/cutoff propellant consumption).

Text: leaves are a mix of a usable NTRS text layer and RapidOCR. All tables and figures cited
below were **read visually** from rendered PNGs (`.lit_work/png/J_j2s/`); OCR was used only to
find them.

## J-2S specification parameters (R-7211 via this document)

**Main stage** `[J2S-Boeing69 §2.2 p.2-1 leaf 56; §4.0 pp.4-1..4-5, leaves 120-124; Table
4.0-III p.4-5]`:

| Item | Value |
|---|---|
| Vacuum thrust | any precalibrated level **230,000-265,000 lbf (1,023-1,179 kN)**, +-3 % |
| Calibration MR | **5.50 +-2 %**; PU valve range **4.5-5.5** (bypasses LOX from ox-pump discharge) |
| Min. instantaneous vacuum Isp | **427 s** (spec guarantee; Fig. 4.0-3 nominal is 431 s at MR 5.5) |
| Expansion ratio | 40:1 |
| Engine duct inlet pressure (total) | fuel **30 psia (207 kPa)**, oxidizer **39 psia (269 kPa)** |
| Propellant densities assumed | LH2 4.40 lb/ft3 (70.5 kg/m3); LOX 70.79 lb/ft3 (1,134 kg/m3) |
| Rated duration | **500 s** main stage per burn; idle **1,000 s** max (total) |
| Restarts | **2 restarts** to main stage (3 starts) in orbit, coasts up to 10 h each (20 h total); min coast **300 s** (Fig. 4.0-11) |
| Service life | **3,750 s** main stage + **3,500 s** idle; **30 starts** to main stage + 10 idle-only starts |
| Envelope | ~81 in dia (2.06 m) x 133 in max length (3.38 m); 116 in (2.95 m) gimbal-to-exit (Fig. 2.2-1) |
| Prelaunch redline | one: He control tank pressure |

**Weight** `[Table 4.0-I / 4.0-II p.4-4, leaf 123]` (read visually):

| | Dry | Burnout* | Wet |
|---|---|---|---|
| Rocket engine | **3,235 lb (1,467.4 kg)** | 3,288 lb | 3,347 lb |
| Accessories | 565 lb (256.3 kg) | 625 lb | 630 lb |
| Restart accessories (multi-start only) | 250 lb (113.4 kg) | 221 lb (as printed) | 250 lb |
| **Total dry, single start** | **3,800 lb (1,723.7 kg)** max | | |
| **Total dry, multiple start** | **4,050 lb (1,837.0 kg)** max | | |

\*Dry plus fluids remaining at the end of rated duration. Installed S-IVB deltas `[§10.3.5.2
p.10-547, leaf 846]`: remove J-2 **-3,515 lb**; add J-2S with 2 SPTS **+3,960 lb**, with 3 SPTS
**+4,021 lb** (so ~61 lb per extra starter cartridge, derived).

**Idle mode, steady state, liquid propellants** `[Table 4.0-IV p.4-10, leaf 129]` (read
visually):

| LOX / fuel inlet (total) | LOX flow | Fuel flow | MR | Min Isp | Thrust (vac) | Pc (injector end, vac) | Rated duration |
|---|---|---|---|---|---|---|---|
| 39 / 30 psia | 12.5 +-2.5 lb/s (5.67 kg/s) | 5.0 +-1.0 lb/s (2.27 kg/s) | 2.5 +-0.5 | 280 s | **5,000 +-1,000 lbf (22.2 kN)** | **26 +-5 psia (179 kPa)** | 1,000 s total |

**Main-stage flows at 265K** (R-7211, quoted by the S-II contractor `[§10.2.2.4.1 p.10-110,
leaf 426]`): MR 5.5: LOX **525 lb/s (238.1 kg/s)**, LH2 **95 lb/s (43.1 kg/s)**; MR 5.0: 450 /
88 lb/s. J-2 flow tolerances (5.5 % fuel, 4 % LOX) assumed for the J-2S.

**NPSH required** (maximum value of minimum NPSH, at the engine-vehicle interface, with
<= **4 % pump head loss** from cavitation `[p.4-35, leaf 154]`), read visually:

| Source | LH2, MR 4.5-5.0 | LH2, MR 5.5 | LOX, MR 4.5-5.0 | LOX, MR 5.5 |
|---|---|---|---|---|
| §4 Figs 4.0-23/24 `[pp.4-38/39, leaves 157-158]` (no thrust level stated) | **164 ft (50.0 m)** | **176 ft (53.6 m)** | **31.9 ft (9.72 m)** | **42.3 ft (12.9 m)** |
| S-II Fig. 10.2-69, **265K** `[p.10-109, leaf 425]` | 197 ft (60.0 m) | 216 ft (65.8 m) | 31.9 ft | 42.3 ft |
| S-II Fig. 10.2-69, **230K** | 164 ft | 176 ft | 26.0 ft (7.92 m) | 34.5 ft (10.5 m) |

In psi (S-II text, p.10-110): LOX 20.8 psi (143 kPa) at 5.5 / 15.7 psi at 5.0; LH2 6.6 psi
(45.5 kPa) at 5.5 / 6.02 psi at 5.0. The NPSH is flat from MR 4.5 to 5.0 and rises to MR 5.5.

## Key results

1. **Isp vs mixture ratio, spec curve** `[Fig. 4.0-3 p.4-8, leaf 127; Fig. 5.1-2 p.5-4, leaf
   167]` (read visually). Nominal **431 s at MR 5.5**, band 427 (min, -3 sigma) to 435 (max).
   The nominal rises roughly linearly to **~437 s at MR 4.5** (visual, +-1 s). Fig. 5.1-2 (the
   R-7211 curve used in the trades) gives the S-IVB engine 437.2 s at MR 4.5 → 431.0 s at 5.5,
   and the text quotes **434.5 s at MR 5.0** `[§5.1 p.5-1]`. The S-II engines' simulated curve
   sits ~2 s lower (435.2 → 429.0 s), unexplained in the parts read. "Isp is a function of MR
   but independent of the calibrated thrust level" `[§5.1 p.5-1]`. Slope: about **-6 s per unit
   MR** between 4.5 and 5.5 (derived).
2. **Thrust vs MR** `[Fig. 4.0-1 p.4-6, leaf 125; Fig. 5.1-1 p.5-3, leaf 166]`. A
   265K-calibrated engine gives 265K at MR 5.5 but only **210K at MR 4.5**; a 230K engine gives
   230K → 183K. +-3 sigma: 276K / 221K (upper), 220K / 173K (lower). So thrust falls **~21 %**
   from MR 5.5 to 4.5 at fixed calibration (derived), because the PU valve only trims LOX flow.
   The S-II's optimal schedule is MR **5.0 (2.5 s at start, required by the engine) → 5.5 →
   4.7**; the S-IVB is best at constant MR `[§2.3.2 p.2-3; §5.2 p.5-2]`.
3. **Weight: RO's J-2S dry mass is the engine WITHOUT accessories** `[Table 4.0-I p.4-4]`. The
   rocket-engine dry weight is **3,235 lb = 1,467.4 kg**, which is exactly RO's
   `Engine_Configs/J2_Config.cfg` J-2S dry mass (1,467.37 kg, massMult 0.9366, header "mass w/o
   accessories?"). The 3,800 lb of `[Vilja-J2S]` is the same engine **plus 565 lb of
   accessories**; the restart kit adds 250 lb (4,050 lb). This **corrects** the
   `sources/vilja-aiaa93-2129-j2s.md` Caveat that says the manufacturer number contradicts RO's
   guess: both numbers are right, on different bases.
4. **Idle mode is pressure-fed tank-head operation with the turbopumps stopped** `[Fig. 4.0-27
   p.4-43, leaf 162]` (read visually): "combustion is supported by a portion of the main
   combustor injector"; it can be initiated with gaseous or liquid propellants. Labelled
   hardware: P.U. valve, idle-mode oxidizer bypass, T/C (thrust-chamber) bypass, tap-off valve,
   MOV, MFV, SPTS, a "mixture ratio control orifice".
   - Steady idle: **5,000 +-1,000 lbf, MR 2.5, Pc 26 psia, Isp >= 280 s** (table above). Derived
     check: 5,000 / 17.5 lb/s = 286 s, consistent.
   - **Idle Isp vs MR** `[Fig. 4.0-5 p.4-11, leaf 130]` (visual): ~240 s at MR 0.5, a broad
     peak **~284-285 s at MR ~1.5-2**, ~280 s at MR 2.8, ~259 s at MR 5, ~222 s at MR 10.
   - **Restart on warm ducts** starts at ~1,000 lbf on gas/two-phase propellant and rises as
     liquid arrives `[§10.3.2.2 p.10-427, leaf 738]`; the S-IVB hydraulics section quotes
     **1,350 lbf at start rising to 5,000 lbf over up to 100 s** `[§10.3.2.8 p.10-464, leaf 768]`.
     The S-II LEO restart analysis lands at **MR ~1.45, ~4,400 lbf average** on tank pressures
     after a 45-min coast `[p.10-118, leaf 434]`.
   - Idle doubles as the **chill-down**: main-stage restart must be preceded by **30-100 s of
     idle** to chill the feed system; first start needs only >= 1 s idle; steady idle within
     100 s `[pp.4-10, 4-40; Fig. 4.0-11 p.4-19]`. It replaced the S-IVB/S-II recirculation
     chill systems, prevalves and ullage motors `[§10.3.2.2; §10.3.2.6 p.10-445]`.
5. **Mainstage start and inlet conditions** `[Fig. 4.0-25 p.4-41, leaf 160]` (read visually):
   safe start box **fuel 27-40 psia, ox 33-45 psia**; extended (sea-level static only) to fuel 46
   / ox 53 psia. First start can be on gas, two-phase or liquid in the ducts provided run NPSH
   exists at the tank outlets `[p.10-445]`. Before the first start, propellants are supplied to
   the engine 1-18 h ahead; restart inlets must be colder than -100 F `[p.4-40]`. The
   **thrust-chamber fuel-jacket bypass** allows an ambient (unchilled) chamber at start, which
   eliminated the J-2's cold-helium chamber preconditioning; the **tap-off drive "relaxes the
   4.5:1 EMR restraint during engine restart"** `[§10.3 p.10-385, leaf 697]`.
6. **Transients** `[pp.4-10, 4-17, 4-18, leaves 129, 136-137]`:
   - thrust rise <= 40,000 lbf per 10 ms; start consumption (first start, or main-stage start
     after long idle) **280 +-30 lbm fuel, 1,010 +-110 lbm LOX**;
   - main stage → zero: to 8,000 lbf in <= 600 ms, zero in <= 2.5 s; cutoff impulse <= 67,000
     lbf-s (298 kN-s), +-6,500 lbf-s repeatability; consumption 40 +-8 lbm fuel, 91 +-18 lbm LOX;
   - main stage → idle: below 8,000 lbf within 4 s; impulse (4 s window) <= 110,000 lbf-s;
     83 +-10 lbm fuel, 138 +-23 lbm LOX;
   - idle → zero: <= 2.0 s; <= 7,000 lbf-s; 20 +-4 lbm fuel, 7.5 +-1.5 lbm LOX.
   - S-IVB drop-weight table `[Table 10.3.5-II p.10-550, leaf 849]` (visual): **turbine-spin
     (SPTS) propellant 10 lbm per start**; idle-mode start 13 lbm LOX / 5 lbm LH2; main-stage
     thrust build-up 365 lbm LOX / 145 lbm LH2; thrust decay 91 / 40 lbm (matching the spec).
7. **Engine-supplied tank pressurants** `[pp.4-18..4-25, leaves 137-144]` (figures read
   visually):
   - **GOX heat exchanger** (heats LOX "tapped from the engine system", or vehicle helium):
     design point **190 F (361 K) at 2 lb/s (0.91 kg/s)**, nominal 230K, MR 5.5; flow range 1.0-
     3.0 lb/s; minimum outlet pressure "4?0 psia" (middle digit illegible in the scan). Fig.
     4.0-12 envelope: ~185 to ~635 F (358-608 K) at 1 lb/s, ~-85 to ~210 F (208-372 K) at
     3 lb/s; closed PU valve runs hotter. Fig. 4.0-13 outlet pressure: up to **~1,530 psia
     (10.5 MPa)** at 1 lb/s (265K, closed PU), ~400 psia lowest (230K, open PU, 3 lb/s). GOX and
     helium Mach <= 0.3 everywhere in the system.
   - **Helium coil**: supplied at 350 psia (2.41 MPa; Fig. 4.0-15 says 350-700 psia) and 40 R
     (22 K; figure: -390 to -424 F); outlet >= 200 psia (1.38 MPa) over **0.05-0.34 lb/s
     (0.023-0.154 kg/s)**. Outlet temperature (Fig. 4.0-15): ~370-750 F (461-672 K) at
     0.05 lb/s, ~95-440 F (308-500 K) at 0.34 lb/s.
   - **GH2 pressurant tap**: "from a thrust chamber tap" `[p.4-22]`, i.e. "tapped off of the
     fuel injector" `[§10.3.7.1, leaf 897]`; up to **3.0 lb/s (1.36 kg/s) at -320 to -190 F
     (78-150 K)**. Fig. 4.0-16: ~**1,300 psia (8.96 MPa)** at zero flow (265K, max PU), falling
     with flow; the S-IVB schematic labels the orifice outlet **1,150 psia, -260 F (7.93 MPa,
     111 K)** `[Fig. 10.3.2-6 p.10-441, leaf 749]`.
   - **J-2S vs J-2 stage impact** `[§10.2.2.4.1 p.10-103, leaf 419]`: GOX HX outlet pressure
     **1,700 psia (J-2S) vs 1,100 psia (J-2)**; GOX outlet **620 F max (600 K) vs 440 F
     (500 K)**, so four S-II engines' HX output suffices and the centre-engine line is deleted;
     GH2 tap **1,300 psia max vs 900 psia**. The stage lines needed orifices and requalification.
   - **No heat-exchanger weight, coil area or heat-duty number is given.**
8. **Turbopump-side numbers visible from the stage** (the only ones in the document):
   - **LOX turbopump speed** (which drives the S-IVB hydraulic pump directly): nominal
     **10,500 rpm**, max 10,870, pump-spec overspeed 12,000; J-2: 8,000 / 8,700 / 10,000
     `[§10.3.2.8 p.10-464, leaf 768]`. 10,500 matches `[AEDC-J2S]`.
   - **LOX turbopump exhaust hood gas temperature at engine cutoff: 730 F (661 K) J-2S vs 675 F
     (630 K) J-2** (an estimate, for hydraulic-pump soak) `[§10.2.2.6 p.10-142, leaf 458]`.
     Drive-pad/spline temperature range with exhaust gases: -250 to +900 F (117-755 K), same as
     the J-2 `[p.10-466, leaf 770]`.
   - Engine instrumentation ranges `[Table 10.3.3-VI pp.10-512..517, leaves 811-816]` (visual):
     fuel turbine inlet pressure **0-1,500 psia**, ox turbine inlet pressure **0-200 psia**, main
     fuel and main ox injection pressures **0-2,500 psia**. These are transducer full-scale
     ranges, not operating values (consistent with `[SP-8110]`'s 889 psia fuel-turbine inlet).
   - The stage test plans list "tapoff gas pressure/temperature, fuel and ox turbine inlet
     temperature/pressure" as quantities to be measured `[§10.3.7 pp.10-588..589, leaves
     887-888]`; no values are given.
9. **Derived bounds on pump/manifold pressures** (this note's inference, not stated):
   - If the GOX coil is fed from LOX pump discharge (the spec says only "tapped from the engine
     system"), LOX pump discharge is **>= 1,700 psia (11.7 MPa) ≈ 1.42 x Pc** (Pc 1,200 psia
     from `[Vilja-J2S]`).
   - The GH2 pressurant comes off the fuel injector at up to 1,300 psia, so the fuel-injector
     manifold runs **>= ~1.08 x Pc**; fuel-pump discharge = that plus the jacket dP (not given).
10. **Main-stage flows vs thrust** (derived): 525 + 95 = 620 lb/s (281.2 kg/s) at 265K gives
    265,000 / 620 = **427.4 s**, i.e. the R-7211 flows are sized at the 427 s minimum Isp. At the
    431 s nominal the flow would be 614.8 lb/s (278.9 kg/s).
11. **Service life vs RO** (report only): spec life 3,750 s main stage / 30 starts against RO's
    `testedBurnTime = 12000` (comment "design lifetime 12000 seconds") and `[Vilja-J2S]`'s
    11,508.8 s demonstrated on one engine. RO's `ratedBurnTime = 500` and 300 s restart window
    match this spec exactly.

## Section map

- Leaves 0-53, front matter (cover, title, abstract, contents, lists, abbreviations,
  references, foreword). Contents, abstract, foreword, part of references read.
- §1 Introduction, p.1-1..1-2 (leaves 54-55). **as-needed - not read (2026-10-18)** - study
  background.
- **§2.0-2.2 General / Objectives / J-2S Engine Description, p.2-1..2-2 (leaves 56-57). Read;
  Fig. 2.2-1 general arrangement read visually.**
- §2.3 Trade studies summary, p.2-3..2-4 (leaves 58-59). Read.
- §2.4-2.9 summaries of environments, performance, stage descriptions, KSC, SE&I, resources,
  p.2-5..2-57 (leaves 60-112). **as-needed - not read (2026-10-18)** - summaries of §§7-11.
- §2.10-2.11 Problem areas, conclusions, recommendations, p.2-58..2-60 (leaves 113-115). Read.
- §3 Study objectives and ground rules, p.3-1..3-4 (leaves 116-119). Skimmed (engine data
  from R-7211; J-2S effectivity SA-518; 1968 dollars).
- **§4 J-2S Engine Description (engine spec: features, envelope, weights Tables 4.0-I/II,
  main-stage Table 4.0-III, Figs 4.0-1..4 thrust/Isp/flow vs MR, idle Table 4.0-IV and Figs
  4.0-5..9, transients and Fig. 4.0-10, start/restart Fig. 4.0-11, pressurant HX and GH2 tap
  Figs 4.0-12..16, external requirements (propellant spec, helium tank and Table 4.0-V
  consumption, electrical Figs 4.0-17..20, purges Figs 4.0-21/22), NPSH Figs 4.0-23/24, start
  box Fig. 4.0-25, idle Fig. 4.0-27, PU Fig. 4.0-28), p.4-1..4-44 (leaves 120-163). Read in
  full; all tables and the performance/HX/NPSH/start figures read visually.** Figs 4.0-2
  (thrust vs altitude), 4.0-6..9 (idle vs inlet conditions), 4.0-10 (thrust build-up),
  4.0-26 (restart inlet box, leaf 161, scan garbled) and 4.0-28 (PU calibration) not digitized.
- §5.0-5.2 Trade studies: thrust trades and MR trades (Figs 5.1-1/5.1-2 = R-7211 thrust and Isp
  vs MR), p.5-1..5-5 (leaves 164-168). **Read; Figs 5.1-1/5.1-2 read visually.**
- §5.2.1.2-5.3.4 S-II/S-IVB MR optimization detail, missions/profiles/payload envelopes,
  p.5-5..5-30 (leaves 168-193). **as-needed - not read (2026-10-18)** - stage payload trades.
- §6 Vehicle description, p.6-1..6-4 (leaves 194-197). **as-needed - not read (2026-10-18)**.
- §7 Vehicle environments (trajectories, weights, aerodynamics, structural loads, heating,
  control), p.7-1..7-100 (leaves 198-~297). **as-needed - not read (2026-10-18)** - vehicle
  loads/aero; §7.6 heating is aerodynamic, not engine.
- §8 Performance/mission analysis, p.8-1..8-15 (leaves 298-~312). **as-needed - not read
  (2026-10-18)** - payload comparisons.
- §9 Payload exchange ratios, p.9-1..9-2+ (leaves 316-319). **as-needed - not read
  (2026-10-18)**.
- §10.1 S-IC stage, p.10-1..10-6 (leaves 320-325). **as-needed - not read (2026-10-18)**.
- §10.2 S-II/J-2S stage: structures 10-7 (leaf 326); mechanical 10-38 (357), of which
  **§10.2.2.4 pressurization pp.10-103..10-128 (leaves 419-444) read** (GOX/GH2 tap pressures,
  NPSH Fig. 10.2-69, ullage factors Table 10.2-VII, idle restart Fig. 10.2-74, settling vent),
  and the hydraulic-soak paragraph p.10-142 (leaf 458) read; electrical 10-146 (462), thermal
  protection/base heating 10-208 (524), RCS 10-211 (527), weights 10-235 (551), GSE 10-267,
  integrated tests 10-330 (645), checkout 10-346 (658), launch ops 10-361 (673), reliability
  10-373 (685: stage reliability 0.95 → 0.954 with J-2S; skimmed), design-modification
  summary 10-374 (686). Engine-measurement tables p.10-197..10-200 (leaves 513-516) skimmed.
  Rest **as-needed - not read (2026-10-18)** - stage structures/electrics/ops.
- §10.3 S-IVB stage: stage design 10-386 (698); **§10.3.2 propulsion/mechanical pp.10-424..
  10-466 (leaves 736-770) read** (fluid service, feed/chill-down deletion, fuel pressurization
  schematic Fig. 10.3.2-6 read visually, hydraulic pump vs LOX-turbine speed); electrical
  10-480 (784) with **instrumentation Table 10.3.3-VI pp.10-512..517 (leaves 811-816) read
  visually**; weights 10-533 (832) with **§10.3.5.2-5.3 (leaves 846-851) read** (engine weight
  deltas, drop weights; Table 10.3.5-II visually); GSE 10-553 (852-862) skimmed; systems test
  10-583 (882) test objectives skimmed for tap-off items (leaves 887-922); reliability 10-634
  (931). Rest **as-needed - not read (2026-10-18)**.
- §10.4 Instrument Unit, p.10-651..10-803 (leaves ~948-1100). **as-needed - not read
  (2026-10-18)** - IU structure/software/avionics.
- §10.5 Astrionic system integration (LOR/synchronous/LEO/polar), p.10-804..10-967 (leaves
  ~1101-1261). **as-needed - not read (2026-10-18)** - only engine-signal interface lists.
- §10.6 Vehicle final weights, p.10-968 (leaf 1262). **as-needed - not read (2026-10-18)**.
- §10.7 KSC launch operations impact, p.10-984..10-1009 (leaves 1278-1303). **as-needed - not
  read (2026-10-18)**.
- §10.8 SE&I, p.10-1010+ (leaves 1304-1311). **as-needed - not read (2026-10-18)**.
- §11 Resources (facilities, test plan, schedule), p.11-1..11-6+ (leaves 1312-1319).
  **as-needed - not read (2026-10-18)** - cost/schedule.
- §12 Wind sensitivity study, p.12-1..12-14 (leaves 1320-1333). **as-needed - not read
  (2026-10-18)**.
- App. A Baseline SA-511 vehicle definition, p.A-1..A-119 (leaves 1334-1452). **as-needed -
  not read (2026-10-18)** - J-2 baseline vehicle data.

## Caveats

- **Spec values, not test data.** 427 s is a guaranteed minimum; 431 s is the 1968 nominal at
  MR 5.5. `[Vilja-J2S]` (1993) quotes 436 s at MR 5.5 and `[AEDC-J2S]` measured ~433-434 s at
  MR 4.6-5.1. On this document's own curve, ~434-435 s at MR 4.9-5.0 is nominal, so AEDC's
  test points sit roughly on or slightly above the 1968 nominal; 436 s at MR 5.5 is ~5 s above
  it (later development or a different basis; unresolved). RO uses 436 s.
- **No main-stage chamber pressure** is given anywhere in the parts read (only idle Pc 26 psia).
  Use `[Vilja-J2S]`'s 1,200 psi.
- **The document does not answer the tap-off-gas questions**: no tap-off temperature, pressure,
  flow fraction, dilution-H2 entry point or idle-mode tap-off condition (idle runs with the
  turbopumps stopped, so there is no idle tap-off flow). No tube counts, turbine materials,
  turbine efficiencies, turbine-exhaust disposal detail or pump discharge pressures either.
- **NPSH inconsistency.** §4's LH2 curve (164 → 176 ft) equals the S-II figure's **230K**
  line, while §4's LOX curve (31.9 → 42.3 ft) equals its **265K** line. The S-II text also says
  the J-2S NPSH requirement "was subsequently lowered to the existing J-2 requirement"
  `[p.10-105, leaf 421]`. Treat the §4 values as the later revision and the 197/216 ft LH2
  figures as superseded or 265K-specific; the source does not settle it.
- **Flow inconsistency (derived).** 450 + 88 = 538 lb/s at MR 5.0 against the ~237,500 lbf a
  265K engine gives at MR 5.0 (`[§5.1 p.5-1]`) implies ~441 s, above any Isp curve here. The MR
  5.0 flows probably belong to a different calibration or include tolerance; use the MR 5.5
  pair (525 / 95 lb/s).
- `[Vilja-J2S]` says "zero NPSP" for the J-2S. This spec gives non-zero main-stage NPSH; the
  zero-NPSP claim refers to the start (idle start on gas or two-phase propellant).
- The two-curve difference in Fig. 5.1-2 (S-II ~2 s below S-IVB) is not explained in the parts
  read (perhaps installation or pressurant offtake); not resolved.
- Restart-accessory "burnout 221 lb" below its 250 lb dry weight is as printed in Table 4.0-II
  (likely an expended SPTS cartridge).
- The GOX HX minimum outlet pressure digit is illegible ("4?0 psia"); figure-read values are
  +-5 % of full scale.
