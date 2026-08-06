#!/usr/bin/env bash
set -euo pipefail
AQUA="$HOME/AquaProjects"
REPORT_HTML="$HOME/kskin-web(cms)-automation/reports/KS-CMS-FRANCHISEE-REPORTS-001.html"
export PATH="/Library/Frameworks/Python.framework/Versions/3.8/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"
export PYTHONPATH="$AQUA:$AQUA/MCP_Appium_Server/python"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3.8 || command -v python3)}"
mkdir -p "$(dirname "$REPORT_HTML")"
cd "$AQUA"
echo "========================================"
echo "  Kskin CMS — Franchisee Reports (Playwright)"
echo "  Note: Sales Overview may wait up to 5 min"
echo "========================================"
"$PYTHON_BIN" <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.playwright_auth import get_page, quit_page, PlaywrightShotAdapter
from KskinCMS.FranchiseeReports_Module.FranchiseeReports import (
    open_browser,
    reports_sales_overview,
    reports_filters,
    reports_statements_listing,
    reports_statements_search,
    reports_statements_status_filter,
    reports_statements_date_filter,
    reports_statements_export_csv,
    reports_statements_kebab_and_invoice,
    reports_statements_rows_per_page,
)
OUT = "/Users/aungwaiwaithin/kskin-web(cms)-automation/reports/KS-CMS-FRANCHISEE-REPORTS-001.html"
page = get_page()
r = StepReporter()
r.init(
    test_case_id="KS-CMS-FRANCHISEE-REPORTS-001",
    test_name="Franchisee Reports — Playwright regression",
    subtitle="Staging: Sales Overview hydrate (≤5m) + full Franchise Statements actions",
    environment=[
        ("Test Case ID", "KS-CMS-FRANCHISEE-REPORTS-001"),
        ("Module", "Franchisee Reports"),
        ("URL", "https://staging-cms.kskinfacial.com/account/franchise-management/franchisee-reports"),
        ("Platform", "Web / Playwright / Chromium"),
        ("Screenshots", "Live capture per step"),
        ("Actions", "Overview wait + Statements search/filters/export/invoice (no Send)"),
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
