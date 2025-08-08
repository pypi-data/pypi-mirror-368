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
from webwidgets.utility.indentation import get_indentation


class TestIndentation:
    @pytest.mark.parametrize("indent_level", [0, 1, 2])
    @pytest.mark.parametrize("indent_size", [3, 4, 8])
    def test_get_indentation(self, indent_level: int, indent_size: int):
        """Tests get_indentation with different indentation levels and sizes."""
        expected_indentation = ' ' * indent_size * indent_level
        assert get_indentation(
            indent_level, indent_size) == expected_indentation

    @pytest.mark.parametrize("indent_level", [-2, -1, 0])
    @pytest.mark.parametrize("indent_size", [3, 4, 8])
    def test_get_indentation_for_negative_levels(self, indent_level, indent_size):
        assert get_indentation(indent_level, indent_size) == ''
