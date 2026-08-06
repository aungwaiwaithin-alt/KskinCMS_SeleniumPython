"""Shared Playwright login + session helpers for Kskin CMS (Playwright phase)."""

from __future__ import annotations

import base64
import os
import time
from typing import Optional

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from KskinCMS.cms_config import (
    LOGIN_URL,
    CMS_EMAIL,
    CMS_PASSWORD,
    CMS_OTP_DIGIT,
    VIEWPORT_WIDTH,
    VIEWPORT_HEIGHT,
)

_PW: Optional[Playwright] = None
_BROWSER: Optional[Browser] = None
_CONTEXT: Optional[BrowserContext] = None
_PAGE: Optional[Page] = None


class PlaywrightShotAdapter:
    """Duck-type Selenium driver for StepReporter screenshots."""

    def __init__(self, page: Page):
        self.page = page

    def get_screenshot_as_base64(self) -> str:
        return base64.b64encode(self.page.screenshot(full_page=False)).decode("ascii")


def _is_authenticated(url: str) -> bool:
    u = url or ""
    return "/account/" in u and "/login" not in u and "/otp-login" not in u


def get_page() -> Page:
    """One Chromium + one page for the Playwright module run."""
    global _PW, _BROWSER, _CONTEXT, _PAGE
    if _PAGE is not None:
        try:
            _ = _PAGE.url
            return _PAGE
        except Exception:
            quit_page()

    _PW = sync_playwright().start()
    headless = os.environ.get("PLAYWRIGHT_HEADLESS", "").strip() in ("1", "true", "yes")
    _BROWSER = _PW.chromium.launch(headless=headless)
    _CONTEXT = _BROWSER.new_context(
        viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
    )
    _PAGE = _CONTEXT.new_page()
    print("Playwright Chromium started (one browser for this run).")
    return _PAGE


def quit_page() -> None:
    global _PW, _BROWSER, _CONTEXT, _PAGE
    try:
        if _CONTEXT:
            _CONTEXT.close()
    except Exception:
        pass
    try:
        if _BROWSER:
            _BROWSER.close()
    except Exception:
        pass
    try:
        if _PW:
            _PW.stop()
    except Exception:
        pass
    _PW = _BROWSER = _CONTEXT = _PAGE = None
    print("Playwright Chromium closed.")


def login_cms(
    page: Page,
    email: str = CMS_EMAIL,
    password: str = CMS_PASSWORD,
    otp_digit: str = CMS_OTP_DIGIT,
) -> None:
    if _is_authenticated(page.url or ""):
        print(f"Already logged in — skip login. ({page.url})")
        return

    page.goto(LOGIN_URL, wait_until="domcontentloaded")
    page.wait_for_selector('input[name="email"]', timeout=20000)
    time.sleep(1.0)

    # React controlled inputs — native setters (fill() leaves Login disabled)
    page.evaluate(
        """([email, password]) => {
          const setNative = (el, v) => {
            const setter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype, 'value'
            ).set;
            setter.call(el, v);
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
          };
          setNative(document.querySelector('input[name="email"]'), email);
          setNative(document.querySelector('input[name="password"]'), password);
        }""",
        [email, password],
    )
    page.wait_for_function(
        """() => {
          const b = document.querySelector('button[type="submit"]');
          return !!b && !b.disabled;
        }""",
        timeout=15000,
    )
    page.locator('button[type="submit"]').click()

    page.wait_for_selector("#otp-field-0", timeout=30000)
    time.sleep(0.4)
    # React OTP — native value setter (same as Selenium cms_auth)
    page.evaluate(
        """(digit) => {
          for (let i = 0; i < 6; i++) {
            const input = document.getElementById('otp-field-' + i);
            if (!input) continue;
            const setter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype, 'value'
            ).set;
            setter.call(input, digit);
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
            input.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true, key: digit }));
          }
        }""",
        otp_digit,
    )
    page.wait_for_function(
        """() => {
          const u = location.href || '';
          const onAccount = u.includes('/account/') && !u.includes('/login') && !u.includes('/otp-login');
          const shell = /Outlet Management|Franchise Management|Inventory/i.test(
            document.body ? document.body.innerText : ''
          );
          return onAccount || shell;
        }""",
        timeout=45000,
    )
    # Prefer settling on a real account URL if SPA is mid-transition
    for _ in range(20):
        if _is_authenticated(page.url or ""):
            break
        time.sleep(0.25)
    print(f"CMS login + OTP completed. Landed: {page.url}")


def open_module(page: Page, module_url: str, wait_selector: str = 'input[name="code"]') -> None:
    login_cms(page)
    page.goto(module_url, wait_until="domcontentloaded")
    page.wait_for_function(
        """(frag) => {
          const u = location.href || '';
          return u.includes('/account/') && u.includes(frag);
        }""",
        arg=module_url.rstrip("/").split("/")[-1],
        timeout=30000,
    )
    if wait_selector:
        page.wait_for_selector(wait_selector, timeout=30000)
    time.sleep(1)
    print(f"Opened module: {page.url}")


def search_listing(page: Page, query: str) -> None:
    page.wait_for_selector('input[name="code"]', timeout=15000)
    page.evaluate(
        """(value) => {
          const input = document.querySelector('input[name="code"]');
          const setter = Object.getOwnPropertyDescriptor(
            window.HTMLInputElement.prototype, 'value'
          ).set;
          setter.call(input, '');
          input.dispatchEvent(new Event('input', { bubbles: true }));
          setter.call(input, value);
          input.dispatchEvent(new Event('input', { bubbles: true }));
          input.dispatchEvent(new Event('change', { bubbles: true }));
        }""",
        query,
    )
    time.sleep(2)
