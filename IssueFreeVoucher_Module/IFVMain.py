import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# if didn't add above three things, will show ' No module named 'KskinCMS'. error
# >>That’s because KskinCMS is a subfolder, not a top-level module/package in your current Python path (sys.path).
# When running FranchiseAccMain.py, Python is not treating the project root (i.e. SeleniumPython/)
# as part of the module search path.

import pytest
from KskinCMS.IssueFreeVoucher_Module.IFV import *

@pytest.fixture(scope="module")
def setup():
    yield driver
    driver.quit()


@pytest.mark.order(1)
def test_open_browser():
    open_browser()

@pytest.mark.order(2)
def test_ifv_search_and_filter():
    ifv_search_and_filter()

@pytest.mark.order(3)
def test_rows_per_page_actions():
    rows_per_page_actions()

@pytest.mark.order(4)
def test_add_new_ifv():
    add_new_ifv()
