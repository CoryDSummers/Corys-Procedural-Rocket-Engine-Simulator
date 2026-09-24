"""
Draws a basic 2D cutaway outline of the engine (chamber - convergent cone -
throat - divergent cone) from an EngineDesign.compute() result dict onto a
given matplotlib Axes. Straight conical sections, not a true bell contour -
"a basic outline of the design," per the brief, not a manufacturing drawing.

Kept independent of Tkinter so it can be unit-tested headlessly (matplotlib
Agg backend, no display needed) - see the __main__ block.
"""
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Rectangle

from ..physics import geometry, materials

# Cooling-method -> colour for the zone bands drawn above the contour. Film is
# not a zone (it's an overlay on any method) - its injection stations get ticks.
_FILM_COLOR = "#2fa79b"
_COOLING_METHOD_COLOR = {
    "regenerative": "#2f6fb0",
    "dump": "#7b5fb0",
    "ablative": "#8a5a3a",
    "radiative": "#d08a2f",
    "uncooled": "#9aa0a6",
}


def _draw_cooling_overlay(ax, result, xs_mm, rs_mm, transition_x_mm, cooled_end_x_mm=None):
    """Heat-flux colouring on the contour + cooling-zone bands + a peak/total
    annotation + a legend. Guarded by the caller on result['cooling']; kept in
    its own function so the base schematic stays readable."""
    cooling = result["cooling"]
    q = np.asarray(cooling["q_profile_w_m2"], dtype=float) / 1e6  # MW/m^2
    if q.size != xs_mm.size or q.size < 2:
        return

    norm = Normalize(vmin=float(q.min()), vmax=float(q.max()) or 1.0)
    seg_q = 0.5 * (q[:-1] + q[1:])
    for sign in (1.0, -1.0):
        pts = np.column_stack([xs_mm, sign * rs_mm])
        segs = np.stack([pts[:-1], pts[1:]], axis=1)
        lc = LineCollection(segs, cmap="turbo", norm=norm, linewidths=4.5, zorder=4)
        lc.set_array(seg_q)
        ax.add_collection(lc)

    # Cooling-regime bands just above the upper contour (WHERE each regime
    # applies along the axis). Labels go in the legend, not floating text.
    band_y = rs_mm.max() * 1.14
    _co = result.get("cooling", {})
    chamber_method = _co.get("chamber_cooling_method") or \
        materials.MATERIALS[result["inputs"]["material_key"]].cooling_method
    bell_method = _co.get("nozzle_cooling_method") or \
        materials.MATERIALS[result["inputs"]["bell_material_key"]].cooling_method
    m_margin = result["material_margin"]["margin_ratio"]
    b_margin = result["bell_material_margin"]["margin_ratio"]
    x_lo, x_hi = xs_mm[0], xs_mm[-1]
    tx = transition_x_mm if transition_x_mm is not None else x_hi

    zones = [(x_lo, tx, chamber_method)]
    if transition_x_mm is not None and tx < x_hi:
        zones.append((tx, x_hi, bell_method))
    for zx0, zx1, method in zones:
        ax.plot([zx0, zx1], [band_y, band_y], lw=6, solid_capstyle="butt",
                color=_COOLING_METHOD_COLOR.get(method, "#888888"), zorder=2)

    q_throat = cooling["q_throat_w_m2"] / 1e6
    total_mw = cooling["wall_heat_total_w"] / 1e6
    t_wg = cooling.get("t_wg_throat_k")
    hg = cooling.get("hg_throat_w_m2k")
    tint_label = (f"contour tint = wall heat flux ({q_throat:.0f} MW/m$^2$ peak, "
                  f"~{total_mw:.0f} MW total)")
    if t_wg and hg:
        tint_label += f"\nthroat h_g {hg:.0f} W/m$^2$K -> wall temp ~{t_wg:.0f} K"
    handles = [Line2D([0], [0], color="#d33", lw=4, label=tint_label)]
    film_fraction = cooling.get("film_cooling_fraction") or 0.0
    if film_fraction > 0.0:
        handles.append(Line2D([0], [0], color=_FILM_COLOR, lw=2,
                              label=f"chamber film curtain {film_fraction*100:.0f}% of fuel "
                                    f"(flux x{cooling.get('film_flux_factor', 1.0):.2f})"))
    nozzle_film = cooling.get("nozzle_film_fraction") or 0.0
    if nozzle_film > 0.0:
        handles.append(Line2D([0], [0], color=_FILM_COLOR, lw=2, linestyle="--",
                              label=f"nozzle film slot {nozzle_film*100:.0f}% of fuel at eps "
                                    f"{cooling.get('nozzle_film_inject_eps', 0):.0f} (Isp -"
                                    f"{(cooling.get('nozzle_film_isp_penalty_fraction') or 0)*100:.2f}%)"))
    # A short wall-normal tick at each film injection station (first station
    # each site's multiplier drops below 1), both walls.
    for _key, _ls in (("chamber_film_profile", "-"), ("nozzle_film_profile", "--")):
        _phi = np.asarray(cooling.get(_key) if cooling.get(_key) is not None else [], dtype=float)
        if _phi.size == xs_mm.size and np.any(_phi < 1.0):
            _i = int(np.argmax(_phi < 1.0))
            for _sg in (1.0, -1.0):
                ax.plot([xs_mm[_i]] * 2, [_sg * rs_mm[_i] * 0.88, _sg * rs_mm[_i] * 1.12],
                        color=_FILM_COLOR, lw=2.0, linestyle=_ls, zorder=5)
    peak_k = cooling.get("peak_wall_temp_k")
    if peak_k:
        handles.append(Line2D([0], [0], color="none",
                              label=f"hottest cooled wall ~{peak_k:.0f} K in the "
                                    f"{cooling.get('peak_wall_temp_zone')} "
                                    f"({cooling.get('peak_wall_margin_ratio', 0):.2f}x margin)"))
    seen = set()
    for _, _, method in zones:
        if method in seen:
            continue
        seen.add(method)
        margin = m_margin if method == chamber_method else b_margin
        handles.append(Line2D([0], [0], color=_COOLING_METHOD_COLOR.get(method, "#888888"),
                              lw=6, label=f"{method} zone ({margin:.1f}x wall-temp margin)"))
    if not cooling["regen_ok"]:
        handles.append(Line2D([0], [0], color="none",
                              label="[!] regen coolant dT over coking/boiling limit"))
    dump_penalty = cooling.get("dump_isp_penalty_fraction") or 0.0
    if dump_penalty > 0.0:
        handles.append(Line2D([0], [0], color="none",
                              label=f"dump-cooled nozzle {cooling.get('dump_coolant_fraction', 0)*100:.0f}% "
                                    f"of fuel, ejected overboard (Isp -{dump_penalty*100:.2f}%)"))
        # An arrow at the exit lip showing the coolant leaving the flow, distinct
        # from the main exhaust the contour already implies.
        ax.annotate("", xy=(x_hi + (x_hi - x_lo) * 0.06, rs_mm[-1] * 1.15),
                    xytext=(x_hi, rs_mm[-1] * 0.9),
                    arrowprops=dict(arrowstyle="->", color="#7b5fb0", lw=1.3), zorder=3)
        ax.annotate("dump", xy=(x_hi + (x_hi - x_lo) * 0.06, rs_mm[-1] * 1.15),
                    fontsize=6, color="#7b5fb0", ha="left", va="center")
    if cooled_end_x_mm is not None:
        # Active cooling extends past the bell-MATERIAL transition (regen_nozzle_end_eps):
        # a light marker distinct from the material-boundary dotted line drawn elsewhere.
        ax.plot([cooled_end_x_mm] * 2, [-rs_mm.max() * 1.05, rs_mm.max() * 1.05],
                 color="#2f6fb0", linewidth=1.0, linestyle="-.", zorder=2, alpha=0.7)
        handles.append(Line2D([0], [0], color="#2f6fb0", lw=1.0, linestyle="-.",
                              label=f"active cooling ends here (eps "
                                    f"{cooling['cooled_length_eps']:.0f}, past the material split)"))
    ax.legend(handles=handles, loc="lower right", fontsize=6, framealpha=0.9)


def _draw_injector_block(ax, result, xs_mm, rs_mm):
    """A side-profile injector manifold/dome on the chamber head (x <= 0), with
    feed stubs, and (when fitted) baffle blades reaching downstream into the
    chamber and Helmholtz-cavity pockets in the wall near the head."""
    rc = float(rs_mm[0])                       # chamber radius at the head [mm]
    if rc <= 0:
        return
    lc_mm = float(result["geometry"]["chamber_length_m"]) * 1000.0
    ig = result.get("injector_geometry", {})
    st = result.get("stability", {})
    l_dome = 0.38 * rc

    # Domed manifold: a half-ellipse bulging upstream (-x) from a face flange.
    th = np.linspace(np.pi / 2.0, -np.pi / 2.0, 24)
    dome_x = -l_dome * np.cos(th)
    dome_r = rc * 1.06 * np.sin(th)
    ax.fill(dome_x, dome_r, facecolor="#9a9a9a", edgecolor="black", linewidth=1.2, zorder=3)
    ax.plot([0.0, 0.0], [-rc * 1.06, rc * 1.06], color="black", linewidth=1.2, zorder=3)

    # Fuel / ox feed stubs off the back of the dome. Linewidth reflects each
    # propellant's real computed manifold bore (physics/manifold.py) - a flat
    # line-width cue, not a routed pipe.
    mr = result.get("manifold_result", {})
    _STUB_LW_MM_PER_M = 40.0   # display scale only: matplotlib points per meter
                                # of inner diameter, chosen so a ~50mm ID reads
                                # close to the old fixed lw=5 default
    for r_frac, tag, prop_key in ((0.55, "F", "fuel"), (-0.55, "O", "ox")):
        sx = -l_dome * 0.55
        inner_d_m = mr.get(prop_key, {}).get("inner_diameter_m", 0.0)
        lw = max(2.0, min(12.0, inner_d_m * _STUB_LW_MM_PER_M)) if inner_d_m > 0 else 5.0
        ax.plot([sx, sx - 0.5 * l_dome], [rc * r_frac, rc * r_frac],
                color="#6b6b6b", linewidth=lw, solid_capstyle="round", zorder=3)
        ax.annotate(tag, xy=(sx - 0.5 * l_dome, rc * r_frac), fontsize=6, ha="right",
                    va="center")

    # Injector-face baffle blades reaching downstream into the chamber.
    if st.get("baffles"):
        n = min(int(st.get("baffle_compartments", 5) or 5), 6)
        blade_len = 0.14 * lc_mm if lc_mm > 0 else 0.5 * rc
        for rr in np.linspace(-rc * 0.85, rc * 0.85, n):
            ax.plot([0.0, blade_len], [rr, rr], color="#333333", linewidth=2.2, zorder=4)

    # Corner Helmholtz cavities as pockets in the wall just aft of the head.
    if st.get("cavities") and int(st.get("cavity_count", 0) or 0) > 0:
        px = 0.03 * lc_mm if lc_mm > 0 else 0.1 * rc
        pw = max(0.04 * rc, 0.02 * lc_mm)
        ph = 0.09 * rc
        for sgn in (1.0, -1.0):
            y0 = sgn * rc - ph if sgn > 0 else sgn * rc
            ax.add_patch(Rectangle((px, y0), pw, ph, facecolor="white",
                                    edgecolor="#2e7d32", linewidth=1.0, zorder=4))

    pattern = result.get("inputs", {}).get("injector_type", "impinging")
    ax.annotate(f"injector: {pattern}  ~{ig.get('n_elements', 0):,} elem  "
                f"Rm {ig.get('momentum_ratio', 0):.2f}",
                xy=(-l_dome * 0.5, rc * 1.2), fontsize=7, ha="center")


_EXHAUST_COLOR = "#8a6e5c"


def _draw_turbine_exhaust(ax, result, xs_mm, rs_mm):
    """Open cycles: the turbine-exhaust termination in side view (physics/
    turbine_exhaust.size_hardware) - the injection manifold's section as a
    circle on both walls, the aspirator shroud as an offset line over the aft
    nozzle, or the overboard exhaust nozzle as an arrow beside the bell - each
    labelled with the mode and the exhaust's own Isp. Returns the largest
    |radius| drawn [mm] (so the axes can make room), or None."""
    hw = result.get("turbine_exhaust_hardware")
    te = result.get("turbine_exhaust")
    if not hw or not te:
        return None
    label = (f"turbine exhaust: {te['mode'].replace('_', ' ')}, "
             f"{te['isp_vac_s']:.0f} s vac, PR {te['turbine_pressure_ratio']:.1f}")
    if hw["mode"] == "nozzle_injection":
        ring = hw["exhaust"]
        x = ring["attach_axial_station_m"] * 1000.0
        rc = ring["major_radius_m"] * 1000.0
        rt = ring["outer_radius_m"] * 1000.0
        for sg in (1.0, -1.0):
            ax.add_patch(Circle((x, sg * rc), rt, facecolor=_EXHAUST_COLOR, edgecolor="black",
                                linewidth=0.6, zorder=4))
        ax.annotate(label, xy=(x, rc + rt), xytext=(x, rs_mm.max() * 1.25), ha="center",
                    fontsize=6, color=_EXHAUST_COLOR, arrowprops=dict(arrowstyle="->", lw=0.6,
                                                                      color=_EXHAUST_COLOR))
        return rc + rt
    elif hw["mode"] == "aspirator":
        a = hw["aspirator"]
        sx = np.asarray(a["xs"]) * 1000.0
        so = np.asarray(a["r_outer"]) * 1000.0
        for sg in (1.0, -1.0):
            ax.plot(sx, sg * so, color=_EXHAUST_COLOR, linewidth=2.0, zorder=4)
        ax.annotate(label + f", slot {te.get('aspirator_gap_m', 0) * 1000:.1f} mm",
                    xy=(sx[-1], so[-1]), xytext=(sx[0], rs_mm.max() * 1.25), ha="center",
                    fontsize=6, color=_EXHAUST_COLOR,
                    arrowprops=dict(arrowstyle="->", lw=0.6, color=_EXHAUST_COLOR))
        return float(so.max())
    else:
        o = hw["outlet"]
        x0, y0 = o["pos"][0] * 1000.0, np.hypot(o["pos"][1], o["pos"][2]) * 1000.0
        L = max(o["length_m"], o["exit_dia_m"]) * 1000.0
        dx, dr = o["dir"][0], np.hypot(o["dir"][1], o["dir"][2])
        # upper half: the legend owns the lower right
        ax.annotate("", xy=(x0 + L * dx, y0 + L * dr), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color=_EXHAUST_COLOR, lw=2.0), zorder=4)
        ax.annotate(label, xy=(x0, y0), xytext=(x0 - L, y0 + L * dr + 0.15 * rs_mm.max()),
                    ha="center", fontsize=6, color=_EXHAUST_COLOR)
        return y0 + L * dr + 0.3 * rs_mm.max()


def draw_schematic(ax, result):
    ax.clear()
    xs = result["profile_xs_m"]
    rs = result["profile_rs_m"]
    body_xs, body_rs, ext_xs, ext_rs, has_extension = geometry.split_profile_by_area_ratio(
        xs, rs, result["geometry"]["throat_dia_m"], result["eps_for_transition"])

    xs_mm = xs * 1000.0
    rs_mm = rs * 1000.0
    body_x, body_r = body_xs * 1000.0, body_rs * 1000.0
    ext_x, ext_r = ext_xs * 1000.0, ext_rs * 1000.0

    separated = result["separated_at_100pct_sl"]
    fill_color = "#c97a3a" if separated else "#5a8fc9"

    # Main body (chamber through the throat and up to the cooling-transition
    # point) vs. nozzle extension (past it, checked against a different
    # material - bell_material_key). Same hue for both (still carries the
    # separated/attached status), but the extension is drawn at lower alpha
    # with a hatch pattern and a dashed outline so the material boundary
    # reads even without color (don't rely on color alone).
    outline_x = np.concatenate([body_x, body_x[::-1]])
    outline_r = np.concatenate([body_r, -body_r[::-1]])
    ax.fill(outline_x, outline_r, color=fill_color, alpha=0.35, zorder=1)
    ax.plot(body_x, body_r, color="black", linewidth=1.5, zorder=2)
    ax.plot(body_x, -body_r, color="black", linewidth=1.5, zorder=2)

    if has_extension:
        outline_ext_x = np.concatenate([ext_x, ext_x[::-1]])
        outline_ext_r = np.concatenate([ext_r, -ext_r[::-1]])
        ax.fill(outline_ext_x, outline_ext_r, facecolor=fill_color, alpha=0.15,
                 hatch="//", edgecolor="black", linewidth=0, zorder=1)
        ax.plot(ext_x, ext_r, color="black", linewidth=1.5, linestyle="--", zorder=2)
        ax.plot(ext_x, -ext_r, color="black", linewidth=1.5, linestyle="--", zorder=2)
        # Boundary marker between the two materials.
        ax.plot([ext_x[0]] * 2, [-ext_r[0], ext_r[0]],
                 color="black", linewidth=1.0, linestyle=":", zorder=2)

    ax.plot([xs_mm[0], xs_mm[0]], [-rs_mm[0], rs_mm[0]], color="black", linewidth=1.5, zorder=2)
    ax.plot([xs_mm[-1], xs_mm[-1]], [-rs_mm[-1], rs_mm[-1]], color="black", linewidth=1.5, zorder=2)

    ax.axhline(0, color="grey", linestyle="--", linewidth=0.8, zorder=0)

    chamber_mat_name = materials.MATERIALS[result["inputs"]["material_key"]].display_name
    bell_mat_name = materials.MATERIALS[result["inputs"]["bell_material_key"]].display_name
    if has_extension:
        ax.annotate(f"chamber/nozzle: {chamber_mat_name}",
                    xy=(ext_x[0], -ext_r[0]),
                    xytext=(xs_mm.min(), -rs_mm.max() * 1.45),
                    ha="left", fontsize=7)
        ax.annotate(f"nozzle extension (hatched): {bell_mat_name}",
                    xy=(ext_x[0], -ext_r[0]),
                    xytext=(xs_mm.min(), -rs_mm.max() * 1.6),
                    ha="left", fontsize=7)
    else:
        ax.annotate(f"chamber/nozzle material: {chamber_mat_name} "
                    f"(no separate extension section - cooling transition is at/past the exit)",
                    xy=(xs_mm.min(), -rs_mm.max() * 1.45), xytext=(xs_mm.min(), -rs_mm.max() * 1.45),
                    ha="left", fontsize=7)

    throat_x = xs_mm[2]
    ax.annotate(f"throat {result['geometry']['throat_dia_m']*100:.1f} cm",
                xy=(throat_x, rs_mm[2]), xytext=(throat_x, rs_mm[2] + rs_mm.max() * 0.35),
                ha="center", fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.8))
    ax.annotate(f"exit {result['geometry']['exit_dia_m']*100:.1f} cm",
                xy=(xs_mm[-1], rs_mm[-1]), xytext=(xs_mm[-1], -rs_mm.max() * 1.15),
                ha="right", fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.8))
    _chx = float(result["geometry"]["chamber_length_m"]) * 1000.0 * 0.5
    ax.annotate(f"chamber {result['geometry']['chamber_dia_m']*100:.1f} cm",
                xy=(_chx, rs_mm[0]), xytext=(_chx, rs_mm.max() * 1.35),
                ha="center", fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.8))

    transition_x_mm = ext_x[0] if has_extension else None
    has_cooling = "cooling" in result and result["cooling"].get("q_profile_w_m2") is not None
    cooled_end_x_mm = None
    if has_cooling:
        _cooled_eps = result["cooling"].get("cooled_length_eps")
        if _cooled_eps is not None and _cooled_eps > result["eps_for_transition"] + 1e-6:
            _, _, _cool_ext_xs, _, _cool_has_ext = geometry.split_profile_by_area_ratio(
                xs, rs, result["geometry"]["throat_dia_m"], _cooled_eps)
            if _cool_has_ext:
                cooled_end_x_mm = _cool_ext_xs[0] * 1000.0
        _draw_cooling_overlay(ax, result, xs_mm, rs_mm, transition_x_mm, cooled_end_x_mm)
        _co = result["cooling"]
        if not _co["regen_ok"]:
            ax.annotate(f"[!] regen coolant dT ~{_co['coolant_delta_t_k']:.0f} K exceeds "
                        f"~{_co['coolant_limit_k']:.0f} K limit",
                        xy=(xs_mm.min(), rs_mm.max() * 1.45),
                        xytext=(xs_mm.min(), rs_mm.max() * 1.45), ha="left", fontsize=7,
                        color="#a03030")

    te_extent_mm = None
    try:
        te_extent_mm = _draw_turbine_exhaust(ax, result, xs_mm, rs_mm)
    except Exception:
        pass   # a drawing hiccup here must never blank the schematic

    # Side-view injector block sitting on the chamber head.
    if result.get("injector_geometry"):
        try:
            _draw_injector_block(ax, result, xs_mm, rs_mm)
        except Exception:
            pass   # a drawing hiccup here must never blank the schematic

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("axial position [mm]")
    ax.set_ylabel("radius [mm]")
    title = "Engine schematic"
    if has_cooling:
        title += "  -  contour tinted by wall heat flux (dark = cool, bright = hot)"
    if separated:
        title += "  (SEPARATED at sea level)"
    ax.set_title(title, fontsize=9)
    margin = rs_mm.max() * 0.5
    # extra room in front of the head for the injector block + feed stubs
    left = xs_mm.min() - max(margin, rs_mm[0] * 0.75)
    ax.set_xlim(left, xs_mm.max() + margin)
    top = rs_mm.max() * (1.62 if has_cooling else 1.6)
    if te_extent_mm:
        top = max(top, te_extent_mm * 1.08)
    ax.set_ylim(-rs_mm.max() * 1.85, top)


if __name__ == "__main__":
    # Headless smoke test: no Tkinter, no display needed (Agg backend).
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from ..physics import cycles
    from ..physics.design import EngineDesign

    design = EngineDesign(propellant_pair="LOX/RP-1", mixture_ratio=2.34,
                           chamber_pressure_pa=8.0e6, expansion_ratio=14,
                           nozzle_half_angle_deg=15, cycle=cycles.GAS_GENERATOR,
                           material_key="narloy_z", throttle_floor=0.6,
                           target_vac_thrust_n=1_450_000)
    result = design.compute()

    fig, ax = plt.subplots(figsize=(6, 4))
    draw_schematic(ax, result)
    out_path = "/tmp/engine_designer_schematic_smoketest.png"
    fig.savefig(out_path, dpi=100)

    # Both film sites + the full-length wall balance: two tick pairs in the film
    # colour, and the film / peak-wall legend entries.
    film_design = EngineDesign(material_key="narloy_z", regen_channel_model="channels",
                               nozzle_type="bell", film_cooling_fraction=0.05,
                               nozzle_film_fraction=0.03, nozzle_film_inject_eps=8.0,
                               bell_material_key="inconel_718", nozzle_cooling_method="uncooled")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    draw_schematic(ax2, film_design.compute())
    _ticks = [ln for ln in ax2.get_lines() if ln.get_color() == _FILM_COLOR]
    assert len(_ticks) == 4, len(_ticks)
    _labels = [t.get_text() for t in ax2.get_legend().get_texts()]
    assert any("nozzle film slot" in t for t in _labels), _labels
    assert any("hottest cooled wall" in t for t in _labels), _labels
    plt.close(fig2)
    # Turbine exhaust: each mode draws its termination + a labelled annotation.
    for _mode in ("overboard_duct", "aspirator", "nozzle_injection"):
        _r = EngineDesign(propellant_pair="LOX/RP-1", mixture_ratio=2.34,
                          chamber_pressure_pa=5.0e6, expansion_ratio=12.0,
                          cycle=cycles.GAS_GENERATOR, target_vac_thrust_n=900_000.0,
                          turbine_exhaust_mode=_mode).compute()
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        draw_schematic(ax3, _r)
        _txt = [t.get_text() for t in ax3.texts]
        assert any("turbine exhaust: " + _mode.replace("_", " ") in t for t in _txt), _txt
        plt.close(fig3)
    print(f"schematic.py headless smoke test OK -> {out_path}")
