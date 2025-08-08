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

def get_indentation(level: int, size: int = 4) -> str:
    """Returns an indentation string for the given level.

    :param level: The level of indentation. If negative, this
        function will return an empty string representing no indentation.
    :type level: int
    :param size: The number of spaces to use for each indentation level.
        Defaults to 4 spaces.
    :type size: int
    :return: A string representing the indentation.
    :rtype: str
    """
    return ' ' * (max(level, 0) * size)
