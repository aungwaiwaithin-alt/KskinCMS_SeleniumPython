import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# if didn't add above three things, will show ' No module named 'KskinCMS'. error
# >>That’s because KskinCMS is a subfolder, not a top-level module/package in your current Python path (sys.path).
# When running FranchiseAccMain.py, Python is not treating the project root (i.e. SeleniumPython/)
# as part of the module search path.

import pytest
from KskinCMS.Therapists_Module.Therapist import *

@pytest.fixture(scope="module")
def setup():
    # Keep shared Chrome alive across modules (sequential runner closes once).
    yield driver


@pytest.mark.order(1)
def test_open_browser():
    open_browser()

@pytest.mark.order(2)
def test_therapist_search_and_filter():
    therapist_search_and_filter()

@pytest.mark.order(3)
def test_listing_active_inactive_action():
    listing_active_inactive_action()

@pytest.mark.order(4)
def test_listing_inactive_active_action():
    listing_inactive_active_action()

@pytest.mark.order(5)
def test_rows_per_page_actions():
    rows_per_page_actions()

@pytest.mark.order(6)
def test_add_new_therapist():
    add_new_therapist()

@pytest.mark.order(7)
def test_check_created_therapist_value():
    check_created_therapist_value()

@pytest.mark.order(8)
def test_update_old_therapist():
    update_old_therapist()













