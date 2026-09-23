"""Host-model catalog: the "pick a known RO part to bind onto" data source.

- catalog.json            - header spec-table per #engineType (build_catalog.py)
- roengines_models.json    - rendered model height per #engineType, for export
                             model-scaling (build_roengines_models.py)
"""
import json
from pathlib import Path

_DIR = Path(__file__).resolve().parent
CATALOG_PATH = _DIR / "catalog.json"
ROENGINES_MODELS_PATH = _DIR / "roengines_models.json"


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
    to a user-entered reference height.
    """
    try:
        data = json.loads(ROENGINES_MODELS_PATH.read_text())
        return {e["engine_type"]: e for e in data.get("models", [])}
    except Exception:
        return {}
