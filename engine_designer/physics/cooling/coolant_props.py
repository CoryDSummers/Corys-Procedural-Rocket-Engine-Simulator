"""Coolant (fuel) properties and capacity: cp, transport, density, dT limits, flat-model temperature rise / feasibility.

Part of the physics/cooling/ package (split verbatim out of the former
single-file cooling.py - see cooling/__init__.py for the package overview)."""

from ..propellant_pairs import alias_variants

# --- coolant side (owned here; physics/expander.py imports these) -------------
# Max practical coolant (fuel-side) temperature rise before the turbine / before
# the jacket outlet, per propellant pair. Hydrocarbons coke (crack into solid
# channel-fouling deposits) well below hydrogen's limits - this is why real
# expander-cycle engines are LH2-only and why a hydrocarbon regen jacket at high
# Pc runs out of margin.
MAX_COOLANT_DELTA_T_K = {
    "LOX/LH2": 500.0,
    "LOX/RP-1": 120.0,
    "LOX/CH4": 250.0,        # methane cokes far less than RP-1, well above LH2's limit
    "N2O4/MMH": 150.0,
    "LOX/UDMH": 150.0,       # UDMH: same hydrazine-family decomposition-limited regime as MMH
    "N2O4/UDMH": 150.0,      # (Tier 3 transfer; [Sutton Table 8-5]: UDMH boils 400 K at 1 MPa,
                             # 489 K at 3.45 MPa, critical 522 K / 6.06 MPa)
}
FUEL_CP_J_KGK = {
    "LOX/LH2": 14300.0,
    "LOX/RP-1": 2100.0,
    "LOX/CH4": 3450.0,       # liquid/supercritical methane
    "N2O4/MMH": 2900.0,
    "LOX/UDMH": 2810.0,      # [Sutton Table 7-1 p.245] UDMH 0.672 kcal/kg-K at 298 K
    "N2O4/UDMH": 2810.0,
}

def coolant_temp_rise_k(total_heat_w, mdot_coolant_kgs, cp_j_kgk):
    """Bulk coolant temperature rise if `total_heat_w` is dumped into a coolant
    stream of `mdot_coolant_kgs` at specific heat `cp_j_kgk`."""
    if not mdot_coolant_kgs or not cp_j_kgk or mdot_coolant_kgs <= 0 or cp_j_kgk <= 0:
        return 0.0
    return total_heat_w / (mdot_coolant_kgs * cp_j_kgk)


def coolant_limit_k(pair):
    """Coking/boiling coolant delta-T limit for `pair`, or None if not tabulated."""
    return MAX_COOLANT_DELTA_T_K.get(pair)


def regen_feasible(delta_t_k, pair):
    """True if a regen jacket carrying the fuel can absorb the wall heat within
    the coking/boiling limit. Unknown pair -> True (no basis to warn)."""
    limit = MAX_COOLANT_DELTA_T_K.get(pair)
    return limit is None or delta_t_k <= limit


# Per-pair coolant (fuel) transport at jacket conditions: (conductivity W/m-K,
# dynamic viscosity Pa.s). Representative liquid / supercritical values; cp and
# density come from FUEL_CP_J_KGK / COOLANT_DENSITY_KG_M3 below.
COOLANT_TRANSPORT = {
    "LOX/RP-1": (0.13, 7.5e-4),
    "LOX/LH2":  (0.10, 1.3e-5),
    "LOX/CH4":  (0.19, 1.1e-4),
    "N2O4/MMH": (0.20, 5.8e-4),
    # UDMH: viscosity 0.48 cP at 300 K [Sutton Table 7-1 p.245]; conductivity NOT in
    # Sutton - MMH's 0.20 W/m-K carried over (Tier 3 transfer, same fuel family).
    "LOX/UDMH": (0.20, 4.8e-4),
    "N2O4/UDMH": (0.20, 4.8e-4),
}
COOLANT_DENSITY_KG_M3 = {              # fuel density in the jacket (kept local to avoid
    "LOX/RP-1": 810.0,                 # importing combustion.py from here)
    "LOX/LH2": 71.0,
    "LOX/CH4": 422.0,
    "N2O4/MMH": 880.0,
    "LOX/UDMH": 784.0,                 # [Sutton Table 7-1 p.245] UDMH s.g. 0.784
    "N2O4/UDMH": 784.0,
    # chilled RP-1 at 266 K (has a coolant table; this is only the no-table path)
    "LOX/RP-1 (subcooled)": 831.9,
}
# Subcooled LOX/RP-1: same fuel, so the same limits/cp/transport (its density above
# and its own coolant table differ).
for _t in (MAX_COOLANT_DELTA_T_K, FUEL_CP_J_KGK, COOLANT_TRANSPORT):
    alias_variants(_t)
_COOLANT_TRANSPORT_FALLBACK = (0.15, 5.0e-4)
_COOLANT_DENSITY_FALLBACK = 800.0
