# QoL packs 1.1.0 — Factorio 2.1

Lite, Plus, and Max now support Factorio 2.1.22 or newer.

- Replace RecipeBook with RecipeBook2_1 >= 1.0.0 in Lite, inherited by Plus and Max.
- Update all external minimum versions to releases explicitly supporting Factorio 2.1.
- Require the updated 1.1.0 packs throughout the cascade.
- Fix the dependency updater to reject incompatible releases, retain patch-level minimums, emit valid exact-version syntax, and fail on unresolved dependencies.
- Avoid including upload credentials in release-script error messages.

The unpublished Editor pack stays on Factorio 2.0 / version 1.0.2 because Waterfill has no 2.1 release. It is not included in this release's assets.

Validation: updater regression tests, Mod Portal metadata and dependency-constraint checks, and ZIP structure/content checks. Full in-game testing was not performed because the installed game is 2.1.21, below the required version.

Install the desired tier and its lower-tier ZIPs into the Factorio mods directory, then install the required external mods. These GitHub artifacts do not automatically publish the packs to the Factorio Mod Portal.
