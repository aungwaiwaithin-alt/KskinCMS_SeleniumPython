#!/usr/bin/env bash
# One-shot: pull + install simple Claude-style mobile one-clicks to Desktop.
set -euo pipefail

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
CMS=""
for c in "$AQUA/KskinCMS" "$AQUA/KskinCMS_SeleniumPython" "$AQUA/kskincms_seleniumpython"; do
  [[ -d "$c/.git" ]] && CMS="$c" && break
done
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
[[ -z "$CMS" && -d "$SCRIPT_DIR/../.git" ]] && CMS="$(cd "$SCRIPT_DIR/.." && pwd)"
[[ -n "$CMS" ]] || { echo "ERROR: KskinCMS not found"; exit 1; }

echo "CMS: $CMS"
cd "$CMS"
git stash -u || true
git pull --ff-only || git pull

bash "$CMS/one_click/install_mobile_simple.sh"

# Warm venv once
APPIUM_PY="$AQUA/MCP_Appium_Server/python"
if [[ -d "$APPIUM_PY" ]]; then
  BASE=""
  for c in /usr/local/bin/python3 /opt/homebrew/bin/python3.12 /opt/homebrew/bin/python3; do
    [[ -x "$c" ]] || continue
    "$c" -c 'import sys; raise SystemExit(0 if sys.version_info>=(3,9) else 1)' 2>/dev/null && BASE="$c" && break
  done
  if [[ -n "$BASE" ]]; then
    [[ -x "$APPIUM_PY/.venv/bin/python" ]] || "$BASE" -m venv "$APPIUM_PY/.venv"
    "$APPIUM_PY/.venv/bin/python" -m pip install -U pip pytest Appium-Python-Client selenium >/dev/null
    echo "venv ready: $("$APPIUM_PY/.venv/bin/python" -V)"
  fi
fi

echo ""
echo "DONE. Double-click run-android-full-regression.command"
echo "It should say 'Claude-style, self-contained' — not 'thin wrapper'."
