#!/usr/bin/env bash
# Restore Claude-era Appium mobile signup originals on your Mac.
# Removes the long-timestamp stub email (qa.android.YYMMDDHHMMSS##@yopmail.com)
# that Cursor agents invented — that was NEVER your Claude original.
#
# Run:
#   bash ~/AquaProjects/KskinCMS/one_click/restore_claude_mobile_originals.sh
set -euo pipefail

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
CMS=""
for c in "$AQUA/KskinCMS" "$AQUA/KskinCMS_SeleniumPython" "$AQUA/kskincms_seleniumpython"; do
  [[ -d "$c/one_click" ]] && CMS="$c" && break
done
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
[[ -z "$CMS" ]] && CMS="$(cd "$SCRIPT_DIR/.." && pwd)"

APPIUM="${APPIUM_ROOT:-$AQUA/MCP_Appium_Server}"
APPIUM_PY="$APPIUM/python"
HELPERS="$APPIUM_PY/helpers"
DD="$HELPERS/dynamic_data.py"
SHA="${APPIUM_RESTORE_SHA:-8f544632f1b717687dd5be6df13df353ca0827b8}"

echo "=============================================================="
echo "  Restore Claude mobile originals (no long stub email)"
echo "  Appium : $APPIUM_PY"
echo "  SHA    : $SHA"
echo "=============================================================="

if [[ ! -d "$APPIUM_PY" ]]; then
  echo "ERROR: missing $APPIUM_PY"
  exit 1
fi

is_our_stub() {
  local f="$1"
  [[ -f "$f" ]] || return 1
  grep -qE 'Auto-generated|compat stub|restored stub|Replace with original|Replace with your original' "$f" 2>/dev/null
}

# --- 1) Quarantine our invented stub ---
if is_our_stub "$DD"; then
  bak="$DD.stub_long_email_bak_$(date +%Y%m%d_%H%M%S)"
  mv -f "$DD" "$bak"
  echo "Quarantined long-email stub → $bak"
fi

# --- 2) Restore helpers/pages/tests/conftest from Appium git ---
if [[ -d "$APPIUM/.git" ]]; then
  cd "$APPIUM"
  if git cat-file -e "${SHA}^{commit}" 2>/dev/null; then
    echo "Checking out originals from $SHA ..."
    git checkout "$SHA" -- \
      python/helpers \
      python/pages \
      python/conftest.py \
      python/tests 2>/dev/null || \
    git checkout "$SHA" -- python/helpers python/pages python/conftest.py
  else
    echo "WARNING: commit $SHA not found — trying any historical dynamic_data.py"
    ANY="$(git log --all --format=%H -- python/helpers/dynamic_data.py 2>/dev/null | head -1 || true)"
    if [[ -n "$ANY" ]]; then
      git checkout "$ANY" -- python/helpers/dynamic_data.py
      echo "Restored dynamic_data.py from $ANY"
    fi
    ANY_PAGES="$(git log --all --format=%H -- python/pages/signup_login_android_page.py 2>/dev/null | head -1 || true)"
    if [[ -n "$ANY_PAGES" ]]; then
      git checkout "$ANY_PAGES" -- python/pages
      echo "Restored pages/ from $ANY_PAGES"
    fi
  fi
else
  echo "WARNING: no .git under $APPIUM — cannot checkout. Use Time Machine / Local History."
fi

# --- 3) Zip fallback for dynamic_data only ---
restore_dd_from_zip() {
  local z="$1" tmp found
  [[ -f "$z" ]] || return 1
  tmp="$(mktemp -d)"
  unzip -q -o "$z" -d "$tmp" 2>/dev/null || { rm -rf "$tmp"; return 1; }
  found="$(find "$tmp" -type f -name 'dynamic_data.py' 2>/dev/null | head -1 || true)"
  if [[ -z "$found" ]]; then
    rm -rf "$tmp"
    return 1
  fi
  # Reject if zip itself contains our stub
  if grep -qE 'Auto-generated|compat stub|restored stub' "$found" 2>/dev/null; then
    echo "Zip $z has stub dynamic_data — skip"
    rm -rf "$tmp"
    return 1
  fi
  mkdir -p "$HELPERS"
  cp -f "$found" "$DD"
  rm -rf "$tmp"
  echo "Restored dynamic_data.py from zip: $z"
  return 0
}

if [[ ! -f "$DD" ]] || is_our_stub "$DD"; then
  [[ -f "$DD" ]] && is_our_stub "$DD" && mv -f "$DD" "$DD.stub_again_bak_$(date +%Y%m%d_%H%M%S)"
  OK=0
  for z in \
    "$AQUA/MCP_Appium_Server.zip" \
    "$HOME/Desktop/MCP_Appium_Server.zip" \
    "$HOME/Downloads/MCP_Appium_Server.zip" \
    "$HOME/Desktop/One click bash files/QA_AsanaFromReport_share.zip"
  do
    restore_dd_from_zip "$z" && OK=1 && break || true
  done
  if [[ "$OK" -eq 0 ]]; then
    echo ""
    echo "NOTE: Original dynamic_data.py not found in git/zip."
    echo "Writing SHORT uniq fallback (CMS-style 6 digits) — NOT the long YYMMDDHHMMSS stub."
    echo "If you have Claude Local History for helpers/dynamic_data.py, restore that instead."
    mkdir -p "$HELPERS"
    cat > "$DD" <<'PY'
"""Per-run signup values — short uniq fallback (CMS-style).

Prefer restoring the real Claude helpers/dynamic_data.py from Local History / git.
This fallback uses a 6-digit suffix only (no long datetime stamp).
"""
from __future__ import annotations

import random
import time
from types import SimpleNamespace


def _uniq() -> str:
    # Same idea as CMS therapists: last 6 digits of epoch — short, readable
    return str(int(time.time()))[-6:]


def _bag(platform: str) -> SimpleNamespace:
    u = _uniq()
    mobile = "9" + "".join(str(random.randint(0, 9)) for _ in range(7))
    email = f"qa.{platform}.{u}@yopmail.com"
    password = "P@ssw0rd"
    first = "QA"
    last = f"{platform.title()}{u[-4:]}"
    full = f"{first} {last}"
    otp = "111111"
    dob = "01/01/1995"
    gender = "Female"
    return SimpleNamespace(
        email=email,
        signup_email=email,
        login_email=email,
        user_email=email,
        password=password,
        signup_password=password,
        login_password=password,
        user_password=password,
        first_name=first,
        signup_first_name=first,
        last_name=last,
        signup_last_name=last,
        full_name=full,
        name=full,
        signup_name=full,
        mobile=mobile,
        phone=mobile,
        mobile_number=mobile,
        signup_mobile=mobile,
        signup_phone=mobile,
        otp=otp,
        email_otp=otp,
        mobile_otp=otp,
        sms_otp=otp,
        signup_otp=otp,
        gender=gender,
        signup_gender=gender,
        dob=dob,
        date_of_birth=dob,
        signup_dob=dob,
        signup_date_of_birth=dob,
        platform=platform,
        run_id=u,
        stamp=u,
    )


def next_android_run_values():
    return _bag("android")


def next_ios_run_values():
    return _bag("ios")


def get_android_run_values():
    return next_android_run_values()


def get_ios_run_values():
    return next_ios_run_values()
PY
  fi
fi

# --- 4) If original exists but missing signup_email alias, add aliases only ---
python3 "$CMS/one_click/ensure_signup_email_aliases.py" || true

# --- 5) Remove our junk patch files ---
rm -f "$HELPERS/android_type.py" "$HELPERS/patch_email_runtime.py" 2>/dev/null || true

# Strip conftest email patch
if [[ -f "$APPIUM_PY/conftest.py" ]] && grep -q "KSKIN_EMAIL_TYPE_PATCH\|patch_email_runtime" "$APPIUM_PY/conftest.py"; then
  python3 - <<PY
from pathlib import Path
import re
p = Path("$APPIUM_PY/conftest.py")
t = p.read_text(encoding="utf-8", errors="ignore")
t2 = re.sub(r"\n# KSKIN_EMAIL_TYPE_PATCH[\s\S]*$", "\n", t)
if t2 != t:
    p.write_text(t2, encoding="utf-8")
    print("conftest: stripped KSKIN_EMAIL_TYPE_PATCH")
PY
fi

# Strip mass-patch markers from android signup page (keep file body from git)
PAGE="$APPIUM_PY/pages/signup_login_android_page.py"
if [[ -f "$PAGE" ]]; then
  python3 - <<PY
from pathlib import Path
import re
p = Path("$PAGE")
t = p.read_text(encoding="utf-8", errors="ignore")
# Remove blocks we previously appended
for marker in ("ENTER_OTP_ONLY", "KSKIN_GAP_FILL", "KSKIN_SIGNUP_METHODS", "KSKIN_BOOL_CLEAR"):
    t = re.sub(rf"\n    # --- {marker}[\s\S]*?(?=\n    # --- |\Z)", "\n", t)
t = re.sub(r"\n{3,}", "\n\n", t)
p.write_text(t, encoding="utf-8")
print(f"cleaned patch markers on {p.name}")
PY
fi

# --- 6) enter_otp: copy from iOS page only (Claude), else Android-only minimal from iOS pattern ---
python3 "$CMS/one_click/add_enter_otp_only.py" || true

# --- 7) Verify ---
echo ""
echo "=== Verify email (must NOT be 14-digit YYMMDDHHMMSS##) ==="
PYBIN="$APPIUM_PY/.venv/bin/python"
[[ -x "$PYBIN" ]] || PYBIN="python3"
"$PYBIN" - <<PY
import sys, re
sys.path.insert(0, "$APPIUM_PY")
from helpers.dynamic_data import next_android_run_values
from pages.signup_login_android_page import SignupLoginAndroidPage
v = next_android_run_values()
email = getattr(v, "signup_email", None) or getattr(v, "email", None)
print("signup_email =", email)
print("enter_otp    =", hasattr(SignupLoginAndroidPage, "enter_otp"))
if email and re.search(r"qa\.android\.\d{12,}@", str(email)):
    print("FAIL: still long-timestamp stub email — restore Local History for dynamic_data.py")
    raise SystemExit(2)
print("OK: email looks short / non-stub")
PY

echo ""
echo "DONE. Re-run Desktop: run-android-signup-login.command"
echo "If email still wrong: Cursor Local History on"
echo "  $DD"
echo "and pick the Claude-era version."
