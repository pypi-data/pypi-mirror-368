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

import itertools
import pytest
import re
from webwidgets.compilation.css import apply_css, compile_css
from webwidgets.compilation.html import HTMLNode
from webwidgets.utility.validation import validate_css_comment, \
    validate_css_identifier, validate_css_selector, validate_css_value, \
    validate_html_class


class TestValidateCSS:
    @pytest.fixture
    def valid_css_identifiers(self):
        return [
            "i",
            "identifier",
            "identifier123",
            "myIdentifier",
            "myIdentifier123",
            "my-identifier-456",
            "my-Ident_ifier-456",
            "_identifier123",
            "_myIdentifier",
            "_my-Identifier456",
            "--myIdentifier",
            "--my-Identifier456"
        ]

    def test_valid_css_comments(self):
        """Test that valid CSS comments are accepted"""
        validate_css_comment("")  # Empty comment is valid
        validate_css_comment("This is a comment")
        validate_css_comment("Comment /* with an opening sequence")
        validate_css_comment("Many /* /* /* /* opening sequences")
        validate_css_comment("1234567890!#*?")
        validate_css_comment("*!/*H//*J/*J/*")  # Almost closing

    @pytest.mark.parametrize("comment", [
        "/* comment */", "comment */", "/*/", "abc /* 123 */"
    ])
    def test_invalid_css_comment(self, comment):
        with pytest.raises(ValueError, match=re.escape("*/")):
            validate_css_comment(comment)

    def test_valid_css_identifiers(self, valid_css_identifiers):
        """Test that valid CSS identifiers are accepted"""
        for identifier in valid_css_identifiers:
            validate_css_identifier(identifier)

    def test_invalid_css_identifier_empty(self):
        """Test that an invalid CSS identifier (that is empty) raises an exception"""
        with pytest.raises(ValueError, match="must start with"):
            validate_css_identifier("")

    def test_invalid_css_identifier_starting_with_digit(self):
        """Test that an invalid CSS identifier (starting with a digit) raises an exception"""
        with pytest.raises(ValueError, match="must start with"):
            validate_css_identifier("123my-class")

    def test_invalid_css_identifier_starting_with_single_hyphen(self):
        """Test that an invalid CSS identifier (starting with a single hyphen) raises an exception"""
        with pytest.raises(ValueError, match="must start with"):
            validate_css_identifier("-my-class")

    def test_invalid_css_identifier_starting_with_space(self):
        """Test that an invalid CSS identifier (starting with a space) raises an exception"""
        with pytest.raises(ValueError, match="must start with"):
            validate_css_identifier(" identifier")

    def test_invalid_css_identifier_ending_with_space(self):
        """Test that an invalid CSS identifier (ending with a space) raises an exception"""
        with pytest.raises(ValueError, match=r"Invalid character\(s\)"):
            validate_css_identifier("identifier ")

    def test_invalid_css_identifier_with_double_space(self):
        """Test that an invalid CSS identifier (containing double spaces) raises an exception"""
        with pytest.raises(ValueError, match=r"Invalid character\(s\).*  "):
            validate_css_identifier("myClass  myOtherClass")

    @pytest.mark.parametrize("char", "!@#$%^&*()<>?/|\\}{[\":;\'] ")
    def test_invalid_css_identifier_with_invalid_character(self, char):
        """Test that an invalid CSS identifier (containing an invalid character) raises an exception"""
        with pytest.raises(ValueError,
                           match=fr"Invalid character\(s\).*{re.escape(char)}"):
            validate_css_identifier(f"my-class-{char}")

    @pytest.mark.parametrize("chars", [
        "!@#", "$%&", "<>{}()[]", "*+=|;:'\""
    ])
    def test_invalid_characters_in_error_message(self, chars):
        """Test that invalid characters are all present in the error message"""
        with pytest.raises(ValueError, match=re.escape(', '.join(chars))):
            validate_css_identifier(f"my-class-{chars}")

    @pytest.mark.parametrize("code, chars, raise_on_start", [
        # Injection in class name
        ("rule{}custom-code", "{, }", False),
        ("rule {}custom-code", "  , {, }", False),

        # Injection in property name
        ("}custom-code", None, True),
        ("} custom-code", None, True),
        ("url(\"somewhere.com\")", "(, \", ., \", )", False),
    ])
    def test_code_injection_in_css_identifier(self, code, chars, raise_on_start):
        """Test that code injected into CSS identifier raises an exception"""
        match = (r"must start with.*:.*" + code) if raise_on_start else \
            (r"Invalid character\(s\).*" + re.escape(chars))
        with pytest.raises(ValueError, match=match):
            validate_css_identifier(code)

    def test_valid_css_identifiers_as_selectors(self, valid_css_identifiers):
        """Test that valid CSS identifiers are also valid selectors"""
        for identifier in valid_css_identifiers:
            validate_css_selector('.' + identifier)

    def test_special_css_selectors(self):
        """Testing all possible combinations of special CSS selectors with no
        repetition.
        """
        for i in (1, 2, 3):
            for c in itertools.combinations(["*", "*::before", "*::after"], i):
                for p in itertools.permutations(c):
                    validate_css_selector(", ".join(p))

    def test_invalid_empty_selector(self):
        """Tests that an empty selector raises an exception"""
        with pytest.raises(ValueError, match="selector must start with '.'"):
            validate_css_selector("")

    def test_non_special_selector_within_special_selectors(self):
        """Tests that a non-special selector within a combination of special
        selectors raises an exception"""
        with pytest.raises(ValueError, match="selector must start with '.'"):
            validate_css_selector("*, *::before, hello, *::after")

    def test_invalid_css_selector_extra_space(self):
        """Tests that an invalid combination of special selectors (with an
        extra space) raises an exception"""
        with pytest.raises(ValueError, match="selector must start with '.'"):
            validate_css_selector("*,  *::before")

    def test_invalid_non_special_css_selectors(self):
        """Tests that invalid CSS selectors are rejected as invalid identifiers"""
        with pytest.raises(ValueError, match="selector must start with '.'"):
            validate_css_selector("*::has()")
        with pytest.raises(ValueError, match="selector must start with '.'"):
            validate_css_selector("::before")
        with pytest.raises(ValueError, match=r"Invalid character\(s\).* !"):
            validate_css_selector(".h!")

    def test_valid_css_values(self):
        """Tests that valid CSS property values are accepted"""
        validate_css_value("abcdefghijklmnopqrstuvwxyz")
        validate_css_value("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        validate_css_value("0123456789")
        validate_css_value("9876543210px")
        validate_css_value("blue 0 0 5-5 30px")
        validate_css_value("4 orange 56")
        validate_css_value("4 oRAnGe  56")
        validate_css_value("border-box")
        validate_css_value("5 #ff0Az3 space-between auto 10%m")

    @pytest.mark.parametrize("char1", "!@$^&*()<>?/|\\}{[\":;\']")
    @pytest.mark.parametrize("char2", "}{")
    @pytest.mark.parametrize("use_char2", (False, True))
    def test_invalid_css_value_with_invalid_character(self, char1, char2,
                                                      use_char2):
        """Tests that an invalid CSS value (containing one or two invalid
        characters) raises an exception"""
        chars = ', '.join([char1, char2] if use_char2 else [char1])
        with pytest.raises(ValueError,
                           match=fr"Invalid character\(s\).*{re.escape(chars)}"):
            validate_css_value(f"red-{char1} 0{char2 if use_char2 else ''} px")


class TestValidateHTML:
    def test_valid_html_classes(self):
        """Test that valid HTML class attributes are accepted"""
        validate_html_class("")
        validate_html_class("z e r")
        validate_html_class("myClass myOtherClass")
        validate_html_class("myClass z myOtherClass3")
        validate_html_class("my-class123 my-other-class- _my-last-class4")

    def test_invalid_html_class_starting_with_space(self):
        """Test that an invalid HTML class attribute (starting with a space) raises an exception"""
        with pytest.raises(ValueError, match="cannot start nor end with a space"):
            validate_html_class(" myClass myOtherClass")

    def test_invalid_html_class_ending_with_space(self):
        """Test that an invalid HTML class attribute (ending with a space) raises an exception"""
        with pytest.raises(ValueError, match="cannot start nor end with a space"):
            validate_html_class("myClass myOtherClass ")

    def test_invalid_html_class_with_double_space(self):
        """Test that an invalid HTML class attribute (containing double spaces) raises an exception"""
        with pytest.raises(ValueError, match="cannot contain double spaces"):
            validate_html_class("myClass  myOtherClass")

    def test_invalid_html_class_with_invalid_identifiers(self):
        """Test that an invalid HTML class attribute with invalid CSS identifiers raises an exception"""
        with pytest.raises(ValueError, match=r"Invalid character\(s\).*!, @, #"):
            validate_html_class("my-class123 my-other-class-!@#")
        with pytest.raises(ValueError, match="must start with"):
            validate_html_class("my-class123 -ec4 my-other-class")

    @pytest.mark.parametrize("code, chars, raise_on_start", [
        # Exception are raised on first offending class before space
        (">custom-code", None, True),
        ("\">custom-code", None, True),
        ("c>custom-code", ">", False),
        ("c\">custom-code", "\", >", False),
        ("c\"> custom-code", "\", >", False),
        ("c\">custom-code<div class=\"", "\", >, <", False),
        ("c\"><script src=\"file.js\"></script>", "\", >, <", False),
    ])
    def test_code_injection_in_html_class(self, code, chars, raise_on_start):
        """Test that HTML code injected into class attribute raises an exception"""
        match = (r"must start with.*:.*" + code) if raise_on_start else \
            (r"Invalid character\(s\).*" + re.escape(chars))
        with pytest.raises(ValueError, match=match):
            validate_html_class(code)

    @pytest.mark.parametrize("class_in, valid", [
        (None, True),
        ("", True),
        ("c", True),
        ("c-2_", True),
        ("--c-", True),
        ("--c d mn r", True),
        (" ", False),  # Starts with space
        ("c 2", False),  # Starts with digit
        ("-c", False),  # Starts with single hyphen
        ("--c ", False),  # Ends with space
        ("--c d! r", False),  # Contains invalid character
    ])
    @pytest.mark.parametrize("add_c2_in", [False, True])
    def test_validation_within_apply_css(self, class_in, valid, add_c2_in):
        """Tests that valid class attributes make it through HTML rendering"""
        # Compiling and applying CSS to a tree
        c_in = None if class_in is None else ' '.join(
            ([class_in] if class_in else []) + (["c2"] if add_c2_in else []))
        tree = HTMLNode(
            attributes=None if c_in is None else {"class": c_in},
            style={"margin": "0", "padding": "0"},
            children=[
                HTMLNode(style={"margin": "0", "color": "blue"})
            ]
        )
        apply_css(compile_css(tree), tree)

        # Checking the final HTML code
        class_out = "c1 c2" if not c_in else (c_in +
                                              " c1" + ("" if add_c2_in else " c2"))
        expected_html = '\n'.join([
            f'<htmlnode class="{class_out}">',
            f'    <htmlnode class="c0 c1"></htmlnode>',
            '</htmlnode>'
        ])
        if valid:
            tree.validate_attributes()
            assert tree.to_html() == expected_html
        else:
            with pytest.raises(ValueError):
                tree.validate_attributes()
            with pytest.raises(ValueError):
                tree.to_html()

    @pytest.mark.parametrize("class_namer, valid", [
        (None, True),  # Default class namer
        (lambda _, i: f"rule{i}", True),
        (lambda _, i: f"r-{i + 1}", True),
        (lambda _, i: f"--r-{i + 1}", True),
        (lambda r, i: f"{list(r[i].declarations.items())[0][0][0]}{i}", True),
        (lambda _, i: str(i), False),  # Starts with digit
        (lambda _, i: f"-r{i}", False),  # Starts with single hyphen
        (lambda _, i: f"rule {i + 1}", False),  # Invalid character (space)
        (lambda _, i: f"r={i}", False),  # Invalid character (=)
        (lambda r, i: f"{list(r[i].declarations.items())[0]}",
         False),  # Invalid characters (comma...)
        (lambda _, i: f"r{i}" + "{}custom-code", False),  # Code injection
    ])
    def test_validation_within_to_css(self, class_namer, valid):
        """Tests that valid class attributes make it through CSS rendering"""
        tree = HTMLNode(
            style={"az": "5", "bz": "4"},
            children=[
                HTMLNode(style={"az": "5"}),
                HTMLNode(style={"bz": "10"}),
            ]
        )
        compiled_css = compile_css(tree, class_namer=class_namer)
        if valid:
            compiled_css.to_css()
        else:
            with pytest.raises(ValueError):
                compiled_css.to_css()
