#!/usr/bin/env bash
# One-click: visible paced steps → HTML report → Google Chrome
set -uo pipefail
CMS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../scripts/one_click_lib.sh
source "$CMS_ROOT/scripts/one_click_lib.sh"

one_click_setup "KS-CMS-FRANCHISEE-REPORTS-001.html" "Kskin CMS — Franchisee Reports (Playwright)" || { one_click_finish 1; exit 1; }
export ONE_CLICK_KEEP_OPEN=1
one_click_run_python - <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.playwright_auth import get_page, quit_page, PlaywrightShotAdapter
from KskinCMS.report_runner_util import run_paced_steps
from KskinCMS.FranchiseeReports_Module.FranchiseeReports import (
    open_browser, reports_sales_overview, reports_filters, reports_statements_listing,
    reports_statements_search, reports_statements_status_filter, reports_statements_date_filter,
    reports_statements_export_csv, reports_statements_kebab_and_invoice, reports_statements_rows_per_page,
)
import os
OUT = os.environ["CMS_REPORT_HTML"]
page = get_page()
r = StepReporter()
r.init(
    test_case_id="KS-CMS-FRANCHISEE-REPORTS-001",
    test_name="Franchisee Reports — Playwright regression",
    subtitle="Staging: Sales Overview + Franchise Statements",
    environment=[
        ("Test Case ID", "KS-CMS-FRANCHISEE-REPORTS-001"),
        ("Module", "Franchisee Reports"),
        ("URL", "https://staging-cms.kskinfacial.com/account/franchise-management/franchisee-reports"),
        ("Platform", "Web / Playwright / Chromium"),
        ("Screenshots", "Live capture per step"),
    ],
    driver=PlaywrightShotAdapter(page),
)
cases = [
    (1, "Open Franchisee Reports", "Login + Franchise Reports", lambda: open_browser(page)),
    (2, "Sales Overview hydrate", "Total Sales/Royalties within 5 min", lambda: reports_sales_overview(page)),
    (3, "Franchisee + year filters", "Filter applies on Overview", lambda: reports_filters(page)),
    (4, "Statements listing + Export btn", "Columns + rows + Export CSV", lambda: reports_statements_listing(page)),
    (5, "Statements search", "Matched + unmatched", lambda: reports_statements_search(page)),
    (6, "Statements status filter", "Pending / Sent / All", lambda: reports_statements_status_filter(page)),
    (7, "Statements date filter", "Calendar Today + Okay", lambda: reports_statements_date_filter(page)),
    (8, "Export CSV download", "CSV download starts", lambda: reports_statements_export_csv(page)),
    (9, "Kebab + invoice edit/restore", "View/Edit; txn/remark round-trip; no Send", lambda: reports_statements_kebab_and_invoice(page)),
    (10, "Statements rows/page", "Page size + pagination", lambda: reports_statements_rows_per_page(page)),
]
raise SystemExit(run_paced_steps(r, cases, quit_page, OUT))
PY
STATUS=$?
one_click_finish "$STATUS"
exit "$STATUS"
