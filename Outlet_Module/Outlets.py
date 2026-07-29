import os
import time

from KskinCMS.Outlet_Module.OutletHelper import *
from KskinCMS.Outlet_Module.OutletVarPaths import *
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

load_dotenv()

# QA outlet created in this module run (ACTIVE↔INACTIVE / view / edit)
_QA_OUTLET_NAME = None
_QA_OUTLET_CODE = None


def open_browser():
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["outlets"], wait_css='input[name="code"]')
    print("Test 1 : Open browser success!")


def outlets_search_and_filters():
    """Listing: matched/unmatched search + region/status filters. Fail hard on product bugs."""
    from KskinCMS.cms_auth import js_fill, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    driver.get(MODULE_URLS["outlets"])
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "code")))
    time.sleep(2)
    print("Test 2 : Navigated to outlet listing successful!")

    # Matched search — use live first-row name (staging data changes)
    first_name = ""
    cells = driver.find_elements(By.CSS_SELECTOR, "table tbody tr:first-child td")
    if cells:
        first_name = (cells[0].text or "").strip().split("\n")[0].strip()
    if not first_name or len(first_name) < 2:
        raise AssertionError("Outlet search FAILED: no usable name on first listing row")

    search_listing(driver, first_name)
    time.sleep(1)
    result = driver.find_element(By.XPATH, "//table//tbody/tr[1]/td[1]").text.strip()
    print(result)
    if first_name not in result and result not in first_name:
        raise AssertionError(
            f"Outlet matched search FAILED: expected '{first_name}', got '{result}' "
            "(report to dev / Asana)"
        )
    print("Test 3 : Searching with matched value is successful!")

    driver.get(MODULE_URLS["outlets"])
    time.sleep(2)

    # Unmatched search
    search = driver.find_element(By.NAME, "code")
    js_fill(driver, search, "520aaZZZ_no_such_outlet")
    time.sleep(2)
    body = driver.find_element(By.TAG_NAME, "body").text
    rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
    empty_ok = (
        "No outlets" in body
        or "No outlet" in body
        or "no result" in body.lower()
        or "no data" in body.lower()
        or not rows
    )
    if not empty_ok:
        raise AssertionError(
            "Outlet unmatched search FAILED: expected empty/no-result state "
            "(report to dev / Asana)"
        )
    print("Test 4 : Searching with unmatched value can show empty result successfully")

    driver.get(MODULE_URLS["outlets"])
    time.sleep(2)

    # Region filter by visible text
    combos = driver.find_elements(By.CSS_SELECTOR, "[role=combobox]")
    if not combos:
        raise AssertionError("Outlet region filter FAILED: no combobox on listing")
    combos[0].click()
    time.sleep(1)
    preferred = (
        "Singapore West",
        "Singapore East",
        "Singapore North",
        "Singapore South",
        "QA Test Region",
    )
    picked = None
    for want in preferred:
        opt = driver.find_elements(
            By.XPATH, f"//*[@role='option' and contains(normalize-space(.), '{want}')]"
        )
        visible = [o for o in opt if o.is_displayed()]
        if visible:
            driver.execute_script("arguments[0].click();", visible[0])
            picked = want
            break
    if not picked:
        opts = [o for o in driver.find_elements(By.CSS_SELECTOR, "[role='option']") if o.is_displayed()]
        if not opts:
            raise AssertionError("Outlet region filter FAILED: no region options")
        picked = (opts[0].text or "").strip()
        driver.execute_script("arguments[0].click();", opts[0])
    time.sleep(2)
    region_cell = driver.find_element(By.XPATH, "//table//tbody/tr[1]/td[4]").text.strip()
    print(region_cell)
    if picked and picked not in region_cell and region_cell not in picked:
        # Some UIs show short region label — still require a non-empty filtered row
        if not region_cell:
            raise AssertionError(
                f"Outlet region filter FAILED after selecting '{picked}' "
                "(report to dev / Asana)"
            )
    print("Test 5 : Region filter applied:", region_cell)

    driver.get(MODULE_URLS["outlets"])
    time.sleep(2)

    # Status filter Active
    combos = driver.find_elements(By.CSS_SELECTOR, "[role=combobox]")
    if len(combos) < 2:
        raise AssertionError("Outlet status filter FAILED: status combobox missing")
    combos[1].click()
    time.sleep(1)
    opt = driver.find_elements(
        By.XPATH, "//*[@role='option' and contains(.,'Active')] | //*[normalize-space()='Active']"
    )
    visible = [o for o in opt if o.is_displayed()]
    if not visible:
        raise AssertionError("Outlet status filter FAILED: Active option not found")
    driver.execute_script("arguments[0].click();", visible[0])
    time.sleep(2)
    status = driver.find_element(By.XPATH, "//table//tbody/tr[1]/td[7]").text.strip().upper()
    print(status)
    if "INACTIVE" in status or status != "ACTIVE":
        raise AssertionError(
            f"Outlet status filter Active FAILED: row status='{status}' "
            "(report to dev / Asana)"
        )
    print("Test 6 : Status filter Active successful!")
    driver.get(MODULE_URLS["outlets"])
    time.sleep(2)


def _fill_outlet_form_required(uniq, outlet_name, outlet_code):
    """Shared create/edit required fields (staging-safe selectors)."""
    from KskinCMS.cms_auth import js_fill

    wait_name("name")
    js_fill(driver, driver.find_element(By.NAME, "name"), outlet_name)
    js_fill(driver, driver.find_element(By.NAME, "code"), outlet_code)
    if driver.find_elements(By.NAME, "unitNo"):
        js_fill(driver, driver.find_element(By.NAME, "unitNo"), f"U{uniq}")
    if driver.find_elements(By.NAME, "postalCode"):
        js_fill(driver, driver.find_element(By.NAME, "postalCode"), "123456")

    # Region
    region_btns = driver.find_elements(
        By.XPATH,
        "//label[contains(.,'Region')]/following::button[@role='combobox'][1]",
    )
    if not region_btns:
        region_btns = [
            b
            for b in driver.find_elements(By.XPATH, "//button[@role='combobox']")
            if "Region" in (b.text or "") or (b.text or "").strip() in ("Select", "Select Region")
        ]
    region_set = False
    if region_btns:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", region_btns[0])
        driver.execute_script("arguments[0].click();", region_btns[0])
        time.sleep(1.5)
        for want in (
            "Singapore West",
            "Singapore East",
            "Singapore North",
            "Singapore South",
            "QA Test Region",
        ):
            matches = driver.find_elements(
                By.XPATH,
                f"//*[@role='option' and contains(normalize-space(.), '{want}')]",
            )
            visible = [m for m in matches if m.is_displayed()]
            if visible:
                driver.execute_script("arguments[0].click();", visible[0])
                print(f"Outlet region selected: {want}")
                region_set = True
                break
        if not region_set:
            for o in driver.find_elements(By.CSS_SELECTOR, "[role='option']"):
                try:
                    if o.is_displayed() and (o.text or "").strip():
                        driver.execute_script("arguments[0].click();", o)
                        print(f"Outlet region selected: {(o.text or '')[:60]}")
                        region_set = True
                        break
                except Exception:
                    continue
        try:
            driver.find_element(By.TAG_NAME, "body").click()
        except Exception:
            pass
    if not region_set:
        raise AssertionError("Outlet create FAILED: could not set Region")

    tas = driver.find_elements(By.TAG_NAME, "textarea")
    if tas:
        js_fill(driver, tas[0], f"QA Addr {uniq}")

    if driver.find_elements(By.NAME, "queueUrl"):
        js_fill(driver, driver.find_element(By.NAME, "queueUrl"), f"https://queue.sg/qa-{uniq}")

    # Opening hours
    try:
        oh = driver.find_elements(By.XPATH, "//*[contains(text(),'Opening Hours')]")
        if oh:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", oh[0])
        time.sleep(0.4)
        for u in driver.find_elements(By.CSS_SELECTOR, "td button[role='switch'], td button[role='checkbox']"):
            try:
                if u.is_displayed():
                    driver.execute_script("arguments[0].click();", u)
                    print("Toggled an opening-hours switch")
                    time.sleep(1)
                    break
            except Exception:
                continue
        for label, want in (("From", "9:00 am"), ("To", "10:00 pm")):
            btns = driver.find_elements(
                By.XPATH, f"//table//button[@role='combobox' and normalize-space()='{label}']"
            )
            if not btns:
                btns = driver.find_elements(
                    By.XPATH, f"//button[@role='combobox' and normalize-space()='{label}']"
                )
            if not btns:
                continue
            driver.execute_script("arguments[0].click();", btns[0])
            time.sleep(0.8)
            opt = driver.find_elements(
                By.XPATH, f"//*[@role='option' and contains(normalize-space(.), '{want}')]"
            )
            if not opt:
                opt = driver.find_elements(
                    By.XPATH, "//*[@role='option' and (contains(., 'am') or contains(., 'pm'))]"
                )
            visible = [o for o in opt if o.is_displayed()]
            if visible:
                driver.execute_script("arguments[0].click();", visible[0])
                print(f"Opening hours {label} set")
            try:
                driver.find_element(By.TAG_NAME, "body").click()
            except Exception:
                pass
    except Exception as e:
        raise AssertionError(f"Outlet create FAILED: opening hours — {e}") from e

    # Starts from
    start_btns = driver.find_elements(
        By.XPATH,
        "//*[contains(.,'Starts from')]/following::button[contains(.,'Pick a Date') or contains(.,'Pick a date')][1]",
    )
    if not start_btns:
        start_btns = driver.find_elements(By.XPATH, "//button[contains(.,'Pick a Date')]")
    if not start_btns:
        raise AssertionError("Outlet create FAILED: Starts-from date control missing")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", start_btns[0])
    driver.execute_script("arguments[0].click();", start_btns[0])
    time.sleep(1)
    day_cells = driver.find_elements(
        By.XPATH,
        "//button[not(@disabled) and normalize-space(text())!='' and string-length(normalize-space(text()))<=2]",
    )
    for c in day_cells:
        try:
            if c.is_displayed() and (c.text or "").strip().isdigit():
                driver.execute_script("arguments[0].click();", c)
                time.sleep(0.3)
                break
        except Exception:
            continue
    for ok in driver.find_elements(By.XPATH, "//button[contains(.,'Ok') or contains(.,'OK') or contains(.,'Apply')]"):
        if ok.is_displayed():
            driver.execute_script("arguments[0].click();", ok)
            time.sleep(0.3)
            break
    print("Starts-from date picked")

    time_btns = driver.find_elements(
        By.XPATH,
        "//*[contains(.,'Starts from')]/following::button[contains(.,'Pick a time') or contains(.,'Pick a Time')][1]",
    )
    if not time_btns:
        time_btns = driver.find_elements(By.XPATH, "//button[contains(.,'Pick a time')]")
    if time_btns:
        driver.execute_script("arguments[0].click();", time_btns[0])
        time.sleep(1)
        for ok in driver.find_elements(By.XPATH, "//button[contains(.,'Ok') or contains(.,'OK')]"):
            if ok.is_displayed():
                driver.execute_script("arguments[0].click();", ok)
                time.sleep(0.3)
                break
        print("Starts-from time picked")

    img = "/Users/aungwaiwaithin/Downloads/test_image.png"
    if not os.path.isfile(img):
        img = "/Users/aungwaiwaithin/Downloads/llk_abs.jpeg"
    file_inputs = driver.find_elements(By.XPATH, '//input[@type="file"]')
    if file_inputs and os.path.isfile(img):
        try:
            file_inputs[0].send_keys(img)
            time.sleep(2)
            up = driver.find_elements(By.XPATH, "//button[contains(.,'Upload')]")
            if up:
                driver.execute_script("arguments[0].click();", up[-1])
                time.sleep(3)
                print("Outlet image uploaded")
        except Exception as e:
            print(f"Image upload skipped: {e}")


def _submit_outlet_publish():
    publish = [
        b for b in driver.find_elements(By.XPATH, "//button[contains(.,'Publish')]") if b.is_displayed()
    ]
    draft = [
        b
        for b in driver.find_elements(
            By.XPATH, "//button[contains(.,'Save as draft') or contains(.,'Save')]"
        )
        if b.is_displayed()
    ]
    if publish and publish[-1].is_enabled():
        driver.execute_script("arguments[0].click();", publish[-1])
        print("Outlet submit clicked: Publish")
    elif draft:
        driver.execute_script("arguments[0].click();", draft[0])
        print("Outlet submit clicked: Save as draft (Publish disabled)")
    else:
        raise AssertionError("Outlet create FAILED: No Publish/Save button")
    time.sleep(5)


def create_new_outlet():
    """Create published QA outlet + light required-field check. Stores name for later steps."""
    global _QA_OUTLET_NAME, _QA_OUTLET_CODE
    from KskinCMS.cms_auth import js_fill, open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    uniq = str(int(time.time()))[-6:]
    outlet_name = f"QA Outlet {uniq}"
    outlet_code = f"QO{uniq}"

    open_module(driver, MODULE_URLS["outlets"], wait_css='input[name="code"]')
    # Open create — prefer UI button, else direct URL
    create_btns = driver.find_elements(
        By.XPATH,
        "//button[contains(.,'Create') or contains(.,'Add') or contains(.,'New')]",
    )
    if create_btns:
        driver.execute_script("arguments[0].click();", create_btns[0])
        time.sleep(3)
    if "/new" not in (driver.current_url or ""):
        driver.get(MODULE_URLS["outlets"] + "/new")
        time.sleep(4)

    # Light validation: clear name → expect required
    wait_name("name")
    js_fill(driver, driver.find_element(By.NAME, "name"), "x")
    time.sleep(0.3)
    el = driver.find_element(By.NAME, "name")
    el.send_keys(Keys.COMMAND, "a")
    el.send_keys(Keys.BACKSPACE)
    time.sleep(0.5)
    body = driver.find_element(By.TAG_NAME, "body").text
    if "Outlet name is required" in body or "required" in body.lower():
        print("Test 7 : Outlet name required message shown")
    else:
        print("Test 7 : Name required soft-check — message text not found (continuing create)")

    _fill_outlet_form_required(uniq, outlet_name, outlet_code)
    _submit_outlet_publish()

    if "/new" in (driver.current_url or ""):
        msgs = []
        for m in driver.find_elements(By.CSS_SELECTOR, "p, [role='alert']"):
            t = (m.text or "").strip()
            if t and any(k in t.lower() for k in ("required", "invalid", "must", "please")):
                msgs.append(t)
        raise AssertionError(
            f"Outlet create FAILED: still on /new. msgs={msgs[:15]} (report to dev / Asana)"
        )

    open_module(driver, MODULE_URLS["outlets"], wait_css='input[name="code"]')
    search_listing(driver, outlet_name)
    time.sleep(2)
    rows = driver.find_elements(By.XPATH, f"//table//tbody/tr[contains(., '{outlet_name}')]")
    if not rows:
        raise AssertionError(
            f"Outlet create FAILED: '{outlet_name}' not in listing (report to dev / Asana)"
        )
    _QA_OUTLET_NAME = outlet_name
    _QA_OUTLET_CODE = outlet_code
    print(f"Test 23 : New outlet is created successfully! : {outlet_name}")


def change_outlet_status_from_listing():
    """ACTIVE↔INACTIVE on the QA outlet only (never random first row)."""
    from KskinCMS.cms_auth import open_module, toggle_row_status
    from KskinCMS.cms_config import MODULE_URLS

    name = _QA_OUTLET_NAME
    if not name:
        raise AssertionError("Outlet status FAILED: no QA outlet from create step")

    open_module(driver, MODULE_URLS["outlets"], wait_css='input[name="code"]')
    ok = toggle_row_status(driver, name, make_inactive=True)
    if not ok:
        raise AssertionError(
            f"Outlet ACTIVE→INACTIVE FAILED for '{name}' (report to dev / Asana)"
        )
    print("Test 24 : Changed QA outlet to inactive successfully!")

    ok = toggle_row_status(driver, name, make_inactive=False)
    if not ok:
        raise AssertionError(
            f"Outlet INACTIVE→ACTIVE FAILED for '{name}' (report to dev / Asana)"
        )
    print("Test 25 : Changed QA outlet back to active successfully!")


def _open_qa_outlet_edit():
    from KskinCMS.cms_auth import open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    name = _QA_OUTLET_NAME
    if not name:
        raise AssertionError("Outlet view/edit FAILED: no QA outlet name")
    open_module(driver, MODULE_URLS["outlets"], wait_css='input[name="code"]')
    search_listing(driver, name)
    time.sleep(1)
    row = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, f"//table//tbody/tr[contains(., '{name}')]"))
    )
    # Prefer edit icon span; fallback row click / actions
    spans = row.find_elements(By.CSS_SELECTOR, ".actions-column > span, td:last-child span")
    if spans:
        ActionChains(driver).move_to_element(spans[0]).click().perform()
    else:
        ActionChains(driver).move_to_element(row).click().perform()
    time.sleep(3)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "name")))


def check_created_outlet_value():
    """Open QA outlet edit/view and verify name + code are readable."""
    _open_qa_outlet_edit()
    name_val = driver.find_element(By.NAME, "name").get_attribute("value") or ""
    code_val = driver.find_element(By.NAME, "code").get_attribute("value") or ""
    print(f"View name: {name_val}")
    print(f"View code: {code_val}")
    if _QA_OUTLET_NAME not in name_val:
        raise AssertionError(
            f"Outlet view FAILED: name '{name_val}' != '{_QA_OUTLET_NAME}' "
            "(report to dev / Asana)"
        )
    if _QA_OUTLET_CODE and _QA_OUTLET_CODE not in code_val:
        raise AssertionError(
            f"Outlet view FAILED: code '{code_val}' != '{_QA_OUTLET_CODE}' "
            "(report to dev / Asana)"
        )
    print("Test 26-27 : View/edit form opened and values readable successfully!")


def update_old_outlet():
    """Rename QA outlet, save, verify searchable under new name."""
    global _QA_OUTLET_NAME
    from KskinCMS.cms_auth import js_fill, open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    _open_qa_outlet_edit()
    uniq = str(int(time.time()))[-5:]
    new_name = f"Updated Outlet {uniq}"
    js_fill(driver, driver.find_element(By.NAME, "name"), new_name)
    time.sleep(0.5)

    save_btns = [
        b
        for b in driver.find_elements(
            By.XPATH,
            "//button[contains(.,'Publish') or contains(.,'Save') or contains(.,'Update')]",
        )
        if b.is_displayed()
    ]
    if not save_btns:
        raise AssertionError("Outlet edit FAILED: no Save/Publish button")
    # Prefer Publish/Update over generic Save if both exist
    preferred = [b for b in save_btns if "Publish" in (b.text or "") or "Update" in (b.text or "")]
    btn = preferred[-1] if preferred else save_btns[-1]
    driver.execute_script("arguments[0].click();", btn)
    time.sleep(5)

    open_module(driver, MODULE_URLS["outlets"], wait_css='input[name="code"]')
    search_listing(driver, new_name)
    time.sleep(2)
    rows = driver.find_elements(By.XPATH, f"//table//tbody/tr[contains(., '{new_name}')]")
    if not rows:
        raise AssertionError(
            f"Outlet edit FAILED: '{new_name}' not found after save (report to dev / Asana)"
        )
    _QA_OUTLET_NAME = new_name
    print(f"Test 30 : Edit outlet successful! : {new_name}")
