"""
Curated REAL RP-1 tech-node names for the export tech-gating combobox -
fetched directly from RP-1's own tech tree source
(https://raw.githubusercontent.com/KSP-RO/RP-1/master/GameData/RP-1/Tree/TREE-Engines.cfg,
fetched 2026-09-05) rather than invented. Only chemical-liquid-engine-relevant
families are included - the real tree also has solids/nuclear/electric-
propulsion node families, but this tool only designs chemical liquid
bipropellant/monopropellant engines, so those are excluded entirely.

This is a SUGGESTION list for an EDITABLE combobox, not an enforced
enumeration - RP-1's tech tree can and does change between versions, and the
user's own install may differ; typing any node name they actually have is
expected and supported.

This project's own TR341_Config.cfg (a lunar-lander thruster) uses
"advancedUncrewedLanding" as its tech node - that name could NOT be
re-confirmed in this fetch of TREE-Engines.cfg (it may be from an older RP-1
version, or defined in a different tree file, e.g. one covering probe/lander
PARTS rather than engines). It is included below as a further suggestion,
same as before, but NOT presented as freshly verified, and TR341's own file
is not "corrected" - there's nothing here to confirm it's wrong.
"""

ORBITAL_ROCKETRY = [
    "orbitalRocketry1956", "orbitalRocketry1959", "orbitalRocketry1960",
    "orbitalRocketry1962", "orbitalRocketry1964", "orbitalRocketry1965",
    "orbitalRocketry1966", "orbitalRocketry1968", "orbitalRocketry1970",
    "orbitalRocketry1972", "orbitalRocketry1976", "orbitalRocketry1981",
    "orbitalRocketry1986", "orbitalRocketry1992", "orbitalRocketry2004",
    "orbitalRocketry2009", "orbitalRocketry2014", "orbitalRocketry2019",
]

HYDROLOX = [
    "earlyHydrolox", "hydrolox1969", "hydrolox1972", "hydrolox1976",
    "hydrolox1981", "hydrolox1986", "hydrolox1992", "hydrolox1998",
    "hydrolox2004", "hydrolox2009", "hydrolox2014", "hydrolox2019",
    "largeHydrolox", "improvedHydrolox",
]

STAGED_COMBUSTION = [
    "stagedCombustion1963", "stagedCombustion1966", "stagedCombustion1967",
    "stagedCombustion1969", "stagedCombustion1972", "stagedCombustion1981",
]

FRSC_FAMILY = [
    "prototypeFRSC", "FRSC1976", "FRSC1981", "FRSC1986", "FRSC1992",
    "FRSC1998", "FRSC2009", "FRSC2019",
]

# lunarLanding / improvedLandingEngines: verified in the fetched TREE-Engines.cfg.
# advancedUncrewedLanding: TR341's existing value, not re-confirmed (see module docstring).
LANDING = ["lunarLanding", "improvedLandingEngines", "advancedUncrewedLanding"]

FOUNDATIONAL = ["basicRocketryRP0", "earlyRocketry", "rocketryTesting", "unlockParts"]


def suggested_nodes(propellant_pair, cycle):
    """
    Contextually-ordered suggestion list for the tech-node combobox - most-
    relevant family first (LOX/LH2 -> hydrolox, an FRSC/ORSC cycle -> the
    FRSC family, a staged-combustion-flavored cycle or LOX/RP-1 -> the
    stagedCombustion family), but every family is always included since this
    only orders suggestions, it never restricts what can be typed.
    """
    from . import cycles

    staged = (cycles.FRSC, cycles.ORSC, cycles.FFSC)

    families = []
    # Electric pump-fed (Rutherford) is a modern development - lead with the
    # late orbital-rocketry nodes; it has no staged-combustion prerequisite.
    if cycle == cycles.ELECTRIC_PUMP:
        families.append(ORBITAL_ROCKETRY[::-1])
    if propellant_pair == "LOX/LH2":
        families.append(HYDROLOX)
    if cycle in staged:
        families.append(FRSC_FAMILY)
    if cycle in staged or propellant_pair == "LOX/RP-1":
        families.append(STAGED_COMBUSTION)
    families.append(ORBITAL_ROCKETRY)
    families.append(LANDING)
    families.append(FOUNDATIONAL)

    seen = set()
    ordered = []
    for family in families:
        for node in family:
            if node not in seen:
                seen.add(node)
                ordered.append(node)
    return ordered
