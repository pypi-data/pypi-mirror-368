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
from typing import Dict
import webwidgets as ww
from webwidgets.compilation.html.html_node import HTMLNode, RawText


class TestWebsite:
    class Empty(ww.Widget):
        def build(self):
            return HTMLNode()

    class Text(ww.Widget):
        def __init__(self, text: str, style: Dict[str, str] = None):
            super().__init__()
            self.text = text
            self.style = style

        def build(self):
            return HTMLNode(children=[RawText(self.text)], style=self.style)

    class SimpleWebsite(ww.Website):
        def __init__(self):
            page = ww.Page([
                TestWebsite.Text("Text!", {"padding": "0"}),
                TestWebsite.Text("Another Text!", {"margin": "0"}),
            ])
            super().__init__([page])

    @pytest.mark.parametrize("num_pages", [1, 2, 3])
    @pytest.mark.parametrize("num_widgets", [1, 2, 3])
    @pytest.mark.parametrize("text", ["a", "b", "c"])
    def test_compile_website_without_css(self, num_pages, num_widgets, text,
                                         wrap_core_css):
        # Create a new website object
        website = ww.Website()
        for _ in range(num_pages):
            website.add(ww.Page([TestWebsite.Text(text)] * num_widgets))

        # Compile the website to HTML
        compiled = website.compile()

        # Check if the compiled HTML contains the expected code
        expected_html = "\n".join([
            "<!DOCTYPE html>",
            "<html>",
            "    <head></head>",
            "    <body>"
        ]) + "\n" + "\n".join([
            "        <htmlnode>",
            f"            {text}",
            "        </htmlnode>",
        ] * num_widgets) + "\n" + "\n".join([
            "    </body>",
            "</html>"
        ])
        assert len(compiled.html_content) == num_pages
        assert all(c == expected_html for c in compiled.html_content)

        # Check if the compiled CSS contains the expected code
        assert compiled.css_content == wrap_core_css("")  # No core CSS here

    @pytest.mark.parametrize("num_pages", [1, 2, 3, 4, 5, 6])
    @pytest.mark.parametrize("num_widgets", [1, 2, 3])
    @pytest.mark.parametrize("text", ["a", "b", "c"])
    def test_compile_website_with_css(self, num_pages, num_widgets, text,
                                      wrap_core_css):
        # Defining a set of styles to pick from
        styles = [{"margin": "0"}, {"color": "blue"}, {"font-size": "16px"}]

        # Compile expected class names based on number of pages involved
        class_names = {
            1: ["c0"],
            2: ["c1", "c0"],
            3: ["c2", "c0", "c1"]
        }
        for k in range(4, num_pages + 1):
            class_names[k] = [
                class_names[3][i % len(styles)] for i in range(k)]

        # Create a new website object
        website = ww.Website()
        for i in range(num_pages):
            website.add(
                ww.Page([
                    TestWebsite.Text(text, styles[i % len(styles)])
                ] * num_widgets))

        # Compile the website to HTML
        compiled = website.compile()

        # Check if the compiled HTML contains the expected code
        expected_html = [(
            "\n".join([
                "<!DOCTYPE html>",
                "<html>",
                "    <head>",
                '        <link href="styles.css" rel="stylesheet">',
                "    </head>",
                "    <body>"
            ]) + "\n" + "\n".join([
                f'        <htmlnode class="{class_names[num_pages][i % len(class_names)]}">',
                f"            {text}",
                "        </htmlnode>",
            ] * num_widgets) + "\n" + "\n".join([
                "    </body>",
                "</html>"
            ])) for i in range(num_pages)]
        assert compiled.html_content == expected_html

        # Check if the compiled CSS contains the expected code
        sorted_rules = sorted(list(set(
            zip(class_names[num_pages],
                [list(styles[i % len(styles)].items())[0]
                 for i in range(num_pages)]))), key=lambda x: x[0])
        expected_core_css = "\n\n".join([
            '\n'.join([
                f".{name} " + "{",
                f"    {p}: {v};",
                "}"
            ]) for name, (p, v) in sorted_rules
        ])
        assert compiled.css_content == wrap_core_css(expected_core_css)

    def test_compile_collapse_empty(self, wrap_core_css):
        website = ww.Website([ww.Page([TestWebsite.Empty()])])

        # Collapse empty elements
        compiled_true = website.compile(collapse_empty=True)
        expected_html_true = "\n".join([
            "<!DOCTYPE html>",
            "<html>",
            "    <head></head>",
            "    <body>",
            "        <htmlnode></htmlnode>",
            "    </body>",
            "</html>"
        ])
        assert len(compiled_true.html_content) == 1
        assert compiled_true.html_content[0] == expected_html_true
        assert compiled_true.css_content == wrap_core_css("")

        # Don't collapse empty elements
        compiled_false = website.compile(collapse_empty=False)
        expected_html_false = "\n".join([
            "<!DOCTYPE html>",
            "<html>",
            "    <head>",
            "    </head>",
            "    <body>",
            "        <htmlnode>",
            "        </htmlnode>",
            "    </body>",
            "</html>"
        ])
        assert len(compiled_false.html_content) == 1
        assert compiled_false.html_content[0] == expected_html_false
        assert compiled_false.css_content == wrap_core_css("")

    @pytest.mark.parametrize("css_file_name",
                             ["style.css", "s.css", "css.css"])
    def test_compile_css_file_name(self, css_file_name, wrap_core_css):
        website = TestWebsite.SimpleWebsite()
        compiled = website.compile(css_file_name=css_file_name)
        expected_html = "\n".join([
            "<!DOCTYPE html>",
            "<html>",
            "    <head>",
            f'        <link href="{css_file_name}" rel="stylesheet">',
            "    </head>",
            "    <body>",
            '        <htmlnode class="c1">',
            "            Text!",
            "        </htmlnode>",
            '        <htmlnode class="c0">',
            "            Another Text!",
            "        </htmlnode>",
            "    </body>",
            "</html>"
        ])
        expected_core_css = "\n".join([
            ".c0 {",
            "    margin: 0;",
            "}",
            "",
            ".c1 {",
            "    padding: 0;",
            "}"
        ])
        assert len(compiled.html_content) == 1
        assert compiled.html_content[0] == expected_html
        assert compiled.css_content == wrap_core_css(expected_core_css)

    def test_compile_force_one_line(self, wrap_core_css):
        website = TestWebsite.SimpleWebsite()
        expected_core_css = "\n".join([
            ".c0 {",
            "    margin: 0;",
            "}",
            "",
            ".c1 {",
            "    padding: 0;",
            "}"
        ])

        # Force one line HTML
        compiled_true = website.compile(force_one_line=True)
        expected_html_true = ''.join([
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            '<link href="styles.css" rel="stylesheet">',
            "</head>",
            "<body>",
            '<htmlnode class="c1">',
            "Text!",
            "</htmlnode>",
            '<htmlnode class="c0">',
            "Another Text!",
            "</htmlnode>",
            "</body>",
            "</html>"
        ])
        assert len(compiled_true.html_content) == 1
        assert compiled_true.html_content[0] == expected_html_true
        assert compiled_true.css_content == wrap_core_css(expected_core_css)

        # Don't force one line HTML
        compiled_false = website.compile(force_one_line=False)
        expected_html_false = "\n".join([
            "<!DOCTYPE html>",
            "<html>",
            "    <head>",
            '        <link href="styles.css" rel="stylesheet">',
            "    </head>",
            "    <body>",
            '        <htmlnode class="c1">',
            "            Text!",
            "        </htmlnode>",
            '        <htmlnode class="c0">',
            "            Another Text!",
            "        </htmlnode>",
            "    </body>",
            "</html>"
        ])
        assert len(compiled_false.html_content) == 1
        assert compiled_false.html_content[0] == expected_html_false
        assert compiled_false.css_content == wrap_core_css(expected_core_css)

    @pytest.mark.parametrize("indent_level", [0, 1, 2])
    @pytest.mark.parametrize("indent_size", [2, 3, 4, 8])
    def test_compile_indentation(self, indent_level: int, indent_size: int,
                                 wrap_core_css):
        """Test the `compile` method with custom indentation levels and sizes."""
        website = TestWebsite.SimpleWebsite()
        compiled = website.compile(
            indent_level=indent_level,
            indent_size=indent_size
        )

        # Check the results
        expected_html = "\n".join([
            f"{' ' * indent_size * indent_level}<!DOCTYPE html>",
            f"{' ' * indent_size * indent_level}<html>",
            f"{' ' * indent_size * (indent_level + 1)}<head>",
            f'{" " * indent_size * (indent_level + 2)}<link href="styles.css" rel="stylesheet">',
            f"{' ' * indent_size * (indent_level + 1)}</head>",
            f"{' ' * indent_size * (indent_level + 1)}<body>",
            f'{" " * indent_size * (indent_level + 2)}<htmlnode class="c1">',
            f"{' ' * indent_size * (indent_level + 3)}Text!",
            f"{' ' * indent_size * (indent_level + 2)}</htmlnode>",
            f'{" " * indent_size * (indent_level + 2)}<htmlnode class="c0">',
            f"{' ' * indent_size * (indent_level + 3)}Another Text!",
            f"{' ' * indent_size * (indent_level + 2)}</htmlnode>",
            f"{' ' * indent_size * (indent_level + 1)}</body>",
            f"{' ' * indent_size * indent_level}</html>"
        ])
        assert len(compiled.html_content) == 1
        assert compiled.html_content[0] == expected_html
        expected_core_css = "\n".join([
            ".c0 {",
            f"{' ' * indent_size}margin: 0;",
            "}",
            "",
            ".c1 {",
            f"{' ' * indent_size}padding: 0;",
            "}"
        ])
        assert compiled.css_content == wrap_core_css(
            expected_core_css, indent_size=indent_size)

    @pytest.mark.parametrize("indent_level", [-2, -1])
    def test_compile_negative_indent_levels(self, indent_level: int,
                                            wrap_core_css):
        website = TestWebsite.SimpleWebsite()
        compiled = website.compile(indent_level=indent_level)
        indent = "    " if indent_level == -1 else ""
        expected_html = "\n".join([
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f'{indent}<link href="styles.css" rel="stylesheet">',
            "</head>",
            "<body>",
            f'{indent}<htmlnode class="c1">',
            f"{indent}    Text!",
            f"{indent}</htmlnode>",
            f'{indent}<htmlnode class="c0">',
            f"{indent}    Another Text!",
            f"{indent}</htmlnode>",
            "</body>",
            "</html>"
        ])
        expected_core_css = "\n".join([
            ".c0 {",
            "    margin: 0;",
            "}",
            "",
            ".c1 {",
            "    padding: 0;",
            "}"
        ])
        assert len(compiled.html_content) == 1
        assert compiled.html_content[0] == expected_html
        assert compiled.css_content == wrap_core_css(expected_core_css)

    def test_compile_class_namer(self, wrap_core_css):
        """Test the `compile` method with a custom class namer function."""
        # Define a custom class namer function
        def custom_class_namer(rules, index):
            return f"custom_{index}_{list(rules[index].declarations.keys())[0]}"

        # Compile a simple website with the custom class namer
        website = TestWebsite.SimpleWebsite()
        compiled = website.compile(class_namer=custom_class_namer)

        # Check the results
        expected_html = "\n".join([
            "<!DOCTYPE html>",
            "<html>",
            "    <head>",
            '        <link href="styles.css" rel="stylesheet">',
            "    </head>",
            "    <body>",
            '        <htmlnode class="custom_1_padding">',
            "            Text!",
            "        </htmlnode>",
            '        <htmlnode class="custom_0_margin">',
            "            Another Text!",
            "        </htmlnode>",
            "    </body>",
            "</html>"
        ])
        assert len(compiled.html_content) == 1
        assert compiled.html_content[0] == expected_html
        expected_core_css = "\n".join([
            ".custom_0_margin {",
            "    margin: 0;",
            "}",
            "",
            ".custom_1_padding {",
            "    padding: 0;",
            "}"
        ])
        assert compiled.css_content == wrap_core_css(expected_core_css)

    def test_compile_kwargs(self, wrap_core_css):
        website = TestWebsite.SimpleWebsite()
        compiled = website.compile(replace_all_entities=True)
        expected_html = "\n".join([
            "<!DOCTYPE html>",
            "<html>",
            "    <head>",
            '        <link href="styles.css" rel="stylesheet">',
            "    </head>",
            "    <body>",
            '        <htmlnode class="c1">',
            "            Text&excl;",
            "        </htmlnode>",
            '        <htmlnode class="c0">',
            "            Another Text&excl;",
            "        </htmlnode>",
            "    </body>",
            "</html>"
        ])
        expected_core_css = "\n".join([
            ".c0 {",
            "    margin: 0;",
            "}",
            "",
            ".c1 {",
            "    padding: 0;",
            "}"
        ])
        assert len(compiled.html_content) == 1
        assert compiled.html_content[0] == expected_html
        assert compiled.css_content == wrap_core_css(expected_core_css)
