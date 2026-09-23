"""
Driver: H-4-250K design point -> engine_physics / isentropic -> printed report.

No new physics here - this file only supplies numbers (the design point and
the documented modeling-assumption constants) and formats the output.
"""
import numpy as np

import isentropic as iso
import engine_physics as ep

G0 = iso.G0
PA_SEA_LEVEL = 101_325.0  # Pa, standard sea level


def cf_vac_effective(gamma, pe_pc, eps, eta_noz):
    return iso.cf_vacuum(gamma, pe_pc, eps) * eta_noz


def cf_sl_effective(gamma, pe_pc, eps, eta_noz, pa_pc):
    return cf_vac_effective(gamma, pe_pc, eps, eta_noz) - eps * pa_pc


def nozzle_performance(pc, eps, mr, eta_cstar, eta_noz, pa=PA_SEA_LEVEL):
    tc, gamma, m_molar = ep.combustion_state(mr)
    mach = iso.mach_from_area_ratio(eps, gamma)
    pe_pc = iso.pe_over_pc(mach, gamma)
    pe = pe_pc * pc
    cstar = iso.c_star(tc, gamma, m_molar, eta_cstar)
    cf_vac = cf_vac_effective(gamma, pe_pc, eps, eta_noz)
    cf_sl = cf_sl_effective(gamma, pe_pc, eps, eta_noz, pa / pc)
    isp_vac = iso.isp_from_cf(cstar, cf_vac)
    isp_sl = iso.isp_from_cf(cstar, cf_sl)
    separated_sl = iso.is_separated(pe, pa)
    return {
        "eps": eps, "tc_k": tc, "gamma": gamma, "m_molar": m_molar,
        "pe_pc": pe_pc, "pe_pa": pe, "cstar_ms": cstar,
        "cf_vac": cf_vac, "cf_sl": cf_sl,
        "isp_vac_s": isp_vac, "isp_sl_s": isp_sl,
        "separated_sl_at_100pct": separated_sl,
    }


# ===========================================================================
# 1) SPOT CHECK — re-derive RD-111 (real RO engine) from its own Pc/eps/MR
#    using the SAME model + efficiency assumptions we're about to apply to
#    H-4. This is the go/no-go gate: if this is far off, eta_cstar / eta_noz
#    get adjusted HERE, not by fudging the H-4 numbers directly.
# ===========================================================================
ETA_CSTAR = 0.975
ETA_NOZ = 0.985

RD111_PC = 7.85e6      # Pa, Engine_Configs/RD111_config.cfg comment
RD111_EPS = 18
RD111_MR = 2.39         # Engine_Configs/RD111_config.cfg comment "Prop Ratio: 2.39"
RD111_ACTUAL_ISP_VAC = 309.5
RD111_ACTUAL_ISP_SL = 268.0

rd111 = nozzle_performance(RD111_PC, RD111_EPS, RD111_MR, ETA_CSTAR, ETA_NOZ)
rd111_err_vac = (rd111["isp_vac_s"] - RD111_ACTUAL_ISP_VAC) / RD111_ACTUAL_ISP_VAC * 100
rd111_err_sl = (rd111["isp_sl_s"] - RD111_ACTUAL_ISP_SL) / RD111_ACTUAL_ISP_SL * 100

print("=" * 78)
print("SPOT CHECK — RD-111 (Pc 7.85 MPa, eps 18, MR 2.39) re-derived from the model")
print("=" * 78)
print(f"  eta_cstar = {ETA_CSTAR}, eta_noz = {ETA_NOZ}")
print(f"  Tc = {rd111['tc_k']:.1f} K, gamma = {rd111['gamma']:.4f}, M = {rd111['m_molar']:.2f} kg/kmol")
print(f"  predicted  vac Isp = {rd111['isp_vac_s']:.1f} s   (actual {RD111_ACTUAL_ISP_VAC} s, err {rd111_err_vac:+.2f}%)")
print(f"  predicted  sl  Isp = {rd111['isp_sl_s']:.1f} s   (actual {RD111_ACTUAL_ISP_SL} s, err {rd111_err_sl:+.2f}%)")
if max(abs(rd111_err_vac), abs(rd111_err_sl)) > 5.0:
    print("  *** WARNING: spot-check error exceeds 5% — treat H-4 numbers below with caution ***")
else:
    print("  spot-check within tolerance (<5%) — proceeding with H-4 design point")
print()

# ===========================================================================
# 2) H-4-250K DESIGN POINT
# ===========================================================================
PC = 8.0e6          # Pa — evolved gas-generator, up from the H-3's ~6.2 MPa
MR = 2.34            # H-x family common mixture ratio
EPS_BASE = 14        # pad-attached booster nozzle
EPS_SUB = 20         # high-altitude sustainer nozzle (SUBCONFIG 20AR)
THROTTLE_FLOOR = 0.50
TARGET_VAC_THRUST_SUB_N = 1_500_000.0  # aim under the user's 1600 kN ceiling

base = nozzle_performance(PC, EPS_BASE, MR, ETA_CSTAR, ETA_NOZ)
sub = nozzle_performance(PC, EPS_SUB, MR, ETA_CSTAR, ETA_NOZ)

# Shared powerhead flow rate, sized off the higher-Cf (sub/20AR) nozzle so
# ITS vacuum thrust lands at the target; the base nozzle's thrust then falls
# out of the SAME mdot (same turbopump, same powerhead, two nozzles).
MDOT = TARGET_VAC_THRUST_SUB_N / (sub["isp_vac_s"] * G0)

thrust_base_vac = MDOT * base["isp_vac_s"] * G0
thrust_base_sl = MDOT * base["isp_sl_s"] * G0
thrust_sub_vac = MDOT * sub["isp_vac_s"] * G0
thrust_sub_sl = MDOT * sub["isp_sl_s"] * G0

print("=" * 78)
print("H-4-250K DESIGN POINT")
print("=" * 78)
print(f"  Pc = {PC/1e6:.2f} MPa, MR = {MR}, mdot (shared powerhead) = {MDOT:.2f} kg/s")
print(f"  combustion: Tc = {base['tc_k']:.1f} K, gamma = {base['gamma']:.4f}, M = {base['m_molar']:.2f} kg/kmol")
print(f"  c* = {base['cstar_ms']:.1f} m/s  (eta_cstar {ETA_CSTAR})")
print()
print(f"  {'':14}{'eps '+str(EPS_BASE)+' (base)':>18}{'eps '+str(EPS_SUB)+' (20AR)':>18}")
print(f"  {'Isp vac [s]':14}{base['isp_vac_s']:18.1f}{sub['isp_vac_s']:18.1f}")
print(f"  {'Isp sl  [s]':14}{base['isp_sl_s']:18.1f}{sub['isp_sl_s']:18.1f}")
print(f"  {'thrust vac [kN]':14}{thrust_base_vac/1e3:18.1f}{thrust_sub_vac/1e3:18.1f}")
print(f"  {'thrust sl  [kN]':14}{thrust_base_sl/1e3:18.1f}{thrust_sub_sl/1e3:18.1f}")
print(f"  {'Pe/Pa @ SL 100%':14}{base['pe_pa']/PA_SEA_LEVEL:18.3f}{sub['pe_pa']/PA_SEA_LEVEL:18.3f}")
print(f"  {'attached @ SL?':14}{str(not base['separated_sl_at_100pct']):>18}{str(not sub['separated_sl_at_100pct']):>18}")
print()
print(f"  minThrust (50% floor):  base {thrust_base_vac*THROTTLE_FLOOR/1e3:.1f} kN vac   "
      f"20AR {thrust_sub_vac*THROTTLE_FLOOR/1e3:.1f} kN vac")

# ===========================================================================
# 3) CHAMBER GEOMETRY (shared powerhead — throat is nozzle-independent;
#    exit geometry given for both bells)
# ===========================================================================
geo = ep.chamber_geometry(MDOT, base["cstar_ms"], PC, EPS_BASE, lstar=1.0, contraction_ratio=1.6)
geo_sub_exit = ep.chamber_geometry(MDOT, base["cstar_ms"], PC, EPS_SUB, lstar=1.0, contraction_ratio=1.6)

print()
print("=" * 78)
print("CHAMBER GEOMETRY")
print("=" * 78)
print(f"  throat: {geo['throat_dia_m']*100:.1f} cm dia  ({geo['throat_area_m2']:.4f} m^2)")
print(f"  chamber: {geo['chamber_dia_m']*100:.1f} cm dia, L* 1.0 m -> {geo['chamber_length_m']*100:.1f} cm to throat")
print(f"  exit (eps {EPS_BASE}): {geo['exit_dia_m']:.2f} m dia")
print(f"  exit (eps {EPS_SUB}): {geo_sub_exit['exit_dia_m']:.2f} m dia")

# ===========================================================================
# 4) TURBOPUMP POWER BALANCE
# ===========================================================================
DP_FUEL = 11.4e6   # Pa — Pc + injector dP + jacket dP + lines - tank head
DP_OX = 10.2e6     # Pa — Pc + injector dP + lines - tank head
RHO_RP1 = 810.0
RHO_LOX = 1141.0
ETA_PUMP_FUEL = 0.72
ETA_PUMP_OX = 0.75

tp = ep.turbopump_power(MDOT, MR, DP_FUEL, DP_OX, RHO_RP1, RHO_LOX, ETA_PUMP_FUEL, ETA_PUMP_OX)

print()
print("=" * 78)
print("TURBOPUMP POWER BALANCE")
print("=" * 78)
print(f"  mdot_fuel = {tp['mdot_fuel_kgs']:.1f} kg/s, mdot_ox = {tp['mdot_ox_kgs']:.1f} kg/s")
print(f"  fuel pump: {tp['power_fuel_w']/1e6:.2f} MW ({tp['power_fuel_w']/745.7:.0f} shp) @ dP {DP_FUEL/1e6:.1f} MPa")
print(f"  ox pump:   {tp['power_ox_w']/1e6:.2f} MW ({tp['power_ox_w']/745.7:.0f} shp) @ dP {DP_OX/1e6:.1f} MPa")
print(f"  TOTAL:     {tp['power_total_w']/1e6:.2f} MW ({tp['power_total_w']/745.7:.0f} shp)")

# ===========================================================================
# 5) GAS-GENERATOR FLOW FRACTION — single-crystal turbine (1050 K inlet)
#    vs. the H-3-era 900 K inlet, same pump power requirement
# ===========================================================================
CP_GG = 2100.0
ETA_TURBINE = 0.62
PR_TURBINE = 22.0
GAMMA_GG = 1.13

mdot_gg_1050, dh_1050 = ep.gg_flow_fraction(tp["power_total_w"], 1050.0, CP_GG, ETA_TURBINE, PR_TURBINE, GAMMA_GG)
mdot_gg_900, dh_900 = ep.gg_flow_fraction(tp["power_total_w"], 900.0, CP_GG, ETA_TURBINE, PR_TURBINE, GAMMA_GG)

print()
print("=" * 78)
print("GAS-GENERATOR FLOW FRACTION")
print("=" * 78)
print(f"  turbine inlet 1050 K (single-crystal, H-4): mdot_gg = {mdot_gg_1050:.2f} kg/s = {mdot_gg_1050/MDOT*100:.2f}% of total flow")
print(f"  turbine inlet  900 K (H-3-era comparison):  mdot_gg = {mdot_gg_900:.2f} kg/s = {mdot_gg_900/MDOT*100:.2f}% of total flow")
delta_frac = (mdot_gg_900 - mdot_gg_1050) / MDOT * 100
print(f"  single-crystal turbine saves {delta_frac:.2f}% of total flow vs. the H-3-era inlet temp")

# ===========================================================================
# 6) ENGINE-LEVEL ISP — mass-average the main-chamber flow with the GG-dump
#    flow. The chamber Isp computed above is for the (1-x) fraction that
#    goes through the injector/chamber/nozzle at the design MR; the x
#    fraction (~3.5%) is fuel-rich GG exhaust dumped into the skirt at low
#    pressure, only partially expanded. ISP_GG_DUMP_FRACTION is a documented
#    engineering assumption (not derived): a skirt-dumped, fuel-rich,
#    lower-pressure-ratio exhaust is assumed to deliver ~55% of the main
#    chamber's specific impulse. This is the correction that turns "chamber
#    performance" into "what the engine actually delivers."
# ===========================================================================
ISP_GG_DUMP_FRACTION = 0.55
x = mdot_gg_1050 / MDOT

def engine_isp(chamber_isp):
    return (1.0 - x) * chamber_isp + x * (ISP_GG_DUMP_FRACTION * chamber_isp)

base_isp_vac_eng = engine_isp(base["isp_vac_s"])
base_isp_sl_eng = engine_isp(base["isp_sl_s"])
sub_isp_vac_eng = engine_isp(sub["isp_vac_s"])
sub_isp_sl_eng = engine_isp(sub["isp_sl_s"])

thrust_base_vac_eng = MDOT * base_isp_vac_eng * G0
thrust_base_sl_eng = MDOT * base_isp_sl_eng * G0
thrust_sub_vac_eng = MDOT * sub_isp_vac_eng * G0
thrust_sub_sl_eng = MDOT * sub_isp_sl_eng * G0

print()
print("=" * 78)
print(f"ENGINE-LEVEL ISP (chamber Isp mass-averaged with {x*100:.1f}% GG-dump flow "
      f"@ {ISP_GG_DUMP_FRACTION*100:.0f}% of chamber Isp) — THESE ARE THE .cfg NUMBERS")
print("=" * 78)
print(f"  {'':14}{'eps '+str(EPS_BASE)+' (base)':>18}{'eps '+str(EPS_SUB)+' (20AR)':>18}")
print(f"  {'Isp vac [s]':14}{base_isp_vac_eng:18.1f}{sub_isp_vac_eng:18.1f}")
print(f"  {'Isp sl  [s]':14}{base_isp_sl_eng:18.1f}{sub_isp_sl_eng:18.1f}")
print(f"  {'thrust vac [kN]':14}{thrust_base_vac_eng/1e3:18.1f}{thrust_sub_vac_eng/1e3:18.1f}")
print(f"  {'thrust sl  [kN]':14}{thrust_base_sl_eng/1e3:18.1f}{thrust_sub_sl_eng/1e3:18.1f}")
print(f"  {'minThrust @50% vac [kN]':24}{thrust_base_vac_eng*THROTTLE_FLOOR/1e3:12.1f}{thrust_sub_vac_eng*THROTTLE_FLOOR/1e3:18.1f}")

# ===========================================================================
# 7) THROTTLE SWEEP — separation onset + injector stiffness, both nozzles
# ===========================================================================
DP_INJ_NOMINAL = 0.25 * PC  # purpose-built platelet injector, stiff for deep throttle
throttle_grid = np.arange(0.50, 1.001, 0.02)

rows_base = ep.throttle_sweep(PC, EPS_BASE, base["gamma"], base["pe_pc"], PA_SEA_LEVEL,
                               DP_INJ_NOMINAL, throttle_grid)
rows_sub = ep.throttle_sweep(PC, EPS_SUB, sub["gamma"], sub["pe_pc"], PA_SEA_LEVEL,
                              DP_INJ_NOMINAL, throttle_grid)

onset_base = ep.separation_onset_throttle(rows_base)
onset_sub = ep.separation_onset_throttle(rows_sub)

dp_over_pc_at_floor_base = [r for r in rows_base if abs(r["throttle"] - THROTTLE_FLOOR) < 1e-9][0]["dp_inj_over_pc"]

print()
print("=" * 78)
print("THROTTLE SWEEP (sea level)")
print("=" * 78)
print(f"  base (eps {EPS_BASE}) separation onset (sea level): {onset_base*100:.0f}% throttle"
      if onset_base else f"  base (eps {EPS_BASE}) never reattaches down to {throttle_grid[0]*100:.0f}%")
print(f"  20AR (eps {EPS_SUB}) separation onset (sea level): {onset_sub*100:.0f}% throttle"
      if onset_sub else f"  20AR (eps {EPS_SUB}) never reattaches down to {throttle_grid[0]*100:.0f}%")
print(f"  injector dP/Pc at {THROTTLE_FLOOR*100:.0f}% throttle: {dp_over_pc_at_floor_base:.3f}"
      f"  ({'STABLE' if dp_over_pc_at_floor_base > 0.10 else 'MARGINAL/UNSTABLE'}, threshold ~0.10)")
print()
print(f"  {'throttle':>9}{'Pc [MPa]':>10}{'base Pe/Pa':>12}{'base sep?':>11}{'20AR Pe/Pa':>12}{'20AR sep?':>11}")
for rb, rs in zip(rows_base, rows_sub):
    print(f"  {rb['throttle']*100:8.0f}%{rb['pc_pa']/1e6:10.2f}{rb['pe_over_pa']:12.3f}"
          f"{str(rb['separated_sl']):>11}{rs['pe_over_pa']:12.3f}{str(rs['separated_sl']):>11}")
