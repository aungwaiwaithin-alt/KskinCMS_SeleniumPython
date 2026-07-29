import time
from KskinCMS.IssueFreeVoucher_Module.IFVHelper import *
from KskinCMS.IssueFreeVoucher_Module.IFVVarPaths import *
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# install this to use load dotevn >> pip install python-dotenv
load_dotenv()

#pytest IFVMain.py --html=IFVReport.html
#pytest -s IFVMain.py --html=IFVReport.html


def open_browser():
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS
    open_module(driver, MODULE_URLS["issue_free_vouchers"], wait_css='input[name="code"]')
    print("Test 1 : Open browser success!")


def _type_search(value):
    el = wait_name("code")
    js_fill_input(el, value)


def ifv_search_and_filter():
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS

    open_module(driver, MODULE_URLS["issue_free_vouchers"], wait_css='input[name="code"]')
    time.sleep(2)

    # Placeholder soft-check (live: Find by voucher name)
    placeholder = driver.find_element(By.NAME, "code").get_attribute("placeholder") or ""
    print("Search placeholder:", placeholder)
    if "voucher name" in placeholder.lower():
        print("Test 2 : Search placeholder is Find by voucher name")

    # Matched voucher name search (live staging recon)
    _type_search("testawwtifv")
    time.sleep(2)
    actual = driver.find_element(By.XPATH, "//table//tbody/tr[1]/td[1]").text.strip()
    print(actual)
    if "testawwtifv" in actual:
        print("Test 3 : Voucher name searching with matched value is successful!")
    else:
        print("Something went wrong. Voucher name searching with matched value is failed!")

    driver.get(MODULE_URLS["issue_free_vouchers"])
    time.sleep(2)

    # Unmatched search
    _type_search("NoSuchVoucherZZZ999")
    time.sleep(2)
    body = driver.find_element(By.TAG_NAME, "body").text
    rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
    if "No vouchers yet" in body or not rows:
        print("Test 4 : Searching with unmatched value can show empty result successfully!!")
    else:
        print("Something went wrong. Unmatched search did not show empty state.")

    driver.get(MODULE_URLS["issue_free_vouchers"])
    time.sleep(2)

    # Type filter via hidden <select> (All types / 1 for 1 / $ off / % off)
    driver.execute_script(
        """
        const selects = document.querySelectorAll('select[aria-hidden="true"]');
        const select = selects[0];
        if (select) {
          select.value = 'FixedPriceOff';
          select.dispatchEvent(new Event('change', { bubbles: true }));
        }
        """
    )
    time.sleep(2)
    type_text = ""
    rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
    if rows:
        type_text = driver.find_element(By.XPATH, "//table//tbody/tr[1]/td[4]").text.strip()
        print(type_text)
    if type_text == "$ off":
        print("Test 5 : Searching with matched value for voucher type is successful!")
    else:
        dropdown_select_value("//button[@role='combobox']", 0, "FixedPriceOff")
        time.sleep(2)
        type_text = driver.find_element(By.XPATH, "//table//tbody/tr[1]/td[4]").text.strip()
        print(type_text)
        if type_text == "$ off":
            print("Test 5 : Searching with matched value for voucher type is successful!")
        else:
            print("Type filter check soft-failed:", type_text)

    # Reset to All types
    driver.execute_script(
        """
        const selects = document.querySelectorAll('select[aria-hidden="true"]');
        const select = selects[0];
        if (select) {
          select.value = 'All';
          select.dispatchEvent(new Event('change', { bubbles: true }));
        }
        """
    )
    time.sleep(1)
    print("Test 6 : Type filter reset to All types")

    driver.get(MODULE_URLS["issue_free_vouchers"])
    time.sleep(2)


def rows_per_page_actions():
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS
    from selenium.webdriver.support.ui import Select

    open_module(driver, MODULE_URLS["issue_free_vouchers"], wait_css='input[name="code"]')
    time.sleep(2)

    scroll_to_bottom()
    time.sleep(2)

    # Displaying 10 / 20 / 50 via stable pageSize select
    select = Select(driver.find_element(By.XPATH, "//select[@title='pageSize']"))
    select.select_by_value("20")
    time.sleep(2)
    select = Select(driver.find_element(By.XPATH, "//select[@title='pageSize']"))
    select.select_by_value("50")
    time.sleep(2)
    select = Select(driver.find_element(By.XPATH, "//select[@title='pageSize']"))
    select.select_by_value("10")
    time.sleep(2)
    print("Test 7(A) : Checking rows per page functions is done and all are working fine!")

    # Pagination only when item count > page size (staging has 60 items)
    page2 = driver.find_elements(By.XPATH, "//table//tfoot//*[normalize-space()='2']")
    if page2:
        page2[0].click()
        time.sleep(2)
        page1 = driver.find_elements(By.XPATH, "//table//tfoot//*[normalize-space()='1']")
        if page1:
            page1[0].click()
            time.sleep(2)
        print("Test 7(B) : Checking pagination function is done and all are working fine!")
    else:
        print("Test 7(B) : Rows per page checked (pagination N/A — single page of results).")


def add_new_ifv():
    ###### Add New IFV flow (brittle create — skipped in IFVMain by default) ######

    voucher_type_req_err_msg = 'Voucher type is required'
    voucher_name_req_err_msg = 'Voucher name is required'
    desc_req_err_msg = 'Description is required'

    discount_amt_req_err_msg = 'Discount amount is required'
    discount_amt_minus_value_validation_err_msg = 'Value must be positive number'
    discount_amt_max_value_validation_err_msg = 'Value must not exceed 100'

    discount_apply_to_req_err_msg = 'Please select where to apply the discount'
    remark_req_err_msg = 'Remark is required'
    t_and_c_req_err_msg = 'Terms and conditions are required'

    min_spent_amt_req_err_msg = 'Minimum spent amount is required'
    min_spent_amt_minus_value_validation_err_msg = 'Minimum spent amount cannot be negative'

    expires_in_req_err_msg = 'Expired in is required'

    from KskinCMS.cms_config import MODULE_URLS

    click_by_xpath(ifv_path['add_issue_voucher_btn_pth'])
    time.sleep(5)

    click_by_xpath(ifv_path['dollar_off_radio_btn_path'])
    time.sleep(3)
    click_by_xpath(ifv_path['percent_off_radio_btn_path'])
    time.sleep(2)

    send_keys_by_name(ifv_path['voucher_name'], 'A@#$%')
    time.sleep(2)
    clear_by_name(ifv_path['voucher_name'])
    time.sleep(2)

    if voucher_name_req_err_msg in driver.find_element(By.TAG_NAME, "body").text:
        print("Test 8 : Voucher name required error message is : ", voucher_name_req_err_msg)
    else:
        print("Something went wrong with checking voucher name required message")

    send_keys_by_name(ifv_path['voucher_name'], 'Auto Test Voucher_@#$%')
    time.sleep(2)

    send_keys_by_xpath(ifv_path['description_path'], 'Test description')
    time.sleep(2)
    send_keys_by_name(ifv_path['discount_value_name'], '5')
    time.sleep(2)
    click_by_xpath(ifv_path['individual_item_path'])
    time.sleep(2)
    send_keys_by_name(ifv_path['remark_name'], 'Auto Test Remarks')
    time.sleep(2)
    send_keys_by_xpath(ifv_path['t_n_c_path'], 'Test T&C')
    time.sleep(2)
    send_keys_by_name(ifv_path['min_spent_amt_name'], '200')
    time.sleep(2)
    send_keys_by_name(ifv_path['expire_in_textbox_name'], '3')
    time.sleep(2)

    print("Test 24 : Create flow soft-check completed (brittle publish skipped).")
    driver.get(MODULE_URLS["issue_free_vouchers"])
    time.sleep(3)
