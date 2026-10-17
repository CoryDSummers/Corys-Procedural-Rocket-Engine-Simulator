"""Host-model catalog: the "pick a known RO part to bind onto" data source.

- catalog.json            - header spec-table per #engineType (build_catalog.py)
- roengines_models.json    - rendered model height per #engineType, for export
                             model-scaling, plus each part's B9PartSwitch model
                             variants and alternate parts (build_roengines_models.py)
- rp1_snapshot.json        - RP-1 tech nodes, engine part / config costs and ECM
                             entry-cost rows (build_rp1_snapshot.py)
"""
import json
from pathlib import Path

_DIR = Path(__file__).resolve().parent
CATALOG_PATH = _DIR / "catalog.json"
ROENGINES_MODELS_PATH = _DIR / "roengines_models.json"
_CACHE = {}    # the snapshot is read-only reference data - load it once per process


def load_catalog():
    """The full list of catalog entries (or [] if unreadable)."""
    try:
        return json.loads(CATALOG_PATH.read_text())
    except Exception:
        return []


def load_roengines_models():
    """{engine_type: model-dimension entry} from the ROEngines snapshot.

    Entry keys: native_height_m, native_max_dia_m, node_stack_top_m,
    node_stack_bottom_m, rescale_factor, model, part_name, source_file.
    Empty dict if the snapshot is missing/unreadable - callers then fall back
    to a user-entered reference height. Cached: treat the result as read-only.
    """
    if "models" not in _CACHE:
        try:
            data = json.loads(ROENGINES_MODELS_PATH.read_text())
            _CACHE["models"] = {e["engine_type"]: e for e in data.get("models", [])}
        except Exception:
            _CACHE["models"] = {}
    return _CACHE["models"]


def host_model_parts(engine_type, models=None):
    """Every ROEngines part carrying `engine_type`, snapshot default first:
    [{part_name, native_height_m, variants, source_file, ...}]. Several parts can
    share one engineType (e.g. ROE-LR105 / ROE-LR105_2) - each is its own model."""
    models = load_roengines_models() if models is None else models
    e = models.get(engine_type)
    if not e:
        return []
    return [e] + list(e.get("alt_parts", []))


def host_model_part(engine_type, part_name="", models=None):
    """The chosen part entry (by name), else the snapshot default, else None."""
    parts = host_model_parts(engine_type, models)
    for p in parts:
        if part_name and p.get("part_name") == part_name:
            return p
    return parts[0] if parts else None


def host_native_height_m(engine_type, part_name="", variants=None, manual_m=0.0, models=None):
    """(height_m or None, source, note) for model scaling.

    Order: the user's manual override; else the chosen variant's height when a
    selected subtype moves a stack node; else the part's own height (note says
    when a selected variant only toggles meshes, so its length is unknown)."""
    if manual_m and manual_m > 0:
        return float(manual_m), "manual", ""
    part = host_model_part(engine_type, part_name, models)
    if not part or not part.get("native_height_m"):
        return None, "", ""
    variants = variants or {}
    note = ""
    for sw in part.get("variants", []):
        pick = variants.get(sw["module_id"])
        st = next((s for s in sw["subtypes"] if s["name"] == pick), None)
        if st is None:
            continue
        if not st["height_from_part"]:
            return float(st["native_height_m"]), f"ROEngines variant {sw['module_id']}={pick}", ""
        if st is sw["subtypes"][0]:
            continue        # B9PS's default subtype: the part's own nodes describe it
        note = (f"variant {sw['module_id']}={pick} only swaps meshes - its length isn't in the "
                f"part file; set the reference height by hand if it differs")
    return float(part["native_height_m"]), "ROEngines", note
