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

from .container import Container
from webwidgets.compilation.html.html_node import RootNode
from webwidgets.compilation.html.html_tags import Body, Doctype, Head, Html, \
    Link


class Page(Container):
    """A widget representing a web page. It contains other widgets and is
    responsible for laying them out within the page.
    """

    def build(self, css_file_name: str = "styles.css") -> RootNode:
        """Builds the HTML representation of the page.

        This method constructs an HTML structure that includes a doctype
        declaration, a head section with meta tags, and a body section
        containing the widgets. The widgets are rendered recurisvely by calling
        their :py:meth:`build` method.

        :param css_file_name: The name of the CSS file to link to the page if
            the page elements contain any styles. Defaults to "styles.css".
        :type css_file_name: str
        :return: A :py:class:`RootNode` object representing the page.
        :rtype: RootNode
        """
        # Building nodes from the page's widgets
        nodes = [w.build() for w in self.widgets]

        # Initializing the head section of the page
        head = Head()

        # Checking if there is any style sheet to link to the page.
        # To do so, we just check if any child node has a non-empty style.
        if any(style for n in nodes for style in n.get_styles().values()):
            head.add(Link(
                attributes={"href": css_file_name, "rel": "stylesheet"}
            ))

        # Building the HTML representation of the page
        return RootNode(
            children=[
                Doctype(),
                Html(
                    children=[head, Body(children=nodes)]
                )
            ]
        )
