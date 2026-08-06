#!/usr/bin/env bash
set -euo pipefail
AQUA="$HOME/AquaProjects"
REPORT_HTML="$HOME/kskin-web(cms)-automation/reports/KS-CMS-GIFTCARD-001_gift_card.html"
export PATH="/Library/Frameworks/Python.framework/Versions/3.8/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"
export PYTHONPATH="$AQUA:$AQUA/MCP_Appium_Server/python"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3.8 || command -v python3)}"
mkdir -p "$(dirname "$REPORT_HTML")"
cd "$AQUA"
echo "========================================"
echo "  Kskin CMS — Gift Card"
echo "  Python: $PYTHON_BIN"
echo "========================================"
"$PYTHON_BIN" <<'PY'
from helpers.step_report import StepReporter
from KskinCMS.cms_auth import get_driver, quit_driver
from KskinCMS.GiftCard_Module.GiftCard import (
    open_browser, gift_card_view_page, open_edit_form,
    gift_card_required_validations, update_gift_card,
    listing_active_inactive_action, listing_inactive_active_action,
)
OUT = "/Users/aungwaiwaithin/kskin-web(cms)-automation/reports/KS-CMS-GIFTCARD-001_gift_card.html"
driver = get_driver()
r = StepReporter()
r.init(
    test_case_id="KS-CMS-GIFTCARD-001",
    test_name="Gift Card — Selenium regression",
    subtitle="Staging: view, validations, full field update+restore, ACTIVE↔INACTIVE",
    environment=[
        ("Test Case ID", "KS-CMS-GIFTCARD-001"),
        ("Module", "Gift Card"),
        ("URL", "https://staging-cms.kskinfacial.com/account/inventory/gift-card"),
        ("Platform", "Web / Selenium / Chrome"),
        ("Screenshots", "Live capture per step"),
        ("Actions", "Edit; More actions status; Publish Changes"),
        ("Validations", "Required desc/T&C/design/amount/expired + amount > 0"),
        ("Note", "Singleton — no Duplicate/create; restore fields + ACTIVE after run"),
    ],
    driver=driver,
)
cases = [
    (1, "Open browser + navigate to Gift Card", "Login + view page", open_browser),
    (2, "View page asserts", "ACTIVE + amounts + description + Edit", gift_card_view_page),
    (3, "Open Edit form (hydrated)", "Publish + textareas + designs + amounts", open_edit_form),
    (4, "Required + validation messages", "User-facing errs; Publish disabled", gift_card_required_validations),
    (5, "Update all fields + Publish + restore", "View/edit verify then restore", update_gift_card),
    (6, "ACTIVE → INACTIVE", "More actions + Yes, set as inactive", listing_active_inactive_action),
    (7, "INACTIVE → ACTIVE", "More actions + Yes, set as active", listing_inactive_active_action),
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
