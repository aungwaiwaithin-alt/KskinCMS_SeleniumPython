#!/bin/bash
# Mobile one-click: FRESH run + visible paced steps + open ONLY a new HTML report in Chrome.
# Does NOT rewrite legacy scripts (sed broke heredocs/quotes → "unexpected end of file").
set -uo pipefail
cd "$(dirname "$0")" || exit 1

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM_PY="${APPIUM_PY:-$AQUA/MCP_Appium_Server/python}"
SELF_DIR="$(pwd)"
BASE="$(basename "$0")"
RUN_ID="$(date +%Y%m%d_%H%M%S)"
START_EPOCH="$(date +%s)"

PACE_FIRST=""
for d in \
  "$SELF_DIR/python_path_first" \
  "$AQUA/KskinCMS/one_click/python_path_first" \
  "$HOME/AquaProjects/KskinCMS/one_click/python_path_first"
do
  [[ -f "$d/helpers/step_report.py" ]] && { PACE_FIRST="$d"; break; }
done

PACE_STARTUP=""
for f in \
  "$SELF_DIR/pace_startup.py" \
  "$AQUA/KskinCMS/one_click/pace_startup.py" \
  "$HOME/AquaProjects/KskinCMS/one_click/pace_startup.py"
do
  [[ -f "$f" ]] && { PACE_STARTUP="$f"; break; }
done

export PATH="/Library/Frameworks/Python.framework/Versions/3.8/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
export STEP_PAUSE_SEC="${STEP_PAUSE_SEC:-3}"
export STEP_PRE_PAUSE_SEC="${STEP_PRE_PAUSE_SEC:-1}"
export AQUA_ROOT="$AQUA"
export APPIUM_PY
export ONE_CLICK_KEEP_OPEN=1
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export KSKIN_PACE_STARTUP="${PACE_STARTUP}"
export KSKIN_PACE_FIRST="${PACE_FIRST}"

if [[ -n "$PACE_FIRST" ]]; then
  export PYTHONPATH="$PACE_FIRST:$APPIUM_PY:${PYTHONPATH:-}"
else
  export PYTHONPATH="$APPIUM_PY:${PYTHONPATH:-}"
fi

REAL_PY="$(command -v python3.8 || command -v python3)"
REAL_OPEN="$(command -v open || echo /usr/bin/open)"
BIN_DIR="$SELF_DIR/.one_click_bin"
mkdir -p "$BIN_DIR"

# --- Fake `open`: suppress HTML during the suite (we open Chrome ourselves after) ---
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

# --- Python shim: inject pace bootstrap for script / -m / -c / stdin ---
cat > "$BIN_DIR/_kskin_py_shim.py" <<'PY'
import os, sys, runpy

def bootstrap():
    startup = os.environ.get("KSKIN_PACE_STARTUP") or ""
    first = os.environ.get("KSKIN_PACE_FIRST") or ""
    appium = os.environ.get("APPIUM_PY") or ""
    parts = []
    if first:
        parts.append(first)
    if appium:
        parts.append(appium)
    cur = os.environ.get("PYTHONPATH", "")
    if cur:
        parts.extend(p for p in cur.split(os.pathsep) if p and p not in parts)
    os.environ["PYTHONPATH"] = os.pathsep.join(parts)
    for p in reversed(parts):
        if p and p not in sys.path:
            sys.path.insert(0, p)
    if startup and os.path.isfile(startup):
        with open(startup, "r", encoding="utf-8") as f:
            exec(compile(f.read(), startup, "exec"), {"__name__": "__kskin_pace__"})

def main(argv):
    bootstrap()
    if not argv:
        code = sys.stdin.read()
        exec(compile(code, "<stdin>", "exec"), {"__name__": "__main__"})
        return 0
    if argv[0] == "-u":
        argv = argv[1:]
    if not argv:
        code = sys.stdin.read()
        exec(compile(code, "<stdin>", "exec"), {"__name__": "__main__"})
        return 0
    if argv[0] == "-c":
        sys.argv = ["-c", *argv[2:]]
        exec(compile(argv[1], "<string>", "exec"), {"__name__": "__main__"})
        return 0
    if argv[0] == "-m":
        sys.argv = argv[1:]
        runpy.run_module(argv[1], run_name="__main__", alter_sys=True)
        return 0
    sys.argv = argv
    runpy.run_path(argv[0], run_name="__main__")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except Exception:
        import traceback
        traceback.print_exc()
        raise SystemExit(1)
PY

cat > "$BIN_DIR/python3" <<EOF
#!/bin/bash
export PYTHONUNBUFFERED=1
export PYTHONPATH="${PACE_FIRST}:$APPIUM_PY:\${PYTHONPATH:-}"
export KSKIN_PACE_STARTUP="$PACE_STARTUP"
export KSKIN_PACE_FIRST="$PACE_FIRST"
export APPIUM_PY="$APPIUM_PY"
exec "$REAL_PY" -u "$BIN_DIR/_kskin_py_shim.py" "\$@"
EOF
cp "$BIN_DIR/python3" "$BIN_DIR/python"
chmod +x "$BIN_DIR/python3" "$BIN_DIR/python"

# Put shims first on PATH
export PATH="$BIN_DIR:$PATH"

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
echo "  Appium reports: $APPIUM_PY/reports"
echo "  Pace: ${STEP_PAUSE_SEC}s between steps — watch the device"
echo "  Python shim: $BIN_DIR/python3"
echo "  Pace startup: ${PACE_STARTUP:-NONE}"
echo "  Legacy (unchanged): $LEGACY"
echo "  Run id: $RUN_ID"
echo "  Started: $(date)"
echo "=============================================================="

if [[ ! -d "$APPIUM_PY" ]]; then
  echo "ERROR: Missing $APPIUM_PY" >&2
  read -r -p "Press Enter…" _; exit 1
fi
if [[ ! -f "$LEGACY" ]]; then
  echo "ERROR: Missing legacy runner: $LEGACY" >&2
  echo "Re-run: bash \"\$HOME/AquaProjects/KskinCMS/one_click/install_one_click_commands.sh\"" >&2
  read -r -p "Press Enter…" _; exit 1
fi

# Quick syntax check — fail fast with a clear message
if ! bash -n "$LEGACY" 2>/tmp/kskin_legacy_bashn.err; then
  echo "ERROR: legacy script has a bash syntax error:" >&2
  cat /tmp/kskin_legacy_bashn.err >&2
  echo "Restore from Time Machine / re-copy your known-good .command into:" >&2
  echo "  $SELF_DIR/.legacy/$BASE" >&2
  read -r -p "Press Enter…" _; exit 2
fi

REPORT_DIR="$APPIUM_PY/reports"
mkdir -p "$REPORT_DIR"

echo ""
echo "Keep Terminal visible. STEP banners should appear while the device moves."
echo "Chrome opens ONLY if a NEW report is written after this start time."
echo ""
sleep 1

echo "[one-click] Launching legacy suite (no script rewrite)…"
set +e
# Feed a few Enter keypresses so nested "Press any key" at end of legacy does not hang.
# Use a coproc-style background yes only for stdin of the legacy bash.
(
  # small delay then newlines for trailing reads; suite itself should not need stdin
  sleep 1
  # keep feeding Enter slowly in case legacy waits at the end
  for _i in 1 2 3 4 5 6 7 8 9 10; do
    printf '\n'
    sleep 2
  done
) | bash "$LEGACY"
ST=${PIPESTATUS[1]:-$?}
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
  echo "==============================================================" >&2
  echo "ERROR: No NEW HTML report since this run started." >&2
  echo "Not opening an old report." >&2
  echo "Scroll Terminal for Appium/Python errors." >&2
  echo "==============================================================" >&2
  OLD="$(ls -t "$REPORT_DIR"/*.html 2>/dev/null | head -1 || true)"
  [[ -n "$OLD" ]] && echo "Newest OLD report (not opened): $OLD" >&2
fi

echo "Finished: $(date)  (exit $ST)"
read -r -p "Press Enter to close…" _ || true
exit "$ST"
