#!/usr/bin/env python3
"""Generate engine_designer's baked thermophysical property tables.

KEPT, re-runnable source of every combustion-gas and coolant property number in
``engine_designer/physics/property_data/`` (CLAUDE.md: never invent a number -
derive it and say how). The runtime tool never imports Cantera/CoolProp; it only
reads the JSON this script writes.

What it computes
----------------
1. ``combustion_equilibrium.json`` - for every bipropellant pair, on a
   (chamber pressure x mixture ratio) grid, with Cantera chemical equilibrium
   (NASA-Glenn thermo, ``nasa_gas.yaml``, C/H/O/N species) from LIQUID
   reactants at their CEA storage enthalpies:
     Tc, molar mass M, frozen cp / gamma, equilibrium cp, equilibrium
     isentropic exponent gamma_s, mixture-averaged viscosity + FROZEN thermal
     conductivity (GRI-Mech 3.0 transport data) and the resulting frozen
     Prandtl number, shifting-equilibrium c*, and vacuum Isp at eps 10/40/100.
   Plus informational monopropellant points (HTP decomposition).
2. ``coolant_properties.json`` - regen-jacket coolant properties on a
   (temperature x pressure) grid with CoolProp: density, cp, viscosity,
   conductivity, enthalpy for parahydrogen (LOX/LH2), methane (LOX/CH4) and
   n-dodecane (LOX/RP-1 - a SURROGATE: RP-1 is a kerosene blend; n-dodecane is
   the standard single-component stand-in, flagged as such in the output).
   MMH / UDMH / hydrazine are not in CoolProp - left to the tool's constants.

Self-check: the script re-derives Sutton Table 5-5 (Pc = 1000 psia, optimum
sea-level expansion, shifting equilibrium) and fails loudly if Tc / M / c*
disagree beyond tolerance - the same "reproduce a real reference before trusting
it" discipline as physics/validate.py.

How to run
----------
Locally (needs network once for pip; ~2-5 min on a laptop, no GPU needed)::

    python3 -m venv .venv-props
    .venv-props/bin/pip install cantera CoolProp
    .venv-props/bin/python tools/property_tables/generate_property_tables.py

Google Colab (one cell; then download the two JSON files it prints and drop
them into engine_designer/physics/property_data/)::

    !pip -q install cantera CoolProp
    # upload this file, then:
    !python generate_property_tables.py --out .

Options: ``--out DIR`` (default: the repo's property_data dir), ``--quick``
(coarse grid, for a smoke test), ``--check-only`` (just the Sutton self-check).
"""
from __future__ import annotations

import argparse
import datetime
import json
import math
import os
import sys
import time

import numpy as np

G0 = 9.80665
R_UNIV = 8314.462618  # J/kmol-K

# ---------------------------------------------------------------------------
# Reactants: elemental formula per mole + assigned enthalpy (J/mol) of the
# LIQUID at its storage temperature, relative to the elements at 298.15 K -
# exactly the reactant entries of NASA CEA's thermo.inp (McBride & Gordon,
# NASA RP-1311 / TP-2002-211556), which is how CEA/RPA treat liquid reactants.
# ---------------------------------------------------------------------------
REACTANTS = {
    "H2(L)":   ({"H": 2}, -9012.0, "20.27 K"),
    "O2(L)":   ({"O": 2}, -12979.0, "90.17 K"),
    "CH4(L)":  ({"C": 1, "H": 4}, -89233.0, "111.64 K"),
    "RP-1":    ({"C": 1, "H": 1.9423}, -24717.7, "298.15 K"),
    "N2O4(L)": ({"N": 2, "O": 4}, -19564.0, "298.15 K"),
    "MMH(L)":  ({"C": 1, "H": 6, "N": 2}, 54200.0, "298.15 K"),
    "UDMH(L)": ({"C": 2, "H": 8, "N": 2}, 48300.0, "298.15 K"),
    "N2H4(L)": ({"N": 2, "H": 4}, 50630.0, "298.15 K"),
    "H2O2(L)": ({"H": 2, "O": 2}, -187780.0, "298.15 K"),
    "H2O(L)":  ({"H": 2, "O": 1}, -285830.0, "298.15 K"),
}
ATOMIC_MASS = {"H": 1.00794, "C": 12.0107, "N": 14.0067, "O": 15.9994}

# pair -> (fuel blend {reactant: mass fraction}, oxidizer blend, MR grid)
PAIRS = {
    "LOX/RP-1": ({"RP-1": 1.0}, {"O2(L)": 1.0}, np.arange(1.6, 3.41, 0.1)),
    "LOX/LH2": ({"H2(L)": 1.0}, {"O2(L)": 1.0}, np.arange(3.0, 8.01, 0.25)),
    "LOX/CH4": ({"CH4(L)": 1.0}, {"O2(L)": 1.0}, np.arange(2.4, 4.41, 0.1)),
    "N2O4/MMH": ({"MMH(L)": 1.0}, {"N2O4(L)": 1.0}, np.arange(1.2, 3.01, 0.1)),
    "Aerozine-50/NTO": ({"UDMH(L)": 0.5, "N2H4(L)": 0.5}, {"N2O4(L)": 1.0},
                        np.arange(1.2, 3.01, 0.1)),
}
PC_GRID_MPA = [0.5, 1.0, 2.0, 4.0, 7.0, 12.0, 20.0, 30.0]
EPS_GRID = [10.0, 40.0, 100.0]

# Sutton, Rocket Propulsion Elements (7th ed.) Table 5-5 (PDF page 203): Pc 1000
# psia (6.895 MPa), optimum expansion to 1 atm. Each pair has two rows: the row
# that lists k is the FROZEN-flow optimum (its Isp is a frozen value - not
# comparable to this script's shifting-equilibrium Isp, so Isp is None there);
# the other row is the shifting optimum. (label, fuel blend, oxidizer blend, MR,
# Tc K, c* m/s, M kg/kmol, Isp s; None = not gated)
SUTTON_5_5 = [
    ("O2/H2", {"H2(L)": 1.0}, {"O2(L)": 1.0}, 4.02, 2999.0, 2432.0, 10.0, 389.5),
    # Printed/OCR Tc "2959" is internally inconsistent: at the same k, c* ~ sqrt(Tc/M),
    # and this row's own c* 2428 / M 8.9 against the MR-4.02 row require Tc ~2659 K
    # (a 6<->9 misread). Gated on 2659.
    ("O2/H2", {"H2(L)": 1.0}, {"O2(L)": 1.0}, 3.40, 2659.0, 2428.0, 8.9, None),
    ("O2/RP-1", {"RP-1": 1.0}, {"O2(L)": 1.0}, 2.56, 3677.0, 1800.0, 23.3, 300.0),
    ("O2/RP-1", {"RP-1": 1.0}, {"O2(L)": 1.0}, 2.24, 3571.0, 1774.0, 21.9, None),
    ("O2/CH4", {"CH4(L)": 1.0}, {"O2(L)": 1.0}, 3.00, 3526.0, 1853.0, None, 311.0),
    ("N2O4/A-50", {"UDMH(L)": 0.5, "N2H4(L)": 0.5}, {"N2O4(L)": 1.0}, 2.00, 3372.0, 1711.0, 22.6, 289.0),
    ("N2O4/MMH", {"MMH(L)": 1.0}, {"N2O4(L)": 1.0}, 2.15, 3396.0, 1747.0, 22.3, 289.0),
    # The table's two N2O4/N2H4 Tc entries (3258 @ MR 1.08, 3152 @ MR 1.34) are
    # SWAPPED - Tc must rise toward stoichiometric (MR 1.44); equilibrium gives
    # 3128 / 3257 K and the rows' own M (19.5 / 20.9) and c* agree. Gated swapped.
    ("N2O4/N2H4", {"N2H4(L)": 1.0}, {"N2O4(L)": 1.0}, 1.34, 3258.0, 1782.0, 20.9, 292.0),
    ("N2O4/N2H4", {"N2H4(L)": 1.0}, {"N2O4(L)": 1.0}, 1.08, 3152.0, 1765.0, 19.5, None),
]
SUTTON_TOL = {"tc": 0.02, "cstar": 0.025, "m": 0.035, "isp": 0.025}

# Coolants: pair -> (CoolProp fluid, surrogate?, T grid K, P grid MPa)
COOLANTS = {
    "LOX/LH2": ("ParaHydrogen", False,
                np.unique(np.concatenate([np.arange(20.0, 60.0, 1.0), np.arange(60.0, 200.0, 5.0),
                                          np.arange(200.0, 1001.0, 20.0)])),
                [0.5, 1.0, 2.0, 4.0, 7.0, 10.0, 15.0, 20.0, 30.0, 40.0, 50.0]),
    "LOX/CH4": ("Methane", False,
                np.unique(np.concatenate([np.arange(95.0, 250.0, 2.5), np.arange(250.0, 901.0, 10.0)])),
                [0.5, 1.0, 2.0, 4.0, 7.0, 10.0, 15.0, 20.0, 30.0, 40.0, 50.0]),
    "LOX/RP-1": ("n-Dodecane", True, np.arange(280.0, 801.0, 5.0),
                 [0.5, 1.0, 2.0, 4.0, 7.0, 10.0, 15.0, 20.0, 30.0, 40.0, 50.0]),
}


# ---------------------------------------------------------------------------
def _blend(fuel, ox, mr):
    """Element kmol per kg and enthalpy J/kg of the reactant mixture at O/F = mr."""
    w_f, w_o = 1.0 / (1.0 + mr), mr / (1.0 + mr)
    elems = {e: 0.0 for e in ATOMIC_MASS}
    h = 0.0
    for blend, w in ((fuel, w_f), (ox, w_o)):
        for name, frac in blend.items():
            comp, hf, _ = REACTANTS[name]
            mw = sum(ATOMIC_MASS[e] * n for e, n in comp.items())      # kg/kmol
            kmol = w * frac / mw                                        # kmol per kg mix
            for e, n in comp.items():
                elems[e] += kmol * n
            h += kmol * hf * 1000.0                                     # J/mol -> J/kmol
    return elems, h


class Equilibrium:
    def __init__(self):
        import cantera as ct
        self.ct = ct
        sp = ct.Species.list_from_file("nasa_gas.yaml")
        keep = []
        for s in sp:
            comp = s.composition
            if not set(comp) <= {"C", "H", "O", "N"}:
                continue
            if comp.get("C", 0) > 2 or sum(comp.values()) > 6 or "+" in s.name or "-" in s.name:
                continue
            keep.append(s)
        self.gas = ct.Solution(thermo="ideal-gas", species=keep)
        self.tr = ct.Solution("gri30.yaml")
        self.tr_names = set(self.tr.species_names)
        self.n_species = len(keep)

    def chamber(self, elems, h, p_pa):
        g = self.gas
        x = {e: n for e, n in elems.items() if n > 0}
        g.TPX = 3000.0, p_pa, x
        g.equilibrate("TP")
        g.HP = h, p_pa
        g.equilibrate("HP")
        return g.state

    def transport(self, T, P, X):
        tr = self.tr
        xm = {n: X[i] for i, n in enumerate(self.gas.species_names)
              if n in self.tr_names and X[i] > 1e-10}
        tr.TPX = T, P, xm
        return tr.viscosity, tr.thermal_conductivity, sum(xm.values())

    def point(self, elems, h, p_pa, eps_list=EPS_GRID, pe_opt_pa=None):
        g = self.gas
        st0 = self.chamber(elems, h, p_pa)
        g.state = st0
        T0, M = g.T, g.mean_molecular_weight
        cp_f, cv_f = g.cp_mass, g.cv_mass
        h0, s0 = g.enthalpy_mass, g.entropy_mass
        X0 = g.X.copy()
        mu, lam, xcov = self.transport(T0, p_pa, X0)
        # equilibrium cp: dh/dT at constant P with re-equilibration
        dT = 5.0
        hs = []
        for t in (T0 - dT, T0 + dT):
            g.state = st0
            g.TP = t, p_pa
            g.equilibrate("TP")
            hs.append(g.enthalpy_mass)
        cp_eq = (hs[1] - hs[0]) / (2 * dT)
        # equilibrium isentropic exponent gamma_s = dlnP/dlnrho at const s

        def at_p(p):
            g.state = st0
            g.SP = s0, p
            g.equilibrate("SP")
            u = math.sqrt(max(0.0, 2.0 * (h0 - g.enthalpy_mass)))
            return g.density, u, g.T

        rho_a, _, _ = at_p(p_pa * 0.99)
        rho_b, _, _ = at_p(p_pa * 1.01)
        gamma_s = math.log(1.01 / 0.99) / math.log(rho_b / rho_a)
        # throat = max mass flux (golden section in ln P)
        lo, hi = math.log(0.35 * p_pa), math.log(0.85 * p_pa)
        gr = (math.sqrt(5) - 1) / 2

        def G(lp):
            r, u, _ = at_p(math.exp(lp))
            return r * u
        a, b = lo, hi
        c, d = b - gr * (b - a), a + gr * (b - a)
        gc, gd = G(c), G(d)
        for _ in range(40):
            if gc > gd:
                b, d, gd = d, c, gc
                c = b - gr * (b - a)
                gc = G(c)
            else:
                a, c, gc = c, d, gd
                d = a + gr * (b - a)
                gd = G(d)
        lpt = 0.5 * (a + b)
        g_t = G(lpt)
        cstar = p_pa / g_t

        def exit_for_eps(eps):
            a2, b2 = math.log(p_pa * 1e-7), lpt
            for _ in range(60):
                m = 0.5 * (a2 + b2)
                r, u, _ = at_p(math.exp(m))
                if g_t / (r * u) > eps:
                    a2 = m
                else:
                    b2 = m
            pe = math.exp(0.5 * (a2 + b2))
            r, u, t = at_p(pe)
            return (u + pe / (r * u)) / G0, pe, t

        isp_vac = {}
        for eps in eps_list:
            isp, _, _ = exit_for_eps(eps)
            isp_vac[f"{eps:g}"] = isp
        out = dict(tc_k=T0, m_molar=M, cp_frozen_j_kgk=cp_f, gamma_frozen=cp_f / cv_f,
                   cp_equilibrium_j_kgk=cp_eq, gamma_s=gamma_s, mu_pa_s=mu,
                   k_frozen_w_mk=lam, pr_frozen=mu * cp_f / lam, transport_mole_coverage=xcov,
                   pt_over_pc=math.exp(lpt) / p_pa, cstar_ms=cstar, isp_vac_s=isp_vac)
        if pe_opt_pa is not None:
            r, u, _ = at_p(pe_opt_pa)
            out["isp_opt_s"] = u / G0
        return out


def sutton_check(eq, verbose=True):
    ok_all = True
    p = 6.894757e6
    if verbose:
        print("Sutton Table 5-5 self-check (Pc 1000 psia, optimum expansion to 1 atm):")
    for label, fuel, ox, mr, tc, cs, m, isp in SUTTON_5_5:
        el, h = _blend(fuel, ox, mr)
        r = eq.point(el, h, p, eps_list=[], pe_opt_pa=101325.0)
        rows = [("tc", r["tc_k"], tc), ("cstar", r["cstar_ms"], cs)]
        if isp is not None:
            rows.append(("isp", r["isp_opt_s"], isp))
        if m is not None:
            rows.append(("m", r["m_molar"], m))
        bits = []
        for k, v, ref in rows:
            err = (v - ref) / ref
            ok = abs(err) <= SUTTON_TOL[k]
            ok_all &= ok
            bits.append(f"{k} {v:7.1f} vs {ref:7.1f} ({err * 100:+5.1f}%){'' if ok else ' FAIL'}")
        if verbose:
            print(f"  {label:10s} MR {mr:4.2f}: " + " | ".join(bits))
    if verbose:
        print("SUTTON TABLE 5-5 SELF-CHECK OK" if ok_all else "*** SUTTON SELF-CHECK FAILED ***")
    return ok_all


def build_gas_tables(eq, quick=False):
    out = {}
    pcs = PC_GRID_MPA[::3] if quick else PC_GRID_MPA
    for pair, (fuel, ox, mrs) in PAIRS.items():
        mrs = mrs[::4] if quick else mrs
        t0 = time.time()
        grid = {k: [] for k in ("tc_k", "m_molar", "cp_frozen_j_kgk", "gamma_frozen",
                                "cp_equilibrium_j_kgk", "gamma_s", "mu_pa_s", "k_frozen_w_mk",
                                "pr_frozen", "cstar_ms", "transport_mole_coverage")}
        isp = {f"{e:g}": [] for e in EPS_GRID}
        for pc in pcs:
            rows = {k: [] for k in grid}
            irow = {k: [] for k in isp}
            for mr in mrs:
                el, h = _blend(fuel, ox, float(mr))
                r = eq.point(el, h, pc * 1e6)
                for k in grid:
                    rows[k].append(round(float(r[k]), 7))
                for k in isp:
                    irow[k].append(round(float(r["isp_vac_s"][k]), 3))
            for k in grid:
                grid[k].append(rows[k])
            for k in isp:
                isp[k].append(irow[k])
        out[pair] = dict(mr=[round(float(x), 4) for x in mrs], pc_mpa=pcs,
                         fuel=fuel, oxidizer=ox, **grid, isp_vac_s_by_eps=isp)
        print(f"  {pair:16s} {len(pcs)} Pc x {len(mrs)} MR  ({time.time() - t0:.0f} s)")
    # informational monopropellant: HTP decomposition (adiabatic, equilibrium)
    mono = {}
    for conc in (0.85, 0.90, 0.98):
        el, h = _blend({"H2O2(L)": conc, "H2O(L)": 1.0 - conc}, {"H2O2(L)": 1.0}, 0.0)
        r = eq.point(el, h, 1.0e6)
        mono[f"H2O2 {conc:.0%}"] = {k: (round(float(v), 6) if not isinstance(v, dict) else v)
                                    for k, v in r.items()}
    return out, mono


def build_coolant_tables(quick=False):
    import CoolProp
    from CoolProp.CoolProp import PropsSI
    out = {}
    for pair, (fluid, surrogate, ts, ps) in COOLANTS.items():
        ts = ts[::5] if quick else ts
        props = {k: [] for k in ("rho_kg_m3", "cp_j_kgk", "mu_pa_s", "k_w_mk", "h_j_kg")}
        codes = {"rho_kg_m3": "D", "cp_j_kgk": "C", "mu_pa_s": "V", "k_w_mk": "L", "h_j_kg": "H"}
        n_fail = 0
        for p in ps:
            row = {k: [] for k in props}
            for t in ts:
                for k, c in codes.items():
                    try:
                        v = PropsSI(c, "T", float(t), "P", p * 1e6, fluid)
                        if not math.isfinite(v):
                            raise ValueError
                        row[k].append(float(f"{v:.7g}"))
                    except Exception:
                        row[k].append(None)
                        n_fail += 1
            for k in props:
                props[k].append(row[k])
        out[pair] = dict(fluid=fluid, surrogate=surrogate,
                         t_k=[float(x) for x in ts], p_mpa=ps,
                         critical_t_k=PropsSI("Tcrit", fluid), critical_p_pa=PropsSI("pcrit", fluid),
                         failed_points=n_fail, **props)
        print(f"  {pair:10s} {fluid:12s} {len(ps)} P x {len(ts)} T  (failed {n_fail})")
    return out, CoolProp.__version__


def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    default_out = os.path.normpath(os.path.join(here, "..", "..", "engine_designer", "physics",
                                                "property_data"))
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=default_out)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args(argv)

    import warnings

    import cantera as ct
    # Deep-expansion exits (eps 100 at low Pc) cool below the NASA polynomials'
    # 300 K floor; Cantera extrapolates and warns once per call. Only the
    # informational isp_vac_s_by_eps["100"] column can be affected (noted in meta).
    warnings.filterwarnings("ignore", message=".*outside valid range of 300 K.*")
    eq = Equilibrium()
    ok = sutton_check(eq)
    if a.check_only:
        return 0 if ok else 1
    if not ok:
        print("refusing to write tables that fail the Sutton self-check")
        return 1
    os.makedirs(a.out, exist_ok=True)
    now = datetime.date.today().isoformat()
    print("combustion equilibrium tables:")
    gas, mono = build_gas_tables(eq, quick=a.quick)
    meta = dict(generator="tools/property_tables/generate_property_tables.py", date=now,
                cantera_version=ct.__version__, thermo="nasa_gas.yaml (NASA-Glenn), C/H/O/N "
                "neutral species with <=2 C and <=6 atoms (%d species)" % eq.n_species,
                transport="gri30.yaml mixture-averaged (frozen conductivity)",
                reactants={k: dict(formula=v[0], h_j_mol=v[1], state=v[2])
                           for k, v in REACTANTS.items()},
                reactant_source="NASA CEA thermo.inp liquid-reactant assigned enthalpies",
                self_check="Sutton Table 5-5 (1000 psia, opt. expansion): PASSED",
                layout="each property is [len(pc_mpa)][len(mr)]; isp_vac_s_by_eps[eps] likewise",
                caveats=["isp_vac_s_by_eps['100'] exit states can fall below the NASA "
                         "polynomials' 300 K floor (thermo extrapolated) - informational only",
                         "transport: species absent from GRI-Mech 3.0 are dropped "
                         "(transport_mole_coverage records the retained mole fraction)",
                         "properties are chamber (stagnation) values; Bartz uses them as-is"],
                quick=a.quick)
    with open(os.path.join(a.out, "combustion_equilibrium.json"), "w") as f:
        json.dump(dict(meta=meta, pairs=gas, monopropellant_info=mono), f, indent=1)
    print("coolant tables:")
    cool, cpv = build_coolant_tables(quick=a.quick)
    cmeta = dict(generator=meta["generator"], date=now, coolprop_version=cpv,
                 layout="each property is [len(p_mpa)][len(t_k)]; None = CoolProp failure",
                 note="LOX/RP-1 uses n-dodecane as a single-component RP-1 SURROGATE", quick=a.quick)
    with open(os.path.join(a.out, "coolant_properties.json"), "w") as f:
        json.dump(dict(meta=cmeta, coolants=cool), f, indent=1)
    print(f"wrote {a.out}/combustion_equilibrium.json and coolant_properties.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
