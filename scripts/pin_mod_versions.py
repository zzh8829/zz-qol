#!/usr/bin/env python3
"""
Pin Factorio mod dependency versions in info.json files.

Features
- Scans one file or all info.json under a directory.
- For each dependency, fetches the latest portal release compatible with the pack's factorio_version.
- Preserves `!` (conflict) and `?` (optional) flags and leaves `base` and local pack names unmodified.
- Skips dependencies that already have a comparator unless `--force`.
- Modes: `>=` (default) or exact `==` pinning.

Examples
  Dry run for repo:
    scripts/pin_mod_versions.py

  Write changes in-place, pin exact versions:
    scripts/pin_mod_versions.py --write --mode eq

  Only a specific pack file:
    scripts/pin_mod_versions.py --path qol-editor/info.json --write
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.request import urlopen

MOD_PACK_NAMES = {"qol-lite", "qol-plus", "qol-max", "qol-editor"}
DEP_RE = re.compile(r"^\s*([!?])?\s*([A-Za-z0-9_-]+)(?:\s*(>=|<=|==|=|~>)\s*([0-9][0-9.]*))?\s*$")


def parse_dep(dep: str) -> Tuple[str, str, Optional[str], Optional[str]]:
    """Return (flag, name, op, ver) parsed from a dependency string.

    flag: '!' conflict, '?' optional, or ''
    name: mod id
    op, ver: comparator and version, if present
    """
    m = DEP_RE.match(dep)
    if not m:
        raise ValueError(f"Unrecognized dependency format: {dep!r}")
    flag, name, op, ver = m.group(1) or "", m.group(2), m.group(3), m.group(4)
    return flag, name, op, ver


def build_dep(flag: str, name: str, op: Optional[str], ver: Optional[str]) -> str:
    prefix = (flag + " ") if flag else ""
    if op and ver:
        return f"{prefix}{name} {op} {ver}"
    return f"{prefix}{name}"


def fetch_latest_version(mod: str, want_factorio: Optional[str]) -> Optional[str]:
    url = f"https://mods.factorio.com/api/mods/{mod}"
    try:
        with urlopen(url, timeout=15) as r:
            data = json.load(r)
    except Exception as e:
        print(f"WARN: failed to fetch {mod}: {e}", file=sys.stderr)
        return None

    releases = data.get("releases") or []
    if not releases:
        return None

    def parse_ver(v: str) -> Tuple[int, ...]:
        # supports versions like 2.0.60
        return tuple(int(p) for p in v.split("."))

    # Prefer releases matching the desired factorio version if provided
    candidates = []
    for rel in releases:
        rel_info = rel.get("info_json") or {}
        fv = rel_info.get("factorio_version")
        version = rel.get("version")
        if not version:
            continue
        if want_factorio and fv and fv != want_factorio:
            # keep as fallback list but lower priority
            candidates.append((1, parse_ver(version), version))
        else:
            candidates.append((0, parse_ver(version), version))

    if not candidates:
        return None

    # Sort by priority (0 preferred), then semantic version descending
    candidates.sort(key=lambda t: (t[0], t[1]), reverse=True)
    # Because reverse=True sorts larger tuples first but also flips priority, re-sort with a key
    candidates.sort(key=lambda t: (t[0], t[1]), reverse=True)
    # Get best (highest version among preferred)
    best = None
    best_pri = None
    for pri, ver_tuple, ver in sorted(candidates, key=lambda t: (t[0], t[1]), reverse=True):
        if best is None or pri < best_pri or (pri == best_pri and ver_tuple > best[0]):
            best = (ver_tuple, ver)
            best_pri = pri
    return best[1] if best else None


def iter_infojson_paths(root: str) -> Iterable[str]:
    if os.path.isfile(root):
        yield root
        return
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn == "info.json":
                yield os.path.join(dirpath, fn)


def process_file(path: str, mode: str, write: bool, force: bool) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        info = json.load(f)

    factorio_version = info.get("factorio_version")
    name = info.get("name", "")
    deps: List[str] = list(info.get("dependencies") or [])

    changed = False
    new_deps: List[str] = []
    for dep in deps:
        try:
            flag, dep_name, op, ver = parse_dep(dep)
        except ValueError:
            # Keep as-is
            new_deps.append(dep)
            continue

        # Skip base and local packs, and self-references
        if dep_name in {"base"} | MOD_PACK_NAMES | {name}:
            new_deps.append(dep)
            continue

        # Respect existing comparator unless forcing
        if op and not force:
            new_deps.append(dep)
            continue

        latest = fetch_latest_version(dep_name, factorio_version)
        if not latest:
            new_deps.append(dep)
            continue

        new_op = "==" if mode == "eq" else ">="
        updated = build_dep(flag, dep_name, new_op, latest)
        if updated != dep:
            changed = True
            print(f"{path}: {dep}  ->  {updated}")
        new_deps.append(updated)

    if changed and write:
        info["dependencies"] = new_deps
        with open(path, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2)
            f.write("\n")
    return changed


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Pin latest Factorio mod versions in info.json files")
    ap.add_argument("--path", default=".", help="info.json file or root directory (default: .)")
    ap.add_argument("--write", action="store_true", help="write changes in-place (default: dry run)")
    ap.add_argument("--mode", choices=["gte", "eq"], default="gte", help="pin mode: 'gte' => >= latest (default), 'eq' => == exact latest")
    ap.add_argument("--force", action="store_true", help="override existing comparators if present")
    args = ap.parse_args(argv)

    any_changed = False
    for p in iter_infojson_paths(args.path):
        try:
            changed = process_file(p, mode=args.mode, write=args.write, force=args.force)
            any_changed = any_changed or changed
        except Exception as e:
            print(f"ERROR processing {p}: {e}", file=sys.stderr)

    if not any_changed:
        print("No changes (already pinned or no compatible releases found).")
    elif not args.write:
        print("\nDry run only. Re-run with --write to apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

