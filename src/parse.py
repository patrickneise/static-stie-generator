import re
from typing import List, Self, Tuple

from config import BlockType, TextType


class TextNode:
    def __init__(self, text: str, text_type: TextType, url: str = None):
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
        if self.text_type in [TextType.IMAGE, TextType.LINK]:
            return f'TextNode(text="{self.text}", text_type="{self.text_type}", url="{self.url}")'
        else:
            return f'TextNode(text="{self.text}", text_type="{self.text_type}")'


def split_nodes_delimeter(
    old_nodes: List[TextNode], delimeter: str, text_type: TextType
) -> List[TextNode]:
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        split_nodes = []
        chunks = old_node.text.split(delimeter)
        if len(chunks) % 2 == 0:
            raise ValueError("Invalid markdown, formatted section not closed")
        for index, chunk in enumerate(chunks):
            if chunk == "":
                continue
            if index % 2 == 0:
                split_nodes.append(TextNode(chunk, TextType.TEXT))
            else:
                split_nodes.append(TextNode(chunk, text_type))
        new_nodes.extend(split_nodes)
    return new_nodes


def split_nodes_image(old_nodes: List[TextNode]) -> List[TextNode]:
    new_nodes = []
    for node in old_nodes:

        images = extract_markdown_images(node.text)

        if node.text_type != TextType.TEXT or not images:
            new_nodes.append(node)
            continue

        alt_text, url = images[0]
        text_node, next_node = node.text.split(f"![{alt_text}]({url})", 1)
        if text_node:
            new_nodes.append(TextNode(text_node, TextType.TEXT))
        new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
        if next_node:
            new_nodes.extend(split_nodes_image([TextNode(next_node, TextType.TEXT)]))

    return new_nodes


def split_nodes_link(old_nodes: List[TextNode]):
    new_nodes = []
    for node in old_nodes:

        links = extract_markdown_links(node.text)

        if node.text_type != TextType.TEXT or not links:
            new_nodes.append(node)
            continue

        text, url = links[0]
        text_node, next_node = node.text.split(f"[{text}]({url})", 1)
        if text_node:
            new_nodes.append(TextNode(text_node, TextType.TEXT))
        new_nodes.append(TextNode(text, TextType.LINK, url))
        if next_node:
            new_nodes.extend(split_nodes_link([TextNode(next_node, TextType.TEXT)]))

    return new_nodes


def extract_markdown_images(text: str) -> List[Tuple[str, str]]:
    matches = re.findall("!\[(.*?)\]\((.*?)\)", text)
    return matches


def extract_markdown_links(text: str) -> List[Tuple[str, str]]:
    matches = re.findall("\[(.*?)\]\((.*?)\)", text)
    return matches


def text_to_textnodes(text: str) -> List[TextNode]:
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimeter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimeter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimeter(nodes, "*", TextType.ITALIC)

    return nodes


def markdown_to_blocks(markdown: str) -> List[str]:
    blocks = [block.strip() for block in markdown.split("\n\n") if block]

    return blocks


def block_to_block_type(block: str) -> BlockType:
    block_start = block.split()[0]
    block_end = block.split()[-1]

    if block_start in "######":
        return BlockType.HEADING
    if block_start == "```" and block_end == "```":
        return BlockType.CODE
    if block_start == ">":
        for line in block.split("\n"):
            if line.split()[0] != ">":
                return BlockType.PARAGRAPH
        return BlockType.QUOTE
    if block_start in "*-":
        list_char = block_start
        for line in block.split("\n"):
            if line.split()[0] != list_char:
                return BlockType.PARAGRAPH
        return BlockType.UNORDERED
    if block_start == "1.":
        items = 1
        for line in block.split("\n"):

            if (not line[0].isdigit()) or (int(line.split(".")[0]) != items):
                return BlockType.PARAGRAPH
            items += 1
        return BlockType.ORDERED

    return BlockType.PARAGRAPH
