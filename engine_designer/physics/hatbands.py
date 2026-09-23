"""
Structural tube-bundle retaining bands ("hatbands") for tube_wall construction.

Source basis [SP-8120 Sec.2.2.1.1 p.29, Sec.3.2.1.1 p.71-72, Fig. 40]:
  - retaining bands "shall accept all nozzle hoop loads"; the tube bundle itself is
    NOT relied on for gas-pressure or mechanical loads - the brazed tube-to-band
    joint makes the bundle react as a unit;
  - "required retainer band spacing is determined by analyzing the unsupported tube
    length that can be allowed at operating (pressurized) conditions";
  - "band width depends primarily on band dimensions necessary to withstand the
    required operational loads";
  - simple flat bands with thinned edges (Fig. 40a) where buckle resistance can be
    low (near the throat), stiffer sections (Fig. 40b: hat / omega / hat-over-tube)
    where it must be high (near the exit); overexpansion/start side loads have
    buckled real bands (early J-2 aft band);
  - braze-compatible, age-hardenable band alloys: Inconel 718 / X-750.
SP-8120 gives NO sizing equations, so every formula below is first-principles and
every proportion/margin constant is Tier 3 (see engine_designer/ASSUMPTIONS.md):

  tube span  : each tube is a fixed-fixed beam between bands under the net wall
               pressure acting on its own pitch, w = p * pitch; M = w s^2 / 12;
               thin-wall ellipse section modulus Z = pi t b (b + 3a) / 4 (a = half
               width, b = half height of the swaged tube). s_max = sqrt(12 Z sigma / w).
  band hoop  : N = p_wall * R * s_trib (the band carries ALL hoop load of its
               tributary length), sigma = N / A <= sigma_allow / SF.
  band buckle: thin circular ring under uniform external line load
               q = (p_amb - p_wall) * s_trib: q_cr = 3 E I / R^3 [Timoshenko & Gere,
               Theory of Elastic Stability, ring buckling], required
               q_cr >= BAND_BUCKLING_MARGIN * q. Only when p_amb > p_wall (an
               overexpanded sea-level nozzle); vacuum-only designs have no such load.

Band SECTIONS are closed (axial u, radial v) polygons (v = 0 on the tube crests);
area, centroid and second moment come from the polygon itself, so the renderer
(gui/mesh_builder.build_tube_hatband_pieces) draws exactly the section sized here.
Pure functions, no GUI import.
"""
import math

import numpy as np

from . import isentropic as iso
from . import mass_model

BAND_SECTIONS = ("flat", "tee", "hat", "channel", "box")
BAND_SHAPE_CHOICES = ("auto",) + BAND_SECTIONS
BAND_SHAPE_LABELS = {
    "auto": "Auto (SP-8120: flat near throat, stiffer toward exit)",
    "flat": "Flat strap, thinned edges (SP-8120 Fig. 40a)",
    "tee": "Tee (flat strap + radial web)",
    "hat": "Hat section (SP-8120 Fig. 40b)",
    "channel": "Channel (U, webs outward)",
    "box": "Box (closed section)",
}

# --- section proportions (Tier 3; shapes read off SP-8120 Fig. 40 as an image) ---
FLAT_EDGE_THIN_FRAC = 0.4      # flat strap edge thickness / centre thickness
FLAT_EDGE_RAMP_FRAC = 0.15     # fraction of the width each edge chamfer spans
SECTION_HEIGHT_OVER_WIDTH = {  # radial height / axial footprint width
    "tee": 0.5,
    "hat": 0.6,                # Fig. 40b hat is ~0.6-0.8x its width tall
    "channel": 0.4,
    "box": 0.5,
}
HAT_CROWN_FRAC = 0.5           # hat crown width / footprint (feet take the rest)

# --- sizing defaults (Tier 3) ---
TUBE_WALL_T_REF_M = 0.5e-3     # representative formed-tube wall: Huzel A-1 sample calc
                               # t = 0.020 in [Huzel p.111]; SP-8087 >= 0.010 in, many
                               # chambers 0.012-0.016 in [SP-8087 p.13]
BAND_WIDTH_SPACING_FRAC = 0.12 # default (starting) band width / its tributary span;
                               # widened x1.25 at a time if the gauge ceiling fails
BAND_WIDTH_MIN_M = 0.015
BAND_WIDTH_MAX_M = 0.15
BAND_GAUGE_MIN_M = 0.8e-3      # minimum sheet/strap gauge
BAND_GAUGE_MAX_WIDTH_FRAC = 0.25   # sheet-metal section gauge ceiling / footprint width
FLAT_GAUGE_MAX_WIDTH_FRAC = 0.5    # a solid flat strap may run thicker (a bar)
BAND_SPACING_MIN_M = 0.02
BAND_SHELL_SWITCH_WIDTHS = 3.0 # bands start where the allowable tube span first reaches
                               # this many minimum band widths; upstream of that (high
                               # wall pressure just aft of the throat) discrete bands
                               # would nearly touch, so a CONTINUOUS structural shell is
                               # assumed instead - SP-8120 Sec.2.2.1: "continuous shell
                               # is normally used near the chamber/throat", bands aft
BAND_MAX_COUNT = 60
BAND_BUCKLING_MARGIN = 2.0     # q_cr / q required - start-transient side loads are NOT
                               # modeled (SP-8120: "very difficult to predict")
BAND_BRAZE_GAP_M = 0.1e-3      # band sits on the tube crests across a braze gap


# ---------------------------------------------------------------------------
# section geometry
# ---------------------------------------------------------------------------
def section_outline(shape, width_m, gauge_m, height_m=None):
    """Closed polygon [(u, v), ...] of one band cross-section: u axial (centred on
    the band), v radial outward from the tube crests (v = 0 on the crests). The
    box is a keyhole polygon (outer loop + reversed inner loop joined by a
    zero-width slit) so one polygon still describes a hollow section."""
    w, t = float(width_m), float(gauge_m)
    h = float(height_m) if height_m is not None else section_height_m(shape, w, t)
    hw = 0.5 * w
    if shape == "flat":
        e, r = FLAT_EDGE_THIN_FRAC * t, FLAT_EDGE_RAMP_FRAC * w
        return [(-hw, 0.0), (hw, 0.0), (hw, e), (hw - r, t), (-hw + r, t), (-hw, e)]
    if shape == "tee":
        ht = 0.5 * t
        return [(-hw, 0.0), (hw, 0.0), (hw, t), (ht, t), (ht, h), (-ht, h), (-ht, t), (-hw, t)]
    if shape == "hat":
        c = 0.5 * HAT_CROWN_FRAC * w
        return [(-hw, 0.0), (-c + t, 0.0), (-c + t, h - t), (c - t, h - t), (c - t, 0.0),
                (hw, 0.0), (hw, t), (c, t), (c, h), (-c, h), (-c, t), (-hw, t)]
    if shape == "channel":
        return [(-hw, 0.0), (hw, 0.0), (hw, h), (hw - t, h), (hw - t, t), (-hw + t, t),
                (-hw + t, h), (-hw, h)]
    if shape == "box":
        return [(-hw, 0.0), (hw, 0.0), (hw, h), (-hw, h), (-hw, t),
                (-hw + t, t), (-hw + t, h - t), (hw - t, h - t), (hw - t, t), (-hw + t, t),
                (-hw, t)]
    raise ValueError(f"unknown band section {shape!r}")


def section_height_m(shape, width_m, gauge_m):
    if shape == "flat":
        return float(gauge_m)
    return max(SECTION_HEIGHT_OVER_WIDTH[shape] * float(width_m), 3.0 * float(gauge_m))


def section_props(shape, width_m, gauge_m, height_m=None):
    """(area_m2, centroid_v_m, i_m4) of the polygon section - I about the section's
    own centroidal axis parallel to u (i.e. resisting RADIAL in-plane bending of
    the ring, the ring-buckling stiffness)."""
    pts = section_outline(shape, width_m, gauge_m, height_m)
    a2 = cv = iv = 0.0
    n = len(pts)
    for k in range(n):
        u0, v0 = pts[k]
        u1, v1 = pts[(k + 1) % n]
        cr = u0 * v1 - u1 * v0
        a2 += cr
        cv += (v0 + v1) * cr
        iv += (v0 * v0 + v0 * v1 + v1 * v1) * cr
    area = 0.5 * a2
    if abs(area) < 1e-18:
        return 0.0, 0.0, 0.0
    centroid_v = cv / (6.0 * area)
    i_origin = iv / 12.0
    # signed quantities share area's sign -> dividing/normalizing by it fixes orientation
    sign = 1.0 if area > 0 else -1.0
    area, i_origin = abs(area), sign * i_origin
    i_centroid = i_origin - area * centroid_v ** 2
    return area, centroid_v, max(i_centroid, 0.0)


# ---------------------------------------------------------------------------
# loads
# ---------------------------------------------------------------------------
def wall_static_pressure_pa(x_m, xs_m, rs_m, pc_pa, gamma):
    """Hot-gas static pressure on the wall at axial station x: chamber pressure
    upstream of the throat (conservative - the subsonic drop is small and ignored),
    isentropic p/pc from the local area ratio downstream."""
    xs_m, rs_m = np.asarray(xs_m, float), np.asarray(rs_m, float)
    i_t = int(np.argmin(rs_m))
    if x_m <= xs_m[i_t]:
        return float(pc_pa)
    r = float(np.interp(x_m, xs_m[i_t:], rs_m[i_t:]))
    eps = max((r / rs_m[i_t]) ** 2, 1.0 + 1e-6)
    return float(pc_pa) * iso.pe_over_pc_from_eps(eps, gamma)


def tube_section_ab_m(r_wall_m, n_tubes, tube_height_m):
    """Physical swaged-tube half-width a (fills the pitch) and half-height b."""
    pitch = 2.0 * math.pi * r_wall_m / max(int(n_tubes), 1)
    a = 0.5 * pitch
    b = min(0.5 * tube_height_m, a)
    return a, b, pitch


def tube_span_max_m(p_net_pa, r_wall_m, n_tubes, tube_height_m, sigma_allow_pa,
                    tube_wall_t_m=TUBE_WALL_T_REF_M):
    """Longest unsupported tube length between bands [SP-8120 p.29's criterion],
    modelled as a fixed-fixed beam (M = w s^2/12) of thin-wall elliptical section
    Z = pi t b (b + 3a)/4, loaded by the net wall pressure on its own pitch."""
    a, b, pitch = tube_section_ab_m(r_wall_m, n_tubes, tube_height_m)
    w = abs(p_net_pa) * pitch
    if w <= 0 or b <= 0:
        return float("inf")
    z = math.pi * tube_wall_t_m * b * (b + 3.0 * a) / 4.0
    sigma = sigma_allow_pa / mass_model.SAFETY_FACTOR
    return math.sqrt(12.0 * z * sigma / w)


# ---------------------------------------------------------------------------
# band sizing
# ---------------------------------------------------------------------------
def _check_band(shape, w, t, r_crest_m, p_wall_pa, p_amb_pa, s_trib_m, material):
    area, cv, inertia = section_props(shape, w, t)
    r_c = r_crest_m + BAND_BRAZE_GAP_M + cv
    sigma_allow = material.allowable_stress_pa / mass_model.SAFETY_FACTOR
    hoop_n = max(p_wall_pa, 0.0) * r_crest_m * s_trib_m
    hoop_margin = (sigma_allow * area / hoop_n) if hoop_n > 0 else float("inf")
    q_ext = max(p_amb_pa - p_wall_pa, 0.0) * s_trib_m
    q_cr = 3.0 * material.youngs_modulus_pa * inertia / r_c ** 3 if r_c > 0 else 0.0
    buckle_margin = (q_cr / (BAND_BUCKLING_MARGIN * q_ext)) if q_ext > 0 else float("inf")
    mass = material.density_kg_m3 * area * 2.0 * math.pi * r_c
    return dict(area_m2=area, centroid_v_m=cv, i_m4=inertia, r_centroid_m=r_c,
                hoop_force_n_per_m=hoop_n, hoop_margin=hoop_margin,
                ext_load_n_per_m=q_ext, q_cr_n_per_m=q_cr, buckling_margin=buckle_margin,
                mass_kg=mass, ok=hoop_margin >= 1.0 and buckle_margin >= 1.0)


def _size_band_fixed_width(shape, width_m, r_crest_m, p_wall_pa, p_amb_pa, s_trib_m, material):
    """Smallest gauge (bisection, >= BAND_GAUGE_MIN_M) at which `shape` of this
    width passes both checks; returned flagged (ok=False) at the gauge ceiling."""
    t_lo = BAND_GAUGE_MIN_M
    t_hi = max(t_lo, (FLAT_GAUGE_MAX_WIDTH_FRAC if shape == "flat"
                      else BAND_GAUGE_MAX_WIDTH_FRAC) * width_m)
    args = (r_crest_m, p_wall_pa, p_amb_pa, s_trib_m, material)
    res = _check_band(shape, width_m, t_lo, *args)
    if not res["ok"]:
        res_hi = _check_band(shape, width_m, t_hi, *args)
        if not res_hi["ok"]:
            t_lo, res = t_hi, res_hi
        else:
            lo, hi = t_lo, t_hi
            for _ in range(40):
                mid = 0.5 * (lo + hi)
                if _check_band(shape, width_m, mid, *args)["ok"]:
                    hi = mid
                else:
                    lo = mid
            t_lo, res = hi, _check_band(shape, width_m, hi, *args)
    res.update(shape=shape, width_m=width_m, gauge_m=t_lo,
               height_m=section_height_m(shape, width_m, t_lo))
    return res


def size_band(shape, width_m, r_crest_m, p_wall_pa, p_amb_pa, s_trib_m, material,
              width_fixed=False):
    """Size one band of `shape`: the smallest gauge that passes at `width_m`; if even
    the gauge ceiling fails, WIDEN the band (x1.25 steps up to BAND_WIDTH_MAX_M -
    SP-8120: "band width depends primarily on band dimensions necessary to
    withstand the required operational loads") unless the width is user-fixed. A
    band that still fails is returned flagged (ok=False) - warn, don't block."""
    w = float(width_m)
    res = _size_band_fixed_width(shape, w, r_crest_m, p_wall_pa, p_amb_pa, s_trib_m, material)
    while not res["ok"] and not width_fixed and w < BAND_WIDTH_MAX_M:
        w = min(w * 1.25, BAND_WIDTH_MAX_M)
        res = _size_band_fixed_width(shape, w, r_crest_m, p_wall_pa, p_amb_pa, s_trib_m, material)
    return res


def size_band_auto(width_m, r_crest_m, p_wall_pa, p_amb_pa, s_trib_m, material,
                   width_fixed=False):
    """Lightest passing section, ties to the simpler shape (BAND_SECTIONS order).
    With hoop load only (no external pressure) every section needs about the same
    area, so the flat strap wins; where overexpansion puts the ring in buckling the
    deeper sections win - reproducing SP-8120's flat-near-throat / stiff-near-exit
    practice rather than hard-coding it."""
    best = None
    for shape in BAND_SECTIONS:
        r = size_band(shape, width_m, r_crest_m, p_wall_pa, p_amb_pa, s_trib_m, material,
                      width_fixed=width_fixed)
        key = (not r["ok"], r["mass_kg"] * (1.0 + 1e-9))
        if best is None or key < best[0]:
            best = (key, r)
    return best[1]


def size_bands(xs_m, rs_m, x_start_m, x_end_m, pc_pa, gamma, material, tube_material,
               n_tubes_at, tube_height_m, *, shape="auto", count_override=0,
               width_override_m=0.0, p_amb_pa=0.0, tube_wall_t_m=TUBE_WALL_T_REF_M,
               tube_crest_offset_m=0.0):
    """Place and size retaining bands over the tube-wall span [x_start_m, x_end_m] of
    the gas-side contour (xs_m, rs_m).

    n_tubes_at(r_m) -> physical tube count at a station of gas-side radius r
    (so a tube bifurcation is honoured). `tube_crest_offset_m` is the radial
    distance from the gas-side wall to the tube crests (wall + tube height) -
    bands sit on the crests. `p_amb_pa` = the ambient the nozzle must survive
    (PA_SEA_LEVEL for a sea-level-capable design, 0 for vacuum-only).

    Continuous shell: upstream of the first station whose allowable tube span reaches
    BAND_SHELL_SWITCH_WIDTHS band widths, the bundle is taken to be under a continuous
    structural shell (returned as shell_start_x_m..shell_end_x_m) and no bands are
    placed there.

    Placement: `count_override > 0` puts that many bands uniformly (span/(n+1)
    apart) and flags any gap exceeding the allowable tube span; otherwise marches
    from x_start: next band at x + s_max(x), evaluated at the upstream end of each
    gap (conservative - pressure falls downstream), until the remaining length is
    within one allowable span of x_end (the far-end hardware supports the tubes).
    """
    xs_m, rs_m = np.asarray(xs_m, float), np.asarray(rs_m, float)
    out = dict(bands=[], total_mass_kg=0.0, n_bands=0, shapes_used=[], span_m=0.0,
               shell_start_x_m=None, shell_end_x_m=None,
               worst_hoop_margin=float("inf"), worst_buckling_margin=float("inf"),
               span_ok=True, all_ok=True, advisories=[])
    x0, x1 = float(max(x_start_m, xs_m[0])), float(min(x_end_m, xs_m[-1]))
    if x1 <= x0 or pc_pa <= 0:
        return out
    def r_at(x):
        return float(np.interp(x, xs_m, rs_m))

    def p_at(x):
        return wall_static_pressure_pa(x, xs_m, rs_m, pc_pa, gamma)

    def smax_at(x):
        p_net = max(p_at(x), abs(p_amb_pa - p_at(x)))
        r = r_at(x)
        return tube_span_max_m(p_net, r, n_tubes_at(r), tube_height_m,
                               tube_material.allowable_stress_pa, tube_wall_t_m)

    # Continuous-shell region: from x0 until the allowable tube span first reaches
    # BAND_SHELL_SWITCH_WIDTHS minimum band widths (SP-8120: shell near the throat,
    # bands downstream). The bands (and the span check) start there.
    switch_span = BAND_SHELL_SWITCH_WIDTHS * BAND_WIDTH_MIN_M
    x_probe = np.linspace(x0, x1, 200)
    ok_idx = [i for i, xp in enumerate(x_probe) if smax_at(xp) >= switch_span]
    x_shell_end = float(x_probe[ok_idx[0]]) if ok_idx else x1
    out["shell_start_x_m"], out["shell_end_x_m"] = x0, x_shell_end
    x0 = x_shell_end
    if x1 - x0 <= BAND_SPACING_MIN_M:
        return out

    out["span_m"] = x1 - x0
    s_min = BAND_SPACING_MIN_M
    if count_override and count_override > 0:
        n = int(count_override)
        xs_band = [x0 + k * (x1 - x0) / (n + 1) for k in range(1, n + 1)]
    else:
        xs_band, x = [], x0
        while len(xs_band) < BAND_MAX_COUNT:
            s = max(min(smax_at(x), x1 - x0), s_min)
            if x + s >= x1:
                break
            x += s
            xs_band.append(x)
        if len(xs_band) >= BAND_MAX_COUNT:
            out["advisories"].append(
                f"Hatband march hit the {BAND_MAX_COUNT}-band cap - the tube span allowed at "
                f"this wall pressure is very short; thicker/rounder tubes or a continuous "
                f"shell over the high-pressure region would be more realistic.")

    supports = [x0] + xs_band + [x1]
    for k in range(1, len(supports)):
        gap = supports[k] - supports[k - 1]
        allow = smax_at(supports[k - 1])
        if gap > allow * (1.0 + 1e-6):
            out["span_ok"] = False
    if not out["span_ok"]:
        out["advisories"].append(
            "Unsupported tube length between hatbands exceeds the allowable span (tube "
            "bending at wall pressure, SP-8120 p.29) - add bands or set the count to 0 "
            "(structural auto).")

    for k, xb in enumerate(xs_band, start=1):
        s_trib = 0.5 * (supports[k + 1] - supports[k - 1])
        fixed = bool(width_override_m and width_override_m > 0)
        width = (float(width_override_m) if fixed
                 else min(max(BAND_WIDTH_SPACING_FRAC * s_trib, BAND_WIDTH_MIN_M),
                          BAND_WIDTH_MAX_M))
        r_crest = r_at(xb) + tube_crest_offset_m
        p_wall = p_at(xb)
        if shape == "auto":
            band = size_band_auto(width, r_crest, p_wall, p_amb_pa, s_trib, material,
                                  width_fixed=fixed)
        else:
            band = size_band(shape, width, r_crest, p_wall, p_amb_pa, s_trib, material,
                             width_fixed=fixed)
        eps = max((r_at(xb) / rs_m.min()) ** 2, 1.0)
        band.update(x_m=xb, r_crest_m=r_crest, p_wall_pa=p_wall, trib_span_m=s_trib,
                    local_eps=eps)
        out["bands"].append(band)

    bands = out["bands"]
    out["n_bands"] = len(bands)
    out["total_mass_kg"] = float(sum(b["mass_kg"] for b in bands))
    out["shapes_used"] = sorted({b["shape"] for b in bands}, key=BAND_SECTIONS.index)
    if bands:
        out["worst_hoop_margin"] = min(b["hoop_margin"] for b in bands)
        out["worst_buckling_margin"] = min(b["buckling_margin"] for b in bands)
    failed = [b for b in bands if not b["ok"]]
    if failed:
        out["advisories"].append(
            f"{len(failed)} hatband(s) fail hoop or ring-buckling at the gauge ceiling "
            f"({', '.join(sorted({b['shape'] for b in failed}))}) - pick a stiffer section, "
            f"a wider band or 'auto'.")
    out["all_ok"] = out["span_ok"] and not failed
    return out


def hatband_mass_kg(bands):
    """Sum of sized band masses (rho * A * 2 pi R_centroid)."""
    return float(sum(b.get("mass_kg", 0.0) for b in (bands or [])))


# ---------------------------------------------------------------------------
def self_test():
    from . import materials
    inco = materials.MATERIALS["inconel_718"]

    # --- polygon section properties against closed-form rectangles ---
    a, cv, i = section_props("channel", 0.10, 0.01, 0.01)   # h == t -> a plain 0.10 x 0.01 bar
    assert math.isclose(a, 0.10 * 0.01, rel_tol=1e-9)
    assert math.isclose(cv, 0.005, rel_tol=1e-9)
    assert math.isclose(i, 0.10 * 0.01 ** 3 / 12.0, rel_tol=1e-9)
    # box = outer rect minus inner rect
    w, t, h = 0.06, 0.004, 0.03
    a_b, cv_b, i_b = section_props("box", w, t, h)
    a_exp = w * h - (w - 2 * t) * (h - 2 * t)
    i_exp = w * h ** 3 / 12.0 - (w - 2 * t) * (h - 2 * t) ** 3 / 12.0
    assert math.isclose(a_b, a_exp, rel_tol=1e-9) and math.isclose(cv_b, h / 2, rel_tol=1e-9)
    assert math.isclose(i_b, i_exp, rel_tol=1e-9)
    # tee: base + web, parallel-axis
    w, t, h = 0.08, 0.003, 0.04
    a_t, cv_t, i_t = section_props("tee", w, t, h)
    a1, v1, a2, v2 = w * t, t / 2, t * (h - t), t + (h - t) / 2
    cv_exp = (a1 * v1 + a2 * v2) / (a1 + a2)
    i_exp = (w * t ** 3 / 12 + a1 * (v1 - cv_exp) ** 2
             + t * (h - t) ** 3 / 12 + a2 * (v2 - cv_exp) ** 2)
    assert math.isclose(a_t, a1 + a2, rel_tol=1e-9) and math.isclose(cv_t, cv_exp, rel_tol=1e-9)
    assert math.isclose(i_t, i_exp, rel_tol=1e-9)
    # every shape: positive area/inertia; the thinned-edge flat strap has less area
    # than a full rectangle; stiff sections beat the flat strap on I at equal gauge
    for s in BAND_SECTIONS:
        a_s, _, i_s = section_props(s, 0.05, 0.002)
        assert a_s > 0 and i_s > 0, s
    a_f, _, i_f = section_props("flat", 0.05, 0.002)
    assert a_f < 0.05 * 0.002
    for s in ("tee", "hat", "channel", "box"):
        assert section_props(s, 0.05, 0.002)[2] > 20 * i_f, s
    print("section polygon properties self-check: OK")

    # --- gauge solve: passes at the returned gauge, fails just below it ---
    r = size_band("hat", 0.05, 1.0, 5e5, 0.0, 0.2, inco)
    assert r["ok"] and r["hoop_margin"] >= 1.0
    if r["gauge_m"] > BAND_GAUGE_MIN_M * 1.001:
        assert not _check_band("hat", 0.05, r["gauge_m"] * 0.99, 1.0, 5e5, 0.0, 0.2, inco)["ok"]
    # hoop-only -> auto picks the flat strap (least material for pure tension)
    assert size_band_auto(0.05, 1.0, 5e5, 0.0, 0.2, inco)["shape"] == "flat"
    # heavy external (overexpanded) load -> auto escalates past the flat strap
    r_ext = size_band_auto(0.05, 1.0, 5e3, 101325.0, 0.3, inco)
    assert r_ext["shape"] != "flat" and r_ext["ok"], r_ext["shape"]
    print("band gauge solve + auto shape escalation self-check: OK")

    # --- tube span: shorter at higher pressure, longer for taller tubes ---
    s_hi = tube_span_max_m(2e6, 0.4, 200, 0.008, inco.allowable_stress_pa)
    s_lo = tube_span_max_m(2e5, 0.4, 200, 0.008, inco.allowable_stress_pa)
    assert s_lo > s_hi and math.isclose(s_lo / s_hi, math.sqrt(10.0), rel_tol=1e-9)
    assert tube_span_max_m(2e5, 0.4, 200, 0.012, inco.allowable_stress_pa) > s_lo
    print("tube span model self-check: OK")

    # --- march on a bell: spacing grows downstream (pressure falls) ---
    xs = np.linspace(0.0, 2.0, 200)
    rt = 0.2
    rs = rt + 0.6 * np.sqrt(np.maximum(xs - 0.3, 0.0)) + np.where(xs < 0.3, (0.3 - xs) * 0.8, 0.0)
    res = size_bands(xs, rs, 0.3, 2.0, 7e6, 1.2, inco, inco, lambda r_: 180, 0.01,
                     p_amb_pa=101325.0, tube_crest_offset_m=0.012)
    xb = [b["x_m"] for b in res["bands"]]
    assert res["n_bands"] >= 3 and res["span_ok"]
    assert res["bands"][0]["shape"] == "flat"
    assert res["total_mass_kg"] > 0
    # vacuum-only design: no external load -> spacing grows monotonically as the
    # wall pressure falls, and flat straps suffice everywhere. (At sea level the
    # gaps shrink again near the exit once p_wall < p_amb - the net INWARD load
    # |p_amb - p_wall| grows - which is real, so it is not asserted there.)
    res_v = size_bands(xs, rs, 0.3, 2.0, 7e6, 1.2, inco, inco, lambda r_: 180, 0.01,
                       p_amb_pa=0.0, tube_crest_offset_m=0.012)
    gaps = np.diff([0.3] + [b["x_m"] for b in res_v["bands"]])
    assert np.all(np.diff(gaps) > -1e-9), gaps
    assert res_v["shapes_used"] == ["flat"]
    # sea level: the overexpanded aft bands see ring-buckling load -> stiffer sections
    assert res["bands"][-1]["ext_load_n_per_m"] > 0
    # count override too sparse -> span advisory, not a crash
    res_c = size_bands(xs, rs, 0.3, 2.0, 7e6, 1.2, inco, inco, lambda r_: 180, 0.01,
                       count_override=1, p_amb_pa=0.0, tube_crest_offset_m=0.012)
    assert res_c["n_bands"] == 1 and not res_c["span_ok"] and res_c["advisories"]
    print("band placement march self-check: OK "
          f"({res['n_bands']} bands, {res['total_mass_kg']:.1f} kg, shapes {res['shapes_used']})")
    print("ALL HATBANDS CHECKS OK")


if __name__ == "__main__":
    self_test()
