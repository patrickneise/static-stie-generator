import unittest

from generate import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_link_props(self):
        node = HTMLNode(props={"href": "https://www.google.com", "target": "_blank"})
        props_html = node.props_to_html()
        self.assertEqual(props_html, ' href="https://www.google.com" target="_blank"')

    def test_img_props(self):
        node = HTMLNode(props={"src": "img/test.jpg", "alt": "Image Description"})
        props_html = node.props_to_html()
        self.assertEqual(props_html, ' src="img/test.jpg" alt="Image Description"')


class TestLeafNode(unittest.TestCase):
    def test_paragraph(self):
        node = LeafNode("p", "This is a paragraph of text.")
        node_html = node.to_html()
        self.assertEqual(node_html, "<p>This is a paragraph of text.</p>")

    def test_link(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        node_html = node.to_html()
        self.assertEqual(node_html, '<a href="https://www.google.com">Click me!</a>')

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
