import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# if didn't add above three things, will show ' No module named 'KskinCMS'. error
# >>That’s because KskinCMS is a subfolder, not a top-level module/package in your current Python path (sys.path).
# When running FranchiseAccMain.py, Python is not treating the project root (i.e. SeleniumPython/)
# as part of the module search path.

import pytest
from KskinCMS.GiftBundle_Module.GiftBundle import *

@pytest.fixture(scope="module")
def setup():
    yield driver
    driver.quit()


@pytest.mark.order(1)
def test_open_browser():
    open_browser()