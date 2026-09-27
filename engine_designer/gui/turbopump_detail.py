"""
"Turbopump Detail" tab (turbopump Round 2): one pump drawn from its meanline
(physics/pump_meanline.py) - Tk-independent, so it renders headless (Agg) and is
self-tested here; gui/app.py only embeds the Figure.

`draw_turbopump_detail(fig, result, leg="ox")` fills `fig` with six panels:
  A  meridional half-section - inducer, impeller stage(s) (hub/shroud), diffuser /
     volute, shaft; an axial pump's inducer + rotor/stator rows
  B  impeller face - blades + splitters, inducer tip, volute spiral + tongue (vaned
     diffuser ring when fitted); an axial pump's unwrapped rotor/stator cascade
  C  velocity triangles at the impeller inlet and outlet (slipped vs ideal c_u2)
  D  where the shaft power goes - loss breakdown down to the delivered power (eta),
     with the old Ns-bell correlation's eta as a marker
  E  suction - NPSH available vs required (+ thermodynamic-suppression credit),
     suction-limited speed, boost pump, pump heating
  F  head/flow + efficiency sketch vs the throttle floor (zero-slope point / stall)
  plus a caption with the design-intent readout.

Reads result["turbopump_sizing"][f"{leg}_pump"] (its "meanline"), result["suction"],
result["pump_heating"], result["pump_intent"] and result["inputs"]["throttle_floor"].
"""
import math

import numpy as np

_BLUE = "#3a6ea5"
_LIGHT = "#cfe0f3"
_METAL = "#9aa4ae"
_DARK = "#3c434a"
_RED = "#b03a2e"
_GREEN = "#2e7d4f"
_ORANGE = "#d4832a"
_GRAY = "#7a7a7a"

LOSS_LABELS = {
    "friction": "channel friction", "diffusion": "diffusion", "diffuser": "volute / diffuser",
    "hydraulic": "blade-row hydraulic", "inducer": "inducer", "leakage": "wear-ring leakage",
    "disk_friction": "disk friction", "mechanical": "bearings + seals", "suction_ss": "suction (Ss) penalty",
}


def _message(fig, text):
    fig.clear()
    ax = fig.add_subplot(111)
    ax.axis("off")
    ax.text(0.5, 0.5, text, ha="center", va="center", fontsize=11, color=_DARK, wrap=True,
            transform=ax.transAxes)


def _pump(result, leg):
    ts = result.get("turbopump_sizing") or {}
    return ts.get(f"{leg}_pump") or {}


# --- A: meridional ---------------------------------------------------------------
def _draw_meridional_centrifugal(ax, pump, ml):
    st = ml["stage"]
    mer = ml["meridional"]
    d2, b2 = st["d2_m"], st["b2_m"]
    r2 = 0.5 * d2
    n = ml["n_stages"]
    pitch = mer["axial_length_m"] + 0.35 * d2
    r_shaft = 0.35 * 0.5 * st["d_hub_m"] + 0.02 * d2
    # inducer upstream of stage 1
    dt = pump.get("inlet_eye_dia_m") or st["d1_m"]
    li = 0.4 * dt
    z0 = -li - 0.05 * d2
    ax.add_patch(_rect(z0, 0.3 * 0.5 * dt, li, 0.5 * dt * 0.7, _LIGHT, _BLUE))
    for k in range(4):
        zz = z0 + li * (k + 0.5) / 4.0
        ax.plot([zz - 0.12 * li, zz + 0.12 * li], [0.3 * 0.5 * dt, 0.5 * dt], color=_BLUE, lw=1.1)
    ax.text(z0 + 0.5 * li, 0.5 * dt + 0.03 * d2, "inducer", ha="center", fontsize=7, color=_BLUE)
    for i in range(n):
        dz = i * pitch
        sh = np.array(mer["shroud"])
        hb = np.array(mer["hub"])
        poly = np.vstack([np.column_stack([sh[:, 0] + dz, sh[:, 1]]),
                          np.column_stack([hb[::-1, 0] + dz, hb[::-1, 1]])])
        ax.fill(poly[:, 0], poly[:, 1], color=_LIGHT, ec=_BLUE, lw=1.0)
        # hub disk
        ax.fill([hb[0, 0] + dz, hb[-1, 0] + dz, hb[-1, 0] + dz + 0.06 * d2, dz + 0.06 * d2],
                [hb[0, 1], hb[-1, 1], r_shaft, r_shaft], color=_METAL, alpha=0.6, lw=0)
        # shroud
        ax.plot(sh[:, 0] + dz, sh[:, 1] + 0.012 * d2, color=_METAL, lw=2.0)
        last = i == n - 1
        z_out = mer["axial_length_m"] - 0.5 * b2 + dz
        if last:
            vol = ml["volute"]
            dif = vol.get("diffuser")
            if dif:
                ax.add_patch(_rect(z_out - 0.5 * b2, dif["r3_m"], b2, dif["r4_m"] - dif["r3_m"],
                                   "#e8d9b0", _ORANGE))
                ax.text(z_out, dif["r4_m"] + 0.01 * d2, f"vaned diffuser ({dif['zd']})", ha="center",
                        fontsize=6.5, color=_ORANGE)
            r_sec = 0.5 * (vol["od_m"] * 0.5 - vol["r_tongue_m"])
            circ = _circle(z_out, vol["r_tongue_m"] + r_sec, r_sec)
            ax.add_patch(circ)
            ax.text(z_out, vol["r_tongue_m"] + 2.0 * r_sec + 0.02 * d2, "volute", ha="center",
                    fontsize=7, color=_DARK)
        else:
            # crossover back to the next eye
            ax.plot([z_out, z_out + 0.18 * d2, z_out + pitch - 0.2 * d2],
                    [r2 + 0.04 * d2, r2 + 0.06 * d2, 0.6 * st["d1_m"] * 0.5],
                    color=_GRAY, lw=1.0, ls="--")
    ax.add_patch(_rect(z0, 0.0, n * pitch - z0 + 0.1 * d2, r_shaft, _METAL, _DARK, alpha=0.45))
    ax.axhline(0.0, color=_DARK, lw=0.8, ls="-.")
    zmax = (n - 1) * pitch + mer["axial_length_m"]
    ax.annotate("", xy=(zmax + 0.05 * d2, r2), xytext=(zmax + 0.05 * d2, 0.0),
                arrowprops=dict(arrowstyle="<->", color=_RED, lw=0.9))
    ax.text(zmax + 0.07 * d2, 0.5 * r2, f"D2 {d2 * 1000:.0f} mm", rotation=90, va="center",
            fontsize=7, color=_RED)
    ax.text(z0, -0.12 * d2, f"b2 {b2 * 1000:.1f} mm   eye {st['d1_m'] * 1000:.0f} mm   inducer tip "
            f"{dt * 1000:.0f} mm", fontsize=7, color=_DARK)
    ax.set_title(f"A  Meridional section - {n} stage(s)", fontsize=9, loc="left")
    ax.set_aspect("equal")
    ax.set_xlim(z0 - 0.1 * d2, zmax + 0.35 * d2)
    ax.set_ylim(-0.18 * d2, max(ml["volute"]["od_m"] * 0.5, r2) * 1.25)
    ax.axis("off")


def _draw_meridional_axial(ax, pump, ml):
    dt, dh = ml["d_tip_m"], ml["d_hub_m"]
    rt, rh = 0.5 * dt, 0.5 * dh
    c = ml["chord_m"]
    gap = 0.15 * c
    z = 0.0
    li = 0.4 * dt
    ax.add_patch(_rect(z, 0.3 * rt, li, rt - 0.3 * rt, _LIGHT, _BLUE))
    ax.text(z + 0.5 * li, rt * 1.08, "inducer", ha="center", fontsize=7, color=_BLUE)
    z += li + gap
    ax.add_patch(_rect(z, rh, 0.7 * c, rt - rh, "#e8d9b0", _ORANGE))
    z += 0.7 * c + gap
    for i in range(ml["n_stages"]):
        ax.add_patch(_rect(z, rh, 0.6 * c, rt - rh, _BLUE, _DARK, alpha=0.8))
        z += 0.6 * c + gap
        ax.add_patch(_rect(z, rh, 0.6 * c, rt - rh, "#e8d9b0", _ORANGE))
        z += 0.6 * c + gap
    r_sec = 0.35 * rt
    ax.add_patch(_circle(z + r_sec, rt + r_sec * 0.2, r_sec))
    ax.text(z + r_sec, rt + 1.35 * r_sec, "volute", ha="center", fontsize=7, color=_DARK)
    ax.add_patch(_rect(-0.05 * dt, 0.0, z + 0.1 * dt, 0.6 * rh, _METAL, _DARK, alpha=0.45))
    ax.axhline(0.0, color=_DARK, lw=0.8, ls="-.")
    ax.text(0.0, -0.12 * dt, f"tip {dt * 1000:.0f} mm  hub/tip {ml['hub_tip']:.2f}  blade "
            f"{ml['blade_height_m'] * 1000:.1f} mm  rotor (blue) / stator (tan) x {ml['n_stages']}",
            fontsize=7, color=_DARK)
    ax.set_title(f"A  Meridional section - axial, inducer + {ml['n_stages']} stages", fontsize=9, loc="left")
    ax.set_aspect("equal")
    ax.set_xlim(-0.1 * dt, z + 0.9 * dt)
    ax.set_ylim(-0.2 * dt, rt * 1.9)
    ax.axis("off")


def _rect(x, y, w, h, fc, ec, alpha=1.0):
    from matplotlib.patches import Rectangle
    return Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec, lw=0.9, alpha=alpha)


def _circle(x, y, r):
    from matplotlib.patches import Circle
    return Circle((x, y), r, facecolor="#f1e3c8", edgecolor=_DARK, lw=0.9)


# --- B: face / cascade -------------------------------------------------------------
def _draw_face_centrifugal(ax, pump, ml):
    st = ml["stage"]
    r1 = 0.5 * st["d1_m"]
    r2 = 0.5 * st["d2_m"]
    camber = np.array(ml["blade"])
    z, zin = st["z"], st["z_inlet"]
    split = st["splitters"]
    th0 = np.linspace(0.0, 2.0 * math.pi, 200)
    ax.fill(r2 * np.cos(th0), r2 * np.sin(th0), color=_LIGHT, ec=_BLUE, lw=0.8)
    ax.fill(r1 * np.cos(th0), r1 * np.sin(th0), color="white", ec=_BLUE, lw=0.6, ls="--")
    n_full = zin if split else z
    for k in range(n_full):
        a = 2.0 * math.pi * k / n_full
        th = -camber[:, 1] + a       # rotation counter-clockwise, blades swept back
        ax.plot(camber[:, 0] * np.cos(th), camber[:, 0] * np.sin(th), color=_DARK, lw=1.4)
    if split:
        n_sp = z - zin
        r_s = r1 + 0.4 * (r2 - r1)
        sel = camber[:, 0] >= r_s
        for k in range(n_sp):
            a = 2.0 * math.pi * (k + 0.5) / max(n_sp, 1)
            th = -camber[sel, 1] + a
            ax.plot(camber[sel, 0] * np.cos(th), camber[sel, 0] * np.sin(th), color=_DARK, lw=1.0)
    vol = ml["volute"]
    sp = np.array(vol["spiral"])
    tv = np.radians(sp[:, 0]) + math.pi / 2.0
    ax.plot(sp[:, 1] * np.cos(tv), sp[:, 1] * np.sin(tv), color=_DARK, lw=1.2)
    ax.plot(vol["r_tongue_m"] * np.cos(th0), vol["r_tongue_m"] * np.sin(th0), color=_GRAY, lw=0.6, ls=":")
    ax.plot([0.0, 0.0], [vol["r_tongue_m"], sp[-1, 1]], color=_RED, lw=1.5)
    ax.text(0.03 * r2, vol["r_tongue_m"], "tongue", fontsize=6.5, color=_RED)
    dif = vol.get("diffuser")
    if dif:
        for k in range(dif["zd"]):
            a = 2.0 * math.pi * k / dif["zd"]
            ax.plot([dif["r3_m"] * math.cos(a), dif["r4_m"] * math.cos(a + 0.25)],
                    [dif["r3_m"] * math.sin(a), dif["r4_m"] * math.sin(a + 0.25)], color=_ORANGE, lw=1.1)
    eye = pump.get("inlet_eye_dia_m") or 0.0
    if eye > 0:
        ax.plot(0.5 * eye * np.cos(th0), 0.5 * eye * np.sin(th0), color=_BLUE, lw=0.8, ls="-.")
    ax.annotate("", xy=(0.55 * r2 * math.cos(1.2), 0.55 * r2 * math.sin(1.2)),
                xytext=(0.55 * r2 * math.cos(0.7), 0.55 * r2 * math.sin(0.7)),
                arrowprops=dict(arrowstyle="->", color=_GREEN, lw=1.2,
                                connectionstyle="arc3,rad=0.3"))
    ax.set_title(f"B  Impeller face: {z} blades" + (f" ({zin}+{z - zin} split.)" if split else "")
                 + f"\n    beta2 {st['beta2_deg']:.0f} deg, {vol.get('diffuser') and 'vaned diffuser' or 'volute'}",
                 fontsize=8.5, loc="left")
    lim = max(sp[:, 1].max(), r2) * 1.1
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.axis("off")


def _arc_profile(x0, y0, chord, stagger_deg, camber_deg, n=20):
    """Circular-arc camber line, chord along the stagger direction."""
    t = np.linspace(0.0, 1.0, n)
    k = math.radians(camber_deg)
    y = 4.0 * 0.5 * math.tan(k / 4.0) * t * (1.0 - t) * chord
    x = t * chord
    s = math.radians(stagger_deg)
    return x0 + x * math.cos(s) - y * math.sin(s), y0 + x * math.sin(s) + y * math.cos(s)


def _draw_cascade_axial(ax, pump, ml):
    b_in, b_ex = ml["beta_in_deg"], ml["beta_exit_deg"]
    c = 1.0
    pitch_r = c / 1.1
    pitch_s = c / 1.6
    cam = b_in - b_ex
    for k in range(4):
        x, y = _arc_profile(0.0, k * pitch_r, c, 90.0 - 0.5 * (b_in + b_ex), cam)
        ax.plot(x, y, color=_BLUE, lw=2.0)
        x, y = _arc_profile(1.3, k * pitch_s, c, -(90.0 - 0.5 * (b_in + b_ex)) + 180.0, -cam)
        ax.plot(x, y, color=_ORANGE, lw=2.0)
    ax.annotate("rotor (moving)", xy=(-0.5, -0.45), fontsize=7, color=_BLUE)
    ax.annotate("stator", xy=(1.9, -0.45), fontsize=7, color=_ORANGE)
    ax.annotate("", xy=(0.5, 3.6), xytext=(0.0, 3.6),
                arrowprops=dict(arrowstyle="->", color=_GREEN, lw=1.2))
    ax.text(0.55, 3.55, "U", fontsize=8, color=_GREEN)
    ax.set_title(f"B  Blade cascade (unwrapped)\n    {ml['z_rotor']} rotor / {ml['z_stator']} stator blades, "
                 f"DF {max(ml['df_rotor'], ml['df_stator']):.2f}", fontsize=8.5, loc="left")
    ax.set_aspect("equal")
    ax.set_xlim(-0.6, 3.0)
    ax.set_ylim(-0.6, 4.0)
    ax.axis("off")


# --- C: velocity triangles ----------------------------------------------------------
def _triangle(ax, x0, u, cu, cm, label, cu_ideal=None):
    ax.annotate("", xy=(x0 + u, 0.0), xytext=(x0, 0.0), arrowprops=dict(arrowstyle="->", color=_GREEN, lw=1.4))
    ax.annotate("", xy=(x0 + cu, cm), xytext=(x0, 0.0), arrowprops=dict(arrowstyle="->", color=_BLUE, lw=1.4))
    ax.annotate("", xy=(x0 + cu, cm), xytext=(x0 + u, 0.0), arrowprops=dict(arrowstyle="->", color=_RED, lw=1.4))
    if cu_ideal is not None:
        ax.plot([x0, x0 + cu_ideal], [0.0, cm], color=_BLUE, lw=0.8, ls=":")
    ax.text(x0 + 0.5 * u, -0.08, "U", color=_GREEN, fontsize=7, ha="center", va="top")
    ax.text(x0 + 0.5 * cu - 0.04, 0.5 * cm + 0.03, "C", color=_BLUE, fontsize=7)
    ax.text(x0 + 0.5 * (u + cu) + 0.03, 0.5 * cm, "W", color=_RED, fontsize=7)
    ax.text(x0 + 0.5 * u, max(cm, 0.2) + 0.12, label, ha="center", fontsize=7.5, color=_DARK)


def _draw_triangles(ax, ml):
    if ml["type"] == "axial":
        phi, psi_i = ml["phi"], ml["psi_i"]
        _triangle(ax, 0.0, 1.0, (1.0 - psi_i) / 2.0, phi, "rotor inlet")
        _triangle(ax, 1.4, 1.0, (1.0 + psi_i) / 2.0, phi, "rotor outlet")
        ax.set_title(f"C  Velocity triangles (/U mean)\n    phi {phi:.2f}, psi_i {psi_i:.2f}, reaction 0.5",
                     fontsize=8.5, loc="left")
        ax.set_xlim(-0.05, 2.5)
    else:
        st = ml["stage"]
        u2 = st["u2_m_s"]
        _triangle(ax, 0.0, st["u1_m_s"] / u2, 0.0, st["cm1_m_s"] / u2,
                  f"inlet: beta1 {st['beta1_flow_deg']:.0f} deg")
        _triangle(ax, 1.1, 1.0, st["cu2_m_s"] / u2, st["cm2_m_s"] / u2,
                  f"outlet: slip M {st['slip_m']:.2f}", cu_ideal=st["cu2_inf_m_s"] / u2)
        ax.set_title(f"C  Velocity triangles (/U2)\n    phi2 {st['phi2']:.3f}, psi {st['psi']:.2f}, "
                     f"W2/W1 {st['w2_over_w1']:.2f}", fontsize=8.5, loc="left")
        ax.set_xlim(-0.05, 2.2)
    ax.set_ylim(-0.2, 0.75)
    ax.set_aspect("equal")
    ax.axis("off")


# --- D: losses ------------------------------------------------------------------------
def _draw_losses(ax, pump, ml):
    loss = ml["loss_power_w"]
    total = sum(v for k, v in loss.items() if k not in ("useful", "hydraulic")) + loss["useful"]
    if ml["type"] == "centrifugal":
        keys = ["friction", "diffusion", "diffuser", "leakage", "disk_friction", "mechanical", "suction_ss"]
    else:
        keys = ["hydraulic", "inducer", "diffuser", "leakage", "mechanical"]
        total = sum(loss[k] for k in keys) + loss["useful"]
    fr = [(LOSS_LABELS[k], loss[k] / total) for k in keys if loss.get(k, 0.0) > 1e-6 * total]
    eta = pump.get("eta", 0.0)
    y = np.arange(len(fr) + 1)
    left = 1.0
    for i, (lab, f) in enumerate(fr):
        left -= f
        ax.barh(i, f, left=left, color=_RED, alpha=0.75)
        ax.text(1.0, i, f" {lab} {f * 100:.1f}%", va="center", fontsize=7)
    ax.barh(len(fr), eta, color=_GREEN, alpha=0.8)
    ax.text(eta, len(fr), f" delivered: eta {eta:.3f}", va="center", fontsize=7.5, color=_GREEN)
    ec = pump.get("eta_correlation")
    if ec:
        ax.axvline(ec, color=_GRAY, ls="--", lw=0.9)
        ax.text(ec, len(fr) + 0.55, f"Ns-bell {ec:.3f}", fontsize=6.5, color=_GRAY, ha="center")
    ax.set_yticks([])
    ax.set_xlim(0.0, 1.55)
    ax.set_ylim(-0.7, len(fr) + 0.9)
    ax.invert_yaxis()
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.tick_params(labelsize=7)
    ax.set_title("D  Where the shaft power goes", fontsize=9, loc="left")


# --- E: suction -----------------------------------------------------------------------
def _draw_suction(ax, result, leg, pump):
    su = (result.get("suction") or {}).get(leg) or {}
    ph = (result.get("pump_heating") or {}).get(leg) or {}
    npsha = pump.get("npsh_available_ft", 0.0)
    npshr = pump.get("npsh_required_ft", 0.0)
    tsh = pump.get("tsh_ft", 0.0)
    ax.bar([0], [npsha], color=_GREEN, alpha=0.8, width=0.6)
    ax.bar([1], [npshr], color=_ORANGE, alpha=0.8, width=0.6)
    if tsh > 0:
        ax.bar([1], [tsh], bottom=[npshr], color=_ORANGE, alpha=0.3, width=0.6, hatch="//")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["NPSH avail.", "NPSH req."], fontsize=7)
    ax.set_ylabel("ft", fontsize=7)
    ax.tick_params(labelsize=7)
    lines = []
    if pump.get("suction_limited"):
        lines.append(f"SUCTION-LIMITED: {pump['n_rpm']:,.0f} rpm (optimum {pump['rpm_ns_optimum']:,.0f})")
    else:
        lines.append(f"{pump.get('n_rpm', 0):,.0f} rpm, not suction-limited")
    if tsh > 0:
        lines.append(f"TSH credit {tsh:.0f} ft (hatched)")
    if su:
        lines.append(f"inlet {su.get('t_k', 0):.1f} K, p_v {su.get('p_vapor_pa', 0) / 1e3:.0f} kPa")
        b = su.get("boost")
        if b:
            lines.append(f"boost pump +{b['rise_pa'] / 1e5:.1f} bar")
    if ph:
        lines.append(f"pump heating {ph['t_tank_k']:.1f} -> {ph['t_out_k']:.1f} K")
    ax.text(0.98, 0.97, "\n".join(lines), transform=ax.transAxes, fontsize=6.5, va="top", ha="right",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=_GRAY, lw=0.5, alpha=0.9))
    ax.set_xlim(-0.6, 3.2)
    ax.set_title("E  Suction", fontsize=9, loc="left")


# --- F: H-Q ---------------------------------------------------------------------------
def _draw_hq(ax, result, ml):
    hq = ml["hq"]
    x = np.array(hq["x"])
    ax.plot(x, hq["psi_ratio"], color=_BLUE, lw=1.6, label="head / design")
    ax.plot([1.0], [1.0], "o", color=_BLUE)
    ax2 = ax.twinx()
    ax2.plot(x, hq["eta"], color=_GREEN, lw=1.2, ls="--", label="efficiency")
    ax2.set_ylim(0.0, 1.0)
    ax2.tick_params(labelsize=7, colors=_GREEN)
    floor = float((result.get("inputs") or {}).get("throttle_floor", 1.0) or 1.0)
    ax.axvline(floor, color=_GRAY, lw=0.9, ls=":")
    ax.text(floor, ax.get_ylim()[0] if False else 0.05, f" throttle floor {floor:.0%}", fontsize=6.5,
            color=_GRAY, transform=ax.get_xaxis_transform())
    if ml["type"] == "axial":
        xs = hq.get("x_stall", 0.0)
        if xs > 0:
            ax.axvspan(x[0], xs, color=_RED, alpha=0.1)
            ax.text(xs, 0.9, " stall (DF 0.75)", fontsize=6.5, color=_RED, transform=ax.get_xaxis_transform())
    elif not hq["rising_to_shutoff"]:
        ax.axvspan(x[0], hq["x_zero_slope"], color=_RED, alpha=0.1)
        ax.text(hq["x_zero_slope"], 0.9, " zero slope", fontsize=6.5, color=_RED,
                transform=ax.get_xaxis_transform())
    ax.set_xlabel("flow / design flow", fontsize=7)
    ax.set_ylabel("head / design head", fontsize=7, color=_BLUE)
    ax.tick_params(labelsize=7)
    ax.set_title(f"F  Head-flow sketch (shutoff {hq['shutoff_ratio']:.2f} x design) - a sketch, "
                 f"maps are Round 5", fontsize=9, loc="left")


def draw_turbopump_detail(fig, result, leg="ox"):
    """Fill `fig` (a matplotlib Figure) with the detail panels for one pump leg."""
    pump = _pump(result, leg)
    if not pump:
        _message(fig, "No turbopump (pressure-fed engine).")
        return
    ml = pump.get("meanline")
    if not ml:
        _message(fig, "Pump model 'correlation' (Round 1 Ns-bell efficiency) - no blade-level "
                      "design to draw.\nSwitch the pump model to 'meanline' on the Turbopump tab.")
        return
    fig.clear()
    gs = fig.add_gridspec(3, 3, height_ratios=[1.25, 1.0, 1.0], hspace=0.55, wspace=0.35)
    ax_a = fig.add_subplot(gs[0, 0:2])
    ax_b = fig.add_subplot(gs[0, 2])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])
    ax_e = fig.add_subplot(gs[1, 2])
    ax_f = fig.add_subplot(gs[2, 0:2])
    ax_t = fig.add_subplot(gs[2, 2])
    if ml["type"] == "axial":
        _draw_meridional_axial(ax_a, pump, ml)
        _draw_cascade_axial(ax_b, pump, ml)
    else:
        _draw_meridional_centrifugal(ax_a, pump, ml)
        _draw_face_centrifugal(ax_b, pump, ml)
    _draw_triangles(ax_c, ml)
    _draw_losses(ax_d, pump, ml)
    _draw_suction(ax_e, result, leg, pump)
    _draw_hq(ax_f, result, ml)
    ax_t.axis("off")
    intent = (result.get("pump_intent") or {}).get("readout") or []
    head = (f"{leg.upper()} PUMP  {ml['type']}, {ml['n_stages']} stage(s)\n"
            f"{pump['n_rpm']:,.0f} rpm, stage Ns {ml['ns_stage_us']:,.0f}\n"
            f"eta {pump['eta']:.3f} (meanline) vs {pump.get('eta_correlation', 0):.3f} (Ns-bell)\n")
    if ml["type"] == "centrifugal":
        head += f"diffuser: {ml['diffuser']}\n"
    ax_t.text(0.0, 1.0, head + "\nDesign intent:\n" + "\n".join("  " + s for s in intent),
              va="top", ha="left", fontsize=6.8, family="monospace", transform=ax_t.transAxes)
    warn = pump.get("warnings") or []
    if warn:
        ax_t.text(0.0, 0.02, "! " + warn[0][:140], va="bottom", ha="left", fontsize=6.3, color=_RED,
                  transform=ax_t.transAxes, wrap=True)
    fig.suptitle("Turbopump detail - meanline design (physics/pump_meanline.py)", fontsize=10)


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import json
    import os
    from matplotlib.figure import Figure
    from ..physics.design import EngineDesign

    here = os.path.join(os.path.dirname(__file__), "..", "validation_engines", "engines")

    def corpus(name, **over):
        with open(os.path.join(here, f"{name}.json")) as f:
            d = json.load(f)["design"]
        d.update(over)
        return EngineDesign.from_dict({"schema_version": EngineDesign.SCHEMA_VERSION, "design": d})

    cases = [("j2_ox", corpus("J-2"), "ox"), ("j2_fuel_axial", corpus("J-2"), "fuel"),
             ("rs25_fuel", corpus("RS-25"), "fuel"), ("f1_fuel", corpus("F-1"), "fuel"),
             ("f1_ox_maxhead", corpus("F-1", pump_head_curve=1.0), "ox"),
             ("vulcain_ox_vaned", corpus("Vulcain", diffuser_type="vaned"), "ox"),
             ("correlation", corpus("F-1", pump_model="correlation"), "ox"),
             ("pressure_fed", EngineDesign(cycle="pressure_fed"), "ox")]
    for tag, design, leg in cases:
        r = design.compute()
        fig = Figure(figsize=(12, 9))
        draw_turbopump_detail(fig, r, leg)
        out = f"/tmp/engine_designer_turbopump_detail_{tag}.png"
        fig.savefig(out, dpi=80)
        pump = _pump(r, leg)
        ml = pump.get("meanline") if pump else None
        assert (ml is not None) == (tag not in ("correlation", "pressure_fed")), tag
        print(f"{tag:<18} {'meanline ' + ml['type'] if ml else 'message':<22} -> {out}")
    print("turbopump_detail headless smoke test OK")
