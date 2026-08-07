#!/bin/bash
# Reconstructed original-style Android Sign-Up + Login one-click runner.
# Based on your prior working Terminal flow (Appium → device → pytest → HTML report).
set -uo pipefail

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM_PY="${APPIUM_PY:-$AQUA/MCP_Appium_Server/python}"
REPORT_HTML="$APPIUM_PY/reports/KS-SIGNUP-AND-001_signup_login.html"
PKG="${ANDROID_UAT_PACKAGE:-com.kskinfacial.customer.uat}"

# Appium Python client needs Python >= 3.9 (PEP585 tuple[...] hints).
pick_python() {
  local c
  for c in \
    /Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12 \
    /Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11 \
    /Library/Frameworks/Python.framework/Versions/3.10/bin/python3.10 \
    /usr/local/bin/python3.12 \
    /usr/local/bin/python3.11 \
    /opt/homebrew/bin/python3.12 \
    /opt/homebrew/bin/python3.11 \
    /usr/local/bin/python3 \
    /opt/homebrew/bin/python3
  do
    [[ -x "$c" ]] || continue
    if "$c" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
      echo "$c"
      return 0
    fi
  done
  return 1
}
export PATH="/usr/local/bin:/opt/homebrew/bin:/Library/Frameworks/Python.framework/Versions/3.12/bin:$PATH"
export PYTHONPATH="$APPIUM_PY${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1
export JAVA_HOME="${JAVA_HOME:-$(/usr/libexec/java_home 2>/dev/null || true)}"

PYTHON_BIN="$(pick_python || true)"
if [[ -z "${PYTHON_BIN:-}" ]]; then
  echo "ERROR: Need Python >= 3.9 for Appium client."
  echo "Found default: $(command -v python3 || true) ($(python3 -V 2>/dev/null || true))"
  read -r -p "Press Enter…" _; exit 1
fi
echo "Using Python: $PYTHON_BIN ($("$PYTHON_BIN" -V 2>&1))"
cd "$APPIUM_PY" || { echo "ERROR: missing $APPIUM_PY"; read -r -p "Press Enter…" _; exit 1; }

echo "========================================"
echo "  Kskin Android — Sign-Up + Login"
echo "  Dir: $APPIUM_PY"
echo "  Python: $PYTHON_BIN"
echo "  Started: $(date)"
echo "========================================"

# [1/5] Appium
echo "[1/5] Starting Appium in background (if needed)..."
if curl -s "http://127.0.0.1:4723/status" >/dev/null 2>&1; then
  echo "  Appium already running on :4723"
else
  if command -v appium >/dev/null 2>&1; then
    nohup appium --port 4723 >"$APPIUM_PY/reports/appium_android_signup.log" 2>&1 &
    echo "  Appium PID $!"
    for i in 1 2 3 4 5 6 7 8 9 10; do
      curl -s "http://127.0.0.1:4723/status" >/dev/null 2>&1 && break
      sleep 1
    done
  else
    echo "  WARNING: appium CLI not found — assuming already managed elsewhere"
  fi
fi

# [2/5] Device
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

# [3/5] Clean install baseline
echo "[3/5] Uninstalling $PKG for a clean-install baseline (ok if not installed)..."
adb uninstall "$PKG" >/dev/null 2>&1 || echo "  (already clean / not installed)"

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

# [4/5] Pytest
echo "[4/5] Running SIGN-UP + LOGIN via pytest..."
mkdir -p "$APPIUM_PY/reports"
set +e
"$PYTHON_BIN" -m pytest -s -vv \
  "tests/test_signup_login_android.py" \
  --tb=short
ST=$?
set -e

# [5/5] Report
echo "[5/5] Opening report (if present)..."
# Prefer canonical name; else newest matching
if [[ ! -f "$REPORT_HTML" ]]; then
  NEWEST="$(ls -t "$APPIUM_PY"/reports/*SIGNUP*AND*.html "$APPIUM_PY"/reports/*signup*android*.html 2>/dev/null | head -1 || true)"
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
