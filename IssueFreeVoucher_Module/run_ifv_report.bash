#!/usr/bin/env bash
# One-click: visible paced steps → HTML report → Google Chrome
set -uo pipefail
CMS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../scripts/one_click_lib.sh
source "$CMS_ROOT/scripts/one_click_lib.sh"

one_click_setup "KS-CMS-IFV-001_issue_free_vouchers.html" "Kskin CMS — Issue Free Vouchers (Selenium)" || { one_click_finish 1; exit 1; }
export ONE_CLICK_KEEP_OPEN=1
one_click_run_python - <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.cms_auth import get_driver, quit_driver
from KskinCMS.report_runner_util import run_paced_steps
from KskinCMS.IssueFreeVoucher_Module.IFV import (
    open_browser, ifv_search_and_filter, rows_per_page_actions, add_new_ifv,
    check_created_ifv_value,
)
import os
OUT = os.environ["CMS_REPORT_HTML"]
driver = get_driver()
r = StepReporter()
r.init(
    test_case_id="KS-CMS-IFV-001",
    test_name="Issue Free Vouchers — Selenium regression",
    subtitle="Staging: search, filter, rows, create+publish, view-verify",
    environment=[
        ("Test Case ID", "KS-CMS-IFV-001"),
        ("Module", "Issue Free Vouchers"),
        ("URL", "https://staging-cms.kskinfacial.com/account/customer-management/issue-free-vouchers"),
        ("Platform", "Web / Selenium / Chrome"),
        ("Screenshots", "Live capture per step"),
    ],
    driver=driver,
)
cases = [
    (1, "Open browser + navigate to IFV", "Login + listing", open_browser),
    (2, "Search + type filter", "Matched/unmatched + $ off", ifv_search_and_filter),
    (3, "Rows per page + pagination", "Change page size", rows_per_page_actions),
    (4, "Create + publish QA IFV", "Form publish + listed", add_new_ifv),
    (5, "View created IFV", "All create fields shown correctly", check_created_ifv_value),
]
raise SystemExit(run_paced_steps(r, cases, quit_driver, OUT))
PY
STATUS=$?
one_click_finish "$STATUS"
exit "$STATUS"
