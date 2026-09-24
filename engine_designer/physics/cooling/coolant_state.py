"""Coolant (fuel) thermophysical state for the regen / dump coolant marches.

CoolantModel(pair, p_pa) gives temperature-dependent density, cp, viscosity,
conductivity and enthalpy at the jacket pressure, from the baked CoolProp
tables (physics/thermo_tables.py - parahydrogen, methane, n-dodecane as the
RP-1 surrogate). This replaces the old per-pair CONSTANTS, which paired LH2's
saturated-LIQUID density/viscosity with a warm-GAS cp (implied Pr 1.86) and so
mis-sized every LH2 jacket (2026-09-23 audit, C1).

Pairs without a coolant table (N2O4/MMH, Aerozine-50/NTO, the monopropellants)
fall back to the legacy constants (coolant_props.py) with h = cp*(T - T_ref);
`source` says which, and `has_data` is False when even the constants had to be
generic defaults - the design stage turns that into a checklist warning instead
of the old silent zero / TypeError / KeyError.
"""
from __future__ import annotations

import numpy as np

from .. import thermo_tables
from .coolant_props import (
    COOLANT_DENSITY_KG_M3,
    COOLANT_TRANSPORT,
    FUEL_CP_J_KGK,
    _COOLANT_DENSITY_FALLBACK,
    _COOLANT_TRANSPORT_FALLBACK,
)

CP_FALLBACK_J_KGK = 2100.0   # the old march fallback (kerosene-like)
_H_REF_T_K = 0.0             # enthalpy datum for the constant-property fallback


class CoolantModel:
    def __init__(self, pair, p_pa):
        self.pair = pair
        self.p_pa = max(float(p_pa), 1.0e5)
        col = thermo_tables.coolant_column(pair, self.p_pa)
        self.table = col is not None
        if self.table:
            st = thermo_tables.coolant_state(pair, 300.0, self.p_pa)
            self.source = f"table:{st['fluid']}" + (" (surrogate)" if st["surrogate"] else "")
            self.has_data = True
            self._t = col["t_k"]
            self._col = col
            self.t_max_k = float(col["t_k"][-1])
        else:
            self.has_data = (pair in FUEL_CP_J_KGK and pair in COOLANT_TRANSPORT
                             and pair in COOLANT_DENSITY_KG_M3)
            self.source = "constant" if self.has_data else "generic fallback"
            self._cp = FUEL_CP_J_KGK.get(pair, CP_FALLBACK_J_KGK)
            self._k, self._mu = COOLANT_TRANSPORT.get(pair, _COOLANT_TRANSPORT_FALLBACK)
            self._rho = COOLANT_DENSITY_KG_M3.get(pair, _COOLANT_DENSITY_FALLBACK)
            self.t_max_k = float("inf")

    def props(self, t_k):
        """(rho kg/m3, cp J/kg-K, mu Pa.s, k W/m-K) at temperature t_k (table
        edge-clamped)."""
        if self.table:
            c, t = self._col, self._t
            return (float(np.interp(t_k, t, c["rho_kg_m3"])), float(np.interp(t_k, t, c["cp_j_kgk"])),
                    float(np.interp(t_k, t, c["mu_pa_s"])), float(np.interp(t_k, t, c["k_w_mk"])))
        return self._rho, self._cp, self._mu, self._k

    def h(self, t_k):
        if self.table:
            return float(np.interp(t_k, self._t, self._col["h_j_kg"]))
        return self._cp * (t_k - _H_REF_T_K)

    def t_from_h(self, h_j_kg):
        if self.table:
            return float(np.interp(h_j_kg, self._col["h_j_kg"], self._t))
        return _H_REF_T_K + h_j_kg / self._cp

    def heat_capacity_to(self, t_in_k, dt_k):
        """Enthalpy rise [J/kg] from t_in to t_in + dt (the enthalpy-exact
        replacement for cp*dT across the supercritical cp peak)."""
        return self.h(t_in_k + dt_k) - self.h(t_in_k)
