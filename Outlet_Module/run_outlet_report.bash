#!/usr/bin/env bash
# One-click: visible paced steps → HTML report → Google Chrome
set -uo pipefail
CMS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../scripts/one_click_lib.sh
source "$CMS_ROOT/scripts/one_click_lib.sh"

one_click_setup "KS-CMS-OUTLET-001_outlets.html" "Kskin CMS — Outlets (Selenium)" || { one_click_finish 1; exit 1; }
export ONE_CLICK_KEEP_OPEN=1
one_click_run_python - <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.cms_auth import get_driver, quit_driver
from KskinCMS.report_runner_util import run_paced_steps
from KskinCMS.Outlet_Module.Outlets import (
    open_browser, outlets_search_and_filters, create_new_outlet,
    change_outlet_status_from_listing, check_created_outlet_value, update_old_outlet,
)
import os
OUT = os.environ["CMS_REPORT_HTML"]
driver = get_driver()
r = StepReporter()
r.init(
    test_case_id="KS-CMS-OUTLET-001",
    test_name="Outlets — Selenium regression",
    subtitle="Staging: search/filters, create, ACTIVE↔INACTIVE, view, edit",
    environment=[
        ("Test Case ID", "KS-CMS-OUTLET-001"),
        ("Module", "Outlets"),
        ("URL", "https://staging-cms.kskinfacial.com/account/outlet-management/outlets"),
        ("Platform", "Web / Selenium / Chrome"),
        ("Screenshots", "Live capture per step"),
    ],
    driver=driver,
)
cases = [
    (1, "Open browser + navigate to Outlets", "Login + listing", open_browser),
    (2, "Search + region/status filters", "Matched/unmatched + filters", outlets_search_and_filters),
    (3, "Create new QA outlet (Publish)", "Published QA outlet listed", create_new_outlet),
    (4, "ACTIVE → INACTIVE → ACTIVE on QA outlet", "Toggle QA item only", change_outlet_status_from_listing),
    (5, "View created outlet", "Name/code readable", check_created_outlet_value),
    (6, "Edit outlet name", "Rename searchable", update_old_outlet),
]
raise SystemExit(run_paced_steps(r, cases, quit_driver, OUT))
PY
STATUS=$?
one_click_finish "$STATUS"
exit "$STATUS"
