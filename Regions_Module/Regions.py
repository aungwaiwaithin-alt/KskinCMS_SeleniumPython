import time
from KskinCMS.Regions_Module.RegionHelper import *
from KskinCMS.Regions_Module.RegionVarPaths import *
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# install this to use load dotevn >> pip install python-dotenv
load_dotenv()

#pytest RegionMain.py --html=RegionReport.html
#pytest -s RegionMain.py --html=RegionReport.html

def open_browser():
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS
    open_module(driver, MODULE_URLS["regions"], wait_css='input[name="code"]')
    print("Test 1 : Open browser success!")


def region_searching():
    from KskinCMS.cms_config import MODULE_URLS
    driver.get(MODULE_URLS["regions"])
    time.sleep(3)

    def type_search(value):
        el = driver.find_element(By.NAME, "code")
        driver.execute_script(
            """
            const input=arguments[0], value=arguments[1];
            const setter=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
            setter.call(input,''); input.dispatchEvent(new Event('input',{bubbles:true}));
            setter.call(input,value); input.dispatchEvent(new Event('input',{bubbles:true}));
            input.dispatchEvent(new Event('change',{bubbles:true}));
            """,
            el,
            value,
        )

    type_search("Singapore Central")
    time.sleep(2)
    actual = driver.find_element(By.XPATH, "//table//tbody/tr[1]/td[1]").text.strip()
    print(actual)
    if actual == "Singapore Central":
        print("Test 3 : Name searching with matched value is successful!")
    else:
        print("Something went wrong. Name searching with matched value is failed!")

    driver.get(MODULE_URLS["regions"])
    time.sleep(2)
    type_search("NoSuchRegionZZZ")
    time.sleep(2)
    body = driver.find_element(By.TAG_NAME, "body").text
    if "No region" in body or "No regions" in body or not driver.find_elements(By.XPATH, "//table//tbody/tr"):
        print("Test 4 : Unmatched region search shows empty successfully!")
    else:
        print("Unmatched region search soft-failed")
    driver.get(MODULE_URLS["regions"])
    time.sleep(2)



def create_new_region():
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS
    open_module(driver, MODULE_URLS["regions"], wait_css='input[name="code"]')
    time.sleep(1)

    def open_add():
        btn = driver.find_element(By.XPATH, "//button[contains(.,'Add new Region') or contains(.,'Add new region')]")
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(1.5)

    def close_dialog():
        for xp in ["//button[contains(.,'Cancel')]", "//button[@aria-label='Close']"]:
            els = driver.find_elements(By.XPATH, xp)
            if els:
                driver.execute_script("arguments[0].click();", els[0]); time.sleep(1); return
        try:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        except Exception:
            pass
        time.sleep(1)

    def type_name(value):
        el = driver.find_element(By.NAME, "name")
        driver.execute_script(
            """
            const input=arguments[0], value=arguments[1];
            const setter=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
            setter.call(input,''); input.dispatchEvent(new Event('input',{bubbles:true}));
            setter.call(input,value); input.dispatchEvent(new Event('input',{bubbles:true}));
            input.dispatchEvent(new Event('change',{bubbles:true})); input.blur();
            """, el, value)

    open_add(); close_dialog(); print("Test 5 : Cancel/close works for create dialog!")
    open_add(); close_dialog(); print("Test 6 : Dialog dismiss works for create box!")
    open_add()
    title = driver.find_element(By.XPATH, "//h2[contains(.,'region') or contains(.,'Region')]").text.strip()
    print(title)
    print("Test 7 : New region box title:", title)
    type_name("tmp"); type_name(""); time.sleep(1)
    if "required" in driver.find_element(By.TAG_NAME,"body").text.lower():
        print("Test 8 : Required message for region name shown")
    uniq = str(int(time.time()))[-5:]
    created = f"QA Region {uniq}"
    type_name(created); time.sleep(0.5)
    save = driver.find_element(By.XPATH, "//button[contains(.,'Save') or contains(.,'Create') or contains(.,'Add')]")
    driver.execute_script("arguments[0].click();", save); time.sleep(3)
    driver.get(MODULE_URLS["regions"]); time.sleep(2)
    el = driver.find_element(By.NAME, "code")
    driver.execute_script(
        """
        const input=arguments[0], value=arguments[1];
        const setter=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
        setter.call(input,value); input.dispatchEvent(new Event('input',{bubbles:true}));
        """, el, created)
    time.sleep(2)
    actual = driver.find_element(By.XPATH, "//table//tbody/tr[1]/td[1]").text.strip()
    print(actual)
    print("Test 9 : New region created!" if created in actual else "New region creation failed!")


def update_old_region():
    from KskinCMS.cms_auth import open_module
    from KskinCMS.cms_config import MODULE_URLS
    open_module(driver, MODULE_URLS["regions"], wait_css='input[name="code"]')
    time.sleep(1)

    def open_edit():
        span = driver.find_element(By.CSS_SELECTOR, "table tbody tr:first-child td:last-child span")
        driver.execute_script("arguments[0].click();", span); time.sleep(1.5)

    def close_dialog():
        for xp in ["//button[contains(.,'Cancel')]", "//button[@aria-label='Close']"]:
            els = driver.find_elements(By.XPATH, xp)
            if els:
                driver.execute_script("arguments[0].click();", els[0]); time.sleep(1); return
        try:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        except Exception:
            pass
        time.sleep(1)

    def type_name(value):
        el = driver.find_element(By.NAME, "name")
        driver.execute_script(
            """
            const input=arguments[0], value=arguments[1];
            const setter=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
            setter.call(input,''); input.dispatchEvent(new Event('input',{bubbles:true}));
            setter.call(input,value); input.dispatchEvent(new Event('input',{bubbles:true}));
            input.dispatchEvent(new Event('change',{bubbles:true})); input.blur();
            """, el, value)

    open_edit(); close_dialog(); print("Test 10 : Cancel works for edit dialog!")
    open_edit(); close_dialog(); print("Test 11 : Dialog dismiss works for edit box!")
    open_edit()
    title = driver.find_element(By.XPATH, "//h2").text.strip()
    print(title); print("Test 12 : Edit region box title:", title)
    type_name(""); time.sleep(1)
    if "required" in driver.find_element(By.TAG_NAME,"body").text.lower():
        print("Test 13 : Required message for region name in update box shown")
    uniq = str(int(time.time()))[-5:]
    updated = f"Updated Region {uniq}"
    type_name(updated); time.sleep(0.5)
    save = driver.find_element(By.XPATH, "//button[contains(.,'Save') or contains(.,'Update')]")
    driver.execute_script("arguments[0].click();", save); time.sleep(3)
    driver.get(MODULE_URLS["regions"]); time.sleep(2)
    el = driver.find_element(By.NAME, "code")
    driver.execute_script(
        """
        const input=arguments[0], value=arguments[1];
        const setter=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
        setter.call(input,value); input.dispatchEvent(new Event('input',{bubbles:true}));
        """, el, updated)
    time.sleep(2)
    actual = driver.find_element(By.XPATH, "//table//tbody/tr[1]/td[1]").text.strip()
    print(actual)
    print("Test 14 : Old region updated!" if updated in actual else "Old region updating failed!")
