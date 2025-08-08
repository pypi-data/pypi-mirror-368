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

import copy
import itertools
from typing import Any, Dict, List, Union
from webwidgets.utility.indentation import get_indentation
from webwidgets.utility.representation import ReprMixin
from webwidgets.utility.sanitizing import sanitize_html_text
from webwidgets.utility.validation import validate_html_class


class HTMLNode(ReprMixin):
    """Represents an HTML node (for example, a div or a span).
    """

    one_line: bool = False

    def __init__(self, children: List['HTMLNode'] = None,
                 attributes: Dict[str, str] = None, style: Dict[str, str] = None):
        """Creates an HTMLNode with optional children, attributes, and style.

        :param children: List of child HTML nodes. Defaults to an empty list.
        :type children: List[HTMLNode]
        :param attributes: Dictionary of attributes for the node. Defaults to an empty dictionary.
        :type attributes: Dict[str, str]
        :param style: Dictionary of CSS properties for the node. Defaults to an empty dictionary.
        :type style: Dict[str, str]
        """
        super().__init__()
        self.children = [] if children is None else children
        self.attributes = {} if attributes is None else attributes
        self.style = {} if style is None else style

    def _get_tag_name(self) -> str:
        """Returns the tag name of the HTML node.

        The tag name of a node object is the name of its class in lowercase.

        :return: The tag name of the HTML node.
        :rtype: str
        """
        return self.__class__.__name__.lower()

    def _render_attributes(self) -> str:
        """Renders the attributes of the HTML node into a string that can be added to the start tag.

        Attributes are sorted alphabetically by name.

        :return: A string containing all attribute key-value pairs separated by spaces.
        :rtype: str
        """
        return ' '.join(
            f'{k}="{v}"' for k, v in sorted(self.attributes.items())
        )

    @property
    def end_tag(self) -> str:
        """Returns the closing tag of the HTML node.

        :return: A string containing the closing tag of the element.
        :rtype: str
        """
        return f"</{self._get_tag_name()}>"

    @property
    def start_tag(self) -> str:
        """Returns the opening tag of the HTML node, including any attributes.

        Attributes are validated with :py:meth:`HTMLNode.validate_attributes`
        before rendering.

        :return: A string containing the opening tag of the element with its attributes.
        :rtype: str
        """
        # Rendering attributes
        self.validate_attributes()
        attributes = self._render_attributes()
        maybe_space = ' ' if attributes else ''

        # Building start tag
        return f"<{self._get_tag_name()}{maybe_space}{attributes}>"

    def add(self, child: 'HTMLNode') -> None:
        """Adds a child to the HTML node.

        :param child: The child to be added.
        """
        self.children.append(child)

    def copy(self, deep: bool = False) -> 'HTMLNode':
        """Returns a copy of the HTML node.

        This method is just a convenient wrapper around Python's
        `copy.copy()` and `copy.deepcopy()` methods.

        :param deep: If True, creates a deep copy of the node and its children,
            recursively. Otherwise, creates a shallow copy. Defaults to False.
        :type deep: bool
        :return: A new HTMLNode object that is a copy of the original.
        :rtype: HTMLNode
        """
        if deep:
            return copy.deepcopy(self)
        return copy.copy(self)

    def get_styles(self) -> Dict[int, Dict[str, str]]:
        """Returns a dictionary mapping the node and all its children,
        recursively, to their style.

        Nodes are identified by their ID as obtained from Python's built-in
        `id()` function.

        :return: A dictionary mapping node IDs to styles.
        :rtype: Dict[int, Dict[str, str]]
        """
        styles = {id(self): self.style}
        for child in self.children:
            styles.update(child.get_styles())
        return styles

    def to_html(self, collapse_empty: bool = True,
                indent_size: int = 4, indent_level: int = 0,
                force_one_line: bool = False, return_lines: bool = False,
                **kwargs: Any) -> Union[str, List[str]]:
        """Converts the HTML node into HTML code.

        :param collapse_empty: If True, collapses elements without any children
            into a single line. Defaults to True.
        :type collapse_empty: bool
        :param indent_size: The number of spaces to use for each indentation level.
        :type indent_size: int
        :param indent_level: The current level of indentation in the HTML
            output.

            This argument supports negative values as a way to flatten the HTML
            output down to a certain depth with indentation resuming as normal
            afterwards. If negative, `indent_level` is construed as an offset
            on the depth in the HTML tree represented by the node, in which
            case the node will wait for that depth before starting indentation.
        :type indent_level: int
        :param force_one_line: If True, forces all child elements to be rendered on a single line without additional
            indentation. Defaults to False.
        :type force_one_line: bool
        :param return_lines: Whether to return the lines of HTML code individually. Defaults to False.
        :type return_lines: bool
        :param **kwargs: Additional keyword arguments to pass down to child elements.
        :type **kwargs: Any
        :return: A string containing the HTML representation of the element if
            `return_lines` is `False` (default), or the list of individual lines
            from that HTML code if `return_lines` is `True`.
        :rtype: str or List[str]
        """
        # Opening the element
        indentation = "" if force_one_line else get_indentation(
            indent_level, indent_size)
        html_lines = [indentation + self.start_tag]

        # If content must be in one line
        if self.one_line or force_one_line or (collapse_empty
                                               and not self.children):
            html_lines += list(itertools.chain.from_iterable(
                [c.to_html(collapse_empty=collapse_empty,
                           indent_level=0, force_one_line=True, return_lines=True,
                           **kwargs)
                 for c in self.children]))
            html_lines += [self.end_tag]
            html_lines = [''.join(html_lines)]  # Flattening the line

        # If content spans multi-line
        else:
            html_lines += list(itertools.chain.from_iterable(
                [c.to_html(collapse_empty=collapse_empty,
                           indent_size=indent_size,
                           indent_level=indent_level + 1,
                           return_lines=True,
                           **kwargs)
                 for c in self.children]))
            html_lines += [indentation + self.end_tag]
            html_lines = [l for l in html_lines if any(
                c != ' ' for c in l)]  # Trimming empty lines

        # If return_lines is True, return a list of lines
        if return_lines:
            return html_lines

        # Otherwise, return a single string
        return '\n'.join(html_lines)

    def validate_attributes(self) -> None:
        """Validate the node's attributes and raises an exception with a
        descriptive error message if any attribute is invalid.
        """
        if "class" in self.attributes:
            validate_html_class(self.attributes["class"])


def no_start_tag(cls):
    """Decorator to remove the start tag from an HTMLNode subclass.

    :param cls: A subclass of HTMLNode whose start tag should be removed.
    :return: The given class with an empty start tag.
    """
    cls.start_tag = property(
        lambda _: '', doc="This element does not have a start tag")
    return cls


def no_end_tag(cls):
    """Decorator to remove the end tag from an HTMLNode subclass.

    :param cls: A subclass of HTMLNode whose end tag should be removed.
    :return: The given class with an empty end tag.
    """
    cls.end_tag = property(
        lambda _: '', doc="This element does not have an end tag")
    return cls


def one_line(cls):
    """Decorator to make an HTMLNode subclass a one-line element.

    :param cls: A subclass of HTMLNode.
    :return: The given class with the `one_line` attribute set to True.
    """
    cls.one_line = True
    return cls


@no_start_tag
@no_end_tag
@one_line
class RawText(HTMLNode):
    """A raw text node that contains text without any HTML tags."""

    def __init__(self, text: str):
        """Creates a raw text node.

        :param text: The text content of the node. It will be sanitized in
            :py:meth:`RawText.to_html` before being written into HTML code.
        :type text: str
        """
        super().__init__()
        self.text = text

    def to_html(self, indent_size: int = 4, indent_level: int = 0,
                return_lines: bool = False, replace_all_entities: bool = False,
                **kwargs: Any) -> Union[str, List[str]]:
        """Converts the raw text node to HTML.

        The text is sanitized by the :py:func:`sanitize_html_text` function before
        being written into HTML code.

        :param indent_size: See :py:meth:`HTMLNode.to_html`.
        :type indent_size: int
        :param indent_level: See :py:meth:`HTMLNode.to_html`.
        :type indent_level: int
        :param return_lines: See :py:meth:`HTMLNode.to_html`.
        :type return_lines: bool
        :param replace_all_entities: See :py:func:`sanitize_html_text`.
        :type replace_all_entities: bool
        :param kwargs: Other keyword arguments. These are ignored.
        :type kwargs: Any
        :return: See :py:meth:`HTMLNode.to_html`.
        :rtype: str or List[str]
        """
        sanitized = sanitize_html_text(
            self.text, replace_all_entities=replace_all_entities)
        line = get_indentation(indent_level, indent_size) + sanitized
        if return_lines:
            return [line]
        return line


@no_start_tag
@no_end_tag
class RootNode(HTMLNode):
    """The root node of an HTML document.

    This is the top-level node that contains all other nodes.
    """

    def to_html(self, indent_level: int = 0, **kwargs: Any) -> Union[str, List[str]]:
        """Converts the root node to HTML code.

        This method overrides :py:meth:`HTMLNode.to_html`. The only difference
        between this method and that of the base class is that the indentation
        level is adjusted by one level, so the root node acts as an array of
        elements.

        :param indent_level: See :py:meth:`HTMLNode.to_html`.
        :type indent_level: int
        :param kwargs: Other keyword arguments. These are passed to
            :py:meth:`HTMLNode.to_html`.
        :type kwargs: Any
        :return: See :py:meth:`HTMLNode.to_html`.
        :type return: str or List[str]
        """
        return super().to_html(indent_level=indent_level - 1, **kwargs)
