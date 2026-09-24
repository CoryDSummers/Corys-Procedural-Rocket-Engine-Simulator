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

Coolant (per pair's fuel, grid = pressure x temperature, bilinear in (T, ln P)):
    ``coolant_state(pair, t_k, p_pa)`` -> dict with rho_kg_m3, cp_j_kgk,
    mu_pa_s, k_w_mk, h_j_kg (+ clamp flags), or None for a pair with no table.
    ``coolant_temperature_from_enthalpy(pair, h_j_kg, p_pa)`` inverts h(T) at
    fixed pressure (monotonic) - what an enthalpy-based coolant march needs
    across the supercritical H2 / CH4 cp peak, where cp*dT is badly wrong.
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

GAS_KEYS = ("tc_k", "m_molar", "cp_frozen_j_kgk", "gamma_frozen", "cp_equilibrium_j_kgk",
            "gamma_s", "mu_pa_s", "k_frozen_w_mk", "pr_frozen", "cstar_ms")
COOLANT_KEYS = ("rho_kg_m3", "cp_j_kgk", "mu_pa_s", "k_w_mk", "h_j_kg")


@functools.lru_cache(maxsize=None)
def _gas_db():
    if not os.path.exists(GAS_FILE):
        return {}
    with open(GAS_FILE) as f:
        raw = json.load(f)
    out = {}
    for pair, t in raw["pairs"].items():
        out[pair] = dict(mr=np.asarray(t["mr"], float),
                         lnp=np.log(np.asarray(t["pc_mpa"], float) * 1e6),
                         **{k: np.asarray(t[k], float) for k in GAS_KEYS})
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
    for pair in ("LOX/LH2", "LOX/CH4", "LOX/RP-1"):
        s = gas_state(pair, {"LOX/LH2": 6.0, "LOX/CH4": 3.55, "LOX/RP-1": 2.34}[pair], 10e6)
        print(f"  {pair:9s} Tc {s['tc_k']:6.0f} K  M {s['m_molar']:5.2f}  g_f {s['gamma_frozen']:.3f}"
              f"  g_s {s['gamma_s']:.3f}  cp_f {s['cp_frozen_j_kgk']:5.0f}  mu {s['mu_pa_s']:.2e}"
              f"  Pr_f {s['pr_frozen']:.3f}")
    print("ALL THERMO-TABLE CHECKS OK")
