"""
Tap-off turbine drive gas: the hot-gas MIXER model (tap-off accuracy round, 2026-09-26).

The only real tap-off design point for a hydrocarbon in this project's literature is P&W's
Unique STBE Tap-Off engine [STBE-PW p.317 §4.3.1.1; Table 4.3.1-2] (LOX/CH4, 750 klbf SL,
Pc 2400 psia, MR 3.5, eps 35):

    "The tap-off provides 1.9 percent of the O/F biased chamber flow to the mixer inlet
     where cold methane mixes with the hot gases to provide 2293 psia, 1800 R gas to drive
     the high pressure propellant pumps."

12.5 % of the pumped methane reaches that mixer through the fuel bypass valve (85.7 % goes to
the 528 lbm/s coolant circuit). The mixed gas drives the methane turbine, then the oxygen
turbine in series, and is exhausted through a 5:1 nozzle. Table 4.3.1-2 lists a 132 lbm/s
"tap-off flow rate".

So the turbine gas is NOT chamber gas film-cooled to a turbine temperature (the legacy model,
`design.TAP_OFF_TEMP_FRACTION` / `TAP_OFF_TURBINE_LIMIT_K`). It is a small hot tap diluted
with a larger mass of cold PUMPED fuel. The result is fuel-rich (mixed MR ~0.4, GG-like) and
sits at 1,000 K and 0.955 x Pc.

This module is the pure half: the energy balance that fixes the dilution per kg of hot gas.
`design/feed_stage.py` wires it into the power balance, reusing the GG path's pumped-flow
accounting (`cycles.gas_generator_result(gg_mixture_ratio=mixed MR)`).

Energy balance per kg of hot tap gas (adiabatic mixer, frozen hot-gas cp):
    cp_hot * (T_hot - T_mix) = D * [h_fuel(T_mix, p) - h_fuel(T_in, p)]
- D = kg of dilution fuel per kg of hot gas.
- h_fuel comes from the baked coolant table (CoolProp; RP-1 = n-dodecane surrogate) at the
  mixer pressure, extrapolated at the table's top-end cp above its range (CH4 900 K,
  n-dodecane 800 K).
- T_hot = TAP_HOT_T_FRACTION x Tc is an EFFECTIVE hot-tap temperature. It lumps the "O/F
  biased" tap zone and any recombination heat into the frozen-cp balance. It is back-solved
  once on the STBE split (see `back_solve_hot_t_fraction`, which the self-test re-runs).

Reading of the STBE numbers (stated because the report is ambiguous):
- Table 4.3.1-2 has throat flow = injector flow - the 132 lbm/s tap-off flow. Read literally,
  132 lbm/s of HOT gas leaves the chamber.
- The text says 1.9 % of chamber flow (46.8 lbm/s) is hot. With 12.5 % of the methane
  (77 lbm/s) as dilution, that mixes to 1,800 R and totals 124 lbm/s, close to the 132.
- The tool's own power balance independently needs ~5-6 % of chamber flow of 1,000 K
  fuel-rich gas for this engine, i.e. ~132 lbm/s TOTAL.
- So this model follows the text: 132 lbm/s ~ the total (mixed) turbine flow, not hot flow.
"""

import numpy as np

from . import thermo_tables

# --- the STBE anchor [STBE-PW p.317 §4.3.1.1; Table 4.3.1-2] -------------------------------
STBE_ANCHOR = dict(
    pair="LOX/CH4",
    pc_pa=2400.0 * 6894.757,
    mr=3.5,
    injector_flow_lbm_s=2462.0,
    tap_off_flow_lbm_s=132.0,        # Table 4.3.1-2 "tap-off flow rate" (read as the total)
    hot_fraction_of_chamber=0.019,   # "1.9 percent of the O/F biased chamber flow"
    coolant_flow_lbm_s=528.0,        # = 85.7 % of the methane
    coolant_share_of_fuel=0.857,
    bypass_share_of_fuel=0.125,      # "remaining 12.5 percent ... into the hot gas mixer"
    t_fuel_in_k=239.0 / 1.8,         # methane entering the cooling circuit, 239 R
    t_mix_k=1800.0 / 1.8,            # "1800 R gas"
    p_mix_pa=2293.0 * 6894.757,      # "2293 psia"
)

# Turbine-inlet (mixer) temperature default for a hydrocarbon tap-off: the STBE's 1,800 R.
TAP_OFF_MIXER_TIN_K = STBE_ANCHOR["t_mix_k"]
# Turbine-inlet pressure / chamber pressure on the mixer path: STBE 2293 / 2400. The legacy
# path keeps the GG-borrowed 0.855 (turbine_exhaust.TAP_OFF_TURBINE_INLET_PC_FRACTION).
TAP_OFF_MIXER_TURBINE_INLET_PC_FRACTION = STBE_ANCHOR["p_mix_pa"] / STBE_ANCHOR["pc_pa"]
# Effective hot-tap temperature / Tc, back-solved on the STBE split with frozen chamber cp
# (Tier 2-3: one real design point, a design study rather than hardware). The self-test
# re-derives it and fails if this drifts more than 0.005 from the back-solve.
TAP_HOT_T_FRACTION = 0.890
# User turbine-inlet temperature floor (Tier 3): below ~600 K the turbine gas carries so
# little enthalpy that the tap flow runs away.
TAP_OFF_TIN_MIN_K = 600.0
# Pairs whose tap-off defaults to the mixer model ("auto"): the hydrocarbons, per the STBE
# precedent. LOX/LH2 stays legacy until a J-2S tap-off gas source is in hand (OPEN_QUESTIONS);
# storables have no tap-off precedent at all.
MIXER_PAIRS = ("LOX/CH4", "LOX/RP-1")
TAP_OFF_MODELS = ("auto", "mixer", "legacy")


def resolve_model(model, pair):
    """'auto' -> 'mixer' for the MIXER_PAIRS, else 'legacy'. Unknown values act as 'auto'."""
    if model in ("mixer", "legacy"):
        return model
    return "mixer" if pair in MIXER_PAIRS else "legacy"


def fuel_enthalpy_rise_j_kg(pair, t_in_k, t_out_k, p_pa):
    """h_fuel(t_out) - h_fuel(t_in) at pressure p [J/kg], from the baked coolant table.
    Linear in T at the table's end-point cp outside its range. None if the pair has no
    coolant table."""
    col = thermo_tables.coolant_column(pair, p_pa)
    if col is None:
        return None
    t, h, cp = col["t_k"], col["h_j_kg"], col["cp_j_kgk"]

    def _h(x):
        if x > t[-1]:
            return float(h[-1] + cp[-1] * (x - t[-1]))
        if x < t[0]:
            return float(h[0] - cp[0] * (t[0] - x))
        return float(np.interp(x, t, h))

    return _h(t_out_k) - _h(t_in_k)


def mixer_split(pair, mr_chamber, tc_k, cp_hot_j_kgk, t_mix_k, t_fuel_in_k, p_mix_pa,
                hot_t_fraction=TAP_HOT_T_FRACTION):
    """
    Hot-gas mixer split for a tap-off turbine.

    Returns a dict:
    - t_hot_k, t_mix_k: t_mix clamped to [TAP_OFF_TIN_MIN_K, t_hot - 50 K].
    - dilution_per_hot: kg of fuel per kg of hot tap gas.
    - hot_share / dilution_share: of the TURBINE flow.
    - mr_mix: O/F of the mixed turbine gas (hot at chamber MR plus pure fuel). This is what
      the pumps must deliver for the turbine flow on top of the throat flow.
    - dh_fuel_j_kg.
    - clamped: True if the requested t_mix was moved.
    Returns None if the pair has no coolant table.
    """
    t_hot = hot_t_fraction * tc_k
    t_req = float(t_mix_k)
    t_mix = min(max(t_req, TAP_OFF_TIN_MIN_K), t_hot - 50.0)
    dh = fuel_enthalpy_rise_j_kg(pair, t_fuel_in_k, t_mix, p_mix_pa)
    if dh is None or dh <= 0.0:
        return None
    d = cp_hot_j_kgk * (t_hot - t_mix) / dh
    return dict(
        t_hot_k=t_hot, t_mix_k=t_mix, t_mix_requested_k=t_req,
        clamped=abs(t_mix - t_req) > 1e-9,
        dilution_per_hot=d,
        hot_share=1.0 / (1.0 + d),
        dilution_share=d / (1.0 + d),
        mr_mix=mr_chamber / (1.0 + d * (1.0 + mr_chamber)),
        dh_fuel_j_kg=dh,
    )


def stbe_dilution_per_hot():
    """The STBE's own dilution/hot mass ratio from its reported shares."""
    a = STBE_ANCHOR
    methane = a["coolant_flow_lbm_s"] / a["coolant_share_of_fuel"]
    return (a["bypass_share_of_fuel"] * methane) / (a["hot_fraction_of_chamber"]
                                                    * a["injector_flow_lbm_s"])


def back_solve_hot_t_fraction():
    """TAP_HOT_T_FRACTION reproducing the STBE split: 1.9 % hot plus 12.5 % of the methane
    mixes to 1,800 R. Uses the same frozen chamber cp and Tc the design pipeline uses (the
    baked equilibrium table at the STBE's MR/Pc)."""
    a = STBE_ANCHOR
    g = thermo_tables.gas_state(a["pair"], a["mr"], a["pc_pa"])
    dh = fuel_enthalpy_rise_j_kg(a["pair"], a["t_fuel_in_k"], a["t_mix_k"], a["p_mix_pa"])
    t_hot = a["t_mix_k"] + stbe_dilution_per_hot() * dh / g["cp_frozen_j_kgk"]
    return t_hot / g["tc_k"]


if __name__ == "__main__":
    ok = True

    def check(name, cond, detail):
        global ok
        ok = ok and bool(cond)
        print(f"  {name:<58} {detail}  [{'OK' if cond else 'FAIL'}]")

    a = STBE_ANCHOR
    print("TAP-OFF HOT-GAS MIXER SELF-TEST [STBE-PW p.317, Table 4.3.1-2]")
    frac = back_solve_hot_t_fraction()
    check("back-solved hot-T fraction == TAP_HOT_T_FRACTION (+-0.005)",
          abs(frac - TAP_HOT_T_FRACTION) <= 0.005, f"{frac:.4f} vs {TAP_HOT_T_FRACTION}")
    check("hot-T fraction physically inside (0.5, 1.0] of Tc", 0.5 < frac <= 1.0, f"{frac:.3f}")
    g = thermo_tables.gas_state(a["pair"], a["mr"], a["pc_pa"])
    sp = mixer_split(a["pair"], a["mr"], g["tc_k"], g["cp_frozen_j_kgk"], a["t_mix_k"],
                     a["t_fuel_in_k"], a["p_mix_pa"])
    d_ref = stbe_dilution_per_hot()
    check("STBE dilution/hot ratio reproduced (+-3 %)",
          abs(sp["dilution_per_hot"] / d_ref - 1.0) <= 0.03,
          f"{sp['dilution_per_hot']:.3f} vs {d_ref:.3f}")
    hot = a["hot_fraction_of_chamber"] * a["injector_flow_lbm_s"]
    total = hot * (1.0 + sp["dilution_per_hot"])
    check("mixed turbine flow vs Table 4.3.1-2 132 lbm/s (+-10 %)",
          abs(total / a["tap_off_flow_lbm_s"] - 1.0) <= 0.10,
          f"{total:.1f} lbm/s ({(total / a['tap_off_flow_lbm_s'] - 1) * 100:+.1f} %)")
    check("mixed gas is fuel-rich, GG-like (MR 0.2-1.0) [SP-8081]",
          0.2 <= sp["mr_mix"] <= 1.0, f"MR {sp['mr_mix']:.3f}")
    check("turbine inlet / Pc = 2293/2400",
          abs(TAP_OFF_MIXER_TURBINE_INLET_PC_FRACTION - 0.9554) < 1e-3,
          f"{TAP_OFF_MIXER_TURBINE_INLET_PC_FRACTION:.4f}")
    # direction: a cooler turbine needs more dilution per kg of hot gas
    d_lo = mixer_split(a["pair"], a["mr"], g["tc_k"], g["cp_frozen_j_kgk"], 800.0,
                       a["t_fuel_in_k"], a["p_mix_pa"])["dilution_per_hot"]
    d_hi = mixer_split(a["pair"], a["mr"], g["tc_k"], g["cp_frozen_j_kgk"], 1150.0,
                       a["t_fuel_in_k"], a["p_mix_pa"])["dilution_per_hot"]
    check("cooler mix -> more dilution (800 K > 1000 K > 1150 K)",
          d_lo > sp["dilution_per_hot"] > d_hi, f"{d_lo:.2f} > {sp['dilution_per_hot']:.2f} > {d_hi:.2f}")
    # RP-1 (n-dodecane surrogate) works end to end
    g_rp = thermo_tables.gas_state("LOX/RP-1", 2.4, 10e6)
    sp_rp = mixer_split("LOX/RP-1", 2.4, g_rp["tc_k"], g_rp["cp_frozen_j_kgk"], 1000.0,
                        293.0, 9.5e6)
    check("LOX/RP-1 mixer split finite and fuel-rich",
          sp_rp is not None and 0.2 <= sp_rp["mr_mix"] <= 1.0,
          f"D {sp_rp['dilution_per_hot']:.2f}, MR {sp_rp['mr_mix']:.3f}, dh {sp_rp['dh_fuel_j_kg'] / 1e3:.0f} kJ/kg")
    # clamps
    sp_c = mixer_split(a["pair"], a["mr"], g["tc_k"], g["cp_frozen_j_kgk"], 5000.0,
                       a["t_fuel_in_k"], a["p_mix_pa"])
    check("requested Tin above the hot tap clamps below it", sp_c["clamped"]
          and sp_c["t_mix_k"] < sp_c["t_hot_k"], f"{sp_c['t_mix_k']:.0f} K")
    check("resolve_model: auto -> mixer for LOX/RP-1, legacy for LOX/LH2",
          resolve_model("auto", "LOX/RP-1") == "mixer" and resolve_model("auto", "LOX/LH2") == "legacy"
          and resolve_model("legacy", "LOX/CH4") == "legacy", "ok")
    print("ALL TAP-OFF MIXER SELF-TESTS OK" if ok else "TAP-OFF MIXER SELF-TEST FAILED")
    raise SystemExit(0 if ok else 1)
