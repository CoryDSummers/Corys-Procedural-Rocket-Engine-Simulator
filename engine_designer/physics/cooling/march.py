"""1-D coolant marches: single-pass counterflow and the J-2 two-pass layout.

Part of the physics/cooling/ package (split verbatim out of the former
single-file cooling.py - see cooling/__init__.py for the package overview)."""
import math

import numpy as np

from .channels import (
    CHANNEL_DP_CALIBRATION,
    CHANNEL_LAND_FRACTION_DEFAULT,
    DP_CONSTRUCTION_FACTOR,
    _darcy_friction,
    channel_count,
    channel_count_at_station,
    channel_hydraulic_geometry,
    channel_target_height_m,
    coolant_side_htc,
)
from .coolant_props import COOLANT_DENSITY_KG_M3, FUEL_CP_J_KGK, _COOLANT_DENSITY_FALLBACK
from .profile import _frustum_area, _local_area_ratio, bend_segments

def _passage_v(mdot_kgs, rho, total_area_m2):
    """Bulk passage velocity mdot/(rho*A), 0 for a degenerate passage."""
    return mdot_kgs / (rho * total_area_m2) if rho > 0 and total_area_m2 > 0 else 0.0


class _Bulk:
    """Coolant bulk state carried along a march: temperature + (with a real
    CoolantModel) enthalpy, so heat is added as enthalpy - exact across the
    supercritical H2/CH4 cp peak - instead of the constant-cp cp*dT step."""

    def __init__(self, pair, t_k, model):
        self.pair, self.t, self.model = pair, float(t_k), model
        self.h = model.h(self.t) if model is not None else None
        self._cp = FUEL_CP_J_KGK.get(pair, 2100.0)
        self._rho = COOLANT_DENSITY_KG_M3.get(pair, _COOLANT_DENSITY_FALLBACK)

    def props(self):
        """(rho, cp, props-or-None) at the current bulk temperature."""
        if self.model is None:
            return self._rho, self._cp, None
        p = self.model.props(self.t)
        return p[0], p[1], p

    def mu_wall(self, t_wall_k):
        if self.model is None or t_wall_k is None or not np.isfinite(t_wall_k):
            return None
        return self.model.props(float(t_wall_k))[2]

    def add_heat(self, q_w, mdot):
        if mdot <= 0 or q_w == 0.0:
            return 0.0
        t0 = self.t
        if self.model is None:
            self.t += q_w / (mdot * self._cp)
        else:
            self.h += q_w / mdot
            self.t = self.model.t_from_h(self.h)
        return self.t - t0


def _seg_bend(bends, i):
    """(radius, sign, s, length) of segment i for channels.curvature_factor."""
    return (bends["radius_m"][i], bends["sign"][i], bends["s_m"][i], bends["length_m"][i])


def _seg_wall_t(t_wall_profile, i):
    """Mean coolant-side wall temperature of segment i from a per-station
    profile (None / NaN-safe)."""
    if t_wall_profile is None:
        return None
    a, b = t_wall_profile[i], t_wall_profile[i + 1]
    vals = [v for v in (a, b) if v is not None and np.isfinite(v)]
    return sum(vals) / len(vals) if vals else None


def _segments_to_stations(seg_vals, n):
    """Map per-segment march values (length n-1, NaN = segment not cooled) onto
    the n contour stations: each station takes the mean of its cooled adjacent
    segments (NaN where neither is cooled)."""
    seg_vals = np.asarray(seg_vals, dtype=float)
    left = np.concatenate([[np.nan], seg_vals])     # segment ending at station j
    right = np.concatenate([seg_vals, [np.nan]])    # segment starting at station j
    both = np.vstack([left, right])
    cnt = np.sum(np.isfinite(both), axis=0)
    tot = np.nansum(both, axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(cnt > 0, tot / np.maximum(cnt, 1), np.nan)


def march_coolant(xs_m, rs_m, q_profile_w_m2, throat_dia_m, mdot_coolant_kgs, pair,
                  *, n_channels=0, aspect_ratio=0.0, land_fraction=0.0,
                  transition_area_ratio=None, t_inlet_k=None,
                  construction="milled_channel", split_eps=0.0,
                  target_velocity_ms=0.0, coolant_model=None, t_wall_coolant_profile_k=None,
                  rho_sizing_kg_m3=None):
    """
    Counterflow 1-D coolant march over the actively-cooled contour (injector face
    through the throat and out to `transition_area_ratio`). The coolant enters at
    the nozzle (transition) end and flows toward the injector.

    Returns dict(coolant_exit_t_k, coolant_delta_t_k, jacket_dp_pa, n_channels,
    channel_dh_throat_m, t_wc_throat_k) - `t_wc_throat_k` is the coolant-side
    wall temperature at the throat (bulk coolant temp there + the convective film
    rise q/h_c), the number physics/design.py adds the through-wall gradient to.

    `split_eps>0`: channel COUNT doubles past that area ratio
    (channel_count_at_station - real F-1-style practice), changing per-segment
    flow area hence h_c/Re/dP downstream of the split station. `n_channels` in
    the returned dict stays the BASE (pre-split) count, unchanged in meaning.
    Default 0.0 reproduces the prior single-count-throughout behavior exactly.

    `coolant_model` (cooling.coolant_state.CoolantModel): real temperature-
    dependent coolant properties per segment + an enthalpy march; channels are
    sized at the INLET-state density. `t_wall_coolant_profile_k`: per-station
    coolant-side wall temperature (from the previous thermal-solve iteration)
    for the Sieder-Tate wall-viscosity term. Both None -> the legacy constant-
    property march.
    """
    xs = np.asarray(xs_m, dtype=float)
    rs = np.asarray(rs_m, dtype=float)
    q = np.asarray(q_profile_w_m2, dtype=float)
    rt = throat_dia_m / 2.0
    throat_idx = int(np.argmin(rs))
    bends = bend_segments(xs, rs, throat_dia_m)       # [EUCASS-2023 Eq.22] curvature
    n_ch = channel_count(throat_dia_m, n_channels)
    lf = land_fraction if land_fraction and land_fraction > 0 else CHANNEL_LAND_FRACTION_DEFAULT
    bulk = _Bulk(pair, t_inlet_k if t_inlet_k is not None else 290.0, coolant_model)
    rho_inlet = bulk.props()[0]
    # Fixed channel height, sized at the throat to hit the target coolant
    # velocity (or the user's aspect-ratio override). Channels then widen away
    # from the throat as the circumference grows.
    ch_height_m, _ = channel_target_height_m(throat_dia_m, n_ch, mdot_coolant_kgs,
                                              pair, lf, aspect_ratio_override=aspect_ratio,
                                              target_velocity_ms=target_velocity_ms,
                                              rho_kg_m3=(rho_sizing_kg_m3 or rho_inlet) if coolant_model else None)
    t_bulk = bulk.t
    v_seg = np.full(max(len(rs) - 1, 0), np.nan)
    w_seg = np.full(max(len(rs) - 1, 0), np.nan)       # channel width (fin correction)
    p_seg = np.full(max(len(rs) - 1, 0), np.nan)       # channel pitch

    # Segment indices upstream of the transition area ratio, in COOLANT-flow
    # order (from the nozzle/transition end toward the injector).
    seg = []
    for i in range(len(rs) - 1):
        if (transition_area_ratio is not None and i >= throat_idx
                and _local_area_ratio(max(rs[i], rs[i + 1]), rt) > transition_area_ratio + 1e-9):
            continue
        seg.append(i)
    seg_flow = list(reversed(seg))

    delta_t = 0.0
    dp_total = 0.0
    t_wc_throat = None
    dh_throat = 0.0
    throat_state = (t_bulk, 0.0, 0.0)
    h_c_seg = np.full(max(len(rs) - 1, 0), np.nan)    # per-segment, for the
    t_bulk_seg = np.full(max(len(rs) - 1, 0), np.nan)  # full-length wall balance
    for i in seg_flow:
        local_dia = rs[i] + rs[i + 1]
        n_ch_station = (channel_count_at_station(n_ch, _local_area_ratio(local_dia / 2.0, rt), split_eps)
                        if split_eps and split_eps > 0 else n_ch)
        g = channel_hydraulic_geometry(local_dia, n_ch_station, ch_height_m, lf)
        a_seg = _frustum_area(xs[i], rs[i], xs[i + 1], rs[i + 1])
        q_seg = 0.5 * (q[i] + q[i + 1])
        rho, _cp, props = bulk.props()
        h_c, re = coolant_side_htc(mdot_coolant_kgs, g["total_area_m2"], g["dh_m"], pair,
                                   construction=construction, props=props,
                                   mu_wall_pa_s=bulk.mu_wall(_seg_wall_t(t_wall_coolant_profile_k, i)),
                                   bend=_seg_bend(bends, i))

        d_t = bulk.add_heat(q_seg * a_seg, mdot_coolant_kgs)
        t_bulk = bulk.t
        delta_t += d_t

        t_wc = t_bulk + (q_seg / h_c if h_c > 0 else 0.0)
        v = _passage_v(mdot_coolant_kgs, rho, g["total_area_m2"])
        if abs(i - throat_idx) <= 1 and (t_wc_throat is None or t_wc > t_wc_throat):
            t_wc_throat = t_wc
            dh_throat = g["dh_m"]
            throat_state = (t_bulk, h_c, v)
        h_c_seg[i] = h_c
        t_bulk_seg[i] = t_bulk
        v_seg[i] = v
        w_seg[i] = g["width_m"]
        p_seg[i] = math.pi * local_dia / n_ch_station if n_ch_station > 0 else np.nan

        if g["total_area_m2"] > 0 and g["dh_m"] > 0 and rho > 0:
            length = math.hypot(xs[i + 1] - xs[i], rs[i + 1] - rs[i])
            f = _darcy_friction(re, g["dh_m"])
            dp_total += f * (length / g["dh_m"]) * 0.5 * rho * v * v

    dp_total *= CHANNEL_DP_CALIBRATION * DP_CONSTRUCTION_FACTOR.get(construction, 1.0)
    if t_wc_throat is None:
        t_wc_throat = t_bulk
    return dict(coolant_exit_t_k=t_bulk, coolant_delta_t_k=delta_t,
                jacket_dp_pa=dp_total, n_channels=n_ch,
                channel_dh_throat_m=dh_throat, t_wc_throat_k=t_wc_throat,
                t_bulk_throat_k=throat_state[0], h_c_throat_w_m2k=throat_state[1],
                v_throat_ms=throat_state[2], channel_height_m=ch_height_m,
                rho_inlet_kg_m3=rho_inlet,
                # per-STATION (NaN outside the cooled length) - additive, for
                # the full-length coupled wall balance
                h_c_profile_w_m2k=_segments_to_stations(h_c_seg, len(rs)),
                t_bulk_profile_k=_segments_to_stations(t_bulk_seg, len(rs)),
                velocity_profile_ms=_segments_to_stations(v_seg, len(rs)),
                channel_width_profile_m=_segments_to_stations(w_seg, len(rs)),
                channel_pitch_profile_m=_segments_to_stations(p_seg, len(rs)))


# Real J-2 regen circuit: "LH2 fuel from the fuel manifold circulated downward
# through 180 tubes, and back upward through 360 tubes to the thrust chamber
# injector" (literature/Rocket Propulsion Evolution_ 8.22 - J-2 Engine.html,
# thrust-chamber section; the cutaway there puts the fuel manifold partway down
# the nozzle). Tier 2 - one real engine's documented tube counts, informal
# (non-claude_lit) source. The F-1's 178 down / 356 return shares the same 1:2.
J2_DOWN_TO_UP_TUBE_RATIO = 0.5


def two_pass_tube_counts(throat_dia_m, n_channels=0):
    """(n_up, n_down) for the J-2-style two-pass circuit: the up (return)
    tubes run the full length and keep the single-pass channel_count - so the
    throat, which only up-tubes cross, is sized exactly as today - and the
    down tubes are J2_DOWN_TO_UP_TUBE_RATIO of them, sharing the circumference
    only downstream of the mid-nozzle inlet."""
    n_up = channel_count(throat_dia_m, n_channels)
    return n_up, max(1, round(n_up * J2_DOWN_TO_UP_TUBE_RATIO))


def down_pass_velocity_ms(local_dia_m, throat_dia_m, mdot_coolant_kgs, pair, *,
                          n_channels=0, aspect_ratio=0.0, land_fraction=0.0,
                          target_velocity_ms=0.0, rho_kg_m3=None):
    """Bulk coolant velocity in the DOWN tubes of the two-pass circuit at a
    station of wall diameter `local_dia_m` in the shared (down+up) region -
    pure, like passage_velocity_ms, so the mid-nozzle jacket-inlet ring can be
    sized off it in either regen channel model. Down and up tubes share the
    circumference (width = pi*D/(n_up+n_down)), so the down pass runs
    (n_up+n_down)/n_down = 3x faster than a single-pass jacket at the same
    station would."""
    if local_dia_m <= 0 or throat_dia_m <= 0 or mdot_coolant_kgs <= 0:
        return 0.0
    n_up, n_down = two_pass_tube_counts(throat_dia_m, n_channels)
    lf = land_fraction if land_fraction and land_fraction > 0 else CHANNEL_LAND_FRACTION_DEFAULT
    height, _ = channel_target_height_m(throat_dia_m, n_up, mdot_coolant_kgs, pair, lf,
                                        aspect_ratio_override=aspect_ratio,
                                        target_velocity_ms=target_velocity_ms,
                                        rho_kg_m3=rho_kg_m3)
    g = channel_hydraulic_geometry(local_dia_m, n_up + n_down, height, lf)
    rho = rho_kg_m3 if rho_kg_m3 else COOLANT_DENSITY_KG_M3.get(pair, _COOLANT_DENSITY_FALLBACK)
    area_down = g["area_m2"] * n_down
    return mdot_coolant_kgs / (rho * area_down) if area_down > 0 and rho > 0 else 0.0


def march_coolant_two_pass(xs_m, rs_m, q_profile_w_m2, throat_dia_m, mdot_coolant_kgs, pair,
                           *, inlet_area_ratio, n_channels=0, aspect_ratio=0.0,
                           land_fraction=0.0, transition_area_ratio=None, t_inlet_k=None,
                           construction="milled_channel", target_velocity_ms=0.0,
                           coolant_model=None, t_wall_coolant_profile_k=None,
                  rho_sizing_kg_m3=None):
    """
    J-2-style two-pass regen march (EngineDesign.cooling_flow_topology =
    "j2_mid_nozzle_inlet"): the coolant enters a manifold partway down the
    nozzle at `inlet_area_ratio`, flows DOWN n_down tubes to the cooled end
    (`transition_area_ratio`), turns around, and flows back UP n_up tubes over
    the whole cooled length to the injector (two_pass_tube_counts).

    Between the inlet and the cooled end both tube sets share the
    circumference (width = pi*D/(n_up+n_down), the same fixed height
    march_coolant uses) and split that segment's wall heat by circumference
    share; upstream of the inlet only the up tubes exist, exactly as in
    march_coolant. The down pass is marched first (from the inlet toward the
    exit), its outlet temperature carries through the turnaround into the up
    pass (exit -> injector). Per-pass Darcy dP uses the same Haaland friction
    and the same CHANNEL_DP_CALIBRATION x DP_CONSTRUCTION_FACTOR as
    march_coolant - no new calibration constant.

    Invariants (self-tested): an inlet at/after the cooled end (zero-length
    down pass) reproduces march_coolant (split_eps=0) exactly; the TOTAL
    coolant temperature rise equals march_coolant's for any inlet (same wall
    heat into the same mdot*cp); jacket dP grows with the down-pass length.

    Returns march_coolant's keys plus jacket_dp_down_pa, coolant_turnaround_t_k,
    down_pass_inlet_velocity_ms and n_channels_down.
    """
    xs = np.asarray(xs_m, dtype=float)
    rs = np.asarray(rs_m, dtype=float)
    q = np.asarray(q_profile_w_m2, dtype=float)
    rt = throat_dia_m / 2.0
    throat_idx = int(np.argmin(rs))
    bends = bend_segments(xs, rs, throat_dia_m)       # [EUCASS-2023 Eq.22] curvature
    n_up, n_down = two_pass_tube_counts(throat_dia_m, n_channels)
    n_tot = n_up + n_down
    lf = land_fraction if land_fraction and land_fraction > 0 else CHANNEL_LAND_FRACTION_DEFAULT
    bulk = _Bulk(pair, t_inlet_k if t_inlet_k is not None else 290.0, coolant_model)
    rho_inlet = bulk.props()[0]
    ch_height_m, _ = channel_target_height_m(throat_dia_m, n_up, mdot_coolant_kgs,
                                              pair, lf, aspect_ratio_override=aspect_ratio,
                                              target_velocity_ms=target_velocity_ms,
                                              rho_kg_m3=(rho_sizing_kg_m3 or rho_inlet) if coolant_model else None)
    t0 = bulk.t

    seg = []
    for i in range(len(rs) - 1):
        if (transition_area_ratio is not None and i >= throat_idx
                and _local_area_ratio(max(rs[i], rs[i + 1]), rt) > transition_area_ratio + 1e-9):
            continue
        seg.append(i)

    # Per-segment split at the inlet station: the segment containing it is
    # divided into an up-only part (upstream) and a shared part (downstream),
    # by LENGTH for friction and by frustum AREA for heat, so the inlet is
    # resolved at any contour resolution (a conical contour's one throat->exit
    # segment included) and the total wall heat is exactly conserved.
    # (length_frac_shared, area_frac_shared, up-only mean dia, shared mean dia)
    r_inlet = rt * math.sqrt(max(inlet_area_ratio, 1.0))

    def _split(i):
        r0, r1 = rs[i], rs[i + 1]
        mean_dia = r0 + r1
        if i < throat_idx or max(r0, r1) <= r_inlet:
            return 0.0, 0.0, mean_dia, mean_dia
        if min(r0, r1) >= r_inlet or r1 <= r0:
            return 1.0, 1.0, mean_dia, mean_dia
        t = (r_inlet - r0) / (r1 - r0)            # r is linear along the segment
        return 1.0 - t, (r_inlet + r1) * (1.0 - t) / (r0 + r1), r0 + r_inlet, r_inlet + r1

    def _dp(mdot, area, dh, re, length, rho):
        if area <= 0 or dh <= 0 or rho <= 0:
            return 0.0
        v = mdot / (rho * area)
        return _darcy_friction(re, dh) * (length / dh) * 0.5 * rho * v * v

    dp_scale = CHANNEL_DP_CALIBRATION * DP_CONSTRUCTION_FACTOR.get(construction, 1.0)

    # --- down pass: inlet -> cooled end (increasing x), shared parts only.
    dp_down = 0.0
    v_down_inlet = 0.0
    for i in seg:
        f_len, f_area, _, dia_sh = _split(i)
        if f_len <= 0.0:
            continue
        g = channel_hydraulic_geometry(dia_sh, n_tot, ch_height_m, lf)
        area = g["area_m2"] * n_down
        rho, _cp, props = bulk.props()
        if v_down_inlet == 0.0 and area > 0 and rho > 0:
            v_down_inlet = mdot_coolant_kgs / (rho * area)
        a_seg = _frustum_area(xs[i], rs[i], xs[i + 1], rs[i + 1])
        q_seg = 0.5 * (q[i] + q[i + 1])
        _, re = coolant_side_htc(mdot_coolant_kgs, area, g["dh_m"], pair,
                                 construction=construction, props=props)
        bulk.add_heat(q_seg * a_seg * f_area * (n_down / n_tot), mdot_coolant_kgs)
        dp_down += _dp(mdot_coolant_kgs, area, g["dh_m"], re,
                       f_len * math.hypot(xs[i + 1] - xs[i], rs[i + 1] - rs[i]), rho)
    t_bulk = bulk.t
    t_turn = t_bulk

    # --- up pass: cooled end -> injector; within a split segment the coolant
    # meets the shared (downstream) part first, then the up-only part.
    dp_up = 0.0
    t_wc_throat = None
    dh_throat = 0.0
    throat_state = (t_bulk, 0.0, 0.0)
    # Per-segment UP-pass state (the tubes that cross the throat and carry the
    # warmer, returning coolant - the conservative wall in the shared region).
    h_c_seg = np.full(max(len(rs) - 1, 0), np.nan)
    t_bulk_seg = np.full(max(len(rs) - 1, 0), np.nan)
    v_seg = np.full(max(len(rs) - 1, 0), np.nan)
    w_seg = np.full(max(len(rs) - 1, 0), np.nan)
    p_seg = np.full(max(len(rs) - 1, 0), np.nan)
    for i in reversed(seg):
        f_len, f_area, dia_up, dia_sh = _split(i)
        a_seg = _frustum_area(xs[i], rs[i], xs[i + 1], rs[i + 1])
        q_seg = 0.5 * (q[i] + q[i + 1])
        seg_len = math.hypot(xs[i + 1] - xs[i], rs[i + 1] - rs[i])
        parts = []
        if f_len > 0.0:
            g = channel_hydraulic_geometry(dia_sh, n_tot, ch_height_m, lf)
            parts.append((g, g["area_m2"] * n_up, f_area * n_up / n_tot, f_len,
                          math.pi * dia_sh / n_tot))
        if f_len < 1.0:
            g = channel_hydraulic_geometry(dia_up, n_up, ch_height_m, lf)
            parts.append((g, g["total_area_m2"], 1.0 - f_area, 1.0 - f_len,
                          math.pi * dia_up / n_up))
        for g, area, heat_share, len_share, pitch in parts:
            rho, _cp, props = bulk.props()
            h_c, re = coolant_side_htc(
                mdot_coolant_kgs, area, g["dh_m"], pair, construction=construction,
                props=props, mu_wall_pa_s=bulk.mu_wall(_seg_wall_t(t_wall_coolant_profile_k, i)),
                bend=_seg_bend(bends, i))
            bulk.add_heat(q_seg * a_seg * heat_share, mdot_coolant_kgs)
            t_bulk = bulk.t
            t_wc = t_bulk + (q_seg / h_c if h_c > 0 else 0.0)
            v = _passage_v(mdot_coolant_kgs, rho, area)
            h_c_seg[i] = h_c
            t_bulk_seg[i] = t_bulk
            v_seg[i] = v
            w_seg[i] = g["width_m"]
            p_seg[i] = pitch
            if abs(i - throat_idx) <= 1 and (t_wc_throat is None or t_wc > t_wc_throat):
                t_wc_throat = t_wc
                dh_throat = g["dh_m"]
                throat_state = (t_bulk, h_c, v)
            dp_up += _dp(mdot_coolant_kgs, area, g["dh_m"], re, len_share * seg_len, rho)

    if t_wc_throat is None:
        t_wc_throat = t_bulk
    return dict(coolant_exit_t_k=t_bulk, coolant_delta_t_k=t_bulk - t0,
                jacket_dp_pa=(dp_down + dp_up) * dp_scale, n_channels=n_up,
                channel_dh_throat_m=dh_throat, t_wc_throat_k=t_wc_throat,
                jacket_dp_down_pa=dp_down * dp_scale, coolant_turnaround_t_k=t_turn,
                down_pass_inlet_velocity_ms=v_down_inlet, n_channels_down=n_down,
                t_bulk_throat_k=throat_state[0], h_c_throat_w_m2k=throat_state[1],
                v_throat_ms=throat_state[2], channel_height_m=ch_height_m,
                rho_inlet_kg_m3=rho_inlet,
                h_c_profile_w_m2k=_segments_to_stations(h_c_seg, len(rs)),
                t_bulk_profile_k=_segments_to_stations(t_bulk_seg, len(rs)),
                velocity_profile_ms=_segments_to_stations(v_seg, len(rs)),
                channel_width_profile_m=_segments_to_stations(w_seg, len(rs)),
                channel_pitch_profile_m=_segments_to_stations(p_seg, len(rs)))
