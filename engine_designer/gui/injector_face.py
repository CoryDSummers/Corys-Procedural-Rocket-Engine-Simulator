"""
Face-on view of the injector plate: the element pattern, any injector-face
baffle compartments, and any corner-mounted Helmholtz cavities.

Same status as gui/schematic.py / gui/preview3d.py - a schematic, not a
manufacturing drawing. The element count is display-capped (a real large
booster has thousands of orifices); the pattern is representative of the
injector TYPE, not the exact hole layout. Kept independent of Tkinter so it
can be unit-tested headlessly (matplotlib Agg backend) - see __main__.

Reads only `result` keys already produced by physics/design.py:
  geometry.chamber_dia_m, injector_geometry, chamber_acoustics, stability,
  inputs.injector_type.
"""
import numpy as np
from matplotlib.patches import Circle

from ..physics import combustion_stability

_DISPLAY_ELEMENT_CAP = 160          # never draw more dots than this
_ELEMENT_COLOR = "#3a6ea5"
_OX_COLOR = "#b5651d"
_BAFFLE_COLOR = "#444444"
_BAFFLE_BAD_COLOR = "#b02020"
_CAVITY_COLOR = "#2e7d32"


def _element_rings(n_display, r_lo_frac, r_hi_frac, rc):
    """Return a list of (radius, count) concentric rings summing to ~n_display,
    ring populations proportional to ring circumference."""
    if n_display <= 0:
        return []
    n_rings = int(np.clip(round((n_display / np.pi) ** 0.5), 1, 6))
    radii = np.linspace(r_lo_frac * rc, r_hi_frac * rc, n_rings)
    weights = radii / radii.sum()
    counts = np.maximum(1, np.round(weights * n_display).astype(int))
    return list(zip(radii, counts))


def draw_injector_face(ax, result, *, compact=False):
    ax.clear()
    ig = result.get("injector_geometry") or {}
    ac = result.get("chamber_acoustics") or {}
    st = result.get("stability") or {}
    inj_type = (result.get("inputs") or {}).get("injector_type", "impinging")
    rc = float(result["geometry"]["chamber_dia_m"]) / 2.0
    if rc <= 0:
        rc = 1.0

    # Chamber bore / injector plate outline.
    ax.add_patch(Circle((0, 0), rc, fill=False, lw=1.6, color="black", zorder=2))
    ax.add_patch(Circle((0, 0), rc * 0.985, facecolor="#f2efe6", edgecolor="none", zorder=0))

    n_real = int(ig.get("n_elements", 0) or 0)
    n_display = min(n_real, _DISPLAY_ELEMENT_CAP) if n_real else 0
    dot = 8 if compact else 26

    if inj_type == "catalyst_bed":
        ax.add_patch(Circle((0, 0), rc * 0.9, facecolor="#d9cbb3", edgecolor="#8a7a5c",
                             hatch="xx", lw=1.0, zorder=1))
        if not compact:
            ax.text(0, 0, "catalyst bed", ha="center", va="center", fontsize=8)
    elif inj_type == "pintle":
        ax.add_patch(Circle((0, 0), rc * 0.16, facecolor=_ELEMENT_COLOR, edgecolor="black",
                             lw=0.8, zorder=3))
        ang = np.linspace(0, 2 * np.pi, max(12, min(n_display, 48)), endpoint=False)
        ax.scatter(rc * 0.55 * np.cos(ang), rc * 0.55 * np.sin(ang), s=dot,
                   color=_OX_COLOR, zorder=3)
    else:
        open_marker = (inj_type == "coaxial_swirl")
        for ring_r, ring_n in _element_rings(n_display, 0.16, 0.9, rc):
            ang = np.linspace(0, 2 * np.pi, int(ring_n), endpoint=False)
            ax.scatter(ring_r * np.cos(ang), ring_r * np.sin(ang), s=dot,
                       facecolors="none" if open_marker else _ELEMENT_COLOR,
                       edgecolors=_ELEMENT_COLOR, linewidths=0.8, zorder=3)

    # Injector-face baffle compartments (radial blades from a central hub).
    if st.get("baffles"):
        n = int(st.get("baffle_compartments", 5) or 5)
        good = combustion_stability.baffle_compartments_ok(n)
        col = _BAFFLE_COLOR if good else _BAFFLE_BAD_COLOR
        ls = "-" if good else "--"
        ax.add_patch(Circle((0, 0), rc * 0.12, facecolor=col, edgecolor="black",
                             lw=0.6, zorder=4))
        for k in range(n):
            a = k * 2 * np.pi / n
            ax.plot([rc * 0.12 * np.cos(a), rc * 0.97 * np.cos(a)],
                    [rc * 0.12 * np.sin(a), rc * 0.97 * np.sin(a)],
                    color=col, lw=2.2 if not compact else 1.4, ls=ls, zorder=4)
        if not compact and not good:
            ax.text(0, -rc * 1.28, f"baffle: {n} compartments (EVEN/low - use odd >=3)",
                    ha="center", fontsize=7, color=_BAFFLE_BAD_COLOR)

    # Corner-mounted Helmholtz cavities, just inside the wall.
    if st.get("cavities") and int(st.get("cavity_count", 0) or 0) > 0:
        nc = int(st["cavity_count"])
        ang = np.linspace(0, 2 * np.pi, nc, endpoint=False)
        cav_r = rc * 0.055 if not compact else rc * 0.04
        for a in ang:
            ax.add_patch(Circle((rc * 0.92 * np.cos(a), rc * 0.92 * np.sin(a)), cav_r,
                                 facecolor="white", edgecolor=_CAVITY_COLOR, lw=1.0, zorder=5))

    lim = rc * 1.15
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim * (1.35 if not compact else 1.05), lim)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])

    if compact:
        ax.set_title("injector face", fontsize=7)
        for s in ax.spines.values():
            s.set_visible(False)
        return

    resolved = st.get("resolved", True)
    if not st.get("advisory"):
        status = "acoustic modes: stable regime"
    elif resolved:
        how = []
        if st.get("baffles"):
            how.append("baffle")
        if st.get("cavities"):
            how.append("cavities")
        if st.get("injector_stiffness", "nominal") != "nominal":
            how.append("stiff injector")
        status = "acoustic advisory RESOLVED (" + " + ".join(how) + ")"
    else:
        status = "acoustic advisory UNRESOLVED - see Warnings tab"
    aid_bits = []
    if st.get("baffles"):
        aid_bits.append(f"baffle x{st.get('baffle_compartments', 0)}")
    if st.get("cavities") and int(st.get("cavity_count", 0) or 0) > 0:
        aid_bits.append(f"cavities x{st.get('cavity_count')}")
    if st.get("injector_stiffness", "nominal") != "nominal":
        aid_bits.append(f"stiffness {st['injector_stiffness']}")
    lines = [
        f"injector: {inj_type}   elements ~{n_real:,} (showing {n_display})",
        f"orifice ~{ig.get('orifice_dia_mm', 0):.2f} mm   "
        f"V fuel/ox {ig.get('v_fuel_ms', 0):.0f}/{ig.get('v_ox_ms', 0):.0f} m/s   "
        f"Rm {ig.get('momentum_ratio', 0):.2f}",
        f"modes: 1L {ac.get('long_1l_hz', 0):.0f}  1T {ac.get('tang_1t_hz', 0):.0f}  "
        f"1R {ac.get('rad_1r_hz', 0):.0f} Hz",
        "aids: " + (", ".join(aid_bits) if aid_bits else "none"),
        status,
    ]
    ax.text(-lim, -lim * 1.33, "\n".join(lines), ha="left", va="bottom", fontsize=7)
    ax.set_title("Injector face", fontsize=9)


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from ..physics import cycles
    from ..physics.design import EngineDesign

    for label, kwargs in [
        ("plain", dict(injector_type="impinging")),
        ("aided", dict(injector_type="impinging", injector_baffles=True,
                       baffle_compartments=5, acoustic_cavities=True, acoustic_cavity_count=12)),
        ("pintle", dict(injector_type="pintle")),
    ]:
        design = EngineDesign(propellant_pair="LOX/RP-1", mixture_ratio=2.34,
                               chamber_pressure_pa=8.0e6, expansion_ratio=14,
                               cycle=cycles.GAS_GENERATOR, material_key="narloy_z",
                               throttle_floor=0.6, target_vac_thrust_n=1_450_000, **kwargs)
        result = design.compute()

        fig, ax = plt.subplots(figsize=(5, 6))
        draw_injector_face(ax, result)
        out = f"/tmp/engine_designer_injector_face_{label}.png"
        fig.savefig(out, dpi=100)
        # also exercise the compact path
        fig2, ax2 = plt.subplots(figsize=(2, 2))
        draw_injector_face(ax2, result, compact=True)
        fig2.savefig(f"/tmp/engine_designer_injector_face_{label}_compact.png", dpi=100)
        print(f"injector_face.py headless smoke test ({label}) OK -> {out}")
