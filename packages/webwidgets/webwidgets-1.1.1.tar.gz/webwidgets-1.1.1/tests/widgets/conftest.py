# =======================================================================
#
#  This file is part of WebWidgets, a Python package for designing web
#  UIs.
#
#  You should have received a copy of the MIT License along with
#  WebWidgets. If not, see <https://opensource.org/license/mit>.
#
#  Copyright(C) 2025, mlaasri
#
# =======================================================================

import pytest
from .render_page import render_page as _render_page
from selenium.webdriver import Chrome, Firefox
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


@pytest.fixture(scope="session")
def chrome_web_driver():
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--silent")
    driver = Chrome(options=options)
    yield driver
    driver.quit()


@pytest.fixture(scope="session")
def firefox_web_driver():
    options = FirefoxOptions()
    options.add_argument("--headless")
    driver = Firefox(options=options)
    yield driver
    driver.quit()


# Exposing the `render_page` utility as a pytest fixture
@pytest.fixture(scope="session")
def render_page():
    return _render_page


@pytest.fixture(scope="session")
def web_drivers(chrome_web_driver, firefox_web_driver):
    return [chrome_web_driver, firefox_web_driver]
