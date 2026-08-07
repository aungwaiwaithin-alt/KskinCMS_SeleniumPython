#!/usr/bin/env bash
# One-click: visible paced steps → HTML report → Google Chrome
set -uo pipefail
CMS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../scripts/one_click_lib.sh
source "$CMS_ROOT/scripts/one_click_lib.sh"

one_click_setup "KS-CMS-FRANCHISE-001_franchisee_accounts.html" "Kskin CMS — Franchisee Accounts (Selenium)" || { one_click_finish 1; exit 1; }
export ONE_CLICK_KEEP_OPEN=1
one_click_run_python - <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.cms_auth import get_driver, quit_driver
from KskinCMS.report_runner_util import run_paced_steps
from KskinCMS.Franchise_Account_Module.FranchiseAcc import (
    open_browser, franchise_searching, listing_active_inactive_action,
    listing_inactive_active_action, pagination_and_rows_per_page_actions,
    create_new_franchise_account, view_back_created_acc_info, edit_franchise_account,
)
import os
OUT = os.environ["CMS_REPORT_HTML"]
driver = get_driver()
r = StepReporter()
r.init(
    test_case_id="KS-CMS-FRANCHISE-001",
    test_name="Franchisee Accounts — Selenium regression",
    subtitle="Staging CMS: search, ACTIVE↔INACTIVE on QA item, pagination, create, view, edit",
    environment=[
        ("Test Case ID", "KS-CMS-FRANCHISE-001"),
        ("Module", "Franchisee Accounts"),
        ("URL", "https://staging-cms.kskinfacial.com/account/franchise-management/franchisee-accounts"),
        ("Platform", "Web / Selenium / Chrome"),
        ("Screenshots", "Live capture per step"),
    ],
    driver=driver,
)
cases = [
    (1, "Open browser + navigate to Franchisee Accounts", "Login + OTP; listing loads", open_browser),
    (2, "Search — franchise name / email / entity", "Matched rows", franchise_searching),
    (3, "ACTIVE → INACTIVE on new QA franchise", "QA item only", listing_active_inactive_action),
    (4, "INACTIVE → ACTIVE on same QA franchise", "QA item only", listing_inactive_active_action),
    (5, "Rows per page + pagination", "Page size + pagination", pagination_and_rows_per_page_actions),
    (6, "Create new franchise account", "Validations + create", create_new_franchise_account),
    (7, "View created franchise", "Email and name readable", view_back_created_acc_info),
    (8, "Edit franchise account", "Rename searchable", edit_franchise_account),
]
raise SystemExit(run_paced_steps(r, cases, quit_driver, OUT))
PY
STATUS=$?
one_click_finish "$STATUS"
exit "$STATUS"
