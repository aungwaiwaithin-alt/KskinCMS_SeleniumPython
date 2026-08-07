#!/usr/bin/env bash
# Prove whether Appium python files are Claude originals or Cursor-agent modifications.
# Also hunt .bak_* files that still have the methods your test needs.
#
# Run:
#   bash ~/AquaProjects/KskinCMS/one_click/prove_originals.sh
set -uo pipefail

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM="${APPIUM_ROOT:-$AQUA/MCP_Appium_Server}"
APPIUM_PY="${APPIUM_PY:-$APPIUM/python}"
PAGE="$APPIUM_PY/pages/signup_login_android_page.py"
TEST="$APPIUM_PY/tests/test_signup_login_android.py"
DD="$APPIUM_PY/helpers/dynamic_data.py"

OUR_MARKERS='ENTER_OTP_ONLY|KSKIN_|Auto-generated|compat stub|restored stub|Compat stub|short uniq fallback|Not in git history — added|prefer iOS Claude copy'

echo "=============================================================="
echo "  Prove originals vs Cursor modifications"
echo "  $APPIUM_PY"
echo "=============================================================="

score_file() {
  local f="$1"
  [[ -f "$f" ]] || { echo "0"; return; }
  python3 - "$f" "$TEST" <<'PY'
import re, sys
from pathlib import Path
page = Path(sys.argv[1]).read_text(encoding="utf-8", errors="ignore")
test = Path(sys.argv[2]).read_text(encoding="utf-8", errors="ignore") if Path(sys.argv[2]).is_file() else ""
have = set(re.findall(r"^\s{4}def ([A-Za-z_][A-Za-z0-9_]*)\(", page, flags=re.M))
need = set(re.findall(r"\bpage\.([A-Za-z_][A-Za-z0-9_]*)\s*\(", test))
must = {"enter_otp", "tap_create_account", "_hide_keyboard_if_shown"}
hits = len(need & have)
must_hits = len(must & have)
our = len(re.findall(r"ENTER_OTP_ONLY|KSKIN_|Auto-generated|compat stub|Not in git history", page))
print(f"{hits}|{must_hits}|{len(have)}|{our}|{Path(sys.argv[1]).stat().st_size}")
PY
}

print_status() {
  local label="$1" f="$2"
  if [[ ! -f "$f" ]]; then
    echo "$label: MISSING"
    return
  fi
  local ours=0
  if grep -qE "$OUR_MARKERS" "$f" 2>/dev/null; then ours=1; fi
  echo "$label:"
  echo "  path : $f"
  echo "  size : $(wc -c < "$f" | tr -d ' ') bytes"
  echo "  mtime: $(date -r "$f" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || stat -c %y "$f" 2>/dev/null | cut -d. -f1)"
  if [[ "$ours" -eq 1 ]]; then
    echo "  fingerprint: CURSOR-MODIFIED (our markers found)"
    grep -nE "$OUR_MARKERS" "$f" 2>/dev/null | head -8 | sed 's/^/    /'
  else
    echo "  fingerprint: no Cursor markers"
  fi
}

print_status "PAGE " "$PAGE"
print_status "TEST " "$TEST"
print_status "DATA " "$DD"

echo ""
echo "--- Methods the CURRENT page has vs what the test calls ---"
if [[ -f "$PAGE" && -f "$TEST" ]]; then
  python3 - "$PAGE" "$TEST" <<'PY'
import re, sys
from pathlib import Path
page = Path(sys.argv[1]).read_text(encoding="utf-8", errors="ignore")
test = Path(sys.argv[2]).read_text(encoding="utf-8", errors="ignore")
have = set(re.findall(r"^\s{4}def ([A-Za-z_][A-Za-z0-9_]*)\(", page, flags=re.M))
need = set(re.findall(r"\bpage\.([A-Za-z_][A-Za-z0-9_]*)\s*\(", test))
missing = sorted(need - have)
print(f"test calls {len(need)} methods; page has {len(have)}; MISSING {len(missing)}:")
for m in missing:
    mark = " <<<" if m in {"enter_otp", "tap_create_account"} else ""
    print(f"  - {m}{mark}")
if not missing:
    print("  (none)")
PY
fi

echo ""
echo "--- Hunt backups that still look like Claude (have tap_create_account) ---"
BEST=""
BEST_SCORE=-1
while IFS= read -r -d '' f; do
  IFS='|' read -r hits must_hits nmethods our size <<<"$(score_file "$f")"
  # Prefer: has must methods, fewer our markers, more hits, larger size
  score=$(( must_hits * 1000 + hits * 10 - our * 50 + (size / 1000) ))
  printf "  %5d pts  must=%s/%s  hits=%s  our_markers=%s  %s\n" \
    "$score" "$must_hits" "3" "$hits" "$our" "$f"
  if [[ "$score" -gt "$BEST_SCORE" ]]; then
    BEST_SCORE=$score
    BEST=$f
  fi
done < <(find "$APPIUM_PY/pages" -maxdepth 1 \( \
    -name 'signup_login_android_page.py' -o \
    -name 'signup_login_android_page.py.bak*' -o \
    -name 'signup_login_android_page.py.*' \
  \) -type f -print0 2>/dev/null)

echo ""
if [[ -n "$BEST" ]]; then
  echo "BEST CANDIDATE: $BEST  (score $BEST_SCORE)"
  echo ""
  echo "To restore THAT file as the live page (does not invent methods):"
  echo "  cp -f \"$BEST\" \"$PAGE\""
  echo ""
  echo "Or run:"
  echo "  bash ~/AquaProjects/KskinCMS/one_click/recover_claude_from_backups.sh"
else
  echo "No page backups found under pages/."
fi

echo ""
echo "--- Cursor Local History (manual — richest Claude source) ---"
echo "In Cursor: open"
echo "  $PAGE"
echo "then Timeline / Local History and pick a version FROM BEFORE Aug 7 Cursor patches"
echo "that contains def tap_create_account and def enter_otp."
echo ""
echo "Also check:"
echo "  ~/Library/Application Support/Cursor/User/History/"
echo "  Time Machine for $APPIUM_PY/pages/"
echo "=============================================================="

# Exit codes:
# 0 = usable for running (methods complete)
# 2 = markers present but methods may still be complete (warning)
# 3 = incomplete (missing tap_create_account / test methods)
if [[ -f "$PAGE" && -f "$TEST" ]]; then
  EVAL="$(python3 - "$PAGE" "$TEST" <<'PY'
import re, sys
from pathlib import Path
page = Path(sys.argv[1]).read_text(encoding="utf-8", errors="ignore")
test = Path(sys.argv[2]).read_text(encoding="utf-8", errors="ignore")
have = set(re.findall(r"^\s{4}def ([A-Za-z_][A-Za-z0-9_]*)\(", page, flags=re.M))
need = set(re.findall(r"\bpage\.([A-Za-z_][A-Za-z0-9_]*)\s*\(", test))
missing = len(need - have)
has_tap = "tap_create_account" in have
our = 1 if re.search(r"ENTER_OTP_ONLY|KSKIN_|Auto-generated|compat stub|Not in git history|prefer iOS Claude", page) else 0
print(f"{missing}|{int(has_tap)}|{our}")
PY
)"
  IFS='|' read -r missing has_tap our <<<"$EVAL"
  if [[ "$has_tap" != "1" || "$missing" != "0" ]]; then
    echo "VERDICT: INCOMPLETE — missing methods (missing=$missing tap=$has_tap)."
    echo "         Recover bak / Local History, then re-run prove."
    exit 3
  fi
  if [[ "$our" == "1" ]]; then
    echo "VERDICT: METHODS COMPLETE (0 missing) but Cursor markers still in file."
    echo "         Safe to RUN the original test now. Markers are cosmetic."
    exit 0
  fi
fi
echo "VERDICT: page looks usable (methods complete, no Cursor markers)."
exit 0