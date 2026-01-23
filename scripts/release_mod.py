#!/usr/bin/env python3
"""
Build and (optionally) upload a Factorio modpack release.

Features:
- Reads name/version from <moddir>/info.json
- Creates dist/<name>_<version>.zip with proper inner folder structure
- Optional upload to Mod Portal via v2 publish API using a single API key

Environment for upload (--upload):
- FACTORIO_TOKEN: API key with "ModPortal: Upload Mods" permission (from https://factorio.com/profile)

macOS convenience
- If the above env vars are not set, this script will attempt to read
  "service-username" and "service-token" from your local
  player-data.json (e.g.,
  ~/Library/Application Support/factorio/player-data.json).

Usage:
  scripts/release_mod.py --path qol-1-lite [--upload] [--changelog CHANGELOG.md]

This script avoids non-stdlib dependencies; network ops use curl.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
from zipfile import ZipFile, ZIP_DEFLATED


EXCLUDE_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    ".DS_Store",
    ".idea",
    ".vscode",
}


def load_info(mod_dir: Path) -> Dict[str, str]:
    info_path = mod_dir / "info.json"
    if not info_path.exists():
        raise SystemExit(f"Missing info.json in {mod_dir}")
    try:
        data = json.loads(info_path.read_text())
    except Exception as e:
        raise SystemExit(f"Failed to parse {info_path}: {e}")

    for key in ("name", "version"):
        if key not in data or not isinstance(data[key], str) or not data[key].strip():
            raise SystemExit(f"info.json is missing required field '{key}'")
    return data  # type: ignore[return-value]


def should_exclude(path: Path) -> bool:
    name = path.name
    if name in EXCLUDE_NAMES:
        return True
    # exclude hidden files/folders at any level except "." and ".."
    if name.startswith('.') and name not in (".", "..") and name != ".".join(name.split('.')):
        # Keep dotfiles only if they are common and safe. Otherwise skip.
        return True
    return False


def build_zip(mod_dir: Path, out_dir: Path) -> Path:
    info = load_info(mod_dir)
    name = info["name"].strip()
    version = info["version"].strip()
    inner_root = f"{name}_{version}"
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"{inner_root}.zip"

    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(mod_dir):
            root_path = Path(root)
            # prunes
            dirs[:] = [d for d in dirs if not should_exclude(root_path / d)]
            for fname in files:
                fpath = root_path / fname
                if should_exclude(fpath):
                    continue
                if fpath.name in {"release.sh"}:
                    continue
                # compute arcname with inner_root prefix, path relative to mod_dir
                rel = fpath.relative_to(mod_dir)
                arcname = str(Path(inner_root) / rel)
                zf.write(fpath, arcname)

    return zip_path


def run_curl_json(url: str, payload: Dict[str, str], headers: Optional[Dict[str, str]] = None) -> Dict:
    cmd = [
        "curl", "-sS", "-f", "-X", "POST",
    ]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    cmd += ["-H", "Content-Type: application/json"]
    cmd += ["--data", json.dumps(payload)]
    cmd += [url]
    try:
        out = subprocess.check_output(cmd)
    except subprocess.CalledProcessError as e:
        sys.stderr.write(e.output.decode(errors="ignore"))
        raise SystemExit(f"curl JSON request failed: {' '.join(shlex.quote(c) for c in cmd)}\nExit {e.returncode}")
    try:
        return json.loads(out.decode())
    except Exception as e:
        raise SystemExit(f"Failed to parse JSON response from {url}: {e}\nRaw: {out[:200]}...")


def run_curl_form(url: str, fields: Dict[str, str], files: Optional[Dict[str, Path]] = None, headers: Optional[Dict[str, str]] = None) -> str:
    cmd: List[str] = ["curl", "-sS", "-f", "-X", "POST"]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    for k, v in fields.items():
        cmd += ["-F", f"{k}={v}"]
    if files:
        for k, p in files.items():
            cmd += ["-F", f"{k}=@{str(p)}"]
    cmd += [url]
    try:
        out = subprocess.check_output(cmd)
    except subprocess.CalledProcessError as e:
        sys.stderr.write(e.output.decode(errors="ignore"))
        raise SystemExit(f"curl form request failed: {' '.join(shlex.quote(c) for c in cmd)}\nExit {e.returncode}")
    return out.decode()


def maybe_read_changelog(path: Optional[Path]) -> Optional[str]:
    if not path:
        return None
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    return text or None


def upload_v2(mod_name: str, zip_path: Path, description: Optional[str]) -> None:
    """Upload via Factorio's v2 upload API using only FACTORIO_TOKEN.

    Flow:
      1) POST to /api/v2/mods/releases/init_upload with header Authorization: Bearer <token>
         Form field: mod=<mod_name>
         -> returns { upload_url }
      2) POST to <upload_url> with multipart form: file=@zip
         -> returns { success: true }
    """
    token = os.environ.get("FACTORIO_TOKEN")
    if not token:
        raise SystemExit("--upload requires FACTORIO_TOKEN (with ModPortal: Publish Mods permission).")

    init_url = "https://mods.factorio.com/api/v2/mods/releases/init_upload"
    headers = {"Authorization": f"Bearer {token}"}
    init_resp = run_curl_form(init_url, {"mod": mod_name}, headers=headers)
    try:
        init_json = json.loads(init_resp)
    except Exception as e:
        raise SystemExit(f"Failed to parse init_publish response: {e}\nRaw: {init_resp[:200]}...")
    if "error" in init_json:
        raise SystemExit(f"init_upload error: {init_json.get('error')}: {init_json.get('message')}")
    upload_url = init_json.get("upload_url")
    if not upload_url:
        raise SystemExit("init_upload did not return upload_url")

    fields: Dict[str, str] = {}
    if description:
        fields["description"] = description
    upload_resp = run_curl_form(upload_url, fields, files={"file": zip_path})
    try:
        uploaded = json.loads(upload_resp)
    except Exception as e:
        raise SystemExit(f"Failed to parse finish_upload response: {e}\nRaw: {upload_resp[:200]}...")
    if not uploaded.get("success"):
        raise SystemExit(f"finish_upload failed: {uploaded}")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Build and optionally upload a Factorio mod release")
    ap.add_argument("--path", default=".", help="Path to the mod directory containing info.json")
    ap.add_argument("--out-dir", default="dist", help="Output directory for built zips")
    ap.add_argument("--upload", action="store_true", help="Upload to Factorio Mod Portal (v2 publish API)")
    ap.add_argument("--changelog", default=None, help="Path to changelog file to include in release")
    args = ap.parse_args(argv)

    mod_dir = Path(args.path).resolve()
    out_dir = Path(args.out_dir).resolve()

    info = load_info(mod_dir)
    name = info["name"].strip()
    version = info["version"].strip()

    # Build zip
    zip_path = build_zip(mod_dir, out_dir)
    print(f"Built: {zip_path}")

    # Upload if requested
    if args.upload:
        changelog_text = maybe_read_changelog(Path(args.changelog)) if args.changelog else None
        print(f"Uploading {name} {version} to Mod Portal...")
        upload_v2(name, zip_path, changelog_text)
        print("Upload completed.")
    else:
        print("Dry run (no upload). To upload, pass --upload and set FACTORIO_TOKEN.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
