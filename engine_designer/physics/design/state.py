"""Per-pass shared state for EngineDesign._compute_pass.

Each compute stage (design/*_stage.py) receives the design (`self`) and one
PassState `s`. A value produced by one stage and read by a later one lives on
`s` (e.g. `s.mdot`, `s.q_profile_w_m2`); values used inside a single stage stay
plain locals there. Created fresh for every pass, so nothing leaks between the
two passes of a pump-connected plumbing design."""


class PassState:
    """Attribute bag for cross-stage values of one compute pass."""
