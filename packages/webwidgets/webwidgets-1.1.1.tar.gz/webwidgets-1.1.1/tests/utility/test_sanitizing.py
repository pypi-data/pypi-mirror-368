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
from webwidgets.utility.sanitizing import HTML_ENTITIES, \
    CHAR_TO_HTML_ENTITIES, sanitize_html_text


class TestSanitizingHTMLText:
    def test_no_empty_html_entities(self):
        assert all(e for e in CHAR_TO_HTML_ENTITIES.values())

    @pytest.mark.parametrize("name", [
        'amp;', 'lt;', 'gt;', 'semi;', 'sol;', 'apos;', 'quot;'
    ])
    def test_known_html_entities(self, name):
        assert name in HTML_ENTITIES

    def test_char_to_html_entities(self):
        assert set(CHAR_TO_HTML_ENTITIES['&']) == set((
            'amp;', 'AMP', 'amp', 'AMP;'))
        assert CHAR_TO_HTML_ENTITIES['&'][0] == 'amp;'
        assert set(CHAR_TO_HTML_ENTITIES['>']) == set((
            'gt;', 'GT', 'gt', 'GT;'))
        assert CHAR_TO_HTML_ENTITIES['>'][0] == 'gt;'
        assert CHAR_TO_HTML_ENTITIES['\u0391'] == ('Alpha;',)

    @pytest.mark.parametrize("html_entity", [
        '&AMP', '&lt;', '&gt;', '&sol;'
    ])
    def test_sanitize_html_text(self, html_entity):
        text = '<div>Some text &{} and more</div>'.format(html_entity)
        expected_text_partial = '&lt;div&gt;Some text &{} and more&lt;&sol;div&gt;'.format(
            html_entity)
        assert sanitize_html_text(text) == expected_text_partial
        expected_text_full = '&lt;div&gt;Some text &amp;{} and more&lt;&sol;div&gt;'.format(
            html_entity)
        assert sanitize_html_text(
            text, replace_all_entities=True) == expected_text_full

    def test_sanitize_double_delimiting_characters(self):
        text = "&&copy &&copy; &copy;; copy;;"
        expected = "&amp;&copy &amp;&copy; &copy;&semi; copy&semi;&semi;"
        assert sanitize_html_text(text, replace_all_entities=True) == expected

    def test_sanitize_missing_ampersand(self):
        text = "copy; lt; gt;"
        expected = "copy&semi; lt&semi; gt&semi;"
        assert sanitize_html_text(text, replace_all_entities=True) == expected

    @pytest.mark.parametrize("text, expected", [
        ("Some text abcdefghijklmnopqrstuvwxyz",
         "Some text abcdefghijklmnopqrstuvwxyz"),
        ("0123456789.!?#",
         "0123456789.!?#"),
        ("& &; &aamp; &amp &amp; &AMP;",
         "& &; &aamp; &amp &amp; &AMP;"),
        ("&sool; &sol;/",
         "&sool; &sol;&sol;"),
        ('<div>Some text &sol;</div>',
         '&lt;div&gt;Some text &sol;&lt;&sol;div&gt;'),
        ('Some text\nand more',
         'Some text<br>and more'),
        ('<p>&nbsp;</p>',
         '&lt;p&gt;&nbsp;&lt;&sol;p&gt;'),
        ("This 'quote' is not \"there\".",
         "This &apos;quote&apos; is not &quot;there&quot;."),
        ("This is a mix < than 100% & 3/5",
         "This is a mix &lt; than 100% & 3&sol;5")
    ])
    def test_sanitize_html_with_partial_entity_replacement(self, text, expected):
        assert sanitize_html_text(text) == expected
        assert sanitize_html_text(text, replace_all_entities=False) == expected

    @pytest.mark.parametrize("text, expected", [
        ("Some text abcdefghijklmnopqrstuvwxyz",
         "Some text abcdefghijklmnopqrstuvwxyz"),
        ("0123456789.!?#",
         "0123456789&period;&excl;&quest;&num;"),
        ("& &; &aamp; &amp &amp; &AMP;",
         "&amp; &amp;&semi; &amp;aamp&semi; &amp &amp; &AMP;"),
        ("&sool; &sol;/",
         "&amp;sool&semi; &sol;&sol;"),
        ('<div>Some text &sol;</div>',
         '&lt;div&gt;Some text &sol;&lt;&sol;div&gt;'),
        ('Some text\nand more',
         'Some text<br>and more'),
        ('<p>&nbsp;</p>',
         '&lt;p&gt;&nbsp;&lt;&sol;p&gt;'),
        ("This 'quote' is not \"there\".",
         "This &apos;quote&apos; is not &quot;there&quot;&period;"),
        ("This is a mix < than 100% & 3/5",
         "This is a mix &lt; than 100&percnt; &amp; 3&sol;5")
    ])
    def test_sanitize_html_with_full_entity_replacement(self, text, expected):
        assert sanitize_html_text(text, replace_all_entities=True) == expected
