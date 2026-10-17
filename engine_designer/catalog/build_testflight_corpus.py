"""
Scraper for RealismOverhaul's real TestFlight numbers - a committed snapshot
(`testflight_corpus.json`) that physics/reliability.py fits its exported
ratedBurnTime / testedBurnTime / reliability values against.

One row per RealFuels CONFIG in the project's read-only `Engine_Configs/` copy
that carries a `TESTFLIGHT { ratedBurnTime }` block:

  rated_s, tested_s       ratedBurnTime / testedBurnTime (tested None if absent)
  ign_start/end,          ignitionReliabilityStart/End,
  cyc_start/end           cycleReliabilityStart/End
  ignitions               CONFIG ignitions (RF: <= 0 = unlimited)
  thrust_kn, isp_vac,     maxThrust, atmosphereCurve keys 0 / 1 (sea-level Isp
  isp_sl                  None when the curve has no key at 1 atm)
  pressure_fed            CONFIG pressureFed
  biprop                  a liquid oxidiser + a second propellant, no solid grain
  family                  "orsc" / "frsc" / "expander" from the config FILE (the
                          only place RO records the cycle - see FAMILY_FILES),
                          "pf" for a pressure-fed config, else "pump"
  year                    start year of the RP-1 tech node the config is gated
                          at (catalog/rp1_snapshot.json), None if ungated
  tech_transfer           the TESTFLIGHT techTransfer string, if any

What RO's TestFlight does with these (TestFlight_Generic_Engines.cfg in
upstream/RealismOverhaul): per-second failure chance = (1 - cycleReliability) /
ratedBurnTime; the `cycle` curve is 1x until rated + 5 s, 2x (the default
overburnPenalty) at testedBurnTime and 100x at 2.5 x testedBurnTime - so
testedBurnTime is the longest SINGLE burn the engine was demonstrated for, not a
cumulative qualification time.

    python3 -m engine_designer.catalog.build_testflight_corpus

RealismOverhaul is CC-BY-SA: only identifiers and numbers are stored here.
"""
import json
from pathlib import Path

from . import build_rp1_snapshot, mmcfg

OUTPUT_PATH = Path(__file__).resolve().parent / "testflight_corpus.json"
ENGINE_CONFIGS_DIR = build_rp1_snapshot.ENGINE_CONFIGS_DIR

OXIDISERS = {"LqdOxygen", "CooledLqdOxygen", "NTO", "MON1", "MON3", "MON10", "MON25",
             "IRFNA-III", "IRFNA-IV", "IWFNA", "AK20", "AK27", "LqdFluorine", "HTP"}
SOLID_GRAINS = {"HTPB", "PBAN", "CTPB", "PSPC", "NGNC", "PUPE", "PBAA"}

# Cycle family by RO config FILE stem (RO's configs carry no cycle field). Only
# families with enough real rows to fit are listed; everything else pump-fed is
# "pump" (mostly gas-generator) - the reference group.
FAMILY_FILES = {
    "orsc": ("RD180", "RD170", "RD191", "RD120", "RD253", "NK33", "RD8", "RD58", "RD0124",
             "RD864", "RD805", "S5_98M"),
    "frsc": ("SSME", "SSME650", "RD0120", "LE7"),
    "expander": ("RL10", "LE5B", "RD0146", "Vinci"),
}


def _family(stem, pressure_fed):
    up = stem.upper()
    for fam, stems in FAMILY_FILES.items():
        if any(up == s.upper() or up.startswith(s.upper()) for s in stems):
            return fam
    return "pf" if pressure_fed else "pump"


def _isp_keys(config):
    vac = sl = None
    for curve in config.find("atmosphereCurve"):
        for v in curve.get_all("key"):
            parts = v.split()
            if len(parts) < 2:
                continue
            try:
                p, isp = float(parts[0]), float(parts[1])
            except ValueError:
                continue
            if p == 0.0 and vac is None:
                vac = isp
            elif p == 1.0 and sl is None:
                sl = isp
    return vac, sl


def _int_or_none(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def build_rows(cfg_dir=ENGINE_CONFIGS_DIR, snapshot=None):
    snapshot = build_rp1_snapshot.load() if snapshot is None else snapshot
    years = {n["id"]: n.get("year") for n in snapshot.get("tech_nodes", [])}
    techs = {k: v.get("tech") for k, v in snapshot.get("configs", {}).items()}
    rows = []
    for p in sorted(Path(cfg_dir).glob("*_Config.cfg")):
        stem = p.name[:-len("_Config.cfg")]
        for top in mmcfg.parse_file(p):
            if top.type_name != "PART":
                continue
            for mod in top.find("MODULE"):
                if "EngineConfigs" not in (mod.get("name") or mod.selector or ""):
                    continue
                for c in mod.find("CONFIG"):
                    tfs = list(c.find("TESTFLIGHT"))
                    if not tfs or not c.get("name"):
                        continue
                    tf = tfs[0]
                    rated = mmcfg.first_number(tf.get("ratedBurnTime"))
                    if not rated or rated <= 0:
                        continue
                    props = [pp.get("name") for pp in c.find("PROPELLANT") if pp.get("name")]
                    pf = (c.get("pressureFed") or "").lower() == "true"
                    vac, sl = _isp_keys(c)
                    pset = set(props)
                    rows.append({
                        "name": c.get("name"), "file": p.name,
                        "rated_s": rated,
                        "tested_s": mmcfg.first_number(tf.get("testedBurnTime")),
                        "ign_start": mmcfg.first_number(tf.get("ignitionReliabilityStart")),
                        "ign_end": mmcfg.first_number(tf.get("ignitionReliabilityEnd")),
                        "cyc_start": mmcfg.first_number(tf.get("cycleReliabilityStart")),
                        "cyc_end": mmcfg.first_number(tf.get("cycleReliabilityEnd")),
                        "ignitions": _int_or_none(c.get("ignitions")),
                        "thrust_kn": mmcfg.first_number(c.get("maxThrust")),
                        "isp_vac": vac, "isp_sl": sl,
                        "pressure_fed": pf,
                        "biprop": bool(len(pset) >= 2 and pset & OXIDISERS
                                       and not pset & SOLID_GRAINS),
                        "family": _family(stem, pf),
                        "year": years.get(techs.get(c.get("name"))),
                        "tech_transfer": tf.get("techTransfer") or None,
                    })
    return rows


def build():
    if not ENGINE_CONFIGS_DIR.is_dir():
        return _report_existing()
    rows = build_rows()
    payload = {"_source": "RealismOverhaul Engine_Configs (TESTFLIGHT blocks) + "
                          "catalog/rp1_snapshot.json tech-node years",
               "rows": rows}
    OUTPUT_PATH.write_text(json.dumps(payload, indent=0, separators=(",", ":")) + "\n")
    print(f"Wrote {OUTPUT_PATH.name}: {len(rows)} TESTFLIGHT configs")
    return _validate(payload)


def _report_existing():
    if not OUTPUT_PATH.is_file():
        print("No Engine_Configs/ and no testflight_corpus.json present.")
        return None
    return _validate(json.loads(OUTPUT_PATH.read_text()))


def _validate(data):
    rows = {r["name"]: r for r in data["rows"]}
    f1 = rows["F-1-1.5M"]
    assert f1["rated_s"] == 165 and f1["tested_s"] == 2250, f1
    assert f1["biprop"] and f1["family"] == "pump" and not f1["pressure_fed"], f1
    assert rows["H-1-200K"]["rated_s"] == 155, rows["H-1-200K"]
    assert rows["RL10A-3-3"]["family"] == "expander", rows["RL10A-3-3"]
    assert rows["RD-180"]["family"] == "orsc" and rows["RD-180"]["tested_s"] == 1590
    assert rows["AJ10-104"]["pressure_fed"] and rows["AJ10-104"]["family"] == "pf"
    assert f1["year"] == 1967, f1["year"]
    bip = [r for r in data["rows"] if r["biprop"]]
    with_tested = [r for r in bip if r["tested_s"]]
    dated = [r for r in bip if r["year"]]
    print(f"  {len(data['rows'])} configs, {len(bip)} liquid biprop, "
          f"{len(with_tested)} with testedBurnTime, {len(dated)} dated by RP-1 node")
    assert len(bip) > 500 and len(with_tested) > 400 and len(dated) > 450
    print("testflight_corpus: OK")
    return data


_CACHE = {}


def load_rows():
    """The corpus rows ([] if the snapshot is missing)."""
    if "rows" not in _CACHE:
        try:
            _CACHE["rows"] = json.loads(OUTPUT_PATH.read_text())["rows"]
        except Exception:
            _CACHE["rows"] = []
    return _CACHE["rows"]


if __name__ == "__main__":
    build()
