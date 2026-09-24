"""
Colorbar legend for the 3D preview's flow visualization: the active flow
color scale (gui/preview3d_gl_core/flow_meshes.FlowColorScale - the fixed
log-T "absolute" scale, or a linear fit to this design's coolant / stream
range) as a Tk Canvas gradient with tick labels, the current design's drawn
temperature range bracketed on it, and notes when any stream's temperatures
are approximate (see physics/flow_network.py) or fall outside a fit scale
(drawn clamped to the end colors). Tk-only - needs a display; the scale/color
math it draws is the self-tested flow_meshes layer.
"""
import tkinter as tk
from tkinter import ttk

import numpy as np

from . import preview3d_gl_core as core
from ..physics import flow_network

_N_STEPS = 96
_PAD_X = 10
_PROP_LABEL = {"fuel": "fuel", "ox": "ox"}


def _hex(rgb):
    return "#%02x%02x%02x" % tuple(int(round(255 * float(c))) for c in rgb)


def _fmt_k(t):
    return f"{t:.0f}" if abs(t - round(t)) < 1e-6 or abs(t) >= 100 else f"{t:.1f}"


class FlowLegend(ttk.Frame):
    def __init__(self, master, width=320, height=38, **kwargs):
        super().__init__(master, **kwargs)
        self._width, self._height = width, height
        self._scale = core.ABSOLUTE_SCALE
        self._canvas = tk.Canvas(self, width=width, height=height, highlightthickness=0)
        self._canvas.pack(side=tk.LEFT, padx=4, pady=2)
        self._note = ttk.Label(self, text="")
        self._note.pack(side=tk.LEFT, padx=4)
        self._draw_scale()

    def _x_of(self, t_k):
        return _PAD_X + float(core.temperature_unit(t_k, self._scale)) * (self._width - 2 * _PAD_X)

    def _draw_scale(self):
        c = self._canvas
        c.delete("all")
        bar_top, bar_bot = 4, 18
        u = np.linspace(0.0, 1.0, _N_STEPS + 1)
        lo, hi = float(self._scale.lo_k), float(self._scale.hi_k)
        ts = lo * (hi / lo) ** u if self._scale.is_log else lo + (hi - lo) * u
        cols = core.temperature_colors(0.5 * (ts[:-1] + ts[1:]), self._scale)
        for t0, t1, col in zip(ts[:-1], ts[1:], cols):
            c.create_rectangle(self._x_of(t0), bar_top, self._x_of(t1) + 1, bar_bot,
                               fill=_hex(col), width=0)
        for t in core.scale_ticks(self._scale):
            x = self._x_of(t)
            c.create_line(x, bar_bot, x, bar_bot + 3)
            c.create_text(x, bar_bot + 4, text=_fmt_k(t), anchor="n", font=("TkDefaultFont", 7))

    def update_result(self, result, scale=None, network=None):
        """Draw `scale` (default: the absolute scale) and bracket this design's
        drawn stream range on it."""
        self._scale = scale or core.ABSOLUTE_SCALE
        self._draw_scale()
        if result is None:
            self._note.configure(text="")
            return
        net = network if network is not None else flow_network.build_flow_network(result)
        lo, hi = flow_network.temperature_range(net, propellants=("fuel", "ox"))
        c = self._canvas
        for t in (lo, hi):
            x = self._x_of(t)
            c.create_line(x, 1, x, 21, width=2, fill="white")
            c.create_line(x, 1, x, 21, width=1, fill="black")
        if self._scale.is_log:
            note = f"{lo:.0f}-{hi:.0f} K"
        else:
            what = "coolant" if self._scale.mode == "coolant" else "streams"
            note = f"{what} {self._scale.lo_k:.0f}-{self._scale.hi_k:.0f} K"
            # streams the fit clamps to its end colors
            for prop in ("fuel", "ox"):
                vals = [np.atleast_1d(np.asarray(sg.t_k, dtype=float)) for sg in net
                        if sg.propellant == prop]
                if not vals:
                    continue
                v = np.concatenate(vals)
                v = v[np.isfinite(v)]
                if v.size and v.min() < self._scale.lo_k - 0.5:
                    note += f"; {_PROP_LABEL[prop]} {v.min():.0f} K below scale"
                if v.size and v.max() > self._scale.hi_k + 0.5:
                    note += f"; {_PROP_LABEL[prop]} {v.max():.0f} K above scale"
        if flow_network.any_approximate(net):
            note += "  (approx.)"
        self._note.configure(text=note)
