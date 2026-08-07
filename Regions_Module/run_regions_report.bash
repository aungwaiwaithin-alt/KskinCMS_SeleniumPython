#!/usr/bin/env bash
# One-click: visible paced steps → HTML report → Google Chrome
set -uo pipefail
CMS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=../scripts/one_click_lib.sh
source "$CMS_ROOT/scripts/one_click_lib.sh"

one_click_setup "KS-CMS-REGIONS-001_regions.html" "Kskin CMS — Regions (Selenium)" || { one_click_finish 1; exit 1; }
export ONE_CLICK_KEEP_OPEN=1
one_click_run_python - <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.cms_auth import get_driver, quit_driver
from KskinCMS.report_runner_util import run_paced_steps
from KskinCMS.Regions_Module.Regions import (
    open_browser, region_searching, create_new_region, update_old_region,
)
import os
OUT = os.environ["CMS_REPORT_HTML"]
driver = get_driver()
r = StepReporter()
r.init(
    test_case_id="KS-CMS-REGIONS-001",
    test_name="Regions — Selenium regression",
    subtitle="Staging: search, create QA region, edit QA region",
    environment=[
        ("Test Case ID", "KS-CMS-REGIONS-001"),
        ("Module", "Regions"),
        ("URL", "https://staging-cms.kskinfacial.com/account/outlet-management/regions"),
        ("Platform", "Web / Selenium / Chrome"),
        ("Screenshots", "Live capture per step"),
    ],
    driver=driver,
)
cases = [
    (1, "Open browser + navigate to Regions", "Login + listing", open_browser),
    (2, "Search — matched + unmatched", "Matched + empty unmatched", region_searching),
    (3, "Create new QA region", "Dialog cancel + create listed", create_new_region),
    (4, "Edit QA region", "Open Edit dialog, rename, save", update_old_region),
]
raise SystemExit(run_paced_steps(r, cases, quit_driver, OUT))
PY
STATUS=$?
one_click_finish "$STATUS"
exit $?
