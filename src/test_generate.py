import unittest

from generate import (
    HTMLNode,
    LeafNode,
    ParentNode,
    code_to_html,
    heading_to_html,
    markdown_to_html_node,
    ordered_to_html,
    paragraph_to_html,
    quote_to_html,
    text_node_to_html_node,
    unordered_to_html,
)
from parse import TextNode, TextType


class TestHTMLNode(unittest.TestCase):
    def test_link_props(self):
        node = HTMLNode(props={"href": "https://www.google.com", "target": "_blank"})
        props_html = node.props_to_html()
        self.assertEqual(props_html, ' href="https://www.google.com" target="_blank"')

    def test_img_props(self):
        node = HTMLNode(props={"src": "img/test.jpg", "alt": "Image Description"})
        props_html = node.props_to_html()
        self.assertEqual(props_html, ' src="img/test.jpg" alt="Image Description"')

    def test_class_props(self):
        node = HTMLNode(props={"class": "font-semibold text-2xl"})
        props_html = node.props_to_html()
        self.assertEqual(props_html, ' class="font-semibold text-2xl"')

    def test_repr_with_props(self):
        node = HTMLNode(
            "p", "This is a paragraph", None, {"class": "font-semibold text-2xl"}
        )
        output = f"HTMLNode(tag=\"p\", value=\"This is a paragraph\", children=None, props={{'class': 'font-semibold text-2xl'}})"
        self.assertEqual(repr(node), output)


class TestLeafNode(unittest.TestCase):
    def test_paragraph(self):
        node = LeafNode("p", "This is a paragraph of text.")
        node_html = node.to_html()
        self.assertEqual(node_html, "<p>This is a paragraph of text.</p>")

    def test_link(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        node_html = node.to_html()
        self.assertEqual(node_html, '<a href="https://www.google.com">Click me!</a>')

    def test_image(self):
        node = LeafNode("img", None, {"alt": "Alt Text", "src": "/images/image.jpg"})
        node_html = node.to_html()
        self.assertEqual(node_html, '<img alt="Alt Text" src="/images/image.jpg">')

    def test_no_tag(self):
        node = LeafNode("", "Just some text")
        node_html = node.to_html()
        self.assertEqual(node_html, "Just some text")

    def test_value_required(self):
        node = LeafNode("p")
        self.assertRaises(ValueError, node.to_html)


class TestParentNode(unittest.TestCase):
    def test_single_level(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        expected_html = (
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>"
        )
        self.assertEqual(node.to_html(), expected_html)

    def test_two_level(self):
        node = ParentNode(
            "div",
            [
                LeafNode("b", "Bold text", {"class": "font-bold"}),
                LeafNode("p", "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode("p", "Normal text"),
                ParentNode(
                    "div",
                    [
                        LeafNode("p", "Inner Text"),
                    ],
                ),
            ],
        )
        expected_html = '<div><b class="font-bold">Bold text</b><p>Normal text</p><i>italic text</i><p>Normal text</p><div><p>Inner Text</p></div></div>'
        self.assertEqual(node.to_html(), expected_html)

    def test_no_tag(self):
        node = ParentNode(None, [LeafNode("b", "Bold text")])
        self.assertRaises(ValueError, node.to_html)

    def test_no_children(self):
        node = ParentNode("div", None)
        self.assertRaises(ValueError, node.to_html)


class TestTextNodeToHTMLNode(unittest.TestCase):

    def test_text_type(self):
        text_node = TextNode("This is text", TextType.TEXT)
        html_node = text_node_to_html_node(text_node)
        expected_html_node = LeafNode(None, "This is text")
        self.assertEqual(html_node, expected_html_node)

    def test_bold_type(self):
        text_node = TextNode("this is bold text", TextType.BOLD)
        html_node = text_node_to_html_node(text_node)
        expected_html_node = LeafNode("b", "this is bold text")
        self.assertEqual(html_node, expected_html_node)

    def test_italic_type(self):
        text_node = TextNode("This is italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(text_node)
        expected_html_node = LeafNode("i", "This is italic text")
        self.assertEqual(html_node, expected_html_node)

    def test_code_type(self):
        text_node = TextNode("This is code", TextType.CODE)
        html_node = text_node_to_html_node(text_node)
        expected_html_node = LeafNode("code", "This is code")
        self.assertEqual(html_node, expected_html_node)

    def test_link_type(self):
        text_node = TextNode("This is a link", TextType.LINK, "https://www.boot.dev")
        html_node = text_node_to_html_node(text_node)
        expected_html_node = LeafNode(
            "a", "This is a link", {"href": "https://www.boot.dev"}
        )
        self.assertEqual(html_node, expected_html_node)

    def test_image_type(self):
        text_node = TextNode("Image alt text", TextType.IMAGE, "img/test.jpg")
        html_node = text_node_to_html_node(text_node)
        expected_html_node = LeafNode(
            "img", None, {"src": "img/test.jpg", "alt": "Image alt text"}
        )
        self.assertEqual(html_node, expected_html_node)

    def test_invalid_type(self):
        text_node = TextNode("Invalid type", "invalid")
        self.assertRaises(ValueError, text_node_to_html_node, text_node)


class TestQuoteToHTML(unittest.TestCase):
    def test_blockquote(self):
        block = "> this is a\n> block quote"
        html_nodes = quote_to_html(block)
        expected_html_nodes = ParentNode(
            "blockquote", [LeafNode(None, "this is a block quote")]
        )
        self.assertEqual(html_nodes, expected_html_nodes)

    def test_blockquote_with_inline(self):
        block = "> this is a\n> block quote\n> with **bold** text"
        html_nodes = quote_to_html(block)
        expected_html_nodes = ParentNode(
            "blockquote",
            [
                LeafNode(None, "this is a block quote with "),
                LeafNode("b", "bold"),
                LeafNode(None, " text"),
            ],
        )
        self.assertEqual(html_nodes, expected_html_nodes)


class TestUnorderedToHTML(unittest.TestCase):
    def test_two_items_dash(self):
        block = "- this is an\n- unordered list"
        html_nodes = unordered_to_html(block)
        expected_html_nodes = ParentNode(
            "ul",
            children=[
                ParentNode("li", [LeafNode(None, "this is an")]),
                ParentNode("li", [LeafNode(None, "unordered list")]),
            ],
        )
        self.assertEqual(html_nodes, expected_html_nodes)

    def test_two_items_dash_with_inline(self):
        block = "- this is an\n- **unordered** list"
        html_nodes = unordered_to_html(block)
        expected_html_nodes = ParentNode(
            "ul",
            children=[
                ParentNode("li", [LeafNode(None, "this is an")]),
                ParentNode("li", [LeafNode("b", "unordered"), LeafNode(None, " list")]),
            ],
        )
        self.assertEqual(html_nodes, expected_html_nodes)


class TestOrderedToHTML(unittest.TestCase):
    def test_two_items(self):
        block = "1. this is an\n2. ordered list"
        html_nodes = ordered_to_html(block)
        expected_html_nodes = ParentNode(
            "ol",
            children=[
                ParentNode("li", [LeafNode(None, "this is an")]),
                ParentNode("li", [LeafNode(None, "ordered list")]),
            ],
        )
        self.assertEqual(html_nodes, expected_html_nodes)

    def test_two_items_with_inline(self):
        block = "1. this is an\n2. **ordered** list"
        html_nodes = ordered_to_html(block)
        expected_html_nodes = ParentNode(
            "ol",
            children=[
                ParentNode("li", [LeafNode(None, "this is an")]),
                ParentNode("li", [LeafNode("b", "ordered"), LeafNode(None, " list")]),
            ],
        )
        self.assertEqual(html_nodes, expected_html_nodes)


class TestCodeToHTML(unittest.TestCase):
    def test_code(self):
        block = "import math\n\nprint(2+2)"
        html_nodes = code_to_html(block)
        expected_html_nodes = ParentNode(
            "pre",
            [
                ParentNode(
                    "code",
                    [LeafNode(None, "import math\n\nprint(2+2)")],
                )
            ],
        )
        self.assertEqual(html_nodes, expected_html_nodes)


class TestHeadingToHTML(unittest.TestCase):
    def test_h1(self):
        block = "# H1 Heading"
        html_nodes = heading_to_html(block)
        expected_html_nodes = ParentNode("h1", [LeafNode(None, "H1 Heading")])
        self.assertEqual(html_nodes, expected_html_nodes)

    def test_h3(self):
        block = "### H3 Heading"
        html_nodes = heading_to_html(block)
        expected_html_nodes = ParentNode("h3", [LeafNode(None, "H3 Heading")])
        self.assertEqual(html_nodes, expected_html_nodes)

    def test_h1_with_inline(self):
        block = "# H1 *Italic Heading*"
        html_nodes = heading_to_html(block)
        expected_html_nodes = ParentNode(
            "h1", [LeafNode(None, "H1 "), LeafNode("i", "Italic Heading")]
        )
        self.assertEqual(html_nodes, expected_html_nodes)


class TestParagraphToHTML(unittest.TestCase):
    def test_plain_paragraph(self):
        block = "This is paragraph.\nThe paragraph has two lines."
        html_nodes = paragraph_to_html(block)
        expected_html_nodes = LeafNode(
            "p", "This is paragraph.\nThe paragraph has two lines."
        )
        self.assertEqual(html_nodes, expected_html_nodes)

    def test_paragraph_with_inline(self):
        block = "This is a paragraph.\nThis line has **bold text**."
        html_nodes = paragraph_to_html(block)
        expected_html_nodes = ParentNode(
            "p",
            [
                LeafNode(None, "This is a paragraph.\nThis line has "),
                LeafNode("b", "bold text"),
                LeafNode(None, "."),
            ],
        )
        self.assertEqual(html_nodes, expected_html_nodes)
