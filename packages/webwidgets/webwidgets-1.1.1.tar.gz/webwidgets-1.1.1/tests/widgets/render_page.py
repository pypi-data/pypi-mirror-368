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

import numpy as np
import os
from PIL import Image
from selenium.webdriver import Chrome, Firefox
import tempfile
from typing import Union
import webwidgets as ww


def render_page(page: ww.Page, driver: Union[Chrome, Firefox]) -> np.ndarray:
    """Renders a page with the given web driver and returns a numpy array of
    the rendered image.

    :param page: The page to render.
    :type page: Page
    :param driver: The web driver to use for rendering.
    :type driver: Union[Chrome, Firefox]
    :return: A numpy array of the rendered image.
    :rtype: np.ndarray
    """
    # Compiling a website with the given page only
    website = ww.Website(pages=[page])
    compiled = website.compile()

    # Rendering within a temporary directory
    with tempfile.TemporaryDirectory() as tmp:

        # Exporting HTML and CSS code
        html_file_path = os.path.join(tmp, "index.html")
        css_file_path = os.path.join(tmp, "styles.css")
        with open(html_file_path, "w") as f:
            f.write(compiled.html_content[0])
        with open(css_file_path, "w") as f:
            f.write(compiled.css_content)

        # Rendering the page
        render_path = os.path.join(tmp, "render.png")
        driver.get("file://" + html_file_path)
        driver.maximize_window()
        driver.save_screenshot(render_path)

        # Reading the image data
        array = np.array(Image.open(render_path))

    # Returning the image data
    return array
