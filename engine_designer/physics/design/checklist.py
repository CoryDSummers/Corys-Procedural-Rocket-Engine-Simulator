"""The one checklist/warnings recorder shared by every compute stage."""


def _check(checklist, warnings, category, name, passed, fail_detail, pass_detail="OK"):
    """Record one design check into BOTH the flat `warnings` list (failures
    only - exact legacy content/order, consumed by gui/app.py's Warnings box
    AND export/cfg_writer.py's .cfg header comments) and the new structured
    `checklist` list (every check, pass or fail - consumed only by the GUI's
    Checklist tab). One call site keeps the two from ever silently drifting
    apart."""
    checklist.append({"category": category, "name": name, "passed": passed,
                       "detail": fail_detail if not passed else pass_detail})
    if not passed:
        warnings.append(fail_detail)
