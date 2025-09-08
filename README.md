zz-qol: Cascading Factorio QoL Modpacks

These are lightweight, dependency-only modpacks that cascade from least to most game-changing. Each heavier pack depends on the lighter ones, so enabling `zz-qol-max` gives you everything in `zz-qol-plus` and `zz-qol-lite`, and `zz-qol-editor` includes them all.

Modpacks

- qol-1-lite (mod id: zz-qol-lite)
  - Display-only, no gameplay changes. Examples: Infomatrion pages, rate/throughput calculators, milestone tracker.
- qol-2-plus (mod id: zz-qol-plus)
  - Light automation of actions a player can do by clicking. Examples: auto-deconstruct depleted miners, even item distribution.
- qol-3-max (mod id: zz-qol-max)
  - Heavier QoL and build assistance. Example: blueprint shotgun for building/clearing in patterns.
- qol-4-editor (mod id: zz-qol-editor)
  - Creator/god-mode helpers. Includes all items from the screenshots you shared (except Space Age), plus Waterfill.
  - Explicit deps: belt-visualizer, squeak-through-2, better-victory-screen, elevated-rails, far-reach, flib, inventory-repair, mining-patch-planner, pump, quality, show-max-underground-distance, BottleneckLite, factoryplanner, StatsGui, CursorEnhancements, EditorExtensions. Excludes Space Age (conflicts with `space-age`).

Cascading dependencies

- `zz-qol-plus` depends on `zz-qol-lite`.
- `zz-qol-max` depends on `zz-qol-plus` (and thus `zz-qol-lite`).
- `zz-qol-editor` depends on `zz-qol-max` (and thus all below).

Contents (initial curation)

- qol-1-lite
  - informatron
  - RateCalculator
  - Milestones
- qol-2-plus
  - AutoDeconstruct
  - even-distribution
- qol-3-max
  - blueprint-shotgun
- qol-4-editor
  - EditorExtensions
  - Waterfill

Notes

- These packs are dependency-only. They contain no code or prototypes.
- Mod IDs above are the actual mod portal IDs.
- Target Factorio 2.0.

Install

- Option A (local dev): copy the zipped files into your Factorio `mods` directory. Note: Factorio requires folder/zip names to follow `mod_name_version`. The repo folders are named with numeric prefixes for sorting but the mod IDs remain `zz-qol-*`.
- Option B (portal): if you publish, keep folder names identical to the `name` field in `info.json` and tag versions accordingly.

Cross-links

- Start with: `qol-1-lite/`
- Add: `qol-2-plus/` (includes `zz-qol-lite`)
- Go bigger: `qol-3-max/` (includes `zz-qol-plus` + `zz-qol-lite`)
- Creator tools: `qol-4-editor/` (includes everything)

Logos

- Each pack includes a `thumbnail.png` generated via `scripts/generate_logos.py`.
- The thumbnails are 512x512 with the text "ZZ QOL", a level badge (1–4), and a visual motif per tier (Lite chart, Plus plus-sign mosaic, Max lightning over blueprint grid, Editor crown + droplet).
- Regenerate all: `python3 scripts/generate_logos.py`

Pin versions automatically

- Script: `scripts/pin_mod_versions.py`
- Dry run (show what would change):
  - `scripts/pin_mod_versions.py`
- Write in place, use exact pins (`==`):
  - `scripts/pin_mod_versions.py --write --mode eq`
- Only update a specific file:
  - `scripts/pin_mod_versions.py --path qol-4-editor/info.json --write`
- Notes:
  - Preserves `!` and `?` flags and skips `base` and the local pack names.
  - By default, only adds a comparator if one isn’t already present; pass `--force` to override.
  - Chooses the latest release matching the pack’s `factorio_version` if available; otherwise the latest release overall.

License

- MIT License. See `LICENSE` for full text.

Release

- Build a zip (no upload):
  - `qol-1-lite/release.sh`
  - `qol-2-plus/release.sh`
  - `qol-3-max/release.sh`
  - `qol-4-editor/release.sh`
- Upload to Mod Portal (requires env vars):
  - `FACTORIO_USERNAME` = your mods.factorio.com username
  - `FACTORIO_TOKEN` = API token from https://mods.factorio.com/api-key
  - Example: `FACTORIO_USERNAME=zzh8829 FACTORIO_TOKEN=... qol-1-lite/release.sh --upload`
- Output zip path: `dist/<name>_<version>.zip` with correct inner folder structure.
