import time
from RegionHelper import *
from RegionVarPaths import *
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
    driver.get("https://staging.d1xlt4loftsg5g.amplifyapp.com/")
    time.sleep(5)
    driver.maximize_window()
    print("Test 1 : Open browser success!")
    time.sleep(3)

    #Click outlet mgmt menu
    click_by_xpath(region_path['outlet_mgmt_menu_path'])
    time.sleep(3)
    #Click regions sub menu
    click_by_xpath(region_path['region_menu_path'])
    time.sleep(5)
    print("Test 2 : Navigated to Regions listing successfully!")


def region_searching():

#Search functions
    #Region name searching (Matched case)
    send_keys_by_name(region_path['search_box_name'], 'QA Test Region')
    time.sleep(3)
    actual_name_search_result=get_text_by_xpath(region_path['name_search_result_path'])
    exp_name_search_result='QA Test Region'
    print(actual_name_search_result)
    if actual_name_search_result==exp_name_search_result:
        print("Test 3 : Name searching with matched value is successful!")
    else:
        print("Something went wrong. Name searching with matched value is failed!")

    driver.find_element(By.NAME,region_path['search_box_name']).clear()
    time.sleep(5)

    refresh_search_result()

#Region name searching (Un_Matched case)
    send_keys_by_name(region_path['search_box_name'], 'dsf3')
    time.sleep(3)
    actual_name_search_result=get_text_by_xpath(region_path['no_region_result_path'])
    exp_name_search_result='No region'
    print(actual_name_search_result)
    if actual_name_search_result==exp_name_search_result:
        print("Test 4 : Name searching with un_matched value is successful!")
    else:
        print("Something went wrong. Name searching with un_matched value is failed!")

    driver.find_element(By.NAME,region_path['search_box_name']).clear()
    time.sleep(5)

    refresh_search_result()

def create_new_region():

#Click add new region button
    click_by_xpath(region_path['add_new_region_btn_path'])
    time.sleep(3)
#Click cancel button to close
    click_by_xpath(region_path['cancel_btn_path'])
    time.sleep(3)
    print("Test 5 : Cancel button is working fine for create box!")

#Click add new region button again
    click_by_xpath(region_path['add_new_region_btn_path'])
    time.sleep(3)
#Click x sing to dismiss
    print("Before clicking x sign")
    click_by_xpath(region_path['x_sign_btn_path'])
    time.sleep(3)
    print("Test 6 : 'X' sign function is working fine for create box!")

#Click add new region button again to create new region
    click_by_xpath(region_path['add_new_region_btn_path'])
    time.sleep(3)
#Check create box label is correct or not
    expected_create_box_label='Add new region'
    actual_create_box_label=get_text_by_xpath(region_path['add_new_region_label_path'])
    print(actual_create_box_label)
    if actual_create_box_label==expected_create_box_label:
        print("Test 7 : New region box's title is correct!")
    else:
        print("Something went wrong. Checking new region box's title is failed!")


    send_keys_by_name(region_path['region_name_txt_box'],'New Region')
    time.sleep(2)
#Check validation and create new region
    clear_by_name(region_path['region_name_txt_box'])
    time.sleep(2)
    print("Test 8 : Required message for region name in create box is : " + get_text_by_xpath(region_path['region_name_req_err_msg_path']))

    send_keys_by_name(region_path['region_name_txt_box'],'New Region Test 1@')
    time.sleep(2)

    click_by_xpath(region_path['save_btn_path'])
    time.sleep(3)

#Check back new region is created successfully or not
    actual_created_item_name=get_text_by_xpath(region_path['actual_created_item_path'])
    expected_created_item_name='New Region Test 1@'
    print(actual_created_item_name)
    if actual_created_item_name==expected_created_item_name:
        print("Test 9 : New region is created successfully!")
    else:
        print("Something went wrong. New region creation is failed!")



def update_old_region():

    print("Before clicking edit button")
    #Click edit btn of old region
    click_by_xpath(region_path['edit_btn_path'])
    time.sleep(3)
    #Click cancel button to close
    click_by_xpath(region_path['cancel_btn_path'])
    time.sleep(3)
    print("Test 10 : Cancel button is working fine for edit box!")

    #Click edit region button again
    click_by_xpath(region_path['edit_btn_path'])
    time.sleep(3)
    #Click x sing to dismiss
    click_by_xpath(region_path['x_sign_btn_path'])
    time.sleep(3)
    print("Test 11 : 'X' sign function is working fine for edit box!")

    #Click edit region button again to update old region
    click_by_xpath(region_path['edit_btn_path'])
    time.sleep(3)
    #Check update box label is correct or not
    expected_update_box_label='Edit region'
    actual_update_box_label=get_text_by_xpath(region_path['edit_region_label_path'])
    print(actual_update_box_label)
    if actual_update_box_label==expected_update_box_label:
        print("Test 12 : Edit region box's title is correct!")
    else:
        print("Something went wrong. Checking new region box's title is failed!")

    #Check validation and updated old region
    clear_by_name(region_path['region_name_txt_box'])
    time.sleep(2)
    print("Test 13 : Required message for region name in update box is : " + get_text_by_xpath(region_path['region_name_req_err_msg_path']))

    send_keys_by_name(region_path['region_name_txt_box'],'Updated Region Name 2#')
    time.sleep(2)

    click_by_xpath(region_path['save_btn_path'])
    time.sleep(3)

    #Check back edited region name is updated successfully or not
    actual_updated_item_name=get_text_by_xpath(region_path['actual_created_item_path'])
    expected_updated_item_name='Updated Region Name 2#$'
    print(actual_updated_item_name)
    if actual_updated_item_name==expected_updated_item_name:
        print("Test 14 : Old region is updated successfully!")
    else:
        print("Something went wrong. Old region updating is failed!")