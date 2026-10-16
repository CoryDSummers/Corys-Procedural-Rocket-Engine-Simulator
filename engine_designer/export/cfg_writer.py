"""
Renders an EngineDesign + its compute() result to RealFuels CONFIG text,
following the exact conventions used by H3-250K_Config.cfg / TR341_Config.cfg
(header spec table, design-premise comments, the two-patch shape: engine
definition :AFTER[RealismOverhaulEngines], optional RP-1 gating
:NEEDS[RP-0]:BEFORE[RealismOverhaulEnginesPost]).

Derived fields (export-time only - none of this feeds compute() or moves a
validate.py spot check):
  * `cost` / `entryCost` - estimated by physics/cost_model.py from the computed
    dry mass, chamber pressure, cycle complexity and chamber count (the caller
    can still override either). `cost` goes on the CONFIG block always; `cost`
    on a `ModuleEngineConfigs` CONFIG is a per-config recurring VAB delta.
    `entryCost` only appears in the RP-1 gating patch (RF's auto-RFUpgrade
    needs a `techRequired` to be meaningful without it).
  * The TESTFLIGHT ignition/cycle reliability curves are DERIVED from the design
    (physics/reliability.py) with the chosen controller tier as the anchor - a
    modern FFSC and a crude pressure-fed no longer get identical numbers.
  * `throttleResponseRate` / `varyIsp` / `varyMixture` / `residualsThresholdBase`
    still come straight from the controller tier (physics/controller_tech.py).
  * `massMult` defaults to 1.0 (host part's stock mass); the GUI usually passes
    a real ratio from result["computed_dry_mass_kg"] vs the host's stock mass.
  * `rated_burn_time_s` defaults to result["rated_burn_time_s"] (chamber-
    material-driven); `tested_burn_time_s` = rated x a controller-tier
    multiplier nudged by a reusability signal (physics/reliability.py
    derived_burn_times), except ablative chambers which get tested == rated.
  * RP-1 economy (verified against RealFuels' C# source + RP-1's tree files,
    2026-10-15 - README "Export"): the PART carries the base cost, a CONFIG's
    `cost` is a DELTA on it, and a CONFIG's entry cost comes ONLY from an
    `ENTRYCOSTMODS { <config> = cost[, parent...] }` row (a CONFIG-level
    `entryCost` is never read - the old export's was dead). cost_model gives the
    ABSOLUTE engine cost: a standalone part carries it as its PART cost (config
    delta 0, RP-1's own engine-part convention); a CONFIG appended to a host
    gets `cost - host part cost` (catalog/rp1_snapshot.json).
  * A standalone part also needs RP-1's PART-level gating (`TechRequired`,
    `cost`, `entryCost`, `RP0conf = true`, a ModuleTagList engine tag) - the
    clone otherwise keeps ROEngines' defaults (TechRequired = start, cost 1) and
    RP-1's NonRP0.cfg (:FOR[zzzRP-0]) relabels it "non RP-0 - <title>".
  * Host model: the clone copies ONE named ROEngines part (`+PART[<part>]`) -
    `+PART[*]:HAS[#engineType[X]]` would clone every part sharing X under one
    name. Model variants (B9PartSwitch subtypes, e.g. XLR-11 rm3/rm5, LR105
    nozzles) are picked with the CONFIG's `LinkB9PSModule[<id>] { subtype }`,
    written :BEFORE[RealismOverhaulEnginesPost] so it lands after ROEngines' own
    `@CONFIG,*` default-link patches.
  * Names / free text are sanitized: config + part names to [A-Za-z0-9-]
    (spaces break `@CONFIG[...]`, KSP turns `_` into `.` and RealFuels keys `.`
    and `_` as `-`); titles / descriptions to one line without braces or `//`
    (either silently truncates a patch). `export_issues()` lists every such
    change plus the career-mode gaps, warn-only.
  * `new_part_standalone`'s `+PART` clone explicitly sets `%RSSROConfig = True`
    on the new part. Without it, RealismOverhaul_Global_Config.cfg's
    zzzRealismOverhaul pass (`HAS[~RSSROConfig[]]`) prepends "non RO - " to
    the title, blanks/rewrites the description, and sets category to hidden
    (-1) or a "Non-RO" filter bucket - which also makes the part vanish from
    wherever RP-1's tech-node gating would otherwise place it, even though
    %techRequired was written correctly. This field is set per real part by
    RO's own mod-compat patches keyed on the DONOR part's actual name, not
    reliably inherited onto a renamed clone, so it must be set here too.
"""
import re

from .. import catalog as catalog_mod
from ..catalog import build_rp1_snapshot as rp1_mod
from ..physics import controller_tech as controller_tech_mod
from ..physics import cost_model as cost_model_mod
from ..physics import cycles as cycles_mod
from ..physics import ignition as ignition_mod
from ..physics import injectors as injectors_mod
from ..physics import materials as materials_mod
from ..physics import reliability as reliability_mod
from ..physics.combustion import is_monopropellant, propellant_densities

# RF resource names per propellant pair. Ignitor resources now come from the
# chosen ignition system (physics/ignition.py), not a per-pair default.
# Hydrazine's "ox" is None - a monopropellant, not a fuel/oxidizer pair - render_cfg()
# branches on this to emit a single PROPELLANT block instead of a fuel/ox pair.
_RF_PROPELLANTS = {
    "LOX/RP-1": {"fuel": "RP-1", "ox": "LqdOxygen"},
    "LOX/LH2": {"fuel": "LqdHydrogen", "ox": "LqdOxygen"},
    "LOX/CH4": {"fuel": "LqdMethane", "ox": "LqdOxygen"},
    "N2O4/MMH": {"fuel": "MMH", "ox": "NTO"},
    "Aerozine-50/NTO": {"fuel": "Aerozine50", "ox": "NTO"},
    "LOX/UDMH": {"fuel": "UDMH", "ox": "LqdOxygen"},
    "N2O4/UDMH": {"fuel": "UDMH", "ox": "NTO"},
    # RO's densified resources (RO_Resources.cfg), as Merlin 1D+ / NK-33 use them
    "LOX/RP-1 (subcooled)": {"fuel": "CooledRP-1", "ox": "CooledLqdOxygen"},
    "MON-3/MMH": {"fuel": "MMH", "ox": "MON3"},
    "MON-10/MMH": {"fuel": "MMH", "ox": "MON10"},
    "MON-25/MMH": {"fuel": "MMH", "ox": "MON25"},
    "Hydrazine": {"fuel": "Hydrazine", "ox": None},
    "H2O2": {"fuel": "HTP", "ox": None},
}

# The game converts a CONFIG's volumetric PROPELLANT ratios back to a mass MR with
# ITS OWN resource densities, not this tool's physics densities - so a pair whose
# volume ratio is computed from these lands on exactly the designed MR in KSP.
# kg/m3 = RESOURCE_DEFINITION density (t/L) x 1e6. Sources: RealismOverhaul
# GameData/RealismOverhaul/RO_Resources.cfg (upstream/RealismOverhaul @ 25a536b -
# defines/overrides RP-1, NTO and the Cooled* resources) and Community Resource Pack
# CommonResources.cfg (commit b329680, 2021-01-22 - LqdOxygen, UDMH, the rest).
# Cross-check: Merlin 1D+ (CooledRP-1/CooledLqdOxygen, MR 2.36) -> 0.3877/0.6123 and
# RD-253 (UDMH/NTO, MR 2.67) -> 0.4042/0.5958, both exactly as in Engine_Configs/;
# likewise AJ10-190 / Aestus (MMH/MON3) and TD-339 (MMH/MON10).
RF_RESOURCE_DENSITY_KG_M3 = {
    "LqdOxygen": 1141.0, "CooledLqdOxygen": 1236.0,
    "RP-1": 807.0, "CooledRP-1": 827.0,
    "LqdHydrogen": 70.85, "LqdMethane": 425.61,
    "NTO": 1433.0, "MON3": 1436.3, "MON10": 1444.1, "MON25": 1455.4, "MMH": 880.0, "Aerozine50": 900.0, "UDMH": 791.0,
    "Hydrazine": 1004.0, "HTP": 1431.0,
}
# Pairs whose export volume ratio uses the RF densities above. The five pre-2026-10-15
# bipropellants still use the physics densities (combustion.PROPELLANT_DENSITIES) so
# their exported configs stay byte-identical - that costs them up to ~1 % of MR in game
# (RP-1 810 vs 807, NTO 1440 vs 1433, CH4 422 vs 425.6); switching them is a separate,
# deliberate change (OPEN_QUESTIONS).
_RF_DENSITY_PAIRS = ("LOX/UDMH", "N2O4/UDMH", "LOX/RP-1 (subcooled)",
                     "MON-3/MMH", "MON-10/MMH", "MON-25/MMH")


def _propellant_ratios(pair, mr):
    """Volumetric PROPELLANT ratio fields (RF convention) from a mass mixture ratio."""
    if pair in _RF_DENSITY_PAIRS:
        rf = _RF_PROPELLANTS[pair]
        rho_fuel = RF_RESOURCE_DENSITY_KG_M3[rf["fuel"]]
        rho_ox = RF_RESOURCE_DENSITY_KG_M3[rf["ox"]]
    else:
        rho_fuel, rho_ox = propellant_densities(pair)
    # ratio_ox / ratio_fuel = MR * rho_fuel / rho_ox ; normalize to sum to 1.
    raw_ox = mr * rho_fuel / rho_ox
    total = 1.0 + raw_ox
    ratio_fuel = 1.0 / total
    ratio_ox = raw_ox / total
    return ratio_fuel, ratio_ox


def _throttle_isp_curve_block(result, throttle_floor):
    """Build a throttleIspCurve from the throttle-sweep separation onset, same
    style as H4-250K_Config.cfg. Returns None if the whole band is clean at
    sea level (onset <= throttle_floor) - no curve needed."""
    onset = result["separation_onset_throttle"]
    if onset is None or onset <= throttle_floor + 1e-9:
        return None
    ramp_end = min(onset + 0.15, 1.0)
    lines = [
        "\t\t\tuseThrottleIspCurve = true",
        "\t\t\tthrottleIspCurve",
        "\t\t\t{",
        f"\t\t\t\tkey = 0.00 0.001 0 0",
        f"\t\t\t\tkey = {onset:.2f} 0.001 0 0\t//separation onset from the design's throttle sweep",
        f"\t\t\t\tkey = {ramp_end:.2f} 0.85  0 0",
        f"\t\t\t\tkey = 1.00 1.00  0 0",
        "\t\t\t}",
        "\t\t\tthrottleIspCurveAtmStrength",
        "\t\t\t{",
        "\t\t\t\tkey = 0.0 0.02",
        "\t\t\t\tkey = 1.0 1.0",
        "\t\t\t}",
    ]
    return "\n".join(lines)


def _cfg_token(s, fallback="CustomEngine"):
    """A KSP / RealFuels identifier: letters, digits and '-' only. Spaces break
    MM selectors (`@CONFIG[My Engine]`), '.' is a config path separator, KSP
    rewrites '_' in part names to '.', and RealFuels' entry-cost / unlock keys
    map both '.' and '_' to '-' - so '-' is the one safe separator."""
    cleaned = re.sub(r"[^A-Za-z0-9-]+", "-", (s or "").strip()).strip("-")
    cleaned = re.sub(r"-{2,}", "-", cleaned)
    return cleaned or fallback


_sanitize_part_name = _cfg_token   # old name, kept for callers


def _cfg_value(s):
    """Free text safe as a single cfg value: one line, no braces (they open /
    close nodes even mid-value) and no '//' (starts a comment - the rest of the
    value is silently dropped)."""
    out = " ".join((s or "").split())
    out = out.replace("{", "(").replace("}", ")")
    while "//" in out:
        out = out.replace("//", "/ /")
    return out


DEFAULT_CONFIG_NAME = "MyEngine-100K"   # EngineDesign.config_name's default


def resolve_export(design, result, config_name=None, manufacturer=None, tech_node=None,
                   entry_cost=None, cost=None, output_mode=None, new_part=None,
                   config_description=None, ecm_parents=None, tree_icon=None,
                   host_part=None, variants=None):
    """Every exported identifier / text / RP-1 number, resolved and sanitized,
    plus `issues` (warn-only strings). Shared by render_cfg and export_issues.
    Any argument left None comes from the design's own field."""
    d = design
    issues = []
    mode = output_mode or d.output_mode
    standalone = mode == "new_part_standalone"
    host = d.host_model_engine_type
    np_ = dict(new_part or {})

    def _clean_text(label, raw):
        out = _cfg_value(raw)
        if out != " ".join((raw or "").split()):
            issues.append(f"{label}: braces / '//' replaced (they break a ModuleManager value).")
        return out

    # --- RealFuels CONFIG name (picker entry; global key for tech / ECM / TestFlight)
    raw_cfg = (config_name if config_name is not None else d.config_name) or ""
    part_raw = np_.get("name") if new_part is not None else d.new_part_name
    if not raw_cfg.strip() and standalone and (part_raw or "").strip():
        raw_cfg = part_raw
    cfg = _cfg_token(raw_cfg, "CustomEngine")
    if raw_cfg.strip() and cfg != raw_cfg.strip():
        issues.append(f"Config name '{raw_cfg.strip()}' exported as '{cfg}' "
                      f"(RealFuels / ModuleManager need letters, digits and '-').")
    if cfg == DEFAULT_CONFIG_NAME or not raw_cfg.strip():
        issues.append(f"Config name is the default '{cfg}' - every un-renamed export shares it, "
                      f"and RealFuels, RP-1 entry costs and TestFlight all key on it. Rename it.")

    # --- part identity (standalone only)
    name_src = part_raw or raw_cfg
    new_name = _cfg_token(name_src, cfg)
    if standalone and (part_raw or "").strip() and new_name != part_raw.strip():
        issues.append(f"Part name '{part_raw.strip()}' exported as '{new_name}' (the internal ID; "
                      f"the VAB shows the title).")
    title_raw = (np_.get("title") if new_part is not None else d.new_part_title) or raw_cfg or cfg
    mfr_raw = ((np_.get("manufacturer") if new_part is not None else d.new_part_manufacturer)
               or manufacturer or "Fictional")
    desc_raw = np_.get("description") if new_part is not None else d.new_part_description
    title = _clean_text("Part title", title_raw)
    mfr = _clean_text("Manufacturer", mfr_raw)
    part_desc = _clean_text("Part description", desc_raw) if (desc_raw or "").strip() else (
        f"Custom engine designed with engine_designer/. {d.propellant_pair} "
        f"{cycles_mod.CYCLE_DISPLAY[d.cycle]}, Pc {d.chamber_pressure_pa / 1e6:.1f} MPa. "
        f"Borrows the {host} model.")
    cdesc_raw = config_description if config_description is not None else d.config_description
    cfg_desc = _clean_text("Config description", cdesc_raw) if (cdesc_raw or "").strip() else None

    # --- host model part + variants
    hp_name = host_part if host_part is not None else d.host_model_part
    hpart = catalog_mod.host_model_part(host, hp_name)
    host_part_name = hpart.get("part_name") if hpart else None
    if hp_name and hpart and host_part_name != hp_name:
        issues.append(f"Host part '{hp_name}' isn't a ROEngines part for engineType {host}; "
                      f"using '{host_part_name}'.")
    if standalone and not host_part_name:
        issues.append(f"engineType {host} has no ROEngines part in the snapshot - the clone copies "
                      f"every part carrying it; if there are several they all get the same name.")
    chosen = dict(variants if variants is not None else (d.host_model_variants or {}))
    links = {}
    switches = {v["module_id"]: v for v in (hpart or {}).get("variants", [])}
    for mid, sub in chosen.items():
        if not sub:
            continue
        if mid not in switches:
            issues.append(f"Model variant: {host_part_name or host} has no '{mid}' switcher in "
                          f"the snapshot - LinkB9PSModule[{mid}] written anyway.")
        elif sub not in [st["name"] for st in switches[mid]["subtypes"]]:
            issues.append(f"Model variant: '{sub}' isn't a '{mid}' subtype of {host_part_name} - "
                          f"written anyway.")
        links[_cfg_token(mid, mid)] = _cfg_token(sub, sub)

    # --- RP-1 economy
    est = cost_model_mod.estimate_cost(d, result)
    tn = tech_node if tech_node is not None else d.tech_node
    tn = (tn or "").strip() or None
    if tn and _cfg_token(tn) != tn:
        issues.append(f"Tech node '{tn}' doesn't look like an RP-1 node id.")
    titles = rp1_mod.tech_node_titles()
    if tn and titles and tn not in titles:
        issues.append(f"Tech node '{tn}' isn't in the RP-1 snapshot's tree (typo, or a newer RP-1?).")
    abs_cost = cost if cost is not None else d.cost
    abs_cost = round(abs_cost) if abs_cost and abs_cost > 0 else est["cost"]
    ent = entry_cost if entry_cost is not None else d.entry_cost
    ent = round(ent) if ent and ent > 0 else est["entry_cost"]
    host_cost = None
    if standalone:
        part_cost, cfg_delta = abs_cost, 0
    else:
        part_cost = None
        host_cost = (rp1_mod.load().get("engine_parts", {}).get(host_part_name, {}).get("cost")
                     if host_part_name else None)
        if host_cost is None:
            host_cost = rp1_mod.host_part_cost(host)
        if host_cost is None:
            cfg_delta = 0
            if tn:
                issues.append(f"RP-1 has no part cost for host {host}: config cost delta written "
                              f"as 0 (the engine costs whatever the host part costs).")
        else:
            cfg_delta = int(round(abs_cost - host_cost))
    parents_raw = ecm_parents if ecm_parents is not None else d.rp1_ecm_parents
    parents = [_cfg_token(p) for p in (parents_raw or "").split(",") if p.strip()]
    # TestFlight matches the RAW config name (RO writes `F-1-1.5M,F-1-1.52M:50`) -
    # only the ENTRYCOSTMODS key is RealFuels-sanitized (`.`/`_` -> `-`).
    tf_parents = [q for q in (re.sub(r"[^A-Za-z0-9._+\-]", "", p) for p in (parents_raw or "").split(","))
                  if q]
    icon = tree_icon if tree_icon is not None else d.rp1_tree_icon
    pumped = d.cycle != cycles_mod.PRESSURE_FED
    tag = "EngineLiquidTurbo" if pumped else "EngineLiquidPF"
    host_tags = (rp1_mod.load().get("engine_parts", {}).get(host_part_name or "", {})
                 .get("tags", []))
    if not tn:
        issues.append("No RP-1 tech node: the config is ungated" + (
            ", and RP-1 will label the part 'non RP-0' and leave it in the start node "
            "(ROEngines' default TechRequired)." if standalone else "."))
    if icon and tn and not standalone and not host_part_name:
        issues.append("Tech-tree icon skipped: no ROEngines part name for the host to draw it with.")

    return {
        "mode": mode, "standalone": standalone, "host": host,
        "config_name": cfg, "config_description": cfg_desc,
        "part_name": new_name, "title": title, "manufacturer": mfr, "part_description": part_desc,
        "host_part_name": host_part_name, "variant_links": links,
        "tech_node": tn, "tech_title": titles.get(tn, "") if tn else "",
        "cost": abs_cost, "part_cost": part_cost, "config_cost_delta": cfg_delta,
        "host_part_cost": host_cost, "entry_cost": ent, "ecm_parents": parents,
        "testflight_parents": tf_parents,
        "tree_icon": bool(icon and tn and (standalone or host_part_name) and not standalone),
        "engine_tag": tag,
        "config_tag": tag if (not standalone and host_tags and tag not in host_tags) else None,
        "estimate": est, "issues": issues,
    }


def export_issues(design, result, **kwargs):
    """Warn-only problems with what an export would write (see resolve_export)."""
    return resolve_export(design, result, **kwargs)["issues"]


def render_cfg(design, result, config_name=None, manufacturer=None, mass_mult=1.0,
                rated_burn_time_s=None, tested_burn_time_s=None,
                ignitions=None, tech_node=None, entry_cost=None, cost=None,
                output_mode=None, model_scale=None, new_part=None,
                config_description=None, ecm_parents=None, tree_icon=None,
                host_part=None, variants=None):
    """
    design: physics.design.EngineDesign
    result: design.compute()
    Returns the full .cfg file text as a string.

    Every identity / RP-1 argument left None comes from the design's own field
    (config_name, tech_node, cost, entry_cost, output_mode, new_part_*,
    config_description, rp1_ecm_parents, rp1_tree_icon, host_model_part,
    host_model_variants) and is resolved + sanitized by resolve_export().

    `cost` is the ABSOLUTE engine cost (cost_model.estimate_cost; <= 0 ->
    estimate): written as the PART cost of a standalone part, or as the CONFIG
    delta `cost - host part cost` when appended to a host. `entry_cost` goes in
    an ENTRYCOSTMODS row keyed by the config name - the only place RealFuels
    reads a config's entry cost from.

    `output_mode`:
      "additional_config"   - append a CONFIG to the host part's
                              ModuleEngineConfigs.
      "new_part_in_place"   - additional_config PLUS a patch that rescales the
                              host part's model to this engine's length.
      "new_part_standalone" - a separate part cloned from ONE named host part
                              (rescaled), with its own name / title / RP-1
                              part-level tech gating (generated equivalent of
                              TR341_Config.cfg).
    `model_scale`: uniform rescaleFactor multiplier (designed length / host model
      native height - catalog.host_native_height_m). None or ~1.0 -> no rescale
      patch emitted. Only consulted by the two new-part modes.
    `new_part`: dict {name, title, manufacturer, description} overriding the
      design's new_part_* fields.
    """
    output_mode = output_mode or design.output_mode
    host = design.host_model_engine_type
    if not host:
        raise ValueError("design.host_model_engine_type must be set (pick a host model)")
    if output_mode not in ("additional_config", "new_part_in_place", "new_part_standalone"):
        raise ValueError(f"unknown output_mode {output_mode!r}")

    ex = resolve_export(design, result, config_name=config_name, manufacturer=manufacturer,
                        tech_node=tech_node, entry_cost=entry_cost, cost=cost,
                        output_mode=output_mode, new_part=new_part,
                        config_description=config_description, ecm_parents=ecm_parents,
                        tree_icon=tree_icon, host_part=host_part, variants=variants)
    config_name = ex["config_name"]
    tech_node = ex["tech_node"]
    entry_cost = ex["entry_cost"]
    new_name = ex["part_name"]

    _scaling = (output_mode in ("new_part_in_place", "new_part_standalone")
                and model_scale is not None and abs(model_scale - 1.0) > 1e-3)
    _standalone = output_mode == "new_part_standalone"
    # In standalone mode the part mass is pinned by `origMass` (tonnes) on the
    # MODULE, exactly like TR341_Config.cfg, so rescaleFactor stays visual-only
    # and can't double-count mass; the CONFIG's massMult is then 1.0.
    config_mass_mult = 1.0 if _standalone else mass_mult
    # Selector the gimbal / gating patches attach to.
    if _standalone:
        target_selector = f"@PART[{new_name}]"
    else:
        target_selector = f"@PART[*]:HAS[#engineType[{host}]]"
    # The model-variant link only makes sense on the one part that has the switcher.
    link_selector = (f"@PART[{new_name}]" if _standalone
                     else f"@PART[{ex['host_part_name']}]" if ex["host_part_name"]
                     else target_selector)
    clone_selector = (f"+PART[{ex['host_part_name']}]" if ex["host_part_name"]
                      else f"+PART[*]:HAS[#engineType[{host}]]")

    pair = design.propellant_pair
    rf = _RF_PROPELLANTS[pair]
    mono = is_monopropellant(pair)
    chamber_material = materials_mod.MATERIALS[design.material_key]

    if rated_burn_time_s is None:
        rated_burn_time_s = result["rated_burn_time_s"]
    if ignitions is None:
        ignitions = design.ignitions

    cycle_label = cycles_mod.CYCLE_DISPLAY[design.cycle]
    injector = injectors_mod.INJECTORS[design.injector_type]
    ign_sys = ignition_mod.IGNITION_SYSTEMS[design.ignition_system]
    ctrl = controller_tech_mod.CONTROLLER_TECHS[design.controller_tech_key]

    # TESTFLIGHT reliability + tested burn time are DERIVED from the design
    # (physics/reliability.py) with the controller tier as the anchor - a modern
    # FFSC and a crude pressure-fed no longer get identical curves. Export-time
    # only, so no compute()/validate.py number moves.
    # The RESOLVED chamber cooling method (physics/cooling.resolve_cooling_method)
    # - an explicit "ablative" on a non-ablative liner still gets the
    # char-consumption ratedBurnTime, and vice versa.
    _chamber_cooling = result["cooling"].get("chamber_cooling_method",
                                             chamber_material.cooling_method)
    _nozzle_cooling = result["cooling"].get("nozzle_cooling_method", "")
    _is_ablative = _chamber_cooling == "ablative"
    rel = reliability_mod.derived_reliability(design, result, ctrl)
    if tested_burn_time_s is None:
        rated_burn_time_s, tested_burn_time_s = reliability_mod.derived_burn_times(
            design, result, ctrl, rated_burn_time_s=rated_burn_time_s,
            is_ablative=_is_ablative)

    min_thrust_kn = result["thrust_vac_floor_n"] / 1e3
    max_thrust_kn = result["thrust_vac_n"] / 1e3
    isp_vac = result["isp_vac_engine_s"]
    isp_sl = result["isp_sl_engine_s"]

    if design.nozzle_type == "bell":
        nozzle_desc = (f"Bell ({design.bell_percent_length:.0f}% length, "
                        f"theta_n {result['theta_n_deg']:.1f} / theta_e {result['theta_e_deg']:.1f} deg)")
    else:
        nozzle_desc = f"Conical ({design.nozzle_half_angle_deg:.1f} deg half-angle)"

    header_lines = [
        "//\t" + "=" * 78,
        f"//\t{config_name}  -  designed with engine_designer/ (fictional, unless you renamed it)",
        "//",
        f"//\tPropellant: {pair}   Mixture ratio: "
        + ("N/A (monopropellant)" if mono else f"{design.mixture_ratio:.2f}"),
        f"//\tCycle: {cycle_label}   Chamber Pressure: {design.chamber_pressure_pa/1e6:.2f} MPa",
        f"//\tExpansion ratio: {design.expansion_ratio:.1f}   Nozzle: {nozzle_desc}",
        f"//\tInjector: {injector.display_name}   Ignition: {ign_sys.display_name}",
        f"//\tContraction ratio: {design.contraction_ratio:.2f}   L*: {design.lstar_m:.2f} m"
        + (f"   (combustion completeness {result['completeness_factor']:.2f}x - chamber may be "
           f"short for this propellant/injector)" if result['completeness_factor'] < 0.95 else ""),
        f"//\tChamber material: {materials_mod.MATERIALS[design.material_key].display_name} "
        f"(margin {result['material_margin']['margin_ratio']:.2f}x @ Tc {result['tc_k']:.0f} K)",
        f"//\tChamber cooling: {_chamber_cooling} "
        f"({result['cooling'].get('chamber_cooling_source', 'material-default')})   "
        f"Nozzle cooling: {_nozzle_cooling} "
        f"({result['cooling'].get('nozzle_cooling_source', 'material-default')})"
        + (f"\n//\tDump-cooled nozzle slice: {result['cooling']['dump_coolant_fraction']*100:.1f}% "
           f"of fuel, ~{result['cooling']['dump_coolant_dt_k']:.0f} K rise, Isp penalty "
           f"{result['cooling']['dump_isp_penalty_fraction']*100:.2f}%"
           if result["cooling"].get("dump_isp_penalty_fraction") else ""),
        f"//\tNozzle-extension material (past eps {design.cooling_transition_eps:.0f}): "
        f"{materials_mod.MATERIALS[design.bell_material_key].display_name} "
        f"(margin {result['bell_material_margin']['margin_ratio']:.2f}x @ local T "
        f"{result['t_local_at_transition_k']:.0f} K)",
        "//",
        f"//\tThrust (Vac): {max_thrust_kn:.1f} kN   Thrust (Vac, floor): {min_thrust_kn:.1f} kN",
        f"//\tISP: {isp_sl:.1f} SL / {isp_vac:.1f} Vac",
        f"//\tThrottle: {design.throttle_floor*100:.0f} - 100%",
        f"//\tmdot: {result['mdot_kgs']:.1f} kg/s",
        f"//\tEstimated dry mass: {result['computed_dry_mass_kg']:.1f} kg (chamber/nozzle wall "
        f"{result['chamber_wall_mass_kg']+result['bell_wall_mass_kg']:.1f} kg + turbopump "
        f"{result['computed_dry_mass_kg']-result['chamber_wall_mass_kg']-result['bell_wall_mass_kg']-result.get('stability_aid_mass_kg', 0.0)-result.get('injector_plate_mass_kg', 0.0)-result.get('manifold_mass_kg', 0.0)-result.get('plumbing_mass_kg', 0.0):.1f} kg"
        f" + injector plate {result.get('injector_plate_mass_kg', 0.0):.1f} kg"
        f" + manifold {result.get('manifold_mass_kg', 0.0):.1f} kg"
        + (f" + plumbing {result['plumbing_mass_kg']:.1f} kg" if result.get('plumbing_mass_kg', 0.0) > 0.0 else "")
        + (f" + stability aids {result['stability_aid_mass_kg']:.1f} kg" if result.get('stability_aid_mass_kg', 0.0) > 0.0 else "")
        + " - a LOWER BOUND, see physics/mass_model.py: no valves/actuators/mounting structure)",
        f"//\tRated / tested burn time: {rated_burn_time_s:.0f} / {tested_burn_time_s:.0f} s"
        + (f" (duty target {result['rated_burn_time_target_s']:.0f} s, "
           + ("carried" if result.get("rated_limited_by", "target") == "target"
              else f"capped by {result['rated_limited_by'].replace('_', ' ')}")
           + (f"; life {result['burn_life_s']:.0f} s" if result.get("burn_life_s", float("inf"))
              != float("inf") else "") + ")"
           if "rated_burn_time_target_s" in result else ""),
        "//",
    ]
    _sizing = result.get("turbopump_sizing")
    if _sizing:
        _fp = _sizing["fuel_pump"]
        _op = _sizing["ox_pump"]
        header_lines.append(
            f"//\tTurbopump: {_sizing['arrangement'].replace('_', ' ')}, {_sizing['n_turbines']}x "
            f"{_sizing['turbine_staging'].replace('_', ' ')} turbine, "
            f"{_fp['n_stages']}-stage fuel pump {_fp['n_rpm']:.0f} rpm / "
            f"{_op['n_stages']}-stage ox pump {_op['n_rpm']:.0f} rpm, {_sizing['material_display']}")
        header_lines.append(
            f"//\t  derived efficiency: fuel pump {_sizing['eta_pump_fuel']:.3f}, ox pump "
            f"{_sizing['eta_pump_ox']:.3f}, turbine {_sizing['eta_turbine']:.3f} "
            f"(overall {_sizing['eta_overall']:.3f}); assembly ~{_sizing['assembly_length_m']:.2f}x"
            f"{_sizing['assembly_od_m']:.2f} m, ~{_sizing['mass_kg']*_sizing['mass_modifier']:.0f} kg; "
            f"peak tip speed {max(_fp['u_tip_m_s'], _op['u_tip_m_s']):.0f} m/s "
            f"({'feasible' if _sizing['feasible'] else 'MARGINAL - see warnings'})")
        header_lines.append("//")

    _cyc = result.get("cycle_result") or {}
    _cname = _cyc.get("cycle")
    _cycle_note = ""
    if _cname == "electric_pump":
        _cycle_note = (
            f"battery {_cyc['battery_mass_kg']:.0f} kg + motor {_cyc['motor_mass_kg']:.0f} kg, "
            f"~{_cyc['electrical_energy_j']/3.6e6:.1f} kWh at {_cyc['electrical_power_w']/1e3:.0f} kW; "
            f"no turbine, no bleed - engine Isp = chamber Isp")
    elif _cname in ("frsc", "orsc", "ffsc"):
        _dg = _cyc.get("drive_gas", {})
        _boost = {"frsc": "fuel", "orsc": "ox", "ffsc": "both"}[_cname]
        _cycle_note = (
            f"{_cyc['preburner_gas_kind'].replace('_', '-')} preburner, "
            f"~{_cyc['preburner_flow_fraction']*100:.0f}% of flow ({_cyc['gg_mdot_kgs']:.1f} kg/s) "
            f"at ~{_dg.get('tin_k', 0):.0f} K; {_boost} pump(s) boosted > 2x Pc; "
            f"closed cycle - no dump loss")
    elif _cname in ("tap_off", "gas_generator"):
        _dg = _cyc.get("drive_gas", {})
        _cycle_note = (
            f"chamber tap-off gas film-cooled to ~{_dg.get('tin_k', 0):.0f} K, "
            if _cname == "tap_off" else "gas-generator ")
        _cycle_note += (f"bleed {_cyc['gg_flow_fraction']*100:.1f}% "
                        f"({_cyc['gg_mdot_kgs']:.1f} kg/s)")
        # physics/turbine_exhaust.py: where the spent drive gas goes. Its thrust
        # is already folded into the engine Isp/thrust above - RealFuels has no
        # separate exhaust stream, and (like RO's own LR-91) no roll module is
        # emitted for a canted exhaust nozzle.
        _te = result.get("turbine_exhaust")
        if _te:
            _cycle_note += (
                f"; turbine exhaust: {_te['mode'].replace('_', ' ')}, turbine PR "
                f"{_te['turbine_pressure_ratio']:.1f}, {_te['t_exhaust_k']:.0f} K, exhaust Isp "
                f"{_te['isp_vac_s']:.0f} s vac ({_te['isp_fraction_vac']*100:.0f}% of chamber)")
            if _te.get("hx_on"):
                _hx_coils = " + ".join(filter(None, [
                    f"{_te['hx_gox_kgs']:.2f} kg/s GOX" if _te["hx_gox_kgs"] > 0.0 else "",
                    f"{_te['hx_he_kgs']:.2f} kg/s He" if _te["hx_he_kgs"] > 0.0 else ""]))
                _cycle_note += f", exhaust heat exchanger {_hx_coils}"
            if abs(_te.get("roll_torque_nm") or 0.0) > 0:
                _cycle_note += (f", canted {_te['cant_deg']:.0f} deg: "
                                f"{_te['roll_torque_nm']:.0f} N.m roll torque (not exported)")
    if _cycle_note:
        header_lines.append(f"//\tCycle detail: {_cycle_note}")
        header_lines.append("//")

    if result["warnings"]:
        header_lines.append("//\tWARNINGS from the design tool (review before using in a career save):")
        for w in result["warnings"]:
            header_lines.append(f"//\t  - {w}")
        header_lines.append("//")

    # --- identity / career summary: what each name below is FOR in game ---
    header_lines.append(f"//\tRealFuels CONFIG: {config_name}  (engine-config picker entry; also the "
                        f"key for RP-1 tech / entry cost and TestFlight)")
    if _standalone:
        header_lines.append(f"//\tKSP part: name {new_name} (internal ID)  |  title \"{ex['title']}\" "
                            f"(VAB name)  |  manufacturer \"{ex['manufacturer']}\"")
    _model = ex["host_part_name"] or f"#engineType[{host}]"
    _vl = ", ".join(f"{k}={v}" for k, v in ex["variant_links"].items())
    header_lines.append(f"//\tModel: {_model}" + (f"  variant {_vl}" if _vl else "  (part's default variant)"))
    if tech_node:
        if _standalone:
            _costs = "(PART cost; config delta 0)"
        elif ex["host_part_cost"] is not None:
            _costs = (f"(host part {ex['host_part_cost']:.0f} + config delta "
                      f"{ex['config_cost_delta']:+d})")
        else:
            _costs = "(host part cost unknown - delta 0)"
        header_lines.append(
            f"//\tRP-1: tech node {tech_node}" + (f" ({ex['tech_title']})" if ex["tech_title"] else "")
            + f"  |  engine cost {ex['cost']} {_costs}  |  entry cost {entry_cost}"
            + (f" (tech-transfer parents: {', '.join(ex['ecm_parents'])})" if ex["ecm_parents"] else ""))
    else:
        header_lines.append("//\tRP-1: no tech node - not gated in a career save")
    if ex["issues"]:
        header_lines.append("//\tEXPORT NOTES (warn-only):")
        for _iss in ex["issues"]:
            header_lines.append(f"//\t  - {_iss}")
    header_lines.append("//")

    origmass_t = result["computed_dry_mass_kg"] / 1000.0
    _mode_desc = {
        "additional_config": f"additional CONFIG appended to the {host} part",
        "new_part_in_place": f"the {host} part, rescaled in place",
        "new_part_standalone": f"new standalone part '{new_name}' borrowing the {host} model",
    }[output_mode]
    header_lines.append(f"//\tOutput mode: {_mode_desc}")
    if _scaling:
        _L = result["profile_meta"]["total_length_m"]
        header_lines.append(
            f"//\t  model rescaleFactor x{model_scale:.4f} (design length {_L:.2f} m, "
            f"uniform scale)")
    if _standalone:
        header_lines.append(
            f"//\torigMass = {origmass_t:.4f} t - part mass pinned (TR341 convention); "
            f"CONFIG massMult = 1.0 and rescaleFactor is visual only.")
    else:
        header_lines.append(f"//\tmassMult = {mass_mult:.3f} (host part's stock mass x this multiplier). "
                             f"{'Estimated from the design physics above vs. the host part.' if abs(mass_mult - 1.0) > 1e-9 else 'Defaults to 1.0 (host part stock mass) unless the GUI computed a real ratio against the host.'}")
    if output_mode == "new_part_in_place" and _scaling:
        header_lines.append("//\t  NOTE: KSP scales part mass by rescaleFactor^3 - re-check "
                            "massMult against the rescaled host.")
    header_lines.append("//\t" + "=" * 78)
    header = "\n".join(header_lines)

    ignitor_lines = []
    for name, amount in ign_sys.rf_ignitor_resources:
        ignitor_lines.append("\t\t\tIGNITOR_RESOURCE")
        ignitor_lines.append("\t\t\t{")
        ignitor_lines.append(f"\t\t\t\tname = {name}")
        ignitor_lines.append(f"\t\t\t\tamount = {amount}")
        ignitor_lines.append("\t\t\t}")
    ignitor_block = "\n".join(ignitor_lines)
    if ign_sys.forces_single_ignition:
        ignitions = 1

    throttle_curve = _throttle_isp_curve_block(result, design.throttle_floor)
    throttle_curve_block = ("\n" + throttle_curve + "\n") if throttle_curve else ""

    pressure_fed_line = "\t\t\tpressureFed = True\n" if design.cycle == cycles_mod.PRESSURE_FED else "\t\t\tpressureFed = False\n"
    # A monopropellant uses a single positive-expulsion/surface-tension tank (no risk of
    # settling the "wrong" propellant) - matches MR-80B's real `ullage = False`. Bipropellant
    # designs keep the existing `ullage = True` convention (unchanged from before).
    ullage_line = "\t\t\tullage = False\n" if mono else "\t\t\tullage = True\n"

    if mono:
        propellant_block = f"""\t\t\tPROPELLANT
\t\t\t{{
\t\t\t\tname = {rf['fuel']}
\t\t\t\tratio = 1.0
\t\t\t\tDrawGauge = True
\t\t\t}}"""
    else:
        ratio_fuel, ratio_ox = _propellant_ratios(pair, design.mixture_ratio)
        propellant_block = f"""\t\t\tPROPELLANT
\t\t\t{{
\t\t\t\tname = {rf['fuel']}
\t\t\t\tratio = {ratio_fuel:.4f}
\t\t\t\tDrawGauge = True
\t\t\t}}

\t\t\tPROPELLANT
\t\t\t{{
\t\t\t\tname = {rf['ox']}
\t\t\t\tratio = {ratio_ox:.4f}
\t\t\t\tDrawGauge = False
\t\t\t}}"""

    _config_desc = ex["config_description"] or _cfg_value(
        f"Custom engine designed with engine_designer/. {pair} {cycle_label}, "
        f"{injector.display_name} injector, {ign_sys.display_name} ignition, Pc "
        f"{design.chamber_pressure_pa/1e6:.2f} MPa, {nozzle_desc.lower()} nozzle, throttles "
        f"{design.throttle_floor*100:.0f}-100%.")
    _config_cost = 0 if _standalone else ex["config_cost_delta"]
    # TestFlight techTransfer: the ECM tech-transfer parents also hand down a share
    # of their flight data (RO format `A,B:50`; TestFlight_Generic_Engines.cfg).
    _xfer = max(0.0, min(100.0, float(getattr(design, "testflight_transfer_pct", 0.0) or 0.0)))
    tech_transfer_line = (f"\t\t\t\ttechTransfer = {','.join(ex['testflight_parents'])}:{_xfer:.0f}\n"
                          if ex["testflight_parents"] and _xfer > 0 else "")

    # The CONFIG body (fields at 3-tab indent) - identical whether it sits inside
    # an `@MODULE[ModuleEngineConfigs]` patch (additional_config / in-place) or a
    # freshly-built `MODULE { name = ModuleEngineConfigs ... }` (standalone).
    config_inner = f"""\t\t\tname = {config_name}
\t\t\tdescription = {_config_desc}
\t\t\tspecLevel = concept
\t\t\tminThrust = {min_thrust_kn:.2f}
\t\t\tmaxThrust = {max_thrust_kn:.2f}
\t\t\tratedBurnTime = {rated_burn_time_s:.0f}
\t\t\theatProduction = 100
\t\t\tmassMult = {config_mass_mult}
\t\t\tcost = {_config_cost}
\t\t\tthrottleResponseRate = {ctrl.throttle_response_rate}
\t\t\tvaryIsp = {ctrl.vary_isp}
\t\t\tvaryMixture = {ctrl.vary_mixture}
\t\t\tresidualsThresholdBase = {ctrl.residuals_threshold_base}
{pressure_fed_line}{ullage_line}\t\t\tignitions = {ignitions}

{ignitor_block}

{propellant_block}

\t\t\tatmosphereCurve
\t\t\t{{
\t\t\t\tkey = 0 {isp_vac:.1f}
\t\t\t\tkey = 1 {isp_sl:.1f}
\t\t\t}}
{throttle_curve_block}
\t\t\tTESTFLIGHT:NEEDS[TestLite|TestFlight]
\t\t\t{{
\t\t\t\ttestedBurnTime = {tested_burn_time_s:.0f}
\t\t\t\tratedBurnTime = {rated_burn_time_s:.0f}
\t\t\t\tsafeOverburn = true
\t\t\t\tignitionReliabilityStart = {rel['ignition_reliability_start']:.6f}
\t\t\t\tignitionReliabilityEnd = {rel['ignition_reliability_end']:.6f}
\t\t\t\tcycleReliabilityStart = {rel['cycle_reliability_start']:.6f}
\t\t\t\tcycleReliabilityEnd = {rel['cycle_reliability_end']:.6f}
{tech_transfer_line}\t\t\t}}"""

    if _standalone:
        _rescale_line = f"\t@rescaleFactor *= {model_scale:.4f}\n" if _scaling else ""
        engine_patch = f"""{clone_selector}:NEEDS[RealismOverhaul&RealFuels]:BEFORE[RealismOverhaulEngines]
{{
\t@name = {new_name}
\t%engineType = {new_name}
\t%category = Engine
\t%title = {ex["title"]}
\t%manufacturer = {ex["manufacturer"]}
\t%description = {ex["part_description"]}
\t%RSSROConfig = True
\t@tags ^= :$: engine-designer custom fictional
{_rescale_line}\t!MODULE[ModuleEngineConfigs],*{{}}
\t!MODULE[ModuleAlternator],*{{}}
\t!RESOURCE,*{{}}
}}


//\t{'-' * 78}
//\tEngine definition for the new part (its own #engineType[{new_name}]).
//\torigMass pins the part mass in tonnes (TR341 convention).
//\t{'-' * 78}
@PART[{new_name}]:NEEDS[RealismOverhaul&RealFuels]:AFTER[RealismOverhaulEngines]
{{
\tMODULE
\t{{
\t\tname = ModuleEngineConfigs
\t\ttype = ModuleEngines
\t\tmodded = false
\t\tconfiguration = {config_name}
\t\torigMass = {origmass_t:.4f}
\t\tCONFIG
\t\t{{
{config_inner}
\t\t}}
\t}}
}}
"""
    else:
        engine_patch = f"""@PART[*]:HAS[#engineType[{host}]]:NEEDS[RealismOverhaul&RealFuels]:AFTER[RealismOverhaulEngines]
{{
\t@MODULE[ModuleEngineConfigs]
\t{{
\t\tCONFIG
\t\t{{
{config_inner}
\t\t}}
\t}}
}}
"""
        if output_mode == "new_part_in_place" and _scaling:
            engine_patch = f"""//\t{'-' * 78}
//\tRescale the host model to the designed engine's length (uniform rescaleFactor).
//\t{'-' * 78}
@PART[*]:HAS[#engineType[{host}]]:NEEDS[RealismOverhaul&RealFuels]:BEFORE[RealismOverhaulEngines]
{{
\t@rescaleFactor *= {model_scale:.4f}
}}


""" + engine_patch

    gimbal_patch = ""
    if design.gimbal_mode == "custom":
        response_lines = ""
        if design.gimbal_response_speed_deg_s > 0:
            response_lines = (f"\t\t%useGimbalResponseSpeed = true\n"
                               f"\t\t%gimbalResponseSpeed = {design.gimbal_response_speed_deg_s:.1f}\n")
        gimbal_patch = f"""

//\t{'-' * 78}
//\tGimbal: custom override ({design.gimbal_range_deg:.1f} deg).
//\t{'-' * 78}
{target_selector}:NEEDS[RealismOverhaul&RealFuels]:AFTER[RealismOverhaulEngines]
{{
\t@MODULE[ModuleGimbal]
\t{{
\t\t%gimbalRange = {design.gimbal_range_deg:.1f}
{response_lines}\t}}
}}
"""
    elif design.gimbal_mode == "ungimballed":
        gimbal_patch = f"""

//\t{'-' * 78}
//\tGimbal: explicitly removed (matches real small RCS/vernier-class engines
//\tand boosters that use separate vernier chambers for TVC instead of
//\tgimballing the main chamber).
//\t{'-' * 78}
{target_selector}:NEEDS[RealismOverhaul&RealFuels]:AFTER[RealismOverhaulEngines]
{{
\t!MODULE[ModuleGimbal],*{{}}
}}
"""
    # design.gimbal_mode == "inherit" -> gimbal_patch stays "" (no export change,
    # matches H3-250K/H4-250K's "inherited from the part" convention)

    variant_patch = ""
    if ex["variant_links"]:
        _lk = "".join(f"\t\t\t!LinkB9PSModule[{mid}],* {{}}\n"
                      f"\t\t\tLinkB9PSModule[{mid}]\n\t\t\t{{\n\t\t\t\tsubtype = {sub}\n\t\t\t}}\n"
                      for mid, sub in ex["variant_links"].items())
        variant_patch = f"""

//\t{'-' * 78}
//\tModel variant: RealFuels switches the part's B9PartSwitch model to this subtype
//\twhen the config is selected. Runs after ROEngines' own `@CONFIG,*` default
//\tlinks (:AFTER[RealismOverhaulEngines]) so this choice wins.
//\t{'-' * 78}
{link_selector}:NEEDS[RealismOverhaul&RealFuels&B9PartSwitch]:BEFORE[RealismOverhaulEnginesPost]
{{
\t@MODULE[ModuleEngineConfigs]
\t{{
\t\t@CONFIG[{config_name}]
\t\t{{
{_lk}\t\t}}
\t}}
}}
"""

    gating_patch = ""
    if tech_node:
        _tag_line = f"\t\t\ttag = {ex['config_tag']}\n" if ex["config_tag"] else ""
        _ecm = ", ".join([str(entry_cost)] + ex["ecm_parents"])
        gating_patch = f"""

//\t{'-' * 78}
//\tRP-1 career gating.  Every block below no-ops without RP-1 (:NEEDS[RP-0]).
//\t  CONFIG techRequired / cost : the config's tech node; cost is a DELTA on the
//\t                               part's own cost (RP-1 TREE-Engines convention).
//\t  ENTRYCOSTMODS              : the config's unlock cost - the ONLY place
//\t                               RealFuels reads it from (keyed by config name;
//\t                               listed parents discount it once owned).
//\tcost / entry cost estimated by physics/cost_model.py (fit to RP-1's own
//\tengine prices, ~x1.7 scatter) - tune to taste.
//\t{'-' * 78}
{target_selector}:NEEDS[RP-0]:BEFORE[RealismOverhaulEnginesPost]
{{
\t@MODULE[ModuleEngineConfigs]
\t{{
\t\t@CONFIG[{config_name}]
\t\t{{
\t\t\t%techRequired = {tech_node}
\t\t\t%cost = {_config_cost}
{_tag_line}\t\t}}
\t}}
}}

ENTRYCOSTMODS:NEEDS[RP-0]
{{
\t{config_name} = {_ecm}
}}
"""
        if _standalone:
            gating_patch += f"""
//\tRP-1 part placement (the fields RP-1's TREE-Parts.cfg sets on its own parts,
//\t:FOR[xxxRP0]). RP0conf = true keeps NonRP0.cfg (:FOR[zzzRP-0]) from relabelling
//\tthe part "non RP-0"; entryCost 0 because the config's ENTRYCOSTMODS row
//\tcarries the unlock cost; the tag sets RP-1's launch-cost multiplier.
@PART[{new_name}]:NEEDS[RP-0]:AFTER[xxxRP0]
{{
\t%TechRequired = {tech_node}
\t%cost = {ex["part_cost"]}
\t%entryCost = 0
\t%RP0conf = true
\t%MODULE[ModuleTagList] {{ tag = {ex["engine_tag"]} }}
}}
"""
        if ex["tree_icon"]:
            _ttl = _cfg_value(f"{ex['host_part_name']} Engine Upgrade: {config_name} Config")
            gating_patch += f"""
//\tTech-tree icon (RP-1 writes these by hand for its own configs; RealFuels does
//\tnot create them). Cosmetic: the config is still gated by techRequired and
//\tbought in the engine-config picker.
PARTUPGRADE:NEEDS[RP-0]
{{
\tname = RFUpgrade_{config_name}
\tpartIcon = {ex["host_part_name"]}
\ttechRequired = {tech_node}
\tentryCost = 0
\tcost = 0
\ttitle = {_ttl}
\tbasicInfo = Engine Performance Upgrade
\tmanufacturer = Engine Upgrade
\tdescription = Adds the {config_name} configuration (engine_designer/). Unlock it in the VAB/SPH through the engine configs interface.
}}
"""

    return header + "\n\n" + engine_patch + variant_patch + gimbal_patch + gating_patch


def write_cfg(path, *args, **kwargs):
    text = render_cfg(*args, **kwargs)
    with open(path, "w") as f:
        f.write(text)
    return text


def _balanced(text):
    """Every '{' has a matching '}' (ignoring braces in // comments)."""
    depth = 0
    for line in text.splitlines():
        code = line.split("//", 1)[0]
        depth += code.count("{") - code.count("}")
        if depth < 0:
            return False
    return depth == 0


if __name__ == "__main__":
    from ..physics.design import EngineDesign

    base = EngineDesign(host_model_engine_type="F1", tech_node="orbitalRocketry1966",
                        gimbal_mode="custom", gimbal_range_deg=5.0)
    res = base.compute()
    tn = base.tech_node

    # additional_config: unchanged shape - the historical patch.
    a = render_cfg(base, res, "TestEngine-1M", tech_node=tn,
                   output_mode="additional_config")
    assert _balanced(a), "additional_config: unbalanced braces"
    assert "@PART[*]:HAS[#engineType[F1]]:NEEDS[RealismOverhaul&RealFuels]:AFTER[RealismOverhaulEngines]" in a
    assert "@MODULE[ModuleEngineConfigs]" in a and "\t\tCONFIG\n\t\t{" in a
    assert "\t\t\tmassMult = 1.0" in a
    assert "+PART[" not in a and "@rescaleFactor" not in a
    assert "@PART[*]:HAS[#engineType[F1]]:NEEDS[RP-0]:BEFORE[RealismOverhaulEnginesPost]" in a

    # new_part_in_place: same CONFIG patch + a prepended rescale patch.
    b = render_cfg(base, res, "TestEngine-1M", output_mode="new_part_in_place",
                   model_scale=0.75)
    assert _balanced(b), "new_part_in_place: unbalanced braces"
    assert "@rescaleFactor *= 0.7500" in b
    assert ":BEFORE[RealismOverhaulEngines]\n{\n\t@rescaleFactor *= 0.7500\n}" in b
    assert "@MODULE[ModuleEngineConfigs]" in b  # CONFIG still appended to the host

    # new_part_standalone: a borrowed-model copy + its own engine definition.
    c = render_cfg(base, res, "TestEngine 1M!", tech_node=tn,
                   output_mode="new_part_standalone", model_scale=0.509,
                   new_part={"name": "", "title": "Test Engine 1M",
                             "manufacturer": "ACME", "description": "hi"})
    assert _balanced(c), "new_part_standalone: unbalanced braces"
    # Clones ONE named ROEngines part, never every part sharing the engineType.
    assert "+PART[ROE-F1]:NEEDS[RealismOverhaul&RealFuels]:BEFORE[RealismOverhaulEngines]" in c
    assert "@name = TestEngine-1M" in c and "%engineType = TestEngine-1M" in c  # sanitized
    assert "@rescaleFactor *= 0.5090" in c
    assert "!MODULE[ModuleEngineConfigs],*{}" in c
    # RealismOverhaul_Global_Config.cfg's zzzRealismOverhaul pass prepends
    # "non RO - " to the title and hides/recategorizes any part missing this
    # field - the standalone clone must set it explicitly, it is NOT reliably
    # inherited from the +PART donor.
    assert "\t%RSSROConfig = True\n" in c
    assert "\tMODULE\n\t{\n\t\tname = ModuleEngineConfigs" in c
    assert "\t\torigMass = " in c and "\t\t\tmassMult = 1.0" in c
    assert "@PART[TestEngine-1M]:NEEDS[RealismOverhaul&RealFuels]:AFTER[RealismOverhaulEngines]" in c
    assert "@PART[TestEngine-1M]:NEEDS[RP-0]:BEFORE[RealismOverhaulEnginesPost]" in c
    assert "#engineType[F1]" not in c.split("AFTER[RealismOverhaulEngines]", 1)[1]  # gimbal/gating retargeted

    # model_scale ~1.0 -> no rescale line even in a new-part mode.
    d = render_cfg(base, res, "X", output_mode="new_part_standalone", model_scale=1.0004)
    assert "@rescaleFactor" not in d

    # --- RP-1 economy (README "Export"): no CONFIG-level entryCost anywhere (RF never
    # reads it); the entry cost is an ENTRYCOSTMODS row keyed by the config name.
    for txt in (a, b, c):
        assert "%entryCost = " not in txt.split("ENTRYCOSTMODS", 1)[0].split("AFTER[xxxRP0]")[0], txt
        assert "ENTRYCOSTMODS:NEEDS[RP-0]\n{\n\t" in txt
    ab = resolve_export(base, res, config_name="TestEngine-1M", output_mode="additional_config")
    host_cost = ab["host_part_cost"]
    assert host_cost == 1855, ab                       # RP-1's ROE-F1 part cost
    assert ab["config_cost_delta"] == ab["cost"] - 1855
    assert f"\t\t\tcost = {ab['config_cost_delta']}\n" in a       # CONFIG carries the DELTA
    assert f"\t\t\t%cost = {ab['config_cost_delta']}\n" in a
    assert f"\tTestEngine-1M = {ab['entry_cost']}\n" in a
    # Tree icon in additional mode (drawn with the host part), none in standalone.
    assert "PARTUPGRADE:NEEDS[RP-0]" in a and "\tname = RFUpgrade_TestEngine-1M\n" in a
    assert "\tpartIcon = ROE-F1\n" in a
    assert "PARTUPGRADE" not in c
    no_icon = render_cfg(base, res, "TestEngine-1M", output_mode="additional_config", tree_icon=False)
    assert "PARTUPGRADE" not in no_icon
    # Standalone: RP-1 PART-level placement so NonRP0.cfg doesn't relabel it, PART
    # carries the absolute cost, the CONFIG delta is 0.
    sc = resolve_export(base, res, config_name="TestEngine 1M!", output_mode="new_part_standalone")
    assert "@PART[TestEngine-1M]:NEEDS[RP-0]:AFTER[xxxRP0]" in c
    assert "\t%TechRequired = orbitalRocketry1966\n" in c and "\t%RP0conf = true\n" in c
    assert f"\t%cost = {sc['cost']}\n" in c and "\t%entryCost = 0\n" in c
    assert "%MODULE[ModuleTagList] { tag = EngineLiquidTurbo }" in c
    assert "\t\t\tcost = 0\n" in c
    # Tech-transfer parents land in the ECM row.
    par = render_cfg(base, res, "TestEngine-1M", output_mode="additional_config",
                     ecm_parents="F-1, F-1A_v2")
    assert f"\tTestEngine-1M = {ab['entry_cost']}, F-1, F-1A-v2\n" in par
    # ... and hand down TestFlight data (techTransfer, RO's `A,B:pct` format).
    assert "\t\t\t\ttechTransfer = F-1,F-1A_v2:50\n" in par
    assert "techTransfer" not in render_cfg(base, res, "TestEngine-1M", output_mode="additional_config")
    # No tech node: no gating at all, and the issues say what RP-1 will do.
    ungated = EngineDesign(host_model_engine_type="F1", output_mode="new_part_standalone",
                           config_name="Ungated-1", new_part_name="Ungated 1")
    ug = render_cfg(ungated, res)
    assert "RP-0" not in ug.split("//\t" + "=" * 78, 2)[2], "no RP-1 blocks without a tech node"
    assert any("non RP-0" in i for i in export_issues(ungated, res))
    # Default config name is flagged (every un-renamed export would collide).
    assert any("default 'MyEngine-100K'" in i for i in export_issues(EngineDesign(
        host_model_engine_type="F1"), res))
    # Pressure-fed -> EngineLiquidPF tag; a pressure-fed config on a turbo host
    # also gets a CONFIG-level tag (RP-1's own AR-2 convention).
    pf_d = EngineDesign(host_model_engine_type="F1", cycle="pressure_fed", tech_node="orbitalRocketry1966",
                        chamber_pressure_pa=1.5e6, config_name="PF-1")
    pf_ex = resolve_export(pf_d, res, output_mode="additional_config")
    assert pf_ex["engine_tag"] == "EngineLiquidPF" and pf_ex["config_tag"] == "EngineLiquidPF"

    # --- sanitizing: hostile names / text can't break the patch.
    hostile = EngineDesign(host_model_engine_type="F1", output_mode="new_part_standalone",
                           tech_node="orbitalRocketry1966", config_name="My Engine_v1.2",
                           new_part_name="Bell Model 8760", new_part_title="Bell {Model} 8760",
                           new_part_manufacturer="Bell // Textron",
                           new_part_description="Line one\nsee http://example.com {x}",
                           config_description="picker // text")
    hx = render_cfg(hostile, res)
    assert _balanced(hx), "hostile text unbalanced braces"
    assert "@CONFIG[My-Engine-v1-2]" in hx and "\tconfiguration = My-Engine-v1-2" in hx.replace("\t\t", "\t")
    assert "@name = Bell-Model-8760" in hx
    assert "%title = Bell (Model) 8760" in hx and "%manufacturer = Bell / / Textron" in hx
    assert "%description = Line one see http:/ /example.com (x)" in hx
    assert "\t\t\tdescription = picker / / text\n" in hx
    _iss = export_issues(hostile, res)
    assert any("exported as 'My-Engine-v1-2'" in i for i in _iss), _iss
    assert any("exported as 'Bell-Model-8760'" in i for i in _iss), _iss
    # no value line keeps a '//' (it would start a comment mid-value)
    assert not any("//" in ln for ln in hx.splitlines()
                   if "=" in ln and not ln.lstrip().startswith("//")), hx

    # --- model variants: the XLR-11's RM-5 model on a clone and on the host part.
    xlr = EngineDesign(host_model_engine_type="XLR11", output_mode="new_part_standalone",
                       config_name="XLR11-Long", new_part_name="XLR11 Long",
                       host_model_variants={"model": "rm5"}, tech_node="orbitalRocketry1956")
    xr = xlr.compute()
    xs = render_cfg(xlr, xr)
    assert _balanced(xs)
    assert "+PART[ROE-XLR11]:" in xs
    assert ("@PART[XLR11-Long]:NEEDS[RealismOverhaul&RealFuels&B9PartSwitch]:"
            "BEFORE[RealismOverhaulEnginesPost]") in xs
    assert "\t\t\t!LinkB9PSModule[model],* {}\n\t\t\tLinkB9PSModule[model]\n\t\t\t{\n\t\t\t\tsubtype = rm5\n" in xs
    assert "variant model=rm5" in xs
    xa = render_cfg(xlr, xr, output_mode="additional_config")
    assert "@PART[ROE-XLR11]:NEEDS[RealismOverhaul&RealFuels&B9PartSwitch]" in xa
    bad = export_issues(xlr, xr, variants={"model": "rm9"})
    assert any("isn't a 'model' subtype" in i for i in bad), bad
    from .. import catalog as _cat
    h5, src5, _ = _cat.host_native_height_m("XLR11", "", {"model": "rm5"})
    h3, _, _ = _cat.host_native_height_m("XLR11", "", {"model": "rm3"})
    assert h5 > h3 and "rm5" in src5, (h5, h3, src5)
    # Several parts per engineType: the chosen one is cloned.
    lr = EngineDesign(host_model_engine_type="LR105", output_mode="new_part_standalone",
                      host_model_part="ROE-LR105_2", host_model_variants={"nozzle": "NA6"},
                      config_name="LR105-X")
    lrt = render_cfg(lr, res)
    assert "+PART[ROE-LR105_2]:" in lrt and "subtype = NA6" in lrt

    try:
        render_cfg(base, res, "X", output_mode="bogus")
        raise AssertionError("expected ValueError for bad output_mode")
    except ValueError:
        pass

    # Explicit "ablative" cooling on an ablative liner: the resolved method
    # drives the char-consumption ratedBurnTime, so tested ~ rated (the
    # "ablative, no extra time" pattern), and the header names the method.
    abl = EngineDesign(host_model_engine_type="F1", material_key="ablative_phenolic",
                        chamber_cooling_method="ablative")
    abl_res = abl.compute()
    e = render_cfg(abl, abl_res, "AblTest-1M", output_mode="additional_config")
    assert "Chamber cooling: ablative (explicit)" in e
    # ...while "ablative" on a copper (regen-spec) liner is physically meaningless
    # and HARD-BLOCKED (materials.allowed_cooling_methods): it runs regen, and the
    # header says so rather than claiming an explicit choice.
    cu_blk = EngineDesign(host_model_engine_type="F1", material_key="narloy_z",
                           chamber_cooling_method="ablative")
    e_cu = render_cfg(cu_blk, cu_blk.compute(), "AblTest-2M", output_mode="additional_config")
    assert "Chamber cooling: regenerative (material-default - explicit ablative BLOCKED)" in e_cu
    import re as _re
    _rt = int(_re.search(r"ratedBurnTime = (\d+)", e).group(1))
    _tt = int(_re.search(r"testedBurnTime = (\d+)", e).group(1))
    assert abs(_tt - _rt) <= max(2, 0.25 * _rt), (_rt, _tt)   # ~equal, not the 6-17x regen margin

    # Dump-cooled nozzle extension: the header names the dump-cooled slice.
    dmp = EngineDesign(host_model_engine_type="F1", propellant_pair="LOX/LH2", mixture_ratio=5.5,
                        chamber_pressure_pa=11.0e6, expansion_ratio=45.0, cycle="gas_generator",
                        nozzle_type="bell", bell_percent_length=80.0, material_key="narloy_z",
                        nozzle_cooling_method="dump", regen_nozzle_end_eps=45.0,
                        target_vac_thrust_n=1_140_000.0)
    dmp_res = dmp.compute()
    f = render_cfg(dmp, dmp_res, "DumpTest-1M", output_mode="additional_config")
    assert "Nozzle cooling: dump (explicit)" in f
    assert "Dump-cooled nozzle slice:" in f and "Isp penalty" in f

    # New pairs (2026-10-15): every dropdown pair has RF resources, and the RF-density
    # volume ratios reproduce real RO configs exactly (RD-253, Merlin 1D+, RD-119).
    from ..physics.combustion import available_pairs
    assert all(p in _RF_PROPELLANTS for p in available_pairs()), "pair without RF resources"
    for pair, mr, want_fuel in (("N2O4/UDMH", 2.67, 0.4042), ("LOX/RP-1 (subcooled)", 2.36, 0.3877),
                                ("LOX/UDMH", 1.49, 0.4919), ("MON-3/MMH", 1.65, 0.4973),
                                ("MON-3/MMH", 1.9, 0.4621), ("MON-10/MMH", 1.5, 0.5224)):
        assert abs(_propellant_ratios(pair, mr)[0] - want_fuel) < 5e-5, (pair, _propellant_ratios(pair, mr))
    for pair, mr, fuel, ox in (("LOX/UDMH", 1.5, "UDMH", "LqdOxygen"), ("N2O4/UDMH", 2.67, "UDMH", "NTO"),
                               ("LOX/RP-1 (subcooled)", 2.36, "CooledRP-1", "CooledLqdOxygen"),
                               ("MON-3/MMH", 1.65, "MMH", "MON3"), ("MON-10/MMH", 1.5, "MMH", "MON10"),
                               ("MON-25/MMH", 1.65, "MMH", "MON25")):
        npd = EngineDesign(host_model_engine_type="F1", propellant_pair=pair, mixture_ratio=mr,
                           chamber_pressure_pa=10.0e6, expansion_ratio=25.0)
        g = render_cfg(npd, npd.compute(), "PairTest-1M", output_mode="additional_config")
        assert _balanced(g), pair
        assert f"name = {fuel}\n" in g and f"name = {ox}\n" in g, pair

    print("cfg_writer.py self-checks: OK")
