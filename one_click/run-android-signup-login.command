#!/bin/bash
# Android Sign-Up + Login — one-click (Claude-style, self-contained)
# Double-click from Finder. Uses Appium project .venv (Homebrew PEP668-safe).
cd "$(dirname "$0")" 2>/dev/null || true
set -uo pipefail

APPIUM_PY="${APPIUM_PY:-$HOME/AquaProjects/MCP_Appium_Server/python}"
PKG="${ANDROID_UAT_PACKAGE:-com.kskinfacial.customer.uat}"
REPORT="$APPIUM_PY/reports/KS-SIGNUP-AND-001_signup_login.html"
TEST="tests/test_signup_login_android.py"

echo "========================================"
echo "  Kskin Android — Sign-Up + Login"
echo "  $APPIUM_PY"
echo "  Started: $(date)"
echo "========================================"

[[ -d "$APPIUM_PY" ]] || { echo "ERROR: missing $APPIUM_PY"; read -r -p "Press Enter…" _; exit 1; }

# Python >=3.9 + project venv (do not pip into Homebrew)
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

[[ -f "$REPORT" ]] || REPORT="$(ls -t reports/*SIGNUP*AND*.html reports/*signup*android*.html 2>/dev/null | head -1 || true)"
if [[ -n "${REPORT:-}" && -f "$REPORT" ]]; then
  echo "Report → Chrome: $REPORT"
  open -a "Google Chrome" "$REPORT" 2>/dev/null || open "$REPORT" || true
else
  echo "No HTML report found"
fi
echo "Finished: $(date)  exit=$ST"
read -r -n 1 -s -p "Press any key to close..."
echo
exit "$ST"
