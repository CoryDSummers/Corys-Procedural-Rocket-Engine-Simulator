"""
OpenGL-rendered 3D preview - the GL-context/widget layer. Everything
math/data-shape related (mesh-buffer construction primitives, camera state,
colormap sampling) lives in the gui/preview3d_gl_core/ package (pure numpy,
no OpenGL/Tk import, headlessly self-tested - split into submodules by
geometry-operation kind). Per-part mesh assembly (chamber/bell shell,
injector head, far-end cover, tube hatbands, flange joint, turbopump - what
used to be this file's own ~830-line `_build_mesh_data` method) lives in
gui/mesh_builder.py, also pure numpy/no OpenGL/Tk - split out specifically so
it's headlessly testable here too (`_build_mesh_data` never actually touched
`self`). This module is the thin layer that actually imports OpenGL/pyopengltk
and owns a live GL context - it CANNOT be imported or instantiated in a
sandbox without a display (this project's dev sandbox has none - see
CLAUDE.md's standing Tkinter caveat, which now also covers this module), so
it's syntax-checked only there
(`python3 -c "import ast; ast.parse(...)"`), never actually run.

gui/app.py imports this module inside a try/except ImportError and falls
back to gui/preview3d.py's matplotlib renderer if PyOpenGL/pyopengltk aren't
installed - see app.py's tab-setup code. gui/preview3d.py itself is
unmodified and kept as that fallback.

NOTE: the exact call pyopengltk.OpenGLFrame uses to request a one-shot
repaint (assumed below to be `event_generate("<Expose>")` with `animate=0`)
could not be confirmed against the actually-installed package version in
this sandbox (pyopengltk isn't installed here, and even if it were,
constructing the widget needs a live display). Double-check this against the
installed version's docs/source and adjust `_request_redraw` if it differs.
"""
import numpy as np
import OpenGL.GL as GL
from OpenGL.GL import shaders
import pyopengltk

from . import mesh_builder, preview3d_gl_core

_VERTEX_SHADER = """
attribute vec3 in_position;
attribute vec3 in_normal;
attribute vec3 in_color;
uniform mat4 u_view;
uniform mat4 u_proj;
varying vec3 v_normal;
varying vec3 v_color;
varying vec3 v_world_pos;
void main() {
    gl_Position = u_proj * u_view * vec4(in_position, 1.0);
    v_normal = in_normal;
    v_color = in_color;
    v_world_pos = in_position;
}
"""

_FRAGMENT_SHADER = """
varying vec3 v_normal;
varying vec3 v_color;
varying vec3 v_world_pos;
uniform vec3 u_light_dir;
uniform vec3 u_ambient;
uniform vec3 u_eye_pos;
uniform float u_specular_strength;
uniform float u_shininess;
uniform float u_flat_shade;
// X-ray (translucent layer) controls - see preview3d_gl_core/render_layers.py.
// u_alpha = 1.0 is the opaque layer: output identical to the pre-X-ray shader.
uniform float u_alpha;       // face-on opacity
uniform float u_rim_power;   // grazing-angle opacity rise (render_layers.rim_alpha)
uniform int u_facing_pass;   // 0 = all fragments, 1 = facing away from eye, 2 = facing eye
void main() {
    vec3 N = normalize(v_normal);
    vec3 V = normalize(u_eye_pos - v_world_pos);
    float ndotv = dot(N, V);
    // Split by normal vs view direction, not gl_FrontFacing: triangle winding
    // isn't consistent across the mesh builders, the outward normals are.
    if (u_facing_pass == 1 && ndotv >= 0.0) discard;
    if (u_facing_pass == 2 && ndotv < 0.0) discard;
    float alpha = 1.0;
    if (u_alpha < 1.0) {
        float grazing = 1.0 - clamp(abs(ndotv), 0.0, 1.0);
        alpha = u_alpha + (1.0 - u_alpha) * pow(grazing, u_rim_power);
    }
    if (u_flat_shade > 0.5) {
        gl_FragColor = vec4(v_color, alpha);
        return;
    }
    vec3 L = normalize(u_light_dir);
    float ndotl = max(dot(N, L), 0.0);
    vec3 H = normalize(L + V);
    float spec = u_specular_strength * pow(max(dot(N, H), 0.0), u_shininess);
    vec3 lit = u_ambient + v_color * ndotl + vec3(spec);
    gl_FragColor = vec4(min(lit, vec3(1.0)), alpha);
}
"""

# Minimal unlit vertex-color shader pair for the corner orientation gizmo -
# kept separate from the main shader above because the gizmo's vertex buffer
# is position+color only (stride 6 floats), not the main shader's interleaved
# position+normal+color (stride 9 floats); reusing one shader for two
# different vertex layouts would need two VAOs/attribute setups anyway, so a
# second minimal program is simpler and leaves the main render path
# untouched. Still VBO + shader + glDrawArrays, no immediate-mode GL.
_GIZMO_VERTEX_SHADER = """
attribute vec3 in_position;
attribute vec3 in_color;
uniform mat4 u_view;
uniform mat4 u_proj;
varying vec3 v_color;
void main() {
    gl_Position = u_proj * u_view * vec4(in_position, 1.0);
    v_color = in_color;
}
"""

_GIZMO_FRAGMENT_SHADER = """
varying vec3 v_color;
void main() {
    gl_FragColor = vec4(v_color, 1.0);
}
"""

#: Fixed on-screen size (px) and corner margin (px) for the orientation gizmo.
_GIZMO_MAX_PX = 80
_GIZMO_MARGIN_PX = 8


class EnginePreviewGLFrame(pyopengltk.OpenGLFrame):
    """
    Tkinter-native OpenGL canvas (drop-in replacement for the old
    Figure/FigureCanvasTkAgg pair) showing the same revolved-profile engine
    preview as gui/preview3d.py, GPU-rendered with an orbit camera and an
    optional heat-flux colormap overlay.
    """

    def __init__(self, master, clear_color=(0.10, 0.10, 0.12), light_dir=(0.4, 0.6, 0.7), **kwargs):
        super().__init__(master, **kwargs)
        self._clear_color = clear_color
        self._light_dir = light_dir
        self._camera = preview3d_gl_core.CameraState()
        self._heat_flux_mode = False
        self._flat_shade = False
        self._xray = False
        self._xray_opacity = preview3d_gl_core.XRAY_DEFAULT_OPACITY
        self._duct_bend_radius_mult = None  # None = use DUCT_BEND_RADIUS_TUBE_DIA_MULT
        self._last_result = None
        self._last_bounds = None  # (center_xyz, half_extent), set by update_result/update_meshes
        self._pending_mesh_data = []
        self._gl_meshes = []  # [{"vbo", "ibo", "n_indices", "layer", "centroid", ...}] -
                              # live GL objects, one per render_layers.RenderBatch
        self._dirty = False
        self._program = None
        self._locs = {}  # attrib/uniform locations of self._program, cached in initgl
        self._gizmo_program = None
        self._gizmo_vbo = None
        self._drag_last = None

        self.bind("<Button-1>", self._on_mouse_down)
        self.bind("<B1-Motion>", self._on_mouse_drag)
        self.bind("<MouseWheel>", self._on_scroll_windows_mac)
        self.bind("<Button-4>", self._on_scroll_linux_up)
        self.bind("<Button-5>", self._on_scroll_linux_down)

        # Keyboard: arrow-key pan, +/- zoom, Home=reset view, End=recenter on
        # model. Tk only delivers key events to the focused widget, so
        # _on_mouse_down (bound above) also grabs focus - mouse interaction
        # already implies the user is engaging with this widget.
        self.bind("<Left>", lambda e: self._on_pan_key(-1.0, 0.0))
        self.bind("<Right>", lambda e: self._on_pan_key(1.0, 0.0))
        self.bind("<Up>", lambda e: self._on_pan_key(0.0, 1.0))
        self.bind("<Down>", lambda e: self._on_pan_key(0.0, -1.0))
        self.bind("<plus>", lambda e: self._on_zoom_key(-1.0))
        self.bind("<equal>", lambda e: self._on_zoom_key(-1.0))
        self.bind("<KP_Add>", lambda e: self._on_zoom_key(-1.0))
        self.bind("<minus>", lambda e: self._on_zoom_key(1.0))
        self.bind("<KP_Subtract>", lambda e: self._on_zoom_key(1.0))
        self.bind("<Home>", lambda e: self._on_reset_key())
        self.bind("<End>", lambda e: self._on_recenter_key())

    # --- public API, called from gui/app.py ---

    def update_result(self, result):
        """Rebuild meshes for a new EngineDesign.compute() result and redraw."""
        self._last_result = result
        self._pending_mesh_data = mesh_builder.build_mesh_data(
            result, self._heat_flux_mode,
            duct_bend_radius_mult=self._duct_bend_radius_mult)
        center, half = preview3d_gl_core.compute_bounds(result)
        self._last_bounds = (center, half)
        self._camera.set_target(center, fit_distance=half * 2.6)
        self._dirty = True
        self._request_redraw()

    def update_meshes(self, pieces, center, half):
        """
        Upload an already-built list of MeshBuffers directly, bypassing
        update_result/mesh_builder.build_mesh_data entirely - for callers
        with no EngineDesign.compute() result to build from (gui/shape_lab.py's
        synthetic ring+duct scenes). `center`/`half` size the camera framing
        the same way preview3d_gl_core.compute_bounds would for a real result.
        """
        self._last_result = None
        self._last_bounds = (center, half)
        self._pending_mesh_data = list(pieces)
        self._camera.set_target(center, fit_distance=half * 2.6)
        self._dirty = True
        self._request_redraw()

    def set_flat_shade(self, enabled):
        """Pure render-state toggle (Shape Lab's "Engineering shading" checkbox):
        no mesh rebuild needed, just a shader uniform - see u_flat_shade in
        _FRAGMENT_SHADER, which outputs each vertex's own baked color
        unlit instead of the usual ambient+diffuse+specular blend, so
        per-part colors stay but the shading gradient/gloss goes away."""
        self._flat_shade = bool(enabled)
        self._request_redraw()

    def set_xray(self, enabled, opacity=None):
        """Pure render-state toggle: structural pieces (render_layers.XRAY_ROLES)
        move to the translucent layer with a rim-alpha fade (faces go clear,
        silhouettes stay). Re-batches the already-built pieces - no mesh
        rebuild. `opacity` = face-on alpha (None keeps the current value)."""
        if opacity is not None:
            self._xray_opacity = float(min(max(opacity, 0.0), 1.0))
        enabled = bool(enabled)
        if enabled != self._xray:
            self._xray = enabled
            self._dirty = True  # layer assignment changed -> re-batch/upload
        self._request_redraw()

    def set_heat_flux_mode(self, enabled):
        """Pure render-state toggle - rebuilds vertex colors only, no physics."""
        self._heat_flux_mode = bool(enabled)
        if self._last_result is not None:
            self._pending_mesh_data = mesh_builder.build_mesh_data(
                self._last_result, self._heat_flux_mode,
                duct_bend_radius_mult=self._duct_bend_radius_mult)
            self._dirty = True
        self._request_redraw()

    def set_duct_bend_radius_mult(self, value):
        """
        Debug-only override for the fuel main-inlet duct's bend radius
        (normally DUCT_BEND_RADIUS_TUBE_DIA_MULT, a multiple of the duct's
        own tube diameter) - render-state only, no physics recompute, same
        cache-and-rebuild pattern as set_heat_flux_mode. Lets the user drag
        a slider in gui/app.py's 3D-preview tab to find a value to describe
        back rather than guessing blind across a round trip.
        """
        self._duct_bend_radius_mult = value
        if self._last_result is not None:
            self._pending_mesh_data = mesh_builder.build_mesh_data(
                self._last_result, self._heat_flux_mode,
                duct_bend_radius_mult=self._duct_bend_radius_mult)
            self._dirty = True
        self._request_redraw()

    # --- pyopengltk.OpenGLFrame lifecycle hooks ---

    def initgl(self):
        # pyopengltk calls this from its <Map> handler, which (re)creates the
        # GL context - so it runs again every time the widget is unmapped and
        # re-mapped, i.e. on every round trip through the Shape Lab
        # (app._enter_shape_lab pack_forgets the preview's parent, _exit_shape_lab
        # packs it back). Buffer/program names from the previous context are
        # meaningless in the new one: forget them (don't glDeleteBuffers them -
        # wrong context) and mark everything for re-upload from
        # _pending_mesh_data, which is retained after upload for exactly this.
        # Without this a Bake in the Lab recomputed correctly but the main
        # preview came back drawing stale/invalid buffers.
        self._gl_meshes = []
        self._gizmo_vbo = None
        self._dirty = True
        try:
            self._program = shaders.compileProgram(
                shaders.compileShader(_VERTEX_SHADER, GL.GL_VERTEX_SHADER),
                shaders.compileShader(_FRAGMENT_SHADER, GL.GL_FRAGMENT_SHADER))
        except Exception as exc:  # shader compile failure - degrade, don't crash Tk's loop
            print(f"preview3d_gl: shader compile failed, GL preview disabled: {exc}")
            self._program = None
            return
        prog = self._program
        self._locs = {name: GL.glGetAttribLocation(prog, name)
                      for name in ("in_position", "in_normal", "in_color")}
        self._locs.update({name: GL.glGetUniformLocation(prog, name) for name in (
            "u_view", "u_proj", "u_light_dir", "u_ambient", "u_eye_pos", "u_flat_shade",
            "u_specular_strength", "u_shininess", "u_alpha", "u_rim_power", "u_facing_pass")})
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glClearColor(*self._clear_color, 1.0)

        try:
            self._gizmo_program = shaders.compileProgram(
                shaders.compileShader(_GIZMO_VERTEX_SHADER, GL.GL_VERTEX_SHADER),
                shaders.compileShader(_GIZMO_FRAGMENT_SHADER, GL.GL_FRAGMENT_SHADER))
            self._upload_gizmo()
        except Exception as exc:  # same degrade-don't-crash pattern as the main shader
            print(f"preview3d_gl: gizmo shader compile failed, corner axes disabled: {exc}")
            self._gizmo_program = None

    def _upload_gizmo(self):
        """
        Uploads the fixed unit-length X/Y/Z line geometry once - this is
        static orientation geometry, never rebuilt per-result, so it doesn't
        belong in the _upload_meshes/_pending_mesh_data/_dirty per-result
        pipeline.
        """
        positions, colors = preview3d_gl_core.gizmo_axis_lines()
        interleaved = np.ascontiguousarray(
            np.concatenate([positions, colors], axis=1), dtype=np.float32)
        self._gizmo_vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._gizmo_vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, interleaved.nbytes, interleaved, GL.GL_STATIC_DRAW)

    def redraw(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        if self._program is None:
            return
        if self._dirty:
            self._upload_meshes()
            self._dirty = False

        width = max(int(self.winfo_width()), 1)
        height = max(int(self.winfo_height()), 1)
        GL.glViewport(0, 0, width, height)

        GL.glUseProgram(self._program)
        loc = self._locs
        view = self._camera.view_matrix().astype(np.float32)
        proj = self._camera.projection_matrix(aspect=width / height).astype(np.float32)
        GL.glUniformMatrix4fv(loc["u_view"], 1, GL.GL_TRUE, view)
        GL.glUniformMatrix4fv(loc["u_proj"], 1, GL.GL_TRUE, proj)
        GL.glUniform3f(loc["u_light_dir"], *self._light_dir)
        GL.glUniform3f(loc["u_ambient"], 0.25, 0.25, 0.28)
        eye = self._camera.eye_position()
        GL.glUniform3f(loc["u_eye_pos"], float(eye[0]), float(eye[1]), float(eye[2]))
        GL.glUniform1f(loc["u_flat_shade"], 1.0 if self._flat_shade else 0.0)
        GL.glUniform1f(loc["u_rim_power"], preview3d_gl_core.XRAY_RIM_POWER)

        # Pass 1 - opaque layer: depth write on, no blending (the pre-X-ray path).
        GL.glUniform1f(loc["u_alpha"], 1.0)
        GL.glUniform1i(loc["u_facing_pass"], 0)
        for mesh in self._gl_meshes:
            if mesh["layer"] == preview3d_gl_core.LAYER_OPAQUE:
                self._draw_batch(mesh)

        # Pass 2 - translucent (X-ray) layer: depth-tested against the opaque
        # pass but not writing depth, alpha-blended back to front; each batch
        # twice (far-facing fragments, then near-facing) so a revolved shell's
        # back wall is blended under its front wall.
        translucent = [m for m in self._gl_meshes
                       if m["layer"] == preview3d_gl_core.LAYER_TRANSLUCENT]
        if translucent:
            order = preview3d_gl_core.back_to_front_order(
                [m["centroid"] for m in translucent], eye)
            GL.glDepthMask(GL.GL_FALSE)
            GL.glEnable(GL.GL_BLEND)
            GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
            GL.glUniform1f(loc["u_alpha"], self._xray_opacity)
            for facing_pass in (1, 2):
                GL.glUniform1i(loc["u_facing_pass"], facing_pass)
                for k in order:
                    self._draw_batch(translucent[k])
            GL.glDisable(GL.GL_BLEND)
            GL.glDepthMask(GL.GL_TRUE)

        self._draw_gizmo(width, height)

    def _draw_batch(self, mesh):
        """Bind one uploaded batch's buffers and draw it with the current uniforms."""
        loc = self._locs
        stride = 9 * 4  # 9 floats/vertex (pos, normal, color), 4 bytes each
        GL.glUniform1f(loc["u_specular_strength"], mesh["specular_strength"])
        GL.glUniform1f(loc["u_shininess"], mesh["shininess"])
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, mesh["vbo"])
        for name, offset in (("in_position", 0), ("in_normal", 12), ("in_color", 24)):
            GL.glEnableVertexAttribArray(loc[name])
            GL.glVertexAttribPointer(loc[name], 3, GL.GL_FLOAT, GL.GL_FALSE, stride,
                                     GL.GLvoidp(offset))
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, mesh["ibo"])
        GL.glDrawElements(GL.GL_TRIANGLES, mesh["n_indices"], GL.GL_UNSIGNED_INT, None)

    def _draw_gizmo(self, width, height):
        """
        Corner XYZ orientation indicator: drawn last (on top of the main
        scene, never re-clearing the color buffer) into a small fixed-pixel
        viewport rectangle, using only the rotation part of the main camera
        (preview3d_gl_core.gizmo_rotation_matrix) and a fixed small
        orthographic projection - so it spins with orbit but ignores the main
        scene's zoom/pan/target entirely.
        """
        if self._gizmo_program is None or self._gizmo_vbo is None:
            return

        gizmo_size = max(1, min(_GIZMO_MAX_PX, width // 6, height // 6))
        GL.glViewport(_GIZMO_MARGIN_PX, _GIZMO_MARGIN_PX, gizmo_size, gizmo_size)
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT)  # depth only - never touch the color buffer here

        GL.glUseProgram(self._gizmo_program)
        gizmo_view = preview3d_gl_core.gizmo_rotation_matrix(self._camera).astype(np.float32)
        gizmo_proj = preview3d_gl_core.gizmo_projection_matrix().astype(np.float32)
        GL.glUniformMatrix4fv(GL.glGetUniformLocation(self._gizmo_program, "u_view"),
                               1, GL.GL_TRUE, gizmo_view)
        GL.glUniformMatrix4fv(GL.glGetUniformLocation(self._gizmo_program, "u_proj"),
                               1, GL.GL_TRUE, gizmo_proj)

        pos_loc = GL.glGetAttribLocation(self._gizmo_program, "in_position")
        color_loc = GL.glGetAttribLocation(self._gizmo_program, "in_color")
        stride = 6 * 4  # 6 floats/vertex (3 pos + 3 color), 4 bytes each
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._gizmo_vbo)
        GL.glEnableVertexAttribArray(pos_loc)
        GL.glVertexAttribPointer(pos_loc, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, GL.GLvoidp(0))
        GL.glEnableVertexAttribArray(color_loc)
        GL.glVertexAttribPointer(color_loc, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, GL.GLvoidp(12))
        GL.glDrawArrays(GL.GL_LINES, 0, 6)

        GL.glViewport(0, 0, width, height)  # restore full-window viewport for the next frame

    def _upload_meshes(self):
        for mesh in self._gl_meshes:
            GL.glDeleteBuffers(1, [mesh["vbo"]])
            GL.glDeleteBuffers(1, [mesh["ibo"]])
        self._gl_meshes = []
        # Batch per render layer/role/material (render_layers.build_batches):
        # a tube bundle's hundreds of pieces become one draw call.
        for batch in preview3d_gl_core.build_batches(self._pending_mesh_data, self._xray):
            buf = batch.buffers
            interleaved = np.concatenate([buf.vertices, buf.normals, buf.colors], axis=1)
            interleaved = np.ascontiguousarray(interleaved, dtype=np.float32)
            indices = np.ascontiguousarray(buf.indices.ravel(), dtype=np.uint32)

            vbo = GL.glGenBuffers(1)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, interleaved.nbytes, interleaved, GL.GL_STATIC_DRAW)

            ibo = GL.glGenBuffers(1)
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, ibo)
            GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL.GL_STATIC_DRAW)

            self._gl_meshes.append({"vbo": vbo, "ibo": ibo, "n_indices": indices.size,
                                     "specular_strength": float(buf.specular_strength),
                                     "shininess": float(buf.shininess),
                                     "layer": batch.layer, "centroid": batch.centroid})

    def _request_redraw(self):
        # See module docstring's note: unconfirmed against the actually-
        # installed pyopengltk version.
        self.animate = 0
        # While unmapped (the main window is showing the Shape Lab in our
        # place) there is nothing to paint and the context may be about to be
        # replaced on re-map (see initgl) - leave _dirty set so the re-map's
        # own Map/Expose does the upload+draw into the live context instead.
        if not self.winfo_ismapped():
            return
        self.event_generate("<Expose>")

    # --- orbit-camera mouse/scroll bindings ---

    _DRAG_SENSITIVITY_DEG_PER_PX = 0.4
    _ZOOM_STEP = 0.1

    def _on_mouse_down(self, event):
        self.focus_set()  # so subsequent arrow/+-/Home/End key events reach us
        self._drag_last = (event.x, event.y)

    def _on_mouse_drag(self, event):
        if self._drag_last is None:
            self._drag_last = (event.x, event.y)
            return
        last_x, last_y = self._drag_last
        dx, dy = event.x - last_x, event.y - last_y
        self._drag_last = (event.x, event.y)
        self._camera.orbit(dyaw_deg=-dx * self._DRAG_SENSITIVITY_DEG_PER_PX,
                            dpitch_deg=dy * self._DRAG_SENSITIVITY_DEG_PER_PX)
        self._request_redraw()

    def _on_scroll_windows_mac(self, event):
        self._camera.zoom(delta=-self._ZOOM_STEP if event.delta > 0 else self._ZOOM_STEP)
        self._request_redraw()

    def _on_scroll_linux_up(self, _event):
        self._camera.zoom(delta=-self._ZOOM_STEP)
        self._request_redraw()

    def _on_scroll_linux_down(self, _event):
        self._camera.zoom(delta=self._ZOOM_STEP)
        self._request_redraw()

    # --- keyboard bindings: arrow-key pan, +/- zoom, Home=reset, End=recenter ---

    def _on_pan_key(self, dx_screen, dy_screen):
        self._camera.pan(dx_screen, dy_screen)
        self._request_redraw()

    def _on_zoom_key(self, delta):
        self._camera.zoom(delta=delta)
        self._request_redraw()

    def _on_reset_key(self):
        if self._last_bounds is not None:
            center, half = self._last_bounds
            self._camera.reset(center, half)
        else:
            self._camera.reset()
        self._request_redraw()

    def _on_recenter_key(self):
        if self._last_bounds is not None:
            center, half = self._last_bounds
            self._camera.recenter(center, half)
            self._request_redraw()


if __name__ == "__main__":
    print("preview3d_gl.py: syntax-check only - needs OpenGL/pyopengltk + a "
          "live display, neither available in this sandbox. Run "
          "`python3 -c \"import ast; ast.parse(open('engine_designer/gui/"
          "preview3d_gl.py').read())\"` instead, or run this module's caller "
          "(gui/app.py) on a machine with a display.")
