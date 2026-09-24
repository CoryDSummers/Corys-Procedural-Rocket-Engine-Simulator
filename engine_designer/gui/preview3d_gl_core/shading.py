"""
Physically-based (metallic/roughness) shading for the OpenGL 3D preview: the
GLSL fragment shader gui/preview3d_gl.py compiles, the studio light rig /
procedural environment constants it is fed, and a pure-numpy REFERENCE
implementation of the exact same math (`pbr_shade_reference`) so the look
can be self-tested headlessly - this sandbox has no $DISPLAY and no PyOpenGL,
so the GLSL itself can never be run here (see preview3d_gl.py's docstring).
Keep the two in lockstep: every GLSL helper below has a same-named numpy
twin, and a change to one without the other is a bug.

Model: Cook-Torrance specular (GGX/Trowbridge-Reitz NDF, Smith-Schlick-GGX
geometry, Schlick Fresnel) + Lambert diffuse, the standard metallic/roughness
parameterization (F0 = 0.04 dielectric .. base color for metals, diffuse
killed by metalness). Three fixed world-space studio lights (key/fill/rim)
plus a procedural sky/horizon/ground environment for the ambient + reflection
term - what actually makes a metal read as metal is having something to
reflect, and a bright horizon band gives polished nozzle metal a readable
highlight streak without any texture. Environment specular uses Karis'
analytic env-BRDF approximation (Unreal mobile) and "blurs" the environment
for rough surfaces by widening/softening the horizon band. Lighting is done
in linear space: vertex colors (sRGB, as every material.color_hex already
is) are linearized on input, the result is ACES-filmic tone mapped
(Narkowicz fit) and re-encoded to sRGB - replaces the old min(lit, 1) clamp
that blew highlights out to flat white.

All values here are cosmetic/rendering only - no physics meaning, same tier
as materials.color_hex (ASSUMPTIONS.md tier 3).
"""
import numpy as np

# World up is +Z (CameraState.eye_position's spherical parameterization).
ENV_UP = (0.0, 0.0, 1.0)

#: Studio light rig: (world-space direction TOWARD the light, linear RGB
#: radiance). Key is the original single light_dir, so the familiar
#: highlight placement is kept; fill is a dim cool opposite-side light;
#: rim sits low behind/below to pick out silhouettes (bell lips, flanges);
#: back sits roughly opposite the key (raised slightly so it never comes up
#: through the floor) at ~38% of the key, lifting the key's shadow side so it
#: doesn't fall to black. A fifth, CAMERA-RELATIVE fill (camera_fill_dir /
#: CAMERA_FILL_RGB) is appended at draw time - see N_LIGHTS.
LIGHT_RIG = (
    ((0.4, 0.6, 0.7), (2.6, 2.5, 2.35)),     # key - warm white
    ((-0.6, -0.3, 0.25), (0.55, 0.62, 0.75)),  # fill - cool, dim
    ((-0.2, 0.8, -0.55), (0.9, 0.9, 0.95)),    # rim - neutral
    ((-0.45, -0.65, 0.15), (0.95, 0.98, 1.05)),  # back - opposite the key, cool neutral
)

#: Camera-relative "headlight" fill: follows the viewer (from behind the
#: camera, offset up/right by CAMERA_FILL_OFFSET_UP/_RIGHT) so whichever side
#: the user orbits to is never unlit. ~25% of the key so the key still shapes.
#: DIFFUSE-ONLY (no specular): a headlight's highlight would land dead-centre
#: on every metal part as a glare dot.
CAMERA_FILL_RGB = (0.65, 0.65, 0.66)
CAMERA_FILL_OFFSET_UP = 0.35
CAMERA_FILL_OFFSET_RIGHT = 0.25

#: Total lights the shader loops over: the world-fixed rig + the camera fill.
N_LIGHTS = len(LIGHT_RIG) + 1

#: Wrap-lighting factor on the DIFFUSE term only: n.l is remapped to
#: (n.l + w)/(1 + w), so diffuse light rolls ~17 deg past the geometric
#: terminator instead of cutting off hard (a soft "shadow" edge). Specular
#: keeps the true n.l, so highlights stay physically placed.
DIFFUSE_WRAP = 0.3

#: Procedural environment (linear RGB): sky above, ground below, and a bright
#: soft horizon band between them (a studio "softbox" stand-in).
ENV_SKY = (0.32, 0.36, 0.44)
ENV_GROUND = (0.14, 0.13, 0.12)   # raised from 0.07: downward faces pick up bounce light
ENV_HORIZON = (1.05, 1.0, 0.95)
ENV_HORIZON_WIDTH = 0.12      # band half-width in up-component units at roughness 0
ENV_HORIZON_ROUGH_WIDEN = 0.7  # extra half-width at roughness 1 (the "blur")
EXPOSURE = 1.0

#: Floor on GGX alpha - a perfectly smooth (alpha=0) surface makes the NDF a
#: delta that no finite light can hit; matches common real-time practice.
MIN_ALPHA = 0.002
DIELECTRIC_F0 = 0.04


def blinn_to_pbr(specular_strength, shininess):
    """
    Fallback (metallic, roughness) for a MeshBuffers piece built with only the
    legacy Blinn-Phong pair (every generic-hardware call site in
    gui/mesh_builder.py - HARDWARE_SPECULAR_STRENGTH/HARDWARE_SHININESS - plus
    any Shape Lab scene piece). Roughness from the standard Blinn exponent <->
    Beckmann slope mapping alpha^2 = 2/(n+2), GGX alpha ~= Beckmann alpha,
    perceptual roughness = sqrt(alpha). Metalness ramps from 0 at a dull
    highlight (<=0.2, plastics/composites) to 1 at a strong one (>=0.5, bare
    metal) - the old field's documented meaning ("higher = more metallic").
    """
    n = max(float(shininess), 0.0)
    roughness = float(np.clip((2.0 / (n + 2.0)) ** 0.25, 0.0, 1.0))
    metallic = float(np.clip((float(specular_strength) - 0.2) / 0.3, 0.0, 1.0))
    return metallic, roughness


def camera_fill_dir(eye, target):
    """
    World-space unit direction TOWARD the camera-relative fill light: the
    view-back direction (target -> eye) nudged up and to the right in the
    camera's own frame, so the light sits just behind/over the viewer's
    shoulder. Uses the camera-true up (not world +Z) so it stays well-defined
    when CameraState's full-360 orbit passes over the pole.
    """
    f = _norm(np.asarray(eye, dtype=float) - np.asarray(target, dtype=float))
    right = np.cross(np.asarray(ENV_UP, dtype=float), f)
    if np.linalg.norm(right) < 1e-6:          # looking straight down/up
        right = np.cross(np.array([1.0, 0.0, 0.0]), f)
    right = _norm(right)
    up = np.cross(f, right)
    return _norm(f + CAMERA_FILL_OFFSET_UP * up + CAMERA_FILL_OFFSET_RIGHT * right)


def full_light_list(eye, target):
    """The N_LIGHTS (direction, rgb) pairs the shader is fed for one frame."""
    return tuple(LIGHT_RIG) + ((tuple(camera_fill_dir(eye, target)), CAMERA_FILL_RGB),)


def resolve_pbr(buf):
    """(metallic, roughness) for one MeshBuffers - explicit values if the
    builder stamped them, else blinn_to_pbr of its legacy pair."""
    fm, fr = blinn_to_pbr(buf.specular_strength, buf.shininess)
    m = fm if buf.metallic is None else float(buf.metallic)
    r = fr if buf.roughness is None else float(buf.roughness)
    return m, r


def stamp_pbr(pieces, metallic, roughness, data_colors=False):
    """Set explicit PBR values on every piece in-place (a material-backed
    build call's whole output shares one material). Returns `pieces`."""
    for p in pieces:
        p.metallic = metallic
        p.roughness = roughness
        p.data_colors = bool(data_colors)
    return pieces


# ---------------------------------------------------------------------------
# GLSL (GLSL 1.20-compatible: attribute/varying/gl_FragColor, same dialect as
# the existing shaders in preview3d_gl.py). Uses the same vertex shader.
# ---------------------------------------------------------------------------
PBR_FRAGMENT_SHADER = """
varying vec3 v_normal;
varying vec3 v_color;
varying vec3 v_world_pos;
uniform vec3 u_eye_pos;
uniform float u_metallic;
uniform float u_roughness;
uniform float u_flat_shade;
uniform float u_data_colors;
uniform vec3 u_light_dir[%(N_LIGHTS)d];
uniform vec3 u_light_rgb[%(N_LIGHTS)d];
uniform vec3 u_env_up;
uniform vec3 u_env_sky;
uniform vec3 u_env_ground;
uniform vec3 u_env_horizon;
uniform float u_env_horizon_width;
uniform float u_env_horizon_rough_widen;
uniform float u_exposure;
// X-ray / Flow translucent pass (gui/preview3d_gl_core/render_layers.py):
// u_alpha = 1.0 is the opaque path, output identical to the plain PBR shader.
uniform float u_alpha;       // face-on opacity
uniform float u_rim_power;   // grazing-angle opacity rise (render_layers.rim_alpha)
uniform int u_facing_pass;   // 0 = all fragments, 1 = facing away from eye, 2 = facing eye

const float PI = 3.14159265;
const float MIN_ALPHA = %(MIN_ALPHA)r;
const float DIELECTRIC_F0 = %(DIELECTRIC_F0)r;
const float DIFFUSE_WRAP = %(DIFFUSE_WRAP)r;

vec3 srgb_to_linear(vec3 c) { return pow(max(c, vec3(0.0)), vec3(2.2)); }
vec3 linear_to_srgb(vec3 c) { return pow(max(c, vec3(0.0)), vec3(1.0 / 2.2)); }
vec3 aces_tonemap(vec3 x) {
    return clamp((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0);
}

float d_ggx(float n_dot_h, float alpha) {
    float a2 = alpha * alpha;
    float d = n_dot_h * n_dot_h * (a2 - 1.0) + 1.0;
    return a2 / (PI * d * d);
}
float g_smith(float n_dot_v, float n_dot_l, float rough) {
    float k = (rough + 1.0) * (rough + 1.0) / 8.0;
    return (n_dot_v / (n_dot_v * (1.0 - k) + k)) * (n_dot_l / (n_dot_l * (1.0 - k) + k));
}
vec3 f_schlick(float cos_t, vec3 f0) { return f0 + (1.0 - f0) * pow(1.0 - cos_t, 5.0); }

vec3 environment(vec3 d, float rough) {
    float u = dot(normalize(d), u_env_up);
    vec3 base = mix(u_env_ground, u_env_sky, smoothstep(-0.25, 0.6, u));
    float w = u_env_horizon_width + u_env_horizon_rough_widen * rough;
    float band = exp(-(u * u) / (w * w)) * (u_env_horizon_width / w);
    return base + u_env_horizon * band;
}
vec2 env_brdf_approx(float n_dot_v, float rough) {
    vec4 c0 = vec4(-1.0, -0.0275, -0.572, 0.022);
    vec4 c1 = vec4(1.0, 0.0425, 1.04, -0.04);
    vec4 r = rough * c0 + c1;
    float a004 = min(r.x * r.x, exp2(-9.28 * n_dot_v)) * r.x + r.y;
    return vec2(-1.04, 1.04) * a004 + r.zw;
}

void main() {
    vec3 N = normalize(v_normal);
    vec3 V = normalize(u_eye_pos - v_world_pos);
    // Translucent-pass facing split on the RAW normal (before the two-sided
    // flip below) - triangle winding isn't consistent across the builders,
    // the outward normals are.
    float ndotv_raw = dot(N, V);
    if (u_facing_pass == 1 && ndotv_raw >= 0.0) discard;
    if (u_facing_pass == 2 && ndotv_raw < 0.0) discard;
    float out_alpha = 1.0;
    if (u_alpha < 1.0) {
        float grazing = 1.0 - clamp(abs(ndotv_raw), 0.0, 1.0);
        out_alpha = u_alpha + (1.0 - u_alpha) * pow(grazing, u_rim_power);
    }
    if (u_flat_shade > 0.5) {
        gl_FragColor = vec4(v_color, out_alpha);
        return;
    }
    if (u_data_colors > 0.5) {
        // Heat-flux colormap readout: keep the colormap's own sRGB values
        // (no linearize/tonemap hue shift), soft key-light shape cue only.
        float k = max(dot(N, normalize(u_light_dir[0])), 0.0);
        gl_FragColor = vec4(v_color * (0.45 + 0.55 * k), out_alpha);
        return;
    }
    // Two-sided: shells are open at the bell lip, so a back face can be seen.
    if (dot(N, V) < 0.0) N = -N;
    vec3 albedo = srgb_to_linear(v_color);
    float rough = clamp(u_roughness, 0.0, 1.0);
    float metal = clamp(u_metallic, 0.0, 1.0);
    float alpha = max(rough * rough, MIN_ALPHA);
    vec3 f0 = mix(vec3(DIELECTRIC_F0), albedo, metal);
    float n_dot_v = max(dot(N, V), 1e-4);

    vec3 color = vec3(0.0);
    for (int i = 0; i < %(N_LIGHTS)d; i++) {
        vec3 L = normalize(u_light_dir[i]);
        float n_dot_l_raw = dot(N, L);
        float wrap = max((n_dot_l_raw + DIFFUSE_WRAP) / (1.0 + DIFFUSE_WRAP), 0.0);
        if (wrap <= 0.0) continue;
        float n_dot_l = max(n_dot_l_raw, 0.0);
        vec3 H = normalize(L + V);
        float n_dot_h = max(dot(N, H), 0.0);
        float v_dot_h = max(dot(V, H), 0.0);
        vec3 F = f_schlick(v_dot_h, f0);
        vec3 kd = (1.0 - F) * (1.0 - metal);
        color += kd * albedo / PI * u_light_rgb[i] * wrap;
        // camera fill (last light) is diffuse-only: a headlight highlight
        // would sit dead-centre on every metal part and read as a glare dot
        if (n_dot_l > 0.0 && i < %(N_LIGHTS)d - 1) {
            vec3 spec = d_ggx(n_dot_h, alpha) * g_smith(n_dot_v, n_dot_l, rough) * F
                        / (4.0 * n_dot_v * n_dot_l + 1e-4);
            color += spec * u_light_rgb[i] * n_dot_l;
        }
    }
    vec3 R = reflect(-V, N);
    vec2 ab = env_brdf_approx(n_dot_v, rough);
    color += environment(N, 1.0) * albedo * (1.0 - metal);
    color += environment(R, rough) * (f0 * ab.x + ab.y);

    gl_FragColor = vec4(linear_to_srgb(aces_tonemap(color * u_exposure)), out_alpha);
}
""" % dict(MIN_ALPHA=MIN_ALPHA, DIELECTRIC_F0=DIELECTRIC_F0, DIFFUSE_WRAP=DIFFUSE_WRAP,
           N_LIGHTS=N_LIGHTS)

#: Background: vertical gradient drawn as one full-screen triangle before the
#: scene (depth writes off). Colors are final display (sRGB) values.
BACKGROUND_TOP = (0.20, 0.215, 0.25)
BACKGROUND_BOTTOM = (0.06, 0.06, 0.07)

BACKGROUND_VERTEX_SHADER = """
attribute vec2 in_ndc;
varying float v_t;
void main() {
    v_t = in_ndc.y * 0.5 + 0.5;
    gl_Position = vec4(in_ndc, 0.999, 1.0);
}
"""
BACKGROUND_FRAGMENT_SHADER = """
varying float v_t;
uniform vec3 u_top;
uniform vec3 u_bottom;
void main() {
    gl_FragColor = vec4(mix(u_bottom, u_top, clamp(v_t, 0.0, 1.0)), 1.0);
}
"""


def background_triangle():
    """One oversized NDC triangle covering the whole viewport, (3, 2) float32."""
    return np.array([[-1.0, -1.0], [3.0, -1.0], [-1.0, 3.0]], dtype=np.float32)


# ---------------------------------------------------------------------------
# numpy twins of the GLSL above (scalar-direction, vector-color)
# ---------------------------------------------------------------------------
def _norm(v):
    v = np.asarray(v, dtype=float)
    return v / max(np.linalg.norm(v), 1e-12)


def srgb_to_linear(c):
    return np.power(np.maximum(np.asarray(c, dtype=float), 0.0), 2.2)


def linear_to_srgb(c):
    return np.power(np.maximum(np.asarray(c, dtype=float), 0.0), 1.0 / 2.2)


def aces_tonemap(x):
    x = np.asarray(x, dtype=float)
    return np.clip((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0)


def d_ggx(n_dot_h, alpha):
    a2 = alpha * alpha
    d = n_dot_h * n_dot_h * (a2 - 1.0) + 1.0
    return a2 / (np.pi * d * d)


def g_smith(n_dot_v, n_dot_l, rough):
    k = (rough + 1.0) ** 2 / 8.0
    return (n_dot_v / (n_dot_v * (1.0 - k) + k)) * (n_dot_l / (n_dot_l * (1.0 - k) + k))


def f_schlick(cos_t, f0):
    f0 = np.asarray(f0, dtype=float)
    return f0 + (1.0 - f0) * (1.0 - cos_t) ** 5


def _smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def environment(d, rough):
    u = float(np.dot(_norm(d), ENV_UP))
    s = _smoothstep(-0.25, 0.6, u)
    base = np.asarray(ENV_GROUND) * (1.0 - s) + np.asarray(ENV_SKY) * s
    w = ENV_HORIZON_WIDTH + ENV_HORIZON_ROUGH_WIDEN * rough
    band = np.exp(-(u * u) / (w * w)) * (ENV_HORIZON_WIDTH / w)
    return base + np.asarray(ENV_HORIZON) * band


def env_brdf_approx(n_dot_v, rough):
    c0 = np.array([-1.0, -0.0275, -0.572, 0.022])
    c1 = np.array([1.0, 0.0425, 1.04, -0.04])
    r = rough * c0 + c1
    a004 = min(r[0] * r[0], 2.0 ** (-9.28 * n_dot_v)) * r[0] + r[1]
    return np.array([-1.04, 1.04]) * a004 + r[2:]


def pbr_radiance_reference(N, V, base_rgb, metallic, roughness, lights=None,
                           include_env=True, fill_dir=None):
    """Linear-space radiance before tone mapping - the GLSL `color` variable.
    `lights` defaults to the world-fixed LIGHT_RIG plus the camera fill;
    `fill_dir` (world direction toward that fill) defaults to
    camera_fill_dir placed from V itself (V = the view-back vector, i.e.
    eye - point). Pass an explicit `lights` to isolate specific lights."""
    default_rig = lights is None      # only the default list carries the camera fill
    if lights is None:
        cf = fill_dir if fill_dir is not None else camera_fill_dir(V, (0.0, 0.0, 0.0))
        lights = tuple(LIGHT_RIG) + ((tuple(cf), CAMERA_FILL_RGB),)
    N, V = _norm(N), _norm(V)
    if np.dot(N, V) < 0.0:
        N = -N
    albedo = srgb_to_linear(base_rgb)
    rough = float(np.clip(roughness, 0.0, 1.0))
    metal = float(np.clip(metallic, 0.0, 1.0))
    alpha = max(rough * rough, MIN_ALPHA)
    f0 = DIELECTRIC_F0 * (1.0 - metal) + albedo * metal
    n_dot_v = max(float(np.dot(N, V)), 1e-4)
    color = np.zeros(3)
    for li, (ldir, lrgb) in enumerate(lights):
        L = _norm(ldir)
        n_dot_l_raw = float(np.dot(N, L))
        wrap = max((n_dot_l_raw + DIFFUSE_WRAP) / (1.0 + DIFFUSE_WRAP), 0.0)
        if wrap <= 0.0:
            continue
        n_dot_l = max(n_dot_l_raw, 0.0)
        H = _norm(L + V)
        n_dot_h = max(float(np.dot(N, H)), 0.0)
        v_dot_h = max(float(np.dot(V, H)), 0.0)
        F = f_schlick(v_dot_h, f0)
        kd = (1.0 - F) * (1.0 - metal)
        color = color + kd * albedo / np.pi * np.asarray(lrgb) * wrap
        if n_dot_l > 0.0 and not (default_rig and li == len(lights) - 1):
            spec = d_ggx(n_dot_h, alpha) * g_smith(n_dot_v, n_dot_l, rough) * F \
                / (4.0 * n_dot_v * n_dot_l + 1e-4)
            color = color + spec * np.asarray(lrgb) * n_dot_l
    if include_env:
        R = 2.0 * np.dot(N, V) * N - V
        ab = env_brdf_approx(n_dot_v, rough)
        color = color + environment(N, 1.0) * albedo * (1.0 - metal)
        color = color + environment(R, rough) * (f0 * ab[0] + ab[1])
    return color


def pbr_shade_reference(N, L_unused, V, base_rgb, metallic, roughness, **kw):
    """Final display (sRGB, 0..1) color for one shading point, mirroring
    PBR_FRAGMENT_SHADER's main(). `L_unused` kept for signature symmetry with
    the plan/old single-light API - the rig in LIGHT_RIG is what's lit."""
    return linear_to_srgb(aces_tonemap(
        pbr_radiance_reference(N, V, base_rgb, metallic, roughness, **kw) * EXPOSURE))


def self_test():
    from .mesh_primitives import MeshBuffers

    # blinn_to_pbr: range + monotonicity
    shins = [4.0, 8.0, 32.0, 65.0, 110.0, 400.0]
    roughs = [blinn_to_pbr(0.5, s)[1] for s in shins]
    assert all(0.0 <= r <= 1.0 for r in roughs)
    assert all(a > b for a, b in zip(roughs, roughs[1:])), roughs
    mets = [blinn_to_pbr(s, 32.0)[0] for s in (0.0, 0.2, 0.35, 0.5, 0.9)]
    assert mets[0] == 0.0 and mets[1] == 0.0 and mets[-1] == 1.0
    assert all(a <= b for a, b in zip(mets, mets[1:]))
    print("blinn_to_pbr self-check: OK")

    # resolve_pbr: explicit wins, fallback otherwise
    z = np.zeros((0, 3), dtype=np.float32)
    b = MeshBuffers(z, z, z, np.zeros((0, 3), dtype=np.uint32), 0.55, 65.0)
    assert resolve_pbr(b) == blinn_to_pbr(0.55, 65.0)
    stamp_pbr([b], 0.3, 0.7)
    assert resolve_pbr(b) == (0.3, 0.7) and not b.data_colors
    print("resolve_pbr/stamp_pbr self-check: OK")

    # Every real material carries in-range PBR values (the physics-side
    # dataclasses allow None = fallback, but every shipped entry is explicit).
    from ...physics import materials, turbopump_materials
    for m in list(materials.MATERIALS.values()) + list(turbopump_materials.MATERIALS.values()):
        assert m.metallic is not None and 0.0 <= m.metallic <= 1.0, m.key
        assert m.roughness is not None and 0.0 <= m.roughness <= 1.0, m.key
    print("material PBR-field self-check: OK")

    # No NaN/Inf anywhere over a sweep incl. grazing and back-facing views.
    rng = np.random.default_rng(3)
    for _ in range(400):
        N = rng.normal(size=3)
        V = rng.normal(size=3)
        c = pbr_shade_reference(N, None, V, rng.random(3), rng.random(), rng.random())
        assert np.all(np.isfinite(c)) and np.all(c >= 0.0) and np.all(c <= 1.0), c
    for rough in (0.0, 1.0):
        c = pbr_shade_reference((0, 0, 1), None, (1, 0, 1e-6), (0.7, 0.4, 0.2), 1.0, rough)
        assert np.all(np.isfinite(c))
    print("pbr_shade_reference finiteness/range self-check: OK")

    # Mirror-reflection geometry on the key light: smoother = tighter, brighter
    # peak; off-peak falls faster for smooth than rough.
    L = _norm(LIGHT_RIG[0][0])
    N = np.array([0.0, 0.0, 1.0])
    N = _norm(L + np.array([0.0, 0.0, 1.0]))  # a normal that has a clear light
    V_peak = 2.0 * np.dot(N, L) * N - L        # perfect reflection of the key light
    key_only = (LIGHT_RIG[0],)
    grey = (0.6, 0.6, 0.6)

    def spec_at(V, rough):
        return pbr_radiance_reference(N, V, grey, 1.0, rough, lights=key_only,
                                      include_env=False).mean()
    peaks = [spec_at(V_peak, r) for r in (0.2, 0.4, 0.7)]
    assert peaks[0] > peaks[1] > peaks[2], peaks
    off = _norm(V_peak + 0.35 * np.cross(N, V_peak))
    assert spec_at(off, 0.2) / peaks[0] < spec_at(off, 0.7) / peaks[2]
    print("GGX roughness-lobe self-check: OK")

    # Metals tint their highlight with the base color; dielectrics stay white.
    copper = (0.72, 0.45, 0.20)
    c_metal = pbr_radiance_reference(N, V_peak, copper, 1.0, 0.3, lights=key_only,
                                     include_env=False)
    assert c_metal[0] > 1.5 * c_metal[2], c_metal
    # dielectric: subtract its diffuse-only (rough=1 lobe is broad) part by
    # comparing a black-albedo sample, whose light is spec only
    c_diel = pbr_radiance_reference(N, V_peak, (0.0, 0.0, 0.0), 0.0, 0.3, lights=key_only,
                                    include_env=False)
    c_diel = c_diel / np.asarray(LIGHT_RIG[0][1])  # divide out the warm key light's tint
    assert np.allclose(c_diel, c_diel[0], rtol=1e-3) and c_diel[0] > 0.0, c_diel
    c_metal = c_metal / np.asarray(LIGHT_RIG[0][1])
    assert c_metal[0] > 1.5 * c_metal[2], c_metal
    print("metal/dielectric highlight-color self-check: OK")

    # Back/fill lighting: the face pointing straight AWAY from the key is lit
    # noticeably (not black), and brighter than the round-1 3-light rig gave.
    old_rig = LIGHT_RIG[:3]
    Nb = -_norm(LIGHT_RIG[0][0])
    Vb = _norm(Nb + np.array([0.0, 0.0, 0.3]))   # viewer on that shadow side
    grey_d = (0.55, 0.55, 0.55)
    new_b = pbr_radiance_reference(Nb, Vb, grey_d, 0.0, 0.6).mean()
    old_b = pbr_radiance_reference(Nb, Vb, grey_d, 0.0, 0.6, lights=old_rig).mean()
    assert new_b > 1.5 * old_b and new_b > 0.05, (new_b, old_b)
    print(f"shadow-side back/fill self-check: OK (radiance {old_b:.3f} -> {new_b:.3f})")

    # Wrap lighting: diffuse from the key alone is continuous across the
    # geometric terminator and still > 0 a little past 90 deg.
    Lk = _norm(LIGHT_RIG[0][0])
    perp = _norm(np.cross(Lk, [0.0, 0.0, 1.0]))
    Vt = _norm(Lk + perp)
    vals = []
    for ang in np.radians(np.linspace(60.0, 120.0, 121)):
        Nt = _norm(np.cos(ang) * Lk + np.sin(ang) * np.cross(perp, Lk))
        vals.append(pbr_radiance_reference(Nt, Vt, grey_d, 0.0, 1.0, lights=key_only,
                                           include_env=False).mean())
    vals = np.array(vals)
    assert np.max(np.abs(np.diff(vals))) < 0.05 * vals.max(), "hard terminator step"
    assert vals[40] > 0.0    # 100 deg from the key: past the geometric terminator
    print("diffuse wrap (soft terminator) self-check: OK")

    # Camera fill: unit, on the viewer's side, and it follows the camera.
    for eye in ((3.0, 0.0, 0.5), (0.0, -2.0, 1.0), (0.0, 0.0, 4.0), (-1.0, 1.0, -2.0)):
        d = camera_fill_dir(eye, (0.0, 0.0, 0.0))
        assert abs(np.linalg.norm(d) - 1.0) < 1e-9
        assert np.dot(d, _norm(eye)) > 0.8, (eye, d)
    assert np.dot(camera_fill_dir((3, 0, 0), (0, 0, 0)), camera_fill_dir((-3, 0, 0), (0, 0, 0))) < 0
    assert len(full_light_list((3, 0, 0), (0, 0, 0))) == N_LIGHTS
    print("camera_fill_dir self-check: OK")

    # Tone map: monotonic, bounded, 0 -> 0.
    xs = np.linspace(0.0, 50.0, 200)
    t = aces_tonemap(xs)
    assert t[0] == 0.0 and np.all(np.diff(t) >= 0.0) and t.max() <= 1.0
    assert np.allclose(linear_to_srgb(srgb_to_linear([0.2, 0.5, 0.9])), [0.2, 0.5, 0.9])
    print("tonemap/sRGB self-check: OK")

    # GLSL <-> numpy lockstep smoke check: every numpy twin has a same-named
    # GLSL function, and every uniform the widget sets is declared.
    for fn in ("srgb_to_linear", "linear_to_srgb", "aces_tonemap", "d_ggx", "g_smith",
               "f_schlick", "environment", "env_brdf_approx"):
        assert f" {fn}(" in PBR_FRAGMENT_SHADER, fn
    for u in ("u_metallic", "u_roughness", "u_flat_shade", "u_data_colors", "u_light_dir",
              "u_light_rgb", "u_env_up", "u_env_sky", "u_env_ground", "u_env_horizon",
              "u_env_horizon_width", "u_env_horizon_rough_widen", "u_exposure", "u_eye_pos",
              "u_alpha", "u_rim_power", "u_facing_pass"):
        assert f"uniform " in PBR_FRAGMENT_SHADER and f" {u}" in PBR_FRAGMENT_SHADER, u
    assert "%(" not in PBR_FRAGMENT_SHADER
    assert f"u_light_dir[{N_LIGHTS}]" in PBR_FRAGMENT_SHADER
    assert f"u_light_rgb[{N_LIGHTS}]" in PBR_FRAGMENT_SHADER
    assert f"i < {N_LIGHTS};" in PBR_FRAGMENT_SHADER
    tri = background_triangle()
    assert tri.shape == (3, 2) and tri.min() == -1.0
    print("GLSL source structure self-check: OK")

    print("ALL SHADING CHECKS OK")


if __name__ == "__main__":
    self_test()
