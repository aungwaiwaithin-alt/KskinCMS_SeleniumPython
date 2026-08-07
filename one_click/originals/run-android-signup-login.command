#!/bin/bash
# Android Sign-Up + Login — one-click (Claude-style, self-contained)
# Double-click from Finder. Uses Appium project .venv (Homebrew PEP668-safe).
cd "$(dirname "$0")" 2>/dev/null || true
set -uo pipefail
START_EPOCH="$(date +%s)"
SELF_DIR="$(cd "$(dirname "$0")" && pwd)"

APPIUM_PY="${APPIUM_PY:-$HOME/AquaProjects/MCP_Appium_Server/python}"
PKG="${ANDROID_UAT_PACKAGE:-com.kskinfacial.customer.uat}"
TEST="tests/test_signup_login_android.py"

# Load shared helpers if installed beside this .command
if [[ -f "$SELF_DIR/mobile_common.inc.sh" ]]; then
  # shellcheck disable=SC1091
  source "$SELF_DIR/mobile_common.inc.sh"
elif [[ -f "$HOME/AquaProjects/KskinCMS/one_click/mobile_common.inc.sh" ]]; then
  # shellcheck disable=SC1091
  source "$HOME/AquaProjects/KskinCMS/one_click/mobile_common.inc.sh"
else
  open_fresh_report_only() {
    local start_epoch="$1"; shift
    local best="" best_m=0 f m g
    for g in "$@"; do
      for f in $g; do
        [[ -f "$f" ]] || continue
        m="$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null || echo 0)"
        if [[ "$m" -ge "$start_epoch" && "$m" -ge "$best_m" ]]; then best="$f"; best_m="$m"; fi
      done
    done
    if [[ -n "$best" ]]; then
      echo "Fresh report → Chrome: $best"
      open -a "Google Chrome" "$best" 2>/dev/null || open "$best" || true
      return 0
    fi
    echo "ERROR: No NEW HTML report from this run — not opening any old report."
    return 1
  }
fi

echo "========================================"
echo "  Kskin Android — Sign-Up + Login"
echo "  $APPIUM_PY"
echo "  Started: $(date)"
echo "========================================"

[[ -d "$APPIUM_PY" ]] || { echo "ERROR: missing $APPIUM_PY"; read -r -p "Press Enter…" _; exit 1; }

BASE_PY=""
for c in /usr/local/bin/python3 /opt/homebrew/bin/python3.12 /opt/homebrew/bin/python3; do
  [[ -x "$c" ]] || continue
  "$c" -c 'import sys; raise SystemExit(0 if sys.version_info>=(3,9) else 1)' 2>/dev/null && BASE_PY="$c" && break
done
[[ -n "$BASE_PY" ]] || { echo "ERROR: need Python >= 3.9"; read -r -p "Press Enter…" _; exit 1; }
VENV="$APPIUM_PY/.venv"
PY="$VENV/bin/python"
[[ -x "$PY" ]] || "$BASE_PY" -m venv "$VENV" || { echo "ERROR: venv failed"; read -r -p "Press Enter…" _; exit 1; }
export PATH="$VENV/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"
export PYTHONPATH="$APPIUM_PY"
export PYTHONUNBUFFERED=1
"$PY" -c 'import pytest,appium' 2>/dev/null || "$PY" -m pip install -U pytest Appium-Python-Client selenium
echo "Python: $PY ($("$PY" -V))"

cd "$APPIUM_PY" || exit 1
mkdir -p reports

# Fail fast if page objects missing (this was why the old July report opened)
if [[ ! -f pages/permissions_android_page.py ]]; then
  echo "ERROR: missing pages/permissions_android_page.py — pytest cannot collect."
  echo "pages/ listing:"
  ls -la pages 2>/dev/null || echo "  (no pages/ directory)"
  echo ""
  echo "Fix: bash ~/AquaProjects/KskinCMS/one_click/restore_appium_pages.sh"
  echo "Or restore MCP_Appium_Server/python/pages from backup/zip/Time Machine."
  echo "NOT opening any old HTML report."
  read -r -n 1 -s -p "Press any key to close..."
  echo
  exit 2
fi

echo "[1/4] Appium..."
if ! curl -s http://127.0.0.1:4723/status >/dev/null 2>&1; then
  if command -v appium >/dev/null 2>&1; then
    nohup appium --port 4723 >reports/appium_android_signup.log 2>&1 &
    for _ in $(seq 1 15); do curl -s http://127.0.0.1:4723/status >/dev/null 2>&1 && break; sleep 1; done
  else
    echo "  WARNING: appium not in PATH"
  fi
fi

echo "[2/4] Device..."
command -v adb >/dev/null || { echo "ERROR: adb not found"; read -r -p "Press Enter…" _; exit 1; }
adb start-server >/dev/null 2>&1 || true
DEV="$(adb devices | awk 'NR>1 && $2=="device"{print $1}')"
[[ -n "$DEV" ]] || { echo "ERROR: no Android device"; read -r -p "Press Enter…" _; exit 1; }
echo "  $DEV"

echo "[3/4] Clean install baseline..."
adb uninstall "$PKG" >/dev/null 2>&1 || true

echo "[4/4] pytest $TEST"
set +e
"$PY" -m pytest -s -vv "$TEST" --tb=short
ST=$?
set -e

open_fresh_report_only "$START_EPOCH" \
  "reports/*SIGNUP*AND*.html" \
  "reports/*signup*android*.html" \
  "reports/KS-SIGNUP-AND-001_signup_login.html" || true

if [[ "$ST" -ne 0 ]]; then
  echo "RESULT: FAIL / collection error (exit $ST) — ignore any old report still open in Chrome."
fi
echo "Finished: $(date)  exit=$ST"
read -r -n 1 -s -p "Press any key to close..."
echo
exit "$ST"
