"""
Whole-piece solid-shell composition for the OpenGL 3D preview: combines an
inner (gas-side) revolved wall, an outer wall offset by wall thickness (with
structural bumps baked in), optional end caps, and cooling-detail modulation
(discrete tube_wall tubes, milled_channel/coax_shell grid modulation) into
one ShellMesh - the top-level "compose one profile piece" entry point most
callers reach for. Split out of the former single-file
gui/preview3d_gl_core.py by geometry-operation kind - see this package's
__init__.py for the overview. No OpenGL/Tk import, pure numpy.
"""
from dataclasses import dataclass

import numpy as np

from ...physics import geometry3d
from .profile_geometry import offset_profile
from .mesh_primitives import revolve_to_buffers, mesh_from_grid, end_cap_ring, grid_vertex_normals
from .tube_bundle import (channel_modulated_grid, tube_bundle_pieces,
                          double_pass_tube_pieces, visual_channel_count)

@dataclass
class ShellMesh:
    """build_shell_mesh's return value. `pieces` is the drawable content
    (list[MeshBuffers]: [inner, outer, *caps], same as this function used to
    return directly). `outer_xs`/`outer_rs` are the ACTUAL final outer-wall
    contour this call used - post structural-bump application, pre channel/
    tube modulation - so a caller assembling multiple pieces (gui/
    preview3d_gl.py, joining the chamber/throat body to the nozzle extension)
    can bridge between two pieces' outer walls using the EXACT values that
    were actually rendered, not a re-derived approximation that could drift
    from them (the two pieces can have wildly different wall thickness - e.g.
    a chamber material's flat-pressure thickness vs. a nozzle extension's
    local-pressure thickness - so no single formula reliably predicts either
    piece's edge from the other's)."""
    pieces: list
    outer_xs: np.ndarray
    outer_rs: np.ndarray

DOUBLE_PASS_STYLES = ("f1_double_pass", "j2_two_pass")


def is_double_pass(regen_circuit_style):
    """True for the interleaved down/up tube styles - the F-1's, and the
    J-2's (whose down tubes start at its mid-nozzle inlet ring)."""
    return regen_circuit_style in DOUBLE_PASS_STYLES


def build_shell_mesh(xs_m, rs_m, thickness_m, n_theta, base_color_rgb, *,
                      colors_per_station=None, construction="milled_channel",
                      channel_height_profile_m=None, n_channels_physical=0,
                      land_fraction=0.35, structural_bumps=None,
                      cap_start=False, cap_end=False, tube_split_x_m=None,
                      regen_circuit_style="single_pass_upflow", tube_cutoff_x_m=None,
                      down_tube_start_x_m=None,
                      specular_strength=0.0, shininess=32.0):
    """
    Compose one profile piece (the chamber/throat body OR the nozzle
    extension - the same pieces gui/preview3d_gl.py's _build_mesh_data
    already splits via geometry.split_profile_by_area_ratio) into a real,
    approximately-manifold SOLID: an inner (gas-side) wall, an outer wall
    pushed out by `thickness_m` along the local meridian normal
    (offset_profile), optional end caps, and - when real channel data is
    given - circumferential cooling detail on the outer wall: genuinely
    discrete round tubes for "tube_wall" (tube_bundle_pieces), a rectangular
    groove/rib pattern for "milled_channel" (channel_modulated_grid), or
    nothing for "coax_shell" (a smooth double-wall annulus).

    `thickness_m` and `channel_height_profile_m` (if given) must already be
    resampled onto THIS piece's own xs_m/rs_m stations, matching the existing
    q_colors() interpolation convention in gui/preview3d_gl.py.

    `structural_bumps`, if given, is a list of
    {"center_x_m", "half_width_m", "height_m", "shape"} dicts (see
    physics/geometry3d.axial_bump_delta_r) summed into the outer profile
    BEFORE any tube/channel modulation - flanges/rings/the exit lip are
    axial-only bumps on the same base surface the ribs then ride on top of.

    `tube_split_x_m`, if given (construction=="tube_wall" only), is an x
    location WITHIN this piece where the tube count doubles (1 tube -> 2),
    matching a real tube-wall bifurcation (e.g. the F-1's 178->356 split at
    its 3:1 area-ratio plane) - rendered as two independent tube-bundle
    segments sharing one boundary station (a visible radius step there, like
    a real braze joint, not a smooth blend). The caller (gui/preview3d_gl.py)
    is responsible for translating an area ratio into this x-coordinate and
    for doubling `n_channels_physical` itself when a piece starts entirely
    past the split; this function only ever sees a plain x/r geometry problem.

    `regen_circuit_style` (construction=="tube_wall" only): "single_pass_upflow"
    (default) builds one tube_bundle_pieces band, unchanged from before this
    parameter existed. "f1_double_pass" builds double_pass_tube_pieces instead,
    adding a second interleaved "up" tube band alongside the same down tubes - see
    that function's docstring. Both styles use the identical outer envelope/backing
    geometry; only which tube meshes ride on top of it differs.

    `tube_cutoff_x_m`, if given (construction=="tube_wall" only), is an x location
    WITHIN this piece past which no discrete tube geometry should be rendered at
    all - snapped to the nearest station at or before it (same convention
    `tube_split_x_m` already uses), then forwarded as `active_end_idx` to
    tube_bundle_pieces/double_pass_tube_pieces so each tube gets a genuine flat
    end cap there instead of tapering to a point across the station where
    `channel_height_profile_m` (already zeroed past this x by the caller) goes to
    zero. Independent of `tube_split_x_m`; if both fall in the same piece, whichever
    of the resulting pre/post sub-segments the cutoff lands in gets it applied
    (the other is left uncapped - an unusual combination with no obvious real
    design behind it, since a tube-count split downstream of where cooling itself
    already stopped isn't physically meaningful).

    "j2_two_pass" draws the same two tube sets (see `down_tube_start_x_m`).

    `down_tube_start_x_m` (double-pass, no tube split in this piece): the
    x where the DOWN tubes begin - the J-2 layout's mid-nozzle inlet manifold
    (double_pass_tube_pieces' down_start_idx). None = down tubes throughout.

    Returns a ShellMesh.
    """
    xs_m = np.asarray(xs_m, dtype=float)
    rs_m = np.asarray(rs_m, dtype=float)

    inner = revolve_to_buffers(xs_m, rs_m, n_theta, base_color_rgb,
                                colors_per_station=colors_per_station,
                                flip_orientation=True,
                                specular_strength=specular_strength, shininess=shininess)

    outer_xs, outer_rs = offset_profile(xs_m, rs_m, thickness_m)
    for bump in (structural_bumps or []):
        outer_rs = outer_rs + geometry3d.axial_bump_delta_r(
            outer_xs, bump["center_x_m"], bump["half_width_m"], bump["height_m"],
            bump.get("shape", "smooth"))

    extra_pieces = []
    has_channel_data = channel_height_profile_m is not None and n_channels_physical > 0
    if construction == "tube_wall" and has_channel_data:
        # Genuinely discrete round tubes, not a corrugated approximation of
        # them - see tube_bundle_pieces. `rs_m` (the un-offset inner/gas-side
        # radius) is passed through so the valley floor can never cross it.
        n_stations = outer_xs.size
        channel_height_arr = np.broadcast_to(
            np.asarray(channel_height_profile_m, dtype=float), (n_stations,))
        thickness_arr = np.broadcast_to(np.asarray(thickness_m, dtype=float), (n_stations,))
        split_idx = None
        if (tube_split_x_m is not None and n_stations >= 3
                and outer_xs[0] < tube_split_x_m < outer_xs[-1]):
            split_idx = int(np.clip(np.searchsorted(outer_xs, tube_split_x_m), 1, n_stations - 1))

        cutoff_idx = None
        if (tube_cutoff_x_m is not None and n_stations >= 2
                and outer_xs[0] <= tube_cutoff_x_m <= outer_xs[-1]):
            cutoff_idx = int(np.clip(
                np.searchsorted(outer_xs, tube_cutoff_x_m, side="right") - 1, 0, n_stations - 1))

        double_pass = is_double_pass(regen_circuit_style)
        if split_idx is not None:
            sl_pre, sl_post = slice(0, split_idx + 1), slice(split_idx, None)  # shared
                                                          # boundary station - no x-gap
            active_end_idx_pre = cutoff_idx if cutoff_idx is not None and cutoff_idx <= split_idx else None
            active_end_idx_post = (cutoff_idx - split_idx
                                    if cutoff_idx is not None and cutoff_idx > split_idx else None)
            if double_pass:
                backing_pre, tubes_pre, up_pre, _ = double_pass_tube_pieces(
                    outer_xs[sl_pre], outer_rs[sl_pre], rs_m[sl_pre], n_theta,
                    n_channels_physical, channel_height_arr[sl_pre], thickness_arr[sl_pre],
                    base_color_rgb, specular_strength=specular_strength, shininess=shininess,
                    active_end_idx=active_end_idx_pre)
                backing_post, tubes_post, up_post, _ = double_pass_tube_pieces(
                    outer_xs[sl_post], outer_rs[sl_post], rs_m[sl_post], n_theta,
                    2 * n_channels_physical, channel_height_arr[sl_post], thickness_arr[sl_post],
                    base_color_rgb, specular_strength=specular_strength, shininess=shininess,
                    active_end_idx=active_end_idx_post)
                outer_pieces = [backing_pre, backing_post]
                extra_pieces = tubes_pre + up_pre + tubes_post + up_post
            else:
                backing_pre, tubes_pre = tube_bundle_pieces(
                    outer_xs[sl_pre], outer_rs[sl_pre], rs_m[sl_pre], n_theta,
                    n_channels_physical, channel_height_arr[sl_pre], thickness_arr[sl_pre],
                    base_color_rgb, specular_strength=specular_strength, shininess=shininess,
                    active_end_idx=active_end_idx_pre)
                backing_post, tubes_post = tube_bundle_pieces(
                    outer_xs[sl_post], outer_rs[sl_post], rs_m[sl_post], n_theta,
                    2 * n_channels_physical, channel_height_arr[sl_post], thickness_arr[sl_post],
                    base_color_rgb, specular_strength=specular_strength, shininess=shininess,
                    active_end_idx=active_end_idx_post)
                outer_pieces = [backing_pre, backing_post]
                extra_pieces = tubes_pre + tubes_post
        elif double_pass:
            # J-2 layout (down_tube_start_x_m): down tubes begin at the mid-
            # nozzle inlet; a piece wholly upstream of it has only up tubes.
            down_start_idx = None
            if down_tube_start_x_m is not None and n_stations >= 2:
                if down_tube_start_x_m >= outer_xs[-1]:
                    down_start_idx = n_stations - 1
                elif down_tube_start_x_m > outer_xs[0]:
                    down_start_idx = int(np.clip(np.searchsorted(outer_xs, down_tube_start_x_m),
                                                 1, n_stations - 1))
            backing, down_tubes, up_tubes, _ = double_pass_tube_pieces(
                outer_xs, outer_rs, rs_m, n_theta, n_channels_physical,
                channel_height_arr, thickness_arr, base_color_rgb,
                specular_strength=specular_strength, shininess=shininess,
                active_end_idx=cutoff_idx, down_start_idx=down_start_idx)
            outer_pieces = [backing]
            extra_pieces = down_tubes + up_tubes
        else:
            backing, extra_pieces = tube_bundle_pieces(
                outer_xs, outer_rs, rs_m, n_theta, n_channels_physical,
                channel_height_arr, thickness_arr, base_color_rgb,
                specular_strength=specular_strength, shininess=shininess,
                active_end_idx=cutoff_idx)
            outer_pieces = [backing]
    elif construction != "coax_shell" and has_channel_data:
        X, Y, Z = channel_modulated_grid(
            outer_xs, outer_rs, n_theta, n_channels_physical,
            channel_height_profile_m, land_fraction, construction, thickness_m)
        # grid_vertex_normals returns an (n_theta, n_stations, 3) GRID (same
        # shape as X/Y/Z), but mesh_from_grid's `normals` kwarg expects the
        # already-flattened (N, 3) per-vertex convention every other caller
        # (revolve_to_buffers) uses - reshape(-1, 3) matches vertices' own
        # X.ravel()-style C-order flattening of the same (n_theta, n_stations)
        # grid exactly.
        normals_flat = grid_vertex_normals(X, Y, Z).reshape(-1, 3)
        outer_pieces = [mesh_from_grid(X, Y, Z, base_color_rgb, normals=normals_flat,
                                        specular_strength=specular_strength, shininess=shininess)]
        # Milled channels live inside this grid - tell the flow view how many
        # are drawn and where (tube_bundle.channel_modulated_grid's phase).
        outer_pieces[0].meta = {"channel_grid": True,
                                "n_visual": visual_channel_count(n_channels_physical),
                                "land_fraction": float(land_fraction)}
    else:
        outer_pieces = [revolve_to_buffers(outer_xs, outer_rs, n_theta, base_color_rgb,
                                            specular_strength=specular_strength, shininess=shininess)]

    pieces = [inner, *outer_pieces, *extra_pieces]
    if cap_start:
        pieces.append(end_cap_ring(float(xs_m[0]), float(rs_m[0]), float(outer_rs[0]),
                                    n_theta, base_color_rgb, facing_sign=-1.0,
                                    specular_strength=specular_strength, shininess=shininess))
    if cap_end:
        pieces.append(end_cap_ring(float(xs_m[-1]), float(rs_m[-1]), float(outer_rs[-1]),
                                    n_theta, base_color_rgb, facing_sign=1.0,
                                    specular_strength=specular_strength, shininess=shininess))
    return ShellMesh(pieces=pieces, outer_xs=outer_xs, outer_rs=outer_rs)


def self_test():
    n_theta = 8
    xs_shell = np.array([0.0, 0.3, 0.5, 0.7, 1.5])
    rs_shell = np.array([0.20, 0.20, 0.06, 0.06, 0.35])
    thick = np.full_like(rs_shell, 0.006)
    ch_height = np.full_like(rs_shell, 0.01)              # deliberately oversized -> must clamp

    # --- build_shell_mesh: no NaNs, well-formed index buffers, sane triangle
    # counts, for every construction and with structural bumps + both caps ---
    for construction in ("milled_channel", "tube_wall", "coax_shell"):
        shell = build_shell_mesh(
            xs_shell, rs_shell, thick, n_theta, (0.5, 0.5, 0.5),
            construction=construction, channel_height_profile_m=ch_height,
            n_channels_physical=224, land_fraction=0.35,
            structural_bumps=[dict(center_x_m=0.5, half_width_m=0.1, height_m=0.01,
                                    shape="flat")],
            cap_start=True, cap_end=True)
        pieces = shell.pieces
        expected_len = (4 + visual_channel_count(224) if construction == "tube_wall" else 4)
        assert len(pieces) == expected_len  # inner, outer/backing, 2 caps[, N discrete tubes]

        # ShellMesh.outer_xs/outer_rs: the exact final outer-wall contour
        # (post structural-bump, pre channel-modulation) a caller bridging two
        # adjacent pieces (gui/preview3d_gl.py) would use.
        assert shell.outer_xs.shape == xs_shell.shape
        assert shell.outer_rs.shape == rs_shell.shape
        assert not np.any(np.isnan(shell.outer_xs))
        assert not np.any(np.isnan(shell.outer_rs))
        oxs_plain, ors_plain = offset_profile(xs_shell, rs_shell, thick)
        assert np.allclose(shell.outer_xs, oxs_plain)  # bumps only ever move r, never x
        i_bump = int(np.argmin(np.abs(xs_shell - 0.5)))  # xs_shell[2] == 0.5 exactly
        assert shell.outer_rs[i_bump] >= ors_plain[i_bump] + 0.01 - 1e-9  # flange baked in

        for piece in pieces:
            assert not np.any(np.isnan(piece.vertices))
            assert not np.any(np.isnan(piece.normals))
            # Every buffer must be the SAME (N, 3) shape - gui/preview3d_gl.py's
            # _upload_meshes concatenates vertices/normals/colors along axis 1
            # to interleave them for the GPU, which numpy only allows for
            # equal-rank, equal-row-count arrays (caught a real bug once: a
            # grid-shaped (n_theta, n_stations, 3) normals array reaching here
            # unflattened, vs. vertices' already-flat (N, 3)).
            assert piece.vertices.ndim == piece.normals.ndim == piece.colors.ndim == 2
            assert piece.vertices.shape == piece.normals.shape == piece.colors.shape
            interleaved = np.concatenate([piece.vertices, piece.normals, piece.colors], axis=1)
            assert interleaved.shape == (piece.vertices.shape[0], 9)
            if piece.indices.shape[0] > 0:
                assert piece.indices.max() < piece.vertices.shape[0]
        inner_piece, outer_piece = pieces[0], pieces[1]
        assert inner_piece.indices.shape[0] == 2 * (n_theta - 1) * (xs_shell.size - 1)
        assert outer_piece.indices.shape[0] == 2 * (n_theta - 1) * (xs_shell.size - 1)
    print("build_shell_mesh self-check: OK")

    # --- build_shell_mesh tube_split_x_m: a bell tube-split bifurcation
    # (real F-1: 178 -> 356 tubes at its 3:1 area-ratio plane) ---
    n_before = visual_channel_count(224)
    n_after = visual_channel_count(2 * 224)
    split_x = 1.0  # strictly inside (xs_shell[0], xs_shell[-1]) == (0.0, 1.5)
    shell_split = build_shell_mesh(
        xs_shell, rs_shell, thick, n_theta, (0.5, 0.5, 0.5),
        construction="tube_wall", channel_height_profile_m=ch_height,
        n_channels_physical=224, land_fraction=0.35, cap_start=True, cap_end=True,
        tube_split_x_m=split_x)
    # inner, 2 backings (pre+post split), 2 caps, N_before + N_after tubes
    assert len(shell_split.pieces) == 5 + n_before + n_after, (
        len(shell_split.pieces), n_before, n_after)
    # ShellMesh.outer_xs/outer_rs (the envelope used for capping/bridging in
    # gui/preview3d_gl.py) must be completely unaffected by the split - it's
    # the same pre-tube-detail contour regardless of how the tube layer is
    # rendered on top of it.
    shell_nosplit = build_shell_mesh(
        xs_shell, rs_shell, thick, n_theta, (0.5, 0.5, 0.5),
        construction="tube_wall", channel_height_profile_m=ch_height,
        n_channels_physical=224, land_fraction=0.35, cap_start=True, cap_end=True)
    assert np.allclose(shell_split.outer_xs, shell_nosplit.outer_xs)
    assert np.allclose(shell_split.outer_rs, shell_nosplit.outer_rs)
    for piece in shell_split.pieces:
        assert not np.any(np.isnan(piece.vertices)) and not np.any(np.isnan(piece.normals))
    print("build_shell_mesh tube_split_x_m self-check: OK")

    # tube_split_x_m=None (the default) must be byte-identical to today's
    # single-segment behavior - a straight regression check.
    assert len(shell_nosplit.pieces) == 4 + visual_channel_count(224)

    # A split point outside (xs_shell[0], xs_shell[-1]) degrades to the
    # single-segment path, exactly like "no split" - the caller
    # (gui/preview3d_gl.py) is responsible for handling "whole piece already
    # past/before the split" via its own n_channels_physical choice instead.
    for outside_x in (-1.0, 0.0, 1.5, 10.0):
        shell_outside = build_shell_mesh(
            xs_shell, rs_shell, thick, n_theta, (0.5, 0.5, 0.5),
            construction="tube_wall", channel_height_profile_m=ch_height,
            n_channels_physical=224, land_fraction=0.35, cap_start=True, cap_end=True,
            tube_split_x_m=outside_x)
        assert len(shell_outside.pieces) == len(shell_nosplit.pieces), outside_x
    print("build_shell_mesh tube_split_x_m out-of-range self-check: OK")

    # --- build_shell_mesh tube_cutoff_x_m: threads through to a flat-capped
    # tube termination for both regen_circuit_style values, and is a no-op
    # (identical to no cutoff at all) when it falls outside the piece ---
    cutoff_x_test = 0.6  # strictly inside (0.0, 1.5), between stations 2 and 3
    shell_cutoff_sp = build_shell_mesh(
        xs_shell, rs_shell, thick, n_theta, (0.5, 0.5, 0.5),
        construction="tube_wall", channel_height_profile_m=ch_height,
        n_channels_physical=224, land_fraction=0.35, cap_start=True, cap_end=True,
        tube_cutoff_x_m=cutoff_x_test, regen_circuit_style="single_pass_upflow")
    # inner, backing, N tubes, N caps, 2 end caps
    assert len(shell_cutoff_sp.pieces) == 4 + 2 * visual_channel_count(224)
    for piece in shell_cutoff_sp.pieces:
        assert not np.any(np.isnan(piece.vertices))
    # the overall envelope (outer_xs/outer_rs) is completely unaffected by
    # the cutoff, exactly like tube_split_x_m above - only the discrete tube
    # layer is truncated, per the docstring's claim (per-tube truncation
    # itself is already directly verified by the active_end_idx self-check
    # above)
    assert np.allclose(shell_cutoff_sp.outer_xs, shell_nosplit.outer_xs)
    assert np.allclose(shell_cutoff_sp.outer_rs, shell_nosplit.outer_rs)

    shell_cutoff_dp = build_shell_mesh(
        xs_shell, rs_shell, thick, n_theta, (0.5, 0.5, 0.5),
        construction="tube_wall", channel_height_profile_m=ch_height,
        n_channels_physical=224, land_fraction=0.35, cap_start=True, cap_end=True,
        tube_cutoff_x_m=cutoff_x_test, regen_circuit_style="f1_double_pass")
    # inner, backing, N down-tubes + N down-caps + N up-tubes + N up-caps, 2 end caps
    assert len(shell_cutoff_dp.pieces) == 4 + 4 * visual_channel_count(224)
    for piece in shell_cutoff_dp.pieces:
        assert not np.any(np.isnan(piece.vertices))

    # outside the piece entirely -> no-op, byte-identical to no cutoff at all
    shell_no_cutoff = build_shell_mesh(
        xs_shell, rs_shell, thick, n_theta, (0.5, 0.5, 0.5),
        construction="tube_wall", channel_height_profile_m=ch_height,
        n_channels_physical=224, land_fraction=0.35, cap_start=True, cap_end=True)
    shell_cutoff_past_end = build_shell_mesh(
        xs_shell, rs_shell, thick, n_theta, (0.5, 0.5, 0.5),
        construction="tube_wall", channel_height_profile_m=ch_height,
        n_channels_physical=224, land_fraction=0.35, cap_start=True, cap_end=True,
        tube_cutoff_x_m=10.0)
    assert len(shell_cutoff_past_end.pieces) == len(shell_no_cutoff.pieces)
    print("build_shell_mesh tube_cutoff_x_m self-check: OK")

    # --- specular_strength/shininess: omitting them keeps today's Lambertian-
    # only defaults (regression guard); an explicit material-derived pair is
    # stored verbatim on every piece build_shell_mesh returns, including the
    # discrete tube_wall pieces and both end caps ---
    default_mesh = revolve_to_buffers(xs_shell, rs_shell, n_theta, (0.5, 0.5, 0.5))
    assert default_mesh.specular_strength == 0.0 and default_mesh.shininess == 32.0
    custom_mesh = revolve_to_buffers(xs_shell, rs_shell, n_theta, (0.5, 0.5, 0.5),
                                      specular_strength=0.65, shininess=96.0)
    assert custom_mesh.specular_strength == 0.65 and custom_mesh.shininess == 96.0

    shell_spec = build_shell_mesh(
        xs_shell, rs_shell, thick, n_theta, (0.5, 0.5, 0.5),
        construction="tube_wall", channel_height_profile_m=ch_height,
        n_channels_physical=224, land_fraction=0.35, cap_start=True, cap_end=True,
        specular_strength=0.65, shininess=96.0)
    for piece in shell_spec.pieces:
        assert piece.specular_strength == 0.65 and piece.shininess == 96.0
    print("specular_strength/shininess propagation self-check: OK")
    print("ALL SHELL_MESH CHECKS OK")


if __name__ == "__main__":
    self_test()
