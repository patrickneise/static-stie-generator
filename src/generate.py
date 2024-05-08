import os
import re
from typing import Dict, List, Self

import parse


class HTMLNode:
    def __init__(
        self,
        tag: str = None,
        value: str = None,
        children: List[Self] = None,
        props: Dict[str, str] = None,
    ):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def __eq__(self, node: Self):
        return (
            self.tag == node.tag
            and self.value == node.value
            and self.children == node.children
            and self.props == node.props
        )

    def __repr__(self):
        return f'{self.__class__.__qualname__}(tag="{self.tag}", value="{self.value}", children={self.children}, props={self.props})'

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        return (
            "".join([f' {key}="{value}"' for key, value in self.props.items()])
            if self.props
            else ""
        )


class LeafNode(HTMLNode):
    def __init__(self, tag: str = None, value: str = "", props: Dict[str, str] = None):
        super().__init__(tag=tag, value=value, props=props, children=None)

    def to_html(self):
        if self.tag == "img":
            return f"<{self.tag}{self.props_to_html()}>"
        if not self.value:
            raise ValueError("All nodes require a value")
        if self.tag:
            return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
        return self.value


class ParentNode(HTMLNode):
    def __init__(
        self, tag: str, children: List[HTMLNode], props: Dict[str, str] = None
    ):
        super().__init__(tag=tag, children=children, props=props)

    def to_html(self):
        if not self.tag:
            raise ValueError("ParentNode requires a 'tag'")
        if not self.children:
            raise ValueError("ParentNode requires 'children'")

        inner_html = "".join([node.to_html() for node in self.children])

        return f"<{self.tag}{self.props_to_html()}>{inner_html}</{self.tag}>"


def text_node_to_html_node(text_node: parse.TextNode):
    if text_node.text_type == parse.NodeType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == parse.NodeType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == parse.NodeType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == parse.NodeType.CODE:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == parse.NodeType.LINK:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    elif text_node.text_type == parse.NodeType.IMAGE:
        return LeafNode("img", None, {"src": text_node.url, "alt": text_node.text})
    else:
        raise ValueError("Unknown node type")


def quote_to_html(block):
    text = " ".join([line.lstrip("> ") for line in block.split("\n")])
    text_nodes = parse.text_to_textnodes(text)
    children = [text_node_to_html_node(node) for node in text_nodes]
    return ParentNode("blockquote", children)


def unordered_to_html(block):
    items = [line[2:] for line in block.split("\n")]
    children = []
    for item in items:
        text_nodes = parse.text_to_textnodes(item)
        html_nodes = [text_node_to_html_node(node) for node in text_nodes]
        children.append(ParentNode("li", html_nodes))
    return ParentNode("ul", children)


def ordered_to_html(block):
    items = [line[3:] for line in block.split("\n")]
    children = []
    for item in items:
        text_nodes = parse.text_to_textnodes(item)
        html_nodes = [text_node_to_html_node(node) for node in text_nodes]
        children.append(ParentNode("li", html_nodes))
    return ParentNode("ol", children)


def code_to_html(block):
    code = LeafNode(None, block.strip("```"))
    return ParentNode("pre", [ParentNode("code", [code])])


def heading_to_html(block):
    parts = block.split(" ", 1)
    level = len(parts[0])
    text = parts[1]
    text_nodes = parse.text_to_textnodes(text)
    children = [text_node_to_html_node(node) for node in text_nodes]
    return ParentNode(f"h{level}", children)


def paragraph_to_html(block):
    paragraph_nodes = parse.text_to_textnodes(block)
    return ParentNode("p", [text_node_to_html_node(node) for node in paragraph_nodes])


# TODO:
def markdown_to_html_node(markdown: str) -> ParentNode:
    nodes = []
    blocks = parse.markdown_to_blocks(markdown)
    for block in blocks:
        block_type = parse.block_to_block_type(block)
        if block_type == parse.Block.QUOTE:
            nodes.append(quote_to_html(block))
        if block_type == parse.Block.UNORDERED:
            nodes.append(unordered_to_html(block))
        if block_type == parse.Block.ORDERED:
            nodes.append(ordered_to_html(block))
        if block_type == parse.Block.CODE:
            nodes.append(code_to_html(block))
        if block_type == parse.Block.HEADING:
            nodes.append(heading_to_html(block))
        if block_type == parse.Block.PARAGRAPH:
            nodes.append(paragraph_to_html(block))
    return ParentNode("div", nodes)


def extract_title(markdown):
    heading = re.search("^# (.+)", markdown)
    if not heading:
        raise Exception("All pages require h1 header")
    return heading.group(0).strip("# ")


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path) as markdown_file:
        markdown = markdown_file.read()

    with open(template_path) as template_file:
        template = template_file.read()

    title = extract_title(markdown)
    html_content = markdown_to_html_node(markdown).to_html()

    html_file = template.replace("{{ Title }}", title).replace(
        "{{ Content }}", html_content
    )

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(dest_path, "w") as output:
        output.write(html_file)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    for item in os.listdir(dir_path_content):
        src_path = os.path.join(dir_path_content, item)
        if os.path.isfile(src_path):
            name, extension = item.split(".")
            if extension == "md":
                dst_path = os.path.join(dest_dir_path, f"{name}.html")
                generate_page(src_path, template_path, dst_path)
        else:
            new_dest_dir = os.path.join(dest_dir_path, item)
            os.mkdir(new_dest_dir)
            generate_pages_recursive(src_path, template_path, new_dest_dir)
