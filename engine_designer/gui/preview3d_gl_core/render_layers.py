"""
Render-layer bookkeeping for the OpenGL 3D preview's multi-pass pipeline:
which layer (opaque / translucent) each MeshBuffers piece draws in, batching
many small pieces into a few GL buffers, back-to-front ordering for the
translucent pass, and a numpy reference of the shader's rim-alpha formula.
Pure numpy, no OpenGL/Tk import - gui/preview3d_gl.py is the only consumer
that touches GL, and it just uploads/draws what build_batches hands it.

Pass structure (preview3d_gl.EnginePreviewGLFrame.redraw):
  1. LAYER_OPAQUE      - depth write on, blend off (the only pass before X-ray).
  2. LAYER_TRANSLUCENT - depth write off, alpha blend on, batches sorted back
                         to front, each drawn twice (fragments facing away from
                         the eye, then facing it - split in the shader on
                         sign(dot(N, V)), so it doesn't depend on triangle
                         winding, which isn't consistent across the builders).
  Between them, LAYER_FLOW - the propellant-flow visualization (pieces with
  role FLOW_ROLE, built by gui/mesh_builder.build_flow_pieces): depth write
  on, no blend, drawn unlit/emissive. Flow pieces are always built; when the
  Flow toggle is off they're simply skipped here (no rebuild).

X-ray is purely a render-state choice: pieces whose `role` is in XRAY_ROLES
move to LAYER_TRANSLUCENT when it's on; nothing is rebuilt.
"""
from dataclasses import dataclass

import numpy as np

from .mesh_primitives import MeshBuffers

LAYER_OPAQUE = "opaque"
LAYER_TRANSLUCENT = "translucent"
LAYER_FLOW = "flow"
FLOW_ROLE = "flow"

#: Draw order of the layers within one frame.
LAYER_ORDER = (LAYER_OPAQUE, LAYER_FLOW, LAYER_TRANSLUCENT)

#: Piece roles (MeshBuffers.role, stamped by gui/mesh_builder.build_mesh_data)
#: that turn translucent in X-ray mode. "" = untagged (e.g. the Shape Lab's
#: synthetic scenes) - treated as structural too. Cosmetic only.
XRAY_ROLES = frozenset({"", "wall", "injector_head", "cover", "hatband",
                        "flange", "turbopump"})

#: Face-on opacity of temperature-tinted coolant hardware (tubes, channel
#: jacket, rings, plumbing) while the Flow view is on - tinted "glass" round
#: the opaque streams inside. Cosmetic only.
FLOW_TINT_OPACITY = 0.35

#: Default X-ray opacity (face-on alpha) and rim exponent - cosmetic only.
XRAY_DEFAULT_OPACITY = 0.18
XRAY_RIM_POWER = 2.0


@dataclass
class RenderBatch:
    """One merged GL upload: every piece sharing a layer/role/material."""
    layer: str
    buffers: MeshBuffers
    centroid: np.ndarray  # (3,) vertex mean - back-to-front sort key
    alpha: float = None   # translucent face-on opacity; None = the global X-ray opacity


def layer_for(piece, xray_enabled, flow_enabled=False):
    """Which layer this piece draws in, or None = not drawn (a flow piece
    while the Flow toggle is off)."""
    if piece.role == FLOW_ROLE:
        return LAYER_FLOW if flow_enabled else None
    if flow_enabled and piece.flow_colors is not None:
        return LAYER_TRANSLUCENT        # temperature-tinted coolant hardware
    if xray_enabled and piece.role in XRAY_ROLES:
        return LAYER_TRANSLUCENT
    return LAYER_OPAQUE


def merge_buffers(pieces):
    """
    Concatenate pieces into one MeshBuffers, offsetting each piece's indices
    by the running vertex count. Specular/shininess/role come from the first
    piece - callers group by those first (build_batches does).
    """
    pieces = [p for p in pieces if p.vertices.shape[0] > 0]
    if not pieces:
        empty = np.zeros((0, 3), dtype=np.float32)
        return MeshBuffers(empty, empty, empty, np.zeros((0, 3), dtype=np.uint32))
    offsets = np.cumsum([0] + [p.vertices.shape[0] for p in pieces[:-1]])
    first = pieces[0]
    extra = {}
    for name in ("scalar", "flow_s"):   # carried only when every piece has it
        if all(getattr(p, name) is not None for p in pieces):
            extra[name] = np.concatenate([getattr(p, name) for p in pieces]).astype(np.float32)
    return MeshBuffers(
        vertices=np.concatenate([p.vertices for p in pieces]).astype(np.float32),
        normals=np.concatenate([p.normals for p in pieces]).astype(np.float32),
        colors=np.concatenate([p.colors for p in pieces]).astype(np.float32),
        indices=np.concatenate([np.asarray(p.indices, dtype=np.int64).reshape(-1, 3) + off
                                for p, off in zip(pieces, offsets)]).astype(np.uint32),
        specular_strength=first.specular_strength, shininess=first.shininess,
        role=first.role, **extra)


def build_batches(pieces, xray_enabled, flow_enabled=False):
    """
    Group pieces by (layer, role, specular_strength, shininess) and merge each
    group into one RenderBatch - collapses e.g. a discrete tube bundle's
    hundreds of pieces (hundreds of glDrawElements calls) into one. Pieces
    with no triangles are dropped. Batches come back in LAYER_ORDER, groups
    within a layer in first-seen order.
    """
    groups = {}
    for piece in pieces:
        if piece.vertices.shape[0] == 0 or np.asarray(piece.indices).size == 0:
            continue
        layer = layer_for(piece, xray_enabled, flow_enabled)
        if layer is None:
            continue
        tinted = flow_enabled and piece.flow_colors is not None and piece.role != FLOW_ROLE
        if tinted:
            piece = MeshBuffers(piece.vertices, piece.normals, piece.flow_colors, piece.indices,
                                specular_strength=piece.specular_strength,
                                shininess=piece.shininess, role=piece.role)
        key = (layer, piece.role,
               float(piece.specular_strength), float(piece.shininess), tinted)
        groups.setdefault(key, []).append(piece)
    batches = []
    for layer in LAYER_ORDER:
        for key, group in groups.items():
            if key[0] != layer:
                continue
            merged = merge_buffers(group)
            batches.append(RenderBatch(layer=layer, buffers=merged,
                                       centroid=merged.vertices.mean(axis=0),
                                       alpha=FLOW_TINT_OPACITY if key[4] else None))
    return batches


def back_to_front_order(centroids, eye):
    """Indices into `centroids` (N, 3), farthest from `eye` first."""
    centroids = np.asarray(centroids, dtype=float).reshape(-1, 3)
    if centroids.shape[0] == 0:
        return np.zeros(0, dtype=int)
    dist = np.linalg.norm(centroids - np.asarray(eye, dtype=float), axis=1)
    return np.argsort(-dist, kind="stable")


def rim_alpha(n_dot_v, base_alpha, rim_power=XRAY_RIM_POWER):
    """
    Numpy reference of the fragment shader's X-ray alpha: `base_alpha` where
    the surface faces the eye, rising to 1 at grazing angles (silhouettes stay
    readable while faces go clear). Must match _FRAGMENT_SHADER in
    gui/preview3d_gl.py.
    """
    grazing = 1.0 - np.clip(np.abs(n_dot_v), 0.0, 1.0)
    return base_alpha + (1.0 - base_alpha) * grazing ** rim_power


def self_test():
    def _quad(x0, role="", spec=0.0, shin=32.0):
        v = np.array([[x0, 0, 0], [x0 + 1, 0, 0], [x0 + 1, 1, 0], [x0, 1, 0]], dtype=np.float32)
        n = np.tile(np.array([0, 0, 1], dtype=np.float32), (4, 1))
        c = np.full((4, 3), 0.5, dtype=np.float32)
        i = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.uint32)
        return MeshBuffers(v, n, c, i, specular_strength=spec, shininess=shin, role=role)

    # merge: vertex count conserved, indices offset into the right piece
    a, b = _quad(0.0), _quad(5.0)
    m = merge_buffers([a, b])
    assert m.vertices.shape == (8, 3) and m.indices.shape == (4, 3)
    assert m.indices.max() == 7 and m.indices.dtype == np.uint32
    assert np.allclose(m.vertices[m.indices[2:]], b.vertices[b.indices])
    assert merge_buffers([]).vertices.shape == (0, 3)

    # 300 identical-material tubes collapse to one batch; another material stays separate
    tubes = [_quad(float(k), role="wall") for k in range(300)]
    pump = _quad(0.0, role="turbopump", spec=0.4, shin=64.0)
    empty = MeshBuffers(np.zeros((0, 3)), np.zeros((0, 3)), np.zeros((0, 3)),
                        np.zeros((0, 3), dtype=np.uint32), role="wall")
    off = build_batches(tubes + [pump, empty], xray_enabled=False)
    assert len(off) == 2 and all(bt.layer == LAYER_OPAQUE for bt in off)
    assert off[0].buffers.vertices.shape[0] == 1200
    on = build_batches(tubes + [pump], xray_enabled=True)
    assert all(bt.layer == LAYER_TRANSLUCENT for bt in on)
    # a role outside XRAY_ROLES stays opaque and is ordered first
    mixed = build_batches([_quad(0.0, role="wall"), _quad(1.0, role="flow_probe")], True)
    assert [bt.layer for bt in mixed] == [LAYER_OPAQUE, LAYER_TRANSLUCENT]
    # flow pieces: skipped while Flow is off, their own layer (drawn between) when on;
    # per-vertex scalar/flow_s survive the merge
    fl = [_quad(0.0, role=FLOW_ROLE), _quad(2.0, role=FLOW_ROLE)]
    for q in fl:
        q.scalar = np.full(4, 300.0, dtype=np.float32)
        q.flow_s = np.arange(4, dtype=np.float32)
    assert build_batches(fl + [_quad(0.0, role="wall")], True)[0].layer == LAYER_TRANSLUCENT
    assert len(build_batches(fl, True, flow_enabled=False)) == 0
    fb = build_batches(fl + [_quad(0.0, role="wall")], True, flow_enabled=True)
    assert [bt.layer for bt in fb] == [LAYER_FLOW, LAYER_TRANSLUCENT]
    assert fb[0].buffers.scalar.shape == (8,) and fb[0].buffers.flow_s.shape == (8,)
    assert fb[1].buffers.scalar is None
    # temperature-tinted hardware: untouched while Flow is off, translucent with
    # its tint colors + FLOW_TINT_OPACITY while it's on (even with X-ray off)
    tube = _quad(0.0, role="wall")
    tube.flow_colors = np.tile(np.array([[1.0, 0.0, 0.0]], dtype=np.float32), (4, 1))
    off_b = build_batches([tube], False)
    assert off_b[0].layer == LAYER_OPAQUE and np.allclose(off_b[0].buffers.colors, 0.5)
    on_b = build_batches([tube, _quad(1.0, role="wall")], False, flow_enabled=True)
    tb = [b for b in on_b if b.layer == LAYER_TRANSLUCENT]
    assert len(tb) == 1 and tb[0].alpha == FLOW_TINT_OPACITY
    assert np.allclose(tb[0].buffers.colors, [1.0, 0.0, 0.0])
    assert [b.layer for b in on_b if b is not tb[0]] == [LAYER_OPAQUE]
    assert np.allclose(tube.colors, 0.5), "source piece must not be mutated"

    # back-to-front
    order = back_to_front_order([[0, 0, 0], [10, 0, 0], [5, 0, 0]], eye=[-1, 0, 0])
    assert list(order) == [1, 2, 0]
    assert back_to_front_order([], eye=[0, 0, 0]).size == 0

    # rim alpha: face-on = base, grazing = 1, monotonic in between, sign-symmetric
    ndv = np.linspace(1.0, 0.0, 11)
    al = rim_alpha(ndv, 0.2)
    assert abs(al[0] - 0.2) < 1e-12 and abs(al[-1] - 1.0) < 1e-12
    assert np.all(np.diff(al) >= 0)
    assert np.allclose(rim_alpha(-ndv, 0.2), al)
    print("render_layers self-test: OK")


if __name__ == "__main__":
    self_test()
