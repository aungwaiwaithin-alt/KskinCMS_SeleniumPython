import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from KskinCMS.GiftBundle_Module.GiftBundle import *

@pytest.fixture(scope="module")
def setup():
    # Keep shared Chrome alive across modules (sequential runner closes once).
    yield driver


@pytest.mark.order(1)
def test_open_browser():
    open_browser()

@pytest.mark.order(2)
def test_rows_per_page_actions():
    rows_per_page_actions()

@pytest.mark.order(3)
def test_listing_active_inactive_action():
    listing_active_inactive_action()

@pytest.mark.order(4)
def test_listing_inactive_active_action():
    listing_inactive_active_action()

@pytest.mark.order(5)
def test_add_new_gift_bundle():
    add_new_gift_bundle()

@pytest.mark.order(6)
def test_check_created_gift_bundle_value():
    check_created_gift_bundle_value()

@pytest.mark.order(7)
def test_update_old_gift_bundle():
    update_old_gift_bundle()
