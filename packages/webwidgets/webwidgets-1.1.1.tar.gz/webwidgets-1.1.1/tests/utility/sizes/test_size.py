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
from webwidgets.utility.sizes.size import Size, AbsoluteSize, RelativeSize, \
    with_unit
import webwidgets as ww


class TestSize:
    @pytest.mark.parametrize("value", [0, 10, 10.0, 12.33])
    def test_size(self, value):
        size = Size(value)
        assert size.value == value
        assert size.unit == "size"
        assert size.to_css() == f"{value}size"

    @pytest.mark.parametrize("attr_to_test",
                             [AbsoluteSize, RelativeSize, Size,
                              with_unit])
    def test_size_helpers_not_at_top_level(self, attr_to_test):
        """Tests the visibility of helper classes and functions."""
        # Making sure the class or function exists in the proper size module
        assert hasattr(ww.utility.size, attr_to_test.__name__)

        # Making sure it is not visible at the top level
        assert not hasattr(ww, attr_to_test.__name__)

    def test_absolute_size_not_importable_at_top_level(self):
        with pytest.raises(AttributeError, match="AbsoluteSize"):
            ww.AbsoluteSize(5)

    def test_relative_size_not_importable_at_top_level(self):
        with pytest.raises(AttributeError, match="RelativeSize"):
            ww.RelativeSize(5)

    def test_size_not_importable_at_top_level(self):
        with pytest.raises(AttributeError, match="Size"):
            ww.Size(5)

    def test_with_unit_not_importable_at_top_level(self):
        with pytest.raises(AttributeError, match="with_unit"):
            ww.with_unit("10px")

    @pytest.mark.parametrize("unit", ["m", "cm", "%"])
    def test_with_unit(self, unit):
        @with_unit(unit)
        class CustomUnit(Size):
            pass
        assert CustomUnit(3).to_css() == f"3{unit}"
