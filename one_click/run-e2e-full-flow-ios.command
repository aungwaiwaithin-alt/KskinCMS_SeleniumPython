#!/bin/bash
# Mobile one-click: run your original *.legacy unchanged (it owns PYTHONPATH/pytest).
# We only: (1) suppress mid-run HTML open, (2) open Chrome if a NEW report appears,
# (3) optional soft pace via STEP_PAUSE_SEC if the suite already honors it.
set -uo pipefail
cd "$(dirname "$0")" || exit 1

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM_PY="${APPIUM_PY:-$AQUA/MCP_Appium_Server/python}"
SELF_DIR="$(pwd)"
BASE="$(basename "$0")"
RUN_ID="$(date +%Y%m%d_%H%M%S)"
START_EPOCH="$(date +%s)"

export STEP_PAUSE_SEC="${STEP_PAUSE_SEC:-3}"
export STEP_PRE_PAUSE_SEC="${STEP_PRE_PAUSE_SEC:-1}"
export AQUA_ROOT="$AQUA"
export APPIUM_PY
export ONE_CLICK_KEEP_OPEN=1
export PYTHONUNBUFFERED=1

# Critical: do NOT override PYTHONPATH / python3 / pytest — legacy .command owns that.
# Clear any leftover shadow from older one-click installs in this shell only.
if [[ -n "${PYTHONPATH:-}" ]]; then
  export PYTHONPATH="$(echo "$PYTHONPATH" | tr ':' '\n' | grep -v 'python_path_first' | grep -v '^$' | paste -sd: -)"
fi
unset KSKIN_PACE_FIRST KSKIN_PACE_STARTUP PYTHONSTARTUP

REAL_OPEN="$(command -v open || echo /usr/bin/open)"
BIN_DIR="$SELF_DIR/.one_click_bin"
mkdir -p "$BIN_DIR"
# Remove old python/pytest shims that broke helpers.dynamic_data imports
rm -f "$BIN_DIR/python" "$BIN_DIR/python3" "$BIN_DIR/pytest" "$BIN_DIR/_kskin_py_shim.py" 2>/dev/null || true

# Fake open: suppress HTML during suite; we open Chrome ourselves after if fresh
cat > "$BIN_DIR/open" <<EOF
#!/bin/bash
for a in "\$@"; do
  case "\$a" in
    *.html|*.htm)
      echo "[one-click] suppressed legacy open of \$a"
      exit 0
      ;;
  esac
done
exec "$REAL_OPEN" "\$@"
EOF
chmod +x "$BIN_DIR/open"

# Put ONLY fake open ahead of system PATH (not a fake python)
export PATH="$BIN_DIR:/Library/Frameworks/Python.framework/Versions/3.8/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

LEGACY="$SELF_DIR/${BASE}.legacy"
[[ -f "$LEGACY" ]] || LEGACY="$SELF_DIR/.legacy/${BASE}"

HINT="SIGNUP"
case "$BASE" in
  *ios-signup*) HINT="KS-SIGNUP-iOS" ;;
  *android-signup*) HINT="KS-SIGNUP" ;;
  *ios-full*) HINT="KS-REGR-iOS" ;;
  *android-full*) HINT="KS-REGR-AND" ;;
  *e2e*ios*) HINT="E2E" ;;
  *e2e*android*) HINT="E2E" ;;
esac

echo "=============================================================="
echo "  Mobile one-click (FRESH RUN): $BASE"
echo "  Mode   : legacy-owned PYTHONPATH (no python shim)"
echo "  Appium : $APPIUM_PY"
echo "  Legacy : $LEGACY"
echo "  Run id : $RUN_ID"
echo "  Started: $(date)"
echo "=============================================================="

if [[ ! -d "$APPIUM_PY" ]]; then
  echo "ERROR: Missing $APPIUM_PY" >&2
  read -r -p "Press Enter…" _; exit 1
fi
if [[ ! -f "$LEGACY" ]]; then
  echo "ERROR: Missing legacy runner: $LEGACY" >&2
  echo "Re-run installer, or copy your known-good .command to:" >&2
  echo "  $SELF_DIR/.legacy/$BASE" >&2
  read -r -p "Press Enter…" _; exit 1
fi
if ! bash -n "$LEGACY" 2>/tmp/kskin_legacy_bashn.err; then
  echo "ERROR: legacy bash syntax error:" >&2
  cat /tmp/kskin_legacy_bashn.err >&2
  read -r -p "Press Enter…" _; exit 2
fi

# Prove Appium helpers import works in THIS environment (same python legacy will likely use)
echo "[one-click] Preflight helpers.dynamic_data import…"
PRE_PY="$(command -v python3.8 || command -v python3)"
if ! "$PRE_PY" - <<PY
import os, sys
sys.path.insert(0, os.environ.get("APPIUM_PY", ""))
try:
    import helpers.dynamic_data as d
    print("[one-click] OK:", getattr(d, "__file__", d))
except Exception as e:
    print("[one-click] FAIL import helpers.dynamic_data:", e)
    # list helpers package
    import helpers, pkgutil
    print("[one-click] helpers at:", getattr(helpers, "__file__", helpers))
    print("[one-click] helpers submodules:", [m.name for m in pkgutil.iter_modules(helpers.__path__)])
    raise
PY
then
  echo "ERROR: helpers.dynamic_data missing/broken under $APPIUM_PY" >&2
  echo "Fix Appium tree first, or restore MCP_Appium_Server from backup/zip." >&2
  read -r -p "Press Enter…" _; exit 2
fi

REPORT_DIR="$APPIUM_PY/reports"
mkdir -p "$REPORT_DIR"

echo ""
echo "Launching your original signup/regression script…"
echo "Watch the emulator/simulator — this should take minutes, not seconds."
echo ""

set +e
bash "$LEGACY" </dev/null
ST=$?
set -e

pick_new_report() {
  local f mtime best="" best_m=0
  local files=()
  while IFS= read -r f; do files+=("$f"); done < <(ls -1 "$REPORT_DIR"/*"${HINT}"*.html 2>/dev/null || true)
  if [[ ${#files[@]} -eq 0 ]]; then
    while IFS= read -r f; do files+=("$f"); done < <(ls -1 "$REPORT_DIR"/*.html 2>/dev/null || true)
  fi
  for f in "${files[@]}"; do
    [[ -f "$f" ]] || continue
    mtime="$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null || echo 0)"
    if [[ "$mtime" -ge "$START_EPOCH" ]] && [[ "$mtime" -ge "$best_m" ]]; then
      best="$f"; best_m="$mtime"
    fi
  done
  printf '%s' "$best"
}

NEW_REPORT="$(pick_new_report)"
echo ""
if [[ -n "$NEW_REPORT" ]]; then
  echo "Fresh report: $NEW_REPORT"
  echo "Opening Google Chrome…"
  if [[ -d "/Applications/Google Chrome.app" ]]; then
    "$REAL_OPEN" -a "Google Chrome" "$NEW_REPORT" || "$REAL_OPEN" "$NEW_REPORT" || true
  else
    "$REAL_OPEN" "$NEW_REPORT" || true
  fi
else
  echo "ERROR: No NEW HTML report since this run started." >&2
  echo "Scroll UP for the pytest/Appium error from the legacy script." >&2
fi

echo "Finished: $(date)  (exit $ST)"
read -r -p "Press Enter to close…" _ || true
exit "$ST"
