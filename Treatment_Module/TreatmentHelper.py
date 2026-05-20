from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import glob
import subprocess

driver = webdriver.Chrome()

# #Scroll back to top of the page to update data
#
#     driver.execute_script("window.scrollTo(0, 0);")
#     time.sleep(3)
#     print('Scrolled to the top of the page successfully!')

def scroll_by_pixel():
    driver.execute_script("window.scrollBy(0, 500);")  # Scroll down by 500 pixels
    driver.execute_script("window.scrollBy(0, -500);") # Scroll up by 500 pixels

def scroll_to_bottom():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

def scroll_to_top():
    driver.execute_script("window.scrollTo(0, 0);")

def scroll_to_specified_element(xpath):
    element = driver.find_element(By.XPATH, xpath)
    driver.execute_script("arguments[0].scrollIntoView(true);", element)

def smooth_scroll_to_element(xpath):
    element = driver.find_element(By.XPATH, xpath)
    driver.execute_script("""
    arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});
""", element)

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
    #Useful when the element is inside a scrollable section, not the whole window
    scrollable_div = driver.find_element(By.XPATH, scrollable_div_xpath)
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)

def infinite_scroll():
    #Loop until bottom
    #For pages that load content as you scroll (e.g., social feeds).

    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # wait for page to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height



def get_attribute_by_xpath(xpath):
    return driver.find_element(By.XPATH, xpath).get_attribute("value")

def get_attribute_by_name(name):
    return driver.find_element(By.NAME, name).get_attribute("value")

def click_by_xpath(xpath):
    driver.find_element(By.XPATH, xpath).click()

def send_keys_by_xpath(xpath,value):
    driver.find_element(By.XPATH, xpath).send_keys(value)

def click_by_name(name):
    driver.find_element(By.NAME, name).click()

def send_keys_by_name(name,value):
    driver.find_element(By.NAME, name).send_keys(value)

def click_by_id(id):
    driver.find_element(By.ID, id).click()

def send_keys_by_id(id,value):
    driver.find_element(By.ID, id).send_keys(value)

def get_text_by_xpath(xpath):
    return driver.find_element(By.XPATH, xpath).text

def get_text_by_name(name):
    return driver.find_element(By.NAME, name).text

def clear_by_name(name):

    element = driver.find_element(By.NAME, name)

    # Click and clear via keys
    # element.click()
    # element.send_keys(Keys.CONTROL + "a")
    # element.send_keys(Keys.DELETE)
    # time.sleep(3)

    # Click and focus the input
    element.click()

    # Get current text length
    current_value = element.get_attribute("value")
    text_length = len(current_value)

    # Send backspace keys to delete characters one by one
    for _ in range(text_length):
        element.send_keys(Keys.BACKSPACE)

    # Trigger input and change events to simulate user interaction
    driver.execute_script("""
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
    """, element)

    # Remove query params from URL
    driver.execute_script("window.history.pushState({}, document.title, window.location.pathname);")

    # Optional: press Enter to trigger search/refresh
    #element.send_keys(Keys.ENTER)

    # Wait for results
    time.sleep(3)

def clear_by_xpath(xpath):
    element = driver.find_element(By.XPATH, xpath)

    # Click and clear via keys
    element.click()
    element.send_keys(Keys.COMMAND + "a")
    element.send_keys(Keys.DELETE)

    # # Fully clear via JS and trigger input events
    # driver.execute_script("""
    #     arguments[0].value = '';
    #     arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
    #     arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
    # """, element)
    #
    # # Remove `?code=...` from URL via JS router
    # driver.execute_script("window.history.pushState({}, document.title, window.location.pathname);")
    #
    # # Optional: trigger search or refresh action
    # element.send_keys(Keys.ENTER)
    #
    # # Wait to allow data to refresh
    # time.sleep(3)

def export_fun_by_xpath(xpath):
    # Click on the "Export" button
    export_button = driver.find_element(By.XPATH, xpath)
    export_button.click()

    # Wait for the download to complete
    time.sleep(5)  # Adjust based on file size and internet speed

    # Set the downloads directory path
    download_path = os.path.expanduser("/Users/aungwaiwaithin/Downloads")  # Adjust path if needed

    # Get the latest downloaded file
    list_of_files = glob.glob(os.path.join(download_path, "*.xlsx"))  # Searching for Excel files
    latest_file = max(list_of_files, key=os.path.getctime)

    # Open the file using the default application
    subprocess.run(["open", latest_file])  # macOS
    # subprocess.run(["xdg-open", latest_file])  # Linux
    # os.startfile(latest_file)  # Windows

    print(f"Downloaded file opened: {latest_file}")


#Explaination >>
# •	Here we find the invisible <select> tag using its style.
# •	This step is optional — it just proves we found it.
# •	We’re not using this select_id later; it’s for confirmation/debugging.
#Explaination >>
# •	document.querySelector('select[aria-hidden="true"]'):
# •	Finds the hidden dropdown.
# •	We use the aria-hidden="true" attribute to locate it precisely.
# •	select.value = 'b35b0546-0d8d-4f68-8e43-cfd204548828';:
# •	Sets the internal value of the dropdown.
# •	This is like selecting an option manually.
# •	select.dispatchEvent(new Event('change', { bubbles: true }));:
# •	Triggers the change event.
# •	This is critical because many React/JS apps only update UI when that event fires.

#Use querySelectorAll() and pick the right index for "both dropdowns are using the same aria-hidden="true" selector case :

def refresh_search_result():
    current_url = driver.current_url
    base_url = current_url.split("?")[0]
    driver.get(base_url)

    driver.refresh()
    time.sleep(3)


# Explanation:
#
# //table//tbody//tr → select rows in the table body.
#
# [td//span[text()='AungWaiWaiThin']] → pick the row where a <span> has the exact text AungWaiWaiThin.
#
# //td[last()] → go to the last <td> of that row (where the action buttons are).
#
# //span[contains(@class,'rounded-full')][1] → select the first rounded button, which is the pencil (edit) icon.

#To make "exact_text_to_pick_row" variable as dynamic in my XPath, you need to use string formatting (f-string or .format()).

# Wait for the Edit icon in the row containing "Test Outlet Name" (Second way, can click to specific item. This is better)
def click_edit_icon(exact_text_to_pick_row):
    edit_icon = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
        By.XPATH,
        f"//table//tbody//tr[td//span[text()='{exact_text_to_pick_row}']]//td[last()]//span[contains(@class,'rounded-full')][1]"
    )))
    edit_icon.click()
    time.sleep(5)
# 🧩 1. span[text()='{exact_text_to_pick_row}']
#
# Meaning:
# •	This looks specifically for a <span> element whose direct text content exactly matches {exact_text_to_pick_row}.
# •	Example: <span>Apple</span>
# Usage:
# You use this when:
# •	The value you want to match is inside a <span> tag directly.
# •	You know the structure is <td><span>text</span></td>.

def click_edit_icon_for_sec_column(second_col_value):
    edit_icon = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
        By.XPATH,
        f"//table//tbody//tr[td[2][normalize-space()='{second_col_value}']]//td[last()]//span[contains(@class,'rounded-full')][1]"
    )))
    edit_icon.click()
    time.sleep(5)
# 🧩 2. [normalize-space()='{second_col_value}']
#
# Meaning:
# •	This matches an element (like a <td> or <span>) whose text — after trimming spaces — equals the given value.
# •	The normalize-space() function:
# •	Removes leading/trailing spaces.
# •	Replaces multiple spaces between words with a single space.
# Example : <td>  Apple   </td>
# Usage:
# You use this when:
# •	You want to match text even if there are extra spaces.
# •	Or when you’re matching directly on a <td> (cell), not necessarily a <span> inside it.

def clear_dob_value():
    svg_x = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//label[@for='dob']/following-sibling::fieldset[1]//*[name()='svg']")
        )
    )
    driver.execute_script("""
        const el = arguments[0];
        el.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
        el.dispatchEvent(new MouseEvent('mouseup',   { bubbles: true }));
        el.dispatchEvent(new MouseEvent('click',     { bubbles: true }));
    """, svg_x)

def dropdown_select_value(xpath, index, value):
    dropdown_button = driver.find_element(By.XPATH, xpath)
    dropdown_button.click()
    time.sleep(2)

    driver.execute_script("""
        const selects = document.querySelectorAll('select[aria-hidden="true"]');
        const select = selects[arguments[0]];
        if (select) {
            select.value = arguments[1];
            select.dispatchEvent(new Event('change', { bubbles: true }));
        }
    """, index, value)

    time.sleep(2)

#TIP:
# 1.	document.querySelectorAll(...) returns a list – You cannot access it directly with [x] inside JavaScript as you intended if x is Python. You must pass it via arguments[0] in execute_script.
# 2.	value is a Python variable – You need to pass it into the JS context via arguments[1].
# 3.	Hardcoded delay (time.sleep) – It’s better to use explicit waits (e.g. WebDriverWait) for real automation, but sleep is okay for quick tests.


