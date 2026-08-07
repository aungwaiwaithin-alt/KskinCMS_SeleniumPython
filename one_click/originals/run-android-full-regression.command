#!/bin/bash
# KSKIN_MOBILE_RUNNER_VENV — Android full regression (project .venv, never Homebrew pip).
set -uo pipefail

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM_PY="${APPIUM_PY:-$AQUA/MCP_Appium_Server/python}"
REPORT_HTML="$APPIUM_PY/reports/KS-REGR-AND-001_full_regression.html"
PKG="${ANDROID_UAT_PACKAGE:-com.kskinfacial.customer.uat}"

echo "KSKIN_MOBILE_RUNNER_VENV=android-full-regression"

# Load shared venv helpers (CMS first, then beside this script)
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
  echo "ERROR: mobile_venv.sh not found. Pull KskinCMS branch and reinstall:"
  echo "  cd ~/AquaProjects/KskinCMS && git stash -u && git pull"
  echo "  bash one_click/fix_pep668_now.sh"
  read -r -p "Press Enter…" _; exit 1
fi
# shellcheck disable=SC1090
source "$_COMMON"
cd "$APPIUM_PY" || { echo "ERROR: missing $APPIUM_PY"; read -r -p "Press Enter…" _; exit 1; }

echo "========================================"
echo "  Kskin Android — Full Regression"
echo "  Dir: $APPIUM_PY"
echo "  Python: $PYTHON_BIN"
echo "  Started: $(date)"
echo "========================================"

echo "[1/5] Starting Appium..."
ensure_appium "$APPIUM_PY/reports/appium_android_full.log"

echo "[2/5] Checking Android device/emulator..."
if ! command -v adb >/dev/null 2>&1; then
  echo "ERROR: adb not found"; read -r -p "Press Enter…" _; exit 1
fi
adb start-server >/dev/null 2>&1 || true
DEVICES="$(adb devices | awk 'NR>1 && $2=="device" {print $1}')"
if [[ -z "$DEVICES" ]]; then
  echo "ERROR: no Android device/emulator connected (adb devices empty)"
  read -r -p "Press Enter…" _; exit 1
fi
echo "  Connected: $DEVICES"

echo "[3/5] Uninstalling $PKG for a clean baseline (ok if missing)..."
adb uninstall "$PKG" >/dev/null 2>&1 || echo "  (already clean / not installed)"
ensure_dynamic_data

echo "[4/5] Discovering Android pytest targets..."
TARGETS=()
# Preferred entry points (first match wins as exclusive suite)
for pref in \
  "tests/test_full_regression_android.py" \
  "tests/test_android_full_regression.py" \
  "tests/test_regression_android.py" \
  "tests/android/test_full_regression.py" \
  "tests/android"
do
  if [[ -e "$pref" ]]; then
    TARGETS=("$pref")
    break
  fi
done
# Else: all android test modules under tests/
if [[ ${#TARGETS[@]} -eq 0 ]]; then
  while IFS= read -r f; do
    TARGETS+=("$f")
  done < <(find tests -type f -name '*.py' \( -iname '*android*' -o -path '*/android/*' \) ! -name '__init__.py' 2>/dev/null | sort)
fi
if [[ ${#TARGETS[@]} -eq 0 ]]; then
  echo "ERROR: No Android test files found under $APPIUM_PY/tests"
  echo "Expected something like tests/test_*android*.py"
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
  NEWEST="$(ls -t "$APPIUM_PY"/reports/*REGR*AND*.html \
    "$APPIUM_PY"/reports/*REGR*android*.html \
    "$APPIUM_PY"/reports/*full*android*.html \
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
