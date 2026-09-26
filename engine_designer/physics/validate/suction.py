"""Pump suction: computed NPSH available / required and the suction-speed cap
(turbopump Round 1, 2026-09-26) - physics/inducer.py + design/suction_stage.py.

(a) SP-8107 Table II: every real pump runs at or below the model's suction-
    limited speed at its own specified NPSH (NPSH_min); the storable IRFNA pump
    (no TSH data) is report-only. The F-1 LOX pump, designed at its suction
    limit, sits within 15 % of the cap - the cap is not just loose.
(b) RD-0110 [KBKhA Table 2]: both pumps (no boost pumps, 18,400 rpm) under the
    cap at their real inlet pressures, propellants at storage temperature.
(c) Brumfield vs SP-8052 Table I: >= 4 of 6 inducers within 10 %.
(d) TSH anchors [SP-8052 §2.1.4] reproduce.
(e) Full pipeline, corpus F-1: not suction-limited at the corpus Pc; ox rpm within
    10 % of the real 5,488; default inputs leave the pump inlet at TANK_HEAD_PA,
    so pump discharge equals the legacy model's.
(f) Full pipeline, H-1 at its real rated inlet pressures [SP-8107 Table II] 65/57
    psia: NPSH available from tank pressure and the LOX vapor pressure; pump
    discharge unchanged (the pump dP shrinks by exactly the inlet rise).
(g) Real SSME HPOTP: at its real flow and speed the model's cap is exceeded
    when fed straight from the 100 psia LPOTP inlet and satisfied at the real
    380 psia boosted inlet [SP-8107 Table II; SSME-Orientation]. Full pipeline,
    corpus RS-25: its ox pump is suction-limited on the default inlet without
    boost pumps and freed by the real ones.

Part of the physics/validate/ package - run the whole suite with
`python3 -m engine_designer.physics.validate`."""
import json
import os

from .. import combustion, inducer, thermo_tables
from ..design import EngineDesign
from ..design.constants import G0, TANK_HEAD_PA
from .turbine_exhaust_checks import _f1_corpus, _h1_design

PSI = 6894.757
_FT = 3.2808399
_CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "validation_engines", "engines")
# [KBKhA Table 2] RD-0110 (GG, no boost pumps): inlet MPa, flow kg/s, rotor rpm.
RD0110 = dict(rpm=18_400.0, lox=(0.28e6, 64.5), rp1=(0.14e6, 29.3))
F1_RPM = 5488.0   # [SP-8107 Table II]
# SSME high-pressure LOX pump main stage [SP-8107 Table II EPL 7,250 gpm; SSME-Orientation
# p.52-71 NPL 22,220 rpm, inlet 380 psia from the LPOTP's 100 psia].
SSME_HPOTP = dict(gpm=7250.0, rpm=22_220.0)


def _corpus(name, **over):
    with open(os.path.join(_CORPUS_DIR, f"{name}.json")) as f:
        d = json.load(f)["design"]
    d.update(over)
    return EngineDesign.from_dict({"schema_version": EngineDesign.SCHEMA_VERSION, "design": d})


def _rd0110_rows():
    rows = []
    rho_fuel, rho_ox = combustion.propellant_densities("LOX/RP-1")
    for prop, leg, (p_in, mdot), rho in (("LOX", "ox", RD0110["lox"], rho_ox),
                                         ("RP-1", "fuel", RD0110["rp1"], rho_fuel)):
        nbp = thermo_tables.saturation_temperature(prop, 101_325.0)
        t = nbp if nbp < 250.0 else 293.15
        pv = thermo_tables.saturation(prop, t)["p_sat_pa"]
        npsha = (p_in - pv) / (rho * G0) * _FT
        spec = inducer.make_spec(prop, leg, t, npsha)
        cap = inducer.suction_limited_rpm(mdot / rho * 15850.323, spec)
        rows.append((prop, npsha, cap))
    return rows


def run_pump_suction_check():
    print("=" * 78)
    print("PUMP SUCTION (inducer NPSH required vs tank-side NPSH available, turbopump Round 1)")
    print("=" * 78)
    rows = []   # (text, ok, gated)

    # (a) SP-8107 Table II
    rows.append(("(a) SP-8107 Table II real pumps vs the model's suction-limited speed "
                 "at their own NPSH_min:", True, False))
    for eng, prop, rpm, cap, ratio, ind in inducer.real_pump_cap_rows():
        gated = prop != "IRFNA"
        note = "" if ind else " (no inducer: Ss 12,000)"
        if not gated:
            note += " - report only (storable, no TSH data)"
        rows.append((f"    {eng:<12} {prop:<8} {rpm:7,.0f} rpm vs cap {cap:8,.0f} "
                     f"({ratio:.2f}){note}", ratio <= 1.0 or not gated, gated))
    f1 = next(r for r in inducer.real_pump_cap_rows() if r[0] == "F-1" and r[1] == "LOX")
    rows.append((f"    F-1 LOX (designed at its suction limit) at {f1[4]:.2f} of the cap - "
                 f"within [0.85, 1.00]", 0.85 <= f1[4] <= 1.0, True))

    # (b) RD-0110
    for prop, npsha, cap in _rd0110_rows():
        rows.append((f"(b) RD-0110 {prop} pump: {npsha:.0f} ft NPSH available at its real inlet "
                     f"pressure -> cap {cap:,.0f} rpm vs real {RD0110['rpm']:,.0f} [KBKhA]",
                     RD0110["rpm"] <= cap, True))

    # (c) Brumfield vs SP-8052 Table I
    hits = 0
    for name, phi, nu, ss_real in inducer.SP8052_TABLE_I:
        e = inducer.brumfield_ss_at_phi(phi, nu) / ss_real - 1.0
        hits += abs(e) <= 0.10
    rows.append((f"(c) Brumfield at design phi vs SP-8052 Table I water Ss: {hits}/6 within 10 %",
                 hits >= 4, True))

    # (d) TSH anchors
    tsh_ok = all(abs(inducer.thermodynamic_suppression_head_ft(p, t) - v) < 1e-9
                 for p, (v, t) in inducer.TSH_ANCHORS.items())
    rows.append(("(d) TSH anchors reproduce: F-1 LOX 11 ft @ 163 degR, J-2 LH2 250 ft @ 38 degR "
                 "[SP-8052 §2.1.4]", tsh_ok, True))

    # (e) corpus F-1, full pipeline
    f = _f1_corpus().compute()
    fl = _f1_corpus(suction_model="legacy").compute()
    op = f["turbopump_sizing"]["ox_pump"]
    su = f["suction"]["ox"]
    e_rpm = op["n_rpm"] / F1_RPM - 1.0
    rows.append((f"(e) corpus F-1: ox pump {op['n_rpm']:,.0f} rpm ({e_rpm:+.1%} vs real "
                 f"{F1_RPM:,.0f}), NPSH available {su['npsh_available_ft']:.0f} ft vs required "
                 f"{op['npsh_required_ft']:.0f} ft (TSH {su['tsh_ft']:.0f} ft), not suction-limited",
                 abs(e_rpm) <= 0.10 and not op["suction_limited"], True))
    same = (f["pump_inlet_pa"]["ox"] == TANK_HEAD_PA
            and f["pump_discharge_ox_pa"] == fl["pump_discharge_ox_pa"]
            and f["pump_discharge_fuel_pa"] == fl["pump_discharge_fuel_pa"])
    rows.append(("    default inputs: pump inlet stays TANK_HEAD_PA, discharge == legacy", same, True))

    # (f) H-1 at its real rated inlet pressures
    h = _h1_design(tank_pressure_ox_pa=65.0 * PSI, tank_pressure_fuel_pa=57.0 * PSI).compute()
    h0 = _h1_design().compute()
    hs = h["suction"]["ox"]
    rho_ox = combustion.propellant_densities("LOX/RP-1")[1]
    hand = (65.0 * PSI - hs["p_vapor_pa"]) / (rho_ox * G0) * _FT
    rows.append((f"(f) H-1 at real inlet 65/57 psia: LOX NPSH available {hs['npsh_available_ft']:.0f} "
                 f"ft (hand {hand:.0f} ft; p_v {hs['p_vapor_pa'] / PSI:.1f} psia @ "
                 f"{hs['t_k']:.1f} K) vs real NPSH_min 35 ft; ox discharge "
                 f"{h['pump_discharge_ox_pa'] / PSI:.1f} vs default-inlet "
                 f"{h0['pump_discharge_ox_pa'] / PSI:.1f} psia",
                 abs(hs["npsh_available_ft"] - hand) < 1e-6 * hand and hs["npsh_available_ft"] > 35.0
                 and abs(h["pump_discharge_ox_pa"] - h0["pump_discharge_ox_pa"]) < 1.0, True))

    # (g1) real SSME HPOTP: why it needs its low-pressure boost pump
    rho = combustion.propellant_densities("LOX/LH2")[1]
    t_nbp = thermo_tables.saturation_temperature("LOX", 101_325.0)
    pv = thermo_tables.saturation("LOX", t_nbp)["p_sat_pa"]
    caps = {}
    for tag, p_in in (("LPOTP inlet 100 psia", 100.0 * PSI), ("HPOTP inlet 380 psia", 380.0 * PSI)):
        spec = inducer.make_spec("LOX", "ox", t_nbp, (p_in - pv) / (rho * G0) * _FT)
        caps[tag] = inducer.suction_limited_rpm(SSME_HPOTP["gpm"], spec)
    lo, hi = caps.values()
    rows.append((f"(g) SSME HPOTP {SSME_HPOTP['gpm']:,.0f} gpm at {SSME_HPOTP['rpm']:,.0f} rpm: "
                 f"cap {lo:,.0f} rpm fed straight from the 100 psia LPOTP inlet, {hi:,.0f} rpm "
                 f"at its real 380 psia boosted inlet - the model reproduces why the SSME needs "
                 f"its LPOTP [SP-8107 Table II; SSME-Orientation]",
                 lo < SSME_HPOTP["rpm"] <= hi, True))
    # (g2) full pipeline, corpus RS-25 (model rotor speeds are Ns-optimum, below real)
    r = _corpus("RS-25").compute()
    rn = _corpus("RS-25", boost_pump_rise_ox_pa=0.0, boost_pump_rise_fuel_pa=0.0,
                 tank_pressure_ox_pa=0.0, tank_pressure_fuel_pa=0.0).compute()
    ob, onb = r["turbopump_sizing"]["ox_pump"], rn["turbopump_sizing"]["ox_pump"]
    b = r["suction"]["ox"]["boost"]
    rows.append((f"    corpus RS-25 ox pump: {onb['n_rpm']:,.0f} rpm suction-limited (Ns optimum "
                 f"{onb['rpm_ns_optimum']:,.0f}) on the default 3 bar inlet without boost pumps; "
                 f"{ob['n_rpm']:,.0f} rpm, unlimited, with the real ones (LPOTP +"
                 f"{b['rise_pa'] / PSI:.0f} psi at {b['n_rpm']:,.0f} rpm vs real 5,050)",
                 onb["suction_limited"] and not ob["suction_limited"], True))

    all_ok = True
    for text, ok, gated in rows:
        tag = ("[OK]" if ok else "[*** FAIL ***]") if gated else ""
        print(f"  {text}  {tag}")
        all_ok &= ok
    print()
    print("ALL PUMP SUCTION CHECKS OK" if all_ok else
          "*** PUMP SUCTION CHECK FAILED - review physics/inducer.py, design/suction_stage.py ***")
    print("=" * 78)
    return all_ok


if __name__ == "__main__":
    raise SystemExit(0 if run_pump_suction_check() else 1)
