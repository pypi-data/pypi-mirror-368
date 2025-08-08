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

from abc import ABC, abstractmethod
from webwidgets.compilation.html.html_node import HTMLNode
from webwidgets.utility.representation import ReprMixin


class Widget(ABC, ReprMixin):
    """Abstract base class for all widgets.

    All subclasses of :py:class:`Widget` must implement a :py:meth:`build`
    method that returns an :py:class:`HTMLNode` object.
    """

    @abstractmethod
    def build(self) -> HTMLNode:
        """Builds the widget and returns the corresponding :py:class:`HTMLNode`
        object.

        This method must be overridden by subclasses to create specific HTML
        elements.
        """
        pass
