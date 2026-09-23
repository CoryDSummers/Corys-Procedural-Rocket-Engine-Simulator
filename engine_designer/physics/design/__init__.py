"""
EngineDesign: the one object the GUI and the config exporter both talk to.
Takes the user's chosen inputs, calls the physics modules, and returns a
single results dict via compute(). No new physics is derived here - this
is composition + the documented engine-level assumption constants (the
same role /home/cory/ksp_config/sim/h4_report.py played for the H-4 report).
"""

# Package layout (split 2026-09-23 from the former single-file design.py, code moved
# verbatim). engine.py holds the EngineDesign dataclass; compute() runs the ordered
# stage functions in *_stage.py, sharing cross-stage values on a PassState (state.py).
from .checklist import _check  # noqa: F401
from .constants import (  # noqa: F401
    G0,
    PA_SEA_LEVEL,
    JACKET_DP_PA,
    JACKET_DP_FRACTION_BY_COOLING_METHOD,
    LINE_LOSS_PA,
    TANK_HEAD_PA,
    GG_ETA_TURBINE,
    GG_PRESSURE_RATIO,
    EXPANDER_TURBINE_PR,
    GG_GAS_PROPERTIES,
    GG_MIXTURE_RATIO,
    GG_DUMP_ISP_FRACTION,
    TAP_OFF_DUMP_ISP_FRACTION,
    TAP_OFF_TEMP_FRACTION,
    TAP_OFF_TURBINE_LIMIT_K,
    TAP_OFF_PRESSURE_RATIO,
    SEPARATION_K,
    CONVERGENT_HALF_ANGLE_DEG,
    ETA_CSTAR_CEILING,
    FILM_COOLING_ETA_CSTAR_PENALTY,
    FILM_TOTAL_FRACTION_WARN,
    PEAK_WALL_THROAT_ZONE_EPS,
    REGEN_CIRCUIT_STYLE_BY_TOPOLOGY,
    COOLANT_INLET_TEMP_K,
    CONTRACTION_RATIO_TYPICAL,
    LSTAR_TYPICAL_M,
    GG_FLOW_FRACTION_TYPICAL_MAX,
    PRESSURE_FED_PC_TYPICAL_MAX_PA,
    BASE_RATED_BURN_TIME_S,
    RATED_TIME_MARGIN_MULT_MIN,
    RATED_TIME_MARGIN_MULT_MAX,
    REGEN_HOT_WALL_THICKNESS_M,
    FATIGUE_CYCLE_MARGIN,
    FATIGUE_CYCLE_FLOOR,
)
from .engine import EngineDesign  # noqa: F401
from .state import PassState  # noqa: F401
