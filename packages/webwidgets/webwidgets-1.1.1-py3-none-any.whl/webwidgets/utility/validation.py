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

import re


# CSS selectors that are considered valid as selectors but not as identifiers
# according to the `validate_css_identifier()` function.
SPECIAL_SELECTORS = [
    "*", "*::before", "*::after"
]


def validate_css_comment(comment: str) -> None:
    """Checks if the given comment is a valid CSS comment according to the CSS
    syntax rules and raises an exception if not.

    This function just checks that the comment does not contain any closing
    sequence `*/` as defined in the CSS Syntax Module Level 3, paragraph 4.3.2
    (see source: https://www.w3.org/TR/css-syntax-3/#consume-comment).

    :param comment: The CSS comment to validate, without its opening and
        closing sequences. It can include any number of opening sequences
        (`/*`) as part of its content, in which case it is still a valid
        comment per the CSS specification, but it cannot contain any closing
        sequences (`*/`).
    :type comment: str
    :raises ValueError: If the comment is not a valid CSS comment.
    """
    if "*/" in comment:
        raise ValueError(
            f"Invalid CSS comment: '{comment}' contains closing sequence '*/'")


def validate_css_identifier(identifier: str) -> None:
    """Checks if the given identifier is a valid identifier token according to
    the CSS syntax rules and raises an exception if not.

    An identifier token is a sequence of characters that can be used as part of
    a CSS rule, like a class name or an ID. The concept essentially corresponds
    to that of an `ident-token` in the official CSS specification.

    This function enforces the following rules:
    - the identifier must only contain letters (`a-z`, `A-Z`), digits (`0-9`),
      underscores (`_`), and hyphens (`-`)
    - the identifier must start with either a letter, an underscore, or a
      double hyphen (`--`)

    Note that this function imposes stricter rules on identifier tokens than
    the official CSS specification - more precisely, than chapter 4 of the CSS
    Syntax Module Level 3 (see source:
    https://www.w3.org/TR/css-syntax-3/#tokenization - note that this chapter
    remains the same in the current draft for Level 4). For example, this
    function does not allow escaped special characters nor identifier tokens
    starting with a single hyphen whereas the specification does.

    :param identifier: The string to be validated as an identifier token.
    :type identifier: str
    :raises ValueError: If the identifier is not a valid identifier token and
        does not respect the specified rules.
    """
    # Check if identifier starts with anything else than a letter, an
    # underscore, or a double hyphen
    if not re.match(r'^[a-zA-Z_]+|--', identifier):
        raise ValueError("CSS identifier must start with either a letter, an "
                         "underscore, or a double hyphen (`--`), but got: "
                         f"'{identifier}'")

    # Check if identifier contains invalid characters
    if not re.match(r'^[a-zA-Z0-9_-]+$', identifier):
        invalid_chars = re.findall('[^a-zA-Z0-9_-]', identifier)
        raise ValueError("Invalid character(s) in CSS idenfitier "
                         f"'{identifier}': {', '.join(invalid_chars)}\n"
                         "Only letters, digits, hyphens, and underscores are "
                         "allowed.")


def validate_css_selector(selector: str) -> None:
    """Checks if the given CSS selector is valid and raises an exception if
    not.

    To be valid, the selector must either be:
    - a special selector, which is defined as either `*`, `*::before`, or
      `*::after`
    - any combination of special selectors separated by a comma and a single
      space (e.g. `*::before, *::after`)
    - or a class selector, which is defined as a dot `.` followed by a valid
      CSS identifier, as defined and enforced by the
      :py:func:`validate_css_identifier` function

    Note that this function imposes stricter rules than the official CSS
    Selector Level 4 specification (see source:
    https://www.w3.org/TR/selectors-4/). For example, this function does not
    allow selectors with the relational pseudo-class `:has()` whereas the
    specification does.

    :param selector: The CSS selector to validate.
    :type selector: str
    :raises ValueError: If the selector is not a special selector nor a valid
        CSS identifier.
    """
    # Checking if the selector is a special selector
    if selector in SPECIAL_SELECTORS:
        return

    # Checking if the selector is a combination of special selectors
    if all(part in SPECIAL_SELECTORS for part in selector.split(", ")):
        return

    # Otherwise, checking if the selector is a class selector
    if not selector.startswith("."):
        raise ValueError("Class selector must start with '.' but got: "
                         f"{selector}")
    validate_css_identifier(selector[1:])


def validate_css_value(value: str) -> None:
    """Checks if the given value is a valid CSS property value and raises an
    exception if not.

    To be valid, the value must only contain:
    - letters (`a-z`, `A-Z`)
    - digits (`0-9`)
    - dots (`.`)
    - spaces (` `)
    - hyphens (`-`)
    - percent characters (`%`)
    - hashtags (`#`)

    Note that this function imposes stricter rules than the official CSS
    specification - more precisely, than chapter 2 of the CSS Values and Units
    Module Level 3 (see source:
    https://www.w3.org/TR/css-values-3/#value-defs). For example, this function
    does not allow functional notations like `calc()` whereas the specification
    does.

    :param value: The value to validate as a CSS property value.
    :type value: str
    :raises ValueError: If the value is not a valid CSS property value.
    """
    if not re.match(r'^[a-zA-Z0-9. \-%#]+$', value):
        invalid_chars = re.findall(r'[^a-zA-Z0-9. \-%#]', value)
        raise ValueError("Invalid character(s) in CSS property value "
                         f"'{value}': {', '.join(invalid_chars)}\n"
                         "Only letters, digits, dots, spaces, hyphens, "
                         "percent characters, and hashtags are allowed.")


def validate_html_class(class_attribute: str) -> None:
    """Checks if the given HTML class attribute is valid and raises an
    exception if not.

    This function enforces the following rules:
    - the class attribute cannot start nor end with a space
    - the class attribute cannot contain double spaces
    - each class in the attribute must be a valid CSS identifier, as validated
      by the :py:func:`validate_css_identifier` function

    Note that this function imposes stricter rules than rule 2.3.7 of the HTML5
    specification (see source:
    https://html.spec.whatwg.org/#set-of-space-separated-tokens). For example,
    it does not allow for leading nor trailing spaces whereas the specification
    does.

    :param class_attribute: The HTML class attribute to be validated.
    :type class_attribute: str
    :raises ValueError: If the class attribute is invalid and does not respect
        the specified rules.
    """
    # Allow for empty attribute
    if not class_attribute:
        return

    # Check if the class attribute starts or ends with a space
    if class_attribute.startswith(' ') or class_attribute.endswith(' '):
        raise ValueError("Class attribute cannot start nor end with a space, "
                         f"but got: '{class_attribute}'")

    # Check for double spaces in the class attribute
    if '  ' in class_attribute:
        raise ValueError("Class attribute cannot contain double spaces, "
                         f"but got: '{class_attribute}'")

    # Check each class individually
    for c in class_attribute.split(' '):
        validate_css_identifier(c)
