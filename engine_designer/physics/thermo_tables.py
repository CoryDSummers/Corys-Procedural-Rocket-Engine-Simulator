"""Runtime reader for the baked thermophysical property tables.

The tables in ``physics/property_data/`` are GENERATED - by the kept script
``tools/property_tables/generate_property_tables.py`` (Cantera chemical
equilibrium + GRI-Mech transport for combustion gas; CoolProp for coolants).
Regenerate them there; never hand-edit the JSON. This module only
interpolates, so the tool keeps its numpy-only runtime.

Combustion gas (per bipropellant pair, grid = chamber pressure x mixture ratio,
bilinear in (MR, ln Pc)):
    ``gas_state(pair, mr, pc_pa)`` -> dict with tc_k, m_molar, cp_frozen_j_kgk,
    gamma_frozen, cp_equilibrium_j_kgk, gamma_s, mu_pa_s, k_frozen_w_mk,
    pr_frozen, cstar_ms, plus ``mr_clamped`` / ``pc_clamped`` flags (inputs
    outside the grid are clamped to its edge - reported, never silent).
    Returns None for a pair with no table (the monopropellants).
    ``isp_vac_ideal_s(pair, mr, pc_pa, eps, frozen=False)`` -> (ideal vacuum
    Isp [s], eps_clamped): the generator's shifting-equilibrium (or, with
    frozen=True, frozen-composition) expansion, bilinear in (MR, ln Pc) at each
    tabulated area ratio, then monotone-cubic (PCHIP) in ln eps. The
    performance path's ideal thrust coefficient is this x g0 / c*.

Coolant (per pair's fuel, grid = pressure x temperature, bilinear in (T, ln P)):
    ``coolant_state(pair, t_k, p_pa)`` -> dict with rho_kg_m3, cp_j_kgk,
    mu_pa_s, k_w_mk, h_j_kg (+ clamp flags), or None for a pair with no table.
    ``coolant_temperature_from_enthalpy(pair, h_j_kg, p_pa)`` inverts h(T) at
    fixed pressure (monotonic) - what an enthalpy-based coolant march needs
    across the supercritical H2 / CH4 cp peak, where cp*dT is badly wrong.

Saturation (per PUMPED PROPELLANT - "LOX", "LH2", "CH4", "RP-1" - not per pair;
the two-phase dome, triple point .. 0.98 Tc):
    ``saturation(propellant, t_k)`` -> dict with p_sat_pa, rho_l_kg_m3,
    rho_v_kg_m3, h_fg_j_kg (+ ``t_clamped``, ``surrogate``), or None for a
    propellant with no table (N2O4 / MMH / UDMH / N2H4 / H2O2 - not in CoolProp).
    ln p_sat is interpolated linearly in 1/T (Clausius-Clapeyron makes that
    nearly straight), the densities and h_fg linearly in T.
    ``saturation_temperature(propellant, p_pa)`` inverts p_sat(T). What a pump
    NPSH / cavitation model needs; RP-1 is the n-dodecane SURROGATE.
"""
from __future__ import annotations

import functools
import json
import math
import os

import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "property_data")
GAS_FILE = os.path.join(DATA_DIR, "combustion_equilibrium.json")
COOLANT_FILE = os.path.join(DATA_DIR, "coolant_properties.json")
SATURATION_FILE = os.path.join(DATA_DIR, "saturation_properties.json")

GAS_KEYS = ("tc_k", "m_molar", "cp_frozen_j_kgk", "gamma_frozen", "cp_equilibrium_j_kgk",
            "gamma_s", "mu_pa_s", "k_frozen_w_mk", "pr_frozen", "cstar_ms")
COOLANT_KEYS = ("rho_kg_m3", "cp_j_kgk", "mu_pa_s", "k_w_mk", "h_j_kg")
SATURATION_KEYS = ("rho_l_kg_m3", "rho_v_kg_m3", "h_fg_j_kg")   # + p_sat_pa (log-interpolated)


@functools.lru_cache(maxsize=None)
def _gas_db():
    if not os.path.exists(GAS_FILE):
        return {}
    with open(GAS_FILE) as f:
        raw = json.load(f)
    out = {}
    for pair, t in raw["pairs"].items():
        tab = dict(mr=np.asarray(t["mr"], float),
                   lnp=np.log(np.asarray(t["pc_mpa"], float) * 1e6),
                   **{k: np.asarray(t[k], float) for k in GAS_KEYS})
        for src, dst in (("isp_vac_s_by_eps", "isp"), ("isp_vac_frozen_s_by_eps", "isp_frozen"),
                         ("pe_over_pc_by_eps", "lnpe")):
            if src in t:
                eps = sorted(t[src], key=float)
                tab[dst + "_lneps"] = np.log(np.array([float(e) for e in eps]))
                arr = np.asarray([t[src][e] for e in eps], float)          # [eps][pc][mr]
                tab[dst] = np.log(arr) if dst == "lnpe" else arr
        out[pair] = tab
    return out


@functools.lru_cache(maxsize=None)
def _coolant_db():
    if not os.path.exists(COOLANT_FILE):
        return {}
    with open(COOLANT_FILE) as f:
        raw = json.load(f)
    out = {}
    for pair, t in raw["coolants"].items():
        tab = dict(t=np.asarray(t["t_k"], float),
                   lnp=np.log(np.asarray(t["p_mpa"], float) * 1e6),
                   fluid=t["fluid"], surrogate=t["surrogate"],
                   t_crit=t["critical_t_k"], p_crit=t["critical_p_pa"])
        for k in COOLANT_KEYS:
            a = np.array([[np.nan if v is None else v for v in row] for row in t[k]], float)
            tab[k] = a
        out[pair] = tab
    return out


@functools.lru_cache(maxsize=None)
def _saturation_db():
    if not os.path.exists(SATURATION_FILE):
        return {}
    with open(SATURATION_FILE) as f:
        raw = json.load(f)
    out = {}
    for prop, t in raw["propellants"].items():
        tk = np.asarray(t["t_k"], float)
        out[prop] = dict(t=tk, lnp=np.log(np.asarray(t["p_sat_pa"], float)),
                         fluid=t["fluid"], surrogate=t["surrogate"],
                         nbp=t["normal_boiling_t_k"],
                         **{k: np.asarray(t[k], float) for k in SATURATION_KEYS})
    return out


def saturation_meta():
    """Saturation-table provenance dict, or {} if the table is absent."""
    if not os.path.exists(SATURATION_FILE):
        return {}
    with open(SATURATION_FILE) as f:
        return json.load(f)["meta"]


def meta():
    """(gas meta, coolant meta) provenance dicts, or ({}, {}) if tables are absent."""
    g = c = {}
    if os.path.exists(GAS_FILE):
        with open(GAS_FILE) as f:
            g = json.load(f)["meta"]
    if os.path.exists(COOLANT_FILE):
        with open(COOLANT_FILE) as f:
            c = json.load(f)["meta"]
    return g, c


def has_gas_table(pair):
    return pair in _gas_db()


def has_coolant_table(pair):
    return pair in _coolant_db()


def has_saturation(propellant):
    return propellant in _saturation_db()


def _bracket(grid, x):
    """(i, w, clamped): grid[i]*(1-w) + grid[i+1]*w == clamp(x)."""
    n = len(grid)
    if n == 1:
        return 0, 0.0, x != grid[0]
    clamped = x < grid[0] or x > grid[-1]
    xc = min(max(x, grid[0]), grid[-1])
    i = int(np.searchsorted(grid, xc, side="right") - 1)
    i = min(max(i, 0), n - 2)
    w = (xc - grid[i]) / (grid[i + 1] - grid[i])
    return i, w, clamped


def _bilinear(arr, i, wi, j, wj):
    a00, a01 = arr[i, j], arr[i, j + 1]
    a10, a11 = arr[i + 1, j], arr[i + 1, j + 1]
    return ((1 - wi) * ((1 - wj) * a00 + wj * a01) + wi * ((1 - wj) * a10 + wj * a11))


def gas_state(pair, mr, pc_pa):
    tab = _gas_db().get(pair)
    if tab is None:
        return None
    i, wi, pc_cl = _bracket(tab["lnp"], math.log(max(pc_pa, 1.0)))
    j, wj, mr_cl = _bracket(tab["mr"], float(mr))
    out = {k: float(_bilinear(tab[k], i, wi, j, wj)) for k in GAS_KEYS}
    out["mr_clamped"] = bool(mr_cl)
    out["pc_clamped"] = bool(pc_cl)
    out["mr_range"] = (float(tab["mr"][0]), float(tab["mr"][-1]))
    return out


def _pchip(xs, ys, x):
    """Monotone piecewise-cubic Hermite (Fritsch-Carlson) interpolation of
    (xs, ys) at scalar x inside [xs[0], xs[-1]] - numpy only."""
    n = len(xs)
    if n == 1:
        return float(ys[0])
    h = np.diff(xs)
    d = np.diff(ys) / h
    m = np.zeros(n)
    m[0], m[-1] = d[0], d[-1]
    for k in range(1, n - 1):
        if d[k - 1] * d[k] > 0:
            w1, w2 = 2 * h[k] + h[k - 1], h[k] + 2 * h[k - 1]
            m[k] = (w1 + w2) / (w1 / d[k - 1] + w2 / d[k])
    i = int(min(max(np.searchsorted(xs, x, side="right") - 1, 0), n - 2))
    t = (x - xs[i]) / h[i]
    h00, h10 = 2 * t**3 - 3 * t**2 + 1, t**3 - 2 * t**2 + t
    h01, h11 = -2 * t**3 + 3 * t**2, t**3 - t**2
    return float(h00 * ys[i] + h10 * h[i] * m[i] + h01 * ys[i + 1] + h11 * h[i] * m[i + 1])


def isp_vac_ideal_s(pair, mr, pc_pa, eps, frozen=False):
    """(ideal vacuum Isp [s], eps_clamped) at area ratio eps - see the module
    docstring. None for a pair without a table (or without that column)."""
    tab = _gas_db().get(pair)
    key = "isp_frozen" if frozen else "isp"
    if tab is None or key not in tab:
        return None
    i, wi, _ = _bracket(tab["lnp"], math.log(max(pc_pa, 1.0)))
    j, wj, _ = _bracket(tab["mr"], float(mr))
    ys = np.array([_bilinear(tab[key][k], i, wi, j, wj) for k in range(tab[key].shape[0])])
    xs = tab[key + "_lneps"]
    le = math.log(max(float(eps), 1e-9))
    clamped = le < xs[0] - 1e-12 or le > xs[-1] + 1e-12
    return _pchip(xs, ys, min(max(le, xs[0]), xs[-1])), bool(clamped)


def pe_over_pc_at_eps(pair, mr, pc_pa, eps):
    """(exit static / chamber pressure, eps_clamped) of the shifting-
    equilibrium expansion to area ratio eps: bilinear in (MR, ln Pc) on
    ln(pe/pc), monotone PCHIP in ln eps. None without that column."""
    tab = _gas_db().get(pair)
    if tab is None or "lnpe" not in tab:
        return None
    i, wi, _ = _bracket(tab["lnp"], math.log(max(pc_pa, 1.0)))
    j, wj, _ = _bracket(tab["mr"], float(mr))
    ys = np.array([_bilinear(tab["lnpe"][k], i, wi, j, wj) for k in range(tab["lnpe"].shape[0])])
    xs = tab["lnpe_lneps"]
    le = math.log(max(float(eps), 1e-9))
    clamped = le < xs[0] - 1e-12 or le > xs[-1] + 1e-12
    return math.exp(_pchip(xs, ys, min(max(le, xs[0]), xs[-1]))), bool(clamped)


def _coolant_interp(tab, key, t_k, p_pa):
    i, wi, p_cl = _bracket(tab["lnp"], math.log(max(p_pa, 1.0)))
    j, wj, t_cl = _bracket(tab["t"], float(t_k))
    v = _bilinear(tab[key], i, wi, j, wj)
    if not math.isfinite(v):
        # a CoolProp hole at one corner: fall back to the nearest finite corner
        corners = [(tab[key][ii, jj], abs(ii - i - wi) + abs(jj - j - wj))
                   for ii in (i, i + 1) for jj in (j, j + 1)]
        finite = [c for c in corners if math.isfinite(c[0])]
        v = min(finite, key=lambda c: c[1])[0] if finite else float("nan")
    return float(v), p_cl, t_cl


def coolant_state(pair, t_k, p_pa):
    tab = _coolant_db().get(pair)
    if tab is None:
        return None
    out = {}
    p_cl = t_cl = False
    for k in COOLANT_KEYS:
        out[k], p_cl, t_cl = _coolant_interp(tab, k, t_k, p_pa)
    out["t_clamped"] = bool(t_cl)
    out["p_clamped"] = bool(p_cl)
    out["fluid"] = tab["fluid"]
    out["surrogate"] = tab["surrogate"]
    return out


def coolant_column(pair, p_pa):
    """Every coolant property on the table's full temperature grid at ONE
    pressure (linear in ln P between the bracketing isobars; CoolProp holes
    filled by linear interpolation along T). Returns dict(t_k, rho_kg_m3,
    cp_j_kgk, mu_pa_s, k_w_mk, h_j_kg) of 1-D arrays, or None - what a coolant
    march needs to evaluate properties with plain np.interp calls."""
    tab = _coolant_db().get(pair)
    if tab is None:
        return None
    i, wi, _ = _bracket(tab["lnp"], math.log(max(p_pa, 1.0)))
    out = {"t_k": tab["t"]}
    for k in COOLANT_KEYS:
        lo, hi = tab[k][i], tab[k][min(i + 1, len(tab["lnp"]) - 1)]
        col = (1.0 - wi) * lo + wi * hi
        bad = ~np.isfinite(col)
        if bad.any():
            # fall back to the finite isobar, then fill any remaining holes along T
            col = np.where(bad & np.isfinite(lo), lo, col)
            col = np.where(~np.isfinite(col) & np.isfinite(hi), hi, col)
            good = np.isfinite(col)
            col = np.interp(tab["t"], tab["t"][good], col[good])
        out[k] = col
    # enthalpy must be monotonic in T for the inversion (it is physically;
    # guard against interpolation round-off across the pseudo-critical kink)
    out["h_j_kg"] = np.maximum.accumulate(out["h_j_kg"])
    return out


def coolant_temperature_from_enthalpy(pair, h_j_kg, p_pa):
    """Temperature at which h(T, p) == h_j_kg, by bisection on the (monotonic)
    interpolated enthalpy; clamps to the table's T range."""
    tab = _coolant_db().get(pair)
    if tab is None:
        return None
    lo, hi = float(tab["t"][0]), float(tab["t"][-1])
    h_lo = _coolant_interp(tab, "h_j_kg", lo, p_pa)[0]
    h_hi = _coolant_interp(tab, "h_j_kg", hi, p_pa)[0]
    if h_j_kg <= h_lo:
        return lo
    if h_j_kg >= h_hi:
        return hi
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if _coolant_interp(tab, "h_j_kg", mid, p_pa)[0] < h_j_kg:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def saturation(propellant, t_k):
    """Saturated-liquid / vapor state of a pumped propellant at temperature t_k
    (clamped to the table's triple-point .. 0.98 Tc range, flagged)."""
    tab = _saturation_db().get(propellant)
    if tab is None:
        return None
    t = tab["t"]
    tc = min(max(float(t_k), float(t[0])), float(t[-1]))
    inv = 1.0 / t   # decreasing - flip for np.interp
    out = {"p_sat_pa": math.exp(float(np.interp(1.0 / tc, inv[::-1], tab["lnp"][::-1])))}
    for k in SATURATION_KEYS:
        out[k] = float(np.interp(tc, t, tab[k]))
    out["t_clamped"] = tc != float(t_k)
    out["surrogate"] = tab["surrogate"]
    return out


def saturation_temperature(propellant, p_pa):
    """Temperature at which p_sat(T) == p_pa (p_sat rises monotonically along the
    dome); clamped to the table's range. None for a propellant with no table."""
    tab = _saturation_db().get(propellant)
    if tab is None:
        return None
    lnp = min(max(math.log(p_pa), float(tab["lnp"][0])), float(tab["lnp"][-1]))
    inv = float(np.interp(lnp, tab["lnp"], 1.0 / tab["t"]))
    return 1.0 / inv


if __name__ == "__main__":
    gdb, cdb = _gas_db(), _coolant_db()
    assert gdb, f"missing {GAS_FILE} - run tools/property_tables/generate_property_tables.py"
    assert cdb, f"missing {COOLANT_FILE}"
    gm, cm = meta()
    print(f"gas tables: {sorted(gdb)}  (cantera {gm.get('cantera_version')}, {gm.get('date')})")
    print(f"coolant tables: {sorted(cdb)}  (CoolProp {cm.get('coolprop_version')})")
    # 1. grid points reproduce exactly
    for pair, t in gdb.items():
        for ii in (0, len(t["lnp"]) - 1):
            for jj in (0, len(t["mr"]) - 1):
                s = gas_state(pair, t["mr"][jj], math.exp(t["lnp"][ii]))
                assert abs(s["tc_k"] - t["tc_k"][ii, jj]) < 1e-6 * t["tc_k"][ii, jj], pair
    # 2. mass-balance ceiling the OLD hand table violated: fuel-rich LOX/LH2 makes
    #    exactly 1 kmol product per kmol H2 fed (H2O replaces H2 1:1; dissociation
    #    only adds moles), so M <= M_H2 * (1 + MR) (e.g. old table: 10.0 @ MR 3.5 > 9.07)
    for mr in (3.0, 3.5, 4.0, 4.5, 5.0, 5.5):
        m = gas_state("LOX/LH2", mr, 7e6)["m_molar"]
        assert m <= 2.01588 * (1.0 + mr) + 1e-6, (mr, m)
    # 3. LOX/LH2 gamma falls toward stoichiometric (the old table had it rising)
    gs = [gas_state("LOX/LH2", mr, 7e6)["gamma_frozen"] for mr in (4.0, 5.0, 6.0, 7.0)]
    assert all(a > b for a, b in zip(gs, gs[1:])), gs
    # 4. clamps are reported
    assert gas_state("LOX/LH2", 20.0, 7e6)["mr_clamped"]
    assert not gas_state("LOX/LH2", 6.0, 7e6)["mr_clamped"]
    assert gas_state("Hydrazine", 1.0, 2e6) is None
    # 5. coolant sanity: supercritical H2 at 50 K / 20 MPa is dense-fluid, at 300 K gas-like
    c50 = coolant_state("LOX/LH2", 50.0, 20e6)
    c300 = coolant_state("LOX/LH2", 300.0, 20e6)
    assert 40.0 < c50["rho_kg_m3"] < 80.0 and 10.0 < c300["rho_kg_m3"] < 20.0, (c50, c300)
    # 6. enthalpy inversion round-trips
    for pair, (t, p) in {"LOX/LH2": (123.0, 15e6), "LOX/CH4": (211.0, 12e6),
                         "LOX/RP-1": (377.0, 10e6)}.items():
        h = coolant_state(pair, t, p)["h_j_kg"]
        t2 = coolant_temperature_from_enthalpy(pair, h, p)
        assert abs(t2 - t) < 0.05, (pair, t, t2)
    # 7. ideal Isp: grid points reproduce, Isp rises with eps, frozen <= shifting,
    #    and the eps interpolation sits between its neighbours
    for pair, t in gdb.items():
        if "isp" not in t:
            continue
        for kk, le in enumerate(t["isp_lneps"]):
            v, cl = isp_vac_ideal_s(pair, t["mr"][2], math.exp(t["lnp"][3]), math.exp(le))
            assert abs(v - t["isp"][kk, 3, 2]) < 1e-9 and not cl, (pair, kk)
        for mr in (t["mr"][1], t["mr"][-2]):
            for pc in (1e6, 7e6, 20e6):
                es = np.exp(np.linspace(t["isp_lneps"][0], t["isp_lneps"][-1], 40))
                sh = [isp_vac_ideal_s(pair, mr, pc, e)[0] for e in es]
                assert all(b >= a for a, b in zip(sh, sh[1:])), (pair, mr, pc)
                if "isp_frozen" in t:
                    fz = [isp_vac_ideal_s(pair, mr, pc, e, frozen=True)[0] for e in es]
                    assert all(f <= x + 1e-6 for f, x in zip(fz, sh)), (pair, mr, pc)
    assert isp_vac_ideal_s("LOX/LH2", 6.0, 7e6, 1000.0)[1]
    # 8. exit pressure ratio falls with eps and reproduces the grid
    for pair, t in gdb.items():
        if "lnpe" not in t:
            continue
        pes = [pe_over_pc_at_eps(pair, t["mr"][2], 7e6, e)[0]
               for e in np.exp(np.linspace(t["lnpe_lneps"][0], t["lnpe_lneps"][-1], 40))]
        assert all(b < a for a, b in zip(pes, pes[1:])), pair
        v = pe_over_pc_at_eps(pair, t["mr"][2], math.exp(t["lnp"][3]), math.exp(t["lnpe_lneps"][4]))[0]
        assert abs(math.log(v) - t["lnpe"][4, 3, 2]) < 1e-9, pair
    assert isp_vac_ideal_s("Hydrazine", 1.0, 2e6, 20.0) is None
    # 9. saturation: every tabulated propellant boils at 1 atm at its NIST normal
    #    boiling point (O2 90.19, para-H2 20.27, CH4 111.67 K; n-dodecane ~489 K),
    #    p_sat / rho_v rise and rho_l fall along the dome, h_fg falls above the
    #    normal boiling point (para-H2's h_fg genuinely PEAKS at ~16.6 K, just above
    #    its 13.8 K triple point - real CoolProp behaviour, not a table error), the
    #    inverse round-trips, grid points reproduce, and storables report "no table"
    sdb = _saturation_db()
    assert sdb, f"missing {SATURATION_FILE}"
    nbp_ref = {"LOX": 90.19, "LH2": 20.27, "CH4": 111.67, "RP-1": 489.4}
    for prop, ref in nbp_ref.items():
        t_b = saturation_temperature(prop, 101325.0)
        assert abs(t_b - ref) < 0.1, (prop, t_b, ref)
        assert abs(saturation(prop, ref)["p_sat_pa"] / 101325.0 - 1.0) < 0.01, prop
        tab = sdb[prop]
        ts = np.linspace(tab["t"][0], tab["t"][-1], 50)
        st = [saturation(prop, x) for x in ts]
        for k, sign in (("p_sat_pa", 1), ("rho_v_kg_m3", 1), ("rho_l_kg_m3", -1), ("h_fg_j_kg", -1)):
            v = [s[k] for x, s in zip(ts, st) if k != "h_fg_j_kg" or x >= tab["nbp"]]
            assert all(sign * (b - a) > 0 for a, b in zip(v, v[1:])), (prop, k)
        for p in (2e4, 3e5, 2e6):
            if tab["lnp"][0] < math.log(p) < tab["lnp"][-1]:
                assert abs(saturation(prop, saturation_temperature(prop, p))["p_sat_pa"] / p - 1) < 1e-6
        kk = len(tab["t"]) // 2
        assert abs(math.log(saturation(prop, tab["t"][kk])["p_sat_pa"]) - tab["lnp"][kk]) < 1e-9
        assert saturation(prop, 1e4)["t_clamped"]
    assert saturation("N2O4", 293.0) is None and not has_saturation("MMH")
    assert sdb["RP-1"]["surrogate"] and not sdb["LOX"]["surrogate"]
    for prop in nbp_ref:
        s = saturation(prop, sdb[prop]["nbp"])
        print(f"  {prop:4s} NBP {sdb[prop]['nbp']:6.2f} K  rho_l {s['rho_l_kg_m3']:7.1f}  "
              f"rho_v {s['rho_v_kg_m3']:6.3f}  h_fg {s['h_fg_j_kg'] / 1e3:6.1f} kJ/kg")
    for pair in ("LOX/LH2", "LOX/CH4", "LOX/RP-1"):
        s = gas_state(pair, {"LOX/LH2": 6.0, "LOX/CH4": 3.55, "LOX/RP-1": 2.34}[pair], 10e6)
        print(f"  {pair:9s} Tc {s['tc_k']:6.0f} K  M {s['m_molar']:5.2f}  g_f {s['gamma_frozen']:.3f}"
              f"  g_s {s['gamma_s']:.3f}  cp_f {s['cp_frozen_j_kgk']:5.0f}  mu {s['mu_pa_s']:.2e}"
              f"  Pr_f {s['pr_frozen']:.3f}")
    print("ALL THERMO-TABLE CHECKS OK")
