"""
Discrete cooling-tube/channel bundle mesh builders for the OpenGL 3D
preview: the corrugated groove/rib modulated-grid construction
(milled_channel/tube_wall/coax_shell), and genuinely discrete round-tube
geometry (single-pass and F-1-style double-pass) for tube_wall construction
specifically. Split out of the former single-file gui/preview3d_gl_core.py
by geometry-operation kind - see this package's __init__.py for the
overview. No OpenGL/Tk import, pure numpy.
"""
import numpy as np

from ...physics import geometry3d
from .hardware_constants import (VISUAL_CHANNEL_COUNT_MAX, CHANNEL_OUTER_JACKET_M,
                                 TUBE_BRAZE_SEAM_FRAC)
from .mesh_primitives import mesh_from_grid, revolve_to_buffers
from .profile_geometry import offset_profile

def visual_channel_count(n_channels_physical):
    """
    Cosmetic-only downsample from the real physical channel/tube count
    (cooling.channel_count(), ~200-250) to a mesh-legible visual rib count.
    No physics meaning, no validate.py spot-check implication - each visual
    rib represents `group` physical channels, group = ceil(n_phys / MAX).
    """
    if n_channels_physical <= 0:
        return 0
    group = max(1, int(np.ceil(n_channels_physical / VISUAL_CHANNEL_COUNT_MAX)))
    return max(1, round(n_channels_physical / group))

def channel_modulated_grid(outer_xs_m, outer_rs_m, n_theta, n_channels_physical,
                            channel_height_profile_m, land_fraction, construction,
                            thickness_m):
    """
    Builds a (n_theta, n_stations) X,Y,Z grid whose radius varies with BOTH
    the station (x) and the circumferential position (theta) - a rib/tube
    pattern riding on top of the plain offset outer wall (offset_profile).
    triangulate_grid's index buffer needs no change since it only depends on
    grid SHAPE, never on how r was computed.

    `channel_height_profile_m` and `thickness_m` must already be resampled
    onto this piece's own stations (len(outer_xs_m),) - same convention as
    gui/preview3d_gl.py's existing q_colors() interpolation for the heat-flux
    overlay; this function doesn't know about the whole-engine profile.

    construction selects the cross-section waveform:
      "milled_channel" - rectangular groove: flat land (land_fraction of the
                          pitch), hard-edged recessed channel elsewhere.
      "tube_wall"       - smooth round crest, one per pitch, always PROUD of
                          the base wall (tubes stand out, don't recess in).
      "coax_shell"      - no modulation at all (a smooth double-wall
                          annulus); short-circuits straight to
                          geometry3d.revolve_profile.

    Amplitude is clamped to 60% of the local wall thickness so at least 40%
    of the wall remains continuous material at every channel trough/tube
    root (checked in the self-test below).
    """
    outer_xs_m = np.asarray(outer_xs_m, dtype=float)
    outer_rs_m = np.asarray(outer_rs_m, dtype=float)
    n_stations = outer_xs_m.size
    theta = np.linspace(0.0, 2.0 * np.pi, n_theta)

    if construction == "coax_shell" or n_channels_physical <= 0:
        return geometry3d.revolve_profile(outer_xs_m, outer_rs_m, n_theta)

    n_visual = visual_channel_count(n_channels_physical)
    channel_height_profile_m = np.broadcast_to(
        np.asarray(channel_height_profile_m, dtype=float), (n_stations,))
    thickness_m = np.broadcast_to(np.asarray(thickness_m, dtype=float), (n_stations,))
    amp_m = np.clip(channel_height_profile_m, 0.0, 0.6 * thickness_m)

    phase = (n_visual * theta / (2.0 * np.pi)) % 1.0  # (n_theta,), in [0, 1)
    if construction == "milled_channel":
        waveform = np.where(phase < land_fraction, 0.0, -1.0)
    else:  # "tube_wall"
        waveform = 0.5 * (1.0 - np.cos(2.0 * np.pi * phase))

    delta_r = np.outer(waveform, amp_m)  # (n_theta, n_stations)
    R = outer_rs_m[None, :] + delta_r
    X = np.broadcast_to(outer_xs_m[None, :], (n_theta, n_stations))
    Theta = np.broadcast_to(theta[:, None], (n_theta, n_stations))
    Y = R * np.cos(Theta)
    Z = R * np.sin(Theta)
    return X, Y, Z

def _tube_geometry_profile(outer_rs_m, inner_rs_m, channel_height_profile_m, thickness_m, n_visual,
                           n_local=None):
    """
    Shared per-station tube geometry for tube_wall rendering - used by both
    tube_bundle_pieces' single (down-flow) tube pass and double_pass_tube_pieces'
    interleaved down/up passes, so every circuit style derives the same shape.

    Returns (half_height_m, center_rs_m, valley_rs_m, half_width_m), each shape
    (n_stations,). A real brazed tube bundle is CONTIGUOUS: uniform round tubes are
    swaged/hydroformed to a taper, bent to contour, then "spanked" to a round or
    oval section at every station and furnace-brazed on a fixture that keeps the
    gaps between tubes evenly distributed [Huzel p.113-114; SP-8087 Sec.2.1.1.3
    p.12-13, Fig. 1]. So each tube is an ELLIPSE:
      - half_width_m (circumferential) = half the local centre-to-centre chord
        (2*Rc*sin(pi/n_local)) less TUBE_BRAZE_SEAM_FRAC - neighbours always touch;
      - half_height_m (radial) = min(half the real channel height, half the
        despiked outer-inner gap, half_width_m) - never taller than wide, so the
        tube is round where the pitch binds (the throat) and flattens to an oval
        where the circumference outgrows the tube height (Huzel Fig. 4-31).
    `n_local` is the number of tubes actually present around the circumference at
    each station (scalar or (n_stations,)); default n_visual. Double-pass callers
    pass 2*n_visual where down and up tubes interleave.

    `gap_m` (outer_rs_m - inner_rs_m, the hard floor on tube height) is DESPIKED
    first: a real contour-segment join (fillet/arc endpoint, or the exact chamber/
    extension material split) can make ONE station's gap collapse toward zero
    independent of its neighbors - offset_profile's local meridian-normal offset
    briefly goes near-purely-axial there (see meridian_normals/_dedupe_monotonic),
    so outer_rs_m ~= inner_rs_m at exactly that station regardless of thickness_m.
    Left alone, this pinches that one station's tube to near-zero and back to
    normal one station later - a visible "pinch-then-bulge" that reads as tubes
    clipping through the surface, most noticeable right at a body/extension join. A
    single interior station whose gap is less than half of BOTH its neighbors' is
    that exact signature (a genuine, physically real taper never drops that sharply
    over one station), so it's replaced by the neighbor minimum; any real multi-
    station transition is left untouched.
    """
    outer_rs_m = np.asarray(outer_rs_m, dtype=float)
    inner_rs_m = np.asarray(inner_rs_m, dtype=float)
    n_stations = outer_rs_m.size
    channel_height_profile_m = np.broadcast_to(
        np.asarray(channel_height_profile_m, dtype=float), (n_stations,))
    thickness_m = np.broadcast_to(np.asarray(thickness_m, dtype=float), (n_stations,))
    # Clip against the wall thickness actually AVAILABLE for the tube (thickness_m
    # minus the outer jacket skin), not a blanket 0.6x-of-thickness fraction - the
    # caller's effective_offset_thickness_m already guarantees thickness_m >=
    # channel_height + CHANNEL_OUTER_JACKET_M whenever the bare structural wall is
    # too thin to contain the real tube, so this clip is a no-op in exactly that
    # case (a 0.6x clip visibly thinned tubes approaching a skirt/material split).
    amp_m = np.clip(channel_height_profile_m, 0.0, np.maximum(thickness_m - CHANNEL_OUTER_JACKET_M, 0.0))

    n_loc = np.broadcast_to(np.asarray(n_visual if n_local is None else n_local, dtype=float),
                            (n_stations,))
    n_loc = np.maximum(n_loc, 1.0)
    # sin(pi/n) chord factor; n=1 (a single "tube") degenerates to the full diameter.
    chord_factor = np.where(n_loc >= 2.0, np.sin(np.pi / n_loc), 1.0)
    width_at_crest_m = outer_rs_m * chord_factor * (1.0 - TUBE_BRAZE_SEAM_FRAC)

    gap_m = np.maximum(outer_rs_m - inner_rs_m, 0.0)
    if gap_m.size >= 3:
        neighbor_min = np.minimum(gap_m[:-2], gap_m[2:])
        interior_dip = gap_m[1:-1] < 0.5 * neighbor_min
        gap_m[1:-1] = np.where(interior_dip, neighbor_min, gap_m[1:-1])

    half_height_m = np.minimum.reduce([0.5 * amp_m, width_at_crest_m, 0.5 * gap_m])
    center_rs_m = outer_rs_m - half_height_m
    # Neighbours touch at their widest point, i.e. at the tube-centre radius, so
    # the chord is taken there (slightly narrower than at the crest).
    half_width_m = np.maximum(center_rs_m, 0.0) * chord_factor * (1.0 - TUBE_BRAZE_SEAM_FRAC)
    half_height_m = np.minimum(half_height_m, half_width_m)
    center_rs_m = outer_rs_m - half_height_m
    # Re-take the chord at the FINAL centre radius (the clamp above can move it
    # out slightly), so the seam is exact; b <= a still holds since Rc only grew.
    half_width_m = np.maximum(center_rs_m, 0.0) * chord_factor * (1.0 - TUBE_BRAZE_SEAM_FRAC)
    half_width_m = np.where(half_height_m > 1e-12, half_width_m, 0.0)  # no tube -> no ribbon
    valley_rs_m = outer_rs_m - 2.0 * half_height_m
    return half_height_m, center_rs_m, valley_rs_m, half_width_m

def tube_end_cap_disk(x_m, center_y_m, center_z_m, tube_r_m, n_theta_tube, base_color_rgb,
                       facing_sign=1.0, specular_strength=0.0, shininess=32.0,
                       half_width_m=None, theta_i=None):
    """
    A flat filled disk closing one discrete tube's open end - the same
    "2-column grid, r=0 degenerates to a fan" construction end_cap_ring uses to
    close the whole shell's ends, but centered on the TUBE's own local center
    (center_y_m, center_z_m) rather than the main engine axis.

    Elliptical when `half_width_m` and `theta_i` are given: `tube_r_m` is then the
    RADIAL half-height and `half_width_m` the circumferential half-width, matching
    _single_tube_mesh's swaged-oval section at tube angle theta_i. Without them it
    is a plain circle of radius tube_r_m (the old behavior).

    Used to give a discrete tube a genuine flat-cut termination instead of
    letting its swept mesh run into a station with zero radius, which renders
    as a cone tapering to a point (see tube_bundle_pieces' `active_end_idx` /
    build_shell_mesh's `tube_cutoff_x_m`).
    """
    phi = np.linspace(0.0, 2.0 * np.pi, n_theta_tube)
    rad = np.array([0.0, 1.0])
    Rad, Phi = np.meshgrid(rad, phi)  # shape (n_theta_tube, 2), matching end_cap_ring's pattern
    X = np.full_like(Rad, float(x_m))
    if half_width_m is None or theta_i is None:
        Y = center_y_m + Rad * tube_r_m * np.cos(Phi)
        Z = center_z_m + Rad * tube_r_m * np.sin(Phi)
    else:
        loc_r = Rad * tube_r_m * np.cos(Phi)            # radial (outward) component
        loc_t = Rad * half_width_m * np.sin(Phi)        # circumferential component
        Y = center_y_m + loc_r * np.cos(theta_i) - loc_t * np.sin(theta_i)
        Z = center_z_m + loc_r * np.sin(theta_i) + loc_t * np.cos(theta_i)
    normal = np.array([facing_sign, 0.0, 0.0], dtype=np.float32)
    normals = np.tile(normal, (n_theta_tube * 2, 1))
    mesh = mesh_from_grid(X, Y, Z, base_color_rgb, normals=normals,
                           specular_strength=specular_strength, shininess=shininess)

    if mesh.indices.shape[0] > 0:
        for tri in mesh.indices:
            p0, p1, p2 = mesh.vertices[tri]
            face_normal = np.cross(p1 - p0, p2 - p0)
            if np.linalg.norm(face_normal) > 1e-18:
                if np.dot(face_normal, normal) < 0.0:
                    mesh.indices = mesh.indices[:, [0, 2, 1]]
                break
    return mesh

def _tube_caps(x_m, center_r_m, half_h_m, half_w_m, thetas, n_theta_tube, base_color_rgb,
               facing_sign, specular_strength, shininess):
    """Elliptical flat end caps for every tube angle in `thetas` at one station."""
    if half_h_m <= 1e-9:
        return []
    return [tube_end_cap_disk(x_m, center_r_m * np.cos(t), center_r_m * np.sin(t), half_h_m,
                              n_theta_tube, base_color_rgb, facing_sign=facing_sign,
                              specular_strength=specular_strength, shininess=shininess,
                              half_width_m=half_w_m, theta_i=t)
            for t in thetas]

def tube_bundle_pieces(outer_xs_m, outer_rs_m, inner_rs_m, n_theta, n_channels_physical,
                        channel_height_profile_m, thickness_m, base_color_rgb,
                        n_theta_tube=12, specular_strength=0.0, shininess=32.0,
                        active_end_idx=None):
    """
    Genuinely discrete tube geometry for "tube_wall" construction - real
    brazed-tube engines (F-1, J-2, RL10) show individually recognizable tubes,
    not a continuous corrugated ridge (channel_modulated_grid's "tube_wall"
    waveform, which this REPLACES for tube_wall specifically - that function is
    untouched and still used for "milled_channel").

    Returns (backing, tube_pieces): `backing` is a plain smooth revolve at a
    RECESSED "valley" radius - the thin webbing/liner the tubes sit on,
    keeping the shell's outer envelope closed for end-capping/bridging
    (build_shell_mesh's outer_xs/outer_rs contract is untouched by this).
    `tube_pieces` is a list of one MeshBuffers per visual tube
    (visual_channel_count-downsampled from n_channels_physical).

    Each tube is a swept ELLIPSE at a FIXED circumferential angle theta_i (tubes
    run straight down the engine, no twist): radial half-height and
    circumferential half-width from _tube_geometry_profile - neighbours touch
    across a braze seam at EVERY station (a real brazed bundle is contiguous),
    round where the pitch binds and a flattened "spanked" oval downstream. The
    radial half-height never exceeds half the ACTUAL (despiked) outer-inner gap,
    so the recessed valley can never dip below the gas-side wall.

    Known simplifications: an untruncated tube's end is left open (the overall
    shell's own end_cap_ring already closes the big-picture silhouette);
    normals ignore the slight axial tilt a tapering tube would truly impart.

    `active_end_idx`, if given, truncates the swept tube geometry to stations
    [0, active_end_idx] (inclusive) and closes each tube's open end with a flat
    elliptical cap there (tube_end_cap_disk) instead of letting it run to a
    zero-size station, which would render as a cone tapering to a point.
    """
    outer_xs_m = np.asarray(outer_xs_m, dtype=float)
    outer_rs_m = np.asarray(outer_rs_m, dtype=float)
    inner_rs_m = np.asarray(inner_rs_m, dtype=float)

    n_visual = visual_channel_count(n_channels_physical)
    if n_visual <= 0:
        return revolve_to_buffers(outer_xs_m, outer_rs_m, n_theta, base_color_rgb,
                                   specular_strength=specular_strength, shininess=shininess), []

    half_h, center_rs_m, valley_rs_m, half_w = _tube_geometry_profile(
        outer_rs_m, inner_rs_m, channel_height_profile_m, thickness_m, n_visual)

    backing = revolve_to_buffers(outer_xs_m, valley_rs_m, n_theta, base_color_rgb,
                                  specular_strength=specular_strength, shininess=shininess)

    n_stations = outer_xs_m.size
    end_idx = n_stations - 1
    if active_end_idx is not None:
        end_idx = int(np.clip(active_end_idx, 0, n_stations - 1))
    sl = slice(0, end_idx + 1)

    phi = np.linspace(0.0, 2.0 * np.pi, n_theta_tube)
    thetas = [2.0 * np.pi * i / n_visual for i in range(n_visual)]
    tube_pieces = [
        _single_tube_mesh(outer_xs_m[sl], phi, center_rs_m[sl], half_h[sl], t, base_color_rgb,
                           specular_strength=specular_strength, shininess=shininess,
                           half_width_m=half_w[sl])
        for t in thetas
    ]

    if active_end_idx is not None and end_idx < n_stations - 1:
        tube_pieces += _tube_caps(float(outer_xs_m[end_idx]), float(center_rs_m[end_idx]),
                                  float(half_h[end_idx]), float(half_w[end_idx]), thetas,
                                  n_theta_tube, base_color_rgb, 1.0, specular_strength, shininess)

    return backing, tube_pieces

def _single_tube_mesh(outer_xs_m, phi, center_rs_m, tube_radius_m, theta_i, base_color_rgb,
                       specular_strength=0.0, shininess=32.0, half_width_m=None):
    """
    One swept tube mesh at fixed circumferential angle theta_i. `tube_radius_m` is
    the RADIAL half-height; `half_width_m` (default = tube_radius_m, i.e. a circle)
    the circumferential half-width - an ellipse (b cos phi, a sin phi) in the tube's
    local (radial, circumferential) frame, with true ellipse normals
    (a cos phi, b sin phi)/|.|. Also reused by duct/manifold builders in its
    circular form.
    """
    if half_width_m is None:
        half_width_m = tube_radius_m
    X, Phi = np.meshgrid(outer_xs_m, phi)
    Rc, _ = np.meshgrid(center_rs_m, phi)
    B, _ = np.meshgrid(np.asarray(tube_radius_m, dtype=float) * np.ones_like(outer_xs_m), phi)
    A, _ = np.meshgrid(np.asarray(half_width_m, dtype=float) * np.ones_like(outer_xs_m), phi)
    local_r = Rc + B * np.cos(Phi)
    local_t = A * np.sin(Phi)
    Y = local_r * np.cos(theta_i) - local_t * np.sin(theta_i)
    Z = local_r * np.sin(theta_i) + local_t * np.cos(theta_i)
    # Ellipse outward normal in the local frame; a zero-size station falls back
    # to the circle normal so the normal stays unit length.
    n_r = A * np.cos(Phi)
    n_t = B * np.sin(Phi)
    n_len = np.hypot(n_r, n_t)
    degenerate = n_len < 1e-15
    n_r = np.where(degenerate, np.cos(Phi), n_r / np.where(degenerate, 1.0, n_len))
    n_t = np.where(degenerate, np.sin(Phi), n_t / np.where(degenerate, 1.0, n_len))
    Nx = np.zeros_like(X)
    Ny = n_r * np.cos(theta_i) - n_t * np.sin(theta_i)
    Nz = n_r * np.sin(theta_i) + n_t * np.cos(theta_i)
    normals_flat = np.stack([Nx.ravel(), Ny.ravel(), Nz.ravel()], axis=1).astype(np.float32)
    return mesh_from_grid(X, Y, Z, base_color_rgb, normals=normals_flat,
                           specular_strength=specular_strength, shininess=shininess)

def double_pass_tube_pieces(outer_xs_m, outer_rs_m, inner_rs_m, n_theta, n_channels_physical,
                             channel_height_profile_m, thickness_m, base_color_rgb,
                             n_theta_tube=12, specular_strength=0.0, shininess=32.0,
                             active_end_idx=None, down_start_idx=None):
    """
    F-1-style double-pass tube-wall rendering: a "down" tube set plus a second "up"
    set phase-offset by half a pitch so the two INTERLEAVE - real F-1/SP-8120
    references show paired down/up tubes running side by side in one contiguous
    brazed bundle. Where both sets are present there are 2*n_visual tubes around
    the circumference, so _tube_geometry_profile is given n_local = 2*n_visual
    there and each down tube touches the up tubes either side of it.

    Physics note: this is a RENDERING-ONLY approximation of the tube layout; the
    coolant-side physics lives in physics/cooling.py.

    `active_end_idx`, if given, truncates BOTH sets to stations [0, active_end_idx],
    each tube capped with a flat elliptical disk there.

    `down_start_idx`, if given (> 0), starts the DOWN tubes at that station
    instead of station 0, each capped there - the J-2 layout (physics/design.py
    cooling_flow_topology "j2_mid_nozzle_inlet"), whose down tubes begin at the
    mid-nozzle inlet manifold while the up tubes run the whole length. Upstream of
    it only the up tubes exist, so they widen to fill the full pitch there (n_local
    = n_visual) and narrow to half at the inlet ring, which hides the step. A start
    at/after the (active) last station draws no down tubes in this piece at all.

    Returns (backing, down_tube_pieces, up_tube_pieces, terminal_crest_r_m).
    `terminal_crest_r_m` is the whole piece's own last-station crest radius,
    independent of any active_end_idx truncation.
    """
    outer_xs_m = np.asarray(outer_xs_m, dtype=float)
    outer_rs_m = np.asarray(outer_rs_m, dtype=float)
    inner_rs_m = np.asarray(inner_rs_m, dtype=float)
    terminal_crest_r_m = float(outer_rs_m[-1]) if outer_rs_m.size else 0.0

    n_visual = visual_channel_count(n_channels_physical)
    if n_visual <= 0:
        return (revolve_to_buffers(outer_xs_m, outer_rs_m, n_theta, base_color_rgb,
                                   specular_strength=specular_strength, shininess=shininess),
                [], [], terminal_crest_r_m)

    n_stations = outer_xs_m.size
    end_idx = n_stations - 1
    if active_end_idx is not None:
        end_idx = int(np.clip(active_end_idx, 0, n_stations - 1))
    start = int(down_start_idx) if down_start_idx is not None and down_start_idx > 0 else 0
    has_down = start < end_idx or (start == 0 and end_idx >= 0)

    n_local = np.full(n_stations, 2.0 * n_visual)
    if start > 0:
        n_local[:start] = n_visual   # up tubes alone upstream of the J-2 inlet ring
    half_h, center_rs_m, valley_rs_m, half_w = _tube_geometry_profile(
        outer_rs_m, inner_rs_m, channel_height_profile_m, thickness_m, n_visual, n_local=n_local)

    backing = revolve_to_buffers(outer_xs_m, valley_rs_m, n_theta, base_color_rgb,
                                  specular_strength=specular_strength, shininess=shininess)

    phi = np.linspace(0.0, 2.0 * np.pi, n_theta_tube)
    phase_offset = np.pi / n_visual  # half a pitch - nests between the down tubes
    down_thetas = [2.0 * np.pi * i / n_visual for i in range(n_visual)]
    up_thetas = [t + phase_offset for t in down_thetas]
    kw = dict(specular_strength=specular_strength, shininess=shininess)

    sl_up = slice(0, end_idx + 1)
    up_tubes = [_single_tube_mesh(outer_xs_m[sl_up], phi, center_rs_m[sl_up], half_h[sl_up], t,
                                  base_color_rgb, half_width_m=half_w[sl_up], **kw)
                for t in up_thetas]

    down_tubes = []
    if has_down:
        sl_dn = slice(start, end_idx + 1)
        if start > 0:
            # At the start station use the interleaved (narrow) width so the
            # down tube never overlaps the neighbouring up tubes there.
            _, _, _, half_w_dn = _tube_geometry_profile(
                outer_rs_m, inner_rs_m, channel_height_profile_m, thickness_m, n_visual,
                n_local=2.0 * n_visual)
        else:
            half_w_dn = half_w
        down_tubes = [_single_tube_mesh(outer_xs_m[sl_dn], phi, center_rs_m[sl_dn], half_h[sl_dn], t,
                                        base_color_rgb, half_width_m=half_w_dn[sl_dn], **kw)
                      for t in down_thetas]
        if start > 0:
            down_tubes += _tube_caps(float(outer_xs_m[start]), float(center_rs_m[start]),
                                     float(half_h[start]), float(half_w_dn[start]), down_thetas,
                                     n_theta_tube, base_color_rgb, -1.0, specular_strength, shininess)

    if active_end_idx is not None and end_idx < n_stations - 1:
        args = (float(outer_xs_m[end_idx]), float(center_rs_m[end_idx]),
                float(half_h[end_idx]), float(half_w[end_idx]))
        if has_down:
            down_tubes += _tube_caps(*args, down_thetas, n_theta_tube, base_color_rgb, 1.0,
                                     specular_strength, shininess)
        up_tubes += _tube_caps(*args, up_thetas, n_theta_tube, base_color_rgb, 1.0,
                               specular_strength, shininess)

    return backing, down_tubes, up_tubes, terminal_crest_r_m

def self_test():
    n_theta = 8
    xs_shell = np.array([0.0, 0.3, 0.5, 0.7, 1.5])
    rs_shell = np.array([0.20, 0.20, 0.06, 0.06, 0.35])

    # --- visual_channel_count / channel_modulated_grid ---
    assert visual_channel_count(0) == 0
    assert visual_channel_count(40) == 40                # under the cap - no grouping needed
    # realistic physical counts (F-1 ~178, SSME ~390, RL10 ~180) render at
    # their FULL count, unchanged - no artificial thinning for any real design
    n_vis_dense = visual_channel_count(224)
    assert n_vis_dense == 224
    # the cap only ever bites for an extreme, unrealistic channel-count override
    assert visual_channel_count(5000) == VISUAL_CHANNEL_COUNT_MAX
    assert 0 < n_vis_dense <= VISUAL_CHANNEL_COUNT_MAX

    thick = np.full_like(rs_shell, 0.006)
    ch_height = np.full_like(rs_shell, 0.01)              # deliberately oversized -> must clamp
    for construction in ("milled_channel", "tube_wall", "coax_shell"):
        Xc, Yc, Zc = channel_modulated_grid(xs_shell, rs_shell, n_theta, 224,
                                             ch_height, 0.35, construction, thick)
        Rc = np.sqrt(Yc ** 2 + Zc ** 2)
        assert not np.any(np.isnan(Rc))
        if construction == "coax_shell":
            # no modulation at all: every theta ring matches the base radius exactly
            assert np.allclose(Rc, np.broadcast_to(rs_shell[None, :], Rc.shape))
        else:
            # amplitude never eats more than 60% of the local wall thickness,
            # i.e. modulated radius never drops below base - 0.6*thickness
            assert np.all(Rc >= rs_shell[None, :] - 0.6 * thick[None, :] - 1e-12)
            assert np.max(np.abs(Rc - rs_shell[None, :])) > 0.0   # actually modulates something
    print("channel_modulated_grid self-check: OK")

    # --- tube_bundle_pieces: discrete round-tube geometry for tube_wall ---
    outer_xs_tw, outer_rs_tw = offset_profile(xs_shell, rs_shell, thick)
    n_theta_tube = 12
    backing_tw, tube_pieces = tube_bundle_pieces(
        outer_xs_tw, outer_rs_tw, rs_shell, n_theta, 224, ch_height, thick,
        (0.6, 0.6, 0.6), n_theta_tube=n_theta_tube)

    n_vis = visual_channel_count(224)
    assert len(tube_pieces) == n_vis

    # Recompute the same per-station values tube_bundle_pieces derives
    # internally, to check every tube against, independent of internal
    # implementation details (swaged ellipse: radial half-height b, circumferential
    # half-width a, neighbours touching across TUBE_BRAZE_SEAM_FRAC).
    def expect_profile(outer_rs, inner_rs, ch, th, n_loc):
        amp = np.clip(ch, 0.0, np.maximum(th - CHANNEL_OUTER_JACKET_M, 0.0))
        cf = np.sin(np.pi / n_loc)
        b = np.minimum.reduce([0.5 * amp, outer_rs * cf * (1 - TUBE_BRAZE_SEAM_FRAC),
                               0.5 * (outer_rs - inner_rs)])
        a = (outer_rs - b) * cf * (1 - TUBE_BRAZE_SEAM_FRAC)
        b = np.minimum(b, a)
        a = (outer_rs - b) * cf * (1 - TUBE_BRAZE_SEAM_FRAC)
        return b, outer_rs - b, a

    tube_r_expect, center_r_expect, half_w_expect = expect_profile(
        outer_rs_tw, rs_shell, ch_height, thick, float(n_vis))
    valley_expect = outer_rs_tw - 2.0 * tube_r_expect

    def local_frame(V, x, rc, theta):
        """(axial offset, radial offset, circumferential offset) of points V
        relative to a tube centre at (x, rc, theta)."""
        c, s = np.cos(theta), np.sin(theta)
        dy, dz = V[..., 1] - rc * c, V[..., 2] - rc * s
        return V[..., 0] - x, dy * c + dz * s, -dy * s + dz * c

    def check_ellipse(V, j, theta, b, a, rc):
        _, dr, dt = local_frame(V, outer_xs_tw[j], rc, theta)
        if b <= 1e-9:
            return
        lhs = (dr / b) ** 2 + (dt / a) ** 2
        assert np.allclose(lhs, 1.0, atol=1e-3), (j, lhs.min(), lhs.max())

    # (a) backing radius == outer_rs - 2*half_height at every station, and
    # NEVER reaches or crosses the gas-side wall
    backing_r = np.sqrt(backing_tw.vertices[:, 1] ** 2
                         + backing_tw.vertices[:, 2] ** 2).reshape(n_theta, -1)
    assert np.allclose(backing_r, valley_expect[None, :], atol=1e-4)
    assert np.all(valley_expect >= rs_shell - 1e-9)
    print("tube_bundle_pieces valley-vs-inner-wall self-check: OK")

    # (b) every tube vertex lies on THAT tube's own ellipse; normals are unit
    # length and point away from its local centre
    for i, tube in enumerate(tube_pieces):
        theta_i = 2.0 * np.pi * i / n_vis
        V = tube.vertices.reshape(n_theta_tube, xs_shell.size, 3)
        Nrm = tube.normals.reshape(n_theta_tube, xs_shell.size, 3)
        for j in range(xs_shell.size):
            check_ellipse(V[:, j, :], j, theta_i, tube_r_expect[j], half_w_expect[j],
                          center_r_expect[j])
            n_len = np.linalg.norm(Nrm[:, j, :], axis=-1)
            assert np.allclose(n_len, 1.0, atol=1e-6)
            if tube_r_expect[j] > 1e-9:
                center = np.array([outer_xs_tw[j], center_r_expect[j] * np.cos(theta_i),
                                   center_r_expect[j] * np.sin(theta_i)])
                d = V[:, j, :] - center
                assert np.all(np.sum(Nrm[:, j, :] * d, axis=-1) > 0.0), (i, j)
    print("tube_bundle_pieces per-tube ellipse geometry + normal self-check: OK")

    # (b2) CONTACT: at every station neighbouring tubes' widest points are
    # separated by only the braze seam (a real brazed bundle is contiguous) -
    # the old round-tube clamp opened large gaps wherever channel height bound.
    chord = 2.0 * center_r_expect * np.sin(np.pi / n_vis)
    live = tube_r_expect > 1e-9
    gap_between = chord - 2.0 * half_w_expect
    assert np.all(gap_between[live] <= TUBE_BRAZE_SEAM_FRAC * chord[live] * (1 + 1e-9))
    assert np.all(gap_between[live] >= -1e-12)            # and never overlapping
    # ...and the tube flattens to an oval (a > b) where the pitch outgrows it
    assert np.any(half_w_expect[live] > 1.5 * tube_r_expect[live])
    print("tube_bundle_pieces neighbour-contact (braze seam) self-check: OK")

    # (c) empirical winding check: every triangle's face normal points outward
    # from THAT tube's own local centre
    for i in (0, max(1, n_vis // 3)):
        theta_i = 2.0 * np.pi * i / n_vis
        tube = tube_pieces[i]
        cy, cz = np.cos(theta_i), np.sin(theta_i)
        for a, b, c in tube.indices:
            pa, pb, pc = tube.vertices[a], tube.vertices[b], tube.vertices[c]
            centroid = (pa + pb + pc) / 3.0
            j = int(np.argmin(np.abs(outer_xs_tw - centroid[0])))
            if tube_r_expect[j] <= 1e-9:
                continue
            center = np.array([outer_xs_tw[j], center_r_expect[j] * cy, center_r_expect[j] * cz])
            outward = centroid - center
            outward = outward / (np.linalg.norm(outward) + 1e-12)
            face_normal = np.cross(pb - pa, pc - pa)
            if np.linalg.norm(face_normal) < 1e-18:
                continue
            assert np.dot(face_normal, outward) > 0.0, (i, a, b, c)
    print("tube_bundle_pieces winding self-check: OK")

    # (d) degenerate 2-station piece (conical nozzle extension)
    xs2, rs2 = np.array([0.0, 1.0]), np.array([0.09, 0.35])
    oxs2, ors2 = offset_profile(xs2, rs2, 0.004)
    backing2, tubes2 = tube_bundle_pieces(oxs2, ors2, rs2, n_theta, 224,
                                           np.full(2, 0.01), np.full(2, 0.004),
                                           (0.6, 0.6, 0.6))
    assert len(tubes2) == visual_channel_count(224)
    assert backing2.indices.shape[0] == 2 * (n_theta - 1) * 1
    print("tube_bundle_pieces 2-station piece self-check: OK")

    # (e) n_channels_physical <= 0 -> no tubes, falls back to a plain revolve
    backing0, tubes0 = tube_bundle_pieces(outer_xs_tw, outer_rs_tw, rs_shell, n_theta, 0,
                                           ch_height, thick, (0.6, 0.6, 0.6))
    assert tubes0 == []
    assert np.allclose(backing0.vertices, revolve_to_buffers(
        outer_xs_tw, outer_rs_tw, n_theta, (0.6, 0.6, 0.6)).vertices)
    print("tube_bundle_pieces n_channels<=0 fallback self-check: OK")

    # --- _tube_geometry_profile: despikes a single-station gap collapse,
    # leaving genuine multi-station variation alone ---
    outer_rs_dip = np.full(5, 0.30)
    inner_rs_dip = np.array([0.0, 0.0, 0.299, 0.0, 0.0])   # gap -> 0.001 at station 2 only
    thick_dip = np.full(5, 0.02)
    ch_dip = np.full(5, 0.05)
    n_vis_dip = 8
    tube_r_dip, _, _, _ = _tube_geometry_profile(
        outer_rs_dip, inner_rs_dip, ch_dip, thick_dip, n_vis_dip)
    assert np.allclose(tube_r_dip, tube_r_dip[0], atol=1e-9)
    assert tube_r_dip[0] > 1e-4
    inner_rs_taper = np.array([0.0, 0.20, 0.27, 0.295, 0.299])   # gap shrinks gradually
    tube_r_taper, _, _, _ = _tube_geometry_profile(
        outer_rs_dip, inner_rs_taper, ch_dip, thick_dip, n_vis_dip)
    assert tube_r_taper[-1] < tube_r_taper[0]
    print("_tube_geometry_profile despike self-check: OK")

    # --- hard-cutoff contract: channel height hard-zeroed past a station gives
    # EXACTLY full tube size before it and EXACTLY zero (height AND width - no
    # flat ribbon) after ---
    cutoff_idx = 3
    ch_cutoff = ch_dip.copy()
    ch_cutoff[cutoff_idx:] = 0.0
    tube_r_cutoff, _, _, half_w_cutoff = _tube_geometry_profile(
        outer_rs_dip, np.zeros(5), ch_cutoff, thick_dip, n_vis_dip)
    assert np.allclose(tube_r_cutoff[:cutoff_idx], tube_r_cutoff[0], atol=1e-9)
    assert tube_r_cutoff[0] > 1e-4
    assert np.allclose(tube_r_cutoff[cutoff_idx:], 0.0, atol=1e-12)
    assert np.allclose(half_w_cutoff[cutoff_idx:], 0.0, atol=1e-12)
    print("hard-cutoff (no taper) self-check: OK")

    # --- amp clamp: a wall floored to channel_height + CHANNEL_OUTER_JACKET_M
    # must NOT re-clip the tube below its real channel height ---
    ch_amp_test = 0.006
    thick_amp_test = ch_amp_test + CHANNEL_OUTER_JACKET_M
    tube_r_amp, _, _, _ = _tube_geometry_profile(
        np.full(3, 1.0), np.full(3, 0.9), np.full(3, ch_amp_test), np.full(3, thick_amp_test), 8)
    assert np.allclose(tube_r_amp, 0.5 * ch_amp_test, atol=1e-12)
    print("amp clamp (thin-wall floor) self-check: OK")

    # --- tube_bundle_pieces active_end_idx: a flat elliptical cap instead of a
    # cone tip ---
    cutoff_idx_test = 2
    backing_cut, tubes_cut = tube_bundle_pieces(
        outer_xs_tw, outer_rs_tw, rs_shell, n_theta, 224, ch_height, thick,
        (0.6, 0.6, 0.6), n_theta_tube=n_theta_tube, active_end_idx=cutoff_idx_test)
    assert len(tubes_cut) == 2 * n_vis  # n_vis tube meshes + n_vis cap disks
    tube_meshes_cut, cap_meshes_cut = tubes_cut[:n_vis], tubes_cut[n_vis:]
    cutoff_x = float(outer_xs_tw[cutoff_idx_test])
    for tube in tube_meshes_cut:
        assert np.all(tube.vertices[:, 0] <= cutoff_x + 1e-9)
        assert np.any(np.isclose(tube.vertices[:, 0], cutoff_x, atol=1e-9))
    jc = cutoff_idx_test
    for i, cap in enumerate(cap_meshes_cut):
        theta_i = 2.0 * np.pi * i / n_vis
        assert np.allclose(cap.vertices[:, 0], cutoff_x, atol=1e-9)
        _, dr, dt = local_frame(cap.vertices, cutoff_x, center_r_expect[jc], theta_i)
        lhs = (dr / tube_r_expect[jc]) ** 2 + (dt / half_w_expect[jc]) ** 2
        # every vertex is either the cap centre or on its elliptical rim
        assert np.all(np.isclose(lhs, 0.0, atol=1e-5) | np.isclose(lhs, 1.0, atol=1e-3))
        assert np.any(np.isclose(lhs, 1.0, atol=1e-3))
    _, tubes_nocut = tube_bundle_pieces(
        outer_xs_tw, outer_rs_tw, rs_shell, n_theta, 224, ch_height, thick,
        (0.6, 0.6, 0.6), n_theta_tube=n_theta_tube, active_end_idx=len(outer_xs_tw) - 1)
    assert len(tubes_nocut) == n_vis
    print("tube_bundle_pieces active_end_idx flat-cap self-check: OK")

    # --- double_pass_tube_pieces: interleaved down/up sets, 2*n_vis tubes
    # round the circumference, each touching its neighbours ---
    backing_dp, down_dp, up_dp, terminal_r_dp = double_pass_tube_pieces(
        outer_xs_tw, outer_rs_tw, rs_shell, n_theta, 224, ch_height, thick,
        (0.6, 0.6, 0.6), n_theta_tube=n_theta_tube)
    n_vis_dp = visual_channel_count(224)
    assert len(down_dp) == len(up_dp) == n_vis_dp
    assert np.isclose(terminal_r_dp, float(outer_rs_tw[-1]))
    b_dp, rc_dp, a_dp = expect_profile(outer_rs_tw, rs_shell, ch_height, thick, 2.0 * n_vis_dp)
    phase_offset_dp = np.pi / n_vis_dp
    for i in (0, n_vis_dp // 2):
        for tube, theta_i in ((up_dp[i], 2.0 * np.pi * i / n_vis_dp + phase_offset_dp),
                              (down_dp[i], 2.0 * np.pi * i / n_vis_dp)):
            V = tube.vertices.reshape(n_theta_tube, xs_shell.size, 3)
            for j in range(xs_shell.size):
                check_ellipse(V[:, j, :], j, theta_i, b_dp[j], a_dp[j], rc_dp[j])
    chord_dp = 2.0 * rc_dp * np.sin(np.pi / (2.0 * n_vis_dp))   # down<->up spacing
    live_dp = b_dp > 1e-9
    gap_dp = chord_dp - 2.0 * a_dp
    assert np.all(gap_dp[live_dp] >= -1e-12)
    assert np.all(gap_dp[live_dp] <= TUBE_BRAZE_SEAM_FRAC * chord_dp[live_dp] * (1 + 1e-9))
    # down_start_idx (J-2 layout): down tubes begin at that station (plus one
    # entry cap disk each); up tubes run the whole length and are WIDER upstream
    # (they alone fill the pitch there); a start at the last station leaves no
    # down tubes.
    _, down_j2, up_j2, _ = double_pass_tube_pieces(
        outer_xs_tw, outer_rs_tw, rs_shell, n_theta, 224, ch_height, thick,
        (0.6, 0.6, 0.6), n_theta_tube=n_theta_tube, down_start_idx=2)
    assert len(up_j2) == len(up_dp)
    assert len(down_j2) == 2 * n_vis_dp               # tubes + their entry caps
    assert min(float(t.vertices[:, 0].min()) for t in down_j2) > outer_xs_tw[1]
    _, _, _, a_j2 = _tube_geometry_profile(outer_rs_tw, rs_shell, ch_height, thick, n_vis_dp,
                                          n_local=np.r_[np.full(2, n_vis_dp),
                                                        np.full(xs_shell.size - 2, 2 * n_vis_dp)])
    assert a_j2[1] > a_dp[1] * 1.5 or b_dp[1] <= 1e-9
    _, down_none, _, _ = double_pass_tube_pieces(
        outer_xs_tw, outer_rs_tw, rs_shell, n_theta, 224, ch_height, thick,
        (0.6, 0.6, 0.6), n_theta_tube=n_theta_tube, down_start_idx=xs_shell.size - 1)
    assert down_none == []
    print("double_pass_tube_pieces interleave + contact self-check: OK")
    print("ALL TUBE_BUNDLE CHECKS OK")


if __name__ == "__main__":
    self_test()
