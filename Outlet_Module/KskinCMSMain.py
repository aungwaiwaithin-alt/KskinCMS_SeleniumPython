import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# if didn't add above three things, will show ' No module named 'KskinCMS'. error
# >>That’s because KskinCMS is a subfolder, not a top-level module/package in your current Python path (sys.path).
# When running FranchiseAccMain.py, Python is not treating the project root (i.e. SeleniumPython/)
# as part of the module search path.

import pytest
from KskinCMS.Outlet_Module.KskinCMS import *

@pytest.fixture(scope="module")
def setup():
    yield driver
    driver.quit()


@pytest.mark.order(1)
def test_open_browser():
    open_browser()

@pytest.mark.order(2)
def test_outlets_search_and_filters():
    outlets_search_and_filters()

@pytest.mark.order(3)
def test_create_new_outlet():
    create_new_outlet()

@pytest.mark.order(4)
def test_change_outlet_status_from_listing():
    change_outlet_status_from_listing()

@pytest.mark.order(5)
def test_check_created_outlet_value():
    check_created_outlet_value()

@pytest.mark.order(6)
def test_update_old_outlet():
    update_old_outlet()

