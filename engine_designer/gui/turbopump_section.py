"""
"Turbopump Section" tab: the whole turbopump assembly cut through its shaft axis and
drawn as an engineering cross-section (hatched casing walls, hatched rotors, bearings,
seals, leader-line labels) - the style of the classic Rocketdyne F-1 Mk-10 section.

Geometry is physics/turbopump_layout.py's (the ONE casing source - the Turbopump 3D tab
meshes the same layout): each component's revolved casing outline, its volute / collector
/ exhaust scroll cut at u = 0 (top half, +y) and u = pi (bottom half, -y) - so a volute
shows a small section on top and its full discharge section underneath, like the real
drawing - the turbine inlet torus and GG/preburner inlet stub, and the bearing/seal
housings between components. The internals come from the pump meanline (inducer,
impeller hub/shroud per stage, axial rotor/stator rows) and turbopump_sizing (torsion-
sized shaft, bearing bore via turbopump_layout.shaft_bearing, turbine staging/pitchline/
disk OD).

Drawing-only placeholders (Tier 3, ASSUMPTIONS.md - each upgraded automatically when the
roadmap sizes it, since this module reads the layout/sizing): a flat casing wall
thickness (roadmap E3 sizes real walls), bearing positions / proportions and labyrinth
seals (Round 3, SP-8048), turbine disks and blade rows from staging + pitchline only
(Round 3 turbine meanline). A geared set's pumps are drawn inline on one axis (no
gearbox model).

`section_geometry(result)` is pure numpy (self-tested); `draw_turbopump_section(fig,
result)` renders it with matplotlib (Agg-safe, so headless-testable); gui/app.py only
embeds the Figure. Self-test: `python3 -m engine_designer.gui.turbopump_section`.
"""
import math

import numpy as np

from ..physics import turbopump_layout as tl

# --- drawing-only proportions (Tier 3: shape the picture, carry no mass or physics) -----
WALL_OD_FRACTION = 0.025        # casing wall thickness / that component's casing OD (E3 later)
WALL_MIN_M = 0.0015             # ... floored here (a Rutherford-size pump)
SEGMENT_SPLIT_WALLS = 1.0       # casing outline split into pieces <= this x wall before the
                                # scroll-mouth test (a long housing line can open under a scroll)
SHAFT_SLEEVE_MULT = 1.08        # rotor hubs never drawn inside this x the shaft radius
DISK_CLEARANCE_FRACTION = 0.5   # impeller back disk / shroud thickness, x the casing clearance
EYE_RING_GAP_CLEARANCE = 0.25  # eye (wear) ring running gap over the shroud, x the casing clearance
BLADE_LE_FRACTION = 0.15       # impeller blade leading edge, fraction along the meridional passage
INDUCER_HUB_TIP = 0.3           # inducer hub / tip radius at its leading edge (Detail tab's)
INDUCER_SWEEP = 0.3             # hub leading edge behind the tip's, x inducer length
NOSE_LEN_HUB = 0.8              # inducer nose length / hub radius (capped by the inlet lead)
BEARING_WIDTH_SECTION = 1.0     # bearing width / its radial section
BEARING_RACE_SECTION = 0.28     # race thickness / radial section
BEARING_BALL_SECTION = 0.32     # ball radius / radial section
SEAL_PLATE_WALLS = 1.0          # seal plate behind each impeller, x wall
SEAL_LEN_SPAN = 0.4             # labyrinth seal length / bearing-housing span
SEAL_HEIGHT_SHAFT = 0.25        # labyrinth seal radial height / shaft radius
SEAL_TEETH = 6
TURBINE_CHORD_HEIGHT = 0.35     # blade-row axial chord / blade height
TURBINE_GAP_CHORD = 0.25        # inter-row gap / chord
DISK_RIM_CHORD = 1.2            # disk rim width / chord
DISK_WEB_CHORD = 0.35           # disk web width / chord
DISK_HUB_CHORD = 1.0            # disk hub width / chord
DISK_RIM_DEPTH_HEIGHT = 0.25    # rim radial depth / blade height
DISK_HUB_SHAFT = 1.6            # disk hub OD / shaft OD
MOTOR_STATOR_INNER = 0.62       # motor stator bore / casing radius
MOTOR_ROTOR_OUTER = 0.58        # motor rotor OD / casing OD
MOTOR_CORE_SPAN = 0.7           # stator/rotor core length / motor length
# turbine blade rows by staging: N = nozzle, R = rotor, S = turning (stator) row
TURBINE_ROWS = {"single_impulse": "NR", "velocity_compounded_2row": "NRSR",
                "pressure_compounded_2stage": "NRNR", "reaction": "NR"}
LEG = {"fuel_pump": "Fuel", "ox_pump": "Oxidizer"}
U_TOP, U_BOTTOM = 0.0, math.pi           # cut angles: +y half and -y half (scroll convention)

INK = "#1a1a1a"
STYLES = {   # role -> (z-order, patch kwargs)
    "casing": (1, dict(facecolor="white", edgecolor=INK, hatch="////", lw=0.8)),
    "seal": (1, dict(facecolor="white", edgecolor=INK, hatch="////", lw=0.8)),
    "fluid": (2, dict(facecolor="white", edgecolor=INK, lw=0.8)),
    "opening": (2, dict(facecolor="white", edgecolor="none", lw=0.0)),
    "shaft": (3, dict(facecolor="white", edgecolor=INK, hatch="\\\\\\\\", lw=0.8)),
    "rotor": (4, dict(facecolor="white", edgecolor=INK, hatch="\\\\\\\\", lw=0.8)),
    "blade": (5, dict(facecolor="#ececec", edgecolor=INK, lw=0.8)),
    "stator": (5, dict(facecolor="#f6f6f6", edgecolor=INK, hatch="//", lw=0.8)),
    "motor_core": (4, dict(facecolor="white", edgecolor=INK, hatch="xxx", lw=0.8)),
    "winding": (5, dict(facecolor="#6b6b6b", edgecolor=INK, lw=0.6)),
    "race": (6, dict(facecolor="#d4d4d4", edgecolor=INK, lw=0.7)),
    "ball": (7, dict(facecolor=INK, edgecolor=INK, lw=0.5)),
}


# --- small polygon helpers (local frame: x along the shaft, r >= 0) -----------------------
def _rect(x0, x1, r0, r1):
    return np.array([[x0, r0], [x1, r0], [x1, r1], [x0, r1]], dtype=float)


def _circle(xc, rc, rad, n=56):
    t = np.linspace(0.0, 2.0 * math.pi, n, endpoint=False)
    return np.column_stack([xc + rad * np.cos(t), rc + rad * np.sin(t)])


def _dedupe(pts):
    pts = np.asarray(pts, dtype=float)
    keep = [pts[0]]
    for p in pts[1:]:
        if np.hypot(*(p - keep[-1])) > 1e-9:
            keep.append(p)
    return np.array(keep)


def _offset(pts, t):
    """Open polyline offset by t along its LEFT normal (mitred, miter capped)."""
    seg = np.diff(pts, axis=0)
    nrm = np.column_stack([-seg[:, 1], seg[:, 0]]) / np.hypot(seg[:, 0], seg[:, 1])[:, None]
    off = np.empty_like(pts)
    off[0] = pts[0] + t * nrm[0]
    off[-1] = pts[-1] + t * nrm[-1]
    for i in range(1, len(pts) - 1):
        m = nrm[i - 1] + nrm[i]
        ml = np.hypot(*m)
        m = nrm[i] if ml < 1e-9 else m / ml
        off[i] = pts[i] + t * m / max(float(np.dot(m, nrm[i])), 0.35)
    return off


def _band(pts, t):
    """Closed polygon: the polyline thickened by t on its left (the casing's outside)."""
    pts = _dedupe(pts)
    if len(pts) < 2:
        return None
    return np.vstack([pts, _offset(pts, t)[::-1]])


def _split(pts, max_len):
    out = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        k = max(1, int(math.ceil(np.hypot(*(b - a)) / max_len)))
        for j in range(1, k + 1):
            out.append(a + (b - a) * j / k)
    return np.array(out)


def casing_bands(xs, rs, t, holes=(), r_clip_start=0.0, r_clip_end=0.0):
    """A revolved casing outline -> hatched wall bands of thickness t, outside = the
    polyline's left. Axis-touching vertices are lifted to r_clip_start/_end (the shaft
    passes through that end wall); pieces whose midpoint lies inside a hole circle
    ((xc, rc, radius)) - a scroll's mouth - are left open."""
    xs = np.asarray(xs, dtype=float)
    rs = np.asarray(rs, dtype=float).copy()
    x_mid = 0.5 * (xs.min() + xs.max())
    for i in range(len(rs)):
        lo = r_clip_start if xs[i] < x_mid else r_clip_end
        if rs[i] < lo:
            rs[i] = lo
    pts = _split(_dedupe(np.column_stack([xs, rs])), SEGMENT_SPLIT_WALLS * t)
    runs, cur = [], [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        mid = 0.5 * (a + b)
        if any(math.hypot(mid[0] - hx, mid[1] - hr) < hrad for hx, hr, hrad in holes):
            if len(cur) > 1:
                runs.append(cur)
            cur = [b]
        else:
            cur.append(b)
    if len(cur) > 1:
        runs.append(cur)
    return [b for b in (_band(np.array(r), t) for r in runs) if b is not None]


def scroll_cut(scroll, u_target):
    """(x, center_r, tube_r) of a layout scroll cut by the half-plane at angle u_target
    (u = 0 is +y). Ties (a full 360-degree wrap meets itself at the discharge) take the
    LATER station - the discharge end, not the tongue."""
    tube = np.asarray(scroll["tube_r"], dtype=float)
    ctr = np.asarray(scroll["center_r"], dtype=float)
    u = scroll["u_start"] + scroll["span"] * np.linspace(0.0, 1.0, len(tube))
    d = np.abs((u - u_target + math.pi) % (2.0 * math.pi) - math.pi)
    k = len(d) - 1 - int(np.argmin(d[::-1]))
    return float(scroll["x"]), float(ctr[k]), float(tube[k])


def _wall(comp):
    return max(WALL_OD_FRACTION * comp["od_m"], WALL_MIN_M)


class _Parts:
    """Collects (role, local polygon) + leader labels for one component half."""

    def __init__(self):
        self.parts, self.labels = [], []

    def add(self, role, poly):
        if poly is not None and len(poly) >= 3:
            self.parts.append((role, np.asarray(poly, dtype=float)))

    def ring(self, xc, rc, rad, t):
        self.add("casing", _circle(xc, rc, rad + t))
        self.add("fluid", _circle(xc, rc, rad))

    def label(self, text, x, r):
        self.labels.append((text, float(x), float(r)))


# --- shared internals -----------------------------------------------------------------------
def _bearing_pack(P, x0, x1, r_shaft, brg, r_housing, t):
    """Seal plate at x0 + rolling-element bearing(s) in [x0, x1]: journal sleeve, races,
    balls, and a carrier up to the housing. Returns the bearing count drawn."""
    r_b, r_o = 0.5 * brg["bore_m"], 0.5 * brg["od_m"]
    if r_b <= r_shaft or r_o <= r_b or x1 <= x0:
        return 0
    plate = SEAL_PLATE_WALLS * t
    _seal(P, x0, x0 + plate, r_shaft, r_housing)
    xa, xb = x0 + plate, x1
    span = xb - xa
    sect = r_o - r_b
    w = BEARING_WIDTH_SECTION * sect
    n = 2 if span >= 2.3 * w else 1
    w = min(w, 0.8 * span / n)
    race = BEARING_RACE_SECTION * sect
    P.add("rotor", _rect(xa, xb, r_shaft, r_b))                      # journal sleeve
    if r_housing > r_o:
        P.add("casing", _rect(xa, xb, r_o, r_housing))               # bearing carrier
    for j in range(n):
        xc = xa + span * (j + 0.5) / n
        P.add("race", _rect(xc - 0.5 * w, xc + 0.5 * w, r_o - race, r_o))
        P.add("race", _rect(xc - 0.5 * w, xc + 0.5 * w, r_b, r_b + race))
        P.add("ball", _circle(xc, 0.5 * (r_b + r_o), BEARING_BALL_SECTION * sect, 24))
    P.label("Bearings", xa + 0.5 * span, r_o)
    return n


def _seal(P, x0, x1, r_shaft, r_top):
    """A labyrinth seal: a hatched plate from r_top down to just above the shaft, with
    teeth along its bore."""
    gap = 0.04 * r_shaft
    r_in = r_shaft + gap
    if r_top <= r_in or x1 <= x0:
        return
    teeth = []
    for k in range(SEAL_TEETH):
        xa = x0 + (x1 - x0) * k / SEAL_TEETH
        xb = x0 + (x1 - x0) * (k + 1) / SEAL_TEETH
        teeth += [(xa, r_in + 2.0 * gap), (0.5 * (xa + xb), r_in), (xb, r_in + 2.0 * gap)]
    P.add("seal", np.array([(x0, r_top)] + teeth + [(x1, r_top)]))


def _scroll_holes(comp, u):
    out = []
    for s in comp["scrolls"]:
        x, ctr, tube = scroll_cut(s, u)
        out.append((x, ctr, tube + 0.5 * _wall(comp)))
    return out


# --- component halves (local frame) ------------------------------------------------------------
def _centrifugal(comp, pump, brg, r_s, u, notes):
    ml, st = pump["meanline"], comp["stations"]
    stg, mer = ml["stage"], ml["meridional"]
    d2, b2, n = stg["d2_m"], stg["b2_m"], ml["n_stages"]
    r2 = 0.5 * d2
    c = st["clearance"]
    t = _wall(comp)
    leg = LEG[comp["key"]]
    P = _Parts()
    xs, rs = comp["revolves"][0]
    for b in casing_bands(xs, rs, t, _scroll_holes(comp, u), r_clip_end=r_s * 1.04):
        P.add("casing", b)
    # inlet flange
    r_in = st["r_in"]
    P.add("casing", _rect(0.0, tl.FLANGE_WIDTH_BORE_MULT * r_in, r_in + t,
                          r_in * (1.0 + tl.FLANGE_LIP_BORE_MULT) + t))
    # volute at this cut + the vaneless gap from the impeller tip into it
    x_v, ctr, tube = scroll_cut(comp["scrolls"][0], u)
    P.ring(x_v, ctr, tube, t)
    P.add("opening", _rect(st["x_tip"], st["x_tip"] + b2, r2, ctr))
    if u == U_BOTTOM:
        P.label(f"{leg} volute", x_v, ctr + tube + t)
    # impeller stage(s)
    t_disk = DISK_CLEARANCE_FRACTION * c
    sh0, hb0 = np.array(mer["shroud"], dtype=float), np.array(mer["hub"], dtype=float)
    r_sleeve = SHAFT_SLEEVE_MULT * r_s
    if 0.5 * stg["d_hub_m"] < r_sleeve and u == U_TOP:
        notes.append(f"{leg} pump: meanline hub {stg['d_hub_m'] * 1e3:.0f} mm is inside the "
                     f"torsion-sized shaft ({2.0 * r_s * 1e3:.0f} mm) - impeller drawn on a sleeve")
    for i in range(n):
        dz = st["lead"] + i * st["pitch"]
        S = np.column_stack([sh0[:, 0] + dz, sh0[:, 1]])
        H = np.column_stack([hb0[:, 0] + dz, np.maximum(hb0[:, 1], r_sleeve)])
        x_bf = H[-1, 0] + t_disk
        P.add("rotor", np.vstack([H, [[x_bf, r2], [x_bf, r_s], [H[0, 0], r_s]]]))
        P.add("rotor", _band(S, t_disk))
        k0 = int(BLADE_LE_FRACTION * (len(S) - 1))
        P.add("blade", np.vstack([S[k0:], H[k0:][::-1]]))
        if i == 0:   # eye ring: the inlet neck (inducer-tip bore) closed down onto the shroud
            ring = _offset(S, t_disk + EYE_RING_GAP_CLEARANCE * c)
            run = []
            for p in ring:
                if p[1] >= st["r_in"]:
                    break
                run.append(p)
            if len(run) >= 2:
                P.add("casing", np.vstack([[[run[0][0], st["r_in"]]], run, [[run[-1][0], st["r_in"]]]]))
        if i == n - 1 and u == U_TOP:
            P.label(f"{leg} pump impeller", 0.5 * (S[-2, 0] + H[-2, 0]), 0.5 * (S[-2, 1] + H[-2, 1]))
        if i < n - 1:   # crossover diaphragm ahead of the next eye (return channel round it)
            x_next = st["lead"] + (i + 1) * st["pitch"]
            P.add("casing", _rect(x_bf + 0.5 * c, x_next - 0.5 * c, r_s * 1.25, r2 + 0.5 * c))
    # inducer + nose
    x_i0, x_i1 = st["x_inducer"], st["lead"]
    li = x_i1 - x_i0
    r_t = 0.5 * st["inducer_tip_dia"]
    rh0 = max(INDUCER_HUB_TIP * r_t, r_sleeve)
    rh1 = max(float(hb0[0, 1]), r_sleeve)
    ln = min(NOSE_LEN_HUB * rh0, 0.9 * x_i0)
    a = np.linspace(0.0, 0.5 * math.pi, 12)
    nose = np.column_stack([x_i0 - ln * np.cos(a), rh0 * np.sin(a)])
    P.add("rotor", np.vstack([nose, [[x_i1, rh1], [x_i1, 0.0]]]))

    def r_hub(x):
        return rh0 + (rh1 - rh0) * (x - x_i0) / li

    xle_h, xte = x_i0 + INDUCER_SWEEP * li, x_i1 - 0.05 * li
    P.add("blade", np.array([[xle_h, r_hub(xle_h)], [x_i0 + 0.05 * li, 0.985 * r_t],
                             [xte, 0.985 * r_t], [xte, r_hub(xte)]]))
    if u == U_TOP:
        P.label(f"{leg} inducer", x_i0 + 0.4 * li, 0.85 * r_t)
    nb = _bearing_pack(P, st["x_back"], st["x_end"], r_s, brg, st["r_bh"], t)
    if nb and u != U_BOTTOM:
        P.labels.pop()
    return P, (x_i0 - ln, st["x_end"])


def _axial(comp, pump, brg, r_s, u, notes):
    ml, st = pump["meanline"], comp["stations"]
    dt, chord, n = ml["d_tip_m"], ml["chord_m"], ml["n_stages"]
    rt, rh = 0.5 * dt, max(0.5 * ml["d_hub_m"], SHAFT_SLEEVE_MULT * r_s)
    gap = st["gap"]
    t = _wall(comp)
    leg = LEG[comp["key"]]
    P = _Parts()
    xs, rs = comp["revolves"][0]
    for b in casing_bands(xs, rs, t, _scroll_holes(comp, u), r_clip_end=r_s * 1.04):
        P.add("casing", b)
    r_b = st["r_barrel"]
    P.add("casing", _rect(0.0, tl.FLANGE_WIDTH_BORE_MULT * r_b, r_b + t,
                          r_b * (1.0 + tl.FLANGE_LIP_BORE_MULT) + t))
    x_c, ctr, tube = scroll_cut(comp["scrolls"][0], u)
    P.ring(x_c, ctr, tube, t)
    P.add("opening", _rect(x_c - 0.6 * tube, x_c + 0.6 * tube, rt, ctr))
    if u == U_BOTTOM:
        P.label(f"{leg} collector", x_c, ctr + tube + t)
    x = st["x_inducer"]
    li = tl.INDUCER_LEN_TIP_MULT * dt
    rh0 = max(INDUCER_HUB_TIP * rt, SHAFT_SLEEVE_MULT * r_s)
    P.add("blade", np.array([[x + INDUCER_SWEEP * li, rh0 + (rh - rh0) * INDUCER_SWEEP],
                             [x + 0.05 * li, 0.985 * rt], [x + 0.95 * li, 0.985 * rt],
                             [x + 0.95 * li, rh0 + (rh - rh0) * 0.95]]))
    if u == U_TOP:
        P.label(f"{leg} inducer", x + 0.4 * li, 0.85 * rt)
    x_drum0 = x
    x += li + gap
    rows = [("stator", tl.AXIAL_IGV_CHORD)] + [("blade", tl.AXIAL_ROW_CHORD),
                                               ("stator", tl.AXIAL_ROW_CHORD)] * n
    for k, (role, frac) in enumerate(rows):
        w = frac * chord
        P.add(role, _rect(x, x + w, rh, 0.985 * rt))
        if k == 1 and u == U_TOP:
            P.label(f"{leg} pump rotor rows", x + 0.5 * w, 0.5 * (rh + rt))
        x += w + gap
    ln = min(NOSE_LEN_HUB * rh0, 0.9 * st["x_inducer"])
    a = np.linspace(0.0, 0.5 * math.pi, 12)
    nose = np.column_stack([x_drum0 - ln * np.cos(a), rh0 * np.sin(a)])
    P.add("rotor", np.vstack([nose, [[x_drum0 + li, rh], [x, rh], [x, 0.0]]]))
    nb = _bearing_pack(P, st["x_back"], st["x_end"], r_s, brg, st["r_bh"], t)
    if nb and u != U_BOTTOM:
        P.labels.pop()
    return P, (x_drum0 - ln, st["x_end"])


def _envelope(comp, r_s, u, notes):
    t = _wall(comp)
    P = _Parts()
    xs, rs = comp["revolves"][0]
    for b in casing_bands(xs, rs, t, (), r_s * 1.04, r_s * 1.04):
        P.add("casing", b)
    length, r = comp["length_m"], 0.5 * comp["od_m"]
    P.add("rotor", _rect(0.3 * length, 0.5 * length, r_s, 0.75 * r))
    if u == U_TOP:
        P.label(f"{LEG[comp['key']]} pump (envelope - no meanline)", 0.4 * length, 0.6 * r)
        notes.append(f"{LEG[comp['key']]} pump: pump model 'correlation' - no meanline geometry, "
                     "drawn as its sizing envelope")
    return P, (0.0, length)


def _turbine(comp, tb, r_s, u, open_end, notes):
    st = comp["stations"]
    t = _wall(comp)
    P = _Parts()
    xs, rs = comp["revolves"][0]
    for b in casing_bands(xs, rs, t, _scroll_holes(comp, u), r_s * 1.04,
                          r_s * 1.04 if open_end else 0.0):
        P.add("casing", b)
    x_in, ctr_in, tube_in = st["x_inlet"], st["r_inlet_ctr"], st["r_inlet_tube"]
    P.ring(x_in, ctr_in, tube_in, t)
    if u == U_TOP:   # GG / preburner inlet stub (+y) with its flange
        a, b_end, stub_r, _ = comp["cones"][0]
        r0, r1 = ctr_in + 0.5 * tube_in, float(b_end[1])
        P.add("casing", _rect(x_in - stub_r - t, x_in - stub_r, r0, r1))
        P.add("casing", _rect(x_in + stub_r, x_in + stub_r + t, r0, r1))
        P.add("opening", _rect(x_in - stub_r, x_in + stub_r, ctr_in, r1))
        lip = stub_r * (1.0 + tl.FLANGE_LIP_BORE_MULT) + t
        P.add("casing", _rect(x_in - lip, x_in - stub_r, r1 - tl.FLANGE_WIDTH_BORE_MULT * stub_r, r1))
        P.add("casing", _rect(x_in + stub_r, x_in + lip, r1 - tl.FLANGE_WIDTH_BORE_MULT * stub_r, r1))
        P.label("Turbine inlet manifold", x_in, ctr_in + tube_in)
    x_ex, ctr_ex, tube_ex = scroll_cut(comp["scrolls"][0], u)
    P.ring(x_ex, ctr_ex, tube_ex, t)
    if u == U_BOTTOM:
        P.label("Turbine outlet (to injector)" if st["closed"] else "Exhaust scroll",
                x_ex, ctr_ex + tube_ex + t)
    # blade rows from staging + pitchline (no turbine meanline until Round 3)
    rows = TURBINE_ROWS.get(tb["staging"], "NR")
    r_tip = min(0.5 * tb["disk_od_m"], st["r_housing"] - 0.25 * t)
    r_root = max(tb["d_mean_m"] - r_tip, DISK_HUB_SHAFT * r_s * 1.2)
    h = r_tip - r_root
    xa = x_in + 0.6 * tube_in
    xb = x_ex - 0.6 * st["r_exhaust_end"]
    chord = TURBINE_CHORD_HEIGHT * h
    gap = TURBINE_GAP_CHORD * chord
    total = len(rows) * chord + (len(rows) - 1) * gap
    if total > xb - xa > 0.0:
        chord *= (xb - xa) / total
        gap *= (xb - xa) / total
    # inlet duct from the torus to the first nozzle row
    A = (x_in - 0.45 * tube_in, ctr_in - 0.6 * tube_in)
    B = (x_in + 0.45 * tube_in, ctr_in - 0.6 * tube_in)
    C, D = (xa, r_tip), (xa, r_root)
    P.add("casing", _band(np.array([D, A]), t))
    P.add("casing", _band(np.array([B, C]), t))
    P.add("opening", np.array([A, B, C, D]))
    x = xa
    hub_r = DISK_HUB_SHAFT * r_s
    rim_r = r_root - DISK_RIM_DEPTH_HEIGHT * h
    n_rotor = 0
    for kind in rows:
        xc = x + 0.5 * chord
        if kind == "R":
            n_rotor += 1
            rim, web, hub = (0.5 * DISK_RIM_CHORD * chord, 0.5 * DISK_WEB_CHORD * chord,
                             0.5 * DISK_HUB_CHORD * chord)
            P.add("rotor", np.array([
                [xc - hub, r_s], [xc - hub, hub_r], [xc - web, hub_r + 0.3 * (rim_r - hub_r)],
                [xc - web, rim_r], [xc - rim, rim_r], [xc - rim, r_root],
                [xc + rim, r_root], [xc + rim, rim_r], [xc + web, rim_r],
                [xc + web, hub_r + 0.3 * (rim_r - hub_r)], [xc + hub, hub_r], [xc + hub, r_s]]))
            P.add("blade", _rect(x, x + chord, r_root, r_tip))
        else:
            P.add("stator", _rect(x, x + chord, r_root, r_tip))
            if kind == "S":   # turning row hung from the housing
                P.add("casing", _rect(x, x + chord, r_tip, st["r_housing"]))
        x += chord + gap
    if u == U_TOP:
        P.label("Turbine rotors" if n_rotor > 1 else "Turbine rotor",
                x - gap - 0.5 * chord, 0.5 * (r_root + r_tip))
        P.label("Nozzles", xa + 0.5 * chord, r_root + 0.3 * h)
    x_last = x - gap - 0.5 * chord + 0.5 * DISK_HUB_CHORD * chord
    return P, (0.0, comp["length_m"] if open_end else x_last)


def _motor(comp, r_s, u, notes):
    t = _wall(comp)
    P = _Parts()
    xs, rs = comp["revolves"][0]
    for b in casing_bands(xs, rs, t, (), r_s * 1.04, r_s * 1.04):
        P.add("casing", b)
    length, r = comp["length_m"], 0.5 * comp["od_m"]
    x0, x1 = 0.5 * (1.0 - MOTOR_CORE_SPAN) * length, 0.5 * (1.0 + MOTOR_CORE_SPAN) * length
    P.add("motor_core", _rect(x0, x1, MOTOR_STATOR_INNER * r, r))
    P.add("rotor", _rect(x0, x1, r_s, MOTOR_ROTOR_OUTER * r))
    ew = 0.06 * length
    for xa in (x0 - ew, x1):
        P.add("winding", _rect(xa, xa + ew, MOTOR_STATOR_INNER * r, 0.9 * r))
    if u == U_TOP:
        P.label("Motor stator", 0.5 * (x0 + x1), 0.8 * r)
        P.label("Motor rotor", 0.3 * (x0 + x1), 0.5 * MOTOR_ROTOR_OUTER * r)
    return P, (0.0, length)


# --- assembly ------------------------------------------------------------------------------------
def _to_global(poly, pl, half):
    return np.column_stack([pl["x0"] + pl["sx"] * poly[:, 0], half * poly[:, 1]])


def section_geometry(result):
    """
    {"units": [{"title", "parts": [(role, poly(N,2) in metres - X along the shaft, Y the
    signed cut-plane radius)], "labels": [(text, (X, Y), side)], "x_range", "y_extent"}],
    "notes": [str], "summary": [str]} or None without a turbopump. Parts of the top half
    (Y > 0) are cut at u = 0 (+y), the bottom half at u = pi (-y, the discharge side).
    """
    from .turbopump_scene import layout_for_result
    layout = layout_for_result(result)
    if layout is None:
        return None
    sizing = result["turbopump_sizing"]
    comps, places = layout["components"], layout["placements"]
    dual = len(layout["units"]) > 1
    notes, summary, units = [], [], []
    brgs = {k: tl.shaft_bearing(sizing, k) for k in tl.PUMP_KEYS if sizing.get(k)}
    for key, b in brgs.items():
        summary.append(f"{LEG[key]} pump: {b['rpm']:.0f} rpm, shaft {b['shaft_dia_m'] * 1e3:.0f} mm "
                       f"(torsion), bearing bore {b['bore_m'] * 1e3:.0f} mm (DN "
                       f"{b['rpm'] * b['bore_m'] * 1e3 / 1e6:.2f} M) - {comps[key]['summary']}")
    for key in tl.TURBINE_KEYS:
        if key in comps:
            summary.append(f"{'Ox turbine' if key == 'ox_turbine' else 'Turbine'}: "
                           f"{comps[key]['summary']}")
    if sizing.get("geared"):
        notes.append("geared set: pumps drawn inline on one axis - the gearbox is not modelled")
    for u_idx, unit in enumerate(layout["units"]):
        r_unit = max([0.5 * brgs[k]["shaft_dia_m"] for k in unit if k in brgs] or [0.01])
        parts, labels, spans = [], [], {}
        for i, key in enumerate(unit):
            comp, pl = comps[key], places[key]
            open_end = i < len(unit) - 1
            r_s = 0.5 * brgs[key]["shaft_dia_m"] if key in brgs else r_unit
            for half, u in ((1.0, U_TOP), (-1.0, U_BOTTOM)):
                if key in tl.PUMP_KEYS:
                    pump = sizing[key]
                    ml = pump.get("meanline")
                    if ml is None:
                        P, span = _envelope(comp, r_s, u, notes)
                    elif ml["type"] == "axial":
                        P, span = _axial(comp, pump, brgs[key], r_s, u, notes)
                    else:
                        P, span = _centrifugal(comp, pump, brgs[key], r_s, u, notes)
                elif key in tl.TURBINE_KEYS:
                    P, span = _turbine(comp, sizing[key], r_s, u, open_end, notes)
                else:
                    P, span = _motor(comp, r_s, u, notes)
                parts += [(role, _to_global(p, pl, half)) for role, p in P.parts]
                labels += [(text, (pl["x0"] + pl["sx"] * x, half * r), "top" if half > 0 else "bottom")
                           for text, x, r in P.labels]
            # shaft through this component's rotor span (stepped per component)
            xa, xb = sorted(pl["x0"] + pl["sx"] * np.array(span))
            spans[key] = (xa, xb, r_s)
        for k, link in enumerate(l for l in layout["links"] if abs(l["dz"] - _unit_dz(layout, u_idx)) < 1e-12):
            a_key, b_key = unit[k], unit[k + 1]
            r_s = max(spans[a_key][2], spans[b_key][2])
            t = min(_wall(comps[a_key]), _wall(comps[b_key]))
            for half in (1.0, -1.0):
                band = _band(np.array([[link["x0"], link["r0"]], [link["x1"], link["r1"]]]), t)
                parts.append(("casing", np.column_stack([band[:, 0], half * band[:, 1]])))
                xm = 0.5 * (link["x0"] + link["x1"])
                ls = SEAL_LEN_SPAN * (link["x1"] - link["x0"])
                r_wall = 0.5 * (link["r0"] + link["r1"])
                P = _Parts()
                _seal(P, xm - 0.5 * ls, xm + 0.5 * ls, r_s, r_s * (1.04 + SEAL_HEIGHT_SHAFT))
                P.add("seal", _rect(xm - 0.5 * t, xm + 0.5 * t, r_s * (1.04 + SEAL_HEIGHT_SHAFT), r_wall))
                parts += [(role, np.column_stack([p[:, 0], half * p[:, 1]])) for role, p in P.parts]
                if half > 0 and k == 0:
                    labels.append(("Shaft seal", (xm, r_s * (1.04 + SEAL_HEIGHT_SHAFT)), "top"))
            spans[f"link{k}"] = (link["x0"], link["x1"], r_s)
        for xa, xb, r_s in spans.values():
            parts.append(("shaft", _rect(xa, xb, -r_s, r_s)))
        labels.append(("Shaft", (min(s[0] for s in spans.values())
                                 + 0.35 * (max(s[1] for s in spans.values())
                                           - min(s[0] for s in spans.values())), -0.5 * r_unit),
                       "bottom"))
        allp = np.vstack([p for _, p in parts])
        if dual:
            title = ("Fuel turbopump" if "fuel_pump" in unit else "Oxidizer turbopump") + " (dual shaft)"
        elif "motor" in unit:
            title = "Electric pump-fed: motor-driven pumps"
        else:
            title = "Turbopump - " + ("geared set (drawn inline)" if sizing.get("geared")
                                      else "single shaft")
        units.append({"title": title, "parts": parts, "labels": labels,
                      "x_range": (float(allp[:, 0].min()), float(allp[:, 0].max())),
                      "y_top": float(allp[:, 1].max()), "y_bottom": float(-allp[:, 1].min()),
                      "y_extent": float(np.abs(allp[:, 1]).max())})
    if any(k in comps for k in tl.TURBINE_KEYS):
        notes.append("turbine disks and blade rows from staging + pitchline + disk OD only "
                     "(no turbine meanline until Round 3)")
    notes.append(f"drawing-only placeholders: flat wall {WALL_OD_FRACTION:g} x casing OD (E3 sizes "
                 "real walls), bearing positions/OD and labyrinth seals (Round 3) - the shaft and "
                 "bearing bore ARE the torsion sizing")
    return {"units": units, "notes": list(dict.fromkeys(notes)), "summary": summary}


def _unit_dz(layout, u_idx):
    units = layout["units"]
    return (u_idx - (len(units) - 1) / 2.0) * layout["unit_gap_m"]


# --- matplotlib rendering --------------------------------------------------------------------------
def _nice_length(span):
    raw = span / 6.0
    p = 10.0 ** math.floor(math.log10(raw))
    for m in (1.0, 2.0, 5.0, 10.0):
        if m * p >= raw:
            return m * p
    return 10.0 * p


def _fit_equal(ax, x0, x1, y0, y1):
    """Equal-aspect limits that FILL the axes box: the tighter of the two ranges is
    widened about its centre (matplotlib's 'datalim' ignores fixed limits instead)."""
    fig_w, fig_h = ax.figure.get_size_inches()
    pos = ax.get_position()
    box = (pos.width * fig_w) / max(pos.height * fig_h, 1e-9)
    w, h = x1 - x0, y1 - y0
    if w / h < box:
        cx, w = 0.5 * (x0 + x1), h * box
        x0, x1 = cx - 0.5 * w, cx + 0.5 * w
    else:
        cy, h = 0.5 * (y0 + y1), w / box
        y0, y1 = cy - 0.5 * h, cy + 0.5 * h
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal", adjustable="box")


LABEL_TIER_OFFSETS = (0.10, 0.24)   # label rows beyond the section's edge, x its largest radius


def _place_labels(ax, labels, y_top, y_bottom, fontsize):
    """Leader-line labels in two tiers above (top half) / below (bottom half) the section,
    greedily spread so they don't overlap (text width measured in the axes' own data
    units, so call this after the limits/aspect are final)."""
    ax.apply_aspect()
    xl = ax.get_xlim()
    px = max(ax.get_window_extent().width, 1.0)
    char_w = 0.62 * fontsize * ax.figure.dpi / 72.0 * (xl[1] - xl[0]) / px
    ye = max(y_top, y_bottom)
    for side, sign, edge in (("top", 1.0, y_top), ("bottom", -1.0, y_bottom)):
        items = sorted((l for l in labels if l[2] == side), key=lambda l: l[1][0])
        last_right = [-1e18, -1e18]
        for text, (ax_, ay_), _ in items:
            w = char_w * (max(len(line) for line in text.split("\n")) + 2)
            tier, tx = None, ax_
            for k in (0, 1):
                if tx - 0.5 * w > last_right[k]:
                    tier = k
                    break
            if tier is None:
                tier = 0 if last_right[0] <= last_right[1] else 1
                tx = last_right[tier] + 0.5 * w
            last_right[tier] = tx + 0.5 * w
            ty = sign * (edge + LABEL_TIER_OFFSETS[tier] * ye)
            ax.annotate(text, xy=(ax_, ay_), xytext=(tx, ty), fontsize=fontsize,
                        fontfamily="monospace", fontweight="bold", color=INK,
                        ha="center", va="bottom" if sign > 0 else "top",
                        arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.7, shrinkA=1,
                                        shrinkB=0, mutation_scale=7), zorder=20)


def draw_turbopump_section(fig, result):
    """Fill `fig` with the section (one axes per shaft unit) + a caption."""
    from matplotlib.patches import Polygon
    fig.clear()
    geo = section_geometry(result) if result else None
    if geo is None:
        ax = fig.add_subplot(111)
        ax.axis("off")
        ax.text(0.5, 0.5, "No turbopump on this design (pressure-fed or no sizing).",
                ha="center", va="center", fontsize=11, color=INK, transform=ax.transAxes)
        return geo
    n = len(geo["units"])
    caption = geo["summary"] + ["Note: " + s for s in geo["notes"]]
    bottom = min(0.08 + 0.022 * len(caption), 0.4)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=bottom, hspace=0.3)
    fontsize = 8 if n == 1 else 7
    for i, unit in enumerate(geo["units"]):
        ax = fig.add_subplot(n, 1, i + 1)
        for role, poly in unit["parts"]:
            z, kw = STYLES[role]
            ax.add_patch(Polygon(poly, closed=True, zorder=z, **kw))
        x0, x1 = unit["x_range"]
        ye = unit["y_extent"]
        pad = 0.04 * (x1 - x0)
        ax.plot([x0 - pad, x1 + pad], [0.0, 0.0], color=INK, lw=0.6, ls=(0, (12, 3, 2, 3)), zorder=9)
        y_top, y_bot = unit["y_top"], unit["y_bottom"]
        bar = _nice_length(x1 - x0)
        yb = -(y_bot + 0.42 * ye)
        ax.plot([x0, x0 + bar], [yb, yb], color=INK, lw=2.0)
        ax.text(x0 + 0.5 * bar, yb - 0.03 * ye, f"{bar * 1e3:g} mm", ha="center", va="top",
                fontsize=fontsize, color=INK)
        ax.set_title(unit["title"] + " - section through the shaft (true scale)", fontsize=9,
                     loc="left", fontfamily="monospace")
        _fit_equal(ax, x0 - pad, x1 + pad, -(y_bot + 0.52 * ye), y_top + 0.36 * ye)
        ax.axis("off")
        _place_labels(ax, unit["labels"], y_top, y_bot, fontsize)
    fig.text(0.02, 0.01, "\n".join(caption), fontsize=6.5, color=INK, va="bottom", ha="left",
             wrap=True)
    return geo


# --- self-test ------------------------------------------------------------------------------------
def self_test():
    import json
    import os
    import tempfile
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib.figure import Figure
    from ..physics.design import EngineDesign

    # band / clip / mouth helpers
    b = casing_bands([0.0, 1.0], [0.5, 0.5], 0.1)
    assert len(b) == 1 and np.allclose(b[0][:, 1].max(), 0.6) and np.allclose(b[0][:, 1].min(), 0.5)
    holes = [(0.5, 0.7, 0.21)]
    assert len(casing_bands([0.0, 1.0], [0.5, 0.5], 0.05, holes)) == 2       # mouth left open
    cl = casing_bands([0.0, 0.0, 1.0, 1.0], [0.0, 0.5, 0.5, 0.0], 0.05, (), 0.1, 0.0)
    assert np.isclose(min(p[:, 1].min() for p in cl), 0.0)                    # closed aft end
    assert all(p[p[:, 0] < 0.0, 1].min() >= 0.1 - 1e-12 for p in cl if np.any(p[:, 0] < 0.0))
    sc = {"x": 0.0, "center_r": np.linspace(1.0, 2.0, 73), "tube_r": np.linspace(0.1, 0.5, 73),
          "u_start": -math.pi, "span": 2.0 * math.pi}
    assert scroll_cut(sc, U_BOTTOM)[2] == 0.5                                 # discharge, not tongue
    assert abs(scroll_cut(sc, U_TOP)[2] - 0.3) < 1e-12                        # mid-wrap

    here = os.path.join(os.path.dirname(__file__), "..", "validation_engines", "engines")

    def corpus(name, **over):
        with open(os.path.join(here, f"{name}.json")) as f:
            d = json.load(f)["design"]
        d.update(over)
        return EngineDesign.from_dict({"schema_version": EngineDesign.SCHEMA_VERSION, "design": d})

    out_dir = os.environ.get("TURBOPUMP_SECTION_PNG_DIR") or tempfile.mkdtemp()
    from .turbopump_scene import layout_for_result
    cases = [("F-1", {}), ("J-2", {}), ("RS-25", {}), ("RL10A-3-3", {}), ("Rutherford", {}),
             ("RD-180", {}), ("Raptor-2", {}), ("F-1", {"pump_model": "correlation"}),
             ("F-1", {"turbopump_geometry_model": "casings"})]
    for name, over in cases:
        r = corpus(name, **over).compute()
        tag = f"{name}{over or ''}"
        geo = section_geometry(r)
        lay = layout_for_result(r)
        assert len(geo["units"]) == len(lay["units"]), tag
        for unit, keys in zip(geo["units"], lay["units"]):
            roles = {role for role, _ in unit["parts"]}
            assert {"casing", "shaft", "fluid"} <= roles, (tag, roles)
            for role, p in unit["parts"]:
                assert role in STYLES and p.shape[1] == 2 and len(p) >= 3, (tag, role)
                assert np.all(np.isfinite(p)), (tag, role)
            assert unit["labels"] and unit["y_extent"] > 0.0, tag
            # the section is true scale: every part within the layout's own extents
            x_lo = min(lay["placements"][k]["x_start"] for k in keys)
            x_hi = max(lay["placements"][k]["x_end"] for k in keys)
            od = max(lay["components"][k]["od_m"] for k in keys)
            slack = 0.25 * od
            assert x_lo - slack <= unit["x_range"][0] and unit["x_range"][1] <= x_hi + slack, \
                (tag, unit["x_range"], x_lo, x_hi)
            assert unit["y_extent"] <= 0.5 * od * 2.0 + slack, (tag, unit["y_extent"], od)
            # bearings drawn round the torsion shaft, balls between the races
            for k in keys:
                if k in tl.PUMP_KEYS and r["turbopump_sizing"][k].get("meanline"):
                    brg = tl.shaft_bearing(r["turbopump_sizing"], k)
                    races = [p for role, p in unit["parts"] if role == "race"]
                    assert races, (tag, k)
                    assert any(abs(np.abs(p[:, 1]).min() - 0.5 * brg["bore_m"]) < 1e-9 for p in races), (tag, k)
            # the bottom (discharge-side) volute section is the scroll's last, largest one
            for k in keys:
                comp = lay["components"][k]
                if k in tl.PUMP_KEYS and comp["scrolls"] and comp["stations"]:
                    _, ctr_b, tube_b = scroll_cut(comp["scrolls"][0], U_BOTTOM)
                    _, ctr_t, tube_t = scroll_cut(comp["scrolls"][0], U_TOP)
                    assert tube_b == float(comp["scrolls"][0]["tube_r"][-1]) and tube_b >= tube_t, (tag, k)
        fig = Figure(figsize=(14, 7 * len(geo["units"])))
        draw_turbopump_section(fig, r)
        assert fig.axes, tag
        fname = os.path.join(out_dir, f"section_{name}{'_' + '_'.join(over.values()) if over else ''}.png")
        fig.savefig(fname, dpi=110)
        assert os.path.getsize(fname) > 20_000, fname
    # no turbopump -> a message, not a crash
    fig = Figure()
    assert draw_turbopump_section(fig, EngineDesign(cycle="pressure_fed").compute()) is None
    assert draw_turbopump_section(fig, None) is None
    print(f"turbopump_section self-test: OK ({len(cases)} corpus sections - single/dual shaft, "
          f"geared, motor, axial fuel pump, correlation envelope, casings mode; true-scale extents, "
          f"bearings on the torsion shaft, discharge-side volute section; PNGs in {out_dir})")


if __name__ == "__main__":
    self_test()
