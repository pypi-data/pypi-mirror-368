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
from webwidgets.compilation.css.css_rule import ClassRule, CSSRule


class TestClassRule:
    def test_class_rule_to_css(self):
        rule = ClassRule("class-name", {"color": "red", "margin": "0"})
        expected_css = '\n'.join([
            ".class-name {",
            "    color: red;",
            "    margin: 0;",
            "}"
        ])
        assert rule.to_css() == expected_css

    def test_empty_class_rule_to_css(self):
        rule = ClassRule("my-name", {})
        expected_css = '\n'.join([
            ".my-name {",
            "}"
        ])
        assert rule.to_css() == expected_css

    @pytest.mark.parametrize("indent_size", [0, 1, 2, 3, 4])
    def test_class_rule_indentation(self, indent_size):
        rule = ClassRule("class-name", {"color": "red", "margin": "0"})
        expected_css = '\n'.join([
            ".class-name {",
            f"{' ' * indent_size}color: red;",
            f"{' ' * indent_size}margin: 0;",
            "}"
        ])
        assert rule.to_css(indent_size=indent_size) == expected_css

    @pytest.mark.parametrize("name", [
        "3rule", "hi!", "Wrong name", "-invalid"
    ])
    def test_invalid_class_class_name(self, name):
        rule = ClassRule(name, {"property": "value"})
        with pytest.raises(ValueError, match=name):
            rule.to_css()

    @pytest.mark.parametrize("property_name", [
        "3prop", "hi!", "Wrong name", "-invalid"
    ])
    def test_invalid_property_name(self, property_name):
        rule = ClassRule("class-name", {property_name: "value"})
        with pytest.raises(ValueError, match=property_name):
            rule.to_css()


class TestCSSRule:
    def test_rule_to_css(self):
        rule = CSSRule(".rule-name", {"color": "red", "margin": "0"})
        expected_css = '\n'.join([
            ".rule-name {",
            "    color: red;",
            "    margin: 0;",
            "}"
        ])
        assert rule.to_css() == expected_css

    def test_empty_rule_to_css(self):
        rule = CSSRule(".my-selector", {})
        expected_css = '\n'.join([
            ".my-selector {",
            "}"
        ])
        assert rule.to_css() == expected_css

    @pytest.mark.parametrize("indent_size", [0, 1, 2, 3, 4])
    def test_rule_indentation(self, indent_size):
        rule = CSSRule(".rule-selector", {"color": "red", "margin": "0"})
        expected_css = '\n'.join([
            ".rule-selector {",
            f"{' ' * indent_size}color: red;",
            f"{' ' * indent_size}margin: 0;",
            "}"
        ])
        assert rule.to_css(indent_size=indent_size) == expected_css

    @pytest.mark.parametrize("selector", [
        ".3rule", ".hi!", ".Wrong name", ".-invalid",
    ])
    def test_invalid_rule_selector(self, selector):
        rule = CSSRule(selector, {"property": "value"})
        with pytest.raises(ValueError, match=selector):
            rule.to_css()

    @pytest.mark.parametrize("property_name", [
        "3prop", "hi!", "Wrong name", "-invalid"
    ])
    def test_invalid_property_name(self, property_name):
        rule = CSSRule(".rule", {property_name: "value"})
        with pytest.raises(ValueError, match=property_name):
            rule.to_css()
