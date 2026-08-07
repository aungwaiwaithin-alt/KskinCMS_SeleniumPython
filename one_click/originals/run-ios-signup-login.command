#!/bin/bash
# Reconstructed original-style iOS Sign-Up + Login one-click runner.
set -uo pipefail

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM_PY="${APPIUM_PY:-$AQUA/MCP_Appium_Server/python}"
REPORT_HTML="$APPIUM_PY/reports/KS-SIGNUP-iOS-001_signup_login.html"
BUNDLE="${IOS_UAT_BUNDLE:-enterprise.codigo.kskincustomer.uat}"

# Prefer a Python >=3.9 that already has pytest + appium (Homebrew 3.12 may be bare).
pick_python() {
  local c
  for c in \
    /usr/local/bin/python3 \
    /usr/local/bin/python3.12 \
    /usr/local/bin/python3.11 \
    /Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12 \
    /Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11 \
    /Library/Frameworks/Python.framework/Versions/3.10/bin/python3.10 \
    /opt/homebrew/bin/python3.12 \
    /opt/homebrew/bin/python3.11 \
    /opt/homebrew/bin/python3
  do
    [[ -x "$c" ]] || continue
    if "$c" - <<'PY' 2>/dev/null
import sys
assert sys.version_info >= (3, 9)
import pytest
import appium
print(sys.executable)
PY
    then
      return 0
    fi
  done
  return 1
}
export PATH="/usr/local/bin:/opt/homebrew/bin:/Library/Frameworks/Python.framework/Versions/3.12/bin:$PATH"
export PYTHONPATH="$APPIUM_PY${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1
export JAVA_HOME="${JAVA_HOME:-$(/usr/libexec/java_home 2>/dev/null || true)}"

PYTHON_BIN="$(pick_python | tail -1 || true)"
if [[ -z "${PYTHON_BIN:-}" ]]; then
  for c in /usr/local/bin/python3 /opt/homebrew/bin/python3.12 /opt/homebrew/bin/python3 \
           /Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12; do
    [[ -x "$c" ]] || continue
    if "$c" -c 'import sys; raise SystemExit(0 if sys.version_info>=(3,9) else 1)'; then
      PYTHON_BIN="$c"
      break
    fi
  done
fi
if [[ -z "${PYTHON_BIN:-}" ]]; then
  echo "ERROR: Need Python >= 3.9 with Appium/pytest."
  read -r -p "Press Enter…" _; exit 1
fi
echo "Using Python: $PYTHON_BIN ($("$PYTHON_BIN" -V 2>&1))"
if ! "$PYTHON_BIN" -c 'import pytest, appium' 2>/dev/null; then
  echo "Installing pytest + Appium-Python-Client into this Python..."
  "$PYTHON_BIN" -m pip install -U pip pytest Appium-Python-Client selenium || {
    echo "ERROR: pip install failed for $PYTHON_BIN"
    read -r -p "Press Enter…" _; exit 1
  }
fi
cd "$APPIUM_PY" || { echo "ERROR: missing $APPIUM_PY"; read -r -p "Press Enter…" _; exit 1; }

echo "========================================"
echo "  Kskin iOS — Sign-Up + Login"
echo "  Dir: $APPIUM_PY"
echo "  Python: $PYTHON_BIN"
echo "  Bundle: $BUNDLE"
echo "  Started: $(date)"
echo "========================================"

echo "[1/5] Starting Appium in background (if needed)..."
if curl -s "http://127.0.0.1:4723/status" >/dev/null 2>&1; then
  echo "  Appium already running on :4723"
else
  if command -v appium >/dev/null 2>&1; then
    nohup appium --port 4723 >"$APPIUM_PY/reports/appium_ios_signup.log" 2>&1 &
    echo "  Appium PID $!"
    for i in 1 2 3 4 5 6 7 8 9 10; do
      curl -s "http://127.0.0.1:4723/status" >/dev/null 2>&1 && break
      sleep 1
    done
  else
    echo "  WARNING: appium CLI not found — assuming already managed elsewhere"
  fi
fi

echo "[2/5] Checking iOS simulator/device availability..."
if command -v xcrun >/dev/null 2>&1; then
  xcrun simctl list devices booted 2>/dev/null | head -20 || true
else
  echo "  WARNING: xcrun not found"
fi

echo "[3/5] Prep note: ensure Kskin-uat is installed on the booted simulator/device"
echo "  (bundle id: $BUNDLE)"

if [[ ! -f "$APPIUM_PY/helpers/dynamic_data.py" ]]; then
  echo "WARNING: helpers/dynamic_data.py missing — writing stub now..."
  mkdir -p "$APPIUM_PY/helpers"
  cat > "$APPIUM_PY/helpers/dynamic_data.py" <<'PY'
from __future__ import annotations
import random, time
from types import SimpleNamespace

def _stamp():
    return time.strftime("%y%m%d%H%M%S") + f"{random.randint(10,99)}"

def _bag(platform: str) -> SimpleNamespace:
    s = _stamp()
    mobile = "9" + "".join(str(random.randint(0,9)) for _ in range(7))
    return SimpleNamespace(
        email=f"qa.{platform}.{s}@yopmail.com",
        password="P@ssw0rd",
        first_name="QA",
        last_name=f"{platform.title()}{s[-4:]}",
        full_name=f"QA {platform.title()}{s[-4:]}",
        name=f"QA {platform.title()}{s[-4:]}",
        mobile=mobile, phone=mobile, mobile_number=mobile,
        otp="111111", gender="Female",
        dob="01/01/1995", date_of_birth="01/01/1995",
        platform=platform, run_id=s,
    )

def next_android_run_values():
    return _bag("android")

def next_ios_run_values():
    return _bag("ios")
PY
fi

echo "[4/5] Running SIGN-UP + LOGIN via pytest..."
mkdir -p "$APPIUM_PY/reports"
set +e
"$PYTHON_BIN" -m pytest -s -vv \
  "tests/test_signup_login_ios.py" \
  --tb=short
ST=$?
set -e

echo "[5/5] Opening report (if present)..."
if [[ ! -f "$REPORT_HTML" ]]; then
  NEWEST="$(ls -t "$APPIUM_PY"/reports/*SIGNUP*iOS*.html "$APPIUM_PY"/reports/*signup*ios*.html 2>/dev/null | head -1 || true)"
  [[ -n "$NEWEST" ]] && REPORT_HTML="$NEWEST"
fi
if [[ -f "$REPORT_HTML" ]]; then
  echo "  REPORT: $REPORT_HTML"
  if [[ -d "/Applications/Google Chrome.app" ]]; then
    open -a "Google Chrome" "$REPORT_HTML" || open "$REPORT_HTML" || true
  else
    open "$REPORT_HTML" || true
  fi
else
  echo "  No HTML report found under $APPIUM_PY/reports"
fi

if [[ "$ST" -eq 0 ]]; then
  echo "RESULT: PASS (exit code 0)"
else
  echo "RESULT: FAIL (exit code $ST)"
fi
echo "Finished: $(date)"
read -r -n 1 -s -p "Press any key to close this window..."
echo
exit "$ST"
