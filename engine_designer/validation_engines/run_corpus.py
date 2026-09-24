"""Validation-engine corpus runner.

Every ``*.json`` under ``validation_engines/engines/`` (real engines, each with a
top-level ``"reference"`` block of cited real data) and ``validation_engines/
user_designs/`` (frozen copies of Cory's own saved projects, no reference block)
is a normal engine_designer project file (``gui/project_io`` schema) - open any of
them in the GUI with File > Open.

Modes::

    python3 -m engine_designer.validation_engines.run_corpus            # == --check
    python3 -m engine_designer.validation_engines.run_corpus --snapshot # (re)write golden/
    python3 -m engine_designer.validation_engines.run_corpus --check    # bit-identical vs golden
    python3 -m engine_designer.validation_engines.run_corpus --report   # reference vs model +
                                                                        # self-consistency table

``--check`` is the refactor safety net: a pure restructuring of the physics must
reproduce every golden result dict EXACTLY (floats compared by repr). A deliberate
physics change re-snapshots golden only alongside a before/after delta table
(``--report --diff``) recorded in ``engine_designer/COOLING_AUDIT.md``.

The ``reference`` block format (all entries optional)::

    "reference": {
      "source": "free text",
      "metrics": {
        "<metric>": {"value": 7.0, "lo": 5.0, "hi": 9.0, "unit": "MW/m2",
                     "kind": "validated" | "plausibility", "cite": "[Tag p.NN]"}
      }
    }

where ``<metric>`` is a key of ``METRICS`` below. ``--report`` flags a metric
outside [lo, hi] (``value`` alone is shown for comparison but never gates).
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINES_DIR = os.path.join(HERE, "engines")
USER_DIR = os.path.join(HERE, "user_designs")
GOLDEN_DIR = os.path.join(HERE, "golden")


# --------------------------------------------------------------------------
# metric extraction (tolerant of missing keys so it survives refactors)
# --------------------------------------------------------------------------
def _get(r, *path):
    cur = r
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    if cur is None:
        return None
    try:
        return float(cur)
    except (TypeError, ValueError):
        return None


def _scaled(v, k):
    return None if v is None else v * k


METRICS = {
    # name: (label, unit, extractor)
    "isp_vac_s": ("Isp vac", "s", lambda r: _get(r, "isp_vac_engine_s")),
    "isp_sl_s": ("Isp SL", "s", lambda r: _get(r, "isp_sl_engine_s")),
    "thrust_vac_kn": ("F vac", "kN", lambda r: _scaled(_get(r, "thrust_vac_n"), 1e-3)),
    "tc_k": ("Tc", "K", lambda r: _get(r, "tc_k")),
    "q_throat_mw_m2": ("q throat", "MW/m2",
                       lambda r: _scaled(_get(r, "cooling", "q_throat_w_m2"), 1e-6)),
    "hg_throat_kw_m2k": ("h_g throat", "kW/m2K",
                         lambda r: _scaled(_get(r, "cooling", "hg_throat_w_m2k"), 1e-3)),
    "t_wg_throat_k": ("T_wg throat", "K", lambda r: _get(r, "cooling", "t_wg_throat_k")),
    "peak_wall_temp_k": ("T_w peak", "K", lambda r: _get(r, "cooling", "peak_wall_temp_k")),
    "margin_ratio": ("margin", "x", lambda r: _get(r, "material_margin", "margin_ratio")),
    "wall_heat_mw": ("Q wall", "MW",
                     lambda r: _scaled(_get(r, "cooling", "wall_heat_total_w"), 1e-6)),
    "coolant_dt_k": ("coolant dT", "K", lambda r: _get(r, "cooling", "coolant_delta_t_k")),
    "jacket_dp_mpa": ("jacket dP", "MPa",
                      lambda r: _scaled(_get(r, "cooling", "jacket_dp_pa"), 1e-6)),
    "coolant_v_throat_ms": ("v cool thr", "m/s",
                            lambda r: _get(r, "cooling", "coolant_velocity_throat_ms")),
    "regen_isp_bonus_pct": ("regen bonus", "%",
                            lambda r: _scaled(_get(r, "cooling", "regen_isp_bonus_fraction"), 100)),
    "dump_fraction_pct": ("dump frac", "%",
                          lambda r: _scaled(_get(r, "cooling", "dump_coolant_fraction"), 100)),
    "rated_burn_time_s": ("burn time", "s", lambda r: _get(r, "rated_burn_time_s")),
}


# --------------------------------------------------------------------------
# canonical serialisation for golden snapshots
# --------------------------------------------------------------------------
def _canon(obj):
    """Deterministic JSON-able form. Floats go through repr() so equality is exact."""
    if isinstance(obj, dict):
        return {str(k): _canon(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_canon(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return {"__nd__": [_canon(v) for v in obj.tolist()]}
    if isinstance(obj, (bool, np.bool_)):
        return bool(obj)
    if isinstance(obj, (int, np.integer)):
        return int(obj)
    if isinstance(obj, (float, np.floating)):
        return {"__f__": repr(float(obj))}
    if obj is None or isinstance(obj, str):
        return obj
    return {"__repr__": repr(obj)}


def _diff(a, b, path="", out=None, limit=25):
    if out is None:
        out = []
    if len(out) >= limit:
        return out
    if type(a) is not type(b):
        out.append(f"{path}: type {type(a).__name__} -> {type(b).__name__}")
    elif isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append(f"{path}/{k}: added")
            elif k not in b:
                out.append(f"{path}/{k}: removed")
            else:
                _diff(a[k], b[k], f"{path}/{k}", out, limit)
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append(f"{path}: len {len(a)} -> {len(b)}")
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                _diff(x, y, f"{path}[{i}]", out, limit)
    elif a != b:
        out.append(f"{path}: {a!r} -> {b!r}")
    return out


# --------------------------------------------------------------------------
def corpus_files():
    files = sorted(glob.glob(os.path.join(ENGINES_DIR, "*.json")))
    files += sorted(glob.glob(os.path.join(USER_DIR, "*.json")))
    return files


def _name(path):
    sub = os.path.basename(os.path.dirname(path))
    return f"{sub}/{os.path.splitext(os.path.basename(path))[0]}"


def _golden_path(path):
    sub = os.path.basename(os.path.dirname(path))
    return os.path.join(GOLDEN_DIR, sub, os.path.basename(path))


def load_reference(path):
    with open(path) as f:
        return json.load(f).get("reference") or {}


def compute(path):
    from engine_designer.gui.project_io import load_design
    return load_design(path).compute()


def snapshot(files):
    for p in files:
        g = _golden_path(p)
        os.makedirs(os.path.dirname(g), exist_ok=True)
        with open(g, "w") as f:
            json.dump(_canon(compute(p)), f, indent=0, sort_keys=True, allow_nan=True)
        print(f"snapshot  {_name(p)}")
    return True


def check(files):
    ok = True
    for p in files:
        g = _golden_path(p)
        if not os.path.exists(g):
            print(f"MISSING   {_name(p)} (no golden - run --snapshot)")
            ok = False
            continue
        with open(g) as f:
            gold = json.load(f)
        # round-trip through json so tuples/lists etc compare like-for-like
        now = json.loads(json.dumps(_canon(compute(p)), allow_nan=True))
        d = _diff(gold, now)
        if d:
            ok = False
            print(f"CHANGED   {_name(p)}")
            for line in d:
                print("    " + line)
        else:
            print(f"IDENTICAL {_name(p)}")
    print("ALL CORPUS RESULTS BIT-IDENTICAL TO GOLDEN" if ok else "CORPUS CHECK FAILED")
    return ok


# --------------------------------------------------------------------------
# self-consistency probes: physics identities the result must satisfy.
# Each returns (label, value_str, ok_bool_or_None).
# --------------------------------------------------------------------------
def _consistency(r):
    out = []
    c = r.get("cooling") or {}
    inp = r.get("inputs") or {}
    # 1. throat energy balance closure: q = h_g_eff * (T_aw,film - T_wg) at the throat
    q = _get(r, "cooling", "q_throat_w_m2")
    hg = _get(r, "cooling", "hg_throat_w_m2k")
    twg = _get(r, "cooling", "t_wg_throat_k")
    taw = None
    _prof = c.get("t_aw_film_profile_k")
    _rs = r.get("profile_rs_m")
    if _prof is not None and _rs is not None:
        taw = float(np.asarray(_prof)[int(np.argmin(np.asarray(_rs)))])
    if None not in (q, hg, twg, taw) and hg > 0:
        implied = hg * (taw - twg)
        ratio = q / implied if implied else float("nan")
        out.append(("q/(h_g(Taw-Twg))", f"{ratio:.2f}", abs(ratio - 1.0) < 0.10))
    # 2. T_wg as a fraction of T_aw (the circular-inversion fingerprint)
    if None not in (twg, taw) and taw:
        out.append(("Twg/Taw", f"{twg / taw:.3f}", None))
    # 3. jacket heat balance: Q_regen == mdot_jacket * (h(T_in + dT) - h(T_in)),
    #    enthalpy-exact with the same coolant model the march uses
    qw = _get(r, "cooling", "wall_heat_regen_w")
    dt = _get(r, "cooling", "coolant_delta_t_k")
    mj = _get(r, "cooling", "mdot_coolant_jacket_kgs")
    tin = _get(r, "cooling", "coolant_inlet_t_k")
    pc = _get(r, "cooling", "coolant_pressure_pa")
    regen = bool(c.get("regen_cooled"))
    if regen and None not in (qw, dt, mj, tin, pc) and dt > 0 and mj > 0:
        from engine_designer.physics.cooling import CoolantModel
        cm = CoolantModel(inp.get("propellant_pair"), pc)
        q_cool = mj * cm.heat_capacity_to(tin, dt)
        if q_cool > 0:
            out.append(("Qregen/(m dh)", f"{qw / q_cool:.3f}", abs(qw / q_cool - 1.0) < 0.03))
    # 4. throat margin row vs full-length peak row consistency
    m_thr = _get(r, "material_margin", "margin_ratio")
    m_pk = _get(r, "cooling", "peak_wall_margin_ratio")
    if None not in (m_thr, m_pk):
        out.append(("peak<=throat margin", f"{m_pk:.2f}/{m_thr:.2f}", m_pk <= m_thr + 1e-9))
    # 5. two jacket dP sources
    dp = _get(r, "cooling", "jacket_dp_pa")
    dpd = _get(r, "cooling", "jacket_dp_down_pa")
    if None not in (dp, dpd) and dp > 0 and dpd > 0:
        out.append(("dP_down/dP_total", f"{dpd / dp:.2f}", dpd <= dp))
    return out


def report(files, diff_golden=False):
    all_ok = True
    for p in files:
        name = _name(p)
        try:
            r = compute(p)
        except Exception as e:  # a crash IS a finding
            print(f"\n=== {name}\n  CRASH: {e!r}")
            all_ok = False
            continue
        ref = load_reference(p)
        metrics = ref.get("metrics", {})
        inp = r.get("inputs", {})
        print(f"\n=== {name}  [{inp.get('propellant_pair')} MR {inp.get('mixture_ratio')} "
              f"Pc {(_get(r, 'inputs', 'chamber_pressure_pa') or 0) / 1e6:.2f} MPa "
              f"eps {inp.get('expansion_ratio')} {inp.get('cycle')} "
              f"ch={r.get('cooling', {}).get('chamber_cooling_method')} "
              f"noz={r.get('cooling', {}).get('nozzle_cooling_method')}]")
        gold = None
        if diff_golden and os.path.exists(_golden_path(p)):
            with open(_golden_path(p)) as f:
                gold = json.load(f)
        for key, (label, unit, fn) in METRICS.items():
            v = fn(r)
            if v is None:
                continue
            line = f"  {label:<12} {v:>11.4g} {unit:<7}"
            if gold is not None:
                gv = fn(_decanon(gold))
                if gv is not None and gv != v:
                    pct = (v - gv) / gv * 100 if gv else float("inf")
                    line += f" (was {gv:.4g}, {pct:+.1f}%)"
            m = metrics.get(key)
            if m:
                lo, hi = m.get("lo"), m.get("hi")
                flag = ""
                if lo is not None and hi is not None:
                    inside = lo <= v <= hi
                    flag = "ok " if inside else "OUT"
                    if not inside and m.get("kind") == "validated":
                        all_ok = False
                ref_v = m.get("value")
                line += (f"  ref {'' if ref_v is None else f'{ref_v:.4g}'}"
                         f" [{lo}-{hi}] {flag} {m.get('kind', '')} {m.get('cite', '')}")
            print(line)
        for label, val, ok in _consistency(r):
            tag = "" if ok is None else ("ok " if ok else "BAD")
            print(f"  ~ {label:<20} {val:>10} {tag}")
        fails = [row for row in r.get("checklist", []) if _row_failed(row)]
        for row in fails:
            print(f"  ! checklist: {_row_text(row)}")
    return all_ok


def _row_failed(row):
    if isinstance(row, dict):
        return row.get("passed") is False
    if isinstance(row, (list, tuple)) and len(row) >= 2:
        return row[1] is False
    return False


def _row_text(row):
    if isinstance(row, dict):
        return f"[{row.get('category')}] {row.get('name')}: {row.get('detail')}"[:160]
    if isinstance(row, (list, tuple)):
        return " | ".join(str(x) for x in row if not isinstance(x, bool))[:140]
    return str(row)[:140]


def _decanon(obj):
    if isinstance(obj, dict):
        if set(obj) == {"__f__"}:
            return float(obj["__f__"])
        if set(obj) == {"__nd__"}:
            return np.array([_decanon(v) for v in obj["__nd__"]])
        return {k: _decanon(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_decanon(v) for v in obj]
    return obj


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--snapshot", action="store_true")
    g.add_argument("--check", action="store_true")
    g.add_argument("--report", action="store_true")
    ap.add_argument("--diff", action="store_true", help="with --report: show change vs golden")
    ap.add_argument("only", nargs="*", help="substring filter on corpus file names")
    a = ap.parse_args(argv)
    files = corpus_files()
    if a.only:
        files = [p for p in files if any(s.lower() in _name(p).lower() for s in a.only)]
    if not files:
        print("no corpus files found")
        return 1
    if a.snapshot:
        ok = snapshot(files)
    elif a.report:
        ok = report(files, diff_golden=a.diff)
    else:
        ok = check(files)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
