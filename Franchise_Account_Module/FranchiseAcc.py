import time
from KskinCMS.Franchise_Account_Module.FranchiseAccHelper import *
from KskinCMS.Franchise_Account_Module.FranchiseAccVarPaths import *
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# install this to use load dotevn >> pip install python-dotenv
load_dotenv()

#pytest FranchiseAccMain.py --html=FranchiseAccReport.html
#pytest -s FranchiseAccMain.py --html=FranchiseAccReport.html

def open_browser():
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS
    open_module(driver, MODULE_URLS["franchisee_accounts"], wait_css='input[name="code"]')
    print("Test 1 : Open browser success!")
    print("Test 2 : Navigated to franchisee account listing successful!")


def franchise_searching():
    from KskinCMS.cms_auth import js_fill
    from KskinCMS.cms_config import MODULE_URLS
    driver.get(MODULE_URLS["franchisee_accounts"])
    time.sleep(3)

    # Franchise name searching (Matched case)
    send_keys_by_name(franchise_path['search_box_name'], 'SND Franchise')
    time.sleep(2)
    actual_name_search_result = get_text_by_xpath(franchise_path['name_search_result_path'])
    exp_name_search_result = 'SND Franchise'
    print(actual_name_search_result)
    if actual_name_search_result == exp_name_search_result:
        print("Test 3 : Name searching with matched value is successful!")
    else:
        print("Something went wrong. Name searching with matched value is failed!")

    driver.find_element(By.NAME, franchise_path['search_box_name']).clear()
    time.sleep(2)
    refresh_search_result()

    # Franchise email searching (Matched case)
    send_keys_by_name(franchise_path['search_box_name'], 'newfranchise@yopmail.com')
    time.sleep(2)
    actual_email_search_result = get_text_by_xpath(franchise_path['email_search_result_path'])
    exp_email_search_result = 'newfranchise@yopmail.com'
    print(actual_email_search_result)
    if actual_email_search_result == exp_email_search_result:
        print("Test 4 : Email searching with matched value is successful!")
    else:
        print("Something went wrong. Email searching with matched value is failed!")

    driver.find_element(By.NAME, franchise_path['search_box_name']).clear()
    time.sleep(2)
    refresh_search_result()

    # Entity name searching — use an entity currently visible on listing (staging data changes)
    first_entity = ""
    cells = driver.find_elements(By.CSS_SELECTOR, "table tbody tr:first-child td")
    if len(cells) >= 3:
        parts = [p.strip() for p in (cells[2].text or "").split("\n") if p.strip()]
        # Prefer longest token (avoid tiny crumbs like "sd")
        first_entity = max(parts, key=len) if parts else ""
    if not first_entity or len(first_entity) < 3:
        print("Test 5 : Entity search skipped — no usable entity text on first row")
        return

    js_fill(driver, driver.find_element(By.NAME, franchise_path['search_box_name']), first_entity)
    time.sleep(2)
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    if not rows:
        print(f"Something went wrong. Entity Name searching with matched value is failed! ({first_entity})")
        return
    actual = rows[0].text
    print(actual)
    if first_entity in actual:
        print("Test 5 : Entity Name searching with matched value is successful!")
    else:
        print("Something went wrong. Entity Name searching with matched value is failed!")

    driver.find_element(By.NAME, franchise_path['search_box_name']).clear()
    time.sleep(2)
    refresh_search_result()


# QA item created for ACTIVE↔INACTIVE / create-view-edit
_QA_STATUS_FRANCHISE = None
_QA_CREATED_FRANCHISE = None
_QA_CREATED_OUTLET = None


def _create_unassigned_qa_outlet(uniq=None):
    """
    Franchise create requires an outlet that is NOT already owned by another entity.
    Staging often shows: 'No available outlets... establish a new outlet...'
    Create a lean QA outlet first, then use its name in Outlet(s) Owned.
    """
    global _QA_CREATED_OUTLET
    from KskinCMS.cms_auth import js_fill, open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    uniq = uniq or str(int(time.time()))[-6:]
    outlet_name = f"QA Fran Outlet {uniq}"
    outlet_code = f"QFO{uniq}"

    open_module(driver, MODULE_URLS["outlets"], wait_css='input[name="code"]')
    driver.get(MODULE_URLS["outlets"] + "/new")
    time.sleep(4)
    wait_name("name")

    js_fill(driver, driver.find_element(By.NAME, "name"), outlet_name)
    js_fill(driver, driver.find_element(By.NAME, "code"), outlet_code)
    if driver.find_elements(By.NAME, "unitNo"):
        js_fill(driver, driver.find_element(By.NAME, "unitNo"), f"U{uniq}")
    if driver.find_elements(By.NAME, "postalCode"):
        js_fill(driver, driver.find_element(By.NAME, "postalCode"), "123456")

    # Region — button text is often "Select Region"
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
        preferred = (
            "Singapore West",
            "Singapore East",
            "Singapore North",
            "Singapore South",
            "QA Test Region",
        )
        for want in preferred:
            matches = driver.find_elements(
                By.XPATH,
                f"//*[@role='option' and contains(normalize-space(.), '{want}')]",
            )
            visible = [m for m in matches if m.is_displayed()]
            if visible:
                try:
                    driver.execute_script("arguments[0].click();", visible[0])
                    print(f"Outlet region selected: {want}")
                    region_set = True
                    break
                except Exception:
                    continue
        if not region_set:
            # first visible option — re-query each attempt to avoid stale refs
            for _ in range(8):
                opts = driver.find_elements(By.CSS_SELECTOR, "[role='option']")
                for o in opts:
                    try:
                        if not o.is_displayed():
                            continue
                        t = (o.text or "").strip()
                        if not t:
                            continue
                        driver.execute_script("arguments[0].click();", o)
                        print(f"Outlet region selected: {t[:60]}")
                        region_set = True
                        break
                    except Exception:
                        continue
                if region_set:
                    break
                time.sleep(0.3)
        time.sleep(0.3)
        try:
            driver.find_element(By.TAG_NAME, "body").click()
        except Exception:
            pass
    if not region_set:
        print("WARNING: Region may not be set")

    tas = driver.find_elements(By.TAG_NAME, "textarea")
    if tas:
        js_fill(driver, tas[0], f"QA Addr for franchise {uniq}")

    if driver.find_elements(By.NAME, "queueUrl"):
        js_fill(driver, driver.find_element(By.NAME, "queueUrl"), f"https://queue.sg/qa-{uniq}")

    # Opening hours — enable first day switch, then set From/To
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
        # From / To comboboxes appear in hours table
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
                # fallback first afternoon-ish option
                opt = driver.find_elements(By.XPATH, "//*[@role='option' and contains(., 'am') or contains(., 'pm')]")
            visible = [o for o in opt if o.is_displayed()]
            if visible:
                driver.execute_script("arguments[0].click();", visible[0])
                print(f"Opening hours {label} set")
            time.sleep(0.3)
            try:
                driver.find_element(By.TAG_NAME, "body").click()
            except Exception:
                pass
    except Exception as e:
        print(f"Opening hours setup soft-failed: {e}")

    # Starts from* — required for Publish
    start_btns = driver.find_elements(
        By.XPATH,
        "//*[contains(.,'Starts from')]/following::button[contains(.,'Pick a Date') or contains(.,'Pick a date')][1]",
    )
    if not start_btns:
        start_btns = driver.find_elements(By.XPATH, "//button[contains(.,'Pick a Date')]")
    if start_btns:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", start_btns[0])
        driver.execute_script("arguments[0].click();", start_btns[0])
        time.sleep(1)
        # pick today's date cell if available, else first enabled day button in calendar
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
        # click any visible time / Ok
        for ok in driver.find_elements(By.XPATH, "//button[contains(.,'Ok') or contains(.,'OK')]"):
            if ok.is_displayed():
                driver.execute_script("arguments[0].click();", ok)
                time.sleep(0.3)
                break
        print("Starts-from time picked")

    # Optional image if file input exists and local file available
    import os as _os

    img = "/Users/aungwaiwaithin/Downloads/test_image.png"
    if not _os.path.isfile(img):
        img = "/Users/aungwaiwaithin/Downloads/llk_abs.jpeg"
    file_inputs = driver.find_elements(By.XPATH, '//input[@type="file"]')
    if file_inputs and _os.path.isfile(img):
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

    # Prefer Publish if enabled; else Save as draft
    publish = [
        b
        for b in driver.find_elements(By.XPATH, "//button[contains(.,'Publish')]")
        if b.is_displayed()
    ]
    draft = [
        b
        for b in driver.find_elements(By.XPATH, "//button[contains(.,'Save as draft') or contains(.,'Save')]")
        if b.is_displayed()
    ]
    if publish and publish[-1].is_enabled():
        driver.execute_script("arguments[0].click();", publish[-1])
        print("Outlet submit clicked: Publish")
    elif draft:
        driver.execute_script("arguments[0].click();", draft[0])
        print("Outlet submit clicked: Save as draft (Publish disabled)")
    else:
        raise RuntimeError("No Publish/Save button on outlet form")
    time.sleep(5)

    # If still on /new, capture blockers
    if "/new" in (driver.current_url or ""):
        msgs = []
        for m in driver.find_elements(By.CSS_SELECTOR, "p, [role='alert']"):
            t = (m.text or "").strip()
            if t and any(k in t.lower() for k in ("required", "invalid", "must", "please")):
                msgs.append(t)
        print("Outlet still on /new. URL:", driver.current_url, "msgs:", msgs[:15])
        # last resort: draft again
        if draft:
            driver.execute_script("arguments[0].click();", draft[0])
            time.sleep(4)

    open_module(driver, MODULE_URLS["outlets"], wait_css='input[name="code"]')
    search_listing(driver, outlet_name)
    time.sleep(2)
    rows = driver.find_elements(By.XPATH, f"//table//tbody/tr[contains(., '{outlet_name}')]")
    if not rows:
        # try without filter refresh
        driver.get(MODULE_URLS["outlets"])
        time.sleep(2)
        search_listing(driver, outlet_name)
        time.sleep(2)
        rows = driver.find_elements(By.XPATH, f"//table//tbody/tr[contains(., '{outlet_name}')]")
    if not rows:
        raise RuntimeError(
            f"QA outlet create failed / not listed: {outlet_name}. "
            "Franchise create cannot proceed without an unassigned outlet."
        )
    _QA_CREATED_OUTLET = outlet_name
    print(f"Created unassigned QA outlet for franchise: {outlet_name}")
    return outlet_name


def _select_outlet_owned(preferred_outlet_name=None):
    """Outlet(s) Owned uses a Select button (often NOT role=combobox). Country is the combobox."""
    preferred = preferred_outlet_name or _QA_CREATED_OUTLET
    btns = driver.find_elements(
        By.XPATH, "//label[contains(.,'Outlet')]/following::button[normalize-space()='Select' or @role='combobox'][1]"
    )
    if not btns:
        btns = [
            b
            for b in driver.find_elements(By.XPATH, "//button")
            if b.text.strip() == "Select" and (b.get_attribute("role") or "") != "combobox"
        ]
    if not btns:
        btns = [b for b in driver.find_elements(By.XPATH, "//button") if b.text.strip() == "Select"]
    if not btns:
        raise RuntimeError("Outlet(s) Owned Select control not found")

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btns[0])
    driver.execute_script("arguments[0].click();", btns[0])
    time.sleep(1.2)

    body_txt = driver.find_element(By.TAG_NAME, "body").text
    if "No available outlets" in body_txt:
        driver.find_element(By.TAG_NAME, "body").click()
        raise RuntimeError(
            "No available outlets for Franchise entity. "
            "Create a new unassigned outlet first (_create_unassigned_qa_outlet)."
        )

    chosen = None
    options = driver.find_elements(
        By.CSS_SELECTOR, "[role='option'], [role='menuitemcheckbox'], [cmdk-item], li"
    )
    # Prefer exact QA outlet name
    if preferred:
        for o in options:
            try:
                if not o.is_displayed():
                    continue
                t = (o.text or "").strip()
                if preferred in t:
                    driver.execute_script("arguments[0].click();", o)
                    chosen = t
                    break
            except Exception:
                continue
    if not chosen:
        for o in options:
            try:
                if not o.is_displayed():
                    continue
                t = (o.text or "").strip()
                if not t or t.lower() == "select":
                    continue
                if t in ("Åland Islands", "Albania", "Algeria", "Singapore"):
                    continue
                if "No available" in t:
                    continue
                driver.execute_script("arguments[0].click();", o)
                chosen = t
                break
            except Exception:
                continue

    time.sleep(0.4)
    driver.find_element(By.TAG_NAME, "body").click()
    time.sleep(0.4)
    if not chosen:
        raise RuntimeError("Could not select an Outlet(s) Owned value")
    print(f"Outlet owned selected: {chosen[:80]}")
    return chosen


def _select_country_singapore():
    btns = driver.find_elements(
        By.XPATH, "//label[contains(.,'Country')]/following::button[@role='combobox'][1]"
    )
    if not btns:
        return False
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btns[0])
    driver.execute_script("arguments[0].click();", btns[0])
    time.sleep(1)
    for o in driver.find_elements(By.CSS_SELECTOR, "[role='option']"):
        try:
            if o.is_displayed() and (o.text or "").strip() == "Singapore":
                driver.execute_script("arguments[0].click();", o)
                time.sleep(0.4)
                print("Country selected: Singapore")
                return True
        except Exception:
            continue
    return False


def _fill_franchise_required_fields(uniq, franchise_name, email, outlet_name=None):
    from KskinCMS.cms_auth import js_fill

    js_fill(driver, driver.find_element(By.NAME, "email"), email)
    js_fill(driver, driver.find_element(By.NAME, "name"), franchise_name)
    js_fill(driver, driver.find_element(By.NAME, "franchiseEntities.0.title"), f"QA Ent {uniq}")
    js_fill(driver, driver.find_element(By.NAME, "franchiseEntities.0.entityNo"), f"UEN{uniq}")
    _select_outlet_owned(outlet_name)
    for n, v in [
        ("accountNo", f"ACC{uniq}"),
        ("accountHolderName", f"Holder {uniq}"),
        ("bankName", f"Bank {uniq}"),
        ("sortCode", f"SC{uniq}"),
        ("billingName", f"Bill {uniq}"),
        ("billingEmail", f"bill{uniq}@yopmail.com"),
        ("billingMobile", "91234567"),
        ("companyName", f"Co {uniq}"),
        ("postalCode", "123456"),
    ]:
        js_fill(driver, driver.find_element(By.NAME, n), v)
    js_fill(driver, driver.find_element(By.TAG_NAME, "textarea"), f"QA Addr {uniq}")
    _select_country_singapore()


def _submit_create_and_confirm(franchise_name):
    from KskinCMS.cms_auth import open_module, search_listing
    from KskinCMS.cms_config import MODULE_URLS

    create_btns = driver.find_elements(By.XPATH, "//button[contains(.,'Create')]")
    if create_btns:
        driver.execute_script("arguments[0].click();", create_btns[-1])
        time.sleep(5)
    if "/new" in (driver.current_url or ""):
        # retry country + create once
        _select_country_singapore()
        create_btns = driver.find_elements(By.XPATH, "//button[contains(.,'Create')]")
        if create_btns:
            driver.execute_script("arguments[0].click();", create_btns[-1])
            time.sleep(5)

    open_module(driver, MODULE_URLS["franchisee_accounts"], wait_css='input[name="code"]')
    search_listing(driver, franchise_name)
    time.sleep(2)
    rows = driver.find_elements(
        By.XPATH, f"//table//tbody/tr[contains(., '{franchise_name}')]"
    )
    ok = bool(rows)
    print(f"Create verified in listing for '{franchise_name}'? {ok}")
    return ok


def _create_qa_franchise_for_status():
    """Create unassigned outlet → franchise → used only for status toggle tests."""
    from KskinCMS.cms_config import MODULE_URLS

    uniq = str(int(time.time()))[-6:]
    qa_name = f"QA Status Fran {uniq}"
    outlet_name = _create_unassigned_qa_outlet(uniq)

    driver.get(MODULE_URLS["franchisee_accounts"] + "/new")
    time.sleep(3)
    wait_name("email")
    _fill_franchise_required_fields(
        uniq, qa_name, f"qa.status.{uniq}@yopmail.com", outlet_name=outlet_name
    )
    if not _submit_create_and_confirm(qa_name):
        raise RuntimeError(f"QA franchise create failed / not found in listing: {qa_name}")
    print(f"Created QA franchise for status tests: {qa_name}")
    return qa_name


def listing_active_inactive_action():
    """Create a new QA franchise, then ACTIVE → INACTIVE on that row only."""
    global _QA_STATUS_FRANCHISE
    from KskinCMS.cms_auth import open_module, toggle_row_status
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["franchisee_accounts"], wait_css='input[name="code"]')
    _QA_STATUS_FRANCHISE = _create_qa_franchise_for_status()
    ok = toggle_row_status(driver, _QA_STATUS_FRANCHISE, make_inactive=True)
    if ok:
        print("Test 5 : Changed NEW QA item to inactive successfully!")
    else:
        print("Changed to inactive status failed!")


def listing_inactive_active_action():
    """INACTIVE → ACTIVE on the same QA franchise created above."""
    from KskinCMS.cms_auth import open_module, toggle_row_status
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["franchisee_accounts"], wait_css='input[name="code"]')
    name = _QA_STATUS_FRANCHISE
    if not name:
        print("No QA franchise from prior step — creating one first")
        listing_active_inactive_action()
        name = _QA_STATUS_FRANCHISE
    ok = toggle_row_status(driver, name, make_inactive=False)
    if ok:
        print("Test 6 : Changed NEW QA item back to active successfully!")
    else:
        print("Changed to active status failed!")

def pagination_and_rows_per_page_actions():
    from KskinCMS.cms_config import MODULE_URLS
    from selenium.webdriver.support.ui import Select
    driver.get(MODULE_URLS["franchisee_accounts"])
    time.sleep(3)

    scroll_to_bottom()
    time.sleep(2)

    select = Select(driver.find_element(By.XPATH, franchise_path['row_per_page_select_box_path']))
    select.select_by_value('50')
    time.sleep(2)
    select = Select(driver.find_element(By.XPATH, franchise_path['row_per_page_select_box_path']))
    select.select_by_value('10')
    time.sleep(2)

    # Pagination only when > page size; currently ~10 items so page-2 may be absent
    page2 = driver.find_elements(By.XPATH, "//table//tfoot//*[normalize-space()='2']")
    if page2:
        page2[0].click()
        time.sleep(2)
        page1 = driver.find_elements(By.XPATH, "//table//tfoot//*[normalize-space()='1']")
        if page1:
            page1[0].click()
            time.sleep(2)
        print("Test 7 : Rows per page + pagination checked.")
    else:
        print("Test 7 : Rows per page checked (pagination N/A — single page of results).")



def create_new_franchise_account():
    """Validation + create happy path against current staging UI."""
    global _QA_CREATED_FRANCHISE
    from KskinCMS.cms_config import MODULE_URLS

    invalid_email_address_err_msg = 'Invalid email address'
    email_address_req_err_msg = 'Email is required'
    franchise_name_req_err_msg = 'Franchise name is required'

    driver.get(MODULE_URLS["franchisee_accounts"] + "/new")
    time.sleep(4)
    wait_name(franchise_path['email_address_name'])

    send_keys_by_name(franchise_path['email_address_name'], '123')
    time.sleep(1)
    if invalid_email_address_err_msg == get_text_by_xpath(franchise_path['invalid_email_err_msg_path']):
        print("Test 8 : Invalid email address error message : ", invalid_email_address_err_msg)

    clear_by_name(franchise_path['email_address_name'])
    time.sleep(1)
    if email_address_req_err_msg == get_text_by_xpath(franchise_path['req_email_err_msg_path']):
        print("Test 9 : Email address required error message : ", email_address_req_err_msg)

    uniq = str(int(time.time()))[-6:]
    fname = f"QA Franchise {uniq}"
    # Dependency: create unassigned outlet first (all existing outlets may already be owned)
    outlet_name = _create_unassigned_qa_outlet(uniq)

    driver.get(MODULE_URLS["franchisee_accounts"] + "/new")
    time.sleep(3)
    wait_name("email")
    # Re-check franchise name required quickly
    send_keys_by_name(franchise_path['franchise_name'], 'tmp')
    clear_by_name(franchise_path['franchise_name'])
    time.sleep(1)
    if franchise_name_req_err_msg == get_text_by_xpath(franchise_path['req_franchise_name_err_msg_path']):
        print("Test 10 : Franchise name required error message : ", franchise_name_req_err_msg)

    _fill_franchise_required_fields(
        uniq, fname, f"qa.franchise.{uniq}@yopmail.com", outlet_name=outlet_name
    )
    print("Test 13 : Outlet owned selected")
    ok = _submit_create_and_confirm(fname)
    if ok:
        _QA_CREATED_FRANCHISE = fname
        print(f"Test 28 : New Franchise Account is created successfully!! : {fname}")
    else:
        print("Something went wrong with new franchise account creation!")
        print("URL:", driver.current_url)


def view_back_created_acc_info():
    from KskinCMS.cms_auth import search_listing
    from KskinCMS.cms_config import MODULE_URLS
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.common.action_chains import ActionChains

    driver.get(MODULE_URLS["franchisee_accounts"])
    time.sleep(3)
    name = _QA_CREATED_FRANCHISE or _QA_STATUS_FRANCHISE
    if name:
        search_listing(driver, name)
        time.sleep(2)
    row = driver.find_element(By.CSS_SELECTOR, "table tbody tr:first-child")
    span = row.find_element(By.CSS_SELECTOR, ".actions-column > span, td:last-child .actions-column > span")
    ActionChains(driver).move_to_element(span).pause(0.2).click().perform()
    WebDriverWait(driver, 20).until(lambda d: d.find_elements(By.NAME, "email"))
    time.sleep(2)
    email = get_attribute_by_name(franchise_path['email_address_name'])
    fname = get_attribute_by_name(franchise_path['franchise_name'])
    print("View email:", email)
    print("View franchise name:", fname)
    if email and fname:
        print("Test 29 : View/edit form opened and values readable successfully!")
    else:
        print("View back failed — empty fields")
    driver.get(MODULE_URLS["franchisee_accounts"])
    time.sleep(2)


def edit_franchise_account():
    from KskinCMS.cms_auth import js_fill, search_listing
    from KskinCMS.cms_config import MODULE_URLS
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.common.action_chains import ActionChains

    global _QA_CREATED_FRANCHISE
    driver.get(MODULE_URLS["franchisee_accounts"])
    time.sleep(3)
    name = _QA_CREATED_FRANCHISE or _QA_STATUS_FRANCHISE
    if name:
        search_listing(driver, name)
        time.sleep(2)
    row = driver.find_element(By.CSS_SELECTOR, "table tbody tr:first-child")
    span = row.find_element(By.CSS_SELECTOR, ".actions-column > span, td:last-child .actions-column > span")
    ActionChains(driver).move_to_element(span).pause(0.2).click().perform()
    WebDriverWait(driver, 20).until(lambda d: d.find_elements(By.NAME, "email"))
    time.sleep(2)
    uniq = str(int(time.time()))[-5:]
    updated = f"Updated Franchise {uniq}"
    js_fill(driver, driver.find_element(By.NAME, franchise_path['franchise_name']), updated)
    btns = driver.find_elements(By.XPATH, "//button[contains(.,'Save') or contains(.,'Update') or contains(.,'Publish')]")
    if btns:
        driver.execute_script("arguments[0].click();", btns[-1])
        time.sleep(4)
    driver.get(MODULE_URLS["franchisee_accounts"])
    time.sleep(3)
    search_listing(driver, updated)
    time.sleep(2)
    result = get_text_by_xpath(franchise_path['name_search_result_path'])
    print("Edit search result:", result)
    if updated in result:
        _QA_CREATED_FRANCHISE = updated
        print("Test 30 : Edit franchise account successful!")
    else:
        print("Edit franchise account failed!")


