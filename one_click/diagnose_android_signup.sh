#!/usr/bin/env bash
# Dump Android signup test + page bits for debugging early FAIL (only ~4 steps).
# Run on Mac, then paste the output:
#   bash ~/AquaProjects/KskinCMS/one_click/diagnose_android_signup.sh
set -euo pipefail

APPIUM_PY="${APPIUM_PY:-$HOME/AquaProjects/MCP_Appium_Server/python}"
OUT="${1:-/tmp/kskin_android_signup_diagnose.txt}"

{
  echo "=== $(date) ==="
  echo "APPIUM_PY=$APPIUM_PY"
  echo ""
  echo "=== pages ==="
  ls -la "$APPIUM_PY/pages" | head -40
  echo ""
  echo "=== helpers/dynamic_data signup_email ==="
  "$APPIUM_PY/.venv/bin/python" - <<PY
import sys
sys.path.insert(0, "$APPIUM_PY")
from helpers.dynamic_data import next_android_run_values
v = next_android_run_values()
print("signup_email=", getattr(v, "signup_email", None))
print("email=", getattr(v, "email", None))
print("attrs sample=", [a for a in dir(v) if not a.startswith("_")][:40])
PY
  echo ""
  echo "=== test: email / EMPTY / step lines ==="
  rg -n "email|EMPTY|step|signup_email|enter_|type_|Next|valid" \
    "$APPIUM_PY/tests/test_signup_login_android.py" | head -80 || true
  echo ""
  echo "=== test file (first 220 lines) ==="
  sed -n '1,220p' "$APPIUM_PY/tests/test_signup_login_android.py"
  echo ""
  echo "=== signup_login_android_page.py (email-related) ==="
  rg -n "email|Email|NEXT|Next|send_keys|set_value|clear" \
    "$APPIUM_PY/pages/signup_login_android_page.py" | head -60 || true
  echo ""
  echo "=== signup_login_android_page.py full (cap 250 lines) ==="
  sed -n '1,250p' "$APPIUM_PY/pages/signup_login_android_page.py"
  echo ""
  echo "=== permissions_android_page.py ==="
  sed -n '1,120p' "$APPIUM_PY/pages/permissions_android_page.py" 2>/dev/null || echo "(missing)"
  echo ""
  echo "=== latest report step summary ==="
  REPORT="$APPIUM_PY/reports/KS-SIGNUP-AND-001_signup_login.html"
  if [[ -f "$REPORT" ]]; then
    ls -la "$REPORT"
    rg -n "TOTAL STEPS|PASSED|FAILED|EMPTY EMAIL|Overall|step" "$REPORT" | head -40 || true
  fi
} | tee "$OUT"

echo ""
echo "Wrote $OUT"
echo "Paste that file contents (or the terminal output) back to Cursor."
