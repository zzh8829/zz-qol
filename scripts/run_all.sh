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
    declare -A changed=()
    for mod_dir in "${mods[@]}"; do
      if [ ! -f "$mod_dir/info.json" ]; then
        continue
      fi
      mod_name="$(python3 - "$mod_dir/info.json" <<'PY'
import json
import sys
with open(sys.argv[1], "r", encoding="utf-8") as f:
    data = json.load(f)
print(data.get("name", "").strip())
PY
)"
      bump="false"
      case "$mod_name" in
        zz-qol-plus)
          [ "${changed[zz-qol-lite]:-0}" = "1" ] && bump="true"
          ;;
        zz-qol-max)
          [ "${changed[zz-qol-plus]:-0}" = "1" ] && bump="true"
          ;;
        zz-qol-editor)
          [ "${changed[zz-qol-max]:-0}" = "1" ] && bump="true"
          ;;
      esac
      before="$(python3 - "$mod_dir/info.json" <<'PY'
import json
import sys
with open(sys.argv[1], "r", encoding="utf-8") as f:
    data = json.load(f)
print(data.get("version", "").strip())
PY
)"
      echo "==> pin: $mod_dir"
      if [ "$bump" = "true" ]; then
        python3 "$ROOT/scripts/pin_mod_versions.py" --path "$mod_dir/info.json" --bump "$@"
      else
        python3 "$ROOT/scripts/pin_mod_versions.py" --path "$mod_dir/info.json" "$@"
      fi
      after="$(python3 - "$mod_dir/info.json" <<'PY'
import json
import sys
with open(sys.argv[1], "r", encoding="utf-8") as f:
    data = json.load(f)
print(data.get("version", "").strip())
PY
)"
      if [ -n "$before" ] && [ "$before" != "$after" ]; then
        changed["$mod_name"]="1"
      fi
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
