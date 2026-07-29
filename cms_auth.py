"""Shared login + desktop window helpers for Kskin CMS Selenium modules."""

import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from KskinCMS.cms_config import (
    LOGIN_URL,
    CMS_EMAIL,
    CMS_PASSWORD,
    CMS_OTP_DIGIT,
    VIEWPORT_WIDTH,
    VIEWPORT_HEIGHT,
)

# One Chrome for the whole regression process (reuse across modules when possible)
_SHARED_DRIVER = None


def chrome_options_desktop():
    opts = Options()
    opts.add_argument(f"--window-size={VIEWPORT_WIDTH},{VIEWPORT_HEIGHT}")
    # Do not use --start-maximized on macOS — it often yields ~1440×750 logical
    return opts


def get_driver():
    """Return a single shared Chrome instance. Do NOT create Chrome in each Helper."""
    global _SHARED_DRIVER
    if _SHARED_DRIVER is not None:
        try:
            _ = _SHARED_DRIVER.current_url  # dead session check
            return _SHARED_DRIVER
        except Exception:
            print("Shared Chrome session dead — starting a new one.")
            try:
                _SHARED_DRIVER.quit()
            except Exception:
                pass
            _SHARED_DRIVER = None

    _SHARED_DRIVER = webdriver.Chrome(options=chrome_options_desktop())
    ensure_desktop(_SHARED_DRIVER)
    print("Shared Chrome started (one browser for this run).")
    return _SHARED_DRIVER


def quit_driver():
    global _SHARED_DRIVER
    if _SHARED_DRIVER is not None:
        try:
            _SHARED_DRIVER.quit()
        except Exception:
            pass
        _SHARED_DRIVER = None
        print("Shared Chrome closed.")


def ensure_desktop(driver):
    """Force desktop viewport. Avoid maximize_window on macOS — it shrinks to screen."""
    for _ in range(2):
        try:
            driver.set_window_rect(x=0, y=0, width=VIEWPORT_WIDTH, height=VIEWPORT_HEIGHT)
        except Exception:
            try:
                driver.set_window_size(VIEWPORT_WIDTH, VIEWPORT_HEIGHT)
            except Exception:
                pass
        try:
            size = driver.get_window_size()
            if size.get("width", 0) >= 1600 and size.get("height", 0) >= 900:
                return
        except Exception:
            return


def _is_authenticated(url: str) -> bool:
    u = url or ""
    return "/account/" in u and "/login" not in u and "/otp-login" not in u


def login_cms(driver, email=CMS_EMAIL, password=CMS_PASSWORD, otp_digit=CMS_OTP_DIGIT):
    """Login + OTP once. Skips if already on an /account/ page."""
    ensure_desktop(driver)
    if _is_authenticated(driver.current_url or ""):
        print(f"Already logged in — skip login. ({driver.current_url})")
        return

    driver.get(LOGIN_URL)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "email")))
    ensure_desktop(driver)
    time.sleep(1.5)  # hydration — avoid native GET submit before JS binds

    email_el = driver.find_element(By.NAME, "email")
    email_el.click()
    email_el.send_keys(Keys.COMMAND, "a")
    email_el.send_keys(Keys.BACKSPACE)
    email_el.send_keys(email)

    pwd_el = driver.find_element(By.NAME, "password")
    pwd_el.click()
    pwd_el.send_keys(Keys.COMMAND, "a")
    pwd_el.send_keys(Keys.BACKSPACE)
    pwd_el.send_keys(password)
    time.sleep(0.5)

    login_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Login')]"))
    )
    login_btn.click()

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "otp-field-0")))
    time.sleep(0.5)

    # React OTP inputs ignore Selenium send_keys — set via native value setter + events
    driver.execute_script(
        """
        const digit = arguments[0];
        for (let i = 0; i < 6; i++) {
          const input = document.getElementById('otp-field-' + i);
          const setter = Object.getOwnPropertyDescriptor(
            window.HTMLInputElement.prototype, 'value'
          ).set;
          setter.call(input, digit);
          input.dispatchEvent(new Event('input', { bubbles: true }));
          input.dispatchEvent(new Event('change', { bubbles: true }));
          input.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true, key: digit }));
        }
        """,
        otp_digit,
    )

    WebDriverWait(driver, 30).until(
        lambda d: _is_authenticated(d.current_url or "")
    )
    ensure_desktop(driver)
    print(f"CMS login + OTP completed. Landed: {driver.current_url}")


def open_module(driver, module_url, wait_css=None):
    """Login only if needed, then open module URL (same browser)."""
    login_cms(driver)
    ensure_desktop(driver)
    driver.get(module_url)
    ensure_desktop(driver)

    WebDriverWait(driver, 30).until(
        lambda d: _is_authenticated(d.current_url or "")
        and module_url.rstrip("/").split("/")[-1] in (d.current_url or "")
    )

    if wait_css:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, wait_css))
        )
    else:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "h1, table, input[name='code'], button")
            )
        )

    time.sleep(1)
    ensure_desktop(driver)
    print(f"Opened module: {driver.current_url}")


def js_fill(driver, element, value):
    """Fill React-controlled input/textarea reliably."""
    tag = (element.tag_name or "input").lower()
    proto = "HTMLTextAreaElement" if tag == "textarea" else "HTMLInputElement"
    driver.execute_script(
        f"""
        const input = arguments[0];
        const value = arguments[1];
        const setter = Object.getOwnPropertyDescriptor(window.{proto}.prototype, 'value').set;
        setter.call(input, '');
        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
        setter.call(input, value);
        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
        """,
        element,
        value,
    )


def search_listing(driver, query):
    """Type into listing search (name=code)."""
    el = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "code"))
    )
    js_fill(driver, el, query)
    time.sleep(2)


def toggle_row_status(driver, item_name, make_inactive=True):
    """
    Preferred status-test flow:
    search the QA-created item → open row menu → Set as inactive/active → confirm.
    """
    from selenium.webdriver.common.action_chains import ActionChains

    search_listing(driver, item_name.split("\n")[0].strip())
    time.sleep(1)
    safe_name = item_name.split("\n")[0].strip().replace("'", "")
    row = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.XPATH, f"//table//tbody/tr[contains(., '{safe_name}')]")
        )
    )
    btn = row.find_element(By.CSS_SELECTOR, ".actions-column button, td:last-child button")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
    time.sleep(0.2)

    def _menu_open():
        return bool(
            driver.find_elements(
                By.XPATH,
                "//*[@role='menuitem' and (contains(.,'Set as inactive') or contains(.,'Set as active')"
                " or contains(.,'Inactive') or contains(.,'Active') or contains(.,'Duplicate')"
                " or contains(.,'Edit') or contains(.,'Delete'))]",
            )
        )

    def _click_menu_btn():
        # Radix DropdownMenu needs a full pointer event sequence; plain click often no-ops
        driver.execute_script(
            """
            const el = arguments[0];
            const r = el.getBoundingClientRect();
            const x = r.left + r.width / 2, y = r.top + r.height / 2;
            el.focus();
            for (const type of [
              'pointerover','pointerenter','pointerdown','mousedown',
              'pointerup','mouseup','click'
            ]) {
              const C = type.startsWith('pointer') ? PointerEvent : MouseEvent;
              el.dispatchEvent(new C(type, {
                bubbles: true, cancelable: true, view: window,
                clientX: x, clientY: y, pointerId: 1, pointerType: 'mouse',
                buttons: type.endsWith('down') ? 1 : 0
              }));
            }
            """,
            btn,
        )

    _click_menu_btn()
    time.sleep(0.8)
    # Only retry if menu did NOT open — a second click often closes Radix menus
    if not _menu_open():
        try:
            ActionChains(driver).move_to_element(btn).pause(0.15).click().perform()
        except Exception:
            pass
        time.sleep(0.8)
    if not _menu_open():
        rect = driver.execute_script(
            "const r=arguments[0].getBoundingClientRect();"
            "return {x:r.left+r.width/2,y:r.top+r.height/2};",
            btn,
        )
        for typ, button, buttons in (
            ("mouseMoved", "none", 0),
            ("mousePressed", "left", 1),
            ("mouseReleased", "left", 0),
        ):
            payload = {"type": typ, "x": rect["x"], "y": rect["y"], "button": button, "buttons": buttons}
            if typ != "mouseMoved":
                payload["clickCount"] = 1
            driver.execute_cdp_cmd("Input.dispatchMouseEvent", payload)
        time.sleep(0.8)

    if make_inactive:
        menu = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//*[@role='menuitem' and (contains(.,'Set as inactive') or contains(.,'Inactive'))]",
                )
            )
        )
        driver.execute_script("arguments[0].click();", menu)
        time.sleep(0.5)
        yes = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//button[contains(.,'Yes, set as inactive') or contains(.,'Yes, update status') or contains(.,'Yes')]",
                )
            )
        )
        driver.execute_script("arguments[0].click();", yes)
        expect = "INACTIVE"
    else:
        menu = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//*[@role='menuitem' and (contains(.,'Set as active') or contains(.,'Active'))]",
                )
            )
        )
        driver.execute_script("arguments[0].click();", menu)
        time.sleep(0.5)
        yes = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//button[contains(.,'Yes, set as active') or contains(.,'Yes, update status') or contains(.,'Yes')]",
                )
            )
        )
        driver.execute_script("arguments[0].click();", yes)
        expect = "ACTIVE"

    time.sleep(3)
    search_listing(driver, safe_name)
    status = driver.find_element(
        By.XPATH, f"//table//tbody/tr[contains(., '{safe_name}')]"
    ).text.upper()
    ok = expect in status
    print(f"Status for '{safe_name}' → want {expect}; row text has it? {ok}")
    return ok


def duplicate_row_as_qa(driver, qa_name, name_field="name", name_col_index=0):
    """
    Create a dedicated QA row for status tests:
    Duplicate first ACTIVE row → set unique name → Create/Save → return qa_name.
    Falls back to returning an existing ACTIVE row name if Duplicate is unavailable.
    """
    time.sleep(1)
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    target = None
    for r in rows:
        txt = (r.text or "").upper()
        if "INACTIVE" in txt:
            continue
        if "ACTIVE" in txt:
            target = r
            break
    if target is None and rows:
        target = rows[0]
    if target is None:
        raise RuntimeError("No listing rows to duplicate for QA status item")

    from selenium.webdriver.common.action_chains import ActionChains

    btn = target.find_element(By.CSS_SELECTOR, ".actions-column button, td:last-child button")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
    try:
        ActionChains(driver).move_to_element(btn).pause(0.2).click().perform()
    except Exception:
        driver.execute_script("arguments[0].click();", btn)
    time.sleep(1)
    if (btn.get_attribute("aria-expanded") or "") != "true":
        try:
            btn.click()
        except Exception:
            driver.execute_script("arguments[0].click();", btn)
        time.sleep(1)
    dups = driver.find_elements(
        By.XPATH, "//*[@role='menuitem' and (contains(.,'Duplicate') or contains(.,'duplicate'))]"
    )
    if not dups:
        # No duplicate action — use that row's name (still search-scoped, not random toggle alone)
        try:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        except Exception:
            pass
        cells = target.find_elements(By.TAG_NAME, "td")
        fallback = cells[name_col_index].text.strip() if cells else target.text.strip().split("\n")[0]
        print(f"No Duplicate menu — will toggle existing row: {fallback}")
        return fallback

    driver.execute_script("arguments[0].click();", dups[0])
    time.sleep(3)

    # On create/edit form: rename to qa_name and submit
    fields = driver.find_elements(By.NAME, name_field)
    if not fields:
        # common alternates
        for alt in ("title", "displayName", "fullName", "productName", "treatmentName", "bundleName"):
            fields = driver.find_elements(By.NAME, alt)
            if fields:
                break
    if fields:
        js_fill(driver, fields[0], qa_name)
        time.sleep(0.5)

    for label in ("Create", "Save", "Update", "Confirm"):
        btns = driver.find_elements(By.XPATH, f"//button[contains(.,'{label}')]")
        if btns:
            driver.execute_script("arguments[0].click();", btns[-1])
            time.sleep(3)
            break

    print(f"QA item ready for status tests: {qa_name}")
    return qa_name
