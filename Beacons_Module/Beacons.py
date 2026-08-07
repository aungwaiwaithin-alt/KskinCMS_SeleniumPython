"""Beacons module — Playwright regression (actions-first).

Staging `/account/outlet-management/beacons` is a **view-only listing**:
  - Search: Find by outlet or beacon ID
  - Columns: ASSIGNED OUTLET | BEACON ID | BATTERY LEVEL | LAST UPDATED
  - Rows per page / pagination
  - No Add / Edit / Duplicate / Status actions on staging
"""
from __future__ import annotations

import time

from playwright.sync_api import Page

from KskinCMS.cms_config import MODULE_URLS
from KskinCMS.playwright_auth import open_module, search_listing


def open_browser(page: Page) -> None:
    open_module(page, MODULE_URLS["beacons"], wait_selector='input[name="code"]')
    page.wait_for_selector("table tbody tr", timeout=30000)
    time.sleep(0.5)
    print("Test 1 : Open browser + Beacons listing OK")


def beacons_listing_asserts(page: Page) -> None:
    page.wait_for_selector("table tbody tr", timeout=30000)
    body = page.inner_text("body")
    # Headers may be separated by tabs in accessibility text
    for col in ("ASSIGNED OUTLET", "BEACON ID", "BATTERY LEVEL", "LAST UPDATED"):
        if col not in body:
            ths = " | ".join(page.locator("table thead th").all_text_contents())
            raise AssertionError(
                f"Beacons listing FAILED: missing column '{col}' (ths={ths!r}) "
                "(report to dev / Asana)"
            )
    rows = page.locator("table tbody tr")
    if rows.count() < 1:
        raise AssertionError(
            "Beacons listing FAILED: no rows (report to dev / Asana)"
        )
    # No create/edit actions on staging
    if page.get_by_role("button", name="Add new beacon").count() > 0:
        raise AssertionError(
            "Beacons listing unexpected: Add button appeared — revisit automation "
            "(report to QA)"
        )
    print(f"Test 2 : Listing OK — {rows.count()} rows, columns present (view-only)")


def beacons_search_and_filter(page: Page) -> None:
    open_module(page, MODULE_URLS["beacons"], wait_selector='input[name="code"]')
    page.wait_for_selector("table tbody tr", timeout=30000)
    rows = page.locator("table tbody tr")
    if rows.count() < 1:
        raise AssertionError("Beacons search FAILED: empty listing")

    first = (rows.nth(0).inner_text() or "").strip()
    # Prefer beacon ID token (2nd column-ish) — often like 14jN08FA
    cells = rows.nth(0).locator("td")
    beacon_id = ""
    outlet = ""
    if cells.count() >= 2:
        outlet = (cells.nth(0).inner_text() or "").strip().split("\n")[0].strip()
        beacon_id = (cells.nth(1).inner_text() or "").strip().split("\n")[0].strip()
    query = beacon_id or outlet
    if not query or len(query) < 2:
        raise AssertionError(
            f"Beacons search FAILED: no usable outlet/beacon from row {first!r} "
            "(report to dev / Asana)"
        )

    search_listing(page, query)
    time.sleep(0.5)
    matched = page.locator("table tbody tr")
    if matched.count() < 1:
        raise AssertionError(
            f"Beacons matched search FAILED: no rows for '{query}' "
            "(report to dev / Asana)"
        )
    hit = matched.nth(0).inner_text() or ""
    if query not in hit:
        raise AssertionError(
            f"Beacons matched search FAILED: expected '{query}' in {hit!r} "
            "(report to dev / Asana)"
        )
    print(f"Test 3 : Matched search OK ({query})")

    page.goto(MODULE_URLS["beacons"], wait_until="domcontentloaded")
    page.wait_for_selector('input[name="code"]')
    time.sleep(1)
    search_listing(page, "NoSuchBeaconZZZ999")
    time.sleep(1)
    body = page.inner_text("body")
    empty_rows = page.locator("table tbody tr")
    empty_ok = (
        empty_rows.count() == 0
        or "no result" in body.lower()
        or "no data" in body.lower()
        or "no beacon" in body.lower()
        or "of 0 items" in body.lower()
    )
    if not empty_ok:
        # some UIs keep a placeholder row
        texts = [empty_rows.nth(i).inner_text() for i in range(min(empty_rows.count(), 3))]
        if any("NoSuchBeaconZZZ999" in t for t in texts):
            raise AssertionError(
                "Beacons unmatched search FAILED: bogus query matched "
                "(report to dev / Asana)"
            )
        if empty_rows.count() > 0 and "Displaying" in body and "of 0" not in body:
            # if still showing all 6 items, search didn't filter
            if "of 6 items" in body or empty_rows.count() >= 6:
                raise AssertionError(
                    f"Beacons unmatched search FAILED: still showing rows {texts!r} "
                    "(report to dev / Asana)"
                )
    print("Test 4 : Unmatched search empty/filtered OK")


def beacons_rows_per_page(page: Page) -> None:
    open_module(page, MODULE_URLS["beacons"], wait_selector='input[name="code"]')
    page.wait_for_selector("table tbody tr", timeout=30000)
    time.sleep(0.5)
    # pageSize select near Displaying
    selects = page.locator("select")
    target = None
    for i in range(selects.count()):
        s = selects.nth(i)
        opts = s.locator("option").all_text_contents()
        if "10" in opts and "50" in opts:
            target = s
            break
    if target is None:
        n = page.locator("table tbody tr").count()
        print(f"Test 5 : Rows per page N/A ({n} rows)")
        return
    target.select_option("10")
    time.sleep(1)
    target.select_option("20")
    time.sleep(1)
    # restore small page
    vals = target.locator("option").evaluate_all(
        "els => els.map(e => e.value)"
    )
    if "6" in vals:
        target.select_option("6")
    else:
        target.select_option("10")
    time.sleep(1)
    print("Test 5 : Rows per page checked")
