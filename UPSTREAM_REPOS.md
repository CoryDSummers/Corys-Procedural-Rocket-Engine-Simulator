# Upstream KSP-RO repos (local reference clones)

## 1. Purpose & scope

`upstream/` holds shallow, no-history local clones of the three GitHub repos this
project's modding work is built on top of: `KSP-RO/RealismOverhaul`, `KSP-RO/RP-1`,
and `KSP-RO/ROEngines`. They exist so a Claude session can grep/read the real
upstream source directly instead of re-deriving facts from memory or asking the
user to paste snippets. They are **local-only reference material, never
redistributed or committed as a git submodule** — the project directory itself
isn't a git repo, and `upstream/.gitignore` (`*`) keeps the whole tree out of any
future `git init` here regardless. Nothing in this project vendors upstream
content wholesale except in the narrow, pre-existing, license-compliant ways
described below (`Engine_Configs/`, `roengines_models.json`).

This doc is the "read this instead of re-cloning/re-exploring" summary. Read
`CLAUDE.md` first as always; it points here.

## 2. What's cloned, where, and how to refresh

| Repo | Local path | Commit (shallow HEAD) | Cloned | Refresh |
|---|---|---|---|---|
| RealismOverhaul | `upstream/RealismOverhaul` | `25a536b` | 2026-09-14 | `rm -rf upstream/RealismOverhaul && git clone --depth 1 https://github.com/KSP-RO/RealismOverhaul.git upstream/RealismOverhaul` |
| RP-1 | `upstream/RP-1` | `4055038` | 2026-09-14 | `rm -rf upstream/RP-1 && git clone --depth 1 https://github.com/KSP-RO/RP-1.git upstream/RP-1` |
| ROEngines | `upstream/ROEngines` | `5c1c437` | 2026-09-14 | `rm -rf upstream/ROEngines && git clone --depth 1 https://github.com/KSP-RO/ROEngines.git upstream/ROEngines` |

All are `--depth 1` (no history) — refreshing means delete-and-reclone, not `git
pull`. Sizes on disk: RealismOverhaul 113M, RP-1 279M, ROEngines 1.1G (almost
entirely 3D model/texture assets under `GameData/ROEngines/Assets/`, not configs).

## 3. Licensing

- **RealismOverhaul**: no `LICENSE` file; `README.md` states CC-BY-SA for existing
  content, `CONTRIBUTING.md` requires new contributions under CC-BY-4.0.
- **RP-1**: `LICENSE.md` = CC-BY-NC-SA 4.0 (NonCommercial + ShareAlike), also
  incorporating other CC-BY-NC-SA assets (KerbalConstructionTime, Bluedog Design
  Bureau, Coatl Aerospace) and one BSD-3-Clause component (DMagic Orbital Science).
- **ROEngines**: `LICENSE.md` = **CC BY-NC-ND 4.0** (NonCommercial + **No
  Derivatives**) — permits sharing unmodified copies with attribution, forbids
  commercial use and forbids distributing anything derived/modified. This is why
  `roengines_models.json` stores only derived numeric dimensions and identifiers,
  never model assets or verbatim config text (see `build_roengines_models.py`'s
  own docstring) — that constraint predates this clone and is unaffected by it.

**Bottom line**: these clones are for local study only. Nothing beyond the
already-existing derived data (`Engine_Configs/`, `roengines_models.json`) gets
copied out of `upstream/` into anything this project commits or shares.

## 4. RealismOverhaul

Top-level layout: `GameData/` (the actual mod payload — what installs into KSP),
`Source/` (C# plugin source, Harmony patches), `Ships/` + `Subassemblies/` (stock
craft files), `KSPediaSource/` (in-game help assets), `Notes/` (dev notes,
spreadsheets, not shipped), `Scripts/` (one-off Python/Perl migration scripts).

Engine configs live at `GameData/RealismOverhaul/Engine_Configs/` (316 files) plus
three sibling dirs also under `GameData/RealismOverhaul/`:
`Nuclear_Engine_Configs/` (22), `Electric_Engine_Configs/` (26),
`Jet_Engine_Configs/` (60) — 424 total, matching this project's
`/home/cory/ksp_config/Engine_Configs/` file count exactly.

**Confirmed**: this project's flat `Engine_Configs/` copy is the byte-identical
union of upstream's 4 directories flattened into one (spot-checked
`H1_Config.cfg`, `F1_Config.cfg`, `RD180_Config.cfg`, `SSME_Config.cfg`,
`LR87LH2_Config.cfg` — all diff-clean against `upstream/RealismOverhaul`). No
resync needed as of commit `25a536b`.

Engine cfgs do **not** contain `TechRequired` (0 hits) — RP-1 tech-tree gating is
applied entirely on the RP-1 side (see below), never baked into RealismOverhaul's
own configs. `build_catalog.py` continues to be the right tool for scraping this
data; it targets the flat local copy, not `upstream/RealismOverhaul`, and needs no
changes.

## 5. RP-1: tech-tree node reference

Tech-tree nodes are `RDNode { }` blocks in
**`upstream/RP-1/GameData/RP-1/Tree/RP0TechTree.cfg`** (148KB, 7802 lines, 332
nodes total — `grep -c '^\s*RDNode$'`). This is the authoritative source for every
`TechRequired`-style node ID used anywhere in this project's fictional-engine
configs (confirmed: `orbitalRocketry1972` at line 3269, `advancedUncrewedLanding`
at line 1751).

Node shape:

```
RDNode
{
    id = advancedUncrewedLanding
    title = Advanced Uncrewed Landing
    description = Advanced Uncrewed Landing (1972-1980)
    cost = 116
    nodeName = advancedUncrewedLanding
    icon = RP-1/Tree/Icons/rp0_icon_viking
    pos = -1847,1665,-1
    scale = 0.6
    Parent { parentID = improvedLandingEngines; lineFrom = RIGHT; lineTo = LEFT }
    Parent { parentID = materialsScienceSpaceStation; lineFrom = RIGHT; lineTo = LEFT }
}
```

`id`/`nodeName` (identical) is the string used as `TechRequired` in part configs.
`description` usually embeds a year range — the most reliable way to place a node
in time. Many families are a category name with a trailing year
(`orbitalRocketry1972`/`1976`/... — 24 variants; `colonization*` — 54 variants;
also `stagedCombustion*`, `solids*`, `hydrolox*`, `FRSC*`, `elecPropulsion*`), so a
plausible new node name for an unmodeled year can often be guessed from the
pattern of its neighbors rather than requiring a fresh read of the whole tree —
but always grep `RP0TechTree.cfg` to confirm a guessed ID actually exists before
using it in a config. `upstream/RP-1/Source/Tech Tree/TreeYears.csv` is a
supplementary year-mapping table if a broader survey is ever needed.

Secondary files that *reference* (don't define) these IDs:
`GameData/RP-1/SCMData/TechNodeData.cfg`, `GameData/RP-1/Tree/TREE-Engines.cfg`,
`GameData/RP-1/Tree/TREE-Parts.cfg`.

Out of scope for this project (present but not studied): `GameData/RP-1/Contracts/`
and `GameData/RP-1/Programs/` (contract packs / Mission Control), both siblings of
`GameData/RP-1/Tree/`.

## 6. ROEngines

`GameData/ROEngines/PartConfigs/*.cfg` (227 files) is exactly what
`engine_designer/catalog/build_roengines_models.py` already expects and parses —
confirmed by running it against this checkout: it found the same 150 deduped
engineType entries already committed in `roengines_models.json`, byte-for-byte
(the existing snapshot's `_commit` field, `5c1c437...`, already matched this exact
clone).

`_find_partconfigs_dir()` in that script now checks `upstream/ROEngines` first
(before the old `../ROEngines`-relative-to-project-root fallback and
`$ROENGINES_DIR`), so simply running

```
python3 -m engine_designer.catalog.build_roengines_models
```

from the project root now finds this checkout automatically with no env var
needed — this is the one code change made as part of vendoring these repos.
Everything else about how `roengines_models.json` is built/used is unchanged; see
the licensing note in section 3 for why only derived numbers are ever stored.

## 7. Optional future ideas (not built)

- A small script analogous to `build_roengines_models.py` that scrapes
  `RP0TechTree.cfg` into a committed `techtree_nodes.json` snapshot (id → title →
  year → parents), so `engine_designer`'s GUI could offer a node picker instead of
  free-text `TechRequired` entry. Flagged as a future idea only — not implemented
  here, and shouldn't be built speculatively without an actual GUI use case
  driving it.
