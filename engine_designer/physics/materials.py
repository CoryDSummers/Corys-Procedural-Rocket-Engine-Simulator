"""
Chamber/nozzle material dropdown catalog + a thermal-margin check.

Per the locked decision, this WARNS on a thermally marginal material choice
but never blocks it (modding aid, not a hard simulator) - unlike Children of
a Dead Earth's confirmed hard melting-point gate.

Standard propulsion-engineering figures (density, service temperature,
relative cost) - no further research needed for this part, unlike the
combustion tables.

Thermal-margin heuristic (explicitly approximate, not real heat-transfer
analysis): the adiabatic wall temperature is close to Tc (recovery factor
~1). An active cooling system is what actually keeps the material below
that. We do NOT model coolant-channel heat transfer here - instead each
material's typical cooling method carries a documented "effectiveness
fraction" (assumed achievable wall temperature as a fraction of Tc), and the
warning compares that assumed wall temperature to the material's max
service temperature. This is a coarse proxy, not a substitute for real
regenerative-cooling channel design.

Contraction-ratio heat-flux factor: the classical Bartz correlation's local
area-ratio term (At/A_local)^0.9 (Sutton & Biblarz) is a real, citable
relation - gas-side heat flux at the chamber wall scales with (1/CR)^0.9, so
a tighter chamber (low contraction ratio) genuinely runs a hotter wall than
a roomier one. contraction_ratio_heat_flux_factor() below applies that
exponent, referenced at the tool's own CR default (1.6) so nothing changes
there, then damps it (WALL_TEMP_DAMPING) before folding it into the coarse
wall-temp proxy - the raw exponent alone would swing margin_ratio by -17%/
+229% across the CR slider's full range, which is more precision than a flat
"wall temp = Tc * fraction" proxy with no coolant-side heat-transfer model
behind it can honestly claim. The 0.9 exponent is the real Bartz constant;
the 0.5 damping and the defensive clamp are this tool's own judgment call,
not derived - see ASSUMPTIONS.md.

allowable_stress_pa: real, cited high-temperature yield/allowable-stress
figures (at or near each material's max_service_temp_k) used by
physics/mass_model.py to derive chamber/nozzle wall thickness from a
thin-wall pressure-vessel hoop-stress formula (t = safety_factor * Pc * r /
allowable_stress) - the same "derive a real physical consequence from
chamber pressure" pattern already used for turbopump mass
(physics/turbopump_tech.py's specific_power_w_kg). Confidence varies by
material - see each material's `notes` and ASSUMPTIONS.md for exactly what's
well-sourced vs. extrapolated beyond good data. ablative_phenolic's value is
a structural (char-layer composite) floor only - its ACTUAL wall thickness
is governed by char consumption over the rated burn time, not hoop stress
(see ABLATIVE_CONSUMPTION_RATE_M_S below and physics/mass_model.py).

ABLATIVE_CONSUMPTION_RATE_M_S: real ablative liners regress/char away at a
rate that scales strongly with heat flux (NASA TM-X, "Application of
Ablation to a High Chamber Pressure Rocket Engine," 1971: silica-phenolic
liner at 4000 psia chamber pressure eroded at ~0.18-0.22 cm/s, an extreme
upper bound at much higher heat flux than this tool's typical designs).
Lower-heat-flux, hypergolic-class chambers (NASA TM-107041, ~165 psia)
show sharply lower (qualitatively, "6-75x more erosion-resistant") rates
that the source doesn't reduce to a single absolute number. The single flat
rate below is a reasoned point within the real cited range for a
representative small-to-medium hypergolic-class ablative chamber - Tier 2/3,
see ASSUMPTIONS.md.
"""
from dataclasses import dataclass

CONTRACTION_RATIO_REFERENCE = 1.6   # matches EngineDesign's contraction_ratio
                                     # default, so validate.py's spot checks
                                     # (which don't pass contraction_ratio,
                                     # hence get this default) see factor==1.0
BARTZ_AREA_RATIO_EXPONENT = 0.9     # real, citable Bartz/Sutton & Biblarz term
WALL_TEMP_DAMPING = 0.5             # NOT a Bartz constant - only half the
                                     # geometric flux ratio's log-swing is
                                     # allowed into the wall-temp proxy
HEAT_FLUX_FACTOR_CLAMP = (0.5, 1.6)  # defensive backstop; doesn't bind for
                                      # any CR in the real 1.3-6.0 slider range
THIN_MARGIN_THRESHOLD = 1.15         # same threshold thermal_margin() uses for
                                      # its own "thin margin" warning - reused
                                      # by design.py's rated-burn-time scaling
                                      # as the margin_ratio reference point

ABLATIVE_CONSUMPTION_RATE_M_S = 1.5e-4  # ~0.15 mm/s - a reasoned point within
                                         # the real cited range (see module
                                         # docstring) for a representative
                                         # small/medium hypergolic-class
                                         # ablative chamber; NOT scaled by
                                         # heat flux/Pc here (Tier 3 simplification)

CHAR_DEPTH_SAFETY_FACTOR = 1.25  # [SP-8124 Sec.2.1/3.1]: real cited char-depth safety
                                  # factor for sizing an ablative liner's sacrificial
                                  # thickness against its predicted char depth over the
                                  # design's target burn time (mass_model.
                                  # ablative_liner_thickness_m). Tier 1/validated - a
                                  # real NASA design criterion, not an estimate (unlike
                                  # ABLATIVE_CONSUMPTION_RATE_M_S itself, which stays
                                  # Tier 2/3). Notably, mass_model.SAFETY_FACTOR (1.5,
                                  # the structural hoop-stress margin used for the
                                  # OVERWRAP behind this liner) independently sits
                                  # inside SP-8124's own cited 1.5-1.8 fiberglass-
                                  # overwrap safety-factor band - a nice cross-check,
                                  # not a coincidence forced to fit.

_REFRASIL_CONSUMPTION_RATE_M_S = 2.7e-5  # ~74x more erosion-resistant than the 4000psi
                                          # extreme-case baseline above - the top of this
                                          # docstring's own cited "6-75x more erosion-
                                          # resistant" range for low-Pc hypergolic chambers,
                                          # picked (vs. the generic entry's ~13x) to reflect
                                          # Refrasil's higher silica content plus the added
                                          # asbestos-phenolic insulation layer. NOT back-
                                          # solved to hit LMAE's real 560s ratedBurnTime
                                          # exactly - doing so would need a rate ~750x more
                                          # resistant than the cited baseline (~10x past
                                          # this range's own top), an artifact of this tool's
                                          # ablative_rated_burn_time_s reusing the hoop-
                                          # stress-derived wall thickness (thin at LMAE's low
                                          # 120 psia Pc) rather than a real ablative liner's
                                          # erosion-life sizing. See physics/validate.py's
                                          # LMAE row and ASSUMPTIONS.md.


def contraction_ratio_heat_flux_factor(contraction_ratio):
    """
    Relative chamber-wall heat-flux factor from contraction ratio, via the
    Bartz area-ratio term (1/CR)^0.9, referenced at CR=1.6 and damped (see
    module docstring). Multiplies thermal_margin()'s assumed wall temp for
    the CHAMBER material check only - the nozzle-extension/bell material
    check is unrelated to chamber contraction ratio and must keep passing
    the default heat_flux_factor=1.0.
    """
    raw = (CONTRACTION_RATIO_REFERENCE / contraction_ratio) ** BARTZ_AREA_RATIO_EXPONENT
    damped = raw ** WALL_TEMP_DAMPING
    lo, hi = HEAT_FLUX_FACTOR_CLAMP
    return max(lo, min(hi, damped))


@dataclass(frozen=True)
class Material:
    key: str
    display_name: str
    density_kg_m3: float
    max_service_temp_k: float
    relative_cost_factor: float
    cooling_method: str
    cooling_effectiveness: float  # assumed wall temp = Tc * this fraction
    color_hex: str  # real-world-plausible metal/composite tone for the 3D preview -
                     # not spectrophotometrically measured, informational/rendering only
    thermal_conductivity_w_mk: float  # NOT read by thermal_margin(). Real
                                       # physics use added 2026-09-17: the
                                       # longitudinal thermal-restraint term
                                       # (Huzel eq 4-28/4-31) in design.py's
                                       # per-wall_construction jacket-
                                       # overpressure check (dT = q*t/k)
    tech_era_hint: str  # plain display string (e.g. "Modern (1970s+, ...)") -
                         # NOT a real RP-1 tech-node ID, NOT wired into any
                         # .cfg export gating - flavor/context only
    allowable_stress_pa: float  # high-temperature yield/allowable stress,
                                 # used to derive wall thickness via hoop
                                 # stress (physics/mass_model.py) - see module
                                 # docstring for sourcing/confidence per material
    emissivity: float           # hot-face total hemispherical emissivity, as
                                 # actually used in service (coated where the
                                 # material needs a coating for radiative duty).
                                 # Read by cooling.radiative_wall_temperature()
                                 # for the nozzle-extension equilibrium check -
                                 # matters most for the cooling_method="radiative"
                                 # entries. Tier 2, standard figures.
    youngs_modulus_pa: float    # elastic modulus at temperature, for the throat
                                 # low-cycle thermal-fatigue estimate
                                 # (physics/mass_model.py). Tier 2.
    cte_per_k: float            # linear coefficient of thermal expansion [1/K],
                                 # same use. Tier 2.
    specular_strength: float    # 3D-preview Blinn-Phong highlight strength (0..1) -
                                 # cosmetic/rendering only, same tier as color_hex,
                                 # no physics meaning. Higher = shinier/more metallic.
    shininess: float            # 3D-preview Blinn-Phong exponent - cosmetic/rendering
                                 # only, same tier as color_hex. Higher = tighter/more
                                 # polished highlight, lower = broader/duller highlight.
                                 # Legacy Blinn-Phong pair - metallic/roughness below
                                 # are what the PBR preview shader actually reads.
    notes: str
    metallic: float = None       # 3D-preview PBR metalness (0 dielectric .. 1 bare metal) -
                                 # cosmetic/rendering only, same tier as color_hex. Coated
                                 # refractories (silicide on Nb/TZM) sit low: the visible
                                 # surface is the coating, not the metal. None = derive
                                 # from specular_strength/shininess (preview3d_gl_core.
                                 # blinn_to_pbr). Also the value a future mesh/texture
                                 # export would bake into its metalness map.
    roughness: float = None      # 3D-preview PBR perceptual roughness (0 mirror .. 1 matte),
                                 # same tier/None rule as metallic.
    allowed_cooling_methods: tuple = ()  # the ONLY section cooling methods this material
                                 # can physically be built for (cooling.COOLING_METHODS
                                 # subset; its own cooling_method is always one). An explicit
                                 # choice outside it is HARD-BLOCKED - coerced back to
                                 # cooling_method with a failing checklist row
                                 # (cooling.resolve_cooling_method_checked) - a deliberate
                                 # exception to the tool's "warn, don't block" rule: blocked
                                 # combos are ones whose construction does not exist (no
                                 # coolant passages in a charring composite, a metal can't
                                 # ablate, a refractory/C-C wall is never a regen jacket,
                                 # copper can't run at radiation-equilibrium temperature),
                                 # not merely risky ones - those stay allowed and the thermal
                                 # margin warns. Film is NOT a section method: it is the
                                 # EngineDesign.film_cooling_fraction / nozzle_film_fraction
                                 # overlay, allowed on every material. See ASSUMPTIONS.md.
    ablative_consumption_rate_m_s: float = None  # per-material char/erosion rate override
                                 # for mass_model.ablative_rated_burn_time_s. None (the
                                 # default, used by every material defined before this
                                 # field existed) means "use the flat module-level
                                 # ABLATIVE_CONSUMPTION_RATE_M_S below" - zero behavior
                                 # change for ablative_phenolic. A material sets this
                                 # explicitly only when it has its own real-engine-derived
                                 # rate - see refrasil_phenolic below.
    e_c_pa: float = None         # tangential modulus from the COMPRESSION stress-strain
                                 # curve at wall temperature [Huzel eq 4-29] - a distinct,
                                 # generally lower, nonlinear-regime modulus from
                                 # youngs_modulus_pa (the elastic/tangential modulus, used
                                 # as E_t), needed for the longitudinal thermal inelastic-
                                 # buckling criterion S_c = 4*E_t*E_c*t/[(sqrt(E_t)+
                                 # sqrt(E_c))^2*sqrt(3*(1-v^2))*r] (mass_model.
                                 # longitudinal_buckling_stress_pa). None (every material
                                 # today) means "no compression-curve data available" -
                                 # the buckling check reports n/a rather than estimating a
                                 # cross-material ratio with no real grounding (unlike
                                 # Huzel's own cited K_A 0.3-0.5 range for the elongated-
                                 # tube bending term, E_c genuinely varies by alloy in real
                                 # Shanley tangent-modulus buckling theory - a flat guessed
                                 # ratio here would be a materially different, less
                                 # defensible kind of estimate). See ASSUMPTIONS.md.


MATERIALS = {
    "narloy_z": Material(
        key="narloy_z",
        display_name="NARloy-Z Copper Alloy (Cu-Ag-Zr)",
        density_kg_m3=9000.0,
        max_service_temp_k=800.0,
        relative_cost_factor=1.0,
        cooling_method="regenerative",
        allowed_cooling_methods=("regenerative", "dump", "uncooled"),
        cooling_effectiveness=0.25,
        color_hex="#B87333",
        thermal_conductivity_w_mk=325.0,
        tech_era_hint="Modern (1970s+, SSME-era copper alloy)",
        allowable_stress_pa=1.1e+08,
        emissivity=0.35,
        youngs_modulus_pa=1.15e+11,
        cte_per_k=1.85e-05,
        specular_strength=0.65,
        shininess=96.0,
        metallic=1.0,
        roughness=0.3,
        notes="High thermal conductivity regen-chamber baseline (SSME/most modern engines). "
              "Needs active regen cooling; poor choice uncooled.",
    ),
    "inconel_718": Material(
        key="inconel_718",
        display_name="Inconel 718 Nickel Superalloy",
        density_kg_m3=8190.0,
        max_service_temp_k=1250.0,
        relative_cost_factor=1.8,
        cooling_method="regenerative",
        allowed_cooling_methods=("regenerative", "dump", "radiative", "uncooled"),
        cooling_effectiveness=0.30,
        color_hex="#8E8C84",
        thermal_conductivity_w_mk=15.0,
        tech_era_hint="Mature/modern (widespread since the 1960s)",
        allowable_stress_pa=2.0e+08,
        emissivity=0.7,
        youngs_modulus_pa=2.0e+11,
        cte_per_k=1.3e-05,
        specular_strength=0.40,
        shininess=45.0,
        metallic=1.0,
        roughness=0.42,
        notes="Higher-temp, higher-strength, lower thermal conductivity than copper alloys. "
              "Common for nozzle extensions and structural jackets.",
    ),
    "inconel_x750": Material(
        key="inconel_x750",
        display_name="Inconel X-750 Nickel-Chromium Superalloy",
        density_kg_m3=8280.0,
        max_service_temp_k=1255.0,
        relative_cost_factor=2.0,
        cooling_method="regenerative",
        allowed_cooling_methods=("regenerative", "dump", "radiative", "uncooled"),
        cooling_effectiveness=0.31,
        color_hex="#8C8A82",
        thermal_conductivity_w_mk=12.0,
        tech_era_hint="Mature (1950s+, predates Inconel 718; classic precipitation-hardened "
                      "Ni-Cr-Fe superalloy)",
        allowable_stress_pa=2.1e+08,
        emissivity=0.90,
        youngs_modulus_pa=2.14e+11,
        cte_per_k=1.40e-05,
        specular_strength=0.40,
        shininess=45.0,
        metallic=1.0,
        roughness=0.42,
        notes="Precipitation-hardened by gamma-prime Ni3(Al,Ti) (Special Metals SMC-067), "
              "'used extensively in rocket-engine thrust chambers' per the alloy's own "
              "datasheet. Named alongside Inconel 718 as a real SP-8120 nozzle-hatband "
              "material (see hatbands.py/claude_lit topic 12) - this entry makes it "
              "selectable as a chamber/nozzle material too. Broadly similar duty to "
              "Inconel 718 (slightly lower thermal conductivity, real cited emissivity "
              "0.90 vs. 718's uncited 0.7) - predates 718 and was the earlier workhorse "
              "Ni-Cr thrust-chamber/hot-structure alloy.",
    ),
    "stainless_steel": Material(
        key="stainless_steel",
        display_name="Stainless Steel (304/316)",
        density_kg_m3=8000.0,
        max_service_temp_k=1100.0,
        relative_cost_factor=0.5,
        cooling_method="regenerative",
        allowed_cooling_methods=("regenerative", "dump", "radiative", "uncooled"),
        cooling_effectiveness=0.30,
        color_hex="#C0C0C0",
        thermal_conductivity_w_mk=16.0,
        tech_era_hint="Early/mature (widely available since the 1900s-40s, common on early "
                      "liquid rocket engines)",
        allowable_stress_pa=1.0e+08,
        emissivity=0.7,
        youngs_modulus_pa=1.93e+11,
        cte_per_k=1.7e-05,
        specular_strength=0.70,
        shininess=110.0,
        metallic=1.0,
        roughness=0.28,
        notes="Cheap, easy to work, moderate temperature capability. Common on early/cheap "
              "pressure-fed and hypergolic engines, and as brazed regen tube walls (J-2's "
              "347 SS tubes) - hence its regenerative default. A film-cooled-only SS "
              "chamber = 'uncooled' wall + the film-cooling overlay.",
    ),
    "niobium_c103": Material(
        key="niobium_c103",
        display_name="Niobium C-103 (radiative)",
        density_kg_m3=8600.0,
        max_service_temp_k=1650.0,
        relative_cost_factor=2.5,
        cooling_method="radiative",
        allowed_cooling_methods=("radiative", "uncooled"),
        cooling_effectiveness=0.55,
        color_hex="#6E7B8B",
        thermal_conductivity_w_mk=54.0,
        tech_era_hint="Mature (1960s+, Apollo-era radiative nozzles)",
        allowable_stress_pa=1.8e+08,
        emissivity=0.8,
        youngs_modulus_pa=1.0e+11,
        cte_per_k=7.5e-06,
        specular_strength=0.30,
        shininess=35.0,
        metallic=0.2,
        roughness=0.65,
        notes="Radiatively-cooled nozzle-extension material (Apollo SPS, LMDE skirt). No "
              "active cooling needed but requires an oxidation-protective coating.",
    ),
    "ablative_phenolic": Material(
        key="ablative_phenolic",
        display_name="Ablative Phenolic-Silica",
        density_kg_m3=1400.0,
        max_service_temp_k=2000.0,
        relative_cost_factor=0.7,
        cooling_method="ablative",
        allowed_cooling_methods=("ablative",),
        cooling_effectiveness=0.35,
        color_hex="#2B1B12",
        thermal_conductivity_w_mk=0.30,
        tech_era_hint="Early/mature (widely used since the 1950s-60s, simple low-tech option)",
        allowable_stress_pa=5.0e+07,
        emissivity=0.9,
        youngs_modulus_pa=1.5e+10,
        cte_per_k=1.0e-05,
        specular_strength=0.04,
        shininess=8.0,
        metallic=0.0,
        roughness=0.88,
        notes="Sacrificial char layer, no active cooling plumbing. Light, cheap, but "
              "consumed over the burn - a burn-time/life limiter, not modeled here.",
    ),
    "refrasil_phenolic": Material(
        key="refrasil_phenolic",
        display_name="Refrasil-Phenolic / Asbestos-Insulated (LMAE-style)",
        density_kg_m3=1800.0,
        max_service_temp_k=2150.0,
        relative_cost_factor=0.9,
        cooling_method="ablative",
        allowed_cooling_methods=("ablative",),
        cooling_effectiveness=0.38,
        color_hex="#3A2415",
        thermal_conductivity_w_mk=0.18,
        tech_era_hint="Mature (1960s-70s, Apollo-era hypergolic ablative chambers - "
                      "LMAE/SPS lineage)",
        allowable_stress_pa=6.0e+07,
        emissivity=0.9,
        youngs_modulus_pa=2.0e+10,
        cte_per_k=1.2e-05,
        specular_strength=0.05,
        shininess=8.0,
        metallic=0.0,
        roughness=0.85,
        ablative_consumption_rate_m_s=_REFRASIL_CONSUMPTION_RATE_M_S,
        notes="Real 3-layer Apollo-era ablative chamber construction (Bell Aerosystems "
              "Lunar Module Ascent Engine, Engine_Configs/LMAE_Config.cfg): a Refrasil "
              "(near-pure amorphous silica cloth) phenolic ablative liner, insulated with "
              "asbestos-phenolic, wrapped in a structural glass-fiber overwrap that carries "
              "the pressure load. Denser and higher max service temp than the generic "
              "ablative_phenolic entry (higher-silica-content liner); lower effective "
              "through-wall conductivity (the asbestos-phenolic layer's job is knocking "
              "down conduction to the structural jacket). Its consumption rate is back-"
              "solved so this tool's own chamber-wall-thickness sizing at LMAE's real "
              "operating point (Pc 0.83 MPa, eps 45.6, MON1/A-50, ~15.57 kN vac) reproduces "
              "LMAE's real ratedBurnTime = 560 s - see ASSUMPTIONS.md and "
              "physics/validate.py's ablative realism-sanity block.",
    ),
    "grcop_84": Material(
        key="grcop_84",
        display_name="GRCop-84 Copper-Chromium-Niobium Alloy",
        density_kg_m3=8900.0,
        max_service_temp_k=900.0,
        relative_cost_factor=1.5,
        cooling_method="regenerative",
        allowed_cooling_methods=("regenerative", "dump", "uncooled"),
        cooling_effectiveness=0.27,
        color_hex="#A5672A",
        thermal_conductivity_w_mk=290.0,
        tech_era_hint="Modern (2000s+, NASA Glenn Research Center copper alloy)",
        allowable_stress_pa=1.5e+08,
        emissivity=0.35,
        youngs_modulus_pa=1.2e+11,
        cte_per_k=1.75e-05,
        specular_strength=0.63,
        shininess=90.0,
        metallic=1.0,
        roughness=0.32,
        notes="NASA GRC Cu-8Cr-4Nb alloy. Better high-temperature creep/fatigue resistance "
              "than NARloy-Z at similar conductivity, at higher processing cost (powder "
              "metallurgy) - used on advanced regen-chamber test articles/RS-25 upgrade "
              "studies.",
    ),
    "rhenium_iridium": Material(
        key="rhenium_iridium",
        display_name="Rhenium (Iridium-coated, radiative)",
        density_kg_m3=21000.0,
        max_service_temp_k=2200.0,
        relative_cost_factor=6.0,
        cooling_method="radiative",
        allowed_cooling_methods=("radiative", "uncooled"),
        cooling_effectiveness=0.60,
        color_hex="#D6D6D8",
        thermal_conductivity_w_mk=48.0,
        tech_era_hint="Modern (1990s+, small bipropellant apogee/upper-stage engines)",
        allowable_stress_pa=9.0e+07,
        emissivity=0.4,
        youngs_modulus_pa=4.6e+11,
        cte_per_k=6.6e-06,
        specular_strength=0.45,
        shininess=55.0,
        metallic=1.0,
        roughness=0.35,
        notes="Iridium-coated rhenium radiative chamber/nozzle, as used on small hypergolic "
              "apogee/upper-stage thrusters (R-4D lineage, Aestus). Extremely expensive "
              "(rhenium is one of the rarest/costliest engineering metals) - realistic only "
              "at small scale.",
    ),
    "haynes_230": Material(
        key="haynes_230",
        display_name="Haynes 230 Nickel Superalloy",
        density_kg_m3=8970.0,
        max_service_temp_k=1400.0,
        relative_cost_factor=2.2,
        cooling_method="regenerative",
        allowed_cooling_methods=("regenerative", "dump", "radiative", "uncooled"),
        cooling_effectiveness=0.32,
        color_hex="#79776E",
        thermal_conductivity_w_mk=10.5,
        tech_era_hint="Modern (1980s+, gas-turbine-derived nickel superalloy)",
        allowable_stress_pa=1.5e+08,
        emissivity=0.7,
        youngs_modulus_pa=2.11e+11,
        cte_per_k=1.4e-05,
        specular_strength=0.38,
        shininess=42.0,
        metallic=1.0,
        roughness=0.45,
        notes="Ni-Cr-W-Mo superalloy (a NICKEL superalloy, not cobalt-based) - better "
              "high-temperature oxidation resistance and fabricability than Inconel 718, at "
              "higher cost. A step up from Inconel 718 for hot structure/nozzle extensions "
              "rather than a chamber baseline.",
    ),
    "carbon_carbon": Material(
        key="carbon_carbon",
        display_name="Carbon-Carbon Composite",
        density_kg_m3=1800.0,
        max_service_temp_k=1900.0,
        relative_cost_factor=3.5,
        cooling_method="radiative",
        allowed_cooling_methods=("radiative", "uncooled"),
        cooling_effectiveness=0.55,
        color_hex="#1C1C1C",
        thermal_conductivity_w_mk=20.0,
        tech_era_hint="Modern (1970s+ SRM/TPS origin, adapted to liquid-engine radiative "
                      "nozzle extensions since ~1990s-2000s)",
        allowable_stress_pa=2.5e+08,
        emissivity=0.85,
        youngs_modulus_pa=6.0e+10,
        cte_per_k=1.5e-06,
        specular_strength=0.03,
        shininess=8.0,
        metallic=0.0,
        roughness=0.7,
        notes="Lightweight radiatively-cooled composite (Shuttle RCC/SRM-nozzle lineage), "
              "used on some hypergolic upper-stage engine nozzle extensions (e.g. OMS-class "
              "engines). Needs an oxidation-protective coating (e.g. SiC) for repeated use "
              "in an oxidizing exhaust stream. Thermal conductivity is strongly anisotropic "
              "(much higher in-plane along the fiber weave than through-thickness) - the "
              "figure here is a representative through-thickness value.",
    ),
    "molybdenum_tzm": Material(
        key="molybdenum_tzm",
        display_name="Molybdenum TZM Alloy",
        density_kg_m3=10200.0,
        max_service_temp_k=1950.0,
        relative_cost_factor=2.0,
        cooling_method="radiative",
        allowed_cooling_methods=("radiative", "uncooled"),
        cooling_effectiveness=0.55,
        color_hex="#9A9C9E",
        thermal_conductivity_w_mk=123.0,
        tech_era_hint="Mature (1960s+, historically used for high-temp nozzle throat "
                      "inserts/furnace hardware)",
        allowable_stress_pa=1.5e+08,
        emissivity=0.85,
        youngs_modulus_pa=3.2e+11,
        cte_per_k=5.3e-06,
        specular_strength=0.42,
        shininess=48.0,
        metallic=0.2,
        roughness=0.65,
        notes="Mo-0.5Ti-0.08Zr alloy. Needs oxidation protection or a reducing/fuel-rich "
              "environment above ~800 K. Legitimate historical radiative-nozzle option, "
              "largely superseded by niobium/rhenium alloys for flight hardware specifically "
              "because of its much higher density (10200 vs. niobium's 8600 kg/m3) - a real "
              "mass penalty, not a performance deficiency.",
    ),
    "titanium_6al4v": Material(
        key="titanium_6al4v",
        display_name="Titanium 6Al-4V Alloy (radiative)",
        density_kg_m3=4430.0,
        max_service_temp_k=700.0,
        relative_cost_factor=2.0,
        cooling_method="radiative",
        allowed_cooling_methods=("radiative", "uncooled"),
        cooling_effectiveness=0.50,
        color_hex="#8A8D91",
        thermal_conductivity_w_mk=6.7,
        tech_era_hint="Mature (1960s+, Bell Aerosystems Agena XLR81 titanium radiative "
                      "nozzle extensions - Model 8096/8247)",
        allowable_stress_pa=9.0e+07,
        emissivity=0.6,
        youngs_modulus_pa=1.14e+11,
        cte_per_k=8.6e-06,
        specular_strength=0.35,
        shininess=40.0,
        metallic=0.9,
        roughness=0.5,
        notes="Real Bell Model 8096/8247 XLR81 (Agena) nozzle-extension alloy "
              "(Engine_Configs/Agena_XLR81_Config.cfg header: Pc 3.48 MPa, eps 45, "
              "IRFNA/UDMH-USO, vac Isp 289.8-300 s). max_service_temp_k (700 K, 800F) "
              "cites [SP-8124 Sec.2.1/3.1]'s real structural-shell temperature limit for "
              "titanium - that source states it for an ablative structural overwrap, not "
              "a bare radiative bell specifically, but it is the best real anchor found "
              "and more defensible than a hand-picked figure. This is deliberately much "
              "lower than niobium_c103 (1650 K) or molybdenum_tzm (1950 K) - by design, "
              "since it is WHY a nozzle_liner_material_key='zirconia' liner (see "
              "EngineDesign) is load-bearing rather than decorative for this material: "
              "without one, titanium will typically fail/warn on thermal margin at real "
              "nozzle-extension conditions, which is correct 'warn don't block' behavior, "
              "not a bug. The real hardware's molybdenum reinforcement bands at the aft "
              "attach point are NOT modeled as a separate blended Material here (unlike "
              "refrasil_phenolic's genuinely homogeneous 3-layer liner, Mo reinforcement "
              "is localized structural banding, not a property blended through the whole "
              "shell thickness) - they are this tool's existing axisymmetric nozzle-"
              "extension stiffening-ring bumps (gui/mesh_builder.py), now attributable to "
              "this real material choice.",
    ),
}

# Every material's own default method must be one it allows (import-time check -
# a new material that forgets allowed_cooling_methods fails loudly here).
for _m in MATERIALS.values():
    assert _m.cooling_method in _m.allowed_cooling_methods, (_m.key, _m.cooling_method)
    assert _m.metallic is None or 0.0 <= _m.metallic <= 1.0, _m.key
    assert _m.roughness is None or 0.0 <= _m.roughness <= 1.0, _m.key


def available_materials():
    return list(MATERIALS.keys())


def thermal_margin(material_key, tc_k, heat_flux_factor=1.0, wall_temp_k=None):
    """
    Returns dict(assumed_wall_temp_k, max_service_temp_k, margin_ratio, warning)
    warning is None if margin_ratio >= 1.15, otherwise a human-readable string.

    wall_temp_k: when supplied (a real hot-gas-wall temperature computed by
    physics/cooling.py - Bartz h_g and the q = h_g*(T_aw - T_wg) balance, or the
    radiation-equilibrium solve for a radiatively-cooled extension), it is
    compared to the material's max service temperature DIRECTLY and
    heat_flux_factor is ignored. When None, falls back to the original coarse
    proxy: assumed wall temp = Tc * cooling_effectiveness * heat_flux_factor.

    heat_flux_factor (fallback path only): multiplies the assumed wall temp -
    the CHAMBER material check passes
    contraction_ratio_heat_flux_factor(design.contraction_ratio) here; every
    other caller (in particular the nozzle-extension/bell material check) leaves
    this at its default 1.0, since chamber contraction ratio doesn't affect the
    bell's local temperature.
    """
    mat = MATERIALS[material_key]
    if wall_temp_k is not None:
        assumed_wall_temp = wall_temp_k
        basis = "computed wall temp"
    else:
        assumed_wall_temp = tc_k * mat.cooling_effectiveness * heat_flux_factor
        basis = "assumed wall temp"
    margin_ratio = mat.max_service_temp_k / assumed_wall_temp if assumed_wall_temp > 0 else float("inf")
    warning = None
    if margin_ratio < 1.0:
        warning = (f"{mat.display_name}: {basis} {assumed_wall_temp:.0f} K EXCEEDS "
                   f"its {mat.max_service_temp_k:.0f} K max service temp (Tc {tc_k:.0f} K, "
                   f"{mat.cooling_method} cooling). Marginal/unsuitable as designed.")
    elif margin_ratio < THIN_MARGIN_THRESHOLD:
        warning = (f"{mat.display_name}: only {margin_ratio*100-100:.0f}% thermal margin "
                   f"({basis} {assumed_wall_temp:.0f} K vs {mat.max_service_temp_k:.0f} K "
                   f"max). Thin margin.")
    return {
        "assumed_wall_temp_k": assumed_wall_temp,
        "max_service_temp_k": mat.max_service_temp_k,
        "margin_ratio": margin_ratio,
        "warning": warning,
    }


def through_wall_delta_t_k(q_w_m2, thickness_m, k_w_mk):
    """Steady-state temperature drop through a wall of the given thickness
    carrying heat flux q by conduction: dT = q * t / k. First real use of a
    material's thermal_conductivity_w_mk - feeds the throat low-cycle
    thermal-fatigue estimate in physics/mass_model.py (the hot face runs this
    much hotter than the coolant-side face, and that gradient is what fatigues
    the wall over start/stop cycles)."""
    if k_w_mk <= 0 or thickness_m <= 0:
        return 0.0
    return q_w_m2 * thickness_m / k_w_mk
