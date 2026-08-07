#!/bin/bash
# Clean Android signup+login one-click (greenfield — not the old patched suite)
set -uo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
REPORT="$ROOT/reports/KS-CLEAN-AND-001_signup_login.html"
export CLEAN_ANDROID_SIGNUP_REPORT="$REPORT"
export STEP_PAUSE_SEC="${STEP_PAUSE_SEC:-2.0}"
export STEP_PRE_PAUSE_SEC="${STEP_PRE_PAUSE_SEC:-0.6}"
export ANDROID_UAT_PACKAGE="${ANDROID_UAT_PACKAGE:-com.kskinfacial.customer.uat}"

echo "=============================================================="
echo "  KS-CLEAN-AND-001  Android signup + login (CLEAN)"
echo "  Suite  : $ROOT"
echo "  Report : $REPORT"
echo "  Package: $ANDROID_UAT_PACKAGE"
echo "  Started: $(date)"
echo "=============================================================="

# Prefer package .venv; create if missing
PY="$ROOT/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  BASE=""
  for c in /opt/homebrew/bin/python3.12 /opt/homebrew/bin/python3 /usr/local/bin/python3 /usr/bin/python3; do
    [[ -x "$c" ]] || continue
    "$c" -c 'import sys; raise SystemExit(0 if sys.version_info>=(3,9) else 1)' 2>/dev/null && BASE="$c" && break
  done
  if [[ -z "$BASE" ]]; then
    echo "ERROR: need Python >= 3.9"
    read -r -p "Press Enter…" _
    exit 1
  fi
  echo "Creating .venv with $BASE ..."
  "$BASE" -m venv "$ROOT/.venv"
  "$PY" -m pip install -U pip
  "$PY" -m pip install -r "$ROOT/requirements.txt"
fi

if ! curl -s --max-time 3 "http://127.0.0.1:4723/status" >/dev/null 2>&1; then
  echo "WARNING: Appium not responding on :4723 — start it in another tab: appium"
fi

cd "$ROOT" || exit 1
set +e
"$PY" -m pytest -s -vv tests/test_signup_login_android.py --tb=short
STATUS=$?
set +e

echo ""
if [[ -f "$REPORT" ]]; then
  echo "Opening report in Google Chrome:"
  echo "  $REPORT"
  if [[ -d "/Applications/Google Chrome.app" ]]; then
    open -a "Google Chrome" "$REPORT" 2>/dev/null || open "$REPORT" 2>/dev/null || true
  else
    open "$REPORT" 2>/dev/null || true
  fi
else
  echo "WARNING: report not found: $REPORT"
fi

echo "Finished: $(date)  exit=$STATUS"
read -r -p "Press Enter to close…" _
exit "$STATUS"
