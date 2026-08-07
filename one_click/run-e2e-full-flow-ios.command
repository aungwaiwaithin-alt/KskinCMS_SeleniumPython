#!/bin/bash
# Mobile one-click: FRESH run + paced steps + open ONLY a new HTML report.
# Critical: do NOT put a fake helpers/ package first on PYTHONPATH (breaks pytest collection).
set -uo pipefail
cd "$(dirname "$0")" || exit 1

AQUA="${AQUA_ROOT:-$HOME/AquaProjects}"
APPIUM_PY="${APPIUM_PY:-$AQUA/MCP_Appium_Server/python}"
SELF_DIR="$(pwd)"
BASE="$(basename "$0")"
RUN_ID="$(date +%Y%m%d_%H%M%S)"
START_EPOCH="$(date +%s)"

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

# ONLY Appium python on PYTHONPATH — never a shadow helpers package
export PYTHONPATH="$APPIUM_PY${PYTHONPATH:+:$PYTHONPATH}"

REAL_PY="$(command -v python3.8 || command -v python3)"
REAL_OPEN="$(command -v open || echo /usr/bin/open)"
# Prefer real pytest module via our shim; keep absolute path to real pytest if needed
REAL_PYTEST="$(command -v pytest || true)"

BIN_DIR="$SELF_DIR/.one_click_bin"
mkdir -p "$BIN_DIR"

# Fake `open`: suppress HTML during suite (we open Chrome after if fresh)
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

cat > "$BIN_DIR/_kskin_py_shim.py" <<'PY'
import os, sys, runpy

def bootstrap():
    startup = os.environ.get("KSKIN_PACE_STARTUP") or ""
    appium = os.environ.get("APPIUM_PY") or ""
    parts = []
    if appium:
        parts.append(appium)
    cur = os.environ.get("PYTHONPATH", "")
    if cur:
        parts.extend(p for p in cur.split(os.pathsep) if p and p not in parts)
    # Drop any accidental one_click python_path_first helpers shadow
    parts = [p for p in parts if "python_path_first" not in p.replace("\\", "/")]
    os.environ["PYTHONPATH"] = os.pathsep.join(parts)
    # Rebuild sys.path prefixes
    for p in list(sys.path):
        if p and "python_path_first" in p.replace("\\", "/"):
            try:
                sys.path.remove(p)
            except ValueError:
                pass
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
        mod = argv[1]
        sys.argv = argv[1:]
        runpy.run_module(mod, run_name="__main__", alter_sys=True)
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
export PYTHONPATH="$APPIUM_PY:\${PYTHONPATH:-}"
export KSKIN_PACE_STARTUP="$PACE_STARTUP"
export APPIUM_PY="$APPIUM_PY"
# Strip shadow path if something re-added it
export PYTHONPATH="\$(echo "\$PYTHONPATH" | tr ':' '\n' | grep -v python_path_first | paste -sd: -)"
exec "$REAL_PY" -u "$BIN_DIR/_kskin_py_shim.py" "\$@"
EOF
cp "$BIN_DIR/python3" "$BIN_DIR/python"
chmod +x "$BIN_DIR/python3" "$BIN_DIR/python"

# Route bare `pytest` through our python so pace + path fixes apply
cat > "$BIN_DIR/pytest" <<EOF
#!/bin/bash
export PYTHONUNBUFFERED=1
export PYTHONPATH="$APPIUM_PY:\${PYTHONPATH:-}"
export KSKIN_PACE_STARTUP="$PACE_STARTUP"
export APPIUM_PY="$APPIUM_PY"
export PYTHONPATH="\$(echo "\$PYTHONPATH" | tr ':' '\n' | grep -v python_path_first | paste -sd: -)"
exec "$BIN_DIR/python3" -m pytest "\$@"
EOF
chmod +x "$BIN_DIR/pytest"

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
echo "  Appium : $APPIUM_PY"
echo "  Pace   : ${STEP_PAUSE_SEC}s between steps"
echo "  Startup: ${PACE_STARTUP:-NONE}"
echo "  Legacy : $LEGACY"
echo "  Note   : PYTHONPATH has NO helpers shadow (pytest collection safe)"
echo "  Run id : $RUN_ID"
echo "  Started: $(date)"
echo "=============================================================="

if [[ ! -d "$APPIUM_PY" ]]; then
  echo "ERROR: Missing $APPIUM_PY" >&2
  read -r -p "Press Enter…" _; exit 1
fi
if [[ ! -f "$LEGACY" ]]; then
  echo "ERROR: Missing legacy runner: $LEGACY" >&2
  read -r -p "Press Enter…" _; exit 1
fi
if ! bash -n "$LEGACY" 2>/tmp/kskin_legacy_bashn.err; then
  echo "ERROR: legacy bash syntax error:" >&2
  cat /tmp/kskin_legacy_bashn.err >&2
  read -r -p "Press Enter…" _; exit 2
fi

REPORT_DIR="$APPIUM_PY/reports"
mkdir -p "$REPORT_DIR"

echo ""
echo "Keep Terminal visible. Device should move; STEP banners after each step."
echo ""
sleep 1

echo "[one-click] Launching legacy suite…"
set +e
# stdin = /dev/null so nested "Press Enter" cannot hang, and pytest is not fed junk
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
  echo "==============================================================" >&2
  echo "ERROR: No NEW HTML report since this run started." >&2
  echo "Scroll UP in Terminal for the real pytest/Appium error (collection/import)." >&2
  echo "==============================================================" >&2
fi

echo "Finished: $(date)  (exit $ST)"
read -r -p "Press Enter to close…" _ || true
exit "$ST"
