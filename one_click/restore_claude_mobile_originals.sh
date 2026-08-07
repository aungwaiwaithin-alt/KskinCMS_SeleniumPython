#!/usr/bin/env bash
# SAFE restore for mobile helpers ONLY.
# NEVER git-checkouts pages/ or tests/ — that previously wiped Claude page objects
# and left an incomplete SignupLoginAndroidPage (no tap_create_account).
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
echo "  SAFE helper restore (will NOT overwrite pages/ or tests/)"
echo "  Appium : $APPIUM_PY"
echo "=============================================================="

if [[ ! -d "$APPIUM_PY" ]]; then
  echo "ERROR: missing $APPIUM_PY"
  exit 1
fi

is_our_stub() {
  local f="$1"
  [[ -f "$f" ]] || return 1
  grep -qE 'Auto-generated|compat stub|restored stub|Replace with original|Replace with your original|strftime\("%y%m%d%H%M%S"\)|short uniq fallback' "$f" 2>/dev/null
}

# --- 1) Quarantine long-email / stub dynamic_data ---
if is_our_stub "$DD"; then
  bak="$DD.stub_long_email_bak_$(date +%Y%m%d_%H%M%S)"
  mv -f "$DD" "$bak"
  echo "Quarantined stub → $bak"
fi

# --- 2) Restore ONLY dynamic_data.py from git/zip if missing ---
# NEVER: git checkout python/pages or python/tests
if [[ ! -f "$DD" ]] && [[ -d "$APPIUM/.git" ]]; then
  cd "$APPIUM"
  if git cat-file -e "${SHA}:python/helpers/dynamic_data.py" 2>/dev/null; then
    git checkout "$SHA" -- python/helpers/dynamic_data.py
    echo "Restored dynamic_data.py from $SHA"
  else
    ANY="$(git log --all --format=%H -- python/helpers/dynamic_data.py 2>/dev/null | head -1 || true)"
    if [[ -n "$ANY" ]]; then
      git checkout "$ANY" -- python/helpers/dynamic_data.py
      echo "Restored dynamic_data.py from $ANY"
    fi
  fi
fi

if [[ ! -f "$DD" ]] || is_our_stub "$DD"; then
  [[ -f "$DD" ]] && is_our_stub "$DD" && mv -f "$DD" "$DD.stub_again_bak_$(date +%Y%m%d_%H%M%S)"
  for z in \
    "$AQUA/MCP_Appium_Server.zip" \
    "$HOME/Desktop/MCP_Appium_Server.zip" \
    "$HOME/Downloads/MCP_Appium_Server.zip"
  do
    [[ -f "$z" ]] || continue
    tmp="$(mktemp -d)"
    unzip -q -o "$z" -d "$tmp" 2>/dev/null || { rm -rf "$tmp"; continue; }
    found="$(find "$tmp" -type f -name 'dynamic_data.py' 2>/dev/null | head -1 || true)"
    if [[ -n "$found" ]] && ! is_our_stub "$found"; then
      mkdir -p "$HELPERS"
      cp -f "$found" "$DD"
      echo "Restored dynamic_data.py from zip: $z"
      rm -rf "$tmp"
      break
    fi
    rm -rf "$tmp"
  done
fi

if [[ ! -f "$DD" ]]; then
  echo "WARNING: dynamic_data.py still missing — restore from Cursor Local History:"
  echo "  $DD"
fi

# Remove junk helpers we invented (safe)
rm -f "$HELPERS/android_type.py" "$HELPERS/patch_email_runtime.py" 2>/dev/null || true

# Strip conftest email patch only (do not touch pages)
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

echo ""
echo "Pages/tests were NOT touched (on purpose)."
echo "Next — prove / recover Claude page object:"
echo "  bash $CMS/one_click/prove_originals.sh"
echo "  bash $CMS/one_click/recover_claude_from_backups.sh"
echo "  bash $CMS/one_click/recover_claude_from_backups.sh --apply   # if a good bak is found"
echo ""
echo "If no bak has tap_create_account, use Cursor Local History on:"
echo "  $APPIUM_PY/pages/signup_login_android_page.py"
