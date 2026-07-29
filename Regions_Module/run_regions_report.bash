#!/usr/bin/env bash
set -euo pipefail
AQUA="$HOME/AquaProjects"
REPORT_HTML="$HOME/kskin-web(cms)-automation/reports/KS-CMS-REGIONS-001_regions.html"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
export PYTHONPATH="$AQUA:$AQUA/MCP_Appium_Server/python"
mkdir -p "$(dirname "$REPORT_HTML")"
cd "$AQUA"
echo "========================================"
echo "  Kskin CMS — Regions"
echo "========================================"
python3 <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.cms_auth import get_driver, quit_driver
from KskinCMS.Regions_Module.Regions import (
    open_browser, region_searching, create_new_region, update_old_region,
)
OUT = "/Users/aungwaiwaithin/kskin-web(cms)-automation/reports/KS-CMS-REGIONS-001_regions.html"
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
failed = False
for num, title, expected, fn in cases:
    try:
        fn(); r.record_step(num, title, expected, "OK — step completed", "pass"); print(f"[PASS] Step {num}")
    except Exception as e:
        r.record_step(num, title, expected, f"FAIL: {e}", "fail"); print(f"[FAIL] Step {num}: {e}"); failed = True; break
r.emit(OUT); print("REPORT:", OUT); quit_driver()
raise SystemExit(1 if failed else 0)
PY
STATUS=$?
open "$REPORT_HTML" || true
read -n 1 -s -p "Press any key to close..." || true
exit "$STATUS"
