# GUI responsiveness: background compute + progress bar (2026-09-26)

Branch `gui/async-compute` (off `origin/main` 6cc04cb), draft PR. Approved plan copy.

## Why
The GUI froze on load and on value changes. Measured per recompute:

| step | typical | worst |
|---|---|---|
| `EngineDesign.compute()` | 0.4–1.4 s | 2.3 s (J-2) |
| GL mesh build (3D tab visible) | 0.2–0.6 s | 1.2 s |
| Isp-vs-MR sweep, 25 computes (Combustion Chamber tab visible) | 10–27 s | 57 s (J-2) |

The Combustion Chamber tab is the first input tab, so startup, every Load, and every change on
that tab paid the sweep on the Tk thread. Cory's call: keep the sweep automatic, but run it in
parallel on a process pool, cancelled on each change.

## Checklist
- [x] C1 `physics/mixture_ratio.py`: `sweep_mrs` / `sweep_point` / `curve_from_points`.
      `isp_vs_mr_curve` is composed from them, output unchanged.
- [x] C2 `gui/async_compute.py`: `ComputeWorker` (thread, latest-wins per kind) +
      `MrSweepRunner` (spawn process pool, thread fallback) + self-test (pooled == serial,
      bit-identical).
- [x] C3 `gui/app.py`:
      - async `recompute()`, `_poll_workers`, `_apply_result` (the old post-solve body);
      - `recompute_now` / `ensure_current_result` (used by Export + the Shape Lab);
      - status bar + progress bar;
      - async MR label / Optimize MR;
      - GL mesh built on the worker on a 3D tab switch;
      - `_on_quit` shuts the pool down.
- [x] C4 `gui/preview3d_gl.py`: `mesh_build_job()` + `update_result(prebuilt=)`.
- [x] C5 `verify_all.sh`, CLAUDE.md, README responsiveness note.
- [ ] Cory: run the real GUI.
  - Load J-2 / RS-29 and drag sliders on the Combustion Chamber / Cooling tabs.
  - Switch to the 3D tab.
  - Try Optimize MR mid-sweep and Export mid-solve.
  - Open the Shape Lab.
  - Quit, and confirm no python workers are left.

## Notes
- No `$DISPLAY` / Xvfb on the dev machine, so the Tk side is syntax / import / code-reviewed
  only.
- Speed-up on the sweep is ~3.7x on a 4-core / 8-thread Xeon (every J-2 point costs ~2.1 s,
  flat across MR). It scales with physical cores.
- Spawned workers re-import the launching `__main__` (`engine_designer.gui.app`). That is
  harmless because of the `if __name__ == "__main__"` guard, but costs ~1 s on the first sweep.
