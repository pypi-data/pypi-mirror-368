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

from typing import Dict
from webwidgets.utility.indentation import get_indentation
from webwidgets.utility.representation import ReprMixin
from webwidgets.utility.validation import validate_css_identifier, \
    validate_css_selector, validate_css_value


class CSSRule(ReprMixin):
    """A rule in a style sheet.
    """

    def __init__(self, selector: str, declarations: Dict[str, str]):
        """Stores the selector and declarations of the rule.

        :param selector: The selector of the rule.
        :type selector: str
        :param declarations: The CSS declarations for the rule, specified as a
            dictionary where keys are property names and values are their
            corresponding values. For example: `{'color': 'red'}`
        :type declarations: Dict[str, str]
        """
        super().__init__()
        self.selector = selector
        self.declarations = declarations

    def to_css(self, indent_size: int = 4) -> str:
        """Converts the rule into CSS code.

        The rule's name is converted to a class selector.

        Note that the rule's name and all property names are validated before
        being converted. The rule's name is validated with
        :py:func:`validate_css_selector` while the property names are validated
        with :py:func:`validate_css_identifier`. 

        :param indent_size: The number of spaces to use for indentation in the
            CSS code. Defaults to 4.
        :type indent_size: int
        :return: The CSS code as a string.
        :rtype: str
        """
        # Defining indentation
        indentation = get_indentation(level=1, size=indent_size)

        # Validating the selector
        validate_css_selector(self.selector)

        # Writing down each property
        css_code = self.selector + " {\n"
        for property_name, value in self.declarations.items():
            validate_css_identifier(property_name)
            validate_css_value(value)
            css_code += f"{indentation}{property_name}: {value};\n"
        css_code += "}"

        return css_code


class ClassRule(CSSRule):
    """A CSS rule that targets a CSS class.

    The class dynamically sets its selector based on its class name.
    """

    def __init__(self, name: str, declarations: Dict[str, str]):
        """Creates a new CSS class rule.

        :param name: The name of the CSS class.
        :type name: str
        :param declarations: See :py:meth:`CSSRule.__init__`.
        :type declarations: Dict[str, str]
        """
        super().__init__(None, declarations)  # Starting without a selector
        self._name = None  # Starting without a name
        self.name = name  # Setting both the selector and the name here

    @property
    def name(self) -> str:
        """Returns the name of the CSS class.

        :return: The name of the CSS class.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Sets the name of the CSS class.

        :param value: The new name of the CSS class.
        :type value: str
        """
        self._name = value
        self.selector = f".{value}"  # Updating the selector
