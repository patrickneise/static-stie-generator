from enum import Enum
import re
from typing import List, Self, Tuple


class NodeType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class Block(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED = "unordered_list"
    ORDERED = "ordered_list"


class TextNode:
    def __init__(self, text: str, text_type: str, url: str = None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, node: Self):
        return (
            self.text == node.text
            and self.text_type == node.text_type
            and self.url == node.url
        )

    def __repr__(self):
        return f'TextNode("{self.text}", {self.text_type}, "{self.url}")'


# TODO: this needs a refactor
def split_nodes_delimeter(
    old_nodes: List[TextNode], delimeter: str, text_type: str
) -> List[TextNode]:
    new_nodes = []
    for node in old_nodes:
        if node.text_type == NodeType.TEXT.value:
            chunks = node.text.split(delimeter)
            for index, chunk in enumerate(chunks):
                if chunk:
                    (
                        new_nodes.append(TextNode(chunk, NodeType.TEXT.value))
                        if index % 2 == 0
                        else new_nodes.append(TextNode(chunk, text_type))
                    )
        else:
            new_nodes.append(node)
        # TODO: handle missing ending delimeter
        # if len(chunks) % 2 == 0:
        #     raise Exception("Invalid Markdown format")
    return new_nodes


# TODO: tests
def split_nodes_image(old_nodes: List[TextNode]) -> List[TextNode]:
    new_nodes = []
    for node in old_nodes:
        images = extract_markdown_images(node.text)
        if node.text and not images:
            new_nodes.extend([TextNode(node.text, "text")])
        if images:
            alt_text, url = images[0]
            text_node, next_node = node.text.split(f"![{alt_text}]({url})", 1)
            new_nodes.extend(
                [
                    TextNode(text_node, NodeType.TEXT.value),
                    TextNode(alt_text, NodeType.IMAGE.value, url),
                ]
                + split_nodes_image([TextNode(next_node, NodeType.TEXT.value)])
            )
    return new_nodes


# TODO: tests
def split_nodes_link(old_nodes: List[TextNode]):
    new_nodes = []
    for node in old_nodes:
        links = extract_markdown_links(node.text)
        if node.text and not links:
            new_nodes.append(node)
        if links:
            text, url = links[0]
            text_node, next_node = node.text.split(f"[{text}]({url})", 1)
            new_nodes.extend(
                [
                    TextNode(text_node, NodeType.TEXT.value),
                    TextNode(text, NodeType.LINK.value, url),
                ]
                + split_nodes_image([TextNode(next_node, NodeType.TEXT.value)])
            )
    return new_nodes


# TODO: tests
def extract_markdown_images(text: str) -> List[Tuple[str, str]]:
    matches = re.findall("!\[(.*?)\]\((.*?)\)", text)
    return matches


# TODO: tests
def extract_markdown_links(text: str) -> List[Tuple[str, str]]:
    matches = re.findall("\[(.*?)\]\((.*?)\)", text)
    return matches


# TODO: better way to call multiple functions?
def text_to_textnodes(text: str) -> List[TextNode]:
    nodes = [TextNode(text, "text")]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimeter(nodes, "`", NodeType.CODE.value)
    nodes = split_nodes_delimeter(nodes, "**", NodeType.BOLD.value)
    nodes = split_nodes_delimeter(nodes, "*", NodeType.ITALIC.value)

    return nodes


def markdown_to_blocks(markdown: str) -> List[str]:
    blocks = [block.strip() for block in markdown.split("\n\n") if block]

    return blocks


def block_to_block_type(block: str) -> Block:
    block_start = block.split()[0]
    block_end = block.split()[-1]

    if block_start in "######":
        return Block.HEADING.value
    if block_start == "```" and block_end == "```":
        return Block.CODE.value
    if block_start == ">":
        for line in block.split("\n"):
            if line.split()[0] != ">":
                return Block.PARAGRAPH.value
        return Block.QUOTE.value
    if block_start in "*-":
        list_char = block_start
        for line in block.split("\n"):
            if line.split()[0] != list_char:
                return Block.PARAGRAPH.value
        return Block.UNORDERED.value
    if block_start == "1.":
        items = 1
        for line in block.split("\n"):
            if int(line.split(".")[0]) != items:
                return Block.PARAGRAPH.value
            items += 1
        return Block.ORDERED.value

    return Block.PARAGRAPH.value
