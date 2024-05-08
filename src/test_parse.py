import unittest

from config import BlockType, TextType
from parse import (
    TextNode,
    block_to_block_type,
    extract_markdown_images,
    extract_markdown_links,
    markdown_to_blocks,
    split_nodes_delimeter,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
)


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_eq_url(self):
        node = TextNode("This is a text node", TextType.BOLD, "https://boot.dev")
        node2 = TextNode("This is a text node", TextType.BOLD, "https://boot.dev")
        self.assertEqual(node, node2)

    def test_not_equal_text(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a different text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_not_equal_type(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_not_equal_url(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD, "https://boot.dev")
        self.assertNotEqual(node, node2)

    def test_repr_text(self):
        node = TextNode("This is a text Node", TextType.ITALIC)
        output = f'TextNode(text="This is a text Node", text_type="{node.text_type}")'
        self.assertEqual(repr(node), output)

    def test_repr_image(self):
        node = TextNode("This is a Link", TextType.LINK, "https://www.boot.dev")
        output = f'TextNode(text="This is a Link", text_type="{node.text_type}", url="https://www.boot.dev")'
        self.assertEqual(repr(node), output)


class TestSplitNodesDelimeter(unittest.TestCase):
    def test_code_text(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimeter([node], "`", TextType.CODE)
        expected_nodes = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]

        self.assertEqual(new_nodes, expected_nodes)

    def test_bold_text(self):
        node = TextNode("This is **bold text** in a sentence", TextType.TEXT)
        new_nodes = split_nodes_delimeter([node], "**", TextType.BOLD)
        expected_nodes = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold text", TextType.BOLD),
            TextNode(" in a sentence", TextType.TEXT),
        ]

        self.assertEqual(new_nodes, expected_nodes)

    def test_italic_text(self):
        node = TextNode("This is *italic text* in a sentence", TextType.TEXT)
        new_nodes = split_nodes_delimeter([node], "*", TextType.ITALIC)
        expected_nodes = [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic text", TextType.ITALIC),
            TextNode(" in a sentence", TextType.TEXT),
        ]

        self.assertEqual(new_nodes, expected_nodes)

    def test_missing_delimeter(self):
        node = TextNode("This is `code block missing a backtic", TextType.TEXT)

        self.assertRaises(Exception, split_nodes_delimeter, node)


class TestExtractMarkdownImages(unittest.TestCase):
    def test_extract_images(self):
        text = "This is text with an ![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) and ![another](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/dfsdkjfd.png)"
        images = [
            (
                "image",
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png",
            ),
            (
                "another",
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/dfsdkjfd.png",
            ),
        ]
        self.assertEqual(extract_markdown_images(text), images)

    def test_no_images(self):
        text = "This is text with no images"
        images = []
        self.assertEqual(extract_markdown_images(text), images)


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_extract_links(self):
        text = "This is text with a [link](https://www.example.com) and [another](https://www.example.com/another)"
        links = [
            ("link", "https://www.example.com"),
            ("another", "https://www.example.com/another"),
        ]
        self.assertEqual(extract_markdown_links(text), links)

    def test_no_links(self):
        text = "This is text with no links"
        links = []
        self.assertEqual(extract_markdown_links(text), links)


class TestSplitNodesImages(unittest.TestCase):
    def test_image_start_line(self):
        node = TextNode(
            "![alt text](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected_nodes = [
            TextNode(
                "alt text",
                TextType.IMAGE,
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png",
            )
        ]
        self.assertEqual(new_nodes, expected_nodes)

    def test_single_image(self):
        node = TextNode(
            "This is text with an ![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) and nothing else",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected_nodes = [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode(
                "image",
                TextType.IMAGE,
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png",
            ),
            TextNode(" and nothing else", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected_nodes)

    def test_multiple_image(self):
        node = TextNode(
            "This is text with an ![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) and another ![second image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected_nodes = [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode(
                "image",
                TextType.IMAGE,
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png",
            ),
            TextNode(" and another ", TextType.TEXT),
            TextNode(
                "second image",
                TextType.IMAGE,
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/3elNhQu.png",
            ),
        ]
        self.assertEqual(new_nodes, expected_nodes)


class TestSplitNodesLinks(unittest.TestCase):
    def test_single_link(self):
        node = TextNode(
            "This is text with a [link to boot.dev](https://www.boot.dev) and nothing else",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected_nodes = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode(
                "link to boot.dev",
                TextType.LINK,
                "https://www.boot.dev",
            ),
            TextNode(" and nothing else", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected_nodes)

    def test_multiple_links(self):
        node = TextNode(
            "This is text with a [link to boot.dev](https://www.boot.dev) and one to [my github](https://www.github.com/patrickneise)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected_nodes = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode(
                "link to boot.dev",
                TextType.LINK,
                "https://www.boot.dev",
            ),
            TextNode(" and one to ", TextType.TEXT),
            TextNode(
                "my github",
                TextType.LINK,
                "https://www.github.com/patrickneise",
            ),
        ]
        self.assertEqual(new_nodes, expected_nodes)


class TestTextToTextNodes(unittest.TestCase):
    def test_text_node(self):
        text = "This is just text"
        nodes = text_to_textnodes(text)
        expected_nodes = [TextNode("This is just text", TextType.TEXT)]
        self.assertEqual(nodes, expected_nodes)

    def test_all_nodes(self):
        text = "This is **text** with an *italic* word and a `code block` and an ![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        expected_nodes = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode(
                "image",
                TextType.IMAGE,
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png",
            ),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertEqual(nodes, expected_nodes)


class TestMarkdownToBlocks(unittest.TestCase):
    def test_one_block(self):
        markdown = "# This is a heading"
        blocks = markdown_to_blocks(markdown)
        expected_blocks = ["# This is a heading"]
        self.assertEqual(blocks, expected_blocks)

    def test_three_blocks(self):
        markdown = """
# This is a heading

This is a paragraph of text. It has some **bold** and *italic* words inside of it.

* This is a list item
* This is another list item
"""
        blocks = markdown_to_blocks(markdown)
        expected_blocks = [
            "# This is a heading",
            "This is a paragraph of text. It has some **bold** and *italic* words inside of it.",
            "* This is a list item\n* This is another list item",
        ]
        self.assertEqual(blocks, expected_blocks)


class TestBlockToBlockType(unittest.TestCase):
    def test_h1(self):
        block = "# This is a heading"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.HEADING)

    def test_h4(self):
        block = "#### This is a heading"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.HEADING)

    def test_code(self):
        block = "```\nthis is code\n```"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.CODE)

    def test_code_missing_backticks(self):
        block = "```\nthis is code\n"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.PARAGRAPH)

    def test_quote(self):
        block = "> this is a quote\n> on multiple lines"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.QUOTE)

    def test_quote_missing_format(self):
        block = "> this is a quote\non multiple lines"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.PARAGRAPH)

    def test_ul_astrick(self):
        block = "* this is an\n* unordered list"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.UNORDERED)

    def test_ul_hyphen(self):
        block = "- this is an\n- unordered list"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.UNORDERED)

    def test_ul_missing(self):
        block = "- this is an\nunordered list"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.PARAGRAPH)

    def test_ol(self):
        block = "1. this is an\n2. ordered list"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.ORDERED)

    def test_ol_missing(self):
        block = "1. this is an\nordered list"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.PARAGRAPH)

    def test_ol_start_at_2(self):
        block = "2. this is an\nordered list"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.PARAGRAPH)


if __name__ == "__main__":
    unittest.main()
