#!/usr/bin/env python3
"""Generate clean mobile one-click .command files from MCP_Appium_Server/python/tests.

No page-object patching. Each .command:
  - uses Appium project .venv
  - starts Appium if needed
  - checks device (android) / notes simulator (ios)
  - runs: python -m pytest -s -vv <test_file>
  - opens ONLY a report newer than start time in Chrome

Usage:
  python3 generate_mobile_commands.py --dest ~/Desktop/One\\ click\\ bash\\ files \\
      --appium-py ~/AquaProjects/MCP_Appium_Server/python
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

# Map test filename → Desktop .command basename (Claude-era names)
NAME_MAP = {
    "test_signup_login_android.py": "run-android-signup-login.command",
    "test_signup_login_ios.py": "run-ios-signup-login.command",
    "test_full_regression_android.py": "run-android-full-regression.command",
    "test_full_regression_ios.py": "run-ios-full-regression.command",
    "test_therapist_e2e_full_flow.py": "run-e2e-full-flow-android.command",  # default android therapist e2e
    "test_guest_android_002.py": "run-android-guest.command",
    "test_therapist_e2e_sidemenu.py": "run-android-therapist-sidemenu.command",
}

REPORT_HINT = {
    "test_signup_login_android.py": ("KS-SIGNUP-AND", "SIGNUP"),
    "test_signup_login_ios.py": ("KS-SIGNUP-iOS", "SIGNUP"),
    "test_full_regression_android.py": ("KS-REGR-AND", "REGR"),
    "test_full_regression_ios.py": ("KS-REGR-iOS", "REGR"),
    "test_therapist_e2e_full_flow.py": ("E2E", "E2E"),
    "test_guest_android_002.py": ("GUEST", "GUEST"),
    "test_therapist_e2e_sidemenu.py": ("E2E", "E2E"),
}


def platform_of(test_name: str) -> str:
    n = test_name.lower()
    if "ios" in n:
        return "ios"
    return "android"


def command_body(test_file: str, appium_py_default: str) -> str:
    plat = platform_of(test_file)
    hint, _ = REPORT_HINT.get(test_file, ("", ""))
    title = test_file.replace("test_", "").replace(".py", "").replace("_", " ").title()
    is_android = plat == "android"

    device_block = ""
    if is_android:
        device_block = r'''
echo "[2/4] Android device..."
command -v adb >/dev/null || { echo "ERROR: adb not found"; read -r -p "Press Enter…" _; exit 1; }
adb start-server >/dev/null 2>&1 || true
DEV="$(adb devices | awk 'NR>1 && $2=="device"{print $1}')"
[[ -n "$DEV" ]] || { echo "ERROR: no Android device/emulator"; read -r -p "Press Enter…" _; exit 1; }
echo "  $DEV"
'''
    else:
        device_block = r'''
echo "[2/4] iOS simulator/device..."
command -v xcrun >/dev/null && xcrun simctl list devices booted 2>/dev/null | head -10 || true
'''

    return f'''#!/bin/bash
# AUTO-GENERATED from Appium test: {test_file}
# Do not hand-patch page objects from this runner. Fix pages/ in MCP_Appium_Server.
set -uo pipefail
START_EPOCH="$(date +%s)"

APPIUM_PY="${{APPIUM_PY:-$HOME/AquaProjects/MCP_Appium_Server/python}}"
TEST="tests/{test_file}"
HINT="{hint}"

echo "========================================"
echo "  Kskin Mobile — {title}"
echo "  Test: $TEST"
echo "  Dir : $APPIUM_PY"
echo "  Started: $(date)"
echo "========================================"

[[ -d "$APPIUM_PY" ]] || {{ echo "ERROR: missing $APPIUM_PY"; read -r -p "Press Enter…" _; exit 1; }}
[[ -f "$APPIUM_PY/$TEST" ]] || {{ echo "ERROR: missing $APPIUM_PY/$TEST"; read -r -p "Press Enter…" _; exit 1; }}

BASE_PY=""
for c in /usr/local/bin/python3 /opt/homebrew/bin/python3.12 /opt/homebrew/bin/python3; do
  [[ -x "$c" ]] || continue
  "$c" -c 'import sys; raise SystemExit(0 if sys.version_info>=(3,9) else 1)' 2>/dev/null && BASE_PY="$c" && break
done
[[ -n "$BASE_PY" ]] || {{ echo "ERROR: need Python >= 3.9"; read -r -p "Press Enter…" _; exit 1; }}
VENV="$APPIUM_PY/.venv"
PY="$VENV/bin/python"
[[ -x "$PY" ]] || "$BASE_PY" -m venv "$VENV" || {{ echo "ERROR: venv failed"; read -r -p "Press Enter…" _; exit 1; }}
export PATH="$VENV/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"
export PYTHONPATH="$APPIUM_PY"
export PYTHONUNBUFFERED=1
"$PY" -c 'import pytest,appium' 2>/dev/null || "$PY" -m pip install -U pytest Appium-Python-Client selenium
echo "Python: $PY ($("$PY" -V))"

cd "$APPIUM_PY" || exit 1
mkdir -p reports

echo "[1/4] Appium..."
if ! curl -s http://127.0.0.1:4723/status >/dev/null 2>&1; then
  if command -v appium >/dev/null 2>&1; then
    nohup appium --port 4723 >"reports/appium_{plat}.log" 2>&1 &
    for _ in $(seq 1 15); do curl -s http://127.0.0.1:4723/status >/dev/null 2>&1 && break; sleep 1; done
  else
    echo "  WARNING: appium CLI not in PATH"
  fi
fi
{device_block}
echo "[3/4] pytest $TEST"
set +e
"$PY" -m pytest -s -vv "$TEST" --tb=short
ST=$?
set -e

echo "[4/4] Fresh report only (never open stale HTML)..."
BEST=""
BEST_M=0
shopt -s nullglob
for f in reports/*${{HINT}}*.html reports/*.html; do
  [[ -f "$f" ]] || continue
  m="$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null || echo 0)"
  if [[ "$m" -ge "$START_EPOCH" && "$m" -ge "$BEST_M" ]]; then BEST="$f"; BEST_M="$m"; fi
done
if [[ -n "$BEST" ]]; then
  echo "Fresh report → Chrome: $BEST"
  open -a "Google Chrome" "$BEST" 2>/dev/null || open "$BEST" || true
else
  echo "ERROR: No NEW HTML report from this run — not opening old report."
fi

echo "Finished: $(date)  exit=$ST"
read -r -n 1 -s -p "Press any key to close..."
echo
exit "$ST"
'''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", required=True, help="Folder to write .command files")
    ap.add_argument(
        "--appium-py",
        default=str(Path.home() / "AquaProjects" / "MCP_Appium_Server" / "python"),
    )
    ap.add_argument("--cms-pack", action="store_true", help="Also write into CMS one_click names")
    args = ap.parse_args()

    dest = Path(args.dest).expanduser()
    appium_py = Path(args.appium_py).expanduser()
    tests = sorted((appium_py / "tests").glob("test_*.py"))
    if not tests:
        print(f"ERROR: no test_*.py under {appium_py / 'tests'}")
        return 1

    dest.mkdir(parents=True, exist_ok=True)
    written = []
    for tf in tests:
        name = tf.name
        out_name = NAME_MAP.get(name)
        if not out_name:
            # generic name
            slug = re.sub(r"^test_|\.py$", "", name)
            slug = slug.replace("_", "-")
            out_name = f"run-{slug}.command"
        body = command_body(name, str(appium_py))
        out = dest / out_name
        out.write_text(body, encoding="utf-8")
        out.chmod(0o755)
        written.append(out)
        print(f"Wrote {out}  ←  {name}")

    # therapist e2e: if both naming conventions wanted
    print(f"Generated {len(written)} command(s) → {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
