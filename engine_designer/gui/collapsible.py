"""
CollapsibleSection: a small ttk.Frame with a clickable header (an arrow +
title) that shows or hides a body frame. Toggling only grid()s/grid_remove()s
the body - it never destroys widgets, so tk.Variable references (and their
trace_add callbacks) built inside stay valid regardless of collapsed state.
This matters because app.py's _on_control_change/_refresh_widgets_from_design
reference those variables unconditionally by attribute name.

Usage: create one per logical group of controls, grid it into the parent at
columnspan=2 like any other row, then build controls into `.body_parent()`
using a fresh local row counter starting at 0 - exactly as if it were a bare
tab Frame. _add_slider/_add_dropdown are parent-agnostic, so they work
unchanged.

No collapsed-state persistence across app restarts by design - this is a
single-user desktop tool, not worth a settings file for it.
"""
import tkinter as tk
from tkinter import ttk

_ARROW_OPEN = "▼"     # ▼
_ARROW_CLOSED = "▶"   # ▶


class CollapsibleSection(ttk.Frame):
    def __init__(self, parent, title, start_open=True, **kwargs):
        super().__init__(parent, **kwargs)
        self.columnconfigure(0, weight=1)
        self._open = start_open

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        self._arrow_var = tk.StringVar(value=_ARROW_OPEN if start_open else _ARROW_CLOSED)
        arrow_label = ttk.Label(header, textvariable=self._arrow_var, width=2, cursor="hand2")
        arrow_label.grid(row=0, column=0, sticky="w")
        title_label = ttk.Label(header, text=title, cursor="hand2",
                                 font=("TkDefaultFont", 9, "bold"))
        title_label.grid(row=0, column=1, sticky="w")

        for widget in (header, arrow_label, title_label):
            widget.bind("<Button-1>", self._on_click)

        self.body = ttk.Frame(self, padding=(12, 0, 0, 4))
        self.body.columnconfigure(0, weight=1)
        self.body.columnconfigure(1, weight=0)
        self.body.grid(row=1, column=0, sticky="ew")
        if not start_open:
            self.body.grid_remove()

    def _on_click(self, _event=None):
        self.toggle()

    def toggle(self):
        self._open = not self._open
        self._arrow_var.set(_ARROW_OPEN if self._open else _ARROW_CLOSED)
        if self._open:
            self.body.grid()
        else:
            self.body.grid_remove()

    def body_parent(self):
        """The frame to build this section's controls into (fresh row=0)."""
        return self.body
