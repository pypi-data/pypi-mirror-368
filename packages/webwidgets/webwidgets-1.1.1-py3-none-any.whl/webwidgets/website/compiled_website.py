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

from typing import List
from webwidgets.utility.representation import ReprMixin


class CompiledWebsite(ReprMixin):
    """A utility class to store compiled HTML and CSS code obtained from a
    :py:class:`Website` object.
    """

    def __init__(self, html_content: List[str], css_content: str):
        """Stores compiled HTML and CSS content.

        :param html_content: The compiled HTML code of each page in the
            website.
        :type html_content: List[str]
        :param css_content: The compiled CSS code of the website, shared across
            all pages.
        :type css_content: str
        """
        super().__init__()
        self.html_content = html_content
        self.css_content = css_content
