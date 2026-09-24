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
        display_name="Powder-Metallurgy Superalloy (HIP, e.g. MAR-M / Rene PM)",
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
        notes="Hot-isostatic-pressed powder-metallurgy superalloy blisks are "
              "what real staged-combustion turbopumps (KBKhA RD-0124-class, "
              "SSME) use to survive the pump discharge pressures (>2x Pc) and "
              "turbine temperatures those cycles impose - [KBKhA] notes staged "
              "combustion cannot use the lower-strength cast/forged housings a "
              "GG cycle gets away with. Highest cost. Figures are Tier 3 estimates.",
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


_STRENGTH_ORDER = {"low": 0, "medium": 1, "high": 2, "very_high": 3}
_STAGED_COMBUSTION_CYCLES = {"frsc", "orsc", "ffsc"}
_OXIDIZER_RICH_CYCLES = {"orsc", "ffsc"}   # FFSC's ox-side turbopump runs an ox-rich preburner


def available_turbopump_materials():
    return list(MATERIALS.keys())


def turbopump_material_suitability(mat_key, *, turbine_inlet_k, tip_speed_m_s,
                                   cycle, touches_oxidizer):
    """
    Warn-not-block suitability check for a chosen turbopump material against the
    duty the rest of the design implies. Returns a list of human-readable
    warning strings (empty list = nothing to flag). Never raises, never blocks.
    """
    mat = MATERIALS[mat_key]
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
    if turbine_inlet_k > mat.max_use_temp_k * 1.08:
        out.append(
            f"{mat.display_name}: turbine-inlet gas ~{turbine_inlet_k:.0f} K is well above its "
            f"~{mat.max_use_temp_k:.0f} K service limit - the turbine disk/blades need a "
            f"hotter-capable alloy (powder-met superalloy) or turbine cooling.")

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

    print(f"turbopump_materials.py smoke test OK - {len(keys)} rotor materials, "
          f"{len(bkeys)} bearing materials, tip-speed ceiling "
          f"{MATERIALS['titanium_forged'].max_tip_speed_m_s:.0f} m/s (forged Ti, SP-8107 "
          f"anchor), DN ceiling {BEARING_MATERIALS['si3n4_ceramic'].max_dn_mm_rpm:,.0f} "
          f"mm*rpm (Si3N4, flagged Tier-3 estimate)")
