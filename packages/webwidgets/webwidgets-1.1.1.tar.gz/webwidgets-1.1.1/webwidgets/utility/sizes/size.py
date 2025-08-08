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

from webwidgets.utility.representation import ReprMixin
from typing import Callable, Type, Union


class Size(ReprMixin):
    """Base class representing a length.

    Sizes are specified by a numerical value and a CSS unit (e.g. `px`, `%`,
    etc.). The value is provided upon creation and the unit is derived from the
    class name of the :py:class:`Size` object.
    """

    def __init__(self, value: Union[float, int]):
        """Creates a new :py:class:`Size` object with the given numerical
        value.

        :param value: The numerical value of the size.
        :type value: Union[float, int]
        """
        self.value = value

    @property
    def unit(self) -> str:
        """Returns the unit of the size's numerical value.

        The unit of a size object is the name of its class in lowercase.

        :return: The unit of the size.
        :rtype: str
        """
        return self.__class__.__name__.lower()

    def to_css(self) -> str:
        """Compiles and returns the CSS representation of the :py:class:`Size`
        object.

        The CSS representation is obtained by concatenating the value of the
        size with its unit (e.g. `"10px"`).

        :return: The CSS representation of the size.
        :rtype: str
        """
        return str(self.value) + self.unit


class AbsoluteSize(Size):
    """A size whose unit is an absolute unit that does not depend on any
    context. Examples include pixels (`"px"`) and centimeters (`"cm"`).
    """
    pass


class RelativeSize(Size):
    """A size whose unit is relative to the size of other elements, such as the
    size of a display or a font. Examples include percentages (`"%"`) and ems
    (`"em"`).
    """
    pass


def with_unit(unit: str) -> Callable[[Type[Size]], Type[Size]]:
    """Returns a decorator to override the unit of a Size subclass with the
    given unit.

    :param unit: The unit to be used for the Size subclass.
    :type unit: str
    :return: A decorator that overrides the unit of a Size subclass with the
        given unit.
    :rtype: Callable[[Type[Size]], Type[Size]]
    """
    def _decorator(cls):
        """Decorator to override the unit of a Size subclass.

        :param cls: A subclass of Size whose unit should be overridden.
        :return: The given class with a new unit.
        """
        cls.unit = property(
            lambda _: unit, doc=f"Always returns '{unit}'.")
        return cls
    return _decorator
