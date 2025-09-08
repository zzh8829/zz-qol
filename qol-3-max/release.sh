#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HERE/.." && pwd)"
python3 "$REPO_ROOT/scripts/release_mod.py" --path "$HERE" "$@"

