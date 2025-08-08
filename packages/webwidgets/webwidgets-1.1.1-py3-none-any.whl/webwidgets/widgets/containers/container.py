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
from webwidgets.widgets.widget import Widget


class Container(Widget):
    """
    A widget that can contain other widgets.
    """

    def __init__(self, widgets: List[Widget] = None):
        """Creates a new Container with optional widgets inside.

        :param widgets: A list of widgets to be contained within the container.
                    Defaults to an empty list.
        :type widgets: List[Widget]
        """
        super().__init__()
        self._widgets = [] if widgets is None else widgets

    @property
    def widgets(self) -> List[Widget]:
        """Returns the list of widgets contained within the container."""
        return self._widgets

    def add(self, widget: Widget) -> None:
        """Adds a widget to the container.

        :param widget: The widget to add to the container.
        :type widget: Widget
        """
        self._widgets.append(widget)
