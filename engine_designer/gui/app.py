"""
Tkinter + embedded-matplotlib GUI: dropdowns/sliders on the left, a live
schematic + numeric readouts on the right, an Export button that writes a
RealFuels .cfg.

Every slider is paired with a typable entry box bound to the SAME
tk.DoubleVar as the ttk.Scale (not a second, separately-synced variable) -
typing a value and hitting Enter or tabbing out moves the slider; dragging
the slider updates the displayed number. A `trace_add("write", ...)` on
each shared variable is what unifies both input paths into one recompute
trigger (a Scale's own `command` only fires on direct interaction with the
scale, not when some other widget writes to the shared variable - the
trace fires on every write regardless of source).

IMPORTANT: this needs a real display (X11/Wayland/Windows/macOS desktop).
The sandbox this was built in has no $DISPLAY, so this file could only be
syntax-checked and code-reviewed here, NOT interactively run - launch it on
your own machine and tell me if anything misbehaves (the Entry/Scale sync
is the part most worth double-checking).

Run via:  python3 -m engine_designer.gui.app   (from /home/cory/ksp_config)
"""
import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from ..catalog import load_roengines_models
from ..export.cfg_writer import write_cfg
from ..physics import (combustion, controller_tech, cooling, cost_model, cycles, ignition,
                        hatbands, injectors, materials, mixture_ratio, plumbing, reliability,
                        tech_tree,
                        turbopump_materials, turbopump_sizing, turbopump_tech)
from ..physics.design import EngineDesign
from . import project_io
from .collapsible import CollapsibleSection
from .injector_face import draw_injector_face
from .schematic import draw_schematic
from .turbopump_diagram import draw_turbopump_diagram

# 3D preview: prefer the GPU-rendered OpenGL widget (real-time orbit camera);
# fall back to the older matplotlib renderer if PyOpenGL/pyopengltk aren't
# installed (see requirements.txt) or the GL widget fails to construct.
# Neither path is exercised in this project's dev sandbox (no $DISPLAY, and
# the GL packages aren't installed there either) - see preview3d_gl.py's
# module docstring.
try:
    from .preview3d_gl import EnginePreviewGLFrame
    from .preview3d_gl_core import XRAY_DEFAULT_OPACITY
    from .flow_legend import FlowLegend
    _GL_PREVIEW_AVAILABLE = True
except ImportError:
    from .preview3d import draw_3d_preview
    _GL_PREVIEW_AVAILABLE = False

# Shape Lab: an in-window context switch for interactive shape editing
# (the procedural plumbing editor on any manifold ring, with a synthetic
# fallback), opened per host from the Plumbing tab. Needs Tkinter's mplot3d
# toolkit; guarded the same way as the GL preview import above so a missing/
# broken matplotlib 3D toolkit disables just the tab's Edit buttons instead
# of the app.
try:
    from .shape_lab import open_plumbing_shape_lab
    from .shape_lab_geometry import PLUMBING_HOST_RGB
    _SHAPE_LAB_AVAILABLE = True
except ImportError:
    _SHAPE_LAB_AVAILABLE = False
    PLUMBING_HOST_RGB = {}

CATALOG_PATH = Path(__file__).resolve().parents[1] / "catalog" / "catalog.json"

NOZZLE_TYPE_DISPLAY = {"conical": "Conical", "bell": "Bell (Rao parabolic)"}
NOZZLE_TYPE_FROM_DISPLAY = {v: k for k, v in NOZZLE_TYPE_DISPLAY.items()}

# Single source of truth for cycle names lives in physics/cycles.py (shared
# with the .cfg header text in export/cfg_writer.py, so they can't drift).
CYCLE_DISPLAY = cycles.CYCLE_DISPLAY
CYCLE_FROM_DISPLAY = {v: k for k, v in CYCLE_DISPLAY.items()}

GIMBAL_MODE_DISPLAY = {"inherit": "Inherit from host part", "custom": "Custom",
                        "ungimballed": "Ungimballed"}
GIMBAL_MODE_FROM_DISPLAY = {v: k for k, v in GIMBAL_MODE_DISPLAY.items()}

# How the exported .cfg is shaped (export/cfg_writer.py output_mode).
OUTPUT_MODE_DISPLAY = {
    "additional_config": "Additional CONFIG on host part",
    "new_part_in_place": "New engine - rescale host part in place",
    "new_part_standalone": "New standalone part (borrow host model)",
}
OUTPUT_MODE_FROM_DISPLAY = {v: k for k, v in OUTPUT_MODE_DISPLAY.items()}

# Fixed display order for the Checklist tab's category groups - a category
# with no applicable checks for the current cycle/injector (e.g. "expander"
# when cycle != Expander) simply doesn't appear, same as any other category.
CHECKLIST_CATEGORY_ORDER = ["propellant/cycle", "turbopump", "chamber geometry", "materials",
                            "cooling", "injector", "stability", "ignition", "gimbal",
                            "nozzle/aero", "expander"]


class EngineDesignerApp:
    def __init__(self, root):
        self.root = root
        root.title("RO Engine Designer")
        root.geometry("1200x760")

        self.catalog = self._load_catalog()
        self.roengines_models = load_roengines_models()   # {engine_type: model dims}
        self.design = EngineDesign()
        if self.catalog:
            self.design.host_model_engine_type = self.catalog[0]["engine_type"]

        self.last_result = None
        self._cost_overridden = False   # True once the user edits the cost/entryCost fields
        self._loading = False           # trace-storm guard for New / Load (WS4)
        self._current_project_path = None   # last Saved/Loaded .json (Ctrl+S target)
        self._gated_controls = []       # [(frame, predicate)] - see _register_gate/_apply_gates
        self._shape_lab_panel = None    # active ShapeLabPanel, if any - see _enter/_exit_shape_lab
        self._build_menu()
        self._build_layout()
        self._set_title()
        self.recompute()

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", accelerator="Ctrl+N", command=self._on_new)
        filemenu.add_command(label="Open…", accelerator="Ctrl+O", command=self._on_load)
        filemenu.add_command(label="Save", accelerator="Ctrl+S", command=self._on_save_current)
        filemenu.add_command(label="Save As…", accelerator="Ctrl+Shift+S", command=self._on_save)
        filemenu.add_separator()
        filemenu.add_command(label="Export .cfg…", accelerator="Ctrl+E", command=self._on_export)
        filemenu.add_separator()
        filemenu.add_command(label="Quit", accelerator="Ctrl+Q", command=self.root.destroy)
        menubar.add_cascade(label="File", menu=filemenu)
        for seq, fn in (("<Control-n>", self._on_new), ("<Control-o>", self._on_load),
                        ("<Control-s>", self._on_save_current), ("<Control-S>", self._on_save),
                        ("<Control-e>", self._on_export), ("<Control-q>", self.root.destroy)):
            self.root.bind(seq, lambda _e, f=fn: f())

    def _set_title(self):
        name = Path(self._current_project_path).name if self._current_project_path else None
        self.root.title("RO Engine Designer" + (f" — {name}" if name else ""))

    # ------------------------------------------------------------------ setup
    def _load_catalog(self):
        try:
            return json.loads(CATALOG_PATH.read_text())
        except Exception:
            return []

    def _build_layout(self):
        # --- scrollable left control panel ---
        # A Canvas+Scrollbar container holding an inner ttk.Frame ("left") that
        # every control below is placed into, same recipe Tkinter apps commonly
        # use for a scrollable region (there's no built-in scrollable Frame).
        # Nothing about how any individual control works changes - only what
        # frame it's gridded into - which is why this was the lower-risk choice
        # over a tabbed/two-column restructure.
        container = ttk.Frame(self.root)
        container.pack(side=tk.LEFT, fill=tk.Y)
        self.container = container   # Shape Lab context switch needs to pack_forget/restore this
        left_canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0, width=380)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=left_canvas.yview)
        left = ttk.Frame(left_canvas, padding=10)
        left.columnconfigure(0, weight=1)
        left.columnconfigure(1, weight=0)

        left_window = left_canvas.create_window((0, 0), window=left, anchor="nw")
        left_canvas.configure(yscrollcommand=scrollbar.set)

        def _on_left_configure(_event=None):
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))

        def _on_canvas_configure(event):
            left_canvas.itemconfigure(left_window, width=event.width)

        left.bind("<Configure>", _on_left_configure)
        left_canvas.bind("<Configure>", _on_canvas_configure)

        def _on_mousewheel(event):
            if event.num == 4:       # Linux scroll up
                left_canvas.yview_scroll(-1, "units")
            elif event.num == 5:     # Linux scroll down
                left_canvas.yview_scroll(1, "units")
            else:                    # Windows/Mac
                left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            left_canvas.bind_all(seq, _on_mousewheel)

        left_canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        right = ttk.Frame(self.root, padding=10)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.right = right   # Shape Lab context switch needs to pack_forget/restore this

        row = 0

        # Input controls are grouped into left-side tabs by design concern -
        # Combustion Chamber, Engine Bell, Turbopump, Gimbal, Model - rather
        # than one long scrolling list. Adding a future tab (e.g. a "Cooling"
        # or "Mass" tab) is just another notebook.add(...) block in this same
        # shape; _add_dropdown/_add_slider are parent-agnostic (proven by the
        # right-side tabs already), so they work unchanged inside any tab's
        # own Frame. Readout/Warnings/Export stay OUTSIDE the tabs, below
        # them, since they're relevant regardless of which tab is active.
        input_notebook = ttk.Notebook(left)
        input_notebook.grid(row=row, column=0, columnspan=2, sticky="nsew")
        row += 1

        # --- Combustion Chamber tab ---
        # Grouped into collapsible sections (gui/collapsible.py) rather than one
        # flat stacked list, to cut down on scrolling - CollapsibleSection just
        # hides/shows a body Frame via grid()/grid_remove(), so _add_slider/
        # _add_dropdown work unchanged when pointed at section.body_parent()
        # instead of the tab frame directly. Each section gets its own fresh
        # local row counter starting at 0.
        tab_chamber = ttk.Frame(input_notebook, padding=8)
        input_notebook.add(tab_chamber, text="Combustion Chamber")
        tab_chamber.columnconfigure(0, weight=1)
        tab_chamber.columnconfigure(1, weight=0)
        cc_row = 0

        sec_propellant = CollapsibleSection(tab_chamber, "Propellant & Chamber Pressure")
        sec_propellant.grid(row=cc_row, column=0, columnspan=2, sticky="ew")
        cc_row += 1
        pb = sec_propellant.body_parent()
        p_row = 0

        p_row = self._add_dropdown(pb, p_row, "Propellant pair", "pair_var",
                                    combustion.available_pairs(), self.design.propellant_pair,
                                    on_select=self._on_pair_change)

        self.pc_var = tk.DoubleVar(value=self.design.chamber_pressure_pa / 1e6)
        p_row = self._add_slider(pb, p_row, "Chamber pressure [MPa]", self.pc_var, 0.5, 30.0)

        mr_lo, mr_hi = combustion.mr_bounds(self.design.propellant_pair)
        self.mr_var = tk.DoubleVar(value=self.design.mixture_ratio)
        p_row, self.mr_scale = self._add_slider(pb, p_row, "Mixture ratio", self.mr_var,
                                                  mr_lo, mr_hi, return_scale=True)
        # Isp-vs-MR feedback: a peak-Isp readout + an "Optimize MR" button that
        # jumps the slider to the vacuum-Isp-maximising mixture ratio (within the
        # pair's table range). Disabled for monopropellants (no mixture ratio).
        self.mr_peak_var = tk.StringVar(value="")
        ttk.Label(pb, textvariable=self.mr_peak_var).grid(
            row=p_row, column=0, columnspan=2, sticky="w")
        p_row += 1
        self.optimize_mr_btn = ttk.Button(pb, text="Optimize MR (max vac Isp)",
                                           command=self._on_optimize_mr)
        self.optimize_mr_btn.grid(row=p_row, column=0, columnspan=2, sticky="w")
        p_row += 1

        sec_sizing = CollapsibleSection(tab_chamber, "Chamber Sizing")
        sec_sizing.grid(row=cc_row, column=0, columnspan=2, sticky="ew")
        cc_row += 1
        sb = sec_sizing.body_parent()
        s_row = 0

        self.contraction_var = tk.DoubleVar(value=self.design.contraction_ratio)
        s_row = self._add_slider(sb, s_row, "Contraction ratio", self.contraction_var, 1.3, 6.0)

        self.lstar_var = tk.DoubleVar(value=self.design.lstar_m)
        s_row = self._add_slider(sb, s_row,
                                  "Chamber L* [m] (small engines need ~0.02-0.2, large ~0.9-1.3)",
                                  self.lstar_var, 0.02, 3.0, decimals=3)

        s_row = self._add_dropdown(
            sb, s_row, "Chamber sizing method", "chamber_sizing_method_var",
            ["lstar", "residence_time"], self.design.chamber_sizing_method)
        self.chamber_residence_time_var = tk.DoubleVar(value=self.design.chamber_residence_time_ms)
        s_row = self._add_slider(sb, s_row,
                                  "Target residence time [ms] (0 = auto, residence_time method)",
                                  self.chamber_residence_time_var, 0.0, 20.0, decimals=2)

        self.convergent_angle_var = tk.DoubleVar(value=self.design.convergent_half_angle_deg)
        s_row = self._add_slider(sb, s_row, "Convergent-cone half-angle [deg]",
                                  self.convergent_angle_var, 15.0, 50.0, decimals=1)

        self.chamber_wall_fillet_var = tk.DoubleVar(value=self.design.chamber_wall_fillet_r_over_rt)
        s_row = self._add_slider(sb, s_row,
                                  "Cylinder->cone wall fillet R/Rt (0 = sharp corner)",
                                  self.chamber_wall_fillet_var, 0.0, 3.0, decimals=2)

        self.pc_loss_var = tk.BooleanVar(value=self.design.apply_chamber_pressure_loss)
        ttk.Checkbutton(sb, text="Charge the injector-end Pc rise (low contraction ratio)",
                         variable=self.pc_loss_var, command=self._on_control_change).grid(
            row=s_row, column=0, columnspan=2, sticky="w")
        s_row += 1

        sec_cooling = CollapsibleSection(tab_chamber, "Chamber Material")
        sec_cooling.grid(row=cc_row, column=0, columnspan=2, sticky="ew")
        cc_row += 1
        cb = sec_cooling.body_parent()
        cool_row = 0

        self.material_display_to_key = {
            materials.MATERIALS[k].display_name: k for k in materials.available_materials()
        }
        cool_row = self._add_dropdown(cb, cool_row, "Chamber material", "material_var",
                                       list(self.material_display_to_key.keys()),
                                       materials.MATERIALS[self.design.material_key].display_name, width=34)
        ttk.Label(cb, text="Chamber material details").grid(row=cool_row, column=0, columnspan=2, sticky="w")
        cool_row += 1
        self.material_details = tk.Text(cb, width=40, height=6, state="disabled", wrap="word",
                                         font=("Courier", 9))
        self.material_details.grid(row=cool_row, column=0, columnspan=2, sticky="ew")
        cool_row += 1

        # Chamber-side cooling-flow controls (cooling method, wall construction,
        # jacket topology, regen-channel geometry) now live on their own
        # "Cooling" tab (built below), grouped with nozzle-side cooling rather
        # than split by which physical part they're on.

        # Injector type + its element/acoustics/feed detail now live on their own
        # "Injectors" tab (built below) - the dropdown var self.injector_var is
        # created there.

        sec_ignition = CollapsibleSection(tab_chamber, "Ignition")
        sec_ignition.grid(row=cc_row, column=0, columnspan=2, sticky="ew")
        cc_row += 1
        ib = sec_ignition.body_parent()
        i_row = 0

        self.ignition_display_to_key = {
            ignition.IGNITION_SYSTEMS[k].display_name: k for k in ignition.available_ignition_systems()
        }
        i_row = self._add_dropdown(ib, i_row, "Ignition system", "ignition_var",
                                    list(self.ignition_display_to_key.keys()),
                                    ignition.IGNITION_SYSTEMS[self.design.ignition_system].display_name, width=34)

        # --- Cooling tab ---
        # Consolidates every cooling-FLOW control (method/topology/wall
        # construction/regen-channel geometry/fuel diversion) in one place,
        # ordered top-to-bottom along the actual propellant flow path
        # (chamber -> nozzle-side method/transition -> fuel diversion).
        # Material/part selection (material_var, bell_material_var) stays on
        # the Combustion Chamber / Engine Bell tabs - that's part choice, not
        # cooling flow.
        tab_cooling = ttk.Frame(input_notebook, padding=8)
        input_notebook.add(tab_cooling, text="Cooling")
        tab_cooling.columnconfigure(0, weight=1)
        tab_cooling.columnconfigure(1, weight=0)
        cool_tab_row = 0

        sec_cool_chamber = CollapsibleSection(tab_cooling, "Chamber-Side Cooling")
        sec_cool_chamber.grid(row=cool_tab_row, column=0, columnspan=2, sticky="ew")
        cool_tab_row += 1
        ccb = sec_cool_chamber.body_parent()
        cc2_row = 0

        # Cooling method per section (physics/cooling.resolve_cooling_method). "auto"
        # = infer from the material (historical). Explicit decouples the two.
        # Only the methods the chamber MATERIAL can physically be built for are
        # listed (materials.Material.allowed_cooling_methods - a hard block, see
        # _filter_cooling_dropdowns); film is an overlay under "Fuel Diversion".
        cc2_row = self._add_dropdown(
            ccb, cc2_row, "Chamber cooling method", "chamber_cooling_method_var",
            ["auto"] + list(cooling.COOLING_METHODS), self.design.chamber_cooling_method,
            width=16)
        self.chamber_cooling_hint_var = tk.StringVar(value="")
        ttk.Label(ccb, textvariable=self.chamber_cooling_hint_var, wraplength=260,
                  foreground="#666666").grid(row=cc2_row, column=0, columnspan=2, sticky="w")
        cc2_row += 1
        cc2_row = self._add_dropdown(
            ccb, cc2_row, "Cooled-wall construction", "wall_construction_var",
            list(cooling.WALL_CONSTRUCTIONS), self.design.wall_construction, width=16)

        # Regen-cooling JACKET's own flow topology (physics/manifold.
        # size_jacket_manifolds) - geometry/mass only, distinct from
        # it also picks the 3D tube-drawing style (design.
        # REGEN_CIRCUIT_STYLE_BY_TOPOLOGY).
        cc2_row = self._add_dropdown(
            ccb, cc2_row, "Cooling jacket flow topology", "cooling_flow_topology_var",
            ["single_pass_countercurrent", "f1_split_reverse_flow", "j2_mid_nozzle_inlet"],
            self.design.cooling_flow_topology, width=24)
        self.manifold_bypass_group = ttk.Frame(ccb)
        self.manifold_bypass_group.grid(row=cc2_row, column=0, columnspan=2, sticky="ew")
        cc2_row += 1
        self.manifold_bypass_var = tk.DoubleVar(value=self.design.manifold_bypass_fraction * 100.0)
        self._add_slider(self.manifold_bypass_group, 0, "Jacket bypass fraction [%]",
                          self.manifold_bypass_var, 0.0, 60.0, decimals=0)
        self._register_gate(
            self.manifold_bypass_group,
            lambda: self.cooling_flow_topology_var.get() == "f1_split_reverse_flow")
        # J-2 layout: the mid-nozzle inlet manifold's area ratio (physics/
        # cooling.march_coolant_two_pass - down 1/2-count tubes to the cooled
        # end, back up the full count; the real J-2's 180/360).
        self.jacket_inlet_eps_group = ttk.Frame(ccb)
        self.jacket_inlet_eps_group.grid(row=cc2_row, column=0, columnspan=2, sticky="ew")
        cc2_row += 1
        self.jacket_inlet_eps_var = tk.DoubleVar(value=self.design.jacket_inlet_eps)
        self._add_slider(self.jacket_inlet_eps_group, 0, "J-2 inlet manifold area ratio",
                          self.jacket_inlet_eps_var, 1.0, 60.0, decimals=1)
        self._register_gate(
            self.jacket_inlet_eps_group,
            lambda: self.cooling_flow_topology_var.get() == "j2_mid_nozzle_inlet")

        # --- regenerative coolant-channel design (physics/cooling.py) ---
        # "flat" = the legacy flat 1.6 MPa jacket dP (neutral default). "channels"
        # runs the 1-D coolant march: a real coolant-side wall temp + a real
        # Darcy-Weisbach jacket dP (which feeds pump discharge -> Isp). The three
        # channel knobs are auto (0) unless dragged off zero, and only apply in
        # "channels" mode (gated below - the wrapper frame is grid_remove()d
        # when "flat" is selected).
        cc2_row = self._add_dropdown(
            ccb, cc2_row, "Regen cooling model", "regen_channel_model_var",
            ["flat", "channels"], self.design.regen_channel_model, width=14)

        self.regen_channels_group = ttk.Frame(ccb)
        self.regen_channels_group.grid(row=cc2_row, column=0, columnspan=2, sticky="ew")
        self.regen_channels_group.columnconfigure(0, weight=1)
        self.regen_channels_group.columnconfigure(1, weight=1)
        cc2_row += 1
        rg_left = ttk.Frame(self.regen_channels_group)
        rg_left.grid(row=0, column=0, sticky="new", padx=(0, 4))
        rg_left.columnconfigure(0, weight=1)
        rg_left.columnconfigure(1, weight=0)
        rg_right = ttk.Frame(self.regen_channels_group)
        rg_right.grid(row=0, column=1, sticky="new", padx=(4, 0))
        rg_right.columnconfigure(0, weight=1)
        rg_right.columnconfigure(1, weight=0)
        self.regen_channel_count_var = tk.DoubleVar(value=float(self.design.regen_channel_count))
        self._add_slider(rg_left, 0,
                          "Coolant channels (0=auto)", self.regen_channel_count_var,
                          0.0, 600.0, decimals=0)
        self.regen_channel_aspect_var = tk.DoubleVar(value=self.design.regen_channel_aspect_ratio)
        self._add_slider(rg_right, 0,
                          "Channel aspect h/w (0=auto)", self.regen_channel_aspect_var,
                          0.0, 8.0, decimals=1)
        rg_land = ttk.Frame(self.regen_channels_group)
        rg_land.grid(row=1, column=0, columnspan=2, sticky="ew")
        rg_land.columnconfigure(0, weight=1)
        rg_land.columnconfigure(1, weight=0)
        self.regen_channel_land_var = tk.DoubleVar(value=self.design.regen_channel_land_fraction)
        self._add_slider(rg_land, 0,
                          "Channel land fraction (0 = auto)", self.regen_channel_land_var,
                          0.0, 0.6, decimals=2)
        # Throat coolant velocity the channel height is sized to (0 = per-pair
        # auto, RP-1 35 m/s) - the main lever on the coupled throat wall temp.
        rg_vel = ttk.Frame(self.regen_channels_group)
        rg_vel.grid(row=2, column=0, columnspan=2, sticky="ew")
        rg_vel.columnconfigure(0, weight=1)
        rg_vel.columnconfigure(1, weight=0)
        self.regen_coolant_velocity_var = tk.DoubleVar(value=self.design.regen_coolant_velocity_ms)
        self._add_slider(rg_vel, 0,
                          "Coolant velocity m/s (0 = auto)", self.regen_coolant_velocity_var,
                          0.0, 80.0, decimals=0)
        self._register_gate(self.regen_channels_group,
                             lambda: self.regen_channel_model_var.get() == "channels")

        # 3D-preview-only (tube_wall construction): cover the chamber/throat
        # body with a smooth jacket instead of showing its tubes - no
        # physics/mass effect, purely how the 3D preview renders.
        self.chamber_tube_jacket_var = tk.BooleanVar(value=self.design.chamber_tube_jacket)
        ttk.Checkbutton(ccb, text="Chamber Jacket (hide chamber tubes in 3D preview)",
                         variable=self.chamber_tube_jacket_var,
                         command=self._on_control_change).grid(
            row=cc2_row, column=0, columnspan=2, sticky="w")
        cc2_row += 1

        sec_cool_nozzle = CollapsibleSection(tab_cooling, "Nozzle-Side Cooling")
        sec_cool_nozzle.grid(row=cool_tab_row, column=0, columnspan=2, sticky="ew")
        cool_tab_row += 1
        ncb = sec_cool_nozzle.body_parent()
        nc_row = 0

        nc_row = self._add_dropdown(
            ncb, nc_row, "Nozzle / bell cooling method", "nozzle_cooling_method_var",
            ["auto"] + list(cooling.COOLING_METHODS), self.design.nozzle_cooling_method,
            width=16)
        self.nozzle_cooling_hint_var = tk.StringVar(value="")
        ttk.Label(ncb, textvariable=self.nozzle_cooling_hint_var, wraplength=260,
                  foreground="#666666").grid(row=nc_row, column=0, columnspan=2, sticky="w")
        nc_row += 1
        self.regen_nozzle_end_var = tk.DoubleVar(value=self.design.regen_nozzle_end_eps)
        nc_row = self._add_slider(
            ncb, nc_row,
            "Regen/dump nozzle end [eps] (0 = stop at cooling transition)",
            self.regen_nozzle_end_var, 0.0, 150.0, decimals=1)

        # (The 3D tube-drawing style - single pass / F-1 double pass / J-2 two
        # pass - now follows "Cooling jacket flow topology" automatically:
        # design.REGEN_CIRCUIT_STYLE_BY_TOPOLOGY. No separate dropdown.)

        # Everything in this section is a 3D-preview-only hardware detail that
        # only applies to wall_construction == "tube_wall" (no physics/mass
        # effect either way) - the whole section body is gated as one unit,
        # default-closed since it's the largest, least-frequently-touched
        # group. Hatband count/width are additionally nested-gated on the
        # "Tube hatbands" checkbox within it.
        sec_tube_wall = CollapsibleSection(tab_cooling, "Tube-Wall Hardware", start_open=False)
        sec_tube_wall.grid(row=cool_tab_row, column=0, columnspan=2, sticky="ew")
        cool_tab_row += 1
        twb = sec_tube_wall.body_parent()
        tw_row = 0
        self._register_gate(twb, lambda: self.wall_construction_var.get() == "tube_wall")

        # 3D-preview-only: area ratio where the visual tube count doubles (1
        # tube -> 2), matching a real tube-wall bifurcation (e.g. the F-1's
        # 178->356 split at its 3:1 plane) - can fall anywhere along the
        # profile, including inside the chamber/throat body (as the real
        # F-1's does).
        # Under the J-2 layout the split IS the inlet ring (down tubes join
        # the up tubes there), so the slider is swapped for a note.
        self.tube_split_eps_var = tk.DoubleVar(value=self.design.tube_split_eps)
        tube_split_group = ttk.Frame(twb)
        tube_split_group.grid(row=tw_row, column=0, columnspan=2, sticky="ew")
        tube_split_group.columnconfigure(1, weight=1)
        tw_row += 1
        self._add_slider(tube_split_group, 0, "Tube split area ratio (0 = no split)",
                          self.tube_split_eps_var, 0.0, 150.0, decimals=1)
        self._register_gate(
            tube_split_group,
            lambda: self.cooling_flow_topology_var.get() != "j2_mid_nozzle_inlet")
        tube_split_j2_note = ttk.Label(
            twb, text="J-2 layout: tubes split at the inlet ring (J-2 inlet manifold area ratio).",
            wraplength=320, justify="left")
        tube_split_j2_note.grid(row=tw_row, column=0, columnspan=2, sticky="w")
        tw_row += 1
        self._register_gate(
            tube_split_j2_note,
            lambda: self.cooling_flow_topology_var.get() == "j2_mid_nozzle_inlet")

        # Structural retaining bands ("hatbands", physics/hatbands.py) wrapped
        # round the tube bundle aft of the throat - they carry ALL the nozzle hoop
        # load (SP-8120), are spaced at the allowable unsupported tube span, sized
        # for hoop + ring buckling, and add real dry mass; optionally continued
        # onto the nozzle extension.
        self.tube_hatbands_var = tk.BooleanVar(value=self.design.tube_hatbands)
        ttk.Checkbutton(twb, text="Structural hatbands (retaining bands aft of the throat)",
                         variable=self.tube_hatbands_var,
                         command=self._on_control_change).grid(
            row=tw_row, column=0, columnspan=2, sticky="w")
        tw_row += 1

        self.tube_hatbands_on_extension_var = tk.BooleanVar(
            value=self.design.tube_hatbands_on_extension)
        ttk.Checkbutton(twb, text="Extend hatbands onto nozzle extension",
                         variable=self.tube_hatbands_on_extension_var,
                         command=self._on_control_change).grid(
            row=tw_row, column=0, columnspan=2, sticky="w")
        tw_row += 1

        # Two short sliders side by side (rather than stacked) - cuts vertical
        # space in this already-dense, default-closed section.
        hatband_detail_group = ttk.Frame(twb)
        hatband_detail_group.grid(row=tw_row, column=0, columnspan=2, sticky="ew")
        hatband_detail_group.columnconfigure(0, weight=1)
        hatband_detail_group.columnconfigure(1, weight=1)
        tw_row += 1
        hd_left = ttk.Frame(hatband_detail_group)
        hd_left.grid(row=0, column=0, sticky="new", padx=(0, 4))
        hd_left.columnconfigure(0, weight=1)
        hd_left.columnconfigure(1, weight=0)
        hd_right = ttk.Frame(hatband_detail_group)
        hd_right.grid(row=0, column=1, sticky="new", padx=(4, 0))
        hd_right.columnconfigure(0, weight=1)
        hd_right.columnconfigure(1, weight=0)
        self.tube_hatband_count_var = tk.DoubleVar(value=self.design.tube_hatband_count)
        self._add_slider(
            hd_left, 0, "Hatband count (0 = structural auto)",
            self.tube_hatband_count_var, 0.0, 40.0, decimals=0)
        self.tube_hatband_width_var = tk.DoubleVar(value=self.design.tube_hatband_width_m * 1000.0)
        self._add_slider(
            hd_right, 0, "Hatband width [mm] (0 = auto)",
            self.tube_hatband_width_var, 0.0, 500.0, decimals=0)
        self._register_gate(hatband_detail_group, lambda: bool(self.tube_hatbands_var.get()))

        hatband_shape_group = ttk.Frame(twb)
        hatband_shape_group.grid(row=tw_row, column=0, columnspan=2, sticky="ew")
        hatband_shape_group.columnconfigure(0, weight=1)
        tw_row += 1
        self.hatband_shape_display_to_key = {v: k for k, v in hatbands.BAND_SHAPE_LABELS.items()}
        hs_row = self._add_dropdown(
            hatband_shape_group, 0, "Hatband cross-section", "tube_hatband_shape_var",
            list(hatbands.BAND_SHAPE_LABELS.values()),
            hatbands.BAND_SHAPE_LABELS.get(self.design.tube_hatband_shape,
                                           hatbands.BAND_SHAPE_LABELS["auto"]))
        hs_row = self._add_dropdown(
            hatband_shape_group, hs_row, "Hatband material", "tube_hatband_material_var",
            list(self.material_display_to_key.keys()),
            {v: k for k, v in self.material_display_to_key.items()}.get(
                self.design.tube_hatband_material, next(iter(self.material_display_to_key))))
        self.hatband_summary_label = ttk.Label(hatband_shape_group, text="", wraplength=320,
                                               justify="left")
        self.hatband_summary_label.grid(row=hs_row, column=0, columnspan=2, sticky="w")
        self._register_gate(hatband_shape_group, lambda: bool(self.tube_hatbands_var.get()))

        # Bolted-flange-joint 3D-preview-only hardware detail (has_real_joint
        # gated - a genuine two-material chamber/nozzle-extension joint). No
        # physics/mass effect, same "0 = auto, >0 = exact override" character
        # as the hatband controls just above. Thickness/width side by side,
        # bolt count full-width below.
        flange_group = ttk.Frame(twb)
        flange_group.grid(row=tw_row, column=0, columnspan=2, sticky="ew")
        flange_group.columnconfigure(0, weight=1)
        flange_group.columnconfigure(1, weight=1)
        tw_row += 1
        fl_left = ttk.Frame(flange_group)
        fl_left.grid(row=0, column=0, sticky="new", padx=(0, 4))
        fl_left.columnconfigure(0, weight=1)
        fl_left.columnconfigure(1, weight=0)
        fl_right = ttk.Frame(flange_group)
        fl_right.grid(row=0, column=1, sticky="new", padx=(4, 0))
        fl_right.columnconfigure(0, weight=1)
        fl_right.columnconfigure(1, weight=0)
        self.flange_thickness_var = tk.DoubleVar(value=self.design.flange_thickness_m * 1000.0)
        self._add_slider(
            fl_left, 0, "Flange thickness [mm] (axial, 0=auto)",
            self.flange_thickness_var, 0.0, 100.0, decimals=1)
        self.flange_width_var = tk.DoubleVar(value=self.design.flange_width_m * 1000.0)
        self._add_slider(
            fl_right, 0, "Flange radial width [mm] (0=auto)",
            self.flange_width_var, 0.0, 100.0, decimals=1)
        self.flange_bolt_count_var = tk.DoubleVar(value=self.design.flange_bolt_count)
        tw_row = self._add_slider(
            twb, tw_row, "Bolt count (0 = auto spacing)",
            self.flange_bolt_count_var, 0.0, 150.0, decimals=0)

        sec_cool_transition = CollapsibleSection(tab_cooling, "Cooling Transition")
        sec_cool_transition.grid(row=cool_tab_row, column=0, columnspan=2, sticky="ew")
        cool_tab_row += 1
        ctb = sec_cool_transition.body_parent()
        ct_row = 0

        self.cooling_transition_var = tk.DoubleVar(value=self.design.cooling_transition_eps)
        ct_row = self._add_slider(ctb, ct_row, "Cooling transition (expansion ratio)",
                                   self.cooling_transition_var, 2.0, 150.0, decimals=1)

        sec_cool_fuel = CollapsibleSection(tab_cooling, "Fuel Diversion for Cooling")
        sec_cool_fuel.grid(row=cool_tab_row, column=0, columnspan=2, sticky="ew")
        cool_tab_row += 1
        cfb = sec_cool_fuel.body_parent()
        cf_row = 0

        # Film cooling = an OVERLAY on whatever each section's cooling method is
        # (regen + film, ablative + film, ...), at two independent sites, both fed
        # with post-jacket fuel (physics/design.EngineDesign._film_phi).
        self.film_cooling_var = tk.DoubleVar(value=self.design.film_cooling_fraction * 100.0)
        cf_row = self._add_slider(cfb, cf_row,
                                  "Chamber film curtain [% of fuel flow]", self.film_cooling_var,
                                  0.0, 15.0, decimals=1)
        self.chamber_film_inject_var = tk.DoubleVar(
            value=self.design.chamber_film_inject_area_ratio)
        cf_row = self._add_slider(cfb, cf_row,
                                  "Chamber film injection (0 = injector face; >1 = convergent "
                                  "ring at that area ratio)", self.chamber_film_inject_var,
                                  0.0, 6.0, decimals=2)
        self.nozzle_film_var = tk.DoubleVar(value=self.design.nozzle_film_fraction * 100.0)
        cf_row = self._add_slider(cfb, cf_row,
                                  "Nozzle-extension slot film [% of fuel flow] (Isp cost like "
                                  "dump flow)", self.nozzle_film_var, 0.0, 10.0, decimals=1)
        self.nozzle_film_eps_var = tk.DoubleVar(value=self.design.nozzle_film_inject_eps)
        cf_row = self._add_slider(cfb, cf_row,
                                  "Nozzle film slot area ratio (F-1: 10)", self.nozzle_film_eps_var,
                                  1.5, 150.0, decimals=1)

        self.dump_coolant_group = ttk.Frame(cfb)
        self.dump_coolant_group.grid(row=cf_row, column=0, columnspan=2, sticky="ew")
        cf_row += 1
        self.dump_coolant_fraction_var = tk.DoubleVar(value=self.design.dump_coolant_fraction * 100.0)
        self._add_slider(
            self.dump_coolant_group, 0,
            "Dump coolant fraction [% of fuel] (0 = auto, dump method only)",
            self.dump_coolant_fraction_var, 0.0, 30.0, decimals=1)
        self._register_gate(
            self.dump_coolant_group,
            lambda: self.nozzle_cooling_method_var.get() == "dump")

        # --- Injectors tab ---
        tab_injector = ttk.Frame(input_notebook, padding=8)
        input_notebook.add(tab_injector, text="Injectors")
        tab_injector.columnconfigure(0, weight=1)
        tab_injector.columnconfigure(1, weight=0)
        inj_row = 0

        sec_inj_geom = CollapsibleSection(tab_injector, "Injector Geometry")
        sec_inj_geom.grid(row=inj_row, column=0, columnspan=2, sticky="ew")
        inj_row += 1
        gb2 = sec_inj_geom.body_parent()
        g_row = 0

        self.injector_display_to_key = {
            injectors.INJECTORS[k].display_name: k for k in injectors.available_injectors()
        }
        g_row = self._add_dropdown(gb2, g_row, "Injector type / element pattern",
                                    "injector_var",
                                    list(self.injector_display_to_key.keys()),
                                    injectors.INJECTORS[self.design.injector_type].display_name, width=34)

        g_row = self._add_dropdown(gb2, g_row, "Orifice geometry (Cd)", "orifice_type_var",
                                    list(injectors.CD_BY_ORIFICE_TYPE.keys()),
                                    self.design.orifice_type, width=20)

        self.impingement_var = tk.DoubleVar(value=self.design.impingement_angle_deg)
        g_row = self._add_slider(gb2, g_row, "Impingement included angle [deg]",
                                  self.impingement_var, 15.0, 60.0, decimals=1)

        # Fuel-film cooling now lives on the "Cooling" tab (built above, next
        # to dump coolant fraction - both are fuel diverted for cooling); the
        # manifold feed-velocity slider and the Shape Lab entry point live on
        # the "Plumbing" tab (built below, after Turbopump).

        # --- combustion-stability aids (resolve the acoustic-mode advisory) ---
        sec_stability = CollapsibleSection(tab_injector, "Combustion Stability")
        sec_stability.grid(row=inj_row, column=0, columnspan=2, sticky="ew")
        inj_row += 1
        stb = sec_stability.body_parent()
        st_row = 0

        self.baffles_var = tk.BooleanVar(value=self.design.injector_baffles)
        ttk.Checkbutton(stb, text="Injector-face baffle", variable=self.baffles_var,
                         command=self._on_control_change).grid(row=st_row, column=0, sticky="w")
        baffle_comp_group = ttk.Frame(stb)
        baffle_comp_group.grid(row=st_row, column=1, sticky="e")
        self.baffle_comp_var = tk.StringVar(value=str(self.design.baffle_compartments))
        _bc = ttk.Combobox(baffle_comp_group, textvariable=self.baffle_comp_var, width=5,
                            state="readonly", values=["3", "5", "7", "9"])
        _bc.pack()
        _bc.bind("<<ComboboxSelected>>", self._on_control_change)
        self._register_gate(baffle_comp_group, lambda: bool(self.baffles_var.get()))
        st_row += 1

        self.cavities_var = tk.BooleanVar(value=self.design.acoustic_cavities)
        ttk.Checkbutton(stb, text="Corner Helmholtz cavities", variable=self.cavities_var,
                         command=self._on_control_change).grid(row=st_row, column=0, sticky="w")
        cavity_count_group = ttk.Frame(stb)
        cavity_count_group.grid(row=st_row, column=1, sticky="e")
        self.cavity_count_var = tk.StringVar(value=str(self.design.acoustic_cavity_count))
        _cc = ttk.Spinbox(cavity_count_group, textvariable=self.cavity_count_var, width=5,
                           from_=0, to=48, increment=2, command=self._on_control_change)
        _cc.pack()
        _cc.bind("<Return>", self._on_control_change)
        _cc.bind("<FocusOut>", self._on_control_change)
        self._register_gate(cavity_count_group, lambda: bool(self.cavities_var.get()))
        st_row += 1

        sec_stiffness = CollapsibleSection(tab_injector, "Stiffness & Details")
        sec_stiffness.grid(row=inj_row, column=0, columnspan=2, sticky="ew")
        inj_row += 1
        fb = sec_stiffness.body_parent()
        f_row = 0

        ttk.Label(fb, text="Injector stiffness").grid(row=f_row, column=0, sticky="w")
        self.stiffness_var = tk.StringVar(value=self.design.injector_stiffness)
        _sf = ttk.Combobox(fb, textvariable=self.stiffness_var, width=11,
                            state="readonly", values=["nominal", "stiff", "very_stiff"])
        _sf.grid(row=f_row, column=1, sticky="e")
        _sf.bind("<<ComboboxSelected>>", self._on_control_change)
        f_row += 1

        ttk.Label(fb, text="Element geometry / acoustics / feed pressure").grid(
            row=f_row, column=0, columnspan=2, sticky="w")
        f_row += 1
        self.injector_details = tk.Text(fb, width=40, height=20, state="disabled",
                                         wrap="word", font=("Courier", 9))
        self.injector_details.grid(row=f_row, column=0, columnspan=2, sticky="ew")

        # --- Engine Bell tab ---
        tab_bell = ttk.Frame(input_notebook, padding=8)
        input_notebook.add(tab_bell, text="Engine Bell")
        tab_bell.columnconfigure(0, weight=1)
        tab_bell.columnconfigure(1, weight=0)
        eb_row = 0

        sec_nozzle_shape = CollapsibleSection(tab_bell, "Nozzle Shape")
        sec_nozzle_shape.grid(row=eb_row, column=0, columnspan=2, sticky="ew")
        eb_row += 1
        nsb = sec_nozzle_shape.body_parent()
        ns_row = 0

        ns_row = self._add_dropdown(nsb, ns_row, "Nozzle type", "nozzle_type_var",
                                     list(NOZZLE_TYPE_DISPLAY.values()),
                                     NOZZLE_TYPE_DISPLAY[self.design.nozzle_type])

        self.eps_var = tk.DoubleVar(value=self.design.expansion_ratio)
        ns_row = self._add_slider(nsb, ns_row, "Expansion ratio", self.eps_var, 2.0, 150.0, decimals=1)

        half_angle_group = ttk.Frame(nsb)
        half_angle_group.grid(row=ns_row, column=0, columnspan=2, sticky="ew")
        half_angle_group.columnconfigure(0, weight=1)
        half_angle_group.columnconfigure(1, weight=0)
        ns_row += 1
        self.half_angle_var = tk.DoubleVar(value=self.design.nozzle_half_angle_deg)
        self._add_slider(half_angle_group, 0, "Nozzle half-angle [deg] (conical mode)",
                          self.half_angle_var, 5.0, 30.0, decimals=1)
        self._register_gate(
            half_angle_group,
            lambda: NOZZLE_TYPE_FROM_DISPLAY.get(self.nozzle_type_var.get()) == "conical")

        bell_pct_group = ttk.Frame(nsb)
        bell_pct_group.grid(row=ns_row, column=0, columnspan=2, sticky="ew")
        bell_pct_group.columnconfigure(0, weight=1)
        bell_pct_group.columnconfigure(1, weight=0)
        ns_row += 1
        self.bell_pct_var = tk.DoubleVar(value=self.design.bell_percent_length)
        self._add_slider(bell_pct_group, 0, "Bell % length (bell mode)", self.bell_pct_var,
                          60.0, 100.0, decimals=0)
        self._register_gate(
            bell_pct_group,
            lambda: NOZZLE_TYPE_FROM_DISPLAY.get(self.nozzle_type_var.get()) == "bell")

        # Nozzle-side cooling-flow controls (cooling method, regen nozzle end,
        # regen-circuit style, tube-wall hardware) now live on the "Cooling"
        # tab (built above), grouped with chamber-side cooling.

        sec_bell_material = CollapsibleSection(tab_bell, "Bell Material")
        sec_bell_material.grid(row=eb_row, column=0, columnspan=2, sticky="ew")
        eb_row += 1
        bmb = sec_bell_material.body_parent()
        bm_row = 0

        bm_row = self._add_dropdown(bmb, bm_row,
                                     "Nozzle extension material (past the cooling transition)",
                                     "bell_material_var", list(self.material_display_to_key.keys()),
                                     materials.MATERIALS[self.design.bell_material_key].display_name, width=34)
        ttk.Label(bmb, text="Nozzle extension material details").grid(
            row=bm_row, column=0, columnspan=2, sticky="w")
        bm_row += 1
        self.bell_material_details = tk.Text(bmb, width=40, height=6, state="disabled", wrap="word",
                                              font=("Courier", 9))
        self.bell_material_details.grid(row=bm_row, column=0, columnspan=2, sticky="ew")

        # --- Turbopump tab ---
        tab_turbopump_left = ttk.Frame(input_notebook, padding=8)
        input_notebook.add(tab_turbopump_left, text="Turbopump")
        tab_turbopump_left.columnconfigure(0, weight=1)
        tab_turbopump_left.columnconfigure(1, weight=0)
        tp_row = 0

        tp_row = self._add_dropdown(tab_turbopump_left, tp_row, "Cycle", "cycle_var",
                                     list(CYCLE_DISPLAY.values()), CYCLE_DISPLAY[self.design.cycle])

        # Everything below is meaningless for cycle == pressure-fed (no
        # turbopump at all) - the whole section body is gated as one unit,
        # default-closed since it's the largest group and the cycle dropdown
        # above is what actually matters most often.
        sec_tp_config = CollapsibleSection(tab_turbopump_left, "Turbopump Configuration",
                                            start_open=False)
        sec_tp_config.grid(row=tp_row, column=0, columnspan=2, sticky="ew")
        tp_row += 1
        tcb = sec_tp_config.body_parent()
        tc_row = 0
        self._register_gate(tcb, lambda: CYCLE_FROM_DISPLAY.get(self.cycle_var.get()) != cycles.PRESSURE_FED)

        self.turbopump_display_to_key = {
            turbopump_tech.TURBOPUMP_TECHS[k].display_name: k
            for k in turbopump_tech.available_turbopump_techs()
        }
        # Pump & turbine efficiency is DERIVED from the machinery design
        # (physics/turbopump_efficiency.py); this tier is now only a
        # build-quality / era MULTIPLIER on that derived efficiency.
        tc_row = self._add_dropdown(
            tcb, tc_row, "Build quality (era)", "turbopump_tech_var",
            list(self.turbopump_display_to_key.keys()),
            turbopump_tech.TURBOPUMP_TECHS[self.design.turbopump_tech_key].display_name,
            on_select=self._on_control_change, width=34)

        # Optional manual efficiency overrides: 0 = use the derived value.
        self.eta_pump_fuel_var = tk.DoubleVar(value=self.design.eta_pump_fuel)
        tc_row = self._add_slider(tcb, tc_row, "Fuel pump eta override (0=derived)",
                                   self.eta_pump_fuel_var, 0.0, 0.9, decimals=2)
        self.eta_pump_ox_var = tk.DoubleVar(value=self.design.eta_pump_ox)
        tc_row = self._add_slider(tcb, tc_row, "Ox pump eta override (0=derived)",
                                   self.eta_pump_ox_var, 0.0, 0.9, decimals=2)
        self.specific_power_var = tk.DoubleVar(value=self.design.pump_specific_power_w_kg / 1e3)

        # Architecture (physics/turbopump_sizing.py). "auto" derives from
        # propellant pair + cycle + thrust; an override is the only thing that
        # moves computed dry mass.
        tc_row = self._add_dropdown(
            tcb, tc_row, "Shaft arrangement", "turbopump_arrangement_var",
            ["auto", *turbopump_sizing.ARRANGEMENTS],
            self.design.turbopump_arrangement, width=20)
        tc_row = self._add_dropdown(
            tcb, tc_row, "Turbine staging", "turbine_staging_var",
            ["auto", *turbopump_sizing.TURBINE_STAGINGS],
            self.design.turbine_staging, width=24)

        self.turbopump_material_display_to_key = {
            turbopump_materials.MATERIALS[k].display_name: k
            for k in turbopump_materials.available_turbopump_materials()
        }
        tc_row = self._add_dropdown(
            tcb, tc_row, "Turbopump material", "turbopump_material_var",
            list(self.turbopump_material_display_to_key.keys()),
            turbopump_materials.MATERIALS[self.design.turbopump_material_key].display_name,
            width=34)

        self.bearing_material_display_to_key = {
            turbopump_materials.BEARING_MATERIALS[k].display_name: k
            for k in turbopump_materials.available_bearing_materials()
        }
        tc_row = self._add_dropdown(
            tcb, tc_row, "Bearing material", "bearing_material_var",
            list(self.bearing_material_display_to_key.keys()),
            turbopump_materials.BEARING_MATERIALS[self.design.bearing_material_key].display_name,
            width=34)

        self.suction_limit_var = tk.BooleanVar(value=self.design.enforce_suction_limit)
        ttk.Checkbutton(tcb,
                         text="Enforce suction-specific-speed limit (NPSH required, not "
                              "available - no tank model)",
                         variable=self.suction_limit_var, command=self._on_control_change).grid(
            row=tc_row, column=0, columnspan=2, sticky="w")
        tc_row += 1
        # Vehicle-delivered NPSH at each pump inlet (a user input - no tank
        # model): 0 = not limiting; > 0 caps that pump's rpm at its suction-
        # specific-speed limit (bigger impeller, lower efficiency).
        self.npsh_fuel_var = tk.DoubleVar(value=self.design.npsh_available_fuel_ft)
        tc_row = self._add_slider(tcb, tc_row, "Fuel pump inlet NPSH available [ft] (0 = not limiting)",
                                   self.npsh_fuel_var, 0.0, 300.0, decimals=0)
        self.npsh_ox_var = tk.DoubleVar(value=self.design.npsh_available_ox_ft)
        tc_row = self._add_slider(tcb, tc_row, "Ox pump inlet NPSH available [ft] (0 = not limiting)",
                                   self.npsh_ox_var, 0.0, 300.0, decimals=0)
        # Staged-combustion preburner temperatures - design INPUTS; the turbine PR
        # (hence pump discharge) is solved from them (staged_combustion.py). 0 = the
        # propellant pair's default. Ignored by non-staged cycles.
        self.pb_tin_fr_var = tk.DoubleVar(value=self.design.preburner_tin_k)
        tc_row = self._add_slider(tcb, tc_row,
                                   "Fuel-rich preburner temp [K] (FRSC/FFSC; 0 = pair default)",
                                   self.pb_tin_fr_var, 0.0, 1400.0, decimals=0)
        self.pb_tin_or_var = tk.DoubleVar(value=self.design.ox_preburner_tin_k)
        tc_row = self._add_slider(tcb, tc_row,
                                   "Ox-rich preburner temp [K] (ORSC/FFSC; 0 = pair default)",
                                   self.pb_tin_or_var, 0.0, 1400.0, decimals=0)

        ttk.Label(tcb, text="Turbopump details").grid(row=tc_row, column=0, columnspan=2, sticky="w")
        tc_row += 1
        self.turbopump_details = tk.Text(tcb, width=40, height=12, state="disabled",
                                          wrap="word", font=("Courier", 9))
        self.turbopump_details.grid(row=tc_row, column=0, columnspan=2, sticky="ew")

        # --- Plumbing tab ---
        # Manifold hardware sizing + the per-host procedural pipe runs
        # (physics/plumbing.py, edited in the Shape Lab). One row per
        # plumbing.HOSTS entry; a future host (turbopump ports, a GG exhaust
        # manifold) is one more HOSTS/HOST_LABELS entry and gets its row for free.
        tab_plumbing = ttk.Frame(input_notebook, padding=8)
        input_notebook.add(tab_plumbing, text="Plumbing")
        tab_plumbing.columnconfigure(0, weight=1)
        tab_plumbing.columnconfigure(1, weight=0)
        pl_row = 0

        sec_manifold_sizing = CollapsibleSection(tab_plumbing, "Manifold Sizing")
        sec_manifold_sizing.grid(row=pl_row, column=0, columnspan=2, sticky="ew")
        pl_row += 1
        msb = sec_manifold_sizing.body_parent()
        # Per-ring sizing (physics/manifold.py), one group per ring. Injector-
        # feed rings: velocity head as a % of that leg's own injector dP
        # (manifold.velocity_from_head_fraction). Jacket inlet: a trim on the
        # matched local coolant-passage velocity. Taper everywhere: 0 = constant
        # area, 1 = constant velocity (SP-8087: a real torus lies between).
        # The jacket turnaround collar/band has no sizing knobs.
        msb.columnconfigure(0, weight=1)
        self.fuel_manifold_head_var = tk.DoubleVar(
            value=self.design.fuel_manifold_head_fraction * 100.0)
        self.ox_manifold_head_var = tk.DoubleVar(
            value=self.design.ox_manifold_head_fraction * 100.0)
        self.fuel_manifold_taper_var = tk.DoubleVar(value=self.design.fuel_manifold_taper_blend)
        self.ox_manifold_taper_var = tk.DoubleVar(value=self.design.ox_manifold_taper_blend)
        self.jacket_inlet_taper_var = tk.DoubleVar(value=self.design.jacket_inlet_taper_blend)
        self.jacket_inlet_vmult_var = tk.DoubleVar(value=self.design.jacket_inlet_velocity_mult)
        _ms_groups = (
            ("Fuel injector ring", [
                ("Velocity head [% of fuel injector dP]", self.fuel_manifold_head_var, 1.0, 15.0, 1),
                ("Taper (0 = const. area, 1 = const. velocity)", self.fuel_manifold_taper_var,
                 0.0, 1.0, 2)]),
            ("Ox injector ring", [
                ("Velocity head [% of ox injector dP]", self.ox_manifold_head_var, 1.0, 15.0, 1),
                ("Taper (0 = const. area, 1 = const. velocity)", self.ox_manifold_taper_var,
                 0.0, 1.0, 2)]),
            ("Jacket inlet ring", [
                ("Velocity [x local coolant-passage velocity]", self.jacket_inlet_vmult_var,
                 0.5, 2.0, 2),
                ("Taper (0 = const. area, 1 = const. velocity)", self.jacket_inlet_taper_var,
                 0.0, 1.0, 2)]),
        )
        for _gi, (_title, _sliders) in enumerate(_ms_groups):
            _grp = ttk.LabelFrame(msb, text=_title, padding=4)
            _grp.grid(row=_gi, column=0, columnspan=2, sticky="ew", pady=(0, 4))
            _grp.columnconfigure(1, weight=1)
            _gr = 0
            for _label, _var, _lo, _hi, _dec in _sliders:
                _gr = self._add_slider(_grp, _gr, _label, _var, _lo, _hi, decimals=_dec)

        sec_pipe_runs = CollapsibleSection(tab_plumbing, "Manifold Pipe Runs")
        sec_pipe_runs.grid(row=pl_row, column=0, columnspan=2, sticky="ew")
        pl_row += 1
        prb = sec_pipe_runs.body_parent()
        prb.columnconfigure(1, weight=1)
        self._plumbing_rows = {}
        for pr_row, host in enumerate(plumbing.HOSTS):
            name_cell = ttk.Frame(prb)
            name_cell.grid(row=pr_row, column=0, sticky="w", pady=(2, 2))
            rgb = PLUMBING_HOST_RGB.get(host)
            if rgb is not None:
                swatch = tk.Canvas(name_cell, width=12, height=12, highlightthickness=0)
                swatch.create_rectangle(0, 0, 12, 12, outline="",
                                        fill="#%02x%02x%02x" % tuple(int(round(255 * c)) for c in rgb))
                swatch.pack(side=tk.LEFT, padx=(0, 4))
            ttk.Label(name_cell, text=plumbing.HOST_LABELS[host]).pack(side=tk.LEFT)
            status_var = tk.StringVar(value="Shape Lab unavailable" if not _SHAPE_LAB_AVAILABLE
                                      else "(not computed yet)")
            ttk.Label(prb, textvariable=status_var, wraplength=220, justify="left").grid(
                row=pr_row, column=1, sticky="w", padx=(6, 6))
            edit_btn = ttk.Button(prb, text="Edit in Shape Lab...",
                                  command=lambda h=host: open_plumbing_shape_lab(self, h))
            edit_btn.grid(row=pr_row, column=2, sticky="e")
            clear_btn = ttk.Button(prb, text="Clear run",
                                   command=lambda h=host: self._clear_plumbing_run(h))
            clear_btn.grid(row=pr_row, column=3, sticky="e", padx=(2, 0))
            if not _SHAPE_LAB_AVAILABLE:
                edit_btn.state(["disabled"])
            self._plumbing_rows[host] = {"status": status_var, "edit": edit_btn, "clear": clear_btn}

        # --- Gimbal tab ---
        tab_gimbal = ttk.Frame(input_notebook, padding=8)
        input_notebook.add(tab_gimbal, text="Gimbal")
        tab_gimbal.columnconfigure(0, weight=1)
        tab_gimbal.columnconfigure(1, weight=0)
        gb_row = 0

        sec_gimbal = CollapsibleSection(tab_gimbal, "Gimbal")
        sec_gimbal.grid(row=gb_row, column=0, columnspan=2, sticky="ew")
        gb_row += 1
        gmb = sec_gimbal.body_parent()
        gm_row = 0

        gm_row = self._add_dropdown(gmb, gm_row, "Gimbal mode", "gimbal_mode_var",
                                     list(GIMBAL_MODE_DISPLAY.values()),
                                     GIMBAL_MODE_DISPLAY[self.design.gimbal_mode], width=34)

        gimbal_custom_group = ttk.Frame(gmb)
        gimbal_custom_group.grid(row=gm_row, column=0, columnspan=2, sticky="ew")
        gimbal_custom_group.columnconfigure(0, weight=1)
        gimbal_custom_group.columnconfigure(1, weight=0)
        gm_row += 1
        gc_row = 0
        self.gimbal_range_var = tk.DoubleVar(value=self.design.gimbal_range_deg)
        gc_row = self._add_slider(gimbal_custom_group, gc_row, "Gimbal range [deg]",
                                   self.gimbal_range_var, 2.0, 12.0, decimals=1)
        self.gimbal_response_var = tk.DoubleVar(value=self.design.gimbal_response_speed_deg_s)
        gc_row = self._add_slider(gimbal_custom_group, gc_row,
                                   "Gimbal response speed [deg/s] (0 = unset)",
                                   self.gimbal_response_var, 0.0, 20.0, decimals=1)
        self._register_gate(
            gimbal_custom_group,
            lambda: GIMBAL_MODE_FROM_DISPLAY.get(self.gimbal_mode_var.get()) == "custom")

        # --- Model tab (host part binding + overall performance target + controller) ---
        tab_model = ttk.Frame(input_notebook, padding=8)
        input_notebook.add(tab_model, text="Model")
        tab_model.columnconfigure(0, weight=1)
        tab_model.columnconfigure(1, weight=0)
        md_row = 0

        sec_host = CollapsibleSection(tab_model, "Host & Output")
        sec_host.grid(row=md_row, column=0, columnspan=2, sticky="ew")
        md_row += 1
        hb = sec_host.body_parent()
        h_row = 0

        self.host_display_to_type = {}
        host_values = []
        for e in self.catalog:
            label = f"{e['engine_type']} - {e.get('title') or ''}".strip(" -")
            self.host_display_to_type[label] = e["engine_type"]
            host_values.append(label)
        h_row = self._add_dropdown(hb, h_row,
                                    "Host model (existing RO part to bind onto for export)",
                                    "host_var", host_values, host_values[0] if host_values else "", width=34)

        # --- export output shape ---
        h_row = self._add_dropdown(
            hb, h_row, "Output mode", "output_mode_var",
            list(OUTPUT_MODE_DISPLAY.values()),
            OUTPUT_MODE_DISPLAY[self.design.output_mode], width=34)

        ttk.Label(hb, text="Host model reference height [m] (0 = auto from ROEngines data)").grid(
            row=h_row, column=0, columnspan=2, sticky="w")
        h_row += 1
        self.host_ref_height_var = tk.StringVar(
            value=f"{self.design.host_model_reference_height_m:g}")
        _hrh = ttk.Entry(hb, textvariable=self.host_ref_height_var, width=16)
        _hrh.grid(row=h_row, column=0, sticky="ew")
        _hrh.bind("<Return>", self._on_control_change)
        _hrh.bind("<FocusOut>", self._on_control_change)
        h_row += 1

        sec_identity = CollapsibleSection(tab_model, "New Part Identity")
        sec_identity.grid(row=md_row, column=0, columnspan=2, sticky="ew")
        md_row += 1
        idb = sec_identity.body_parent()
        id_row = 0

        ttk.Label(idb, text="New standalone part: name / title / manufacturer "
                            "(blank = derived from CONFIG name)").grid(
            row=id_row, column=0, columnspan=2, sticky="w")
        id_row += 1
        self.new_part_name_var = tk.StringVar(value=self.design.new_part_name)
        self.new_part_title_var = tk.StringVar(value=self.design.new_part_title)
        self.new_part_mfr_var = tk.StringVar(value=self.design.new_part_manufacturer)
        for _c, _v in ((0, self.new_part_name_var), (1, self.new_part_title_var)):
            _e = ttk.Entry(idb, textvariable=_v)
            _e.grid(row=id_row, column=_c, sticky="ew")
            _e.bind("<KeyRelease>", self._on_export_field_change)
        id_row += 1
        _e = ttk.Entry(idb, textvariable=self.new_part_mfr_var)
        _e.grid(row=id_row, column=0, columnspan=2, sticky="ew")
        _e.bind("<KeyRelease>", self._on_export_field_change)
        id_row += 1

        sec_perf = CollapsibleSection(tab_model, "Performance Targets")
        sec_perf.grid(row=md_row, column=0, columnspan=2, sticky="ew")
        md_row += 1
        pfb = sec_perf.body_parent()
        pf_row = 0

        ttk.Label(pfb, text="Target vacuum thrust [kN]").grid(row=pf_row, column=0, columnspan=2, sticky="w")
        pf_row += 1
        self.thrust_var = tk.StringVar(value=f"{self.design.target_vac_thrust_n/1e3:.1f}")
        thrust_entry = ttk.Entry(pfb, textvariable=self.thrust_var)
        thrust_entry.grid(row=pf_row, column=0, columnspan=2, sticky="ew")
        thrust_entry.bind("<Return>", self._on_control_change)
        thrust_entry.bind("<FocusOut>", self._on_control_change)
        pf_row += 1

        self.throttle_var = tk.DoubleVar(value=self.design.throttle_floor)
        pf_row = self._add_slider(pfb, pf_row, "Throttle floor [fraction of max]",
                                   self.throttle_var, 0.1, 1.0)

        self.controller_display_to_key = {
            controller_tech.CONTROLLER_TECHS[k].display_name: k
            for k in controller_tech.available_controller_techs()
        }
        pf_row = self._add_dropdown(
            pfb, pf_row, "Engine controller/avionics", "controller_var",
            list(self.controller_display_to_key.keys()),
            controller_tech.CONTROLLER_TECHS[self.design.controller_tech_key].display_name, width=34)
        ttk.Label(pfb, text="Controller details").grid(row=pf_row, column=0, columnspan=2, sticky="w")
        pf_row += 1
        self.controller_details = tk.Text(pfb, width=40, height=5, state="disabled", wrap="word",
                                           font=("Courier", 9))
        self.controller_details.grid(row=pf_row, column=0, columnspan=2, sticky="ew")
        pf_row += 1

        sec_ign_mass = CollapsibleSection(tab_model, "Ignitions & Mass")
        sec_ign_mass.grid(row=md_row, column=0, columnspan=2, sticky="ew")
        md_row += 1
        imb = sec_ign_mass.body_parent()
        im_row = 0

        # Number of ignitions: export-time only, like tech_node/entry_cost/cost - doesn't
        # affect compute()'s physics, so it's read directly at export time rather than
        # wired through _on_control_change's recompute trace. Forced to 1 at export if the
        # chosen ignition system's forces_single_ignition is True (see ignition.py) - shown
        # here as typed, the override happens silently in cfg_writer.py, same as before.
        ttk.Label(imb, text="Number of ignitions (forced to 1 for single-shot igniters)").grid(
            row=im_row, column=0, columnspan=2, sticky="w")
        im_row += 1
        self.ignitions_var = tk.StringVar(value=str(self.design.ignitions))
        ignitions_entry = ttk.Entry(imb, textvariable=self.ignitions_var, width=16)
        ignitions_entry.grid(row=im_row, column=0, sticky="ew")
        ignitions_entry.bind("<KeyRelease>", self._on_export_field_change)
        im_row += 1

        ttk.Label(imb, text="Mass / burn-time estimate").grid(row=im_row, column=0, columnspan=2, sticky="w")
        im_row += 1
        self.mass_burn_details = tk.Text(imb, width=40, height=9, state="disabled", wrap="word",
                                          font=("Courier", 9))
        self.mass_burn_details.grid(row=im_row, column=0, columnspan=2, sticky="ew")

        ttk.Separator(left, orient="horizontal").grid(row=row, column=0, columnspan=2, sticky="ew", pady=6)
        row += 1

        # Readout/Warnings/Export live below the tabs (relevant regardless of
        # which tab is active), each in their own collapsible section so they
        # don't add fixed height under every tab - Readout/Warnings default
        # open (the primary feedback loop), Export & Metadata default closed
        # (touched rarely, once name/tech-node/cost are set).
        sec_readout = CollapsibleSection(left, "Readout")
        sec_readout.grid(row=row, column=0, columnspan=2, sticky="ew")
        row += 1
        rob = sec_readout.body_parent()
        self.readout = tk.Text(rob, width=42, height=15, state="disabled", wrap="word", font=("Courier", 9))
        self.readout.grid(row=0, column=0, columnspan=2, sticky="ew")

        sec_warnings = CollapsibleSection(left, "Warnings")
        sec_warnings.grid(row=row, column=0, columnspan=2, sticky="ew")
        row += 1
        wb = sec_warnings.body_parent()
        self.warnings_box = tk.Text(wb, width=42, height=7, state="disabled", wrap="word",
                                     foreground="#a03030", font=("Courier", 9))
        self.warnings_box.grid(row=0, column=0, columnspan=2, sticky="ew")

        sec_export = CollapsibleSection(left, "Export & Metadata", start_open=False)
        sec_export.grid(row=row, column=0, columnspan=2, sticky="ew")
        row += 1
        exb = sec_export.body_parent()
        ex_row = 0

        ttk.Label(exb, text="Export CONFIG name").grid(row=ex_row, column=0, columnspan=2, sticky="w")
        ex_row += 1
        self.export_name_var = tk.StringVar(value=self.design.config_name)
        _cfg_name_entry = ttk.Entry(exb, textvariable=self.export_name_var)
        _cfg_name_entry.grid(row=ex_row, column=0, columnspan=2, sticky="ew")
        _cfg_name_entry.bind("<KeyRelease>", self._on_export_field_change)
        ex_row += 1

        # RP-1 tech-node gating: these three fields never affect compute()'s physics
        # (Isp/thrust/warnings are unrelated to a career-mode tech unlock), so they're
        # read/written directly on self.design by _on_export_field_change WITHOUT
        # triggering a full recompute() on every keystroke - unlike every slider/dropdown
        # above, which all funnel through _on_control_change's trace-triggered recompute.
        ttk.Label(exb, text="RP-1 tech node (optional - blank = no tech-tree gating; "
                             "type any node, suggestions are real RP-1 engine nodes)").grid(
            row=ex_row, column=0, columnspan=2, sticky="w")
        ex_row += 1
        self.tech_node_var = tk.StringVar(value=self.design.tech_node)
        self.tech_node_combo = ttk.Combobox(
            exb, textvariable=self.tech_node_var,
            values=tech_tree.suggested_nodes(self.design.propellant_pair, self.design.cycle))
        self.tech_node_combo.grid(row=ex_row, column=0, columnspan=2, sticky="ew")
        self.tech_node_combo.bind("<KeyRelease>", self._on_export_field_change)
        self.tech_node_combo.bind("<<ComboboxSelected>>", self._on_export_field_change)
        ex_row += 1

        ttk.Label(exb, text="Entry cost").grid(row=ex_row, column=0, sticky="w")
        ttk.Label(exb, text="Cost").grid(row=ex_row, column=1, sticky="w")
        ex_row += 1
        self.entry_cost_var = tk.StringVar(value=f"{self.design.entry_cost:.0f}")
        entry_cost_entry = ttk.Entry(exb, textvariable=self.entry_cost_var, width=16)
        entry_cost_entry.grid(row=ex_row, column=0, sticky="ew")
        entry_cost_entry.bind("<KeyRelease>", self._on_cost_field_edit)
        self.cost_var = tk.StringVar(value=f"{self.design.cost:.0f}")
        cost_entry = ttk.Entry(exb, textvariable=self.cost_var, width=16)
        cost_entry.grid(row=ex_row, column=1, sticky="ew")
        cost_entry.bind("<KeyRelease>", self._on_cost_field_edit)
        # Reset button: hand the cost fields back to the auto estimate.
        ttk.Button(exb, text="Reset cost to estimate",
                   command=self._on_cost_reset).grid(row=ex_row + 1, column=0, columnspan=2, sticky="w")
        ex_row += 2

        # Project New / Save / Load (JSON design file) - all four project actions
        # together beneath the tabs.
        proj_frame = ttk.Frame(left)
        proj_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Button(proj_frame, text="New", command=self._on_new).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(proj_frame, text="Save…", command=self._on_save).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(proj_frame, text="Load…", command=self._on_load).pack(side=tk.LEFT, expand=True, fill=tk.X)
        row += 1

        export_btn = ttk.Button(left, text="Export .cfg...", command=self._on_export)
        export_btn.grid(row=row, column=0, columnspan=2, sticky="ew", pady=6)
        row += 1

        notebook = ttk.Notebook(right)
        notebook.pack(fill=tk.BOTH, expand=True)

        tab_2d = ttk.Frame(notebook)
        notebook.add(tab_2d, text="2D Schematic")
        self.fig = Figure(figsize=(6, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=tab_2d)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        tab_3d = ttk.Frame(notebook)
        notebook.add(tab_3d, text="3D Preview")
        self.gl_preview = None
        self._use_gl_preview = _GL_PREVIEW_AVAILABLE
        if self._use_gl_preview:
            try:
                self.gl_preview = EnginePreviewGLFrame(tab_3d, width=600, height=600)
                # X-ray toggle (GL-only render state - see EnginePreviewGLFrame.set_xray):
                # structural pieces go translucent with a rim-alpha fade. Packed before
                # the canvas so it sits above it; destroyed with the rest of tab_3d's
                # children by the fallback below if GL fails.
                xray_bar = ttk.Frame(tab_3d)
                xray_bar.pack(fill=tk.X)
                self._xray_var = tk.BooleanVar(value=False)
                self._xray_opacity_var = tk.DoubleVar(value=XRAY_DEFAULT_OPACITY)
                ttk.Checkbutton(xray_bar, text="X-ray", variable=self._xray_var,
                                command=self._on_xray_change).pack(side=tk.LEFT, padx=4, pady=2)
                ttk.Label(xray_bar, text="opacity").pack(side=tk.LEFT, padx=(8, 2))
                ttk.Scale(xray_bar, from_=0.02, to=0.8, variable=self._xray_opacity_var,
                          orient="horizontal", length=140,
                          command=lambda _v: self._on_xray_change()).pack(side=tk.LEFT, padx=2)
                # Flow toggle (propellant-flow visualization, GL render state
                # only - see EnginePreviewGLFrame.set_flow) + its colorbar legend,
                # which is packed in above the canvas only while Flow is on.
                self._flow_var = tk.BooleanVar(value=False)
                ttk.Checkbutton(xray_bar, text="Flow", variable=self._flow_var,
                                command=self._on_flow_change).pack(side=tk.LEFT, padx=(12, 4))
                self._flow_legend = FlowLegend(tab_3d)
                self._last_result = None
                self.gl_preview.pack(fill=tk.BOTH, expand=True)
            except Exception as exc:
                # Construction-time GL failure (e.g. no usable GL context) -
                # degrade to the matplotlib fallback rather than leaving a
                # broken tab; see preview3d_gl.py's module docstring.
                print(f"3D Preview: OpenGL widget failed to initialize, "
                      f"falling back to matplotlib: {exc}")
                for child in tab_3d.winfo_children():
                    child.destroy()
                self._use_gl_preview = False
        if not self._use_gl_preview:
            global draw_3d_preview
            from .preview3d import draw_3d_preview, _GIZMO_LABEL
            ttk.Label(tab_3d, text="PyOpenGL/pyopengltk not available - using the "
                      "slower matplotlib 3D preview. See requirements.txt.").pack(fill=tk.X)
            self.fig3d = Figure(figsize=(6, 6))
            self.ax3d = self.fig3d.add_subplot(111, projection="3d")
            self.canvas3d = FigureCanvasTkAgg(self.fig3d, master=tab_3d)
            self.canvas3d.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self._gizmo3d_label = _GIZMO_LABEL
            self.canvas3d.mpl_connect("motion_notify_event", self._sync_gizmo3d)

        tab_injector_face = ttk.Frame(notebook)
        notebook.add(tab_injector_face, text="Injector Face")
        self.fig_if = Figure(figsize=(6, 6))
        self.ax_if = self.fig_if.add_subplot(111)
        self.canvas_if = FigureCanvasTkAgg(self.fig_if, master=tab_injector_face)
        self.canvas_if.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Checklist tab: every design check's pass/warn status (not just the
        # currently-failing ones shown in the left Warnings box), grouped by
        # category. Uses a ttk.Treeview (keyboard-navigable, structured columns)
        # rather than colored text, and plain "PASS"/"WARN" status text rather
        # than a symbol glyph - color is a secondary cue only, never the sole
        # signal, so this doesn't depend on color vision or font glyph support.
        tab_checklist = ttk.Frame(notebook)
        notebook.add(tab_checklist, text="Checklist")
        self.checklist_tree = ttk.Treeview(tab_checklist, columns=("status", "detail"),
                                            show="tree headings")
        self.checklist_tree.heading("#0", text="Check")
        self.checklist_tree.heading("status", text="Status")
        self.checklist_tree.heading("detail", text="Detail")
        self.checklist_tree.column("#0", width=260, stretch=True)
        self.checklist_tree.column("status", width=70, anchor="center", stretch=False)
        self.checklist_tree.column("detail", width=420, stretch=True)
        checklist_scrollbar = ttk.Scrollbar(tab_checklist, orient="vertical",
                                             command=self.checklist_tree.yview)
        self.checklist_tree.configure(yscrollcommand=checklist_scrollbar.set)
        self.checklist_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        checklist_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.checklist_tree.tag_configure("pass", foreground="#207020")
        self.checklist_tree.tag_configure("fail", foreground="#a03030")

        # Turbopump systems / flow diagram (physics/turbopump_sizing.py).
        tab_turbopump = ttk.Frame(notebook)
        notebook.add(tab_turbopump, text="Turbopump")
        self.fig_tp = Figure(figsize=(6, 6))
        self.ax_tp = self.fig_tp.add_subplot(111)
        self.canvas_tp = FigureCanvasTkAgg(self.fig_tp, master=tab_turbopump)
        self.canvas_tp.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _add_dropdown(self, parent, row, label, attr_name, values, initial_value,
                       on_select=None, width=None):
        ttk.Label(parent, text=label).grid(row=row, column=0, columnspan=2, sticky="w")
        row += 1
        var = tk.StringVar(value=initial_value)
        setattr(self, attr_name, var)
        kwargs = {"width": width} if width else {}
        box = ttk.Combobox(parent, textvariable=var, values=values, state="readonly", **kwargs)
        box.grid(row=row, column=0, columnspan=2, sticky="ew")
        setattr(self, attr_name + "_box", box)   # e.g. for material-filtered value lists
        box.bind("<<ComboboxSelected>>", on_select or self._on_control_change)
        row += 1
        return row

    def _add_slider(self, parent, row, label, var, lo, hi, decimals=2, return_scale=False,
                     on_change=None):
        """A ttk.Scale and a ttk.Entry sharing the SAME variable - typing in the
        entry and dragging the scale both work, and both stay in sync because
        there's only one underlying Tk variable, not two separately-synced
        copies. The Scale's own `command` (fires only on direct drag/click,
        never while typing in the Entry) rounds the shared value for display;
        typed Entry text is left exactly as typed until it's read on the next
        recompute.

        `on_change` overrides the default `_on_control_change` (design-
        mutation + physics recompute) trace target - used by cosmetic-only
        sliders that shouldn't touch self.design (e.g. the 3D preview's
        flange render-detail sliders)."""
        ttk.Label(parent, text=f"{label}  [{lo:g}-{hi:g}]").grid(row=row, column=0, columnspan=2, sticky="w")
        row += 1
        entry = ttk.Entry(parent, textvariable=var, width=8)
        entry.grid(row=row, column=1, sticky="e")

        def on_drag(v):
            var.set(round(float(v), decimals))

        scale = ttk.Scale(parent, from_=lo, to=hi, variable=var, orient="horizontal", command=on_drag)
        scale.grid(row=row, column=0, sticky="ew")
        row += 1
        var.trace_add("write", lambda *_a: (on_change or self._on_control_change)())
        if return_scale:
            return row, scale
        return row

    def _register_gate(self, frame, predicate):
        """Register `frame` (a wrapper Frame holding one logical control, or a
        CollapsibleSection's body) to be shown only while `predicate()` is
        True. Purely a display simplification - the tk vars inside `frame`
        keep feeding self.design in _on_control_change exactly as before
        regardless of gate state, so a hidden control's stored value never
        gets silently dropped or reset just because it's not currently shown.
        `_apply_gates()` re-evaluates every registered predicate from
        scratch on every call, so nested gates (e.g. hatband count/width
        inside the tube_wall-only group) stay correct regardless of order."""
        self._gated_controls.append((frame, predicate))
        self._apply_gates()

    def _apply_gates(self):
        for frame, predicate in self._gated_controls:
            try:
                visible = bool(predicate())
            except (tk.TclError, KeyError):
                visible = True   # widget mid-construction / var not set yet - default shown
            if visible:
                frame.grid()
            else:
                frame.grid_remove()

    # ----------------------------------------------------------- Shape Lab
    def _enter_shape_lab(self, panel_factory):
        """In-window context switch: unpack the normal sidebar/preview and
        pack the Lab panel `panel_factory(parent, on_close)` returns (a
        gui/shape_lab.py _ShapeLabBase subclass) into self.root in their
        place. See _exit_shape_lab for the reverse."""
        self.container.pack_forget()
        self.right.pack_forget()
        self._shape_lab_panel = panel_factory(self.root, self._exit_shape_lab)
        self._shape_lab_panel.pack(fill=tk.BOTH, expand=True)

    def _exit_shape_lab(self):
        if self._shape_lab_panel is not None:
            self._shape_lab_panel.destroy()
            self._shape_lab_panel = None
        # Order matters (pack places left-to-right) - must match _build_layout exactly.
        self.container.pack(side=tk.LEFT, fill=tk.Y)
        self.right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # ----------------------------------------------------------- Plumbing tab
    def _refresh_plumbing_rows(self, result):
        """Per-host status/buttons on the Plumbing tab from the latest
        compute() result (called from recompute)."""
        if not hasattr(self, "_plumbing_rows"):
            return
        by_host = {p["host"]: p for p in (result.get("plumbing_results") or [])}
        for host, row in self._plumbing_rows.items():
            has_run = bool(plumbing.runs_for_host(self.design.plumbing_runs, host))
            hook = plumbing.hook_for_host(result, host)
            if hook is None:
                row["status"].set(f"no ring: {plumbing.HOST_MISSING_HINT[host]}"
                                  + (" - stale run, clear it" if has_run else ""))
                row["edit"].state(["disabled"])
            else:
                pr = by_host.get(host)
                if pr is not None:
                    n_adv = len(pr.get("advisories") or [])
                    row["status"].set(
                        f"run: {pr['n_pipes']} pipes, {pr['n_flanges']} flanges, "
                        f"{pr['total_length_m']:.2f} m, {pr['mass_kg']:.1f} kg"
                        + (f", -> {pr['connected_pump'].replace('_', ' ')}, loss "
                           f"{pr.get('pressure_loss_pa', 0.0) / 1e3:.0f} kPa"
                           if pr.get("connected_pump") else "")
                        + (f" - {n_adv} advisor{'y' if n_adv == 1 else 'ies'}" if n_adv else ""))
                elif host == "jacket_inlet":
                    # mesh_builder still draws the legacy auto-drawn stub duct
                    # on this one ring until a run is baked over it.
                    row["status"].set("no run (legacy auto duct drawn)")
                else:
                    row["status"].set("no run")
                if _SHAPE_LAB_AVAILABLE:
                    row["edit"].state(["!disabled"])
            row["clear"].state(["!disabled"] if has_run else ["disabled"])

    def _clear_plumbing_run(self, host):
        """Drop the baked run on `host` (same filter the Shape Lab's Bake uses
        to replace one) and recompute."""
        self.design.plumbing_runs = [r for r in (self.design.plumbing_runs or [])
                                     if (r or {}).get("host") != host]
        self.recompute()

    # --------------------------------------------------------------- handlers
    def _on_pair_change(self, _event=None):
        if self._loading:      # New / Load pushes many vars at once - one recompute at the end
            return
        pair = self.pair_var.get()
        # Set every default BEFORE mr_var, since mr_var's trace is what actually fires
        # the recompute - it needs to see all the already-updated values, not the
        # previous pair's defaults. A monopropellant suggests catalyst-bed + pressure-
        # fed as sensible starting points - a suggestion via .set(), not a hard block;
        # the user can still switch away and get warned (design.py's cross-checks),
        # not stopped.
        default_ign = ignition.default_for_pair(pair)
        self.ignition_var.set(ignition.IGNITION_SYSTEMS[default_ign].display_name)
        self.lstar_var.set(combustion.l_star_default_for_pair(pair))  # [Huzel Table 4-1]
        if combustion.is_monopropellant(pair):
            self.injector_var.set(injectors.INJECTORS["catalyst_bed"].display_name)
            self.cycle_var.set(CYCLE_DISPLAY[cycles.PRESSURE_FED])
        mr_lo, mr_hi = combustion.mr_bounds(pair)
        self.mr_scale.configure(from_=mr_lo, to=mr_hi)
        self.mr_var.set((mr_lo + mr_hi) / 2.0)  # fires the trace -> recompute

    def _on_optimize_mr(self):
        """Jump the mixture-ratio slider to the vacuum-Isp-maximising MR for the
        current design (within the propellant pair's table range). No-op for a
        monopropellant. The slider's trace fires the recompute."""
        if combustion.is_monopropellant(self.design.propellant_pair):
            return
        curve = mixture_ratio.isp_vs_mr_curve(self.design, n=25)
        self.mr_var.set(round(curve["peak_mr"], 3))

    def _filter_cooling_dropdowns(self):
        """HARD block, GUI side: each section's cooling-method dropdown lists only
        "auto" + the methods its CURRENT material can physically be built for
        (materials.Material.allowed_cooling_methods). A selection that the new
        material can't take is reset to "auto" and the hint says so - including
        one read from a loaded project file (Load ends in _on_control_change).
        compute() enforces the same block independently (red BLOCKED checklist
        row), so a design built outside the GUI is covered too."""
        for mat_var, meth_var, hint_var, section in (
                ("material_var", "chamber_cooling_method_var", "chamber_cooling_hint_var",
                 "chamber"),
                ("bell_material_var", "nozzle_cooling_method_var", "nozzle_cooling_hint_var",
                 "nozzle/bell")):
            if not hasattr(self, mat_var) or not hasattr(self, meth_var + "_box"):
                continue
            key = self.material_display_to_key.get(getattr(self, mat_var).get())
            mat = materials.MATERIALS.get(key)
            if mat is None:
                continue
            allowed = ["auto"] + list(mat.allowed_cooling_methods)
            getattr(self, meth_var + "_box").configure(values=allowed)
            hint = (f"{mat.display_name}: {', '.join(mat.allowed_cooling_methods)} "
                    f"(auto = {mat.cooling_method}); film is added below as an overlay.")
            cur = getattr(self, meth_var).get()
            if cur not in allowed:
                getattr(self, meth_var).set("auto")
                hint = (f"'{cur}' is impossible on {mat.display_name} - reset to auto "
                        f"({mat.cooling_method}). " + hint)
            if hasattr(self, hint_var):
                getattr(self, hint_var).set(hint)

    def _on_control_change(self, *_args):
        # Reads every input widget into self.design, then recomputes. Its exact
        # inverse is _refresh_widgets_from_design() (used by New / Load) - keep
        # the two in lockstep when adding a control.
        if self._loading:      # suppress the per-var trace storm during New / Load
            return
        self._filter_cooling_dropdowns()
        # Re-evaluate conditional show/hide first, independent of whether the
        # rest of this call ends up recomputing physics below - the gated
        # controls' predicates only ever read dropdown/checkbox vars, which
        # can't be mid-keystroke-invalid the way a typed slider Entry can.
        self._apply_gates()
        try:
            self.design.propellant_pair = self.pair_var.get()
            self.design.cycle = CYCLE_FROM_DISPLAY.get(self.cycle_var.get(), self.design.cycle)
            self.design.nozzle_type = NOZZLE_TYPE_FROM_DISPLAY.get(
                self.nozzle_type_var.get(), self.design.nozzle_type)
            self.design.material_key = self.material_display_to_key.get(
                self.material_var.get(), self.design.material_key)
            self.design.bell_material_key = self.material_display_to_key.get(
                self.bell_material_var.get(), self.design.bell_material_key)
            self.design.injector_type = self.injector_display_to_key.get(
                self.injector_var.get(), self.design.injector_type)
            self.design.ignition_system = self.ignition_display_to_key.get(
                self.ignition_var.get(), self.design.ignition_system)
            self.design.controller_tech_key = self.controller_display_to_key.get(
                self.controller_var.get(), self.design.controller_tech_key)
            self.design.gimbal_mode = GIMBAL_MODE_FROM_DISPLAY.get(
                self.gimbal_mode_var.get(), self.design.gimbal_mode)
            self.design.host_model_engine_type = self.host_display_to_type.get(
                self.host_var.get(), self.design.host_model_engine_type)
            self.design.turbopump_tech_key = self.turbopump_display_to_key.get(
                self.turbopump_tech_var.get(), self.design.turbopump_tech_key)
            self.design.turbopump_arrangement = self.turbopump_arrangement_var.get()
            self.design.turbine_staging = self.turbine_staging_var.get()
            self.design.turbopump_material_key = self.turbopump_material_display_to_key.get(
                self.turbopump_material_var.get(), self.design.turbopump_material_key)
            self.design.bearing_material_key = self.bearing_material_display_to_key.get(
                self.bearing_material_var.get(), self.design.bearing_material_key)
            self.design.enforce_suction_limit = bool(self.suction_limit_var.get())
            self.design.npsh_available_fuel_ft = max(0.0, float(self.npsh_fuel_var.get()))
            self.design.npsh_available_ox_ft = max(0.0, float(self.npsh_ox_var.get()))
            self.design.preburner_tin_k = max(0.0, float(self.pb_tin_fr_var.get()))
            self.design.ox_preburner_tin_k = max(0.0, float(self.pb_tin_or_var.get()))

            self.design.chamber_pressure_pa = self.pc_var.get() * 1e6
            self.design.mixture_ratio = self.mr_var.get()
            self.design.expansion_ratio = self.eps_var.get()
            self.design.nozzle_half_angle_deg = self.half_angle_var.get()
            self.design.bell_percent_length = self.bell_pct_var.get()
            self.design.contraction_ratio = self.contraction_var.get()
            self.design.lstar_m = self.lstar_var.get()
            self.design.chamber_sizing_method = self.chamber_sizing_method_var.get()
            self.design.chamber_residence_time_ms = self.chamber_residence_time_var.get()
            self.design.chamber_wall_fillet_r_over_rt = self.chamber_wall_fillet_var.get()
            self.design.convergent_half_angle_deg = self.convergent_angle_var.get()
            self.design.apply_chamber_pressure_loss = bool(self.pc_loss_var.get())
            self.design.orifice_type = self.orifice_type_var.get()
            self.design.impingement_angle_deg = self.impingement_var.get()
            self.design.fuel_manifold_head_fraction = self.fuel_manifold_head_var.get() / 100.0
            self.design.ox_manifold_head_fraction = self.ox_manifold_head_var.get() / 100.0
            self.design.fuel_manifold_taper_blend = self.fuel_manifold_taper_var.get()
            self.design.ox_manifold_taper_blend = self.ox_manifold_taper_var.get()
            self.design.jacket_inlet_taper_blend = self.jacket_inlet_taper_var.get()
            self.design.jacket_inlet_velocity_mult = self.jacket_inlet_vmult_var.get()
            self.design.cooling_transition_eps = self.cooling_transition_var.get()
            self.design.chamber_cooling_method = self.chamber_cooling_method_var.get()
            self.design.nozzle_cooling_method = self.nozzle_cooling_method_var.get()
            self.design.regen_nozzle_end_eps = self.regen_nozzle_end_var.get()
            self.design.dump_coolant_fraction = self.dump_coolant_fraction_var.get() / 100.0
            self.design.wall_construction = self.wall_construction_var.get()
            self.design.cooling_flow_topology = self.cooling_flow_topology_var.get()
            self.design.manifold_bypass_fraction = self.manifold_bypass_var.get() / 100.0
            self.design.jacket_inlet_eps = self.jacket_inlet_eps_var.get()
            self.design.chamber_tube_jacket = bool(self.chamber_tube_jacket_var.get())
            self.design.tube_split_eps = self.tube_split_eps_var.get()
            self.design.tube_hatbands = bool(self.tube_hatbands_var.get())
            self.design.tube_hatbands_on_extension = bool(self.tube_hatbands_on_extension_var.get())
            self.design.tube_hatband_count = int(self.tube_hatband_count_var.get())
            self.design.tube_hatband_width_m = self.tube_hatband_width_var.get() / 1000.0
            self.design.tube_hatband_shape = self.hatband_shape_display_to_key.get(
                self.tube_hatband_shape_var.get(), self.design.tube_hatband_shape)
            self.design.tube_hatband_material = self.material_display_to_key.get(
                self.tube_hatband_material_var.get(), self.design.tube_hatband_material)
            self.design.flange_thickness_m = self.flange_thickness_var.get() / 1000.0
            self.design.flange_width_m = self.flange_width_var.get() / 1000.0
            self.design.flange_bolt_count = int(self.flange_bolt_count_var.get())
            self.design.film_cooling_fraction = self.film_cooling_var.get() / 100.0
            self.design.chamber_film_inject_area_ratio = max(0.0, self.chamber_film_inject_var.get())
            self.design.nozzle_film_fraction = max(0.0, self.nozzle_film_var.get() / 100.0)
            self.design.nozzle_film_inject_eps = self.nozzle_film_eps_var.get()
            self.design.regen_channel_model = self.regen_channel_model_var.get()
            self.design.regen_channel_count = int(self.regen_channel_count_var.get())
            self.design.regen_channel_aspect_ratio = self.regen_channel_aspect_var.get()
            self.design.regen_channel_land_fraction = self.regen_channel_land_var.get()
            self.design.regen_coolant_velocity_ms = self.regen_coolant_velocity_var.get()
            self.design.injector_baffles = bool(self.baffles_var.get())
            self.design.baffle_compartments = int(self.baffle_comp_var.get())
            self.design.acoustic_cavities = bool(self.cavities_var.get())
            self.design.acoustic_cavity_count = int(float(self.cavity_count_var.get()))
            self.design.injector_stiffness = self.stiffness_var.get()
            self.design.gimbal_range_deg = self.gimbal_range_var.get()
            self.design.gimbal_response_speed_deg_s = self.gimbal_response_var.get()
            self.design.eta_pump_fuel = self.eta_pump_fuel_var.get()
            self.design.eta_pump_ox = self.eta_pump_ox_var.get()
            self.design.pump_specific_power_w_kg = self.specific_power_var.get() * 1e3
            self.design.throttle_floor = self.throttle_var.get()
            self.design.target_vac_thrust_n = float(self.thrust_var.get()) * 1e3
            self.design.output_mode = OUTPUT_MODE_FROM_DISPLAY.get(
                self.output_mode_var.get(), self.design.output_mode)
            try:
                self.design.host_model_reference_height_m = max(
                    0.0, float(self.host_ref_height_var.get()))
            except ValueError:
                pass   # mid-keystroke; keep the last good value
        except (ValueError, tk.TclError):
            # A shared Entry/Scale variable can be transiently unparseable mid-
            # keystroke (e.g. a bare "-" or "1."). Quietly skip this cycle
            # rather than crash - the next valid keystroke recomputes fine.
            return

        # Keep the tech-node combobox's suggestions relevant to the current
        # propellant/cycle (e.g. LOX/LH2 -> hydrolox nodes first) without
        # clobbering anything the user already typed/selected.
        self.tech_node_combo["values"] = tech_tree.suggested_nodes(
            self.design.propellant_pair, self.design.cycle)

        self.recompute()

    def _on_turbopump_tech_change(self, _event=None):
        # The tier no longer pre-fills efficiency sliders (efficiency is derived);
        # it's a build-quality multiplier read straight from turbopump_tech_var.
        self._on_control_change()

    def _on_cost_field_edit(self, *_args):
        """User typed in the cost / entryCost fields -> stop auto-populating them."""
        self._cost_overridden = True
        self._on_export_field_change()

    def _on_cost_reset(self):
        """Hand the cost / entryCost fields back to the auto estimate."""
        self._cost_overridden = False
        self.recompute()

    def _on_export_field_change(self, *_args):
        """tech_node/entry_cost/cost/ignitions never affect compute()'s physics
        (Isp/thrust/warnings are unrelated to a career-mode tech unlock or
        restart count), so unlike every other control these are read/written
        directly on self.design without calling recompute() - typing a value
        shouldn't trigger a full physics recompute on every keystroke."""
        self.design.tech_node = self.tech_node_var.get().strip()
        self.design.config_name = self.export_name_var.get().strip() or self.design.config_name
        self.design.new_part_name = self.new_part_name_var.get().strip()
        self.design.new_part_title = self.new_part_title_var.get().strip()
        self.design.new_part_manufacturer = (
            self.new_part_mfr_var.get().strip() or "Fictional")
        try:
            self.design.entry_cost = float(self.entry_cost_var.get())
        except ValueError:
            pass
        try:
            self.design.cost = float(self.cost_var.get())
        except ValueError:
            pass
        try:
            self.design.ignitions = int(self.ignitions_var.get())
        except ValueError:
            pass

    def _on_xray_change(self):
        if self.gl_preview is not None:
            self.gl_preview.set_xray(self._xray_var.get(), self._xray_opacity_var.get())

    def _on_flow_change(self):
        if self.gl_preview is None:
            return
        on = self._flow_var.get()
        # The streams run inside the walls: turn X-ray on with them (it can be
        # unticked again).
        if on and not self._xray_var.get():
            self._xray_var.set(True)
            self._on_xray_change()
        self.gl_preview.set_flow(on)
        if on:
            self._flow_legend.pack(fill=tk.X, before=self.gl_preview)
            self._flow_legend.update_result(self._last_result)
        else:
            self._flow_legend.pack_forget()

    def _sync_gizmo3d(self, event):
        """
        Keep the matplotlib-fallback corner orientation gizmo tracking the
        main 3D axes' rotation live during mouse-drag orbiting. matplotlib's
        interactive 3D rotation mutates ax3d.elev/azim/roll directly inside
        the Tk backend's event loop without calling draw_3d_preview() again,
        so without this hook the gizmo would only resync on the next
        result-driven recompute() - see preview3d.py's _draw_orientation_gizmo
        docstring.
        """
        if self._use_gl_preview or not hasattr(self, "_gizmo3d_label"):
            return
        gizmo_ax = next((a for a in self.fig3d.axes if a.get_label() == self._gizmo3d_label), None)
        if gizmo_ax is None:
            return
        gizmo_ax.view_init(elev=self.ax3d.elev, azim=self.ax3d.azim,
                            roll=getattr(self.ax3d, "roll", 0))
        self.canvas3d.draw_idle()

    def _update_hatband_summary(self, result):
        """One-line readout of the sized hatbands under the hatband controls."""
        label = getattr(self, "hatband_summary_label", None)
        if label is None:
            return
        hb = (result.get("cooling") or {}).get("hatbands")
        if not hb:
            label.config(text="")
            return
        shell = ""
        if hb.get("shell_end_x_m") is not None and hb.get("shell_start_x_m") is not None:
            shell = (f"continuous shell for {1000 * (hb['shell_end_x_m'] - hb['shell_start_x_m']):.0f}"
                     f" mm aft of the throat, then ")
        buck = hb.get("worst_buckling_margin", float("inf"))
        buck_txt = f", ring-buckling margin {buck:.2f}" if buck != float("inf") else ""
        label.config(text=(f"{shell}{hb['n_bands']} bands "
                           f"({'/'.join(hb['shapes_used']) or '-'}), "
                           f"{hb['total_mass_kg']:.1f} kg{buck_txt}"
                           + ("" if hb.get("all_ok") else "  - see Warnings")))

    def recompute(self):
        if self._loading:      # New / Load calls recompute() itself once, at the end
            return
        try:
            result = self.design.compute()
        except Exception as exc:
            self._set_text(self.readout, f"ERROR computing design:\n{exc}")
            return
        self.last_result = result
        self._update_hatband_summary(result)

        draw_schematic(self.ax, result)
        self.canvas.draw_idle()

        if self._use_gl_preview:
            self.gl_preview.update_result(result)
            self._last_result = result
            if self._flow_var.get():
                self._flow_legend.update_result(result)
        else:
            draw_3d_preview(self.ax3d, result)
            self.canvas3d.draw_idle()

        draw_injector_face(self.ax_if, result)
        self.canvas_if.draw_idle()

        draw_turbopump_diagram(self.ax_tp, result)
        self.canvas_tp.draw_idle()

        self._refresh_plumbing_rows(result)

        # Isp-vs-MR feedback for the Combustion Chamber tab.
        if combustion.is_monopropellant(self.design.propellant_pair):
            self.mr_peak_var.set("Mixture ratio: n/a (monopropellant)")
            self.optimize_mr_btn.state(["disabled"])
        else:
            curve = mixture_ratio.isp_vs_mr_curve(self.design, n=25)
            delta = result["isp_vac_engine_s"] - curve["peak_isp_s"]
            self.mr_peak_var.set(
                f"Peak vac Isp {curve['peak_isp_s']:.1f} s at MR {curve['peak_mr']:.2f}"
                f"  (current MR {self.design.mixture_ratio:.2f}: {delta:+.1f} s)")
            self.optimize_mr_btn.state(["!disabled"])

        injector = injectors.INJECTORS[self.design.injector_type]
        ig = result.get("injector_geometry", {})
        ac = result.get("chamber_acoustics", {})
        cool = result.get("cooling", {})
        sizing = result.get("turbopump_sizing")
        lo_ang, hi_ang = ig.get("impingement_angle_band_deg", (20.0, 45.0))
        injector_lines = [
            injector.display_name,
            injector.stability_note,
            "",
            "-- catalog --",
            f"eta_cstar multiplier: {injector.eta_cstar_multiplier:.2f}   "
            f"nominal dP/Pc: {injector.dp_over_pc_nominal:.3f}",
            f"min stable dP/Pc (chug): {injector.min_stable_dp_ratio:.2f}   "
            f"practical min throttle: {injector.practical_min_throttle*100:.0f}%",
            f"suited pairs: {', '.join(injector.suited_pairs) if injector.suited_pairs else 'any'}",
            "",
            "-- derived element geometry --",
            f"injection velocity: fuel {ig.get('v_fuel_ms', 0):.0f} / ox {ig.get('v_ox_ms', 0):.0f} m/s",
            f"orifice dia ~{ig.get('orifice_dia_mm', 0):.2f} mm   "
            f"elements ~{ig.get('n_elements', 0):,}",
            f"orifices: fuel ~{ig.get('n_fuel_orifices', 0):,} / ox ~{ig.get('n_ox_orifices', 0):,}",
            f"injection momentum ratio Rm: {ig.get('momentum_ratio', 0):.2f}   "
            f"resultant beta: {ig.get('beta_deg', 0):+.1f} deg"
            + ("  (symmetric pattern)" if ig.get("symmetric_pattern") else ""),
            f"orifice Cd: {result.get('orifice_cd', 0.65):.2f} ({self.design.orifice_type})   "
            f"impingement angle: {self.design.impingement_angle_deg:.0f} deg",
            f"note: {ig.get('note', '')}",
            f"plate mass: {result.get('injector_plate_mass_kg', 0):.0f} kg",
            "",
            "-- feed pressure --",
            f"injector dP: fuel {result.get('injector_dp_fuel_pa', 0)/1e6:.2f} / "
            f"ox {result.get('injector_dp_ox_pa', 0)/1e6:.2f} MPa "
            f"(nominal {result.get('injector_dp_nominal_pa', 0)/1e6:.2f}, "
            f"velocity-derived {result.get('injector_dp_derived_pa', 0)/1e6:.2f})",
            f"dP/Pc actual: {result.get('injector_dp_pa', 0)/self.design.chamber_pressure_pa:.3f}",
            "",
            "-- propellant intake manifold --",
        ]
        _mr = result.get("manifold_result", {})
        _mf, _mo = _mr.get("fuel", {}), _mr.get("ox", {})
        def _ring_line(tag, m):
            # Feed bore (full flow, the connecting pipe) vs. the split/tapered
            # ring's own inlet -> far-side bore (physics/manifold.py).
            return (f"{tag} feed ID {m.get('inner_diameter_m', 0)*1000:.0f} mm @ "
                    f"{m.get('design_feed_velocity_ms', 0):.1f} m/s; ring ID "
                    f"{m.get('ring_inlet_inner_diameter_m', 0)*1000:.0f}->"
                    f"{2*m.get('min_flow_radius_m', 0)*1000:.0f} mm, wall "
                    f"{m.get('wall_thickness_m', 0)*1000:.2f} mm, {m.get('mass_kg', 0):.1f} kg")
        injector_lines += [_ring_line("fuel:", _mf), _ring_line("ox:  ", _mo)]
        for _jk, _jlabel in (("jacket_inlet", "jacket in:"), ("jacket_return", "jacket ret:")):
            _jm = (result.get("jacket_manifold_result") or {}).get(_jk)
            if _jm:
                injector_lines.append(_ring_line(_jlabel, _jm))
        if sizing:
            injector_lines.append(
                f"pump discharge -> shaft: fuel {sizing.get('fuel_shaft_rpm', 0):,.0f} rpm / "
                f"ox {sizing.get('ox_shaft_rpm', 0):,.0f} rpm")
        injector_lines += [
            "",
            "-- chamber acoustics --",
            f"sound speed a_e: {ac.get('sound_speed_ms', 0):.0f} m/s",
            f"1L {ac.get('long_1l_hz', 0):.0f} Hz   1T {ac.get('tang_1t_hz', 0):.0f} Hz   "
            f"1R {ac.get('rad_1r_hz', 0):.0f} Hz",
        ]
        stab = result.get("stability", {})
        aid_bits = []
        if stab.get("baffles"):
            aid_bits.append(f"{stab.get('baffle_compartments')}-compartment baffle")
        if stab.get("cavities"):
            aid_bits.append(f"{stab.get('cavity_count')} Helmholtz cavities")
        if stab.get("injector_stiffness", "nominal") != "nominal":
            aid_bits.append(f"{stab['injector_stiffness']} injector "
                            f"(dP/Pc {stab.get('effective_dp_over_pc', 0):.2f})")
        injector_lines += [
            "",
            "-- stability aids --",
            "aids: " + (", ".join(aid_bits) if aid_bits else "none"),
            f"aid mass: {stab.get('aid_mass_kg', 0.0):.1f} kg",
            (f"advisory: {stab['advisory'][:120]}" if stab.get("advisory") else
             "advisory: none (stable regime)"),
            (f"-> RESOLVED: {stab.get('resolution')}" if stab.get("advisory") and stab.get("resolved")
             else ("-> UNRESOLVED" if stab.get("advisory") else "")),
            "",
            "-- injector-face thermal --",
            f"chamber film: {cool.get('film_cooling_fraction', 0)*100:.1f}% of fuel  "
            f"(gas-side flux x{cool.get('film_flux_factor', 1.0):.2f} area-avg, "
            f"decaying curtain"
            + (f", ring at eps {cool.get('chamber_film_inject_area_ratio'):.2f}"
               if (cool.get('chamber_film_inject_area_ratio') or 0) > 1.0 else ", at the face")
            + f"; post-jacket fuel ~{(cool.get('film_temperature_k') or 0):.0f} K)",
            (f"nozzle slot film: {cool.get('nozzle_film_fraction', 0)*100:.1f}% of fuel at eps "
             f"{cool.get('nozzle_film_inject_eps', 0):.1f}  (Isp -"
             f"{(cool.get('nozzle_film_isp_penalty_fraction') or 0)*100:.2f}%)"
             if (cool.get('nozzle_film_fraction') or 0) > 0 else "nozzle slot film: off"),
            (f"hottest cooled wall ~{cool['peak_wall_temp_k']:.0f} K in the "
             f"{cool.get('peak_wall_temp_zone')} ({cool.get('peak_wall_margin_ratio', 0):.2f}x "
             f"margin, full-length balance)" if cool.get('peak_wall_temp_k')
             else "full-length wall balance: n/a (needs 'channels' regen model)"),
            f"throat flux {cool.get('q_throat_w_m2', 0)/1e6:.1f} MW/m2   "
            f"wall temp ~{(cool.get('t_wg_throat_k') or 0):.0f} K",
        ]
        if cool.get("regen_channel_model") == "channels" and cool.get("coolant_channels"):
            injector_lines += [
                "",
                "-- regen coolant channels --",
                f"{cool['coolant_channels']} channels, Dh_throat "
                f"{cool.get('coolant_channel_dh_throat_m', 0)*1e3:.2f} mm",
                f"coolant exit ~{(cool.get('coolant_exit_t_k') or 0):.0f} K "
                f"(+{cool.get('coolant_delta_t_k', 0):.0f} K)   "
                f"T_wc,throat ~{(cool.get('coolant_side_wall_t_throat_k') or 0):.0f} K",
                f"jacket dP {cool.get('jacket_dp_pa', 0)/1e6:.2f} MPa "
                f"(feeds pump discharge)",
            ]
        else:
            injector_lines += [
                "",
                f"-- regen cooling: flat model (jacket dP "
                f"{cool.get('jacket_dp_pa', 0)/1e6:.2f} MPa) --",
            ]
        self._set_text(self.injector_details, "\n".join(injector_lines))

        self._set_text(self.material_details,
                        "\n".join(self._material_detail_lines(materials.MATERIALS[self.design.material_key])))
        self._set_text(self.bell_material_details,
                        "\n".join(self._material_detail_lines(materials.MATERIALS[self.design.bell_material_key])))

        ctrl = controller_tech.CONTROLLER_TECHS[self.design.controller_tech_key]
        rel = reliability.derived_reliability(self.design, result, ctrl)
        controller_lines = [
            ctrl.display_name, ctrl.notes,
            f"Throttle response rate: {ctrl.throttle_response_rate:.2f}   "
            f"Relative cost factor: {ctrl.relative_cost_factor:.1f}",
            f"varyIsp: {ctrl.vary_isp:.3f}   varyMixture: {ctrl.vary_mixture:.3f}   "
            f"residualsThresholdBase: {ctrl.residuals_threshold_base:.3f}",
            f"DERIVED reliability (tier {ctrl.cycle_reliability_start:.3f} anchor, "
            f"cycle x{rel['cycle_base']:.2f}, risk x{rel['risk_multiplier']:.2f}):",
            f"  ignition {rel['ignition_reliability_start']:.3f}-{rel['ignition_reliability_end']:.3f}   "
            f"cycle {rel['cycle_reliability_start']:.3f}-{rel['cycle_reliability_end']:.3f}",
        ]
        self._set_text(self.controller_details, "\n".join(controller_lines))

        cyc = result["cycle_result"]
        lines = [
            f"Isp vac / sl:       {result['isp_vac_engine_s']:.1f} / {result['isp_sl_engine_s']:.1f} s",
            f"Thrust vac @100%:   {result['thrust_vac_n']/1e3:.1f} kN",
            f"Thrust vac @floor:  {result['thrust_vac_floor_n']/1e3:.1f} kN",
            f"Thrust sl  @100%:   {result['thrust_sl_n']/1e3:.1f} kN",
            f"mdot:               {result['mdot_kgs']:.1f} kg/s",
            f"Tc / gamma:         {result['tc_k']:.0f} K / {result['gamma']:.3f}",
            f"c* / eta_cstar:     {result['cstar_ms']:.0f} m/s / {result['eta_cstar']:.3f}",
            f"Combustion completeness: {result['completeness_factor']:.3f}  "
            f"(residence {result['residence_time_s']*1000:.3f} ms vs. needed "
            f"{result['required_time_s']*1000:.3f} ms)",
            f"Nozzle efficiency:  {result['nozzle_divergence_efficiency']:.4f}",
        ]
        if result["theta_n_deg"] is not None:
            lines.append(f"Bell theta_n/e:     {result['theta_n_deg']:.1f} / {result['theta_e_deg']:.1f} deg")
        _chf = result.get("chamber_flow", {})
        lines += [
            f"Throat / exit dia:  {result['geometry']['throat_dia_m']*100:.1f} / "
            f"{result['geometry']['exit_dia_m']*100:.1f} cm",
            f"Chamber dia:        {result['geometry']['chamber_dia_m']*100:.1f} cm  "
            f"L/D {result.get('chamber_l_over_d', 0):.2f}  stay {result.get('stay_time_s', 0)*1e3:.1f} ms",
            f"Chamber gas Mach:   {_chf.get('mach', 0):.2f}  -> injector-end Pc "
            f"{_chf.get('injector_end_pressure_ratio', 1):.3f}x nozzle Pc "
            f"({'fed to pump' if self.design.apply_chamber_pressure_loss else 'shown only'})",
            f"Chamber material margin: {result['material_margin']['margin_ratio']:.2f}x "
            f"(wall temp ~{(result['cooling'].get('t_wg_throat_k') or 0):.0f} K, "
            f"CR flux factor {result['chamber_heat_flux_factor']:.2f}x)",
            f"Bell material margin:    {result['bell_material_margin']['margin_ratio']:.2f}x @ "
            f"{('radiative eq ~%.0f K' % result['cooling']['bell_wall_temp_k']) if result['cooling'].get('bell_wall_temp_k') else 'local T %.0f K' % result['t_local_at_transition_k']}",
            f"Wall heat flux:     {result['cooling']['q_throat_w_m2']/1e6:.1f} MW/m2 throat, "
            f"h_g {result['cooling']['hg_throat_w_m2k']:.0f} W/m2/K, "
            f"{result['cooling']['wall_heat_total_w']/1e6:.1f} MW total",
            f"Regen coolant dT:   {result['cooling']['coolant_delta_t_k']:.0f} K"
            + (f" (limit ~{result['cooling']['coolant_limit_k']:.0f} K)"
               if result['cooling'].get('coolant_limit_k') else "")
            + (f"   Isp credit +{result['cooling']['regen_isp_bonus_fraction']*100:.2f}%"
               if result['cooling'].get('regen_isp_bonus_fraction') else ""),
            f"Throat fatigue:     ~{result['cooling']['throat_fatigue_cycles']:,.0f} thermal cycles "
            f"(through-wall dT {result['cooling']['through_wall_delta_t_k']:.0f} K)",
        ]
        if result["cooling"].get("dump_isp_penalty_fraction"):
            lines.append(
                f"Dump-cooled nozzle: {result['cooling']['dump_coolant_fraction']*100:.1f}% of fuel, "
                f"dT {result['cooling']['dump_coolant_dt_k']:.0f} K, "
                f"Isp penalty -{result['cooling']['dump_isp_penalty_fraction']*100:.2f}%")
        if cyc["has_turbopump"]:
            tp = cyc["turbopump"]
            lines.append(f"Turbopump power:    {tp['power_total_w']/1e6:.2f} MW  "
                         f"(est. mass {tp['turbopump_mass_kg']:.1f} kg)")
            if "feasibility_margin" in cyc:
                lines.append(f"Expander heat pickup:{cyc['heat_pickup_w']/1e3:.1f} kW  "
                              f"(flux {cyc['heat_flux_w_m2']/1e6:.2f} MW/m2 x {cyc['cooled_area_m2']:.3f} m2)")
                lines.append(f"Turbine power avail/req: {cyc['available_turbine_power_w']/1e3:.1f} / "
                             f"{cyc['required_turbine_power_w']/1e3:.1f} kW  "
                             f"(feasibility margin {cyc['feasibility_margin']:.2f})")
            elif "battery_mass_kg" in cyc:
                lines.append(f"Battery + motor:    {cyc['battery_mass_kg']:.0f} + "
                             f"{cyc['motor_mass_kg']:.0f} kg  "
                             f"({cyc['electrical_energy_j']/3.6e6:.1f} kWh, "
                             f"{cyc['electrical_power_w']/1e3:.0f} kW elec)")
            elif "preburner_flow_fraction" in cyc:
                lines.append(f"Preburner fraction: {cyc['preburner_flow_fraction']*100:.1f}%  "
                             f"({cyc['preburner_gas_kind'].replace('_', '-')} gas "
                             f"~{cyc['drive_gas']['tin_k']:.0f} K)")
            else:
                gg_label = ("Chamber tap-off" if cyc["cycle"] == "tap_off" else "GG flow")
                lines.append(f"{gg_label} fraction: {cyc['gg_flow_fraction']*100:.2f}%")
        else:
            lines.append(f"Required tank Pa:   {cyc['required_tank_pressure_pa']/1e6:.2f} MPa")
        onset = result["separation_onset_throttle"]
        if onset:
            lines.append(f"SL separation onset:{onset*100:.0f}% throttle")
        elif result["separated_at_100pct_sl"]:
            lines.append("SL: separated across the whole throttle range")
        else:
            lines.append("SL: attached across the whole throttle range")

        self._set_text(self.readout, "\n".join(lines))
        self._set_text(self.warnings_box, "\n".join(result["warnings"]) if result["warnings"] else "(none)")
        self._populate_checklist(result["checklist"])

        tp_tech = turbopump_tech.TURBOPUMP_TECHS[self.design.turbopump_tech_key]
        tp_lines = [
            f"Build quality: {tp_tech.display_name} (x{tp_tech.build_quality_factor:.2f} on "
            f"derived efficiency)   Tech era: {tp_tech.tech_era_hint}",
        ]
        if cyc["has_turbopump"]:
            tpump = cyc["turbopump"]
            sizing = result.get("turbopump_sizing")
            if sizing:
                tp_lines += [
                    f"DERIVED efficiency: fuel pump {sizing['eta_pump_fuel']:.3f}, "
                    f"ox pump {sizing['eta_pump_ox']:.3f}, turbine {sizing['eta_turbine']:.3f}  "
                    f"(overall {sizing['eta_overall']:.3f})",
                ]
                if self.design.eta_pump_fuel > 0 or self.design.eta_pump_ox > 0:
                    tp_lines.append(f"  (manual pump-eta override active: "
                                    f"{self.design.eta_pump_fuel:.2f} / {self.design.eta_pump_ox:.2f})")
            tp_lines += [
                "",
                f"Turbopump power: {tpump['power_total_w']/1e6:.2f} MW",
                f"Fuel/ox mass flow: {tpump['mdot_fuel_kgs']:.2f} / {tpump['mdot_ox_kgs']:.2f} kg/s",
                f"Fuel/ox pump power: {tpump['power_fuel_w']/1e3:.1f} / {tpump['power_ox_w']/1e3:.1f} kW",
            ]
            if "feasibility_margin" in cyc:
                tp_lines.append(f"Expander feasibility margin: {cyc['feasibility_margin']:.2f}")
            elif "battery_mass_kg" in cyc:
                tp_lines.append(
                    f"Battery {cyc['battery_mass_kg']:.0f} kg + motor {cyc['motor_mass_kg']:.0f} kg "
                    f"({cyc['electrical_energy_j']/3.6e6:.1f} kWh, {cyc['electrical_power_w']/1e3:.0f} kW "
                    f"electrical) - no turbine, no bleed")
            elif "preburner_flow_fraction" in cyc:
                dg = cyc["drive_gas"]
                tp_lines.append(
                    f"Preburner: {cyc['preburner_gas_kind'].replace('_', '-')} drive gas, "
                    f"{cyc['preburner_flow_fraction']*100:.1f}% of total flow "
                    f"({cyc['gg_mdot_kgs']:.1f} kg/s), ~{dg['tin_k']:.0f} K, cp {dg['cp']:.0f} - "
                    f"closed cycle (no dump loss)")
                if "power_margin" in cyc:
                    pc_ref = max(result.get("pc_feed_pa", 0.0) or 0.0, 1.0)
                    tp_lines.append(
                        "Power balance: " + ("closes" if cyc["feasible"] else "DOES NOT CLOSE")
                        + f" (margin {cyc['power_margin']:.2f}); preburner "
                        f"{cyc['preburner_pressure_pa']/1e6:.1f} MPa ({cyc['preburner_pressure_pa']/pc_ref:.2f} x Pc)")
                    for sd in cyc.get("preburner_sides", []):
                        tp_lines.append(
                            f"  {sd['kind'].replace('_', '-')} turbine: solved PR {sd['pr']:.2f} @ "
                            f"{sd['gas']['tin_k']:.0f} K, {sd['mdot_turbine_kgs']:.1f} kg/s")
                    tp_lines.append(
                        f"Pump discharge: fuel {cyc['pump_discharge_fuel_pa']/1e6:.1f} MPa "
                        f"({cyc['pump_discharge_fuel_pa']/pc_ref:.2f} x Pc), ox "
                        f"{cyc['pump_discharge_ox_pa']/1e6:.1f} MPa "
                        f"({cyc['pump_discharge_ox_pa']/pc_ref:.2f} x Pc)")
            elif cyc["cycle"] == "tap_off":
                tap_tin = cyc.get("drive_gas", {}).get("tin_k", 0.0)
                tp_lines.append(
                    f"Chamber tap-off: {cyc['gg_flow_fraction']*100:.2f}% of flow, film-cooled to "
                    f"~{tap_tin:.0f} K (dump Isp fraction {cyc['gg_dump_isp_fraction']:.2f})")
            else:
                tp_lines.append(f"GG flow fraction: {cyc['gg_flow_fraction']*100:.2f}%")
            sizing = result.get("turbopump_sizing")
            if sizing:
                fp, op, turb = sizing["fuel_pump"], sizing["ox_pump"], sizing["turbine"]
                tp_lines += [
                    "",
                    f"Architecture: {sizing['arrangement'].replace('_', ' ')} "
                    f"({'auto' if self.design.turbopump_arrangement == 'auto' else 'override'}), "
                    f"{sizing['n_turbines']} turbine(s), {sizing['turbine_staging'].replace('_', ' ')}",
                    f"Material: {sizing['material_display']}",
                    f"Fuel pump: {fp['n_stages']}-stage, {fp['n_rpm']:,.0f} rpm, "
                    f"tip {fp['u_tip_m_s']:.0f} m/s ({100.0/fp['tip_speed_margin']:.0f}% of limit)",
                    f"Ox pump:   {op['n_stages']}-stage, {op['n_rpm']:,.0f} rpm, "
                    f"tip {op['u_tip_m_s']:.0f} m/s ({100.0/op['tip_speed_margin']:.0f}% of limit)",
                ]
                if turb:
                    tp_lines.append(f"Turbine pitchline: {turb['u_pitchline_m_s']:.0f} m/s "
                                    f"(U/C0 {turb['u_over_c0']:.2f}), gas inlet {sizing['turbine_inlet_k']:.0f} K")
                tp_lines.append(
                    f"Bearings ({sizing['bearing_material_display']}): fuel DN "
                    f"{sizing['fuel_bearing_dn']:,.0f} / ox DN {sizing['ox_bearing_dn']:,.0f} mm*rpm "
                    f"(engineering-estimate limits, not literature-sourced - see ASSUMPTIONS.md)")
                for _nm, _pp in (("Fuel", fp), ("Ox", op)):
                    if _pp.get("suction_limited"):
                        tp_lines.append(
                            f"{_nm} pump SUCTION-LIMITED: {_pp['rpm_ns_optimum']:,.0f} -> "
                            f"{_pp['n_rpm']:,.0f} rpm at {_pp['npsh_available_ft']:.0f} ft NPSH available")
                tp_lines.append(
                    f"Inlet eye: fuel {1000.0 * fp.get('inlet_eye_dia_m', 0.0):.0f} mm / ox "
                    f"{1000.0 * op.get('inlet_eye_dia_m', 0.0):.0f} mm; feed-line loss fuel "
                    f"{result.get('line_loss_fuel_pa', 0.0) / 1e3:.0f} kPa "
                    f"({(result.get('line_loss_source') or {}).get('fuel', 'flat')}) / ox "
                    f"{result.get('line_loss_ox_pa', 0.0) / 1e3:.0f} kPa "
                    f"({(result.get('line_loss_source') or {}).get('ox', 'flat')})")
                if self.design.enforce_suction_limit:
                    tp_lines.append(
                        f"NPSH required: fuel ~{fp['npsh_required_ft']:.0f} ft / "
                        f"ox ~{op['npsh_required_ft']:.0f} ft (REQUIRED, not available - "
                        f"this tool has no tank/vapor-pressure model)")
                tp_lines.append(
                    f"Assembly: ~{sizing['assembly_length_m']:.2f} x {sizing['assembly_od_m']:.2f} m, "
                    f"{sizing['mass_kg']*sizing['mass_modifier']:.0f} kg "
                    f"(SP-8107 mass-vs-power trend; envelope x-check {sizing['mass_geometry_kg']:.0f} kg)")
                tp_lines.append(f"Dry-mass modifier: x{sizing['mass_modifier']:.3f}  "
                                f"({'FEASIBLE' if sizing['feasible'] else 'MARGINAL'})")
                for w in sizing["warnings"]:
                    tp_lines.append(f"  [!] {w}")
        else:
            tp_lines += ["", "Not applicable - pressure-fed cycle has no turbopump."]
        self._set_text(self.turbopump_details, "\n".join(tp_lines))

        ctrl_tech = controller_tech.CONTROLLER_TECHS[self.design.controller_tech_key]
        is_ablative = materials.MATERIALS[self.design.material_key].cooling_method == "ablative"
        _rated, tested_burn_time_s = reliability.derived_burn_times(
            self.design, result, ctrl_tech, is_ablative=is_ablative)
        rated_line = (f"Rated burn time: {result['rated_burn_time_s']:.0f} s "
                      f"(ablative char-consumption limited)" if is_ablative else
                      f"Rated burn time: {result['rated_burn_time_s']:.0f} s")
        tested_line = ("Tested burn time: same as rated (ablative, no extra time)" if is_ablative else
                       f"Tested burn time: {tested_burn_time_s:.0f} s "
                       f"(x{tested_burn_time_s/max(result['rated_burn_time_s'],1e-9):.1f})")

        # Cost estimate (physics/cost_model.py). Pushed into the export fields
        # unless the user has manually edited them (self._cost_overridden).
        cost_est = self._compute_cost(result)
        stability_aid_mass = result.get("stability_aid_mass_kg", 0.0)
        injector_plate_mass = result.get("injector_plate_mass_kg", 0.0)
        manifold_mass = result.get("manifold_mass_kg", 0.0)
        plumbing_mass = result.get("plumbing_mass_kg", 0.0)
        turbopump_mass = (result['computed_dry_mass_kg'] - result['chamber_wall_mass_kg']
                          - result['bell_wall_mass_kg'] - stability_aid_mass - injector_plate_mass
                          - manifold_mass - plumbing_mass)
        _mr = result.get("manifold_result", {})
        mass_burn_lines = [
            f"Chamber/nozzle wall mass: {result['chamber_wall_mass_kg']+result['bell_wall_mass_kg']:.1f} kg",
            f"Injector plate mass: {injector_plate_mass:.1f} kg",
            f"Manifold mass: {manifold_mass:.1f} kg (fuel "
            f"{_mr.get('fuel', {}).get('mass_kg', 0.0):.1f} + ox "
            f"{_mr.get('ox', {}).get('mass_kg', 0.0):.1f})",
            f"Turbopump mass: {turbopump_mass:.1f} kg",
        ]
        if plumbing_mass > 0.0:
            _pr = result.get("plumbing_results", [])
            mass_burn_lines.append(
                f"Plumbing mass: {plumbing_mass:.1f} kg ("
                + ", ".join(f"{p['host']}: {p['n_pipes']} pipes/{p['n_flanges']} flanges, "
                            f"{p['total_length_m']:.2f} m" for p in _pr) + ")")
        if stability_aid_mass > 0.0:
            mass_burn_lines.append(f"Stability-aid mass: {stability_aid_mass:.1f} kg "
                                   f"(baffle / cavities)")
        mass_burn_lines += [
            f"Estimated dry mass: {result['computed_dry_mass_kg']:.1f} kg "
            f"(LOWER BOUND - no valves/actuators/mounting structure)",
            rated_line,
            tested_line,
        ]
        if self.design.output_mode != "additional_config":
            engine_len = result["profile_meta"]["total_length_m"]
            native_h = self._host_native_height_m()
            scale = self._compute_model_scale()
            if scale is not None:
                src = ("manual" if self.design.host_model_reference_height_m > 0
                       else "ROEngines")
                mass_burn_lines.append(
                    f"Model scale: engine {engine_len:.2f} m / host {native_h:.2f} m "
                    f"({src}) -> rescaleFactor x{scale:.3f}")
            else:
                mass_burn_lines.append(
                    f"Model scale: no known height for host '{self.design.host_model_engine_type}'"
                    f" - set a reference height or export won't rescale")
        mass_burn_lines += [
            "",
            f"Estimated cost {cost_est['cost']} / entryCost {cost_est['entry_cost']}"
            + ("  (auto - editable in the fields below)" if not self._cost_overridden
               else "  (fields below manually overridden)"),
        ]
        self._set_text(self.mass_burn_details, "\n".join(mass_burn_lines))

    def _material_detail_lines(self, mat):
        return [
            mat.display_name,
            mat.notes,
            f"Density: {mat.density_kg_m3:.0f} kg/m3   Relative cost factor: {mat.relative_cost_factor:.1f}",
            f"Cooling method: {mat.cooling_method}   Cooling effectiveness: {mat.cooling_effectiveness:.2f}",
            f"Allowable stress: {mat.allowable_stress_pa/1e6:.0f} MPa (drives wall thickness/mass - "
            f"physics/mass_model.py)",
            f"Thermal conductivity: {mat.thermal_conductivity_w_mk:.1f} W/m-K "
            f"(informational only, not used in the margin calc)",
            f"Tech era: {mat.tech_era_hint}",
        ]

    def _populate_checklist(self, checklist):
        self.checklist_tree.delete(*self.checklist_tree.get_children())
        by_category = {}
        for item in checklist:
            by_category.setdefault(item["category"], []).append(item)
        for category in CHECKLIST_CATEGORY_ORDER:
            items = by_category.get(category)
            if not items:
                continue
            cat_id = self.checklist_tree.insert("", "end", text=category, open=True)
            for item in items:
                status = "PASS" if item["passed"] else "WARN"
                tag = "pass" if item["passed"] else "fail"
                self.checklist_tree.insert(cat_id, "end", text=item["name"],
                                            values=(status, item["detail"]), tags=(tag,))

    def _set_text(self, widget, text):
        widget.configure(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    # --------------------------------------------------------- project New/Save/Load
    def _refresh_widgets_from_design(self):
        """Push every field of self.design back into its tk var / widget. The
        exact inverse of _on_control_change + _on_export_field_change - keep the
        two in lockstep. Caller must have set self._loading = True so the traces
        this fires are suppressed; the caller does one recompute() at the end.
        """
        d = self.design
        mat_key_to_disp = {k: v for v, k in self.material_display_to_key.items()}
        inj_key_to_disp = {k: v for v, k in self.injector_display_to_key.items()}
        ign_key_to_disp = {k: v for v, k in self.ignition_display_to_key.items()}
        ctl_key_to_disp = {k: v for v, k in self.controller_display_to_key.items()}
        tpt_key_to_disp = {k: v for v, k in self.turbopump_display_to_key.items()}
        tpm_key_to_disp = {k: v for v, k in self.turbopump_material_display_to_key.items()}
        bearing_key_to_disp = {k: v for v, k in self.bearing_material_display_to_key.items()}
        host_type_to_disp = {t: lbl for lbl, t in self.host_display_to_type.items()}

        # dropdowns
        self.pair_var.set(d.propellant_pair)
        self.cycle_var.set(CYCLE_DISPLAY.get(d.cycle, self.cycle_var.get()))
        self.nozzle_type_var.set(NOZZLE_TYPE_DISPLAY.get(d.nozzle_type, self.nozzle_type_var.get()))
        self.material_var.set(mat_key_to_disp.get(d.material_key, self.material_var.get()))
        self.bell_material_var.set(mat_key_to_disp.get(d.bell_material_key, self.bell_material_var.get()))
        self.injector_var.set(inj_key_to_disp.get(d.injector_type, self.injector_var.get()))
        self.ignition_var.set(ign_key_to_disp.get(d.ignition_system, self.ignition_var.get()))
        self.controller_var.set(ctl_key_to_disp.get(d.controller_tech_key, self.controller_var.get()))
        self.gimbal_mode_var.set(GIMBAL_MODE_DISPLAY.get(d.gimbal_mode, self.gimbal_mode_var.get()))
        self.turbopump_tech_var.set(tpt_key_to_disp.get(d.turbopump_tech_key, self.turbopump_tech_var.get()))
        self.turbopump_arrangement_var.set(d.turbopump_arrangement)
        self.turbine_staging_var.set(d.turbine_staging)
        self.turbopump_material_var.set(tpm_key_to_disp.get(d.turbopump_material_key,
                                                            self.turbopump_material_var.get()))
        self.bearing_material_var.set(bearing_key_to_disp.get(d.bearing_material_key,
                                                              self.bearing_material_var.get()))
        self.suction_limit_var.set(bool(d.enforce_suction_limit))
        self.npsh_fuel_var.set(d.npsh_available_fuel_ft)
        self.npsh_ox_var.set(d.npsh_available_ox_ft)
        self.pb_tin_fr_var.set(d.preburner_tin_k)
        self.pb_tin_or_var.set(d.ox_preburner_tin_k)
        self.orifice_type_var.set(d.orifice_type)
        self.stiffness_var.set(d.injector_stiffness)
        self.chamber_sizing_method_var.set(d.chamber_sizing_method)
        self.chamber_cooling_method_var.set(d.chamber_cooling_method)
        self.nozzle_cooling_method_var.set(d.nozzle_cooling_method)
        self.regen_nozzle_end_var.set(d.regen_nozzle_end_eps)
        self.dump_coolant_fraction_var.set(d.dump_coolant_fraction * 100.0)
        self.wall_construction_var.set(d.wall_construction)
        self.cooling_flow_topology_var.set(d.cooling_flow_topology)
        self.manifold_bypass_var.set(d.manifold_bypass_fraction * 100.0)
        self.jacket_inlet_eps_var.set(d.jacket_inlet_eps)
        self.chamber_tube_jacket_var.set(bool(d.chamber_tube_jacket))
        self.tube_split_eps_var.set(d.tube_split_eps)
        self.tube_hatbands_var.set(bool(d.tube_hatbands))
        self.tube_hatbands_on_extension_var.set(bool(d.tube_hatbands_on_extension))
        self.tube_hatband_count_var.set(float(d.tube_hatband_count))
        self.tube_hatband_width_var.set(d.tube_hatband_width_m * 1000.0)
        self.tube_hatband_shape_var.set(hatbands.BAND_SHAPE_LABELS.get(
            d.tube_hatband_shape, hatbands.BAND_SHAPE_LABELS["auto"]))
        self.tube_hatband_material_var.set(
            {v: k for k, v in self.material_display_to_key.items()}.get(
                d.tube_hatband_material, self.tube_hatband_material_var.get()))
        self.flange_thickness_var.set(d.flange_thickness_m * 1000.0)
        self.flange_width_var.set(d.flange_width_m * 1000.0)
        self.flange_bolt_count_var.set(float(d.flange_bolt_count))
        self.regen_channel_model_var.set(d.regen_channel_model)
        self.output_mode_var.set(OUTPUT_MODE_DISPLAY.get(d.output_mode, self.output_mode_var.get()))
        if d.host_model_engine_type in host_type_to_disp:
            self.host_var.set(host_type_to_disp[d.host_model_engine_type])

        # sliders / scaled numeric vars
        mr_lo, mr_hi = combustion.mr_bounds(d.propellant_pair)
        self.mr_scale.configure(from_=mr_lo, to=mr_hi)
        self.pc_var.set(d.chamber_pressure_pa / 1e6)
        self.mr_var.set(d.mixture_ratio)
        self.eps_var.set(d.expansion_ratio)
        self.half_angle_var.set(d.nozzle_half_angle_deg)
        self.bell_pct_var.set(d.bell_percent_length)
        self.contraction_var.set(d.contraction_ratio)
        self.lstar_var.set(d.lstar_m)
        self.chamber_residence_time_var.set(d.chamber_residence_time_ms)
        self.chamber_wall_fillet_var.set(d.chamber_wall_fillet_r_over_rt)
        self.convergent_angle_var.set(d.convergent_half_angle_deg)
        self.impingement_var.set(d.impingement_angle_deg)
        self.fuel_manifold_head_var.set(d.fuel_manifold_head_fraction * 100.0)
        self.ox_manifold_head_var.set(d.ox_manifold_head_fraction * 100.0)
        self.fuel_manifold_taper_var.set(d.fuel_manifold_taper_blend)
        self.ox_manifold_taper_var.set(d.ox_manifold_taper_blend)
        self.jacket_inlet_taper_var.set(d.jacket_inlet_taper_blend)
        self.jacket_inlet_vmult_var.set(d.jacket_inlet_velocity_mult)
        self.cooling_transition_var.set(d.cooling_transition_eps)
        self.film_cooling_var.set(d.film_cooling_fraction * 100.0)
        self.chamber_film_inject_var.set(d.chamber_film_inject_area_ratio)
        self.nozzle_film_var.set(d.nozzle_film_fraction * 100.0)
        self.nozzle_film_eps_var.set(d.nozzle_film_inject_eps)
        self.regen_channel_count_var.set(float(d.regen_channel_count))
        self.regen_channel_aspect_var.set(d.regen_channel_aspect_ratio)
        self.regen_channel_land_var.set(d.regen_channel_land_fraction)
        self.regen_coolant_velocity_var.set(d.regen_coolant_velocity_ms)
        self.gimbal_range_var.set(d.gimbal_range_deg)
        self.gimbal_response_var.set(d.gimbal_response_speed_deg_s)
        self.eta_pump_fuel_var.set(d.eta_pump_fuel)
        self.eta_pump_ox_var.set(d.eta_pump_ox)
        self.specific_power_var.set(d.pump_specific_power_w_kg / 1e3)
        self.throttle_var.set(d.throttle_floor)

        # bools / combos / spinboxes / string-numerics
        self.pc_loss_var.set(bool(d.apply_chamber_pressure_loss))
        self.baffles_var.set(bool(d.injector_baffles))
        self.baffle_comp_var.set(str(d.baffle_compartments))
        self.cavities_var.set(bool(d.acoustic_cavities))
        self.cavity_count_var.set(str(d.acoustic_cavity_count))
        self.thrust_var.set(f"{d.target_vac_thrust_n / 1e3:.1f}")
        self.tech_node_var.set(d.tech_node)
        self.entry_cost_var.set(f"{d.entry_cost:.0f}")
        self.cost_var.set(f"{d.cost:.0f}")
        self.ignitions_var.set(str(d.ignitions))
        self.export_name_var.set(d.config_name)
        self.host_ref_height_var.set(f"{d.host_model_reference_height_m:g}")
        self.new_part_name_var.set(d.new_part_name)
        self.new_part_title_var.set(d.new_part_title)
        self.new_part_mfr_var.set(d.new_part_manufacturer)

    def _load_into_gui(self, new_design):
        self._loading = True
        try:
            self.design = new_design
            if self.catalog and not self.design.host_model_engine_type:
                self.design.host_model_engine_type = self.catalog[0]["engine_type"]
            self._refresh_widgets_from_design()
        finally:
            self._loading = False
        self._on_control_change()   # one sync + recompute, re-reading every var

    def _on_new(self):
        self._cost_overridden = False
        self._current_project_path = None
        self._load_into_gui(EngineDesign())
        self._set_title()

    def _write_project(self, path):
        self._on_export_field_change()   # flush export-only fields onto self.design
        try:
            project_io.save_design(path, self.design)
        except Exception as exc:
            messagebox.showerror("Save failed", str(exc))
            return False
        self._current_project_path = path
        self._set_title()
        return True

    def _on_save(self):
        """Save As - always prompt for a path."""
        self._on_export_field_change()
        name = self.design.config_name.strip() or "design"
        path = filedialog.asksaveasfilename(
            defaultextension=project_io.FILE_SUFFIX, initialfile=f"{name}{project_io.FILE_SUFFIX}",
            filetypes=[("Engine designer project", "*" + project_io.FILE_SUFFIX)])
        if not path:
            return
        if self._write_project(path):
            messagebox.showinfo("Saved", f"Wrote {path}")

    def _on_save_current(self):
        """Save - write straight to the current file, or fall back to Save As."""
        if self._current_project_path:
            self._write_project(self._current_project_path)
        else:
            self._on_save()

    def _on_load(self):
        path = filedialog.askopenfilename(
            filetypes=[("Engine designer project", "*" + project_io.FILE_SUFFIX)])
        if not path:
            return
        try:
            if project_io.file_schema_version(path) > EngineDesign.SCHEMA_VERSION:
                messagebox.showwarning(
                    "Newer file",
                    "This project was saved by a newer version of the tool; loading best-effort.")
            self._cost_overridden = True   # a loaded design carries its own cost/entryCost
            self._load_into_gui(project_io.load_design(path))
            self._current_project_path = path
            self._set_title()
        except Exception as exc:
            messagebox.showerror("Load failed", str(exc))

    def _on_export(self):
        if self.last_result is None:
            return
        self._on_export_field_change()
        d = self.design
        default_name = (d.new_part_name.strip()
                        if d.output_mode == "new_part_standalone" and d.new_part_name.strip()
                        else d.config_name.strip() or "MyEngine")
        path = filedialog.asksaveasfilename(
            defaultextension=".cfg", initialfile=f"{default_name}_Config.cfg",
            filetypes=[("KSP config", "*.cfg")])
        if not path:
            return
        try:
            write_cfg(path, d, self.last_result, config_name=d.config_name.strip() or "MyEngine",
                      tech_node=d.tech_node or None,
                      entry_cost=d.entry_cost, cost=d.cost,
                      mass_mult=self._compute_mass_mult(),
                      output_mode=d.output_mode,
                      model_scale=self._compute_model_scale(),
                      new_part={"name": d.new_part_name, "title": d.new_part_title,
                                "manufacturer": d.new_part_manufacturer,
                                "description": d.new_part_description})
        except Exception as exc:
            messagebox.showerror("Export failed", str(exc))
            return
        messagebox.showinfo("Exported", f"Wrote {path}")

    def _compute_cost(self, result):
        """Estimate cost / entryCost (physics/cost_model.py) and, unless the user
        has manually edited the export fields, push the estimate into them so the
        exported .cfg and the GUI stay in sync. (Setting a StringVar does not
        fire the fields' <KeyRelease> binding, so there is no feedback loop.)"""
        est = cost_model.estimate_cost(self.design, result)
        if not self._cost_overridden:
            self.design.cost = float(est["cost"])
            self.design.entry_cost = float(est["entry_cost"])
            self.cost_var.set(str(est["cost"]))
            self.entry_cost_var.set(str(est["entry_cost"]))
        return est

    def _compute_mass_mult(self):
        """massMult is a MULTIPLIER on the host RO part's own stock dry mass,
        not an absolute mass - so this design's computed_dry_mass_kg needs to
        be divided by the host's real stock dry mass (already scraped from
        Engine_Configs into catalog.json) to get a real ratio. Falls back to
        cfg_writer.py's default (1.0 - "keep the host part's stock mass") if
        the host's dry_mass isn't available in the catalog."""
        for entry in self.catalog:
            if entry.get("engine_type") == self.design.host_model_engine_type:
                try:
                    host_dry_mass_kg = float(entry.get("dry_mass"))
                    if host_dry_mass_kg > 0:
                        return self.last_result["computed_dry_mass_kg"] / host_dry_mass_kg
                except (TypeError, ValueError):
                    pass
                break
        return 1.0

    def _host_native_height_m(self):
        """Rendered height (m) of the current host model: the user's manual
        override if set, else the ROEngines snapshot, else None."""
        manual = self.design.host_model_reference_height_m
        if manual and manual > 0:
            return manual
        entry = self.roengines_models.get(self.design.host_model_engine_type)
        if entry and entry.get("native_height_m", 0) > 0:
            return float(entry["native_height_m"])
        return None

    def _compute_model_scale(self):
        """Uniform rescaleFactor multiplier for a borrowed host model =
        designed engine length / host model native height. None when there's no
        known native height (export then emits no rescale patch) or no result
        yet, or for the plain additional-CONFIG mode (nothing is rescaled)."""
        if self.design.output_mode == "additional_config" or self.last_result is None:
            return None
        native_h = self._host_native_height_m()
        if not native_h:
            return None
        designed_h = self.last_result["profile_meta"]["total_length_m"]
        if designed_h <= 0:
            return None
        return designed_h / native_h


def main():
    root = tk.Tk()
    EngineDesignerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
