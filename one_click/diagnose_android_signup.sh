#!/usr/bin/env bash
# Dump Android signup test + page bits for debugging early FAIL.
# Uses grep (rg not required on Mac).
#   bash ~/AquaProjects/KskinCMS/one_click/diagnose_android_signup.sh
set -euo pipefail

APPIUM_PY="${APPIUM_PY:-$HOME/AquaProjects/MCP_Appium_Server/python}"
OUT="${1:-/tmp/kskin_android_signup_diagnose.txt}"
Grep() { grep -nE "$@" 2>/dev/null || true; }

{
  echo "=== $(date) ==="
  echo "APPIUM_PY=$APPIUM_PY"
  echo ""
  echo "=== pages ==="
  ls -la "$APPIUM_PY/pages" | head -40
  echo ""
  echo "=== helpers/dynamic_data signup_email ==="
  if [[ -x "$APPIUM_PY/.venv/bin/python" ]]; then
    "$APPIUM_PY/.venv/bin/python" - <<PY
import sys
sys.path.insert(0, "$APPIUM_PY")
from helpers.dynamic_data import next_android_run_values
v = next_android_run_values()
print("signup_email=", getattr(v, "signup_email", None))
print("has enter_otp on page?", end=" ")
try:
    from pages.signup_login_android_page import SignupLoginAndroidPage
    print(hasattr(SignupLoginAndroidPage, "enter_otp"))
except Exception as e:
    print("import fail", e)
PY
  fi
  echo ""
  echo "=== test methods called (page.*) ==="
  Grep "\\.(enter_|tap_|click_|type_|fill_|select_|allow_)" "$APPIUM_PY/tests/test_signup_login_android.py" | head -80
  echo ""
  echo "=== test: email / OTP / EMPTY lines ==="
  Grep "email|OTP|otp|EMPTY|enter_otp|Next|valid" "$APPIUM_PY/tests/test_signup_login_android.py" | head -80
  echo ""
  echo "=== page defs ==="
  Grep "^[[:space:]]*def " "$APPIUM_PY/pages/signup_login_android_page.py" | head -80
  echo ""
  echo "=== has enter_otp? ==="
  Grep "def enter_otp" "$APPIUM_PY/pages/signup_login_android_page.py"
  echo ""
  echo "=== signup_login_android_page.py (first 200 lines) ==="
  sed -n '1,200p' "$APPIUM_PY/pages/signup_login_android_page.py"
  echo ""
  echo "=== latest report errors ==="
  REPORT="$APPIUM_PY/reports/KS-SIGNUP-AND-001_signup_login.html"
  if [[ -f "$REPORT" ]]; then
    ls -la "$REPORT"
    Grep "TOTAL STEPS|Overall|enter_otp|ERROR:|FAILED|EMPTY EMAIL" "$REPORT" | head -40
  fi
} | tee "$OUT"

echo ""
echo "Wrote $OUT"
echo "If enter_otp missing, run:"
echo "  python3 ~/AquaProjects/KskinCMS/one_click/patch_android_signup_methods.py"
