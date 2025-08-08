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

from .html_node import HTMLNode, no_end_tag, one_line, RawText
from typing import Dict


@one_line
class TextNode(HTMLNode):
    """A one-line HTML element that only contains raw text (like `<h1>`).

    A text node renders on one line and only contains one child: a
    :py:class:`RawText` node with the text to be rendered.
    """

    def __init__(self, text: str, attributes: Dict[str, str] = None,
                 style: Dict[str, str] = None):
        """Creates a new text node with the given text and attributes.

        :param text: The text content of the node.
        :type text: str
        :param attributes: See :py:meth:`HTMLNode.__init__`. Defaults to an
            empty dictionary.
        :type attributes: Dict[str, str]
        :param style: See :py:meth:`HTMLNode.__init__`. Defaults to an empty
            dictionary.
        :type style: Dict[str, str]
        """
        super().__init__(children=[
            RawText(text)
        ], attributes=attributes, style=style)


class Body(HTMLNode):
    """The `<body>` element containing the visible content of a document."""
    pass


class Div(HTMLNode):
    """A `<div>` element used for grouping elements."""
    pass


@one_line
@no_end_tag
class Doctype(HTMLNode):
    """The `<!DOCTYPE html>` doctype declaration of a document."""

    def __init__(self):
        """Creates a `<!DOCTYPE html>` doctype declaration element."""
        super().__init__()

    @property
    def start_tag(self) -> str:
        """Overrides the start tag for this node."""
        return "<!DOCTYPE html>"


class Head(HTMLNode):
    """The `<head>` element containing metadata about a document."""
    pass


class Html(HTMLNode):
    """The `<html>` element of an HTML document."""
    pass


@one_line
@no_end_tag
class Link(HTMLNode):
    """A `<link>` element for linking to external resources."""
    pass
