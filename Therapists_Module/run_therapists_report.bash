#!/usr/bin/env bash
# One-click: visible paced steps → HTML report → Google Chrome
set -uo pipefail
CMS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../scripts/one_click_lib.sh
source "$CMS_ROOT/scripts/one_click_lib.sh"

one_click_setup "KS-CMS-THERAPISTS-001_therapists.html" "Kskin CMS — Therapists (Selenium)" || { one_click_finish 1; exit 1; }
export ONE_CLICK_KEEP_OPEN=1
one_click_run_python - <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.cms_auth import get_driver, quit_driver
from KskinCMS.report_runner_util import run_paced_steps
from KskinCMS.Therapists_Module.Therapist import (
    open_browser, therapist_search_and_filter, add_new_therapist,
    listing_active_inactive_action, listing_inactive_active_action,
    rows_per_page_actions, check_created_therapist_value, update_old_therapist,
)
import os
OUT = os.environ["CMS_REPORT_HTML"]
driver = get_driver()
r = StepReporter()
r.init(
    test_case_id="KS-CMS-THERAPISTS-001",
    test_name="Therapists — Selenium regression",
    subtitle="Staging: search, create QA, ACTIVE↔INACTIVE, rows, view, edit",
    environment=[
        ("Test Case ID", "KS-CMS-THERAPISTS-001"),
        ("Module", "Therapists"),
        ("URL", "https://staging-cms.kskinfacial.com/account/therapist-management/therapists"),
        ("Platform", "Web / Selenium / Chrome"),
        ("Screenshots", "Live capture per step"),
    ],
    driver=driver,
)
cases = [
    (1, "Open browser + navigate to Therapists", "Login + listing", open_browser),
    (2, "Search + status filter", "Matched/unmatched + Active", therapist_search_and_filter),
    (3, "Create new QA therapist", "Form create + listed", add_new_therapist),
    (4, "ACTIVE → INACTIVE on QA therapist", "Toggle QA item only", listing_active_inactive_action),
    (5, "INACTIVE → ACTIVE on same QA therapist", "Toggle QA item only", listing_inactive_active_action),
    (6, "Rows per page + pagination", "Change page size", rows_per_page_actions),
    (7, "View created therapist", "Form values readable", check_created_therapist_value),
    (8, "Edit therapist", "Rename searchable", update_old_therapist),
]
raise SystemExit(run_paced_steps(r, cases, quit_driver, OUT))
PY
STATUS=$?
one_click_finish "$STATUS"
exit $?
