zz-qol: Cascading Factorio QoL Modpacks

These are lightweight, dependency-only modpacks that cascade from least to most game-changing. Each heavier pack depends on the lighter ones, so enabling `qol-max` gives you everything in `qol-plus` and `qol-lite`, and `qol-editor` includes them all.

Modpacks

- qol-lite
  - Display-only, no gameplay changes. Examples: Infomatrion pages, rate/throughput calculators, milestone tracker.
- qol-plus
  - Light automation of actions a player can do by clicking. Examples: auto-deconstruct depleted miners, even item distribution.
- qol-max
  - Heavier QoL and build assistance. Example: blueprint shotgun for building/clearing in patterns.
- qol-editor
  - Creator/god-mode helpers. Includes all items from the screenshots you shared (except Space Age), plus Waterfill.
  - Explicit deps: belt-visualizer, squeak-through-2, better-victory-screen, elevated-rails, far-reach, flib, inventory-repair, mining-patch-planner, pump, quality, show-max-underground-distance, BottleneckLite, factoryplanner, StatsGui, CursorEnhancements, EditorExtensions. Excludes Space Age (conflicts with `space-age`).

Cascading dependencies

- `qol-plus` depends on `qol-lite`.
- `qol-max` depends on `qol-plus` (and thus `qol-lite`).
- `qol-editor` depends on `qol-max` (and thus all below).

Contents (initial curation)

- qol-lite
  - informatron
  - RateCalculator
  - Milestones
- qol-plus
  - AutoDeconstruct
  - even-distribution
- qol-max
  - blueprint-shotgun
- qol-editor
  - EditorExtensions
  - Waterfill

Notes

- These packs are dependency-only. They contain no code or prototypes.
- Mod IDs above are the actual mod portal IDs.
- Target Factorio 2.0.

Install

- Option A (local dev): copy any of the `qol-*` folders into your Factorio `mods` directory as-is or zip each folder as `name_version.zip` (e.g., `qol-lite_1.0.0.zip`).
- Option B (portal): if you publish, keep folder names identical to the `name` field in `info.json` and tag versions accordingly.

Cross-links

- Start with: `qol-lite/`
- Add: `qol-plus/` (includes `qol-lite`)
- Go bigger: `qol-max/` (includes `qol-plus` + `qol-lite`)
- Creator tools: `qol-editor/` (includes everything)

Pin versions automatically

- Script: `scripts/pin_mod_versions.py`
- Dry run (show what would change):
  - `scripts/pin_mod_versions.py`
- Write in place, use exact pins (`==`):
  - `scripts/pin_mod_versions.py --write --mode eq`
- Only update a specific file:
  - `scripts/pin_mod_versions.py --path qol-editor/info.json --write`
- Notes:
  - Preserves `!` and `?` flags and skips `base` and the local pack names.
  - By default, only adds a comparator if one isn’t already present; pass `--force` to override.
  - Chooses the latest release matching the pack’s `factorio_version` if available; otherwise the latest release overall.
