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
from webwidgets.utility.sizes.size import AbsoluteSize, RelativeSize
import webwidgets as ww


class TestSizes:
    @pytest.mark.parametrize("value", [0, 10, 10.0, 82.33])
    def test_percent(self, value):
        size = ww.Percent(value)
        assert isinstance(size, RelativeSize)
        assert size.value == value
        assert size.unit == "%"
        assert size.to_css() == f"{value}%"

    @pytest.mark.parametrize("value", [0, 10, 10.0, 12.33])
    def test_px(self, value):
        size = ww.Px(value)
        assert isinstance(size, AbsoluteSize)
        assert size.value == value
        assert size.unit == "px"
        assert size.to_css() == f"{value}px"
