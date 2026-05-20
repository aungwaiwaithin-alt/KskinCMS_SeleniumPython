import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# if didn't add above three things, will show ' No module named 'KskinCMS'. error
# >>That’s because KskinCMS is a subfolder, not a top-level module/package in your current Python path (sys.path).
# When running FranchiseAccMain.py, Python is not treating the project root (i.e. SeleniumPython/)
# as part of the module search path.

import pytest
from KskinCMS.Franchise_Account_Module.FranchiseAcc import *

@pytest.fixture(scope="module")
def setup():
    yield driver
    driver.quit()


@pytest.mark.order(1)
def test_open_browser():
    open_browser()
#
# @pytest.mark.order(2)
# def test_franchise_searching():
#     franchise_searching()
#
# @pytest.mark.order(3)
# def test_listing_active_inactive_action():
#     listing_active_inactive_action()
#
# @pytest.mark.order(4)
# def test_listing_inactive_active_action():
#     listing_inactive_active_action()
#
# @pytest.mark.order(5)
# def test_pagination_and_rows_per_page_actions():
#     pagination_and_rows_per_page_actions()
#
# @pytest.mark.order(6)
# def test_create_new_franchise_account():
#     create_new_franchise_account()
#
@pytest.mark.order(7)
def test_view_back_created_acc_info():
    view_back_created_acc_info()

@pytest.mark.order(8)
def test_edit_franchise_account():
    edit_franchise_account()



