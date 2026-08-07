#!/bin/bash
# KSKIN_MOBILE_RUNNER_VENV — iOS E2E full flow (project .venv, never Homebrew pip).
set -uo pipefail

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM_PY="${APPIUM_PY:-$AQUA/MCP_Appium_Server/python}"
REPORT_HTML="$APPIUM_PY/reports/KS-E2E-iOS-001_full_flow.html"
BUNDLE="${IOS_UAT_BUNDLE:-enterprise.codigo.kskincustomer.uat}"

echo "KSKIN_MOBILE_RUNNER_VENV=ios-e2e"

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
echo "  Kskin iOS — E2E Full Flow"
echo "  Dir: $APPIUM_PY"
echo "  Python: $PYTHON_BIN"
echo "  Bundle: $BUNDLE"
echo "  Started: $(date)"
echo "========================================"

echo "[1/5] Starting Appium..."
ensure_appium "$APPIUM_PY/reports/appium_ios_e2e.log"

echo "[2/5] Checking iOS simulator/device..."
if command -v xcrun >/dev/null 2>&1; then
  xcrun simctl list devices booted 2>/dev/null | head -20 || true
else
  echo "  WARNING: xcrun not found"
fi

echo "[3/5] Prep: ensure UAT app installed ($BUNDLE)"
ensure_dynamic_data

echo "[4/5] Discovering iOS E2E pytest targets..."
TARGETS=()
for pref in \
  "tests/test_e2e_full_flow_ios.py" \
  "tests/test_e2e_ios.py" \
  "tests/test_full_flow_ios.py" \
  "tests/e2e/test_ios.py" \
  "tests/e2e"
do
  if [[ -e "$pref" ]]; then
    TARGETS=("$pref")
    break
  fi
done
if [[ ${#TARGETS[@]} -eq 0 ]]; then
  while IFS= read -r f; do
    TARGETS+=("$f")
  done < <(find tests -type f -name '*.py' \( -iname '*e2e*ios*' -o -iname '*ios*e2e*' -o -iname '*full_flow*ios*' \) ! -name '__init__.py' 2>/dev/null | sort)
fi
if [[ ${#TARGETS[@]} -eq 0 ]]; then
  echo "ERROR: No iOS E2E test files found under $APPIUM_PY/tests"
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
  NEWEST="$(ls -t "$APPIUM_PY"/reports/*E2E*iOS*.html \
    "$APPIUM_PY"/reports/*e2e*ios*.html \
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
