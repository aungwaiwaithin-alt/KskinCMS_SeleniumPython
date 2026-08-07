#!/bin/bash
# iOS Sign-Up + Login — one-click (Claude-style, self-contained)
cd "$(dirname "$0")" 2>/dev/null || true
set -uo pipefail

START_EPOCH="$(date +%s)"
SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
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


APPIUM_PY="${APPIUM_PY:-$HOME/AquaProjects/MCP_Appium_Server/python}"
BUNDLE="${IOS_UAT_BUNDLE:-enterprise.codigo.kskincustomer.uat}"
REPORT="$APPIUM_PY/reports/KS-SIGNUP-iOS-001_signup_login.html"
TEST="tests/test_signup_login_ios.py"

echo "========================================"
echo "  Kskin iOS — Sign-Up + Login"
echo "  $APPIUM_PY"
echo "  Bundle: $BUNDLE"
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

echo "[1/4] Appium..."
if ! curl -s http://127.0.0.1:4723/status >/dev/null 2>&1; then
  if command -v appium >/dev/null 2>&1; then
    nohup appium --port 4723 >reports/appium_ios_signup.log 2>&1 &
    for _ in $(seq 1 15); do curl -s http://127.0.0.1:4723/status >/dev/null 2>&1 && break; sleep 1; done
  else
    echo "  WARNING: appium not in PATH"
  fi
fi

echo "[2/4] Simulator/device..."
command -v xcrun >/dev/null && xcrun simctl list devices booted 2>/dev/null | head -10 || true

echo "[3/4] Ensure UAT app installed ($BUNDLE)"

echo "[4/4] pytest $TEST"
set +e
"$PY" -m pytest -s -vv "$TEST" --tb=short
ST=$?
set -e

open_fresh_report_only "$START_EPOCH" \
  "reports/*SIGNUP*iOS*.html" \
  "reports/*signup*ios*.html" || true
if [[ "$ST" -ne 0 ]]; then
  echo "RESULT: FAIL / collection error (exit $ST) — ignore any old report still open in Chrome."
fi
echo "Finished: $(date)  exit=$ST"
read -r -n 1 -s -p "Press any key to close..."
echo
exit "$ST"
