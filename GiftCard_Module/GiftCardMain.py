import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from KskinCMS.GiftCard_Module.GiftCard import *


@pytest.fixture(scope="module")
def setup():
    # Keep shared Chrome alive across modules (sequential runner closes once).
    yield driver


@pytest.mark.order(1)
def test_open_browser():
    open_browser()


@pytest.mark.order(2)
def test_gift_card_view_page():
    gift_card_view_page()


@pytest.mark.order(3)
def test_open_edit_form():
    open_edit_form()


@pytest.mark.order(4)
def test_gift_card_required_validations():
    gift_card_required_validations()


@pytest.mark.order(5)
def test_update_gift_card():
    update_gift_card()


@pytest.mark.order(6)
def test_listing_active_inactive_action():
    listing_active_inactive_action()


@pytest.mark.order(7)
def test_listing_inactive_active_action():
    listing_inactive_active_action()
