"""
Pure-numpy per-part mesh construction for the OpenGL 3D preview - the piece
that used to be gui/preview3d_gl.py's ~830-line `_build_mesh_data` method
(never actually touched `self`, so it's really a plain function of
`(result, heat_flux_mode)` masquerading as one). Split out into its own
module with NO OpenGL/Tk import specifically so it's headlessly testable
here for the first time (this sandbox has no $DISPLAY and neither
OpenGL/pyopengltk is installed - see CLAUDE.md's standing sandbox caveat,
which used to cover this logic too, back when it lived inside
preview3d_gl.py).

`build_mesh_data(result, heat_flux_mode)` is the orchestrator: it does the
shared prep once (profile split into body/ext, material colors, effective-
thickness arrays, far-end cover/cutoff x-position, tube-split params,
q_colors/spec helper closures), then calls one builder function per engine
part - in the same order `_build_mesh_data` always built them in - and
concatenates the returned piece lists:
  - build_chamber_and_bell_shell_pieces - body/ext shell via build_shell_mesh,
    chamber-jacket override, structural bumps (flanges/stiffening rings/exit
    lip)
  - build_injector_head_pieces - domed cap + manifold collar
  - build_far_end_cover_pieces - single_pass_upflow ring / f1_double_pass
    end-cap band
  - build_tube_hatband_pieces - hatband rings on body/extension
  - build_flange_joint_pieces - tilted flange collar + bolt ring
  - build_turbopump_pieces - turbopump assembly meshes

gui/preview3d_gl.py's EnginePreviewGLFrame calls build_mesh_data(...) in
place of its old self._build_mesh_data(...); everything genuinely OpenGL/Tk
(shaders, the GL lifecycle hooks, mouse/scroll handlers) stays there.
"""
import numpy as np

from . import preview3d_gl_core
from ..physics import (flow_network, geometry, geometry3d, hatbands, manifold, materials,
                       plumbing, turbopump_materials)

_N_THETA = 32

def _hex_to_rgb01(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return (r / 255.0, g / 255.0, b / 255.0)


def _darken_rgb01(rgb, factor=0.72):
    return tuple(c * factor for c in rgb)


# Real rendered outer-wall radius lookup at an arbitrary axial
# station - hoisted here (was previously defined further down,
# inline, only for the far-end tube-cutoff manifold ring) so the
# fuel/ox injector-feed ring placement below can reuse the exact
# same technique to sit flush on the real wall rather than a
# formula-derived radius. No logic change from the original.
def _lookup_shell(shell, x_query):
    if shell is None or shell.outer_xs.size < 2:
        return None
    order = np.argsort(shell.outer_xs)
    oxs_s, ors_s = shell.outer_xs[order], shell.outer_rs[order]
    if not (oxs_s[0] - 1e-9 <= x_query <= oxs_s[-1] + 1e-9):
        return None
    return float(np.interp(x_query, oxs_s, ors_s))

def _lookup_r(body_shell, ext_shell, has_extension, x_query, chamber_shell=None):
    # chamber_shell: the smooth Chamber-Jacket segment (injector face ->
    # throat) when that option is on - body_shell is then only the throat->
    # bell piece, so without it an injector-end query fell through to the
    # bell-end fallback below and the upper rings ballooned outward.
    r = _lookup_shell(chamber_shell, x_query)
    if r is None:
        r = _lookup_shell(body_shell, x_query)
    if r is None and has_extension:
        r = _lookup_shell(ext_shell, x_query)
    if r is None:
        # x_query landed outside both pieces' actual rendered
        # outer-wall ranges (possible from offset_profile's own
        # x-shift at an extreme slope) - fall back to the
        # nearest piece's own outer edge.
        edges = [(body_shell.outer_xs[-1], body_shell.outer_rs[-1])]
        if has_extension:
            edges.append((ext_shell.outer_xs[-1], ext_shell.outer_rs[-1]))
        _, r = min(edges, key=lambda edge: abs(edge[0] - x_query))
    return r

# Colors shared by the Shape Lab scene and the main preview so a baked run
# looks identical in both. Selected-segment tint is the Shape Lab's only.
PLUMBING_FLANGE_RGB = (0.5, 0.5, 0.52)          # same grey as the bell-joint flange
PLUMBING_SELECTED_RGB = (0.95, 0.75, 0.25)      # Shape Lab selected-segment highlight
PLUMBING_AUTO_LEG_LIGHTEN = 0.45                # auto-close legs: blend this far toward white
PORT_STUB_RGB = (0.62, 0.62, 0.65)              # turbopump inlet/discharge nozzle stubs
PORT_STUB_MAX_BODY_OD_FRACTION = 0.4            # stub radius cap vs the (render-scaled) body OD
PLUMBING_N_BEND_SAMPLES = 12


def build_plumbing_pieces(run, hook, ring_center_r_m, ring_tube_r_m, base_rgb,
                          selected_index=None, n_theta=_N_THETA, supercritical=False, port=None):
    """
    Mesh pieces for one physics/plumbing.py run rooted on `hook` (a
    manifold.py ring dict) drawn with render centreline radius
    ring_center_r_m / tube radius ring_tube_r_m: ONE swept body for the
    whole polyline (elbows via fillet_polyline with the run's per-corner
    radii), two end disks, and pipe_flange_pieces at every joint flagged
    `flange`. Shared by gui/shape_lab_geometry.py (live editing, with
    `selected_index` tinting that pipe's stations PLUMBING_SELECTED_RGB - a
    per-station color override on the single body, no extra shader work)
    and build_injector_head_pieces below (the baked run on the real engine).

    `port` (a turbopump_ports discharge dict) closes a connect_to_pump run
    onto the pump; its auto-close legs are drawn lightened toward white.

    Returns (pieces, resolved) - `resolved` is plumbing.resolve_run's dict so
    the caller also gets advisories/lengths without a second solve. An
    empty run returns ([], resolved).
    """
    resolved = plumbing.resolve_run(run, hook, ring_center_r_m, ring_tube_r_m,
                                    supercritical=supercritical, port=port)
    wp = resolved["waypoints_xyz"]
    if wp.shape[0] < 2:
        return [], resolved
    kw = dict(specular_strength=preview3d_gl_core.HARDWARE_SPECULAR_STRENGTH,
              shininess=preview3d_gl_core.HARDWARE_SHININESS)
    centerline, tangents = preview3d_gl_core.fillet_polyline(
        wp, resolved["bend_radii_eff_m"], PLUMBING_N_BEND_SAMPLES)
    normals_f, binormals_f = preview3d_gl_core.rotation_minimizing_frames(centerline, tangents)
    # Per-station bore: each pipe's own, coned through its reducers (pipe 1
    # starts at the ring's local flow bore, flush with the drawn torus).
    station_r = plumbing.centerline_radii(resolved, centerline)
    body = preview3d_gl_core._swept_tube_mesh_from_frames(
        centerline, tangents, normals_f, binormals_f, station_r, n_theta, base_rgb, **kw)
    tint_sel = selected_index is not None and 0 <= selected_index < wp.shape[0] - 1
    if tint_sel or resolved["auto_leg_indices"]:
        # Nearest-straight-segment assignment per centreline station (arc
        # samples split at roughly mid-elbow) -> tint those pipes' stations.
        nearest, _ = plumbing.nearest_segment(wp, centerline)
        colors = body.colors.reshape(n_theta, centerline.shape[0], 3).copy()
        for k in resolved["auto_leg_indices"]:
            colors[:, nearest == k, :] += PLUMBING_AUTO_LEG_LIGHTEN * (1.0 - colors[:, nearest == k, :])
        if tint_sel:
            colors[:, nearest == selected_index, :] = np.asarray(PLUMBING_SELECTED_RGB, dtype=np.float32)
        body.colors = np.ascontiguousarray(colors.reshape(-1, 3), dtype=np.float32)
    pieces = [body,
              preview3d_gl_core._tube_end_disk(centerline[0], normals_f[0], binormals_f[0],
                                               tangents[0], float(station_r[0]), n_theta, base_rgb,
                                               facing_sign=-1.0, **kw),
              preview3d_gl_core._tube_end_disk(centerline[-1], normals_f[-1], binormals_f[-1],
                                               tangents[-1], float(station_r[-1]), n_theta, base_rgb,
                                               facing_sign=1.0, **kw)]
    for joint in resolved["joint_frames"]:
        if joint["flange"]:
            fl = joint["flange_dims"]
            pieces.extend(preview3d_gl_core.pipe_flange_pieces(
                joint["pos"], joint["t"], joint["n"], joint["b"], joint["r_m"],
                fl["lip_m"], fl["width_m"], fl["bolt_count"], n_theta, PLUMBING_FLANGE_RGB, **kw))
    # The drawn centreline + bore (ring -> outward), for the flow visualization.
    resolved["render_centerline_xyz"] = centerline
    resolved["render_station_r_m"] = station_r
    return pieces, resolved


def _wall_snapped_ring_center_r(body_shell, ext_shell, has_extension, ring, chamber_shell=None):
    """
    Option A (rendering-only fix): a manifold-shaped ring dict's RENDER
    center radius, snapped flush against the ACTUAL rendered wall
    (body_shell/ext_shell.outer_xs/outer_rs) at its own axial station,
    instead of physics/manifold.py's formula-derived major_radius_m - which
    has no idea what the real wall looks like once wall thickness/regen
    jacket/tube-bundle ribs are drawn on top of the nominal chamber/local-
    bore radius it was computed from, and so can visibly float off it.
    major_radius_m itself is untouched and still drives the physics mass/
    hoop-stress result; this only changes where the ring gets DRAWN.

    Option B (not done): fold the real per-station wall profile into
    physics/manifold.py itself so major_radius_m is exact there too -
    skipped because that data (wall thickness/regen jacket/tube-bundle
    geometry) doesn't exist in the physics module today (it only receives a
    bare chamber_dia_m/local_bore_dia_m scalar), and threading it through
    would blur the physics/rendering boundary this file otherwise keeps
    clean. Revisit if the MASS number itself (not just the render position)
    ever needs to reflect the real wall.

    Shared by the fuel/ox injector-feed rings and the regen-jacket
    coolant-supply ring(s) - same fix, same reasoning, previously
    duplicated inline for the injector-feed rings only.
    """
    return (_ring_inner_edge_r(body_shell, ext_shell, has_extension, ring, chamber_shell)
            + ring["outer_radius_m"])


def _ring_inner_edge_r(body_shell, ext_shell, has_extension, ring, chamber_shell=None):
    """Render radius of the ring's INNER edge - flush on the drawn wall plus
    MANIFOLD_RING_WALL_CLEARANCE_M (Option A, see _wall_snapped_ring_center_r),
    or the physics ring's own inner edge when no wall is found there. A
    split/tapered ring (physics/manifold.py) keeps this edge fixed all the way
    round, so its centreline follows the taper."""
    r_wall = _lookup_r(body_shell, ext_shell, has_extension, ring["attach_axial_station_m"],
                       chamber_shell=chamber_shell)
    if r_wall is None:
        return ring["major_radius_m"] - ring["outer_radius_m"]
    return r_wall + preview3d_gl_core.MANIFOLD_RING_WALL_CLEARANCE_M


def ring_local_render(ring, inner_edge_r_m, angle_deg):
    """(centreline radius, tube radius) of a drawn - possibly tapered - ring at
    absolute angle `angle_deg` (0 = +y, attach_angular_position_deg's
    convention): what a plumbing run rooted there must start from."""
    tube = manifold.ring_outer_radius_at(ring, angle_deg)
    return inner_edge_r_m + tube, tube


def ring_render_arrays(ring, inner_edge_r_m, n_theta_main):
    """Per-u (centre, tube) radius arrays for manifold_ring_mesh at
    u = linspace(0, 2pi, n_theta_main) - u=0 is +y, the same angle convention
    as the ring's attach_angular_position_deg, so the fat end lands on the
    inlet. Periodic, so the last station repeats the first (the mesh seam)."""
    u_deg = np.degrees(np.linspace(0.0, 2.0 * np.pi, n_theta_main))
    tube = np.array([manifold.ring_outer_radius_at(ring, a) for a in u_deg])
    return inner_edge_r_m + tube, tube


def ring_mesh_for(ring, inner_edge_r_m, rgb):
    """The drawn manifold torus for a physics ring dict (tapered when the ring
    is a split header, constant for a turnaround collar)."""
    ctr, tube = ring_render_arrays(ring, inner_edge_r_m, _N_THETA)
    return preview3d_gl_core.manifold_ring_mesh(
        ring["attach_axial_station_m"], ctr, tube, _N_THETA, 12, rgb,
        specular_strength=preview3d_gl_core.HARDWARE_SPECULAR_STRENGTH,
        shininess=preview3d_gl_core.HARDWARE_SHININESS)


def ring_render_inner_edge_r(result, ring):
    """_ring_inner_edge_r from a bare compute() result (see
    ring_render_center_r for the cost note)."""
    _, ctx = build_mesh_data(result, False, return_context=True)
    return _ring_inner_edge_r(ctx["body_shell"], ctx["ext_shell"], ctx["has_extension"], ring,
                              ctx["chamber_shell"])


def ring_render_center_r(result, ring):
    """Wall-snapped render centreline radius for a manifold ring dict, from a
    bare compute() result - rebuilds the body/ext shells the same way
    build_mesh_data does so gui/shape_lab_geometry.py roots its run exactly
    where the main preview draws the ring. Costs one build_shell_mesh pass
    per call (a full build_mesh_data pass - the shells need every bit of its
    prep); the Lab calls it once per session, not per redraw."""
    _, ctx = build_mesh_data(result, False, return_context=True)
    return _wall_snapped_ring_center_r(ctx["body_shell"], ctx["ext_shell"],
                                       ctx["has_extension"], ring, ctx["chamber_shell"])


def build_chamber_and_bell_shell_pieces(body_xs, body_rs, ext_xs, ext_rs, has_extension,
                                         has_real_joint, chamber_rgb, bell_rgb, chamber_mat,
                                         bell_mat, construction, n_channels_physical,
                                         land_fraction, regen_circuit_style, throat_dia_m,
                                         x_split, body_thickness_eff, ext_thickness_eff,
                                         body_channel_heights, ext_channel_heights,
                                         chamber_tube_jacket, tube_split_x_for_piece,
                                         n_channels_for_piece, x_tube_end, q_colors, spec_for,
                                         cooling_result, down_tube_start_x_m=None):
    """body/ext shell via build_shell_mesh, chamber-jacket override, structural
    bumps (flanges/stiffening rings/exit lip). Returns (pieces, body_shell,
    ext_shell, flange_height_m, chamber_shell) - chamber_shell is the smooth
    Chamber-Jacket segment (None when that option is off), needed only for
    wall lookups at the injector end; body_shell/ext_shell (ext_shell is None if
    has_extension is False) and flange_height_m (None unless has_real_joint) are
    needed by later builders (injector-head/far-end-cover radius lookups, the
    flange-joint collar)."""
    pieces = []
    ext_shell = None
    chamber_shell = None
    flange_height_m = None
    # Structural detail (flanges/stiffening rings/exit lip) - built from
    # real design quantities already in the result (the material-
    # transition point, throat diameter, resolved nozzle cooling method,
    # the per-station EFFECTIVE thickness arrays above, so a flange/ring/
    # lip stays proportionate to whatever's actually rendered there, not a
    # stale bare-structural number), not arbitrary constants. Each is an
    # axial-only radius bump (physics/geometry3d.axial_bump_delta_r)
    # summed into the outer wall before any tube/channel modulation - see
    # gui/preview3d_gl_core.build_shell_mesh's `structural_bumps`.
    body_bumps, ext_bumps = [], []
    if has_extension and throat_dia_m > 0:
        joint_thickness = max(float(body_thickness_eff[-1]) if len(body_thickness_eff) else 0.0,
                               float(ext_thickness_eff[0]) if len(ext_thickness_eff) else 0.0,
                               1e-4)
        # axial_bump_delta_r only ever evaluates at the profile's OWN
        # discrete x-samples (it doesn't resample the contour) - a bump
        # half-width narrower than half the local sample spacing can fall
        # entirely between two stations and register at NONE of them,
        # silently vanishing. A local wall-thickness-based half-width
        # (mm-scale) can be far smaller than this contour's station
        # spacing (cm-scale) - found via direct testing this session,
        # affecting the stiffening rings below and the hatbands. Floor
        # every ring/band half-width at a multiple of the extension's own
        # median station spacing so it always spans multiple samples
        # regardless of how thin the local wall is.
        ext_local_dx = float(np.median(np.diff(ext_xs))) if len(ext_xs) > 1 else 0.0
        if has_real_joint:
            # Sized off throat diameter, not local wall thickness - the
            # same fix already applied to hatbands/bolt heads: a
            # correctly-thin nozzle-extension skirt (sub-mm once wall
            # thickness uses local static pressure past the throat) would
            # make a thickness-relative flange imperceptible. The actual
            # flange mesh itself is built later, once body_shell/ext_shell
            # exist (it needs the real rendered outer wall's local slope,
            # not just these two sizing numbers) - see
            # preview3d_gl_core.tilted_flange_mesh below. flange_half_width
            # itself is computed earlier (before the tube hard-cutoff x) -
            # only the height needs computing here.
            width_override_m = float(cooling_result.get("flange_width_m") or 0.0)
            flange_height_m = (width_override_m if width_override_m > 0
                                else preview3d_gl_core.FLANGE_HEIGHT_THROAT_DIA_MULT * throat_dia_m)

        if cooling_result.get("nozzle_cooling_method") == "radiative" and len(ext_xs) >= 2:
            skirt_length = float(ext_xs[-1] - ext_xs[0])
            spacing = preview3d_gl_core.RING_SPACING_THROAT_DIA_MULT * throat_dia_m
            n_rings = max(2, round(skirt_length / spacing)) if spacing > 0 else 0
            for k in range(1, n_rings):
                cx = float(ext_xs[0] + k * skirt_length / n_rings)
                t_local = (float(np.interp(cx, ext_xs, ext_thickness_eff))
                           if len(ext_thickness_eff) else joint_thickness)
                ext_bumps.append(dict(
                    center_x_m=cx,
                    half_width_m=max(preview3d_gl_core.RING_HALF_WIDTH_FACTOR * t_local,
                                      2.0 * ext_local_dx),
                    height_m=preview3d_gl_core.RING_HEIGHT_FACTOR * t_local,
                    shape="smooth"))


    if chamber_tube_jacket and construction == "tube_wall" and len(body_rs) >= 3:
        # Split the body piece at the THROAT (its own local minimum
        # radius - not the material-transition point) into a jacketed
        # combustion-chamber segment and a normally-rendered throat-to-
        # bell segment, sharing one boundary station (no x-gap). Both
        # segments slice the SAME underlying per-station arrays, so their
        # outer envelopes land on the exact same radius at that shared
        # station - any visual step there is only ever the tube layer
        # (backing recessed, crests still reaching the envelope) meeting
        # the smooth jacket, not a genuine geometry mismatch.
        throat_idx = int(np.argmin(body_rs))
        throat_idx = max(1, min(throat_idx, len(body_rs) - 2))
        sl_chamber, sl_throat_bell = slice(0, throat_idx + 1), slice(throat_idx, None)
        chamber_colors = q_colors(body_xs[sl_chamber])
        chamber_spec, chamber_shin = spec_for(chamber_colors, chamber_mat)
        chamber_shell = preview3d_gl_core.build_shell_mesh(
            body_xs[sl_chamber], body_rs[sl_chamber], body_thickness_eff[sl_chamber],
            _N_THETA, chamber_rgb, colors_per_station=chamber_colors,
            construction="coax_shell", channel_height_profile_m=body_channel_heights[sl_chamber]
            if body_channel_heights is not None else None,
            cap_start=True, cap_end=False,
            specular_strength=chamber_spec, shininess=chamber_shin)
        pieces.extend(chamber_shell.pieces)
        body_colors = q_colors(body_xs[sl_throat_bell])
        body_spec, body_shin = spec_for(body_colors, chamber_mat)
        body_shell = preview3d_gl_core.build_shell_mesh(
            body_xs[sl_throat_bell], body_rs[sl_throat_bell], body_thickness_eff[sl_throat_bell],
            _N_THETA, chamber_rgb, colors_per_station=body_colors,
            construction=construction, channel_height_profile_m=body_channel_heights[sl_throat_bell]
            if body_channel_heights is not None else None,
            n_channels_physical=n_channels_for_piece(body_rs[sl_throat_bell]),
            land_fraction=land_fraction, structural_bumps=body_bumps,
            cap_start=False, cap_end=not has_extension,
            tube_split_x_m=tube_split_x_for_piece(body_xs[sl_throat_bell], body_rs[sl_throat_bell]),
            regen_circuit_style=regen_circuit_style, tube_cutoff_x_m=x_tube_end,
            down_tube_start_x_m=down_tube_start_x_m,
            specular_strength=body_spec, shininess=body_shin)
        pieces.extend(body_shell.pieces)
    else:
        body_colors = q_colors(body_xs)
        body_spec, body_shin = spec_for(body_colors, chamber_mat)
        body_shell = preview3d_gl_core.build_shell_mesh(
            body_xs, body_rs, body_thickness_eff, _N_THETA, chamber_rgb,
            colors_per_station=body_colors, construction=construction,
            channel_height_profile_m=body_channel_heights,
            n_channels_physical=n_channels_for_piece(body_rs), land_fraction=land_fraction,
            structural_bumps=body_bumps, cap_start=True, cap_end=not has_extension,
            tube_split_x_m=tube_split_x_for_piece(body_xs, body_rs),
            regen_circuit_style=regen_circuit_style, tube_cutoff_x_m=x_tube_end,
            down_tube_start_x_m=down_tube_start_x_m,
            specular_strength=body_spec, shininess=body_shin)
        pieces.extend(body_shell.pieces)
    if has_extension:
        ext_colors = q_colors(ext_xs)
        ext_spec, ext_shin = spec_for(ext_colors, bell_mat)
        ext_shell = preview3d_gl_core.build_shell_mesh(
            ext_xs, ext_rs, ext_thickness_eff, _N_THETA, bell_rgb,
            colors_per_station=ext_colors, construction=construction,
            channel_height_profile_m=ext_channel_heights,
            n_channels_physical=n_channels_for_piece(ext_rs), land_fraction=land_fraction,
            structural_bumps=ext_bumps, cap_start=False, cap_end=True,
            tube_split_x_m=tube_split_x_for_piece(ext_xs, ext_rs),
            regen_circuit_style=regen_circuit_style, tube_cutoff_x_m=x_tube_end,
            down_tube_start_x_m=down_tube_start_x_m,
            specular_strength=ext_spec, shininess=ext_shin)
        pieces.extend(ext_shell.pieces)

        # Bridge the body/extension outer-wall gap: the two pieces' outer
        # walls are built entirely independently and can land at very
        # different radii at the shared joint (chamber vs. bell-material
        # wall thickness can differ by 1-2 orders of magnitude, especially
        # since the extension now uses the LOCAL isentropic pressure) - a
        # short connecting frustum between the two pieces' ACTUAL rendered
        # outer-wall edges (ShellMesh.outer_xs/outer_rs) closes that gap
        # exactly, regardless of how different the two thicknesses are.
        # The flange bump above only decorates each side's OWN profile;
        # it can't reconcile two already-different base radii on its own.
        bx = np.array([body_shell.outer_xs[-1], ext_shell.outer_xs[0]])
        br = np.array([body_shell.outer_rs[-1], ext_shell.outer_rs[0]])
        order = np.argsort(bx)  # each side offsets x along its own local
                                 # normal - guard against the two landing
                                 # in reversed order at the joint
        bridge_rgb = tuple((c1 + c2) / 2.0 for c1, c2 in zip(chamber_rgb, bell_rgb))
        pieces.append(preview3d_gl_core.revolve_to_buffers(
            bx[order], br[order], _N_THETA, bridge_rgb,
            specular_strength=chamber_mat.specular_strength, shininess=chamber_mat.shininess))
    return pieces, body_shell, ext_shell, flange_height_m, chamber_shell


def build_injector_head_pieces(body_rs, result, chamber_rgb, construction, n_channels_physical,
                                body_shell, ext_shell, has_extension,
                                duct_bend_radius_mult=None, return_band_drawn=False,
                                chamber_shell=None, flow_anchors=None):
    """domed cap + manifold collar. `return_band_drawn`: the f1_double_pass
    end-cap band (build_far_end_cover_pieces) is being drawn and stands in as
    the fuel RETURN manifold, so the jacket_return torus itself is skipped.
    `flow_anchors`: optional dict filled with where rings/feed lines were
    DRAWN ({"rings": {host: (ring, inner_edge_r)}, "feed_lines": {host:
    (centerline, station_r)}}) for build_flow_pieces."""
    pieces = []
    # Injector-head hardware (domed cap + manifold collar), same shapes as
    # draw_3d_preview - flat material colors always, heat-flux data
    # doesn't apply to hardware. Feed stubs/baffle blades/acoustic-cavity
    # markers (thin lines/points in the matplotlib version) aren't
    # reproduced here - this minimal GL pipeline only draws triangulated
    # surfaces; a follow-on could add a GL_LINES/GL_POINTS path for them.
    chamber_head_r = float(body_rs[0]) if len(body_rs) else float(result["profile_rs_m"].max())
    if chamber_head_r > 0:
        dome_depth = 0.42 * chamber_head_r
        t = np.linspace(0.0, np.pi / 2.0, 16)
        dome_xs = -dome_depth * np.sin(t)
        dome_rs = chamber_head_r * np.cos(t)
        pieces.append(preview3d_gl_core.revolve_to_buffers(
            dome_xs, dome_rs, _N_THETA, _darken_rgb01(chamber_rgb, 0.6),
            specular_strength=preview3d_gl_core.HARDWARE_SPECULAR_STRENGTH,
            shininess=preview3d_gl_core.HARDWARE_SHININESS))

        collar_len = max(0.02 * chamber_head_r, 0.06 * dome_depth)
        if construction == "tube_wall" and n_channels_physical > 0:
            # A real coolant-manifold ring where the tube bundle's inlet/
            # outlet collects, not a flat-sided collar - reuses
            # collar_len/chamber_head_r*1.10 exactly as the old collar
            # did (same axial span, same centerline radius).
            pieces.append(preview3d_gl_core.manifold_ring_mesh(
                0.0, chamber_head_r * 1.10, collar_len, _N_THETA, 12, (0.56, 0.56, 0.56),
                specular_strength=preview3d_gl_core.HARDWARE_SPECULAR_STRENGTH,
                shininess=preview3d_gl_core.HARDWARE_SHININESS))
        else:
            Xc, Yc, Zc = geometry3d.capped_cylinder(-collar_len, collar_len,
                                                      chamber_head_r * 1.10, n_theta=_N_THETA)
            pieces.append(preview3d_gl_core.mesh_from_grid(
                Xc, Yc, Zc, (0.56, 0.56, 0.56),
                specular_strength=preview3d_gl_core.HARDWARE_SPECULAR_STRENGTH,
                shininess=preview3d_gl_core.HARDWARE_SHININESS))

        # Propellant intake manifold rings (physics/manifold.py) - real,
        # independently-sized fuel/ox tori, distinct from BOTH the collar
        # above (cosmetic injector-head hardware) and the tube-bundle/
        # far-end coolant-manifold tori below (regen-coolant hardware,
        # unrelated). Sized entirely from the physics result, no
        # recomputation here. Placed by physics/manifold.py's own
        # concentric-stacking formula so the two rings never overlap
        # each other or (by construction, via MANIFOLD_RING_CLEARANCE_M)
        # this collar - NOT visually confirmed in this sandbox (no
        # $DISPLAY/PyOpenGL); check for overlap on a real run, especially
        # on small engines where the absolute clearance margins could
        # read as disproportionate.
        # Render centreline radius + tube radius + base color per ring, keyed
        # by physics/plumbing.py's host names, so baked plumbing runs (below)
        # emerge from the ring exactly where it is DRAWN, not where the
        # physics nominally puts it.
        _ring_render = {}
        _feed_lines = {}
        # LH2 fuel: SP-8087's liquid-velocity advisory doesn't apply to its pipes.
        _lh2_fuel = result.get("inputs", {}).get("propellant_pair") == "LOX/LH2"
        manifold_result = result.get("manifold_result")
        if manifold_result:
            _MANIFOLD_RGB = {"fuel": (0.55, 0.62, 0.75), "ox": (0.70, 0.60, 0.55)}
            for _prop_key in ("fuel", "ox"):
                _m = manifold_result[_prop_key]
                # Option A wall-snap (see _wall_snapped_ring_center_r) -
                # render position only, physics major_radius_m untouched.
                _edge = _ring_inner_edge_r(body_shell, ext_shell, has_extension, _m, chamber_shell)
                _ring_render[_prop_key] = (_m, _edge, _MANIFOLD_RGB[_prop_key])
                pieces.append(ring_mesh_for(_m, _edge, _MANIFOLD_RGB[_prop_key]))

        # Regen-cooling JACKET's own coolant-supply ring(s) (physics/
        # manifold.size_jacket_manifolds) - distinct from the injector-
        # feed rings just above (fuel/ox, gray-ish tints). Olive tint so
        # the two kinds of ring read as different hardware. Not visually
        # confirmed in this sandbox - check on a real run whether the
        # forward split-topology jacket_inlet ring clears the ox ring
        # without looking cramped, and whether the aft ring lines up
        # sensibly with the tube-cutoff hardware built just below (which
        # computes its own x independently via x_tube_cutoff - a small,
        # unverified risk of the two disagreeing slightly on a coarsely
        # sampled contour, or by the flange-clearance shift when a real
        # nozzle-extension joint exists). The aft ring (split topology's
        # jacket_return) is a small turnaround COLLAR since 2026-09-22 -
        # bore from the local passage height (manifold.TURNAROUND_BORE_*),
        # not a header-sized torus; it's deliberately left at its physics x
        # (not moved onto x_tube_cutoff) so plumbing runs rooted on it, here
        # and in the Shape Lab, still start exactly on the drawn ring.
        #
        # jacket_inlet is treated as THE "main fuel inlet" for the purposes
        # of the demo duct below - for single_pass_countercurrent (the only
        # topology with just one ring) it carries the FULL fuel mdot and
        # sits at the bell/nozzle-extension end, genuinely the point where
        # fuel first enters the engine from the outside feed system, unlike
        # the injector-feed rings above (which are the last, POST-jacket
        # header right before the orifices). Known simplification: for
        # f1_split_reverse_flow, jacket_inlet there only carries the
        # down-leg (bypassed fuel still physically arrives via the fuel
        # injector-feed ring above) - attaching the duct to it anyway isn't
        # perfectly physically accurate for that topology, but it's still
        # the most sensible single "main inlet" candidate to draw; revisit
        # if that topology's duct routing ever needs to be more precise.
        jacket_manifold_result = result.get("jacket_manifold_result")
        if jacket_manifold_result:
            _JACKET_RGB = (0.56, 0.56, 0.20)
            for _jkey in ("jacket_inlet", "jacket_return"):
                _jm = jacket_manifold_result.get(_jkey)
                if _jm:
                    _jedge = _ring_inner_edge_r(body_shell, ext_shell, has_extension, _jm, chamber_shell)
                    _ring_render[_jkey] = (_jm, _jedge, _JACKET_RGB)
                    # Under f1_split_reverse_flow the gray end-cap band IS the
                    # drawn return manifold whenever it exists (user direction,
                    # 2026-09-22) - skip the olive torus there. _ring_render
                    # still registers it so a baked jacket_return plumbing run
                    # keeps its root (right at the band's wall station).
                    if _jkey == "jacket_return" and return_band_drawn:
                        continue
                    pieces.append(ring_mesh_for(_jm, _jedge, _JACKET_RGB))

            # Fuel main-inlet duct - a short stub with one bend off the
            # jacket_inlet ring's hook point (plumbing.default_run_for_host's
            # path). Only the FALLBACK for a design with no baked run on
            # jacket_inlet - a baked run (design.plumbing_runs, edited in the
            # Shape Lab) replaces it below; both go through the same
            # build_plumbing_pieces the Lab uses. NOT visually confirmed in
            # this sandbox (no $DISPLAY/PyOpenGL).
            _runs = result.get("inputs", {}).get("plumbing_runs") or []
            _has_inlet_run = any(len((r or {}).get("pipes") or []) > 0
                                 for r in plumbing.runs_for_host(_runs, "jacket_inlet"))
            if jacket_manifold_result.get("jacket_inlet") and not _has_inlet_run:
                # Drawn through the same build_plumbing_pieces as a baked run
                # (default_run_for_host reproduces the legacy stub's path), so
                # it also leaves the ring at the ring's own inlet bore and
                # cones out to the full-flow feed bore.
                _jhk, _jedge_in, _ = _ring_render["jacket_inlet"]
                _jang = float(_jhk.get("attach_angular_position_deg", 0.0))
                _jrr, _jrt = ring_local_render(_jhk, _jedge_in, _jang)
                _legacy_run = plumbing.default_run_for_host(
                    _jhk, _jrt, "jacket_inlet", bend_radius_dia_mult=duct_bend_radius_mult)
                _lp, _lres = build_plumbing_pieces(_legacy_run, _jhk, _jrr, _jrt, _JACKET_RGB,
                                                   supercritical=_lh2_fuel)
                pieces.extend(_lp)
                if _lp:
                    _feed_lines["jacket_inlet"] = (_lres["render_centerline_xyz"],
                                                   _lres["render_station_r_m"])

        # Baked procedural plumbing runs (physics/plumbing.py) on whichever
        # ring each is rooted on - a run whose host ring doesn't exist for
        # this design (e.g. jacket_return on a single-pass topology) is
        # simply skipped here; design.py's compute() raises the advisory.
        for _run in result.get("inputs", {}).get("plumbing_runs") or []:
            _host = (_run or {}).get("host")
            if _host in _ring_render:
                _hk, _edge, _rgb = _ring_render[_host]
                _rr, _rt = ring_local_render(_hk, _edge, plumbing.run_from_dict(_run).attach_angle_deg)
                _pp, _pres = build_plumbing_pieces(_run, _hk, _rr, _rt, _rgb,
                                                   supercritical=_lh2_fuel and _host != "ox",
                                                   port=run_port_for_result(result, _run))
                pieces.extend(_pp)
                if _pp and _host not in _feed_lines:
                    _feed_lines[_host] = (_pres["render_centerline_xyz"],
                                          _pres["render_station_r_m"])
    if flow_anchors is not None and chamber_head_r > 0:
        flow_anchors["rings"] = {k: (v[0], v[1]) for k, v in _ring_render.items()}
        flow_anchors["feed_lines"] = _feed_lines
    return pieces


def build_far_end_cover_pieces(construction, n_channels_physical, x_tube_cutoff,
                                regen_circuit_style, throat_dia_m, body_shell, ext_shell,
                                has_extension):
    """single_pass_upflow ring / f1_double_pass end-cap band."""
    pieces = []
    # Far-end return/turnaround hardware, at x_tube_cutoff (computed
    # earlier, before body_shell/ext_shell existed - see there, including
    # the shift clear of a real flange joint that now applies to EITHER
    # style). The discrete tube geometry has already been HARD-cut off at
    # that same x (channel_heights, above), so the pipes terminate tucked
    # under/into whichever of these gets built:
    #  - "single_pass_upflow": the small manifold-ring torus.
    #  - "f1_double_pass": a solid end-cap band (built the same way as
    #    tube_hatbands: a short frustum following the local crest at
    #    each edge) covering the sharp edge where the tubes cut off.
    if construction == "tube_wall" and n_channels_physical > 0 and x_tube_cutoff is not None:
        if regen_circuit_style == "single_pass_upflow":
            manifold_tube_r = preview3d_gl_core.MANIFOLD_TUBE_R_THROAT_DIA_MULT * throat_dia_m
            r_local = _lookup_r(body_shell, ext_shell, has_extension, x_tube_cutoff)
            pieces.append(preview3d_gl_core.manifold_ring_mesh(
                x_tube_cutoff, r_local + manifold_tube_r, manifold_tube_r,
                _N_THETA, 12, (0.56, 0.56, 0.56),
                specular_strength=preview3d_gl_core.HARDWARE_SPECULAR_STRENGTH,
                shininess=preview3d_gl_core.HARDWARE_SHININESS))
        else:
            # Double-pass (F-1 or J-2) end band - drawn whether or not a
            # separate nozzle extension exists (the combined profile below
            # is just the body when it doesn't).
            half_width = preview3d_gl_core.TUBE_END_CAP_HALF_WIDTH_THROAT_DIA_MULT * throat_dia_m
            band_x_lo, band_x_hi = x_tube_cutoff - half_width, x_tube_cutoff + half_width

            combined_xs_all = [body_shell.outer_xs]
            combined_rs_all = [body_shell.outer_rs]
            if has_extension:
                combined_xs_all.append(ext_shell.outer_xs)
                combined_rs_all.append(ext_shell.outer_rs)
            combined_xs_all = np.concatenate(combined_xs_all)
            combined_rs_all = np.concatenate(combined_rs_all)
            order_all = np.argsort(combined_xs_all)
            combined_xs_all = combined_xs_all[order_all]
            combined_rs_all = combined_rs_all[order_all]

            band_x_lo = max(float(combined_xs_all[0]), band_x_lo)
            band_x_hi = min(float(combined_xs_all[-1]), band_x_hi)
            if band_x_hi > band_x_lo:
                band_height = preview3d_gl_core.HATBAND_HEIGHT_THROAT_DIA_MULT * throat_dia_m
                band_clearance = preview3d_gl_core.HATBAND_CLEARANCE_THROAT_DIA_MULT * throat_dia_m
                r_lo = (float(np.interp(band_x_lo, combined_xs_all, combined_rs_all))
                        + band_clearance + band_height)
                r_hi = (float(np.interp(band_x_hi, combined_xs_all, combined_rs_all))
                        + band_clearance + band_height)
                pieces.append(preview3d_gl_core.revolve_to_buffers(
                    np.array([band_x_lo, band_x_hi]), np.array([r_lo, r_hi]),
                    _N_THETA, (0.56, 0.56, 0.56),
                    specular_strength=preview3d_gl_core.HARDWARE_SPECULAR_STRENGTH,
                    shininess=preview3d_gl_core.HARDWARE_SHININESS))
    return pieces


def _crest_envelope(body_shell, ext_shell, has_extension):
    """Sorted (xs, rs) of the rendered outer envelope (tube crests where tubes are
    drawn) across the body and, if present, the extension."""
    xs_all, rs_all = [body_shell.outer_xs], [body_shell.outer_rs]
    if has_extension and ext_shell is not None and ext_shell.outer_xs.size >= 2:
        xs_all.append(ext_shell.outer_xs)
        rs_all.append(ext_shell.outer_rs)
    xs_all, rs_all = np.concatenate(xs_all), np.concatenate(rs_all)
    order = np.argsort(xs_all, kind="stable")
    return xs_all[order], rs_all[order]


def _on_crest(env_xs, env_rs, x_center, us, vs):
    """Map section points (u axial, v radial-out) onto the crest envelope at
    x_center: each point's base is the crest point u along the local tangent, then
    it is pushed v along the local outward normal - so a band's underside hugs the
    real (curved) crest across its whole width and the section tilts with the bell."""
    h = max(1e-4, 0.002 * float(env_xs[-1] - env_xs[0]))
    drdx = (float(np.interp(x_center + h, env_xs, env_rs))
            - float(np.interp(x_center - h, env_xs, env_rs))) / (2.0 * h)
    norm = np.hypot(1.0, drdx)
    tx, tr = 1.0 / norm, drdx / norm
    nx, nr = -drdx / norm, 1.0 / norm
    us, vs = np.asarray(us, float), np.asarray(vs, float)
    bx = x_center + us * tx
    br = np.interp(bx, env_xs, env_rs)
    return bx + vs * nx, br + vs * nr


def build_tube_hatband_pieces(cooling_result, construction, n_channels_physical, throat_dia_m,
                               body_shell, ext_shell, has_extension):
    """Structural hatbands (physics/hatbands.py via design.compute()'s
    cooling_result["hatbands"]): each band drawn as its SIZED cross-section (flat /
    tee / hat / channel / box polygon, hatbands.section_outline) revolved round the
    engine, sitting on the tube crests across a braze gap and tilted with the local
    bell - plus a smooth sleeve over the continuous-shell region between the throat
    and the first band (SP-8120: shell near the throat, bands downstream). Falls
    back to the legacy throat-diameter-scaled rings for a result without sizing
    data (an older caller)."""
    if not (cooling_result.get("tube_hatbands") and construction == "tube_wall"
            and n_channels_physical > 0 and throat_dia_m > 0):
        return []
    hb = cooling_result.get("hatbands")
    if not isinstance(hb, dict):
        return _legacy_tube_hatband_pieces(cooling_result, construction, n_channels_physical,
                                           throat_dia_m, body_shell, ext_shell, has_extension)
    if body_shell is None or body_shell.outer_xs.size < 2:
        return []
    env_xs, env_rs = _crest_envelope(body_shell, ext_shell, has_extension)
    kw = dict(specular_strength=preview3d_gl_core.HARDWARE_SPECULAR_STRENGTH,
              shininess=preview3d_gl_core.HARDWARE_SHININESS)
    pieces = []
    gap = hatbands.BAND_BRAZE_GAP_M
    for band in hb.get("bands") or []:
        outline = hatbands.section_outline(band["shape"], band["width_m"], band["gauge_m"],
                                           band["height_m"])
        us = [p[0] for p in outline]
        vs = [gap + p[1] for p in outline]
        px, pr = _on_crest(env_xs, env_rs, float(band["x_m"]), us, vs)
        pieces.append(preview3d_gl_core.revolve_closed_section(
            px, pr, _N_THETA, (0.35, 0.35, 0.37), **kw))

    x_s0, x_s1 = hb.get("shell_start_x_m"), hb.get("shell_end_x_m")
    if x_s0 is not None and x_s1 is not None and x_s1 - x_s0 > 1e-3:
        x_s0 = max(float(x_s0), float(env_xs[0]))
        x_s1 = min(float(x_s1), float(env_xs[-1]))
        if x_s1 > x_s0:
            t_sleeve = preview3d_gl_core.HATBAND_SHELL_SLEEVE_THROAT_DIA_MULT * throat_dia_m
            xb = np.linspace(x_s0, x_s1, 24)
            bot_x, bot_r = [], []
            top_x, top_r = [], []
            for x in xb:
                bx, br = _on_crest(env_xs, env_rs, x, [0.0, 0.0], [gap, gap + t_sleeve])
                bot_x.append(bx[0]); bot_r.append(br[0])
                top_x.append(bx[1]); top_r.append(br[1])
            pieces.append(preview3d_gl_core.revolve_closed_section(
                np.r_[bot_x, top_x[::-1]], np.r_[bot_r, top_r[::-1]], _N_THETA,
                (0.45, 0.45, 0.47), **kw))
    return pieces


def _legacy_tube_hatband_pieces(cooling_result, construction, n_channels_physical, throat_dia_m,
                                body_shell, ext_shell, has_extension):
    """Pre-2026-09-23 cosmetic hatband rings (throat-diameter spacing/size), kept
    only for results that carry no cooling_result["hatbands"] sizing."""
    pieces = []
    # Tube hatbands: discrete horizontal (circumferential) bands wrapped
    # around the tube bundle at intervals, for structural stability -
    # matches real tube-wall engines (e.g. F-1) whose hatbands wrap the
    # thrust CHAMBER itself, not a separate bolted-on nozzle extension -
    # so the body is the default/primary host, with the extension only
    # included when tube_hatbands_on_extension is also on. Built as
    # SEPARATE ring pieces sitting visibly PROUD of the tube crests (not
    # baked into the same offset-profile envelope the tubes are computed
    # from, and not sized off local wall thickness, which can be a
    # fraction of a mm on a thin skirt and was previously imperceptible)
    # - sized off throat diameter instead, so they're always visible
    # regardless of how thin the local wall is.
    if (cooling_result.get("tube_hatbands") and construction == "tube_wall"
            and n_channels_physical > 0 and throat_dia_m > 0):
        # Host pieces in axial order: the body's own tube-wall segment,
        # then - only if the extension toggle is on - the nozzle
        # extension. The jacketed chamber segment (chamber_shell, when
        # chamber_tube_jacket is on) is deliberately EXCLUDED - hatbands
        # reinforce the tube bundle itself, and a jacketed chamber has no
        # tubes showing to begin with; excluding it here also keeps it
        # out of the span used for both auto-spacing and the manual
        # count below, so neither factors in the jacketed length. Each
        # ShellMesh's outer_xs/outer_rs is its ACTUAL rendered outer
        # envelope (tube crest where tubes are modulated) - so this
        # generalizes the crest lookup across pieces with no special-
        # casing.
        host_shells = [body_shell]
        if cooling_result.get("tube_hatbands_on_extension") and has_extension:
            host_shells.append(ext_shell)
        host_shells = [s for s in host_shells if s.outer_xs.size >= 2]

        if host_shells:
            combined_xs, combined_rs = [], []
            for s in host_shells:
                order = np.argsort(s.outer_xs)
                combined_xs.append(s.outer_xs[order])
                combined_rs.append(s.outer_rs[order])
            combined_xs = np.concatenate(combined_xs)
            combined_rs = np.concatenate(combined_rs)

            band_x0, band_x1 = float(combined_xs[0]), float(combined_xs[-1])
            band_span = band_x1 - band_x0
            count_override = int(cooling_result.get("tube_hatband_count") or 0)
            if count_override > 0:
                # range(1, n_bands) below places exactly n_bands - 1
                # bands, so +1 here yields exactly count_override of them.
                n_bands = count_override + 1
            else:
                band_spacing = preview3d_gl_core.HATBAND_SPACING_THROAT_DIA_MULT * throat_dia_m
                n_bands = (max(2, round(band_span / band_spacing))
                           if band_spacing > 0 and band_span > 0 else 0)

            width_override_m = float(cooling_result.get("tube_hatband_width_m") or 0.0)
            band_half_width = (width_override_m / 2.0 if width_override_m > 0
                                else preview3d_gl_core.HATBAND_HALF_WIDTH_THROAT_DIA_MULT * throat_dia_m)
            band_height = preview3d_gl_core.HATBAND_HEIGHT_THROAT_DIA_MULT * throat_dia_m
            band_clearance = preview3d_gl_core.HATBAND_CLEARANCE_THROAT_DIA_MULT * throat_dia_m
            for k in range(1, n_bands):
                cx = band_x0 + k * band_span / n_bands
                x_lo, x_hi = cx - band_half_width, cx + band_half_width
                # combined_xs/combined_rs IS the tube crest radius at
                # every station (tube_bundle_pieces builds each tube so
                # its outward-most point always reaches exactly this
                # envelope, regardless of which clamp sizes that
                # station's tube radius). Looking this up SEPARATELY at
                # each edge (rather than once at the center and reusing
                # that radius for both edges) makes the band a short
                # frustum that follows the local bell taper, instead of
                # a flat ring perpendicular to the axis - the same way
                # every other offset surface in this file follows the
                # local wall rather than standing upright.
                r_lo = float(np.interp(x_lo, combined_xs, combined_rs)) + band_clearance + band_height
                r_hi = float(np.interp(x_hi, combined_xs, combined_rs)) + band_clearance + band_height
                # A plain open cylindrical (here: conical) strip (lateral
                # surface only, no end caps) - capped_cylinder's flat
                # disk end-caps are right for a collar tucked against
                # the dome, but wrong here: an exposed band floating on
                # the chamber/bell would show them as odd solid plates
                # reaching all the way to the axis.
                pieces.append(preview3d_gl_core.revolve_to_buffers(
                    np.array([x_lo, x_hi]), np.array([r_lo, r_hi]),
                    _N_THETA, (0.35, 0.35, 0.37),
                    specular_strength=preview3d_gl_core.HARDWARE_SPECULAR_STRENGTH,
                    shininess=preview3d_gl_core.HARDWARE_SHININESS))
    return pieces


def build_flange_joint_pieces(has_real_joint, throat_dia_m, body_shell, ext_shell, x_split,
                               flange_half_width, flange_height_m, cooling_result):
    """tilted flange collar + bolt ring."""
    pieces = []
    # Bolted-flange-joint collar + bolt heads, matching a real chamber/
    # nozzle-extension bolted joint (reference photo). Built here (not
    # above with the other structural_bumps) because the flange must sit
    # TILTED perpendicular to the local bell surface, not perpendicular
    # to the engine centerline - a plain axial_bump_delta_r bump can only
    # add pure radius at a fixed x, which is wrong for a diverging bell
    # (see preview3d_gl_core.tilted_flange_mesh's own docstring for the
    # non-monotonic-x geometry this requires). That tilt needs the local
    # surface tangent/normal, taken from the ACTUAL rendered outer wall
    # (matching how the bolts already anchor to body_shell.outer_rs
    # rather than a re-derived value) - averaged from TWO local secants,
    # one within the body piece's own last segment and one within the
    # extension's own first segment (rather than a single secant
    # spanning clear across the joint), so the estimate stays close to
    # the true LOCAL slope at x_split even where the bell curves - a
    # wide cross-joint secant lets curvature drift the estimate away
    # from the true tangent right at the joint, which visibly showed as
    # the flange's flat base sitting off the real (curved) surface.
    # Only meaningful where an actual bolted joint exists (has_real_joint
    # - a genuine material change, not just has_extension's rendering
    # split).
    if has_real_joint and throat_dia_m > 0:
        if len(body_shell.outer_xs) >= 2:
            nb_x, nb_r = preview3d_gl_core.meridian_normals(
                body_shell.outer_xs[-2:], body_shell.outer_rs[-2:])
            normal_body = (float(nb_x[-1]), float(nb_r[-1]))
        else:
            normal_body = None
        if len(ext_shell.outer_xs) >= 2:
            ne_x, ne_r = preview3d_gl_core.meridian_normals(
                ext_shell.outer_xs[:2], ext_shell.outer_rs[:2])
            normal_ext = (float(ne_x[0]), float(ne_r[0]))
        else:
            normal_ext = None
        sides = [s for s in (normal_body, normal_ext) if s is not None]
        if sides:
            n_x_avg = sum(s[0] for s in sides) / len(sides)
            n_r_avg = sum(s[1] for s in sides) / len(sides)
            norm_len = float(np.hypot(n_x_avg, n_r_avg))
            normal = (n_x_avg / norm_len, n_r_avg / norm_len)
            tangent = (normal[1], -normal[0])
            r_base = float(body_shell.outer_rs[-1])
            # Snap the flange's base edge onto the REAL rendered wall
            # (body_shell + ext_shell's own outer profile) instead of an
            # idealized straight chord between the two endpoints - a
            # straight chord between two points on a curved/kinked wall
            # generally doesn't touch it in between, leaving a gap that
            # reads as "part of the flange floating." sample_profile_segment
            # reuses the exact same piecewise-linear data the wall mesh
            # itself draws, so the base touches it exactly, for any local
            # curvature or native station spacing.
            combined_xs = np.concatenate([body_shell.outer_xs, ext_shell.outer_xs])
            combined_rs = np.concatenate([body_shell.outer_rs, ext_shell.outer_rs])
            x_lo = x_split - flange_half_width * tangent[0]
            x_hi = x_split + flange_half_width * tangent[0]
            base_xs, base_rs = preview3d_gl_core.sample_profile_segment(
                combined_xs, combined_rs, min(x_lo, x_hi), max(x_lo, x_hi))
            # The flange's own real OD polyline (same construction
            # tilted_flange_mesh uses internally) - reused below to give
            # the bolt ring an anchor point that's an ACTUAL point on the
            # flange's rendered OD surface, not an independent
            # approximation of one (that mismatch is what let a gap open
            # up between the bolt bases and the flange after the flange's
            # own base got snapped onto the real wall).
            od_xs = base_xs + flange_height_m * normal[0]
            od_rs = base_rs + flange_height_m * normal[1]
            
            flange_mesh = preview3d_gl_core.tilted_flange_mesh(
                base_xs, base_rs, normal, flange_height_m,
                _N_THETA, (0.5, 0.5, 0.52),
                specular_strength=preview3d_gl_core.HARDWARE_SPECULAR_STRENGTH,
                shininess=preview3d_gl_core.HARDWARE_SHININESS)
            if flange_mesh is not None:
                pieces.append(flange_mesh)

            # Bolts sit on the flange's CHAMBER-SIDE face - anchored at
            # od_xs[0]/od_rs[0], the actual raised corner where the
            # leading (chamber-facing) face meets the OD rim (base_xs/
            # od_xs are sorted ascending, chamber at low x, so index 0 is
            # that chamber-side end) - not the OD-rim point nearest
            # x_split (roughly the flange's middle), which was the wrong
            # face. Bolts protrude purely AXIALLY toward the chamber
            # (fixed direction (-1, 0) in (x, r) terms - x-component -1,
            # zero radial component). With n_r=0, bolt_ring_pieces' own
            # rotation collapses to the SAME (-1, 0, 0) direction for
            # every bolt regardless of theta_i - matching a real flange,
            # whose fasteners run axially through its thickness rather
            # than radiating outward or following the local surface tilt
            # (both tried and rejected in earlier rounds this session).
            # Anchored at the MIDPOINT of the leading face (between its
            # inner/root edge base_pts[0] and outer/OD edge od_pts[0]),
            # not the outer edge itself - centers the bolt ring on the
            # face instead of hugging its rim.
            bolt_tangent = (0.0, 1.0)
            bolt_normal = (-1.0, 0.0)
            bolt_x = float((base_xs[0] + od_xs[0]) / 2.0)
            flange_r = float((base_rs[0] + od_rs[0]) / 2.0)

            bolt_count_override = int(cooling_result.get("flange_bolt_count") or 0)
            if bolt_count_override > 0:
                n_bolts = max(preview3d_gl_core.BOLT_MIN_COUNT,
                               min(preview3d_gl_core.BOLT_MAX_COUNT, bolt_count_override))
            else:
                bolt_spacing = preview3d_gl_core.BOLT_SPACING_THROAT_DIA_MULT * throat_dia_m
                n_bolts = (max(preview3d_gl_core.BOLT_MIN_COUNT,
                                min(preview3d_gl_core.BOLT_MAX_COUNT,
                                    round(2.0 * np.pi * flange_r / bolt_spacing)))
                           if bolt_spacing > 0 else 0)
            if n_bolts > 0:
                bolt_radius = preview3d_gl_core.BOLT_HEAD_RADIUS_THROAT_DIA_MULT * throat_dia_m
                bolt_length = preview3d_gl_core.BOLT_HEAD_LENGTH_THROAT_DIA_MULT * throat_dia_m
                pieces.extend(preview3d_gl_core.bolt_ring_pieces(
                    bolt_x, flange_r, n_bolts, bolt_radius, bolt_length,
                    preview3d_gl_core.BOLT_N_THETA_CYL, (0.5, 0.5, 0.52),
                    specular_strength=preview3d_gl_core.HARDWARE_SPECULAR_STRENGTH,
                    shininess=preview3d_gl_core.HARDWARE_SHININESS,
                    tangent=bolt_tangent, normal=bolt_normal))
    return pieces


def run_port_for_result(result, run):
    """The turbopump discharge port a connect_to_pump run closes onto
    (result["turbopump_ports"], built by design.py), or None."""
    r = run if isinstance(run, plumbing.PlumbingRun) else plumbing.run_from_dict(run)
    if not r.connect_to_pump:
        return None
    ports = result.get("turbopump_ports") or {}
    return (ports.get(plumbing.HOST_PUMP.get(r.host, "fuel_pump")) or {}).get("discharge")


def turbopump_port_stub_pieces(result, rgb=PORT_STUB_RGB, n_theta=_N_THETA):
    """A short nozzle stub (body surface `base` -> port face `pos`) at every
    turbopump inlet/discharge port in result["turbopump_ports"]. Ports carry
    TRUE bores while the bodies are render-scaled (turbopump_sizing's 0.2-2x
    render_scale), so the drawn stub radius is capped at
    PORT_STUB_MAX_BODY_OD_FRACTION x the assembly OD - cosmetic only."""
    ports = result.get("turbopump_ports") or {}
    sizing = result.get("turbopump_sizing") or {}
    cap = PORT_STUB_MAX_BODY_OD_FRACTION * float(sizing.get("assembly_od_m", 0.0) or 0.0)
    kw = dict(specular_strength=preview3d_gl_core.HARDWARE_SPECULAR_STRENGTH,
              shininess=preview3d_gl_core.HARDWARE_SHININESS)
    pieces = []
    for pump in ports.values():
        for port in pump.values():
            r = 0.5 * float(port.get("dia_m", 0.0) or 0.0)
            if cap > 0:
                r = min(r, cap)
            pieces.extend(preview3d_gl_core.ray_mesh(port["base"], port["pos"], r, n_theta, rgb, **kw))
    return pieces


def build_turbopump_pieces(result):
    """turbopump assembly meshes + port nozzle stubs."""
    pieces = []
    sizing = result.get("turbopump_sizing")
    if sizing and sizing.get("bodies"):
        tp_mat = turbopump_materials.MATERIALS[result["inputs"]["turbopump_material_key"]]
        pump_rgb = _hex_to_rgb01(tp_mat.color_hex)
        turb_rgb = _darken_rgb01(pump_rgb)
        # Placement shared with gui/preview3d's fallback and the Shape Lab's
        # ghost turbopump - see geometry3d.turbopump_origin_xyz.
        origin = geometry3d.turbopump_origin_for_result(result)
        for kind, (Xt, Yt, Zt) in geometry3d.turbopump_assembly_meshes(sizing["bodies"], origin):
            rgb = turb_rgb if kind == "turbine" else pump_rgb
            pieces.append(preview3d_gl_core.mesh_from_grid(
                Xt, Yt, Zt, rgb,
                specular_strength=tp_mat.specular_strength, shininess=tp_mat.shininess))
        pieces.extend(turbopump_port_stub_pieces(result))

    return pieces


def _tag(pieces, role):
    """Stamp MeshBuffers.role on every piece (render-layer choice only - see
    preview3d_gl_core/render_layers.py) and hand the list back."""
    for piece in pieces:
        piece.role = role
    return pieces


# Flow visualization (cosmetic only - how the physics/flow_network.py streams
# are DRAWN; the temperatures themselves all come from that module).
FLOW_JACKET_STREAMS = 16          # visual coolant streams round the jacket
FLOW_GAS_CORE_R_FRACTION = 0.85   # hot-gas core radius / local gas-side wall radius
FLOW_TUBE_BORE_FRACTION = 0.45    # ring / feed-line flow tube radius / its drawn bore
FLOW_JACKET_TUBE_GAP_FRACTION = 0.35  # jacket stream radius / local wall-to-jacket gap
FLOW_JACKET_TUBE_DT_CLAMP = (0.006, 0.02)  # ... clamped to this fraction of throat dia


def build_flow_pieces(result, flow_anchors, body_shell, ext_shell, has_extension,
                      chamber_shell=None, network=None):
    """
    Flow-visualization pieces (untagged - build_mesh_data tags them "flow")
    for physics/flow_network.build_flow_network's segments, mapped onto the
    RENDERED geometry:
      - jacket passes -> FLOW_JACKET_STREAMS tubes midway between the gas-side
        contour and the drawn outer wall, in flow order (a two-pass design
        alternates down/up streams round the circumference);
      - manifold rings -> a loop at the drawn ring's own centreline;
      - feed lines -> the drawn plumbing run's centreline, reversed so it runs
        pump -> ring (hosts with no drawn run get none);
      - hot gas -> a revolved core at FLOW_GAS_CORE_R_FRACTION of the wall.
    """
    network = network if network is not None else flow_network.build_flow_network(result)
    xs = np.asarray(result["profile_xs_m"], dtype=float)
    rs = np.asarray(result["profile_rs_m"], dtype=float)
    dt = float(result["geometry"]["throat_dia_m"])
    rings = (flow_anchors or {}).get("rings", {})
    feeds = (flow_anchors or {}).get("feed_lines", {})
    pieces = []
    s_run = {"fuel": 0.0, "ox": 0.0, "gas": 0.0}   # arc length travelled per stream

    def _add(piece):
        if piece is not None:
            pieces.append(piece)

    for seg in sorted(network, key=lambda sg: (sg.propellant, sg.order)):
        host = seg.anchor.get("host")
        if seg.kind == "chamber_gas":
            _add(preview3d_gl_core.gas_core_mesh(xs, FLOW_GAS_CORE_R_FRACTION * rs, seg.t_k))
        elif seg.kind == "feed_line" and host in feeds:
            line, bore = feeds[host]
            r = FLOW_TUBE_BORE_FRACTION * float(np.median(bore))
            tube = preview3d_gl_core.flow_tube_mesh(line[::-1], seg.t_k[0], r,
                                                    s_offset_m=s_run[seg.propellant])
            _add(tube)
            if tube is not None:
                s_run[seg.propellant] = float(tube.flow_s.max())
        elif seg.kind == "manifold_ring" and host in rings:
            ring, edge = rings[host]
            ang0 = float(ring.get("attach_angular_position_deg", 0.0))
            angles = ang0 + np.linspace(0.0, 360.0, 97)
            rr = np.array([ring_local_render(ring, edge, a)[0] for a in angles])
            tube_r = FLOW_TUBE_BORE_FRACTION * float(ring["outer_radius_m"])
            loop = preview3d_gl_core.ring_loop_points(ring["attach_axial_station_m"], rr, ang0,
                                                      n=angles.size)
            tube = preview3d_gl_core.flow_tube_mesh(loop, seg.t_k[0], tube_r,
                                                    s_offset_m=s_run[seg.propellant])
            _add(tube)
            if tube is not None:
                s_run[seg.propellant] = float(tube.flow_s.max())
        elif seg.kind == "jacket_pass":
            idx = np.asarray(seg.anchor["stations"])
            x = xs[idx]
            r_in = rs[idx]
            r_out = np.array([_lookup_r(body_shell, ext_shell, has_extension, xq, chamber_shell)
                              for xq in x])
            gap = np.maximum(r_out - r_in, 0.0)
            lo, hi = FLOW_JACKET_TUBE_DT_CLAMP
            tube_r = float(np.clip(FLOW_JACKET_TUBE_GAP_FRACTION * np.median(gap), lo * dt, hi * dt))
            # Mid-jacket, but never closer than one stream radius to the gas-side
            # wall: a thin aft jacket (~1 mm) is narrower than a VISIBLE stream,
            # so there the stream may stand proud of the drawn outer wall instead.
            # (Clearance measured along the wall normal: a sloped wall needs
            # tube_r * sqrt(1 + (dr/dx)^2) of radial standoff.)
            slope = np.gradient(r_in, x) if x.size > 1 else np.zeros_like(x)
            r_mid = np.maximum(r_in + 0.5 * gap, r_in + tube_r * np.sqrt(1.0 + slope ** 2))
            n = FLOW_JACKET_STREAMS
            ks = range(n)
            if seg.anchor.get("pass") == "down":
                ks = range(0, n, 2)
            elif seg.anchor.get("pass") == "up":
                ks = range(1, n, 2)
            s_end = s_run[seg.propellant]
            for k in ks:
                th = 2.0 * np.pi * (k + 0.5) / n
                line = np.stack([x, r_mid * np.cos(th), r_mid * np.sin(th)], axis=1)
                tube = preview3d_gl_core.flow_tube_mesh(line, seg.t_k, tube_r,
                                                        s_offset_m=s_run[seg.propellant])
                _add(tube)
                if tube is not None:
                    s_end = max(s_end, float(tube.flow_s.max()))
            s_run[seg.propellant] = s_end
    return pieces


def build_mesh_data(result, heat_flux_mode, duct_bend_radius_mult=None, return_context=False):
    """
    Build every mesh piece for one EngineDesign.compute() result - the
    orchestrator that was `_build_mesh_data` before this split. Does the
    shared prep once, then calls each per-part builder in the same order the
    original method always built them in.

    duct_bend_radius_mult: optional override for the fuel main-inlet duct's
    bend radius (plumbing.default_run_for_host, via build_injector_head_pieces) -
    None uses DUCT_BEND_RADIUS_TUBE_DIA_MULT; threaded through purely for
    gui/app.py's debug slider, no physics effect.

    return_context=True additionally returns the body/ext ShellMesh + has_extension
    used for wall-snapping (ring_render_center_r's need), as (pieces, context).
    """
    pieces = []
    body_xs, body_rs, ext_xs, ext_rs, has_extension = geometry.split_profile_by_area_ratio(
        result["profile_xs_m"], result["profile_rs_m"],
        result["geometry"]["throat_dia_m"], result["eps_for_transition"])

    chamber_mat = materials.MATERIALS[result["inputs"]["material_key"]]
    bell_mat = materials.MATERIALS[result["inputs"]["bell_material_key"]]
    chamber_rgb = _hex_to_rgb01(chamber_mat.color_hex)
    bell_rgb = _hex_to_rgb01(bell_mat.color_hex)

    # has_extension (above) is purely a RENDERING split - True whenever the
    # cooling-transition area ratio falls short of the nozzle exit, which
    # is true of nearly every design by default, regardless of whether the
    # chamber and bell are actually different materials. A flange/bolted
    # joint only makes physical sense where there's a genuine two-piece
    # assembly (a real material change) - so gate that detail on this,
    # not on has_extension alone.
    has_real_joint = has_extension and (
        result["inputs"]["material_key"] != result["inputs"]["bell_material_key"])

    def q_colors(xs):
        if not heat_flux_mode:
            return None
        cooling = result.get("cooling")
        if not cooling or cooling.get("q_profile_w_m2") is None or len(xs) == 0:
            return None
        q = np.interp(xs, result["profile_xs_m"], cooling["q_profile_w_m2"])
        return preview3d_gl_core.heat_flux_colors(q)

    def spec_for(colors_per_station, mat):
        # The heat-flux colormap overlay is a data readout, not a material
        # look - a specular highlight would compete with/obscure it, so
        # force flat (no-specular) shading on any piece using it.
        return (0.0, mat.shininess) if colors_per_station is not None \
            else (mat.specular_strength, mat.shininess)

    # Real per-station wall thickness (physics/mass_model.wall_thickness_profile_m,
    # threaded through physics/design.py) drives an actual solid shell
    # instead of a bare open surface; real per-station channel geometry
    # (physics/cooling.channel_geometry_profile) - where the regen model
    # ran in "channels" mode - drives a rib/tube pattern on the outer
    # wall, distinguishing wall_construction visually. Both fall back to
    # zero/absent gracefully (a flat, undetailed shell) if unavailable.
    cooling_result = result.get("cooling") or {}
    body_wall_thickness_m = result.get("body_wall_thickness_m")
    if body_wall_thickness_m is None or len(body_wall_thickness_m) != len(body_rs):
        body_wall_thickness_m = np.zeros_like(body_rs)
    ext_wall_thickness_m = result.get("ext_wall_thickness_m")
    if ext_wall_thickness_m is None or len(ext_wall_thickness_m) != len(ext_rs):
        ext_wall_thickness_m = np.zeros_like(ext_rs)

    construction = cooling_result.get("wall_construction", "milled_channel")
    n_channels_physical = cooling_result.get("coolant_channels") or 0
    land_fraction = cooling_result.get("channel_land_fraction") or 0.35
    regen_circuit_style = cooling_result.get("regen_circuit_style", "single_pass_upflow")
    # J-2 layout: the double-pass down tubes begin at the mid-nozzle inlet ring.
    _jmr = result.get("jacket_manifold_result") or {}
    down_tube_start_x_m = (float(_jmr["jacket_inlet"]["attach_axial_station_m"])
                           if result.get("cooling_flow_topology") == "j2_mid_nozzle_inlet"
                           and _jmr.get("jacket_inlet") else None)

    throat_dia_m = result["geometry"]["throat_dia_m"]
    x_split = float(body_xs[-1]) if len(body_xs) else 0.0

    # Flange half-width needs to be known EARLY (before the tube
    # hard-cutoff x below), not just at the point the flange mesh itself
    # gets built further down.
    flange_half_width = 0.0
    if has_real_joint and throat_dia_m > 0:
        thickness_override_m = float(cooling_result.get("flange_thickness_m") or 0.0)
        flange_half_width = (thickness_override_m / 2.0 if thickness_override_m > 0
                              else preview3d_gl_core.FLANGE_HALF_WIDTH_THROAT_DIA_MULT * throat_dia_m)

    def _x_at_eps(eps_value):
        """x where local area ratio (over the WHOLE profile, searched
        from the throat forward) first reaches eps_value - already
        pre-clamped to <= expansion_ratio by callers, so np.interp's own
        out-of-range clamping naturally handles a full-length-regen
        design with no special case."""
        if eps_value is None or throat_dia_m <= 0:
            return None
        full_xs = np.asarray(result["profile_xs_m"], dtype=float)
        full_rs = np.asarray(result["profile_rs_m"], dtype=float)
        if full_rs.size < 2:
            return None
        full_throat_idx = int(np.argmin(full_rs))
        full_local_eps = (full_rs / (throat_dia_m / 2.0)) ** 2
        div_eps, div_xs = full_local_eps[full_throat_idx:], full_xs[full_throat_idx:]
        if div_eps.size < 2:
            return None
        return float(np.interp(eps_value, div_eps, div_xs))

    # The far-end cover hardware's x position - determined here, BEFORE
    # body_shell/ext_shell are built, because build_shell_mesh's returned
    # outer_xs/outer_rs is the SMOOTH pre-tube-modulation envelope (see
    # its own docstring), so this position never actually depended on the
    # shells existing. Computing it now lets the tube/channel geometry
    # below HARD-TERMINATE exactly where the cover ends up - tucked
    # under/into it - instead of the earlier smooth-taper approach (tubes
    # shrinking gradually into the extension, still visibly poking past
    # the cover as a tapering point).
    #
    # BOTH regen_circuit_style values get shifted clear of a real
    # bolted-flange joint the same way (onto the chamber side, away from
    # the nozzle exit) - the raw cooled-length x by default coincides
    # almost exactly with the flange itself (cooled_length_eps ==
    # eps_for_transition unless regen_nozzle_end_eps was raised), so an
    # unshifted, symmetric cover there straddles the flange - half on
    # the chamber side, half poking past it into the extension. Since
    # the pipes now hard-cut to match wherever the cover ends up
    # (nothing left to "uncover" the way a shift could with the old
    # smooth-taper approach), there's no downside to shifting either
    # style - only "own_extent" (how far each style's own hardware
    # reaches from its center) differs.
    cooled_length_eps = cooling_result.get("cooled_length_eps")
    x_manifold_raw = _x_at_eps(cooled_length_eps)
    x_tube_cutoff = x_manifold_raw
    own_extent = (preview3d_gl_core.MANIFOLD_TUBE_R_THROAT_DIA_MULT * throat_dia_m
                  if regen_circuit_style == "single_pass_upflow"
                  else preview3d_gl_core.TUBE_END_CAP_HALF_WIDTH_THROAT_DIA_MULT * throat_dia_m)
    if x_manifold_raw is not None and has_real_joint and throat_dia_m > 0:
        bolt_reach = preview3d_gl_core.BOLT_HEAD_LENGTH_THROAT_DIA_MULT * throat_dia_m
        required_reach = (flange_half_width + bolt_reach
                           + preview3d_gl_core.FLANGE_HARDWARE_CLEARANCE_MARGIN_M)
        x_tube_cutoff = preview3d_gl_core.manifold_clear_of_flange_x(
            x_manifold_raw, x_split, required_reach, own_extent)

    # x_tube_cutoff (above) positions the COVER hardware itself (the
    # manifold ring / end-cap band, built further down) - unchanged by
    # this. The discrete PIPES need to reach further than that: a pipe
    # ending exactly at the ring's own center sits merely TANGENT to its
    # torus surface (touching, not embedded - the ring only dips down to
    # the pipe's own radius at that one axial station), reading as
    # "stopping right at the ring" rather than genuinely running into it.
    #
    # A prior round tried solving exactly where the pipe's path first
    # gets geometrically INSIDE the ring's solid torus volume - real
    # math, but capped by the LOCAL bell slope there: the closest
    # approach achievable by pure axial motion is
    # ring_r/sqrt(1+slope^2), which for the shallow slopes typical of a
    # real bell is only a few percent inside at best - often not even
    # visually perceptible, so "solving it exactly" still didn't look
    # like it reached. Spanning the cover's own axial footprint instead
    # (push by its own "reach," own_extent, times a style-dependent
    # fraction) is slope-independent and always reads as "the pipe runs
    # through the cover," not "the pipe barely grazes its surface" -
    # TUBE_COVER_PENETRATION_RING_FRACTION (1.0) spans the manifold
    # ring's entire width; TUBE_COVER_PENETRATION_BAND_FRACTION (0.25) is
    # more modest since the end-cap band is already much wider than the
    # ring to begin with.
    x_tube_end = x_tube_cutoff
    if x_tube_cutoff is not None:
        penetration_fraction = (preview3d_gl_core.TUBE_COVER_PENETRATION_RING_FRACTION
                                 if regen_circuit_style == "single_pass_upflow"
                                 else preview3d_gl_core.TUBE_COVER_PENETRATION_BAND_FRACTION)
        x_tube_end = x_tube_cutoff + penetration_fraction * own_extent

    # Chamber Jacket: cover the COMBUSTION CHAMBER (injector face through
    # the throat) with a smooth wall instead of showing its tubes (real
    # tube-wall engines often wrap the chamber in a reinforcing band) -
    # purely a rendering choice, forces that segment onto the existing
    # "coax_shell" smooth-revolve path. Deliberately does NOT cover the
    # rest of the "body" piece past the throat (which, in this tool's
    # material-transition split, already reaches partway into the bell/
    # divergent nozzle, e.g. eps up to 6 by default) - that portion is the
    # bell, not the chamber, and should keep showing tubes. Where the
    # jacket ends is found the same way as tube_split_x_for_piece below
    # (local minimum radius = the throat), not the material-transition
    # point. effective_offset_thickness_m (below) is construction-
    # agnostic, so the jacket still sits far enough out to plausibly cover
    # the hidden tube layer. A no-op unless wall_construction is actually
    # "tube_wall" (milled_channel/coax_shell already show no exposed tubes).
    chamber_tube_jacket = bool(cooling_result.get("chamber_tube_jacket", False))

    # Bell tube-split: at a configurable area ratio, the visual tube count
    # doubles (1 tube -> 2), matching a real tube-wall bifurcation (e.g.
    # the F-1's 178->356 split at its 3:1 plane). tube_split_eps==0 means
    # "no split" (today's single-count-for-the-whole-engine behavior).
    tube_split_eps = cooling_result.get("tube_split_eps") or 0.0
    throat_dia_m_for_split = result["geometry"]["throat_dia_m"]

    def tube_split_x_for_piece(xs, rs):
        """Interpolated x where local area ratio first reaches
        tube_split_eps, searched only in the diverging (post-throat) part
        of this piece (matches geometry.split_profile_by_area_ratio's own
        throat-idx-forward search convention - a split before the throat
        isn't physically meaningful). None if the split doesn't fall
        inside this piece's own x-range."""
        if tube_split_eps <= 0 or throat_dia_m_for_split <= 0 or len(xs) < 2:
            return None
        rs = np.asarray(rs, dtype=float)
        throat_idx = int(np.argmin(rs))
        local_eps = (rs / (throat_dia_m_for_split / 2.0)) ** 2
        div_eps = local_eps[throat_idx:]
        div_xs = np.asarray(xs, dtype=float)[throat_idx:]
        if div_eps[-1] < tube_split_eps or div_eps[0] >= tube_split_eps:
            return None
        return float(np.interp(tube_split_eps, div_eps, div_xs))

    def n_channels_for_piece(rs):
        """Base tube count to pass for this piece: doubled if the WHOLE
        piece already starts past the split (no internal split needed),
        unchanged otherwise (build_shell_mesh handles an internal split
        itself via tube_split_x_for_piece)."""
        if tube_split_eps <= 0 or throat_dia_m_for_split <= 0 or len(rs) == 0:
            return n_channels_physical
        rs = np.asarray(rs, dtype=float)
        throat_idx = int(np.argmin(rs))
        start_eps = (rs[throat_idx] / (throat_dia_m_for_split / 2.0)) ** 2
        return 2 * n_channels_physical if start_eps >= tube_split_eps else n_channels_physical

    def channel_heights(xs, rs, wall_thickness_m):
        prof = cooling_result.get("channel_height_profile_m")
        if prof is None or len(xs) == 0:
            return None
        heights = np.interp(xs, result["profile_xs_m"], prof)
        # Real channel/tube geometry only exists where the regen jacket
        # actually runs. physics/cooling.channel_geometry_profile is a
        # purely geometric function of the WHOLE contour, unaware of
        # where active cooling stops, so it still returns a nonzero
        # height past that point - which would otherwise draw channel
        # ribs/tubes on a bare (radiatively-cooled or otherwise uncooled)
        # skirt where none physically exist, or keep showing pipes well
        # past the far-end cover hardware. HARD cutoff (no gradual taper)
        # at x_tube_end (not x_tube_cutoff - the COVER's own position;
        # x_tube_end deliberately reaches a bit further, into the cover's
        # footprint, computed above), so the pipes terminate genuinely
        # embedded inside/under that cover instead of merely touching its
        # near surface or tapering past it into the extension.
        #
        # This threshold compares against RAW (pre-offset) xs, while
        # build_shell_mesh's own tube_cutoff_x_m resolution (which decides
        # which station actually gets the flat cap) compares against the
        # THICKNESS-OFFSET xs (offset_profile shifts x by up to the local
        # wall thickness along the meridian normal). With x_tube_end's
        # push into the cover now deliberately small (a fraction of the
        # cover's own size - see TUBE_COVER_PENETRATION_*_FRACTION), that
        # offset shift can be comparable to or larger than the push
        # itself, so a station this raw-xs comparison zeroes could still
        # be the exact station build_shell_mesh resolves as the cap -
        # rendering a zero-radius "cap" instead of a real one. Pad the
        # threshold by the local wall thickness (an upper bound on the
        # offset shift, since offset_profile's normal component is always
        # <= 1) so this comparison can never zero a station before
        # build_shell_mesh's own offset-aware resolution would.
        if x_tube_end is not None:
            safety_pad = float(np.max(wall_thickness_m)) if len(wall_thickness_m) else 0.0
            heights = np.where(np.asarray(xs, dtype=float) <= x_tube_end + safety_pad, heights, 0.0)
        return heights

    # The rendered wall-offset distance, used everywhere below in place of
    # the bare structural thickness: at least as large as (channel height
    # + a thin outer jacket) when real channel data exists, since a
    # ribbed wall's true outer surface sits outside the channel/tube
    # layer, not at the bare hoop-stress shell thickness that's only
    # correct for an unribbed wall. Without this, a thin nozzle-extension
    # skirt (sized off local static pressure, can be a fraction of a mm)
    # would choke channel_modulated_grid's amplitude clamp down to
    # invisible ribs despite several mm of real channel height.
    body_channel_heights = channel_heights(body_xs, body_rs, body_wall_thickness_m)
    ext_channel_heights = channel_heights(ext_xs, ext_rs, ext_wall_thickness_m)
    body_thickness_eff = preview3d_gl_core.effective_offset_thickness_m(
        body_wall_thickness_m, body_channel_heights)
    ext_thickness_eff = preview3d_gl_core.effective_offset_thickness_m(
        ext_wall_thickness_m, ext_channel_heights)

    (chamber_pieces, body_shell, ext_shell, flange_height_m,
     chamber_shell) = build_chamber_and_bell_shell_pieces(
        body_xs, body_rs, ext_xs, ext_rs, has_extension, has_real_joint, chamber_rgb, bell_rgb,
        chamber_mat, bell_mat, construction, n_channels_physical, land_fraction,
        regen_circuit_style, throat_dia_m, x_split, body_thickness_eff, ext_thickness_eff,
        body_channel_heights, ext_channel_heights, chamber_tube_jacket, tube_split_x_for_piece,
        n_channels_for_piece, x_tube_end, q_colors, spec_for, cooling_result,
        down_tube_start_x_m=down_tube_start_x_m)
    pieces.extend(_tag(chamber_pieces, "wall"))
    flow_anchors = {}

    pieces.extend(_tag(build_injector_head_pieces(
        body_rs, result, chamber_rgb, construction, n_channels_physical,
        body_shell, ext_shell, has_extension,
        duct_bend_radius_mult=duct_bend_radius_mult,
        return_band_drawn=(construction == "tube_wall" and n_channels_physical > 0
                           and x_tube_cutoff is not None
                           and preview3d_gl_core.is_double_pass(regen_circuit_style)),
        chamber_shell=chamber_shell, flow_anchors=flow_anchors), "injector_head"))

    pieces.extend(_tag(build_far_end_cover_pieces(
        construction, n_channels_physical, x_tube_cutoff, regen_circuit_style, throat_dia_m,
        body_shell, ext_shell, has_extension), "cover"))

    pieces.extend(_tag(build_tube_hatband_pieces(
        cooling_result, construction, n_channels_physical, throat_dia_m,
        body_shell, ext_shell, has_extension), "hatband"))

    pieces.extend(_tag(build_flange_joint_pieces(
        has_real_joint, throat_dia_m, body_shell, ext_shell, x_split,
        flange_half_width, flange_height_m, cooling_result), "flange"))

    pieces.extend(_tag(build_turbopump_pieces(result), "turbopump"))

    # Flow visualization - always built, only drawn while the preview's Flow
    # toggle is on (render_layers skips "flow" pieces otherwise; no rebuild).
    pieces.extend(_tag(build_flow_pieces(result, flow_anchors, body_shell, ext_shell,
                                         has_extension, chamber_shell),
                       preview3d_gl_core.FLOW_ROLE))

    if return_context:
        return pieces, {"body_shell": body_shell, "ext_shell": ext_shell,
                        "has_extension": has_extension, "chamber_shell": chamber_shell}
    return pieces


def self_test():
    """
    Builds a representative EngineDesign result (same pattern gui/schematic.py's
    and gui/preview3d.py's own headless smoke tests use, via
    physics.design.EngineDesign) and asserts build_mesh_data returns a non-empty,
    structurally sane piece list, for both heat_flux_mode=False and True. Uses
    wall_construction="tube_wall" (plus tube_hatbands/chamber_tube_jacket) and a
    real chamber/bell material split (default narloy_z/inconel_718) so this
    exercises every per-part builder above, not just the plain milled_channel/
    no-hardware path.
    """
    from ..physics import cycles
    from ..physics.design import EngineDesign

    design = EngineDesign(propellant_pair="LOX/RP-1", mixture_ratio=2.34,
                           chamber_pressure_pa=8.0e6, expansion_ratio=14,
                           nozzle_type="bell", bell_percent_length=80.0,
                           cycle=cycles.GAS_GENERATOR, throttle_floor=0.6,
                           target_vac_thrust_n=1_450_000, wall_construction="tube_wall",
                           tube_hatbands=True, chamber_tube_jacket=True)
    result = design.compute()

    # Turbopump placement refactor regression: the shared geometry3d helper
    # must put the assembly exactly where the previous inline formula did.
    _sz = result["turbopump_sizing"]
    _cr = float(result["profile_rs_m"].max())
    _old_origin = (0.03 * float(result["profile_xs_m"].max()),
                   _cr + 0.5 * _sz["assembly_od_m"] + 0.04 * _cr, 0.0)
    _new_origin = geometry3d.turbopump_origin_xyz(
        float(result["profile_xs_m"].max()), _cr, _sz["assembly_od_m"])
    assert np.allclose(_old_origin, _new_origin), (_old_origin, _new_origin)
    _tp_pieces = build_turbopump_pieces(result)
    _stubs = turbopump_port_stub_pieces(result)
    assert _tp_pieces and len(_tp_pieces) == len(_sz["bodies"]) + len(_stubs)
    assert len(_stubs) == 3 * 2 * len(result["turbopump_ports"])   # ray_mesh = body + 2 disks
    _pump_pts = geometry3d.turbopump_pump_points(_sz["bodies"], _new_origin)
    # each pump point sits inside the x-span of some turbopump piece's vertices
    for _pt in _pump_pts.values():
        assert any(p.vertices[:, 0].min() - 1e-9 <= _pt[0] <= p.vertices[:, 0].max() + 1e-9
                   for p in _tp_pieces)
    print("turbopump placement (geometry3d.turbopump_origin_xyz) regression: OK")

    # Structural hatbands: one revolved section per physics-sized band (+ the
    # continuous-shell sleeve), each sitting OUTSIDE the tube-crest envelope.
    _hb = result["cooling"]["hatbands"]
    assert _hb and _hb["n_bands"] > 0, "self-test design should carry sized hatbands"
    _bx, _br, _ex, _er, _has_ext = geometry.split_profile_by_area_ratio(
        result["profile_xs_m"], result["profile_rs_m"],
        result["geometry"]["throat_dia_m"], result["eps_for_transition"])

    class _Env:     # minimal ShellMesh stand-in: crest envelope = gas-side contour
        def __init__(self, xs, rs):
            self.outer_xs, self.outer_rs = np.asarray(xs), np.asarray(rs)
    _hb_pieces = build_tube_hatband_pieces(
        result["cooling"], "tube_wall", 200, result["geometry"]["throat_dia_m"],
        _Env(_bx, _br), _Env(_ex, _er), _has_ext)
    _sleeve = 1 if (_hb["shell_end_x_m"] or 0) - (_hb["shell_start_x_m"] or 0) > 1e-3 else 0
    assert len(_hb_pieces) == _hb["n_bands"] + _sleeve, (len(_hb_pieces), _hb["n_bands"], _sleeve)
    _env_xs = np.concatenate([_bx, _ex]) if _has_ext else _bx
    _env_rs = np.concatenate([_br, _er]) if _has_ext else _br
    for _pc in _hb_pieces:
        _r = np.hypot(_pc.vertices[:, 1], _pc.vertices[:, 2])
        _crest = np.interp(_pc.vertices[:, 0], _env_xs, _env_rs)
        assert np.all(_r >= _crest - 2e-3), "band dips into the tube crests"
        assert not np.any(np.isnan(_pc.vertices))
    # every section shape renders
    for _shape in hatbands.BAND_SECTIONS:
        _one = dict(_hb, bands=[dict(_hb["bands"][0], shape=_shape,
                                     height_m=hatbands.section_height_m(
                                         _shape, _hb["bands"][0]["width_m"],
                                         _hb["bands"][0]["gauge_m"]))],
                    shell_start_x_m=None, shell_end_x_m=None)
        _p1 = build_tube_hatband_pieces(dict(result["cooling"], hatbands=_one), "tube_wall", 200,
                                        result["geometry"]["throat_dia_m"], _Env(_bx, _br),
                                        _Env(_ex, _er), _has_ext)
        assert len(_p1) == 1 and _p1[0].indices.shape[0] > 0, _shape
    print(f"structural hatband rendering: OK ({_hb['n_bands']} bands, "
          f"{'/'.join(_hb['shapes_used'])}, sleeve={bool(_sleeve)})")

    for heat_flux_mode in (False, True):
        pieces = build_mesh_data(result, heat_flux_mode)
        assert isinstance(pieces, list)
        assert len(pieces) > 0
        for piece in pieces:
            assert not np.any(np.isnan(piece.vertices))
            assert not np.any(np.isnan(piece.normals))
            assert piece.vertices.shape == piece.normals.shape == piece.colors.shape
            if piece.indices.shape[0] > 0:
                assert piece.indices.max() < piece.vertices.shape[0]
        # heat_flux_mode=True should actually vary vertex colors across at
        # least one piece (the whole point of the overlay), unlike the flat
        # per-material colors of heat_flux_mode=False.
        if heat_flux_mode:
            assert any(np.ptp(p.colors, axis=0).max() > 1e-6 for p in pieces)
        # every piece carries a render role, and X-ray batching conserves geometry
        assert all(p.role for p in pieces), sorted({p.role for p in pieces})
        for xray in (False, True):
            batches = preview3d_gl_core.build_batches(pieces, xray, flow_enabled=True)
            assert sum(b.buffers.vertices.shape[0] for b in batches) == \
                sum(p.vertices.shape[0] for p in pieces if p.indices.size)
            assert len(batches) < len(pieces)
    print("build_mesh_data self-check (tube_wall, real joint, turbopump): OK")

    # Flow visualization pieces: present, every vertex carries a finite
    # temperature/arc length, and the drawn temperature range is the network's.
    _flow = [p for p in build_mesh_data(result, False) if p.role == preview3d_gl_core.FLOW_ROLE]
    _net = flow_network.build_flow_network(result)
    _n_jacket = sum(1 for sg in _net if sg.kind == "jacket_pass")
    assert _n_jacket and len(_flow) >= 1 + FLOW_JACKET_STREAMS, len(_flow)
    _all_t = np.concatenate([p.scalar for p in _flow])
    assert np.all(np.isfinite(_all_t)) and all(np.all(np.isfinite(p.flow_s)) for p in _flow)
    _lo, _hi = flow_network.temperature_range(_net)
    assert abs(_all_t.min() - _lo) < 1.0 and abs(_all_t.max() - _hi) < 1.0, (_all_t.min(), _lo)
    # jacket streams sit radially between the gas-side contour and the drawn outer wall
    _, _ctx = build_mesh_data(result, False, return_context=True)
    _xs, _rs = result["profile_xs_m"], result["profile_rs_m"]
    _jnet = [sg for sg in _net if sg.kind == "jacket_pass"]
    _jet = build_flow_pieces(result, {}, _ctx["body_shell"], _ctx["ext_shell"],
                             _ctx["has_extension"], _ctx["chamber_shell"], network=_jnet)
    assert len(_jet) == FLOW_JACKET_STREAMS * len(_jnet)
    for _p in _jet:
        _r = np.hypot(_p.vertices[:, 1], _p.vertices[:, 2])
        _rin = np.interp(_p.vertices[:, 0], _xs, _rs)
        assert np.all(_r > _rin - 1e-4), ("jacket stream inside the gas-side wall",
                                          float((_r - _rin).min()), _p.vertices[np.argmin(_r - _rin)])
    print(f"flow pieces: OK ({len(_flow)} pieces, {_lo:.0f}-{_hi:.0f} K)")

    # A second, simpler design (milled_channel, no forced material split via
    # matching chamber/bell materials) - covers the has_real_joint=False path
    # (no flange/bolt hardware) and the plain channel_modulated_grid shell.
    design_simple = EngineDesign(propellant_pair="LOX/RP-1", mixture_ratio=2.34,
                                  chamber_pressure_pa=8.0e6, expansion_ratio=14,
                                  nozzle_type="conical", nozzle_half_angle_deg=15.0,
                                  cycle=cycles.GAS_GENERATOR, material_key="narloy_z",
                                  bell_material_key="narloy_z", throttle_floor=0.6,
                                  target_vac_thrust_n=1_450_000)
    result_simple = design_simple.compute()
    pieces_simple = build_mesh_data(result_simple, heat_flux_mode=False)
    assert len(pieces_simple) > 0
    for piece in pieces_simple:
        assert not np.any(np.isnan(piece.vertices))
    print("build_mesh_data self-check (milled_channel, no real joint): OK")

    # Double-pass topologies (F-1 split and J-2 mid-nozzle inlet): the end-cap
    # band IS the return manifold, so the olive jacket_return torus is never
    # drawn - exactly one olive piece fewer than a hypothetical torus-drawing
    # build (the inlet ring + legacy duct pieces are olive in both). The tube
    # style now follows the topology (design.REGEN_CIRCUIT_STYLE_BY_TOPOLOGY).
    def _n_olive(res):
        return sum(1 for p in build_mesh_data(res, False)
                   if p.colors.shape[0] and np.allclose(p.colors[:, :3], (0.56, 0.56, 0.20)))
    for _topo, _style in (("f1_split_reverse_flow", "f1_double_pass"),
                          ("j2_mid_nozzle_inlet", "j2_two_pass")):
        _inputs = {**result["inputs"], "cooling_flow_topology": _topo,
                   "regen_channel_model": "channels"}  # real tube count -> band drawn
        _res_band = EngineDesign(**_inputs).compute()
        assert _res_band["cooling"]["regen_circuit_style"] == _style
        assert _res_band["jacket_manifold_result"]["jacket_return"] is not None
        _n_band = _n_olive(_res_band)
        # Force the torus path (return_band_drawn=False) for the comparison.
        _real = build_injector_head_pieces
        def _no_band(*a, **k):
            k["return_band_drawn"] = False
            return _real(*a, **k)
        globals()["build_injector_head_pieces"] = _no_band
        try:
            _n_torus = _n_olive(_res_band)
        finally:
            globals()["build_injector_head_pieces"] = _real
        assert _n_torus - _n_band == 1, (_topo, _n_torus, _n_band)
        # J-2: the user's tube_split_eps is ignored (the inlet ring is the split)
        if _topo == "j2_mid_nozzle_inlet":
            _res_split = EngineDesign(**{**_inputs, "tube_split_eps": 3.0}).compute()
            assert _res_split["cooling"]["tube_split_eps"] == 0.0
    # Chamber Jacket on vs off: the injector-end rings stay flush on the
    # chamber wall (the jacket used to hide the chamber shell from the wall
    # lookup, snapping the rings out to the bell-end radius).
    _jk_inputs = {**result["inputs"], "chamber_tube_jacket": False}
    _res_nojk = EngineDesign(**_jk_inputs).compute()
    _cr_nojk = float(_res_nojk["profile_rs_m"].max())
    for _k in ("fuel", "ox"):
        _e_on = ring_render_inner_edge_r(result, result["manifold_result"][_k])
        _e_off = ring_render_inner_edge_r(_res_nojk, _res_nojk["manifold_result"][_k])
        assert abs(_e_on - _e_off) < 0.05 * _cr_nojk, (_k, _e_on, _e_off)
    print("Chamber Jacket keeps the injector rings on the chamber wall: OK")
    print("F-1 / J-2: end-cap band replaces the jacket_return torus: OK")

    # --- procedural plumbing (physics/plumbing.py): a baked jacket_inlet run
    # replaces the legacy auto duct (piece count differs by exactly the
    # run's own pieces minus the legacy duct's 3), flanges add pieces, the
    # selected-segment tint only touches the body's colors, and a run on a
    # host ring this design doesn't have is skipped silently ---
    hook = result["jacket_manifold_result"]["jacket_inlet"]
    n_legacy = len(build_mesh_data(result, False))
    run = plumbing.default_run_for_host(hook, hook["outer_radius_m"])
    run.pipes.append(plumbing.PipeSegment(length_dia_mult=4.0, yaw_deg=45.0, flange_at_end=True))
    run.flange_at_root = True
    design_run = EngineDesign(**{**{k: v for k, v in result["inputs"].items()},
                                 "plumbing_runs": [plumbing.run_to_dict(run)]})
    result_run = design_run.compute()
    pieces_run = build_mesh_data(result_run, False)
    ring_r = hook["major_radius_m"]  # any radius will do for the count/tint checks
    own_pieces, resolved = build_plumbing_pieces(run, hook, ring_r, hook["outer_radius_m"],
                                                 (0.56, 0.56, 0.20))
    assert len(own_pieces) > 3  # body + 2 caps + flange pieces
    assert len(pieces_run) == n_legacy - 3 + len(own_pieces), (len(pieces_run), n_legacy, len(own_pieces))
    for piece in pieces_run:
        assert not np.any(np.isnan(piece.vertices)) and not np.any(np.isnan(piece.normals))
    assert result_run["plumbing_mass_kg"] > 0.0
    # tint: same vertex count, only colors differ, and some stations changed
    tinted, _ = build_plumbing_pieces(run, hook, ring_r, hook["outer_radius_m"],
                                      (0.56, 0.56, 0.20), selected_index=2)
    assert tinted[0].vertices.shape == own_pieces[0].vertices.shape
    assert np.allclose(tinted[0].vertices, own_pieces[0].vertices)
    changed = np.any(tinted[0].colors != own_pieces[0].colors, axis=1)
    assert 0 < changed.sum() < changed.size
    # unknown-host run: skipped, and an empty run draws nothing
    orphan = plumbing.run_to_dict(plumbing.PlumbingRun(host="jacket_return", pipes=[plumbing.PipeSegment()]))
    design_orphan = EngineDesign(**{**result["inputs"], "plumbing_runs": [orphan]})
    assert len(build_mesh_data(design_orphan.compute(), False)) == n_legacy
    assert build_plumbing_pieces(plumbing.PlumbingRun(), hook, ring_r, hook["outer_radius_m"],
                                 (0.5, 0.5, 0.5))[0] == []
    # an elbow too big for its straights: resolve_run pre-clamps the effective
    # radius, so the render must NOT re-warn on every redraw (the Shape Lab
    # redraws on every slider tick - this used to spam the console)
    import warnings as _warnings
    tight = plumbing.PlumbingRun(pipes=[plumbing.PipeSegment(length_dia_mult=1.0),
                                        plumbing.PipeSegment(length_dia_mult=1.0, yaw_deg=90.0,
                                                             bend_radius_dia_mult=4.0),
                                        plumbing.PipeSegment(length_dia_mult=1.0, yaw_deg=90.0,
                                                             bend_radius_dia_mult=4.0)])
    with _warnings.catch_warnings():
        _warnings.simplefilter("error")
        tight_pieces, tight_res = build_plumbing_pieces(tight, hook, ring_r, hook["outer_radius_m"],
                                                        (0.5, 0.5, 0.5))
    assert tight_pieces and any("rendered at" in a for a in tight_res["advisories"])
    print("build_plumbing_pieces / baked-run swap-in self-check: OK")

    # --- pump-connected runs: seeded on the RENDER ring radius, closed onto
    # the design's discharge port in BOTH the physics (two-pass line loss) and
    # the render (auto legs lightened), landing exactly on the port ---
    _seeds = []
    for _host in ("jacket_inlet", "ox"):
        _hk = plumbing.hook_for_host(result, _host) if _host == "jacket_inlet" else \
            result["manifold_result"]["ox"]
        _port = result["turbopump_ports"][plumbing.HOST_PUMP[_host]]["discharge"]
        _seeds.append(plumbing.seed_route_to_port(_hk, _port, ring_render_center_r(result, _hk),
                                                  _hk["outer_radius_m"], _host))
    _res_conn = EngineDesign(**{**result["inputs"],
                                "plumbing_runs": [plumbing.run_to_dict(r) for r in _seeds]}).compute()
    assert _res_conn["line_loss_source"] == {"fuel": "computed", "ox": "computed"}
    for _leg in ("fuel", "ox"):
        assert _res_conn["line_loss_residual_pa"] < 0.02 * _res_conn[f"line_loss_{_leg}_pa"]
    assert all(pr["connected_pump"] for pr in _res_conn["plumbing_results"])
    for _r in _seeds:
        _hk = plumbing.hook_for_host(_res_conn, _r.host)
        _port = run_port_for_result(_res_conn, _r)
        _pcs, _rs = build_plumbing_pieces(_r, _hk, ring_render_center_r(_res_conn, _hk),
                                          _hk["outer_radius_m"], (0.5, 0.5, 0.5), port=_port)
        assert np.linalg.norm(_rs["waypoints_xyz"][-1] - _port["pos"]) < 1e-9
        _plain, _ = build_plumbing_pieces(_r, _hk, ring_render_center_r(_res_conn, _hk),
                                          _hk["outer_radius_m"], (0.5, 0.5, 0.5))
        assert _rs["auto_leg_indices"] and len(_pcs[0].vertices) > len(_plain[0].vertices)
        assert np.any(_pcs[0].colors > 0.5 + 1e-6)          # lightened auto legs
    assert len(build_mesh_data(_res_conn, False)) > n_legacy
    print(f"pump-connected runs (render + two-pass line loss): OK - fuel "
          f"{_res_conn['line_loss_fuel_pa'] / 1e3:.0f} kPa / ox {_res_conn['line_loss_ox_pa'] / 1e3:.0f} kPa "
          f"vs flat {500:.0f}, residual {_res_conn['line_loss_residual_pa']:.0f} Pa")

    print("ALL MESH_BUILDER CHECKS OK")


if __name__ == "__main__":
    self_test()
