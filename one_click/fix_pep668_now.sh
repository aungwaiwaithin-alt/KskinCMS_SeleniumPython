#!/usr/bin/env bash
# One-shot Mac fix for externally-managed-environment (PEP668) on mobile one-clicks.
# Paste into Terminal:
#   bash ~/AquaProjects/KskinCMS/one_click/fix_pep668_now.sh
set -euo pipefail

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
CMS=""
for c in "$AQUA/KskinCMS" "$AQUA/KskinCMS_SeleniumPython" "$AQUA/kskincms_seleniumpython"; do
  [[ -d "$c/.git" ]] && CMS="$c" && break
done
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
[[ -z "$CMS" && -d "$SCRIPT_DIR/../.git" ]] && CMS="$(cd "$SCRIPT_DIR/.." && pwd)"
[[ -n "$CMS" ]] || { echo "ERROR: KskinCMS repo not found"; exit 1; }

echo "=== PEP668 fix ==="
echo "CMS: $CMS"
cd "$CMS"

echo "[1/4] git stash -u && git pull ..."
git stash -u || true
git pull --ff-only || git pull

AND_SRC="$CMS/one_click/originals/run-android-full-regression.command"
if ! grep -q 'KSKIN_MOBILE_RUNNER_VENV' "$AND_SRC" 2>/dev/null; then
  echo "ERROR: pulled code still missing full-regression venv runner." >&2
  echo "Branch may be behind. Show: git log -1 --oneline && ls one_click/originals" >&2
  exit 1
fi
if [[ ! -f "$CMS/one_click/mobile_venv.sh" ]]; then
  echo "ERROR: missing one_click/mobile_venv.sh after pull." >&2
  exit 1
fi

echo "[2/4] install mobile originals + wrappers ..."
bash "$CMS/one_click/install_mobile_originals.sh"

echo "[3/4] ensure Appium helpers/dynamic_data.py ..."
if [[ ! -f "$AQUA/MCP_Appium_Server/python/helpers/dynamic_data.py" ]]; then
  python3 "$CMS/one_click/generate_dynamic_data.py" || true
fi

echo "[4/4] pre-create Appium .venv (optional warm-up) ..."
APPIUM_PY="$AQUA/MCP_Appium_Server/python"
if [[ -d "$APPIUM_PY" ]]; then
  BASE_PY=""
  for c in /usr/local/bin/python3 /opt/homebrew/bin/python3.12 /opt/homebrew/bin/python3; do
    [[ -x "$c" ]] || continue
    if "$c" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
      BASE_PY="$c"; break
    fi
  done
  if [[ -n "$BASE_PY" ]]; then
    if [[ ! -x "$APPIUM_PY/.venv/bin/python" ]]; then
      echo "Creating $APPIUM_PY/.venv ..."
      "$BASE_PY" -m venv "$APPIUM_PY/.venv"
    fi
    "$APPIUM_PY/.venv/bin/python" -m pip install -U pip setuptools wheel >/dev/null
    "$APPIUM_PY/.venv/bin/python" -m pip install -U pytest Appium-Python-Client selenium
    echo "venv python: $("$APPIUM_PY/.venv/bin/python" -V)"
  fi
fi

DEST=""
for d in "$HOME/Desktop/One click bash files" "$HOME/One click bash files"; do
  [[ -d "$d" ]] && DEST="$d" && break
done
echo ""
echo "VERIFY Desktop runners (must print KSKIN_MOBILE_RUNNER_VENV):"
if [[ -n "$DEST" ]]; then
  echo "--- signup ---"
  grep -n 'KSKIN_MOBILE_RUNNER_VENV' "$DEST/.legacy/run-android-signup-login.command" | head -3 || true
  echo "--- full regression ---"
  grep -n 'KSKIN_MOBILE_RUNNER_VENV' "$DEST/.legacy/run-android-full-regression.command" | head -3 || true
  echo "--- mobile_venv.sh ---"
  ls -la "$DEST/mobile_venv.sh" "$CMS/one_click/mobile_venv.sh" 2>/dev/null || true
  echo "Wrapper first lines (full regression):"
  head -5 "$DEST/run-android-full-regression.command"
fi

echo ""
echo "DONE. Double-click either:"
echo "  run-android-signup-login.command"
echo "  run-android-full-regression.command"
echo "Header MUST show KSKIN_MOBILE_RUNNER_VENV=... and CMS must NOT be NOT FOUND."
echo "Using Python: .../MCP_Appium_Server/python/.venv/bin/python"
