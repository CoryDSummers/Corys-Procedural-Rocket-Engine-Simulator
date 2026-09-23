"""Cooling method as an explicit per-section design choice + the material x method hard block.

Part of the physics/cooling/ package (split verbatim out of the former
single-file cooling.py - see cooling/__init__.py for the package overview)."""

# --- cooling method as an explicit per-section design choice -----------------
# The chamber and the nozzle/bell each get their own cooling method. Until now
# the method was inferred from the chosen material (materials.Material.
# cooling_method - one value per material); an EngineDesign field of "auto" keeps
# exactly that, an explicit value overrides it - but ONLY within the material's
# allowed_cooling_methods (resolve_cooling_method_checked below).
#
# "film" is NOT a section method (it was until 2026-09-23): fuel-film cooling is
# an OVERLAY on top of whichever method a section uses - the chamber curtain
# (EngineDesign.film_cooling_fraction, film_effectiveness_profile) and the
# nozzle-extension slot (EngineDesign.nozzle_film_fraction,
# nozzle_film_effectiveness_profile) - so regen + film, ablative + film,
# radiative extension + slot film all combine in the flux / T_aw math. A
# film-cooled-only wall is "uncooled" + the overlay.
COOLING_METHODS = ("regenerative", "dump", "radiative", "ablative", "uncooled")


def resolve_cooling_method(explicit, material_default):
    """The cooling method requested for a section: `material_default` (the
    material's own cooling_method) when `explicit` is "" / "auto" / None,
    otherwise `explicit`. No compatibility check - see
    resolve_cooling_method_checked, which design.py uses."""
    if not explicit or explicit == "auto":
        return material_default
    return explicit


def resolve_cooling_method_checked(explicit, material):
    """
    The cooling method actually in effect for a section built from `material`
    (a materials.Material), HARD-BLOCKING physically meaningless choices.

    Returns (method, rejected): `rejected` is None when the request was honoured
    ("auto", or an explicit method in material.allowed_cooling_methods), else
    the rejected explicit name - in which case `method` falls back to the
    material's own cooling_method. Unknown / retired names (e.g. the pre-overlay
    "film") are rejected the same way. The caller surfaces a rejection as a
    failing checklist row; old project files are never rewritten.
    """
    requested = resolve_cooling_method(explicit, material.cooling_method)
    allowed = material.allowed_cooling_methods or (material.cooling_method,)
    if requested in allowed and requested in COOLING_METHODS:
        return requested, None
    return material.cooling_method, requested
