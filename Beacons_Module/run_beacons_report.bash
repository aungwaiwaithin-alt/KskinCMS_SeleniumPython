#!/usr/bin/env bash
set -euo pipefail
AQUA="$HOME/AquaProjects"
REPORT_HTML="$HOME/kskin-web(cms)-automation/reports/KS-CMS-BEACONS-001_beacons.html"
export PATH="/Library/Frameworks/Python.framework/Versions/3.8/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"
export PYTHONPATH="$AQUA:$AQUA/MCP_Appium_Server/python"
# Playwright browsers may live under sandbox cache from install — prefer default user cache
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-0}"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3.8 || command -v python3)}"
mkdir -p "$(dirname "$REPORT_HTML")"
cd "$AQUA"
echo "========================================"
echo "  Kskin CMS — Beacons (Playwright)"
echo "  Python: $PYTHON_BIN"
echo "========================================"
"$PYTHON_BIN" <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.playwright_auth import get_page, quit_page, PlaywrightShotAdapter
from KskinCMS.Beacons_Module.Beacons import (
    open_browser, beacons_listing_asserts, beacons_search_and_filter, beacons_rows_per_page,
)
OUT = "/Users/aungwaiwaithin/kskin-web(cms)-automation/reports/KS-CMS-BEACONS-001_beacons.html"
page = get_page()
r = StepReporter()
r.init(
    test_case_id="KS-CMS-BEACONS-001",
    test_name="Beacons — Playwright regression",
    subtitle="Staging: view-only listing — open, columns, search, rows/page",
    environment=[
        ("Test Case ID", "KS-CMS-BEACONS-001"),
        ("Module", "Beacons"),
        ("URL", "https://staging-cms.kskinfacial.com/account/outlet-management/beacons"),
        ("Platform", "Web / Playwright / Chromium"),
        ("Screenshots", "Live capture per step"),
        ("Actions", "View-only — no Add/Edit/Status/Duplicate on staging"),
    ],
    driver=PlaywrightShotAdapter(page),
)
cases = [
    (1, "Open browser + navigate to Beacons", "Login + listing", lambda: open_browser(page)),
    (2, "Listing columns + rows", "Headers + ≥1 row; no Add button", lambda: beacons_listing_asserts(page)),
    (3, "Search matched + unmatched", "Beacon/outlet filter works", lambda: beacons_search_and_filter(page)),
    (4, "Rows per page", "Change page size or N/A", lambda: beacons_rows_per_page(page)),
]
failed = False
for num, title, expected, fn in cases:
    try:
        fn(); r.record_step(num, title, expected, "OK — step completed", "pass"); print(f"[PASS] Step {num}")
    except Exception as e:
        r.record_step(num, title, expected, f"FAIL: {e}", "fail"); print(f"[FAIL] Step {num}: {e}"); failed = True; break
r.emit(OUT); print("REPORT:", OUT); quit_page()
raise SystemExit(1 if failed else 0)
PY
STATUS=$?
open "$REPORT_HTML" || true
read -n 1 -s -p "Press any key to close..." || true
exit "$STATUS"
