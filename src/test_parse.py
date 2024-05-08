import unittest

from parse import (
    Block,
    NodeType,
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
        node = TextNode("This is a text node", "bold")
        node2 = TextNode("This is a text node", "bold")
        self.assertEqual(node, node2)

    def test_eq_url(self):
        node = TextNode("This is a text node", "bold", "https://boot.dev")
        node2 = TextNode("This is a text node", "bold", "https://boot.dev")
        self.assertEqual(node, node2)

    def test_not_equal_text(self):
        node = TextNode("This is a text node", "bold")
        node2 = TextNode("This is a different text node", "bold")
        self.assertNotEqual(node, node2)

    def test_not_equal_type(self):
        node = TextNode("This is a text node", "bold")
        node2 = TextNode("This is a text node", "italic")
        self.assertNotEqual(node, node2)

    def test_not_equal_url(self):
        node = TextNode("This is a text node", "bold")
        node2 = TextNode("This is a text node", "bold", "https://boot.dev")
        self.assertNotEqual(node, node2)

    def test_repr_text(self):
        node = TextNode("This is a text Node", "italic")
        output = f'TextNode("This is a text Node", {node.text_type})'
        self.assertEqual(repr(node), output)

    def test_repr_image(self):
        node = TextNode("This is a Link", "link", "https://www.boot.dev")
        output = f'TextNode("This is a Link", {node.text_type}, "https://www.boot.dev")'
        self.assertEqual(repr(node), output)


class TestSplitNodesDelimeter(unittest.TestCase):
    def test_code_text(self):
        node = TextNode("This is text with a `code block` word", NodeType.TEXT)
        new_nodes = split_nodes_delimeter([node], "`", NodeType.CODE)
        expected_nodes = [
            TextNode("This is text with a ", NodeType.TEXT),
            TextNode("code block", NodeType.CODE),
            TextNode(" word", NodeType.TEXT),
        ]

        self.assertEqual(new_nodes, expected_nodes)

    def test_bold_text(self):
        node = TextNode("This is **bold text** in a sentence", NodeType.TEXT)
        new_nodes = split_nodes_delimeter([node], "**", NodeType.BOLD)
        expected_nodes = [
            TextNode("This is ", NodeType.TEXT),
            TextNode("bold text", NodeType.BOLD),
            TextNode(" in a sentence", NodeType.TEXT),
        ]

        self.assertEqual(new_nodes, expected_nodes)

    def test_italic_text(self):
        node = TextNode("This is *italic text* in a sentence", NodeType.TEXT)
        new_nodes = split_nodes_delimeter([node], "*", NodeType.ITALIC)
        expected_nodes = [
            TextNode("This is ", NodeType.TEXT),
            TextNode("italic text", NodeType.ITALIC),
            TextNode(" in a sentence", NodeType.TEXT),
        ]

        self.assertEqual(new_nodes, expected_nodes)

    def test_missing_delimeter(self):
        node = TextNode("This is `code block missing a backtic", NodeType.TEXT)

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
            NodeType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected_nodes = [
            TextNode(
                "alt text",
                NodeType.IMAGE,
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png",
            )
        ]
        self.assertEqual(new_nodes, expected_nodes)

    def test_single_image(self):
        node = TextNode(
            "This is text with an ![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) and nothing else",
            NodeType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected_nodes = [
            TextNode("This is text with an ", NodeType.TEXT),
            TextNode(
                "image",
                NodeType.IMAGE,
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png",
            ),
            TextNode(" and nothing else", NodeType.TEXT),
        ]
        self.assertEqual(new_nodes, expected_nodes)

    def test_multiple_image(self):
        node = TextNode(
            "This is text with an ![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) and another ![second image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/3elNhQu.png)",
            NodeType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected_nodes = [
            TextNode("This is text with an ", NodeType.TEXT),
            TextNode(
                "image",
                NodeType.IMAGE,
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png",
            ),
            TextNode(" and another ", NodeType.TEXT),
            TextNode(
                "second image",
                NodeType.IMAGE,
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/3elNhQu.png",
            ),
        ]
        self.assertEqual(new_nodes, expected_nodes)


class TestSplitNodesLinks(unittest.TestCase):
    def test_single_link(self):
        node = TextNode(
            "This is text with a [link to boot.dev](https://www.boot.dev) and nothing else",
            NodeType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected_nodes = [
            TextNode("This is text with a ", NodeType.TEXT),
            TextNode(
                "link to boot.dev",
                NodeType.LINK,
                "https://www.boot.dev",
            ),
            TextNode(" and nothing else", NodeType.TEXT),
        ]
        self.assertEqual(new_nodes, expected_nodes)

    def test_multiple_links(self):
        node = TextNode(
            "This is text with a [link to boot.dev](https://www.boot.dev) and one to [my github](https://www.github.com/patrickneise)",
            NodeType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected_nodes = [
            TextNode("This is text with a ", NodeType.TEXT),
            TextNode(
                "link to boot.dev",
                NodeType.LINK,
                "https://www.boot.dev",
            ),
            TextNode(" and one to ", NodeType.TEXT),
            TextNode(
                "my github",
                NodeType.LINK,
                "https://www.github.com/patrickneise",
            ),
        ]
        self.assertEqual(new_nodes, expected_nodes)


class TestTextToTextNodes(unittest.TestCase):
    def test_text_node(self):
        text = "This is just text"
        nodes = text_to_textnodes(text)
        expected_nodes = [TextNode("This is just text", NodeType.TEXT)]
        self.assertEqual(nodes, expected_nodes)

    def test_all_nodes(self):
        text = "This is **text** with an *italic* word and a `code block` and an ![image](https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        expected_nodes = [
            TextNode("This is ", NodeType.TEXT),
            TextNode("text", NodeType.BOLD),
            TextNode(" with an ", NodeType.TEXT),
            TextNode("italic", NodeType.ITALIC),
            TextNode(" word and a ", NodeType.TEXT),
            TextNode("code block", NodeType.CODE),
            TextNode(" and an ", NodeType.TEXT),
            TextNode(
                "image",
                NodeType.IMAGE,
                "https://storage.googleapis.com/qvault-webapp-dynamic-assets/course_assets/zjjcJKZ.png",
            ),
            TextNode(" and a ", NodeType.TEXT),
            TextNode("link", NodeType.LINK, "https://boot.dev"),
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
        self.assertEqual(block_type, Block.HEADING)

    def test_h4(self):
        block = "#### This is a heading"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, Block.HEADING)

    def test_code(self):
        block = "```\nthis is code\n```"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, Block.CODE)

    def test_code_missing_backticks(self):
        block = "```\nthis is code\n"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, Block.PARAGRAPH)

    def test_quote(self):
        block = "> this is a quote\n> on multiple lines"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, Block.QUOTE)

    def test_quote_missing_format(self):
        block = "> this is a quote\non multiple lines"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, Block.PARAGRAPH)

    def test_ul_astrick(self):
        block = "* this is an\n* unordered list"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, Block.UNORDERED)

    def test_ul_hyphen(self):
        block = "- this is an\n- unordered list"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, Block.UNORDERED)

    def test_ul_missing(self):
        block = "- this is an\nunordered list"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, Block.PARAGRAPH)

    def test_ol(self):
        block = "1. this is an\n2. ordered list"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, Block.ORDERED)

    def test_ol_missing(self):
        block = "1. this is an\nordered list"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, Block.PARAGRAPH)

    def test_ol_start_at_2(self):
        block = "2. this is an\nordered list"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, Block.PARAGRAPH)


if __name__ == "__main__":
    unittest.main()
