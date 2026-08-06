#!/usr/bin/env python3
"""Non-interactive Fee Management Playwright runner (cloud / CI friendly)."""
from __future__ import annotations

import os
import sys

OUT = os.environ.get(
    "FEE_REPORT_HTML",
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "reports", "KS-CMS-FEE-MGMT-001.html")
    ),
)

from helpers.step_report import StepReporter
from KskinCMS.playwright_auth import get_page, quit_page, PlaywrightShotAdapter
from KskinCMS.FeeManagement_Module.FeeManagement import (
    open_browser,
    fee_listing_asserts,
    fee_view_detail,
    fee_edit_default_restore,
    fee_override_outlet_restore,
    fee_detail_rows_per_page,
)


def main() -> int:
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    page = get_page()
    r = StepReporter()
    r.init(
        test_case_id="KS-CMS-FEE-MGMT-001",
        test_name="Fee Management — Playwright regression",
        subtitle="Staging: listing, view detail, edit default + outlet override (restore), rows/page",
        environment=[
            ("Test Case ID", "KS-CMS-FEE-MGMT-001"),
            ("Module", "Fee Management"),
            (
                "URL",
                "https://staging-cms.kskinfacial.com/account/franchise-management/fee-management",
            ),
            ("Platform", "Web / Playwright / Chromium"),
            ("Screenshots", "Live capture per step"),
            ("Actions", "View + Edit default % + Override outlet % (always restore)"),
        ],
        driver=PlaywrightShotAdapter(page),
    )
    cases = [
        (1, "Open Fee Management", "Login + listing", lambda: open_browser(page)),
        (2, "Listing fee types + eye", "4 fees + view actions", lambda: fee_listing_asserts(page)),
        (3, "View Platform Fee detail", "Default % + outlet table", lambda: fee_view_detail(page)),
        (4, "Edit default % + restore", "Save temp then restore", lambda: fee_edit_default_restore(page)),
        (5, "Outlet override + restore", "QA outlet % round-trip", lambda: fee_override_outlet_restore(page)),
        (6, "Detail rows/page", "Change page size", lambda: fee_detail_rows_per_page(page)),
    ]
    failed = False
    for num, title, expected, fn in cases:
        try:
            fn()
            r.record_step(num, title, expected, "OK — step completed", "pass")
            print(f"[PASS] Step {num}")
        except Exception as e:
            r.record_step(num, title, expected, f"FAIL: {e}", "fail")
            print(f"[FAIL] Step {num}: {e}")
            failed = True
            break
    r.emit(OUT)
    print("REPORT:", OUT)
    quit_page()
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
