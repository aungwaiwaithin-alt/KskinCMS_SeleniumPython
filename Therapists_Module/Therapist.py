import os
import time

from KskinCMS.Therapists_Module.TherapistHelper import *
from KskinCMS.Therapists_Module.TherapistVarPaths import *
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

load_dotenv()

_QA_STATUS_THERAPIST = None
_QA_CREATED_THERAPIST = None  # display name used for view/edit


def open_browser():
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["therapists"], wait_css='input[name="code"]')
    print("Test 1 : Open browser success!")
    print("Test 2 : Navigated to therapists listing successful!")


def therapist_search_and_filter():
    """Matched/unmatched search + Active status filter. Soft-fails → AssertionError."""
    from KskinCMS.cms_auth import search_listing
    from KskinCMS.cms_config import MODULE_URLS

    driver.get(MODULE_URLS["therapists"])
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "code")))
    time.sleep(2)

    first_name = ""
    cells = driver.find_elements(By.CSS_SELECTOR, "table tbody tr:first-child td")
    if cells:
        first_name = (cells[0].text or "").strip().split("\n")[0].strip()
    if not first_name or len(first_name) < 2:
        raise AssertionError(
            "Therapist search FAILED: no usable name on first listing row "
            "(report to dev / Asana)"
        )

    search_listing(driver, first_name)
    time.sleep(1)
    actual = driver.find_element(By.XPATH, "//table//tbody/tr[1]/td[1]").text.strip()
    print(actual)
    if first_name not in actual and actual not in first_name:
        raise AssertionError(
            f"Therapist matched search FAILED: expected '{first_name}', got '{actual}' "
            "(report to dev / Asana)"
        )
    print("Test 3 : Therapist name searching with matched value is successful!")

    driver.get(MODULE_URLS["therapists"])
    time.sleep(2)
    search_listing(driver, "NoSuchTherapistZZZ")
    time.sleep(2)
    body = driver.find_element(By.TAG_NAME, "body").text
    rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
    empty_ok = (
        "No therapists" in body
        or "No therapist" in body
        or "no result" in body.lower()
        or "no data" in body.lower()
        or not rows
    )
    if not empty_ok:
        raise AssertionError(
            "Therapist unmatched search FAILED: expected empty/no-result "
            "(report to dev / Asana)"
        )
    print("Test 4 : Searching with unmatched value can show empty result successfully!!")

    driver.get(MODULE_URLS["therapists"])
    time.sleep(2)

    # Status filter Active — try each combobox, then hidden <select> fallback
    status_ok = False
    combos = driver.find_elements(By.CSS_SELECTOR, "[role=combobox]")
    for combo in combos[:3]:
        try:
            driver.execute_script("arguments[0].click();", combo)
            time.sleep(0.8)
            opt = [
                o
                for o in driver.find_elements(
                    By.XPATH,
                    "//*[@role='option' and (normalize-space()='Active' or contains(.,'Active'))]",
                )
                if o.is_displayed()
            ]
            # Prefer exact Active over Inactive
            exact = [o for o in opt if (o.text or "").strip() == "Active"]
            pick = exact[0] if exact else (opt[0] if opt else None)
            if pick and "Inactive" not in ((pick.text or "")):
                driver.execute_script("arguments[0].click();", pick)
                status_ok = True
                break
            try:
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            except Exception:
                pass
            time.sleep(0.3)
        except Exception:
            continue

    if not status_ok:
        driver.execute_script(
            """
            const selects = document.querySelectorAll('select[aria-hidden="true"]');
            for (const select of selects) {
              const opts = [...select.options].map(o => o.value || o.text);
              if (opts.some(v => String(v).toLowerCase() === 'active')) {
                select.value = [...select.options].find(o =>
                  String(o.value||o.text).toLowerCase() === 'active'
                ).value;
                select.dispatchEvent(new Event('change', { bubbles: true }));
                return true;
              }
            }
            return false;
            """
        )
        time.sleep(2)

    time.sleep(1.5)
    rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
    if not rows:
        raise AssertionError(
            "Therapist status filter Active FAILED: no rows after filter "
            "(report to dev / Asana)"
        )
    status = driver.find_element(By.XPATH, "//table//tbody/tr[1]/td[5]").text.strip().upper()
    print(status)
    if "INACTIVE" in status or status != "ACTIVE":
        raise AssertionError(
            f"Therapist status filter Active FAILED: '{status}' "
            "(report to dev / Asana)"
        )
    print("Test 5 : Status filter Active successful!")

    driver.get(MODULE_URLS["therapists"])
    time.sleep(2)
    print("Test 6 : Listing filters checked")


def listing_active_inactive_action():
    """ACTIVE → INACTIVE on the QA-created therapist only (never production first row)."""
    global _QA_STATUS_THERAPIST
    from KskinCMS.cms_auth import open_module, toggle_row_status
    from KskinCMS.cms_config import MODULE_URLS

    name = _QA_CREATED_THERAPIST
    if not name:
        raise AssertionError(
            "Therapist status FAILED: no QA therapist from create step "
            "(create before toggle)"
        )
    # Use first line only if cell text ever includes mobile
    name = name.split("\n")[0].strip()
    _QA_STATUS_THERAPIST = name
    open_module(driver, MODULE_URLS["therapists"], wait_css='input[name="code"]')
    ok = toggle_row_status(driver, name, make_inactive=True)
    if not ok:
        raise AssertionError(
            f"Therapist ACTIVE→INACTIVE FAILED for '{name}' (report to dev / Asana)"
        )
    print("Test 9 : Changed NEW QA therapist to inactive successfully!")


def listing_inactive_active_action():
    """INACTIVE → ACTIVE on the same QA therapist."""
    from KskinCMS.cms_auth import open_module, toggle_row_status
    from KskinCMS.cms_config import MODULE_URLS

    name = (_QA_STATUS_THERAPIST or _QA_CREATED_THERAPIST or "").split("\n")[0].strip()
    if not name:
        raise AssertionError("Therapist status FAILED: no QA therapist name")
    open_module(driver, MODULE_URLS["therapists"], wait_css='input[name="code"]')
    ok = toggle_row_status(driver, name, make_inactive=False)
    if not ok:
        raise AssertionError(
            f"Therapist INACTIVE→ACTIVE FAILED for '{name}' (report to dev / Asana)"
        )
    print("Test 10 : Changed NEW QA therapist back to active successfully!")


def rows_per_page_actions():
    from KskinCMS.cms_config import MODULE_URLS

    driver.get(MODULE_URLS["therapists"])
    time.sleep(2)
    scroll_to_bottom()
    time.sleep(1)
    selects = driver.find_elements(By.XPATH, "//select[@title='pageSize']")
    if not selects:
        print("Test 11 : Rows per page control not present — skipped")
        return
    select = Select(selects[0])
    select.select_by_value("50")
    time.sleep(2)
    select = Select(driver.find_element(By.XPATH, "//select[@title='pageSize']"))
    select.select_by_value("10")
    time.sleep(2)
    page2 = driver.find_elements(By.XPATH, "//table//tfoot//*[normalize-space()='2']")
    if page2:
        page2[0].click()
        time.sleep(1)
        page1 = driver.find_elements(By.XPATH, "//table//tfoot//*[normalize-space()='1']")
        if page1:
            page1[0].click()
            time.sleep(1)
        print("Test 11 : Rows per page + pagination checked!")
    else:
        print("Test 11 : Rows per page checked (pagination N/A — single page).")


def _pick_calendar_day(prefer_past=False, adult_dob=False):
    """Open date picker already clicked; pick a visible day.

    adult_dob=True: year dropdown → Previous decades → pick 1995 → day 15.
    prefer_past=True: step back a few months (non-DOB use).
    """
    if adult_dob:
        year_hdr = [
            b
            for b in driver.find_elements(By.XPATH, "//button[string-length(normalize-space())=4]")
            if b.is_displayed() and (b.text or "").strip().isdigit()
        ]
        if year_hdr:
            driver.execute_script("arguments[0].click();", year_hdr[0])
            time.sleep(0.5)
            # Decade grid starts ~2017–2028; two Previous → 1993–2004
            for _ in range(2):
                prev = [
                    b
                    for b in driver.find_elements(By.XPATH, "//button[@aria-label='Previous']")
                    if b.is_displayed()
                ]
                if prev:
                    driver.execute_script("arguments[0].click();", prev[0])
                    time.sleep(0.35)
            picked_year = False
            for y in ("1995", "1998", "2000", "1996", "1994"):
                ok = driver.execute_script(
                    """
                    const y=arguments[0];
                    const b=[...document.querySelectorAll('button')].find(el =>
                      el.offsetParent && (el.innerText||'').trim()===y
                    );
                    if (b) { b.click(); return true; }
                    return false;
                    """,
                    y,
                )
                if ok:
                    picked_year = True
                    time.sleep(0.5)
                    break
            if not picked_year:
                # fallback: first year button that is not the header year
                driver.execute_script(
                    """
                    const hdr = arguments[0];
                    const b=[...document.querySelectorAll('button')].find(el =>
                      el.offsetParent && /^\\d{4}$/.test((el.innerText||'').trim())
                      && (el.innerText||'').trim() !== hdr
                    );
                    if (b) b.click();
                    """,
                    (year_hdr[0].text or "").strip(),
                )
                time.sleep(0.5)
    elif prefer_past:
        for _ in range(3):
            prev = driver.find_elements(
                By.XPATH,
                "//button[contains(@aria-label,'Previous') or contains(@aria-label,'previous')]",
            )
            visible = [b for b in prev if b.is_displayed()]
            if visible:
                driver.execute_script("arguments[0].click();", visible[0])
                time.sleep(0.4)
            else:
                break

    # Prefer react-day-picker day buttons
    day_clicked = driver.execute_script(
        """
        const want = [15, 10, 5, 1];
        const days = [...document.querySelectorAll('button.rdp-button, button[name=day], .rdp-day button, button')]
          .filter(b => b.offsetParent && !b.disabled
            && /^\\d{1,2}$/.test((b.innerText||'').trim())
            && (b.className||'').toString().includes('rdp'));
        for (const n of want) {
          const hit = days.find(b => (b.innerText||'').trim() === String(n));
          if (hit) { hit.click(); return n; }
        }
        // fallback any visible day button
        for (const n of want) {
          const hit = [...document.querySelectorAll('button')].find(b =>
            b.offsetParent && !b.disabled && (b.innerText||'').trim() === String(n)
            && (b.innerText||'').trim().length <= 2
          );
          if (hit) { hit.click(); return n; }
        }
        return null;
        """
    )
    time.sleep(0.35)
    for ok in driver.find_elements(
        By.XPATH, "//button[contains(.,'Ok') or contains(.,'OK') or contains(.,'Apply')]"
    ):
        if ok.is_displayed():
            driver.execute_script("arguments[0].click();", ok)
            time.sleep(0.3)
            break
    return day_clicked


def _assign_outlet():
    """Pick at least one Assigned Outlet (required on therapist create)."""
    btn = None
    for _ in range(4):
        candidates = [
            b
            for b in driver.find_elements(
                By.XPATH,
                "//button[contains(.,'Select an outlet') or contains(.,'outlet or more')]",
            )
            if b.is_displayed()
        ]
        if candidates:
            btn = candidates[0]
            break
        time.sleep(0.4)
    if not btn:
        raise AssertionError("Therapist create FAILED: Assigned Outlet control missing")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
    driver.execute_script("arguments[0].click();", btn)
    time.sleep(1.2)
    prefer = (
        "Anchorpoint",
        "Kskin Compass One Hub",
        "Chinatown Point",
        "Le Quest",
        "Outlet B",
    )
    picked_name = None
    for name in prefer:
        items = driver.find_elements(
            By.XPATH, f"//li[.//label[contains(.,'{name}')] or contains(.,'{name}')]"
        )
        visible = [li for li in items if li.is_displayed()]
        if not visible:
            continue
        # Re-query label text then click via JS on fresh locator
        driver.execute_script(
            """
            const name = arguments[0];
            const lis = [...document.querySelectorAll('li')].filter(li =>
              li.offsetParent && (li.innerText||'').includes(name)
            );
            if (!lis.length) return false;
            const lab = lis[0].querySelector('label') || lis[0];
            lab.click();
            return true;
            """,
            name,
        )
        picked_name = name
        break
    if not picked_name:
        ok = driver.execute_script(
            """
            const lis = [...document.querySelectorAll('li')].filter(li =>
              li.offsetParent && !(li.innerText||'').includes('All outlets')
              && (li.querySelector('label') || li.innerText)
            );
            if (!lis.length) return null;
            const lab = lis[0].querySelector('label') || lis[0];
            const name = (lab.innerText||lis[0].innerText||'').trim().split('\\n')[0];
            lab.click();
            return name;
            """
        )
        picked_name = ok
    if not picked_name:
        raise AssertionError("Therapist create FAILED: no outlet options to assign")
    time.sleep(0.5)
    try:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    except Exception:
        pass
    time.sleep(0.3)
    print("Outlet assigned:", str(picked_name)[:60])


def _pick_time_ok():
    for ok in driver.find_elements(By.XPATH, "//button[contains(.,'Ok') or contains(.,'OK')]"):
        if ok.is_displayed():
            driver.execute_script("arguments[0].click();", ok)
            time.sleep(0.3)
            break


def _real_click(el):
    """Pointer-event sequence first (Radix-friendly), then CDP mouse as fallback."""
    try:
        driver.execute_script(
            """
            const el = arguments[0];
            const r = el.getBoundingClientRect();
            const x = r.left + r.width / 2, y = r.top + r.height / 2;
            el.scrollIntoView({block:'center'});
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
            el,
        )
        return
    except Exception:
        pass
    rect = driver.execute_script(
        "const r=arguments[0].getBoundingClientRect();"
        "return {x:r.left+r.width/2,y:r.top+r.height/2};",
        el,
    )
    x, y = rect["x"], rect["y"]
    for typ, btn, buttons in (
        ("mouseMoved", "none", 0),
        ("mousePressed", "left", 1),
        ("mouseReleased", "left", 0),
    ):
        payload = {"type": typ, "x": x, "y": y, "button": btn, "buttons": buttons}
        if typ != "mouseMoved":
            payload["clickCount"] = 1
        driver.execute_cdp_cmd("Input.dispatchMouseEvent", payload)


def add_new_therapist():
    """Create a QA therapist via form (staging-safe selectors)."""
    global _QA_CREATED_THERAPIST
    from KskinCMS.cms_auth import js_fill, open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    uniq = str(int(time.time()))[-6:]
    full_name = f"QA Ther Full {uniq}"
    display_name = f"QA Ther {uniq}"
    email = f"qa.ther.{uniq}@yopmail.com"
    mobile = f"9{uniq}1"  # 8 digits

    open_module(driver, MODULE_URLS["therapists"], wait_css='input[name="code"]')
    create_btns = driver.find_elements(
        By.XPATH,
        "//button[contains(.,'Add') or contains(.,'Create') or contains(.,'New therapist')]",
    )
    if create_btns:
        driver.execute_script("arguments[0].click();", create_btns[0])
        time.sleep(3)
    if "/new" not in (driver.current_url or ""):
        driver.get(MODULE_URLS["therapists"] + "/new")
        time.sleep(4)

    wait_name("fullName")

    # Optional image
    img = "/Users/aungwaiwaithin/Downloads/llk_abs.jpeg"
    if not os.path.isfile(img):
        img = "/Users/aungwaiwaithin/Downloads/test_image.png"
    file_inputs = driver.find_elements(By.XPATH, '//input[@type="file"]')
    if file_inputs and os.path.isfile(img):
        try:
            file_inputs[0].send_keys(img)
            time.sleep(2)
            up = [b for b in driver.find_elements(By.XPATH, "//button[contains(.,'Upload')]") if b.is_displayed()]
            if up:
                driver.execute_script("arguments[0].click();", up[-1])
                time.sleep(3)
                print("Test 12 : Image uploaded")
        except Exception as e:
            print(f"Image upload skipped: {e}")

    js_fill(driver, driver.find_element(By.NAME, "fullName"), full_name)
    js_fill(driver, driver.find_element(By.NAME, "displayName"), display_name)

    # DOB past date
    dob_btns = driver.find_elements(By.XPATH, "//label[@for='dob']/following::button[1]")
    if not dob_btns:
        dob_btns = driver.find_elements(
            By.XPATH,
            "//*[contains(.,'Date of Birth') or contains(.,'Date of birth')]/following::button[1]",
        )
    if not dob_btns:
        raise AssertionError("Therapist create FAILED: DOB control missing")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", dob_btns[0])
    driver.execute_script("arguments[0].click();", dob_btns[0])
    time.sleep(1)
    _pick_calendar_day(adult_dob=True)
    time.sleep(0.5)
    dob_val = (dob_btns[0].text if dob_btns else "") or ""
    try:
        dob_val = driver.find_element(By.XPATH, "//label[@for='dob']/following::button[1]").text
    except Exception:
        pass
    if "Pick a Date" in (dob_val or "") or not (dob_val or "").strip():
        raise AssertionError(
            f"Therapist create FAILED: DOB not set (got {dob_val!r}) (report to dev / Asana)"
        )
    print("Test 15 : DOB selected —", (dob_val or "").strip()[:40])
    time.sleep(0.5)

    from selenium.common.exceptions import StaleElementReferenceException

    def _safe_js_fill(field_name, value, tries=4):
        last = None
        for _ in range(tries):
            try:
                el = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, field_name))
                )
                js_fill(driver, el, value)
                return
            except StaleElementReferenceException as e:
                last = e
                time.sleep(0.4)
        raise AssertionError(f"Therapist create FAILED filling {field_name}: {last}")

    _safe_js_fill("email", email)

    # Gender — re-query each attempt
    gender_done = False
    for _ in range(3):
        try:
            g_label = driver.find_elements(
                By.XPATH, "//label[contains(.,'Gender')]/following::button[@role='combobox'][1]"
            )
            gender_btns = driver.find_elements(By.XPATH, "//button[@role='combobox']")
            gbtn = g_label[0] if g_label else (gender_btns[0] if gender_btns else None)
            if not gbtn:
                break
            driver.execute_script("arguments[0].click();", gbtn)
            time.sleep(0.8)
            opt = [
                o
                for o in driver.find_elements(
                    By.XPATH, "//*[@role='option' and (contains(.,'Female') or contains(.,'Male'))]"
                )
                if o.is_displayed()
            ]
            if opt:
                label = (opt[0].text or "")[:20]
                driver.execute_script("arguments[0].click();", opt[0])
                print("Gender selected:", label)
                gender_done = True
            try:
                driver.find_element(By.TAG_NAME, "body").click()
            except Exception:
                pass
            time.sleep(0.3)
            break
        except StaleElementReferenceException:
            time.sleep(0.4)
            continue
    if not gender_done:
        print("Gender select soft — continuing (may be optional)")

    for attempt in range(4):
        try:
            if driver.find_elements(By.NAME, "mobile"):
                _safe_js_fill("mobile", mobile)
            else:
                print("Mobile field not found — continuing")
            _assign_outlet()
            break
        except StaleElementReferenceException:
            time.sleep(0.5)
            if attempt == 3:
                raise
    else:
        raise AssertionError("Therapist create FAILED: mobile/outlet after retries")

    # Starts from* (required) — scope under Employment / Starts from, not DOB
    start_btns = driver.find_elements(
        By.XPATH,
        "//label[contains(.,'Starts from')]/following::button[contains(.,'Pick a Date') or contains(.,'Pick a date')][1]",
    )
    if not start_btns:
        start_btns = driver.find_elements(
            By.XPATH,
            "//*[normalize-space()='Starts from*' or normalize-space()='Starts from']"
            "/following::button[contains(.,'Pick a Date')][1]",
        )
    if not start_btns:
        # After DOB is set, first remaining "Pick a Date" is Starts from
        start_btns = [
            b
            for b in driver.find_elements(By.XPATH, "//button[contains(.,'Pick a Date')]")
            if b.is_displayed() and "Pick a Date" in (b.text or "")
        ][:1]
    if not start_btns:
        raise AssertionError("Therapist create FAILED: Starts-from date control missing")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", start_btns[0])
    driver.execute_script("arguments[0].click();", start_btns[0])
    time.sleep(1)
    _pick_calendar_day(prefer_past=False)
    time.sleep(0.4)
    start_txt = (start_btns[0].text or "").strip()
    try:
        start_txt = driver.find_elements(
            By.XPATH,
            "//label[contains(.,'Starts from')]/following::button[1]",
        )[0].text
    except Exception:
        pass
    if "Pick a Date" in (start_txt or ""):
        raise AssertionError(
            f"Therapist create FAILED: Starts-from date not set (got {start_txt!r})"
        )
    print("Starts-from date picked —", (start_txt or "")[:40])
    time_btns = [
        b for b in driver.find_elements(By.XPATH, "//button[contains(.,'Pick a time')]") if b.is_displayed()
    ]
    if time_btns:
        driver.execute_script("arguments[0].click();", time_btns[0])
        time.sleep(0.8)
        _pick_time_ok()
        print("Starts-from time picked")

    # Ends on (optional but fill when present)
    end_date = [
        b
        for b in driver.find_elements(
            By.XPATH,
            "//label[contains(.,'Ends on') or contains(.,'End On')]"
            "/following::button[contains(.,'Pick a Date') or contains(.,'Pick a date')][1]",
        )
        if b.is_displayed()
    ]
    if end_date:
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", end_date[0])
            driver.execute_script("arguments[0].click();", end_date[0])
            time.sleep(1)
            nxt = driver.find_elements(
                By.XPATH,
                "//button[contains(@aria-label,'Next') or contains(@aria-label,'next')]",
            )
            visible = [b for b in nxt if b.is_displayed()]
            if visible:
                driver.execute_script("arguments[0].click();", visible[0])
                time.sleep(0.4)
            _pick_calendar_day(prefer_past=False)
            print("Ends-on date picked")
            end_time = [
                b
                for b in driver.find_elements(
                    By.XPATH,
                    "//label[contains(.,'Ends on')]/following::button[contains(.,'Pick a time')][1]",
                )
                if b.is_displayed()
            ]
            if not end_time:
                end_time = [
                    b
                    for b in driver.find_elements(By.XPATH, "//button[contains(.,'Pick a time')]")
                    if b.is_displayed()
                ]
            if end_time:
                driver.execute_script("arguments[0].click();", end_time[-1])
                time.sleep(0.8)
                _pick_time_ok()
                print("Ends-on time picked")
        except StaleElementReferenceException:
            print("Ends-on soft — continuing")

    save = [
        b
        for b in driver.find_elements(
            By.XPATH,
            "//footer//button[contains(.,'Save') or contains(.,'Create')] | //button[contains(.,'Save')]",
        )
        if b.is_displayed()
    ]
    if not save:
        raise AssertionError("Therapist create FAILED: no Save button")
    # Prefer enabled Save
    enabled = [b for b in save if b.is_enabled()]
    btn = enabled[-1] if enabled else save[-1]
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
    driver.execute_script("arguments[0].click();", btn)
    time.sleep(6)

    if "/new" in (driver.current_url or ""):
        # retry save once
        save2 = [b for b in driver.find_elements(By.XPATH, "//button[contains(.,'Save')]") if b.is_displayed()]
        if save2:
            driver.execute_script("arguments[0].click();", save2[-1])
            time.sleep(5)
    if "/new" in (driver.current_url or ""):
        msgs = []
        for m in driver.find_elements(By.CSS_SELECTOR, "p, [role='alert'], label"):
            t = (m.text or "").strip()
            if t and any(
                k in t.lower()
                for k in ("required", "invalid", "must", "please", "already", "error")
            ):
                msgs.append(t)
        body_snip = (driver.find_element(By.TAG_NAME, "body").text or "")[:500]
        raise AssertionError(
            f"Therapist create FAILED: still on /new. msgs={msgs[:15]} "
            f"body={body_snip!r} (report to dev / Asana)"
        )

    open_module(driver, MODULE_URLS["therapists"], wait_css='input[name="code"]')
    search_listing(driver, display_name)
    time.sleep(2)
    rows = driver.find_elements(By.XPATH, f"//table//tbody/tr[contains(., '{display_name}')]")
    if not rows:
        # try full name
        search_listing(driver, full_name)
        time.sleep(2)
        rows = driver.find_elements(By.XPATH, f"//table//tbody/tr[contains(., '{full_name}')]")
        if rows:
            display_name = full_name
    if not rows:
        raise AssertionError(
            f"Therapist create FAILED: '{display_name}' not listed "
            "(report to dev / Asana)"
        )
    _QA_CREATED_THERAPIST = display_name
    print(f"Test 22 : New therapist created successfully! : {display_name}")


def _open_qa_therapist_edit(name=None):
    from KskinCMS.cms_auth import open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    name = name or _QA_CREATED_THERAPIST
    if not name:
        raise AssertionError("Therapist view/edit FAILED: no QA therapist name")
    open_module(driver, MODULE_URLS["therapists"], wait_css='input[name="code"]')
    search_listing(driver, name)
    time.sleep(1.5)
    row = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, f"//table//tbody/tr[contains(., '{name}')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", row)
    time.sleep(0.2)

    def _form_open():
        return bool(
            driver.find_elements(By.NAME, "displayName") or driver.find_elements(By.NAME, "fullName")
        )

    opened = False
    spans = row.find_elements(By.CSS_SELECTOR, ".actions-column > span")
    if spans:
        try:
            # Staging needs a real double-click on the pencil span
            ActionChains(driver).move_to_element(spans[0]).pause(0.2).click().pause(0.15).click().perform()
            time.sleep(2)
            opened = _form_open()
        except Exception:
            pass
    if not opened and spans:
        try:
            _real_click(spans[0])
            time.sleep(1)
            ActionChains(driver).move_to_element(spans[0]).double_click().perform()
            time.sleep(2)
            opened = _form_open()
        except Exception:
            pass
    if not opened:
        # Re-find row (may be stale after navigation attempts)
        rows = driver.find_elements(By.XPATH, f"//table//tbody/tr[contains(., '{name}')]")
        if rows:
            btns = rows[0].find_elements(By.CSS_SELECTOR, ".actions-column button")
            if btns:
                _real_click(btns[0])
                time.sleep(1)
                edits = driver.find_elements(
                    By.XPATH, "//*[@role='menuitem' and (contains(.,'Edit') or contains(.,'View'))]"
                )
                if edits:
                    driver.execute_script("arguments[0].click();", edits[0])
                    time.sleep(2)
                    opened = _form_open()
    if not opened:
        raise AssertionError(
            f"Therapist edit FAILED: could not open form for '{name}' "
            f"url={driver.current_url} (report to dev / Asana)"
        )
    WebDriverWait(driver, 15).until(
        lambda d: d.find_elements(By.NAME, "displayName") or d.find_elements(By.NAME, "fullName")
    )


def check_created_therapist_value():
    """Open QA therapist and verify display/full name readable."""
    _open_qa_therapist_edit()
    disp = ""
    full = ""
    if driver.find_elements(By.NAME, "displayName"):
        disp = driver.find_element(By.NAME, "displayName").get_attribute("value") or ""
    if driver.find_elements(By.NAME, "fullName"):
        full = driver.find_element(By.NAME, "fullName").get_attribute("value") or ""
    print(f"View displayName: {disp}")
    print(f"View fullName: {full}")
    name = _QA_CREATED_THERAPIST or ""
    if name not in disp and name not in full:
        raise AssertionError(
            f"Therapist view FAILED: expected '{name}' in form "
            f"(display='{disp}', full='{full}') (report to dev / Asana)"
        )
    print("Test 26 : View/edit form opened and values readable successfully!")


def update_old_therapist():
    """Rename QA therapist and verify listing."""
    global _QA_CREATED_THERAPIST
    from KskinCMS.cms_auth import js_fill, open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    _open_qa_therapist_edit()
    uniq = str(int(time.time()))[-5:]
    new_name = f"Updated Ther {uniq}"
    # Listing often shows fullName; update both when present
    if driver.find_elements(By.NAME, "fullName"):
        js_fill(driver, driver.find_element(By.NAME, "fullName"), new_name)
    if driver.find_elements(By.NAME, "displayName"):
        js_fill(driver, driver.find_element(By.NAME, "displayName"), new_name)
    time.sleep(0.5)
    save = [
        b
        for b in driver.find_elements(
            By.XPATH, "//footer//button[contains(.,'Save')] | //button[contains(.,'Save')]"
        )
        if b.is_displayed()
    ]
    if not save:
        raise AssertionError("Therapist edit FAILED: no Save button")
    enabled = [b for b in save if b.is_enabled()]
    btn = enabled[-1] if enabled else save[-1]
    driver.execute_script("arguments[0].click();", btn)
    time.sleep(6)
    # If still on detail/edit URL, retry once
    if "/therapists/" in (driver.current_url or "") and "therapists?" not in (driver.current_url or ""):
        save2 = [b for b in driver.find_elements(By.XPATH, "//button[contains(.,'Save')]") if b.is_displayed()]
        if save2:
            driver.execute_script("arguments[0].click();", save2[-1])
            time.sleep(5)

    open_module(driver, MODULE_URLS["therapists"], wait_css='input[name="code"]')
    search_listing(driver, new_name)
    time.sleep(2)
    rows = driver.find_elements(By.XPATH, f"//table//tbody/tr[contains(., '{new_name}')]")
    if not rows:
        body = (driver.find_element(By.TAG_NAME, "body").text or "")[:400]
        raise AssertionError(
            f"Therapist edit FAILED: '{new_name}' not found after save. "
            f"url={driver.current_url} body={body!r} (report to dev / Asana)"
        )
    _QA_CREATED_THERAPIST = new_name
    print(f"Test 30 : Edit therapist successful! : {new_name}")
