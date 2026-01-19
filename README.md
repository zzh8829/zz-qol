zz-qol: Cascading Factorio QoL Modpacks

Lightweight, dependency-only modpacks that cascade from least to most game‑changing. Enable a higher tier to get everything below.

Packs

- qol-1-lite (mod id: `zz-qol-lite`)
  - Purpose: pure visibility and planning — zero gameplay changes.
  - Why: better information leads to better decisions without affecting balance.
- qol-2-plus (mod id: `zz-qol-plus`)
  - Purpose: automate tedious click-work the player can already do manually.
  - Why: fewer repetitive actions, same outcomes and tech progression.
- qol-3-max (mod id: `zz-qol-max`)
  - Purpose: stronger build/maintenance helpers that still respect survival play.
  - Why: speed up building and upkeep without creative‑mode powers.
- qol-4-editor (mod id: `zz-qol-editor`)
  - Purpose: god/creator tools for map work and megabase grooming.
  - Why: fast terraforming/test setups outside normal progression.

How Cascading Works

- `zz-qol-plus` depends on `zz-qol-lite`.
- `zz-qol-max` depends on `zz-qol-plus` (thus also lite).
- `zz-qol-editor` depends on `zz-qol-max` (thus all below).

Tier Details

- zz-qol-lite
  - `informatron` — in‑game docs hub; keeps info in one place.
  - `RateCalculator` — live throughput/rate overlays; quick bottleneck checks.
  - `Milestones` — progress tracker; motivation without changing play.
  - `belt-visualizer` — render belt flow; debug lanes at a glance.
  - `flib` — shared GUI/utility lib used by several QoL mods.
  - `better-victory-screen` — cleaner end‑screen; no gameplay impact.
  - `show-max-underground-distance` — shows max span; avoids misplacements.
  - `BottleneckLite` — lamp‑style activity indicators; see “stuck” machines.
  - `StatsGui` — surface/factory stats; plan expansions sensibly.
  - `factoryplanner` — production planner; blueprint inputs/outputs clearly.
  - `RecipeBook` — browse recipes/uses; learn chains quickly.
  - `FactorySearch` — fast search for items/recipes/entities.

- zz-qol-plus
  - `AutoDeconstruct` — flag empty miners; less babysitting of ore patches.
  - `EvenDistributionLite` — spread items evenly; fewer drag‑drop passes.
  - `EditorExtensions` — handy utilities/shortcuts; quality‑of‑life console.
  - `pump` — smoother fluid connection UX.
  - `mining-patch-planner` — select ore patches neatly; tidy outposts.
  - `manual-inventory-sort` — one‑key inventory sorting.

- zz-qol-max
  - `blueprint-shotgun` — paint/erase with blueprints; fast area edits.
  - `squeak-through-2` — tighter collision; walk between close entities.
  - `inventory-repair` — auto‑repair from inventory when applicable.

- zz-qol-editor
  - `Waterfill` — place water tiles; quick lakes/canals for testing.
  - Inherits everything from lower tiers.

Install

- Copy the built zip(s) to your Factorio `mods` folder. Repo folders use numeric prefixes (`qol-1..4`) for sorting, while mod IDs in `info.json` are `zz-qol-*`.
- Or publish using the release script below.

Build/Release

- Build a zip (no upload):
  - `qol-1-lite/release.sh`
  - `qol-2-plus/release.sh`
  - `qol-3-max/release.sh`
  - `qol-4-editor/release.sh`
- Upload to Mod Portal (v2 publish API):
  - Set `FACTORIO_TOKEN` (API key with “ModPortal: Publish Mods”).
  - Example: `FACTORIO_TOKEN=... qol-1-lite/release.sh --upload`
- Output: `dist/<name>_<version>.zip` with correct inner folder structure.

Batch Operations

- Pin versions across all packs (also bumps pack patch on dependency/remote changes): `scripts/run_all.sh pin --upgrade --write`
- Regenerate thumbnails across all packs: `scripts/run_all.sh logos`
- Build zips across all packs: `scripts/run_all.sh release`

Script Reference

- `scripts/run_all.sh` — driver that scans one level under the repo root for `*/info.json` and runs a script per pack.
  - Runs in fixed order: `qol-1-lite`, `qol-2-plus`, `qol-3-max`, `qol-4-editor`.
- `scripts/pin_mod_versions.py` — pin mod dependencies for a single `info.json` file.
  - Dry run: `python3 scripts/pin_mod_versions.py --path qol-4-editor/info.json`
  - Exact pins: `python3 scripts/pin_mod_versions.py --path qol-4-editor/info.json --write --mode eq`
  - Notes: preserves `!`/`?`, skips local pack IDs and `base`, prefers releases for the pack’s `factorio_version`, bumps patch when deps or remote version change.
- `scripts/generate_logos.py` — generate one pack thumbnail.
  - Example: `python3 scripts/generate_logos.py --path qol-4-editor`
  - Output: `thumbnail.png` (512x512 with “ZZ QOL”, tier badge, and motif).
- `scripts/release_mod.py` — build (and optionally upload) a single pack release zip.
  - Example: `python3 scripts/release_mod.py --path qol-4-editor`
  - Upload: `FACTORIO_TOKEN=... python3 scripts/release_mod.py --path qol-4-editor --upload`

License

- MIT License. See `LICENSE` for full text.
