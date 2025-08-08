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

from .rule_section import RuleSection
from webwidgets.compilation.css.css_rule import CSSRule


class Preamble(RuleSection):
    """A set of CSS rules that apply globally to all HTML elements.

    The CSS preamble serves as a global default for multiple properties. For
    example, it defines the document's box model and sets all margin and
    padding values to 0.
    """

    def __init__(self):
        """Creates a new CSS preamble."""
        super().__init__(
            rules=[
                CSSRule("*, *::before, *::after", {

                    # Defining the box model to border-box
                    "box-sizing": "border-box",

                    # Setting all margin and padding values to 0
                    "margin": "0",
                    "padding": "0",

                    # Sets the overflow policy to hidden
                    "overflow": "hidden"
                })
            ],
            title="Preamble"
        )
