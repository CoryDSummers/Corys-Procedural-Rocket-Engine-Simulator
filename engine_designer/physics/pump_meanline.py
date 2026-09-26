"""
Pump MEANLINE hydraulics (turbopump Round 2): velocity triangles, slip, blade
count, outlet width, volute/diffuser, and a loss build-up that gives the pump
efficiency - replacing the Ns-bell correlation (turbopump_efficiency.
pump_efficiency, kept as a cross-check) when EngineDesign.pump_model is
"meanline".

Centrifugal stage [SP-8109 §2.3-2.4, §3.3-3.4; Huzel §6.3]:
  - slip: SP-8109's own eq. 17 (M = c_u2inf/c_u2), X_L 0.25 (fitted: reproduces
    the Fig. 16 blade carpet with eta_h 0.82); psi = eta_h (1 - phi2 cot b2)/M
  - blade count z = beta2/3 [Huzel eq. 6-44], raised/lowered until the outlet
    flow coefficient sits in SP-8109's 0.05-0.30; splitters above 8 blades
    (4-8 inlet blades [SP-8109 §3.3.1.3])
  - b2 from continuity with Huzel's discharge contraction factor
  - losses: channel friction (Haaland, 63 uin cast finish [SP-8109 §2.4.4]),
    diffusion past W2/W1 0.7 (Tier 3), volute/diffuser zeta*c2^2/2g (Huzel:
    70-90 % of the discharge kinetic head recovered), wear-ring leakage
    (0.0005 D2 clearance, Q = K pi D c sqrt(2 g dh) [SP-8109 p.34, Fig. 22]),
    disk friction (Tier 3: no coefficient in the reference set), mechanical
    (20 % at a 1 in impeller -> negligible at 10 in [SP-8109 p.8]), and the
    suction-specific-speed penalty [SP-8109 Fig. 9]
  - ONE calibrated multiplier K_HYD on the hydraulic losses (Tier 2), fitted to
    CENTRIFUGAL_ANCHORS (real pumps, ±0.08 like turbopump_efficiency)
Axial stage [SP-8125 §2.2; Huzel §6.4]: pitchline, reaction 0.5, free vortex,
  diffusion factor eqs. 5-6, Fig. 8 profile loss; ONE multiplier K_AX (Tier 2)
  fitted to AXIAL_ANCHORS (J-2 Mark 15-F, M-1).

Also returns an approximate H-Q curve (a sketch, labelled so - maps are Round 5)
and the geometry the Turbopump Detail tab draws. Pure module (math only); run
`python3 -m engine_designer.physics.pump_meanline` for the self-test + fit.
"""
import functools
import math
from dataclasses import dataclass

G = 9.80665
_FT = 0.3048
_IN = 0.0254
_GPM_TO_M3S = 6.30902e-5

# --- centrifugal: geometry rules ---------------------------------------------
X_L = 0.25                 # eq. 17 axial-length ratio; with ETA_H 0.82 reproduces Fig. 16
                           # (Round 2 fit of SP-8109's own carpet; Tier 2)
DELTA_DEFAULT = 0.65       # Dt1/Dt2 when no inducer diameter is given (Fig. 16 basis)
DELTA_MAX = 0.80           # impeller eye range: fleet Dt1/Dt2 0.44-0.81 [SP-8109 Figs. 5, 13]; a
DELTA_MIN = 0.40           # larger inducer tapers down to it (Huzel SC 6-7's tapered inducer)
DELTA_FLEET_AT_1570 = 0.69  # fleet_delta(): J-2 LOX at Ns 1570 [SP-8109 Fig. 5]
DELTA_FLEET_EXP = 0.45      # fitted on the Fig. 5 fleet points (Tier 2)
SS_FLEET_REF = 38_000.0     # the fleet's design Ss (F-1 LOX ~38k, J-2 LOX ~42k at NPSH_min
                            # [SP-8107 Table II])
DELTA_SS_EXP = 0.32         # delta ~ Ss^0.32 from SP-8109 Fig. 8 (0.45 @ 10k, 0.70 @ 40k)
CM2_OVER_CM1_MIN = 1.0     # discharge meridional velocity 1-1.5 x the inlet [SP-8109 §3.3.1.2]
Z_CAP_MIN = 12             # auto blade count may rise to max(12, 28 sin beta2)
INLET_HUB_RATIO = 0.30     # impeller eye hub/tip (= inducer.HUB_TIP_RATIO)
EPS1 = 0.85                # inlet contraction factor [Huzel eq. 6-42: 0.75-0.9]
EPS2 = 0.90                # discharge contraction factor [Huzel eq. 6-43: 0.85-0.95]
Z_PER_DEG = 1.0 / 3.0      # z = beta2/3 [Huzel eq. 6-44]
Z_MIN_BLADES = 5           # Huzel "usually 5-12"
Z_MAX_BLADES = 48          # Fig. 16 upper sheet
Z_INLET_MAX = 8            # 4-8 inlet blades, splitters beyond [SP-8109 §3.3.1.3]
PHI2_MIN, PHI2_MAX = 0.05, 0.30        # [SP-8109 §2.3.1.2 p.28]
INCIDENCE_DEG = 3.0        # blade inlet angle above the flow angle (reporting/drawing)
DT2_OVER_B2_MACHINED = 20.0            # [SP-8109 §3.3.3]
MACHINABLE_Z_PER_SIN_B2 = 28.0         # Z2 <= 28 sin beta2 [SP-8109 §3.3.3]

# --- centrifugal: losses -------------------------------------------------------
WALL_ROUGHNESS_M = 63e-6 * _IN          # 63 uin rms finish [SP-8109 §2.4.4, §3.4.1.1]
W_RATIO_LIMIT = 0.70       # de Haller-type limit - NOT in SP-8109 (which gives only G <= 3.5);
K_DIFFUSION = 0.5          #   Tier 3 textbook practice
ZETA_DIFFUSER = {"volute": 0.30,       # fraction of c2^2/2g NOT recovered: Huzel "70-90 % of
                 "vaned": 0.20,        # the flow KE converted" [p.220]; vaned better [SP-8109
                 "crossover": 0.35}    # p.20, +3 % at Ns 1200]; interstage crossover worst (Tier 2)
SEAL_C_OVER_D2 = 0.0005    # wear-ring clearance [SP-8109 §2.3.1.4 p.34]
SEAL_C_MIN_M = 0.006 * _IN  # Tier 3 floor: 0.0005 D2 is unbuildable on a small impeller; fitted
                           # so the size effect follows SP-8109 Fig. 6 (small pumps leak more)
SEAL_K = 0.5               # leak coefficient, middle of Fig. 22's 0.25-0.7 [SP-8109 p.36]
SEAL_HEAD_FRACTION = 0.75  # wear-ring dP ~ 0.75 x stage head [Huzel eq. 6-76]
DISK_CM_COEFF = 0.0622     # C_M = 0.0622 Re^-0.2 (both faces), Daily-Nece-type turbulent
                           # enclosed disk - Tier 3, no coefficient in the reference set
MECH_LOSS_AT_1IN = 0.15    # seal+bearing power: "may be as high as 20 %" at 1 in (an upper
                           # bound; 15 % nominal), negligible at >= 10 in
MECH_LOSS_EXPONENT = 1.3   #   [SP-8109 §2.2 p.8] -> 1 % at 10 in (Tier 2)
# SP-8109 Fig. 9 efficiency penalty (points) vs design Ss (water), per stage Ns:
# (Ns, points at Ss 10,000, points per decade of Ss) - read from Fig. 9 (straight in log Ss)
SS_PENALTY_TABLE = ((500.0, 0.05, 1.6), (1000.0, 0.2, 3.1), (2000.0, 0.4, 6.0),
                    (3000.0, 1.0, 8.5), (4000.0, 1.3, 11.2))
K_HYD = 1.76               # calibrated hydraulic-loss multiplier: least squares on
                           # CENTRIFUGAL_ANCHORS (rms 0.031, Round 2 fit) - Tier 2

# --- centrifugal: volute / diffuser geometry (drawing + checks) ----------------
TONGUE_RADIUS_RATIO = 1.05             # tongue 5-10 % beyond r2 [Huzel p.220]; >1.05 r4 [SP-8109]
KV_AT_NS = ((500.0, 0.50), (3000.0, 0.20))   # c3 = Kv sqrt(2 g H), Kv 0.15-0.55, lower at high
                                             # Ns [Huzel eq. 6-70] (A-1 LOX Ns 1980 -> 0.337)
VANELESS_GAP = ((0.0, 0.0), (5.0, 0.035), (10.0, 0.07), (15.0, 0.115), (20.0, 0.195),
                (23.5, 0.25))          # (D3-D2)/D2 vs alpha2 [SP-8109 Fig. 24]
DIFFUSER_R4_OVER_R3 = 1.30             # <= 1.4 per vane ring [SP-8109 §3.4.1.2.2]

# --- H-Q sketch ---------------------------------------------------------------
K_SHOCK = 0.29             # off-design (1-x)^2 loss as a fraction of the design slipped
                           # Euler head: J-2 LOX-class backswept impeller -> shutoff psi/psi_d
                           # ~1.2, radial 24-blade -> droop ~0.87 [SP-8109 Fig. 13] (Tier 2)
HQ_POINTS = 29

# --- axial --------------------------------------------------------------------
AX_BLOCKAGE = 0.10         # Mark 9/15-F/25/26 ~10 % [SP-8125 p.25]
AX_SIGMA_ROTOR = 1.1       # mean-radius solidity: rotor 1-1.3, stator 1.5-1.8 [Huzel p.230]
AX_SIGMA_STATOR = 1.6
AX_HUB_TIP = 0.83          # 0.76-0.86 rocket H2 [Huzel p.230]; J-2 0.829, M-1 0.85
AX_PSI_T = 0.25            # stage tip head coefficient, J-2 0.226, M-1 0.258 [SP-8125 Table II]
AX_H_PER_STAGE_FT = 6000.0 # 5,000-9,000 ft per axial stage [Huzel p.225]
AX_NS_TARGET_US = 4450.0   # axial stage Ns: Mark 9/15-F 4,450, M-1 4,470 [SP-8125 Table II]
                           # (fleet 3,200-4,800); scaled with the intent's Ns factor
AX_LEAK_FRACTION = 0.06    # impeller + balance leakage [Huzel eq. 6-87, SC 6-10]
AX_INDUCER_HEAD_FRACTION = 0.12  # inducer 5-20 % of head [Huzel p.210]
AX_INDUCER_ETA = 0.70
AX_ASPECT = 0.6            # blade height / chord (J-2 0.45, M-1 1.0, A-2 0.37) - Tier 3
AX_DF_DESIGN_MAX = 0.55    # 0.45-0.55 design; stall 0.75 [SP-8125 §3.2.2.1, §3.2.2.6]
AX_DF_STALL = 0.75
# [SP-8125 Fig. 8] profile-loss parameter omega*cos(beta_exit)/(2 sigma) vs DF (30-90 % span)
AX_PROFILE_LOSS = ((0.0, 0.004), (0.1, 0.006), (0.2, 0.008), (0.3, 0.0095), (0.4, 0.012),
                   (0.5, 0.018), (0.6, 0.027), (0.7, 0.040), (0.8, 0.056))
K_AX = 2.49                # calibrated end-wall/secondary/tip multiplier on the Fig. 8 profile loss:
                           # least squares on AXIAL_ANCHORS (rms 0.025) - Tier 2

# --- real anchors -------------------------------------------------------------
# (name, fluid, rho kg/m3, gpm, head ft (None = from psi_d & D2), rpm, stages, D2 in,
#  beta2, z, psi_d, eta_real, kinematic visc m2/s)
CENTRIFUGAL_ANCHORS = (
    # [SP-8107 Table II] flow/head/rpm/eta; [SP-8109 Table I] D2/beta2/z
    ("F-1 LOX",   "LOX",  1141.0, 25_200.0, 3097.0, 5488.0, 1, 19.5, 25.0, 6, None, 0.746, 1.7e-7),
    ("F-1 RP-1",  "RP-1",  809.0, 15_250.0, 5168.0, 5488.0, 1, 23.4, 25.0, 6, None, 0.726, 2.5e-6),
    # J-2 / H-1 heads from the design psi of [SP-8109 Fig. 13] and Dt2 [Table I / Fig. 6]
    ("J-2 LOX",   "LOX",  1134.0,  2_920.0, None, 8753.0, 1, 10.2, 25.0, 6, 0.448, 0.800, 1.7e-7),
    ("H-1 LOX",   "LOX",  1134.0,  3_410.0, None, 6680.0, 1, 11.0, 35.0, 10, 0.56, 0.778, 1.7e-7),
    ("H-1 RP-1",  "RP-1",  809.0,  2_130.0, None, 6680.0, 1, 13.3, 25.0, 10, 0.613, 0.718, 2.5e-6),
    # SSME Block IIA NPL [SSME-Orientation p.59, p.67]; D2/blades not published here -> tool psi
    ("SSME HPOTP main", "LOX", 1142.0, 7_063.0, 7402.0, 22_220.0, 1, None, None, None, None, 0.718, 1.7e-7),
    ("SSME HPFTP (3st)", "LH2", 73.7, 15_800.0, 178_400.0, 34_360.0, 3, None, None, None, None, 0.750, 2.0e-7),
)
CENTRIFUGAL_OUTLIERS = ()
# Real outlet width / tip diameter [SP-8109 Table I] - a PREDICTION check (not fitted)
TABLE_I_B2_OVER_D2 = {"F-1 LOX": 2.7 / 19.5, "F-1 RP-1": 1.7 / 23.4, "J-2 LOX": 0.74 / 10.2,
                      "H-1 RP-1": 0.85 / 14.25}
AXIAL_ANCHORS = (
    # name, rho, gpm, head ft, rpm, main stages, eta (whole pump)
    ("J-2 Mark 15-F LH2", 70.8, 9_062.0, 40_300.0, 28_266.0, 7, 0.73),  # [SP-8125 Table I; SP-8107 II]
    ("M-1 LH2",           70.8, 62_300.0, 56_500.0, 13_225.0, 8, 0.70),  # [SP-8125 Table I, Fig. 1]
)
ANCHOR_TOLERANCE = 0.08


@dataclass(frozen=True)
class HydraulicsSpec:
    """What turbopump_sizing.size_pump needs for one leg's meanline (built by
    design/suction_stage.pump_hydraulics from turbopump_intent.PumpIntent)."""
    ns_target_us: float
    psi: float
    beta2_deg: float
    tip_speed_fraction: float
    diffuser: str = "auto"
    pump_type: str = "centrifugal"
    nu_kin: float = 2.0e-7
    leg: str = ""
    neutral: bool = True     # every intent slider at 0 (size_turbopump's mass ratio = 1)


def _interp(table, x):
    xs = [p[0] for p in table]
    if x <= xs[0]:
        return table[0][1]
    if x >= xs[-1]:
        return table[-1][1]
    for (x0, y0), (x1, y1) in zip(table, table[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return table[-1][1]


def slip_coefficient(phi2, beta2_deg, z, delta=DELTA_DEFAULT, x_l=X_L):
    """SP-8109 eq. 17: M = c_u2(infinite blades)/c_u2 >= 1."""
    b = math.radians(beta2_deg)
    num = (1.37 + 0.23 * math.sin(b)) * max(phi2 + 0.05, 1e-6) ** 0.6
    den = 0.5 * z * x_l ** 0.6 * (1.0 + x_l / 2.0) * (1.0 - 0.12 * delta)
    return 1.0 + num / den


def psi_theoretical(phi2, beta2_deg, z, delta=DELTA_DEFAULT):
    """Slipped Euler head coefficient (1 - phi2 cot beta2)/M, zero prewhirl."""
    cot = 1.0 / math.tan(math.radians(beta2_deg)) if beta2_deg < 89.999 else 0.0
    return (1.0 - phi2 * cot) / slip_coefficient(phi2, beta2_deg, z, delta)


def solve_phi2(psi_th, beta2_deg, z, delta=DELTA_DEFAULT):
    """Outlet flow coefficient giving the slipped Euler head psi_th; None if
    unreachable (too few blades for that head)."""
    cot = 1.0 / math.tan(math.radians(beta2_deg)) if beta2_deg < 89.999 else 0.0
    lo, hi = 0.0, (0.95 / cot if cot > 0 else 0.6)
    f = lambda p: psi_theoretical(p, beta2_deg, z, delta) - psi_th
    if f(lo) < 0:
        return None
    f_lo, f_hi = f(lo), f(hi)
    if f_hi > 0:
        return hi
    side = 0
    for _ in range(60):                       # Illinois regula falsi (f decreasing in phi)
        mid = (lo * f_hi - hi * f_lo) / (f_hi - f_lo)
        fm = f(mid)
        if abs(fm) < 1e-12 or hi - lo < 1e-12:
            return mid
        if fm > 0:
            lo, f_lo = mid, fm
            if side == 1:
                f_hi *= 0.5
            side = 1
        else:
            hi, f_hi = mid, fm
            if side == -1:
                f_lo *= 0.5
            side = -1
    return mid


def fleet_delta(ns_stage_us, ss_design=0.0):
    """Impeller eye/tip diameter ratio Dt1/Dt2 from the SP-8109 Fig. 5 fleet
    (Ns, delta): F-1 LOX 2110/0.78, J-2 LOX 1570/0.69, Atlas booster LOX
    1190/0.58, H-1-class RP-1 750/0.45, X-8 620/0.48 -> 0.69 (Ns/1570)^0.45
    (Tier 2 fit, fleet Ss ~SS_FLEET_REF), scaled by (Ss/SS_FLEET_REF)^0.32 for
    the design Ss [SP-8109 Fig. 8: Ns 1500, Ss 10,000 -> 0.45, 40,000 -> 0.70],
    clamped to the fleet's 0.40-0.80."""
    if ns_stage_us <= 0:
        return DELTA_DEFAULT
    d = DELTA_FLEET_AT_1570 * (ns_stage_us / 1570.0) ** DELTA_FLEET_EXP
    if ss_design > 0:
        d *= (max(ss_design, 10_000.0) / SS_FLEET_REF) ** DELTA_SS_EXP
    return max(DELTA_MIN, min(DELTA_MAX, d))


def ss_penalty_points(ns_stage_us, ss_design):
    """[SP-8109 Fig. 9] efficiency loss (percentage points) of a stage designed
    for water Ss `ss_design` at stage Ns (0 below Ss 10,000)."""
    if ss_design <= 10_000.0 or ns_stage_us <= 0:
        return 0.0
    a = _interp([(n, a0) for n, a0, _ in SS_PENALTY_TABLE], ns_stage_us)
    b = _interp([(n, b0) for n, _, b0 in SS_PENALTY_TABLE], ns_stage_us)
    return a + b * math.log10(ss_design / 10_000.0)


def _haaland_f(re, dh):
    if re <= 0 or dh <= 0:
        return 0.02
    if re < 2300.0:
        return 64.0 / re
    t = (WALL_ROUGHNESS_M / dh / 3.7) ** 1.11 + 6.9 / re
    return (-1.8 * math.log10(t)) ** -2


def _mech_eta(d2_m):
    return max(0.5, 1.0 - MECH_LOSS_AT_1IN * (_IN / max(d2_m, 1e-4)) ** MECH_LOSS_EXPONENT)


def _ns_us(n_rpm, q_m3s, h_m):
    if h_m <= 0 or q_m3s <= 0:
        return 0.0
    return n_rpm * math.sqrt(q_m3s / _GPM_TO_M3S) / (h_m / _FT) ** 0.75


def _prime_near(n, avoid):
    """Diffuser vane count: the prime nearest n with no common factor with the
    impeller blade count [SP-8109 §3.4.1.2.2]."""
    def is_prime(k):
        return k > 1 and all(k % d for d in range(2, int(k ** 0.5) + 1))
    for off in range(0, 40):
        for c in (n + off, n - off):
            if c >= 5 and is_prime(c) and math.gcd(c, avoid) == 1:
                return c
    return max(5, n)


def blade_camber(r1, r2, beta1_deg, beta2_deg, n=24):
    """Blade camber line (r, theta) from inlet to outlet, beta linear in r
    (measured from tangential): d theta = dr / (r tan beta)."""
    pts = [(r1, 0.0)]
    th = 0.0
    for i in range(1, n + 1):
        ra = r1 + (r2 - r1) * (i - 1) / n
        rb = r1 + (r2 - r1) * i / n
        rm = 0.5 * (ra + rb)
        bm = math.radians(beta1_deg + (beta2_deg - beta1_deg) * (rm - r1) / (r2 - r1))
        th += (rb - ra) / (rm * math.tan(max(bm, math.radians(1.0))))
        pts.append((rb, th))
    return pts


def centrifugal_stage(q_m3s, h_stage_m, n_rpm, u2_m_s, beta2_deg, rho, nu_kin, *,
                      z=None, delta=None, diffuser="volute", ss_design=0.0,
                      d_eye_m=0.0, k_hyd=None):
    """One centrifugal stage at its design point. Returns a dict of velocity
    triangles, geometry, loss breakdown and efficiencies (build quality NOT
    applied)."""
    k_hyd = K_HYD if k_hyd is None else k_hyd
    warnings = []
    omega = 2.0 * math.pi * n_rpm / 60.0
    d2 = 2.0 * u2_m_s / omega
    r2 = 0.5 * d2
    psi = G * h_stage_m / (u2_m_s * u2_m_s)
    if delta is None:
        # impeller eye from the fleet trend [SP-8109 Fig. 5; §3.3.1.1: delta "shall maximize
        # efficiency consistent with the required suction performance"]; a larger inducer
        # tapers down to it (Huzel SC 6-7) - d_eye_m is the inducer tip, drawn separately
        delta = fleet_delta(_ns_us(n_rpm, q_m3s, h_stage_m), ss_design)
    d1 = delta * d2
    d_hub = INLET_HUB_RATIO * d1
    r1m = 0.5 * d1 * math.sqrt((1.0 + INLET_HUB_RATIO ** 2) / 2.0)
    u1 = omega * r1m
    ns_stage = _ns_us(n_rpm, q_m3s, h_stage_m)
    # blade count: Huzel z = beta2/3, adjusted into SP-8109's phi2 band
    z_auto = z is None
    z_base = max(Z_MIN_BLADES, int(round(beta2_deg * Z_PER_DEG))) if z_auto else z
    z_cap = min(Z_MAX_BLADES, max(Z_CAP_MIN, int(MACHINABLE_Z_PER_SIN_B2 * math.sin(math.radians(beta2_deg)))))
    seal_c = max(SEAL_C_OVER_D2 * d2, SEAL_C_MIN_M)
    q_leak = SEAL_K * math.pi * 1.05 * d1 * seal_c * math.sqrt(2.0 * G * SEAL_HEAD_FRACTION * h_stage_m)
    q_imp = q_m3s + q_leak
    a1 = 0.25 * math.pi * d1 * d1 * (1.0 - INLET_HUB_RATIO ** 2) * EPS1
    cm1 = q_imp / a1
    def _select_z(psi_th):
        # Huzel's z = beta2/3, then more blades (less slip -> larger phi2 at this psi)
        # until c_m2 >= c_m1 [SP-8109 §3.3.1.2: 1-1.5 x], up to the machinable count
        zz = z_base
        ph = solve_phi2(psi_th, beta2_deg, zz, delta)
        while zz < z_cap and (ph is None or ph < PHI2_MIN or ph * u2_m_s < CM2_OVER_CM1_MIN * cm1):
            zz += 1
            ph = solve_phi2(psi_th, beta2_deg, zz, delta)
        while (ph is None or ph < PHI2_MIN) and zz < Z_MAX_BLADES:
            zz += 1
            ph = solve_phi2(psi_th, beta2_deg, zz, delta)
        while ph is not None and ph > PHI2_MAX and zz > 3:
            zz -= 1
            ph = solve_phi2(psi_th, beta2_deg, zz, delta)
        return zz

    eta_h = 0.85
    res = None
    unreachable = False
    if z_auto:
        z = _select_z(psi / eta_h)
    reselected = not z_auto
    hist = [eta_h]
    for _ in range(80):
        psi_th = psi / eta_h
        phi2 = solve_phi2(psi_th, beta2_deg, z, delta)
        unreachable = phi2 is None
        if unreachable:
            phi2 = PHI2_MIN
        m_slip = slip_coefficient(phi2, beta2_deg, z, delta)
        cm2 = phi2 * u2_m_s
        cu2 = psi_th * u2_m_s
        cu2_inf = cu2 * m_slip
        w2 = math.hypot(cm2, u2_m_s - cu2)
        c2 = math.hypot(cm2, cu2)
        w1 = math.hypot(cm1, u1)
        beta1 = math.degrees(math.atan2(cm1, u1))
        b2 = q_imp / (math.pi * d2 * cm2 * EPS2) if cm2 > 0 else 0.0
        # channel friction along the mean blade passage
        bm = math.radians(0.5 * (beta1 + beta2_deg))
        length = (r2 - r1m) / max(math.sin(bm), 0.05)
        pitch = 2.0 * math.pi * 0.5 * (r1m + r2) * math.sin(bm) / z
        b_eye = 0.5 * (d1 - d_hub)
        b_m = 0.5 * (b_eye + b2)
        dh = 2.0 * pitch * b_m / (pitch + b_m) if pitch + b_m > 0 else 1e-3
        w_m = 0.5 * (w1 + w2)
        f = _haaland_f(w_m * dh / nu_kin, dh)
        h_fric = f * length / dh * w_m * w_m / (2.0 * G)
        h_diff = K_DIFFUSION * max(0.0, W_RATIO_LIMIT - w2 / w1) * w1 * w1 / (2.0 * G)
        h_vol = ZETA_DIFFUSER.get(diffuser, ZETA_DIFFUSER["volute"]) * c2 * c2 / (2.0 * G)
        losses = k_hyd * (h_fric + h_diff + h_vol)
        eta_h_new = h_stage_m / (h_stage_m + losses)
        converged = abs(eta_h_new - eta_h) < 1e-9
        # Aitken delta^2 acceleration of the (linearly converging) fixed point
        hist.append(eta_h_new)
        if not converged and len(hist) >= 3:
            x0, x1, x2 = hist[-3:]
            den = x2 - 2.0 * x1 + x0
            if abs(den) > 1e-15:
                acc = x2 - (x2 - x1) ** 2 / den
                if 0.3 < acc < 1.0:
                    eta_h_new = acc
                    hist.clear()
        eta_h = eta_h_new
        res = dict(phi2=phi2, m_slip=m_slip, cm2=cm2, cu2=cu2, cu2_inf=cu2_inf, w2=w2, c2=c2,
                   cm1=cm1, w1=w1, beta1=beta1, b2=b2, h_fric=h_fric, h_diff=h_diff,
                   h_vol=h_vol)
        if converged:
            if not reselected:
                reselected = True
                z_new = _select_z(psi / eta_h)
                if z_new != z:
                    z = z_new
                    hist = [eta_h]
                    continue
            break
    if unreachable:
        warnings.append(f"head coefficient {psi:.2f} unreachable at beta2 {beta2_deg:.0f} deg "
                        f"with {z} blades [SP-8109 Fig. 16]")
    h_th = h_stage_m / eta_h
    p_useful = rho * G * q_m3s * h_stage_m
    p_th = rho * G * q_imp * h_th
    re_d = omega * r2 * r2 / nu_kin
    p_df = DISK_CM_COEFF * re_d ** -0.2 * rho * omega ** 3 * r2 ** 5
    eta_m = _mech_eta(d2)
    p_shaft = (p_th + p_df) / eta_m
    eta = p_useful / p_shaft
    pen = ss_penalty_points(ns_stage, ss_design) / 100.0
    eta_after_ss = max(0.2, eta - pen)
    p_shaft_final = p_useful / eta_after_ss
    # Checks (warn-only)
    if b2 > 0 and d2 / b2 > DT2_OVER_B2_MACHINED:
        warnings.append(f"impeller outlet only {b2 * 1000:.1f} mm wide (D2/b2 {d2 / b2:.0f} > 20): "
                        f"too thin for a machined shrouded impeller [SP-8109 §3.3.3]")
    if z > MACHINABLE_Z_PER_SIN_B2 * math.sin(math.radians(beta2_deg)) + 1e-9:
        warnings.append(f"{z} blades exceeds the ~{MACHINABLE_Z_PER_SIN_B2 * math.sin(math.radians(beta2_deg)):.0f}"
                        f" machinable at beta2 {beta2_deg:.0f} deg (cast or open-face) [SP-8109 §3.3.3]")
    cm_ratio = cm2 / cm1 if cm1 > 0 else 0.0
    loss_power = {
        "useful": p_useful,
        "hydraulic": rho * G * q_imp * (h_th - h_stage_m),
        "friction": rho * G * q_imp * k_hyd * res["h_fric"],
        "diffusion": rho * G * q_imp * k_hyd * res["h_diff"],
        "diffuser": rho * G * q_imp * k_hyd * res["h_vol"],
        "leakage": rho * G * q_leak * h_stage_m,
        "disk_friction": p_df,
        "mechanical": (p_th + p_df) * (1.0 / eta_m - 1.0),
        "suction_ss": p_shaft_final - p_shaft,
    }
    return {
        "type": "centrifugal", "q_m3s": q_m3s, "q_imp_m3s": q_imp, "q_leak_m3s": q_leak,
        "h_stage_m": h_stage_m, "h_th_m": h_th, "n_rpm": n_rpm, "ns_stage_us": ns_stage,
        "psi": psi, "psi_th": psi / eta_h, "psi_inf": psi / eta_h * res["m_slip"],
        "phi2": res["phi2"], "slip_m": res["m_slip"], "z": z,
        "z_inlet": z if z <= Z_INLET_MAX else (z // 2 if z % 2 == 0 else max(4, z // 3)),
        "splitters": z > Z_INLET_MAX, "beta1_flow_deg": res["beta1"],
        "beta1_blade_deg": res["beta1"] + INCIDENCE_DEG, "beta2_deg": beta2_deg,
        "delta": delta, "d1_m": d1, "d_hub_m": d_hub, "d2_m": d2, "b2_m": res["b2"],
        "u1_m_s": u1, "u2_m_s": u2_m_s, "cm1_m_s": res["cm1"], "w1_m_s": res["w1"],
        "cm2_m_s": res["cm2"], "cu2_m_s": res["cu2"], "cu2_inf_m_s": res["cu2_inf"],
        "w2_m_s": res["w2"], "c2_m_s": res["c2"],
        "alpha2_deg": math.degrees(math.atan2(res["cm2"], res["cu2"])),
        "w2_over_w1": res["w2"] / res["w1"], "cm2_over_cm1": cm_ratio,
        "eta_h": eta_h, "eta_v": q_m3s / q_imp, "eta_m": eta_m,
        "disk_friction_fraction": p_df / p_shaft, "ss_penalty_pts": pen * 100.0,
        "eta": eta_after_ss, "p_shaft_w": p_shaft_final, "p_useful_w": p_useful,
        "loss_power_w": loss_power, "diffuser": diffuser, "seal_clearance_m": seal_c,
        "warnings": warnings,
    }


def _volute_geometry(stage, h_stage_m, ns_stage):
    """Volute spiral (constant mean velocity, Huzel eq. 6-69/6-70) and, for a
    vaned diffuser, its ring (SP-8109 Fig. 24 gap, R4/R3 1.3, prime vane count)."""
    r2 = 0.5 * stage["d2_m"]
    kv = _interp(KV_AT_NS, ns_stage)
    c3 = kv * math.sqrt(2.0 * G * h_stage_m)
    a_throat = stage["q_imp_m3s"] / c3 if c3 > 0 else 0.0
    diff = None
    r_tongue = TONGUE_RADIUS_RATIO * r2
    if stage["diffuser"] == "vaned":
        gap = _interp(VANELESS_GAP, stage["alpha2_deg"])
        r3 = r2 * (1.0 + max(gap, 0.035))
        r4 = DIFFUSER_R4_OVER_R3 * r3
        zd = _prime_near(stage["z"] + 2, stage["z"])
        diff = {"r3_m": r3, "r4_m": r4, "zd": zd}
        r_tongue = TONGUE_RADIUS_RATIO * r4
    spiral = []
    for i in range(0, 37):
        th = 10.0 * i
        a = a_throat * th / 360.0
        rs = math.sqrt(a / math.pi) if a > 0 else 0.0
        spiral.append((th, r_tongue + 2.0 * rs))
    return {"kv": kv, "c3_m_s": c3, "throat_area_m2": a_throat, "r_tongue_m": r_tongue,
            "tongue_angle_deg": stage["alpha2_deg"], "spiral": spiral, "diffuser": diff,
            "od_m": 2.0 * max(r for _, r in spiral)}


def hq_curve(stage, k_shock=K_SHOCK, n=HQ_POINTS):
    """Approximate head/flow and efficiency curves (normalised to the design
    point) from the meanline: slipped Euler line, design losses ~ x^2, an
    off-design shock term (1-x)^2. A SKETCH - real maps are Round 5."""
    cot = 1.0 / math.tan(math.radians(stage["beta2_deg"])) if stage["beta2_deg"] < 89.999 else 0.0
    m = stage["slip_m"]
    phi = stage["phi2"]
    psi_d = stage["psi"]
    psi_e1 = (1.0 - phi * cot) / m
    l_d = psi_e1 - psi_d
    q_ratio = stage["q_imp_m3s"] / stage["q_m3s"]
    b_df = stage["disk_friction_fraction"] * stage["p_shaft_w"] / max(stage["p_useful_w"], 1e-9) * psi_d
    xs, psis, etas = [], [], []
    for i in range(n):
        x = 0.05 + 1.4 * i / (n - 1)
        psi_e = (1.0 - x * phi * cot) / m
        psi_x = psi_e - l_d * x * x - k_shock * psi_e1 * (1.0 - x) ** 2
        power = x * psi_e * q_ratio + b_df
        eta_x = max(0.0, x * psi_x / power * stage["eta_m"]) if power > 0 else 0.0
        xs.append(x)
        psis.append(psi_x / psi_d)
        etas.append(eta_x)
    eta1 = stage["eta"] + stage["ss_penalty_pts"] / 100.0
    scale = eta1 / max(etas[min(range(n), key=lambda i: abs(xs[i] - 1.0))], 1e-9)
    etas = [e * scale for e in etas]
    # zero-slope point (the flow below which head stops rising)
    x_zero = 0.0
    for i in range(1, n):
        if psis[i] > psis[i - 1]:
            x_zero = xs[i]
    shutoff = psis[0]
    return {"x": xs, "psi_ratio": psis, "eta": etas, "x_zero_slope": x_zero,
            "shutoff_ratio": shutoff, "rising_to_shutoff": x_zero <= xs[0] + 1e-9}


def meridional_outline(stage, n=16):
    """Hub and shroud (z, r) curves of one impeller: quarter-ellipses from the
    eye to the tip, axial length X_L * D2 to the outlet shroud face."""
    r1t, rh, r2, b2 = 0.5 * stage["d1_m"], 0.5 * stage["d_hub_m"], 0.5 * stage["d2_m"], stage["b2_m"]
    lz = X_L * stage["d2_m"]
    shroud, hub = [], []
    for i in range(n + 1):
        t = 0.5 * math.pi * i / n
        shroud.append((lz * math.sin(t), r2 - (r2 - r1t) * math.cos(t)))
        hub.append(((lz + b2) * math.sin(t), r2 - (r2 - rh) * math.cos(t)))
    return {"shroud": shroud, "hub": hub, "axial_length_m": lz + b2}


def _exact_cache(fn):
    """Memoize on the EXACT arguments (the staged-combustion solvers re-size the
    same pumps many times per compute - Raptor: 2,270 calls, 183 distinct). A
    shallow copy is returned: the nested stage/geometry/curve data is SHARED and
    must be treated as read-only (nothing downstream mutates it; a deep copy cost
    more than the meanline itself)."""
    cached = functools.lru_cache(maxsize=512)(fn)

    @functools.wraps(fn)
    def wrapper(*args, **kw):
        return dict(cached(*args, **kw))
    wrapper.cache_clear = cached.cache_clear
    return wrapper


@_exact_cache
def design_centrifugal(q_m3s, h_total_m, n_rpm, u2_m_s, n_stages, rho, nu_kin, *,
                       beta2_deg=25.0, diffuser="auto", psi_for_diffuser=None,
                       ss_design=0.0, d_eye_m=0.0, z=None, build_quality=1.0, k_hyd=None,
                       vaned_psi_above=0.5, vaned_ns_below=1000.0):
    """Whole centrifugal pump: n identical stages (interstage crossovers, the last
    discharging to the volute or vaned diffuser + volute)."""
    n_stages = max(1, int(n_stages))
    h_st = h_total_m / n_stages
    psi = G * h_st / (u2_m_s * u2_m_s)
    ns_st = _ns_us(n_rpm, q_m3s, h_st)
    if diffuser not in ("volute", "vaned"):
        diffuser = "vaned" if (psi > vaned_psi_above or 0 < ns_st < vaned_ns_below) else "volute"
    # identical stages: only the first (inducer Ss penalty), a middle one and the last
    # (its own diffuser) differ - evaluate each kind once
    kinds = {}
    stages = []
    for i in range(n_stages):
        last = i == n_stages - 1
        key = (i == 0, last)
        if key not in kinds:
            kinds[key] = centrifugal_stage(
                q_m3s, h_st, n_rpm, u2_m_s, beta2_deg, rho, nu_kin, z=z,
                diffuser=diffuser if last else "crossover",
                ss_design=ss_design if i == 0 else 0.0, d_eye_m=d_eye_m, k_hyd=k_hyd)
        stages.append(kinds[key])
    p_use = sum(s["p_useful_w"] for s in stages)
    p_sh = sum(s["p_shaft_w"] for s in stages)
    eta = max(0.2, min(0.92, p_use / p_sh * build_quality)) if p_sh > 0 else 0.0
    s0, sl = stages[0], stages[-1]
    loss = {k: sum(s["loss_power_w"][k] for s in stages) for k in s0["loss_power_w"]}
    volute = _volute_geometry(sl, h_st, ns_st)
    warnings = []
    for s in stages:
        for w in s["warnings"]:
            if w not in warnings:
                warnings.append(w)
    hq = hq_curve(s0)
    return {
        "type": "centrifugal", "n_stages": n_stages, "eta": eta, "eta_raw": p_use / p_sh,
        "build_quality": build_quality, "diffuser": diffuser, "stage": s0, "last_stage": sl,
        "stages": stages, "loss_power_w": loss, "p_shaft_w": p_sh / build_quality,
        "p_useful_w": p_use, "volute": volute, "hq": hq, "meridional": meridional_outline(s0),
        "blade": blade_camber(0.5 * s0["d1_m"] * math.sqrt((1 + INLET_HUB_RATIO ** 2) / 2),
                              0.5 * s0["d2_m"], s0["beta1_blade_deg"], beta2_deg),
        "ns_stage_us": ns_st, "warnings": warnings,
    }


# --- axial -------------------------------------------------------------------
def _axial_triangles(phi, psi_i, sigma):
    """R = 0.5 pitchline triangles (velocities / U): returns w1, w2, DF, exit
    angle from axial (deg)."""
    w1 = math.hypot(phi, (1.0 + psi_i) / 2.0)
    w2 = math.hypot(phi, (1.0 - psi_i) / 2.0)
    df = 1.0 - w2 / w1 + psi_i / (2.0 * sigma * w1)
    beta_exit = math.degrees(math.atan2((1.0 - psi_i) / 2.0, phi))
    beta_in = math.degrees(math.atan2((1.0 + psi_i) / 2.0, phi))
    return w1, w2, df, beta_in, beta_exit


def axial_stage_eta(phi, psi_actual, k_ax=None):
    """Stage hydraulic efficiency of a symmetric (R 0.5) stage. The blade
    loading (diffusion factors, ideal head) comes from the Fig. 8 PROFILE loss
    alone - SP-8125's DF is an aerodynamic loading measure, and its Table II
    stage eta excludes tip/secondary loss; K_AX then scales the loss for the
    end-wall/secondary/tip losses in the returned efficiency only. Returns
    (eta_st, psi_i, rotor DF, stator DF, triangles)."""
    k_ax = K_AX if k_ax is None else k_ax
    eta_p = 0.9
    for _ in range(80):
        psi_i = psi_actual / eta_p
        w1, w2, df_r, b_in, b_ex = _axial_triangles(phi, psi_i, AX_SIGMA_ROTOR)
        _, _, df_s, _, _ = _axial_triangles(phi, psi_i, AX_SIGMA_STATOR)
        cosb = math.cos(math.radians(b_ex))
        om_r = _interp(AX_PROFILE_LOSS, df_r) * 2.0 * AX_SIGMA_ROTOR / cosb
        om_s = _interp(AX_PROFILE_LOSS, df_s) * 2.0 * AX_SIGMA_STATOR / cosb
        profile = (om_r + om_s) * w1 * w1 / 2.0            # in U^2 units (V2 = w1, symmetric)
        eta_new = psi_actual / (psi_actual + profile)
        converged = abs(eta_new - eta_p) < 1e-9
        eta_p = eta_new
        if converged:
            break
    eta = psi_actual / (psi_actual + k_ax * profile)
    return eta, psi_i, df_r, df_s, (w1, w2, b_in, b_ex)


@_exact_cache
def design_axial(q_m3s, h_total_m, n_rpm, n_stages, rho, nu_kin, *, psi_t=AX_PSI_T,
                 hub_tip=AX_HUB_TIP, build_quality=1.0, k_ax=None):
    """Multistage axial pump (inducer + n rotor/stator stages + volute)."""
    warnings = []
    n_stages = max(1, int(n_stages))
    h_ind = AX_INDUCER_HEAD_FRACTION * h_total_m
    h_st = (h_total_m - h_ind) / n_stages
    u_t = math.sqrt(G * h_st / psi_t)
    d_t = 60.0 * u_t / (math.pi * n_rpm)
    d_h = hub_tip * d_t
    d_m = math.sqrt((d_t * d_t + d_h * d_h) / 2.0)
    u_m = u_t * d_m / d_t
    q_imp = q_m3s * (1.0 + AX_LEAK_FRACTION)
    area = 0.25 * math.pi * (d_t * d_t - d_h * d_h) * (1.0 - AX_BLOCKAGE)
    v_a = q_imp / area
    phi = v_a / u_m
    psi_m = G * h_st / (u_m * u_m)
    eta_st, psi_i, df_r, df_s, (w1, w2, b_in, b_ex) = axial_stage_eta(phi, psi_m, k_ax)
    if max(df_r, df_s) > AX_DF_DESIGN_MAX:
        warnings.append(f"axial blade loading DF {max(df_r, df_s):.2f} above the 0.45-0.55 design "
                        f"range (stall at 0.75) [SP-8125 §3.2.2.1]")
    if phi < 0.25:
        warnings.append(f"axial stage flow coefficient {phi:.2f} below SP-8125's 0.25 guide")
    blade_h = 0.5 * (d_t - d_h)
    if blade_h < 0.5 * _IN:
        warnings.append(f"axial blade height {blade_h * 1000:.1f} mm below Huzel's ~0.5 in practical "
                        f"minimum (tip clearance dominates) [Huzel p.225]")
    chord = blade_h / AX_ASPECT
    z_r = max(8, int(round(AX_SIGMA_ROTOR * math.pi * d_m / chord)))
    z_s = _prime_near(int(round(AX_SIGMA_STATOR * math.pi * d_m / chord)), z_r)
    # whole pump: stage hydraulics x leakage x inducer x volute x mechanical
    p_use = rho * G * q_m3s * h_total_m
    p_main = rho * G * q_imp * (n_stages * h_st) / eta_st
    p_ind = rho * G * q_imp * h_ind / AX_INDUCER_ETA
    v_exit = v_a / math.cos(math.radians(b_ex))
    p_vol = rho * q_imp * ZETA_DIFFUSER["volute"] * 0.5 * v_exit ** 2
    eta_m = _mech_eta(d_t)
    p_sh = (p_main + p_ind + p_vol) / eta_m
    eta = max(0.2, min(0.92, p_use / p_sh * build_quality))
    loss = {"useful": p_use,
            "hydraulic": p_main - rho * G * q_imp * n_stages * h_st,
            "inducer": p_ind - rho * G * q_imp * h_ind,
            "diffuser": p_vol, "leakage": rho * G * (q_imp - q_m3s) * h_total_m,
            "mechanical": (p_main + p_ind + p_vol) * (1.0 / eta_m - 1.0),
            "disk_friction": 0.0, "suction_ss": 0.0, "friction": 0.0, "diffusion": 0.0}
    # H-Q sketch: ideal psi_i(x) = 1 - x (1 - psi_i_d) at fixed blade angles; stall at DF 0.75
    xs, psis, etas = [], [], []
    x_stall = 0.0
    for i in range(HQ_POINTS):
        x = 0.3 + 1.1 * i / (HQ_POINTS - 1)
        psi_ix = 1.0 - x * (1.0 - psi_i)
        v1u = x * (1.0 - psi_i) / 2.0
        w1x = math.hypot(x * phi, 1.0 - v1u)
        w2x = math.hypot(x * phi, x * (1.0 - psi_i) / 2.0)
        df_x = 1.0 - w2x / w1x + psi_ix / (2.0 * AX_SIGMA_ROTOR * w1x)
        if df_x >= AX_DF_STALL and x > x_stall:
            x_stall = x
        loss_x = (K_AX if k_ax is None else k_ax) * 2.0 * _interp(AX_PROFILE_LOSS, df_x) * \
            (AX_SIGMA_ROTOR + AX_SIGMA_STATOR) * w1x * w1x / 2.0 + K_SHOCK * psi_i * (1.0 - x) ** 2
        psi_x = psi_ix - loss_x
        xs.append(x)
        psis.append(psi_x / psi_m)
        etas.append(max(0.0, eta * (psi_x / max(psi_ix, 1e-9)) / (psi_m / psi_i)))
    return {
        "type": "axial", "n_stages": n_stages, "eta": eta, "eta_raw": p_use / p_sh,
        "eta_stage": eta_st, "eta_v": q_m3s / q_imp, "eta_m": eta_m, "build_quality": build_quality,
        "d_tip_m": d_t, "d_hub_m": d_h, "d_mean_m": d_m, "blade_height_m": blade_h,
        "u_tip_m_s": u_t, "u_mean_m_s": u_m, "v_axial_m_s": v_a, "phi": phi, "psi_mean": psi_m,
        "psi_tip": psi_t, "psi_i": psi_i, "df_rotor": df_r, "df_stator": df_s,
        "beta_in_deg": b_in, "beta_exit_deg": b_ex, "w1_m_s": w1 * u_m, "w2_m_s": w2 * u_m,
        "chord_m": chord, "z_rotor": z_r, "z_stator": z_s, "hub_tip": hub_tip,
        "h_stage_m": h_st, "h_inducer_m": h_ind, "ns_stage_us": _ns_us(n_rpm, q_m3s, h_st),
        "loss_power_w": loss, "p_shaft_w": p_sh, "p_useful_w": p_use,
        "hq": {"x": xs, "psi_ratio": psis, "eta": etas, "x_stall": x_stall,
               "x_zero_slope": 0.0, "shutoff_ratio": psis[0], "rising_to_shutoff": True},
        "warnings": warnings,
    }


def axial_stage_count(h_total_m, h_per_stage_ft=AX_H_PER_STAGE_FT):
    return max(1, math.ceil((1.0 - AX_INDUCER_HEAD_FRACTION) * h_total_m / (h_per_stage_ft * _FT)))


# --- anchors / calibration ----------------------------------------------------
def centrifugal_anchor_eta(row, k_hyd=None):
    name, fluid, rho, gpm, head_ft, rpm, stages, d2_in, beta2, z, psi_d, eta_real, nu = row
    q = gpm * _GPM_TO_M3S
    if head_ft is None:
        u2 = math.pi * d2_in * _IN * rpm / 60.0
        h = psi_d * u2 * u2 / G
    else:
        h = head_ft * _FT
    h_st = h / stages
    if d2_in:
        u2 = math.pi * d2_in * _IN * rpm / 60.0
    else:
        u2 = math.sqrt(G * h_st / 0.5)
    ss = 40_000.0      # all anchors are inducer pumps designed near the limit
    r = design_centrifugal(q, h, rpm, u2, stages, rho, nu, beta2_deg=beta2 or 25.0, z=z,
                           ss_design=ss, k_hyd=k_hyd)
    return r["eta"], r


def axial_anchor_eta(row, k_ax=None):
    name, rho, gpm, head_ft, rpm, stages, eta_real = row
    r = design_axial(gpm * _GPM_TO_M3S, head_ft * _FT, rpm, stages, rho, 2.0e-7, k_ax=k_ax)
    return r["eta"], r


def fit_report(k_hyd=None, k_ax=None):
    rows, ok = [], True
    for row in CENTRIFUGAL_ANCHORS:
        eta, _ = centrifugal_anchor_eta(row, k_hyd)
        d = eta - row[11]
        good = abs(d) <= ANCHOR_TOLERANCE or row[0] in CENTRIFUGAL_OUTLIERS
        ok &= good
        rows.append((row[0], eta, row[11], d, good))
    for row in AXIAL_ANCHORS:
        eta, _ = axial_anchor_eta(row, k_ax)
        d = eta - row[6]
        good = abs(d) <= ANCHOR_TOLERANCE
        ok &= good
        rows.append((row[0], eta, row[6], d, good))
    return rows, ok


if __name__ == "__main__":
    # 1. eq. 17 reproduces the SP-8109 Fig. 16 carpet (eta_h 0.82, delta 0.65)
    carpet = ((6, 25.0, 0.101, 0.477), (8, 20.0, 0.062, 0.567), (12, 30.0, 0.089, 0.605),
              (20, 35.0, 0.080, 0.673), (4, 30.0, 0.155, 0.371))
    for z, b2, phi, psi_real in carpet:
        psi = 0.82 * psi_theoretical(phi, b2, z)
        print(f"Fig. 16 Z{z:>2} b2 {b2:>4.0f}: phi2 {phi:.3f} psi eq17 {psi:.3f} vs {psi_real:.3f}")
        assert abs(psi - psi_real) < 0.03, (z, b2, psi, psi_real)
    # 2. Huzel SC 6-7 A-1 LOX impeller: psi 0.46, beta2 24, z 8 -> phi2 ~0.116
    phi = solve_phi2(0.46 / 0.82, 24.0, 8, delta=0.75)
    print(f"Huzel A-1 LOX: phi2 {phi:.3f} (worked example 0.116)")
    assert 0.09 < phi < 0.14
    # 3. anchors
    rows, ok = fit_report()
    print(f"{'anchor':<22} {'model':>6} {'real':>6} {'d':>7}")
    for name, eta, real, d, good in rows:
        print(f"{name:<22} {eta:6.3f} {real:6.3f} {d:+7.3f} {'ok' if good else 'FAIL'}")
    assert ok, "meanline anchor fit out of tolerance"
    # 4. directions: more blades -> steeper H-Q; radial droops, backswept rises to shutoff
    _, f1 = centrifugal_anchor_eta(CENTRIFUGAL_ANCHORS[0])
    s = f1["stage"]
    print(f"F-1 LOX meanline: z {s['z']} phi2 {s['phi2']:.3f} b2/D2 {s['b2_m'] / s['d2_m']:.3f} "
          f"eta_h {s['eta_h']:.3f} eta_v {s['eta_v']:.3f} eta_m {s['eta_m']:.3f} "
          f"disk {s['disk_friction_fraction']:.3f} shutoff {f1['hq']['shutoff_ratio']:.2f}")
    assert f1["hq"]["shutoff_ratio"] > 1.05
    # outlet width vs the real impellers [SP-8109 Table I] - not fitted, a prediction
    for name, real in TABLE_I_B2_OVER_D2.items():
        row = next(r for r in CENTRIFUGAL_ANCHORS if r[0] == name)
        st = centrifugal_anchor_eta(row)[1]["stage"]
        ratio = st["b2_m"] / st["d2_m"]
        print(f"  b2/D2 {name:<9} model {ratio:.3f} real {real:.3f}")
        assert abs(ratio / real - 1.0) < 0.15, (name, ratio, real)
    rad = design_centrifugal(0.5, 5000.0, 30000.0, math.sqrt(G * 5000.0 / 0.70), 1, 71.0, 2e-7,
                             beta2_deg=90.0, z=24)
    print(f"radial 24-blade LH2: shutoff {rad['hq']['shutoff_ratio']:.2f}")
    assert rad["hq"]["shutoff_ratio"] < f1["hq"]["shutoff_ratio"]
    # 5. size effect (SP-8109 Fig. 6 direction): same Ns, smaller pump -> lower eta
    big = design_centrifugal(0.30, 700.0, 9000.0, math.sqrt(G * 700.0 / 0.5), 1, 1141.0, 1.7e-7)
    small = design_centrifugal(0.003, 70.0, 9000.0 * 10 ** 0.5 * (0.1 ** 0.75) ** -1 / 10,
                               math.sqrt(G * 70.0 / 0.5), 1, 1141.0, 1.7e-7)
    print(f"size effect: big {big['eta']:.3f} (D2 {big['stage']['d2_m']:.3f} m) vs small "
          f"{small['eta']:.3f} (D2 {small['stage']['d2_m']:.3f} m)")
    assert small["eta"] < big["eta"]
    # 6. axial J-2
    _, j2 = axial_anchor_eta(AXIAL_ANCHORS[0])
    print(f"J-2 axial: d_t {j2['d_tip_m'] / _IN:.2f} in (real 7.22), hub/tip {j2['hub_tip']:.2f}, "
          f"phi {j2['phi']:.3f} DF {j2['df_rotor']:.2f} z_r {j2['z_rotor']} z_s {j2['z_stator']} "
          f"stall x {j2['hq']['x_stall']:.2f}")
    print("pump_meanline self-test OK")
