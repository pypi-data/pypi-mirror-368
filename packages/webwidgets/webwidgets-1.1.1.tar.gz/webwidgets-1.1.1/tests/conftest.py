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
from .wrap_core_css import wrap_core_css as _wrap_core_css


# Exposing the `wrap_core_css` utility as a pytest fixture
@pytest.fixture(scope="session")
def wrap_core_css():
    return _wrap_core_css
