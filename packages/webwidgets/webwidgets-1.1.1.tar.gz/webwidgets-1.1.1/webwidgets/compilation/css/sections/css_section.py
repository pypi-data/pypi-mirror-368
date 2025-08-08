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

from abc import ABC, abstractmethod
from typing import Any
from webwidgets.utility.representation import ReprMixin
from webwidgets.utility.validation import validate_css_comment


class CSSSection(ABC, ReprMixin):
    """Abstract base class representing a section of a CSS file.

    All subclasses of :py:class:`CSSSection` must implement a
    :py:meth:`compile_content` method that returns a string.
    """

    @staticmethod
    def prettify_title(title: str, min_length: int) -> str:
        """Returns a prettified version of the given title with decorative
        characters `=` around it.

        This function will add the minimum number of decorative characters to
        the title while keeping symmetry and remaining over the given minimum
        length. In particular, if the given title is already above the minimum
        length, this function will return it as is.

        :param title: The title to prettify.
        :type title: str
        :param max_length: The minimum length of the prettified title.
        :type max_length: int
        :return: The prettified title.
        :rtype: str
        """
        # If the title is already above min_length, we don't add decorative
        # characters
        if len(title) >= min_length:
            return title

        # Otherwise, we add decorative characters around the title
        remaining = min_length - len(title)
        characters = "=" * max(((remaining - 1) // 2), 1)
        return characters + ' ' + title + ' ' + characters

    def __init__(self, title: str = None):
        """Creates a new section with an optional title.

        :param title: The title of the section. If provided, the section will
            be preceded by a comment containing the title in the output CSS
            code. If None, no title will be used to separate the section from
            the rest of the code.
        :type title: str
        """
        super().__init__()
        self.title = title

    @abstractmethod
    def compile_content(self) -> str:
        """Converts the content of the CSSSection object (excluding the title)
        into CSS code.

        This method must be overridden by subclasses to compile specific CSS
        code.
        """
        pass

    def to_css(self, *args: Any, **kwargs: Any) -> str:
        """Converts the CSSSection object into CSS code.

        If the section has a title, it will be prettified with
        :py:meth:`CSSSection.prettify_title` and turned into a comment. That
        comment will be validated with :py:func:`validate_css_comment` and
        inserted before the result of :py:meth:`CSSSection.compile_content` in
        the CSS code.

        If the section has no title, this function will produce the same result
        as :py:meth:`CSSSection.compile_content`.

        :param args: Arguments to pass to
            :py:meth:`CSSSection.compile_content`.
        :type args: Any
        :param kwargs: Keyword arguments to pass to
            :py:meth:`CSSSection.compile_content`.
        :type kwargs: Any
        :return: The CSS code for the section.
        :rtype: str
        """
        # If no title, we just return the compiled content
        if self.title is None:
            return self.compile_content(*args, **kwargs)

        # Otherwise, we turn the title into a comment and validate it
        comment = ' ' + CSSSection.prettify_title(self.title, 40) + ' '
        validate_css_comment(comment)

        # Adding the comment before the compiled content
        return "/*" + comment + "*/\n\n" + \
            self.compile_content(*args, **kwargs)
