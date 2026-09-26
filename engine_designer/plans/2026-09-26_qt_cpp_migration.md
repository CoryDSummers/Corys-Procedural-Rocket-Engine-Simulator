# Qt / C++ migration — structure plan (2026-09-26)

A structure plan for moving `engine_designer/` from Python/Tkinter to a **Qt 6 C++**
application, to be hand-coded by Cory. This is a map and a phase checklist, not code.
Unticked boxes = not landed yet (same convention as the other `plans/*.md` files).

**Scope (Cory's call): GUI first, physics port planned in full.**
- **Stage A** — a native Qt/C++ GUI that *embeds the existing Python physics* through
  pybind11. Feature parity with `gui/app.py`, then Tk is retired.
- **Stage B** — the physics, export and schema migrations are ported to a standalone C++
  library behind the *same* backend interface, verified against the Python oracle, and
  then Python is dropped from the runtime (it stays as tooling).

This supersedes the 2026-09-14 "don't port to C++" decision. That decision was about
3D-preview goals, which the PyOpenGL preview has since met. This port is a deliberate
choice made for other reasons.

---

## 0. What exists today (survey numbers this plan is sized from)

| Area | Lines | Notes |
|---|---:|---|
| `gui/app.py` | 2,903 | One `EngineDesignerApp` class. 8 input tabs (Combustion Chamber, Cooling, Injectors, Engine Bell, Turbopump, Plumbing, Gimbal, Model) + 5 result tabs (2D Schematic, 3D Preview, Injector Face, Checklist, Turbopump). |
| `gui/mesh_builder.py` | 2,298 | Per-part mesh assembly. Pure numpy, no Tk/GL. |
| `gui/preview3d_gl_core/` | 4,950 | Pure-numpy mesh primitives, camera, colormaps, render-layer batching, **GLSL source strings** (`shading.py`). |
| `gui/preview3d_gl.py` | 734 | `EnginePreviewGLFrame(pyopengltk.OpenGLFrame)`: the GL widget shell. |
| `gui/shape_lab.py` + `shape_lab_geometry.py` | 746 + 438 | Shape Lab window + `PlumbingLabPanel`; scene geometry is pure numpy. |
| `gui/schematic.py`, `injector_face.py`, `turbopump_diagram.py` | 416 / 179 / 280 | matplotlib, each a `draw_x(ax, result)` function. |
| `gui/flow_legend.py`, `collapsible.py`, `project_io.py`, `preview3d.py` | 96 / 65 / 159 / 230 | Colorbar; collapsible frame; JSON save/load; matplotlib 3D fallback. |
| `physics/` (+ `cooling/`, `design/`) | ~19,000 | All computation. |
| `physics/validate/` | ~3,000 | Spot checks (28 `ALL ... OK` banners). |
| `export/cfg_writer.py` | 659 | RF `.cfg` text rendering. |
| `catalog/` | 360 | Build scripts + JSON loaders. |

**The one boundary between GUI and physics:**
```
EngineDesign  (dataclass, ~107 fields; to_dict()/from_dict() with schema_version migrations)
    │  .compute()
    ▼
result  (nested dict: 111 top-level keys, ~725 keys total; numpy arrays for contours/profiles)
```
`compute()` runs up to 6 open-cycle thrust-closure iterations. Each iteration is 1 or 2
passes (line loss / exhaust film feedback), and each pass is
`_compute_pass` = **17 ordered stage functions** sharing a `PassState` attribute bag
(~215 cross-stage fields).

**Numerical dependencies are light:** `scipy.optimize.brentq` (3 uses),
`scipy.interpolate.RegularGridInterpolator` (1, in `nozzle_shapes.py`'s Rao θ table), `np.interp` (19), plus `norm`,
`cross`, `cumsum`, `gradient`, `searchsorted` and `meshgrid`. No linear solves or ODE
integrators, so no Eigen/GSL/Boost dependency is needed.

**Oracles that already exist:** `validation_engines/run_corpus.py --check` (12 real
engines + 8 user designs vs `golden/`), `physics.validate`, a `__main__` self-test in
every physics module, and baked JSON property tables in `physics/property_data/`.

---

## 1. Goals and non-goals

**Goals**
1. A native Qt GUI with feature parity to the Tk app, including the 3D preview (PBR,
   X-ray, flow view, heat-flux view) and the Shape Lab plumbing editor.
2. A C++ physics library that reproduces the Python results within a stated tolerance
   (§9) on the whole validation corpus.
3. Keep every external contract unchanged: the project `.json` format and its
   `schema_version` migrations, the RF `.cfg` output text, and `catalog.json` /
   `roengines_models.json`.
4. Each step leaves a working app. You never have a half-Tk, half-Qt program with no
   runnable GUI.

**Non-goals (during the port)**
- No UI redesign. Rearranging tabs is fine. New features wait for parity.
- No physics changes made *in C++ first*. See the transition rules in §10.
- The Cantera/CoolProp table generator (`tools/property_tables/`), `build_catalog.py`,
  `build_roengines_models.py` and `build_corpus.py` stay Python. They are offline tooling
  that produces JSON, and C++ just reads that JSON.

---

## 2. Target stack

| Concern | Choice | Why |
|---|---|---|
| GUI toolkit | **Qt 6 LTS (6.5+ / 6.8), Qt Widgets** | Dense form-driven engineering UI. Widgets maps 1:1 onto the Tk layout, while QML would mean designing a new UI. |
| 3D | **`QOpenGLWidget` + `QOpenGLFunctions_3_3_Core`** | The existing GLSL (3.3-core-compatible PBR shader) ports verbatim. The widget's MSAA comes from `QSurfaceFormat::setSamples`. |
| 2D diagrams | **Custom `QPainter` widgets** on a shared `Canvas2D` base | The schematic, injector face and turbopump diagram are *drawings* (patches, lines, text), not charts, so no charting library is needed. |
| Build | **CMake ≥ 3.24**, C++20 | Qt 6's native build system. |
| Python embedding (Stage A) | **pybind11** (`pybind11::embed`) | Header-only, embeds the interpreter, and handles numpy ↔ C++ buffers. |
| JSON | **nlohmann/json** | Project files, property tables, catalog, and test fixtures. |
| Tests | **Catch2 v3** (or GoogleTest) + **Qt Test** for widgets | Catch2's `Approx`/`WithinRel` suits tolerance-based parity. |
| Dependency fetch | `FetchContent` for pybind11/nlohmann/Catch2. Qt from the system or the Qt online installer. | |

Nothing else is needed. In particular, don't add Eigen for the physics: a 60-line `Vec3`
plus the §8.1 numerics kit covers every numpy call the physics makes.

---

## 3. Repository layout

Add a new top-level directory next to `engine_designer/`. The Python package stays where
it is and keeps working the whole time.

```
engine_designer_qt/
├── CMakeLists.txt                 # top level: options ED_WITH_PYTHON (A), ED_NATIVE_PHYSICS (B)
├── cmake/                         # FindPython helpers, compiler warnings, sanitizers
├── resources/
│   ├── resources.qrc
│   ├── shaders/                   # pbr.vert, pbr.frag, background.vert/.frag, gizmo.*  (from shading.py)
│   └── icons/                     # checklist pass/warn/fail, toolbar
├── src/
│   ├── app/                       # main.cpp, MainWindow, menus/actions, settings
│   ├── model/                     # DesignModel, FieldSpec registry, ResultTree, Gates
│   ├── backend/                   # PhysicsBackend.h, PyBackend (A), NativeBackend (B), ComputeWorker
│   ├── widgets/                   # CollapsibleBox, LabeledSlider, FieldForm, ChecklistView
│   ├── views/                     # Canvas2D, SchematicView, InjectorFaceView, TurbopumpDiagramView, FlowLegend
│   ├── gl/                        # EngineGLView, Renderer, OrbitCamera, GpuMesh, ShaderLibrary, Gizmo
│   ├── mesh/                      # (A6) port of preview3d_gl_core + mesh_builder: MeshBuffers & builders
│   └── shapelab/                  # ShapeLabWindow, PlumbingLabPanel, ShapeLabScene
├── physics/                       # (Stage B) libedphysics — STATIC LIB, NO Qt DEPENDENCY
│   ├── include/edphys/…           # public headers (mirrors the Python module tree)
│   ├── src/…
│   └── CMakeLists.txt
├── bindings/                      # (optional, Stage B) edphys_native pybind11 *extension* module
├── tests/
│   ├── physics/                   # Catch2: replay fixtures per module
│   ├── corpus/                    # NativeBackend vs validation_engines/golden
│   ├── mesh/                      # mesh builders vs numpy fixtures
│   └── gui/                       # Qt Test (offscreen) + GL screenshot diffs (xvfb)
└── tools/                         # PYTHON helpers that generate reference data for the C++ side
    ├── dump_result_schema.py      # result key/type tree → docs/result_schema.md + .json
    ├── dump_fields.py             # EngineDesign fields/defaults/types → fields.json
    ├── dump_fixtures.py           # per-function input→output fixtures
    └── dump_meshes.py             # MeshBuffers for reference designs → .npz/.json
```

**Rule:** `physics/` must never include a Qt header. That keeps it testable headless and
reusable (a CLI, a KSP-side tool, bindings) and keeps the GUI/physics line as sharp as it
is in Python today.

---

## 4. Core architecture

### 4.1 The backend seam

Everything in the GUI talks to one abstract interface. Stage A implements it with
Python and Stage B with native C++. The GUI can't tell which one it has.

```cpp
// src/backend/PhysicsBackend.h
class PhysicsBackend {
public:
    virtual ~PhysicsBackend() = default;
    virtual nlohmann::json defaults() = 0;                     // EngineDesign().to_dict()
    virtual nlohmann::json migrate(const nlohmann::json&) = 0; // from_dict(...).to_dict()
    virtual ResultTree     compute(const nlohmann::json& design) = 0;
    virtual MeshSet        buildMeshes(const ResultTree&, const MeshOptions&) = 0; // A: py, A6+: native
    virtual std::string    renderCfg(const nlohmann::json& design, const ResultTree&,
                                     const ExportOptions&) = 0;
    virtual CatalogData    catalog() = 0;                      // or read the JSON directly in C++
    // Shape Lab / plumbing helpers that the Tk app calls straight into physics:
    virtual nlohmann::json defaultRunForHost(const std::string& host, const ResultTree&) = 0;
    virtual nlohmann::json seedRouteToPort(const nlohmann::json& run, const ResultTree&) = 0;
};
```

Before writing this header, grep `gui/*.py` for `from ..physics import` and list every
physics function the GUI calls directly, beyond `compute()`. Today that includes
`materials` (dropdown lists + allowed cooling methods), `combustion` (pair list, MR
optimum), `plumbing` (hosts, labels, default runs, route seeding), `geometry3d`,
`flow_network`, `manifold`, `cost_model`, `controller_tech` and `cycles`. Each one becomes
either a backend method or a static data query (§4.5). **This list is the real size of the
seam, so write it down in the header's comment.**

### 4.2 `DesignModel`: the design as data

```cpp
class DesignModel : public QObject {
    Q_OBJECT
public:
    const nlohmann::json& json() const;          // exactly EngineDesign.to_dict()
    QVariant value(std::string_view key) const;
    void setValue(std::string_view key, const QVariant&);   // emits fieldChanged + changed
    void load(const nlohmann::json& projectFile);           // runs backend.migrate()
    nlohmann::json toProjectFile() const;                   // {"schema_version": N, "design": {...}}
signals:
    void fieldChanged(QString key);
    void changed();                                         // anything; drives the debounce
};
```

- Store the design as **JSON keyed by the Python field names** in Stage A, not as a C++
  struct. The Python dataclass stays the single source of truth for field names,
  defaults and migrations until Stage B. `tools/dump_fields.py` writes
  `fields.json` (name, type, default, docstring-comment) as your reference sheet.
- `plumbing_runs` is the one list-valued field. The Shape Lab edits it as a JSON array
  and writes it back through `setValue("plumbing_runs", ...)`.
- Undo/redo is cheap to add later: each `setValue` is a `QUndoCommand` (old/new
  value). This is not required for parity.

### 4.3 `ResultTree`: the result as data

`compute()` returns a nested dict. Carry it across as a generic tree with typed
accessors. Don't design 111 structs up front.

```cpp
class ResultTree {
public:
    double                     num(std::string_view key, double fallback = NAN) const;
    const std::vector<double>& arr(std::string_view key) const;  // numpy 1-D → vector
    std::string                str(std::string_view key) const;
    bool                       has(std::string_view key) const;
    ResultTree                 sub(std::string_view key) const;  // nested dict
    std::vector<ResultTree>    list(std::string_view key) const; // e.g. checklist rows
    // path helper: r.at("cooling/regen_circuit_style")
};
```

Implement it as `std::shared_ptr<const Node>`, where `Node` is a
`std::variant<std::monostate, double, bool, std::string, std::vector<double>, std::vector<Node>, std::map<std::string, Node>>`.
Immutable after construction, so it is safe to hand from the worker thread to the GUI thread.

**How to use it while hand-coding:** each view reads only the keys it draws. When a view
settles, you can wrap its reads in a small typed struct (`SchematicInputs from(const ResultTree&)`)
that fails loudly on a missing key. `tools/dump_result_schema.py` produces the full
key → type → shape → example-value sheet (`docs/result_schema.md`) for the reference
designs. Regenerate it whenever the Python result changes.

### 4.4 `ComputeWorker`: threading, the GIL and debounce

```
UI thread                                   Compute thread (owns the Python interpreter)
─────────                                   ──────────────────────────────────────────
DesignModel::changed ──► QTimer(150 ms, single-shot, restart on change)
                               │ timeout
                               ▼
               ++generation; emit requestCompute(designJson, generation) ──queued──►
                                                         backend.compute(json) → ResultTree
                                                         (numpy → vector copies here)
               ◄──queued── resultReady(ResultTree, generation, elapsed_ms)
if generation == latest: views->setResult(r)   else: drop (stale)
```

- **All Python calls happen on the one compute thread.** `py::scoped_interpreter` is
  created in that thread's `run()`, and nothing on the UI thread ever touches `py::object`.
  This rule makes GIL problems impossible, so follow it strictly.
- Convert numpy to `std::vector<double>` *on the worker*, so the UI never holds a
  Python reference. Arrays are small (hundreds of stations), so a copy is fine.
- The 150 ms debounce + generation counter replaces `_schedule_recompute` /
  `_debounced_recompute`. Show `elapsed_ms` in the status bar, because this is your
  performance budget to watch.
- Slider *drag* (`on_drag` in Tk) updates the value label immediately and lets the
  debounce handle recompute. The Tk app's "only redraw the visible result tab"
  optimization (`_visible_result_tab`) carries over: views mark themselves dirty and
  repaint on `showEvent`.
- Exceptions: catch `py::error_already_set` on the worker, turn it into
  `computeFailed(QString traceback)`, and show it in a dock or the status bar. Never let
  a Python exception cross into Qt's event loop.

### 4.5 The field registry, which replaces most of `app.py`

About half of `app.py` is repetitive widget placement (`_add_slider`, `_add_dropdown`,
`_register_gate`, `CollapsibleSection` stacking). Replace it with data:

```cpp
enum class FieldKind { Slider, Spin, Dropdown, Check, Text, Button };

struct FieldSpec {
    std::string key;            // EngineDesign field name ("" for buttons/readouts)
    QString     label;
    FieldKind   kind;
    double      lo = 0, hi = 1; int decimals = 2; double step = 0;
    QString     unit;           // display only; the model stores SI like Python
    std::function<QStringList(const DesignModel&)> options;   // dynamic dropdowns
    std::function<bool(const DesignModel&)>        gate;      // visible/enabled predicate
    QString     tab, section;   // "Cooling", "Film overlay"
    QString     tooltip;
};
std::vector<FieldSpec> buildFieldRegistry();   // one .cpp per input tab: fields_cooling.cpp, …
```

- A `FieldForm` widget takes a tab's specs, builds `CollapsibleBox` sections with
  `QFormLayout`s, binds each widget ↔ `DesignModel`, and re-evaluates every `gate` on
  `DesignModel::changed`. This replaces `_register_gate`/`_apply_gates`.
- **Dynamic options with the hard-block rule.** The cooling-method dropdowns
  (`_filter_cooling_dropdowns`, `_effective_cooling_method`) list only
  `materials.Material.allowed_cooling_methods` for the chosen material. That list comes
  from the backend (Stage A) or the native materials table (Stage B). Keep the
  CLAUDE.md convention exactly: coerce + a failing checklist row, and the dropdown lists
  only allowed methods.
- Things that are *not* simple fields get hand-written widgets inside the form: the
  Plumbing tab's per-host status/Edit/Clear rows, the cost-override fields,
  the "Optimize MR" button + peak label, the liner/hatband readouts, and the export fields.
- **Porting procedure per tab:** read that tab's block in `app.py` (tab boundaries at
  lines ~217/231/352/751/840/905/1075/1154/1188), and turn each `_add_slider(...)` /
  `_add_dropdown(...)` call into one `FieldSpec` line. Most calls map mechanically.

### 4.6 Data queries that don't need `compute()`

Dropdown contents (propellant pairs, materials, turbopump materials, cycles, injector
types, ignition systems, host-part catalog) are static tables. In Stage A, fetch them once at
startup through the backend into a `StaticData` struct. In Stage B they come from native
tables. `catalog.json` / `roengines_models.json` can be read directly with nlohmann/json
from day one.

---

## 5. Tk / matplotlib → Qt mapping

| Today (Python) | Qt/C++ replacement | Notes |
|---|---|---|
| `EngineDesignerApp` (Tk root, `_build_layout`) | `MainWindow : QMainWindow` | Central `QSplitter`: left = input `QTabWidget` in a `QScrollArea`, right = result `QTabWidget`. |
| `ttk.Notebook` (input, 8 tabs) | `QTabWidget` + one `FieldForm` per tab | Tab names unchanged. |
| `ttk.Notebook` (result, 5 tabs) | `QTabWidget` | `_on_result_tab_changed` → `currentChanged` → lazy repaint. |
| `CollapsibleSection` (`collapsible.py`) | `CollapsibleBox : QWidget` | A `QToolButton` arrow header + content widget; ~60 lines. |
| `_add_slider` (Scale + value label) | `LabeledSlider` | `QSlider` (int-scaled) + `QDoubleSpinBox`, synced. Tk sliders have no typed entry, so this is a free UX win. |
| `_add_dropdown` | `QComboBox` via `FieldSpec::options` | |
| `_register_gate` / `_apply_gates` | `FieldSpec::gate` | Evaluated on `changed`. |
| `messagebox`, `filedialog` | `QMessageBox`, `QFileDialog` | |
| File menu, Ctrl+S/O/N/E | `QAction`s with `QKeySequence::Save/Open/New` + Ctrl+E | `_on_save_current` = Save; `_on_save` = Save As. |
| `project_io.save_design/load_design` | `DesignModel::toProjectFile/load` | Migration stays in Python (`from_dict`) until Stage B Tier 4. |
| `_on_export` → `cfg_writer.write_cfg` | `ExportDialog` → `backend.renderCfg` → write file | Keep the 3 output modes. |
| Checklist `Text` (`_populate_checklist`) | `ChecklistView : QTreeWidget` | Columns: status icon, item, detail. Group by category if the rows carry one. |
| `draw_schematic(ax, result)` | `SchematicView : Canvas2D` | Includes the cooling overlay, injector block and turbine-exhaust drawing. |
| `draw_injector_face(ax, result)` | `InjectorFaceView : Canvas2D` | |
| `draw_turbopump_diagram(ax, result)` | `TurbopumpDiagramView : Canvas2D` | Boxes + arrows + text; the simplest view. |
| `flow_legend.py` | `FlowLegend : QWidget` | Vertical colorbar using the same log-T turbo colormap LUT. |
| `EnginePreviewGLFrame` (`preview3d_gl.py`) | `EngineGLView : QOpenGLWidget` | §6. |
| manual MSAA FBO (`_ensure_msaa`/`_resolve_msaa`) | `QSurfaceFormat::setSamples(4)` | Delete that code path. |
| mouse/scroll/key bindings (`_on_mouse_*`, `_on_*_key`) | `mousePressEvent`/`mouseMoveEvent`/`wheelEvent`/`keyPressEvent` | Same orbit/pan/zoom/reset/recenter semantics. |
| X-ray / Flow / heat-flux / flat-shade toggles | toolbar `QAction`s (checkable) above the 3D view | `_on_xray_change`, `_on_flow_change`, `_apply_flow_scale`. |
| `shape_lab.py` `_ShapeLabBase` / `ShapeLabPanel` / `PlumbingLabPanel` | `ShapeLabWindow` (page in a `QStackedWidget` or a separate `QMainWindow`) | The Tk app swaps the whole left pane (`_enter_shape_lab`/`_exit_shape_lab`), and a `QStackedWidget` reproduces that. |
| `preview3d.py` (matplotlib 3D fallback) | **dropped** | Qt always has GL. |
| Shape Lab's matplotlib-3D fallback | **dropped** | Same. |

### 5.1 `Canvas2D`, the shared base for the three matplotlib views

matplotlib does a lot that you'll need to rebuild. Build it once:

- A **world→screen transform** with equal aspect (the schematic is in mm), autoscaling to
  a data bounding box plus margin, wheel zoom around the cursor, and drag pan. Use `QTransform`.
- Drawing primitives in *world* units: `polyline`, `polygon(fill, edge)`, `circle`,
  `rect`, `arrow`, `text(anchor, pt_size)` (text size in screen points, not world
  units), and `colorLine(xs, ys, values, colormap)` for the cooling overlay (matplotlib's
  `LineCollection` + `Normalize`).
- Optional axes and ticks, which only the schematic may want. The diagrams don't.
- `QPainter::setRenderHint(Antialiasing)`, plus `exportPng()/exportSvg()` using
  `QSvgGenerator`, which comes free once everything is `QPainter`.

The three `draw_*` functions are then line-by-line translations, because each matplotlib
call becomes a `Canvas2D` call. Port `turbopump_diagram` first (simplest), then
`injector_face`, then `schematic`.

---

## 6. The 3D renderer

### 6.1 Shaders
`preview3d_gl_core/shading.py` holds the GLSL as Python strings:
`PBR_FRAGMENT_SHADER` (with the X-ray `u_alpha`/`u_rim_power`/`u_facing_pass` inputs) and
`BACKGROUND_VERTEX_SHADER`/`BACKGROUND_FRAGMENT_SHADER`. `preview3d_gl.py` holds the rest:
`_VERTEX_SHADER`, `_FRAGMENT_SHADER` and `_GIZMO_VERTEX_SHADER`/`_GIZMO_FRAGMENT_SHADER`. Copy each one **verbatim** into
`resources/shaders/*.glsl` and load them with `QOpenGLShaderProgram::addShaderFromSourceFile(":/shaders/…")`.
Keep the uniform names identical so the numpy reference twin (`shading.py`'s CPU
`pbr_shade_reference`) stays a valid oracle for a pixel test.

### 6.2 Class split
```
EngineGLView : QOpenGLWidget, protected QOpenGLFunctions_3_3_Core
 ├── OrbitCamera          (port of camera_color.py camera math: yaw/pitch/dist/target, view/proj matrices → QMatrix4x4)
 ├── ShaderLibrary        (compiles once per context)
 ├── std::vector<GpuMesh> (VAO + VBOs: position, normal, color, flow_color, scalar, flow_s; IBO)
 ├── Renderer             (the multi-pass pipeline below)
 └── Gizmo                (axis triad, drawn in a corner viewport)
```

### 6.3 The render pipeline (port of `render_layers.py`)
1. Background gradient pass.
2. **Opaque layer**: depth write on, PBR.
3. **Translucent X-ray layer**: sort batches back-to-front by view depth
   (`render_layers` already defines the sort key and batching), depth write off, blend
   on, rim alpha via `u_rim_power`, and the `u_facing_pass` two-pass (back faces, then front).
4. **Flow tint** (Flow mode): `MeshBuffers.meta` tags (`coolant_pass`, `channel_grid`,
   `flow_host`) select which pieces get `flow_colors` at `FLOW_TINT_OPACITY`. A
   color-scale change (`FlowColorScale`: coolant / streams / absolute) is a
   **re-batch, not a rebuild**. Keep that property by recoloring from the per-vertex
   `scalar` attribute: either on the CPU into the color VBO (`glBufferSubData`) or, better,
   in the shader via a uniform LUT + range.
5. Gizmo.

`render_layers.py`'s pure functions (layer assignment, batching, sort) become a plain C++
`RenderLayers` unit in `src/mesh/` with no GL calls, so it stays unit-testable exactly as
it is now.

### 6.4 Mesh data crossing the seam
`MeshBuffers` (per piece: `positions float32[N,3]`, `normals`, `colors`, optional
`scalar`, `flow_s`, `flow_colors`, `indices uint32[M]`, `meta` dict, `role` string)
crosses as flat arrays. In Stage A, `PyBackend::buildMeshes` calls
`mesh_builder` + `preview3d_gl_core` and copies each array into a `std::vector<float>`,
which you upload with `glBufferData`. **Cache meshes per result generation**, because the Tk
app rebuilds them only when the result changes, not on camera motion.

### 6.5 GL context sharing
The main 3D view and the Shape Lab view are two `QOpenGLWidget`s. Either set
`Qt::AA_ShareOpenGLContexts` before `QApplication` so they can share shader programs,
or just compile shaders per widget, which is simpler and cheap. Never delete GL objects
outside `makeCurrent()`/`doneCurrent()`, and do cleanup in a slot connected to
`QOpenGLContext::aboutToBeDestroyed`.

---

## 7. Stage A — native GUI over embedded Python

Each phase ends with a runnable app. "Done when" is the exit criterion.

### A0 — Scaffold and the embed (small)
- [ ] `engine_designer_qt/CMakeLists.txt`: Qt6 Widgets/OpenGLWidgets, pybind11 embed,
      nlohmann/json, and Catch2 via FetchContent.
- [ ] `PyBackend` constructor: `py::scoped_interpreter`, `sys.path` += repo root, then
      `import engine_designer.physics.design`.
- [ ] `tools/dump_fields.py` → `fields.json`; `tools/dump_result_schema.py` →
      `docs/result_schema.md` (key path, type, shape, value for the default design + 2 corpus engines).
- [ ] A `ResultTree` converter (dict/list/float/int/bool/str/ndarray/None) with a unit
      test on the default design's result.
- **Done when:** a console `ed_probe` binary prints `thrust_vac_n` and `isp_vac_engine_s`
  for the default design and a loaded project file, and the numbers match
  `python3 -c "…EngineDesign().compute()…"` exactly (it is the same code).

### A1 — Main window skeleton and the compute loop
- [ ] `MainWindow` with the splitter, both tab widgets (empty tabs with the right names), and a status bar.
- [ ] `DesignModel`, `ComputeWorker` (thread + debounce + generation), and an error surface.
- [ ] `FieldSpec`/`FieldForm`/`LabeledSlider`/`CollapsibleBox`.
- [ ] **Combustion Chamber tab** fully in the registry (the biggest-traffic tab, which proves the pattern).
- [ ] `ChecklistView` (the easiest result view, and it shows everything the physics warns about).
- **Done when:** dragging a Chamber slider updates the checklist within ~debounce + compute
  time, and a Python exception in compute shows as an error without killing the app.

### A2 — The remaining input tabs, project IO and export
- [ ] Cooling (including the hard-block dropdown filtering), Injectors, Engine Bell, Turbopump
      (including the turbopump-tech/cost fields), Plumbing (per-host rows; the Edit button is
      disabled until A5), Gimbal, Model.
- [ ] Gates on every tab. Cross-check the visibility behaviour against the Tk app side by side.
- [ ] File menu: New/Open/Save/Save As with the schema migration going through `backend.migrate`.
      Window title with the file name and a dirty marker.
- [ ] `ExportDialog` → `renderCfg`, all 3 output modes, plus model-scale/mass-mult readouts
      (`_compute_model_scale`, `_compute_mass_mult`, `_host_native_height_m`).
- **Done when:** every user design in `validation_engines/user_designs/` loads, saves
  back byte-equivalent JSON (modulo key order), and exports a `.cfg` identical to the Tk
  app's.

### A3 — 2D views
- [ ] `Canvas2D` (§5.1).
- [ ] `TurbopumpDiagramView` → `InjectorFaceView` → `SchematicView` (with cooling overlay,
      injector block and turbine exhaust).
- [ ] `FlowLegend`.
- **Done when:** for the 12 corpus engines, the Qt views and the matplotlib PNGs look
  equivalent in a side-by-side check. Keep a `tools/render_matplotlib_refs.py` that saves
  the Tk-era PNGs as references.

### A4 — 3D preview
- [ ] `EngineGLView` + `OrbitCamera` + shaders loaded from resources.
- [ ] `PyBackend::buildMeshes` → `GpuMesh` upload, with a mesh cache per generation.
- [ ] The opaque pass, then X-ray, flow tint + scale switch, heat-flux mode, flat shade,
      and the duct bend-radius control (`set_duct_bend_radius_mult`).
- [ ] Gizmo and the keyboard pan/zoom/reset/recenter keys.
- **Done when:** a `grabFramebuffer()` screenshot of F-1 / J-2 / RS-25 under xvfb
  pixel-diffs within a small threshold against the PyOpenGL build's `glReadPixels`
  output (the cloud-sandbox recipe in CLAUDE.md produces those references).

### A5 — Shape Lab and the plumbing editor
- [ ] `ShapeLabWindow` shell (sidebar + its own `EngineGLView`) swapped into the left pane
      through a `QStackedWidget`.
- [ ] `PlumbingLabPanel`: segment list (`QListWidget`), per-segment controls
      (length, dia/bore_scale, yaw, pitch, elbow radius, flange), add/remove pipe,
      root angles, `root_mode`, connect-to-pump + "Route to pump", and Bake →
      `DesignModel::setValue("plumbing_runs", …)`.
- [ ] The manifold Shape Lab (`open_manifold_shape_lab`).
- [ ] Wire the Plumbing tab's Edit buttons.
- **Done when:** the whole Tk workflow is reproducible in Qt. **Then retire the Tk
  app**: keep `gui/app.py` in git history, and drop Tk from the README's run
  instructions. From then on the Python GUI modules that only drew things
  (`schematic.py`, `injector_face.py`, `turbopump_diagram.py`, `preview3d*.py`,
  `shape_lab.py`, `app.py`) are frozen references and can be deleted once you no longer
  want them as oracles.

### A6 — Native mesh layer (the first real C++ math)
The mesh code is GUI-owned, pure math, and the part most likely to matter for
interactive speed, which makes it the ideal first port.
- [ ] `tools/dump_meshes.py`: every `MeshBuffers` for the corpus engines + user designs
      (positions/normals/indices per piece, plus `meta`/`role`).
- [ ] Port `preview3d_gl_core` in its own dependency order: `hardware_constants` →
      `profile_geometry` → `mesh_primitives` → `shell_mesh` / `duct_meshes` / `tube_bundle`
      → `flow_meshes` → `camera_color` → `render_layers` (`shading.py`'s CPU twin only if
      you want the pixel oracle).
- [ ] Port `mesh_builder.py` (2.3k lines; split it by part family as you go) and
      `shape_lab_geometry.py`.
- [ ] Switch `buildMeshes` to native with a runtime toggle (`--py-meshes`), so you can
      A/B the two implementations.
- **Done when:** every dumped mesh matches its fixture in vertex/index count, and
  positions match to 1e-5 m. Once this phase lands, `mesh_builder` needs a
  `ResultTree` input, *not* a Python dict. That forces the result schema to be pinned down,
  which is good preparation for Stage B.

---

## 8. Stage B — porting the physics

**Strategy: strangler fig, leaves first, verified against Python at every step.**
Python stays the canonical implementation until the final cutover (B5), and the GUI
keeps running on `PyBackend` throughout. The native library grows beside it until
`NativeBackend` can replace `PyBackend` in full.

### 8.1 Numerics kit (write first; ~300 lines)
`edphys/numerics.h`:
- `interp(x, xp, fp)` with **numpy's exact edge semantics** (clamps to the end values,
  and requires `xp` increasing). Most parity bugs will come from here.
- `brent(f, a, b, xtol, rtol, maxiter)`, matching `scipy.optimize.brentq` defaults
  (`xtol=2e-12`, `rtol=4*eps`, `maxiter=100`). It must *throw* on a no-sign-change
  bracket like scipy does, because the Python code may rely on catching `ValueError`.
- `RegularGrid2D::operator()` (linear, with `bounds_error`/`fill_value` semantics copied
  from the one call site: `nozzle_shapes.py`'s Rao-TOP (θn, θe) table). `thermo_tables.py`
  does its own 1-D lookups, so check which interpolation it uses before porting it.
- `cumsum`, `gradient` (numpy's second-order central interior + first-order edges),
  `searchsorted` (left/right), `linspace`, `trapezoid`.
- `Vec3` with `dot`/`cross`/`norm`/`normalized`.
- `Profile` = `struct { std::vector<double> x, r; }` (the contour type every stage passes around).

### 8.2 Porting conventions
- **One Python module → one header/source pair** in the same relative path
  (`physics/cooling/march.py` → `edphys/cooling/march.{h,cpp}`), with the same function
  names in `snake_case` inside `namespace edphys::cooling`. That keeps `ASSUMPTIONS.md`,
  `COOLING_AUDIT.md` and every `claude_lit` "Implications" pointer valid, because a
  grep for the Python name finds the C++ one.
- **Constants keep their exact names** (`BARTZ_ABS_FLUX_CALIBRATION`,
  `DEFAULT_ETA_CSTAR`, `GAS_SIDE_DEPOSIT_FACTOR`, …) as `inline constexpr` in the
  module's header, **with the citation comment copied verbatim**.
- **Python dicts returned by physics functions become structs.** Name them after
  the function (`ChamberFlow chamber_flow(...)`). Where Python returns
  `None`-or-dict, use `std::optional<T>`.
- **String enums** (`cycle`, `pair`, cooling methods, `turbine_exhaust_mode`, topology
  names, …) become `enum class` with `to_string`/`from_string` using *the Python string
  values*, since those values are what appear in project JSON and golden files.
- **Tables** (`materials`, `turbopump_materials`, `*_tech`, combustion's hand
  monopropellant `_TABLES`, injector Cd tables, SPOT_CHECKS data) become
  `static const` arrays of structs. For anything with more than ~20 rows, consider
  dumping it to JSON from Python and loading it, so the two can't drift.
- **Baked property tables** (`physics/property_data/*.json`, ~1 MB) are loaded
  at runtime by `thermo_tables.cpp`, from the same files. Never convert them to
  C++ source.
- **Warn-don't-block is preserved.** Checklist rows are data (`struct CheckRow {status, item, detail}`),
  and the hard-block coercion stays in `resolve_cooling_method_checked`.

### 8.3 Port order by dependency tier

Port bottom-up. A module is ready to port once everything it imports is ported. For each
module, the checklist is: fixtures dumped → C++ written → fixture tests green → its
`__main__` self-test assertions ported as Catch2 cases.

**B1 — Tier 0: leaves (no intra-physics imports), ~4.3k lines**
- [ ] `isentropic` (166). Do this first, because nearly everything uses it.
- [ ] `thermo_tables` (339)
- [ ] `materials` (709), `turbopump_materials` (404), `turbopump_tech` (119), `controller_tech` (139)
- [ ] `geometry` (306), `geometry3d` (389), `nozzle_shapes` (226; imports isentropic; the grid interpolator's only user)
- [ ] `injectors` (493), `combustion_stability` (203), `ignition` (83), `gimbal` (31)
- [ ] `mass_model` (490), `reliability` (192), `tech_tree` (91), `turbopump` (77)
- [ ] `plumbing` (1,257). It is a leaf by import, but big and geometry-heavy. It can go in
      B2 if you want the other leaves done first.

**B2 — Tier 1, ~2.3k lines**
- [ ] `combustion` (519): `performance_state`, `cf_vac_ideal`, `exit_pressure_ratio`, `chamber_flow`, L* helpers
- [ ] `mixture_ratio` (91), `throttle` (50), `turbopump_efficiency` (212)
- [ ] `hatbands` (483; isentropic + mass_model), `manifold` (846; mass_model), `flow_network` (319)
- [ ] `cycles` (113), `electric_pump` (65)

**B3 — Tier 2: `cooling/` + turbomachinery, ~5.5k lines**
- [ ] `cooling/` in internal order: `coolant_props` → `coolant_state` → `gas_side` →
      `profile` → `film` → `radiation` → `wall` → `channels` → `march` (incl. two-pass) →
      `dump` → `regen_credit` → `methods` (incl. `resolve_cooling_method_checked`) →
      `thermal_solve`. Read `COOLING_AUDIT.md` before starting this tier.
- [ ] `turbopump_sizing` (957), `staged_combustion` (406, incl. `solve_staged_power_balance`),
      `expander` (142), `turbine_exhaust` (861), `cost_model` (105)

**B4 — Tier 3: `design/`, the orchestrator (~3.9k lines)**
- [ ] `EngineDesign` → a `struct EngineDesign` with ~107 typed fields + `from_json`/`to_json`
      (field names = Python names) + **the schema migrations** (port them from
      `from_dict` step by step, and keep `project_io.py`'s self-test cases (schema 3/4/5/99 files)
      as C++ tests).
- [ ] `PassState` → a typed `struct PassState`. The Python attribute bag has ~215 fields.
      Generate the field list with
      `grep -ohE '\bs\.[a-z_0-9]+ *=[^=]' physics/design/*_stage.py | sort -u`, then group it
      into sub-structs by the stage that *writes* each field (`s.comb`, `s.geom`, `s.thermal`, …).
      This is the single most tedious step, and grouping makes it readable.
- [ ] `constants.py` (199), `checklist.py`
- [ ] The 17 stages, **in `_compute_pass` order**, each testable in isolation by dumping
      `PassState` before/after it from Python:
      `combustion_setup` → `nozzle_performance` → `contour` →
      `injector_and_cooling_routing` → `thermal` → `turbomachinery_cycle` →
      `chamber_detail` → `thermal_reporting` → `nozzle_extension_thermal` →
      `coolant_capacity_and_isp` → `injector_and_manifolds` → `thermal_margins` →
      `jacket_manifolds_and_stability` → `wall_structure` → `tubes_and_hatbands` →
      `turbopump_and_plumbing` → `burn_time_and_mass` → `checks_and_result`
- [ ] `_compute_passes` (line-loss / exhaust-film second pass + residuals) and `compute()`
      (open-cycle thrust closure, ≤ 6 iterations, `thrust_closure_scale`).
- [ ] `checks_and_result` builds a `ResultTree` (the same tree the GUI already consumes), so
      the GUI needs no changes.

**B5 — Tier 4: export, cutover and cleanup**
- [ ] `export/cfg_writer` → `edphys/export/cfg_writer` (text rendering. Golden-test the
      *exact text* against the Python output for every corpus engine × 3 output modes.)
- [ ] `NativeBackend` implements every `PhysicsBackend` method.
- [ ] Runtime switch `--backend=py|native`, plus a **dual-run debug mode** that computes both and
      logs the largest relative diff per key. Leave it on for a few weeks of normal use.
- [ ] Port `physics/validate` spot checks to `tests/physics/validate_*.cpp` (the 28 banners
      become 28 Catch2 test cases with the same names).
- [ ] Cutover: make `native` the default and build without `ED_WITH_PYTHON` for releases.
      `PyBackend` remains available behind the CMake option for as long as Python stays the
      physics sandbox.

---

## 9. Parity and testing

### 9.1 Fixture dumping (the key to hand-porting safely)
`tools/dump_fixtures.py` imports a Python module, wraps chosen functions, runs the
corpus + user designs through `compute()`, and records `{"fn": ..., "args": ..., "kwargs": ..., "out": ...}`
for each call, de-duplicated and capped at N per function. That gives every C++ function
realistic inputs from real engines with no hand-written test values. The C++ side
replays them:

```cpp
TEST_CASE("isentropic::area_ratio_from_mach") {
    for (auto& fx : load_fixtures("isentropic.area_ratio_from_mach"))
        CHECK_THAT(area_ratio_from_mach(fx.arg<double>(0), fx.arg<double>(1)),
                   WithinRel(fx.out<double>(), 1e-12));
}
```

For the design stages, dump `PassState` (via `vars(s)`) before and after each stage for
each corpus engine. Stage *k* in C++ then gets Python's exact inputs, so a divergence is
localized to one stage and never compounds.

### 9.2 Tolerance policy
Bit-identical results against Python are **not** achievable: numpy's summation order, `libm`
differences, and `brentq`'s exact iterate sequence will differ in the last bits. State
the policy up front:

| What | Tolerance |
|---|---|
| Closed-form functions (isentropic, geometry, mass) | rel 1e-12 |
| Table lookups/interpolation | rel 1e-10 |
| Root-finds, marches, iterated solves (cooling march, staged power balance, thrust closure) | rel 1e-7 (tighten if it holds) |
| Discrete outputs (checklist statuses, chosen hatband section, stage counts, turbine counts) | **exact** |
| Rendered `.cfg` text | **exact** (format numbers the same way Python's f-strings do) |

A discrete output that flips near a threshold because of last-bit noise is a real
finding. Note the engine and key in the test, rather than loosening the tolerance.

### 9.3 Corpus harness
`tests/corpus/`: for each `validation_engines/{engines,user_designs}/*.json`, compute natively
and diff against `validation_engines/golden/**.json` under §9.2. This is the C++ twin of
`run_corpus.py --check`. Add it to `verify_all.sh` as one more PASS/FAIL line once it exists.

### 9.4 The optional `edphys_native` extension
A pybind11 *extension* (the reverse direction from Stage A's embedding) exposing ported
functions to Python lets you monkeypatch
`engine_designer.physics.isentropic.area_ratio_from_mach = edphys_native.isentropic.area_ratio_from_mach`
and run the *existing* `python3 -m engine_designer.physics.validate` against C++ code
mid-port. It's optional but cheap once the bindings exist, and it's the strongest
check available before B4 is done.

### 9.5 GUI tests
- Qt Test with `QT_QPA_PLATFORM=offscreen`: `FieldForm` binding, gates, and the
  debounce/generation logic (feed three rapid changes and assert one compute).
- GL: `EngineGLView::grabFramebuffer()` under `xvfb-run` on the cloud container (Mesa),
  pixel-diffed against references. Same recipe as CLAUDE.md's cloud-sandbox exception.
- Clicking and interaction are still checked by hand, as they are today.

---

## 10. Rules during the transition

1. **Python is canonical until B5 cutover.** Any physics change (new pair, new constant,
   bug fix) lands in Python first, with `validate` + corpus as today. Then it gets ported,
   its fixtures are re-dumped, and the golden snapshot is refreshed. Never fix a physics
   bug only in C++.
2. **The spot-check convention still applies to C++**: new physics is trusted only once it
   reproduces a real `Engine_Configs/` engine. The C++ `validate_*` tests are how that
   shows up after cutover.
3. **Keep the docs pointing at real code.** `ASSUMPTIONS.md`, `COOLING_AUDIT.md`,
   `claude_lit/topics/*` "Implications" sections and CLAUDE.md name Python files. After B5,
   either update those pointers or add a one-line "C++ twin: `edphys/…`" note per module.
   The identical-names rule in §8.2 makes this mechanical.
4. **Warn-don't-block + the one hard-block exception** carry over unchanged (§4.5, §8.2).
5. **Project JSON is the contract.** A C++ build must open every file a Python build
   wrote, and vice versa, for as long as both exist.

---

## 11. Risks and hand-coding notes

| Risk | Mitigation |
|---|---|
| The result dict changes under you (Python is still evolving) | Regenerate `docs/result_schema.md` from `tools/dump_result_schema.py`. Typed per-view wrappers fail loudly on a missing key. |
| Surprise numpy/scipy edge semantics (`interp` clamping, `gradient` edge order, `brentq` raising) | §8.1 kit with fixture tests *before* any module uses it. |
| GIL/threading bugs in Stage A | The one-thread-owns-Python rule (§4.4), with no exceptions. |
| `PassState` port is huge and untyped | Generate the field list, group by writing stage, and dump per-stage before/after fixtures (§9.1). |
| Responsiveness regression | The status bar shows compute ms. The budget stays "slider → redraw feels live". Stage B should make compute far faster, so profile it then. |
| GL resource lifetime across two widgets | §6.5. Clean up on `aboutToBeDestroyed`. |
| Schema migrations diverge | Port the `from_dict` chain in one go (B4), keeping `project_io.py`'s self-test cases, plus a round-trip test over every file in `user_designs/`. |
| Scope creep ("while I'm in here…") | Non-goals (§1). New features go on a list for after A5/B5. |

**Suggested first weekend:** A0 plus a stripped-down A1. Build a window with one
`LabeledSlider` bound to `chamber_pressure_pa` (shown in bar; the model stays SI), plus a
label showing `thrust_vac_n` / `isp_vac_engine_s` from a background compute.
That proves CMake, the pybind embed, the worker thread, the debounce and `ResultTree`
end to end. Everything after it is repetition of patterns this exercise establishes.

**Keep the old app runnable until A5.** Being able to run both side by side
(`python3 -m engine_designer.gui.app` vs `./ed_qt`) on the same project file is the
fastest way to spot a missed gate or a mis-wired field.

---

## Appendix — module inventory

Stage = where it gets ported. "A-py" = called through `PyBackend` in Stage A.
"Tool" = stays Python permanently.

### GUI (`engine_designer/gui/`)
| Python | Lines | C++ target | Phase |
|---|---:|---|---|
| `app.py` | 2,903 | `app/MainWindow` + `model/*` + `widgets/FieldForm` + `fields_*.cpp` | A1–A2 |
| `collapsible.py` | 65 | `widgets/CollapsibleBox` | A1 |
| `project_io.py` | 159 | `model/DesignModel::load/toProjectFile` (migrations: A-py → B4) | A2 |
| `schematic.py` | 416 | `views/SchematicView` | A3 |
| `injector_face.py` | 179 | `views/InjectorFaceView` | A3 |
| `turbopump_diagram.py` | 280 | `views/TurbopumpDiagramView` | A3 |
| `flow_legend.py` | 96 | `views/FlowLegend` | A3 |
| `preview3d_gl.py` | 734 | `gl/EngineGLView`, `gl/Renderer`, `gl/Gizmo` | A4 |
| `preview3d_gl_core/shading.py` | 549 | `resources/shaders/*.glsl` (+ optional CPU twin) | A4 (A6 twin) |
| `preview3d_gl_core/render_layers.py` | 270 | `mesh/RenderLayers` | A4 (py) → A6 |
| `preview3d_gl_core/camera_color.py` | 416 | `gl/OrbitCamera` + `mesh/Colormaps` | A4 |
| `preview3d_gl_core/` other 8 modules | 3,715 | `mesh/*` | A-py → A6 |
| `mesh_builder.py` | 2,298 | `mesh/MeshBuilder*` | A-py → A6 |
| `shape_lab.py` | 746 | `shapelab/ShapeLabWindow`, `shapelab/PlumbingLabPanel` | A5 |
| `shape_lab_geometry.py` | 438 | `shapelab/ShapeLabScene` | A-py → A6 |
| `preview3d.py` | 230 | — dropped | — |

### Physics (`engine_designer/physics/`)
| Python | Lines | Tier / phase |
|---|---:|---|
| `isentropic` | 166 | B1 |
| `thermo_tables` (+ `property_data/*.json`, loaded as-is) | 339 | B1 |
| `materials` | 709 | B1 |
| `turbopump_materials` | 404 | B1 |
| `turbopump_tech` / `controller_tech` | 119 / 139 | B1 |
| `geometry` / `geometry3d` | 306 / 389 | B1 |
| `nozzle_shapes` | 226 | B1 |
| `injectors` / `combustion_stability` / `ignition` / `gimbal` | 493 / 203 / 83 / 31 | B1 |
| `mass_model` / `reliability` / `tech_tree` / `turbopump` | 490 / 192 / 91 / 77 | B1 |
| `plumbing` | 1,257 | B1 (or B2) |
| `combustion` | 519 | B2 |
| `mixture_ratio` / `throttle` / `turbopump_efficiency` | 91 / 50 / 212 | B2 |
| `hatbands` / `manifold` / `flow_network` | 483 / 846 / 319 | B2 |
| `cycles` / `electric_pump` | 113 / 65 | B2 |
| `cooling/` (13 modules) | ~2,100 | B3 |
| `turbopump_sizing` / `staged_combustion` / `expander` | 957 / 406 / 142 | B3 |
| `turbine_exhaust` / `cost_model` | 861 / 105 | B3 |
| `design/engine.py` (+ `state.py`, `constants.py`, `checklist.py`) | 638 + 224 | B4 |
| `design/*_stage.py` (8 files, 17 stage functions) | ~3,000 | B4 |
| `validate/` | ~3,000 | B5 (as Catch2 tests) |

### Export / catalog / tooling
| Python | Lines | Target |
|---|---:|---|
| `export/cfg_writer.py` | 659 | A-py → B5 native |
| `catalog/__init__.py` (loaders) | 35 | Read JSON directly in C++ from A1 |
| `catalog/build_catalog.py`, `build_roengines_models.py` | 325 | Tool |
| `tools/property_tables/generate_property_tables.py` | — | Tool |
| `validation_engines/build_corpus.py`, `run_corpus.py` | — | Tool (the C++ harness mirrors `--check`) |
