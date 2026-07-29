from selenium import webdriver
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from KskinCMS.cms_auth import get_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import glob
import subprocess

driver = get_driver()  # shared one Chrome; login once via open_module/login_cms


def wait_xpath(xpath, timeout=20):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )


def wait_clickable_xpath(xpath, timeout=20):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )


def wait_name(name, timeout=20):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.NAME, name))
    )


def js_fill_input(el, value):
    """React-controlled inputs need native value setter + input/change events."""
    driver.execute_script(
        """
        const input = arguments[0];
        const value = arguments[1];
        const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        setter.call(input, '');
        input.dispatchEvent(new Event('input', { bubbles: true }));
        setter.call(input, value);
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        """,
        el,
        value,
    )


def scroll_by_pixel():
    driver.execute_script("window.scrollBy(0, 500);")
    driver.execute_script("window.scrollBy(0, -500);")


def scroll_to_bottom():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def scroll_to_top():
    driver.execute_script("window.scrollTo(0, 0);")


def scroll_to_specified_element(xpath):
    element = driver.find_element(By.XPATH, xpath)
    driver.execute_script("arguments[0].scrollIntoView(true);", element)


def smooth_scroll_to_element(xpath):
    element = driver.find_element(By.XPATH, xpath)
    driver.execute_script(
        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
        element,
    )


def scroll_down_using_page_down():
    body = driver.find_element(By.TAG_NAME, "body")
    body.send_keys(Keys.PAGE_DOWN)


def scroll_to_bottom_by_using_end():
    body = driver.find_element(By.TAG_NAME, "body")
    body.send_keys(Keys.END)


def scroll_up_by_using_home():
    body = driver.find_element(By.TAG_NAME, "body")
    body.send_keys(Keys.HOME)


def scroll_using_actionChains(xpath):
    from selenium.webdriver.common.action_chains import ActionChains

    element = driver.find_element(By.XPATH, xpath)
    ActionChains(driver).move_to_element(element).perform()


def scroll_in_a_scrollable_div_or_container(scrollable_div_xpath):
    scrollable_div = driver.find_element(By.XPATH, scrollable_div_xpath)
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)


def infinite_scroll():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def get_attribute_by_xpath(xpath):
    return wait_xpath(xpath).get_attribute("value")


def get_attribute_by_name(name):
    return wait_name(name).get_attribute("value")


def click_by_xpath(xpath):
    el = wait_xpath(xpath)
    try:
        wait_clickable_xpath(xpath, timeout=5).click()
    except Exception:
        driver.execute_script("arguments[0].click();", el)


def send_keys_by_xpath(xpath, value):
    wait_xpath(xpath).send_keys(value)


def click_by_name(name):
    wait_name(name).click()


def send_keys_by_name(name, value):
    js_fill_input(wait_name(name), value)


def click_by_id(id):
    driver.find_element(By.ID, id).click()


def send_keys_by_id(id, value):
    driver.find_element(By.ID, id).send_keys(value)


def get_text_by_xpath(xpath):
    return wait_xpath(xpath).text


def get_text_by_name(name):
    return driver.find_element(By.NAME, name).text


def clear_by_name(name):
    element = wait_name(name)
    driver.execute_script(
        """
        const input = arguments[0];
        const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        setter.call(input, '');
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.blur();
        """,
        element,
    )
    driver.execute_script("window.history.pushState({}, document.title, window.location.pathname);")
    time.sleep(2)


def clear_by_xpath(xpath):
    element = driver.find_element(By.XPATH, xpath)
    element.click()
    element.send_keys(Keys.COMMAND + "a")
    element.send_keys(Keys.DELETE)


def export_fun_by_xpath(xpath):
    export_button = driver.find_element(By.XPATH, xpath)
    export_button.click()
    time.sleep(5)
    download_path = os.path.expanduser("/Users/aungwaiwaithin/Downloads")
    list_of_files = glob.glob(os.path.join(download_path, "*.xlsx"))
    latest_file = max(list_of_files, key=os.path.getctime)
    subprocess.run(["open", latest_file])
    print(f"Downloaded file opened: {latest_file}")


def refresh_search_result():
    current_url = driver.current_url
    base_url = current_url.split("?")[0]
    driver.get(base_url)
    driver.refresh()
    time.sleep(5)


def click_edit_icon(exact_text_to_pick_row):
    edit_icon = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
        By.XPATH,
        f"//table//tbody//tr[td//span[text()='{exact_text_to_pick_row}']]//td[last()]//span[contains(@class,'rounded-full')][1]"
    )))
    edit_icon.click()
    time.sleep(5)


def dropdown_select_value(xpath, index, value):
    dropdown_button = driver.find_element(By.XPATH, xpath)
    dropdown_button.click()
    time.sleep(2)
    driver.execute_script(
        """
        const selects = document.querySelectorAll('select[aria-hidden="true"]');
        const select = selects[arguments[0]];
        if (select) {
            select.value = arguments[1];
            select.dispatchEvent(new Event('change', { bubbles: true }));
        }
        """,
        index,
        value,
    )
    time.sleep(2)
