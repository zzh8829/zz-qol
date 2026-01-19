#!/usr/bin/env python3
"""
Pin Factorio mod dependency versions in info.json files.

Features
- Scans a single info.json file.
- For each dependency, fetches the latest portal release compatible with the pack's factorio_version.
- Preserves `!` (conflict) and `?` (optional) flags and leaves `base` and local pack names unmodified.
- Skips dependencies that already have a comparator unless `--force`.
- Modes: `>=` (default) or exact `==` pinning.
- When dependencies or remote versions change, bumps this pack's patch version.

Examples
  Dry run for a pack:
    scripts/pin_mod_versions.py --path qol-4-editor/info.json

  Write changes in-place, pin exact versions:
    scripts/pin_mod_versions.py --write --mode eq

  Only a specific pack file:
    scripts/pin_mod_versions.py --path qol-4-editor/info.json --write

  Force a patch bump (e.g., local dependency changed):
    scripts/pin_mod_versions.py --path qol-4-editor/info.json --bump --write
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Optional, Tuple
from urllib.request import urlopen

MOD_PACK_NAMES = {"zz-qol-lite", "zz-qol-plus", "zz-qol-max", "zz-qol-editor"}
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


def parse_version(v: str) -> Tuple[int, int, int]:
    parts = [int(p) for p in v.split(".")]
    while len(parts) < 3:
        parts.append(0)
    return parts[0], parts[1], parts[2]


def bump_patch(local_ver: str, remote_ver: Optional[str]) -> str:
    local_tuple = parse_version(local_ver)
    remote_tuple = parse_version(remote_ver) if remote_ver else (0, 0, 0)
    base = max(local_tuple, remote_tuple)
    return f"{base[0]}.{base[1]}.{base[2] + 1}"


def resolve_infojson_path(path: str) -> str:
    if os.path.isdir(path):
        candidate = os.path.join(path, "info.json")
        if os.path.isfile(candidate):
            return candidate
        raise SystemExit(f"Missing info.json in {path}")
    if os.path.isfile(path):
        if os.path.basename(path) != "info.json":
            raise SystemExit(f"Expected info.json, got {path}")
        return path
    raise SystemExit(f"Path not found: {path}")


def process_file(path: str, mode: str, write: bool, force: bool, upgrade: bool, bump: bool) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        info = json.load(f)

    factorio_version = info.get("factorio_version")
    name = info.get("name", "")
    current_version = info.get("version", "").strip()
    deps: List[str] = list(info.get("dependencies") or [])

    print(f"{path}: processing {len(deps)} dependencies (factorio_version={factorio_version or 'none'})")
    changed = False
    deps_changed = False
    deps_latest_mismatch = False
    new_deps: List[str] = []
    for dep in deps:
        try:
            flag, dep_name, op, ver = parse_dep(dep)
        except ValueError:
            # Keep as-is
            print(f"{path}: skip unparsable dependency: {dep!r}")
            new_deps.append(dep)
            continue

        # Skip base and local packs, and self-references
        if dep_name in {"base"} | MOD_PACK_NAMES | {name}:
            print(f"{path}: skip local/base/self: {dep_name}")
            new_deps.append(dep)
            continue

        # Respect existing comparator unless forcing or upgrading
        if op and not (force or upgrade):
            print(f"{path}: skip already pinned: {dep_name} {op} {ver}")
            new_deps.append(dep)
            continue
        if op and upgrade and op not in {">=", "==", "="}:
            print(f"{path}: skip upgrade unsupported comparator: {dep_name} {op} {ver}")
            new_deps.append(dep)
            continue

        latest = fetch_latest_version(dep_name, factorio_version)
        if not latest:
            print(f"{path}: skip no compatible releases: {dep_name}")
            new_deps.append(dep)
            continue

        if ver and latest != ver:
            deps_latest_mismatch = True
        print(f"{path}: {dep_name} current={ver or 'none'} latest={latest}")
        # Upgrade note: for >= pins, default to latest major.minor; if already pinned to a patch, keep patch upgrades.
        latest_parts = latest.split(".")
        gte_version = ".".join(latest_parts[:2]) if len(latest_parts) >= 2 else latest
        if upgrade and op in {">=", "="} and ver and len(ver.split(".")) >= 3:
            gte_version = latest
        if op and not force:
            new_op = op
        else:
        new_op = "==" if mode == "eq" else ">="
        new_ver = gte_version if new_op == ">=" else latest
        updated = build_dep(flag, dep_name, new_op, new_ver)
        if updated != dep:
            deps_changed = True
            changed = True
            print(f"{path}: {dep}  ->  {updated}")
        new_deps.append(updated)

    remote_latest = fetch_latest_version(name, factorio_version) if name else None
    if remote_latest:
        print(f"{path}: {name} local_version={current_version or 'none'} remote_latest={remote_latest}")
    remote_mismatch = bool(remote_latest and current_version and remote_latest != current_version)

    bump_reason = bump or deps_changed or deps_latest_mismatch or remote_mismatch
    if bump_reason and current_version:
        new_version = bump_patch(current_version, remote_latest)
        if new_version != current_version:
            changed = True
            info["version"] = new_version
            print(f"{path}: version bump {current_version} -> {new_version}")

    if changed and write:
        info["dependencies"] = new_deps
        with open(path, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2)
            f.write("\n")
    return changed


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Pin latest Factorio mod versions in info.json files")
    ap.add_argument("--path", default=".", help="Path to an info.json file (or a folder containing it)")
    ap.add_argument("--write", action="store_true", help="write changes in-place (default: dry run)")
    ap.add_argument("--mode", choices=["gte", "eq"], default="gte", help="pin mode: 'gte' => >= latest (default), 'eq' => == exact latest")
    ap.add_argument("--force", action="store_true", help="override existing comparators if present")
    ap.add_argument("--upgrade", action="store_true", help="update already pinned dependencies to latest")
    ap.add_argument("--bump", action="store_true", help="force a version patch bump (e.g., local dependency changed)")
    args = ap.parse_args(argv)

    any_changed = False
    path = resolve_infojson_path(args.path)
    try:
        changed = process_file(
            path,
            mode=args.mode,
            write=args.write,
            force=args.force,
            upgrade=args.upgrade,
            bump=args.bump,
        )
        any_changed = any_changed or changed
    except Exception as e:
        print(f"ERROR processing {path}: {e}", file=sys.stderr)

    if not any_changed:
        print("No changes (already pinned or no compatible releases found).")
    elif not args.write:
        print("\nDry run only. Re-run with --write to apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
