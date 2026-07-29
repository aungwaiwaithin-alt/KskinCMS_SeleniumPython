import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from KskinCMS.Franchise_Account_Module.FranchiseAcc import *

@pytest.fixture(scope="module")
def setup():
    # Keep shared Chrome alive across modules (sequential runner closes once).
    yield driver


@pytest.mark.order(1)
def test_open_browser():
    open_browser()

@pytest.mark.order(2)
def test_franchise_searching():
    franchise_searching()

@pytest.mark.order(3)
def test_listing_active_inactive_action():
    listing_active_inactive_action()

@pytest.mark.order(4)
def test_listing_inactive_active_action():
    listing_inactive_active_action()

@pytest.mark.order(5)
def test_pagination_and_rows_per_page_actions():
    pagination_and_rows_per_page_actions()

@pytest.mark.order(6)
def test_create_new_franchise_account():
    create_new_franchise_account()

@pytest.mark.order(7)
def test_view_back_created_acc_info():
    view_back_created_acc_info()

@pytest.mark.order(8)
def test_edit_franchise_account():
    edit_franchise_account()
