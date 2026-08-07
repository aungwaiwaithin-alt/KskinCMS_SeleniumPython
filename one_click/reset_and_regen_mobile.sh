#!/usr/bin/env bash
# RESET + REGEN mobile one-clicks from YOUR local Appium python tests.
# Does NOT invent page-object methods. Restores pages/ from Appium git when possible.
#
# YOU should first delete Desktop mobile .command files if you want a clean Finder folder.
# Then run:
#   bash ~/AquaProjects/KskinCMS/one_click/reset_and_regen_mobile.sh
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
DEST=""
for d in \
  "$HOME/Desktop/One click bash files" \
  "$HOME/One click bash files" \
  "$HOME/Documents/One click bash files"
do
  [[ -d "$d" ]] && DEST="$d" && break
done
DEST="${DEST:-$HOME/Desktop/One click bash files}"
mkdir -p "$DEST"

echo "CMS     : $CMS"
echo "Appium  : $APPIUM_PY"
echo "Desktop : $DEST"

if [[ ! -d "$APPIUM_PY/tests" ]]; then
  echo "ERROR: missing $APPIUM_PY/tests — cannot generate from originals."
  exit 1
fi

echo ""
echo "=== 1) Inventory original tests ==="
ls -la "$APPIUM_PY/tests"/test_*.py

echo ""
echo "=== 2) DO NOT checkout pages/ from git ==="
echo "Previous git checkout wiped Claude page objects (no tap_create_account)."
echo "Pages are left as-is. Recover from backups / Local History instead:"
echo "  bash $CMS/one_click/prove_originals.sh"
echo "  bash $CMS/one_click/recover_claude_from_backups.sh"
# Keep only junk-helper cleanup below — no git checkout of pages.

# Remove ONLY our known junk helpers (safe)
rm -f "$APPIUM_PY/helpers/android_type.py" \
      "$APPIUM_PY/helpers/patch_email_runtime.py" 2>/dev/null || true

# Quarantine long-email stub if still present after checkout
if [[ -f "$APPIUM_PY/helpers/dynamic_data.py" ]] && \
   grep -qE 'Auto-generated|compat stub|strftime\("%y%m%d%H%M%S"\)' \
     "$APPIUM_PY/helpers/dynamic_data.py" 2>/dev/null; then
  echo "Long-email stub still present — running restore_claude_mobile_originals.sh ..."
  bash "$CMS/one_click/restore_claude_mobile_originals.sh" || true
fi
# Do NOT delete permissions_android_page.py after git checkout — the suite imports it.
# Only remove if it is clearly our stub AND git has a real copy to restore.
if [[ -f "$APPIUM_PY/pages/permissions_android_page.py" ]] && \
   grep -q "Auto-generated compat page object" "$APPIUM_PY/pages/permissions_android_page.py" 2>/dev/null; then
  echo "Found auto-generated permissions stub — trying git restore..."
  if [[ -d "$APPIUM/.git" ]]; then
    cd "$APPIUM"
    if git cat-file -e 8f544632f1b717687dd5be6df13df353ca0827b8:python/pages/permissions_android_page.py 2>/dev/null; then
      git checkout 8f544632f1b717687dd5be6df13df353ca0827b8 -- python/pages/permissions_android_page.py
      echo "Restored permissions_android_page.py from 8f544632"
    else
      echo "WARNING: permissions_android_page.py not in 8f544632 — leaving stub (suite needs this import)."
    fi
  fi
fi
# If completely missing, restore from git
if [[ ! -f "$APPIUM_PY/pages/permissions_android_page.py" ]] && [[ -d "$APPIUM/.git" ]]; then
  cd "$APPIUM"
  echo "permissions_android_page.py missing — searching git..."
  if git cat-file -e 8f544632f1b717687dd5be6df13df353ca0827b8:python/pages/permissions_android_page.py 2>/dev/null; then
    git checkout 8f544632f1b717687dd5be6df13df353ca0827b8 -- python/pages/permissions_android_page.py
    echo "Restored from 8f544632"
  else
    SHA="$(git log --all --format=%H -- python/pages/permissions_android_page.py | head -1 || true)"
    if [[ -n "$SHA" ]]; then
      git checkout "$SHA" -- python/pages/permissions_android_page.py
      echo "Restored permissions_android_page.py from $SHA"
    else
      echo "ERROR: permissions_android_page.py not found in git history."
    fi
  fi
fi

# Strip KSKIN_EMAIL_TYPE_PATCH from conftest if still present
if [[ -f "$APPIUM_PY/conftest.py" ]] && grep -q "KSKIN_EMAIL_TYPE_PATCH\|patch_email_runtime" "$APPIUM_PY/conftest.py"; then
  echo "Stripping email patch block from conftest.py..."
  python3 - <<PY
from pathlib import Path
p = Path("$APPIUM_PY/conftest.py")
t = p.read_text(encoding="utf-8", errors="ignore")
import re
t2 = re.sub(r"\n# KSKIN_EMAIL_TYPE_PATCH[\s\S]*$", "\n", t)
if t2 != t:
    p.write_text(t2, encoding="utf-8")
    print("conftest cleaned")
else:
    print("conftest unchanged")
PY
fi

echo ""
echo "=== 3) Ensure Appium project .venv (PEP668-safe) ==="
BASE_PY=""
for c in /usr/local/bin/python3 /opt/homebrew/bin/python3.12 /opt/homebrew/bin/python3; do
  [[ -x "$c" ]] || continue
  "$c" -c 'import sys; raise SystemExit(0 if sys.version_info>=(3,9) else 1)' 2>/dev/null && BASE_PY="$c" && break
done
[[ -n "$BASE_PY" ]] || { echo "ERROR: need Python >= 3.9"; exit 1; }
if [[ ! -x "$APPIUM_PY/.venv/bin/python" ]]; then
  "$BASE_PY" -m venv "$APPIUM_PY/.venv"
fi
"$APPIUM_PY/.venv/bin/python" -m pip install -U pip pytest Appium-Python-Client selenium >/dev/null
echo "venv: $("$APPIUM_PY/.venv/bin/python" -V)"

echo ""
echo "=== 4) Generate clean Desktop .command files from tests/ ==="
python3 "$CMS/one_click/generate_mobile_commands.py" --dest "$DEST" --appium-py "$APPIUM_PY"

echo ""
echo "=== 5) Also copy into CMS one_click/ for the pack ==="
python3 "$CMS/one_click/generate_mobile_commands.py" --dest "$CMS/one_click" --appium-py "$APPIUM_PY" --cms-pack

echo ""
echo "DONE."
echo "Desktop commands:"
ls -la "$DEST"/run-*-signup*.command "$DEST"/run-*-full*.command "$DEST"/run-e2e*.command 2>/dev/null || ls -la "$DEST"/run-*.command | head -20
echo ""
echo "If signup still uses a long qa.android.YYMMDD... email, run:"
echo "  bash $CMS/one_click/restore_claude_mobile_originals.sh"
echo "Do not re-run mass patch scripts."
