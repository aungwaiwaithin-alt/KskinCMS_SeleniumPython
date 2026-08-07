#!/usr/bin/env bash
# Restore MCP_Appium_Server/python/helpers if dynamic_data (and friends) went missing.
# Run on your Mac:
#   bash ~/AquaProjects/KskinCMS/one_click/restore_appium_helpers.sh
set -euo pipefail

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM="$AQUA/MCP_Appium_Server"
HELPERS="$APPIUM/python/helpers"
ZIP="$AQUA/MCP_Appium_Server.zip"
BACKUP_DIR="$AQUA/_helpers_backup_$(date +%Y%m%d_%H%M%S)"

echo "Appium  : $APPIUM"
echo "Helpers : $HELPERS"

if [[ -f "$HELPERS/dynamic_data.py" ]]; then
  echo "OK: dynamic_data.py already present — nothing to restore."
  ls "$HELPERS" | head
  exit 0
fi

echo "MISSING: helpers/dynamic_data.py"
echo "Current helpers contents:"
ls -la "$HELPERS" 2>/dev/null || echo "  (no helpers dir)"

# Backup whatever is there now
if [[ -d "$HELPERS" ]]; then
  mkdir -p "$BACKUP_DIR"
  cp -R "$HELPERS" "$BACKUP_DIR/helpers"
  echo "Backed up current helpers → $BACKUP_DIR/helpers"
fi

restore_from_zip() {
  local z="$1"
  local tmp
  tmp="$(mktemp -d)"
  echo "Extracting helpers from $z …”
  unzip -q -o "$z" -d "$tmp"
  # Find a helpers dir that contains dynamic_data.py
  local found
  found="$(find "$tmp" -type f -name 'dynamic_data.py' 2>/dev/null | head -1 || true)"
  if [[ -z "$found" ]]; then
    echo "ZIP has no dynamic_data.py: $z" >&2
    rm -rf "$tmp"
    return 1
  fi
  local src
  src="$(cd "$(dirname "$found")" && pwd)"
  mkdir -p "$(dirname "$HELPERS")"
  rm -rf "$HELPERS"
  cp -R "$src" "$HELPERS"
  rm -rf "$tmp"
  echo "Restored helpers from zip → $HELPERS"
  return 0
}

OK=0
if [[ -f "$ZIP" ]]; then
  restore_from_zip "$ZIP" && OK=1 || true
fi

# Also try common alternate zips / copies
if [[ "$OK" -eq 0 ]]; then
  for z in \
    "$HOME/Desktop/MCP_Appium_Server.zip" \
    "$AQUA/MCP_Appium_Server"/*.zip \
    "$HOME/Downloads/MCP_Appium_Server.zip"
  do
    [[ -f "$z" ]] || continue
    restore_from_zip "$z" && OK=1 && break || true
  done
fi

if [[ "$OK" -eq 0 ]]; then
  echo ""
  echo "Could not auto-restore. Do ONE of these:"
  echo "  1) Unzip ~/AquaProjects/MCP_Appium_Server.zip over MCP_Appium_Server"
  echo "  2) Copy helpers/ from a known-good machine/backup into:"
  echo "       $HELPERS"
  echo "  3) Ask Claude/Cursor to recreate helpers/dynamic_data.py from your suite"
  exit 1
fi

echo ""
echo "Verify:"
ls "$HELPERS" | head -30
python3 - <<PY
import sys
sys.path.insert(0, "$APPIUM/python")
import helpers.dynamic_data as d
print("IMPORT OK:", d.__file__)
PY
echo "Done. Re-run your one-click signup command."
