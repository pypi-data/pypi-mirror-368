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
from webwidgets.compilation.css.css_rule import CSSRule
from webwidgets.compilation.css.sections.css_section import CSSSection
from webwidgets.compilation.css.sections.preamble import Preamble
from webwidgets.compilation.css.sections.rule_section import RuleSection


class TestPreamble:
    def test_preamble_is_rule_section(self):
        preamble = Preamble()
        assert isinstance(preamble, CSSSection)
        assert isinstance(preamble, RuleSection)

    def test_preamble_to_css(self):
        preamble = Preamble()
        expected_css = '\n'.join([
            "/* " + CSSSection.prettify_title("Preamble", 40) + " */",
            "",
            "*, *::before, *::after {",
            "    box-sizing: border-box;",
            "    margin: 0;",
            "    padding: 0;",
            "    overflow: hidden;",
            "}"
        ])
        assert preamble.to_css() == expected_css


class TestCSSSection:
    def test_css_section_is_abstract(self):
        with pytest.raises(TypeError, match="compile_content"):
            CSSSection("title")

    def test_prettify_empty_title(self):
        assert CSSSection.prettify_title("", 0) == ""
        for i in range(1, 5):
            assert CSSSection.prettify_title("", i) == "=  ="
        for i in range(5, 16):
            characters = "=" * ((i - 1) // 2)
            assert CSSSection.prettify_title(
                "", i) == f"{characters}  {characters}"

    @pytest.mark.parametrize("title", ["Title", "Section", "a" * 16])
    def test_prettify_basic_titles(self, title: str):
        pretty_title = CSSSection.prettify_title(title, 20)
        characters = '=' * ((19 - len(title)) // 2)
        assert pretty_title == f"{characters} {title} {characters}"

    def test_pretty_title_is_over_min_length(self):
        for min_length in range(8):
            for i in range(min_length + 1):
                pretty_title = CSSSection.prettify_title("a" * i, min_length)
                assert len(pretty_title) >= min_length

    def test_pretty_title_is_minimum_length(self):
        # Minimum length is defined as at most a constant number of characters
        # over min_length
        for min_length in range(8):
            for i in range(min_length + 1):
                pretty_title = CSSSection.prettify_title("a" * i, min_length)
                assert len(pretty_title) <= min_length + 4

    def test_pretty_title_is_symmetric(self):
        for i in range(8):
            pretty_title = CSSSection.prettify_title("a" * i, 8)
            assert pretty_title[::-1] == pretty_title


class TestRuleSection:
    def test_compile_content_one_rule(self):
        section = RuleSection([
            CSSRule(".rule", {"property": "value"})
        ])
        expected_css = '\n'.join([
            ".rule {",
            "    property: value;",
            "}"
        ])
        assert section.compile_content() == expected_css
        section.title = "title"  # Shouldn't impact content
        assert section.compile_content() == expected_css

    def test_compile_content_multiple_rules(self):
        section = RuleSection([
            CSSRule(".ruleA", {"p1": "v1", "p2": "v2"}),
            CSSRule(".ruleB", {"p1": "x", "q1": "y"}),
            CSSRule(".rC", {"a": "u", "b": "v"})
        ])
        expected_css = '\n'.join([
            ".ruleA {",
            "    p1: v1;",
            "    p2: v2;",
            "}",
            "",
            ".ruleB {",
            "    p1: x;",
            "    q1: y;",
            "}",
            "",
            ".rC {",
            "    a: u;",
            "    b: v;",
            "}"
        ])
        assert section.compile_content() == expected_css
        section.title = "title"  # Shouldn't impact content
        assert section.compile_content() == expected_css

    @pytest.mark.parametrize("indent_size", [0, 2, 3, 4])
    def test_compile_content_indentation(self, indent_size: int):
        section = RuleSection([
            CSSRule(".rule", {"property": "value"})
        ])
        expected_css = '\n'.join([
            ".rule {",
            f"{' ' * indent_size}property: value;",
            "}"
        ])
        assert section.compile_content(
            indent_size=indent_size) == expected_css

    def test_to_css_no_title(self):
        section = RuleSection([
            CSSRule(".rule", {"property": "value"}),
        ])
        expected_css = '\n'.join([
            ".rule {",
            "    property: value;",
            "}"
        ])
        assert section.to_css() == expected_css

    def test_to_css_with_title(self):
        section = RuleSection([
            CSSRule(".rule", {"property": "value"}),
        ], "title")
        symbols = "=" * 17
        expected_css = '\n'.join([
            f"/* {symbols} title {symbols} */",
            "",
            ".rule {",
            "    property: value;",
            "}"
        ])
        assert section.to_css() == expected_css

    @pytest.mark.parametrize("indent_size", [0, 2, 3, 4])
    def test_to_css_passes_down_indentation_no_title(self, indent_size: int):
        section = RuleSection([
            CSSRule(".rule", {"property": "value"}),
        ])
        expected_css = '\n'.join([
            ".rule {",
            f"{' ' * indent_size}property: value;",
            "}"
        ])
        assert section.to_css(indent_size=indent_size) == expected_css

    @pytest.mark.parametrize("indent_size", [0, 2, 3, 4])
    @pytest.mark.parametrize("title", ["title", "Hello", "World"])
    def test_to_css_passes_down_indentation_with_title(self,
                                                       indent_size: int,
                                                       title: str):
        section = RuleSection([
            CSSRule(".rule", {"property": "value"}),
        ], title)
        symbols = "=" * 17
        expected_css = '\n'.join([
            f"/* {symbols} {title} {symbols} */",
            "",
            ".rule {",
            f"{' ' * indent_size}property: value;",
            "}"
        ])
        assert section.to_css(indent_size=indent_size) == expected_css

    @pytest.mark.parametrize("title", ["Title */", "No*/*", "/*/"])
    def test_invalid_title(self, title: str):
        with pytest.raises(ValueError, match="Invalid CSS comment"):
            RuleSection([], title).to_css()
