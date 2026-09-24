"""
Colorbar legend for the 3D preview's flow visualization: the fixed log-T
color scale (gui/preview3d_gl_core/flow_meshes.py) as a Tk Canvas gradient
with tick labels, the current design's temperature range bracketed on it,
and a note when any stream's temperatures are approximate (see
physics/flow_network.py). Tk-only - needs a display; the scale/color math it
draws is the self-tested flow_meshes layer.
"""
import tkinter as tk
from tkinter import ttk

import numpy as np

from . import preview3d_gl_core as core
from ..physics import flow_network

_N_STEPS = 96
_PAD_X = 10


def _hex(rgb):
    return "#%02x%02x%02x" % tuple(int(round(255 * float(c))) for c in rgb)


class FlowLegend(ttk.Frame):
    def __init__(self, master, width=320, height=38, **kwargs):
        super().__init__(master, **kwargs)
        self._width, self._height = width, height
        self._canvas = tk.Canvas(self, width=width, height=height, highlightthickness=0)
        self._canvas.pack(side=tk.LEFT, padx=4, pady=2)
        self._note = ttk.Label(self, text="")
        self._note.pack(side=tk.LEFT, padx=4)
        self._draw_scale()

    def _x_of(self, t_k):
        return _PAD_X + float(core.temperature_unit(t_k)) * (self._width - 2 * _PAD_X)

    def _draw_scale(self):
        c = self._canvas
        c.delete("all")
        bar_top, bar_bot = 4, 18
        ts = core.FLOW_T_MIN_K * (core.FLOW_T_MAX_K / core.FLOW_T_MIN_K) ** np.linspace(0, 1, _N_STEPS + 1)
        cols = core.temperature_colors(0.5 * (ts[:-1] + ts[1:]))
        for t0, t1, col in zip(ts[:-1], ts[1:], cols):
            c.create_rectangle(self._x_of(t0), bar_top, self._x_of(t1) + 1, bar_bot,
                               fill=_hex(col), width=0)
        for t in core.FLOW_LEGEND_TICKS_K:
            x = self._x_of(t)
            c.create_line(x, bar_bot, x, bar_bot + 3)
            c.create_text(x, bar_bot + 4, text=f"{t}", anchor="n", font=("TkDefaultFont", 7))

    def update_result(self, result):
        """Bracket this design's stream temperature range on the scale."""
        self._draw_scale()
        if result is None:
            self._note.configure(text="")
            return
        net = flow_network.build_flow_network(result)
        lo, hi = flow_network.temperature_range(net, propellants=("fuel", "ox"))
        c = self._canvas
        for t in (lo, hi):
            x = self._x_of(t)
            c.create_line(x, 1, x, 21, width=2, fill="white")
            c.create_line(x, 1, x, 21, width=1, fill="black")
        note = f"{lo:.0f}-{hi:.0f} K"
        if flow_network.any_approximate(net):
            note += "  (approx. coolant profile)"
        self._note.configure(text=note)
