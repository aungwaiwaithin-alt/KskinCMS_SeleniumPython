#!/bin/bash
# KSKIN_MOBILE_RUNNER_VENV — iOS full regression (project .venv, never Homebrew pip).
set -uo pipefail

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM_PY="${APPIUM_PY:-$AQUA/MCP_Appium_Server/python}"
REPORT_HTML="$APPIUM_PY/reports/KS-REGR-iOS-001_full_regression.html"
BUNDLE="${IOS_UAT_BUNDLE:-enterprise.codigo.kskincustomer.uat}"

echo "KSKIN_MOBILE_RUNNER_VENV=ios-full-regression"

_COMMON=""
for c in \
  "$AQUA/KskinCMS/one_click/mobile_venv.sh" \
  "$AQUA/KskinCMS_SeleniumPython/one_click/mobile_venv.sh" \
  "$(cd "$(dirname "$0")/../.." 2>/dev/null && pwd)/one_click/mobile_venv.sh" \
  "$(cd "$(dirname "$0")/.." 2>/dev/null && pwd)/mobile_venv.sh"
do
  [[ -f "$c" ]] && _COMMON="$c" && break
done
if [[ -z "$_COMMON" ]]; then
  echo "ERROR: mobile_venv.sh not found. Pull + reinstall:"
  echo "  cd ~/AquaProjects/KskinCMS && git stash -u && git pull && bash one_click/fix_pep668_now.sh"
  read -r -p "Press Enter…" _; exit 1
fi
# shellcheck disable=SC1090
source "$_COMMON"
cd "$APPIUM_PY" || { echo "ERROR: missing $APPIUM_PY"; read -r -p "Press Enter…" _; exit 1; }

echo "========================================"
echo "  Kskin iOS — Full Regression"
echo "  Dir: $APPIUM_PY"
echo "  Python: $PYTHON_BIN"
echo "  Bundle: $BUNDLE"
echo "  Started: $(date)"
echo "========================================"

echo "[1/5] Starting Appium..."
ensure_appium "$APPIUM_PY/reports/appium_ios_full.log"

echo "[2/5] Checking iOS simulator/device..."
if command -v xcrun >/dev/null 2>&1; then
  xcrun simctl list devices booted 2>/dev/null | head -20 || true
else
  echo "  WARNING: xcrun not found"
fi

echo "[3/5] Prep: ensure UAT app installed ($BUNDLE)"
ensure_dynamic_data

echo "[4/5] Discovering iOS pytest targets..."
TARGETS=()
for pref in \
  "tests/test_full_regression_ios.py" \
  "tests/test_ios_full_regression.py" \
  "tests/test_regression_ios.py" \
  "tests/ios/test_full_regression.py" \
  "tests/ios"
do
  if [[ -e "$pref" ]]; then
    TARGETS=("$pref")
    break
  fi
done
if [[ ${#TARGETS[@]} -eq 0 ]]; then
  while IFS= read -r f; do
    TARGETS+=("$f")
  done < <(find tests -type f -name '*.py' \( -iname '*ios*' -o -path '*/ios/*' \) ! -name '__init__.py' 2>/dev/null | sort)
fi
if [[ ${#TARGETS[@]} -eq 0 ]]; then
  echo "ERROR: No iOS test files found under $APPIUM_PY/tests"
  ls -la tests 2>/dev/null || true
  read -r -p "Press Enter…" _; exit 1
fi
echo "  Targets:"
for t in "${TARGETS[@]}"; do echo "    - $t"; done

mkdir -p "$APPIUM_PY/reports"
set +e
"$PYTHON_BIN" -m pytest -s -vv "${TARGETS[@]}" --tb=short
ST=$?
set -e

echo "[5/5] Opening report (if present)..."
if [[ ! -f "$REPORT_HTML" ]]; then
  NEWEST="$(ls -t "$APPIUM_PY"/reports/*REGR*iOS*.html \
    "$APPIUM_PY"/reports/*REGR*ios*.html \
    "$APPIUM_PY"/reports/*full*ios*.html \
    "$APPIUM_PY"/reports/*.html 2>/dev/null | head -1 || true)"
  [[ -n "$NEWEST" ]] && REPORT_HTML="$NEWEST"
fi
open_report "$REPORT_HTML" || true

if [[ "$ST" -eq 0 ]]; then
  echo "RESULT: PASS (exit code 0)"
else
  echo "RESULT: FAIL (exit code $ST)"
fi
echo "Finished: $(date)"
read -r -n 1 -s -p "Press any key to close this window..."
echo
exit "$ST"
