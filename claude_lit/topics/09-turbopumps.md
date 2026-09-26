# 09 — Turbopumps

## Scope

Pump specific speed and suction performance (NPSH), tip-speed limits, turbine staging and
efficiency, the turbine-drive power balance, and real efficiency / specific-power / mass
data. Feeds `engine_designer/physics/turbopump.py`, `turbopump_tech.py`, and the turbine
constants in `design.py`.

## Key relations

**Pump power** `[Huzel §6.2]`, `[turbopump.py]`:

    P_pump = ṁ · Δp / (ρ · η_pump)          per pump; sum fuel + oxidizer

**Specific speed** `[SP-8107 eq. 1 p.12]`:

    Ns = N · Q^½ / H^¾          (rpm · gpm^½ / ft^¾)

**Pump headrise** `[SP-8107 eq. 16]`: `H = 144·[(Po)₂ − (Po)₁] / ρ₁` (psia → ft). For
high-pressure H2 pumps (> 2000 psi rise) use an incremental isentropic-enthalpy-rise
calculation (compressibility) — the headrise then lands roughly halfway between the
inlet-density and single-step values `[SP-8107 §2.1.1.1]`.

**Turbine specific work → GG bleed fraction** `[turbopump.py]`, consistent with
`[Sutton §10.1]`:

    Δh_turbine = Cp · T_in · η_turbine · (1 − PR^(−(γ−1)/γ))
    ṁ_gg       = P_turbine_required / Δh_turbine
    Isp_engine = (1 − x)·Isp_chamber + x·(dump_frac · Isp_chamber)      x = ṁ_gg / ṁ_total

**Turbopump mass** `[turbopump.py]`, `[SP-8107 Table I]`:

    m_turbopump = P_total / specific_power        specific_power from real hardware (below)

## Empirical correlations & typical values

**Real turbopump-assembly specific power** `[SP-8107 Table I, mid-1973]` — column is
"specific horsepower, hp/lbm"; **× 1644 ≈ W/kg**:

| Engine | hp/lbm | ≈ W/kg | Era / class |
|---|---|---|---|
| A-7 (Redstone) | 2.22 | 3 650 | earliest US, geared, monoprop start |
| MA-5 booster (Atlas) | 3.59 | 5 900 | — |
| MB-3 (Thor) | 5.40 | 8 900 | — |
| H-1 (Saturn IB) | 7.98 | 13 100 | mature GG |
| J-2 (Saturn upper) | 7.73 / **21.60** | 12 700 / **35 500** | dual turbopump (two rows: whole assy / one unit) |
| F-1 (Saturn IC) | **16.6** | **27 300** | Saturn V first stage |
| SSME (EPL) | 50.0 / **108.9** | 82 000 / **179 000** | high-pressure staged combustion |

**Real pump efficiencies** `[SP-8107 Table II]`: A-7 70–72 %; MB-3 72–79 %; H-1 72–78 %;
MA-5 sustainer ~64 %; MA-5 booster ~74 %; **F-1 O₂ 74.6 % / RP-1 72.6 %**; YLR87 (storable)
68 %; RL10 O₂ 63 % / H₂ 55 %; J-2 O₂ 80 % / H₂ 73 %; SSME O₂ 78 % / H₂ 74 %.
Small H2 pumps are the low end (~55 %); large LOX pumps the high end (~80 %).

**Real turbine data** `[SP-8107 Table III]` — see the table in `sources/nasa-sp8107-...md`.
Summary: GG-cycle turbine inlet temp 1200–1450 °F (922–1061 K), efficiency 46–70 % (most
55–66 %), PR 15.7–29; storable turbines hotter (~1650 °F); expander/staged-combustion
turbines PR 1.4–1.6, efficiency 73–79 %.

**Overall turbopump efficiency** (η_pump · η_turbine) `[SP-8107 §2.1.1.6]`: **35–48 %** for
GG-era engines, approaching **60 %** for SSME (needs high-Ns pumps + reaction turbines).

**Suction performance / NPSH** `[SP-8107 §2.1.1.2]`:
- Critical NPSH = where headrise is 2 % below the noncavitating value.
- Real NPSH_min (contractually specified, max acceptable) 12–132 ft; NPSH_crit (at 2 %
  drop) 11–75 ft `[Table II]`. LH2 pumps high (J-2 H₂ 130/75); LOX pumps low (F-1 O₂ 65/60).
- LH2 has excellent cavitation characteristics and low density → often no preinducer needed;
  can run at **zero NPSH at the tank** for some applications.
- LOX has good density but its cavitation characteristics need a preinducer to avoid high
  tank pressures.
- Fixes for insufficient NPSH: raise tank pressure (heavier tank), lower pump speed (lower
  efficiency, heavier turbopump), or redesign the inlet (bigger diameter, lower flow
  coefficient — used on the J-2 H₂ pump).

**Tip-speed limits (forged titanium, highest capability)** `[SP-8107 §3.2.1.3]`:
**2800 ft/s** unshrouded centrifugal, **2000 ft/s** shrouded centrifugal (1700–2300 by
design), **1500 ft/s** inducers & axial rotors. Only H2 pumps approach these. J-2 LH2 pump
impeller tip speed ~865 ft/s; LOX pump ~390 ft/s `[SP-8107 Table IV]`.

**Real impeller tip-speed by material/shrouding, a second concrete anchor**
`[SP-8109 §2.3.2 p.37]`: shrouded cast Inconel 718 or vacuum-melt/vacuum-cast aluminum
impellers in LH2 service are limited to **1400 fps**; a machined **open-face titanium
(Ti-5Al-2.5Sn) impeller ran to 2500 fps in LH2** (real hardware, not a spin-test only); a
shrouded diffusion-bonded titanium impeller was spin-tested to 2870 fps at room temperature
(spin-test only, not an operating limit). Open-face titanium buys **~80% more tip speed**
than a shrouded Inconel/aluminum impeller for the same LH2 service — a real
shrouding-configuration trade `turbopump_materials.py`'s rotor catalog doesn't currently
capture (it varies max-use-temperature and density, not shrouding-vs-tip-speed).

**Real suction-specific-speed design limits** `[SP-8109 §3.2.1.2 p.63]` — a direct,
quotable design criterion: **"For a pump with an integral inducer, maximum suction specific
speed of 40,000 for the inducer is recommended. Without an integral inducer, limit the Ss
value to 12,000."** Real fleet Ss data (corrected, roughly ×1000) sits well below that
ceiling: F-1 RP-1 pump ≈23,400; F-1 LOX ≈19,500; J-2 LOX ≈10,200; Atlas booster LOX
≈14,250; Atlas sustainer LOX ≈8,600 (no inducer, ≈15,000 for its RP-1 pump); X-8 LH2
≈11,000 — i.e. **40,000 is an upper design limit, not a typical achieved value**; real
hardware historically ran with much more suction margin than the limit allows. Also gives a
real **NPSH margin factor by propellant class**: NPSH ≥ 3.0·cm1²/2g (water/RP-1, low vapor
pressure), 2.3·cm1²/2g (LOX/LF2), 1.3·cm1²/2g (LH2) — no counterpart yet in
`turbopump_sizing.py`.

**Real critical-speed design criterion** `[SP-8109 §2.2.1.1/§3.2.1.1 p.8-10, 63]`: two real
design philosophies — operate below the first rigid-body whirl critical speed (needs stiff/
roller bearings, at the cost of "high bearing DN values"), or operate above the first/second
whirl critical speed but below shaft-bending resonance (needs preloaded/duplex ball bearings,
lower spring rates). Both keep a firm **~20% margin** between operating speed and the
nearest critical speed — "shall not operate continuously at a critical speed" is stated as
an explicit design criterion, not just a typical practice.

**Real bearing DN design ceiling** `[SP-8048 §3.1.2 p.31]` — the dedicated NASA bearings
monograph, read specifically because `turbopump_materials.py`'s `max_dn_mm_rpm` values were
flagged as an unsourced Tier-3 estimate: **one-piece cages required above 1.0×10⁶ DN;
angular-contact ball bearings recommended for 1.0–3.0×10⁶ DN; rolling-element bearings
should not be used above 3.0×10⁶ DN without prior testing.** Real achieved/tested DN data
(Table III): Conrad-type ball 1.6M DN (cage-weakness-limited, LH2); angular-contact ball
2.05M turbopump / 3.0M tested (heat-generation-limited, LH2); cylindrical roller 1.6M
(roller-guidance-limited, RP-1). Two real uprating-failure anecdotes reinforce the
one-piece-cage-above-1M-DN criterion: Atlas/Thor→H-1 bearings failed at ~10% higher
speed/load (fixed by split-inner-ring one-piece-bronze-cage bearings); J-2 fuel-pump
bearings at 1.6M DN suffered two-piece PTFE-cage failures (fixed by a one-piece cage of the
same otherwise-identical design). **Real coolant/lubricant ranking** (descending
bearing-lubricating ability): RP-1 > LOX > LH2 > N₂O₄ > IRFNA > EDA > UDMH > N₂H₄ >
50-50 N₂H₄-UDMH. **Real bearing material baseline**: AISI 440-C steel for races/rolling
elements — "none has been found with the combination of hardness, corrosion resistance,
fatigue life, and availability displayed by 440-C" — directly corroborating
`turbopump_materials.py`'s `440c_steel` entry; no ceramic (Si3N4-class) material appears
anywhere in this 1971 monograph, consistent with ceramic bearings being a later SSME-era
development (`[Ch12-Materials]` remains the source for that). Real clamping-load precedents:
J-2S 50,000 lbf tension-bolt bearing-race clamping load; F-1 800 ft-lb clamping-nut torque
(a real Atlas-sustainer gear/race fretting failure was fixed by raising nut torque to
200 ft-lb) — under-clamped rotating hardware is a recurring real turbopump failure mode.

**Second independent real bearing DN fleet anchor** `[STBE-PW leaf 40-41, 44]` — a 1989 P&W
booster-engine study's real GG-cycle turbopump hardware gives a second fleet data point
alongside `[SP-8048]`'s: oxidizer turbopump (DGGOT) ball bearing DN **0.88×10⁶**, roller
bearing DN **1.06×10⁶** (LOX-side); fuel turbopump (DGGFT) ball/roller DN **0.64×10⁶ /
0.78×10⁶** (fuel-side, lower than the LOX side) — consistent with `[SP-8048]`'s coolant/
lubricant ranking above (RP-1 > LOX > LH2 for bearing lubricity) and both well inside
`[SP-8048]`'s 1.0-3.0×10⁶ recommended band. Real rotordynamics data from the same source:
oxidizer-pump critical-speed margins run supercritical-with-large-margin (1st bending mode at
740% of design speed, >6× the report's own >20%-margin design goal), while the fuel pump is
run subcritical (fundamental bending pushed to 149% above design speed) — two different real
design philosophies for the same engine family, both satisfying the same 20%-margin
criterion from a different direction. Real turbopump rotor materials for this engine class:
oxidizer-side rotating thrust piston forged Inconel 718 vs. stationary Bearium B-10 (leaded
bronze) insert; fuel-side pump impeller Titanium, turbine disk/shaft Super A-286, turbine
blades/vanes MAR-M-247, housings Inco 718/MAR-M-247/Haynes 230 — a real late-1980s
turbopump material selection set, consistent in kind with (not cross-validated against)
`[Ch12-Materials]`'s broader survey below.

**Real expander-cycle turbopump performance data at two power levels** `[STBE-PW leaf 335,
337]` — a real, complete per-stage Ns/efficiency/head-coefficient dataset for a P&W "split
expander" cycle turbopump (see `topics/08-engine-cycles.md`), useful as an Ns-vs-efficiency
cross-check specifically for an *expander-class* pump (lower turbine PR/available power than
a GG or staged-combustion pump): CH4 turbopump, 2-stage centrifugal, turbine efficiency (T/T)
0.867 (NPL, normal power level) / 0.883 (DPL, design power level), pump-stage efficiencies
0.787/0.594 (stage 1/2) at NPL rising to 0.780/0.584 at DPL, speed 9,689/11,409 rpm, suction
specific speed 1,351/1,355 (stage 1), head coefficient 0.504-0.624, turbine pressure ratio
(T/T) 1.90 (NPL)/2.11 (DPL). O2 turbopump: single-stage centrifugal, turbine efficiency (T/T)
0.875/0.877, pump efficiency 0.795/0.796, speed 4,054/5,134 rpm, suction specific speed
1,384/1,396, turbine PR (T/T) 1.29/1.46 — consistent with the expander cycle's known lower
feed pressures/turbine PR (`[SP-8107]`'s "< 1.5" ceiling above) relative to GG/staged pumps.

**Ns and efficiency** `[SP-8107 §2.1.1.6]`: below Ns 2000–3000, raising speed raises pump
efficiency. Centrifugal-pump efficiency peaks at stage Ns 1300 (φ_it1 = 0.05) to 2500
(φ_it1 = 0.20). Axial-pump efficiency drops below Ns 2000, flat 2000–10 000.

**Turbine staging** `[SP-8107 §2.1.1.3–2.1.1.4]`: GG/tap-off → two-row velocity-compounded;
expander/staged combustion → two-stage pressure-compounded or reaction. Low-energy fuels
(LOX/RP-1, N₂O₄/A-50) → pressure-compounded; H₂ → velocity-compounded (exceptions: F-1 &
Redstone low pitchline; RL10 & SSME PR only 1.4–1.6). Turbine efficiency ≈ f(pitchline
velocity, i.e. U/C₀) for given inlet temp and PR; small low-hp turbines use partial
admission and gain efficiency with rotational speed.

**Pump/shaft arrangement** `[SP-8107 §2.1.2, KBKhA §V]`: similar-density propellants
(LOX/RP-1) → both pumps on one shaft at a common speed (F-1); widely-differing densities
(LOX/LH2) → separate shafts each at its optimum speed (J-2); or gear the LOX pump to the H2
turbopump shaft (RL10) to avoid a small inefficient LOX turbine. Geared turbopump for engine
thrust < 10 000 lbf.

**Cycle → turbopump stress** `[KBKhA]`: RD-0110 (GG) → RD-0124 (staged combustion), same
thrust: Pc ×2.3 demanded LOX pump discharge ×3.4, turbine flowrate ×15, rotor speed ×2.1.
Staged-combustion turbopumps need higher-strength materials (stainless vs aluminium
housings), castings + HIP, powder-metallurgy blisks, and **cannot be developed by standalone
component test** — component interaction dominates, especially in start/shutdown transients
(turbopump failures are historically 50–70 % of all engine development failures).

## Worked numbers

`[Huzel §6.2 / Sutton §10.1]` power balance (method): compute pump Δp from Pc + downstream
losses, → pump power from `ṁ·Δp/(ρ·η)`; split flow by MR; the turbine must deliver that
power within its available PR; `ṁ_gg = P/Δh_turbine`. `[SP-8107 Table IV]` J-2: LH2 inducer
headrise alone (5050 ft) exceeds the *entire* LOX pump headrise (2185 ft); LH2 pump overall
headrise ~38 000 ft, ~20× the LOX value, though the pressure *rises* are similar (~1075 vs
1208 psi) — density does everything.

**Real SSME turbopump stage-count architecture, not previously in this file (2026-09-24)**
`[SSME-Orientation p.52-71]`: LPOTP = 6-stage axial hydraulic turbine (LOX-driven, not gas);
LPFTP = 2-stage axial gas turbine (driven by MCC-jacket-exit GH2); HPOTP = double-entry
back-to-back main impeller + 3-stage cantilevered turbine; HPFTP = 3-stage centrifugal pump +
2-stage turbine. Real per-pump efficiency/PR table at 104.5% power (see `topics/08` for the
full figures) sits a few points off `[SP-8107]`'s 1973 pre-operational SSME row — a later,
real, named-hardware corroboration/refinement of that existing anchor. Real gimbal-bearing
duty-cycle data (also corroborating `[Sutton Table 16-2]`'s existing SSME entry in
`topics/16-gimbal-and-tvc.md`): ±12.5° gimbal capability, 200 operational cycles to 10.5° /
1,400 nonoperational, 6Al-6V-2Sn Ti with Fabroid inserts.

**Real F-1 turbine pressure-ratio anchor, not previously in this file (2026-09-24)** `[F1-Man
Fig 3-14 p.3-7]`: turbine inlet **945 psia total** / exit **58 psia static** → **PR ≈ 16.3**
(uprated F-1 engines); baseline (non-uprated) 918/58 → **PR ≈ 15.8**. Independent of `[H1-Man]`'s
H-1 PR≈17.7 anchor already cited elsewhere — a second real GG-cycle turbine-PR data point,
directly from Rocketdyne's own engine manual rather than a design-criteria monograph. No F-1
turbine efficiency percentage was found in the same source (unlike H-1's cited 69.6%) — an
open item if ever needed.

## Real component data & design criteria (SP-8052 / 8110 / 8121 / 8125 / 8101 batch, 2026-09-26)

**Turbines — fleet data, all total-to-static** `[SP-8110 Table I p.10]`:

| Engine | Type | hp | rpm | Dm in | U ft/s | Tt1 °F | PR | U/C0 | η |
|---|---|---|---|---|---|---|---|---|---|
| F-1 | 2-row VC | 54,359 | 5,490 | 34.9 | 840 | 1550 | 16.3 | 0.20 | 60.5 % |
| H-1 (geared) | 2-stage PC | 4,007 | 32,800 | 9.0 | 1290 | 1200 | 17.7 | 0.42 | 62.5 % |
| J-2 fuel | 2-row VC | 8,749 | 26,052 | 12.5 | 1448 | 1200 | 6.35 | 0.18 | 60.1 % |
| J-2 ox | 2-row VC | 2,604 | 8,650 | 15.5 | 585 | 740 | 3.16 | 0.11 | 48.4 % |
| Atlas sustainer | 2-stage PC | 1,680 | 38,000 | 6.0 | 995 | 1075 | 25 | 0.39 | 46.3 % |
| M-1 fuel | 2-row VC | 74,138 | 12,961 | 23.2 | 1310 | 1000 | 3.87 | 0.19 | 65.0 % |
| RL10 A3-3 | 2-stage PC | 660 | 28,670 | 5.9 | 738 | −88 | 1.42 | 0.35 | 74.0 % |

- **Staging is chosen by the ACHIEVABLE U/C0, not by propellant** `[SP-8110 §3.1.4 p.83]`:
  - reaction above ~0.45
  - single-row impulse / pressure-compounded at ~0.30–0.45
  - 2-row velocity-compounded at ~0.20–0.30
  - below ~0.15, one or two more rows are worth +10 / +23 points

  U is capped by stress (fleet pitchline 1000–1500 ft/s). On a DIRECT-DRIVE shaft U is also
  capped by the pump shaft speed × a practical wheel size. That is why the slow F-1 (5,490 rpm)
  lands at 0.20, while the H-1's turbine is geared to 32,800 rpm and reaches 0.42.
  `[SP-8101 p.3]`: the H-1 and RL10 turbopumps are geared.
- **Idealized η vs U/C0 peaks** `[SP-8110 Fig 13 p.17]`: 1-row ~80 % at 0.42, 2-row ~69 % at
  0.23, 3-row ~54 % at 0.13. Real hardware runs 5–10 points lower.
- **Loss correlation** `[SP-8110 Fig 55]`: the 2-row VC η multiplier vs blade-size ratio
  Dm/An (shrouded ≈ 1.076 − 0.0455·Dm/An). The monograph's worked example reproduces the J-2
  fuel turbine's 60.1 %.
- **Frozen turbine-gas properties** `[SP-8110 Table III p.16]`: LOX/RP-1 at 1300 / 1500 °F has
  cp 0.648 / 0.656 Btu/lb·°R (≈ 2,710 / 2,750 J/kg·K) and γ 1.115 / 1.132. LOX/LH2 at
  1200 °F has cp 1.91 Btu/lb·°R (≈ 8,000), γ 1.364.
- **Structural criteria** `[SP-8110 §3.5-3.6]`:
  - design speed 1.10× max
  - burst ≥ 120 %, yield ≥ 105 %
  - blades ±15 % off resonance; rotor ±20 % off criticals
- **H-1 turbine η disagreement.** [SP-8110] gives 62.5 % T-S. [SP-8107 Table III] gives
  70.2 % and [H1-Man Fig 1-47] 69.6 % for the same Mark 3 turbine. Unresolved; see
  OPEN_QUESTIONS.

**Inducers** `[SP-8052 Table I p.4]` (Ss measured in water at 10 % head drop):

| Inducer | Fluid | φ | β_tip | ν (hub/tip) | Ss |
|---|---|---|---|---|---|
| Thor Mk 3 | LOX | 0.116 | 14.2° | 0.31 | 28,500 |
| J-2 Mk 15 | LOX | 0.109 | 9.8° | 0.20 | 34,300 |
| X-8 Mk 19 | LOX | 0.106 | 9.8° | 0.23 | 31,200 |
| X-8 Mk 19 shrouded | LOX | 0.05 | 5.0° | 0.19 | 58,000 |
| J-2 Mk 15 | LH2 | 0.074–0.094 | 7.4–7.9° | 0.38–0.42 | 43,200–44,200 |

- **Brumfield sizing** `[SP-8052 §2.2]`: φ_opt = √(K/2(1+K)), and max S′s = 5055 /
  ((1+K)^¼·K^½). A K* of 0.006–0.01 caps Ss at about 50–65k. It reproduces 4 of the 6 Table I
  Ss values within 1–8 %.
- **NPSH:** NPSHr ≈ 3·c_m²/2g for an ideal fluid (the same Z ≈ 3 as SP-8109).
- **Thermodynamic suppression head (TSH)** is empirical per fluid and not predicted: F-1 LOX
  11 ft, J-2 LH2 250 ft.
- **Tip clearance** costs Ss a factor (1 − 0.5…0.65·√(c/L)).
- **Structural:** burst speed ≥ 1.2× and yield ≥ 1.05× design speed.

**Axial pumps** `[SP-8125 Table I p.4, Table II p.17]` (all LH2; only the J-2's flew):

| Pump | Flow | Head | Speed | Stages |
|---|---|---|---|---|
| **J-2 Mk 15-F** | 9,062 gpm | 40,300 ft | 28,266 rpm | inducer + 7 |
| M-1 | 62,300 gpm | 56,500 ft | 13,225 rpm | inducer + transition + 8 |

- The Mk 15-F runs a tip speed of ~890 ft/s, ~5,100–5,600 ft per stage and head coefficient
  ψ_T 0.23 (g·H/U², the tool's definition). That is well below the centrifugal 0.5.
- Stage hydraulic η is 0.84–0.92; overall pump peak is 0.70–0.79 `[SP-8125 Fig 1]`.
- **Axial vs centrifugal selection** `[§3.2.1 p.68]`: axial when stage Ns is above ~3,000 and
  no wide flow range or throttling is needed.
- **Stage-loading limits for LH2** `[§3.2.2]`:
  - φ ≥ 0.25, hub/tip ≤ 0.9
  - diffusion factor 0.45–0.55 for efficiency, 0.55–0.60 to minimise stages; stall at DF 0.75
  - tip clearance ≤ 2 % of blade height
- **Bearing DN:** 2×10⁶ is the LH2-cooled "state-of-the-art limit" for short-life pumps `[p.8]`.
- **H₂ embrittlement:** Ti-5Al-2.5Sn ELI forgings gave 1 % elongation at LH2 temperature
  until vacuum degassing raised it to 10 %. Criteria are ≥ 4 % elongation and ≥ 12 ft-lbf
  Charpy.

**Shafts and couplings** `[SP-8101]`:
- **Shaft size is set by STIFFNESS (critical speed) at the bearings, not by torsion.** "Shaft
  torsional shear stress rarely is a controlling factor" `[§3.1.1.3 p.62]`.
- **Journal sizing:** the journal is made as large as DN and seal-rubbing-speed limits allow,
  and journals are made SMALLER than the rest of the shaft to meet DN. The bearing bore equals
  the journal to within microns `[Table IV p.14]`.
- **Allowables:**
  - preliminary shear allowable at the bearings: 2/3 of ultimate shear `[§2.1.1.3 p.7]`
  - safety factors ≥ 1.1 yield / 1.3 ultimate / 1.25 fatigue `[§3.1.3.2 p.70]`
- **Critical-speed rule** `[§3.2.1.2.1 p.79]`:
  - lowest bending critical ≥ max(1.25 × normal speed, 1.15 × max overspeed)
  - rigid-body criticals below running speed ≤ 0.85 × the lowest steady speed
  - predictions are good to ±5 % at best
- **Material:** no 4340 at cryogenic temperature `[p.68]`, although Table II rates it
  satisfactory in oxygen.

**Rotating-shaft seals** `[SP-8121]`:
- **Selection by condition** `[§3.2.1 p.106]`:
  - welded-bellows face-contact seals for cryogenic or reactive liquids to ~500 psig;
    piston-ring face seals above that
  - elastomer face seals for RP-1 / oil to ~1000 psig
  - segmented carbon for purged or hot-gas seals below 100 psig; floating ring above
  - clearance or fluid-film seals above ~500 ft/s rubbing speed or beyond 4 h life
- **Real seals** `[Table I p.4-6]`:
  - F-1 LOX face seal: 6.46 in, 6,000 rpm, 25 SCFM
  - J-2 LH2: 2.95 in, 28,000 rpm, 360 ft/s, 0.01 lb/s
  - J-2 turbine: segmented carbon at 460 ft/s, 20 SCFM
- **Inter-propellant layout:**
  - two primary face seals plus separate drains, with a purged intermediate seal between them
  - the purge must exceed the maximum drain back-pressure and come from a supply that cannot
    fail
  - F-1 and H-1 use a GN2 purge; hydrogen systems use helium only
  - **No purge flow rates are given** (gap: OPEN_QUESTIONS)
- **Leakage magnitudes:** primary-seal leakage is ~1e-5–1e-4 of pump flow, negligible. The
  real efficiency loss is the pressure-breakdown recirculation bleed.
- **Relative leakage:** a labyrinth leaks ~5× a floating ring; a stepped labyrinth ~½ a
  straight one.

## Caveats

- Specific-power figures are for the turbopump *assembly* as flown; "turbopump" (Table II)
  vs "assembly" (Table I) masses differ, so a W/kg derived from Table I can differ from one
  the tool derives from a component mass.
- SSME rows in `[SP-8107]` are pre-operational projections (mid-1973).
- `Ns` and tip-speed limits are US-customary and geometry-specific; they bound a design,
  they don't predict one.
- `[SP-8109]`'s real fleet Ss data (8,600–23,400) sits well below its own 40,000 recommended
  ceiling — don't calibrate a future Nss validate.py check against 40,000 as if it were a
  typical achieved value; use it as an upper bound and the fleet data as typical-case anchors.
- `[SP-8048]`'s 3.0×10⁶ DN ceiling is a blanket rolling-element limit, not broken out by
  bearing material — it validates the tool's overall order-of-magnitude but not its
  material-by-material gradation (440C vs Cronidur 30 vs Si3N4). Only ~15 of 84 pages of
  this image-scanned (no text layer) monograph were read; a shaft/bore sizing formula, if one
  exists, wasn't found in the sections read.

## Implications for engine_designer

- **`turbopump_tech.py` specific power** (ASSUMPTIONS.md items relating to turbopump mass):
  - `mature = 36000 W/kg` — the tool sources this from the F-1. `[SP-8107 Table I]` gives
    F-1 = 16.6 hp/lbm ≈ **27 300 W/kg** (turbopump *assembly*, 3150 lbm). The 36 000 figure
    is closer to the J-2 single-unit value (21.6 hp/lbm ≈ 35 500 W/kg). Both are defensible
    "mature GG-era" numbers; note the ~25 % spread depending on which engine/definition.
  - `advanced = 70000 W/kg` — flagged as **NOT independently sourced** (ASSUMPTIONS.md
    item #41). `[SP-8107 Table I]` **directly supports it**: SSME (EPL) high-pressure staged
    combustion = 50.0–108.9 hp/lbm ≈ **82 000–179 000 W/kg**. 70 000 W/kg is *conservative*
    for SSME-class. ASSUMPTIONS.md item #41 can be upgraded from "round 2× F-1 extrapolation,
    treat with skepticism" to "bracketed below the SSME turbopump-assembly figure
    (82–179 kW/kg, SP-8107 Table I)."
  - `early_simple = 1300 W/kg` (from V-2, upper bound) — `[SP-8107 Table I]` A-7 (Redstone,
    the earliest US turbopump) = 2.22 hp/lbm ≈ **3 650 W/kg**. The V-2 predates the
    Redstone, so 1300 < 3650 is consistent; the tool's value is the low anchor.
- **Pump & turbine efficiency are now DERIVED** (`physics/turbopump_efficiency.py`), not
  picked from a tier. Pump η = `ETA_PUMP_PEAK(0.78) · ns_bell(whole-pump Ns) · size_penalty`
  — a bell peaking at Ns ~2200 per `[SP-8107 2.1.1.6]`, so a multistage LH2 pump (low
  whole-pump Ns) lands below peak. Turbine η = `ceiling(staging) · pitchline · admission(power)
  · PR` with ceilings 2-row-VC 0.63 / 2-stage-PC 0.76 / reaction 0.80 from the `[SP-8107
  Table III]` per-type maxima. Both curves are calibrated to Table II/III (F-1 72.6/74.6 %,
  60.5 %; J-2 73/80 %, 60 %; H-1 turbine 70 %; RL10 74 %; SSME 74-79 %; A-7 37 %; YLR81
  41 %) and pinned by `validate.py::run_turbopump_efficiency_check()`. The early/mature/
  advanced tier is now only a `build_quality_factor` multiplier (×0.93/1.00/1.04);
  `mature` = 1.00. `GG_ETA_TURBINE = 0.62` is the fallback/seed only.
- **`design.py` GG constants** — `GG_TIN_K = 1050` = RD-0110 exactly `[KBKhA]`;
  `GG_PRESSURE_RATIO = 22` ≈ the "~20" guidance; the actual turbine PR for staged/expander
  is `STAGED_COMBUSTION_TURBINE_PR = 1.5` / `EXPANDER_TURBINE_PR = 1.4` (efficiency only).
- **`gg_flow_fraction` red-flag threshold `GG_FLOW_FRACTION_TYPICAL_MAX = 0.07`**
  (ASSUMPTIONS.md item #42): `[SP-8107 Table VI]` GG Isp loss is "⅓ to 1 % at 1000-psia Pc";
  a 7 % bleed fraction with a dump-Isp fraction of ~0.55 gives roughly a 3 % Isp loss, which
  is on the high side — so 0.07 as a *warning* threshold (not a hard limit) is reasonable.
- **`turbopump_sizing.py` (added)**: a 1-D preliminary sizing pass now DOES derive rotor
  speed, impeller tip speed, pump stage count, turbine pitchline (`U/C0` by staging), and
  the shaft arrangement / turbine count, using this file's relations: `Ns = N·Q^½/H^¾` with
  a target in the 1300-2500 efficient band; `psi = g·H_stage/U_tip²` with `psi ≈ 0.5-0.6`;
  the 2800/2000/1500 ft/s tip-speed limits (now per-material via `turbopump_materials.py`,
  forged Ti = the 853 m/s anchor); the "geared below ~10,000 lbf" rule (raised to ~15,000
  lbf so the RL10 class is caught); and the similar-vs-differing-density → single-vs-dual
  shaft rule (F-1 vs J-2). Anchored so the J-2 LH2 pump comes out ~7 stages. Spot-checked
  in `physics/validate.py::run_turbopump_sizing_check()` against real J-2 / F-1 / RD-0110
  rotor & tip speeds with wide (factor ~2-3) bands.
- **NPSH / cavitation / suction specific speed**: still NOT modelled - so the 1-D sizing
  above over-predicts rotor speed for extreme high-head pumps a real designer slows with
  extra axial stages for cavitation margin. `[SP-8107 §2.1.1.2, §2.2.1]` has the framework
  if a real NPSH model is ever added. **Update**: `[SP-8109 §3.2.1.2]` now gives this a real
  citation — the pending NPSH/suction-specific-speed feature plan's `NSS_TARGET_US
  ["lox_class"] = 40_000.0` seed value matches this monograph's integral-inducer
  recommendation exactly (though `[SP-8109]` frames 40,000 as a general inducer-equipped
  limit, not LOX-specific, and gives no separate LH2-class number — the plan's `lh2_class:
  58_000.0` still rests on the F-1/J-2 two-anchor derivation, not this source). The
  3.0/2.3/1.3 NPSH-margin-factor-by-propellant-class numbers above are new and have no
  counterpart in `turbopump_sizing.py` yet.
- **Bearing DN Tier-3 estimate now has a real citation**: `[SP-8048 §3.1.2]`'s 1.0×10⁶/
  3.0×10⁶ DN bands are noticeably **more permissive** than `turbopump_materials.py`'s current
  flagged-estimate `max_dn_mm_rpm` values (~1.2M–2.4M) — either the tool's numbers are
  conservative relative to this real 1971 NASA design criterion, or the tool's per-material
  gradation is a reasonable finer scheme *within* this document's single blanket ceiling.
  Either way, `ASSUMPTIONS.md`'s Tier-3 DN-limit entry can now point to a real source instead
  of "general aerospace rolling-element-bearing knowledge" — report-only here, no code
  changed this pass. `[STBE-PW]`'s real fleet DN data (0.64-1.06×10⁶ across a late-1980s
  GG-cycle engine's LOX/fuel bearings) is a second independent real-hardware anchor, sitting
  comfortably inside `[SP-8048]`'s band and reinforcing the RP-1>LOX>LH2 lubricity ranking.
- **Turbopump mass** now follows the `[SP-8107 Table I]` "specific horsepower" trend
  directly (`turbopump_sizing.turbopump_mass_kg`: ~12 kW/kg small → ~27 kW/kg large,
  log-interpolated; F-1 1429 kg / J-2 ~305 kg / RD-0110 ~90 kg spot-checked). A physical
  envelope (`bodies`) is also built for the 3D preview but scaled to that mass - a raw
  d²·L volumetric mass runs several × heavy because the tool's rotor speeds (no NPSH
  model) inflate the diameters.
- **ORSC reliability caveat**: `[KBKhA]` confirms oxidizer-rich turbines require special
  oxidation-tolerant design (vaneless gas distributor, coatings) and were a Soviet/Russian
  achievement — the tool's standing ORSC warning is literature-backed. `[NK-33-Mod]` adds a
  real construction-level confirmation, not new numbers: NK-33 turbopump housings are
  aluminum castings/forgings, high-speed inducers/impellers investment-cast chrome-nickel
  steel (fuel inducer titanium), turbine housing an Inconel equivalent — no numeric
  Ns/pump-efficiency data given, so this source can't feed `turbopump_efficiency.py` or
  `turbopump_sizing.py` directly the way `[SP-8107]` does.
- **Turbopump materials by engine generation**: `[Ch12-Materials]` (topic 12) has a real
  alloy-per-engine-generation table (Rene 41/alloy 718/single-crystal PW1480 turbine
  hardware; Monel K-500/Tens-50 Al pump hardware; Cronidur 30 → Si3N4-ceramic bearing
  progression) — a candidate reference if `turbopump_materials.py`'s catalog is ever
  extended with named historical entries; see topic 12's implications for detail.
- **`turbopump_sizing.py`/`turbopump_efficiency.py` now have a real SSME stage-count
  reference architecture** (`[SSME-Orientation]`, above) — real per-turbopump stage counts
  (6/2/3+3/3+2 across LPOTP/LPFTP/HPOTP/HPFTP) at a real high-Pc staged-combustion design
  point, a useful plausibility check if the tool's own stage-count logic is ever validated
  against a named real engine beyond the existing `[SP-8107]` table. Report-only.
- **Turbopump Round 0 (2026-09-26) - what the SP-8052/8110/8125/8121/8101 batch changed or
  flagged in `engine_designer`:**
  - **Turbine staging.** Open-cycle staging is now derived from the achievable U/C0
    `[SP-8110 §3.1.4]` (`turbopump_sizing.open_cycle_turbine_staging`): a stress cap
    `TURBINE_PITCHLINE_CAP_M_S` = 1,500 ft/s, plus a direct-drive wheel-diameter cap
    `TURBINE_DMEAN_OVER_PUMP_D` (Tier 3, F-1-fitted). The old cycle/propellant rule
    mis-staged the F-1 as pressure-compounded.
  - **LOX/RP-1 GG gas cp.** Changed 2100 → 2735 J/kg·K from `[SP-8110 Table III]`. The old
    value under-stated the F-1's isentropic drop by ~23 %.
  - **NSS targets.** `lox_class` 40,411 sits at the top of the LOX water-test band
    (28.5–34.3k; SP-8052 treats > 40k as the special high-performance case). `lh2_class`
    58,027 is really a water Ss of ~44k plus the J-2's 250 ft thermodynamic suppression head.
    The Round 1 inducer model should use water Ss + TSH credit `[SP-8052]` instead of one
    effective number.
  - **`H_PER_STAGE_FT_TYPICAL` = 6000 ft.** It reproduces the J-2 stage count by matching an
    AXIAL machine (ψ_T 0.23, ~5,100–5,600 ft/stage `[SP-8125]`), not a centrifugal one at
    ψ 0.5. That coincidence belongs wherever the anchor is cited.
  - **Shaft constants.** `SHAFT_ALLOWABLE_SHEAR_PA` (200 MPa) now has a cited structure: 2/3 of
    ultimate shear `[SP-8101]`, which still needs an alloy value.
    `BEARING_BORE_OVER_SHAFT_FACTOR` 1.15 is contradicted: the bore equals the journal, and
    the journal is sized DOWN to the DN limit `[SP-8101 Table IV]`. Torsion sizing is a lower
    bound only. Round 4 should size the journal at the DN limit and check critical speeds
    with the `[SP-8101]` margin rule.
  - **Bearing DN.** The `max_dn_mm_rpm` flag gains a third real cite: LH2-cooled 2×10⁶ state
    of the art `[SP-8125 p.8]`.
