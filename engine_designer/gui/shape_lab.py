"""
Shape Lab: an in-window "context switch" for interactively editing a small
piece of geometry against a live 3D preview, then "baking" the result back
into the design. Launched from a button in the main window (gui/app.py), it
takes over the ENTIRE main window in place - the normal sidebar + preview
tabs are unpacked and a Lab panel fills that same space, restored on
Bake/Cancel (see gui/app.py's _enter_shape_lab/_exit_shape_lab). This is a
stronger modal than a dialog's grab_set(): the underlying controls aren't
just input-blocked, they're physically removed from the layout.

Two panels share one base (_ShapeLabBase: header, GL-or-matplotlib preview,
Bake/Cancel row, the redraw plumbing):

- PlumbingLabPanel - THE editor since the procedural-plumbing round: a
  physics/plumbing.py PlumbingRun rooted on the loaded design's real
  jacket-inlet ring (host_ring_from_result), with a Run group (attach angle
  around the engine axis, poloidal angle around the ring tube, root flange,
  shared flange style), a Segment group (a "Pipe k" selector whose sliders -
  length x dia, yaw, pitch, elbow radius x dia, flange-at-end - rebind to the
  selected pipe, plus Add pipe / Remove last), a View group (ghost chamber
  wall; ghost turbopump + a straight "ray" from the run's free end to the
  pump it will feed - the placeholder for future connecting pipes;
  engineering shading), and a live advisory line from plumbing.resolve_run. The scene comes from gui/shape_lab_geometry.
  build_plumbing_scene, which draws the run with the SAME
  mesh_builder.build_plumbing_pieces the main 3D preview uses for a baked
  run - what you see is what bakes. Bake stores run_to_dict() into
  design.plumbing_runs (replacing any existing run on that host) and
  recomputes, so the run appears on the real engine, in the mass rollup, in
  the checklist and in the saved project.

- ShapeLabPanel - the original generic sliders-only panel, parameterized by
  SliderSpecs + a build_pieces_fn(values) callback. Still used for the
  synthetic-ring FALLBACK (open_manifold_shape_lab) when the design has no
  jacket-inlet ring to root a run on; its three legacy sliders are
  preview-only now (the dead-stored EngineDesign fields they used to bake
  into were removed in schema 4).

Renderer: prefers the same GPU-rendered EnginePreviewGLFrame the main
window's 3D Preview tab uses (real orbit camera via mouse-drag, scroll-wheel
zoom, for free), falling back to a matplotlib Poly3DCollection renderer if
PyOpenGL/pyopengltk aren't installed or the GL widget fails to construct -
the exact same availability-check-and-degrade pattern gui/app.py already
uses for its own 3D Preview tab. Either way, per-piece color comes from each
MeshBuffers' own baked-in `.colors`.

IMPORTANT: like the rest of gui/, this needs a real display. The sandbox
this was built in has no $DISPLAY (and no PyOpenGL/pyopengltk installed
either), so this file could only be syntax-checked here - launch it for real
and report back whether the controls/preview/Bake/Cancel behave as expected,
and whether the GL renderer or the matplotlib fallback is the one that
actually loads on your machine.
"""
from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from tkinter import messagebox

from . import shape_lab_geometry
from ..physics import plumbing

# Prefer the GPU-rendered OpenGL widget (real-time orbit camera), same
# availability flag / fallback convention as gui/app.py's own 3D Preview
# tab - see that module's docstring for why this can't be exercised here.
try:
    from .preview3d_gl import EnginePreviewGLFrame
    _GL_AVAILABLE = True
except ImportError:
    _GL_AVAILABLE = False


@dataclass
class SliderSpec:
    name: str            # key in the values dict passed to build_pieces_fn/on_bake
    label: str
    lo: float
    hi: float
    default: float
    decimals: int = 1


class _ShapeLabBase(ttk.Frame):
    """Shared shell: title header, a sidebar frame the subclass populates via
    _build_sidebar(sidebar), the GL-or-matplotlib preview, and Bake/Cancel.
    Subclasses implement _build_sidebar(), _build_scene() -> {"pieces",
    "center", "half"} and _bake(). `on_close()` is always called last, either
    way, to hand control back to the caller (gui/app.py's _exit_shape_lab)."""

    def __init__(self, parent, title, on_close):
        super().__init__(parent)
        self._on_close = on_close
        self._gl_frame = None
        self._flat_shade_var = None
        self._xray_var = None
        self._fig = self._ax = self._canvas = None

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Label(self, text=title, font=("TkDefaultFont", 13, "bold"), padding=8)
        header.grid(row=0, column=0, columnspan=2, sticky="w")

        sidebar = ttk.Frame(self, padding=8)
        sidebar.grid(row=1, column=0, sticky="ns")
        self._build_sidebar(sidebar)

        button_row = ttk.Frame(self, padding=8)
        button_row.grid(row=2, column=0, columnspan=2, sticky="ew")
        ttk.Button(button_row, text="Bake", command=self._bake).pack(side=tk.RIGHT, padx=4)
        ttk.Button(button_row, text="Cancel", command=self._on_close).pack(side=tk.RIGHT)

        preview = ttk.Frame(self)
        preview.grid(row=1, column=1, sticky="nsew")
        self._build_preview_widget(preview)

        self._redraw()

    def _build_sidebar(self, sidebar):
        raise NotImplementedError

    def _build_scene(self):
        raise NotImplementedError

    def _bake(self):
        raise NotImplementedError

    def _build_preview_widget(self, preview):
        if _GL_AVAILABLE:
            try:
                # Shape Lab gets its own light-blue background (distinct from
                # the main window's dark 3D Preview tab) so it reads as a
                # separate mode at a glance - main window's own
                # EnginePreviewGLFrame instance keeps the class default.
                # The synthetic ring+duct scene also gets its own light_dir,
                # mirrored across Y from the main preview's default
                # (0.4, 0.6, 0.7) -> (0.4, -0.6, 0.7): the main preview's
                # default was tuned for the revolved-engine scene, and read
                # as lighting the ring/duct scene from the wrong side.
                self._gl_frame = EnginePreviewGLFrame(preview, width=500, height=500,
                                                       clear_color=(209 / 255, 228 / 255, 240 / 255),
                                                       light_dir=(0.4, -0.6, 0.7))
                # "Engineering shading" toggle - GL-only (see set_flat_shade's
                # docstring on EnginePreviewGLFrame); the matplotlib fallback
                # below keeps its current shaded look unconditionally, no
                # toggle shown, so there's nothing here for it to control.
                toolbar = ttk.Frame(preview)
                toolbar.pack(fill=tk.X)
                self._flat_shade_var = tk.BooleanVar(value=False)
                ttk.Checkbutton(toolbar, text="Engineering shading",
                                variable=self._flat_shade_var,
                                command=self._on_flat_shade_toggle).pack(side=tk.LEFT, padx=4, pady=2)
                self._xray_var = tk.BooleanVar(value=False)
                ttk.Checkbutton(toolbar, text="X-ray", variable=self._xray_var,
                                command=lambda: self._gl_frame.set_xray(self._xray_var.get())
                                ).pack(side=tk.LEFT, padx=4, pady=2)
                self._gl_frame.pack(fill=tk.BOTH, expand=True)
                return
            except Exception as exc:
                print(f"Shape Lab: OpenGL widget failed to initialize, "
                      f"falling back to matplotlib: {exc}")
                for child in preview.winfo_children():
                    child.destroy()
                self._gl_frame = None

        self._fig = Figure(figsize=(5, 5))
        self._ax = self._fig.add_subplot(111, projection="3d")
        self._canvas = FigureCanvasTkAgg(self._fig, master=preview)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _on_flat_shade_toggle(self):
        self._gl_frame.set_flat_shade(self._flat_shade_var.get())

    def _redraw(self):
        if self._gl_frame is None and self._ax is None:
            return  # sidebar var writes during construction, before the preview exists
        data = self._build_scene()
        if self._gl_frame is not None:
            self._gl_frame.update_meshes(data["pieces"], data["center"], data["half"])
            return

        self._ax.clear()
        for mesh in data["pieces"]:
            triangles = mesh.vertices[mesh.indices]
            facecolors = mesh.colors[mesh.indices].mean(axis=1)
            self._ax.add_collection3d(Poly3DCollection(triangles, facecolor=facecolors,
                                                         edgecolor="none", alpha=1.0))
        cx, cy, cz = data["center"]
        half = data["half"]
        self._ax.set_xlim(cx - half, cx + half)
        self._ax.set_ylim(cy - half, cy + half)
        self._ax.set_zlim(cz - half, cz + half)
        self._ax.set_box_aspect((1, 1, 1))
        self._ax.set_xlabel("axial [m]")
        self._ax.set_ylabel("y [m]")
        self._ax.set_zlabel("z [m]")
        self._canvas.draw_idle()


class ShapeLabPanel(_ShapeLabBase):
    """The generic sliders-only panel: a sidebar of sliders (mirroring
    gui/app.py's own Label+Entry+Scale-sharing-one-tk.DoubleVar pattern)
    next to the live preview.

    `build_pieces_fn(values_dict) -> {"pieces": [MeshBuffers, ...], "center":
    (x, y, z), "half": float}` is called once at construction and again on
    every slider change. `on_bake(values_dict)` is called once, only if the
    user clicks Bake (not Cancel)."""

    def __init__(self, parent, title, slider_specs, build_pieces_fn, on_bake, on_close):
        self._build_pieces_fn = build_pieces_fn
        self._on_bake = on_bake
        self._slider_specs = list(slider_specs)
        self._vars = {}
        self._specs = {}
        self._last_values = {}
        super().__init__(parent, title, on_close)

    def _build_sidebar(self, sidebar):
        row = 0
        for spec in self._slider_specs:
            var = tk.DoubleVar(value=spec.default)
            self._vars[spec.name] = var
            self._specs[spec.name] = spec
            self._last_values[spec.name] = spec.default
            row = self._add_slider(sidebar, row, spec, var)

    def _build_scene(self):
        return self._build_pieces_fn(self._values())

    def _add_slider(self, parent, row, spec, var):
        ttk.Label(parent, text=f"{spec.label}  [{spec.lo:g}-{spec.hi:g}]").grid(
            row=row, column=0, columnspan=2, sticky="w")
        row += 1
        entry = ttk.Entry(parent, textvariable=var, width=8)
        entry.grid(row=row, column=1, sticky="e")

        def on_drag(v):
            var.set(round(float(v), spec.decimals))

        scale = ttk.Scale(parent, from_=spec.lo, to=spec.hi, variable=var,
                           orient="horizontal", command=on_drag)
        scale.grid(row=row, column=0, sticky="ew")
        row += 1
        var.trace_add("write", lambda *_a: self._redraw())
        return row

    def _values(self):
        # A shared Entry/Scale variable can be transiently unparseable
        # mid-keystroke (e.g. a bare "-" or an emptied field) and typing
        # directly into the Entry isn't clamped to the Scale's [lo, hi] the
        # way dragging the Scale is (e.g. typing "0" for a bend-radius ratio
        # would otherwise reach build_pieces_fn as a literal zero and blow up
        # duct_meshes.fillet_polyline on a zero-length segment) - so fall
        # back to the last good value on a parse error, then clamp into
        # range, same defensive pattern as gui/app.py's own _on_control_change.
        values = {}
        for name, var in self._vars.items():
            spec = self._specs[name]
            try:
                v = float(var.get())
            except (ValueError, tk.TclError):
                v = self._last_values[name]
            v = min(max(v, spec.lo), spec.hi)
            values[name] = v
        self._last_values = values
        return values

    def _bake(self):
        self._on_bake(self._values())
        self._on_close()


def _manifold_build_pieces(values):
    pieces = shape_lab_geometry.build_manifold_test_pieces(
        intake_angle_deg=values["intake_to_manifold_angle_deg"],
        bend_radius_tube_dia_mult=values["bend_radius_tube_dia_mult"],
        rotation_deg=values["rotation_deg"])
    flat = [pieces["ring"]] + list(pieces["duct"])
    half = shape_lab_geometry.SYNTHETIC_RING_MAJOR_R_M * 1.6
    return {"pieces": flat, "center": (0.0, 0.0, 0.0), "half": half}


MANIFOLD_SLIDER_SPECS = [
    SliderSpec("intake_to_manifold_angle_deg", "Intake-to-manifold angle [deg]",
               0.0, 90.0, 45.0, decimals=1),
    SliderSpec("bend_radius_tube_dia_mult", "Bend radius : pipe diameter",
               0.5, 5.0, 0.5, decimals=2),
    SliderSpec("rotation_deg", "Rotational angle [deg]", 0.0, 360.0, 0.0, decimals=1),
]


def open_manifold_shape_lab(parent_app):
    """Synthetic-ring FALLBACK lab (no design-side effect - the three legacy
    sliders are preview-only since schema 4; Bake just closes the panel)."""
    parent_app._enter_shape_lab(lambda parent, on_close: ShapeLabPanel(
        parent, "Shape Lab - synthetic manifold / intake duct (preview only)",
        MANIFOLD_SLIDER_SPECS, _manifold_build_pieces, on_bake=lambda values: None,
        on_close=on_close))


# ---------------------------------------------------------------------------
# Procedural plumbing editor
# ---------------------------------------------------------------------------

@dataclass
class _Ctl:
    """One numeric control: a tk.DoubleVar shared by an Entry + Scale, with
    its clamp range and the last parseable value (same defensive pattern as
    ShapeLabPanel._values / gui/app.py's _on_control_change)."""
    var: tk.DoubleVar
    lo: float
    hi: float
    last: float
    scale: ttk.Scale = None
    entry: ttk.Entry = None


class PlumbingLabPanel(_ShapeLabBase):
    """Editor for one physics/plumbing.py PlumbingRun rooted on a real ring
    (see module docstring). `run` is edited IN PLACE (pass a copy if the
    caller wants Cancel to be lossless - open_plumbing_shape_lab does);
    `on_bake(run)` is called only on Bake."""

    def __init__(self, parent, title, run, hook, ring_center_r_m, ring_tube_r_m, host,
                 wall_profile, on_bake, on_close, ghost_turbopump=None, supercritical=False,
                 pump_port=None, propellant_pair=""):
        self.run = run
        # design.py's turbopump_ports discharge dict for HOST_PUMP[host] (None
        # without a turbopump): the connect_to_pump target / Route-to-pump goal.
        self._pump_port = pump_port
        self._pair = propellant_pair
        self._supercritical = supercritical   # LH2: no SP-8087 liquid-velocity advisory
        self._hook = hook
        self._ring_r = ring_center_r_m
        self._tube_r = ring_tube_r_m
        self._host = host
        self._wall_profile = wall_profile
        # shape_lab_geometry.ghost_turbopump_from_result(result), or None for
        # a design with no turbopump (pressure-fed) - then no ghost, no ray.
        self._ghost_turbopump = ghost_turbopump
        self._on_bake_cb = on_bake
        self._selected = 0 if run.pipes else -1
        self._syncing = False
        self._ctls = {}
        self._bools = {}
        super().__init__(parent, title, on_close)

    # --- sidebar -----------------------------------------------------------
    def _build_sidebar(self, sidebar):
        r = self.run
        row = 0
        run_box = ttk.LabelFrame(
            sidebar, text=f"{plumbing.HOST_LABELS.get(r.host, r.host)} [{r.role}]", padding=6)
        run_box.grid(row=row, column=0, sticky="ew"); row += 1
        rr = 0
        rr = self._add_ctl(run_box, rr, "attach_angle_deg", "Position around engine axis [deg]",
                           0.0, 360.0, r.attach_angle_deg, 1)
        rr = self._add_ctl(run_box, rr, "attach_poloidal_deg",
                           "Position around ring tube [deg] (0 out, 90 fwd)", 0.0, 360.0,
                           r.attach_poloidal_deg, 1)
        rr = self._add_bool(run_box, rr, "flange_at_root", "Flange at manifold joint",
                            r.flange_at_root)
        rr = self._add_ctl(run_box, rr, "flange_lip_dia_mult", "Flange lip height [x pipe dia]",
                           0.0, plumbing.FLANGE_LIP_DIA_MULT_MAX, r.flange_lip_dia_mult, 2)
        rr = self._add_ctl(run_box, rr, "flange_width_dia_mult", "Flange width [x pipe dia]",
                           0.0, plumbing.FLANGE_WIDTH_DIA_MULT_MAX, r.flange_width_dia_mult, 2)
        ttk.Label(run_box, text="Flange bolts (0 = auto)").grid(row=rr, column=0, sticky="w")
        self._bolt_var = tk.IntVar(value=int(r.flange_bolt_count))
        ttk.Spinbox(run_box, from_=0, to=plumbing.FLANGE_BOLT_MAX_COUNT, width=5,
                    textvariable=self._bolt_var, command=self._on_change).grid(
            row=rr, column=1, sticky="e")
        self._bolt_var.trace_add("write", lambda *_a: self._on_change())
        rr += 1

        # --- pump connection (auto-close onto the turbopump discharge port) ---
        pump_name = plumbing.HOST_PUMP.get(r.host, "fuel_pump").replace("_", " ")
        pump_box = ttk.LabelFrame(sidebar, text=f"Pump connection ({pump_name} discharge)",
                                  padding=6)
        pump_box.grid(row=row, column=0, sticky="ew", pady=(8, 0)); row += 1
        pr = 0
        can_connect = self._pump_port is not None and r.host in plumbing.CONNECTABLE_HOSTS
        pr = self._add_bool(pump_box, pr, "connect_to_pump",
                            "Connect to pump (last 2 legs auto-close on the port)",
                            r.connect_to_pump and can_connect)
        pr = self._add_ctl(pump_box, pr, "port_standoff_dia_mult",
                           "Straight entry into port [x port bore]",
                           plumbing.PORT_STANDOFF_DIA_MULT_MIN, plumbing.PORT_STANDOFF_DIA_MULT_MAX,
                           r.port_standoff_dia_mult, 2)
        self._route_btn = ttk.Button(pump_box, text="Route to pump (replaces pipes)",
                                     command=self._route_to_pump)
        self._route_btn.grid(row=pr, column=0, columnspan=2, sticky="w"); pr += 1
        if not can_connect:
            why = ("a turnaround ring never connects to a pump"
                   if r.host not in plumbing.CONNECTABLE_HOSTS else "no turbopump in this design")
            self._connect_check.state(["disabled"])
            self._route_btn.state(["disabled"])
            self._set_ctl_enabled("port_standoff_dia_mult", False)
            ttk.Label(pump_box, text=f"({why})", foreground="#666666").grid(
                row=pr, column=0, columnspan=2, sticky="w"); pr += 1

        seg_box = ttk.LabelFrame(sidebar, text="Pipe segments", padding=6)
        seg_box.grid(row=row, column=0, sticky="ew", pady=(8, 0)); row += 1
        sr = 0
        ttk.Label(seg_box, text="Selected pipe").grid(row=sr, column=0, sticky="w")
        self._seg_combo = ttk.Combobox(seg_box, state="readonly", width=10, values=[])
        self._seg_combo.grid(row=sr, column=1, sticky="e")
        self._seg_combo.bind("<<ComboboxSelected>>", self._on_select_segment)
        sr += 1
        btns = ttk.Frame(seg_box)
        btns.grid(row=sr, column=0, columnspan=2, sticky="ew"); sr += 1
        ttk.Button(btns, text="Add pipe", command=self._add_pipe).pack(side=tk.LEFT)
        ttk.Button(btns, text="Remove last", command=self._remove_last).pack(side=tk.LEFT, padx=4)
        sr = self._add_ctl(seg_box, sr, "length_dia_mult", "Length [x pipe dia]",
                           plumbing.PIPE_LENGTH_DIA_MULT_MIN, plumbing.PIPE_LENGTH_DIA_MULT_MAX,
                           3.0, 2)
        sr = self._add_ctl(seg_box, sr, "yaw_deg", "Yaw vs. previous pipe [deg]",
                           -plumbing.PIPE_TURN_DEG_MAX, plumbing.PIPE_TURN_DEG_MAX, 0.0, 1)
        sr = self._add_ctl(seg_box, sr, "pitch_deg", "Pitch vs. previous pipe [deg]",
                           -plumbing.PIPE_TURN_DEG_MAX, plumbing.PIPE_TURN_DEG_MAX, 0.0, 1)
        sr = self._add_ctl(seg_box, sr, "bend_radius_dia_mult", "Elbow radius at start [x pipe dia]",
                           plumbing.BEND_RADIUS_DIA_MULT_MIN, plumbing.BEND_RADIUS_DIA_MULT_MAX,
                           0.5, 2)
        # Each pipe's own bore (a reducer cones between bores; pipe 1 starts
        # at the ring's inlet bore) - 1.0 = the ring's design velocity.
        sr = self._add_ctl(seg_box, sr, "bore_scale", "Bore [x full-flow feed bore]",
                           plumbing.PIPE_BORE_SCALE_MIN, plumbing.PIPE_BORE_SCALE_MAX, 1.0, 2)
        sr = self._add_bool(seg_box, sr, "flange_at_end", "Flange at this pipe's end", False)
        self._pipe_dia_label = ttk.Label(seg_box, text="")
        self._pipe_dia_label.grid(row=sr, column=0, columnspan=2, sticky="w"); sr += 1

        view_box = ttk.LabelFrame(sidebar, text="View", padding=6)
        view_box.grid(row=row, column=0, sticky="ew", pady=(8, 0)); row += 1
        self._ghost_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(view_box, text="Ghost chamber wall", variable=self._ghost_var,
                        command=self._redraw).grid(row=0, column=0, sticky="w")
        self._tp_var = tk.BooleanVar(value=self._ghost_turbopump is not None)
        tp_check = ttk.Checkbutton(view_box, text="Ghost turbopump (+ ray when not connected)",
                                   variable=self._tp_var, command=self._redraw)
        tp_check.grid(row=1, column=0, sticky="w")
        if self._ghost_turbopump is None:
            tp_check.state(["disabled"])
            ttk.Label(view_box, text="(no turbopump in this design)",
                      foreground="#666666").grid(row=2, column=0, sticky="w")

        self._advisory = ttk.Label(sidebar, text="", wraplength=300, justify="left",
                                   foreground="#a04000")
        self._advisory.grid(row=row, column=0, sticky="ew", pady=(8, 0)); row += 1
        self._summary = ttk.Label(sidebar, text="", wraplength=300, justify="left")
        self._summary.grid(row=row, column=0, sticky="ew"); row += 1

        self._refresh_segment_list()
        self._load_selected_into_vars()

    def _add_ctl(self, parent, row, name, label, lo, hi, default, decimals):
        ttk.Label(parent, text=f"{label}  [{lo:g}-{hi:g}]").grid(
            row=row, column=0, columnspan=2, sticky="w")
        row += 1
        var = tk.DoubleVar(value=default)
        entry = ttk.Entry(parent, textvariable=var, width=8)
        entry.grid(row=row, column=1, sticky="e")

        def on_drag(v):
            var.set(round(float(v), decimals))

        scale = ttk.Scale(parent, from_=lo, to=hi, variable=var, orient="horizontal",
                          command=on_drag)
        scale.grid(row=row, column=0, sticky="ew")
        row += 1
        self._ctls[name] = _Ctl(var=var, lo=lo, hi=hi, last=default, scale=scale, entry=entry)
        var.trace_add("write", lambda *_a: self._on_change())
        return row

    def _add_bool(self, parent, row, name, label, default):
        var = tk.BooleanVar(value=bool(default))
        check = ttk.Checkbutton(parent, text=label, variable=var, command=self._on_change)
        check.grid(row=row, column=0, columnspan=2, sticky="w")
        self._bools[name] = var
        if name == "connect_to_pump":
            self._connect_check = check
        return row + 1

    def _ctl_value(self, name):
        c = self._ctls[name]
        try:
            v = float(c.var.get())
        except (ValueError, tk.TclError):
            v = c.last
        v = min(max(v, c.lo), c.hi)
        c.last = v
        return v

    def _set_ctl(self, name, value):
        self._ctls[name].last = float(value)
        self._ctls[name].var.set(float(value))

    def _set_ctl_enabled(self, name, enabled):
        flags = ["!disabled"] if enabled else ["disabled"]
        self._ctls[name].scale.state(flags)
        self._ctls[name].entry.state(flags)

    # --- segment list -----------------------------------------------------
    def _refresh_segment_list(self):
        names = [f"Pipe {i + 1}" for i in range(len(self.run.pipes))]
        self._seg_combo.configure(values=names)
        if not names:
            self._selected = -1
            self._seg_combo.set("")
        else:
            self._selected = min(max(self._selected, 0), len(names) - 1)
            self._seg_combo.current(self._selected)

    def _load_selected_into_vars(self):
        """Push the selected pipe's fields into the segment sliders without
        triggering _on_change writes back into the run (self._syncing)."""
        self._syncing = True
        try:
            k = self._selected
            if k < 0:
                for name in ("length_dia_mult", "yaw_deg", "pitch_deg", "bend_radius_dia_mult",
                             "bore_scale"):
                    self._set_ctl_enabled(name, False)
                self._bools["flange_at_end"].set(False)
                return
            p = self.run.pipes[k]
            self._set_ctl("length_dia_mult", p.length_dia_mult)
            self._set_ctl("yaw_deg", p.yaw_deg)
            self._set_ctl("pitch_deg", p.pitch_deg)
            self._set_ctl("bend_radius_dia_mult", p.bend_radius_dia_mult)
            self._set_ctl("bore_scale", p.bore_scale)
            self._bools["flange_at_end"].set(p.flange_at_end)
            # Pipe 1 leaves along the torus normal - no elbow, no turn.
            self._set_ctl_enabled("length_dia_mult", True)
            self._set_ctl_enabled("bore_scale", True)
            for name in ("yaw_deg", "pitch_deg", "bend_radius_dia_mult"):
                self._set_ctl_enabled(name, k > 0)
        finally:
            self._syncing = False

    def _on_select_segment(self, _event=None):
        idx = self._seg_combo.current()
        if idx >= 0:
            self._selected = idx
            self._load_selected_into_vars()
            self._redraw()

    def _add_pipe(self):
        prev = self.run.pipes[-1] if self.run.pipes else None
        role = prev.role if prev else plumbing.default_run_for_host(
            self._hook, self._tube_r, self._host).pipes[0].role
        self.run.pipes.append(plumbing.PipeSegment(role=role))
        self._selected = len(self.run.pipes) - 1
        self._refresh_segment_list()
        self._load_selected_into_vars()
        self._redraw()

    def _remove_last(self):
        if not self.run.pipes:
            return
        self.run.pipes.pop()
        self._refresh_segment_list()
        self._load_selected_into_vars()
        self._redraw()

    def _route_to_pump(self):
        """Replace the run's pipes with plumbing.seed_route_to_port's editable
        orthogonal seed (connect_to_pump on - the auto legs finish it)."""
        if self._pump_port is None:
            return
        if self.run.pipes and not messagebox.askyesno(
                "Route to pump", "Replace the current pipes with an auto-routed line to the "
                                 "pump? (Cancel/close the Lab without Bake to undo.)"):
            return
        seed = plumbing.seed_route_to_port(self._hook, self._pump_port, self._ring_r, self._tube_r,
                                           self._host)
        r = self.run
        r.attach_angle_deg, r.attach_poloidal_deg = seed.attach_angle_deg, seed.attach_poloidal_deg
        r.connect_to_pump, r.port_standoff_dia_mult = True, seed.port_standoff_dia_mult
        r.pipes = seed.pipes
        self._syncing = True
        try:
            self._set_ctl("attach_angle_deg", r.attach_angle_deg)
            self._set_ctl("attach_poloidal_deg", r.attach_poloidal_deg)
            self._set_ctl("port_standoff_dia_mult", r.port_standoff_dia_mult)
            self._bools["connect_to_pump"].set(True)
        finally:
            self._syncing = False
        self._selected = 0
        self._refresh_segment_list()
        self._load_selected_into_vars()
        self._redraw()

    # --- model sync + scene -----------------------------------------------
    def _on_change(self):
        if self._syncing:
            return
        r = self.run
        r.attach_angle_deg = self._ctl_value("attach_angle_deg")
        r.attach_poloidal_deg = self._ctl_value("attach_poloidal_deg")
        r.flange_at_root = bool(self._bools["flange_at_root"].get())
        r.flange_lip_dia_mult = self._ctl_value("flange_lip_dia_mult")
        r.flange_width_dia_mult = self._ctl_value("flange_width_dia_mult")
        try:
            r.flange_bolt_count = max(0, int(self._bolt_var.get()))
        except (ValueError, tk.TclError):
            pass
        r.connect_to_pump = (bool(self._bools["connect_to_pump"].get())
                             and self._pump_port is not None
                             and r.host in plumbing.CONNECTABLE_HOSTS)
        r.port_standoff_dia_mult = self._ctl_value("port_standoff_dia_mult")
        k = self._selected
        if k >= 0:
            p = r.pipes[k]
            p.length_dia_mult = self._ctl_value("length_dia_mult")
            p.bore_scale = self._ctl_value("bore_scale")
            if k > 0:
                p.yaw_deg = self._ctl_value("yaw_deg")
                p.pitch_deg = self._ctl_value("pitch_deg")
                p.bend_radius_dia_mult = self._ctl_value("bend_radius_dia_mult")
            p.flange_at_end = bool(self._bools["flange_at_end"].get())
        self._redraw()

    def _build_scene(self):
        scene = shape_lab_geometry.build_plumbing_scene(
            self.run, self._hook, self._ring_r, self._tube_r, host=self._host,
            selected_index=self._selected if self._selected >= 0 else None,
            wall_profile=self._wall_profile,
            show_ghost_wall=bool(self._ghost_var.get()) if hasattr(self, "_ghost_var") else True,
            ghost_turbopump=self._ghost_turbopump,
            show_ghost_turbopump=bool(self._tp_var.get()) if hasattr(self, "_tp_var") else True,
            supercritical=self._supercritical,
            port=self._pump_port if self.run.connect_to_pump else None)
        res = scene["resolved"]
        if hasattr(self, "_advisory"):
            self._advisory.configure(text="\n".join(res["advisories"]))
            mass, _, _ = plumbing.plumbing_mass_kg(self._hook, res)
            ray_txt = ""
            if scene["ray_target"] is not None:
                ray_txt = (f", ray to {scene['ray_target'].replace('_', ' ')}: "
                           f"{scene['ray_length_m']:.2f} m")
            loss, _parts = plumbing.run_pressure_loss_pa(
                res, self._hook, plumbing.liquid_viscosity_pa_s(self._pair, self._host))
            n_auto = len(res["auto_leg_indices"])
            auto_txt = f" + {n_auto} auto leg(s) to the pump" if n_auto else ""
            loss_txt = (f"\nLine loss {loss / 1e3:.0f} kPa (pipes, elbows, reducers, ring entry"
                        + ("; design.py adds a valve allowance and feeds it to the pump dP)"
                           if res["closes_on_port"] else "; used by the pump only once connected)"))
            self._summary.configure(
                text=f"{len(self.run.pipes)} pipe(s){auto_txt}, {res['total_length_m']:.2f} m, "
                     f"~{mass:.1f} kg incl. {sum(j['flange'] for j in res['joint_frames'])} flange(s)"
                     f"{ray_txt}{loss_txt}")
            k = self._selected
            if 0 <= k < len(res["pipe_radii_m"]):
                self._pipe_dia_label.configure(
                    text=f"Pipe {k + 1}: {2000.0 * res['pipe_radii_m'][k]:.0f} mm bore, "
                         f"{res['pipe_velocities_ms'][k]:.1f} m/s (ring inlet bore "
                         f"{2000.0 * res['root_flow_radius_m']:.0f} mm)")
            else:
                self._pipe_dia_label.configure(text="")
        return scene

    def _bake(self):
        self._on_bake_cb(self.run)
        self._on_close()


def open_plumbing_shape_lab(parent_app, host="jacket_inlet"):
    """Switch `parent_app` (gui.app.EngineDesignerApp) into the plumbing
    editor for the run rooted on `host` (the jacket-inlet ring by default).
    Seeds from the design's existing run on that host, else from
    plumbing.default_run_for_host (= the legacy auto-drawn duct). Bake
    replaces that host's run in design.plumbing_runs and recomputes. If the
    current design has no such ring (no regen jacket), explains why and
    opens the synthetic fallback lab instead."""
    if parent_app.last_result is None:
        parent_app.recompute()
    result = parent_app.last_result
    ring = shape_lab_geometry.host_ring_from_result(result, host) if result else None
    label = plumbing.HOST_LABELS.get(host, host)
    if ring is None:
        hint = plumbing.HOST_MISSING_HINT.get(host, "unknown host")
        messagebox.showinfo(
            "Shape Lab",
            f"This design has no {label} to root a pipe run on ({hint}). Opening the "
            f"synthetic preview-only lab instead - nothing will bake onto the engine.")
        open_manifold_shape_lab(parent_app)
        return
    hook, ring_r, tube_r = ring
    existing = plumbing.runs_for_host(parent_app.design.plumbing_runs, host)
    run = (plumbing.run_from_dict(existing[0]) if existing
           else plumbing.default_run_for_host(hook, tube_r, host))
    wall_profile = (result["profile_xs_m"], result["profile_rs_m"])
    ghost_turbopump = shape_lab_geometry.ghost_turbopump_from_result(result)
    pump_port = ((result.get("turbopump_ports") or {})
                 .get(plumbing.HOST_PUMP.get(host, "fuel_pump")) or {}).get("discharge")

    def on_bake(baked_run):
        kept = [r for r in parent_app.design.plumbing_runs
                if (r or {}).get("host") != host]
        parent_app.design.plumbing_runs = kept + [plumbing.run_to_dict(baked_run)]
        parent_app.recompute()

    parent_app._enter_shape_lab(lambda parent, on_close: PlumbingLabPanel(
        parent, f"Shape Lab - {label} plumbing (real ring, real scale)", run, hook, ring_r, tube_r,
        host, wall_profile, on_bake=on_bake, on_close=on_close,
        ghost_turbopump=ghost_turbopump,
        supercritical=(result.get("inputs", {}).get("propellant_pair") == "LOX/LH2"
                       and host != "ox"),
        pump_port=pump_port, propellant_pair=result.get("inputs", {}).get("propellant_pair", "")))


if __name__ == "__main__":
    import ast
    from pathlib import Path
    # No $DISPLAY in this sandbox (Tkinter/matplotlib-3D window), and
    # PyOpenGL/pyopengltk aren't installed either - syntax-only, same
    # treatment as gui/preview3d_gl.py's own __main__ note. Run this for
    # real (python3 -m engine_designer.gui.app, then "Open Shape Lab...")
    # and report back whether the sliders/preview/Bake behave as expected,
    # and which renderer (GL or matplotlib fallback) actually loads.
    ast.parse(Path(__file__).read_text())
    print("shape_lab.py syntax OK (Tk/GL/matplotlib-3D window not exercised - no $DISPLAY here)")
