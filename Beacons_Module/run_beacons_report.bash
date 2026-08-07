#!/usr/bin/env bash
# One-click: visible paced steps → HTML report → Google Chrome
set -uo pipefail
CMS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../scripts/one_click_lib.sh
source "$CMS_ROOT/scripts/one_click_lib.sh"

one_click_setup "KS-CMS-BEACONS-001_beacons.html" "Kskin CMS — Beacons (Playwright)" || { one_click_finish 1; exit 1; }
export ONE_CLICK_KEEP_OPEN=1
one_click_run_python - <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.playwright_auth import get_page, quit_page, PlaywrightShotAdapter
from KskinCMS.report_runner_util import run_paced_steps
from KskinCMS.Beacons_Module.Beacons import (
    open_browser, beacons_listing_asserts, beacons_search_and_filter, beacons_rows_per_page,
)
import os
OUT = os.environ["CMS_REPORT_HTML"]
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
    ],
    driver=PlaywrightShotAdapter(page),
)
cases = [
    (1, "Open browser + navigate to Beacons", "Login + listing", lambda: open_browser(page)),
    (2, "Listing columns + rows", "Headers + ≥1 row; no Add button", lambda: beacons_listing_asserts(page)),
    (3, "Search matched + unmatched", "Beacon/outlet filter works", lambda: beacons_search_and_filter(page)),
    (4, "Rows per page", "Change page size or N/A", lambda: beacons_rows_per_page(page)),
]
raise SystemExit(run_paced_steps(r, cases, quit_page, OUT))
PY
STATUS=$?
one_click_finish "$STATUS"
exit "$STATUS"
