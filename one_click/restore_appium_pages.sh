#!/usr/bin/env bash
# Restore missing Appium pages/*.py from MCP_Appium_Server.zip if present.
set -euo pipefail

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM_PY="$AQUA/MCP_Appium_Server/python"
PAGES="$APPIUM_PY/pages"
ZIP="$AQUA/MCP_Appium_Server.zip"

echo "pages → $PAGES"
mkdir -p "$PAGES"

need_restore=0
[[ -f "$PAGES/permissions_android_page.py" ]] || need_restore=1

if [[ "$need_restore" -eq 0 ]]; then
  echo "OK: permissions_android_page.py already present"
  ls "$PAGES" | head -30
  exit 0
fi

echo "MISSING: pages/permissions_android_page.py"
echo "Current pages/:"
ls -la "$PAGES" 2>/dev/null || echo "(empty/missing)"

restore_pages_from_zip() {
  local z="$1" tmp found
  [[ -f "$z" ]] || return 1
  tmp="$(mktemp -d)"
  echo "Scanning zip: $z"
  unzip -l "$z" | grep -i 'permissions_android_page.py' || true
  unzip -q -o "$z" -d "$tmp"
  found="$(find "$tmp" -type f -name 'permissions_android_page.py' 2>/dev/null | head -1 || true)"
  if [[ -z "$found" ]]; then
    echo "Zip has no permissions_android_page.py"
    rm -rf "$tmp"
    return 1
  fi
  local src
  src="$(cd "$(dirname "$found")" && pwd)"
  echo "Copying pages from: $src"
  cp -R "$src"/. "$PAGES"/
  rm -rf "$tmp"
  return 0
}

OK=0
for z in "$ZIP" "$HOME/Desktop/MCP_Appium_Server.zip" "$HOME/Downloads/MCP_Appium_Server.zip"; do
  [[ -f "$z" ]] || continue
  if restore_pages_from_zip "$z"; then OK=1; break; fi
done

if [[ "$OK" -eq 0 ]]; then
  echo ""
  echo "Could not restore pages from zip."
  echo "Paste this output and also run:"
  echo "  ls -la \"$PAGES\""
  echo "  ls -la \"$AQUA\"/*.zip 2>/dev/null"
  echo "Or restore MCP_Appium_Server/python/pages from Time Machine / backup."
  exit 1
fi

echo ""
echo "Verify:"
ls -la "$PAGES" | head -40
python3 - <<PY
import sys
sys.path.insert(0, "$APPIUM_PY")
from pages.permissions_android_page import PermissionsAndroidPage
print("IMPORT OK:", PermissionsAndroidPage)
PY
echo "Done. Re-run the one-click."
