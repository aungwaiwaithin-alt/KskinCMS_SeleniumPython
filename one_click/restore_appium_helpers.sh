#!/usr/bin/env bash
# Restore / recreate MCP_Appium_Server/python/helpers/dynamic_data.py
set -euo pipefail

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM="$AQUA/MCP_Appium_Server"
HELPERS="$APPIUM/python/helpers"
ZIP="$AQUA/MCP_Appium_Server.zip"
CMS="$AQUA/KskinCMS"
BACKUP_DIR="$AQUA/_helpers_backup_$(date +%Y%m%d_%H%M%S)"

echo "Appium  : $APPIUM"
echo "Helpers : $HELPERS"

if [[ -f "$HELPERS/dynamic_data.py" ]]; then
  echo "OK: dynamic_data.py already present"
  ls "$HELPERS"
  python3 - <<PY
import sys
sys.path.insert(0, "$APPIUM/python")
from helpers.dynamic_data import next_android_run_values
print("import OK", next_android_run_values())
PY
  exit 0
fi

echo "MISSING: helpers/dynamic_data.py"
echo "Current helpers:"
ls -la "$HELPERS" 2>/dev/null || echo "(none)"

if [[ -d "$HELPERS" ]]; then
  mkdir -p "$BACKUP_DIR"
  cp -R "$HELPERS" "$BACKUP_DIR/helpers"
  echo "Backed up -> $BACKUP_DIR/helpers"
fi

restore_from_zip() {
  local z="$1"
  local tmp found src
  [[ -f "$z" ]] || return 1
  tmp="$(mktemp -d)"
  echo "Scanning zip: $z"
  unzip -l "$z" | grep -i 'dynamic_data.py' || true
  unzip -q -o "$z" -d "$tmp"
  found="$(find "$tmp" -type f -name 'dynamic_data.py' 2>/dev/null | head -1 || true)"
  if [[ -z "$found" ]]; then
    echo "No dynamic_data.py inside zip"
    rm -rf "$tmp"
    return 1
  fi
  src="$(cd "$(dirname "$found")" && pwd)"
  mkdir -p "$HELPERS"
  # Copy all files from that helpers dir into place (merge, do not delete step_report)
  cp -R "$src"/. "$HELPERS"/
  rm -rf "$tmp"
  echo "Restored helpers files from zip"
  return 0
}

OK=0
if [[ -f "$ZIP" ]]; then
  restore_from_zip "$ZIP" && OK=1 || true
fi
if [[ "$OK" -eq 0 ]]; then
  for z in "$HOME/Desktop/MCP_Appium_Server.zip" "$HOME/Downloads/MCP_Appium_Server.zip"; do
    [[ -f "$z" ]] || continue
    restore_from_zip "$z" && OK=1 && break || true
  done
fi

# If zip did not help, generate a stub from signup tests
if [[ ! -f "$HELPERS/dynamic_data.py" ]]; then
  echo "Generating stub helpers/dynamic_data.py from signup tests..."
  GEN="$CMS/one_click/generate_dynamic_data.py"
  if [[ ! -f "$GEN" ]]; then
    GEN="$(cd "$(dirname "$0")" && pwd)/generate_dynamic_data.py"
  fi
  python3 "$GEN"
fi

echo ""
echo "Verify:"
ls -la "$HELPERS"
python3 - <<PY
import sys
sys.path.insert(0, "$APPIUM/python")
from helpers.dynamic_data import next_android_run_values
v = next_android_run_values()
print("IMPORT OK:", getattr(v, "email", v))
PY
echo "Done. Now re-run the one-click signup command."
