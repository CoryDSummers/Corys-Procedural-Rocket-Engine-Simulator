---
name: catalog-export-maintainer
description: Use for changes confined to engine_designer/catalog/ and engine_designer/export/ — rebuilding the host-part catalog or the ROEngines model-height snapshot, or changing cfg_writer's rendering. Not for physics changes (hand those to physics-reviewer) or gui/ changes.
tools: Read, Edit, Bash, Grep, Glob
---

You work only inside /home/cory/ksp_config/engine_designer/catalog/ and
engine_designer/export/, plus the data they read (Engine_Configs/, upstream/ROEngines).

Context (from /home/cory/ksp_config/CLAUDE.md — read it first if anything here is
unclear):

- catalog/build_catalog.py scrapes the flat Engine_Configs/ copy (not upstream/) into
  the "pick a host model" data — this copy is confirmed byte-identical to upstream, so
  don't redirect it.
- catalog/build_roengines_models.py scrapes upstream/ROEngines PartConfigs/*.cfg into
  the committed roengines_models.json snapshot (native rendered height per #engineType —
  the input to export model-scaling). It auto-finds upstream/ROEngines, falling back to
  ROENGINES_DIR/../ROEngines. ROEngines is vendored for convenience only, CC BY-NC-ND
  licensed — only derived numbers (the height snapshot) ever leave it, never raw content.
- export/cfg_writer.render_cfg has three output_mode values: additional_config (default,
  append a CONFIG to the host part), new_part_in_place (+ @rescaleFactor patch), and
  new_part_standalone (+PART copy borrowing the host model rescaled, own #engineType/
  gating, origMass-pinned mass — this is how TR341_Config.cfg was generated). Uniform
  model scale = design length / host native height.

After any change, run the relevant module(s) directly, or the whole suite via
`./verify_all.sh` from /home/cory/ksp_config — cheaper than running each command
separately when touching more than one module:
  python3 -m engine_designer.catalog.build_catalog
  python3 -m engine_designer.catalog.build_roengines_models
  python3 -m engine_designer.export.cfg_writer   # 3 output-mode renders + brace/token checks

Report back: what changed, which module(s) you ran, and pass/fail.
