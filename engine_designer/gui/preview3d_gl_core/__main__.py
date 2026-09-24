"""
Meta self-test for the preview3d_gl_core package: runs every submodule's own
self_test() in sequence and prints one combined pass banner, mirroring
physics/validate.py's existing multi-banner style. This is what
`python3 -m engine_designer.gui.preview3d_gl_core` runs - verify_all.sh's
existing line for this module needs no change.
"""
from . import profile_geometry
from . import mesh_primitives
from . import duct_meshes
from . import tube_bundle
from . import shell_mesh
from . import camera_color
from . import shading

if __name__ == "__main__":
    profile_geometry.self_test()
    mesh_primitives.self_test()
    duct_meshes.self_test()
    tube_bundle.self_test()
    shell_mesh.self_test()
    camera_color.self_test()
    shading.self_test()
    print("ALL PREVIEW3D_GL_CORE CHECKS OK")
