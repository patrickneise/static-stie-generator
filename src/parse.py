from enum import StrEnum
import re
from typing import List, Self, Tuple


class NodeType(StrEnum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class Block(StrEnum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED = "unordered_list"
    ORDERED = "ordered_list"


class TextNode:
    def __init__(self, text: str, text_type: NodeType, url: str = None):
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
        if self.text_type in [NodeType.IMAGE, NodeType.LINK]:
            return f'TextNode("{self.text}", {self.text_type}, "{self.url}")'
        else:
            return f'TextNode("{self.text}", {self.text_type})'


# TODO: update based on regex to split
def split_nodes_delimeter(
    old_nodes: List[TextNode], delimeter: str, text_type: NodeType
) -> List[TextNode]:
    new_nodes = []
    re_delimeter = "\\".join(list(delimeter))
    for node in old_nodes:
        chunks = re.split(f"(\{re_delimeter}.+\{re_delimeter})", node.text)
        if len(chunks) % 2 == 0:
            raise Exception("Invalid Markdown format")
        if node.text_type == NodeType.TEXT:
            for index, chunk in enumerate(chunks):
                if chunk:
                    (
                        new_nodes.append(TextNode(chunk, NodeType.TEXT))
                        if index % 2 == 0
                        else new_nodes.append(
                            TextNode(chunk.strip(delimeter), text_type)
                        )
                    )
        else:
            new_nodes.append(node)
    return new_nodes


def split_nodes_image(old_nodes: List[TextNode]) -> List[TextNode]:
    new_nodes = []
    for node in old_nodes:
        images = extract_markdown_images(node.text)
        if images:
            alt_text, url = images[0]
            text_node, next_node = node.text.split(f"![{alt_text}]({url})", 1)
            if text_node:
                new_nodes.append(TextNode(text_node, NodeType.TEXT))
            new_nodes.append(TextNode(alt_text, NodeType.IMAGE, url))
            if next_node:
                new_nodes.extend(
                    split_nodes_image([TextNode(next_node, NodeType.TEXT)])
                )
        else:
            new_nodes.append(node)
    return new_nodes


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
                    TextNode(text_node, NodeType.TEXT),
                    TextNode(text, NodeType.LINK, url),
                ]
                + split_nodes_link([TextNode(next_node, NodeType.TEXT)])
            )
    return new_nodes


def extract_markdown_images(text: str) -> List[Tuple[str, str]]:
    matches = re.findall("!\[(.*?)\]\((.*?)\)", text)
    return matches


def extract_markdown_links(text: str) -> List[Tuple[str, str]]:
    matches = re.findall("\[(.*?)\]\((.*?)\)", text)
    return matches


def text_to_textnodes(text: str) -> List[TextNode]:
    nodes = [TextNode(text, NodeType.TEXT)]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimeter(nodes, "`", NodeType.CODE)
    nodes = split_nodes_delimeter(nodes, "**", NodeType.BOLD)
    nodes = split_nodes_delimeter(nodes, "*", NodeType.ITALIC)

    return nodes


def markdown_to_blocks(markdown: str) -> List[str]:
    blocks = [block.strip() for block in markdown.split("\n\n") if block]

    return blocks


def block_to_block_type(block: str) -> Block:
    block_start = block.split()[0]
    block_end = block.split()[-1]

    if block_start in "######":
        return Block.HEADING
    if block_start == "```" and block_end == "```":
        return Block.CODE
    if block_start == ">":
        for line in block.split("\n"):
            if line.split()[0] != ">":
                return Block.PARAGRAPH
        return Block.QUOTE
    if block_start in "*-":
        list_char = block_start
        for line in block.split("\n"):
            if line.split()[0] != list_char:
                return Block.PARAGRAPH
        return Block.UNORDERED
    if block_start == "1.":
        items = 1
        for line in block.split("\n"):

            if (not line[0].isdigit()) or (int(line.split(".")[0]) != items):
                return Block.PARAGRAPH
            items += 1
        return Block.ORDERED

    return Block.PARAGRAPH
