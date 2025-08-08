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

import pytest
import webwidgets as ww
from webwidgets.compilation.html.html_node import HTMLNode, RawText
from webwidgets.widgets.widget import Widget


class TestPage:
    class Text(ww.Widget):
        def __init__(self, text):
            super().__init__()
            self.text = text

        def build(self):
            return HTMLNode(children=[RawText(self.text)])

    class Styled(ww.Widget):
        def build(self):
            return HTMLNode(style={"color": "blue"})

    def test_page_is_widget(self):
        page = ww.Page()
        assert isinstance(page, Widget)

    def test_compiling_empty_page(self):
        page = ww.Page()
        expected_html = "\n".join([
            "<!DOCTYPE html>",
            "<html>",
            "    <head></head>",
            "    <body></body>",
            "</html>"
        ])
        assert page.build().to_html() == expected_html

    @pytest.mark.parametrize("text", [
        "Hello, World!", "This is a test.", "Message is 354."])
    def test_page_add_one(self, text):
        page = ww.Page()
        page.add(TestPage.Text(text))
        expected_html = "\n".join([
            "<!DOCTYPE html>",
            "<html>",
            "    <head></head>",
            "    <body>",
            "        <htmlnode>",
            f"            {text}",
            "        </htmlnode>",
            "    </body>",
            "</html>"
        ])
        assert page.build().to_html() == expected_html

    def test_page_add_many(self):
        page = ww.Page()
        page.add(TestPage.Text("Hello, World!"))
        page.add(TestPage.Text("This is a test."))
        page.add(TestPage.Text("Bye!"))
        expected_html = "\n".join([
            "<!DOCTYPE html>",
            "<html>",
            "    <head></head>",
            "    <body>",
            "        <htmlnode>",
            "            Hello, World!",
            "        </htmlnode>",
            "        <htmlnode>",
            "            This is a test.",
            "        </htmlnode>",
            "        <htmlnode>",
            "            Bye!",
            "        </htmlnode>",
            "    </body>",
            "</html>"
        ])
        assert page.build().to_html() == expected_html

    def test_page_with_stylesheet(self):
        """Tests that the HTML head links to a style sheet when necessary"""
        page = ww.Page()
        page.add(TestPage.Text("Text"))

        # Testing HTML before adding styled widget
        expected_html_after = "\n".join([
            "<!DOCTYPE html>",
            "<html>",
            "    <head></head>",
            "    <body>",
            "        <htmlnode>",
            "            Text",
            "        </htmlnode>",
            "    </body>",
            "</html>"
        ])
        assert page.build().to_html() == expected_html_after

        # Testing HTML after adding styled widget (a new <link> element should
        # be added to the head).
        page.add(TestPage.Styled())
        expected_html_after = "\n".join([
            "<!DOCTYPE html>",
            "<html>",
            "    <head>",
            '        <link href="styles.css" rel="stylesheet">',
            "    </head>",
            "    <body>",
            "        <htmlnode>",
            "            Text",
            "        </htmlnode>",
            "        <htmlnode></htmlnode>",
            "    </body>",
            "</html>"
        ])
        assert page.build().to_html() == expected_html_after

    @pytest.mark.parametrize("css_file_name",
                             ["style.css", "s.css", "css.css"])
    def test_page_with_custom_css_file_name(self, css_file_name):
        page = ww.Page([TestPage.Styled()])
        expected_html = "\n".join([
            "<!DOCTYPE html>",
            "<html>",
            "    <head>",
            f'        <link href="{css_file_name}" rel="stylesheet">',
            "    </head>",
            "    <body>",
            "        <htmlnode></htmlnode>",
            "    </body>",
            "</html>"
        ])
        assert page.build(
            css_file_name=css_file_name).to_html() == expected_html
