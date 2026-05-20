import time

from KskinCMSHelper import *
from KskinCMSVarPaths import *
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# install this to use load dotevn >> pip install python-dotenv
load_dotenv()

#pytest TherapistMain.py --html=TherapistReport.html
#pytest -s TherapistMain.py --html=TherapistReport.html

def open_browser():
    driver.get("https://staging.d1xlt4loftsg5g.amplifyapp.com/")
    time.sleep(5)
    driver.maximize_window()
    print("Test 1 : Open browser success!")
    time.sleep(3)


def outlets_search_and_filters():

#Go to outlet listing
    click_by_xpath(outlets_path['outlet_mgmt_menu_path'])
    time.sleep(3)
    click_by_xpath(outlets_path['outlet_submenu_path'])
    time.sleep(5)
    print("Test 2 : Navigated to outlet listing successful!")

#Search functions
    #Outlet name searching Matched case
    send_keys_by_xpath(outlets_path['outlet_searchbox_path'], 'Chinatown')
    time.sleep(2)
    outlet_name_search_result=get_text_by_xpath(outlets_path['outlet_name_searchresult_path'])
    print(outlet_name_search_result)
    if outlet_name_search_result=="Chinatown Point (QA Test)":
        print("Test 3 : Searching with matched value is successful!")
    else:
        print("Something went wrong. Searching with matched value is failed!")

    driver.find_element(By.XPATH,outlets_path['outlet_searchbox_path']).clear()
    time.sleep(5)

    current_url = driver.current_url
    base_url = current_url.split("?")[0]
    driver.get(base_url)

    driver.refresh()
    time.sleep(5)

#Outlet name searching UnMatched case
    send_keys_by_xpath(outlets_path['outlet_searchbox_path'], '520aa')
    time.sleep(2)
    outlet_name_noserach_result=get_text_by_xpath(outlets_path['outlet_name_nosearchresult_path'])
    if outlet_name_noserach_result=="No outlets yet.":
        print("Test 4 : Searching with unmatched value can show empty result successfully")
    else:
        print("Something went wrong.")

    driver.find_element(By.XPATH,outlets_path['outlet_searchbox_path']).clear()
    time.sleep(5)

    current_url = driver.current_url
    base_url = current_url.split("?")[0]
    driver.get(base_url)

    driver.refresh()
    time.sleep(5)

#Region filter case (Dropdown)

    want_to_select_region_value='ce9d03da-bfa3-42a4-b432-121a2c7b1631'
    dropdown_select_value("//button[@role='combobox']",0,want_to_select_region_value)
    time.sleep(2)

    region_search_result=get_text_by_xpath(outlets_path['region_searchresult_path'])
    print(region_search_result)
    if region_search_result=="Singapore West":
        print("Test 5 : Searching with matched value for region is successful!")
    else:
        print("Something went wrong.")
    time.sleep(2)
#set back to default state region value
    dropdown_select_value("//button[@role='combobox']",0,'All')
    time.sleep(2)

#Status filter case (Dropdown)

    dropdown_select_value(outlets_path['status_dropdown_path'],1,'Active')

    status_search_result=get_text_by_xpath(outlets_path['status_searchresult_path'])

    if status_search_result=="ACTIVE":
        print("Test 6 : Searching with Inactive status is successful!")
    else:
        print("Something went wrong with status searching.")
    time.sleep(2)

#set back to default state status value
    dropdown_select_value(outlets_path['status_dropdown_path'],1,'All')
    time.sleep(2)


def create_new_outlet():
###### Create New Outlet flow  ######

    outlet_name_err_msg='Outlet name is required'
    outlet_code_err_msg='Outlet code is required'
    unit_number_err_msg='Unit number is required'
    postal_code_err_msg='Postal code is required'
    address_box_err_msg='Address is required'
    invalid_url_err_msg='Please enter a valid URL.'

#Click create new button
    click_by_xpath(outlets_path['create_new_outlet_button_path'])
    time.sleep(6)

#Outlet Name field validation
    send_keys_by_name(outlets_path['outlet_name_n'],'123 $#@ wai')
    time.sleep(2)
    clear_by_name(outlets_path['outlet_name_n'])
    time.sleep(2)

    if outlet_name_err_msg==get_text_by_xpath(outlets_path['outlet_name_required_path']):
        print("Test 7 : Outlet name required message : ", outlet_name_err_msg)
    else :
        print("Something went wrong with checking outlet name required message")

    send_keys_by_name(outlets_path['outlet_name_n'],'Wai Wai Auto Test 123 !@# ')
    time.sleep(2)

# Click on checkbox
    click_by_xpath(outlets_path['HQ_checkbox_path'])
    time.sleep(2)


#Outlet Code field validation
    send_keys_by_name(outlets_path['outlet_code_n'],'@#$%^&sdfg2345')
    time.sleep(2)
    clear_by_name(outlets_path['outlet_code_n'])
    time.sleep(2)

    if outlet_code_err_msg==get_text_by_xpath(outlets_path['outlet_code_required_path']):
        print("Test 8 : Outlet code required message : ", outlet_code_err_msg)
    else :
        print("Something went wrong with checking outlet code required message")

    send_keys_by_name(outlets_path['outlet_code_n'],'Outlet code auto test !@#$% 1234')
    time.sleep(2)


#Unit Number field validation
    send_keys_by_name(outlets_path['unit_number_n'],'asadf4323@')
    time.sleep(2)
    clear_by_name(outlets_path['unit_number_n'])
    time.sleep(2)

    if unit_number_err_msg==get_text_by_xpath(outlets_path['unit_no_required_path']):
        print("Test 9 : Unit Number required message : ", unit_number_err_msg)
    else :
        print("Something went wrong with checking unit number required message")

    send_keys_by_name(outlets_path['unit_number_n'],'Unit Number auto test !@#$ 123')
    time.sleep(2)

# Selecting value from Region dropdown

    sg_west_value="ce9d03da-bfa3-42a4-b432-121a2c7b1631"
    dropdown_select_value(outlets_path['region_dropdown_path'],0,sg_west_value)
    time.sleep(2)

    driver.find_element(By.CSS_SELECTOR, "body").click()

#Postal Code field validation
    send_keys_by_name(outlets_path['postal_code_n'],'asd!23')
    time.sleep(2)
    clear_by_name(outlets_path['postal_code_n'])
    time.sleep(2)

    if postal_code_err_msg==get_text_by_xpath(outlets_path['postal_code_required_path']):
        print("Test 10 : Postal Code required message : ", postal_code_err_msg)
    else :
        print("Something went wrong with checking postal code required message")

    send_keys_by_name(outlets_path['postal_code_n'],'Postal Code auto test !@#$ 123')
    time.sleep(2)

#First scrolling
    element = driver.find_element(By.NAME, "queueUrl")
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)

#Address textarea field validation

    address_value_over_chars="""Lorem Ipsum is simply dummy text of the printing and typesetting industry.
    Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer
    took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries,
    123 !@#$
    """
    send_keys_by_xpath(outlets_path['address_path'],'Test Address 012 !#@ 33')
    time.sleep(2)
    clear_by_xpath(outlets_path['address_path'])
    time.sleep(2)
    print("Address box is cleared")

    if address_box_err_msg==get_text_by_xpath(outlets_path['address_required_path']):
        print("Test 11 : Address field required message : ", address_box_err_msg)
    else :
        print("Something went wrong with checking address box required message")

    send_keys_by_xpath(outlets_path['address_path'],address_value_over_chars)
    time.sleep(2)


#Image file upload

    image_path = "/Users/aungwaiwaithin/Downloads/test_image.png"

# Locate the hidden <input type="file"> element and send the image path

    scroll_element=driver.find_element(By.XPATH, outlets_path['scroll_for_img_upload'])
    driver.execute_script("arguments[0].scrollIntoView();", scroll_element)

#You should not click the upload button that opens the system file dialog.
# Because, when you click upload_btn.click(), it opens the OS-level file picker, and Selenium cannot interact with OS-native dialogs.
# SO, instead, you should only send the file path to the hidden file input element directly.

    upload_input = driver.find_element(By.XPATH, '//input[@type="file"]')
    time.sleep(2)
    upload_input.send_keys(image_path)
    time.sleep(3)

#Click upload button after image is selected

    driver.find_element(By.XPATH, outlets_path['upload_btn_path']).click()
    print("Test 12 : Image is uploaded successfully!!" )
    time.sleep(5)

#Assigned Beacon dropdown selection

    dropdown_select_value(outlets_path['beacon_dropdown_path'],1,'14jP08FB')
    time.sleep(3)
#Dismiss dropdown after selecting value
    driver.find_element(By.CSS_SELECTOR, "body").click()
    time.sleep(3)
    print("Test 13 : Assigned Beacon value is selected successfully!!")

#Oulet Queue System URL

    valid_url_value='https://queue.sg/outlet_north/updated'
    exp_invalid_url_err_msg="Please enter a valid URL."

    send_keys_by_name(outlets_path['queue_url_n'],'asdf')
    time.sleep(2)

    act_invalid_url_err_msg=get_text_by_xpath(outlets_path['invalid_url_path'])
    if act_invalid_url_err_msg==exp_invalid_url_err_msg:
        print("Test 14 : Invalid URL entered! But, error message is correct!!")
    else:
        print("Something went wrong when checking url validation!!")


    clear_by_name(outlets_path['queue_url_n'])
    time.sleep(2)

    send_keys_by_name(outlets_path['queue_url_n'],valid_url_value)
    time.sleep(2)
    print("Test 15 : Valid system URL entered successfully!!")

#Selecting Opening Hours

    sec_scroll_element=driver.find_element(By.NAME, "queueUrl")
    driver.execute_script("arguments[0].scrollIntoView();", sec_scroll_element)
    time.sleep(2)

    driver.find_element(By.XPATH, outlets_path['sunday_btn_path']).click()
    time.sleep(2)

    time.sleep(5) #To wait manual clicking


#Select 'From' time value
    dropdown_select_value(outlets_path['select_from_time_dropdown_path'],2,'09:00:00')
    time.sleep(5)
# Manually clicked to dismiss dropdown box
    driver.find_element(By.CSS_SELECTOR, "body").click()
    print("Test 16 : From time value selected successfully!")

#Select 'To' time value
    dropdown_select_value(outlets_path['select_to_time_dropdown_path'],3,'22:00:00')
    time.sleep(5)
# Manually clicked to dismiss dropdown box
    driver.find_element(By.CSS_SELECTOR, "body").click()
    print("Test 17 : To time value selected successfully!")

#Add remarks
    send_keys_by_name(outlets_path['remarks_n'],"We've updated opening hours!!")
    time.sleep(2)
    print("Test 18 : Added remarks successfully!")

#Select Start from date value

    click_by_xpath(outlets_path['start_datebox_path'])
    time.sleep(3)
    click_by_xpath(outlets_path['start_date_value_path'])
    time.sleep(2)
    click_by_xpath(outlets_path['start_date_Ok_btn_path'])
    time.sleep(2)
    print("Test 19 : Selecting Start from date value successful!")

#Select Start from time value

    click_by_xpath(outlets_path['start_timebox_path'])
    time.sleep(3)
#
# #facing a common issue with dynamic elements like time pickers:
# # when you try to inspect them, they disappear because clicking outside triggers their closing event.
#
# # Steps:
# # 1.	Open DevTools (F12 or Ctrl+Shift+I)
# # 2. Use setTimeout() trick in console
# # Let the picker stay open for a while: Run below script in console
#
# setTimeout(() => {
#     debugger;
# }, 2000);

    click_by_xpath(outlets_path['hour_path'])
    time.sleep(2)
    click_by_xpath(outlets_path['minute_path'])
    time.sleep(2)
    click_by_xpath(outlets_path['Ok_btn_path'])
    time.sleep(2)
    print("Test 20 : Selecting Start from time value successful!")

#Second Scroll

    element = driver.find_element(By.XPATH, outlets_path['sec_scroll_path'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)

#Select End On date value

    click_by_xpath(outlets_path['end_datebox_path'])
    time.sleep(3)
    click_by_xpath(outlets_path['end_date_value_path'])
    time.sleep(2)
    click_by_xpath(outlets_path['end_date_Ok_btn_path'])
    time.sleep(2)
    print("Test 21 : Selecting End On date value successful!")

#Select End On time value

    click_by_xpath(outlets_path['end_timebox_path'])
    time.sleep(3)

    click_by_xpath(outlets_path['end_hour_path'])
    time.sleep(2)
    click_by_xpath(outlets_path['end_minute_path'])
    time.sleep(2)
    click_by_xpath(outlets_path['end_Ok_btn_path'])
    time.sleep(2)
    print("Test 22 : Selecting End On time value successful!")

#Click publish button to create new outlet

    try:
        click_by_xpath(outlets_path['publ_btn_path'])
        time.sleep(6)
        print("Test 23 : New outlet is created successfully!")
        time.sleep(4)
    except Exception as e:
        print("Outlet is created successfully but, got unexpected error!!", str(e))

    driver.get("https://staging.d1xlt4loftsg5g.amplifyapp.com/account/outlet-management/outlets")
    time.sleep(5)

def change_outlet_status_from_listing():
###### Set as inactive action from listing  ######

    click_by_xpath(outlets_path['list_three_dots_action_btn'])
    time.sleep(2)
    click_by_xpath(outlets_path['list_setasinactive_btn'])
    time.sleep(2)
    click_by_xpath(outlets_path['yes_setasinactive_btn'])
    time.sleep(3)
    actual_status=get_text_by_xpath(outlets_path['check_status_path'])
    print(actual_status)
    expected_status='INACTIVE'

    if actual_status==expected_status:
        print("Test 24 : Changed to inactive status successfully!")
    else:
        print("Changed to inactive status failed!")



###### Set as active action from listing  ######
    click_by_xpath(outlets_path['list_three_dots_action_btn'])
    time.sleep(2)
    click_by_xpath(outlets_path['list_setasactive_btn'])
    time.sleep(2)
    click_by_xpath(outlets_path['yes_setasactive_btn'])
    time.sleep(3)
    actual_status=get_text_by_xpath(outlets_path['check_status_path'])
    print(actual_status)
    expected_status='ACTIVE'

    if actual_status==expected_status:
        print("Test 25 : Change back to active status successfully!")
    else:
        print("Change back to active status failed!")


def check_created_outlet_value():
###### Update Old Outlet flow  ######

# # XPath for the 2nd row's edit icon (SVG inside span inside last td) (First way, no specific item)
#     edit_icon = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
#         By.XPATH,
#         "(//table//tbody//tr)[2]//td[last()]//span[contains(@class, 'rounded-full')]"
#     )))
#     edit_icon.click()
#     time.sleep(6)

# Wait for the Edit icon in the row containing "Test Outlet Name" (Second way, can click to specific item. This is better)
    edit_icon = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
        By.XPATH,
        "//table//tbody//tr[td[contains(text(), 'Test Outlet Name')]]//td[last()]//span[contains(@class, 'rounded-full')][1]"
    )))
    edit_icon.click()
    time.sleep(10)


#Check added/updated data first

    actual_outlet_name='Test Outlet Name'
    actual_outlet_code='OC4773732'
    actual_unit_number='#3113_4212'
    actual_region='Moji'
    actual_postal_code='546374123'
    actual_address='No32. Pthathon Street, Th'
    actual_assigned_beacon='14jP08FB'
    actual_q_system_url='https://queue.sg/outlet_central123'
    actual_open_from_time='12:30 am'
    actual_open_to_time='1:45 pm'
    actual_remarks='Near Northpoint City 123'
    actual_start_from_date='Jun 6, 2025'
    actual_start_from_time='05:30 PM'
    actual_end_on_date='Jun 29, 2025'
    actual_end_one_time='05:30 PM'


    try:
        if get_attribute_by_name(outlets_path['outlet_name_n'])==actual_outlet_name:
            print("Test 26 : Matching outlet name value is success!")
        else:
            print("Outlet name value is : ", get_attribute_by_name(outlets_path['outlet_name_n']))
    except Exception as e:
        print("Error during outlet name value check:", str(e))

    try:
        if get_attribute_by_name(outlets_path['outlet_code_n'])==actual_outlet_code:
            print("Test 27 : Matching outlet code value is success!")
        else:
            print("Outlet code value is not : ", get_attribute_by_name(outlets_path['outlet_code_n']))
    except Exception as e:
        print("Error during outlet code value check:", str(e))

    try:
        if get_attribute_by_name(outlets_path['unit_number_n'])==actual_unit_number:
            print("Test 28 : Matching unit number value is success!")
        else:
            print("Unit number value is : ", get_attribute_by_name(outlets_path['unit_number_n']))
    except Exception as e:
        print("Error during unit number value check:", str(e))

    try:
        if get_text_by_xpath(outlets_path['selected_region_value_path'])==actual_region:
            print("Test 29 : Matching region value is success!")
        else:
            print("Region value is : ", get_text_by_xpath(outlets_path['selected_region_value_path']))
    except Exception as e:
        print("Error during region value check:", str(e))

    try:
        if get_attribute_by_name(outlets_path['postal_code_n'])==actual_postal_code:
            print("Test 30 : Matching postal code value is success!")
        else:
            print("Postal code value is : ", get_attribute_by_name(outlets_path['postal_code_n']))
    except Exception as e:
        print("Error during postal code value check:", str(e))

    try:
        if get_attribute_by_xpath(outlets_path['address_path'])==actual_address:
            print("Test 31 : Matching address value is success!")
        else:
            print("Address value is : ", get_attribute_by_name(outlets_path['address_path']))
    except Exception as e:
        print("Error during address value check:", str(e))

#Cheking uploaded image exists or not
    # Wait until the <img> is present and visible
    img = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//img[@alt='Uploaded image']"))
    )

    # Get the src attribute
    img_src = img.get_attribute("src")

    # Check if src is not empty and is a real image URL
    try:
        if img_src and "kskin.s3.ap-southeast-1.amazonaws.com" in img_src:
            print("✅ Uploaded image is found out successfully.")
        else:
            print("❌ Cannot find uploaded image.")
    except Exception as e:
        print("Error during uploaded image check:", str(e))

    try:
        if get_text_by_xpath(outlets_path['selected_beacon_value_path']) == actual_assigned_beacon:
            print("Test 33 : Matching assigned beacon value is success!")
        else:
            print("Assigned beacon value is:", get_text_by_xpath(outlets_path['selected_beacon_value_path']))
    except Exception as e:
        print("Error during beacon value check:", str(e))

    try:
        if get_attribute_by_name(outlets_path['queue_url_n'])==actual_q_system_url:
            print("Test 34 : Matching queue system URL value is success!")
        else:
            print("Queue System URL value is : ", get_attribute_by_name(outlets_path['queue_url_n']))
    except Exception as e:
        print("Error during queue system url value check:", str(e))

    try:
        if get_text_by_xpath(outlets_path['selected_from_open_hour_value_path'])==actual_open_from_time:
            print("Test 35 : Matching open hour from time value is success!")
        else:
            print("Open hour from time value is : ", get_text_by_xpath(outlets_path['selected_from_open_hour_value_path']))
    except Exception as e:
        print("Error during open hour from time value check:", str(e))

    try:
        if get_text_by_xpath(outlets_path['selected_from_close_hour_value_path'])==actual_open_to_time:
            print("Test 36 : Matching open hour to time value is success!")
        else:
            print("Open hour to time value is :", get_text_by_xpath(outlets_path['selected_from_close_hour_value_path']))
    except Exception as e:
        print("Error during open hour to time value check:", str(e))

    try:
        if get_attribute_by_name(outlets_path['remarks_n'])==actual_remarks:
            print("Test 37 : Matching remarks value is success!")
        else:
            print("Remarks value is : ", get_attribute_by_name(outlets_path['remarks_n']))
    except Exception as e:
        print("Error during remarks value check:", str(e))

    try:
        if get_text_by_xpath(outlets_path['selected_start_from_date_value_path'])==actual_start_from_date:
            print("Test 38 : Matching start from date value is success!")
        else:
            print("Start from date value is : ", get_text_by_xpath(outlets_path['selected_start_from_date_value_path']))
    except Exception as e:
        print("Error during start from date value check:", str(e))

    try:
        if get_text_by_xpath(outlets_path['selected_start_from_time_value_path'])==actual_start_from_time:
            print("Test 39 : Matching start from time value is success!")
        else:
            print("Start from time value is : ", get_text_by_xpath(outlets_path['selected_start_from_time_value_path']))
    except Exception as e:
        print("Error during start from time value check:", str(e))

    try:
        if get_text_by_xpath(outlets_path['selected_end_on_date_value_path'])==actual_end_on_date:
            print("Test 40 : Matching end on date value is success!")
        else:
            print("End on date value is : ", get_text_by_xpath(outlets_path['selected_end_on_date_value_path']))
    except Exception as e:
        print("Error during end on date value check:", str(e))

    try:
        if get_text_by_xpath(outlets_path['selected_end_on_time_value_path'])==actual_end_one_time:
            print("Test 41 : Matching end on time value is success!")
        else:
            print("End on time value is : ", get_text_by_xpath(outlets_path['selected_end_on_time_value_path']))
    except Exception as e:
        print("Error during end on time value check:", str(e))


def update_old_outlet():

    outlet_name_err_msg='Outlet name is required'
    outlet_code_err_msg='Outlet code is required'
    unit_number_err_msg='Unit number is required'
    postal_code_err_msg='Postal code is required'
    address_box_err_msg='Address is required'
    invalid_url_err_msg='Please enter a valid URL.'

#Outlet Name field validation
    clear_by_name(outlets_path['outlet_name_n'])
    time.sleep(2)

    if outlet_name_err_msg==get_text_by_xpath(outlets_path['outlet_name_required_path']):
        print("Test 42 : Outlet name required message : ", outlet_name_err_msg)
    else :
        print("Something went wrong with checking outlet name required message")

    send_keys_by_name(outlets_path['outlet_name_n'],'Updated outlet Name @#12')
    time.sleep(2)

# Check checkbox state
    # Locate the checkbox (use the correct locator strategy)
    checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox' and @aria-hidden='true']")

    # Check if it is selected
    if checkbox.is_selected():
        print("Test 43 : Checkbox is checked ✅")
    else:
        print("Checkbox is NOT checked ❌")


#Outlet Code field validation
    clear_by_name(outlets_path['outlet_code_n'])
    time.sleep(2)

    if outlet_code_err_msg==get_text_by_xpath(outlets_path['outlet_code_required_path']):
        print("Test 44 : Outlet code required message : ", outlet_code_err_msg)
    else :
        print("Something went wrong with checking outlet code required message")

    send_keys_by_name(outlets_path['outlet_code_n'],'Updated Outlet code @#12')
    time.sleep(2)


#Unit Number field validation
    clear_by_name(outlets_path['unit_number_n'])
    time.sleep(2)

    if unit_number_err_msg==get_text_by_xpath(outlets_path['unit_no_required_path']):
        print("Test 45 : Unit Number required message : ", unit_number_err_msg)
    else :
        print("Something went wrong with checking unit number required message")

    send_keys_by_name(outlets_path['unit_number_n'],'Updated Unit Number 34@#')
    time.sleep(2)

    #Third scrolling
    element = driver.find_element(By.NAME, outlets_path['outlet_name_n'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(5)
    print("Test 46 : Third Scrolled successfully!!")

# Selecting value from Region dropdown

    sg_west_value="ce9d03da-bfa3-42a4-b432-121a2c7b1631"
    dropdown_select_value(outlets_path['region_dropdown_path'],0,sg_west_value)
    time.sleep(2)

    driver.find_element(By.CSS_SELECTOR, "body").click()
    print("Test 47 : Region value is updated !!")

#Postal Code field validation
    clear_by_name(outlets_path['postal_code_n'])
    time.sleep(2)

    if postal_code_err_msg==get_text_by_xpath(outlets_path['postal_code_required_path']):
        print("Test 48 : Postal Code required message : ", postal_code_err_msg)
    else :
        print("Something went wrong with checking postal code required message")

    send_keys_by_name(outlets_path['postal_code_n'],'Updated Postal Code &%45')
    time.sleep(2)


#Address textarea field validation

    clear_by_xpath(outlets_path['address_path'])
    time.sleep(2)
    print("Test 49 : Address box is cleared")

    if address_box_err_msg==get_text_by_xpath(outlets_path['address_required_path']):
        print("Test 50 : Address field required message : ", address_box_err_msg)
    else :
        print("Something went wrong with checking address box required message")

    send_keys_by_xpath(outlets_path['address_path'],"Updated address value !@# 234")
    time.sleep(2)

    #Third scrolling
    element = driver.find_element(By.XPATH, outlets_path['address_path'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(5)
    print("Test 51 : Scrolled successfully!!")

## Image upload update case is skipped for now since there is issue
# #Image file upload
#
#     image_path = "/Users/aungwaiwaithin/Downloads/LLK 14.jpg"
#
# # Locate the hidden <input type="file"> element and send the image path
#
#     scroll_element=driver.find_element(By.XPATH, outlets_path['scroll_for_img_upload'])
#     driver.execute_script("arguments[0].scrollIntoView();", scroll_element)
#     print("Scrolled for image upload!!")
#
# #You should not click the upload button that opens the system file dialog.
# # Because, when you click upload_btn.click(), it opens the OS-level file picker, and Selenium cannot interact with OS-native dialogs.
# # SO, instead, you should only send the file path to the hidden file input element directly.
#
#     upload_input = driver.find_element(By.XPATH, '//input[@type="file"]')
#     time.sleep(2)
#     upload_input.send_keys(image_path)
#     time.sleep(3)
#
# #Click upload button after image is selected
#
#     driver.find_element(By.XPATH, outlets_path['upload_btn_path']).click()
#     print("Updated Image is uploaded successfully!!" )
#     time.sleep(5)

#Assigned Beacon dropdown selection

    dropdown_select_value(outlets_path['beacon_dropdown_path'],1,'14jM08F9')
    time.sleep(3)
#Dismiss dropdown after selecting value
    driver.find_element(By.CSS_SELECTOR, "body").click()
    time.sleep(3)
    print("Test 52 : Assigned Beacon value is updated successfully!!")

#Oulet Queue System URL

    valid_url_value='https://queue.sg/outlet_north/updated'
    exp_invalid_url_err_msg="Please enter a valid URL."

    clear_by_name(outlets_path['queue_url_n'])
    time.sleep(2)

    send_keys_by_name(outlets_path['queue_url_n'],'45tt#')
    time.sleep(2)

    act_invalid_url_err_msg=get_text_by_xpath(outlets_path['invalid_url_path'])
    if act_invalid_url_err_msg==exp_invalid_url_err_msg:
        print("Test 53 : Invalid URL entered! But, error message is correct!!")
    else:
        print("Something went wrong when checking url validation!!")

    clear_by_name(outlets_path['queue_url_n'])
    time.sleep(2)

    send_keys_by_name(outlets_path['queue_url_n'],valid_url_value)
    time.sleep(2)
    print("Test 54 : Valid system URL is updated successfully!!")

#Selecting Opening Hours

    sec_scroll_element=driver.find_element(By.NAME, "queueUrl")
    driver.execute_script("arguments[0].scrollIntoView();", sec_scroll_element)
    time.sleep(2)

    driver.find_element(By.XPATH, outlets_path['sunday_btn_path']).click()
    time.sleep(2)

    time.sleep(3) #To wait manual clicking

#Select 'From' time value
    dropdown_select_value(outlets_path['select_from_time_dropdown_path'],2,'09:00:00')
    time.sleep(5)
# Manually clicked to dismiss dropdown box
    driver.find_element(By.CSS_SELECTOR, "body").click()
    print("Test 55 : From time value selected successfully!")

#Select 'To' time value
    dropdown_select_value(outlets_path['select_to_time_dropdown_path'],3,'22:00:00')
    time.sleep(5)
# Manually clicked to dismiss dropdown box
    driver.find_element(By.CSS_SELECTOR, "body").click()
    print("Test 56 : To time value selected successfully!")

#Fourth scrolling
    element = driver.find_element(By.NAME, outlets_path['remarks_n'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(5)
    print("Test 57 : Fourth Scrolled successfully!!")

#Update remarks
    clear_by_name(outlets_path['remarks_n'])
    time.sleep(2)
    send_keys_by_name(outlets_path['remarks_n'],"We've updated all of this outlet's related information!!")
    time.sleep(2)
    print("Test 58 : Updated remarks successfully!")

#Select Start from date value

    click_by_xpath(outlets_path['start_datebox_path'])
    time.sleep(3)
    click_by_xpath(outlets_path['start_date_value_path'])
    time.sleep(2)
    click_by_xpath(outlets_path['start_date_Ok_btn_path'])
    time.sleep(2)
    print("Test 59 : Updating Start from date value successful!")

#Select Start from time value

    click_by_xpath(outlets_path['start_timebox_path'])
    time.sleep(3)
#
# #facing a common issue with dynamic elements like time pickers:
# # when you try to inspect them, they disappear because clicking outside triggers their closing event.
#
# # Steps:
# # 1.	Open DevTools (F12 or Ctrl+Shift+I)
# # 2. Use setTimeout() trick in console
# # Let the picker stay open for a while: Run below script in console

# setTimeout(() => {
#     debugger;
# }, 2000);

    click_by_xpath(outlets_path['hour_path'])
    time.sleep(2)
    click_by_xpath(outlets_path['minute_path'])
    time.sleep(2)
    click_by_xpath(outlets_path['Ok_btn_path'])
    time.sleep(2)
    print("Test 60 : Updating Start from time value successful!")

#Second Scroll

    element = driver.find_element(By.XPATH, outlets_path['sec_scroll_path'])
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(2)

#Select End On date value

    click_by_xpath(outlets_path['end_datebox_path'])
    time.sleep(3)
    click_by_xpath(outlets_path['end_date_value_path'])
    time.sleep(2)
    click_by_xpath(outlets_path['end_date_Ok_btn_path'])
    time.sleep(2)
    print("Test 61 : Updating End On date value successful!")

#Select End On time value

    click_by_xpath(outlets_path['end_timebox_path'])
    time.sleep(3)

    click_by_xpath(outlets_path['end_hour_path'])
    time.sleep(2)
    click_by_xpath(outlets_path['end_minute_path'])
    time.sleep(2)
    click_by_xpath(outlets_path['end_Ok_btn_path'])
    time.sleep(2)
    print("Test 62 : Updating End On time value successful!")

#Click publish button to update outlet

    click_by_xpath(outlets_path['publ_btn_path'])
    time.sleep(6)
    print("Test 63 : Outlet is updated successfully now!")

    #
    # ###### Set as inactive action from listing  ######
    # click_by_xpath(outlets_path['more_action_btn_path'])
    # time.sleep(2)
    # click_by_xpath(outlets_path['more_action_inactive_btn_path'])
    # time.sleep(2)
    # click_by_xpath(outlets_path['yes_setasinactive_btn'])
    # time.sleep(3)
    #
    # print("Changed to inactive status successfully!")
    #
    # ###### Set as active action from listing  ######
    # click_by_xpath(outlets_path['more_action_btn_path'])
    # time.sleep(2)
    # click_by_xpath(outlets_path['more_action_active_btn_path'])
    # time.sleep(2)
    # click_by_xpath(outlets_path['yes_setasactive_btn'])
    # time.sleep(3)
    #
    # print("Change back to active status successfully!")





















