#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

usage() {
  cat <<'EOF'
Usage:
  scripts/run_all.sh pin [pin_mod_versions args...]
  scripts/run_all.sh logos [generate_logos args...]
  scripts/run_all.sh release [release_mod args...]

Runs the selected script once per pack in a fixed order:
qol-1-lite, qol-2-plus, qol-3-max, qol-4-editor.
EOF
}

if [ "${#}" -lt 1 ]; then
  usage
  exit 1
fi

cmd="$1"
shift

mods=(
  "$ROOT/qol-1-lite"
  "$ROOT/qol-2-plus"
  "$ROOT/qol-3-max"
  "$ROOT/qol-4-editor"
)

case "$cmd" in
  pin)
    for mod_dir in "${mods[@]}"; do
      if [ ! -f "$mod_dir/info.json" ]; then
        continue
      fi
      echo "==> pin: $mod_dir"
      python3 "$ROOT/scripts/pin_mod_versions.py" --path "$mod_dir/info.json" "$@"
    done
    ;;
  logos)
    for mod in "${mods[@]}"; do
      echo "==> logos: $mod"
      python3 "$ROOT/scripts/generate_logos.py" --path "$mod" "$@"
    done
    ;;
  release)
    for mod in "${mods[@]}"; do
      echo "==> release: $mod"
      python3 "$ROOT/scripts/release_mod.py" --path "$mod" "$@"
    done
    ;;
  *)
    usage
    exit 1
    ;;
esac
