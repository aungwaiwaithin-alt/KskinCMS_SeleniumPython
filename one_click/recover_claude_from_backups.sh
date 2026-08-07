#!/usr/bin/env bash
# Recover signup_login_android_page.py from the best local .bak / prior copy.
# Does NOT invent methods. Does NOT git-checkout pages (that wiped Claude before).
#
# Run:
#   bash ~/AquaProjects/KskinCMS/one_click/recover_claude_from_backups.sh
#   bash ~/AquaProjects/KskinCMS/one_click/recover_claude_from_backups.sh --apply
set -euo pipefail

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM="${APPIUM_ROOT:-$AQUA/MCP_Appium_Server}"
APPIUM_PY="${APPIUM_PY:-$APPIUM/python}"
PAGE="$APPIUM_PY/pages/signup_login_android_page.py"
TEST="$APPIUM_PY/tests/test_signup_login_android.py"
APPLY=0
[[ "${1:-}" == "--apply" ]] && APPLY=1

if [[ ! -f "$TEST" ]]; then
  echo "ERROR: missing test $TEST"
  exit 1
fi

echo "=============================================================="
echo "  Recover Claude page from local backups"
echo "  apply=$APPLY"
echo "=============================================================="

BEST=""
BEST_SCORE=-1
BEST_INFO=""

while IFS= read -r -d '' f; do
  info="$(python3 - "$f" "$TEST" <<'PY'
import re, sys
from pathlib import Path
p = Path(sys.argv[1])
page = p.read_text(encoding="utf-8", errors="ignore")
test = Path(sys.argv[2]).read_text(encoding="utf-8", errors="ignore")
have = set(re.findall(r"^\s{4}def ([A-Za-z_][A-Za-z0-9_]*)\(", page, flags=re.M))
need = set(re.findall(r"\bpage\.([A-Za-z_][A-Za-z0-9_]*)\s*\(", test))
must = {"enter_otp", "tap_create_account", "_hide_keyboard_if_shown"}
hits = len(need & have)
must_hits = len(must & have)
our = len(re.findall(r"ENTER_OTP_ONLY|KSKIN_|Auto-generated|compat stub|Not in git history", page))
size = p.stat().st_size
# Reject empty / tiny junk, but keep small real pages that already have must-methods
if size < 80 and must_hits == 0:
    print("SKIP|0|0|0|0|0")
else:
    score = must_hits * 1000 + hits * 10 - our * 50 + size // 1000
    print(f"OK|{score}|{must_hits}|{hits}|{our}|{size}")
PY
)"
  IFS='|' read -r tag score must_hits hits our size <<<"$info"
  [[ "$tag" == "OK" ]] || continue
  printf "  score=%5s must=%s hits=%s our=%s size=%s  %s\n" \
    "$score" "$must_hits" "$hits" "$our" "$size" "$f"
  if [[ "$score" -gt "$BEST_SCORE" ]]; then
    BEST_SCORE=$score
    BEST=$f
    BEST_INFO="$info"
  fi
done < <(find "$APPIUM_PY/pages" -maxdepth 1 -type f \( \
    -name 'signup_login_android_page.py' -o \
    -name 'signup_login_android_page.py.*' \
  \) -print0 2>/dev/null)

# Also scan common backup dump locations
for extra in \
  "$APPIUM_PY/pages/.bak" \
  "$APPIUM/_helpers_backup_"* \
  "$HOME/Desktop/One click bash files/.purged_mobile_"* \
  "$AQUA/_helpers_backup_"*
do
  [[ -e "$extra" ]] || continue
  while IFS= read -r -d '' f; do
    [[ "$(basename "$f")" == signup_login_android_page.py* ]] || continue
    info="$(python3 - "$f" "$TEST" <<'PY'
import re, sys
from pathlib import Path
p = Path(sys.argv[1])
page = p.read_text(encoding="utf-8", errors="ignore")
test = Path(sys.argv[2]).read_text(encoding="utf-8", errors="ignore")
have = set(re.findall(r"^\s{4}def ([A-Za-z_][A-Za-z0-9_]*)\(", page, flags=re.M))
need = set(re.findall(r"\bpage\.([A-Za-z_][A-Za-z0-9_]*)\s*\(", test))
must = {"enter_otp", "tap_create_account", "_hide_keyboard_if_shown"}
hits = len(need & have)
must_hits = len(must & have)
our = len(re.findall(r"ENTER_OTP_ONLY|KSKIN_|Auto-generated|compat stub|Not in git history", page))
size = p.stat().st_size
if size < 80 and must_hits == 0:
    print("SKIP|0|0|0|0|0")
else:
    score = must_hits * 1000 + hits * 10 - our * 50 + size // 1000
    print(f"OK|{score}|{must_hits}|{hits}|{our}|{size}")
PY
)"
    IFS='|' read -r tag score must_hits hits our size <<<"$info"
    [[ "$tag" == "OK" ]] || continue
    printf "  score=%5s must=%s hits=%s our=%s size=%s  %s\n" \
      "$score" "$must_hits" "$hits" "$our" "$size" "$f"
    if [[ "$score" -gt "$BEST_SCORE" ]]; then
      BEST_SCORE=$score
      BEST=$f
      BEST_INFO="$info"
    fi
  done < <(find "$extra" -type f -name 'signup_login_android_page.py*' -print0 2>/dev/null)
done

echo ""
if [[ -z "$BEST" ]]; then
  echo "No usable backup found."
  echo "Use Cursor Local History on:"
  echo "  $PAGE"
  exit 1
fi

IFS='|' read -r _ score must_hits hits our size <<<"$BEST_INFO"
echo "BEST: $BEST"
echo "  score=$score  must_methods=$must_hits/3  test_hits=$hits  our_markers=$our  bytes=$size"

if [[ "$must_hits" -lt 2 ]]; then
  echo ""
  echo "WARNING: best backup is still missing critical methods."
  echo "Do NOT apply yet — open Cursor Local History instead."
  exit 2
fi

if [[ "$APPLY" -ne 1 ]]; then
  echo ""
  echo "Dry-run only. To apply:"
  echo "  bash $0 --apply"
  exit 0
fi

mkdir -p "$APPIUM_PY/pages"
STASH="$PAGE.pre_recover_$(date +%Y%m%d_%H%M%S)"
if [[ -f "$PAGE" ]]; then
  cp -f "$PAGE" "$STASH"
  echo "Stashed current → $STASH"
fi
cp -f "$BEST" "$PAGE"
echo "Restored → $PAGE"
echo ""
echo "Verify:"
grep -n 'def enter_otp\|def tap_create_account\|ENTER_OTP_ONLY\|KSKIN_' "$PAGE" | head -20 || true
echo ""
echo "Re-run original test:"
echo "  bash ~/AquaProjects/KskinCMS/one_click/run_original_mobile_test.sh android-signup"
