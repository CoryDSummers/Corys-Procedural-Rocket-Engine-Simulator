"""
Gimbal actuation - a real design choice with real precedent (RF's
`%gimbalRange` on `ModuleGimbal`), but no derivable formula: real gimbal
ranges cluster ~4-8 deg (up to ~11.5 deg for reusable high-performance
hydrolox engines like SSME/RS-68), but do NOT scale simply with thrust - a
huge kerolox booster (RD-170) and a small lander engine (LMDE) both commonly
use ~6 deg. Many small RCS/vernier-class real engines, and boosters that use
separate vernier chambers for TVC instead of gimballing the main chamber
(the RD-107/108 family), have NO gimbal module at all.

This module is just the plausibility band + a warn-only check - there is no
physics computation here, only a real research-derived typical range.
"""

GIMBAL_RANGE_TYPICAL_DEG = (2.0, 11.5)


def plausibility_warning(gimbal_mode, gimbal_range_deg):
    """None if not in "custom" mode, or if the range is within the typical
    band; otherwise a human-readable warning string (never blocks)."""
    if gimbal_mode != "custom":
        return None
    lo, hi = GIMBAL_RANGE_TYPICAL_DEG
    if not (lo <= gimbal_range_deg <= hi):
        return (f"Custom gimbal range {gimbal_range_deg:.1f} deg is outside the "
                f"typical {lo:.1f}-{hi:.1f} deg band real gimballed engines use "
                f"(note: real gimbal range doesn't scale simply with thrust - a "
                f"large booster and a small lander engine commonly use the same "
                f"~6 deg). Consider 'ungimballed' instead if this is meant to be "
                f"a fixed/vernier-TVC design.")
    return None
