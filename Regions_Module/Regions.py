import time

from KskinCMS.Regions_Module.RegionHelper import *
from KskinCMS.Regions_Module.RegionVarPaths import *
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

load_dotenv()

# QA region created in this module run (edit that item only)
_QA_REGION_NAME = None


def open_browser():
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["regions"], wait_css='input[name="code"]')
    print("Test 1 : Open browser success!")
    print("Test 2 : Navigated to regions listing successful!")


def region_searching():
    """Matched + unmatched search. Product failures → AssertionError (Failed for Asana)."""
    from KskinCMS.cms_auth import search_listing
    from KskinCMS.cms_config import MODULE_URLS

    driver.get(MODULE_URLS["regions"])
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "code")))
    time.sleep(2)

    first_name = ""
    cells = driver.find_elements(By.CSS_SELECTOR, "table tbody tr:first-child td")
    if cells:
        first_name = (cells[0].text or "").strip().split("\n")[0].strip()
    if not first_name or len(first_name) < 2:
        raise AssertionError(
            "Region search FAILED: no usable name on first listing row "
            "(report to dev / Asana)"
        )

    search_listing(driver, first_name)
    time.sleep(1)
    actual = driver.find_element(By.XPATH, "//table//tbody/tr[1]/td[1]").text.strip()
    print(actual)
    if first_name not in actual and actual not in first_name:
        raise AssertionError(
            f"Region matched search FAILED: expected '{first_name}', got '{actual}' "
            "(report to dev / Asana)"
        )
    print("Test 3 : Name searching with matched value is successful!")

    driver.get(MODULE_URLS["regions"])
    time.sleep(2)
    search_listing(driver, "NoSuchRegionZZZ")
    time.sleep(2)
    body = driver.find_element(By.TAG_NAME, "body").text
    rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
    empty_ok = (
        "No region" in body
        or "No regions" in body
        or "no result" in body.lower()
        or "no data" in body.lower()
        or not rows
    )
    if not empty_ok:
        raise AssertionError(
            "Region unmatched search FAILED: expected empty/no-result state "
            "(report to dev / Asana)"
        )
    print("Test 4 : Unmatched region search shows empty successfully!")
    driver.get(MODULE_URLS["regions"])
    time.sleep(2)


def _open_add_dialog():
    btn = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//button[contains(.,'Add new Region') or contains(.,'Add new region') "
                "or contains(.,'Create') or contains(.,'Add')]",
            )
        )
    )
    driver.execute_script("arguments[0].click();", btn)
    time.sleep(1.5)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "name")))


def _close_dialog():
    for xp in ["//button[contains(.,'Cancel')]", "//button[@aria-label='Close']"]:
        els = [e for e in driver.find_elements(By.XPATH, xp) if e.is_displayed()]
        if els:
            driver.execute_script("arguments[0].click();", els[0])
            time.sleep(1)
            return
    try:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    except Exception:
        pass
    time.sleep(1)


def _type_name(value):
    from KskinCMS.cms_auth import js_fill

    el = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "name")))
    js_fill(driver, el, value)


def create_new_region():
    """Dialog cancel + create QA region; store name for edit step."""
    global _QA_REGION_NAME
    from KskinCMS.cms_auth import open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["regions"], wait_css='input[name="code"]')
    time.sleep(1)

    _open_add_dialog()
    _close_dialog()
    print("Test 5 : Cancel/close works for create dialog!")

    _open_add_dialog()
    titles = driver.find_elements(
        By.XPATH, "//h2[contains(.,'region') or contains(.,'Region')]"
    )
    if not titles:
        raise AssertionError(
            "Region create FAILED: dialog title missing (report to dev / Asana)"
        )
    print("Test 7 : New region box title:", titles[0].text.strip())

    _type_name("tmp")
    _type_name("")
    time.sleep(0.8)
    if "required" in driver.find_element(By.TAG_NAME, "body").text.lower():
        print("Test 8 : Required message for region name shown")
    else:
        print("Test 8 : Required message text not found (continuing create)")

    uniq = str(int(time.time()))[-5:]
    created = f"QA Region {uniq}"
    _type_name(created)
    time.sleep(0.5)
    save_btns = [
        b
        for b in driver.find_elements(
            By.XPATH, "//button[contains(.,'Save') or contains(.,'Create') or contains(.,'Add')]"
        )
        if b.is_displayed()
    ]
    if not save_btns:
        raise AssertionError("Region create FAILED: no Save/Create button")
    driver.execute_script("arguments[0].click();", save_btns[-1])
    time.sleep(3)

    open_module(driver, MODULE_URLS["regions"], wait_css='input[name="code"]')
    search_listing(driver, created)
    time.sleep(2)
    rows = driver.find_elements(By.XPATH, f"//table//tbody/tr[contains(., '{created}')]")
    if not rows:
        raise AssertionError(
            f"Region create FAILED: '{created}' not in listing (report to dev / Asana)"
        )
    _QA_REGION_NAME = created
    print(f"Test 9 : New region created! : {created}")


def _open_qa_region_edit():
    from KskinCMS.cms_auth import open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    name = _QA_REGION_NAME
    if not name:
        raise AssertionError("Region edit FAILED: no QA region from create step")

    open_module(driver, MODULE_URLS["regions"], wait_css='input[name="code"]')
    search_listing(driver, name)
    time.sleep(1.5)
    row = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.XPATH, f"//table//tbody/tr[contains(., '{name}')]")
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", row)
    time.sleep(0.3)

    # Pencil lives in .actions-column > span (svg.cursor-pointer inside)
    span = row.find_element(By.CSS_SELECTOR, ".actions-column > span")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", span)
    time.sleep(0.2)

    def _dialog_open():
        return bool(
            driver.find_elements(By.XPATH, "//h2[contains(.,'Edit')]")
            or driver.find_elements(By.XPATH, "//*[@role='dialog']//input[@name='name']")
            or driver.find_elements(By.NAME, "name")
        )

    def _real_click(el):
        """CDP mouse click — React/Radix often ignores JS click on icon spans."""
        rect = driver.execute_script(
            "const r=arguments[0].getBoundingClientRect();"
            "return {x:r.left+r.width/2,y:r.top+r.height/2,w:r.width,h:r.height};",
            el,
        )
        x, y = rect["x"], rect["y"]
        driver.execute_cdp_cmd(
            "Input.dispatchMouseEvent",
            {"type": "mouseMoved", "x": x, "y": y, "button": "none", "buttons": 0},
        )
        driver.execute_cdp_cmd(
            "Input.dispatchMouseEvent",
            {
                "type": "mousePressed",
                "x": x,
                "y": y,
                "button": "left",
                "buttons": 1,
                "clickCount": 1,
            },
        )
        driver.execute_cdp_cmd(
            "Input.dispatchMouseEvent",
            {
                "type": "mouseReleased",
                "x": x,
                "y": y,
                "button": "left",
                "buttons": 0,
                "clickCount": 1,
            },
        )

    last_err = None
    for attempt in range(4):
        try:
            # blur search so it doesn't steal focus
            try:
                driver.find_element(By.TAG_NAME, "body").click()
            except Exception:
                pass
            time.sleep(0.2)
            row = driver.find_element(By.XPATH, f"//table//tbody/tr[contains(., '{name}')]")
            span = row.find_element(By.CSS_SELECTOR, ".actions-column > span")
            try:
                _real_click(span)
            except Exception as e:
                last_err = e
                ActionChains(driver).move_to_element(span).pause(0.25).click().perform()
            time.sleep(1.5)
            if _dialog_open():
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.NAME, "name"))
                )
                return
            # also try clicking the svg itself
            svg = row.find_element(By.CSS_SELECTOR, ".actions-column svg")
            try:
                _real_click(svg)
            except Exception as e:
                last_err = e
                ActionChains(driver).move_to_element(svg).pause(0.25).click().perform()
            time.sleep(1.5)
            if _dialog_open():
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.NAME, "name"))
                )
                return
        except Exception as e:
            last_err = e
            time.sleep(0.5)

    raise AssertionError(
        f"Region edit FAILED: could not open Edit region dialog for '{name}': {last_err} "
        "(report to dev / Asana)"
    )


def update_old_region():
    """Edit the QA-created region only (never random first row)."""
    global _QA_REGION_NAME
    from KskinCMS.cms_auth import open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    _open_qa_region_edit()
    _close_dialog()
    print("Test 10 : Cancel works for edit dialog!")

    _open_qa_region_edit()
    titles = driver.find_elements(By.XPATH, "//h2")
    if titles:
        print("Test 12 : Edit region box title:", titles[0].text.strip())

    _type_name("")
    time.sleep(0.8)
    if "required" in driver.find_element(By.TAG_NAME, "body").text.lower():
        print("Test 13 : Required message for region name in update box shown")

    uniq = str(int(time.time()))[-5:]
    updated = f"Updated Region {uniq}"
    _type_name(updated)
    time.sleep(0.5)
    save_btns = [
        b
        for b in driver.find_elements(
            By.XPATH, "//button[contains(.,'Save') or contains(.,'Update')]"
        )
        if b.is_displayed()
    ]
    if not save_btns:
        raise AssertionError("Region edit FAILED: no Save/Update button")
    driver.execute_script("arguments[0].click();", save_btns[-1])
    time.sleep(3)

    open_module(driver, MODULE_URLS["regions"], wait_css='input[name="code"]')
    search_listing(driver, updated)
    time.sleep(2)
    rows = driver.find_elements(By.XPATH, f"//table//tbody/tr[contains(., '{updated}')]")
    if not rows:
        raise AssertionError(
            f"Region edit FAILED: '{updated}' not found after save (report to dev / Asana)"
        )
    _QA_REGION_NAME = updated
    print(f"Test 14 : Region updated successfully! : {updated}")
