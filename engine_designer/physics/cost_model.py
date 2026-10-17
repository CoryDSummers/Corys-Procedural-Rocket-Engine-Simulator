"""
CER-style engine cost estimate for the RP-1 career economy: the ABSOLUTE
per-unit engine `cost` and the R&D `entry_cost` of its engine config.

EXPORT-TIME ONLY - nothing here feeds EngineDesign.compute(), so no validate.py
spot check moves.

How RP-1 prices an engine (verified against RealFuels' source and RP-1's tree
files, 2026-10-15 - see engine_designer/README.md "Export"):
  * the PART carries the base `cost` (RP-1 TREE-Parts.cfg, per part name);
  * each RealFuels CONFIG's `cost` is a DELTA on top of it (TREE-Engines.cfg:
    H-1 part 392, configs +0 / +21 / +67; AJ10-153 is -62);
  * a CONFIG's entry cost comes ONLY from an ENTRYCOSTMODS row keyed by config
    name (a CONFIG-level `entryCost` is never read by RealFuels).
So `estimate_cost()["cost"]` is the absolute engine cost (= part + config delta)
and export/cfg_writer.py splits it: a standalone part gets it as its PART cost
(config delta 0); a CONFIG appended to a host gets `cost - host_part_cost()`.

CALIBRATION (Tier 2 - fitted to real data, wide scatter): a least-squares fit in
log space over every RealismOverhaul engine config that joins to an RP-1-priced
part (catalog/rp1_snapshot.json, 487 configs, solids/cold-gas excluded):

    ln(cost) = A + B ln(F_vac kN) + C_pf [pressure-fed] + C_class[propellant class]

RMS log residual 0.53 (one sigma ~ x1.7) - RP-1 prices also carry era,
heritage and gameplay balance this can't see. Trust the magnitude to within
~x2 and the trends (bigger -> pricier, hydrolox ~x3.9) more than any one number.
The self-test RE-FITS from the snapshot and fails if the frozen coefficients
drift, so a refreshed snapshot forces a deliberate update here.

On top of the fit, Tier-3 relative modifiers (neutral = 1.0, ordering only):
cycle complexity within pump-fed (GG = 1), chamber pressure vs the class's
typical Pc, the material / injector / turbopump / controller
`relative_cost_factor`s (damped), and clustering (n chambers of F/n each).

ENTRY COST (Tier 2/3): RP-1's ECM-Engines rows are almost all INCREMENTAL
(361 of 363 numeric rows name tech-transfer parents); their median ratio to the
config's absolute cost is 28 (IQR 11-63). entry_cost = 28 x cost x a Tier-3
cycle R&D factor. A clean-sheet engine with no ECM parents arguably deserves
more - the GUI lets the user override it.
"""
from . import controller_tech, injectors, materials, turbopump_tech

# --- fitted on catalog/rp1_snapshot.json (RP-1 @ 4055038, 2026-10-15) -----------
FIT_A = 3.085                  # ln(cost) intercept
FIT_B_THRUST = 0.480           # exponent on vacuum thrust [kN]
FIT_C_PRESSURE_FED = -0.099    # pressure-fed vs pump-fed
FIT_C_CLASS = {                # vs kerolox (0)
    "kerolox": 0.0,
    "hydrolox": 1.359,
    "methalox": 0.586,         # n = 13 - thin
    "storable": -0.205,
}
FIT_RMS_LOG = 0.526
# Our propellant pairs -> fit class. Monopropellants map onto "storable"
# (RP-1 has a single liquid-mono row - too thin to fit on its own; Tier 3).
PAIR_CLASS = {
    "LOX/RP-1": "kerolox",
    "LOX/LH2": "hydrolox",
    "LOX/CH4": "methalox",
    "N2O4/MMH": "storable",
    "Aerozine-50/NTO": "storable",
    "Hydrazine": "storable",
    "H2O2": "storable",
}

# --- Tier-3 relative modifiers (neutral 1.0) ------------------------------------
# Pump-fed cycle complexity relative to a gas generator; pressure-fed's own
# discount is the fitted FIT_C_PRESSURE_FED, so it is neutral here.
COST_BY_CYCLE = {
    "pressure_fed": 1.0,
    "gas_generator": 1.0,
    "tap_off": 1.1,
    "expander": 1.3,
    "electric_pump": 1.2,
    "frsc": 1.8,
    "orsc": 2.2,
    "ffsc": 2.6,
}
_CYCLE_FALLBACK = 1.0
PC_REF_PA = {"pump": 7.0e6, "pressure_fed": 1.5e6}   # "typical" Pc the fit implicitly averages
PC_COST_EXP = 0.30

ENTRY_COST_RATIO = 28.0        # median RP-1 ECM row / absolute engine cost
ENTRY_CYCLE_EXTRA = {
    "frsc": 1.5,
    "orsc": 2.0,
    "ffsc": 2.5,
    "expander": 1.3,
    "tap_off": 1.15,
    "electric_pump": 1.2,
}


def _blend(f):
    """Damp a relative_cost_factor around its neutral value 1.0 so an exotic
    material / injector / turbopump doesn't swing cost 2x on its own."""
    return 0.5 + 0.5 * f


def fitted_cost(thrust_vac_kn, propellant_class, pressure_fed):
    """The bare RP-1 fit: absolute engine cost for one chamber."""
    import math
    lnc = (FIT_A + FIT_B_THRUST * math.log(max(thrust_vac_kn, 0.01))
           + (FIT_C_PRESSURE_FED if pressure_fed else 0.0)
           + FIT_C_CLASS.get(propellant_class, 0.0))
    return math.exp(lnc)


def estimate_cost(design, result):
    """Return dict(cost, entry_cost) - integers, in RP-1 career funds.
    `cost` is the ABSOLUTE engine cost (part + config delta in RP-1 terms)."""
    from . import cycles
    pf = design.cycle == cycles.PRESSURE_FED
    chambers = max(1, int(getattr(design, "chamber_count", 1) or 1))
    f_kn = max(result.get("thrust_vac_n", design.target_vac_thrust_n), 1.0) / 1e3
    base = chambers * fitted_cost(f_kn / chambers, PAIR_CLASS.get(design.propellant_pair, "kerolox"), pf)

    mat = materials.MATERIALS[design.material_key].relative_cost_factor
    inj = injectors.INJECTORS[design.injector_type].relative_cost_factor
    tp = turbopump_tech.TURBOPUMP_TECHS[design.turbopump_tech_key].relative_cost_factor
    ctl = controller_tech.CONTROLLER_TECHS[design.controller_tech_key].relative_cost_factor
    pc_ref = PC_REF_PA["pressure_fed" if pf else "pump"]
    cost = (base
            * COST_BY_CYCLE.get(design.cycle, _CYCLE_FALLBACK)
            * (design.chamber_pressure_pa / pc_ref) ** PC_COST_EXP
            * _blend(mat) * _blend(inj) * _blend(tp) * _blend(ctl))
    entry = cost * ENTRY_COST_RATIO * ENTRY_CYCLE_EXTRA.get(design.cycle, 1.0)
    return {"cost": max(1, round(cost)), "entry_cost": max(1, round(entry))}


# --- re-fit from the snapshot (self-test / refresh aid) --------------------------

_SOLIDS = {"HTPB", "PBAN", "CTPB", "PSPC", "NGNC", "PUPE", "PBAA", "ANFA37"}
_STORABLE = {"NTO", "MON1", "MON3", "MON10", "MON25", "AK20", "AK27", "IRFNA-III",
             "IRFNA-IV", "IWFNA", "UDMH", "MMH", "Aerozine50"}


def _snapshot_class(props):
    s = {p.replace("Cooled", "") for p in props} - {"Helium", "Nitrogen", "ElectricCharge", "Water"}
    if not s or s & _SOLIDS:
        return None
    if "LqdHydrogen" in s:
        return "hydrolox"
    if "LqdMethane" in s:
        return "methalox"
    if "LqdOxygen" in s and s & {"RP-1", "Kerosene", "RG-1", "Syntin"}:
        return "kerolox"
    if len(s) == 1 and s & {"HTP", "Hydrazine"}:
        return "mono"
    if s & _STORABLE and "LqdOxygen" not in s:
        return "storable"
    return "other"


def snapshot_rows(snapshot=None):
    """[(config, thrust_kn, pressure_fed, class, absolute_cost, ecm_cost)] joined
    from catalog/rp1_snapshot.json."""
    if snapshot is None:
        from ..catalog import build_rp1_snapshot
        snapshot = build_rp1_snapshot.load()
    parts, types = snapshot.get("engine_parts", {}), snapshot.get("engine_types", {})
    rows = []
    for name, c in snapshot.get("configs", {}).items():
        cl = _snapshot_class(c["propellants"])
        names = [n for n in types.get(c["engine_type"], [])
                 if n in parts and parts[n].get("cost") is not None
                 and "EngineSolid" not in parts[n]["tags"]]
        if cl is None or not names or not c.get("max_thrust_kn") or c["max_thrust_kn"] <= 0:
            continue
        pc = sorted(parts[n]["cost"] for n in names)[len(names) // 2]
        absc = pc + (c.get("cost_delta") or 0)
        if absc > 0:
            rows.append((name, c["max_thrust_kn"], c["pressure_fed"], cl, absc, c.get("ecm_cost")))
    return rows


def refit(rows=None):
    """Least-squares re-fit of the FIT_* coefficients. Returns (coeffs, rms)."""
    import math
    import numpy as np
    rows = snapshot_rows() if rows is None else rows
    classes = ["hydrolox", "methalox", "storable", "mono", "other"]
    X = np.array([[1.0, math.log(r[1]), float(r[2])] + [1.0 if r[3] == k else 0.0 for k in classes]
                  for r in rows])
    y = np.array([math.log(r[4]) for r in rows])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    rms = float(np.sqrt(np.mean((y - X @ b) ** 2)))
    coeffs = {"A": b[0], "B": b[1], "pf": b[2]}
    coeffs.update({k: b[3 + i] for i, k in enumerate(classes)})
    return coeffs, rms, len(rows)


if __name__ == "__main__":
    import statistics
    from .design import EngineDesign

    # 1. The frozen coefficients still match a re-fit of the committed snapshot.
    co, rms, n = refit()
    print(f"  RP-1 fit over {n} configs: A {co['A']:.3f}  B {co['B']:.3f}  pf {co['pf']:+.3f}  "
          f"hydrolox {co['hydrolox']:+.3f}  methalox {co['methalox']:+.3f}  "
          f"storable {co['storable']:+.3f}  rms log {rms:.3f} (x{2.718281828 ** rms:.2f})")
    assert n > 400, n
    for key, frozen in (("A", FIT_A), ("B", FIT_B_THRUST), ("pf", FIT_C_PRESSURE_FED),
                        ("hydrolox", FIT_C_CLASS["hydrolox"]), ("methalox", FIT_C_CLASS["methalox"]),
                        ("storable", FIT_C_CLASS["storable"])):
        assert abs(co[key] - frozen) < 0.01, (key, co[key], frozen, "snapshot changed - re-freeze")
    assert abs(rms - FIT_RMS_LOG) < 0.01, rms

    # 2. Real anchors: the bare fit lands within ~x2.5 of RP-1's own absolute cost.
    snap = {r[0]: r for r in snapshot_rows()}
    for cfg in ("H-1-200K", "LR87-AJ-3", "RL10A-3-3A", "AJ10-118K", "LR105-NA-6", "Merlin1D"):
        _, f, pf, cl, absc, _ = snap[cfg]
        est = fitted_cost(f, cl, pf)
        print(f"    {cfg:12s} {f:7.0f} kN {cl:9s} RP-1 {absc:6.0f}  fit {est:6.0f}  ({est / absc:.2f}x)")
        assert 0.4 < est / absc < 2.5, (cfg, est, absc)

    # 3. Entry ratio = median ECM / absolute cost over the numeric ECM rows.
    ratios = [r[5] / r[4] for r in snap.values() if r[5] and r[5] > 1]
    med = statistics.median(ratios)
    print(f"  ECM / absolute cost: median {med:.1f} over {len(ratios)} rows (frozen {ENTRY_COST_RATIO})")
    assert abs(med - ENTRY_COST_RATIO) < 1.0, med

    def c(pair, cycle, **kw):
        d = EngineDesign(propellant_pair=pair, cycle=cycle, **kw)
        return estimate_cost(d, d.compute())

    # 4. Design-level envelopes (RP-1 scale now: H-1 part 392 + delta, F-1 1855).
    kerolox_gg = c("LOX/RP-1", "gas_generator", chamber_pressure_pa=8e6,
                    target_vac_thrust_n=1.4e6)          # H3/H4-class
    big_orsc = c("LOX/RP-1", "orsc", chamber_pressure_pa=25e6, mixture_ratio=2.7,
                  target_vac_thrust_n=4.0e6)
    thruster = c("N2O4/MMH", "pressure_fed", chamber_pressure_pa=0.8e6,
                  injector_type="impinging", target_vac_thrust_n=1.5e4)
    hydrolox = c("LOX/LH2", "gas_generator", chamber_pressure_pa=8e6, mixture_ratio=5.5,
                  target_vac_thrust_n=1.0e6)
    print(f"  kerolox GG (~1.4 MN):  cost {kerolox_gg['cost']:>6}  entryCost {kerolox_gg['entry_cost']:>8}")
    print(f"  big ORSC   (~4 MN):    cost {big_orsc['cost']:>6}  entryCost {big_orsc['entry_cost']:>8}")
    print(f"  hydrolox GG (~1 MN):   cost {hydrolox['cost']:>6}  entryCost {hydrolox['entry_cost']:>8}")
    print(f"  small thruster:        cost {thruster['cost']:>6}  entryCost {thruster['entry_cost']:>8}")
    assert 300 <= kerolox_gg["cost"] <= 1500, kerolox_gg
    assert 5000 <= kerolox_gg["entry_cost"] <= 60000, kerolox_gg
    assert big_orsc["cost"] > kerolox_gg["cost"] > thruster["cost"]
    assert big_orsc["entry_cost"] > kerolox_gg["entry_cost"] > thruster["entry_cost"]
    assert hydrolox["cost"] > kerolox_gg["cost"]
    assert 20 <= thruster["cost"] <= 200, thruster

    # 5. Monotonicity: bigger / higher-Pc / pricier-material -> higher cost.
    base = c("LOX/RP-1", "gas_generator", chamber_pressure_pa=8e6, target_vac_thrust_n=1e6)
    big = c("LOX/RP-1", "gas_generator", chamber_pressure_pa=8e6, target_vac_thrust_n=4e6)
    hipc = c("LOX/RP-1", "gas_generator", chamber_pressure_pa=16e6, target_vac_thrust_n=1e6)
    exotic = c("LOX/RP-1", "gas_generator", chamber_pressure_pa=8e6, target_vac_thrust_n=1e6,
                material_key="rhenium_iridium")
    assert big["cost"] > base["cost"] and hipc["cost"] > base["cost"]
    assert exotic["cost"] > base["cost"]

    print("cost_model.py self-checks: OK")
