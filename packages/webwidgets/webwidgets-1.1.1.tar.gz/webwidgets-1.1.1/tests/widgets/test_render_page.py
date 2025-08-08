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
import pytest
from typing import Tuple
import webwidgets as ww
from webwidgets.compilation.html import Div


class TestRenderPage:
    """Test cases for the `render_page` fixture.
    """

    class Color(ww.Widget):
        def __init__(self, color: Tuple[int, int, int]):
            super().__init__()
            self.color = color

        def build(self):
            hex_color = "#%02x%02x%02x" % self.color
            return Div(style={"background-color": hex_color,
                              "height": "100vh",
                              "width": "100vw"})

    def test_return_type_and_shape(self, web_drivers, render_page):
        for web_driver in web_drivers:
            array = render_page(ww.Page(), web_driver)
            assert isinstance(array, np.ndarray)
            assert array.ndim == 3
            assert array.shape[0] >= 10
            assert array.shape[1] >= 10
            assert array.shape[2] in (3, 4)  # Some drivers add alpha channel

    @pytest.mark.parametrize("color", [
        (255, 0, 0),  # Red
        (0, 255, 0),  # Green
        (0, 0, 255),  # Blue
        (0, 0, 0),  # Black
        (128, 128, 128),  # Gray
        (255, 255, 255),  # White
        (123, 45, 67),  # Other color 1
        (234, 0, 156)  # Other color 2
    ])
    def test_colored_page(self, color, web_drivers, render_page):
        page = ww.Page([TestRenderPage.Color(color)])
        for web_driver in web_drivers:
            array = render_page(page, web_driver)
            assert isinstance(array, np.ndarray)
            assert np.all(array[..., 0] == color[0])
            assert np.all(array[..., 1] == color[1])
            assert np.all(array[..., 2] == color[2])
