import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from KskinCMS.Treatment_Module.Treatment import *


@pytest.fixture(scope="module")
def setup():
    # Keep shared Chrome alive across modules (sequential runner closes once).
    yield driver


@pytest.mark.order(1)
def test_open_browser():
    open_browser()


@pytest.mark.order(2)
def test_treatments_search_and_filter():
    treatments_search_and_filter()


@pytest.mark.order(3)
def test_add_new_treatment():
    add_new_treatment()


@pytest.mark.order(4)
def test_listing_active_inactive_action():
    listing_active_inactive_action()


@pytest.mark.order(5)
def test_listing_inactive_active_action():
    listing_inactive_active_action()


@pytest.mark.order(6)
def test_rows_per_page_actions():
    rows_per_page_actions()


@pytest.mark.order(7)
def test_check_created_treatment_value():
    check_created_treatment_value()


@pytest.mark.order(8)
def test_update_old_treatment():
    update_old_treatment()
