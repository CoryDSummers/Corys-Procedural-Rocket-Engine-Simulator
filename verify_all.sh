#!/usr/bin/env bash
# Token-cheap runner for the engine_designer verification suite documented in
# CLAUDE.md. Runs every module self-test, keeps full stdout/stderr in
# verify_output.log, and only prints a PASS/FAIL line per module plus the full
# output of any module that fails. Exit code is nonzero if anything failed.
#
# Usage: ./verify_all.sh   (run from the repo root, same as the manual commands)

set -u
cd "$(dirname "${BASH_SOURCE[0]}")"

LOG=verify_output.log
: > "$LOG"

MODULES=(
  engine_designer.physics.isentropic
  engine_designer.physics.nozzle_shapes
  engine_designer.physics.geometry3d
  engine_designer.physics.combustion
  engine_designer.physics.thermo_tables   # baked Cantera/CoolProp property tables load + sanity
  engine_designer.physics.mixture_ratio
  engine_designer.physics.cooling
  engine_designer.physics.combustion_stability
  engine_designer.physics.injectors
  engine_designer.physics.manifold
  engine_designer.physics.plumbing
  engine_designer.physics.mass_model
  engine_designer.physics.hatbands
  engine_designer.physics.staged_combustion
  engine_designer.physics.turbine_exhaust   # GG/tap-off exhaust: back pressure, exhaust Isp, modes
  engine_designer.physics.electric_pump
  engine_designer.physics.reliability
  engine_designer.physics.cost_model
  engine_designer.physics.turbopump_materials
  engine_designer.physics.turbopump_efficiency
  engine_designer.physics.inducer             # suction: Brumfield / NPSHr / TSH vs SP-8107 Table II
  engine_designer.physics.turbopump_sizing
  engine_designer.physics.validate
  engine_designer.physics.flow_network
  engine_designer.catalog.build_catalog
  engine_designer.catalog.build_roengines_models
  engine_designer.export.cfg_writer
  engine_designer.gui.schematic
  engine_designer.gui.preview3d
  engine_designer.gui.preview3d_gl_core
  engine_designer.gui.mesh_builder
  engine_designer.gui.shape_lab_geometry
  engine_designer.gui.injector_face
  engine_designer.gui.turbopump_diagram
  engine_designer.gui.project_io
  engine_designer.validation_engines.run_corpus   # default --check: every corpus project
                                                  # bit-identical to validation_engines/golden/
)

fail=0
for m in "${MODULES[@]}"; do
  {
    echo "===== $m ====="
  } >> "$LOG"
  if python3 -m "$m" >> "$LOG" 2>&1; then
    echo "PASS  $m"
  else
    echo "FAIL  $m"
    fail=1
    echo "--- output for $m ---"
    awk -v m="===== $m =====" 'p{print} $0==m{p=1}' "$LOG" | tail -n +2
    echo "--- end output ---"
  fi
done

for f in gui/app.py gui/preview3d_gl.py gui/shape_lab.py gui/flow_legend.py; do
  path="engine_designer/$f"
  if python3 -c "import ast; ast.parse(open('$path').read())" >> "$LOG" 2>&1; then
    echo "PASS  syntax-check $path"
  else
    echo "FAIL  syntax-check $path"
    fail=1
  fi
done

if [ "$fail" -eq 0 ]; then
  echo "ALL MODULES PASSED. Full log: $LOG"
else
  echo "ONE OR MORE MODULES FAILED. Full log: $LOG"
fi
exit "$fail"
