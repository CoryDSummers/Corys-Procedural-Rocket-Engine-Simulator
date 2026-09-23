"""
One-time scraper: regex-parses Engine_Configs/*.cfg header spec-tables into
catalog.json - the "choose a known RO model to bind onto" data source for
the GUI's host-model dropdown.

RO engine parts are individually modeled (confirmed: 315 distinct
#engineType tags across 316 config files, no generic reskinnable part), so
one file == one #engineType == one physical model/part, even when a file's
header documents several historical thrust variants (they're all CONFIGs
on the same modeled part - see H1_Config.cfg / RD100_Config.cfg). This
scraper captures the FIRST header spec-block per file as a representative
size/class indicator for that model - not authoritative, just enough to
pick a visually-plausible host.

Run via:  python3 -m engine_designer.catalog.build_catalog   (from /home/cory/ksp_config)
"""
import json
import re
from pathlib import Path

ENGINE_CONFIGS_DIR = Path(__file__).resolve().parents[2] / "Engine_Configs"
OUTPUT_PATH = Path(__file__).resolve().parent / "catalog.json"

ENGINE_TYPE_RE = re.compile(r"#engineType\[([A-Za-z0-9_.\-]+)\]")
MANUFACTURER_RE = re.compile(r"//\s*Manufacturer:\s*(.+)")
TITLE_RE = re.compile(r"^//\s*([A-Za-z0-9][^\n]*?)\s*$")
SEPARATOR_RE = re.compile(r"^//\s*=+\s*$")

FIELD_PATTERNS = {
    "dry_mass": re.compile(r"//\s*Dry Mass:\s*([\d.]+)"),
    "thrust_sl_kn": re.compile(r"//\s*Thrust \(SL\):\s*([\d.]+)"),
    "thrust_vac_kn": re.compile(r"//\s*Thrust \(Vac\):\s*([\d.]+)"),
    "isp_sl_s": re.compile(r"//\s*ISP:\s*([\d.]+)\s*SL"),
    "isp_vac_s": re.compile(r"//\s*ISP:.*?/\s*([\d.]+)\s*Vac"),
    "chamber_pressure_mpa": re.compile(r"//\s*Chamber Pressure:\s*([\d.]+)"),
    "propellant": re.compile(r"//\s*Propellant:\s*(.+)"),
    "nozzle_ratio": re.compile(r"//\s*Nozzle Ratio:\s*([\d.]+)"),
    "throttle": re.compile(r"//\s*Throttle:\s*(.+)"),
}


def _first_header_block(text):
    """Text up to the first @PART patch - covers every documented variant,
    but we only pull the FIRST match of each field (the first/earliest variant)."""
    idx = text.find("@PART[")
    return text[:idx] if idx != -1 else text


def _extract_title(header_text):
    """First non-separator, non-'Manufacturer' comment line after the top banner."""
    lines = header_text.splitlines()
    seen_separator = False
    for line in lines:
        if SEPARATOR_RE.match(line):
            seen_separator = True
            continue
        m = TITLE_RE.match(line)
        if not m:
            continue
        candidate = m.group(1).strip()
        if candidate.lower().startswith("manufacturer:"):
            continue
        if seen_separator or candidate:
            return candidate
    return None


def parse_file(path):
    text = path.read_text(errors="replace")
    engine_type_match = ENGINE_TYPE_RE.search(text)
    if not engine_type_match:
        return None
    engine_type = engine_type_match.group(1)

    header = _first_header_block(text)
    manufacturer_match = MANUFACTURER_RE.search(header)
    manufacturer = manufacturer_match.group(1).strip() if manufacturer_match else None
    title = _extract_title(header)

    entry = {
        "engine_type": engine_type,
        "title": title,
        "manufacturer": manufacturer,
        "source_file": path.name,
    }
    for key, pattern in FIELD_PATTERNS.items():
        m = pattern.search(header)
        entry[key] = m.group(1).strip() if m else None
    return entry


def build():
    if not ENGINE_CONFIGS_DIR.is_dir():
        raise SystemExit(f"Engine_Configs directory not found at {ENGINE_CONFIGS_DIR}")

    entries = []
    for path in sorted(ENGINE_CONFIGS_DIR.glob("*.cfg")):
        try:
            entry = parse_file(path)
        except Exception as exc:  # keep the scraper best-effort, never fatal on one bad file
            entry = None
            print(f"  [skip] {path.name}: {exc}")
        if entry:
            entries.append(entry)

    OUTPUT_PATH.write_text(json.dumps(entries, indent=2))
    print(f"Wrote {len(entries)} entries to {OUTPUT_PATH}")
    return entries


if __name__ == "__main__":
    build()
