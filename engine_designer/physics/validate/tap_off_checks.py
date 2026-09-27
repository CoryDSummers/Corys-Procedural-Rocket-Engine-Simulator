"""Tap-off cycle accuracy (2026-09-26) - physics/tap_off.py wired through
design/feed_stage.py, plus the turbine blade/disk material split.

(a) STBE-like engine (LOX/CH4, 2400 psia, MR 3.5, eps 35, 5:1 exhaust nozzle)
    [STBE-PW p.317 §4.3.1.1; Table 4.3.1-2], full pipeline on the mixer model:
    - turbine inlet 1,800 R (1,000 K) at 2293/2400 = 0.955 x Pc;
    - total turbine flow / injector flow vs 132/2462 = 5.36 % within +-25 %. This is the
      INDEPENDENT part: it comes from the tool's own pump power balance;
    - hot tap vs 1.9 % of chamber flow and dilution vs 12.5 % of the fuel, within +-30 %.
      This is a CONSISTENCY check, since TAP_HOT_T_FRACTION was back-solved on this split.
(b) tap_off_model "legacy" is the pre-round model: chamber-MR gas at
    min(Tc x 0.55, 1150 K), pumps on chamber flow only (tap flow not pumped), inlet
    0.855 x Pc.
(c) Direction: a lower tap_off_tin_k -> more turbine flow and a lower engine Isp, on
    both models.
(d) LOX/LH2 tap-off (the J-2X row of the cycle-model check): "auto" resolves to legacy and
    is identical to it.
(e) A LOX/RP-1 tap-off (RS-29-class) on the mixer: 1,000 K fuel-rich turbine gas
    (MR 0.2-1.0) and a turbine flow within the GG-fleet's few percent.

Part of the physics/validate/ package - run the whole suite with
`python3 -m engine_designer.physics.validate`."""
from .. import tap_off
from ..design import EngineDesign
from ..design.constants import TAP_OFF_TEMP_FRACTION, TAP_OFF_TURBINE_LIMIT_K

_BELL = dict(nozzle_type="bell", bell_percent_length=80.0)
STBE_DESIGN = dict(propellant_pair="LOX/CH4", mixture_ratio=3.5,
                   chamber_pressure_pa=2400.0 * 6894.757, expansion_ratio=35.0,
                   cycle="tap_off", target_vac_thrust_n=3.70e6,
                   turbine_exhaust_nozzle_eps=5.0, **_BELL)
J2X_DESIGN = dict(propellant_pair="LOX/LH2", mixture_ratio=5.5, chamber_pressure_pa=9.22e6,
                  expansion_ratio=92.0, cycle="tap_off", target_vac_thrust_n=1_307_000.0,
                  turbine_exhaust_mode="nozzle_injection", turbine_exhaust_inject_eps=10.9)
KEROLOX_DESIGN = dict(propellant_pair="LOX/RP-1", mixture_ratio=2.4, chamber_pressure_pa=10.0e6,
                      expansion_ratio=30.0, cycle="tap_off", target_vac_thrust_n=1.6e6, **_BELL)


def _flows(r):
    cr = r["cycle_result"]
    t = cr["tap_off"]
    turb = cr["gg_mdot_kgs"]
    hot = t.get("hot_mdot_kgs", turb)
    inj = r["mdot_chamber_kgs"] + hot
    return cr, t, turb, hot, inj


def run_tap_off_check():
    print("=" * 78)
    print("TAP-OFF CYCLE (hot-gas mixer [STBE-PW p.317] + legacy)")
    print("=" * 78)
    ok = True

    def row(name, cond, detail):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  {name:<66} {detail}  [{'OK' if cond else 'FAIL'}]")

    a = tap_off.STBE_ANCHOR
    # (a) STBE-like engine on the mixer
    r = EngineDesign(tap_off_model="mixer", **STBE_DESIGN).compute()
    cr, t, turb, hot, inj = _flows(r)
    ref_total = a["tap_off_flow_lbm_s"] / a["injector_flow_lbm_s"]
    row("(a) STBE turbine inlet 1,800 R", abs(cr["drive_gas"]["tin_k"] - a["t_mix_k"]) < 1.0,
        f"{cr['drive_gas']['tin_k']:.0f} K")
    row("(a) STBE turbine inlet / Pc = 2293/2400",
        abs(r["cycle_result"]["tap_off"]["p_mix_pa"] / STBE_DESIGN["chamber_pressure_pa"]
            - 0.9554) < 1e-3, f"{t['p_mix_pa'] / STBE_DESIGN['chamber_pressure_pa']:.4f}")
    row("(a) STBE total turbine flow / injector flow vs 5.36 % (+-25 %, independent)",
        abs(turb / inj / ref_total - 1.0) <= 0.25,
        f"{turb / inj * 100:.2f} % ({(turb / inj / ref_total - 1) * 100:+.1f} %)")
    row("(a) STBE hot tap vs 1.9 % of chamber flow (+-30 %, consistency)",
        abs(hot / inj / a["hot_fraction_of_chamber"] - 1.0) <= 0.30, f"{hot / inj * 100:.2f} %")
    row("(a) STBE dilution vs 12.5 % of the fuel (+-30 %, consistency)",
        abs(t["dilution_fraction_of_fuel"] / a["bypass_share_of_fuel"] - 1.0) <= 0.30,
        f"{t['dilution_fraction_of_fuel'] * 100:.1f} %")
    row("(a) STBE turbine gas fuel-rich, GG-like (MR 0.2-1.0) [SP-8081]",
        0.2 <= t["mr_mix"] <= 1.0, f"MR {t['mr_mix']:.3f}")

    # (b) legacy = the pre-round model
    rl = EngineDesign(tap_off_model="legacy", **STBE_DESIGN).compute()
    cl, tl, turb_l, _, _ = _flows(rl)
    tin_old = min(rl["tc_k"] * TAP_OFF_TEMP_FRACTION, TAP_OFF_TURBINE_LIMIT_K)
    mdot_c = rl["mdot_chamber_kgs"]
    tp = cl["turbopump"]
    row("(b) legacy tap gas = min(Tc x 0.55, 1150 K)", abs(cl["drive_gas"]["tin_k"] - tin_old) < 1e-9,
        f"{cl['drive_gas']['tin_k']:.0f} K")
    row("(b) legacy pumps move chamber flow only (tap flow not pumped)",
        abs(tp["mdot_fuel_kgs"] + tp["mdot_ox_kgs"] - mdot_c) <= 1e-9 * mdot_c,
        f"{tp['mdot_fuel_kgs'] + tp['mdot_ox_kgs']:.2f} vs {mdot_c:.2f} kg/s")
    row("(b) mixer pumps move chamber + turbine flow",
        abs(cr["turbopump"]["mdot_fuel_kgs"] + cr["turbopump"]["mdot_ox_kgs"]
            - r["mdot_chamber_kgs"] - turb) <= 1e-6 * r["mdot_chamber_kgs"],
        f"+{turb:.2f} kg/s")

    # (c) direction on both models
    for model in ("mixer", "legacy"):
        rs = [EngineDesign(tap_off_model=model, tap_off_tin_k=tin, **STBE_DESIGN).compute()
              for tin in (1150.0, 1000.0, 850.0)]
        fl = [_flows(x)[2] / x["mdot_chamber_kgs"] for x in rs]
        isp = [x["isp_vac_engine_s"] for x in rs]
        row(f"(c) {model}: tap Tin 1150 -> 1000 -> 850 K raises turbine flow, lowers Isp",
            fl[0] < fl[1] < fl[2] and isp[0] > isp[1] > isp[2],
            f"{fl[0] * 100:.2f} < {fl[1] * 100:.2f} < {fl[2] * 100:.2f} %; "
            f"{isp[0]:.1f} > {isp[1]:.1f} > {isp[2]:.1f} s")

    # (d) LOX/LH2: auto == legacy
    ra = EngineDesign(**J2X_DESIGN).compute()
    rl2 = EngineDesign(tap_off_model="legacy", **J2X_DESIGN).compute()
    row("(d) J-2X LOX/LH2 tap-off: auto -> legacy, identical",
        ra["cycle_result"]["tap_off"]["model"] == "legacy"
        and ra["isp_vac_engine_s"] == rl2["isp_vac_engine_s"]
        and ra["mdot_kgs"] == rl2["mdot_kgs"],
        f"Isp {ra['isp_vac_engine_s']:.2f} s, {ra['cycle_result']['drive_gas']['tin_k']:.0f} K")

    # (e) kerolox tap-off on the mixer
    rk = EngineDesign(**KEROLOX_DESIGN).compute()
    ck, tk, turb_k, _, _ = _flows(rk)
    row("(e) LOX/RP-1 tap-off: auto -> mixer, 1,000 K fuel-rich gas",
        tk["model"] == "mixer" and abs(ck["drive_gas"]["tin_k"] - 1000.0) < 1.0
        and 0.2 <= tk["mr_mix"] <= 1.0, f"{ck['drive_gas']['tin_k']:.0f} K, MR {tk['mr_mix']:.2f}")
    row("(e) LOX/RP-1 turbine flow a few % of chamber flow (2-8 %)",
        0.02 <= turb_k / rk["mdot_chamber_kgs"] <= 0.08,
        f"{turb_k / rk['mdot_chamber_kgs'] * 100:.2f} %")

    print("ALL TAP-OFF CHECKS OK" if ok else "TAP-OFF CHECKS FAILED")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if run_tap_off_check() else 1)
