#!/usr/bin/env bash
# Shared: resolve Appium project .venv (never Homebrew pip / PEP668).
# Source from originals:  source "$CMS/one_click/mobile_venv.sh"
# Sets: AQUA APPIUM_PY VENV_DIR PYTHON_BIN BASE_PY

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM_PY="${APPIUM_PY:-$AQUA/MCP_Appium_Server/python}"

BASE_PY=""
for c in \
  /usr/local/bin/python3 \
  /usr/local/bin/python3.12 \
  /Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12 \
  /Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11 \
  /opt/homebrew/bin/python3.12 \
  /opt/homebrew/bin/python3
do
  [[ -x "$c" ]] || continue
  if "$c" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
    BASE_PY="$c"
    break
  fi
done
if [[ -z "$BASE_PY" ]]; then
  echo "ERROR: Need Python >= 3.9"
  read -r -p "Press Enter…" _; exit 1
fi

VENV_DIR="$APPIUM_PY/.venv"
PYTHON_BIN="$VENV_DIR/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Creating Appium venv at $VENV_DIR (base=$BASE_PY)..."
  "$BASE_PY" -m venv "$VENV_DIR" || {
    echo "ERROR: venv create failed with $BASE_PY"
    read -r -p "Press Enter…" _; exit 1
  }
fi
case "$PYTHON_BIN" in
  */.venv/bin/python*) ;;
  *)
    echo "ERROR: refusing non-venv python: $PYTHON_BIN"
    read -r -p "Press Enter…" _; exit 1
    ;;
esac
export PATH="$VENV_DIR/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"
export PYTHONPATH="$APPIUM_PY${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1
export JAVA_HOME="${JAVA_HOME:-$(/usr/libexec/java_home 2>/dev/null || true)}"

echo "Using Python: $PYTHON_BIN ($("$PYTHON_BIN" -V 2>&1))"
if ! "$PYTHON_BIN" -c 'import pytest, appium' 2>/dev/null; then
  echo "Installing pytest + Appium-Python-Client into venv..."
  "$PYTHON_BIN" -m pip install -U pip setuptools wheel
  "$PYTHON_BIN" -m pip install -U pytest Appium-Python-Client selenium || {
    echo "ERROR: pip install failed in venv ($PYTHON_BIN)"
    read -r -p "Press Enter…" _; exit 1
  }
fi

ensure_dynamic_data() {
  # Never invent long YYMMDDHHMMSS emails. Prefer Claude restore script / existing file.
  if [[ -f "$APPIUM_PY/helpers/dynamic_data.py" ]]; then
    if grep -qE 'Auto-generated|compat stub|strftime\("%y%m%d%H%M%S"\)' \
         "$APPIUM_PY/helpers/dynamic_data.py" 2>/dev/null; then
      echo "WARNING: long-email stub detected — run restore_claude_mobile_originals.sh"
    fi
    return 0
  fi
  local cms_restore=""
  for c in "${AQUA_ROOT:-$HOME/AquaProjects}/KskinCMS" \
           "${AQUA_ROOT:-$HOME/AquaProjects}/KskinCMS_SeleniumPython"; do
    if [[ -f "$c/one_click/restore_claude_mobile_originals.sh" ]]; then
      cms_restore="$c/one_click/restore_claude_mobile_originals.sh"
      break
    fi
  done
  if [[ -n "$cms_restore" ]]; then
    echo "WARNING: helpers/dynamic_data.py missing — restoring Claude originals..."
    bash "$cms_restore" || true
    return 0
  fi
  echo "WARNING: helpers/dynamic_data.py missing — writing SHORT uniq fallback (6 digits)..."
  mkdir -p "$APPIUM_PY/helpers"
  cat > "$APPIUM_PY/helpers/dynamic_data.py" <<'PY'
"""Short-uniq fallback — CMS-style 6 digits (not long datetime stub)."""
from __future__ import annotations
import random, time
from types import SimpleNamespace

def _uniq():
    return str(int(time.time()))[-6:]

def _bag(platform: str) -> SimpleNamespace:
    s = _uniq()
    mobile = "9" + "".join(str(random.randint(0,9)) for _ in range(7))
    email = f"qa.{platform}.{s}@yopmail.com"
    return SimpleNamespace(
        email=email, signup_email=email, login_email=email, user_email=email,
        password="P@ssw0rd", signup_password="P@ssw0rd", login_password="P@ssw0rd",
        first_name="QA", last_name=f"{platform.title()}{s[-4:]}",
        full_name=f"QA {platform.title()}{s[-4:]}", name=f"QA {platform.title()}{s[-4:]}",
        mobile=mobile, phone=mobile, mobile_number=mobile,
        signup_mobile=mobile, signup_phone=mobile,
        otp="111111", email_otp="111111", mobile_otp="111111", signup_otp="111111",
        gender="Female", dob="01/01/1995", date_of_birth="01/01/1995",
        platform=platform, run_id=s, stamp=s,
    )

def next_android_run_values():
    return _bag("android")

def next_ios_run_values():
    return _bag("ios")
PY
}

ensure_appium() {
  local log="${1:-$APPIUM_PY/reports/appium.log}"
  mkdir -p "$APPIUM_PY/reports"
  if curl -s "http://127.0.0.1:4723/status" >/dev/null 2>&1; then
    echo "  Appium already running on :4723"
    return 0
  fi
  if command -v appium >/dev/null 2>&1; then
    nohup appium --port 4723 >"$log" 2>&1 &
    echo "  Appium PID $!"
    for _ in 1 2 3 4 5 6 7 8 9 10; do
      curl -s "http://127.0.0.1:4723/status" >/dev/null 2>&1 && break
      sleep 1
    done
  else
    echo "  WARNING: appium CLI not found — assuming already managed elsewhere"
  fi
}

open_report() {
  local html="$1"
  if [[ -z "$html" || ! -f "$html" ]]; then
    echo "  No HTML report found under $APPIUM_PY/reports"
    return 1
  fi
  echo "  REPORT: $html"
  if [[ -d "/Applications/Google Chrome.app" ]]; then
    open -a "Google Chrome" "$html" || open "$html" || true
  else
    open "$html" || true
  fi
}
