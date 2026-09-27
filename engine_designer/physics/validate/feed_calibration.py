"""Open-cycle feed-system + pump/turbine calibration (turbopump Round 0,
2026-09-26): the F-1 and H-1 pump discharge pressures, pump power, GG share and
turbine staging through the full EngineDesign.compute() pipeline, against their
published turbopump data.

What is GATED is what Round 0 calibrated - the per-leg feed loss
(design.FEED_LOSS_OVER_PC), the shared-shaft pump speed, the SP-8110 U/C0 staging
rule and the SP-8110 LOX/RP-1 turbine-gas cp. The fuel legs are gated EXCLUDING
the regen-jacket dP, which comes from the cooling solve (not this round) and is
reported alongside: the model's jacket dP runs 194 vs 244 psi on the F-1 and 244 vs
135 psi on the H-1 - see claude_lit/OPEN_QUESTIONS.md.

Part of the physics/validate/ package - run the whole suite with
`python3 -m engine_designer.physics.validate`."""
import json
import os

from ..design import EngineDesign
from .turbine_exhaust_checks import _f1_corpus, _h1_design

PSI = 6894.757
HP = 745.7
TOL = 0.10
_CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "validation_engines", "engines")

# [F1-Man Fig 3-14 / 1-16]: pump discharge, jacket dP, pump shaft power, GG share;
# [SP-8110 Table I]: turbine type / U/C0 / efficiency / rpm / mean diameter.
F1_REAL = dict(pc_ie_psia=1125.0, disch_ox_psia=1602.0, disch_fuel_psia=1870.0, jacket_psi=244.0,
               p_ox_bhp=30_300.0, p_fuel_bhp=22_700.0, gg_share=0.0291, eta_ox=0.746,
               eta_fuel=0.726, eta_turb=0.605, rpm=5490.0, uc0=0.20, dm_m=34.9 * 0.0254)
# [H1-Man Fig 1-44 / 1-18] 200K rating: discharge, shaft power, efficiency; jacket 135 psi.
H1_REAL = dict(pc_ie_psia=689.3, disch_ox_psia=950.2, disch_fuel_psia=1011.8, jacket_psi=135.0,
               p_ox_bhp=2277.0, p_fuel_bhp=1613.0, eta_ox=0.7712, eta_fuel=0.7244)


def _f1_at_real_pc():
    """The corpus F-1 fed at its real 1,125 psia injector-end Pc: the corpus Pc
    (RO's 6.77 MPa) is below it, so the nozzle Pc is scaled until pc_feed (with the
    injector-end rise on) equals the real injector-end value."""
    probe = _f1_corpus(apply_chamber_pressure_loss=True).compute()
    ratio = probe["pc_feed_pa"] / probe["inputs"]["chamber_pressure_pa"]
    return _f1_corpus(apply_chamber_pressure_loss=True,
                      chamber_pressure_pa=F1_REAL["pc_ie_psia"] * PSI / ratio).compute()


def _err(model, real):
    return (model - real) / real


def _gate(rows, label, model, real, unit, fmt="{:.0f}"):
    e = _err(model, real)
    ok = abs(e) <= TOL
    rows.append((f"{label}: {fmt.format(model)} vs real {fmt.format(real)} {unit} ({e:+.1%})", ok, True))
    return ok


def _report(rows, label, model, real, unit, fmt="{:.0f}", note=""):
    rows.append((f"{label}: {fmt.format(model)} vs real {fmt.format(real)} {unit} "
                 f"({_err(model, real):+.1%}){note}", True, False))


def run_feed_pump_calibration_check():
    """
    (a) F-1 at its real injector-end Pc [F1-Man Fig 3-14]: ox pump discharge,
        fuel discharge less the jacket dP, ox pump shaft power and GG share of
        total flow each within +-10 %; the auto turbine staging is 2-row
        velocity-compounded at U/C0 0.15-0.30 [SP-8110 Table I: 0.20]. Reported,
        not gated: fuel pump power / total discharge (jacket-dominated), pump
        and turbine efficiency, shaft rpm, wheel diameter.
    (b) H-1 200K [H1-Man Fig 1-44]: ox discharge, fuel discharge less the jacket
        and ox pump power within +-10 %; fuel side reported.
    (c) staging rule direction [SP-8110 §3.1.4]: the same H-1 GEARED (as the real
        one is, [SP-8101 p.3]) reaches U/C0 >= 0.30 and runs 2-stage
        pressure-compounded; direct-drive it falls back to velocity-compounded.
    (d) J-2 cross-check, reported only: fuel-pump discharge / Pc vs [SP-8107
        Table V]'s 1.6 - an LH2 regen jacket dominates it.
    """
    print("=" * 78)
    print("FEED-SYSTEM + PUMP/TURBINE CALIBRATION (F-1 / H-1, turbopump Round 0)")
    print("=" * 78)
    rows = []

    # (a) F-1
    f = _f1_at_real_pc()
    sz, tp = f["turbopump_sizing"], f["cycle_result"]["turbopump"]
    jk = f["cooling"]["jacket_dp_pa"] / PSI
    rows.append(("(a) F-1 at real injector-end Pc "
                 f"{f['pc_feed_pa'] / PSI:.0f} psia [F1-Man Fig 3-14]", True, False))
    _gate(rows, "    ox pump discharge", f["pump_discharge_ox_pa"] / PSI, F1_REAL["disch_ox_psia"], "psia")
    _gate(rows, "    fuel discharge less jacket", f["pump_discharge_fuel_pa"] / PSI - jk,
          F1_REAL["disch_fuel_psia"] - F1_REAL["jacket_psi"], "psia")
    _gate(rows, "    ox pump shaft power", tp["power_ox_w"] / HP, F1_REAL["p_ox_bhp"], "bhp")
    _gate(rows, "    GG share of total flow", f["cycle_result"]["gg_fraction_of_total"] * 100,
          F1_REAL["gg_share"] * 100, "%", "{:.2f}")
    t = sz["turbine"]
    stg_ok = (sz["turbine_staging"] == "velocity_compounded_2row" and 0.15 <= t["u_over_c0"] <= 0.30)
    rows.append((f"    turbine staging {sz['turbine_staging']} at U/C0 {t['u_over_c0']:.2f} "
                 f"(real 2-row VC at {F1_REAL['uc0']:.2f} [SP-8110 Table I])", stg_ok, True))
    _report(rows, "    fuel pump shaft power", tp["power_fuel_w"] / HP, F1_REAL["p_fuel_bhp"], "bhp",
            note=" - not gated (jacket dP)")
    _report(rows, "    fuel pump discharge (total)", f["pump_discharge_fuel_pa"] / PSI,
            F1_REAL["disch_fuel_psia"], "psia")
    _report(rows, "    regen-jacket dP", jk, F1_REAL["jacket_psi"], "psi", note=" - cooling solve")
    _report(rows, "    pump eta ox", sz["eta_pump_ox"], F1_REAL["eta_ox"], "", "{:.3f}")
    _report(rows, "    pump eta fuel", sz["eta_pump_fuel"], F1_REAL["eta_fuel"], "", "{:.3f}")
    _report(rows, "    turbine eta", sz["eta_turbine"], F1_REAL["eta_turb"], "", "{:.3f}")
    _report(rows, "    shared shaft speed", sz["fuel_shaft_rpm"], F1_REAL["rpm"], "rpm")
    _report(rows, "    turbine wheel mean dia", t["d_mean_m"], F1_REAL["dm_m"], "m", "{:.2f}")

    # (b) H-1
    h = _h1_design(mode="aspirator").compute()
    tph = h["cycle_result"]["turbopump"]
    jkh = h["cooling"]["jacket_dp_pa"] / PSI
    rows.append((f"(b) H-1 200K at {h['pc_feed_pa'] / PSI:.0f} psia [H1-Man Fig 1-44]", True, False))
    _gate(rows, "    ox pump discharge", h["pump_discharge_ox_pa"] / PSI, H1_REAL["disch_ox_psia"], "psia")
    _gate(rows, "    fuel discharge less jacket", h["pump_discharge_fuel_pa"] / PSI - jkh,
          H1_REAL["disch_fuel_psia"] - H1_REAL["jacket_psi"], "psia")
    _gate(rows, "    ox pump shaft power", tph["power_ox_w"] / HP, H1_REAL["p_ox_bhp"], "bhp")
    _report(rows, "    fuel pump shaft power", tph["power_fuel_w"] / HP, H1_REAL["p_fuel_bhp"], "bhp",
            note=" - not gated (jacket dP)")
    _report(rows, "    regen-jacket dP", jkh, H1_REAL["jacket_psi"], "psi", note=" - cooling solve")
    _report(rows, "    pump eta ox", h["turbopump_sizing"]["eta_pump_ox"], H1_REAL["eta_ox"], "", "{:.3f}")
    _report(rows, "    pump eta fuel", h["turbopump_sizing"]["eta_pump_fuel"], H1_REAL["eta_fuel"], "",
            "{:.3f}")

    # (c) staging direction
    hg = _h1_design(mode="aspirator", turbopump_arrangement="geared").compute()["turbopump_sizing"]
    hd = h["turbopump_sizing"]
    c_ok = (hg["turbine_staging"] == "pressure_compounded_2stage"
            and hd["turbine_staging"] == "velocity_compounded_2row")
    rows.append((f"(c) H-1 geared -> {hg['turbine_staging']} (real 2-stage PC at U/C0 0.42); "
                 f"direct-drive -> {hd['turbine_staging']} [SP-8110 §3.1.4]", c_ok, True))

    # (d) J-2 cross-check
    with open(os.path.join(_CORPUS_DIR, "J-2.json")) as fh:
        jd = json.load(fh)["design"]
    j = EngineDesign.from_dict({"schema_version": EngineDesign.SCHEMA_VERSION, "design": jd}).compute()
    rows.append((f"(d) J-2 fuel discharge / Pc {j['pump_discharge_fuel_pa'] / j['pc_feed_pa']:.2f} "
                 f"vs 1.6 [SP-8107 Table V] - reported only (LH2 jacket "
                 f"{j['cooling']['jacket_dp_pa'] / PSI:.0f} psi dominates)", True, False))

    all_ok = True
    for text, ok, gated in rows:
        tag = ("[OK]" if ok else "[*** FAIL ***]") if gated else ""
        print(f"  {text}  {tag}")
        all_ok &= ok
    print()
    print("ALL FEED/PUMP CALIBRATION CHECKS OK" if all_ok else
          "*** FEED/PUMP CALIBRATION CHECK FAILED - review design/constants.py FEED_LOSS_OVER_PC, "
          "turbopump_sizing.py ***")
    print("=" * 78)
    return all_ok


if __name__ == "__main__":
    raise SystemExit(0 if run_feed_pump_calibration_check() else 1)
