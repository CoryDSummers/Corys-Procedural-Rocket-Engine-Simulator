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

# Legacy Blinn-Phong fragment shader - kept ONLY as the compile fallback for
# the PBR shader (preview3d_gl_core.PBR_FRAGMENT_SHADER, same vertex shader)
# on a driver that rejects it; see initgl.
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

#: Multisample count for the offscreen anti-aliasing framebuffer (see
#: _ensure_msaa). 0 disables it outright.
_MSAA_SAMPLES = 4


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
        self._flow = False
        self._flow_scale = None     # flow_meshes.FlowColorScale; None = baked absolute colors
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
        self._pbr = False           # True = PBR shader compiled; False = legacy fallback
        self._bg_program = None
        self._bg_vbo = None
        self._max_attribs = None    # GL_MAX_VERTEX_ATTRIBS, queried once per context
        self._msaa = None           # {"fbo", "rbos", "size"} offscreen multisample target
        self._msaa_failed = False
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
        preview3d_gl_core.PBR_FRAGMENT_SHADER (and the legacy fallback), which outputs each vertex's own baked color
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

    def set_flow(self, enabled):
        """Pure render-state toggle for the propellant-flow visualization
        (physics/flow_network.py streams, built into every mesh rebuild as
        role "flow" pieces): shows/hides the flow layer by re-batching - no
        mesh rebuild."""
        enabled = bool(enabled)
        if enabled != self._flow:
            self._flow = enabled
            self._dirty = True
        self._request_redraw()

    def set_flow_scale(self, scale):
        """Render-state only: the FlowColorScale the Flow view's temperature
        colors use (render_layers recolors from each vertex's temperature at
        batch time - a re-batch, no mesh rebuild)."""
        if scale != self._flow_scale:
            self._flow_scale = scale
            self._dirty = True
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
        self._bg_vbo = None
        self._max_attribs = None    # new context - re-query
        self._msaa = None           # same forget-don't-delete rule as the buffers above
        self._msaa_failed = False
        self._dirty = True
        # PBR shader first; on a driver that rejects it, the legacy Blinn-Phong
        # one (same vertex shader/attributes) - and only if BOTH fail is the
        # preview disabled.
        self._program = None
        for pbr, frag in ((True, preview3d_gl_core.PBR_FRAGMENT_SHADER), (False, _FRAGMENT_SHADER)):
            try:
                self._program = shaders.compileProgram(
                    shaders.compileShader(_VERTEX_SHADER, GL.GL_VERTEX_SHADER),
                    shaders.compileShader(frag, GL.GL_FRAGMENT_SHADER))
                self._pbr = pbr
                break
            except Exception as exc:  # shader compile failure - degrade, don't crash Tk's loop
                print(f"preview3d_gl: {'PBR' if pbr else 'legacy'} shader compile failed: {exc}")
        if self._program is None:
            print("preview3d_gl: no shader compiled, GL preview disabled")
            return
        if not self._pbr:
            print("preview3d_gl: using legacy Blinn-Phong shading fallback")
        prog = self._program
        self._locs = {name: GL.glGetAttribLocation(prog, name)
                      for name in ("in_position", "in_normal", "in_color")}
        self._locs.update({name: GL.glGetUniformLocation(prog, name) for name in (
            "u_view", "u_proj", "u_light_dir", "u_ambient", "u_eye_pos", "u_flat_shade",
            "u_specular_strength", "u_shininess", "u_metallic", "u_roughness", "u_data_colors",
            "u_alpha", "u_rim_power", "u_facing_pass")})
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glClearColor(*self._clear_color, 1.0)

        try:
            self._bg_program = shaders.compileProgram(
                shaders.compileShader(preview3d_gl_core.BACKGROUND_VERTEX_SHADER,
                                      GL.GL_VERTEX_SHADER),
                shaders.compileShader(preview3d_gl_core.BACKGROUND_FRAGMENT_SHADER,
                                      GL.GL_FRAGMENT_SHADER))
            tri = np.ascontiguousarray(preview3d_gl_core.background_triangle(), dtype=np.float32)
            self._bg_vbo = GL.glGenBuffers(1)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._bg_vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, tri.nbytes, tri, GL.GL_STATIC_DRAW)
        except Exception as exc:  # cosmetic - plain clear color instead
            print(f"preview3d_gl: background gradient disabled: {exc}")
            self._bg_program = None

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

    def _ensure_msaa(self, width, height):
        """
        Offscreen multisample color+depth framebuffer the scene renders into,
        resolved to the window's own framebuffer by _resolve_msaa - 4x MSAA
        without having to request a multisample pixel format from pyopengltk
        (not something its OpenGLFrame exposes). (Re)built on resize; any
        failure (pre-GL-3.0 context, driver refusal) disables it for the life
        of this context and the scene just draws directly, un-antialiased.
        Returns True if the MSAA target is bound.
        """
        if _MSAA_SAMPLES <= 0 or self._msaa_failed:
            return False
        try:
            if self._msaa is None or self._msaa["size"] != (width, height):
                if self._msaa is not None:
                    GL.glDeleteFramebuffers(1, [self._msaa["fbo"]])
                    GL.glDeleteRenderbuffers(2, self._msaa["rbos"])
                fbo = GL.glGenFramebuffers(1)
                rbos = GL.glGenRenderbuffers(2)
                GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, fbo)
                for rbo, fmt, attach in ((rbos[0], GL.GL_RGBA8, GL.GL_COLOR_ATTACHMENT0),
                                         (rbos[1], GL.GL_DEPTH_COMPONENT24,
                                          GL.GL_DEPTH_ATTACHMENT)):
                    GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, rbo)
                    GL.glRenderbufferStorageMultisample(GL.GL_RENDERBUFFER, _MSAA_SAMPLES,
                                                        fmt, width, height)
                    GL.glFramebufferRenderbuffer(GL.GL_FRAMEBUFFER, attach,
                                                 GL.GL_RENDERBUFFER, rbo)
                status = GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER)
                self._msaa = {"fbo": fbo, "rbos": list(rbos), "size": (width, height)}
                if status != GL.GL_FRAMEBUFFER_COMPLETE:
                    raise RuntimeError(f"framebuffer incomplete (0x{int(status):x})")
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self._msaa["fbo"])
            return True
        except Exception as exc:
            print(f"preview3d_gl: MSAA disabled, drawing un-antialiased: {exc}")
            self._msaa_failed = True
            self._msaa = None
            try:
                GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
            except Exception:
                pass
            return False

    def _resolve_msaa(self, width, height):
        GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, self._msaa["fbo"])
        GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, 0)
        GL.glBlitFramebuffer(0, 0, width, height, 0, 0, width, height,
                             GL.GL_COLOR_BUFFER_BIT, GL.GL_NEAREST)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

    def _disable_stray_attribs(self, keep=-1):
        """
        Disable every vertex-attribute array except `keep`. GL fetches from ALL
        enabled arrays on a draw, whatever the bound shader reads - and an
        array whose VBO was deleted (every _upload_meshes re-upload: a new
        design, the X-ray/Flow toggles) falls back to buffer 0, so its byte
        offset becomes a raw client pointer. That was the Windows crash
        "access violation reading 0x0000000000000018" in _draw_background's
        glDrawArrays (0x18 = in_color's offset 24). Mesa tolerates it; NVIDIA/
        AMD drivers don't.
        """
        if self._max_attribs is None:
            self._max_attribs = int(np.ravel(GL.glGetIntegerv(GL.GL_MAX_VERTEX_ATTRIBS))[0])
        for i in range(self._max_attribs):
            if i != keep:
                GL.glDisableVertexAttribArray(i)

    def _draw_background(self):
        """Vertical gradient behind the scene (depth test off, so it never
        occludes anything); falls back to the plain clear color."""
        if self._bg_program is None or self._bg_vbo is None or self._flat_shade:
            return
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glUseProgram(self._bg_program)
        GL.glUniform3f(GL.glGetUniformLocation(self._bg_program, "u_top"),
                       *preview3d_gl_core.BACKGROUND_TOP)
        GL.glUniform3f(GL.glGetUniformLocation(self._bg_program, "u_bottom"),
                       *preview3d_gl_core.BACKGROUND_BOTTOM)
        loc = GL.glGetAttribLocation(self._bg_program, "in_ndc")
        self._disable_stray_attribs(keep=loc)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._bg_vbo)
        GL.glEnableVertexAttribArray(loc)
        GL.glVertexAttribPointer(loc, 2, GL.GL_FLOAT, GL.GL_FALSE, 8, GL.GLvoidp(0))
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)
        GL.glDisableVertexAttribArray(loc)
        GL.glEnable(GL.GL_DEPTH_TEST)

    def _set_lighting_uniforms(self):
        prog = self._program
        if not self._pbr:
            GL.glUniform3f(GL.glGetUniformLocation(prog, "u_light_dir"), *self._light_dir)
            GL.glUniform3f(GL.glGetUniformLocation(prog, "u_ambient"), 0.25, 0.25, 0.28)
            return
        from .preview3d_gl_core import shading
        # World-fixed rig (key follows this widget's configurable light_dir;
        # fill/rim/back stay as the rig defines them) + the camera-relative
        # fill, re-aimed every frame so the side being viewed is never unlit.
        lights = shading.full_light_list(self._camera.eye_position(), self._camera.target)
        dirs = [self._light_dir] + [d for d, _ in lights[1:]]
        rgbs = [c for _, c in lights]
        GL.glUniform3fv(GL.glGetUniformLocation(prog, "u_light_dir"), shading.N_LIGHTS,
                        np.asarray(dirs, dtype=np.float32).ravel())
        GL.glUniform3fv(GL.glGetUniformLocation(prog, "u_light_rgb"), shading.N_LIGHTS,
                        np.asarray(rgbs, dtype=np.float32).ravel())
        for name, val in (("u_env_up", shading.ENV_UP), ("u_env_sky", shading.ENV_SKY),
                          ("u_env_ground", shading.ENV_GROUND),
                          ("u_env_horizon", shading.ENV_HORIZON)):
            GL.glUniform3f(GL.glGetUniformLocation(prog, name), *val)
        for name, val in (("u_env_horizon_width", shading.ENV_HORIZON_WIDTH),
                          ("u_env_horizon_rough_widen", shading.ENV_HORIZON_ROUGH_WIDEN),
                          ("u_exposure", shading.EXPOSURE)):
            GL.glUniform1f(GL.glGetUniformLocation(prog, name), float(val))

    def redraw(self):
        if self._program is None:
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
            return
        if self._dirty:
            self._upload_meshes()
            self._dirty = False

        width = max(int(self.winfo_width()), 1)
        height = max(int(self.winfo_height()), 1)
        msaa = self._ensure_msaa(width, height)
        GL.glViewport(0, 0, width, height)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        self._draw_background()

        GL.glUseProgram(self._program)
        loc = self._locs
        view = self._camera.view_matrix().astype(np.float32)
        proj = self._camera.projection_matrix(aspect=width / height).astype(np.float32)
        GL.glUniformMatrix4fv(loc["u_view"], 1, GL.GL_TRUE, view)
        GL.glUniformMatrix4fv(loc["u_proj"], 1, GL.GL_TRUE, proj)
        self._set_lighting_uniforms()
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

        # Pass 1b - flow layer: solid, unlit (reads as emissive), depth-tested
        # and depth-writing like the opaque pass, so the translucent pass
        # below blends over it.
        flow = [m for m in self._gl_meshes if m["layer"] == preview3d_gl_core.LAYER_FLOW]
        if flow:
            GL.glUniform1f(loc["u_flat_shade"], 1.0)
            for mesh in flow:
                self._draw_batch(mesh)
            GL.glUniform1f(loc["u_flat_shade"], 1.0 if self._flat_shade else 0.0)

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
            for facing_pass in (1, 2):
                GL.glUniform1i(loc["u_facing_pass"], facing_pass)
                for k in order:
                    # per-batch opacity: temperature-tinted coolant hardware
                    # (Flow view) has its own; everything else the X-ray slider's
                    alpha = translucent[k]["alpha"]
                    GL.glUniform1f(loc["u_alpha"], self._xray_opacity if alpha is None else alpha)
                    self._draw_batch(translucent[k])
            GL.glDisable(GL.GL_BLEND)
            GL.glDepthMask(GL.GL_TRUE)

        self._draw_gizmo(width, height)
        if msaa:
            self._resolve_msaa(width, height)

    def _draw_batch(self, mesh):
        """Bind one uploaded batch's buffers and draw it with the current uniforms."""
        loc = self._locs
        stride = 9 * 4  # 9 floats/vertex (pos, normal, color), 4 bytes each
        # Per-batch material uniforms: the PBR shader's metallic/roughness/
        # data-readout flag, or the legacy fallback's Blinn-Phong pair.
        if self._pbr:
            GL.glUniform1f(loc["u_metallic"], mesh["metallic"])
            GL.glUniform1f(loc["u_roughness"], mesh["roughness"])
            GL.glUniform1f(loc["u_data_colors"], mesh["data_colors"])
        else:
            GL.glUniform1f(loc["u_specular_strength"], mesh["specular_strength"])
            GL.glUniform1f(loc["u_shininess"], mesh["shininess"])
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, mesh["vbo"])
        for name, offset in (("in_position", 0), ("in_normal", 12), ("in_color", 24)):
            GL.glEnableVertexAttribArray(loc[name])
            GL.glVertexAttribPointer(loc[name], 3, GL.GL_FLOAT, GL.GL_FALSE, stride,
                                     GL.GLvoidp(offset))
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, mesh["ibo"])
        GL.glDrawElements(GL.GL_TRIANGLES, mesh["n_indices"], GL.GL_UNSIGNED_INT, None)
        # Never leave an array enabled past its draw: the next re-upload
        # deletes this VBO, and a still-enabled array would then dangle (see
        # _disable_stray_attribs).
        for name in ("in_position", "in_normal", "in_color"):
            if loc[name] >= 0:
                GL.glDisableVertexAttribArray(loc[name])

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
        for attr_loc in (pos_loc, color_loc):   # same hygiene as _draw_batch
            if attr_loc >= 0:
                GL.glDisableVertexAttribArray(attr_loc)

        GL.glViewport(0, 0, width, height)  # restore full-window viewport for the next frame

    def _upload_meshes(self):
        for mesh in self._gl_meshes:
            GL.glDeleteBuffers(1, [mesh["vbo"]])
            GL.glDeleteBuffers(1, [mesh["ibo"]])
        self._gl_meshes = []
        # Batch per render layer/role/material (render_layers.build_batches):
        # a tube bundle's hundreds of pieces become one draw call.
        for batch in preview3d_gl_core.build_batches(self._pending_mesh_data, self._xray,
                                                     flow_enabled=self._flow,
                                                     color_scale=self._flow_scale):
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

            metallic, roughness = preview3d_gl_core.resolve_pbr(buf)
            self._gl_meshes.append({"vbo": vbo, "ibo": ibo, "n_indices": indices.size,
                                     "specular_strength": float(buf.specular_strength),
                                     "shininess": float(buf.shininess),
                                     "layer": batch.layer, "centroid": batch.centroid,
                                     "alpha": batch.alpha,
                                     "metallic": metallic, "roughness": roughness,
                                     "data_colors": 1.0 if getattr(buf, "data_colors", False)
                                     else 0.0})

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
