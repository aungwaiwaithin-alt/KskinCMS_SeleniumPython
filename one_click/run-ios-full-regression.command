#!/bin/bash
# iOS Full Regression — one-click (Claude-style, self-contained)
cd "$(dirname "$0")" 2>/dev/null || true
set -uo pipefail

APPIUM_PY="${APPIUM_PY:-$HOME/AquaProjects/MCP_Appium_Server/python}"
BUNDLE="${IOS_UAT_BUNDLE:-enterprise.codigo.kskincustomer.uat}"
REPORT="$APPIUM_PY/reports/KS-REGR-iOS-001_full_regression.html"

echo "========================================"
echo "  Kskin iOS — Full Regression"
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
    nohup appium --port 4723 >reports/appium_ios_full.log 2>&1 &
    for _ in $(seq 1 15); do curl -s http://127.0.0.1:4723/status >/dev/null 2>&1 && break; sleep 1; done
  else
    echo "  WARNING: appium not in PATH"
  fi
fi

echo "[2/4] Simulator/device..."
command -v xcrun >/dev/null && xcrun simctl list devices booted 2>/dev/null | head -10 || true

echo "[3/4] Ensure UAT app installed ($BUNDLE)"

TEST=""
for cand in \
  tests/test_full_regression_ios.py \
  tests/test_ios_full_regression.py \
  tests/test_regression_ios.py \
  tests/ios/test_full_regression.py
do
  [[ -f "$cand" ]] && TEST="$cand" && break
done

echo "[4/4] pytest..."
set +e
if [[ -n "$TEST" ]]; then
  echo "  $TEST"
  "$PY" -m pytest -s -vv "$TEST" --tb=short
  ST=$?
else
  mapfile -t FILES < <(find tests -type f -name '*.py' \( -iname '*ios*' -o -path '*/ios/*' \) ! -name '__init__.py' 2>/dev/null | sort)
  if [[ ${#FILES[@]} -eq 0 ]]; then
    echo "ERROR: no iOS tests under tests/"
    ls -la tests 2>/dev/null || true
    read -r -p "Press Enter…" _; exit 1
  fi
  printf '  %s\n' "${FILES[@]}"
  "$PY" -m pytest -s -vv "${FILES[@]}" --tb=short
  ST=$?
fi
set -e

[[ -f "$REPORT" ]] || REPORT="$(ls -t reports/*REGR*iOS*.html reports/*REGR*ios*.html reports/*.html 2>/dev/null | head -1 || true)"
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
