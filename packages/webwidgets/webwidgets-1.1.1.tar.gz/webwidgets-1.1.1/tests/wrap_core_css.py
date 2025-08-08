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

from typing import Any
from webwidgets.compilation.css.sections.css_section import CSSSection
from webwidgets.compilation.css.sections.preamble import Preamble


def wrap_core_css(core_css: str, *args: Any, **kwargs: Any) -> str:
    """A utility function that wraps the CSS code from a core section into a
    final output code with the appropriate preamble and section titles.

    :param core_css: The CSS code for the core section.
    :type core_css: str
    :param args: Additional arguments to pass to :py:meth:`Preamble.to_css`.
    :type args: Any
    :param kwargs: Additional keyword arguments to pass to
        :py:meth:`Preamble.to_css`.
    :type kwargs: Any
    :return: The final CSS code with the appropriate preamble and section
        titles.
    :rtype: str
    """
    return "\n\n".join((
        Preamble().to_css(*args, **kwargs),
        "/* " + CSSSection.prettify_title("Core", 40) + " */",
        core_css
    ))
