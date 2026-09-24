"""Run the whole validation suite: python3 -m engine_designer.physics.validate

Runs EVERY check (the old single-file version chained them with `and`, so the
first failure silently skipped all later checks), then prints a failure summary
and exits nonzero if any check failed or raised."""
import traceback

from engine_designer.physics.validate import ALL_CHECKS

if __name__ == "__main__":
    failed = []
    for check in ALL_CHECKS:
        try:
            if not check():
                failed.append(check.__name__)
        except Exception:  # a crash is a failure, but keep running the rest
            traceback.print_exc()
            failed.append(f"{check.__name__} (raised)")
    if failed:
        print(f"\n*** {len(failed)} of {len(ALL_CHECKS)} VALIDATION CHECK(S) FAILED: "
              + ", ".join(failed))
    raise SystemExit(1 if failed else 0)
