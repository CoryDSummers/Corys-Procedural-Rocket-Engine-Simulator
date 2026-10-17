"""
Scraper for ROEngines' PLUME placements - the data export/plume.py needs to give an
exported engine a plume.

Why this exists (2026-10-16): ROEngines attaches every plume BY PART NAME, in a
ModuleManager pass after the one our standalone clone is made in:

    @PART[ROE-AJ10-transtar]:BEFORE[ROWaterfall]:NEEDS[Waterfall]   (Waterfall/<Prop>/*.cfg)
    { ROWaterfall { template = ...  position = ...  scale = ...  glow = ... } }
    @PART[ROE-AJ10-transtar]:BEFORE[RealPlume]:NEEDS[!Waterfall]    (RealPlume/*.cfg)
    { PLUME { name = ... } @MODULE[ModuleEngineConfigs] { @CONFIG,* { %powerEffectName = ... } } }

A `+PART[ROE-AJ10-transtar]` copy renamed to `BellModel8760` is never matched, so
it flew with no plume. RO's processor (RealismOverhaul/Waterfall_Configs/
_Processor/) turns ANY `@PART[*]:HAS[@ROWaterfall]` into a ModuleWaterfallFX from
:FOR[ROWaterfall] on - so the exporter only has to write the node itself.

Per ROEngines part this records:
  * `waterfall`  - the ROWaterfall node (values + ExtraTemplate / MainPlumeVariant
                   children), the propellant folder it sits in, and how many OTHER
                   plume patches target the part (not copied - see export/plume.py);
  * `realplume`  - the PLUME nodes + the default powerEffectName;
  * `rescale_factor` and the RF propellants of the part's DEFAULT RO config
                   (Engine_Configs/ joined on engineType via catalog.json).

Derived tables (RO's own choices, nothing hand-picked):
  * `template_by_propellants[fuel+ox][lower|upper|any]` - the template ROEngines uses
    most for real engines burning that pair (MONx -> NTO, Cooled* -> base, as RO's
    own autoConfig treats them), with the glow most used alongside it;
  * `audio_bands` - pump-fed audio class vs the real vacuum thrust (median per class,
    boundaries at the geometric mean between neighbours);
  * `template_scale_per_m` - plume `scale` (its world size: Waterfall does NOT apply
    the part's rescaleFactor unless useRelativeScaling = true) per metre of nozzle
    exit diameter, fitted
    over every part whose RO config gives thrust / Pc / eps (exit diameter from
    At = F / (Pc CF), Ae = eps At), with its ln-scatter. A design's exit diameter x
    this = its "generated" plume scale.

Output: engine_designer/catalog/roengines_plumes.json (committed snapshot). With no
ROEngines checkout it re-validates the snapshot. ROEngines is CC BY-NC-ND 4.0: only
template / effect IDENTIFIERS and numbers are stored, not config text or assets.
"""
import fnmatch
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from . import mmcfg
from .build_roengines_models import _find_partconfigs_dir, _git_commit

OUTPUT_PATH = Path(__file__).resolve().parent / "roengines_plumes.json"
_CATALOG = Path(__file__).resolve().parent / "catalog.json"
_ENGINE_CONFIGS = Path(__file__).resolve().parents[2] / "Engine_Configs"

_PASS_RE = re.compile(r":((?:BEFORE|FOR|AFTER|LAST)\[[^\]]*\]|FIRST|FINAL)")
_NEEDS_RE = re.compile(r":NEEDS\[([^\]]*)\]")
# Not part of the plume's propellant identity: electric ignition / pressurants / the
# coolant-water of an RD-253-era config.
_NOT_PROPELLANT = {"ElectricCharge", "Helium", "Nitrogen", "Water"}
_OXIDIZERS = {"LqdOxygen", "NTO", "AK20", "AK27", "IRFNA-III", "IWFNA", "LqdFluorine"}
# RF resource -> the family RO's plume choice treats it as (15_auto-config.cfg:
# MMH+MON3 / MMH+MON10 / MMH+NTO all get the same hypergolic-white plume; ROEngines'
# Kerolox/ folder holds RP-1, Kerosene and RG-1 engines alike).
_RESOURCE_FAMILY = {"MON1": "NTO", "MON3": "NTO", "MON10": "NTO", "MON25": "NTO",
                    "Kerosene": "RP-1", "RG-1": "RP-1"}
_G0 = 9.80665


def resource_family(name):
    if not name:
        return name
    if name.startswith("Cooled"):
        name = name[len("Cooled"):]
    return _RESOURCE_FAMILY.get(name, name)


def propellant_key(names):
    """Order-free key for a set of RF propellant resources ('LqdOxygen+RP-1')."""
    fam = {resource_family(n) for n in names if n and n not in _NOT_PROPELLANT}
    if "HTP" in fam and fam & _OXIDIZERS:
        fam.discard("HTP")        # HTP drives the turbopump (RD-107, A-4), not the plume
    return "+".join(sorted(fam))


def template_role(template):
    t = template.lower()
    if any(s in t for s in ("lower", "sustainer", "booster")):
        return "lower"
    if any(s in t for s in ("upper", "vac")):
        return "upper"
    return "any"


def relative_scaling(wf_node):
    """True when a ROWaterfall node's plume scales with the part's rescaleFactor."""
    return any(k.lstrip("%@&") == "useRelativeScaling" and v.strip().lower() == "true"
               for k, v in wf_node.get("values", []))


def _node_dict(node):
    return {"header": node.header, "values": [list(kv) for kv in node.values],
            "children": [_node_dict(c) for c in node.children]}


def _selector_matches(selector, name):
    return any(fnmatch.fnmatchcase(name, alt.strip()) for alt in selector.split("|"))


def _parts(partconfigs):
    """{part name: {engine_type, rescale_factor}} for every ROEngines PART."""
    out = {}
    for path in sorted(partconfigs.glob("*.cfg")):
        for node in mmcfg.parse_file(path):
            if node.op or node.type_name != "PART" or not node.get("name"):
                continue
            out[node.get("name")] = {
                "engine_type": node.get("engineType"),
                "rescale_factor": mmcfg.first_number(node.get("rescaleFactor"), 1.0),
            }
    return out


def _patches(root, names):
    """Yield (part name, pass, needs, node, folder) for every @PART patch under root."""
    for path in sorted(root.rglob("*.cfg")):
        folder = path.parent.name if path.parent != root else ""
        for node in mmcfg.parse_file(path):
            if node.op != "@" or node.type_name != "PART" or not node.selector:
                continue
            pas = _PASS_RE.search(node.header)
            needs = _NEEDS_RE.search(node.header)
            for name in names:
                if _selector_matches(node.selector, name):
                    yield (name, pas.group(1) if pas else "", needs.group(1) if needs else "",
                           node, folder)


def _default_config_propellants():
    """{engineType: [RF propellant names of the default CONFIG]} from Engine_Configs/."""
    catalog = json.loads(_CATALOG.read_text())
    out = {}
    for e in catalog:
        path = _ENGINE_CONFIGS / (e.get("source_file") or "")
        if not path.is_file() or e["engine_type"] in out:
            continue
        for top in mmcfg.parse_file(path):
            if top.type_name != "PART" or f"#engineType[{e['engine_type']}]" not in top.header:
                continue
            for mec in top.walk():
                if mec.get("name") != "ModuleEngineConfigs":
                    continue
                configs = [c for c in mec.children if c.type_name == "CONFIG"]
                default = mec.get("configuration")
                pick = next((c for c in configs if c.get("name") == default),
                            configs[0] if configs else None)
                if pick is not None:
                    out[e["engine_type"]] = [p.get("name") for p in pick.find("PROPELLANT")]
                break
    return out


def _num(value):
    """catalog.json keeps the header numbers as strings ('131.41')."""
    return mmcfg.first_number(str(value)) if value is not None else None


def _exit_diameter_m(e):
    """Nozzle exit diameter from an RO config's own header numbers: At = F/(Pc CF_vac),
    CF_vac at a frozen gamma of 1.2 (the ideal CF moves < 3 % over gamma 1.15-1.25)."""
    from ..physics import isentropic
    f, pc, eps = (_num(e.get(k)) for k in ("thrust_vac_kn", "chamber_pressure_mpa", "nozzle_ratio"))
    if not (f and pc and eps) or eps < 1.5:
        return None
    gamma = 1.2
    cf = isentropic.cf_vacuum(gamma, isentropic.pe_over_pc_from_eps(eps, gamma), eps)
    at = f * 1e3 / (pc * 1e6 * cf)
    return math.sqrt(4.0 * eps * at / math.pi)


def _vec3(raw):
    vals = [mmcfg.first_number(x) for x in str(raw).split(",")]
    return vals if len(vals) == 3 and None not in vals else None


def build():
    partconfigs = _find_partconfigs_dir()
    if partconfigs is None:
        return _report_existing()
    root = partconfigs.parent
    parts = _parts(partconfigs)
    names = sorted(parts)

    plumes = {n: {"rescale_factor": parts[n]["rescale_factor"],
                  "engine_type": parts[n]["engine_type"]} for n in names}
    for name, pas, needs, node, folder in _patches(root / "Waterfall", names):
        p = plumes[name]
        rw = node.find("ROWaterfall")
        # The node is read by RO's processor from :FOR[ROWaterfall] on; ROEngines adds it
        # :BEFORE[ROWaterfall] (or earlier, e.g. RaptorVac :AFTER[ROEngines]).
        if rw and "ROWaterfall" not in pas.replace("BEFORE[ROWaterfall]", "") \
                and "waterfall" not in p:
            p["waterfall"] = dict(_node_dict(rw[0]), folder=folder, needs=needs)
        else:
            p["waterfall_other_patches"] = p.get("waterfall_other_patches", 0) + 1
    for name, pas, needs, node, folder in _patches(root / "RealPlume", names):
        plume_nodes = node.find("PLUME")
        if not plume_nodes or "!Waterfall" not in needs and pas != "BEFORE[RealPlume]":
            continue
        p = plumes[name]
        if "realplume" in p:
            continue
        power = None
        for n in node.walk():
            if n.type_name == "CONFIG" and n.selector is None and n.header.endswith(",*"):
                power = n.get("powerEffectName") or power
        power = power or plume_nodes[0].get("name")
        p["realplume"] = {"plumes": [_node_dict(x) for x in plume_nodes],
                          "power_effect_name": power, "pass": pas, "needs": needs}

    catalog = {e["engine_type"]: e for e in json.loads(_CATALOG.read_text())}
    props = _default_config_propellants()
    for p in plumes.values():
        et = p["engine_type"]
        if et in props:
            p["propellants"] = props[et]
            p["propellant_key"] = propellant_key(props[et])
    plumes = {n: p for n, p in plumes.items() if "waterfall" in p or "realplume" in p}

    payload = {"_source": "https://github.com/KSP-RO/ROEngines",
               "_commit": _git_commit(partconfigs), "_count": len(plumes),
               "parts": plumes}
    payload.update(_derive_tables(plumes, catalog))
    OUTPUT_PATH.write_text(_dump(payload))
    print(f"Wrote {len(plumes)} plume entries to {OUTPUT_PATH} (ROEngines @ {payload['_commit']})")
    _check(payload)
    return payload


def _dump(payload):
    """One line per part / table row: small, diffable."""
    lines = ["{"]
    items = list(payload.items())
    for i, (key, value) in enumerate(items):
        end = "," if i + 1 < len(items) else ""
        if isinstance(value, dict) and value and all(isinstance(v, dict) for v in value.values()):
            rows = [f"  {json.dumps(k)}: {json.dumps(v, separators=(',', ':'))}"
                    for k, v in value.items()]
            lines.append(f"{json.dumps(key)}: {{\n" + ",\n".join(rows) + f"\n}}{end}")
        else:
            lines.append(f"{json.dumps(key)}: {json.dumps(value)}{end}")
    return "\n".join(lines) + "\n}\n"


def _wf_value(p, key):
    return next((v for k, v in p["waterfall"]["values"] if k.lstrip("%@&") == key), None)


def _derive_tables(plumes, catalog):
    # Templates and glows per propellant family and role.
    uses = defaultdict(Counter)
    glow_with = defaultdict(Counter)
    for p in plumes.values():
        if "waterfall" not in p or not p.get("propellant_key"):
            continue
        tpl = _wf_value(p, "template")
        if not tpl:
            continue
        uses[p["propellant_key"]][tpl] += 1
        glow_with[tpl][_wf_value(p, "glow") or ""] += 1
    by_prop = {}
    for key, counter in sorted(uses.items()):
        roles = {}
        for role in ("lower", "upper"):
            ranked = [(t, n) for t, n in counter.most_common() if template_role(t) == role]
            if ranked:
                roles[role] = ranked[0][0]
        roles["any"] = counter.most_common(1)[0][0]
        by_prop[key] = {"roles": roles, "counts": dict(counter.most_common())}
    glow_by_template = {t: c.most_common(1)[0][0] for t, c in glow_with.items()}

    # Pump-fed audio class vs real vacuum thrust.
    thrust_by_audio = defaultdict(list)
    for p in plumes.values():
        audio = _wf_value(p, "audio") if "waterfall" in p else None
        f = _num((catalog.get(p["engine_type"]) or {}).get("thrust_vac_kn"))
        if audio and f and audio.startswith("pump-fed-") and re.search(r"-\d+$", audio):
            thrust_by_audio[audio].append(f)
    classes = sorted(((statistics.median(v), a, len(v)) for a, v in thrust_by_audio.items()
                      if len(v) >= 3))
    audio_bands = []
    for i, (med, audio, n) in enumerate(classes):
        upper = math.sqrt(med * classes[i + 1][0]) if i + 1 < len(classes) else None
        audio_bands.append({"audio": audio, "median_thrust_kn": round(med, 1), "n": n,
                            "upper_kn": round(upper, 1) if upper else None})

    # Plume scale per metre of exit diameter, per template (and per folder).
    ratios = defaultdict(list)
    folder_ratios = defaultdict(list)
    for name, p in plumes.items():
        if "waterfall" not in p:
            continue
        d = _exit_diameter_m(catalog.get(p["engine_type"]) or {})
        sc = _vec3(_wf_value(p, "scale") or "1,1,1")
        if not d or not sc:
            continue
        # Waterfall parents an effect with SetParent(parent, worldPositionStays=true): its
        # world size is `scale` itself, NOT x the part's rescaleFactor, unless the node
        # sets useRelativeScaling = true (WaterfallEffect.InitializeEffect).
        r = sc[0] * (p["rescale_factor"] if relative_scaling(p["waterfall"]) else 1.0) / d
        ratios[_wf_value(p, "template")].append(r)
        folder_ratios[p["waterfall"]["folder"]].append(r)
    def fit(vals):
        logs = [math.log(v) for v in vals]
        return {"k": round(math.exp(statistics.median(logs)), 4), "n": len(vals),
                "ln_sd": round(statistics.pstdev(logs), 3) if len(vals) > 1 else None}
    scale_fit = {t: fit(v) for t, v in sorted(ratios.items())}
    folder_fit = {f: fit(v) for f, v in sorted(folder_ratios.items())}
    return {"template_by_propellants": by_prop, "glow_by_template": glow_by_template,
            "audio_bands": audio_bands, "template_scale_per_m": scale_fit,
            "folder_scale_per_m": folder_fit,
            "recolor_scale_check": _recolor_scale_check(plumes, scale_fit)}


def _recolor_scale_check(plumes, scale_fit):
    """RO's own hand-tuned MainPlumeVariants (a part's plume swapped to another
    template for another config) vs the two recolor rules: keep the donor scale, or
    scale by k_new / k_old. Variants on another transform (LR-91's x113-250 vernier
    scales) and templates with < 2 fitted anchors are skipped."""
    k = {t: f["k"] for t, f in scale_fit.items() if f["n"] >= 2}
    seen, err_ratio, err_keep = set(), [], []
    for p in plumes.values():
        wf = p.get("waterfall")
        if not wf:
            continue
        get = lambda n, key: next((v for kk, v in n["values"] if kk.lstrip("%@&") == key), None)
        t0, s0, tr0 = get(wf, "template"), _vec3(get(wf, "scale") or ""), get(wf, "transform")
        for c in wf["children"]:
            t1, s1 = get(c, "template"), _vec3(get(c, "scale") or "")
            if (not c["header"].startswith("MainPlumeVariant") or t1 == t0 or not s0 or not s1
                    or t0 not in k or t1 not in k or get(c, "transform") not in (None, tr0)):
                continue
            ro = s1[0] / s0[0]
            if not 0.05 < ro < 20 or (t0, t1, round(ro, 3)) in seen:
                continue
            seen.add((t0, t1, round(ro, 3)))
            err_ratio.append(math.log(k[t1] / k[t0] / ro))
            err_keep.append(math.log(1.0 / ro))
    med = lambda v: round(statistics.median(v), 3) if v else None
    mad = lambda v: round(statistics.median(abs(x - statistics.median(v)) for x in v), 3) if v else None
    mae = lambda v: round(statistics.median(abs(x) for x in v), 3) if v else None
    return {"n": len(err_ratio), "ratio_rule_ln_err_median": med(err_ratio),
            "ratio_rule_ln_err_mad": mad(err_ratio), "ratio_rule_ln_abs_err_median": mae(err_ratio),
            "keep_scale_ln_err_median": med(err_keep), "keep_scale_ln_err_mad": mad(err_keep),
            "keep_scale_ln_abs_err_median": mae(err_keep)}


def _check(payload):
    parts = payload["parts"]
    aj = parts["ROE-AJ10-transtar"]["waterfall"]
    assert _wf_value(parts["ROE-AJ10-transtar"], "template") == "waterfall-hypergolic-white-upper-1", aj
    assert _vec3(_wf_value(parts["ROE-AJ10-transtar"], "scale"))[0] == 0.82, aj
    assert any(c["header"] == "MainPlumeVariant:NEEDS[B9PartSwitch]" for c in aj["children"]), aj
    assert any(c["header"] == "ExtraTemplate" for c in parts["ROE-RD107"]["waterfall"]["children"])
    assert _wf_value(parts["ROE-E1"], "template") == "waterfall-kerolox-lower-5"
    assert parts["ROE-E1"]["waterfall"]["folder"] == "Kerolox"
    assert parts["ROE-AJ10-transtar"]["realplume"]["power_effect_name"] == "Hypergolic_UpperWhite"
    assert any(n.startswith("ROE-Star37") for n in parts), "wildcard selector not resolved"
    tbp = payload["template_by_propellants"]
    assert "kerolox" in tbp["LqdOxygen+RP-1"]["roles"]["lower"], tbp["LqdOxygen+RP-1"]
    assert "hydrolox" in tbp["LqdHydrogen+LqdOxygen"]["roles"]["upper"]
    assert payload["audio_bands"] and payload["template_scale_per_m"]
    rc = payload["recolor_scale_check"]
    assert rc["n"] >= 10 and rc["ratio_rule_ln_abs_err_median"] < rc["keep_scale_ln_abs_err_median"], rc
    print(f"  recolor scale vs RO's own {rc['n']} MainPlumeVariants: median |ln err| k-ratio rule "
          f"{rc['ratio_rule_ln_abs_err_median']:.2f} (bias {rc['ratio_rule_ln_err_median']:+.2f}) vs "
          f"keep-donor-scale {rc['keep_scale_ln_abs_err_median']:.2f} "
          f"(bias {rc['keep_scale_ln_err_median']:+.2f})")
    n_wf = sum(1 for p in parts.values() if "waterfall" in p)
    n_rp = sum(1 for p in parts.values() if "realplume" in p)
    print(f"  {n_wf} parts with a ROWaterfall node, {n_rp} with RealPlume; "
          f"{len(tbp)} propellant families; {len(payload['template_scale_per_m'])} templates "
          f"with a fitted scale/exit-diameter")
    print("roengines_plumes snapshot: OK")


def _report_existing():
    if not OUTPUT_PATH.is_file():
        print("No ROEngines checkout found and no plume snapshot present.")
        return None
    payload = json.loads(OUTPUT_PATH.read_text())
    print(f"No ROEngines checkout found; validating existing snapshot "
          f"({OUTPUT_PATH.name}, ROEngines @ {payload.get('_commit', '?')}).")
    _check(payload)
    return payload


if __name__ == "__main__":
    build()
