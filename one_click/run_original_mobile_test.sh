#!/usr/bin/env bash
# Run an ORIGINAL Appium test exactly as it is. READ-ONLY on your Appium tree:
# no stubs written, no page patching, no dynamic_data generation, no report copying.
#
# Usage:
#   bash ~/AquaProjects/KskinCMS/one_click/run_original_mobile_test.sh                 # list tests
#   bash ~/AquaProjects/KskinCMS/one_click/run_original_mobile_test.sh android-signup
#   bash ~/AquaProjects/KskinCMS/one_click/run_original_mobile_test.sh tests/test_signup_login_android.py
set -uo pipefail

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM="${APPIUM_ROOT:-$AQUA/MCP_Appium_Server}"
APPIUM_PY="${APPIUM_PY:-$APPIUM/python}"
WANT="${1:-}"

if [[ ! -d "$APPIUM_PY/tests" ]]; then
  echo "ERROR: no tests dir at $APPIUM_PY/tests"
  exit 1
fi

# ---------- pick test ----------
declare -a SHORTCUTS=(
  "android-signup:test_signup_login_android.py"
  "ios-signup:test_signup_login_ios.py"
  "android-regression:test_full_regression_android.py"
  "ios-regression:test_full_regression_ios.py"
  "android-e2e:test_e2e_full_flow_android.py"
  "ios-e2e:test_e2e_full_flow_ios.py"
)

resolve_test() {
  local want="$1" sc key val
  [[ -z "$want" ]] && return 1
  # direct path
  if [[ -f "$APPIUM_PY/$want" ]]; then
    echo "$want"
    return 0
  fi
  if [[ -f "$APPIUM_PY/tests/$want" ]]; then
    echo "tests/$want"
    return 0
  fi
  for sc in "${SHORTCUTS[@]}"; do
    key="${sc%%:*}"
    val="${sc#*:}"
    if [[ "$want" == "$key" ]] && [[ -f "$APPIUM_PY/tests/$val" ]]; then
      echo "tests/$val"
      return 0
    fi
  done
  # fuzzy: single match on name
  local hits
  hits="$(cd "$APPIUM_PY" && ls tests/test_*.py 2>/dev/null | grep -i -- "$want" || true)"
  if [[ "$(echo "$hits" | grep -c . || true)" == "1" ]]; then
    echo "$hits"
    return 0
  fi
  return 1
}

if [[ -z "$WANT" ]]; then
  echo "=============================================================="
  echo "  Original Appium tests in $APPIUM_PY/tests"
  echo "=============================================================="
  (cd "$APPIUM_PY" && ls -1 tests/test_*.py)
  echo ""
  echo "Shortcuts: android-signup, ios-signup, android-regression,"
  echo "           ios-regression, android-e2e, ios-e2e"
  echo ""
  echo "Run e.g.: bash $0 android-signup"
  exit 0
fi

TEST_REL="$(resolve_test "$WANT" || true)"
if [[ -z "$TEST_REL" ]]; then
  echo "ERROR: cannot resolve test '$WANT'"
  (cd "$APPIUM_PY" && ls -1 tests/test_*.py)
  exit 1
fi

# ---------- pick python (>=3.9 for Appium client) ----------
CANDIDATES=(
  "$APPIUM_PY/.venv/bin/python"
  /opt/homebrew/bin/python3.12
  /opt/homebrew/bin/python3.11
  /opt/homebrew/bin/python3
  /usr/local/bin/python3
  /usr/bin/python3
)

PYBIN=""
PARTIAL=""
for c in "${CANDIDATES[@]}"; do
  [[ -x "$c" ]] || continue
  "$c" -c 'import sys; raise SystemExit(0 if sys.version_info>=(3,9) else 1)' 2>/dev/null || continue
  if "$c" -c 'import pytest, appium' 2>/dev/null; then
    PYBIN="$c"
    break
  fi
  if [[ -z "$PARTIAL" ]] && "$c" -c 'import pytest' 2>/dev/null; then
    PARTIAL="$c"
  fi
done

if [[ -z "$PYBIN" && -n "$PARTIAL" ]]; then
  PYBIN="$PARTIAL"
  echo "WARNING: $PYBIN has pytest but not Appium-Python-Client — collection may fail."
  echo "  Install into the Appium venv:"
  echo "    cd $APPIUM_PY && python3 -m venv .venv"
  echo "    .venv/bin/python -m pip install -U pip pytest pytest-html Appium-Python-Client selenium"
  echo ""
fi

if [[ -z "$PYBIN" ]]; then
  echo "ERROR: no Python >=3.9 with pytest available."
  echo ""
  echo "Create the Appium venv once (does not touch your test code):"
  echo "  cd $APPIUM_PY"
  echo "  python3 -m venv .venv"
  echo "  .venv/bin/python -m pip install -U pip pytest pytest-html Appium-Python-Client selenium"
  echo "Then re-run this script."
  exit 1
fi

echo "=============================================================="
echo "  Original Appium test run (no patching, no stubs)"
echo "  Dir    : $APPIUM_PY"
echo "  Test   : $TEST_REL"
echo "  Python : $PYBIN ($("$PYBIN" -V 2>&1))"
echo "  Started: $(date)"
echo "=============================================================="

# ---------- preflight (report only, change nothing) ----------
echo ""
echo "--- Preflight (informational) ---"
if [[ -f "$APPIUM_PY/helpers/dynamic_data.py" ]]; then
  if grep -qE 'Auto-generated|compat stub|strftime\("%y%m%d%H%M%S"\)' \
       "$APPIUM_PY/helpers/dynamic_data.py" 2>/dev/null; then
    echo "helpers/dynamic_data.py : STUB (long email) — restore your original:"
    echo "  bash $AQUA/KskinCMS/one_click/restore_claude_mobile_originals.sh"
  else
    echo "helpers/dynamic_data.py : present (non-stub)"
  fi
else
  echo "helpers/dynamic_data.py : MISSING (test import may fail)"
fi

if curl -s --max-time 3 "http://127.0.0.1:4723/status" >/dev/null 2>&1; then
  echo "Appium server           : running on :4723"
else
  echo "Appium server           : NOT running"
  echo "  Start it in another Terminal tab:  appium"
fi

if command -v adb >/dev/null 2>&1; then
  echo "Android devices:"
  adb devices | sed -n '2,$p' | sed '/^$/d' | sed 's/^/  /' || true
fi

# ---------- run ----------
echo ""
echo "--- pytest (original test, unmodified) ---"
cd "$APPIUM_PY" || exit 1
echo "\$ $PYBIN -m pytest -s -vv $TEST_REL"
echo ""
"$PYBIN" -m pytest -s -vv "$TEST_REL"
STATUS=$?

echo ""
echo "=============================================================="
echo "  Finished: $(date)   exit=$STATUS"
if [[ "$STATUS" -eq 0 ]]; then
  echo "  PASS — originals work. Now we can generate fresh .command files."
else
  echo "  FAIL — fix the original test/page in Appium first."
  echo "  Do NOT run any patch_*/add_* scripts."
fi
echo "  Reports (newest 5):"
ls -1t "$APPIUM_PY/reports"/*.html 2>/dev/null | head -5 | sed 's/^/    /' || echo "    (none)"
echo "=============================================================="
exit "$STATUS"
