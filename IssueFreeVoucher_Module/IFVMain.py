import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from KskinCMS.IssueFreeVoucher_Module.IFV import *


@pytest.fixture(scope="module")
def setup():
    # Keep shared Chrome alive across modules (sequential runner closes once).
    yield driver


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


@pytest.mark.order(5)
def test_check_created_ifv_value():
    check_created_ifv_value()
