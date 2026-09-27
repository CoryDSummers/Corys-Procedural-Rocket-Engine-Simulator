"""
Turbopump structural-material catalog - the rotating/pressure-containing
hardware of the turbopump (impellers, inducers, turbine disk/blades, housings),
NOT the thrust-chamber wall (that is physics/materials.py).

Same epistemic status and idiom as physics/materials.py / turbopump_tech.py /
controller_tech.py: a frozen dataclass + a module dict + an accessor + one
warn-not-block suitability helper. No real RO config exposes a turbopump
material field, so there is nothing to calibrate against - this is an
engineering-judgment catalog.

`max_tip_speed_m_s` is the one number with a real anchor: [SP-8107 3.2.1.3]
gives, for the best-capability forged-titanium rotor, 2800 ft/s (853 m/s)
unshrouded centrifugal / 2000 ft/s (610 m/s) shrouded / 1500 ft/s (457 m/s)
inducers and axial rotors. `titanium_forged` here is set to that 853 m/s
anchor (Tier 2); every other alloy's tip-speed capability is scaled from it by
rough specific-strength and is a Tier 3 estimate. Everything else in the table
(service temps, strength class, oxidizer compatibility, cost) is a documented
engineering estimate - see ASSUMPTIONS.md.

`relative_cost_factor` is tracked and displayed only, never folded into a cost
model - same as physics/materials.py's field of the same name.

Also carries `BEARING_MATERIALS` - a separate, parallel catalog for the
turbopump's ROLLING-ELEMENT BEARINGS (a different duty than the rotor/blade
table above: rotating-contact DN limit, not blade tip speed or hot-gas service
temp). Its `max_dn_mm_rpm` field is a flagged Tier-3 estimate NOT sourced from
claude_lit or any read literature - see ASSUMPTIONS.md and `bearing_suitability`'s
docstring.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class TurbopumpMaterial:
    key: str
    display_name: str
    density_kg_m3: float
    max_use_temp_k: float          # hot-end (turbine disk/blade) service limit
    max_tip_speed_m_s: float       # impeller / blade tip-speed capability
    strength_class: str            # "low" | "medium" | "high" | "very_high"
    oxidizer_compatible: bool      # safe wetted by an oxidizer-rich / LOX stream
    relative_cost_factor: float    # display only (like materials.py)
    color_hex: str                 # 3D-preview tone only - real-world-plausible metal
                                    # colour, not measured (same status as materials.color_hex)
    specular_strength: float       # 3D-preview Blinn-Phong highlight strength (0..1) -
                                    # cosmetic/rendering only, same tier as color_hex
    shininess: float                # 3D-preview Blinn-Phong exponent - cosmetic/rendering
                                    # only, same tier as color_hex
    tech_era_hint: str
    notes: str
    metallic: float = None          # 3D-preview PBR metalness/roughness - cosmetic only,
    roughness: float = None         # same meaning/None rule as materials.Material's


MATERIALS = {
    "aluminum_7075": TurbopumpMaterial(
        key="aluminum_7075",
        display_name="7075-T6 Aluminium",
        density_kg_m3=2810.0,
        max_use_temp_k=420.0,
        max_tip_speed_m_s=350.0,
        strength_class="low",
        oxidizer_compatible=False,
        relative_cost_factor=0.6,
        color_hex="#C7CCD0",
        specular_strength=0.55,
        shininess=70.0,
        metallic=1.0,
        roughness=0.35,
        tech_era_hint="Early (V-2 / early ICBM cast-aluminium pumps)",
        notes="Light and cheap; real early turbopumps (A-4, early Atlas) used "
              "cast/forged aluminium impellers and housings. Strength falls off "
              "fast with temperature and it cannot approach modern tip speeds - "
              "a hard ceiling on chamber pressure for an aluminium pump. Not for "
              "an oxidiser-wetted rotor (LOX impact sensitivity). Tip-speed "
              "figure is a Tier 3 estimate scaled from the SP-8107 titanium anchor.",
    ),
    "stainless_17_4ph": TurbopumpMaterial(
        key="stainless_17_4ph",
        display_name="17-4PH Stainless Steel",
        density_kg_m3=7800.0,
        max_use_temp_k=700.0,
        max_tip_speed_m_s=520.0,
        strength_class="medium",
        oxidizer_compatible=True,
        relative_cost_factor=0.8,
        color_hex="#9DA1A6",
        specular_strength=0.6,
        shininess=80.0,
        metallic=1.0,
        roughness=0.38,
        tech_era_hint="Mature (precipitation-hardening stainless, general pump use)",
        notes="A workhorse pump-side material: corrosion-resistant, weldable, "
              "oxidiser-compatible, moderate strength. Heavier than aluminium or "
              "titanium so its practical tip speed is limited by disk stress. "
              "Tip-speed and temperature figures are Tier 3 estimates.",
    ),
    "inconel_718": TurbopumpMaterial(
        key="inconel_718",
        display_name="Inconel 718 (nickel superalloy)",
        density_kg_m3=8190.0,
        max_use_temp_k=980.0,
        max_tip_speed_m_s=620.0,
        strength_class="high",
        oxidizer_compatible=True,
        relative_cost_factor=1.0,
        color_hex="#8E8C84",
        specular_strength=0.4,
        shininess=45.0,
        metallic=1.0,
        roughness=0.42,
        tech_era_hint="Mature (hot turbine end, GG / staged-combustion)",
        notes="The default turbine-end alloy: high strength retained to ~980 K, "
              "used for GG and staged-combustion turbine disks and hot housings. "
              "Dense, so tip speed is disk-stress limited rather than the "
              "titanium tip-speed anchor. Widely run oxidiser-side. Service "
              "temp and tip-speed figures are Tier 3 estimates.",
    ),
    "titanium_forged": TurbopumpMaterial(
        key="titanium_forged",
        display_name="Forged Titanium (6Al-4V-class)",
        density_kg_m3=4430.0,
        max_use_temp_k=590.0,
        max_tip_speed_m_s=853.0,
        strength_class="high",
        oxidizer_compatible=False,
        relative_cost_factor=1.6,
        color_hex="#6E7076",
        specular_strength=0.5,
        shininess=60.0,
        metallic=1.0,
        roughness=0.4,
        tech_era_hint="Mature (LH2 pump impellers / inducers)",
        notes="Best strength-to-weight of the table -> the highest tip speed, "
              "which is exactly why real high-head LH2 pump impellers (J-2, "
              "SSME HPFTP) are forged titanium. 853 m/s = 2800 ft/s is the "
              "SP-8107 3.2.1.3 forged-titanium unshrouded-centrifugal anchor "
              "(Tier 2). MUST NOT be wetted by LOX or an oxidiser-rich stream: "
              "titanium ignites on impact/rub in oxygen - a severe, well-"
              "documented hazard, hence oxidizer_compatible=False.",
    ),
    "powder_met_superalloy": TurbopumpMaterial(
        key="powder_met_superalloy",
        display_name="Powder-Metallurgy / HIP Superalloy (high-strength disks & housings)",
        density_kg_m3=8250.0,
        max_use_temp_k=1150.0,
        max_tip_speed_m_s=700.0,
        strength_class="very_high",
        oxidizer_compatible=True,
        relative_cost_factor=2.4,
        color_hex="#7C7A73",
        specular_strength=0.35,
        shininess=40.0,
        metallic=1.0,
        roughness=0.45,
        tech_era_hint="Modern (HIP / powder-metallurgy blisks, staged combustion)",
        notes="Hot-isostatic-pressed powder-metallurgy superalloy disks, blisks "
              "and housings are what real staged-combustion turbopumps (KBKhA "
              "RD-0124-class, SSME) use to survive the pump discharge pressures "
              "(>2x Pc) those cycles impose - [KBKhA] notes staged combustion "
              "cannot use the lower-strength cast/forged housings a GG cycle gets "
              "away with. It is a STRENGTH choice first: hot turbine BLADES are "
              "cast alloys (713C, IN100, directionally-solidified MAR-M-246 - see "
              "BLADE_MATERIALS; MAR-M alloys are cast, not powder). A GG turbine "
              "near 1,100 K ran on wrought Inconel 718 / Rene 41 disks with cast "
              "713C blades (F-1, [SP-8110 p.3, Table II]). Highest cost. Figures "
              "are Tier 3 estimates.",
    ),
    "rene_41": TurbopumpMaterial(
        key="rene_41",
        display_name="Rene 41 (wrought Ni-Co superalloy)",
        density_kg_m3=8250.0,
        max_use_temp_k=1090.0,
        max_tip_speed_m_s=620.0,
        strength_class="high",
        oxidizer_compatible=True,
        relative_cost_factor=1.5,
        color_hex="#86847C",
        specular_strength=0.4,
        shininess=45.0,
        metallic=1.0,
        roughness=0.44,
        tech_era_hint="Mature (F-1 turbine disks, nozzles and manifolds)",
        notes="The F-1 turbine's disk / nozzle / manifold alloy alongside Inconel 718 "
              "([SP-8110 p.3, Table II]; SP-8110 also lists it for disks, nozzles and "
              "manifolds and warns its welds need Hastelloy W filler). Hotter-capable "
              "than 718 for the disk and hot casings. max_use_temp_k 1,090 K "
              "(~1,500 F) and tip speed (= 718's) are Tier 3 estimates - no Rene 41 "
              "strength-vs-temperature data in claude_lit.",
    ),
    "monel_k500": TurbopumpMaterial(
        key="monel_k500",
        display_name="Monel K-500 (Ni-Cu)",
        density_kg_m3=8440.0,
        max_use_temp_k=810.0,
        max_tip_speed_m_s=500.0,
        strength_class="medium",
        oxidizer_compatible=True,
        relative_cost_factor=1.3,
        color_hex="#A8A29A",
        specular_strength=0.45,
        shininess=55.0,
        metallic=1.0,
        roughness=0.4,
        tech_era_hint="Mature (oxidiser-rich / LOX-side rotating hardware)",
        notes="Nickel-copper alloy prized for oxygen compatibility: resists "
              "ignition in high-pressure oxygen far better than steel or "
              "titanium, so it (and coated variants) is the class of material "
              "real oxidiser-rich staged-combustion turbines and LOX pump "
              "hot sections use ([KBKhA]: ORSC turbines need special "
              "oxidation-tolerant design). Modest strength -> modest tip speed. "
              "Figures are Tier 3 estimates.",
    ),
}

@dataclass(frozen=True)
class BearingMaterial:
    key: str
    display_name: str
    density_kg_m3: float
    max_dn_mm_rpm: float           # DN limit: bore diameter (mm) x shaft speed (rpm) -
                                    # THE FLAGGED-ESTIMATE FIELD, see notes below
    max_use_temp_k: float          # bearing's own local service temperature (near the
                                    # pumped-fluid inlet temp, NOT the hot turbine-gas temp)
    oxidizer_compatible: bool      # reliability/fatigue framing in LOX service, NOT an
                                    # ignition-hazard framing like the rotor MATERIALS table
    relative_cost_factor: float    # display only, like MATERIALS
    color_hex: str                 # 3D-preview tone only, not measured
    tech_era_hint: str
    notes: str


BEARING_MATERIALS = {
    "440c_steel": BearingMaterial(
        key="440c_steel",
        display_name="440C Stainless Steel",
        density_kg_m3=7650.0,
        max_dn_mm_rpm=1_200_000.0,
        max_use_temp_k=600.0,
        oxidizer_compatible=False,
        relative_cost_factor=0.7,
        color_hex="#9A9EA3",
        tech_era_hint="Mature (early-to-1990s turbopump bearings)",
        notes="440C/52100-class martensitic stainless was the historical rolling-element "
              "choice on essentially every turbopump through the original SSME HPFTP/HPOTP "
              "[Ch12-Materials p.45]. Bearing wear/fatigue life in cryogenic, poorly-"
              "lubricated (process-fluid-lubricated) service was a real recurring "
              "reliability driver - the reason later programs moved on (below).",
    ),
    "cronidur_30": BearingMaterial(
        key="cronidur_30",
        display_name="Cronidur 30 (15Cr-N stainless)",
        density_kg_m3=7700.0,
        max_dn_mm_rpm=1_500_000.0,
        max_use_temp_k=620.0,
        oxidizer_compatible=False,
        relative_cost_factor=1.1,
        color_hex="#8F949A",
        tech_era_hint="Modern (SSME / RS-68 bearing upgrade)",
        notes="Nitrogen-alloyed stainless adopted for SSME and RS-68 bearings "
              "[Ch12-Materials p.45] - better corrosion/fatigue resistance than 440C at a "
              "similar DN capability; still a rolling-contact steel, not a hard "
              "ceiling-buster.",
    ),
    "si3n4_ceramic": BearingMaterial(
        key="si3n4_ceramic",
        display_name="Silicon Nitride (Si3N4) ceramic",
        density_kg_m3=3200.0,
        max_dn_mm_rpm=2_400_000.0,
        max_use_temp_k=900.0,
        oxidizer_compatible=True,
        relative_cost_factor=2.0,
        color_hex="#3D3F42",
        tech_era_hint="Modern (SSME alternate HPOTP / Block II)",
        notes="Ceramic rolling elements adopted for the SSME alternate HPOTP/Block II "
              "HPFTP specifically to fix bearing wear/fatigue [Ch12-Materials p.45: "
              "'virtually eliminating bearing wear and fatigue concerns'] - notably on the "
              "OXIDIZER turbopump, i.e. real flight heritage running ceramic in LOX "
              "service. Lower density and higher hardness raise the achievable DN "
              "substantially.",
    ),
}


def available_bearing_materials():
    return list(BEARING_MATERIALS.keys())


def bearing_suitability(mat_key, *, dn_mm_rpm, use_temp_k):
    """
    Warn-not-block: bearing DN over the material's limit, or the bearing's own
    local environment temperature over its service limit. NOTE: `max_dn_mm_rpm`
    is a flagged Tier-3 estimate (general aerospace rolling-element-bearing
    knowledge, NOT sourced from claude_lit or any read literature) - see
    ASSUMPTIONS.md. Trust the ORDERING (440C < Cronidur 30 < Si3N4) far more
    than the absolute numbers.
    """
    mat = BEARING_MATERIALS[mat_key]
    out = []
    if dn_mm_rpm > mat.max_dn_mm_rpm:
        out.append(
            f"{mat.display_name}: bearing DN {dn_mm_rpm:,.0f} mm*rpm exceeds this "
            f"material's ~{mat.max_dn_mm_rpm:,.0f} limit (engineering-estimate threshold, "
            f"not independently sourced) - real turbopumps this fast either use a lower-DN "
            f"bearing arrangement or a higher-DN material.")
    if use_temp_k > mat.max_use_temp_k:
        out.append(
            f"{mat.display_name}: bearing environment ~{use_temp_k:.0f} K exceeds its "
            f"~{mat.max_use_temp_k:.0f} K service limit.")
    return out


# --- turbine BLADE materials (tap-off accuracy round, 2026-09-26) ---------------------
# The rotor MATERIALS table above is the disk / housing / impeller alloy. Real turbines
# split it: the F-1's turbine (1,550 F = ~1,116 K inlet total) ran Inconel 718 / Rene 41
# disks with CAST Alloy 713C blades [SP-8110 p.3, Table II], and SP-8110 lists blades of
# cast 713C / IN100 / Udimet 700 vs disks of 16-25-6 / X-750 / Rene 41 / 718.
#
# Blade limits are DERIVED from [SP-8110 Fig. 30]: the allowable blade loading AaN^2
# (annulus area x speed^2, x1e9 in^2 rpm^2, blade+shroud/solid weight ratio 0.85) vs
# temperature. An alloy's limit is the temperature at which its allowable falls to the level
# the F-1's 713C blades demonstrably ran at. That level is 713C's allowable at the F-1's
# blade metal temperature, taking the inlet gas / the gas-to-metal margin the suitability
# check already uses. So 713C sits exactly at the F-1 point, and the others follow from
# their own curves (linear in F). An alloy still above that level at Fig. 30's top point
# (1,500 F) is capped there - the data go no further. Round 3's blade-stress check will
# compare the turbine's real AaN^2 against these same rows.
FIG30_TEMPS_F = (100.0, 600.0, 1000.0, 1200.0, 1500.0)
FIG30_AAN2 = {
    "inconel_718": (35.0, 33.0, 31.0, 27.0, 5.0),
    "udimet_700": (51.0, 35.0, 31.0, 28.0, 16.0),
    "in100": (45.0, 38.0, 35.0, 29.0, 22.0),
    "alloy_713c": (26.0, 24.0, 24.0, 21.0, 12.0),
}
TURBINE_GAS_TO_METAL_MARGIN = 1.08     # the suitability check's gas-vs-metal allowance
F1_TURBINE_INLET_K = (1550.0 + 459.67) / 1.8   # [SP-8110] F-1 inlet total 1,550 F
F1_BLADE_METAL_K = F1_TURBINE_INLET_K / TURBINE_GAS_TO_METAL_MARGIN
# Disk metal temperature / turbine-inlet gas temperature (Tier 3, one anchor): set so the
# F-1's real Inconel 718 disks (rotor limit 980 K) at its 1,116 K inlet just pass.
DISK_METAL_TEMP_FRACTION = 980.0 / F1_TURBINE_INLET_K


def _f(t_k):
    return t_k * 1.8 - 459.67


def _k(t_f):
    return (t_f + 459.67) / 1.8


def fig30_allowable(key, t_k):
    """SP-8110 Fig. 30 allowable AaN^2 [x1e9 in^2 rpm^2] of a blade alloy at t_k (linear
    in F; held flat outside 100-1500 F)."""
    ys = FIG30_AAN2[key]
    tf = min(max(_f(t_k), FIG30_TEMPS_F[0]), FIG30_TEMPS_F[-1])
    for i in range(len(FIG30_TEMPS_F) - 1):
        t0, t1 = FIG30_TEMPS_F[i], FIG30_TEMPS_F[i + 1]
        if tf <= t1:
            return ys[i] + (ys[i + 1] - ys[i]) * (tf - t0) / (t1 - t0)
    return ys[-1]


F1_DEMONSTRATED_AAN2 = fig30_allowable("alloy_713c", F1_BLADE_METAL_K)


def fig30_temperature_limit_k(key):
    """Temperature at which the alloy's Fig. 30 allowable falls to F1_DEMONSTRATED_AAN2
    (capped at Fig. 30's 1,500 F top point)."""
    ys, a = FIG30_AAN2[key], F1_DEMONSTRATED_AAN2
    for i in range(len(FIG30_TEMPS_F) - 1):
        if ys[i] >= a >= ys[i + 1] and ys[i] > ys[i + 1]:
            t0, t1 = FIG30_TEMPS_F[i], FIG30_TEMPS_F[i + 1]
            return _k(t0 + (t1 - t0) * (ys[i] - a) / (ys[i] - ys[i + 1]))
    return _k(FIG30_TEMPS_F[-1])


@dataclass(frozen=True)
class BladeMaterial:
    key: str
    display_name: str
    max_use_temp_k: float          # blade metal service limit (derived, or Tier 3 - see notes)
    cast: bool
    oxidizer_compatible: bool      # same ignition-hazard framing as the rotor MATERIALS table
    source: str
    notes: str


BLADE_MATERIALS = {
    "inconel_718": BladeMaterial(
        key="inconel_718", display_name="Inconel 718 (wrought) blades",
        max_use_temp_k=fig30_temperature_limit_k("inconel_718"), cast=False,
        oxidizer_compatible=True, source="[SP-8110 Fig. 30]",
        notes="A disk alloy first: its Fig. 30 allowable collapses from 27 to 5 (x1e9) "
              "between 1,200 and 1,500 F, so as a BLADE it tops out near 1,000 K."),
    "udimet_700": BladeMaterial(
        key="udimet_700", display_name="Udimet 700 (wrought) blades",
        max_use_temp_k=fig30_temperature_limit_k("udimet_700"), cast=False,
        oxidizer_compatible=True, source="[SP-8110 Fig. 30]",
        notes="Still above the F-1-demonstrated blade loading at Fig. 30's 1,500 F top "
              "point, so its limit is capped there (the data end)."),
    "in100": BladeMaterial(
        key="in100", display_name="IN100 (cast) blades",
        max_use_temp_k=fig30_temperature_limit_k("in100"), cast=True,
        oxidizer_compatible=True, source="[SP-8110 Fig. 30]",
        notes="The strongest cast alloy in Fig. 30 at temperature (22 x1e9 at 1,500 F vs "
              "713C's 12); capped at the 1,500 F top point."),
    "alloy_713c": BladeMaterial(
        key="alloy_713c", display_name="Alloy 713C (cast) blades - F-1",
        max_use_temp_k=fig30_temperature_limit_k("alloy_713c"), cast=True,
        oxidizer_compatible=True, source="[SP-8110 p.3, Table II, Fig. 30]",
        notes="The F-1's turbine blade alloy (investment castings). Its limit IS the F-1 "
              "point by construction: 1,550 F inlet / the 1.08 gas-to-metal margin."),
    "mar_m_246_ds": BladeMaterial(
        key="mar_m_246_ds", display_name="MAR-M-246 (directionally solidified) blades",
        max_use_temp_k=1150.0, cast=True, oxidizer_compatible=True,
        source="[Ch12-Materials via topics/12] (use only; limit Tier 3)",
        notes="SSME HPFTP turbine blades: cast, directionally solidified MAR-M-246 on "
              "Waspaloy hubs (hydrogen-embrittlement-prone). No strength-vs-temperature "
              "data in claude_lit - the 1,150 K limit is a Tier 3 estimate, flagged."),
}


def available_blade_materials():
    return list(BLADE_MATERIALS.keys())


def turbine_gas_temperature_limit_k(rotor_key, blade_key=""):
    """Highest turbine-inlet gas temperature the chosen alloys tolerate without a warning.
    blade_key "" = the single-material rule (rotor limit x the gas-to-metal margin)."""
    rotor = MATERIALS[rotor_key]
    blade = BLADE_MATERIALS.get(blade_key or "")
    if blade is None:
        return rotor.max_use_temp_k * TURBINE_GAS_TO_METAL_MARGIN
    return min(blade.max_use_temp_k * TURBINE_GAS_TO_METAL_MARGIN,
               rotor.max_use_temp_k / DISK_METAL_TEMP_FRACTION)


_STRENGTH_ORDER = {"low": 0, "medium": 1, "high": 2, "very_high": 3}
_STAGED_COMBUSTION_CYCLES = {"frsc", "orsc", "ffsc"}
_OXIDIZER_RICH_CYCLES = {"orsc", "ffsc"}   # FFSC's ox-side turbopump runs an ox-rich preburner


def available_turbopump_materials():
    return list(MATERIALS.keys())


def turbopump_material_suitability(mat_key, *, turbine_inlet_k, tip_speed_m_s,
                                   cycle, touches_oxidizer, blade_key=""):
    """
    Warn-not-block suitability check for a chosen turbopump material against the
    duty the rest of the design implies. Returns a list of human-readable
    warning strings (empty list = nothing to flag). Never raises, never blocks,
    and never changes the user's choice.

    blade_key "" (default): one material for the whole rotor, judged on the turbine gas
    temperature with the 1.08 gas-to-metal margin (the original rule). A BLADE_MATERIALS
    key splits the check: blades on their own [SP-8110 Fig. 30]-derived limit, and the
    disk (mat_key) on an estimated disk metal temperature (DISK_METAL_TEMP_FRACTION x gas).
    """
    mat = MATERIALS[mat_key]
    blade = BLADE_MATERIALS.get(blade_key or "")
    out = []

    if tip_speed_m_s > mat.max_tip_speed_m_s:
        out.append(
            f"{mat.display_name}: required impeller/blade tip speed "
            f"{tip_speed_m_s:.0f} m/s exceeds this material's ~{mat.max_tip_speed_m_s:.0f} m/s "
            f"capability - add a pump stage, drop chamber pressure, or move to a "
            f"higher-strength rotor material.")

    # Turbine disk/blade METAL runs cooler than the gas inlet temperature (short
    # burn, blade cooling, incomplete thermal soak), so allow an 8% margin
    # between the gas temperature and the material's service limit before warning.
    fix = ("lower the turbine gas temperature (GG / tap-off / preburner temperature) or "
           "choose a hotter-capable alloy")
    if blade is None:
        if turbine_inlet_k > mat.max_use_temp_k * TURBINE_GAS_TO_METAL_MARGIN:
            out.append(
                f"{mat.display_name}: turbine-inlet gas ~{turbine_inlet_k:.0f} K is well above its "
                f"~{mat.max_use_temp_k:.0f} K service limit for disk AND blades - {fix}, or set a "
                f"separate turbine blade material (real turbines near 1,100 K ran wrought disks "
                f"with cast blades, e.g. the F-1's Inconel 718 / 713C [SP-8110]).")
    else:
        if turbine_inlet_k > blade.max_use_temp_k * TURBINE_GAS_TO_METAL_MARGIN:
            out.append(
                f"{blade.display_name}: turbine-inlet gas ~{turbine_inlet_k:.0f} K is above the "
                f"blades' ~{blade.max_use_temp_k:.0f} K limit {blade.source} - {fix}.")
        disk_k = turbine_inlet_k * DISK_METAL_TEMP_FRACTION
        if disk_k > mat.max_use_temp_k:
            out.append(
                f"{mat.display_name} (disk/rotor): estimated disk metal ~{disk_k:.0f} K "
                f"({DISK_METAL_TEMP_FRACTION:.3f} x gas, F-1-anchored estimate) exceeds its "
                f"~{mat.max_use_temp_k:.0f} K service limit - {fix}.")
        if (touches_oxidizer and cycle in _OXIDIZER_RICH_CYCLES
                and not blade.oxidizer_compatible):
            out.append(f"{blade.display_name} is not oxidiser-compatible but an oxidiser-rich "
                       f"turbine wets it.")

    if touches_oxidizer and not mat.oxidizer_compatible:
        extra = (" Titanium ignites on impact/rub in oxygen." if mat.key == "titanium_forged"
                 else "")
        out.append(
            f"{mat.display_name} is not oxidiser-compatible but this design wets it with the "
            f"oxidiser stream (oxidiser pump / oxidiser-rich turbine).{extra} Use Monel K-500 "
            f"or an oxygen-compatible coated superalloy for oxidiser-side rotating hardware.")

    if cycle in _OXIDIZER_RICH_CYCLES and not mat.oxidizer_compatible:
        out.append(
            f"Oxidiser-rich staged combustion runs hot oxygen-rich gas through the turbine; "
            f"{mat.display_name} needs an oxidation-tolerant substitute (Monel-class / coated).")

    if cycle in _STAGED_COMBUSTION_CYCLES and _STRENGTH_ORDER[mat.strength_class] < _STRENGTH_ORDER["high"]:
        out.append(
            f"Staged combustion drives pump discharge pressure well above 2x chamber pressure; "
            f"{mat.display_name} ({mat.strength_class} strength class) is under-strength for the "
            f"housings/impellers - real staged-combustion turbopumps use HIP powder-metallurgy "
            f"superalloys.")

    return out


if __name__ == "__main__":
    keys = available_turbopump_materials()
    assert all(0.0 <= m.metallic <= 1.0 and 0.0 <= m.roughness <= 1.0
               for m in MATERIALS.values()), "every rotor material carries PBR values"
    assert keys and all(MATERIALS[k].key == k for k in keys)
    # Titanium tip-speed anchor is the SP-8107 forged-Ti value.
    assert MATERIALS["titanium_forged"].max_tip_speed_m_s == 853.0
    assert MATERIALS["titanium_forged"].max_tip_speed_m_s == max(
        m.max_tip_speed_m_s for m in MATERIALS.values()), "Ti should be the tip-speed ceiling"

    # A high-tip-speed LH2 pump on aluminium should complain on tip speed; on
    # forged titanium (below its temp limit) it should not.
    w_al = turbopump_material_suitability("aluminum_7075", turbine_inlet_k=500.0,
                                          tip_speed_m_s=650.0, cycle="gas_generator",
                                          touches_oxidizer=False)
    w_ti = turbopump_material_suitability("titanium_forged", turbine_inlet_k=500.0,
                                          tip_speed_m_s=650.0, cycle="gas_generator",
                                          touches_oxidizer=False)
    assert any("tip speed" in s for s in w_al) and not w_ti, (w_al, w_ti)

    # Titanium wetted by oxidiser -> hazard warning.
    w_ti_ox = turbopump_material_suitability("titanium_forged", turbine_inlet_k=300.0,
                                             tip_speed_m_s=100.0, cycle="gas_generator",
                                             touches_oxidizer=True)
    assert any("oxid" in s.lower() for s in w_ti_ox), w_ti_ox

    # Aluminium on a staged-combustion cycle -> under-strength warning.
    w_al_sc = turbopump_material_suitability("aluminum_7075", turbine_inlet_k=300.0,
                                             tip_speed_m_s=100.0, cycle="frsc",
                                             touches_oxidizer=False)
    assert any("staged combustion" in s.lower() for s in w_al_sc), w_al_sc

    # --- bearing materials ---
    bkeys = available_bearing_materials()
    assert bkeys and all(BEARING_MATERIALS[k].key == k for k in bkeys)
    # Capability ordering: 440C < Cronidur 30 < Si3N4 ceramic (DN and temp).
    assert (BEARING_MATERIALS["440c_steel"].max_dn_mm_rpm
            < BEARING_MATERIALS["cronidur_30"].max_dn_mm_rpm
            < BEARING_MATERIALS["si3n4_ceramic"].max_dn_mm_rpm)
    assert BEARING_MATERIALS["si3n4_ceramic"].oxidizer_compatible
    assert not BEARING_MATERIALS["440c_steel"].oxidizer_compatible

    # A DN that 440C can't take but Cronidur 30 can.
    dn_mid = (BEARING_MATERIALS["440c_steel"].max_dn_mm_rpm
              + BEARING_MATERIALS["cronidur_30"].max_dn_mm_rpm) / 2.0
    w_440c = bearing_suitability("440c_steel", dn_mm_rpm=dn_mid, use_temp_k=400.0)
    w_cron = bearing_suitability("cronidur_30", dn_mm_rpm=dn_mid, use_temp_k=400.0)
    assert any("DN" in s for s in w_440c) and not w_cron, (w_440c, w_cron)

    # Si3N4 never warns where 440C does at the same (DN, temp) - monotonic ordering.
    for dn_test in (5e5, 1.0e6, 1.3e6, 1.6e6, 2.0e6, 2.3e6):
        w_steel = bearing_suitability("440c_steel", dn_mm_rpm=dn_test, use_temp_k=400.0)
        w_ceramic = bearing_suitability("si3n4_ceramic", dn_mm_rpm=dn_test, use_temp_k=400.0)
        assert not (w_steel == [] and w_ceramic != []), (dn_test, w_steel, w_ceramic)

    # --- blade materials (SP-8110 Fig. 30, F-1 anchored) ---
    assert abs(BLADE_MATERIALS["alloy_713c"].max_use_temp_k - F1_BLADE_METAL_K) < 0.5, \
        "713C's limit is the F-1 blade point by construction"
    assert 13.0 < F1_DEMONSTRATED_AAN2 < 17.0, F1_DEMONSTRATED_AAN2   # ~15 x1e9 at 1,400 F
    assert (BLADE_MATERIALS["inconel_718"].max_use_temp_k
            < BLADE_MATERIALS["alloy_713c"].max_use_temp_k
            <= BLADE_MATERIALS["in100"].max_use_temp_k), "718 < 713C <= IN100 at temperature"
    # F-1 hardware (1,116 K gas, Inconel 718 disks + 713C blades): no temperature warning;
    # 718 blades: warns; the single-material 718 rule flags the real F-1 (why the split exists).
    kw = dict(turbine_inlet_k=F1_TURBINE_INLET_K, tip_speed_m_s=300.0, cycle="gas_generator",
              touches_oxidizer=True)
    w_f1 = turbopump_material_suitability("inconel_718", blade_key="alloy_713c", **kw)
    w_718b = turbopump_material_suitability("inconel_718", blade_key="inconel_718", **kw)
    w_one = turbopump_material_suitability("inconel_718", **kw)
    assert not any("K" in s and "limit" in s for s in w_f1), w_f1
    assert any("blades" in s for s in w_718b), w_718b
    assert any("disk AND blades" in s for s in w_one), w_one
    assert abs(turbine_gas_temperature_limit_k("inconel_718", "alloy_713c")
               - F1_TURBINE_INLET_K) < 1.0

    print(f"turbopump_materials.py smoke test OK - {len(keys)} rotor materials, "
          f"{len(BLADE_MATERIALS)} blade materials (713C {BLADE_MATERIALS['alloy_713c'].max_use_temp_k:.0f} K, "
          f"718 {BLADE_MATERIALS['inconel_718'].max_use_temp_k:.0f} K, IN100 "
          f"{BLADE_MATERIALS['in100'].max_use_temp_k:.0f} K; F-1 blade loading "
          f"{F1_DEMONSTRATED_AAN2:.1f}e9 in2rpm2), "
          f"{len(bkeys)} bearing materials, tip-speed ceiling "
          f"{MATERIALS['titanium_forged'].max_tip_speed_m_s:.0f} m/s (forged Ti, SP-8107 "
          f"anchor), DN ceiling {BEARING_MATERIALS['si3n4_ceramic'].max_dn_mm_rpm:,.0f} "
          f"mm*rpm (Si3N4, flagged Tier-3 estimate)")
