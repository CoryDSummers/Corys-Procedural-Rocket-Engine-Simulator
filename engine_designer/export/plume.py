"""
Exhaust plume for an exported engine (2026-10-16) - `EngineDesign.plume_mode`:

  "host"      the host part's own ROEngines plume (catalog/roengines_plumes.json),
              RECOLORED when the design burns a different propellant family: the
              template + glow RO uses most for real engines of that family and role,
              rescaled by k_new / k_old (plume scale per metre of exit diameter,
              fitted per template on ROEngines' own placements - halves the error of
              keeping the donor scale against RO's hand-tuned MainPlumeVariants, see
              the snapshot's `recolor_scale_check`). Same family -> the donor plume
              verbatim.
  "generated" built from the design: template from the propellant family and the
              nozzle's regime (sea-level vs vacuum, from Isp_sl/Isp_vac and sea-level
              separation), scale = k_template x the design's computed exit diameter
              (a world size - see below), audio from cycle + thrust (pump-fed bands
              fitted on ROEngines' audio vs real thrust), placed on the host model's
              own plume anchor (transform + position). The lead-up to the tool's own
              generated models, where the exit plane is exact.
  "none"      nothing written.

Why a standalone clone needs this at all: ROEngines attaches plumes BY PART NAME
(`@PART[ROE-xxx]:BEFORE[ROWaterfall]`), in a later ModuleManager pass than the
`+PART[ROE-xxx]:BEFORE[RealismOverhaulEngines]` clone - so the renamed copy never
got one. RO's processor (RealismOverhaul/Waterfall_Configs/_Processor/) builds the
ModuleWaterfallFX for ANY part with a ROWaterfall node from :FOR[ROWaterfall] on;
writing that node on the clone :BEFORE[ROWaterfall] is all it takes. Without
Waterfall, the donor's RealPlume PLUME nodes are written instead (verbatim - RealPlume
presets carry no fitted scale, so they are not recolored).

Scale convention (Waterfall WaterfallEffect.InitializeEffect): an effect is parented
with SetParent(parent, worldPositionStays=true), so its WORLD size is the node's
`scale` and ignores the part's rescaleFactor - unless useRelativeScaling = true. Its
position is local, so it does follow the model. A rescaled copy of a host therefore
multiplies a non-relative plume's scale by the model scale, or the plume would keep
the host's full size on a shrunken nozzle.

In additional_config / new_part_in_place the host part keeps its plume for its own
configs; a recolored or generated plume is added as RO's own per-CONFIG mechanism:
a MainPlumeVariant on the host's ROWaterfall + `rowaterfallVariant` on this CONFIG
(needs B9PartSwitch, as RO's own variants do).
"""
import json
from functools import lru_cache
from pathlib import Path

from ..catalog.build_roengines_plumes import propellant_key, relative_scaling
from ..physics.burn_time import ROLE_ISP_RATIO

PLUME_MODES = ("host", "generated", "none")
PLUME_MODE_DISPLAY = {"host": "Host plume (recolored to propellant)",
                      "generated": "Generated from design",
                      "none": "None"}
_SNAPSHOT = Path(__file__).resolve().parents[1] / "catalog" / "roengines_plumes.json"

# RO's own autoConfig for an HTP / hydrazine-class thruster with no ROEngines
# template of its own (15_auto-config.cfg): the cold-gas plume at 12.65625 x the
# hypergolic-white scale.
_COLD_GAS = {"template": "rowaterfall-cold-gas-1", "glow": "ro-cold-gas",
             "scale_vs": "waterfall-hypergolic-white-upper-1", "scale_mult": 12.65625}
_FALLBACK_TEMPLATE_BY_KEY = {"HTP": _COLD_GAS}
_MIN_ANCHORS = 2            # a template's fitted k is used from this many anchors


@lru_cache(maxsize=1)
def load_snapshot():
    try:
        return json.loads(_SNAPSHOT.read_text())
    except (OSError, ValueError):
        return {}


def _get(node, key):
    return next((v for k, v in node.get("values", []) if k.lstrip("%@&") == key), None)


def _vec3(raw, default=(0.0, 0.0, 0.0)):
    try:
        vals = [float(x) for x in str(raw).split(",")]
    except ValueError:
        return list(default)
    return vals if len(vals) == 3 else list(default)


def _fmt3(v):
    return ", ".join(f"{x:.4g}" for x in v)


def plume_role(result):
    """'lower' (sea-level plume) or 'upper' (vacuum plume) from the nozzle's own
    regime: Isp_sl/Isp_vac above burn_time.ROLE_ISP_RATIO and attached at sea level."""
    vac, sl = result.get("isp_vac_engine_s"), result.get("isp_sl_engine_s")
    sea_level = bool(vac and sl and sl / vac > ROLE_ISP_RATIO
                     and not result.get("separated_at_100pct_sl"))
    return "lower" if sea_level else "upper"


def template_scale_per_m(template, folder=None, snap=None):
    """(k, source): plume scale per metre of exit diameter for a template."""
    snap = snap or load_snapshot()
    fit = snap.get("template_scale_per_m", {}).get(template)
    if fit and fit["n"] >= _MIN_ANCHORS:
        sd = f", ln-sd {fit['ln_sd']:.2f}" if fit.get("ln_sd") is not None else ""
        return fit["k"], f"k {fit['k']:.3g} fitted on {fit['n']} ROEngines plumes{sd}"
    if template == _COLD_GAS["template"]:
        k0, _ = template_scale_per_m(_COLD_GAS["scale_vs"], snap=snap)
        return k0 * _COLD_GAS["scale_mult"], "RO autoConfig cold-gas x12.65625"
    ffit = snap.get("folder_scale_per_m", {}).get(folder or "")
    if ffit:
        return ffit["k"], f"k {ffit['k']:.3g} = {folder} folder median (template unfitted)"
    if fit:
        return fit["k"], f"k {fit['k']:.3g} from a single ROEngines plume"
    return None, "no fitted scale"


def target_template(key, role, snap=None):
    """(template, glow) ROEngines uses for this propellant family + role, or None."""
    snap = snap or load_snapshot()
    fam = snap.get("template_by_propellants", {}).get(key)
    if fam:
        roles = fam["roles"]
        tpl = roles.get(role) or roles.get("any")
        return tpl, snap.get("glow_by_template", {}).get(tpl) or None
    fb = _FALLBACK_TEMPLATE_BY_KEY.get(key)
    if fb:
        return fb["template"], fb["glow"]
    return None


def audio_for(design, result, snap=None):
    snap = snap or load_snapshot()
    if design.cycle == "pressure_fed":
        return "pressure-fed-1"
    f_kn = result.get("thrust_vac_n", 0.0) / 1e3
    for band in snap.get("audio_bands", []):
        if band["upper_kn"] is None or f_kn < band["upper_kn"]:
            return band["audio"]
    return "pump-fed-medium-1"


def donor_part(host_engine_type, host_part_name, snap=None):
    """(name, entry) of the ROEngines part whose plume is borrowed."""
    parts = (snap or load_snapshot()).get("parts", {})
    if host_part_name and host_part_name in parts:
        return host_part_name, parts[host_part_name]
    for name, p in sorted(parts.items()):
        if p.get("engine_type") == host_engine_type:
            return name, p
    return None, None


def resolve_plume(design, result, rf_propellants, ex, model_scale=None):
    """Everything the .cfg needs for the plume, plus warn-only `issues`.

    rf_propellants: the CONFIG's RF resources {"fuel", "ox"}; ex: cfg_writer.
    resolve_export(); model_scale: the export's rescaleFactor multiplier (or None)."""
    mode = getattr(design, "plume_mode", "host") or "host"
    out = {"mode": mode, "issues": [], "waterfall": None, "realplume": None, "summary": ""}
    if mode == "none":
        out["summary"] = "none (no plume written)"
        return out
    snap = load_snapshot()
    if not snap:
        out["issues"].append("Plume: catalog/roengines_plumes.json missing - no plume written.")
        out["summary"] = "unavailable"
        return out

    dname, donor = donor_part(ex["host"], ex.get("host_part_name"), snap)
    wf = (donor or {}).get("waterfall")
    key = propellant_key([rf_propellants.get("fuel"), rf_propellants.get("ox")])
    role = plume_role(result)
    target = target_template(key, role, snap)
    exit_d = (result.get("geometry") or {}).get("exit_dia_m")
    model_mult = (model_scale if (model_scale and ex["mode"] != "additional_config") else 1.0)
    out.update(donor=dname, role=role, propellant_key=key)

    if mode == "host" and not wf:
        out["issues"].append(f"Plume: host {dname or ex['host']} has no ROEngines Waterfall plume - "
                             f"generated one from the design instead.")
        mode = out["mode"] = "generated"

    base_vals = [list(kv) for kv in (wf or {}).get("values", [])]
    donor_tpl = _get(wf, "template") if wf else None
    donor_scale = _vec3(_get(wf, "scale") if wf else None, (1.0, 1.0, 1.0))
    # A non-relative plume keeps its world size when the model is rescaled - follow it.
    follow = 1.0 if (wf and relative_scaling(wf)) else model_mult

    if mode == "host":
        same = (donor or {}).get("propellant_key") == key
        if same or target is None:
            if target is None and not same:
                out["issues"].append(f"Plume: no ROEngines template for {key} - kept the host's "
                                     f"{donor_tpl} plume.")
            tpl, glow, scale = donor_tpl, _get(wf, "glow"), [x * follow for x in donor_scale]
            source = f"{dname}'s own plume, verbatim" + (
                f" (scale x{follow:.3g} with the model)" if abs(follow - 1.0) > 1e-3 else "")
            children = [c for c in wf.get("children", []) if c["header"] == "ExtraTemplate"]
        else:
            tpl, glow = target
            k_new, s_new = template_scale_per_m(tpl, snap=snap)
            k_old, s_old = template_scale_per_m(donor_tpl, wf.get("folder"), snap)
            factor = (k_new / k_old) if (k_new and k_old) else 1.0
            if not (k_new and k_old):
                out["issues"].append(f"Plume: no fitted scale for {tpl if not k_new else donor_tpl} - "
                                     f"recolored plume keeps the host's scale.")
            scale = [s * factor * follow for s in donor_scale]
            glow = glow if _get(wf, "glow") else None
            source = (f"{dname}'s plume recolored {donor_tpl} -> {tpl} for {key}, scale x{factor:.2f} "
                      f"(k {k_old:.3g} -> {k_new:.3g})"
                      + (f" x{follow:.3g} with the model" if abs(follow - 1.0) > 1e-3 else "")
                      if k_new and k_old else
                      f"{dname}'s plume recolored {donor_tpl} -> {tpl} for {key}")
            children = []        # ExtraTemplates (verniers, glows) belong to the old propellant
        audio = _get(wf, "audio")
    else:  # generated
        if target is None:
            out["issues"].append(f"Plume: no ROEngines template for propellants {key} - none written.")
            out["summary"] = f"generated: no template for {key}"
            out["mode"] = "none"
            return out
        tpl, glow = target
        k, k_src = template_scale_per_m(tpl, snap=snap)
        if k is None or not exit_d:
            out["issues"].append(f"Plume: {tpl} has no fitted scale - generated plume at scale 1.")
            k, k_src = None, "unfitted"
        s = (k * exit_d) if k else 1.0
        scale = [s, s, s]
        base_vals = [kv for kv in base_vals if kv[0].lstrip("%@&") != "useRelativeScaling"]
        audio = audio_for(design, result, snap)
        children = []
        if wf:
            source = (f"generated: {tpl} ({role}), scale {s:.3g} = {k_src} x exit dia "
                      f"{exit_d:.3f} m; on {dname}'s plume anchor")
        else:
            base_vals = [["transform", "thrustTransform"], ["position", "0,0,0"], ["rotation", "0,0,0"]]
            source = (f"generated: {tpl} ({role}), scale {s:.3g} = {k_src} x exit dia "
                      f"{exit_d:.3f} m; thrustTransform origin (no host plume anchor)")
            out["issues"].append("Plume: the host has no ROEngines plume anchor - the generated plume "
                                 "sits on thrustTransform's origin; check its position in game.")

    vals = []
    overrides = {"template": tpl, "scale": _fmt3(scale), "audio": audio, "glow": glow}
    seen = set()
    for k_, v in base_vals:
        bare = k_.lstrip("%@&")
        if bare in ("moduleID", "engineID", "defaultMainPlumeVariantName", "autoConfig"):
            continue
        if bare in overrides:
            if overrides[bare] is not None and bare not in seen:
                vals.append([bare, overrides[bare]])
            seen.add(bare)
        else:
            vals.append([bare, v])
    for bare in ("template", "audio", "scale", "glow"):
        if bare not in seen and overrides[bare] is not None:
            vals.append([bare, overrides[bare]])
    out["waterfall"] = {"values": vals, "children": children}
    if mode == "host" and donor and donor.get("realplume"):
        out["realplume"] = donor["realplume"]
    out["template"], out["scale"], out["source"] = tpl, scale[0], source
    out["recolored"] = mode == "generated" or tpl != donor_tpl or scale != donor_scale
    out["summary"] = source
    return out


def _node_text(node, indent):
    tab = "\t" * indent
    lines = [f"{tab}{node['header']}", f"{tab}{{"]
    lines += [f"{tab}\t{k} = {v}" for k, v in node.get("values", [])]
    for c in node.get("children", []):
        lines.append(_node_text(c, indent + 1))
    lines.append(f"{tab}}}")
    return "\n".join(lines)


def render_blocks(plume, ex, config_name, target_selector):
    """ModuleManager text for the resolved plume ('' when nothing is written)."""
    wf = plume.get("waterfall")
    if not wf:
        return ""
    rule = "//\t" + "-" * 78
    if ex["standalone"]:
        node = {"header": "ROWaterfall", "values": wf["values"], "children": wf["children"]}
        text = f"""

{rule}
//\tPlume: {plume['summary']}.
//\tROEngines attaches plumes by PART NAME, after this clone was made - so the new
//\tpart gets its own ROWaterfall node; RO's processor builds the Waterfall module
//\tfrom it (:FOR[ROWaterfall] on).
{rule}
@PART[{ex['part_name']}]:NEEDS[Waterfall]:BEFORE[ROWaterfall]
{{
{_node_text(node, 1)}
}}
"""
        rp = plume.get("realplume")
        if rp:
            plumes = "\n".join(_node_text(p, 1) for p in rp["plumes"])
            text += f"""
//\tWithout Waterfall: the host's RealPlume effects, verbatim.
@PART[{ex['part_name']}]:NEEDS[RealPlume&!Waterfall]:BEFORE[RealPlume]
{{
\t@MODULE[ModuleEngines*]
\t{{
\t\t!runningEffectName = DELETE
\t}}
{plumes}
\t@MODULE[ModuleEngineConfigs]
\t{{
\t\t@CONFIG,*
\t\t{{
\t\t\t%powerEffectName = {rp['power_effect_name']}
\t\t}}
\t}}
}}
"""
        return text
    if not plume.get("recolored"):
        return ""           # the host's own plume already fits this config
    variant = f"engdes-{config_name}"
    keep = {"template", "scale", "position", "rotation", "transform"}
    vals = [["name", variant]] + [[k, v] for k, v in wf["values"] if k in keep]
    glow = next((v for k, v in wf["values"] if k == "glow"), None)
    if glow:
        vals.append(["glowRecolor", glow])
    node = {"header": "MainPlumeVariant", "values": vals, "children": []}
    sel = target_selector
    sel = (sel[:-1] + ",@ROWaterfall]") if sel.endswith("]]") and ":HAS[" in sel \
        else sel + ":HAS[@ROWaterfall]"
    return f"""

{rule}
//\tPlume: {plume['summary']}.
//\tThe host part keeps its own plume for its own configs; this config switches to
//\ta per-config plume variant (RO's own MainPlumeVariant / rowaterfallVariant
//\tmechanism - needs Waterfall + B9PartSwitch).
{rule}
{sel}:NEEDS[Waterfall&B9PartSwitch]:AFTER[ROWaterfall]
{{
\t@ROWaterfall
\t{{
{_node_text(node, 2)}
\t}}
\t@MODULE[ModuleEngineConfigs]
\t{{
\t\t@CONFIG[{config_name}]
\t\t{{
\t\t\t%rowaterfallVariant = {variant}
\t\t}}
\t}}
}}
"""


if __name__ == "__main__":
    snap = load_snapshot()
    assert snap, "roengines_plumes.json missing"
    # Recolor a hypergolic Transtar donor to kerolox: k-ratio scale.
    tpl, glow = target_template("LqdOxygen+RP-1", "upper", snap)
    assert tpl == "waterfall-kerolox-upper-3", tpl
    k_new, _ = template_scale_per_m(tpl, snap=snap)
    k_old, _ = template_scale_per_m("waterfall-hypergolic-white-upper-1", snap=snap)
    print(f"kerolox-upper-3 k {k_new:.3f}, hypergolic-white k {k_old:.3f} -> recolor x{k_new / k_old:.2f}")
    assert target_template("LqdHydrogen+LqdOxygen", "lower", snap)[0] == "waterfall-hydrolox-lower-4"
    assert target_template("HTP", "upper", snap)[0] == "rowaterfall-cold-gas-1"
    k_cg, src = template_scale_per_m("rowaterfall-cold-gas-1", snap=snap)
    assert abs(k_cg - k_old * 12.65625) < 1e-9, src
    print("plume: OK")
