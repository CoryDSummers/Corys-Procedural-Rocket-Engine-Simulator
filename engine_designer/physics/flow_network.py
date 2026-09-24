"""
Propellant flow network - the data contract behind the 3D preview's flow
visualization. Walks one EngineDesign.compute() result and returns, per
stream (fuel / ox / hot gas), an ORDERED list of FlowSegments giving the
stream's temperature along its route: feed line -> manifold ring -> regen
jacket pass(es) -> injector ring, and the hot gas from the injector face out
through the nozzle.

No new physics and no 3D geometry here: every number comes from the result
(the coolant march, the stream inlet-temperature tables, Tc/gamma + the
isentropic relations), and each segment carries only an ANCHOR naming the
geometry it lives on (profile stations, a manifold host, a plumbing host).
gui/mesh_builder.build_flow_pieces maps anchors onto the RENDERED shells, so
flow tubes always sit inside what is drawn. The pending cooling rework only
has to keep filling the same fields. The hot-gas segment is kept as data but
the 3D view doesn't draw it (Cory's call, 2026-09-24: the chamber stays a
plain X-ray wall; only the propellant plumbing is colored).

Exact vs approximate (FlowSegment.approximate):
  - "channels" regen mode: jacket temperatures are the march's own per-station
    bulk temperatures (result["cooling"]["coolant_t_bulk_profile_k"]) - exact
    to the model. Two-pass (J-2) down legs only have inlet/turnaround temps, so
    they are linear between those (approximate).
  - Any other regen mode: only the lumped coolant_delta_t_k exists, so the rise
    is distributed along the pass by the cumulative absorbed wall heat
    (q_profile_abs_w_m2 x local wall area) - approximate.
  - f1_split_reverse_flow is drawn as one pass (the physics lumps it too).
"""
from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import brentq

from . import isentropic

PROPELLANTS = ("fuel", "ox", "gas")
KINDS = ("feed_line", "manifold_ring", "jacket_pass", "chamber_gas")


@dataclass
class FlowSegment:
    propellant: str          # "fuel" | "ox" | "gas"
    kind: str                # one of KINDS
    anchor: dict             # {"host": ...} | {"stations": idx, "pass": "single"|"down"|"up"}
    t_k: np.ndarray          # temperature per sample (len 1 for a ring / feed line)
    order: int               # position along its stream (0 = upstream-most)
    approximate: bool = False
    x_m: np.ndarray = field(default=None)  # axial station per sample (station anchors only)


def _subsonic_mach(eps, gamma):
    if eps <= 1.0 + 1e-9:
        return 1.0
    return brentq(lambda m: isentropic.area_ratio_from_mach(m, gamma) - eps, 1e-7, 1.0 - 1e-12)


def gas_static_temperature_profile(result):
    """Static gas temperature at every profile station: Tc x isentropic T/T0 at
    the local area ratio - subsonic up to the throat, supersonic after."""
    xs, rs = np.asarray(result["profile_xs_m"]), np.asarray(result["profile_rs_m"])
    gamma, tc = float(result["gamma"]), float(result["tc_k"])
    i_t = int(np.argmin(rs))
    eps = (rs / rs[i_t]) ** 2
    t = np.empty_like(xs, dtype=float)
    for i, e in enumerate(eps):
        if i == i_t or e <= 1.0 + 1e-9:
            m = 1.0
        elif i < i_t:
            m = _subsonic_mach(e, gamma)
        else:
            m = isentropic.mach_from_area_ratio(e, gamma)
        t[i] = tc * isentropic.static_temperature_ratio(m, gamma)
    return t


def cooled_station_mask(result):
    """Profile stations under the regen jacket: the whole chamber/convergent
    plus the divergent section out to cooled_length_eps."""
    rs = np.asarray(result["profile_rs_m"])
    i_t = int(np.argmin(rs))
    eps = (rs / rs[i_t]) ** 2
    cle = result["cooling"].get("cooled_length_eps") or result.get("eps_for_transition") or 1.0
    idx = np.arange(rs.size)
    return (idx <= i_t) | (eps <= float(cle) + 1e-9)


def _heat_weighted(result, stations, t_start, t_end):
    """t_start -> t_end along `stations` (in flow order), distributed by the
    cumulative absorbed wall heat q_abs x 2 pi r ds."""
    xs, rs = np.asarray(result["profile_xs_m"]), np.asarray(result["profile_rs_m"])
    q = result["cooling"].get("q_profile_abs_w_m2")
    q = np.ones_like(xs) if q is None else np.nan_to_num(np.asarray(q, dtype=float))
    if len(stations) < 2:
        return np.full(len(stations), float(t_start))
    x, r, qq = xs[stations], rs[stations], q[stations]
    ds = np.hypot(np.diff(x), np.diff(r))
    dq = 0.5 * (qq[1:] * r[1:] + qq[:-1] * r[:-1]) * 2.0 * np.pi * ds
    cum = np.concatenate([[0.0], np.cumsum(np.maximum(dq, 0.0))])
    frac = cum / cum[-1] if cum[-1] > 0 else np.linspace(0.0, 1.0, len(stations))
    return float(t_start) + (float(t_end) - float(t_start)) * frac


def jacket_segments(result, order0=0):
    """Regen jacket pass segment(s), fuel, in flow order. [] if not regen."""
    cool = result["cooling"]
    if cool.get("chamber_cooling_method") != "regenerative":
        return []
    xs = np.asarray(result["profile_xs_m"])
    rs = np.asarray(result["profile_rs_m"])
    mask = cooled_station_mask(result)
    t_in = float(result.get("coolant_inlet_t_k", 290.0))
    dt = float(cool.get("coolant_delta_t_k") or 0.0)
    t_exit = cool.get("coolant_exit_t_k")
    t_exit = float(t_exit) if t_exit is not None else t_in + dt
    profile = cool.get("coolant_t_bulk_profile_k")
    up = np.flatnonzero(mask)[::-1]              # aft -> injector face
    segs = []
    if result.get("cooling_flow_topology") == "j2_mid_nozzle_inlet":
        i_t = int(np.argmin(rs))
        eps = (rs / rs[i_t]) ** 2
        inlet_eps = float(result.get("jacket_inlet_eps_effective") or 1.0)
        down = np.flatnonzero(mask & (np.arange(rs.size) > i_t) & (eps >= inlet_eps - 1e-9))
        t_turn = cool.get("coolant_turnaround_t_k")
        t_turn = float(t_turn) if t_turn is not None else t_in
        if down.size >= 2:
            segs.append(FlowSegment("fuel", "jacket_pass", {"stations": down, "pass": "down"},
                                    np.linspace(t_in, t_turn, down.size), order0,
                                    approximate=True, x_m=xs[down]))
            order0 += 1
        t_up_start = t_turn
    else:
        t_up_start = t_in
    if profile is not None:
        t_up = np.asarray(profile, dtype=float)[up]
        ok = np.isfinite(t_up)
        up, t_up = up[ok], t_up[ok]
        approx = False
    else:
        t_up = _heat_weighted(result, up, t_up_start, t_exit)
        approx = True
    if up.size >= 2:
        segs.append(FlowSegment("fuel", "jacket_pass", {"stations": up, "pass": "up"
                                if segs else "single"}, t_up, order0, approximate=approx,
                                x_m=xs[up]))
    return segs


def build_flow_network(result):
    """Ordered FlowSegments for every stream of one compute() result."""
    segs = []
    cool = result["cooling"]
    t_fuel_in = float(result.get("coolant_inlet_t_k", 290.0))
    t_ox_in = result.get("oxidizer_inlet_t_k")
    jm = result.get("jacket_manifold_result") or {}
    mr = result.get("manifold_result") or {}
    jacket = jacket_segments(result)
    regen = bool(jacket)
    t_jacket_exit = float(jacket[-1].t_k[-1]) if regen else t_fuel_in

    # --- fuel: feed line(s) -> jacket-inlet ring -> jacket -> injector ring ---
    o = 0
    if regen and jm.get("jacket_inlet"):
        segs.append(FlowSegment("fuel", "feed_line", {"host": "jacket_inlet"},
                                np.array([t_fuel_in]), o)); o += 1
        segs.append(FlowSegment("fuel", "manifold_ring", {"host": "jacket_inlet"},
                                np.array([t_fuel_in]), o)); o += 1
    for s in jacket:
        s.order = o; segs.append(s); o += 1
    if regen and jm.get("jacket_return"):
        segs.append(FlowSegment("fuel", "manifold_ring", {"host": "jacket_return"},
                                np.array([t_jacket_exit]), o, approximate=True)); o += 1
    if mr.get("fuel"):
        if not regen:
            segs.append(FlowSegment("fuel", "feed_line", {"host": "fuel"},
                                    np.array([t_fuel_in]), o)); o += 1
        segs.append(FlowSegment("fuel", "manifold_ring", {"host": "fuel"},
                                np.array([t_jacket_exit]), o, approximate=False)); o += 1

    # --- ox: feed line -> ox ring ---
    if t_ox_in is not None and mr.get("ox"):
        segs.append(FlowSegment("ox", "feed_line", {"host": "ox"}, np.array([float(t_ox_in)]), 0))
        segs.append(FlowSegment("ox", "manifold_ring", {"host": "ox"},
                                np.array([float(t_ox_in)]), 1))

    # --- hot gas: injector face -> nozzle exit ---
    xs = np.asarray(result["profile_xs_m"])
    stations = np.arange(xs.size)
    segs.append(FlowSegment("gas", "chamber_gas", {"stations": stations},
                            gas_static_temperature_profile(result), 0, x_m=xs))
    return segs


def temperature_range(segments, propellants=PROPELLANTS):
    """(min, max) temperature over every sample of the segments of
    `propellants` (the 3D view draws only ("fuel", "ox") - see
    gui/mesh_builder.build_flow_pieces)."""
    segments = [s for s in segments if s.propellant in propellants]
    vals = np.concatenate([np.atleast_1d(s.t_k) for s in segments]) if segments else np.zeros(1)
    vals = vals[np.isfinite(vals)]
    return float(vals.min()), float(vals.max())


def any_approximate(segments):
    return any(s.approximate for s in segments)


def self_test():
    from . import cycles
    from .design import EngineDesign

    base = dict(propellant_pair="LOX/RP-1", mixture_ratio=2.34, chamber_pressure_pa=8.0e6,
                expansion_ratio=14, nozzle_type="bell", bell_percent_length=80.0,
                cycle=cycles.GAS_GENERATOR, throttle_floor=0.6, target_vac_thrust_n=1_450_000)

    def _check_common(res, net):
        gas = [s for s in net if s.propellant == "gas"]
        assert len(gas) == 1
        t = gas[0].t_k
        i_t = int(np.argmin(res["profile_rs_m"]))
        g = res["gamma"]
        assert abs(t[0] - res["tc_k"]) / res["tc_k"] < 0.02, (t[0], res["tc_k"])
        assert abs(t[i_t] - res["tc_k"] * 2.0 / (g + 1.0)) < 1e-6 * res["tc_k"]
        assert np.all(np.diff(t[i_t:]) <= 1e-9), "gas must cool monotonically past the throat"
        assert np.all(t <= res["tc_k"] + 1e-9)
        for prop in ("fuel", "ox"):
            orders = [s.order for s in net if s.propellant == prop]
            assert orders == sorted(orders) and len(set(orders)) == len(orders)
        lo, hi = temperature_range(net)
        assert 0 < lo < hi <= res["tc_k"] + 1e-9

    # 1) flat-mode regen: heat-weighted approximation, ends exactly at inlet + dT
    r1 = EngineDesign(**base).compute()
    n1 = build_flow_network(r1)
    _check_common(r1, n1)
    j1 = [s for s in n1 if s.kind == "jacket_pass"]
    assert len(j1) == 1 and j1[0].approximate and j1[0].anchor["pass"] == "single"
    assert abs(j1[0].t_k[0] - r1["coolant_inlet_t_k"]) < 1e-9
    assert abs(j1[0].t_k[-1] - (r1["coolant_inlet_t_k"] + r1["cooling"]["coolant_delta_t_k"])) < 1e-6
    assert np.all(np.diff(j1[0].t_k) >= -1e-9) and np.all(np.diff(j1[0].x_m) < 0)  # aft -> fwd
    ox = [s for s in n1 if s.propellant == "ox"]
    assert ox and all(abs(s.t_k[0] - 90.0) < 1e-9 for s in ox)
    print(f"flat regen: {len(n1)} segments, coolant {j1[0].t_k[0]:.0f}->{j1[0].t_k[-1]:.0f} K "
          f"(approx), gas {n1[-1].t_k.min():.0f}-{n1[-1].t_k.max():.0f} K: OK")

    # 2) channels-mode regen: the march's own per-station profile, exact
    r2 = EngineDesign(**base, regen_channel_model="channels").compute()
    n2 = build_flow_network(r2)
    _check_common(r2, n2)
    j2 = [s for s in n2 if s.kind == "jacket_pass"]
    assert len(j2) == 1 and not j2[0].approximate
    assert np.all(np.diff(j2[0].t_k) >= -1e-6), "coolant must heat up along its flow"
    assert abs(j2[0].t_k[-1] - r2["cooling"]["coolant_exit_t_k"]) < 1.0, \
        (j2[0].t_k[-1], r2["cooling"]["coolant_exit_t_k"])
    fuel_ring = [s for s in n2 if s.kind == "manifold_ring" and s.anchor["host"] == "fuel"]
    assert fuel_ring and abs(fuel_ring[0].t_k[0] - j2[0].t_k[-1]) < 1e-9
    print(f"channels regen: coolant {j2[0].t_k[0]:.0f}->{j2[0].t_k[-1]:.0f} K (exact): OK")

    # 3) J-2 two-pass LOX/LH2: a down leg (inlet -> turnaround) then the up pass
    r3 = EngineDesign(**{**base, "propellant_pair": "LOX/LH2", "mixture_ratio": 5.5,
                         "expansion_ratio": 27.5}, regen_channel_model="channels",
                      cooling_flow_topology="j2_mid_nozzle_inlet", regen_nozzle_end_eps=20.0,
                      jacket_inlet_eps=10.0).compute()
    n3 = build_flow_network(r3)
    _check_common(r3, n3)
    j3 = [s for s in n3 if s.kind == "jacket_pass"]
    assert [s.anchor["pass"] for s in j3] == ["down", "up"], [s.anchor["pass"] for s in j3]
    assert np.all(np.diff(j3[0].x_m) > 0) and np.all(np.diff(j3[1].x_m) < 0)
    assert abs(j3[0].t_k[-1] - r3["cooling"]["coolant_turnaround_t_k"]) < 1e-9
    print(f"J-2 two-pass: down {j3[0].t_k[0]:.0f}->{j3[0].t_k[-1]:.0f} K, "
          f"up {j3[1].t_k[0]:.0f}->{j3[1].t_k[-1]:.0f} K: OK")

    # 4) pressure-fed ablative monopropellant: no jacket, no ox
    r4 = EngineDesign(propellant_pair="Hydrazine", mixture_ratio=1.0, chamber_pressure_pa=1.0e6,
                      expansion_ratio=50, nozzle_type="bell", cycle=cycles.PRESSURE_FED,
                      target_vac_thrust_n=400, material_key="niobium_c103",
                      bell_material_key="niobium_c103").compute()
    n4 = build_flow_network(r4)
    assert not any(s.kind == "jacket_pass" for s in n4)
    assert not any(s.propellant == "ox" for s in n4)
    print("monoprop / no regen: OK")
    print("ALL FLOW-NETWORK CHECKS OK")


if __name__ == "__main__":
    self_test()
