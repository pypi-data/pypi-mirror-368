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

from .css_rule import ClassRule
import itertools
from .sections.preamble import Preamble
from .sections.rule_section import RuleSection
from typing import Callable, Dict, List, Union
from webwidgets.compilation.html.html_node import HTMLNode
from webwidgets.utility.representation import ReprMixin


class CompiledCSS(ReprMixin):
    """A utility class to hold compiled CSS rules.
    """

    def __init__(self, trees: List[HTMLNode], core: RuleSection,
                 mapping: Dict[int, List[ClassRule]]):
        """Stores compiled CSS rules and their mapping to the nodes in the
        given trees.

        :param trees: The HTML trees at the origin of the compilation. These
            are the elements that have been styled with CSS properties.
        :type trees: List[HTMLNode]
        :param rules: The CSS section containing the compiled CSS rules.
        :type rules: RuleSection
        :param mapping: A dictionary mapping each node ID to a list of rules
            that achieve the same style.
        :type mapping: Dict[int, List[ClassRule]]
        """
        super().__init__()
        self.trees = trees
        self.preamble = Preamble()
        self.core = core
        self.mapping = mapping

    def to_css(self, indent_size: int = 4) -> str:
        """Converts the `preamble` and `core` sections of the
        :py:class:`CompiledCSS` object into CSS code.

        Sections are converted with their :py:meth:`RuleSection.to_css`
        methods.

        :param indent_size: See :py:meth:`RuleSection.to_css`.
        :type indent_size: int
        :return: The CSS code as a string.
        :rtype: str
        """
        return '\n\n'.join(
            section.to_css(indent_size=indent_size) for section in (
                self.preamble, self.core
            ))


def apply_css(css: CompiledCSS, tree: HTMLNode) -> None:
    """Applies the CSS rules to the given tree.

    Rules are added as HTML classes to each node with a style in the tree. If a
    node does not have a `class` attribute yet, it will be created for that
    node. Nodes that do not have any style are left untouched.

    Note that this function is recursive and calls itself on each child node of
    the tree.

    :param css: The compiled CSS object containing the rules to apply and the
        mapping to each node. It should have been created by invoking
        :py:func:`compile_css` on the given tree, but it can be modified before
        passing it to this function, as long as its content remains consistent.
    :type css: CompiledCSS
    :param tree: The tree to which the CSS rules should be applied. It will be
        modified in place by this function. If you want to keep the original
        tree unchanged, make a deep copy of it using its
        :py:meth:`HTMLNode.copy` method and pass this copy instead.
    :type tree: HTMLNode
    """
    # Only modifying nodes if they have a style (and therefore if the list of
    # rules mapped to them in `css.mapping` is not empty)
    if tree.style:

        # Listing rules to add as classes. We do not add rules that are already
        # there.
        rules_to_add = [r.name for r in css.mapping[id(tree)] if r.name not in
                        tree.attributes.get('class', '').split(' ')]

        # Updating the class attribute. If it already exists and is not empty,
        # we need to insert a space before adding the CSS classes.
        maybe_space = ' ' if tree.attributes.get(
            'class', None) and rules_to_add else ''
        tree.attributes['class'] = tree.attributes.get(
            'class', '') + maybe_space + ' '.join(rules_to_add)

    # Recursively applying the CSS rules to all child nodes of the tree
    for child in tree.children:
        apply_css(css, child)


def compile_css(trees: Union[HTMLNode, List[HTMLNode]],
                class_namer: Callable[[List[ClassRule], int],
                                      str] = None) -> CompiledCSS:
    """Computes optimized CSS rules from the given HTML trees.

    The main purpose of this function is to reduce the number of CSS rules
    required to achieve a particular style across one or more HTML trees. The
    function takes a list of HTML nodes as input (not necessarily from the same
    tree) and computes an optimized set of CSS rules that achieves the same
    style across all nodes. The resulting :py:class:`CompiledCSS` object
    contains the optimized rules and their mapping to each node.

    For example, the following tree:

    .. code-block:: python

        tree = HTMLNode(
            style={"margin": "0", "padding": "0"},
            children=[
                HTMLNode(style={"margin": "0", "padding": "0"}),
                HTMLNode(style={"margin": "0", "color": "blue"}),
            ]
        )

    can be stylistically described with only 3 CSS rules:

    .. code-block:: python

        >>> compiled_css = compile_css(tree)
        >>> print(compiled_css.core.rules)
        [
            ClassRule(selector='.c0', declarations={'color': 'blue'}, ...),
            ClassRule(selector='.c1', declarations={'margin': '0'}, ...),
            ClassRule(selector='.c2', declarations={'padding': '0'}, ...)
        ]

    Internally, each optimized rule gets compiled into a :py:class:`ClassRule`
    object, which represents a CSS rule whose selector targets the HTML `class`
    attribute. Each rule gets assigned a unique HTML class and all classes can
    then be added to the trees with :py:func:`apply_css`. Classes are named
    `"c0"`, `"c1"`, and so on by default, but this naming process can be
    customized using the `class_namer` argument.

    :param trees: A single tree or a list of trees to optimize over. All
        children are recursively included in the compilation.
    :type trees: Union[HTMLNode, List[HTMLNode]]
    :param class_namer: A callable that takes two arguments, which are the list
        of all compiled rules and an index within that list, and returns a
        unique name for the HTML class to associate with the rule at the given
        index.

        This argument allows to customize the class naming process and use names
        other than the default `"c0"`, `"c1"`, etc. For example, it can be used
        to achieve something similar to Tailwind CSS and name HTML classes
        according to what they achieve, e.g. by prefixing their name with `"m"`
        for margin rules or `"p"` for padding rules. Note that all class
        selectors will be validated with the :py:func:`validate_css_selector`
        function before being written into CSS code.

        Defaults to the :py:func:`default_class_namer` function which
        implements a default naming strategy where each class is named `"c{i}"`
        where `i` is the index of the rule in the list.
    :type class_namer: Callable[[List[ClassRule], int], str]
    :return: The :py:class:`CompiledCSS` object containing the optimized rules.
        Every HTML node present in one or more of the input trees is included
        in the :py:attr:`CompiledCSS.mapping` attribute, even if the node does
        not have a style. Rules are alphabetically ordered by class name in the
        mapping and in the :py:attr:`CompiledCSS.core` rule section.
    :rtype: CompiledCSS
    """
    # Handling case of a single tree
    if isinstance(trees, HTMLNode):
        trees = [trees]

    # Handling default class_namer
    class_namer = default_class_namer if class_namer is None else class_namer

    # We compute a simple mapping where each CSS property defines its own
    # ruleset
    styles = {k: v for tree in trees for k, v in tree.get_styles().items()}
    properties = set(itertools.chain.from_iterable(s.items()
                     for s in styles.values()))
    rules = [ClassRule("", dict([p]))  # Initializing with empty name
             for p in sorted(properties)]
    for i, rule in enumerate(rules):  # Assigning name from callback
        rule.name = class_namer(rules, i)
    rules = sorted(rules, key=lambda r: r.name)  # Sorting by name
    mapping = {node_id: [r for r in rules if
                         set(r.declarations.items()).issubset(style.items())]
               for node_id, style in styles.items()}

    # Packaging the results into a CompiledCSS object
    core = RuleSection(rules=rules, title="Core")
    return CompiledCSS(trees, core, mapping)


def default_class_namer(rules: List[ClassRule], index: int) -> str:
    """Default class naming function. Returns a string like "c{i}" where {i} is
    the index of the rule.

    :param rules: List of all compiled ClassRule objects. This argument is not
        used in this function, but it can be used in other naming strategies.
    :type rules: List[ClassRule]
    :param index: Index of the rule whose class is being named.
    :type index: int
    :return: A string like `"c{i}"` where `i` is the index of the rule.
    """
    return f'c{index}'
