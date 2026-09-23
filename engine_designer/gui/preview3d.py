"""
3D preview: revolves the same axisymmetric profile gui/schematic.py draws in
2D (physics/geometry3d.revolve_profile) and renders it as a matplotlib 3D
surface. Same status as schematic.py - a basic shape outline, not a
manufacturing model (no wall thickness, no injector/flange detail).

Kept independent of Tkinter so it can be unit-tested headlessly (matplotlib
Agg backend, no display needed) - see the __main__ block.
"""
import numpy as np

from ..physics import geometry, geometry3d, materials, turbopump_materials


def _darken(hex_color, factor=0.72):
    """Return `hex_color` scaled toward black by `factor` (turbine/hot-end tint)."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (int(r * factor), int(g * factor), int(b * factor))


_GIZMO_LABEL = "_gizmo3d"

#: Corner orientation-gizmo axis colors, matching preview3d_gl_core's
#: GIZMO_AXIS_COLORS convention: X=red, Y=green, Z=blue.
_GIZMO_AXIS_COLORS = (("X", "#d92626"), ("Y", "#26cc33"), ("Z", "#3366f2"))


def _draw_orientation_gizmo(fig, ax3d):
    """
    Small fixed-corner XYZ orientation indicator: a secondary 3D inset axes
    (figure-fraction anchored, so it stays a fixed on-screen size regardless
    of the main view's zoom/pan) with three colored unit-length lines from
    the origin, synced to the main axes' current elev/azim/roll. Rebuilt
    from scratch on every call (removing any prior gizmo axes first) to
    match draw_3d_preview's own full-clear-and-rebuild pattern - see the
    live-drag-sync note in gui/app.py's _sync_gizmo3d for why this alone
    doesn't track interactive mouse-drag rotation frame-by-frame.
    """
    for existing in list(fig.axes):
        if existing.get_label() == _GIZMO_LABEL:
            fig.delaxes(existing)

    gizmo_ax = fig.add_axes([0.01, 0.01, 0.16, 0.16], projection="3d", label=_GIZMO_LABEL)
    gizmo_ax.set_facecolor((1, 1, 1, 0))
    gizmo_ax.patch.set_alpha(0.0)

    for (name, color), (dx, dy, dz) in zip(_GIZMO_AXIS_COLORS, ((1, 0, 0), (0, 1, 0), (0, 0, 1))):
        gizmo_ax.plot([0, dx], [0, dy], [0, dz], color=color, lw=2.2)
        gizmo_ax.text(dx * 1.25, dy * 1.25, dz * 1.25, name, color=color,
                       fontsize=8, fontweight="bold", ha="center", va="center")

    for axis in (gizmo_ax.xaxis, gizmo_ax.yaxis, gizmo_ax.zaxis):
        axis.pane.set_visible(False)
        axis.line.set_visible(False)
        axis.set_ticks([])
    gizmo_ax.grid(False)
    gizmo_ax.set_xlim(-1, 1)
    gizmo_ax.set_ylim(-1, 1)
    gizmo_ax.set_zlim(-1, 1)
    gizmo_ax.set_box_aspect((1, 1, 1))

    gizmo_ax.view_init(elev=ax3d.elev, azim=ax3d.azim, roll=getattr(ax3d, "roll", 0))
    return gizmo_ax


def draw_3d_preview(ax3d, result, n_theta=32):
    ax3d.clear()
    body_xs, body_rs, ext_xs, ext_rs, has_extension = geometry.split_profile_by_area_ratio(
        result["profile_xs_m"], result["profile_rs_m"],
        result["geometry"]["throat_dia_m"], result["eps_for_transition"])

    chamber_mat = materials.MATERIALS[result["inputs"]["material_key"]]
    bell_mat = materials.MATERIALS[result["inputs"]["bell_material_key"]]

    # Colored by the ACTUAL chosen material, fully opaque - separation status
    # (previously the fill color) now lives in the title text only, same
    # precedent already set by the 2D schematic when it needed to free up
    # color for material identity.
    Xb, Yb, Zb = geometry3d.revolve_profile(body_xs, body_rs, n_theta)
    ax3d.plot_surface(Xb, Yb, Zb, color=chamber_mat.color_hex, alpha=1.0, linewidth=0,
                       antialiased=True, rstride=1, cstride=1)
    if has_extension:
        Xe, Ye, Ze = geometry3d.revolve_profile(ext_xs, ext_rs, n_theta)
        ax3d.plot_surface(Xe, Ye, Ze, color=bell_mat.color_hex, alpha=1.0, linewidth=0,
                           antialiased=True, rstride=1, cstride=1)

    # --- injector hardware at the chamber head (x <= 0) ---
    chamber_head_r = float(body_rs[0]) if len(body_rs) else float(result["profile_rs_m"].max())
    chamber_len = float(result["profile_xs_m"].max())
    st = result.get("stability", {})
    dome_depth = 0.0
    if chamber_head_r > 0:
        dome_depth = 0.42 * chamber_head_r
        # Domed injector cap: a quarter-ellipse (0, rc) -> (-dome_depth, 0) revolved.
        t = np.linspace(0.0, np.pi / 2.0, 16)
        dome_xs = -dome_depth * np.sin(t)
        dome_rs = chamber_head_r * np.cos(t)
        Xh, Yh, Zh = geometry3d.revolve_profile(dome_xs, dome_rs, n_theta)
        ax3d.plot_surface(Xh, Yh, Zh, color=_darken(chamber_mat.color_hex, 0.6), alpha=1.0,
                           linewidth=0, antialiased=True, rstride=1, cstride=1)
        # Manifold collar just wider than the chamber, at the head base.
        collar_len = max(0.02 * chamber_head_r, 0.06 * dome_depth)
        Xc, Yc, Zc = geometry3d.capped_cylinder(-collar_len, collar_len, chamber_head_r * 1.10,
                                                 n_theta=n_theta)
        ax3d.plot_surface(Xc, Yc, Zc, color="#8f8f8f", alpha=1.0, linewidth=0,
                           antialiased=True, rstride=1, cstride=1)
        # Fuel / ox feed stubs poking radially off the collar (+y and -y).
        # Linewidth reflects each propellant's real computed manifold bore
        # (physics/manifold.py) - a stub-width cue only, same treatment as
        # gui/schematic.py's 2D version; no torus geometry in this fallback.
        mr = result.get("manifold_result", {})
        stub_len = 0.5 * chamber_head_r
        for sgn, prop_key in ((1.0, "fuel"), (-1.0, "ox")):
            inner_d_m = mr.get(prop_key, {}).get("inner_diameter_m", 0.0)
            lw = max(2.0, min(12.0, inner_d_m * 20.0)) if inner_d_m > 0 else 6.0
            ax3d.plot([-collar_len * 0.5, -collar_len * 0.5],
                      [sgn * chamber_head_r * 1.10, sgn * (chamber_head_r * 1.10 + stub_len)],
                      [0.0, 0.0], color="#6b6b6b", lw=lw, solid_capstyle="round")
        # Baffle blades reaching downstream (+x) into the chamber.
        if st.get("baffles"):
            n = int(st.get("baffle_compartments", 5) or 5)
            blade_len = 0.15 * chamber_len if chamber_len > 0 else 0.5 * chamber_head_r
            for k in range(n):
                ang = k * 2 * np.pi / n
                ax3d.plot([0.0, blade_len],
                          [0.12 * chamber_head_r * np.cos(ang), 0.9 * chamber_head_r * np.cos(ang)],
                          [0.12 * chamber_head_r * np.sin(ang), 0.9 * chamber_head_r * np.sin(ang)],
                          color="#333333", lw=2.2)
        # Corner Helmholtz cavities, small bumps just inside the wall near the head.
        if st.get("cavities") and int(st.get("cavity_count", 0) or 0) > 0:
            nc = int(st["cavity_count"])
            a = np.linspace(0, 2 * np.pi, nc, endpoint=False)
            cx = 0.03 * chamber_len if chamber_len > 0 else 0.05 * chamber_head_r
            ax3d.scatter(np.full_like(a, cx), 0.92 * chamber_head_r * np.cos(a),
                         0.92 * chamber_head_r * np.sin(a), s=24, facecolor="white",
                         edgecolor="#2e7d32", depthshade=False)

    sizing = result.get("turbopump_sizing")
    tp_y_extent = 0.0
    tp_x_extent = result["profile_xs_m"].max()
    tp_mat = None
    if sizing and sizing.get("bodies"):
        tp_mat = turbopump_materials.MATERIALS[result["inputs"]["turbopump_material_key"]]
        pump_c = tp_mat.color_hex
        turb_c = _darken(tp_mat.color_hex)
        # Mount at the injector end, axis parallel to the engine, offset outboard
        # in +Y - the same placement as the GL preview (geometry3d.turbopump_origin_xyz).
        origin = geometry3d.turbopump_origin_for_result(result)
        for kind, (Xt, Yt, Zt) in geometry3d.turbopump_assembly_meshes(sizing["bodies"], origin):
            ax3d.plot_surface(Xt, Yt, Zt, color=turb_c if kind == "turbine" else pump_c,
                               alpha=1.0, linewidth=0, antialiased=True, rstride=1, cstride=1)
            tp_y_extent = max(tp_y_extent, float(Yt.max()))
            tp_x_extent = max(tp_x_extent, float(Xt.max()))

    # Equalize the axes so the shape isn't visually squashed/stretched - matplotlib's
    # 3D axes don't respect 'equal' aspect directly, so size a common cube manually.
    max_r = max(result["profile_rs_m"].max(), tp_y_extent)
    # the injector-face plate/elements sit just proud of x=0 in -x
    head_x_lo = -dome_depth * 1.15 if chamber_head_r > 0 else 0.0
    x_lo = min(result["profile_xs_m"].min(), head_x_lo)
    x_hi = max(result["profile_xs_m"].max(), tp_x_extent)
    x_span = x_hi - x_lo
    half = max(max_r, x_span / 2.0)
    x_mid = (x_hi + x_lo) / 2.0
    ax3d.set_xlim(x_mid - half, x_mid + half)
    ax3d.set_ylim(-half, half)
    ax3d.set_zlim(-half, half)
    # Equal data ranges alone don't make the RENDERED box a cube (Matplotlib's
    # 3D box aspect has been independent of the axis limits since 3.3) - this
    # is what actually fixes the "oblong" look.
    ax3d.set_box_aspect((1, 1, 1))

    ax3d.set_xlabel("axial [m]")
    ax3d.set_ylabel("y [m]")
    ax3d.set_zlabel("z [m]")
    separated = result["separated_at_100pct_sl"]
    title = "3D preview"
    if separated:
        title += "  (SEPARATED at sea level)"
    ax3d.set_title(title, fontsize=9)

    legend_text = f"Chamber/nozzle: {chamber_mat.display_name}"
    if has_extension:
        legend_text += f"\nExtension: {bell_mat.display_name}"
    if tp_mat is not None:
        legend_text += (f"\nTurbopump ({sizing['arrangement'].replace('_', ' ')}, "
                        f"{sizing['n_turbines']}x, ~{sizing['assembly_length_m']:.2f} x "
                        f"{sizing['assembly_od_m']:.2f} m): {tp_mat.display_name}")
    ax3d.text2D(0.02, 0.98, legend_text, transform=ax3d.transAxes, fontsize=7, va="top")

    _draw_orientation_gizmo(ax3d.figure, ax3d)


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from ..physics import cycles
    from ..physics.design import EngineDesign

    for label, kwargs in [
        ("conical", dict(nozzle_type="conical", nozzle_half_angle_deg=15.0)),
        ("bell", dict(nozzle_type="bell", bell_percent_length=80.0)),
    ]:
        design = EngineDesign(propellant_pair="LOX/RP-1", mixture_ratio=2.34,
                               chamber_pressure_pa=8.0e6, expansion_ratio=14,
                               cycle=cycles.GAS_GENERATOR, material_key="narloy_z",
                               throttle_floor=0.6, target_vac_thrust_n=1_450_000, **kwargs)
        result = design.compute()

        fig = plt.figure(figsize=(6, 6))
        ax3d = fig.add_subplot(111, projection="3d")
        draw_3d_preview(ax3d, result)
        assert any(a.get_label() == _GIZMO_LABEL for a in fig.axes), \
            "orientation gizmo axes missing after draw_3d_preview"
        out_path = f"/tmp/engine_designer_3d_smoketest_{label}.png"
        fig.savefig(out_path, dpi=100)
        print(f"preview3d.py headless smoke test ({label}) OK -> {out_path}")

    # --- orientation gizmo tracks the main axes' elev/azim ---
    fig2 = plt.figure(figsize=(4, 4))
    ax3d2 = fig2.add_subplot(111, projection="3d")
    ax3d2.view_init(elev=41, azim=-63)
    draw_3d_preview(ax3d2, result)
    gizmo_ax2 = next(a for a in fig2.axes if a.get_label() == _GIZMO_LABEL)
    assert np.isclose(gizmo_ax2.elev, 41)
    assert np.isclose(gizmo_ax2.azim, -63)
    print("preview3d.py orientation-gizmo elev/azim sync self-check OK")
