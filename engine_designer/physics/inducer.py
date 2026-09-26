"""
Pump-inlet INDUCER suction model: how much NPSH a rotor at speed n needs, and
the fastest speed a given NPSH available allows (turbopump Round 1).

This is the design procedure of [SP-8052 §3.1.3.1], nothing more:

- Brumfield optimum [SP-8052 §2.1.3 eq. 2-7]: a design blade cavitation number
  K fixes the optimum inlet flow coefficient phi_opt = sqrt(K/(2(1+K))) and the
  maximum hub-corrected suction specific speed S's = 5055/((1+K)^0.25 K^0.5);
  Ss = S's*sqrt(1-nu^2). US units (rpm, gpm, ft) throughout, as in
  turbopump_sizing.py.
- Tip-clearance loss [SP-8052 eq. 54]: Ss x (1 - k_s*sqrt(c/L)), at the
  minimum practical clearance (fuel c/L 0.005, oxidizer 0.020 [§3.2.8]).
- Thermodynamic suppression head (TSH), the "thermodynamic effect" of LOX/LH2
  [SP-8052 §2.1.4 p.16]: an EMPIRICAL per-fluid allowance added to the tank
  NPSH ("no theoretical prediction is attempted"). Anchors: F-1 LOX 11 ft at
  163 degR, J-2 LH2 250 ft at 38 degR; scaled with vapor pressure ("rises
  almost as a linear function of vapor pressure"). No data for CH4/RP-1/the
  storables -> 0 (conservative, an ideal fluid).
- Flight NPSH required at speed n = max[(n Q^0.5/Ss)^(4/3) - TSH,
  Z_min*c_m^2/2g], the second term the [SP-8109 §3.2.1.2] TSH-credited NPSH
  factor (LOX 2.3, LH2 1.3, others 3.0) - it floors the TSH credit. c_m is the
  inducer-inlet meridional velocity at phi_opt on the [SP-8052 eq. 8] tip
  diameter. Both terms scale as n^(4/3), so suction_limited_rpm inverts
  exactly.

The ONE calibrated constant is DESIGN_CAVITATION_NUMBER (Tier 2): back-solved so
Brumfield at nu 0.3 gives [SP-8109 §3.2.1.2]'s recommended maximum inducer Ss of
40,000. Validated against SP-8107 Table II's real pumps (REAL_PUMP_SUCTION_DATA):
every inducer pump there runs at or below this cap at its own specified NPSH,
and the F-1 LOX pump sits just under it (it was designed at the suction limit).
See validate/suction.py.
"""
import math
from dataclasses import dataclass

from . import thermo_tables

G_FT_S2 = 32.174
_M3S_TO_GPM = 15850.323
_FT_TO_M = 0.3048

# --- Brumfield design point -------------------------------------------------
BRUMFIELD_SS_COEFF = 8147.0      # S's = 8147 phi^0.5 tau^-0.75 [SP-8052 eq. 3]
BRUMFIELD_MAX_SS_COEFF = 5055.0  # max S's = 5055/((1+K)^0.25 K^0.5) [eq. 7]
# Tier 2: the design blade cavitation number. Back-solved so the Brumfield
# maximum at nu = HUB_TIP_RATIO lands on [SP-8109 §3.2.1.2]'s "maximum suction
# specific speed of 40,000 for the inducer is recommended"; it sits inside
# [SP-8052 p.12]'s measured thin-blade K* 0.006-0.01 x its "attained values are
# approximately two to three times greater" (0.012-0.03), and gives phi_opt
# 0.0845, inside SP-8052 Table I's real 0.074-0.116.
DESIGN_CAVITATION_NUMBER = 0.0145
HUB_TIP_RATIO = 0.3              # rear-drive (overhung) inducer 0.2-0.4 [SP-8052 §3.1.2]
# Minimum practical tip clearance / blade radial length [SP-8052 §3.2.8]: LOX
# pumps run looser (rub margin). Ss loss coefficient k_s 0.50-0.65 [eq. 54],
# mid-band.
TIP_CLEARANCE_C_OVER_L = {"fuel": 0.005, "ox": 0.020}
TIP_CLEARANCE_KS = 0.575

# --- thermodynamic suppression head -----------------------------------------
# (TSH ft, fluid temperature K) [SP-8052 §2.1.4 p.16]: F-1 Mark 10 LOX pump 11 ft
# at 163 degR; J-2 Mark 15-F LH2 pump 250 ft at 38 degR. "Presently established
# empirical values", used "with considerable reservation" on other pumps.
TSH_ANCHORS = {"LOX": (11.0, 163.0 / 1.8), "LH2": (250.0, 38.0 / 1.8)}
# TSH-credited NPSH factor Z = NPSH/(c_m^2/2g) [SP-8109 §3.2.1.2]: 3.0 for a
# low-vapor-pressure (ideal) fluid, 2.3 LOX/LF2, 1.3 LH2 - the floor on the
# flight NPSH required however large the TSH credit.
Z_MIN = {"LOX": 2.3, "LH2": 1.3}
Z_MIN_IDEAL = 3.0

# SP-8107 Table II "Chief Features of Operational Turbopumps" (p.4): engine,
# propellant, density lbm/ft3, rated inlet pressure psia, gpm, rpm,
# NPSH_min ft (contractually specified - the NPSH the pump must run at),
# NPSH_crit ft (2 % head drop; None = not given). `inducer` False only where a
# source says so (Atlas MA-5 sustainer RP-1 pump [SP-8109 Fig. 4-5]).
REAL_PUMP_SUCTION_DATA = (
    # engine        prop     rho   p_in    gpm    rpm  npsh_min crit  inducer
    ("A-7",         "LOX",   71.4, 49.8,  1290,  4718,  18,  11,  True),
    ("A-7",         "alcohol", 56.6, 42.5, 1190,  4718,  40,  35,  True),
    ("MB-3",        "LOX",   71.4, 53.0,  2870,  6303,  55, None, True),
    ("MB-3",        "RJ-1",  53.2, 48.0,  1700,  6303,  34, None, True),
    ("LR87-AJ-3",   "LOX",   71.4, 53.0,  2600,  7949,  40, None, True),
    ("LR87-AJ-3",   "RP-1",  50.5, 22.0,  1630,  8780,  30, None, True),
    ("LR91-AJ-3",   "LOX",   71.4, 35.0,  1100,  8945,  31, None, True),
    ("LR91-AJ-3",   "RP-1",  50.5, 42.0,   659, 25207, 100, None, True),
    ("H-1",         "LOX",   70.8, 65.0,  3410,  6680,  35,  25,  True),
    ("H-1",         "RP-1",  50.5, 57.0,  2130,  6680,  35,  28,  True),
    ("MA-5 sust.",  "LOX",   71.4, 53.0,  1200, 10160,  30,  14,  True),
    ("MA-5 sust.",  "RP-1",  50.5, 77.0,   745, 10160,  85,  60,  False),
    ("MA-5 boost.", "LOX",   71.4, 50.0,  2862,  6314,  40, None, True),
    ("MA-5 boost.", "RP-1",  50.5, 73.0,  1867,  6314,  33, None, True),
    ("F-1",         "LOX",   71.4, 65.0, 25200,  5488,  65,  60,  True),
    ("F-1",         "RP-1",  50.5, 45.0, 15250,  5488,  70,  55,  True),
    ("YLR81-BA-11", "IRFNA", 98.2, 24.0,   180, 25389,  12, None, True),
    ("YLR81-BA-11", "UDMH",  49.4, 24.0,   139, 14410,  34, None, True),
    ("YLR87-AJ-7",  "N2O4",  90.3, 84.0,  2700,  8382,  44, None, True),
    ("YLR87-AJ-7",  "A-50",  56.1, 33.5,  2180,  9209,  43, None, True),
    ("YLR91-AJ-7",  "N2O4",  90.3, 41.0,  1010,  8405,  30, None, True),
    ("YLR91-AJ-7",  "A-50",  56.1, 44.5,   904, 23685, 100, None, True),
    ("RL10A-3-3",   "LOX",   68.8, 60.5,   184, 12100,  17, None, True),
    ("RL10A-3-3",   "LH2",   4.35, 30.0,   581, 30250, 132, None, True),
    ("J-2",         "LOX",   70.8, 39.0,  2920,  8753,  25,  18,  True),
    ("J-2",         "LH2",   4.4,  30.0,  8530, 27130, 130,  75,  True),
)
# Without an integral inducer the [SP-8109 §3.2.1.2] limit is Ss 12,000.
SS_NO_INDUCER = 12_000.0

# SP-8052 Table I (water Ss at 10 % head drop): (name, phi_d, nu, Ss) - the
# Brumfield-at-design-phi cross-check.
SP8052_TABLE_I = (
    ("Thor Mark 3 LOX",          0.116,  0.31, 28_500.0),
    ("J-2 Mark 15 LOX",          0.109,  0.20, 34_300.0),
    ("X-8 Mark 19 LOX",          0.106,  0.23, 31_200.0),
    ("X-8 Mark 19 LOX shrouded", 0.05,   0.19, 58_000.0),
    ("J-2 Mark 15 LH2 (e)",      0.0942, 0.42, 43_200.0),
    ("J-2 Mark 15 LH2 (f)",      0.0735, 0.38, 44_200.0),
)


def brumfield_phi_opt(k):
    """Optimum inlet flow coefficient for blade cavitation number K [eq. 6]."""
    return math.sqrt(k / (2.0 * (1.0 + k))) if k > 0 else 0.0


def brumfield_max_ss_prime(k):
    """Maximum hub-corrected suction specific speed S's at K [eq. 7]."""
    return BRUMFIELD_MAX_SS_COEFF / ((1.0 + k) ** 0.25 * math.sqrt(k)) if k > 0 else 0.0


def brumfield_ss_at_phi(phi, nu):
    """Water Ss an inducer designed at flow coefficient `phi` (hub ratio nu)
    achieves on the Brumfield optimum: K = 2phi^2/(1-2phi^2) [eq. 5] -> eq. 7 ->
    eq. 4. (The Table I cross-check.)"""
    k = 2.0 * phi * phi / (1.0 - 2.0 * phi * phi)
    return brumfield_max_ss_prime(k) * math.sqrt(1.0 - nu * nu)


def tip_clearance_factor(c_over_l, k_s=TIP_CLEARANCE_KS):
    """Suction-specific-speed multiplier for tip clearance [SP-8052 eq. 54]."""
    return 1.0 - k_s * math.sqrt(max(c_over_l, 0.0))


def design_suction_specific_speed(leg, k=DESIGN_CAVITATION_NUMBER, nu=HUB_TIP_RATIO):
    """Water-basis Ss of a Brumfield-optimum inducer at K, after the leg's
    minimum-practical tip-clearance loss."""
    return (brumfield_max_ss_prime(k) * math.sqrt(1.0 - nu * nu)
            * tip_clearance_factor(TIP_CLEARANCE_C_OVER_L.get(leg, TIP_CLEARANCE_C_OVER_L["ox"])))


def tip_diameter_ft(q_gpm, n_rpm, phi, nu=HUB_TIP_RATIO):
    """Inducer inlet tip diameter, ft [SP-8052 eq. 8]: 0.37843 [Q/((1-nu^2) n phi)]^(1/3)."""
    if q_gpm <= 0 or n_rpm <= 0 or phi <= 0:
        return 0.0
    return 0.37843 * (q_gpm / ((1.0 - nu * nu) * n_rpm * phi)) ** (1.0 / 3.0)


def tip_diameter_m(q_m3s, n_rpm, phi=None, nu=HUB_TIP_RATIO):
    """tip_diameter_ft in metres from SI flow; phi defaults to the design phi_opt."""
    phi = brumfield_phi_opt(DESIGN_CAVITATION_NUMBER) if phi is None else phi
    return tip_diameter_ft(q_m3s * _M3S_TO_GPM, n_rpm, phi, nu) * _FT_TO_M


def meridional_velocity_head_ft(q_gpm, n_rpm, phi, nu=HUB_TIP_RATIO):
    """c_m^2/2g (ft) at the inducer inlet: c_m = phi * pi D n / 60."""
    d = tip_diameter_ft(q_gpm, n_rpm, phi, nu)
    c_m = phi * math.pi * d * n_rpm / 60.0
    return c_m * c_m / (2.0 * G_FT_S2)


def thermodynamic_suppression_head_ft(propellant, t_k):
    """Empirical TSH (ft) [SP-8052 §2.1.4], the propellant's anchor scaled with
    vapor pressure. 0 for a propellant with no anchor or no saturation data."""
    anchor = TSH_ANCHORS.get(propellant)
    if anchor is None or not thermo_tables.has_saturation(propellant):
        return 0.0
    tsh, t_ref = anchor
    pv = thermo_tables.saturation(propellant, t_k)["p_sat_pa"]
    pv_ref = thermo_tables.saturation(propellant, t_ref)["p_sat_pa"]
    return tsh * pv / pv_ref if pv_ref > 0 else 0.0


def z_min(propellant):
    """[SP-8109 §3.2.1.2] TSH-credited NPSH factor floor for the propellant."""
    return Z_MIN.get(propellant, Z_MIN_IDEAL)


@dataclass(frozen=True)
class SuctionSpec:
    """Everything size_pump needs to evaluate one pump's suction limit.
    `npsh_available_ft` <= 0 means the inlet is at/below vapor pressure: no
    finite speed satisfies it and suction_limited_rpm returns 0 (the caller
    leaves the rotor speed alone and raises a red checklist row instead)."""
    npsh_available_ft: float
    ss_water: float
    tsh_ft: float = 0.0
    z_min: float = Z_MIN_IDEAL
    phi: float = 0.0
    nu: float = HUB_TIP_RATIO
    propellant: str = ""
    leg: str = ""
    has_inducer: bool = True


def make_spec(propellant, leg, t_k, npsh_available_ft, *, has_inducer=True):
    """The computed-model spec for one pump leg ("fuel"/"ox") pumping
    `propellant` at inlet temperature t_k with the given NPSH available (ft)."""
    phi = brumfield_phi_opt(DESIGN_CAVITATION_NUMBER)
    ss = design_suction_specific_speed(leg) if has_inducer else SS_NO_INDUCER
    return SuctionSpec(npsh_available_ft=float(npsh_available_ft), ss_water=ss,
                       tsh_ft=thermodynamic_suppression_head_ft(propellant, t_k),
                       z_min=z_min(propellant), phi=phi, nu=HUB_TIP_RATIO,
                       propellant=propellant, leg=leg, has_inducer=has_inducer)


def npsh_required_ft(n_rpm, q_gpm, spec):
    """Flight NPSH (ft) a pump at n_rpm / q_gpm needs: the water-basis Ss
    requirement less the TSH credit, floored at Z_min velocity heads."""
    if n_rpm <= 0 or q_gpm <= 0 or spec.ss_water <= 0:
        return 0.0
    water = (n_rpm * math.sqrt(q_gpm) / spec.ss_water) ** (4.0 / 3.0)
    floor = spec.z_min * meridional_velocity_head_ft(q_gpm, n_rpm, spec.phi, spec.nu)
    return max(water - spec.tsh_ft, floor)


def suction_limited_rpm(q_gpm, spec):
    """Fastest rotor speed whose npsh_required_ft equals spec.npsh_available_ft
    (exact: both terms of npsh_required_ft scale as n^(4/3)). 0 if undefined
    (no flow, or no NPSH available)."""
    a = spec.npsh_available_ft
    if q_gpm <= 0 or a <= 0 or spec.ss_water <= 0:
        return 0.0
    n_water = spec.ss_water * (a + spec.tsh_ft) ** 0.75 / math.sqrt(q_gpm)
    per_n = meridional_velocity_head_ft(q_gpm, 1.0, spec.phi, spec.nu) * spec.z_min
    n_floor = (a / per_n) ** 0.75 if per_n > 0 else float("inf")
    return min(n_water, n_floor)


def real_pump_cap_rows():
    """SP-8107 Table II pumps vs the model: (engine, prop, rpm, cap, ratio,
    inducer). Each pump's own NPSH_min is its NPSH available; TSH at the anchor
    temperature for LOX/LH2 (the only fluids with data)."""
    rows = []
    for eng, prop, _rho, _pin, gpm, rpm, npsh_min, _crit, ind in REAL_PUMP_SUCTION_DATA:
        leg = "fuel" if prop in ("LH2", "RP-1", "RJ-1", "alcohol", "UDMH", "A-50") else "ox"
        t_ref = TSH_ANCHORS.get(prop, (0.0, 293.15))[1]
        spec = make_spec(prop, leg, t_ref, npsh_min, has_inducer=ind)
        cap = suction_limited_rpm(gpm, spec)
        rows.append((eng, prop, rpm, cap, rpm / cap if cap > 0 else float("inf"), ind))
    return rows


if __name__ == "__main__":
    # 1. Brumfield constant: eq. 7's 5055 == eq. 3's 8147 at the optimum.
    assert abs(BRUMFIELD_SS_COEFF * 2 ** -0.25 * 1.5 ** -0.75 - BRUMFIELD_MAX_SS_COEFF) < 2.0
    k = DESIGN_CAVITATION_NUMBER
    ss0 = brumfield_max_ss_prime(k) * math.sqrt(1.0 - HUB_TIP_RATIO ** 2)
    phi = brumfield_phi_opt(k)
    print(f"design K {k}: phi_opt {phi:.4f}, S's {brumfield_max_ss_prime(k):,.0f}, "
          f"Ss(nu {HUB_TIP_RATIO}) {ss0:,.0f}; after clearance fuel "
          f"{design_suction_specific_speed('fuel'):,.0f} / ox {design_suction_specific_speed('ox'):,.0f}")
    # 2. the calibration target: SP-8109's 40,000 recommended maximum
    assert abs(ss0 - 40_000.0) / 40_000.0 < 0.01, ss0
    assert 0.074 <= phi <= 0.116, phi
    # 3. Brumfield vs SP-8052 Table I: >= 4 of 6 within 10 %
    hits = 0
    for name, ph, nu, ss_real in SP8052_TABLE_I:
        pred = brumfield_ss_at_phi(ph, nu)
        d = pred / ss_real - 1.0
        hits += abs(d) <= 0.10
        print(f"  Table I {name:<26} phi {ph:.4f} pred {pred:7,.0f} real {ss_real:7,.0f} {d:+.1%}")
    assert hits >= 4, hits
    # 4. TSH anchors reproduce; LOX TSH rises with temperature; no data -> 0
    for prop, (tsh, t) in TSH_ANCHORS.items():
        assert abs(thermodynamic_suppression_head_ft(prop, t) - tsh) < 1e-9
    assert (thermodynamic_suppression_head_ft("LOX", 95.0)
            > thermodynamic_suppression_head_ft("LOX", 90.0)
            > thermodynamic_suppression_head_ft("LOX", 80.0))
    assert thermodynamic_suppression_head_ft("RP-1", 293.15) == 0.0
    assert thermodynamic_suppression_head_ft("N2O4", 293.15) == 0.0
    # 5. exact inversion, both branches (water-Ss and Z-floor)
    for prop, leg, t, npsh, gpm in (("LOX", "ox", 90.56, 65.0, 25_200.0),
                                    ("LH2", "fuel", 21.11, 130.0, 8_530.0),
                                    ("LH2", "fuel", 21.11, 5.0, 8_530.0),
                                    ("RP-1", "fuel", 293.15, 70.0, 15_250.0)):
        sp = make_spec(prop, leg, t, npsh)
        n = suction_limited_rpm(gpm, sp)
        assert abs(npsh_required_ft(n, gpm, sp) - npsh) < 1e-6 * npsh, (prop, n)
    assert suction_limited_rpm(1000.0, make_spec("LOX", "ox", 90.0, 0.0)) == 0.0
    assert suction_limited_rpm(1000.0, make_spec("LOX", "ox", 90.0, -5.0)) == 0.0
    # 6. SP-8107 Table II: every real pump at or below the model cap at its own
    # NPSH_min (the storable IRFNA - no TSH data - is the one report-only row).
    print(f"  {'SP-8107 Table II':<24} {'rpm':>7} {'cap':>8} {'rpm/cap':>8}")
    for eng, prop, rpm, cap, ratio, ind in real_pump_cap_rows():
        print(f"  {eng:<12} {prop:<11} {rpm:7,.0f} {cap:8,.0f} {ratio:8.2f}"
              f"{'' if ind else '  (no inducer)'}")
        if prop != "IRFNA":
            assert ratio <= 1.0, (eng, prop, ratio)
    f1_ox = next(r for r in real_pump_cap_rows() if r[0] == "F-1" and r[1] == "LOX")
    assert 0.85 <= f1_ox[4] <= 1.0, f1_ox
    print("inducer self-test OK")
