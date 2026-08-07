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
echo "=== 2) Restore pages/ from Appium git (best effort) ==="
if [[ -d "$APPIUM/.git" ]]; then
  cd "$APPIUM"
  # Prefer the e2e commit if present; else leave pages as-is after user cleanup
  if git cat-file -e 8f544632f1b717687dd5be6df13df353ca0827b8^{commit} 2>/dev/null; then
    echo "Checking out pages/ + helpers/ from 8f544632 (July 29 e2e commit)..."
    git checkout 8f544632f1b717687dd5be6df13df353ca0827b8 -- \
      python/pages \
      python/helpers \
      python/conftest.py \
      python/tests 2>/dev/null || \
    git checkout 8f544632f1b717687dd5be6df13df353ca0827b8 -- python/pages python/conftest.py
  else
    echo "Commit 8f544632 not found — using current pages/ (you should have cleaned junk)."
  fi
else
  echo "No .git in $APPIUM — skip checkout. Ensure pages/ is your clean original."
fi

# Remove ONLY our known junk helpers (safe)
rm -f "$APPIUM_PY/helpers/android_type.py" \
      "$APPIUM_PY/helpers/patch_email_runtime.py" 2>/dev/null || true
# Remove auto-generated permissions stub if it still says Auto-generated compat
if [[ -f "$APPIUM_PY/pages/permissions_android_page.py" ]] && \
   grep -q "Auto-generated compat page object" "$APPIUM_PY/pages/permissions_android_page.py" 2>/dev/null; then
  echo "Removing auto-generated permissions_android_page.py stub..."
  rm -f "$APPIUM_PY/pages/permissions_android_page.py"
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
echo "Double-click a generated .command. If a page AttributeError appears,"
echo "that means the PYTHON page object in Appium git is incomplete — fix pages in Aqua,"
echo "do not re-run mass patch scripts."
