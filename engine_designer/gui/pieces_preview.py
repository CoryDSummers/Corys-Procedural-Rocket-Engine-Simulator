"""
A reusable 3D preview for a prebuilt scene ({"pieces": [MeshBuffers, ...], "center",
"half"}) - the GL-or-matplotlib pattern of gui/shape_lab.py's _ShapeLabBase, lifted out
as a plain ttk.Frame for tabs that draw their own scene (the Turbopump 3D tab,
gui/turbopump_scene.py). Prefers the GPU EnginePreviewGLFrame (orbit camera, X-ray,
engineering shading) via its update_meshes(); falls back to a matplotlib Poly3DCollection
renderer if PyOpenGL/pyopengltk are missing or the GL widget fails to construct.

The Shape Lab isn't moved onto this yet (GUI-only code, can't be click-tested in the dev
sandbox - no $DISPLAY); syntax-checked by verify_all.sh.
"""
import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

try:
    from .preview3d_gl import EnginePreviewGLFrame
    _GL_AVAILABLE = True
except ImportError:
    _GL_AVAILABLE = False


class PiecesPreview(ttk.Frame):
    """show(scene) draws a {"pieces", "center", "half"} scene. `toolbar` is a frame
    above the viewport that callers may add their own controls to."""

    def __init__(self, parent, name="3D view", width=600, height=600):
        super().__init__(parent)
        self._name = name
        self._gl_frame = None
        self._fig = self._ax = self._canvas = None
        self.toolbar = ttk.Frame(self)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        body = ttk.Frame(self)
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        if _GL_AVAILABLE:
            try:
                self._gl_frame = EnginePreviewGLFrame(body, width=width, height=height)
                self._xray_var = tk.BooleanVar(value=False)
                ttk.Checkbutton(self.toolbar, text="X-ray", variable=self._xray_var,
                                command=lambda: self._gl_frame.set_xray(self._xray_var.get())
                                ).pack(side=tk.RIGHT, padx=4, pady=2)
                self._flat_var = tk.BooleanVar(value=False)
                ttk.Checkbutton(self.toolbar, text="Engineering shading",
                                variable=self._flat_var,
                                command=lambda: self._gl_frame.set_flat_shade(self._flat_var.get())
                                ).pack(side=tk.RIGHT, padx=4, pady=2)
                self._gl_frame.pack(fill=tk.BOTH, expand=True)
                return
            except Exception as exc:
                print(f"{name}: OpenGL widget failed to initialize, "
                      f"falling back to matplotlib: {exc}")
                for child in body.winfo_children():
                    child.destroy()
                self._gl_frame = None
        ttk.Label(body, text="PyOpenGL/pyopengltk not available - using the slower "
                  "matplotlib 3D view. See requirements.txt.").pack(fill=tk.X)
        self._fig = Figure(figsize=(6, 6))
        self._ax = self._fig.add_subplot(111, projection="3d")
        self._canvas = FigureCanvasTkAgg(self._fig, master=body)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show(self, scene):
        pieces = scene["pieces"]
        if self._gl_frame is not None:
            self._gl_frame.update_meshes(pieces, scene["center"], scene["half"])
            return
        ax = self._ax
        ax.clear()
        for mesh in pieces:
            triangles = mesh.vertices[mesh.indices]
            facecolors = mesh.colors[mesh.indices].mean(axis=1)
            ax.add_collection3d(Poly3DCollection(triangles, facecolor=facecolors,
                                                 edgecolor="none", alpha=1.0))
        cx, cy, cz = scene["center"]
        half = scene["half"]
        ax.set_xlim(cx - half, cx + half)
        ax.set_ylim(cy - half, cy + half)
        ax.set_zlim(cz - half, cz + half)
        ax.set_box_aspect((1, 1, 1))
        ax.set_xlabel("shaft axis [m]")
        ax.set_ylabel("y [m]")
        ax.set_zlabel("z [m]")
        self._canvas.draw_idle()
