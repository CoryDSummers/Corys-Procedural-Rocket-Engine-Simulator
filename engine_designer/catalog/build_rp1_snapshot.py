"""
Scraper for the RP-1 career data the exporter needs - a committed snapshot,
like roengines_models.json:

  tech_nodes    every RP0TechTree.cfg RDNode: id, title, start year (from the
                node's own "(1972-1980)" description), parent ids. Feeds the
                GUI's tech-node combobox labels (`id - title`) and the era of a
                design / an RO config (physics/reliability.py).
  engine_parts  RP-1's own TREE-Parts.cfg placement of every ENGINE part
                (tagged EngineLiquidTurbo / EngineLiquidPF / EngineSolid):
                TechRequired, cost, entryCost, tags.
  engine_types  #engineType -> the part names that carry it (ROEngines
                PartConfigs `PART {}` + RealismOverhaul's own `@PART[...] {
                %engineType = X }` patches) - the join from an RO engine config
                to the part whose RP-1 cost it rides on.
  configs       every RealFuels CONFIG in Engine_Configs/ (RO): engineType,
                maxThrust, pressureFed, propellants, mass (origMass x massMult),
                plus RP-1's TREE-Engines.cfg techRequired / cost DELTA and its
                ECM-Engines.cfg entry-cost row (cost + tech-transfer parents).

How RP-1 prices an engine (verified against RealFuels' source, see
engine_designer/README.md "Export"): the PART carries the base `cost`; each
CONFIG's `cost` is a DELTA on top of it; a CONFIG's entry cost comes ONLY from
an ENTRYCOSTMODS row keyed by the config name (a CONFIG-level `entryCost` is
never read). physics/cost_model.py fits its absolute engine-cost estimate to
`part cost + config delta` over these rows.

Auto-detects `upstream/RP-1` (see UPSTREAM_REPOS.md) or $RP1_DIR; the RO
configs come from the project's own read-only `Engine_Configs/` copy, the
ROEngines parts from `upstream/ROEngines` (or $ROENGINES_DIR). With RP-1 absent
it re-validates the existing snapshot.

    python3 -m engine_designer.catalog.build_rp1_snapshot

RP-1 is CC BY-NC-SA 4.0 and ROEngines CC BY-NC-ND 4.0: only identifiers and
derived numbers are stored here, never verbatim config text.
"""
import json
import os
import re
import subprocess
from pathlib import Path

from . import mmcfg

OUTPUT_PATH = Path(__file__).resolve().parent / "rp1_snapshot.json"
_REPO_ROOT = Path(__file__).resolve().parents[2]
ENGINE_CONFIGS_DIR = _REPO_ROOT / "Engine_Configs"
ENGINE_TAGS = ("EngineLiquidTurbo", "EngineLiquidPF", "EngineSolid")


def _find_dir(env_var, *rel_candidates):
    env = os.environ.get(env_var)
    cands = [Path(env)] if env else []
    cands += [_REPO_ROOT / "upstream" / r for r in rel_candidates]
    cands += [_REPO_ROOT.parent / r for r in rel_candidates]
    for c in cands:
        if c.is_dir():
            return c
    return None


def _git_commit(path):
    try:
        return subprocess.check_output(["git", "-C", str(path), "rev-parse", "--short", "HEAD"],
                                       text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"


# --- RP-1 tree files -----------------------------------------------------------

def parse_tech_nodes(path):
    nodes = []
    for top in mmcfg.parse_file(path):
        for n in top.walk():
            if n.type_name == "RDNode" and n.get("id"):
                nodes.append({"id": n.get("id"), "title": n.get("title", ""),
                              "year": _node_year(n.get("description", ""), n.get("title", "")),
                              "parents": [p.get("parentID") for p in n.find("Parent")
                                          if p.get("parentID")]})
    return nodes


def _node_year(description, title):
    """First 4-digit year in the node's description ("... (1972-1980)") or title
    ("1976-1980 Orbital Rocketry"); None for undated nodes (start, unlockParts)."""
    for text in (description or "", title or ""):
        m = re.search(r"\b(19[0-9]{2}|2[01][0-9]{2})\b", text)
        if m:
            return int(m.group(1))
    return None


def parse_tree_parts(path):
    """{part_name: {tech, cost, entry_cost, rp0conf, tags}} for parts whose
    TREE-Parts entry carries an engine tag."""
    out = {}
    for top in mmcfg.parse_file(path):
        if top.type_name != "PART" or not top.selector:
            continue
        tags = []
        for c in top.find("MODULE"):
            if c.selector == "ModuleTagList" or c.get("name") == "ModuleTagList":
                tags += c.get_all("tag")
        if not any(t in ENGINE_TAGS for t in tags):
            continue
        out[top.selector] = {
            "tech": top.get("TechRequired"),
            "cost": mmcfg.first_number(top.get("cost")),
            "entry_cost": mmcfg.first_number(top.get("entryCost")),
            "rp0conf": (top.get("RP0conf") or "").lower() == "true",
            "tags": sorted(set(tags)),
        }
    return out


def parse_tree_engines(path):
    """{config_name: {tech, cost_delta, tags}} from TREE-Engines' @CONFIG[...] edits."""
    out = {}
    for top in mmcfg.parse_file(path):
        # Only the tree-placement patch (`@PART[*]:HAS[@MODULE[...]]`); the later
        # `@PART[RFUpgrade_engineConfigSource_X]` icon-source parts re-list each
        # CONFIG without tech/cost and must not overwrite it.
        if top.type_name != "PART" or top.selector != "*":
            continue
        for n in top.walk():
            if n.type_name == "CONFIG" and n.selector and n.selector not in out:
                out[n.selector] = {
                    "tech": n.get("techRequired"),
                    "cost_delta": mmcfg.first_number(n.get("cost")),
                    "tags": n.get_all("tag"),
                }
    return out


def parse_ecm(path):
    """{name: {cost, parents}} from ENTRYCOSTMODS rows `NAME = [cost,] parent, ...`.
    A row with no leading number is a pure alias (`30x-NK-15 = NK-15`): cost None."""
    out = {}
    for top in mmcfg.parse_file(path):
        if top.type_name != "ENTRYCOSTMODS":
            continue
        for k, v in top.values:
            toks = [t.strip() for t in v.split(",") if t.strip()]
            cost = mmcfg.first_number(toks[0]) if toks else None
            if cost is not None and toks and toks[0].replace(".", "", 1).isdigit():
                toks = toks[1:]
            else:
                cost = None
            out[k.lstrip("%@")] = {"cost": cost, "parents": toks}
    return out


# --- engineType -> part names ---------------------------------------------------

def _part_names_from_selector(sel):
    return [s for s in (sel or "").split("|") if s and "*" not in s and "?" not in s]


def collect_engine_types(roengines_partconfigs, ro_gamedata):
    """{engineType: sorted part names}."""
    by_type = {}

    def add(et, names):
        for nm in names:
            by_type.setdefault(et, set()).add(nm)

    if roengines_partconfigs:
        for p in sorted(roengines_partconfigs.glob("*.cfg")):
            for top in mmcfg.parse_file(p):
                if top.header == "PART" and top.get("engineType") and top.get("name"):
                    add(top.get("engineType"), [top.get("name")])
    if ro_gamedata:
        for p in sorted(ro_gamedata.rglob("*.cfg")):
            if "Engine_Configs" in p.parts:
                continue
            for top in mmcfg.parse_file(p):
                if top.type_name == "PART" and top.op == "@" and top.get("engineType"):
                    add(top.get("engineType"), _part_names_from_selector(top.selector))
    return {k: sorted(v) for k, v in sorted(by_type.items())}


# --- RO engine configs ------------------------------------------------------------

def _engine_type_of(header):
    i = header.find("#engineType[")
    if i < 0:
        return None
    j = header.find("]", i)
    return header[i + len("#engineType["):j] if j > i else None


def parse_engine_configs(cfg_dir):
    """{config_name: {engine_type, max_thrust_kn, pressure_fed, propellants, mass_t,
    source_file}} for every top-level RealFuels CONFIG (SUBCONFIGs skipped)."""
    out = {}
    for p in sorted(cfg_dir.glob("*_Config.cfg")):
        for top in mmcfg.parse_file(p):
            if top.type_name != "PART":
                continue
            et = _engine_type_of(top.header)
            for mod in top.find("MODULE"):
                if "EngineConfigs" not in (mod.get("name") or mod.selector or ""):
                    continue
                orig_mass = mmcfg.first_number(mod.get("origMass"))
                for c in mod.find("CONFIG"):
                    name = c.get("name")
                    if not name:
                        continue
                    mult = mmcfg.first_number(c.get("massMult"), 1.0)
                    out[name] = {
                        "engine_type": et,
                        "max_thrust_kn": mmcfg.first_number(c.get("maxThrust")),
                        "pressure_fed": (c.get("pressureFed") or "").lower() == "true",
                        "propellants": [pp.get("name") for pp in c.find("PROPELLANT")
                                        if pp.get("name")],
                        "mass_t": (round(orig_mass * mult, 5) if orig_mass else None),
                        "source_file": p.name,
                    }
    return out


# --- build / validate -------------------------------------------------------------

def build():
    rp1 = _find_dir("RP1_DIR", "RP-1")
    if rp1 is None or not ENGINE_CONFIGS_DIR.is_dir():
        return _report_existing()
    tree = rp1 / "GameData/RP-1/Tree"
    roe = _find_dir("ROENGINES_DIR", "ROEngines")
    roe_pc = roe / "GameData/ROEngines/PartConfigs" if roe else None
    ro = _find_dir("RO_DIR", "RealismOverhaul")
    ro_gd = ro / "GameData/RealismOverhaul" if ro else None

    tech_nodes = parse_tech_nodes(tree / "RP0TechTree.cfg")
    parts = parse_tree_parts(tree / "TREE-Parts.cfg")
    tree_eng = parse_tree_engines(tree / "TREE-Engines.cfg")
    ecm = parse_ecm(tree / "ECM-Engines.cfg")
    engine_types = collect_engine_types(roe_pc if roe_pc and roe_pc.is_dir() else None, ro_gd)
    ro_cfgs = parse_engine_configs(ENGINE_CONFIGS_DIR)

    configs = {}
    for name, c in ro_cfgs.items():
        t = tree_eng.get(name, {})
        e = ecm.get(name, {})
        configs[name] = dict(c, tech=t.get("tech"), cost_delta=t.get("cost_delta"),
                             ecm_cost=e.get("cost"), ecm_parents=e.get("parents", []))
    # Only keep part names RP-1 actually prices, to keep the snapshot small.
    engine_types = {et: [n for n in names if n in parts] or names
                    for et, names in engine_types.items()}
    referenced = {n for names in engine_types.values() for n in names}
    parts = {n: v for n, v in parts.items() if n in referenced}
    payload = {
        "_source": "https://github.com/KSP-RO/RP-1 (GameData/RP-1/Tree) + RealismOverhaul "
                   "Engine_Configs + ROEngines PartConfigs",
        "_commit": {"RP-1": _git_commit(rp1), "ROEngines": _git_commit(roe) if roe else None,
                    "RealismOverhaul": _git_commit(ro) if ro else None},
        "tech_nodes": tech_nodes,
        "engine_parts": dict(sorted(parts.items())),
        "engine_types": engine_types,
        "configs": dict(sorted(configs.items())),
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=0, separators=(",", ":")) + "\n")
    print(f"Wrote {OUTPUT_PATH.name}: {len(tech_nodes)} tech nodes, {len(parts)} engine parts, "
          f"{len(engine_types)} engineTypes, {len(configs)} configs "
          f"(RP-1 @ {payload['_commit']['RP-1']})")
    return _validate(payload)


def _report_existing():
    if not OUTPUT_PATH.is_file():
        print("No RP-1 checkout found and no rp1_snapshot.json present - set RP1_DIR.")
        return None
    data = json.loads(OUTPUT_PATH.read_text())
    print(f"No RP-1 checkout found; validating existing {OUTPUT_PATH.name} "
          f"(RP-1 @ {data.get('_commit', {}).get('RP-1', '?')}).")
    return _validate(data)


def _validate(data):
    ids = {n["id"]: n for n in data["tech_nodes"]}
    assert len(ids) > 200, len(ids)
    assert ids["orbitalRocketry1976"]["title"] == "1976-1980 Orbital Rocketry", ids["orbitalRocketry1976"]
    assert ids["orbitalRocketry1976"].get("year") == 1976, ids["orbitalRocketry1976"]
    assert ids["start"].get("year") is None
    assert sum(1 for n in ids.values() if n.get("year")) > 250
    parts = data["engine_parts"]
    assert parts["ROE-AJ10-transtar"]["cost"] == 138, parts.get("ROE-AJ10-transtar")
    assert parts["ROE-AJ10-transtar"]["tags"] == ["EngineLiquidTurbo"]
    assert parts["RO-H1-RS27"]["cost"] == 392, parts.get("RO-H1-RS27")
    assert "ROE-AJ10-transtar" in data["engine_types"]["AJ10_Transtar"]
    cfgs = data["configs"]
    h1 = cfgs["H-1-200K"]
    assert h1["engine_type"] == "H1" and h1["cost_delta"] == 21, h1
    assert h1["max_thrust_kn"] and h1["max_thrust_kn"] > 800, h1
    assert cfgs["AJ10-153"]["cost_delta"] == -62, cfgs["AJ10-153"]
    assert cfgs["AJ10-118"]["ecm_cost"] == 1000 and cfgs["AJ10-118"]["ecm_parents"] == ["AJ10-142"]
    assert not cfgs["H-1-200K"]["pressure_fed"] and cfgs["AJ10-118"]["pressure_fed"]
    # Join coverage: how many RO configs land on an RP-1-priced part.
    priced = sum(1 for c in cfgs.values()
                 if any(n in parts for n in data["engine_types"].get(c["engine_type"], [])))
    print(f"  {len(ids)} tech nodes, {len(parts)} engine parts, {len(cfgs)} RO configs, "
          f"{priced} joinable to an RP-1 part cost")
    assert priced > 300, priced
    print("rp1_snapshot: OK")
    return data


# --- read helpers (used by physics/cost_model, physics/tech_tree, export, GUI) ------

_CACHE = {}


def load():
    """The snapshot dict, or {} if missing/unreadable."""
    if "d" not in _CACHE:
        try:
            _CACHE["d"] = json.loads(OUTPUT_PATH.read_text())
        except Exception:
            _CACHE["d"] = {}
    return _CACHE["d"]


def tech_node_titles():
    """{node id: title} (empty if no snapshot)."""
    return {n["id"]: n.get("title", "") for n in load().get("tech_nodes", [])}


def tech_node_year(node_id):
    """Start year of an RP-1 tech node, or None (unknown / undated / no snapshot)."""
    for n in load().get("tech_nodes", []):
        if n["id"] == node_id:
            return n.get("year")
    return None


def host_part_names(engine_type):
    return list(load().get("engine_types", {}).get(engine_type, []))


def host_part_cost(engine_type):
    """Median RP-1 TREE-Parts cost over the parts carrying `engine_type`, or None."""
    parts = load().get("engine_parts", {})
    costs = sorted(parts[n]["cost"] for n in host_part_names(engine_type)
                   if n in parts and parts[n].get("cost") is not None)
    return costs[len(costs) // 2] if costs else None


if __name__ == "__main__":
    build()
