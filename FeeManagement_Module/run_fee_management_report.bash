#!/usr/bin/env bash
# One-click: visible paced steps → HTML report → Google Chrome
set -uo pipefail
CMS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../scripts/one_click_lib.sh
source "$CMS_ROOT/scripts/one_click_lib.sh"

one_click_setup "KS-CMS-FEE-MGMT-001.html" "Kskin CMS — Fee Management (Playwright)" || { one_click_finish 1; exit 1; }
export ONE_CLICK_KEEP_OPEN=1
one_click_run_python - <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.playwright_auth import get_page, quit_page, PlaywrightShotAdapter
from KskinCMS.report_runner_util import run_paced_steps
from KskinCMS.FeeManagement_Module.FeeManagement import (
    open_browser, fee_listing_asserts, fee_view_detail,
    fee_edit_default_required_validation, fee_edit_default_restore,
    fee_edit_minimum_fee_restore, fee_override_outlet_restore, fee_detail_rows_per_page,
)
import os
OUT = os.environ["CMS_REPORT_HTML"]
page = get_page()
r = StepReporter()
r.init(
    test_case_id="KS-CMS-FEE-MGMT-001",
    test_name="Fee Management — Playwright regression",
    subtitle="Staging: listing, view, empty required validation, edit default % + Minimum Fee + outlet override (restore), rows/page",
    environment=[
        ("Test Case ID", "KS-CMS-FEE-MGMT-001"),
        ("Module", "Fee Management"),
        ("URL", "https://staging-cms.kskinfacial.com/account/franchise-management/fee-management"),
        ("Platform", "Web / Playwright / Chromium"),
        ("Screenshots", "Live capture per step"),
    ],
    driver=PlaywrightShotAdapter(page),
)
cases = [
    (1, "Open Fee Management", "Login + listing", lambda: open_browser(page)),
    (2, "Listing fee types + eye", "4 fees + view actions", lambda: fee_listing_asserts(page)),
    (3, "View Platform Fee detail", "Default % + outlet table", lambda: fee_view_detail(page)),
    (4, "Edit default required validation", "Empty Percentage / Minimum Fee / both", lambda: fee_edit_default_required_validation(page)),
    (5, "Edit default % + restore", "Save temp then restore", lambda: fee_edit_default_restore(page)),
    (6, "Edit Minimum Fee + restore", "Dialog S$ min fee round-trip", lambda: fee_edit_minimum_fee_restore(page)),
    (7, "Outlet override + restore", "QA outlet % round-trip", lambda: fee_override_outlet_restore(page)),
    (8, "Detail rows/page", "Change page size", lambda: fee_detail_rows_per_page(page)),
]
raise SystemExit(run_paced_steps(r, cases, quit_page, OUT))
PY
STATUS=$?
one_click_finish "$STATUS"
exit "$STATUS"
