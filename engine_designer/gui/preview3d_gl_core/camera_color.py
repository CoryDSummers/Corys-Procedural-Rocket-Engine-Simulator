"""
Colormap and camera-math helpers for the OpenGL 3D preview: per-station
heat-flux-to-RGB mapping, whole-preview bounding-sphere computation, and the
orbit camera (yaw/pitch/distance view + projection matrices). Split out of
the former single-file gui/preview3d_gl_core.py by geometry-operation kind -
see this package's __init__.py for the overview. No OpenGL/Tk import, pure
numpy (+ matplotlib for the colormap only).
"""
from dataclasses import dataclass, field

import matplotlib
import matplotlib.colors as mcolors
import numpy as np

def heat_flux_colors(q_w_m2, cmap_name="turbo"):
    """
    Per-station RGB from a wall-heat-flux profile (W/m^2), same convention as
    gui/schematic.py's 2D cooling overlay: convert to MW/m^2, per-frame
    min/max autoscale (not a fixed global scale), sample the colormap. Uses
    matplotlib.colormaps[name] rather than the deprecated
    matplotlib.cm.get_cmap (confirmed emitting MatplotlibDeprecationWarning on
    matplotlib 3.10, slated for removal in 3.11). Returns (n_stations, 3)
    float32 in 0..1.
    """
    q = np.asarray(q_w_m2, dtype=float) / 1.0e6
    if q.size == 0:
        return np.zeros((0, 3), dtype=np.float32)
    vmax = float(q.max()) or 1.0
    norm = mcolors.Normalize(vmin=float(q.min()), vmax=vmax)
    cmap = matplotlib.colormaps[cmap_name]
    rgba = cmap(norm(q))
    return np.asarray(rgba[:, :3], dtype=np.float32)

def compute_bounds(result):
    """
    Bounding sphere/cube center + half-extent for the whole preview (profile
    body + turbopump assembly if present), for seeding the camera's
    target/auto-fit distance. Same bounding-box logic gui/preview3d.py's tail
    already used to set ax3d.set_xlim/ylim/zlim, repurposed here.
    Returns (center_xyz: np.ndarray shape (3,), half_extent: float).
    """
    xs = np.asarray(result["profile_xs_m"], dtype=float)
    rs = np.asarray(result["profile_rs_m"], dtype=float)
    chamber_head_r = float(rs[0]) if rs.size else 0.0
    dome_depth = 0.42 * chamber_head_r if chamber_head_r > 0 else 0.0

    x_lo = float(xs.min()) if xs.size else 0.0
    if chamber_head_r > 0:
        x_lo = min(x_lo, -dome_depth * 1.15)
    x_hi = float(xs.max()) if xs.size else 0.0
    max_r = float(rs.max()) if rs.size else 0.0

    sizing = result.get("turbopump_sizing")
    if sizing and sizing.get("bodies"):
        y_offset = max_r + 0.5 * sizing["assembly_od_m"] + 0.04 * max_r
        max_r = max(max_r, y_offset + 0.5 * sizing["assembly_od_m"])
        tp_x_extent = x_hi
        for b in sizing["bodies"]:
            tp_x_extent = max(tp_x_extent, 0.03 * x_hi + b["x0_m"] + b["length_m"])
        x_hi = max(x_hi, tp_x_extent)

    x_span = x_hi - x_lo
    half = max(max_r, x_span / 2.0, 1e-6)
    x_mid = (x_hi + x_lo) / 2.0
    return np.array([x_mid, 0.0, 0.0]), half

@dataclass
class CameraState:
    """
    Orbit camera: yaw/pitch/distance about a target point, world up=(0,0,1)
    (an arbitrary but reasonable choice - the engine's Y/Z axes have no
    inherent "up," matching how preview3d.py's equal-box-aspect view already
    treats all three axes symmetrically). No Tk/GL dependency - pure math,
    bound to widget mouse events in gui/preview3d_gl.py.
    """
    target: np.ndarray = field(default_factory=lambda: np.zeros(3))
    distance: float = 2.0
    yaw_deg: float = 35.0
    pitch_deg: float = 20.0
    min_distance: float = 0.05
    max_distance: float = 200.0

    #: Default yaw/pitch a fresh CameraState (and reset()) start at - kept as
    #: class constants so reset() can restore them without a second instance.
    _DEFAULT_YAW_DEG = 35.0
    _DEFAULT_PITCH_DEG = 20.0

    #: Screen-space pan step per arrow-key press, as a fraction of current
    #: distance (so panning speed scales naturally with zoom level).
    _PAN_STEP_FRACTION = 0.08

    def __post_init__(self):
        self.target = np.asarray(self.target, dtype=float)

    def set_target(self, center_xyz, fit_distance):
        self.target = np.asarray(center_xyz, dtype=float)
        self.distance = float(np.clip(fit_distance, self.min_distance, self.max_distance))

    def orbit(self, dyaw_deg, dpitch_deg):
        """
        Full 360-degree orbit in any direction: both yaw and pitch wrap
        modulo 360 into (-180, 180] rather than clamping. eye_position()'s
        spherical parameterization is continuous/periodic in pitch, so
        letting pitch swing past +/-90 just carries the camera up and over
        the pole (no gimbal-lock special-casing needed beyond the existing
        near-pole up-vector fallback already in view_matrix()).
        """
        self.yaw_deg = (self.yaw_deg + dyaw_deg) % 360.0
        self.pitch_deg = ((self.pitch_deg + dpitch_deg + 180.0) % 360.0) - 180.0

    def zoom(self, delta):
        """delta > 0 zooms out, delta < 0 zooms in (fractional step on distance)."""
        self.distance = float(np.clip(self.distance * (1.0 + delta),
                                       self.min_distance, self.max_distance))

    def pan(self, dx_screen, dy_screen):
        """
        Shift target along the camera's current screen-space right/up axes
        (arrow-key panning). dx_screen/dy_screen are unitless step counts
        (e.g. +1/-1 per keypress); actual world-space shift scales with
        the current distance so panning feels consistent at any zoom level.
        """
        right, up = self._right_up_vectors()
        step = self.distance * self._PAN_STEP_FRACTION
        self.target = self.target + step * (dx_screen * right + dy_screen * up)

    def reset(self, center_xyz=None, half_extent=None):
        """
        Restore the default view: default yaw/pitch, and (if a model's
        bounds are given) re-fit target/distance the same way a fresh load
        via set_target() would.
        """
        self.yaw_deg = self._DEFAULT_YAW_DEG
        self.pitch_deg = self._DEFAULT_PITCH_DEG
        if center_xyz is not None and half_extent is not None:
            self.set_target(center_xyz, fit_distance=half_extent * 2.6)

    def recenter(self, center_xyz, half_extent):
        """
        Re-center target/distance on the model's current bounds without
        touching yaw/pitch - for recovering after arrow-key panning has
        drifted the target away from the model, while keeping the current
        rotation.
        """
        self.set_target(center_xyz, fit_distance=half_extent * 2.6)

    def eye_position(self):
        yaw = np.radians(self.yaw_deg)
        pitch = np.radians(self.pitch_deg)
        direction = np.array([np.cos(pitch) * np.cos(yaw),
                               np.cos(pitch) * np.sin(yaw),
                               np.sin(pitch)])
        return self.target + self.distance * direction

    def _right_up_vectors(self):
        """
        Camera-space right/up unit vectors, shared by view_matrix() and
        pan() so both use the identical basis. Derived analytically as the
        tangent vectors of eye_position()'s spherical parameterization
        w.r.t. yaw and pitch (partial derivatives of eye position), rather
        than via cross(forward, world_up) - that cross-product approach
        degenerates exactly at pitch = +/-90 deg (forward parallel to world
        up), which orbit()'s full 360-degree range now regularly passes
        through; a fallback swap of the up axis there caused a visible
        rotation "flip" when dragging straight up/down through the pole.
        The tangent-vector basis is smooth and well-defined at every pitch,
        including exactly +/-90, with no branching needed.
        """
        yaw = np.radians(self.yaw_deg)
        pitch = np.radians(self.pitch_deg)
        right = np.array([-np.sin(yaw), np.cos(yaw), 0.0])
        up = np.array([-np.sin(pitch) * np.cos(yaw),
                        -np.sin(pitch) * np.sin(yaw),
                        np.cos(pitch)])
        return right, up

    def view_matrix(self):
        """Standard right-handed look-at matrix (v' = M @ [x,y,z,1])."""
        eye = self.eye_position()
        forward = self.target - eye
        fnorm = np.linalg.norm(forward)
        forward = forward / fnorm if fnorm > 1e-12 else np.array([0.0, 1.0, 0.0])
        right, true_up = self._right_up_vectors()

        m = np.eye(4)
        m[0, :3] = right
        m[1, :3] = true_up
        m[2, :3] = -forward
        m[0, 3] = -np.dot(right, eye)
        m[1, 3] = -np.dot(true_up, eye)
        m[2, 3] = np.dot(forward, eye)
        return m

    def projection_matrix(self, aspect, fov_deg=45.0, near=0.01, far=1000.0):
        """Standard OpenGL perspective matrix (v' = M @ [x,y,z,1])."""
        f = 1.0 / np.tan(np.radians(fov_deg) / 2.0)
        m = np.zeros((4, 4))
        m[0, 0] = f / aspect
        m[1, 1] = f
        m[2, 2] = (far + near) / (near - far)
        m[2, 3] = (2.0 * far * near) / (near - far)
        m[3, 2] = -1.0
        return m


#: Corner orientation-gizmo axis colors (slightly desaturated from pure
#: RGB primaries, matching this codebase's general material-color style):
#: X=red, Y=green, Z=blue.
GIZMO_AXIS_COLORS = (
    (0.85, 0.15, 0.15),
    (0.15, 0.80, 0.20),
    (0.20, 0.40, 0.95),
)


def gizmo_axis_lines():
    """
    Fixed unit-length X/Y/Z line-segment geometry for the corner orientation
    gizmo, as 6 vertices (3 disjoint segments, origin -> +axis) suitable for
    GL_LINES. Returns (positions: (6,3) float32, colors: (6,3) float32).
    """
    positions = np.array([
        [0.0, 0.0, 0.0], [1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0], [0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0], [0.0, 0.0, 1.0],
    ], dtype=np.float32)
    colors = np.repeat(np.asarray(GIZMO_AXIS_COLORS, dtype=np.float32), 2, axis=0)
    return positions, colors


def gizmo_rotation_matrix(camera):
    """
    Rotation-only 4x4 (v' = M @ [x,y,z,1]) for the corner gizmo: the same
    3x3 rotation block as camera.view_matrix(), with translation zeroed out,
    so the gizmo orbits in sync with the main view but ignores target/pan
    and distance/zoom entirely.
    """
    m = np.eye(4)
    m[:3, :3] = camera.view_matrix()[:3, :3]
    return m


def gizmo_projection_matrix(size=1.6, near=-10.0, far=10.0):
    """
    Fixed small orthographic projection (v' = M @ [x,y,z,1]) for the corner
    gizmo, independent of the main scene's perspective projection_matrix()
    (no fov/aspect dependence) so the unit-length gizmo axes never appear
    perspective-distorted at their tiny on-screen size. Symmetric in x/y for
    a square gizmo viewport.
    """
    m = np.zeros((4, 4))
    m[0, 0] = 1.0 / size
    m[1, 1] = 1.0 / size
    m[2, 2] = -2.0 / (far - near)
    m[2, 3] = -(far + near) / (far - near)
    m[3, 3] = 1.0
    return m


def self_test():
    xs_cyl = np.linspace(0.0, 1.0, 5)
    rs_cyl = np.full_like(xs_cyl, 0.5)

    # --- heat_flux_colors: matches matplotlib.colormaps["turbo"] at the
    # normalized 0.0/1.0 endpoints for a known synthetic q array ---
    q = np.array([0.0, 5.0e6, 10.0e6])
    colors = heat_flux_colors(q)
    turbo = matplotlib.colormaps["turbo"]
    assert np.allclose(colors[0], np.asarray(turbo(0.0))[:3], atol=1e-6)
    assert np.allclose(colors[-1], np.asarray(turbo(1.0))[:3], atol=1e-6)
    print("heat_flux_colors self-check: OK")

    # --- CameraState: view-matrix rotation-part orthonormality, known
    # projection-matrix elements, orbit/zoom clamping ---
    cam = CameraState(target=(0.0, 0.0, 0.0), distance=3.0, yaw_deg=10.0, pitch_deg=5.0)
    vm = cam.view_matrix()
    rot = vm[:3, :3]
    assert np.allclose(rot @ rot.T, np.eye(3), atol=1e-9)
    assert np.allclose(np.linalg.det(rot), 1.0, atol=1e-6)

    pm = cam.projection_matrix(aspect=1.5, fov_deg=90.0, near=0.1, far=100.0)
    assert pm.shape == (4, 4)
    assert np.isclose(pm[0, 0], (1.0 / np.tan(np.radians(45.0))) / 1.5)
    assert np.isclose(pm[3, 2], -1.0)

    # --- full 360-degree orbit: pitch is no longer clamped to +/-89, it
    # wraps continuously like yaw, and eye_position stays finite/continuous
    # well past the poles ---
    cam.orbit(dyaw_deg=0.0, dpitch_deg=100.0)
    assert -180.0 < cam.pitch_deg <= 180.0
    assert np.isfinite(cam.eye_position()).all()
    cam.orbit(dyaw_deg=0.0, dpitch_deg=100.0)  # now well past the pole
    assert -180.0 < cam.pitch_deg <= 180.0
    assert np.isfinite(cam.eye_position()).all()
    cam.orbit(dyaw_deg=1000.0, dpitch_deg=-100000.0)
    assert 0.0 <= cam.yaw_deg < 360.0
    assert -180.0 < cam.pitch_deg <= 180.0

    cam.zoom(delta=1.0e9)
    assert cam.distance == cam.max_distance
    cam.zoom(delta=-1.0)
    assert cam.distance == cam.min_distance
    print("CameraState orbit/zoom self-check: OK")

    # --- pan(): shifts target along the camera's own right/up axes, not
    # world axes; net zero pan for a push-then-pull round trip ---
    cam2 = CameraState(target=(1.0, 2.0, 3.0), distance=5.0, yaw_deg=0.0, pitch_deg=0.0)
    right, up = cam2._right_up_vectors()
    before = cam2.target.copy()
    cam2.pan(dx_screen=1.0, dy_screen=0.0)
    expected_step = cam2.distance * CameraState._PAN_STEP_FRACTION
    assert np.allclose(cam2.target, before + expected_step * right, atol=1e-9)
    cam2.pan(dx_screen=-1.0, dy_screen=0.0)
    assert np.allclose(cam2.target, before, atol=1e-9)
    cam2.pan(dx_screen=0.0, dy_screen=1.0)
    assert np.allclose(cam2.target, before + expected_step * up, atol=1e-9)
    print("CameraState pan self-check: OK")

    # --- reset()/recenter(): reset restores default yaw/pitch + refits,
    # recenter refits target/distance but leaves yaw/pitch untouched ---
    cam3 = CameraState(target=(9.0, 9.0, 9.0), distance=50.0, yaw_deg=123.0, pitch_deg=-77.0)
    cam3.recenter(center_xyz=(1.0, 0.0, 0.0), half_extent=2.0)
    assert np.allclose(cam3.target, [1.0, 0.0, 0.0])
    assert np.isclose(cam3.distance, 2.0 * 2.6)
    assert cam3.yaw_deg == 123.0 and cam3.pitch_deg == -77.0

    cam3.reset(center_xyz=(3.0, 0.0, 0.0), half_extent=1.0)
    assert cam3.yaw_deg == CameraState._DEFAULT_YAW_DEG
    assert cam3.pitch_deg == CameraState._DEFAULT_PITCH_DEG
    assert np.allclose(cam3.target, [3.0, 0.0, 0.0])
    assert np.isclose(cam3.distance, 1.0 * 2.6)

    cam4 = CameraState(yaw_deg=5.0, pitch_deg=5.0, target=(1.0, 1.0, 1.0), distance=9.0)
    cam4.reset()  # no bounds given - only yaw/pitch reset, target/distance untouched
    assert cam4.yaw_deg == CameraState._DEFAULT_YAW_DEG
    assert cam4.pitch_deg == CameraState._DEFAULT_PITCH_DEG
    assert np.allclose(cam4.target, [1.0, 1.0, 1.0])
    assert cam4.distance == 9.0
    print("CameraState reset/recenter self-check: OK")

    # --- _right_up_vectors(): orthonormal basis at every pitch (incl. exact
    # poles, the case that used to trip the old cross-product fallback), and
    # continuous across the pole crossing that used to cause a visible flip ---
    for yaw_deg in (0.0, 37.0, 123.0, 270.0):
        for pitch_deg in (-90.0, -45.0, 0.0, 45.0, 90.0):
            cam5 = CameraState(target=(0.0, 0.0, 0.0), distance=1.0,
                                yaw_deg=yaw_deg, pitch_deg=pitch_deg)
            right, up = cam5._right_up_vectors()
            assert np.isclose(np.linalg.norm(right), 1.0, atol=1e-9)
            assert np.isclose(np.linalg.norm(up), 1.0, atol=1e-9)
            assert np.isclose(np.dot(right, up), 0.0, atol=1e-9)
            vm = cam5.view_matrix()
            rot = vm[:3, :3]
            assert np.allclose(rot @ rot.T, np.eye(3), atol=1e-9)
            assert np.isclose(np.linalg.det(rot), 1.0, atol=1e-6)

    # continuity across the pole: right/up must not jump as pitch crosses 90
    cam_below = CameraState(target=(0, 0, 0), distance=1.0, yaw_deg=15.0, pitch_deg=89.999)
    cam_above = CameraState(target=(0, 0, 0), distance=1.0, yaw_deg=15.0, pitch_deg=90.001)
    r_below, u_below = cam_below._right_up_vectors()
    r_above, u_above = cam_above._right_up_vectors()
    assert np.allclose(r_below, r_above, atol=1e-3)
    assert np.allclose(u_below, u_above, atol=1e-3)
    print("CameraState _right_up_vectors pole continuity self-check: OK")

    # --- compute_bounds: sane center/half-extent for a simple profile ---
    fake_result = {"profile_xs_m": xs_cyl, "profile_rs_m": rs_cyl}
    center, half = compute_bounds(fake_result)
    assert half > 0.0
    # chamber_head_r > 0 (rs_cyl[0]=0.5) pulls x_lo out to cover the domed
    # injector cap preview3d.py also reserves room for - so the midpoint sits
    # left of the raw profile's own midpoint, not exactly on it.
    dome_depth = 0.42 * float(rs_cyl[0])
    expected_x_lo = min(float(xs_cyl.min()), -dome_depth * 1.15)
    assert np.isclose(center[0], (float(xs_cyl.max()) + expected_x_lo) / 2.0)
    print("compute_bounds self-check: OK")

    # --- gizmo_axis_lines: fixed unit X/Y/Z segments, paired colors ---
    gizmo_pos, gizmo_col = gizmo_axis_lines()
    assert gizmo_pos.shape == (6, 3)
    assert gizmo_col.shape == (6, 3)
    assert np.allclose(gizmo_pos[1], [1.0, 0.0, 0.0])
    assert np.allclose(gizmo_pos[3], [0.0, 1.0, 0.0])
    assert np.allclose(gizmo_pos[5], [0.0, 0.0, 1.0])
    assert np.allclose(gizmo_pos[0], [0.0, 0.0, 0.0])
    for i in range(3):
        assert np.allclose(gizmo_col[2 * i], gizmo_col[2 * i + 1])
    print("gizmo_axis_lines self-check: OK")

    # --- gizmo_rotation_matrix: matches view_matrix()'s rotation block
    # exactly, zero translation, still orthonormal ---
    cam6 = CameraState(target=(5.0, -3.0, 2.0), distance=7.0, yaw_deg=61.0, pitch_deg=-24.0)
    gm = gizmo_rotation_matrix(cam6)
    assert gm.shape == (4, 4)
    assert np.allclose(gm[:3, :3], cam6.view_matrix()[:3, :3])
    assert np.allclose(gm[:3, 3], 0.0)
    assert np.allclose(gm[3, :3], 0.0)
    assert np.isclose(gm[3, 3], 1.0)
    rot6 = gm[:3, :3]
    assert np.allclose(rot6 @ rot6.T, np.eye(3), atol=1e-9)
    print("gizmo_rotation_matrix self-check: OK")

    # --- gizmo_projection_matrix: valid orthographic form, structurally
    # distinct from the main perspective projection_matrix() ---
    gp = gizmo_projection_matrix()
    assert gp.shape == (4, 4)
    assert np.isclose(gp[3, 3], 1.0)
    assert np.allclose(gp[3, :3], 0.0)
    assert not np.isclose(gp[3, 2], -1.0)  # perspective sets m[3,2] = -1
    print("gizmo_projection_matrix self-check: OK")

    print("ALL CAMERA_COLOR CHECKS OK")


if __name__ == "__main__":
    self_test()
