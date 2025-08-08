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

from .css_section import CSSSection
from typing import List
from webwidgets.compilation.css.css_rule import CSSRule


class RuleSection(CSSSection):
    """A section containing a set of CSS rules.
    """

    def __init__(self, rules: List[CSSRule] = None, title: str = None):
        """Creates a new section with the given rules and title.

        :param rules: A list of CSSRule objects to include in the section.
        :type rules: List[CSSRule]
        :param title: The title of the section.
        :type title: str
        """
        super().__init__(title=title)
        self.rules = [] if rules is None else rules

    def compile_content(self, indent_size: int = 4) -> str:
        """Compiles the CSS representation of the rules contained in the
        section.

        :param indent_size: See :py:meth:`CSSRule.to_css`.
        :type indent_size: int
        :return: The CSS representation of the rules.
        :rtype: str
        """
        return "\n\n".join([
            rule.to_css(indent_size=indent_size) for rule in self.rules])
