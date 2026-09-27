"""
Background execution for the GUI, so the Tk thread never blocks on physics.

Two runners, both free of any Tk/OpenGL import (headlessly self-tested here,
`python3 -m engine_designer.gui.async_compute`); gui/app.py polls them from a
`root.after` loop and applies whatever has finished on the Tk thread:

- ComputeWorker: ONE daemon thread running submitted callables (the design's
  compute(), optionally the 3D mesh build) with a latest-wins slot per job
  KIND - a burst of edits while a solve is running collapses to "finish the
  running one, then solve the newest", never a queue of stale solves. A
  thread, not a process: a compute() result is a large nested dict that would
  cost real time to pickle back, and compute() only reads its (snapshotted)
  design and module-level lru_caches (thread-safe), so it runs safely off the
  Tk thread. The GIL's 5 ms switch interval keeps Tk responsive meanwhile.

- MrSweepRunner: the Combustion Chamber tab's Isp-vs-MR sweep
  (mixture_ratio.isp_vs_mr_curve = 25 FULL compute()s, 10-57 s serially on
  real designs) farmed out point-by-point to a persistent spawn-context
  ProcessPoolExecutor - true parallelism past the GIL, and each point is a
  pickled ~4 KB design in and three floats out. Results are reassembled by
  mixture_ratio.curve_from_points, so the curve is bit-identical to the
  serial sweep. A new start() cancels the previous sweep's not-yet-started
  points (running ones finish - one compute, <~2.5 s - and are discarded).
  If a pool can't be started (or breaks), the same points run on a one-thread
  ThreadPoolExecutor instead: same semantics, just serial.
"""
import concurrent.futures as cf
import multiprocessing
import os
import queue
import threading
import time
from collections import namedtuple
from concurrent.futures.process import BrokenProcessPool

from ..physics import combustion, mixture_ratio

# One finished ComputeWorker job. ok=False -> value is the raised exception.
JobResult = namedtuple("JobResult", "kind gen ok value elapsed_s")

# One MrSweepRunner.poll() snapshot. curve/error are set only on the final
# poll of a sweep (done == total), after which the runner is idle again.
SweepStatus = namedtuple("SweepStatus", "gen done total curve error")

# Kinds run in this order when several are pending (a fresh solve outranks a
# mesh rebuild of the result it is about to replace).
_KIND_PRIORITY = ("compute", "mesh")


class ComputeWorker:
    def __init__(self):
        self._cv = threading.Condition()
        self._pending = {}          # kind -> (gen, fn); latest submit per kind wins
        self._running = None        # (kind, gen) of the job in flight
        self._closed = False
        self._results = queue.Queue()
        self._thread = threading.Thread(target=self._run, name="engine-compute", daemon=True)
        self._thread.start()

    def submit(self, kind, gen, fn):
        """Queue fn() under `kind`, replacing any not-yet-started job of that kind."""
        with self._cv:
            self._pending[kind] = (gen, fn)
            self._cv.notify()

    def discard(self, kind):
        """Drop a not-yet-started job of `kind` (a running one still finishes)."""
        with self._cv:
            self._pending.pop(kind, None)

    @property
    def busy(self):
        with self._cv:
            return bool(self._pending) or self._running is not None

    def running(self):
        """(kind, gen) of the job in flight, else None."""
        with self._cv:
            return self._running

    def poll(self):
        """Every JobResult finished since the last poll, oldest first (non-blocking).
        Check `busy` BEFORE polling to know the drain was complete: a job's
        result is queued before the worker clears its running flag."""
        out = []
        while True:
            try:
                out.append(self._results.get_nowait())
            except queue.Empty:
                return out

    def close(self):
        with self._cv:
            self._closed = True
            self._pending.clear()
            self._cv.notify()

    def _run(self):
        while True:
            with self._cv:
                while not self._pending and not self._closed:
                    self._cv.wait()
                if self._closed:
                    return
                kind = next((k for k in _KIND_PRIORITY if k in self._pending),
                            next(iter(self._pending)))
                gen, fn = self._pending.pop(kind)
                self._running = (kind, gen)
            t0 = time.perf_counter()
            try:
                value, ok = fn(), True
            except Exception as exc:        # delivered to the Tk side, never raised here
                value, ok = exc, False
            self._results.put(JobResult(kind, gen, ok, value, time.perf_counter() - t0))
            with self._cv:
                self._running = None


def default_pool_workers():
    """Leave one core for the Tk thread + the compute worker; cap at 7 (the
    25-point sweep gains little past that, and each worker is a full Python
    with numpy/matplotlib imported, ~100+ MB)."""
    return max(1, min((os.cpu_count() or 2) - 1, 7))


class MrSweepRunner:
    def __init__(self, n=25, max_workers=None, use_pool=True):
        self.n = n
        self._max_workers = max_workers or default_pool_workers()
        self._use_pool = use_pool
        self._executor = None
        self._gen = None
        self._design = None
        self._mrs = None
        self._futures = []
        self._single = False        # monopropellant / zero-width range: one isp_vs_mr_curve call

    @property
    def active(self):
        return self._gen is not None

    @property
    def gen(self):
        return self._gen

    def start(self, gen, design):
        """Sweep `design` (a snapshot the caller won't mutate) for generation
        `gen`, cancelling any sweep in progress."""
        self.cancel()
        self._gen, self._design = gen, design
        lo, hi = combustion.mr_bounds(design.propellant_pair)
        self._single = combustion.is_monopropellant(design.propellant_pair) or hi - lo < 1e-9
        self._mrs = None if self._single else mixture_ratio.sweep_mrs(design, self.n)
        self._submit()

    def cancel(self):
        for f in self._futures:
            f.cancel()
        self._futures = []
        self._gen = self._design = self._mrs = None

    def poll(self):
        """SweepStatus for the active sweep, or None when idle. The final
        (done == total) status carries the curve (or the error) and returns the
        runner to idle."""
        if self._gen is None:
            return None
        total = len(self._futures)
        done = sum(f.done() for f in self._futures)
        if done < total:
            return SweepStatus(self._gen, done, total, None, None)
        gen = self._gen
        try:
            points = [f.result() for f in self._futures]
        except BrokenProcessPool:
            # A worker process died (OOM killer, ...): retire the pool and
            # redo this sweep serially rather than leave the label hanging.
            self._retire_executor(use_pool=False)
            self._submit()
            return SweepStatus(gen, 0, len(self._futures), None, None)
        except Exception as exc:
            self.cancel()
            return SweepStatus(gen, total, total, None, exc)
        curve = points[0] if self._single else mixture_ratio.curve_from_points(self._mrs, points)
        self.cancel()
        return SweepStatus(gen, total, total, curve, None)

    def shutdown(self):
        self.cancel()
        self._retire_executor(use_pool=self._use_pool)

    # --- internals ---
    def _submit(self):
        for _attempt in range(2):
            ex = self._ensure_executor()
            try:
                if self._single:
                    self._futures = [ex.submit(mixture_ratio.isp_vs_mr_curve, self._design)]
                else:
                    self._futures = [ex.submit(mixture_ratio.sweep_point, self._design, mr)
                                     for mr in self._mrs]
                return
            except (BrokenProcessPool, RuntimeError, OSError):
                self._retire_executor(use_pool=False)   # retry once on the thread fallback
        raise RuntimeError("MR sweep: no executor could accept work")

    def _ensure_executor(self):
        if self._executor is None and self._use_pool:
            try:
                self._executor = cf.ProcessPoolExecutor(
                    max_workers=self._max_workers,
                    # spawn, not fork: forking a process that holds a Tk
                    # interpreter, a GL context and running threads is unsafe.
                    mp_context=multiprocessing.get_context("spawn"))
            except (OSError, ValueError, NotImplementedError):
                self._use_pool = False
        if self._executor is None:
            self._executor = cf.ThreadPoolExecutor(max_workers=1, thread_name_prefix="mr-sweep")
        return self._executor

    def _retire_executor(self, use_pool):
        if self._executor is not None:
            self._executor.shutdown(wait=False, cancel_futures=True)
        self._executor = None
        self._use_pool = use_pool


def _drain(runner, timeout_s=300.0):
    t_end = time.monotonic() + timeout_s
    last = None
    while time.monotonic() < t_end:
        st = runner.poll()
        if st is None:
            return last
        last = st
        if st.curve is not None or st.error is not None:
            return st
        time.sleep(0.02)
    raise TimeoutError("sweep did not finish")


def self_test():
    from pathlib import Path

    from ..physics.design import EngineDesign
    from . import project_io

    # --- ComputeWorker: latest-wins per kind, exceptions delivered ---
    w = ComputeWorker()
    gate = threading.Event()
    w.submit("compute", 1, lambda: (gate.wait(5), "one")[1])
    while w.running() is None:
        time.sleep(0.001)
    for g in (2, 3, 4):                  # queued behind gen 1 -> only 4 survives
        w.submit("compute", g, lambda g=g: f"gen{g}")
    w.submit("mesh", 4, lambda: "mesh4")
    gate.set()
    while w.busy:
        time.sleep(0.005)
    got = [(r.kind, r.gen, r.value) for r in w.poll()]
    assert got == [("compute", 1, "one"), ("compute", 4, "gen4"), ("mesh", 4, "mesh4")], got
    w.submit("compute", 5, lambda: 1 / 0)
    while w.busy:
        time.sleep(0.005)
    (r,) = w.poll()
    assert not r.ok and isinstance(r.value, ZeroDivisionError), r
    w.discard("compute")
    w.close()
    print("ComputeWorker: latest-wins coalescing + exception delivery OK")

    # --- MrSweepRunner: bit-identical to the serial sweep, pool and fallback ---
    corpus = Path(__file__).resolve().parents[1] / "validation_engines" / "engines"
    d = project_io.load_design(corpus / "LMAE.json")      # ~10 ms per compute
    ref = mixture_ratio.isp_vs_mr_curve(d, n=25)
    for use_pool in (True, False):
        runner = MrSweepRunner(n=25, max_workers=2, use_pool=use_pool)
        runner.start(1, d)
        st = _drain(runner)
        assert st.gen == 1 and st.error is None and st.done == st.total == 25, st
        assert st.curve == ref, "pooled sweep differs from mixture_ratio.isp_vs_mr_curve"
        assert runner.poll() is None and not runner.active
        # A restart supersedes: only the newest generation ever reports.
        runner.start(2, d)
        runner.start(3, EngineDesign(propellant_pair="Hydrazine", cycle="pressure_fed",
                                     injector_type="catalyst_bed"))
        st = _drain(runner)
        assert st.gen == 3 and st.total == 1 and st.curve["is_monopropellant"], st
        runner.shutdown()
        mode = "process pool" if use_pool else "thread fallback"
        print(f"MrSweepRunner ({mode}): curve bit-identical to isp_vs_mr_curve "
              f"(peak MR {ref['peak_mr']:.3f}), restart supersedes, mono = 1 point OK")
    print("async_compute.py self-checks: OK")


if __name__ == "__main__":
    self_test()
