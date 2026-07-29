import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from KskinCMS.Outlet_Module.Outlets import *


@pytest.fixture(scope="module")
def setup():
    # Keep shared Chrome alive across modules (sequential runner closes once).
    yield driver


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
