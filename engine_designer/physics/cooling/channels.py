"""Coolant-side channel/tube model: geometry, wall constructions, velocities, Dittus-Boelter h_c, Darcy friction.

Part of the physics/cooling/ package (split verbatim out of the former
single-file cooling.py - see cooling/__init__.py for the package overview)."""
import math

import numpy as np

from .coolant_props import (
    COOLANT_DENSITY_KG_M3,
    COOLANT_TRANSPORT,
    FUEL_CP_J_KGK,
    _COOLANT_DENSITY_FALLBACK,
    _COOLANT_TRANSPORT_FALLBACK,
)
from .profile import _local_area_ratio

# --- coolant-side channel model (regenerative jackets only) ------------------
# A 1-D counterflow coolant march: the fuel enters the jacket at the nozzle
# cooling-transition point and flows UP toward the injector, picking up the
# gas-side heat flux station by station. It gives (1) a coolant-side wall
# temperature via a series-resistance solve against the already-computed
# gas-side flux, and (2) a real jacket pressure drop (Darcy-Weisbach) that
# REPLACES the flat design.JACKET_DP_PA constant.
#
# Same honesty tier as BARTZ_SIGMA / materials.cooling_effectiveness: the
# relations (Dittus-Boelter, Darcy-Weisbach via Haaland, series resistance) are
# textbook; the channel-geometry defaults and the single CHANNEL_DP_CALIBRATION
# scalar are calibrated so the reference regen design (EngineDesign(
# cycle="gas_generator") defaults - LOX/RP-1, Pc 8 MPa, CR 1.6, narloy_z, auto
# channels) reproduces ~1.6 MPa jacket dP, the tool's long-standing flat value.
# That is a neutral-default contract: nothing already validated moves unless the
# user changes channel geometry or selects regen_channel_model="channels".
# Channel COUNT scales with engine size, not a fixed pitch: real regen jackets
# hold the channel count roughly constant (~150-400 - F-1 ~178, SSME ~390, RL10
# ~180) and grow the channel cross-section with the engine, so the throat
# coolant velocity - and hence the jacket dP - stays roughly scale-invariant.
CHANNEL_PITCH_FRACTION = 0.014         # throat channel pitch as a fraction of throat dia
                                       # -> n_channels ~ pi/0.014 ~ 224, near-constant
CHANNEL_PITCH_MIN_M = 1.2e-3           # floor for a tiny throat
CHANNEL_PITCH_MAX_M = 9.0e-3           # ceiling for a very large throat
CHANNEL_LAND_FRACTION_DEFAULT = 0.35   # fraction of the pitch taken by the rib (land) between channels
CHANNEL_ROUGHNESS_M = 6.0e-6          # milled / EDM channel wall
CHANNEL_MIN_COUNT = 40
# Target THROAT coolant velocity, per pair - the channel height is sized to hit
# this (aspect ratio is then an output, unless the user overrides it). Real
# regen practice: kerosene ~30-45 m/s, LH2 much faster, methane in between.
TARGET_COOLANT_VELOCITY_MS = {
    "LOX/RP-1": 35.0,
    "LOX/LH2": 95.0,
    "LOX/CH4": 45.0,
    "N2O4/MMH": 28.0,
}
_TARGET_COOLANT_VELOCITY_FALLBACK = 35.0
CHANNEL_ASPECT_RATIO_MAX = 8.0         # cap on the derived height/width
# Coolant-side Nusselt number (2026-09-23 audit, C1): Sieder-Tate turbulent
#   Nu = 0.027 Re^0.8 Pr^(1/3) (mu_bulk / mu_wall)^0.14
# [EUCASS-2023 Eq.11; Fagherazzi-2019 eq. 2.50] - the Dittus-Boelter family
# [Huzel eq. 4-12] PLUS the wall/bulk property-variation term that matters for
# a gas-like supercritical H2 layer heated to several times the bulk
# temperature, evaluated on REAL temperature-dependent properties
# (cooling/coolant_state.py). Below Re 2300 the fully-developed laminar floor
# Nu = 4.36 (uniform heat flux, textbook) replaces the turbulent form.
SIEDER_TATE_C = 0.027
SIEDER_TATE_RE_EXP = 0.8
SIEDER_TATE_PR_EXP = 1.0 / 3.0
SIEDER_TATE_VISC_EXP = 0.14
LAMINAR_NU = 4.36
RE_LAMINAR = 2300.0
CHANNEL_DP_CALIBRATION = 0.93          # single free multiplier on the summed straight-channel
                                       # Darcy dP - folds together the manifold entry/exit and
                                       # throat U-turn losses this 1-D single-pass march omits
                                       # AND the fact that a real jacket is not one perfectly
                                       # straight tube. Tuned so the reference regen design
                                       # (see module docstring) lands at ~1.6 MPa - the tool's
                                       # long-standing flat JACKET_DP_PA. Same trust tier as
                                       # BARTZ_SIGMA; pinned by validate.py's cooling check.

# --- jacket wall construction ------------------------------------------------
# The cooled wall can be built three ways, each with its own coolant-side heat
# transfer, jacket pressure drop and structural mass. "milled_channel" is the
# reference (the channel model above is calibrated to it: SSME MCC-class slotted
# liner). Multipliers are Tier 3 - the DIRECTION is solid (a brazed tube bundle
# runs a bit hotter and heavier than milled channels; a single coax annulus is
# gentler on dP but the worst heat-transfer and the heaviest structure), the
# magnitudes are engineering estimates.
#   milled_channel : SSME / RS-25 main chamber (reference, all factors 1.0)
#   tube_wall      : F-1, J-2, RL10 - brazed formed-tube bundle + outer jacket
#   coax_shell     : V-2, early Atlas - one annular gap between two shells
WALL_CONSTRUCTIONS = ("milled_channel", "tube_wall", "coax_shell")
H_C_CONSTRUCTION_FACTOR = {            # multiplies the Dittus-Boelter coolant-side h_c
    "milled_channel": 1.00,
    "tube_wall": 0.85,                 # round tubes: lower wetted-perimeter efficiency
    "coax_shell": 0.55,               # one low-velocity annular passage
}
DP_CONSTRUCTION_FACTOR = {            # multiplies the summed jacket Darcy dP
    "milled_channel": 1.00,
    "tube_wall": 1.15,               # extra tube bends / return manifold
    "coax_shell": 0.50,             # one big annulus, low velocity
}
JACKET_MASS_CONSTRUCTION_FACTOR = {   # extra structural mass vs the bare hoop-stress shell
    "milled_channel": 1.00,           # already what shell_mass_kg captures
    "tube_wall": 1.20,               # braze-filled tube bundle + structural jacket
    "coax_shell": 1.35,             # full structural outer shell
}


def channel_count(throat_dia_m, override=0):
    """Number of coolant channels around the circumference. Auto: from a
    throat-diameter-scaled pitch, so the count comes out roughly constant
    (~200-250) across engine sizes, matching real practice."""
    if override and override > 0:
        return int(override)
    if throat_dia_m <= 0:
        return CHANNEL_MIN_COUNT
    pitch = min(CHANNEL_PITCH_MAX_M,
                max(CHANNEL_PITCH_MIN_M, CHANNEL_PITCH_FRACTION * throat_dia_m))
    return max(CHANNEL_MIN_COUNT, round(math.pi * throat_dia_m / pitch))


def channel_target_height_m(throat_dia_m, n_channels, mdot_coolant_kgs, pair,
                             land_fraction, aspect_ratio_override=0.0,
                             target_velocity_ms=0.0, rho_kg_m3=None):
    """Channel height that makes the THROAT coolant velocity equal
    TARGET_COOLANT_VELOCITY_MS (so jacket dP is scale-invariant), unless the
    user pins an aspect ratio. `target_velocity_ms>0` replaces the per-pair
    target (EngineDesign.regen_coolant_velocity_ms). `rho_kg_m3` = the coolant
    density the channel is sized at (the real inlet-state density from
    CoolantModel); None -> the legacy per-pair constant. Returns (height_m,
    throat_width_m)."""
    pitch = math.pi * throat_dia_m / n_channels if n_channels > 0 else throat_dia_m
    width = max(1e-5, pitch * (1.0 - land_fraction))
    if aspect_ratio_override and aspect_ratio_override > 0:
        return width * aspect_ratio_override, width
    rho = rho_kg_m3 if rho_kg_m3 else COOLANT_DENSITY_KG_M3.get(pair, _COOLANT_DENSITY_FALLBACK)
    v_target = (target_velocity_ms if target_velocity_ms and target_velocity_ms > 0
                else TARGET_COOLANT_VELOCITY_MS.get(pair, _TARGET_COOLANT_VELOCITY_FALLBACK))
    total_area_needed = mdot_coolant_kgs / (rho * v_target) if rho > 0 and v_target > 0 else 0.0
    height = total_area_needed / (n_channels * width) if n_channels > 0 and width > 0 else width
    height = min(height, width * CHANNEL_ASPECT_RATIO_MAX)
    return max(height, width * 0.5), width


def channel_count_at_station(n_channels_base, local_eps, split_eps):
    """Real F-1-style channel-COUNT doubling (e.g. 178->356) once the contour
    reaches `split_eps` area ratio, keeping per-channel width from growing
    unbounded as circumference increases downstream of the split. Matches
    `EngineDesign.tube_split_eps` - previously a 3D-preview-only rendering
    field (gui/preview3d_gl.py/preview3d_gl_core.py), now also real physics
    via march_coolant()/channel_geometry_profile() below.
    `split_eps<=0` (the default) means no split - unchanged prior behavior,
    a single channel count for the whole march."""
    if split_eps and split_eps > 0 and local_eps >= split_eps:
        return 2 * n_channels_base
    return n_channels_base


def channel_hydraulic_geometry(local_dia_m, n_channels, channel_height_m, land_fraction):
    """Per-station channel width/height/flow-area/hydraulic-diameter for
    `n_channels` rectangular channels of fixed height `channel_height_m` wrapped
    around a wall of `local_dia_m` (channels widen as the circumference grows)."""
    if local_dia_m <= 0 or n_channels <= 0:
        return dict(width_m=0.0, height_m=0.0, area_m2=0.0, dh_m=0.0, total_area_m2=0.0)
    pitch = math.pi * local_dia_m / n_channels
    width = max(1e-5, pitch * (1.0 - land_fraction))
    height = max(1e-5, channel_height_m)
    area = width * height
    perim = 2.0 * (width + height)
    dh = 4.0 * area / perim if perim > 0 else 0.0
    return dict(width_m=width, height_m=height, area_m2=area, dh_m=dh,
                total_area_m2=area * n_channels)


def passage_velocity_ms(local_dia_m, throat_dia_m, mdot_coolant_kgs, pair, *,
                        n_channels=0, aspect_ratio=0.0, land_fraction=0.0, split_eps=0.0,
                        target_velocity_ms=0.0, rho_kg_m3=None):
    """Bulk coolant velocity in the jacket passages at a station of wall
    diameter `local_dia_m`: V = mdot / (rho * total passage flow area) - the
    exact expression march_coolant() uses per segment, but as a pure function
    of the same channel-sizing relations (channel_count /
    channel_target_height_m / channel_count_at_station /
    channel_hydraulic_geometry), so it is available in BOTH regen channel
    models ("flat" never runs the march). Used to size the regen-jacket
    manifold rings off the passages they feed: SP-8087's constant-velocity
    torus theory gives every passage the same inlet velocity [SP-8087
    Sec.2.1.2.1 p.19-20], and Fagherazzi's supply-volute design explicitly
    avoids abrupt velocity changes between the volute and the channels
    [Fagherazzi, see claude_lit/sources/fagherazzi-regen-cooling-thesis.md]."""
    if local_dia_m <= 0 or throat_dia_m <= 0 or mdot_coolant_kgs <= 0:
        return 0.0
    n_ch = channel_count(throat_dia_m, n_channels)
    lf = land_fraction if land_fraction and land_fraction > 0 else CHANNEL_LAND_FRACTION_DEFAULT
    height, _ = channel_target_height_m(throat_dia_m, n_ch, mdot_coolant_kgs, pair, lf,
                                        aspect_ratio_override=aspect_ratio,
                                        target_velocity_ms=target_velocity_ms,
                                        rho_kg_m3=rho_kg_m3)
    n_station = (channel_count_at_station(n_ch, _local_area_ratio(local_dia_m / 2.0,
                                                                  throat_dia_m / 2.0), split_eps)
                 if split_eps and split_eps > 0 else n_ch)
    g = channel_hydraulic_geometry(local_dia_m, n_station, height, lf)
    rho = rho_kg_m3 if rho_kg_m3 else COOLANT_DENSITY_KG_M3.get(pair, _COOLANT_DENSITY_FALLBACK)
    if g["total_area_m2"] <= 0 or rho <= 0:
        return 0.0
    return mdot_coolant_kgs / (rho * g["total_area_m2"])


def channel_geometry_profile(xs_m, rs_m, n_channels, channel_height_m, land_fraction,
                              throat_dia_m=0.0, split_eps=0.0):
    """Per-station channel/tube width/height/hydraulic-diameter across the
    WHOLE contour, for the 3D preview's rib pattern only - a separate,
    additive wrapper around channel_hydraulic_geometry(). Unlike
    march_coolant() (which restricts itself to the actively-cooled segments,
    in coolant-flow order, and feeds jacket dP / coolant temperature rise),
    this covers every station in xs_m/rs_m and feeds no lumped physics
    number - march_coolant's own internal per-station calls and outputs are
    untouched by this function's existence.

    `throat_dia_m`/`split_eps`: when both given, channel COUNT doubles past
    `split_eps` area ratio (channel_count_at_station) - matches the real
    channel count march_coolant() now uses, so the rendered rib pattern and
    the actual flow physics agree. `throat_dia_m<=0` (the default) skips the
    area-ratio computation entirely and reproduces the prior no-split
    behavior exactly."""
    xs_m = np.asarray(xs_m, dtype=float)
    rs_m = np.asarray(rs_m, dtype=float)
    n = rs_m.size
    width_m = np.zeros(n)
    height_m = np.zeros(n)
    dh_m = np.zeros(n)
    area_m2 = np.zeros(n)
    n_station_arr = np.zeros(n, dtype=int)
    total_area_m2 = np.zeros(n)
    rt = throat_dia_m / 2.0 if throat_dia_m > 0 else 0.0
    for i, r in enumerate(rs_m):
        n_ch_station = n_channels
        if rt > 0 and split_eps and split_eps > 0:
            n_ch_station = channel_count_at_station(
                n_channels, _local_area_ratio(r, rt), split_eps)
        g = channel_hydraulic_geometry(2.0 * r, n_ch_station, channel_height_m, land_fraction)
        width_m[i] = g["width_m"]
        height_m[i] = g["height_m"]
        dh_m[i] = g["dh_m"]
        area_m2[i] = g["area_m2"]
        n_station_arr[i] = n_ch_station
        total_area_m2[i] = g["total_area_m2"]
    return dict(width_m=width_m, height_m=height_m, dh_m=dh_m, area_m2=area_m2,
                n_channels_station=n_station_arr, total_area_m2=total_area_m2)


def coolant_side_htc(mdot_coolant_kgs, total_area_m2, dh_m, pair,
                     construction="milled_channel", *, props=None, mu_wall_pa_s=None):
    """Coolant-side convective coefficient h_c [W/m^2/K] and channel Reynolds
    number: Sieder-Tate turbulent / laminar floor (see SIEDER_TATE_C), scaled by
    the wall-construction factor (milled_channel = 1.0 reference).
    `props` = (rho, cp, mu, k) at the local bulk state (CoolantModel.props);
    None -> the legacy per-pair constants. `mu_wall_pa_s` = coolant viscosity
    at the coolant-side wall temperature (None -> ratio 1)."""
    if props is not None:
        _, cp, mu, k = props
    else:
        k, mu = COOLANT_TRANSPORT.get(pair, _COOLANT_TRANSPORT_FALLBACK)
        cp = FUEL_CP_J_KGK.get(pair, 2100.0)
    if total_area_m2 <= 0 or dh_m <= 0 or mu <= 0 or k <= 0:
        return 0.0, 0.0
    g_flux = mdot_coolant_kgs / total_area_m2          # coolant mass flux [kg/m^2/s]
    re = g_flux * dh_m / mu
    pr = mu * cp / k
    visc = (mu / mu_wall_pa_s) ** SIEDER_TATE_VISC_EXP if mu_wall_pa_s and mu_wall_pa_s > 0 else 1.0
    nu_turb = SIEDER_TATE_C * re ** SIEDER_TATE_RE_EXP * pr ** SIEDER_TATE_PR_EXP * visc
    nu = LAMINAR_NU if re < RE_LAMINAR else max(LAMINAR_NU, nu_turb)
    h_c = nu * k / dh_m * H_C_CONSTRUCTION_FACTOR.get(construction, 1.0)
    return h_c, re


def rib_fin_factor(h_c_w_m2k, width_m, pitch_m, height_m, k_wall_w_mk):
    """Rib / fin correction of the coolant-side coefficient, referred to the
    hot-wall area [EUCASS-2023 Eq. 24-25]: the lands (mid-walls) between
    channels conduct heat down into the coolant like fins, so
        eta_f  = tanh(m h_ch) / (m h_ch),  m = sqrt(2 h_c / (k_wall t_mw))
        h_c,f  = h_c (w_ch + 2 eta_f h_ch) / (w_ch + t_mw)
    with t_mw = pitch - width. Array-friendly; returns 1.0 where the geometry
    is degenerate. [SP-8087 Sec.3.1.1.4.3] makes the same point qualitatively
    ("enhanced two-dimensional (fin) cooling" through conductive lands)."""
    h = np.asarray(h_c_w_m2k, dtype=float)
    w = np.asarray(width_m, dtype=float)
    p = np.asarray(pitch_m, dtype=float)
    hc = np.asarray(height_m, dtype=float)
    k = np.asarray(k_wall_w_mk, dtype=float)
    t_mw = p - w
    ok = (np.isfinite(h) & np.isfinite(w) & np.isfinite(p) & (h > 0) & (w > 0)
          & (t_mw > 0) & (hc > 0) & (k > 0))
    with np.errstate(invalid="ignore", divide="ignore"):
        mh = np.sqrt(2.0 * h / (k * t_mw)) * hc
        eta = np.where(mh > 1e-9, np.tanh(mh) / mh, 1.0)
        f = (w + 2.0 * eta * hc) / (w + t_mw)
    return np.where(ok, f, 1.0)


# Constructions whose passages are separated by conducting lands/tube walls
# (the fin correction applies); a coax shell is one open annulus - no ribs.
FIN_CONSTRUCTIONS = ("milled_channel", "tube_wall")


def _darcy_friction(re, dh_m, roughness_m=None):
    """Darcy friction factor: laminar 64/Re below Re 2300, else Haaland.
    `roughness_m` defaults to the milled-channel CHANNEL_ROUGHNESS_M
    (physics/plumbing.py passes its own drawn-tubing value)."""
    if re < 1.0:
        return 0.02
    if re < 2300.0:
        return 64.0 / re
    rough = CHANNEL_ROUGHNESS_M if roughness_m is None else roughness_m
    eps_rel = rough / dh_m if dh_m > 0 else 0.0
    inv_sqrt_f = -1.8 * math.log10((eps_rel / 3.7) ** 1.11 + 6.9 / re)
    return 1.0 / inv_sqrt_f ** 2 if inv_sqrt_f != 0 else 0.02
