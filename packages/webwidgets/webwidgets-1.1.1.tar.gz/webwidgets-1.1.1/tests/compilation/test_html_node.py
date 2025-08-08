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
from webwidgets.compilation.html.html_node import HTMLNode, no_start_tag, \
    no_end_tag, one_line, RawText, RootNode


class TestHTMLNode:
    class CustomNode(HTMLNode):
        pass

    @no_start_tag
    class NoStartNode(HTMLNode):
        pass

    @no_end_tag
    class NoEndNode(HTMLNode):
        pass

    @no_start_tag
    @no_end_tag
    class NoStartEndNode(HTMLNode):
        pass

    class OneLineNode(HTMLNode):
        one_line = True

    class OneLineNoStartNode(NoStartNode):
        one_line = True

    @one_line
    class OneLineDecoratorNode(HTMLNode):
        pass

    class KwargsReceiverNode(HTMLNode):
        def to_html(self, return_lines: bool, message: str,
                    **kwargs):
            if return_lines:
                return [message]
            return message

    def test_basic_node(self):
        node = HTMLNode()
        assert node.start_tag == "<htmlnode>"
        assert node.end_tag == "</htmlnode>"
        assert node.to_html() == "<htmlnode></htmlnode>"

    def test_custom_name(self):
        node = TestHTMLNode.CustomNode()
        assert node.start_tag == "<customnode>"
        assert node.end_tag == "</customnode>"
        assert node.to_html() == "<customnode></customnode>"

    def test_attributes(self):
        node = HTMLNode(attributes={'id': 'test-id', 'class': 'test-class'})
        assert node.start_tag == '<htmlnode class="test-class" id="test-id">'
        assert node.end_tag == '</htmlnode>'
        assert node.to_html() == '<htmlnode class="test-class" id="test-id"></htmlnode>'

    def test_attributes_order(self):
        node = HTMLNode(attributes={'d': '0', 'a': '1', 'c': '2', 'b': '3'})
        assert node._render_attributes() == 'a="1" b="3" c="2" d="0"'
        assert node.to_html() == '<htmlnode a="1" b="3" c="2" d="0"></htmlnode>'

    def test_no_start_tag(self):
        node = TestHTMLNode.NoStartNode()
        assert node.start_tag == ''
        assert node.end_tag == '</nostartnode>'
        assert node.to_html() == "</nostartnode>"

    def test_no_end_tag(self):
        node = TestHTMLNode.NoEndNode()
        assert node.start_tag == '<noendnode>'
        assert node.end_tag == ''
        assert node.to_html() == "<noendnode>"

    def test_no_start_end_tag(self):
        node = TestHTMLNode.NoStartEndNode()
        assert node.start_tag == ''
        assert node.end_tag == ''
        assert node.to_html() == ""

    def test_one_line_rendering(self):
        node = HTMLNode(children=[RawText('child1'),
                        RawText('child2')])
        expected_html = "<htmlnode>child1child2</htmlnode>"
        assert node.to_html(force_one_line=True) == expected_html

    def test_no_start_tag_with_one_line(self):
        node = TestHTMLNode.NoStartNode(children=[RawText('child1'),
                                                  RawText('child2')])
        expected_html = "child1child2</nostartnode>"
        assert node.to_html(force_one_line=True) == expected_html

    def test_no_end_tag_with_one_line(self):
        node = TestHTMLNode.NoEndNode(children=[RawText('child1'),
                                                RawText('child2')])
        expected_html = "<noendnode>child1child2"
        assert node.to_html(force_one_line=True) == expected_html

    def test_one_line_decorator(self):
        inner_node = HTMLNode(children=[RawText('inner_child')])
        node = TestHTMLNode.OneLineDecoratorNode(
            children=[inner_node]
        )
        expected_html = "<onelinedecoratornode>" + \
            "<htmlnode>inner_child</htmlnode></onelinedecoratornode>"
        assert node.to_html() == expected_html

    def test_recursive_rendering(self):
        inner_node = HTMLNode(children=[RawText('inner_child')])
        node = TestHTMLNode.CustomNode(children=[inner_node])
        expected_html = '\n'.join([
            "<customnode>",
            "    <htmlnode>",
            "        inner_child",
            "    </htmlnode>",
            "</customnode>"
        ])
        assert node.to_html() == expected_html
        assert node.to_html(force_one_line=False) == expected_html

    def test_no_start_tag_with_recursive_rendering(self):
        inner_node = HTMLNode(children=[RawText('inner_child')])
        node = TestHTMLNode.NoStartNode(children=[inner_node])
        expected_html = '\n'.join([
            "    <htmlnode>",
            "        inner_child",
            "    </htmlnode>",
            "</nostartnode>"
        ])
        assert node.to_html() == expected_html

    def test_no_end_tag_with_recursive_rendering(self):
        inner_node = HTMLNode(children=[RawText('inner_child')])
        node = TestHTMLNode.NoEndNode(children=[inner_node])
        expected_html = '\n'.join([
            "<noendnode>",
            "    <htmlnode>",
            "        inner_child",
            "    </htmlnode>"
        ])
        assert node.to_html() == expected_html

    def test_recursive_rendering_one_line(self):
        inner_node = HTMLNode(children=[RawText('inner_child')])
        node = TestHTMLNode.CustomNode(children=[inner_node])
        expected_html = "<customnode><htmlnode>inner_child</htmlnode></customnode>"
        assert node.to_html(force_one_line=True) == expected_html

    def test_recursive_rendering_one_line_propagation(self):
        one_line = TestHTMLNode.OneLineNode(
            [HTMLNode(children=[RawText('inner_child')])]
        )
        node = HTMLNode(children=[one_line])
        expected_html = '\n'.join([
            "<htmlnode>",
            "    <onelinenode><htmlnode>inner_child</htmlnode></onelinenode>",
            "</htmlnode>"
        ])
        assert node.to_html() == expected_html

    def test_recursive_rendering_of_tagless_mix(self):
        children = [
            TestHTMLNode.NoEndNode([RawText("child1")]),
            TestHTMLNode.NoStartNode([RawText("child2")]),
            TestHTMLNode.NoEndNode([RawText("child3")]),
        ]
        inner_node = TestHTMLNode.NoStartNode(children=children)
        node = TestHTMLNode.NoEndNode(children=[inner_node])
        expected_html = '\n'.join([
            "<noendnode>",
            "        <noendnode>",
            "            child1",
            "            child2",
            "        </nostartnode>",
            "        <noendnode>",
            "            child3",
            "    </nostartnode>"
        ])
        assert node.to_html() == expected_html

    def test_recursive_rendering_of_tagless_mix_one_line(self):
        children = [
            TestHTMLNode.NoEndNode([RawText("child1")]),
            TestHTMLNode.OneLineNoStartNode([RawText("child2")]),
            TestHTMLNode.NoEndNode([RawText("child3")]),
        ]
        inner_node = TestHTMLNode.NoStartNode(children=children)
        node = TestHTMLNode.NoEndNode(children=[inner_node])
        expected_html = '\n'.join([
            "<noendnode>",
            "        <noendnode>",
            "            child1",
            "        child2</onelinenostartnode>",
            "        <noendnode>",
            "            child3",
            "    </nostartnode>"
        ])
        assert node.to_html() == expected_html

    def test_recursive_rendering_of_tagless_mix_force_one_line(self):
        children = [
            TestHTMLNode.NoEndNode([RawText("child1")]),
            TestHTMLNode.NoStartNode([RawText("child2")]),
            TestHTMLNode.NoEndNode([RawText("child3")]),
        ]
        inner_node = TestHTMLNode.NoStartNode(children=children)
        node = TestHTMLNode.NoEndNode(children=[inner_node])
        expected_html = "<noendnode><noendnode>child1child2</nostartnode>" + \
            "<noendnode>child3</nostartnode>"
        assert node.to_html(force_one_line=True) == expected_html

    def test_raw_text_as_orphan_node(self):
        node = HTMLNode(children=[
            TestHTMLNode.CustomNode(),
            RawText("raw_text")
        ])
        expected_html = '\n'.join([
            "<htmlnode>",
            "    <customnode></customnode>",
            "    raw_text",
            "</htmlnode>"
        ])
        assert node.to_html() == expected_html

    @pytest.mark.parametrize("indent_level", [0, 1, 2])
    @pytest.mark.parametrize("indent_size", [2, 3, 4, 8])
    def test_indentation(self, indent_level: int, indent_size: int):
        """Test the to_html method with different indentation parameters."""

        # Creating a simple HTMLNode
        node = HTMLNode(children=[
            RawText('child1'),
            RawText('child2'),
            HTMLNode(children=[
                RawText('grandchild1'),
                RawText('grandchild2')
            ])
        ])

        # Expected output based on the test parameters
        expected_html = "\n".join([
            f"{' ' * indent_size * indent_level}<htmlnode>",
            f"{' ' * indent_size * (indent_level + 1)}child1",
            f"{' ' * indent_size * (indent_level + 1)}child2",
            f"{' ' * indent_size * (indent_level + 1)}<htmlnode>",
            f"{' ' * indent_size * (indent_level + 2)}grandchild1",
            f"{' ' * indent_size * (indent_level + 2)}grandchild2",
            f"{' ' * indent_size * (indent_level + 1)}</htmlnode>",
            f"{' ' * indent_size * indent_level}</htmlnode>"
        ])

        # Calling to_html with the test parameters
        actual_html = node.to_html(
            indent_size=indent_size, indent_level=indent_level)
        assert actual_html == expected_html

    @pytest.mark.parametrize("indent_level", [0, 1, 2])
    @pytest.mark.parametrize("indent_size", [3, 4, 8])
    def test_indentation_empty_node(self, indent_level, indent_size):
        node = HTMLNode()
        expected_html = f"{' ' * indent_size * indent_level}<htmlnode></htmlnode>"
        actual_html = node.to_html(
            indent_size=indent_size, indent_level=indent_level)
        assert actual_html == expected_html

    @pytest.mark.parametrize("indent_level", [-3, -2, -1])
    def test_negative_indent_level(self, indent_level: int):
        node = HTMLNode(children=[
            RawText('child1'),
            RawText('child2'),
            HTMLNode(children=[
                RawText('grandchild1'),
                RawText('grandchild2')
            ])
        ])
        expected_html = "\n".join([
            "<htmlnode>",
            "child1",
            "child2",
            "<htmlnode>",
            f"{'    ' if indent_level == -1 else ''}grandchild1",
            f"{'    ' if indent_level == -1 else ''}grandchild2",
            "</htmlnode>",
            "</htmlnode>"
        ])
        assert node.to_html(indent_level=indent_level) == expected_html

    def test_collapse_empty(self):
        node = HTMLNode(children=[
            TestHTMLNode.CustomNode(),
            HTMLNode(children=[RawText('grandchild1')])
        ])
        expected_html = "\n".join([
            "<htmlnode>",
            "    <customnode></customnode>",
            "    <htmlnode>",
            "        grandchild1",
            "    </htmlnode>",
            "</htmlnode>"
        ])
        assert node.to_html() == expected_html
        assert node.to_html(collapse_empty=True) == expected_html

    def test_not_collapse_empty(self):
        node = HTMLNode(children=[
            TestHTMLNode.CustomNode(),
            HTMLNode(children=[RawText('grandchild1')])
        ])
        expected_html = "\n".join([
            "<htmlnode>",
            "    <customnode>",
            "    </customnode>",
            "    <htmlnode>",
            "        grandchild1",
            "    </htmlnode>",
            "</htmlnode>"
        ])
        assert node.to_html(collapse_empty=False) == expected_html

    def test_kwargs_pass_down(self):
        node = HTMLNode(children=[
            TestHTMLNode.CustomNode(),
            TestHTMLNode.KwargsReceiverNode()
        ])
        expected_html = "\n".join([
            "<htmlnode>",
            "    <customnode></customnode>",
            "Message is 42",
            "</htmlnode>"
        ])
        assert node.to_html(message="Message is 42") == expected_html

    @pytest.mark.parametrize("raw, sanitized", [
        ('<div>text</div>', "&lt;div&gt;text&lt;&sol;div&gt;"),
        ('\"Yes?\" > \'No!\'', "&quot;Yes?&quot; &gt; &apos;No!&apos;"),
        ('Yes &\nNo', "Yes &<br>No"),
    ])
    def test_sanitize_raw_text(self, raw, sanitized):
        node = HTMLNode(children=[RawText(raw)])
        expected_html = "\n".join([
            "<htmlnode>",
            f"    {sanitized}",
            "</htmlnode>"
        ])
        assert node.to_html() == expected_html
        assert node.to_html(replace_all_entities=False) == expected_html

    @pytest.mark.parametrize("raw, sanitized", [
        ('<div>text</div>',
         "&lt;div&gt;text&lt;&sol;div&gt;"),
        ('\"Yes?\" > \'No!\'',
         "&quot;Yes&quest;&quot; &gt; &apos;No&excl;&apos;"),
        ('Yes &\nNo',
         "Yes &amp;<br>No"),
    ])
    def test_sanitize_all_entities_in_raw_text(self, raw, sanitized):
        node = HTMLNode(children=[RawText(raw)])
        expected_html = "\n".join([
            "<htmlnode>",
            f"    {sanitized}",
            "</htmlnode>"
        ])
        assert node.to_html(replace_all_entities=True) == expected_html

    def test_get_styles_no_children(self):
        node = HTMLNode()
        assert node.get_styles() == {id(node): {}}

    def test_get_styles_no_children_with_style(self):
        node = HTMLNode(style={"color": "red"})
        assert node.get_styles() == {id(node): {"color": "red"}}

    def test_get_styles(self):
        inner_1 = HTMLNode(style={"color": "red"})
        inner_2 = HTMLNode(style={"margin": "0"})
        node = HTMLNode(children=[inner_1, inner_2],
                        style={"font-size": "20px"})
        assert node.get_styles() == {
            id(inner_1): {"color": "red"},
            id(inner_2): {"margin": "0"},
            id(node): {"font-size": "20px"},
        }

    def test_get_styles_deeper_tree(self):
        grandchild_1 = HTMLNode(style={"color": "red"})
        grandchild_2 = HTMLNode(style={"margin": "0"})
        child_1 = HTMLNode(children=[grandchild_1, grandchild_2],
                           style={"font-size": "20px"})
        grandchild_3 = HTMLNode(style={"background-color": "blue"})
        child_2 = HTMLNode(children=[grandchild_3],
                           style={"font-weight": "bold"})
        node = HTMLNode(children=[child_1, child_2],
                        style={"padding": "5px"})

        assert node.get_styles() == {
            id(grandchild_1): {"color": "red"},
            id(grandchild_2): {"margin": "0"},
            id(child_1): {"font-size": "20px"},
            id(grandchild_3): {"background-color": "blue"},
            id(child_2): {"font-weight": "bold"},
            id(node): {"padding": "5px"},
        }

    def test_shallow_copy(self):
        node = HTMLNode(style={"color": "red"})
        copied_node = node.copy(deep=False)
        assert id(copied_node) != id(node)
        assert copied_node.style == {"color": "red"}
        child = RawText("text")
        copied_node.children.append(child)
        assert len(copied_node.children) == 1
        assert id(copied_node.children[0]) == id(child)
        assert len(node.children) == 1
        assert id(node.children[0]) == id(child)

    def test_shallow_copy_nested(self):
        node = HTMLNode(
            style={"a": "0"},
            children=[HTMLNode(style={"a": "1"})]
        )
        copied_node = node.copy(deep=False)
        assert id(copied_node) != id(node)
        assert copied_node.style == {"a": "0"}
        assert [id(c) for c in copied_node.children] == [
            id(c) for c in node.children]
        copied_node.children[0].style["a"] = "2"
        assert node.children[0].style == {"a": "2"}

    def test_deep_copy(self):
        node = HTMLNode(style={"color": "red"})
        copied_node = node.copy(deep=True)
        assert id(copied_node) != id(node)
        assert copied_node.style == {"color": "red"}
        copied_node.children.append(RawText("text"))
        assert len(copied_node.children) == 1
        assert len(node.children) == 0

    def test_deep_copy_nested(self):
        node = HTMLNode(
            style={"a": "0"},
            children=[HTMLNode(style={"a": "1"})]
        )
        copied_node = node.copy(deep=True)
        assert id(copied_node) != id(node)
        assert copied_node.style == {"a": "0"}
        assert id(copied_node.children[0]) != id(node.children[0])
        assert copied_node.children[0].style == {"a": "1"}
        copied_node.children[0].style["a"] = "2"
        assert node.children[0].style == {"a": "1"}

    def test_copy_default(self):
        """Tests that the default copy is a shallow copy"""
        node = HTMLNode(style={"color": "red"})
        copied_node = node.copy()
        child = RawText("text")
        copied_node.children.append(child)
        assert len(node.children) == 1
        assert id(node.children[0]) == id(child)

    def test_empty_root_node(self):
        node = RootNode()
        assert node.to_html() == ""

    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_root_node_with_children(self, n):
        node = RootNode(
            children=[HTMLNode()] * n
        )
        expected_html = "\n".join(["<htmlnode></htmlnode>"] * n)
        print(expected_html)
        assert node.to_html() == expected_html
