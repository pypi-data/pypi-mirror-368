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

from .compiled_website import CompiledWebsite
from typing import Any, Callable, List
from webwidgets.compilation.css import apply_css, compile_css, ClassRule
from webwidgets.utility.representation import ReprMixin
from webwidgets.widgets.containers.page import Page


class Website(ReprMixin):
    """A collection of :py:class:`Page` objects that make up the structure of a
    web site."""

    def __init__(self, pages: List[Page] = None):
        """Creates a new website with an optional list of pages.

        :param pages: The pages of the website. Defaults to an empty list.
        :type pages: List[Page]
        """
        super().__init__()
        self.pages = [] if pages is None else pages

    def add(self, page: Page):
        """Adds a new page to the website.

        :param page: The page to be added.
        :type page: Page
        """
        self.pages.append(page)

    def compile(self,
                collapse_empty: bool = True,
                css_file_name: str = "styles.css",
                force_one_line: bool = False,
                indent_level: int = 0,
                indent_size: int = 4,
                class_namer: Callable[[List[ClassRule], int], str] = None,
                **kwargs: Any) -> CompiledWebsite:
        """Compiles the website into HTML and CSS code.

        :param collapse_empty: See :py:meth:`HTMLNode.to_html`.
        :type collapse_empty: bool
        :param css_file_name: See :py:meth:`Page.build`.
        :type css_file_name: str
        :param force_one_line: See :py:meth:`HTMLNode.to_html`.
        :type force_one_line: bool
        :param indent_level: See :py:meth:`HTMLNode.to_html`.
        :type indent_level: int
        :param indent_size: See :py:meth:`HTMLNode.to_html` and
            :py:meth:`CompiledCSS.to_css`.
        :type indent_size: int
        :param class_namer: See :py:func:`compile_css`.
        :type class_namer: Callable[[List[ClassRule], int], str]
        :param kwargs: See :py:meth:`HTMLNode.to_html`.
        :type kwargs: Any
        :return: A new :py:class:`CompiledWebsite` object containing the
            compiled HTML and CSS code.
        :rtype: CompiledWebsite
        """
        # Building the HTML representation of each page
        trees = [page.build(css_file_name=css_file_name)
                 for page in self.pages]

        # Compiling HTML and CSS code
        compiled_css = compile_css(trees, class_namer)
        for tree in trees:
            apply_css(compiled_css, tree)
        html_content = [tree.to_html(
            collapse_empty=collapse_empty,
            force_one_line=force_one_line,
            indent_level=indent_level,
            indent_size=indent_size,
            **kwargs
        ) for tree in trees]
        css_content = compiled_css.to_css(indent_size=indent_size)

        # Storing the result in a new CompiledWebsite object
        return CompiledWebsite(html_content, css_content)
