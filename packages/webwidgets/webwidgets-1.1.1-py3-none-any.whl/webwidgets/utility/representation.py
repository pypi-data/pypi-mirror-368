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

class ReprMixin:
    """A mixin class that is represented with its variables when printed.

    For example:

    >>> class MyClass(RepresentedWithVars):
    ...     def __init__(self, a, b):
    ...         self.a = a
    ...         self.b = b
    >>> obj = MyClass(1, 2)
    >>> print(obj)
    MyClass(a=1, b=2)
    """

    def __repr__(self) -> str:
        """Returns a string exposing all member variables of the class.

        :return: A string representing the class with its variables.
        :rtype: str
        """
        variables = ', '.join(f'{k}={repr(v)}' for k, v in vars(self).items())
        return f"{self.__class__.__name__}({variables})"
