#!/usr/bin/env bash
# Restore MCP_Appium_Server/python/helpers/dynamic_data.py from git/zip.
# Never invents the long YYMMDDHHMMSS## email stub.
set -euo pipefail

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM="$AQUA/MCP_Appium_Server"
HELPERS="$APPIUM/python/helpers"
DD="$HELPERS/dynamic_data.py"
ZIP="$AQUA/MCP_Appium_Server.zip"
CMS="$AQUA/KskinCMS"
[[ -d "$CMS/one_click" ]] || CMS="$(cd "$(dirname "$0")/.." && pwd)"
SHA="${APPIUM_RESTORE_SHA:-8f544632f1b717687dd5be6df13df353ca0827b8}"

echo "Appium  : $APPIUM"
echo "Helpers : $HELPERS"

is_long_stub() {
  [[ -f "$1" ]] || return 1
  grep -qE 'Auto-generated|compat stub|restored stub|strftime\("%y%m%d%H%M%S"\)' "$1" 2>/dev/null
}

# Prefer the full Claude restore path
if [[ -f "$CMS/one_click/restore_claude_mobile_originals.sh" ]]; then
  echo "Delegating to restore_claude_mobile_originals.sh ..."
  exec bash "$CMS/one_click/restore_claude_mobile_originals.sh"
fi

if [[ -f "$DD" ]] && ! is_long_stub "$DD"; then
  echo "OK: non-stub dynamic_data.py present"
  ls "$HELPERS"
  exit 0
fi

if is_long_stub "$DD"; then
  mv -f "$DD" "$DD.long_stub_bak_$(date +%Y%m%d_%H%M%S)"
  echo "Quarantined long-email stub"
fi

if [[ -d "$APPIUM/.git" ]]; then
  cd "$APPIUM"
  if git cat-file -e "${SHA}:python/helpers/dynamic_data.py" 2>/dev/null; then
    git checkout "$SHA" -- python/helpers/dynamic_data.py
    echo "Restored from git $SHA"
  fi
fi

if [[ ! -f "$DD" ]] && [[ -f "$ZIP" ]]; then
  tmp="$(mktemp -d)"
  unzip -q -o "$ZIP" -d "$tmp"
  found="$(find "$tmp" -type f -name 'dynamic_data.py' 2>/dev/null | head -1 || true)"
  if [[ -n "$found" ]] && ! is_long_stub "$found"; then
    mkdir -p "$HELPERS"
    cp -f "$found" "$DD"
    echo "Restored from zip"
  fi
  rm -rf "$tmp"
fi

if [[ ! -f "$DD" ]]; then
  echo "ERROR: original dynamic_data.py not found. Run restore_claude_mobile_originals.sh"
  exit 1
fi

echo "Verify:"
ls -la "$DD"
python3 - <<PY
import sys
sys.path.insert(0, "$APPIUM/python")
from helpers.dynamic_data import next_android_run_values
v = next_android_run_values()
print("email:", getattr(v, "signup_email", None) or getattr(v, "email", None))
PY
