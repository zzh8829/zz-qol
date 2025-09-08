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

Logos

- Each pack includes a `thumbnail.png` generated via `scripts/generate_logos.py`.
- Thumbnails are 512x512 with “ZZ QOL”, a tier badge (1–4), and a distinct motif.
- Regenerate: `python3 scripts/generate_logos.py`

Pin Versions

- Script: `scripts/pin_mod_versions.py`
- Dry run: `scripts/pin_mod_versions.py`
- Exact pins: `scripts/pin_mod_versions.py --write --mode eq`
- Single file: `scripts/pin_mod_versions.py --path qol-4-editor/info.json --write`
- Notes: preserves `!`/`?`, skips local pack IDs and `base`, prefers releases for the pack’s `factorio_version`.

License

- MIT License. See `LICENSE` for full text.

