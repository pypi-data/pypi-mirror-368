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

from webwidgets.compilation.html.html_tags import *


class TestHTMLTags:
    def test_text_node(self):
        text_node = TextNode("Hello, World!")
        assert text_node.to_html() == "<textnode>Hello, World!</textnode>"

    def test_text_node_with_attributes(self):
        text_node = TextNode("Hello, World!",
                             attributes={"class": "my-class", "id": "my-id"})
        assert text_node.to_html() == \
            '<textnode class="my-class" id="my-id">Hello, World!</textnode>'

    def test_body(self):
        body = Body()
        assert body.to_html() == "<body></body>"

    def test_div(self):
        div = Div()
        assert div.to_html() == "<div></div>"

    def test_doctype(self):
        doctype = Doctype()
        assert doctype.to_html() == "<!DOCTYPE html>"

    def test_head(self):
        head = Head()
        assert head.to_html() == "<head></head>"

    def test_html(self):
        html = Html()
        assert html.to_html() == "<html></html>"
